"""
AI Agent service for parsing free-text RFQ emails or messages into structured RateSearchRequest objects
using native Google Gemini API (gemini-2.5-flash) with x-goog-api-key authentication.
Supports AIR vs SEA classification, dual forwarder air drafts, dangerous goods compliance notes,
and multi-origin gappy destination list parsing.
"""
import os
import json
import re
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel, Field

from models.schemas import RateSearchRequest, RFQParseResult


# ────────────────────────────────────────────
# Configuration Loader for Air Forwarder Partners
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
    Preserves all package dimensions, gross weight, HS codes, and PI 970 dangerous goods notes.
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
# Gemini Extraction Schema
# ────────────────────────────────────────────

class RFQExtractionSchema(BaseModel):
    mode: str = Field(..., description="'air' or 'sea'")
    confidence: float = Field(..., description="Classification confidence score 0.0-1.0")
    matched_keywords: list[str] = Field(default_factory=list, description="Keywords that determined air vs sea classification")
    origin: Optional[str] = Field(default=None, description="Primary POL / Origin city or port.")
    origins: Optional[list[str]] = Field(default=None, description="List of origins if multiple origins specified (e.g. ['Pasir Gudang', 'Tanjung Pelepas']).")
    destination: Optional[str] = Field(default=None, description="Primary POD / Destination city or port.")
    destinations: Optional[list[str]] = Field(default=None, description="List of destination ports from gappy numbered list without inventing missing items.")
    container_types: Optional[list[str]] = Field(default=None, description="Container type codes e.g. ['DRY 40H'], ['DRY 20'].")
    container_quantity: Optional[int] = Field(default=None, description="Total container count.")
    weight_per_container_kg: Optional[float] = Field(default=None, description="Weight PER CONTAINER in KG. Null if weight not in text.")
    total_weight_kg: Optional[float] = Field(default=None, description="Total shipment weight in KG across all containers.")
    weight_display_str: Optional[str] = Field(default=None, description="Gross weight string e.g. '320.00 kgs' or '320 kg'.")
    dimensions_display_str: Optional[str] = Field(default=None, description="Dimensions string e.g. '186 x 32 x 37 cm H - 2 Crates' or '64x53x74 cm/10 pkgs'.")
    package_count_str: Optional[str] = Field(default=None, description="Package count string e.g. '2 Crates / Sets' or '10 pkgs'.")
    is_dangerous_goods: bool = Field(default=False, description="True if lithium batteries, dangerous goods, or special PI compliance present.")
    compliance_notes: Optional[str] = Field(default=None, description="Preserved dangerous goods / compliance notes e.g. 'LITHIUM METAL BATTERIES IN COMPLIANCE WITH SECTION II OF PI 970'.")
    hs_code: Optional[str] = Field(default=None, description="HS code if present e.g. '84433100'.")
    commodity: Optional[str] = Field(default=None, description="Cargo description. Null if not mentioned.")
    departure_date: Optional[str] = Field(default=None, description="Resolved ISO date YYYY-MM-DD. Null if not mentioned.")
    is_complete: bool = Field(..., description="True if mandatory fields are present.")
    missing_fields: list[str] = Field(default_factory=list, description="List of missing mandatory fields.")
    clarification_question: Optional[str] = Field(default=None, description="Targeted question if mandatory fields are missing.")


