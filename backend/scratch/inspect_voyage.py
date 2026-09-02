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

# Let's search for "voyage" or "voy" case-insensitively
print("--- Searching for voyage/voy ---")
for m in re.finditer(re.escape("voyage"), html_content, re.IGNORECASE):
    start = max(0, m.start() - 100)
    end = min(len(html_content), m.end() + 100)
    print("Match Voyage:", " ".join(html_content[start:end].split()))

for m in re.finditer(re.escape("voy"), html_content, re.IGNORECASE):
    start = max(0, m.start() - 50)
    end = min(len(html_content), m.end() + 50)
    print("Match Voy:", " ".join(html_content[start:end].split()))
