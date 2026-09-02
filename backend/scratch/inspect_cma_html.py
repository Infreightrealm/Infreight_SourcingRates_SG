import os
import re

html_path = "scratch/cma_results_page.html"
if not os.path.exists(html_path):
    html_path = "c:\\Users\\Brian\\Downloads\\Telegram Desktop\\Infreight_Sourcing_18526\\Infreight_Sourcing_New\\backend\\scratch\\cma_results_page.html"

with open(html_path, "r", encoding="utf-8") as f:
    html_content = f.read()

# Let's search for "Details" (case-sensitive or insensitive) and print its matches with their surrounding HTML tags.
print("--- Searching for 'Details' elements ---")
matches = list(re.finditer(r'Details', html_content))
print(f"Found {len(matches)} occurrences of 'Details'")

for idx, m in enumerate(matches):
    start = max(0, m.start() - 150)
    end = min(len(html_content), m.end() + 150)
    context = html_content[start:end]
    print(f"\nMatch {idx} at position {m.start()}:")
    print("--- CONTEXT ---")
    print(context)
    print("---------------")
