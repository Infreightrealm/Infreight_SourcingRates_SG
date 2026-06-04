
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
from services.normalizer import normalize_quote
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
        "REEFER 20": "20' Reefer Standard",
        "REEFER 40": "40' Reefer Standard",
        "REEFER 40H": "40' Reefer High Cube",
    }

    def __init__(self):
        super().__init__()
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
                shutil.copytree(self.master_profile_dir, self.temp_profile_dir, dirs_exist_ok=True)
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
        
        await locator.scroll_into_view_if_needed()
        await self._random_mouse_move()
        await locator.hover()
        await self._human_delay(200, 500)
        await locator.click()

    async def _solve_datadome_slider(self) -> bool:
        """
        Human-in-the-Loop (HITL) CAPTCHA Bypass.
        Immediately pauses the automation script and waits up to 90 seconds for the user
        to manually slide the CAPTCHA inside the opened browser window.
        """
        frame_selector = 'iframe[src*="captcha-delivery.net"], iframe[src*="datadome.co"], iframe[src*="captcha-delivery.com"]'
        captcha_iframe = self.page.locator(frame_selector).first

        try:
            print("[CMA] [WARN] [ACTION REQUIRED] DataDome CAPTCHA/Verification Page Detected!")
            print("[CMA] [WARN] Please look at the opened Chrome browser window on your screen.")
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
        username = os.getenv("CMA_USERNAME") or os.getenv("CMA_CGM_USERNAME")
        password = os.getenv("CMA_PASSWORD") or os.getenv("CMA_CGM_PASSWORD")
        if not username or not password:
            print("[CMA] ERROR: Credentials not set in environment")
            return False

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

    async def _select_cma_dropdown_option(self, label: str, locode: str, cached_name: Optional[str] = None) -> bool:
        # Target individual <li> items only — NOT the <ul class="options"> container
        suggestion_sel = 'ul[role="listbox"] li, ul.options li, li[role="option"], [class*="suggestion"] li'
        try:
            # Wait for suggestions to appear in DOM (don't require "visible" — CMA's dropdown CSS can be tricky)
            await self.page.wait_for_selector(suggestion_sel, state="attached", timeout=10000)
            await self.page.wait_for_timeout(500)  # Let dropdown fully render
            suggestions = self.page.locator(suggestion_sel)
            count = await suggestions.count()
            
            print(f"[CMA] Found {count} suggestions in dropdown for {label} (LOCODE: {locode}, cached: '{cached_name}')")
            
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

    async def search_quotes(self, request: RateSearchRequest) -> CarrierResultStatus:
        try:
            print("[CMA] Starting search...")
            
            # Initialize fallback notice
            self.port_fallback_notice = None
            
            # --- ORIGIN ---
            origin_locode = resolve_port_for_carrier(request.origin, "cma")
            if not origin_locode or len(origin_locode) != 5 or not origin_locode.isupper():
                origin_locode = self._extract_port_code(request.origin)
                if len(origin_locode) != 5 or not origin_locode.isupper():
                    from services.port_manager import search_port
                    ports = search_port(request.origin)
                    if ports:
                        origin_locode = ports[0]['code']

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
            dest_locode = resolve_port_for_carrier(request.destination, "cma")
            if not dest_locode or len(dest_locode) != 5 or not dest_locode.isupper():
                dest_locode = self._extract_port_code(request.destination)
                if len(dest_locode) != 5 or not dest_locode.isupper():
                    from services.port_manager import search_port
                    ports = search_port(request.destination)
                    if ports:
                        dest_locode = ports[0]['code']

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

            print(f"[CMA] Filling Destination: '{dest_query}' (locode: {dest_locode}, cached: '{dest_cached}')")
            dest_field = self.page.locator('input[placeholder*="Name / Code / Port" i]').nth(1)
            await dest_field.click()
            await dest_field.fill("")
            await dest_field.type(dest_query, delay=30)
            await self.page.wait_for_timeout(2000)

            if not await self._select_cma_dropdown_option("Destination", dest_locode, dest_cached):
                return CarrierResultStatus.INVALID_SEARCH_INPUT
            
            print(f"[CMA] Destination selected: {dest_locode}")

            # --- CONTAINER TYPE & SIZE ---
            cma_container = self.CONTAINER_TYPE_MAP.get(request.container_type)
            if not cma_container:
                print(f"[CMA] Container type {request.container_type} not mapped.")
                return CarrierResultStatus.INVALID_SEARCH_INPUT

            print(f"[CMA] Selecting container: '{cma_container}' (internal: {request.container_type})")
            await self.page.wait_for_timeout(2000)

            # CMA displays individual container items like "20' DRY STANDARD", "40' DRY HIGH CUBE"
            # each with its own "Add" button. We need to find the SPECIFIC item and click its Add.
            container_selected = False
            target_upper = cma_container.upper()  # e.g., "40' DRY HIGH CUBE"
            
            # Extract key identifiers: size (40), type (DRY/REEFER), variant (STANDARD/HIGH CUBE)
            # We'll match items that contain ALL these parts
            target_parts = target_upper.replace("'", "").split()  # ["40", "DRY", "HIGH", "CUBE"]

            # Strategy: Find all items with "Add" text nearby and match the right one
            # Look for elements that contain our container name and have a sibling/child Add button
            try:
                # Get all text blocks in the container section
                items = self.page.locator('text=/\\d+.*(?:DRY|REEFER|FLAT|OPEN)/i')
                item_count = await items.count()
                print(f"[CMA] Found {item_count} container items on page")
                
                for i in range(item_count):
                    item = items.nth(i)
                    try:
                        item_text = (await item.inner_text(timeout=1000)).strip().upper()
                        # Check if this item matches our target
                        item_clean = item_text.replace("'", "")
                        if all(part in item_clean for part in target_parts):
                            print(f"[CMA] Found matching container item: '{item_text}'")
                            # Click the Add button - try parent first, then siblings
                            parent = item.locator('..')
                            add_btn = parent.locator('button:has-text("Add"), button:has-text("+")')
                            if await add_btn.count() > 0:
                                await add_btn.first.click()
                                container_selected = True
                                print(f"[CMA] Clicked Add for: '{item_text}'")
                                break
                            # Try grandparent
                            grandparent = parent.locator('..')
                            add_btn = grandparent.locator('button:has-text("Add"), button:has-text("+")')
                            if await add_btn.count() > 0:
                                await add_btn.first.click()
                                container_selected = True
                                print(f"[CMA] Clicked Add (grandparent) for: '{item_text}'")
                                break
                    except:
                        continue
            except Exception as e:
                print(f"[CMA] Container text scan error: {e}")

            # Fallback: use Playwright's has-text with the exact name
            if not container_selected:
                try:
                    # Find the smallest div containing our container name AND an Add button
                    item_locator = self.page.locator(f'div:has-text("{cma_container}")').filter(
                        has=self.page.locator('button:has-text("Add"), button:has-text("+")')
                    )
                    count = await item_locator.count()
                    if count > 0:
                        # Use the last (most specific/smallest) match
                        target = item_locator.last
                        await target.locator('button:has-text("Add"), button:has-text("+")').first.click()
                        container_selected = True
                        print(f"[CMA] Container selected via fallback div match")
                except Exception as e:
                    print(f"[CMA] Container fallback failed: {e}")

            if not container_selected:
                print(f"[CMA] Could not find container type '{cma_container}'")
                await self.page.screenshot(path="cma_container_fail.png")
                print("[CMA] Saved debug screenshot to cma_container_fail.png")
                return CarrierResultStatus.INVALID_SEARCH_INPUT

            await self.page.wait_for_timeout(1500)

            # --- CARGO WEIGHT ---
            # CMA's weight field is inside the selected container card, below "Max Net Weight" label.
            # The input has NO placeholder/name/id — the "ex. 10 000 KGM" text is pure CSS.
            # Minimum weight for CMA is 10000 KGM
            weight_kg = max(int(request.weight_per_container_kg), 10000)
            print(f"[CMA] Entering cargo weight: {weight_kg} KGM...")

            weight_set = await self._set_cma_cargo_weight(weight_kg, cma_container)
            if not weight_set:
                print("[CMA] Weight field NOT filled - saving screenshot.")
                await self.page.screenshot(path="cma_weight_fail.png")
                return CarrierResultStatus.INVALID_SEARCH_INPUT

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
            try:
                await self.page.wait_for_selector('div[class*="schedules-result"], div[class*="sailing-result"], article[class*="schedule"], div[class*="result"], div[class*="quote"]', timeout=30000)
                print("[CMA] Results loaded.")
                return CarrierResultStatus.AVAILABLE_QUOTES_FOUND
            except Exception:
                page_text = await self.page.inner_text('body')
                if 'no result' in page_text.lower() or 'no schedule' in page_text.lower():
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
            max_clicks = 5
            clicks = 0
            
            while clicks < max_clicks:
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
            card = quote_ref["card_locator"]
            await card.scroll_into_view_if_needed()
            await self._random_mouse_move()
            details_btn = card.locator('label:has-text("Details"), button:has-text("Details")').first
            
            # Fast fail if Details button doesn't exist (e.g. for "Sold out" cards)
            if not await details_btn.is_visible(timeout=2000):
                print(f"[CMA] Details button not visible for quote. Possibly Sold out.")
                return False
                
            await self._hover_and_click(details_btn)
            await self._human_delay(1500, 2500)

            # --- Extract Free Time from D&D tab ---
            try:
                dd_tab = card.locator('button:has-text("D&D"), [role="tab"]:has-text("D&D")').first
                if await dd_tab.is_visible(timeout=2000):
                    await self._hover_and_click(dd_tab)
                    await self._human_delay(1000, 1500)
                    
                    dd_text = await card.inner_text()
                    # Look for Import free time, skip Export free time
                    match = re.search(r'Import free time.*?(\d+)\s+Calendar', dd_text, re.IGNORECASE | re.DOTALL)
                    if match:
                        quote_ref["free_time"] = int(match.group(1))
                        print(f"[CMA] Extracted Import Free Time: {quote_ref['free_time']} days")
                    else:
                        print("[CMA] D&D tab opened but could not parse Import free time.")
            except Exception as e:
                print(f"[CMA] Error extracting free time from D&D: {e}")

            # --- Switch back to Rate tab for charge breakdown ---
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
            
            charges = []
            
            # Pattern matching key charge groups and their amounts/currencies dynamically
            pattern = r'(Ocean Freight|Charges payable as per freight|Charges payable at import|Charges payable at export|Charges payable at origin|Charges payable at destination)\s+([\d,]+)\s+([A-Z]{3})'
            matches = re.findall(pattern, text, re.IGNORECASE)
            
            for name, amount_str, currency in matches:
                amount = float(amount_str.replace(",", ""))
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
                
                charges.append({
                    "name": name.strip(),
                    "amount": amount,
                    "currency": currency.upper(),
                    "category": category.value
                })
            
            if not charges:
                # Fallback: extract all rows from table
                rows = self.current_card.locator('tr, [class*="charge-row"]')
                for i in range(await rows.count()):
                    row_text = await rows.nth(i).inner_text()
                    amt_match = re.search(r'(\d[\d,]+)\s*$', row_text.strip())
                    if amt_match:
                        # Very crude fallback, better to use regex above
                        pass

            print(f"[CMA] Extracted {len(charges)} charge lines.")
            return charges
        except Exception as e:
            print(f"[CMA] Error extracting charges: {e}")
            return []

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
            etd=raw_quote.get("etd"),
            eta=raw_quote.get("eta"),
            transit_time_days=raw_quote.get("transit_time_days"),
            routing=raw_quote.get("routing", "Direct"),
            free_time=raw_quote.get("free_time"),
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

    async def close(self):
        try:
            if self.page: await self.page.close()
            if self.context: await self.context.close()
            if self.browser: await self.browser.close()
            if self.playwright: await self.playwright.stop()
        except Exception:
            pass

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
                        shutil.copytree(self.temp_profile_dir, self.master_profile_dir, dirs_exist_ok=True)
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
