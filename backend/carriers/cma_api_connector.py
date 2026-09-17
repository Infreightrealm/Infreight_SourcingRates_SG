"""
CMA CGM API Connector — EXPERIMENTAL.

An alternative to the Playwright connector (`cma_connector.py`) that talks to the
CMA CGM REST API instead of driving a browser. Nothing imports this by default:
it is only used when CMA_CGM_USE_API=true, so the live scraping path is unchanged
until that flag is deliberately set.

WHY IT MATTERS
    The browser connector exists mainly to look like a human to CMA CGM's bot
    defences — that is the reason the office laptop runs the crawls at all. An
    authenticated API call has no bot problem, so if this path works, CMA CGM can
    run from the cloud permanently and finish in seconds rather than minutes.

TARGET API
    "CMA CGM API SpotOn" (PRICING_API, v2.6.0) — POST GetSpotOn returns spot
    offers; POST CreateQuotationFromSpotOffer converts one into a quotation. Only
    GetSpotOn is used here: sourcing needs the price, not a booked quotation.

    Both methods are secured with OAuth2, not a bare API key, so this connector
    exchanges client credentials for a bearer token and caches it until expiry.

CONFIGURATION (all via env — never hardcode credentials)
    CMA_CGM_USE_API            "true" to route CMA_CGM through this connector.
    CMA_CGM_API_BASE           gateway base URL, e.g. https://apis.cma-cgm.net
    CMA_CGM_API_TOKEN_URL      OAuth2 token endpoint (client_credentials grant).
    CMA_CGM_API_CLIENT_ID      OAuth2 client id.
    CMA_CGM_API_CLIENT_SECRET  OAuth2 client secret.
    CMA_CGM_API_SCOPE          optional scope for the token request.
    CMA_CGM_API_KEY            optional APIM subscription key, sent alongside the
                               bearer token when the gateway also requires it.
    CMA_CGM_API_KEY_HEADER     header for that key. Default "KeyId".
    CMA_CGM_API_SPOTON_PATH    path of the GetSpotOn method.

    These are configuration rather than constants because they come straight from
    the Swagger tab of the SpotOn product page — filling them in needs no code
    change.

STATUS
    OAuth2 token exchange, POST transport, error mapping, isolation and charge
    classification are written and tested against a local fake gateway. The
    request body in `build_payload` and the response mapping in FIELD_ALIASES are
    provisional: they have NOT been checked against the real SpotOn contract.
    Export the Swagger for PRICING_API v2.6.0 and both become exact.
"""
from __future__ import annotations

import os
import time
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


def api_enabled() -> bool:
    """True only when the operator has explicitly opted in."""
    return os.getenv("CMA_CGM_USE_API", "false").strip().lower() in ("true", "1", "yes")


# Field-name aliases. The first key present in a response object wins. Extend
# these once the live response shape is known rather than rewriting the parser.
FIELD_ALIASES: dict[str, tuple[str, ...]] = {
    "etd": ("etd", "departureDate", "sailingDate", "departure", "polEtd", "estimatedDeparture"),
    "eta": ("eta", "arrivalDate", "arrival", "podEta", "estimatedArrival"),
    "transit_time_days": ("transitTime", "transitTimeDays", "transitDays", "totalTransitTime"),
    "vessel": ("vessel", "vesselName", "firstVesselName"),
    "service_name": ("service", "serviceName", "serviceCode", "loop"),
    "currency": ("currency", "currencyCode", "priceCurrency"),
    "total_price": ("totalPrice", "total", "amount", "totalAmount", "price", "grandTotal"),
    "validity_till": ("validityTo", "validUntil", "expiryDate", "validityEndDate", "quoteValidTo"),
    "container_type": ("containerType", "equipmentType", "equipmentSize", "isoCode"),
    "routing": ("routing", "routingType", "via"),
}

# Names under which a response may nest its per-charge breakdown.
CHARGE_LIST_KEYS = ("charges", "chargeList", "surcharges", "priceDetails",
                    "rateDetails", "lineItems", "breakdown", "costBreakdown")

# Names under which a response may nest the list of priced sailings.
QUOTE_LIST_KEYS = ("spotOffers", "spotOffer", "offers", "rates", "quotations",
                   "quotes", "results", "spotRates", "products", "items", "data")

# Fields that mark an object as a sailing rather than a charge line. A charge has
# a name and an amount; a sailing has dates, a vessel, or a headline total. Used to
# stop the fallback scan picking a long list of charges over a short list of
# sailings — which it otherwise does, since charges usually outnumber offers.
QUOTE_MARKERS = frozenset(
    alias.lower()
    for field in ("etd", "eta", "transit_time_days", "vessel", "service_name",
                  "total_price", "validity_till")
    for alias in FIELD_ALIASES[field]
)

