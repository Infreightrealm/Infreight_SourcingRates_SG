"""
Tests for the experimental CMA CGM SpotOn API connector.

Fixtures are built from the documented examples in the SpotOn OpenAPI spec
(scripts/experimental/spoton-swagger-v2.6.0.json), so the parser is exercised
against the shape CMA CGM says it returns rather than an invented one.

Two things are proven here that cannot be proven for a scraping connector:
  1. The default search path is unchanged unless CMA_CGM_USE_API is set.
  2. Parsing is pure, so a saved response replays deterministically.
"""
import os
import sys
import copy
import asyncio
from datetime import date, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from models.schemas import RateSearchRequest
from carriers.cma_api_connector import (
    parse_spoton_response, build_search_payload, resolve_departure_date,
    api_enabled, CMAAPIConnector, CONTAINER_TYPE_TO_ISO,
)


def req(types=("DRY 20", "DRY 40H"), **kw):
    kwargs = dict(carriers=["CMA_CGM"], origin="SGSIN", destination="DEHAM",
                  container_types=list(types), container_type=list(types)[0],
                  container_quantity=1, weight_per_container_kg=20000)
    kwargs.update(kw)
    return RateSearchRequest(**kwargs)


# A SpotOffer as the spec documents it. Basic freight for 20GP is 1400 and
# already contains a 100 LSS; BAF of 120 is additional -> allInRate 1520.
OFFER = {
    "offerId": "6bdac5a3-5a28-447d-b9cb-9eb1c9be2025",
    "offerType": "ExactRouting",
    "solutionDescription": "Service French Asia Line 1",
    "transitTime": 32,
    "departureDate": "2026-10-05T16:00:00Z",
    "arrivalDate": "2026-11-06T00:00:00Z",
    "routingLegs": [{
        "legNumber": 1,
        "vesselName": "CMA CGM JACQUES SAADE",
        "voyageReference": "0FADZW1MA",
        "service": {"code": "FAL1", "name": "French Asia Line 1"},
        "legFrom": {"place": {"name": "Singapore", "internalCode": "SGSIN"}, "port": True},
        "legTo": {"place": {"name": "Hamburg", "internalCode": "DEHAM"}, "port": True},
    }],
    "ddsmConditions": [
        {"tariff": {"code": "DEM", "name": "Demurrage"},
         "conditionsByEquipment": [{"equipmentGroupIsoCode": "20GP",
                                    "freeDays": {"number": 7, "calculationType": "Calendar"}}]},
        {"tariff": {"code": "DET", "name": "Detention"},
         "conditionsByEquipment": [{"equipmentGroupIsoCode": "20GP",
                                    "freeDays": {"number": 10, "calculationType": "Calendar"}}]},
    ],
    "allocation": [{"equipmentGroupIsoCode": ["20GP", "40HC"], "allocation": True,
                    "nbOfContainersAvailable": 12}],
    "quoteLine": {
        "shippingCompany": "0001",
        "validityFrom": "2026-10-01",
        "validityTo": "2026-10-20",
        "spotEquipments": [
            {"equipmentGroupIsoCode": "20GP", "availableRate": True, "maxNetWeight": 18},
            {"equipmentGroupIsoCode": "40HC", "availableRate": True, "maxNetWeight": 26},
        ],
        "commodity": {"commodityGroup": True, "code": "FAK", "name": "Freight all kinds"},
        "surcharges": {
            "simulationDate": "2026-09-17",
            "matchingSurchargesPerEquipmentTypes": [
                {"equipmentGroupIsoCode": "20GP", "allInRate": 1520,
                 "basicOceanFreightRate": 1400, "currency": {"code": "USD"},
                 "matchingCargoSurcharges": [
                     {"charge": {"code": "BAF03", "name": "Bunker surcharge NOS"},
                      "chargeCurrency": {"code": "USD"}, "amount": 120,
                      "surcharge": True, "includedInBasicFreight": False},
                     {"charge": {"code": "LSS01", "name": "Low Sulphur Surcharge"},
                      "chargeCurrency": {"code": "USD"}, "amount": 100,
                      "surcharge": True, "includedInBasicFreight": True},
                 ]},
                {"equipmentGroupIsoCode": "40HC", "allInRate": 2800,
                 "basicOceanFreightRate": 2600, "currency": {"code": "USD"},
                 "matchingCargoSurcharges": [
                     {"charge": {"code": "BAF03", "name": "Bunker surcharge NOS"},
                      "chargeCurrency": {"code": "USD"}, "amount": 200,
                      "surcharge": True, "includedInBasicFreight": False},
                 ]},
            ],
            "matchingBlSurcharges": [],
        },
    },
}


