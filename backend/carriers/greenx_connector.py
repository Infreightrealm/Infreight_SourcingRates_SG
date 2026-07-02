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

            # 3. Fill container quantity boxes: 20' SD, 40' SD, 40' SH to 1 for all 3
            # so we can fetch all container size rates in a single page load.
            qty_20_sd = 1
            qty_40_sd = 1
            qty_40_sh = 1

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
                # Match links as well as buttons — GreenX renders the detail tabs as <a>
                # links; the button-only selector found 0 cards and reported "No Quotes"
                # even though results were visibly loaded (search_quotes already accepts both).
                card_buttons = self.page.locator('button:has-text("Route Details"):visible, a:has-text("Route Details"):visible')
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
            
            route_details_locs = self.page.locator('button:has-text("Route Details"):visible, a:has-text("Route Details"):visible')
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

    async def _click_detail_tab(self, card, tab_text: str, verify_text: str = None) -> bool:
        try:
            btn = card.locator(f'button:has-text("{tab_text}"), a:has-text("{tab_text}"), :text("{tab_text}")').first
            try:
                await btn.wait_for(state="attached", timeout=2000)
            except Exception:
                pass
            
            await btn.scroll_into_view_if_needed()
            
            # Try to click up to 3 times if verify_text is provided and not seen
            for attempt in range(3):
                text_before = await card.inner_text()
                
                # Click with JS fallback
                try:
                    await btn.click(timeout=3000)
                except Exception as ce:
                    print(f"[GreenX] Standard click on {tab_text} failed: {ce}. Retrying via JS click...")
                    try:
                        await btn.evaluate("el => el.click()")
                    except Exception as je:
                        print(f"[GreenX] JS click on {tab_text} failed: {je}")
                        if attempt == 2:
                            return False
                
                # If verify_text is provided, wait until it appears in the card
                if verify_text:
                    success = False
                    for _ in range(15):
                        await self.page.wait_for_timeout(200)
                        try:
                            current_text = await card.inner_text()
                            if verify_text in current_text:
                                success = True
                                break
                        except Exception:
                            break
                    if success:
                        return True
                    print(f"[GreenX] Warning: verify_text '{verify_text}' not found after clicking {tab_text} (attempt {attempt + 1}/3). Retrying click...")
                    await self.page.wait_for_timeout(500)
                else:
                    # Generic wait for any text change
                    for _ in range(15):
                        await self.page.wait_for_timeout(200)
                        try:
                            text_after = await card.inner_text()
                            if text_after != text_before:
                                return True
                        except Exception:
                            break
                    return True
            
            return False
        except Exception as e:
            print(f"[GreenX] Error clicking {tab_text} tab: {e}")
            return False

    async def open_price_breakdown(self, quote_ref: dict) -> bool:
        try:
            card = quote_ref["card_locator"]
            
            # 1. Route Details
            print(f"[GreenX] Opening Route Details for card {quote_ref['index']}...")
            if await self._click_detail_tab(card, "Route Details", verify_text="POL"):
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
            if await self._click_detail_tab(card, "Price Details", verify_text="Prepaid Charges"):
                price_text = await card.inner_text()
                charges = []
                
                # Regex for matching line item charge name, its container type, and its price
                pattern = r"(.+?)\s+(20'\s*Standard\s*Dry|40'\s*Standard\s*Dry|40'\s*High\s*Cube|Per\s*B/L|20'\s*SD|40'\s*SD|40'\s*SH)\s+x\s*\d+\s+USD\s*([\d,]+\.\d{2})"
                matches = re.findall(pattern, price_text)
                
                for name_raw, type_raw, amount_str in matches:
                    name = name_raw.strip()
                    name = re.sub(r'^\s*\d+\s+', '', name) # Strip numbers
                    ct_type = type_raw.strip()
                    amount = float(amount_str.replace(",", ""))
                    charges.append({
                        "name": name,
                        "container_type": ct_type,
                        "amount": amount,
                        "currency": "USD"
                    })
                    if os.getenv("GREENX_DEBUG", "").lower() == "true":
                        print(f"[GreenX] Parsed charge row: {name} ({ct_type}) = USD {amount}")
                
                quote_ref["charges"] = charges
                self.current_charges = charges

            # 3. Free Time
            print(f"[GreenX] Opening Free Time details for card {quote_ref['index']}...")
            if await self._click_detail_tab(card, "Free Time", verify_text="Tariff Free Time"):
                free_time_text = await card.inner_text()
                if "Tariff Free Time at Destination" in free_time_text:
                    dest_part = free_time_text.split("Tariff Free Time at Destination")[1]
                    # We report DESTINATION free time only — never origin. Cut off any
                    # "Tariff Free Time at Origin" section that might follow so origin
                    # components (e.g. PSA Singapore's Detention/Demurrage) can't leak in.
                    dest_part = re.split(r"Tariff Free Time at Origin", dest_part, flags=re.IGNORECASE)[0]
                    # Preference: use "Container Detention" when the terminal lists it.
                    # If there is no Detention line (e.g. GATEWAY TERMINALS INDIA at Nhava
                    # Sheva only shows "Container Usage"), fall back to the COMBINED days —
                    # the sum of the other free-time components shown at destination.
                    det = re.search(
                        r"Container\s+Detention\s*[\r\n]*\s*(\d+)\s+Calendar\s+Days",
                        dest_part, re.IGNORECASE)
                    if det:
                        quote_ref["free_time"] = int(det.group(1))
                    else:
                        others = re.findall(
                            r"Container\s+(?:Usage|Demurrage|Storage|Combined)\s*[\r\n]*\s*(\d+)\s+Calendar\s+Days",
                            dest_part, re.IGNORECASE)
                        if others:
                            quote_ref["free_time"] = sum(int(x) for x in others)
                    if quote_ref.get("free_time") is not None and os.getenv("GREENX_DEBUG", "").lower() == "true":
                        print(f"[GreenX] Extracted destination free time: {quote_ref['free_time']} days "
                              f"({'detention' if det else 'combined'})")
            
            return True
        except Exception as e:
            print(f"[GreenX] Error opening price breakdown: {e}")
            return False

    async def extract_charge_breakdown(self) -> list[dict]:
        return self.current_charges

    def _split_raw_quote_by_container_types(self, raw_quote: dict, raw_charges: list[dict]) -> list[QuoteSchema]:
        """
        Splits a single raw multi-container quote card into multiple QuoteSchema objects,
        one for each standard container type that has pricing.
        """
        mapping = {
            "20' Standard Dry": "DRY 20",
            "20' SD": "DRY 20",
            "40' Standard Dry": "DRY 40",
            "40' SD": "DRY 40",
            "40' High Cube": "DRY 40H",
            "40' SH": "DRY 40H"
        }

        # 1. Separate container-specific charges from flat (Per B/L) charges
        container_charges = {
            "DRY 20": [],
            "DRY 40": [],
            "DRY 40H": []
        }
        flat_charges = []

        for charge in raw_charges:
            ct_raw = charge.get("container_type", "")
            mapped_ct = mapping.get(ct_raw)
            if mapped_ct:
                container_charges[mapped_ct].append(charge)
            else:
                flat_charges.append(charge)

        # Whitelist of surcharges to fold into the final freight value. These are
        # taken whether GreenX bills them per-container (EUIS / ISOCC / LSS) or
        # per-B/L (ENS / EBKF), and ONLY when billed in USD. Per-B/L charges are
        # added in full to every container size below (e.g. a $10 ENS adds $10 to
        # each size's total), matching how GreenX bills them once per booking.
        INCLUDED_SURCHARGES = {
            "EU INNOVATION SURCHARGE (EUIS)",
            "IMO SOX COMPLIANCE CHARGE (ISOCC)",
            "LOW SULPHUR SURCHARGE (LSS)",
            "EU ENTRY SUMMARY DECLARATION CHARGE (ENS)",
            "E BOOKING FEE VIA GREENX (EBKF)",
        }

        def _categorize(name: str, currency: str) -> str:
            name_u = " ".join((name or "").upper().split())
            if name_u == "BASIC OCEAN FREIGHT":
                return "BASIC_OCEAN_FREIGHT"
            if name_u in INCLUDED_SURCHARGES and (currency or "").upper() == "USD":
                return "FREIGHT_SURCHARGE_INCLUDED"
            return "ORIGIN_CHARGE_EXCLUDED"

        # 2. For each container type that has at least one charge (specifically, Basic Ocean Freight)
        split_quotes = []
        for std_ct, c_charges in container_charges.items():
            # Check if there is Basic Ocean Freight for this type
            bof_charge = next((c for c in c_charges if c["name"].upper() == "BASIC OCEAN FREIGHT"), None)
            if not bof_charge:
                continue  # This container size is not available/N/A

            # Build raw_charges list for this container type:
            # Combine the container-specific charges and flat (Per B/L) charges
            split_raw_charges = []
            for c in c_charges:
                split_raw_charges.append({
                    "name": c["name"],
                    "amount": c["amount"],
                    "currency": c["currency"],
                    "category": _categorize(c["name"], c.get("currency")),
                })
            for f in flat_charges:
                split_raw_charges.append({
                    "name": f["name"],
                    "amount": f["amount"],
                    "currency": f["currency"],
                    "category": _categorize(f["name"], f.get("currency")),
                })

            # Create a localized raw_quote dict with the correct container type
            local_raw_quote = raw_quote.copy()
            local_raw_quote["container_type"] = std_ct

            # Use normalize_result (or local normalization) to create QuoteSchema
            from models.schemas import ChargeSchema
            from services.normalizer import standardize_date_string
            
            basic_ocean_freight = bof_charge["amount"]
            included_surcharges = []
            excluded_charges = []
            
            for src in split_raw_charges:
                cs = ChargeSchema(
                    name=src["name"],
                    amount=src["amount"],
                    currency=src["currency"],
                    category=src["category"]
                )
                if src["name"].upper() == "BASIC OCEAN FREIGHT":
                    pass  # Already handled
                elif src["category"] == "FREIGHT_SURCHARGE_INCLUDED":
                    included_surcharges.append(cs)
                else:
                    excluded_charges.append(cs)

            final_value = basic_ocean_freight + sum(c.amount for c in included_surcharges)

            vessel = local_raw_quote.get("vessel_voyage") or local_raw_quote.get("vessel")
            if local_raw_quote.get("detailed_vessel"):
                voyage_num = ""
                if vessel:
                    v_parts = vessel.split()
                    if v_parts:
                        voyage_num = v_parts[-1]
                vessel = f"{local_raw_quote['detailed_vessel']}"
                if voyage_num:
                    vessel = f"{vessel} (Voy: {voyage_num})"

            # For the unique reference, append container type to avoid duplicate DB keys
            raw_ref = local_raw_quote.get("raw_reference", "GREENX")
            unique_ref = f"{raw_ref}-{std_ct.replace(' ', '_')}"

            quote_schema = QuoteSchema(
                etd=local_raw_quote.get("etd_standardized"),
                eta=local_raw_quote.get("eta_standardized"),
                transit_time_days=local_raw_quote.get("transit_time_days"),
                routing=local_raw_quote.get("routing", "Direct"),
                free_time=local_raw_quote.get("free_time"),
                service_name=local_raw_quote.get("service_name"),
                vessel=vessel,
                currency=local_raw_quote.get("currency", "USD"),
                container_type=std_ct,
                basic_ocean_freight=basic_ocean_freight,
                included_freight_surcharges=included_surcharges,
                excluded_charges=excluded_charges,
                final_freight_value=round(final_value, 2),
                source="carrier_portal",
                raw_reference=unique_ref
            )
            split_quotes.append(quote_schema)

        return split_quotes

    async def run_full_search(self, request: RateSearchRequest) -> tuple[CarrierResultStatus, list[QuoteSchema]]:
        """
        Overrides base search runner to query all 3 sizes at once and cache the resulting quotes
        across sequential container type cycles to save time.
        """
        if not hasattr(self, "_cached_quotes"):
            self._cached_quotes = None
            self._cached_status = None

        if self._cached_quotes is not None:
            print(f"[GreenX] Returning cached quotes for '{request.container_type}' (avoiding redundant browser search).")
            matching_quotes = [q for q in self._cached_quotes if q.container_type == request.container_type]
            return self._cached_status, matching_quotes

        quotes: list[QuoteSchema] = []
        try:
            # Step 1: Login
            login_ok = await self.login()
            if not login_ok:
                self._cached_quotes = []
                self._cached_status = CarrierResultStatus.LOGIN_FAILED
                return CarrierResultStatus.LOGIN_FAILED, []

            # Step 2: Search quotes (always searches 20' SD, 40' SD, and 40' SH with quantity 1)
            search_status = await self.search_quotes(request)
            if search_status != CarrierResultStatus.AVAILABLE_QUOTES_FOUND:
                self._cached_quotes = []
                self._cached_status = search_status
                return search_status, []

            # Step 3: Extract quote list
            raw_quotes = await self.extract_quote_list()
            if not raw_quotes:
                self._cached_quotes = []
                self._cached_status = CarrierResultStatus.NO_QUOTES_AVAILABLE
                return CarrierResultStatus.NO_QUOTES_AVAILABLE, []

            # Step 4: For each quote, get breakdown, extract, and split
            for raw_quote in raw_quotes:
                try:
                    opened = await self.open_price_breakdown(raw_quote)
                    raw_charges = []
                    if opened:
                        raw_charges = await self.extract_charge_breakdown()
                        
                    split_quotes = self._split_raw_quote_by_container_types(raw_quote, raw_charges)
                    quotes.extend(split_quotes)
                except Exception as e:
                    print(f"[GreenX] Error extracting quote: {e}")
                    continue

            self._cached_quotes = quotes
            self._cached_status = CarrierResultStatus.AVAILABLE_QUOTES_FOUND if quotes else CarrierResultStatus.EXTRACTION_FAILED
            
            # Filter and return quotes matching current request container type
            matching_quotes = [q for q in quotes if q.container_type == request.container_type]
            return self._cached_status, matching_quotes

        except Exception as e:
            print(f"[GreenX] Unexpected error in run_full_search: {e}")
            return CarrierResultStatus.UNKNOWN_ERROR, []

    async def normalize_result(self, raw_quote: dict, raw_charges: list[dict]) -> QuoteSchema:
        # Keep fallback method signature just in case
        return QuoteSchema()

    async def close(self):
        await super().close()
        try:
            if self.playwright:
                await self.page.close()
                await self.context.close()
                await self.browser.close()
                await self.playwright.stop()
        except:
            pass
