import re

sample_msc_popup = """
FREIGHT CHARGE
Sea Freight (FRT) Per Equipment 2834 USD Prepaid, Collect, Elsewhere

FREIGHT SURCHARGES
Emission control areas [ECA] Per Equipment 15 USD Prepaid, Collect, Elsewhere
Global fuel surcharge [GFS] Per Equipment 271 USD Prepaid, Collect, Elsewhere
Carbon review surcharge [CRS] Per Equipment 81 USD Prepaid, Collect, Elsewhere

EXPORT SURCHARGES
Terminal handling charge [THC] Per Equipment 245 SGD Prepaid, Collect, Elsewhere
Documentation fee [DOC] Per Bill of lading 280 SGD Prepaid, Collect, Elsewhere
Seal fee [SEL] Per Equipment 28 SGD Prepaid, Collect, Elsewhere

IMPORT SURCHARGES
Isps - intern. ship and port security charge (pod) [SPD] Per Equipment 17 EUR Prepaid, Collect, Elsewhere
Delivery order fee [DOF] Per Bill of lading 55 EUR Prepaid, Collect, Elsewhere
Customs inspections [CUI] Per Equipment 31 EUR Prepaid, Collect, Elsewhere
Container compliance charge [CCC] Per Equipment 20 EUR Prepaid, Collect, Elsewhere
Fuel energy transition charge [FEC] Per Equipment 50 EUR Collect Collect terms of payment only.
Cargo data declaration [CDD] Per Bill of lading 25 USD Prepaid, Collect, Elsewhere Must follow same terms of Payment as Freight.
Terminal handling charge [THC] Per Equipment 260 EUR Prepaid, Collect, Elsewhere
""".replace('\n', ' ').upper()

def extract_section(txt, current_header, next_headers):
    start = txt.find(current_header)
    if start == -1: return ""
    end_indices = [txt.find(h) for h in next_headers if txt.find(h) > start]
    end = min(end_indices) if end_indices else len(txt)
    return txt[start:end]

sections = {
    "FREIGHT CHARGE": ["FREIGHT SURCHARGES", "EXPORT SURCHARGES", "IMPORT SURCHARGES"],
    "FREIGHT SURCHARGES": ["EXPORT SURCHARGES", "IMPORT SURCHARGES"],
    "EXPORT SURCHARGES": ["IMPORT SURCHARGES"],
    "IMPORT SURCHARGES": ["TOTAL", "SUBJECT TO CHARGES"]
}

extracted_charges = []
for section_name, next_headers in sections.items():
    section_text = extract_section(sample_msc_popup, section_name, next_headers)
    if not section_text: continue
    
    pattern = r"(.*?)(?:PER EQUIPMENT|PER BILL OF LADING)\s+([\d,]+(?:\.\d+)?)\s*([A-Z]{3})\s+(?:PREPAID|COLLECT)"
    
    for match in re.finditer(pattern, section_text, re.DOTALL):
        raw_name = match.group(1).strip()
        
        # Clean leading noise and trailing comments from previous row
        clean_name = re.sub(r"^(?:,\s*ELSEWHERE|,\s*COLLECT|,\s*PREPAID|COLLECT|PREPAID)+", "", raw_name).strip()
        clean_name = re.sub(r"^(?:FREIGHT CHARGE|FREIGHT SURCHARGES|EXPORT SURCHARGES|IMPORT SURCHARGES)", "", clean_name).strip()
        clean_name = re.sub(r"^(?:MUST FOLLOW SAME TERMS OF PAYMENT AS FREIGHT\.?|COLLECT TERMS OF PAYMENT ONLY\.?|TERMS OF PAYMENT ONLY\.?|ELSEWHERE\.?)", "", clean_name).strip(" ,.")
        clean_name = re.sub(r".*?(MUST FOLLOW SAME TERMS OF PAYMENT AS FREIGHT\.?|COLLECT TERMS OF PAYMENT ONLY\.?|TERMS OF PAYMENT ONLY\.?)\s*", "", clean_name).strip(" ,.")
        
        if not clean_name: continue
        
        val = float(match.group(2).replace(",", ""))
        curr = match.group(3)
        
        formatted_name = clean_name.title()
        # Preserve uppercase inside brackets like [CDD], [THC], [ECA]
        formatted_name = re.sub(r'\[([a-zA-Z0-9]+)\]', lambda m: f'[{m.group(1).upper()}]', formatted_name)
        
        extracted_charges.append((section_name, formatted_name, val, curr))

print(f"Total charges extracted: {len(extracted_charges)}")
for ch in extracted_charges:
    print(ch)
