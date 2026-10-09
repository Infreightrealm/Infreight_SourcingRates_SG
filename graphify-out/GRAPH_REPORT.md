# Graph Report - Infreight_SourcingRates_SG  (2026-10-09)

## Corpus Check
- 246 files · ~1,163,239 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 23 file(s) not represented in the graph (top: (none) 10, .bat 6, .conf 2)

## Summary
- 2370 nodes · 5852 edges · 125 communities (105 shown, 20 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 334 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `eeacdfe2`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- port_manager.py
- BaseCarrierConnector
- cn
- user_routes.py
- auth_routes.py
- browser_cleanup.py
- OOCLConnector
- api.ts
- PortManager
- capture_failure_context
- CMAConnector
- test_normalizer.py
- job_service.py
- .login
- ._fs_dismiss_modals
- HapagLloydAPIConnector
- preferences.ts
- test_rfq_agent.py
- User
- SocialWidget.tsx
- MobileTabBar.tsx
- GreenXConnector
- social_routes.py
- port_routes.py
- backend/main.py
- rate_search_routes.py
- msc_connector.py
- parse_rfq
- utils.ts
- AIBrowserAgent
- database.py
- ONEConnector
- _Page
- Engineering Report: Sourcing Portal Enhancements & Scraping Pipeline Stability
- Changelog
- react
- package.json
- RateSearch
- RateResults.tsx
- SearchQueueManager
- ChargeCategory
- Frontend Redesign — Componentry Design System, Workspace & Launch Intro (2026-09-07)
- compilerOptions
- search_port
- test_carrier_timeout.py
- RfqInputSection.tsx
- dithered-logo.tsx
- 👥 The 5 Agent Roles
- HapagLloydConnector
- CarrierResultStatus
- selector_memory.py
- CurrencyManager
- CarrierSearchResult
- test_hapag_freetime.py
- 🚢 Infreight Sourcing & Ocean Rate Automation System
- RateSearchRequest
- [2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split
- ._parse_offer_response_to_quotes
- 🛠 Detailed Carrier Log
- orbit-card-stack.tsx
- silk-aurora.tsx
- [2026-08-07] — Carrier Specific Free Time, Demurrage/Detention Splitting, MSC CDD Surcharges, OOCL Nearby Route Filtering & Favicon Cache Busting
- [2026-06-30] — ONE Multi-Container & Sold-Out, GreenX Surcharge Intake, Free-Time Fixes, Maersk Diagnosis
- [2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup
- ai_repair_agent.py
- RFQParseResult
- GreenX — Surcharge Intake Fix (2026-06-30)
- Admin Page & Port Prioritization Guide
- [2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning
- test_self_healing.py
- dependencies
- carrier_switches.py
- deploy
- .search_quotes
- test_panama_canal_surcharge.py
- Summary of Changes — July 20, 2026
- safe_step.py
- [2026-05-29 – 2026-05-30] — Hapag-Lloyd Full Integration
- resolve_port_alias
- test_brightdata.py
- ._mouse_glide_to
- Design system — read before touching any UI
- tunnel_relay/main.py
- layout.tsx
- ._fs_extract_rows
- compute_admin_analytics
- tunnel_client.py
- RateLimiter
- os
- [2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History
- MockCard
- ref_fs
- devDependencies
- .search_port
- handle_chat_query
- playwright_async_api
- frontend/README.md
- pytest
- [2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control
- [2026-08-04 - 2026-08-06] — CMA CGM Dynamic RAMP/POD Rerouting, Brand Excel Styling, Port Synonym Matching & Tunnel Relays
- ._lookup_freetime
- [2026-05-20 – 2026-05-22] — Port Resolution & Frontend Improvements
- [2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash
- scripts
- Working in this repository
- [2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes
- install_pi.sh
- models/__init__.py
- postcss.config.mjs
- eslint.config.mjs
- [2026-05-23 – 2026-05-24] — Maersk Shadow DOM & Stealth Upgrades
- ._execute_single_price_request
- .extract_charge_breakdown
- Architecture Overview
- [2026-05-25 – 2026-05-26] — VNC Display Isolation & Proxy Integration
- [2026-05-31] — Multi-Instance Support & Charge Classification
- alembic
- main

## God Nodes (most connected - your core abstractions)
1. `RateSearchRequest` - 161 edges
2. `cn()` - 89 edges
3. `CarrierResultStatus` - 69 edges
4. `QuoteSchema` - 67 edges
5. `User` - 59 edges
6. `PortManager` - 58 edges
7. `HapagLloydConnector` - 56 edges
8. `CMAConnector` - 55 edges
9. `MaerskConnector` - 52 edges
10. `BaseCarrierConnector` - 50 edges

## Surprising Connections (you probably didn't know these)
- `Excel Export — Routing & Free Time Columns Always Empty` --references--> `Quote`  [INFERRED]
  CHANGELOG.md → backend/models/quote.py
- `Hapag-Lloyd — Date String Standardization` --references--> `standardize_date_string()`  [INFERRED]
  CHANGELOG.md → backend/services/normalizer.py
- `2. Bugs found and fixed during the restyle` --references--> `BackendConfigModal()`  [INFERRED]
  FRONTEND_REDESIGN_2026-09-07.md → frontend/src/components/BackendConfigModal.tsx
- `4. Follow-up fixes (`2f9d92b`)` --references--> `PortAutocomplete()`  [INFERRED]
  FRONTEND_REDESIGN_2026-09-07.md → frontend/src/components/PortAutocomplete.tsx
- ``WorkspacePanel.tsx` — four customization cards (header → "Workspace")` --references--> `RateSearchForm()`  [INFERRED]
  FRONTEND_REDESIGN_2026-09-07.md → frontend/src/components/RateSearchForm.tsx

## Import Cycles
- None detected.

## Communities (125 total, 20 thin omitted)

### Community 0 - "port_manager.py"
Cohesion: 0.26
Nodes (11): add_carrier_override(), add_custom_port(), delete_carrier_override(), delete_custom_port(), get_carrier_overrides(), get_custom_ports(), get_popular_ports_config(), update_popular_ports_config() (+3 more)

### Community 1 - "BaseCarrierConnector"
Cohesion: 0.06
Nodes (28): ABC, BaseCarrierConnector, NotAvailableConnector, Any, Open the price breakdown / detail view for a specific quote. Args: quote_ref:…, Extract individual charge line items from the price breakdown. Returns: List of…, Normalize extracted data into a QuoteSchema using the normalizer. Args:…, Abstract base class for carrier portal connectors. (+20 more)

### Community 2 - "cn"
Cohesion: 0.11
Nodes (32): Reuse the primitives, New primitives — `frontend/src/components/ui/`, LoadingState(), LoginModalProps, SearchCompletionModal(), SearchCompletionModalProps, Badge(), badgeVariants (+24 more)

### Community 3 - "user_routes.py"
Cohesion: 0.08
Nodes (59): admin_delete_user(), AdminLoginRequest, approve_user(), CarrierOverrideRequest, CarrierSwitchRequest, Config, create_custom_port_endpoint(), CustomPortRequest (+51 more)

### Community 4 - "auth_routes.py"
Cohesion: 0.06
Nodes (73): clear_session_cookie(), get_current_user_optional(), login(), LoginRequest, logout(), AsyncSession, BaseModel, post (+65 more)

### Community 5 - "browser_cleanup.py"
Cohesion: 0.12
Nodes (32): _is_chrome(), _is_playwright_driver(), _kill(), kill_profile_browsers(), _proc_supported(), Cleanup for Chrome browsers and temporary profiles that a failed close leaves…, Kill every automated Chrome and Playwright driver. Only call this when no…, Delete per-search profile copies ("chrome_profile_<carrier>_tmp_<id>") and… (+24 more)

### Community 6 - "OOCLConnector"
Cohesion: 0.13
Nodes (12): OOCLConnector, _parse_date(), parse_oocl_date(), Parses one FreightSmart result card's inner text into a raw row dict. Text-…, Attempts to automatically click the Cloudflare Turnstile 'Verify you are human'…, Position-based fallback for the onboarding tour popup: instead of guessing its…, asyncio, test_oocl_cwx_different_port_pair_different_amount() (+4 more)

### Community 7 - "api.ts"
Cohesion: 0.07
Nodes (67): AdminDashboard(), LoginContent(), HomeContent(), AppHeader(), initials(), systemStatus(), BackendConfigModal(), BackendConfigModalProps (+59 more)

### Community 8 - "PortManager"
Cohesion: 0.11
Nodes (8): PortManager, Where admin-saved port name fixes are kept. Railway rebuilds /app on every…, Retrieve verified carrier port name from persistent cache by UN/LOCODE,…, Cache verified carrier port name and save persistently to…, Clean and normalize user input for port searching., Retrieve port data by full UN/LOCODE (e.g., 'SGSIN')., _user_overrides_path(), test_saved_fixes_live_on_the_persistent_volume()

### Community 9 - "capture_failure_context"
Cohesion: 0.33
Nodes (5): capture_failure_context(), Exception, Failure Detector — parses and structures error context from failed Playwright…, Assembles a standardized diagnostic dictionary containing all available details…, test_failure_detector()

### Community 10 - "CMAConnector"
Cohesion: 0.07
Nodes (20): CMAConnector, Ensures 'Ramp' is explicitly selected under 'Type of location' toggle buttons…, Scans for Route, POL (Port of Loading), or POD (Port of Discharge) dropdown…, Clears the currently selected Destination port tag/card, re-types the locode,…, Dynamically extracts any recommended 5-letter POD LOCODE mentioned in the…, Detects if CMA CGM displayed an advisory banner message: "Looking for AEJEA or…, Handles the 'Customer account' -> 'Role (you are acting as)' dropdown on CMA…, Repeatedly clicks 'More results' if visible to load ALL quotes on the page. (+12 more)

### Community 11 - "test_normalizer.py"
Cohesion: 0.13
Nodes (17): is_weight_surcharge_applicable(), Evaluates whether a weight-tier or overweight surcharge is applicable for the…, calculate_final_freight_value(), classify_and_organize_charges(), Takes raw charge line items and classifies them. Args: raw_charges: list of…, Calculate the final freight value from a list of classified charges. Args:…, Tests for normalizer / final freight value calculator., test_basic_calculation() (+9 more)

### Community 12 - "job_service.py"
Cohesion: 0.12
Nodes (30): close_all_active_connectors(), get_connector(), Get the appropriate connector for a carrier. If USE_MOCK_CARRIERS=true: returns…, Force close all active carrier connectors and their Playwright Chrome windows., get_async_session_maker(), Get the session maker for use outside of FastAPI dependency injection., SearchStatus, cancel_all_active_searches() (+22 more)

### Community 13 - ".login"
Cohesion: 0.20
Nodes (6): _is_logged_in_url(), Wait until the login page either redirects to a signed-in page or shows its…, True once Maersk has moved past the login pages to a signed-in page., Types text character by character into a given locator or element handle with…, Turn off Chrome's password manager and autofill in this profile. Real Chrome…, test_logged_in_url()

### Community 14 - "._fs_dismiss_modals"
Cohesion: 0.11
Nodes (14): _dismiss_once(), _click_date_strip_item(), _open_calendar(), Lock, Iterates through the FreightSmart results date calendar to collect E-Quote and…, Full FreightSmart phase: login â†’ fill quote form â†’ search â†’ extract rows., Shadow-DOM-aware check for whether the onboarding tour heading is on screen., Runs CONCURRENTLY with the rest of the FreightSmart form-filling flow and… (+6 more)

### Community 15 - "HapagLloydAPIConnector"
Cohesion: 0.11
Nodes (11): HapagLloydAPIConnector, Direct REST API connector for Hapag-Lloyd Prices API v2.1.4., API connectors do not require browser login sessions., No browser session to reset between batch routes., Resolves a free-text port name or string (e.g. 'Singapore', 'Hamburg, Germany…, Hapag-Lloyd Prices API requires earliestDepartureDate to be at least 4 calendar…, main(), test_locode_resolution() (+3 more)

### Community 16 - "preferences.ts"
Cohesion: 0.08
Nodes (35): nextConfig, LaunchIntro(), SearchHistoryItem, derive(), Derived, startOfDay(), UsageStats(), ChoiceCard() (+27 more)

### Community 17 - "test_rfq_agent.py"
Cohesion: 0.10
Nodes (28): asyncio, Unit tests for the Gemini AI RFQ Agent service (parse_rfq). Includes…, Test Image 4: Steel Plate ex Pasir Gudang / Tanjung Pelepas for 20' & 40'., Test Guardrail: Detects LCL request., Test OpenFlights 6,072 IATA airport dataset and shorthand alias resolution., Test Pak Shaun email: "Hi team, need rate for 10x20GP from PK to JKT. Urgent…, Test Multimodal Image Input validation and parsing., Test Stress Test Scenario: "Dear Sir, Pls quote 3 x 20'FCL Singapore to… (+20 more)

### Community 18 - "User"
Cohesion: 0.11
Nodes (24): get_me(), get, Dependency that strictly requires an active admin user., Get profile of currently signed-in user., require_admin(), fetch_carrier_overrides(), fetch_port_fixes(), get_admin_custom_ports() (+16 more)

### Community 19 - "SocialWidget.tsx"
Cohesion: 0.16
Nodes (21): ACCENT_COLORS, errorMessage(), relativeTime(), resizeImageToDataUrl(), SocialWidget(), SocialWidgetProps, EMOJI_GROUPS, EmojiPicker() (+13 more)

### Community 20 - "MobileTabBar.tsx"
Cohesion: 0.12
Nodes (20): ChatWidget(), ChatWidgetProps, Message, MenuRow(), MobileTab, MobileTabBar(), MobileTabBarProps, tabClass() (+12 more)

### Community 21 - "GreenXConnector"
Cohesion: 0.07
Nodes (16): GreenXConnector, date, GreenX (Evergreen) Live Connector - Playwright automation., Overrides base search runner to query all 3 sizes at once and cache the…, Type a LOCODE into the autocomplete field and click the first visible dropdown…, Find quantity input next to or below label_text and fill it., Find the exact individual quote card container row encompassing dates, rates,…, Dismiss any cookie/alert modal that would intercept pointer events. (+8 more)

### Community 22 - "social_routes.py"
Cohesion: 0.10
Nodes (31): get_current_user(), Dependency that strictly requires an authenticated active member., get_conversation(), list_colleagues(), poke_colleague(), PokeRequest, AsyncSession, BaseModel (+23 more)

### Community 23 - "port_routes.py"
Cohesion: 0.29
Nodes (9): get_countries(), get_port(), get_suggestions(), get, Get list of countries for autocomplete dropdown., Get specific port details by UN/LOCODE., Get port suggestions for autocomplete., search() (+1 more)

### Community 24 - "backend/main.py"
Cohesion: 0.08
Nodes (26): health(), lifespan(), get, websocket, Infreight Ocean Carrier Rate Automation — FastAPI Application. Main entry point…, Check if the VNC viewer is available (production only, where Xvfb runs)., Proxy WebSocket connections to legacy local x11vnc at localhost:5900., Proxy WebSocket connections to specific carrier x11vnc servers. (+18 more)

### Community 25 - "rate_search_routes.py"
Cohesion: 0.07
Nodes (49): approve_repair(), ApproveRepairRequest, carrier_switch_status(), chat_endpoint(), ChatRequest, create_batch_rate_search(), _contains(), _looks_like() (+41 more)

### Community 26 - "msc_connector.py"
Cohesion: 0.10
Nodes (15): format_to_iso_date(), MSCConnector, Playwright-based automation for MSC (Mediterranean Shipping Company)., Handles the MSC login flow., Clicks Instant Quote, fills form, clicks Search., Detects and clicks the 'Ramp' delivery/haulage option if MSC displays Ramp /…, Parse '14 Jun 2026' to 'YYYY-MM-DD, ChargeSchema (+7 more)

### Community 27 - "parse_rfq"
Cohesion: 0.14
Nodes (24): _call_native_gemini_api(), _detect_booking_confirmation(), _detect_dual_mode_enquiry(), _detect_mode_by_hierarchy(), _detect_unsupported_cargo(), _extract_20gp_weight_priority(), generate_dual_air_drafts(), _load_airport_aliases_config() (+16 more)

### Community 28 - "utils.ts"
Cohesion: 0.11
Nodes (30): 0. The one invariant, CarrierMultiSelect(), CarrierMultiSelectProps, isAllCarriers(), toggleAllCarriers(), toggleCarrierSelection(), PortAutocomplete(), PortAutocompleteProps (+22 more)

### Community 29 - "AIBrowserAgent"
Cohesion: 0.13
Nodes (15): AIBrowserAgent, Capture the current page as a PNG screenshot., Build the prompt with task description and action history., Parse Gemini's response into an action dict., Call Gemini API with exponential backoff retry., Execute a parsed action on the browser page., Detect if the agent is stuck repeating the same action., Find all visible interactive elements and format them as a prompt guide. (+7 more)

### Community 30 - "database.py"
Cohesion: 0.12
Nodes (22): Chat Service — manages conversational AI queries from the frontend user using…, get_sync_url(), run_migrations_offline(), run_migrations_online(), Base, _get_database_url(), _get_engine(), _get_session_maker() (+14 more)

### Community 31 - "ONEConnector"
Cohesion: 0.08
Nodes (14): ONEConnector, _classify(), date, Parses ONE QUOTE Free Time popover text for DESTINATION ONLY. Ignores Origin…, Splits a single raw multi-container quote card into multiple QuoteSchema…, Extracts 5-letter UN/LOCODE from strings like 'Singapore [SGSIN]' or 'Singapore…, asyncio, test_one_breakdown_currency_and_arbitrary_destination_classification() (+6 more)

### Community 32 - "_Page"
Cohesion: 0.15
Nodes (8): _connector(), _Locator, _Page, Maersk's login page redirects to the Hub a few seconds after loading when the…, Sits on /portaluser/login, then redirects after `redirect_after` URL reads., test_login_uses_saved_session_after_late_redirect(), test_wait_detects_late_redirect(), test_wait_detects_login_form()

### Community 33 - "Engineering Report: Sourcing Portal Enhancements & Scraping Pipeline Stability"
Cohesion: 0.08
Nodes (23): 1. Anti-Bot Mitigation & CAPTCHA Human-in-the-Loop Recovery, 2. Sourcing Parallelization & Surcharges Optimization, 3. Autocomplete Intelligence & Location Mapping, 4. Scraper Pipeline Maintenance, 5. Infrastructure & DevSecOps Enhancements, Business Value, Business Value, Business Value (+15 more)

### Community 34 - "Changelog"
Cohesion: 0.10
Nodes (20): [2026-05-18 – 2026-05-19] — Railway Deployment & Docker, [2026-06-01] — Hapag-Lloyd Sold Out Detection & Date Parsing, [2026-06-02] — Hapag-Lloyd Transshipment & Duplicate Fix, [2026-06-03] — CMA CGM Routing & Free Time Extraction, [2026-07-03] — Robustness Review & Multi-Port Quick Search Fixes, [2026-07-08] — OOCL E-Quote Calendar Navigation, cheapest E-Spot selection, and E-Quote/E-Spot isolation refinements, [2026-07-09] — Hapag-Lloyd Quick Quotes pairing and selection simplification, Changelog (+12 more)

### Community 35 - "react"
Cohesion: 0.05
Nodes (64): UserRecord, AdminCarriers(), when(), AdminAnalytics, AdminOverview(), AdminOverviewProps, AdminOverviewUser, AnalyticsRange (+56 more)

### Community 36 - "package.json"
Cohesion: 0.12
Nodes (15): engines, node, name, packageManager, private, version, react-dom, tailwind-merge (+7 more)

### Community 37 - "RateSearch"
Cohesion: 0.12
Nodes (23): get_route_health(), Get carrier search reliability & route health matrix across origin-destination…, _create_sqlite_engine(), init_db(), Create all tables on startup with automatic fallback to local SQLite if…, RateSearch, Represents a rate search request from an employee., Live search verification script for port logging and mismatch detection.… (+15 more)

### Community 38 - "RateResults.tsx"
Cohesion: 0.06
Nodes (63): ACTION_STATUSES, ChipModel, describe(), EMPTY_STATUSES, formatElapsed(), LiveSearchProgress(), LiveSearchProgressProps, parseServerTime() (+55 more)

### Community 39 - "SearchQueueManager"
Cohesion: 0.12
Nodes (11): Lock, Marks a search as completed internally so we can track the auto-release timeout., Called periodically in a background task to check if the user has held the lock…, Forcefully clears all queued searches and the active lock. Useful for…, Returns or creates an asyncio.Lock for a specific carrier code to prevent…, Adds a search to the queue and waits until it becomes the active search. Event-…, Singleton manager to enforce a FIFO queue for rate searches. Since web scraping…, Returns the current position of the search in the queue. 0 means it is the… (+3 more)

### Community 40 - "ChargeCategory"
Cohesion: 0.14
Nodes (26): ChargeCategory, classify_charge(), Charge Classifier — rule-based classification of freight charge line items.…, Classify a charge line item based on its name, amount, section heading, and…, Tests for charge classifier., test_basic_ocean_freight(), test_cwx_heavy_weight_charge(), test_destination_charges() (+18 more)

### Community 41 - "Frontend Redesign — Componentry Design System, Workspace & Launch Intro (2026-09-07)"
Cohesion: 0.11
Nodes (17): 1. Design system foundation (`082b43a`), 2. Bugs found and fixed during the restyle, 3. Workspace + launch intro (`21ade75`), 4. Follow-up fixes (`2f9d92b`), 5. Verification, 6. Known limitations / candidate follow-ups, 7. Conventions to follow from here, Dependencies added (5, all small, no runtime lib dependency on Componentry) (+9 more)

### Community 42 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 43 - "search_port"
Cohesion: 0.12
Nodes (17): Resolves input text (e.g. 'Belfast (GBBEL)' or 'GBBEL') to a tuple of…, resolve_msc_port(), fill_container_card(), Resolves input text to (location_name, locode, country_code, country_name)., resolve_oocl_port_info(), get_carrier_search_query(), get_port_by_code(), Suggest top N ports for a partial query. (+9 more)

### Community 44 - "test_carrier_timeout.py"
Cohesion: 0.19
Nodes (10): CrashingConnector, HangingConnector, asyncio, A carrier whose browser hangs must be stopped after CARRIER_SEARCH_TIMEOUT_SEC…, Hangs on the sizes in `hang_on`; answers NO_QUOTES_AVAILABLE for the rest., Like a real connector whose tab dies: reports a crash, then never returns., _run(), test_crashed_tab_stops_the_carrier_without_waiting_for_the_timeout() (+2 more)

### Community 45 - "RfqInputSection.tsx"
Cohesion: 0.18
Nodes (13): RateSearchFormProps, DEMO_EXAMPLES, RfqInputSection(), RfqInputSectionProps, Box(), fieldName(), laneFlags(), RfqLane (+5 more)

### Community 46 - "dithered-logo.tsx"
Cohesion: 0.19
Nodes (15): applyMaskInversion(), buildRoundedMask(), DEFAULTS, DitherConfig, DitheredLogo(), DitheredLogoProps, drawParticles(), errorDiffusionDither() (+7 more)

### Community 47 - "👥 The 5 Agent Roles"
Cohesion: 0.13
Nodes (14): 1. Intake Agent (Email Listener), 2. Sourcing Orchestrator (The Coordinator), 3. Sourcing & Scraping Agent (Rates Engine), 4. Finance & Costing Agent (Excel Compiler), 5. Email Draft Agent (Communicator), 📋 Executive Summary, 🛠️ Implementation Stages, Phase 1: Email Integration (Week 1-2) (+6 more)

### Community 48 - "HapagLloydConnector"
Cohesion: 0.06
Nodes (33): HapagLloydConnector, HapagServiceUnavailableException, Exception, Normalize various date formats (e.g. 2026-05-31, 31.05.2026, 31 May 2026, 31…, Robustly selects options from Hapag-Lloyd custom dropdown lists. Types the…, Detects the Microsoft B2C identity/OAuth login page. Hapag can silently bounce…, Guards against the session-expiry-mid-crawl failure mode: the existing redirect…, Crawls Hapag-Lloyd sailing schedules from the Schedule tab. (+25 more)

### Community 49 - "CarrierResultStatus"
Cohesion: 0.04
Nodes (44): Override to immediately return CONNECTOR_NOT_AVAILABLE., Fill in the carrier's search form and submit a quote search. Args: request: The…, Required abstract method implementation; delegates to run_full_search., Batch (RFQ) mode: the base implementation drives a browser page, so answer from…, Called by job_service once per container type (request.container_type). All…, Executes full rate search against Hapag-Lloyd Prices API. Queries each…, MaerskConnector, Execute the full search flow with Progressive Lazy Loading: 1. Login 2. Search… (+36 more)

### Community 50 - "selector_memory.py"
Cohesion: 0.24
Nodes (12): get_approved_selector(), _load_memory(), Selector Memory — stores and retrieves human-approved selector patches., Loads memory JSON file. Returns empty dict if file is missing or invalid., Saves memory dict back to JSON file., Looks up if there is an approved replacement selector for the given carrier and…, Stores an approved replacement selector., Marks any proposed selector for this step as REJECTED. (+4 more)

### Community 51 - "CurrencyManager"
Cohesion: 0.23
Nodes (7): convert_currency_to_usd(), CurrencyManager, get_all_exchange_rates(), Any, Currency Exchange Rate Service — manages currency conversions and custom…, update_exchange_rate(), threading

### Community 52 - "CarrierSearchResult"
Cohesion: 0.18
Nodes (15): CarrierSearchResult, Tracks the result of searching a specific carrier for a rate search., Copy the connector's "port not found" note onto the result row, if it made one., _store_port_not_found(), Admin carrier on/off switch: stored on the volume, and a switched-off carrier…, test_switched_off_carrier_is_skipped(), run(), _miss() (+7 more)

### Community 53 - "test_hapag_freetime.py"
Cohesion: 0.18
Nodes (15): _apply_freetime_to_quote(), freetime_days(), match_freetime_entry(), Any, Destination free time from config/hapag_freetime.json, shared by the Hapag-…, Days for this container from a table entry ({"20GP": n, "40GP": n} or a bare…, The table entry whose country name appears in `text` as whole words. Whole…, days() (+7 more)

### Community 54 - "🚢 Infreight Sourcing & Ocean Rate Automation System"
Cohesion: 0.14
Nodes (13): 1. Multi-Carrier Automation Engine, 2. Intelligent Surcharge & Charge Classifier Engine (`charge_classifier.py`), 3. Container Comparison Matrix & Excel Export Engine, 🚢 Infreight Sourcing & Ocean Rate Automation System, 🌟 Key Capabilities, 📄 License & Confidentiality, Prerequisites, 🛠️ Project Structure (+5 more)

### Community 55 - "RateSearchRequest"
Cohesion: 0.08
Nodes (28): RateSearchRequest, CMA CGM end-to-end test — login + search + extract quotes., # IMPORTANT: Clear ALL proxy env vars BEFORE any import triggers load_dotenv()…, test_cma(), run_test(), run_test(), test_montreal_ramp(), debug_cma() (+20 more)

### Community 56 - "[2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split"
Cohesion: 0.15
Nodes (13): G2 Stress Test: "Hi, Please book the below as per your quote ref INF-2026-0842:…, H1 Stress Test: Table with 2 distinct rows: Row 1: POL Singapore, POD Jakarta,…, test_g2_booking_confirmation_guardrail(), test_h1_table_deduplication_two_pairs(), [2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split, Booking Confirmation / Instructions Intercept Guardrail G2 (`rfq_agent.py` & `RfqInputSection.tsx`), Commercial Sales Desk Intelligence (`sales_notes`), Deterministic Port Alias Resolver (`ports_aliases.json`) (+5 more)

### Community 57 - "._parse_offer_response_to_quotes"
Cohesion: 0.17
Nodes (6): Any, Constructs OpenAPI compliant OfferRequest payload., Maps a Prices API rate onto the categories the portal scraper produces (freight…, Leg locations are UnLocation/Facility objects per the spec; tolerate plain…, Renders a graduated weight tier (e.g. Heavy Lift: 18-99 TON) in the portal's…, Parses Hapag-Lloyd OfferResponse JSON into InFreight QuoteSchema objects.

### Community 58 - "🛠 Detailed Carrier Log"
Cohesion: 0.15
Nodes (12): 🛠 Detailed Carrier Log, 🟢 GreenX, 🟠 Hapag-Lloyd, Infreight Ocean Carrier Rate Automation — Development Log, 🚀 Key Highlights & Architectural Changes, 🔌 Local Laptop Deployment (Self-Hosted Worker), 🔵 Maersk, 💗 ONE (Ocean Network Express) (+4 more)

### Community 59 - "orbit-card-stack.tsx"
Cohesion: 0.22
Nodes (13): HalftoneAvatar(), HalftoneAvatarProps, hashSeed(), pick(), clamp(), initialsFor(), laneLabel(), OrbitCardStack() (+5 more)

### Community 60 - "silk-aurora.tsx"
Cohesion: 0.19
Nodes (9): hexToRgb01(), sanitizeHexColor(), SilkAurora(), SilkAuroraProps, WebGLErrorBoundary, WebGLErrorBoundaryProps, WebGLErrorBoundaryState, WebGLFallback() (+1 more)

### Community 61 - "[2026-08-07] — Carrier Specific Free Time, Demurrage/Detention Splitting, MSC CDD Surcharges, OOCL Nearby Route Filtering & Favicon Cache Busting"
Cohesion: 0.40
Nodes (5): [2026-08-07] — Carrier Specific Free Time, Demurrage/Detention Splitting, MSC CDD Surcharges, OOCL Nearby Route Filtering & Favicon Cache Busting, Demurrage & Detention Split Fields Across System (`schema.py`, `msc_connector.py`, `maersk_connector.py`, `one_connector.py`, `greenx_connector.py`, `cma_connector.py`, `oocl_connector.py`, `ResultsTable.tsx`, `excel_export.py`), Favicon Cache Busting & Brand Icon (`layout.tsx`, `icon.png`, `favicon.ico`), Hapag-Lloyd MHD (Merchant Haulage Detention) PDF Tariff Scraper (`hapag_freetime_scraper.py`, `hapag_freetime.json`), MSC Cargo Data Declaration [CDD] & Working Days Free Time (`msc_connector.py`)

### Community 62 - "[2026-06-30] — ONE Multi-Container & Sold-Out, GreenX Surcharge Intake, Free-Time Fixes, Maersk Diagnosis"
Cohesion: 0.29
Nodes (7): [2026-06-30] — ONE Multi-Container & Sold-Out, GreenX Surcharge Intake, Free-Time Fixes, Maersk Diagnosis, GreenX — Only Basic Ocean Freight & LSS Folded Into Final Value, MAERSK — "Quotes Found" but Empty Excel (Diagnosis), ONE — All-Container-Type Search Returning 0 Quotes, ONE — Multi-Container Breakdown Triple-Counted / Inflated Final Value, ONE — Sold-Out ("Notify Me") Sailings Appearing as Quotes, Performance/Reliability — Stop Copying Chrome Caches During Profile Clone/Sync

### Community 63 - "[2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup"
Cohesion: 0.22
Nodes (8): [2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup, Chromium Cache Auto-Cleanup (Railway Storage Bloat Prevention), CMA CGM — 30-Second Timeout on Sold Out Cards, CMA CGM — Free Time Regex Too Strict, CMA CGM — Routing Regex Not Matching "via LEKKI, LA, NG", Excel Export — Routing & Free Time Columns Always Empty, Excel Export — Sold Out Rows Not Showing, Maersk — Hardcoded Port Overrides

### Community 64 - "ai_repair_agent.py"
Cohesion: 0.33
Nodes (6): _local_fuzzy_repair(), AI Repair Agent — diagnoses Playwright step failures and suggests selector…, A local rule-based heuristic to locate reasonable buttons or inputs when Gemini…, Analyzes the failure context and DOM content to suggest a selector repair. Uses…, suggest_fix(), bs4

### Community 65 - "RFQParseResult"
Cohesion: 0.17
Nodes (12): parse_rfq_endpoint(), post, API routes for RFQ parsing agent., Parse a free-text RFQ email or message into a structured RateSearchRequest…, RFQParseRequest, RFQParseResult, Test Image 2: Air rate request generates 3 drafts to Glenn (AWOT), Jing Hui…, Test Guardrail: Detects Reefer container request and returns unsupported_cargo… (+4 more)

### Community 66 - "GreenX — Surcharge Intake Fix (2026-06-30)"
Cohesion: 0.22
Nodes (8): Charges that must be taken into the final value (USD only), Files changed, Fix, GreenX — Surcharge Intake Fix (2026-06-30), Per-B/L charges (billed once per booking, added in full to *each* container type), Problem, Root cause, Verification

### Community 67 - "Admin Page & Port Prioritization Guide"
Cohesion: 0.25
Nodes (7): 1. Popular Ports (UN/LOCODEs), 2. Boosted Countries, Admin Page & Port Prioritization Guide, 🔒 How to Access the Admin Page, ⚙️ How to Use Port Prioritization, ⚡ Important Notes, 📝 Step-by-Step Example

### Community 68 - "[2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning"
Cohesion: 0.14
Nodes (13): Verifies the "I am the price owner" radio is genuinely checked, piercing shadow…, [2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning, [2026-07-03] — OOCL FreightSmart Autoclear, Hapag Price Leak & Redirect fixes, Maersk Cache Scoping, Dallas Overrides, GreenX — "No Quotes" Reported While Quotes Visibly Loaded in VNC, Hapag-Lloyd — Configurable Pacing & Redundant-Wait Removal, Hapag-Lloyd — Price Leaks, Column Matching, and Redirect Recovery, Job Scheduler — Concurrency Default, Maersk — 0.0-USD / "Not Open" Card Flakiness (the "Quotes Found but Empty Excel" root causes) (+5 more)

### Community 69 - "test_self_healing.py"
Cohesion: 0.20
Nodes (13): detect_manual_action_required(), Manual Action Detector — identifies pages requiring human verification (2FA,…, Scans the current Playwright page to see if a CAPTCHA, Cloudflare challenge,…, clean_selector_memory(), asyncio, fixture, Self-Healing Layer & Chatbot Test Suite. Tests the selector memory, failure…, Wipes the selector memory JSON file before and after each test. (+5 more)

### Community 70 - "dependencies"
Cohesion: 0.15
Nodes (13): dependencies, class-variance-authority, clsx, exceljs, lucide-react, next, next-themes, @radix-ui/react-slot (+5 more)

### Community 71 - "carrier_switches.py"
Cohesion: 0.35
Nodes (10): get_switches(), off_message(), _path(), Admin on/off switch per carrier, for when a carrier's site is down or under…, Every switchable carrier: {"enabled", "reason", "updated_by", "updated_at"}; on…, The message for a switched-off carrier's result, or None when it is on., _read(), set_switch() (+2 more)

### Community 72 - "deploy"
Cohesion: 0.25
Nodes (7): build, builder, deploy, restartPolicyMaxRetries, restartPolicyType, startCommand, $schema

### Community 73 - ".search_quotes"
Cohesion: 0.13
Nodes (9): extract_locode_and_country(), prepare_maersk_query(), Fills an autocomplete field using the proven original element-level…, Extracts LOCODE and country name from text like 'CASABLANCA, MOROCCO (MACAS)'…, Maps standard container search codes (e.g. 'DRY 20', '20GP') to Maersk Spot…, Scores a Maersk autocomplete dropdown suggestion. NOTE: The nested/indented…, Tries to click a matching option from ONE's visible dropdown. Returns True only…, get_cached_carrier_port() (+1 more)

### Community 74 - "test_panama_canal_surcharge.py"
Cohesion: 0.12
Nodes (17): parse_msc_modal_charges(), Parses charges from MSC BreakdownModal text. Correctly includes charges whose…, Sort container types in standard order: DRY 20 (20GP) -> DRY 40 (40GP) -> DRY…, sort_container_types(), Test MSC charges parsing for Singapore to Conakry, Guinea (40GP). Charges with…, Test when only some surcharges have the payment condition., test_msc_charges_mixed_conditions(), test_msc_charges_singapore_to_conakry_guinea() (+9 more)

### Community 75 - "Summary of Changes — July 20, 2026"
Cohesion: 0.29
Nodes (6): 1. AI RFQ Front Door & Air Freight Support (Phase A), 2. Multi-Origin & Gappy List Parsing for Sea RFQs (Phase B), 3. Search Form Streamlining (Form Input Restrictions), 4. Native Gemini 2.5 Flash API & Chatbot Resiliency, 5. Verification & Test Suite, Summary of Changes — July 20, 2026

### Community 76 - "safe_step.py"
Cohesion: 0.12
Nodes (17): capture_page_state(), Page Observer — captures page state (screenshot, DOM, visible text) on failure., Captures screenshot, DOM HTML, and inner text of the current page. Saves…, generate_report(), Repair Report — generates and saves diagnosis reports on Playwright selector…, Assembles a comprehensive repair report and writes it as JSON and Markdown…, Safe Step — Playwright action execution wrapper with manual intervention pause…, Updates the status of a carrier search in the database. (+9 more)

### Community 77 - "[2026-05-29 – 2026-05-30] — Hapag-Lloyd Full Integration"
Cohesion: 0.40
Nodes (5): [2026-05-29 – 2026-05-30] — Hapag-Lloyd Full Integration, Hapag-Lloyd — Dropdown Autocomplete Issues, Hapag-Lloyd — Live Connector Implementation, Hapag-Lloyd — Onboarding Modal Blocking Form Interaction, Hapag-Lloyd — Search Button Selector Failures

### Community 78 - "resolve_port_alias"
Cohesion: 0.33
Nodes (6): _load_port_aliases_config(), Deterministically resolves a port string against ports_aliases.json and the…, resolve_port_alias(), Test that resolve_port_alias cleans 'City, Country' and parenthetical notes to…, test_resolve_city_country_format_to_clean_database_port_name(), Clean Search Dropdown Port Name Resolution (`rfq_agent.py` & `port_manager.py`)

### Community 79 - "test_brightdata.py"
Cohesion: 0.40
Nodes (5): get_title(), Script to test fetching CMA CGM pricing page using Bright Data Web Access HTTP…, test_brightdata_api(), urllib_error, urllib_request

### Community 80 - "._mouse_glide_to"
Cohesion: 0.24
Nodes (5): Clicks an element with pre-click and post-click human-like reaction pauses., Visible page size. With no_viewport the size comes from the real window., Move the real mouse pointer to (x, y) along a slightly curved, uneven path.…, Scroll with the wheel if needed, glide to the element, hover, then press and…, Small aimless pointer drift, as a person does while a page loads.

### Community 81 - "Design system — read before touching any UI"
Cohesion: 0.33
Nodes (5): Animation rules, Client-only preferences, Design system — read before touching any UI, This is NOT the Next.js you know, Use tokens, not raw colours

### Community 82 - "tunnel_relay/main.py"
Cohesion: 0.25
Nodes (8): api_route, fastapi_middleware_cors, health(), get, Request, websocket, relay_request(), websocket_endpoint()

### Community 83 - "layout.tsx"
Cohesion: 0.22
Nodes (7): frontend_src_app_globals, instrumentSans, inter, metadata, viewport, ThemeProvider(), next-themes

### Community 84 - "._fs_extract_rows"
Cohesion: 0.17
Nodes (8): clean_vessel_name(), get_booking_start_date(), date, Opens the Details dialog for a card, clicks the Charge Breakdown tab, extracts…, Collects result cards from the FreightSmart quote results page., Applies the business rules and pairs FreightSmart prices with crawled…, OOCL — FreightSmart Price Quotes (E-Quote / E-Spot) Paired With Sailing Schedules, OOCL Nearby Route Recommendations Suppression (`oocl_connector.py`)

### Community 85 - "compute_admin_analytics"
Cohesion: 0.25
Nodes (8): compute_admin_analytics(), get_clean_lane_key(), normalize_lane_port(), Any, AsyncSession, Normalize port string to cleanly aggregate naming variations., Returns (norm_origin, norm_dest, display_lane_key)., Compute full consolidated analytics payload for the admin dashboard.

### Community 86 - "tunnel_client.py"
Cohesion: 0.17
Nodes (11): ambiguous_python_import_b35980c0aa01, argparse, asyncio, Integration tests for authentication, legacy user password setup, pending…, test_full_auth_lifecycle(), httpx, pytest_asyncio, handle_request() (+3 more)

### Community 88 - "os"
Cohesion: 0.06
Nodes (50): asyncio, Base Carrier Connector — abstract base class for all carrier connectors. Each…, CMA CGM Live Connector — Playwright automation. Credentials read from env:…, Hapag-Lloyd Prices API Connector (REST API v2.1.4). Provides real-time rate…, # NOTE: No start date fill needed — schedule page defaults to today,, Hapag-Lloyd Live Connector -- Playwright automation. Credentials read from env:…, Maersk Browser Connector — Playwright automation using your real Google Chrome…, # NOTE: Bright Data Web Unlocker proxies break Playwright browser sessions… (+42 more)

### Community 89 - "[2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History"
Cohesion: 0.40
Nodes (5): [2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History, Admin User Search History & SGT GMT+8 Conversion (`AdminDashboard.tsx`), GreenX (Evergreen) Card Isolation & Surcharge Parsing (`greenx_connector.py`), Multi-Route Batch Execution Engine (`batch_engine.py`), OOCL FreightSmart 28-Day Calendar Expansion (`oocl_connector.py`)

### Community 92 - "devDependencies"
Cohesion: 0.22
Nodes (9): devDependencies, eslint, eslint-config-next, tailwindcss, @tailwindcss/postcss, @types/node, @types/react, @types/react-dom (+1 more)

### Community 94 - "handle_chat_query"
Cohesion: 0.33
Nodes (6): get_recent_search_status_context(), handle_chat_query(), _local_chatbot_fallback(), Intelligent responder for search status, carrier guidance, air/sea info, and…, Queries the database for the most recent rate search status to give the chatbot…, Sends the chat message and history to native Gemini 2.5 Flash API. If Gemini…

### Community 95 - "playwright_async_api"
Cohesion: 0.19
Nodes (8): dump_options(), main(), Diagnostic: dump ALL dropdown options (text + innerHTML) when typing 'DEHAM'…, check_and_wait_for_captcha(), login(), main(), Script to test Playwright browser launching using your REAL Google Chrome…, playwright_async_api

### Community 96 - "frontend/README.md"
Cohesion: 0.50
Nodes (3): Deploy on Vercel, Getting Started, Learn More

### Community 97 - "pytest"
Cohesion: 0.17
Nodes (8): parse_hapag_card_text_mock(), Verify that multi-leg/feeder routes take the final arrival ETA and 28 days TT., Mock implementation of the JS evaluate logic inside hapag_lloyd_connector.py., test_hapag_multi_leg_schedule_extraction(), Tests for rate search API endpoints., Placeholder test — integration tests require DB setup., test_placeholder(), pytest

### Community 98 - "[2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control"
Cohesion: 0.40
Nodes (5): [2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control, Concurrency Limit Queue & Admin Control Panel, MSC — Mediterranean Shipping Company Connector Implementation, ONE — Inbound Free Time Swap & Scraper Upgrade, OOCL — Orient Overseas Container Line Connector Implementation

### Community 99 - "[2026-08-04 - 2026-08-06] — CMA CGM Dynamic RAMP/POD Rerouting, Brand Excel Styling, Port Synonym Matching & Tunnel Relays"
Cohesion: 0.40
Nodes (5): [2026-08-04 - 2026-08-06] — CMA CGM Dynamic RAMP/POD Rerouting, Brand Excel Styling, Port Synonym Matching & Tunnel Relays, Brand-Aligned Excel Export Styling (`excel_export.py`), CMA CGM Dynamic RAMP / POD Advisory Banner Detection (`cma_connector.py`), Dynamic Carrier Port Overrides & Admin Registry (`PortManager`, `AdminDashboard.tsx`), Railway WebSocket Tunnel Relay & Failover (`tunnel_client.py`, `run_tunnel_client.bat`, `FailoverFetch`)

### Community 101 - "[2026-05-20 – 2026-05-22] — Port Resolution & Frontend Improvements"
Cohesion: 0.50
Nodes (4): [2026-05-20 – 2026-05-22] — Port Resolution & Frontend Improvements, Excel Export — ETA Column & Container Type Header, Frontend Light Mode & CORS Fix, Port Resolution System

### Community 102 - "[2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash"
Cohesion: 0.40
Nodes (5): [2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash, AI RFQ Front Door & Air Freight Support, Multi-Origin & Gappy List Parsing (Sea RFQs), Native Gemini 2.5 Flash Direct API Integration, Search Form Streamlining

### Community 103 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, dev, lint, start

### Community 106 - "[2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes"
Cohesion: 0.50
Nodes (4): [2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes, CMA CGM — Chrome Profile Bypass, ONE — Date Formatting & Charge Breakdown Pollution, ONE — Date Picker Pre-selection Issue

### Community 116 - "eslint.config.mjs"
Cohesion: 0.50
Nodes (3): eslintConfig, eslint, eslint-config-next

### Community 117 - "[2026-05-23 – 2026-05-24] — Maersk Shadow DOM & Stealth Upgrades"
Cohesion: 0.50
Nodes (4): [2026-05-23 – 2026-05-24] — Maersk Shadow DOM & Stealth Upgrades, Maersk — 2FA/CAPTCHA Human-in-the-Loop via noVNC, Maersk — Login Credential Autofill Corruption, Maersk — Shadow DOM Piercing for MDS Web Components

### Community 120 - "Architecture Overview"
Cohesion: 0.50
Nodes (4): Architecture Overview, Carrier Connector Lifecycle, Charge Classification Rules, Search Flow

### Community 121 - "[2026-05-25 – 2026-05-26] — VNC Display Isolation & Proxy Integration"
Cohesion: 0.67
Nodes (3): [2026-05-25 – 2026-05-26] — VNC Display Isolation & Proxy Integration, Bright Data ISP Proxy Integration, VNC Display Isolation for Concurrent Carriers

### Community 122 - "[2026-05-31] — Multi-Instance Support & Charge Classification"
Cohesion: 0.67
Nodes (3): [2026-05-31] — Multi-Instance Support & Charge Classification, Charge Classification Improvements, Multi-Instance Concurrent Searches

## Knowledge Gaps
- **312 isolated node(s):** `Config`, `install_pi.sh script`, `eslintConfig`, `nextConfig`, `name` (+307 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 938 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **20 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Changelog` connect `Changelog` to `[2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History`, `[2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control`, `[2026-08-04 - 2026-08-06] — CMA CGM Dynamic RAMP/POD Rerouting, Brand Excel Styling, Port Synonym Matching & Tunnel Relays`, `[2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning`, `[2026-05-20 – 2026-05-22] — Port Resolution & Frontend Improvements`, `[2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash`, `[2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes`, `[2026-05-29 – 2026-05-30] — Hapag-Lloyd Full Integration`, `[2026-05-23 – 2026-05-24] — Maersk Shadow DOM & Stealth Upgrades`, `[2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split`, `[2026-05-25 – 2026-05-26] — VNC Display Isolation & Proxy Integration`, `[2026-05-31] — Multi-Instance Support & Charge Classification`, `Architecture Overview`, `[2026-08-07] — Carrier Specific Free Time, Demurrage/Detention Splitting, MSC CDD Surcharges, OOCL Nearby Route Filtering & Favicon Cache Busting`, `[2026-06-30] — ONE Multi-Container & Sold-Out, GreenX Surcharge Intake, Free-Time Fixes, Maersk Diagnosis`, `[2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup`?**
  _High betweenness centrality (0.336) - this node is a cross-community bridge._
- **Why does `Maersk — Free Time Extraction from Card Text` connect `Changelog` to `RateResults.tsx`?**
  _High betweenness centrality (0.302) - this node is a cross-community bridge._
- **Are the 32 inferred relationships involving `RateSearchRequest` (e.g. with `create_batch_rate_search()` and `create_rate_search()`) actually correct?**
  _`RateSearchRequest` has 32 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `cn()` (e.g. with `Reuse the primitives` and `7. Conventions to follow from here`) actually correct?**
  _`cn()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 21 inferred relationships involving `CarrierResultStatus` (e.g. with `safe_step()` and `update_carrier_status()`) actually correct?**
  _`CarrierResultStatus` has 21 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Config`, `install_pi.sh script`, `eslintConfig` to the rest of the system?**
  _312 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `BaseCarrierConnector` be split into smaller, more focused modules?**
  _Cohesion score 0.05576441102756892 - nodes in this community are weakly interconnected._