import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

import asyncio
from carriers.cma_connector import CMAConnector
from models.schemas import RateSearchRequest

async def inspect():
    os.environ["CMA_USERNAME"] = "bookingsg@in-freight.com"
    os.environ["CMA_PASSWORD"] = "@IFSGc2023"

    for key in ["CMA_PROXY_USER", "CMA_PROXY_PASS", "MAERSK_PROXY_USER", "MAERSK_PROXY_PASS",
                "BRIGHTDATA_PROXY_USER", "BRIGHTDATA_PROXY_PASS", "BRIGHTDATA_PROXY_SERVER"]:
        os.environ[key] = ""

    connector = CMAConnector()
    try:
        print("Logging in...")
        await connector.login()
        
        request = RateSearchRequest(
            origin="SGSIN",
            destination="MYPKG",
            container_type="DRY 40H",
            container_quantity=1,
            weight_per_container_kg=15000,
            commodity="Furniture",
            departure_date="tomorrow",
            carriers=["CMA"]
        )

        print("Filling Origin & Destination & Container...")
        # Step 1: Origin
        origin_field = connector.page.locator('input[placeholder*="Name / Code / Port" i]').nth(0)
        await origin_field.click()
        await origin_field.fill("SGSIN")
        await connector.page.wait_for_timeout(2000)
        await connector._select_cma_dropdown_option("Origin", "SGSIN", None)

        # Step 2: Destination
        dest_field = connector.page.locator('input[placeholder*="Name / Code / Port" i]').nth(1)
        await dest_field.click()
        await dest_field.fill("MYPKG")
        await connector.page.wait_for_timeout(2000)
        await connector._select_cma_dropdown_option("Destination", "MYPKG", None)

        # Step 3: Container
        cma_container = "40' Dry High Cube"
        items = connector.page.locator('text=/\\d+.*(?:DRY|REEFER|FLAT|OPEN)/i')
        item_count = await items.count()
        for i in range(item_count):
            item = items.nth(i)
            item_text = (await item.inner_text()).strip().upper()
            if "40" in item_text and "HIGH" in item_text:
                parent = item.locator('..')
                add_btn = parent.locator('button:has-text("Add"), button:has-text("+")')
                if await add_btn.count() > 0:
                    await add_btn.first.click()
                    break
        
        await connector.page.wait_for_timeout(2000)

        # Step 4: Click the commodity dropdown input to open it
        print("Clicking commodity dropdown...")
        commodity_input = connector.page.locator('#DdlCommodity').first
        await commodity_input.click()
        await connector.page.wait_for_timeout(2000)

        # Let's inspect all option texts inside the dropdown
        print("--- DUMPING DROPDOWN OPTIONS ---")
        options = await connector.page.evaluate(
            """
            () => {
                const items = Array.from(document.querySelectorAll('.el-select-dropdown__item'));
                return items.map(el => ({
                    text: el.innerText || el.textContent,
                    html: el.outerHTML
                }));
            }
            """
        )
        for idx, opt in enumerate(options):
            print(f"Option {idx}: '{opt['text']}'")
        
    finally:
        await connector.close()

if __name__ == "__main__":
    asyncio.run(inspect())
