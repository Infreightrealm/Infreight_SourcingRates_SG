import os
from bs4 import BeautifulSoup

def main():
    html_file = os.path.join(os.path.dirname(__file__), 'breakdown_html_3.html')
    if not os.path.exists(html_file):
        print(f"Error: {html_file} does not exist.")
        return

    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Search for any element containing "breakdown" or "Price breakdown" in text or attributes
    all_elements = soup.find_all(lambda tag: tag.string and 'breakdown' in tag.string.lower())
    print(f"Found {len(all_elements)} elements containing 'breakdown' in their string:")
    for el in all_elements:
        print(f"Tag: <{el.name}>, Classes: '{el.get('class', [])}', Text: '{el.string.strip()}', Attributes: {el.attrs}")
        
    print("\n--- Searching broadly in elements' children ---")
    broad_elements = soup.find_all(lambda tag: tag.text and 'price breakdown & details' in tag.text.lower())
    print(f"Found {len(broad_elements)} broad elements containing the text:")
    for el in broad_elements[:5]: # print first 5 to avoid overflow
        print(f"Tag: <{el.name}>, Classes: '{el.get('class', [])}', Attrs: {el.attrs}")
        # print first few lines of text
        snippet = ' | '.join([t.strip() for t in el.stripped_strings])[:150]
        print(f"  Text snippet: '{snippet}'")

if __name__ == '__main__':
    main()
