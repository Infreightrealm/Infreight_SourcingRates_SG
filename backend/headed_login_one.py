"""
Interactive Headed Login Helper for ONE (Ocean Network Express).
Opens Chrome using the persistent profile `backend/chrome_profile_one`,
navigates to ONE login, pre-fills credentials, and automatically clicks 'OK'
on any security policy popups (e.g. 'Enhancing Your Account Security').
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
for key in ["ONE_PROXY_USER", "ONE_PROXY_PASS", "BRIGHTDATA_PROXY_USER", "BRIGHTDATA_PROXY_PASS", "BRIGHTDATA_PROXY_SERVER"]:
    os.environ[key] = ""

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


async def main():
    master_profile_dir = os.path.join(backend_dir, "chrome_profile_one")

    if "--reset" in sys.argv:
        print("[ONE] --reset flag passed. Clearing stale chrome profile...")
        if os.path.exists(master_profile_dir):
            try:
                shutil.rmtree(master_profile_dir)
                print("[ONE] Cleared stale profile successfully.")
            except Exception as e:
                print(f"[ONE] Note clearing profile: {e}")

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

    load_dotenv(os.path.join(backend_dir, ".env"), override=True)
    username = os.getenv("ONE_USERNAME", "INFREIGHTSG")
    password = os.getenv("ONE_PASSWORD", "IFSGa2020")

    print("=" * 60)
    print(" [ONE HEADED LOGIN]")
    print(f" Profile Directory: {master_profile_dir}")
    print(f" Username: {username}")
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

    print("[ONE] Launching Chrome...")
    try:
        context = await playwright.chromium.launch_persistent_context(**launch_kwargs)
    except Exception as e:
        if "channel" in launch_kwargs:
            print(f"[ONE] Launching with system Chrome failed ({e}). Falling back to bundled browser...")
            launch_kwargs.pop("channel", None)
            context = await playwright.chromium.launch_persistent_context(**launch_kwargs)
        else:
            raise e
    page = context.pages[0] if context.pages else await context.new_page()

    login_url = "https://www.one-line.com/one-ecom/login"
    print(f"[ONE] Navigating to {login_url} ...")
    try:
        await page.goto(login_url, wait_until="domcontentloaded", timeout=45000)
    except Exception as e:
        print(f"[ONE] Initial navigation note: {e}")

    await page.wait_for_timeout(2000)

    # Pre-fill credentials if login inputs are present
    try:
        curr_url = page.url.lower()
        if "login" in curr_url or "auth" in curr_url:
            user_field = page.locator('input[name="userId"], input[id="userId"], input[name="username"]').first
            if await user_field.is_visible(timeout=3000):
                print("[ONE] Pre-filling userId...")
                await user_field.fill(username)

            pass_field = page.locator('input[name="password"], input[id="password"], input[type="password"]').first
            if await pass_field.is_visible(timeout=3000):
                print("[ONE] Pre-filling password...")
                await pass_field.fill(password)

            submit_btn = page.locator('button[type="submit"], button:has-text("Login"), button:has-text("Sign in")').first
            if await submit_btn.is_visible(timeout=2000):
                print("[ONE] Clicking Login submit...")
                await submit_btn.click()
    except Exception as e:
        print(f"[ONE] Note during login autofill: {e}")

    print("\n" + "=" * 60)
    print(" >>> CHROME IS NOW OPEN <<<")
    print(" Please complete any CAPTCHA, 2FA, or verification on screen.")
    print(" The script will also automatically click 'OK' on any")
    print(" 'Enhancing Your Account Security' popup that appears.")
    print("=" * 60 + "\n")

    # Monitor for login success and dismiss security popup
    logged_in = False
    for second in range(300):
        await asyncio.sleep(1)
        curr_url = page.url.lower()

        # Check and click "OK" or "Skip" on any popup
        try:
            dismissed = await page.evaluate('''() => {
                const bodyText = (document.body ? document.body.innerText || '' : '').toLowerCase();
                if (bodyText.includes('enhancing your account security') || bodyText.includes('password policy')) {
                    const buttons = Array.from(document.querySelectorAll('button, [role="button"], a'));
                    for (const b of buttons) {
                        const txt = (b.textContent || '').trim().toLowerCase();
                        if (txt === 'ok' || txt === 'okay' || txt === 'confirm') {
                            b.click();
                            return true;
                        }
                    }
                }
                return false;
            }''')
            if dismissed:
                print("[ONE] Automatically clicked OK on 'Enhancing Your Account Security' popup!")
        except Exception:
            pass

        # Check if redirected to quote booking or dashboard
        if "login" not in curr_url and "auth" not in curr_url and any(k in curr_url for k in ["price", "quote", "booking", "home", "dashboard"]):
            print(f"\n[ONE SUCCESS] Logged in successfully! URL: {page.url}")
            logged_in = True
            break

        if second % 15 == 14:
            print(f"[ONE] Waiting for login completion... ({300 - second - 1}s remaining)")

    if logged_in:
        print("[ONE] Waiting 5 seconds to ensure session cookies are saved...")
        await page.wait_for_timeout(5000)
        print("[ONE] Session successfully persisted to backend/chrome_profile_one!")
    else:
        print("[ONE] Login was not detected within timeout.")

    print("[ONE] Closing browser...")
    await context.close()
    await playwright.stop()
    print("[ONE] Done.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[ONE] Finished by user.")
