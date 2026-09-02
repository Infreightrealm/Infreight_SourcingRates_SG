with open("carriers/maersk_connector.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "offer-card" in line or "card" in line or "nth(" in line:
        print(f"Line {idx+1}: {line.strip()}")
