import asyncio
import os
import re
from datetime import date, timedelta
from models.schemas import RateSearchRequest
from carriers.greenx_connector import GreenXConnector

async def main():
    print("[TEST ACCORDION EXPAND] Inspecting accordion collapse element...")
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
    card = await connector._get_card_container(route_details_locs.first)
    
    price_btn = card.locator('button:has-text("Price Details")').first
    target_id = await price_btn.evaluate("el => el.getAttribute('data-bs-target') || el.getAttribute('href') || el.getAttribute('aria-controls')")
    print(f"Price Details button target: {target_id}")
    
    await price_btn.click()
    print("Clicked Price Details button. Waiting 1.5s...")
    await connector.page.wait_for_timeout(1500)
    
    if target_id:
        target_sel = target_id if target_id.startswith('#') else f'#{target_id}'
        target_el = connector.page.locator(target_sel)
        if await target_el.count() > 0:
            txt = await target_el.inner_text()
            print("\n--- TARGET ACCORDION CONTENT ---")
            print(repr(txt))
            print("---------------------------------")
        else:
            print(f"Target selector {target_sel} not found on page.")

    await connector.close()

if __name__ == "__main__":
    asyncio.run(main())
