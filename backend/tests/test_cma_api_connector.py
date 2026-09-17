"""
Tests for the experimental CMA CGM API connector.

The two things worth proving without a live API:
  1. The default search path is byte-identical unless CMA_CGM_USE_API is set.
  2. The parser is pure, so a saved response can be replayed through it — the
     regression-testing the scraping connectors cannot do.
"""
import os
import sys
import asyncio

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from models.schemas import RateSearchRequest, ChargeCategory
from carriers.cma_api_connector import (
    parse_rate_payload, find_quote_list, api_enabled, CMAAPIConnector,
)


def req(ct="DRY 40H"):
    return RateSearchRequest(carriers=["CMA_CGM"], origin="SGSIN", destination="DEHAM",
                             container_type=ct, container_types=[ct],
                             weight_per_container_kg=20000)


# ── 1. Isolation: the current process must be untouched ──────────────────────

def test_disabled_by_default():
    os.environ.pop("CMA_CGM_USE_API", None)
    assert api_enabled() is False
    print("api_enabled() is False when the flag is absent: PASS")


def test_registry_returns_browser_connector_by_default():
    os.environ.pop("CMA_CGM_USE_API", None)
    os.environ["USE_MOCK_CARRIERS"] = "false"
    import importlib
    import carriers.registry as registry
    importlib.reload(registry)
    conn = registry.get_connector("CMA_CGM")
    assert type(conn).__name__ == "CMAConnector", type(conn).__name__
    print("registry still returns the Playwright CMAConnector by default: PASS")


def test_registry_opt_in_switches():
    os.environ["CMA_CGM_USE_API"] = "true"
    os.environ["USE_MOCK_CARRIERS"] = "false"
    import importlib
    import carriers.registry as registry
    importlib.reload(registry)
    conn = registry.get_connector("CMA_CGM")
    assert type(conn).__name__ == "CMAAPIConnector", type(conn).__name__
    os.environ.pop("CMA_CGM_USE_API", None)
    print("registry switches to the API connector only when opted in: PASS")


def test_other_carriers_unaffected_by_flag():
    os.environ["CMA_CGM_USE_API"] = "true"
    os.environ["USE_MOCK_CARRIERS"] = "false"
    import importlib
    import carriers.registry as registry
    importlib.reload(registry)
    assert type(registry.get_connector("MAERSK")).__name__ == "MaerskConnector"
    assert type(registry.get_connector("HAPAG_LLOYD")).__name__ == "HapagLloydConnector"
    os.environ.pop("CMA_CGM_USE_API", None)
    print("the flag touches CMA_CGM only, no other carrier: PASS")


# ── 2. Parser ────────────────────────────────────────────────────────────────

def test_finds_quotes_in_named_list():
    payload = {"rates": [{"etd": "2026-10-01", "totalPrice": 1500}]}
    assert len(find_quote_list(payload)) == 1
    print("finds the quote list under a known key: PASS")


def test_finds_quotes_in_unexpected_envelope():
    """A shape we did not anticipate must still yield the sailings."""
    payload = {"response": {"payload": {"someUnknownName": [
        {"etd": "2026-10-01", "totalPrice": 1500},
        {"etd": "2026-10-08", "totalPrice": 1600},
    ]}}}
    assert len(find_quote_list(payload)) == 2
    print("falls back to the deepest list of objects in an unknown envelope: PASS")


def test_charge_list_is_not_mistaken_for_the_sailing_list():
    """
    Regression: the fallback scan picked the LONGEST list of objects, so an offer
    carrying 3 charges beat a list of 1 offer — turning one sailing into three
    bogus quotes. Sailing fields, not list length, decide.
    """
    payload = {"spotOffers": [{
        "departureDate": "2026-10-05", "vesselName": "CMA CGM JACQUES SAADE",
        "charges": [{"chargeName": "Basic Ocean Freight", "amount": 1400},
                    {"chargeName": "Low Sulphur Surcharge", "amount": 120},
                    {"chargeName": "Terminal Handling Charge Destination", "amount": 200}],
    }]}
    assert len(find_quote_list(payload)) == 1
    quotes = parse_rate_payload(payload, req(), "DRY 40H")
    assert len(quotes) == 1, f"one offer must yield one quote, got {len(quotes)}"
    assert quotes[0].final_freight_value == 1520.0, quotes[0].final_freight_value
    print("a nested charge list is never mistaken for the sailing list: PASS")


def test_charges_are_classified_like_the_scraper():
    payload = {"rates": [{
        "etd": "2026-10-01", "eta": "2026-11-02", "transitTime": 32,
        "vesselName": "CMA CGM MARCO POLO", "currency": "USD",
        "charges": [
            {"name": "Basic Ocean Freight", "amount": 1200, "currency": "USD"},
            {"name": "Bunker Adjustment Factor", "amount": 300, "currency": "USD"},
            {"name": "Terminal Handling Charge Origin", "amount": 150, "currency": "USD"},
        ],
    }]}
    q = parse_rate_payload(payload, req(), "DRY 40H")[0]
    assert q.basic_ocean_freight == 1200, q.basic_ocean_freight
    included = [c.name for c in q.included_freight_surcharges]
    excluded = [c.name for c in q.excluded_charges]
    assert "Bunker Adjustment Factor" in included, included
    assert any("Terminal Handling" in c for c in excluded), excluded
    # BAF rides with the freight, THC does not — same rule as every other carrier.
    assert q.final_freight_value == 1500.0, q.final_freight_value
    assert q.vessel == "CMA CGM MARCO POLO"
    assert q.transit_time_days == 32
    print("charges classified consistently with the scraping connectors: PASS")