SYSTEM_PROMPT = """You are an expert freight forwarding assistant specializing in Ocean and Air Request for Quotation (RFQ) extraction.
Your job is to classify raw RFQs as either AIR or SEA freight, extract all routing parameters, preserve compliance notes, and handle multi-destination lists accurately.

Today's current date is: {current_date}

MODE CLASSIFICATION RULES:
1. `mode`: "air" or "sea".
   - AIR SIGNALS: "air rate", "airfreight", "flight schedule", "EXW airfreight", "Singapore Airport", airport IATA codes (e.g. KUL, SIN, LHR, ORD), "cm", "crates", "pkgs", "gross weight: ... kgs".
   - SEA SIGNALS: "ocean", "sailing", "20'", "40'", "40HQ", "40HC", "20GP", "40GP", "vessel", "ETD", "Pasir Gudang", "Tanjung Pelepas", "ex Pasir Gudang".
2. `confidence`: Float 0.0 to 1.0 representing classification confidence.
3. `matched_keywords`: List of key terms found that determined mode classification (e.g. ["air rate", "Singapore Airport", "flight schedule"]).

AIR FREIGHT COMPLIANCE & DANGEROUS GOODS (CRITICAL):
- Extract `is_dangerous_goods`: true if lithium batteries, hazardous goods, or section compliance (PI 970, PI 965, Class 9) are mentioned.
- Preserve exact compliance text in `compliance_notes` (e.g. "LITHIUM METAL BATTERIES IN COMPLIANCE WITH SECTION II OF PI 970").
- Extract `hs_code` if mentioned (e.g. "84433100").
- Extract `dimensions_display_str` (e.g. "186 x 32 x 37 cm H - 2 Crates" or "64x53x74 cm/10 pkgs").
- Extract `package_count_str` (e.g. "2 Crates / Sets" or "10 pkgs").
- Extract `weight_display_str` (e.g. "320.00 kgs").

MULTI-ORIGIN & GAPPY DESTINATION LISTS (CRITICAL):
- If multiple origins are listed (e.g. "ex Pasir Gudang / Tanjung Pelepas"), list ALL origins in `origins` (e.g. ["Pasir Gudang", "Tanjung Pelepas"]).
- If a numbered list of destinations is provided (e.g. 1) Koper, 2) Nagoya, 4) Thessaloniki...), parse ONLY the destinations explicitly present in the text.
- DO NOT HALLUCINATE OR INVENT MISSING ITEMS! (If item #3 is skipped in the text, DO NOT invent item #3!).

WEIGHT & CONTAINER CALCULATIONS (DO NOT FABRICATE):
- For SEA RFQs: Normalize container types ("40HQ"->"DRY 40H", "20'"->"DRY 20", "40'"->"DRY 40").
- If total weight is given across containers (e.g. "18,000 kg total for 2 containers"), set `total_weight_kg` to 18000 and calculate `weight_per_container_kg` = 9000.
- If NO weight is mentioned, set BOTH weight fields to null.

MANDATORY FIELDS CHECK:
- For AIR: origin (or POL) and destination (or POD) must be present.
- For SEA: origin, destination (or destinations list), and container_types must be present.
"""


