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

    # ────────────────────────────────────────────────────────────────────
    # QUICK SEARCH (multi-port RFQ) — shared, per-container-type correct
    # ────────────────────────────────────────────────────────────────────

    @staticmethod
    def _card_etd_date(q: dict):
        """Best-effort ETD date from a raw card dict (ISO, MM/DD/YYYY)."""
        from datetime import date
        for d_key in ("etd_standardized", "etd", "etd_date", "etd_date_raw"):
            val = q.get(d_key)
            if not val:
                continue
            s = str(val).strip()
            try:
                return date.fromisoformat(s[:10])
            except Exception:
                pass
            if "/" in s:
                parts = s.split("/")
                if len(parts) == 3:
                    try:
                        return date(int(parts[2]), int(parts[0]), int(parts[1]))
                    except Exception:
                        pass
        return None

    @staticmethod
    def _card_summary_price(q: dict) -> float:
        """The card's summary price. NOTE: on multi-container cards this is the SUM
        across every size on the card, not any single size's price."""
        for p_key in ("total_price", "final_freight_value", "basic_ocean_freight", "price", "rate", "usd_price"):
            val = q.get(p_key)
            if val is None:
                continue
            try:
                return float(str(val).replace(",", "").replace("$", ""))
            except Exception:
                pass
        return 999999.0

    def select_cheapest_per_window(
        self,
        raw_quotes: list[dict],
        departure_date_val: Optional[str] = None,
    ) -> dict:
        """
        Picks the cheapest card in EACH tariff window the customer RFQ sheet needs:
          "1ST" = [start, start+14d]      "2ND" = (start+14d, start+28d]
        Cards are ranked by their summary price, which is a consistent basis across
        cards of one search. Returns {"1ST": card|None, "2ND": card|None}.
        """
        from datetime import date, timedelta
        if not raw_quotes:
            return {"1ST": None, "2ND": None}

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
            except Exception:
                return today_d

        start = _resolve_start(departure_date_val)
        end_1st = start + timedelta(days=14)
        end_2nd = start + timedelta(days=28)
        first, second, undated = [], [], []
        for q in raw_quotes:
            if q.get("is_sold_out"):
                continue
            d = self._card_etd_date(q)
            if d is None:
                undated.append(q)
            elif start <= d <= end_1st:
                first.append(q)
            elif end_1st < d <= end_2nd:
                second.append(q)
        # Undated cards can't be windowed; they only fill the 1st window if nothing else does.
        if not first and undated:
            first = undated
        pick = lambda pool: min(pool, key=self._card_summary_price) if pool else None
        return {"1ST": pick(first), "2ND": pick(second)}

    async def _split_or_none(self, raw_quote: dict, raw_charges: list[dict]) -> list[QuoteSchema]:
        """Calls the connector's per-container splitter whether it is sync or async
        (GreenX's is sync; awaiting it raised TypeError and silently dropped the quote)."""
        splitter = getattr(self, "_split_raw_quote_by_container_types", None)
        if not callable(splitter):
            return []
        import inspect
        result = splitter(raw_quote, raw_charges)
        if inspect.isawaitable(result):
            result = await result
        return list(result or [])

    async def build_quick_quotes(self, request: RateSearchRequest, raw_quotes: list[dict]) -> list[QuoteSchema]:
        """
        Quick-mode quote builder shared by every connector and both search paths.

        Fixes the previous quick path, which stamped the card's SUMMARY price onto
        every requested container type. On multi-container cards (ONE, GreenX,
        Maersk searched with all sizes) that summary is the SUM across sizes, so a
        20' and a 40' got the same, inflated number — and the tariff sheet then took a
        cross-carrier min of those corrupted values.

        Strategy per window (1ST / 2ND):
          1. Pick the cheapest card.
          2. Open ONLY that card's breakdown and split it per container type —
             one modal per window instead of one per card, so still fast.
          3. Return the requested types that have a real per-type price.
          4. Fall back to the summary price only when exactly ONE type was requested
             (then the card total genuinely is that type's price). Never fabricate a
             per-type price for other sizes.
        """
        requested = list(request.container_types or ([request.container_type] if request.container_type else []))
        if not requested:
            requested = ["DRY 20", "DRY 40"]
        windows = self.select_cheapest_per_window(raw_quotes, request.departure_date)
        out: list[QuoteSchema] = []
        for label, card in windows.items():
            if not card:
                continue
            per_type: dict[str, QuoteSchema] = {}
            try:
                opened = await self.open_price_breakdown(card)
                raw_charges = await self.extract_charge_breakdown() if opened else []
                for q in await self._split_or_none(card, raw_charges):
                    if q.container_type:
                        per_type[q.container_type] = q
            except Exception as e:
                print(f"[{self.carrier_code}] [Quick {label}] Per-type breakdown unavailable: {e}")

            summary = self._card_summary_price(card)
            etd_d = self._card_etd_date(card)
            etd_val = etd_d.isoformat() if etd_d else (card.get("etd_standardized") or card.get("etd"))
            eta_val = card.get("eta_standardized") or card.get("eta")
            for ct in requested:
                ref = f"{self.carrier_code}-QUICK-{label}-{ct.replace(' ', '_')}"
                if ct in per_type:
                    out.append(per_type[ct].model_copy(update={"raw_reference": ref, "etd": per_type[ct].etd or etd_val, "eta": per_type[ct].eta or eta_val}))
                elif len(requested) == 1 and summary < 999999.0:
                    out.append(QuoteSchema(
                        container_type=ct, container_quantity=1,
                        currency=card.get("currency", "USD"),
                        basic_ocean_freight=summary, discount=0.0, final_freight_value=summary,
                        included_freight_surcharges=[], excluded_charges=[], uncertain_charges=[],
                        etd=etd_val, eta=eta_val,
                        transit_time_days=card.get("transit_time_days"),
                        vessel=card.get("vessel"), service_name=card.get("service_name"),
                        source=self.carrier_code, raw_reference=ref,
                    ))
                else:
                    print(f"[{self.carrier_code}] [Quick {label}] No per-type price for {ct} on the cheapest card; "
                          f"not fabricating one from the {summary:.2f} summary total.")
        print(f"[{self.carrier_code}] [Quick Search] Built {len(out)} per-type quote(s) across windows "
              f"{[k for k, v in windows.items() if v]} for types {requested}.")
        return out

    def filter_cheapest_in_14d_window(
        self,
        raw_quotes: list[dict],
        departure_date_val: Optional[str] = None
    ) -> list[dict]:
        """Backward-compatible: the single cheapest card (1ST window, else 2ND)."""
        w = self.select_cheapest_per_window(raw_quotes, departure_date_val)
        card = w.get("1ST") or w.get("2ND")
        return [card] if card else []

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

            # Quick mode: cheapest card per tariff window, priced PER container type
            # (see build_quick_quotes for why the old summary-price stamping was wrong).
            if (request.search_mode or "detailed") == "quick":
                quotes = await self.build_quick_quotes(request, raw_quotes)
                if quotes:
                    return CarrierResultStatus.AVAILABLE_QUOTES_FOUND, quotes
                return CarrierResultStatus.NO_QUOTES_AVAILABLE, []

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

    async def _run_batch_route(self, req: RateSearchRequest) -> tuple[CarrierResultStatus, list[QuoteSchema]]:
        """One route of a persistent batch on the already-open session (no login/close)."""
        search_status = await self.search_quotes(req)
        if search_status != CarrierResultStatus.AVAILABLE_QUOTES_FOUND:
            return search_status, []
        raw_quotes = await self.extract_quote_list()
        if not raw_quotes:
            return CarrierResultStatus.NO_QUOTES_AVAILABLE, []

        quotes: list[QuoteSchema] = []
        if (req.search_mode or "detailed") == "quick":
            quotes = await self.build_quick_quotes(req, raw_quotes)
        else:
            for raw_q in raw_quotes:
                try:
                    opened = await self.open_price_breakdown(raw_q)
                    raw_charges = await self.extract_charge_breakdown() if opened else []
                    split_res = await self._split_or_none(raw_q, raw_charges)
                    if split_res:
                        quotes.extend(split_res)
                    else:
                        quotes.append(await self.normalize_result(raw_q, raw_charges))
                except Exception as e:
                    print(f"[{self.carrier_code}] Error extracting batch quote: {e}")
                    continue
        status = CarrierResultStatus.AVAILABLE_QUOTES_FOUND if quotes else CarrierResultStatus.NO_QUOTES_AVAILABLE
        return status, quotes

    async def _reset_between_routes(self, relogin: bool = False) -> None:
        """
        Returns the open session to a clean search page for the next route. With
        relogin=True (after a route failure) it also re-runs login(), which every
        connector implements as a cheap "already logged in?" check that only submits
        credentials if the session was actually lost.
        """
        try:
            if relogin:
                ok = await self.login()
                print(f"[{self.carrier_code}] Batch session re-check after failure: login_ok={ok}")
        except Exception as le:
            print(f"[{self.carrier_code}] Batch re-login attempt failed: {le}")
        try:
            reset_url = getattr(self, "SEARCH_URL", None) or getattr(self, "QUOTE_URL", None)
            if self.page and reset_url:
                await self.page.goto(reset_url, wait_until="domcontentloaded", timeout=15000)
                await self.page.wait_for_timeout(1000)
        except Exception as ne:
            print(f"[{self.carrier_code}] Navigation reset note: {ne}")

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

            # Step 2: Loop over each route request on the SAME open browser context.
            # Each route is isolated: a hard per-route timeout (one hung route used to
            # stall the whole 168-route batch), one retry after a page reset (which also
            # re-checks login, since a mid-batch session expiry used to kill every
            # remaining route), and a navigation reset that no longer depends on the
            # connector defining SEARCH_URL.
            import os
            route_timeout = float(os.getenv("BATCH_ROUTE_TIMEOUT_SEC", "420"))
            for idx, req in enumerate(requests):
                print(f"[{self.carrier_code}] Persistent Batch Step {idx+1}/{len(requests)}: {req.origin} -> {req.destination}")
                status_res, quotes = CarrierResultStatus.FAILED, []
                for attempt in (1, 2):
                    try:
                        status_res, quotes = await asyncio.wait_for(
                            self._run_batch_route(req), timeout=route_timeout)
                        break
                    except asyncio.TimeoutError:
                        status_res, quotes = CarrierResultStatus.TIMEOUT, []
                        print(f"[{self.carrier_code}] Batch route TIMEOUT after {route_timeout:.0f}s "
                              f"({req.origin}->{req.destination}), attempt {attempt}/2.")
                    except Exception as e:
                        status_res, quotes = CarrierResultStatus.FAILED, []
                        print(f"[{self.carrier_code}] Persistent Batch route error "
                              f"({req.origin}->{req.destination}), attempt {attempt}/2: {e}")
                    if attempt == 1:
                        await self._reset_between_routes(relogin=True)
                batch_results.append((req, status_res, quotes))

                if route_callback:
                    try:
                        await route_callback(idx, req, status_res, quotes)
                    except Exception as cb_err:
                        print(f"[{self.carrier_code}] route_callback error (route {idx+1}): {cb_err}")

                if idx < len(requests) - 1:
                    await self._reset_between_routes(relogin=False)

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
