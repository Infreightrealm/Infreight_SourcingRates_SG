import re

with open('scratch/debug_results.html', 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

# Find all new-sailings-card-article sections
card_regions = []
pattern = re.compile(r'<article class="new-sailings-card-article"[^>]*>(.*?)(?=<article class="new-sailings-card-article"|$)', re.DOTALL)
for m in pattern.finditer(html):
    card_regions.append(m.group(0))

print(f'Found {len(card_regions)} article.new-sailings-card-article regions')

for i, region in enumerate(card_regions):
    usd_prices = re.findall(r'USD[\s]*[\d,]+\.?\d*', region)
    dates = re.findall(r'datetime="([^"]+)"', region)
    data_tests = re.findall(r'data-test="([^"]+)"', region)
    product_offer = re.findall(r'class="product-offer[^"]*"', region)
    
    print(f'\n=== Card {i} ===')
    print(f'  USD prices: {usd_prices}')
    print(f'  Datetime attrs: {dates[:5]}')
    print(f'  data-test attrs: {data_tests[:15]}')
    print(f'  product-offer classes: {product_offer[:5]}')
    
    # Check if Rollable
    if 'rollable' in region.lower():
        rollable_ctx = re.findall(r'.{0,30}[Rr]ollable.{0,30}', region)
        print(f'  Rollable mentions: {rollable_ctx[:3]}')