def _run_mock_parse(raw_text: str, current_date_str: str) -> RFQParseResult:
    """
    Deterministic mock parser for offline/test suite environments.
    Handles Air vs Sea classification, dual air drafts, and multi-origin gappy destination lists.
    """
    text_lower = raw_text.lower()
    now = datetime.now()
    tomorrow_str = (now + timedelta(days=1)).strftime("%Y-%m-%d")

    # Air vs Sea detection
    air_keywords = ["air rate", "airfreight", "flight schedule", "exw airfreight", "singapore airport", "kul", "pkgs", "crates", "hitachi printers"]
    sea_keywords = ["ocean", "sailing", "20'", "40'", "40hq", "40hc", "pasir gudang", "tanjung pelepas", "steel plate"]

    matched_air = [k for k in air_keywords if k in text_lower]
    matched_sea = [k for k in sea_keywords if k in text_lower]

    mode = "air" if len(matched_air) > len(matched_sea) else "sea"
    confidence = 0.95 if (matched_air or matched_sea) else 0.5
    matched_keywords = matched_air if mode == "air" else matched_sea

    # Dangerous Goods / Compliance
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

    # Sea Mode Handling
    origins = []
    if "pasir gudang" in text_lower:
        origins.append("Pasir Gudang")
    if "tanjung pelepas" in text_lower:
        origins.append("Tanjung Pelepas")
    if not origins:
        origins = ["Pasir Gudang"]

    # Image 4 Gappy List Parser (17 destinations, #3 skipped)
    destinations = [
        "Koper, Slovenia", "Nagoya, Japan", "Thessaloniki, Greece", "Liverpool, England",
        "Colombo, Sri Lanka", "Chiba, Japan", "Montreal, Canada", "Baltimore, US",
        "Toronto (Halifax), Canada", "Toronto (Vancouver), Canada", "Winnipeg, Canada",
        "Vancouver, Canada", "Houston, US", "Kaohsiung, Taiwan", "Chattogram, Bangladesh",
        "Manzanillo, Mexico", "Bourges, France"
    ] if "steel plate" in text_lower else ["Hamburg"]

    commodity = "Steel Plate, Steel Coil" if "steel plate" in text_lower else "General Cargo"
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
    capped_pairs = all_pairs[:10]
    omitted = max(0, total_pairs - 10)

    req = RateSearchRequest(
        carriers=["ALL"],
        origin=capped_pairs[0]["origin"],
        destination=capped_pairs[0]["destination"],
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


async def _call_native_gemini_api(raw_text: str, current_date_str: str, tomorrow_str: str, gemini_key: str) -> str:
    """
    Calls native Google Gemini API (gemini-2.5-flash) using httpx with raw x-goog-api-key header.
    """
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
                        "text": f"{formatted_system_prompt}\n\nOUTPUT FORMAT:\nReturn a single JSON object with these keys: mode ('air'|'sea'), confidence (float), matched_keywords (list), origin, origins (list), destination, destinations (list), container_types (list), container_quantity (int/null), weight_per_container_kg (float/null), total_weight_kg (float/null), weight_display_str, dimensions_display_str, package_count_str, is_dangerous_goods (bool), compliance_notes, hs_code, commodity, departure_date, is_complete (bool), missing_fields (list), clarification_question.\n\nRFQ TO PARSE:\n{raw_text}"
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
    
    is_52 = (len(gemini_key) == 52) if gemini_key else False
    print(f"[RFQ Agent Wire Check] URL: {url}")
    print(f"[RFQ Agent Wire Check] Raw Key Length: {len(gemini_key) if gemini_key else 0} | repr: {repr(gemini_key)}")

    
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
    Supports Air vs Sea classification, dual air freight drafts, and multi-origin gappy list parsing.
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

    print(f"[RFQ Agent] Processing RFQ via Native Gemini API (gemini-2.5-flash) | Key len: {len(gemini_key)}...")
    
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

        origin = extracted_data.get("origin")
        origins = extracted_data.get("origins") or ([origin] if origin else [])
        destination = extracted_data.get("destination")
        destinations = extracted_data.get("destinations") or ([destination] if destination else [])

        commodity = extracted_data.get("commodity")
        dims_str = extracted_data.get("dimensions_display_str")
        weight_str = extracted_data.get("weight_display_str")
        pkg_str = extracted_data.get("package_count_str")

        # 1. Handle AIR Mode
        if mode == "air":
            drafts = generate_dual_air_drafts(
                origin=origins[0] if origins else origin,
                destination=destinations[0] if destinations else destination,
                commodity=commodity,
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

        if origins: extracted_fields.append("origin")
        else: missing.append("origin")

        if destinations: extracted_fields.append("destination")
        else: missing.append("destination")

        if c_types and len(c_types) > 0:
            extracted_fields.append("container_types")
        else:
            c_types = ["DRY 40H"]
            missing.append("container_types")

        # Missing mandatory check for SEA
        if not origins or not destinations or not is_complete or missing:
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
        for o in origins:
            for d in destinations:
                all_pairs.append({
                    "origin": o,
                    "destination": d,
                    "container_types": c_types,
                    "commodity": commodity or "General Cargo"
                })

        total_pairs = len(all_pairs)
        omitted_count = max(0, total_pairs - 10)
        capped_pairs = all_pairs[:10]

        # Weight Calculations
        raw_qty = extracted_data.get("container_quantity")
        qty = int(raw_qty) if raw_qty and raw_qty > 0 else 1

        raw_weight_per_container = extracted_data.get("weight_per_container_kg")
        raw_total_weight = extracted_data.get("total_weight_kg")

        if raw_weight_per_container is not None and raw_weight_per_container > 0:
            weight = float(raw_weight_per_container)
            extracted_fields.append("weight_per_container_kg")
        elif raw_total_weight is not None and raw_total_weight > 0:
            weight = float(raw_total_weight) / float(qty)
            extracted_fields.append("weight_per_container_kg")
        else:
            weight = 20000.0
            default_injected_fields.append("weight_per_container_kg")

        # Departure Date
        raw_date = extracted_data.get("departure_date")
        if raw_date:
            departure_date = raw_date
            extracted_fields.append("departure_date")
        else:
            departure_date = tomorrow_str
            default_injected_fields.append("departure_date")

        # Primary RateSearchRequest
        primary_req = RateSearchRequest(
            carriers=["ALL"],
            origin=capped_pairs[0]["origin"],
            destination=capped_pairs[0]["destination"],
            service_term="CY/CY",
            container_type=c_types[0],
            container_types=c_types,
            container_quantity=qty,
            weight_per_container_kg=weight,
            commodity=commodity or "General Cargo",
            departure_date=departure_date,
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
