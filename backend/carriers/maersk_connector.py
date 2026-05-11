"""
Maersk Live Connector — Playwright automation for Maersk booking portal.

Portal URL: https://www.maersk.com/book/
Account: INFREIGHT LOGISTICS PTE LTD
Credentials read from env: MAERSK_USERNAME, MAERSK_PASSWORD
Never hardcode credentials.
"""
import os
import re
from datetime import datetime
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout
from models.schemas import RateSearchRequest, QuoteSchema, CarrierResultStatus
from carriers.base_connector import BaseCarrierConnector


# ────────────────────────────────────────────
# Constants
# ────────────────────────────────────────────

LOGIN_URL = "https://www.maersk.com/portaluser/login"
BOOKING_URL = "https://www.maersk.com/book/"

CONTAINER_TYPE_MAP = {
    "DRY 20":     "20' Standard",
    "DRY 40":     "40' Standard",
    "DRY 40H":    "40' High Cube",
    "REEFER 20":  "20' Reefer",
    "REEFER 40":  "40' Reefer",
    "REEFER 40H": "40' Reefer High",
}

MAERSK_SECTION_CLASSIFICATION = {
    "Freight charges":      "FREIGHT",
    "Origin charges":       "ORIGIN",
    "Destination charges":  "DESTINATION",
}


