# Graph Report - Infreight_Sourcing_New  (2026-10-15)

## Corpus Check
- 282 files · ~1,190,166 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 27 file(s) not represented in the graph (top: (none) 10, .bat 9, .conf 2)

## Summary
- 2555 nodes · 6292 edges · 133 communities (108 shown, 25 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 366 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `74088589`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- database.py
- CarrierResultStatus
- cn
- user_routes.py
- auth_routes.py
- browser_cleanup.py
- SocialWidget.tsx
- api.ts
- PortManager
- ._parse_offer_response_to_quotes
- CMAConnector
- env.py
- maersk_connector.py
- test_hapag_freetime.py
- RateSearchRequest
- test_hapag_api_connector.py
- preferences.ts
- test_rfq_agent.py
- re
- tunnel_relay/main.py
- ._verify_price_owner_selected
- GreenXConnector
- social_routes.py
- ChargeCategory
- backend/main.py
- rate_search_routes.py
- MSCConnector
- rfq_agent.py
- HapagLloydAPIConnector
- AIBrowserAgent
- CarrierSearchResult
- ONEConnector
- _Page
- Engineering Report: Sourcing Portal Enhancements & Scraping Pipeline Stability
- Changelog
- admin/page.tsx
- package.json
- carrier_switches.py
- RateResults.tsx
- SearchQueueManager
- job_service.py
- app/page.tsx
- compilerOptions
- ._fs_dismiss_modals
- test_carrier_timeout.py
- .extract_charge_breakdown
- dithered-logo.tsx
- 👥 The 5 Agent Roles
- HapagLloydConnector
- [2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning
- [2026-06-03] — CMA CGM Routing & Free Time Extraction
- carrier_sessions.py
- LiveSearchProgress.tsx
- types.ts
- 🚢 Infreight Sourcing & Ocean Rate Automation System
- QuoteSchema
- [2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split
- .run_full_search
- 🛠 Detailed Carrier Log
- ._dismiss_hapag_modals
- test_panama_canal_surcharge.py
- [2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control
- [2026-06-30] — ONE Multi-Container & Sold-Out, GreenX Surcharge Intake, Free-Time Fixes, Maersk Diagnosis
- [2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup
- orbit-card-stack.tsx
- Scraper Robustness Review — July 2026
- GreenX — Surcharge Intake Fix (2026-06-30)
- Admin Page & Port Prioritization Guide
- parse_msc_modal_charges
- test_self_healing.py
- schemas.py
- RFQParseResult
- deploy
- Frontend Redesign — Componentry Design System, Workspace & Launch Intro (2026-09-07)
- revoke_user_sessions
- Summary of Changes — July 20, 2026
- silk-aurora.tsx
- [2026-05-29 – 2026-05-30] — Hapag-Lloyd Full Integration
- resolve_port_alias
- test_brightdata.py
- MockCard
- Design system — read before touching any UI
- [2026-05-18 – 2026-05-19] — Railway Deployment & Docker
- layout.tsx
- test_one_premium_override.py
- Infreight Sourcing Automation — Run Audit (30 Jul 2026)
- [2026-06-02] — Hapag-Lloyd Transshipment & Duplicate Fix
- RateLimiter
- [2026-05-23 – 2026-05-24] — Maersk Shadow DOM & Stealth Upgrades
- dependencies
- parse_rfq
- test_excel_exports.js
- websockify_carrier_proxy
- [2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History
- ._lookup_freetime
- devDependencies
- frontend/README.md
- test_js.js
- get_me
- os
- fill_container_card
- .extract_charge_breakdown
- ._wait_for_captcha_resolution
- MockCard
- Working in this repository
- [2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes
- install_pi.sh
- remote_worker.py
- postcss.config.mjs
- get_current_user_optional
- scripts
- require_admin
- fetch_port_fixes
- test_one_breakdown_parsing
- Architecture Overview
- e2e_downloaded_multisheet_28ec47f9.md
- eslint.config.mjs
- test_normalizer.py
- e2e_downloaded_tariff_d21a0cb7.md
- [2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash
- pytest
- HapagServiceUnavailableException
- ambiguous_python_import_b35980c0aa01
- [2026-05-25 – 2026-05-26] — VNC Display Isolation & Proxy Integration
- [2026-06-01] — Hapag-Lloyd Sold Out Detection & Date Parsing

## God Nodes (most connected - your core abstractions)
1. `RateSearchRequest` - 168 edges
2. `cn()` - 89 edges
3. `CarrierResultStatus` - 72 edges
4. `QuoteSchema` - 69 edges
5. `User` - 63 edges
6. `CMAConnector` - 58 edges
7. `PortManager` - 58 edges
8. `HapagLloydConnector` - 56 edges
9. `MaerskConnector` - 55 edges
10. `BaseCarrierConnector` - 51 edges

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

## Communities (133 total, 25 thin omitted)

### Community 0 - "database.py"
Cohesion: 0.07
Nodes (45): get_recent_search_status_context(), handle_chat_query(), _local_chatbot_fallback(), Chat Service — manages conversational AI queries from the frontend user using…, Intelligent responder for search status, carrier guidance, air/sea info, and…, Queries the database for the most recent rate search status to give the chatbot…, Sends the chat message and history to native Gemini 2.5 Flash API. If Gemini…, get_route_health() (+37 more)

### Community 1 - "CarrierResultStatus"
Cohesion: 0.04
Nodes (38): ABC, BaseCarrierConnector, NotAvailableConnector, Any, Open the price breakdown / detail view for a specific quote. Args: quote_ref:…, Extract individual charge line items from the price breakdown. Returns: List of…, Abstract base class for carrier portal connectors., Detects if a CAPTCHA, Turnstile, hCaptcha, reCAPTCHA, or 2FA screen is… (+30 more)

### Community 2 - "cn"
Cohesion: 0.08
Nodes (47): Reuse the primitives, 0. The one invariant, New primitives — `frontend/src/components/ui/`, LoginModalProps, PortAutocomplete(), PortAutocompleteProps, RateSearchForm(), SearchCompletionModal() (+39 more)

### Community 3 - "user_routes.py"
Cohesion: 0.07
Nodes (74): admin_delete_user(), AdminLoginRequest, approve_user(), CarrierOverrideRequest, CarrierSwitchRequest, Config, create_custom_port_endpoint(), CustomPortRequest (+66 more)

### Community 4 - "auth_routes.py"
Cohesion: 0.06
Nodes (73): clear_session_cookie(), login(), LoginRequest, logout(), AsyncSession, BaseModel, post, Request (+65 more)

### Community 5 - "browser_cleanup.py"
Cohesion: 0.11
Nodes (31): _is_chrome(), _is_playwright_driver(), _kill(), kill_profile_browsers(), _proc_supported(), Cleanup for Chrome browsers and temporary profiles that a failed close leaves…, Kill every automated Chrome and Playwright driver. Only call this when no…, Replace `master_dir` with a copy of `source_dir` (caches and lock files left… (+23 more)

### Community 6 - "SocialWidget.tsx"
Cohesion: 0.16
Nodes (21): ACCENT_COLORS, errorMessage(), relativeTime(), resizeImageToDataUrl(), SocialWidget(), SocialWidgetProps, EMOJI_GROUPS, EmojiPicker() (+13 more)

### Community 7 - "api.ts"
Cohesion: 0.08
Nodes (55): AdminDashboard(), LoginContent(), AdminCarriers(), PROFILE_NAMES, when(), LoginModal(), addCarrierOverride(), addCustomPort() (+47 more)

### Community 8 - "PortManager"
Cohesion: 0.05
Nodes (32): get_countries(), get_port(), get_suggestions(), get, Get list of countries for autocomplete dropdown., Get specific port details by UN/LOCODE., Get port suggestions for autocomplete., search() (+24 more)

### Community 9 - "._parse_offer_response_to_quotes"
Cohesion: 0.13
Nodes (9): Any, AsyncClient, Constructs OpenAPI compliant OfferRequest payload., Queries Hapag-Lloyd DCSA Commercial Schedules API (v1.0.2) to retrieve point-…, Correlates an offer from the Prices API to a physical solution in DCSA…, Maps a Prices API rate onto the categories the portal scraper produces (freight…, Leg locations are UnLocation/Facility objects per the spec; tolerate plain…, Renders a graduated weight tier (e.g. Heavy Lift: 18-99 TON) in the portal's… (+1 more)

### Community 10 - "CMAConnector"
Cohesion: 0.07
Nodes (19): CMAConnector, Ensures 'Ramp' is explicitly selected under 'Type of location' toggle buttons…, Scans for Route, POL (Port of Loading), or POD (Port of Discharge) dropdown…, Clears the currently selected Destination port tag/card, re-types the locode,…, Dynamically extracts any recommended 5-letter POD LOCODE mentioned in the…, Detects if CMA CGM displayed an advisory banner message: "Looking for AEJEA or…, Handles the 'Customer account' -> 'Role (you are acting as)' dropdown on CMA…, Repeatedly clicks 'More results' if visible to load ALL quotes on the page. (+11 more)

### Community 11 - "env.py"
Cohesion: 0.10
Nodes (22): alembic, get_sync_url(), run_migrations_offline(), run_migrations_online(), _get_database_url(), Quote, QuoteCharge, SQLAlchemy models for quotes and individual charge line items. (+14 more)

### Community 12 - "maersk_connector.py"
Cohesion: 0.09
Nodes (28): extract_locode_and_country(), prepare_maersk_query(), Maersk Browser Connector — Playwright automation using your real Google Chrome…, Fills an autocomplete field using the proven original element-level…, Extracts LOCODE and country name from text like 'CASABLANCA, MOROCCO (MACAS)'…, # NOTE: Bright Data Web Unlocker proxies break Playwright browser sessions…, Maps standard container search codes (e.g. 'DRY 20', '20GP') to Maersk Spot…, Scores a Maersk autocomplete dropdown suggestion. NOTE: The nested/indented… (+20 more)

### Community 13 - "test_hapag_freetime.py"
Cohesion: 0.18
Nodes (16): _apply_freetime_to_quote(), freetime_days(), match_freetime_entry(), Any, Destination free time from config/hapag_freetime.json, shared by the Hapag-…, Days for this container from a table entry ({"20GP": n, "40GP": n} or a bare…, The table entry whose country name appears in `text` as whole words. Whole…, days() (+8 more)

### Community 14 - "RateSearchRequest"
Cohesion: 0.05
Nodes (41): OOCLConnector, parse_oocl_date(), Serves one container-type cycle from the cached merged quote set: -…, One crawl serves all container-type cycles (cached), combining: 1. Sailing…, Attempts to automatically click the Cloudflare Turnstile 'Verify you are human'…, Public oocl.com Chromium sailing schedule crawl bypassed per directive. All…, RateSearchRequest, CMA CGM end-to-end test — login + search + extract quotes. (+33 more)

### Community 15 - "test_hapag_api_connector.py"
Cohesion: 0.22
Nodes (12): get_connector(), Get the appropriate connector for a carrier. If USE_MOCK_CARRIERS=true: returns…, main(), Standalone Test & Verification Suite for Hapag-Lloyd Prices REST API Connector.…, test_dcsa_commercial_schedules_cross_validation(), test_locode_resolution(), test_origin_landfreight_inclusion(), test_payload_generation() (+4 more)

### Community 16 - "preferences.ts"
Cohesion: 0.08
Nodes (35): nextConfig, LaunchIntro(), SearchHistoryItem, derive(), Derived, startOfDay(), UsageStats(), ChoiceCard() (+27 more)

### Community 17 - "test_rfq_agent.py"
Cohesion: 0.11
Nodes (26): asyncio, Unit tests for the Gemini AI RFQ Agent service (parse_rfq). Includes…, Test Image 2: Air rate request generates 3 drafts to Glenn (AWOT), Jing Hui…, Test Image 4: Steel Plate ex Pasir Gudang / Tanjung Pelepas for 20' & 40'., Test Guardrail: Detects LCL request., Test OpenFlights 6,072 IATA airport dataset and shorthand alias resolution., Test Pak Shaun email: "Hi team, need rate for 10x20GP from PK to JKT. Urgent…, Test Multimodal Image Input validation and parsing. (+18 more)

### Community 18 - "re"
Cohesion: 0.07
Nodes (12): AI Browser Agent — Vision-based browser automation using Gemini Flash. This…, parse_hapag_pdf(), scrape_hapag_freetime(), check_and_wait_for_captcha(), login(), main(), base64, google (+4 more)

### Community 19 - "tunnel_relay/main.py"
Cohesion: 0.25
Nodes (8): api_route, fastapi_middleware_cors, health(), get, Request, websocket, relay_request(), websocket_endpoint()

### Community 20 - "._verify_price_owner_selected"
Cohesion: 0.25
Nodes (7): Verifies the "I am the price owner" radio is genuinely checked, piercing shadow…, [2026-07-03] — OOCL FreightSmart Autoclear, Hapag Price Leak & Redirect fixes, Maersk Cache Scoping, Dallas Overrides, Hapag-Lloyd — Price Leaks, Column Matching, and Redirect Recovery, Maersk — 0.0-USD / "Not Open" Card Flakiness (the "Quotes Found but Empty Excel" root causes), Maersk — Caching Scope & Selector Tuning, OOCL — FreightSmart Popup Dismissals & Input Lock Serialization, Ports — Hardcoded Dallas Override

### Community 21 - "GreenXConnector"
Cohesion: 0.08
Nodes (14): GreenXConnector, date, Overrides base search runner to query all 3 sizes at once and cache the…, Type a LOCODE into the autocomplete field and click the first visible dropdown…, Find quantity input next to or below label_text and fill it., Find the exact individual quote card container row encompassing dates, rates,…, Dismiss any cookie/alert modal that would intercept pointer events., Splits a single raw multi-container quote card into multiple QuoteSchema… (+6 more)

### Community 22 - "social_routes.py"
Cohesion: 0.11
Nodes (30): get_current_user(), Dependency that strictly requires an authenticated active member., get_conversation(), list_colleagues(), poke_colleague(), PokeRequest, AsyncSession, BaseModel (+22 more)

### Community 23 - "ChargeCategory"
Cohesion: 0.20
Nodes (21): ChargeCategory, classify_charge(), Charge Classifier — rule-based classification of freight charge line items.…, Classify a charge line item based on its name, amount, section heading, and…, Tests for charge classifier., test_basic_ocean_freight(), test_cwx_heavy_weight_charge(), test_destination_charges() (+13 more)

### Community 24 - "backend/main.py"
Cohesion: 0.14
Nodes (15): health(), get, Infreight Ocean Carrier Rate Automation — FastAPI Application. Main entry point…, Check if the VNC viewer is available (production only, where Xvfb runs)., vnc_status(), profile_base_dirs(), purge_carrier_profile(), Where connectors keep chrome_profile_* folders (see each connector's… (+7 more)

### Community 25 - "rate_search_routes.py"
Cohesion: 0.06
Nodes (58): _load_memory(), Selector Memory — stores and retrieves human-approved selector patches., Loads memory JSON file. Returns empty dict if file is missing or invalid., Saves memory dict back to JSON file., Stores an approved replacement selector., Marks any proposed selector for this step as REJECTED., reject_selector(), save_approved_selector() (+50 more)

### Community 26 - "MSCConnector"
Cohesion: 0.13
Nodes (12): format_to_iso_date(), MSCConnector, Playwright-based automation for MSC (Mediterranean Shipping Company)., Handles the MSC login flow., Clicks Instant Quote, fills form, clicks Search., Detects and clicks the 'Ramp' delivery/haulage option if MSC displays Ramp /…, Parse '14 Jun 2026' to 'YYYY-MM-DD, main() (+4 more)

### Community 27 - "rfq_agent.py"
Cohesion: 0.12
Nodes (22): _call_native_gemini_api(), _detect_booking_confirmation(), _detect_dual_mode_enquiry(), _detect_mode_by_hierarchy(), _detect_unsupported_cargo(), _extract_20gp_weight_priority(), generate_dual_air_drafts(), _load_airport_aliases_config() (+14 more)

### Community 28 - "HapagLloydAPIConnector"
Cohesion: 0.13
Nodes (6): HapagLloydAPIConnector, Direct REST API connector for Hapag-Lloyd Prices API v2.1.4., API connectors do not require browser login sessions., No browser session to reset between batch routes., Resolves a free-text port name or string (e.g. 'Singapore', 'Hamburg, Germany…, Hapag-Lloyd Prices API requires earliestDepartureDate to be at least 4 calendar…

### Community 29 - "AIBrowserAgent"
Cohesion: 0.12
Nodes (16): AIBrowserAgent, Capture the current page as a PNG screenshot., Build the prompt with task description and action history., Parse Gemini's response into an action dict., Call Gemini API with exponential backoff retry., Execute a parsed action on the browser page., Detect if the agent is stuck repeating the same action., Find all visible interactive elements and format them as a prompt guide. (+8 more)

### Community 30 - "CarrierSearchResult"
Cohesion: 0.07
Nodes (41): Base, CarrierSearchResult, SQLAlchemy models for rate searches and carrier search results., Tracks the result of searching a specific carrier for a rate search., A worker machine (e.g. the office laptop) that runs some carriers' searches., WorkerHeartbeat, Copy the connector's "port not found" note onto the result row, if it made one., _store_port_not_found() (+33 more)

### Community 31 - "ONEConnector"
Cohesion: 0.12
Nodes (9): ONEConnector, date, Parses ONE QUOTE Free Time popover text for DESTINATION ONLY. Ignores Origin…, Splits a single raw multi-container quote card into multiple QuoteSchema…, Tries to click a matching option from ONE's visible dropdown. Returns True only…, test_one_free_time_parser_origin_only_ignored(), test_one_free_time_parser_test_a(), test_one_free_time_parser_test_b() (+1 more)

### Community 32 - "_Page"
Cohesion: 0.07
Nodes (19): _is_logged_in_url(), Small aimless pointer drift, as a person does while a page loads., Clicks an element with pre-click and post-click human-like reaction pauses., Maersk's "You are authenticated / Continue as <name>" page: the account is…, Wait until the login page either redirects to a signed-in page or shows its…, True once Maersk has moved past the login pages to a signed-in page., Types text character by character into a given locator or element handle with…, Visible page size, read from the page. (+11 more)

### Community 33 - "Engineering Report: Sourcing Portal Enhancements & Scraping Pipeline Stability"
Cohesion: 0.08
Nodes (23): 1. Anti-Bot Mitigation & CAPTCHA Human-in-the-Loop Recovery, 2. Sourcing Parallelization & Surcharges Optimization, 3. Autocomplete Intelligence & Location Mapping, 4. Scraper Pipeline Maintenance, 5. Infrastructure & DevSecOps Enhancements, Business Value, Business Value, Business Value (+15 more)

### Community 34 - "Changelog"
Cohesion: 0.12
Nodes (15): [2026-05-20 – 2026-05-22] — Port Resolution & Frontend Improvements, [2026-05-31] — Multi-Instance Support & Charge Classification, [2026-07-03] — Robustness Review & Multi-Port Quick Search Fixes, [2026-07-08] — OOCL E-Quote Calendar Navigation, cheapest E-Spot selection, and E-Quote/E-Spot isolation refinements, [2026-07-09] — Hapag-Lloyd Quick Quotes pairing and selection simplification, Batch (168-route) Execution — Isolation, Lock Scope, Polling, Changelog, Charge Classification Improvements (+7 more)

### Community 35 - "admin/page.tsx"
Cohesion: 0.06
Nodes (50): UserRecord, AdminAnalytics, AdminOverview(), AdminOverviewProps, AdminOverviewUser, AnalyticsRange, Attention, attentionItems() (+42 more)

### Community 36 - "package.json"
Cohesion: 0.12
Nodes (15): engines, node, name, packageManager, private, version, react-dom, tailwind-merge (+7 more)

### Community 37 - "carrier_switches.py"
Cohesion: 0.35
Nodes (10): get_switches(), off_message(), _path(), Admin on/off switch per carrier, for when a carrier's site is down or under…, Every switchable carrier: {"enabled", "reason", "updated_by", "updated_at"}; on…, The message for a switched-off carrier's result, or None when it is on., _read(), set_switch() (+2 more)

### Community 38 - "RateResults.tsx"
Cohesion: 0.08
Nodes (50): LiveSearchProgressProps, QuoteBreakdownDrawer(), QuoteBreakdownDrawerProps, Breakdown(), ChargeList(), dateValue(), freeTimeText(), isSoldOut() (+42 more)

### Community 39 - "SearchQueueManager"
Cohesion: 0.12
Nodes (11): Lock, Marks a search as completed internally so we can track the auto-release timeout., Called periodically in a background task to check if the user has held the lock…, Forcefully clears all queued searches and the active lock. Useful for…, Returns or creates an asyncio.Lock for a specific carrier code to prevent…, Adds a search to the queue and waits until it becomes the active search. Event-…, Singleton manager to enforce a FIFO queue for rate searches. Since web scraping…, Returns the current position of the search in the queue. 0 means it is the… (+3 more)

### Community 40 - "job_service.py"
Cohesion: 0.12
Nodes (25): close_all_active_connectors(), Force close all active carrier connectors and their Playwright Chrome windows., SearchStatus, Delete per-search profile copies ("chrome_profile_<carrier>_tmp_<id>") and…, remove_stale_temp_profiles(), cancel_all_active_searches(), cleanup_browsers_if_idle(), UUID (+17 more)

### Community 41 - "app/page.tsx"
Cohesion: 0.09
Nodes (40): 6. Known limitations / candidate follow-ups, HomeContent(), AppHeader(), AppHeaderProps, initials(), systemStatus(), BackendConfigModal(), BackendConfigModalProps (+32 more)

### Community 42 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 43 - "._fs_dismiss_modals"
Cohesion: 0.07
Nodes (24): _dismiss_once(), _click_date_strip_item(), _open_calendar(), _parse_date(), Event, Lock, Parses one FreightSmart result card's inner text into a raw row dict. Text-…, Opens the Details dialog for a card, clicks the Charge Breakdown tab, extracts… (+16 more)

### Community 44 - "test_carrier_timeout.py"
Cohesion: 0.19
Nodes (10): CrashingConnector, HangingConnector, asyncio, A carrier whose browser hangs must be stopped after CARRIER_SEARCH_TIMEOUT_SEC…, Hangs on the sizes in `hang_on`; answers NO_QUOTES_AVAILABLE for the rest., Like a real connector whose tab dies: reports a crash, then never returns., _run(), test_crashed_tab_stops_the_carrier_without_waiting_for_the_timeout() (+2 more)

### Community 46 - "dithered-logo.tsx"
Cohesion: 0.19
Nodes (15): applyMaskInversion(), buildRoundedMask(), DEFAULTS, DitherConfig, DitheredLogo(), DitheredLogoProps, drawParticles(), errorDiffusionDither() (+7 more)

### Community 47 - "👥 The 5 Agent Roles"
Cohesion: 0.13
Nodes (14): 1. Intake Agent (Email Listener), 2. Sourcing Orchestrator (The Coordinator), 3. Sourcing & Scraping Agent (Rates Engine), 4. Finance & Costing Agent (Excel Compiler), 5. Email Draft Agent (Communicator), 📋 Executive Summary, 🛠️ Implementation Stages, Phase 1: Email Integration (Week 1-2) (+6 more)

### Community 48 - "HapagLloydConnector"
Cohesion: 0.12
Nodes (13): HapagLloydConnector, Fuzzy match quote ETD with crawled schedules within a window of +/- 2 days., Performs a single modal dismissal check and attempt., inspect(), check(), test_mapping(), test(), asyncio (+5 more)

### Community 49 - "[2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning"
Cohesion: 0.12
Nodes (13): Detects the Microsoft B2C identity/OAuth login page. Hapag can silently bounce…, clean_vessel_name(), get_booking_start_date(), date, Applies the business rules and pairs FreightSmart prices with crawled…, [2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning, GreenX — "No Quotes" Reported While Quotes Visibly Loaded in VNC, Hapag-Lloyd — Configurable Pacing & Redundant-Wait Removal (+5 more)

### Community 50 - "[2026-06-03] — CMA CGM Routing & Free Time Extraction"
Cohesion: 0.50
Nodes (4): [2026-06-03] — CMA CGM Routing & Free Time Extraction, CMA CGM — Import Free Time from D&D Tab, CMA CGM — Routing Detection (Direct vs Transit), Maersk — Free Time Extraction from Card Text

### Community 51 - "carrier_sessions.py"
Cohesion: 0.08
Nodes (29): maersk_proxy_settings(), Load the saved login an admin uploaded (Admin > Carriers on / off) into this…, Proxy for the Maersk browser, from environment variables, or None. Any…, clean_storage_state(), delete_session(), load_session(), _on_domain(), _path() (+21 more)

### Community 52 - "LiveSearchProgress.tsx"
Cohesion: 0.09
Nodes (29): ChatWidget(), ChatWidgetProps, Message, ACTION_STATUSES, ChipModel, describe(), EMPTY_STATUSES, formatElapsed() (+21 more)

### Community 53 - "types.ts"
Cohesion: 0.09
Nodes (33): CarrierMultiSelect(), CarrierMultiSelectProps, isAllCarriers(), toggleAllCarriers(), toggleCarrierSelection(), RateSearchFormProps, DEMO_EXAMPLES, RfqInputSectionProps (+25 more)

### Community 54 - "🚢 Infreight Sourcing & Ocean Rate Automation System"
Cohesion: 0.14
Nodes (13): 1. Multi-Carrier Automation Engine, 2. Intelligent Surcharge & Charge Classifier Engine (`charge_classifier.py`), 3. Container Comparison Matrix & Excel Export Engine, 🚢 Infreight Sourcing & Ocean Rate Automation System, 🌟 Key Capabilities, 📄 License & Confidentiality, Prerequisites, 🛠️ Project Structure (+5 more)

### Community 55 - "QuoteSchema"
Cohesion: 0.04
Nodes (30): Normalize extracted data into a QuoteSchema using the normalizer. Args:…, MaerskConnector, Execute the full search flow with Progressive Lazy Loading: 1. Login 2. Search…, Extracts freetime, demurrage, and detention from the 'Import D&D fees' tab…, Extracts the routing details from the 'Route & other details' accordion.…, Splits a single raw multi-container quote card into multiple QuoteSchema…, Extracts the port/city name by removing any UN/LOCODE parentheses (e.g.,…, _generate_maersk_mock_quotes() (+22 more)

### Community 56 - "[2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split"
Cohesion: 0.15
Nodes (13): G2 Stress Test: "Hi, Please book the below as per your quote ref INF-2026-0842:…, H1 Stress Test: Table with 2 distinct rows: Row 1: POL Singapore, POD Jakarta,…, test_g2_booking_confirmation_guardrail(), test_h1_table_deduplication_two_pairs(), [2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split, Booking Confirmation / Instructions Intercept Guardrail G2 (`rfq_agent.py` & `RfqInputSection.tsx`), Commercial Sales Desk Intelligence (`sales_notes`), Deterministic Port Alias Resolver (`ports_aliases.json`) (+5 more)

### Community 57 - ".run_full_search"
Cohesion: 0.17
Nodes (3): Normalize various date formats (e.g. 2026-05-31, 31.05.2026, 31 May 2026, 31…, Parses Hapag-Lloyd left search/summary panel for: - PoD (Port of Discharge),…, Normalize raw Hapag-Lloyd quotes into unified QuoteSchema.

### Community 58 - "🛠 Detailed Carrier Log"
Cohesion: 0.15
Nodes (12): 🛠 Detailed Carrier Log, 🟢 GreenX, 🟠 Hapag-Lloyd, Infreight Ocean Carrier Rate Automation — Development Log, 🚀 Key Highlights & Architectural Changes, 🔌 Local Laptop Deployment (Self-Hosted Worker), 🔵 Maersk, 💗 ONE (Ocean Network Express) (+4 more)

### Community 59 - "._dismiss_hapag_modals"
Cohesion: 0.26
Nodes (6): Robustly selects options from Hapag-Lloyd custom dropdown lists. Types the…, Guards against the session-expiry-mid-crawl failure mode: the existing redirect…, Crawls Hapag-Lloyd sailing schedules from the Schedule tab., Dismisses any obscuring modal popups (including multi-step tutorial dialogs)., Ensures the browser is actively on the Quick Quote form (SPA)., Checks if Hapag-Lloyd API Gateway has returned 'This service is currently…

### Community 60 - "test_panama_canal_surcharge.py"
Cohesion: 0.18
Nodes (11): Sort container types in standard order: DRY 20 (20GP) -> DRY 40 (40GP) -> DRY…, sort_container_types(), asyncio, Verify charge_classifier classifies Panama Canal Surcharge as…, Verify regex extraction of Estimated Transportation Days from Hapag-Lloyd modal…, Verify OOCL normalize_result incorporates Panama Canal Surcharge (PCS)., test_charge_classifier_panama_canal_surcharge(), test_container_types_standard_ordering() (+3 more)

### Community 61 - "[2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control"
Cohesion: 0.40
Nodes (5): [2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control, Concurrency Limit Queue & Admin Control Panel, MSC — Mediterranean Shipping Company Connector Implementation, ONE — Inbound Free Time Swap & Scraper Upgrade, OOCL — Orient Overseas Container Line Connector Implementation

### Community 62 - "[2026-06-30] — ONE Multi-Container & Sold-Out, GreenX Surcharge Intake, Free-Time Fixes, Maersk Diagnosis"
Cohesion: 0.29
Nodes (7): [2026-06-30] — ONE Multi-Container & Sold-Out, GreenX Surcharge Intake, Free-Time Fixes, Maersk Diagnosis, GreenX — Only Basic Ocean Freight & LSS Folded Into Final Value, MAERSK — "Quotes Found" but Empty Excel (Diagnosis), ONE — All-Container-Type Search Returning 0 Quotes, ONE — Multi-Container Breakdown Triple-Counted / Inflated Final Value, ONE — Sold-Out ("Notify Me") Sailings Appearing as Quotes, Performance/Reliability — Stop Copying Chrome Caches During Profile Clone/Sync

### Community 63 - "[2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup"
Cohesion: 0.22
Nodes (8): [2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup, Chromium Cache Auto-Cleanup (Railway Storage Bloat Prevention), CMA CGM — 30-Second Timeout on Sold Out Cards, CMA CGM — Free Time Regex Too Strict, CMA CGM — Routing Regex Not Matching "via LEKKI, LA, NG", Excel Export — Routing & Free Time Columns Always Empty, Excel Export — Sold Out Rows Not Showing, Maersk — Hardcoded Port Overrides

### Community 64 - "orbit-card-stack.tsx"
Cohesion: 0.22
Nodes (13): HalftoneAvatar(), HalftoneAvatarProps, hashSeed(), pick(), clamp(), initialsFor(), laneLabel(), OrbitCardStack() (+5 more)

### Community 65 - "Scraper Robustness Review — July 2026"
Cohesion: 0.33
Nodes (5): 1. What was measured, 3. Multi-port quick search — defects found and fixed, 4. Ranked recommendations, 5. Verification of this change, Scraper Robustness Review — July 2026

### Community 66 - "GreenX — Surcharge Intake Fix (2026-06-30)"
Cohesion: 0.22
Nodes (8): Charges that must be taken into the final value (USD only), Files changed, Fix, GreenX — Surcharge Intake Fix (2026-06-30), Per-B/L charges (billed once per booking, added in full to *each* container type), Problem, Root cause, Verification

### Community 67 - "Admin Page & Port Prioritization Guide"
Cohesion: 0.25
Nodes (7): 1. Popular Ports (UN/LOCODEs), 2. Boosted Countries, Admin Page & Port Prioritization Guide, 🔒 How to Access the Admin Page, ⚙️ How to Use Port Prioritization, ⚡ Important Notes, 📝 Step-by-Step Example

### Community 68 - "parse_msc_modal_charges"
Cohesion: 0.24
Nodes (8): parse_msc_modal_charges(), Parses charges from MSC BreakdownModal text. Correctly includes charges whose…, Test MSC charges parsing for Singapore to Conakry, Guinea (40GP). Charges with…, Test when only some surcharges have the payment condition., test_msc_charges_mixed_conditions(), test_msc_charges_singapore_to_conakry_guinea(), Verify MSC charge extraction logic parses Panama Canal Surcharge properly., test_msc_charge_extraction_logic()

### Community 69 - "test_self_healing.py"
Cohesion: 0.08
Nodes (38): _local_fuzzy_repair(), AI Repair Agent — diagnoses Playwright step failures and suggests selector…, A local rule-based heuristic to locate reasonable buttons or inputs when Gemini…, Analyzes the failure context and DOM content to suggest a selector repair. Uses…, suggest_fix(), capture_failure_context(), Exception, Failure Detector — parses and structures error context from failed Playwright… (+30 more)

### Community 70 - "schemas.py"
Cohesion: 0.10
Nodes (22): argparse, Base Carrier Connector — abstract base class for all carrier connectors. Each…, Normalize CMA CGM data into QuoteSchema. Rule: include BASIC_OCEAN_FREIGHT and…, GreenX (Evergreen) Live Connector - Playwright automation., Hapag-Lloyd Prices API Connector (REST API v2.1.4). Provides real-time rate…, OOCL Live Connector â€” Playwright automation for Sailing Schedules., Carrier Registry — factory for getting the right connector per carrier. When…, ChargeSchema (+14 more)

### Community 71 - "RFQParseResult"
Cohesion: 0.25
Nodes (8): parse_rfq_endpoint(), post, API routes for RFQ parsing agent., Parse a free-text RFQ email or message into a structured RateSearchRequest…, RFQParseRequest, RFQParseResult, Test scenario with 3 container types with individual quantities and weights:…, test_multi_container_types_and_20gp_overweight_priority()

### Community 72 - "deploy"
Cohesion: 0.25
Nodes (7): build, builder, deploy, restartPolicyMaxRetries, restartPolicyType, startCommand, $schema

### Community 73 - "Frontend Redesign — Componentry Design System, Workspace & Launch Intro (2026-09-07)"
Cohesion: 0.14
Nodes (13): 1. Design system foundation (`082b43a`), 2. Bugs found and fixed during the restyle, 3. Workspace + launch intro (`21ade75`), 4. Follow-up fixes (`2f9d92b`), 5. Verification, 7. Conventions to follow from here, Dependencies added (5, all small, no runtime lib dependency on Componentry), Frontend Redesign — Componentry Design System, Workspace & Launch Intro (2026-09-07) (+5 more)

### Community 74 - "revoke_user_sessions"
Cohesion: 0.33
Nodes (6): PasswordResetRequest, Admin-directed password reset. Sets new password and immediately revokes all…, reset_user_password(), UUID, Revoke all sessions belonging to a user (used on disable, delete, or password…, revoke_user_sessions()

### Community 75 - "Summary of Changes — July 20, 2026"
Cohesion: 0.29
Nodes (6): 1. AI RFQ Front Door & Air Freight Support (Phase A), 2. Multi-Origin & Gappy List Parsing for Sea RFQs (Phase B), 3. Search Form Streamlining (Form Input Restrictions), 4. Native Gemini 2.5 Flash API & Chatbot Resiliency, 5. Verification & Test Suite, Summary of Changes — July 20, 2026

### Community 76 - "silk-aurora.tsx"
Cohesion: 0.19
Nodes (9): hexToRgb01(), sanitizeHexColor(), SilkAurora(), SilkAuroraProps, WebGLErrorBoundary, WebGLErrorBoundaryProps, WebGLErrorBoundaryState, WebGLFallback() (+1 more)

### Community 77 - "[2026-05-29 – 2026-05-30] — Hapag-Lloyd Full Integration"
Cohesion: 0.40
Nodes (5): [2026-05-29 – 2026-05-30] — Hapag-Lloyd Full Integration, Hapag-Lloyd — Dropdown Autocomplete Issues, Hapag-Lloyd — Live Connector Implementation, Hapag-Lloyd — Onboarding Modal Blocking Form Interaction, Hapag-Lloyd — Search Button Selector Failures

### Community 78 - "resolve_port_alias"
Cohesion: 0.33
Nodes (6): _load_port_aliases_config(), Deterministically resolves a port string against ports_aliases.json and the…, resolve_port_alias(), Test that resolve_port_alias cleans 'City, Country' and parenthetical notes to…, test_resolve_city_country_format_to_clean_database_port_name(), Clean Search Dropdown Port Name Resolution (`rfq_agent.py` & `port_manager.py`)

### Community 79 - "test_brightdata.py"
Cohesion: 0.40
Nodes (5): get_title(), Script to test fetching CMA CGM pricing page using Bright Data Web Access HTTP…, test_brightdata_api(), urllib_error, urllib_request

### Community 81 - "Design system — read before touching any UI"
Cohesion: 0.33
Nodes (5): Animation rules, Client-only preferences, Design system — read before touching any UI, This is NOT the Next.js you know, Use tokens, not raw colours

### Community 82 - "[2026-05-18 – 2026-05-19] — Railway Deployment & Docker"
Cohesion: 0.67
Nodes (3): [2026-05-18 – 2026-05-19] — Railway Deployment & Docker, Persistent Chrome Profiles on Railway Volume, Railway Deployment Setup

### Community 83 - "layout.tsx"
Cohesion: 0.22
Nodes (7): frontend_src_app_globals, instrumentSans, inter, metadata, viewport, ThemeProvider(), next-themes

### Community 84 - "test_one_premium_override.py"
Cohesion: 0.40
Nodes (3): MockCard, Unit test for ONE connector and charge classifier Premium Cargo Service…, test_premium_cargo_service_override()

### Community 85 - "Infreight Sourcing Automation — Run Audit (30 Jul 2026)"
Cohesion: 0.33
Nodes (5): Expected on this machine (not automation faults), Faults (correctness), Inefficiencies (speed), Infreight Sourcing Automation — Run Audit (30 Jul 2026), Suggested priority

### Community 86 - "[2026-06-02] — Hapag-Lloyd Transshipment & Duplicate Fix"
Cohesion: 0.67
Nodes (3): [2026-06-02] — Hapag-Lloyd Transshipment & Duplicate Fix, Hapag-Lloyd — Duplicate Sailings from Transshipment Vessels, Hapag-Lloyd — Routing Not Marked as Transit

### Community 88 - "[2026-05-23 – 2026-05-24] — Maersk Shadow DOM & Stealth Upgrades"
Cohesion: 0.50
Nodes (4): [2026-05-23 – 2026-05-24] — Maersk Shadow DOM & Stealth Upgrades, Maersk — 2FA/CAPTCHA Human-in-the-Loop via noVNC, Maersk — Login Credential Autofill Corruption, Maersk — Shadow DOM Piercing for MDS Web Components

### Community 89 - "dependencies"
Cohesion: 0.15
Nodes (13): dependencies, class-variance-authority, clsx, exceljs, lucide-react, next, next-themes, @radix-ui/react-slot (+5 more)

### Community 90 - "parse_rfq"
Cohesion: 0.20
Nodes (9): parse_rfq(), Parses free-text or multimodal screenshot RFQ into structured RFQParseResult…, Test Guardrail: Detects Reefer container request and returns unsupported_cargo…, Test 40RF / temperature / frozen seafood reefer guardrail: "Please quote 1 x…, Test Image 1: EXW airfreight rates with lithium batteries PI 970 & HS code…, test_air_rfq_image1_lithium_batteries_compliance(), test_reefer_40rf_temperature_unsupported_equipment_guardrail(), test_unsupported_reefer_equipment_guardrail() (+1 more)

### Community 91 - "test_excel_exports.js"
Cohesion: 0.33
Nodes (6): ref_fs, assert(), ExcelJS, fs, mockBatchResults, testTariffExport()

### Community 92 - "websockify_carrier_proxy"
Cohesion: 0.22
Nodes (5): websocket, Proxy WebSocket connections to legacy local x11vnc at localhost:5900., Proxy WebSocket connections to specific carrier x11vnc servers., websockify_carrier_proxy(), websockify_proxy()

### Community 93 - "[2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History"
Cohesion: 0.40
Nodes (5): [2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History, Admin User Search History & SGT GMT+8 Conversion (`AdminDashboard.tsx`), GreenX (Evergreen) Card Isolation & Surcharge Parsing (`greenx_connector.py`), Multi-Route Batch Execution Engine (`batch_engine.py`), OOCL FreightSmart 28-Day Calendar Expansion (`oocl_connector.py`)

### Community 95 - "devDependencies"
Cohesion: 0.22
Nodes (9): devDependencies, eslint, eslint-config-next, tailwindcss, @tailwindcss/postcss, @types/node, @types/react, @types/react-dom (+1 more)

### Community 96 - "frontend/README.md"
Cohesion: 0.50
Nodes (3): Deploy on Vercel, Getting Started, Learn More

### Community 98 - "get_me"
Cohesion: 0.67
Nodes (3): get_me(), get, Get profile of currently signed-in user.

### Community 99 - "os"
Cohesion: 0.04
Nodes (51): asyncio, Page Observer — captures page state (screenshot, DOM, visible text) on failure., CMA CGM Live Connector — Playwright automation. Credentials read from env:…, # NOTE: No start date fill needed — schedule page defaults to today,, Hapag-Lloyd Live Connector -- Playwright automation. Credentials read from env:…, dump_options(), main(), Diagnostic: dump ALL dropdown options (text + innerHTML) when typing 'DEHAM'… (+43 more)

### Community 102 - "._wait_for_captcha_resolution"
Cohesion: 0.33
Nodes (4): Best-effort automated CAPTCHA/Turnstile clearing, tried BEFORE escalating to a…, Locate the Cloudflare Turnstile / challenge widget and click its checkbox using…, Helper that pauses execution if a CAPTCHA challenge is detected, and waits up…, Hapag-Lloyd — Best-Effort Automated CAPTCHA Clear + Per-Sailing Speedup

### Community 106 - "[2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes"
Cohesion: 0.50
Nodes (4): [2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes, CMA CGM — Chrome Profile Bypass, ONE — Date Formatting & Charge Breakdown Pollution, ONE — Date Picker Pre-selection Issue

### Community 108 - "remote_worker.py"
Cohesion: 0.10
Nodes (31): Models package. Note: Individual modules can be imported directly (e.g.,…, _claim_loop(), claim_next(), delegate_and_wait(), heartbeat_once(), _heartbeat_thread(), beat(), is_worker() (+23 more)

### Community 116 - "get_current_user_optional"
Cohesion: 0.40
Nodes (5): get_current_user_optional(), Dependency that returns the current User if valid token is provided, or None., Request, Verify that caller has admin privileges via session cookie, Bearer token, or…, verify_admin_access()

### Community 117 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, dev, lint, start

### Community 121 - "Architecture Overview"
Cohesion: 0.50
Nodes (4): Architecture Overview, Carrier Connector Lifecycle, Charge Classification Rules, Search Flow

### Community 123 - "eslint.config.mjs"
Cohesion: 0.50
Nodes (3): eslintConfig, eslint, eslint-config-next

### Community 124 - "test_normalizer.py"
Cohesion: 0.18
Nodes (16): is_weight_surcharge_applicable(), Evaluates whether a weight-tier or overweight surcharge is applicable for the…, calculate_final_freight_value(), classify_and_organize_charges(), Takes raw charge line items and classifies them. Args: raw_charges: list of…, Calculate the final freight value from a list of classified charges. Args:…, Tests for normalizer / final freight value calculator., test_basic_calculation() (+8 more)

### Community 126 - "[2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash"
Cohesion: 0.40
Nodes (5): [2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash, AI RFQ Front Door & Air Freight Support, Multi-Origin & Gappy List Parsing (Sea RFQs), Native Gemini 2.5 Flash Direct API Integration, Search Form Streamlining

### Community 127 - "pytest"
Cohesion: 0.12
Nodes (12): asyncio, Integration tests for authentication, legacy user password setup, pending…, test_full_auth_lifecycle(), parse_hapag_card_text_mock(), Verify that multi-leg/feeder routes take the final arrival ETA and 28 days TT., Mock implementation of the JS evaluate logic inside hapag_lloyd_connector.py., test_hapag_multi_leg_schedule_extraction(), asyncio (+4 more)

### Community 128 - "HapagServiceUnavailableException"
Cohesion: 0.67
Nodes (3): HapagServiceUnavailableException, Exception, Exception raised when Hapag-Lloyd API Gateway reports service is unavailable.

### Community 131 - "[2026-05-25 – 2026-05-26] — VNC Display Isolation & Proxy Integration"
Cohesion: 0.67
Nodes (3): [2026-05-25 – 2026-05-26] — VNC Display Isolation & Proxy Integration, Bright Data ISP Proxy Integration, VNC Display Isolation for Concurrent Carriers

### Community 132 - "[2026-06-01] — Hapag-Lloyd Sold Out Detection & Date Parsing"
Cohesion: 0.67
Nodes (3): [2026-06-01] — Hapag-Lloyd Sold Out Detection & Date Parsing, Hapag-Lloyd — Date String Standardization, Hapag-Lloyd — Sold Out Schedule Detection

## Knowledge Gaps
- **326 isolated node(s):** `Config`, `install_pi.sh script`, `eslintConfig`, `nextConfig`, `name` (+321 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1005 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **25 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Changelog` connect `Changelog` to `[2026-05-25 – 2026-05-26] — VNC Display Isolation & Proxy Integration`, `[2026-06-01] — Hapag-Lloyd Sold Out Detection & Date Parsing`, `PortManager`, `._verify_price_owner_selected`, `._fs_dismiss_modals`, `[2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning`, `[2026-06-03] — CMA CGM Routing & Free Time Extraction`, `[2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split`, `[2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control`, `[2026-06-30] — ONE Multi-Container & Sold-Out, GreenX Surcharge Intake, Free-Time Fixes, Maersk Diagnosis`, `[2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup`, `[2026-05-29 – 2026-05-30] — Hapag-Lloyd Full Integration`, `[2026-05-18 – 2026-05-19] — Railway Deployment & Docker`, `[2026-06-02] — Hapag-Lloyd Transshipment & Duplicate Fix`, `[2026-05-23 – 2026-05-24] — Maersk Shadow DOM & Stealth Upgrades`, `[2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History`, `[2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes`, `Architecture Overview`, `[2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash`?**
  _High betweenness centrality (0.327) - this node is a cross-community bridge._
- **Why does `[2026-06-03] — CMA CGM Routing & Free Time Extraction` connect `[2026-06-03] — CMA CGM Routing & Free Time Extraction` to `Changelog`?**
  _High betweenness centrality (0.291) - this node is a cross-community bridge._
- **Why does `Maersk — Free Time Extraction from Card Text` connect `[2026-06-03] — CMA CGM Routing & Free Time Extraction` to `RateResults.tsx`?**
  _High betweenness centrality (0.290) - this node is a cross-community bridge._
- **Are the 37 inferred relationships involving `RateSearchRequest` (e.g. with `create_batch_rate_search()` and `create_rate_search()`) actually correct?**
  _`RateSearchRequest` has 37 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `cn()` (e.g. with `Reuse the primitives` and `7. Conventions to follow from here`) actually correct?**
  _`cn()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 23 inferred relationships involving `CarrierResultStatus` (e.g. with `safe_step()` and `update_carrier_status()`) actually correct?**
  _`CarrierResultStatus` has 23 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Config`, `install_pi.sh script`, `eslintConfig` to the rest of the system?**
  _326 weakly-connected nodes found - possible documentation gaps or missing edges._