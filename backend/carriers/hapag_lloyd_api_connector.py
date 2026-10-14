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
    ChargeCategory,
    DRY_CONTAINER_TYPES,
    REEFER_CONTAINER_TYPES,
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
    # Operating reefers (40' operating reefer is the high-cube 45RT per the Prices API spec)
    "REEFER 20": "22RT",
    "20RF": "22RT",
    "20'RF": "22RT",
    "REEFER 40": "45RT",
    "40RF": "45RT",
    "40RH": "45RT",
    "40'RF": "45RT",
    "40'RH": "45RT",
}

ISO_TO_CONTAINER = {
    "22GP": "DRY 20",
    "42GP": "DRY 40",
    "45GP": "DRY 40H",
    "45HC": "DRY 40H",
    "22RT": "REEFER 20",
    "45RT": "REEFER 40",
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
    supported_container_types = DRY_CONTAINER_TYPES | REEFER_CONTAINER_TYPES

    DEFAULT_BASE_URL = "https://api.hlag.com/hlag/external/v2/quotation-booking-engine/external"
    DEFAULT_SCHEDULES_BASE_URL = "https://api.hlag.com/hlag/external/v1"
    MOCK_BASE_URL = "https://mock.api-portal.hlag.com/v2/quotation-booking-engine/external"
    MOCK_SCHEDULES_BASE_URL = "https://mock.api-portal.hlag.com/v1"

    def __init__(self):
        super().__init__()
        self.port_manager = PortManager()
        self.client_id = os.getenv("HAPAG_API_CLIENT_ID", "").strip()
        self.client_secret = os.getenv("HAPAG_API_CLIENT_SECRET", "").strip()
        self.customer_email = os.getenv("HAPAG_API_CUSTOMER_EMAIL", "sgpricing05@infreight-logistics.com").strip()
        self.base_url = os.getenv("HAPAG_API_BASE_URL", self.DEFAULT_BASE_URL).rstrip("/")
        self.schedules_base_url = os.getenv("HAPAG_API_SCHEDULES_BASE_URL", self.DEFAULT_SCHEDULES_BASE_URL).rstrip("/")
        self.use_mock_api = os.getenv("HAPAG_API_USE_MOCK", "false").lower() in ("true", "1", "yes")

        # job_service calls run_full_search once per container type; all sizes are fetched on the
        # first call and cached here so a 3-size search costs 3 API calls, not 9 (Tryout = 40/day).
        self._route_cache: Dict[tuple, Tuple[CarrierResultStatus, List[QuoteSchema]]] = {}
        # Human-readable reason for a failed search, surfaced by job_service as the carrier error.
        self.last_error_message: Optional[str] = None
        # Error reason codes (overarching / offer / equipment) seen in the current response, for logging
        self._response_reasons: List[str] = []

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
        return self._lookup_freetime(destination_locode, destination_name, container_type)[0]

    def _lookup_freetime(self, destination_locode: str, destination_name: str, container_type: str) -> Tuple[int, bool]:
        """(days, estimated): estimated when the destination has no entry in the free
        time table and no set figure, so the 4-day default is a guess."""
        if not self.freetime_config:
            return 4, True

        from services.hapag_freetime import freetime_days, match_freetime_entry
        from services.port_manager import COUNTRY_CODE_TO_NAME

        # The country from the LOCODE (e.g. JOAQJ -> Jordan) plus whatever was typed
        # ("Apapa, Nigeria [NGAPP]"), matched as whole words.
        port_obj = self.port_manager.get_port_by_code(destination_locode) if destination_locode else None
        country = COUNTRY_CODE_TO_NAME.get((port_obj or {}).get("country", ""), "") if port_obj else ""
        hit = match_freetime_entry(self.freetime_config, f"{country} {destination_name or ''}")
        if hit:
            days = freetime_days(hit[1], container_type)
            if days is not None:
                return days, False

        # Common destination fallbacks
        locode = destination_locode or ""
        if locode.startswith("DE"):  # Germany
            return 4, False
        if locode.startswith("US") or locode.startswith("CA"):
            return 4, False
        if locode.startswith("SG"):  # Singapore
            return 5, False

        return 4, True

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

    async def fetch_commercial_schedules(
        self,
        client: httpx.AsyncClient,
        origin_locode: str,
        destination_locode: str,
        departure_date: str,
    ) -> List[Dict[str, Any]]:
        """
        Queries Hapag-Lloyd DCSA Commercial Schedules API (v1.0.2) to retrieve point-to-point routes,
        physical vessel rotations, cut-off deadlines (STA, DCO, FCO, VCO), and feeder connections.
        """
        endpoint = f"{self.schedules_base_url}/point-to-point-routes"
        if self.use_mock_api:
            endpoint = f"{self.MOCK_SCHEDULES_BASE_URL}/point-to-point-routes"

        headers = {
            "Accept": "application/json",
        }
        if self.client_id:
            headers["X-IBM-Client-Id"] = self.client_id
        if self.client_secret:
            headers["X-IBM-Client-Secret"] = self.client_secret

        params = {
            "placeOfReceipt": origin_locode,
            "placeOfDelivery": destination_locode,
            "departureStartDate": departure_date,
            "receiptTypeAtOrigin": "CY",
            "deliveryTypeAtDestination": "CY",
        }

        await _HAPAG_RATE_LIMITER.acquire()

        try:
            start_t = time.perf_counter()
            response = await client.get(endpoint, params=params, headers=headers, timeout=25.0)
            elapsed_ms = (time.perf_counter() - start_t) * 1000
            print(f"[HAPAG_API] GET /point-to-point-routes returned HTTP {response.status_code} ({elapsed_ms:.1f}ms)")

            if response.status_code != 200:
                print(f"[HAPAG_API] DCSA Schedules returned HTTP {response.status_code}: {response.text[:200]}")
                return []

            raw_solutions = response.json()
            if not isinstance(raw_solutions, list):
                return []

            solutions: List[Dict[str, Any]] = []
            for sol in raw_solutions:
                rec = sol.get("placeOfReceipt", {})
                deliv = sol.get("placeOfDelivery", {})
                cutoffs = {}
                for co in sol.get("cutOffTimes", []):
                    code = co.get("cutOffDateTimeCode")
                    dt_val = co.get("cutOffDateTime")
                    if code and dt_val:
                        cutoffs[code] = dt_val

                legs_parsed = []
                for leg in sol.get("legs", []):
                    dep = leg.get("departure", {})
                    arr = leg.get("arrival", {})
                    transport = leg.get("transport", {})
                    vessel_obj = transport.get("vessel", {})
                    partners = transport.get("servicePartners", [{}])
                    partner = partners[0] if partners else {}
                    legs_parsed.append({
                        "sequence": leg.get("sequenceNumber", 1),
                        "vessel_name": vessel_obj.get("name") or transport.get("vesselName"),
                        "vessel_imo": vessel_obj.get("vesselIMONumber"),
                        "voyage": partner.get("carrierExportVoyageNumber") or partner.get("carrierImportVoyageNumber") or transport.get("carrierVoyageNumber"),
                        "service_name": partner.get("carrierServiceName") or transport.get("carrierServiceName"),
                        "service_code": partner.get("carrierServiceCode") or transport.get("carrierServiceCode"),
                        "departure_locode": (dep.get("location", {}).get("UNLocationCode") or "").upper(),
                        "departure_terminal": dep.get("location", {}).get("facility", {}).get("facilityCode"),
                        "departure_dt": dep.get("dateTime"),
                        "arrival_locode": (arr.get("location", {}).get("UNLocationCode") or "").upper(),
                        "arrival_terminal": arr.get("location", {}).get("facility", {}).get("facilityCode"),
                        "arrival_dt": arr.get("dateTime"),
                    })

                solutions.append({
                    "transit_time": sol.get("transitTime"),
                    "receipt_dt": rec.get("dateTime"),
                    "receipt_locode": (rec.get("location", {}).get("UNLocationCode") or "").upper(),
                    "delivery_dt": deliv.get("dateTime"),
                    "delivery_locode": (deliv.get("location", {}).get("UNLocationCode") or "").upper(),
                    "cutoffs": cutoffs,
                    "legs": legs_parsed,
                })

            return solutions

        except Exception as e:
            print(f"[HAPAG_API] Error querying DCSA Commercial Schedules: {e}")
            return []

    @staticmethod
    def _match_dcsa_schedule(
        raw_etd_str: Optional[str],
        offer_vessels: List[str],
        dcsa_schedules: List[Dict[str, Any]],
        first_voyage: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Correlates an offer from the Prices API to a physical solution in DCSA Commercial Schedules.
        Matches primarily by departure date window (+/- 48 hours), scored by departure vessel and voyage.
        """
        if not dcsa_schedules or not raw_etd_str:
            return None

        try:
            offer_dt = datetime.fromisoformat(str(raw_etd_str).replace("Z", "+00:00"))
        except Exception:
            return None

        first_vessel = offer_vessels[0].strip().upper() if offer_vessels else ""
        if "HAPAG VESSEL" in first_vessel:
            first_vessel = ""

        candidates: List[Tuple[float, Dict[str, Any]]] = []
        for sol in dcsa_schedules:
            rec_dt_str = sol.get("receipt_dt")
            if not rec_dt_str:
                continue
            try:
                sol_dt = datetime.fromisoformat(str(rec_dt_str).replace("Z", "+00:00"))
                diff_hours = abs((sol_dt - offer_dt).total_seconds()) / 3600.0
                if diff_hours <= 48.0:
                    score = 100.0 - diff_hours
                    legs = sol.get("legs", [])
                    sol_v1 = (legs[0].get("vessel_name") or "").strip().upper() if legs else ""
                    sol_voy1 = (legs[0].get("voyage") or "").strip().upper() if legs else ""

                    if first_vessel and sol_v1:
                        if first_vessel == sol_v1:
                            score += 80.0
                        elif first_vessel in sol_v1 or sol_v1 in first_vessel:
                            score += 50.0
                    if first_voyage and sol_voy1 and first_voyage.strip().upper() == sol_voy1:
                        score += 60.0

                    candidates.append((score, sol))
            except Exception:
                continue

        if candidates:
            candidates.sort(key=lambda x: x[0], reverse=True)
            return candidates[0][1]

        return None

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
            # "included into lump sum" = already inside the SEA amount. Verified Keelung -> Pasir Gudang:
            # API SEA 450/400/400 equals the portal's Ocean Freight, which "includes the following
            # assessorial charges: Carrier Security Fee, Destination Landfreight, Inland Transport Add.
            # Origin" (Marine Fuel Recovery, also included=true there, is not listed separately).
            # Listed for transparency, never added again.
            return False, ChargeCategory.UNCERTAIN_EXCLUDED.value
        proposal = rate.get("locationProposal")
        if proposal == "BASE_PORT_FROM":
            return False, ChargeCategory.ORIGIN_CHARGE_EXCLUDED.value
        if proposal == "BASE_PORT_TO":
            return False, ChargeCategory.DESTINATION_CHARGE_EXCLUDED.value
        if proposal == "PC_CARRIAGE":
            # Inland pre-carriage charge NOT in the lump sum (e.g. Fuel Origin Inland): the portal lists it
            # under Export Surcharges, unticked. Lump-sum ones (Inland Transport Add. Origin) return above.
            return False, ChargeCategory.ORIGIN_CHARGE_EXCLUDED.value
        if proposal == "ON_CARRIAGE":
            return False, ChargeCategory.DESTINATION_CHARGE_EXCLUDED.value
        if proposal == "MAIN_CARRIAGE":
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

    @staticmethod
    def _weight_tier_text(rate: Dict[str, Any]) -> Optional[str]:
        """
        Renders a graduated weight tier (e.g. Heavy Lift: 18-99 TON) in the portal's wording,
        'between 18 and 99 ton container gross weight', which is_weight_surcharge_applicable parses.
        """
        if rate.get("graduatedUnitOfMeasureType") != "WEIGHT" and rate.get("graduatedUnitOfMeasure") != "TON":
            return None
        low, high = rate.get("graduatedLowValue"), rate.get("graduatedHighValue")
        if low is not None and high is not None:
            return f"between {low:g} and {high:g} ton container gross weight"
        if low is not None:
            return f"over {low:g} ton container gross weight"
        if high is not None:
            return f"up to {high:g} ton container gross weight"
        return None

    @staticmethod
    def _vessel_label(leg: Dict[str, Any]) -> str:
        name = leg.get("vesselName") or "Hapag Vessel"
        voyage = leg.get("scheduleVoyageNumber")
        return f"{name} (Voy: {voyage})" if voyage else f"{name} /Performa"

    @staticmethod
    def _leg_duration_hours(leg: Dict[str, Any]) -> float:
        try:
            dep = datetime.fromisoformat(str(leg.get("departureDateTime")).replace("Z", "+00:00"))
            arr = datetime.fromisoformat(str(leg.get("arrivalDateTime")).replace("Z", "+00:00"))
            return (arr - dep).total_seconds() / 3600
        except (TypeError, ValueError):
            return 0.0

    def _port_display_name(self, locode: str) -> str:
        port_obj = self.port_manager.get_port_by_code(locode)
        return port_obj.get("name") if port_obj and port_obj.get("name") else locode

    def _record_error_reason(self, reason: Optional[str]) -> None:
        if reason:
            explanation = ERROR_REASON_EXPLANATIONS.get(reason, reason)
            self.last_error_message = f"Hapag-Lloyd API: {explanation} ({reason})"
            self._response_reasons.append(reason)

    def _parse_offer_response_to_quotes(
        self,
        api_data: Dict[str, Any],
        requested_container_type: str,
        destination_locode: str,
        destination_name: str,
        weight_kg: Optional[float] = None,
        dcsa_schedules: Optional[List[Dict[str, Any]]] = None,
    ) -> List[QuoteSchema]:
        """
        Parses Hapag-Lloyd OfferResponse JSON into InFreight QuoteSchema objects,
        cross-referencing with DCSA Commercial Schedules for cutoff and spot space validation.
        """
        quotes: List[QuoteSchema] = []
        offers = api_data.get("offers", [])

        if not offers:
            self._record_error_reason(api_data.get("overarchingErrorReason"))
            return quotes

        free_time_days, free_time_estimated = self._lookup_freetime(destination_locode, destination_name, requested_container_type)

        # Index offers by departure date to correlate Spot vs Quick Quotes availability
        sailing_spot_meta: Dict[str, Dict[str, Any]] = {}
        for off in offers:
            raw_dep = off.get("placeOfReceiptDate") or off.get("portOfLoadingDateTime") or ""
            dep_key = str(raw_dep)[:10]
            if not dep_key:
                continue
            prod = off.get("productIdentifier", "")
            if prod == "QUICK_QUOTES_SPOT":
                has_rates = any(bool(eq.get("rates")) for eq in off.get("equipments", []))
                spot_errs = [eq.get("errorReason") for eq in off.get("equipments", []) if eq.get("errorReason")]
                if off.get("errorReason"):
                    spot_errs.append(off.get("errorReason"))
                sailing_spot_meta[dep_key] = {
                    "has_spot_rates": has_rates,
                    "spot_errors": spot_errs,
                }

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
            # Main (mother) vessel = the longest ocean leg; feeders on either side are short hops
            main_ocean = max(ocean_legs, key=self._leg_duration_hours) if ocean_legs else {}

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

            # Cross-reference with DCSA Commercial Schedules
            matched_schedule: Optional[Dict[str, Any]] = None
            if dcsa_schedules:
                offer_vessels = [l.get("vesselName", "") for l in ocean_legs if l.get("vesselName")]
                first_voy = ocean_legs[0].get("scheduleVoyageNumber") if ocean_legs else None
                matched_schedule = self._match_dcsa_schedule(raw_etd, offer_vessels, dcsa_schedules, first_voy)

            # Evaluate cutoffs & schedule viability
            cutoff_warning: Optional[str] = None
            active_cutoffs: List[str] = []
            is_cutoff_expired = False

            if matched_schedule:
                # Enrich transit time if missing
                if not transit_time and matched_schedule.get("transit_time"):
                    transit_time = matched_schedule.get("transit_time")

                # Enrich transshipment ports if offer had missing feeder legs
                if not transshipment_ports and len(matched_schedule.get("legs", [])) > 1:
                    for d_leg in matched_schedule["legs"][:-1]:
                        arr_loc = d_leg.get("arrival_locode")
                        term = d_leg.get("arrival_terminal")
                        p_name = self._port_display_name(arr_loc) if arr_loc else ""
                        if term:
                            p_name = f"{p_name} ({term})"
                        if p_name and p_name not in transshipment_ports:
                            transshipment_ports.append(p_name)

                # Check cutoffs
                now_utc = datetime.now(timezone.utc)
                cutoffs = matched_schedule.get("cutoffs", {})
                expired_codes = []
                for code, dt_str in cutoffs.items():
                    try:
                        c_dt = datetime.fromisoformat(str(dt_str).replace("Z", "+00:00"))
                        if c_dt < now_utc:
                            if code in ("DCO", "STA", "FCO"):
                                expired_codes.append(f"{code} ({c_dt.strftime('%d %b %H:%M')})")
                        else:
                            if code in ("DCO", "STA"):
                                active_cutoffs.append(f"{code} {c_dt.strftime('%d %b')}")
                    except Exception:
                        pass

                if expired_codes:
                    is_cutoff_expired = True
                    cutoff_warning = f"Booking cutoff expired [{', '.join(expired_codes)}]. Sailing closed on carrier website."

            # Format Vessel String. Many offers share the same origin feeder but connect to different
            # mother vessels / transshipment ports, so name the main vessel and the via-ports too;
            # otherwise those rows look identical in the results table and Excel Remark column.
            vessel_display = self._vessel_label(main_ocean)
            if transshipment_ports:
                vessel_display = f"{vessel_display} | via {', '.join(transshipment_ports)}"
            if first_ocean and first_ocean is not main_ocean:
                vessel_display = f"{vessel_display} | feeder {self._vessel_label(first_ocean)}"

            # Booking availability warning & tag determination
            booking_warning: Optional[str] = None
            dep_key = str(raw_etd)[:10]
            spot_meta = sailing_spot_meta.get(dep_key, {})
            spot_errs = spot_meta.get("spot_errors", [])

            if is_cutoff_expired:
                booking_warning = cutoff_warning
                vessel_display = f"{vessel_display} [BOOKING CLOSED - CUTOFF EXPIRED]"
            elif is_spot:
                vessel_display = f"{vessel_display} (SPOT) [SPOT GUARANTEED]"
                if active_cutoffs:
                    booking_warning = f"Spot space guaranteed. Cut-off: {', '.join(active_cutoffs)}"
            else:
                # product_id == "QUICK_QUOTES"
                if "CAPACITY" in spot_errs:
                    booking_warning = "Tariff quote (QQ). Online Spot booking unavailable (Vessel at CAPACITY on carrier portal). Space subject to manual confirmation."
                    vessel_display = f"{vessel_display} [TARIFF ONLY - SPOT FULL]"
                elif "CAN_NOT_BE_OFFERED" in spot_errs:
                    # Spot product is not offered on this specific routing, but Quick Quotes IS actively bookable online
                    vessel_display = f"{vessel_display} (QQ Tariff)"
                    booking_warning = "Standard Quick Quotes rate (Spot rate not offered on this routing)."
                    if active_cutoffs:
                        booking_warning = f"{booking_warning} Cut-off: {', '.join(active_cutoffs)}"
                elif "RESTRICTIONS" in spot_errs:
                    # Spot rate restricted on carrier portal, but Quick Quotes remains bookable
                    vessel_display = f"{vessel_display} (QQ Tariff)"
                    booking_warning = "Standard Quick Quotes rate (Spot rate restricted on carrier portal)."
                    if active_cutoffs:
                        booking_warning = f"{booking_warning} Cut-off: {', '.join(active_cutoffs)}"
                elif dcsa_schedules is not None and len(dcsa_schedules) == 0:
                    booking_warning = "No active commercial sailing found in Hapag-Lloyd schedule engine for this corridor. Offline enquiry required."
                    vessel_display = f"{vessel_display} [NO ONLINE SCHEDULE]"
                elif dcsa_schedules and not matched_schedule:
                    booking_warning = "Tariff quote. Departure date not verified against active carrier schedules."
                    vessel_display = f"{vessel_display} [UNVERIFIED SCHEDULE]"
                else:
                    vessel_display = f"{vessel_display} (QQ Tariff)"
                    if active_cutoffs:
                        booking_warning = f"Schedule active. Booking cut-off: {', '.join(active_cutoffs)}"

            # Process Equipments & Rates
            equipments = offer.get("equipments", [])
            for equip in equipments:
                if equip.get("errorReason") and not equip.get("rates"):
                    self._record_error_reason(equip.get("errorReason"))
                    continue

                size_type = equip.get("requestedEquipment", {}).get("requestedEquipmentSizeType", "45GP")
                container_type = ISO_TO_CONTAINER.get(size_type)
                if not container_type:
                    # Never relabel an unknown size (e.g. a special box) as the requested type
                    print(f"[HAPAG_API] Ignoring equipment of unsupported size {size_type}")
                    continue

                raw_charges = []
                for r in equip.get("rates", []):
                    print(
                        f"[HAPAG_API]   rate {product_id} {size_type} {r.get('chargeTypeCode')} "
                        f"'{r.get('chargeTypeShortDescription')}' {r.get('amount')} {r.get('currency')} "
                        f"uom={r.get('unitOfMeasure')} sea={r.get('seaFreightIndicator')} included={r.get('included')} "
                        f"chargeable={r.get('chargeable')} loc={r.get('locationProposal')} "
                        f"graduated={r.get('graduatedLowValue')}-{r.get('graduatedHighValue')} "
                        f"{r.get('graduatedUnitOfMeasure')}/{r.get('graduatedUnitOfMeasureType')}"
                    )
                    skip, category = self._classify_rate(r)
                    if skip:
                        continue
                    desc = r.get("chargeTypeShortDescription") or r.get("chargeTypeCode") or "Charge"
                    weight_tier = self._weight_tier_text(r)
                    if weight_tier:
                        # The shared classifier only reads weight tiers from the charge name (as the portal
                        # prints them); without this a Heavy Lift tier is counted for any cargo weight.
                        desc = f"{desc} ({weight_tier})"
                    if r.get("included") and not r.get("seaFreightIndicator"):
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
                warning_message = booking_warning
                if other_currency:
                    curr_note = "Not in total (different currency): " + ", ".join(
                        f"{c['name']} {c['amount']:g} {c['currency']}" for c in other_currency
                    )
                    warning_message = f"{warning_message} | {curr_note}" if warning_message else curr_note

                # Check Value Added Services for Free Time Override
                vas_list = equip.get("valueAddedServices", [])
                for vas in vas_list:
                    if "ADFT" in vas.get("vasCode", "") or "Free" in vas.get("name", ""):
                        ft_days = vas.get("freetimeDays")
                        if ft_days and ft_days > 0:
                            free_time_days = ft_days
                            free_time_estimated = False

                quote = QuoteSchema(
                    etd=etd,
                    eta=eta,
                    transit_time_days=transit_time,
                    service_name=service_name,
                    vessel=vessel_display,
                    routing=", ".join(transshipment_ports) if transshipment_ports else "Direct",
                    port_of_discharge=port_of_discharge,
                    # "(est.)" marks the default for destinations missing from the free time table.
                    free_time=(f"{free_time_days} days" + (" (est.)" if free_time_estimated else "")) if free_time_days else None,
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
        unknown_types = []
        for c in req_types:
            iso = CONTAINER_TO_ISO.get(c.upper().strip())
            if not iso:
                # Never fall back to another size: a reefer priced as a 40'HC would look like a valid quote
                unknown_types.append(c)
                continue
            if iso not in iso_types:
                iso_types.append(iso)
        if unknown_types:
            print(f"[HAPAG_API] Skipping unsupported container type(s): {unknown_types}")
        if not iso_types:
            self.last_error_message = f"Hapag-Lloyd API: unsupported container type(s) {', '.join(unknown_types)}"
            return CarrierResultStatus.INVALID_SEARCH_INPUT, []

        last_status = CarrierResultStatus.NO_QUOTES_AVAILABLE
        last_error = None
        requested_names = [ISO_TO_CONTAINER[iso] for iso in iso_types]
        # Hapag answers a 22GP request with 22GP, 42GP and 45GP for every sailing, so one response can
        # cover several requested sizes. Keep the first response's quotes per size (no duplicates) and
        # skip calls for sizes already returned (saves Tryout quota).
        collected: Dict[str, List[QuoteSchema]] = {}
        missing_notes: List[str] = []

        async with httpx.AsyncClient(timeout=30.0) as client:
            # Query DCSA Commercial Schedules to verify physical vessel rotations and booking cutoffs
            dcsa_schedules: List[Dict[str, Any]] = []
            try:
                dcsa_schedules = await self.fetch_commercial_schedules(
                    client=client,
                    origin_locode=origin_locode,
                    destination_locode=destination_locode,
                    departure_date=departure_date,
                )
                print(f"[HAPAG_API] Retrieved {len(dcsa_schedules)} DCSA commercial schedule solution(s) for {origin_locode} -> {destination_locode}")
            except Exception as ex:
                print(f"[HAPAG_API] Warning: Failed to retrieve DCSA commercial schedules: {ex}")

            for iso in iso_types:
                mapped_container_name = ISO_TO_CONTAINER[iso]
                if mapped_container_name in collected:
                    print(f"[HAPAG_API] {iso} already returned by an earlier response - skipping its API call.")
                    continue
                self._response_reasons = []
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
                        dcsa_schedules=dcsa_schedules,
                    )
                    by_type: Dict[str, List[QuoteSchema]] = {}
                    for q in parsed:
                        by_type.setdefault(q.container_type, []).append(q)
                    reasons = list(dict.fromkeys(self._response_reasons))
                    print(
                        f"[HAPAG_API] Requested {iso}: {len(data.get('offers') or [])} offer(s), "
                        f"returned sizes {sorted(by_type)}, error reasons {reasons or 'none'}"
                    )
                    for ct, qs in by_type.items():
                        if ct in requested_names and ct not in collected:
                            collected[ct] = qs
                    if mapped_container_name not in by_type:
                        missing_notes.append(
                            f"no {mapped_container_name} offers returned" + (f" ({', '.join(reasons)})" if reasons else "")
                        )
                else:
                    if err:
                        last_error = err
                        missing_notes.append(f"{mapped_container_name}: {err}")
                    if status != CarrierResultStatus.NO_QUOTES_AVAILABLE and last_status != CarrierResultStatus.AVAILABLE_QUOTES_FOUND:
                        last_status = status

        all_quotes = [q for name in requested_names for q in collected.get(name, [])]
        if missing_notes:
            print(f"[HAPAG_API] Missing sizes: {'; '.join(missing_notes)}")

        if all_quotes:
            print(f"[HAPAG_API] Successfully retrieved {len(all_quotes)} quotes for {sorted(collected)}.")
            self.last_error_message = None
            return CarrierResultStatus.AVAILABLE_QUOTES_FOUND, all_quotes

        if missing_notes and not last_error:
            self.last_error_message = "Hapag-Lloyd API: " + "; ".join(missing_notes)

        if last_error:
            self.last_error_message = last_error
        if self.last_error_message:
            print(f"[HAPAG_API] Search completed with status {last_status}: {self.last_error_message}")
        return last_status, []
