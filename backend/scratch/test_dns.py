import asyncio
from patchright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        # Test 1: Without add_init_script
        print("Test 1: Launching browser without add_init_script...")
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        try:
            print("Navigating to https://www.hapag-lloyd.com/en/home.html...")
            await page.goto("https://www.hapag-lloyd.com/en/home.html")
            print("Successfully navigated without add_init_script!")
        except Exception as e:
            print(f"Error in Test 1: {e}")
        await browser.close()

        # Test 2: With add_init_script
        print("\nTest 2: Launching browser with add_init_script...")
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await page.add_init_script("() => { console.log('hello'); }")
        try:
            print("Navigating to https://www.hapag-lloyd.com/en/home.html...")
            await page.goto("https://www.hapag-lloyd.com/en/home.html")
            print("Successfully navigated with add_init_script!")
        except Exception as e:
            print(f"Error in Test 2: {e}")
        await browser.close()

asyncio.run(run())
