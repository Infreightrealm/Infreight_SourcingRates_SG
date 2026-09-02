import asyncio
import os
import re
from datetime import date, timedelta
from models.schemas import RateSearchRequest
from carriers.greenx_connector import GreenXConnector

async def main():
    print("[TEST CLICK METHODS] Testing different click methods on Price Details...")
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
    
    card = await connector._get_card_container(route_details_locs.first)
    
    # Print all links/buttons inside card
    items = card.locator('a, button')
    item_cnt = await items.count()
    print(f"Total clickable items in card: {item_cnt}")
    for i in range(item_cnt):
        item = items.nth(i)
        t = await item.inner_text()
        tag = await item.evaluate("el => el.tagName")
        cls = await item.evaluate("el => el.className")
        href = await item.evaluate("el => el.getAttribute('href')")
        print(f"  Item {i}: <{tag} class='{cls}' href='{href}'> {repr(t)}")

    await connector.close()

if __name__ == "__main__":
    asyncio.run(main())
