"""
CMA CGM SpotOn API Connector — EXPERIMENTAL.

An alternative to the Playwright connector (`cma_connector.py`) that calls the
CMA CGM SpotOn pricing API instead of driving a browser. Nothing uses this by
default: it is only selected when CMA_CGM_USE_API=true, so the live scraping path
is unchanged until that flag is deliberately set.

WHY IT MATTERS
    The browser connector exists mainly to look human to CMA CGM's bot defences —
    the reason the office laptop runs crawls at all. An authenticated API call has
    no bot problem, so this path can run in the cloud and returns in seconds.

THE CONTRACT (from the SpotOn OpenAPI 3.0 spec, v2.6.0 — see
`scripts/experimental/spoton-swagger-v2.6.0.json`)
    POST {base}/spotOn/search, OAuth2 client_credentials, scope instantquote:read:be.

    Three properties of this API shape the design:

    1. `requestedEquipments` is an ARRAY, and multiple sizes in the same category
       may be requested together. One call therefore prices 20', 40' and 40'HC at
       once — a third of the requests the browser path needs, which matters
       because the portal quota is 20 requests/hour.

    2. Each charge carries `includedInBasicFreight`. A charge already inside
       `basicOceanFreightRate` must NOT be added again, or the total double-counts.
       The API states its own total as `allInRate`, which is reconciled against
       ours and surfaced as a warning on mismatch rather than silently trusted.

    3. Unavailability is explicit. `offerId` carries sentinel values ('no-offer',
       'Sold-out', 'Quantities cannot be confirmed'), `allocation[].allocation`
       reports capacity, and `spotEquipments[].availableRate` reports per-size
       availability. No guessing from a blank cell, which is the failure mode that
       plagues the scraping connectors.

    Note "Local surcharges are not provided" — THC and documentation fees are
    absent by design, so an API quote's excluded_charges will be thinner than a
    scraped one's. That is the API's behaviour, not a parsing gap.

CONFIGURATION (all via env — never hardcode credentials)
    CMA_CGM_USE_API            "true" to route CMA_CGM through this connector.
    CMA_CGM_API_CLIENT_ID      OAuth2 client id.       (required)
    CMA_CGM_API_CLIENT_SECRET  OAuth2 client secret.   (required)
    CMA_CGM_API_BASE           default https://apis.cma-cgm.net/pricing/commercial/instantquote/v2
    CMA_CGM_API_TOKEN_URL      default https://auth.cma-cgm.com/as/token.oauth2
    CMA_CGM_API_SCOPE          default instantquote:read:be
    CMA_CGM_API_RANGE          pagination header, default "0-4" (the API caps at 5 rows)
    CMA_CGM_API_BEHALF_OF      end-customer code; mandatory only for third parties.
"""
from __future__ import annotations

import os
import time
from datetime import date, datetime, timedelta
from typing import Any, Optional

import httpx

from models.schemas import (
    RateSearchRequest,
    QuoteSchema,
    ChargeSchema,
    CarrierResultStatus,
    ChargeCategory,
)
from services.charge_classifier import classify_charge
from services.normalizer import standardize_date_string
from carriers.base_connector import BaseCarrierConnector


DEFAULT_BASE = "https://apis.cma-cgm.net/pricing/commercial/instantquote/v2"
DEFAULT_TOKEN_URL = "https://auth.cma-cgm.com/as/token.oauth2"
DEFAULT_SCOPE = "instantquote:read:be"
SEARCH_PATH = "/spotOn/search"


def api_enabled() -> bool:
    """True only when the operator has explicitly opted in."""
    return os.getenv("CMA_CGM_USE_API", "false").strip().lower() in ("true", "1", "yes")


# Equipment group ISO codes. Confirmable against the referential.packaging.v2 API,
# which the same account is subscribed to.
CONTAINER_TYPE_TO_ISO = {
    "DRY 20": "20GP",
    "DRY 40": "40GP",
    "DRY 40H": "40HC",
}
ISO_TO_CONTAINER_TYPE = {v: k for k, v in CONTAINER_TYPE_TO_ISO.items()}
# Spellings the rest of the system uses for the same sizes.
ISO_TO_CONTAINER_TYPE.update({"40HQ": "DRY 40H", "45G1": "DRY 40H"})