CONTAINER_TYPE_TO_ISO = {
    "DRY 20": "22G1",
    "DRY 40": "42G1",
    "DRY 40H": "45G1",
}


def _first(obj: dict, names: tuple[str, ...]) -> Any:
    """Return the first present, non-empty value among `names` (case-insensitive)."""
    lowered = {k.lower(): v for k, v in obj.items()}
    for n in names:
        v = lowered.get(n.lower())
        if v not in (None, "", []):
            return v
    return None


def _as_float(v: Any) -> float:
    if v is None:
        return 0.0
    if isinstance(v, (int, float)):
        return float(v)
    try:
        return float(str(v).replace(",", "").replace("$", "").strip())
    except (ValueError, AttributeError):
        return 0.0


def find_quote_list(payload: Any) -> list[dict]:
    """
    Locate the list of priced sailings inside an arbitrary response body.

    Tries named keys first, then falls back to the longest list of dicts anywhere
    in the document — which survives a response wrapped in an envelope we did not
    anticipate.
    """
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    if not isinstance(payload, dict):
        return []

    for key in QUOTE_LIST_KEYS:
        for k, v in payload.items():
            if k.lower() == key.lower() and isinstance(v, list):
                dicts = [x for x in v if isinstance(x, dict)]
                if dicts:
                    return dicts

    def looks_like_quotes(dicts: list[dict]) -> bool:
        """True when these objects carry sailing fields rather than charge fields."""
        if not dicts:
            return False
        keys = {k.lower() for k in dicts[0]}
        return bool(keys & QUOTE_MARKERS)

    best: list[dict] = []

    def walk(node: Any, key_name: str = "") -> None:
        nonlocal best
        if isinstance(node, list):
            # Never mistake a nested charge breakdown for the list of sailings.
            if key_name.lower() not in {k.lower() for k in CHARGE_LIST_KEYS}:
                dicts = [x for x in node if isinstance(x, dict)]
                if looks_like_quotes(dicts) and len(dicts) > len(best):
                    best = dicts
            for x in node:
                walk(x, key_name)
        elif isinstance(node, dict):
            for k, v in node.items():
                walk(v, k)

    walk(payload)
    return best


def extract_charges(quote_obj: dict, request: RateSearchRequest,
                    container_type: str) -> list[dict]:
    """
    Pull the charge breakdown out of one quote object and classify each line with
    the same classifier every other connector uses, so an API-sourced quote is
    categorised identically to a scraped one.
    """
    raw_list: list[dict] = []
    for key in CHARGE_LIST_KEYS:
        found = _first(quote_obj, (key,))
        if isinstance(found, list):
            raw_list = [c for c in found if isinstance(c, dict)]
            if raw_list:
                break

    charges: list[dict] = []
    for c in raw_list:
        name = _first(c, ("name", "chargeName", "description", "label", "code", "chargeCode"))
        amount = _as_float(_first(c, ("amount", "value", "price", "total", "chargeAmount")))
        currency = _first(c, ("currency", "currencyCode")) or "USD"
        if not name:
            continue
        category, reason = classify_charge(
            charge_name=str(name),
            amount=amount,
            weight_per_container_kg=request.weight_per_container_kg,
            container_type=container_type,
        )
        charges.append({
            "name": str(name),
            "amount": amount,
            "currency": str(currency),
            "category": category.value,
            "reason": reason,
        })
    return charges


