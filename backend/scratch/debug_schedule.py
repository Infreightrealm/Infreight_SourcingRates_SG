import sys
sys.path.append(".")
import asyncio
import os
import json
from dotenv import load_dotenv
from carriers.hapag_lloyd_connector import HapagLloydConnector
from models.schemas import RateSearchRequest

async def debug_schedules():
    load_dotenv()
    
    print("Initializing HapagLloydConnector for debugging...")
    connector = HapagLloydConnector()
    
    try:
        login_ok = await connector.login()
        print(f"Login result: {login_ok}")
        if not login_ok:
            return
            
        request = RateSearchRequest(
            origin="SGSIN",
            destination="MYPKG",
            container_type="DRY 40H",
            container_quantity=2,
            weight_per_container_kg=20000,
            departure_date="tomorrow",
            carriers=["HAPAG_LLOYD"]
        )
        
        # Navigate to schedule url
        print("Navigating to Schedule page...")
        await connector.page.goto("https://www.hapag-lloyd.com/solutions/schedule/#/")
        await connector.page.wait_for_load_state("domcontentloaded", timeout=12000)
        await connector._human_delay(1500, 2500)
        await connector._dismiss_hapag_modals()
        
        # Select Origin
        origin_locode = "SGSIN"
        start_field = connector.page.locator('xpath=(//*[contains(text(), "Start Location")])[1]/following::input[1]').first
        await start_field.click()
        await start_field.press("Control+A")
        await start_field.press("Backspace")
        await start_field.type(origin_locode, delay=50)
        await connector._human_delay(1500, 2500)
        await connector._select_hapag_dropdown_option("Start Location", origin_locode, None)
        
        # Select Destination
        dest_locode = "MYPKG"
        end_field = connector.page.locator('xpath=(//*[contains(text(), "End Location")])[1]/following::input[1]').first
        await end_field.click()
        await end_field.press("Control+A")
        await end_field.press("Backspace")
        await end_field.type(dest_locode, delay=50)
        await connector._human_delay(1500, 2500)
        await connector._select_hapag_dropdown_option("End Location", dest_locode, None)
        
        # Start Date
        from datetime import date, timedelta
        target_start_date = (date.today() + timedelta(days=1)).isoformat()
        date_field = connector.page.locator('xpath=(//*[contains(text(), "Start Date")])[1]/following::input[1]').first
        await date_field.click()
        await date_field.press("Control+A")
        await date_field.press("Backspace")
        await date_field.type(target_start_date, delay=50)
        await date_field.press("Enter")
        await connector._human_delay(500, 1000)
        
        # Click search
        search_btn = connector.page.locator('button:has-text("Search")').first
        await search_btn.click()
        await connector._human_delay(4000, 6000)
        
        print("Waiting for results...")
        try:
            await connector.page.wait_for_selector('button:has-text("Show Details")', timeout=20000)
            print("Results loaded successfully!")
        except Exception as wait_err:
            print(f"Wait failed: {wait_err}")
            await connector.page.screenshot(path="scratch/debug_schedule_loaded.png")
            raise wait_err
        
        await connector.page.screenshot(path="scratch/debug_schedule_loaded.png")
        
        # Capture all element text to see how Voyage no is structured
        info = await connector.page.evaluate('''() => {
            const allElements = Array.from(document.querySelectorAll('*'));
            const matching = allElements.filter(el => {
                const text = el.textContent || "";
                return text.includes("Voyage") || text.includes("Show Details");
            });
            
            return matching.slice(0, 100).map(el => {
                return {
                    tagName: el.tagName,
                    className: el.className,
                    text: (el.textContent || "").substring(0, 100).trim(),
                    childrenCount: el.children.length
                };
            });
        }''')
        
        # Capture the raw HTML of the first card
        card_html = await connector.page.evaluate('''() => {
            const card = Array.from(document.querySelectorAll('*')).find(el => {
                return (el.textContent || "").includes("Voyage no.:") && (el.textContent || "").includes("Show Details");
            });
            return card ? card.outerHTML : "Card not found";
        }''')
        
        os.makedirs("scratch", exist_ok=True)
        with open("scratch/debug_schedules_info.json", "w", encoding="utf-8") as f:
            json.dump({"elements": info, "card_html": card_html}, f, indent=2)
            
        print("Debug info saved to scratch/debug_schedules_info.json")
        
    finally:
        await connector.close()

if __name__ == "__main__":
    asyncio.run(debug_schedules())