class MaerskConnector(BaseCarrierConnector):
    carrier_code = "MAERSK"
    carrier_name = "Maersk"

    def __init__(self):
        super().__init__()
        self.playwright = None
        self._all_quote_cards: list[dict] = []

    # ────────────────────────────────────────
    # Browser helpers
    # ────────────────────────────────────────

    async def _init_browser(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"],
        )
        self.context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
            ),
        )
        self.page = await self.context.new_page()
        self.page.set_default_timeout(30_000)

    async def _safe_click(self, selector: str, timeout: int = 10_000):
        """Wait for element, scroll into view, then click."""
        el = self.page.locator(selector).first
        await el.wait_for(state="visible", timeout=timeout)
        await el.scroll_into_view_if_needed()
        await el.click()

    async def _fill_typeahead(self, input_selector: str, text: str):
        """
        Fill a type-ahead input: type text, wait for dropdown, select first match.
        Used for both Origin and Destination fields.
        """
        field = self.page.locator(input_selector).first
        await field.wait_for(state="visible", timeout=15_000)
        await field.click()
        await field.fill("")
        await field.type(text, delay=80)
        # Wait for dropdown suggestions to appear
        dropdown = self.page.locator(
            '[class*="suggestion"], [class*="dropdown-item"], '
            '[class*="autocomplete"] li, [role="option"], [role="listbox"] li'
        ).first
        await dropdown.wait_for(state="visible", timeout=10_000)
        await dropdown.click()
        await self.page.wait_for_timeout(500)

    # ────────────────────────────────────────
    # STEP 1 — LOGIN
    # ────────────────────────────────────────

    async def login(self) -> bool:
        username = os.getenv("MAERSK_USERNAME")
        password = os.getenv("MAERSK_PASSWORD")
        if not username or not password:
            print("[MAERSK] ERROR: Credentials not set in environment")
            return False
        try:
            await self._init_browser()
            print("[MAERSK] Navigating to login page...")
            await self.page.goto(LOGIN_URL, wait_until="domcontentloaded", timeout=30_000)
            print(f"[MAERSK] Initial page loaded: {self.page.url}")
            await self.page.wait_for_timeout(1000)
            
            # Wait for OAuth redirect to accounts.maersk.com
            print("[MAERSK] Waiting for OAuth redirect to accounts.maersk.com...")
            try:
                await self.page.wait_for_url(lambda url: "accounts.maersk.com" in url, timeout=10_000)
                print(f"[MAERSK] OAuth redirect successful: {self.page.url}")
                # Wait for OAuth page to fully load and render form
                await self.page.wait_for_timeout(3000)
                print("[MAERSK] OAuth page waiting for content to load...")
            except Exception as e:
                print(f"[MAERSK] OAuth redirect failed or timed out: {e}")
                print(f"[MAERSK] Current URL: {self.page.url}")
                return False
            
            # Now fill credentials on OAuth page
            email_sel = 'input[type="email"], input[name="email"], input[id="email"], input[name="username"], input[id="username"]'
            pwd_sel = 'input[type="password"], input[name="password"], input[id="password"]'
            
            print(f"[MAERSK] Looking for email input on OAuth page...")
            try:
                await self.page.wait_for_selector(email_sel, timeout=15_000)
                print("[MAERSK] Email input found, filling...")
                email_field = self.page.locator(email_sel).first
                await email_field.click()
                await email_field.clear()
                await email_field.type(username, delay=50)
                print(f"[MAERSK] Email filled: {username}")
            except Exception as e:
                print(f"[MAERSK] Email input not found: {e}")
                return False

            print("[MAERSK] Looking for password input...")
            try:
                await self.page.wait_for_selector(pwd_sel, timeout=10_000)
                pwd_field = self.page.locator(pwd_sel).first
                await pwd_field.click()
                await pwd_field.clear()
                await pwd_field.type(password, delay=50)
                print("[MAERSK] Password filled")
            except Exception as e:
                print(f"[MAERSK] Password input not found: {e}")
                return False

            # Submit
            submit_sel = 'button[type="submit"], button:has-text("Log in"), button:has-text("Sign in")'
            print("[MAERSK] Clicking submit button...")
            try:
                await self.page.locator(submit_sel).first.click()
                print("[MAERSK] Submit button clicked")
            except Exception as e:
                print(f"[MAERSK] Failed to click submit button: {e}")
                return False
            
            print("[MAERSK] Waiting for navigation after submit (checking for OAuth or booking page)...")
            try:
                # Wait for page to navigate away from login
                await self.page.wait_for_url(
                    lambda url: "login" not in url.lower() and "auth/login" not in url.lower(),
                    timeout=15_000
                )
                print(f"[MAERSK] Navigation successful! Current URL: {self.page.url}")
                await self.page.wait_for_timeout(2000)  # Extra wait for page to fully load
                return True
            except Exception as e:
                print(f"[MAERSK] Navigation timeout: {e}")
                current_url = self.page.url
                print(f"[MAERSK] Current URL: {current_url}")
                
                # Check for error messages
                try:
                    page_html = await self.page.content()
                    if "invalid" in page_html.lower():
                        print("[MAERSK] INVALID credentials message found")
                    if "error" in page_html.lower():
                        print("[MAERSK] ERROR message found in page")
                    if "denied" in page_html.lower():
                        print("[MAERSK] ACCESS DENIED message found")
                except:
                    pass
                
                if "login" in current_url.lower() or "auth/login" in current_url.lower():
                    print("[MAERSK] Still on login/OAuth page, login failed")
                    return False
                else:
                    print("[MAERSK] URL suggests login succeeded")
                    return True

            if "login" in self.page.url.lower():
                print("[MAERSK] Login failed — still on login page")
                return False

            # Navigate to booking page post-login
            print("[MAERSK] Login successful, navigating to /book/...")
            await self.page.goto(BOOKING_URL, wait_until="networkidle", timeout=60_000)
            print("[MAERSK] Booking page loaded")
            return True

        except Exception as e:
            print(f"[MAERSK] Login failed: {e}")
            return False

    # ────────────────────────────────────────
    # STEPS 2–7 — FILL SEARCH FORM
    # ────────────────────────────────────────

    async def search_quotes(self, request: RateSearchRequest) -> CarrierResultStatus:
        try:
            print("[MAERSK] Filling search form...")

            # STEP 2 — Origin (type-ahead)
            origin_sel = (
                'input[placeholder*="origin" i], input[placeholder*="from" i], '
                'input[aria-label*="origin" i], input[aria-label*="from" i], '
                'input[data-testid*="origin"], input[name*="origin"]'
            )
            await self._fill_typeahead(origin_sel, request.origin)
            print(f"[MAERSK] Origin set: {request.origin}")

            # STEP 3 — Destination (type-ahead)
            dest_sel = (
                'input[placeholder*="destination" i], input[placeholder*="to" i], '
                'input[aria-label*="destination" i], input[aria-label*="to" i], '
                'input[data-testid*="destination"], input[name*="destination"]'
            )
            await self._fill_typeahead(dest_sel, request.destination)
            print(f"[MAERSK] Destination set: {request.destination}")

            # STEP 4 — Container type
            maersk_container = CONTAINER_TYPE_MAP.get(
                request.container_type, "40' High Cube"
            )
            container_dropdown = self.page.locator(
                'select[name*="container" i], [class*="container-type"] select, '
                '[data-testid*="container"] select, '
                'button:has-text("container type"), [aria-label*="container type" i]'
            ).first
            try:
                tag = await container_dropdown.evaluate("el => el.tagName.toLowerCase()")
                if tag == "select":
                    await container_dropdown.select_option(label=maersk_container)
                else:
                    await container_dropdown.click()
                    await self.page.locator(
                        f'[role="option"]:has-text("{maersk_container}"), '
                        f'li:has-text("{maersk_container}")'
                    ).first.click()
            except Exception:
                print(f"[MAERSK] Container type selector fallback for: {maersk_container}")
            print(f"[MAERSK] Container type set: {maersk_container}")

            # STEP 5 — Price owner: verify "I am the price owner" is selected
            price_owner_radio = self.page.locator(
                'input[type="radio"][value*="self" i], '
                'input[type="radio"]:near(:text("I am the price owner")), '
                'label:has-text("I am the price owner") input[type="radio"]'
            ).first
            try:
                is_checked = await price_owner_radio.is_checked()
                if not is_checked:
                    await price_owner_radio.check()
                print("[MAERSK] Price owner: 'I am the price owner' confirmed")
            except Exception:
                print("[MAERSK] Price owner radio not found — may be default, continuing")

            # STEP 6 — Service term: verify CY is selected
            cy_sel = (
                'input[type="radio"][value*="CY" i], '
                'label:has-text("CY") input[type="radio"], '
                'button:has-text("CY")[aria-pressed], [data-testid*="cy" i]'
            )
            try:
                cy_radio = self.page.locator(cy_sel).first
                is_checked = await cy_radio.is_checked()
                if not is_checked:
                    await cy_radio.check()
                print("[MAERSK] Service term: CY confirmed")
            except Exception:
                print("[MAERSK] CY radio not found — may be default, continuing")

            # STEP 7 — Departure date: click "Tomorrow" button
            tomorrow_sel = (
                'button:has-text("Tomorrow"), '
                '[data-testid*="tomorrow" i], '
                'label:has-text("Tomorrow")'
            )
            try:
                await self._safe_click(tomorrow_sel, timeout=10_000)
                print("[MAERSK] Departure date: Tomorrow selected")
            except Exception:
                print("[MAERSK] 'Tomorrow' button not found — date may already be set")

            # Wait for results to auto-populate in right panel
            print("[MAERSK] Waiting for 'Spot and market rates' panel...")
            await self.page.wait_for_selector(
                '[class*="spot"], [class*="rate-card"], [class*="offer-card"], '
                ':text("Spot and market rates"), [data-testid*="rate-result"]',
                timeout=30_000,
            )
            await self.page.wait_for_timeout(2_000)
            print("[MAERSK] Results panel loaded")
            return CarrierResultStatus.AVAILABLE_QUOTES_FOUND

        except PlaywrightTimeout:
            print("[MAERSK] Search timed out waiting for results")
            return CarrierResultStatus.TIMEOUT
        except Exception as e:
            print(f"[MAERSK] Search failed: {e}")
            return CarrierResultStatus.UNKNOWN_ERROR

    # ────────────────────────────────────────
    # STEP 8 — READ RESULTS (with pagination)
    # ────────────────────────────────────────

    async def extract_quote_list(self) -> list[dict]:
        try:
            self._all_quote_cards = []
            page_num = 0

            while True:
                page_num += 1
                # Locate result cards on current page
                card_sel = (
                    '[class*="offer-card"], [class*="rate-card"], '
                    '[class*="result-card"], [class*="spot-rate"]'
                )
                cards = self.page.locator(card_sel)
                count = await cards.count()
                print(f"[MAERSK] Page {page_num}: {count} card(s)")

                for i in range(count):
                    card = cards.nth(i)
                    card_text = await card.text_content() or ""

                    # Parse date (e.g. "14 MAY")
                    date_match = re.search(r'(\d{1,2}\s+[A-Z]{3})', card_text)
                    raw_date = date_match.group(1) if date_match else None

                    # Parse price (e.g. "4,335 USD")
                    price_match = re.search(r'([\d,]+)\s*(USD|EUR|SGD)', card_text)
                    raw_price = price_match.group(1).replace(",", "") if price_match else None
                    raw_currency = price_match.group(2) if price_match else "USD"

                    global_idx = len(self._all_quote_cards)
                    self._all_quote_cards.append({
                        "index": global_idx,
                        "page": page_num,
                        "card_text": card_text.strip()[:200],
                        "raw_date": raw_date,
                        "raw_all_inclusive_price": raw_price,
                        "etd": None,
                        "eta": None,
                        "transit_time_days": None,
                        "service_name": None,
                        "vessel": None,
                        "voyage": None,
                        "service_code": None,
                        "gate_in_deadline": None,
                        "container_type": None,
                        "container_quantity": None,
                        "currency": raw_currency,
                        "source": "carrier_portal",
                        "raw_reference": None,
                    })

                # Pagination: try clicking Next
                next_btn = self.page.locator(
                    'button:has-text("Next"), button[aria-label*="next" i], '
                    '[class*="pagination"] button:last-child'
                ).first
                try:
                    is_disabled = await next_btn.is_disabled()
                    if is_disabled:
                        break
                    await next_btn.click()
                    await self.page.wait_for_timeout(1_500)
                except Exception:
                    break  # No more pages

            print(f"[MAERSK] Total quotes collected: {len(self._all_quote_cards)}")
            return self._all_quote_cards

        except Exception as e:
            print(f"[MAERSK] Error extracting quote list: {e}")
            return []

    # ────────────────────────────────────────
    # STEP 9 — OPEN PRICE DETAILS
    # ────────────────────────────────────────

    async def open_price_breakdown(self, quote_ref: dict) -> bool:
        try:
            idx = quote_ref.get("index", 0)
            print(f"[MAERSK] Opening price details for card #{idx + 1}...")

            # Click "Price details" button on the card
            detail_btns = self.page.locator(
                'button:has-text("Price details"), '
                'button:has-text("price details"), '
                'a:has-text("Price details")'
            )
            btn_count = await detail_btns.count()
            if btn_count == 0:
                print("[MAERSK] No 'Price details' buttons found")
                return False

            # Use modulo in case pagination reset the visible index
            visible_idx = idx % max(btn_count, 1)
            await detail_btns.nth(visible_idx).click()
            await self.page.wait_for_timeout(2_000)

            # Extract metadata from the detail panel
            detail_panel = self.page.locator(
                '[class*="detail-panel"], [class*="price-detail"], '
                '[class*="offer-detail"], [class*="modal"], [role="dialog"]'
            ).first

            panel_text = await detail_panel.text_content() or ""

            # Extract transit time
            transit_match = re.search(r'(\d+)\s*(?:days?|d)\s*(?:transit)?', panel_text, re.I)
            if transit_match:
                quote_ref["transit_time_days"] = int(transit_match.group(1))

            # Extract vessel name
            vessel_match = re.search(r'(?:Vessel|Ship)[:\s]*([A-Za-z\s]+?)(?:\s*\/|\s*\n|$)', panel_text)
            if vessel_match:
                quote_ref["vessel"] = vessel_match.group(1).strip()

            # Extract service code (e.g. A05)
            svc_match = re.search(r'(?:Service|Route)[:\s]*([A-Z0-9]{2,6})', panel_text)
            if svc_match:
                quote_ref["service_code"] = svc_match.group(1)
                quote_ref["service_name"] = svc_match.group(1)

            # Extract offer ID
            offer_match = re.search(r'(P_\w+)', panel_text)
            if offer_match:
                quote_ref["raw_reference"] = offer_match.group(1)
            else:
                quote_ref["raw_reference"] = f"MAERSK-LIVE-{idx + 1}"

            print(f"[MAERSK] Detail panel loaded — ref: {quote_ref.get('raw_reference')}")
            return True

        except Exception as e:
            print(f"[MAERSK] Error opening price breakdown: {e}")
            return False

    # ────────────────────────────────────────
    # STEPS 10–11 — BREAKDOWN TAB + CHARGE EXTRACTION
    # ────────────────────────────────────────

    async def extract_charge_breakdown(self) -> list[dict]:
        """
        Click the 'Breakdown' tab and extract charges with section awareness.

        Maersk's Breakdown tab uses explicit section headers:
          - "Freight charges"      → INCLUDE in final freight value
          - "Origin charges"       → EXCLUDE
          - "Destination charges"  → EXCLUDE

        Each charge row includes: name, basis, quantity, currency, unit price, total price.
        We tag each charge with its section for the Maersk-specific normalizer.
        """
        try:
            # STEP 10 — Click "Breakdown" tab
            breakdown_tab = self.page.locator(
                'button:has-text("Breakdown"), '
                '[role="tab"]:has-text("Breakdown"), '
                'a:has-text("Breakdown")'
            ).first
            await breakdown_tab.click()
            await self.page.wait_for_timeout(1_500)
            print("[MAERSK] Breakdown tab opened")

            # STEP 11 — Extract charges with section awareness
            charges = []
            current_section = "Unknown"

            # Get all rows in the breakdown table/list
            # Maersk uses section headers followed by charge rows
            all_rows = self.page.locator(
                '[class*="breakdown"] tr, [class*="breakdown"] [class*="row"], '
                '[class*="charge-table"] tr, [class*="price-breakdown"] tr, '
                '[class*="breakdown"] li, [class*="charge-line"]'
            )
            row_count = await all_rows.count()
            print(f"[MAERSK] Found {row_count} breakdown rows")

            for i in range(row_count):
                row = all_rows.nth(i)
                row_text = (await row.text_content() or "").strip()
                if not row_text:
                    continue

                # Check if this row is a section header
                matched_section = False
                for section_name in MAERSK_SECTION_CLASSIFICATION:
                    if section_name.lower() in row_text.lower():
                        current_section = section_name
                        matched_section = True
                        print(f"[MAERSK] Section: {current_section}")
                        break

                if matched_section:
                    continue

                # Parse charge row — try to extract amount and currency
                amount_match = re.search(
                    r'([\d,]+(?:\.\d{2})?)\s*(USD|EUR|SGD|GBP)?', row_text
                )
                if not amount_match:
                    continue

                # Extract all amounts — last one is typically "Total price"
                amounts = re.findall(r'([\d,]+(?:\.\d{2})?)', row_text)
                total_amount = float(amounts[-1].replace(",", "")) if amounts else 0.0

                # Currency
                currency_match = re.search(r'(USD|EUR|SGD|GBP)', row_text)
                currency = currency_match.group(1) if currency_match else "USD"

                # Charge name — text before the first number
                name_match = re.match(r'^([A-Za-z\s\-/()]+)', row_text)
                charge_name = name_match.group(1).strip() if name_match else row_text[:50]

                charges.append({
                    "name": charge_name,
                    "amount": total_amount,
                    "currency": currency,
                    "section": current_section,
                })

            print(f"[MAERSK] Extracted {len(charges)} charge line items")

            # Close the detail panel to go back to results
            await self._close_detail_panel()

            return charges

        except Exception as e:
            print(f"[MAERSK] Error extracting charge breakdown: {e}")
            await self._close_detail_panel()
            return []

    # ────────────────────────────────────────
    # Close detail panel
    # ────────────────────────────────────────

    async def _close_detail_panel(self):
        """Close the price detail panel to return to the results list."""
        try:
            close_btn = self.page.locator(
                'button[aria-label*="close" i], button[aria-label*="back" i], '
                'button:has-text("Close"), button:has-text("Back"), '
                '[class*="close-button"], [class*="modal-close"]'
            ).first
            await close_btn.click()
            await self.page.wait_for_timeout(1_000)
        except Exception:
            # Try pressing Escape as fallback
            try:
                await self.page.keyboard.press("Escape")
                await self.page.wait_for_timeout(500)
            except Exception:
                pass

    # ────────────────────────────────────────
    # Normalize using Maersk section-based path
    # ────────────────────────────────────────

    async def normalize_result(self, raw_quote: dict, raw_charges: list[dict]) -> QuoteSchema:
        from services.normalizer import normalize_quote_maersk
        return normalize_quote_maersk(self.carrier_code, raw_quote, raw_charges)

    # ────────────────────────────────────────
    # Cleanup
    # ────────────────────────────────────────

    async def close(self):
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
        except Exception:
            pass