def parse_rate_payload(payload: Any, request: RateSearchRequest,
                       container_type: str) -> list[QuoteSchema]:
    """
    Pure function: response body in, QuoteSchema list out. No network, no browser.

    Being pure is what makes this testable against a saved response, which is the
    one thing the scraping connectors cannot do.
    """
    quotes: list[QuoteSchema] = []

    for idx, q in enumerate(find_quote_list(payload)):
        charges = extract_charges(q, request, container_type)

        basic = 0.0
        included: list[ChargeSchema] = []
        excluded: list[ChargeSchema] = []
        for c in charges:
            schema = ChargeSchema(name=c["name"], amount=c["amount"],
                                  currency=c["currency"], category=c["category"],
                                  reason=c.get("reason"))
            if c["category"] == ChargeCategory.BASIC_OCEAN_FREIGHT.value:
                basic += c["amount"]
            elif c["category"] == ChargeCategory.FREIGHT_SURCHARGE_INCLUDED.value:
                included.append(schema)
            else:
                excluded.append(schema)

        final_value = basic + sum(c.amount for c in included)
        if final_value == 0:
            # No usable breakdown — fall back to the headline total so a sailing
            # that really is priced never surfaces as an empty row.
            final_value = _as_float(_first(q, FIELD_ALIASES["total_price"]))
            basic = final_value

        transit = _first(q, FIELD_ALIASES["transit_time_days"])
        try:
            transit = int(transit) if transit is not None else None
        except (TypeError, ValueError):
            transit = None

        quotes.append(QuoteSchema(
            etd=standardize_date_string(_first(q, FIELD_ALIASES["etd"])),
            eta=standardize_date_string(_first(q, FIELD_ALIASES["eta"])),
            transit_time_days=transit,
            routing=_first(q, FIELD_ALIASES["routing"]) or "Direct",
            container_type=container_type,
            container_quantity=request.container_quantity,
            service_name=_first(q, FIELD_ALIASES["service_name"]),
            vessel=_first(q, FIELD_ALIASES["vessel"]),
            currency=_first(q, FIELD_ALIASES["currency"]) or "USD",
            basic_ocean_freight=round(basic, 2),
            included_freight_surcharges=included,
            excluded_charges=excluded,
            final_freight_value=round(final_value, 2),
            validity_till=standardize_date_string(_first(q, FIELD_ALIASES["validity_till"])),
            is_breakdown_unavailable=not charges,
            source="carrier_api",
            raw_reference=f"CMA-API-{idx}",
        ))

    return quotes