# offerId sentinels meaning "priced offer not available", per the spec.
NO_OFFER_IDS = {
    "no-offer",
    "sold-out",
    "quantities cannot be confirmed",
    "offer cannot be created under fmc scope",
}
SOLD_OUT_IDS = {"sold-out", "quantities cannot be confirmed"}


def _f(v: Any) -> float:
    if v is None:
        return 0.0
    if isinstance(v, (int, float)):
        return float(v)
    try:
        return float(str(v).replace(",", "").strip())
    except (ValueError, AttributeError):
        return 0.0


def _date_only(v: Any) -> Optional[str]:
    """SpotOn returns date-times ('2023-01-24T16:00:00Z'); the system wants dates."""
    if not v:
        return None
    text = str(v)
    if "T" in text:
        text = text.split("T", 1)[0]
    return standardize_date_string(text)


def resolve_departure_date(raw: Optional[str]) -> str:
    """
    The API rejects a departure date before today or more than 30 days out
    (DAT_ERR), so clamp rather than let a whole search fail on an out-of-range date.
    """
    today = date.today()
    if not raw or str(raw).strip().lower() in ("", "tomorrow"):
        target = today + timedelta(days=1)
    else:
        try:
            target = datetime.strptime(str(raw).strip()[:10], "%Y-%m-%d").date()
        except ValueError:
            target = today + timedelta(days=1)
    target = max(today, min(target, today + timedelta(days=30)))
    return target.isoformat()


def build_search_payload(request: RateSearchRequest,
                         container_types: list[str]) -> dict:
    """
    Body for POST /spotOn/search.

    All requested sizes go in one call: the spec allows multiple equipment sizes
    of the same category, and the hourly quota makes that worth doing.
    """
    equipments = []
    for ct in container_types:
        iso = CONTAINER_TYPE_TO_ISO.get(ct.upper().strip(), ct)
        equipments.append({
            "equipmentGroupIsoCode": iso,
            "numberOfContainers": request.container_quantity,
            "weightPerContainer": request.weight_per_container_kg,
        })

    commodity = (request.commodity or "FAK").strip()
    # The spec accepts 'FAK' or an HS code of 4+ digits; anything else is CDY_ERR.
    commodity_code = commodity if commodity.isdigit() and len(commodity) >= 4 else "FAK"

    payload: dict[str, Any] = {
        "departureDate": resolve_departure_date(request.departure_date),
        "locationCodificationType": "UNLOCODE",
        "portOfLoading": request.origin,
        "portOfDischarge": request.destination,
        "commodityCode": commodity_code,
        # Only spot-specific DDSM conditions: the spec notes this improves
        # response time, and general conditions are not what we quote on.
        "spotDDSMConditionsOnly": True,
        "requestedEquipments": equipments,
    }
    return payload


def _free_days(offer: dict) -> tuple[Optional[int], Optional[int], Optional[int]]:
    """
    Pull (free_time, demurrage, detention) days out of ddsmConditions.

    Tariff codes: DEM demurrage, DET detention, MER the two merged.
    """
    free_time = demurrage = detention = None
    for cond in offer.get("ddsmConditions") or []:
        code = ((cond.get("tariff") or {}).get("code") or "").upper()
        days = None
        for by_eq in cond.get("conditionsByEquipment") or []:
            n = (by_eq.get("freeDays") or {}).get("number")
            if n is not None:
                days = int(n)
                break
        if days is None:
            continue
        if code == "DEM":
            demurrage = days
        elif code == "DET":
            detention = days
        elif code == "MER":
            free_time = days
    if free_time is None:
        # Merged value absent: fall back to whichever single tariff was given.
        free_time = demurrage if demurrage is not None else detention
    return free_time, demurrage, detention


