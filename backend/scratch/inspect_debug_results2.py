import re

with open('scratch/debug_results.html', 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

# Look for USD mentions
usd_matches = re.findall(r'USD.{0,80}', html)
print(f'All USD mentions ({len(usd_matches)}):')
for m in usd_matches[:20]:
    print(f'  {repr(m)}')

# Look for class names containing sailings/schedule/card
all_classes = re.findall(r'class="([^"]+)"', html)
# flatten
flat = []
for c in all_classes:
    flat.extend(c.split())

from collections import Counter
class_counts = Counter(flat)
print(f'\nTop 40 CSS classes:')
for cls, count in class_counts.most_common(40):
    print(f'  {count:4d}x  {cls}')

# look for pricing-related text patterns
price_texts = re.findall(r'[\d,]+\s*(?:USD|usd|price|Price)', html)
print(f'\nPrice-like patterns: {price_texts[:20]}')

# Check what the HTML says around "book" URL patterns
book_idx = html.find('book/')
if book_idx > -1:
    print(f'\nContext around /book/ URL: ...{html[book_idx-100:book_idx+300]}...')
