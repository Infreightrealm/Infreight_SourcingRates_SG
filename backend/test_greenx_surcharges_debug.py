import asyncio
import os
import re
from datetime import date, timedelta
from models.schemas import RateSearchRequest
from carriers.greenx_connector import GreenXConnector

async def main():
    print("[TEST SURCHARGES] Debugging Price Details surcharge extraction...")
    connector = GreenXConnector()
    await connector.login()
    
    target_dt = date.today() + timedelta(days=3)
    req = RateSearchRequest(
        origin="Singapore",
        destination="Hamburg",
        container_type="DRY 40H",
        container_quantity=1,
        weight_per_container_kg=20000,
        commodity="Furniture",
        departure_date=target_dt.strftime("%Y-%m-%d"),
        carriers=["GREENX"]
    )
    
    await connector.search_quotes(req)
    route_details_locs = connector.page.locator('button:has-text("Route Details"):visible, a:has-text("Route Details"):visible')
    count = await route_details_locs.count()
    print(f"[TEST SURCHARGES] Total route details buttons: {count}")
    
    for i in range(min(2, count)):
        el = route_details_locs.nth(i)
        card = await connector._get_card_container(el)
        
        # Click Price Details button inside card
        price_btn = card.locator('button:has-text("Price Details"), a:has-text("Price Details"), :text("Price Details")').first
        await price_btn.scroll_into_view_if_needed()
        await price_btn.click()
        print(f"[TEST SURCHARGES] Clicked Price Details for card {i}. Waiting 2s for AJAX...")
        await connector.page.wait_for_timeout(2000)
        
        price_text = await card.inner_text()
        print(f"\n--- CARD {i} PRICE DETAILS TEXT ---")
        print(repr(price_text))
        print("-----------------------------------")
        
        pattern = r"(.+?)\s+(20'\s*Standard\s*Dry|40'\s*Standard\s*Dry|40'\s*High\s*Cube|Per\s*B/L|20'\s*SD|40'\s*SD|40'\s*SH)\s+x\s*\d+\s+USD\s*([\d,]+\.\d{2})"
        matches = re.findall(pattern, price_text)
        print(f"Matches found: {len(matches)}")
        for m in matches:
            print(f"  Charge: {m[0].strip()} | Type: {m[1]} | Price: {m[2]}")

    await connector.close()

if __name__ == "__main__":
    asyncio.run(main())
