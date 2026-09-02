import os
import re

html_path = "scratch/cma_breakdown_page.html"
if not os.path.exists(html_path):
    html_path = "c:\\Users\\Brian\\Downloads\\Telegram Desktop\\Infreight_Sourcing_18526\\Infreight_Sourcing_New\\backend\\scratch\\cma_breakdown_page.html"

with open(html_path, "r", encoding="utf-8") as f:
    html_content = f.read()

# Clean up script/style
html_content = re.sub(r'<script.*?>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
html_content = re.sub(r'<style.*?>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)

# Let's extract the first <article class="card-route-horizontal ..."> in this breakdown page
start_idx = html_content.find('class="card-route-horizontal')
if start_idx != -1:
    art_start = html_content.rfind('<article', 0, start_idx)
    art_end = html_content.find('</article>', art_start)
    art_html = html_content[art_start:art_end+len('</article>')]
    
    # Simulate inner_text()
    def get_inner_text(html):
        text = re.sub(r'<[^>]+>', ' ', html)
        text = " ".join(text.split())
        return text
    
    text = get_inner_text(art_html)
    print("--- CARD INNER TEXT (WITH DETAILS OPEN) ---")
    print(text)
    
    # Let's search for voyage reference
    voyage_match = re.search(r'Voyage\s+Ref\b.*?(\b[A-Z0-9]+)', text, re.IGNORECASE)
    if voyage_match:
        print("\n[SUCCESS] Found Voyage Ref:", voyage_match.group(1))
    else:
        print("\n[FAIL] Voyage Ref not found with regex.")
        # Try a different regex
        v_match = re.search(r'Voyage\s+Ref\.\s*(\S+)', text, re.IGNORECASE)
        if v_match:
            print("Alternative regex found:", v_match.group(1))
else:
    print("Article class not found on breakdown page.")
