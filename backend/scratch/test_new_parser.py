import os
import sys
import re
from datetime import date, datetime, timedelta
from typing import List, Optional
from bs4 import BeautifulSoup

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)

from carriers.oocl_connector import OOCLConnector, parse_oocl_date

class TestOOCLConnector(OOCLConnector):
    @staticmethod
    def _fs_parse_card(text: str) -> Optional[dict]:
        if not text or "USD" not in text.upper():
            return None
            
        # Pre-process text to separate concatenated words/labels on BOTH sides
        t = text
        for label in ["20GP", "40GP", "40HQ", "20RF", "40RQ"]:
            t = re.sub(rf"({label})", r" \1 ", t, flags=re.IGNORECASE)
        for keyword in ["Origin", "Destination", "Smart Uno", "Smart Combo", "Transit Time", "Vessel", "ETD", "ETA", "CY", "Cut-off"]:
            t = re.sub(rf"({keyword})", r" \1 ", t, flags=re.IGNORECASE)
            
        t = " ".join(t.split())
        print(f"[DEBUG parse] Preprocessed text: '{t}'")
        
        kind = "E-Spot" if (re.search(r"\bE[- ]?Spot\b", t, re.IGNORECASE) or 
                            "smart uno" in t.lower() or 
                            "smart combo" in t.lower()) else "E-Quote"

        def _parse_date(raw: str) -> Optional[str]:
            raw = raw.strip()
            m = re.match(r"(\d{4})-(\d{2})-(\d{2})$", raw)
            if m:
                return raw
            m = re.match(r"(\d{1,2})/(\d{1,2})$", raw)
            if m:
                today = date.today()
                month, day = int(m.group(1)), int(m.group(2))
                year = today.year if (month, day) >= (today.month, today.day) or \
                    (today.month, today.day)[0] - month < 6 else today.year + 1
                try:
                    return date(year, month, day).strftime("%Y-%m-%d")
                except ValueError:
                    return None
            m = re.match(r"(\d{1,2})\s+([A-Za-z]{3})", raw)
            if m:
                return parse_oocl_date(raw, 2026) # Match user year
            return None

        etd = eta = None
        # FTD - FTA date range
        m = re.search(r"(\d{1,2}\s+[A-Za-z]{3})\s*-\s*(\d{1,2}\s+[A-Za-z]{3})", t, re.IGNORECASE)
        if m:
            etd = _parse_date(m.group(1))
            eta = _parse_date(m.group(2))
            
        if not etd or not eta:
            m = re.search(r"ETD[:\s]*([0-9/\-]+|\d{1,2}\s+[A-Za-z]{3})", t, re.IGNORECASE)
            if m:
                etd = _parse_date(m.group(1))
            m = re.search(r"ETA[:\s]*([0-9/\-]+|\d{1,2}\s+[A-Za-z]{3})", t, re.IGNORECASE)
            if m:
                eta = _parse_date(m.group(2) if len(m.groups()) > 1 else m.group(1))

        transit = None
        m = re.search(r"(\d+)\s*day", t, re.IGNORECASE)
        if m:
            transit = int(m.group(1))

        # Free time
        free_time = None
        # Match Destination DD2in1 14 CD
        m = re.search(r"Destination\s+(?:DD2in1\s+)?(\d+)\s*(?:CD|WD|calendar\s*days?|days?)", t, re.IGNORECASE)
        if m:
            free_time = int(m.group(1))
        else:
            m = re.search(r"(?:detention|free\s*time)\D{0,30}?(\d+)\s*(?:calendar\s*)?days?", t, re.IGNORECASE) or \
                re.search(r"(\d+)\s*(?:calendar\s*)?days?\D{0,30}?detention", t, re.IGNORECASE)
            if m:
                free_time = int(m.group(1))

        vessel = None
        # Start of card text before CY/Cut-off/ETD
        m = re.search(r"^([A-Z0-9][A-Z0-9 .\-]{2,45}?)(?=\s+(?:CY|Cut-off|ETD|ETA|Transit|USD|Service))", t, re.IGNORECASE)
        if m:
            vessel = m.group(1).strip()
        else:
            m = re.search(r"Vessel\s*(?:/|Voyage)?\s*[:\s]\s*([A-Z0-9][A-Z0-9 .\-]{2,40}?)(?=\s{2,}|\s+(?:ETD|ETA|USD|Transit|Service)|$)",
                          text, re.IGNORECASE)
            if m:
                vessel = m.group(1).strip()

        prices = {}
        for label, ct in OOCLConnector.FS_CONTAINER_MAP.items():
            pm = re.search(rf"{label}[^0-9]{{0,24}}([\d,]+(?:\.\d{{1,2}})?)", t)
            if pm:
                val = float(pm.group(1).replace(",", ""))
                if val > 0 and (ct not in prices or val < prices[ct]):
                    prices[ct] = val

        total_price = None
        m = re.search(r"USD\s*([\d,]+(?:\.\d{1,2})?)", t)
        if m:
            total_price = float(m.group(1).replace(",", ""))

        if not prices and not total_price:
            return None
        return {
            "kind": kind, "etd": etd, "eta": eta, "vessel": vessel,
            "transit_time_days": transit, "free_time": free_time,
            "prices": prices, "total_price": total_price, "currency": "USD",
        }

