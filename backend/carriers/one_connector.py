
"""
ONE (Ocean Network Express) Live Connector — Playwright automation.

Credentials read from env: ONE_USERNAME, ONE_PASSWORD
Never hardcode credentials.
"""
import os
import re
from datetime import date, datetime, timedelta
from playwright.async_api import async_playwright
from models.schemas import RateSearchRequest, QuoteSchema, CarrierResultStatus
from services.charge_classifier import classify_charge
from services.normalizer import normalize_quote
from carriers.base_connector import BaseCarrierConnector


class ONEConnector(BaseCarrierConnector):
    carrier_code = "ONE"
    carrier_name = "Ocean Network Express"
    LOGIN_URL = "https://ecomm.one-line.com/one-ecom/login"
    QUOTE_URL = "https://ecomm.one-line.com/one-ecom/prices/one-quote-booking"

    def __init__(self):
        super().__init__()
        self.playwright = None

    async def _init_browser(self):
        self.playwright = await async_playwright().start()
        is_prod = os.name != "nt"
        self.browser = await self.playwright.chromium.launch(
            headless=is_prod,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"],
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

    async def _select_dropdown_option(self, label: str, value: str) -> bool:
        normalized_value = value.strip().upper()
        option_candidates = [normalized_value]
        if "," in normalized_value:
            option_candidates.append(normalized_value.split(",", 1)[0].strip())

        try:
            options = self.page.locator('[role="option"]:visible')
            option_count = await options.count()

            for index in range(option_count):
                option = options.nth(index)
                option_text = (await option.inner_text()).strip().upper()
                if any(candidate in option_text for candidate in option_candidates):
                    await option.click()
                    print(f"[ONE] {label} selected: {option_text}")
                    return True

            for candidate in option_candidates:
                try:
                    option = self.page.locator('[role="option"]').filter(has_text=candidate).first
                    await option.wait_for(state="visible", timeout=2_000)
                    await option.click()
                    print(f"[ONE] {label} selected: {candidate}")
                    return True
                except Exception:
                    continue

            # Final last resort: just press Enter on what was typed and hope the portal accepts it
            print(f"[ONE] {label} no dropdown match, pressing Enter as last resort for: {value}")
            await self.page.keyboard.press("Enter")
            await self.page.wait_for_timeout(1000)
            return True
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

            target_date = self._resolve_departure_date(request.departure_date)
            target_date_text = target_date.isoformat()

            origin_code = self._extract_port_code(request.origin)
            print(f"[ONE] Filling Origin: {origin_code} (extracted from {request.origin})")
            try:
                origin_field = self.page.get_by_role("combobox", name="Please search location").nth(0)
                await origin_field.click()
                await self.page.keyboard.type(origin_code, delay=25)
                await self.page.wait_for_timeout(1500)
                if not await self._select_dropdown_option("Origin", origin_code):
                    return CarrierResultStatus.INVALID_SEARCH_INPUT
            except Exception as e:
                print(f"[ONE] Origin combobox failed: {e}")
                return CarrierResultStatus.INVALID_SEARCH_INPUT

            destination_code = self._extract_port_code(request.destination)
            print(f"[ONE] Filling Destination: {destination_code} (extracted from {request.destination})")
            try:
                destination_field = self.page.get_by_role("combobox", name="Please search location").nth(1)
                await destination_field.click()
                await self.page.keyboard.type(destination_code, delay=25)
                await self.page.wait_for_timeout(1500)
                if not await self._select_dropdown_option("Destination", destination_code):
                    return CarrierResultStatus.INVALID_SEARCH_INPUT
            except Exception as e:
                print(f"[ONE] Destination combobox failed: {e}")
                return CarrierResultStatus.INVALID_SEARCH_INPUT

            print(f"[ONE] Setting Equipment Type: {request.container_type}")
            try:
                equipment_field = self.page.get_by_role("combobox", name="Select an Equipment Type").first
                await equipment_field.click()
                await self.page.wait_for_timeout(500)
                equipment_option = self.page.get_by_role("option", name=request.container_type).first
                await equipment_option.wait_for(state="visible", timeout=5_000)
                await equipment_option.click()
                print(f"[ONE] Equipment selected: {request.container_type}")
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

            print(f"[ONE] Setting Commodity: {request.commodity}")
            try:
                commodity_field = self.page.get_by_role("combobox", name="Please input Commodity Name or HS code").first
                await commodity_field.click()
                await self.page.wait_for_timeout(500)
                await self.page.keyboard.type(request.commodity, delay=25)
                
                # Wait for dropdown options to appear
                try:
                    first_option = self.page.locator('[role="option"]').first
                    await first_option.wait_for(state="visible", timeout=3000)
                    
                    # Try to find exact match first, fallback to first available option
                    exact_match = self.page.locator('[role="option"]').filter(has_text=request.commodity.upper()).first
                    if await exact_match.is_visible():
                        await exact_match.click()
                    else:
                        await first_option.click()
                except Exception:
                    # Fallback to Enter key if no dropdown appears
                    await self.page.keyboard.press("Enter")
                    
                await self.page.wait_for_timeout(3000) # Wait for chip to form
            except Exception as e:
                print(f"[ONE] Commodity selection failed: {e}")
                return CarrierResultStatus.INVALID_SEARCH_INPUT

            print("[ONE] Opening date picker and accepting available sailing date...")
            try:
                date_field = self.page.locator('text=/please select vessel departure date at origin/i').first
                try:
                    await date_field.wait_for(state="visible", timeout=5000)
                except Exception:
                    date_field = self.page.get_by_role("textbox", name="Please select vessel departure date at origin")
                    await date_field.wait_for(state="visible", timeout=5000)
                
                # Ensure we scroll the date field into view and wait a bit for any dynamic overlays to settle
                await date_field.scroll_into_view_if_needed()
                await self.page.wait_for_timeout(1000)
                await date_field.click(force=True)
                
                # Wait for the calendar container to be visible
                print("[ONE] Waiting for calendar to appear...")
                try:
                    calendar_sel = 'div[class*="Calendar"], .react-calendar, [class*="calendar-picker"], .MuiCalendarPicker-root'
                    await self.page.locator(calendar_sel).first.wait_for(state="visible", timeout=10000)
                    print("[ONE] Calendar visible")
                except Exception:
                    print("[ONE] Warning: Calendar container not detected, continuing with strategies")

                await self.page.wait_for_timeout(2000)
                
                date_selected = False
                
                # Strategy 1: Click "view Quote" directly if it's already there (e.g. from a previous search)
                try:
                    view_quote_btn = self.page.locator('button:has-text("View Quote"), button:has-text("view Quote"), text="View Quote", text="view Quote"').first
                    await view_quote_btn.wait_for(state="visible", timeout=2000)
                    await view_quote_btn.click(force=True)
                    date_selected = True
                    print("[ONE] Clicked 'view Quote' directly from calendar")
                except Exception:
                    pass
                
                # We wrap the main hunting strategies in a loop to handle "Next Month" if current month is empty
                for month_attempt in range(2): # Current month + Next month
                    if date_selected: break
                    
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
                            # The debug screenshot showed prices in elements with "date-picker-date-highlight"
                            price_locator = self.page.locator('[class*="date-picker-date-highlight"], .react-datepicker__day--highlighted').first
                            await price_locator.wait_for(state="visible", timeout=5000)

                            await price_locator.click(force=True)
                            date_selected = True
                            price_text = await price_locator.inner_text()
                            print(f"[ONE] Clicked highlighted date cell with price: {price_text}")
                        except Exception:
                            pass

                    # Strategy 3: Search for ANY numeric price label (anchored regex) inside calendar tiles
                    if not date_selected:
                        try:
                            # Broad search for 3-4 digit numbers or K-values inside anything that looks like a day tile
                            price_tile = self.page.locator('.react-datepicker__day, [class*="day"], [class*="tile"]').get_by_text(
                                re.compile(r"\d{3,4}|[\d.]+[kK]"), exact=False
                            ).first
                            await price_tile.wait_for(state="visible", timeout=3000)

                            await price_tile.click(force=True)
                            date_selected = True
                            tile_text = await price_tile.inner_text()
                            print(f"[ONE] Safety-net: clicked tile with numeric content: {tile_text}")
                        except Exception:
                            pass

                # Strategy 4: Click any non-disabled calendar cell with content
                if not date_selected:
                    try:
                        # Target anything that looks like a date cell and is not disabled
                        any_cell = self.page.locator('[class*="Calendar"] button:not([disabled]), .react-calendar__tile:not([disabled]), [class*="Calendar"] [class*="available"]').first
                        await any_cell.wait_for(state="visible", timeout=3000)
                        await any_cell.click(force=True)
                        date_selected = True
                        print("[ONE] Clicked an available calendar cell (tile search)")
                    except Exception:
                        pass

                # Strategy 5: Absolute fallback - click any element with a price-like number
                if not date_selected:
                    try:
                        fallback_price = self.page.get_by_text(re.compile(r"^\d{3,4}$")).first
                        await fallback_price.click(force=True, timeout=3000)
                        date_selected = True
                        print("[ONE] Clicked a 3-4 digit number as absolute fallback")
                    except Exception:
                        await self.page.screenshot(path=r"C:\Users\Brian\.gemini\antigravity\brain\ceb649b4-c6b6-446d-8bd7-1b3242bce92b\one_debug.png")
                        print("[ONE] All date picker strategies failed (saved screenshot to artifacts)")

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
                for _ in range(10):
                    is_disabled = await submit_btn.get_attribute("disabled")
                    if is_disabled is None:
                        # Also check common "disabled" classes
                        btn_class = await submit_btn.get_attribute("class") or ""
                        if "disabled" not in btn_class.lower():
                            break
                    await self.page.wait_for_timeout(500)
                
                await submit_btn.click(force=True, timeout=5000)
                print("[ONE] Search submitted (force click)")
            except Exception as e:
                print(f"[ONE] Submit click failed: {e}")

            print("[ONE] Waiting for search results to load...")
            try:
                await self.page.wait_for_url(lambda url: "search" in url.lower() or "result" in url.lower() or "quote" in url.lower(), timeout=30000)
            except Exception:
                pass
            await self.page.wait_for_timeout(5000)
            print(f"[ONE] Search page ready: {self.page.url}")
            return CarrierResultStatus.AVAILABLE_QUOTES_FOUND
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
                    if vessel == "---" or not vessel:
                        vessel = "Sold out"
                        
                    status = summary_match.group(6).strip()
                    pol = summary_match.group(7).strip()
                    pod = summary_match.group(8).strip()
                    total_price = float(summary_match.group(9).replace(",", ""))
                    service_name = f"{service_lane} / {vessel}" if vessel != "Sold out" else "Sold out"
                else:
                    print(f"[ONE] Could not parse full quote summary for card {index + 1}. Fallback extraction...")
                    price_match = re.search(r"USD\s*([\d,]+\.\d{2})", normalized_text)
                    if price_match:
                        total_price = float(price_match.group(1).replace(",", ""))
                    etd_match = re.search(r"Origin\s+(\d{4}-\d{2}-\d{2})", normalized_text)
                    if etd_match: etd = etd_match.group(1)
                    eta_match = re.search(r"Destination\s+(\d{4}-\d{2}-\d{2})", normalized_text)
                    if eta_match: eta = eta_match.group(1)

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

            charges = []
            for index, line in enumerate(lines):
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
        return normalize_quote(self.carrier_code, raw_quote, raw_charges)

    async def close(self):
        try:
            if self.page: await self.page.close()
            if self.context: await self.context.close()
            if self.browser: await self.browser.close()
            if self.playwright: await self.playwright.stop()
        except Exception:
            pass
