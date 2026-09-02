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
    
    # Let's find the first product-card-container
    container = soup.select_one('[class*="product-card-container" i]')
    if not container:
        print("No product-card-container found.")
        return
        
    print("--- HTML of product-card-container ---")
    print(container.prettify()[:4000])

if __name__ == "__main__":
    main()
