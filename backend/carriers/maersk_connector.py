"""
Maersk Browser Connector — Playwright automation using your real Google Chrome browser.
Includes Human-in-the-Loop (HITL) bypasses and optional Bright Data proxy support.
"""
import os
import re
import random
import asyncio
from datetime import date, datetime, timedelta
from dotenv import load_dotenv
from patchright.async_api import async_playwright
from models.schemas import RateSearchRequest, QuoteSchema, CarrierResultStatus
from services.charge_classifier import classify_charge
from services.normalizer import normalize_quote
from services.port_manager import resolve_port_for_carrier, get_carrier_search_query, get_cached_carrier_port, set_cached_carrier_port
from carriers.base_connector import BaseCarrierConnector

from typing import Optional
# Load environment variables from .env
load_dotenv()

# Map container types to Maersk size descriptions
SIZE_TYPE_MAP = {
    "DRY 20": "20' Dry Van",
    "DRY 40": "40' Dry Van",
    "DRY 40H": "40' High Cube Dry",
    "REEFER 20": "20' Reefer",
    "REEFER 40": "40' Reefer",
    "REEFER 40H": "40' High Cube Reefer",
    "DRY 45": "45' High Cube Dry",
}

COUNTRY_CODE_TO_NAME = {
    "MA": "Morocco",
    "CL": "Chile",
    "MY": "Malaysia",
    "VN": "Vietnam",
    "SG": "Singapore",
    "DE": "Germany",
    "IN": "India",
    "CN": "China",
    "US": "United States",
    "GB": "United Kingdom",
    "FR": "France",
    "ES": "Spain",
    "IT": "Italy",
    "NL": "Netherlands",
    "BE": "Belgium",
    "BR": "Brazil",
    "AR": "Argentina",
    "MX": "Mexico",
    "ZA": "South Africa",
    "JP": "Japan",
    "KR": "South Korea",
    "TW": "Taiwan",
    "HK": "Hong Kong",
    "AE": "United Arab Emirates",
    "SA": "Saudi Arabia",
    "TR": "Turkey",
    "EG": "Egypt",
    "TH": "Thailand",
    "ID": "Indonesia",
    "PH": "Philippines",
    "PK": "Pakistan",
    "BD": "Bangladesh",
    "LK": "Sri Lanka",
    "RU": "Russia",
    "AU": "Australia",
    "NZ": "New Zealand",
    "CA": "Canada",
}

def extract_locode_and_country(text: str) -> tuple[Optional[str], Optional[str]]:
    """Extracts LOCODE and country name from text like 'CASABLANCA, MOROCCO (MACAS)'."""
    if not text:
        return None, None
    
    locode = None
    country_name = None
    
    # 1. Try to extract UN/LOCODE from the text
    paren_match = re.search(r'\(\s*([A-Za-z]{2})\s*([A-Za-z]{3})\s*\)', text)
    if paren_match:
        locode = (paren_match.group(1) + paren_match.group(2)).upper()
        
    # 2. Try to extract country name
    parts = text.split(',')
    if len(parts) > 1:
        c_part = parts[-1].strip()
        c_part = re.sub(r'\s*\([^)]*\)', '', c_part).strip()
        if c_part:
            country_name = c_part
            
    return locode, country_name



