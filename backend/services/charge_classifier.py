"""
Charge Classifier — rule-based classification of freight charge line items.

Classifies each charge into one of:
- BASIC_OCEAN_FREIGHT
- DISCOUNT
- FREIGHT_SURCHARGE_INCLUDED
- ORIGIN_CHARGE_EXCLUDED
- DESTINATION_CHARGE_EXCLUDED
- UNCERTAIN_EXCLUDED
"""
import re
from typing import Optional
from models.schemas import ChargeCategory


def is_weight_surcharge_applicable(
    charge_name: str,
    weight_per_container_kg: Optional[float] = None,
    container_type: Optional[str] = None
) -> tuple[bool, str]:
    """
    Evaluates whether a weight-tier or overweight surcharge is applicable for the given cargo weight / container gross weight.

    Returns:
        (is_applicable: bool, reason: str)
    """
    if weight_per_container_kg is None or weight_per_container_kg <= 0:
        return True, "No weight provided; default to applicable"

    name_clean = charge_name.lower().strip()
    name_clean = re.sub(r"\s+", " ", name_clean)

    cargo_wt_kg = float(weight_per_container_kg)
    cargo_wt_tons = cargo_wt_kg / 1000.0

    c_type_upper = (container_type or "").upper()
    if "20" in c_type_upper:
        tare_kg = 2200.0
    elif "40" in c_type_upper or "45" in c_type_upper:
        tare_kg = 3800.0
    else:
        tare_kg = 3000.0

    gross_wt_kg = cargo_wt_kg + tare_kg
    gross_wt_tons = gross_wt_kg / 1000.0

    # 1. Pattern: Between MIN and MAX ton/tons/mt/kg
    m_between = re.search(
        r"between\s+(\d+(?:\.\d+)?)\s+(?:and|to|-)\s+(\d+(?:\.\d+)?)\s*(ton|tons|mt|tonne|tonnes|kg)?",
        name_clean
    )
    if m_between:
        val1 = float(m_between.group(1))
        val2 = float(m_between.group(2))
        unit = (m_between.group(3) or "ton").lower()

        min_kg = val1 if unit == "kg" else val1 * 1000.0
        max_kg = val2 if unit == "kg" else val2 * 1000.0

        min_tons, max_tons = min_kg / 1000.0, max_kg / 1000.0

        is_gross = any(k in name_clean for k in ["gross", "vgm", "container weight"])
        eval_kg = gross_wt_kg if is_gross else cargo_wt_kg
        eval_tons = gross_wt_tons if is_gross else cargo_wt_tons

        if eval_kg < (min_kg - 0.1) or eval_kg > (max_kg + 0.1):
            wt_type_str = f"Gross Weight ({eval_tons:.1f}T)" if is_gross else f"Cargo Weight ({eval_tons:.1f}T)"
            return False, f"Not applicable: {wt_type_str} is outside required range [{min_tons:.1f}T - {max_tons:.1f}T]"
        return True, "Applicable: weight falls within tier range"

    # 2. Pattern: Over / Exceeding / Above / > MIN ton/tons/mt/kg
    m_over = re.search(
        r"(?:over|exceeding|above|>)\s*(\d+(?:\.\d+)?)\s*(ton|tons|mt|tonne|tonnes|kg)?",
        name_clean
    )
    if m_over:
        val = float(m_over.group(1))
        unit = (m_over.group(2) or "ton").lower()
        thresh_kg = val if unit == "kg" else val * 1000.0
        thresh_tons = thresh_kg / 1000.0

        is_gross = any(k in name_clean for k in ["gross", "vgm", "container weight"])
        eval_kg = gross_wt_kg if is_gross else cargo_wt_kg
        eval_tons = gross_wt_tons if is_gross else cargo_wt_tons

        if eval_kg <= thresh_kg:
            wt_type_str = f"Gross Weight ({eval_tons:.1f}T)" if is_gross else f"Cargo Weight ({eval_tons:.1f}T)"
            return False, f"Not applicable: {wt_type_str} does not exceed threshold of {thresh_tons:.1f}T"
        return True, "Applicable: weight exceeds threshold"

    # 3. Pattern: Up to / Under / Below / < MAX ton/tons/mt/kg
    m_under = re.search(
        r"(?:up\s+to|under|below|<)\s*(\d+(?:\.\d+)?)\s*(ton|tons|mt|tonne|tonnes|kg)?",
        name_clean
    )
    if m_under:
        val = float(m_under.group(1))
        unit = (m_under.group(2) or "ton").lower()
        thresh_kg = val if unit == "kg" else val * 1000.0
        thresh_tons = thresh_kg / 1000.0

        is_gross = any(k in name_clean for k in ["gross", "vgm", "container weight"])
        eval_kg = gross_wt_kg if is_gross else cargo_wt_kg
        eval_tons = gross_wt_tons if is_gross else cargo_wt_tons

        if eval_kg > thresh_kg:
            wt_type_str = f"Gross Weight ({eval_tons:.1f}T)" if is_gross else f"Cargo Weight ({eval_tons:.1f}T)"
            return False, f"Not applicable: {wt_type_str} exceeds maximum limit of {thresh_tons:.1f}T"
        return True, "Applicable: weight is below max limit"

    return True, "Standard charge"


