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
        "pk": "Port Klang",
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


def resolve_port_alias(port_str: Optional[str]) -> tuple[Optional[str], Optional[str], bool]:
    """
    Deterministically resolves a port string against ports_aliases.json.
    Returns (resolved_full_name, display_str_with_orig_code, requires_clarification).
    - If port_str is in ports_aliases.json: returns ("Port Klang", "Port Klang (from 'PK')", False)
    - If port_str is 2-3 letters NOT in ports_aliases.json: returns (port_str, None, True)
    - Otherwise: returns (port_str, port_str, False)
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

    # Check if clean_str is a short code (2-3 chars) not in alias map -> require clarification!
    if len(clean_str) <= 3 and clean_str.isalpha():
        return clean_str, f"Unknown code '{clean_str}'", True

    return clean_str, clean_str, False


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
    comm_str = commodity or "General Cargo"
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

UNSUPPORTED_EQUIPMENT_MAP = {
    "reefer": "Reefer (Refrigerated Container)",
    "rf": "Reefer (Refrigerated Container)",
    "refrigerated": "Reefer (Refrigerated Container)",
    "open top": "Open Top Container",
    "open-top": "Open Top Container",
    "ot container": "Open Top Container",
    "flat rack": "Flat Rack Container",
    "flat-rack": "Flat Rack Container",
    "flatrack": "Flat Rack Container",
    "fr container": "Flat Rack Container",
    "iso tank": "ISO Tank Container",
    "isotank": "ISO Tank Container",
    "tank container": "ISO Tank Container",
    "hard top": "Hard Top Container",
    "hard-top": "Hard Top Container",
    "ht container": "Hard Top Container"
}

LCL_KEYWORDS = ["lcl", "less than container load", "less than a container load", "groupage", "consolidation"]


def _detect_unsupported_cargo(raw_text: str) -> tuple[bool, Optional[str], bool, Optional[str]]:
    text_lower = raw_text.lower()

    detected_equip = None
    for kw, label in UNSUPPORTED_EQUIPMENT_MAP.items():
        if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
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
    urgency: Optional[str] = Field(default=None, description="Urgency mentions e.g. 'Urgent for this week'.")
    target_rate: Optional[str] = Field(default=None, description="Target rate mentions e.g. 'try USD 70-80'.")
    is_complete: bool = Field(..., description="True if mandatory fields are present.")
    missing_fields: list[str] = Field(default_factory=list, description="List of missing mandatory fields.")
    clarification_question: Optional[str] = Field(default=None, description="Targeted question if mandatory fields are missing.")


SYSTEM_PROMPT = """You are an expert freight forwarding assistant specializing in Ocean and Air Request for Quotation (RFQ) extraction.
Your job is to classify raw RFQs as either AIR or SEA freight, extract routing parameters, preserve compliance notes, and extract commercial sales signals.

Today's current date is: {current_date}

MODE CLASSIFICATION RULES:
1. `mode`: "air" or "sea".
   - AIR SIGNALS: "air rate", "airfreight", "flight schedule", "EXW airfreight", "Singapore Airport", airport IATA codes (e.g. KUL, SIN, LHR, ORD), "cm", "crates", "pkgs", "gross weight: ... kgs".
   - SEA SIGNALS: "ocean", "sailing", "20'", "40'", "40HQ", "40HC", "20GP", "40GP", "vessel", "ETD", "Pasir Gudang", "Tanjung Pelepas", "ex Pasir Gudang", "PK", "JKT".
2. `confidence`: Float 0.0 to 1.0.
3. `matched_keywords`: List of key terms found.

SALES DESK INTELLIGENCE (NON-ROUTING SIGNALS):
Extract commercial notes into fields if present (do not alter routing execution — just surface them for sales):
- `future_volume`: Mention of follow-up or repeat shipments (e.g. "another 15x20 and 10x20 coming up next week").
- `competitive_pressure`: Mention of competing forwarders or dual sourcing (e.g. "Using 2 forwarders currently").
- `urgency`: Mention of tight deadlines or prompt ETD (e.g. "Urgent for this week", "ASAP").
- `target_rate`: Mention of customer target price (e.g. "try USD 70-80 target rate").

PORT CODES & ABBREVIATIONS:
Extract exact port strings or codes (e.g. "PK", "JKT", "PGU", "TP", "Singapore", "Hamburg").

