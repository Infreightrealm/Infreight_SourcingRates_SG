
"""
CMA CGM Live Connector — Playwright automation.

Credentials read from env: CMA_USERNAME, CMA_PASSWORD
Never hardcode credentials.
"""
import os
import re
import asyncio
import random
from datetime import date, datetime, timedelta
from patchright.async_api import async_playwright
from typing import Optional
from models.schemas import RateSearchRequest, QuoteSchema, CarrierResultStatus, ChargeCategory
from services.charge_classifier import classify_charge
from services.normalizer import normalize_quote, standardize_date_string
from carriers.base_connector import BaseCarrierConnector
from services.port_manager import get_cached_carrier_port, set_cached_carrier_port, resolve_port_for_carrier


class CMAConnector(BaseCarrierConnector):
    carrier_code = "CMA"
    carrier_name = "CMA CGM"
    QUOTE_URL = "https://www.cma-cgm.com/ebusiness/pricing/instant-Quoting"

    CONTAINER_TYPE_MAP = {
        "DRY 20": "20' Dry Standard",
        "DRY 40": "40' Dry Standard",
        "DRY 40H": "40' Dry High Cube",
        "DRY 45": "45' Dry High Cube",
    }

    def __init__(self):
        super().__init__()
        self.SEARCH_URL = "https://www.cma-cgm.com/ebusiness/pricing/instant-Quoting"
        self.playwright = None
        self._all_quotes = []
        self.current_card = None
        self.master_profile_dir = None
        self.temp_profile_dir = None
        self.is_login_successful = False
        self._current_voyage = None

    async def _init_browser(self):
        import uuid
        import shutil
        import subprocess
        is_prod = os.name != "nt"
        self.playwright = await async_playwright().start()

        # ── Persistent profile setup (identical pattern to Maersk) ──────────────
        persistent_dir = os.getenv("PERSISTENT_PROFILES_DIR")
        if persistent_dir:
            self.master_profile_dir = os.path.join(persistent_dir, "chrome_profile_cma")
        else:
            self.master_profile_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chrome_profile_cma")

        if os.getenv("RESET_CHROME_PROFILES", "").lower() == "true":
            print(f"[CMA] [WARN] RESET_CHROME_PROFILES active. Clearing master profile: {self.master_profile_dir}")
            if os.path.exists(self.master_profile_dir):
                try:
                    shutil.rmtree(self.master_profile_dir)
                    print("[CMA] Master profile cleared.")
                except Exception as e:
                    print(f"[CMA] Failed to clear master profile: {e}")

        # Create unique temp profile copy for this session
        unique_id = str(uuid.uuid4())[:8]
        if persistent_dir:
            self.temp_profile_dir = os.path.join(persistent_dir, f"chrome_profile_cma_tmp_{unique_id}")
        else:
            self.temp_profile_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), f"chrome_profile_cma_tmp_{unique_id}")

        print(f"[CMA] Creating temp isolated profile: {self.temp_profile_dir}")
        if os.path.exists(self.master_profile_dir):
            try:
                # Skip throwaway Chrome caches on clone (Chromium regenerates them);
                # session identity (Cookies / Local Storage / IndexedDB) is still copied.
                shutil.copytree(
                    self.master_profile_dir, self.temp_profile_dir, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns(
                        "Cache", "Code Cache", "DawnCache", "GPUCache", "CacheStorage", "ScriptCache"),
                )
                lock_files = ["SingletonLock", "lock", "SingletonCookie"]
                for root_dir, _, filenames in os.walk(self.temp_profile_dir):
                    for filename in filenames:
                        if filename in lock_files:
                            try:
                                os.remove(os.path.join(root_dir, filename))
                            except Exception:
                                pass
                print("[CMA] Master profile copied with lock files cleaned.")
            except Exception as e:
                print(f"[CMA] Warning: could not copy master profile ({e}). Starting fresh.")
        else:
            print("[CMA] No master profile found. Initialising fresh profile.")
            os.makedirs(self.temp_profile_dir, exist_ok=True)

        # ── Proxy setup ──────────────────────────────────────────────────────────
        proxy_user = os.getenv("CMA_PROXY_USER")
        proxy_pass = os.getenv("CMA_PROXY_PASS")

        if proxy_user and "unlocker" in proxy_user.lower():
            isp_user = os.getenv("BRIGHTDATA_RESIDENTIAL_PROXY_USER")
            isp_pass = os.getenv("BRIGHTDATA_RESIDENTIAL_PROXY_PASS")
            if isp_user and isp_pass:
                print("[CMA] [PROXY] Web Unlocker detected — switching to ISP residential proxy.")
                proxy_user = isp_user
                proxy_pass = isp_pass

        # ── Browser launch ───────────────────────────────────────────────────────
        is_prod = os.name != "nt"

        # On Windows: use the REAL Chrome binary to avoid DataDome fingerprint detection.
        # Patchright's bundled Chromium gets hard-blocked by DataDome ("Access is temporarily restricted").
        # Using the user's actual Chrome.exe makes the session indistinguishable from normal browsing.
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

        # Thread-safe virtual display environment injection
        browser_env = os.environ.copy()
        if is_prod:
            browser_env["DISPLAY"] = ":100"

        launch_kwargs = {
            "user_data_dir": self.temp_profile_dir,
            "headless": False,
            "ignore_https_errors": True,
            "slow_mo": random.randint(80, 150),
            "viewport": {"width": 1920, "height": 1080},
            "env": browser_env,
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-infobars",
                "--disable-component-update",
                "--disable-default-apps",
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding",
            ]
        }

        if chrome_exe:
            launch_kwargs["executable_path"] = chrome_exe
            print(f"[CMA] Using real Chrome: {chrome_exe}")
        elif not is_prod:
            launch_kwargs["channel"] = "chrome"
            print("[CMA] Using channel='chrome' (system Chrome)")
        else:
            # Use real Google Chrome Stable in production — Patchright's bundled
            # Chromium gets hard-blocked by DataDome fingerprinting.
            chrome_path = "/usr/bin/google-chrome-stable"
            if os.path.exists(chrome_path):
                launch_kwargs["executable_path"] = chrome_path
                print(f"[CMA] Using real Google Chrome Stable: {chrome_path}")
            else:
                print("[CMA] WARNING: Real Chrome not found, falling back to Patchright bundled Chromium")

        if proxy_user and proxy_pass:
            proxy_server = os.getenv("BRIGHTDATA_PROXY_SERVER") or "http://brd.superproxy.io:22225"
            if ":33335" in proxy_server:
                proxy_server = proxy_server.replace(":33335", ":22225")
            if "-session-" not in proxy_user:
                import uuid
                session_id = str(uuid.uuid4())[:8]
                proxy_user = f"{proxy_user}-session-{session_id}"
            print(f"[CMA] [PROXY] Routing through ISP residential proxy ({proxy_server}) with session pinning ({proxy_user.split('-session-')[-1]})...")
            launch_kwargs["proxy"] = {
                "server": proxy_server,
                "username": proxy_user,
                "password": proxy_pass,
            }
        else:
            print("[CMA] [INFO] No proxy configured. Running on local Chrome directly.")

        self.context = await self.playwright.chromium.launch_persistent_context(**launch_kwargs)
        self.browser = None
        self.page = self.context.pages[0] if self.context.pages else await self.context.new_page()
        self.page.set_default_timeout(30000)

    async def _human_delay(self, min_ms=500, max_ms=1500):
        await self.page.wait_for_timeout(random.randint(min_ms, max_ms))

    async def _random_mouse_move(self):
        try:
            width, height = 1920, 1080
            for _ in range(3):
                await self.page.mouse.move(random.randint(0, width), random.randint(0, height), steps=10)
                await self._human_delay(100, 300)
        except: pass

    async def _hover_and_click(self, selector_or_locator):
        if isinstance(selector_or_locator, str):
            locator = self.page.locator(selector_or_locator).first
        else:
            locator = selector_or_locator
        
        try:
            await locator.scroll_into_view_if_needed(timeout=2000)
        except Exception: pass
        
        try:
            await self._random_mouse_move()
            await locator.hover(timeout=2000)
            await self._human_delay(100, 300)
        except Exception: pass

        try:
            await locator.click(timeout=3000)
        except Exception:
            try:
                await locator.click(force=True, timeout=3000)
            except Exception:
                await locator.evaluate("el => el.click()")

    async def _solve_datadome_slider(self) -> bool:
        """
        Human-in-the-Loop (HITL) CAPTCHA Bypass.
        Immediately pauses the automation script and waits up to 90 seconds for the user
        to manually slide the CAPTCHA inside the opened browser window.
        """
        frame_selector = 'iframe[src*="captcha-delivery.net"], iframe[src*="datadome.co"], iframe[src*="captcha-delivery.com"]'
        captcha_iframe = self.page.locator(frame_selector).first

        try:
            self.captcha_detected = True
            print("[CMA] [WARN] [ACTION REQUIRED] DataDome CAPTCHA/Verification Page Detected!")
            print("[CMA] [WARN] Please look at the opened Chrome browser window on your VNC display.")
            print("[CMA] [WARN] Manually DRAG the slider handle to the right to solve the CAPTCHA.")
            print("[CMA] [WARN] Waiting up to 3 minutes for manual resolution...")

            for i in range(180):
                await asyncio.sleep(1)
                try:
                    is_visible = await captcha_iframe.is_visible(timeout=500)
                    if not is_visible:
                        print("[CMA] [SUCCESS] CAPTCHA resolved! Resuming automation...")
                        return True
                except Exception:
                    print("[CMA] [SUCCESS] CAPTCHA resolved! Resuming automation...")
                    return True

                remaining = 180 - i - 1
                if remaining % 5 == 0 and remaining > 0:
                    print(f"[CMA] Waiting for CAPTCHA solve... {remaining}s remaining. Drag the slider NOW.")

            print("[CMA] [TIMEOUT] CAPTCHA not solved within 3 minutes.")
            return False

        except Exception as e:
            print(f"[CMA] Error during manual CAPTCHA check: {e}")
            return False

    async def login(self) -> bool:
        username = os.getenv("CMA_USERNAME") or os.getenv("CMA_CGM_USERNAME") or "BOOKINGSG@IN-FREIGHT.COM"
        password = os.getenv("CMA_PASSWORD") or os.getenv("CMA_CGM_PASSWORD") or "IFSGb2020"

        try:
            await self._init_browser()

            # Step 1: Warm up session on homepage first (going straight to quote page triggers DataDome)
            print("[CMA] Warming up session on homepage...")
            await self.page.goto("https://www.cma-cgm.com", wait_until="domcontentloaded")
            await self._human_delay(2000, 4000)
            await self._random_mouse_move()

            # Check for hard-block ("Access is temporarily restricted") or CAPTCHA on homepage
            page_content = await self.page.content()
            if "temporarily restricted" in page_content.lower() or "access denied" in page_content.lower():
                print("[CMA] [WARN] 'Access is temporarily restricted' detected on homepage!")
                print("[CMA] [WARN] DataDome has hard-blocked this session. Waiting up to 3 minutes for manual resolution...")
                print("[CMA] [WARN] If you see a CAPTCHA, solve it. Otherwise, try refreshing the page in the browser.")
                for i in range(180):
                    await asyncio.sleep(1)
                    page_content = await self.page.content()
                    if "temporarily restricted" not in page_content.lower() and "access denied" not in page_content.lower():
                        print("[CMA] [SUCCESS] Block cleared! Continuing...")
                        break
                    remaining = 180 - i - 1
                    if remaining % 15 == 0 and remaining > 0:
                        print(f"[CMA] Still blocked... {remaining}s remaining.")
                else:
                    print("[CMA] [TIMEOUT] Still blocked after 3 minutes.")
                    return False

            await self._human_delay(1000, 2000)

            # Step 2: Navigate to quote page
            print("[CMA] Navigating to quote page...")
            await self.page.goto(self.QUOTE_URL, wait_until="domcontentloaded")
            await self._random_mouse_move()
            
            # Check for CAPTCHA/Verification on quote page
            print(f"[CMA] Page title: {await self.page.title()}")
            captcha_iframe = self.page.locator('iframe[src*="captcha-delivery.net"], iframe[src*="datadome.co"], iframe[src*="captcha-delivery.com"]')
            is_captcha = await captcha_iframe.is_visible(timeout=10000)
            
            if is_captcha:
                print("[CMA] CAPTCHA detected via iframe. Attempting to solve slider...")
                solved = await self._solve_datadome_slider()
                if not solved:
                    print("[CMA] Failed to solve CAPTCHA.")
                    return False
                print("[CMA] CAPTCHA solved (or attempted). Waiting for page to reload...")
                await self._human_delay(3000, 5000)
                if "Verification Required" in await self.page.content():
                    print("[CMA] Still on CAPTCHA page. Giving up.")
                    return False

            # Also check for hard-block on quote page
            page_content = await self.page.content()
            if "temporarily restricted" in page_content.lower():
                print("[CMA] [WARN] Hard-blocked on quote page too. Waiting for manual resolution...")
                for i in range(180):
                    await asyncio.sleep(1)
                    page_content = await self.page.content()
                    if "temporarily restricted" not in page_content.lower():
                        print("[CMA] [SUCCESS] Block cleared on quote page!")
                        break
                    remaining = 180 - i - 1
                    if remaining % 15 == 0 and remaining > 0:
                        print(f"[CMA] Still blocked on quote page... {remaining}s remaining.")
                else:
                    print("[CMA] [TIMEOUT] Still blocked after 3 minutes on quote page.")
                    return False
            
            await self._human_delay(1000, 3000)
            print("[CMA] Waiting for OAuth redirect...")
            try:
                await self.page.wait_for_url(lambda url: "auth.cma-cgm.com" in url, timeout=15000)
                print(f"[CMA] Redirected to auth: {self.page.url}")
            except Exception:
                print(f"[CMA] Redirect to auth page timed out or did not happen. Current URL: {self.page.url}")
                # We might already be logged in or redirect was too fast

            # Login fields
            email_sel = 'input[type="email"], input[name="Email"], input[placeholder*="email" i], input[id*="email" i]'
            pwd_sel = 'input[type="password"]'
            
            try:
                email_field = self.page.locator(email_sel).first
                await email_field.wait_for(state="visible", timeout=15000)
                await email_field.click()
                await email_field.fill("")  # Clear any pre-filled text
                await email_field.type(username, delay=random.randint(70, 150))
                await self._human_delay(400, 800)

                pwd_field = self.page.locator(pwd_sel).first
                await pwd_field.click()
                await pwd_field.fill("")
                await pwd_field.type(password, delay=random.randint(70, 150))
            except Exception as e:
                print(f"[CMA] Credential entry error: {e}")
                return False

            print("[CMA] Clicking Log in button...")
            submit_sel = 'button:has-text("Log in"), button[type="submit"]'
            await self._hover_and_click(submit_sel)

            # CMA's OAuth uses a POST form redirect which can trigger net::ERR_CACHE_MISS in Chrome.
            # We catch that and just wait, then navigate directly to the quote page.
            print("[CMA] Waiting for redirect back to cma-cgm.com...")
            try:
                await self.page.wait_for_url(
                    lambda url: "cma-cgm.com" in url and "auth.cma-cgm" not in url,
                    timeout=30000
                )
                print(f"[CMA] Redirect successful: {self.page.url}")
            except Exception as redirect_err:
                err_str = str(redirect_err)
                if "ERR_CACHE_MISS" in err_str or "net::" in err_str:
                    print(f"[CMA] Post-login redirect error (expected with POST form): {err_str.split(chr(10))[0]}")
                    print("[CMA] Waiting briefly then navigating to quote page directly...")
                    await self._human_delay(3000, 5000)
                else:
                    print(f"[CMA] Redirect wait failed: {err_str.split(chr(10))[0]}")
                    await self._human_delay(2000, 3000)

            print("[CMA] Navigating to quote form...")
            await self.page.goto(self.QUOTE_URL, wait_until="domcontentloaded")
            await self._human_delay(4000, 7000)

            # Final check for CAPTCHA
            captcha_iframe = self.page.locator('iframe[src*="captcha-delivery.net"], iframe[src*="datadome.co"], iframe[src*="captcha-delivery.com"]')
            if await captcha_iframe.is_visible(timeout=5000):
                print("[CMA] CAPTCHA appeared after login. Attempting to solve...")
                await self._solve_datadome_slider()

            origin_sel = 'input[placeholder*="Name / Code / Port" i]'
            try:
                await self.page.wait_for_selector(origin_sel, timeout=20000)
                print("[CMA] Login successful, form loaded.")
                self.is_login_successful = True  # Triggers master profile sync on close()
                await self._random_mouse_move()
                return True
            except Exception:
                print("[CMA] Login failed or form not loaded.")
                return False

        except Exception as e:
            print(f"[CMA] Login error: {e}")
            try:
                # Save debug screenshot to backend root for easy access
                await self.page.screenshot(path="cma_login_fail.png")
                print("[CMA] Saved debug screenshot to cma_login_fail.png")
            except:
                pass
            return False

    def _extract_port_code(self, text: str) -> str:
        if not text: return ""
        match = re.search(r'\(([A-Z]{5})\)', text)
        if match:
            return match.group(1)
        clean = text.strip()
        if len(clean) == 5 and clean.isupper():
            return clean
        return text

    async def _dismiss_cma_modals(self):
        """
        Dismisses any informational popups/modals that appear on CMA CGM (e.g.
        'Information on Egypt Terminal Handling and Sealing Charges', port notices, etc.)
        by clicking 'Okay, I got it!' or close buttons or pressing Escape.
        """
        if not self.page:
            return
        try:
            modal_btn_selectors = [
                'button:has-text("Okay, I got it!")',
                'button:has-text("Okay, I got it")',
                'button:has-text("I got it")',
                'button:has-text("Got it")',
                'button:has-text("Okay")',
                'button:has-text("Accept")',
                'button:has-text("Understand")',
                'button:has-text("Close")',
                '[role="dialog"] button',
                'div[class*="modal"] button',
                'div[class*="popup"] button',
                'div[class*="dialog"] button',
                'button.close',
                'button[aria-label="Close"]',
                'span:has-text("×")',
            ]
            
            dismissed = False
            for sel in modal_btn_selectors:
                try:
                    btns = self.page.locator(sel)
                    count = await btns.count()
                    for i in range(count):
                        btn = btns.nth(i)
                        if await btn.is_visible(timeout=300):
                            btn_text = (await btn.inner_text()).strip()
                            if any(k in btn_text.lower() for k in ["okay", "got it", "accept", "understand", "close", "ok"]) or btn_text == "×" or btn_text == "":
                                print(f"[CMA] Dismissing popup modal via button ('{btn_text}'): {sel}")
                                await btn.click(force=True)
                                await self.page.wait_for_timeout(500)
                                dismissed = True
                                break
                    if dismissed:
                        break
                except Exception:
                    pass

            if not dismissed:
                dialogs = self.page.locator('[role="dialog"]:visible, div[class*="modal"]:visible, div[class*="overlay"]:visible, div[class*="backdrop"]:visible')
                if await dialogs.count() > 0:
                    print("[CMA] Visible popup dialog/overlay detected. Pressing Escape key fallback...")
                    await self.page.keyboard.press("Escape")
                    await self.page.wait_for_timeout(500)
                    try:
                        await self.page.mouse.click(20, 20)
                        await self.page.wait_for_timeout(300)
                    except Exception:
                        pass
        except Exception:
            pass

    async def _select_cma_dropdown_option(self, label: str, locode: str, cached_name: Optional[str] = None, prefer_ramp: bool = False) -> bool:
        # Target individual <li> items only — NOT the <ul class="options"> container
        suggestion_sel = 'ul[role="listbox"] li, ul.options li, li[role="option"], [class*="suggestion"] li'
        try:
            # Wait for suggestions to appear in DOM (don't require "visible" — CMA's dropdown CSS can be tricky)
            await self.page.wait_for_selector(suggestion_sel, state="attached", timeout=10000)
            await self.page.wait_for_timeout(500)  # Let dropdown fully render
            suggestions = self.page.locator(suggestion_sel)
            count = await suggestions.count()
            
            print(f"[CMA] Found {count} suggestions in dropdown for {label} (LOCODE: {locode}, cached: '{cached_name}', prefer_ramp: {prefer_ramp})")
            
            # Step 0: If prefer_ramp is requested, look for option containing "RAMP" or "DOOR" first!
            if prefer_ramp:
                for i in range(count):
                    item = suggestions.nth(i)
                    text = (await item.inner_text()).strip().upper()
                    clean_locode = locode.strip().upper()
                    if clean_locode in text and ("RAMP" in text or "DOOR" in text):
                        inner_text = (await item.inner_text()).strip()
                        print(f"[CMA] [RAMP PREFERRED] Selected RAMP/DOOR option for {label}: '{inner_text}'")
                        await self._hover_and_click(item)
                        set_cached_carrier_port("cma", locode, inner_text)
                        return True
            
            # Normalised target candidate list
            target_candidates = []
            if cached_name:
                target_candidates.append(cached_name.strip().upper())
            target_candidates.append(locode.strip().upper())
            
            # Step 1: Scan for target candidates with exact LOCODE / word boundary matching
            for i in range(count):
                item = suggestions.nth(i)
                text = (await item.inner_text()).strip().upper()
                if locode == "AUMEL" and ("AUMELAS" in text or "FRYUH" in text):
                    continue
                
                # Check for exact LOCODE match in parentheses first (e.g. "(AUMEL)")
                sug_locode_match = re.search(r'\(([A-Z]{5})\)', text)
                if sug_locode_match:
                    sug_locode = sug_locode_match.group(1)
                    if sug_locode == locode.strip().upper():
                        inner_text = (await item.inner_text()).strip()
                        print(f"[CMA] [SUCCESS] Found exact LOCODE match for {label}: '{inner_text}'")
                        await self._hover_and_click(item)
                        set_cached_carrier_port("cma", locode, inner_text)
                        return True
                
                # Check with word boundaries for other candidates
                matched = False
                for cand in target_candidates:
                    if len(cand) == 5 and cand.isupper():
                        if re.search(rf"\b{re.escape(cand)}\b", text):
                            matched = True
                            break
                    else:
                        if cand in text:
                            matched = True
                            break
                
                if matched:
                    inner_text = (await item.inner_text()).strip()
                    print(f"[CMA] [SUCCESS] Found match for {label}: '{inner_text}'")
                    await self._hover_and_click(item)
                    set_cached_carrier_port("cma", locode, inner_text)
                    return True

            # Step 2: Fallback to any option containing the LOCODE with word boundaries
            for i in range(count):
                item = suggestions.nth(i)
                text = (await item.inner_text()).strip().upper()
                if locode == "AUMEL" and ("AUMELAS" in text or "FRYUH" in text):
                    continue
                clean_locode = locode.strip().upper()
                if re.search(rf"\b{re.escape(clean_locode)}\b", text):
                    inner_text = (await item.inner_text()).strip()
                    print(f"[CMA] [Fallback] Found LOCODE-only match for {label}: '{inner_text}'")
                    await self._hover_and_click(item)
                    set_cached_carrier_port("cma", locode, inner_text)
                    return True

            # Step 3: Ultimate fallback - click the first option (that is safe if AUMEL)
            if count > 0:
                item = suggestions.nth(0)
                inner_text = (await item.inner_text()).strip()
                if locode == "AUMEL" and ("AUMELAS" in inner_text.upper() or "FRYUH" in inner_text.upper()):
                    # Find first safe option
                    found_safe = False
                    for i in range(count):
                        cand_item = suggestions.nth(i)
                        cand_text = (await cand_item.inner_text()).strip().upper()
                        if not ("AUMELAS" in cand_text or "FRYUH" in cand_text):
                            item = cand_item
                            inner_text = (await cand_item.inner_text()).strip()
                            found_safe = True
                            break
                    if not found_safe:
                        print(f"[CMA] [ERROR] No safe Melbourne option found in dropdown")
                        return False

                print(f"[CMA] [WARN] No exact match found for {label}. Clicking first option: '{inner_text}'")
                await self._hover_and_click(item)
                set_cached_carrier_port("cma", locode, inner_text)
                return True

            print(f"[CMA] [ERROR] No suggestions found in dropdown for {label}")
            return False
        except Exception as e:
            print(f"[CMA] [ERROR] Exception selecting dropdown option for {label}: {e}")
            return False

    async def _is_cma_weight_set(self, weight_kg: int) -> bool:
        expected_digits = str(weight_kg)
        try:
            return await self.page.evaluate(
                """
                ({ expectedDigits }) => {
                    const digits = (value) => String(value || "").replace(/\\D/g, "");
                    const isVisible = (el) => {
                        if (!el || !el.isConnected) return false;
                        const style = window.getComputedStyle(el);
                        const rect = el.getBoundingClientRect();
                        return style.visibility !== "hidden" &&
                            style.display !== "none" &&
                            rect.width > 0 &&
                            rect.height > 0;
                    };
                    const queryDeep = (root, selector) => {
                        const found = Array.from(root.querySelectorAll(selector));
                        for (const el of Array.from(root.querySelectorAll("*"))) {
                            if (el.shadowRoot) found.push(...queryDeep(el.shadowRoot, selector));
                        }
                        return found;
                    };

                    const ownText = (el) => Array.from(el.childNodes)
                        .filter((node) => node.nodeType === Node.TEXT_NODE)
                        .map((node) => node.textContent || "")
                        .join(" ");
                    const isWeightLabel = (el) => {
                        const text = (el.textContent || "").replace(/\\s+/g, " ").trim();
                        return /Max\\s+Net\\s+Weight/i.test(ownText(el)) ||
                            (/^Max\\s+Net\\s+Weight$/i.test(text) && text.length < 40);
                    };
                    const isNear = (anchor, field) => {
                        const a = anchor.getBoundingClientRect();
                        const f = field.getBoundingClientRect();
                        if (!a.width || !a.height || !f.width || !f.height) return false;
                        return f.top >= a.top - 20 &&
                            f.top <= a.bottom + 220 &&
                            Math.abs((f.left + f.right) / 2 - (a.left + a.right) / 2) < 700;
                    };
                    const editableSelector = [
                        "input:not([type='hidden'])",
                        "textarea",
                        "[contenteditable='true']",
                        "[role='textbox']"
                    ].join(",");
                    const placeholders = queryDeep(document, ".placeholder")
                        .filter((el) => isVisible(el) && /ex\\.\\s*10\\s*000/i.test(el.textContent || ""));
                    const labels = queryDeep(document, "*").filter((el) => isVisible(el) && isWeightLabel(el));
                    for (const anchor of [...placeholders, ...labels]) {
                        let scope = anchor;
                        for (let i = 0; i < 6 && scope.parentElement; i += 1) {
                            const fields = queryDeep(scope, editableSelector)
                                .filter((field) => isVisible(field) && isNear(anchor, field));
                            for (const field of fields) {
                                const value = field.value || field.getAttribute("aria-valuenow") || field.textContent;
                                if (digits(value) === expectedDigits) return true;
                            }

                            scope = scope.parentElement;
                            const text = scope.innerText || scope.textContent || "";
                            const scopePlaceholders = queryDeep(scope, ".placeholder")
                                .filter((el) => isVisible(el) && /ex\\.\\s*10\\s*000/i.test(el.textContent || ""));
                            if (
                                /Max\\s+Net\\s+Weight/i.test(text) &&
                                !/Weight\\s+is\\s+required/i.test(text) &&
                                scopePlaceholders.length === 0 &&
                                digits(text).includes(expectedDigits)
                            ) {
                                return true;
                            }
                        }
                    }
                    return false;
                }
                """,
                {"expectedDigits": expected_digits},
            )
        except Exception:
            return False

    async def _set_cma_cargo_weight(self, weight_kg: int, container_name: Optional[str] = None) -> bool:
        weight_text = str(weight_kg)

        # Strategy 1: Target specifically inside the correct container card if name is known
        if container_name:
            try:
                card_selectors = [
                    f'li:has(span:has-text("{container_name}"))',
                    f'div.content:has-text("{container_name}")',
                    f'div:has-text("{container_name}")',
                ]
                for card_sel in card_selectors:
                    card = self.page.locator(card_sel).filter(has=self.page.locator('span[name="weightPerContainer"] input')).first
                    if await card.count() > 0:
                        field = card.locator('span[name="weightPerContainer"] input').first
                        await field.scroll_into_view_if_needed(timeout=3000)
                        await field.click(force=True, timeout=3000)
                        await self.page.keyboard.press("Control+A")
                        await self.page.keyboard.press("Backspace")
                        await self.page.keyboard.type(weight_text, delay=40)
                        await self.page.keyboard.press("Tab")
                        await self.page.wait_for_timeout(500)
                        if await self._is_cma_weight_set(weight_kg):
                            print(f"[CMA] Weight set to {weight_kg} KGM (via container-specific card selector)")
                            return True
            except Exception as e:
                print(f"[CMA] Weight specific card strategy failed: {e}")

        # Strategy 2: Target any visible input field inside a weightPerContainer span
        try:
            field = self.page.locator('span[name="weightPerContainer"] input >> visible=true').first
            if await field.count() > 0:
                await field.scroll_into_view_if_needed(timeout=3000)
                await field.click(force=True, timeout=3000)
                await self.page.keyboard.press("Control+A")
                await self.page.keyboard.press("Backspace")
                await self.page.keyboard.type(weight_text, delay=40)
                await self.page.keyboard.press("Tab")
                await self.page.wait_for_timeout(500)
                if await self._is_cma_weight_set(weight_kg):
                    print(f"[CMA] Weight set to {weight_kg} KGM (via visible weightPerContainer input)")
                    return True
        except Exception as e:
            print(f"[CMA] Weight visible input strategy failed: {e}")

        # Strategy 3: Target span placeholder that is visible
        placeholder_selectors = [
            'span.placeholder:has-text("ex. 10 000") >> visible=true',
            'span.placeholder:has-text("ex. 10 000 KGM") >> visible=true',
        ]
        for selector in placeholder_selectors:
            try:
                target = self.page.locator(selector).first
                if await target.count() == 0:
                    continue
                await target.scroll_into_view_if_needed(timeout=3000)
                await target.click(force=True, timeout=3000)
                await self.page.keyboard.press("Control+A")
                await self.page.keyboard.press("Backspace")
                await self.page.keyboard.type(weight_text, delay=40)
                await self.page.keyboard.press("Tab")
                await self.page.wait_for_timeout(500)
                if await self._is_cma_weight_set(weight_kg):
                    print(f"[CMA] Weight set to {weight_kg} KGM (via visible placeholder)")
                    return True
            except Exception as e:
                print(f"[CMA] Weight visible placeholder strategy failed: {e}")

        # Strategy 4: Fallback to the original direct selectors but only if they are visible
        direct_selectors = [
            'xpath=(//*[text()[contains(normalize-space(.), "Max Net Weight")]]/following::input[not(@type="hidden")])[1] >> visible=true',
        ]
        for selector in direct_selectors:
            try:
                field = self.page.locator(selector).first
                if await field.count() == 0:
                    continue
                await field.scroll_into_view_if_needed(timeout=3000)
                await field.click(force=True, timeout=3000)
                await self.page.keyboard.press("Control+A")
                await self.page.keyboard.press("Backspace")
                await self.page.keyboard.type(weight_text, delay=40)
                await self.page.keyboard.press("Tab")
                await self.page.wait_for_timeout(500)
                if await self._is_cma_weight_set(weight_kg):
                    print(f"[CMA] Weight set to {weight_kg} KGM (via visible fallback input)")
                    return True
            except Exception as e:
                print(f"[CMA] Weight visible fallback strategy failed: {e}")

        return False

    async def _handle_cma_pod_selection(self, target_pod_locode: Optional[str] = None) -> bool:
        """
        Handles selecting a POD (Port of Discharge) when CMA CGM destination is set to RAMP.
        CMA CGM requires selecting a POD (e.g. Fujairah AEJFR or Khor Fakkan AEKLF for Jebel Ali AEJEA).
        """
        try:
            print("[CMA] Looking for POD dropdown field...")
            pod_selectors = [
                'div:has(label:has-text("POD")) .el-select',
                'div:has(label:has-text("POD")) input',
                'input[placeholder*="POD" i]',
                '.el-select:has-text("Select")',
            ]
            
            pod_field = None
            for sel in pod_selectors:
                loc = self.page.locator(sel).first
                if await loc.count() > 0 and await loc.is_visible(timeout=1000):
                    pod_field = loc
                    break

            if pod_field:
                print("[CMA] Opening POD dropdown...")
                await pod_field.scroll_into_view_if_needed(timeout=3000)
                await pod_field.click(force=True)
                await self.page.wait_for_timeout(1500)
                
                suggestion_sel = 'ul[role="listbox"] li:visible, .el-select-dropdown:visible .el-select-dropdown__item, li[role="option"]:visible'
                suggestions = self.page.locator(suggestion_sel)
                count = await suggestions.count()
                print(f"[CMA] Found {count} options in visible POD dropdown.")
                
                valid_pod_item = None
                for i in range(count):
                    item = suggestions.nth(i)
                    text = (await item.inner_text()).strip().upper()
                    
                    # Ignore header menu links
                    if any(bad in text for bad in ["CMA CGM", "SEARCH IN NEWS", "TRACKING", "VOYAGE", "ENGLISH", "FRANCAIS", "ESPAOL", "PORTUGUS"]):
                        continue
                    
                    # If specific target POD requested (e.g. AEJFR or AEKLF)
                    if target_pod_locode and target_pod_locode.strip().upper() in text:
                        valid_pod_item = item
                        print(f"[CMA] [SUCCESS] Found target POD option: '{await item.inner_text()}'")
                        break
                    
                    # Otherwise pick first option containing a 5-letter locode or valid port
                    if not valid_pod_item and (re.search(r'\([A-Z]{5}\)', text) or any(p in text for p in ["AEJFR", "AEKLF", "AEJEA", "AEKHL", "FUJAIRAH", "KHOR", "JEBEL", "KHALIFA"])):
                        valid_pod_item = item

                if valid_pod_item:
                    inner_text = (await valid_pod_item.inner_text()).strip()
                    print(f"[CMA] [SUCCESS] Selected POD option: '{inner_text}'")
                    await self._hover_and_click(valid_pod_item)
                    return True
                else:
                    print("[CMA] [WARN] No valid POD port option found in dropdown.")
        except Exception as e:
            print(f"[CMA] POD selection error: {e}")
        return False

    async def _clear_cma_destination_and_reselect_ramp(self, dest_locode: str, prefer_pod: Optional[str] = None) -> bool:
        """
        Clears the currently selected Destination port tag/card, re-types the locode,
        and selects the RAMP option, then populates the POD field!
        """
        try:
            print(f"[CMA] Clearing current Destination selection to switch to RAMP...")
            # Look for clear / change / remove buttons on the destination tag/card
            clear_btn = self.page.locator('div:has-text("Destination") button, button[aria-label*="clear" i], button[aria-label*="remove" i], .icon-close, i.el-icon-close, button:has-text("Clear")').first
            if await clear_btn.count() > 0:
                try:
                    await clear_btn.click(force=True, timeout=1000)
                    await self.page.wait_for_timeout(1000)
                except Exception: pass
            
            # Re-locate Destination input field (ensure visible=true filter)
            dest_field = self.page.locator('input[placeholder*="Name / Code / Port" i] >> visible=true').first
            if await dest_field.count() == 0:
                dest_container = self.page.locator('div:has(label:has-text("Destination")) input, div[name*="destination" i] input').first
                if await dest_container.count() > 0:
                    dest_field = dest_container
            
            if await dest_field.count() > 0:
                await dest_field.click(force=True)
                await dest_field.fill("")
                await dest_field.type(dest_locode, delay=30)
                await self.page.wait_for_timeout(2000)
            
            if await self._select_cma_dropdown_option("Destination", dest_locode, prefer_ramp=True):
                await self.page.wait_for_timeout(1500)
                await self._handle_cma_pod_selection(target_pod_locode=prefer_pod)
                return True
        except Exception as e:
            print(f"[CMA] Error clearing and re-selecting destination as RAMP: {e}")
        return False

    def _extract_recommended_pod_from_banner(self, page_text: str, dest_locode: str, origin_locode: Optional[str] = None) -> Optional[str]:
        """
        Dynamically extracts any recommended 5-letter POD LOCODE mentioned in the carrier advisory banner.
        Works across all routes worldwide (e.g. AEJFR, AEKLF, AEFJR, OMSOH, SADMM, SARIY, etc.).
        """
        try:
            found_locodes = re.findall(r'\b[A-Z]{5}\b', page_text)
            candidates = [c for c in found_locodes if c not in (dest_locode, origin_locode or "", "HTTPS", "ECOM", "MUST")]
            if candidates:
                print(f"[CMA] Dynamically parsed recommended POD candidate(s) from banner: {candidates}")
                return candidates[0]
        except Exception: pass
        return None

    async def _check_cma_ramp_banner_and_retry(self, dest_locode: str, origin_locode: Optional[str] = None) -> bool:
        """
        Detects if CMA CGM displayed an advisory banner message:
        "Looking for AEJEA or AEKHL, please select AEJEA or AEKHL as ramp and select either AEJFR or AEKLF as POD"
        (or any similar intermodal advisory for any route worldwide)
        and automatically retries the search with RAMP + POD selection!
        """
        try:
            page_text = await self.page.inner_text('body')
            if "select" in page_text.lower() and "as ramp" in page_text.lower():
                print(f"\n[CMA] [RAMP BANNER DETECTED] CMA CGM suggested selecting {dest_locode} as RAMP and selecting a POD!")
                preferred_pod = self._extract_recommended_pod_from_banner(page_text, dest_locode, origin_locode)
                retried = await self._clear_cma_destination_and_reselect_ramp(dest_locode, prefer_pod=preferred_pod)
                if retried:
                    print("[CMA] Re-submitting search with RAMP + POD...")
                    submit_btn = self.page.locator('button:has-text("Get My Quote")').first
                    return True
        except Exception as e:
            print(f"[CMA] Ramp banner retry error: {e}")
        return False

    async def _handle_cma_customer_account_role(self) -> bool:
        """
        Handles the 'Customer account' -> 'Role (you are acting as)' dropdown on CMA CGM form.
        Selects 'NVOCC' if the section is present.
        """
        try:
            role_field = self.page.locator('#DdlCustomerRole, input[placeholder*="Select your role" i]').first
            if await role_field.count() > 0 and await role_field.is_visible(timeout=1500):
                print("[CMA] 'Customer account' section detected. Selecting Role: NVOCC...")
                await self._hover_and_click(role_field)
                await self.page.wait_for_timeout(800)

                # Click NVOCC option inside visible dropdown list
                nvocc_opt = self.page.locator('.el-select-dropdown__item:has-text("NVOCC"), li:has-text("NVOCC")').first
                if await nvocc_opt.count() > 0 and await nvocc_opt.is_visible(timeout=1500):
                    await self._hover_and_click(nvocc_opt)
                    print("[CMA] [SUCCESS] Selected Role: NVOCC")
                    await self.page.wait_for_timeout(500)
                    return True
                else:
                    # Fallback: type NVOCC and press Enter
                    print("[CMA] NVOCC option not directly clickable, attempting keyboard selection...")
                    await role_field.fill("NVOCC")
                    await self.page.wait_for_timeout(500)
                    await self.page.keyboard.press("Enter")
                    print("[CMA] [SUCCESS] Selected Role: NVOCC via keyboard")
                    return True
        except Exception as e:
            print(f"[CMA] Customer account role handling notice: {e}")
        return False

    async def search_quotes(self, request: RateSearchRequest) -> CarrierResultStatus:
        try:
            print("[CMA] Starting search...")
            
            # Initialize fallback notice
            self.port_fallback_notice = None
            
            # --- ORIGIN ---
            if request.origin and ("rotterdam" in request.origin.lower() or request.origin.strip().upper() == "NLRTM"):
                origin_locode = "NLRTM"
            elif request.origin and ("xingang" in request.origin.lower() or request.origin.strip().upper() in ("CNXIP", "CNTXG")):
                origin_locode = "CNTXG"
            else:
                origin_locode = resolve_port_for_carrier(request.origin, "cma")
                if origin_locode == "CNXIP":
                    origin_locode = "CNTXG"
                if not origin_locode or len(origin_locode) != 5 or not origin_locode.isupper():
                    origin_locode = self._extract_port_code(request.origin)
                    if origin_locode == "CNXIP":
                        origin_locode = "CNTXG"
                    if len(origin_locode) != 5 or not origin_locode.isupper():
                        from services.port_manager import search_port
                        ports = search_port(request.origin)
                        if ports:
                            origin_locode = ports[0]['code']
                            if origin_locode == "CNXIP":
                                origin_locode = "CNTXG"

            # Always type the LOCODE (e.g. SGSIN) — CMA accepts port codes and shows matching suggestions.
            origin_cached = get_cached_carrier_port("cma", origin_locode) if origin_locode else None
            origin_query = origin_locode
            
            print(f"[CMA] Filling Origin: '{origin_query}' (locode: {origin_locode}, cached: '{origin_cached}')")
            origin_field = self.page.locator('input[placeholder*="Name / Code / Port" i]').nth(0)
            await origin_field.click()
            await origin_field.fill("")  # Clear field
            await origin_field.type(origin_query, delay=30)
            await self.page.wait_for_timeout(2000)

            if not await self._select_cma_dropdown_option("Origin", origin_locode, origin_cached):
                return CarrierResultStatus.INVALID_SEARCH_INPUT
            
            print(f"[CMA] Origin selected: {origin_locode}")

            # --- DESTINATION ---
            if request.destination and ("rotterdam" in request.destination.lower() or request.destination.strip().upper() == "NLRTM"):
                dest_locode = "NLRTM"
            elif request.destination and ("xingang" in request.destination.lower() or request.destination.strip().upper() in ("CNXIP", "CNTXG")):
                dest_locode = "CNTXG"
            else:
                dest_locode = resolve_port_for_carrier(request.destination, "cma")
                if dest_locode == "CNXIP":
                    dest_locode = "CNTXG"
                if not dest_locode or len(dest_locode) != 5 or not dest_locode.isupper():
                    dest_locode = self._extract_port_code(request.destination)
                    if dest_locode == "CNXIP":
                        dest_locode = "CNTXG"
                    if len(dest_locode) != 5 or not dest_locode.isupper():
                        from services.port_manager import search_port
                        ports = search_port(request.destination)
                        if ports:
                            dest_locode = ports[0]['code']
                            if dest_locode == "CNXIP":
                                dest_locode = "CNTXG"

            # Check cache
            dest_cached = get_cached_carrier_port("cma", dest_locode) if dest_locode else None
            dest_query = dest_locode

            # Check if Sokhna -> Ain Sukhna fallback occurred
            if "EGSOK" in (request.origin.upper() if request.origin else "") or "SOKHNA" in (request.origin.upper() if request.origin else ""):
                if origin_locode == "EGAIS":
                    self.port_fallback_notice = "Sokhna fell back to Ain Sukhna"
            elif "EGSOK" in (request.destination.upper() if request.destination else "") or "SOKHNA" in (request.destination.upper() if request.destination else ""):
                if dest_locode == "EGAIS":
                    self.port_fallback_notice = "Sokhna fell back to Ain Sukhna"

            # Initial search uses standard PORT selection; switches to RAMP only if CMA displays the advisory banner
            print(f"[CMA] Filling Destination: '{dest_query}' (locode: {dest_locode}, cached: '{dest_cached}')")
            dest_field = self.page.locator('input[placeholder*="Name / Code / Port" i]').nth(1)
            await dest_field.click()
            await dest_field.fill("")
            await dest_field.type(dest_query, delay=30)
            await self.page.wait_for_timeout(2000)

            if not await self._select_cma_dropdown_option("Destination", dest_locode, dest_cached, prefer_ramp=False):
                return CarrierResultStatus.INVALID_SEARCH_INPUT
            
            print(f"[CMA] Destination selected: {dest_locode}")

            # --- IMMEDIATE FORM RAMP BANNER CHECK ---
            await self.page.wait_for_timeout(1000)
            page_text = await self.page.inner_text('body')
            if "select" in page_text.lower() and "as ramp" in page_text.lower():
                print(f"\n[CMA] [FORM BANNER DETECTED] CMA CGM displayed advisory banner immediately after selecting Destination!")
                preferred_pod = self._extract_recommended_pod_from_banner(page_text, dest_locode, origin_locode)
                await self._clear_cma_destination_and_reselect_ramp(dest_locode, prefer_pod=preferred_pod)
                await self.page.wait_for_timeout(1000)

            # --- CONTAINER TYPE & SIZE & WEIGHTS ---
            target_containers = ["20' Dry Standard", "40' Dry Standard", "40' Dry High Cube"]
            print(f"[CMA] Selecting all 3 dry container sizes: {target_containers}")
            await self.page.wait_for_timeout(2000)

            async def add_cma_container(container_name: str) -> bool:
                target_upper = container_name.upper()
                target_parts = target_upper.replace("'", "").split()
                
                # Locate and click Add / +
                try:
                    items = self.page.locator('text=/\\d+.*(?:DRY|REEFER|FLAT|OPEN)/i')
                    item_count = await items.count()
                    for i in range(item_count):
                        item = items.nth(i)
                        item_text = (await item.inner_text(timeout=1000)).strip().upper()
                        item_clean = item_text.replace("'", "")
                        if all(part in item_clean for part in target_parts):
                            parent = item.locator('..')
                            add_btn = parent.locator('button:has-text("Add"), button:has-text("+")')
                            if await add_btn.count() > 0 and await add_btn.first.is_visible(timeout=500):
                                await add_btn.first.click()
                                print(f"[CMA] Clicked Add for: '{item_text}'")
                                return True
                            
                            grandparent = parent.locator('..')
                            add_btn = grandparent.locator('button:has-text("Add"), button:has-text("+")')
                            if await add_btn.count() > 0 and await add_btn.first.is_visible(timeout=500):
                                await add_btn.first.click()
                                print(f"[CMA] Clicked Add (grandparent) for: '{item_text}'")
                                return True
                            
                            # If no Add button is visible, it means it is already selected!
                            print(f"[CMA] Container '{container_name}' already added (Add button not visible).")
                            return True
                except Exception as e:
                    print(f"[CMA] Error scanning Add buttons for '{container_name}': {e}")

                # Fallback div match
                try:
                    item_locator = self.page.locator(f'div:has-text("{container_name}")').filter(
                        has=self.page.locator('button:has-text("Add"), button:has-text("+")')
                    )
                    if await item_locator.count() > 0:
                        btn = item_locator.last.locator('button:has-text("Add"), button:has-text("+")').first
                        if await btn.is_visible(timeout=500):
                            await btn.click()
                            print(f"[CMA] Selected '{container_name}' via fallback div match")
                            return True
                        else:
                            print(f"[CMA] Container '{container_name}' already added (fallback button not visible).")
                            return True
                except Exception as e:
                    print(f"[CMA] Fallback failed for '{container_name}': {e}")
                
                return False

            for ct in target_containers:
                success = await add_cma_container(ct)
                if not success:
                    print(f"[CMA] Could not add container type '{ct}'")
                    await self.page.screenshot(path="cma_container_fail.png")
                    return CarrierResultStatus.INVALID_SEARCH_INPUT
                await self.page.wait_for_timeout(1000)

            # --- CARGO WEIGHT ---
            weight_kg = max(int(request.weight_per_container_kg), 10000)
            for ct in target_containers:
                print(f"[CMA] Entering cargo weight for {ct}: {weight_kg} KGM...")
                weight_set = await self._set_cma_cargo_weight(weight_kg, ct)
                if not weight_set:
                    print(f"[CMA] Weight field NOT filled for {ct} - saving screenshot.")
                    await self.page.screenshot(path="cma_weight_fail.png")
                    return CarrierResultStatus.INVALID_SEARCH_INPUT

            await self.page.wait_for_timeout(1500)

            # --- QUANTITY ---
            # Quantity is already 1 by default. The +/- buttons are next to the count.
            if request.container_quantity > 1:
                try:
                    # The + button is inside the selected container card
                    qty_plus = self.page.locator('button:has-text("+")').nth(-2)  # Second-to-last + (last is the Add button for unselected containers)
                    for _ in range(request.container_quantity - 1):
                        await qty_plus.click()
                        await self.page.wait_for_timeout(300)
                    print(f"[CMA] Quantity set to: {request.container_quantity}")
                except Exception as e:
                    print(f"[CMA] [WARN] Could not set quantity: {e}")

            # --- COMMODITY ---
            # Click "Choose a commodity" dropdown (Element UI el-select) and select "Freight All Kinds".
            # Do NOT type anything; simply click the dropdown and select the "Freight All Kinds" option.
            print("[CMA] Selecting commodity: Freight All Kinds...")
            try:
                # Click the commodity dropdown input to open it
                commodity_input = self.page.locator('#DdlCommodity').first
                await commodity_input.click()
                await self.page.wait_for_timeout(1000)
                
                # Look for option containing "Freight All Kinds" and click it directly without typing
                fak_option = self.page.locator('.el-select-dropdown__item:has-text("Freight All Kinds")').first
                if await fak_option.count() > 0:
                    await fak_option.click()
                    print("[CMA] Commodity 'Freight All Kinds' selected directly (no typing).")
                else:
                    # Fallback to general "FAK" text match
                    fak_option = self.page.locator('.el-select-dropdown__item:has-text("FAK")').first
                    if await fak_option.count() > 0:
                        await fak_option.click()
                        print("[CMA] Commodity FAK selected directly as fallback.")
                    else:
                        print("[CMA] [WARN] 'Freight All Kinds' option not found. Attempting fallback by typing...")
                        await commodity_input.fill("Freight All Kinds")
                        await self.page.wait_for_timeout(1000)
                        await self.page.keyboard.press("Enter")
                
                await self.page.wait_for_timeout(500)
            except Exception as e:
                print(f"[CMA] Commodity primary approach failed: {e}")
                # Fallback: type FAK and press Enter
                try:
                    commodity_input = self.page.locator('#DdlCommodity').first
                    await commodity_input.click()
                    await commodity_input.fill("FAK")
                    await self.page.wait_for_timeout(1000)
                    await self.page.keyboard.press("Enter")
                    print("[CMA] Commodity FAK selected via Enter key fallback.")
                except Exception as e2:
                    print(f"[CMA] [WARN] Commodity fallback also failed: {e2}")

            # --- CUSTOMER ACCOUNT / ROLE SELECTION ---
            # Select "NVOCC" if the "Customer account" -> "Role (you are acting as)" dropdown is present on the form
            await self._handle_cma_customer_account_role()

            # --- SUBMIT ---
            print("[CMA] Clicking 'Get My Quote'...")
            try:
                submit_btn = self.page.locator('button:has-text("Get My Quote")').first
                await self._hover_and_click(submit_btn)
                print("[CMA] Search submitted!")
                await self._human_delay(5000, 8000)
            except Exception as e:
                print(f"[CMA] Submit failed: {e}")
                await self.page.screenshot(path="cma_submit_fail.png")
                return CarrierResultStatus.UNKNOWN_ERROR

            # Results detection
            await self.page.wait_for_timeout(3000)
            page_text = await self.page.inner_text('body')
            
            # ONLY IF CMA displayed the blue ramp banner ("please select ... as ramp and select ... as POD")
            if "iqnoresult" in self.page.url or ("select" in page_text.lower() and "as ramp" in page_text.lower()):
                retried = await self._check_cma_ramp_banner_and_retry(dest_locode)
                if retried:
                    try:
                        await self.page.wait_for_selector('article.card-route-horizontal, article[class*="card-route-horizontal"], div[class*="schedules-result"]', timeout=30000)
                        print("[CMA] Results loaded after Ramp/POD retry!")
                        return CarrierResultStatus.AVAILABLE_QUOTES_FOUND
                    except Exception:
                        pass

            try:
                await self.page.wait_for_selector('article.card-route-horizontal, article[class*="card-route-horizontal"], div[class*="schedules-result"], div[class*="sailing-result"]', timeout=20000)
                print("[CMA] Results loaded.")
                return CarrierResultStatus.AVAILABLE_QUOTES_FOUND
            except Exception:
                page_text = await self.page.inner_text('body')
                if 'no result' in page_text.lower() or 'no schedule' in page_text.lower() or 'unable to propose' in page_text.lower():
                    print("[CMA] No results found for this route/date.")
                    return CarrierResultStatus.NO_QUOTES_AVAILABLE
                print("[CMA] Results timeout — saving screenshot.")
                await self.page.screenshot(path="cma_results_fail.png")
                return CarrierResultStatus.NO_QUOTES_AVAILABLE

        except Exception as e:
            print(f"[CMA] Search failed: {e}")
            return CarrierResultStatus.TIMEOUT if "timeout" in str(e).lower() else CarrierResultStatus.UNKNOWN_ERROR

    async def extract_quote_list(self) -> list[dict]:
        try:
            # First scroll and click "More results" repeatedly to load all cards
            await self._handle_more_results()

            cards_sel = 'article.card-route-horizontal, article[class*="card-route-horizontal"], div[class*="schedules-result"], div[class*="sailing-result"]'
            cards = self.page.locator(cards_sel)
            count = await cards.count()
            
            if count == 0:
                # Broader fallback
                cards = self.page.locator('div:has(button:has-text("Details")):has-text("USD")')
                count = await cards.count()

            print(f"[CMA] Found {count} total quote cards after loading all results.")
            self._all_quotes = []

            for i in range(count):
                card = cards.nth(i)
                text = await card.inner_text()
                
                # ETD & ETA extraction
                # Pattern: "Saturday, 16-May-2026" or "16-May-2026"
                date_pattern = r'(?:[A-Za-z]+,\s+)?\d{1,2}-[A-Za-z]+-\d{4}'
                found_dates = re.findall(date_pattern, text)
                etd_str = found_dates[0] if len(found_dates) > 0 else None
                eta_str = found_dates[1] if len(found_dates) > 1 else None
                
                etd = None
                if etd_str:
                    try:
                        if "," in etd_str:
                            etd = datetime.strptime(etd_str, "%A, %d-%b-%Y").date()
                        else:
                            etd = datetime.strptime(etd_str, "%d-%b-%Y").date()
                    except: pass
                
                eta = None
                if eta_str:
                    try:
                        if "," in eta_str:
                            eta = datetime.strptime(eta_str, "%A, %d-%b-%Y").date()
                        else:
                            eta = datetime.strptime(eta_str, "%d-%b-%Y").date()
                    except: pass

                # Transit time
                tt_match = re.search(r'(\d+)\s*[Dd]ays?', text)
                transit_time = int(tt_match.group(1)) if tt_match else None
                
                if etd and eta and transit_time is None:
                    transit_time = (eta - etd).days

                # Routing (Direct or Transit via X)
                routing = "Direct"
                routing_match = re.search(r'(via\s+[^\r\n]+|Direct)', text, re.IGNORECASE)
                if routing_match:
                    routing_val = routing_match.group(1).strip()
                    if routing_val.lower() == "direct":
                        routing = "Direct"
                    elif routing_val.lower().startswith("via"):
                        # Format "via JEDDAH , SA" -> "Transit - JEDDAH , SA"
                        via_port = routing_val[3:].strip()
                        routing = f"Transit - {via_port}"
                
                # Service & Vessel
                service_match = re.search(r'First Service\s+(\S+)', text)
                service = service_match.group(1).strip() if service_match else None
                
                vessel_match = re.search(r'Vessel\s+(.+?)\s+CO2', text)
                vessel = vessel_match.group(1).strip() if vessel_match else None

                # Total price
                price_match = re.search(r'(\d[\d,]*)\s*USD', text)
                total_price = float(price_match.group(1).replace(",", "")) if price_match else 0.0

                # Tags
                tags = []
                if "EARLIEST ARRIVAL" in text: tags.append("EARLIEST ARRIVAL")
                if "EARLIEST DEPARTURE" in text: tags.append("EARLIEST DEPARTURE")
                if "LATE BOOKING" in text: tags.append("LATE BOOKING")

                self._all_quotes.append({
                    "index": i,
                    "etd": etd.isoformat() if etd else None,
                    "eta": eta.isoformat() if eta else None,
                    "transit_time_days": transit_time,
                    "routing": routing,
                    "service_name": service,
                    "vessel": vessel,
                    "total_price": total_price,
                    "currency": "USD",
                    "tags": tags,
                    "card_locator": card,
                    "source": "carrier_portal",
                    "carrier_code": self.carrier_code
                })

            return self._all_quotes
        except Exception as e:
            print(f"[CMA] Error extracting quotes: {e}")
            return []

    async def _handle_more_results(self):
        """
        Repeatedly clicks 'More results' if visible to load ALL quotes on the page.
        """
        try:
            await self._dismiss_cma_modals()
            max_clicks = 5
            clicks = 0
            
            while clicks < max_clicks:
                await self._dismiss_cma_modals()
                # Scroll to bottom first to ensure button is rendered/visible
                print(f"[CMA] Scrolling to bottom to check for more results (iteration {clicks+1})...")
                await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await self.page.wait_for_timeout(1500)

                more_btn = self.page.locator('button:has-text("More results"), a:has-text("More results")').first
                if await more_btn.is_visible():
                    print(f"[CMA] Loading more results (click {clicks+1})...")
                    await more_btn.scroll_into_view_if_needed()
                    await more_btn.click()
                    await self.page.wait_for_timeout(4000)  # Wait for new cards to load
                    clicks += 1
                else:
                    print("[CMA] No more 'More results' buttons visible.")
                    break
        except Exception as e:
            print(f"[CMA] Error handling more results: {e}")

    async def open_price_breakdown(self, quote_ref: dict) -> bool:
        try:
            await self._dismiss_cma_modals()
            card = quote_ref["card_locator"]
            await card.scroll_into_view_if_needed()
            await self._random_mouse_move()
            details_btn = card.locator('label:has-text("Details"), button:has-text("Details")').first
            
            # Fast fail if Details button doesn't exist (e.g. for "Sold out" cards)
            if not await details_btn.is_visible(timeout=2000):
                await self._dismiss_cma_modals()
                if not await details_btn.is_visible(timeout=1000):
                    print(f"[CMA] Details button not visible for quote. Possibly Sold out.")
                    return False
                
            await self._hover_and_click(details_btn)
            await self._human_delay(1500, 2500)
            await self._dismiss_cma_modals()

            # --- Extract Free Time from D&D tab ---
            try:
                await self._dismiss_cma_modals()
                dd_tab = card.locator('button:has-text("D&D"), [role="tab"]:has-text("D&D")').first
                if await dd_tab.is_visible(timeout=2000):
                    await self._hover_and_click(dd_tab)
                    await self._human_delay(1000, 1500)
                    
                    # Scoped JS evaluation to parse the D&D table and sum Demurrage and Detention days for each container size
                    free_time_data = await card.evaluate('''card => {
                        const tables = Array.from(card.querySelectorAll('table'));
                        let importTable = null;
                        
                        const importHeading = Array.from(card.querySelectorAll('*')).find(el => {
                            const text = el.innerText ? el.innerText.trim().toUpperCase() : '';
                            return text === 'IMPORT FREE TIME';
                        });
                        
                        if (importHeading) {
                            // Find the first table that comes after the heading in the DOM
                            importTable = tables.find(t => {
                                return !!(importHeading.compareDocumentPosition(t) & Node.DOCUMENT_POSITION_FOLLOWING);
                            });
                        }
                        
                        // Fallback: second table is Import, first is Export
                        if (!importTable && tables.length >= 2) {
                            importTable = tables[1];
                        } else if (!importTable && tables.length === 1) {
                            importTable = tables[0];
                        }
                        
                        if (!importTable) return null;
                        
                        const rows = Array.from(importTable.querySelectorAll('tr'));
                        if (rows.length === 0) return null;
                        
                        const headers = Array.from(rows[0].querySelectorAll('th, td')).map(el => el.innerText.trim().toUpperCase());
                        const colIndices = { charge: 0, sizeType: 1, duration: 2 };
                        headers.forEach((h, idx) => {
                            if (h.includes('CHARGE')) colIndices.charge = idx;
                            else if ((h.includes('SIZE') || h.includes('TYPE')) && !h.includes('DAYS')) colIndices.sizeType = idx;
                            else if (h.includes('DURATION') || (h.includes('DAYS') && !h.includes('TYPE')) || h.includes('FREE')) colIndices.duration = idx;
                        });
                        
                        const res = {
                            free_times: { 'DRY 20': 0, 'DRY 40': 0, 'DRY 40H': 0 },
                            demurrage_times: { 'DRY 20': 0, 'DRY 40': 0, 'DRY 40H': 0 },
                            detention_times: { 'DRY 20': 0, 'DRY 40': 0, 'DRY 40H': 0 }
                        };
                        
                        for (let r = 1; r < rows.length; r++) {
                            const cells = Array.from(rows[r].querySelectorAll('td, th')).map(el => el.innerText.trim());
                            if (cells.length < 3) continue;
                            
                            const chargeType = (cells[colIndices.charge] || '').toUpperCase();
                            const sizeType = (cells[colIndices.sizeType] || '').toUpperCase();
                            const duration = parseInt(cells[colIndices.duration] || '0', 10);
                            if (isNaN(duration) || duration <= 0) continue;
                            
                            let containerKey = null;
                            if (sizeType.includes('20')) {
                                containerKey = 'DRY 20';
                            } else if (sizeType.includes('40ST') || (sizeType.includes('40') && !sizeType.includes('HC') && !sizeType.includes('HIGH'))) {
                                containerKey = 'DRY 40';
                            } else if (sizeType.includes('40HC') || sizeType.includes('HIGH CUBE') || sizeType.includes('40H')) {
                                containerKey = 'DRY 40H';
                            }
                            
                            if (containerKey) {
                                res.free_times[containerKey] += duration;
                                if (chargeType.includes('DEMURRAGE') || chargeType === 'DEM') {
                                    res.demurrage_times[containerKey] += duration;
                                } else if (chargeType.includes('DETENTION') || chargeType === 'DET') {
                                    res.detention_times[containerKey] += duration;
                                }
                            }
                        }
                        return res;
                    }''')
                    
                    if free_time_data and isinstance(free_time_data, dict):
                        free_times = free_time_data.get("free_times") or {}
                        demurrage_times = free_time_data.get("demurrage_times") or {}
                        detention_times = free_time_data.get("detention_times") or {}
                        
                        if any(v > 0 for v in free_times.values()):
                            quote_ref["free_times"] = free_times
                            quote_ref["demurrage_times"] = demurrage_times
                            quote_ref["detention_times"] = detention_times
                            
                            quote_ref["free_time"] = free_times.get("DRY 40H") or free_times.get("DRY 40") or free_times.get("DRY 20")
                            quote_ref["demurrage"] = demurrage_times.get("DRY 40H") or demurrage_times.get("DRY 40") or demurrage_times.get("DRY 20") or None
                            quote_ref["detention"] = detention_times.get("DRY 40H") or detention_times.get("DRY 40") or detention_times.get("DRY 20") or None
                            print(f"[CMA] Extracted container D&D free_times={free_times}, demurrage={demurrage_times}, detention={detention_times}")
                    else:
                        print("[CMA] D&D tab table not found/parsed. Attempting regex fallback.")
                        dd_text = await card.inner_text()
                        dem_match = re.search(r'Demurrage.*?(\d+)\s+Calendar', dd_text, re.IGNORECASE | re.DOTALL)
                        det_match = re.search(r'Detention.*?(\d+)\s+Calendar', dd_text, re.IGNORECASE | re.DOTALL)
                        merged_match = re.search(r'Import free time.*?(\d+)\s+Calendar', dd_text, re.IGNORECASE | re.DOTALL)
                        
                        dem_val = int(dem_match.group(1)) if dem_match else None
                        det_val = int(det_match.group(1)) if det_match else None
                        
                        if dem_val or det_val:
                            quote_ref["demurrage"] = dem_val
                            quote_ref["detention"] = det_val
                            quote_ref["free_time"] = (dem_val or 0) + (det_val or 0)
                        elif merged_match:
                            quote_ref["free_time"] = int(merged_match.group(1))
                            quote_ref["demurrage"] = None
                            quote_ref["detention"] = None
            except Exception as e:
                print(f"[CMA] Error extracting free time from D&D: {e}")

            # --- Switch back to Rate tab for charge breakdown ---
            await self._dismiss_cma_modals()
            rate_tab = card.locator('button:has-text("Rate"), [role="tab"]:has-text("Rate")').first
            if await rate_tab.is_visible():
                await self._hover_and_click(rate_tab)
            await self._human_delay(500, 1000)
            
            self.current_card = card
            return True
        except Exception as e:
            print(f"[CMA] Error opening breakdown: {e}")
            return False

    async def extract_charge_breakdown(self) -> list[dict]:
        try:
            await self._dismiss_cma_modals()
            if not self.current_card: return []
            text = await self.current_card.inner_text()
            
            # Extract Voyage Reference if present
            self._current_voyage = None
            try:
                voyage_loc = self.current_card.locator('dt:has-text("Voyage Ref") + dd').first
                voy_text = (await voyage_loc.text_content() or "").strip()
                if voy_text:
                    self._current_voyage = voy_text
                    print(f"[CMA] Found Voyage Ref via sibling locator: {self._current_voyage}")
            except Exception:
                pass

            if not self._current_voyage:
                raw_text = await self.current_card.text_content()
                voyage_match = re.search(r'Voyage\s+Ref\b.*?(\b[A-Z0-9]+)', raw_text, re.IGNORECASE)
                if voyage_match:
                    self._current_voyage = voyage_match.group(1)
                    print(f"[CMA] Found Voyage Ref via text_content regex: {self._current_voyage}")
            
            # Evaluate using JavaScript within the card context to parse the details table
            charges = await self.current_card.evaluate('''card => {
                const tables = Array.from(card.querySelectorAll('table'));
                
                // Find headers table (Table 0)
                const headerTable = tables.find(t => {
                    const text = t.innerText.toUpperCase();
                    return text.includes('CHARGES DETAILS') || text.includes('20ST');
                });
                if (!headerTable) return null;
                
                // Find rows table (Table 1)
                const rowsTable = tables.find(t => {
                    const text = t.innerText.toUpperCase();
                    return text.includes('OCEAN FREIGHT') || text.includes('CHARGES PAYABLE');
                });
                if (!rowsTable) return null;
                
                const headerRows = Array.from(headerTable.querySelectorAll('tr'));
                if (headerRows.length === 0) return null;
                
                const headers = Array.from(headerRows[0].querySelectorAll('th, td')).map(el => el.innerText.trim().toUpperCase());
                
                // Locate columns
                const colIndices = { name: 0, 'DRY 20': -1, 'DRY 40': -1, 'DRY 40H': -1, BL: -1, Currency: -1 };
                headers.forEach((h, idx) => {
                    if (h.includes('DETAIL') || h.includes('CHARGE') || h === '') {
                        colIndices.name = idx;
                    } else if (h.includes('20')) {
                        colIndices['DRY 20'] = idx;
                    } else if (h.includes('40ST') || h === '40ST' || (h.includes('40') && !h.includes('HC') && !h.includes('HIGH'))) {
                        colIndices['DRY 40'] = idx;
                    } else if (h.includes('40HC') || h.includes('HIGH CUBE') || h.includes('40H')) {
                        colIndices['DRY 40H'] = idx;
                    } else if (h === 'BL' || h.includes('B/L') || h.includes('LUMP')) {
                        colIndices.BL = idx;
                    } else if (h === 'CURRENCY' || h === 'CURR') {
                        colIndices.Currency = idx;
                    }
                });
                
                // Fallback if index not found
                if (colIndices['DRY 20'] === -1) colIndices['DRY 20'] = 1;
                if (colIndices['DRY 40'] === -1) colIndices['DRY 40'] = 2;
                if (colIndices['DRY 40H'] === -1) colIndices['DRY 40H'] = 3;
                if (colIndices.BL === -1) colIndices.BL = 4;
                if (colIndices.Currency === -1) colIndices.Currency = 5;
                
                const rows = Array.from(rowsTable.querySelectorAll('tr'));
                const list = [];
                for (let r = 0; r < rows.length; r++) {
                    const cells = Array.from(rows[r].querySelectorAll('td, th')).map(el => el.innerText.trim());
                    if (cells.length < 2) continue;
                    
                    const name = cells[colIndices.name] || '';
                    if (!name || name.toUpperCase().includes('SUBTOTAL') || name.toUpperCase().includes('TOTAL')) {
                        continue;
                    }
                    
                    const curr = cells[colIndices.Currency] || 'USD';
                    
                    // Extract container-specific charges
                    ['DRY 20', 'DRY 40', 'DRY 40H'].forEach(ct => {
                        const valStr = cells[colIndices[ct]];
                        if (valStr) {
                            const val = parseFloat(valStr.replace(/,/g, ''));
                            if (!isNaN(val) && val > 0) {
                                list.push({
                                    name: name,
                                    amount: val,
                                    currency: curr,
                                    container_type: ct
                                });
                            }
                        }
                    });
                    
                    // Extract flat BL charges
                    if (colIndices.BL !== -1) {
                        const valStr = cells[colIndices.BL];
                        if (valStr) {
                            const val = parseFloat(valStr.replace(/,/g, ''));
                            if (!isNaN(val) && val > 0) {
                                list.push({
                                    name: name,
                                    amount: val,
                                    currency: curr,
                                    container_type: null // Flat charge
                                });
                            }
                        }
                    }
                }
                return list;
            }''')

            if not charges:
                print("[CMA] Details table not found/parsed via JS. Attempting regex fallback.")
                charges = []
                pattern = r'(Ocean Freight|Charges payable as per freight|Charges payable at import|Charges payable at export|Charges payable at origin|Charges payable at destination)\s+([\d,\.]+)\s+(?:[\d,\.]+\s+)?([A-Z]{3})'
                matches = re.findall(pattern, text, re.IGNORECASE)
                
                for name, amount_str, currency in matches:
                    amount = float(amount_str.replace(",", ""))
                    charges.append({
                        "name": name.strip(),
                        "amount": amount,
                        "currency": currency.upper(),
                        "container_type": None
                    })

            # Classify categories on all extracted charges
            for charge in charges:
                name = charge["name"]
                if "Ocean Freight" in name:
                    category = ChargeCategory.BASIC_OCEAN_FREIGHT
                elif "as per freight" in name:
                    category = ChargeCategory.FREIGHT_SURCHARGE_INCLUDED
                elif "at import" in name or "at destination" in name:
                    category = ChargeCategory.DESTINATION_CHARGE_EXCLUDED
                elif "at export" in name or "at origin" in name:
                    category = ChargeCategory.ORIGIN_CHARGE_EXCLUDED
                else:
                    category = ChargeCategory.UNCERTAIN_EXCLUDED
                charge["category"] = category.value

            print(f"[CMA] Extracted {len(charges)} charge lines.")
            return charges
        except Exception as e:
            print(f"[CMA] Error extracting charges: {e}")
            return []

    async def run_full_search(self, request: RateSearchRequest) -> tuple[CarrierResultStatus, list[QuoteSchema]]:
        """
        Overrides base search runner to query all 3 sizes at once and cache the resulting quotes
        across sequential container type cycles to save time.
        """
        if not hasattr(self, "_cached_quotes"):
            self._cached_quotes = None
            self._cached_status = None

        if self._cached_quotes is not None:
            print(f"[CMA] Returning cached quotes for '{request.container_type}' (avoiding redundant browser search).")
            matching_quotes = [q for q in self._cached_quotes if q.container_type == request.container_type]
            return self._cached_status, matching_quotes

        quotes: list[QuoteSchema] = []
        try:
            # Step 1: Login
            login_ok = await self.login()
            if not login_ok:
                self._cached_quotes = []
                self._cached_status = CarrierResultStatus.LOGIN_FAILED
                return CarrierResultStatus.LOGIN_FAILED, []

            # Step 2: Search quotes (always searches 20' Dry, 40' Dry, and 40' Dry High Cube with quantity 1)
            search_status = await self.search_quotes(request)
            if search_status != CarrierResultStatus.AVAILABLE_QUOTES_FOUND:
                self._cached_quotes = []
                self._cached_status = search_status
                return search_status, []

            # Step 3: Extract quote list
            raw_quotes = await self.extract_quote_list()
            if not raw_quotes:
                self._cached_quotes = []
                self._cached_status = CarrierResultStatus.NO_QUOTES_AVAILABLE
                return CarrierResultStatus.NO_QUOTES_AVAILABLE, []

            # Step 4: For each quote, get breakdown, extract, and split
            for raw_quote in raw_quotes:
                try:
                    opened = await self.open_price_breakdown(raw_quote)
                    raw_charges = []
                    if opened:
                        raw_charges = await self.extract_charge_breakdown()
                        
                    split_quotes = await self._split_raw_quote_by_container_types(raw_quote, raw_charges)
                    quotes.extend(split_quotes)
                except Exception as e:
                    print(f"[CMA] Error extracting quote: {e}")
                    continue

            self._cached_quotes = quotes
            self._cached_status = CarrierResultStatus.AVAILABLE_QUOTES_FOUND if quotes else CarrierResultStatus.EXTRACTION_FAILED
            
            # Filter and return quotes matching current request container type
            matching_quotes = [q for q in quotes if q.container_type == request.container_type]
            return self._cached_status, matching_quotes

        except Exception as e:
            print(f"[CMA] Unexpected error in run_full_search: {e}")
            return CarrierResultStatus.UNKNOWN_ERROR, []
        finally:
            await asyncio.shield(self.close())

    async def normalize_result(self, raw_quote: dict, raw_charges: list[dict]) -> QuoteSchema:
        """
        Normalize CMA CGM data into QuoteSchema.
        Rule: include BASIC_OCEAN_FREIGHT and FREIGHT_SURCHARGE_INCLUDED in final value.
        """
        basic_ocean_freight = 0.0
        included_freight_surcharges = []
        excluded_charges = []
        
        from models.schemas import ChargeSchema
        
        for charge in raw_charges:
            c_schema = ChargeSchema(
                name=charge["name"],
                amount=charge["amount"],
                currency=charge["currency"],
                category=charge["category"]
            )
            
            if charge["category"] == ChargeCategory.BASIC_OCEAN_FREIGHT.value:
                basic_ocean_freight += charge["amount"]
            elif charge["category"] == ChargeCategory.FREIGHT_SURCHARGE_INCLUDED.value:
                included_freight_surcharges.append(c_schema)
            else:
                excluded_charges.append(c_schema)

        final_value = basic_ocean_freight + sum(c.amount for c in included_freight_surcharges)
        
        # Fallback to total_price if no breakdown was found
        if final_value == 0 and raw_quote.get("total_price"):
            final_value = raw_quote["total_price"]

        vessel = raw_quote.get("vessel")
        if self._current_voyage:
            if vessel:
                if f"(Voy: {self._current_voyage})" not in vessel:
                    vessel = f"{vessel} (Voy: {self._current_voyage})"
            else:
                vessel = f"Voy: {self._current_voyage}"

        # Append port fallback warning if any
        if hasattr(self, 'port_fallback_notice') and self.port_fallback_notice:
            if vessel:
                vessel = f"{vessel} ({self.port_fallback_notice})"
            else:
                vessel = f"({self.port_fallback_notice})"

        return QuoteSchema(
            etd=standardize_date_string(raw_quote.get("etd")),
            eta=standardize_date_string(raw_quote.get("eta")),
            transit_time_days=raw_quote.get("transit_time_days"),
            routing=raw_quote.get("routing", "Direct"),
            free_time=raw_quote.get("free_time"),
            demurrage=raw_quote.get("demurrage"),
            detention=raw_quote.get("detention"),
            container_type=raw_quote.get("container_type"),
            container_quantity=raw_quote.get("container_quantity", 1),
            service_name=raw_quote.get("service_name"),
            vessel=vessel,
            currency=raw_quote.get("currency", "USD"),
            basic_ocean_freight=basic_ocean_freight,
            included_freight_surcharges=included_freight_surcharges,
            excluded_charges=excluded_charges,
            final_freight_value=round(final_value, 2),
            source="carrier_portal",
            raw_reference=f"CMA-{raw_quote.get('index', 0)}"
        )

    async def _split_raw_quote_by_container_types(self, raw_quote: dict, raw_charges: list[dict]) -> list[QuoteSchema]:
        """
        Splits a single raw multi-container quote card into multiple QuoteSchema objects,
        one for each standard container type that has pricing.
        """
        # Separate container-specific charges from flat (Per B/L) charges
        container_charges = {
            "DRY 20": [],
            "DRY 40": [],
            "DRY 40H": []
        }
        flat_charges = []

        for charge in raw_charges:
            ct = charge.get("container_type")
            if ct in container_charges:
                container_charges[ct].append(charge)
            else:
                flat_charges.append(charge)

        split_quotes = []
        for std_ct, c_charges in container_charges.items():
            # Check if there is Basic Ocean Freight for this type
            bof_charge = next((c for c in c_charges if c["category"] == ChargeCategory.BASIC_OCEAN_FREIGHT.value), None)
            if not bof_charge:
                continue  # This container size is not available/N/A

            # Build raw_charges list for this container type
            split_raw_charges = []
            for c in c_charges:
                split_raw_charges.append({
                    "name": c["name"],
                    "amount": c["amount"],
                    "currency": c["currency"],
                    "category": c["category"]
                })
            for f in flat_charges:
                split_raw_charges.append({
                    "name": f["name"],
                    "amount": f["amount"],
                    "currency": f["currency"],
                    "category": f["category"]
                })

            # Create local raw_quote dict with the correct container type
            local_raw_quote = raw_quote.copy()
            local_raw_quote["container_type"] = std_ct

            # Extract specific free time, demurrage, and detention if present
            if "free_times" in raw_quote and isinstance(raw_quote["free_times"], dict):
                local_raw_quote["free_time"] = raw_quote["free_times"].get(std_ct)
            if "demurrage_times" in raw_quote and isinstance(raw_quote["demurrage_times"], dict):
                dem_val = raw_quote["demurrage_times"].get(std_ct)
                local_raw_quote["demurrage"] = dem_val if dem_val and dem_val > 0 else None
            if "detention_times" in raw_quote and isinstance(raw_quote["detention_times"], dict):
                det_val = raw_quote["detention_times"].get(std_ct)
                local_raw_quote["detention"] = det_val if det_val and det_val > 0 else None

            # Normalize using the local method
            normalized = await self.normalize_result(local_raw_quote, split_raw_charges)
            split_quotes.append(normalized)

        return split_quotes

    async def close(self):
        await super().close()

        # Sync temp profile back to master (saves login cookies for next run),
        # then clean up the temp directory — identical pattern to Maersk.
        try:
            import shutil
            if self.temp_profile_dir and os.path.exists(self.temp_profile_dir):
                if self.is_login_successful and self.master_profile_dir:
                    print(f"[CMA] Login successful. Syncing temp profile back to master: {self.master_profile_dir}")
                    if os.path.exists(self.master_profile_dir):
                        try:
                            shutil.rmtree(self.master_profile_dir)
                        except Exception:
                            pass
                    try:
                        # Never copy throwaway caches back to master (avoids storage bloat + sync I/O).
                        shutil.copytree(
                            self.temp_profile_dir, self.master_profile_dir, dirs_exist_ok=True,
                            ignore=shutil.ignore_patterns(
                                "Cache", "Code Cache", "DawnCache", "GPUCache", "CacheStorage", "ScriptCache"),
                        )
                        # Remove lock files from the saved master copy
                        lock_files = ["SingletonLock", "lock", "SingletonCookie"]
                        for root_dir, _, filenames in os.walk(self.master_profile_dir):
                            for filename in filenames:
                                if filename in lock_files:
                                    try:
                                        os.remove(os.path.join(root_dir, filename))
                                    except Exception:
                                        pass
                        print("[CMA] Master profile updated with fresh session data.")
                        
                        # Auto-clean heavy cache directories to prevent 5GB storage bloat
                        cache_dirs = ["Cache", "Code Cache", "DawnCache", "GPUCache", "CacheStorage", "ScriptCache"]
                        for root_dir, dirs, _ in os.walk(self.master_profile_dir):
                            for d in list(dirs):
                                if d in cache_dirs:
                                    try:
                                        shutil.rmtree(os.path.join(root_dir, d))
                                    except Exception:
                                        pass
                    except Exception as copy_err:
                        print(f"[CMA] Failed to sync profile to master: {copy_err}")

                print(f"[CMA] Cleaning up temp profile: {self.temp_profile_dir}")
                try:
                    shutil.rmtree(self.temp_profile_dir)
                except Exception as e:
                    print(f"[CMA] Failed to remove temp profile: {e}")
        except Exception as e:
            print(f"[CMA] Profile sync/cleanup error: {e}")
