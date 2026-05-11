"""
Normalizer — calculates the final freight value and normalizes quote data.

Final Freight Value =
    Basic Ocean Freight
    + Discount (already negative, or normalized to negative if positive)
    + Freight-related surcharges (included)

Excludes: Origin charges, destination charges, uncertain charges.
"""
from models.schemas import ChargeCategory, ChargeSchema, QuoteSchema
from services.charge_classifier import classify_charge


def calculate_final_freight_value(charges: list[dict]) -> float:
    """
    Calculate the final freight value from a list of classified charges.

    Args:
        charges: list of dicts with keys: name, amount, currency, category

    Returns:
        Final freight value as float
    """
    final = 0.0

    for charge in charges:
        category = charge.get("category", ChargeCategory.UNCERTAIN_EXCLUDED)
        amount = float(charge.get("amount", 0.0))

        if category == ChargeCategory.BASIC_OCEAN_FREIGHT:
            final += amount

        elif category == ChargeCategory.DISCOUNT:
            # Ensure discount is negative (reduces the total)
            if amount > 0:
                final -= amount  # Normalize positive discount to negative effect
            else:
                final += amount  # Already negative, just add

        elif category == ChargeCategory.FREIGHT_SURCHARGE_INCLUDED:
            final += amount

        # All other categories (ORIGIN_CHARGE_EXCLUDED, DESTINATION_CHARGE_EXCLUDED,
        # UNCERTAIN_EXCLUDED) are excluded from the final value

    return round(final, 2)


def classify_and_organize_charges(raw_charges: list[dict]) -> dict:
    """
    Takes raw charge line items and classifies them.

    Args:
        raw_charges: list of dicts with keys: name, amount, currency

    Returns:
        dict with keys:
            basic_ocean_freight (float),
            discount (float),
            included_freight_surcharges (list[ChargeSchema]),
            excluded_charges (list[ChargeSchema]),
            uncertain_charges (list[ChargeSchema]),
            all_classified (list[dict])  — full list with categories for DB storage
    """
    basic_ocean_freight = 0.0
    discount = 0.0
    included_surcharges = []
    excluded_charges = []
    uncertain_charges = []
    all_classified = []

    for raw in raw_charges:
        name = raw.get("name", "Unknown Charge")
        amount = float(raw.get("amount", 0.0))
        currency = raw.get("currency", "USD")

        category, reason = classify_charge(name, amount)

        classified = {
            "name": name,
            "amount": amount,
            "currency": currency,
            "category": category.value,
            "reason": reason,
            "included_in_final_value": category in [
                ChargeCategory.BASIC_OCEAN_FREIGHT,
                ChargeCategory.DISCOUNT,
                ChargeCategory.FREIGHT_SURCHARGE_INCLUDED,
            ],
        }
        all_classified.append(classified)

        charge_schema = ChargeSchema(
            name=name,
            amount=amount,
            currency=currency,
            category=category.value,
            reason=reason,
        )

        if category == ChargeCategory.BASIC_OCEAN_FREIGHT:
            basic_ocean_freight += amount

        elif category == ChargeCategory.DISCOUNT:
            if amount > 0:
                discount -= amount  # Normalize to negative
            else:
                discount += amount

        elif category == ChargeCategory.FREIGHT_SURCHARGE_INCLUDED:
            included_surcharges.append(charge_schema)

        elif category in [ChargeCategory.ORIGIN_CHARGE_EXCLUDED, ChargeCategory.DESTINATION_CHARGE_EXCLUDED]:
            excluded_charges.append(charge_schema)

        elif category == ChargeCategory.UNCERTAIN_EXCLUDED:
            uncertain_charges.append(charge_schema)

    return {
        "basic_ocean_freight": round(basic_ocean_freight, 2),
        "discount": round(discount, 2),
        "included_freight_surcharges": included_surcharges,
        "excluded_charges": excluded_charges,
        "uncertain_charges": uncertain_charges,
        "all_classified": all_classified,
    }


def normalize_quote(
    carrier: str,
    raw_quote: dict,
    raw_charges: list[dict],
) -> QuoteSchema:
    """
    Normalize a raw quote from a carrier connector into a QuoteSchema.

    Args:
        carrier: Carrier code
        raw_quote: Dict with keys like etd, eta, transit_time_days, service_name, vessel, etc.
        raw_charges: List of raw charge dicts with name, amount, currency

    Returns:
        QuoteSchema with calculated final_freight_value
    """
    organized = classify_and_organize_charges(raw_charges)

    final_value = calculate_final_freight_value(organized["all_classified"])

    return QuoteSchema(
        etd=raw_quote.get("etd"),
        eta=raw_quote.get("eta"),
        transit_time_days=raw_quote.get("transit_time_days"),
        service_name=raw_quote.get("service_name"),
        vessel=raw_quote.get("vessel"),
        container_type=raw_quote.get("container_type"),
        container_quantity=raw_quote.get("container_quantity"),
        currency=raw_quote.get("currency", "USD"),
        basic_ocean_freight=organized["basic_ocean_freight"],
        discount=organized["discount"],
        included_freight_surcharges=organized["included_freight_surcharges"],
        excluded_charges=organized["excluded_charges"],
        uncertain_charges=organized["uncertain_charges"],
        final_freight_value=final_value,
        source="mock" if raw_quote.get("source") == "mock" else "carrier_portal",
        raw_reference=raw_quote.get("raw_reference"),
    )
