"""
Diagnostic: dump ALL dropdown options (text + innerHTML) when typing 'DEHAM' and 'Hamburg'
into the GreenX destination field so we can see exactly what GreenX offers.
"""
import asyncio
import os
from playwright.async_api import async_playwright

LOGIN_URL = "https://www.greenxtrade.com/_gx/GREENX_SignIn"
USERNAME = "INFREIGHT.SG@IN-FREIGHT.COM"
PASSWORD = "InfreightSGa2026"


async def dump_options(page, query: str, label: str):
    print(f"\n{'='*60}")
    print(f"Typing '{query}' into Destination field:")
    print(f"{'='*60}")

    dest_selectors = [
        'input[placeholder*="DESTINATION" i]',
        'input[id*="destination" i]',
        'input[name*="destination" i]',
    ]
    input_field = None
    for sel in dest_selectors:
        try:
            loc = page.locator(sel).first
            if await loc.is_visible():
                input_field = loc
                break
        except:
            continue

    if not input_field:
        print("  [!] Destination field not found")
        return

    await input_field.click()
    await input_field.press("Control+A")
    await input_field.press("Backspace")
    await input_field.type(query, delay=100)
    await page.wait_for_timeout(2500)

    # Dump all visible li/option elements
    candidates = await page.locator('li, [role="option"]').all()
    print(f"  Found {len(candidates)} li/option elements:")
    for i, sug in enumerate(candidates):
        try:
            visible = await sug.is_visible()
            text = (await sug.text_content() or "").strip()
            inner = (await sug.inner_html() or "").strip()[:200]
            print(f"  [{i}] visible={visible} | text={repr(text)}")
            print(f"       html={inner}")
        except Exception as e:
            print(f"  [{i}] error: {e}")

    # Also dump the value attribute of the input after typing
    val = await input_field.input_value()
    print(f"\n  Input value after typing: {repr(val)}")

    # Press Escape to close dropdown without selecting
    await input_field.press("Escape")
    await page.wait_for_timeout(500)


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        )
        page = await context.new_page()
        page.set_default_timeout(30000)

        print("Navigating to login page...")
        await page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=45000)
        await page.wait_for_timeout(2000)

        # Accept cookies
        try:
            btn = page.locator('button:has-text("Accept All"), button:has-text("Accept all")').first
            if await btn.count() > 0 and await btn.is_visible():
                await btn.click()
                await page.wait_for_timeout(1000)
        except:
            pass

        # Login
        await page.locator('input[type="email"]').first.fill(USERNAME)
        await page.locator('input[type="password"]').first.fill(PASSWORD)
        await page.locator('button[type="submit"]').first.click()
        await page.wait_for_timeout(5000)

        # Accept cookies again if needed
        try:
            btn = page.locator('button:has-text("Accept All"), button:has-text("Accept all")').first
            if await btn.count() > 0 and await btn.is_visible():
                await btn.click()
                await page.wait_for_timeout(1000)
        except:
            pass

        print(f"Logged in. URL: {page.url}")

        # Navigate to Quotes tab
        quotes_btn = page.locator('a:has-text("Quotes"), button:has-text("Quotes")').first
        if await quotes_btn.count() > 0:
            await quotes_btn.click()
            await page.wait_for_timeout(3000)
        print(f"Quotes URL: {page.url}")

        # Try typing different queries for Hamburg destination
        for query in ["DEHAM", "Hamburg", "HAM"]:
            await dump_options(page, query, "Destination")
            await page.wait_for_timeout(1000)

        await page.screenshot(path="diagnose_dropdown.png")
        print("\nSaved screenshot to diagnose_dropdown.png")
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
