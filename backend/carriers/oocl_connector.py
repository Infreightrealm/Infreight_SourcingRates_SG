"""
OOCL Live Connector — Playwright automation for Sailing Schedules.
"""
import os
import re
import asyncio
from datetime import datetime, date, timedelta
from typing import Optional, List
from playwright.async_api import async_playwright
from models.schemas import RateSearchRequest, QuoteSchema, CarrierResultStatus, ChargeSchema
from carriers.base_connector import BaseCarrierConnector
from services.normalizer import standardize_date_string
from services.port_manager import resolve_port_for_carrier

MONTH_MAP = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12
}

def parse_oocl_date(date_str: str, year: int) -> Optional[str]:
    if not date_str:
        return None
    try:
        parts = date_str.strip().split()
        if len(parts) >= 2:
            day = int(parts[0])
            month_str = parts[1].lower()[:3]
            month = MONTH_MAP.get(month_str)
            if month:
                dt = date(year, month, day)
                return dt.strftime("%Y-%m-%d")
    except Exception as e:
        print(f"[OOCL] Error parsing date {date_str}: {e}")
    return None

def resolve_oocl_port_info(text: str) -> tuple[str, str, str, str]:
    """
    Resolves input text to (location_name, locode, country_code, country_name).
    """
    if not text:
        return "", "", "", ""
        
    text_lower = text.lower().strip()
    
    # Rotterdam override
    if "rotterdam" in text_lower or text_lower == "nlrtm":
        return "Rotterdam", "NLRTM", "NL", "Netherlands"
        
    # Extract LOCODE
    locode = None
    paren_match = re.search(r'\(\s*([A-Za-z]{2})\s*([A-Za-z]{3})\s*\)', text)
    if paren_match:
        locode = (paren_match.group(1) + paren_match.group(2)).upper()
    else:
        word_match = re.search(r'\b([A-Za-z]{2})\s*([A-Za-z]{3})\b', text)
        if word_match:
            candidate = (word_match.group(1) + word_match.group(2)).upper()
            from services.port_manager import PortManager
            if candidate in PortManager()._ports:
                locode = candidate
    if not locode:
        clean_word = text.strip()
        if len(clean_word) == 5 and clean_word.isalpha():
            candidate = clean_word.upper()
            from services.port_manager import PortManager
            if candidate in PortManager()._ports:
                locode = candidate
                
    # If still not found, search in port manager database
    if not locode:
        from services.port_manager import search_port
        results = search_port(text)
        if results:
            locode = results[0]['code'].upper()
            
    location_name = ""
    country_code = ""
    country_name = ""
    
    if locode:
        from services.port_manager import PortManager, COUNTRY_CODE_TO_NAME
        port_data = PortManager().get_port_by_code(locode)
        if port_data:
            name = port_data.get("name", "")
            location_name = re.sub(r'\s*\([^)]*\)', '', name).strip()
            country_code = port_data.get("country", "").upper()
            country_name = COUNTRY_CODE_TO_NAME.get(country_code, "")
            
    if not location_name:
        location_name = re.sub(r'\s*\([^)]*\)', '', text).strip()
        
    if not locode:
        locode = ""
        
    return location_name, locode, country_code, country_name