class CMAAPIConnector(BaseCarrierConnector):
    """CMA CGM over REST. No browser, no profile, no display."""

    carrier_code = "CMA_CGM"
    carrier_name = "CMA CGM (API)"

    def __init__(self):
        super().__init__()
        self.base_url = os.getenv("CMA_CGM_API_BASE", "https://apis.cma-cgm.net").rstrip("/")
        self.token_url = os.getenv("CMA_CGM_API_TOKEN_URL", "").strip()
        self.client_id = os.getenv("CMA_CGM_API_CLIENT_ID", "").strip()
        self.client_secret = os.getenv("CMA_CGM_API_CLIENT_SECRET", "").strip()
        self.scope = os.getenv("CMA_CGM_API_SCOPE", "").strip()
        self.api_key = os.getenv("CMA_CGM_API_KEY", "").strip()
        self.key_header = os.getenv("CMA_CGM_API_KEY_HEADER", "KeyId").strip()
        self.spoton_path = os.getenv("CMA_CGM_API_SPOTON_PATH", "").strip()
        self.last_error: Optional[str] = None
        self.last_payload: Any = None
        self.last_call_ms: float = 0.0
        self._token: Optional[str] = None
        self._token_expires_at: float = 0.0

    async def get_token(self) -> Optional[str]:
        """
        Exchange client credentials for a bearer token, cached until shortly
        before it expires. SpotOn is OAuth2-secured, so every call needs this.
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

        # Refresh a minute early so a long batch never runs on an expiring token.
        expires_in = float(body.get("expires_in", 3600))
        self._token = token
        self._token_expires_at = time.time() + max(expires_in - 60, 30)
        return token

    def _headers(self, token: str) -> dict:
        headers = {"Authorization": f"Bearer {token}",
                   "Accept": "application/json",
                   "Content-Type": "application/json"}
        if self.api_key:
            headers[self.key_header] = self.api_key
        return headers

    async def login(self) -> bool:
        """Verify configuration, then prove the credentials mint a token."""
        missing = [n for n, v in (
            ("CMA_CGM_API_TOKEN_URL", self.token_url),
            ("CMA_CGM_API_CLIENT_ID", self.client_id),
            ("CMA_CGM_API_CLIENT_SECRET", self.client_secret),
            ("CMA_CGM_API_SPOTON_PATH", self.spoton_path),
        ) if not v]
        if missing:
            self.last_error = f"not configured: {', '.join(missing)} unset"
            return False
        return await self.get_token() is not None

    def build_payload(self, request: RateSearchRequest, container_type: str) -> dict:
        """
        JSON body for POST GetSpotOn.

        PROVISIONAL — field names are a best guess until the SpotOn Swagger is
        available. Collected here so there is exactly one place to correct them.
        """
        return {
            "placeOfLoading": request.origin,
            "placeOfDischarge": request.destination,
            "departureDate": request.departure_date,
            "containers": [{
                "type": CONTAINER_TYPE_TO_ISO.get(container_type, container_type),
                "quantity": request.container_quantity,
                "weight": request.weight_per_container_kg,
            }],
            "commodity": request.commodity,
        }

    async def fetch_rates(self, request: RateSearchRequest,
                          container_type: str) -> tuple[CarrierResultStatus, Any]:
        """One POST to GetSpotOn. Returns (status, parsed JSON or None)."""
        token = await self.get_token()
        if not token:
            return CarrierResultStatus.LOGIN_FAILED, None

        url = f"{self.base_url}{self.spoton_path}"
        payload = self.build_payload(request, container_type)
        started = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                resp = await client.post(url, json=payload, headers=self._headers(token))
        except httpx.TimeoutException:
            self.last_error = f"timed out after 60s calling {url}"
            return CarrierResultStatus.TIMEOUT, None
        except Exception as e:
            self.last_error = f"{type(e).__name__}: {e}"
            return CarrierResultStatus.SERVICE_UNAVAILABLE, None
        finally:
            self.last_call_ms = (time.perf_counter() - started) * 1000

        if resp.status_code == 401:
            # The cached token may simply have expired mid-batch. Mint a new one
            # and retry once before calling it a login failure.
            self._token = None
            retry_token = await self.get_token()
            if retry_token:
                try:
                    async with httpx.AsyncClient(timeout=60.0) as client:
                        resp = await client.post(url, json=payload,
                                                 headers=self._headers(retry_token))
                except Exception as e:
                    self.last_error = f"retry after 401 failed: {type(e).__name__}: {e}"
                    return CarrierResultStatus.SERVICE_UNAVAILABLE, None
            if resp.status_code == 401:
                self.last_error = f"auth rejected (401): {resp.text[:300]}"
                return CarrierResultStatus.LOGIN_FAILED, None
        if resp.status_code == 403:
            self.last_error = (f"forbidden (403) — the token is valid but this "
                               f"application may not be subscribed to SpotOn: {resp.text[:200]}")
            return CarrierResultStatus.LOGIN_FAILED, None
        if resp.status_code == 404:
            self.last_error = f"endpoint not found: {url}"
            return CarrierResultStatus.CONNECTOR_NOT_AVAILABLE, None
        if resp.status_code == 429:
            self.last_error = "rate limited by CMA CGM gateway (portal quota is 20/hour)"
            return CarrierResultStatus.SERVICE_UNAVAILABLE, None
        if resp.status_code >= 400:
            self.last_error = f"HTTP {resp.status_code}: {resp.text[:300]}"
            return CarrierResultStatus.INVALID_SEARCH_INPUT, None

        try:
            payload = resp.json()
        except Exception:
            self.last_error = f"response was not JSON: {resp.text[:300]}"
            return CarrierResultStatus.EXTRACTION_FAILED, None

        self.last_payload = payload
        return CarrierResultStatus.AVAILABLE_QUOTES_FOUND, payload

    async def run_full_search(self, request: RateSearchRequest
                              ) -> tuple[CarrierResultStatus, list[QuoteSchema]]:
        """Fetch every requested container type and return normalised quotes."""
        if not await self.login():
            print(f"[CMA-API] not configured: {self.last_error}")
            return CarrierResultStatus.CONNECTOR_NOT_AVAILABLE, []

        all_quotes: list[QuoteSchema] = []
        last_status = CarrierResultStatus.NO_QUOTES_AVAILABLE

        for container_type in (request.container_types or [request.container_type]):
            status, payload = await self.fetch_rates(request, container_type)
            print(f"[CMA-API] {container_type}: {status.value} in {self.last_call_ms:.0f}ms")
            if payload is None:
                last_status = status
                continue
            parsed = parse_rate_payload(payload, request, container_type)
            if parsed:
                all_quotes.extend(parsed)
                last_status = CarrierResultStatus.AVAILABLE_QUOTES_FOUND
            elif last_status != CarrierResultStatus.AVAILABLE_QUOTES_FOUND:
                last_status = CarrierResultStatus.NO_QUOTES_AVAILABLE

        if not all_quotes:
            return last_status, []
        return CarrierResultStatus.AVAILABLE_QUOTES_FOUND, all_quotes

    # ── Abstract members the base class requires. There is no page to drive, so
    #    the browser-shaped steps collapse into the single call above. ──────────

    async def search_quotes(self, request: RateSearchRequest) -> CarrierResultStatus:
        status, _ = await self.fetch_rates(
            request, request.container_type or "DRY 40H")
        return status

    async def extract_quote_list(self) -> list[dict]:
        return find_quote_list(self.last_payload) if self.last_payload else []

    async def open_price_breakdown(self, quote_ref: dict) -> bool:
        return True  # the breakdown arrives with the quote

    async def extract_charge_breakdown(self) -> list[dict]:
        return []

    async def normalize_result(self, raw_quote: dict, raw_charges: list[dict]) -> QuoteSchema:
        quotes = parse_rate_payload([raw_quote], self.current_request,
                                    raw_quote.get("container_type", "DRY 40H"))
        return quotes[0] if quotes else QuoteSchema()

    async def close(self, force: bool = False):
        return  # nothing to tear down
