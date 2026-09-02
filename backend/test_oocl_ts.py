import asyncio
from carriers.oocl_connector import OOCLConnector
from models.schemas import RateSearchRequest
import os

async def main():
    connector = OOCLConnector()
    request = RateSearchRequest(
        carriers=["OOCL"],
        origin="Singapore",
        destination="Keelung",
        service_term="CY/CY",
        container_type="DRY 20",
        container_quantity=1,
        weight_per_container_kg=10000,
        commodity="General Cargo",
        departure_date="2026-06-18",
        search_window_days=14
    )
    
    print("Searching...")
    status = await connector.search_quotes(request)
    print("Search Status:", status)
    
    if status == "AVAILABLE_QUOTES_FOUND":
        rows = connector.page.locator('.ag-row')
        count = await rows.count()
        print(f"Found {count} rows")
        
        # Click the first Schedule Details button
        details_btn = connector.page.locator('text="Schedule Details"').first
        if await details_btn.is_visible():
            print("Clicking Schedule Details...")
            await details_btn.click()
            await connector.page.wait_for_timeout(2000)
            
            os.makedirs("scratch", exist_ok=True)
            html = await connector.page.content()
            with open("scratch/oocl_ts_debug.html", "w", encoding="utf-8") as f:
                f.write(html)
            print("Dumped HTML to scratch/oocl_ts_debug.html")

    await connector.close()

if __name__ == "__main__":
    asyncio.run(main())
