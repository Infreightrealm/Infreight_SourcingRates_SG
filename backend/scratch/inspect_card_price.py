import re

with open('scratch/breakdown_html_0.html', 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

# Find USD amounts in context
usd_sections = []
for m in re.finditer(r'USD\s*[\d,]+\.\d+', html):
    start = max(0, m.start() - 500)
    end = min(len(html), m.end() + 200)
    usd_sections.append((m.group(), html[start:end]))

for amount, context in usd_sections:
    print(f'\n=== Amount: {amount} ===')
    # Just show class names and relevant tags around it
    print(context[:800])
    print()

# Also find departure date patterns
depart = re.findall(r'datetime="(\d{4}-\d{2}-\d{2})"', html)
print(f'\nDatetime attributes: {depart[:10]}')

# Find duration hours
durations = re.findall(r'durationinhours="(\d+)"', html)
print(f'Duration hours: {durations}')

# Find vessel names
vessel = re.findall(r'data-test="vessel[^"]*"[^>]*>([^<]+)', html)
print(f'Vessel names: {vessel}')
