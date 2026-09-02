import os
import re

fpath = "scratch/debug_results.html"
if not os.path.exists(fpath):
    fpath = "c:\\Users\\Brian\\Downloads\\Telegram Desktop\\Infreight_Sourcing_18526\\Infreight_Sourcing_New\\backend\\scratch\\debug_results.html"

if os.path.exists(fpath):
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Strip scripts/styles
    content_clean = re.sub(r'<script.*?>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
    content_clean = re.sub(r'<style.*?>.*?</style>', '', content_clean, flags=re.DOTALL | re.IGNORECASE)
    
    is_maersk = "maersk" in content.lower() or "mds-headline" in content.lower()
    is_cma = "cma cgm" in content.lower() or "card-route-horizontal" in content_clean.lower()
    
    print(f"File: {os.path.basename(fpath)} | size={len(content)} | Maersk={is_maersk} | CMA={is_cma}")
else:
    print("debug_results.html does not exist.")