# ── Isolation: the current process must be untouched ─────────────────────────

def test_disabled_by_default():
    os.environ.pop("CMA_CGM_USE_API", None)
    assert api_enabled() is False
    print("api_enabled() is False when the flag is absent: PASS")


def test_registry_returns_browser_connector_by_default():
    os.environ.pop("CMA_CGM_USE_API", None)
    os.environ["USE_MOCK_CARRIERS"] = "false"
    import importlib, carriers.registry as registry
    importlib.reload(registry)
    assert type(registry.get_connector("CMA_CGM")).__name__ == "CMAConnector"
    print("registry still returns the Playwright CMAConnector by default: PASS")


def test_registry_opt_in_switches():
    os.environ["CMA_CGM_USE_API"] = "true"
    os.environ["USE_MOCK_CARRIERS"] = "false"
    import importlib, carriers.registry as registry
    importlib.reload(registry)
    assert type(registry.get_connector("CMA_CGM")).__name__ == "CMAAPIConnector"
    os.environ.pop("CMA_CGM_USE_API", None)
    print("registry switches to the API connector only when opted in: PASS")


def test_other_carriers_unaffected_by_flag():
    os.environ["CMA_CGM_USE_API"] = "true"
    os.environ["USE_MOCK_CARRIERS"] = "false"
    import importlib, carriers.registry as registry
    importlib.reload(registry)
    assert type(registry.get_connector("MAERSK")).__name__ == "MaerskConnector"
    assert type(registry.get_connector("HAPAG_LLOYD")).__name__ == "HapagLloydConnector"
    os.environ.pop("CMA_CGM_USE_API", None)
    print("the flag touches CMA_CGM only, no other carrier: PASS")


# ── Request building ─────────────────────────────────────────────────────────

def test_all_sizes_go_in_one_call():
    """
    The spec allows several equipment sizes per request. At 20 requests/hour that
    is the difference between one call per search and three.
    """
    body = build_search_payload(req(("DRY 20", "DRY 40", "DRY 40H")),
                                ["DRY 20", "DRY 40", "DRY 40H"])
    isos = [e["equipmentGroupIsoCode"] for e in body["requestedEquipments"]]
    assert isos == ["20GP", "40GP", "40HC"], isos
    print("all three container sizes ride in a single request: PASS")


def test_required_body_fields_present():
    """Per the spec, requestedEquipments and its three fields are mandatory."""
    body = build_search_payload(req(), ["DRY 20"])
    assert "requestedEquipments" in body
    for eq in body["requestedEquipments"]:
        for field in ("equipmentGroupIsoCode", "numberOfContainers", "weightPerContainer"):
            assert field in eq, f"{field} missing — the API returns EQP_ERR/USE_ERR"
    assert body["locationCodificationType"] == "UNLOCODE"
    assert body["portOfLoading"] == "SGSIN" and body["portOfDischarge"] == "DEHAM"
    print("mandatory request fields are all present: PASS")


def test_departure_date_is_clamped_to_the_accepted_window():
    """DAT_ERR: the API rejects a date before today or beyond today+30."""
    today = date.today()
    assert resolve_departure_date((today - timedelta(days=5)).isoformat()) == today.isoformat()
    assert resolve_departure_date((today + timedelta(days=99)).isoformat()) == \
        (today + timedelta(days=30)).isoformat()
    assert resolve_departure_date("tomorrow") == (today + timedelta(days=1)).isoformat()
    assert resolve_departure_date("not a date") == (today + timedelta(days=1)).isoformat()
    print("departure date is clamped into the window the API accepts: PASS")


def test_commodity_falls_back_to_fak():
    """CDY_ERR: commodity must be FAK or an HS code of 4+ digits."""
    assert build_search_payload(req(commodity="Furniture"), ["DRY 20"])["commodityCode"] == "FAK"
    assert build_search_payload(req(commodity="9403"), ["DRY 20"])["commodityCode"] == "9403"
    print("a free-text commodity falls back to FAK rather than erroring: PASS")


# ── Response parsing ─────────────────────────────────────────────────────────

def test_one_offer_yields_one_quote_per_equipment():
    quotes, messages = parse_spoton_response([OFFER], req())
    assert len(quotes) == 2, len(quotes)
    assert {q.container_type for q in quotes} == {"DRY 20", "DRY 40H"}
    print("one offer yields one quote per priced equipment size: PASS")


