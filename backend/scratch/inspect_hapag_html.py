import re
from bs4 import BeautifulSoup

def inspect_html():
    file_path = "c:/Users/Brian/Downloads/Telegram Desktop/Infreight_Sourcing_18526/Infreight_Sourcing_New/backend/scratch/hapag_results_page.html"
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    # Let's print all TH text
    print("=== TH Elements ===")
    for th in soup.find_all("th"):
        txt = th.get_text(strip=True)
        if txt:
            print(f"TH: '{txt}'")

    # Let's print any element containing text matching common date forms
    print("\n=== Elements matching broad date regex ===")
    seen = set()
    # Find any element containing 2-digit numbers and month names
    for el in soup.find_all(string=re.compile(r"\d{1,4}[-./\s]?(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|2026)", re.IGNORECASE)):
        txt = el.strip()
        if txt and txt not in seen and len(txt) < 50:
            seen.add(txt)
            print(f"Text: '{txt}' (parent tag: {el.parent.name}, classes: {el.parent.get('class')})")

if __name__ == "__main__":
    inspect_html()
