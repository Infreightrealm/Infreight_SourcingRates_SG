import re

with open('scratch/breakdown_html_0.html', 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

# Find the new-sailings-card-article sections
card_starts = [m.start() for m in re.finditer(r'new-sailings-card-article', html)]
print(f'Found {len(card_starts)} new-sailings-card-article occurrences')

for i, start in enumerate(card_starts[:3]):
    # Get context around it
    chunk = html[start-100:start+2000]
    print(f'\n--- Card occurrence {i} ---')
    print(chunk[:1500])
    print('...')
