# Graph Report - Infreight_SourcingRates_SG  (2026-10-07)

## Corpus Check
- 230 files · ~1,147,614 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 21 file(s) not represented in the graph (top: (none) 8, .bat 6, .conf 2)

## Summary
- 2201 nodes · 5350 edges · 112 communities (97 shown, 15 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 313 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `645a1732`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- schemas.py
- MockCarrierConnector
- cn
- user_routes.py
- auth_routes.py
- browser_cleanup.py
- RateSearchRequest
- api.ts
- PortManager
- test_self_healing.py
- CMAConnector
- MaerskConnector
- .search_quotes
- NotAvailableConnector
- ._fs_dismiss_modals
- HapagLloydAPIConnector
- preferences.ts
- test_rfq_agent.py
- app/page.tsx
- SocialWidget.tsx
- types.ts
- GreenXConnector
- list_colleagues
- CarrierSearchResult
- backend/main.py
- rate_search_routes.py
- MSCConnector
- parse_rfq
- job_service.py
- AIBrowserAgent
- database.py
- ONEConnector
- _Page
- Engineering Report: Sourcing Portal Enhancements & Scraping Pipeline Stability
- Changelog
- OOCLConnector
- package.json
- LiveSearchProgress.tsx
- RateResults.tsx
- SearchQueueManager
- ChargeCategory
- Frontend Redesign — Componentry Design System, Workspace & Launch Intro (2026-09-07)
- compilerOptions
- asyncio
- test_carrier_timeout.py
- tunnel_client.py
- dithered-logo.tsx
- 👥 The 5 Agent Roles
- HapagLloydConnector
- safe_step.py
- RfqInputSection.tsx
- CurrencyManager
- port_manager.py
- silk-aurora.tsx
- 🚢 Infreight Sourcing & Ocean Rate Automation System
- selector_memory.py
- [2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split
- dependencies
- 🛠 Detailed Carrier Log
- [2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning
- os
- port_routes.py
- post
- [2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup
- devDependencies
- layout.tsx
- GreenX — Surcharge Intake Fix (2026-06-30)
- Admin Page & Port Prioritization Guide
- ._verify_price_owner_selected
- resolve_port_for_carrier
- .login
- MockCard
- deploy
- websockify_carrier_proxy
- tunnel_relay/main.py
- Summary of Changes — July 20, 2026
- create_batch_rate_search
- .search_port
- resolve_port_alias
- test_brightdata.py
- _detect_port_mismatch
- Design system — read before touching any UI
- sort_container_types
- [2026-05-29 – 2026-05-30] — Hapag-Lloyd Full Integration
- [2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control
- [2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash
- scripts
- RateLimiter
- .validate_currency
- ai_repair_agent.py
- [2026-05-20 – 2026-05-22] — Port Resolution & Frontend Improvements
- [2026-05-23 – 2026-05-24] — Maersk Shadow DOM & Stealth Upgrades
- [2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes
- [2026-06-03] — CMA CGM Routing & Free Time Extraction
- [2026-08-04 - 2026-08-06] — CMA CGM Dynamic RAMP/POD Rerouting, Brand Excel Styling, Port Synonym Matching & Tunnel Relays
- cancel_all_active_searches
- frontend/README.md
- test_hapag_schedule.py
- get_me
- Architecture Overview
- [2026-06-02] — Hapag-Lloyd Transshipment & Duplicate Fix
- Working in this repository
- install_pi.sh
- models/__init__.py
- postcss.config.mjs

## God Nodes (most connected - your core abstractions)
1. `RateSearchRequest` - 149 edges
2. `CarrierResultStatus` - 69 edges
3. `cn()` - 69 edges
4. `QuoteSchema` - 67 edges
5. `HapagLloydConnector` - 56 edges
6. `User` - 56 edges
7. `PortManager` - 56 edges
8. `CMAConnector` - 55 edges
9. `BaseCarrierConnector` - 49 edges
10. `MaerskConnector` - 47 edges

## Surprising Connections (you probably didn't know these)
- `4. Ranked recommendations` --references--> `safe_step()`  [INFERRED]
  docs/ROBUSTNESS_REVIEW_2026-07.md → backend/agent/safe_step.py
- `Excel Export — Routing & Free Time Columns Always Empty` --references--> `Quote`  [INFERRED]
  CHANGELOG.md → backend/models/quote.py
- `Hapag-Lloyd — Date String Standardization` --references--> `standardize_date_string()`  [INFERRED]
  CHANGELOG.md → backend/services/normalizer.py
- `2. Bugs found and fixed during the restyle` --references--> `BackendConfigModal()`  [INFERRED]
  FRONTEND_REDESIGN_2026-09-07.md → frontend/src/components/BackendConfigModal.tsx
- `4. Follow-up fixes (`2f9d92b`)` --references--> `PortAutocomplete()`  [INFERRED]
  FRONTEND_REDESIGN_2026-09-07.md → frontend/src/components/PortAutocomplete.tsx

## Import Cycles
- None detected.

## Communities (112 total, 15 thin omitted)

### Community 0 - "schemas.py"
Cohesion: 0.07
Nodes (43): ABC, BaseCarrierConnector, Base Carrier Connector — abstract base class for all carrier connectors. Each…, Extract individual charge line items from the price breakdown. Returns: List of…, Normalize extracted data into a QuoteSchema using the normalizer. Args:…, Detects if a CAPTCHA, Turnstile, hCaptcha, reCAPTCHA, or 2FA screen is…, Abstract base class for carrier portal connectors., Log into the carrier portal. Returns: True if login successful, False otherwise. (+35 more)

### Community 1 - "MockCarrierConnector"
Cohesion: 0.12
Nodes (10): _generate_maersk_mock_quotes(), _generate_msc_mock_quotes(), _generate_one_mock_quotes(), MockCarrierConnector, any, Generate realistic ONE sample quotes with charge breakdowns., Generate realistic MSC sample quotes with validity_till., Generate realistic Maersk sample quotes with charge breakdowns. (+2 more)

### Community 2 - "cn"
Cohesion: 0.07
Nodes (54): Reuse the primitives, New primitives — `frontend/src/components/ui/`, AppHeader(), AppHeaderProps, initials(), BatchProgressPanel(), BatchProgressPanelProps, cheapest() (+46 more)

### Community 3 - "user_routes.py"
Cohesion: 0.08
Nodes (71): get_current_user(), Dependency that strictly requires an authenticated active member., admin_delete_user(), AdminLoginRequest, approve_user(), CarrierOverrideRequest, Config, create_custom_port_endpoint() (+63 more)

### Community 4 - "auth_routes.py"
Cohesion: 0.06
Nodes (71): clear_session_cookie(), get_current_user_optional(), login(), LoginRequest, logout(), AsyncSession, BaseModel, post (+63 more)

### Community 5 - "browser_cleanup.py"
Cohesion: 0.11
Nodes (33): _is_chrome(), _is_playwright_driver(), _kill(), kill_profile_browsers(), _proc_supported(), profile_base_dirs(), Cleanup for Chrome browsers and temporary profiles that a failed close leaves…, Kill every automated Chrome and Playwright driver. Only call this when no… (+25 more)

### Community 6 - "RateSearchRequest"
Cohesion: 0.08
Nodes (25): RateSearchRequest, CMA CGM end-to-end test — login + search + extract quotes., # IMPORTANT: Clear ALL proxy env vars BEFORE any import triggers load_dotenv()…, test_cma(), run_test(), run_test(), CMA CGM Montreal Ramp selection test. Verifies that when…, test_montreal_ramp() (+17 more)

### Community 7 - "api.ts"
Cohesion: 0.09
Nodes (52): AdminDashboard(), UserRecord, LoginContent(), BackendConfigModal(), BackendConfigModalProps, LoginModal(), LoginModalProps, addCarrierOverride() (+44 more)

### Community 8 - "PortManager"
Cohesion: 0.11
Nodes (7): PortManager, Suggest top N ports for a partial query., Retrieve verified carrier port name from persistent cache by UN/LOCODE,…, Cache verified carrier port name and save persistently to…, Clean and normalize user input for port searching., Retrieve port data by full UN/LOCODE (e.g., 'SGSIN')., Dynamic Carrier Port Overrides & Admin Registry (`PortManager`, `AdminDashboard.tsx`)

### Community 9 - "test_self_healing.py"
Cohesion: 0.16
Nodes (16): handle_chat_query(), _local_chatbot_fallback(), Intelligent responder for search status, carrier guidance, air/sea info, and…, Sends the chat message and history to native Gemini 2.5 Flash API. If Gemini…, detect_manual_action_required(), Manual Action Detector — identifies pages requiring human verification (2FA,…, Scans the current Playwright page to see if a CAPTCHA, Cloudflare challenge,…, clean_selector_memory() (+8 more)

### Community 10 - "CMAConnector"
Cohesion: 0.08
Nodes (18): CMAConnector, Ensures 'Ramp' is explicitly selected under 'Type of location' toggle buttons…, Scans for Route, POL (Port of Loading), or POD (Port of Discharge) dropdown…, Clears the currently selected Destination port tag/card, re-types the locode,…, Dynamically extracts any recommended 5-letter POD LOCODE mentioned in the…, Detects if CMA CGM displayed an advisory banner message: "Looking for AEJEA or…, Handles the 'Customer account' -> 'Role (you are acting as)' dropdown on CMA…, Repeatedly clicks 'More results' if visible to load ALL quotes on the page. (+10 more)

### Community 11 - "MaerskConnector"
Cohesion: 0.06
Nodes (25): MaerskConnector, flatten_tree(), Execute the full search flow with Progressive Lazy Loading: 1. Login 2. Search…, Extracts freetime, demurrage, and detention from the 'Import D&D fees' tab…, Extracts the routing details from the 'Route & other details' accordion.…, Splits a single raw multi-container quote card into multiple QuoteSchema…, Extracts the port/city name by removing any UN/LOCODE parentheses (e.g.,…, Hapag-Lloyd form inspector. (+17 more)

### Community 12 - ".search_quotes"
Cohesion: 0.15
Nodes (9): extract_locode_and_country(), prepare_maersk_query(), Extracts LOCODE and country name from text like 'CASABLANCA, MOROCCO (MACAS)'…, Maps standard container search codes (e.g. 'DRY 20', '20GP') to Maersk Spot…, Scores a Maersk autocomplete dropdown suggestion. NOTE: The nested/indented…, Fills an autocomplete field using the proven original element-level…, get_cached_carrier_port(), get_carrier_overrides() (+1 more)

### Community 13 - "NotAvailableConnector"
Cohesion: 0.06
Nodes (25): NotAvailableConnector, Any, Clean up browser resources robustly, ensuring failures or hangs never block…, Best-effort ETD date from a raw card dict (ISO, MM/DD/YYYY)., The card's summary price. NOTE: on multi-container cards this is the SUM across…, Picks the cheapest card in EACH tariff window the customer RFQ sheet needs:…, Calls the connector's per-container splitter whether it is sync or async…, Quick-mode quote builder shared by every connector and both search paths. Fixes… (+17 more)

### Community 14 - "._fs_dismiss_modals"
Cohesion: 0.06
Nodes (26): clean_vessel_name(), _dismiss_once(), _click_date_strip_item(), _open_calendar(), _parse_date(), Lock, Parses one FreightSmart result card's inner text into a raw row dict. Text-…, Opens the Details dialog for a card, clicks the Charge Breakdown tab, extracts… (+18 more)

### Community 15 - "HapagLloydAPIConnector"
Cohesion: 0.07
Nodes (20): HapagLloydAPIConnector, Any, AsyncClient, Direct REST API connector for Hapag-Lloyd Prices API v2.1.4., API connectors do not require browser login sessions., No browser session to reset between batch routes., Resolves a free-text port name or string (e.g. 'Singapore', 'Hamburg, Germany…, Hapag-Lloyd Prices API requires earliestDepartureDate to be at least 4 calendar… (+12 more)

### Community 16 - "preferences.ts"
Cohesion: 0.09
Nodes (33): LaunchIntro(), SearchHistoryItem, derive(), Derived, startOfDay(), UsageStats(), ChoiceCard(), Toggle() (+25 more)

### Community 17 - "test_rfq_agent.py"
Cohesion: 0.10
Nodes (36): API routes for RFQ parsing agent., RFQParseResult, asyncio, Unit tests for the Gemini AI RFQ Agent service (parse_rfq). Includes…, Test Image 2: Air rate request generates 3 drafts to Glenn (AWOT), Jing Hui…, Test Image 4: Steel Plate ex Pasir Gudang / Tanjung Pelepas for 20' & 40'., Test Guardrail: Detects Reefer container request and returns unsupported_cargo…, Test Guardrail: Detects LCL request. (+28 more)

### Community 18 - "app/page.tsx"
Cohesion: 0.12
Nodes (33): HomeContent(), ChatWidget(), ChatWidgetProps, Message, LiveSearchProgressProps, RateResultsProps, ResultsTable(), ResultsTableProps (+25 more)

### Community 19 - "SocialWidget.tsx"
Cohesion: 0.10
Nodes (34): ACCENT_COLORS, errorMessage(), relativeTime(), resizeImageToDataUrl(), SocialWidget(), SocialWidgetProps, EMOJI_GROUPS, EmojiPicker() (+26 more)

### Community 20 - "types.ts"
Cohesion: 0.12
Nodes (30): 0. The one invariant, CarrierMultiSelect(), CarrierMultiSelectProps, isAllCarriers(), toggleAllCarriers(), toggleCarrierSelection(), PortAutocomplete(), PortAutocompleteProps (+22 more)

### Community 21 - "GreenXConnector"
Cohesion: 0.11
Nodes (9): GreenXConnector, date, Overrides base search runner to query all 3 sizes at once and cache the…, Type a LOCODE into the autocomplete field and click the first visible dropdown…, Find quantity input next to or below label_text and fill it., Find the exact individual quote card container row encompassing dates, rates,…, Dismiss any cookie/alert modal that would intercept pointer events., Splits a single raw multi-container quote card into multiple QuoteSchema… (+1 more)

### Community 22 - "list_colleagues"
Cohesion: 0.11
Nodes (23): get_conversation(), list_colleagues(), poke_colleague(), PokeRequest, AsyncSession, BaseModel, delete, get (+15 more)

### Community 23 - "CarrierSearchResult"
Cohesion: 0.15
Nodes (22): get_recent_search_status_context(), Queries the database for the most recent rate search status to give the chatbot…, Updates the status of a carrier search in the database., update_carrier_status(), _create_sqlite_engine(), get_async_session_maker(), init_db(), Get the session maker for use outside of FastAPI dependency injection. (+14 more)

### Community 24 - "backend/main.py"
Cohesion: 0.13
Nodes (16): health(), lifespan(), get, Infreight Ocean Carrier Rate Automation — FastAPI Application. Main entry point…, Check if the VNC viewer is available (production only, where Xvfb runs)., Startup and shutdown events., vnc_status(), cleanup_old_debug_files() (+8 more)

### Community 25 - "rate_search_routes.py"
Cohesion: 0.10
Nodes (32): get_admin_analytics_endpoint(), get_batch_search_status(), get_rate_search(), get_repair_reports(), get_route_health(), get_user_search_history(), AsyncSession, get (+24 more)

### Community 26 - "MSCConnector"
Cohesion: 0.10
Nodes (15): format_to_iso_date(), MSCConnector, parse_msc_modal_charges(), Playwright-based automation for MSC (Mediterranean Shipping Company)., Handles the MSC login flow., Clicks Instant Quote, fills form, clicks Search., Parses charges from MSC BreakdownModal text. Correctly includes charges whose…, Detects and clicks the 'Ramp' delivery/haulage option if MSC displays Ramp /… (+7 more)

### Community 27 - "parse_rfq"
Cohesion: 0.12
Nodes (27): parse_rfq_endpoint(), post, Parse a free-text RFQ email or message into a structured RateSearchRequest…, _call_native_gemini_api(), _detect_booking_confirmation(), _detect_dual_mode_enquiry(), _detect_mode_by_hierarchy(), _detect_unsupported_cargo() (+19 more)

### Community 28 - "job_service.py"
Cohesion: 0.13
Nodes (22): get_connector(), Get the appropriate connector for a carrier. If USE_MOCK_CARRIERS=true: returns…, SearchStatus, cleanup_browsers_if_idle(), UUID, Job Service — orchestrates carrier search jobs. Creates background tasks per…, Run one container-size search, stopping it early if the browser tab crashes or…, Check all carrier results and update the overall search status. (+14 more)

### Community 29 - "AIBrowserAgent"
Cohesion: 0.12
Nodes (16): AIBrowserAgent, Capture the current page as a PNG screenshot., Build the prompt with task description and action history., Parse Gemini's response into an action dict., Call Gemini API with exponential backoff retry., Execute a parsed action on the browser page., Detect if the agent is stuck repeating the same action., Find all visible interactive elements and format them as a prompt guide. (+8 more)

### Community 30 - "database.py"
Cohesion: 0.08
Nodes (40): Chat Service — manages conversational AI queries from the frontend user using…, get_sync_url(), run_migrations_offline(), run_migrations_online(), Base, _get_database_url(), _get_engine(), get_session() (+32 more)

### Community 31 - "ONEConnector"
Cohesion: 0.07
Nodes (14): ONEConnector, _classify(), fill_container_card(), date, Parses ONE QUOTE Free Time popover text for DESTINATION ONLY. Ignores Origin…, Splits a single raw multi-container quote card into multiple QuoteSchema…, Tries to click a matching option from ONE's visible dropdown. Returns True only…, Extracts 5-letter UN/LOCODE from strings like 'Singapore [SGSIN]' or 'Singapore… (+6 more)

### Community 32 - "_Page"
Cohesion: 0.15
Nodes (8): _connector(), _Locator, _Page, Maersk's login page redirects to the Hub a few seconds after loading when the…, Sits on /portaluser/login, then redirects after `redirect_after` URL reads., test_login_uses_saved_session_after_late_redirect(), test_wait_detects_late_redirect(), test_wait_detects_login_form()

### Community 33 - "Engineering Report: Sourcing Portal Enhancements & Scraping Pipeline Stability"
Cohesion: 0.08
Nodes (23): 1. Anti-Bot Mitigation & CAPTCHA Human-in-the-Loop Recovery, 2. Sourcing Parallelization & Surcharges Optimization, 3. Autocomplete Intelligence & Location Mapping, 4. Scraper Pipeline Maintenance, 5. Infrastructure & DevSecOps Enhancements, Business Value, Business Value, Business Value (+15 more)

### Community 34 - "Changelog"
Cohesion: 0.09
Nodes (22): [2026-05-18 – 2026-05-19] — Railway Deployment & Docker, [2026-05-25 – 2026-05-26] — VNC Display Isolation & Proxy Integration, [2026-05-31] — Multi-Instance Support & Charge Classification, [2026-06-01] — Hapag-Lloyd Sold Out Detection & Date Parsing, [2026-07-08] — OOCL E-Quote Calendar Navigation, cheapest E-Spot selection, and E-Quote/E-Spot isolation refinements, [2026-07-09] — Hapag-Lloyd Quick Quotes pairing and selection simplification, [2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History, Admin User Search History & SGT GMT+8 Conversion (`AdminDashboard.tsx`) (+14 more)

### Community 35 - "OOCLConnector"
Cohesion: 0.10
Nodes (11): OOCLConnector, parse_oocl_date(), Serves one container-type cycle from the cached merged quote set: -…, One crawl serves all container-type cycles (cached), combining: 1. Sailing…, Attempts to automatically click the Cloudflare Turnstile 'Verify you are human'…, Public oocl.com Chromium sailing schedule crawl bypassed per directive. All…, main(), main() (+3 more)

### Community 36 - "package.json"
Cohesion: 0.10
Nodes (19): eslintConfig, nextConfig, engines, node, name, packageManager, private, version (+11 more)

### Community 37 - "LiveSearchProgress.tsx"
Cohesion: 0.14
Nodes (18): ACTION_STATUSES, ChipModel, describe(), EMPTY_STATUSES, formatElapsed(), LiveSearchProgress(), parseServerTime(), Phase (+10 more)

### Community 38 - "RateResults.tsx"
Cohesion: 0.17
Nodes (17): QuoteBreakdownDrawer(), QuoteBreakdownDrawerProps, Breakdown(), ChargeList(), dateValue(), freeTimeText(), isSoldOut(), isSpot() (+9 more)

### Community 39 - "SearchQueueManager"
Cohesion: 0.12
Nodes (11): Lock, Marks a search as completed internally so we can track the auto-release timeout., Called periodically in a background task to check if the user has held the lock…, Forcefully clears all queued searches and the active lock. Useful for…, Returns or creates an asyncio.Lock for a specific carrier code to prevent…, Adds a search to the queue and waits until it becomes the active search. Event-…, Singleton manager to enforce a FIFO queue for rate searches. Since web scraping…, Returns the current position of the search in the queue. 0 means it is the… (+3 more)

### Community 40 - "ChargeCategory"
Cohesion: 0.07
Nodes (50): ChargeCategory, classify_charge(), is_weight_surcharge_applicable(), Charge Classifier — rule-based classification of freight charge line items.…, Classify a charge line item based on its name, amount, section heading, and…, Evaluates whether a weight-tier or overweight surcharge is applicable for the…, calculate_final_freight_value(), classify_and_organize_charges() (+42 more)

### Community 41 - "Frontend Redesign — Componentry Design System, Workspace & Launch Intro (2026-09-07)"
Cohesion: 0.11
Nodes (17): 1. Design system foundation (`082b43a`), 2. Bugs found and fixed during the restyle, 3. Workspace + launch intro (`21ade75`), 4. Follow-up fixes (`2f9d92b`), 5. Verification, 6. Known limitations / candidate follow-ups, 7. Conventions to follow from here, Dependencies added (5, all small, no runtime lib dependency on Componentry) (+9 more)

### Community 42 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 43 - "asyncio"
Cohesion: 0.07
Nodes (29): asyncio, # NOTE: No start date fill needed — schedule page defaults to today,, Hapag-Lloyd Live Connector -- Playwright automation. Credentials read from env:…, AI Browser Agent — Vision-based browser automation using Gemini Flash. This…, Interactive Headed Login Helper for Maersk. Opens real Chrome using the…, Interactive Headed Login Helper for ONE (Ocean Network Express). Opens Chrome…, Wrapper script to set Windows event loop policy before starting Uvicorn. This…, parse_hapag_pdf() (+21 more)

### Community 44 - "test_carrier_timeout.py"
Cohesion: 0.19
Nodes (10): CrashingConnector, HangingConnector, asyncio, A carrier whose browser hangs must be stopped after CARRIER_SEARCH_TIMEOUT_SEC…, Hangs on the sizes in `hang_on`; answers NO_QUOTES_AVAILABLE for the rest., Like a real connector whose tab dies: reports a crash, then never returns., _run(), test_crashed_tab_stops_the_carrier_without_waiting_for_the_timeout() (+2 more)

### Community 45 - "tunnel_client.py"
Cohesion: 0.17
Nodes (11): ambiguous_python_import_b35980c0aa01, argparse, asyncio, Integration tests for authentication, legacy user password setup, pending…, test_full_auth_lifecycle(), httpx, pytest_asyncio, handle_request() (+3 more)

### Community 46 - "dithered-logo.tsx"
Cohesion: 0.19
Nodes (15): applyMaskInversion(), buildRoundedMask(), DEFAULTS, DitherConfig, DitheredLogo(), DitheredLogoProps, drawParticles(), errorDiffusionDither() (+7 more)

### Community 47 - "👥 The 5 Agent Roles"
Cohesion: 0.13
Nodes (14): 1. Intake Agent (Email Listener), 2. Sourcing Orchestrator (The Coordinator), 3. Sourcing & Scraping Agent (Rates Engine), 4. Finance & Costing Agent (Excel Compiler), 5. Email Draft Agent (Communicator), 📋 Executive Summary, 🛠️ Implementation Stages, Phase 1: Email Integration (Week 1-2) (+6 more)

### Community 48 - "HapagLloydConnector"
Cohesion: 0.05
Nodes (40): HapagLloydConnector, _apply_freetime_to_quote(), HapagServiceUnavailableException, Exception, Normalize various date formats (e.g. 2026-05-31, 31.05.2026, 31 May 2026, 31…, Robustly selects options from Hapag-Lloyd custom dropdown lists. Types the…, Detects the Microsoft B2C identity/OAuth login page. Hapag can silently bounce…, Guards against the session-expiry-mid-crawl failure mode: the existing redirect… (+32 more)

### Community 49 - "safe_step.py"
Cohesion: 0.14
Nodes (15): capture_failure_context(), Exception, Failure Detector — parses and structures error context from failed Playwright…, Assembles a standardized diagnostic dictionary containing all available details…, capture_page_state(), Page Observer — captures page state (screenshot, DOM, visible text) on failure., Captures screenshot, DOM HTML, and inner text of the current page. Saves…, generate_report() (+7 more)

### Community 50 - "RfqInputSection.tsx"
Cohesion: 0.21
Nodes (11): RateSearchFormProps, DEMO_EXAMPLES, RfqInputSectionProps, Box(), fieldName(), laneFlags(), RfqLane, RfqWorkspace() (+3 more)

### Community 51 - "CurrencyManager"
Cohesion: 0.23
Nodes (7): convert_currency_to_usd(), CurrencyManager, get_all_exchange_rates(), Any, Currency Exchange Rate Service — manages currency conversions and custom…, update_exchange_rate(), threading

### Community 52 - "port_manager.py"
Cohesion: 0.32
Nodes (10): add_carrier_override(), add_custom_port(), delete_carrier_override(), delete_custom_port(), get_custom_ports(), get_popular_ports_config(), search_port(), update_popular_ports_config() (+2 more)

### Community 53 - "silk-aurora.tsx"
Cohesion: 0.19
Nodes (9): hexToRgb01(), sanitizeHexColor(), SilkAurora(), SilkAuroraProps, WebGLErrorBoundary, WebGLErrorBoundaryProps, WebGLErrorBoundaryState, WebGLFallback() (+1 more)

### Community 54 - "🚢 Infreight Sourcing & Ocean Rate Automation System"
Cohesion: 0.14
Nodes (13): 1. Multi-Carrier Automation Engine, 2. Intelligent Surcharge & Charge Classifier Engine (`charge_classifier.py`), 3. Container Comparison Matrix & Excel Export Engine, 🚢 Infreight Sourcing & Ocean Rate Automation System, 🌟 Key Capabilities, 📄 License & Confidentiality, Prerequisites, 🛠️ Project Structure (+5 more)

### Community 55 - "selector_memory.py"
Cohesion: 0.24
Nodes (12): get_approved_selector(), _load_memory(), Selector Memory — stores and retrieves human-approved selector patches., Loads memory JSON file. Returns empty dict if file is missing or invalid., Saves memory dict back to JSON file., Looks up if there is an approved replacement selector for the given carrier and…, Stores an approved replacement selector., Marks any proposed selector for this step as REJECTED. (+4 more)

### Community 56 - "[2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split"
Cohesion: 0.15
Nodes (13): G2 Stress Test: "Hi, Please book the below as per your quote ref INF-2026-0842:…, H1 Stress Test: Table with 2 distinct rows: Row 1: POL Singapore, POD Jakarta,…, test_g2_booking_confirmation_guardrail(), test_h1_table_deduplication_two_pairs(), [2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split, Booking Confirmation / Instructions Intercept Guardrail G2 (`rfq_agent.py` & `RfqInputSection.tsx`), Commercial Sales Desk Intelligence (`sales_notes`), Deterministic Port Alias Resolver (`ports_aliases.json`) (+5 more)

### Community 57 - "dependencies"
Cohesion: 0.15
Nodes (13): dependencies, class-variance-authority, clsx, exceljs, lucide-react, next, next-themes, @radix-ui/react-slot (+5 more)

### Community 58 - "🛠 Detailed Carrier Log"
Cohesion: 0.15
Nodes (12): 🛠 Detailed Carrier Log, 🟢 GreenX, 🟠 Hapag-Lloyd, Infreight Ocean Carrier Rate Automation — Development Log, 🚀 Key Highlights & Architectural Changes, 🔌 Local Laptop Deployment (Self-Hosted Worker), 🔵 Maersk, 💗 ONE (Ocean Network Express) (+4 more)

### Community 59 - "[2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning"
Cohesion: 0.17
Nodes (10): get_booking_start_date(), date, Applies the business rules and pairs FreightSmart prices with crawled…, [2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning, GreenX — "No Quotes" Reported While Quotes Visibly Loaded in VNC, Hapag-Lloyd — Configurable Pacing & Redundant-Wait Removal, Job Scheduler — Concurrency Default, Maersk — Regression: Other-Container-Type Sizes Went "Sold Out" in Multi-Container Searches (+2 more)

### Community 60 - "os"
Cohesion: 0.06
Nodes (19): GreenX (Evergreen) Live Connector - Playwright automation., dump_options(), main(), Diagnostic: dump ALL dropdown options (text + innerHTML) when typing 'DEHAM'…, check_and_wait_for_captcha(), login(), main(), Script to test Playwright browser launching using your REAL Google Chrome… (+11 more)

### Community 61 - "port_routes.py"
Cohesion: 0.16
Nodes (14): get_countries(), get_port(), get_suggestions(), get, Get list of countries for autocomplete dropdown., Get specific port details by UN/LOCODE., Get port suggestions for autocomplete., search() (+6 more)

### Community 62 - "post"
Cohesion: 0.22
Nodes (11): approve_repair(), ApproveRepairRequest, chat_endpoint(), ChatRequest, BaseModel, post, Chatbot helper endpoint powered by Gemini API., Approves a suggested AI selector fix and saves it to memory. (+3 more)

### Community 63 - "[2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup"
Cohesion: 0.22
Nodes (8): [2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup, Chromium Cache Auto-Cleanup (Railway Storage Bloat Prevention), CMA CGM — 30-Second Timeout on Sold Out Cards, CMA CGM — Free Time Regex Too Strict, CMA CGM — Routing Regex Not Matching "via LEKKI, LA, NG", Excel Export — Routing & Free Time Columns Always Empty, Excel Export — Sold Out Rows Not Showing, Maersk — Hardcoded Port Overrides

### Community 64 - "devDependencies"
Cohesion: 0.22
Nodes (9): devDependencies, eslint, eslint-config-next, tailwindcss, @tailwindcss/postcss, @types/node, @types/react, @types/react-dom (+1 more)

### Community 65 - "layout.tsx"
Cohesion: 0.25
Nodes (6): frontend_src_app_globals, instrumentSans, inter, metadata, viewport, ThemeProvider()

### Community 66 - "GreenX — Surcharge Intake Fix (2026-06-30)"
Cohesion: 0.22
Nodes (8): Charges that must be taken into the final value (USD only), Files changed, Fix, GreenX — Surcharge Intake Fix (2026-06-30), Per-B/L charges (billed once per booking, added in full to *each* container type), Problem, Root cause, Verification

### Community 67 - "Admin Page & Port Prioritization Guide"
Cohesion: 0.25
Nodes (7): 1. Popular Ports (UN/LOCODEs), 2. Boosted Countries, Admin Page & Port Prioritization Guide, 🔒 How to Access the Admin Page, ⚙️ How to Use Port Prioritization, ⚡ Important Notes, 📝 Step-by-Step Example

### Community 68 - "._verify_price_owner_selected"
Cohesion: 0.25
Nodes (7): Verifies the "I am the price owner" radio is genuinely checked, piercing shadow…, [2026-07-03] — OOCL FreightSmart Autoclear, Hapag Price Leak & Redirect fixes, Maersk Cache Scoping, Dallas Overrides, Hapag-Lloyd — Price Leaks, Column Matching, and Redirect Recovery, Maersk — 0.0-USD / "Not Open" Card Flakiness (the "Quotes Found but Empty Excel" root causes), Maersk — Caching Scope & Selector Tuning, OOCL — FreightSmart Popup Dismissals & Input Lock Serialization, Ports — Hardcoded Dallas Override

### Community 69 - "resolve_port_for_carrier"
Cohesion: 0.24
Nodes (9): Resolves input text (e.g. 'Belfast (GBBEL)' or 'GBBEL') to a tuple of…, resolve_msc_port(), Resolves input text to (location_name, locode, country_code, country_name)., resolve_oocl_port_info(), resolve_port_for_carrier(), Verify non-Maersk carriers get standard UN/LOCODE or default mappings., Verify that El Dekheila maps specifically to 'Alexandria Dekheila, Egypt' for…, test_el_dekheila_maersk_override() (+1 more)

### Community 70 - ".login"
Cohesion: 0.20
Nodes (6): _is_logged_in_url(), True once Maersk has moved past the login pages to a signed-in page., Types text character by character into a given locator or element handle with…, Clicks an element with pre-click and post-click human-like reaction pauses., Wait until the login page either redirects to a signed-in page or shows its…, test_logged_in_url()

### Community 72 - "deploy"
Cohesion: 0.25
Nodes (7): build, builder, deploy, restartPolicyMaxRetries, restartPolicyType, startCommand, $schema

### Community 73 - "websockify_carrier_proxy"
Cohesion: 0.22
Nodes (5): websocket, Proxy WebSocket connections to legacy local x11vnc at localhost:5900., Proxy WebSocket connections to specific carrier x11vnc servers., websockify_carrier_proxy(), websockify_proxy()

### Community 74 - "tunnel_relay/main.py"
Cohesion: 0.25
Nodes (8): api_route, fastapi_middleware_cors, health(), get, Request, websocket, relay_request(), websocket_endpoint()

### Community 75 - "Summary of Changes — July 20, 2026"
Cohesion: 0.29
Nodes (6): 1. AI RFQ Front Door & Air Freight Support (Phase A), 2. Multi-Origin & Gappy List Parsing for Sea RFQs (Phase B), 3. Search Form Streamlining (Form Input Restrictions), 4. Native Gemini 2.5 Flash API & Chatbot Resiliency, 5. Verification & Test Suite, Summary of Changes — July 20, 2026

### Community 76 - "create_batch_rate_search"
Cohesion: 0.33
Nodes (9): create_batch_rate_search(), _contains(), _looks_like(), _norm(), _resolve(), create_rate_search(), Execute a multi-route RFQ batch using Vertical Parallel Persistent Sessions.…, Create a new rate search and dispatch carrier jobs. (+1 more)

### Community 78 - "resolve_port_alias"
Cohesion: 0.33
Nodes (6): _load_port_aliases_config(), Deterministically resolves a port string against ports_aliases.json and the…, resolve_port_alias(), Test that resolve_port_alias cleans 'City, Country' and parenthetical notes to…, test_resolve_city_country_format_to_clean_database_port_name(), Clean Search Dropdown Port Name Resolution (`rfq_agent.py` & `port_manager.py`)

### Community 79 - "test_brightdata.py"
Cohesion: 0.40
Nodes (5): get_title(), Script to test fetching CMA CGM pricing page using Bright Data Web Access HTTP…, test_brightdata_api(), urllib_error, urllib_request

### Community 80 - "_detect_port_mismatch"
Cohesion: 0.22
Nodes (8): _detect_port_mismatch(), Detects port mismatch for origin or destination. Returns: - True if verified…, Test that matching LOCODE or City + Country code returns False (Verified Match)., Test that differing port strings return True (Verified Mismatch)., Test that null/empty matched port strings return None (Unknown / Could Not…, test_detect_port_mismatch_unknown_null(), test_detect_port_mismatch_verified_match(), test_detect_port_mismatch_verified_mismatch()

### Community 81 - "Design system — read before touching any UI"
Cohesion: 0.33
Nodes (5): Animation rules, Client-only preferences, Design system — read before touching any UI, This is NOT the Next.js you know, Use tokens, not raw colours

### Community 82 - "sort_container_types"
Cohesion: 0.40
Nodes (4): Sort container types in standard order: DRY 20 (20GP) -> DRY 40 (40GP) -> DRY…, sort_container_types(), test_container_types_standard_ordering(), model_validator

### Community 83 - "[2026-05-29 – 2026-05-30] — Hapag-Lloyd Full Integration"
Cohesion: 0.40
Nodes (5): [2026-05-29 – 2026-05-30] — Hapag-Lloyd Full Integration, Hapag-Lloyd — Dropdown Autocomplete Issues, Hapag-Lloyd — Live Connector Implementation, Hapag-Lloyd — Onboarding Modal Blocking Form Interaction, Hapag-Lloyd — Search Button Selector Failures

### Community 84 - "[2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control"
Cohesion: 0.40
Nodes (5): [2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control, Concurrency Limit Queue & Admin Control Panel, MSC — Mediterranean Shipping Company Connector Implementation, ONE — Inbound Free Time Swap & Scraper Upgrade, OOCL — Orient Overseas Container Line Connector Implementation

### Community 85 - "[2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash"
Cohesion: 0.40
Nodes (5): [2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash, AI RFQ Front Door & Air Freight Support, Multi-Origin & Gappy List Parsing (Sea RFQs), Native Gemini 2.5 Flash Direct API Integration, Search Form Streamlining

### Community 86 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, dev, lint, start

### Community 89 - "ai_repair_agent.py"
Cohesion: 0.29
Nodes (7): _local_fuzzy_repair(), AI Repair Agent — diagnoses Playwright step failures and suggests selector…, A local rule-based heuristic to locate reasonable buttons or inputs when Gemini…, Analyzes the failure context and DOM content to suggest a selector repair. Uses…, suggest_fix(), test_ai_repair_agent_offline_fallback(), bs4

### Community 90 - "[2026-05-20 – 2026-05-22] — Port Resolution & Frontend Improvements"
Cohesion: 0.50
Nodes (4): [2026-05-20 – 2026-05-22] — Port Resolution & Frontend Improvements, Excel Export — ETA Column & Container Type Header, Frontend Light Mode & CORS Fix, Port Resolution System

### Community 91 - "[2026-05-23 – 2026-05-24] — Maersk Shadow DOM & Stealth Upgrades"
Cohesion: 0.50
Nodes (4): [2026-05-23 – 2026-05-24] — Maersk Shadow DOM & Stealth Upgrades, Maersk — 2FA/CAPTCHA Human-in-the-Loop via noVNC, Maersk — Login Credential Autofill Corruption, Maersk — Shadow DOM Piercing for MDS Web Components

### Community 92 - "[2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes"
Cohesion: 0.50
Nodes (4): [2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes, CMA CGM — Chrome Profile Bypass, ONE — Date Formatting & Charge Breakdown Pollution, ONE — Date Picker Pre-selection Issue

### Community 93 - "[2026-06-03] — CMA CGM Routing & Free Time Extraction"
Cohesion: 0.50
Nodes (4): [2026-06-03] — CMA CGM Routing & Free Time Extraction, CMA CGM — Import Free Time from D&D Tab, CMA CGM — Routing Detection (Direct vs Transit), Maersk — Free Time Extraction from Card Text

### Community 94 - "[2026-08-04 - 2026-08-06] — CMA CGM Dynamic RAMP/POD Rerouting, Brand Excel Styling, Port Synonym Matching & Tunnel Relays"
Cohesion: 0.50
Nodes (4): [2026-08-04 - 2026-08-06] — CMA CGM Dynamic RAMP/POD Rerouting, Brand Excel Styling, Port Synonym Matching & Tunnel Relays, Brand-Aligned Excel Export Styling (`excel_export.py`), CMA CGM Dynamic RAMP / POD Advisory Banner Detection (`cma_connector.py`), Railway WebSocket Tunnel Relay & Failover (`tunnel_client.py`, `run_tunnel_client.bat`, `FailoverFetch`)

### Community 95 - "cancel_all_active_searches"
Cohesion: 0.33
Nodes (6): force_stop_searches(), Forcefully clears the queue and cancels all active search tasks., close_all_active_connectors(), Force close all active carrier connectors and their Playwright Chrome windows., cancel_all_active_searches(), Cancel all active single & vertical batch search tasks and force close browsers.

### Community 96 - "frontend/README.md"
Cohesion: 0.50
Nodes (3): Deploy on Vercel, Getting Started, Learn More

### Community 97 - "test_hapag_schedule.py"
Cohesion: 0.50
Nodes (4): parse_hapag_card_text_mock(), Verify that multi-leg/feeder routes take the final arrival ETA and 28 days TT., Mock implementation of the JS evaluate logic inside hapag_lloyd_connector.py., test_hapag_multi_leg_schedule_extraction()

### Community 98 - "get_me"
Cohesion: 0.30
Nodes (5): get_me(), get, Dependency that strictly requires an active admin user., Get profile of currently signed-in user., require_admin()

### Community 99 - "Architecture Overview"
Cohesion: 0.50
Nodes (4): Architecture Overview, Carrier Connector Lifecycle, Charge Classification Rules, Search Flow

### Community 100 - "[2026-06-02] — Hapag-Lloyd Transshipment & Duplicate Fix"
Cohesion: 0.67
Nodes (3): [2026-06-02] — Hapag-Lloyd Transshipment & Duplicate Fix, Hapag-Lloyd — Duplicate Sailings from Transshipment Vessels, Hapag-Lloyd — Routing Not Marked as Transit

## Knowledge Gaps
- **291 isolated node(s):** `Config`, `install_pi.sh script`, `eslintConfig`, `nextConfig`, `name` (+286 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 889 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **15 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Changelog` connect `Changelog` to `Architecture Overview`, `[2026-06-02] — Hapag-Lloyd Transshipment & Duplicate Fix`, `._verify_price_owner_selected`, `[2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning`, `NotAvailableConnector`, `._fs_dismiss_modals`, `HapagLloydConnector`, `[2026-05-29 – 2026-05-30] — Hapag-Lloyd Full Integration`, `[2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control`, `[2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash`, `[2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split`, `[2026-05-20 – 2026-05-22] — Port Resolution & Frontend Improvements`, `[2026-05-23 – 2026-05-24] — Maersk Shadow DOM & Stealth Upgrades`, `[2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes`, `[2026-06-03] — CMA CGM Routing & Free Time Extraction`, `[2026-08-04 - 2026-08-06] — CMA CGM Dynamic RAMP/POD Rerouting, Brand Excel Styling, Port Synonym Matching & Tunnel Relays`, `[2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup`?**
  _High betweenness centrality (0.327) - this node is a cross-community bridge._
- **Why does `[2026-06-03] — CMA CGM Routing & Free Time Extraction` connect `[2026-06-03] — CMA CGM Routing & Free Time Extraction` to `Changelog`?**
  _High betweenness centrality (0.299) - this node is a cross-community bridge._
- **Why does `Maersk — Free Time Extraction from Card Text` connect `[2026-06-03] — CMA CGM Routing & Free Time Extraction` to `app/page.tsx`?**
  _High betweenness centrality (0.298) - this node is a cross-community bridge._
- **Are the 27 inferred relationships involving `RateSearchRequest` (e.g. with `create_batch_rate_search()` and `create_rate_search()`) actually correct?**
  _`RateSearchRequest` has 27 INFERRED edges - model-reasoned connections that need verification._
- **Are the 21 inferred relationships involving `CarrierResultStatus` (e.g. with `safe_step()` and `update_carrier_status()`) actually correct?**
  _`CarrierResultStatus` has 21 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `cn()` (e.g. with `Reuse the primitives` and `7. Conventions to follow from here`) actually correct?**
  _`cn()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Config`, `install_pi.sh script`, `eslintConfig` to the rest of the system?**
  _291 weakly-connected nodes found - possible documentation gaps or missing edges._