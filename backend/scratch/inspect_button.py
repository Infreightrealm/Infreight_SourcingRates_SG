from bs4 import BeautifulSoup

def main():
    print("Reading scratch/debug_results.html...")
    with open("scratch/debug_results.html", "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    
    # 1. Search for any elements containing "price breakdown" or "details"
    print("\n--- ELEMENTS CONTAINING 'PRICE BREAKDOWN' OR 'DETAILS' ---")
    for tag in soup.find_all(True):
        if tag.name not in ["script", "style"] and tag.string and any(w in tag.string.lower() for w in ["price breakdown", "breakdown"]):
            print(f"Tag: <{tag.name}>, Class: '{' '.join(tag.get('class', []))}'")
            print(f"  Parent: <{tag.parent.name}>, Parent class: '{' '.join(tag.parent.get('class', []))}'")
            print(f"  String: '{tag.string.strip()}'")
            
    # 2. Search for any button or link that could be the details toggle
    print("\n--- BUTTONS/LINKS/SPAN TOGGLES INSIDE THE FIRST new-sailings-card-article ---")
    card = soup.find("article", class_="new-sailings-card-article")
    if card:
        for item in card.find_all(["button", "a", "span", "div"]):
            item_text = item.get_text(strip=True)
            if any(w in item_text.lower() for w in ["breakdown", "details", "price"]):
                # Only print if it's a leaf element (has no child elements with text containing those words)
                children_match = False
                for child in item.find_all(True):
                    if any(w in child.get_text(strip=True).lower() for w in ["breakdown", "details"]):
                        children_match = True
                        break
                if not children_match:
                    print(f"Tag: <{item.name}>, Class: '{' '.join(item.get('class', []))}', Text: '{item_text[:100]}'")
    else:
        print("No new-sailings-card-article found in DOM.")

if __name__ == "__main__":
    main()
