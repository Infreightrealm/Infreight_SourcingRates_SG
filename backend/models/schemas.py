"""
Pydantic schemas for API request/response validation.
"""
from __future__ import annotations
from typing import Optional
from datetime import date
from pydantic import BaseModel, Field
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
    EVERGREEN = "EVERGREEN"
    COSCO = "COSCO"
    OOCL = "OOCL"
    HMM = "HMM"
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
    container_type: str = Field(default="DRY 40H", description="e.g. DRY 20, DRY 40, DRY 40H, REEFER 20, REEFER 40, REEFER 40H")
    container_quantity: int = Field(default=1, ge=1)
    weight_per_container_kg: float = Field(default=20000, gt=0)
    commodity: str = Field(default="Furniture")
    departure_date: str = Field(default="tomorrow", description="ISO date or 'tomorrow'")
    search_window_days: int = Field(default=14, ge=1, le=90)
    user_name: Optional[str] = Field(default=None, description="The name of the user making the request")
    use_mock: Optional[bool] = Field(default=None, description="Override mock/live mode for this search. None = use server default.")


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
    container_quantity: Optional[int] = None
    commodity: Optional[str] = None
    created_at: Optional[str] = None
    queue_position: Optional[int] = None
    active_search_info: Optional[str] = None
    results: list[CarrierResultSchema] = []