def _routing(offer: dict) -> tuple[str, Optional[str], Optional[str]]:
    """Return (routing label, vessel, service name) from the routing legs."""
    legs = offer.get("routingLegs") or []
    if not legs:
        return (offer.get("solutionDescription") or "Direct"), None, None

    first = legs[0]
    vessel = first.get("vesselName")
    voyage = first.get("voyageReference")
    if vessel and voyage:
        vessel = f"{vessel} (Voy: {voyage})"
    service = (first.get("service") or {}).get("name") or (first.get("service") or {}).get("code")

    if len(legs) == 1:
        routing = "Direct"
    else:
        vias = []
        for leg in legs[1:]:
            place = ((leg.get("legFrom") or {}).get("place") or {})
            name = place.get("name") or place.get("internalCode")
            if name and name not in vias:
                vias.append(str(name))
        routing = f"via {', '.join(vias)}" if vias else "Transhipment"
    return routing, vessel, service


def _charge_rows(eq_block: dict, bl_surcharges: list[dict],
                 request: RateSearchRequest, container_type: str) -> list[dict]:
    """
    Flatten an equipment's cargo surcharges plus the BL-level surcharges.

    `includedInBasicFreight` is honoured: such a charge is already inside
    basicOceanFreightRate and is reported for transparency but never re-added.
    """
    rows: list[dict] = []
    for source, per_bl in ((eq_block.get("matchingCargoSurcharges") or [], False),
                           (bl_surcharges or [], True)):
        for s in source:
            charge = s.get("charge") or {}
            name = charge.get("name") or charge.get("code")
            if not name:
                continue
            amount = _f(s.get("amount"))
            currency = ((s.get("chargeCurrency") or {}).get("code")) or "USD"
            already_in_freight = bool(s.get("includedInBasicFreight"))
            category, reason = classify_charge(
                charge_name=str(name),
                amount=amount,
                weight_per_container_kg=request.weight_per_container_kg,
                container_type=container_type,
            )
            rows.append({
                "name": str(name),
                "amount": amount,
                "currency": currency,
                "category": category.value,
                "reason": reason,
                "already_in_freight": already_in_freight,
                "per_bl": per_bl,
            })
    return rows


