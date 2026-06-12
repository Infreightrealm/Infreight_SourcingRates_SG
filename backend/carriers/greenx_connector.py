"""
GreenX (Evergreen) Live Connector - Playwright automation.
"""
import os
import re
import asyncio
from datetime import date
from playwright.async_api import async_playwright
from models.schemas import RateSearchRequest, QuoteSchema, CarrierResultStatus
from carriers.base_connector import BaseCarrierConnector
from services.port_manager import resolve_port_for_carrier

class GreenXConnector(BaseCarrierConnector):
    carrier_code = "GREENX"
    carrier_name = "GreenX (Evergreen)"
    LOGIN_URL = "https://www.greenxtrade.com/_gx/GREENX_SignIn"

    def __init__(self):
        super().__init__()
        self.playwright = None
        self._all_quotes = []
        self.current_charges = []
        self.search_year = date.today().year

    async def _init_browser(self):
        is_prod = os.name != "nt"
        self.playwright = await async_playwright().start()
        
        # Thread-safe virtual display environment injection
        browser_env = os.environ.copy()
        if is_prod:
            browser_env["DISPLAY"] = ":103"

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

    async def _clear_cookie_overlay(self) -> None:
        """Dismiss any cookie/alert modal that would intercept pointer events."""
        try:
            # Target the specific Bootstrap modal by ID first
            cookie_modal = self.page.locator("#modal_cookie_alert")
            if await cookie_modal.count() > 0 and await cookie_modal.is_visible():
                print("[GreenX] Cookie alert modal detected (#modal_cookie_alert). Dismissing...")
                # Try clicking any button inside it (Accept, OK, Close, etc.)
                dismissed = False
                for btn_sel in [
                    "#modal_cookie_alert button",
                    "#modal_cookie_alert .btn",
                    "#modal_cookie_alert [class*='accept' i]",
                    "#modal_cookie_alert [class*='close' i]",
                    "#modal_cookie_alert [data-bs-dismiss]",
                ]:
                    btn = self.page.locator(btn_sel).first
                    if await btn.count() > 0:
                        try:
                            await btn.click(timeout=3000)
                            dismissed = True
                            print(f"[GreenX] Clicked dismiss button via selector: {btn_sel}")
                            break
                        except Exception:
                            continue

                if not dismissed:
                    # Force-hide via JS as fallback
                    print("[GreenX] Force-hiding cookie modal via JS...")
                    await self.page.evaluate("""
                        const m = document.getElementById('modal_cookie_alert');
                        if (m) {
                            m.classList.remove('show');
                            m.style.display = 'none';
                            m.setAttribute('aria-hidden', 'true');
                            m.removeAttribute('aria-modal');
                            document.body.classList.remove('modal-open');
                            const backdrop = document.querySelector('.modal-backdrop');
                            if (backdrop) backdrop.remove();
                        }
                    """)

                # Wait for modal to fully disappear
                try:
                    await cookie_modal.wait_for(state="hidden", timeout=5000)
                    print("[GreenX] Cookie modal dismissed successfully.")
                except Exception:
                    pass
                await self.page.wait_for_timeout(500)
                return

            # Fallback: generic accept-all button scan
            accept_btn = self.page.locator(
                'button:has-text("Accept All"), button:has-text("Accept all"), [class*="accept" i]'
            ).first
            if await accept_btn.count() > 0 and await accept_btn.is_visible():
                print("[GreenX] Generic cookie overlay detected. Clicking 'Accept All'...")
                await accept_btn.click()
                await self.page.wait_for_timeout(1000)
        except Exception as e:
            print(f"[GreenX] Warning: failed to clear cookie overlay: {e}")


    async def login(self) -> bool:
        username = os.getenv("GREENX_USERNAME", "INFREIGHT.SG@IN-FREIGHT.COM")
        password = os.getenv("GREENX_PASSWORD", "InfreightSGa2026")
        
        try:
            await self._init_browser()
            print("[GreenX] Navigating to login page...")
            await self.page.goto(self.LOGIN_URL, wait_until="domcontentloaded", timeout=45000)
            await self.page.wait_for_timeout(2000) # Let page load JS
            await self._clear_cookie_overlay()
            
            # Find and fill email
            email_selectors = [
                'input[type="email"]',
                'input[placeholder*="Email" i]',
                'input[name*="email" i]',
                'input[id*="email" i]'
            ]
            email_field = None
            for sel in email_selectors:
                try:
                    locator = self.page.locator(sel).first
                    if await locator.is_visible():
                        email_field = locator
                        break
                except:
                    continue
            
            if not email_field:
                print("[GreenX] Email field not found")
                return False
                
            await email_field.fill(username)
            print("[GreenX] Filled email")

            # Find and fill password
            pwd_selectors = [
                'input[type="password"]',
                'input[placeholder*="password" i]',
                'input[name*="password" i]',
                'input[id*="password" i]'
            ]
            pwd_field = None
            for sel in pwd_selectors:
                try:
                    locator = self.page.locator(sel).first
                    if await locator.is_visible():
                        pwd_field = locator
                        break
                except:
                    continue

            if not pwd_field:
                print("[GreenX] Password field not found")
                return False

            await pwd_field.fill(password)
            print("[GreenX] Filled password")

            # Click submit
            submit_selectors = [
                'button[type="submit"]',
                'button:has-text("Submit")',
                'input[type="submit"]',
                '.btn-submit'
            ]
            submit_btn = None
            for sel in submit_selectors:
                try:
                    locator = self.page.locator(sel).first
                    if await locator.is_visible():
                        submit_btn = locator
                        break
                except:
                    continue

            if not submit_btn:
                print("[GreenX] Submit button not found")
                return False

            print("[GreenX] Clicking submit...")
            await submit_btn.click()
            
            # Verification Loop (HITL Bypassing)
            print("[GreenX] Waiting for dashboard redirect or verification gate...")
            for i in range(180):
                await asyncio.sleep(1)
                curr_url = self.page.url
                
                # Check for successful redirects
                if "signin" not in curr_url.lower() and "login" not in curr_url.lower() and "auth" not in curr_url.lower():
                    print("[GreenX] Login successful!")
                    await self._clear_cookie_overlay()
                    return True

                # Active challenge/captcha/2FA detection
                if await self.check_captcha_challenge():
                    if not self.captcha_detected:
                        self.captcha_detected = True
                        print("[GreenX] [ACTION REQUIRED] Bot challenge, CAPTCHA, or 2FA verification page detected! Please look at the opened VNC window to solve it.")
                
                # Print manual action notices
                if i % 15 == 14:
                    if self.captcha_detected:
                        print("[GreenX] [ACTION REQUIRED] Still blocked by CAPTCHA/2FA challenge. Please solve it in the VNC window.")
                    else:
                        print("[GreenX] [ACTION REQUIRED] GreenX Verification/2FA Page Detected!")
                        print("[GreenX] Please look at the opened Chromium window and manually complete the verification/CAPTCHA.")
                    print(f"[GreenX] Still waiting... {180 - i - 1} seconds remaining.")

            # Check if we somehow ended up on dashboard but loop timed out
            curr_url = self.page.url
            if "signin" not in curr_url.lower() and "login" not in curr_url.lower():
                print("[GreenX] Login successful (redirected after timeout)!")
                await self._clear_cookie_overlay()
                return True

            print("[GreenX] [TIMEOUT] Login verification timed out.")
            return False

        except Exception as e:
            print(f"[GreenX] Login error: {e}")
            return False

    async def _fill_autocomplete_port(self, input_selector_candidates: list[str], query: str, label: str) -> bool:
        """Type a LOCODE into the autocomplete field and click the first visible dropdown suggestion."""
        input_field = None
        for sel in input_selector_candidates:
            try:
                locator = self.page.locator(sel).first
                if await locator.is_visible():
                    input_field = locator
                    break
            except:
                continue

        if not input_field:
            print(f"[GreenX] Port input field for {label} not found")
            return False

        print(f"[GreenX] Typing '{query}' into {label}...")
        await input_field.click()
        await input_field.press("Control+A")
        await input_field.press("Backspace")
        await input_field.type(query, delay=100)
        await self.page.wait_for_timeout(1500)  # Wait for suggestions to render

        clicked = False
        query_upper = query.strip().upper()

        # Click the first visible dropdown option that contains the query
        try:
            suggestions = await self.page.locator('li, [role="option"]').all()
            for sug in suggestions:
                try:
                    if await sug.is_visible():
                        sug_text = (await sug.text_content() or "").strip()
                        if query_upper in sug_text.upper():
                            print(f"[GreenX] Clicking option: '{sug_text}'")
                            await sug.click()
                            clicked = True
                            break
                except:
                    continue
        except Exception as err:
            print(f"[GreenX] Error checking suggestions: {err}")

        if not clicked:
            print(f"[GreenX] WARNING: No dropdown option found for '{query}'. Proceeding.")
        else:
            print(f"[GreenX] Port selection locked in for {label}")

        await self.page.wait_for_timeout(1000)
        return True



    async def _fill_quantity(self, label_text: str, quantity: int) -> bool:
        """Find quantity input next to or below label_text and fill it."""
        print(f"[GreenX] Setting quantity for {label_text} to {quantity}...")
        selectors = [
            f'xpath=//*[contains(text(), "{label_text}")]/following::input[1]',
            f'xpath=//*[contains(text(), "{label_text}")]/ancestor::div[1]//input',
            f'input[aria-label*="{label_text}" i]',
            f'input[placeholder*="{label_text}" i]',
            f'input[id*="{label_text}" i]',
            f'input[name*="{label_text}" i]'
        ]
        
        input_field = None
        for sel in selectors:
            try:
                locator = self.page.locator(sel).first
                if await locator.is_visible():
                    input_field = locator
                    break
            except:
                continue

        if not input_field:
            print(f"[GreenX] Quantity field for {label_text} not found")
            return False

        try:
            # Use fill first
            await input_field.click()
            await input_field.press("Control+A")
            await input_field.press("Backspace")
            await input_field.type(str(quantity))
            print(f"[GreenX] Quantity for {label_text} set to {quantity}")
            return True
        except Exception as e:
            print(f"[GreenX] Failed to fill quantity for {label_text}: {e}")
            return False

    async def _fill_date(self, target_date: date) -> bool:
        date_str = target_date.strftime("%m/%d/%Y")
        print(f"[GreenX] Setting departure date to {date_str}...")
        selectors = [
            'input[placeholder*="date" i]',
            'input[placeholder*="ETD" i]',
            'input[id*="etd" i]',
            'input[name*="etd" i]',
            'xpath=//*[contains(text(), "EARLIEST ETD")]/following::input[1]'
        ]
        
        input_field = None
        for sel in selectors:
            try:
                locator = self.page.locator(sel).first
                if await locator.is_visible():
                    input_field = locator
                    break
            except:
                continue

        if not input_field:
            print("[GreenX] Date field not found")
            return False

        try:
            await input_field.click()
            await input_field.press("Control+A")
            await input_field.press("Backspace")
            await input_field.type(date_str)
            await input_field.press("Tab")
            print(f"[GreenX] Date set to {date_str}")
            return True
        except Exception as e:
            print(f"[GreenX] Failed to fill date: {e}")
            return False

    async def search_quotes(self, request: RateSearchRequest) -> CarrierResultStatus:
        try:
            # Resolve target search date
            try:
                from datetime import datetime, timedelta
                if request.departure_date == "today":
                    target_date = date.today()
                elif request.departure_date == "tomorrow":
                    target_date = date.today() + timedelta(days=1)
                else:
                    target_date = date.fromisoformat(request.departure_date)
                self.search_year = target_date.year
            except Exception as e:
                print(f"[GreenX] Failed to parse target date: {e}")
                target_date = date.today()
                self.search_year = target_date.year

            # 1. Click Quotes navigation tab
            print("[GreenX] Navigating to Quotes tab...")
            quotes_selectors = [
                'a[href*="Quotes" i]',
                ':text("Quotes")',
                '[class*="menu" i] >> text="Quotes"',
                'a:has-text("Quotes")',
                'button:has-text("Quotes")'
            ]
            quotes_btn = None
            for sel in quotes_selectors:
                try:
                    locator = self.page.locator(sel).first
                    if await locator.is_visible():
                        quotes_btn = locator
                        break
                except:
                    continue

            if not quotes_btn:
                print("[GreenX] Quotes tab button not found in header, trying direct URL redirection...")
                current_url = self.page.url
                if "tabkey=" in current_url:
                    tabkey = current_url.split("tabkey=")[1].split("&")[0]
                    target_url = f"https://www.greenxtrade.com/_gx/GREENX_Quotes?tabkey={tabkey}"
                    print(f"[GreenX] Navigating directly to: {target_url}")
                    await self.page.goto(target_url, wait_until="domcontentloaded", timeout=30000)
                else:
                    print("[GreenX] Could not redirect directly, Quotes tab unavailable")
                    return CarrierResultStatus.CONNECTOR_NOT_AVAILABLE
            else:
                await quotes_btn.click()
                print("[GreenX] Clicked Quotes button")
                # Wait dynamically for the search form to appear (up to 5s)
                for _ in range(10):
                    await self.page.wait_for_timeout(500)
                    try:
                        if await self.page.locator('input[placeholder*="ORIGIN" i], input[placeholder*="DESTINATION" i]').first.is_visible():
                            break
                    except Exception:
                        pass

            await self._clear_cookie_overlay()

            # Wait for search form
            print("[GreenX] Waiting for search form to render...")
            await self.page.wait_for_timeout(2000)

            # Fill date
            await self._fill_date(target_date)

            # 2. Resolve port LOCODEs
            origin_locode = resolve_port_for_carrier(request.origin, "greenx")
            dest_locode = resolve_port_for_carrier(request.destination, "greenx")
            
            # Fill Origin
            origin_selectors = [
                'input[placeholder*="ORIGIN" i]',
                'input[id*="origin" i]',
                'input[name*="origin" i]',
                'input[aria-label*="origin" i]',
                'xpath=//label[contains(text(),"ORIGIN")]/following::input[1]',
                'xpath=//*[contains(text(),"ORIGIN")]/following::input[1]'
            ]
            await self._fill_autocomplete_port(origin_selectors, origin_locode, "Origin")

            # Fill Destination
            dest_selectors = [
                'input[placeholder*="DESTINATION" i]',
                'input[id*="destination" i]',
                'input[name*="destination" i]',
                'input[aria-label*="destination" i]',
                'xpath=//label[contains(text(),"DESTINATION")]/following::input[1]',
                'xpath=//*[contains(text(),"DESTINATION")]/following::input[1]'
            ]
            await self._fill_autocomplete_port(dest_selectors, dest_locode, "Destination")

            # 3. Fill container quantity boxes: 20' SD, 40' SD, 40' SH
            qty_20_sd = 0
            qty_40_sd = 0
            qty_40_sh = 0

            req_type = request.container_type.upper().strip()
            if "20" in req_type:
                qty_20_sd = 1
            elif "40H" in req_type or "HC" in req_type or "SH" in req_type:
                qty_40_sh = 1
            elif "40" in req_type:
                qty_40_sd = 1
            else:
                qty_20_sd = 1

            await self._fill_quantity("20' SD", qty_20_sd)
            await self._fill_quantity("40' SD", qty_40_sd)
            await self._fill_quantity("40' SH", qty_40_sh)

            # 4. Click Search
            search_selectors = [
                'button:has-text("Search")',
                'button[type="submit"]',
                'input[type="submit"][value*="Search" i]',
                '.btn-search'
            ]
            search_btn = None
            for sel in search_selectors:
                try:
                    locator = self.page.locator(sel).first
                    if await locator.is_visible():
                        search_btn = locator
                        break
                except:
                    continue

            if not search_btn:
                print("[GreenX] Search button not found")
                return CarrierResultStatus.INVALID_SEARCH_INPUT

            print("[GreenX] Clicking Search...")
            await search_btn.click()

            # 5. Poll dynamically for results page elements (up to 30 seconds)
            print("[GreenX] Waiting for results page to load...")
            for attempt in range(30):
                await self.page.wait_for_timeout(1000)
                
                # Check for cookie overlay on first few attempts
                if attempt < 3:
                    await self._clear_cookie_overlay()

                # Check if Route Details is present
                route_details = self.page.locator('button:has-text("Route Details"), a:has-text("Route Details")')
                if await route_details.count() > 0:
                    print(f"[GreenX] Route Details found after {attempt + 1}s. Results loaded successfully.")
                    break
                
                # Check for no-results indicators
                try:
                    body_text = await self.page.locator("body").inner_text(timeout=500)
                    if "no results" in body_text.lower() or "no records" in body_text.lower() or "not found" in body_text.lower():
                        print(f"[GreenX] No results text found after {attempt + 1}s.")
                        return CarrierResultStatus.NO_QUOTES_AVAILABLE
                except Exception:
                    pass

            print(f"[GreenX] Current page URL after search: {self.page.url}")

            # Verify results actually rendered
            final_count = await self.page.locator('button:has-text("Route Details"), a:has-text("Route Details")').count()
            if final_count == 0:
                print("[GreenX] Poll loop exhausted — no Route Details cards found. Returning TIMEOUT.")
                return CarrierResultStatus.TIMEOUT

            return CarrierResultStatus.AVAILABLE_QUOTES_FOUND

        except Exception as e:
            print(f"[GreenX] Search quotes error: {e}")
            return CarrierResultStatus.UNKNOWN_ERROR

    async def _get_card_container(self, route_details_el):
        parent = route_details_el
        for _ in range(6):
            try:
                parent = parent.locator('..')
                if await parent.locator('button:has-text("Book"), [class*="book" i]').count() > 0:
                    # Go up one more level to wrap both header and collapsed/expanded detail panel
                    return parent.locator('..')
            except:
                break
        return route_details_el.locator('xpath=../../..')

    def standardize_date_smart(self, date_str: str) -> str:
        if not date_str:
            return ""
        parts = date_str.strip().split("/")
        if len(parts) == 2:
            try:
                month = int(parts[0])
                day = int(parts[1])
                return f"{self.search_year}-{month:02d}-{day:02d}"
            except:
                pass
        return date_str

    async def extract_quote_list(self) -> list[dict]:
        try:
            await self._clear_cookie_overlay()
            
            # Scroll to the bottom of the page repeatedly by scrolling the last card into view
            print("[GreenX] Scrolling to the bottom of the page to load all quotes...")
            prev_count = 0
            for scroll_attempt in range(15):
                card_buttons = self.page.locator('button:has-text("Route Details"):visible')
                count = await card_buttons.count()
                if os.getenv("GREENX_DEBUG", "").lower() == "true":
                    print(f"[GreenX] Scroll attempt {scroll_attempt}: found {count} visible buttons.")
                if count == 0:
                    await self.page.wait_for_timeout(1000)
                    continue
                if count == prev_count:
                    break
                prev_count = count
                # Scroll the last card button into view to trigger lazy loading
                last_btn = card_buttons.nth(count - 1)
                try:
                    await last_btn.scroll_into_view_if_needed()
                    await self.page.wait_for_timeout(800)
                except Exception as se:
                    print(f"[GreenX] Scroll warning: {se}")
                    break

            if os.getenv("GREENX_DEBUG", "").lower() == "true":
                await self.page.screenshot(path="greenx_after_scroll.png")
                print("[GreenX] Saved screenshot after scroll to greenx_after_scroll.png")
            
            route_details_locs = self.page.locator('button:has-text("Route Details"):visible')
            count = await route_details_locs.count()
            print(f"[GreenX] Found {count} potential quote cards on the page.")
            
            quotes = []
            for i in range(count):
                el = route_details_locs.nth(i)
                card = await self._get_card_container(el)
                card_text = await card.inner_text()
                
                # Check for USD price to filter out sold-out cards
                price_match = re.search(r'USD\s*([\d,]+\.\d{2})', card_text)
                if not price_match:
                    print(f"[GreenX] Quote card {i} does not have a USD price. Skipping (assumed sold out).")
                    continue
                    
                total_price = float(price_match.group(1).replace(",", ""))
                
                # Parse lines to extract fields
                lines = [l.strip() for l in card_text.split("\n") if l.strip()]
                
                etd_date = None
                eta_date = None
                service_name = None
                vessel_voyage = None
                
                for idx, line in enumerate(lines):
                    line_upper = line.upper()
                    if line_upper == "ETD" and idx + 1 < len(lines):
                        etd_date = lines[idx + 1]
                    elif line_upper == "ETA" and idx + 1 < len(lines):
                        eta_date = lines[idx + 1]
                    elif line_upper == "SERVICES" and idx + 1 < len(lines):
                        service_name = lines[idx + 1]
                    elif (line_upper == "VESSEL VOYAGE" or line_upper == "VESSEL/VOYAGE") and idx + 1 < len(lines):
                        vessel_voyage = lines[idx + 1]

                if not service_name:
                    # Fallback regex Loop search (e.g. NE3 loop name)
                    service_match = re.search(r'\b[A-Z]{2,3}\d\b', card_text)
                    if service_match:
                        service_name = service_match.group(0)

                # Transit time
                tt_match = re.search(r'(\d+)\s*days', card_text, re.IGNORECASE)
                transit_time = int(tt_match.group(1)) if tt_match else None

                etd_standardized = self.standardize_date_smart(etd_date)
                eta_standardized = self.standardize_date_smart(eta_date)

                quote_ref = {
                    "index": i,
                    "etd_date_raw": etd_date,
                    "eta_date_raw": eta_date,
                    "etd_standardized": etd_standardized,
                    "eta_standardized": eta_standardized,
                    "transit_time_days": transit_time,
                    "service_name": service_name,
                    "vessel_voyage": vessel_voyage,
                    "total_price": total_price,
                    "currency": "USD",
                    "card_locator": card,
                    "raw_reference": f"GREENX-{i}",
                    "routing": "Direct",
                    "free_time": None,
                    "charges": []
                }
                quotes.append(quote_ref)
                print(f"[GreenX] Extracted card {i}: ETD={etd_date}, ETA={eta_date}, Service={service_name}, Voyage={vessel_voyage}, Price={total_price}")

            self._all_quotes = quotes
            return quotes
        except Exception as e:
            print(f"[GreenX] Error extracting quote list: {e}")
            return []

    async def _click_detail_tab(self, card, tab_text: str) -> bool:
        try:
            btn = card.locator(f'button:has-text("{tab_text}"), a:has-text("{tab_text}"), :text("{tab_text}")').first
            await btn.scroll_into_view_if_needed()
            # Snapshot text before click to detect content change
            text_before = await card.inner_text()
            await btn.click()
            # Wait dynamically for the card content to update (up to 3s)
            for _ in range(15):
                await self.page.wait_for_timeout(200)
                try:
                    text_after = await card.inner_text()
                    if text_after != text_before:
                        break
                except Exception:
                    break
            return True
        except Exception as e:
            print(f"[GreenX] Error clicking {tab_text} tab: {e}")
            return False

    async def open_price_breakdown(self, quote_ref: dict) -> bool:
        try:
            card = quote_ref["card_locator"]
            
            # 1. Route Details
            print(f"[GreenX] Opening Route Details for card {quote_ref['index']}...")
            if await self._click_detail_tab(card, "Route Details"):
                route_text = await card.inner_text()
                # Find voyages (3 digits followed by direction letter, e.g. 037W)
                voyage_matches = re.findall(r'\b\d{3}[A-Z]\b', route_text)
                
                # Check for detailed vessel name
                vessel_match = re.search(r'POL\s+[^\r\n]+\s+POD\s+[^\r\n]+\s+([A-Z\s]{5,30})', route_text)
                if vessel_match:
                    quote_ref["detailed_vessel"] = vessel_match.group(1).strip()
                    
                unique_voyages = list(set(voyage_matches))
                # If multiple legs/vessels are found, it's Transit. Otherwise, Direct.
                if len(unique_voyages) > 1:
                    quote_ref["routing"] = "Transit"
                else:
                    quote_ref["routing"] = "Direct"
                if os.getenv("GREENX_DEBUG", "").lower() == "true":
                    print(f"[GreenX] Extracted routing: {quote_ref['routing']}")

            # 2. Price Details
            print(f"[GreenX] Opening Price Details for card {quote_ref['index']}...")
            if await self._click_detail_tab(card, "Price Details"):
                price_text = await card.inner_text()
                charges = []
                
                # Regex for matching line item charge name and its price
                pattern = r"(.+?)\s+(?:20'\s*Standard\s*Dry|40'\s*Standard\s*Dry|40'\s*High\s*Cube|Per\s*B/L|20'\s*SD|40'\s*SD|40'\s*SH)\s+x\s*\d+\s+USD\s*([\d,]+\.\d{2})"
                matches = re.findall(pattern, price_text)
                
                for name_raw, amount_str in matches:
                    name = name_raw.strip()
                    name = re.sub(r'^\s*\d+\s+', '', name) # Strip numbers
                    amount = float(amount_str.replace(",", ""))
                    charges.append({
                        "name": name,
                        "amount": amount,
                        "currency": "USD"
                    })
                    if os.getenv("GREENX_DEBUG", "").lower() == "true":
                        print(f"[GreenX] Parsed charge row: {name} = USD {amount}")
                
                quote_ref["charges"] = charges
                self.current_charges = charges

            # 3. Free Time
            print(f"[GreenX] Opening Free Time details for card {quote_ref['index']}...")
            if await self._click_detail_tab(card, "Free Time"):
                free_time_text = await card.inner_text()
                
                if "Tariff Free Time at Destination" in free_time_text:
                    dest_part = free_time_text.split("Tariff Free Time at Destination")[1]
                    det_match = re.search(r"Container\s+Detention\s*[\r\n]*\s*(\d+)\s+Calendar\s+Days", dest_part, re.IGNORECASE)
                    if det_match:
                        quote_ref["free_time"] = int(det_match.group(1))
                        if os.getenv("GREENX_DEBUG", "").lower() == "true":
                            print(f"[GreenX] Extracted free time detention: {quote_ref['free_time']} days")
            
            return True
        except Exception as e:
            print(f"[GreenX] Error opening price breakdown: {e}")
            return False

    async def extract_charge_breakdown(self) -> list[dict]:
        return self.current_charges

    async def normalize_result(self, raw_quote: dict, raw_charges: list[dict]) -> QuoteSchema:
        basic_ocean_freight = 0.0
        included_freight_surcharges = []
        excluded_charges = []
        
        from models.schemas import ChargeSchema
        
        # Specified surcharges to include in final value
        INCLUDED_SURCHARGES = {
            "EU INNOVATION SURCHARGE (EUIS)",
            "IMO SOX COMPLIANCE CHARGE (ISOCC)",
            "LOW SULPHUR SURCHARGE (LSS)",
            "EU ENTRY SUMMARY DECLARATION CHARGE (ENS)",
            "E BOOKING FEE VIA GREENX (EBKF)"
        }
        
        for charge in raw_charges:
            name = charge["name"].strip()
            name_upper = name.upper()
            amount = charge["amount"]
            currency = charge["currency"]
            
            # Determine category
            category = "ORIGIN_CHARGE_EXCLUDED"
            if name_upper == "BASIC OCEAN FREIGHT":
                category = "BASIC_OCEAN_FREIGHT"
            elif name_upper in INCLUDED_SURCHARGES:
                category = "FREIGHT_SURCHARGE_INCLUDED"
                
            c_schema = ChargeSchema(
                name=name,
                amount=amount,
                currency=currency,
                category=category
            )
            
            if name_upper == "BASIC OCEAN FREIGHT":
                basic_ocean_freight = amount
            elif name_upper in INCLUDED_SURCHARGES:
                included_freight_surcharges.append(c_schema)
            else:
                excluded_charges.append(c_schema)
                
        # Fallback to total_price if no breakdown was found
        if basic_ocean_freight == 0.0 and not included_freight_surcharges and raw_quote.get("total_price"):
            basic_ocean_freight = raw_quote["total_price"]
            
        final_value = basic_ocean_freight + sum(c.amount for c in included_freight_surcharges)
        
        vessel = raw_quote.get("vessel_voyage") or raw_quote.get("vessel")
        if raw_quote.get("detailed_vessel"):
            # Clean up voyage number if present in vessel_voyage
            voyage_num = ""
            if vessel:
                v_parts = vessel.split()
                if v_parts:
                    voyage_num = v_parts[-1]
            vessel = f"{raw_quote['detailed_vessel']}"
            if voyage_num:
                vessel = f"{vessel} (Voy: {voyage_num})"
            
        return QuoteSchema(
            etd=raw_quote.get("etd_standardized"),
            eta=raw_quote.get("eta_standardized"),
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
            raw_reference=raw_quote.get("raw_reference")
        )

    async def close(self):
        await super().close()
        try:
            if self.playwright:
                await self.playwright.stop()
        except:
            pass
