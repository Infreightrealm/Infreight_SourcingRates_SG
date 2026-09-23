"""
Interactive Headed Login Helper for Maersk.
Opens real Chrome using the persistent profile `backend/chrome_profile_maersk`,
navigates to Maersk login, automatically fills credentials from .env,
and stays open until you solve any CAPTCHA/2FA and log in successfully.
"""
import asyncio
import os
import sys
import shutil
from dotenv import load_dotenv
from patchright.async_api import async_playwright

# Setup paths
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

load_dotenv(os.path.join(backend_dir, ".env"))

# Clear proxy variables to ensure direct local IP connection
for key in ["MAERSK_PROXY_USER", "MAERSK_PROXY_PASS", "BRIGHTDATA_PROXY_USER", "BRIGHTDATA_PROXY_PASS", "BRIGHTDATA_PROXY_SERVER"]:
    os.environ[key] = ""

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


async def main():
    master_profile_dir = os.path.join(backend_dir, "chrome_profile_maersk")

    if "--reset" in sys.argv:
        print("[MAERSK] --reset flag passed. Clearing stale chrome profile...")
        if os.path.exists(master_profile_dir):
            try:
                shutil.rmtree(master_profile_dir)
                print("[MAERSK] Cleared stale profile successfully.")
            except Exception as e:
                print(f"[MAERSK] Note clearing profile: {e}")

    os.makedirs(master_profile_dir, exist_ok=True)

    # Clean lock files
    lock_files = ["SingletonLock", "lock", "SingletonCookie"]
    for root_dir, _, filenames in os.walk(master_profile_dir):
        for filename in filenames:
            if filename in lock_files:
                try:
                    os.remove(os.path.join(root_dir, filename))
                except Exception:
                    pass

    # Reload .env in case user just updated it
    load_dotenv(os.path.join(backend_dir, ".env"), override=True)
    username = os.getenv("MAERSK_USERNAME", "")
    password = os.getenv("MAERSK_PASSWORD", "")

    print("=" * 60)
    print(" [MAERSK HEADED LOGIN]")
    print(f" Profile Directory: {master_profile_dir}")
    print(f" Username: {username[:3]}***" if username else " Username: [Not set in .env]")
    print("=" * 60)

    playwright = await async_playwright().start()

    launch_kwargs = {
        "user_data_dir": master_profile_dir,
        "headless": False,
        "ignore_https_errors": True,
        "viewport": {"width": 1400, "height": 900},
        "args": [
            "--disable-blink-features=AutomationControlled",
            "--start-maximized",
            "--no-sandbox",
            "--disable-setuid-sandbox",
        ]
    }
    if sys.platform == "win32":
        launch_kwargs["channel"] = "chrome"

    print("[MAERSK] Launching Chrome...")
    try:
        context = await playwright.chromium.launch_persistent_context(**launch_kwargs)
    except Exception as e:
        if "channel" in launch_kwargs:
            print(f"[MAERSK] Launching with system Chrome failed ({e}). Falling back to bundled browser...")
            launch_kwargs.pop("channel", None)
            context = await playwright.chromium.launch_persistent_context(**launch_kwargs)
        else:
            raise e
    page = context.pages[0] if context.pages else await context.new_page()

    print("[MAERSK] Navigating to https://www.maersk.com/login ...")
    try:
        await page.goto("https://www.maersk.com/login", wait_until="domcontentloaded", timeout=45000)
    except Exception as e:
        print(f"[MAERSK] Initial navigation note: {e}")

    await page.wait_for_timeout(3000)

    # Attempt to accept cookies if visible
    try:
        cookie_btn = page.locator('#onetrust-accept-btn-handler, button:has-text("Allow all"), button:has-text("Accept All"), button:has-text("Essential only")').first
        if await cookie_btn.is_visible(timeout=3000):
            print("[MAERSK] Dismissing cookie banner...")
            await cookie_btn.click()
            await page.wait_for_timeout(1000)
    except Exception:
        pass

    # Try pre-filling credentials if username/password inputs are present
    try:
        if username and password:
            curr_url = page.url.lower()
            if "login" in curr_url or "auth" in curr_url:
                user_host = page.locator('#mc-input-username, input#signInName, input[name*="username" i]').first
                if await user_host.is_visible(timeout=3000):
                    print("[MAERSK] Pre-filling username...")
                    try:
                        inner_user = page.locator('#mc-input-username input').first
                        if await inner_user.is_visible(timeout=1000):
                            await inner_user.fill(username)
                        else:
                            await user_host.fill(username)
                    except:
                        await user_host.fill(username)

                pass_host = page.locator('#mc-input-password, input#password, input[type="password"]').first
                if await pass_host.is_visible(timeout=3000):
                    print("[MAERSK] Pre-filling password...")
                    try:
                        inner_pass = page.locator('#mc-input-password input').first
                        if await inner_pass.is_visible(timeout=1000):
                            await inner_pass.fill(password)
                        else:
                            await pass_host.fill(password)
                    except:
                        await pass_host.fill(password)

                # Try clicking submit
                submit_btn = page.locator('mc-button#button-submit, button#next, button[type="submit"]:has-text("Log in"), button:has-text("Sign in")').first
                if await submit_btn.is_visible(timeout=2000):
                    print("[MAERSK] Submitting login form...")
                    await submit_btn.click()
    except Exception as e:
        print(f"[MAERSK] Note during auto-fill: {e}")

    print("\n" + "=" * 60)
    print(" >>> CHROME IS NOW OPEN <<<")
    print(" Please complete any CAPTCHA, 2FA, or verification on screen.")
    print(" The script is monitoring the page and will automatically detect")
    print(" when you are logged in, or you can press Ctrl+C when done.")
    print("=" * 60 + "\n")

    # Monitor for login success
    logged_in = False
    for second in range(600):  # 10 minutes max
        await asyncio.sleep(1)
        curr_url = page.url.lower()

        # Check if redirected to hub, book, or dashboard, or logout button appears
        is_hub_or_book = ("login" not in curr_url and "auth" not in curr_url) and any(
            k in curr_url for k in ["hub", "book", "dashboard", "portal", "home", "maersk.com/tracking"]
        )

        has_logout = False
        try:
            logout_el = page.locator('text="Log out", text="Sign out", text="Log Out", text="Sign Out", a[href*="logout"]').first
            if await logout_el.is_visible(timeout=200):
                has_logout = True
        except:
            pass

        if is_hub_or_book or has_logout:
            print(f"\n[MAERSK SUCCESS] Login detected! Current URL: {page.url}")
            logged_in = True
            break

        if second % 15 == 14:
            print(f"[MAERSK] Waiting for login completion... ({600 - second - 1}s remaining)")

    if logged_in:
        print("[MAERSK] Waiting 5 seconds to ensure all session tokens and cookies are saved to disk...")
        await page.wait_for_timeout(5000)
        print("[MAERSK] Session successfully persisted to backend/chrome_profile_maersk!")
    else:
        print("[MAERSK] Login was not detected within timeout.")

    print("[MAERSK] Closing browser...")
    await context.close()
    await playwright.stop()
    print("[MAERSK] Done.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[MAERSK] Finished by user.")
