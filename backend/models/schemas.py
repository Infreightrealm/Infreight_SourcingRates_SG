"""
Pydantic schemas for API request/response validation.
"""
from __future__ import annotations
from typing import Optional
from datetime import date
from pydantic import BaseModel, Field, model_validator
from enum import Enum


# ────────────────────────────────────────────
# Enums
# ────────────────────────────────────────────

class CarrierCode(str, Enum):
    MAERSK = "MAERSK"
    ONE = "ONE"
    CMA_CGM = "CMA_CGM"
    HAPAG_LLOYD = "HAPAG_LLOYD"
    MSC = "MSC"
    OOCL = "OOCL"
    GREENX = "GREENX"


ALL_CARRIERS = [c.value for c in CarrierCode]


class SearchStatus(str, Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    PARTIAL_COMPLETED = "PARTIAL_COMPLETED"
    FAILED = "FAILED"


class CarrierResultStatus(str, Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    AVAILABLE_QUOTES_FOUND = "AVAILABLE_QUOTES_FOUND"
    NO_QUOTES_AVAILABLE = "NO_QUOTES_AVAILABLE"
    LOGIN_FAILED = "LOGIN_FAILED"
    INVALID_SEARCH_INPUT = "INVALID_SEARCH_INPUT"
    CARRIER_SITE_CHANGED = "CARRIER_SITE_CHANGED"
    CAPTCHA_OR_MANUAL_REVIEW_REQUIRED = "CAPTCHA_OR_MANUAL_REVIEW_REQUIRED"
    PRICE_BREAKDOWN_NOT_FOUND = "PRICE_BREAKDOWN_NOT_FOUND"
    EXTRACTION_FAILED = "EXTRACTION_FAILED"
    CONNECTOR_NOT_AVAILABLE = "CONNECTOR_NOT_AVAILABLE"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    TIMEOUT = "TIMEOUT"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
    FAILED = "FAILED"
    
    # AI Self-healing & Manual Intervention statuses
    MANUAL_ACTION_REQUIRED = "MANUAL_ACTION_REQUIRED"
    WAITING_FOR_HUMAN_VERIFICATION = "WAITING_FOR_HUMAN_VERIFICATION"
    HUMAN_VERIFICATION_COMPLETED = "HUMAN_VERIFICATION_COMPLETED"
    LOGIN_SESSION_RESTORED = "LOGIN_SESSION_RESTORED"
    BOT_CHALLENGE_DETECTED = "BOT_CHALLENGE_DETECTED"
    CONNECTOR_REPAIR_REQUIRED = "CONNECTOR_REPAIR_REQUIRED"
    AI_SELECTOR_REPAIR_SUGGESTED = "AI_SELECTOR_REPAIR_SUGGESTED"
    AI_SELECTOR_REPAIR_TESTED = "AI_SELECTOR_REPAIR_TESTED"
    AI_SELECTOR_REPAIR_APPROVED = "AI_SELECTOR_REPAIR_APPROVED"
    AI_SELECTOR_REPAIR_REJECTED = "AI_SELECTOR_REPAIR_REJECTED"


class ChargeCategory(str, Enum):
    BASIC_OCEAN_FREIGHT = "BASIC_OCEAN_FREIGHT"
    DISCOUNT = "DISCOUNT"
    FREIGHT_SURCHARGE_INCLUDED = "FREIGHT_SURCHARGE_INCLUDED"
    ORIGIN_CHARGE_EXCLUDED = "ORIGIN_CHARGE_EXCLUDED"
    DESTINATION_CHARGE_EXCLUDED = "DESTINATION_CHARGE_EXCLUDED"
    UNCERTAIN_EXCLUDED = "UNCERTAIN_EXCLUDED"


# ────────────────────────────────────────────
# Request schemas
# ────────────────────────────────────────────

class RateSearchRequest(BaseModel):
    carriers: list[str] = Field(..., description="List of carrier codes or ['ALL']")
    origin: str = Field(default="Singapore", description="Origin port/location")
    destination: str = Field(default="Hamburg, Germany", description="Destination port/location")
    service_term: str = Field(default="CY/CY")
    container_type: str = Field(default="DRY 40H", description="e.g. DRY 20, DRY 40, DRY 40H")
    container_types: list[str] = Field(default=["DRY 40H"], description="List of container types to search")
    container_quantity: int = Field(default=1, ge=1)
    weight_per_container_kg: float = Field(default=20000, gt=0)
    commodity: str = Field(default="Furniture")
    departure_date: str = Field(default="tomorrow", description="ISO date or 'tomorrow'")
    search_window_days: int = Field(default=14, ge=1, le=28)
    user_name: Optional[str] = Field(default=None, description="The name of the user making the request")
    use_mock: Optional[bool] = Field(default=None, description="Override mock/live mode for this search. None = use server default.")
    hapag_region: Optional[str] = Field(default="ROW", description="Hapag-Lloyd account region: 'US_CA', 'EU', or 'ROW'")

    @model_validator(mode="before")
    @classmethod
    def populate_container_types(cls, data):
        if isinstance(data, dict):
            # Clamp search window to 28 days (4 weeks) max
            sw_days = data.get("search_window_days")
            if sw_days is not None:
                try:
                    data["search_window_days"] = min(int(sw_days), 28)
                except:
                    pass

            c_types = data.get("container_types")
            c_type = data.get("container_type")
            if c_types is not None:
                if isinstance(c_types, str):
                    data["container_types"] = [c.strip() for c in c_types.split(",") if c.strip()]
                elif isinstance(c_types, list):
                    data["container_types"] = [c for c in c_types if c]
                if not data.get("container_type") and data["container_types"]:
                    data["container_type"] = data["container_types"][0]
            elif c_type is not None:
                data["container_types"] = [c_type]
            else:
                data["container_types"] = ["DRY 40H"]
                data["container_type"] = "DRY 40H"
        return data


class RFQParseRequest(BaseModel):
    text: Optional[str] = Field(default="", description="Raw RFQ text from email or message")
    image_b64: Optional[str] = Field(default=None, description="Base64 encoded string of uploaded RFQ screenshot image")
    image_mime: Optional[str] = Field(default=None, description="MIME type of uploaded image (e.g. image/png, image/jpeg)")



class RFQParseResult(BaseModel):
    status: str = Field(..., description="'success', 'air_draft_generated', 'needs_clarification', or 'unsupported_cargo'")
    mode: str = Field(default="sea", description="'air' or 'sea'")
    confidence: float = Field(default=1.0, description="Classification confidence score 0.0-1.0")
    matched_keywords: list[str] = Field(default_factory=list, description="Matched keyword signals")
    is_dangerous_goods: bool = Field(default=False, description="True if dangerous goods / compliance detected")
    compliance_notes: Optional[str] = Field(default=None, description="Preserved compliance notes e.g. Lithium Metal Batteries PI 970 Section II")
    hs_code: Optional[str] = Field(default=None, description="HS Code if mentioned in text")
    is_unsupported_equipment: bool = Field(default=False, description="True if special equipment like Reefer, Open Top, Flat Rack, ISO Tank, Hard Top is detected")
    unsupported_equipment_type: Optional[str] = Field(default=None, description="Type of unsupported equipment detected")
    is_lcl: bool = Field(default=False, description="True if LCL / Less than Container Load is detected")
    is_dual_mode: bool = Field(default=False, description="True if email contains both Air freight and Ocean freight requests")
    is_booking_confirmation: bool = Field(default=False, description="True if email is a booking confirmation/instruction rather than a rate request")
    unsupported_reason: Optional[str] = Field(default=None, description="Explanation message if shipment uses unsupported equipment or LCL mode")


    origin_display: Optional[str] = Field(default=None, description="Resolved origin string e.g. Port Klang (from 'PK')")
    destination_display: Optional[str] = Field(default=None, description="Resolved destination string e.g. Jakarta (from 'JKT')")
    sales_notes: Optional[dict] = Field(default=None, description="Extracted commercial signals (future_volume, competitive_pressure, urgency, target_rate)")
    air_drafts: Optional[list[dict]] = Field(default=None, description="Dual draft emails for AWOT (Glenn) and ASPAC (Jing Hui)")
    parsed_fields: Optional[RateSearchRequest] = Field(default=None, description="Primary RateSearchRequest if successful")
    all_parsed_pairs: Optional[list[dict]] = Field(default=None, description="All parsed POL-POD pairs for multi-pair RFQs")
    total_pairs_found: int = Field(default=1, description="Total expanded POL-POD pairs found")
    pairs_omitted_count: int = Field(default=0, description="Number of pairs omitted due to search cap")
    clarification_question: Optional[str] = Field(default=None, description="Question or warning for user if required fields are missing, ambiguous, or unsupported")
    missing_fields: list[str] = Field(default_factory=list, description="List of missing required fields")
    extracted_fields: list[str] = Field(default_factory=list, description="Fields explicitly extracted from raw text")
    default_injected_fields: list[str] = Field(default_factory=list, description="Fields populated from system defaults")
    debug_raw_llm_response: Optional[str] = Field(default=None, description="Raw response returned by Gemini LLM")






# ────────────────────────────────────────────
# Response schemas

# ────────────────────────────────────────────

class ChargeSchema(BaseModel):
    name: str
    amount: float
    currency: str = "USD"
    category: Optional[str] = None
    reason: Optional[str] = None


class QuoteSchema(BaseModel):
    etd: Optional[str] = None
    eta: Optional[str] = None
    transit_time_days: Optional[int] = None
    service_name: Optional[str] = None
    vessel: Optional[str] = None
    routing: Optional[str] = "Direct"
    free_time: Optional[int] = None
    container_type: Optional[str] = None
    container_quantity: Optional[int] = None
    currency: str = "USD"
    basic_ocean_freight: float = 0.0
    discount: float = 0.0
    included_freight_surcharges: list[ChargeSchema] = []
    excluded_charges: list[ChargeSchema] = []
    uncertain_charges: list[ChargeSchema] = []
    final_freight_value: float = 0.0
    source: str = "carrier_portal"
    raw_reference: Optional[str] = None
    validity_till: Optional[str] = None



class CarrierResultSchema(BaseModel):
    carrier: str
    status: str
    error_message: Optional[str] = None
    quotes: list[QuoteSchema] = []


class RateSearchCreateResponse(BaseModel):
    search_id: str
    status: str = "QUEUED"


class RateSearchResultResponse(BaseModel):
    search_id: str
    status: str
    origin: Optional[str] = None
    destination: Optional[str] = None
    container_type: Optional[str] = None
    container_types: Optional[list[str]] = None
    container_quantity: Optional[int] = None
    commodity: Optional[str] = None
    created_at: Optional[str] = None
    queue_position: Optional[int] = None
    active_search_info: Optional[str] = None
    results: list[CarrierResultSchema] = []
