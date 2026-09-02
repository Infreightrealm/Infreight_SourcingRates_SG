import os
import re
import glob

files = glob.glob("c:\\Users\\Brian\\Downloads\\Telegram Desktop\\Infreight_Sourcing_18526\\Infreight_Sourcing_New\\backend\\scratch\\breakdown_html_*.html")

for fpath in files:
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Strip scripts/styles
    content_clean = re.sub(r'<script.*?>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
    content_clean = re.sub(r'<style.*?>.*?</style>', '', content_clean, flags=re.DOTALL | re.IGNORECASE)
    
    # Check carrier indicators
    is_maersk = "maersk" in content.lower() or "mds-headline" in content.lower() or "mc-checkbox" in content.lower()
    is_cma = "cma cgm" in content.lower() or "card-route-horizontal" in content_clean.lower() or "o-button" in content_clean.lower()
    
    print(f"File: {os.path.basename(fpath)} (size: {len(content)} bytes) | Maersk Indicator: {is_maersk} | CMA Indicator: {is_cma}")
    
    # Let's search for "Ocean Freight" or "USD" in this file
    usd_matches = re.findall(r'(\d[\d,]*\s*USD|USD\s*\d[\d,]*)', content_clean)
    ocean_freight_matches = re.findall(r'(Ocean Freight|Charges payable as per freight|Charges payable at import)', content_clean, re.IGNORECASE)
    
    print(f"  USD matches: {len(usd_matches)} | Ocean Freight/Charges matches: {len(ocean_freight_matches)}")
    if ocean_freight_matches:
        print(f"  First 3 Ocean Freight/Charges matches: {ocean_freight_matches[:3]}")
    if usd_matches:
        print(f"  First 5 USD matches: {usd_matches[:5]}")
