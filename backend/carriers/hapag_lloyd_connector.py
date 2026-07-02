# -*- coding: utf-8 -*-
"""
Hapag-Lloyd Live Connector -- Playwright automation.

Credentials read from env: HAPAG_LLOYD_USERNAME, HAPAG_LLOYD_PASSWORD
Never hardcode credentials.
"""
import os
import re
import asyncio
import random
import shutil
import uuid
import subprocess
from datetime import date, datetime, timedelta
from patchright.async_api import async_playwright
from typing import Optional

from models.schemas import RateSearchRequest, QuoteSchema, CarrierResultStatus, ChargeCategory
from services.charge_classifier import classify_charge
from services.normalizer import normalize_quote, standardize_date_string
from carriers.base_connector import BaseCarrierConnector
from services.port_manager import get_cached_carrier_port, set_cached_carrier_port, resolve_port_for_carrier


class HapagServiceUnavailableException(Exception):
    """Exception raised when Hapag-Lloyd API Gateway reports service is unavailable."""
    pass


class HapagLloydConnector(BaseCarrierConnector):
    carrier_code = "HAPAG_LLOYD"
    carrier_name = "Hapag-Lloyd"
    QUOTE_URL = "https://www.hapag-lloyd.com/en/home.html"

    CONTAINER_TYPE_MAP = {
        "DRY 20": "20' General Purpose",
        "DRY 40": "40' General Purpose",
        "DRY 40H": "40' General Purpose High Cube",
    }

    def __init__(self):
        super().__init__()
        self.playwright = None
        self._all_quotes = []
        self.master_profile_dir = None
        self.temp_profile_dir = None
        self.is_login_successful = False
        self._onboarding_dismissed = False

    async def _check_service_unavailable(self):
        """Checks if Hapag-Lloyd API Gateway has returned 'This service is currently unavailable'."""
        try:
            if not self.page or (self.page.is_closed() if hasattr(self.page, "is_closed") and callable(self.page.is_closed) else getattr(self.page, "is_closed", False)):
                return

            # Check modal visibility quickly
            modal = self.page.locator('div:has-text("This service is currently unavailable"), h1:has-text("This service is currently unavailable"), p:has-text("This service is currently unavailable")').first
            if await modal.is_visible(timeout=500):
                print("[HAPAG] Hapag-Lloyd API Gateway error detected: 'This service is currently unavailable'.")
                raise HapagServiceUnavailableException("Hapag-Lloyd service is currently unavailable.")
            
            # Check body text quickly (much safer/faster than page.content())
            try:
                body_text = await self.page.locator("body").inner_text(timeout=500)
            except Exception:
                body_text = ""
                
            if "This service is currently unavailable" in body_text or "Global transaction ID" in body_text:
                print("[HAPAG] Hapag-Lloyd API Gateway text detected in content: 'This service is currently unavailable'.")
                raise HapagServiceUnavailableException("Hapag-Lloyd service is currently unavailable.")
        except HapagServiceUnavailableException:
            raise
        except Exception:
            pass

    async def _init_browser(self):
        is_prod = os.name != "nt"
        
        self.playwright = await async_playwright().start()

        # ── Persistent profile setup (similar to Maersk / CMA CGM) ──────────────
        persistent_dir = os.getenv("PERSISTENT_PROFILES_DIR")
        if persistent_dir:
            self.master_profile_dir = os.path.join(persistent_dir, "chrome_profile_hapag")
        else:
            self.master_profile_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chrome_profile_hapag")

        if os.getenv("RESET_CHROME_PROFILES", "").lower() == "true":
            print(f"[HAPAG] [WARN] RESET_CHROME_PROFILES active. Clearing master profile: {self.master_profile_dir}")
            if os.path.exists(self.master_profile_dir):
                try:
                    shutil.rmtree(self.master_profile_dir)
                    print("[HAPAG] Master profile cleared.")
                except Exception as e:
                    print(f"[HAPAG] Failed to clear master profile: {e}")

        # Create unique temp profile copy for this session
        unique_id = str(uuid.uuid4())[:8]
        if persistent_dir:
            self.temp_profile_dir = os.path.join(persistent_dir, f"chrome_profile_hapag_tmp_{unique_id}")
        else:
            self.temp_profile_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), f"chrome_profile_hapag_tmp_{unique_id}")

        # Sweep orphaned temp profiles left behind by crashed runs (close() removes
        # the current one on normal exit). Only THIS carrier's prefix, and only dirs
        # old enough (>6h) that no live run can still own them.
        try:
            parent_dir = os.path.dirname(self.temp_profile_dir)
            cutoff = datetime.now().timestamp() - 6 * 3600
            for entry in os.listdir(parent_dir):
                if entry.startswith("chrome_profile_hapag_tmp_") and entry != os.path.basename(self.temp_profile_dir):
                    stale_path = os.path.join(parent_dir, entry)
                    if os.path.isdir(stale_path) and os.path.getmtime(stale_path) < cutoff:
                        shutil.rmtree(stale_path, ignore_errors=True)
                        print(f"[HAPAG] Removed orphaned temp profile: {entry}")
        except Exception:
            pass

        print(f"[HAPAG] Creating temp isolated profile: {self.temp_profile_dir}")
        if os.path.exists(self.master_profile_dir):
            try:
                # Skip heavy throwaway Chrome caches when cloning — Chromium regenerates
                # them, so copying only bloats launch I/O and disk. Session identity
                # (Cookies / Local Storage / IndexedDB) is still copied intact.
                shutil.copytree(
                    self.master_profile_dir, self.temp_profile_dir, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns(
                        "Cache", "Code Cache", "DawnCache", "GPUCache", "CacheStorage", "ScriptCache"),
                )
                lock_files = ["SingletonLock", "lock", "SingletonCookie"]
                for root_dir, _, filenames in os.walk(self.temp_profile_dir):
                    for filename in filenames:
                        if filename in lock_files:
                            try:
                                os.remove(os.path.join(root_dir, filename))
                            except Exception:
                                pass
                print("[HAPAG] Master profile copied with lock files cleaned.")
            except Exception as e:
                print(f"[HAPAG] Warning: could not copy master profile ({e}). Starting fresh.")
        else:
            print("[HAPAG] No master profile found. Initialising fresh profile.")
            os.makedirs(self.temp_profile_dir, exist_ok=True)

        # ── Proxy setup ──────────────────────────────────────────────────────────
        proxy_user = os.getenv("BRIGHTDATA_PROXY_USER")
        proxy_pass = os.getenv("BRIGHTDATA_PROXY_PASS")
        proxy_server = os.getenv("BRIGHTDATA_PROXY_SERVER", "http://brd.superproxy.io:22225")
        
        # Check carrier-specific proxies
        if os.getenv("HAPAG_PROXY_USER"):
            proxy_user = os.getenv("HAPAG_PROXY_USER")
            proxy_pass = os.getenv("HAPAG_PROXY_PASS")
            if os.getenv("HAPAG_PROXY_SERVER"):
                proxy_server = os.getenv("HAPAG_PROXY_SERVER")

        proxy_config = None
        if proxy_user and proxy_pass:
            if "-session-" not in proxy_user:
                session_id = str(uuid.uuid4())[:8]
                proxy_user = f"{proxy_user}-session-{session_id}"
                
            proxy_config = {
                "server": proxy_server,
                "username": proxy_user,
                "password": proxy_pass,
            }
            print(f"[HAPAG] [PROXY] Routing through ISP residential proxy ({proxy_server}) with session pinning ({proxy_user.split('-session-')[-1]})...")
        else:
            print("[HAPAG] [INFO] No proxy configured. Running on local IP directly.")

        # ── Browser Launch Arguments ─────────────────────────────────────────────
        args = [
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-infobars",
            "--disable-component-update",
            "--disable-default-apps",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            "--disable-ipc-flooding-protection",
            "--force-color-profile=srgb",
            "--use-gl=desktop",
            "--window-size=1920,1080",
            "--start-maximized",
        ]

        # On Windows: use the REAL Chrome binary to avoid fingerprint detection.
        chrome_exe = None
        if not is_prod:
            chrome_candidates = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
            ]
            for path in chrome_candidates:
                if os.path.exists(path):
                    chrome_exe = path
                    break

        executable_path = None
        if is_prod:
            executable_path = "/usr/bin/google-chrome-stable"
            if not os.path.exists(executable_path):
                executable_path = None
                print("[HAPAG] [WARN] google-chrome-stable not found. Falling back to bundled Chromium.")
            else:
                print(f"[HAPAG] Using real Chrome: {executable_path}")
        elif chrome_exe:
            executable_path = chrome_exe
            print(f"[HAPAG] Using local real Chrome: {chrome_exe}")

        # Thread-safe virtual display environment injection
        browser_env = os.environ.copy()
        if is_prod:
            browser_env["DISPLAY"] = ":102"

        self.context = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=self.temp_profile_dir,
            headless=False,  # Headless mode must be False for VNC rendering
            executable_path=executable_path,
            # HAPAG_INTERACTION_DELAY (ms) overrides the global input throttle; the
            # randomized 80-150ms default is deliberate anti-detection pacing.
            slow_mo=(int(os.getenv("HAPAG_INTERACTION_DELAY"))
                     if (os.getenv("HAPAG_INTERACTION_DELAY") or "").isdigit()
                     else random.randint(80, 150)),
            args=args,
            proxy=proxy_config,
            no_viewport=True,
            ignore_default_args=["--enable-automation"],
            env=browser_env,
        )

        self.page = self.context.pages[0] if self.context.pages else await self.context.new_page()
        
        # We will inject the onboarding style overlay after navigation and modal dismissal passes
        # rather than pre-navigation add_init_script (which causes net::ERR_NAME_NOT_RESOLVED under Patchright on Windows).
        pass
        
        # Custom timeouts
        self.page.set_default_timeout(45000)
        self.page.set_default_navigation_timeout(60000)

    async def _human_delay(self, min_ms=500, max_ms=1500):
        # HAPAG_GOVERNOR_FACTOR scales ALL human-pacing delays (default 1.0 = current
        # behavior). <1.0 runs faster in low-latency/trusted environments; raising it
        # slows pacing if challenge rates climb. Clamped to a sane range.
        factor = getattr(self, "_governor_factor", None)
        if factor is None:
            try:
                factor = float(os.getenv("HAPAG_GOVERNOR_FACTOR", "1.0"))
            except (TypeError, ValueError):
                factor = 1.0
            factor = max(0.2, min(3.0, factor))
            self._governor_factor = factor
        await self.page.wait_for_timeout(random.randint(int(min_ms * factor), max(int(min_ms * factor), int(max_ms * factor))))

    async def _attempt_captcha_autoclear(self) -> bool:
        """
        Best-effort automated CAPTCHA/Turnstile clearing, tried BEFORE escalating
        to a manual VNC solve. Two steps:
          1. Give a passive challenge a few seconds to resolve itself — with a clean
             fingerprint + residential proxy, Turnstile often auto-passes with no click.
          2. If an interactive Turnstile/checkbox widget is present, click it once
             with human-like mouse motion.
        Returns True only if the challenge actually cleared. Never raises for
        non-fatal issues, so the caller can always fall through to the manual path.
        Page-closed/crashed errors are re-raised so teardown is handled upstream.
        """
        try:
            # Step 1 — passive auto-resolve window.
            for _ in range(4):
                await asyncio.sleep(1.5)
                if not await self.check_captcha_challenge():
                    print("[HAPAG] Challenge cleared passively (no interaction needed).")
                    return True

            # Step 2 — best-effort human-like checkbox click.
            if await self._click_turnstile_checkbox():
                print("[HAPAG] Attempted human-like Turnstile click; waiting for verdict...")
                for _ in range(5):
                    await asyncio.sleep(1.5)
                    if not await self.check_captcha_challenge():
                        print("[HAPAG] Challenge cleared after checkbox click.")
                        return True
            return False
        except Exception as e:
            if any(k in str(e).lower() for k in ("closed", "crashed", "target")):
                raise
            print(f"[HAPAG] Auto-clear attempt error (falling back to manual): {e}")
            return False

    async def _click_turnstile_checkbox(self) -> bool:
        """
        Locate the Cloudflare Turnstile / challenge widget and click its checkbox
        using a REAL mouse click at the widget's bounding box (trusted input events),
        which Cloudflare is far more likely to accept than a synthetic .click().
        Best-effort only — returns True if a click was dispatched, False otherwise.
        """
        try:
            container_selectors = [
                '#cf-turnstile',
                '.cf-turnstile',
                'div[class*="turnstile" i]',
                'iframe[src*="challenges.cloudflare.com" i]',
                'iframe[title*="challenge" i]',
                'iframe[src*="turnstile" i]',
            ]
            box = None
            for sel in container_selectors:
                try:
                    el = self.page.locator(sel).first
                    if await el.count() and await el.is_visible(timeout=800):
                        box = await el.bounding_box()
                        if box and box.get("width") and box.get("height"):
                            break
                except Exception:
                    continue
            if not box:
                return False

            # The checkbox sits near the left edge, vertically centered.
            target_x = box["x"] + 28
            target_y = box["y"] + box["height"] / 2

            # Human-like approach: glide in over a few steps, small pause, then click.
            await self.page.mouse.move(target_x - 45, target_y - 14, steps=8)
            await self._human_delay(180, 420)
            await self.page.mouse.move(target_x, target_y, steps=6)
            await self._human_delay(120, 300)
            await self.page.mouse.click(target_x, target_y, delay=random.randint(45, 110))
            return True
        except Exception:
            return False

    async def _wait_for_captcha_resolution(self, timeout_sec=240) -> bool:
        """
        Helper that pauses execution if a CAPTCHA challenge is detected,
        and waits up to timeout_sec for the user to resolve it in VNC.
        """
        if not self.page or (self.page.is_closed() if hasattr(self.page, "is_closed") and callable(self.page.is_closed) else getattr(self.page, "is_closed", False)):
            raise Exception("Playwright page is closed or crashed.")

        try:
            if not await self.check_captcha_challenge():
                return False
        except Exception as e:
            if "closed" in str(e).lower() or "crashed" in str(e).lower() or "target" in str(e).lower():
                raise
            return False

        # Best-effort automated clear (passive auto-resolve + human-like Turnstile
        # click) before escalating to a manual solve. Falls through to the manual
        # VNC wait below if it doesn't clear — so this can only help, never hurt.
        try:
            if await self._attempt_captcha_autoclear():
                self.captcha_detected = False
                return False
        except Exception as e:
            if any(k in str(e).lower() for k in ("closed", "crashed", "target")):
                raise

        print("[HAPAG] [ACTION REQUIRED] CAPTCHA / bot challenge page detected! Pausing crawler. Please look at the VNC tab to solve it.")
        
        # Trigger WAITING_FOR_HUMAN_VERIFICATION status in DB
        self.captcha_detected = True
        if self.status_update_callback:
            await self.status_update_callback(CarrierResultStatus.WAITING_FOR_HUMAN_VERIFICATION)

        start_time = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start_time < timeout_sec:
            if not self.page or (self.page.is_closed() if hasattr(self.page, "is_closed") and callable(self.page.is_closed) else getattr(self.page, "is_closed", False)):
                raise Exception("Playwright page is closed or crashed during CAPTCHA resolution.")

            elapsed = int(asyncio.get_event_loop().time() - start_time)
            if elapsed > 0 and elapsed % 5 == 0:
                print(f"[HAPAG] Still waiting for CAPTCHA resolution in VNC window... ({elapsed}s elapsed)")

            await asyncio.sleep(1.0)

            try:
                challenge_active = await self.check_captcha_challenge()
            except Exception as e:
                if "closed" in str(e).lower() or "crashed" in str(e).lower() or "target" in str(e).lower():
                    raise
                challenge_active = False

            if not challenge_active:
                print("[HAPAG] CAPTCHA challenge cleared! Resuming crawler...")
                self.captcha_detected = False
                if self.status_update_callback:
                    await self.status_update_callback(CarrierResultStatus.RUNNING)
                return True

        print("[HAPAG] Timed out waiting for CAPTCHA resolution.")
        self.captcha_detected = False
        if self.status_update_callback:
            await self.status_update_callback(CarrierResultStatus.RUNNING)
        return False

    async def _inject_onboarding_styles(self):
        try:
            if self.page and not (self.page.is_closed() if hasattr(self.page, "is_closed") and callable(self.page.is_closed) else getattr(self.page, "is_closed", False)):
                await self.page.add_style_tag(content="""
                    .hal-onboarding__content, 
                    [class*="onboarding" i],
                    [id*="onboarding" i],
                    .productfruits-overlay,
                    .productfruits__onboarding { 
                        display: none !important; 
                        visibility: hidden !important; 
                        pointer-events: none !important;
                    }
                """)
        except Exception as e:
            print(f"[HAPAG] Warning: Failed to inject onboarding style tag: {e}")

    async def _dismiss_hapag_modals(self):
        """
        Dismisses any obscuring modal popups (including multi-step tutorial dialogs).
        """
        await self._check_service_unavailable()
        await self._inject_onboarding_styles()
        
        # If onboarding has already been dismissed this session, just do a single quick check
        # for other generic modals, rather than running the full 5-step onboarding loop.
        if self._onboarding_dismissed:
            # Debounce: several call sites invoke this back-to-back per sailing. If the
            # last pass ran very recently AND found nothing, skip the repeat JS work.
            # If the last pass actually dismissed something, we do NOT skip, so a real
            # popup is never missed.
            now = asyncio.get_event_loop().time()
            if (now - getattr(self, "_last_clean_dismiss_ts", 0.0)) < 2.5:
                return False
            try:
                found = await self._run_modal_dismissal_pass()
            except Exception:
                found = False
            if not found:
                self._last_clean_dismiss_ts = now
            return False

        print("[HAPAG] Dismissing any obscuring modal popups or onboarding wizards...")
        try:
            dismissed_any = False
            for step in range(1, 6):
                dismissed = await self._run_modal_dismissal_pass()
                if not dismissed:
                    break
                print(f"[HAPAG] Tutorial step {step} popup dismissed successfully.")
                dismissed_any = True
                await self.page.wait_for_timeout(800)  # brief wait for transition to next step/dialog
            
            # Mark onboarding as handled for the rest of this session
            self._onboarding_dismissed = True
            return dismissed_any
        except Exception as e:
            print(f"[HAPAG] Error in modal dismissal loop: {e}")
            return False

    async def _run_modal_dismissal_pass(self) -> bool:
        """
        Performs a single modal dismissal check and attempt.
        """
        try:
            # 1. Run quick selector-based closes
            close_selectors = [
                'button[aria-label*="close" i]',
                'button:has-text("Close")',
                'div[role="dialog"] button:has-text("Close")',
                'div:has-text("Recently Searched") button:has-text("Close")',
                'div:has-text("Recently Searched") button',
                'span:has-text("Close")',
                '.modal button:has-text("Close")',
                '.el-dialog__headerbtn',
                '.el-dialog__close'
            ]
            combined_close = ", ".join(close_selectors)
            try:
                close_btn = self.page.locator(combined_close).first
                if await close_btn.is_visible(timeout=150):
                    print("[HAPAG] Modal close button detected. Clicking to dismiss...")
                    await close_btn.scroll_into_view_if_needed()
                    await close_btn.click()
                    return True
            except:
                pass

            # 1.5. Onboarding specific dismissal
            onboarding_selectors = [
                '.hal-onboarding__content button',
                '[class*="onboarding" i] button',
                'button:has-text("Skip")',
                'button:has-text("Next")',
                'button:has-text("Got it")',
                '.q-dialog button:has-text("Skip")',
                'div[id^="q-portal--dialog"] button:has-text("Skip")'
            ]
            combined_onboarding = ", ".join(onboarding_selectors)
            try:
                btn = self.page.locator(combined_onboarding).first
                if await btn.is_visible(timeout=150):
                    print("[HAPAG] Onboarding button/close detected. Clicking...")
                    await btn.click()
                    return True
            except:
                pass
            
            # 2. Run advanced JavaScript evaluation to close custom overlay popups (e.g. currency onboarding)
            js_close_result = await self.page.evaluate('''() => {
                const dialogs = Array.from(document.querySelectorAll('div[role="dialog"], .el-dialog, .modal, .q-dialog, .q-card'));
                for (const dialog of dialogs) {
                    // Try to find close buttons or icons (like the X icon in top right)
                    const closeBtn = dialog.querySelector('button[aria-label*="close" i], .el-dialog__headerbtn, [class*="close" i]');
                    if (closeBtn && closeBtn.getBoundingClientRect().width > 0) {
                        closeBtn.click();
                        return "Clicked close button/icon";
                    }
                    
                    // Scan all buttons/text/icons in this dialog for X symbols or "close" text
                    const elements = Array.from(dialog.querySelectorAll('button, span, i, a'));
                    for (const el of elements) {
                        const txt = (el.textContent || "").trim();
                        const cls = el.className || "";
                        if (txt === '\u2715' || txt === '\u00d7' || txt === 'x' || txt.toLowerCase() === 'close' || cls.includes('close') || cls.includes('icon-close')) {
                            el.click();
                            return "Clicked text/class close symbol: " + txt;
                        }
                    }
                    
                    // Fallback to "Next" or "OK" buttons in onboarding modals
                    const actionBtn = Array.from(dialog.querySelectorAll('button, .q-btn, .orange')).find(btn => {
                        const txt = (btn.textContent || "").trim().toLowerCase();
                        return txt === 'next' || txt === 'ok' || txt.includes('got it') || txt.includes('skip') || txt.includes('confirm') || btn.classList.contains('orange');
                    });
                    if (actionBtn && actionBtn.getBoundingClientRect().width > 0) {
                        actionBtn.click();
                        return "Clicked modal action button: " + actionBtn.textContent.trim();
                    }
                }
                return null;
            }''')
            
            if js_close_result:
                print(f"[HAPAG] JavaScript popup manager: {js_close_result}")
                return True
                
            return False
        except Exception as e:
            print(f"[HAPAG] Error in single modal dismissal pass: {e}")
            return False

    async def login(self) -> bool:
        try:
            await self._init_browser()
            print("[HAPAG] Navigating to home page...")
            try:
                await self.page.goto(self.QUOTE_URL)
            except Exception as navigation_error:
                print(f"[HAPAG] Navigation encountered an error/non-200 code: {navigation_error}")
                print("[HAPAG] Proceeding anyway in case of Akamai/Cloudflare challenge rendering on 403...")
            try:
                await self.page.wait_for_load_state("domcontentloaded", timeout=12000)
            except:
                pass
            
            # Check for CAPTCHA immediately on homepage load
            await self._wait_for_captcha_resolution()
            
            await self._check_service_unavailable()
            await self._human_delay(1500, 2500)

            # Accept cookies banner if present
            try:
                accept_selectors = [
                    '#accept-recommended-btn-handler',
                    '#onetrust-accept-btn-handler',
                    'button:has-text("Accept All")',
                    'button:has-text("Accept")',
                    'button:has-text("Agree")',
                    '.cookie-accept-button'
                ]
                for selector in accept_selectors:
                    btn = self.page.locator(selector).first
                    if await btn.is_visible(timeout=1000):
                        print(f"[HAPAG] Accepting cookies: Clicking {selector}")
                        await btn.click()
                        await self._human_delay(800, 1500)
                        break
            except Exception:
                pass

            # Check if already logged in (look for sign-out or profile buttons)
            is_logged_in = False
            try:
                signout_loc = self.page.locator('a:has-text("Log out"), button:has-text("Log out"), button:has-text("Sign out")')
                if await signout_loc.count() > 0 and await signout_loc.first.is_visible(timeout=1000):
                    is_logged_in = True
                    print("[HAPAG] Already logged in.")
            except:
                pass

            # Check if Quick Quote form is already visible
            start_input_selector = 'xpath=(//*[contains(text(), "Start Location")])[1]/following::input[1]'
            is_form_visible = False
            try:
                is_form_visible = await self.page.locator(start_input_selector).first.is_visible(timeout=2000)
            except:
                pass

            if is_form_visible:
                print("[HAPAG] Already on New Quote page after login. Skipping sidebar clicks.")
            else:
                # Expand Quote Sidebar
                print("[HAPAG] Expanding 'Quote' sidebar menu...")
                quote_sidebar = self.page.locator('span:has-text("Quote"), li:has-text("Quote"), a:has-text("Quote")').first
                await quote_sidebar.scroll_into_view_if_needed()
                await quote_sidebar.click(force=True)
                await self._human_delay(1000, 1800)

                # Click 'New Quote'
                print("[HAPAG] Clicking 'New Quote' sub-menu...")
                new_quote_btn = self.page.locator('a:has-text("New Quote"), span:has-text("New Quote")').first
                await new_quote_btn.scroll_into_view_if_needed()
                await new_quote_btn.click(force=True)
                # Short settle only — the 180s settle loop below actively detects the
                # login form / Quick Quote page, so a long blind wait here is redundant.
                await self._human_delay(1500, 2500)

            # Wait for either the login form (credentials required) or the Quick Quote page (already logged in) to settle
            print("[HAPAG] Waiting for page to settle (up to 180s) to detect if login is required or already logged in...")
            is_logged_in = False
            settle_start_time = asyncio.get_event_loop().time()
            settled = False
            
            while asyncio.get_event_loop().time() - settle_start_time < 180:
                # Check for login selectors
                login_selectors = [
                    'input#email',
                    'input#signInName',
                    'input[type="email"]',
                    'input[name*="username" i]',
                    'input[name*="email" i]',
                    'input[placeholder*="Email" i]',
                    'input[placeholder*="E-mail" i]'
                ]
                found_login = False
                for sel in login_selectors:
                    try:
                        loc = self.page.locator(sel).first
                        if await loc.is_visible(timeout=300):
                            print(f"[HAPAG] Login field detected: {sel}")
                            found_login = True
                            break
                    except:
                        pass
                
                if found_login:
                    is_logged_in = False
                    settled = True
                    break

                # Check for quick quote form selectors (already logged in)
                quote_selectors = [
                    'input[placeholder*="Start" i]',
                    '[id*="start" i] input',
                    '[class*="start" i] input',
                    'input[placeholder*="Origin" i]'
                ]
                found_quote = False
                for sel in quote_selectors:
                    try:
                        loc = self.page.locator(sel).first
                        if await loc.is_visible(timeout=300):
                            print(f"[HAPAG] Quick Quote form field detected: {sel}")
                            found_quote = True
                            break
                    except:
                        pass

                if found_quote:
                    is_logged_in = True
                    settled = True
                    break

                # Also print a status update every 5 seconds
                elapsed = int(asyncio.get_event_loop().time() - settle_start_time)
                if elapsed > 0 and elapsed % 5 == 0:
                    if self.captcha_detected:
                        print(f"[HAPAG] [ACTION REQUIRED] Still blocked by CAPTCHA/Turnstile. Please solve it in the VNC window. (elapsed {elapsed}s)")
                    else:
                        print(f"[HAPAG] Still waiting for page to settle... (elapsed {elapsed}s). Solve Cloudflare in VNC if prompted.")

                # Check for active challenge/captcha
                await self._wait_for_captcha_resolution()
                await asyncio.sleep(1)

            if not settled:
                print("[HAPAG] Timeout waiting for page to settle. Proceeding under assumption that credentials might be needed.")
                is_logged_in = False

            if not is_logged_in:
                # Need to log in
                print("[HAPAG] Credentials required. Automating login form...")
                
                email = os.getenv("HAPAG_LLOYD_USERNAME")
                password = os.getenv("HAPAG_LLOYD_PASSWORD")
                
                if not email or not password:
                    print("[HAPAG] [ERROR] HAPAG_LLOYD_USERNAME or HAPAG_LLOYD_PASSWORD environment variables are not set. Cannot perform login.")
                    return False
                    
                email = email.strip()
                password = password.strip()

                mask_pass = f"{password[:2]}***{password[-2:]}" if len(password) > 4 else "***"
                print(f"[HAPAG] Login profile setup: email='{email}', password='{mask_pass}' (length: {len(password)})")

                # Define locator lists for the fields
                email_selectors = [
                    'input#email',
                    'input#signInName',
                    'input[type="email"]',
                    'input[name*="username" i]',
                    'input[name*="email" i]',
                    'input[placeholder*="Email" i]',
                    'input[placeholder*="E-mail" i]'
                ]
                
                email_input = None
                for sel in email_selectors:
                    try:
                        loc = self.page.locator(sel).first
                        if await loc.is_visible(timeout=1000):
                            email_input = loc
                            print(f"[HAPAG] Email input located using selector: {sel}")
                            break
                    except:
                        pass
                
                if not email_input:
                    email_input = self.page.locator('input[type="email"], input[type="text"]').first
                    print("[HAPAG] Fallback to general input for email.")

                await email_input.scroll_into_view_if_needed()
                await email_input.click()  # Click to focus the email box
                await self._human_delay(300, 600)
                await email_input.press("Control+A")
                await email_input.press("Backspace")
                await email_input.fill("")
                await self._human_delay(200, 400)
                await email_input.type(email, delay=random.randint(60, 120))
                await self._human_delay(500, 1000)

                password_selectors = [
                    'input#password',
                    'input[type="password"]',
                    'input[name*="password" i]'
                ]
                
                password_input = None
                for sel in password_selectors:
                    try:
                        loc = self.page.locator(sel).first
                        if await loc.is_visible(timeout=1000):
                            password_input = loc
                            print(f"[HAPAG] Password input located using selector: {sel}")
                            break
                    except:
                        pass

                if not password_input:
                    password_input = self.page.locator('input[type="password"]').first
                    print("[HAPAG] Fallback to standard password input.")

                await password_input.scroll_into_view_if_needed()
                await password_input.click()  # Click to focus the password box
                await self._human_delay(300, 600)
                await password_input.press("Control+A")
                await password_input.press("Backspace")
                await password_input.fill("")
                await self._human_delay(200, 400)
                await password_input.type(password, delay=random.randint(60, 120))
                await self._human_delay(1000, 1800)

                submit_selectors = [
                    'button#next',
                    'button#logIn',
                    'button:has-text("Log in")',
                    'button[type="submit"]',
                    'button:has-text("Sign In")',
                    'input[type="submit"]'
                ]
                
                submit_btn = None
                for sel in submit_selectors:
                    try:
                        loc = self.page.locator(sel).first
                        if await loc.is_visible(timeout=1000):
                            submit_btn = loc
                            print(f"[HAPAG] Submit button located using selector: {sel}")
                            break
                    except:
                        pass

                if not submit_btn:
                    submit_btn = self.page.locator('button:has-text("Log in"), button[type="submit"], button:has-text("Sign In")').first
                    print("[HAPAG] Fallback to standard login/submit button.")

                await submit_btn.scroll_into_view_if_needed()
                await submit_btn.click()
                print("[HAPAG] Login form submitted. Waiting for page redirect to Quick Quote page...")
                try:
                    await self.page.wait_for_load_state("domcontentloaded", timeout=10000)
                except:
                    pass
                await self._human_delay(2000, 4000)

            # Confirm quick quotes form is displayed
            try:
                print("[HAPAG] Confirming Quick Quote form loading...")
                quote_selectors = [
                    'text="Start Location"',
                    'text="End Location"',
                    'text="New Quote"',
                    'input[placeholder*="Start" i]',
                    'div:has-text("Start Location")'
                ]
                
                form_loaded = False
                confirm_start_time = asyncio.get_event_loop().time()
                
                # Poll for up to 240 seconds (4 minutes) for redirect/loading of the Quote form (handling 2FA human in the loop)
                while asyncio.get_event_loop().time() - confirm_start_time < 240:
                    for sel in quote_selectors:
                        try:
                            loc = self.page.locator(sel).first
                            if await loc.is_visible():
                                print(f"[HAPAG] Confirmed Quick Quote page loaded using: {sel}")
                                form_loaded = True
                                break
                        except:
                            pass
                    if form_loaded:
                        break
                    
                    elapsed = int(asyncio.get_event_loop().time() - confirm_start_time)
                    if elapsed > 0 and elapsed % 5 == 0:
                        if self.captcha_detected:
                            print(f"[HAPAG] [ACTION REQUIRED] Still blocked by CAPTCHA/Turnstile. Please solve it in the VNC window. (elapsed {elapsed}s)")
                        else:
                            print(f"[HAPAG] Still waiting for Quick Quote page to load... (elapsed {elapsed}s). Solve 2FA / Verification code in VNC if prompted.")
                        
                    # Check for active challenge/captcha
                    await self._wait_for_captcha_resolution()
                    await asyncio.sleep(1)
                
                if not form_loaded:
                    # Try a fallback general wait for any input, but make sure it is not the login page
                    is_login_page = "identity.hapag-lloyd.com" in self.page.url
                    for sel in login_selectors:
                        try:
                            if await self.page.locator(sel).first.is_visible(timeout=200):
                                is_login_page = True
                                break
                        except:
                            pass
                            
                    if is_login_page:
                        print("[HAPAG] Settle fallback detected login inputs/URL. Quick Quote form NOT loaded.")
                    else:
                        try:
                            await self.page.wait_for_selector('input', timeout=5000)
                            print("[HAPAG] Found inputs (non-login). Assuming form loaded.")
                            form_loaded = True
                        except:
                            pass


                if form_loaded:
                    print("[HAPAG] Quick Quote form successfully verified. Dismissing any initial modals...")
                    await self._dismiss_hapag_modals()
                    self.is_login_successful = True
                    return True
                else:
                    raise Exception("No confirming Quick Quote page elements were visible after 240s.")
                    
            except Exception as e:
                print(f"[HAPAG] [ERROR] Quick Quote form verification failed: {e}")
                await self.page.screenshot(path="hapag_login_fail.png")
                return False

        except Exception as e:
            print(f"[HAPAG] [ERROR] Login process crashed: {e}")
            await self.page.screenshot(path="hapag_login_crash.png")
            return False

    def _normalize_date_string(self, date_str: str) -> str:
        """
        Normalize various date formats (e.g. 2026-05-31, 31.05.2026, 31 May 2026, 31 May) into ISO YYYY-MM-DD.
        """
        date_str = date_str.strip()
        # Try YYYY-MM-DD
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date().isoformat()
        except ValueError:
            pass
            
        # Try DD.MM.YYYY
        try:
            return datetime.strptime(date_str, "%d.%m.%Y").date().isoformat()
        except ValueError:
            pass
            
        # Try DD-MM-YYYY
        try:
            return datetime.strptime(date_str, "%d-%m-%Y").date().isoformat()
        except ValueError:
            pass
            
        # Try DD MMM YYYY (e.g. 31 May 2026)
        try:
            return datetime.strptime(date_str, "%d %b %Y").date().isoformat()
        except ValueError:
            pass
        try:
            return datetime.strptime(date_str, "%d %B %Y").date().isoformat()
        except ValueError:
            pass
            
        # Try DD MMM (use current/next year)
        try:
            parsed = datetime.strptime(date_str, "%d %b")
            current_year = date.today().year
            res_date = parsed.replace(year=current_year).date()
            if res_date < date.today():
                res_date = res_date.replace(year=current_year + 1)
            return res_date.isoformat()
        except ValueError:
            pass
            
        # Try MMM DD (use current/next year, e.g. Jun 12)
        try:
            parsed = datetime.strptime(date_str, "%b %d")
            current_year = date.today().year
            res_date = parsed.replace(year=current_year).date()
            if res_date < date.today():
                res_date = res_date.replace(year=current_year + 1)
            return res_date.isoformat()
        except ValueError:
            pass

        # Try MMM DD, YYYY (e.g. Jun 12, 2026)
        try:
            return datetime.strptime(date_str, "%b %d, %Y").date().isoformat()
        except ValueError:
            pass

        return date_str

    def extract_validity_date(self, text: str) -> Optional[str]:
        # Pattern 1: Valid 2026-06-25 to 2026-06-30
        match1 = re.search(r'Valid\s+\d{4}-\d{2}-\d{2}\s+to\s+(\d{4}-\d{2}-\d{2})', text, re.IGNORECASE)
        if match1:
            return match1.group(1)
        
        # Pattern 2: Valid to: 30 Jun 2026 or Valid to 30 Jun 2026
        match2 = re.search(r'Valid\s+to:?\s*(\d{1,2}\s+[A-Za-z]{3,10}\s+\d{4})', text, re.IGNORECASE)
        if match2:
            return match2.group(1).strip()
            
        # Pattern 3: Valid to: 2026-06-30
        match3 = re.search(r'Valid\s+to:?\s*(\d{4}-\d{2}-\d{2})', text, re.IGNORECASE)
        if match3:
            return match3.group(1)
            
        return None





    async def _select_hapag_dropdown_option(self, label: str, locode: str, cached_name: Optional[str] = None) -> bool:
        """
        Robustly selects options from Hapag-Lloyd custom dropdown lists.
        Types the locode, waits for list suggestions, and selects the matching suggestion.
        """
        try:
            print(f"[HAPAG] Selecting dropdown option for {label}: '{locode}'...")
            
            # Combine all suggestions selectors (including Quasar-specific classes)
            suggestions_selectors = [
                '.q-menu .q-item',
                '.q-virtual-scroll__content .q-item',
                '.q-select__dialog .q-item',
                '.q-menu [role="option"]',
                '.q-virtual-scroll__content [role="option"]',
                '.q-select__dialog [role="option"]',
                '.q-menu [class*="option" i]',
                '.q-virtual-scroll__content [class*="option" i]',
                '.q-select__dialog [class*="option" i]',
                '.q-menu .q-item__label',
                '.q-virtual-scroll__content .q-item__label',
                '[class*="suggestion" i]',
                '[class*="dropdown" i] li',
                '.el-autocomplete-suggestion li',
                '.el-select-dropdown__item',
                'ul[role="listbox"] li'
            ]
            combined_selector = ", ".join(suggestions_selectors)
            
            # Wait up to 10 seconds for the suggestion popup to become visible
            try:
                await self.page.wait_for_selector(combined_selector, state="visible", timeout=10000)
                print("[HAPAG] Dropdown suggestions became visible.")
            except Exception as wait_err:
                print(f"[HAPAG] Suggestions visible wait timeout. Retrying force-open by clicking field and pressing ArrowDown...")
                try:
                    # Force suggestions list to open/reload
                    input_xpath = f'xpath=(//*[contains(text(), "{label}")])[1]/following::input[1]'
                    input_field = self.page.locator(input_xpath).first
                    await input_field.click()
                    await self.page.keyboard.press("ArrowDown")
                    await self.page.wait_for_selector(combined_selector, state="visible", timeout=8000)
                    print("[HAPAG] Dropdown suggestions became visible after force-open.")
                except Exception as retry_err:
                    print(f"[HAPAG] Suggestions still not visible after retry: {retry_err}")

            await self._human_delay(800, 1500)  # Small buffer time for suggestions to stabilize
            
            # Locate dropdown overlay suggestions
            suggestions = self.page.locator(combined_selector)
            count = await suggestions.count()
            print(f"[HAPAG] Suggestions matching selector count: {count}")
            
            # Filter to only currently visible suggestions in the page
            visible_suggestions = []
            for idx in range(count):
                item = suggestions.nth(idx)
                if await item.is_visible():
                    visible_suggestions.append(item)
            print(f"[HAPAG] Actually visible suggestions count: {len(visible_suggestions)}")
            
            # Match criteria: locode or cached_name
            target_match = locode.upper()
            
            # Scroll and scan suggestions
            for item in visible_suggestions:
                item_text = (await item.text_content() or await item.inner_text() or "").strip().upper()
                print(f"  Visible Suggestion text: '{item_text}'")
                
                # Filter out standard non-port option labels (e.g. Door delivery options)
                is_unit_or_door = (
                    "SELECT UNITS" in item_text or 
                    "TERMINAL/RAMP" in item_text or 
                    re.search(r'\b(KG|LB|DOOR)\b', item_text)
                )
                if is_unit_or_door:
                    continue
                
                if target_match in item_text or (cached_name and cached_name.upper() in item_text):
                    print(f"[HAPAG] [MATCH] Found suggestion: '{item_text}'. Clicking...")
                    try:
                        await item.scroll_into_view_if_needed()
                        await item.click(timeout=3000)
                    except Exception as item_click_err:
                        print(f"[HAPAG] Playwright click on dropdown item failed: {item_click_err}. Trying JS click...")
                        await item.evaluate("el => el.click()")
                    await self._human_delay(1500, 2500)  # Buffer time after selection click to let form settle
                    return True

            # If no exact match, fallback to the first valid (non-Door, non-unit) suggestion
            for item in visible_suggestions:
                item_text = (await item.text_content() or await item.inner_text() or "").strip().upper()
                is_unit_or_door = (
                    "SELECT UNITS" in item_text or 
                    "TERMINAL/RAMP" in item_text or 
                    re.search(r'\b(KG|LB|DOOR)\b', item_text)
                )
                if is_unit_or_door:
                    continue
                print(f"[HAPAG] No exact suggestion matched '{target_match}'. Falling back to first valid option: '{item_text}'.")
                try:
                    await item.scroll_into_view_if_needed()
                    await item.click(timeout=3000)
                except Exception as item_click_err:
                    print(f"[HAPAG] Playwright click on dropdown item fallback failed: {item_click_err}. Trying JS click...")
                    await item.evaluate("el => el.click()")
                await self._human_delay(1500, 2500)
                return True

            print(f"[HAPAG] Dropdown suggestions did not appear or match for {label}.")
            return False
        except Exception as e:
            print(f"[HAPAG] Dropdown selection error for {label}: {e}")
            return False

    async def search_sailing_schedules(self, request: RateSearchRequest) -> list[dict]:
        """
        Crawls Hapag-Lloyd sailing schedules from the Schedule tab.
        """
        schedules = []
        try:
            # Check if page is currently on the login portal
            if "identity.hapag-lloyd.com" in self.page.url or await self.page.locator('input[type="email"], input#email, input#signInName').first.is_visible(timeout=500):
                raise Exception("Redirected to login portal. Schedule query aborted.")

            print("[HAPAG] Navigating to Schedule page...")
            schedule_url = "https://www.hapag-lloyd.com/solutions/schedule/#/"
            await self.page.goto(schedule_url)
            try:
                await self.page.wait_for_load_state("domcontentloaded", timeout=12000)
            except:
                pass
            
            # Check redirect after navigation
            if "identity.hapag-lloyd.com" in self.page.url or await self.page.locator('input[type="email"], input#email, input#signInName').first.is_visible(timeout=500):
                raise Exception("Redirected to login portal after accessing schedule page. Schedule query aborted.")

            await self._check_service_unavailable()
            await self._human_delay(1500, 2500)


            # Dismiss any active modals
            await self._dismiss_hapag_modals()

            # --- START LOCATION (ORIGIN) ---
            if request.origin and ("rotterdam" in request.origin.lower() or request.origin.strip().upper() == "NLRTM"):
                origin_locode = "NLRTM"
            else:
                origin_locode = resolve_port_for_carrier(request.origin, "hapag")
                if not origin_locode or len(origin_locode) != 5:
                    origin_locode = request.origin[:5].upper()

            origin_cached = get_cached_carrier_port("hapag", origin_locode)
            print(f"[HAPAG] Schedule: Filling Start Location: '{origin_locode}' (cached: '{origin_cached}')")

            start_selectors = [
                'xpath=(//*[contains(text(), "Start Location")])[1]/following::input[1]',
                'input:below(:text("Start Location"))',
                'div:has-text("Start Location") input',
                'input[placeholder*="Location" i]',
                'input[type="text"]'
            ]

            start_field = None
            print("[HAPAG] Schedule: Waiting for Start Location input field to become visible...")
            for i in range(20):
                for sel in start_selectors:
                    try:
                        loc = self.page.locator(sel).first
                        if await loc.is_visible(timeout=300):
                            start_field = loc
                            print(f"[HAPAG] Schedule Start input found using selector: {sel}")
                            break
                    except:
                        pass
                if start_field:
                    break
                await self.page.wait_for_timeout(500)

            if not start_field:
                print("[HAPAG] Warning: Start Location input field not found after wait. Falling back...")
                start_field = self.page.locator('input').first

            # Type and select
            start_success = False
            for attempt in range(1, 4):
                print(f"[HAPAG] Attempt {attempt} to fill Start Location on Schedule: '{origin_locode}'")
                try:
                    try:
                        await start_field.scroll_into_view_if_needed()
                    except Exception as scroll_err:
                        print(f"[HAPAG] Warning: scroll_into_view failed for Start Location input: {scroll_err}")
                    await start_field.click()
                    await self._human_delay(300, 600)
                    await start_field.fill("")  # fill() clears in one call
                    await self._human_delay(200, 400)
                    await start_field.type(origin_locode, delay=50)
                    await self._human_delay(1500, 2500)

                    if await self._select_hapag_dropdown_option("Start Location", origin_locode, origin_cached):
                        start_success = True
                        break
                    else:
                        print(f"[HAPAG] Attempt {attempt} failed to select Start Location dropdown on Schedule.")
                except Exception as fill_err:
                    print(f"[HAPAG] Attempt {attempt} failed to fill Start Location on Schedule: {fill_err}")
                    await self._human_delay(1000, 2000)

            if not start_success:
                raise Exception("Failed to select Start Location on Schedule page.")

            await self._human_delay(1000, 1800)

            # --- END LOCATION (DESTINATION) ---
            if request.destination and ("rotterdam" in request.destination.lower() or request.destination.strip().upper() == "NLRTM"):
                dest_locode = "NLRTM"
            else:
                dest_locode = resolve_port_for_carrier(request.destination, "hapag")
                if not dest_locode or len(dest_locode) != 5:
                    dest_locode = request.destination[:5].upper()

            dest_cached = get_cached_carrier_port("hapag", dest_locode)
            print(f"[HAPAG] Schedule: Filling End Location: '{dest_locode}' (cached: '{dest_cached}')")

            end_selectors = [
                'xpath=(//*[contains(text(), "End Location")])[1]/following::input[1]',
                'input[type="text"]'
            ]

            end_field = None
            print("[HAPAG] Schedule: Waiting for End Location input field to become visible...")
            for i in range(20):
                for sel in end_selectors:
                    try:
                        if sel == 'input[type="text"]':
                            loc = self.page.locator(sel).nth(1)
                        else:
                            loc = self.page.locator(sel).first
                        if await loc.is_visible(timeout=300):
                            end_field = loc
                            print(f"[HAPAG] Schedule End input found using selector: {sel}")
                            break
                    except:
                        pass
                if end_field:
                    break
                await self.page.wait_for_timeout(500)

            if not end_field:
                print("[HAPAG] Warning: End Location input field not found after wait. Falling back...")
                visible_inputs = self.page.locator('input:visible')
                if await visible_inputs.count() > 1:
                    end_field = visible_inputs.nth(1)
                    print("[HAPAG] Fallback to second visible input on page.")
                else:
                    end_field = self.page.locator('input').nth(1)
                    print("[HAPAG] Fallback to second general input on page.")

            end_success = False
            for attempt in range(1, 4):
                print(f"[HAPAG] Attempt {attempt} to fill End Location on Schedule: '{dest_locode}'")
                try:
                    try:
                        await end_field.scroll_into_view_if_needed()
                    except Exception as scroll_err:
                        print(f"[HAPAG] Warning: scroll_into_view failed for End Location input: {scroll_err}")
                    await end_field.click()
                    await self._human_delay(300, 600)
                    await end_field.fill("")  # fill() clears in one call
                    await self._human_delay(200, 400)
                    await end_field.type(dest_locode, delay=50)
                    await self._human_delay(1500, 2500)

                    if await self._select_hapag_dropdown_option("End Location", dest_locode, dest_cached):
                        end_success = True
                        break
                    else:
                        print(f"[HAPAG] Attempt {attempt} failed to select End Location dropdown on Schedule.")
                except Exception as fill_err:
                    print(f"[HAPAG] Attempt {attempt} failed to fill End Location on Schedule: {fill_err}")
                    await self._human_delay(1000, 2000)

            if not end_success:
                raise Exception("Failed to select End Location on Schedule page.")

            # NOTE: No start date fill needed — schedule page defaults to today,
            # and we only need Origin + Destination + Container Type + Search.

            # --- ADVANCED SEARCH & CONTAINER TYPE ---
            try:
                # Check if already expanded ("Hide advanced search" visible)
                is_expanded = False
                try:
                    is_expanded = await self.page.locator(':text("Hide advanced search")').first.is_visible(timeout=1500)
                except:
                    pass
                if not is_expanded:
                    print("[HAPAG] Schedule: Clicking 'Advanced search' to expand...")
                    # Try multiple selector strategies for the toggle
                    adv_toggle_selectors = [
                        ':text("Advanced search")',
                        'text=Advanced search',
                        'button:has-text("Advanced")',
                        'a:has-text("Advanced")',
                        'span:has-text("Advanced search")',
                    ]
                    adv_clicked = False
                    for adv_sel in adv_toggle_selectors:
                        try:
                            loc = self.page.locator(adv_sel).first
                            if await loc.is_visible(timeout=1000):
                                await loc.click()
                                adv_clicked = True
                                print(f"[HAPAG] Schedule: Advanced search expanded via '{adv_sel}'")
                                break
                        except:
                            pass
                    if not adv_clicked:
                        print("[HAPAG] Schedule: Could not find Advanced search toggle — container type may not be available")
                    await self._human_delay(1000, 1800)
                else:
                    print("[HAPAG] Schedule: Advanced search already expanded.")
            except Exception as adv_err:
                print(f"[HAPAG] Schedule: Advanced search expand error: {adv_err}")

            # Force using "DRY 40H" (40' General Purpose High Cube) to query all departures.
            # Hapag-Lloyd returns pricing for all 3 container types (20/40/40H) in the same document
            # regardless of which one was selected, but selecting 40'HC displays the maximum number of departures.
            hapag_container = "40' General Purpose High Cube"

            print(f"[HAPAG] Schedule: Selecting container type: '{hapag_container}'")
            container_selected = False
            try:
                # Press Escape first to close any stray open dropdowns
                await self.page.keyboard.press("Escape")
                await self._human_delay(300, 500)

                # Find container type dropdown — it's the LAST q-select on the page
                # (after Start Location and End Location selects)
                container_box = None
                container_selectors = [
                    'xpath=(//*[contains(text(), "Container Type")])[last()]/following::input[1]',
                    'xpath=(//*[contains(text(), "Container Type")])[1]/following::input[1]',
                    'input:below(:text("Container Type"))',
                ]
                for sel in container_selectors:
                    try:
                        loc = self.page.locator(sel).first
                        if await loc.is_visible(timeout=1500):
                            container_box = loc
                            print(f"[HAPAG] Schedule container input found: {sel}")
                            break
                    except:
                        pass

                # Fallback: use the LAST visible q-select__focus-target
                if not container_box:
                    q_selects = self.page.locator('input.q-select__focus-target')
                    q_count = await q_selects.count()
                    print(f"[HAPAG] Schedule: {q_count} q-select inputs found")
                    for idx in range(q_count - 1, -1, -1):
                        try:
                            if await q_selects.nth(idx).is_visible(timeout=500):
                                container_box = q_selects.nth(idx)
                                print(f"[HAPAG] Schedule: Using q-select at index {idx} for container type")
                                break
                        except:
                            pass

                if container_box:
                    try:
                        await container_box.scroll_into_view_if_needed()
                    except Exception as scroll_err:
                        print(f"[HAPAG] Warning: scroll_into_view failed for schedule container box: {scroll_err}")
                    try:
                        await container_box.click(timeout=3000)
                    except Exception as click_err:
                        print(f"[HAPAG] Playwright click on schedule container box failed: {click_err}. Trying JS click...")
                        try:
                            await container_box.evaluate("el => el.click()")
                        except Exception as js_click_err:
                            print(f"[HAPAG] JS click on schedule container box failed: {js_click_err}")
                    await self._human_delay(1000, 1800)

                    # Select matching option
                    option = self.page.locator(
                        f'.q-menu .q-item:has-text("{hapag_container}"), '
                        f'div.q-item:has-text("{hapag_container}"), '
                        f'.q-select__dialog .q-item:has-text("{hapag_container}"), '
                        f'[role="option"]:has-text("{hapag_container}")'
                    ).first
                    if await option.is_visible(timeout=5000):
                        try:
                            try:
                                await option.scroll_into_view_if_needed()
                            except Exception as scroll_err:
                                print(f"[HAPAG] Warning: scroll_into_view failed for container option: {scroll_err}")
                            await option.click(timeout=3000)
                        except Exception as option_err:
                            print(f"[HAPAG] Playwright click on option failed: {option_err}. Trying JS click...")
                            try:
                                await option.evaluate("el => el.click()")
                            except Exception as js_err:
                                print(f"[HAPAG] JS click on option failed: {js_err}")
                        container_selected = True
                        print(f"[HAPAG] Schedule: Container type selected: {hapag_container}")
                    else:
                        # Try partial match (e.g. "High Cube" or "General Purpose")
                        short_label = hapag_container.split("'")[0].strip() if "'" in hapag_container else hapag_container[:10]
                        option2 = self.page.locator(f'.q-menu .q-item:has-text("{short_label}"), div.q-item:has-text("{short_label}")').first
                        if await option2.is_visible(timeout=2000):
                            txt = (await option2.inner_text()).strip()
                            try:
                                try:
                                    await option2.scroll_into_view_if_needed()
                                except Exception as scroll_err:
                                    print(f"[HAPAG] Warning: scroll_into_view failed for container option2: {scroll_err}")
                                await option2.click(timeout=3000)
                            except Exception as option_err:
                                print(f"[HAPAG] Playwright click on option2 failed: {option_err}. Trying JS click...")
                                try:
                                    await option2.evaluate("el => el.click()")
                                except Exception as js_err:
                                    print(f"[HAPAG] JS click on option2 failed: {js_err}")
                            container_selected = True
                            print(f"[HAPAG] Schedule: Container selected (partial match): {txt}")
                        else:
                            print(f"[HAPAG] Schedule: Container option '{hapag_container}' not found — pressing Escape")
                            await self.page.keyboard.press("Escape")
                    await self._human_delay(500, 1000)
                else:
                    print("[HAPAG] Schedule: Container type input NOT found — skipping")
            except Exception as container_err:
                print(f"[HAPAG] Schedule: Container type selection failed: {container_err}")
                try:
                    await self.page.keyboard.press("Escape")
                except:
                    pass

            # Press Escape to close any open dropdown before clicking Search
            await self.page.keyboard.press("Escape")
            await self._human_delay(400, 700)

            # Take screenshot before clicking Search for debugging
            try:
                await self.page.screenshot(path="scratch/hapag_schedule_before_search.png")
            except:
                pass

            # --- VALIDATE AND RE-FILL IF TURNSTILE CLEARED INPUTS ---
            try:
                orig_val = ""
                dest_val = ""
                if start_field:
                    orig_val = (await start_field.input_value()).strip()
                if end_field:
                    dest_val = (await end_field.input_value()).strip()
                    
                if not orig_val or not dest_val:
                    print("[HAPAG] Warning: Form input fields are empty prior to schedule search (Turnstile redirect likely cleared them). Re-filling...")
                    if not orig_val and start_field:
                        try:
                            await start_field.scroll_into_view_if_needed()
                        except Exception as scroll_err:
                            print(f"[HAPAG] Warning: scroll_into_view failed for Start Location input during re-fill: {scroll_err}")
                        await start_field.click()
                        await start_field.fill("")  # fill() clears in one call
                        await start_field.type(origin_locode, delay=50)
                        await self._human_delay(1500, 2500)
                        await self._select_hapag_dropdown_option("Start Location", origin_locode, origin_cached)
                        
                    if not dest_val and end_field:
                        try:
                            await end_field.scroll_into_view_if_needed()
                        except Exception as scroll_err:
                            print(f"[HAPAG] Warning: scroll_into_view failed for End Location input during re-fill: {scroll_err}")
                        await end_field.click()
                        await end_field.fill("")  # fill() clears in one call
                        await end_field.type(dest_locode, delay=50)
                        await self._human_delay(1500, 2500)
                        await self._select_hapag_dropdown_option("End Location", dest_locode, dest_cached)
            except Exception as re_err:
                print(f"[HAPAG] Warning: Validation/Re-filling empty inputs failed: {re_err}")

            # --- SEARCH ---
            print("[HAPAG] Schedule: Clicking Search...")
            search_btn = None
            search_selectors = [
                'form button[type="submit"]:has-text("Search")',
                'div[role="search"] button:has-text("Search")',
                'button[type="submit"]:has-text("Search")',
                'button.q-btn:has-text("Search")',
                'button[class*="primary"]:has-text("Search")',
            ]
            for sel in search_selectors:
                try:
                    locs = self.page.locator(sel)
                    count = await locs.count()
                    for idx in range(count):
                        try:
                            if await locs.nth(idx).is_visible(timeout=500):
                                search_btn = locs.nth(idx)
                                print(f"[HAPAG] Schedule: Search button found via '{sel}' at index {idx}")
                                break
                        except:
                            pass
                    if search_btn:
                        break
                except:
                    pass
            
            if not search_btn:
                # Fallback to specifically avoid the top nav if possible
                search_btn = self.page.locator('button:has-text("Search")').last

            try:
                await search_btn.scroll_into_view_if_needed()
            except Exception as scroll_e:
                print(f"[HAPAG] Warning: scroll_into_view failed for search button: {scroll_e}")
            await self._human_delay(500, 1000)
            
            try:
                await search_btn.click(force=True)
                print("[HAPAG] Schedule: Search button clicked.")
            except Exception as click_err:
                print(f"[HAPAG] Warning: Playwright click on search button failed: {click_err}. Trying JS click...")
                try:
                    await search_btn.evaluate("el => el.click()")
                except Exception as js_err:
                    print(f"[HAPAG] JS click on search button failed: {js_err}. Trying fallback click...")
                    await self.page.locator('button:has-text("Search")').last.click(force=True)
            
            # Additional fallback: press Enter just in case the button click was intercepted
            try:
                await search_btn.press("Enter")
            except:
                pass
                
            # Short settle only — the selector wait below actively detects the results
            # (up to 45s), so a long blind wait here just adds latency.
            await self._human_delay(1500, 2500)

            # Wait for schedule results
            print("[HAPAG] Waiting for schedule results (up to 45s)...")
            try:
                await self.page.wait_for_selector(
                    'div:has-text("Doc Cut-off"), div:has-text("Voyage no"), div.sailing-card, span:has-text("Voyage no"), :has-text("Doc Cut-off")', 
                    timeout=45000
                )
                print("[HAPAG] Schedule results loaded.")
            except Exception as wait_err:
                print(f"[HAPAG] Timeout waiting for schedule results: {wait_err}")
                await self.page.screenshot(path="scratch/hapag_schedule_wait_timeout.png")
                return []

            # --- SCRAPE RESULTS ---
            schedules = await self.page.evaluate(r'''() => {
                const results = [];
                const processedCards = new Set();
                const voyageLabels = Array.from(document.querySelectorAll('*')).filter(el => {
                    const text = (el.textContent || "");
                    if (!text.includes("Voyage no")) return false;
                    return !Array.from(el.children).some(child => (child.textContent || "").includes("Voyage no"));
                });

                voyageLabels.forEach(voyageEl => {
                    let card = voyageEl.parentElement;
                    let foundCard = false;
                    for (let depth = 0; depth < 10; depth++) {
                        if (!card) break;
                        const text = (card.textContent || "");
                        if (text.includes("Voyage no") && (text.includes("Show Details") || text.includes("Hide Details") || text.includes("Quote Now"))) {
                            foundCard = true;
                            break;
                        }
                        card = card.parentElement;
                    }

                    if (!foundCard || !card) return;
                    if (processedCards.has(card)) return;
                    processedCards.add(card);

                    let is_sold_out = false;
                    let prev = card.previousElementSibling;
                    for (let i = 0; i < 3; i++) {
                        if (prev) {
                            const prevText = (prev.textContent || "").toLowerCase();
                            if (prevText.includes("no space available") || prevText.includes("sold out")) {
                                is_sold_out = true;
                                break;
                            }
                            prev = prev.previousElementSibling;
                        }
                    }

                    const cardText = (card.textContent || "").replace(/\s+/g, " ");

                    const dateRegex = /\d{4}-\d{2}-\d{2}/g;
                    const dates = cardText.match(dateRegex) || [];

                    if (dates.length < 2) return;
                    const etd = dates[0];
                    const eta = dates[1];

                    let routing = "Direct";
                    const viaMatch = cardText.match(/via:\s*(.*?)(?=Terminal|Doc Cut-off|FCL Cut-off|$)/i);
                    if (viaMatch) {
                        const ports = viaMatch[1].replace(/Terminal.*$/i, "").trim();
                        routing = "Transshipment via " + ports.replace(/\s+/g, " ");
                    }

                    const voyageMatch = cardText.match(/Voyage no\s*\.?\s*:\s*(\S+)/i);
                    const voyage = voyageMatch ? voyageMatch[1] : "";

                    let vessel = "Hapag Vessel";
                    let service = "Hapag Service";

                    const voyageParent = voyageEl.parentElement;
                    if (voyageParent) {
                        const chips = Array.from(voyageParent.querySelectorAll('span, button, a, div'))
                            .map(c => (c.textContent || "").trim())
                            .filter(Boolean);
                        
                        const voyageIndex = chips.findIndex(c => c.includes("Voyage no"));
                        if (voyageIndex !== -1) {
                            if (voyageIndex > 0) {
                                vessel = chips[voyageIndex - 1];
                            }
                            if (voyageIndex > 1) {
                                service = chips[voyageIndex - 2];
                            }
                        }
                    }

                    const docCutoffMatch = cardText.match(/Doc Cut-off\s+(\d{4}-\d{2}-\d{2})/i);
                    const fclCutoffMatch = cardText.match(/FCL Cut-off\s+(\d{4}-\d{2}-\d{2})/i);
                    const vgmCutoffMatch = cardText.match(/VGM Cut-off\s+(\d{4}-\d{2}-\d{2})/i);

                    const doc_cutoff = docCutoffMatch ? docCutoffMatch[1] : "";
                    const fcl_cutoff = fclCutoffMatch ? fclCutoffMatch[1] : "";
                    const vgm_cutoff = vgmCutoffMatch ? vgmCutoffMatch[1] : "";

                    let transit = null;
                    try {
                        const d1 = new Date(etd);
                        const d2 = new Date(eta);
                        const diffTime = Math.abs(d2 - d1);
                        transit = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
                    } catch (e) {}

                    results.push({
                        etd: etd,
                        eta: eta,
                        transit_time_days: transit,
                        voyage: voyage,
                        vessel: vessel,
                        service: service,
                        doc_cutoff: doc_cutoff,
                        fcl_cutoff: fcl_cutoff,
                        vgm_cutoff: vgm_cutoff,
                        is_sold_out: is_sold_out,
                        routing: routing
                    });
                });

                return results;
            }''')

            print(f"[HAPAG] Successfully crawled {len(schedules)} sailing schedules:")
            for s in schedules:
                print(f"  ETD={s['etd']} ETA={s['eta']} Vessel='{s['vessel']}' Voyage='{s['voyage']}' Service='{s['service']}'")

        except Exception as e:
            print(f"[HAPAG] [ERROR] Failed to crawl sailing schedules: {e}")
            try:
                await self.page.screenshot(path="scratch/hapag_schedule_crawl_crash.png")
            except:
                pass

        return schedules

    def _find_matching_schedule(self, quote_etd: str, schedules: list[dict]) -> Optional[dict]:
        """
        Fuzzy match quote ETD with crawled schedules within a window of +/- 2 days.
        """
        if not quote_etd or not schedules:
            return None
            
        try:
            q_date = datetime.strptime(quote_etd, "%Y-%m-%d").date()
        except Exception as e:
            print(f"[HAPAG] Error parsing quote ETD '{quote_etd}': {e}")
            return None
            
        best_match = None
        min_diff = 999
        
        for s in schedules:
            if not s.get("etd"):
                continue
            try:
                s_date = datetime.strptime(s["etd"], "%Y-%m-%d").date()
            except Exception as e:
                print(f"[HAPAG] Error parsing schedule ETD '{s['etd']}': {e}")
                continue
            diff = abs((q_date - s_date).days)
            if diff <= 2:  # +/- 2 days window
                if diff < min_diff:
                    min_diff = diff
                    best_match = s
                    
        return best_match

    async def search_quotes(self, request: RateSearchRequest) -> CarrierResultStatus:
        try:
            # Check if page is currently on the login portal
            if "identity.hapag-lloyd.com" in self.page.url or await self.page.locator('input[type="email"], input#email, input#signInName').first.is_visible(timeout=500):
                print("[HAPAG] Redirected to login portal. Aborting Quick Quote search.")
                return CarrierResultStatus.LOGIN_FAILED

            print("[HAPAG] Starting Quick Quote search...")
            self.current_request = request
            
            # Dismiss any active modals (like "Recently Searched") before form filling
            await self._dismiss_hapag_modals()
            
            # --- CHECK IF ALREADY ON RESULTS PAGE ---
            is_results = False
            try:
                # Check if departures calendar grid or Price Breakdown button is visible
                results_el = self.page.locator('text=/\\d{4}-\\d{2}-\\d{2}/, button:has-text("Price Breakdown")').first
                if await results_el.is_visible(timeout=3000):
                    is_results = True
                    print("[HAPAG] Detected that browser is already on the results/Offer Selection page.")
            except:
                pass
                
            if is_results:
                print("[HAPAG] Clicking 'Edit' button to expand search form...")
                edit_selectors = [
                    'button:has-text("Edit")',
                    'span:has-text("Edit")',
                    '.left-panel button',
                    'div.search-summary button',
                    'xpath=//button[contains(., "Edit")]'
                ]
                
                edit_clicked = False
                for sel in edit_selectors:
                    try:
                        btn = self.page.locator(sel).first
                        if await btn.is_visible(timeout=1000):
                            await btn.click()
                            print(f"[HAPAG] Clicked Edit button using selector: {sel}")
                            edit_clicked = True
                            break
                    except:
                        pass
                        
                if edit_clicked:
                    await self._human_delay(1500, 2500)
                else:
                    print("[HAPAG] Warning: Edit button not found or not clickable.")
            
            # --- START LOCATION (ORIGIN) ---
            if request.origin and ("rotterdam" in request.origin.lower() or request.origin.strip().upper() == "NLRTM"):
                origin_locode = "NLRTM"
            else:
                origin_locode = resolve_port_for_carrier(request.origin, "hapag")
                if not origin_locode or len(origin_locode) != 5:
                    origin_locode = request.origin[:5].upper()

            origin_cached = get_cached_carrier_port("hapag", origin_locode)
            print(f"[HAPAG] Filling Start Location: '{origin_locode}' (cached: '{origin_cached}')")

            # Find Start Location text input
            start_selectors = [
                'xpath=(//*[contains(text(), "Start Location")])[1]/following::input[1]',
                'input[placeholder*="Start" i]',
                'input[placeholder*="Origin" i]',
            ]
            
            start_field = None
            print("[HAPAG] Waiting for Start Location input field to become visible...")
            for i in range(20):
                for sel in start_selectors:
                    try:
                        loc = self.page.locator(sel).first
                        if await loc.is_visible(timeout=300):
                            start_field = loc
                            print(f"[HAPAG] Start Location input found using selector: {sel}")
                            break
                    except:
                        pass
                if start_field:
                    break
                await asyncio.sleep(1)
            
            if not start_field:
                # Absolute fallback: first visible input
                visible_inputs = self.page.locator('input:visible')
                if await visible_inputs.count() > 0:
                    start_field = visible_inputs.first
                    print("[HAPAG] Fallback to first visible input on page.")
                else:
                    start_field = self.page.locator('input').first
                    print("[HAPAG] Fallback to first general input on page.")

            # Try to fill and select Start Location (up to 3 attempts)
            start_success = False
            for attempt in range(1, 4):
                print(f"[HAPAG] Attempt {attempt} to fill Start Location: '{origin_locode}'")
                await start_field.scroll_into_view_if_needed()
                await start_field.click()
                await self._human_delay(300, 600)
                await start_field.fill("")  # fill() clears in one call
                await self._human_delay(200, 400)
                await start_field.type(origin_locode, delay=50)
                await self._human_delay(1500, 2500)
                
                if await self._select_hapag_dropdown_option("Start Location", origin_locode, origin_cached):
                    start_success = True
                    break
                else:
                    print(f"[HAPAG] Attempt {attempt} failed to select Start Location dropdown option.")
                    await self.page.screenshot(path=f"hapag_start_location_fail_attempt_{attempt}.png")
            
            if not start_success:
                raise Exception("Failed to select Start Location dropdown option after 3 attempts.")

            # Settle wait after origin suggestion selection before destination click/type
            await self._human_delay(1200, 2000)

            # --- END LOCATION (DESTINATION) ---
            if request.destination and ("rotterdam" in request.destination.lower() or request.destination.strip().upper() == "NLRTM"):
                dest_locode = "NLRTM"
            else:
                dest_locode = resolve_port_for_carrier(request.destination, "hapag")
                if not dest_locode or len(dest_locode) != 5:
                    dest_locode = request.destination[:5].upper()

            dest_cached = get_cached_carrier_port("hapag", dest_locode)
            print(f"[HAPAG] Filling End Location: '{dest_locode}' (cached: '{dest_cached}')")

            # Find End Location text input
            end_selectors = [
                'xpath=(//*[contains(text(), "End Location")])[1]/following::input[1]',
                'input[placeholder*="End" i]',
                'input[placeholder*="Destination" i]',
            ]
            
            end_field = None
            print("[HAPAG] Waiting for End Location input field to become visible...")
            for i in range(20):
                for sel in end_selectors:
                    try:
                        loc = self.page.locator(sel).first
                        if await loc.is_visible(timeout=300):
                            end_field = loc
                            print(f"[HAPAG] End Location input found using selector: {sel}")
                            break
                    except:
                        pass
                if end_field:
                    break
                await asyncio.sleep(1)
            
            if not end_field:
                # Fallback to second visible input
                visible_inputs = self.page.locator('input:visible')
                if await visible_inputs.count() > 1:
                    end_field = visible_inputs.nth(1)
                    print("[HAPAG] Fallback to second visible input on page.")
                else:
                    end_field = self.page.locator('input').nth(1)
                    print("[HAPAG] Fallback to second general input on page.")

            # Try to fill and select End Location (up to 3 attempts)
            end_success = False
            for attempt in range(1, 4):
                print(f"[HAPAG] Attempt {attempt} to fill End Location: '{dest_locode}'")
                await end_field.scroll_into_view_if_needed()
                await end_field.click()
                await self._human_delay(300, 600)
                await end_field.fill("")  # fill() clears in one call
                await self._human_delay(200, 400)
                await end_field.type(dest_locode, delay=50)
                await self._human_delay(1500, 2500)
                
                if await self._select_hapag_dropdown_option("End Location", dest_locode, dest_cached):
                    end_success = True
                    break
                else:
                    print(f"[HAPAG] Attempt {attempt} failed to select End Location dropdown option.")
                    await self.page.screenshot(path=f"hapag_end_location_fail_attempt_{attempt}.png")
            
            if not end_success:
                raise Exception("Failed to select End Location dropdown option after 3 attempts.")

            # --- CONTAINER TYPE ---
            # Force using "DRY 40H" (40' General Purpose High Cube) to query all departures.
            # Hapag-Lloyd returns pricing for all 3 container types (20/40/40H) in the same document
            # regardless of which one was selected, but selecting 40'HC displays the maximum number of departures.
            hapag_container = "40' General Purpose High Cube"

            print(f"[HAPAG] Mapped container to choose: '{hapag_container}'")

            # Always select container type — Hapag default is 20' GP, not 40' HC
            try:
                container_selectors = [
                    'input.q-select__focus-target',
                    'xpath=(//input[contains(@class, "q-select__focus-target")])[1]'
                ]
                container_box = None
                for sel in container_selectors:
                    try:
                        loc = self.page.locator(sel).first
                        if await loc.is_visible(timeout=1000):
                            container_box = loc
                            print(f"[HAPAG] Container select input found using: {sel}")
                            break
                    except:
                        pass
                if not container_box:
                    container_box = self.page.locator('input.q-select__focus-target').first

                await container_box.scroll_into_view_if_needed()
                try:
                    await container_box.click(timeout=3000)
                except Exception as click_err:
                    print(f"[HAPAG] Playwright click on container box failed: {click_err}. Trying JS click...")
                    await container_box.evaluate("el => el.click()")
                await self._human_delay(1000, 1800)

                # Choose option containing container type name
                option = self.page.locator(
                    f'.q-menu .q-item:has-text("{hapag_container}"), '
                    f'div.q-item:has-text("{hapag_container}"), '
                    f'.q-select__dialog .q-item:has-text("{hapag_container}")'
                ).first
                if await option.is_visible(timeout=5000):
                    try:
                        await option.scroll_into_view_if_needed()
                        await option.click(timeout=3000)
                    except Exception as option_err:
                        print(f"[HAPAG] Playwright click on container option failed: {option_err}. Trying JS click...")
                        await option.evaluate("el => el.click()")
                    print(f"[HAPAG] Container type selected successfully: {hapag_container}")
                else:
                    print(f"[HAPAG] Container option not found for '{hapag_container}' — pressing Escape")
                    await self.page.keyboard.press("Escape")
                # Wait for quantity/weight rows to render after container selection
                await self._human_delay(1000, 1500)
            except Exception as container_err:
                print(f"[HAPAG] Container type selection failed: {container_err}")

            # --- CONTAINER QUANTITY ---
            print(f"[HAPAG] Setting Container Quantity: {request.container_quantity}")
            try:
                qty_selectors = [
                    'xpath=(//input[@type="number"])[1]',
                    'input[type="number"]',
                    'div:has-text("Container Quantity") input[type="number"]'
                ]
                qty_box = None
                for sel in qty_selectors:
                    try:
                        loc = self.page.locator(sel).first
                        if await loc.is_visible(timeout=1000):
                            qty_box = loc
                            print(f"[HAPAG] Quantity input found using: {sel}")
                            break
                    except:
                        pass
                if not qty_box:
                    qty_box = self.page.locator('xpath=(//input[@type="number"])[1]').first
                
                await qty_box.scroll_into_view_if_needed()
                await qty_box.click()
                await self._human_delay(200, 400)
                # Plain number input, no autocomplete to trigger — fill() clears and
                # populates in one call (typing char-by-char buys nothing here).
                await qty_box.fill(str(request.container_quantity))
                await self._human_delay(300, 600)
            except Exception as qty_err:
                print(f"[HAPAG] Quantity fill failed: {qty_err}")

            # --- CARGO WEIGHT ---
            # Hapag-Lloyd max cargo weight is around 28470 kg. Cap it to 28000 to be safe and prevent validation blocks.
            weight_val = min(max(int(request.weight_per_container_kg), 5000), 28000)
            print(f"[HAPAG] Setting Cargo Weight: {weight_val} kg")
            try:
                weight_selectors = [
                    'xpath=(//input[@type="number"])[2]',
                    'xpath=(//input[@type="number" or @class="q-field__native q-placeholder"])[2]',
                    'div:has-text("Weight per Container") input[type="number"]'
                ]
                weight_box = None
                for sel in weight_selectors:
                    try:
                        loc = self.page.locator(sel).first
                        if await loc.is_visible(timeout=1000):
                            weight_box = loc
                            print(f"[HAPAG] Weight input found using: {sel}")
                            break
                    except:
                        pass
                if not weight_box:
                    weight_box = self.page.locator('xpath=(//input[@type="number"])[2]').first
                
                await weight_box.scroll_into_view_if_needed()
                await weight_box.click()
                await self._human_delay(200, 400)
                # Plain number input — single fill() replaces clear+type sequence.
                await weight_box.fill(str(weight_val))
                await self._human_delay(300, 600)
            except Exception as weight_err:
                print(f"[HAPAG] Weight fill failed: {weight_err}")

            # --- SEARCH ---
            print("[HAPAG] Clicking 'Search' (orange box)...")
            try:
                # Find the Search button robustly
                search_selectors = [
                    'button:has-text("Search")',
                    'button[type="submit"]:has-text("Search")',
                    'xpath=//button[contains(., "Search")]',
                    'xpath=//*[contains(@class, "orange") or contains(@class, "button") or contains(@class, "btn")][contains(., "Search")]',
                    'span:has-text("Search")',
                    '[role="button"]:has-text("Search")',
                    'button:has-text("Get Quote")',
                    'button:has-text("Find Rates")'
                ]
                
                search_btn = None
                for sel in search_selectors:
                    try:
                        locs = self.page.locator(sel)
                        count = await locs.count()
                        for idx in range(count):
                            candidate = locs.nth(idx)
                            if await candidate.is_visible(timeout=500):
                                tag = await candidate.evaluate("el => el.tagName.toLowerCase()")
                                is_header = tag in ("h1", "h2", "h3", "h4", "h5", "h6")
                                if not is_header:
                                    search_btn = candidate
                                    print(f"[HAPAG] Search button found using selector: {sel} (tag: {tag})")
                                    break
                        if search_btn:
                            break
                    except:
                        pass
                
                if not search_btn:
                    search_btn = self.page.locator('button:has-text("Search"), button.orange').first
                    print("[HAPAG] Fallback to first Search button or orange button.")
                
                await search_btn.scroll_into_view_if_needed()
                await search_btn.click()
                print("[HAPAG] Quote search submitted successfully!")
                try:
                    await self.page.wait_for_load_state("domcontentloaded", timeout=12000)
                except:
                    pass
                # Short settle only — the 180s results-detection loop below actively
                # polls for quote cards, so a long blind wait here is redundant.
                await self._human_delay(1500, 2500)
            except Exception as submit_err:
                print(f"[HAPAG] Submit failed: {submit_err}")
                await self.page.screenshot(path="hapag_submit_fail.png")
                return CarrierResultStatus.UNKNOWN_ERROR

            # Results detection
            print("[HAPAG] Waiting for search results to load (up to 180s)...")
            start_wait = asyncio.get_event_loop().time()
            max_wait_seconds = 180
            results_found = False
            no_rates_found = False
            
            # Create scratch dir if not exists
            os.makedirs("scratch", exist_ok=True)
            
            while asyncio.get_event_loop().time() - start_wait < max_wait_seconds:
                if not self.page or (self.page.is_closed() if hasattr(self.page, "is_closed") and callable(self.page.is_closed) else getattr(self.page, "is_closed", False)):
                    raise Exception("Playwright page is closed or crashed while waiting for search results.")
                
                await self._wait_for_captcha_resolution()

                elapsed = int(asyncio.get_event_loop().time() - start_wait)
                
                # Periodically take a screenshot and log status
                if elapsed > 0 and elapsed % 15 == 0:
                    print(f"[HAPAG] Still waiting for results... ({elapsed}s elapsed)")
                    # Save a rolling diagnostic screenshot
                    try:
                        await self.page.screenshot(path=f"scratch/hapag_loading_{elapsed}s.png")
                    except Exception as ss_err:
                        print(f"[HAPAG] Diagnostic screenshot failed: {ss_err}")
                
                # Check if results are visible
                try:
                    # Check for date format YYYY-MM-DD or Price Breakdown or Select button
                    results_selectors = [
                        'text=/\\d{4}-\\d{2}-\\d{2}/',
                        'text=/\\d{2}\\.\\d{2}\\.\\d{4}/',
                        'text=/\\d{2}-\\d{2}-\\d{4}/',
                        'text=/\\d{2}\\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)/i',
                        'text=/(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\\s+\\d{1,2}/i',
                        '[class*="sailing" i]',
                        '[class*="price" i]',
                        'button:has-text("Select")',
                        'button:has-text("Price Breakdown")'
                    ]
                    
                    found_selector = None
                    for sel in results_selectors:
                        try:
                            loc = self.page.locator(sel).first
                            if await loc.is_visible(timeout=200):
                                found_selector = sel
                                break
                        except:
                            pass
                            
                    if found_selector:
                        # Wait for loader spinner or "Offer is loading" text to be hidden before confirming results are ready
                        is_loading = False
                        try:
                            loading_el = self.page.locator('text="Offer is loading" i, [class*="loading" i]:not([class*="sonner"]):not([class*="toast"]):not([class*="productfruits"]):not([class*="heap"])').first
                            if await loading_el.is_visible(timeout=200):
                                is_loading = True
                        except:
                            pass
                        
                        if is_loading:
                            print("[HAPAG] Results matched selector, but 'Offer is loading' or spinner is still active. Waiting...")
                        else:
                            print(f"[HAPAG] Results detected via selector: '{found_selector}'")
                            results_found = True
                            break
                except Exception as detect_err:
                    print(f"[HAPAG] Error in selector check: {detect_err}")
                
                # Check for explicit "No rates" or "No schedules" messages, or service blockages
                try:
                    page_text = await self.page.inner_text('body')
                    text_lower = page_text.lower()
                    if "service is currently unavailable" in text_lower or "service is temporarily unavailable" in text_lower:
                        print("[HAPAG] Hapag-Lloyd anti-bot blocked the request (Service is currently unavailable popup detected).")
                        no_rates_found = True
                        break
                    if any(msg in text_lower for msg in [
                        "no result", 
                        "no schedule", 
                        "no rate",
                        "no offer",
                        "no routing found",
                        "could not be found",
                        "is not available"
                    ]):
                        print("[HAPAG] Explicitly reported: No quotes available.")
                        no_rates_found = True
                        break
                except:
                    pass
                
                await asyncio.sleep(2)
                
            if results_found:
                print("[HAPAG] Sourced quotes successfully.")
                return CarrierResultStatus.AVAILABLE_QUOTES_FOUND
            elif no_rates_found:
                return CarrierResultStatus.NO_QUOTES_AVAILABLE
            else:
                print("[HAPAG] Results wait timeout.")
                await self.page.screenshot(path="hapag_results_fail.png")
                return CarrierResultStatus.NO_QUOTES_AVAILABLE

        except Exception as e:
            print(f"[HAPAG] Sourcing form fill failed: {e}")
            await self.page.screenshot(path="hapag_form_crash.png")
            return CarrierResultStatus.UNKNOWN_ERROR

    async def extract_quote_list(self) -> list[dict]:
        try:
            # Dismiss any obscuring popups that might have appeared after results loaded
            await self._dismiss_hapag_modals()

            # Screenshot the results page to see what we're working with
            try:
                await self.page.screenshot(path="scratch/hapag_results_before_calendar.png")
                page_sample = (await self.page.inner_text('body'))[:500].replace('\n', ' ')
                print(f"[HAPAG] Page text sample: {page_sample}")
            except:
                pass

            print("[HAPAG] Paginating through all departure columns in calendar grid...")
            # Wait for calendar grid / departure dates to appear using a robust fallback sequence
            date_selectors = [
                'text=/\\d{4}-\\d{2}-\\d{2}/',
                'text=/\\d{2}\\.\\d{2}\\.\\d{4}/',
                'text=/\\d{2}-\\d{2}-\\d{4}/',
                'text=/\\d{2}\\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)/i'
            ]
            found_date_element = False
            for sel in date_selectors:
                try:
                    await self.page.wait_for_selector(sel, timeout=4000)
                    found_date_element = True
                    print(f"[HAPAG] Date element detected in grid using: '{sel}'")
                    break
                except:
                    pass
            if not found_date_element:
                print("[HAPAG] Warning: No standard date headers found. Sifting page text elements directly...")

            # ------------------------------------------------------------------
            # JS helper: scrape all visible date columns and their prices (excluding portal/dialog)
            # ------------------------------------------------------------------
            JS_GET_VISIBLE_DATES_AND_PRICES = '''() => {
                const patterns = [
                    /^\\d{4}-\\d{2}-\\d{2}$/,
                    /^\\d{2}\\.\\d{2}\\.\\d{4}$/,
                    /^\\d{2}-\\d{2}-\\d{4}$/,
                    /^\\d{2}\\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\\s+\\d{4}$/i,
                    /^\\d{2}\\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*$/i,
                    /^(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\\s+\\d{1,2}$/i,
                    /^(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\\s+\\d{1,2},\\s+\\d{4}$/i
                ];
                const dateEls = Array.from(document.querySelectorAll('*')).filter(el => {
                    const raw = (el.innerText || el.textContent || '').trim().replace(/\\s+/g, ' ');
                    if (!raw || raw.length > 30) return false;
                    if (!patterns.some(pat => pat.test(raw))) return false;
                    let parent = el.parentElement;
                    while (parent) {
                        const id = (parent.id || '').toLowerCase();
                        const cls = (parent.className || '').toLowerCase();
                        if (id.includes('q-portal') || cls.includes('q-dialog') || cls.includes('el-dialog') || cls.includes('modal')) return false;
                        if (cls.includes('summary') || cls.includes('sidebar') || cls.includes('left-panel') ||
                            cls.includes('criteria') || cls.includes('quick-quotes') ||
                            id.includes('summary') || id.includes('sidebar') || id.includes('left-panel')) return false;
                        parent = parent.parentElement;
                    }
                    return true;
                });
                const cols = [];
                const seen = new Set();
                dateEls.forEach(el => {
                    const rect = el.getBoundingClientRect();
                    const txt = (el.innerText || el.textContent || '').trim();
                    if (rect.width > 0 && rect.height > 0 && !seen.has(txt)) {
                        seen.add(txt);
                        
                        // Extract price from parent container
                        let price = null;
                        let parent = el.parentElement;
                        for (let i = 0; i < 4; i++) {
                            if (!parent) break;
                            const pTxt = (parent.innerText || parent.textContent || '').trim().replace(/\s+/g, ' ');
                            const match = pTxt.match(/(?:USD|\\$)\\s*(-?[\\d,]+(?:\\.\\d{1,2})?)/i);
                            if (match) {
                                price = parseFloat(match[1].replace(/,/g, ''));
                                break;
                            }
                            parent = parent.parentElement;
                        }
                        cols.push({
                            raw_date: txt,
                            price: price
                        });
                    }
                });
                return cols;
            }'''


            # ------------------------------------------------------------------
            # JS helper: check if the "No further departures" end-of-line message
            # is visible anywhere on the page (tooltip or inline text)
            # ------------------------------------------------------------------
            JS_IS_END_OF_QUOTES = '''() => {
                const needle = 'no further departures currently available for quoting';
                const allEls = Array.from(document.querySelectorAll('*'));
                return allEls.some(el => {
                    if (el.children.length > 0) return false;
                    const txt = (el.textContent || '').trim().toLowerCase();
                    return txt.includes(needle);
                });
            }'''

            # ------------------------------------------------------------------
            # Selectors for the right-arrow navigation button in the calendar grid
            # ------------------------------------------------------------------
            ARROW_RIGHT_SELECTORS = [
                'button[aria-label*="next" i]',
                'button[aria-label*="forward" i]',
                'button[aria-label*="right" i]',
                '[class*="arrow-right" i]',
                '[class*="next" i] button',
                'button[class*="next" i]',
                # Generic: a visible button with > or chevron that is NOT a submit/search button
                'button.q-btn:not([type="submit"]):not([aria-label*="search" i])'
            ]

            all_dates_seen: list[str] = []       # ordered, de-duped list of all ETD strings
            seen_set: set[str] = set()
            date_to_price: dict[str, float] = {}
            max_pages = 25          # safety cap -- Hapag-Lloyd has at most ~8-12 weeks of departures
            page_num = 0

            # JS to click the rightmost visible arrow/chevron button in the grid
            JS_CLICK_RIGHT_ARROW = '''() => {
                const candidates = Array.from(document.querySelectorAll('button, [role="button"], .q-btn, i, span'));
                const visible = candidates.filter(el => {
                    const r = el.getBoundingClientRect();
                    return r.width > 0 && r.height > 0;
                });
                // Score each button: prefer ones whose text/class/aria-label suggests a right-navigation
                // and exclude search/submit buttons
                const arrows = visible.filter(el => {
                    const txt = (el.textContent || '').trim().replace(/\s+/g, ' ');
                    const cls = (el.className || '').toLowerCase();
                    const lbl = (el.getAttribute('aria-label') || '').toLowerCase();
                    const isNav = (
                        txt === '>' ||
                        txt.includes('chevron_right') ||
                        txt.includes('chevron-right') ||
                        txt.includes('arrow_forward') ||
                        cls.includes('arrow-right') || cls.includes('chevron-right') ||
                        cls.includes('next') ||
                        lbl.includes('next') || lbl.includes('right') || lbl.includes('forward')
                    );
                    const isSearch = cls.includes('search') || lbl.includes('search') || el.type === 'submit';
                    return isNav && !isSearch;
                });
                if (arrows.length > 0) {
                    // Pick rightmost button (the > arrow in the calendar toolbar)
                    arrows.sort((a, b) => b.getBoundingClientRect().left - a.getBoundingClientRect().left);
                    const btn = arrows[0];
                    // Check if disabled
                    if (btn.disabled || btn.getAttribute('aria-disabled') === 'true') return 'disabled';
                    
                    let clickable = btn;
                    while (clickable && clickable.tagName !== 'BUTTON' && !clickable.classList.contains('q-btn') && clickable.parentElement) {
                        if (clickable.getAttribute('role') === 'button') break;
                        clickable = clickable.parentElement;
                    }
                    if (clickable) {
                        clickable.click();
                        return 'clicked';
                    }
                    btn.click();
                    return 'clicked';
                }
                return 'not_found';
            }'''

            while page_num < max_pages:
                page_num += 1
                await self._human_delay(600, 900)

                # Read unique dates and prices currently visible in the grid
                visible_data: list[dict] = await self.page.evaluate(JS_GET_VISIBLE_DATES_AND_PRICES)
                new_count = 0
                for item in visible_data:
                    d = item["raw_date"]
                    p = item["price"]
                    if p is not None:
                        date_to_price[d] = p
                    if d not in seen_set:
                        seen_set.add(d)
                        all_dates_seen.append(d)
                        new_count += 1

                print(f"[HAPAG] Page {page_num}: {len(visible_data)} columns visible, {new_count} new -> total {len(all_dates_seen)} unique dates so far")

                # Try to click the right-arrow to advance to the next column window
                # NOTE: we check the end sentinel only AFTER a click yields 0 new dates,
                # because the tooltip is always present in the DOM even before it's hoverable.
                arrow_result = await self.page.evaluate(JS_CLICK_RIGHT_ARROW)
                print(f"[HAPAG] Right-arrow JS result: {arrow_result}")

                if arrow_result == 'disabled':
                    print("[HAPAG] Right-arrow is disabled -- end of departures reached.")
                    break

                if arrow_result == 'not_found':
                    print("[HAPAG] No right-arrow button found -- assuming end of departures.")
                    break

                # Arrow was clicked -- wait for new columns to render
                await self._human_delay(900, 1400)

                # Check how many new dates appeared after the click
                visible_after_data: list[dict] = await self.page.evaluate(JS_GET_VISIBLE_DATES_AND_PRICES)
                visible_after = [item["raw_date"] for item in visible_after_data]
                new_after = sum(1 for d in visible_after if d not in seen_set)

                if new_after == 0:
                    # Grid did not advance -- we've reached the end
                    end_reached = await self.page.evaluate(JS_IS_END_OF_QUOTES)
                    if end_reached:
                        print("[HAPAG] No new dates after arrow click and end sentinel confirmed -- done.")
                    else:
                        print("[HAPAG] No new dates after arrow click -- grid exhausted.")
                    break

            print(f"[HAPAG] Pagination complete. Total unique departure dates collected: {len(all_dates_seen)}")
            for d in all_dates_seen:
                print(f"  >> {d}")

            self._all_quotes = []
            for seq_idx, raw_date_str in enumerate(all_dates_seen):
                normalized_date = self._normalize_date_string(raw_date_str)
                grid_price = date_to_price.get(raw_date_str, 0.0)
                self._all_quotes.append({
                    # seq_idx is the logical position (0-based) across all paginated pages
                    # page_offset will be calculated in open_price_breakdown to know how many
                    # arrow clicks are needed to bring this date into view
                    "seq_idx": seq_idx,
                    "raw_date": raw_date_str,
                    "etd": normalized_date,
                    "eta": None,
                    "transit_time_days": None,
                    "via_routing": "",
                    "service_name": "Hapag Service",
                    "vessel": "Hapag Vessel",
                    "total_price": grid_price,
                    "currency": "USD",
                    "is_sold_out": False,
                    "source": "carrier_portal",
                    "carrier_code": self.carrier_code
                })
                
            return self._all_quotes
        except Exception as e:
            print(f"[HAPAG] Quotes sifting error: {e}")
            return []

    async def open_price_breakdown(self, quote_ref: dict) -> bool:
        try:
            self._last_parsed_card_prices = {}
            self._last_parsed_validity_till = None

            if not self.page or (self.page.is_closed() if hasattr(self.page, "is_closed") and callable(self.page.is_closed) else getattr(self.page, "is_closed", False)):
                raise Exception("Playwright page is closed or crashed at start of open_price_breakdown.")
            await self._wait_for_captcha_resolution()

            raw_date = quote_ref.get("raw_date", quote_ref.get("etd", ""))
            seq_idx  = quote_ref.get("seq_idx", 0)
            print(f"[HAPAG] Navigating to departure date '{raw_date}' (seq {seq_idx})...")

            # ------------------------------------------------------------------
            # JS helpers re-used in this method
            # ------------------------------------------------------------------
            JS_GET_VISIBLE_DATES = '''() => {
                const patterns = [
                    /^\\d{4}-\\d{2}-\\d{2}$/,
                    /^\\d{2}\\.\\d{2}\\.\\d{4}$/,
                    /^\\d{2}-\\d{2}-\\d{4}$/,
                    /^\\d{2}\\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\\s+\\d{4}$/i,
                    /^\\d{2}\\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*$/i,
                    /^(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\\s+\\d{1,2}$/i,
                    /^(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\\s+\\d{1,2},\\s+\\d{4}$/i
                ];
                const dateEls = Array.from(document.querySelectorAll('*')).filter(el => {
                    const txt = (el.innerText || el.textContent || '').trim().replace(/\\s+/g, ' ');
                    if (!patterns.some(pat => pat.test(txt))) return false;
                    let parent = el.parentElement;
                    while (parent) {
                        const id = (parent.id || '').toLowerCase();
                        const cls = (parent.className || '').toLowerCase();
                        if (id.includes('q-portal') || cls.includes('q-dialog') || cls.includes('el-dialog') || cls.includes('modal')) return false;
                        if (cls.includes('summary') || cls.includes('sidebar') || cls.includes('left-panel') || 
                            cls.includes('criteria') || cls.includes('quick-quotes') ||
                            id.includes('summary') || id.includes('sidebar') || id.includes('left-panel')) return false;
                        parent = parent.parentElement;
                    }
                    return true;
                });
                return dateEls.filter(el => {
                    const r = el.getBoundingClientRect();
                    return r.width > 0 && r.height > 0;
                }).map(el => el.textContent.trim());
            }'''

            JS_CLICK_LEFT_ARROW = '''() => {
                const candidates = Array.from(document.querySelectorAll('button, [role="button"], .q-btn, i, span'));
                const visible = candidates.filter(el => {
                    const r = el.getBoundingClientRect();
                    return r.width > 0 && r.height > 0;
                });
                const arrows = visible.filter(el => {
                    const txt = (el.textContent || '').trim().replace(/\s+/g, ' ');
                    const cls = (el.className || '').toLowerCase();
                    const lbl = (el.getAttribute('aria-label') || '').toLowerCase();
                    const isNav = (
                        txt === '<' ||
                        txt.includes('chevron_left') ||
                        txt.includes('chevron-left') ||
                        txt.includes('arrow_back') ||
                        cls.includes('arrow-left') || cls.includes('chevron-left') ||
                        cls.includes('prev') || cls.includes('back') ||
                        lbl.includes('prev') || lbl.includes('left') || lbl.includes('back') || lbl.includes('previous')
                    );
                    const isSearch = cls.includes('search') || lbl.includes('search') || el.type === 'submit';
                    return isNav && !isSearch;
                });
                if (arrows.length > 0) {
                    arrows.sort((a, b) => a.getBoundingClientRect().left - b.getBoundingClientRect().left);
                    const btn = arrows[0];
                    if (btn.disabled || btn.getAttribute('aria-disabled') === 'true') return 'disabled';
                    
                    let clickable = btn;
                    while (clickable && clickable.tagName !== 'BUTTON' && !clickable.classList.contains('q-btn') && clickable.parentElement) {
                        if (clickable.getAttribute('role') === 'button') break;
                        clickable = clickable.parentElement;
                    }
                    if (clickable) {
                        clickable.click();
                        return 'clicked';
                    }
                    btn.click();
                    return 'clicked';
                }
                return 'not_found';
            }'''

            JS_CLICK_RIGHT_ARROW = '''() => {
                const candidates = Array.from(document.querySelectorAll('button, [role="button"], .q-btn, i, span'));
                const visible = candidates.filter(el => {
                    const r = el.getBoundingClientRect();
                    return r.width > 0 && r.height > 0;
                });
                const arrows = visible.filter(el => {
                    const txt = (el.textContent || '').trim().replace(/\s+/g, ' ');
                    const cls = (el.className || '').toLowerCase();
                    const lbl = (el.getAttribute('aria-label') || '').toLowerCase();
                    const isNav = (
                        txt === '>' ||
                        txt.includes('chevron_right') ||
                        txt.includes('chevron-right') ||
                        txt.includes('arrow_forward') ||
                        cls.includes('arrow-right') || cls.includes('chevron-right') ||
                        cls.includes('next') ||
                        lbl.includes('next') || lbl.includes('right') || lbl.includes('forward')
                    );
                    const isSearch = cls.includes('search') || lbl.includes('search') || el.type === 'submit';
                    return isNav && !isSearch;
                });
                if (arrows.length > 0) {
                    arrows.sort((a, b) => b.getBoundingClientRect().left - a.getBoundingClientRect().left);
                    const btn = arrows[0];
                    if (btn.disabled || btn.getAttribute('aria-disabled') === 'true') return 'disabled';
                    
                    let clickable = btn;
                    while (clickable && clickable.tagName !== 'BUTTON' && !clickable.classList.contains('q-btn') && clickable.parentElement) {
                        if (clickable.getAttribute('role') === 'button') break;
                        clickable = clickable.parentElement;
                    }
                    if (clickable) {
                        clickable.click();
                        return 'clicked';
                    }
                    btn.click();
                    return 'clicked';
                }
                return 'not_found';
            }'''

            target_idx = quote_ref.get("seq_idx", 0)

            # ------------------------------------------------------------------
            # Step 1: navigate left or right until target date is visible in the grid
            # ------------------------------------------------------------------
            for nav_attempt in range(30):    # safety: at most 30 arrow clicks
                if not self.page or (self.page.is_closed() if hasattr(self.page, "is_closed") and callable(self.page.is_closed) else getattr(self.page, "is_closed", False)):
                    raise Exception("Playwright page is closed or crashed during date navigation.")
                
                await self._dismiss_hapag_modals()
                await self._wait_for_captcha_resolution()

                visible: list[str] = await self.page.evaluate(JS_GET_VISIBLE_DATES)
                if raw_date in visible:
                    print(f"[HAPAG] Target date '{raw_date}' is now visible in grid.")
                    break

                # Determine direction to move
                direction = "right"  # default fallback
                target_etd = quote_ref.get("etd")
                if self._all_quotes and target_etd:
                    visible_etds = []
                    for vd in visible:
                        match = next((q for q in self._all_quotes if q["raw_date"] == vd), None)
                        if match and match.get("etd"):
                            visible_etds.append(match["etd"])
                    if visible_etds:
                        min_vis_etd = min(visible_etds)
                        max_vis_etd = max(visible_etds)
                        if target_etd < min_vis_etd:
                            direction = "left"
                        elif target_etd > max_vis_etd:
                            direction = "right"

                if direction == "left":
                    arrow_result = await self.page.evaluate(JS_CLICK_LEFT_ARROW)
                    print(f"[HAPAG] Left-arrow click #{nav_attempt+1} JS result: {arrow_result} (target_idx {target_idx})")
                else:
                    arrow_result = await self.page.evaluate(JS_CLICK_RIGHT_ARROW)
                    print(f"[HAPAG] Right-arrow click #{nav_attempt+1} JS result: {arrow_result} (target_idx {target_idx})")

                if arrow_result in ['disabled', 'not_found']:
                    print(f"[HAPAG] Arrow navigation returned '{arrow_result}' -- assuming date not reachable.")
                    break

                await self._human_delay(800, 1200)

            # ------------------------------------------------------------------
            # Step 2: Click the correct date column by text content (not DOM index)
            # ------------------------------------------------------------------
            clicked = await self.page.evaluate(r'''targetDate => {
                const patterns = [
                    /^\d{4}-\d{2}-\d{2}$/,
                    /^\d{2}\.\d{2}\.\d{4}$/,
                    /^\d{2}-\d{2}-\d{4}$/,
                    /^\d{2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}$/i,
                    /^\d{2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*$/i,
                    /^(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2}$/i,
                    /^(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},\s+\d{4}$/i
                ];
                const dateEls = Array.from(document.querySelectorAll('*')).filter(el => {
                    const txt = (el.innerText || el.textContent || '').trim().replace(/\s+/g, ' ');
                    if (!patterns.some(pat => pat.test(txt))) return false;
                    let parent = el.parentElement;
                    while (parent) {
                        const id = (parent.id || '').toLowerCase();
                        const cls = (parent.className || '').toLowerCase();
                        if (id.includes('q-portal') || cls.includes('q-dialog') || cls.includes('el-dialog') || cls.includes('modal')) return false;
                        if (cls.includes('summary') || cls.includes('sidebar') || cls.includes('left-panel') || 
                            cls.includes('criteria') || cls.includes('quick-quotes') ||
                            id.includes('summary') || id.includes('sidebar') || id.includes('left-panel')) return false;
                        parent = parent.parentElement;
                    }
                    return true;
                });
                const visible = dateEls.filter(el => {
                    const r = el.getBoundingClientRect();
                    return r.width > 0 && r.height > 0;
                });
                const target = visible.find(el => el.textContent.trim() === targetDate);
                if (target) {
                    target.click();
                    // Also click parent cell (TH/TD)
                    let cell = target;
                    while (cell && cell.tagName !== 'TH' && cell.tagName !== 'TD' && !cell.classList.contains('cell')) {
                        cell = cell.parentElement;
                    }
                    if (cell) cell.click();
                    return true;
                }
                return false;
            }''', raw_date)
            
            if not clicked:
                print(f"[HAPAG] Could not click column '{raw_date}'.")
                return False
                
            if not self.page or (self.page.is_closed() if hasattr(self.page, "is_closed") and callable(self.page.is_closed) else getattr(self.page, "is_closed", False)):
                raise Exception("Playwright page is closed or crashed after clicking date column.")
            await self._wait_for_captcha_resolution()
                
            # Wait for any loading indicator to disappear (up to 15 seconds)
            print("[HAPAG] Waiting for details loading spinner to hide...")
            try:
                for check in range(30):
                    if not self.page or (self.page.is_closed() if hasattr(self.page, "is_closed") and callable(self.page.is_closed) else getattr(self.page, "is_closed", False)):
                        raise Exception("Playwright page is closed or crashed while waiting for details spinner.")
                    await self._wait_for_captcha_resolution()
                    
                    loading_selectors = [
                        'text="Offer is loading" i',
                        '.q-loading',
                        '.loading',
                        '[class*="loading" i]:not([class*="sonner"]):not([class*="toast"]):not([class*="productfruits"]):not([class*="heap"])'
                    ]
                    is_still_loading = False
                    for sel in loading_selectors:
                        try:
                            loc = self.page.locator(sel).first
                            if await loc.is_visible(timeout=100):
                                is_still_loading = True
                                break
                        except:
                            pass
                    if not is_still_loading:
                        break
                    await asyncio.sleep(0.5)
            except Exception as wait_err:
                print(f"[HAPAG] Warning: Error waiting for loading spinner: {wait_err}")
                
            await self._human_delay(1200, 2200)
            
            # --- PARSE DETAILS FROM LEFT PANEL ---
            tt = None
            via_routing = ""
            try:
                left_panel = self.page.locator('div:has-text("Estimated Transit Time"), [class*="search" i], [class*="summary" i]').first
                left_panel_text = await left_panel.inner_text()
                
                tt_match = re.search(r'Estimated Transit Time\s*(\d+)\s*days?', left_panel_text, re.IGNORECASE)
                if not tt_match:
                    tt_match = re.search(r'(\d+)\s*days?', left_panel_text, re.IGNORECASE)
                if tt_match:
                    tt = int(tt_match.group(1))
                    
                via_match = re.search(r'via\s*:\s*([^\n\r]+)', left_panel_text, re.IGNORECASE)
                if via_match:
                    via_routing = via_match.group(1).strip()
            except Exception as left_err:
                print(f"[HAPAG] Warning: Left panel parsing failed: {left_err}")
                
            if tt:
                quote_ref["transit_time_days"] = tt
                try:
                    etd_date = datetime.strptime(quote_ref["etd"], "%Y-%m-%d").date()
                    eta_date = etd_date + timedelta(days=tt)
                    quote_ref["eta"] = eta_date.isoformat()
                except:
                    pass
            if via_routing:
                quote_ref["via_routing"] = via_routing
                quote_ref["service_name"] = f"Hapag Service (via {via_routing})"
                
            print(f"[HAPAG] Parsed transit time: {tt} days, via: '{via_routing}'")
            
            # Parse card price directly for fallback and sold-out screening across all 3 container types
            self._last_parsed_card_prices = {}
            try:
                card_prices = await self.page.evaluate(r'''() => {
                    const res = {
                        "DRY 20": null,
                        "DRY 40": null,
                        "DRY 40H": null
                    };
                    const containerKeys = {
                        "20STD": "DRY 20",
                        "20'STD": "DRY 20",
                        "20GP": "DRY 20",
                        "20'GP": "DRY 20",
                        "20'": "DRY 20",
                        
                        "40STD": "DRY 40",
                        "40'STD": "DRY 40",
                        "40GP": "DRY 40",
                        "40'GP": "DRY 40",
                        "40'": "DRY 40",
                        
                        "40HC": "DRY 40H",
                        "40'HC": "DRY 40H",
                        "40HQ": "DRY 40H",
                        "40'HQ": "DRY 40H",
                        "High Cube": "DRY 40H"
                    };

                    const rows = Array.from(document.querySelectorAll('div, span, p, tr, td'));
                    for (const row of rows) {
                        if (row.children.length > 8) continue;
                        const txt = (row.textContent || '').trim();
                        for (const [label, typeKey] of Object.entries(containerKeys)) {
                            if (txt.includes(label) && (txt.includes("USD") || txt.includes("$") || txt.includes("/Container"))) {
                                const cleanTxt = txt.replace(/\s+/g, ' ');
                                if (/\bUSD\s*-(?!\d)/i.test(cleanTxt) || /-(?!\d)\s*\/Container/i.test(cleanTxt) || /-(?!\d)\u00a0\/Container/i.test(cleanTxt) || cleanTxt.includes("not available") || cleanTxt.includes("sold out")) {
                                    if (res[typeKey] === null) {
                                        res[typeKey] = "sold_out";
                                    }
                                } else {
                                    const match = cleanTxt.match(/(?:USD|\$)\s*(-?[\d,]+(?:\.\d{1,2})?)/i);
                                    if (match) {
                                        const val = parseFloat(match[1].replace(/,/g, ''));
                                        if (!isNaN(val) && val !== 0) {
                                            if (res[typeKey] === null || res[typeKey] === "sold_out") {
                                                res[typeKey] = val;
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }

                    // Fallback to scanning body innerText lines
                    const allText = document.body.innerText || "";
                    const lines = allText.split("\n");
                    for (const line of lines) {
                        const cleanLine = line.replace(/\s+/g, ' ').trim();
                        for (const [label, typeKey] of Object.entries(containerKeys)) {
                            if (cleanLine.includes(label)) {
                                if (/\bUSD\s*-(?!\d)/i.test(cleanLine) || /-(?!\d)\s*\/Container/i.test(cleanLine) || /-(?!\d)\u00a0\/Container/i.test(cleanLine) || cleanLine.includes("sold out") || cleanLine.includes("not available")) {
                                    if (res[typeKey] === null) {
                                        res[typeKey] = "sold_out";
                                    }
                                } else {
                                    const match = cleanLine.match(/(?:USD|\$)\s*(-?[\d,]+(?:\.\d{1,2})?)/i);
                                    if (match) {
                                        const val = parseFloat(match[1].replace(/,/g, ''));
                                        if (!isNaN(val) && val !== 0) {
                                            if (res[typeKey] === null || res[typeKey] === "sold_out") {
                                                res[typeKey] = val;
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                    return res;
                }''')
                print(f"[HAPAG] Multi-container card price evaluation results: {card_prices}")
                if isinstance(card_prices, dict):
                    self._last_parsed_card_prices = card_prices
                
                # Check if all are sold out
                all_sold_out = all(v == "sold_out" or v is None for v in self._last_parsed_card_prices.values())
                if all_sold_out:
                    print(f"[HAPAG] All container types are sold out / unavailable for this departure.")
                    quote_ref["is_sold_out"] = True
                    return False
            except Exception as pe:
                print(f"[HAPAG] Warning: Card price evaluation failed: {pe}")

            # Dismiss any onboarding tutorial popups that might intercept the Price Breakdown click
            print("[HAPAG] Dismissing any tutorial popups before clicking Price Breakdown...")
            await self._dismiss_hapag_modals()
            await self._human_delay(500, 800)
            
            # Find Price Breakdown button
            pb_selectors = [
                'button:has-text("Price Breakdown")',
                'button[title="Price Breakdown"]',
                'span:has-text("Price Breakdown")',
                'div.price-breakdown button'
            ]
            
            pb_btn = None
            for sel in pb_selectors:
                try:
                    loc = self.page.locator(sel).first
                    if await loc.is_visible(timeout=1000):
                        pb_btn = loc
                        break
                except:
                    pass
                    
            if not self.page or (self.page.is_closed() if hasattr(self.page, "is_closed") and callable(self.page.is_closed) else getattr(self.page, "is_closed", False)):
                raise Exception("Playwright page is closed or crashed before clicking Price Breakdown.")
            await self._wait_for_captcha_resolution()

            # Click Price Breakdown -- use JS click as fallback if intercepted by overlay
            print("[HAPAG] Clicking 'Price Breakdown' button...")
            try:
                await pb_btn.scroll_into_view_if_needed(timeout=5000)
                await pb_btn.click(timeout=8000)
            except Exception as click_err:
                print(f"[HAPAG] Playwright click blocked ({click_err}). Falling back to JS click...")
                await self.page.evaluate('''() => {
                    const btns = Array.from(document.querySelectorAll('button[title="Price Breakdown"], button'));
                    const pb = btns.find(b => b.textContent.includes("Price Breakdown") || b.title === "Price Breakdown");
                    if (pb) pb.click();
                }''')
            
            # Wait for modal dialog to open
            print("[HAPAG] Waiting for Price Breakdown modal...")
            modal_selectors = [
                '[role="dialog"]',
                '.el-dialog',
                'div:has-text("Freight Charges")'
            ]
            
            modal_opened = False
            for sel in modal_selectors:
                try:
                    if not self.page or (self.page.is_closed() if hasattr(self.page, "is_closed") and callable(self.page.is_closed) else getattr(self.page, "is_closed", False)):
                        raise Exception("Playwright page is closed or crashed while waiting for Price Breakdown modal.")
                    await self._wait_for_captcha_resolution()

                    if await self.page.locator(sel).first.is_visible(timeout=5000):
                        modal_opened = True
                        print(f"[HAPAG] Price Breakdown modal opened successfully using: {sel}")
                        break
                except:
                    pass
                    
            if not modal_opened:
                try:
                    await self.page.wait_for_selector('text="Freight Charges"', timeout=5000)
                    modal_opened = True
                    print("[HAPAG] Price Breakdown modal found via text search.")
                except:
                    pass
                    
            if modal_opened:
                await self._human_delay(1000, 1800)
                return True
                
            print("[HAPAG] Failed to detect Price Breakdown modal.")
            return False
            
        except Exception as e:
            print(f"[HAPAG] open_price_breakdown failed: {e}")
            return False

    async def extract_charge_breakdown(self) -> dict[str, list[dict]]:
        charges = {"DRY 20": [], "DRY 40": [], "DRY 40H": []}
        try:
            if not self.page or (self.page.is_closed() if hasattr(self.page, "is_closed") and callable(self.page.is_closed) else getattr(self.page, "is_closed", False)):
                raise Exception("Playwright page is closed or crashed at start of extract_charge_breakdown.")
            await self._wait_for_captcha_resolution()

            print("[HAPAG] Extracting validity date from body text...")
            try:
                page_text = await self.page.inner_text("body")
                validity_date = self.extract_validity_date(page_text)
                if validity_date:
                    self._last_parsed_validity_till = self._normalize_date_string(validity_date)
                    print(f"[HAPAG] Extracted validity_till: {self._last_parsed_validity_till}")
                else:
                    self._last_parsed_validity_till = None
            except Exception as e:
                print(f"[HAPAG] Warning: failed to extract validity date: {e}")
                self._last_parsed_validity_till = None

            print("[HAPAG] Parsing breakdown table for all container sizes...")
            
            # --- DEBUG DUMP MODAL ROWS (gated behind HAPAG_DEBUG=true) ---
            import os as _os
            if _os.getenv("HAPAG_DEBUG", "").lower() == "true":
                try:
                    dump_res = await self.page.evaluate('''() => {
                        const rows = Array.from(document.querySelectorAll('tr, div[role="row"]'));
                        return rows.map((r, i) => {
                            const cells = Array.from(r.querySelectorAll('td, th, div[role="gridcell"], div[role="columnheader"]'));
                            return `Row ${i} (${r.tagName}): ` + cells.map(c => `[${c.tagName}: ${c.textContent.trim()}]`).join(", ");
                        });
                    }''')
                    print("[HAPAG] [DEBUG DUMP] Modal Rows:")
                    for line in dump_res:
                        print(f"  >> {line}")
                except Exception as de:
                    print(f"[HAPAG] Debug dump failed: {de}")
            
            charges = await self.page.evaluate(r'''() => {
                let idx_20 = -1;
                let idx_40 = -1;
                let idx_40h = -1;

                // Dynamically detect column header position
                const allRows = Array.from(document.querySelectorAll('tr, div[role="row"]'));
                let headerRows = [];
                for (const r of allRows) {
                    const cells = Array.from(r.querySelectorAll('td, th, div[role="gridcell"], div[role="columnheader"]'));
                    if (cells.length >= 3) {
                        const cellTexts = cells.map(c => (c.textContent || '').trim());
                        if (cellTexts.includes("Unit") && (cellTexts.includes("Curr.") || cellTexts.includes("Currency"))) {
                            headerRows.push(cells);
                        }
                    }
                }

                // Pick the matching header row with the maximum number of cells to align with data rows
                headerRows.sort((a, b) => b.length - a.length);
                let headerRow = headerRows[0] || null;

                if (headerRow) {
                    const searchTerms20 = ["20STD", "20'STD", "20GP", "20'GP", "20'"];
                    const searchTerms40 = ["40STD", "40'STD", "40GP", "40'GP", "40'"];
                    const searchTerms40h = ["40HC", "40'HC", "40HQ", "40'HQ", "High Cube"];
                    for (let idx = 0; idx < headerRow.length; idx++) {
                        const headerText = (headerRow[idx].textContent || '').trim().replace(/\s+/g, '');
                        if (searchTerms20.some(term => headerText.includes(term.replace(/\s+/g, '')))) {
                            idx_20 = idx;
                        } else if (searchTerms40.some(term => headerText.includes(term.replace(/\s+/g, '')))) {
                            idx_40 = idx;
                        } else if (searchTerms40h.some(term => headerText.includes(term.replace(/\s+/g, '')))) {
                            idx_40h = idx;
                        }
                    }
                }

                // Fallback to default indexes only if no container columns were mapped at all
                if (idx_20 === -1 && idx_40 === -1 && idx_40h === -1) {
                    idx_20 = 3;
                    idx_40 = 4;
                    idx_40h = 5;
                }
                
                const results = {
                    "DRY 20": [],
                    "DRY 40": [],
                    "DRY 40H": []
                };
                const rows = Array.from(document.querySelectorAll('tr, div[role="row"]'));
                let currentSection = "";
                
                function parseAmount(valStr) {
                    if (!valStr || valStr === "-" || valStr === "not applicable" || valStr.toLowerCase() === "included") {
                        return null;
                    }
                    const match = valStr.replace(/,/g, '').match(/[\d\.]+/);
                    if (match) {
                        const val = parseFloat(match[0]);
                        if (!isNaN(val) && val !== 0) {
                            return val;
                        }
                    }
                    return null;
                }

                for (const row of rows) {
                    const cells = Array.from(row.querySelectorAll('td, th, div[role="gridcell"], div[role="columnheader"]'));
                    if (cells.length === 0) continue;
                    
                    const firstCellText = cells[0].textContent ? cells[0].textContent.trim() : "";
                    const lowerText = firstCellText.toLowerCase();
                    
                    if (lowerText === "freight charges") {
                        currentSection = "freight_charges";
                        continue;
                    }
                    if (lowerText === "freight surcharges" || lowerText === "surcharges") {
                        currentSection = "surcharges";
                        continue;
                    }
                    if (lowerText === "export surcharges") {
                        currentSection = "export_surcharges";
                        continue;
                    }
                    if (lowerText === "import surcharges") {
                        currentSection = "import_surcharges";
                        continue;
                    }
                    
                    if (cells.length >= 4) {
                        // Skip table header elements
                        if (row.closest('thead') || cells.some(c => c.tagName === 'TH' || c.getAttribute('role') === 'columnheader')) {
                            continue;
                        }
                        
                        const name = cells[0].textContent ? cells[0].textContent.trim() : "";
                        const unit = cells[1].textContent ? cells[1].textContent.trim() : "";
                        const curr = cells[2].textContent ? cells[2].textContent.trim() : "";
                        
                        // Ignore header labels, section descriptors, or empty rows
                        if (!name || name === "Freight Charges" || name === "Freight Surcharges" || 
                            name === "Charge" || name === "Unit" || name === "Currency" || name === "Ctr." ||
                            name.includes("20STD") || name.includes("40STD") || name.includes("40HC") ||
                            curr.includes("20STD") || curr.includes("40STD") || curr.includes("40HC") ||
                            curr.includes("20'STD") || curr.includes("40'STD") || curr.includes("40'HC")) {
                            continue;
                        }
                        
                        const valStr_20 = (idx_20 !== -1 && cells[idx_20]) ? (cells[idx_20].textContent || "").trim() : "";
                        const valStr_40 = (idx_40 !== -1 && cells[idx_40]) ? (cells[idx_40].textContent || "").trim() : "";
                        const valStr_40h = (idx_40h !== -1 && cells[idx_40h]) ? (cells[idx_40h].textContent || "").trim() : "";

                        let amt_20 = parseAmount(valStr_20);
                        let amt_40 = parseAmount(valStr_40);
                        let amt_40h = parseAmount(valStr_40h);

                        const isIrrelevant = (unit.toLowerCase() === "bl" || unit.toLowerCase() === "b/l" || 
                                              (idx_20 !== -1 && valStr_20.toLowerCase().includes("irrelevant")) ||
                                              (idx_40 !== -1 && valStr_40.toLowerCase().includes("irrelevant")) ||
                                              (idx_40h !== -1 && valStr_40h.toLowerCase().includes("irrelevant")));
                        
                        const commonAmt = amt_20 || amt_40 || amt_40h;
                        if (isIrrelevant && commonAmt !== null) {
                            if (idx_20 !== -1 && amt_20 === null) amt_20 = commonAmt;
                            if (idx_40 !== -1 && amt_40 === null) amt_40 = commonAmt;
                            if (idx_40h !== -1 && amt_40h === null) amt_40h = commonAmt;
                        }

                        let determinedCategory = null;
                        if (currentSection === "freight_charges") determinedCategory = "BASIC_OCEAN_FREIGHT";
                        else if (currentSection === "surcharges") {
                            const nameLower = name.toLowerCase();
                            if (nameLower.includes("manifest") || nameLower.includes("document fee") || nameLower.includes("documentation fee")) {
                                determinedCategory = "ORIGIN_CHARGE_EXCLUDED";
                            } else {
                                determinedCategory = "FREIGHT_SURCHARGE_INCLUDED";
                            }
                        }
                        else if (currentSection === "export_surcharges") determinedCategory = "ORIGIN_CHARGE_EXCLUDED";
                        else if (currentSection === "import_surcharges") determinedCategory = "DESTINATION_CHARGE_EXCLUDED";

                        if (amt_20 !== null) {
                            results["DRY 20"].push({
                                name: name,
                                amount: amt_20,
                                currency: curr || "USD",
                                category: determinedCategory
                            });
                        }
                        if (amt_40 !== null) {
                            results["DRY 40"].push({
                                name: name,
                                amount: amt_40,
                                currency: curr || "USD",
                                category: determinedCategory
                            });
                        }
                        if (amt_40h !== null) {
                            results["DRY 40H"].push({
                                name: name,
                                amount: amt_40h,
                                currency: curr || "USD",
                                category: determinedCategory
                            });
                        }
                    }
                }
                return results;
            }''')
            
            print(f"[HAPAG] Successfully extracted charges for DRY 20 ({len(charges['DRY 20'])} items), DRY 40 ({len(charges['DRY 40'])} items), DRY 40H ({len(charges['DRY 40H'])} items)")
            
        except Exception as e:
            print(f"[HAPAG] Surcharge details extraction error: {e}")
        finally:
            try:
                print("[HAPAG] Closing Price Breakdown modal...")
                await self.page.keyboard.press("Escape")
                await self._human_delay(400, 700)
                
                close_selectors = [
                    'div[role="dialog"] button i.el-icon-close',
                    'button:has-text("Close")',
                    'div[role="dialog"] button',
                    'span:has-text("Close")',
                    '.el-dialog__headerbtn',
                    '.q-dialog__close',
                    '[aria-label*="close" i]'
                ]
                for sel in close_selectors:
                    try:
                        btn = self.page.locator(sel).first
                        if await btn.is_visible(timeout=300):
                            await btn.scroll_into_view_if_needed()
                            try:
                                await btn.click(timeout=2000)
                            except Exception:
                                await btn.evaluate("el => el.click()")
                            print(f"[HAPAG] Closed modal via selector: {sel}")
                            await self._human_delay(500, 1000)
                            break
                    except:
                        pass
                
                # Bulletproof JS cleanup: hide all dialogs/modals and remove backdrops to ensure no blocking overlay remains
                await self.page.evaluate('''() => {
                    const dialogs = document.querySelectorAll('div[role="dialog"], .el-dialog, .modal, .q-dialog');
                    dialogs.forEach(d => {
                        d.style.display = 'none';
                    });
                    const backdrops = document.querySelectorAll('.v-modal, .q-dialog__backdrop, [class*="backdrop" i], [class*="overlay" i]');
                    backdrops.forEach(b => {
                        b.remove();
                    });
                    document.body.classList.remove('q-body--prevent-scroll', 'el-popup-parent--hidden');
                    document.body.style.overflow = '';
                }''')
                
            except Exception as close_err:
                print(f"[HAPAG] Error closing modal: {close_err}")
                
            await self._human_delay(800, 1500)
            
        return charges

    async def normalize_result(self, raw_quote: dict, raw_charges: list[dict], container_type: str, is_sold_out: bool = False) -> QuoteSchema:
        """
        Normalize raw Hapag-Lloyd quotes into unified QuoteSchema.
        """
        basic_ocean_freight = 0.0
        included_freight_surcharges = []
        excluded_charges = []
        
        from models.schemas import ChargeSchema
        from services.normalizer import classify_and_organize_charges, calculate_final_freight_value
        
        organized = classify_and_organize_charges(raw_charges)
        basic_ocean_freight = organized["basic_ocean_freight"]
        included_freight_surcharges = organized["included_freight_surcharges"]
        excluded_charges = organized["excluded_charges"]
        uncertain_charges = organized["uncertain_charges"]
        
        final_value = calculate_final_freight_value(organized["all_classified"])
        
        # Fallback to total price if no charges breakdown was found
        # (Only do this for the container type that was actually searched/displayed in the departures grid,
        # and only if it is not sold out)
        if is_sold_out or raw_quote.get("is_sold_out"):
            final_value = 0.0
            basic_ocean_freight = 0.0
        else:
            is_searched_type = False
            if hasattr(self, "current_request") and self.current_request:
                req_c_type = self.current_request.container_type
                if req_c_type == container_type:
                    is_searched_type = True
                elif req_c_type == "DRY 20" and container_type == "DRY 20":
                    is_searched_type = True
                elif req_c_type == "DRY 40" and container_type == "DRY 40":
                    is_searched_type = True
                elif req_c_type == "DRY 40H" and container_type == "DRY 40H":
                    is_searched_type = True
                    
            if is_searched_type and final_value == 0.0 and raw_quote.get("total_price"):
                final_value = raw_quote["total_price"]
                if basic_ocean_freight == 0.0:
                    basic_ocean_freight = final_value
            
        vessel = raw_quote.get("vessel", "Hapag Vessel")
        if is_sold_out or raw_quote.get("is_sold_out"):
            vessel = f"{vessel} (Sold out)"

        validity_till = getattr(self, "_last_parsed_validity_till", None)

        return QuoteSchema(
            etd=raw_quote.get("etd"),
            eta=raw_quote.get("eta"),
            transit_time_days=raw_quote.get("transit_time_days"),
            service_name=raw_quote.get("service_name"),
            vessel=vessel,
            currency="USD",
            container_type=container_type,
            basic_ocean_freight=basic_ocean_freight,
            included_freight_surcharges=included_freight_surcharges,
            excluded_charges=excluded_charges,
            uncertain_charges=uncertain_charges,
            final_freight_value=round(final_value, 2),
            source="carrier_portal",
            raw_reference=f"HAPAG-{raw_quote.get('index', 0)}",
            validity_till=validity_till
        )

    async def run_full_search(self, request: RateSearchRequest) -> tuple[CarrierResultStatus, list[QuoteSchema]]:
        if not hasattr(self, "_cached_quotes"):
            self._cached_quotes = None
            self._cached_status = None

        if self._cached_quotes is not None:
            print(f"[HAPAG] Returning cached quotes for '{request.container_type}' (avoiding redundant browser search).")
            matching_quotes = [q for q in self._cached_quotes if q.container_type == request.container_type]
            return self._cached_status, matching_quotes

        quotes: list[QuoteSchema] = []
        
        # Load Freetime Config
        freetime_config = {}
        try:
            import json
            import os
            config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "hapag_freetime.json")
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    freetime_config = json.load(f)
        except Exception as e:
            print(f"[HAPAG] Warning: Could not load freetime config: {e}")

        try:
            # Step 1: Login
            login_ok = await self.login()
            if not login_ok:
                self._cached_quotes = []
                self._cached_status = CarrierResultStatus.LOGIN_FAILED
                return CarrierResultStatus.LOGIN_FAILED, []

            # Step 2: Search Sailing Schedules
            # HAPAG_QUERY_SCHEDULES=false skips the schedule crawl entirely (pricing
            # only, minutes faster). Quotes then use the default vessel fallback the
            # unmatched-schedule path already provides.
            schedules = []
            if os.getenv("HAPAG_QUERY_SCHEDULES", "true").strip().lower() in ("false", "0", "no"):
                print("[HAPAG] HAPAG_QUERY_SCHEDULES=false — skipping schedule crawl (pricing matrix only).")
            else:
                try:
                    schedules = await self.search_sailing_schedules(request)
                except Exception as se:
                    print(f"[HAPAG] Warning: Schedule crawling failed: {se}")

            # Step 3: Transition to Quote Page (always go via New Quote for a fresh form)
            print("[HAPAG] Transitioning to Quote page via New Quote...")
            try:
                await self.page.goto(self.QUOTE_URL)
                try:
                    await self.page.wait_for_load_state("domcontentloaded", timeout=15000)
                except:
                    pass
                await self._human_delay(1500, 2500)

                # Check if Quick Quote form is already visible
                start_input_selector = 'xpath=(//*[contains(text(), "Start Location")])[1]/following::input[1]'
                is_form_visible = False
                try:
                    is_form_visible = await self.page.locator(start_input_selector).first.is_visible(timeout=2000)
                except:
                    pass

                if is_form_visible:
                    print("[HAPAG] Already on New Quote page after navigation. Skipping sidebar clicks.")
                else:
                    print("[HAPAG] Quote form not directly visible. Expanding sidebar menu to click 'New Quote'...")
                    # Expand Quote sidebar and click New Quote
                    quote_sidebar = self.page.locator('span:has-text("Quote"), li:has-text("Quote"), a:has-text("Quote")').first
                    await quote_sidebar.scroll_into_view_if_needed()
                    await quote_sidebar.click(force=True)
                    await self._human_delay(1000, 1800)

                    new_quote_btn = self.page.locator('a:has-text("New Quote"), span:has-text("New Quote")').first
                    await new_quote_btn.scroll_into_view_if_needed()
                    await new_quote_btn.click(force=True)
                    try:
                        await self.page.wait_for_load_state("domcontentloaded", timeout=15000)
                    except:
                        pass
                    await self._human_delay(2000, 3500)
                print("[HAPAG] Transitioned to New Quote page.")
            except Exception as nav_err:
                print(f"[HAPAG] Transition to New Quote failed: {nav_err}")

            await self._human_delay(1000, 2000)
            await self._dismiss_hapag_modals()

            # Step 4: Search quotes
            search_status = await self.search_quotes(request)
            if search_status != CarrierResultStatus.AVAILABLE_QUOTES_FOUND:
                self._cached_quotes = []
                self._cached_status = search_status
                return search_status, []

            # Step 5: Extract quote list
            raw_quotes = await self.extract_quote_list()
            if not raw_quotes:
                self._cached_quotes = []
                self._cached_status = CarrierResultStatus.NO_QUOTES_AVAILABLE
                return CarrierResultStatus.NO_QUOTES_AVAILABLE, []

            # Step 6: For each schedule, map the corresponding quote price
            # Filter out past ETDs (departed sailings produce permanent [NO PRICE MATCH] noise)
            from datetime import date as _date
            today_str = _date.today().isoformat()  # e.g. '2026-06-11'
            future_schedules = [s for s in schedules if s.get("etd", "") >= today_str]
            skipped = len(schedules) - len(future_schedules)
            if skipped:
                print(f"[HAPAG] Skipping {skipped} past-ETD schedule(s) (before {today_str}).")
            schedules = future_schedules

            quotes = []
            matched_raw_quote_etds = set()

            def _apply_freetime_to_quote(normalized):
                if not freetime_config:
                    return
                dest_lower = request.destination.lower()
                expanded_dest = dest_lower
                data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
                try:
                    import json
                    cache_path = os.path.join(data_dir, "carrier_ports_cache.json")
                    if os.path.exists(cache_path):
                        with open(cache_path, "r", encoding="utf-8") as f:
                            cache_data = json.load(f)
                            for carrier, cache_dict in cache_data.items():
                                for key, val in cache_dict.items():
                                    clean_dest = dest_lower.replace(" ", "")
                                    clean_val = str(val).lower().replace(" ", "")
                                    if clean_dest in clean_val:
                                        expanded_dest += f" {str(val).lower()}"
                except Exception:
                    pass
                    
                try:
                    port_codes_path = os.path.join(data_dir, "port_codes.json")
                    country_map_path = os.path.join(data_dir, "country_map.json")
                    if os.path.exists(port_codes_path) and os.path.exists(country_map_path):
                        with open(country_map_path, "r", encoding="utf-8") as f:
                            cmap = json.load(f)
                        with open(port_codes_path, "r", encoding="utf-8") as f:
                            pcodes = json.load(f).get("ports", {})
                            for pcode, pdata in pcodes.items():
                                pname = pdata.get("name", "").lower()
                                clean_dest = dest_lower.replace(" ", "")
                                clean_pname = pname.replace(" ", "")
                                if clean_dest == clean_pname or clean_dest in clean_pname:
                                    ccode = pdata.get("country", "")
                                    cname = cmap.get(ccode, "").lower()
                                    expanded_dest += f" {pname} {ccode.lower()} {cname} {'usa' if ccode == 'US' else ''}"

                            # Robust fallback: resolve the destination to a UN/LOCODE and map
                            # THAT to its country name. Handles destinations given as a bare
                            # locode ("INNSA") or "Nhava Sheva (INNSA) [ZIP: ...]" where the
                            # port-name substring match above does not fire.
                            # Pick the first 5-letter token that is actually a known port
                            # code (so "NHAVA" in the name is skipped in favour of "INNSA").
                            dest_code = None
                            for cand in re.findall(r"[A-Z]{5}", request.destination.upper()):
                                if cand in pcodes:
                                    dest_code = cand
                                    break
                            if not dest_code:
                                try:
                                    resolved = resolve_port_for_carrier(request.destination, "hapag")
                                    if resolved and len(resolved) == 5 and resolved.upper() in pcodes:
                                        dest_code = resolved.upper()
                                except Exception:
                                    pass
                            if dest_code:
                                ccode = pcodes[dest_code].get("country", "")
                                cname = cmap.get(ccode, "").lower()
                                if cname:
                                    expanded_dest += f" {dest_code.lower()} {ccode.lower()} {cname}"
                except Exception as e:
                    print(f"[HAPAG] Port expansion fallback error: {e}")

                for country, ft_data in freetime_config.items():
                    country_clean = country.lower().replace(" ", "")
                    expanded_clean = expanded_dest.replace(" ", "")
                    if country_clean in expanded_clean:
                        c_type = normalized.container_type or request.container_type
                        if "20" in c_type:
                            normalized.free_time = ft_data.get("20GP")
                        elif "40" in c_type:
                            normalized.free_time = ft_data.get("40GP")
                        break

            if schedules:
                for schedule in schedules:
                    try:
                        sched_etd = schedule["etd"]
                        # Find matching raw quote from the Quote page
                        matching_raw_quote = next((q for q in raw_quotes if q["etd"] == sched_etd), None)
                        
                        if matching_raw_quote:
                            matched_raw_quote_etds.add(sched_etd)
                            opened = await self.open_price_breakdown(matching_raw_quote)
                            raw_charges_dict = {}
                            if opened:
                                raw_charges_dict = await self.extract_charge_breakdown()
                                
                            for c_type in ["DRY 20", "DRY 40", "DRY 40H"]:
                                is_sold = False
                                if self._last_parsed_card_prices.get(c_type) == "sold_out":
                                    is_sold = True
                                elif matching_raw_quote.get("is_sold_out"):
                                    is_sold = True
                                
                                c_charges = raw_charges_dict.get(c_type, [])
                                if opened and not c_charges and self._last_parsed_card_prices.get(c_type) and isinstance(self._last_parsed_card_prices[c_type], (int, float)):
                                    c_charges = [{
                                        "name": "Ocean Freight",
                                        "amount": self._last_parsed_card_prices[c_type],
                                        "currency": "USD",
                                        "category": "BASIC_OCEAN_FREIGHT"
                                    }]

                                normalized = await self.normalize_result(matching_raw_quote, c_charges, container_type=c_type, is_sold_out=is_sold)
                                print(f"[HAPAG] [MATCH] Schedule ETD {sched_etd} matched with quote price for {c_type}.")

                                # Step 7: Augment normalized quote with schedule details (vessel, service, eta)
                                vessel_str = schedule["vessel"]
                                if schedule["voyage"]:
                                    vessel_str = f"{vessel_str} (Voyage {schedule['voyage']})"
                                
                                if is_sold or schedule.get("is_sold_out") or matching_raw_quote.get("is_sold_out"):
                                    vessel_str = f"{vessel_str} (Sold out)"
                                    
                                normalized.vessel = vessel_str
                                normalized.routing = schedule.get("routing", "Direct")
                                
                                service_str = schedule["service"]
                                cutoffs = []
                                if schedule["doc_cutoff"]:
                                    cutoffs.append(f"Doc Cut-off: {schedule['doc_cutoff']}")
                                if schedule["fcl_cutoff"]:
                                    cutoffs.append(f"FCL Cut-off: {schedule['fcl_cutoff']}")
                                if cutoffs:
                                    service_str = f"{service_str} ({', '.join(cutoffs)})"
                                normalized.service_name = service_str
                                
                                # Ensure ETD is correctly formatted even if matched from raw_quote
                                normalized.etd = standardize_date_string(sched_etd)
                                
                                if schedule["eta"]:
                                    normalized.eta = standardize_date_string(schedule["eta"])
                                if schedule["transit_time_days"] is not None:
                                    normalized.transit_time_days = schedule["transit_time_days"]
                                    
                                # Apply Freetime
                                _apply_freetime_to_quote(normalized)
                                
                                quotes.append(normalized)
                        else:
                            print(f"[HAPAG] [NO PRICE MATCH] Schedule ETD {sched_etd} has no matching price quote. Emitting schedules without price.")
                            for c_type in ["DRY 20", "DRY 40", "DRY 40H"]:
                                normalized = QuoteSchema(etd=standardize_date_string(sched_etd), container_type=c_type)
                                vessel_str = schedule["vessel"]
                                if schedule["voyage"]:
                                    vessel_str = f"{vessel_str} (Voyage {schedule['voyage']})"
                                normalized.vessel = vessel_str
                                normalized.routing = schedule.get("routing", "Direct")
                                
                                service_str = schedule["service"]
                                cutoffs = []
                                if schedule["doc_cutoff"]:
                                    cutoffs.append(f"Doc Cut-off: {schedule['doc_cutoff']}")
                                if schedule["fcl_cutoff"]:
                                    cutoffs.append(f"FCL Cut-off: {schedule['fcl_cutoff']}")
                                if cutoffs:
                                    service_str = f"{service_str} ({', '.join(cutoffs)})"
                                normalized.service_name = service_str
                                
                                if schedule["eta"]:
                                    normalized.eta = standardize_date_string(schedule["eta"])
                                if schedule["transit_time_days"] is not None:
                                    normalized.transit_time_days = schedule["transit_time_days"]
                                    
                                # Apply Freetime
                                _apply_freetime_to_quote(normalized)
                                
                                quotes.append(normalized)
                    except Exception as e:
                        print(f"[HAPAG] Error processing schedule ETD {schedule.get('etd')}: {e}")
                        continue

                # Add unmatched raw quotes (quotes with no linked schedule)
                for raw_quote in raw_quotes:
                    try:
                        sched_etd = raw_quote["etd"]
                        if sched_etd in matched_raw_quote_etds:
                            continue
                        if sched_etd < today_str:
                            continue
                        
                        print(f"[HAPAG] [UNMATCHED RAW QUOTE] Processing ETD {sched_etd} with default Hapag Vessel /Performa")
                        opened = await self.open_price_breakdown(raw_quote)
                        raw_charges_dict = {}
                        if opened:
                            raw_charges_dict = await self.extract_charge_breakdown()
                            
                        for c_type in ["DRY 20", "DRY 40", "DRY 40H"]:
                            is_sold = False
                            if self._last_parsed_card_prices.get(c_type) == "sold_out":
                                is_sold = True
                            elif raw_quote.get("is_sold_out"):
                                is_sold = True
                                
                            c_charges = raw_charges_dict.get(c_type, [])
                            if opened and not c_charges and self._last_parsed_card_prices.get(c_type) and isinstance(self._last_parsed_card_prices[c_type], (int, float)):
                                c_charges = [{
                                    "name": "Ocean Freight",
                                    "amount": self._last_parsed_card_prices[c_type],
                                    "currency": "USD",
                                    "category": "BASIC_OCEAN_FREIGHT"
                                }]
                            
                            normalized = await self.normalize_result(raw_quote, c_charges, container_type=c_type, is_sold_out=is_sold)
                            normalized.etd = standardize_date_string(sched_etd)
                            normalized.vessel = "Hapag Vessel /Performa"
                            if is_sold:
                                normalized.vessel += " (Sold out)"
                            normalized.service_name = "Hapag Service"
                            normalized.routing = "Direct"
                            normalized.eta = None
                            normalized.transit_time_days = None
                            
                            # Apply Freetime
                            _apply_freetime_to_quote(normalized)
                            
                            quotes.append(normalized)
                    except Exception as e:
                        print(f"[HAPAG] Error processing unmatched raw quote ETD {raw_quote.get('etd')}: {e}")
                        continue
            else:
                print("[HAPAG] Schedules list is empty. Falling back to iterating over raw quotes directly.")
                for raw_quote in raw_quotes:
                    try:
                        sched_etd = raw_quote["etd"]
                        if sched_etd < today_str:
                            continue
                            
                        opened = await self.open_price_breakdown(raw_quote)
                        raw_charges_dict = {}
                        if opened:
                            raw_charges_dict = await self.extract_charge_breakdown()
                            
                        for c_type in ["DRY 20", "DRY 40", "DRY 40H"]:
                            is_sold = False
                            if self._last_parsed_card_prices.get(c_type) == "sold_out":
                                is_sold = True
                            elif raw_quote.get("is_sold_out"):
                                is_sold = True
                                
                            c_charges = raw_charges_dict.get(c_type, [])
                            if not c_charges and self._last_parsed_card_prices.get(c_type) and isinstance(self._last_parsed_card_prices[c_type], (int, float)):
                                c_charges = [{
                                    "name": "Ocean Freight",
                                    "amount": self._last_parsed_card_prices[c_type],
                                    "currency": "USD",
                                    "category": "BASIC_OCEAN_FREIGHT"
                                }]
                                
                            normalized = await self.normalize_result(raw_quote, c_charges, container_type=c_type, is_sold_out=is_sold)
                            normalized.etd = standardize_date_string(sched_etd)
                            normalized.vessel = "Hapag Vessel /Performa"
                            if is_sold:
                                normalized.vessel += " (Sold out)"
                            normalized.service_name = "Hapag Service"
                            normalized.routing = "Direct"
                            normalized.eta = None
                            normalized.transit_time_days = None
                            
                            # Apply Freetime
                            _apply_freetime_to_quote(normalized)
                            
                            quotes.append(normalized)
                    except Exception as e:
                        print(f"[HAPAG] Error processing raw quote ETD {raw_quote.get('etd')}: {e}")
                        continue

            if quotes:
                self._cached_quotes = quotes
                self._cached_status = CarrierResultStatus.AVAILABLE_QUOTES_FOUND
                matching_quotes = [q for q in quotes if q.container_type == request.container_type]
                return CarrierResultStatus.AVAILABLE_QUOTES_FOUND, matching_quotes
            else:
                self._cached_quotes = []
                self._cached_status = CarrierResultStatus.EXTRACTION_FAILED
                return CarrierResultStatus.EXTRACTION_FAILED, []

        except HapagServiceUnavailableException as e:
            print(f"[HAPAG] Hapag-Lloyd service is currently unavailable: {e}")
            self._cached_quotes = []
            self._cached_status = CarrierResultStatus.SERVICE_UNAVAILABLE
            return CarrierResultStatus.SERVICE_UNAVAILABLE, []
        except Exception as e:
            print(f"[HAPAG] Unexpected error in run_full_search: {e}")
            self._cached_quotes = []
            self._cached_status = CarrierResultStatus.UNKNOWN_ERROR
            return CarrierResultStatus.UNKNOWN_ERROR, []
        finally:
            await asyncio.shield(self.close())

    async def close(self):
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.playwright:
                await self.playwright.stop()
        except:
            pass
            
        if self.temp_profile_dir and self.master_profile_dir and self.is_login_successful:
            try:
                print("[HAPAG] Syncing temp profile back to master...")
                # Never copy the throwaway caches back to master — this is the main
                # source of the multi-GB storage bloat and wasted sync I/O.
                shutil.copytree(
                    self.temp_profile_dir, self.master_profile_dir, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns(
                        "Cache", "Code Cache", "DawnCache", "GPUCache", "CacheStorage", "ScriptCache"),
                )
                print("[HAPAG] Master profile updated successfully.")

                # Safety net: remove any stale cache dirs left in master (e.g. from an
                # earlier crashed run). New caches are already excluded by the copy above.
                cache_dirs = ["Cache", "Code Cache", "DawnCache", "GPUCache", "CacheStorage", "ScriptCache"]
                for root_dir, dirs, _ in os.walk(self.master_profile_dir):
                    for d in list(dirs):
                        if d in cache_dirs:
                            try:
                                shutil.rmtree(os.path.join(root_dir, d))
                            except Exception:
                                pass
            except Exception as e:
                print(f"[HAPAG] Warning: master profile sync failed: {e}")
                
        if self.temp_profile_dir and os.path.exists(self.temp_profile_dir):
            try:
                shutil.rmtree(self.temp_profile_dir)
            except:
                pass