def parse_spoton_response(payload: Any, request: RateSearchRequest
                          ) -> tuple[list[QuoteSchema], list[str]]:
    """
    Pure function: SpotOn response in, (quotes, messages) out. No network.

    The response is an array mixing SpotOffer and Message objects; a Message
    explains why no offer could be made and is surfaced rather than dropped.
    """
    quotes: list[QuoteSchema] = []
    messages: list[str] = []

    if isinstance(payload, dict):
        payload = [payload]
    if not isinstance(payload, list):
        return quotes, messages

    for idx, item in enumerate(payload):
        if not isinstance(item, dict):
            continue

        # A Message has code+description and no offerId.
        if "offerId" not in item and item.get("code") and item.get("description"):
            messages.append(f"{item['code']}: {item['description']}")
            continue

        offer_id = str(item.get("offerId") or "").strip()
        if offer_id.lower() in NO_OFFER_IDS:
            label = "sold out" if offer_id.lower() in SOLD_OUT_IDS else "no offer"
            messages.append(f"{_date_only(item.get('departureDate')) or 'sailing'}: {label}")
            continue

        quote_line = item.get("quoteLine") or {}
        surcharges = quote_line.get("surcharges") or {}
        per_equipment = surcharges.get("matchingSurchargesPerEquipmentTypes") or []
        bl_surcharges = surcharges.get("matchingBlSurcharges") or []

        routing, vessel, service = _routing(item)
        free_time, demurrage, detention = _free_days(item)
        etd = _date_only(item.get("departureDate"))
        eta = _date_only(item.get("arrivalDate"))
        transit = item.get("transitTime")
        validity_to = (quote_line.get("validityTo"))

        # Which sizes actually have a rate on this sailing.
        rate_available = {
            e.get("equipmentGroupIsoCode"): e.get("availableRate")
            for e in (quote_line.get("spotEquipments") or [])
        }

        for eq in per_equipment:
            iso = eq.get("equipmentGroupIsoCode")
            container_type = ISO_TO_CONTAINER_TYPE.get(iso, iso or "")
            if rate_available.get(iso) is False:
                messages.append(f"{etd or 'sailing'}: no rate for {container_type or iso}")
                continue

            basic = _f(eq.get("basicOceanFreightRate"))
            all_in = _f(eq.get("allInRate"))
            currency = ((eq.get("currency") or {}).get("code")) or "USD"

            rows = _charge_rows(eq, bl_surcharges, request, container_type)

            included: list[ChargeSchema] = []
            excluded: list[ChargeSchema] = []
            for r in rows:
                schema = ChargeSchema(name=r["name"], amount=r["amount"],
                                      currency=r["currency"], category=r["category"],
                                      reason=r["reason"])
                if r["category"] in (ChargeCategory.BASIC_OCEAN_FREIGHT.value,
                                     ChargeCategory.FREIGHT_SURCHARGE_INCLUDED.value):
                    included.append(schema)
                else:
                    excluded.append(schema)

            # Charges flagged includedInBasicFreight are already inside `basic`.
            addable = sum(r["amount"] for r in rows
                          if not r["already_in_freight"]
                          and r["category"] in (ChargeCategory.BASIC_OCEAN_FREIGHT.value,
                                                ChargeCategory.FREIGHT_SURCHARGE_INCLUDED.value))
            final_value = basic + addable

            warning = None
            if all_in and abs(final_value - all_in) > 1.0:
                # CMA states its own all-in figure; a gap means our classification
                # disagrees with theirs. Trust theirs and say so, rather than
                # quietly publishing a number the carrier would not honour.
                warning = (f"Computed {final_value:.2f} but CMA CGM states allInRate "
                           f"{all_in:.2f}; using the carrier figure.")
                final_value = all_in
            elif not final_value and all_in:
                final_value = all_in

            quotes.append(QuoteSchema(
                etd=etd,
                eta=eta,
                transit_time_days=int(transit) if transit is not None else None,
                routing=routing,
                free_time=free_time,
                demurrage=demurrage,
                detention=detention,
                container_type=container_type,
                container_quantity=request.container_quantity,
                service_name=service,
                vessel=vessel,
                currency=currency,
                basic_ocean_freight=round(basic, 2),
                included_freight_surcharges=included,
                excluded_charges=excluded,
                final_freight_value=round(final_value, 2),
                validity_till=standardize_date_string(validity_to) if validity_to else None,
                is_breakdown_unavailable=not rows,
                warning_message=warning,
                source="carrier_api",
                raw_reference=offer_id or f"CMA-API-{idx}",
            ))

    return quotes, messages


