import re

text = """Equipment type: 40DV Est. Transit Time: 32 Days
Shipment Terms: Port to Port Service: LION Please submit
your booking latest by the 11 Jun 2026 (23:59:59 UTC
time) to benefit from the rate offered above. This rate is
only valid for shipments between 09 Jun 2026 and 14 Jun
2026. For shipments from/to the United States of
America, the rates, charges, and rules applicable to any
given shipment shall be those in effect on the date the
cargo is received by MSC or MSC agent, including
originating carriers in the case of rates for through
transportation. Selected Charges Quote Conditions
Schedule Free Time Charges Charge Charge Level
Amount Supported Payments Comments & Conditions
Freight Charge Sea Freight (FRT) Per Equipment 4220
USD Prepaid, Collect, Elsewhere Freight Surcharges
Emission control areas [ECA] Per Equipment 30 USD
Prepaid, Collect, Elsewhere Global fuel surcharge [GFS]
Per Equipment 450 USD Prepaid, Collect, Elsewhere
Carbon review surcharge [CRS] Per Equipment 156 USD
Prepaid, Collect, Elsewhere Export Surcharges Terminal
handling charge [THC] Per Equipment 370 SGD Prepaid,
Collect, Elsewhere Documentation fee [DOC] Per Bill of
lading 280 SGD Prepaid, Collect, Elsewhere Seal fee [SEL]
Per Equipment 26 SGD Prepaid, Collect, Elsewhere Import
Surcharges Isps - intern. ship and port security charge
(pod) [SPD] Per Equipment 17 EUR Prepaid, Collect,
Elsewhere Terminal handling charge [THC] Per Equipment
260 EUR Prepaid, Collect, Elsewhere Delivery order fee
[DOF] Per Bill of lading 50 EUR Prepaid, Collect,
Elsewhere Customs inspections [CUI] Per Equipment 31
EUR Prepaid, Collect, Elsewhere Container compliance
charge [CCC] Per Equipment 20 EUR Prepaid, Collect,
Elsewhere Fuel energy transition charge [FEC] Per
Equipment 90 EUR Collect Collect terms of payment only.
Cargo data declaration [CDD] Per Bill of lading 25 USD
Prepaid, Collect, Elsewhere Must follow same terms of
Payment as Freight. Total 5,945 USD Subject to charges
calculated on percentage of cargo value which will be
calculated and added at Booking/SI stage. “Per Bill of
Lading” charges will be considered only once per BL.
Additional local and contingency charges may apply."""

# Replace newlines with spaces to simulate innerText of a grid
text = text.replace('\n', ' ')

def extract_section(text, current_header, next_headers):
    start = text.find(current_header)
    if start == -1: return ""
    end_indices = [text.find(h) for h in next_headers if text.find(h) > start]
    end = min(end_indices) if end_indices else len(text)
    return text[start:end]

sections = {
    "Freight Charge": ["Freight Surcharges", "Export Surcharges", "Import Surcharges"],
    "Freight Surcharges": ["Export Surcharges", "Import Surcharges"],
    "Export Surcharges": ["Import Surcharges"],
    "Import Surcharges": ["Total"]
}

for section_name, next_headers in sections.items():
    section_text = extract_section(text, section_name, next_headers)
    print(f"--- {section_name} ---")
    
    # regex to find charges
    pattern = r"(.*?)(?:Per Equipment|Per Bill of lading)\s+([\d,]+(?:\.\d+)?)\s*([A-Z]{3})\s+(?:Prepaid|Collect)"
    
    for match in re.finditer(pattern, section_text):
        raw_name = match.group(1).strip()
        
        # Clean up garbage from previous charge
        clean_name = re.sub(r"^(?:,\s*Elsewhere|,\s*Collect|,\s*Prepaid|Collect|Prepaid)+", "", raw_name).strip()
        clean_name = re.sub(r"^(?:Freight Charge|Freight Surcharges|Export Surcharges|Import Surcharges)", "", clean_name).strip()
        clean_name = clean_name.strip(" ,.")
        
        amount = float(match.group(2).replace(",", ""))
        currency = match.group(3)
        
        print(f"Name: {clean_name}")
        print(f"Amount: {amount} {currency}")
        print()