def test_extraction():
    html_path = "scratch/oocl_fs_results.html"
    if not os.path.exists(html_path):
        print(f"File {html_path} not found.")
        return
        
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()
        
    soup = BeautifulSoup(html, "html.parser")
    
    # We simulate our new structural parser on the html elements
    containers = soup.select('.product-card-container')
    print(f"Found {len(containers)} containers.")
    
    connector = TestOOCLConnector()
    rows = []
    seen = set()
    
    for c_idx, container in enumerate(containers):
        container_text = container.text
        is_espot = ("smart uno" in container_text.lower() or 
                    "smart combo" in container_text.lower() or 
                    "e-spot" in container_text.lower())
                    
        first_card = container.select_one('.product-card')
        if not first_card:
            continue
            
        first_text = first_card.text
        first_parsed = connector._fs_parse_card(first_text)
        if not first_parsed:
            continue
            
        vessel = first_parsed.get("vessel")
        etd = first_parsed.get("etd")
        eta = first_parsed.get("eta")
        transit = first_parsed.get("transit_time_days")
        
        sub_cards = container.select('.product-card')
        print(f"Container [{c_idx}] has {len(sub_cards)} sub-cards.")
        
        for s_idx, card in enumerate(sub_cards):
            card_text = card.text
            parsed = connector._fs_parse_card(card_text)
            if not parsed:
                continue
                
            if not parsed.get("vessel"):
                parsed["vessel"] = vessel
            if not parsed.get("etd"):
                parsed["etd"] = etd
            if not parsed.get("eta"):
                parsed["eta"] = eta
            if not parsed.get("transit_time_days"):
                parsed["transit_time_days"] = transit
            if is_espot:
                parsed["kind"] = "E-Spot"
                
            key = (parsed["kind"], parsed.get("etd"), parsed.get("total_price"),
                   tuple(sorted(parsed["prices"].items())), parsed.get("free_time"))
            if key in seen:
                continue
            seen.add(key)
            rows.append(parsed)
            
    print(f"\n--- Extracted {len(rows)} Rows: ---")
    for idx, r in enumerate(rows):
        print(f"Row {idx+1}:")
        print(f"  Kind: {r['kind']}")
        print(f"  Vessel: {r['vessel']}")
        print(f"  ETD: {r['etd']}")
        print(f"  ETA: {r['eta']}")
        print(f"  Transit Time: {r['transit_time_days']} days")
        print(f"  Free Time: {r['free_time']} days")
        print(f"  Prices: {r['prices']}")

if __name__ == "__main__":
    test_extraction()
