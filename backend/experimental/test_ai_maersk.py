"""
Experimental AI Agent Test -- Maersk Quote Search

This script tests the AI vision agent on the Maersk Spot booking portal.
It is COMPLETELY SEPARATE from production code and uses NO hardcoded selectors.

The agent navigates the website purely by looking at screenshots and deciding
what to click/type, powered by Gemini Flash's vision capabilities.

Usage:
    cd backend
    python -m experimental.test_ai_maersk
"""
import os
import sys
import asyncio
import json
from datetime import datetime
from dotenv import load_dotenv

# Load experimental env (Gemini key)
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
# Load main env (Maersk credentials)
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# Windows event loop fix
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from experimental.ai_agent import AIBrowserAgent


def safe_print(msg: str):
    """Print with ASCII-safe encoding for Windows console."""
    safe = msg.encode("ascii", errors="replace").decode("ascii")
    print(safe)


async def main():
    safe_print("=" * 70)
    safe_print("  EXPERIMENTAL: AI Vision Agent -- Maersk Quote Search")
    safe_print("  This uses ZERO hardcoded selectors. The AI sees screenshots")
    safe_print("  and decides what to click/type on its own.")
    safe_print("=" * 70)
    
    # -- Configuration --
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        safe_print("[ERROR] GEMINI_API_KEY not found in experimental/.env")
        return
    
    maersk_user = os.getenv("MAERSK_USERNAME", "")
    maersk_pass = os.getenv("MAERSK_PASSWORD", "")
    
    origin = "Singapore"
    destination = "Hamburg"
    
    safe_print(f"\n[CONFIG] Route: {origin} -> {destination}")
    safe_print(f"[CONFIG] Maersk user: {maersk_user}")
    safe_print(f"[CONFIG] Gemini model: gemini-2.5-flash")
    safe_print("")
    
    # -- Launch Browser --
    # Reuse the same Patchright stealth engine the production connectors use
    from patchright.async_api import async_playwright
    
    playwright = await async_playwright().start()
    
    # Use a copy of the master profile to bypass 2FA
    import uuid
    import shutil
    temp_profile = os.path.join(
        os.path.dirname(__file__), "..", 
        f"chrome_profile_ai_experiment_{uuid.uuid4().hex[:8]}"
    )
    master_profile = os.path.join(
        os.path.dirname(__file__), "..", "chrome_profile_maersk"
    )
    if os.path.exists(master_profile):
        safe_print(f"[BROWSER] Copying master profile from {master_profile} to bypass 2FA...")
        shutil.copytree(master_profile, temp_profile, dirs_exist_ok=True)
        # Clean locks
        for root_dir, _, filenames in os.walk(temp_profile):
            for filename in filenames:
                if filename in ["SingletonLock", "lock", "SingletonCookie"]:
                    try:
                        os.remove(os.path.join(root_dir, filename))
                    except:
                        pass
    else:
        safe_print("[BROWSER] Master profile not found, starting fresh...")
        os.makedirs(temp_profile, exist_ok=True)
    
    safe_print(f"[BROWSER] Launching Chrome with temp profile...")
    
    context = await playwright.chromium.launch_persistent_context(
        user_data_dir=temp_profile,
        headless=False,
        channel="chrome",
        viewport={"width": 1920, "height": 1080},
        ignore_https_errors=True,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
        ],
    )
    
    page = context.pages[0] if context.pages else await context.new_page()
    page.set_default_timeout(30000)
    await page.bring_to_front()
    
    # -- Create AI Agent --
    screenshot_dir = os.path.join(
        os.path.dirname(__file__), 
        "screenshots", 
        datetime.now().strftime("%Y%m%d_%H%M%S")
    )
    
    agent = AIBrowserAgent(
        page=page,
        api_key=gemini_key,
        model_name="gemini-2.5-flash",
        screenshot_dir=screenshot_dir,
        verbose=True,
    )
    
    # -- Step 1: Navigate to Maersk login --
    safe_print("\n[STEP 1] Navigating to Maersk login page...")
    await page.goto("https://www.maersk.com/login", wait_until="domcontentloaded", timeout=40000)
    await page.wait_for_timeout(3000)
    
    # -- Step 2: AI Agent handles login --
    safe_print("\n[STEP 2] AI Agent taking over for LOGIN...")
    login_task = f"""Log into the Maersk shipping portal.

Instructions:
1. If you see a cookie consent banner, click "Allow all" or "Essential only" to dismiss it.
2. Find the username/email input field and type: {maersk_user}
3. Find the password input field and type: {maersk_pass}
4. Click the login/submit button.
5. Wait for the page to redirect after login (the URL should change away from 'login' or 'auth').
6. If you see a CAPTCHA or 2FA challenge, return fail() -- a human needs to handle that.
7. Once you see a dashboard, hub, or booking page (not a login page), return done().

IMPORTANT: Type credentials carefully, one field at a time. Click the field first, then type."""

    login_result = await agent.execute_task(
        task=login_task,
        max_steps=20,
    )
    
    safe_print(f"\n[LOGIN RESULT] Success: {login_result['success']}")
    safe_print(f"[LOGIN RESULT] Steps: {login_result['steps']}")
    safe_print(f"[LOGIN RESULT] Result: {login_result['result']}")
    
    if not login_result["success"]:
        safe_print("\n[ABORT] Login failed. Cannot proceed to search.")
        await context.close()
        await playwright.stop()
        _cleanup_profile(temp_profile)
        return
    
    # -- Step 3: Navigate to booking page --
    safe_print("\n[STEP 3] Navigating to Maersk booking page...")
    await page.goto("https://www.maersk.com/book", wait_until="domcontentloaded", timeout=40000)
    await page.wait_for_timeout(3000)
    
    # -- Step 4: AI Agent fills the search form --
    safe_print("\n[STEP 4] AI Agent taking over for SEARCH FORM...")
    search_task = f"""Fill out the Maersk Spot ocean freight search form.

Instructions:
1. If you see a "Got it" popup or banner, dismiss it by clicking the banner's button.
2. Find the "From" or origin port input field (usually says "Enter city or port").
   - Click on it and type: {origin}
   - Wait for the autocomplete dropdown to appear.
   - Click option "{origin}, {origin}" or the option matching {origin}.
3. Find the "To" or destination port input field.
   - Click on it and type: {destination}
   - Wait for the autocomplete dropdown to appear.
   - Click the option for {destination} in GERMANY (usually "Hamburg (Hamburg), Germany").
4. For commodity (What do you want to ship?):
   - Click on the commodity input field first, type "Furniture", wait 2 seconds for dropdown options to appear, and CLICK on the option "Furniture" or "Furniture, nos" in the dropdown list. You MUST click the option to unlock container options!
5. Scroll down to bring the container details section into view.
6. For container type:
   - Click the "Select container type and size" input field to open the dropdown list.
   - Wait 1-2 seconds, look at the dropdown list, and click option "40 Dry Standard" or "40' Dry Standard".
7. For cargo weight:
   - Click the "Enter cargo weight" input field first to focus it, then type: 20000
8. Scroll down further to see the price owner and cargo ready date sections.
9. For price owner:
   - Find and click the radio option or label "I am the price owner". (Note: selecting this automatically populates the card inline, there is no modal popup to close. Do NOT click empty space after selecting).
10. For ready date:
    - Click "Select tomorrow" button or link. This will enable the "Continue to book" button.
11. Scroll down to the bottom, locate the "Continue to book" button, and click it.
12. Once you see the "Select sailing" page or results loading, return done().

CRITICAL:
- ALWAYS click the input field to focus it before typing.
- ALWAYS click option suggestions from the dropdowns for origin, destination, commodity, and container type instead of just typing and ignoring them.
- DO NOT try to close a modal after clicking "I am the price owner". It renders inline.
- ALWAYS click "Select tomorrow" to make the "Continue to book" button clickable.
"""

    search_result = await agent.execute_task(
        task=search_task,
        max_steps=35,
    )
    
    safe_print(f"\n[SEARCH RESULT] Success: {search_result['success']}")
    safe_print(f"[SEARCH RESULT] Steps: {search_result['steps']}")
    safe_print(f"[SEARCH RESULT] Result: {search_result['result']}")
    
    # -- Save results --
    results_file = os.path.join(screenshot_dir, "experiment_results.json")
    with open(results_file, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "route": f"{origin} -> {destination}",
            "login": login_result,
            "search": search_result,
        }, f, indent=2, default=str)
    
    safe_print(f"\n[SAVED] Full results and screenshots: {screenshot_dir}")
    
    # Keep browser open briefly for inspection
    safe_print("\n[INFO] Browser will stay open for 30 seconds for inspection...")
    await page.wait_for_timeout(30000)
    
    # -- Cleanup --
    safe_print("[CLEANUP] Closing browser...")
    await context.close()
    await playwright.stop()
    _cleanup_profile(temp_profile)
    safe_print("[DONE] Experiment complete!")


def _cleanup_profile(profile_dir: str):
    """Remove temporary chrome profile directory."""
    import shutil
    try:
        if os.path.exists(profile_dir):
            shutil.rmtree(profile_dir, ignore_errors=True)
            safe_print(f"[CLEANUP] Removed temp profile: {profile_dir}")
    except Exception as e:
        safe_print(f"[CLEANUP] Warning: Could not remove {profile_dir}: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[ABORT] Experiment aborted by user.")