def classify_charge(
    charge_name: str,
    amount: float,
    section_heading: str = None,
    weight_per_container_kg: Optional[float] = None,
    container_type: Optional[str] = None
) -> tuple[ChargeCategory, str]:
    """
    Classify a charge line item based on its name, amount, section heading, and weight parameters.

    Returns:
        tuple of (ChargeCategory, reason_string)
    """
    name_lower = charge_name.lower().strip()
    section = section_heading.strip().lower() if section_heading else ""

    # ── WEIGHT / VGM TIER APPLICABILITY CHECK ─────────────────
    is_app, app_reason = is_weight_surcharge_applicable(charge_name, weight_per_container_kg, container_type)
    if not is_app:
        return ChargeCategory.UNCERTAIN_EXCLUDED, app_reason

    # ── SPECIAL OVERRIDES ────────────────────────────────────
    name_clean = " ".join(name_lower.split())
    if "emergency surcharge" in name_clean:
        return ChargeCategory.FREIGHT_SURCHARGE_INCLUDED, "Forced Emergency Surcharge override to freight surcharge"
    if "premium cargo service" in name_clean:
        return ChargeCategory.FREIGHT_SURCHARGE_INCLUDED, "Forced Premium Cargo Service override to freight surcharge"
    if re.search(r"origin\s*landfreight\s*rail|landfreight\s*rail|emergency\s*fuel\s*origin\s*rail|fuel\s*origin\s*rail", name_clean):
        return ChargeCategory.FREIGHT_SURCHARGE_INCLUDED, "Forced Origin Rail surcharge override to freight surcharge included"
    if "panama canal" in name_clean or "canal surcharge" in name_clean or re.search(r"\bpcs\b", name_clean):
        return ChargeCategory.FREIGHT_SURCHARGE_INCLUDED, "Forced Panama Canal Surcharge override to freight surcharge included"
    if "arbitrary tariff at destination" in name_clean or "arbitrary" in name_clean and ("destination" in name_clean or "dest" in name_clean):
        return ChargeCategory.DESTINATION_CHARGE_EXCLUDED, "Destination arbitrary tariff charge excluded"
    if "arbitrary tariff at origin" in name_clean or "arbitrary" in name_clean and ("origin" in name_clean or "orig" in name_clean):
        return ChargeCategory.ORIGIN_CHARGE_EXCLUDED, "Origin arbitrary tariff charge excluded"

    # ── BASIC OCEAN FREIGHT ──────────────────────────────────
    basic_freight_keywords = [
        "basic ocean freight",
        "ocean freight",
        "base freight",
        "sea freight",
    ]
    for kw in basic_freight_keywords:
        if kw in name_lower:
            return ChargeCategory.BASIC_OCEAN_FREIGHT, f"Matched keyword: '{kw}'"

    # Generic "freight" keyword — but must be standalone, not part of surcharge names
    if name_lower == "freight" or name_lower.startswith("freight rate"):
        return ChargeCategory.BASIC_OCEAN_FREIGHT, "Matched generic freight keyword"

    # ── DISCOUNT / REBATE ────────────────────────────────────
    discount_keywords = ["discount", "rebate"]
    for kw in discount_keywords:
        if kw in name_lower:
            return ChargeCategory.DISCOUNT, f"Matched keyword: '{kw}'"

    # Negative adjustment
    if "adjustment" in name_lower and amount < 0:
        return ChargeCategory.DISCOUNT, "Negative adjustment treated as discount"

    # ── ORIGIN CHARGES (EXCLUDED) ────────────────────────────
    origin_keywords = [
        "origin thc",
        "orig thc",
        "origin terminal",
        "orig terminal",
        "terminal handling origin",
        "terminal handling orig",
        "terminal handling charge origin",
        "terminal handling charge orig",
        "origin handling",
        "orig handling",
        "export customs",
        "export documentation",
        "export fee",
        "pickup fee",
        "pickup charge",
        "pol thc",
        "origin local",
        "orig local",
        "loading charge",
        "origin haulage",
        "orig haulage",
        "terminal handling charge (l)",
    ]
    for kw in origin_keywords:
        if kw in name_lower:
            return ChargeCategory.ORIGIN_CHARGE_EXCLUDED, f"Origin charge matched: '{kw}'"

    # Broad origin pattern
    if ("origin" in name_lower or "orig" in name_lower or "pol" in name_lower or "export" in name_lower) and \
       any(x in name_lower for x in ["thc", "terminal", "handling", "local", "documentation", "customs", "fee", "truck", "landfreight", "haulage", "drayage", "seal", "sealing"]):
        return ChargeCategory.ORIGIN_CHARGE_EXCLUDED, "Broad origin charge pattern matched"

    # ── DESTINATION CHARGES (EXCLUDED) ───────────────────────
    destination_keywords = [
        "destination thc",
        "dest thc",
        "destination terminal",
        "dest terminal",
        "terminal handling destination",
        "terminal handling dest",
        "terminal handling charge destination",
        "terminal handling charge dest",
        "destination handling",
        "dest handling",
        "import customs",
        "import documentation",
        "import fee",
        "delivery fee",
        "delivery charge",
        "pod thc",
        "destination local",
        "dest local",
        "discharge charge",
        "discharging expenses",
        "destination haulage",
        "dest haulage",
        "terminal handling charge (d)",
        "empty reload",
        "equipment maintenance",
        "cargo release",
        "delivery order fee",
    ]
    for kw in destination_keywords:
        if kw in name_lower:
            return ChargeCategory.DESTINATION_CHARGE_EXCLUDED, f"Destination charge matched: '{kw}'"

    # Broad destination pattern
    if ("destination" in name_lower or "dest" in name_lower or "pod" in name_lower or "import" in name_lower) and \
       any(x in name_lower for x in ["thc", "terminal", "handling", "local", "documentation", "customs", "fee", "truck", "landfreight", "haulage", "drayage", "discharging", "reload", "release"]):
        return ChargeCategory.DESTINATION_CHARGE_EXCLUDED, "Broad destination charge pattern matched"

    # ── OTHER LOCAL CHARGES (EXCLUDED) ───────────────────────
    local_charge_keywords = [
        "documentation fee",
        "doc fee",
        "bl fee",
        "bill of lading",
        "customs fee",
        "customs clearance",
        "local handling",
        "container cleaning",
        "cleaning fee",
        "demurrage",
        "detention",
        "storage",
        "free time",
        "seal fee",
        "seal charge",
        "isps",
        "vgm",
        "ams",
        "ens",
        "document charge",
        "document fee",
        "documentation charge",
        "administration fee",
        "admin fee",
        "security charge",
        "maintenance fee",
        "maintenance charge",
        "equipment maintenance",
        "transfer charge",
        "equipment transfer",
        "manifest fee",
        "manifest charge",
    ]
    for kw in local_charge_keywords:
        matched = False
        if len(kw) <= 3:
            if re.search(rf"\b{re.escape(kw)}\b", name_lower):
                matched = True
        else:
            if kw in name_lower:
                matched = True

        if matched:
            # Classify as origin or destination based on context, default to origin
            if any(x in name_lower for x in ["destination", "dest", "pod", "import", "discharge"]):
                return ChargeCategory.DESTINATION_CHARGE_EXCLUDED, f"Local charge at destination: '{kw}'"
            return ChargeCategory.ORIGIN_CHARGE_EXCLUDED, f"Local charge excluded: '{kw}'"

    # ── FREIGHT SURCHARGES (INCLUDED) ────────────────────────
    freight_surcharge_keywords = [
        "bunker",
        "baf",
        "bunker adjustment",
        "fuel surcharge",
        "fuel adjustment",
        "emergency fuel",
        "efs",
        "low sulphur",
        "lss",
        "lsfs",
        "low sulfur",
        "environmental",
        "environment",
        "europe environment",
        "ees",
        "green",
        "carbon",
        "emission",
        "peak season",
        "pss",
        "war risk",
        "wrs",
        "piracy",
        "gulf of aden",
        "congestion surcharge",
        "currency adjustment",
        "caf",
        "gri",
        "general rate increase",
        "one bunker",
        "winter surcharge",
        "heavy weight surcharge",
        "overweight surcharge",
        "reefer surcharge",
        "imdg surcharge",
        "hazardous surcharge",
        "marine fuel",
        "marine fuel recovery",
        "mfr",
        "fuel recovery",
        "emission allowance",
        "emissions allowance",
        "panama canal surcharge",
        "panama canal",
        "pcs",
    ]
    for kw in freight_surcharge_keywords:
        matched = False
        if len(kw) <= 3:
            if re.search(rf"\b{re.escape(kw)}\b", name_lower):
                matched = True
        else:
            if kw in name_lower:
                matched = True

        if matched:
            if any(x in name_lower for x in ["destination", "dest ", "pod", "import", "discharge"]):
                return ChargeCategory.DESTINATION_CHARGE_EXCLUDED, f"Freight surcharge at destination excluded: '{kw}'"
            if any(x in name_lower for x in ["origin", "orig ", "pol", "export"]):
                return ChargeCategory.ORIGIN_CHARGE_EXCLUDED, f"Freight surcharge at origin excluded: '{kw}'"
            return ChargeCategory.FREIGHT_SURCHARGE_INCLUDED, f"Freight surcharge matched: '{kw}'"

    # ── OVERRIDE BY SECTION HEADING (FALLBACK) ────────────────
    if section:
        if "freight" in section:
            return ChargeCategory.BASIC_OCEAN_FREIGHT, f"Forced by section header: '{section_heading}'"
        elif "origin" in section or "export" in section:
            return ChargeCategory.ORIGIN_CHARGE_EXCLUDED, f"Forced by section header: '{section_heading}'"
        elif "destination" in section or "import" in section:
            return ChargeCategory.DESTINATION_CHARGE_EXCLUDED, f"Forced by section header: '{section_heading}'"

    # ── UNCERTAIN ────────────────────────────────────────────
    return ChargeCategory.UNCERTAIN_EXCLUDED, "Could not classify — excluded from final value as a precaution"
