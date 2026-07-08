"""
OOCL Live Connector â€” Playwright automation for Sailing Schedules.
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


def clean_vessel_name(v: str) -> str:
    if not v:
        return ""
    # Remove service prefixes like LL2, CPX, LL6, LL7, THX, etc. (2-4 uppercase letters/numbers)
    v = re.sub(r"^[A-Z0-9]{2,4}\s+", "", v)
    # Remove voyage suffixes (like 007 W, 192 E, 015 W, etc. - digits followed by compass direction or letters)
    v = re.sub(r"\s+\d+[A-Z]?\s*$", "", v)
    v = re.sub(r"\s+\d+\s+[A-Z]\s*$", "", v)
    return v.strip().lower()

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

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # FREIGHTSMART (price quotes: E-Quote / E-Spot)
    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    FS_LOGIN_URL = "https://freightsmart.oocl.com/app/login?loginType=OOCL"
    FS_HOME_URL = "https://freightsmart.oocl.com/ui/"

    # FreightSmart container labels -> internal container type codes.
    # (NOR reefer variants price as their dry size.)
    FS_CONTAINER_MAP = {
        "20GP": "DRY 20", "20RF": "DRY 20",
        "40GP": "DRY 40",
        "40HQ": "DRY 40H", "40RQ": "DRY 40H",
    }

    _TOUR_HEADINGS = [
        "Welcome to the new FreightSmart",
        "All Search Results in One View"
    ]

    async def _fs_tour_present(self, page) -> bool:
        """Shadow-DOM-aware check for whether the onboarding tour heading is on screen."""
        try:
            return await page.evaluate(
                """(headings) => {
                    const collect = (root, out) => {
                        for (const el of root.querySelectorAll('*')) {
                            out.push(el);
                            if (el.shadowRoot) collect(el.shadowRoot, out);
                        }
                        return out;
                    };
                    return collect(document, []).some(el =>
                        el.children.length === 0 && headings.some(h => (el.textContent || '').includes(h)));
                }""",
                self._TOUR_HEADINGS,
            )
        except Exception:
            return False

    async def _fs_popup_watcher_loop(self, page, stop_event: asyncio.Event,
                                     lock: Optional[asyncio.Lock] = None):
        """
        Runs CONCURRENTLY with the rest of the FreightSmart form-filling flow and
        dismisses the onboarding tour the instant it appears â€” live-observed to render
        mid-way through typing into the origin field, which a watcher that only checks
        between discrete steps is too late to catch (typing had already progressed by
        the time the fixed per-step checks would next run). Polls on a short interval
        so it reacts within a few hundred ms regardless of what the main coroutine is
        doing, since Playwright actions yield control to the event loop on every await.

        Detection (_fs_tour_present, read-only JS) always runs freely. Dismissal
        (real clicks/Escape) is serialized via `lock` against the main flow's typing â€”
        without that, an earlier version of this watcher stole focus mid-.type() and
        truncated the typed port name (live-observed + reproduced in testing).
        """
        while not stop_event.is_set():
            try:
                tour_present = await self._fs_tour_present(page)
                generic_modal_present = await page.locator('.ant-modal-wrap, [class*="modal" i], [class*="dialog" i]').first.is_visible()
                if tour_present or generic_modal_present:
                    print(f"[OOCL] [FS] Watcher: popup/modal detected (tour={tour_present}, generic={generic_modal_present}) â€” dismissing...")
                    await self._fs_dismiss_modals(page, lock=lock)
            except Exception as loop_err:
                print(f"[OOCL] [FS] Watcher loop error: {loop_err}")
            try:
                await asyncio.wait_for(stop_event.wait(), timeout=0.4)
            except asyncio.TimeoutError:
                pass

    async def _fs_click_tour_x_by_position(self, page) -> bool:
        """
        Position-based fallback for the onboarding tour popup: instead of guessing its
        close icon's class/aria-label (which a live run showed our selector guesses did
        not match â€” likely a third-party guide widget with unpredictable markup, possibly
        in a shadow root), locate the popup by its heading text, then click the smallest
        short-text/icon element sitting in its TOP-RIGHT corner â€” the conventional
        position of an X â€” while explicitly excluding anything containing "Start Tour"
        or the step-pagination dots. Returns True if a click was dispatched.
        """
        js = """
            (heading) => {
                const collect = (root, out) => {
                    for (const el of root.querySelectorAll('*')) {
                        out.push(el);
                        if (el.shadowRoot) collect(el.shadowRoot, out);
                    }
                    return out;
                };
                const all = collect(document, []);
                const headEl = all.find(el =>
                    (el.textContent || '').trim() === heading ||
                    (el.children.length === 0 && (el.textContent || '').includes(heading)));
                if (!headEl) return { found: false };
                // Walk up to the smallest ancestor that ALSO contains "Start Tour" â€”
                // that bounds the whole popup card.
                let container = headEl;
                for (let i = 0; i < 8 && container.parentElement; i++) {
                    container = container.parentElement;
                    if ((container.textContent || '').includes('Start Tour')) break;
                }
                const rect = container.getBoundingClientRect();
                if (!rect.width || !rect.height) return { found: false };
                const candidates = [];
                collect(container, candidates);
                let best = null, bestScore = Infinity;
                for (const el of candidates) {
                    const text = (el.textContent || '').trim();
                    if (text.includes('Start Tour')) continue;
                    if (text.length > 2) continue;  // an X/icon has ~0-1 chars of text
                    const r = el.getBoundingClientRect();
                    if (!r.width || !r.height) continue;
                    const relX = (r.left - rect.left) / rect.width;
                    const relY = (r.top - rect.top) / rect.height;
                    if (relX < 0.55 || relY > 0.45) continue;  // must be top-right-ish
                    const score = (1 - relX) + relY;  // smaller = closer to top-right corner
                    if (score < bestScore) { bestScore = score; best = el; }
                }
                if (!best) return { found: true, clicked: false };
                const r = best.getBoundingClientRect();
                return { found: true, clicked: true, x: r.left + r.width / 2, y: r.top + r.height / 2 };
            }
        """
        for heading in self._TOUR_HEADINGS:
            try:
                result = await page.evaluate(js, heading)
                if result.get("found") and result.get("clicked"):
                    x, y = result["x"], result["y"]
                    await page.mouse.click(x, y)
                    print(f"[OOCL] [FS] Dismissed tour popup '{heading}' via position heuristic at ({x}, {y})")
                    return True
            except Exception:
                continue
        return False

    async def _fs_dismiss_modals(self, page, lock: Optional[asyncio.Lock] = None):
        """
        Closes FreightSmart popups. Order matters:
          1. Cookie Notice consent ("Accept All") â€” appears on the login page and
             intercepts the Next/Sign In clicks.
          2. The "Welcome to the new FreightSmart" onboarding tour carousel â€” closed
             via its X icon specifically. "Start Tour" is deliberately never matched
             here; clicking it would launch the tour instead of dismissing it.
          3. Generic dialog close buttons (e.g. the post-login "Important Update").
          4. Position-based X heuristic (shadow-DOM aware) â€” for when the tour's close
             icon markup doesn't match any of the guessed selectors above.
          5. Escape key as a final resort.
        Called repeatedly at several points in _fs_run (not just once) since this widget
        can render a few seconds after the page otherwise looks settled.

        When called from the background watcher, pass the same `lock` used to guard
        the main flow's critical typing/clicking â€” this serializes the ACT of dismissal
        against those actions (never runs a click/Escape mid-.type()) without blocking
        the read-only detection in _fs_tour_present, which needs no lock.
        """
        async def _dismiss_once() -> bool:
            selectors = [
                'button:has-text("Accept All")', 'button:has-text("Accept all")',
                '#onetrust-accept-btn-handler', 'button:has-text("Agree")',
            ]
            for heading in self._TOUR_HEADINGS:
                selectors.extend([
                    f'div:has-text("{heading}") button[aria-label="Close" i]',
                    f'div:has-text("{heading}") [aria-label="close" i]',
                    f'div:has-text("{heading}") button:not(:has-text("Start Tour"))',
                    f'div:has-text("{heading}") [class*="close" i]',
                ])
            selectors.extend([
                '.ant-modal-close', '.ant-modal-close-x', '.ant-modal-wrap button.ant-modal-close',
                'button:has-text("Close")', 'button:has-text("OK")',
                '[class*="dialog" i] [class*="close" i]', '[aria-label="Close" i]', '[aria-label="close" i]'
            ])
            for sel in selectors:
                try:
                    btn = page.locator(sel).first
                    if await btn.is_visible():
                        await btn.click()
                        print(f"[OOCL] [FS] Dismissed popup via: {sel}")
                        await page.wait_for_timeout(600)
                        return True
                except Exception:
                    continue

            # General modal escape fallback
            try:
                modal_present = await page.locator('.ant-modal-wrap, [class*="modal" i], [class*="dialog" i]').first.is_visible()
                if modal_present:
                    await page.keyboard.press("Escape")
                    print("[OOCL] [FS] Dismissed popup via general Escape key.")
                    await page.wait_for_timeout(600)
                    return True
            except Exception:
                pass

            # Try the position heuristic for the onboarding tour specifically
            if not await self._fs_tour_present(page):
                return False
            if await self._fs_click_tour_x_by_position(page):
                await page.wait_for_timeout(600)
                return True
            return False

        for _ in range(4):
            if lock is not None:
                async with lock:
                    closed_any = await _dismiss_once()
            else:
                closed_any = await _dismiss_once()
            if not closed_any:
                break

    async def _fs_login(self, page) -> bool:
        """
        Two-step FreightSmart login:
          1. freightsmart.oocl.com/app/login â€” email + "Next"
          2. exiamfw.home.oocl.com (Keycloak) â€” password + "Sign In"
        Credentials from OOCL_USERNAME / OOCL_PASSWORD env vars.
        """
        username = (os.getenv("OOCL_USERNAME") or "").strip()
        password = (os.getenv("OOCL_PASSWORD") or "").strip()
        if not username or not password:
            print("[OOCL] [FS] OOCL_USERNAME / OOCL_PASSWORD not set â€” skipping FreightSmart quotes.")
            return False

        print("[OOCL] [FS] Navigating to FreightSmart login...")
        await page.goto(self.FS_LOGIN_URL, wait_until="domcontentloaded")
        await page.wait_for_timeout(2500)

        # The Cookie Notice consent overlay renders on top of the login form and
        # intercepts clicks â€” clear it before touching anything.
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

    async def _fs_fill_port(self, page, which: str, request_value: str,
                            lock: Optional[asyncio.Lock] = None) -> bool:
        """
        Fills the origin/destination 'Enter Port or Door Point' autocomplete.
        The click+fill+type sequence is serialized against `lock` (shared with the
        background popup watcher): live-observed, the onboarding tour appearing
        mid-type let the watcher's dismissal action (a click/Escape) steal focus
        from the field, truncating the typed text. Holding the lock only for this
        sequence â€” not the whole function â€” blocks the watcher from acting during
        typing while still letting it clear a popup that shows up right after, before
        the dropdown-option search/click that follows.
        """
        name, locode, cc, cn = resolve_oocl_port_info(request_value)
        idx = 0 if which == "origin" else 1
        field = page.locator('input[placeholder*="Port or Door" i]').nth(idx)
        try:
            await field.wait_for(state="visible", timeout=15000)
        except Exception:
            print(f"[OOCL] [FS] {which} port input not found.")
            return False

        # Try up to 3 times to type and select suggestion
        for attempt in range(1, 4):
            print(f"[OOCL] [FS] Filling {which} port (attempt {attempt}/3)...")
            
            # Dismiss any popups beforehand
            await self._fs_dismiss_modals(page, lock=lock)
            
            try:
                await field.click(timeout=3000)
            except Exception as click_err:
                print(f"[OOCL] [FS] Click {which} input blocked, dismissing modals: {click_err}")
                await self._fs_dismiss_modals(page, lock=lock)
                await field.click(timeout=3000)

            await field.fill("")

            if lock is not None:
                async with lock:
                    await field.type(name, delay=100)
            else:
                await field.type(name, delay=100)
            
            await page.wait_for_timeout(1500)
            
            # Dismiss popups that might have appeared during or right after typing
            await self._fs_dismiss_modals(page, lock=lock)

            # Suggestions render as list rows
            options = page.locator('.ant-popover:not(.ant-popover-hidden) .location-item, .ant-select-dropdown:not(.ant-select-dropdown-hidden) .ant-select-item-option')
            best = None
            try:
                count = min(await options.count(), 20)
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

            if best is not None:
                try:
                    await best.click()
                    await page.wait_for_timeout(800)
                    print(f"[OOCL] [FS] Selected {which}: {name} ({locode})")
                    return True
                except Exception as click_err:
                    print(f"[OOCL] [FS] Failed to click option on attempt {attempt}: {click_err}")
            
            print(f"[OOCL] [FS] No autocomplete match or visible suggestions for {which}='{name}' on attempt {attempt}.")

        return False

    async def _fs_set_container_quantities(self, page, lock: Optional[asyncio.Lock] = None) -> bool:
        """
        Opens the 'Container Type and Quantity' picker (General tab: 20GP/20RF(NOR),
        40GP, 40HQ/40RQ(NOR)) and sets quantity 1 for all three rows, so one search
        prices every size at once. Serialized against `lock` (see _fs_fill_port) so
        the watcher's own Escape-key fallback can't fire while this picker is open
        and also relying on Escape to close itself.
        """
        async def _do_fill():
            try:
                picker = page.locator('.cargo-input-wrap .input-container').first
                await picker.click()
                await page.wait_for_timeout(1000)
            except Exception as e:
                print(f"[OOCL] [FS] Could not open container picker: {e}")
                return 0

            filled = 0
            # Direct/Preferred: target by the class inside the container popover
            try:
                inputs = page.locator('.ant-popover:not(.ant-popover-hidden) input.ant-input-number-input')
                await inputs.first.wait_for(state="visible", timeout=5000)
                count = await inputs.count()
                if count >= 3:
                    for i in range(3):
                        await inputs.nth(i).fill("1")
                    filled = 3
            except Exception as fill_err:
                print(f"[OOCL] [FS] Direct popover input fill failed: {fill_err}")

            if filled < 3:
                # Preferred: target each labelled row's input
                for label in ["20GP", "40GP", "40HQ"]:
                    try:
                        row_input = page.locator(
                            f'div:has-text("{label}") >> input').last
                        if await row_input.is_visible():
                            await row_input.fill("1")
                            filled += 1
                            continue
                    except Exception:
                        pass
            print(f"[OOCL] [FS] Container quantities set ({filled}/3 rows).")
            # Close the picker so it doesn't block the Get Quote button
            try:
                await page.keyboard.press("Escape")
                await page.wait_for_timeout(400)
            except Exception:
                pass
            return filled

        if lock is not None:
            async with lock:
                filled = await _do_fill()
        else:
            filled = await _do_fill()
        return filled > 0

    @staticmethod
    def _fs_parse_card(text: str, active_date: Optional[str] = None) -> Optional[dict]:
        """
        Parses one FreightSmart result card's inner text into a raw row dict.
        Text-anchored and tolerant of layout differences:
          kind    — 'E-Spot' if the card mentions E-Spot/Spot/Smart Uno/Smart Combo product, else 'E-Quote'
          etd/eta — 'YYYY-MM-DD', 'MM/DD' or 'DD Mon' formats
          prices  — per container-type USD amounts (20GP/40GP/40HQ/...)
          vessel/transit/free_time when present
        Returns None if the card has no usable price at all and is not sold out.
        """
        if not text:
            return None

        # Pre-process text to separate concatenated words/labels on BOTH sides
        t = text
        for label in ["20GP", "40GP", "40HQ", "20RF", "40RQ"]:
            t = re.sub(rf"({label})", r" \1 ", t, flags=re.IGNORECASE)
        for keyword in ["Origin", "Destination", "Smart Uno", "Smart Combo", "Transit Time", "Vessel", "ETD", "ETA", "CY", "Cut-off"]:
            t = re.sub(rf"({keyword})", r" \1 ", t, flags=re.IGNORECASE)
            
        t = " ".join(t.split())
        
        kind = "E-Spot" if (re.search(r"\bE[- ]?Spot\b", t, re.IGNORECASE) or 
                            "smart uno" in t.lower() or 
                            "smart combo" in t.lower()) else "E-Quote"

        is_sold_out = "sold out" in text.lower() or "***" in text
        if not is_sold_out and "USD" not in text.upper():
            return None

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
        # FTD - FTA date range
        m = re.search(r"(\d{1,2}\s+[A-Za-z]{3})\s*-\s*(\d{1,2}\s+[A-Za-z]{3})", t, re.IGNORECASE)
        if m:
            etd = _parse_date(m.group(1))
            eta = _parse_date(m.group(2))
            
        if not etd or not eta:
            m = re.search(r"ETD[:\s]*([0-9/\-]+|\d{1,2}\s+[A-Za-z]{3})", t, re.IGNORECASE)
            if m:
                etd = _parse_date(m.group(1))
            m = re.search(r"ETA[:\s]*([0-9/\-]+|\d{1,2}\s+[A-Za-z]{3})", t, re.IGNORECASE)
            if m:
                eta = _parse_date(m.group(2) if len(m.groups()) > 1 else m.group(1))

        if not etd:
            etd = active_date

        # Parse Rate Valid range
        validity_start = validity_end = None
        vm = re.search(r"Rate\s+Valid\s*(\d{1,2}\s+[A-Za-z]{3}\s+\d{4})\s*-\s*(\d{1,2}\s+[A-Za-z]{3}\s+\d{4})", t, re.IGNORECASE)
        if vm:
            try:
                validity_start = datetime.strptime(vm.group(1), "%d %b %Y").date().strftime("%Y-%m-%d")
                validity_end = datetime.strptime(vm.group(2), "%d %b %Y").date().strftime("%Y-%m-%d")
            except ValueError:
                pass

        transit = None
        m = re.search(r"(\d+)\s*day", t, re.IGNORECASE)
        if m:
            transit = int(m.group(1))

        # Free time
        free_time = None
        # Match Destination COMBO 14 CD or Destination DD2in1 11 CD
        m = re.search(r"Destination\s+(?:[A-Z0-9a-z-]+\s+){0,3}(\d+)\s*(?:CD|WD|calendar\s*days?|days?)", t, re.IGNORECASE)
        if m:
            free_time = int(m.group(1))
        else:
            m = re.search(r"(?:detention|free\s*time)\D{0,30}?(\d+)\s*(?:calendar\s*)?days?", t, re.IGNORECASE) or \
                re.search(r"(\d+)\s*(?:calendar\s*)?days?\D{0,30}?detention", t, re.IGNORECASE)
            if m:
                free_time = int(m.group(1))

        vessel = None
        # Start of card text before CY/Cut-off/ETD
        m = re.search(r"^([A-Z0-9][A-Z0-9 .\-]{2,45}?)(?=\s+(?:CY|Cut-off|ETD|ETA|Transit|USD|Service))", t, re.IGNORECASE)
        if m:
            vessel = m.group(1).strip()
        else:
            m = re.search(r"Vessel\s*(?:/|Voyage)?\s*[:\s]\s*([A-Z0-9][A-Z0-9 .\-]{2,40}?)(?=\s{2,}|\s+(?:ETD|ETA|USD|Transit|Service)|$)",
                          text, re.IGNORECASE)
            if m:
                vessel = m.group(1).strip()

        # Per-container prices
        prices = {}
        for label, ct in OOCLConnector.FS_CONTAINER_MAP.items():
            pm = re.search(rf"{label}\s*USD\s*([\d,]+(?:\.\d{{1,2}})?)", t, re.IGNORECASE)
            if pm:
                val = float(pm.group(1).replace(",", ""))
                if val > 0 and (ct not in prices or val < prices[ct]):
                    prices[ct] = val

        total_price = None
        m = re.search(r"USD\s*([\d,]+(?:\.\d{1,2})?)", t)
        if m:
            total_price = float(m.group(1).replace(",", ""))

        if not prices and not total_price and not is_sold_out:
            return None
        return {
            "kind": kind, "etd": etd, "eta": eta, "vessel": vessel,
            "transit_time_days": transit, "free_time": free_time,
            "prices": prices, "total_price": total_price, "currency": "USD",
            "validity_start": validity_start, "validity_end": validity_end,
            "is_sold_out": is_sold_out,
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

        # Initialize espot vessels tracking set
        if not hasattr(self, "espot_vessels") or self.espot_vessels is None:
            self.espot_vessels = set()

        # Retrieve active calendar date from the page
        active_date = None
        try:
            active_date_el = page.locator(".date-item.active .date-text, [class*=\"date-item\" i][class*=\"active\" i] [class*=\"date-text\" i]").first
            if await active_date_el.is_visible():
                active_date = (await active_date_el.inner_text()).strip()
                print(f"[OOCL] [FS] Active calendar date detected: {active_date}")
        except Exception as e:
            print(f"[OOCL] [FS] Could not retrieve active calendar date: {e}")

        # First, click any "More Smart Combo Offers" or show-more buttons to expand all options
        try:
            more_buttons = page.locator('button:has-text("More Smart Combo"), .show-more-container button, [class*="show-more" i] button')
            count = await more_buttons.count()
            for i in range(count):
                btn = more_buttons.nth(i)
                if await btn.is_visible():
                    await btn.click()
                    await page.wait_for_timeout(500)
        except Exception as e:
            print(f"[OOCL] [FS] Warning: could not click show-more buttons: {e}")

        # Let's query the outer container card wrappers
        containers = page.locator('.product-card-container')
        container_count = await containers.count()
        
        rows: List[dict] = []
        seen = set()

        for c_idx in range(container_count):
            container = containers.nth(c_idx)
            
            # Check if this container is an E-Spot container
            container_text = await container.inner_text()
            is_espot = ("smart uno" in container_text.lower() or 
                        "smart combo" in container_text.lower() or 
                        "e-spot" in container_text.lower())
            
            # 1. Parse the main/first card in this container to extract header info
            first_card = container.locator('.product-card').first
            if not await first_card.is_visible():
                continue
                
            first_text = await first_card.inner_text()
            first_parsed = self._fs_parse_card(first_text, active_date=active_date)
            if not first_parsed:
                continue
                
            # Header fields to inherit
            vessel = first_parsed.get("vessel")
            etd = first_parsed.get("etd")
            eta = first_parsed.get("eta")
            transit = first_parsed.get("transit_time_days")

            if is_espot and vessel:
                cleaned_v = clean_vessel_name(vessel)
                if cleaned_v:
                    self.espot_vessels.add(cleaned_v)
            
            # 2. Parse all product-cards inside this container (which represent the sub-rows)
            sub_cards = container.locator('.product-card')
            sub_count = await sub_cards.count()
            
            for s_idx in range(sub_count):
                card = sub_cards.nth(s_idx)
                card_text = await card.inner_text()
                parsed = self._fs_parse_card(card_text, active_date=active_date)
                if not parsed:
                    continue
                    
                # Inherit header info if missing
                if not parsed.get("vessel"):
                    parsed["vessel"] = vessel
                if not parsed.get("etd"):
                    parsed["etd"] = etd
                if not parsed.get("eta"):
                    parsed["eta"] = eta
                if not parsed.get("transit_time_days"):
                    parsed["transit_time_days"] = transit
                if is_espot:
                    parsed["kind"] = "E-Spot"
                    if parsed.get("vessel"):
                        cleaned_v = clean_vessel_name(parsed["vessel"])
                        if cleaned_v:
                            self.espot_vessels.add(cleaned_v)
                    
                # Drop if sold out or has no price
                if parsed.get("is_sold_out") or (not parsed.get("prices") and not parsed.get("total_price")):
                    continue

                # Deduplicate
                key = (parsed["kind"], parsed.get("etd"), parsed.get("total_price"),
                       tuple(sorted(parsed["prices"].items())), parsed.get("free_time"))
                if key in seen:
                    continue
                seen.add(key)
                rows.append(parsed)

        # Fallback to old behavior if no containers found
        if not rows:
            print("[OOCL] [FS] No product-card-container elements found. Falling back to flat selectors.")
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
                    parsed = self._fs_parse_card(text, active_date=active_date)
                    if not parsed:
                        continue
                    
                    if parsed.get("kind") == "E-Spot" and parsed.get("vessel"):
                        cleaned_v = clean_vessel_name(parsed["vessel"])
                        if cleaned_v:
                            self.espot_vessels.add(cleaned_v)

                    # Drop if sold out or has no price
                    if parsed.get("is_sold_out") or (not parsed.get("prices") and not parsed.get("total_price")):
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


    async def _fs_iterate_calendar_dates(self, page) -> List[dict]:
        """
        Iterates through the FreightSmart results date calendar to collect E-Quote and E-Spot
        rows for every date within the next 14 days that has available pricing.

        Strategy:
        1. Click the '>' nav button on the date strip to open the full 2-month calendar popup.
        2. Read the visible month headers (e.g. "2026 Jul", "2026 Aug") to determine which
           months are displayed.
        3. Scan all `custom-date-cell` elements, compute each cell's full date from its day
           number + the month context, and filter to todayâ†’today+14.
        4. For each in-window date with a non-'--' price, click its cell directly inside the
           popup (which closes the calendar and updates the result cards below).
        5. Extract rows; then re-open the calendar for the next date.
        6. Fallback: if the calendar cannot be opened or cells can't be read, fall back to
           scanning the visible date strip.
        """
        today = date.today()
        horizon = today + timedelta(days=14)

        MONTH_ABBR = {
            "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
            "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
        }

        async def _open_calendar() -> bool:
            """Click the forward nav button on the date strip to open the calendar popup."""
            try:
                # The '>' button that opens the full 2-month calendar
                nav_btn = page.locator(
                    ".date-navigation button.nav-button:last-child, "
                    ".calendar-container button.nav-button:last-child"
                ).last
                if await nav_btn.is_visible(timeout=3000):
                    await nav_btn.click()
                    await page.wait_for_timeout(1000)
                    # Confirm the calendar popup appeared
                    if await page.locator(".custom-date-cell").first.is_visible(timeout=3000):
                        return True
            except Exception as e:
                print(f"[OOCL] [FS] _open_calendar failed: {e}")
            return False

        async def _read_calendar_dates() -> List[tuple]:
            """
            Returns list of (date_str, cell_locator_index) for dates in the 14-day window
            that have a non-'--' price.  The index lets us re-locate the cell later.
            """
            results = []
            try:
                # Extract month/year pairs via JavaScript from the calendar header text
                # The calendar shows two month panels side-by-side (e.g. "2026 Jul" "2026 Aug")
                month_year_pairs: List[tuple] = []
                header_texts: List[str] = await page.evaluate("""
                    () => {
                        const all = document.querySelectorAll('[class*="calendar-header"], [class*="month-header"], [class*="panel-header"], [class*="calendar-title"]');
                        return Array.from(all).map(el => el.innerText.trim()).filter(t => t.length > 0);
                    }
                """)
                for ht in header_texts:
                    m = re.search(r"(\d{4})\s+([A-Za-z]{3,9})", ht) or \
                        re.search(r"([A-Za-z]{3,9})\s+(\d{4})", ht)
                    if m:
                        g = m.groups()
                        year_str = g[0] if g[0].isdigit() else g[1]
                        mon_str = g[1] if g[0].isdigit() else g[0]
                        mon_num = MONTH_ABBR.get(mon_str.lower()[:3])
                        if mon_num and (int(year_str), mon_num) not in month_year_pairs:
                            month_year_pairs.append((int(year_str), mon_num))

                if not month_year_pairs:
                    # Fallback: infer from today (Jul + Aug if not Dec)
                    month_year_pairs = [(today.year, today.month)]
                    if today.month == 12:
                        month_year_pairs.append((today.year + 1, 1))
                    else:
                        month_year_pairs.append((today.year, today.month + 1))

                print(f"[OOCL] [FS] Calendar months detected: {month_year_pairs}")

                # Read all custom-date-cell elements
                cells = page.locator(".custom-date-cell")
                cell_count = await cells.count()
                # Split cells roughly evenly across the two months
                cells_per_month = cell_count // max(len(month_year_pairs), 1)

                for i in range(cell_count):
                    cell = cells.nth(i)
                    try:
                        text = (await cell.inner_text()).strip()
                    except Exception:
                        continue
                    lines = [l.strip() for l in text.splitlines() if l.strip()]
                    if not lines:
                        continue
                    day_str = lines[0]
                    if not day_str.isdigit():
                        continue
                    day = int(day_str)

                    # Determine which month this cell belongs to
                    month_idx = min(i // max(cells_per_month, 1), len(month_year_pairs) - 1)
                    year, month = month_year_pairs[month_idx]

                    try:
                        cell_date = date(year, month, day)
                    except ValueError:
                        continue

                    if not (today <= cell_date <= horizon):
                        continue

                    # Check for a non-'--' price
                    price_lines = lines[1:]
                    has_price = any(
                        p and p not in ("-", "--") and "sold" not in p.lower()
                        for p in price_lines
                    )
                    if not has_price:
                        continue

                    results.append((cell_date.strftime("%Y-%m-%d"), i))
                    print(f"[OOCL] [FS] Calendar: date {cell_date} has price (cell #{i}): {price_lines}")

            except Exception as e:
                print(f"[OOCL] [FS] _read_calendar_dates error: {e}")
            return results

        async def _click_date_strip_item(target_date_str: str) -> bool:
            """Click a date in the visible date strip (used as fallback after calendar issues)."""
            try:
                strip_items = page.locator(".date-item")
                strip_count = await strip_items.count()
                for i in range(strip_count):
                    item = strip_items.nth(i)
                    try:
                        dt = (await item.locator(".date-text").inner_text()).strip()
                    except Exception:
                        continue
                    if dt == target_date_str:
                        await item.click()
                        await page.wait_for_timeout(1500)
                        await self._fs_dismiss_modals(page)
                        return True
            except Exception:
                pass
            return False

        # â”€â”€ Main flow â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

        all_rows: List[dict] = []
        seen_keys: set = set()
        available_dates: List[tuple] = []  # list of (date_str, cell_index)

        # Step 1: Open calendar and discover available dates
        if await _open_calendar():
            available_dates = await _read_calendar_dates()
            # Close the calendar before proceeding
            try:
                await page.keyboard.press("Escape")
                await page.wait_for_timeout(1000)
            except Exception:
                pass

        # Step 2: If calendar parsing failed, fall back to date strip discovery
        if not available_dates:
            print("[OOCL] [FS] Calendar date discovery failed. Falling back to date strip scan.")
            try:
                strip_items = page.locator(".date-item")
                sc = await strip_items.count()
                for i in range(sc):
                    item = strip_items.nth(i)
                    try:
                        dt_text = (await item.locator(".date-text").inner_text()).strip()
                        if not dt_text:
                            continue
                        item_date = datetime.strptime(dt_text, "%Y-%m-%d").date()
                    except Exception:
                        continue
                    if not (today <= item_date <= horizon):
                        continue
                    price_els = item.locator(".price-text")
                    pc = await price_els.count()
                    has_price = False
                    for pi in range(pc):
                        pt = (await price_els.nth(pi).inner_text()).strip()
                        if pt and pt not in ("-", "--") and "sold" not in pt.lower():
                            has_price = True
                            break
                    if has_price:
                        available_dates.append((dt_text, -1))  # -1 = no cell index
            except Exception as e:
                print(f"[OOCL] [FS] Date strip scan failed: {e}")

        date_strings = sorted(set(d for d, _ in available_dates))
        print(f"[OOCL] [FS] Dates with availability in next 14 days: {date_strings}")

        if not date_strings:
            print("[OOCL] [FS] No dated availability found â€” extracting current active date only.")
            return await self._fs_extract_rows(page)

        # Step 3: For each available date, click it and extract rows
        for target_date_str in date_strings:
            print(f"[OOCL] [FS] Processing date: {target_date_str}")
            clicked = False

            # Strategy A: open calendar, find the cell by index, click it directly
            cell_index = next((ci for ds, ci in available_dates if ds == target_date_str), -1)
            if cell_index >= 0:
                if await _open_calendar():
                    try:
                        cells = page.locator(".custom-date-cell")
                        cell = cells.nth(cell_index)
                        if await cell.is_visible(timeout=3000):
                            await cell.click()
                            await page.wait_for_timeout(1500)
                            await self._fs_dismiss_modals(page)
                            clicked = True
                            print(f"[OOCL] [FS] Clicked calendar cell #{cell_index} for {target_date_str}.")
                    except Exception as e:
                        print(f"[OOCL] [FS] Calendar cell click failed for {target_date_str}: {e}")
                        try:
                            await page.keyboard.press("Escape")
                            await page.wait_for_timeout(800)
                        except Exception:
                            pass

            # Strategy B: click the date strip item
            if not clicked:
                clicked = await _click_date_strip_item(target_date_str)
                if clicked:
                    print(f"[OOCL] [FS] Clicked date strip for {target_date_str}.")

            if not clicked:
                print(f"[OOCL] [FS] Could not click date {target_date_str} â€” skipping.")
                continue

            # Extract rows for this date
            date_rows = await self._fs_extract_rows(page)
            for r in date_rows:
                r_copy = dict(r)
                if r_copy.get("kind") != "E-Spot":
                    r_copy["etd"] = target_date_str  # stamp E-Quote with the clicked date
                key = (
                    r_copy.get("kind"),
                    r_copy.get("etd"),
                    r_copy.get("free_time"),
                    tuple(sorted(r_copy.get("prices", {}).items())),
                )
                if key in seen_keys:
                    continue
                seen_keys.add(key)
                all_rows.append(r_copy)

        print(
            f"[OOCL] [FS] Calendar iteration complete â€” "
            f"{len(all_rows)} total rows "
            f"({sum(1 for r in all_rows if r.get('kind') == 'E-Spot')} E-Spot, "
            f"{sum(1 for r in all_rows if r.get('kind') == 'E-Quote')} E-Quote) "
            f"across {len(date_strings)} date(s)."
        )
        return all_rows
    async def _fs_run(self, request: RateSearchRequest) -> List[dict]:
        """Full FreightSmart phase: login â†’ fill quote form â†’ search â†’ extract rows."""
        if not self.context:
            await self._init_browser()
        page = await self.context.new_page()
        watcher_task = None
        stop_event = None
        try:
            if not await self._fs_login(page):
                return []
            if "/ui" not in (page.url or ""):
                await page.goto(self.FS_HOME_URL, wait_until="domcontentloaded")
                await page.wait_for_timeout(2000)
            await self._fs_dismiss_modals(page)

            # Background watcher: live-observed, the onboarding tour can render
            # mid-way into typing into the origin field â€” a race that any sequence
            # of fixed between-step checks is too slow to reliably catch (typing had
            # already progressed before the next checkpoint would run). This watcher
            # runs CONCURRENTLY for the whole form-filling phase and dismisses the tour
            # within ~400ms of it appearing, no matter what the main flow is doing.
            #
            # `ui_lock` serializes the watcher's dismissal actions against the main
            # flow's critical click/fill/type sequences (passed into _fs_fill_port /
            # _fs_set_container_quantities below) â€” an earlier version without this
            # let the watcher's click/Escape steal focus mid-.type(), truncating the
            # typed port name (reproduced in testing: "SINGAPORE" -> "SINGA").
            stop_event = asyncio.Event()
            ui_lock = asyncio.Lock()
            watcher_task = asyncio.create_task(
                self._fs_popup_watcher_loop(page, stop_event, lock=ui_lock))

            if not await self._fs_fill_port(page, "origin", request.origin, lock=ui_lock):
                return []
            if not await self._fs_fill_port(page, "destination", request.destination, lock=ui_lock):
                return []
            await self._fs_set_container_quantities(page, lock=ui_lock)

            try:
                async with ui_lock:
                    await page.locator('button:has-text("Get Quote")').first.click()
                print("[OOCL] [FS] Submitted Get Quote search.")
            except Exception as e:
                print(f"[OOCL] [FS] Could not click Get Quote: {e}")
                return []

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
            if watcher_task is not None:
                await watcher_task
                watcher_task = None
            await self._fs_dismiss_modals(page)  # final sweep for the gap right after stopping

            # Iterate through the 14-day calendar to collect all dated rows
            return await self._fs_iterate_calendar_dates(page)
        finally:
            if watcher_task is not None:
                stop_event.set()
                try:
                    await watcher_task
                except Exception:
                    pass
            try:
                await page.close()
            except Exception:
                pass

    @staticmethod
    def _fs_pair_and_select(fs_rows: List[dict], schedule_dicts: List[dict],
                            today: Optional[date] = None, window_days: int = 14,
                            espot_vessels: Optional[set] = None) -> List[dict]:
        """
        Applies the business rules and pairs FreightSmart prices with crawled schedules:
          - Only ETDs within `window_days` (2 weeks) are considered.
          - E-Spot rows: per ETD, only the CHEAPEST whole row is kept (they carry their
            own vessel/transit/free time/ETA). E-Spot does NOT pair with schedule details.
          - E-Quote rows: per ETD, only the CHEAPEST whole row is kept (row totals are
            compared; numbers are never mixed across rows).
          - If an E-Quote row's ETD matches a crawled schedule ETD, missing sailing details
            (vessel, ETA, transit, service, routing) are filled from that schedule.
            However, if the schedule's vessel is an E-Spot vessel (present in espot_vessels),
            we prevent the pairing and use the "OOCL Vessel/Performa" fallback.
          - Unmatched sailing schedules (those without any matching price quote) are dropped completely.
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

        # Cheapest complete E-Spot row per ETD (compare row totals; keep the row whole)
        best_espot_per_etd: dict = {}
        for r in espots:
            prices = r.get("prices") or {}
            row_total = sum(prices.values()) if prices else (r.get("total_price") or 0)
            if row_total <= 0:
                continue
            key = r.get("etd")
            if key not in best_espot_per_etd or row_total < best_espot_per_etd[key][0]:
                best_espot_per_etd[key] = (row_total, r)

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

        selected = [r for _, r in best_espot_per_etd.values()] + [r for _, r in best_equote_per_etd.values()]

        sched_by_etd: dict = {}
        for s in schedule_dicts:
            if s.get("etd") and s["etd"] not in sched_by_etd:
                sched_by_etd[s["etd"]] = s

        out: List[dict] = []
        matched_etds = set()
        for r in selected:
            is_equote = r.get("kind") != "E-Spot"
            sched = {}
            if is_equote and r.get("etd"):
                candidate_sched = sched_by_etd.get(r.get("etd")) or {}
                if candidate_sched:
                    sched_vessel = candidate_sched.get("vessel") or ""
                    cleaned_sched_vessel = clean_vessel_name(sched_vessel)
                    if espot_vessels and cleaned_sched_vessel in espot_vessels:
                        sched = {}
                    else:
                        sched = candidate_sched
                        matched_etds.add(r.get("etd"))

            base = {
                "etd": r.get("etd"),
                "eta": r.get("eta") or sched.get("eta"),
                "transit_time_days": r.get("transit_time_days") or sched.get("transit_time_days"),
                "vessel": r.get("vessel") or sched.get("vessel") or "OOCL Vessel/Performa",
                "service_name": sched.get("service_name") or r.get("kind"),
                "routing": sched.get("routing") or "Direct",
                "free_time": r.get("free_time"),
                "currency": r.get("currency", "USD"),
                "source": "carrier_portal",
                "container_quantity": 1,
                "validity_till": r.get("validity_end"),
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
          - FreightSmart-priced quotes carry a real container_type â†’ return only the
            ones matching this cycle's requested type.
          - Schedule-only quotes are untyped (container_type=None) â†’ serve a deep copy
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
                print("[OOCL] OOCL_QUERY_FREIGHTSMART=false â€” schedules-only mode.")

            # Step 3: Pair & select per business rules
            merged_dicts = self._fs_pair_and_select(
                fs_rows, schedule_dicts, espot_vessels=getattr(self, "espot_vessels", None)
            )

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

            # Nothing at all â€” cache the definitive no-quotes outcome; transient
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
