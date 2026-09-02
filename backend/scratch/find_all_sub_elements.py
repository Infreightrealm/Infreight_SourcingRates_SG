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
    
    container = soup.select_one('[class*="product-card-container" i]')
    if not container:
        print("No product-card-container found.")
        return
        
    print("--- Child tag names and classes of product-card-container ---")
    for idx, child in enumerate(container.children):
        # Filter out empty text nodes
        if child.name is None:
            continue
        print(f"Child [{idx}] Tag: {child.name}, Class: '{child.get('class')}', Text length: {len(child.text)}")
        # Check sub-children
        for sub_idx, sub_child in enumerate(child.children):
            if sub_child.name is None:
                continue
            print(f"  Sub-child [{sub_idx}] Tag: {sub_child.name}, Class: '{sub_child.get('class')}'")

if __name__ == "__main__":
    main()
