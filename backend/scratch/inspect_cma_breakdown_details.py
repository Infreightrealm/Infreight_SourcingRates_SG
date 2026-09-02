import os
import re

html_path = "scratch/cma_breakdown_page.html"
if not os.path.exists(html_path):
    html_path = "c:\\Users\\Brian\\Downloads\\Telegram Desktop\\Infreight_Sourcing_18526\\Infreight_Sourcing_New\\backend\\scratch\\cma_breakdown_page.html"

with open(html_path, "r", encoding="utf-8") as f:
    html_content = f.read()

# Let's clean up script and style tags
html_content = re.sub(r'<script.*?>.*?</script>', '', html_content, flags=re.DOTALL | re.IGNORECASE)
html_content = re.sub(r'<style.*?>.*?</style>', '', html_content, flags=re.DOTALL | re.IGNORECASE)

# Print occurrences of 'export' and 'origin' with 100 characters of context
print("--- Context for 'export' ---")
for m in re.finditer(re.escape("export"), html_content, re.IGNORECASE):
    start = max(0, m.start() - 100)
    end = min(len(html_content), m.end() + 100)
    print("Match:", " ".join(html_content[start:end].split()))

print("\n--- Context for 'origin' ---")
for m in re.finditer(re.escape("origin"), html_content, re.IGNORECASE):
    start = max(0, m.start() - 100)
    end = min(len(html_content), m.end() + 100)
    print("Match:", " ".join(html_content[start:end].split()))
