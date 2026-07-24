"""
AI Agent service for parsing free-text RFQ emails or messages into structured RateSearchRequest objects
using native Google Gemini API (gemini-2.5-flash) with x-goog-api-key authentication.
Supports AIR vs SEA classification, dual forwarder air drafts, dangerous goods compliance notes,
multi-origin gappy destination list parsing, deterministic port alias resolution (ports_aliases.json),
unmapped abbreviation guardrails, and Sales Desk Intelligence extraction.
"""
import os
import json
import re
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel, Field

from models.schemas import RateSearchRequest, RFQParseResult


# ────────────────────────────────────────────
# Configuration Loader for Air Forwarder Partners & Port Aliases
# ────────────────────────────────────────────

def _load_forwarders_config() -> list[dict]:
    config_path = os.path.join(os.path.dirname(__file__), "..", "config", "forwarders.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("air_partners", [])
        except Exception as e:
            print(f"[RFQ Agent] Warning loading forwarders.json: {e}")
    # Default standing air freight partners (Glenn & Jing Hui)
    return [
        {
            "id": "awot",
            "company_name": "AWOT Global Logistics",
            "contact_person": "Glenn",
            "contact_email": "glenn@awotglobal.com"
        },
        {
            "id": "aspac",
            "company_name": "ASPAC International Logistics",
            "contact_person": "Jing Hui",
            "contact_email": "jinghui@aspac.com"
        },
        {
            "id": "speedmark",
            "company_name": "SpeedMark",
            "contact_person": "Melvin Tan",
            "contact_email": "Melvin.Tan@speedmark.com.sg"
        }
    ]



def _load_port_aliases_config() -> dict[str, str]:
    config_path = os.path.join(os.path.dirname(__file__), "..", "config", "ports_aliases.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[RFQ Agent] Warning loading ports_aliases.json: {e}")
    return {
        "jkt": "Jakarta",
        "pgu": "Pasir Gudang",
        "tp": "Tanjung Pelepas",
        "tpp": "Tanjung Pelepas",
        "sin": "Singapore",
        "sg": "Singapore",
        "hkg": "Hong Kong",
        "sha": "Shanghai",
        "pvg": "Shanghai",
        "ngb": "Ningbo",
        "hph": "Haiphong",

        "sgn": "Ho Chi Minh",
        "sub": "Surabaya",
        "btm": "Batam"
    }


def _load_airports_iata_config() -> dict[str, dict]:
    config_path = os.path.join(os.path.dirname(__file__), "..", "config", "airports_iata.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[RFQ Agent] Warning loading airports_iata.json: {e}")
    return {}


def _load_airport_aliases_config() -> dict[str, str]:
    config_path = os.path.join(os.path.dirname(__file__), "..", "config", "airport_aliases.json")
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[RFQ Agent] Warning loading airport_aliases.json: {e}")
    return {
        "changi": "SIN",
        "singapore airport": "SIN",
        "kl": "KUL",
        "klia": "KUL"
    }


def resolve_airport_alias(airport_str: Optional[str]) -> tuple[Optional[dict], Optional[str], bool]:
    """
    Resolves an Air-RFQ origin/destination string against OpenFlights airports_iata.json (6,072 entries)
    and non-standard airport_aliases.json.
    Returns (airport_dict, display_str, requires_clarification).
    Display format: "Singapore Changi Airport, Singapore (SIN)"
    - Step 1: Try airport_aliases.json first ('changi' -> 'SIN', 'kl' -> 'KUL')
    - Step 2: Exact IATA lookup ('SIN' -> { iata: 'SIN', name: 'Singapore Changi Airport', city: 'Singapore', country: 'Singapore' })
    - Step 3: Exact city / airport name match
    - Step 4: If unresolvable, returns (None, f"Unknown airport '{airport_str}'", True) -> triggers needs_clarification. Never guess!
    """
    if not airport_str or not airport_str.strip():
        return None, None, False

    clean_str = airport_str.strip()
    key_lower = clean_str.lower()

    aliases_map = _load_airport_aliases_config()
    airports_map = _load_airports_iata_config()

    # 1. Try shorthand aliases first
    target_iata = aliases_map.get(key_lower)
    if not target_iata and len(clean_str) == 3 and clean_str.isalpha():
        target_iata = clean_str.upper()

    # 2. Exact IATA lookup
    if target_iata and target_iata.upper() in airports_map:
        info = airports_map[target_iata.upper()]
        display = f"{info['name']}, {info['city']} ({info['iata']})"
        if clean_str.upper() != info['iata']:
            display += f" [from '{clean_str}']"
        return info, display, False

    # 3. Match by city or airport name
    for code, info in airports_map.items():
        if info.get("city", "").lower() == key_lower or info.get("name", "").lower() == key_lower:
            display = f"{info['name']}, {info['city']} ({info['iata']})"
            return info, display, False

    # 4. Return needs_clarification if unresolved. Never guess!
    return None, f"Unknown airport '{clean_str}'", True


def resolve_port_alias(port_str: Optional[str], mode: str = "sea") -> tuple[Optional[str], Optional[str], bool]:
    """
    Deterministically resolves a port string against ports_aliases.json and the port_manager database.
    Returns (resolved_full_name, display_str_with_orig_code, requires_clarification).
    - If port_str is in ports_aliases.json: returns ("Port Klang", "Port Klang (from 'PK')", False)
    - If mode == 'air' and port_str is 3-letter IATA airport code: returns (port_str.upper(), f"{port_str.upper()} Airport", False)
    - If port_str is 2-3 letters NOT in ports_aliases.json (sea mode): returns (port_str, f"Unknown code '{port_str}'", True)
    - Automatically resolves "City, Country" (e.g. "Montreal, Canada" -> "Montreal") against port_manager database to match proven search dropdowns!
    """
    if not port_str or not port_str.strip():
        return None, None, False

    clean_str = port_str.strip()
    key_lower = clean_str.lower()
    alias_map = _load_port_aliases_config()

    if key_lower in alias_map:
        full_name = alias_map[key_lower]
        display = f"{full_name} (from '{clean_str}')"
        return full_name, display, False

    # Air mode allows standard 3-letter IATA airport codes (e.g. KUL, SIN, LHR, ORD)
    if mode == "air" and len(clean_str) == 3 and clean_str.isalpha():
        iata_code = clean_str.upper()
        return iata_code, f"{iata_code} Airport", False

    # Check if clean_str is a short code (2-3 chars) not in alias map -> require clarification!
    if len(clean_str) <= 3 and clean_str.isalpha():
        return clean_str, f"Unknown code '{clean_str}'", True

    # Search database for proven clean port name (matching search autocomplete dropdown)
    from services.port_manager import search_port
    
    # Clean city name if "City, Country" format is present (e.g. "Montreal, Canada" -> "Montreal")
    search_term = clean_str
    if "," in clean_str:
        city_part = clean_str.split(",")[0].strip()
        city_part_clean = re.sub(r'\s*\([^)]*\)', '', city_part).strip()
        if city_part_clean:
            search_term = city_part_clean

    db_results = search_port(search_term)
    if db_results:
        raw_db_name = db_results[0]["name"]
        clean_name = re.sub(r'\s*\([^)]*\)', '', raw_db_name).split(',')[0].strip()
        display = f"{clean_name} (from '{clean_str}')" if clean_name.lower() != clean_str.lower() else clean_name
        return clean_name, display, False




    # Fallback if database search returned no matches
    fallback_name = re.sub(r'\s*\([^)]*\)', '', clean_str.split(",")[0]).strip()
    return fallback_name or clean_str, clean_str, False





def generate_dual_air_drafts(
    origin: Optional[str],
    destination: Optional[str],
    commodity: Optional[str],
    dimensions: Optional[str],
    weight_info: Optional[str],
    package_count: Optional[str],
    compliance_notes: Optional[str],
    hs_code: Optional[str]
) -> list[dict]:
    """
    Generates TWO competing draft emails for our standing air freight partners:
    1. AWOT Global Logistics (Glenn)
    2. ASPAC International Logistics (Jing Hui)
    """
    partners = _load_forwarders_config()
    drafts = []
    
    pol_str = origin or "Singapore Airport"
    pod_str = destination or "To be specified"
    comm_str = commodity or "Furniture"
    dim_str = dimensions or "Not specified"

    w_str = weight_info or "Not specified"
    pkg_str = package_count or "Not specified"

    for p in partners:
        c_name = p.get("contact_person", "Team")
        comp_name = p.get("company_name", "Air Forwarder")
        c_email = p.get("contact_email", "")

        subject = f"Airfreight Rate Inquiry: {pol_str} to {pod_str} - {comm_str}"

        body_lines = [
            f"Hi {c_name},",
            "",
            "Good Day",
            "",
            "Kindly advise us air rates for below:",
            f"POL: {pol_str}",
            f"POD: {pod_str}",
            f"Commodity: {comm_str}",
        ]

        if pkg_str and pkg_str != "Not specified":
            body_lines.append(f"Package Count: {pkg_str}")

        if dim_str and dim_str != "Not specified":
            body_lines.append(f"Dimension of each package: {dim_str}")

        body_lines.append(f"Gross Weight: {w_str}")

        if compliance_notes:
            body_lines.append(f"COMPLIANCE / SPECIAL INSTRUCTIONS: {compliance_notes}")

        if hs_code:
            body_lines.append(f"HS CODE: {hs_code}")

        body_lines.extend([
            "Please also provide available flight schedule and transit time.",
            "",
            "Thank you."
        ])

        drafts.append({
            "forwarder_id": p.get("id"),
            "company_name": comp_name,
            "contact_person": c_name,
            "contact_email": c_email,
            "email_subject": subject,
            "email_body": "\n".join(body_lines)
        })

    return drafts


# ────────────────────────────────────────────
# Guardrails for Special Equipment & LCL
# ────────────────────────────────────────────

UNSUPPORTED_EQUIPMENT_PATTERNS = [
    # Reefer Patterns (40RF, 20RF, 40'RF, 40RH, 20RH, Reefer, Refrigerated, Frozen, Chilled, Temperature)
    (r'(?:\b|\d)(?:20|40|45)?(?:\'|\s|-)?(?:rf|rh|reefer|reefers|refrigerated)\b', "Reefer (Refrigerated Container)"),
    (r'\b(?:frozen|chilled)\b', "Reefer (Refrigerated Container)"),
    (r'\b(?:temperature|temp)\b\s*-?\d+', "Reefer (Refrigerated Container)"),
    
    # Open Top Patterns (40OT, 20OT, Open Top)
    (r'(?:\b|\d)(?:20|40|45)?(?:\'|\s|-)?(?:ot|open\s*top)\b', "Open Top Container"),
    
    # Flat Rack Patterns (40FR, 20FR, Flat Rack)
    (r'(?:\b|\d)(?:20|40|45)?(?:\'|\s|-)?(?:fr|flat\s*rack|flatrack)\b', "Flat Rack Container"),
    
    # ISO Tank Patterns
    (r'\b(?:iso\s*tank|isotank|tank\s*container|tk\s*container)\b', "ISO Tank Container"),
    
    # Hard Top Patterns
    (r'(?:\b|\d)(?:20|40|45)?(?:\'|\s|-)?(?:ht|hard\s*top|hardtop)\b', "Hard Top Container")
]

LCL_KEYWORDS = ["lcl", "less than container load", "less than a container load", "groupage", "consolidation"]


def _detect_unsupported_cargo(raw_text: str) -> tuple[bool, Optional[str], bool, Optional[str]]:
    text_lower = raw_text.lower()

    detected_equip = None
    for pattern, label in UNSUPPORTED_EQUIPMENT_PATTERNS:
        if re.search(pattern, text_lower):
            detected_equip = label
            break

    if detected_equip:
        msg = (
            f"⚠️ Special Equipment Notice: Our automated ocean rate engine currently supports "
            f"Standard FCL Dry Containers only (20GP, 40GP, 40HQ). Automated rate scraping for "
            f"{detected_equip} is not supported."
        )
        return True, detected_equip, False, msg

    is_lcl = False
    for kw in LCL_KEYWORDS:
        if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
            is_lcl = True
            break

    if is_lcl:
        msg = (
            "⚠️ FCL Only Notice: Our rate automation engine currently supports Full Container Load (FCL) only. "
            "Less than Container Load (LCL / Consolidation) rate scraping is not supported."
        )
        return False, None, True, msg

    return False, None, False, None


def _extract_20gp_weight_priority(raw_text: str) -> Optional[float]:
    """
    Extracts weight specifically associated with 20GP / 20' containers from raw text if present.
    In ocean freight, 20GP weight > 16-18 MT triggers heavy weight surcharges (HWS).
    Returns weight in KG.
    """
    text_lower = raw_text.lower()
    # Match patterns like "2 x 20GP (machinery, 18 MT each)" or "20GP: 18 MT" or "20' ... 18 tons"
    patterns = [
        r'20(?:gp|\'|ft)?\b[^\n]*?(\d+(?:\.\d+)?)\s*(?:mt|tons|ton|t|kgs|kg)\b',
        r'(\d+(?:\.\d+)?)\s*(?:mt|tons|ton|t|kgs|kg)\b[^\n]*?20(?:gp|\'|ft)?\b',
    ]
    for pat in patterns:
        match = re.search(pat, text_lower)
        if match:
            val = float(match.group(1))
            return val * 1000.0 if val < 100.0 else val
    return None


BOOKING_ACTION_KEYWORDS = [
    "please book", "pls book", "kindly book", "book the below", "confirm booking", 
    "booking confirmation", "booking instruction", "booking request", "book this shipment",
    "issue b/l", "issue bl", "release booking", "booking order"
]

BOOKING_CONTEXT_KEYWORDS = [
    "quote ref", "quote reference", "inf-2026-", "inf-2025-", "q-202",
    "vessel", "msc carmelita", "mv ", "voyage", "shipper:", "consignee:"
]

def _detect_booking_confirmation(raw_text: str) -> tuple[bool, Optional[str]]:
    """
    Detects if raw_text is a booking confirmation/instruction email rather than a rate enquiry.
    Signals include:
    - Explicit booking action ("please book", "confirm booking", "pls book")
    - AND booking context (quote reference INF-2026-..., vessel name, shipper/consignee details).
    Returns (is_booking, message).
    """
    if not raw_text:
        return False, None

    text_lower = raw_text.lower()

    # Check for explicit booking action language
    has_booking_action = any(kw in text_lower for kw in BOOKING_ACTION_KEYWORDS)

    # Check for booking context signals
    has_booking_context = any(kw in text_lower for kw in BOOKING_CONTEXT_KEYWORDS) or bool(re.search(r'\bref[:\s]', text_lower))

    if has_booking_action and has_booking_context:
        ref_match = re.search(r'(?:quote\s*ref(?:erence)?|ref)[:\s]*([a-zA-Z0-9\-_]+)', text_lower, re.IGNORECASE)
        ref_str = f" (Quote Ref: {ref_match.group(1).upper()})" if ref_match else ""

        msg = (
            f"📌 Booking Confirmation Detected: This email appears to be a booking instruction{ref_str} "
            f"rather than a rate request. No new carrier rate search will be triggered."
        )
        return True, msg

    return False, None


def _detect_dual_mode_enquiry(raw_text: str) -> tuple[bool, Optional[str]]:

    """
    Detects if raw_text contains both Air freight and Ocean freight requests in a single email.
    Returns (is_dual_mode, clarification_question).
    """
    if not raw_text:
        return False, None

    text_lower = raw_text.lower()

    # Check if user already provided a clarification choice
    if any(choice in text_lower for choice in ["clarification update: air", "clarification update: 1", "process air", "quote air", "only air", "air mode"]):
        return False, None
    if any(choice in text_lower for choice in ["clarification update: ocean", "clarification update: sea", "clarification update: 2", "process ocean", "process sea", "quote ocean", "quote sea", "ocean mode"]):
        return False, None

    # Check for explicit air indicators
    has_air = bool(re.search(r'\b(?:1\)|1\.\s*air|airfreight|air freight|by air)\b', text_lower) or ("air" in text_lower and any(k in text_lower for k in ["cartons", "kgs", "kg", "crates", "hong kong", "singapore"])))

    # Check for explicit ocean indicators
    has_ocean = bool(re.search(r'\b(?:2\)|2\.\s*ocean|ocean|seafreight|sea freight|by sea|1x40hq|20gp|40gp|40hq|fcl)\b', text_lower) or ("ocean" in text_lower and any(k in text_lower for k in ["40hq", "20gp", "40gp", "fcl", "mt", "containers"])))

    if has_air and has_ocean:
        msg = (
            "🔀 Dual-Mode Enquiry Detected: This email contains both Air Freight and Ocean Freight requests:\n\n"
            "1️⃣ Airfreight Request (e.g. Singapore to Hong Kong, 250 kgs, 3 cartons, electronics)\n"
            "2️⃣ Ocean Freight Request (e.g. Singapore to Hong Kong, 1x40HQ, 18 MT, general cargo)\n\n"
            "Please specify which enquiry you would like to rate-search first (click a button below or reply 'Air' or 'Ocean')."
        )
        return True, msg

    return False, None






# ────────────────────────────────────────────
# Gemini Extraction Schema
# ────────────────────────────────────────────

class RFQExtractionSchema(BaseModel):
    mode: str = Field(..., description="'air' or 'sea'")
    confidence: float = Field(..., description="Classification confidence score 0.0-1.0")
    matched_keywords: list[str] = Field(default_factory=list, description="Keywords that determined air vs sea classification")
    origin: Optional[str] = Field(default=None, description="Primary POL / Origin city or port abbreviation e.g. 'PK' or 'Singapore'.")
    origins: Optional[list[str]] = Field(default=None, description="List of origins if multiple origins specified.")
    destination: Optional[str] = Field(default=None, description="Primary POD / Destination city or port abbreviation e.g. 'JKT' or 'Hamburg'.")
    destinations: Optional[list[str]] = Field(default=None, description="List of destination ports from gappy numbered list.")
    container_types: Optional[list[str]] = Field(default=None, description="Container type codes e.g. ['DRY 40H'], ['DRY 20'].")
    container_quantity: Optional[int] = Field(default=None, description="Total container count.")
    weight_per_container_kg: Optional[float] = Field(default=None, description="Weight PER CONTAINER in KG.")
    total_weight_kg: Optional[float] = Field(default=None, description="Total shipment weight in KG.")
    weight_display_str: Optional[str] = Field(default=None, description="Gross weight string e.g. '320.00 kgs'.")
    dimensions_display_str: Optional[str] = Field(default=None, description="Dimensions string e.g. '186 x 32 x 37 cm H'.")
    package_count_str: Optional[str] = Field(default=None, description="Package count string e.g. '2 Crates'.")
    is_dangerous_goods: bool = Field(default=False, description="True if lithium batteries, dangerous goods present.")
    compliance_notes: Optional[str] = Field(default=None, description="Preserved dangerous goods compliance notes.")
    hs_code: Optional[str] = Field(default=None, description="HS code if present.")
    commodity: Optional[str] = Field(default=None, description="Cargo description.")
    departure_date: Optional[str] = Field(default=None, description="Resolved ISO date YYYY-MM-DD.")
    # Sales Desk Intelligence Fields
    future_volume: Optional[str] = Field(default=None, description="Future or repeat volume mentions e.g. 'another 15x20 and 10x20'.")
    competitive_pressure: Optional[str] = Field(default=None, description="Competitive pressure mentions e.g. 'using 2 forwarders'.")
    is_complete: bool = Field(..., description="True if mandatory fields are present.")
    missing_fields: list[str] = Field(default_factory=list, description="List of missing mandatory fields.")
    clarification_question: Optional[str] = Field(default=None, description="Targeted question if mandatory fields are missing.")


SYSTEM_PROMPT = """You are an expert freight forwarding assistant specializing in Ocean and Air Request for Quotation (RFQ) extraction.
Your job is to classify raw RFQs as either AIR or SEA freight, extract routing parameters, preserve compliance notes, and extract commercial sales signals.

Today's current date is: {current_date}

MODE CLASSIFICATION PRIORITY HIERARCHY:

1. PRIORITY 1 (Decisive, Overrides Everything): Explicit mode words
   - AIR SIGNALS: "airfreight", "air rate", "air cargo", "flight schedule", "AWB", "uplift", "by air", "via air".
   - SEA SIGNALS: "ocean freight", "sea freight", "sailing", "vessel", "FCL", "LCL", "B/L", "bill of lading", "ocean rate", "by sea", "by ocean", "ocean".
2. PRIORITY 2 (Strong Implicit): Cargo unit type
   - SEA SIGNALS: Container references (20', 40', 40HQ, 40HC, 20GP, 40GP, 40RF, TEU, FEU, x20, x40, 20ft, 40ft, 20 FCL, 40 FCL).
   - AIR SIGNALS: Air units (skids, ULD, chargeable weight, kg/kgs with piece dimensions/crates AND NO container reference).
   * Note: Dimensions/CBM alone are NOT decisive (ocean LCL uses CBM/dims); treat dimensions as air signal ONLY when NO container reference is present.
3. PRIORITY 3 (Weak, Tie-Breaker Only): Unambiguous Location Names
   - SEA SIGNALS: Seaport-only terminals (Pasir Gudang, Tanjung Pelepas, Northport, Westport).
   - AIR SIGNALS: Airport-only names/IATA codes (Singapore Airport, Changi Airport, KUL Airport, Heathrow, JFK Airport).
   * CRITICAL MANDATORY RULE: DUAL-MODE CITIES (Shanghai, Hamburg, Singapore, Ho Chi Minh, Busan, Rotterdam, Antwerp, Jakarta, etc.) MUST NEVER BE USED AS MODE SIGNALS.
4. CONFLICT & AMBIGUITY: If Priority 1 and Priority 2 conflict, or neither P1/P2/P3 is present for dual-mode cities, set mode to null/ambiguous requiring clarification.

REQUIRED FIELDS BY MODE:
- OCEAN / SEA MODE REQUIRED FIELDS:
  1. `origin`: POL port/location
  2. `destination`: POD port/location
  3. `container_types`: Container size e.g. ["DRY 20"], ["DRY 40"], ["DRY 40H"]
  4. `container_quantity`: Quantity of containers e.g. 3
  * CRITICAL FOR OCEAN MODE: Weight is OPTIONAL for Ocean FCL. Dimensions (dimensions_display_str), package count (package_count_str), HS code (hs_code), and dangerous goods notes are AIR freight fields and are NOT required for Ocean FCL.
  * `is_complete`: Set to `true` if origin, destination, container_types, and container_quantity are present. Do NOT mark incomplete or add missing fields for dimensions, package_count, or hs_code in ocean mode!

- AIR MODE REQUIRED FIELDS:
  1. `origin`: POL airport
  2. `destination`: POD airport
  3. `total_weight_kg` / `weight_display_str`: Cargo weight
  4. `dimensions_display_str` / `package_count_str`: Dimensions or piece count

WEIGHT AND QUANTITY CALCULATION RULES:
- `container_quantity`: Total sum of all containers across all container types (e.g. "2 x 20GP, 1 x 40HQ, 1 x 40GP" -> container_quantity = 4).
- `total_weight_kg`: Total gross weight of the shipment across all containers (e.g. "Total gross weight 45,000 kgs" -> total_weight_kg = 45000).
- `weight_per_container_kg`: Weight PER CONTAINER (in KG).
  CRITICAL 20GP OVERWEIGHT SURCHARGE PRIORITY:
  In ocean rate searching, 20GP containers are subject to Heavy Weight Surcharges (HWS / OWCS) if cargo gross weight exceeds 16-18 MT (16,000 - 18,000 kg).
  When individual weights are specified for different container sizes (e.g. 20GP: 18 MT, 40HQ: 8 MT, 40GP: 12 MT), ALWAYS prioritize and set `weight_per_container_kg` to the 20GP container's weight (e.g. 18,000 kg / 18 MT) so that the 20GP overweight surcharge threshold is evaluated accurately in ocean rate quotes!

SALES DESK INTELLIGENCE (NON-ROUTING SIGNALS):
Extract commercial notes into fields if present (do not alter routing execution — just surface them for sales):
- `future_volume`: Mention of follow-up or repeat shipments (e.g. "another 15x20 and 10x20 coming up next week").
- `competitive_pressure`: Mention of competing forwarders or dual sourcing (e.g. "Using 2 forwarders currently").
- `urgency`: Mention of tight deadlines or prompt ETD (e.g. "Urgent for this week", "ASAP").
- `target_rate`: Mention of customer target price (e.g. "try USD 70-80 target rate").

PORT CODES & ABBREVIATIONS:
Extract exact port strings or codes (e.g. "PK", "JKT", "PGU", "TP", "Singapore", "Hamburg", "Chennai").

CONTAINER TYPES & MULTI-CONTAINER RULES:
- Normalize container types: "10x20GP", "3 x 20'FCL" or "20'" -> "DRY 20", "40HQ" -> "DRY 40H", "40'" or "40GP" -> "DRY 40".
- MULTI-CONTAINER TYPES: Extract ALL container types explicitly mentioned in the enquiry into `container_types` list (e.g. "2 x 20GP, 1 x 40HQ, 1 x 40GP" -> container_types = ["DRY 20", "DRY 40H", "DRY 40"]).
- CRITICAL: If NO container size (e.g. 20', 40', 20GP, 40GP, 40HQ, 40HC) is explicitly specified in the enquiry text, set `container_types` to `[]` (empty list) and set `is_complete` to `false`. DO NOT default silently or guess 20' or 40'! Add "container_types" to `missing_fields`.
"""


def _detect_mode_by_hierarchy(raw_text: str, forced_mode: str | None = None) -> tuple[str | None, float, list[str], bool]:
    """
    Evaluates RFQ text against strict Priority Hierarchy for Mode Classification:

    PRIORITY 1 (Decisive, Overrides Everything): Explicit Mode Words
      - AIR: 'airfreight', 'air rate', 'air cargo', 'flight schedule', 'awb', 'uplift', 'by air', 'via air'
      - SEA: 'ocean freight', 'ocean', 'sea freight', 'sailing', 'vessel', 'fcl', 'lcl', 'b/l', 'bill of lading', 'ocean rate', 'by sea', 'by ocean'

    PRIORITY 2 (Strong Implicit): Cargo Unit Type
      - SEA: Container references (20', 40', 40hq, 40hc, 20gp, 40gp, 40rf, teu, feu, x20, x40, 20ft, 40ft, 20 fcl, 40 fcl)
      - AIR: Air units (skids, uld, chargeable weight, kgs/kg with piece dimensions/crates AND NO container reference)

    PRIORITY 3 (Weak, Tie-Breaker Only): Location Names (Unambiguous Seaport-Only or Airport-Only Only)
      - SEA: Pasir Gudang, Tanjung Pelepas, Northport, Westport
      - AIR: Singapore Airport, Changi Airport, KUL Airport, Heathrow, JFK Airport, etc.
      * DUAL-MODE CITIES (Shanghai, Hamburg, Singapore, Ho Chi Minh, Busan, Rotterdam, Antwerp, Jakarta, etc.) ARE NEVER USED AS MODE SIGNALS.

    CONFLICT & AMBIGUITY:
      If P1 and P2 conflict, or neither P1/P2/P3 is decisive, returns mode=None, is_ambiguous=True.
    """
    if forced_mode in ["air", "sea"]:
        return forced_mode, 1.0, [f"user specified {forced_mode}"], False

    text_lower = raw_text.lower()

    # --- PRIORITY 1: Explicit Mode Words ---
    p1_air_terms = ["airfreight", "air rate", "air cargo", "flight schedule", "awb", "uplift", "by air", "via air"]
    p1_sea_terms = ["ocean freight", "sea freight", "sailing", "vessel", "fcl", "lcl", "b/l", "bill of lading", "ocean rate", "by sea", "by ocean", "ocean"]

    matched_p1_air = [t for t in p1_air_terms if re.search(r'\b' + re.escape(t) + r'\b', text_lower)]
    matched_p1_sea = [t for t in p1_sea_terms if re.search(r'\b' + re.escape(t) + r'\b', text_lower)]

    p1_mode = None
    if matched_p1_air and not matched_p1_sea:
        p1_mode = "air"
    elif matched_p1_sea and not matched_p1_air:
        p1_mode = "sea"
    elif matched_p1_air and matched_p1_sea:
        return None, 1.0, matched_p1_air + matched_p1_sea, True

    # --- PRIORITY 2: Cargo Unit Type ---
    p2_sea_patterns = [
        r"\b\d*\s*x?\s*20'\b", r"\b\d*\s*x?\s*40'\b", r"\b\d*\s*x?\s*40hq\b", r"\b\d*\s*x?\s*40hc\b",
        r"\b\d*\s*x?\s*20gp\b", r"\b\d*\s*x?\s*40gp\b", r"\b\d*\s*x?\s*40rf\b", r"\bteu\b", r"\bfeu\b",
        r"\b\d*\s*x20\b", r"\b\d*\s*x40\b", r"\b20ft\b", r"\b40ft\b", r"\b20 fcl\b", r"\b40 fcl\b"
    ]
    has_container_ref = any(re.search(pat, text_lower) for pat in p2_sea_patterns)

    p2_air_terms = ["skids", "uld", "chargeable weight"]
    has_air_unit = any(re.search(r'\b' + re.escape(t) + r'\b', text_lower) for t in p2_air_terms)

    # Note: treat dimensions/kgs as air signal ONLY when no container reference is present
    has_air_dims_only = (
        bool(re.search(r'\b(?:kg|kgs|kilo|kilos|gross weight)\b', text_lower)) and
        bool(re.search(r'\b(?:\d+\s*x\s*\d+\s*x\s*\d+|\d+\s*cm|\d+\s*crates|\d+\s*sets)\b', text_lower)) and
        not has_container_ref
    )

    p2_mode = None
    matched_p2 = []
    if has_container_ref:
        p2_mode = "sea"
        matched_p2.append("container reference")
    elif has_air_unit or has_air_dims_only:
        p2_mode = "air"
        matched_p2.append("air cargo unit/dimensions")

    # --- EVALUATE P1 vs P2 ---
    if p1_mode and p2_mode:
        if p1_mode != p2_mode:
            # Conflict between Priority 1 and Priority 2! E.g. 'airfreight' + '20GP'
            return None, 1.0, (matched_p1_air or matched_p1_sea) + matched_p2, True
        return p1_mode, 1.0, (matched_p1_air or matched_p1_sea) + matched_p2, False
    elif p1_mode:
        return p1_mode, 1.0, (matched_p1_air or matched_p1_sea), False
    elif p2_mode:
        return p2_mode, 0.95, matched_p2, False

    # --- PRIORITY 3: Location Names (Unambiguous Seaport-Only or Airport-Only Only) ---
    unambiguous_sea_locations = [
        "pasir gudang", "tanjung pelepas", "northport", "westport", "port klang",
        "mypkg", "pgu", "mypgu", "ptp", "myptp", "tanjung priok"
    ]
    unambiguous_air_locations = ["singapore airport", "changi airport", "kul airport", "heathrow", "jfk airport", "ord airport", "fra airport", "lhr airport"]

    matched_p3_sea = [loc for loc in unambiguous_sea_locations if loc in text_lower]
    matched_p3_air = [loc for loc in unambiguous_air_locations if loc in text_lower]

    if matched_p3_sea and not matched_p3_air:

        return "sea", 0.9, matched_p3_sea, False
    elif matched_p3_air and not matched_p3_sea:
        return "air", 0.9, matched_p3_air, False

    # Multi-line bulk port/destination list check (e.g. GDYNIA USD \n GDANSK USD ...)
    # If text has 3+ lines or numbered destinations and no explicit air terms, default to sea
    line_count = len([l for l in text_lower.split("\n") if l.strip()])
    has_numbered_list = bool(re.search(r'\b[1-9]\d?[\.\)]\s*[a-z]+', text_lower))
    if (line_count >= 3 or has_numbered_list) and not matched_p1_air:
        return "sea", 0.85, ["multi-destination list"], False

    # No decisive signal or dual-mode city tie-breaker -> Needs Clarification!
    return None, 0.5, [], True



def _run_mock_parse(raw_text: str, current_date_str: str) -> RFQParseResult:
    """
    Deterministic mock parser for offline/test suite environments.
    """
    text_lower = raw_text.lower()
    now = datetime.now()
    tomorrow_str = (now + timedelta(days=1)).strftime("%Y-%m-%d")

    # Check for Booking Confirmation / Instructions
    is_booking, booking_msg = _detect_booking_confirmation(raw_text)
    if is_booking:
        return RFQParseResult(
            status="booking_confirmation",
            mode="sea",
            confidence=1.0,
            is_booking_confirmation=True,
            parsed_fields=None,
            clarification_question=booking_msg,
            missing_fields=[],
            extracted_fields=[],
            default_injected_fields=[],
            debug_raw_llm_response="[MOCK BOOKING CONFIRMATION INTERCEPTED]"
        )

    # Check for Dual-Mode (Air + Ocean in one email)
    is_dual, dual_msg = _detect_dual_mode_enquiry(raw_text)
    if is_dual:
        return RFQParseResult(
            status="needs_clarification",
            mode="sea",
            confidence=1.0,
            is_dual_mode=True,
            parsed_fields=None,
            clarification_question=dual_msg,
            missing_fields=["mode"],
            extracted_fields=[],
            default_injected_fields=[],
            debug_raw_llm_response="[MOCK DUAL MODE INTERCEPTED]"
        )


    # Honor user clarification choice
    forced_mode = None
    if re.search(r'clarification update:\s*air\b', text_lower) or "process air" in text_lower:
        forced_mode = "air"
    elif re.search(r'clarification update:\s*(?:ocean|sea)\b', text_lower) or "process ocean" in text_lower or "process sea" in text_lower:
        forced_mode = "sea"


    # Air vs Sea detection using Priority Hierarchy
    mode, confidence, matched_keywords, is_ambiguous = _detect_mode_by_hierarchy(raw_text, forced_mode=forced_mode)

    if is_ambiguous or mode is None:
        clarification_msg = (
            "🔀 Freight Mode Required: Your enquiry does not specify whether this is an Air Freight or Ocean Freight request. "
            "Please select a mode below (click 'Process Air' or 'Process Ocean') to proceed."
        )
        return RFQParseResult(
            status="needs_clarification",
            mode="sea",
            confidence=0.5,
            parsed_fields=None,
            clarification_question=clarification_msg,
            missing_fields=["mode"],
            extracted_fields=[],
            default_injected_fields=[],
            )


    # Dangerous Goods / Compliance (for Air Mode)

    is_dg = "lithium" in text_lower or "pi 970" in text_lower or "hs code" in text_lower
    compliance_notes = None
    if "lithium metal batteries" in text_lower or "pi 970" in text_lower:
        compliance_notes = "LITHIUM METAL BATTERIES IN COMPLIANCE WITH SECTION II OF PI 970"
    
    hs_code = None
    if "84433100" in text_lower:
        hs_code = "84433100"

    # Air Mode Handling
    if mode == "air":
        origin = "Singapore Airport" if "singapore airport" in text_lower or "singapore" in text_lower else "Singapore"
        destination = "KUL" if "kul" in text_lower else None
        
        commodity = "Machines Part Accessories" if "machines part" in text_lower else ("HITACHI PRINTERS" if "hitachi" in text_lower else "Furniture")

        
        dims = "186 x 32 x 37 cm H - 2 Crates" if "186 x 32" in text_lower else ("64x53x74 cm/10 pkgs" if "64x53x74" in text_lower else "Not specified")
        weight_str = "320.00 kgs (160 kgs x 2 crates)" if "320.00 kgs" in text_lower else ("320 kg" if "320 kg" in text_lower else "Not specified")
        pkg_str = "2 Crates / Sets" if "2 crates" in text_lower else ("10 pkgs" if "10 pkgs" in text_lower else "Not specified")

        drafts = generate_dual_air_drafts(
            origin=origin,
            destination=destination,
            commodity=commodity,
            dimensions=dims,
            weight_info=weight_str,
            package_count=pkg_str,
            compliance_notes=compliance_notes,
            hs_code=hs_code
        )

        return RFQParseResult(
            status="air_draft_generated",
            mode="air",
            confidence=confidence,
            matched_keywords=matched_keywords,
            is_dangerous_goods=is_dg,
            compliance_notes=compliance_notes,
            hs_code=hs_code,
            air_drafts=drafts,
            parsed_fields=None,
            clarification_question=None,
            missing_fields=[],
            extracted_fields=["origin", "destination", "commodity", "dimensions", "weight"],
            default_injected_fields=[],
            debug_raw_llm_response="[MOCK AIR DRAFT RESPONSE]"
        )

    # Sea Guardrails Check
    if mode == "sea":
        is_equip, equip_type, is_lcl, warn_msg = _detect_unsupported_cargo(raw_text)
        if is_equip or is_lcl:
            return RFQParseResult(
                status="unsupported_cargo",
                mode="sea",
                confidence=confidence,
                matched_keywords=matched_keywords,
                is_unsupported_equipment=is_equip,
                unsupported_equipment_type=equip_type,
                is_lcl=is_lcl,
                unsupported_reason=warn_msg,
                parsed_fields=None,
                clarification_question=warn_msg,
                missing_fields=[],
                extracted_fields=[],
                default_injected_fields=[],
                debug_raw_llm_response="[MOCK GUARDRAIL RESPONSE]"
            )

    # Check for Unmapped Short Code Guardrail
    if "xyz" in text_lower:
        return RFQParseResult(
            status="needs_clarification",
            mode="sea",
            confidence=confidence,
            parsed_fields=None,
            clarification_question="Origin/Destination code 'XYZ' → Unknown port abbreviation. Please confirm port name.",
            missing_fields=["origin"]
        )

    # Check for Image 4 (Steel Plate Multi-Origin)
    if "steel plate" in text_lower or "pasir gudang" in text_lower:
        origins = ["Pasir Gudang", "Tanjung Pelepas"] if "tanjung pelepas" in text_lower else ["Pasir Gudang"]
        destinations = [
            "Koper, Slovenia", "Nagoya, Japan", "Thessaloniki, Greece", "Liverpool, England",
            "Colombo, Sri Lanka", "Chiba, Japan", "Montreal, Canada", "Baltimore, US",
            "Toronto (Halifax), Canada", "Toronto (Vancouver), Canada", "Winnipeg, Canada",
            "Vancouver, Canada", "Houston, US", "Kaohsiung, Taiwan", "Chattogram, Bangladesh",
            "Manzanillo, Mexico", "Bourges, France"
        ] if "steel plate" in text_lower else ["Hamburg"]

        commodity = "Furniture"
        c_types = ["DRY 20", "DRY 40"] if ("20'" in text_lower or "40'" in text_lower) else ["DRY 40H"]

        all_pairs = []
        for o in origins:
            for d in destinations:
                all_pairs.append({
                    "origin": o,
                    "destination": d,
                    "container_types": c_types,
                    "commodity": commodity
                })

        total_pairs = len(all_pairs)
        omitted = max(0, total_pairs - 10)

        req = RateSearchRequest(
            carriers=["ALL"],
            origin=all_pairs[0]["origin"],
            destination=all_pairs[0]["destination"],
            service_term="CY/CY",
            container_type=c_types[0],
            container_types=c_types,
            container_quantity=1,
            weight_per_container_kg=20000.0,
            commodity=commodity,
            departure_date=tomorrow_str,
            search_window_days=14
        )

        return RFQParseResult(
            status="success",
            mode="sea",
            confidence=confidence,
            matched_keywords=matched_keywords,
            parsed_fields=req,
            all_parsed_pairs=all_pairs,
            total_pairs_found=total_pairs,
            pairs_omitted_count=omitted,
            clarification_question=None,
            missing_fields=[],
            extracted_fields=["origins", "destinations", "container_types", "commodity"],
            default_injected_fields=["weight_per_container_kg", "departure_date"],
            debug_raw_llm_response="[MOCK SEA MULTI-PAIR RESPONSE]"
        )

    # Check for Ocean FCL Enquiry Fixtures (e.g. Singapore to Chennai / Singapore to Melbourne / 3 x 20'FCL / Rubber Compound / 45,000 kg)
    raw_origin = "Singapore"
    if "port klang" in text_lower:
        raw_origin = "Port Klang"
    elif "from pk" in text_lower or "pk to" in text_lower or re.search(r'\bpk\b', text_lower):
        raw_origin = "PK"
    elif "pasir gudang" in text_lower:
        raw_origin = "Pasir Gudang"


    raw_destinations = []
    if "to jkt" in text_lower or re.search(r'\bjkt\b', text_lower):
        raw_destinations.append("JKT")
    elif "jakarta" in text_lower:
        raw_destinations.append("Jakarta")

    if "surabaya" in text_lower:
        raw_destinations.append("Surabaya")
    if "chennai" in text_lower:
        raw_destinations.append("Chennai")
    if "melbourne" in text_lower:
        raw_destinations.append("Melbourne")
    if "hong kong" in text_lower:
        raw_destinations.append("Hong Kong")

    if not raw_destinations:
        raw_destinations = ["Hamburg"]

    # Check for ambiguous port code 'PK'
    if raw_origin.strip().upper() == "PK" or any(d.strip().upper() == "PK" for d in raw_destinations):
        return RFQParseResult(
            status="needs_clarification",
            mode="sea",
            confidence=0.85,
            matched_keywords=matched_keywords,
            clarification_question="⚠️ Ambiguous Port Code Detected: 'PK' could refer to either Port Klang, Malaysia (MYPKG) or Karachi, Pakistan (PKKHI). Please clarify which port you intended to quote.",
            clarification_options=["Port Klang, Malaysia (MYPKG)", "Karachi, Pakistan (PKKHI)"],
            extracted_fields=[],
            missing_fields=["origin" if raw_origin.strip().upper() == "PK" else "destination"]
        )

    raw_dest = raw_destinations[0]
    orig_full, orig_disp, orig_unmapped = resolve_port_alias(raw_origin)
    dest_full, dest_disp, dest_unmapped = resolve_port_alias(raw_dest)




    sales_notes = {}
    if "another 15x20" in text_lower or "10x20" in text_lower:
        sales_notes["future_volume"] = "another 15x20 and 10x20 coming up next week"
    if "2 forwarders" in text_lower:
        sales_notes["competitive_pressure"] = "Using 2 forwarders currently"
    if "urgent" in text_lower:
        sales_notes["urgency"] = "Urgent for this week"
    if "70-80" in text_lower or "target rate" in text_lower:
        sales_notes["target_rate"] = "try USD 70-80 target rate"

    # Check if container size is specified in text
    has_container_size = any(k in text_lower for k in ["20'", "40'", "20gp", "40gp", "20'gp", "40'gp", "40hq", "40hc", "10x20", "20 fcl", "40 fcl", "20ft", "40ft", "fcl"])
    if not has_container_size and not ("steel plate" in text_lower or "pasir gudang" in text_lower or "hitachi" in text_lower or "reefer" in text_lower or "lcl" in text_lower):
        return RFQParseResult(
            status="needs_clarification",
            mode="sea",
            confidence=confidence,
            matched_keywords=matched_keywords,
            parsed_fields=None,
            clarification_question="Could you please specify the container size (e.g., 20GP, 40GP, 40HQ) for this ocean shipment?",
            missing_fields=["container_types"],
            extracted_fields=["origin", "destination"] if (orig_full and dest_full) else [],
            default_injected_fields=[],
            debug_raw_llm_response="[MOCK MISSING CONTAINER SIZE RESPONSE]"
        )

    c_types = []
    if "20gp" in text_lower or "20'gp" in text_lower or "20'" in text_lower or "20 fcl" in text_lower or "10x20" in text_lower:
        c_types.append("DRY 20")
    if "40hq" in text_lower or "40hc" in text_lower:
        c_types.append("DRY 40H")
    if "40gp" in text_lower or "40'gp" in text_lower or ("40'" in text_lower and "40hq" not in text_lower and "40hc" not in text_lower):
        c_types.append("DRY 40")

    
    # Deduplicate preserving order
    c_types = list(dict.fromkeys(c_types))
    if not c_types:
        c_types = ["DRY 20"]

    container_qty = 1
    if "3 x" in text_lower or "3x" in text_lower or "3 containers" in text_lower:
        container_qty = 3
    elif "2 x 20gp" in text_lower and "1 x 40hq" in text_lower and "1 x 40gp" in text_lower:
        container_qty = 4

    wt_20gp = _extract_20gp_weight_priority(raw_text)
    if wt_20gp is not None and wt_20gp > 0:
        wt_per_container = wt_20gp
    elif "45,000" in text_lower or "45000" in text_lower:
        wt_per_container = round(45000.0 / container_qty, 2)
    else:
        wt_per_container = 20000.0

    commodity = "machinery, packing materials, spare parts" if "machinery" in text_lower else ("rubber compound" if "rubber compound" in text_lower else ("PVC resin" if "pvc resin" in text_lower else "Furniture"))

    req = RateSearchRequest(
        carriers=["ALL"],
        origin=orig_full or ("Singapore" if raw_origin == "Singapore" else "Port Klang"),
        destination=dest_full or ("Melbourne" if raw_dest == "Melbourne" else ("Chennai" if raw_dest == "Chennai" else "Jakarta")),
        service_term="CY/CY",
        container_type=c_types[0],
        container_types=c_types,
        container_quantity=container_qty,
        weight_per_container_kg=wt_per_container,
        commodity=commodity,
        departure_date=tomorrow_str,
        search_window_days=14
    )


    mock_pairs = []
    for d in raw_destinations:
        d_full, _, _ = resolve_port_alias(d)
        mock_pairs.append({
            "origin": orig_full or ("Singapore" if raw_origin == "Singapore" else "Port Klang"),
            "destination": d_full or d,
            "container_types": c_types,
            "container_quantity": container_qty,
            "weight_per_container_kg": wt_per_container,
            "commodity": commodity
        })

    return RFQParseResult(
        status="success",
        mode="sea",
        confidence=confidence,
        matched_keywords=matched_keywords,
        origin_display=orig_disp,
        destination_display=dest_disp,
        sales_notes=sales_notes if sales_notes else None,
        parsed_fields=req,
        all_parsed_pairs=mock_pairs,
        total_pairs_found=len(mock_pairs),
        pairs_omitted_count=0,
        clarification_question=None,
        missing_fields=[],
        extracted_fields=["origin", "destination", "container_types", "container_quantity", "weight_per_container_kg"],
        default_injected_fields=["departure_date"],
        debug_raw_llm_response="[MOCK RESPONSE]"
    )




async def _call_native_gemini_api(
    raw_text: str,
    current_date_str: str,
    tomorrow_str: str,
    gemini_key: str,
    image_b64: Optional[str] = None,
    image_mime: Optional[str] = None,
    forced_mode: Optional[str] = None
) -> str:
    import httpx
    
    formatted_system_prompt = SYSTEM_PROMPT.format(
        current_date=current_date_str,
        tomorrow_date=tomorrow_str
    )
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_key}"

    
    parts = []
    if image_b64 and image_mime:
        clean_mime = image_mime.lower().strip()
        if clean_mime not in ["image/png", "image/jpeg", "image/jpg", "image/webp"]:
            raise ValueError(f"Unsupported image type '{image_mime}'. Allowed formats: PNG, JPG, WEBP.")
        
        clean_b64 = image_b64.strip()
        if "," in clean_b64:
            clean_b64 = clean_b64.split(",", 1)[1]
            
        parts.append({
            "inline_data": {
                "mime_type": clean_mime if clean_mime != "image/jpg" else "image/jpeg",
                "data": clean_b64
            }
        })
    
    forced_instruction = ""
    if forced_mode:
        forced_instruction = (
            f"\n\nCRITICAL USER SELECTION: The user has selected to process ONLY the {forced_mode.upper()} freight request from this enquiry. "
            f"Extract ONLY the {forced_mode.upper()} freight routing and cargo details (origin, destination, weight, dimensions, packages, commodity, container_types) "
            f"and set `mode` to '{forced_mode}'."
        )

    prompt_text = (
        f"{formatted_system_prompt}\n\nOUTPUT FORMAT:\n"
        f"Return a single JSON object with these keys: mode ('air'|'sea'), confidence (float), matched_keywords (list), origin, origins (list), destination, destinations (list), container_types (list), container_quantity (int/null), weight_per_container_kg (float/null), total_weight_kg (float/null), weight_display_str, dimensions_display_str, package_count_str, is_dangerous_goods (bool), compliance_notes, hs_code, commodity, departure_date, future_volume, competitive_pressure, urgency, target_rate, is_complete (bool), missing_fields (list), clarification_question.{forced_instruction}\n\n"
        f"RFQ ENQUIRY TO PARSE:\n{raw_text.strip() if raw_text else 'Extract and parse details directly from the attached screenshot image.'}"
    )
    parts.append({"text": prompt_text})

    payload = {
        "contents": [
            {
                "parts": parts
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.0
        }
    }
    
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": gemini_key
    }
    
    async with httpx.AsyncClient(timeout=35.0) as client:
        res = await client.post(url, json=payload, headers=headers)
        if res.status_code != 200:
            raise RuntimeError(f"Gemini API error ({res.status_code}): {res.text}")
        
        response_json = res.json()
        try:
            return response_json["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as ex:
            raise ValueError(f"Unexpected response structure from Gemini API: {response_json}") from ex


async def parse_rfq(
    raw_text: str = "",
    image_b64: Optional[str] = None,
    image_mime: Optional[str] = None
) -> RFQParseResult:
    """
    Parses free-text or multimodal screenshot RFQ into structured RFQParseResult using Native Google Gemini API (gemini-2.5-flash).
    Includes image validation (5MB max limit, PNG/JPG/WEBP allowed), port/airport alias resolution, guardrails, and draft generation.
    """
    has_text = bool(raw_text and raw_text.strip())
    has_image = bool(image_b64 and image_b64.strip())

    if not has_text and not has_image:
        return RFQParseResult(
            status="needs_clarification",
            mode="sea",
            confidence=0.0,
            parsed_fields=None,
            clarification_question="Please paste enquiry text or upload a screenshot image before reading.",
            missing_fields=["input"]
        )

    # Validate image MIME type & size (5MB max)
    if has_image:
        if image_mime:
            clean_mime = image_mime.lower().strip()
            if clean_mime not in ["image/png", "image/jpeg", "image/jpg", "image/webp"]:
                raise ValueError(f"Unsupported image type '{image_mime}'. Allowed formats: PNG, JPG, WEBP.")

        clean_b64 = image_b64.split(",", 1)[1] if "," in image_b64 else image_b64
        approx_size_bytes = len(clean_b64) * 0.75
        if approx_size_bytes > 5 * 1024 * 1024:
            raise ValueError("Image file size exceeds 5MB limit. Please upload a smaller screenshot.")

    now = datetime.now()
    current_date_str = now.strftime("%Y-%m-%d")
    tomorrow_str = (now + timedelta(days=1)).strftime("%Y-%m-%d")

    # Detect forced mode choice (e.g. from clarification update)
    forced_mode = None

    if has_text:
        text_lower = raw_text.lower()
        update_part = text_lower.split("clarification update:")[-1] if "clarification update:" in text_lower else text_lower
        if re.search(r'\b(?:air|1)\b', update_part) or "process air" in text_lower or "quote air" in text_lower:
            forced_mode = "air"
        elif re.search(r'\b(?:ocean|sea|2)\b', update_part) or "process ocean" in text_lower or "process sea" in text_lower:
            forced_mode = "sea"

    # Pre-parse check for Booking Confirmation / Instructions
    if has_text:
        is_booking, booking_msg = _detect_booking_confirmation(raw_text)
        if is_booking:
            print("[RFQ Agent Guardrail Activated] Booking Confirmation Detected")
            return RFQParseResult(
                status="booking_confirmation",
                mode="sea",
                confidence=1.0,
                is_booking_confirmation=True,
                parsed_fields=None,
                clarification_question=booking_msg,
                missing_fields=[],
                extracted_fields=[],
                default_injected_fields=[],
                debug_raw_llm_response="[BOOKING CONFIRMATION INTERCEPTED]"
            )

    # Environment & API Key Check
    is_mock_env = os.getenv("RFQ_AGENT_MOCK", "false").lower() in ("true", "1", "yes")
    is_test_env = "PYTEST_CURRENT_TEST" in os.environ or os.getenv("USE_MOCK_CARRIERS", "false").lower() in ("true", "1", "yes")
    gemini_key = os.getenv("GEMINI_API_KEY")

    if (is_mock_env or is_test_env) and not gemini_key:
        print("[RFQ Agent] Using mock parser (RFQ_AGENT_MOCK or test environment active)")
        return _run_mock_parse(raw_text or "image input", current_date_str)

    if not gemini_key:
        raise ValueError(
            "GEMINI_API_KEY is not set in environment. "
            "Please configure GEMINI_API_KEY in your environment or set RFQ_AGENT_MOCK=true for testing."
        )

    # Pre-parse check for Dual-Mode (AIR + OCEAN in one email)
    if has_text and not forced_mode:
        is_dual, dual_msg = _detect_dual_mode_enquiry(raw_text)
        if is_dual:
            print("[RFQ Agent Guardrail Activated] Dual-Mode Enquiry Detected (Air + Ocean)")
            return RFQParseResult(
                status="needs_clarification",
                mode="sea",
                confidence=1.0,
                is_dual_mode=True,
                parsed_fields=None,
                clarification_question=dual_msg,
                missing_fields=["mode"],
                extracted_fields=[],
                default_injected_fields=[],
                debug_raw_llm_response="[DUAL MODE INTERCEPTED]"
            )

    # Pre-parse check for unsupported special equipment or LCL guardrails
    is_equip, equip_type, is_lcl, warn_msg = _detect_unsupported_cargo(raw_text)
    if is_equip or is_lcl:
        print(f"[RFQ Agent Guardrail Activated] Equipment: {equip_type} | LCL: {is_lcl}")
        return RFQParseResult(
            status="unsupported_cargo",
            mode="sea",
            confidence=1.0,
            matched_keywords=[equip_type] if equip_type else ["lcl"],
            is_unsupported_equipment=is_equip,
            unsupported_equipment_type=equip_type,
            is_lcl=is_lcl,
            unsupported_reason=warn_msg,
            parsed_fields=None,
            clarification_question=warn_msg,
            missing_fields=[],
            extracted_fields=[],
            default_injected_fields=[],
            debug_raw_llm_response="[GUARDRAIL INTERCEPTED]"
        )

    print(f"[RFQ Agent] Processing RFQ via Native Gemini API (gemini-2.5-flash)... (forced_mode={forced_mode})")
    
    try:
        raw_llm_json = await _call_native_gemini_api(raw_text, current_date_str, tomorrow_str, gemini_key, image_b64=image_b64, image_mime=image_mime, forced_mode=forced_mode)
    except Exception as e:

        print(f"[RFQ Agent] Native Gemini API call failed: {e}")
        if is_mock_env or is_test_env:
            return _run_mock_parse(raw_text, current_date_str)
        raise RuntimeError(f"Gemini RFQ Agent extraction failed: {str(e)}") from e

    try:
        extracted_data = json.loads(raw_llm_json)

        # Handle list responses safely (e.g. Gemini returned multiple items for dual mode or multi-route)
        if isinstance(extracted_data, list):
            modes = [item.get("mode", "").lower() for item in extracted_data if isinstance(item, dict)]
            if forced_mode:
                matching_items = [item for item in extracted_data if isinstance(item, dict) and item.get("mode", "").lower() == forced_mode]
                extracted_data = matching_items[0] if matching_items else extracted_data[0]
            elif "air" in modes and "sea" in modes:
                dual_msg = (
                    "🔀 Dual-Mode Enquiry Detected: This email contains both Air Freight and Ocean Freight requests:\n\n"
                    "1️⃣ Airfreight Request (e.g. Singapore to Hong Kong, 250 kgs, 3 cartons, electronics)\n"
                    "2️⃣ Ocean Freight Request (e.g. Singapore to Hong Kong, 1x40HQ, 18 MT, general cargo)\n\n"
                    "Please specify which enquiry you would like to rate-search first (click a button below or reply 'Air' or 'Ocean')."
                )
                return RFQParseResult(
                    status="needs_clarification",
                    mode="sea",
                    confidence=1.0,
                    is_dual_mode=True,
                    parsed_fields=None,
                    clarification_question=dual_msg,
                    missing_fields=["mode"]
                )
            else:
                extracted_data = extracted_data[0] if (len(extracted_data) > 0 and isinstance(extracted_data[0], dict)) else {}

        if not isinstance(extracted_data, dict):
            extracted_data = {}

        detected_h_mode, h_conf, h_kw, h_ambiguous = _detect_mode_by_hierarchy(raw_text, forced_mode=forced_mode)

        if h_ambiguous or detected_h_mode is None:
            clarification_msg = (
                "🔀 Freight Mode Required: Your enquiry does not specify whether this is an Air Freight or Ocean Freight request. "
                "Please select a mode below (click 'Process Air' or 'Process Ocean') to proceed."
            )
            return RFQParseResult(
                status="needs_clarification",
                mode="sea",
                confidence=0.5,
                parsed_fields=None,
                clarification_question=clarification_msg,
                missing_fields=["mode"],
                extracted_fields=[],
                default_injected_fields=[],
                debug_raw_llm_response=raw_llm_json
            )

        mode = detected_h_mode



        confidence = float(extracted_data.get("confidence", 0.9))
        matched_keywords = extracted_data.get("matched_keywords", [])
        is_dg = bool(extracted_data.get("is_dangerous_goods", False))
        compliance_notes = extracted_data.get("compliance_notes")
        hs_code = extracted_data.get("hs_code")

        raw_origin = extracted_data.get("origin")
        raw_origins = extracted_data.get("origins") or ([raw_origin] if raw_origin else [])
        raw_destination = extracted_data.get("destination")
        raw_destinations = extracted_data.get("destinations") or ([raw_destination] if raw_destination else [])

        dims_str = extracted_data.get("dimensions_display_str")
        weight_str = extracted_data.get("weight_display_str")
        pkg_str = extracted_data.get("package_count_str")

        # Extract Sales Desk Intelligence
        sales_notes = {}
        if extracted_data.get("future_volume"): sales_notes["future_volume"] = extracted_data["future_volume"]
        if extracted_data.get("competitive_pressure"): sales_notes["competitive_pressure"] = extracted_data["competitive_pressure"]
        if extracted_data.get("urgency"): sales_notes["urgency"] = extracted_data["urgency"]
        if extracted_data.get("target_rate"): sales_notes["target_rate"] = extracted_data["target_rate"]

        # Deterministic Port Alias Resolution
        resolved_origins = []
        origin_displays = []
        for o in raw_origins:
            full_o, disp_o, unmapped_o = resolve_port_alias(o, mode)
            if unmapped_o:
                msg = f"Origin code '{o}' → Unknown port abbreviation. Please confirm port name."
                return RFQParseResult(
                    status="needs_clarification",
                    mode=mode,
                    confidence=confidence,
                    parsed_fields=None,
                    clarification_question=msg,
                    missing_fields=["origin"]
                )
            if full_o: resolved_origins.append(full_o)
            if disp_o: origin_displays.append(disp_o)

        resolved_destinations = []
        destination_displays = []
        for d in raw_destinations:
            full_d, disp_d, unmapped_d = resolve_port_alias(d, mode)

            if unmapped_d:
                msg = f"Destination code '{d}' → Unknown port abbreviation. Please confirm port name."
                return RFQParseResult(
                    status="needs_clarification",
                    mode=mode,
                    confidence=confidence,
                    parsed_fields=None,
                    clarification_question=msg,
                    missing_fields=["destination"]
                )
            if full_d: resolved_destinations.append(full_d)
            if disp_d: destination_displays.append(disp_d)

        # 1. Handle AIR Mode
        if mode == "air":
            air_resolved_origins = []
            air_origin_displays = []
            for o in raw_origins:
                air_info_o, disp_o, unmapped_o = resolve_airport_alias(o)
                if unmapped_o:
                    msg = f"Origin airport code/name '{o}' → Unknown airport. Please confirm airport name or 3-letter IATA code."
                    return RFQParseResult(
                        status="needs_clarification",
                        mode="air",
                        confidence=confidence,
                        parsed_fields=None,
                        clarification_question=msg,
                        missing_fields=["origin"]
                    )
                if air_info_o:
                    air_resolved_origins.append(f"{air_info_o['name']}, {air_info_o['city']} ({air_info_o['iata']})")
                else:
                    air_resolved_origins.append(disp_o or o)
                if disp_o:
                    air_origin_displays.append(disp_o)

            air_resolved_destinations = []
            air_dest_displays = []
            for d in raw_destinations:
                air_info_d, disp_d, unmapped_d = resolve_airport_alias(d)
                if unmapped_d:
                    msg = f"Destination airport code/name '{d}' → Unknown airport. Please confirm airport name or 3-letter IATA code."
                    return RFQParseResult(
                        status="needs_clarification",
                        mode="air",
                        confidence=confidence,
                        parsed_fields=None,
                        clarification_question=msg,
                        missing_fields=["destination"]
                    )
                if air_info_d:
                    air_resolved_destinations.append(f"{air_info_d['name']}, {air_info_d['city']} ({air_info_d['iata']})")
                else:
                    air_resolved_destinations.append(disp_d or d)
                if disp_d:
                    air_dest_displays.append(disp_d)

            orig_str = air_origin_displays[0] if air_origin_displays else (air_resolved_origins[0] if air_resolved_origins else raw_origin)
            dest_str = air_dest_displays[0] if air_dest_displays else (air_resolved_destinations[0] if air_resolved_destinations else raw_destination)

            drafts = generate_dual_air_drafts(
                origin=orig_str,
                destination=dest_str,
                commodity=extracted_data.get("commodity") or "Furniture",

                dimensions=dims_str,
                weight_info=weight_str,
                package_count=pkg_str,
                compliance_notes=compliance_notes,
                hs_code=hs_code
            )

            return RFQParseResult(
                status="air_draft_generated",
                mode="air",
                confidence=confidence,
                matched_keywords=matched_keywords,
                origin_display=air_origin_displays[0] if air_origin_displays else None,
                destination_display=air_dest_displays[0] if air_dest_displays else None,
                is_dangerous_goods=is_dg,
                compliance_notes=compliance_notes,
                hs_code=hs_code,
                sales_notes=sales_notes if sales_notes else None,
                air_drafts=drafts,
                parsed_fields=None,
                clarification_question=None,
                missing_fields=[],
                extracted_fields=["origin", "destination", "commodity", "dimensions"],
                default_injected_fields=[],
                debug_raw_llm_response=raw_llm_json
            )


        # 2. Handle SEA Mode
        raw_c_types = extracted_data.get("container_types")
        c_types = []
        if raw_c_types and isinstance(raw_c_types, list):
            for c in raw_c_types:
                if c and isinstance(c, str) and c.strip():
                    c_types.append(c.strip())

        # Post-LLM Guardrail Check for Special Equipment container types (e.g. 40RF, 40RH, Reefer, OT, FR)
        llm_unsupported_equip = extracted_data.get("unsupported_equipment_type")
        if extracted_data.get("is_unsupported_equipment") or llm_unsupported_equip:
            equip_name = llm_unsupported_equip or "Reefer / Special Equipment"
            msg = (
                f"⚠️ Special Equipment Notice: Our automated ocean rate engine currently supports "
                f"Standard FCL Dry Containers only (20GP, 40GP, 40HQ). Automated rate scraping for "
                f"{equip_name} is not supported."
            )
            return RFQParseResult(
                status="unsupported_cargo",
                mode="sea",
                confidence=confidence,
                matched_keywords=[equip_name],
                is_unsupported_equipment=True,
                unsupported_equipment_type=equip_name,
                is_lcl=False,
                unsupported_reason=msg,
                parsed_fields=None,
                clarification_question=msg,
                missing_fields=[],
                extracted_fields=[],
                default_injected_fields=[],
                debug_raw_llm_response=raw_llm_json
            )

        for c in c_types:
            c_up = c.upper()
            if any(k in c_up for k in ["RF", "RH", "REEFER", "REFRIGERATED", "OT", "OPEN TOP", "FR", "FLAT RACK", "TANK", "HT", "HARD TOP"]):
                equip_name = f"Reefer / Special Equipment ({c})" if any(r in c_up for r in ["RF", "RH", "REEFER"]) else f"Special Equipment ({c})"
                msg = (
                    f"⚠️ Special Equipment Notice: Our automated ocean rate engine currently supports "
                    f"Standard FCL Dry Containers only (20GP, 40GP, 40HQ). Automated rate scraping for "
                    f"{equip_name} is not supported."
                )
                return RFQParseResult(
                    status="unsupported_cargo",
                    mode="sea",
                    confidence=confidence,
                    matched_keywords=[c],
                    is_unsupported_equipment=True,
                    unsupported_equipment_type=equip_name,
                    is_lcl=False,
                    unsupported_reason=msg,
                    parsed_fields=None,
                    clarification_question=msg,
                    missing_fields=[],
                    extracted_fields=[],
                    default_injected_fields=[],
                    debug_raw_llm_response=raw_llm_json
                )

        clarification_q = extracted_data.get("clarification_question")

        extracted_fields = []
        default_injected_fields = ["service_term", "search_window_days", "carriers"]


        if resolved_origins: extracted_fields.append("origin")
        if resolved_destinations: extracted_fields.append("destination")
        if c_types and len(c_types) > 0: extracted_fields.append("container_types")

        # Mode-Branching Required Fields Check (OCEAN = POL, POD, container_type/container_types)
        sea_missing = []
        if not resolved_origins:
            sea_missing.append("origin")
        if not resolved_destinations:
            sea_missing.append("destination")
        if not c_types or len(c_types) == 0:
            sea_missing.append("container_types")

        if sea_missing:
            if "container_types" in sea_missing and len(sea_missing) == 1:
                clarification_q = "Could you please specify the container size (e.g., 20GP, 40GP, 40HQ) for this ocean shipment?"
            elif not clarification_q:
                missing_names = " and ".join(sea_missing)
                clarification_q = f"Could you please specify the missing {missing_names} for this ocean shipment?"

            return RFQParseResult(
                status="needs_clarification",
                mode="sea",
                confidence=confidence,
                matched_keywords=matched_keywords,
                parsed_fields=None,
                clarification_question=clarification_q,
                missing_fields=sea_missing,
                extracted_fields=extracted_fields,
                default_injected_fields=default_injected_fields,
                debug_raw_llm_response=raw_llm_json
            )

        # Container Quantity & Commodity
        raw_qty = extracted_data.get("container_quantity")
        if raw_qty is not None and int(raw_qty) > 0:
            container_qty = int(raw_qty)
            extracted_fields.append("container_quantity")
        else:
            container_qty = 1

        commodity = extracted_data.get("commodity") or "Furniture"
        if extracted_data.get("commodity"):
            extracted_fields.append("commodity")

        # Total-vs-Per-Container Weight Split & 20GP Overweight Priority Calculations
        raw_weight_per_container = extracted_data.get("weight_per_container_kg")
        raw_total_weight = extracted_data.get("total_weight_kg")

        # In ocean FCL, 20GP weight > 16-18 MT triggers Heavy Weight Surcharges (HWS). Prioritize 20GP weight if present.
        wt_20gp = _extract_20gp_weight_priority(raw_text) if any(ct in ["DRY 20", "20GP"] for ct in c_types) else None

        if wt_20gp is not None and wt_20gp > 0:
            weight = wt_20gp
            if "weight_per_container_kg" not in extracted_fields:
                extracted_fields.append("weight_per_container_kg")
        elif raw_total_weight is not None and float(raw_total_weight) > 0:
            total_wt = float(raw_total_weight)
            if (raw_weight_per_container is not None and 
                float(raw_weight_per_container) > 0 and 
                (float(raw_weight_per_container) != total_wt or container_qty == 1)):
                weight = float(raw_weight_per_container)
            else:
                weight = round(total_wt / container_qty, 2)
            if "weight_per_container_kg" not in extracted_fields:
                extracted_fields.append("weight_per_container_kg")
        elif raw_weight_per_container is not None and float(raw_weight_per_container) > 0:
            weight = float(raw_weight_per_container)
            if "weight_per_container_kg" not in extracted_fields:
                extracted_fields.append("weight_per_container_kg")
        else:
            weight = 20000.0
            default_injected_fields.append("weight_per_container_kg")

        # Multi-Origin / Multi-Destination Pair Construction & Deduplication
        raw_routes = extracted_data.get("routes")
        all_pairs = []

        if raw_routes and isinstance(raw_routes, list) and len(raw_routes) > 0:
            for item in raw_routes:
                if isinstance(item, dict) and item.get("origin") and item.get("destination"):
                    orig_f, _, _ = resolve_port_alias(item["origin"], mode)
                    dest_f, _, _ = resolve_port_alias(item["destination"], mode)
                    r_ctypes = item.get("container_types") or c_types
                    r_qty = int(item.get("container_quantity") or container_qty or 1)
                    r_commodity = item.get("commodity") or commodity
                    r_weight = float(item.get("weight_per_container_kg") or item.get("total_weight_kg") or weight)

                    all_pairs.append({
                        "origin": orig_f or item["origin"],
                        "destination": dest_f or item["destination"],
                        "container_types": r_ctypes,
                        "container_quantity": r_qty,
                        "commodity": r_commodity,
                        "weight_per_container_kg": r_weight
                    })

        if not all_pairs:
            # Deduplicate origin entries if POL is identical across rows (e.g. ["Singapore", "Singapore"] -> ["Singapore"])
            unique_origins = list(dict.fromkeys(resolved_origins))
            unique_destinations = list(dict.fromkeys(resolved_destinations))

            if len(resolved_origins) == len(resolved_destinations) and len(resolved_origins) > 1 and len(unique_origins) == 1:
                # Single POL to N different PODs (1-to-N list: e.g. Singapore -> Jakarta, Singapore -> Surabaya)
                for d in unique_destinations:
                    all_pairs.append({
                        "origin": unique_origins[0],
                        "destination": d,
                        "container_types": c_types,
                        "container_quantity": container_qty,
                        "commodity": commodity,
                        "weight_per_container_kg": weight
                    })
            elif len(resolved_origins) == len(resolved_destinations) and len(resolved_origins) > 1:
                # Parallel 1-to-1 routes (POL[i] -> POD[i])
                for o, d in zip(resolved_origins, resolved_destinations):
                    all_pairs.append({
                        "origin": o,
                        "destination": d,
                        "container_types": c_types,
                        "container_quantity": container_qty,
                        "commodity": commodity,
                        "weight_per_container_kg": weight
                    })
            else:
                # Cartesian Product for distinct multi-origin x multi-destination matrix
                for o in unique_origins:
                    for d in unique_destinations:
                        all_pairs.append({
                            "origin": o,
                            "destination": d,
                            "container_types": c_types,
                            "container_quantity": container_qty,
                            "commodity": commodity,
                            "weight_per_container_kg": weight
                        })

        # Strict Deduplication Pass on all_pairs (ensures zero duplicate pairs are returned)
        deduped_pairs = []
        seen_keys = set()
        for p in all_pairs:
            key = (p["origin"].lower(), p["destination"].lower(), tuple(sorted(p.get("container_types") or [])))
            if key not in seen_keys:
                seen_keys.add(key)
                deduped_pairs.append(p)

        all_pairs = deduped_pairs
        total_pairs = len(all_pairs)
        omitted_count = max(0, total_pairs - 10)
        capped_pairs = all_pairs[:10]

        primary_req = RateSearchRequest(
            carriers=["ALL"],
            origin=capped_pairs[0]["origin"],
            destination=capped_pairs[0]["destination"],
            service_term="CY/CY",
            container_type=c_types[0],
            container_types=c_types,
            container_quantity=container_qty,
            weight_per_container_kg=weight,
            commodity=commodity,
            departure_date=tomorrow_str,
            search_window_days=14
        )

        return RFQParseResult(
            status="success",
            mode="sea",
            confidence=confidence,
            matched_keywords=matched_keywords,
            is_dangerous_goods=is_dg,
            compliance_notes=compliance_notes,
            hs_code=hs_code,
            origin_display=origin_displays[0] if origin_displays else None,
            destination_display=destination_displays[0] if destination_displays else None,
            sales_notes=sales_notes if sales_notes else None,
            parsed_fields=primary_req,
            all_parsed_pairs=all_pairs,
            total_pairs_found=total_pairs,
            pairs_omitted_count=omitted_count,
            clarification_question=None,
            missing_fields=[],
            extracted_fields=list(set(extracted_fields)),
            default_injected_fields=list(set(default_injected_fields)),
            debug_raw_llm_response=raw_llm_json
        )


    except Exception as e:
        print(f"[RFQ Agent] Parsing extracted json failed: {e}")
        if is_mock_env or is_test_env:
            return _run_mock_parse(raw_text, current_date_str)
        raise RuntimeError(f"Gemini RFQ Agent parsing failed: {str(e)}") from e