def test_included_in_basic_freight_is_not_double_counted():
    """
    The LSS is flagged includedInBasicFreight, so it already sits inside the 1400
    basic rate. Adding it again would give 1620 against CMA's stated 1520.
    """
    quotes, _ = parse_spoton_response([OFFER], req())
    q20 = next(q for q in quotes if q.container_type == "DRY 20")
    assert q20.basic_ocean_freight == 1400.0, q20.basic_ocean_freight
    assert q20.final_freight_value == 1520.0, q20.final_freight_value
    assert q20.warning_message is None, q20.warning_message
    names = [c.name for c in q20.included_freight_surcharges]
    assert "Low Sulphur Surcharge" in names, "the charge must still be shown"
    print("a charge already inside basic freight is shown but not re-added: PASS")


def test_disagreement_with_allinrate_is_surfaced():
    """If our classification disagrees with CMA's total, say so and use theirs."""
    offer = copy.deepcopy(OFFER)
    eq = offer["quoteLine"]["surcharges"]["matchingSurchargesPerEquipmentTypes"][0]
    eq["allInRate"] = 1600  # CMA says 1600; our sum says 1520
    quotes, _ = parse_spoton_response([offer], req())
    q20 = next(q for q in quotes if q.container_type == "DRY 20")
    assert q20.final_freight_value == 1600.0, q20.final_freight_value
    assert q20.warning_message and "allInRate" in q20.warning_message
    print("a gap against CMA's allInRate is flagged, not silently published: PASS")


def test_sold_out_sentinels_do_not_become_quotes():
    """offerId carries 'Sold-out'/'no-offer' rather than a blank — no guessing."""
    for sentinel in ("no-offer", "Sold-out", "Quantities cannot be confirmed"):
        offer = copy.deepcopy(OFFER)
        offer["offerId"] = sentinel
        quotes, messages = parse_spoton_response([offer], req())
        assert quotes == [], f"{sentinel} produced a phantom quote"
        assert messages, f"{sentinel} produced no explanation"
    print("sold-out and no-offer sailings are reported, never priced: PASS")


def test_message_objects_are_captured():
    """The array mixes SpotOffer and Message; a Message explains an empty result."""
    payload = [{"code": "INQ_SPN",
                "description": "SpotOn offer not available for your search criteria"}]
    quotes, messages = parse_spoton_response(payload, req())
    assert quotes == []
    assert any("INQ_SPN" in m for m in messages), messages
    print("a Message explaining no offer is surfaced, not dropped: PASS")


def test_unavailable_size_is_skipped_not_zeroed():
    offer = copy.deepcopy(OFFER)
    offer["quoteLine"]["spotEquipments"][0]["availableRate"] = False
    quotes, messages = parse_spoton_response([offer], req())
    assert {q.container_type for q in quotes} == {"DRY 40H"}
    assert any("DRY 20" in m for m in messages), messages
    print("a size with no rate is reported, not returned as a zero: PASS")


def test_schedule_and_free_time_are_extracted():
    quotes, _ = parse_spoton_response([OFFER], req())
    q = quotes[0]
    # Dates go through the shared normalizer, so they match every other
    # connector's house format rather than the API's raw ISO date-time.
    assert q.etd == "5 Oct 2026", q.etd
    assert q.eta == "6 Nov 2026", q.eta
    assert q.transit_time_days == 32
    assert q.vessel == "CMA CGM JACQUES SAADE (Voy: 0FADZW1MA)", q.vessel
    assert q.service_name == "French Asia Line 1"
    assert q.routing == "Direct"
    assert q.demurrage == 7 and q.detention == 10, (q.demurrage, q.detention)
    assert q.validity_till == "20 Oct 2026", q.validity_till
    assert q.currency == "USD"
    print("dates, vessel, voyage, service, free days and validity all parse: PASS")


def test_transhipment_routing_is_labelled():
    offer = copy.deepcopy(OFFER)
    offer["routingLegs"].append({
        "legNumber": 2, "vesselName": "CMA CGM MARCO POLO",
        "legFrom": {"place": {"name": "Port Kelang", "internalCode": "MYPKG"}},
        "legTo": {"place": {"name": "Hamburg", "internalCode": "DEHAM"}}})
    quotes, _ = parse_spoton_response([offer], req())
    assert quotes[0].routing == "via Port Kelang", quotes[0].routing
    # the first leg's vessel is still the one loading at origin
    assert quotes[0].vessel.startswith("CMA CGM JACQUES SAADE")
    print("a multi-leg routing is labelled with its transhipment port: PASS")