class CMAAPIConnector(BaseCarrierConnector):
    """CMA CGM over the SpotOn API. No browser, no profile, no display."""

    carrier_code = "CMA_CGM"
    carrier_name = "CMA CGM (API)"

    def __init__(self):
        super().__init__()
        self.base_url = os.getenv("CMA_CGM_API_BASE", DEFAULT_BASE).rstrip("/")
        self.token_url = os.getenv("CMA_CGM_API_TOKEN_URL", DEFAULT_TOKEN_URL).strip()
        self.scope = os.getenv("CMA_CGM_API_SCOPE", DEFAULT_SCOPE).strip()
        self.client_id = os.getenv("CMA_CGM_API_CLIENT_ID", "").strip()
        self.client_secret = os.getenv("CMA_CGM_API_CLIENT_SECRET", "").strip()
        self.range_header = os.getenv("CMA_CGM_API_RANGE", "0-4").strip()
        self.behalf_of = os.getenv("CMA_CGM_API_BEHALF_OF", "").strip()
        self.last_error: Optional[str] = None
        self.last_payload: Any = None
        self.last_messages: list[str] = []
        self.last_call_ms: float = 0.0
        self._token: Optional[str] = None
        self._token_expires_at: float = 0.0

    async def get_token(self) -> Optional[str]:
        """
        Exchange client credentials for a bearer token, cached until shortly
        before expiry. At 20 requests/hour, re-minting per call is not viable.
        """
        if self._token and time.time() < self._token_expires_at:
            return self._token

        data = {"grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret}
        if self.scope:
            data["scope"] = self.scope

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    self.token_url, data=data,
                    headers={"Content-Type": "application/x-www-form-urlencoded"})
        except Exception as e:
            self.last_error = f"token request failed: {type(e).__name__}: {e}"
            return None

        if resp.status_code >= 400:
            self.last_error = f"token rejected (HTTP {resp.status_code}): {resp.text[:300]}"
            return None

        try:
            body = resp.json()
        except Exception:
            self.last_error = f"token endpoint did not return JSON: {resp.text[:200]}"
            return None

        token = body.get("access_token")
        if not token:
            self.last_error = f"no access_token in token response: {str(body)[:200]}"
            return None

        expires_in = _f(body.get("expires_in")) or 3600.0
        self._token = token
        self._token_expires_at = time.time() + max(expires_in - 60, 30)
        return token

    def _headers(self, token: str) -> dict:
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "range": self.range_header,
        }

    async def login(self) -> bool:
        """Verify configuration, then prove the credentials mint a token."""
        missing = [n for n, v in (("CMA_CGM_API_CLIENT_ID", self.client_id),
                                  ("CMA_CGM_API_CLIENT_SECRET", self.client_secret))
                   if not v]
        if missing:
            self.last_error = f"not configured: {', '.join(missing)} unset"
            return False
        return await self.get_token() is not None

    async def search_spoton(self, request: RateSearchRequest,
                            container_types: list[str]) -> tuple[CarrierResultStatus, Any]:
        """One POST to /spotOn/search covering every requested container size."""
        token = await self.get_token()
        if not token:
            return CarrierResultStatus.LOGIN_FAILED, None

        url = f"{self.base_url}{SEARCH_PATH}"
        params = {"behalfOf": self.behalf_of} if self.behalf_of else None
        payload = build_search_payload(request, container_types)

        started = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=90.0) as client:
                resp = await client.post(url, json=payload, params=params,
                                         headers=self._headers(token))
                if resp.status_code == 401:
                    # Token may have expired mid-batch: re-mint once and retry.
                    self._token = None
                    retry = await self.get_token()
                    if retry:
                        resp = await client.post(url, json=payload, params=params,
                                                 headers=self._headers(retry))
        except httpx.TimeoutException:
            self.last_error = f"timed out after 90s calling {url}"
            return CarrierResultStatus.TIMEOUT, None
        except Exception as e:
            self.last_error = f"{type(e).__name__}: {e}"
            return CarrierResultStatus.SERVICE_UNAVAILABLE, None
        finally:
            self.last_call_ms = (time.perf_counter() - started) * 1000

        return self._interpret(resp, url)

    def _interpret(self, resp: httpx.Response, url: str) -> tuple[CarrierResultStatus, Any]:
        """Map the documented status codes onto the system's result statuses."""
        if resp.status_code == 401:
            self.last_error = f"auth rejected (401): {resp.text[:300]}"
            return CarrierResultStatus.LOGIN_FAILED, None
        if resp.status_code == 403:
            self.last_error = ("403 IRT_ERR insufficient rights — the token is valid but "
                               "this application may lack the instantquote:read:be scope")
            return CarrierResultStatus.LOGIN_FAILED, None
        if resp.status_code == 400:
            # The spec enumerates these; the code tells us which input was wrong.
            self.last_error = f"400 bad request: {resp.text[:400]}"
            return CarrierResultStatus.INVALID_SEARCH_INPUT, None
        if resp.status_code == 404:
            self.last_error = f"endpoint not found: {url}"
            return CarrierResultStatus.CONNECTOR_NOT_AVAILABLE, None
        if resp.status_code == 416:
            self.last_error = f"416 range not satisfiable (range header '{self.range_header}')"
            return CarrierResultStatus.EXTRACTION_FAILED, None
        if resp.status_code == 429:
            self.last_error = "rate limited — the portal quota is 20 requests/hour"
            return CarrierResultStatus.SERVICE_UNAVAILABLE, None
        if resp.status_code == 503:
            self.last_error = "503 QUO_UNA — SpotOn temporarily unavailable"
            return CarrierResultStatus.SERVICE_UNAVAILABLE, None
        if resp.status_code >= 500:
            self.last_error = f"HTTP {resp.status_code}: {resp.text[:300]}"
            return CarrierResultStatus.SERVICE_UNAVAILABLE, None
        if resp.status_code >= 400:
            self.last_error = f"HTTP {resp.status_code}: {resp.text[:300]}"
            return CarrierResultStatus.EXTRACTION_FAILED, None

        try:
            payload = resp.json()
        except Exception:
            self.last_error = f"response was not JSON: {resp.text[:300]}"
            return CarrierResultStatus.EXTRACTION_FAILED, None

        self.last_payload = payload
        explain = resp.headers.get("cma-func-explain")
        if explain and explain.upper() != "INQ_OK":
            self.last_messages.append(f"cma-func-explain: {explain}")
        # 206 Partial Content is a documented success: some sizes were adjusted.
        return CarrierResultStatus.AVAILABLE_QUOTES_FOUND, payload

    async def run_full_search(self, request: RateSearchRequest
                              ) -> tuple[CarrierResultStatus, list[QuoteSchema]]:
        """One call for all requested sizes, then split the response per size."""
        if not await self.login():
            print(f"[CMA-API] not configured: {self.last_error}")
            return CarrierResultStatus.CONNECTOR_NOT_AVAILABLE, []

        container_types = request.container_types or [request.container_type]
        self.last_messages = []

        status, payload = await self.search_spoton(request, container_types)
        print(f"[CMA-API] {'+'.join(container_types)} "
              f"{request.origin}->{request.destination}: "
              f"{status.value} in {self.last_call_ms:.0f}ms")
        if payload is None:
            print(f"[CMA-API] {self.last_error}")
            return status, []

        quotes, messages = parse_spoton_response(payload, request)
        self.last_messages.extend(messages)
        for m in messages[:5]:
            print(f"[CMA-API] {m}")

        if not quotes:
            self.last_error = "; ".join(messages) or "no priced offers returned"
            return CarrierResultStatus.NO_QUOTES_AVAILABLE, []

        if request.search_mode == "quick":
            return CarrierResultStatus.AVAILABLE_QUOTES_FOUND, \
                self._cheapest_per_type(quotes)
        return CarrierResultStatus.AVAILABLE_QUOTES_FOUND, quotes

    @staticmethod
    def _cheapest_per_type(quotes: list[QuoteSchema]) -> list[QuoteSchema]:
        """Quick mode: the cheapest priced sailing for each container size."""
        best: dict[str, QuoteSchema] = {}
        for q in quotes:
            if not q.final_freight_value:
                continue
            key = q.container_type or ""
            if key not in best or q.final_freight_value < best[key].final_freight_value:
                best[key] = q
        return list(best.values())

    # ── Abstract members the base class requires. There is no page to drive, so
    #    the browser-shaped steps collapse into the single call above. ──────────

    async def search_quotes(self, request: RateSearchRequest) -> CarrierResultStatus:
        status, _ = await self.search_spoton(
            request, request.container_types or [request.container_type])
        return status

    async def extract_quote_list(self) -> list[dict]:
        return [x for x in (self.last_payload or []) if isinstance(x, dict)]

    async def open_price_breakdown(self, quote_ref: dict) -> bool:
        return True  # the breakdown arrives with the offer

    async def extract_charge_breakdown(self) -> list[dict]:
        return []

    async def normalize_result(self, raw_quote: dict, raw_charges: list[dict]) -> QuoteSchema:
        quotes, _ = parse_spoton_response([raw_quote], self.current_request)
        return quotes[0] if quotes else QuoteSchema()

    async def close(self, force: bool = False):
        return  # nothing to tear down
