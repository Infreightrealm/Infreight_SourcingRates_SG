# Graph Report - Infreight_Sourcing_New  (2026-10-16)

## Corpus Check
- 284 files · ~1,192,194 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 27 file(s) not represented in the graph (top: (none) 10, .bat 9, .conf 2)

## Summary
- 2588 nodes · 6369 edges · 137 communities (113 shown, 24 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 378 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `dab33707`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- RateSearchRequest
- CarrierResultStatus
- cn
- user_routes.py
- auth_routes.py
- browser_cleanup.py
- SocialWidget.tsx
- api.ts
- MaerskConnector
- ._parse_offer_response_to_quotes
- CMAConnector
- rate_search.py
- PortManager
- test_hapag_freetime.py
- HapagLloydAPIConnector
- test_auth_routes.py
- preferences.ts
- test_rfq_agent.py
- re
- safe_step.py
- [2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning
- GreenXConnector
- social_routes.py
- ChargeCategory
- backend/main.py
- rate_search_routes.py
- MSCConnector
- parse_rfq
- port_manager.py
- AIBrowserAgent
- CarrierSearchResult
- ONEConnector
- carrier_sessions.py
- Engineering Report: Sourcing Portal Enhancements & Scraping Pipeline Stability
- Changelog
- AdminOverview.tsx
- package.json
- test_carrier_switches.py
- RateResults.tsx
- SearchQueueManager
- job_service.py
- NotAvailableConnector
- compilerOptions
- ._fs_dismiss_modals
- test_carrier_timeout.py
- OOCLConnector
- dithered-logo.tsx
- 👥 The 5 Agent Roles
- HapagLloydConnector
- app/page.tsx
- AdminUsers.tsx
- CurrencyManager
- LiveSearchProgress.tsx
- SearchComposer.tsx
- 🚢 Infreight Sourcing & Ocean Rate Automation System
- ._query_prices_api
- [2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split
- .search_quotes
- 🛠 Detailed Carrier Log
- _Page
- sort_container_types
- RfqInputSection.tsx
- [2026-06-30] — ONE Multi-Container & Sold-Out, GreenX Surcharge Intake, Free-Time Fixes, Maersk Diagnosis
- [2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup
- orbit-card-stack.tsx
- ._split_or_none
- GreenX — Surcharge Intake Fix (2026-06-30)
- Admin Page & Port Prioritization Guide
- test_self_healing.py
- selector_memory.py
- QuoteSchema
- parse_rfq_endpoint
- deploy
- Frontend Redesign — Componentry Design System, Workspace & Launch Intro (2026-09-07)
- .extract_charge_breakdown
- Summary of Changes — July 20, 2026
- silk-aurora.tsx
- [2026-05-29 – 2026-05-30] — Hapag-Lloyd Full Integration
- resolve_port_alias
- test_brightdata.py
- fetch_port_fixes
- Design system — read before touching any UI
- analytics_service.py
- layout.tsx
- port_routes.py
- Infreight Sourcing Automation — Run Audit (30 Jul 2026)
- .filter_cheapest_in_14d_window
- RateLimiter
- [2026-05-23 – 2026-05-24] — Maersk Shadow DOM & Stealth Upgrades
- dependencies
- .search_port
- test_excel_exports.js
- ai_repair_agent.py
- [2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History
- ._parse_free_time_text
- devDependencies
- frontend/README.md
- test_js.js
- get_me
- os
- export_maersk_login.py
- diagnose_greenx_dropdown.py
- resolve_port_for_carrier
- .validate_currency
- Working in this repository
- [2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes
- install_pi.sh
- remote_worker.py
- postcss.config.mjs
- pytest
- [2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash
- scripts
- database.py
- ._lookup_freetime
- Architecture Overview
- e2e_downloaded_multisheet_28ec47f9.md
- test_one_breakdown.py
- [2026-06-03] — CMA CGM Routing & Free Time Extraction
- e2e_downloaded_tariff_d21a0cb7.md
- .get_booking_start_date
- MockCard
- [2026-08-04 - 2026-08-06] — CMA CGM Dynamic RAMP/POD Rerouting, Brand Excel Styling, Port Synonym Matching & Tunnel Relays
- ambiguous_python_import_b35980c0aa01
- [2026-05-25 – 2026-05-26] — VNC Display Isolation & Proxy Integration
- .search_quotes
- [2026-06-02] — Hapag-Lloyd Transshipment & Duplicate Fix
- require_admin
- [2026-05-20 – 2026-05-22] — Port Resolution & Frontend Improvements
- clean_selector_memory

## God Nodes (most connected - your core abstractions)
1. `RateSearchRequest` - 174 edges
2. `cn()` - 89 edges
3. `CarrierResultStatus` - 73 edges
4. `QuoteSchema` - 71 edges
5. `User` - 63 edges
6. `CMAConnector` - 58 edges
7. `PortManager` - 58 edges
8. `HapagLloydConnector` - 56 edges
9. `OOCLConnector` - 56 edges
10. `MaerskConnector` - 55 edges

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

## Communities (137 total, 24 thin omitted)

### Community 0 - "RateSearchRequest"
Cohesion: 0.06
Nodes (36): RateSearchRequest, main(), Test script to run Belawan (IDBLW) -> Aden (YEADE) route on Maersk and MSC., test_maersk(), test_msc(), CMA CGM end-to-end test — login + search + extract quotes., # IMPORTANT: Clear ALL proxy env vars BEFORE any import triggers load_dotenv()…, test_cma() (+28 more)

### Community 1 - "CarrierResultStatus"
Cohesion: 0.06
Nodes (21): Fill in the carrier's search form and submit a quote search. Args: request: The…, Required abstract method implementation; delegates to run_full_search., Batch (RFQ) mode: the base implementation drives a browser page, so answer from…, Called by job_service once per container type (request.container_type). All…, Executes full rate search against Hapag-Lloyd Prices API. Queries each…, _generate_maersk_mock_quotes(), _generate_msc_mock_quotes(), _generate_one_mock_quotes() (+13 more)

### Community 2 - "cn"
Cohesion: 0.09
Nodes (46): Reuse the primitives, 0. The one invariant, New primitives — `frontend/src/components/ui/`, LoadingState(), LoginModalProps, PortAutocomplete(), PortAutocompleteProps, RateSearchForm() (+38 more)

### Community 3 - "user_routes.py"
Cohesion: 0.08
Nodes (72): admin_delete_user(), AdminLoginRequest, approve_user(), CarrierOverrideRequest, CarrierSwitchRequest, Config, create_custom_port_endpoint(), CustomPortRequest (+64 more)

### Community 4 - "auth_routes.py"
Cohesion: 0.06
Nodes (75): clear_session_cookie(), get_current_user_optional(), login(), LoginRequest, logout(), AsyncSession, BaseModel, post (+67 more)

### Community 5 - "browser_cleanup.py"
Cohesion: 0.11
Nodes (33): _is_chrome(), _is_playwright_driver(), _kill(), kill_profile_browsers(), _proc_supported(), Cleanup for Chrome browsers and temporary profiles that a failed close leaves…, Kill every automated Chrome and Playwright driver. Only call this when no…, Delete per-search profile copies ("chrome_profile_<carrier>_tmp_<id>") and… (+25 more)

### Community 6 - "SocialWidget.tsx"
Cohesion: 0.16
Nodes (21): ACCENT_COLORS, errorMessage(), relativeTime(), resizeImageToDataUrl(), SocialWidget(), SocialWidgetProps, EMOJI_GROUPS, EmojiPicker() (+13 more)

### Community 7 - "api.ts"
Cohesion: 0.07
Nodes (72): AdminDashboard(), UserRecord, LoginContent(), HomeContent(), AdminCarriers(), PROFILE_NAMES, when(), AdminPortFixes() (+64 more)

### Community 8 - "MaerskConnector"
Cohesion: 0.07
Nodes (17): MaerskConnector, flatten_tree(), Execute the full search flow with Progressive Lazy Loading: 1. Login 2. Search…, Extracts freetime, demurrage, and detention from the 'Import D&D fees' tab…, Extracts the routing details from the 'Route & other details' accordion.…, Splits a single raw multi-container quote card into multiple QuoteSchema…, Extracts the port/city name by removing any UN/LOCODE parentheses (e.g.,…, main() (+9 more)

### Community 9 - "._parse_offer_response_to_quotes"
Cohesion: 0.18
Nodes (6): Any, Correlates an offer from the Prices API to a physical solution in DCSA…, Maps a Prices API rate onto the categories the portal scraper produces (freight…, Leg locations are UnLocation/Facility objects per the spec; tolerate plain…, Renders a graduated weight tier (e.g. Heavy Lift: 18-99 TON) in the portal's…, Parses Hapag-Lloyd OfferResponse JSON into InFreight QuoteSchema objects,…

### Community 10 - "CMAConnector"
Cohesion: 0.07
Nodes (19): CMAConnector, Ensures 'Ramp' is explicitly selected under 'Type of location' toggle buttons…, Scans for Route, POL (Port of Loading), or POD (Port of Discharge) dropdown…, Clears the currently selected Destination port tag/card, re-types the locode,…, Dynamically extracts any recommended 5-letter POD LOCODE mentioned in the…, Detects if CMA CGM displayed an advisory banner message: "Looking for AEJEA or…, Handles the 'Customer account' -> 'Role (you are acting as)' dropdown on CMA…, Repeatedly clicks 'More results' if visible to load ALL quotes on the page. (+11 more)

### Community 11 - "rate_search.py"
Cohesion: 0.10
Nodes (21): alembic, get_recent_search_status_context(), handle_chat_query(), _local_chatbot_fallback(), Chat Service — manages conversational AI queries from the frontend user using…, Intelligent responder for search status, carrier guidance, air/sea info, and…, Queries the database for the most recent rate search status to give the chatbot…, Sends the chat message and history to native Gemini 2.5 Flash API. If Gemini… (+13 more)

### Community 12 - "PortManager"
Cohesion: 0.11
Nodes (8): PortManager, Where admin-saved port name fixes are kept. Railway rebuilds /app on every…, Retrieve verified carrier port name from persistent cache by UN/LOCODE,…, Cache verified carrier port name and save persistently to…, Clean and normalize user input for port searching., Retrieve port data by full UN/LOCODE (e.g., 'SGSIN')., _user_overrides_path(), test_saved_fixes_live_on_the_persistent_volume()

### Community 13 - "test_hapag_freetime.py"
Cohesion: 0.18
Nodes (16): _apply_freetime_to_quote(), freetime_days(), match_freetime_entry(), Any, Destination free time from config/hapag_freetime.json, shared by the Hapag-…, Days for this container from a table entry ({"20GP": n, "40GP": n} or a bare…, The table entry whose country name appears in `text` as whole words. Whole…, days() (+8 more)

### Community 14 - "HapagLloydAPIConnector"
Cohesion: 0.16
Nodes (12): HapagLloydAPIConnector, Direct REST API connector for Hapag-Lloyd Prices API v2.1.4., API connectors do not require browser login sessions., No browser session to reset between batch routes., main(), Standalone Test & Verification Suite for Hapag-Lloyd Prices REST API Connector.…, test_dcsa_commercial_schedules_cross_validation(), test_locode_resolution() (+4 more)

### Community 15 - "test_auth_routes.py"
Cohesion: 0.33
Nodes (5): asyncio, Integration tests for authentication, legacy user password setup, pending…, test_full_auth_lifecycle(), main, pytest_asyncio

### Community 16 - "preferences.ts"
Cohesion: 0.09
Nodes (33): LaunchIntro(), SearchHistoryItem, derive(), Derived, startOfDay(), UsageStats(), ChoiceCard(), Toggle() (+25 more)

### Community 17 - "test_rfq_agent.py"
Cohesion: 0.10
Nodes (36): API routes for RFQ parsing agent., RFQParseResult, asyncio, Unit tests for the Gemini AI RFQ Agent service (parse_rfq). Includes…, Test Image 2: Air rate request generates 3 drafts to Glenn (AWOT), Jing Hui…, Test Image 4: Steel Plate ex Pasir Gudang / Tanjung Pelepas for 20' & 40'., Test Guardrail: Detects Reefer container request and returns unsupported_cargo…, Test Guardrail: Detects LCL request. (+28 more)

### Community 18 - "re"
Cohesion: 0.09
Nodes (5): check_and_wait_for_captcha(), login(), main(), Unit test for CMA CGM demurrage and detention combined free time parsing logic., re

### Community 19 - "safe_step.py"
Cohesion: 0.15
Nodes (14): capture_failure_context(), Exception, Failure Detector — parses and structures error context from failed Playwright…, Assembles a standardized diagnostic dictionary containing all available details…, capture_page_state(), Page Observer — captures page state (screenshot, DOM, visible text) on failure., Captures screenshot, DOM HTML, and inner text of the current page. Saves…, generate_report() (+6 more)

### Community 20 - "[2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning"
Cohesion: 0.14
Nodes (13): Verifies the "I am the price owner" radio is genuinely checked, piercing shadow…, [2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning, [2026-07-03] — OOCL FreightSmart Autoclear, Hapag Price Leak & Redirect fixes, Maersk Cache Scoping, Dallas Overrides, GreenX — "No Quotes" Reported While Quotes Visibly Loaded in VNC, Hapag-Lloyd — Configurable Pacing & Redundant-Wait Removal, Hapag-Lloyd — Price Leaks, Column Matching, and Redirect Recovery, Job Scheduler — Concurrency Default, Maersk — 0.0-USD / "Not Open" Card Flakiness (the "Quotes Found but Empty Excel" root causes) (+5 more)

### Community 21 - "GreenXConnector"
Cohesion: 0.11
Nodes (9): GreenXConnector, date, Overrides base search runner to query all 3 sizes at once and cache the…, Type a LOCODE into the autocomplete field and click the first visible dropdown…, Find quantity input next to or below label_text and fill it., Find the exact individual quote card container row encompassing dates, rates,…, Dismiss any cookie/alert modal that would intercept pointer events., Splits a single raw multi-container quote card into multiple QuoteSchema… (+1 more)

### Community 22 - "social_routes.py"
Cohesion: 0.12
Nodes (28): get_current_user(), Dependency that strictly requires an authenticated active member., get_conversation(), list_colleagues(), poke_colleague(), PokeRequest, AsyncSession, BaseModel (+20 more)

### Community 23 - "ChargeCategory"
Cohesion: 0.10
Nodes (34): ChargeCategory, classify_charge(), Classify a charge line item based on its name, amount, section heading, and…, calculate_final_freight_value(), Calculate the final freight value from a list of classified charges. Args:…, Tests for charge classifier., test_basic_ocean_freight(), test_cwx_heavy_weight_charge() (+26 more)

### Community 24 - "backend/main.py"
Cohesion: 0.06
Nodes (34): api_route, health(), lifespan(), get, websocket, Infreight Ocean Carrier Rate Automation — FastAPI Application. Main entry point…, Check if the VNC viewer is available (production only, where Xvfb runs)., Proxy WebSocket connections to legacy local x11vnc at localhost:5900. (+26 more)

### Community 25 - "rate_search_routes.py"
Cohesion: 0.07
Nodes (52): approve_repair(), ApproveRepairRequest, carrier_switch_status(), chat_endpoint(), ChatRequest, create_batch_rate_search(), _contains(), _looks_like() (+44 more)

### Community 26 - "MSCConnector"
Cohesion: 0.06
Nodes (31): format_to_iso_date(), is_same_container_type(), map_requested_containers_to_msc_sizes(), MSCConnector, parse_msc_modal_charges(), Parse '14 Jun 2026' to 'YYYY-MM-DD, Map requested container type strings (e.g. '20GP', 'DRY 20', '40HQ', 'DRY 40H')…, Checks whether two container type representations map to the same MSC equipment… (+23 more)

### Community 27 - "parse_rfq"
Cohesion: 0.13
Nodes (25): _call_native_gemini_api(), _detect_booking_confirmation(), _detect_dual_mode_enquiry(), _detect_mode_by_hierarchy(), _detect_unsupported_cargo(), _extract_20gp_weight_priority(), generate_dual_air_drafts(), _load_airport_aliases_config() (+17 more)

### Community 28 - "port_manager.py"
Cohesion: 0.21
Nodes (13): add_carrier_override(), add_custom_port(), delete_carrier_override(), delete_custom_port(), get_carrier_overrides(), get_custom_ports(), get_popular_ports_config(), Suggest top N ports for a partial query. (+5 more)

### Community 29 - "AIBrowserAgent"
Cohesion: 0.13
Nodes (15): AIBrowserAgent, Capture the current page as a PNG screenshot., Build the prompt with task description and action history., Parse Gemini's response into an action dict., Call Gemini API with exponential backoff retry., Execute a parsed action on the browser page., Detect if the agent is stuck repeating the same action., Find all visible interactive elements and format them as a prompt guide. (+7 more)

### Community 30 - "CarrierSearchResult"
Cohesion: 0.08
Nodes (36): Base, CarrierSearchResult, Tracks the result of searching a specific carrier for a rate search., A worker machine (e.g. the office laptop) that runs some carriers' searches., WorkerHeartbeat, Copy the connector's "port not found" note onto the result row, if it made one., _store_port_not_found(), _miss() (+28 more)

### Community 31 - "ONEConnector"
Cohesion: 0.18
Nodes (3): ONEConnector, date, Splits a single raw multi-container quote card into multiple QuoteSchema…

### Community 32 - "carrier_sessions.py"
Cohesion: 0.08
Nodes (29): _is_logged_in_url(), maersk_proxy_settings(), Clicks an element with pre-click and post-click human-like reaction pauses., Maersk's "You are authenticated / Continue as <name>" page: the account is…, Wait until the login page either redirects to a signed-in page or shows its…, True once Maersk has moved past the login pages to a signed-in page., Load the saved login an admin uploaded (Admin > Carriers on / off) into this…, Proxy for the Maersk browser, from environment variables, or None. Any… (+21 more)

### Community 33 - "Engineering Report: Sourcing Portal Enhancements & Scraping Pipeline Stability"
Cohesion: 0.08
Nodes (23): 1. Anti-Bot Mitigation & CAPTCHA Human-in-the-Loop Recovery, 2. Sourcing Parallelization & Surcharges Optimization, 3. Autocomplete Intelligence & Location Mapping, 4. Scraper Pipeline Maintenance, 5. Infrastructure & DevSecOps Enhancements, Business Value, Business Value, Business Value (+15 more)

### Community 34 - "Changelog"
Cohesion: 0.10
Nodes (19): [2026-05-18 – 2026-05-19] — Railway Deployment & Docker, [2026-05-31] — Multi-Instance Support & Charge Classification, [2026-06-01] — Hapag-Lloyd Sold Out Detection & Date Parsing, [2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control, [2026-07-08] — OOCL E-Quote Calendar Navigation, cheapest E-Spot selection, and E-Quote/E-Spot isolation refinements, [2026-07-09] — Hapag-Lloyd Quick Quotes pairing and selection simplification, Changelog, Charge Classification Improvements (+11 more)

### Community 35 - "AdminOverview.tsx"
Cohesion: 0.10
Nodes (24): AdminAnalytics, AdminOverview(), AdminOverviewProps, AdminOverviewUser, AnalyticsRange, Attention, attentionItems(), CARRIER_LABELS (+16 more)

### Community 36 - "package.json"
Cohesion: 0.09
Nodes (20): eslintConfig, nextConfig, engines, node, name, packageManager, private, version (+12 more)

### Community 37 - "test_carrier_switches.py"
Cohesion: 0.21
Nodes (13): get_switches(), off_message(), _path(), Admin on/off switch per carrier, for when a carrier's site is down or under…, Every switchable carrier: {"enabled", "reason", "updated_by", "updated_at"}; on…, The message for a switched-off carrier's result, or None when it is on., _read(), set_switch() (+5 more)

### Community 38 - "RateResults.tsx"
Cohesion: 0.07
Nodes (57): LiveSearchProgressProps, QuoteBreakdownDrawer(), QuoteBreakdownDrawerProps, Breakdown(), ChargeList(), dateValue(), freeTimeText(), isSoldOut() (+49 more)

### Community 39 - "SearchQueueManager"
Cohesion: 0.12
Nodes (11): Lock, Marks a search as completed internally so we can track the auto-release timeout., Called periodically in a background task to check if the user has held the lock…, Forcefully clears all queued searches and the active lock. Useful for…, Returns or creates an asyncio.Lock for a specific carrier code to prevent…, Adds a search to the queue and waits until it becomes the active search. Event-…, Singleton manager to enforce a FIFO queue for rate searches. Since web scraping…, Returns the current position of the search in the queue. 0 means it is the… (+3 more)

### Community 40 - "job_service.py"
Cohesion: 0.10
Nodes (37): Updates the status of a carrier search in the database., update_carrier_status(), create_rate_search(), Create a new rate search and dispatch carrier jobs., close_all_active_connectors(), get_connector(), Get the appropriate connector for a carrier. If USE_MOCK_CARRIERS=true: returns…, Force close all active carrier connectors and their Playwright Chrome windows. (+29 more)

### Community 41 - "NotAvailableConnector"
Cohesion: 0.09
Nodes (15): NotAvailableConnector, Any, Clean up browser resources robustly, ensuring failures or hangs never block…, Best-effort ETD date from a raw card dict (ISO, MM/DD/YYYY)., The card's summary price. NOTE: on multi-container cards this is the SUM across…, Picks the cheapest card in EACH tariff window the customer RFQ sheet needs:…, Quick-mode quote builder shared by every connector and both search paths. Fixes…, Execute the full search flow: 1. Login 2. Search quotes 3. Extract quote list… (+7 more)

### Community 42 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 43 - "._fs_dismiss_modals"
Cohesion: 0.08
Nodes (21): _dismiss_once(), _click_date_strip_item(), _open_calendar(), Event, Lock, Opens the 'Container Type and Quantity' picker (General tab: 20GP/20RF(NOR),…, Iterates through the FreightSmart results date calendar to collect E-Quote and…, Full FreightSmart phase: login â†’ fill quote form â†’ search â†’ extract rows. (+13 more)

### Community 44 - "test_carrier_timeout.py"
Cohesion: 0.19
Nodes (10): CrashingConnector, HangingConnector, asyncio, A carrier whose browser hangs must be stopped after CARRIER_SEARCH_TIMEOUT_SEC…, Hangs on the sizes in `hang_on`; answers NO_QUOTES_AVAILABLE for the rest., Like a real connector whose tab dies: reports a crash, then never returns., _run(), test_crashed_tab_stops_the_carrier_without_waiting_for_the_timeout() (+2 more)

### Community 45 - "OOCLConnector"
Cohesion: 0.05
Nodes (34): clean_vessel_name(), get_booking_start_date(), OOCLConnector, _parse_date(), parse_oocl_date(), date, Parses one FreightSmart result card's inner text into a raw row dict. Text-…, Opens the Details dialog for a card, clicks the Charge Breakdown tab, extracts… (+26 more)

### Community 46 - "dithered-logo.tsx"
Cohesion: 0.19
Nodes (15): applyMaskInversion(), buildRoundedMask(), DEFAULTS, DitherConfig, DitheredLogo(), DitheredLogoProps, drawParticles(), errorDiffusionDither() (+7 more)

### Community 47 - "👥 The 5 Agent Roles"
Cohesion: 0.13
Nodes (14): 1. Intake Agent (Email Listener), 2. Sourcing Orchestrator (The Coordinator), 3. Sourcing & Scraping Agent (Rates Engine), 4. Finance & Costing Agent (Excel Compiler), 5. Email Draft Agent (Communicator), 📋 Executive Summary, 🛠️ Implementation Stages, Phase 1: Email Integration (Week 1-2) (+6 more)

### Community 48 - "HapagLloydConnector"
Cohesion: 0.06
Nodes (33): HapagLloydConnector, HapagServiceUnavailableException, Exception, Normalize various date formats (e.g. 2026-05-31, 31.05.2026, 31 May 2026, 31…, Robustly selects options from Hapag-Lloyd custom dropdown lists. Types the…, Detects the Microsoft B2C identity/OAuth login page. Hapag can silently bounce…, Guards against the session-expiry-mid-crawl failure mode: the existing redirect…, Crawls Hapag-Lloyd sailing schedules from the Schedule tab. (+25 more)

### Community 49 - "app/page.tsx"
Cohesion: 0.13
Nodes (22): 6. Known limitations / candidate follow-ups, AppHeader(), AppHeaderProps, initials(), systemStatus(), BackendConfigModal(), BackendConfigModalProps, SearchCompletionModal() (+14 more)

### Community 50 - "AdminUsers.tsx"
Cohesion: 0.11
Nodes (24): AdminUserRecord, AdminUsers(), AdminUsersProps, ago(), AuditEntry, Avatar(), Filter, initials() (+16 more)

### Community 51 - "CurrencyManager"
Cohesion: 0.21
Nodes (8): get_exchange_rates_endpoint(), convert_currency_to_usd(), CurrencyManager, get_all_exchange_rates(), Any, Currency Exchange Rate Service — manages currency conversions and custom…, update_exchange_rate(), threading

### Community 52 - "LiveSearchProgress.tsx"
Cohesion: 0.08
Nodes (30): ChatWidget(), ChatWidgetProps, Message, ACTION_STATUSES, ChipModel, describe(), EMPTY_STATUSES, formatElapsed() (+22 more)

### Community 53 - "SearchComposer.tsx"
Cohesion: 0.20
Nodes (16): CarrierMultiSelect(), CarrierMultiSelectProps, isAllCarriers(), toggleAllCarriers(), toggleCarrierSelection(), DeliveryType, HapagRegion, REGIONS (+8 more)

### Community 54 - "🚢 Infreight Sourcing & Ocean Rate Automation System"
Cohesion: 0.14
Nodes (13): 1. Multi-Carrier Automation Engine, 2. Intelligent Surcharge & Charge Classifier Engine (`charge_classifier.py`), 3. Container Comparison Matrix & Excel Export Engine, 🚢 Infreight Sourcing & Ocean Rate Automation System, 🌟 Key Capabilities, 📄 License & Confidentiality, Prerequisites, 🛠️ Project Structure (+5 more)

### Community 55 - "._query_prices_api"
Cohesion: 0.18
Nodes (6): AsyncClient, Resolves a free-text port name or string (e.g. 'Singapore', 'Hamburg, Germany…, Hapag-Lloyd Prices API requires earliestDepartureDate to be at least 4 calendar…, Constructs OpenAPI compliant OfferRequest payload., Sends a single POST /prices request with rate-limiting and error handling., Queries Hapag-Lloyd DCSA Commercial Schedules API (v1.0.2) to retrieve point-…

### Community 56 - "[2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split"
Cohesion: 0.15
Nodes (13): G2 Stress Test: "Hi, Please book the below as per your quote ref INF-2026-0842:…, H1 Stress Test: Table with 2 distinct rows: Row 1: POL Singapore, POD Jakarta,…, test_g2_booking_confirmation_guardrail(), test_h1_table_deduplication_two_pairs(), [2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split, Booking Confirmation / Instructions Intercept Guardrail G2 (`rfq_agent.py` & `RfqInputSection.tsx`), Commercial Sales Desk Intelligence (`sales_notes`), Deterministic Port Alias Resolver (`ports_aliases.json`) (+5 more)

### Community 57 - ".search_quotes"
Cohesion: 0.12
Nodes (11): extract_locode_and_country(), prepare_maersk_query(), Small aimless pointer drift, as a person does while a page loads., Fills an autocomplete field using the proven original element-level…, Extracts LOCODE and country name from text like 'CASABLANCA, MOROCCO (MACAS)'…, Maps standard container search codes (e.g. 'DRY 20', '20GP') to Maersk Spot…, Scores a Maersk autocomplete dropdown suggestion. NOTE: The nested/indented…, Visible page size, read from the page. (+3 more)

### Community 58 - "🛠 Detailed Carrier Log"
Cohesion: 0.15
Nodes (12): 🛠 Detailed Carrier Log, 🟢 GreenX, 🟠 Hapag-Lloyd, Infreight Ocean Carrier Rate Automation — Development Log, 🚀 Key Highlights & Architectural Changes, 🔌 Local Laptop Deployment (Self-Hosted Worker), 🔵 Maersk, 💗 ONE (Ocean Network Express) (+4 more)

### Community 59 - "_Page"
Cohesion: 0.15
Nodes (8): _connector(), _Locator, _Page, Maersk's login page redirects to the Hub a few seconds after loading when the…, Sits on /portaluser/login, then redirects after `redirect_after` URL reads., test_login_uses_saved_session_after_late_redirect(), test_wait_detects_late_redirect(), test_wait_detects_login_form()

### Community 60 - "sort_container_types"
Cohesion: 0.40
Nodes (4): Sort container types in standard order: DRY 20 (20GP) -> DRY 40 (40GP) -> DRY…, sort_container_types(), test_container_types_standard_ordering(), model_validator

### Community 61 - "RfqInputSection.tsx"
Cohesion: 0.18
Nodes (14): RateSearchFormProps, DEMO_EXAMPLES, RfqInputSection(), RfqInputSectionProps, Box(), fieldName(), laneFlags(), RfqLane (+6 more)

### Community 62 - "[2026-06-30] — ONE Multi-Container & Sold-Out, GreenX Surcharge Intake, Free-Time Fixes, Maersk Diagnosis"
Cohesion: 0.29
Nodes (7): [2026-06-30] — ONE Multi-Container & Sold-Out, GreenX Surcharge Intake, Free-Time Fixes, Maersk Diagnosis, GreenX — Only Basic Ocean Freight & LSS Folded Into Final Value, MAERSK — "Quotes Found" but Empty Excel (Diagnosis), ONE — All-Container-Type Search Returning 0 Quotes, ONE — Multi-Container Breakdown Triple-Counted / Inflated Final Value, ONE — Sold-Out ("Notify Me") Sailings Appearing as Quotes, Performance/Reliability — Stop Copying Chrome Caches During Profile Clone/Sync

### Community 63 - "[2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup"
Cohesion: 0.12
Nodes (10): MockCard, MockLocator, [2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup, Chromium Cache Auto-Cleanup (Railway Storage Bloat Prevention), CMA CGM — 30-Second Timeout on Sold Out Cards, CMA CGM — Free Time Regex Too Strict, CMA CGM — Routing Regex Not Matching "via LEKKI, LA, NG", Excel Export — Routing & Free Time Columns Always Empty (+2 more)

### Community 64 - "orbit-card-stack.tsx"
Cohesion: 0.22
Nodes (13): HalftoneAvatar(), HalftoneAvatarProps, hashSeed(), pick(), clamp(), initialsFor(), laneLabel(), OrbitCardStack() (+5 more)

### Community 65 - "._split_or_none"
Cohesion: 0.25
Nodes (7): Calls the connector's per-container splitter whether it is sync or async…, 1. What was measured, 2. Why the scrapers break when a site changes, 3. Multi-port quick search — defects found and fixed, 4. Ranked recommendations, 5. Verification of this change, Scraper Robustness Review — July 2026

### Community 66 - "GreenX — Surcharge Intake Fix (2026-06-30)"
Cohesion: 0.22
Nodes (8): Charges that must be taken into the final value (USD only), Files changed, Fix, GreenX — Surcharge Intake Fix (2026-06-30), Per-B/L charges (billed once per booking, added in full to *each* container type), Problem, Root cause, Verification

### Community 67 - "Admin Page & Port Prioritization Guide"
Cohesion: 0.25
Nodes (7): 1. Popular Ports (UN/LOCODEs), 2. Boosted Countries, Admin Page & Port Prioritization Guide, 🔒 How to Access the Admin Page, ⚙️ How to Use Port Prioritization, ⚡ Important Notes, 📝 Step-by-Step Example

### Community 68 - "test_self_healing.py"
Cohesion: 0.27
Nodes (10): detect_manual_action_required(), Manual Action Detector — identifies pages requiring human verification (2FA,…, Scans the current Playwright page to see if a CAPTCHA, Cloudflare challenge,…, asyncio, Self-Healing Layer & Chatbot Test Suite. Tests the selector memory, failure…, test_ai_repair_agent_offline_fallback(), test_chat_service_offline_fallback(), test_manual_action_detector_captcha() (+2 more)

### Community 69 - "selector_memory.py"
Cohesion: 0.24
Nodes (12): get_approved_selector(), _load_memory(), Selector Memory — stores and retrieves human-approved selector patches., Loads memory JSON file. Returns empty dict if file is missing or invalid., Saves memory dict back to JSON file., Looks up if there is an approved replacement selector for the given carrier and…, Stores an approved replacement selector., Marks any proposed selector for this step as REJECTED. (+4 more)

### Community 70 - "QuoteSchema"
Cohesion: 0.06
Nodes (48): ABC, BaseCarrierConnector, Base Carrier Connector — abstract base class for all carrier connectors. Each…, Open the price breakdown / detail view for a specific quote. Args: quote_ref:…, Extract individual charge line items from the price breakdown. Returns: List of…, Normalize extracted data into a QuoteSchema using the normalizer. Args:…, Detects if a CAPTCHA, Turnstile, hCaptcha, reCAPTCHA, or 2FA screen is…, Abstract base class for carrier portal connectors. (+40 more)

### Community 71 - "parse_rfq_endpoint"
Cohesion: 0.67
Nodes (3): parse_rfq_endpoint(), post, Parse a free-text RFQ email or message into a structured RateSearchRequest…

### Community 72 - "deploy"
Cohesion: 0.25
Nodes (7): build, builder, deploy, restartPolicyMaxRetries, restartPolicyType, startCommand, $schema

### Community 73 - "Frontend Redesign — Componentry Design System, Workspace & Launch Intro (2026-09-07)"
Cohesion: 0.14
Nodes (13): 1. Design system foundation (`082b43a`), 2. Bugs found and fixed during the restyle, 3. Workspace + launch intro (`21ade75`), 4. Follow-up fixes (`2f9d92b`), 5. Verification, 7. Conventions to follow from here, Dependencies added (5, all small, no runtime lib dependency on Componentry), Frontend Redesign — Componentry Design System, Workspace & Launch Intro (2026-09-07) (+5 more)

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

### Community 80 - "fetch_port_fixes"
Cohesion: 0.17
Nodes (10): fetch_carrier_overrides(), fetch_port_fixes(), get_admin_custom_ports(), get_carrier_session(), get_ports_config(), list_workers(), get, Worker machines (e.g. the office laptop running Maersk) and whether they're… (+2 more)

### Community 81 - "Design system — read before touching any UI"
Cohesion: 0.33
Nodes (5): Animation rules, Client-only preferences, Design system — read before touching any UI, This is NOT the Next.js you know, Use tokens, not raw colours

### Community 82 - "analytics_service.py"
Cohesion: 0.22
Nodes (10): compute_admin_analytics(), get_clean_lane_key(), normalize_lane_port(), Any, AsyncSession, Consolidated Analytics Service for Infreight Ocean Carrier Rate Automation.…, Normalize port string to cleanly aggregate naming variations., Returns (norm_origin, norm_dest, display_lane_key). (+2 more)

### Community 83 - "layout.tsx"
Cohesion: 0.25
Nodes (6): frontend_src_app_globals, instrumentSans, inter, metadata, viewport, ThemeProvider()

### Community 84 - "port_routes.py"
Cohesion: 0.16
Nodes (14): get_countries(), get_port(), get_suggestions(), get, Get list of countries for autocomplete dropdown., Get specific port details by UN/LOCODE., Get port suggestions for autocomplete., search() (+6 more)

### Community 85 - "Infreight Sourcing Automation — Run Audit (30 Jul 2026)"
Cohesion: 0.33
Nodes (5): Expected on this machine (not automation faults), Faults (correctness), Inefficiencies (speed), Infreight Sourcing Automation — Run Audit (30 Jul 2026), Suggested priority

### Community 86 - ".filter_cheapest_in_14d_window"
Cohesion: 0.40
Nodes (4): Backward-compatible: the single cheapest card (1ST window, else 2ND)., [2026-07-03] — Robustness Review & Multi-Port Quick Search Fixes, Quick Search (multi-port RFQ) — Per-Container Pricing Was Wrong, Robustness Review (see `docs/ROBUSTNESS_REVIEW_2026-07.md`)

### Community 88 - "[2026-05-23 – 2026-05-24] — Maersk Shadow DOM & Stealth Upgrades"
Cohesion: 0.50
Nodes (4): [2026-05-23 – 2026-05-24] — Maersk Shadow DOM & Stealth Upgrades, Maersk — 2FA/CAPTCHA Human-in-the-Loop via noVNC, Maersk — Login Credential Autofill Corruption, Maersk — Shadow DOM Piercing for MDS Web Components

### Community 89 - "dependencies"
Cohesion: 0.15
Nodes (13): dependencies, class-variance-authority, clsx, exceljs, lucide-react, next, next-themes, @radix-ui/react-slot (+5 more)

### Community 91 - "test_excel_exports.js"
Cohesion: 0.33
Nodes (6): ref_fs, assert(), ExcelJS, fs, mockBatchResults, testTariffExport()

### Community 92 - "ai_repair_agent.py"
Cohesion: 0.33
Nodes (6): _local_fuzzy_repair(), AI Repair Agent — diagnoses Playwright step failures and suggests selector…, A local rule-based heuristic to locate reasonable buttons or inputs when Gemini…, Analyzes the failure context and DOM content to suggest a selector repair. Uses…, suggest_fix(), bs4

### Community 93 - "[2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History"
Cohesion: 0.40
Nodes (5): [2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History, Admin User Search History & SGT GMT+8 Conversion (`AdminDashboard.tsx`), GreenX (Evergreen) Card Isolation & Surcharge Parsing (`greenx_connector.py`), Multi-Route Batch Execution Engine (`batch_engine.py`), OOCL FreightSmart 28-Day Calendar Expansion (`oocl_connector.py`)

### Community 94 - "._parse_free_time_text"
Cohesion: 0.43
Nodes (5): Parses ONE QUOTE Free Time popover text for DESTINATION ONLY. Ignores Origin…, test_one_free_time_parser_origin_only_ignored(), test_one_free_time_parser_test_a(), test_one_free_time_parser_test_b(), test_one_free_time_parser_test_c()

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
Cohesion: 0.05
Nodes (45): argparse, asyncio, Repair Report — generates and saves diagnosis reports on Playwright selector…, GreenX (Evergreen) Live Connector - Playwright automation., AI Browser Agent — Vision-based browser automation using Gemini Flash. This…, Experimental AI Agent Test -- Maersk Quote Search This script tests the AI…, Interactive Headed Login Helper for Maersk. Opens real Chrome using the…, Interactive Headed Login Helper for ONE (Ocean Network Express). Opens Chrome… (+37 more)

### Community 100 - "export_maersk_login.py"
Cohesion: 0.70
Nodes (4): _logged_in(), main(), _on_login_page(), Save a Maersk login from your own PC for the server to use. Opens real Google…

### Community 101 - "diagnose_greenx_dropdown.py"
Cohesion: 0.67
Nodes (3): dump_options(), main(), Diagnostic: dump ALL dropdown options (text + innerHTML) when typing 'DEHAM'…

### Community 102 - "resolve_port_for_carrier"
Cohesion: 0.24
Nodes (9): Resolves input text (e.g. 'Belfast (GBBEL)' or 'GBBEL') to a tuple of…, resolve_msc_port(), Resolves input text to (location_name, locode, country_code, country_name)., resolve_oocl_port_info(), resolve_port_for_carrier(), Verify non-Maersk carriers get standard UN/LOCODE or default mappings., Verify that El Dekheila maps specifically to 'Alexandria Dekheila, Egypt' for…, test_el_dekheila_maersk_override() (+1 more)

### Community 106 - "[2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes"
Cohesion: 0.50
Nodes (4): [2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes, CMA CGM — Chrome Profile Bypass, ONE — Date Formatting & Charge Breakdown Pollution, ONE — Date Picker Pre-selection Issue

### Community 108 - "remote_worker.py"
Cohesion: 0.10
Nodes (31): Models package. Note: Individual modules can be imported directly (e.g.,…, _claim_loop(), claim_next(), delegate_and_wait(), heartbeat_once(), _heartbeat_thread(), beat(), is_worker() (+23 more)

### Community 116 - "pytest"
Cohesion: 0.17
Nodes (8): parse_hapag_card_text_mock(), Verify that multi-leg/feeder routes take the final arrival ETA and 28 days TT., Mock implementation of the JS evaluate logic inside hapag_lloyd_connector.py., test_hapag_multi_leg_schedule_extraction(), Tests for rate search API endpoints., Placeholder test — integration tests require DB setup., test_placeholder(), pytest

### Community 117 - "[2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash"
Cohesion: 0.40
Nodes (5): [2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash, AI RFQ Front Door & Air Freight Support, Multi-Origin & Gappy List Parsing (Sea RFQs), Native Gemini 2.5 Flash Direct API Integration, Search Form Streamlining

### Community 118 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, dev, lint, start

### Community 119 - "database.py"
Cohesion: 0.11
Nodes (24): _create_sqlite_engine(), _get_engine(), get_session(), _get_session_maker(), init_db(), AsyncSession, Database connection and session management. Supports PostgreSQL (production)…, Dependency for getting a database session. (+16 more)

### Community 121 - "Architecture Overview"
Cohesion: 0.50
Nodes (4): Architecture Overview, Carrier Connector Lifecycle, Charge Classification Rules, Search Flow

### Community 124 - "[2026-06-03] — CMA CGM Routing & Free Time Extraction"
Cohesion: 0.50
Nodes (4): [2026-06-03] — CMA CGM Routing & Free Time Extraction, CMA CGM — Import Free Time from D&D Tab, CMA CGM — Routing Detection (Direct vs Transit), Maersk — Free Time Extraction from Card Text

### Community 128 - "[2026-08-04 - 2026-08-06] — CMA CGM Dynamic RAMP/POD Rerouting, Brand Excel Styling, Port Synonym Matching & Tunnel Relays"
Cohesion: 0.40
Nodes (5): [2026-08-04 - 2026-08-06] — CMA CGM Dynamic RAMP/POD Rerouting, Brand Excel Styling, Port Synonym Matching & Tunnel Relays, Brand-Aligned Excel Export Styling (`excel_export.py`), CMA CGM Dynamic RAMP / POD Advisory Banner Detection (`cma_connector.py`), Dynamic Carrier Port Overrides & Admin Registry (`PortManager`, `AdminDashboard.tsx`), Railway WebSocket Tunnel Relay & Failover (`tunnel_client.py`, `run_tunnel_client.bat`, `FailoverFetch`)

### Community 131 - "[2026-05-25 – 2026-05-26] — VNC Display Isolation & Proxy Integration"
Cohesion: 0.67
Nodes (3): [2026-05-25 – 2026-05-26] — VNC Display Isolation & Proxy Integration, Bright Data ISP Proxy Integration, VNC Display Isolation for Concurrent Carriers

### Community 132 - ".search_quotes"
Cohesion: 0.25
Nodes (3): fill_container_card(), Tries to click a matching option from ONE's visible dropdown. Returns True only…, set_cached_carrier_port()

### Community 133 - "[2026-06-02] — Hapag-Lloyd Transshipment & Duplicate Fix"
Cohesion: 0.67
Nodes (3): [2026-06-02] — Hapag-Lloyd Transshipment & Duplicate Fix, Hapag-Lloyd — Duplicate Sailings from Transshipment Vessels, Hapag-Lloyd — Routing Not Marked as Transit

### Community 135 - "[2026-05-20 – 2026-05-22] — Port Resolution & Frontend Improvements"
Cohesion: 0.50
Nodes (4): [2026-05-20 – 2026-05-22] — Port Resolution & Frontend Improvements, Excel Export — ETA Column & Container Type Header, Frontend Light Mode & CORS Fix, Port Resolution System

### Community 136 - "clean_selector_memory"
Cohesion: 0.67
Nodes (3): clean_selector_memory(), fixture, Wipes the selector memory JSON file before and after each test.

## Knowledge Gaps
- **326 isolated node(s):** `Config`, `install_pi.sh script`, `eslintConfig`, `nextConfig`, `name` (+321 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1017 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **24 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Changelog` connect `Changelog` to `[2026-08-04 - 2026-08-06] — CMA CGM Dynamic RAMP/POD Rerouting, Brand Excel Styling, Port Synonym Matching & Tunnel Relays`, `[2026-05-25 – 2026-05-26] — VNC Display Isolation & Proxy Integration`, `[2026-06-02] — Hapag-Lloyd Transshipment & Duplicate Fix`, `[2026-05-20 – 2026-05-22] — Port Resolution & Frontend Improvements`, `[2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes`, `._fs_dismiss_modals`, `[2026-05-29 – 2026-05-30] — Hapag-Lloyd Full Integration`, `[2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning`, `[2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash`, `.filter_cheapest_in_14d_window`, `[2026-05-23 – 2026-05-24] — Maersk Shadow DOM & Stealth Upgrades`, `Architecture Overview`, `[2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split`, `[2026-06-03] — CMA CGM Routing & Free Time Extraction`, `[2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History`, `[2026-06-30] — ONE Multi-Container & Sold-Out, GreenX Surcharge Intake, Free-Time Fixes, Maersk Diagnosis`, `[2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup`?**
  _High betweenness centrality (0.283) - this node is a cross-community bridge._
- **Why does `[2026-06-03] — CMA CGM Routing & Free Time Extraction` connect `[2026-06-03] — CMA CGM Routing & Free Time Extraction` to `Changelog`?**
  _High betweenness centrality (0.249) - this node is a cross-community bridge._
- **Why does `Maersk — Free Time Extraction from Card Text` connect `[2026-06-03] — CMA CGM Routing & Free Time Extraction` to `RateResults.tsx`?**
  _High betweenness centrality (0.248) - this node is a cross-community bridge._
- **Are the 39 inferred relationships involving `RateSearchRequest` (e.g. with `create_batch_rate_search()` and `create_rate_search()`) actually correct?**
  _`RateSearchRequest` has 39 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `cn()` (e.g. with `Reuse the primitives` and `7. Conventions to follow from here`) actually correct?**
  _`cn()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 23 inferred relationships involving `CarrierResultStatus` (e.g. with `safe_step()` and `update_carrier_status()`) actually correct?**
  _`CarrierResultStatus` has 23 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Config`, `install_pi.sh script`, `eslintConfig` to the rest of the system?**
  _326 weakly-connected nodes found - possible documentation gaps or missing edges._