def test_empty_and_malformed_payloads_are_safe():
    for payload in ([], {}, None, "nonsense", [None, 42]):
        quotes, _ = parse_spoton_response(payload, req())
        assert quotes == []
    print("empty and malformed payloads return no quotes rather than raising: PASS")


def test_quotes_are_tagged_as_api_sourced():
    quotes, _ = parse_spoton_response([OFFER], req())
    assert all(q.source == "carrier_api" for q in quotes)
    assert quotes[0].raw_reference == OFFER["offerId"]
    print("quotes carry source=carrier_api and the real offerId: PASS")


def test_quick_mode_returns_cheapest_per_size():
    cheap = copy.deepcopy(OFFER)
    cheap["offerId"] = "cheaper"
    cheap["quoteLine"]["surcharges"]["matchingSurchargesPerEquipmentTypes"][0].update(
        {"allInRate": 900, "basicOceanFreightRate": 900, "matchingCargoSurcharges": []})
    quotes, _ = parse_spoton_response([OFFER, cheap], req())
    best = CMAAPIConnector._cheapest_per_type(quotes)
    by_type = {q.container_type: q.final_freight_value for q in best}
    assert by_type["DRY 20"] == 900.0, by_type
    assert len(best) == 2, by_type
    print("quick mode keeps the cheapest sailing per container size: PASS")


# ── Connector guards ─────────────────────────────────────────────────────────

def test_login_names_missing_credentials():
    for var in ("CMA_CGM_API_CLIENT_ID", "CMA_CGM_API_CLIENT_SECRET"):
        os.environ.pop(var, None)
    c = CMAAPIConnector()
    assert asyncio.run(c.login()) is False
    assert "CLIENT_ID" in c.last_error and "CLIENT_SECRET" in c.last_error
    print("login names every missing credential at once: PASS")


def test_defaults_match_the_published_spec():
    for var in ("CMA_CGM_API_BASE", "CMA_CGM_API_TOKEN_URL", "CMA_CGM_API_SCOPE"):
        os.environ.pop(var, None)
    c = CMAAPIConnector()
    assert c.base_url == "https://apis.cma-cgm.net/pricing/commercial/instantquote/v2"
    assert c.token_url == "https://auth.cma-cgm.com/as/token.oauth2"
    assert c.scope == "instantquote:read:be"
    assert c.range_header == "0-4"  # the API caps at 5 rows
    print("defaults match the SpotOn spec, so only credentials need setting: PASS")


def test_token_is_cached_until_expiry():
    """A batch must not mint a token per call — the quota is 20/hour."""
    import time as _t
    c = CMAAPIConnector()
    c._token, c._token_expires_at = "cached-token", _t.time() + 600
    assert asyncio.run(c.get_token()) == "cached-token"
    c._token_expires_at = _t.time() - 1
    c.token_url = "http://127.0.0.1:9/nonexistent"
    assert asyncio.run(c.get_token()) is None
    print("bearer token is cached until expiry, then re-minted: PASS")


def test_no_credential_is_hardcoded():
    """
    Deliberately pattern-based: writing a real key here as a literal to search for
    would itself commit it.
    """
    import re
    base = os.path.dirname(__file__)
    targets = {
        "cma_api_connector.py": os.path.join(base, "..", "carriers", "cma_api_connector.py"),
        "cma_api_probe.py": os.path.join(base, "..", "..", "scripts", "experimental",
                                         "cma_api_probe.py"),
    }
    secret_like = re.compile(r"['\"][A-Za-z0-9]{24,}['\"]")
    for name, path in targets.items():
        for candidate in secret_like.findall(open(path).read()):
            body = candidate.strip("'\"")
            mixed = body != body.lower() and body != body.upper()
            if mixed and any(ch.isdigit() for ch in body):
                raise AssertionError(f"{name} may contain a hardcoded secret: {body[:6]}…")
    src = open(targets["cma_api_connector.py"]).read()
    assert 'getenv("CMA_CGM_API_CLIENT_SECRET"' in src
    print("no credential is hardcoded in either file: PASS")


if __name__ == "__main__":
    for fn in [v for k, v in sorted(globals().items()) if k.startswith("test_")]:
        fn()
    print("\nALL PASS")
