import os
import re
import asyncio
from typing import Optional
from playwright.async_api import Page, TimeoutError, async_playwright

from carriers.base_connector import BaseCarrierConnector
from models.schemas import CarrierResultStatus, RateSearchRequest, QuoteSchema
from services.port_manager import resolve_port_for_carrier
from services.normalizer import standardize_date_string

def resolve_msc_port(text: str) -> tuple[str, str]:
    """
    Resolves input text (e.g. 'Belfast (GBBEL)' or 'GBBEL') to a tuple of (query_text, locode).
    query_text is what we type in the search input box.
    locode is the 5-letter code we match in the dropdown options.
    """
    if not text:
        return "", ""
        
    text_lower = text.lower().strip()
    
    # 0. Rotterdam override
    if "rotterdam" in text_lower or text_lower == "nlrtm":
        return "Rotterdam", "NLRTM"
        
    # 1. Extract LOCODE from input text
    extracted_locode = None
    paren_match = re.search(r'\(\s*([A-Za-z]{2})\s*([A-Za-z]{3})\s*\)', text)
    if paren_match:
        extracted_locode = (paren_match.group(1) + paren_match.group(2)).upper()
    else:
        word_match = re.search(r'\b([A-Za-z]{2})\s*([A-Za-z]{3})\b', text)
        if word_match:
            candidate = (word_match.group(1) + word_match.group(2)).upper()
            from services.port_manager import PortManager
            if candidate in PortManager()._ports:
                extracted_locode = candidate
    if not extracted_locode:
        clean_word = text.strip()
        if len(clean_word) == 5 and clean_word.isalpha():
            candidate = clean_word.upper()
            from services.port_manager import PortManager
            if candidate in PortManager()._ports:
                extracted_locode = candidate
                
    # 2. If not found, use search_port fallback
    if not extracted_locode:
        from services.port_manager import search_port
        results = search_port(text)
        if results:
            extracted_locode = results[0]['code'].upper()
            
    # 3. Determine query_text (port name)
    query_text = ""
    if extracted_locode:
        from services.port_manager import PortManager, CARRIER_PORT_OVERRIDES
        # Check overrides
        overrides = CARRIER_PORT_OVERRIDES.get("msc", {})
        if extracted_locode in overrides:
            query_text = overrides[extracted_locode]
        else:
            port_data = PortManager().get_port_by_code(extracted_locode)
            if port_data:
                # Clean name: remove parentheses
                name = port_data.get("name", "")
                query_text = re.sub(r'\s*\([^)]*\)', '', name).strip()
                
    if not query_text:
        # Fallback to cleaning the input text
        query_text = re.sub(r'\s*\([^)]*\)', '', text).strip()
        
    if not extracted_locode:
        extracted_locode = ""
        
    return query_text, extracted_locode

