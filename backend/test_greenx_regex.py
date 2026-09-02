import re

sample_text = """
Prepaid Charges at Origin
Collect Charges at Destinations
Charge Items	Container Type	Quantity	Price
Basic Ocean Freight	20' Standard Dry	x 1	USD 3,142.00
Basic Ocean Freight	40' Standard Dry	x 1	USD 4,784.00
Basic Ocean Freight	40' High Cube	x 1	USD 4,784.00
EU INNOVATION SURCHARGE (EUIS)	20' Standard Dry	x 1	
USD 85.31
(EUR 75.00)

IMO SOX COMPLIANCE CHARGE (ISOCC)	20' Standard Dry	x 1	
USD 88.00

LOW SULPHUR SURCHARGE (LSS)	20' Standard Dry	x 1	
USD 20.00

TERMINAL HANDLING CHARGE AT PORT OF LOADING (THC/L)	20' Standard Dry	x 1	
USD 185.76
(SGD 240.00)

EU INNOVATION SURCHARGE (EUIS)	40' Standard Dry	x 1	
USD 170.62
(EUR 150.00)

IMO SOX COMPLIANCE CHARGE (ISOCC)	40' Standard Dry	x 1	
USD 176.00

LOW SULPHUR SURCHARGE (LSS)	40' Standard Dry	x 1	
USD 40.00

TERMINAL HANDLING CHARGE AT PORT OF LOADING (THC/L)	40' Standard Dry	x 1	
USD 270.90
(SGD 350.00)

EU INNOVATION SURCHARGE (EUIS)	40' High Cube	x 1	
USD 170.62
(EUR 150.00)

IMO SOX COMPLIANCE CHARGE (ISOCC)	40' High Cube	x 1	
USD 176.00

LOW SULPHUR SURCHARGE (LSS)	40' High Cube	x 1	
USD 40.00

TERMINAL HANDLING CHARGE AT PORT OF LOADING (THC/L)	40' High Cube	x 1	
USD 270.90
(SGD 350.00)

EU ENTRY SUMMARY DECLARATION CHARGE (ENS)	Per B/L	x 1	
USD 30.00

E BOOKING FEE VIA GREENX (EBKF)	Per B/L	x 1	
USD 10.00

	Total	USD 14,444.11
"""

# Test regex matching across newlines
pattern = r"(.+?)\t+(20'\s*Standard\s*Dry|40'\s*Standard\s*Dry|40'\s*High\s*Cube|Per\s*B/L|20'\s*SD|40'\s*SD|40'\s*SH)\t+x\s*\d+[\s\S]*?USD\s*([\d,]+\.\d{2})"
matches = re.findall(pattern, sample_text)
print(f"Matches count: {len(matches)}")
for m in matches:
    name = m[0].strip()
    name = re.sub(r'^\s*\d+\s+', '', name)
    ct = m[1].strip()
    price = float(m[2].replace(",", ""))
    print(f"  Charge: {name} | Type: {ct} | Amount: USD {price}")
