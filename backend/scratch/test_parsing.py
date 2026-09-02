import os
import re
from datetime import datetime

html_path = "scratch/cma_results_page.html"
if not os.path.exists(html_path):
    html_path = "c:\\Users\\Brian\\Downloads\\Telegram Desktop\\Infreight_Sourcing_18526\\Infreight_Sourcing_New\\backend\\scratch\\cma_results_page.html"

with open(html_path, "r", encoding="utf-8") as f:
    html_content = f.read()

# Let's clean up script and style tags
html_content = re.sub(r'<script.*?>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
html_content = re.sub(r'<style.*?>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)

# Find all <article class="card-route-horizontal..."> elements
articles = []
start_idx = 0
while True:
    match = re.search(r'<article\b[^>]*>', html_content[start_idx:], re.IGNORECASE)
    if not match:
        break
    
    art_start = start_idx + match.start()
    # Find matching closing article tag
    art_end = html_content.find('</article>', art_start)
    if art_end == -1:
        break
    
    art_end += len('</article>')
    art_html = html_content[art_start:art_end]
    
    opening = match.group(0)
    if "card-route-horizontal" in opening:
        articles.append(art_html)
        
    start_idx = art_end

print(f"Extracted {len(articles)} card-route-horizontal articles.")

# Helper to simulate inner_text()
def get_inner_text(html):
    # Replace all tags with spaces
    text = re.sub(r'<[^>]+>', ' ', html)
    # Collapse multiple spaces into one
    text = " ".join(text.split())
    return text

for idx, art_html in enumerate(articles):
    text = get_inner_text(art_html)
    print(f"\n--- Article {idx} Text ---")
    print(text)
    
    # Run extraction regex
    # Pattern: Saturday, 23-May-2026 or 23-May-2026 or 3-May-2026
    # Let's support both: with and without weekday prefix
    date_pattern = r'(?:[A-Za-z]+,\s+)?\d{1,2}-[A-Za-z]+-\d{4}'
    found_dates = re.findall(date_pattern, text)
    etd_str = found_dates[0] if len(found_dates) > 0 else None
    eta_str = found_dates[1] if len(found_dates) > 1 else None
    
    print(f"  Found raw dates: ETD={etd_str}, ETA={eta_str}")
    
    etd = None
    if etd_str:
        try:
            # Check if it has the day name
            if "," in etd_str:
                etd = datetime.strptime(etd_str, "%A, %d-%b-%Y").date()
            else:
                etd = datetime.strptime(etd_str, "%d-%b-%Y").date()
        except Exception as e:
            print("  ETD parse fail:", e)
            
    eta = None
    if eta_str:
        try:
            if "," in eta_str:
                eta = datetime.strptime(eta_str, "%A, %d-%b-%Y").date()
            else:
                eta = datetime.strptime(eta_str, "%d-%b-%Y").date()
        except Exception as e:
            print("  ETA parse fail:", e)

    tt_match = re.search(r'(\d+)\s*[Dd]ays?', text)
    transit_time = int(tt_match.group(1)) if tt_match else None
    
    if etd and eta and transit_time is None:
        transit_time = (eta - etd).days

    service_match = re.search(r'First Service\s+(\S+)', text)
    service = service_match.group(1).strip() if service_match else None
    
    vessel_match = re.search(r'Vessel\s+(.+?)\s+CO2', text)
    vessel = vessel_match.group(1).strip() if vessel_match else None

    price_match = re.search(r'(\d[\d,]*)\s*USD', text)
    total_price = float(price_match.group(1).replace(",", "")) if price_match else 0.0

    print("  Parsed values:")
    print(f"    ETD: {etd}")
    print(f"    ETA: {eta}")
    print(f"    Transit Time (days): {transit_time}")
    print(f"    Service: {service}")
    print(f"    Vessel: {vessel}")
    print(f"    Total Price: {total_price}")
