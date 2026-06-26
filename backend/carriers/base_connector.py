"""
Base Carrier Connector — abstract base class for all carrier connectors.

Each carrier connector must implement these methods to integrate with
the carrier's quote portal via Playwright browser automation.
"""
from abc import ABC, abstractmethod
from typing import Optional
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

    async def close(self):
        """Clean up browser resources."""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
        except Exception:
            pass

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

            # Step 4: For each quote, get breakdown and normalize
            for raw_quote in raw_quotes:
                try:
                    opened = await self.open_price_breakdown(raw_quote)
                    raw_charges = []
                    if opened:
                        raw_charges = await self.extract_charge_breakdown()
                        
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
