import re
from collections import Counter

# Check a breakdown HTML for card classes
html_file = 'scratch/breakdown_html_0.html'
with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

all_classes = re.findall(r'class="([^"]+)"', html)
flat = []
for c in all_classes:
    flat.extend(c.split())

counts = Counter(flat)
print('Top 60 classes in breakdown_html_0.html:')
for cls, cnt in counts.most_common(60):
    print(f'  {cnt:4d}x  {cls}')

# Look for USD
usd = re.findall(r'USD.{0,60}', html)
print(f'\nUSD occurrences: {len(usd)}')
for u in usd[:10]:
    print(f'  {repr(u)}')

# Look for price-related class names
price_classes = [c for c in flat if any(k in c.lower() for k in ['price', 'amount', 'cost', 'rate', 'total', 'sail', 'schedule', 'card', 'offer'])]
price_counts = Counter(price_classes)
print('\nPrice/sail/card related classes:')
for cls, cnt in price_counts.most_common(30):
    print(f'  {cnt:4d}x  {cls}')
