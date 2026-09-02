import asyncio
import os
import sys
import getpass
import re
from dotenv import load_dotenv

# Add backend folder and root folder to python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_dir)
sys.path.append(os.path.dirname(backend_dir))

# Load env variables from backend/.env
load_dotenv(os.path.join(backend_dir, ".env"))

from models.schemas import RateSearchRequest
from carriers.oocl_connector import OOCLConnector
from carriers.registry import get_connector

async def main():
    # Prompt for credentials if they are not in the .env file
    username = os.getenv("OOCL_USERNAME")
    password = os.getenv("OOCL_PASSWORD")
    
    if not username:
        username = input("Enter OOCL FreightSmart Username (Email): ").strip()
        os.environ["OOCL_USERNAME"] = username
    if not password:
        password = getpass.getpass("Enter OOCL FreightSmart Password: ").strip()
        os.environ["OOCL_PASSWORD"] = password

    # Setup the search request
    origin = os.getenv("OOCL_TEST_ORIGIN") or "Singapore"
    destination = os.getenv("OOCL_TEST_DESTINATION") or "Keelung"
    
    request = RateSearchRequest(
        carriers=["OOCL"],
        origin=origin,
        destination=destination,
        container_type="DRY 20",
        container_quantity=1,
        weight_per_container_kg=10000,
        commodity="General Cargo",
        departure_date="2026-07-15",
        search_window_days=14
    )

    connector = OOCLConnector()
    # Force query FreightSmart
    os.environ["OOCL_QUERY_FREIGHTSMART"] = "true"
    
    print("\n--- Starting OOCL FreightSmart Headed Search ---")
    
    # Initialize browser context
    await connector._init_browser()
    page = await connector.context.new_page()
    
    watcher_task = None
    stop_event = None
    
    try:
        # Step 1: Login
        print("[OOCL] [FS] Attempting login...")
        login_ok = await connector._fs_login(page)
        if not login_ok:
            print("[OOCL] [FS] Login failed.")
            return
            
        print("[OOCL] [FS] Login success. Landed on:", page.url)
        
        # Wait for SSO redirect to land on /ui/ automatically
        for _ in range(15):
            if "/ui" in (page.url or ""):
                break
            await page.wait_for_timeout(1000)

        if "/ui" not in (page.url or ""):
            print("[OOCL] [FS] Navigating to FS Home URL...")
            try:
                await page.goto(connector.FS_HOME_URL, wait_until="domcontentloaded")
            except Exception as goto_err:
                if "ERR_ABORTED" not in str(goto_err):
                    raise
            await page.wait_for_timeout(2000)
            
        await connector._fs_dismiss_modals(page)

        # Setup watcher
        stop_event = asyncio.Event()
        ui_lock = asyncio.Lock()
        watcher_task = asyncio.create_task(
            connector._fs_popup_watcher_loop(page, stop_event, lock=ui_lock)
        )

        # Fill origin, destination, container type & quantity
        print(f"[OOCL] [FS] Filling origin: {request.origin}")
        if not await connector._fs_fill_port(page, "origin", request.origin, lock=ui_lock):
            print("[OOCL] [FS] Failed to fill origin.")
            return
            
        print(f"[OOCL] [FS] Filling destination: {request.destination}")
        if not await connector._fs_fill_port(page, "destination", request.destination, lock=ui_lock):
            print("[OOCL] [FS] Failed to fill destination.")
            return
            
        print("[OOCL] [FS] Setting container quantities...")
        await connector._fs_set_container_quantities(page, lock=ui_lock)

        # Submit Quote Request
        try:
            async with ui_lock:
                await page.locator('button:has-text("Get Quote")').first.click()
            print("[OOCL] [FS] Clicked 'Get Quote'. Waiting for results page to render...")
        except Exception as e:
            print(f"[OOCL] [FS] Could not click Get Quote: {e}")
            return

        # Wait for results page to render (either cards or a "no results" state)
        for i in range(45):
            try:
                # Check if at least one product card container is visible
                if await page.locator('.product-card-container, [class*="product-card" i]').first.is_visible():
                    print(f"[OOCL] [FS] Results cards rendered after {i+1} seconds.")
                    break
                # Check if the "no results" placeholder is visible
                body = await page.locator("body").inner_text()
                if "no results" in body.lower() or "sorry" in body.lower():
                    print(f"[OOCL] [FS] No results message detected after {i+1} seconds.")
                    break
            except Exception:
                pass
            await page.wait_for_timeout(1000)

        # Stop the watcher now that results page has loaded and popups are dismissed
        stop_event.set()
        await watcher_task
        watcher_task = None
        await connector._fs_dismiss_modals(page)

        # Save debug screenshot/HTML
        os.makedirs("scratch", exist_ok=True)
        await page.screenshot(path="scratch/oocl_fs_results.png", full_page=True)
        with open("scratch/oocl_fs_results.html", "w", encoding="utf-8") as f:
            f.write(await page.content())
        print("[OOCL] [FS] Saved debug dump to scratch/oocl_fs_results.*")

        # Attempt to extract quotes via full 14-day calendar iteration
        print("[OOCL] [FS] Attempting to iterate calendar dates and extract rows...")
        rows = await connector._fs_iterate_calendar_dates(page)
        print(f"\n--- Extracted {len(rows)} Total Rows (across all dates): ---")
        for idx, row in enumerate(rows):
            print(f"Row {idx+1}: {row}")

    except Exception as e:
        print(f"[OOCL] [FS] Error during run: {e}")
    finally:
        if watcher_task is not None:
            stop_event.set()
            try:
                await watcher_task
            except Exception:
                pass
        
        print("\nBrowser is paused. You can interact with it to inspect elements.")
        await asyncio.get_event_loop().run_in_executor(None, input, "Press Enter to close the browser and finish...")
        await connector.close()

if __name__ == "__main__":
    asyncio.run(main())
