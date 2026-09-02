from bs4 import BeautifulSoup

def inspect_content():
    file_path = "c:/Users/Brian/Downloads/Telegram Desktop/Infreight_Sourcing_18526/Infreight_Sourcing_New/backend/scratch/hapag_results_page.html"
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    print("=== All text elements under 25 chars ===")
    seen = set()
    for el in soup.find_all(True):
        if el.children and any(child.name is not None for child in el.children):
            continue  # Only print leaf-like elements
        txt = el.get_text(strip=True)
        if txt and txt not in seen and len(txt) < 25:
            seen.add(txt)
            print(f"[{el.name}]: '{txt}'")

if __name__ == "__main__":
    inspect_content()
