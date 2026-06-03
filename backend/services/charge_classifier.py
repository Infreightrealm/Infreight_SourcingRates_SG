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
from models.schemas import ChargeCategory


def classify_charge(charge_name: str, amount: float, section_heading: str = None) -> tuple[ChargeCategory, str]:
    """
    Classify a charge line item based on its name, amount, and the section heading it falls under.

    Returns:
        tuple of (ChargeCategory, reason_string)
    """
    name_lower = charge_name.lower().strip()
    section = section_heading.strip().lower() if section_heading else ""

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
       any(x in name_lower for x in ["thc", "terminal", "handling", "local", "documentation", "customs", "fee"]):
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
        "destination haulage",
        "dest haulage",
        "terminal handling charge (d)",
    ]
    for kw in destination_keywords:
        if kw in name_lower:
            return ChargeCategory.DESTINATION_CHARGE_EXCLUDED, f"Destination charge matched: '{kw}'"

    # Broad destination pattern
    if ("destination" in name_lower or "dest" in name_lower or "pod" in name_lower or "import" in name_lower) and \
       any(x in name_lower for x in ["thc", "terminal", "handling", "local", "documentation", "customs", "fee"]):
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
        "panama canal",
        "suez canal",
        "canal surcharge",
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
