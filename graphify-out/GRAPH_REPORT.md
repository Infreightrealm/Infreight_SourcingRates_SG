# Graph Report - Infreight_SourcingRates_SG  (2026-10-09)

## Corpus Check
- 246 files · ~1,163,260 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 23 file(s) not represented in the graph (top: (none) 10, .bat 6, .conf 2)

## Summary
- 2370 nodes · 5854 edges · 127 communities (105 shown, 22 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 334 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `746d6c91`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- port_manager.py
- BaseCarrierConnector
- cn
- user_routes.py
- auth_service.py
- browser_cleanup.py
- auth_routes.py
- api.ts
- PortManager
- AdminUsers.tsx
- CMAConnector
- test_normalizer.py
- get_async_session_maker
- react
- OOCLConnector
- HapagLloydAPIConnector
- preferences.ts
- test_rfq_agent.py
- RateSearchRequest
- SocialWidget.tsx
- LiveSearchProgress.tsx
- GreenXConnector
- social_routes.py
- port_routes.py
- backend/main.py
- create_batch_rate_search
- registry.py
- parse_rfq
- types.ts
- AIBrowserAgent
- rate_search_routes.py
- ONEConnector
- _Page
- Engineering Report: Sourcing Portal Enhancements & Scraping Pipeline Stability
- Changelog
- admin/page.tsx
- package.json
- dependencies
- RateResults.tsx
- SearchQueueManager
- ChargeCategory
- Frontend Redesign — Componentry Design System, Workspace & Launch Intro (2026-09-07)
- compilerOptions
- resolve_port_for_carrier
- test_carrier_timeout.py
- devDependencies
- dithered-logo.tsx
- 👥 The 5 Agent Roles
- HapagLloydConnector
- CarrierResultStatus
- tunnel_relay/main.py
- CurrencyManager
- test_one_charge_override.py
- test_hapag_freetime.py
- 🚢 Infreight Sourcing & Ocean Rate Automation System
- MaerskConnector
- [2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split
- ._parse_offer_response_to_quotes
- 🛠 Detailed Carrier Log
- orbit-card-stack.tsx
- test_one_premium_override.py
- .extract_charge_breakdown
- [2026-06-30] — ONE Multi-Container & Sold-Out, GreenX Surcharge Intake, Free-Time Fixes, Maersk Diagnosis
- [2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup
- compute_admin_analytics
- RFQParseResult
- GreenX — Surcharge Intake Fix (2026-06-30)
- Admin Page & Port Prioritization Guide
- [2026-07-03] — OOCL FreightSmart Autoclear, Hapag Price Leak & Redirect fixes, Maersk Cache Scoping, Dallas Overrides
- test_self_healing.py
- test_panama_canal_surcharge.py
- carrier_switches.py
- deploy
- .search_quotes
- parse_msc_modal_charges
- Summary of Changes — July 20, 2026
- _detect_port_mismatch
- [2026-05-29 – 2026-05-30] — Hapag-Lloyd Full Integration
- resolve_port_alias
- test_brightdata.py
- MockCard
- Design system — read before touching any UI
- .extract_quote_list
- layout.tsx
- [2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning
- [2026-06-03] — CMA CGM Routing & Free Time Extraction
- .search_quotes
- hapag_lloyd_connector.py
- os
- test_hapag_api_connector.py
- one_connector.py
- ref_fs
- AppHeader.tsx
- [2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History
- [2026-06-01] — Hapag-Lloyd Sold Out Detection & Date Parsing
- scripts
- frontend/README.md
- pytest
- [2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control
- .validate_currency
- ._lookup_freetime
- [2026-05-20 – 2026-05-22] — Port Resolution & Frontend Improvements
- [2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash
- test_one_breakdown_parsing
- Working in this repository
- [2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes
- install_pi.sh
- models/__init__.py
- postcss.config.mjs
- eslint.config.mjs
- [2026-05-23 – 2026-05-24] — Maersk Shadow DOM & Stealth Upgrades
- ._execute_single_price_request
- get_me
- Architecture Overview
- verify_admin_access
- [2026-05-31] — Multi-Instance Support & Charge Classification
- .get_carrier_lock
- [2026-06-02] — Hapag-Lloyd Transshipment & Duplicate Fix
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
9. `MaerskConnector` - 51 edges
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
- `4. Follow-up fixes (`2f9d92b`)` --references--> `PortAutocomplete()`  [INFERRED]
  FRONTEND_REDESIGN_2026-09-07.md → frontend/src/components/PortAutocomplete.tsx

## Import Cycles
- None detected.

## Communities (127 total, 22 thin omitted)

### Community 0 - "port_manager.py"
Cohesion: 0.15
Nodes (14): add_carrier_override(), add_custom_port(), delete_carrier_override(), delete_custom_port(), get_custom_ports(), get_popular_ports_config(), normalize_port_input(), Suggest top N ports for a partial query. (+6 more)

### Community 1 - "BaseCarrierConnector"
Cohesion: 0.05
Nodes (34): ABC, BaseCarrierConnector, NotAvailableConnector, Any, Open the price breakdown / detail view for a specific quote. Args: quote_ref:…, Extract individual charge line items from the price breakdown. Returns: List of…, Normalize extracted data into a QuoteSchema using the normalizer. Args:…, Abstract base class for carrier portal connectors. (+26 more)

### Community 2 - "cn"
Cohesion: 0.10
Nodes (38): Reuse the primitives, New primitives — `frontend/src/components/ui/`, PortAutocomplete(), PortAutocompleteProps, Badge(), badgeVariants, Dot(), Card() (+30 more)

### Community 3 - "user_routes.py"
Cohesion: 0.07
Nodes (73): get_current_user(), Dependency that strictly requires an authenticated active member., admin_delete_user(), AdminLoginRequest, approve_user(), CarrierOverrideRequest, CarrierSwitchRequest, Config (+65 more)

### Community 4 - "auth_service.py"
Cohesion: 0.07
Nodes (41): AuditLog, AuthSession, Stores hashed active session tokens., Stores security and operational audit trail entries., check_rate_limit(), clear_login_failures(), get_user_for_token(), hash_token() (+33 more)

### Community 5 - "browser_cleanup.py"
Cohesion: 0.09
Nodes (38): _is_chrome(), _is_playwright_driver(), _kill(), kill_profile_browsers(), _proc_supported(), Cleanup for Chrome browsers and temporary profiles that a failed close leaves…, Kill every automated Chrome and Playwright driver. Only call this when no…, Delete per-search profile copies ("chrome_profile_<carrier>_tmp_<id>") and… (+30 more)

### Community 6 - "auth_routes.py"
Cohesion: 0.11
Nodes (34): clear_session_cookie(), get_current_user_optional(), login(), LoginRequest, logout(), AsyncSession, BaseModel, post (+26 more)

### Community 7 - "api.ts"
Cohesion: 0.08
Nodes (58): AdminDashboard(), HomeContent(), BackendConfigModal(), BackendConfigModalProps, LoadingState(), SearchCompletionModal(), SearchCompletionModalProps, addCarrierOverride() (+50 more)

### Community 8 - "PortManager"
Cohesion: 0.09
Nodes (13): PortManager, Where admin-saved port name fixes are kept. Railway rebuilds /app on every…, Retrieve verified carrier port name from persistent cache by UN/LOCODE,…, Cache verified carrier port name and save persistently to…, Clean and normalize user input for port searching., Retrieve port data by full UN/LOCODE (e.g., 'SGSIN')., _user_overrides_path(), test_saved_fixes_live_on_the_persistent_volume() (+5 more)

### Community 9 - "AdminUsers.tsx"
Cohesion: 0.20
Nodes (14): AdminUserRecord, AdminUsers(), AdminUsersProps, ago(), AuditEntry, Avatar(), Filter, initials() (+6 more)

### Community 10 - "CMAConnector"
Cohesion: 0.08
Nodes (18): CMAConnector, Ensures 'Ramp' is explicitly selected under 'Type of location' toggle buttons…, Scans for Route, POL (Port of Loading), or POD (Port of Discharge) dropdown…, Clears the currently selected Destination port tag/card, re-types the locode,…, Dynamically extracts any recommended 5-letter POD LOCODE mentioned in the…, Detects if CMA CGM displayed an advisory banner message: "Looking for AEJEA or…, Handles the 'Customer account' -> 'Role (you are acting as)' dropdown on CMA…, Repeatedly clicks 'More results' if visible to load ALL quotes on the page. (+10 more)

### Community 11 - "test_normalizer.py"
Cohesion: 0.18
Nodes (16): is_weight_surcharge_applicable(), Evaluates whether a weight-tier or overweight surcharge is applicable for the…, calculate_final_freight_value(), classify_and_organize_charges(), Takes raw charge line items and classifies them. Args: raw_charges: list of…, Calculate the final freight value from a list of classified charges. Args:…, Tests for normalizer / final freight value calculator., test_basic_calculation() (+8 more)

### Community 12 - "get_async_session_maker"
Cohesion: 0.11
Nodes (29): get_connector(), Get the appropriate connector for a carrier. If USE_MOCK_CARRIERS=true: returns…, get_async_session_maker(), Get the session maker for use outside of FastAPI dependency injection., UUID, Run one container-size search, stopping it early if the browser tab crashes or…, Run a single carrier search job. Updates the CarrierSearchResult record…, Check all carrier results and update the overall search status. (+21 more)

### Community 13 - "react"
Cohesion: 0.09
Nodes (24): nextConfig, 0. The one invariant, 6. Known limitations / candidate follow-ups, LoginContent(), LoginModal(), LoginModalProps, RepairReport, SelfHealingAlerts() (+16 more)

### Community 14 - "OOCLConnector"
Cohesion: 0.04
Nodes (40): clean_vessel_name(), OOCLConnector, _dismiss_once(), _click_date_strip_item(), _open_calendar(), _parse_date(), parse_oocl_date(), Lock (+32 more)

### Community 15 - "HapagLloydAPIConnector"
Cohesion: 0.13
Nodes (6): HapagLloydAPIConnector, Direct REST API connector for Hapag-Lloyd Prices API v2.1.4., API connectors do not require browser login sessions., No browser session to reset between batch routes., Resolves a free-text port name or string (e.g. 'Singapore', 'Hamburg, Germany…, Hapag-Lloyd Prices API requires earliestDepartureDate to be at least 4 calendar…

### Community 16 - "preferences.ts"
Cohesion: 0.09
Nodes (34): LaunchIntro(), RfqInputSection(), SearchHistoryItem, derive(), Derived, startOfDay(), UsageStats(), ChoiceCard() (+26 more)

### Community 17 - "test_rfq_agent.py"
Cohesion: 0.10
Nodes (28): asyncio, Unit tests for the Gemini AI RFQ Agent service (parse_rfq). Includes…, Test Image 4: Steel Plate ex Pasir Gudang / Tanjung Pelepas for 20' & 40'., Test Guardrail: Detects LCL request., Test OpenFlights 6,072 IATA airport dataset and shorthand alias resolution., Test Pak Shaun email: "Hi team, need rate for 10x20GP from PK to JKT. Urgent…, Test Multimodal Image Input validation and parsing., Test Stress Test Scenario: "Dear Sir, Pls quote 3 x 20'FCL Singapore to… (+20 more)

### Community 18 - "RateSearchRequest"
Cohesion: 0.06
Nodes (42): CMA CGM Live Connector — Playwright automation. Credentials read from env:…, BatchRateSearchRequest, BatchRateSearchResponse, BatchRoutePair, BatchSearchStatusItem, CarrierResultSchema, BaseModel, RateSearchCreateResponse (+34 more)

### Community 19 - "SocialWidget.tsx"
Cohesion: 0.16
Nodes (21): ACCENT_COLORS, errorMessage(), relativeTime(), resizeImageToDataUrl(), SocialWidget(), SocialWidgetProps, EMOJI_GROUPS, EmojiPicker() (+13 more)

### Community 20 - "LiveSearchProgress.tsx"
Cohesion: 0.08
Nodes (31): ChatWidget(), ChatWidgetProps, Message, ACTION_STATUSES, ChipModel, describe(), EMPTY_STATUSES, formatElapsed() (+23 more)

### Community 21 - "GreenXConnector"
Cohesion: 0.14
Nodes (9): GreenXConnector, Overrides base search runner to query all 3 sizes at once and cache the…, inspect(), main(), main(), main(), test_greenx(), main() (+1 more)

### Community 22 - "social_routes.py"
Cohesion: 0.12
Nodes (29): get_conversation(), list_colleagues(), poke_colleague(), PokeRequest, AsyncSession, BaseModel, delete, get (+21 more)

### Community 23 - "port_routes.py"
Cohesion: 0.29
Nodes (9): get_countries(), get_port(), get_suggestions(), get, Get list of countries for autocomplete dropdown., Get specific port details by UN/LOCODE., Get port suggestions for autocomplete., search() (+1 more)

### Community 24 - "backend/main.py"
Cohesion: 0.08
Nodes (26): health(), lifespan(), get, websocket, Infreight Ocean Carrier Rate Automation — FastAPI Application. Main entry point…, Check if the VNC viewer is available (production only, where Xvfb runs)., Proxy WebSocket connections to legacy local x11vnc at localhost:5900., Proxy WebSocket connections to specific carrier x11vnc servers. (+18 more)

### Community 25 - "create_batch_rate_search"
Cohesion: 0.11
Nodes (24): approve_repair(), ApproveRepairRequest, chat_endpoint(), ChatRequest, create_batch_rate_search(), _contains(), _looks_like(), _norm() (+16 more)

### Community 26 - "registry.py"
Cohesion: 0.09
Nodes (16): Base Carrier Connector — abstract base class for all carrier connectors. Each…, Mock Carrier Connector — returns realistic sample data for testing. Used when…, format_to_iso_date(), MSCConnector, Playwright-based automation for MSC (Mediterranean Shipping Company)., Handles the MSC login flow., Clicks Instant Quote, fills form, clicks Search., Detects and clicks the 'Ramp' delivery/haulage option if MSC displays Ramp /… (+8 more)

### Community 27 - "parse_rfq"
Cohesion: 0.14
Nodes (24): _call_native_gemini_api(), _detect_booking_confirmation(), _detect_dual_mode_enquiry(), _detect_mode_by_hierarchy(), _detect_unsupported_cargo(), _extract_20gp_weight_priority(), generate_dual_air_drafts(), _load_airport_aliases_config() (+16 more)

### Community 28 - "types.ts"
Cohesion: 0.10
Nodes (38): CarrierMultiSelect(), CarrierMultiSelectProps, isAllCarriers(), toggleAllCarriers(), toggleCarrierSelection(), RateSearchForm(), RateSearchFormProps, DEMO_EXAMPLES (+30 more)

### Community 29 - "AIBrowserAgent"
Cohesion: 0.12
Nodes (16): AIBrowserAgent, Capture the current page as a PNG screenshot., Build the prompt with task description and action history., Parse Gemini's response into an action dict., Call Gemini API with exponential backoff retry., Execute a parsed action on the browser page., Detect if the agent is stuck repeating the same action., Find all visible interactive elements and format them as a prompt guide. (+8 more)

### Community 30 - "rate_search_routes.py"
Cohesion: 0.07
Nodes (64): get_recent_search_status_context(), Chat Service — manages conversational AI queries from the frontend user using…, Queries the database for the most recent rate search status to give the chatbot…, get_sync_url(), run_migrations_offline(), run_migrations_online(), get_admin_analytics_endpoint(), get_batch_search_status() (+56 more)

### Community 31 - "ONEConnector"
Cohesion: 0.11
Nodes (13): ONEConnector, date, Parses ONE QUOTE Free Time popover text for DESTINATION ONLY. Ignores Origin…, Splits a single raw multi-container quote card into multiple QuoteSchema…, test_live_one_bangalore(), main(), Verification script for ONE multi-container implementation., main() (+5 more)

### Community 32 - "_Page"
Cohesion: 0.15
Nodes (8): _connector(), _Locator, _Page, Maersk's login page redirects to the Hub a few seconds after loading when the…, Sits on /portaluser/login, then redirects after `redirect_after` URL reads., test_login_uses_saved_session_after_late_redirect(), test_wait_detects_late_redirect(), test_wait_detects_login_form()

### Community 33 - "Engineering Report: Sourcing Portal Enhancements & Scraping Pipeline Stability"
Cohesion: 0.08
Nodes (23): 1. Anti-Bot Mitigation & CAPTCHA Human-in-the-Loop Recovery, 2. Sourcing Parallelization & Surcharges Optimization, 3. Autocomplete Intelligence & Location Mapping, 4. Scraper Pipeline Maintenance, 5. Infrastructure & DevSecOps Enhancements, Business Value, Business Value, Business Value (+15 more)

### Community 34 - "Changelog"
Cohesion: 0.14
Nodes (13): [2026-05-18 – 2026-05-19] — Railway Deployment & Docker, [2026-05-25 – 2026-05-26] — VNC Display Isolation & Proxy Integration, [2026-07-03] — Robustness Review & Multi-Port Quick Search Fixes, [2026-07-08] — OOCL E-Quote Calendar Navigation, cheapest E-Spot selection, and E-Quote/E-Spot isolation refinements, [2026-07-09] — Hapag-Lloyd Quick Quotes pairing and selection simplification, Bright Data ISP Proxy Integration, Changelog, Hapag-Lloyd — Quick Quotes Simplification & Clean Pairing (+5 more)

### Community 35 - "admin/page.tsx"
Cohesion: 0.07
Nodes (43): UserRecord, AdminCarriers(), PROFILE_NAMES, when(), AdminAnalytics, AdminOverview(), AdminOverviewProps, AdminOverviewUser (+35 more)

### Community 36 - "package.json"
Cohesion: 0.12
Nodes (16): engines, node, name, packageManager, private, version, clsx, react-dom (+8 more)

### Community 37 - "dependencies"
Cohesion: 0.15
Nodes (13): dependencies, class-variance-authority, clsx, exceljs, lucide-react, next, next-themes, @radix-ui/react-slot (+5 more)

### Community 38 - "RateResults.tsx"
Cohesion: 0.07
Nodes (53): BatchProgressPanel(), BatchProgressPanelProps, cheapest(), Filter, lanePhase(), Phase, PHASE_STYLE, LiveSearchProgressProps (+45 more)

### Community 39 - "SearchQueueManager"
Cohesion: 0.14
Nodes (9): Marks a search as completed internally so we can track the auto-release timeout., Called periodically in a background task to check if the user has held the lock…, Forcefully clears all queued searches and the active lock. Useful for…, Adds a search to the queue and waits until it becomes the active search. Event-…, Singleton manager to enforce a FIFO queue for rate searches. Since web scraping…, Returns the current position of the search in the queue. 0 means it is the…, Releases the lock so the next user can proceed. Returns True if a lock was…, SearchQueueManager (+1 more)

### Community 40 - "ChargeCategory"
Cohesion: 0.20
Nodes (21): ChargeCategory, classify_charge(), Charge Classifier — rule-based classification of freight charge line items.…, Classify a charge line item based on its name, amount, section heading, and…, Tests for charge classifier., test_basic_ocean_freight(), test_cwx_heavy_weight_charge(), test_destination_charges() (+13 more)

### Community 41 - "Frontend Redesign — Componentry Design System, Workspace & Launch Intro (2026-09-07)"
Cohesion: 0.14
Nodes (13): 1. Design system foundation (`082b43a`), 2. Bugs found and fixed during the restyle, 3. Workspace + launch intro (`21ade75`), 4. Follow-up fixes (`2f9d92b`), 5. Verification, 7. Conventions to follow from here, Dependencies added (5, all small, no runtime lib dependency on Componentry), Frontend Redesign — Componentry Design System, Workspace & Launch Intro (2026-09-07) (+5 more)

### Community 42 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 43 - "resolve_port_for_carrier"
Cohesion: 0.21
Nodes (10): Resolves input text (e.g. 'Belfast (GBBEL)' or 'GBBEL') to a tuple of…, resolve_msc_port(), Resolves input text to (location_name, locode, country_code, country_name)., Fills the origin/destination 'Enter Port or Door Point' autocomplete. The…, resolve_oocl_port_info(), resolve_port_for_carrier(), Verify non-Maersk carriers get standard UN/LOCODE or default mappings., Verify that El Dekheila maps specifically to 'Alexandria Dekheila, Egypt' for… (+2 more)

### Community 44 - "test_carrier_timeout.py"
Cohesion: 0.13
Nodes (16): _create_sqlite_engine(), _get_engine(), _get_session_maker(), init_db(), Create all tables on startup with automatic fallback to local SQLite if…, check_db(), CrashingConnector, HangingConnector (+8 more)

### Community 45 - "devDependencies"
Cohesion: 0.22
Nodes (9): devDependencies, eslint, eslint-config-next, tailwindcss, @tailwindcss/postcss, @types/node, @types/react, @types/react-dom (+1 more)

### Community 46 - "dithered-logo.tsx"
Cohesion: 0.19
Nodes (15): applyMaskInversion(), buildRoundedMask(), DEFAULTS, DitherConfig, DitheredLogo(), DitheredLogoProps, drawParticles(), errorDiffusionDither() (+7 more)

### Community 47 - "👥 The 5 Agent Roles"
Cohesion: 0.13
Nodes (14): 1. Intake Agent (Email Listener), 2. Sourcing Orchestrator (The Coordinator), 3. Sourcing & Scraping Agent (Rates Engine), 4. Finance & Costing Agent (Excel Compiler), 5. Email Draft Agent (Communicator), 📋 Executive Summary, 🛠️ Implementation Stages, Phase 1: Email Integration (Week 1-2) (+6 more)

### Community 48 - "HapagLloydConnector"
Cohesion: 0.06
Nodes (32): HapagLloydConnector, HapagServiceUnavailableException, Exception, Normalize various date formats (e.g. 2026-05-31, 31.05.2026, 31 May 2026, 31…, Robustly selects options from Hapag-Lloyd custom dropdown lists. Types the…, Detects the Microsoft B2C identity/OAuth login page. Hapag can silently bounce…, Guards against the session-expiry-mid-crawl failure mode: the existing redirect…, Crawls Hapag-Lloyd sailing schedules from the Schedule tab. (+24 more)

### Community 49 - "CarrierResultStatus"
Cohesion: 0.06
Nodes (24): Override to immediately return CONNECTOR_NOT_AVAILABLE., Splits a single raw multi-container quote card into multiple QuoteSchema…, Required abstract method implementation; delegates to run_full_search., Batch (RFQ) mode: the base implementation drives a browser page, so answer from…, Called by job_service once per container type (request.container_type). All…, Executes full rate search against Hapag-Lloyd Prices API. Queries each…, Execute the full search flow with Progressive Lazy Loading: 1. Login 2. Search…, Splits a single raw multi-container quote card into multiple QuoteSchema… (+16 more)

### Community 50 - "tunnel_relay/main.py"
Cohesion: 0.29
Nodes (7): api_route, health(), get, Request, websocket, relay_request(), websocket_endpoint()

### Community 51 - "CurrencyManager"
Cohesion: 0.23
Nodes (7): convert_currency_to_usd(), CurrencyManager, get_all_exchange_rates(), Any, Currency Exchange Rate Service — manages currency conversions and custom…, update_exchange_rate(), threading

### Community 52 - "test_one_charge_override.py"
Cohesion: 0.40
Nodes (3): MockCard, Unit test for ONE connector charge classification override., test_emergency_surcharge_override()

### Community 53 - "test_hapag_freetime.py"
Cohesion: 0.18
Nodes (15): _apply_freetime_to_quote(), freetime_days(), match_freetime_entry(), Any, Destination free time from config/hapag_freetime.json, shared by the Hapag-…, Days for this container from a table entry ({"20GP": n, "40GP": n} or a bare…, The table entry whose country name appears in `text` as whole words. Whole…, days() (+7 more)

### Community 54 - "🚢 Infreight Sourcing & Ocean Rate Automation System"
Cohesion: 0.14
Nodes (13): 1. Multi-Carrier Automation Engine, 2. Intelligent Surcharge & Charge Classifier Engine (`charge_classifier.py`), 3. Container Comparison Matrix & Excel Export Engine, 🚢 Infreight Sourcing & Ocean Rate Automation System, 🌟 Key Capabilities, 📄 License & Confidentiality, Prerequisites, 🛠️ Project Structure (+5 more)

### Community 55 - "MaerskConnector"
Cohesion: 0.07
Nodes (22): _is_logged_in_url(), MaerskConnector, flatten_tree(), Maersk Browser Connector — Playwright automation using your real Google Chrome…, Wait until the login page either redirects to a signed-in page or shows its…, Extracts freetime, demurrage, and detention from the 'Import D&D fees' tab…, Extracts the routing details from the 'Route & other details' accordion.…, True once Maersk has moved past the login pages to a signed-in page. (+14 more)

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

### Community 60 - "test_one_premium_override.py"
Cohesion: 0.40
Nodes (3): MockCard, Unit test for ONE connector and charge classifier Premium Cargo Service…, test_premium_cargo_service_override()

### Community 62 - "[2026-06-30] — ONE Multi-Container & Sold-Out, GreenX Surcharge Intake, Free-Time Fixes, Maersk Diagnosis"
Cohesion: 0.29
Nodes (7): [2026-06-30] — ONE Multi-Container & Sold-Out, GreenX Surcharge Intake, Free-Time Fixes, Maersk Diagnosis, GreenX — Only Basic Ocean Freight & LSS Folded Into Final Value, MAERSK — "Quotes Found" but Empty Excel (Diagnosis), ONE — All-Container-Type Search Returning 0 Quotes, ONE — Multi-Container Breakdown Triple-Counted / Inflated Final Value, ONE — Sold-Out ("Notify Me") Sailings Appearing as Quotes, Performance/Reliability — Stop Copying Chrome Caches During Profile Clone/Sync

### Community 63 - "[2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup"
Cohesion: 0.22
Nodes (8): [2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup, Chromium Cache Auto-Cleanup (Railway Storage Bloat Prevention), CMA CGM — 30-Second Timeout on Sold Out Cards, CMA CGM — Free Time Regex Too Strict, CMA CGM — Routing Regex Not Matching "via LEKKI, LA, NG", Excel Export — Routing & Free Time Columns Always Empty, Excel Export — Sold Out Rows Not Showing, Maersk — Hardcoded Port Overrides

### Community 64 - "compute_admin_analytics"
Cohesion: 0.25
Nodes (8): compute_admin_analytics(), get_clean_lane_key(), normalize_lane_port(), Any, AsyncSession, Normalize port string to cleanly aggregate naming variations., Returns (norm_origin, norm_dest, display_lane_key)., Compute full consolidated analytics payload for the admin dashboard.

### Community 65 - "RFQParseResult"
Cohesion: 0.17
Nodes (12): parse_rfq_endpoint(), post, API routes for RFQ parsing agent., Parse a free-text RFQ email or message into a structured RateSearchRequest…, RFQParseRequest, RFQParseResult, Test Image 2: Air rate request generates 3 drafts to Glenn (AWOT), Jing Hui…, Test Guardrail: Detects Reefer container request and returns unsupported_cargo… (+4 more)

### Community 66 - "GreenX — Surcharge Intake Fix (2026-06-30)"
Cohesion: 0.22
Nodes (8): Charges that must be taken into the final value (USD only), Files changed, Fix, GreenX — Surcharge Intake Fix (2026-06-30), Per-B/L charges (billed once per booking, added in full to *each* container type), Problem, Root cause, Verification

### Community 67 - "Admin Page & Port Prioritization Guide"
Cohesion: 0.25
Nodes (7): 1. Popular Ports (UN/LOCODEs), 2. Boosted Countries, Admin Page & Port Prioritization Guide, 🔒 How to Access the Admin Page, ⚙️ How to Use Port Prioritization, ⚡ Important Notes, 📝 Step-by-Step Example

### Community 68 - "[2026-07-03] — OOCL FreightSmart Autoclear, Hapag Price Leak & Redirect fixes, Maersk Cache Scoping, Dallas Overrides"
Cohesion: 0.50
Nodes (4): [2026-07-03] — OOCL FreightSmart Autoclear, Hapag Price Leak & Redirect fixes, Maersk Cache Scoping, Dallas Overrides, Hapag-Lloyd — Price Leaks, Column Matching, and Redirect Recovery, OOCL — FreightSmart Popup Dismissals & Input Lock Serialization, Ports — Hardcoded Dallas Override

### Community 69 - "test_self_healing.py"
Cohesion: 0.06
Nodes (53): _local_fuzzy_repair(), AI Repair Agent — diagnoses Playwright step failures and suggests selector…, A local rule-based heuristic to locate reasonable buttons or inputs when Gemini…, Analyzes the failure context and DOM content to suggest a selector repair. Uses…, suggest_fix(), handle_chat_query(), _local_chatbot_fallback(), Intelligent responder for search status, carrier guidance, air/sea info, and… (+45 more)

### Community 70 - "test_panama_canal_surcharge.py"
Cohesion: 0.18
Nodes (11): Sort container types in standard order: DRY 20 (20GP) -> DRY 40 (40GP) -> DRY…, sort_container_types(), asyncio, Verify charge_classifier classifies Panama Canal Surcharge as…, Verify regex extraction of Estimated Transportation Days from Hapag-Lloyd modal…, Verify OOCL normalize_result incorporates Panama Canal Surcharge (PCS)., test_charge_classifier_panama_canal_surcharge(), test_container_types_standard_ordering() (+3 more)

### Community 71 - "carrier_switches.py"
Cohesion: 0.27
Nodes (12): carrier_switch_status(), Which carriers an admin has switched off (and why), for the search form., get_switches(), off_message(), _path(), Admin on/off switch per carrier, for when a carrier's site is down or under…, Every switchable carrier: {"enabled", "reason", "updated_by", "updated_at"}; on…, The message for a switched-off carrier's result, or None when it is on. (+4 more)

### Community 72 - "deploy"
Cohesion: 0.25
Nodes (7): build, builder, deploy, restartPolicyMaxRetries, restartPolicyType, startCommand, $schema

### Community 73 - ".search_quotes"
Cohesion: 0.11
Nodes (12): extract_locode_and_country(), prepare_maersk_query(), Extracts LOCODE and country name from text like 'CASABLANCA, MOROCCO (MACAS)'…, Maps standard container search codes (e.g. 'DRY 20', '20GP') to Maersk Spot…, Scores a Maersk autocomplete dropdown suggestion. NOTE: The nested/indented…, Visible page size, read from the page., Move the real mouse pointer to (x, y) along a slightly curved, uneven path.…, Scroll with the wheel if needed, glide to the element, hover, then press and… (+4 more)

### Community 74 - "parse_msc_modal_charges"
Cohesion: 0.24
Nodes (8): parse_msc_modal_charges(), Parses charges from MSC BreakdownModal text. Correctly includes charges whose…, Test MSC charges parsing for Singapore to Conakry, Guinea (40GP). Charges with…, Test when only some surcharges have the payment condition., test_msc_charges_mixed_conditions(), test_msc_charges_singapore_to_conakry_guinea(), Verify MSC charge extraction logic parses Panama Canal Surcharge properly., test_msc_charge_extraction_logic()

### Community 75 - "Summary of Changes — July 20, 2026"
Cohesion: 0.29
Nodes (6): 1. AI RFQ Front Door & Air Freight Support (Phase A), 2. Multi-Origin & Gappy List Parsing for Sea RFQs (Phase B), 3. Search Form Streamlining (Form Input Restrictions), 4. Native Gemini 2.5 Flash API & Chatbot Resiliency, 5. Verification & Test Suite, Summary of Changes — July 20, 2026

### Community 76 - "_detect_port_mismatch"
Cohesion: 0.25
Nodes (8): _detect_port_mismatch(), Detects port mismatch for origin or destination. Returns: - True if verified…, Test that matching LOCODE or City + Country code returns False (Verified Match)., Test that differing port strings return True (Verified Mismatch)., Test that null/empty matched port strings return None (Unknown / Could Not…, test_detect_port_mismatch_unknown_null(), test_detect_port_mismatch_verified_match(), test_detect_port_mismatch_verified_mismatch()

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

### Community 83 - "layout.tsx"
Cohesion: 0.22
Nodes (7): frontend_src_app_globals, instrumentSans, inter, metadata, viewport, ThemeProvider(), next-themes

### Community 84 - "[2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning"
Cohesion: 0.22
Nodes (8): Verifies the "I am the price owner" radio is genuinely checked, piercing shadow…, [2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning, Hapag-Lloyd — Configurable Pacing & Redundant-Wait Removal, Job Scheduler — Concurrency Default, Maersk — 0.0-USD / "Not Open" Card Flakiness (the "Quotes Found but Empty Excel" root causes), Maersk — Caching Scope & Selector Tuning, Maersk — Regression: Other-Container-Type Sizes Went "Sold Out" in Multi-Container Searches, OOCL — Schedule Search Repeated Once Per Container Type

### Community 85 - "[2026-06-03] — CMA CGM Routing & Free Time Extraction"
Cohesion: 0.50
Nodes (4): [2026-06-03] — CMA CGM Routing & Free Time Extraction, CMA CGM — Import Free Time from D&D Tab, CMA CGM — Routing Detection (Direct vs Transit), Maersk — Free Time Extraction from Card Text

### Community 86 - ".search_quotes"
Cohesion: 0.29
Nodes (3): date, Type a LOCODE into the autocomplete field and click the first visible dropdown…, Find quantity input next to or below label_text and fill it.

### Community 87 - "hapag_lloyd_connector.py"
Cohesion: 0.10
Nodes (20): Normalize CMA CGM data into QuoteSchema. Rule: include BASIC_OCEAN_FREIGHT and…, RateLimiter, Hapag-Lloyd Prices API Connector (REST API v2.1.4). Provides real-time rate…, Token-bucket rate limiter to strictly respect Tryout/Production rate limits., # NOTE: No start date fill needed — schedule page defaults to today,, Hapag-Lloyd Live Connector -- Playwright automation. Credentials read from env:…, get_booking_start_date(), date (+12 more)

### Community 88 - "os"
Cohesion: 0.05
Nodes (36): argparse, asyncio, Page Observer — captures page state (screenshot, DOM, visible text) on failure., GreenX (Evergreen) Live Connector - Playwright automation., dump_options(), main(), Diagnostic: dump ALL dropdown options (text + innerHTML) when typing 'DEHAM'…, AI Browser Agent — Vision-based browser automation using Gemini Flash. This… (+28 more)

### Community 89 - "test_hapag_api_connector.py"
Cohesion: 0.48
Nodes (6): main(), Standalone Test & Verification Suite for Hapag-Lloyd Prices REST API Connector.…, test_locode_resolution(), test_payload_generation(), test_registry_integration(), test_response_parsing_and_normalization()

### Community 90 - "one_connector.py"
Cohesion: 0.13
Nodes (10): fill_container_card(), ONE (Ocean Network Express) Live Connector — Playwright automation. Credentials…, Tries to click a matching option from ONE's visible dropdown. Returns True only…, # TODO: Verify selectors against ONE ecommerce portal, get_carrier_search_query(), get_port_by_code(), Resolves a port search text (e.g. 'Haiphong (VN HPH)', 'VN HPH', 'Hai Phong')…, Constructs the specific search query to type into carrier search boxes. If the… (+2 more)

### Community 92 - "AppHeader.tsx"
Cohesion: 0.43
Nodes (5): AppHeader(), AppHeaderProps, initials(), systemStatus(), ThemeToggle()

### Community 93 - "[2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History"
Cohesion: 0.40
Nodes (5): [2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History, Admin User Search History & SGT GMT+8 Conversion (`AdminDashboard.tsx`), GreenX (Evergreen) Card Isolation & Surcharge Parsing (`greenx_connector.py`), Multi-Route Batch Execution Engine (`batch_engine.py`), OOCL FreightSmart 28-Day Calendar Expansion (`oocl_connector.py`)

### Community 94 - "[2026-06-01] — Hapag-Lloyd Sold Out Detection & Date Parsing"
Cohesion: 0.67
Nodes (3): [2026-06-01] — Hapag-Lloyd Sold Out Detection & Date Parsing, Hapag-Lloyd — Date String Standardization, Hapag-Lloyd — Sold Out Schedule Detection

### Community 95 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, dev, lint, start

### Community 96 - "frontend/README.md"
Cohesion: 0.50
Nodes (3): Deploy on Vercel, Getting Started, Learn More

### Community 97 - "pytest"
Cohesion: 0.12
Nodes (12): ambiguous_python_import_b35980c0aa01, asyncio, Integration tests for authentication, legacy user password setup, pending…, test_full_auth_lifecycle(), parse_hapag_card_text_mock(), Verify that multi-leg/feeder routes take the final arrival ETA and 28 days TT., Mock implementation of the JS evaluate logic inside hapag_lloyd_connector.py., test_hapag_multi_leg_schedule_extraction() (+4 more)

### Community 98 - "[2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control"
Cohesion: 0.40
Nodes (5): [2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control, Concurrency Limit Queue & Admin Control Panel, MSC — Mediterranean Shipping Company Connector Implementation, ONE — Inbound Free Time Swap & Scraper Upgrade, OOCL — Orient Overseas Container Line Connector Implementation

### Community 101 - "[2026-05-20 – 2026-05-22] — Port Resolution & Frontend Improvements"
Cohesion: 0.50
Nodes (4): [2026-05-20 – 2026-05-22] — Port Resolution & Frontend Improvements, Excel Export — ETA Column & Container Type Header, Frontend Light Mode & CORS Fix, Port Resolution System

### Community 102 - "[2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash"
Cohesion: 0.40
Nodes (5): [2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash, AI RFQ Front Door & Air Freight Support, Multi-Origin & Gappy List Parsing (Sea RFQs), Native Gemini 2.5 Flash Direct API Integration, Search Form Streamlining

### Community 106 - "[2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes"
Cohesion: 0.50
Nodes (4): [2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes, CMA CGM — Chrome Profile Bypass, ONE — Date Formatting & Charge Breakdown Pollution, ONE — Date Picker Pre-selection Issue

### Community 116 - "eslint.config.mjs"
Cohesion: 0.50
Nodes (3): eslintConfig, eslint, eslint-config-next

### Community 117 - "[2026-05-23 – 2026-05-24] — Maersk Shadow DOM & Stealth Upgrades"
Cohesion: 0.50
Nodes (4): [2026-05-23 – 2026-05-24] — Maersk Shadow DOM & Stealth Upgrades, Maersk — 2FA/CAPTCHA Human-in-the-Loop via noVNC, Maersk — Login Credential Autofill Corruption, Maersk — Shadow DOM Piercing for MDS Web Components

### Community 119 - "get_me"
Cohesion: 0.67
Nodes (3): get_me(), get, Get profile of currently signed-in user.

### Community 120 - "Architecture Overview"
Cohesion: 0.50
Nodes (4): Architecture Overview, Carrier Connector Lifecycle, Charge Classification Rules, Search Flow

### Community 121 - "verify_admin_access"
Cohesion: 0.67
Nodes (3): Request, Verify that caller has admin privileges via session cookie, Bearer token, or…, verify_admin_access()

### Community 122 - "[2026-05-31] — Multi-Instance Support & Charge Classification"
Cohesion: 0.67
Nodes (3): [2026-05-31] — Multi-Instance Support & Charge Classification, Charge Classification Improvements, Multi-Instance Concurrent Searches

### Community 124 - "[2026-06-02] — Hapag-Lloyd Transshipment & Duplicate Fix"
Cohesion: 0.67
Nodes (3): [2026-06-02] — Hapag-Lloyd Transshipment & Duplicate Fix, Hapag-Lloyd — Duplicate Sailings from Transshipment Vessels, Hapag-Lloyd — Routing Not Marked as Transit

## Knowledge Gaps
- **313 isolated node(s):** `Config`, `install_pi.sh script`, `eslintConfig`, `nextConfig`, `name` (+308 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 938 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **22 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Changelog` connect `Changelog` to `PortManager`, `OOCLConnector`, `[2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split`, `[2026-06-30] — ONE Multi-Container & Sold-Out, GreenX Surcharge Intake, Free-Time Fixes, Maersk Diagnosis`, `[2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup`, `[2026-07-03] — OOCL FreightSmart Autoclear, Hapag Price Leak & Redirect fixes, Maersk Cache Scoping, Dallas Overrides`, `[2026-05-29 – 2026-05-30] — Hapag-Lloyd Full Integration`, `[2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning`, `[2026-06-03] — CMA CGM Routing & Free Time Extraction`, `[2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History`, `[2026-06-01] — Hapag-Lloyd Sold Out Detection & Date Parsing`, `[2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control`, `[2026-05-20 – 2026-05-22] — Port Resolution & Frontend Improvements`, `[2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash`, `[2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes`, `[2026-05-23 – 2026-05-24] — Maersk Shadow DOM & Stealth Upgrades`, `Architecture Overview`, `[2026-05-31] — Multi-Instance Support & Charge Classification`, `[2026-06-02] — Hapag-Lloyd Transshipment & Duplicate Fix`?**
  _High betweenness centrality (0.337) - this node is a cross-community bridge._
- **Why does `[2026-06-03] — CMA CGM Routing & Free Time Extraction` connect `[2026-06-03] — CMA CGM Routing & Free Time Extraction` to `Changelog`?**
  _High betweenness centrality (0.303) - this node is a cross-community bridge._
- **Why does `Maersk — Free Time Extraction from Card Text` connect `[2026-06-03] — CMA CGM Routing & Free Time Extraction` to `RateResults.tsx`?**
  _High betweenness centrality (0.302) - this node is a cross-community bridge._
- **Are the 32 inferred relationships involving `RateSearchRequest` (e.g. with `create_batch_rate_search()` and `create_rate_search()`) actually correct?**
  _`RateSearchRequest` has 32 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `cn()` (e.g. with `Reuse the primitives` and `7. Conventions to follow from here`) actually correct?**
  _`cn()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 21 inferred relationships involving `CarrierResultStatus` (e.g. with `safe_step()` and `update_carrier_status()`) actually correct?**
  _`CarrierResultStatus` has 21 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Config`, `install_pi.sh script`, `eslintConfig` to the rest of the system?**
  _313 weakly-connected nodes found - possible documentation gaps or missing edges._