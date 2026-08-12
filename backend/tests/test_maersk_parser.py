import re
import pytest
from carriers.maersk_connector import MIN_PLAUSIBLE_OCEAN_RATE


def test_maersk_rollable_badge_price_filtering():
    card_text = """Maersk Spot Rollable
Get USD 15 per container if rolled
Cargo may be rolled
USD 1,662.00
Incl. 7 days of detention freetime"""

    safe_text = "\n".join(
        ln for ln in card_text.splitlines()
        if "if rolled" not in ln.lower() and "may be rolled" not in ln.lower()
    )
    
    price = 0.0
    for v in re.findall(r"(?:USD|\$)\s*([\d,]+\.?\d{0,2})", safe_text, re.IGNORECASE):
        candidate = float(v.replace(",", ""))
        if candidate >= MIN_PLAUSIBLE_OCEAN_RATE:
            price = candidate
            break

    assert price == 1662.0


def test_maersk_multiline_basis_accessibility_parsing():
    lines = [
        "freight charges",
        "Basic Ocean Freight",
        "Container",
        "20 Dry Standard",
        "1",
        "USD",
        "253",
        "253",
        "Basic Ocean Freight",
        "Container",
        "40 Dry Standard",
        "1",
        "USD",
        "586",
        "586",
        "Emergency Bunker Surcharge",
        "Container",
        "20 Dry Standard",
        "1",
        "USD",
        "50",
        "50",
    ]

    amount_pattern = re.compile(r"^(\d[\d,]*\.?\d*)$")
    currency_pattern = re.compile(r"^(USD|SGD|EUR|INR|GBP|AUD|CNY|JPY|HKD|MYR)$")

    charges = []
    current_section = "freight charges"
    i = 0
    row_start = 0

    while i < len(lines):
        line = lines[i]
        line_lower = line.lower()

        if "freight charges" in line_lower:
            current_section = "freight charges"
            i += 1
            row_start = i
            continue
        elif line_lower in ("basis", "quantity", "currency", "unit price", "total price"):
            i += 1
            row_start = i
            continue

        if (currency_pattern.match(line)
                and i - 1 >= row_start
                and i + 2 < len(lines)
                and amount_pattern.match(lines[i - 1])
                and amount_pattern.match(lines[i + 1])
                and amount_pattern.match(lines[i + 2])):

            head = lines[row_start:i - 1]
            if head:
                name_candidate = head[0]
                basis = " ".join(head[1:]).strip()
                amount = float(lines[i + 2].replace(",", ""))
                charges.append({
                    "name": name_candidate,
                    "basis": basis,
                    "amount": amount,
                    "currency": line,
                })
            i += 3
            row_start = i
            continue

        i += 1

    assert len(charges) == 3
    assert charges[0]["name"] == "Basic Ocean Freight"
    assert charges[0]["basis"] == "Container 20 Dry Standard"
    assert charges[0]["amount"] == 253.0

    assert charges[1]["name"] == "Basic Ocean Freight"
    assert charges[1]["basis"] == "Container 40 Dry Standard"
    assert charges[1]["amount"] == 586.0

    assert charges[2]["name"] == "Emergency Bunker Surcharge"
    assert charges[2]["basis"] == "Container 20 Dry Standard"
    assert charges[2]["amount"] == 50.0
