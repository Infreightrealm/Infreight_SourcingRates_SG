import asyncio
import os
from datetime import date, timedelta
from models.schemas import RateSearchRequest
from carriers.greenx_connector import GreenXConnector

async def main():
    print("[TEST CARD ISOLATION] Testing card container resolution for GreenX...")
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
    print(f"[TEST CARD ISOLATION] Total route details buttons: {count}")
    
    for i in range(min(5, count)):
        el = route_details_locs.nth(i)
        
        # Test finding the EXACT card container row for this button
        # Walk up parents until we find an element that has exactly 1 Book button or USD price
        card_row = None
        curr = el
        for depth in range(1, 15):
            curr = curr.locator('..')
            txt = await curr.inner_text()
            # If this ancestor contains USD and Book, check how many Book buttons it has inside
            book_cnt = await curr.locator('button:has-text("Book"), a:has-text("Book")').count()
            if book_cnt == 1:  # EXACTLY ONE CARD ROW!
                card_row = curr
                print(f"[ISOLATION SUCCESS] Card {i} resolved at depth {depth}:")
                lines = [l.strip() for l in txt.split("\n") if l.strip()]
                print(f"   First 5 lines: {lines[:5]}")
                break

    await connector.close()

if __name__ == "__main__":
    asyncio.run(main())