class MaerskConnector(BaseCarrierConnector):
    carrier_code = "MAERSK"
    carrier_name = "Maersk Spot"
    BASE_URL = "https://www.maersk.com/hub/"
    QUOTE_URL = "https://www.maersk.com/book/"

    def __init__(self):
        super().__init__()
        self.playwright = None
        self.current_card = None
        self.temp_profile_dir = None
        self.master_profile_dir = None
        self.is_login_successful = False

    # ────────────────────────────────────────
    # DYNAMIC SEARCH ENGINE OVERRIDE
    # ────────────────────────────────────────

    async def run_full_search(self, request: RateSearchRequest) -> tuple[CarrierResultStatus, list[QuoteSchema]]:
        """
        Execute the full search flow with Progressive Lazy Loading:
        1. Login
        2. Search quotes
        3. Work on the positive return quotes of the currently visible batch first
        4. Scroll down to bottom to search for more sailing options
        5. Expand and repeat (up to 3 times)
        6. Return all normalized quotes
        """
        quotes: list[QuoteSchema] = []
        try:
            # Step 1: Login
            login_ok = await self.login()
            if not login_ok:
                return CarrierResultStatus.LOGIN_FAILED, []

            # Step 2: Search
            search_status = await self.search_quotes(request)
            if search_status != CarrierResultStatus.AVAILABLE_QUOTES_FOUND:
                return search_status, []

            # Step 3: Progressive Processing & Lazy Loading Loop
            processed_keys = set()
            max_expansions = 3
            
            for expansion in range(max_expansions + 1):
                # A. Quick check for "There are no sailings for your search" pink banner
                no_sailings_selectors = [
                    'text="There are no sailings for your search."',
                    'text="no sailings for your search"',
                    'text="changing the transportation mode (CY or SD)"',
                    '[class*="alert" i]:has-text("no sailings")',
                    '[class*="banner" i]:has-text("no sailings")',
                    '[class*="error" i]:has-text("no sailings")'
                ]
                
                no_sailings_detected = False
                for no_sail_sel in no_sailings_selectors:
                    try:
                        banner = self.page.locator(no_sail_sel).first
                        if await banner.is_visible(timeout=500):
                            print(f"[MAERSK] Zero quotes! Found 'No sailings' banner: '{no_sail_sel}'")
                            no_sailings_detected = True
                            break
                    except Exception:
                        continue
                        
                if no_sailings_detected:
                    print("[MAERSK] Halting automation. Maersk Spot explicitly reports no sailings are available.")
                    break
                    
                # B. Locate and count all cards currently visible on the page
                quote_cards = self.page.locator('article.new-sailings-card-article, article.sailings__card')
                count = await quote_cards.count()
                if count == 0:
                    quote_cards = self.page.locator('[class*="offer-card" i], [class*="result-card" i], [class*="schedule-card" i], .c-offer-card')
                    count = await quote_cards.count()
                if count == 0:
                    quote_cards = self.page.locator('.card, .result-row, [class*="card" i]')
                    count = await quote_cards.count()
                    
                print(f"[MAERSK] Processing batch: Found {count} cards on page (Expansion {expansion}/{max_expansions}).")
                
                new_cards_processed_in_this_batch = 0
                for index in range(count):
                    if len(quotes) >= 10:
                        print("[MAERSK] Already found 10 valid quotes. Stopping batch processing.")
                        break

                    card = quote_cards.nth(index)
                    
                    try:
                        # Scroll naturally to the card so the browser viewport follows us and lazy renders cleanly
                        await card.scroll_into_view_if_needed()
                        await self.page.wait_for_timeout(200)
                    except:
                        pass
                        
                    try:
                        card_text = (await card.inner_text(timeout=3000)).strip()
                    except Exception as card_e:
                        print(f"[MAERSK] Warning: Failed to get card text at index {index}: {card_e}")
                        continue
                    card_text_lower = card_text.lower()

                    # Skip non-root elements (which lack departure/arrival grid headers)
                    if "departure" not in card_text_lower or "arrival" not in card_text_lower:
                        continue
                    
                    # --- BULLETPROOF DETAIL PARSER ---
                    # Normalize whitespace and split into lines to support both vertical/grid and horizontal layouts
                    lines = [line.strip() for line in card_text.splitlines() if line.strip()]
                    
                    etd = ""
                    eta = ""
                    transit_time = 20
                    vessel_name = "Maersk Vessel"
                    freetime_text = ""
                    
                    # 1. Line-by-line / label-based grid extraction
                    for idx, line in enumerate(lines):
                        lower_line = line.lower()
                        if lower_line == "departure" and idx + 1 < len(lines):
                            date_match = re.search(r"\d{1,2}\s+[A-Za-z]{3}\s+\d{4}|\d{4}-\d{2}-\d{2}", lines[idx+1])
                            if date_match:
                                etd = date_match.group(0)
                        elif lower_line == "arrival" and idx + 1 < len(lines):
                            date_match = re.search(r"\d{1,2}\s+[A-Za-z]{3}\s+\d{4}|\d{4}-\d{2}-\d{2}", lines[idx+1])
                            if date_match:
                                eta = date_match.group(0)
                        elif "transit time" in lower_line and idx + 1 < len(lines):
                            days_match = re.search(r"(\d+)\s*day", lines[idx+1], re.IGNORECASE)
                            if days_match:
                                transit_time = int(days_match.group(1))
                        elif "vessel/voyage" in lower_line and idx + 1 < len(lines):
                            vessel_name = lines[idx+1].strip()
                            
                    # 2. General regex fallback if grid extraction missed something
                    if not etd:
                        etd_match = re.search(r"Departure\s+([^\r\n]+)", card_text, re.IGNORECASE)
                        if etd_match:
                            date_match = re.search(r"\d{1,2}\s+[A-Za-z]{3}\s+\d{4}|\d{4}-\d{2}-\d{2}", etd_match.group(1))
                            if date_match:
                                etd = date_match.group(0)
                    if not eta:
                        eta_match = re.search(r"Arrival\s+([^\r\n]+)", card_text, re.IGNORECASE)
                        if eta_match:
                            date_match = re.search(r"\d{1,2}\s+[A-Za-z]{3}\s+\d{4}|\d{4}-\d{2}-\d{2}", eta_match.group(1))
                            if date_match:
                                eta = date_match.group(0)
                    if transit_time == 20:
                        transit_match = re.search(r"Transit time\s+([^\r\n]+)", card_text, re.IGNORECASE)
                        if transit_match:
                            days_match = re.search(r"(\d+)\s*day", transit_match.group(1), re.IGNORECASE)
                            if days_match:
                                transit_time = int(days_match.group(1))
                    if vessel_name == "Maersk Vessel":
                        vessel_match = re.search(r"Vessel/voyage\s+([^\r\n]+)", card_text, re.IGNORECASE)
                        if vessel_match:
                            vessel_name = vessel_match.group(1).strip()
                            
                    # 3. Absolute regex date fallback list
                    dates_fallback = re.findall(r"\d{1,2}\s+[A-Za-z]{3}\s+\d{4}|\d{4}-\d{2}-\d{2}", card_text)
                    if not etd and len(dates_fallback) > 0:
                        etd = dates_fallback[0]
                    if not eta and len(dates_fallback) > 1:
                        eta = dates_fallback[1]
                    elif not eta and etd:
                        eta = etd
                        
                    # 4. Extract free time detention & demurrage details
                    free_time = None
                    freetime_match = re.search(r"(\d+)\s*days?\s*(?:of\s*)?(?:detention|demurrage)", card_text, re.IGNORECASE)
                    if freetime_match:
                        free_time = int(freetime_match.group(1))
                        
                    # Build service name
                    service_name = "Maersk Spot Service"

                    # Check if sold out / not open
                    is_sold_out = "vessel sold out" in card_text_lower or "vessel not open" in card_text_lower or "vessel is not open" in card_text_lower
                    
                    if is_sold_out:
                        price = 0.0
                        if "vessel sold out" in card_text_lower:
                            vessel_name = f"{vessel_name} (Sold out)"
                        else:
                            vessel_name = f"{vessel_name} (Not open)"
                    else:
                        # Extract price
                        price_match = re.search(r"(?:USD|\$)\s*([\d,]+\.?\d{0,2})", card_text, re.IGNORECASE)
                        price = float(price_match.group(1).replace(",", "")) if price_match else 0.0

                    unique_key = f"{etd}_{eta}_{vessel_name}_{price}"
                    if unique_key in processed_keys:
                        continue
                        
                    if not is_sold_out and price == 0.0:
                        processed_keys.add(unique_key)
                        continue
                        
                    print(f"[MAERSK] Processing quote card at index {index} ({etd} -> {eta}, {price} USD)...")
                    
                    raw_quote = {
                        "index": index,
                        "etd": etd,
                        "eta": eta,
                        "transit_time_days": transit_time,
                        "service_name": service_name,
                        "vessel": vessel_name,
                        "free_time": free_time,
                        "total_price": price,
                        "currency": "USD",
                        "card_text": card_text
                    }
                    
                    # Click details button inside the scoped card
                    raw_charges = []
                    details_btn = None
                    
                    if not is_sold_out:
                        try:
                            selectors_to_try = [
                                'span.hyperlink-button:has-text("Price breakdown")',
                                '.hyperlink-button:has-text("Price breakdown")',
                                'button:has-text("Price breakdown & details")',
                                'a:has-text("Price breakdown & details")',
                                'span:has-text("Price breakdown & details")',
                                'div:has-text("Price breakdown & details")',
                            ]
                            
                            for sel in selectors_to_try:
                                try:
                                    btn = card.locator(sel).first
                                    if await btn.is_visible(timeout=1000):
                                        details_btn = btn
                                        break
                                except Exception:
                                    continue
                                    
                            if details_btn:
                                print(f"[MAERSK] Found price breakdown details button for card at index {index}. Clicking...")
                                await details_btn.scroll_into_view_if_needed()
                                await details_btn.click(force=True)
                                await self.page.wait_for_timeout(2500)
                                
                                # Save a screenshot to inspect what opened
                                try:
                                    ss_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scratch", f"breakdown_screenshot_{index}.png")
                                    await self.page.screenshot(path=ss_path, full_page=False)
                                    print(f"[MAERSK] Screenshot saved: {ss_path}")
                                    # Also save page HTML to inspect DOM
                                    html_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scratch", f"breakdown_html_{index}.html")
                                    content = await self.page.content()
                                    with open(html_path, "w", encoding="utf-8") as f:
                                        f.write(content)
                                    print(f"[MAERSK] Page HTML saved: {html_path}")
                                except Exception as ss_e:
                                    print(f"[MAERSK] Screenshot/HTML save failed: {ss_e}")
                                
                                # Scrape all text inside active page/breakdown panel scoped strictly to current card
                                raw_charges = await self.extract_charge_breakdown(card)
                                
                                # Click details button again to close/collapse
                                try:
                                    await details_btn.click(force=True)
                                    await self.page.wait_for_timeout(500)
                                except:
                                    pass
                            else:
                                # Fallback pierce click if scoped card search failed
                                print(f"[MAERSK] Scoped button search failed for card at index {index}. Trying fallback...")
                                fallback_btn = self.page.locator('*:has-text("Price breakdown & details")').nth(index)
                                if await fallback_btn.is_visible(timeout=1500):
                                    await fallback_btn.scroll_into_view_if_needed()
                                    await fallback_btn.click(force=True)
                                    await self.page.wait_for_timeout(2000)
                                    raw_charges = await self.extract_charge_breakdown(card)
                                    try:
                                        await fallback_btn.click(force=True)
                                        await self.page.wait_for_timeout(500)
                                    except:
                                        pass
                                else:
                                    print(f"[MAERSK] Could not find details button for card at index {index} using fallback.")
                        except Exception as e:
                            print(f"[MAERSK] Warning: Could not open price details for card at index {index}: {e}")
                        
                    # Normalize and add
                    try:
                        normalized = await self.normalize_result(raw_quote, raw_charges)
                        quotes.append(normalized)
                    except Exception as e:
                        print(f"[MAERSK] Warning: Normalization failed for card at index {index}: {e}")
                        
                    processed_keys.add(unique_key)
                    new_cards_processed_in_this_batch += 1
                
                # C. If we are on the last expansion step, break
                if expansion == max_expansions:
                    break
                    
                # D. Try to click "Search more sailing options"
                print(f"[MAERSK] Scrolling down to bottom to search for more sailing options...")
                await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await self.page.wait_for_timeout(2000)
                
                more_options_selectors = [
                    'slot[part="text-and-icon-label"]:has-text("Search more sailing options")',
                    'slot:has-text("Search more sailing options")',
                    '[data-cy="label"]:has-text("Search more sailing options")',
                    '.label:has-text("Search more sailing options")',
                    'button:has-text("Search more sailing options")',
                    'div:has-text("Search more sailing options")',
                    'a:has-text("Search more sailing options")',
                    'button:has-text("sailing options")',
                    'div:has-text("sailing options")'
                ]
                
                btn = None
                for selector in more_options_selectors:
                    try:
                        loc = self.page.locator(selector).first
                        if await loc.is_visible(timeout=1500):
                            btn = loc
                            break
                    except Exception:
                        continue
                        
                if btn:
                    await btn.scroll_into_view_if_needed()
                    await self.page.wait_for_timeout(500)
                    await btn.click(force=True)
                    print(f"[MAERSK] Clicked 'Search more sailing options' (Expansion {expansion + 1}/{max_expansions}). Waiting 10s for new quotes...")
                    await self.page.wait_for_timeout(10000)
                else:
                    print("[MAERSK] 'Search more sailing options' button not found at the bottom. Done expanding.")
                    break
            
            if quotes:
                # Sort quotes by departure date (ETD) from earlier to later (ascending)
                def get_etd_date(q):
                    if not q.etd:
                        return date.max
                    try:
                        # Parse e.g. "19 May 2026"
                        return datetime.strptime(q.etd, "%d %b %Y").date()
                    except Exception:
                        try:
                            # Parse e.g. "2026-05-19"
                            return datetime.strptime(q.etd, "%Y-%m-%d").date()
                        except Exception:
                            return date.max

                quotes.sort(key=get_etd_date)
                
                # Enforce limit of exactly the top 10 quotes
                quotes = quotes[:10]
                print(f"[MAERSK] Sorted and sliced final result to {len(quotes)} quote(s).")
                
                return CarrierResultStatus.AVAILABLE_QUOTES_FOUND, quotes
            else:
                return CarrierResultStatus.NO_QUOTES_AVAILABLE, []
                
        except Exception as e:
            print(f"[MAERSK] Unexpected error in full search: {e}")
            return CarrierResultStatus.UNKNOWN_ERROR, []
        finally:
            await self.close()

    # ────────────────────────────────────────
    # BROWSER INITIALIZATION (Shared Engine)
    # ────────────────────────────────────────

    async def _init_browser(self):
        import uuid
        import shutil
        is_prod = os.name != "nt"
        self.playwright = await async_playwright().start()
        
        # Local profile directory to persist cookies, logins, and session data
        persistent_dir = os.getenv("PERSISTENT_PROFILES_DIR")
        if persistent_dir:
            self.master_profile_dir = os.path.join(persistent_dir, "chrome_profile_maersk")
        else:
            self.master_profile_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chrome_profile_maersk")
            
        # Check if reset environment variable is set
        if os.getenv("RESET_CHROME_PROFILES", "").lower() == "true":
            print(f"[MAERSK] ⚠️ RESET_CHROME_PROFILES is active. Clearing persistent profile directory: {self.master_profile_dir}")
            if os.path.exists(self.master_profile_dir):
                try:
                    shutil.rmtree(self.master_profile_dir)
                    print("[MAERSK] Persistent profile directory cleared successfully.")
                except Exception as e:
                    print(f"[MAERSK] Failed to clear persistent profile directory: {e}")
        
        # Create a unique temporary copy of the master profile directory for this search instance
        # to support concurrency and avoid Chromium database lock conflicts.
        unique_id = str(uuid.uuid4())[:8]
        if persistent_dir:
            self.temp_profile_dir = os.path.join(persistent_dir, f"chrome_profile_maersk_tmp_{unique_id}")
        else:
            self.temp_profile_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), f"chrome_profile_maersk_tmp_{unique_id}")

        print(f"[MAERSK] Creating temporary isolated profile directory: {self.temp_profile_dir}")
        if os.path.exists(self.master_profile_dir):
            try:
                shutil.copytree(self.master_profile_dir, self.temp_profile_dir, dirs_exist_ok=True)
                # Remove Chromium singleton lock files to avoid launch blocks
                lock_files = ["SingletonLock", "lock", "SingletonCookie"]
                for root_dir, _, filenames in os.walk(self.temp_profile_dir):
                    for filename in filenames:
                        if filename in lock_files:
                            try:
                                os.remove(os.path.join(root_dir, filename))
                            except Exception:
                                pass
                print("[MAERSK] Master profile copied successfully with lock files cleaned.")
            except Exception as e:
                print(f"[MAERSK] Warning: failed to copy master profile to temp: {e}. Running fresh profile instead.")
        else:
            print("[MAERSK] Master profile not found. Initializing a new isolated chrome profile.")
            os.makedirs(self.temp_profile_dir, exist_ok=True)

        is_prod = os.name != "nt"
        
        # Thread-safe virtual display environment injection
        browser_env = os.environ.copy()
        if is_prod:
            browser_env["DISPLAY"] = ":99"

        launch_kwargs = {
            "user_data_dir": self.temp_profile_dir,
            "headless": False,  # Always non-headless: local = real screen, prod = Xvfb virtual display
            "ignore_https_errors": True,
            "slow_mo": random.randint(80, 150),
            "viewport": {"width": 1920, "height": 1080},
            "env": browser_env,
            "args": [
                "--disable-blink-features=AutomationControlled",  # Mask automation flag
                "--no-sandbox",  # Required for Docker
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding",
            ]
        }
        if not is_prod:
            launch_kwargs["channel"] = "chrome"
        
        # Check if Bright Data Web Unlocker or Residential proxy credentials are set
        proxy_user = os.getenv("MAERSK_PROXY_USER") or os.getenv("BRIGHTDATA_PROXY_USER")
        proxy_pass = os.getenv("MAERSK_PROXY_PASS") or os.getenv("BRIGHTDATA_PROXY_PASS")
        
        if proxy_user and proxy_pass:
            proxy_server = os.getenv("BRIGHTDATA_RESIDENTIAL_PROXY_SERVER") or os.getenv("BRIGHTDATA_PROXY_SERVER")
            if not proxy_server:
                proxy_server = "http://brd.superproxy.io:22225"
            elif ":33335" in proxy_server:
                proxy_server = proxy_server.replace(":33335", ":22225") # Override Web Unlocker to standard Residential Proxy
            
            if "-session-" not in proxy_user:
                import uuid
                session_id = str(uuid.uuid4())[:8]
                proxy_user = f"{proxy_user}-session-{session_id}"
            print(f"[MAERSK] [Proxy] Routing browser session through Bright Data Residential Proxy ({proxy_server}) with session pinning ({proxy_user.split('-session-')[-1]})...")
            launch_kwargs["proxy"] = {
                "server": proxy_server,
                "username": proxy_user,
                "password": proxy_pass,
            }
        else:
            print("[MAERSK] [Proxy] Bright Data Proxy not configured in .env. Running on local system Chrome naturally...")
        
        # NOTE: Bright Data Web Unlocker proxies break Playwright browser sessions (returns empty pages)
        # because the Web Unlocker MITM-intercepts TLS and serves API-processed content, not live HTML.
        # Patchright's stealth-compiled Chromium engine is used instead to pass Akamai fingerprint checks.
        print("[MAERSK] Running via Patchright stealth engine (non-headless on Xvfb for VNC HITL).")
            
        self.context = await self.playwright.chromium.launch_persistent_context(**launch_kwargs)
        self.browser = None  # Handled by persistent context
        self.page = self.context.pages[0] if self.context.pages else await self.context.new_page()
        self.page.set_default_timeout(30000)

    def _extract_port_name(self, text: str) -> str:
        """Extracts the port/city name by removing any UN/LOCODE parentheses (e.g., 'Singapore (SGSIN)' -> 'Singapore')."""
        if not text: return ""
        # Remove parenthesis and their content
        clean = re.sub(r'\s*\([^)]*\)', '', text)
        return clean.strip()

    def _map_container_type(self, text: str) -> str:
        """Maps standard container search codes (e.g. 'DRY 40H') to Maersk Spot display names."""
        if not text: return "40 Dry High"
        normalized = text.strip().upper()
        mapping = {
            "DRY 20": "20 Dry Standard",
            "DRY 40": "40 Dry Standard",
            "DRY 40H": "40 Dry High",
            "REEFER 20": "20 Reefer Standard",
            "REEFER 40": "40 Reefer Standard",
            "REEFER 40H": "40 Reefer High",
        }
        return mapping.get(normalized, "40 Dry High")

    async def _human_type(self, locator, text: str, clear: bool = True):
        """Types text character by character into a given locator or element handle with randomized human-like delays."""
        try:
            await locator.scroll_into_view_if_needed()
        except Exception:
            pass
        
        # Human pre-click reaction delay
        await self.page.wait_for_timeout(random.randint(300, 600))
        
        # Click with a slight delay to mimic mouse button release duration
        await locator.click(delay=random.randint(100, 250))
        await self.page.wait_for_timeout(random.randint(500, 900))
        
        if clear:
            # Control + A / Backspace
            await self.page.keyboard.press("Control+A")
            await self.page.wait_for_timeout(random.randint(150, 300))
            await self.page.keyboard.press("Backspace")
            await self.page.wait_for_timeout(random.randint(250, 500))
        
        for char in text:
            await self.page.keyboard.type(char)
            # Randomized keystroke delays representing an average to slow human typing speed
            await self.page.wait_for_timeout(random.randint(150, 320))
            # 5% chance of a micro-pause (human thinking/resting)
            if random.random() < 0.05:
                await self.page.wait_for_timeout(random.randint(400, 800))
        
        # Post-typing pause
        await self.page.wait_for_timeout(random.randint(800, 1500))

    async def _human_click(self, locator, force: bool = True):
        """Clicks an element with pre-click and post-click human-like reaction pauses."""
        try:
            await locator.scroll_into_view_if_needed()
        except Exception:
            pass
        
        # Pre-click pause
        await self.page.wait_for_timeout(random.randint(400, 800))
        
        # Click with randomized button-down/up duration
        await locator.click(force=force, delay=random.randint(100, 250))
        
        # Post-click pause
        await self.page.wait_for_timeout(random.randint(600, 1200))

    async def _stealth_fill_autocomplete(self, field, query: str, selector: str) -> bool:
        """
        Fills an autocomplete field using the proven original element-level click/fill/type sequence.
        """
        try:
            await field.click()
            await field.fill("")
            await self.page.wait_for_timeout(500)
            await field.type(query, delay=100)
            
            print(f"[MAERSK] Waiting for dropdown suggestions using selector: {selector}")
            await self.page.locator(selector).first.wait_for(state="attached", timeout=6000)
            await self.page.wait_for_timeout(500)
            return True
        except Exception as e:
            print(f"[MAERSK] Autocomplete trigger failed: {e}")
            return False

    # ────────────────────────────────────────
    # LOGIN & VERIFICATION GATEWAY
    # ────────────────────────────────────────

    async def login(self) -> bool:
        username = os.getenv("MAERSK_USERNAME")
        password = os.getenv("MAERSK_PASSWORD")
        if not username or not password:
            print("[MAERSK] ERROR: MAERSK_USERNAME or MAERSK_PASSWORD not set in environment")
            return False

        try:
            await self._init_browser()
            print("[MAERSK] Navigating to Maersk Login page...")
            # Navigate and wait for the full page load (MDS web components need JS to hydrate)
            await self.page.goto("https://www.maersk.com/login", wait_until="load", timeout=60000)
            # Extra wait for MDS web components (<mc-input>, <mc-button>) to fully hydrate via JavaScript
            await self.page.wait_for_timeout(5000)
            print(f"[MAERSK] Landed on: {self.page.url}")
            
            # Check if we are already logged in (cookie session remembered in chrome_profile)
            current_url = self.page.url
            
            is_logged_in = False
            if "login" not in current_url.lower() and "auth" not in current_url.lower():
                login_indicators = [
                    'text="Log out"',
                    'text="Sign out"',
                    'text="Log Out"',
                    'text="Sign Out"',
                    '[class*="profile"]',
                    '[class*="avatar"]',
                    'a[href*="logout"]',
                    'a[href*="signout"]'
                ]
                for selector in login_indicators:
                    try:
                        if await self.page.locator(selector).first.is_visible(timeout=1500):
                            print(f"[MAERSK] Found login indicator: {selector}")
                            is_logged_in = True
                            break
                    except Exception:
                        pass
            
            if is_logged_in:
                print("[MAERSK] Session restored successfully! Already logged in.")
                self.is_login_successful = True
                return True
                
            print(f"[MAERSK] Current URL: {current_url}. Initiating login flow...")
            
            # Dismiss Cookie Popup (Maersk is notorious for overlays blocking inputs)
            try:
                print("[MAERSK] Checking for Cookie Consent modal...")
                cookie_buttons = [
                    '#onetrust-accept-btn-handler',
                    'button#onetrust-accept-btn-handler',
                    'button:has-text("Allow all")',
                    'button:has-text("Accept All")',
                    'button:has-text("Essential only")',
                    '#co-accept-all',
                    '.co-accept-all',
                    'button[id*="cookie" i]',
                    'button[class*="cookie" i]'
                ]
                for selector in cookie_buttons:
                    btn = self.page.locator(selector).first
                    if await btn.is_visible(timeout=3000):
                        print(f"[MAERSK] Dismissing cookie banner using selector: {selector}")
                        await self._human_click(btn)
                        await self.page.wait_for_timeout(1500)
                        break
            except Exception as e:
                print(f"[MAERSK] Cookie consent bypass failed/skipped: {e}")
                
            # Fill Username
            username_filled = False
            try:
                # 1. Wait for either host element #mc-input-username or any standard username input to appear (timeout: 10s)
                print("[MAERSK] Locating username field...")
                user_host = self.page.locator('#mc-input-username').first
                try:
                    await user_host.wait_for(state="attached", timeout=10000)
                except Exception:
                    print("[MAERSK] Warning: #mc-input-username host not attached in 10s, trying fallback waiting...")

                # Primarily attempt slow human-like typing on the nested input or shadow host
                try:
                    user_input = self.page.locator('#mc-input-username input').first
                    target_element = user_input if await user_input.is_visible(timeout=2000) else user_host
                    
                    print("[MAERSK] Typing username via human-like keystrokes...")
                    await self._human_type(target_element, username)
                    username_filled = True
                except Exception as e:
                    print(f"[MAERSK] Human typing failed for username: {e}. Trying fallback methods...")

                # Fallback Method A: Try filling the shadow-host directly (standard webcomponent playwright behavior)
                if not username_filled:
                    try:
                        await user_host.fill(username, timeout=3000)
                        print("[MAERSK] Username filled via Direct Shadow Host Fill (fallback).")
                        username_filled = True
                    except Exception:
                        pass

                # Fallback Method B: Try filling the nested input
                if not username_filled:
                    try:
                        user_input = self.page.locator('#mc-input-username input').first
                        await user_input.fill("", timeout=3000)
                        await user_input.fill(username, timeout=3000)
                        print("[MAERSK] Username filled via Nested input fill (fallback).")
                        username_filled = True
                    except Exception:
                        pass

                # Fallback Method C: General Light DOM Input Fallbacks
                if not username_filled:
                    for selector in ['input[name="username" i]', 'input[type="email" i]', 'input[type="text" i]', 'input[id*="username" i]']:
                        try:
                            field = self.page.locator(selector).first
                            if await field.is_visible(timeout=2000):
                                await field.fill(username)
                                print(f"[MAERSK] Username filled via fallback selector: {selector}")
                                username_filled = True
                                break
                        except Exception:
                            continue
            except Exception as e:
                print(f"[MAERSK] Username fill failed completely: {e}")

            # Fill Password
            password_filled = False
            try:
                print("[MAERSK] Locating password field...")
                pass_host = self.page.locator('#mc-input-password').first
                try:
                    await pass_host.wait_for(state="attached", timeout=5000)
                except Exception:
                    pass

                # Primarily attempt slow human-like typing on the nested input or shadow host
                try:
                    pass_input = self.page.locator('#mc-input-password input').first
                    target_element = pass_input if await pass_input.is_visible(timeout=2000) else pass_host
                    
                    print("[MAERSK] Typing password via human-like keystrokes...")
                    await self._human_type(target_element, password)
                    password_filled = True
                except Exception as e:
                    print(f"[MAERSK] Human typing failed for password: {e}. Trying fallback methods...")

                # Fallback Method A: Try filling the shadow-host directly
                if not password_filled:
                    try:
                        await pass_host.fill(password, timeout=3000)
                        print("[MAERSK] Password filled via Direct Shadow Host Fill (fallback).")
                        password_filled = True
                    except Exception:
                        pass

                # Fallback Method B: Try filling the nested input
                if not password_filled:
                    try:
                        pass_input = self.page.locator('#mc-input-password input').first
                        await pass_input.fill("", timeout=3000)
                        await pass_input.fill(password, timeout=3000)
                        print("[MAERSK] Password filled via Nested input fill (fallback).")
                        password_filled = True
                    except Exception:
                        pass

                # Fallback Method C: General Light DOM Input Fallbacks
                if not password_filled:
                    for selector in ['input[name="password" i]', 'input[type="password" i]', 'input[id*="password" i]']:
                        try:
                            field = self.page.locator(selector).first
                            if await field.is_visible(timeout=2000):
                                await field.fill(password)
                                print(f"[MAERSK] Password filled via fallback selector: {selector}")
                                password_filled = True
                                break
                        except Exception:
                            continue
            except Exception as e:
                print(f"[MAERSK] Password fill failed completely: {e}")

            # Submit Login
            try:
                # Add a substantial delay (e.g., 2-3.5 seconds) after entering credentials before clicking submit
                submit_wait = random.randint(2000, 3500)
                print(f"[MAERSK] Credentials entered. Waiting {submit_wait/1000:.2f} seconds before submitting login form...")
                await self.page.wait_for_timeout(submit_wait)
                
                # 1. Wait for host
                submit_host = self.page.locator('#login-submit-button').first
                await submit_host.wait_for(state="attached", timeout=5000)
                
                # 2. Click host using human_click
                await self._human_click(submit_host)
                print("[MAERSK] Login form submitted successfully via MDS Host-Click.")
            except Exception as e:
                print(f"[MAERSK] MDS Submit click failed: {e}. Trying fallback...")
                try:
                    # Target inner button
                    btn = self.page.locator('#login-submit-button button').first
                    await self._human_click(btn)
                    print("[MAERSK] Login form submitted successfully via inner button.")
                except Exception as ex:
                    try:
                        # Target button type submit
                        btn = self.page.locator('button[type="submit"]').first
                        await self._human_click(btn)
                        print("[MAERSK] Login form submitted successfully via button[type='submit'].")
                    except Exception as exc:
                        try:
                            # Final backup: Press enter on active element
                            await self.page.keyboard.press("Enter")
                            print("[MAERSK] Login form submitted successfully via Keyboard Enter keypress.")
                        except:
                            print(f"[MAERSK] Fallback Submit click failed: {exc}")

            # Verification Loop (HITL Bypassing)
            print("[MAERSK] Waiting for verification gate or redirect...")
            for i in range(300):
                await asyncio.sleep(1)
                curr_url = self.page.url
                
                # Check for successful redirects (redirects to hub or dashboard)
                if "login" not in curr_url.lower() and "auth" not in curr_url.lower() and ("hub" in curr_url.lower() or "dashboard" in curr_url.lower() or "book" in curr_url.lower()):
                    print("[MAERSK] Login successful!")
                    self.is_login_successful = True
                    await self.page.wait_for_timeout(2000)
                    return True

                # Print manual action notices
                if i % 15 == 14:
                    print("[MAERSK] [ACTION REQUIRED] Maersk Verification/2FA Page Detected!")
                    print("[MAERSK] Please look at the opened Chromium window and manually complete the verification/CAPTCHA.")
                    print(f"[MAERSK] Still waiting... {300 - i - 1} seconds remaining.")

            print("[MAERSK] [TIMEOUT] Login verification timed out.")
            return False

        except Exception as e:
            print(f"[MAERSK] Login failed: {e}")
            return False

    # ────────────────────────────────────────
    # SEARCH FOR QUOTES (Smart Autofill & Fallback)
    # ────────────────────────────────────────

    async def search_quotes(self, request: RateSearchRequest) -> CarrierResultStatus:
        try:
            print("[MAERSK] Navigating to Booking page...")
            await self.page.goto(self.QUOTE_URL, wait_until="domcontentloaded", timeout=40000)
            await self.page.wait_for_timeout(3000)
            
            # Dismiss Cookie Popup if visible
            try:
                cookie_btn = self.page.locator('button:has-text("Allow all"), button:has-text("Essential only")').first
                if await cookie_btn.is_visible(timeout=3000):
                    await cookie_btn.click(force=True)
                    await self.page.wait_for_timeout(1000)
            except:
                pass

            # Smart autofill attempt
            autofill_success = False
            try:
                # Resolve origin locode
                origin_locode, _ = extract_locode_and_country(request.origin)
                if not origin_locode:
                    clean = request.origin.strip()
                    if len(clean) == 5 and clean.isalpha():
                        origin_locode = clean.upper()
                    else:
                        from services.port_manager import search_port
                        ports = search_port(request.origin)
                        if ports:
                            origin_locode = ports[0]['code']

                # Resolve destination locode
                destination_locode, _ = extract_locode_and_country(request.destination)
                if not destination_locode:
                    clean = request.destination.strip()
                    if len(clean) == 5 and clean.isalpha():
                        destination_locode = clean.upper()
                    else:
                        from services.port_manager import search_port
                        ports = search_port(request.destination)
                        if ports:
                            destination_locode = ports[0]['code']

                # Check cache first (retrieve cached values for fallback autocomplete matching)
                origin_cached = get_cached_carrier_port("maersk", origin_locode) if origin_locode else None
                destination_cached = get_cached_carrier_port("maersk", destination_locode) if destination_locode else None
                
                # ────────────────────────────────────────────────────────
                # PREPARE SEARCH QUERIES
                # ────────────────────────────────────────────────────────
                # We want to let the user type and take it as what it is, avoiding auto-filling or auto-expanding.
                # If they typed a friendly query (like "ho chi minh" or "ho ch minh city"), we type exactly that.
                # If they provided a 5-letter LOCODE (like "VNSGN"), we resolve it to our clean overridden name.
                def prepare_maersk_query(raw_input: str) -> str:
                    if not raw_input:
                        return ""
                    
                    # 0. Hardcoded overrides for problematic cities to bypass autocomplete overlaps
                    raw_lower = raw_input.lower()
                    if "karachi" in raw_lower:
                        return "Karachi, Pakistan"
                    if "melbourne" in raw_lower:
                        return "Melbourne, Australia"
                    if "sydney" in raw_lower or "ausyd" in raw_lower:
                        return "Sydney (New South Wales), Australia"
                    if "jeddah" in raw_lower or "sajed" in raw_lower:
                        return "Jeddah, Saudi Arabia"
                    if "shenzhen" in raw_lower or "cnszx" in raw_lower:
                        return "Shenzhen (Guangdong), China"
                    if "ningbo" in raw_lower or "cnngb" in raw_lower:
                        return "Ningbo (Zhejiang), China"
                    if "nhava sheva" in raw_lower or "jawaharlal" in raw_lower or "innsa" in raw_lower:
                        return "Jawaharlal Nehru (MAHARASHTRA), India"
                    if "bangkok" in raw_lower or "thbkk" in raw_lower:
                        return "Bangkok PAT, Thailand"
                    if "shuaiba" in raw_lower:
                        return "Shuaiba, Kuwait"
                    # 1. Remove parentheses (e.g. "Singapore (SGSIN)" -> "Singapore")
                    cleaned = re.sub(r'\s*\([^)]*\)', '', raw_input).strip()
                    # 2. Strip country suffix if present in the user input (e.g., "Singapore, Singapore" -> "Singapore")
                    if ',' in cleaned:
                        cleaned = cleaned.split(',')[0].strip()
                    
                    # 3. Handle common typos/spellings/abbreviations directly
                    cleaned_lower = cleaned.lower()
                    if "ho chi minh" in cleaned_lower or "ho ch minh" in cleaned_lower:
                        return "Ho Chi Minh"
                    if "haiphong" in cleaned_lower or "hai phong" in cleaned_lower:
                        return "Haiphong"
                    
                    # 4. Check if it is a pure 5-letter LOCODE
                    if len(cleaned) == 5 and cleaned.isalpha():
                        locode_upper = cleaned.upper()
                        # Use clean minimal spelling overrides for Maersk
                        from services.port_manager import CARRIER_PORT_OVERRIDES, PortManager
                        maersk_overrides = CARRIER_PORT_OVERRIDES.get("maersk", {})
                        if locode_upper in maersk_overrides:
                            return maersk_overrides[locode_upper]
                        # Use cached name if available
                        cached_val = get_cached_carrier_port("maersk", locode_upper)
                        if cached_val:
                            return prepare_maersk_query(cached_val)
                        # Use database name
                        port_obj = PortManager().get_port_by_code(locode_upper)
                        if port_obj:
                            name = port_obj.get("name", "")
                            return prepare_maersk_query(name)
                        return cleaned
                    
                    # 5. Clean common trailing noise words and country names for friendly inputs
                    # e.g., "ho chi minh city vietnam" -> "ho chi minh"
                    NOISE_WORDS = {"city", "port", "terminal", "container", "province", "state"}
                    COUNTRY_NAMES = {name.lower() for name in COUNTRY_CODE_TO_NAME.values()}
                    COUNTRY_NAMES.update({"viet nam", "usa", "uk", "uae", "spain", "france", "netherlands"})
                    
                    words = cleaned.split()
                    while len(words) > 1:  # Never strip the last remaining word
                        last_word_lower = words[-1].lower()
                        if last_word_lower in NOISE_WORDS or last_word_lower in COUNTRY_NAMES:
                            words.pop()
                        elif len(words) >= 3 and f"{words[-2].lower()} {last_word_lower}" in COUNTRY_NAMES:
                            words.pop()
                            words.pop()
                        else:
                            break
                    cleaned = " ".join(words)
                    
                    # Re-verify HCM or HP after popping suffixes
                    cleaned_lower = cleaned.lower()
                    if "ho chi minh" in cleaned_lower or "ho ch minh" in cleaned_lower:
                        return "Ho Chi Minh"
                    if "haiphong" in cleaned_lower or "hai phong" in cleaned_lower:
                        return "Haiphong"
                        
                    return cleaned

                origin_query = prepare_maersk_query(request.origin)
                destination_query = prepare_maersk_query(request.destination)
                
                print(f"[MAERSK] Origin prepared query: '{origin_query}' (input: '{request.origin}')")
                print(f"[MAERSK] Destination prepared query: '{destination_query}' (input: '{request.destination}')")

                # 1. Origin Port input (From)
                origin_selectors = [
                    'input#mc-input-from',
                    'input[placeholder*="from" i]',
                    'input[placeholder*="Enter city or port" i]'
                ]
                origin_field = None
                for selector in origin_selectors:
                    field = self.page.locator(selector).first
                    if await field.is_visible(timeout=4000):
                        origin_field = field
                        print(f"[MAERSK] Found Origin Port input field using: {selector}")
                        break
                        
                if origin_field:
                    suggestions_union = 'li[role="option"], ul[role="listbox"] li, [class*="c-location-search" i] li, .c-location-search__result, [class*="location" i] [class*="result" i], [class*="suggestion" i] li'
                    await self._stealth_fill_autocomplete(origin_field, origin_query, suggestions_union)
                    
                    # Wait for autocomplete dropdown to appear, trying several known Maersk selector patterns
                    suggestions_sel = None
                    MAERSK_DROPDOWN_SELECTORS = [
                        'li[role="option"]',
                        'ul[role="listbox"] li',
                        '[class*="c-location-search" i] li',
                        '[class*="location-search" i] [class*="result" i]',
                        '.c-location-search__result',
                        '[class*="location" i] [class*="result" i]',
                        '[class*="suggestion" i] li',
                        '[class*="autocomplete" i] li',
                    ]
                    for _sel in MAERSK_DROPDOWN_SELECTORS:
                        try:
                            test_count = await self.page.locator(_sel).count()
                            if test_count > 0:
                                suggestions_sel = _sel
                                print(f"[MAERSK] Autocomplete selector matched: {_sel!r} ({test_count} items)")
                                break
                        except Exception:
                            continue
                    
                    if not suggestions_sel:
                        # Final fallback: broad selector
                        suggestions_sel = 'li[role="option"], ul[role="listbox"] li, [class*="suggestion" i], [class*="location" i] [class*="result" i]'
                    
                    clicked = False
                    try:
                        # Scan suggestions to select the one that matches our target country code/name
                        suggestion_locators = self.page.locator(suggestions_sel)
                        sug_count = await suggestion_locators.count()
                        print(f"[MAERSK] Found {sug_count} autocomplete suggestions for Origin.")
                        
                        locode, country_from_text = extract_locode_and_country(request.origin)
                        expected_country_code = None
                        if locode:
                            from services.port_manager import PortManager
                            port_obj = PortManager().get_port_by_code(locode)
                            if port_obj:
                                expected_country_code = port_obj.get("country", "").upper()
                                
                        country_keywords = []
                        if country_from_text:
                            country_keywords.append(country_from_text.lower())
                        if expected_country_code:
                            country_keywords.append(expected_country_code.lower())
                            c_name = COUNTRY_CODE_TO_NAME.get(expected_country_code)
                            if c_name:
                                country_keywords.append(c_name.lower())
                                
                        print(f"[MAERSK] Origin expected country keywords: {country_keywords}")
                        
                        INVALID_SUGGESTION_KEYWORDS = [
                            "no results found", "no matching location", "try another search", 
                            "no matches", "loading", "please enter", "check your spelling",
                            "english spelling", "full city name", "abbreviation",
                            "location matching", "try using", "no location",
                            "continue to book", "close", "sign in", "log in", "accept",
                            "cookie", "subscribe", "submit", "cancel", "back",
                            "select container", "select commodity", "price owner"
                        ]
                        
                        valid_suggestions = [] # list of dicts: {"index": idx, "text": sug_text}
                        for idx in range(sug_count):
                            sug = suggestion_locators.nth(idx)
                            sug_text = (await sug.inner_text()).strip()
                            # Clean up potential multi-line layout formatting from LitElement components to ensure comma-splitting works
                            sug_text = re.sub(r'\s*\n\s*', ', ', sug_text)
                            sug_text = re.sub(r',\s*,', ',', sug_text).strip()
                            sug_text_lower = sug_text.lower()
                            print(f"[MAERSK] Dropdown Suggestion {idx}: '{sug_text}'")
                            
                            if not sug_text or any(kw in sug_text_lower for kw in INVALID_SUGGESTION_KEYWORDS):
                                print(f"[MAERSK] -> Suggestion {idx} is invalid/no-results indicator. Skipping.")
                                continue
                            
                            valid_suggestions.append({"index": idx, "text": sug_text})
                            
                        target_idx = None
                        if valid_suggestions:
                            # 1. Try exact LOCODE match first (e.g. "(AUMEL)" or "(SGSIN)" in text)
                            if origin_locode:
                                clean_locode = origin_locode.strip().upper()
                                for vs in valid_suggestions:
                                    vs_upper = vs["text"].upper()
                                    if f"({clean_locode})" in vs_upper or f" {clean_locode} " in vs_upper or vs_upper == clean_locode:
                                        print(f"[MAERSK] -> Exact LOCODE match! Picking index {vs['index']}: '{vs['text']}'")
                                        target_idx = vs["index"]
                                        break

                            # 2. Try exact city name match (e.g. "Karachi, Pakistan" where city part before comma is exactly "Karachi")
                            if target_idx is None:
                                clean_query = origin_query.strip().lower()
                                query_city_part = clean_query.split(",")[0].strip()
                                query_city_part = re.sub(r'\s*\([^)]*\)', '', query_city_part).strip()
                                for vs in valid_suggestions:
                                    vs_lower = vs["text"].lower()
                                    parts = vs_lower.split(",")
                                    if parts:
                                        city_part = parts[0].strip()
                                        # Remove state parentheses if present, e.g. "Melbourne (Victoria)" -> "Melbourne"
                                        city_part_clean = re.sub(r'\s*\([^)]*\)', '', city_part).strip()
                                        if city_part_clean == query_city_part and (not country_keywords or any(kw in vs_lower for kw in country_keywords)):
                                            print(f"[MAERSK] -> Matches exact city name and country! Picking index {vs['index']}: '{vs['text']}'")
                                            target_idx = vs["index"]
                                            break

                            # 3. Try name AND country keywords match
                            if target_idx is None:
                                clean_query = origin_query.strip().lower()
                                for vs in valid_suggestions:
                                    vs_lower = vs["text"].lower()
                                    if (clean_query in vs_lower or vs_lower in clean_query) and any(kw in vs_lower for kw in country_keywords):
                                        print(f"[MAERSK] -> Matches query AND country keywords! Picking index {vs['index']}: '{vs['text']}'")
                                        target_idx = vs["index"]
                                        break

                            # 4. Fallback to exact user-typed query match
                            if target_idx is None:
                                clean_query = origin_query.strip().lower()
                                for vs in valid_suggestions:
                                    if clean_query in vs["text"].lower() or vs["text"].lower() in clean_query:
                                        print(f"[MAERSK] -> Matches typed query! Picking index {vs['index']}: '{vs['text']}'")
                                        target_idx = vs["index"]
                                        break

                            # 4. Try to match exact cached name if available
                            if target_idx is None and origin_cached:
                                clean_cached = origin_cached.strip().lower()
                                for vs in valid_suggestions:
                                    if vs["text"].lower() == clean_cached or clean_cached in vs["text"].lower():
                                        print(f"[MAERSK] -> Matches cached name exactly! Picking index {vs['index']}: '{vs['text']}'")
                                        target_idx = vs["index"]
                                        break
                                        
                            # 5. Try to match country keywords alone
                            if target_idx is None:
                                for vs in valid_suggestions:
                                    if any(kw in vs["text"].lower() for kw in country_keywords):
                                        print(f"[MAERSK] -> Matches target country keywords! Picking index {vs['index']}: '{vs['text']}'")
                                        target_idx = vs["index"]
                                        break
                                        
                            # 6. Fallback to first valid suggestion
                            if target_idx is None:
                                vs = valid_suggestions[0]
                                print(f"[MAERSK] -> No specific match. Picking first valid index {vs['index']}: '{vs['text']}'")
                                target_idx = vs["index"]
                                
                        if target_idx is not None:
                            suggestion = suggestion_locators.nth(target_idx)
                            if await suggestion.is_visible():
                                tag_name = await suggestion.evaluate("el => el.tagName.toLowerCase()")
                                if tag_name != "input":
                                    selected_text = (await suggestion.inner_text()).strip()
                                    await suggestion.scroll_into_view_if_needed()
                                    await suggestion.click(force=True)
                                    print(f"[MAERSK] Clicked autocomplete suggestion element at index {target_idx}: '{selected_text}'")
                                    clicked = True
                                    if origin_locode:
                                        set_cached_carrier_port("maersk", origin_locode, selected_text)
                        else:
                            print("[MAERSK] No valid suggestions found in the dropdown list.")
                    except Exception as e:
                        print(f"[MAERSK] Dropdown click failed or selector not found: {e}")
                        
                    if not clicked:
                        # JS shadow-DOM fallback: pierce custom mc- web components to find visible dropdown items
                        try:
                            js_result = await self.page.evaluate("""
                                () => {
                                    const INVALID = [
                                        'no results', 'no matching', 'loading', 'please enter',
                                        'check your spelling', 'english spelling', 'full city name',
                                        'abbreviation', 'location matching', 'try using', 'no location',
                                        'continue to book', 'close', 'sign in', 'log in', 'accept',
                                        'cookie', 'subscribe', 'submit', 'cancel', 'back',
                                        'select container', 'select commodity', 'price owner'
                                    ];
                                    // Walk all shadow roots looking for listbox/option elements
                                    function findInShadow(root) {
                                        const items = root.querySelectorAll('li[role="option"], [role="listbox"] li, [class*="suggestion"], [class*="result"][class*="location"]');
                                        return Array.from(items);
                                    }
                                    function collectAll(node) {
                                        let found = findInShadow(node);
                                        node.querySelectorAll('*').forEach(el => {
                                            if (el.shadowRoot) found = found.concat(collectAll(el.shadowRoot));
                                        });
                                        return found;
                                    }
                                    const all = collectAll(document);
                                    for (const el of all) {
                                        const txt = (el.innerText || el.textContent || '').trim().toLowerCase();
                                        if (!txt || INVALID.some(k => txt.includes(k))) continue;
                                        el.click();
                                        return txt;
                                    }
                                    return null;
                                }
                            """)
                            if js_result:
                                print(f"[MAERSK] JS shadow-DOM click succeeded: '{js_result}'")
                                clicked = True
                                if origin_locode:
                                    set_cached_carrier_port("maersk", origin_locode, js_result)
                                await self.page.wait_for_timeout(400)
                            else:
                                print("[MAERSK] JS shadow-DOM found no items. Falling back to keyboard.")
                        except Exception as js_e:
                            print(f"[MAERSK] JS shadow-DOM fallback failed: {js_e}")

                    if not clicked:
                        try:
                            await origin_field.focus()
                            press_count = 1
                            q_lower = origin_query.lower()
                            if "karachi" in q_lower or "melbourne" in q_lower:
                                press_count = 2
                                print(f"[MAERSK] Origin Query is '{origin_query}', pressing ArrowDown {press_count} times to select CY/correct option.")
                            else:
                                print(f"[MAERSK] Sending keyboard ArrowDown+Enter to select first suggestion...")
                                
                            for _ in range(press_count):
                                await origin_field.press("ArrowDown")
                                await self.page.wait_for_timeout(300)
                                
                            await origin_field.press("Enter")
                            await self.page.wait_for_timeout(600)
                        except Exception as e:
                            print(f"[MAERSK] Keyboard selection failed: {e}")
                        
                    print("[MAERSK] Origin Port selected successfully.")
                else:
                    raise Exception("Origin Port input field not found")

                # 2. Destination Port input (To)
                dest_selectors = [
                    'input#mc-input-to',
                    'input[placeholder*="to" i]',
                    'input[placeholder*="Enter city or port" i]'
                ]
                dest_field = None
                for selector in dest_selectors:
                    if selector == 'input[placeholder*="Enter city or port" i]':
                        # The destination is the second such input field
                        field = self.page.locator(selector).nth(1)
                    else:
                        field = self.page.locator(selector).first
                        
                    if await field.is_visible(timeout=4000):
                        dest_field = field
                        print(f"[MAERSK] Found Destination Port input field using: {selector}")
                        break
                        
                if dest_field:
                    suggestions_union = 'li[role="option"], ul[role="listbox"] li, [class*="c-location-search" i] li, .c-location-search__result, [class*="location" i] [class*="result" i], [class*="suggestion" i] li'
                    await self._stealth_fill_autocomplete(dest_field, destination_query, suggestions_union)
                    
                    # Wait for autocomplete dropdown to appear, trying several known Maersk selector patterns
                    suggestions_sel = None
                    MAERSK_DROPDOWN_SELECTORS_DEST = [
                        'li[role="option"]',
                        'ul[role="listbox"] li',
                        '[class*="c-location-search" i] li',
                        '[class*="location-search" i] [class*="result" i]',
                        '.c-location-search__result',
                        '[class*="location" i] [class*="result" i]',
                        '[class*="suggestion" i] li',
                        '[class*="autocomplete" i] li',
                    ]
                    for _sel in MAERSK_DROPDOWN_SELECTORS_DEST:
                        try:
                            test_count = await self.page.locator(_sel).count()
                            if test_count > 0:
                                suggestions_sel = _sel
                                print(f"[MAERSK] Dest autocomplete selector matched: {_sel!r} ({test_count} items)")
                                break
                        except Exception:
                            continue
                    
                    if not suggestions_sel:
                        suggestions_sel = 'li[role="option"], ul[role="listbox"] li, [class*="suggestion" i], [class*="location" i] [class*="result" i]'
                    
                    clicked = False
                    try:
                        # Scan suggestions to select the one that matches our target country code/name
                        suggestion_locators = self.page.locator(suggestions_sel)
                        sug_count = await suggestion_locators.count()
                        print(f"[MAERSK] Found {sug_count} autocomplete suggestions for Destination.")
                        
                        locode, country_from_text = extract_locode_and_country(request.destination)
                        expected_country_code = None
                        if locode:
                            from services.port_manager import PortManager
                            port_obj = PortManager().get_port_by_code(locode)
                            if port_obj:
                                expected_country_code = port_obj.get("country", "").upper()
                                
                        country_keywords = []
                        if country_from_text:
                            country_keywords.append(country_from_text.lower())
                        if expected_country_code:
                            country_keywords.append(expected_country_code.lower())
                            c_name = COUNTRY_CODE_TO_NAME.get(expected_country_code)
                            if c_name:
                                country_keywords.append(c_name.lower())
                                
                        print(f"[MAERSK] Destination expected country keywords: {country_keywords}")
                        
                        INVALID_SUGGESTION_KEYWORDS = [
                            "no results found", "no matching location", "try another search",
                            "no matches", "loading", "please enter", "check your spelling",
                            "english spelling", "full city name", "abbreviation",
                            "location matching", "try using", "no location",
                            "continue to book", "close", "sign in", "log in", "accept",
                            "cookie", "subscribe", "submit", "cancel", "back",
                            "select container", "select commodity", "price owner"
                        ]
                        
                        valid_suggestions = []  # list of dicts: {"index": idx, "text": sug_text}
                        for idx in range(sug_count):
                            sug = suggestion_locators.nth(idx)
                            sug_text = (await sug.inner_text()).strip()
                            # Clean up potential multi-line layout formatting from LitElement components to ensure comma-splitting works
                            sug_text = re.sub(r'\s*\n\s*', ', ', sug_text)
                            sug_text = re.sub(r',\s*,', ',', sug_text).strip()
                            sug_text_lower = sug_text.lower()
                            print(f"[MAERSK] Dropdown Suggestion {idx}: '{sug_text}'")
                            
                            if not sug_text or any(kw in sug_text_lower for kw in INVALID_SUGGESTION_KEYWORDS):
                                print(f"[MAERSK] -> Suggestion {idx} is invalid/no-results indicator. Skipping.")
                                continue
                            
                            valid_suggestions.append({"index": idx, "text": sug_text})
                            
                        target_idx = None
                        if valid_suggestions:
                            # 1. Try exact LOCODE match first (e.g. "(AUMEL)" or "(SGSIN)" in text)
                            if destination_locode:
                                clean_locode = destination_locode.strip().upper()
                                for vs in valid_suggestions:
                                    vs_upper = vs["text"].upper()
                                    if f"({clean_locode})" in vs_upper or f" {clean_locode} " in vs_upper or vs_upper == clean_locode:
                                        print(f"[MAERSK] -> Exact LOCODE match! Picking index {vs['index']}: '{vs['text']}'")
                                        target_idx = vs["index"]
                                        break

                            # 2. Try exact city name match (e.g. "Karachi, Pakistan" where city part before comma is exactly "Karachi")
                            if target_idx is None:
                                clean_query = destination_query.strip().lower()
                                query_city_part = clean_query.split(",")[0].strip()
                                query_city_part = re.sub(r'\s*\([^)]*\)', '', query_city_part).strip()
                                for vs in valid_suggestions:
                                    vs_lower = vs["text"].lower()
                                    parts = vs_lower.split(",")
                                    if parts:
                                        city_part = parts[0].strip()
                                        # Remove state parentheses if present, e.g. "Melbourne (Victoria)" -> "Melbourne"
                                        city_part_clean = re.sub(r'\s*\([^)]*\)', '', city_part).strip()
                                        if city_part_clean == query_city_part and (not country_keywords or any(kw in vs_lower for kw in country_keywords)):
                                            print(f"[MAERSK] -> Matches exact city name and country! Picking index {vs['index']}: '{vs['text']}'")
                                            target_idx = vs["index"]
                                            break

                            # 3. Try name AND country keywords match
                            if target_idx is None:
                                clean_query = destination_query.strip().lower()
                                for vs in valid_suggestions:
                                    vs_lower = vs["text"].lower()
                                    if (clean_query in vs_lower or vs_lower in clean_query) and any(kw in vs_lower for kw in country_keywords):
                                        print(f"[MAERSK] -> Matches query AND country keywords! Picking index {vs['index']}: '{vs['text']}'")
                                        target_idx = vs["index"]
                                        break

                            # 4. Fallback to exact user-typed query match
                            if target_idx is None:
                                clean_query = destination_query.strip().lower()
                                for vs in valid_suggestions:
                                    if clean_query in vs["text"].lower() or vs["text"].lower() in clean_query:
                                        print(f"[MAERSK] -> Matches typed query! Picking index {vs['index']}: '{vs['text']}'")
                                        target_idx = vs["index"]
                                        break

                            # 4. Try to match exact cached name if available
                            if target_idx is None and destination_cached:
                                clean_cached = destination_cached.strip().lower()
                                for vs in valid_suggestions:
                                    if vs["text"].lower() == clean_cached or clean_cached in vs["text"].lower():
                                        print(f"[MAERSK] -> Matches cached name exactly! Picking index {vs['index']}: '{vs['text']}'")
                                        target_idx = vs["index"]
                                        break
                                        
                            # 5. Try to match country keywords alone
                            if target_idx is None:
                                for vs in valid_suggestions:
                                    if any(kw in vs["text"].lower() for kw in country_keywords):
                                        print(f"[MAERSK] -> Matches target country keywords! Picking index {vs['index']}: '{vs['text']}'")
                                        target_idx = vs["index"]
                                        break
                                        
                            # 6. Fallback to first valid suggestion
                            if target_idx is None:
                                vs = valid_suggestions[0]
                                print(f"[MAERSK] -> No specific match. Picking first valid index {vs['index']}: '{vs['text']}'")
                                target_idx = vs["index"]
                                
                        if target_idx is not None:
                            suggestion = suggestion_locators.nth(target_idx)
                            if await suggestion.is_visible():
                                tag_name = await suggestion.evaluate("el => el.tagName.toLowerCase()")
                                if tag_name != "input":
                                    selected_text = (await suggestion.inner_text()).strip()
                                    await suggestion.scroll_into_view_if_needed()
                                    await suggestion.click(force=True)
                                    print(f"[MAERSK] Clicked autocomplete suggestion element at index {target_idx}: '{selected_text}'")
                                    clicked = True
                                    if destination_locode:
                                        set_cached_carrier_port("maersk", destination_locode, selected_text)
                        else:
                            print("[MAERSK] No valid suggestions found in the dropdown list.")
                    except Exception as e:
                        print(f"[MAERSK] Dropdown click failed or selector not found: {e}")
                        
                    if not clicked:
                        # JS shadow-DOM fallback: pierce custom mc- web components to find visible dropdown items
                        try:
                            js_result = await self.page.evaluate("""
                                () => {
                                    const INVALID = [
                                        'no results', 'no matching', 'loading', 'please enter',
                                        'check your spelling', 'english spelling', 'full city name',
                                        'abbreviation', 'location matching', 'try using', 'no location',
                                        'continue to book', 'close', 'sign in', 'log in', 'accept',
                                        'cookie', 'subscribe', 'submit', 'cancel', 'back',
                                        'select container', 'select commodity', 'price owner'
                                    ];
                                    function findInShadow(root) {
                                        const items = root.querySelectorAll('li[role="option"], [role="listbox"] li, [class*="suggestion"], [class*="result"][class*="location"]');
                                        return Array.from(items);
                                    }
                                    function collectAll(node) {
                                        let found = findInShadow(node);
                                        node.querySelectorAll('*').forEach(el => {
                                            if (el.shadowRoot) found = found.concat(collectAll(el.shadowRoot));
                                        });
                                        return found;
                                    }
                                    const all = collectAll(document);
                                    for (const el of all) {
                                        const txt = (el.innerText || el.textContent || '').trim().toLowerCase();
                                        if (!txt || INVALID.some(k => txt.includes(k))) continue;
                                        el.click();
                                        return txt;
                                    }
                                    return null;
                                }
                            """)
                            if js_result:
                                print(f"[MAERSK] JS shadow-DOM click succeeded: '{js_result}'")
                                clicked = True
                                if destination_locode:
                                    set_cached_carrier_port("maersk", destination_locode, js_result)
                                await self.page.wait_for_timeout(400)
                            else:
                                print("[MAERSK] JS shadow-DOM found no items. Falling back to keyboard.")
                        except Exception as js_e:
                            print(f"[MAERSK] JS shadow-DOM fallback failed: {js_e}")

                    if not clicked:
                        try:
                            await dest_field.focus()
                            press_count = 1
                            q_lower = destination_query.lower()
                            if "karachi" in q_lower or "melbourne" in q_lower:
                                press_count = 2
                                print(f"[MAERSK] Destination Query is '{destination_query}', pressing ArrowDown {press_count} times to select CY/correct option.")
                            else:
                                print(f"[MAERSK] Sending keyboard ArrowDown+Enter to select first suggestion...")
                                
                            for _ in range(press_count):
                                await dest_field.press("ArrowDown")
                                await self.page.wait_for_timeout(300)
                                
                            await dest_field.press("Enter")
                            await self.page.wait_for_timeout(600)
                        except Exception as e:
                            print(f"[MAERSK] Keyboard selection failed: {e}")
                        
                    print("[MAERSK] Destination Port selected successfully.")
                    
                    # 2.5 Commodity selection (What do you want to ship?) - MUST BE FIRST TO UNLOCK CONTAINER OPTIONS
                    await self.page.wait_for_timeout(1000)
                    try:
                        # Scroll to shipping section to ensure visibility
                        ship_heading = self.page.locator('h3:has-text("ship"), h2:has-text("ship"), text=/What do you want to ship/i').first
                        if await ship_heading.is_visible():
                            await ship_heading.scroll_into_view_if_needed()
                            await self.page.wait_for_timeout(500)
                    except Exception:
                        pass

                    commodity_selectors = [
                        'input[placeholder*="minimum 2 characters" i]',
                        'input[placeholder*="Type in minimum" i]',
                        'input[placeholder*="commodity" i]',
                        'input#mc-input-commodity',
                        'input[id*="commodity" i]',
                        '[class*="commodity" i] input'
                    ]
                    
                    commodity_field = None
                    for selector in commodity_selectors:
                        field = self.page.locator(selector).first
                        if await field.is_visible():
                            commodity_field = field
                            print(f"[MAERSK] Found Commodity input field using: {selector}")
                            break
                            
                    if commodity_field:
                        await commodity_field.scroll_into_view_if_needed()
                        await commodity_field.click()
                        await commodity_field.fill("")
                        await commodity_field.type(request.commodity, delay=100)
                        
                        # Wait 1.5 seconds for the autocomplete suggestions to fetch and render
                        await self.page.wait_for_timeout(1500)
                        
                        commodity_suggestions_sel = (
                            'ul[role="listbox"] li, '
                            '[class*="results" i] [class*="item" i], '
                            '[class*="results" i] div, '
                            '[class*="dropdown" i] div, '
                            '[class*="dropdown" i] li, '
                            '[class*="autocomplete" i] div, '
                            '.autocomplete-suggestion, '
                            '[class*="suggestion" i], '
                            'li[role="option"]'
                        )
                        
                        clicked_commodity = False
                        try:
                            suggestion = self.page.locator(commodity_suggestions_sel).first
                            if await suggestion.is_visible():
                                tag_name = await suggestion.evaluate("el => el.tagName.toLowerCase()")
                                if tag_name != "input":
                                    await suggestion.scroll_into_view_if_needed()
                                    await suggestion.click(force=True)
                                    print("[MAERSK] Clicked commodity autocomplete suggestion element.")
                                    clicked_commodity = True
                        except Exception as e:
                            print(f"[MAERSK] Commodity dropdown click failed: {e}")
                            
                        if not clicked_commodity:
                            print("[MAERSK] Commodity dropdown click bypassed. Sending keyboard selection directly...")
                            try:
                                await commodity_field.focus()
                                await commodity_field.press("ArrowDown")
                                await self.page.wait_for_timeout(300)
                                await commodity_field.press("Enter")
                                await self.page.wait_for_timeout(500)
                            except Exception as e:
                                print(f"[MAERSK] Commodity keyboard selection failed: {e}")
                                
                        print("[MAERSK] Commodity selected successfully.")
                    else:
                        print("[MAERSK] Warning: Commodity input field not found.")

                    # 3. Container details ("How will your cargo be shipped?") - NOW UNLOCKED!
                    await self.page.wait_for_timeout(1000)
                    try:
                        # Scroll to container details section first
                        container_heading = self.page.locator('h3:has-text("shipped"), h2:has-text("shipped"), text=/How will your cargo be shipped/i').first
                        if await container_heading.is_visible():
                            await container_heading.scroll_into_view_if_needed()
                            await self.page.wait_for_timeout(500)
                    except Exception:
                        pass

                    # Click container type dropdown
                    container_field_selectors = [
                        'input[placeholder*="Select container type and size" i]',
                        '[class*="container-type" i] input',
                        '[class*="size" i] input',
                        'input[placeholder*="container type" i]'
                    ]
                    
                    container_field = None
                    for selector in container_field_selectors:
                        field = self.page.locator(selector).first
                        if await field.is_visible():
                            container_field = field
                            print(f"[MAERSK] Found Container dropdown input using: {selector}")
                            break
                            
                    if container_field:
                        await container_field.scroll_into_view_if_needed()
                        await container_field.click()
                        await self.page.wait_for_timeout(1000)
                        
                        target_type = self._map_container_type(request.container_type)
                        print(f"[MAERSK] Selecting container type: {target_type} (from {request.container_type})")
                        
                        # Find option and click it
                        option_selectors = [
                            f'ul[role="listbox"] li:has-text("{target_type}")',
                            f'[class*="option" i]:has-text("{target_type}")',
                            f'li:has-text("{target_type}")',
                            f'text="{target_type}"'
                        ]
                        
                        option_clicked = False
                        for opt_sel in option_selectors:
                            try:
                                opt = self.page.locator(opt_sel).first
                                if await opt.is_visible(timeout=2000):
                                    await opt.click(force=True)
                                    print(f"[MAERSK] Clicked container option using: {opt_sel}")
                                    option_clicked = True
                                    break
                            except Exception:
                                continue
                                
                        if not option_clicked:
                            print(f"[MAERSK] Dropdown click failed, attempting direct type or arrow navigation...")
                            await container_field.type(target_type)
                            await self.page.wait_for_timeout(500)
                            await container_field.press("Enter")
                            
                        await self.page.wait_for_timeout(1000)
                    else:
                        print("[MAERSK] Warning: Container dropdown field not found.")

                    # Set cargo weight
                    weight_selectors = [
                        'input[placeholder*="Enter cargo weight" i]',
                        'input[placeholder*="cargo weight" i]',
                        'input[placeholder*="weight" i]',
                        '[class*="weight" i] input'
                    ]
                    
                    weight_field = None
                    for selector in weight_selectors:
                        field = self.page.locator(selector).first
                        if await field.is_visible():
                            weight_field = field
                            print(f"[MAERSK] Found Cargo Weight input field using: {selector}")
                            break
                            
                    if weight_field:
                        await weight_field.scroll_into_view_if_needed()
                        await weight_field.click()
                        await weight_field.fill("")
                        weight_val = str(int(request.weight_per_container_kg))
                        await weight_field.type(weight_val, delay=100)
                        print(f"[MAERSK] Cargo weight set to: {weight_val} kg")
                        await self.page.wait_for_timeout(500)
                    else:
                        print("[MAERSK] Warning: Cargo Weight input field not found.")

                    # Set container quantity
                    qty_target = request.container_quantity
                    if qty_target > 1:
                        print(f"[MAERSK] Setting quantity to {qty_target} containers...")
                        try:
                            # Try to find increase/plus button
                            plus_btn = self.page.locator('button:has-text("+"), [class*="plus" i], [class*="increase" i], text="+"').first
                            if await plus_btn.is_visible(timeout=2000):
                                for _ in range(qty_target - 1):
                                    await plus_btn.click()
                                    await self.page.wait_for_timeout(300)
                                print(f"[MAERSK] Increased quantity by clicking + button {qty_target - 1} times.")
                            else:
                                # Try to find numeric input box and fill directly
                                qty_field = self.page.locator('input[value="1"], [class*="quantity" i] input, [class*="number" i] input').first
                                if await qty_field.is_visible():
                                    await qty_field.click()
                                    await qty_field.fill(str(qty_target))
                                    print(f"[MAERSK] Set quantity directly inside input field to {qty_target}.")
                        except Exception as e:
                            print(f"[MAERSK] Warning: Could not adjust container quantity: {e}")
                    # 3.5 Select Price Owner ("Who is the Price Owner?")
                    await self.page.wait_for_timeout(1000)
                    try:
                        price_owner_selectors = [
                            'label:has-text("I am the price owner")',
                            'text="I am the price owner"',
                            'label:has-text("I am the price owner") span',
                            'label:has-text("I am the price owner") input',
                            '[class*="price-owner" i] label'
                        ]
                        
                        for selector in price_owner_selectors:
                            btn = self.page.locator(selector).first
                            if await btn.is_visible(timeout=2000):
                                await btn.scroll_into_view_if_needed()
                                await btn.click(force=True)
                                print(f"[MAERSK] Selected Price Owner using: {selector}")
                                await self.page.wait_for_timeout(500)
                                break
                    except Exception as e:
                        print(f"[MAERSK] Warning: Could not select Price Owner: {e}")

                    # 3.8 Check for "We do not have any routes currently matching your search"
                    print("[MAERSK] Checking if the route has direct coverage or shows 'No matching routes'...")
                    no_coverage_selectors = [
                        'text="We do not have any routes currently matching your search."',
                        'text="We do not have any routes currently matching"',
                        'text="alternative route suggestions"',
                        '[class*="route" i]:has-text("do not have any routes")'
                    ]
                    
                    has_no_coverage = False
                    for selector in no_coverage_selectors:
                        try:
                            el = self.page.locator(selector).first
                            if await el.is_visible(timeout=2000):
                                print(f"[MAERSK] Route has NO coverage! Found warning message: '{selector}'")
                                has_no_coverage = True
                                break
                        except Exception:
                            continue
                            
                    if has_no_coverage:
                        print("[MAERSK] Halting automation. No direct routes matching the query exist on Maersk Spot.")
                        return CarrierResultStatus.NO_QUOTES_AVAILABLE

                    # 4. Click Search / Show rates button
                    await self.page.wait_for_timeout(1000)
                    search_selectors = [
                        'button:has-text("Show rates")',
                        'button:has-text("Show results")',
                        'button:has-text("Search")',
                        'button:has-text("Continue")',
                        'button[class*="search" i]',
                        'button[class*="submit" i]',
                        'button[type="submit"]',
                        'a:has-text("Show rates")',
                        'a:has-text("Search")'
                    ]
                    
                    search_btn = None
                    for selector in search_selectors:
                        btn = self.page.locator(selector).first
                        if await btn.is_visible():
                            search_btn = btn
                            print(f"[MAERSK] Found Search/Submit button using: {selector}")
                            break
                            
                    if search_btn:
                        await search_btn.click(force=True)
                        print("[MAERSK] Clicked Search/Show Rates button successfully.")
                    else:
                        print("[MAERSK] Warning: Search/Show Rates button not found or already clicked.")

                    # 4.5 Select Ready Date ("Select tomorrow")
                    await self.page.wait_for_timeout(2000)
                    select_tomorrow_selectors = [
                        'button:has-text("Select tomorrow")',
                        'a:has-text("Select tomorrow")',
                        'text="Select tomorrow"',
                        '[class*="tomorrow" i]'
                    ]
                    
                    tomorrow_clicked = False
                    for selector in select_tomorrow_selectors:
                        try:
                            btn = self.page.locator(selector).first
                            if await btn.is_visible(timeout=5000):
                                await btn.scroll_into_view_if_needed()
                                await btn.click(force=True)
                                print(f"[MAERSK] Clicked Select Tomorrow using: {selector}")
                                tomorrow_clicked = True
                                break
                        except Exception:
                            continue
                            
                    # 4.6 Click "Continue to book" / "Price booking" with retry on temporary system error banner
                    continue_book_selectors = [
                        'button:has-text("Continue to book")',
                        'a:has-text("Continue to book")',
                        'button:has-text("Price booking")',
                        'a:has-text("Price booking")',
                        'text="Price booking"',
                        'text="Continue to book"',
                        '[class*="continue" i]'
                    ]
                    
                    max_retries = 5
                    for attempt in range(max_retries):
                        await self.page.wait_for_timeout(1000)
                        continue_clicked = False
                        
                        for selector in continue_book_selectors:
                            try:
                                btn = self.page.locator(selector).first
                                if await btn.is_visible(timeout=5000):
                                    # Ensure button is not disabled before clicking
                                    is_disabled = await btn.evaluate("el => el.disabled || el.getAttribute('aria-disabled') === 'true'")
                                    if is_disabled:
                                        print(f"[MAERSK] Button {selector} is disabled, waiting 2 seconds...")
                                        await self.page.wait_for_timeout(2000)
                                    
                                    await btn.scroll_into_view_if_needed()
                                    await btn.click(force=True)
                                    print(f"[MAERSK] Clicked Submit Form (Attempt {attempt + 1}/{max_retries}) using: {selector}")
                                    continue_clicked = True
                                    break
                            except Exception:
                                continue
                                
                        if not continue_clicked:
                            print("[MAERSK] Warning: Submit Form button not found or already submitted.")
                            
                        # Wait 3 seconds to see if the temporary system error banner appears
                        await self.page.wait_for_timeout(3000)
                        
                        # Check for system error banners/texts
                        error_selectors = [
                            'text="Due to a temporary issue in our systems"',
                            'text="not able to process your request"',
                            'text="apologize for this inconvenience"',
                            '[class*="error" i]:has-text("temporary")',
                            '[class*="banner" i]:has-text("temporary")'
                        ]
                        
                        error_detected = False
                        for err_sel in error_selectors:
                            try:
                                banner = self.page.locator(err_sel).first
                                if await banner.is_visible(timeout=1000):
                                    print(f"[MAERSK] Detected temporary system error banner! ('{err_sel}')")
                                    error_detected = True
                                    break
                            except Exception:
                                continue
                                
                        if error_detected:
                            print(f"[MAERSK] Maersk API reports a temporary issue. Waiting 5 seconds before retrying Submit Form...")
                            await self.page.wait_for_timeout(5000)
                            # Let the loop continue and click again!
                        else:
                            # No error banner detected, we are good to go!
                            print("[MAERSK] No temporary system error detected. Proceeding...")
                            break

                    autofill_success = True
                else:
                    raise Exception("Destination Port input field not found")

            except Exception as e:
                print(f"[MAERSK] Autofill skipped or failed ({e}). Entering Human-in-the-Loop Search Helper...")

            # Fallback HITL loop for the search page
            if not autofill_success:
                print("[MAERSK] [ACTION REQUIRED] Could not auto-fill booking ports.")
                print("[MAERSK] Please click on 'From' to select Origin and 'To' to select Destination in the Chrome window.")
                print("[MAERSK] Waiting for the results page to load...")

            # Wait for results to appear (look for sailing schedules, pricing, or selection container)
            results_loaded = False
            for i in range(90):
                await asyncio.sleep(1)
                curr_url = self.page.url
                
                # Check for "There are no sailings for your search" pink banner
                no_sailings_selectors = [
                    'text="There are no sailings for your search."',
                    'text="no sailings for your search"',
                    'text="changing the transportation mode (CY or SD)"',
                    '[class*="alert" i]:has-text("no sailings")',
                    '[class*="banner" i]:has-text("no sailings")',
                    '[class*="error" i]:has-text("no sailings")'
                ]
                
                no_sailings_detected = False
                for no_sail_sel in no_sailings_selectors:
                    try:
                        banner = self.page.locator(no_sail_sel).first
                        if await banner.is_visible(timeout=500):
                            print(f"[MAERSK] Zero quotes! Found 'No sailings' banner: '{no_sail_sel}'")
                            no_sailings_detected = True
                            break
                    except Exception:
                        continue
                        
                if no_sailings_detected:
                    print("[MAERSK] Halting automation. Maersk Spot explicitly reports no sailings are available.")
                    return CarrierResultStatus.NO_QUOTES_AVAILABLE
                
                # 1. Primary check: check for a real, fully-rendered sailing quote card with text
                real_cards = self.page.locator('article.new-sailings-card-article, article.sailings__card, [class*="offer-card" i], [class*="result-card" i], [class*="schedule-card" i], .c-offer-card')
                real_card_count = await real_cards.count()
                real_card_loaded = False
                if real_card_count > 0:
                    for c_idx in range(min(real_card_count, 3)):
                        try:
                            card_text = await real_cards.nth(c_idx).inner_text(timeout=500)
                            card_text_lower = card_text.lower()
                            if "departure" in card_text_lower and ("usd" in card_text_lower or "$" in card_text_lower or "eur" in card_text_lower or "price" in card_text_lower):
                                real_card_loaded = True
                                break
                        except Exception:
                            continue
                
                # 2. Secondary fallback checks for pages with other layouts/indicators
                indicator_visible = False
                indicators = [
                    'text="Price breakdown & details"',
                    'text="Vessel/voyage"',
                    'text="Departure"',
                    'text="Transit time"'
                ]
                for ind in indicators:
                    try:
                        if await self.page.locator(ind).first.is_visible(timeout=200):
                            indicator_visible = True
                            break
                    except Exception:
                        continue

                # 3. Resolve results loaded status
                cards_count = await self.page.locator('[class*="offer" i], [class*="result" i], [class*="card" i], [class*="sailing" i], .c-offer-card').count()
                
                is_results_url = any(word in curr_url.lower() for word in ["sailings", "schedules", "select-sailing", "results"])
                
                ready = False
                if is_results_url and real_card_loaded:
                    print(f"[MAERSK] Confirmed real quote card fully rendered on page!")
                    ready = True
                elif i >= 15:  # Fallback to URL and broad counts after 15 seconds of waiting
                    if (cards_count > 0 or is_results_url or "price" in curr_url.lower()) and "/book/" not in curr_url.lower():
                        print(f"[MAERSK] Fallback loading check succeeded after 15s wait (URL: {curr_url}).")
                        ready = True
                
                if ready:
                    print(f"[MAERSK] Results loaded successfully! Found {cards_count} options (URL: {curr_url}).")
                    try:
                        html = await self.page.content()
                        import os
                        os.makedirs("scratch", exist_ok=True)
                        with open("scratch/debug_results.html", "w", encoding="utf-8") as f:
                            f.write(html)
                        print("[MAERSK] Saved results page HTML to scratch/debug_results.html")
                    except Exception as e:
                        print(f"[MAERSK] Warning: Could not save results page HTML: {e}")
                    results_loaded = True
                    break
                
                if i % 15 == 14:
                    print(f"[MAERSK] Still waiting for results page to load... {90 - i - 1} seconds remaining.")

            if not results_loaded:
                print("[MAERSK] [TIMEOUT] Results page did not load.")
                return CarrierResultStatus.TIMEOUT

            return CarrierResultStatus.AVAILABLE_QUOTES_FOUND

        except Exception as e:
            print(f"[MAERSK] Search quotes failed: {e}")
            return CarrierResultStatus.UNKNOWN_ERROR

    # ────────────────────────────────────────
    # EXTRACT QUOTATION LIST
    # ────────────────────────────────────────

    async def extract_quote_list(self) -> list[dict]:
        try:
            # Quick check for "There are no sailings for your search" pink banner
            no_sailings_selectors = [
                'text="There are no sailings for your search."',
                'text="no sailings for your search"',
                'text="changing the transportation mode (CY or SD)"',
                '[class*="alert" i]:has-text("no sailings")',
                '[class*="banner" i]:has-text("no sailings")',
                '[class*="error" i]:has-text("no sailings")'
            ]
            
            for no_sail_sel in no_sailings_selectors:
                try:
                    banner = self.page.locator(no_sail_sel).first
                    if await banner.is_visible(timeout=1000):
                        print(f"[MAERSK] Early Exit: Found 'No sailings' banner ('{no_sail_sel}'). Returning empty quote list.")
                        return []
                except Exception:
                    continue

            # Wait for the real sailing cards to appear in the DOM (up to 20s)
            quote_cards = self.page.locator('article.new-sailings-card-article')
            try:
                await quote_cards.first.wait_for(state="visible", timeout=20000)
                print("[MAERSK] Confirmed article.new-sailings-card-article is visible.")
            except Exception:
                print("[MAERSK] Warning: article.new-sailings-card-article not visible after 20s wait. Trying fallback selectors.")
                quote_cards = self.page.locator('article.sailings__card, [class*="new-sailings-routes-offer-card" i], [class*="new-sailings-product-offer-card" i]')

            count = await quote_cards.count()
            if count == 0:
                print("[MAERSK] No sailing cards found with primary selectors.")
                return []

            print(f"[MAERSK] Found {count} raw quotation card(s) on page.")
            quotes = []

            for index in range(count):
                card = quote_cards.nth(index)
                try:
                    card_text = (await card.inner_text(timeout=5000)).strip()
                except Exception as card_e:
                    print(f"[MAERSK] Warning: Failed to get card text at index {index}: {card_e}")
                    continue
                card_text_lower = card_text.lower()
                if "vessel sold out" in card_text_lower or "vessel not open" in card_text_lower or "vessel is not open" in card_text_lower:
                    print(f"[MAERSK] Skipping card at index {index} - Vessel sold out or not open.")
                    continue

                # --- Price: try data-test selector first, then regex fallback ---
                total_price = 0.0
                try:
                    price_el = card.locator('[data-test="product-offer-price"] p, .product-offer-price p, .mds-price-breakdown').first
                    price_text = (await price_el.inner_text(timeout=2000)).strip()
                    price_match = re.search(r"([\d,]+\.?\d{0,2})", price_text)
                    if price_match:
                        total_price = float(price_match.group(1).replace(",", ""))
                except Exception:
                    # fallback to regex on full card text
                    price_match = re.search(r"(?:USD|\$)\s*([\d,]+\.?\d{0,2})", card_text, re.IGNORECASE)
                    if price_match:
                        total_price = float(price_match.group(1).replace(",", ""))

                if total_price <= 0:
                    print(f"[MAERSK] Skipping card {index} - no valid price found.")
                    continue

                # --- Departure date: try <time datetime> attribute first ---
                etd = date.today().isoformat()
                eta = (date.today() + timedelta(days=20)).isoformat()
                try:
                    depart_time = card.locator('.new-sailings-card-date time, .new-sailings-group-header__departure-section time').first
                    depart_dt = await depart_time.get_attribute("datetime", timeout=1000)
                    if depart_dt:
                        etd = depart_dt[:10]  # take just YYYY-MM-DD
                except Exception:
                    # fallback to text pattern
                    dates = re.findall(r"\d{1,2}\s+[A-Za-z]{3}\s+\d{4}|\d{4}-\d{2}-\d{2}", card_text)
                    if dates:
                        etd = dates[0]

                # --- Transit time: try durationinhours attribute first ---
                transit_time = 20
                try:
                    dur_el = card.locator('mc-c-duration-display[durationinhours]').first
                    dur_hours = await dur_el.get_attribute("durationinhours", timeout=1000)
                    if dur_hours:
                        transit_time = max(1, round(int(dur_hours) / 24))
                except Exception:
                    transit_match = re.search(r"(\d+)\s*day", card_text, re.IGNORECASE)
                    if transit_match:
                        transit_time = int(transit_match.group(1))

                # ETA = ETD + transit_time
                try:
                    from datetime import date as _date, timedelta as _td
                    etd_parsed = _date.fromisoformat(etd[:10])
                    eta = (etd_parsed + _td(days=transit_time)).isoformat()
                except Exception:
                    pass

                # --- Vessel / service name ---
                vessel = "Maersk Vessel"
                try:
                    vessel_el = card.locator('[data-test*="vessel" i], .new-sailings-group-header__vessel-section .new-sailings-group-header__value').first
                    vessel_text = (await vessel_el.inner_text(timeout=1000)).strip()
                    if vessel_text:
                        vessel = vessel_text
                except Exception:
                    vessel_match = re.search(r"vessel:\s*([A-Za-z0-9 ]+)|service:\s*([A-Za-z0-9 ]+)", card_text, re.IGNORECASE)
                    if vessel_match:
                        vessel = (vessel_match.group(1) or vessel_match.group(2)).strip()

                quotes.append({
                    "index": index,
                    "etd": etd,
                    "eta": eta,
                    "transit_time_days": transit_time,
                    "service_name": "Maersk Spot Service",
                    "vessel": vessel,
                    "total_price": total_price,
                    "currency": "USD",
                    "card_text": card_text[:500]  # truncate for logging
                })
                print(f"[MAERSK] Parsed card {index}: ETD={etd}, transit={transit_time}d, price=USD {total_price}")

            print(f"[MAERSK] Parsed {len(quotes)} valid quote(s) successfully.")
            return quotes

        except Exception as e:
            print(f"[MAERSK] Error extracting quote list: {e}")
            return []

    # ────────────────────────────────────────
    # ACCORDION & DETAIL CHARGES EXTRACTOR
    # ────────────────────────────────────────

    async def open_price_breakdown(self, quote_ref: dict) -> bool:
        try:
            idx = quote_ref.get("index", 0)
            
            # Locate the specific card container first for perfect scoping
            card_selectors = [
                'article.new-sailings-card-article',
                'article.sailings__card',
                '[class*="offer-card" i]',
                '[class*="result-card" i]',
                '[class*="schedule-card" i]',
                '.c-offer-card',
                '.card',
                '.result-row',
                '[class*="card" i]'
            ]
            
            card = None
            for card_sel in card_selectors:
                try:
                    locator = self.page.locator(card_sel)
                    if await locator.count() > idx:
                        card = locator.nth(idx)
                        break
                except Exception:
                    continue
            
            details_btn = None
            selectors_to_try = [
                'span.hyperlink-button:has-text("Price breakdown")',
                '.hyperlink-button:has-text("Price breakdown")',
                'button:has-text("Price breakdown & details")',
                'a:has-text("Price breakdown & details")',
                'span:has-text("Price breakdown & details")',
                'div:has-text("Price breakdown & details")',
            ]
            
            if card:
                for sel in selectors_to_try:
                    try:
                        btn = card.locator(sel).first
                        if await btn.is_visible(timeout=1000):
                            details_btn = btn
                            break
                    except Exception:
                        continue
            else:
                for sel in selectors_to_try:
                    try:
                        btn = self.page.locator(sel).nth(idx)
                        if await btn.is_visible(timeout=1000):
                            details_btn = btn
                            break
                    except Exception:
                        continue
                
            if details_btn:
                await details_btn.scroll_into_view_if_needed()
                await details_btn.click(force=True)
                await self.page.wait_for_timeout(2000)
                print(f"[MAERSK] Price breakdown details expanded for quote {idx}.")
                return True
            
            print(f"[MAERSK] Info: Details button not found or already open for quote {idx}.")
            return True
        except Exception as e:
            print(f"[MAERSK] Failed to open breakdown details: {e}")
            return False

    async def extract_charge_breakdown(self, card_locator=None) -> list[dict]:
        try:
            charges = []
            
            # Recursive helper to flatten the accessibility tree into lines of text
            def flatten_tree(node) -> list[str]:
                lines_list = []
                name = node.get("name")
                role = node.get("role", "")
                
                # We want text or list/table content
                if name and isinstance(name, str) and name.strip():
                    lines_list.append(name.strip())
                
                for child in node.get("children", []):
                    lines_list.extend(flatten_tree(child))
                return lines_list

            # Dynamic Wait Loop: Wait up to 5 seconds (10 attempts * 500ms) for the breakdown table to fully render.
            # We know it is fully rendered when the accessibility tree contains "freight charges"
            # AND a currency indicator (like USD, SGD, EUR, INR).
            snapshot = None
            lines = []
            print("[MAERSK] Capturing live page accessibility snapshot with dynamic rendering wait...")
            for attempt in range(10):
                snapshot = await self.page.accessibility.snapshot()
                if snapshot:
                    lines = flatten_tree(snapshot)
                    has_freight = any("freight charges" in l.lower() for l in lines)
                    has_currency = any(c in [l.upper() for l in lines] for c in ["USD", "SGD", "EUR", "INR"])
                    if has_freight and has_currency:
                        print(f"[MAERSK] Breakdown table content detected after {attempt * 0.5} seconds!")
                        break
                await asyncio.sleep(0.5)
            
            if snapshot:
                
                # Debug: Write live flattened accessibility tree to file
                try:
                    debug_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scratch")
                    os.makedirs(debug_dir, exist_ok=True)
                    with open(os.path.join(debug_dir, f"debug_live_accessibility_{int(asyncio.get_event_loop().time())}.txt"), "w", encoding="utf-8") as f:
                        f.write("\n".join(lines))
                    print(f"[MAERSK] Saved live accessibility tree lines (total: {len(lines)})")
                except Exception as de:
                    print(f"[MAERSK] Failed to write debug live accessibility file: {de}")
                
                # Parse the flattened accessibility lines
                current_section = "freight charges"
                amount_pattern = re.compile(r"^(\d[\d,]*\.?\d*)$")
                currency_pattern = re.compile(r"^(USD|SGD|EUR|INR|GBP|AUD|CNY|JPY|HKD|MYR)$")
                
                i = 0
                while i < len(lines):
                    line = lines[i]
                    line_lower = line.lower()
                    
                    # Detect section headers
                    if "freight charges" in line_lower:
                        current_section = "freight charges"
                        i += 1
                        continue
                    elif "origin charges" in line_lower:
                        current_section = "origin charges"
                        i += 1
                        continue
                    elif "destination charges" in line_lower:
                        current_section = "destination charges"
                        i += 1
                        continue
                    elif line_lower in ("basis", "quantity", "currency", "unit price", "total price"):
                        i += 1
                        continue
                    elif line_lower == "total price" or "total price" in line_lower:
                        i += 1
                        continue
                    
                    # Check for pattern: Name | Basis | Qty | Currency | UnitPrice | TotalPrice
                    if (i + 5) < len(lines):
                        name_candidate = line
                        basis = lines[i+1]
                        qty_str = lines[i+2]
                        currency_candidate = lines[i+3]
                        unit_price_str = lines[i+4]
                        total_price_str = lines[i+5]
                        
                        if (currency_pattern.match(currency_candidate) and
                            amount_pattern.match(qty_str) and
                            amount_pattern.match(total_price_str) and
                            len(name_candidate) > 2 and
                            not any(kw in name_candidate.lower() for kw in ["charges", "basis", "quantity", "currency", "price"])):
                            
                            amount = float(total_price_str.replace(",", ""))
                            category, reason = classify_charge(name_candidate, amount, current_section)
                            charges.append({
                                "name": name_candidate,
                                "amount": amount,
                                "currency": currency_candidate,
                                "category": category.value,
                                "reason": reason,
                            })
                            print(f"[MAERSK] Accessibility Parsed: {name_candidate} -> {amount} {currency_candidate} ({current_section})")
                            i += 6
                            continue
                    
                    i += 1
                
                if charges:
                    print(f"[MAERSK] Successfully extracted {len(charges)} charges using live accessibility tree.")
                    return charges
            
            # Step 2: Fallback — read the expanded card's inner_text and parse line by line
            print("[MAERSK] Accessibility tree extraction empty or failed, falling back to card text parsing...")
            
            
            text = ""
            if card_locator:
                text = await card_locator.inner_text()
            else:
                text = await self.page.locator("body").inner_text()
            
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            
            # Debug log
            try:
                debug_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scratch")
                os.makedirs(debug_dir, exist_ok=True)
                with open(os.path.join(debug_dir, f"debug_maersk_fallback_{int(asyncio.get_event_loop().time())}.txt"), "w", encoding="utf-8") as f:
                    f.write("\n".join(lines))
            except Exception:
                pass
            
            amount_pattern = re.compile(r"(?:^|\s)([A-Z]{3})\s*([\d,]+\.\d{2})$")

            def is_section_heading(line: str) -> bool:
                n = line.strip().lower()
                return "charge" in n or "freight" in n or "origin" in n or "destination" in n

            for index, line in enumerate(lines):
                amount_match = amount_pattern.search(line)
                if not amount_match:
                    continue
                currency = amount_match.group(1)
                amount = float(amount_match.group(2).replace(",", ""))
                remaining_line = line[:amount_match.start()].strip()
                name = remaining_line
                if not name and index > 0:
                    candidate_name = lines[index - 1].strip()
                    if not amount_pattern.search(candidate_name) and not is_section_heading(candidate_name):
                        name = candidate_name
                if not name:
                    name = f"Surcharge {len(charges) + 1}"
                section_heading = "freight charges"
                sec_index = index - 1
                while sec_index >= 0:
                    candidate = lines[sec_index]
                    if is_section_heading(candidate):
                        section_heading = candidate.strip().lower()
                        break
                    sec_index -= 1
                category, reason = classify_charge(name, amount, section_heading)
                charges.append({
                    "name": name,
                    "amount": amount,
                    "currency": currency,
                    "category": category.value,
                    "reason": reason,
                })

            print(f"[MAERSK] Parsed {len(charges)} charges from fallback text breakdown.")
            return charges
        except Exception as e:
            print(f"[MAERSK] Error parsing charge breakdown: {e}")
            return []

    # ────────────────────────────────────────
    # NORMALIZE QUOTE
    # ────────────────────────────────────────

    async def normalize_result(self, raw_quote: dict, raw_charges: list[dict]) -> QuoteSchema:
        return normalize_quote(self.carrier_code, raw_quote, raw_charges)

    # ────────────────────────────────────────
    # BROWSER TEARDOWN
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

        # Concurrency cleanup: Copy successful login data back to master profile and remove temporary profile directory
        try:
            import shutil
            if self.temp_profile_dir and os.path.exists(self.temp_profile_dir):
                if self.is_login_successful and self.master_profile_dir:
                    print(f"[MAERSK] Login was successful or restored. Syncing temporary profile back to master: {self.master_profile_dir}")
                    # Clear master directory safely
                    if os.path.exists(self.master_profile_dir):
                        try:
                            shutil.rmtree(self.master_profile_dir)
                        except Exception:
                            pass
                    # Copy temp directory contents back to master
                    try:
                        shutil.copytree(self.temp_profile_dir, self.master_profile_dir, dirs_exist_ok=True)
                        # Remove Chromium lock files from the master copy
                        lock_files = ["SingletonLock", "lock", "SingletonCookie"]
                        for root_dir, _, filenames in os.walk(self.master_profile_dir):
                            for filename in filenames:
                                if filename in lock_files:
                                    try:
                                        os.remove(os.path.join(root_dir, filename))
                                    except Exception:
                                        pass
                        print("[MAERSK] Master profile updated with fresh session data.")
                        
                        # Auto-clean heavy cache directories to prevent 5GB storage bloat
                        cache_dirs = ["Cache", "Code Cache", "DawnCache", "GPUCache", "CacheStorage", "ScriptCache"]
                        for root_dir, dirs, _ in os.walk(self.master_profile_dir):
                            for d in list(dirs):
                                if d in cache_dirs:
                                    try:
                                        shutil.rmtree(os.path.join(root_dir, d))
                                    except Exception:
                                        pass
                    except Exception as copy_err:
                        print(f"[MAERSK] Failed to sync profile to master: {copy_err}")
                
                # Delete temporary directory completely
                print(f"[MAERSK] Cleaning up temporary isolated profile directory: {self.temp_profile_dir}")
                try:
                    shutil.rmtree(self.temp_profile_dir)
                except Exception as rmtree_err:
                    print(f"[MAERSK] Failed to clean up temp profile directory: {rmtree_err}")
        except Exception as e:
            print(f"[MAERSK] Failed during profile synchronization and cleanup: {e}")
