"""
Base Carrier Connector — abstract base class for all carrier connectors.

Each carrier connector must implement these methods to integrate with
the carrier's quote portal via Playwright browser automation.
"""
from abc import ABC, abstractmethod
from typing import Optional, Any
import asyncio
from models.schemas import RateSearchRequest, QuoteSchema, CarrierResultStatus


class BaseCarrierConnector(ABC):
    """Abstract base class for carrier portal connectors."""

    carrier_code: str = "UNKNOWN"
    carrier_name: str = "Unknown Carrier"

    def __init__(self):
        self.browser = None
        self.page = None
        self.context = None
        self.captcha_detected = False
        self.status_update_callback = None
        self.submitted_origin: Optional[str] = None
        self.submitted_destination: Optional[str] = None
        self.matched_origin: Optional[str] = None
        self.matched_destination: Optional[str] = None


    @abstractmethod
    async def login(self) -> bool:
        """
        Log into the carrier portal.

        Returns:
            True if login successful, False otherwise.
        """
        pass

    @abstractmethod
    async def search_quotes(self, request: RateSearchRequest) -> CarrierResultStatus:
        """
        Fill in the carrier's search form and submit a quote search.

        Args:
            request: The rate search parameters from the employee.

        Returns:
            CarrierResultStatus indicating the search result status.
        """
        pass

    @abstractmethod
    async def extract_quote_list(self) -> list[dict]:
        """
        Extract the list of available quotes from the search results page.

        Returns:
            List of raw quote dicts (etd, eta, transit_time_days, service_name, vessel, etc.)
        """
        pass

    @abstractmethod
    async def open_price_breakdown(self, quote_ref: dict) -> bool:
        """
        Open the price breakdown / detail view for a specific quote.

        Args:
            quote_ref: Reference dict for the quote to open.

        Returns:
            True if the breakdown was opened successfully.
        """
        pass

    @abstractmethod
    async def extract_charge_breakdown(self) -> list[dict]:
        """
        Extract individual charge line items from the price breakdown.

        Returns:
            List of dicts with keys: name, amount, currency
        """
        pass

    @abstractmethod
    async def normalize_result(
        self,
        raw_quote: dict,
        raw_charges: list[dict],
    ) -> QuoteSchema:
        """
        Normalize extracted data into a QuoteSchema using the normalizer.

        Args:
            raw_quote: Raw quote data dict.
            raw_charges: List of raw charge line items.

        Returns:
            Normalized QuoteSchema.
        """
        pass

    async def check_captcha_challenge(self) -> bool:
        """
        Detects if a CAPTCHA, Turnstile, hCaptcha, reCAPTCHA, or 2FA screen
        is currently visible on the active page.
        """
        if not self.page or (self.page.is_closed() if hasattr(self.page, "is_closed") and callable(self.page.is_closed) else getattr(self.page, "is_closed", False)):
            raise Exception("Playwright page is closed or crashed.")
        try:
            # If standard login fields (email/username and password inputs) are visible,
            # we are on the login form and should not treat the page as blocked by a CAPTCHA challenge.
            try:
                email_selectors = ['input#signInName', 'input#email', 'input[type="email"]', 'input[name*="username" i]']
                pass_selectors = ['input#password', 'input[type="password"]', 'input[name*="password" i]']
                
                has_email = False
                for sel in email_selectors:
                    if await self.page.locator(sel).first.is_visible(timeout=50):
                        has_email = True
                        break
                
                has_pass = False
                for sel in pass_selectors:
                    if await self.page.locator(sel).first.is_visible(timeout=50):
                        has_pass = True
                        break
                        
                if has_email and has_pass:
                    return False
            except:
                pass

            is_challenge = False
            
            # 1. Check page title and URL for common challenge patterns
            url = self.page.url.lower()
            title = (await self.page.title()).lower()
            if any(k in url or k in title for k in ["challenge", "turnstile", "captcha", "recaptcha", "hcaptcha", "arkose", "funcaptcha", "just a moment", "security check", "managed challenge"]):
                is_challenge = True

            # 2. Check for Cloudflare/Akamai/Arkose challenge markers
            if not is_challenge:
                cf_selectors = [
                    'iframe[src*="cloudflare" i]',
                    'iframe[src*="challenges" i]',
                    'iframe[src*="recaptcha" i]',
                    'iframe[src*="hcaptcha" i]',
                    'iframe[src*="arkose" i]',
                    'iframe[src*="funcaptcha" i]',
                    '#cf-turnstile',
                    '#challenge-running',
                    '.g-recaptcha',
                    '#captcha-container',
                    '[class*="captcha" i]',
                    '[id*="captcha" i]',
                    '[src*="turnstile" i]',
                    'div[class*="arkose" i]'
                ]
                for sel in cf_selectors:
                    try:
                        if await self.page.locator(sel).first.is_visible(timeout=100):
                            is_challenge = True
                            break
                    except Exception:
                        pass

            # 3. Check for 2FA / Verification code input fields
            if not is_challenge:
                two_factor_selectors = [
                    'input[id*="verificationCode" i]',
                    'input[name*="code" i]',
                    'input[id*="otp" i]',
                    'input[placeholder*="verification code" i]',
                    'input[placeholder*="security code" i]',
                    'input[placeholder*="OTP" i]'
                ]
                for sel in two_factor_selectors:
                    try:
                        if await self.page.locator(sel).first.is_visible(timeout=100):
                            is_challenge = True
                            break
                    except Exception:
                        pass

            # 4. Check for common challenge text on page
            if not is_challenge:
                body_text = (await self.page.locator("body").inner_text(timeout=200)).lower()
                challenge_phrases = [
                    "verify your identity",
                    "verification code",
                    "two-factor authentication",
                    "enter security code",
                    "enter the code",
                    "confirm 2fa",
                    "verify you are human",
                    "security verification",
                    "robot check",
                    "one-time password",
                    "otp code",
                    "drag the letter",
                    "where it fits",
                    "drag the slider",
                    "slide to verify",
                    "select the shadow",
                    "solve the puzzle",
                    "complete the security check",
                    "press and hold",
                    "security check",
                    "managed challenge",
                    "just a moment..."
                ]
                if any(phrase in body_text for phrase in challenge_phrases):
                    is_challenge = True

            if is_challenge:
                if not self.captcha_detected:
                    self.captcha_detected = True
                    if self.status_update_callback:
                        asyncio.create_task(self.status_update_callback(CarrierResultStatus.WAITING_FOR_HUMAN_VERIFICATION))
                return True

        except Exception:
            pass
        return False

    async def close(self, force: bool = False):
        """Clean up browser resources robustly, ensuring failures or hangs never block execution."""
        if getattr(self, "is_batch_active", False) and not force:
            # Keep browser session open during persistent batch execution
            return
        try:
            if self.page:
                try:
                    await asyncio.wait_for(self.page.close(), timeout=2.0)
                except Exception:
                    pass
        except:
            pass

        try:
            if self.context:
                try:
                    await asyncio.wait_for(self.context.close(), timeout=2.0)
                except Exception:
                    pass
        except:
            pass

        try:
            if self.browser:
                try:
                    await asyncio.wait_for(self.browser.close(), timeout=2.0)
                except Exception:
                    pass
        except:
            pass

        try:
            if hasattr(self, "playwright") and self.playwright:
                try:
                    await asyncio.wait_for(self.playwright.stop(), timeout=3.0)
                except Exception:
                    pass
        except:
            pass

    def filter_cheapest_in_14d_window(
        self,
        raw_quotes: list[dict],
        departure_date_val: Optional[str] = None
    ) -> list[dict]:
        """
        Quick Search Filter:
        1. Identifies target start date (today, tomorrow, or ISO date).
        2. Filters raw quotes for ETD within [start_date, start_date + 14 days].
        3. Selects the single cheapest quote card by summary price.
        4. If none in 14 days, picks the cheapest within 28 days as fallback.
        """
        if not raw_quotes:
            return []

        from datetime import date, timedelta

        def _resolve_start(dep_val):
            today_d = date.today()
            if not dep_val:
                return today_d
            val = str(dep_val).strip().lower()
            if val in ("today", "now"):
                return today_d
            if val == "tomorrow":
                return today_d + timedelta(days=1)
            try:
                return date.fromisoformat(val[:10])
            except:
                return today_d

        start_date = _resolve_start(departure_date_val)
        window_14d = start_date + timedelta(days=14)
        window_28d = start_date + timedelta(days=28)

        def _get_price(q: dict) -> float:
            for p_key in ("total_price", "final_freight_value", "basic_ocean_freight", "price", "rate", "usd_price"):
                val = q.get(p_key)
                if val is not None:
                    try:
                        return float(str(val).replace(",", "").replace("$", ""))
                    except:
                        pass
            return 999999.0

        def _get_etd_date(q: dict) -> Optional[date]:
            for d_key in ("etd_standardized", "etd", "etd_date", "etd_date_raw"):
                val = q.get(d_key)
                if val:
                    try:
                        val_str = str(val).strip()[:10]
                        return date.fromisoformat(val_str)
                    except:
                        pass
                    # Try MM/DD/YYYY
                    if "/" in str(val):
                        parts = str(val).strip().split("/")
                        if len(parts) == 3:
                            try:
                                return date(int(parts[2]), int(parts[0]), int(parts[1]))
                            except:
                                pass
            return None

        # 1. First pass: quotes strictly within [start_date, start_date + 14 days]
        in_14d = []
        in_28d = []
        for q in raw_quotes:
            if q.get("is_sold_out"):
                continue
            q_date = _get_etd_date(q)
            if q_date:
                if start_date <= q_date <= window_14d:
                    in_14d.append(q)
                elif start_date <= q_date <= window_28d:
                    in_28d.append(q)
            else:
                # If date could not be parsed, keep in 28d bucket
                in_28d.append(q)

        pool = in_14d if in_14d else (in_28d if in_28d else raw_quotes)
        # Pick the lowest price quote
        cheapest_quote = min(pool, key=_get_price)
        print(f"[{self.carrier_code}] [Quick Search] Filtered {len(raw_quotes)} cards -> selected cheapest quote (Price: {_get_price(cheapest_quote)}, ETD: {cheapest_quote.get('etd') or cheapest_quote.get('etd_standardized')})")
        return [cheapest_quote]

    async def run_full_search(self, request: RateSearchRequest) -> tuple[CarrierResultStatus, list[QuoteSchema]]:
        """
        Execute the full search flow:
        1. Login
        2. Search quotes
        3. Extract quote list
        4. For each quote: open breakdown → extract charges → normalize
        5. Return all normalized quotes

        Returns:
            Tuple of (status, list of QuoteSchema)
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

            # Step 3: Extract quote list
            raw_quotes = await self.extract_quote_list()
            if not raw_quotes:
                return CarrierResultStatus.NO_QUOTES_AVAILABLE, []

            # Apply Quick Search filter if requested
            if getattr(request, "search_mode", "detailed") == "quick":
                raw_quotes = self.filter_cheapest_in_14d_window(raw_quotes, request.departure_date)
                # ULTRA-FAST QUICK SEARCH: Capture final freight price only (no modals, no breakdown, no freetime, no TT)
                for raw_quote in raw_quotes:
                    price_val = float(raw_quote.get("total_price") or raw_quote.get("final_freight_value") or raw_quote.get("price") or 0.0)
                    c_types = request.container_types or ["DRY 20", "DRY 40"]
                    for ct in c_types:
                        quotes.append(QuoteSchema(
                            container_type=ct,
                            container_quantity=1,
                            currency=raw_quote.get("currency", "USD"),
                            basic_ocean_freight=price_val,
                            discount=0.0,
                            final_freight_value=price_val,
                            included_freight_surcharges=[],
                            excluded_charges=[],
                            uncertain_charges=[],
                            source=self.carrier_code
                        ))
                if quotes:
                    return CarrierResultStatus.AVAILABLE_QUOTES_FOUND, quotes
                else:
                    return CarrierResultStatus.EXTRACTION_FAILED, []

            # Step 4: For each quote, get breakdown and normalize (Detailed Mode)
            for raw_quote in raw_quotes:
                try:
                    opened = await self.open_price_breakdown(raw_quote)
                    raw_charges = []
                    if opened:
                        raw_charges = await self.extract_charge_breakdown()
                        
                    if hasattr(self, "_split_raw_quote_by_container_types") and callable(getattr(self, "_split_raw_quote_by_container_types")):
                        split_res = await self._split_raw_quote_by_container_types(raw_quote, raw_charges)
                        if split_res:
                            quotes.extend(split_res)
                        else:
                            normalized = await self.normalize_result(raw_quote, raw_charges)
                            quotes.append(normalized)
                    else:
                        normalized = await self.normalize_result(raw_quote, raw_charges)
                        quotes.append(normalized)
                except Exception as e:
                    # Log but don't fail the entire search for one quote
                    print(f"[{self.carrier_code}] Error extracting quote: {e}")
                    continue

            if quotes:
                return CarrierResultStatus.AVAILABLE_QUOTES_FOUND, quotes
            else:
                return CarrierResultStatus.EXTRACTION_FAILED, []

        except Exception as e:
            print(f"[{self.carrier_code}] Unexpected error: {e}")
            return CarrierResultStatus.UNKNOWN_ERROR, []

        finally:
            await asyncio.shield(self.close())

    async def run_batch_persistent_search(
        self,
        requests: list[RateSearchRequest],
        route_callback: Optional[Any] = None
    ) -> list[tuple[RateSearchRequest, CarrierResultStatus, list[QuoteSchema]]]:
        """
        Executes a vertical batch search over multiple route requests using a SINGLE persistent browser session.
        Login and browser initialization happen ONCE at the start.
        The browser is closed only when all routes in the batch complete.
        """
        batch_results = []
        self.is_batch_active = True
        try:
            # Step 1: Login ONCE
            login_ok = await self.login()
            if not login_ok:
                print(f"[{self.carrier_code}] Persistent Batch LOGIN FAILED. Updating database status for {len(requests)} routes.")
                for idx, req in enumerate(requests):
                    batch_results.append((req, CarrierResultStatus.LOGIN_FAILED, []))
                    if route_callback:
                        try:
                            await route_callback(idx, req, CarrierResultStatus.LOGIN_FAILED, [])
                        except Exception:
                            pass
                return batch_results

            # Step 2: Loop over each route request on the SAME open browser context
            for idx, req in enumerate(requests):
                print(f"[{self.carrier_code}] Persistent Batch Step {idx+1}/{len(requests)}: {req.origin} -> {req.destination}")
                quotes = []
                try:
                    # Execute search flow on active page
                    search_status = await self.search_quotes(req)
                    if search_status == CarrierResultStatus.AVAILABLE_QUOTES_FOUND:
                        raw_quotes = await self.extract_quote_list()
                        if raw_quotes:
                            # Apply Quick Search filter if requested
                            if getattr(req, "search_mode", "quick") == "quick":
                                raw_quotes = self.filter_cheapest_in_14d_window(raw_quotes, req.departure_date)
                                # ULTRA-FAST QUICK SEARCH: Capture final freight price only (no modals, no breakdown, no freetime, no TT)
                                for raw_q in raw_quotes:
                                    price_val = float(raw_q.get("total_price") or raw_q.get("final_freight_value") or raw_q.get("price") or 0.0)
                                    c_types = req.container_types or ["DRY 20", "DRY 40"]
                                    for ct in c_types:
                                        quotes.append(QuoteSchema(
                                            container_type=ct,
                                            container_quantity=1,
                                            currency=raw_q.get("currency", "USD"),
                                            basic_ocean_freight=price_val,
                                            discount=0.0,
                                            final_freight_value=price_val,
                                            included_freight_surcharges=[],
                                            excluded_charges=[],
                                            uncertain_charges=[],
                                            source=self.carrier_code
                                        ))
                            else:
                                for raw_q in raw_quotes:
                                    try:
                                        opened = await self.open_price_breakdown(raw_q)
                                        raw_charges = []
                                        if opened:
                                            raw_charges = await self.extract_charge_breakdown()
                                        
                                        if hasattr(self, "_split_raw_quote_by_container_types") and callable(getattr(self, "_split_raw_quote_by_container_types")):
                                            split_res = await self._split_raw_quote_by_container_types(raw_q, raw_charges)
                                            if split_res:
                                                quotes.extend(split_res)
                                            else:
                                                normalized = await self.normalize_result(raw_q, raw_charges)
                                                quotes.append(normalized)
                                        else:
                                            normalized = await self.normalize_result(raw_q, raw_charges)
                                            quotes.append(normalized)
                                    except Exception as e:
                                        print(f"[{self.carrier_code}] Error extracting batch quote: {e}")
                                        continue
                            
                            status_res = CarrierResultStatus.AVAILABLE_QUOTES_FOUND if quotes else CarrierResultStatus.EXTRACTION_FAILED
                            batch_results.append((req, status_res, quotes))
                        else:
                            batch_results.append((req, CarrierResultStatus.NO_QUOTES_AVAILABLE, []))
                    else:
                        batch_results.append((req, search_status, []))
                except Exception as e:
                    print(f"[{self.carrier_code}] Persistent Batch route error ({req.origin}->{req.destination}): {e}")
                    batch_results.append((req, CarrierResultStatus.FAILED, []))
                
                if route_callback:
                    try:
                        await route_callback(idx, req, batch_results[-1][1], quotes)
                    except Exception:
                        pass

                # Reset or navigate back to search page for next route without closing browser
                try:
                    if self.page and idx < len(requests) - 1 and getattr(self, "SEARCH_URL", None):
                        await self.page.goto(self.SEARCH_URL, wait_until="domcontentloaded", timeout=15000)
                        await self.page.wait_for_timeout(1000)
                except Exception as ne:
                    print(f"[{self.carrier_code}] Navigation reset note: {ne}")

            return batch_results

        except Exception as e:
            print(f"[{self.carrier_code}] Persistent batch execution error: {e}")
            return batch_results
        finally:
            self.is_batch_active = False
            await asyncio.shield(self.close(force=True))


class NotAvailableConnector(BaseCarrierConnector):
    """Placeholder connector for carriers not yet implemented."""

    def __init__(self, carrier_code: str):
        super().__init__()
        self.carrier_code = carrier_code
        self.carrier_name = carrier_code.replace("_", " ").title()

    async def login(self) -> bool:
        return False

    async def search_quotes(self, request: RateSearchRequest) -> CarrierResultStatus:
        return CarrierResultStatus.CONNECTOR_NOT_AVAILABLE

    async def extract_quote_list(self) -> list[dict]:
        return []

    async def open_price_breakdown(self, quote_ref: dict) -> bool:
        return False

    async def extract_charge_breakdown(self) -> list[dict]:
        return []

    async def normalize_result(self, raw_quote: dict, raw_charges: list[dict]) -> QuoteSchema:
        return QuoteSchema()

    async def run_full_search(self, request: RateSearchRequest) -> tuple[CarrierResultStatus, list[QuoteSchema]]:
        """Override to immediately return CONNECTOR_NOT_AVAILABLE."""
        return CarrierResultStatus.CONNECTOR_NOT_AVAILABLE, []