class OOCLConnector(BaseCarrierConnector):
    carrier_code = "OOCL"
    carrier_name = "OOCL"
    SEARCH_URL = "https://moc.oocl.com/nj_prs_wss/#/sailing_schedules/search?PREFER_LANGUAGE=en-US"

    def __init__(self):
        super().__init__()
        self.playwright = None
        self.browser = None
        self.context = None

    async def _init_browser(self):
        is_prod = os.name != "nt"
        self.playwright = await async_playwright().start()
        
        browser_env = os.environ.copy()
        if is_prod:
            browser_env["DISPLAY"] = ":105"

        self.browser = await self.playwright.chromium.launch(
            headless=False,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled",
            ],
            env=browser_env,
        )
        self.context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            ignore_https_errors=True,
        )
        self.page = await self.context.new_page()
        self.page.set_default_timeout(30000)

    async def login(self) -> bool:
        return True

    async def _select_location(self, label: str, field_selector: str, location_name: str, locode: str = None, country_code: str = None, country_name: str = None) -> bool:
        try:
            print(f"[OOCL] Typing {label}: {location_name}")
            field = self.page.locator(field_selector).first
            await field.click()
            await self.page.keyboard.press("Control+A")
            await self.page.keyboard.press("Backspace")
            
            await field.type(location_name, delay=100)
            
            dropdown_sel = 'ul[role="listbox"] li, .ui-autocomplete-items li, .dropdown-menu li, .cdk-overlay-container [role="option"], [role="option"]'

            try:
                # Give the dropdown up to 15s to appear, as OOCL API can be slow
                await self.page.locator(dropdown_sel).first.wait_for(state="visible", timeout=15000)
            except Exception:
                print(f"[OOCL] No dropdown appeared for {label}")
                os.makedirs("scratch", exist_ok=True)
                await self.page.screenshot(path=f"scratch/oocl_dropdown_{label}_fail.png", full_page=True)
                html = await self.page.content()
                with open(f"scratch/oocl_dropdown_{label}_fail.html", "w", encoding="utf-8") as f:
                    f.write(html)
                return False
                
            options = self.page.locator(dropdown_sel)
            count = await options.count()
            if count == 0:
                print(f"[OOCL] Dropdown empty for {label}")
                return False
                
            # Try to match option using LOCODE / Country
            matching_option = None
            for i in range(count):
                opt = options.nth(i)
                text = await opt.inner_text()
                if text:
                    text_lower = text.lower()
                    if location_name.lower() in text_lower:
                        if locode or country_code or country_name:
                            matched = False
                            if locode and locode.lower() in text_lower:
                                matched = True
                            elif country_name and country_name.lower() in text_lower:
                                matched = True
                            elif country_code and (country_code.lower() in text_lower or re.search(rf'\b{re.escape(country_code.lower())}\b', text_lower)):
                                matched = True
                            if matched:
                                matching_option = opt
                                print(f"[OOCL] Matched option by LOCODE/Country for {label}: '{text.strip()}'")
                                break
            
            # Fallback if no specific locode/country matched
            if not matching_option:
                for i in range(count):
                    opt = options.nth(i)
                    text = await opt.inner_text()
                    if text and location_name.lower() in text.lower():
                        matching_option = opt
                        print(f"[OOCL] Fallback matched option by name for {label}: '{text.strip()}'")
                        break
            
            if matching_option:
                await matching_option.scroll_into_view_if_needed()
                await matching_option.click()
                await self.page.wait_for_timeout(1000) # Give Angular time to sync the ng-model
                return True
                    
            opt_text = await options.nth(0).inner_text()
            await options.nth(0).scroll_into_view_if_needed()
            await options.nth(0).click()
            print(f"[OOCL] Selected first {label} option: {opt_text.strip()}")
            await self.page.wait_for_timeout(1000) # Give Angular time to sync the ng-model
            return True
            
        except Exception as e:
            print(f"[OOCL] Failed to select {label}: {e}")
            return False

    async def search_quotes(self, request: RateSearchRequest) -> CarrierResultStatus:
        try:
            await self._init_browser()
            
            async def log_response(response):
                print(f"[OOCL] API Response: {response.url} - Status: {response.status}")
            
            self.page.on("response", log_response)
            
            self.page.on("console", lambda msg: print(f"[OOCL-Console] {msg.type}: {msg.text}"))
            
            print(f"[OOCL] Navigating to search URL: {self.SEARCH_URL}")
            await self.page.goto(self.SEARCH_URL, wait_until="networkidle")
            await self.page.wait_for_timeout(3000)
            
            # Find inputs. In OOCL there is an Origin input and a Destination input inside the form.
            # Usually they are inside app-autocomplete or similar.
            origin_field = 'input[placeholder="Origin"], oocl-autocomplete-input[formcontrolname="origin"] input'
            dest_field = 'input[placeholder="Destination"], oocl-autocomplete-input[formcontrolname="destination"] input'
            
            # If placeholders are different, let's use the nth input approach as a fallback
            try:
                await self.page.locator(origin_field).first.wait_for(state="attached", timeout=5000)
            except Exception:
                origin_field = 'input[type="text"] >> nth=0'
                dest_field = 'input[type="text"] >> nth=1'
            
            origin_name, origin_locode, origin_cc, origin_cn = resolve_oocl_port_info(request.origin)
            origin_success = await self._select_location("Origin", origin_field, origin_name, origin_locode, origin_cc, origin_cn)
            if not origin_success:
                return CarrierResultStatus.INVALID_SEARCH_INPUT
                
            dest_name, dest_locode, dest_cc, dest_cn = resolve_oocl_port_info(request.destination)
            dest_success = await self._select_location("Destination", dest_field, dest_name, dest_locode, dest_cc, dest_cn)
            if not dest_success:
                return CarrierResultStatus.INVALID_SEARCH_INPUT
                

            try:
                await self.page.keyboard.press("Tab")
                await self.page.wait_for_timeout(500)
                
                # Use Playwright's native click so it waits for actionability/overlays
                search_btn = self.page.locator('button[ng-click="displayResult()"], button[form="searchForm"]').first
                await search_btn.wait_for(state="visible", timeout=5000)
                await search_btn.click()
                print("[OOCL] Clicked Search button.")
            except Exception as e:
                print(f"[OOCL] Failed to click Search button: {e}")
                return CarrierResultStatus.INVALID_SEARCH_INPUT
            
            try:
                # OOCL can be slow, wait up to 90 seconds for results/captcha
                await self.page.locator('.ag-row, :text-matches("No schedule found", "i")').first.wait_for(state="attached", timeout=90000)
            except Exception as e:
                print(f"[OOCL] Timeout or error waiting for search results: {e}")
                os.makedirs("scratch", exist_ok=True)
                await self.page.screenshot(path="scratch/oocl_search_timeout.png", full_page=True)
                html = await self.page.content()
                with open("scratch/oocl_search_timeout.html", "w", encoding="utf-8") as f:
                    f.write(html)
                return CarrierResultStatus.TIMEOUT
                
            no_results = self.page.locator('text=/No schedule found/i, text=/no results/i').first
            if await no_results.is_visible(timeout=2000):
                print("[OOCL] No schedules found.")
                return CarrierResultStatus.NO_QUOTES_AVAILABLE
                
            print("[OOCL] Results loaded successfully.")
            return CarrierResultStatus.AVAILABLE_QUOTES_FOUND

        except Exception as e:
            print(f"[OOCL] Search failed: {e}")
            return CarrierResultStatus.UNKNOWN_ERROR

    async def extract_quote_list(self) -> List[dict]:
        quotes = []
        try:
            print("[OOCL] Extracting results...")
            
            # Wait for the Search Result count text to appear and be stable
            result_count_locator = self.page.locator('span:has-text("Search Result:")')
            expected_count = 0
            try:
                await result_count_locator.wait_for(state="visible", timeout=15000)
                await self.page.wait_for_timeout(1000) # Let it settle to ensure accurate number
                text = await result_count_locator.inner_text()
                match = re.search(r'Search Result:\s*(\d+)', text)
                if match:
                    expected_count = int(match.group(1))
                    print(f"[OOCL] Expected result count: {expected_count}")
            except Exception as e:
                print(f"[OOCL] Warning: could not parse expected result count: {e}")

            # Wait up to 15 seconds for the .ag-row count to match expected_count (or be stable and >0)
            for attempt in range(30):
                rows = self.page.locator('.ag-row')
                count = await rows.count()
                if expected_count > 0 and count >= expected_count:
                    print(f"[OOCL] All {count} rows loaded successfully matching expected count.")
                    break
                elif expected_count == 0 and count > 0:
                    await self.page.wait_for_timeout(500)
                    new_count = await rows.count()
                    if new_count == count:
                        print(f"[OOCL] Count settled at {count} rows.")
                        break
                await asyncio.sleep(0.5)

            os.makedirs("scratch", exist_ok=True)
            await self.page.screenshot(path="scratch/oocl_results.png", full_page=True)
            html = await self.page.content()
            with open("scratch/oocl_results.html", "w", encoding="utf-8") as f:
                f.write(html)
            
            rows = self.page.locator('.ag-row')
            count = await rows.count()
            if count == 0:
                print("[OOCL] Could not locate any result rows.")
                html = await self.page.content()
                os.makedirs("scratch", exist_ok=True)
                with open("scratch/oocl_debug.html", "w", encoding="utf-8") as f:
                    f.write(html)
                return []
                
            print(f"[OOCL] Found {count} result rows.")
            
            for i in range(count):
                row = rows.nth(i)
                try:
                    text = await row.inner_text()
                    
                    tt_match = re.search(r'(\d+)\s*day\(s\)', text, re.IGNORECASE)
                    tt_days = int(tt_match.group(1)) if tt_match else None
                    
                    ts_match = re.search(r'(\d+)\s*Transshipment', text, re.IGNORECASE)
                    is_transit = ts_match is not None
                    
                    # Extract ETD/ETA from the port-time divs
                    port_times = await row.locator('.port-time').all_inner_texts()
                    etd_str = None
                    eta_str = None
                    if len(port_times) >= 2:
                        etd_raw = port_times[0].strip() # e.g. "14 Jun (Sun)"
                        eta_raw = port_times[-1].strip()
                        etd_match = re.search(r'(\d{1,2}\s+[A-Za-z]{3})', etd_raw)
                        eta_match = re.search(r'(\d{1,2}\s+[A-Za-z]{3})', eta_raw)
                        etd_str = etd_match.group(1) if etd_match else None
                        eta_str = eta_match.group(1) if eta_match else None
                    
                    etd_iso = None
                    eta_iso = None
                    current_year = datetime.now().year
                    
                    if etd_str:
                        etd_iso = parse_oocl_date(etd_str, current_year)
                    if eta_str:
                        eta_iso = parse_oocl_date(eta_str, current_year)
                        
                    # Extract Service, Vessel, Voyage
                    service_info_links = await row.locator('a.service-info').all_inner_texts()
                    service_info_links = [l.strip() for l in service_info_links if l.strip()]
                    
                    service_name = None
                    vessel = "UNKNOWN"
                    voyage = None
                    
                    # Usually service is first, then vessel, then voyage
                    if len(service_info_links) >= 3:
                        service_name = service_info_links[0]
                        vessel = service_info_links[1]
                        voyage = service_info_links[2]
                        vessel = f"{vessel} {voyage}"
                    elif len(service_info_links) >= 2:
                        vessel = service_info_links[0]
                        voyage = service_info_links[1]
                        vessel = f"{vessel} {voyage}"
                        
                    routing_str = "Transit" if is_transit else "Direct"
                    
                    if is_transit:
                        ts_ports = []
                        # The button often has extra whitespace, use a looser selector
                        details_btn = row.locator('text=/Schedule Details/i').first
                        if await details_btn.is_visible():
                            await details_btn.click()
                            await self.page.wait_for_timeout(3000) # Wait for expansion
                            
                            try:
                                # The expanded detail might be inside the row or immediately following it
                                grid_html = await self.page.locator('.ag-body-viewport').inner_html()
                                ts_matches = re.finditer(r'<strong class="ng-binding">([^<]+)</strong>', grid_html)
                                ports_found = []
                                for m in ts_matches:
                                    val = m.group(1).strip()
                                    # Skip dates like "22 Jun (Mon) 20:00" and durations like "7 Days"
                                    if re.search(r'\d', val):
                                        continue
                                    if val and val not in ports_found:
                                        ports_found.append(val)
                                
                                # Origin is first, Destination is last. Anything in between is a transshipment port!
                                if len(ports_found) >= 3:
                                    ts_ports = ports_found[1:-1]
                                    
                                # Close it so it doesn't mess up the grid!
                                await details_btn.click()
                                await self.page.wait_for_timeout(500)
                            except Exception as e:
                                print(f"[OOCL] Error extracting T/S ports: {e}")
                                
                        if ts_ports:
                            routing_str = "via " + " - ".join(ts_ports)
                        else:
                            routing_str = "via 1 Transshipment Port"
                            
                    if not etd_iso and not eta_iso and vessel == "UNKNOWN":
                        continue
                        
                    quote = QuoteSchema(
                        source=self.carrier_name,
                        basic_ocean_freight=0,
                        discount=0,
                        included_freight_surcharges=[],
                        excluded_charges=[],
                        uncertain_charges=[],
                        final_freight_value=0,
                        currency="USD",
                        transit_time_days=tt_days,
                        etd=etd_iso,
                        eta=eta_iso,
                        routing=routing_str,
                        vessel=vessel,
                        service_name=service_name
                    )
                    quotes.append(quote.model_dump())
                    
                except Exception as e:
                    print(f"[OOCL] Error parsing row {i}: {e}")
                    
        except Exception as e:
            print(f"[OOCL] Error extracting quotes: {e}")
            
        return quotes

    # ────────────────────────────────────────
    # FREIGHTSMART (price quotes: E-Quote / E-Spot)
    # ────────────────────────────────────────

    FS_LOGIN_URL = "https://freightsmart.oocl.com/app/login?loginType=OOCL"
    FS_HOME_URL = "https://freightsmart.oocl.com/ui/"

    # FreightSmart container labels -> internal container type codes.
    # (NOR reefer variants price as their dry size.)
    FS_CONTAINER_MAP = {
        "20GP": "DRY 20", "20RF": "DRY 20",
        "40GP": "DRY 40",
        "40HQ": "DRY 40H", "40RQ": "DRY 40H",
    }

    async def _fs_dismiss_modals(self, page):
        """
        Closes FreightSmart popups. Order matters:
          1. Cookie Notice consent ("Accept All") — appears on the login page and
             intercepts the Next/Sign In clicks.
          2. The "Welcome to the new FreightSmart" onboarding tour carousel — closed
             via its X icon specifically. "Start Tour" is deliberately never matched
             here; clicking it would launch the tour instead of dismissing it.
          3. Generic dialog close buttons (e.g. the post-login "Important Update").
          4. Escape key as a last resort, for any of the above whose close control
             isn't a plain <button> our selectors can reach.
        """
        for _ in range(4):
            closed_any = False
            for sel in ['button:has-text("Accept All")', 'button:has-text("Accept all")',
                        '#onetrust-accept-btn-handler', 'button:has-text("Agree")',
                        'div:has-text("Welcome to the new FreightSmart") button[aria-label="Close" i]',
                        'div:has-text("Welcome to the new FreightSmart") [aria-label="close" i]',
                        'div:has-text("Welcome to the new FreightSmart") button:not(:has-text("Start Tour"))',
                        'div:has-text("Welcome to the new FreightSmart") [class*="close" i]',
                        'button:has-text("Close")', 'button:has-text("OK")',
                        '[class*="dialog" i] [class*="close" i]', '[aria-label="Close"]']:
                try:
                    btn = page.locator(sel).first
                    if await btn.is_visible(timeout=800):
                        await btn.click()
                        print(f"[OOCL] [FS] Dismissed popup via: {sel}")
                        await page.wait_for_timeout(600)
                        closed_any = True
                        break
                except Exception:
                    continue
            if closed_any:
                continue

            # Fallback: the onboarding tour's X may not be a plain <button> our
            # selectors can reach. If the tour text is still visible, try Escape
            # (never "Start Tour") before giving up on this pass.
            try:
                tour_visible = await page.locator(
                    'text="Welcome to the new FreightSmart"').first.is_visible(timeout=500)
            except Exception:
                tour_visible = False
            if tour_visible:
                try:
                    await page.keyboard.press("Escape")
                    print("[OOCL] [FS] Dismissed onboarding tour via Escape key.")
                    await page.wait_for_timeout(600)
                    continue
                except Exception:
                    pass
            break

    async def _fs_login(self, page) -> bool:
        """
        Two-step FreightSmart login:
          1. freightsmart.oocl.com/app/login — email + "Next"
          2. exiamfw.home.oocl.com (Keycloak) — password + "Sign In"
        Credentials from OOCL_USERNAME / OOCL_PASSWORD env vars.
        """
        username = (os.getenv("OOCL_USERNAME") or "").strip()
        password = (os.getenv("OOCL_PASSWORD") or "").strip()
        if not username or not password:
            print("[OOCL] [FS] OOCL_USERNAME / OOCL_PASSWORD not set — skipping FreightSmart quotes.")
            return False

        print("[OOCL] [FS] Navigating to FreightSmart login...")
        await page.goto(self.FS_LOGIN_URL, wait_until="domcontentloaded")
        await page.wait_for_timeout(2500)

        # The Cookie Notice consent overlay renders on top of the login form and
        # intercepts clicks — clear it before touching anything.
        await self._fs_dismiss_modals(page)

        # Already logged in from a previous navigation in this context?
        if "/app/login" not in (page.url or "") and "exiamfw" not in (page.url or ""):
            print(f"[OOCL] [FS] Already logged in (landed on {page.url}).")
            return True

        # Step 1: email + Next
        email_input = None
        for sel in ['input[placeholder*="Email" i]', 'input[type="email"]', 'input[type="text"]']:
            try:
                loc = page.locator(sel).first
                if await loc.is_visible(timeout=2000):
                    email_input = loc
                    break
            except Exception:
                continue
        if not email_input:
            print("[OOCL] [FS] Email input not found on login page.")
            return False
        await email_input.fill(username)
        await page.wait_for_timeout(400)
        await self._fs_dismiss_modals(page)  # consent overlay can (re)appear late
        try:
            await page.locator('button:has-text("Next")').first.click()
        except Exception as e:
            print(f"[OOCL] [FS] Could not click Next: {e}")
            return False

        # Step 2: password + Sign In (on exiamfw.home.oocl.com)
        pwd_input = page.locator('input[type="password"]').first
        try:
            await pwd_input.wait_for(state="visible", timeout=20000)
        except Exception:
            print(f"[OOCL] [FS] Password page did not load (url: {page.url}).")
            return False
        await pwd_input.fill(password)
        await page.wait_for_timeout(400)
        await self._fs_dismiss_modals(page)  # the Keycloak domain may show its own consent
        try:
            await page.locator('button:has-text("Sign In"), button:has-text("Sign in")').first.click()
        except Exception as e:
            print(f"[OOCL] [FS] Could not click Sign In: {e}")
            return False

        # Wait for redirect back into the FreightSmart app
        for _ in range(30):
            await page.wait_for_timeout(1000)
            url = page.url or ""
            if "freightsmart.oocl.com" in url and "/app/login" not in url and "exiamfw" not in url:
                print(f"[OOCL] [FS] Login successful (landed on {url}).")
                await self._fs_dismiss_modals(page)
                return True
        print(f"[OOCL] [FS] Login did not complete within 30s (url: {page.url}).")
        return False

    async def _fs_fill_port(self, page, which: str, request_value: str) -> bool:
        """Fills the origin/destination 'Enter Port or Door Point' autocomplete."""
        name, locode, cc, cn = resolve_oocl_port_info(request_value)
        idx = 0 if which == "origin" else 1
        field = page.locator('input[placeholder*="Port or Door" i]').nth(idx)
        try:
            await field.wait_for(state="visible", timeout=15000)
        except Exception:
            print(f"[OOCL] [FS] {which} port input not found.")
            return False
        await field.click()
        await field.fill("")
        await field.type(name, delay=90)
        await page.wait_for_timeout(1500)

        # Suggestions render as list rows, e.g. "Singapore, Singapore" / "Port Klang, Selangor, Malaysia"
        options = page.locator('[role="option"], li, [class*="option" i], [class*="suggest" i] div')
        best = None
        try:
            count = min(await options.count(), 15)
            for i in range(count):
                try:
                    text = (await options.nth(i).inner_text()).strip()
                except Exception:
                    continue
                if not text or name.lower() not in text.lower():
                    continue
                if cn and cn.lower() in text.lower():
                    best = options.nth(i)
                    break
                if best is None:
                    best = options.nth(i)
        except Exception:
            pass
        if best is None:
            print(f"[OOCL] [FS] No autocomplete match for {which}='{name}'.")
            return False
        await best.click()
        await page.wait_for_timeout(800)
        print(f"[OOCL] [FS] Selected {which}: {name} ({locode})")
        return True

    async def _fs_set_container_quantities(self, page) -> bool:
        """
        Opens the 'Container Type and Quantity' picker (General tab: 20GP/20RF(NOR),
        40GP, 40HQ/40RQ(NOR)) and sets quantity 1 for all three rows, so one search
        prices every size at once.
        """
        try:
            picker = page.locator('input[placeholder*="Container Type" i]').first
            await picker.click()
            await page.wait_for_timeout(1000)
        except Exception as e:
            print(f"[OOCL] [FS] Could not open container picker: {e}")
            return False

        filled = 0
        # Preferred: target each labelled row's input
        for label in ["20GP", "40GP", "40HQ"]:
            try:
                row_input = page.locator(
                    f'div:has-text("{label}") >> input').last
                if await row_input.is_visible(timeout=800):
                    await row_input.fill("1")
                    filled += 1
                    continue
            except Exception:
                pass
        if filled < 3:
            # Fallback: the picker panel exposes three visible quantity inputs
            try:
                qty_inputs = page.locator('input[type="number"]:visible')
                count = await qty_inputs.count()
                if count >= 3:
                    for i in range(count - 3, count):
                        await qty_inputs.nth(i).fill("1")
                    filled = 3
            except Exception as e:
                print(f"[OOCL] [FS] Quantity fallback failed: {e}")
        print(f"[OOCL] [FS] Container quantities set ({filled}/3 rows).")
        # Close the picker so it doesn't block the Get Quote button
        try:
            await page.keyboard.press("Escape")
            await page.wait_for_timeout(400)
        except Exception:
            pass
        return filled > 0

    @staticmethod
    def _fs_parse_card(text: str) -> Optional[dict]:
        """
        Parses one FreightSmart result card's inner text into a raw row dict.
        Text-anchored and tolerant of layout differences:
          kind    — 'E-Spot' if the card mentions E-Spot/Spot product, else 'E-Quote'
          etd/eta — 'YYYY-MM-DD', 'MM/DD' or 'DD Mon' formats
          prices  — per container-type USD amounts (20GP/40GP/40HQ/...)
          vessel/transit/free_time when present
        Returns None if the card has no usable price at all.
        """
        if not text or "USD" not in text.upper():
            return None
        t = " ".join(text.split())
        kind = "E-Spot" if re.search(r"\bE[- ]?Spot\b", t, re.IGNORECASE) else "E-Quote"

        def _parse_date(raw: str) -> Optional[str]:
            raw = raw.strip()
            m = re.match(r"(\d{4})-(\d{2})-(\d{2})$", raw)
            if m:
                return raw
            m = re.match(r"(\d{1,2})/(\d{1,2})$", raw)
            if m:
                # FreightSmart shows MM/DD (e.g. ETD 07/03); infer year, rolling over
                today = date.today()
                month, day = int(m.group(1)), int(m.group(2))
                year = today.year if (month, day) >= (today.month, today.day) or \
                    (today.month, today.day)[0] - month < 6 else today.year + 1
                try:
                    return date(year, month, day).strftime("%Y-%m-%d")
                except ValueError:
                    return None
            m = re.match(r"(\d{1,2})\s+([A-Za-z]{3})", raw)
            if m:
                return parse_oocl_date(raw, date.today().year)
            return None

        etd = eta = None
        m = re.search(r"ETD[:\s]*([0-9/\-]+|\d{1,2}\s+[A-Za-z]{3})", t, re.IGNORECASE)
        if m:
            etd = _parse_date(m.group(1))
        m = re.search(r"ETA[:\s]*([0-9/\-]+|\d{1,2}\s+[A-Za-z]{3})", t, re.IGNORECASE)
        if m:
            eta = _parse_date(m.group(1))

        transit = None
        m = re.search(r"(\d+)\s*day", t, re.IGNORECASE)
        if m:
            transit = int(m.group(1))

        free_time = None
        m = re.search(r"(?:detention|free\s*time)\D{0,30}?(\d+)\s*(?:calendar\s*)?days?", t, re.IGNORECASE) or \
            re.search(r"(\d+)\s*(?:calendar\s*)?days?\D{0,30}?detention", t, re.IGNORECASE)
        if m:
            free_time = int(m.group(1))

        vessel = None
        m = re.search(r"Vessel\s*(?:/|Voyage)?\s*[:\s]\s*([A-Z0-9][A-Z0-9 .\-]{2,40}?)(?=\s{2,}|\s+(?:ETD|ETA|USD|Transit|Service)|$)",
                      text, re.IGNORECASE)
        if m:
            vessel = m.group(1).strip()

        # Per-container prices: "40GP ... USD 1,100.00" or "40GP from USD 160" or bare
        # column layouts "20GP 800.00 40GP 1,100.00"
        prices = {}
        for label, ct in OOCLConnector.FS_CONTAINER_MAP.items():
            pm = re.search(rf"{label}[^0-9]{{0,24}}([\d,]+(?:\.\d{{1,2}})?)", t)
            if pm:
                val = float(pm.group(1).replace(",", ""))
                if val > 0 and (ct not in prices or val < prices[ct]):
                    prices[ct] = val

        total_price = None
        m = re.search(r"USD\s*([\d,]+(?:\.\d{1,2})?)", t)
        if m:
            total_price = float(m.group(1).replace(",", ""))

        if not prices and not total_price:
            return None
        return {
            "kind": kind, "etd": etd, "eta": eta, "vessel": vessel,
            "transit_time_days": transit, "free_time": free_time,
            "prices": prices, "total_price": total_price, "currency": "USD",
        }

    async def _fs_extract_rows(self, page) -> List[dict]:
        """Collects result cards from the FreightSmart quote results page."""
        os.makedirs("scratch", exist_ok=True)
        try:
            await page.screenshot(path="scratch/oocl_fs_results.png", full_page=True)
            with open("scratch/oocl_fs_results.html", "w", encoding="utf-8") as f:
                f.write(await page.content())
            print("[OOCL] [FS] Saved results debug dump to scratch/oocl_fs_results.*")
        except Exception:
            pass

        rows: List[dict] = []
        seen = set()
        card_selectors = [
            '[class*="quote-card" i]', '[class*="quoteItem" i]', '[class*="product" i]',
            '[class*="result" i] [class*="card" i]', '[class*="card" i]',
        ]
        for sel in card_selectors:
            try:
                cards = page.locator(sel)
                count = min(await cards.count(), 40)
            except Exception:
                continue
            for i in range(count):
                try:
                    text = await cards.nth(i).inner_text()
                except Exception:
                    continue
                parsed = self._fs_parse_card(text)
                if not parsed:
                    continue
                key = (parsed["kind"], parsed.get("etd"), parsed.get("total_price"),
                       tuple(sorted(parsed["prices"].items())))
                if key in seen:
                    continue
                seen.add(key)
                rows.append(parsed)
            if rows:
                break
        print(f"[OOCL] [FS] Extracted {len(rows)} priced row(s) "
              f"({sum(1 for r in rows if r['kind'] == 'E-Spot')} E-Spot, "
              f"{sum(1 for r in rows if r['kind'] == 'E-Quote')} E-Quote).")
        return rows

    async def _fs_run(self, request: RateSearchRequest) -> List[dict]:
        """Full FreightSmart phase: login → fill quote form → search → extract rows."""
        if not self.context:
            await self._init_browser()
        page = await self.context.new_page()
        try:
            if not await self._fs_login(page):
                return []
            if "/ui" not in (page.url or ""):
                await page.goto(self.FS_HOME_URL, wait_until="domcontentloaded")
                await page.wait_for_timeout(2000)
            await self._fs_dismiss_modals(page)

            if not await self._fs_fill_port(page, "origin", request.origin):
                return []
            if not await self._fs_fill_port(page, "destination", request.destination):
                return []
            await self._fs_set_container_quantities(page)

            try:
                await page.locator('button:has-text("Get Quote")').first.click()
                print("[OOCL] [FS] Submitted Get Quote search.")
            except Exception as e:
                print(f"[OOCL] [FS] Could not click Get Quote: {e}")
                return []

            # Wait for the results to render (URL change and/or price content)
            for _ in range(45):
                await page.wait_for_timeout(1000)
                try:
                    body = await page.locator("body").inner_text()
                except Exception:
                    continue
                if "USD" in body and re.search(r"E[- ]?(Spot|Quote)", body, re.IGNORECASE):
                    break
            return await self._fs_extract_rows(page)
        finally:
            try:
                await page.close()
            except Exception:
                pass

    @staticmethod
    def _fs_pair_and_select(fs_rows: List[dict], schedule_dicts: List[dict],
                            today: Optional[date] = None, window_days: int = 14) -> List[dict]:
        """
        Applies the business rules and pairs FreightSmart prices with crawled schedules:
          - Only ETDs within `window_days` (2 weeks) are considered.
          - E-Spot rows: ALL are logged (they carry their own vessel/transit/free time/ETA).
          - E-Quote rows: per ETD, only the CHEAPEST whole row is kept (row totals are
            compared; numbers are never mixed across rows).
          - If a row's ETD matches a crawled schedule ETD, missing sailing details
            (vessel, ETA, transit, service, routing) are filled from that schedule.
          - Schedule sailings whose ETD matched a priced row are replaced by the priced
            quote(s); unmatched sailings pass through unchanged (schedule-only, as today).
        Pure function — unit-testable without a browser.
        """
        today = today or date.today()
        horizon = today + timedelta(days=window_days)

        def _in_window(etd: Optional[str]) -> bool:
            if not etd:
                return True
            try:
                d = datetime.strptime(etd, "%Y-%m-%d").date()
            except ValueError:
                return True
            return today <= d <= horizon

        rows = [r for r in fs_rows if _in_window(r.get("etd"))]
        espots = [r for r in rows if r.get("kind") == "E-Spot"]
        equotes = [r for r in rows if r.get("kind") != "E-Spot"]

        # Cheapest complete E-Quote row per ETD (compare row totals; keep the row whole)
        best_equote_per_etd: dict = {}
        for r in equotes:
            prices = r.get("prices") or {}
            row_total = sum(prices.values()) if prices else (r.get("total_price") or 0)
            if row_total <= 0:
                continue
            key = r.get("etd")
            if key not in best_equote_per_etd or row_total < best_equote_per_etd[key][0]:
                best_equote_per_etd[key] = (row_total, r)
        selected = espots + [r for _, r in best_equote_per_etd.values()]

        sched_by_etd: dict = {}
        for s in schedule_dicts:
            if s.get("etd") and s["etd"] not in sched_by_etd:
                sched_by_etd[s["etd"]] = s

        out: List[dict] = []
        matched_etds = set()
        for r in selected:
            sched = sched_by_etd.get(r.get("etd")) or {}
            if sched:
                matched_etds.add(r.get("etd"))
            base = {
                "etd": r.get("etd"),
                "eta": r.get("eta") or sched.get("eta"),
                "transit_time_days": r.get("transit_time_days") or sched.get("transit_time_days"),
                "vessel": r.get("vessel") or sched.get("vessel") or "OOCL Vessel",
                "service_name": sched.get("service_name") or r.get("kind"),
                "routing": sched.get("routing") or "Direct",
                "free_time": r.get("free_time"),
                "currency": r.get("currency", "USD"),
                "source": "carrier_portal",
                "container_quantity": 1,
            }
            prices = r.get("prices") or {}
            if prices:
                for ct, price in prices.items():
                    q = dict(base)
                    q.update({
                        "container_type": ct,
                        "basic_ocean_freight": price,
                        "final_freight_value": price,
                        "raw_reference": f"OOCL-FS-{r['kind']}-{r.get('etd') or 'NA'}-{ct.replace(' ', '_')}",
                    })
                    out.append(q)
            elif r.get("total_price"):
                # Priced row without per-type breakdown — keep it untyped; the caller
                # stamps the requested container type per cycle.
                q = dict(base)
                q.update({
                    "basic_ocean_freight": r["total_price"],
                    "final_freight_value": r["total_price"],
                    "raw_reference": f"OOCL-FS-{r['kind']}-{r.get('etd') or 'NA'}",
                })
                out.append(q)

        # Unmatched schedule sailings pass through unchanged (schedule-only rows)
        for s in schedule_dicts:
            if s.get("etd") in matched_etds:
                continue
            out.append(s)
        return out

    async def close(self):
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def open_price_breakdown(self, quote_ref: dict) -> bool:
        return True

    async def extract_charge_breakdown(self) -> list[dict]:
        return []

    async def normalize_result(self, raw_quote: dict, raw_charges: list[dict]) -> QuoteSchema:
        raw_quote["etd"] = standardize_date_string(raw_quote.get("etd"))
        raw_quote["eta"] = standardize_date_string(raw_quote.get("eta"))
        return QuoteSchema(**raw_quote)

    def _serve_for_cycle(self, request: RateSearchRequest) -> list[QuoteSchema]:
        """
        Serves one container-type cycle from the cached merged quote set:
          - FreightSmart-priced quotes carry a real container_type → return only the
            ones matching this cycle's requested type.
          - Schedule-only quotes are untyped (container_type=None) → serve a deep copy
            stamped with the requested type (previous behavior).
        """
        out: list[QuoteSchema] = []
        for q in self._cached_quotes:
            if q.container_type == request.container_type:
                out.append(q.model_copy(deep=True))
            elif not q.container_type:
                out.append(q.model_copy(deep=True, update={"container_type": request.container_type}))
        return out

    async def run_full_search(self, request: RateSearchRequest) -> tuple[CarrierResultStatus, list[QuoteSchema]]:
        """
        One crawl serves all container-type cycles (cached), combining:
          1. Sailing schedules (existing 2-week CargoSmart crawl), and
          2. FreightSmart price quotes (E-Quote / E-Spot), paired to schedules by ETD
             per business rules (all E-Spots; cheapest whole E-Quote row per date).
        The FreightSmart phase is best-effort: any failure there degrades to the
        schedules-only behavior this connector always had.
        """
        if not hasattr(self, "_cached_quotes"):
            self._cached_quotes = None
            self._cached_status = None

        if self._cached_quotes is not None:
            print(f"[OOCL] Returning cached quotes for '{request.container_type}' "
                  f"(single crawl serves all container cycles).")
            cycle_quotes = self._serve_for_cycle(request)
            if cycle_quotes:
                return CarrierResultStatus.AVAILABLE_QUOTES_FOUND, cycle_quotes
            return self._cached_status, []

        try:
            # Step 1: Sailing schedules (existing behavior)
            schedule_dicts: list[dict] = []
            status = await self.search_quotes(request)
            if status == CarrierResultStatus.AVAILABLE_QUOTES_FOUND:
                schedule_dicts = await self.extract_quote_list()
            else:
                print(f"[OOCL] Schedule crawl returned {status}; continuing to FreightSmart anyway.")

            # Step 2: FreightSmart price quotes (best-effort)
            fs_rows: list[dict] = []
            if os.getenv("OOCL_QUERY_FREIGHTSMART", "true").strip().lower() not in ("false", "0", "no"):
                try:
                    fs_rows = await self._fs_run(request)
                except Exception as fs_err:
                    print(f"[OOCL] [FS] FreightSmart phase failed (falling back to schedules-only): {fs_err}")
            else:
                print("[OOCL] OOCL_QUERY_FREIGHTSMART=false — schedules-only mode.")

            # Step 3: Pair & select per business rules
            merged_dicts = self._fs_pair_and_select(fs_rows, schedule_dicts)

            quotes: list[QuoteSchema] = []
            for raw in merged_dicts:
                try:
                    quotes.append(await self.normalize_result(dict(raw), []))
                except Exception as norm_err:
                    print(f"[OOCL] Warning: could not normalize merged quote: {norm_err}")

            if quotes:
                self._cached_quotes = quotes
                self._cached_status = CarrierResultStatus.AVAILABLE_QUOTES_FOUND
                cycle_quotes = self._serve_for_cycle(request)
                if cycle_quotes:
                    return CarrierResultStatus.AVAILABLE_QUOTES_FOUND, cycle_quotes
                return CarrierResultStatus.NO_QUOTES_AVAILABLE, []

            # Nothing at all — cache the definitive no-quotes outcome; transient
            # errors (timeouts etc.) are NOT cached so later cycles can retry.
            if status in (CarrierResultStatus.AVAILABLE_QUOTES_FOUND, CarrierResultStatus.NO_QUOTES_AVAILABLE):
                self._cached_quotes = []
                self._cached_status = CarrierResultStatus.NO_QUOTES_AVAILABLE
                return CarrierResultStatus.NO_QUOTES_AVAILABLE, []
            return status, []

        except Exception as e:
            print(f"[OOCL] Unexpected error in full search: {e}")
            return CarrierResultStatus.UNKNOWN_ERROR, []
        finally:
            await asyncio.shield(self.close())