class MSCConnector(BaseCarrierConnector):
    """
    Playwright-based automation for MSC (Mediterranean Shipping Company).
    """
    carrier_code = "MSC"
    carrier_name = "MSC"

    def __init__(self):
        super().__init__()
        self.playwright = None

    def log(self, msg: str):
        print(f"[MSC] {msg}")

    async def save_screenshot(self, filename: str, full_page: bool = False):
        if self.page:
            try:
                await self.page.screenshot(path=filename, full_page=full_page)
                self.log(f"Screenshot saved to {filename}")
            except Exception as e:
                self.log(f"Failed to save screenshot: {e}")

    async def login(self) -> bool:
        """Handles the MSC login flow."""
        self.log("Initializing browser...")
        self.playwright = await async_playwright().start()

        # Thread-safe virtual display environment injection
        browser_env = os.environ.copy()
        if os.name != "nt":
            browser_env["DISPLAY"] = ":104"

        self.browser = await self.playwright.chromium.launch(
            headless=False,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding",
                "--start-maximized",
            ],
            env=browser_env
        )
        self.context = await self.browser.new_context(viewport={'width': 1920, 'height': 1080})
        self.page = await self.context.new_page()

        username = os.getenv("MSC_USERNAME")
        password = os.getenv("MSC_PASSWORD")
        if not username or not password:
            self.log("Missing MSC credentials.")
            return False

        self.log("Navigating to MSC login page...")
        try:
            await self.page.goto("https://www.mymsc.com/myMSC/", timeout=60000, wait_until="domcontentloaded")
            await self.page.wait_for_timeout(3000)

            # Accept cookies if the banner appears
            try:
                cookie_btn = self.page.locator("button#onetrust-accept-btn-handler")
                if await cookie_btn.is_visible():
                    self.log("Accepting cookies...")
                    await cookie_btn.click()
            except Exception:
                pass

            # Fill email
            self.log("Filling email...")
            email_input = self.page.locator("input[type='email'], input[name='email'], input[placeholder*='Email']")
            await email_input.wait_for(state="visible", timeout=15000)
            await email_input.fill(username)

            # Click Next
            self.log("Clicking Next...")
            next_btn = self.page.locator("button:has-text('Next')")
            await next_btn.click()

            # Wait for password field
            self.log("Waiting for password field...")
            password_input = self.page.locator("input[type='password'], input[name='password']")
            await password_input.wait_for(state="visible", timeout=15000)
            await password_input.fill(password)

            # Click Login
            self.log("Clicking Login...")
            login_btn = self.page.locator("button:has-text('Login'), button:has-text('Sign in')")
            await login_btn.click()

            # Wait for dashboard to load (up to 45 seconds)
            self.log("Waiting for dashboard to load...")
            # Verify login success by checking the URL
            await self.page.wait_for_url("**/welcome", timeout=45000)
            self.log("Login successful.")
            return True

        except Exception as e:
            self.log(f"Login failed: {e}")
            await self.save_screenshot("msc_login_fail.png")
            return False

    async def search_quotes(self, request: RateSearchRequest) -> CarrierResultStatus:
        """Clicks Instant Quote, fills form, clicks Search."""
        try:
            self.log("Navigating directly to Instant Quote page...")
            await self.page.goto("https://www.mymsc.com/myMSC/instantquote")
            
            await self.page.locator("text='Equipment Type'").first.wait_for(state="visible", timeout=20000)
            await self.page.wait_for_timeout(2000)

            # 1. Equipment Size (leave default 20DV, 40DV, 40HC checked to search all simultaneously)
            self.log("Leaving all equipment sizes checked (20DV, 40DV, 40HC)")

            # 2. Cargo Weight
            self.log(f"Setting cargo weight to {request.weight_per_container_kg}...")
            weight_input = self.page.locator("input[type='number']").first
            await weight_input.wait_for(state="visible")
            await weight_input.click()
            # To overwrite value, we can use fill
            await weight_input.fill(str(request.weight_per_container_kg))

            # 3. Origin and Destination
            origin_query, origin_locode = resolve_msc_port(request.origin)
            self.log(f"Filling origin: query='{origin_query}', locode='{origin_locode}' (input: '{request.origin}')")
            await self._fill_autocomplete("Select Start Point", origin_query, origin_locode)

            dest_query, dest_locode = resolve_msc_port(request.destination)
            self.log(f"Filling destination: query='{dest_query}', locode='{dest_locode}' (input: '{request.destination}')")
            await self._fill_autocomplete("Select End Point", dest_query, dest_locode)

            self.log("Clicking Search Rates button...")
            search_btn = self.page.locator("button:has-text('Search Rates')")
            await search_btn.wait_for(state="visible", timeout=10000)
            await search_btn.click()
            
            self.log("Waiting for results page to load...")
            # Wait dynamically up to 45 seconds for shipping window cards to render.
            # Use a specific text selector that MSC renders ONLY on the results page.
            windows_loaded = False
            consecutive_timeouts = 0
            for tick in range(45):
                # --- Deadlock watchdog: check if page is frozen (after 10s grace period) ---
                if tick >= 10:
                    try:
                        await self.page.evaluate("1", timeout=5000)
                        consecutive_timeouts = 0
                    except TimeoutError:
                        consecutive_timeouts += 1
                        self.log(f"WARNING: Page evaluation timed out (attempt {consecutive_timeouts}/2).")
                        if consecutive_timeouts >= 2:
                            self.log("WARNING: Page appears frozen/deadlocked during results wait. Aborting.")
                            await self.save_screenshot("msc_results_fail.png", full_page=True)
                            return CarrierResultStatus.NO_QUOTES_AVAILABLE
                    except Exception as eval_err:
                        # Ignore other transient errors (context destroyed, navigation, etc.)
                        consecutive_timeouts = 0

                # Check for specific MSC shipping-window result text
                try:
                    # MSC results page always renders "Shipping window" inside result cards
                    sw_count = await self.page.locator("text='Shipping window'").count()
                    if sw_count > 0:
                        windows_loaded = True
                        self.log(f"Shipping window cards detected after {tick + 1}s.")
                        break
                except Exception:
                    pass

                # Early bail: explicit no-results text
                try:
                    body_text = (await self.page.inner_text("body", timeout=500)).lower()
                    if any(kw in body_text for kw in ["no departures", "no rates available", "no sailings", "no routes found"]):
                        self.log("Explicit 'No rates' indicator detected early.")
                        return CarrierResultStatus.NO_QUOTES_AVAILABLE
                except Exception:
                    pass

                await asyncio.sleep(1)
            
            if not windows_loaded:
                self.log("Timeout waiting for shipping window cards to load. Checking page fallback text...")
                await self.save_screenshot("msc_results_fail.png", full_page=True)
                try:
                    body_text = (await self.page.inner_text("body")).lower()
                    if any(kw in body_text for kw in ["no departures", "no rates", "no quotes", "no sailings", "no routes found", "no matching"]):
                        self.log("Explicit 'No rates' or 'No departures' indicator detected.")
                        return CarrierResultStatus.NO_QUOTES_AVAILABLE
                except Exception:
                    pass
                return CarrierResultStatus.NO_QUOTES_AVAILABLE

            # Save HTML for debugging/extraction planning
            html_content = await self.page.content()
            with open("msc_results_debug.html", "w", encoding="utf-8") as f:
                f.write(html_content)
                
            return CarrierResultStatus.AVAILABLE_QUOTES_FOUND

        except Exception as e:
            self.log(f"Form filling failed: {e}")
            await self.save_screenshot("msc_form_fail.png")
            return CarrierResultStatus.INVALID_SEARCH_INPUT

    async def _fill_autocomplete(self, label_text: str, query_text: str, locode: str):
        try:
            # Try to find the text label, then go to its parent, then find the input inside
            # MSC uses custom combobox components
            label_element = self.page.locator(f"text='{label_text}'").first
            await label_element.wait_for(state="visible", timeout=5000)
            
            # Find the input relative to the label (either following sibling or inside parent)
            input_box = label_element.locator("xpath=..").locator("input").first
            await input_box.wait_for(state="visible", timeout=5000)
            await input_box.click()
            await input_box.fill("")
            await input_box.fill(query_text)
            
            self.log(f"Waiting for dropdown option containing [{locode}] for query '{query_text}'...")
            await self.page.wait_for_timeout(2000)
            
            import re as _re

            # 1. Try to find the option matching the LOCODE (e.g. matching GBBEL or NLRTM in the text)
            matching_option = None
            options = self.page.locator("li, div[role='option']")
            count = await options.count()
            self.log(f"Found {count} dropdown options.")
            
            for i in range(count):
                opt = options.nth(i)
                text = await opt.inner_text()
                if text:
                    text_lower = text.lower()
                    if locode and locode.lower() in text_lower:
                        matching_option = opt
                        self.log(f"Matched option by LOCODE '{locode}': '{text.strip()}'")
                        break
            
            if matching_option:
                await matching_option.click()
            else:
                # Fallback: standard word boundary / substring matching using query_text / locode
                exact_option = None
                fallback_option = None
                if locode:
                    exact_option = self.page.locator("li, div[role='option']").filter(
                        has_text=_re.compile(rf"\b{_re.escape(locode)}\b", _re.IGNORECASE)
                    ).first
                    fallback_option = self.page.locator(
                        f"li:has-text('{locode}'), div[role='option']:has-text('{locode}')"
                    ).first
                
                if exact_option and await exact_option.is_visible():
                    self.log(f"Found exact word match for '{locode}'. Clicking it.")
                    await exact_option.click()
                elif fallback_option and await fallback_option.is_visible():
                    self.log(f"Found substring match for '{locode}'. Clicking it.")
                    await fallback_option.click()
                else:
                    # Fallback to query_text
                    query_exact = self.page.locator("li, div[role='option']").filter(
                        has_text=_re.compile(rf"\b{_re.escape(query_text)}\b", _re.IGNORECASE)
                    ).first
                    if await query_exact.is_visible():
                        self.log(f"Found exact word match for query_text '{query_text}'. Clicking it.")
                        await query_exact.click()
                    else:
                        self.log("Warning: Option matching LOCODE/query not found in loop/filters, pressing Enter.")
                        await input_box.press("Enter")
            
            await self.page.wait_for_timeout(2000)
        except Exception as e:
            self.log(f"Failed to fill autocomplete for {label_text}: {e}")
            raise

    async def run_full_search(self, request: RateSearchRequest) -> tuple[CarrierResultStatus, list[QuoteSchema]]:
        if not hasattr(self, "_cached_quotes"):
            self._cached_quotes = None
            self._cached_status = None

        if self._cached_quotes is not None:
            self.log(f"Returning cached quotes for '{request.container_type}' (avoiding redundant browser search).")
            matching_quotes = [q for q in self._cached_quotes if q.container_type == request.container_type]
            return self._cached_status, matching_quotes

        quotes: list[QuoteSchema] = []
        try:
            # 1. Login
            login_ok = await self.login()
            if not login_ok:
                self._cached_quotes = []
                self._cached_status = CarrierResultStatus.LOGIN_FAILED
                return CarrierResultStatus.LOGIN_FAILED, []

            # 2. Search
            search_status = await self.search_quotes(request)
            if search_status != CarrierResultStatus.AVAILABLE_QUOTES_FOUND:
                self._cached_quotes = []
                self._cached_status = search_status
                return search_status, []

            # 3. Extract quotes by iterating over Shipping Windows
            self.log("Extracting quotes from shipping windows...")
            
            # Find all shipping window cards
            window_locators = self.page.locator("div.card, div[role='button']").filter(has_text="Shipping window")
            
            count = await window_locators.count()
            if count == 0:
                # Try a broader locator
                window_locators = self.page.locator("text='Shipping window'").locator("xpath=../..")
                count = await window_locators.count()

            self.log(f"Found {count} shipping windows.")
            if count == 0:
                self._cached_quotes = []
                self._cached_status = CarrierResultStatus.NO_QUOTES_AVAILABLE
                return CarrierResultStatus.NO_QUOTES_AVAILABLE, []

            for i in range(count):
                window = window_locators.nth(i)
                self.log(f"Processing shipping window {i+1}/{count}...")
                # Snapshot page content before clicking to detect update
                text_before = await self.page.locator("body").inner_text()
                await window.click()
                # Wait dynamically for at least one "show details" button to be visible (up to 5s)
                for _ in range(25):
                    try:
                        if await self.page.locator("text='show details'").locator("visible=true").count() > 0:
                            break
                    except Exception:
                        pass
                    await self.page.wait_for_timeout(200)

                show_details_locators = self.page.locator("text='show details'")
                detail_btn_count = await show_details_locators.count()
                self.log(f"Found {detail_btn_count} total 'show details' buttons in DOM")

                for j in range(detail_btn_count):
                    btn = show_details_locators.nth(j)
                    if not await btn.is_visible():
                        continue
                    
                    # Walk up to find the card container text to determine the container type
                    card_text = ""
                    parent = btn
                    for _ in range(6):
                        try:
                            parent = parent.locator("xpath=..")
                            parent_text = await parent.inner_text()
                            if any(kw in parent_text for kw in ["20' Dry Van", "40' Dry Van", "40' High Cube", "20DV", "40DV", "40HC"]):
                                card_text = parent_text
                                break
                        except Exception:
                            break
                            
                    container_type = "DRY 20"
                    if "40' High Cube" in card_text or "40HC" in card_text:
                        container_type = "DRY 40H"
                    elif "40' Dry Van" in card_text or "40DV" in card_text:
                        container_type = "DRY 40"
                    elif "20' Dry Van" in card_text or "20DV" in card_text:
                        container_type = "DRY 20"
                    else:
                        container_type = request.container_type
                        
                    self.log(f"Processing quote card {j+1}/{detail_btn_count} - container type: {container_type}")

                    # Open details popup
                    await btn.scroll_into_view_if_needed()
                    await btn.click()
                    
                    # Wait dynamically for modal to appear (up to 5s)
                    modal_visible = False
                    for _ in range(25):
                        await self.page.wait_for_timeout(200)
                        try:
                            if await self.page.locator("div[data-test-id='BreakdownModal']").is_visible():
                                modal_visible = True
                                break
                        except Exception:
                            break
                            
                    if not modal_visible:
                        self.log(f"Modal did not open for card {j+1}, skipping.")
                        continue

                    # 1. Initialize Free Time
                    free_time = 0

                    # 2. Extract Charges (Tab 1)
                    self.log("Extracting charges...")
                    charges = []
                    total_freight = 0.0
                    bof_value = 0.0
                    currency = "USD"
                    
                    # Re-resolve modal fresh for EACH card to avoid stale/hidden element hangs
                    modal = self.page.locator("div[data-test-id='BreakdownModal']")
                    try:
                        await modal.wait_for(state="visible", timeout=10000)
                    except Exception as e:
                        self.log(f"Modal did not become visible for card {j+1}: {e}")
                        continue
                    
                    # Wait for the charges to actually render inside the modal before reading inner_text
                    try:
                        await modal.locator("*:has-text('Freight Charge'), *:has-text('Per Equipment')").first.wait_for(state="visible", timeout=15000)
                    except Exception as e:
                        self.log(f"Timed out waiting for charges to render inside modal: {e}")
                    
                    popup_text = (await modal.inner_text(timeout=15000)).replace('\n', ' ').upper()
                    self.log(f"Popup text length: {len(popup_text)}")
                    
                    def extract_section(txt, current_header, next_headers):
                        start = txt.find(current_header)
                        if start == -1: return ""
                        end_indices = [txt.find(h) for h in next_headers if txt.find(h) > start]
                        end = min(end_indices) if end_indices else len(txt)
                        return txt[start:end]

                    sections = {
                        "FREIGHT CHARGE": ["FREIGHT SURCHARGES", "EXPORT SURCHARGES", "IMPORT SURCHARGES"],
                        "FREIGHT SURCHARGES": ["EXPORT SURCHARGES", "IMPORT SURCHARGES"],
                        "EXPORT SURCHARGES": ["IMPORT SURCHARGES"],
                        "IMPORT SURCHARGES": ["TOTAL", "SUBJECT TO CHARGES"]
                    }
                    
                    for section_name, next_headers in sections.items():
                        section_text = extract_section(popup_text, section_name, next_headers)
                        if not section_text: continue
                        
                        pattern = r"(.*?)(?:PER EQUIPMENT|PER BILL OF LADING)\s+([\d,]+(?:\.\d+)?)\s*([A-Z]{3})\s+(?:PREPAID|COLLECT)"
                        
                        for match in re.finditer(pattern, section_text, re.DOTALL):
                            raw_name = match.group(1).strip()
                            clean_name = re.sub(r"^(?:,\s*ELSEWHERE|,\s*COLLECT|,\s*PREPAID|COLLECT|PREPAID)+", "", raw_name).strip()
                            clean_name = re.sub(r"^(?:FREIGHT CHARGE|FREIGHT SURCHARGES|EXPORT SURCHARGES|IMPORT SURCHARGES)", "", clean_name).strip()
                            clean_name = re.sub(r"^(?:TERMS OF PAYMENT ONLY\.?)", "", clean_name).strip(" ,.")
                            
                            if not clean_name: continue
                            
                            val = float(match.group(2).replace(",", ""))
                            curr = match.group(3)
                            
                            charge_obj = {
                                "name": clean_name.title(),
                                "amount": val,
                                "currency": curr,
                                "category": "bof" if section_name == "FREIGHT CHARGE" else ("included" if section_name == "FREIGHT SURCHARGES" else "excluded")
                            }
                            
                            if section_name == "FREIGHT CHARGE":
                                bof_value += val
                                total_freight += val
                                currency = curr
                            elif section_name == "FREIGHT SURCHARGES":
                                total_freight += val
                                currency = curr
                            
                            charges.append(charge_obj)
                            
                    # 3. Extract Free Time
                    self.log("Extracting free time...")
                    try:
                        free_time_tab = modal.locator("text='Free Time'").first
                        if await free_time_tab.is_visible():
                            text_before_ft = await modal.inner_text(timeout=10000)
                            await free_time_tab.click()
                            for _ in range(15):
                                await self.page.wait_for_timeout(200)
                                try:
                                    if await modal.inner_text(timeout=5000) != text_before_ft:
                                        break
                                except Exception:
                                    break
                            
                            free_time_el = modal.locator("*:has-text('Import Combined')").last
                            await free_time_el.wait_for(state="visible", timeout=5000)
                            popup_inner = await modal.inner_text(timeout=10000)
                            
                            match = re.search(r"Import Combined.*?(\d+)\s*Calendar", popup_inner, re.IGNORECASE | re.DOTALL)
                            if match:
                                free_time = int(match.group(1))
                    except Exception as e:
                        self.log(f"Failed to find Free Time text in popup: {e}")

                    # 4. Extract Routing (Tab 2)
                    self.log("Extracting routing...")
                    quote_conditions_tab = modal.locator("text='Quote Conditions'").first
                    try:
                        text_before_qc = await modal.inner_text(timeout=10000)
                    except Exception as e:
                        self.log(f"Failed to read modal text before Quote Conditions tab: {e}")
                        text_before_qc = ""
                    await quote_conditions_tab.click()
                    for _ in range(10):
                        await self.page.wait_for_timeout(200)
                        try:
                            if await modal.inner_text(timeout=5000) != text_before_qc:
                                break
                        except Exception:
                            break
                    
                    routing_el = modal.locator("text='Routing:'").locator("xpath=..")
                    routing_text = ""
                    if await routing_el.count() > 0:
                        routing_text = await routing_el.first.inner_text()
                    
                    if not routing_text or "Routing:" not in routing_text:
                        routing_text = await modal.inner_text()
                    
                    is_direct = "Direct" in routing_text
                    routing_val = "Direct"
                    if not is_direct:
                        routing_section = ""
                        r_idx = routing_text.find("Routing:")
                        if r_idx != -1:
                            routing_section = routing_text[r_idx:]
                            end_keywords = ["INCLUSIVE OF", "QUOTE VALIDITY", "PAYMENT TERMS", "TRANSIT TIME", "CHARGES AND CONDITIONS"]
                            end_idx = len(routing_section)
                            for kw in end_keywords:
                                kw_idx = routing_section.upper().find(kw)
                                if kw_idx != -1 and kw_idx < end_idx:
                                    end_idx = kw_idx
                            routing_section = routing_section[:end_idx]
                        else:
                            routing_section = routing_text

                        via_match = re.search(r"Via\s*:\s*([^(\n\r]+)", routing_section, re.IGNORECASE)
                        if via_match:
                            via_port = via_match.group(1).strip()
                            routing_val = f"Transit via {via_port}"
                        else:
                            routing_val = "Transshipment"

                    # 5. Extract Schedules (Tab 3)
                    self.log("Extracting schedules...")
                    schedule_tab = modal.locator("text='Schedule'").first
                    try:
                        text_before_sched = await modal.inner_text(timeout=8000)
                    except Exception:
                        text_before_sched = ""

                    await schedule_tab.click()

                    content_changed = False
                    for _ in range(30):
                        await self.page.wait_for_timeout(200)
                        try:
                            current_text = await modal.inner_text(timeout=3000)
                            if current_text != text_before_sched:
                                content_changed = True
                                break
                        except Exception:
                            break

                    if not content_changed:
                        self.log("Warning: modal content did not change after clicking Schedule tab.")

                    sched_rows = modal.locator("tr:has-text('Days')")
                    try:
                        await sched_rows.first.wait_for(state="visible", timeout=15000)
                        self.log("Schedule rows visible.")
                    except Exception as e:
                        self.log(f"Timed out waiting for schedule rows: {e}")

                    s_count = await sched_rows.count()
                    self.log(f"Schedule rows found: {s_count}")
                    
                    for s in range(s_count):
                        s_text = await sched_rows.nth(s).inner_text()
                        parts = [p.strip() for p in s_text.split('\t') if p.strip()]
                        if len(parts) < 5:
                            parts = [p.strip() for p in s_text.split('\n') if p.strip()]
                            
                        tt_match = re.search(r"(\d+)\s*Days", s_text, re.IGNORECASE)
                        tt_days = int(tt_match.group(1)) if tt_match else 0
                        
                        dates = re.findall(r"\d{1,2}\s+[A-Za-z]{3}\s+\d{4}", s_text)
                        etd = dates[0] if len(dates) > 0 else ""
                        eta = dates[1] if len(dates) > 1 else ""
                        
                        vessel = parts[0] if parts else "MSC Vessel"
                        service_name = parts[-3] if len(parts) > 3 else "MSC Service"

                        from models.schemas import ChargeSchema
                        quote = QuoteSchema(
                            service_name=service_name,
                            routing=routing_val,
                            transit_time_days=tt_days,
                            etd=standardize_date_string(etd) if etd else None,
                            eta=standardize_date_string(eta) if eta else None,
                            vessel=vessel,
                            free_time=free_time,
                            currency=currency,
                            container_type=container_type,
                            basic_ocean_freight=bof_value,
                            final_freight_value=total_freight,
                            included_freight_surcharges=[ChargeSchema(**c) for c in charges if c.get("category") == "included"],
                            excluded_charges=[ChargeSchema(**c) for c in charges if c.get("category") == "excluded"]
                        )
                        quotes.append(quote)

                    # Close popup and wait for it to be fully gone before next iteration
                    self.log("Closing popup...")
                    try:
                        close_btn = modal.locator("button, svg").first
                        await close_btn.click(timeout=5000)
                    except Exception as e:
                        self.log(f"Failed to click close button normally: {e}")
                        await self.page.evaluate('''() => {
                            const modal = document.querySelector('[data-test-id="BreakdownModal"]');
                            if (modal) {
                                modal.style.display = 'none';
                            }
                            const backdrops = document.querySelectorAll('.MuiBackdrop-root');
                            backdrops.forEach(b => b.style.display = 'none');
                        }''')
                    try:
                        await modal.wait_for(state="hidden", timeout=5000)
                    except Exception:
                        pass
                    await self.page.wait_for_timeout(500)

            if quotes:
                self._cached_quotes = quotes
                self._cached_status = CarrierResultStatus.AVAILABLE_QUOTES_FOUND
                matching_quotes = [q for q in quotes if q.container_type == request.container_type]
                return CarrierResultStatus.AVAILABLE_QUOTES_FOUND, matching_quotes
            
            self._cached_quotes = []
            self._cached_status = CarrierResultStatus.NO_QUOTES_AVAILABLE
            return CarrierResultStatus.NO_QUOTES_AVAILABLE, []

        except Exception as e:
            self.log(f"Unexpected error in run_full_search: {e}")
            await self.save_screenshot("msc_error_fallback.png", full_page=True)
            self._cached_quotes = []
            self._cached_status = CarrierResultStatus.UNKNOWN_ERROR
            return CarrierResultStatus.UNKNOWN_ERROR, []
        finally:
            await asyncio.shield(self.close())

    def _parse_date(self, date_str: str) -> str:
        """Parse '14 Jun 2026' to 'YYYY-MM-DD'"""
        from datetime import datetime
        try:
            dt = datetime.strptime(date_str, "%d %b %Y")
            return dt.strftime("%Y-%m-%d")
        except:
            return date_str

    # Provide empty implementations for the abstract methods to satisfy BaseCarrierConnector
    async def extract_quote_list(self) -> list[dict]:
        return []
    async def open_price_breakdown(self, quote_ref: dict) -> bool:
        return False
    async def extract_charge_breakdown(self) -> list[dict]:
        return []
    async def normalize_result(self, raw_quote: dict, raw_charges: list[dict]) -> QuoteSchema:
        return QuoteSchema()
