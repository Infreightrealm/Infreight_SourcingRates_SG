"""
Manual Action Detector — identifies pages requiring human verification (2FA, CAPTCHA, bot challenges).
"""
import re
from playwright.async_api import Page

# Selectors for common verification iframes, dialogs, and widgets
CHALLENGE_SELECTORS = [
    "iframe[src*='recaptcha' i]",
    "iframe[src*='hcaptcha' i]",
    "iframe[src*='turnstile' i]",
    "iframe[src*='arkoselabs' i]",
    "iframe[src*='funcaptcha' i]",
    ".cf-turnstile",
    "#cf-challenge-running",
    "#challenge-running",
    ".cf-browser-verification",
    "div[id*='captcha' i]",
    "div[class*='captcha' i]",
    "iframe[title*='recaptcha' i]",
    "iframe[title*='hcaptcha' i]"
]

# Keywords that indicate standard 2FA, OTP, suspicious logins, or bot blocks
CHALLENGE_KEYWORDS = [
    r"verify.*human",
    r"confirm.*not.*robot",
    r"checking.*connection.*secure",
    r"access.*denied",
    r"suspicious.*activity",
    r"security.*check",
    r"enter.*verification.*code",
    r"verification.*code.*sent",
    r"two-factor.*authentication",
    r"multi-factor.*authentication",
    r"2fa",
    r"otp",
    r"security.*verification",
    r"one.*more.*step",
    r"security.*challenge",
    r"please.*verify.*your.*identity",
    r"identity.*verification"
]

async def detect_manual_action_required(page: Page) -> bool:
    """
    Scans the current Playwright page to see if a CAPTCHA, Cloudflare challenge,
    2FA, or bot-block screen is displayed.
    """
    try:
        # 1. Check for challenge selectors in DOM
        for selector in CHALLENGE_SELECTORS:
            try:
                locator = page.locator(selector).first
                if await locator.is_visible(timeout=200):
                    print(f"[Self-Healing] Detected bot challenge / CAPTCHA selector: '{selector}'")
                    return True
            except Exception:
                continue

        # 2. Check for challenge keywords in page visible text
        body_locator = page.locator("body")
        if await body_locator.is_attached():
            body_text = await body_locator.inner_text()
            
            for pattern in CHALLENGE_KEYWORDS:
                if re.search(pattern, body_text, re.IGNORECASE):
                    print(f"[Self-Healing] Detected manual action keyword matching pattern: '{pattern}'")
                    return True

        # 3. Check for iframes inside the page (re-run checks in frames)
        for frame in page.frames:
            if frame != page.main_frame:
                frame_url = frame.url.lower()
                if any(x in frame_url for x in ["recaptcha", "hcaptcha", "turnstile", "arkose"]):
                    print(f"[Self-Healing] Detected bot challenge in frame URL: {frame.url}")
                    return True

        return False
    except Exception as e:
        print(f"[Self-Healing] Error running manual action detector: {e}")
        return False