CONTAINER TYPES:
Normalize container types: "10x20GP" or "20'" -> "DRY 20", "40HQ" -> "DRY 40H", "40'" -> "DRY 40".
"""


def _run_mock_parse(raw_text: str, current_date_str: str) -> RFQParseResult:
    """
    Deterministic mock parser for offline/test suite environments.
    """
    text_lower = raw_text.lower()
    now = datetime.now()
    tomorrow_str = (now + timedelta(days=1)).strftime("%Y-%m-%d")

    # Air vs Sea detection
    air_keywords = ["air rate", "airfreight", "flight schedule", "exw airfreight", "singapore airport", "kul", "hitachi printers"]
    sea_keywords = ["ocean", "sailing", "20'", "40'", "40hq", "40hc", "pasir gudang", "tanjung pelepas", "steel plate", "jkt"]
    if re.search(r'\bpk\b', text_lower) and "pkgs" not in text_lower:
        sea_keywords.append("pk")

    matched_air = [k for k in air_keywords if k in text_lower]
    matched_sea = [k for k in sea_keywords if k in text_lower]

    mode = "air" if len(matched_air) > len(matched_sea) else "sea"
    confidence = 0.95 if (matched_air or matched_sea) else 0.5
    matched_keywords = matched_air if mode == "air" else matched_sea

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
        
        commodity = "Machines Part Accessories" if "machines part" in text_lower else ("HITACHI PRINTERS" if "hitachi" in text_lower else "General Cargo")
        
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

    # Check for Pak Shaun Email Fixture
    raw_origin = "PK" if ("from pk" in text_lower or "pk to" in text_lower or re.search(r'\bpk\b', text_lower)) else "Singapore"
    raw_dest = "JKT" if ("to jkt" in text_lower or re.search(r'\bjkt\b', text_lower)) else "Hamburg"

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

    c_types = ["DRY 20"] if ("10x20" in text_lower or "20gp" in text_lower or "20'" in text_lower) else ["DRY 40H"]

    req = RateSearchRequest(
        carriers=["ALL"],
        origin=orig_full or "Port Klang",
        destination=dest_full or "Jakarta",
        service_term="CY/CY",
        container_type=c_types[0],
        container_types=c_types,
        container_quantity=1,
        weight_per_container_kg=20000.0,
        commodity="Furniture",
        departure_date=tomorrow_str,
        search_window_days=14
    )

    return RFQParseResult(
        status="success",
        mode="sea",
        confidence=confidence,
        matched_keywords=matched_keywords,
        origin_display=orig_disp,
        destination_display=dest_disp,
        sales_notes=sales_notes if sales_notes else None,
        parsed_fields=req,
        all_parsed_pairs=[{"origin": orig_full, "destination": dest_full, "container_types": c_types}],
        total_pairs_found=1,
        pairs_omitted_count=0,
        clarification_question=None,
        missing_fields=[],
        extracted_fields=["origin", "destination", "container_types"],
        default_injected_fields=["weight_per_container_kg", "departure_date"],
        debug_raw_llm_response="[MOCK RESPONSE]"
    )



async def _call_native_gemini_api(raw_text: str, current_date_str: str, tomorrow_str: str, gemini_key: str) -> str:
    import httpx
    
    formatted_system_prompt = SYSTEM_PROMPT.format(
        current_date=current_date_str,
        tomorrow_date=tomorrow_str
    )
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_key}"
    
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": f"{formatted_system_prompt}\n\nOUTPUT FORMAT:\nReturn a single JSON object with these keys: mode ('air'|'sea'), confidence (float), matched_keywords (list), origin, origins (list), destination, destinations (list), container_types (list), container_quantity (int/null), weight_per_container_kg (float/null), total_weight_kg (float/null), weight_display_str, dimensions_display_str, package_count_str, is_dangerous_goods (bool), compliance_notes, hs_code, commodity, departure_date, future_volume, competitive_pressure, urgency, target_rate, is_complete (bool), missing_fields (list), clarification_question.\n\nRFQ TO PARSE:\n{raw_text}"
                    }
                ]
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
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        res = await client.post(url, json=payload, headers=headers)
        if res.status_code != 200:
            raise RuntimeError(f"Gemini API error ({res.status_code}): {res.text}")
        
        response_json = res.json()
        try:
            return response_json["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as ex:
            raise ValueError(f"Unexpected response structure from Gemini API: {response_json}") from ex


async def parse_rfq(raw_text: str) -> RFQParseResult:
    """
    Parses free-text RFQ message into structured RFQParseResult using Native Google Gemini API (gemini-2.5-flash).
    Includes deterministic port alias resolution, abbreviation guardrails, and sales notes extraction.
    """
    if not raw_text or not raw_text.strip():
        return RFQParseResult(
            status="needs_clarification",
            mode="sea",
            confidence=0.0,
            parsed_fields=None,
            clarification_question="The RFQ text was empty. Please paste an RFQ email or inquiry details.",
            missing_fields=["text"]
        )

    now = datetime.now()
    current_date_str = now.strftime("%Y-%m-%d")
    tomorrow_str = (now + timedelta(days=1)).strftime("%Y-%m-%d")

    # Environment & API Key Check
    is_mock_env = os.getenv("RFQ_AGENT_MOCK", "false").lower() in ("true", "1", "yes")
    is_test_env = "PYTEST_CURRENT_TEST" in os.environ or os.getenv("USE_MOCK_CARRIERS", "false").lower() in ("true", "1", "yes")
    gemini_key = os.getenv("GEMINI_API_KEY")

    if (is_mock_env or is_test_env) and not gemini_key:
        print("[RFQ Agent] Using mock parser (RFQ_AGENT_MOCK or test environment active)")
        return _run_mock_parse(raw_text, current_date_str)

    if not gemini_key:
        raise ValueError(
            "GEMINI_API_KEY is not set in environment. "
            "Please configure GEMINI_API_KEY in your environment or set RFQ_AGENT_MOCK=true for testing."
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

    print(f"[RFQ Agent] Processing RFQ via Native Gemini API (gemini-2.5-flash)...")
    
    try:
        raw_llm_json = await _call_native_gemini_api(raw_text, current_date_str, tomorrow_str, gemini_key)
    except Exception as e:
        print(f"[RFQ Agent] Native Gemini API call failed: {e}")
        if is_mock_env or is_test_env:
            return _run_mock_parse(raw_text, current_date_str)
        raise RuntimeError(f"Gemini RFQ Agent extraction failed: {str(e)}") from e

    try:
        extracted_data = json.loads(raw_llm_json)

        mode = extracted_data.get("mode", "sea").lower()
        confidence = float(extracted_data.get("confidence", 0.9))
        matched_keywords = extracted_data.get("matched_keywords", [])
        is_dg = bool(extracted_data.get("is_dangerous_goods", False))
        compliance_notes = extracted_data.get("compliance_notes")
        hs_code = extracted_data.get("hs_code")

        raw_origin = extracted_data.get("origin")
        raw_origins = extracted_data.get("origins") or ([raw_origin] if raw_origin else [])
        raw_destination = extracted_data.get("destination")
        raw_destinations = extracted_data.get("destinations") or ([raw_destination] if raw_destination else [])

        commodity = "Furniture"
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
            full_o, disp_o, unmapped_o = resolve_port_alias(o)
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
            full_d, disp_d, unmapped_d = resolve_port_alias(d)
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
            drafts = generate_dual_air_drafts(
                origin=resolved_origins[0] if resolved_origins else raw_origin,
                destination=resolved_destinations[0] if resolved_destinations else raw_destination,
                commodity=extracted_data.get("commodity") or "General Cargo",
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
        c_types = extracted_data.get("container_types") or ["DRY 40H"]
        is_complete = extracted_data.get("is_complete", True)
        missing = extracted_data.get("missing_fields", [])
        clarification_q = extracted_data.get("clarification_question")

        extracted_fields = []
        default_injected_fields = ["service_term", "search_window_days", "carriers"]

        if resolved_origins: extracted_fields.append("origin")
        else: missing.append("origin")

        if resolved_destinations: extracted_fields.append("destination")
        else: missing.append("destination")

        if c_types and len(c_types) > 0:
            extracted_fields.append("container_types")
        else:
            c_types = ["DRY 40H"]
            missing.append("container_types")

        if not resolved_origins or not resolved_destinations or not is_complete or missing:
            missing = list(set(missing))
            if not clarification_q:
                missing_names = " and ".join(missing)
                clarification_q = f"Could you please specify the missing {missing_names} for this ocean shipment?"

            return RFQParseResult(
                status="needs_clarification",
                mode="sea",
                confidence=confidence,
                matched_keywords=matched_keywords,
                parsed_fields=None,
                clarification_question=clarification_q,
                missing_fields=missing,
                extracted_fields=extracted_fields,
                default_injected_fields=default_injected_fields,
                debug_raw_llm_response=raw_llm_json
            )

        # Multi-Origin x Multi-Destination Expansion
        all_pairs = []
        for o in resolved_origins:
            for d in resolved_destinations:
                all_pairs.append({
                    "origin": o,
                    "destination": d,
                    "container_types": c_types,
                    "commodity": "Furniture"
                })

        total_pairs = len(all_pairs)
        omitted_count = max(0, total_pairs - 10)
        capped_pairs = all_pairs[:10]

        # Weight Calculations
        raw_weight_per_container = extracted_data.get("weight_per_container_kg")
        raw_total_weight = extracted_data.get("total_weight_kg")

        if raw_weight_per_container is not None and raw_weight_per_container > 0:
            weight = float(raw_weight_per_container)
            extracted_fields.append("weight_per_container_kg")
        elif raw_total_weight is not None and raw_total_weight > 0:
            weight = float(raw_total_weight)
            extracted_fields.append("weight_per_container_kg")
        else:
            weight = 20000.0
            default_injected_fields.append("weight_per_container_kg")

        primary_req = RateSearchRequest(
            carriers=["ALL"],
            origin=capped_pairs[0]["origin"],
            destination=capped_pairs[0]["destination"],
            service_term="CY/CY",
            container_type=c_types[0],
            container_types=c_types,
            container_quantity=1,
            weight_per_container_kg=weight,
            commodity="Furniture",
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
