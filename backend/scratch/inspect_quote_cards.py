import os
from bs4 import BeautifulSoup

def main():
    html_path = "scratch/oocl_fs_results.html"
    if not os.path.exists(html_path):
        print(f"File {html_path} not found.")
        return
        
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()
        
    soup = BeautifulSoup(html, "html.parser")
    
    # Let's search for classes in the DOM that look like cards
    print("--- Searching for card-like elements ---")
    card_selectors = [
        '.quote-card', '.quoteItem', '.product', '[class*="quote-card" i]', 
        '[class*="quoteItem" i]', '[class*="product" i]', '[class*="card" i]'
    ]
    
    for sel in card_selectors:
        elements = soup.select(sel)
        print(f"Selector '{sel}' found {len(elements)} elements.")
        
    # Let's inspect all elements containing "3,718" or "3,733" or "3,748"
    print("\n--- Searching for elements containing specific prices ---")
    for price in ["3,718", "3,733", "3,748"]:
        elements = soup.find_all(lambda tag: tag.name == 'div' and price in tag.text)
        print(f"Found {len(elements)} div tags containing price '{price}':")
        # Print the most specific one (deepest in tree)
        deepest = None
        for el in elements:
            if deepest is None or len(str(el)) < len(str(deepest)):
                deepest = el
        if deepest:
            print(f"Deepest tag: {deepest.name}, Class: '{deepest.get('class')}'")
            print(f"Text content: '{deepest.text.strip()}'")
            print(f"HTML: {str(deepest)[:300]}...\n")

if __name__ == "__main__":
    main()
