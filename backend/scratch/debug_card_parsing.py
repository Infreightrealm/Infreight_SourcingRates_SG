import os
import sys
from bs4 import BeautifulSoup

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)

from carriers.oocl_connector import OOCLConnector

def main():
    html_path = "scratch/oocl_fs_results.html"
    if not os.path.exists(html_path):
        print(f"File {html_path} not found.")
        return
        
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()
        
    soup = BeautifulSoup(html, "html.parser")
    elements = soup.select('[class*="product" i]')
    print(f"Found {len(elements)} product elements.")
    
    connector = OOCLConnector()
    
    for idx, el in enumerate(elements):
        # In BeautifulSoup, we can get text content similar to inner_text
        # We replace multiple spaces/newlines with single ones
        text = " ".join(el.get_text().split())
        print(f"\n--- Element [{idx}] (Class='{el.get('class')}') ---")
        print(f"Text content: '{text}'")
        
        parsed = connector._fs_parse_card(el.get_text())
        print(f"Parsed result: {parsed}")

if __name__ == "__main__":
    main()
