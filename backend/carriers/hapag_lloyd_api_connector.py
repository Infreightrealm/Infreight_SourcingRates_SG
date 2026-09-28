# -*- coding: utf-8 -*-
"""
Hapag-Lloyd Prices API Connector (REST API v2.1.4).

Provides real-time rate lookup via Hapag-Lloyd's Official Prices API.
Eliminates headless browser overhead, DOM fragility, and profile collisions.
Outputs standardized QuoteSchema objects identical to InFreight's sourcing format.

Authentication:
- X-IBM-Client-Id (from env HAPAG_API_CLIENT_ID)
- X-IBM-Client-Secret (from env HAPAG_API_CLIENT_SECRET)
- customerIdentifier (from env HAPAG_API_CUSTOMER_EMAIL, default: BOOKINGSG@IN-FREIGHT.COM)
"""
import os
import re
import json
import asyncio
import time
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Dict, Any, Tuple
import httpx

from models.schemas import (
    RateSearchRequest,
    QuoteSchema,
    ChargeSchema,
    CarrierResultStatus,
    ChargeCategory
)
from carriers.base_connector import BaseCarrierConnector
from services.port_manager import PortManager
from services.normalizer import standardize_date_string, classify_and_organize_charges


# ISO container mapping for Hapag-Lloyd Prices API
CONTAINER_TO_ISO = {
    "DRY 20": "22GP",
    "20GP": "22GP",
    "20'GP": "22GP",
    "20STD": "22GP",
    "DRY 40": "42GP",
    "40GP": "42GP",
    "40'GP": "42GP",
    "40STD": "42GP",
    "DRY 40H": "45GP",
    "40HQ": "45GP",
    "40HC": "45GP",
    "40'HQ": "45GP",
    "40'HC": "45GP",
}

ISO_TO_CONTAINER = {
    "22GP": "DRY 20",
    "42GP": "DRY 40",
    "45GP": "DRY 40H",
    "45HC": "DRY 40H",
}

# Error reason mapping from OpenAPI spec
ERROR_REASON_EXPLANATIONS = {
    "MISSING_INFORMATION": "Hapag-Lloyd encountered an error calculating the quote for this route.",
    "RESTRICTIONS": "The requested offer is temporarily restricted by Hapag-Lloyd.",
    "CAN_NOT_BE_OFFERED": "This routing is currently unavailable for online quotation.",
    "USER_UNKNOWN": "Customer account is unrecognized or being provisioned.",
    "MISSING_PERMISSIONS": "Account lacks required permissions for online price retrieval on this lane.",
    "TECHNICAL_ERROR": "Hapag-Lloyd experienced a temporary technical calculation error.",
    "JONES_ACT": "Route involves US territory restricted under the Jones Act.",
    "OPTIMIZED_ROUTING": "This route requires manual sales representative handling.",
    "INLAND_UNAVAILABLE": "Inland haulage is unavailable to/from the requested location.",
    "CAPACITY": "Request exceeds available vessel capacity on this departure.",
    "INLAND_RESTRICTIONS": "Inland routing restrictions apply to this location.",
    "DANGEROUS_GOODS_RESTRICTION": "Dangerous goods quotation is not available for this request.",
    "COMMODITY_PROHIBITED_FOR_REEFER_AND_SPOT": "Requested commodity is prohibited for spot rates (try FAK).",
    "IN_GAUGE_PROHIBITED": "Offer temporarily unavailable for special containers.",
    "QQS_CAN_NOT_BE_OFFERED_FOR_LIGHT_USER": "Spot quotes require verified enterprise customer tier.",
    "SOC_PROHIBITED_FOR_SPOT": "Shipper Owned Containers prohibited for spot products.",
    "NO_ROUTE_FOR_EQUIPMENT": "No active routing available for the requested container equipment.",
    "DEPARTURE_DATE_TO_EARLY": "Departure date must be at least 4 calendar days in the future.",
    "OPTIMIZED_ROUTINGS": "This route cannot be quoted online; contact your Hapag-Lloyd sales representative.",
    "NO_OFFERS_FOUND_FOR_ROUTE": "No Hapag-Lloyd offers are currently available for this route.",
}


