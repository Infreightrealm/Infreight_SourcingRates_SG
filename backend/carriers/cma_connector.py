
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
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
from models.schemas import RateSearchRequest, QuoteSchema, CarrierResultStatus, ChargeCategory
from services.charge_classifier import classify_charge
from services.normalizer import normalize_quote
from carriers.base_connector import BaseCarrierConnector


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

    async def _init_browser(self):
        self.playwright = await async_playwright().start()
        
        # Local profile directory to persist cookies, logins, and session data
        profile_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chrome_profile")
        
        # Check if Bright Data Web Unlocker proxy credentials are set
        proxy_user = os.getenv("BRIGHTDATA_PROXY_USER")
        proxy_pass = os.getenv("BRIGHTDATA_PROXY_PASS")
        
        is_prod = os.name != "nt"
        launch_kwargs = {
            "user_data_dir": profile_dir,
            "headless": is_prod,
            "ignore_https_errors": True,
            "slow_mo": random.randint(50, 150) if not is_prod else 0,
            "viewport": {"width": 1920, "height": 1080},
            "args": [
                "--disable-blink-features=AutomationControlled",  # Mask automation flag
            ]
        }
        if not is_prod:
            launch_kwargs["channel"] = "chrome"
        
        if proxy_user and proxy_pass:
            proxy_server = os.getenv("BRIGHTDATA_PROXY_SERVER", "http://brd.superproxy.io:33335")
            print(f"[CMA] 🌐 Routing browser session through Bright Data Proxy ({proxy_server})...")
            launch_kwargs["proxy"] = {
                "server": proxy_server,
                "username": proxy_user,
                "password": proxy_pass,
            }
        else:
            print("[CMA] ℹ️ Bright Data Proxy not configured in .env. Running on local system Chrome naturally...")
            
        self.context = await self.playwright.chromium.launch_persistent_context(**launch_kwargs)
        self.browser = None  # Handled by persistent context
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
            print("[CMA] ⚠️  [ACTION REQUIRED] DataDome CAPTCHA/Verification Page Detected!")
            print("[CMA] ⚠️  Please look at the opened Chromium browser window on your screen.")
            print("[CMA] ⚠️  Manually slide the captcha handle with your mouse.")
            print("[CMA] ⚠️  Waiting up to 90 seconds for manual resolution...")

            for i in range(90):
                await asyncio.sleep(1)
                try:
                    # Check if the iframe is still visible on the page
                    is_visible = await captcha_iframe.is_visible(timeout=500)
                    if not is_visible:
                        print("[CMA] 🎉 [SUCCESS] CAPTCHA resolved by user! Resuming search automation...")
                        return True
                except Exception:
                    # If the page reloads or the iframe is destroyed, we've successfully passed the verification
                    print("[CMA] 🎉 [SUCCESS] CAPTCHA resolved! Resuming search automation...")
                    return True
                
                if i % 10 == 9:
                    print(f"[CMA] Still waiting for manual CAPTCHA solving... {90 - i - 1} seconds remaining.")
            
            print("[CMA] ❌ [TIMEOUT] User did not solve the CAPTCHA within 90 seconds.")
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
            print("[CMA] Navigating to quote page...")
            await self.page.goto(self.QUOTE_URL, wait_until="networkidle")
            await self._random_mouse_move()
            
            # Check for CAPTCHA/Verification
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
                # Check again
                if "Verification Required" in await self.page.content():
                    print("[CMA] Still on CAPTCHA page. Giving up.")
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
                await self.page.wait_for_selector(email_sel, timeout=15000)
                await self._hover_and_click(email_sel)
                await self.page.keyboard.type(username, delay=random.randint(70, 150))
                await self._human_delay(400, 800)
                await self._hover_and_click(pwd_sel)
                await self.page.keyboard.type(password, delay=random.randint(70, 150))
            except Exception:
                # Fallback to click + type
                await self._hover_and_click(email_sel)
                await self.page.keyboard.type(username, delay=100)
                await self._human_delay(500, 1000)
                await self._hover_and_click(pwd_sel)
                await self.page.keyboard.type(password, delay=100)

            print("[CMA] Clicking Log in button...")
            submit_sel = 'button:has-text("Log in"), button[type="submit"]'
            await self._hover_and_click(submit_sel)

            print("[CMA] Waiting for redirect back to cma-cgm.com...")
            await self.page.wait_for_url(
                lambda url: "cma-cgm.com" in url and "auth.cma-cgm" not in url,
                timeout=30000
            )

            print("[CMA] Navigating explicitly back to quote form...")
            await self.page.goto(self.QUOTE_URL, wait_until="networkidle")
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

    async def search_quotes(self, request: RateSearchRequest) -> CarrierResultStatus:
        try:
            print("[CMA] Starting search...")
            
            # --- ORIGIN ---
            origin_code = self._extract_port_code(request.origin)
            origin_field = self.page.locator('input[placeholder*="Name / Code / Port" i]').nth(0)
            await origin_field.click()
            await self.page.keyboard.type(origin_code, delay=30)
            await self.page.wait_for_timeout(1500)

            # Dropdown selection
            suggestion_sel = '[class*="suggestion"], [class*="option"], li[role="option"]'
            try:
                suggestions = self.page.locator(suggestion_sel)
                count = await suggestions.count()
                selected = False
                for i in range(count):
                    text = await suggestions.nth(i).inner_text()
                    if origin_code in text and "PORT" in text:
                        await self._hover_and_click(suggestions.nth(i))
                        selected = True
                        break
                if not selected and count > 0:
                    await self._hover_and_click(suggestions.nth(0))
                    selected = True
                
                if not selected:
                    print("[CMA] Origin suggestion not found.")
                    return CarrierResultStatus.INVALID_SEARCH_INPUT
            except Exception:
                return CarrierResultStatus.INVALID_SEARCH_INPUT
            
            print(f"[CMA] Origin selected: {origin_code}")

            # --- DESTINATION ---
            dest_code = self._extract_port_code(request.destination)
            dest_field = self.page.locator('input[placeholder*="Name / Code / Port" i]').nth(1)
            await dest_field.click()
            await self.page.keyboard.type(dest_code, delay=30)
            await self.page.wait_for_timeout(1500)

            try:
                suggestions = self.page.locator(suggestion_sel)
                count = await suggestions.count()
                selected = False
                for i in range(count):
                    text = await suggestions.nth(i).inner_text()
                    if dest_code in text and "PORT" in text:
                        await self._hover_and_click(suggestions.nth(i))
                        selected = True
                        break
                if not selected and count > 0:
                    await self._hover_and_click(suggestions.nth(0))
                    selected = True
                
                if not selected:
                    print("[CMA] Destination suggestion not found.")
                    return CarrierResultStatus.INVALID_SEARCH_INPUT
            except Exception:
                return CarrierResultStatus.INVALID_SEARCH_INPUT
            
            print(f"[CMA] Destination selected: {dest_code}")

            # --- CONTAINER TYPE & SIZE ---
            cma_container = self.CONTAINER_TYPE_MAP.get(request.container_type)
            if not cma_container:
                print(f"[CMA] Container type {request.container_type} not mapped.")
                return CarrierResultStatus.INVALID_SEARCH_INPUT

            try:
                container_section = self.page.locator(f'div:has-text("{cma_container}")').filter(has_text="Add").first
                await container_section.locator('button:has-text("+"), button[aria-label*="add" i]').click()
            except Exception:
                # Fallback
                cards = self.page.locator('div:has-text("' + cma_container + '")')
                found = False
                for i in range(await cards.count()):
                    card = cards.nth(i)
                    if "Add" in await card.inner_text():
                        await card.locator('button').filter(has_text="+").click()
                        found = True
                        break
                if not found:
                    print(f"[CMA] Could not find 'Add' button for {cma_container}")
                    return CarrierResultStatus.INVALID_SEARCH_INPUT

            # Confirm selection
            weight_field_sel = 'input[placeholder*="10 000" i], input[placeholder*="KGM" i], input[aria-label*="weight" i]'
            await self.page.wait_for_selector(weight_field_sel, timeout=5000)

            # --- QUANTITY ---
            if request.container_quantity > 1:
                qty_plus_btn = self.page.locator('div[class*="selected"] button:has-text("+")').first
                for _ in range(request.container_quantity - 1):
                    await qty_plus_btn.click()
                    await self.page.wait_for_timeout(300)

            # --- CARGO WEIGHT ---
            weight_field = self.page.locator(weight_field_sel).first
            await weight_field.click()
            await weight_field.fill(str(int(request.weight_per_container_kg)))

            # --- COMMODITY ---
            commodity_dropdown = self.page.locator('div[class*="commodity"], button:has-text("Choose a commodity"), [placeholder*="commodity" i]').first
            await commodity_dropdown.click()
            await self.page.wait_for_timeout(1000)
            
            fak_option = self.page.locator('li:has-text("Freight All Kinds"), [role="option"]:has-text("Freight All Kinds")').first
            await fak_option.click()

            # --- SUBMIT ---
            submit_btn = self.page.locator('button:has-text("Get My Quote"), input[value*="Get My Quote" i]').first
            await self._hover_and_click(submit_btn)
            await self._human_delay(4000, 7000)

            # Results detection
            try:
                await self.page.wait_for_selector('div[class*="schedules-result"], div[class*="sailing-result"], article[class*="schedule"]', timeout=20000)
                print("[CMA] Results loaded.")
                return CarrierResultStatus.AVAILABLE_QUOTES_FOUND
            except Exception:
                print("[CMA] No results found or timeout.")
                return CarrierResultStatus.NO_RATES_FOUND

        except Exception as e:
            print(f"[CMA] Search failed: {e}")
            return CarrierResultStatus.TIMEOUT if "timeout" in str(e).lower() else CarrierResultStatus.UNKNOWN_ERROR

    async def extract_quote_list(self) -> list[dict]:
        try:
            cards_sel = 'div[class*="schedules-result"], div[class*="sailing-result"], div[class*="quote-card"], article[class*="schedule"]'
            cards = self.page.locator(cards_sel)
            count = await cards.count()
            
            if count == 0:
                # Broader fallback
                cards = self.page.locator('div:has(button:has-text("Details")):has-text("USD")')
                count = await cards.count()

            print(f"[CMA] Found {count} quote cards.")
            self._all_quotes = []

            for i in range(count):
                card = cards.nth(i)
                text = await card.inner_text()
                
                # ETD & ETA extraction
                # Pattern: "Saturday, 16-May-2026"
                date_pattern = r'[A-Za-z]+, \d{2}-[A-Za-z]+-\d{4}'
                found_dates = re.findall(date_pattern, text)
                etd_str = found_dates[0] if len(found_dates) > 0 else None
                eta_str = found_dates[1] if len(found_dates) > 1 else None
                
                etd = None
                if etd_str:
                    try:
                        etd = datetime.strptime(etd_str, "%A, %d-%b-%Y").date()
                    except: pass
                
                eta = None
                if eta_str:
                    try:
                        eta = datetime.strptime(eta_str, "%A, %d-%b-%Y").date()
                    except: pass

                # Transit time
                tt_match = re.search(r'(\d+)\s*[Dd]ay', text)
                transit_time = int(tt_match.group(1)) if tt_match else None

                # Service & Vessel
                service_match = re.search(r'First Service\s+(.+)', text)
                service = service_match.group(1).strip().split('\n')[0] if service_match else None
                
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
                    "service_name": service,
                    "vessel": vessel,
                    "total_price": total_price,
                    "currency": "USD",
                    "tags": tags,
                    "card_locator": card,
                    "source": "carrier_portal",
                    "carrier_code": self.carrier_code
                })

            # Handle "More results"
            await self._handle_more_results()

            return self._all_quotes
        except Exception as e:
            print(f"[CMA] Error extracting quotes: {e}")
            return []

    async def _handle_more_results(self):
        """
        Clicks 'More results' once and appends new unique quotes to self._all_quotes.
        """
        try:
            # Scroll to bottom first to ensure button is rendered/visible
            print("[CMA] Scrolling to bottom to check for more results...")
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await self.page.wait_for_timeout(1000)

            more_btn = self.page.locator('button:has-text("More results"), a:has-text("More results")').first
            if await more_btn.is_visible():
                print("[CMA] Loading more results...")
                await more_btn.scroll_into_view_if_needed()
                await more_btn.click()
                await self.page.wait_for_timeout(5000)  # Wait for new cards to load
                
                cards_sel = 'div[class*="schedules-result"], div[class*="sailing-result"], div[class*="quote-card"], article[class*="schedule"]'
                new_cards = self.page.locator(cards_sel)
                new_count = await new_cards.count()
                
                # Keep track of what we already have (ETD + Vessel)
                existing_keys = { (q["etd"], q["vessel"]) for q in self._all_quotes }
                
                for i in range(new_count):
                    card = new_cards.nth(i)
                    text = await card.inner_text()
                    
                    # Basic extraction for deduplication
                    date_pattern = r'[A-Za-z]+, \d{2}-[A-Za-z]+-\d{4}'
                    found_dates = re.findall(date_pattern, text)
                    etd_str = found_dates[0] if len(found_dates) > 0 else None
                    etd_iso = None
                    if etd_str:
                        try:
                            etd_iso = datetime.strptime(etd_str, "%A, %d-%b-%Y").date().isoformat()
                        except: pass
                    
                    vessel_match = re.search(r'Vessel\s+(.+?)\s+CO2', text)
                    vessel = vessel_match.group(1).strip() if vessel_match else None
                    
                    if (etd_iso, vessel) not in existing_keys:
                        # Full extraction for new card
                        eta_str = found_dates[1] if len(found_dates) > 1 else None
                        eta_iso = None
                        if eta_str:
                            try:
                                eta_iso = datetime.strptime(eta_str, "%A, %d-%b-%Y").date().isoformat()
                            except: pass

                        tt_match = re.search(r'(\d+)\s*[Dd]ay', text)
                        transit_time = int(tt_match.group(1)) if tt_match else None

                        service_match = re.search(r'First Service\s+(.+)', text)
                        service = service_match.group(1).strip().split('\n')[0] if service_match else None

                        price_match = re.search(r'(\d[\d,]*)\s*USD', text)
                        total_price = float(price_match.group(1).replace(",", "")) if price_match else 0.0

                        tags = []
                        if "EARLIEST ARRIVAL" in text: tags.append("EARLIEST ARRIVAL")
                        if "EARLIEST DEPARTURE" in text: tags.append("EARLIEST DEPARTURE")
                        if "LATE BOOKING" in text: tags.append("LATE BOOKING")

                        self._all_quotes.append({
                            "index": len(self._all_quotes),
                            "etd": etd_iso,
                            "eta": eta_iso,
                            "transit_time_days": transit_time,
                            "service_name": service,
                            "vessel": vessel,
                            "total_price": total_price,
                            "currency": "USD",
                            "tags": tags,
                            "card_locator": card,
                            "source": "carrier_portal",
                            "carrier_code": self.carrier_code
                        })
                        existing_keys.add((etd_iso, vessel))
                
                print(f"[CMA] Total quotes after 'More results': {len(self._all_quotes)}")
        except Exception as e:
            print(f"[CMA] Error handling more results: {e}")

    async def open_price_breakdown(self, quote_ref: dict) -> bool:

        try:
            card = quote_ref["card_locator"]
            await card.scroll_into_view_if_needed()
            await self._random_mouse_move()
            details_btn = card.locator('button:has-text("Details")').first
            await self._hover_and_click(details_btn)
            await self._human_delay(1500, 2500)

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
            
            charges = []
            
            # Pattern from user: (Ocean Freight|Charges payable as per freight|Charges payable at import)\s+([\d,]+)\s+USD
            pattern = r'(Ocean Freight|Charges payable as per freight|Charges payable at import)\s+([\d,]+)\s+USD'
            matches = re.findall(pattern, text, re.IGNORECASE)
            
            for name, amount_str in matches:
                amount = float(amount_str.replace(",", ""))
                if "Ocean Freight" in name:
                    category = ChargeCategory.BASIC_OCEAN_FREIGHT
                elif "as per freight" in name:
                    category = ChargeCategory.FREIGHT_SURCHARGE_INCLUDED
                elif "at import" in name:
                    category = ChargeCategory.DESTINATION_CHARGE_EXCLUDED
                
                charges.append({
                    "name": name.strip(),
                    "amount": amount,
                    "currency": "USD",
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

        return QuoteSchema(
            etd=raw_quote.get("etd"),
            eta=raw_quote.get("eta"),
            transit_time_days=raw_quote.get("transit_time_days"),
            service_name=raw_quote.get("service_name"),
            vessel=raw_quote.get("vessel"),
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
