# Graph Report - Infreight_SourcingRates_SG  (2026-10-09)

## Corpus Check
- 253 files · ~1,167,718 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 25 file(s) not represented in the graph (top: (none) 10, .bat 8, .conf 2)

## Summary
- 2482 nodes · 6136 edges · 123 communities (101 shown, 22 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 356 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `06d041b7`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- run_vertical_batch_searches
- CarrierResultStatus
- cn
- user_routes.py
- auth_routes.py
- browser_cleanup.py
- LiveSearchProgress.tsx
- api.ts
- PortManager
- RateSearch
- CMAConnector
- get_async_session_maker
- selector_memory.py
- login/page.tsx
- RateSearchRequest
- HapagLloydAPIConnector
- preferences.ts
- test_rfq_agent.py
- tunnel_relay/main.py
- SocialWidget.tsx
- ._parse_offer_response_to_quotes
- GreenXConnector
- social_routes.py
- ChargeCategory
- backend/main.py
- rate_search_routes.py
- MSCConnector
- parse_rfq
- lucide-react
- ai_agent.py
- job_service.py
- ONEConnector
- _Page
- Engineering Report: Sourcing Portal Enhancements & Scraping Pipeline Stability
- Changelog
- admin/page.tsx
- package.json
- carrier_switches.py
- RateResults.tsx
- SearchQueueManager
- test_normalizer.py
- SelfHealingAlerts.tsx
- compilerOptions
- ._fs_dismiss_modals
- test_carrier_timeout.py
- ._query_prices_api
- dithered-logo.tsx
- 👥 The 5 Agent Roles
- HapagLloydConnector
- [2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning
- [2026-06-03] — CMA CGM Routing & Free Time Extraction
- carrier_sessions.py
- BatchProgressPanel.tsx
- test_hapag_freetime.py
- 🚢 Infreight Sourcing & Ocean Rate Automation System
- MaerskConnector
- [2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split
- compute_admin_analytics
- 🛠 Detailed Carrier Log
- .extract_charge_breakdown
- CurrencyManager
- test_one_premium_override.py
- [2026-06-30] — ONE Multi-Container & Sold-Out, GreenX Surcharge Intake, Free-Time Fixes, Maersk Diagnosis
- [2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup
- json
- Scraper Robustness Review — July 2026
- GreenX — Surcharge Intake Fix (2026-06-30)
- Admin Page & Port Prioritization Guide
- ._verify_price_owner_selected
- test_self_healing.py
- test_panama_canal_surcharge.py
- test_one_charge_override.py
- deploy
- export_maersk_login.py
- ._lookup_freetime
- Summary of Changes — July 20, 2026
- .validate_currency
- [2026-05-29 – 2026-05-30] — Hapag-Lloyd Full Integration
- resolve_port_alias
- test_brightdata.py
- ._fs_fill_port
- Design system — read before touching any UI
- ai_repair_agent.py
- layout.tsx
- diagnose_greenx_dropdown.py
- test_one_breakdown_parsing
- test_rate_search_api.py
- RateLimiter
- sys
- test_hapag_api_connector.py
- test_el_dekheila_maersk.py
- ref_fs
- test_one_breakdown.py
- [2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History
- require_admin
- [2026-05-20 – 2026-05-22] — Port Resolution & Frontend Improvements
- frontend/README.md
- parse_msc_modal_charges
- [2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control
- os
- .extract_charge_breakdown
- [2026-05-18 – 2026-05-19] — Railway Deployment & Docker
- [2026-05-25 – 2026-05-26] — VNC Display Isolation & Proxy Integration
- Working in this repository
- [2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes
- install_pi.sh
- remote_worker.py
- postcss.config.mjs
- [2026-05-31] — Multi-Instance Support & Charge Classification
- [2026-05-23 – 2026-05-24] — Maersk Shadow DOM & Stealth Upgrades
- get_me
- Architecture Overview
- main
- safe_step.py
- alembic

## God Nodes (most connected - your core abstractions)
1. `RateSearchRequest` - 164 edges
2. `cn()` - 89 edges
3. `CarrierResultStatus` - 71 edges
4. `QuoteSchema` - 67 edges
5. `User` - 63 edges
6. `PortManager` - 58 edges
7. `HapagLloydConnector` - 56 edges
8. `CMAConnector` - 55 edges
9. `MaerskConnector` - 54 edges
10. `BaseCarrierConnector` - 50 edges

## Surprising Connections (you probably didn't know these)
- `4. Ranked recommendations` --references--> `safe_step()`  [INFERRED]
  docs/ROBUSTNESS_REVIEW_2026-07.md → backend/agent/safe_step.py
- `Excel Export — Routing & Free Time Columns Always Empty` --references--> `Quote`  [INFERRED]
  CHANGELOG.md → backend/models/quote.py
- `Hapag-Lloyd — Date String Standardization` --references--> `standardize_date_string()`  [INFERRED]
  CHANGELOG.md → backend/services/normalizer.py
- `2. Bugs found and fixed during the restyle` --references--> `BackendConfigModal()`  [INFERRED]
  FRONTEND_REDESIGN_2026-09-07.md → frontend/src/components/BackendConfigModal.tsx
- `7. Conventions to follow from here` --references--> `cn()`  [INFERRED]
  FRONTEND_REDESIGN_2026-09-07.md → frontend/src/lib/utils.ts

## Import Cycles
- None detected.

## Communities (123 total, 22 thin omitted)

### Community 0 - "run_vertical_batch_searches"
Cohesion: 0.21
Nodes (14): cleanup_browsers_if_idle(), UUID, Check all carrier results and update the overall search status., Run search jobs for all selected carriers concurrently, updating overall status…, Kill leftover browsers and delete leftover temporary profiles, but only when no…, Executes multi-route RFQ tenders using Vertical Carrier-First Persistent…, run_all_carrier_searches(), do_cleanup() (+6 more)

### Community 1 - "CarrierResultStatus"
Cohesion: 0.04
Nodes (50): ABC, BaseCarrierConnector, NotAvailableConnector, Any, Open the price breakdown / detail view for a specific quote. Args: quote_ref:…, Extract individual charge line items from the price breakdown. Returns: List of…, Normalize extracted data into a QuoteSchema using the normalizer. Args:…, Abstract base class for carrier portal connectors. (+42 more)

### Community 2 - "cn"
Cohesion: 0.08
Nodes (48): Reuse the primitives, New primitives — `frontend/src/components/ui/`, BackendConfigModalProps, LoadingState(), LoginModalProps, Box(), fieldName(), laneFlags() (+40 more)

### Community 3 - "user_routes.py"
Cohesion: 0.06
Nodes (85): get_current_user(), Dependency that strictly requires an authenticated active member., admin_delete_user(), AdminLoginRequest, approve_user(), CarrierOverrideRequest, CarrierSwitchRequest, Config (+77 more)

### Community 4 - "auth_routes.py"
Cohesion: 0.06
Nodes (74): clear_session_cookie(), get_current_user_optional(), login(), LoginRequest, logout(), AsyncSession, BaseModel, post (+66 more)

### Community 5 - "browser_cleanup.py"
Cohesion: 0.07
Nodes (40): _is_chrome(), _is_playwright_driver(), _kill(), kill_profile_browsers(), _proc_supported(), Cleanup for Chrome browsers and temporary profiles that a failed close leaves…, Kill every automated Chrome and Playwright driver. Only call this when no…, Delete per-search profile copies ("chrome_profile_<carrier>_tmp_<id>") and… (+32 more)

### Community 6 - "LiveSearchProgress.tsx"
Cohesion: 0.09
Nodes (25): AppHeader(), AppHeaderProps, initials(), systemStatus(), ACTION_STATUSES, ChipModel, describe(), EMPTY_STATUSES (+17 more)

### Community 7 - "api.ts"
Cohesion: 0.08
Nodes (66): AdminDashboard(), HomeContent(), AdminCarriers(), PROFILE_NAMES, when(), BackendConfigModal(), SearchCompletionModal(), addCarrierOverride() (+58 more)

### Community 8 - "PortManager"
Cohesion: 0.05
Nodes (43): get_countries(), get_port(), get_suggestions(), get, Get list of countries for autocomplete dropdown., Get specific port details by UN/LOCODE., Get port suggestions for autocomplete., search() (+35 more)

### Community 9 - "RateSearch"
Cohesion: 0.09
Nodes (23): RateSearch, Represents a rate search request from an employee., test_switched_off_carrier_is_skipped(), run(), db(), row(), setup(), FakeConnector (+15 more)

### Community 10 - "CMAConnector"
Cohesion: 0.08
Nodes (18): CMAConnector, Ensures 'Ramp' is explicitly selected under 'Type of location' toggle buttons…, Scans for Route, POL (Port of Loading), or POD (Port of Discharge) dropdown…, Clears the currently selected Destination port tag/card, re-types the locode,…, Dynamically extracts any recommended 5-letter POD LOCODE mentioned in the…, Detects if CMA CGM displayed an advisory banner message: "Looking for AEJEA or…, Handles the 'Customer account' -> 'Role (you are acting as)' dropdown on CMA…, Repeatedly clicks 'More results' if visible to load ALL quotes on the page. (+10 more)

### Community 11 - "get_async_session_maker"
Cohesion: 0.09
Nodes (32): get_recent_search_status_context(), Queries the database for the most recent rate search status to give the chatbot…, get_route_health(), Get carrier search reliability & route health matrix across origin-destination…, _create_sqlite_engine(), get_async_session_maker(), _get_engine(), _get_session_maker() (+24 more)

### Community 12 - "selector_memory.py"
Cohesion: 0.24
Nodes (12): get_approved_selector(), _load_memory(), Selector Memory — stores and retrieves human-approved selector patches., Loads memory JSON file. Returns empty dict if file is missing or invalid., Saves memory dict back to JSON file., Looks up if there is an approved replacement selector for the given carrier and…, Stores an approved replacement selector., Marks any proposed selector for this step as REJECTED. (+4 more)

### Community 13 - "login/page.tsx"
Cohesion: 0.12
Nodes (16): nextConfig, LoginContent(), LoginModal(), hexToRgb01(), sanitizeHexColor(), SilkAurora(), SilkAuroraProps, WebGLErrorBoundary (+8 more)

### Community 14 - "RateSearchRequest"
Cohesion: 0.06
Nodes (38): OOCLConnector, parse_oocl_date(), Serves one container-type cycle from the cached merged quote set: -…, One crawl serves all container-type cycles (cached), combining: 1. Sailing…, Attempts to automatically click the Cloudflare Turnstile 'Verify you are human'…, Public oocl.com Chromium sailing schedule crawl bypassed per directive. All…, RateSearchRequest, run_test() (+30 more)

### Community 15 - "HapagLloydAPIConnector"
Cohesion: 0.15
Nodes (8): HapagLloydAPIConnector, Direct REST API connector for Hapag-Lloyd Prices API v2.1.4., API connectors do not require browser login sessions., No browser session to reset between batch routes., main(), test_locode_resolution(), test_payload_generation(), test_response_parsing_and_normalization()

### Community 16 - "preferences.ts"
Cohesion: 0.07
Nodes (39): LaunchIntro(), RateSearchFormProps, DEMO_EXAMPLES, RfqInputSection(), RfqInputSectionProps, SearchHistoryItem, derive(), Derived (+31 more)

### Community 17 - "test_rfq_agent.py"
Cohesion: 0.10
Nodes (36): API routes for RFQ parsing agent., RFQParseResult, asyncio, Unit tests for the Gemini AI RFQ Agent service (parse_rfq). Includes…, Test Image 2: Air rate request generates 3 drafts to Glenn (AWOT), Jing Hui…, Test Image 4: Steel Plate ex Pasir Gudang / Tanjung Pelepas for 20' & 40'., Test Guardrail: Detects Reefer container request and returns unsupported_cargo…, Test Guardrail: Detects LCL request. (+28 more)

### Community 18 - "tunnel_relay/main.py"
Cohesion: 0.25
Nodes (8): api_route, fastapi_middleware_cors, health(), get, Request, websocket, relay_request(), websocket_endpoint()

### Community 19 - "SocialWidget.tsx"
Cohesion: 0.07
Nodes (46): ChatWidget(), ChatWidgetProps, Message, ACCENT_COLORS, errorMessage(), relativeTime(), resizeImageToDataUrl(), SocialWidget() (+38 more)

### Community 20 - "._parse_offer_response_to_quotes"
Cohesion: 0.21
Nodes (5): Any, Maps a Prices API rate onto the categories the portal scraper produces (freight…, Leg locations are UnLocation/Facility objects per the spec; tolerate plain…, Renders a graduated weight tier (e.g. Heavy Lift: 18-99 TON) in the portal's…, Parses Hapag-Lloyd OfferResponse JSON into InFreight QuoteSchema objects.

### Community 21 - "GreenXConnector"
Cohesion: 0.09
Nodes (14): GreenXConnector, date, Overrides base search runner to query all 3 sizes at once and cache the…, Type a LOCODE into the autocomplete field and click the first visible dropdown…, Find quantity input next to or below label_text and fill it., Find the exact individual quote card container row encompassing dates, rates,…, Dismiss any cookie/alert modal that would intercept pointer events., Splits a single raw multi-container quote card into multiple QuoteSchema… (+6 more)

### Community 22 - "social_routes.py"
Cohesion: 0.12
Nodes (29): get_conversation(), list_colleagues(), poke_colleague(), PokeRequest, AsyncSession, BaseModel, delete, get (+21 more)

### Community 23 - "ChargeCategory"
Cohesion: 0.20
Nodes (21): ChargeCategory, classify_charge(), Charge Classifier — rule-based classification of freight charge line items.…, Classify a charge line item based on its name, amount, section heading, and…, Tests for charge classifier., test_basic_ocean_freight(), test_cwx_heavy_weight_charge(), test_destination_charges() (+13 more)

### Community 24 - "backend/main.py"
Cohesion: 0.10
Nodes (21): health(), lifespan(), get, websocket, Infreight Ocean Carrier Rate Automation — FastAPI Application. Main entry point…, Check if the VNC viewer is available (production only, where Xvfb runs)., Proxy WebSocket connections to legacy local x11vnc at localhost:5900., Proxy WebSocket connections to specific carrier x11vnc servers. (+13 more)

### Community 25 - "rate_search_routes.py"
Cohesion: 0.07
Nodes (52): approve_repair(), ApproveRepairRequest, carrier_switch_status(), chat_endpoint(), ChatRequest, create_batch_rate_search(), _contains(), _looks_like() (+44 more)

### Community 26 - "MSCConnector"
Cohesion: 0.13
Nodes (12): format_to_iso_date(), MSCConnector, Playwright-based automation for MSC (Mediterranean Shipping Company)., Handles the MSC login flow., Clicks Instant Quote, fills form, clicks Search., Detects and clicks the 'Ramp' delivery/haulage option if MSC displays Ramp /…, Parse '14 Jun 2026' to 'YYYY-MM-DD, main() (+4 more)

### Community 27 - "parse_rfq"
Cohesion: 0.12
Nodes (27): parse_rfq_endpoint(), post, Parse a free-text RFQ email or message into a structured RateSearchRequest…, _call_native_gemini_api(), _detect_booking_confirmation(), _detect_dual_mode_enquiry(), _detect_mode_by_hierarchy(), _detect_unsupported_cargo() (+19 more)

### Community 28 - "lucide-react"
Cohesion: 0.09
Nodes (35): 0. The one invariant, 1. Design system foundation (`082b43a`), 2. Bugs found and fixed during the restyle, 3. Workspace + launch intro (`21ade75`), 4. Follow-up fixes (`2f9d92b`), 5. Verification, 7. Conventions to follow from here, Dependencies added (5, all small, no runtime lib dependency on Componentry) (+27 more)

### Community 29 - "ai_agent.py"
Cohesion: 0.10
Nodes (20): AIBrowserAgent, AI Browser Agent — Vision-based browser automation using Gemini Flash. This…, Capture the current page as a PNG screenshot., Build the prompt with task description and action history., Parse Gemini's response into an action dict., Call Gemini API with exponential backoff retry., Execute a parsed action on the browser page., Detect if the agent is stuck repeating the same action. (+12 more)

### Community 30 - "job_service.py"
Cohesion: 0.10
Nodes (37): Chat Service — manages conversational AI queries from the frontend user using…, get_sync_url(), run_migrations_offline(), run_migrations_online(), fetch_port_fixes(), Saved port name fixes, marked built in or admin-added, and the ports each…, Base, _get_database_url() (+29 more)

### Community 31 - "ONEConnector"
Cohesion: 0.10
Nodes (11): ONEConnector, fill_container_card(), date, Parses ONE QUOTE Free Time popover text for DESTINATION ONLY. Ignores Origin…, Splits a single raw multi-container quote card into multiple QuoteSchema…, Tries to click a matching option from ONE's visible dropdown. Returns True only…, Extracts 5-letter UN/LOCODE from strings like 'Singapore [SGSIN]' or 'Singapore…, test_one_free_time_parser_origin_only_ignored() (+3 more)

### Community 32 - "_Page"
Cohesion: 0.15
Nodes (8): _connector(), _Locator, _Page, Maersk's login page redirects to the Hub a few seconds after loading when the…, Sits on /portaluser/login, then redirects after `redirect_after` URL reads., test_login_uses_saved_session_after_late_redirect(), test_wait_detects_late_redirect(), test_wait_detects_login_form()

### Community 33 - "Engineering Report: Sourcing Portal Enhancements & Scraping Pipeline Stability"
Cohesion: 0.08
Nodes (23): 1. Anti-Bot Mitigation & CAPTCHA Human-in-the-Loop Recovery, 2. Sourcing Parallelization & Surcharges Optimization, 3. Autocomplete Intelligence & Location Mapping, 4. Scraper Pipeline Maintenance, 5. Infrastructure & DevSecOps Enhancements, Business Value, Business Value, Business Value (+15 more)

### Community 34 - "Changelog"
Cohesion: 0.10
Nodes (19): [2026-06-01] — Hapag-Lloyd Sold Out Detection & Date Parsing, [2026-06-02] — Hapag-Lloyd Transshipment & Duplicate Fix, [2026-07-03] — Robustness Review & Multi-Port Quick Search Fixes, [2026-07-08] — OOCL E-Quote Calendar Navigation, cheapest E-Spot selection, and E-Quote/E-Spot isolation refinements, [2026-07-09] — Hapag-Lloyd Quick Quotes pairing and selection simplification, [2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash, AI RFQ Front Door & Air Freight Support, Batch (168-route) Execution — Isolation, Lock Scope, Polling (+11 more)

### Community 35 - "admin/page.tsx"
Cohesion: 0.06
Nodes (51): UserRecord, AdminAnalytics, AdminOverview(), AdminOverviewProps, AdminOverviewUser, AnalyticsRange, Attention, attentionItems() (+43 more)

### Community 36 - "package.json"
Cohesion: 0.04
Nodes (46): eslintConfig, dependencies, class-variance-authority, clsx, exceljs, lucide-react, next, next-themes (+38 more)

### Community 37 - "carrier_switches.py"
Cohesion: 0.35
Nodes (10): get_switches(), off_message(), _path(), Admin on/off switch per carrier, for when a carrier's site is down or under…, Every switchable carrier: {"enabled", "reason", "updated_by", "updated_at"}; on…, The message for a switched-off carrier's result, or None when it is on., _read(), set_switch() (+2 more)

### Community 38 - "RateResults.tsx"
Cohesion: 0.08
Nodes (53): LiveSearchProgressProps, QuoteBreakdownDrawer(), QuoteBreakdownDrawerProps, Breakdown(), ChargeList(), dateValue(), freeTimeText(), isSoldOut() (+45 more)

### Community 39 - "SearchQueueManager"
Cohesion: 0.12
Nodes (11): Lock, Marks a search as completed internally so we can track the auto-release timeout., Called periodically in a background task to check if the user has held the lock…, Forcefully clears all queued searches and the active lock. Useful for…, Returns or creates an asyncio.Lock for a specific carrier code to prevent…, Adds a search to the queue and waits until it becomes the active search. Event-…, Singleton manager to enforce a FIFO queue for rate searches. Since web scraping…, Returns the current position of the search in the queue. 0 means it is the… (+3 more)

### Community 40 - "test_normalizer.py"
Cohesion: 0.18
Nodes (16): is_weight_surcharge_applicable(), Evaluates whether a weight-tier or overweight surcharge is applicable for the…, calculate_final_freight_value(), classify_and_organize_charges(), Takes raw charge line items and classifies them. Args: raw_charges: list of…, Calculate the final freight value from a list of classified charges. Args:…, Tests for normalizer / final freight value calculator., test_basic_calculation() (+8 more)

### Community 41 - "SelfHealingAlerts.tsx"
Cohesion: 0.40
Nodes (4): 6. Known limitations / candidate follow-ups, RepairReport, SelfHealingAlerts(), SelfHealingAlertsProps

### Community 42 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 43 - "._fs_dismiss_modals"
Cohesion: 0.06
Nodes (29): clean_vessel_name(), get_booking_start_date(), _dismiss_once(), _click_date_strip_item(), _open_calendar(), _parse_date(), date, Event (+21 more)

### Community 44 - "test_carrier_timeout.py"
Cohesion: 0.13
Nodes (15): CrashingConnector, HangingConnector, asyncio, A carrier whose browser hangs must be stopped after CARRIER_SEARCH_TIMEOUT_SEC…, Hangs on the sizes in `hang_on`; answers NO_QUOTES_AVAILABLE for the rest., Like a real connector whose tab dies: reports a crash, then never returns., _run(), test_crashed_tab_stops_the_carrier_without_waiting_for_the_timeout() (+7 more)

### Community 45 - "._query_prices_api"
Cohesion: 0.20
Nodes (5): AsyncClient, Resolves a free-text port name or string (e.g. 'Singapore', 'Hamburg, Germany…, Hapag-Lloyd Prices API requires earliestDepartureDate to be at least 4 calendar…, Constructs OpenAPI compliant OfferRequest payload., Sends a single POST /prices request with rate-limiting and error handling.

### Community 46 - "dithered-logo.tsx"
Cohesion: 0.19
Nodes (15): applyMaskInversion(), buildRoundedMask(), DEFAULTS, DitherConfig, DitheredLogo(), DitheredLogoProps, drawParticles(), errorDiffusionDither() (+7 more)

### Community 47 - "👥 The 5 Agent Roles"
Cohesion: 0.13
Nodes (14): 1. Intake Agent (Email Listener), 2. Sourcing Orchestrator (The Coordinator), 3. Sourcing & Scraping Agent (Rates Engine), 4. Finance & Costing Agent (Excel Compiler), 5. Email Draft Agent (Communicator), 📋 Executive Summary, 🛠️ Implementation Stages, Phase 1: Email Integration (Week 1-2) (+6 more)

### Community 48 - "HapagLloydConnector"
Cohesion: 0.06
Nodes (31): HapagLloydConnector, HapagServiceUnavailableException, Exception, Normalize various date formats (e.g. 2026-05-31, 31.05.2026, 31 May 2026, 31…, Robustly selects options from Hapag-Lloyd custom dropdown lists. Types the…, Guards against the session-expiry-mid-crawl failure mode: the existing redirect…, Crawls Hapag-Lloyd sailing schedules from the Schedule tab., Fuzzy match quote ETD with crawled schedules within a window of +/- 2 days. (+23 more)

### Community 49 - "[2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning"
Cohesion: 0.22
Nodes (8): Detects the Microsoft B2C identity/OAuth login page. Hapag can silently bounce…, [2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning, GreenX — "No Quotes" Reported While Quotes Visibly Loaded in VNC, Hapag-Lloyd — Configurable Pacing & Redundant-Wait Removal, Hapag-Lloyd — Crawl Stalls by Typing a Port Locode Into the Login Email Field, Job Scheduler — Concurrency Default, Maersk — Regression: Other-Container-Type Sizes Went "Sold Out" in Multi-Container Searches, OOCL — Schedule Search Repeated Once Per Container Type

### Community 50 - "[2026-06-03] — CMA CGM Routing & Free Time Extraction"
Cohesion: 0.50
Nodes (4): [2026-06-03] — CMA CGM Routing & Free Time Extraction, CMA CGM — Import Free Time from D&D Tab, CMA CGM — Routing Detection (Direct vs Transit), Maersk — Free Time Extraction from Card Text

### Community 51 - "carrier_sessions.py"
Cohesion: 0.07
Nodes (32): _is_logged_in_url(), maersk_proxy_settings(), Small aimless pointer drift, as a person does while a page loads., Clicks an element with pre-click and post-click human-like reaction pauses., Wait until the login page either redirects to a signed-in page or shows its…, True once Maersk has moved past the login pages to a signed-in page., Load the saved login an admin uploaded (Admin > Carriers on / off) into this…, Proxy for the Maersk browser, from environment variables, or None. Any… (+24 more)

### Community 52 - "BatchProgressPanel.tsx"
Cohesion: 0.31
Nodes (8): BatchProgressPanel(), BatchProgressPanelProps, cheapest(), Filter, lanePhase(), Phase, PHASE_STYLE, BatchRouteResult

### Community 53 - "test_hapag_freetime.py"
Cohesion: 0.18
Nodes (15): _apply_freetime_to_quote(), freetime_days(), match_freetime_entry(), Any, Destination free time from config/hapag_freetime.json, shared by the Hapag-…, Days for this container from a table entry ({"20GP": n, "40GP": n} or a bare…, The table entry whose country name appears in `text` as whole words. Whole…, days() (+7 more)

### Community 54 - "🚢 Infreight Sourcing & Ocean Rate Automation System"
Cohesion: 0.14
Nodes (13): 1. Multi-Carrier Automation Engine, 2. Intelligent Surcharge & Charge Classifier Engine (`charge_classifier.py`), 3. Container Comparison Matrix & Excel Export Engine, 🚢 Infreight Sourcing & Ocean Rate Automation System, 🌟 Key Capabilities, 📄 License & Confidentiality, Prerequisites, 🛠️ Project Structure (+5 more)

### Community 55 - "MaerskConnector"
Cohesion: 0.06
Nodes (23): extract_locode_and_country(), MaerskConnector, Fills an autocomplete field using the proven original element-level…, Execute the full search flow with Progressive Lazy Loading: 1. Login 2. Search…, Extracts freetime, demurrage, and detention from the 'Import D&D fees' tab…, Extracts the routing details from the 'Route & other details' accordion.…, Extracts LOCODE and country name from text like 'CASABLANCA, MOROCCO (MACAS)'…, Splits a single raw multi-container quote card into multiple QuoteSchema… (+15 more)

### Community 56 - "[2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split"
Cohesion: 0.15
Nodes (13): G2 Stress Test: "Hi, Please book the below as per your quote ref INF-2026-0842:…, H1 Stress Test: Table with 2 distinct rows: Row 1: POL Singapore, POD Jakarta,…, test_g2_booking_confirmation_guardrail(), test_h1_table_deduplication_two_pairs(), [2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split, Booking Confirmation / Instructions Intercept Guardrail G2 (`rfq_agent.py` & `RfqInputSection.tsx`), Commercial Sales Desk Intelligence (`sales_notes`), Deterministic Port Alias Resolver (`ports_aliases.json`) (+5 more)

### Community 57 - "compute_admin_analytics"
Cohesion: 0.25
Nodes (8): compute_admin_analytics(), get_clean_lane_key(), normalize_lane_port(), Any, AsyncSession, Normalize port string to cleanly aggregate naming variations., Returns (norm_origin, norm_dest, display_lane_key)., Compute full consolidated analytics payload for the admin dashboard.

### Community 58 - "🛠 Detailed Carrier Log"
Cohesion: 0.15
Nodes (12): 🛠 Detailed Carrier Log, 🟢 GreenX, 🟠 Hapag-Lloyd, Infreight Ocean Carrier Rate Automation — Development Log, 🚀 Key Highlights & Architectural Changes, 🔌 Local Laptop Deployment (Self-Hosted Worker), 🔵 Maersk, 💗 ONE (Ocean Network Express) (+4 more)

### Community 60 - "CurrencyManager"
Cohesion: 0.23
Nodes (6): convert_currency_to_usd(), CurrencyManager, Any, Currency Exchange Rate Service — manages currency conversions and custom…, update_exchange_rate(), threading

### Community 61 - "test_one_premium_override.py"
Cohesion: 0.40
Nodes (3): MockCard, Unit test for ONE connector and charge classifier Premium Cargo Service…, test_premium_cargo_service_override()

### Community 62 - "[2026-06-30] — ONE Multi-Container & Sold-Out, GreenX Surcharge Intake, Free-Time Fixes, Maersk Diagnosis"
Cohesion: 0.29
Nodes (7): [2026-06-30] — ONE Multi-Container & Sold-Out, GreenX Surcharge Intake, Free-Time Fixes, Maersk Diagnosis, GreenX — Only Basic Ocean Freight & LSS Folded Into Final Value, MAERSK — "Quotes Found" but Empty Excel (Diagnosis), ONE — All-Container-Type Search Returning 0 Quotes, ONE — Multi-Container Breakdown Triple-Counted / Inflated Final Value, ONE — Sold-Out ("Notify Me") Sailings Appearing as Quotes, Performance/Reliability — Stop Copying Chrome Caches During Profile Clone/Sync

### Community 63 - "[2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup"
Cohesion: 0.12
Nodes (10): MockCard, MockLocator, [2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup, Chromium Cache Auto-Cleanup (Railway Storage Bloat Prevention), CMA CGM — 30-Second Timeout on Sold Out Cards, CMA CGM — Free Time Regex Too Strict, CMA CGM — Routing Regex Not Matching "via LEKKI, LA, NG", Excel Export — Routing & Free Time Columns Always Empty (+2 more)

### Community 64 - "json"
Cohesion: 0.21
Nodes (10): argparse, Repair Report — generates and saves diagnosis reports on Playwright selector…, check_and_wait_for_captcha(), login(), main(), json, handle_request(), AsyncClient (+2 more)

### Community 65 - "Scraper Robustness Review — July 2026"
Cohesion: 0.33
Nodes (5): 1. What was measured, 3. Multi-port quick search — defects found and fixed, 4. Ranked recommendations, 5. Verification of this change, Scraper Robustness Review — July 2026

### Community 66 - "GreenX — Surcharge Intake Fix (2026-06-30)"
Cohesion: 0.22
Nodes (8): Charges that must be taken into the final value (USD only), Files changed, Fix, GreenX — Surcharge Intake Fix (2026-06-30), Per-B/L charges (billed once per booking, added in full to *each* container type), Problem, Root cause, Verification

### Community 67 - "Admin Page & Port Prioritization Guide"
Cohesion: 0.25
Nodes (7): 1. Popular Ports (UN/LOCODEs), 2. Boosted Countries, Admin Page & Port Prioritization Guide, 🔒 How to Access the Admin Page, ⚙️ How to Use Port Prioritization, ⚡ Important Notes, 📝 Step-by-Step Example

### Community 68 - "._verify_price_owner_selected"
Cohesion: 0.25
Nodes (7): Verifies the "I am the price owner" radio is genuinely checked, piercing shadow…, [2026-07-03] — OOCL FreightSmart Autoclear, Hapag Price Leak & Redirect fixes, Maersk Cache Scoping, Dallas Overrides, Hapag-Lloyd — Price Leaks, Column Matching, and Redirect Recovery, Maersk — 0.0-USD / "Not Open" Card Flakiness (the "Quotes Found but Empty Excel" root causes), Maersk — Caching Scope & Selector Tuning, OOCL — FreightSmart Popup Dismissals & Input Lock Serialization, Ports — Hardcoded Dallas Override

### Community 69 - "test_self_healing.py"
Cohesion: 0.15
Nodes (17): handle_chat_query(), _local_chatbot_fallback(), Intelligent responder for search status, carrier guidance, air/sea info, and…, Sends the chat message and history to native Gemini 2.5 Flash API. If Gemini…, detect_manual_action_required(), Manual Action Detector — identifies pages requiring human verification (2FA,…, Scans the current Playwright page to see if a CAPTCHA, Cloudflare challenge,…, clean_selector_memory() (+9 more)

### Community 70 - "test_panama_canal_surcharge.py"
Cohesion: 0.18
Nodes (11): Sort container types in standard order: DRY 20 (20GP) -> DRY 40 (40GP) -> DRY…, sort_container_types(), asyncio, Verify charge_classifier classifies Panama Canal Surcharge as…, Verify regex extraction of Estimated Transportation Days from Hapag-Lloyd modal…, Verify OOCL normalize_result incorporates Panama Canal Surcharge (PCS)., test_charge_classifier_panama_canal_surcharge(), test_container_types_standard_ordering() (+3 more)

### Community 71 - "test_one_charge_override.py"
Cohesion: 0.40
Nodes (3): MockCard, Unit test for ONE connector charge classification override., test_emergency_surcharge_override()

### Community 72 - "deploy"
Cohesion: 0.25
Nodes (7): build, builder, deploy, restartPolicyMaxRetries, restartPolicyType, startCommand, $schema

### Community 73 - "export_maersk_login.py"
Cohesion: 0.70
Nodes (4): _logged_in(), main(), _on_login_page(), Save a Maersk login from your own PC for the server to use. Opens real Google…

### Community 75 - "Summary of Changes — July 20, 2026"
Cohesion: 0.29
Nodes (6): 1. AI RFQ Front Door & Air Freight Support (Phase A), 2. Multi-Origin & Gappy List Parsing for Sea RFQs (Phase B), 3. Search Form Streamlining (Form Input Restrictions), 4. Native Gemini 2.5 Flash API & Chatbot Resiliency, 5. Verification & Test Suite, Summary of Changes — July 20, 2026

### Community 77 - "[2026-05-29 – 2026-05-30] — Hapag-Lloyd Full Integration"
Cohesion: 0.40
Nodes (5): [2026-05-29 – 2026-05-30] — Hapag-Lloyd Full Integration, Hapag-Lloyd — Dropdown Autocomplete Issues, Hapag-Lloyd — Live Connector Implementation, Hapag-Lloyd — Onboarding Modal Blocking Form Interaction, Hapag-Lloyd — Search Button Selector Failures

### Community 78 - "resolve_port_alias"
Cohesion: 0.33
Nodes (6): _load_port_aliases_config(), Deterministically resolves a port string against ports_aliases.json and the…, resolve_port_alias(), Test that resolve_port_alias cleans 'City, Country' and parenthetical notes to…, test_resolve_city_country_format_to_clean_database_port_name(), Clean Search Dropdown Port Name Resolution (`rfq_agent.py` & `port_manager.py`)

### Community 79 - "test_brightdata.py"
Cohesion: 0.40
Nodes (5): get_title(), Script to test fetching CMA CGM pricing page using Bright Data Web Access HTTP…, test_brightdata_api(), urllib_error, urllib_request

### Community 80 - "._fs_fill_port"
Cohesion: 0.50
Nodes (3): Resolves input text to (location_name, locode, country_code, country_name)., Fills the origin/destination 'Enter Port or Door Point' autocomplete. The…, resolve_oocl_port_info()

### Community 81 - "Design system — read before touching any UI"
Cohesion: 0.33
Nodes (5): Animation rules, Client-only preferences, Design system — read before touching any UI, This is NOT the Next.js you know, Use tokens, not raw colours

### Community 82 - "ai_repair_agent.py"
Cohesion: 0.14
Nodes (13): ambiguous_python_import_b35980c0aa01, _local_fuzzy_repair(), AI Repair Agent — diagnoses Playwright step failures and suggests selector…, A local rule-based heuristic to locate reasonable buttons or inputs when Gemini…, Analyzes the failure context and DOM content to suggest a selector repair. Uses…, suggest_fix(), asyncio, Integration tests for authentication, legacy user password setup, pending… (+5 more)

### Community 83 - "layout.tsx"
Cohesion: 0.25
Nodes (6): frontend_src_app_globals, instrumentSans, inter, metadata, viewport, ThemeProvider()

### Community 84 - "diagnose_greenx_dropdown.py"
Cohesion: 0.67
Nodes (3): dump_options(), main(), Diagnostic: dump ALL dropdown options (text + innerHTML) when typing 'DEHAM'…

### Community 86 - "test_rate_search_api.py"
Cohesion: 0.50
Nodes (3): Tests for rate search API endpoints., Placeholder test — integration tests require DB setup., test_placeholder()

### Community 88 - "sys"
Cohesion: 0.11
Nodes (13): Interactive Headed Login Helper for Maersk. Opens real Chrome using the…, Interactive Headed Login Helper for ONE (Ocean Network Express). Opens Chrome…, Wrapper script to set Windows event loop policy before starting Uvicorn. This…, parse_hapag_pdf(), scrape_hapag_freetime(), Script to test Playwright browser launching using your REAL Google Chrome…, debug_cma(), safe_str() (+5 more)

### Community 89 - "test_hapag_api_connector.py"
Cohesion: 0.15
Nodes (8): get_connector(), Get the appropriate connector for a carrier. If USE_MOCK_CARRIERS=true: returns…, Standalone Test & Verification Suite for Hapag-Lloyd Prices REST API Connector.…, test_registry_integration(), Saving the Maersk session back to the master profile survives Chrome's file…, test_profile_save_retries_while_chrome_holds_files(), main(), run_carrier()

### Community 90 - "test_el_dekheila_maersk.py"
Cohesion: 0.40
Nodes (4): Verify non-Maersk carriers get standard UN/LOCODE or default mappings., Verify that El Dekheila maps specifically to 'Alexandria Dekheila, Egypt' for…, test_el_dekheila_maersk_override(), test_el_dekheila_other_carriers_unaffected()

### Community 93 - "[2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History"
Cohesion: 0.40
Nodes (5): [2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History, Admin User Search History & SGT GMT+8 Conversion (`AdminDashboard.tsx`), GreenX (Evergreen) Card Isolation & Surcharge Parsing (`greenx_connector.py`), Multi-Route Batch Execution Engine (`batch_engine.py`), OOCL FreightSmart 28-Day Calendar Expansion (`oocl_connector.py`)

### Community 95 - "[2026-05-20 – 2026-05-22] — Port Resolution & Frontend Improvements"
Cohesion: 0.50
Nodes (4): [2026-05-20 – 2026-05-22] — Port Resolution & Frontend Improvements, Excel Export — ETA Column & Container Type Header, Frontend Light Mode & CORS Fix, Port Resolution System

### Community 96 - "frontend/README.md"
Cohesion: 0.50
Nodes (3): Deploy on Vercel, Getting Started, Learn More

### Community 97 - "parse_msc_modal_charges"
Cohesion: 0.24
Nodes (8): parse_msc_modal_charges(), Parses charges from MSC BreakdownModal text. Correctly includes charges whose…, Test MSC charges parsing for Singapore to Conakry, Guinea (40GP). Charges with…, Test when only some surcharges have the payment condition., test_msc_charges_mixed_conditions(), test_msc_charges_singapore_to_conakry_guinea(), Verify MSC charge extraction logic parses Panama Canal Surcharge properly., test_msc_charge_extraction_logic()

### Community 98 - "[2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control"
Cohesion: 0.40
Nodes (5): [2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control, Concurrency Limit Queue & Admin Control Panel, MSC — Mediterranean Shipping Company Connector Implementation, ONE — Inbound Free Time Swap & Scraper Upgrade, OOCL — Orient Overseas Container Line Connector Implementation

### Community 99 - "os"
Cohesion: 0.07
Nodes (43): asyncio, Page Observer — captures page state (screenshot, DOM, visible text) on failure., Base Carrier Connector — abstract base class for all carrier connectors. Each…, CMA CGM Live Connector — Playwright automation. Credentials read from env:…, Normalize CMA CGM data into QuoteSchema. Rule: include BASIC_OCEAN_FREIGHT and…, GreenX (Evergreen) Live Connector - Playwright automation., Hapag-Lloyd Prices API Connector (REST API v2.1.4). Provides real-time rate…, # NOTE: No start date fill needed — schedule page defaults to today, (+35 more)

### Community 102 - "[2026-05-18 – 2026-05-19] — Railway Deployment & Docker"
Cohesion: 0.67
Nodes (3): [2026-05-18 – 2026-05-19] — Railway Deployment & Docker, Persistent Chrome Profiles on Railway Volume, Railway Deployment Setup

### Community 103 - "[2026-05-25 – 2026-05-26] — VNC Display Isolation & Proxy Integration"
Cohesion: 0.67
Nodes (3): [2026-05-25 – 2026-05-26] — VNC Display Isolation & Proxy Integration, Bright Data ISP Proxy Integration, VNC Display Isolation for Concurrent Carriers

### Community 106 - "[2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes"
Cohesion: 0.50
Nodes (4): [2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes, CMA CGM — Chrome Profile Bypass, ONE — Date Formatting & Charge Breakdown Pollution, ONE — Date Picker Pre-selection Issue

### Community 108 - "remote_worker.py"
Cohesion: 0.08
Nodes (34): Models package. Note: Individual modules can be imported directly (e.g.,…, A worker machine (e.g. the office laptop) that runs some carriers' searches., WorkerHeartbeat, _claim_loop(), claim_next(), delegate_and_wait(), heartbeat_once(), _heartbeat_thread() (+26 more)

### Community 116 - "[2026-05-31] — Multi-Instance Support & Charge Classification"
Cohesion: 0.67
Nodes (3): [2026-05-31] — Multi-Instance Support & Charge Classification, Charge Classification Improvements, Multi-Instance Concurrent Searches

### Community 117 - "[2026-05-23 – 2026-05-24] — Maersk Shadow DOM & Stealth Upgrades"
Cohesion: 0.50
Nodes (4): [2026-05-23 – 2026-05-24] — Maersk Shadow DOM & Stealth Upgrades, Maersk — 2FA/CAPTCHA Human-in-the-Loop via noVNC, Maersk — Login Credential Autofill Corruption, Maersk — Shadow DOM Piercing for MDS Web Components

### Community 119 - "get_me"
Cohesion: 0.67
Nodes (3): get_me(), get, Get profile of currently signed-in user.

### Community 120 - "Architecture Overview"
Cohesion: 0.50
Nodes (4): Architecture Overview, Carrier Connector Lifecycle, Charge Classification Rules, Search Flow

### Community 128 - "safe_step.py"
Cohesion: 0.15
Nodes (15): capture_failure_context(), Exception, Failure Detector — parses and structures error context from failed Playwright…, Assembles a standardized diagnostic dictionary containing all available details…, capture_page_state(), Captures screenshot, DOM HTML, and inner text of the current page. Saves…, generate_report(), Assembles a comprehensive repair report and writes it as JSON and Markdown… (+7 more)

## Knowledge Gaps
- **313 isolated node(s):** `Config`, `install_pi.sh script`, `eslintConfig`, `nextConfig`, `name` (+308 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 969 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **22 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Changelog` connect `Changelog` to `[2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control`, `._verify_price_owner_selected`, `[2026-05-18 – 2026-05-19] — Railway Deployment & Docker`, `[2026-05-25 – 2026-05-26] — VNC Display Isolation & Proxy Integration`, `PortManager`, `[2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes`, `._fs_dismiss_modals`, `[2026-05-29 – 2026-05-30] — Hapag-Lloyd Full Integration`, `[2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning`, `[2026-06-03] — CMA CGM Routing & Free Time Extraction`, `[2026-05-31] — Multi-Instance Support & Charge Classification`, `[2026-05-23 – 2026-05-24] — Maersk Shadow DOM & Stealth Upgrades`, `[2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History`, `[2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split`, `Architecture Overview`, `[2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup`, `[2026-06-30] — ONE Multi-Container & Sold-Out, GreenX Surcharge Intake, Free-Time Fixes, Maersk Diagnosis`, `[2026-05-20 – 2026-05-22] — Port Resolution & Frontend Improvements`?**
  _High betweenness centrality (0.322) - this node is a cross-community bridge._
- **Why does `[2026-06-03] — CMA CGM Routing & Free Time Extraction` connect `[2026-06-03] — CMA CGM Routing & Free Time Extraction` to `Changelog`?**
  _High betweenness centrality (0.270) - this node is a cross-community bridge._
- **Why does `Maersk — Free Time Extraction from Card Text` connect `[2026-06-03] — CMA CGM Routing & Free Time Extraction` to `RateResults.tsx`?**
  _High betweenness centrality (0.269) - this node is a cross-community bridge._
- **Are the 33 inferred relationships involving `RateSearchRequest` (e.g. with `create_batch_rate_search()` and `create_rate_search()`) actually correct?**
  _`RateSearchRequest` has 33 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `cn()` (e.g. with `Reuse the primitives` and `7. Conventions to follow from here`) actually correct?**
  _`cn()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 22 inferred relationships involving `CarrierResultStatus` (e.g. with `safe_step()` and `update_carrier_status()`) actually correct?**
  _`CarrierResultStatus` has 22 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Config`, `install_pi.sh script`, `eslintConfig` to the rest of the system?**
  _313 weakly-connected nodes found - possible documentation gaps or missing edges._