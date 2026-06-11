
"""
ONE (Ocean Network Express) Live Connector — Playwright automation.

Credentials read from env: ONE_USERNAME, ONE_PASSWORD
Never hardcode credentials.
"""
import os
import re
from datetime import date, datetime, timedelta
from typing import Optional
from playwright.async_api import async_playwright
from models.schemas import RateSearchRequest, QuoteSchema, CarrierResultStatus
from services.charge_classifier import classify_charge
from services.normalizer import normalize_quote
from services.port_manager import resolve_port_for_carrier, get_carrier_search_query, get_cached_carrier_port, set_cached_carrier_port
from carriers.base_connector import BaseCarrierConnector


class ONEConnector(BaseCarrierConnector):
    carrier_code = "ONE"
    carrier_name = "Ocean Network Express"
    LOGIN_URL = "https://ecomm.one-line.com/one-ecom/login"
    QUOTE_URL = "https://ecomm.one-line.com/one-ecom/prices/one-quote-booking"

    # Maps internal container type codes to ONE portal dropdown labels.
    # ONE uses the same naming convention as our internal codes \u2014 verified live from portal.
    CONTAINER_TYPE_MAP = {
        "DRY 20":    "DRY 20",
        "DRY 40":    "DRY 40",
        "DRY 40H":   "DRY 40H",
        "DRY 45":    "DRY 40H",     # No 45' option on ONE; closest is 40H
        "REEFER 20": "REEFER 20",
        "REEFER 40": "REEFER 40H",  # No plain REEFER 40 on ONE; closest is 40H
        "REEFER 40H":"REEFER 40H",
    }

    def __init__(self):
        super().__init__()
        self.playwright = None

    async def _init_browser(self):
        is_prod = os.name != "nt"
        self.playwright = await async_playwright().start()
        
        # Thread-safe virtual display environment injection
        browser_env = os.environ.copy()
        if is_prod:
            browser_env["DISPLAY"] = ":101"

        self.browser = await self.playwright.chromium.launch(
            headless=False,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding",
            ],
            env=browser_env,
        )
        self.context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            ignore_https_errors=True,
        )
        self.page = await self.context.new_page()
        self.page.set_default_timeout(30000)

    def _resolve_departure_date(self, departure_date_value: str) -> date:
        if not departure_date_value:
            return date.today() + timedelta(days=1)

        normalized_value = departure_date_value.strip().lower()
        if normalized_value == "tomorrow":
            return date.today() + timedelta(days=1)
        if normalized_value == "today":
            return date.today()

        try:
            return date.fromisoformat(departure_date_value)
        except Exception:
            pass

        for pattern in ("%d/%m/%Y", "%m/%d/%Y", "%d %b %Y", "%d %B %Y"):
            try:
                return datetime.strptime(departure_date_value, pattern).date()
            except Exception:
                continue

        print(f"[ONE] Could not parse departure date '{departure_date_value}', defaulting to tomorrow")
        return date.today() + timedelta(days=1)

    async def _clear_overlays(self) -> None:
        try:
            # Use JS evaluation to instantly click the Skip button to prevent blocking the Playwright thread
            await self.page.evaluate('''() => {
                // Clear any selection/highlighting first
                window.getSelection()?.removeAllRanges();

                const skipBtns = Array.from(document.querySelectorAll('button, a, [role="button"], span, div')).filter(el => {
                    const text = (el.textContent || '').trim().toLowerCase();
                    if (text !== 'skip') return false;
                    
                    // Exclude accessibility skip links pointing to same-page anchors
                    if (el.tagName === 'A' && (el.getAttribute('href') || '').startsWith('#')) {
                        return false;
                    }
                    return true;
                });
                if (skipBtns.length > 0) {
                    skipBtns[0].click();
                }
            }''')
            await self.page.wait_for_timeout(300)
            
            # Also attempt standard playwright click if it's still there
            skip_btn = self.page.locator('button:has-text("Skip"), [role="button"]:has-text("Skip"), a:has-text("Skip"):not([href^="#"])').first
            if await skip_btn.is_visible(timeout=200):
                await skip_btn.click(force=True)
                await self.page.wait_for_timeout(500)

            # Clear selection one more time in case the click triggered any text highlighting
            await self.page.evaluate('window.getSelection()?.removeAllRanges()')
        except Exception:
            pass

    async def _fill_first_visible(self, selectors: str, value: str, label: str) -> bool:
        try:
            field = self.page.locator(selectors).first
            await field.wait_for(state="visible", timeout=10_000)
            try:
                await field.fill(value)
            except Exception:
                await field.click()
                await field.press("Control+A")
                await field.type(value, delay=25)
            print(f"[ONE] {label} filled: {value}")
            return True
        except Exception as e:
            print(f"[ONE] {label} input not found or failed: {e}")
            return False

    async def _set_departure_date(self, target_date: date) -> bool:
        date_candidates = [
            target_date.isoformat(),
            target_date.strftime("%d/%m/%Y"),
            target_date.strftime("%m/%d/%Y"),
            target_date.strftime("%d %b %Y"),
            target_date.strftime("%d %B %Y"),
        ]

        date_input_sel = (
            'input[type="date"], '
            'input[placeholder*="date" i], '
            'input[aria-label*="date" i], '
            'input[name*="date" i], '
            'input[id*="date" i]'
        )

        try:
            date_field = self.page.locator(date_input_sel).first
            await date_field.wait_for(state="visible", timeout=10_000)
            print("[ONE] Departure date field found, trying direct input...")
            for candidate in date_candidates:
                try:
                    await date_field.fill(candidate)
                    await date_field.press("Enter")
                    print(f"[ONE] Departure date entered: {candidate}")
                    return True
                except Exception:
                    continue
        except Exception as e:
            print(f"[ONE] Departure date input not directly editable: {e}")

        calendar_button_sel = (
            'button[aria-label*="calendar" i], '
            'button[title*="calendar" i], '
            '[class*="calendar" i]'
        )
        try:
            print("[ONE] Clicking calendar icon for departure date...")
            await self.page.locator(calendar_button_sel).first.click()
            await self.page.wait_for_timeout(1000)

            day_label = str(target_date.day)
            day_selectors = [
                f'button:has-text("{day_label}")',
                f'[role="gridcell"]:has-text("{day_label}")',
                f'td:has-text("{day_label}")',
                f'[aria-label*="{target_date.strftime("%d %B %Y")}" i]',
                f'[aria-label*="{target_date.strftime("%B %d, %Y")}" i]',
            ]

            for selector in day_selectors:
                try:
                    await self.page.locator(selector).first.click(timeout=5000)
                    print(f"[ONE] Departure date selected from calendar: {target_date.isoformat()}")
                    return True
                except Exception:
                    continue
        except Exception as e:
            print(f"[ONE] Calendar picker selection failed: {e}")

        print("[ONE] Unable to set departure date")
        return False

    async def _click_submit(self) -> bool:
        submit_sel = 'button:has-text("GetQuote"), button:has-text("Get Quote"), button:has-text("Search Rates"), button:has-text("View Quote"), button:has-text("view Quote"), button[type="submit"]'
        try:
            submit_button = self.page.locator(submit_sel).first
            await submit_button.wait_for(state="visible", timeout=10_000)
            await submit_button.click()
            print("[ONE] Search submitted")
            return True
        except Exception as e:
            print(f"[ONE] Failed to click submit button: {e}")
            return False

    async def _select_dropdown_option(self, label: str, value: str, locode: Optional[str] = None) -> bool:
        """
        Tries to click a matching option from ONE's visible dropdown.
        Returns True only if an option was actually clicked.
        Returns False if no match was found — caller must handle the fallback.
        NOTE: We deliberately do NOT press Enter as a fallback here because ONE requires
        an explicit dropdown click to confirm the port and unlock subsequent fields.
        """
        normalized_value = value.strip().upper()
        option_candidates = [normalized_value]
        if "," in normalized_value:
            option_candidates.append(normalized_value.split(",", 1)[0].strip())

        def _extract_locode_for_cache(option_text_upper: str, original_locode: str) -> str:
            """
            Extract the LOCODE that ONE actually uses from option text, so the cache
            stores a valid ONE search query (e.g. 'CNSHA') not the full label text.
            Falls back to original_locode if nothing found.
            """
            import re as _re
            # ONE option text typically contains the LOCODE as a standalone 5-letter code
            matches = _re.findall(r'\b([A-Z]{5})\b', option_text_upper)
            if matches:
                # Prefer the one that matches our original locode prefix (same country)
                country = (original_locode or '')[:2].upper()
                for m in matches:
                    if country and m.startswith(country):
                        return m
                return matches[0]  # return first found
            return original_locode or value

        try:
            try:
                await self.page.locator('[role="option"]').first.wait_for(state="visible", timeout=5000)
            except Exception:
                pass
            options = self.page.locator('[role="option"]:visible')
            option_count = await options.count()
            print(f"[ONE] {label}: {option_count} dropdown options visible (searching for '{value}', locode='{locode}')")

            # 1. Try strict LOCODE matching first (handles cases where ONE shows a different LOCODE)
            if locode:
                normalized_locode = locode.strip().upper()
                locode_candidates = [normalized_locode]
                # Also try spaced format (e.g. "NL RTM" instead of "NLRTM")
                if len(normalized_locode) == 5:
                    locode_candidates.append(f"{normalized_locode[:2]} {normalized_locode[2:]}")

                for index in range(option_count):
                    option = options.nth(index)
                    option_text = (await option.inner_text()).strip().upper()
                    if locode == "AUMEL" and ("AUMELAS" in option_text or "FRYUH" in option_text):
                        continue
                    if any(cand in option_text for cand in locode_candidates):
                        await option.click(force=True)
                        cache_val = _extract_locode_for_cache(option_text, locode)
                        print(f"[ONE] {label} selected by LOCODE match '{locode}': ONE code='{cache_val}'")
                        set_cached_carrier_port("one", locode, cache_val)
                        return True

            # 2. Name-based EXACT WORD boundary matching
            import re as _re
            for index in range(option_count):
                option = options.nth(index)
                option_text = (await option.inner_text()).strip().upper()
                if locode == "AUMEL" and ("AUMELAS" in option_text or "FRYUH" in option_text):
                    continue
                
                # Use regex  boundary to prevent "ADEN" from matching "ADENAU"
                match_found = False
                for candidate in option_candidates:
                    if _re.search(rf"\b{_re.escape(candidate)}\b", option_text):
                        match_found = True
                        break
                        
                if match_found:
                    await option.click(force=True)
                    if locode:
                        cache_val = _extract_locode_for_cache(option_text, locode)
                        print(f"[ONE] {label} selected by name match '{value}': ONE code='{cache_val}'")
                        set_cached_carrier_port("one", locode, cache_val)
                    return True

            # 3. Playwright filter-based fallback using Exact Word boundary regex
            import re as _re
            for candidate in option_candidates:
                try:
                    filtered_options = self.page.locator('[role="option"]').filter(has_text=_re.compile(rf"\b{_re.escape(candidate)}\b", _re.IGNORECASE))
                    filtered_count = await filtered_options.count()
                    matched_option = None
                    matched_text = ""
                    for idx in range(filtered_count):
                        opt = filtered_options.nth(idx)
                        opt_text = (await opt.inner_text()).strip().upper()
                        if locode == "AUMEL" and ("AUMELAS" in opt_text or "FRYUH" in opt_text):
                            continue
                        matched_option = opt
                        matched_text = opt_text
                        break

                    if matched_option:
                        await matched_option.click(force=True)
                        if locode:
                            cache_val = _extract_locode_for_cache(matched_text, locode)
                            print(f"[ONE] {label} selected by filter: {candidate} -> ONE code='{cache_val}'")
                            set_cached_carrier_port("one", locode, cache_val)
                        return True
                except Exception:
                    continue

            print(f"[ONE] {label}: no dropdown match found for '{value}' (locode='{locode}')")
            return False
        except Exception as e:
            print(f"[ONE] {label} selection failed: {e}")
            return False

    async def login(self) -> bool:
        username = os.getenv("ONE_USERNAME")
        password = os.getenv("ONE_PASSWORD")
        if not username or not password:
            print("[ONE] ERROR: Credentials not set in environment")
            return False
        try:
            await self._init_browser()
            print("[ONE] Navigating to login page...")
            await self.page.goto(self.LOGIN_URL, wait_until="domcontentloaded", timeout=30000)
            print(f"[ONE] Page loaded: {self.page.url}")
            await self.page.wait_for_timeout(1000)  # Wait for JS to render
            
            # TODO: Verify selectors against ONE ecommerce portal
            userId_sel = 'input[name="userId"], input[id="userId"], input[name="username"]'
            print(f"[ONE] Looking for userId input with selector: {userId_sel}")
            try:
                await self.page.wait_for_selector(userId_sel, timeout=10000)
                print("[ONE] UserId input found, filling...")
                await self.page.locator(userId_sel).first.fill(username)
                print(f"[ONE] UserId filled: {username}")
            except Exception as e:
                print(f"[ONE] UserId input not found: {e}")
                return False
            
            pwd_sel = 'input[name="password"], input[id="password"], input[type="password"]'
            try:
                await self.page.locator(pwd_sel).first.fill(password)
                print("[ONE] Password filled")
            except Exception as e:
                print(f"[ONE] Password input not found: {e}")
                return False
            
            print("[ONE] Clicking submit button...")
            submit_sel = 'button[type="submit"], button:has-text("Login"), button:has-text("Sign in")'
            try:
                await self.page.locator(submit_sel).first.click()
                print("[ONE] Submit button clicked successfully")
            except Exception as e:
                print(f"[ONE] Failed to click submit button: {e}")
                # Try to get page content for debugging
                page_html = await self.page.content()
                if "error" in page_html.lower():
                    print("[ONE] ERROR message found in page HTML")
                return False
            
            print("[ONE] Waiting for navigation after submit...")
            try:
                # Wait for page to navigate away from login (to OAuth callback or dashboard)
                await self.page.wait_for_url(lambda url: "login" not in url.lower() and "sign" not in url.lower(), timeout=12000)
                print(f"[ONE] Navigation successful! Current URL: {self.page.url}")
                
                # If on OAuth callback, wait for final redirect to dashboard
                if "callback" in self.page.url.lower() or "authorization" in self.page.url.lower():
                    print("[ONE] On OAuth callback page, waiting for dashboard redirect...")
                    await self.page.wait_for_timeout(3000)  # Wait for redirect
                    # Try to wait for page to fully load or redirect
                    try:
                        await self.page.wait_for_url(lambda url: "callback" not in url.lower(), timeout=10000)
                        print(f"[ONE] Redirected to dashboard: {self.page.url}")
                    except:
                        # Even if redirect times out, login was successful
                        print("[ONE] OAuth callback processed, assuming success")
                
                print("[ONE] Login successful!")
                return True
            except Exception as e:
                print(f"[ONE] Navigation timeout: {e}")
                # Check if we're still on login page
                current_url = self.page.url
                print(f"[ONE] Current URL after wait: {current_url}")
                
                # Try to capture any error messages on the page
                try:
                    page_html = await self.page.content()
                    if "invalid" in page_html.lower():
                        print("[ONE] INVALID credentials message found in page")
                    if "error" in page_html.lower():
                        print("[ONE] ERROR message found in page")
                    if "wrong" in page_html.lower():
                        print("[ONE] WRONG password message found in page")
                except:
                    pass
                
                if "login" in current_url.lower() or "sign" in current_url.lower():
                    print("[ONE] Login failed — still on login page after submit")
                    return False
                else:
                    print("[ONE] URL changed away from login, assuming success")
                    return True
        except Exception as e:
            print(f"[ONE] Login failed: {e}")
            return False

    def _extract_port_code(self, text: str) -> str:
        """Extracts 5-letter UN/LOCODE from strings like 'Singapore (SGSIN)'."""
        if not text: return ""
        match = re.search(r'\(([A-Z]{5})\)', text)
        if match:
            return match.group(1)
        # Fallback: if it's already a 5-letter code
        clean = text.strip()
        if len(clean) == 5 and clean.isupper():
            return clean
        return text

    async def search_quotes(self, request: RateSearchRequest) -> CarrierResultStatus:
        try:
            print("[ONE] Starting search, navigating to spot rate page...")
            # Use domcontentloaded instead of networkidle to avoid timeouts on portals with continuous tracking
            await self.page.goto(self.QUOTE_URL, wait_until="domcontentloaded", timeout=30000)
            print(f"[ONE] Spot rate page loaded: {self.page.url}")
            await self.page.wait_for_timeout(2500)  # Wait for JS to fully render form
            await self._clear_overlays()

            target_date = self._resolve_departure_date(request.departure_date)
            target_date_text = target_date.isoformat()

            # Initialize fallback notice
            self.port_fallback_notice = None

            # Resolve origin locode for strict dropdown selection matching
            origin_locode = resolve_port_for_carrier(request.origin, "one")
            if not origin_locode or len(origin_locode) != 5 or not origin_locode.isupper():
                origin_locode = self._extract_port_code(request.origin)
                if len(origin_locode) != 5 or not origin_locode.isupper():
                    from services.port_manager import search_port
                    ports = search_port(request.origin)
                    if ports:
                        origin_locode = ports[0]['code']
            
            self.origin_locode = origin_locode

            origin_cached = get_cached_carrier_port("one", origin_locode) if origin_locode else None
            origin_selected = False

            await self._clear_overlays()
            try:
                origin_field = self.page.locator('input[placeholder="Please search location"]').first
                await origin_field.wait_for(state="attached", timeout=15000)

                if origin_cached:
                    # Use the cached carrier-specific spelling directly
                    print(f"[ONE] Origin (cached): typing '{origin_cached}' for LOCODE '{origin_locode}'")
                    await origin_field.click(force=True)
                    await self._clear_overlays()
                    await self.page.keyboard.type(origin_cached, delay=25)
                    await self.page.wait_for_timeout(1500)
                    origin_selected = await self._select_dropdown_option("Origin", origin_cached, origin_locode)

                if not origin_selected:
                    # Step 1: Try typing LOCODE directly (works if ONE recognises this LOCODE)
                    origin_locode_query = origin_locode if origin_locode else request.origin
                    print(f"[ONE] Origin (step 1): typing LOCODE '{origin_locode_query}'")
                    await origin_field.click(force=True)
                    await self._clear_overlays()
                    await self.page.keyboard.press("Control+A")
                    await self.page.keyboard.press("Backspace")
                    await self.page.keyboard.type(origin_locode_query, delay=25)
                    await self.page.wait_for_timeout(1500)
                    origin_selected = await self._select_dropdown_option("Origin", origin_locode_query, origin_locode)

                if not origin_selected and origin_locode:
                    # Step 2: LOCODE not recognised by ONE — fall back to port name from our database
                    from services.port_manager import get_port_by_code
                    port_obj = get_port_by_code(origin_locode)
                    origin_name = port_obj.get('name_ascii') or port_obj.get('name') if port_obj else None
                    if origin_name:
                        print(f"[ONE] Origin (step 2): LOCODE unknown to ONE, trying port name '{origin_name}'")
                        await origin_field.click(force=True)
                        await self._clear_overlays()
                        await self.page.keyboard.press("Control+A")
                        await self.page.keyboard.press("Backspace")
                        await self.page.keyboard.type(origin_name, delay=25)
                        await self.page.wait_for_timeout(1500)
                        origin_selected = await self._select_dropdown_option("Origin", origin_name, origin_locode)

                if not origin_selected:
                    print(f"[ONE] Origin: all input strategies failed for '{request.origin}'")
                    return CarrierResultStatus.INVALID_SEARCH_INPUT
            except Exception as e:
                print(f"[ONE] Origin combobox failed: {e}")
                return CarrierResultStatus.INVALID_SEARCH_INPUT

            # Resolve destination locode for strict dropdown selection matching
            destination_locode = resolve_port_for_carrier(request.destination, "one")
            if not destination_locode or len(destination_locode) != 5 or not destination_locode.isupper():
                destination_locode = self._extract_port_code(request.destination)
                if len(destination_locode) != 5 or not destination_locode.isupper():
                    from services.port_manager import search_port
                    ports = search_port(request.destination)
                    if ports:
                        destination_locode = ports[0]['code']
            
            self.destination_locode = destination_locode

            destination_cached = get_cached_carrier_port("one", destination_locode) if destination_locode else None
            destination_selected = False

            # Check if Ain Sukhna -> Alexandria fallback occurred
            if "EGAIS" in (request.origin.upper() if request.origin else "") or "SUKHNA" in (request.origin.upper() if request.origin else ""):
                if origin_locode == "EGALY":
                    self.port_fallback_notice = "Ain Sukhna fell back to Alexandria"
            elif "EGAIS" in (request.destination.upper() if request.destination else "") or "SUKHNA" in (request.destination.upper() if request.destination else ""):
                if destination_locode == "EGALY":
                    self.port_fallback_notice = "Ain Sukhna fell back to Alexandria"

            await self._clear_overlays()
            try:
                destination_field = self.page.locator('input[placeholder="Please search location"]').last
                await destination_field.wait_for(state="attached", timeout=15000)

                if destination_cached:
                    # Use cached carrier-specific spelling
                    print(f"[ONE] Destination (cached): typing '{destination_cached}' for LOCODE '{destination_locode}'")
                    await destination_field.click(force=True)
                    await self._clear_overlays()
                    await self.page.keyboard.type(destination_cached, delay=25)
                    await self.page.wait_for_timeout(1500)
                    destination_selected = await self._select_dropdown_option("Destination", destination_cached, destination_locode)

                if not destination_selected:
                    # Step 1: Try typing LOCODE directly
                    dest_locode_query = destination_locode if destination_locode else request.destination
                    print(f"[ONE] Destination (step 1): typing LOCODE '{dest_locode_query}'")
                    await destination_field.click(force=True)
                    await self._clear_overlays()
                    await self.page.keyboard.press("Control+A")
                    await self.page.keyboard.press("Backspace")
                    await self.page.keyboard.type(dest_locode_query, delay=25)
                    await self.page.wait_for_timeout(1500)
                    destination_selected = await self._select_dropdown_option("Destination", dest_locode_query, destination_locode)

                if not destination_selected and destination_locode:
                    # Step 2: Fall back to port name from our database
                    from services.port_manager import get_port_by_code
                    port_obj = get_port_by_code(destination_locode)
                    dest_name = port_obj.get('name_ascii') or port_obj.get('name') if port_obj else None
                    if dest_name:
                        print(f"[ONE] Destination (step 2): LOCODE unknown to ONE, trying port name '{dest_name}'")
                        await destination_field.click(force=True)
                        await self._clear_overlays()
                        await self.page.keyboard.press("Control+A")
                        await self.page.keyboard.press("Backspace")
                        await self.page.keyboard.type(dest_name, delay=25)
                        await self.page.wait_for_timeout(1500)
                        destination_selected = await self._select_dropdown_option("Destination", dest_name, destination_locode)

                if not destination_selected:
                    print(f"[ONE] Destination: all input strategies failed for '{request.destination}'")
                    return CarrierResultStatus.INVALID_SEARCH_INPUT
            except Exception as e:
                print(f"[ONE] Destination combobox failed: {e}")
                return CarrierResultStatus.INVALID_SEARCH_INPUT

            # --- JS BYPASS FOR STUCK LOADING DIALOG ---
            # We must immediately remove the stuck welcome/loading modal and backdrop to destroy the FocusTrap
            # and allow the background form fields to transition out of their "disabled" state!
            await self._clear_overlays()

            # Wait for equipment dropdown to become enabled (only unlocks after both ports are confirmed and fully loaded in background)
            print("[ONE] Waiting for Equipment Type dropdown to become enabled...")
            try:
                await self.page.wait_for_function(
                    """() => {
                        const el = document.querySelector('[role="combobox"][placeholder="Select an Equipment Type"], #downshift-0-input');
                        return el && !el.disabled;
                    }""",
                    timeout=60000
                )
                print("[ONE] Equipment dropdown is now enabled.")
            except Exception:
                print("[ONE] Timed out waiting for equipment dropdown — proceeding anyway.")

            one_container_label = self.CONTAINER_TYPE_MAP.get(request.container_type, request.container_type)
            print(f"[ONE] Setting Equipment Type: '{request.container_type}' -> ONE label: '{one_container_label}'")
            try:
                equipment_field = self.page.get_by_role("combobox", name="Select an Equipment Type").first
                await equipment_field.click()
                await self.page.wait_for_timeout(800)

                # Iterate through all visible options and find the best match
                # (avoids apostrophe/quoting issues with filter(has_text=...))
                eq_options = self.page.locator('[role="option"]:visible')
                eq_count = await eq_options.count()
                print(f"[ONE] Equipment dropdown opened: {eq_count} options visible")
                eq_selected = False

                def _norm_eq(s):
                    return s.strip().upper().replace("\u2019", "'").replace("\u2018", "'")

                label_norm = _norm_eq(one_container_label)

                # Pass 1: exact match
                for i in range(eq_count):
                    opt = eq_options.nth(i)
                    opt_text = (await opt.inner_text()).strip()
                    if _norm_eq(opt_text) == label_norm:
                        await opt.click()
                        print(f"[ONE] Equipment selected (exact): '{opt_text}'")
                        eq_selected = True
                        break

                # Pass 2: option text starts with our label (e.g. 'DRY 40H' matches 'DRY 40H STD')
                if not eq_selected:
                    for i in range(eq_count):
                        opt = eq_options.nth(i)
                        opt_text = (await opt.inner_text()).strip()
                        opt_norm = _norm_eq(opt_text)
                        if opt_norm.startswith(label_norm) or label_norm.startswith(opt_norm + " "):
                            await opt.click()
                            print(f"[ONE] Equipment selected (prefix): '{opt_text}'")
                            eq_selected = True
                            break

                if not eq_selected:
                    available = [(await eq_options.nth(i).inner_text()).strip() for i in range(eq_count)]
                    print(f"[ONE] Equipment: no match for '{one_container_label}'. Available: {available}")
                    return CarrierResultStatus.INVALID_SEARCH_INPUT

                await self.page.wait_for_timeout(750)
            except Exception as e:
                print(f"[ONE] Equipment combobox failed: {e}")
                return CarrierResultStatus.INVALID_SEARCH_INPUT

            print(f"[ONE] Setting Quantity: {request.container_quantity}")
            try:
                quantity_field = self.page.locator('input[type="number"], input[aria-label*="quantity" i], input[name*="quantity" i], input[id*="quantity" i]').first
                await quantity_field.wait_for(state="visible", timeout=10_000)
                await quantity_field.fill(str(request.container_quantity))
            except Exception:
                print("[ONE] Quantity field not directly editable — continuing")

            print(f"[ONE] Setting Cargo Weight: {int(request.weight_per_container_kg)}")
            try:
                weight_field = self.page.locator('input[placeholder="0"], input[aria-label*="weight" i], input[name*="weight" i], input[id*="weight" i]').first
                await weight_field.wait_for(state="visible", timeout=10_000)
                await weight_field.fill(str(int(request.weight_per_container_kg)))
                await weight_field.press("Enter")
            except Exception as e:
                print(f"[ONE] Cargo weight field failed: {e}")
                return CarrierResultStatus.INVALID_SEARCH_INPUT

            # Wait for any loading dialogs/spinners to disappear before proceeding to commodity selection (excl. persistent widgets like toast/sonner/heap/productfruits)
            try:
                loader_sel = (
                    '[class*="loading" i]:not([class*="sonner"]):not([class*="toast"]):not([class*="productfruits"]):not([class*="heap"]), '
                    '[class*="spinner" i]:not([class*="sonner"]):not([class*="toast"]):not([class*="productfruits"]):not([class*="heap"]), '
                    '[class*="loader" i]:not([class*="sonner"]):not([class*="toast"]):not([class*="productfruits"]):not([class*="heap"]), '
                    '[class*="backdrop" i]:not([class*="sonner"]):not([class*="toast"]):not([class*="productfruits"]):not([class*="heap"]):not([class*="modal"])'
                )
                for _ in range(150):
                    loaders = self.page.locator(loader_sel)
                    visible_loaders = 0
                    for i in range(await loaders.count()):
                        if await loaders.nth(i).is_visible():
                            visible_loaders += 1
                    if visible_loaders == 0:
                        break
                    await self.page.wait_for_timeout(100)
            except Exception:
                pass

            # --- COMMODITY ---
            # Use the commodity exactly as typed by the user on the frontend (e.g. "Furniture").
            # ONE has a searchable commodity field — type the name and pick the first matching suggestion.
            print(f"[ONE] Setting Commodity: '{request.commodity}' (user-provided)")
            try:
                commodity_field = self.page.get_by_role("combobox", name="Please input Commodity Name or HS code").first
                await commodity_field.wait_for(state="attached", timeout=15000)

                # Wait for the commodity field to become enabled before clicking
                for _ in range(100):
                    is_disabled = await commodity_field.get_attribute("disabled")
                    cls = await commodity_field.get_attribute("class") or ""
                    if is_disabled is None and "disabled" not in cls.lower():
                        break
                    await self.page.wait_for_timeout(100)

                await commodity_field.click(timeout=5000)
                await self.page.wait_for_timeout(200)
                await self.page.keyboard.type(request.commodity, delay=25)

                # Wait for dropdown suggestions to appear
                try:
                    # Scope to active listbox container to avoid stale options from previous fields
                    first_option = self.page.locator('[role="listbox"] [role="option"]:visible, [role="listbox"] li:visible, [role="option"]:visible').first
                    await first_option.wait_for(state="visible", timeout=2000)

                    # Try to find a case-insensitive match first, else pick the first option
                    commodity_upper = request.commodity.strip().upper()
                    all_options = self.page.locator('[role="listbox"] [role="option"]:visible, [role="listbox"] li:visible, [role="option"]:visible')
                    opted = False
                    for i in range(await all_options.count()):
                        try:
                            # Use small timeout to prevent waiting for detached placeholder elements (e.g. Loading...)
                            opt_text = (await all_options.nth(i).inner_text(timeout=1000)).strip().upper()
                            if "LOADING" in opt_text:
                                continue
                            if commodity_upper in opt_text or opt_text.startswith(commodity_upper[:6]):
                                await all_options.nth(i).click(timeout=1500)
                                print(f"[ONE] Commodity matched: '{opt_text}'")
                                opted = True
                                break
                        except Exception:
                            pass
                    if not opted:
                        await first_option.click(timeout=1500)
                        print("[ONE] Commodity: no exact match, selected first available option")
                except Exception as e:
                    # No dropdown appeared or click timed out — press Enter and continue
                    print(f"[ONE] Commodity: no dropdown appeared or click timed out ({e}), pressing Enter")
                    await self.page.keyboard.press("Enter")

                await self.page.wait_for_timeout(200)
            except Exception as e:
                print(f"[ONE] Commodity selection failed: {e}")
                return CarrierResultStatus.INVALID_SEARCH_INPUT

            # Wait for any loading dialogs/spinners to disappear before proceeding to date picker (excl. persistent widgets like toast/sonner/heap/productfruits)
            try:
                loader_sel = (
                    '[class*="loading" i]:not([class*="sonner"]):not([class*="toast"]):not([class*="productfruits"]):not([class*="heap"]), '
                    '[class*="spinner" i]:not([class*="sonner"]):not([class*="toast"]):not([class*="productfruits"]):not([class*="heap"]), '
                    '[class*="loader" i]:not([class*="sonner"]):not([class*="toast"]):not([class*="productfruits"]):not([class*="heap"]), '
                    '[class*="backdrop" i]:not([class*="sonner"]):not([class*="toast"]):not([class*="productfruits"]):not([class*="heap"]):not([class*="modal"])'
                )
                for _ in range(150):
                    loaders = self.page.locator(loader_sel)
                    visible_loaders = 0
                    for i in range(await loaders.count()):
                        if await loaders.nth(i).is_visible():
                            visible_loaders += 1
                    if visible_loaders == 0:
                        break
                    await self.page.wait_for_timeout(100)
            except Exception:
                pass

            print("[ONE] Opening date picker and accepting available sailing date...")
            try:
                # Combined selector to avoid sequential timeouts
                date_field = self.page.locator(
                    'input[placeholder*="date" i], '
                    'input[placeholder*="departure" i], '
                    'input[aria-label*="date" i], '
                    'input[name*="date" i], '
                    'input[id*="date" i], '
                    'input[placeholder*="YYYY-MM-DD" i]'
                ).first
                await date_field.wait_for(state="visible", timeout=5000)
                
                # Ensure we scroll the date field into view and wait a bit for any dynamic overlays to settle
                await date_field.scroll_into_view_if_needed()
                await self.page.wait_for_timeout(300) # Reduced from 1000

                # Wait for the date field to be enabled before clicking
                for _ in range(50):
                    is_disabled = await date_field.get_attribute("disabled")
                    cls = await date_field.get_attribute("class") or ""
                    if is_disabled is None and "disabled" not in cls.lower():
                        break
                    await self.page.wait_for_timeout(100)

                # Try standard click first to trigger Playwright's actionability checks, fallback to force click
                try:
                    await date_field.click(timeout=5000)
                except Exception:
                    print("[ONE] Normal date field click blocked/failed, trying force click...")
                    await date_field.click(force=True)
                
                # Wait for the calendar container to be visible
                print("[ONE] Waiting for calendar to appear...")
                calendar_sel = 'div[class*="Calendar"], .react-calendar, [class*="calendar-picker"], .MuiCalendarPicker-root, .react-datepicker, .react-datepicker-popper, .react-datepicker__calendar-container'
                calendar_loc = self.page.locator(calendar_sel).first
                try:
                    await calendar_loc.wait_for(state="visible", timeout=8000)
                    print("[ONE] Calendar visible")
                except Exception:
                    # Retry click if calendar did not appear (helps if page focus swallowed first click)
                    print("[ONE] Calendar did not appear, retrying click on date field...")
                    await date_field.click(force=True)
                    await calendar_loc.wait_for(state="visible", timeout=5000)
                    print("[ONE] Calendar visible (retry)")

                # Wait up to 6 seconds for prices to load (e.g. highlighted day or cell containing 'USD'), but proceed immediately as soon as they appear!
                print("[ONE] Waiting for prices to load in calendar...")
                try:
                    price_locator = self.page.locator('[class*="date-picker-date-highlight"], .react-datepicker__day--highlighted, .react-datepicker__day:has-text("USD")').first
                    await price_locator.wait_for(state="visible", timeout=6000)
                    print("[ONE] Prices loaded successfully.")
                except Exception:
                    print("[ONE] Prices did not load or highlighted days not found within timeout. Proceeding with available dates.")
                
                date_selected = False
                
                # We wrap the main hunting strategies in a loop to handle "Next Month" if current month is empty
                for month_attempt in range(2): # Current month + Next month
                    if date_selected: break
                    
                    # Self-healing: if the calendar closed prematurely (due to background AJAX completions or focus loss), click again to reopen it!
                    if not await calendar_loc.is_visible():
                        print(f"[ONE] Calendar closed prematurely before month attempt {month_attempt}, reopening...")
                        await date_field.click(force=True)
                        await calendar_loc.wait_for(state="visible", timeout=5000)

                    if month_attempt > 0:
                        print(f"[ONE] No sailings in current view, trying Next Month (attempt {month_attempt})...")
                        try:
                            # Try to find the "Next Month" arrow button
                            next_month_btn = self.page.locator('button[aria-label*="Next Month" i], button[class*="next"], .react-calendar__navigation__next-button').first
                            if await next_month_btn.is_visible():
                                await next_month_btn.click(force=True)
                                await self.page.wait_for_timeout(3000) # Wait for new dates to render
                            else:
                                print("[ONE] Next Month button not found, skipping month jump")
                                break
                        except Exception as e:
                            print(f"[ONE] Failed to click Next Month: {e}")
                            break

                    # Strategy 2: Click first calendar date that has ANY price (using highlight class)
                    if not date_selected:
                        try:
                            # Reopen calendar if closed
                            if not await calendar_loc.is_visible():
                                print("[ONE] Calendar closed, reopening for Strategy 2...")
                                await date_field.click(force=True)
                                await calendar_loc.wait_for(state="visible", timeout=3000)

                            # The debug screenshot showed prices in elements with "date-picker-date-highlight"
                            price_locator = self.page.locator('[class*="date-picker-date-highlight"], .react-datepicker__day--highlighted').filter(has_text="USD").first
                            await price_locator.wait_for(state="visible", timeout=5000)

                            # Get price text BEFORE click to prevent detaching issue
                            price_text = ""
                            try:
                                price_text = await price_locator.inner_text()
                            except Exception:
                                pass

                            await price_locator.click(force=True)
                            date_selected = True
                            print(f"[ONE] Clicked highlighted date cell with price: {price_text}")
                        except Exception:
                            pass

                    # Strategy 3: Search for ANY numeric price label (anchored regex) inside calendar tiles
                    if not date_selected:
                        try:
                            # Reopen calendar if closed
                            if not await calendar_loc.is_visible():
                                print("[ONE] Calendar closed, reopening for Strategy 3...")
                                await date_field.click(force=True)
                                await calendar_loc.wait_for(state="visible", timeout=3000)

                            # Broad search for 3-4 digit numbers or K-values inside anything that looks like a day tile
                            price_tile = self.page.locator('.react-datepicker__day, [class*="day"], [class*="tile"]').get_by_text(
                                re.compile(r"\d{3,4}|[\d.]+[kK]"), exact=False
                            ).first
                            await price_tile.wait_for(state="visible", timeout=3000)

                            # Get tile text BEFORE click to prevent detaching issue
                            tile_text = ""
                            try:
                                tile_text = await price_tile.inner_text()
                            except Exception:
                                pass

                            await price_tile.click(force=True)
                            date_selected = True
                            print(f"[ONE] Safety-net: clicked tile with numeric content: {tile_text}")
                        except Exception:
                            pass

                # Strategy 4: Click any non-disabled calendar cell with content
                if not date_selected:
                    try:
                        # Reopen calendar if closed
                        if not await calendar_loc.is_visible():
                            print("[ONE] Calendar closed, reopening for Strategy 4...")
                            await date_field.click(force=True)
                            await calendar_loc.wait_for(state="visible", timeout=3000)

                        # Target anything that looks like a date cell and is not disabled
                        any_cell = self.page.locator(
                            '[class*="Calendar"] button:not([disabled]), '
                            '.react-calendar__tile:not([disabled]), '
                            '[class*="Calendar"] [class*="available"], '
                            '.react-datepicker__day:not([class*="disabled"]):not([class*="outside"]), '
                            '[role="gridcell"]:not([aria-disabled="true"]):not([class*="disabled"])'
                        ).first
                        await any_cell.wait_for(state="visible", timeout=3000)
                        await any_cell.click(force=True)
                        date_selected = True
                        print("[ONE] Clicked an available calendar cell (tile search)")
                    except Exception:
                        pass

                # Strategy 5: Check if no sailing date could be selected (No Coverage)
                if not date_selected:
                    print("[ONE] No available sailing dates found in calendar (all dates are disabled). Route lacks spot coverage.")
                    # Take debug screenshot to brain directory
                    try:
                        artifact_dir = r"C:\Users\Brian\.gemini\antigravity\brain\2febadc4-254a-470f-9d04-a43202bfc8dc"
                        import os
                        await self.page.screenshot(path=os.path.join(artifact_dir, "one_no_coverage.png"))
                    except Exception:
                        pass
                    return CarrierResultStatus.NO_QUOTES_AVAILABLE

                # Verify calendar closure or wait for state change
                await self.page.wait_for_timeout(2000)
                
                # If calendar is still visible, try to click the body to close it
                if await self.page.locator('div[class*="Calendar"], div[class*="calendar"], .react-calendar').is_visible():
                    print("[ONE] Calendar still visible, attempting to close by clicking body")
                    await self.page.mouse.click(10, 10)
                    await self.page.wait_for_timeout(1000)

                print(f"[ONE] Date picker step completed (selected: {date_selected})")
            except Exception as e:
                print(f"[ONE] Date picker interaction failed (non-fatal): {e}")

            # Submit the search — wait for button to be truly enabled
            try:
                submit_btn = self.page.locator('button:has-text("GetQuote"), button:has-text("Get Quote"), button:has-text("Search Rates"), button:has-text("View Quote"), button:has-text("view Quote"), button[type="submit"]').first
                await submit_btn.wait_for(state="visible", timeout=5000)
                
                # Poll for enabled state (some buttons use 'disabled' attribute, others use classes)
                for _ in range(50):
                    is_disabled = await submit_btn.get_attribute("disabled")
                    if is_disabled is None:
                        # Also check common "disabled" classes
                        btn_class = await submit_btn.get_attribute("class") or ""
                        if "disabled" not in btn_class.lower():
                            break
                    await self.page.wait_for_timeout(100)
                
                await submit_btn.click(force=True, timeout=5000)
                print("[ONE] Search submitted (force click)")
            except Exception as e:
                print(f"[ONE] Submit click failed: {e}")

            print("[ONE] Waiting for search results or no results message...")
            try:
                cards = self.page.locator('div[class*="NewQuoteSummary_body-card"]').first
                await cards.wait_for(state="visible", timeout=25000)
                print("[ONE] Quote cards detected on search results page.")
            except Exception as e:
                print(f"[ONE] Quote cards did not appear within timeout: {e}")

            await self.page.wait_for_timeout(3000)
            print(f"[ONE] Search page ready: {self.page.url}")

            cards_count = await self.page.locator('div[class*="NewQuoteSummary_body-card"]').count()
            if cards_count > 0:
                return CarrierResultStatus.AVAILABLE_QUOTES_FOUND
            else:
                body_text = (await self.page.locator("body").inner_text()).lower()
                if "no quote" in body_text or "no rate" in body_text or "not found" in body_text or "no routing" in body_text:
                    print("[ONE] No coverage / no quotes found text detected in page body.")
                return CarrierResultStatus.NO_QUOTES_AVAILABLE
        except Exception as e:
            print(f"[ONE] Search failed: {e}")
            return CarrierResultStatus.TIMEOUT if "timeout" in str(e).lower() else CarrierResultStatus.UNKNOWN_ERROR

    async def extract_quote_list(self) -> list[dict]:
        try:
            quote_cards = self.page.locator('div[class*="NewQuoteSummary_body-card"]')
            count = await quote_cards.count()
            print(f"[ONE] Found {count} quote(s)")
            quotes = []
            for index in range(count):
                card_text = (await quote_cards.nth(index).inner_text()).strip()
                normalized_text = re.sub(r"\s+", " ", card_text)

                summary_match = re.search(
                    r"Origin\s+(\d{4}-\d{2}-\d{2})\s+(\d+)\s+day\(s\)\s+(?:.*?)\s*Destination\s+(\d{4}-\d{2}-\d{2})\s+Service Lane/\s*Vessel Voyage\s+([A-Z0-9]+)\s*/\s*([A-Z0-9 ().-]+?)\s+Status\s+([A-Za-z]+)\s+POL\s+(.+?)\s+POD\s+(.+?)\s+USD\s*([\d,]+\.\d{2})",
                    normalized_text,
                )

                etd = None
                eta = None
                transit_time_days = None
                service_name = None
                vessel = None
                status = None
                pol = None
                pod = None
                total_price = 0.0

                if summary_match:
                    etd = summary_match.group(1)
                    transit_time_days = int(summary_match.group(2))
                    eta = summary_match.group(3)
                    service_lane = summary_match.group(4).strip()
                    vessel = summary_match.group(5).strip()
                    status = summary_match.group(6).strip()
                    pol = summary_match.group(7).strip()
                    pod = summary_match.group(8).strip()
                    total_price = float(summary_match.group(9).replace(",", ""))
                    service_name = f"{service_lane} / {vessel}"
                else:
                    print(f"[ONE] Could not parse full quote summary for card {index + 1}. Fallback extraction...")
                    price_match = re.search(r"USD\s*([\d,]+\.\d{2})", normalized_text)
                    if price_match:
                        total_price = float(price_match.group(1).replace(",", ""))
                    
                    etd_match = re.search(r"Origin\s+(\d{4}-\d{2}-\d{2})", normalized_text)
                    if etd_match: etd = etd_match.group(1)
                    
                    eta_match = re.search(r"Destination\s+(\d{4}-\d{2}-\d{2})", normalized_text)
                    if eta_match: eta = eta_match.group(1)
                    
                    tt_match = re.search(r"(\d+)\s+day\(s\)", normalized_text)
                    if tt_match:
                        transit_time_days = int(tt_match.group(1))

                    sv_match = re.search(r"Service Lane/\s*Vessel Voyage\s+(\S+)\s*/\s*([A-Za-z0-9 ().-]+?)(?:\s+POL|\s+Status|\s+POD)", normalized_text)
                    if sv_match:
                        service_lane = sv_match.group(1).strip()
                        vessel = sv_match.group(2).strip()
                        service_name = f"{service_lane} / {vessel}"
                    
                    pol_match = re.search(r"POL\s+(.+?)(?:\s+POD|\s+Status|\s+USD)", normalized_text)
                    if pol_match:
                        pol = pol_match.group(1).strip()
                        
                    pod_match = re.search(r"POD\s+(.+?)(?:\s+USD|\s+Status)", normalized_text)
                    if pod_match:
                        pod = pod_match.group(1).strip()

                    status_match = re.search(r"Status\s+([A-Za-z ]+?)(?:\s+POL|\s+POD|\s+USD)", normalized_text)
                    if status_match:
                        status = status_match.group(1).strip()

                # Robust check for Sold Out status
                is_sold_out = False
                if status and "sold" in status.lower():
                    is_sold_out = True
                if "sold out" in normalized_text.lower() or "soldout" in normalized_text.lower() or "notify me" in normalized_text.lower():
                    is_sold_out = True
                if vessel == "---" or not vessel or vessel == "Sold out":
                    is_sold_out = True

                if is_sold_out:
                    vessel = "Sold out"
                    service_name = "Sold out"
                    status = "Sold Out"
                    total_price = 0.0

                quotes.append({
                    "index": index,
                    "card_text": card_text,
                    "etd": etd,
                    "eta": eta,
                    "transit_time_days": transit_time_days,
                    "service_name": service_name,
                    "vessel": vessel,
                    "container_type": None,
                    "container_quantity": None,
                    "currency": "USD",
                    "source": "carrier_portal",
                    "raw_reference": f"ONE-LIVE-{index + 1}",
                    "status": status,
                    "pol": pol,
                    "pod": pod,
                    "total_price": total_price,
                })
            return quotes
        except Exception as e:
            print(f"[ONE] Error extracting quotes: {e}")
            return []

    async def open_price_breakdown(self, quote_ref: dict) -> bool:
        try:
            idx = quote_ref.get("index", 0)
            quote_cards = self.page.locator('div[class*="NewQuoteSummary_body-card"]')
            if await quote_cards.count() <= idx:
                return False

            card = quote_cards.nth(idx)
            self.current_card = quote_cards.nth(idx)
            self.current_pol = (quote_ref.get("pol") or "").strip().upper()
            self.current_pod = (quote_ref.get("pod") or "").strip().upper()
            self.current_routing = "Direct"
            
            all_details_buttons = self.page.locator('button.NewQuoteSummary_breakdown-button__oIAYJ')
            
            # Close the previous accordion to prevent text stacking
            if idx > 0:
                try:
                    prev_btn = None
                    if await all_details_buttons.count() > (idx - 1):
                        prev_btn = all_details_buttons.nth(idx - 1)
                    else:
                        prev_btn = self.page.locator('button:has-text("Details")').nth(idx - 1)
                    
                    if await prev_btn.is_visible():
                        await prev_btn.scroll_into_view_if_needed()
                        await prev_btn.click(timeout=3000)
                    await self.page.wait_for_timeout(1000) # Wait for close animation
                except Exception:
                    pass
            
            details_count = await all_details_buttons.count()
            print(f"[ONE] Found {details_count} Details button(s) on page for quote {idx}")
            
            if details_count > idx:
                btn = all_details_buttons.nth(idx)
                await btn.scroll_into_view_if_needed()
                await self.page.wait_for_timeout(500)
                await btn.click(timeout=5000)
                print(f"[ONE] Clicked Details button for quote {idx}")
            else:
                # Fallback: try any button containing "Details" text on the page
                btn = self.page.locator('button:has-text("Details")').nth(idx)
                await btn.scroll_into_view_if_needed()
                await self.page.wait_for_timeout(500)
                await btn.click(timeout=5000)
                print(f"[ONE] Clicked Details via fallback for quote {idx}")

            # Wait for the breakdown to render (look for Basic Ocean Freight text)
            try:
                bof_text = self.page.locator('text=/basic ocean freight/i').first
                await bof_text.wait_for(state="visible", timeout=10000)
            except Exception:
                print(f"[ONE] Warning: 'Basic Ocean Freight' text did not appear within 10s for quote {idx}")
            
            # Short fallback wait just in case
            await self.page.wait_for_timeout(1000)
            return True
        except Exception as e:
            print(f"[ONE] Error opening breakdown for quote {idx}: {e}")
            return False

    async def extract_charge_breakdown(self) -> list[dict]:
        try:
            text = ""
            if hasattr(self, 'current_card') and self.current_card:
                text = await self.current_card.inner_text()
            
            # If the charges aren't inside the card (e.g. rendered in a portal), fallback to body
            if "BASIC OCEAN FREIGHT" not in text.upper() and "OCEAN FREIGHT" not in text.upper():
                text = await self.page.locator("body").inner_text()

            # Parse routing from the timeline text
            try:
                pol_code = self._extract_port_code(self.current_pol).strip().upper()
                pod_code = self._extract_port_code(self.current_pod).strip().upper()
                
                # Find all "PORT NAME (LOCODE)" matches in the expanded card text
                import re
                locode_matches = re.findall(r"([A-Za-z0-9\t ,.-]+?)\s*\(([A-Z]{5})\)", text)
                transit_ports = []
                seen_locodes = set()
                for port_name, locode in locode_matches:
                    locode_upper = locode.strip().upper()
                    port_name_clean = port_name.strip()
                    # Skip empty labels, POL, POD, and duplicates
                    if locode_upper == pol_code or locode_upper == pod_code:
                        continue
                    if locode_upper in seen_locodes:
                        continue
                    seen_locodes.add(locode_upper)
                    if port_name_clean:
                        transit_ports.append(f"{port_name_clean} ({locode_upper})")
                
                if transit_ports:
                    self.current_routing = "Transit via " + ", ".join(transit_ports)
                    print(f"[ONE] Extracted routing: {self.current_routing}")
                else:
                    self.current_routing = "Direct"
                    print("[ONE] Extracted routing: Direct")
            except Exception as re_err:
                print(f"[ONE] Warning: failed to parse timeline routing: {re_err}")

            # Isolate the breakdown section to avoid parsing the card summary
            if "BASIC OCEAN FREIGHT" in text.upper():
                idx_bof = text.upper().find("BASIC OCEAN FREIGHT")
                text = text[idx_bof:]
            else:
                # For debugging why the accordion didn't open or isn't extracted
                print(f"[ONE] BASIC OCEAN FREIGHT not found! Attempted click failed to render charges.")
                if hasattr(self, 'current_card') and self.current_card:
                    html = await self.current_card.inner_html()
                    print(f"[ONE] Card HTML snippet: {html[:5000]}")

            lines = [line.strip() for line in text.splitlines() if line.strip()]
            amount_pattern = re.compile(r"(?:^|\s)([A-Z]{3})\s*([\d,]+\.\d{2})$")

            def is_section_heading(line: str) -> bool:
                normalized = line.strip().lower()
                return normalized in {
                    "freight charge",
                    "origin charge",
                    "destination charge",
                    "special promotion service",
                    "promotion",
                } or normalized.startswith("what is special promotion service")

            def is_container_line(line: str) -> bool:
                return "x" in line and "(" in line and ")" in line

            def is_stop_line(line: str) -> bool:
                normalized = line.strip().lower()
                if normalized in {"pol", "pod", "accept", "details", "origin", "destination"}:
                    return True
                if "service lane" in normalized or "vessel voyage" in normalized:
                    return True
                if re.match(r"^\d{4}-\d{2}-\d{2}$", normalized):
                    return True
                return False

            charges = []
            for index, line in enumerate(lines):
                if is_stop_line(line):
                    print(f"[ONE] Stopping breakdown parsing at line: '{line}'")
                    break
                amount_match = amount_pattern.search(line)
                if not amount_match:
                    continue

                currency = amount_match.group(1)
                amount = float(amount_match.group(2).replace(",", ""))

                remaining_line = line[:amount_match.start()].strip()
                name = ""

                if remaining_line and not is_container_line(remaining_line) and not is_section_heading(remaining_line):
                    name = remaining_line
                else:
                    # Try to find the charge name by walking backwards
                    name_index = index - 1
                    while name_index >= 0:
                        candidate = lines[name_index]
                        if not candidate or is_section_heading(candidate) or is_container_line(candidate):
                            name_index -= 1
                            continue
                        if amount_pattern.search(candidate):
                            name_index -= 1
                            continue
                        break

                    name = lines[name_index] if name_index >= 0 else f"Charge {len(charges) + 1}"

                # Find the section heading for this charge
                section_heading = "unknown"
                sec_index = index - 1
                while sec_index >= 0:
                    candidate = lines[sec_index]
                    if is_section_heading(candidate):
                        section_heading = candidate.strip().lower()
                        break
                    sec_index -= 1

                # Classify the charge
                category, reason = classify_charge(name, amount, section_heading)
                charges.append({
                    "name": name,
                    "amount": amount,
                    "currency": currency,
                    "category": category.value,
                    "reason": reason,
                })

            print(f"[ONE] Parsed {len(charges)} charge line(s)")
            return charges
        except Exception as e:
            print(f"[ONE] Error extracting charges: {e}")
            return []

    async def normalize_result(self, raw_quote, raw_charges):
        quote_schema = normalize_quote(self.carrier_code, raw_quote, raw_charges)
        if hasattr(self, "current_routing") and self.current_routing:
            quote_schema.routing = self.current_routing
        if hasattr(self, 'port_fallback_notice') and self.port_fallback_notice:
            if quote_schema.vessel:
                quote_schema.vessel = f"{quote_schema.vessel} ({self.port_fallback_notice})"
            else:
                quote_schema.vessel = f"({self.port_fallback_notice})"
                
        # Resolve Freetime from offline cache
        cache_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "one_freetime.json")
        if os.path.exists(cache_path):
            try:
                import json
                with open(cache_path, "r") as f:
                    freetime_cache = json.load(f)
                    
                origin_country = None
                dest_continent = None
                
                if hasattr(self, 'origin_locode') and self.origin_locode:
                    origin_country = self.origin_locode[:2].upper()
                    
                if hasattr(self, 'destination_locode') and self.destination_locode:
                    dest_country = self.destination_locode[:2].upper()
                    
                    # Comprehensive country→region maps.
                    # City names (e.g. Hai Phong, Lagos) are first resolved to LOCODEs
                    # by port_manager (e.g. VNHPH, NGLOS), then the 2-letter country
                    # prefix (VN, NG) is used to classify the destination region.
                    EUROPE = [
                        "AL", "AD", "AT", "BY", "BE", "BA", "BG", "HR", "CY", "CZ",
                        "DK", "EE", "FI", "FR", "DE", "GR", "HU", "IS", "IE", "IT",
                        "XK", "LV", "LI", "LT", "LU", "MT", "MD", "MC", "ME", "NL",
                        "MK", "NO", "PL", "PT", "RO", "RU", "SM", "RS", "SK", "SI",
                        "ES", "SE", "CH", "TR", "UA", "GB", "VA",
                        # Baltic/Scandinavian extras
                        "AX", "FO", "GI", "GG", "IM", "JE",
                    ]
                    ASIA = [
                        # Southeast Asia
                        "BN", "KH", "ID", "LA", "MY", "MM", "PH", "SG", "TH", "TL", "TP", "VN",
                        # East Asia
                        "CN", "HK", "JP", "KR", "KP", "MO", "MN", "TW",
                        # South Asia
                        "AF", "BD", "BT", "IN", "MV", "NP", "PK", "LK",
                        # Middle East / West Asia
                        "AE", "BH", "CY", "GE", "IQ", "IR", "IL", "JO", "KW",
                        "LB", "OM", "PS", "QA", "SA", "SY", "YE",
                        # Central Asia
                        "AM", "AZ", "KZ", "KG", "TJ", "TM", "UZ",
                        # Oceania — ONE maps Australia/NZ under Asia region
                        "AU", "NZ", "FJ", "PG", "WS",
                    ]
                    AFRICA = [
                        # North Africa
                        "DZ", "EG", "LY", "MA", "SD", "SS", "TN", "EH",
                        # West Africa
                        "BJ", "BF", "CV", "CI", "GM", "GH", "GN", "GW",
                        "LR", "ML", "MR", "NE", "NG", "SN", "SL", "TG",
                        # East Africa
                        "BI", "KM", "DJ", "ER", "ET", "KE", "MG", "MW",
                        "MU", "MZ", "RE", "RW", "SC", "SO", "TZ", "UG",
                        "YT", "ZM", "ZW",
                        # Central Africa
                        "AO", "CM", "CF", "TD", "CG", "CD", "GQ", "GA", "ST",
                        # Southern Africa
                        "BW", "LS", "NA", "ZA", "SZ",
                    ]
                    NORTH_AMERICA = [
                        "US", "CA", "MX",
                        # Central America & Caribbean
                        "AG", "BS", "BB", "BZ", "CU", "DM", "DO", "SV", "GD",
                        "GT", "HT", "HN", "JM", "KN", "LC", "VC", "TT",
                        "NI", "CR", "PA", "PR", "VI",
                    ]
                    LATIN_AMERICA = [
                        "AR", "BO", "BR", "CL", "CO", "EC", "GF", "GY",
                        "PY", "PE", "SR", "UY", "VE",
                    ]

                    if dest_country in EUROPE: dest_continent = "EUROPE"
                    elif dest_country in AFRICA: dest_continent = "AFRICA"
                    elif dest_country in LATIN_AMERICA: dest_continent = "LATIN AMERICA"
                    elif dest_country in NORTH_AMERICA: dest_continent = "NORTH AMERICA"
                    elif dest_country in ASIA: dest_continent = "ASIA"

                if origin_country and dest_continent and origin_country in freetime_cache:
                    fd = freetime_cache[origin_country].get(dest_continent)
                    if fd is not None:
                        quote_schema.free_time = fd
                        print(f"[ONE] Successfully mapped offline Freetime: {origin_country} -> {dest_continent} = {fd} days")
            except Exception as e:
                print(f"[ONE] Warning: Failed to apply freetime from cache: {e}")
                
        return quote_schema

    async def close(self):
        try:
            if self.page: await self.page.close()
            if self.context: await self.context.close()
            if self.browser: await self.browser.close()
            if self.playwright: await self.playwright.stop()
        except Exception:
            pass
