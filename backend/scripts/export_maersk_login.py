"""
Save a Maersk login from your own PC for the server to use.

Opens real Google Chrome with its own clean profile. You log in to Maersk yourself
(type the password and solve any CAPTCHA). Once you're in, it opens the booking
page and saves the logged-in cookies to maersk_session.json in the project folder.
Upload that file in Admin > Carriers on / off > Maersk > Upload saved login.

The file is a live login: don't share it or commit it (it's gitignored).

Run:  EXPORT_MAERSK_LOGIN.bat   (or: python backend/scripts/export_maersk_login.py)
"""
import asyncio
import json
import os
import sys

from patchright.async_api import async_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROFILE_DIR = os.path.join(ROOT, "backend", "chrome_profile_maersk_export")
OUT_FILE = os.path.join(ROOT, "maersk_session.json")
LOGIN_URL = "https://www.maersk.com/login"
BOOK_URL = "https://www.maersk.com/book/"

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


def _on_login_page(url: str) -> bool:
    u = url.lower()
    return "accounts.maersk.com" in u or "login" in u or "/auth" in u


async def _logged_in(page) -> bool:
    if _on_login_page(page.url) or "maersk.com" not in page.url.lower():
        return False
    for sel in ['a[href*="logout"]', 'text="Log out"', 'text="Sign out"']:
        try:
            if await page.locator(sel).first.is_visible(timeout=300):
                return True
        except Exception:
            pass
    return any(k in page.url.lower() for k in ["/hub", "/book"]) and "login" not in page.url.lower()


async def main():
    os.makedirs(PROFILE_DIR, exist_ok=True)
    async with async_playwright() as p:
        kwargs = dict(user_data_dir=PROFILE_DIR, headless=False, no_viewport=True, args=["--start-maximized"])
        try:
            context = await p.chromium.launch_persistent_context(channel="chrome", **kwargs)
        except Exception as e:
            print(f"Google Chrome not found ({e}). Install Chrome, or this uses the bundled browser instead.")
            context = await p.chromium.launch_persistent_context(**kwargs)
        page = context.pages[0] if context.pages else await context.new_page()

        print("=" * 64)
        print(" Chrome is open. Log in to Maersk in that window yourself:")
        print("   - type the username and password (don't let Chrome autofill)")
        print("   - solve any CAPTCHA or verification")
        print(" This window saves the login as soon as you're in (15 min max).")
        print("=" * 64)
        try:
            await page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=60000)
        except Exception as e:
            print(f"Note: {e}")

        for second in range(900):
            await asyncio.sleep(1)
            page = context.pages[-1] if context.pages else page
            if await _logged_in(page):
                break
            if second % 30 == 29:
                print(f"Waiting for you to log in... ({(900 - second) // 60} min left)")
        else:
            print("Login wasn't detected in 15 minutes. Nothing was saved.")
            await context.close()
            return

        print("Logged in. Opening the booking page so its cookies are saved too...")
        try:
            await page.goto(BOOK_URL, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(8000)
        except Exception as e:
            print(f"Note: {e}")
        if _on_login_page(page.url):
            print("Maersk sent the booking page back to login. Log in again and rerun this script.")
            await context.close()
            return

        state = await context.storage_state()
        state["cookies"] = [c for c in state["cookies"] if "maersk.com" in c.get("domain", "")]
        state["origins"] = [o for o in state.get("origins", []) if "maersk.com" in o.get("origin", "")]
        with open(OUT_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f)
        await context.close()

    print("=" * 64)
    print(f" Saved {len(state['cookies'])} Maersk cookies to:")
    print(f"   {OUT_FILE}")
    print(" Upload it in Admin > Carriers on / off > Maersk > Upload saved login.")
    print(" Then delete the file from this PC.")
    print("=" * 64)


if __name__ == "__main__":
    asyncio.run(main())
