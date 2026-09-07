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
from services.normalizer import standardize_date_string


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
        commodity_group: str = "FAK"
    ) -> Dict[str, Any]:
        """Constructs OpenAPI compliant OfferRequest payload."""
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
            "commodity": {
                "commodityTypeGroup": commodity_group,
                "cargoGrossWeight": int(weight_kg) if weight_kg > 0 else 20000,
                "cargoGrossWeightUnit": "KG",
                "isHazardous": False
            },
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

    def _parse_offer_response_to_quotes(
        self,
        api_data: Dict[str, Any],
        requested_container_type: str,
        destination_locode: str,
        destination_name: str
    ) -> List[QuoteSchema]:
        """
        Parses Hapag-Lloyd OfferResponse JSON into InFreight QuoteSchema objects.
        """
        quotes: List[QuoteSchema] = []
        offers = api_data.get("offers", [])

        if not offers:
            return quotes

        free_time_days = self._get_freetime_days(destination_locode, destination_name, requested_container_type)

        for offer in offers:
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

            # Parse Legs (Ocean & Intermodal)
            legs = offer.get("legs", [])
            vessel_name = "Hapag Vessel"
            voyage_no = ""
            service_name = "Hapag Service"
            transshipment_ports = []

            for leg in legs:
                # Ocean leg info
                v_name = leg.get("vesselName")
                v_voy = leg.get("scheduleVoyageNumber")
                s_name = leg.get("carrierServiceName")
                arr_loc = leg.get("arrivalLocation")

                if v_name:
                    vessel_name = v_name
                if v_voy:
                    voyage_no = v_voy
                if s_name:
                    service_name = f"Hapag {s_name} Service"

                # Check for transshipment ports
                if arr_loc and arr_loc != destination_locode:
                    port_obj = self.port_manager.get_port_by_code(arr_loc)
                    p_name = port_obj.get("name") if port_obj else arr_loc
                    transshipment_ports.append(p_name)

            # Build Routing String
            if transshipment_ports:
                routing_str = f"via {transshipment_ports[0]}"
                display_service = f"{service_name} ({routing_str})"
            else:
                routing_str = "Direct"
                display_service = service_name

            # Format Vessel String
            vessel_display = f"{vessel_name} /Performa" if not voyage_no else f"{vessel_name} (Voy: {voyage_no})"
            if is_spot:
                vessel_display = f"{vessel_display} (SPOT)"

            # Process Equipments & Rates
            equipments = offer.get("equipments", [])
            for equip in equipments:
                size_type = equip.get("requestedEquipment", {}).get("requestedEquipmentSizeType", "45GP")
                container_type = ISO_TO_CONTAINER.get(size_type, requested_container_type)

                rates = equip.get("rates", [])
                basic_ocean_freight = 0.0
                included_surcharges: List[ChargeSchema] = []
                excluded_charges: List[ChargeSchema] = []
                currency = "USD"

                for r in rates:
                    code = r.get("chargeTypeCode", "")
                    desc = r.get("chargeTypeShortDescription") or r.get("chargeText") or code
                    amt = float(r.get("amount", 0.0))
                    curr = r.get("currency", "USD")
                    is_sea_freight = r.get("seaFreightIndicator", False) or code in ("BAS", "OFR", "SEA")
                    is_included = r.get("included", False)

                    if is_sea_freight or r.get("chargeTypeClass") == 1:
                        basic_ocean_freight += amt
                        if curr:
                            currency = curr
                    elif is_included or code in ("MFR", "EMA", "BAF", "SEC", "EBS", "CAF"):
                        included_surcharges.append(
                            ChargeSchema(
                                name=desc,
                                amount=round(amt, 2),
                                currency=curr,
                                category=ChargeCategory.FREIGHT_SURCHARGE_INCLUDED.value,
                                reason="Preserved carrier connector classification"
                            )
                        )
                    else:
                        # Local / Destination / Origin charges
                        excluded_charges.append(
                            ChargeSchema(
                                name=desc,
                                amount=round(amt, 2),
                                currency=curr,
                                category=ChargeCategory.DESTINATION_CHARGE_EXCLUDED.value,
                                reason="Excluded local tariff charge"
                            )
                        )

                # Total Surcharges + Freight
                surcharge_total = sum(c.amount for c in included_surcharges)
                final_freight_value = round(basic_ocean_freight + surcharge_total, 2)

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
                    service_name=display_service,
                    vessel=vessel_display,
                    routing=transshipment_ports[0] if transshipment_ports else "Direct",
                    free_time=f"{free_time_days} days" if free_time_days else None,
                    demurrage=0,
                    detention=0,
                    container_type=container_type,
                    container_quantity=1,
                    currency=currency,
                    basic_ocean_freight=round(basic_ocean_freight, 2),
                    discount=0.0,
                    included_freight_surcharges=included_surcharges,
                    excluded_charges=excluded_charges,
                    final_freight_value=final_freight_value,
                    source="carrier_api",
                    raw_reference=offer.get("carrierOfferRequestReference", "HLAG-API"),
                    validity_till=validity_till,
                    is_breakdown_unavailable=False
                )
                quotes.append(quote)

        return quotes

    async def run_full_search(self, request: RateSearchRequest) -> Tuple[CarrierResultStatus, List[QuoteSchema]]:
        """
        Executes full rate search against Hapag-Lloyd Prices API.
        Queries each requested container size (20GP, 40GP, 40HQ) and merges results.
        """
        print(f"[HAPAG_API] Starting API rate search: {request.origin} -> {request.destination}")

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
            return CarrierResultStatus.INVALID_SEARCH_INPUT, []

        departure_date = self._calculate_earliest_departure_date(request.departure_date)

        # Determine container types to query
        req_types = request.container_types or ([request.container_type] if request.container_type else ["DRY 40H"])
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
                        destination_name=request.destination
                    )
                    all_quotes.extend(parsed)
                    last_status = CarrierResultStatus.AVAILABLE_QUOTES_FOUND
                else:
                    if err:
                        last_error = err
                    if status != CarrierResultStatus.NO_QUOTES_AVAILABLE:
                        last_status = status

        if all_quotes:
            print(f"[HAPAG_API] Successfully retrieved {len(all_quotes)} quotes across {len(iso_types)} container sizes.")
            return CarrierResultStatus.AVAILABLE_QUOTES_FOUND, all_quotes

        if last_error:
            print(f"[HAPAG_API] Search completed with status {last_status}: {last_error}")
        return last_status, []
