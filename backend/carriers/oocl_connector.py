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

    async def _select_location(self, label: str, field_selector: str, location_name: str) -> bool:
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
                
            for i in range(count):
                opt = options.nth(i)
                text = await opt.inner_text()
                if text and location_name.lower() in text.lower():
                    await opt.scroll_into_view_if_needed()
                    await opt.click()
                    print(f"[OOCL] Selected {label} from dropdown: {text.strip()}")
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
            
            if request.origin and ("rotterdam" in request.origin.lower() or request.origin.strip().upper() == "NLRTM"):
                resolved_origin = "NLRTM"
            else:
                resolved_origin = resolve_port_for_carrier(request.origin, "oocl")
                if not resolved_origin:
                    resolved_origin = request.origin
            origin_success = await self._select_location("Origin", origin_field, resolved_origin)
            if not origin_success:
                return CarrierResultStatus.INVALID_SEARCH_INPUT
                
            if request.destination and ("rotterdam" in request.destination.lower() or request.destination.strip().upper() == "NLRTM"):
                resolved_dest = "NLRTM"
            else:
                resolved_dest = resolve_port_for_carrier(request.destination, "oocl")
                if not resolved_dest:
                    resolved_dest = request.destination
            dest_success = await self._select_location("Destination", dest_field, resolved_dest)
            if not dest_success:
                return CarrierResultStatus.INVALID_SEARCH_INPUT
                
            if "REEFER" in request.container_type.upper():
                try:
                    await self.page.locator('label:has-text("Reefer"), input[value="Reefer"]').first.click()
                except Exception:
                    pass
                    
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
