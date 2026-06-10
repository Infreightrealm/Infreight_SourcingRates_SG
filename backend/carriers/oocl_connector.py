"""
OOCL Live Connector — Playwright automation for Sailing Schedules.
"""
import os
import re
import asyncio
from datetime import datetime, date, timedelta
from typing import Optional
from playwright.async_api import async_playwright
from models.schemas import RateSearchRequest, QuoteSchema, CarrierResultStatus, ChargeSchema
from carriers.base_connector import BaseCarrierConnector

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
            browser_env["DISPLAY"] = ":101"

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
            await self.page.wait_for_timeout(2000)
            
            dropdown_sel = 'ul[role="listbox"] li, .ui-autocomplete-items li, .dropdown-menu li, .cdk-overlay-container [role="option"], [role="option"]'
            try:
                await self.page.locator(dropdown_sel).first.wait_for(state="visible", timeout=8000)
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
                if location_name.lower() in text.lower():
                    await opt.click()
                    print(f"[OOCL] Selected {label} from dropdown: {text.strip()}")
                    return True
                    
            opt_text = await options.nth(0).inner_text()
            await options.nth(0).click()
            print(f"[OOCL] Selected first {label} option: {opt_text.strip()}")
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
            
            origin_success = await self._select_location("Origin", origin_field, request.origin)
            if not origin_success:
                return CarrierResultStatus.INVALID_SEARCH_INPUT
                
            dest_success = await self._select_location("Destination", dest_field, request.destination)
            if not dest_success:
                return CarrierResultStatus.INVALID_SEARCH_INPUT
                
            if "REEFER" in request.container_type.upper():
                try:
                    await self.page.locator('label:has-text("Reefer"), input[value="Reefer"]').first.click()
                except Exception:
                    pass
                    
            search_btn = self.page.locator('button:has-text("Search")').first
            await search_btn.click()
            print("[OOCL] Clicked Search button.")
            
            try:
                await self.page.locator('.ag-row, text=/No schedule found/i').first.wait_for(state="attached", timeout=20000)
            except Exception:
                print("[OOCL] Timeout waiting for search results.")
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

    async def extract_quote_list(self) -> list[dict]:
        quotes = []
        try:
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
                    lines = [line.strip() for line in text.split('\\n') if line.strip()]
                    
                    tt_match = re.search(r'(\d+)\s*day\(s\)', text, re.IGNORECASE)
                    tt_days = int(tt_match.group(1)) if tt_match else None
                    
                    ts_match = re.search(r'(\d+)\s*Transshipment', text, re.IGNORECASE)
                    is_transit = ts_match is not None
                    
                    details_btn = row.locator('text="Schedule Details"').first
                    expanded_text = ""
                    if await details_btn.is_visible():
                        await details_btn.click()
                        await self.page.wait_for_timeout(1000)
                        
                        try:
                            expanded_text = await row.inner_text()
                            next_row = self.page.locator('tr').nth(i * 2 + 1)
                            if await next_row.is_visible(timeout=500):
                                expanded_text += "\\n" + await next_row.inner_text()
                        except Exception:
                            pass
                        
                    etd_match = re.search(r'(\d{1,2}\s+[A-Za-z]{3}).*?ETD at POL', expanded_text)
                    eta_match = re.search(r'(\d{1,2}\s+[A-Za-z]{3}).*?ETA at POD', expanded_text)
                    
                    etd_str = etd_match.group(1) if etd_match else None
                    eta_str = eta_match.group(1) if eta_match else None
                    
                    etd_iso = None
                    eta_iso = None
                    current_year = datetime.now().year
                    
                    if etd_str:
                        try:
                            dt = datetime.strptime(f"{etd_str} {current_year}", "%d %b %Y")
                            etd_iso = dt.strftime("%Y-%m-%d")
                        except: pass
                    if eta_str:
                        try:
                            dt = datetime.strptime(f"{eta_str} {current_year}", "%d %b %Y")
                            eta_iso = dt.strftime("%Y-%m-%d")
                        except: pass
                        
                    routing_str = "Direct"
                    if is_transit:
                        ts_ports = []
                        ts_matches = re.finditer(r'ETA at T/S Port\s*([A-Za-z\s\(\)]+)', expanded_text)
                        for m in ts_matches:
                            port_name = m.group(1).strip()
                            port_name = re.split(r'\\n', port_name)[0].strip()
                            if port_name not in ts_ports:
                                ts_ports.append(port_name)
                        
                        if ts_ports:
                            routing_str = "via " + ", ".join(ts_ports)
                        else:
                            routing_str = "Transit"
                            
                    vessel_voyage = lines[-2] + " " + lines[-1] if len(lines) >= 2 else "UNKNOWN"
                    
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
                        vessel=vessel_voyage
                    )
                    quotes.append(quote.model_dump())
                    
                    if await details_btn.is_visible():
                        await details_btn.click()
                        await self.page.wait_for_timeout(500)
                        
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

    async def open_price_breakdown(self) -> bool:
        return True

    async def extract_charge_breakdown(self) -> dict:
        return {"ocean_freight": 0, "surcharges": [], "total": 0}

    def normalize_result(self, raw_quote: dict) -> dict:
        return raw_quote
