import asyncio
from playwright.async_api import async_playwright
import os

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()

        print("Logging in...")
        await page.goto("https://ecomm.one-line.com/one-ecom/login")
        await page.get_by_role("textbox", name="User ID").first.fill(os.getenv("ONE_USERNAME", "INFREIGHTSG"))
        await page.get_by_role("textbox", name="Password").first.fill(os.getenv("ONE_PASSWORD", "Infreight123!"))
        await page.locator('button:has-text("Login"), button[type="submit"], input[type="submit"]').first.click()
        
        print("Waiting for dashboard...")
        await page.wait_for_url("**/one-ecom**", timeout=30000)
        await page.wait_for_timeout(3000)

        print("Going to quote booking...")
        await page.goto("https://ecomm.one-line.com/one-ecom/prices/one-quote-booking", wait_until="domcontentloaded")
        
        origin_field = page.get_by_role("combobox", name="Please search location").nth(0)
        await origin_field.wait_for(state="visible", timeout=60000)
        await origin_field.click()
        await page.keyboard.type("Singapore", delay=50)
        await page.wait_for_timeout(1500)
        await page.locator('[role="option"]:visible').filter(has_text="SINGAPORE").first.click()

        destination_field = page.get_by_role("combobox", name="Please search location").nth(1)
        await destination_field.click()
        await page.keyboard.type("HO CHI MINH", delay=50)
        await page.wait_for_timeout(1500)
        await page.locator('[role="option"]:visible').filter(has_text="HO CHI MINH").first.click()

        equipment_field = page.get_by_role("combobox", name="Select an Equipment Type").first
        await equipment_field.click()
        await page.locator('[role="option"]').filter(has_text="DRY 20").first.click()

        weight_field = page.locator('input[placeholder="0"]').first
        await weight_field.fill("18000")
        await weight_field.press("Enter")

        commodity_field = page.get_by_role("combobox", name="Please input Commodity Name or HS code").first
        await commodity_field.click()
        await page.wait_for_timeout(500)
        await page.keyboard.type("Furniture", delay=25)
        await page.wait_for_timeout(3000)
        try:
            await page.locator('[role="option"]').first.click()
        except:
            await page.keyboard.press("Enter")
            
        await page.wait_for_timeout(3000)

        date_field = page.locator('text=/please select vessel departure date at origin/i').first
        try:
            await date_field.click()
        except:
            date_field = page.get_by_role("textbox", name="Please select vessel departure date at origin")
            await date_field.click()
            
        await page.wait_for_timeout(5000)
        
        calendar = page.locator('div[class*="BookingCalendar_calendar-wrapper"]')
        if await calendar.count() == 0:
            calendar = page.locator('div.react-calendar')
        
        print("Calendar DOM:")
        print(await calendar.first.inner_html())
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
