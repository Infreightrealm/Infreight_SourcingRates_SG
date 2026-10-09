# Graph Report - Infreight_SourcingRates_SG  (2026-10-09)

## Corpus Check
- 246 files · ~1,162,997 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 23 file(s) not represented in the graph (top: (none) 10, .bat 6, .conf 2)

## Summary
- 2368 nodes · 5849 edges · 128 communities (109 shown, 19 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 334 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `41dc261f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- port_manager.py
- CarrierResultStatus
- cn
- user_routes.py
- auth_routes.py
- browser_cleanup.py
- OOCLConnector
- api.ts
- PortManager
- safe_step.py
- CMAConnector
- normalizer.py
- job_service.py
- MaerskConnector
- ._fs_run
- HapagLloydAPIConnector
- preferences.ts
- test_rfq_agent.py
- sys
- SocialWidget.tsx
- lucide-react
- GreenXConnector
- list_colleagues
- port_routes.py
- backend/main.py
- rate_search_routes.py
- MSCConnector
- parse_rfq
- types.ts
- AIBrowserAgent
- CarrierSearchResult
- ONEConnector
- _Page
- Engineering Report: Sourcing Portal Enhancements & Scraping Pipeline Stability
- Changelog
- AdminOverview.tsx
- package.json
- datetime
- RateResults.tsx
- SearchQueueManager
- ChargeCategory
- Frontend Redesign — Componentry Design System, Workspace & Launch Intro (2026-09-07)
- compilerOptions
- resolve_port_for_carrier
- test_carrier_timeout.py
- app/page.tsx
- dithered-logo.tsx
- 👥 The 5 Agent Roles
- HapagLloydConnector
- MockCarrierConnector
- selector_memory.py
- CurrencyManager
- get_port_by_code
- test_hapag_freetime.py
- 🚢 Infreight Sourcing & Ocean Rate Automation System
- os
- [2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split
- ai_agent.py
- 🛠 Detailed Carrier Log
- one_connector.py
- silk-aurora.tsx
- [2026-08-07] — Carrier Specific Free Time, Demurrage/Detention Splitting, MSC CDD Surcharges, OOCL Nearby Route Filtering & Favicon Cache Busting
- [2026-06-30] — ONE Multi-Container & Sold-Out, GreenX Surcharge Intake, Free-Time Fixes, Maersk Diagnosis
- [2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup
- ai_repair_agent.py
- RFQParseResult
- GreenX — Surcharge Intake Fix (2026-06-30)
- Admin Page & Port Prioritization Guide
- ._verify_price_owner_selected
- test_self_healing.py
- dependencies
- AdminUsers.tsx
- deploy
- .search_quotes
- test_panama_canal_surcharge.py
- Summary of Changes — July 20, 2026
- safe_step
- [2026-05-29 – 2026-05-30] — Hapag-Lloyd Full Integration
- resolve_port_alias
- json
- ._fs_dismiss_modals
- Design system — read before touching any UI
- tunnel_relay/main.py
- [2026-06-03] — CMA CGM Routing & Free Time Extraction
- [2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning
- ._fs_extract_rows
- test_auth_routes.py
- RateLimiter
- RateSearchRequest
- [2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History
- websockify_carrier_proxy
- ref_fs
- devDependencies
- .search_port
- fill_container_card
- diagnose_greenx_dropdown.py
- frontend/README.md
- pytest
- [2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control
- ._save_carrier_overrides
- test_belawan_aden.py
- [2026-05-20 – 2026-05-22] — Port Resolution & Frontend Improvements
- [2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash
- scripts
- Working in this repository
- [2026-05-18 – 2026-05-19] — Railway Deployment & Docker
- install_pi.sh
- models/__init__.py
- postcss.config.mjs
- QuoteSchema
- [2026-05-23 – 2026-05-24] — Maersk Shadow DOM & Stealth Upgrades
- cma_cgm_connector.py
- SearchStatus
- Architecture Overview
- [2026-05-25 – 2026-05-26] — VNC Display Isolation & Proxy Integration
- [2026-06-01] — Hapag-Lloyd Sold Out Detection & Date Parsing
- .suggest_ports
- alembic
- maersk_connector.py
- main
- [2026-06-02] — Hapag-Lloyd Transshipment & Duplicate Fix

## God Nodes (most connected - your core abstractions)
1. `RateSearchRequest` - 161 edges
2. `cn()` - 89 edges
3. `CarrierResultStatus` - 69 edges
4. `QuoteSchema` - 67 edges
5. `User` - 59 edges
6. `PortManager` - 58 edges
7. `HapagLloydConnector` - 56 edges
8. `CMAConnector` - 55 edges
9. `MaerskConnector` - 51 edges
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

## Communities (128 total, 19 thin omitted)

### Community 0 - "port_manager.py"
Cohesion: 0.25
Nodes (12): add_carrier_override(), add_custom_port(), delete_carrier_override(), delete_custom_port(), get_carrier_overrides(), get_custom_ports(), get_popular_ports_config(), search_port() (+4 more)

### Community 1 - "CarrierResultStatus"
Cohesion: 0.06
Nodes (28): ABC, BaseCarrierConnector, NotAvailableConnector, Any, Open the price breakdown / detail view for a specific quote. Args: quote_ref:…, Extract individual charge line items from the price breakdown. Returns: List of…, Abstract base class for carrier portal connectors., Detects if a CAPTCHA, Turnstile, hCaptcha, reCAPTCHA, or 2FA screen is… (+20 more)

### Community 2 - "cn"
Cohesion: 0.07
Nodes (51): Reuse the primitives, New primitives — `frontend/src/components/ui/`, LoadingState(), LoginModalProps, PortAutocompleteProps, DEMO_EXAMPLES, Box(), fieldName() (+43 more)

### Community 3 - "user_routes.py"
Cohesion: 0.06
Nodes (84): get_current_user(), get_me(), get, Dependency that strictly requires an authenticated active member., Get profile of currently signed-in user., admin_delete_user(), AdminLoginRequest, approve_user() (+76 more)

### Community 4 - "auth_routes.py"
Cohesion: 0.05
Nodes (78): clear_session_cookie(), get_current_user_optional(), login(), LoginRequest, logout(), AsyncSession, BaseModel, post (+70 more)

### Community 5 - "browser_cleanup.py"
Cohesion: 0.12
Nodes (30): _is_chrome(), _is_playwright_driver(), _kill(), kill_profile_browsers(), _proc_supported(), Cleanup for Chrome browsers and temporary profiles that a failed close leaves…, Kill every automated Chrome and Playwright driver. Only call this when no…, Replace `master_dir` with a copy of `source_dir` (caches and lock files left… (+22 more)

### Community 6 - "OOCLConnector"
Cohesion: 0.20
Nodes (8): OOCLConnector, Attempts to automatically click the Cloudflare Turnstile 'Verify you are human'…, asyncio, test_oocl_cwx_different_port_pair_different_amount(), test_oocl_cwx_heavy_weight_charge_not_applied_40gp(), test_oocl_cwx_heavy_weight_charge_not_applied_under_threshold(), test_oocl_cwx_port_pair_surabaya_karachi(), test_oocl_cwx_port_pair_without_cwx()

### Community 7 - "api.ts"
Cohesion: 0.08
Nodes (59): AdminDashboard(), UserRecord, LoginContent(), AdminCarriers(), when(), AdminPortFixes(), AdminPortFixesProps, ago() (+51 more)

### Community 8 - "PortManager"
Cohesion: 0.14
Nodes (5): PortManager, Retrieve verified carrier port name from persistent cache by UN/LOCODE,…, Cache verified carrier port name and save persistently to…, Clean and normalize user input for port searching., Retrieve port data by full UN/LOCODE (e.g., 'SGSIN').

### Community 9 - "safe_step.py"
Cohesion: 0.17
Nodes (12): capture_failure_context(), Exception, Failure Detector — parses and structures error context from failed Playwright…, Assembles a standardized diagnostic dictionary containing all available details…, Manual Action Detector — identifies pages requiring human verification (2FA,…, capture_page_state(), Page Observer — captures page state (screenshot, DOM, visible text) on failure., Captures screenshot, DOM HTML, and inner text of the current page. Saves… (+4 more)

### Community 10 - "CMAConnector"
Cohesion: 0.08
Nodes (17): CMAConnector, Ensures 'Ramp' is explicitly selected under 'Type of location' toggle buttons…, Scans for Route, POL (Port of Loading), or POD (Port of Discharge) dropdown…, Clears the currently selected Destination port tag/card, re-types the locode,…, Dynamically extracts any recommended 5-letter POD LOCODE mentioned in the…, Detects if CMA CGM displayed an advisory banner message: "Looking for AEJEA or…, Handles the 'Customer account' -> 'Role (you are acting as)' dropdown on CMA…, Repeatedly clicks 'More results' if visible to load ALL quotes on the page. (+9 more)

### Community 11 - "normalizer.py"
Cohesion: 0.12
Nodes (22): is_weight_surcharge_applicable(), Evaluates whether a weight-tier or overweight surcharge is applicable for the…, calculate_final_freight_value(), classify_and_organize_charges(), format_maersk_date(), normalize_quote(), Normalizer — calculates the final freight value and normalizes quote data.…, Takes raw charge line items and classifies them. Args: raw_charges: list of… (+14 more)

### Community 12 - "job_service.py"
Cohesion: 0.06
Nodes (56): get_route_health(), Get carrier search reliability & route health matrix across origin-destination…, close_all_active_connectors(), Force close all active carrier connectors and their Playwright Chrome windows., get_async_session_maker(), Get the session maker for use outside of FastAPI dependency injection., Quote, Represents a single freight quote from a carrier. (+48 more)

### Community 13 - "MaerskConnector"
Cohesion: 0.08
Nodes (17): _is_logged_in_url(), MaerskConnector, flatten_tree(), Wait until the login page either redirects to a signed-in page or shows its…, Execute the full search flow with Progressive Lazy Loading: 1. Login 2. Search…, Extracts freetime, demurrage, and detention from the 'Import D&D fees' tab…, Extracts the routing details from the 'Route & other details' accordion.…, Splits a single raw multi-container quote card into multiple QuoteSchema… (+9 more)

### Community 14 - "._fs_run"
Cohesion: 0.15
Nodes (7): Lock, Full FreightSmart phase: login â†’ fill quote form â†’ search â†’ extract rows., Shadow-DOM-aware check for whether the onboarding tour heading is on screen., Runs CONCURRENTLY with the rest of the FreightSmart form-filling flow and…, Two-step FreightSmart login: 1. freightsmart.oocl.com/app/login â€” email +…, Opens the 'Container Type and Quantity' picker (General tab: 20GP/20RF(NOR),…, Event

### Community 15 - "HapagLloydAPIConnector"
Cohesion: 0.07
Nodes (25): HapagLloydAPIConnector, Any, AsyncClient, Direct REST API connector for Hapag-Lloyd Prices API v2.1.4., API connectors do not require browser login sessions., No browser session to reset between batch routes., Resolves a free-text port name or string (e.g. 'Singapore', 'Hamburg, Germany…, Hapag-Lloyd Prices API requires earliestDepartureDate to be at least 4 calendar… (+17 more)

### Community 16 - "preferences.ts"
Cohesion: 0.09
Nodes (33): LaunchIntro(), SearchHistoryItem, derive(), Derived, startOfDay(), UsageStats(), ChoiceCard(), Toggle() (+25 more)

### Community 17 - "test_rfq_agent.py"
Cohesion: 0.10
Nodes (28): asyncio, Unit tests for the Gemini AI RFQ Agent service (parse_rfq). Includes…, Test Image 4: Steel Plate ex Pasir Gudang / Tanjung Pelepas for 20' & 40'., Test Guardrail: Detects LCL request., Test OpenFlights 6,072 IATA airport dataset and shorthand alias resolution., Test Pak Shaun email: "Hi team, need rate for 10x20GP from PK to JKT. Urgent…, Test Multimodal Image Input validation and parsing., Test Stress Test Scenario: "Dear Sir, Pls quote 3 x 20'FCL Singapore to… (+20 more)

### Community 18 - "sys"
Cohesion: 0.11
Nodes (13): Wrapper script to set Windows event loop policy before starting Uvicorn. This…, parse_hapag_pdf(), scrape_hapag_freetime(), Script to test Playwright browser launching using your REAL Google Chrome…, Tests for rate search API endpoints., Placeholder test — integration tests require DB setup., test_placeholder(), pdfplumber (+5 more)

### Community 19 - "SocialWidget.tsx"
Cohesion: 0.10
Nodes (34): ACCENT_COLORS, errorMessage(), relativeTime(), resizeImageToDataUrl(), SocialWidget(), SocialWidgetProps, EMOJI_GROUPS, EmojiPicker() (+26 more)

### Community 20 - "lucide-react"
Cohesion: 0.07
Nodes (38): AppHeader(), AppHeaderProps, initials(), systemStatus(), ChatWidget(), ChatWidgetProps, Message, ACTION_STATUSES (+30 more)

### Community 21 - "GreenXConnector"
Cohesion: 0.09
Nodes (14): GreenXConnector, date, Overrides base search runner to query all 3 sizes at once and cache the…, Type a LOCODE into the autocomplete field and click the first visible dropdown…, Find quantity input next to or below label_text and fill it., Find the exact individual quote card container row encompassing dates, rates,…, Dismiss any cookie/alert modal that would intercept pointer events., Splits a single raw multi-container quote card into multiple QuoteSchema… (+6 more)

### Community 22 - "list_colleagues"
Cohesion: 0.11
Nodes (23): get_conversation(), list_colleagues(), poke_colleague(), PokeRequest, AsyncSession, BaseModel, delete, get (+15 more)

### Community 23 - "port_routes.py"
Cohesion: 0.29
Nodes (9): get_countries(), get_port(), get_suggestions(), get, Get list of countries for autocomplete dropdown., Get specific port details by UN/LOCODE., Get port suggestions for autocomplete., search() (+1 more)

### Community 24 - "backend/main.py"
Cohesion: 0.19
Nodes (13): health(), lifespan(), get, Infreight Ocean Carrier Rate Automation — FastAPI Application. Main entry point…, Check if the VNC viewer is available (production only, where Xvfb runs)., Startup and shutdown events., vnc_status(), profile_base_dirs() (+5 more)

### Community 25 - "rate_search_routes.py"
Cohesion: 0.06
Nodes (54): approve_repair(), ApproveRepairRequest, carrier_switch_status(), chat_endpoint(), ChatRequest, create_batch_rate_search(), _contains(), _looks_like() (+46 more)

### Community 26 - "MSCConnector"
Cohesion: 0.18
Nodes (7): format_to_iso_date(), MSCConnector, Playwright-based automation for MSC (Mediterranean Shipping Company)., Handles the MSC login flow., Clicks Instant Quote, fills form, clicks Search., Detects and clicks the 'Ramp' delivery/haulage option if MSC displays Ramp /…, Parse '14 Jun 2026' to 'YYYY-MM-DD

### Community 27 - "parse_rfq"
Cohesion: 0.14
Nodes (24): _call_native_gemini_api(), _detect_booking_confirmation(), _detect_dual_mode_enquiry(), _detect_mode_by_hierarchy(), _detect_unsupported_cargo(), _extract_20gp_weight_priority(), generate_dual_air_drafts(), _load_airport_aliases_config() (+16 more)

### Community 28 - "types.ts"
Cohesion: 0.13
Nodes (27): 0. The one invariant, CarrierMultiSelect(), CarrierMultiSelectProps, isAllCarriers(), toggleAllCarriers(), toggleCarrierSelection(), PortAutocomplete(), RateSearchForm() (+19 more)

### Community 29 - "AIBrowserAgent"
Cohesion: 0.17
Nodes (10): AIBrowserAgent, Capture the current page as a PNG screenshot., Build the prompt with task description and action history., Parse Gemini's response into an action dict., Call Gemini API with exponential backoff retry., Execute a parsed action on the browser page., Detect if the agent is stuck repeating the same action., Find all visible interactive elements and format them as a prompt guide. (+2 more)

### Community 30 - "CarrierSearchResult"
Cohesion: 0.07
Nodes (51): get_recent_search_status_context(), Chat Service — manages conversational AI queries from the frontend user using…, Queries the database for the most recent rate search status to give the chatbot…, get_sync_url(), run_migrations_offline(), run_migrations_online(), fetch_port_fixes(), Saved port name fixes, marked built in or admin-added, and the ports each… (+43 more)

### Community 31 - "ONEConnector"
Cohesion: 0.09
Nodes (11): ONEConnector, _classify(), date, Parses ONE QUOTE Free Time popover text for DESTINATION ONLY. Ignores Origin…, Splits a single raw multi-container quote card into multiple QuoteSchema…, Tries to click a matching option from ONE's visible dropdown. Returns True only…, Extracts 5-letter UN/LOCODE from strings like 'Singapore [SGSIN]' or 'Singapore…, test_one_free_time_parser_origin_only_ignored() (+3 more)

### Community 32 - "_Page"
Cohesion: 0.15
Nodes (8): _connector(), _Locator, _Page, Maersk's login page redirects to the Hub a few seconds after loading when the…, Sits on /portaluser/login, then redirects after `redirect_after` URL reads., test_login_uses_saved_session_after_late_redirect(), test_wait_detects_late_redirect(), test_wait_detects_login_form()

### Community 33 - "Engineering Report: Sourcing Portal Enhancements & Scraping Pipeline Stability"
Cohesion: 0.08
Nodes (23): 1. Anti-Bot Mitigation & CAPTCHA Human-in-the-Loop Recovery, 2. Sourcing Parallelization & Surcharges Optimization, 3. Autocomplete Intelligence & Location Mapping, 4. Scraper Pipeline Maintenance, 5. Infrastructure & DevSecOps Enhancements, Business Value, Business Value, Business Value (+15 more)

### Community 34 - "Changelog"
Cohesion: 0.15
Nodes (12): [2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes, [2026-05-31] — Multi-Instance Support & Charge Classification, [2026-07-08] — OOCL E-Quote Calendar Navigation, cheapest E-Spot selection, and E-Quote/E-Spot isolation refinements, [2026-07-09] — Hapag-Lloyd Quick Quotes pairing and selection simplification, Changelog, Charge Classification Improvements, CMA CGM — Chrome Profile Bypass, Hapag-Lloyd — Quick Quotes Simplification & Clean Pairing (+4 more)

### Community 35 - "AdminOverview.tsx"
Cohesion: 0.10
Nodes (24): AdminAnalytics, AdminOverview(), AdminOverviewProps, AdminOverviewUser, AnalyticsRange, Attention, attentionItems(), CARRIER_LABELS (+16 more)

### Community 36 - "package.json"
Cohesion: 0.07
Nodes (27): eslintConfig, nextConfig, engines, node, name, packageManager, private, version (+19 more)

### Community 37 - "datetime"
Cohesion: 0.10
Nodes (13): Base Carrier Connector — abstract base class for all carrier connectors. Each…, Normalize CMA CGM data into QuoteSchema. Rule: include BASIC_OCEAN_FREIGHT and…, GreenX (Evergreen) Live Connector - Playwright automation., Hapag-Lloyd Prices API Connector (REST API v2.1.4). Provides real-time rate…, Mock Carrier Connector — returns realistic sample data for testing. Used when…, OOCL Live Connector â€” Playwright automation for Sailing Schedules., Carrier Registry — factory for getting the right connector per carrier. When…, ChargeSchema (+5 more)

### Community 38 - "RateResults.tsx"
Cohesion: 0.11
Nodes (32): LiveSearchProgressProps, QuoteBreakdownDrawer(), QuoteBreakdownDrawerProps, Breakdown(), ChargeList(), dateValue(), freeTimeText(), isSoldOut() (+24 more)

### Community 39 - "SearchQueueManager"
Cohesion: 0.12
Nodes (11): Lock, Marks a search as completed internally so we can track the auto-release timeout., Called periodically in a background task to check if the user has held the lock…, Forcefully clears all queued searches and the active lock. Useful for…, Returns or creates an asyncio.Lock for a specific carrier code to prevent…, Adds a search to the queue and waits until it becomes the active search. Event-…, Singleton manager to enforce a FIFO queue for rate searches. Since web scraping…, Returns the current position of the search in the queue. 0 means it is the… (+3 more)

### Community 40 - "ChargeCategory"
Cohesion: 0.18
Nodes (23): ChargeCategory, classify_charge(), Charge Classifier — rule-based classification of freight charge line items.…, Classify a charge line item based on its name, amount, section heading, and…, Tests for charge classifier., test_basic_ocean_freight(), test_cwx_heavy_weight_charge(), test_destination_charges() (+15 more)

### Community 41 - "Frontend Redesign — Componentry Design System, Workspace & Launch Intro (2026-09-07)"
Cohesion: 0.12
Nodes (15): 1. Design system foundation (`082b43a`), 2. Bugs found and fixed during the restyle, 3. Workspace + launch intro (`21ade75`), 4. Follow-up fixes (`2f9d92b`), 5. Verification, 6. Known limitations / candidate follow-ups, 7. Conventions to follow from here, Dependencies added (5, all small, no runtime lib dependency on Componentry) (+7 more)

### Community 42 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 43 - "resolve_port_for_carrier"
Cohesion: 0.21
Nodes (10): Resolves input text (e.g. 'Belfast (GBBEL)' or 'GBBEL') to a tuple of…, resolve_msc_port(), Resolves input text to (location_name, locode, country_code, country_name)., Fills the origin/destination 'Enter Port or Door Point' autocomplete. The…, resolve_oocl_port_info(), resolve_port_for_carrier(), Verify non-Maersk carriers get standard UN/LOCODE or default mappings., Verify that El Dekheila maps specifically to 'Alexandria Dekheila, Egypt' for… (+2 more)

### Community 44 - "test_carrier_timeout.py"
Cohesion: 0.19
Nodes (10): CrashingConnector, HangingConnector, asyncio, A carrier whose browser hangs must be stopped after CARRIER_SEARCH_TIMEOUT_SEC…, Hangs on the sizes in `hang_on`; answers NO_QUOTES_AVAILABLE for the rest., Like a real connector whose tab dies: reports a crash, then never returns., _run(), test_crashed_tab_stops_the_carrier_without_waiting_for_the_timeout() (+2 more)

### Community 45 - "app/page.tsx"
Cohesion: 0.08
Nodes (46): HomeContent(), BackendConfigModal(), BackendConfigModalProps, BatchProgressPanel(), BatchProgressPanelProps, cheapest(), Filter, lanePhase() (+38 more)

### Community 46 - "dithered-logo.tsx"
Cohesion: 0.19
Nodes (15): applyMaskInversion(), buildRoundedMask(), DEFAULTS, DitherConfig, DitheredLogo(), DitheredLogoProps, drawParticles(), errorDiffusionDither() (+7 more)

### Community 47 - "👥 The 5 Agent Roles"
Cohesion: 0.13
Nodes (14): 1. Intake Agent (Email Listener), 2. Sourcing Orchestrator (The Coordinator), 3. Sourcing & Scraping Agent (Rates Engine), 4. Finance & Costing Agent (Excel Compiler), 5. Email Draft Agent (Communicator), 📋 Executive Summary, 🛠️ Implementation Stages, Phase 1: Email Integration (Week 1-2) (+6 more)

### Community 48 - "HapagLloydConnector"
Cohesion: 0.06
Nodes (31): HapagLloydConnector, HapagServiceUnavailableException, Exception, Normalize various date formats (e.g. 2026-05-31, 31.05.2026, 31 May 2026, 31…, Robustly selects options from Hapag-Lloyd custom dropdown lists. Types the…, Detects the Microsoft B2C identity/OAuth login page. Hapag can silently bounce…, Guards against the session-expiry-mid-crawl failure mode: the existing redirect…, Crawls Hapag-Lloyd sailing schedules from the Schedule tab. (+23 more)

### Community 49 - "MockCarrierConnector"
Cohesion: 0.12
Nodes (10): _generate_maersk_mock_quotes(), _generate_msc_mock_quotes(), _generate_one_mock_quotes(), MockCarrierConnector, any, Generate realistic ONE sample quotes with charge breakdowns., Generate realistic MSC sample quotes with validity_till., Generate realistic Maersk sample quotes with charge breakdowns. (+2 more)

### Community 50 - "selector_memory.py"
Cohesion: 0.24
Nodes (12): get_approved_selector(), _load_memory(), Selector Memory — stores and retrieves human-approved selector patches., Loads memory JSON file. Returns empty dict if file is missing or invalid., Saves memory dict back to JSON file., Looks up if there is an approved replacement selector for the given carrier and…, Stores an approved replacement selector., Marks any proposed selector for this step as REJECTED. (+4 more)

### Community 51 - "CurrencyManager"
Cohesion: 0.23
Nodes (7): convert_currency_to_usd(), CurrencyManager, get_all_exchange_rates(), Any, Currency Exchange Rate Service — manages currency conversions and custom…, update_exchange_rate(), threading

### Community 52 - "get_port_by_code"
Cohesion: 0.32
Nodes (5): get_carrier_search_query(), get_port_by_code(), Resolves a port search text (e.g. 'Haiphong (VN HPH)', 'VN HPH', 'Hai Phong')…, Constructs the specific search query to type into carrier search boxes. If the…, test()

### Community 53 - "test_hapag_freetime.py"
Cohesion: 0.15
Nodes (16): Looks up standard destination demurrage/detention free time days., (days, estimated): estimated when the destination has no entry in the free time…, _apply_freetime_to_quote(), freetime_days(), match_freetime_entry(), Any, Days for this container from a table entry ({"20GP": n, "40GP": n} or a bare…, The table entry whose country name appears in `text` as whole words. Whole… (+8 more)

### Community 54 - "🚢 Infreight Sourcing & Ocean Rate Automation System"
Cohesion: 0.14
Nodes (13): 1. Multi-Carrier Automation Engine, 2. Intelligent Surcharge & Charge Classifier Engine (`charge_classifier.py`), 3. Container Comparison Matrix & Excel Export Engine, 🚢 Infreight Sourcing & Ocean Rate Automation System, 🌟 Key Capabilities, 📄 License & Confidentiality, Prerequisites, 🛠️ Project Structure (+5 more)

### Community 55 - "os"
Cohesion: 0.12
Nodes (14): # NOTE: No start date fill needed — schedule page defaults to today,, Hapag-Lloyd Live Connector -- Playwright automation. Credentials read from env:…, Interactive Headed Login Helper for Maersk. Opens real Chrome using the…, Interactive Headed Login Helper for ONE (Ocean Network Express). Opens Chrome…, Storage Cleanup Utility — automatically removes stale debug screenshots, HTML…, Hapag-Lloyd end-to-end test using run_full_search., test_hapag(), Debug script: Reuse HapagLloydConnector login, then step through the Schedule… (+6 more)

### Community 56 - "[2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split"
Cohesion: 0.15
Nodes (13): G2 Stress Test: "Hi, Please book the below as per your quote ref INF-2026-0842:…, H1 Stress Test: Table with 2 distinct rows: Row 1: POL Singapore, POD Jakarta,…, test_g2_booking_confirmation_guardrail(), test_h1_table_deduplication_two_pairs(), [2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split, Booking Confirmation / Instructions Intercept Guardrail G2 (`rfq_agent.py` & `RfqInputSection.tsx`), Commercial Sales Desk Intelligence (`sales_notes`), Deterministic Port Alias Resolver (`ports_aliases.json`) (+5 more)

### Community 57 - "ai_agent.py"
Cohesion: 0.15
Nodes (12): AI Browser Agent — Vision-based browser automation using Gemini Flash. This…, _cleanup_profile(), main(), Experimental AI Agent Test -- Maersk Quote Search This script tests the AI…, Remove temporary chrome profile directory., Print with ASCII-safe encoding for Windows console., safe_print(), base64 (+4 more)

### Community 58 - "🛠 Detailed Carrier Log"
Cohesion: 0.15
Nodes (12): 🛠 Detailed Carrier Log, 🟢 GreenX, 🟠 Hapag-Lloyd, Infreight Ocean Carrier Rate Automation — Development Log, 🚀 Key Highlights & Architectural Changes, 🔌 Local Laptop Deployment (Self-Hosted Worker), 🔵 Maersk, 💗 ONE (Ocean Network Express) (+4 more)

### Community 59 - "one_connector.py"
Cohesion: 0.15
Nodes (8): ONE (Ocean Network Express) Live Connector — Playwright automation. Credentials…, # TODO: Verify selectors against ONE ecommerce portal, MockCard, Unit test for ONE connector charge classification override., test_emergency_surcharge_override(), MockCard, Unit test for ONE connector and charge classifier Premium Cargo Service…, test_premium_cargo_service_override()

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
Cohesion: 0.12
Nodes (10): MockCard, MockLocator, [2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup, Chromium Cache Auto-Cleanup (Railway Storage Bloat Prevention), CMA CGM — 30-Second Timeout on Sold Out Cards, CMA CGM — Free Time Regex Too Strict, CMA CGM — Routing Regex Not Matching "via LEKKI, LA, NG", Excel Export — Routing & Free Time Columns Always Empty (+2 more)

### Community 64 - "ai_repair_agent.py"
Cohesion: 0.29
Nodes (7): _local_fuzzy_repair(), AI Repair Agent — diagnoses Playwright step failures and suggests selector…, A local rule-based heuristic to locate reasonable buttons or inputs when Gemini…, Analyzes the failure context and DOM content to suggest a selector repair. Uses…, suggest_fix(), test_ai_repair_agent_offline_fallback(), bs4

### Community 65 - "RFQParseResult"
Cohesion: 0.17
Nodes (12): parse_rfq_endpoint(), post, API routes for RFQ parsing agent., Parse a free-text RFQ email or message into a structured RateSearchRequest…, RFQParseRequest, RFQParseResult, Test Image 2: Air rate request generates 3 drafts to Glenn (AWOT), Jing Hui…, Test Guardrail: Detects Reefer container request and returns unsupported_cargo… (+4 more)

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
Cohesion: 0.17
Nodes (15): handle_chat_query(), _local_chatbot_fallback(), Intelligent responder for search status, carrier guidance, air/sea info, and…, Sends the chat message and history to native Gemini 2.5 Flash API. If Gemini…, detect_manual_action_required(), Scans the current Playwright page to see if a CAPTCHA, Cloudflare challenge,…, clean_selector_memory(), asyncio (+7 more)

### Community 70 - "dependencies"
Cohesion: 0.15
Nodes (13): dependencies, class-variance-authority, clsx, exceljs, lucide-react, next, next-themes, @radix-ui/react-slot (+5 more)

### Community 71 - "AdminUsers.tsx"
Cohesion: 0.20
Nodes (14): AdminUserRecord, AdminUsers(), AdminUsersProps, ago(), AuditEntry, Avatar(), Filter, initials() (+6 more)

### Community 72 - "deploy"
Cohesion: 0.25
Nodes (7): build, builder, deploy, restartPolicyMaxRetries, restartPolicyType, startCommand, $schema

### Community 73 - ".search_quotes"
Cohesion: 0.17
Nodes (8): extract_locode_and_country(), prepare_maersk_query(), Fills an autocomplete field using the proven original element-level…, Extracts LOCODE and country name from text like 'CASABLANCA, MOROCCO (MACAS)'…, Maps standard container search codes (e.g. 'DRY 20', '20GP') to Maersk Spot…, Scores a Maersk autocomplete dropdown suggestion. NOTE: The nested/indented…, get_cached_carrier_port(), set_cached_carrier_port()

### Community 74 - "test_panama_canal_surcharge.py"
Cohesion: 0.12
Nodes (17): parse_msc_modal_charges(), Parses charges from MSC BreakdownModal text. Correctly includes charges whose…, Sort container types in standard order: DRY 20 (20GP) -> DRY 40 (40GP) -> DRY…, sort_container_types(), Test MSC charges parsing for Singapore to Conakry, Guinea (40GP). Charges with…, Test when only some surcharges have the payment condition., test_msc_charges_mixed_conditions(), test_msc_charges_singapore_to_conakry_guinea() (+9 more)

### Community 75 - "Summary of Changes — July 20, 2026"
Cohesion: 0.29
Nodes (6): 1. AI RFQ Front Door & Air Freight Support (Phase A), 2. Multi-Origin & Gappy List Parsing for Sea RFQs (Phase B), 3. Search Form Streamlining (Form Input Restrictions), 4. Native Gemini 2.5 Flash API & Chatbot Resiliency, 5. Verification & Test Suite, Summary of Changes — July 20, 2026

### Community 76 - "safe_step"
Cohesion: 0.17
Nodes (11): generate_report(), Assembles a comprehensive repair report and writes it as JSON and Markdown…, Updates the status of a carrier search in the database., Executes a Playwright action. If it fails: 1. Detects CAPTCHA/bot challenges…, safe_step(), update_carrier_status(), 1. What was measured, 3. Multi-port quick search — defects found and fixed (+3 more)

### Community 77 - "[2026-05-29 – 2026-05-30] — Hapag-Lloyd Full Integration"
Cohesion: 0.40
Nodes (5): [2026-05-29 – 2026-05-30] — Hapag-Lloyd Full Integration, Hapag-Lloyd — Dropdown Autocomplete Issues, Hapag-Lloyd — Live Connector Implementation, Hapag-Lloyd — Onboarding Modal Blocking Form Interaction, Hapag-Lloyd — Search Button Selector Failures

### Community 78 - "resolve_port_alias"
Cohesion: 0.33
Nodes (6): _load_port_aliases_config(), Deterministically resolves a port string against ports_aliases.json and the…, resolve_port_alias(), Test that resolve_port_alias cleans 'City, Country' and parenthetical notes to…, test_resolve_city_country_format_to_clean_database_port_name(), Clean Search Dropdown Port Name Resolution (`rfq_agent.py` & `port_manager.py`)

### Community 79 - "json"
Cohesion: 0.12
Nodes (15): argparse, Repair Report — generates and saves diagnosis reports on Playwright selector…, check_and_wait_for_captcha(), login(), main(), get_title(), Script to test fetching CMA CGM pricing page using Bright Data Web Access HTTP…, test_brightdata_api() (+7 more)

### Community 80 - "._fs_dismiss_modals"
Cohesion: 0.23
Nodes (7): _dismiss_once(), _click_date_strip_item(), _open_calendar(), Iterates through the FreightSmart results date calendar to collect E-Quote and…, Position-based fallback for the onboarding tour popup: instead of guessing its…, Closes FreightSmart popups. Order matters: 1. Cookie Notice consent ("Accept…, setter

### Community 81 - "Design system — read before touching any UI"
Cohesion: 0.33
Nodes (5): Animation rules, Client-only preferences, Design system — read before touching any UI, This is NOT the Next.js you know, Use tokens, not raw colours

### Community 82 - "tunnel_relay/main.py"
Cohesion: 0.25
Nodes (8): api_route, fastapi_middleware_cors, health(), get, Request, websocket, relay_request(), websocket_endpoint()

### Community 83 - "[2026-06-03] — CMA CGM Routing & Free Time Extraction"
Cohesion: 0.50
Nodes (4): [2026-06-03] — CMA CGM Routing & Free Time Extraction, CMA CGM — Import Free Time from D&D Tab, CMA CGM — Routing Detection (Direct vs Transit), Maersk — Free Time Extraction from Card Text

### Community 84 - "[2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning"
Cohesion: 0.17
Nodes (10): get_booking_start_date(), date, Applies the business rules and pairs FreightSmart prices with crawled…, [2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning, GreenX — "No Quotes" Reported While Quotes Visibly Loaded in VNC, Hapag-Lloyd — Configurable Pacing & Redundant-Wait Removal, Job Scheduler — Concurrency Default, Maersk — Regression: Other-Container-Type Sizes Went "Sold Out" in Multi-Container Searches (+2 more)

### Community 85 - "._fs_extract_rows"
Cohesion: 0.18
Nodes (7): clean_vessel_name(), _parse_date(), parse_oocl_date(), Parses one FreightSmart result card's inner text into a raw row dict. Text-…, Opens the Details dialog for a card, clicks the Charge Breakdown tab, extracts…, Collects result cards from the FreightSmart quote results page., OOCL Nearby Route Recommendations Suppression (`oocl_connector.py`)

### Community 86 - "test_auth_routes.py"
Cohesion: 0.29
Nodes (6): ambiguous_python_import_b35980c0aa01, asyncio, Integration tests for authentication, legacy user password setup, pending…, test_full_auth_lifecycle(), httpx, pytest_asyncio

### Community 88 - "RateSearchRequest"
Cohesion: 0.07
Nodes (34): asyncio, CMA CGM Live Connector — Playwright automation. Credentials read from env:…, RateSearchRequest, Pydantic schemas for API request/response validation., CMA CGM end-to-end test — login + search + extract quotes., # IMPORTANT: Clear ALL proxy env vars BEFORE any import triggers load_dotenv()…, test_cma(), run_test() (+26 more)

### Community 89 - "[2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History"
Cohesion: 0.40
Nodes (5): [2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History, Admin User Search History & SGT GMT+8 Conversion (`AdminDashboard.tsx`), GreenX (Evergreen) Card Isolation & Surcharge Parsing (`greenx_connector.py`), Multi-Route Batch Execution Engine (`batch_engine.py`), OOCL FreightSmart 28-Day Calendar Expansion (`oocl_connector.py`)

### Community 90 - "websockify_carrier_proxy"
Cohesion: 0.22
Nodes (5): websocket, Proxy WebSocket connections to legacy local x11vnc at localhost:5900., Proxy WebSocket connections to specific carrier x11vnc servers., websockify_carrier_proxy(), websockify_proxy()

### Community 92 - "devDependencies"
Cohesion: 0.22
Nodes (9): devDependencies, eslint, eslint-config-next, tailwindcss, @tailwindcss/postcss, @types/node, @types/react, @types/react-dom (+1 more)

### Community 95 - "diagnose_greenx_dropdown.py"
Cohesion: 0.67
Nodes (3): dump_options(), main(), Diagnostic: dump ALL dropdown options (text + innerHTML) when typing 'DEHAM'…

### Community 96 - "frontend/README.md"
Cohesion: 0.50
Nodes (3): Deploy on Vercel, Getting Started, Learn More

### Community 97 - "pytest"
Cohesion: 0.18
Nodes (7): parse_hapag_card_text_mock(), Verify that multi-leg/feeder routes take the final arrival ETA and 28 days TT., Mock implementation of the JS evaluate logic inside hapag_lloyd_connector.py., test_hapag_multi_leg_schedule_extraction(), asyncio, test_one_breakdown_currency_and_arbitrary_destination_classification(), pytest

### Community 98 - "[2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control"
Cohesion: 0.40
Nodes (5): [2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control, Concurrency Limit Queue & Admin Control Panel, MSC — Mediterranean Shipping Company Connector Implementation, ONE — Inbound Free Time Swap & Scraper Upgrade, OOCL — Orient Overseas Container Line Connector Implementation

### Community 99 - "._save_carrier_overrides"
Cohesion: 0.18
Nodes (8): Where admin-saved port name fixes are kept. Railway rebuilds /app on every…, _user_overrides_path(), test_saved_fixes_live_on_the_persistent_volume(), [2026-08-04 - 2026-08-06] — CMA CGM Dynamic RAMP/POD Rerouting, Brand Excel Styling, Port Synonym Matching & Tunnel Relays, Brand-Aligned Excel Export Styling (`excel_export.py`), CMA CGM Dynamic RAMP / POD Advisory Banner Detection (`cma_connector.py`), Dynamic Carrier Port Overrides & Admin Registry (`PortManager`, `AdminDashboard.tsx`), Railway WebSocket Tunnel Relay & Failover (`tunnel_client.py`, `run_tunnel_client.bat`, `FailoverFetch`)

### Community 100 - "test_belawan_aden.py"
Cohesion: 0.60
Nodes (4): main(), Test script to run Belawan (IDBLW) -> Aden (YEADE) route on Maersk and MSC., test_maersk(), test_msc()

### Community 101 - "[2026-05-20 – 2026-05-22] — Port Resolution & Frontend Improvements"
Cohesion: 0.50
Nodes (4): [2026-05-20 – 2026-05-22] — Port Resolution & Frontend Improvements, Excel Export — ETA Column & Container Type Header, Frontend Light Mode & CORS Fix, Port Resolution System

### Community 102 - "[2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash"
Cohesion: 0.40
Nodes (5): [2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash, AI RFQ Front Door & Air Freight Support, Multi-Origin & Gappy List Parsing (Sea RFQs), Native Gemini 2.5 Flash Direct API Integration, Search Form Streamlining

### Community 103 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, dev, lint, start

### Community 106 - "[2026-05-18 – 2026-05-19] — Railway Deployment & Docker"
Cohesion: 0.67
Nodes (3): [2026-05-18 – 2026-05-19] — Railway Deployment & Docker, Persistent Chrome Profiles on Railway Volume, Railway Deployment Setup

### Community 116 - "QuoteSchema"
Cohesion: 0.08
Nodes (16): Normalize extracted data into a QuoteSchema using the normalizer. Args:…, Splits a single raw multi-container quote card into multiple QuoteSchema…, Required abstract method implementation; delegates to run_full_search., Batch (RFQ) mode: the base implementation drives a browser page, so answer from…, Called by job_service once per container type (request.container_type). All…, Executes full rate search against Hapag-Lloyd Prices API. Queries each…, Serves one container-type cycle from the cached merged quote set: -…, One crawl serves all container-type cycles (cached), combining: 1. Sailing… (+8 more)

### Community 117 - "[2026-05-23 – 2026-05-24] — Maersk Shadow DOM & Stealth Upgrades"
Cohesion: 0.50
Nodes (4): [2026-05-23 – 2026-05-24] — Maersk Shadow DOM & Stealth Upgrades, Maersk — 2FA/CAPTCHA Human-in-the-Loop via noVNC, Maersk — Login Credential Autofill Corruption, Maersk — Shadow DOM Piercing for MDS Web Components

### Community 119 - "SearchStatus"
Cohesion: 0.67
Nodes (4): CarrierCode, SearchStatus, Enum, str

### Community 120 - "Architecture Overview"
Cohesion: 0.50
Nodes (4): Architecture Overview, Carrier Connector Lifecycle, Charge Classification Rules, Search Flow

### Community 121 - "[2026-05-25 – 2026-05-26] — VNC Display Isolation & Proxy Integration"
Cohesion: 0.67
Nodes (3): [2026-05-25 – 2026-05-26] — VNC Display Isolation & Proxy Integration, Bright Data ISP Proxy Integration, VNC Display Isolation for Concurrent Carriers

### Community 122 - "[2026-06-01] — Hapag-Lloyd Sold Out Detection & Date Parsing"
Cohesion: 0.67
Nodes (3): [2026-06-01] — Hapag-Lloyd Sold Out Detection & Date Parsing, Hapag-Lloyd — Date String Standardization, Hapag-Lloyd — Sold Out Schedule Detection

### Community 126 - "maersk_connector.py"
Cohesion: 0.11
Nodes (16): Maersk Browser Connector — Playwright automation using your real Google Chrome…, # NOTE: Bright Data Web Unlocker proxies break Playwright browser sessions…, Hapag-Lloyd form inspector., main(), Inspection script to dump the Maersk autocomplete dropdown structure., main(), Verification script for Maersk multi-container implementation., main() (+8 more)

### Community 129 - "[2026-06-02] — Hapag-Lloyd Transshipment & Duplicate Fix"
Cohesion: 0.67
Nodes (3): [2026-06-02] — Hapag-Lloyd Transshipment & Duplicate Fix, Hapag-Lloyd — Duplicate Sailings from Transshipment Vessels, Hapag-Lloyd — Routing Not Marked as Transit

## Knowledge Gaps
- **312 isolated node(s):** `Config`, `install_pi.sh script`, `eslintConfig`, `nextConfig`, `name` (+307 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 937 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **19 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Changelog` connect `Changelog` to `[2026-06-02] — Hapag-Lloyd Transshipment & Duplicate Fix`, `HapagLloydAPIConnector`, `[2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split`, `[2026-08-07] — Carrier Specific Free Time, Demurrage/Detention Splitting, MSC CDD Surcharges, OOCL Nearby Route Filtering & Favicon Cache Busting`, `[2026-06-30] — ONE Multi-Container & Sold-Out, GreenX Surcharge Intake, Free-Time Fixes, Maersk Diagnosis`, `[2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup`, `._verify_price_owner_selected`, `[2026-05-29 – 2026-05-30] — Hapag-Lloyd Full Integration`, `[2026-06-03] — CMA CGM Routing & Free Time Extraction`, `[2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning`, `[2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History`, `[2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control`, `._save_carrier_overrides`, `[2026-05-20 – 2026-05-22] — Port Resolution & Frontend Improvements`, `[2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash`, `[2026-05-18 – 2026-05-19] — Railway Deployment & Docker`, `[2026-05-23 – 2026-05-24] — Maersk Shadow DOM & Stealth Upgrades`, `Architecture Overview`, `[2026-05-25 – 2026-05-26] — VNC Display Isolation & Proxy Integration`, `[2026-06-01] — Hapag-Lloyd Sold Out Detection & Date Parsing`?**
  _High betweenness centrality (0.327) - this node is a cross-community bridge._
- **Why does `[2026-06-03] — CMA CGM Routing & Free Time Extraction` connect `[2026-06-03] — CMA CGM Routing & Free Time Extraction` to `Changelog`?**
  _High betweenness centrality (0.301) - this node is a cross-community bridge._
- **Why does `Maersk — Free Time Extraction from Card Text` connect `[2026-06-03] — CMA CGM Routing & Free Time Extraction` to `app/page.tsx`?**
  _High betweenness centrality (0.300) - this node is a cross-community bridge._
- **Are the 32 inferred relationships involving `RateSearchRequest` (e.g. with `create_batch_rate_search()` and `create_rate_search()`) actually correct?**
  _`RateSearchRequest` has 32 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `cn()` (e.g. with `Reuse the primitives` and `7. Conventions to follow from here`) actually correct?**
  _`cn()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 21 inferred relationships involving `CarrierResultStatus` (e.g. with `safe_step()` and `update_carrier_status()`) actually correct?**
  _`CarrierResultStatus` has 21 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Config`, `install_pi.sh script`, `eslintConfig` to the rest of the system?**
  _312 weakly-connected nodes found - possible documentation gaps or missing edges._