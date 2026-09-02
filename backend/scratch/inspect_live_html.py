from bs4 import BeautifulSoup
import re

def main():
    print("Reading scratch/debug_results.html...")
    with open("scratch/debug_results.html", "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    print(f"Total HTML size: {len(html)} characters")

    # Let's search for elements with "sailing", "card", "offer", "result" in class names
    matched_elements = []
    for tag in soup.find_all(True):
        class_list = tag.get("class", [])
        class_str = " ".join(class_list).lower()
        if any(w in class_str or w in tag.name for w in ["sailing", "card", "offer", "result"]):
            matched_elements.append(tag)

    print(f"Found {len(matched_elements)} elements containing 'sailing', 'card', 'offer', or 'result'.")

    # Let's count occurrences of classes
    class_counts = {}
    for tag in matched_elements:
        class_list = tag.get("class", [])
        for cls in class_list:
            class_counts[cls] = class_counts.get(cls, 0) + 1

    print("\nClass frequencies:")
    for cls, count in sorted(class_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  - '{cls}': {count} occurrences")

    # Let's look at the structure of tags containing "sailing"
    print("\nTags containing 'sailing' or 'card' class name examples:")
    printed = 0
    for tag in matched_elements:
        class_list = tag.get("class", [])
        class_str = " ".join(class_list)
        if "sailing" in class_str.lower() and tag.name in ["article", "section", "div", "header"]:
            # Print tag info, parent tag, and snippet of text
            parent_name = tag.parent.name if tag.parent else "None"
            parent_classes = " ".join(tag.parent.get("class", [])) if tag.parent else ""
            text_snippet = tag.get_text(strip=True)[:120].replace('\n', ' ')
            print(f"Tag: <{tag.name}>, Class: '{class_str}' | Parent: <{parent_name}> (class: '{parent_classes}')")
            print(f"  Text: {text_snippet[:100]}...")
            printed += 1
            if printed >= 15:
                break

    # Search for all h1, h2, h3, h4 tags to see headers on the page
    print("\nAll Header elements on page:")
    for h in soup.find_all(["h1", "h2", "h3", "h4"]):
        print(f"  <{h.name}>: '{h.get_text(strip=True)}'")

if __name__ == "__main__":
    main()
