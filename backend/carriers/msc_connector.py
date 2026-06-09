import os
import re
import asyncio
from typing import Optional
from playwright.async_api import Page, TimeoutError, async_playwright

from carriers.base_connector import BaseCarrierConnector
from models.schemas import CarrierResultStatus, RateSearchRequest, QuoteSchema

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
        import sys
        
        # Thread-safe virtual display environment injection
        browser_env = os.environ.copy()
        if sys.platform != "win32":
            browser_env["DISPLAY"] = ":104"

        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=False, 
            args=["--start-maximized"],
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

            # Wait for dashboard to load (5-10 seconds)
            self.log("Waiting for dashboard to load...")
            # Verify login success by checking the URL
            await self.page.wait_for_url("**/welcome", timeout=20000)
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

            # 1. Equipment Size
            target_eq = ""
            if "20" in request.container_type:
                target_eq = "20DV"
            elif "40H" in request.container_type:
                target_eq = "40HC"
            elif "40" in request.container_type:
                target_eq = "40DV"
            else:
                target_eq = "20DV"

            self.log(f"Target equipment: {target_eq}")

            for eq_type in ["20DV", "40DV", "40HC"]:
                if eq_type != target_eq:
                    self.log(f"Unchecking {eq_type}...")
                    checkbox_wrapper = self.page.locator(f"label:has-text('{eq_type}')")
                    if await checkbox_wrapper.is_visible():
                        input_el = checkbox_wrapper.locator("input[type='checkbox']")
                        if await input_el.count() > 0:
                            if await input_el.first.is_checked():
                                await checkbox_wrapper.first.click()
                                await self.page.wait_for_timeout(500)
                        else:
                            await checkbox_wrapper.first.click()
                            await self.page.wait_for_timeout(500)

            # 2. Cargo Weight
            self.log(f"Setting cargo weight to {request.weight_per_container_kg}...")
            weight_input = self.page.locator("input[type='number']").first
            await weight_input.wait_for(state="visible")
            await weight_input.click()
            # To overwrite value, we can use fill
            await weight_input.fill(str(request.weight_per_container_kg))

            # 3. Origin and Destination
            self.log(f"Filling origin: {request.origin}")
            await self._fill_autocomplete("Select Start Point", request.origin)

            self.log(f"Filling destination: {request.destination}")
            await self._fill_autocomplete("Select End Point", request.destination)

            self.log("Clicking Search Rates button...")
            search_btn = self.page.locator("button:has-text('Search Rates')")
            await search_btn.wait_for(state="visible", timeout=10000)
            await search_btn.click()
            
            self.log("Waiting for results page to load...")
            await self.page.wait_for_timeout(15000)
            await self.save_screenshot("msc_results_debug.png", full_page=True)
            
            # Save HTML for debugging/extraction planning
            html_content = await self.page.content()
            with open("msc_results_debug.html", "w", encoding="utf-8") as f:
                f.write(html_content)
                
            return CarrierResultStatus.AVAILABLE_QUOTES_FOUND

        except Exception as e:
            self.log(f"Form filling failed: {e}")
            await self.save_screenshot("msc_form_fail.png")
            return CarrierResultStatus.INVALID_SEARCH_INPUT

    async def _fill_autocomplete(self, label_text: str, locode: str):
        try:
            # Try to find the text label, then go to its parent, then find the input inside
            # MSC uses custom combobox components
            label_element = self.page.locator(f"text='{label_text}'").first
            await label_element.wait_for(state="visible", timeout=5000)
            
            # Find the input relative to the label (either following sibling or inside parent)
            input_box = label_element.locator("xpath=..").locator("input").first
            await input_box.wait_for(state="visible", timeout=5000)
            await input_box.click()
            await input_box.fill(locode)
            
            self.log(f"Waiting for dropdown option containing [{locode}]...")
            await self.page.wait_for_timeout(2000)
            
            option = self.page.locator(f"li:has-text('{locode}'), div[role='option']:has-text('{locode}')").first
            if await option.is_visible():
                await option.click()
            else:
                self.log("Warning: Option containing LOCODE not visible, pressing Enter.")
                await input_box.press("Enter")
            
            await self.page.wait_for_timeout(1000)
        except Exception as e:
            self.log(f"Failed to fill autocomplete for {label_text}: {e}")
            raise

    async def run_full_search(self, request: RateSearchRequest) -> tuple[CarrierResultStatus, list[QuoteSchema]]:
        quotes: list[QuoteSchema] = []
        try:
            # 1. Login
            login_ok = await self.login()
            if not login_ok:
                return CarrierResultStatus.LOGIN_FAILED, []

            # 2. Search
            search_status = await self.search_quotes(request)
            if search_status != CarrierResultStatus.AVAILABLE_QUOTES_FOUND:
                return search_status, []

            # 3. Extract quotes by iterating over Shipping Windows
            self.log("Extracting quotes from shipping windows...")
            
            # Find all shipping window cards
            # The cards seem to contain text like "Shipping window"
            window_cards = self.page.locator("div:has-text('Shipping window')")
            # To avoid matching too broadly, let's find the specific clickable cards.
            # In MSC, these cards usually have a class or role. Let's find elements that contain "Shipping window" and a date range.
            window_locators = self.page.locator("div.card, div[role='button']").filter(has_text="Shipping window")
            
            count = await window_locators.count()
            if count == 0:
                # Try a broader locator
                window_locators = self.page.locator("text='Shipping window'").locator("xpath=../..")
                count = await window_locators.count()

            self.log(f"Found {count} shipping windows.")
            if count == 0:
                return CarrierResultStatus.NO_QUOTES_AVAILABLE, []

            for i in range(count):
                window = window_locators.nth(i)
                self.log(f"Processing shipping window {i+1}/{count}...")
                await window.click()
                await self.page.wait_for_timeout(2000) # Wait for lower section to update

                # 1. Get Free Time
                free_time_text = ""
                try:
                    free_time_el = self.page.locator("text='Import Combined :'").first
                    if await free_time_el.is_visible():
                        free_time_text = await free_time_el.inner_text()
                except:
                    pass
                
                # Default 0, parse if found (e.g. "Import Combined : 7 Calendar days")
                free_time = 0
                match = re.search(r"Import Combined\s*:\s*(\d+)", free_time_text, re.IGNORECASE)
                if match:
                    free_time = int(match.group(1))

                # 2. Open details popup
                show_details_btn = self.page.locator("text='show details'").first
                if not await show_details_btn.is_visible():
                    self.log("Could not find 'show details' button, skipping window.")
                    continue
                await show_details_btn.click()
                await self.page.wait_for_timeout(2000)

                # 3. Extract Charges (Tab 1)
                self.log("Extracting charges...")
                charges = []
                total_freight = 0.0
                currency = "USD"
                
                # Broad modal locator
                modal = self.page.locator("div[role='dialog'], .MuiDialog-container, .modal, [class*='modal' i]").filter(has=self.page.locator("table")).first
                if await modal.count() == 0:
                    modal = self.page.locator("table").locator("xpath=../../..").first
                
                rows = modal.locator("tr")
                row_count = await rows.count()
                self.log(f"Found {row_count} rows in charges table.")
                
                
                current_group = ""
                for r in range(row_count):
                    row_text = await rows.nth(r).inner_text()
                    # Determine group
                    if "Freight Charge" in row_text and "Surcharges" not in row_text:
                        current_group = "Freight Charge"
                    elif "Freight Surcharges" in row_text:
                        current_group = "Freight Surcharges"
                    elif "Export Surcharges" in row_text or "Import Surcharges" in row_text:
                        current_group = "Other"

                    # Parse amount: "15 USD", "2500 USD"
                    amt_match = re.search(r"(\d+(?:[.,]\d+)?)\s*([A-Z]{3})", row_text)
                    if amt_match:
                        val = float(amt_match.group(1).replace(",", ""))
                        curr = amt_match.group(2)
                        
                        charge_name = row_text.split('\n')[0].strip() if '\n' in row_text else row_text.split('  ')[0].strip()
                        
                        charge_obj = {
                            "name": charge_name,
                            "amount": val,
                            "currency": curr,
                            "category": "included" if current_group in ["Freight Charge", "Freight Surcharges"] else "excluded"
                        }
                        
                        # We extract all charges but sum up freight specifically
                        if current_group in ["Freight Charge", "Freight Surcharges"]:
                            total_freight += val
                            currency = curr
                        
                        charges.append(charge_obj)

                # 4. Extract Routing (Tab 2)
                self.log("Extracting routing...")
                quote_conditions_tab = modal.locator("text='Quote Conditions'").first
                await quote_conditions_tab.click()
                await self.page.wait_for_timeout(1000)
                
                routing_el = modal.locator("text='Routing:'").locator("xpath=..")
                routing_text = ""
                if await routing_el.count() > 0:
                    routing_text = await routing_el.first.inner_text()
                
                is_direct = "Direct" in routing_text

                # 5. Extract Schedules (Tab 3)
                self.log("Extracting schedules...")
                schedule_tab = modal.locator("text='Schedule'").first
                await schedule_tab.click()
                await self.page.wait_for_timeout(1000)

                # The schedule table has rows with Vessel, Voyage, ETD, ETA, Service, Est.TT.
                # Let's find rows that contain "Days" for Transit Time
                sched_rows = modal.locator("tr")
                s_count = await sched_rows.count()
                self.log(f"Found {s_count} rows in schedule table.")
                
                for s in range(s_count):
                    s_text = await sched_rows.nth(s).inner_text()
                    if "Days" not in s_text and "days" not in s_text.lower():
                        continue
                    parts = [p.strip() for p in s_text.split('\t') if p.strip()]
                    if len(parts) < 5:
                        parts = [p.strip() for p in s_text.split('\n') if p.strip()]
                        
                    # Usually: [Vessel Name, Voyage, ETD, ETA, Service, TT]
                    # We can use regex to find dates and TT
                    tt_match = re.search(r"(\d+)\s*Days", s_text, re.IGNORECASE)
                    tt_days = int(tt_match.group(1)) if tt_match else 0
                    
                    # Find dates (e.g., "14 Jun 2026")
                    dates = re.findall(r"\d{1,2}\s+[A-Za-z]{3}\s+\d{4}", s_text)
                    etd = dates[0] if len(dates) > 0 else ""
                    eta = dates[1] if len(dates) > 1 else ""
                    
                    # Vessel name is usually at the start, Service name near the end
                    # We can just capture the first text before Voyage
                    vessel = parts[0] if parts else "MSC Vessel"
                    service_name = parts[-3] if len(parts) > 3 else "MSC Service"

                    # Create Quote Schema for this vessel
                    from models.schemas import ChargeSchema
                    quote = QuoteSchema(
                        service_name=service_name,
                        routing="Direct" if is_direct else "Transshipment",
                        transit_time_days=tt_days,
                        etd=self._parse_date(etd) if etd else None,
                        eta=self._parse_date(eta) if eta else None,
                        vessel=vessel,
                        free_time=free_time,
                        currency=currency,
                        basic_ocean_freight=total_freight,
                        final_freight_value=total_freight,
                        included_freight_surcharges=[ChargeSchema(**c) for c in charges if c.get("category") == "included"],
                        excluded_charges=[ChargeSchema(**c) for c in charges if c.get("category") == "excluded"]
                    )
                    quotes.append(quote)

                # Close popup
                self.log("Closing popup...")
                try:
                    # Usually the close button is an SVG or button at the top right
                    close_btn = modal.locator("button, svg").first
                    await close_btn.click(timeout=5000)
                except Exception as e:
                    self.log(f"Failed to click close button normally: {e}")
                    await self.page.evaluate('''() => {
                        const dialogs = document.querySelectorAll('[role="dialog"], .MuiDialog-root, .modal');
                        dialogs.forEach(d => d.style.display = 'none');
                        const backdrops = document.querySelectorAll('.MuiBackdrop-root');
                        backdrops.forEach(b => b.style.display = 'none');
                    }''')
                await self.page.wait_for_timeout(1000)

            if quotes:
                return CarrierResultStatus.AVAILABLE_QUOTES_FOUND, quotes
            return CarrierResultStatus.NO_QUOTES_AVAILABLE, []

        except Exception as e:
            self.log(f"Unexpected error in run_full_search: {e}")
            await self.save_screenshot("msc_error_fallback.png", full_page=True)
            return CarrierResultStatus.UNKNOWN_ERROR, []
        finally:
            await self.close()

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
