"""
Hapag-Lloyd Live Connector — Playwright automation.

Credentials read from env: HAPAG_LLOYD_USERNAME, HAPAG_LLOYD_PASSWORD
Never hardcode credentials.
"""
import os
import re
import asyncio
import random
import shutil
import uuid
import subprocess
from datetime import date, datetime, timedelta
from patchright.async_api import async_playwright
from typing import Optional

from models.schemas import RateSearchRequest, QuoteSchema, CarrierResultStatus, ChargeCategory
from services.charge_classifier import classify_charge
from services.normalizer import normalize_quote
from carriers.base_connector import BaseCarrierConnector
from services.port_manager import get_cached_carrier_port, set_cached_carrier_port, resolve_port_for_carrier


class HapagLloydConnector(BaseCarrierConnector):
    carrier_code = "HAPAG_LLOYD"
    carrier_name = "Hapag-Lloyd"
    QUOTE_URL = "https://www.hapag-lloyd.com/en/home.html"

    CONTAINER_TYPE_MAP = {
        "DRY 20": "20' General Purpose",
        "DRY 40": "40' General Purpose",
        "DRY 40H": "40' General Purpose High Cube",
    }

    def __init__(self):
        super().__init__()
        self.playwright = None
        self._all_quotes = []
        self.master_profile_dir = None
        self.temp_profile_dir = None
        self.is_login_successful = False

    async def _init_browser(self):
        is_prod = os.name != "nt"
        if is_prod:
            os.environ["DISPLAY"] = ":102"  # Hapag-Lloyd dedicated virtual display
        
        self.playwright = await async_playwright().start()

        # ── Persistent profile setup (similar to Maersk / CMA CGM) ──────────────
        persistent_dir = os.getenv("PERSISTENT_PROFILES_DIR")
        if persistent_dir:
            self.master_profile_dir = os.path.join(persistent_dir, "chrome_profile_hapag")
        else:
            self.master_profile_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chrome_profile_hapag")

        if os.getenv("RESET_CHROME_PROFILES", "").lower() == "true":
            print(f"[HAPAG] [WARN] RESET_CHROME_PROFILES active. Clearing master profile: {self.master_profile_dir}")
            if os.path.exists(self.master_profile_dir):
                try:
                    shutil.rmtree(self.master_profile_dir)
                    print("[HAPAG] Master profile cleared.")
                except Exception as e:
                    print(f"[HAPAG] Failed to clear master profile: {e}")

        # Create unique temp profile copy for this session
        unique_id = str(uuid.uuid4())[:8]
        if persistent_dir:
            self.temp_profile_dir = os.path.join(persistent_dir, f"chrome_profile_hapag_tmp_{unique_id}")
        else:
            self.temp_profile_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), f"chrome_profile_hapag_tmp_{unique_id}")

        print(f"[HAPAG] Creating temp isolated profile: {self.temp_profile_dir}")
        if os.path.exists(self.master_profile_dir):
            try:
                shutil.copytree(self.master_profile_dir, self.temp_profile_dir, dirs_exist_ok=True)
                lock_files = ["SingletonLock", "lock", "SingletonCookie"]
                for root_dir, _, filenames in os.walk(self.temp_profile_dir):
                    for filename in filenames:
                        if filename in lock_files:
                            try:
                                os.remove(os.path.join(root_dir, filename))
                            except Exception:
                                pass
                print("[HAPAG] Master profile copied with lock files cleaned.")
            except Exception as e:
                print(f"[HAPAG] Warning: could not copy master profile ({e}). Starting fresh.")
        else:
            print("[HAPAG] No master profile found. Initialising fresh profile.")
            os.makedirs(self.temp_profile_dir, exist_ok=True)

        # ── Proxy setup ──────────────────────────────────────────────────────────
        proxy_user = os.getenv("BRIGHTDATA_PROXY_USER")
        proxy_pass = os.getenv("BRIGHTDATA_PROXY_PASS")
        proxy_server = os.getenv("BRIGHTDATA_PROXY_SERVER", "http://brd.superproxy.io:22225")
        
        # Check carrier-specific proxies
        if os.getenv("HAPAG_PROXY_USER"):
            proxy_user = os.getenv("HAPAG_PROXY_USER")
            proxy_pass = os.getenv("HAPAG_PROXY_PASS")
            if os.getenv("HAPAG_PROXY_SERVER"):
                proxy_server = os.getenv("HAPAG_PROXY_SERVER")

        proxy_config = None
        if proxy_user and proxy_pass:
            if "-session-" not in proxy_user:
                session_id = str(uuid.uuid4())[:8]
                proxy_user = f"{proxy_user}-session-{session_id}"
                
            proxy_config = {
                "server": proxy_server,
                "username": proxy_user,
                "password": proxy_pass,
            }
            print(f"[HAPAG] [PROXY] Routing through ISP residential proxy ({proxy_server}) with session pinning ({proxy_user.split('-session-')[-1]})...")
        else:
            print("[HAPAG] [INFO] No proxy configured. Running on local IP directly.")

        # ── Browser Launch Arguments ─────────────────────────────────────────────
        args = [
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-infobars",
            "--disable-component-update",
            "--disable-default-apps",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            "--disable-ipc-flooding-protection",
            "--force-color-profile=srgb",
            "--use-gl=desktop",
            "--window-size=1920,1080",
            "--start-maximized",
        ]

        # On Windows: use the REAL Chrome binary to avoid fingerprint detection.
        chrome_exe = None
        if not is_prod:
            chrome_candidates = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
            ]
            for path in chrome_candidates:
                if os.path.exists(path):
                    chrome_exe = path
                    break

        executable_path = None
        if is_prod:
            executable_path = "/usr/bin/google-chrome-stable"
            if not os.path.exists(executable_path):
                executable_path = None
                print("[HAPAG] [WARN] google-chrome-stable not found. Falling back to bundled Chromium.")
            else:
                print(f"[HAPAG] Using real Chrome: {executable_path}")
        elif chrome_exe:
            executable_path = chrome_exe
            print(f"[HAPAG] Using local real Chrome: {chrome_exe}")

        self.context = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=self.temp_profile_dir,
            headless=False,  # Headless mode must be False for VNC rendering
            executable_path=executable_path,
            slow_mo=random.randint(80, 150),
            args=args,
            proxy=proxy_config,
            no_viewport=True,
            ignore_default_args=["--enable-automation"],
        )

        self.page = self.context.pages[0] if self.context.pages else await self.context.new_page()
        
        # Custom timeouts
        self.page.set_default_timeout(45000)
        self.page.set_default_navigation_timeout(60000)

    async def _human_delay(self, min_ms=500, max_ms=1500):
        await self.page.wait_for_timeout(random.randint(min_ms, max_ms))

    async def login(self) -> bool:
        try:
            await self._init_browser()
            print("[HAPAG] Navigating to home page...")
            await self.page.goto(self.QUOTE_URL)
            try:
                await self.page.wait_for_load_state("domcontentloaded", timeout=12000)
            except:
                pass
            await self._human_delay(1500, 2500)

            # Accept cookies banner if present
            try:
                accept_selectors = [
                    '#accept-recommended-btn-handler',
                    '#onetrust-accept-btn-handler',
                    'button:has-text("Accept All")',
                    'button:has-text("Accept")',
                    'button:has-text("Agree")',
                    '.cookie-accept-button'
                ]
                for selector in accept_selectors:
                    btn = self.page.locator(selector).first
                    if await btn.is_visible(timeout=1000):
                        print(f"[HAPAG] Accepting cookies: Clicking {selector}")
                        await btn.click()
                        await self._human_delay(800, 1500)
                        break
            except Exception:
                pass

            # Check if already logged in (look for sign-out or profile buttons)
            is_logged_in = False
            try:
                signout_loc = self.page.locator('a:has-text("Log out"), button:has-text("Log out"), button:has-text("Sign out")')
                if await signout_loc.count() > 0 and await signout_loc.first.is_visible(timeout=1000):
                    is_logged_in = True
                    print("[HAPAG] Already logged in.")
            except:
                pass

            # Expand Quote Sidebar
            print("[HAPAG] Expanding 'Quote' sidebar menu...")
            quote_sidebar = self.page.locator('span:has-text("Quote"), li:has-text("Quote"), a:has-text("Quote")').first
            await quote_sidebar.scroll_into_view_if_needed()
            await quote_sidebar.click(force=True)
            await self._human_delay(1000, 1800)

            # Click 'New Quote'
            print("[HAPAG] Clicking 'New Quote' sub-menu...")
            new_quote_btn = self.page.locator('a:has-text("New Quote"), span:has-text("New Quote")').first
            await new_quote_btn.scroll_into_view_if_needed()
            await new_quote_btn.click(force=True)
            await self._human_delay(3000, 5000)

            # Wait for either the login form (credentials required) or the Quick Quote page (already logged in) to settle
            print("[HAPAG] Waiting for page to settle (up to 90s) to detect if login is required or already logged in...")
            is_logged_in = False
            settle_start_time = asyncio.get_event_loop().time()
            settled = False
            
            while asyncio.get_event_loop().time() - settle_start_time < 90:
                # Check for login selectors
                login_selectors = [
                    'input#email',
                    'input#signInName',
                    'input[type="email"]',
                    'input[name*="username" i]',
                    'input[name*="email" i]',
                    'input[placeholder*="Email" i]',
                    'input[placeholder*="E-mail" i]'
                ]
                found_login = False
                for sel in login_selectors:
                    try:
                        loc = self.page.locator(sel).first
                        if await loc.is_visible(timeout=300):
                            print(f"[HAPAG] Login field detected: {sel}")
                            found_login = True
                            break
                    except:
                        pass
                
                if found_login:
                    is_logged_in = False
                    settled = True
                    break

                # Check for quick quote form selectors (already logged in)
                quote_selectors = [
                    'input[placeholder*="Start" i]',
                    '[id*="start" i] input',
                    '[class*="start" i] input',
                    'input[placeholder*="Origin" i]'
                ]
                found_quote = False
                for sel in quote_selectors:
                    try:
                        loc = self.page.locator(sel).first
                        if await loc.is_visible(timeout=300):
                            print(f"[HAPAG] Quick Quote form field detected: {sel}")
                            found_quote = True
                            break
                    except:
                        pass

                if found_quote:
                    is_logged_in = True
                    settled = True
                    break

                # Also print a status update every 5 seconds
                elapsed = int(asyncio.get_event_loop().time() - settle_start_time)
                if elapsed > 0 and elapsed % 5 == 0:
                    print(f"[HAPAG] Still waiting for page to settle... (elapsed {elapsed}s). Solve Cloudflare in VNC if prompted.")
                
                await asyncio.sleep(1)

            if not settled:
                print("[HAPAG] Timeout waiting for page to settle. Proceeding under assumption that credentials might be needed.")
                is_logged_in = False

            if not is_logged_in:
                # Need to log in
                print("[HAPAG] Credentials required. Automating login form...")
                
                email = os.getenv("HAPAG_LLOYD_USERNAME")
                if not email or not email.strip():
                    email = "BOOKINGSG@IN-FREIGHT.COM"
                else:
                    email = email.strip()

                password = os.getenv("HAPAG_LLOYD_PASSWORD")
                if not password or not password.strip():
                    password = "IFSGb2020"
                else:
                    password = password.strip()

                mask_pass = f"{password[:2]}***{password[-2:]}" if len(password) > 4 else "***"
                print(f"[HAPAG] Login profile setup: email='{email}', password='{mask_pass}' (length: {len(password)})")

                # Define locator lists for the fields
                email_selectors = [
                    'input#email',
                    'input#signInName',
                    'input[type="email"]',
                    'input[name*="username" i]',
                    'input[name*="email" i]',
                    'input[placeholder*="Email" i]',
                    'input[placeholder*="E-mail" i]'
                ]
                
                email_input = None
                for sel in email_selectors:
                    try:
                        loc = self.page.locator(sel).first
                        if await loc.is_visible(timeout=1000):
                            email_input = loc
                            print(f"[HAPAG] Email input located using selector: {sel}")
                            break
                    except:
                        pass
                
                if not email_input:
                    email_input = self.page.locator('input[type="email"], input[type="text"]').first
                    print("[HAPAG] Fallback to general input for email.")

                await email_input.scroll_into_view_if_needed()
                await email_input.click()  # Click to focus the email box
                await self._human_delay(300, 600)
                await email_input.press("Control+A")
                await email_input.press("Backspace")
                await email_input.fill("")
                await self._human_delay(200, 400)
                await email_input.type(email, delay=random.randint(60, 120))
                await self._human_delay(500, 1000)

                password_selectors = [
                    'input#password',
                    'input[type="password"]',
                    'input[name*="password" i]'
                ]
                
                password_input = None
                for sel in password_selectors:
                    try:
                        loc = self.page.locator(sel).first
                        if await loc.is_visible(timeout=1000):
                            password_input = loc
                            print(f"[HAPAG] Password input located using selector: {sel}")
                            break
                    except:
                        pass

                if not password_input:
                    password_input = self.page.locator('input[type="password"]').first
                    print("[HAPAG] Fallback to standard password input.")

                await password_input.scroll_into_view_if_needed()
                await password_input.click()  # Click to focus the password box
                await self._human_delay(300, 600)
                await password_input.press("Control+A")
                await password_input.press("Backspace")
                await password_input.fill("")
                await self._human_delay(200, 400)
                await password_input.type(password, delay=random.randint(60, 120))
                await self._human_delay(1000, 1800)

                submit_selectors = [
                    'button#next',
                    'button#logIn',
                    'button:has-text("Log in")',
                    'button[type="submit"]',
                    'button:has-text("Sign In")',
                    'input[type="submit"]'
                ]
                
                submit_btn = None
                for sel in submit_selectors:
                    try:
                        loc = self.page.locator(sel).first
                        if await loc.is_visible(timeout=1000):
                            submit_btn = loc
                            print(f"[HAPAG] Submit button located using selector: {sel}")
                            break
                    except:
                        pass

                if not submit_btn:
                    submit_btn = self.page.locator('button:has-text("Log in"), button[type="submit"], button:has-text("Sign In")').first
                    print("[HAPAG] Fallback to standard login/submit button.")

                await submit_btn.scroll_into_view_if_needed()
                await submit_btn.click()
                print("[HAPAG] Login form submitted. Waiting for page redirect to Quick Quote page...")
                try:
                    await self.page.wait_for_load_state("domcontentloaded", timeout=10000)
                except:
                    pass
                await self._human_delay(2000, 4000)

            # Confirm quick quotes form is displayed
            try:
                print("[HAPAG] Confirming Quick Quote form loading...")
                quote_selectors = [
                    'text="Start Location"',
                    'text="End Location"',
                    'text="New Quote"',
                    'input[placeholder*="Start" i]',
                    'div:has-text("Start Location")'
                ]
                
                form_loaded = False
                confirm_start_time = asyncio.get_event_loop().time()
                
                # Poll for up to 45 seconds for redirect/loading of the Quote form
                while asyncio.get_event_loop().time() - confirm_start_time < 45:
                    for sel in quote_selectors:
                        try:
                            loc = self.page.locator(sel).first
                            if await loc.is_visible():
                                print(f"[HAPAG] Confirmed Quick Quote page loaded using: {sel}")
                                form_loaded = True
                                break
                        except:
                            pass
                    if form_loaded:
                        break
                    await asyncio.sleep(1)
                
                if not form_loaded:
                    # Try a fallback general wait for any input
                    try:
                        await self.page.wait_for_selector('input', timeout=5000)
                        print("[HAPAG] Found inputs. Assuming form loaded.")
                        form_loaded = True
                    except:
                        pass

                if form_loaded:
                    print("[HAPAG] Quick Quote form successfully verified.")
                    self.is_login_successful = True
                    return True
                else:
                    raise Exception("No confirming Quick Quote page elements were visible after 45s.")
                    
            except Exception as e:
                print(f"[HAPAG] [ERROR] Quick Quote form verification failed: {e}")
                await self.page.screenshot(path="hapag_login_fail.png")
                return False

        except Exception as e:
            print(f"[HAPAG] [ERROR] Login process crashed: {e}")
            await self.page.screenshot(path="hapag_login_crash.png")
            return False

    async def _select_hapag_dropdown_option(self, label: str, locode: str, cached_name: Optional[str] = None) -> bool:
        """
        Robustly selects options from Hapag-Lloyd custom dropdown lists.
        Types the locode, waits for list suggestions, and selects the matching suggestion.
        """
        try:
            print(f"[HAPAG] Selecting dropdown option for {label}: '{locode}'...")
            await self.page.wait_for_timeout(1500)
            
            # Locate dropdown overlay suggestions
            suggestions = self.page.locator('[class*="suggestion" i], [class*="dropdown" i] li, [class*="option" i]')
            count = await suggestions.count()
            print(f"[HAPAG] Suggestions visible: {count}")
            
            if count == 0:
                # Try generic selectors
                suggestions = self.page.locator('ul[role="listbox"] li, .el-select-dropdown__item')
                count = await suggestions.count()
                print(f"[HAPAG] Suggestion retry count: {count}")

            # Match criteria: locode or cached_name
            target_match = locode.upper()
            
            # Scroll and scan suggestions
            for idx in range(count):
                item = suggestions.nth(idx)
                item_text = (await item.inner_text()).strip().upper()
                print(f"  Suggestion {idx}: '{item_text}'")
                
                if target_match in item_text or (cached_name and cached_name.upper() in item_text):
                    print(f"[HAPAG] [MATCH] Found suggestion at index {idx}: '{item_text}'. Clicking...")
                    await item.click()
                    await self._human_delay(800, 1500)
                    return True

            # If no suggestion matched, click the first suggestion as fallback
            if count > 0:
                print(f"[HAPAG] No exact suggestion matched '{target_match}'. Falling back to first available option.")
                await suggestions.first.click()
                await self._human_delay(800, 1500)
                return True

            print(f"[HAPAG] Dropdown suggestions did not appear for {label}.")
            return False
        except Exception as e:
            print(f"[HAPAG] Dropdown selection error for {label}: {e}")
            return False

    async def search_quotes(self, request: RateSearchRequest) -> CarrierResultStatus:
        try:
            print("[HAPAG] Starting Quick Quote search...")
            
            # --- START LOCATION (ORIGIN) ---
            origin_locode = resolve_port_for_carrier(request.origin, "hapag")
            if not origin_locode or len(origin_locode) != 5:
                origin_locode = request.origin[:5].upper()

            origin_cached = get_cached_carrier_port("hapag", origin_locode)
            print(f"[HAPAG] Filling Start Location: '{origin_locode}' (cached: '{origin_cached}')")

            # Find Start Location text input
            start_selectors = [
                'div:has-text("Start Location") input',
                'input[placeholder*="Start" i]',
                'input[placeholder*="Origin" i]',
                'input[type="text"]'  # Fallback to first text input
            ]
            
            start_field = None
            for sel in start_selectors:
                try:
                    loc = self.page.locator(sel).first
                    if await loc.is_visible(timeout=1000):
                        start_field = loc
                        print(f"[HAPAG] Start Location input found using selector: {sel}")
                        break
                except:
                    pass
            
            if not start_field:
                # Absolute fallback: first visible input
                start_field = self.page.locator('input').first
                print("[HAPAG] Fallback to first general input on page.")

            await start_field.scroll_into_view_if_needed()
            await start_field.click()
            await self._human_delay(300, 600)
            await start_field.press("Control+A")
            await start_field.press("Backspace")
            await start_field.fill("")
            await self._human_delay(200, 400)
            await start_field.type(origin_locode, delay=35)
            await self._human_delay(1500, 2500)
            
            if not await self._select_hapag_dropdown_option("Start Location", origin_locode, origin_cached):
                print("[HAPAG] Warning: Origin suggestion selection failed.")

            # --- END LOCATION (DESTINATION) ---
            dest_locode = resolve_port_for_carrier(request.destination, "hapag")
            if not dest_locode or len(dest_locode) != 5:
                dest_locode = request.destination[:5].upper()

            dest_cached = get_cached_carrier_port("hapag", dest_locode)
            print(f"[HAPAG] Filling End Location: '{dest_locode}' (cached: '{dest_cached}')")

            # Find End Location text input
            end_selectors = [
                'div:has-text("End Location") input',
                'input[placeholder*="End" i]',
                'input[placeholder*="Destination" i]',
                'input[type="text"]'  # Fallback to second text input
            ]
            
            end_field = None
            for sel in end_selectors:
                try:
                    if sel == 'input[type="text"]':
                        loc = self.page.locator(sel).nth(1)
                    else:
                        loc = self.page.locator(sel).first
                        
                    if await loc.is_visible(timeout=1000):
                        end_field = loc
                        print(f"[HAPAG] End Location input found using selector: {sel}")
                        break
                except:
                    pass
            
            if not end_field:
                # Absolute fallback: second visible input
                end_field = self.page.locator('input').nth(1)
                print("[HAPAG] Fallback to second general input on page.")

            await end_field.scroll_into_view_if_needed()
            await end_field.click()
            await self._human_delay(300, 600)
            await end_field.press("Control+A")
            await end_field.press("Backspace")
            await end_field.fill("")
            await self._human_delay(200, 400)
            await end_field.type(dest_locode, delay=35)
            await self._human_delay(1500, 2500)

            if not await self._select_hapag_dropdown_option("End Location", dest_locode, dest_cached):
                print("[HAPAG] Warning: Destination suggestion selection failed.")

            # --- CONTAINER TYPE ---
            hapag_container = self.CONTAINER_TYPE_MAP.get(request.container_type)
            if not hapag_container:
                print(f"[HAPAG] Container type {request.container_type} not mapped. Using default 40' GP High Cube.")
                hapag_container = "40' General Purpose High Cube"

            print(f"[HAPAG] Mapped container to choose: '{hapag_container}'")
            
            # If the user selected 40HC (which is the default 40' GP High Cube), we don't need to change it
            if request.container_type != "DRY 40H":
                try:
                    container_box = self.page.locator('input[placeholder*="Container" i], [id*="container" i] input, label:has-text("Container Type") + div input').first
                    await container_box.click()
                    await self._human_delay(1000, 1800)
                    
                    # Choose option containing container type name
                    option = self.page.locator(f'[class*="option" i]:has-text("{hapag_container}"), li:has-text("{hapag_container}")').first
                    if await option.is_visible(timeout=2000):
                        await option.click()
                        print(f"[HAPAG] Container type selected successfully: {hapag_container}")
                except Exception as container_err:
                    print(f"[HAPAG] Container type selection failed: {container_err}")

            # --- CONTAINER QUANTITY ---
            print(f"[HAPAG] Setting Container Quantity: {request.container_quantity}")
            try:
                qty_box = self.page.locator('input[placeholder*="Quantity" i], [id*="quantity" i] input, label:has-text("Quantity") + div input').first
                await qty_box.click()
                await qty_box.fill("")
                await qty_box.type(str(request.container_quantity), delay=50)
                await self._human_delay(500, 1000)
            except Exception as qty_err:
                print(f"[HAPAG] Quantity fill failed: {qty_err}")

            # --- CARGO WEIGHT ---
            weight_val = max(int(request.weight_per_container_kg), 5000)
            print(f"[HAPAG] Setting Cargo Weight: {weight_val} kg")
            try:
                weight_box = self.page.locator('input[placeholder*="Weight" i], [id*="weight" i] input, label:has-text("Weight") + div input').first
                await weight_box.click()
                await weight_box.fill("")
                await weight_box.type(str(weight_val), delay=50)
                await self._human_delay(500, 1000)
            except Exception as weight_err:
                print(f"[HAPAG] Weight fill failed: {weight_err}")

            # --- SEARCH ---
            print("[HAPAG] Clicking 'Search' (orange box)...")
            try:
                search_btn = self.page.locator('button:has-text("Search"), button[type="submit"]:has-text("Search"), button.orange').first
                if await search_btn.count() == 0:
                    search_btn = self.page.locator('button:has-text("Get Quote"), button:has-text("Find Rates")').first
                
                await search_btn.scroll_into_view_if_needed()
                await search_btn.click()
                print("[HAPAG] Quote search submitted!")
                try:
                    await self.page.wait_for_load_state("domcontentloaded", timeout=12000)
                except:
                    pass
                await self._human_delay(5000, 8000)
            except Exception as submit_err:
                print(f"[HAPAG] Submit failed: {submit_err}")
                await self.page.screenshot(path="hapag_submit_fail.png")
                return CarrierResultStatus.UNKNOWN_ERROR

            # Results detection
            try:
                # Wait for any schedule route cards, price tags, or results element
                await self.page.wait_for_selector('[class*="route" i], [class*="result" i], [class*="sailing" i], [class*="price" i], button:has-text("Book"), button:has-text("Select")', timeout=30000)
                print("[HAPAG] Sourced quotes successfully.")
                return CarrierResultStatus.AVAILABLE_QUOTES_FOUND
            except Exception:
                page_text = await self.page.inner_text('body')
                if 'no result' in page_text.lower() or 'no schedule' in page_text.lower() or 'no rate' in page_text.lower():
                    print("[HAPAG] Explicitly reported: No quotes available.")
                    return CarrierResultStatus.NO_QUOTES_AVAILABLE
                
                print("[HAPAG] Results wait timeout.")
                await self.page.screenshot(path="hapag_results_fail.png")
                return CarrierResultStatus.NO_QUOTES_AVAILABLE

        except Exception as e:
            print(f"[HAPAG] Sourcing form fill failed: {e}")
            await self.page.screenshot(path="hapag_form_crash.png")
            return CarrierResultStatus.UNKNOWN_ERROR

    async def extract_quote_list(self) -> list[dict]:
        try:
            # Sift the schedule elements on Hapag-Lloyd results page
            # Look for divs representing sailings cards
            cards_sel = '[class*="route" i], [class*="result-card" i], div.schedules-card, div:has(button:has-text("Select")):has-text("USD")'
            cards = self.page.locator(cards_sel)
            count = await cards.count()
            
            if count == 0:
                # Generic container blocks
                cards = self.page.locator('.card, .row:has-text("USD")')
                count = await cards.count()

            print(f"[HAPAG] Found {count} total quote cards.")
            self._all_quotes = []

            for idx in range(count):
                card = cards.nth(idx)
                try:
                    await card.scroll_into_view_if_needed()
                except:
                    pass

                text = await card.inner_text()
                text_lower = text.lower()

                # Basic validation: Skip cards that are unrelated header segments
                if "departure" not in text_lower and "eta" not in text_lower and "transit" not in text_lower and "usd" not in text_lower:
                    continue

                # 1. Parse departure/arrival dates
                # Pattern: matches date formats like "18-May-2026", "2026-05-18", or "May 18, 2026"
                date_pattern = r'\d{1,2}-[A-Za-z]{3}-\d{4}|\d{4}-\d{2}-\d{2}|[A-Za-z]{3}\s+\d{1,2},\s+\d{4}'
                found_dates = re.findall(date_pattern, text)
                
                etd_str = found_dates[0] if len(found_dates) > 0 else None
                eta_str = found_dates[1] if len(found_dates) > 1 else None

                etd = None
                if etd_str:
                    try:
                        etd = datetime.strptime(etd_str, "%d-%b-%Y").date()
                    except:
                        try:
                            etd = datetime.strptime(etd_str, "%Y-%m-%d").date()
                        except:
                            pass

                eta = None
                if eta_str:
                    try:
                        eta = datetime.strptime(eta_str, "%d-%b-%Y").date()
                    except:
                        try:
                            eta = datetime.strptime(eta_str, "%Y-%m-%d").date()
                        except:
                            pass

                # 2. Transit time
                tt_match = re.search(r'(\d+)\s*[Dd]ays?', text)
                transit_time = int(tt_match.group(1)) if tt_match else None
                if etd and eta and transit_time is None:
                    transit_time = (eta - etd).days

                # 3. Service / Vessel info
                service_match = re.search(r'(?:Service|Voyage|Vessel)\s+(\S+)', text)
                service = service_match.group(1).strip() if service_match else "Hapag Service"
                
                vessel_match = re.search(r'Vessel\s+(.+?)(?:\r|\n|$)', text)
                vessel = vessel_match.group(1).strip() if vessel_match else "Hapag Vessel"

                # Check if sold out
                is_sold_out = "sold out" in text_lower or "no availability" in text_lower or "unavailable" in text_lower

                # 4. Total Price
                price = 0.0
                if not is_sold_out:
                    price_match = re.search(r'(\d[\d,]*)\s*USD', text, re.IGNORECASE)
                    if not price_match:
                        price_match = re.search(r'\$\s*(\d[\d,]*)', text)
                    
                    if price_match:
                        price = float(price_match.group(1).replace(",", ""))

                self._all_quotes.append({
                    "index": idx,
                    "etd": etd.isoformat() if etd else None,
                    "eta": eta.isoformat() if eta else None,
                    "transit_time_days": transit_time,
                    "service_name": service,
                    "vessel": vessel,
                    "total_price": price,
                    "currency": "USD",
                    "card_locator": card,
                    "is_sold_out": is_sold_out,
                    "source": "carrier_portal",
                    "carrier_code": self.carrier_code
                })

            return self._all_quotes
        except Exception as e:
            print(f"[HAPAG] Quotes sifting error: {e}")
            return []

    async def open_price_breakdown(self, quote_ref: dict) -> bool:
        """
        Attempts to click detail/charges buttons to open the breakdown panel.
        For sold-out quotes, immediately return False.
        """
        if quote_ref.get("is_sold_out"):
            return False
            
        try:
            card = quote_ref["card_locator"]
            await card.scroll_into_view_if_needed()
            await self._human_delay(400, 800)
            
            # Locate "Details", "Price breakdown", "Charges" buttons
            details_btn = card.locator('button:has-text("Details"), button:has-text("Charges"), a:has-text("Charges")').first
            if await details_btn.count() > 0 and await details_btn.is_visible():
                await details_btn.click()
                await self._human_delay(1500, 2500)
                return True
            return False
        except Exception as e:
            print(f"[HAPAG] Pricing drawer open failed: {e}")
            return False

    async def extract_charge_breakdown(self) -> list[dict]:
        """
        Extract detailed surcharge list items from the open pricing drawer.
        """
        charges = []
        try:
            # Locate breakdown table rows or lines
            rows = self.page.locator('[class*="charge" i], [class*="breakdown" i] tr, .drawer-row')
            count = await rows.count()
            
            for idx in range(count):
                row_text = await rows.nth(idx).inner_text()
                # Extract line item name and amount
                # Pattern: Basic Freight 850.00 USD
                parts = [p.strip() for p in row_text.splitlines() if p.strip()]
                if len(parts) >= 2:
                    name = parts[0]
                    amount_str = parts[-1]
                    
                    price_match = re.search(r'([\d,]+\.?\d*)', amount_str)
                    if price_match:
                        amount = float(price_match.group(1).replace(",", ""))
                        currency = "USD"
                        if "EUR" in amount_str.upper(): currency = "EUR"
                        elif "SGD" in amount_str.upper(): currency = "SGD"
                        
                        charges.append({
                            "name": name,
                            "amount": amount,
                            "currency": currency
                        })
            return charges
        except Exception as e:
            print(f"[HAPAG] Surcharge details extraction error: {e}")
            return []

    async def normalize_result(self, raw_quote: dict, raw_charges: list[dict]) -> QuoteSchema:
        """
        Normalize raw Hapag-Lloyd quotes into unified QuoteSchema.
        """
        basic_ocean_freight = 0.0
        included_freight_surcharges = []
        excluded_charges = []
        
        from models.schemas import ChargeSchema
        from services.normalizer import classify_and_organize_charges, calculate_final_freight_value
        
        # Organize and classify surcharge items
        organized = classify_and_organize_charges(raw_charges)
        basic_ocean_freight = organized["basic_ocean_freight"]
        included_freight_surcharges = organized["included_freight_surcharges"]
        excluded_charges = organized["excluded_charges"]
        uncertain_charges = organized["uncertain_charges"]
        
        final_value = calculate_final_freight_value(organized["all_classified"])
        
        # Fallback to total price if no charges breakdown drawer was found
        if final_value == 0.0 and raw_quote.get("total_price"):
            final_value = raw_quote["total_price"]
            
        vessel = raw_quote.get("vessel", "Hapag Vessel")
        if raw_quote.get("is_sold_out"):
            vessel = f"{vessel} (Sold out)"

        return QuoteSchema(
            etd=raw_quote.get("etd"),
            eta=raw_quote.get("eta"),
            transit_time_days=raw_quote.get("transit_time_days"),
            service_name=raw_quote.get("service_name"),
            vessel=vessel,
            currency="USD",
            basic_ocean_freight=basic_ocean_freight,
            included_freight_surcharges=included_freight_surcharges,
            excluded_charges=excluded_charges,
            uncertain_charges=uncertain_charges,
            final_freight_value=round(final_value, 2),
            source="carrier_portal",
            raw_reference=f"HAPAG-{raw_quote.get('index', 0)}"
        )

    async def close(self):
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.playwright:
                await self.playwright.stop()
        except:
            pass
            
        # Copy temporary profile back to master to persist login sessions
        if self.temp_profile_dir and self.master_profile_dir and self.is_login_successful:
            try:
                print("[HAPAG] Syncing temp profile back to master...")
                shutil.copytree(self.temp_profile_dir, self.master_profile_dir, dirs_exist_ok=True)
                print("[HAPAG] Master profile updated successfully.")
            except Exception as e:
                print(f"[HAPAG] Warning: master profile sync failed: {e}")
                
        # Clean up temporary profiles
        if self.temp_profile_dir and os.path.exists(self.temp_profile_dir):
            try:
                shutil.rmtree(self.temp_profile_dir)
            except:
                pass
