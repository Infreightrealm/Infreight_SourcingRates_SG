import asyncio
import os
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("Logging in...")
        await page.goto("https://ecomm.one-line.com/one-ecom/login")
        await page.wait_for_timeout(3000)
        await page.locator('input[name="userId"], input[id="userId"], input[name="username"]').first.fill("INFREIGHTSG")
        await page.locator('input[type="password"], input[name="password"], input[id="password"]').first.fill("SGinfreight!23")
        await page.locator('button:has-text("Login"), button[type="submit"], input[type="submit"]').first.click()
        await page.wait_for_timeout(10000)
        print("Logged in!")

        print("Going to quote booking...")
        await page.goto("https://ecomm.one-line.com/one-ecom/prices/one-quote-booking", wait_until="domcontentloaded")
        
        print("Origin...")
        origin_field = page.get_by_role("combobox", name="Please search location").nth(0)
        await origin_field.wait_for(state="visible", timeout=60000)
        await origin_field.click()
        await page.keyboard.type("Singapore", delay=50)
        await page.wait_for_timeout(1500)
        await page.locator('[role="option"]:visible').filter(has_text="SINGAPORE").first.click()

        print("Destination...")
        destination_field = page.get_by_role("combobox", name="Please search location").nth(1)
        await destination_field.click()
        await page.keyboard.type("HO CHI MINH", delay=50)
        await page.wait_for_timeout(3000)
        
        options = page.locator('[role="option"]:visible')
        count = await options.count()
        print(f"Found {count} options for HO CHI MINH:")
        for i in range(count):
            text = await options.nth(i).inner_text()
            print(f"Option {i}: {text.strip()}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