def test_falls_back_to_headline_total_without_breakdown():
    payload = {"rates": [{"etd": "2026-10-01", "totalPrice": "2,450.00"}]}
    q = parse_rate_payload(payload, req(), "DRY 40")[0]
    assert q.final_freight_value == 2450.0, q.final_freight_value
    assert q.is_breakdown_unavailable is True
    print("a priced sailing with no breakdown still returns its total: PASS")


def test_alias_field_names():
    """Different field spellings must resolve to the same QuoteSchema."""
    a = parse_rate_payload({"rates": [{"departureDate": "2026-10-01",
                                       "arrivalDate": "2026-11-02",
                                       "totalAmount": 1000}]}, req(), "DRY 20")[0]
    b = parse_rate_payload({"rates": [{"etd": "2026-10-01", "eta": "2026-11-02",
                                       "total": 1000}]}, req(), "DRY 20")[0]
    assert a.etd == b.etd and a.eta == b.eta
    assert a.final_freight_value == b.final_freight_value == 1000.0
    print("field-name aliases resolve to the same quote: PASS")


def test_container_type_is_carried_through():
    payload = {"rates": [{"etd": "2026-10-01", "totalPrice": 900}]}
    for ct in ("DRY 20", "DRY 40", "DRY 40H"):
        q = parse_rate_payload(payload, req(ct), ct)[0]
        assert q.container_type == ct
    print("each requested container type is labelled correctly: PASS")


def test_empty_payload_is_not_a_crash():
    assert parse_rate_payload({}, req(), "DRY 40H") == []
    assert parse_rate_payload({"rates": []}, req(), "DRY 40H") == []
    assert parse_rate_payload(None, req(), "DRY 40H") == []
    print("empty and malformed payloads return no quotes rather than raising: PASS")


def test_source_marks_api_origin():
    q = parse_rate_payload({"rates": [{"etd": "2026-10-01", "totalPrice": 100}]},
                           req(), "DRY 40H")[0]
    assert q.source == "carrier_api", q.source
    print("quotes are tagged source=carrier_api so they are distinguishable: PASS")


# ── 3. Connector guards ──────────────────────────────────────────────────────

def test_login_refuses_without_config():
    """Every missing OAuth2 setting must be named, not discovered one at a time."""
    for var in ("CMA_CGM_API_TOKEN_URL", "CMA_CGM_API_CLIENT_ID",
                "CMA_CGM_API_CLIENT_SECRET", "CMA_CGM_API_SPOTON_PATH"):
        os.environ.pop(var, None)
    c = CMAAPIConnector()
    assert asyncio.run(c.login()) is False
    err = c.last_error or ""
    for var in ("CMA_CGM_API_TOKEN_URL", "CMA_CGM_API_CLIENT_ID",
                "CMA_CGM_API_CLIENT_SECRET", "CMA_CGM_API_SPOTON_PATH"):
        assert var in err, f"{var} missing from error: {err}"
    print("login names every unset OAuth2 setting at once: PASS")


def test_token_is_cached_until_expiry():
    """A batch must not mint a token per call — the quota is 20/hour."""
    c = CMAAPIConnector()
    c._token = "cached-token"
    c._token_expires_at = __import__("time").time() + 600
    assert asyncio.run(c.get_token()) == "cached-token"
    # expired token must not be reused
    c._token_expires_at = __import__("time").time() - 1
    c.token_url = "http://127.0.0.1:9/nonexistent"
    assert asyncio.run(c.get_token()) is None
    print("bearer token is cached until expiry, then re-minted: PASS")


def test_no_key_is_ever_hardcoded():
    """
    Guard against a secret being committed. Deliberately pattern-based: writing the
    real key here as a literal to search for would itself put it in the repo.
    """
    import re
    base = os.path.dirname(__file__)
    targets = {
        "cma_api_connector.py": os.path.join(base, "..", "carriers", "cma_api_connector.py"),
        "cma_api_probe.py": os.path.join(base, "..", "..", "scripts", "experimental", "cma_api_probe.py"),
    }
    # A CMA CGM key is a long opaque alphanumeric run with both cases and digits.
    secret_like = re.compile(r"['\"][A-Za-z0-9]{24,}['\"]")
    for name, path in targets.items():
        src = open(path).read()
        for candidate in secret_like.findall(src):
            body = candidate.strip("'\"")
            has_mixed_case = body != body.lower() and body != body.upper()
            if has_mixed_case and any(ch.isdigit() for ch in body):
                raise AssertionError(f"{name} contains a possible hardcoded secret: {body[:6]}…")
    src = open(targets["cma_api_connector.py"]).read()
    assert 'getenv("CMA_CGM_API_KEY"' in src, "the key must be read from the environment"
    print("no API key is hardcoded in either file: PASS")


if __name__ == "__main__":
    for fn in [v for k, v in sorted(globals().items()) if k.startswith("test_")]:
        fn()
    print("\nALL PASS")