class RateLimiter:
    """Token-bucket rate limiter to strictly respect Tryout/Production rate limits."""
    def __init__(self, min_interval_seconds: float = 1.0):
        self.min_interval = min_interval_seconds
        self._last_call = 0.0
        self._lock = asyncio.Lock()

    async def acquire(self):
        async with self._lock:
            now = time.time()
            elapsed = now - self._last_call
            if elapsed < self.min_interval:
                await asyncio.sleep(self.min_interval - elapsed)
            self._last_call = time.time()


# Global rate limiter instance (1 call / sec default for Tryout tier)
_HAPAG_RATE_LIMITER = RateLimiter(min_interval_seconds=1.0)


class HapagLloydAPIConnector(BaseCarrierConnector):
    """
    Direct REST API connector for Hapag-Lloyd Prices API v2.1.4.
    """
    carrier_code = "HAPAG_LLOYD"
    carrier_name = "Hapag-Lloyd"

    DEFAULT_BASE_URL = "https://api.hlag.com/hlag/external/v2/quotation-booking-engine/external"
    MOCK_BASE_URL = "https://mock.api-portal.hlag.com/v2/quotation-booking-engine/external"

    def __init__(self):
        super().__init__()
        self.port_manager = PortManager()
        self.client_id = os.getenv("HAPAG_API_CLIENT_ID", "").strip()
        self.client_secret = os.getenv("HAPAG_API_CLIENT_SECRET", "").strip()
        self.customer_email = os.getenv("HAPAG_API_CUSTOMER_EMAIL", "BOOKINGSG@IN-FREIGHT.COM").strip()
        self.base_url = os.getenv("HAPAG_API_BASE_URL", self.DEFAULT_BASE_URL).rstrip("/")
        self.use_mock_api = os.getenv("HAPAG_API_USE_MOCK", "false").lower() in ("true", "1", "yes")

        # job_service calls run_full_search once per container type; all sizes are fetched on the
        # first call and cached here so a 3-size search costs 3 API calls, not 9 (Tryout = 40/day).
        self._route_cache: Dict[tuple, Tuple[CarrierResultStatus, List[QuoteSchema]]] = {}
        # Human-readable reason for a failed search, surfaced by job_service as the carrier error.
        self.last_error_message: Optional[str] = None

        # Load Freetime Database
        self.freetime_config = self._load_freetime_config()

    def _load_freetime_config(self) -> dict:
        try:
            cfg_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "config",
                "hapag_freetime.json"
            )
            if os.path.exists(cfg_path):
                with open(cfg_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            print(f"[HAPAG_API] Warning: Could not load freetime config: {e}")
        return {}

    async def login(self) -> bool:
        """API connectors do not require browser login sessions."""
        return bool(self.client_id and self.client_secret)

    async def search_quotes(self, request: RateSearchRequest) -> CarrierResultStatus:
        """Required abstract method implementation; delegates to run_full_search."""
        status, _ = await self.run_full_search(request)
        return status

    async def extract_quote_list(self) -> list[dict]:
        return []

    async def open_price_breakdown(self, quote_ref: dict) -> bool:
        return True

    async def extract_charge_breakdown(self) -> list[dict]:
        return []

    async def _run_batch_route(self, req: RateSearchRequest) -> Tuple[CarrierResultStatus, List[QuoteSchema]]:
        """Batch (RFQ) mode: the base implementation drives a browser page, so answer from the API directly."""
        return await self._fetch_all_container_types(req)

    async def _reset_between_routes(self, relogin: bool = False) -> None:
        """No browser session to reset between batch routes."""
        return None

    async def normalize_result(self, raw_quote: dict, raw_charges: list[dict]) -> QuoteSchema:
        return QuoteSchema()

    def resolve_locode(self, location_str: str) -> Optional[str]:
        """
        Resolves a free-text port name or string (e.g. 'Singapore', 'Hamburg, Germany [DEHAM]')
        into a valid 5-letter UN/LOCODE.
        """
        if not location_str:
            return None
        text = location_str.strip()

        # 1. Check for bracketed or parenthesized LOCODE e.g. [DEHAM] or (SGSIN)
        match = re.search(r'[\[\(]\s*([A-Za-z]{5})\s*[\]\)]', text)
        if match:
            return match.group(1).upper()

        # 2. Check if text is directly a 5-letter alpha code
        clean = re.sub(r'[^A-Za-z]', '', text)
        if len(clean) == 5 and text.isupper():
            return clean.upper()

        # 3. Direct common port dictionary lookup
        from services.port_manager import PORT_NAME_KEYWORD_MAP
        clean_name = re.sub(r'[,\-].*$', '', text).strip().lower()
        if clean_name in PORT_NAME_KEYWORD_MAP:
            return PORT_NAME_KEYWORD_MAP[clean_name].upper()

        # 4. Check entire text against PORT_NAME_KEYWORD_MAP
        for k, v in PORT_NAME_KEYWORD_MAP.items():
            if k in text.lower():
                return v.upper()

        # 5. Use PortManager carrier override resolution
        try:
            resolved = self.port_manager.resolve_port_for_carrier(text, "hapag")
            if resolved and len(resolved) == 5 and resolved.isupper():
                return resolved
        except Exception:
            pass

        # 6. Fallback search via PortManager database
        try:
            search_res = self.port_manager.search_port(text)
            if search_res and len(search_res) > 0:
                code = search_res[0].get("code")
                if code and len(code) == 5:
                    return code.upper()
        except Exception:
            pass

        return None

    def _calculate_earliest_departure_date(self, requested_date_str: Optional[str]) -> str:
        """
        Hapag-Lloyd Prices API requires earliestDepartureDate to be at least 4 calendar days
        in the future. Returns ISO YYYY-MM-DD string.
        """
        min_allowed_date = datetime.now(timezone.utc).date() + timedelta(days=4)

        if not requested_date_str or requested_date_str.lower() in ("tomorrow", "today"):
            target_date = min_allowed_date
        else:
            try:
                # Attempt to parse requested date
                dt = None
                for fmt in ("%Y-%m-%d", "%d %b %Y", "%d-%b-%Y", "%d/%m/%Y", "%m/%d/%Y"):
                    try:
                        dt = datetime.strptime(requested_date_str.strip(), fmt).date()
                        break
                    except ValueError:
                        continue
                if dt and dt >= min_allowed_date:
                    target_date = dt
                else:
                    target_date = min_allowed_date
            except Exception:
                target_date = min_allowed_date

        return target_date.strftime("%Y-%m-%d")

    def _get_freetime_days(self, destination_locode: str, destination_name: str, container_type: str) -> Optional[int]:
        """Looks up standard destination demurrage/detention free time days."""
        if not self.freetime_config:
            return 4  # Default fallback

        norm_ct = "20GP" if "20" in container_type else "40GP"

        # Check by country name or destination name
        port_obj = self.port_manager.get_port_by_code(destination_locode) if destination_locode else None
        country = port_obj.get("country_name") or port_obj.get("country") if port_obj else ""

        for key, val in self.freetime_config.items():
            if (country and key.lower() in country.lower()) or (destination_name and key.lower() in destination_name.lower()):
                if isinstance(val, dict):
                    return val.get(norm_ct, val.get("40GP", 4))
                elif isinstance(val, int):
                    return val

        # Common destination fallbacks
        if destination_locode.startswith("DE"):  # Germany
            return 4
        if destination_locode.startswith("US") or destination_locode.startswith("CA"):
            return 4
        if destination_locode.startswith("SG"):  # Singapore
            return 5

        return 4

    def build_offer_request_payload(
        self,
        origin_locode: str,
        destination_locode: str,
        container_iso: str,
        quantity: int,
        weight_kg: float,
        earliest_departure_date: str,
        commodity_group: str = "FAK",
        commodity_group_number: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Constructs OpenAPI compliant OfferRequest payload."""
        commodity: Dict[str, Any] = {
            "cargoGrossWeight": int(weight_kg) if weight_kg > 0 else 20000,
            "cargoGrossWeightUnit": "KG",
            "isHazardous": False
        }
        # The API rejects commodityTypeGroup without commodityTypeGroupNumber (HTTP 400:
        # "Either both ... must be set or none of them"). Omitting both defaults to FAK.
        if commodity_group_number is not None:
            commodity["commodityTypeGroup"] = commodity_group
            commodity["commodityTypeGroupNumber"] = commodity_group_number
        return {
            "placeOfReceipt": {
                "locode": origin_locode
            },
            "placeOfDelivery": {
                "locode": destination_locode
            },
            "receiptTypeAtOrigin": "CY",
            "deliveryTypeAtDestination": "CY",
            "requestedEquipment": {
                "requestedEquipmentSizeType": container_iso,
                "requestedEquipmentUnits": max(1, min(quantity, 20)),
                "isNonOperatingReefer": False,
                "shippersOwnedContainer": False
            },
            "commodity": commodity,
            "earliestDepartureDate": earliest_departure_date,
            "productIdentifiers": [
                "QUICK_QUOTES",
                "QUICK_QUOTES_SPOT"
            ],
            "customerIdentifier": self.customer_email
        }

    async def _execute_single_price_request(
        self,
        client: httpx.AsyncClient,
        payload: Dict[str, Any]
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str], Optional[CarrierResultStatus]]:
        """Sends a single POST /prices request with rate-limiting and error handling."""
        endpoint = f"{self.base_url}/prices"
        if self.use_mock_api:
            endpoint = f"{self.MOCK_BASE_URL}/prices"

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        # Inject IBM API Gateway security headers if provided
        if self.client_id:
            headers["X-IBM-Client-Id"] = self.client_id
        if self.client_secret:
            headers["X-IBM-Client-Secret"] = self.client_secret

        await _HAPAG_RATE_LIMITER.acquire()

        try:
            start_t = time.perf_counter()
            response = await client.post(endpoint, json=payload, headers=headers, timeout=25.0)
            elapsed_ms = (time.perf_counter() - start_t) * 1000
            print(f"[HAPAG_API] POST /prices returned HTTP {response.status_code} ({elapsed_ms:.1f}ms)")

            if response.status_code in (200, 201):
                data = response.json()
                return data, None, CarrierResultStatus.AVAILABLE_QUOTES_FOUND

            # Handle 4xx / 5xx error responses
            try:
                err_data = response.json()
            except Exception:
                err_data = {}

            title = err_data.get("title") or err_data.get("detail") or response.text
            detail = err_data.get("detail", "")
            error_code = err_data.get("overarchingErrorReason") or err_data.get("type")

            friendly_msg = ERROR_REASON_EXPLANATIONS.get(error_code) or detail or title

            if response.status_code == 401:
                return None, f"Hapag-Lloyd Authentication Failed: {friendly_msg}", CarrierResultStatus.LOGIN_FAILED
            elif response.status_code == 400:
                return None, f"Invalid Search Parameters: {friendly_msg}", CarrierResultStatus.INVALID_SEARCH_INPUT
            elif response.status_code == 409:
                return None, f"Business Restriction: {friendly_msg}", CarrierResultStatus.NO_QUOTES_AVAILABLE
            else:
                return None, f"Hapag-Lloyd Gateway Error ({response.status_code}): {friendly_msg}", CarrierResultStatus.SERVICE_UNAVAILABLE

        except httpx.TimeoutException:
            return None, "Hapag-Lloyd Prices API connection timed out (>25s)", CarrierResultStatus.TIMEOUT
        except Exception as ex:
            return None, f"Hapag-Lloyd Prices API network error: {str(ex)}", CarrierResultStatus.FAILED

    @staticmethod
    def _classify_rate(rate: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Maps a Prices API rate onto the categories the portal scraper produces
        (freight charges / surcharges / export surcharges / import surcharges).
        Returns (skip, category); category None lets the shared name-based classifier decide.
        """
        if rate.get("chargeable") is False:
            return True, None
        if rate.get("unitOfMeasure") == "PERCENT":
            return False, ChargeCategory.UNCERTAIN_EXCLUDED.value
        if rate.get("seaFreightIndicator") or rate.get("chargeTypeCode") == "SEA":
            return False, ChargeCategory.BASIC_OCEAN_FREIGHT.value
        if rate.get("included"):
            # "included into lump sum": already part of the Ocean Freight amount (e.g. Carrier
            # Security Fee, shown on the portal as an assessorial of Ocean Freight). Listed, never added.
            return False, ChargeCategory.UNCERTAIN_EXCLUDED.value
        proposal = rate.get("locationProposal")
        if proposal == "BASE_PORT_FROM":
            return False, ChargeCategory.ORIGIN_CHARGE_EXCLUDED.value
        if proposal == "BASE_PORT_TO":
            return False, ChargeCategory.DESTINATION_CHARGE_EXCLUDED.value
        if proposal in ("MAIN_CARRIAGE", "PC_CARRIAGE", "ON_CARRIAGE"):
            # Main-carriage surcharges and inland pre/on-carriage are part of the freight (as on the portal)
            return False, ChargeCategory.FREIGHT_SURCHARGE_INCLUDED.value
        return False, None

    @staticmethod
    def _leg_locode(location: Any) -> Optional[str]:
        """Leg locations are UnLocation/Facility objects per the spec; tolerate plain LOCODE strings too."""
        if isinstance(location, str):
            return location.strip().upper() or None
        if isinstance(location, dict):
            code = location.get("unLocationCode") or location.get("UNLocationCode") or location.get("locode")
            return code.strip().upper() if code else None
        return None

    def _port_display_name(self, locode: str) -> str:
        port_obj = self.port_manager.get_port_by_code(locode)
        return port_obj.get("name") if port_obj and port_obj.get("name") else locode

    def _record_error_reason(self, reason: Optional[str]) -> None:
        if reason:
            explanation = ERROR_REASON_EXPLANATIONS.get(reason, reason)
            self.last_error_message = f"Hapag-Lloyd API: {explanation} ({reason})"

    def _parse_offer_response_to_quotes(
        self,
        api_data: Dict[str, Any],
        requested_container_type: str,
        destination_locode: str,
        destination_name: str,
        weight_kg: Optional[float] = None,
    ) -> List[QuoteSchema]:
        """
        Parses Hapag-Lloyd OfferResponse JSON into InFreight QuoteSchema objects.
        """
        quotes: List[QuoteSchema] = []
        offers = api_data.get("offers", [])

        if not offers:
            self._record_error_reason(api_data.get("overarchingErrorReason"))
            return quotes

        free_time_days = self._get_freetime_days(destination_locode, destination_name, requested_container_type)

        for offer in offers:
            if offer.get("errorReason") and not offer.get("equipments"):
                self._record_error_reason(offer.get("errorReason"))
                continue

            product_id = offer.get("productIdentifier", "QUICK_QUOTES")
            is_spot = (product_id == "QUICK_QUOTES_SPOT")

            # Extract ETD / ETA
            raw_etd = offer.get("placeOfReceiptDate") or offer.get("portOfLoadingDateTime")
            raw_eta = offer.get("placeOfDeliveryDateTime") or offer.get("portOfDischargeDateTime")

            etd = standardize_date_string(raw_etd)
            eta = standardize_date_string(raw_eta)
            transit_time = offer.get("transitTime")

            # Extract Validity
            raw_validity = offer.get("potentialQuotationValidTo") or offer.get("offerValidTo")
            validity_till = standardize_date_string(raw_validity)

            # Parse Legs: only Ocean legs carry vessel / service; intermodal legs are pre/on-carriage.
            ocean_legs = [
                leg for leg in offer.get("legs", [])
                if leg.get("vesselName") or leg.get("carrierServiceName") or leg.get("modeOfTransport") == "VESSEL"
            ]
            first_ocean = ocean_legs[0] if ocean_legs else {}
            vessel_name = first_ocean.get("vesselName") or "Hapag Vessel"
            voyage_no = first_ocean.get("scheduleVoyageNumber") or ""

            service_codes: List[str] = []
            for leg in ocean_legs:
                s_code = leg.get("carrierServiceName")
                if s_code and s_code not in service_codes:
                    service_codes.append(s_code)
            service_name = " / ".join(service_codes) if service_codes else "Hapag Service"

            # Transshipment ports = arrival of every ocean leg except the last one (which is the POD)
            transshipment_ports = []
            for leg in ocean_legs[:-1]:
                ts_code = self._leg_locode(leg.get("arrivalLocation"))
                if ts_code:
                    transshipment_ports.append(self._port_display_name(ts_code))

            pod_code = offer.get("portOfDischarge") or (self._leg_locode(ocean_legs[-1].get("arrivalLocation")) if ocean_legs else None)
            port_of_discharge = self._port_display_name(pod_code) if pod_code else None

            # Format Vessel String
            vessel_display = f"{vessel_name} /Performa" if not voyage_no else f"{vessel_name} (Voy: {voyage_no})"
            if is_spot:
                vessel_display = f"{vessel_display} (SPOT)"

            # Process Equipments & Rates
            equipments = offer.get("equipments", [])
            for equip in equipments:
                if equip.get("errorReason") and not equip.get("rates"):
                    self._record_error_reason(equip.get("errorReason"))
                    continue

                size_type = equip.get("requestedEquipment", {}).get("requestedEquipmentSizeType", "45GP")
                container_type = ISO_TO_CONTAINER.get(size_type, requested_container_type)

                raw_charges = []
                for r in equip.get("rates", []):
                    print(
                        f"[HAPAG_API]   rate {product_id} {size_type} {r.get('chargeTypeCode')} "
                        f"'{r.get('chargeTypeShortDescription')}' {r.get('amount')} {r.get('currency')} "
                        f"uom={r.get('unitOfMeasure')} sea={r.get('seaFreightIndicator')} included={r.get('included')} "
                        f"chargeable={r.get('chargeable')} loc={r.get('locationProposal')}"
                    )
                    skip, category = self._classify_rate(r)
                    if skip:
                        continue
                    desc = r.get("chargeTypeShortDescription") or r.get("chargeTypeCode") or "Charge"
                    if r.get("included") and category == ChargeCategory.UNCERTAIN_EXCLUDED.value:
                        desc = f"{desc} (included in Ocean Freight)"
                    amount = float(r.get("amount") or 0.0)
                    if r.get("unitOfMeasure") == "PERCENT":
                        # Percentage-based charge: not a money amount, keep it visible but out of totals
                        desc = f"{desc} ({amount:g}%)"
                        amount = 0.0
                    entry = {"name": desc, "amount": round(amount, 2), "currency": r.get("currency") or "USD"}
                    if category:
                        entry["category"] = category
                    raw_charges.append(entry)

                # Same classifier the portal scraper uses, so the result table / Excel look identical
                organized = classify_and_organize_charges(raw_charges, weight_per_container_kg=weight_kg, container_type=container_type)
                all_classified = organized["all_classified"]
                basic_ocean_freight = organized["basic_ocean_freight"]
                included_surcharges = organized["included_freight_surcharges"]
                excluded_charges = organized["excluded_charges"]
                uncertain_charges = organized["uncertain_charges"]

                # Total in the sea-freight currency; flag included charges billed in another currency
                currency = next(
                    (c["currency"] for c in all_classified if c["category"] == ChargeCategory.BASIC_OCEAN_FREIGHT.value),
                    "USD"
                ).upper()
                totalled = [
                    c for c in all_classified
                    if c["category"] in (ChargeCategory.BASIC_OCEAN_FREIGHT.value, ChargeCategory.FREIGHT_SURCHARGE_INCLUDED.value)
                ]
                final_freight_value = round(sum(c["amount"] for c in totalled if c["currency"].upper() == currency), 2)
                other_currency = [c for c in totalled if c["currency"].upper() != currency]
                warning_message = None
                if other_currency:
                    warning_message = "Not in total (different currency): " + ", ".join(
                        f"{c['name']} {c['amount']:g} {c['currency']}" for c in other_currency
                    )

                # Check Value Added Services for Free Time Override
                vas_list = equip.get("valueAddedServices", [])
                for vas in vas_list:
                    if "ADFT" in vas.get("vasCode", "") or "Free" in vas.get("name", ""):
                        ft_days = vas.get("freetimeDays")
                        if ft_days and ft_days > 0:
                            free_time_days = ft_days

                quote = QuoteSchema(
                    etd=etd,
                    eta=eta,
                    transit_time_days=transit_time,
                    service_name=service_name,
                    vessel=vessel_display,
                    routing=", ".join(transshipment_ports) if transshipment_ports else "Direct",
                    port_of_discharge=port_of_discharge,
                    free_time=f"{free_time_days} days" if free_time_days else None,
                    container_type=container_type,
                    container_quantity=1,
                    currency=currency,
                    basic_ocean_freight=round(basic_ocean_freight, 2),
                    discount=0.0,
                    included_freight_surcharges=included_surcharges,
                    excluded_charges=excluded_charges,
                    uncertain_charges=uncertain_charges,
                    final_freight_value=final_freight_value,
                    source="carrier_api",
                    raw_reference=offer.get("carrierOfferRequestReference", "HLAG-API"),
                    validity_till=validity_till,
                    is_breakdown_unavailable=False,
                    warning_message=warning_message,
                )
                quotes.append(quote)

        return quotes

    async def run_full_search(self, request: RateSearchRequest) -> Tuple[CarrierResultStatus, List[QuoteSchema]]:
        """
        Called by job_service once per container type (request.container_type). All requested
        sizes are fetched on the first call and cached; each call returns only its own size.
        """
        status, quotes = await self._fetch_all_container_types(request)
        if request.container_type:
            wanted = ISO_TO_CONTAINER.get(CONTAINER_TO_ISO.get(request.container_type.upper().strip(), ""), request.container_type)
            quotes = [q for q in quotes if q.container_type == wanted]
        return status, quotes

    async def _fetch_all_container_types(self, request: RateSearchRequest) -> Tuple[CarrierResultStatus, List[QuoteSchema]]:
        """
        Executes full rate search against Hapag-Lloyd Prices API.
        Queries each requested container size (20GP, 40GP, 40HQ) and merges results.
        """
        req_types = request.container_types or ([request.container_type] if request.container_type else ["DRY 40H"])
        cache_key = (request.origin, request.destination, request.departure_date, tuple(req_types))
        if cache_key in self._route_cache:
            print(f"[HAPAG_API] Returning cached API quotes for {cache_key[:3]} (container_type='{request.container_type}')")
            return self._route_cache[cache_key]

        result = await self._query_prices_api(request, req_types)
        self._route_cache[cache_key] = result
        return result

    async def _query_prices_api(self, request: RateSearchRequest, req_types: List[str]) -> Tuple[CarrierResultStatus, List[QuoteSchema]]:
        print(f"[HAPAG_API] Starting API rate search: {request.origin} -> {request.destination}")
        self.last_error_message = None

        if not self.use_mock_api and not (self.client_id and self.client_secret):
            self.last_error_message = "Hapag-Lloyd API credentials missing: set HAPAG_API_CLIENT_ID and HAPAG_API_CLIENT_SECRET on the backend."
            print(f"[HAPAG_API] Error: {self.last_error_message}")
            return CarrierResultStatus.LOGIN_FAILED, []

        # Resolve Origin and Destination UN/LOCODEs
        origin_locode = self.resolve_locode(request.origin)
        destination_locode = self.resolve_locode(request.destination)

        self.submitted_origin = origin_locode
        self.submitted_destination = destination_locode
        self.matched_origin = origin_locode
        self.matched_destination = destination_locode

        if not origin_locode or not destination_locode:
            err_msg = f"Could not resolve UN/LOCODE for Origin='{request.origin}' ({origin_locode}) or Destination='{request.destination}' ({destination_locode})"
            print(f"[HAPAG_API] Error: {err_msg}")
            self.last_error_message = err_msg
            return CarrierResultStatus.INVALID_SEARCH_INPUT, []

        departure_date = self._calculate_earliest_departure_date(request.departure_date)

        # Determine container types to query
        iso_types = []
        for c in req_types:
            iso = CONTAINER_TO_ISO.get(c.upper().strip(), "45GP")
            if iso not in iso_types:
                iso_types.append(iso)

        all_quotes: List[QuoteSchema] = []
        last_status = CarrierResultStatus.NO_QUOTES_AVAILABLE
        last_error = None

        async with httpx.AsyncClient(timeout=30.0) as client:
            for iso in iso_types:
                mapped_container_name = ISO_TO_CONTAINER.get(iso, "DRY 40H")
                payload = self.build_offer_request_payload(
                    origin_locode=origin_locode,
                    destination_locode=destination_locode,
                    container_iso=iso,
                    quantity=request.container_quantity or 1,
                    weight_kg=request.weight_per_container_kg or 20000.0,
                    earliest_departure_date=departure_date,
                    commodity_group="FAK"
                )

                data, err, status = await self._execute_single_price_request(client, payload)

                if status == CarrierResultStatus.AVAILABLE_QUOTES_FOUND and data:
                    parsed = self._parse_offer_response_to_quotes(
                        api_data=data,
                        requested_container_type=mapped_container_name,
                        destination_locode=destination_locode,
                        destination_name=request.destination,
                        weight_kg=request.weight_per_container_kg,
                    )
                    if parsed:
                        all_quotes.extend(parsed)
                        last_status = CarrierResultStatus.AVAILABLE_QUOTES_FOUND
                else:
                    if err:
                        last_error = err
                    if status != CarrierResultStatus.NO_QUOTES_AVAILABLE and last_status != CarrierResultStatus.AVAILABLE_QUOTES_FOUND:
                        last_status = status

        if all_quotes:
            print(f"[HAPAG_API] Successfully retrieved {len(all_quotes)} quotes across {len(iso_types)} container sizes.")
            self.last_error_message = None
            return CarrierResultStatus.AVAILABLE_QUOTES_FOUND, all_quotes

        if last_error:
            self.last_error_message = last_error
        if self.last_error_message:
            print(f"[HAPAG_API] Search completed with status {last_status}: {self.last_error_message}")
        return last_status, []
