# Graph Report - Infreight_SourcingRates_SG  (2026-10-08)

## Corpus Check
- 240 files · ~1,158,759 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 21 file(s) not represented in the graph (top: (none) 8, .bat 6, .conf 2)

## Summary
- 2310 nodes · 5669 edges · 135 communities (110 shown, 25 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 330 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `852309b6`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- BaseCarrierConnector
- cn
- user_routes.py
- auth_routes.py
- browser_cleanup.py
- RateSearchRequest
- api.ts
- PortManager
- selector_memory.py
- CMAConnector
- os
- CarrierSearchResult
- safe_step
- ._fs_dismiss_modals
- CarrierResultStatus
- preferences.ts
- test_rfq_agent.py
- database.py
- SocialWidget.tsx
- MobileTabBar.tsx
- GreenXConnector
- social_routes.py
- scrape_one_freetime.py
- backend/main.py
- rate_search_routes.py
- MSCConnector
- parse_rfq
- lucide-react
- AIBrowserAgent
- job_service.py
- ONEConnector
- _Page
- Engineering Report: Sourcing Portal Enhancements & Scraping Pipeline Stability
- Changelog
- react
- package.json
- test_hapag_freetime.py
- RateResults.tsx
- SearchQueueManager
- ChargeCategory
- Frontend Redesign — Componentry Design System, Workspace & Launch Intro (2026-09-07)
- compilerOptions
- login/page.tsx
- test_carrier_timeout.py
- RateSearch
- dithered-logo.tsx
- 👥 The 5 Agent Roles
- HapagLloydConnector
- QuoteSchema
- port_manager.py
- CurrencyManager
- parse_msc_modal_charges
- test_one_premium_override.py
- 🚢 Infreight Sourcing & Ocean Rate Automation System
- AdminUsers.tsx
- [2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split
- test_self_healing.py
- 🛠 Detailed Carrier Log
- ._fs_pair_and_select
- safe_step.py
- .search_quotes
- [2026-05-18 – 2026-05-19] — Railway Deployment & Docker
- [2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup
- [2026-05-31] — Multi-Instance Support & Charge Classification
- layout.tsx
- GreenX — Surcharge Intake Fix (2026-06-30)
- Admin Page & Port Prioritization Guide
- ._verify_price_owner_selected
- orbit-card-stack.tsx
- MockCard
- dependencies
- deploy
- .login
- time
- Summary of Changes — July 20, 2026
- analytics_service.py
- port_routes.py
- resolve_port_alias
- test_brightdata.py
- tunnel_client.py
- Design system — read before touching any UI
- test_panama_canal_surcharge.py
- [2026-05-29 – 2026-05-30] — Hapag-Lloyd Full Integration
- auth_service.py
- get_me
- excelExport.ts
- RateLimiter
- resolve_port_for_carrier
- [2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History
- devDependencies
- [2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning
- headed_login_maersk.py
- [2026-06-03] — CMA CGM Routing & Free Time Extraction
- get_port_by_code
- test_one_charge_override.py
- frontend/README.md
- pytest
- [2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control
- ._save_carrier_overrides
- sort_container_types
- [2026-05-20 – 2026-05-22] — Port Resolution & Frontend Improvements
- ai_repair_agent.py
- run_carrier
- Working in this repository
- .search_quotes
- install_pi.sh
- models/__init__.py
- postcss.config.mjs
- fill_container_card
- [2026-05-23 – 2026-05-24] — Maersk Shadow DOM & Stealth Upgrades
- .run_full_search
- [2026-06-01] — Hapag-Lloyd Sold Out Detection & Date Parsing
- .search_port
- [2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash
- scripts
- diagnose_greenx_dropdown.py
- [2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes
- eslint.config.mjs
- MaerskConnector
- auto_updater.py
- .get_carrier_lock
- [2026-06-02] — Hapag-Lloyd Transshipment & Duplicate Fix
- .suggest_ports
- test_placeholder

## God Nodes (most connected - your core abstractions)
1. `RateSearchRequest` - 158 edges
2. `cn()` - 87 edges
3. `CarrierResultStatus` - 69 edges
4. `QuoteSchema` - 67 edges
5. `PortManager` - 58 edges
6. `User` - 57 edges
7. `HapagLloydConnector` - 56 edges
8. `CMAConnector` - 55 edges
9. `BaseCarrierConnector` - 50 edges
10. `OOCLConnector` - 49 edges

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

## Communities (135 total, 25 thin omitted)

### Community 1 - "BaseCarrierConnector"
Cohesion: 0.05
Nodes (29): ABC, BaseCarrierConnector, NotAvailableConnector, Any, Open the price breakdown / detail view for a specific quote. Args: quote_ref:…, Extract individual charge line items from the price breakdown. Returns: List of…, Abstract base class for carrier portal connectors., Detects if a CAPTCHA, Turnstile, hCaptcha, reCAPTCHA, or 2FA screen is… (+21 more)

### Community 2 - "cn"
Cohesion: 0.11
Nodes (32): Reuse the primitives, New primitives — `frontend/src/components/ui/`, Badge(), badgeVariants, Dot(), Card(), CardContent(), CardDescription() (+24 more)

### Community 3 - "user_routes.py"
Cohesion: 0.08
Nodes (66): admin_delete_user(), AdminLoginRequest, approve_user(), CarrierOverrideRequest, Config, create_custom_port_endpoint(), CustomPortRequest, delete_carrier_override_endpoint() (+58 more)

### Community 4 - "auth_routes.py"
Cohesion: 0.08
Nodes (48): clear_session_cookie(), get_current_user_optional(), login(), LoginRequest, logout(), AsyncSession, BaseModel, post (+40 more)

### Community 5 - "browser_cleanup.py"
Cohesion: 0.07
Nodes (38): flatten_tree(), Execute the full search flow with Progressive Lazy Loading: 1. Login 2. Search…, Extracts freetime, demurrage, and detention from the 'Import D&D fees' tab…, Extracts the routing details from the 'Route & other details' accordion.…, Splits a single raw multi-container quote card into multiple QuoteSchema…, _is_chrome(), _is_playwright_driver(), _kill() (+30 more)

### Community 6 - "RateSearchRequest"
Cohesion: 0.06
Nodes (38): clean_vessel_name(), OOCLConnector, _parse_date(), parse_oocl_date(), Parses one FreightSmart result card's inner text into a raw row dict. Text-…, Opens the Details dialog for a card, clicks the Charge Breakdown tab, extracts…, Collects result cards from the FreightSmart quote results page., Serves one container-type cycle from the cached merged quote set: -… (+30 more)

### Community 7 - "api.ts"
Cohesion: 0.08
Nodes (58): AdminDashboard(), HomeContent(), BackendConfigModal(), BackendConfigModalProps, LoadingState(), SearchCompletionModal(), SearchCompletionModalProps, addCarrierOverride() (+50 more)

### Community 8 - "PortManager"
Cohesion: 0.14
Nodes (5): PortManager, Retrieve verified carrier port name from persistent cache by UN/LOCODE,…, Cache verified carrier port name and save persistently to…, Clean and normalize user input for port searching., Retrieve port data by full UN/LOCODE (e.g., 'SGSIN').

### Community 9 - "selector_memory.py"
Cohesion: 0.24
Nodes (12): get_approved_selector(), _load_memory(), Selector Memory — stores and retrieves human-approved selector patches., Loads memory JSON file. Returns empty dict if file is missing or invalid., Saves memory dict back to JSON file., Looks up if there is an approved replacement selector for the given carrier and…, Stores an approved replacement selector., Marks any proposed selector for this step as REJECTED. (+4 more)

### Community 10 - "CMAConnector"
Cohesion: 0.07
Nodes (21): CMAConnector, Ensures 'Ramp' is explicitly selected under 'Type of location' toggle buttons…, Scans for Route, POL (Port of Loading), or POD (Port of Discharge) dropdown…, Clears the currently selected Destination port tag/card, re-types the locode,…, Dynamically extracts any recommended 5-letter POD LOCODE mentioned in the…, Detects if CMA CGM displayed an advisory banner message: "Looking for AEJEA or…, Handles the 'Customer account' -> 'Role (you are acting as)' dropdown on CMA…, Repeatedly clicks 'More results' if visible to load ALL quotes on the page. (+13 more)

### Community 11 - "os"
Cohesion: 0.06
Nodes (51): asyncio, Manual Action Detector — identifies pages requiring human verification (2FA,…, Page Observer — captures page state (screenshot, DOM, visible text) on failure., Base Carrier Connector — abstract base class for all carrier connectors. Each…, CMA CGM Live Connector — Playwright automation. Credentials read from env:…, GreenX (Evergreen) Live Connector - Playwright automation., Hapag-Lloyd Prices API Connector (REST API v2.1.4). Provides real-time rate…, # NOTE: No start date fill needed — schedule page defaults to today, (+43 more)

### Community 12 - "CarrierSearchResult"
Cohesion: 0.24
Nodes (12): Updates the status of a carrier search in the database., update_carrier_status(), CarrierSearchResult, Tracks the result of searching a specific carrier for a rate search., Copy the connector's "port not found" note onto the result row, if it made one., _store_port_not_found(), _miss(), Port name fixes: connectors note ports their own search couldn't find, results… (+4 more)

### Community 13 - "safe_step"
Cohesion: 0.20
Nodes (9): capture_page_state(), Captures screenshot, DOM HTML, and inner text of the current page. Saves…, Executes a Playwright action. If it fails: 1. Detects CAPTCHA/bot challenges…, safe_step(), 1. What was measured, 3. Multi-port quick search — defects found and fixed, 4. Ranked recommendations, 5. Verification of this change (+1 more)

### Community 14 - "._fs_dismiss_modals"
Cohesion: 0.08
Nodes (21): _dismiss_once(), _click_date_strip_item(), _open_calendar(), Lock, Iterates through the FreightSmart results date calendar to collect E-Quote and…, Full FreightSmart phase: login â†’ fill quote form â†’ search â†’ extract rows., Shadow-DOM-aware check for whether the onboarding tour heading is on screen., Runs CONCURRENTLY with the rest of the FreightSmart form-filling flow and… (+13 more)

### Community 15 - "CarrierResultStatus"
Cohesion: 0.07
Nodes (28): HapagLloydAPIConnector, Any, AsyncClient, Direct REST API connector for Hapag-Lloyd Prices API v2.1.4., API connectors do not require browser login sessions., Required abstract method implementation; delegates to run_full_search., Batch (RFQ) mode: the base implementation drives a browser page, so answer from…, No browser session to reset between batch routes. (+20 more)

### Community 16 - "preferences.ts"
Cohesion: 0.09
Nodes (33): LaunchIntro(), SearchHistoryItem, derive(), Derived, startOfDay(), UsageStats(), ChoiceCard(), Toggle() (+25 more)

### Community 17 - "test_rfq_agent.py"
Cohesion: 0.10
Nodes (36): API routes for RFQ parsing agent., RFQParseResult, asyncio, Unit tests for the Gemini AI RFQ Agent service (parse_rfq). Includes…, Test Image 2: Air rate request generates 3 drafts to Glenn (AWOT), Jing Hui…, Test Image 4: Steel Plate ex Pasir Gudang / Tanjung Pelepas for 20' & 40'., Test Guardrail: Detects Reefer container request and returns unsupported_cargo…, Test Guardrail: Detects LCL request. (+28 more)

### Community 18 - "database.py"
Cohesion: 0.14
Nodes (21): get_sync_url(), run_migrations_offline(), run_migrations_online(), Base, _create_sqlite_engine(), _get_database_url(), _get_engine(), _get_session_maker() (+13 more)

### Community 19 - "SocialWidget.tsx"
Cohesion: 0.16
Nodes (21): ACCENT_COLORS, errorMessage(), relativeTime(), resizeImageToDataUrl(), SocialWidget(), SocialWidgetProps, EMOJI_GROUPS, EmojiPicker() (+13 more)

### Community 20 - "MobileTabBar.tsx"
Cohesion: 0.12
Nodes (20): ChatWidget(), ChatWidgetProps, Message, MenuRow(), MobileTab, MobileTabBar(), MobileTabBarProps, tabClass() (+12 more)

### Community 21 - "GreenXConnector"
Cohesion: 0.19
Nodes (4): GreenXConnector, Find the exact individual quote card container row encompassing dates, rates,…, Dismiss any cookie/alert modal that would intercept pointer events., inspect()

### Community 22 - "social_routes.py"
Cohesion: 0.11
Nodes (31): get_current_user(), Dependency that strictly requires an authenticated active member., get_conversation(), list_colleagues(), poke_colleague(), PokeRequest, AsyncSession, BaseModel (+23 more)

### Community 23 - "scrape_one_freetime.py"
Cohesion: 1.00
Nodes (3): check_and_wait_for_captcha(), login(), main()

### Community 24 - "backend/main.py"
Cohesion: 0.09
Nodes (20): api_route, health(), get, websocket, Infreight Ocean Carrier Rate Automation — FastAPI Application. Main entry point…, Check if the VNC viewer is available (production only, where Xvfb runs)., Proxy WebSocket connections to legacy local x11vnc at localhost:5900., Proxy WebSocket connections to specific carrier x11vnc servers. (+12 more)

### Community 25 - "rate_search_routes.py"
Cohesion: 0.07
Nodes (48): approve_repair(), ApproveRepairRequest, chat_endpoint(), ChatRequest, create_batch_rate_search(), _contains(), _looks_like(), _norm() (+40 more)

### Community 26 - "MSCConnector"
Cohesion: 0.16
Nodes (8): format_to_iso_date(), MSCConnector, Playwright-based automation for MSC (Mediterranean Shipping Company)., Handles the MSC login flow., Clicks Instant Quote, fills form, clicks Search., Detects and clicks the 'Ramp' delivery/haulage option if MSC displays Ramp /…, Parse '14 Jun 2026' to 'YYYY-MM-DD, test_msc()

### Community 27 - "parse_rfq"
Cohesion: 0.12
Nodes (27): parse_rfq_endpoint(), post, Parse a free-text RFQ email or message into a structured RateSearchRequest…, _call_native_gemini_api(), _detect_booking_confirmation(), _detect_dual_mode_enquiry(), _detect_mode_by_hierarchy(), _detect_unsupported_cargo() (+19 more)

### Community 28 - "lucide-react"
Cohesion: 0.10
Nodes (35): 0. The one invariant, CarrierMultiSelect(), CarrierMultiSelectProps, isAllCarriers(), toggleAllCarriers(), toggleCarrierSelection(), PortAutocomplete(), PortAutocompleteProps (+27 more)

### Community 29 - "AIBrowserAgent"
Cohesion: 0.13
Nodes (15): AIBrowserAgent, Capture the current page as a PNG screenshot., Build the prompt with task description and action history., Parse Gemini's response into an action dict., Call Gemini API with exponential backoff retry., Execute a parsed action on the browser page., Detect if the agent is stuck repeating the same action., Find all visible interactive elements and format them as a prompt guide. (+7 more)

### Community 30 - "job_service.py"
Cohesion: 0.11
Nodes (34): close_all_active_connectors(), get_connector(), Get the appropriate connector for a carrier. If USE_MOCK_CARRIERS=true: returns…, Force close all active carrier connectors and their Playwright Chrome windows., get_async_session_maker(), Get the session maker for use outside of FastAPI dependency injection., Quote, Represents a single freight quote from a carrier. (+26 more)

### Community 31 - "ONEConnector"
Cohesion: 0.09
Nodes (13): ONEConnector, _classify(), date, Parses ONE QUOTE Free Time popover text for DESTINATION ONLY. Ignores Origin…, Splits a single raw multi-container quote card into multiple QuoteSchema…, Tries to click a matching option from ONE's visible dropdown. Returns True only…, Extracts 5-letter UN/LOCODE from strings like 'Singapore [SGSIN]' or 'Singapore…, main() (+5 more)

### Community 32 - "_Page"
Cohesion: 0.15
Nodes (8): _connector(), _Locator, _Page, Maersk's login page redirects to the Hub a few seconds after loading when the…, Sits on /portaluser/login, then redirects after `redirect_after` URL reads., test_login_uses_saved_session_after_late_redirect(), test_wait_detects_late_redirect(), test_wait_detects_login_form()

### Community 33 - "Engineering Report: Sourcing Portal Enhancements & Scraping Pipeline Stability"
Cohesion: 0.08
Nodes (23): 1. Anti-Bot Mitigation & CAPTCHA Human-in-the-Loop Recovery, 2. Sourcing Parallelization & Surcharges Optimization, 3. Autocomplete Intelligence & Location Mapping, 4. Scraper Pipeline Maintenance, 5. Infrastructure & DevSecOps Enhancements, Business Value, Business Value, Business Value (+15 more)

### Community 34 - "Changelog"
Cohesion: 0.13
Nodes (14): [2026-05-25 – 2026-05-26] — VNC Display Isolation & Proxy Integration, [2026-07-03] — Robustness Review & Multi-Port Quick Search Fixes, [2026-07-08] — OOCL E-Quote Calendar Navigation, cheapest E-Spot selection, and E-Quote/E-Spot isolation refinements, [2026-07-09] — Hapag-Lloyd Quick Quotes pairing and selection simplification, Architecture Overview, Bright Data ISP Proxy Integration, Carrier Connector Lifecycle, Changelog (+6 more)

### Community 35 - "react"
Cohesion: 0.08
Nodes (41): UserRecord, AdminAnalytics, AdminOverview(), AdminOverviewProps, AdminOverviewUser, AnalyticsRange, Attention, attentionItems() (+33 more)

### Community 36 - "package.json"
Cohesion: 0.12
Nodes (15): engines, node, name, packageManager, private, version, clsx, react-dom (+7 more)

### Community 37 - "test_hapag_freetime.py"
Cohesion: 0.12
Nodes (21): Looks up standard destination demurrage/detention free time days., _apply_freetime_to_quote(), freetime_days(), match_freetime_entry(), Any, Days for this container from a table entry ({"20GP": n, "40GP": n} or a bare…, The table entry whose country name appears in `text` as whole words. Whole…, days() (+13 more)

### Community 38 - "RateResults.tsx"
Cohesion: 0.08
Nodes (43): ACTION_STATUSES, ChipModel, describe(), EMPTY_STATUSES, formatElapsed(), LiveSearchProgress(), LiveSearchProgressProps, parseServerTime() (+35 more)

### Community 39 - "SearchQueueManager"
Cohesion: 0.14
Nodes (9): Marks a search as completed internally so we can track the auto-release timeout., Called periodically in a background task to check if the user has held the lock…, Forcefully clears all queued searches and the active lock. Useful for…, Adds a search to the queue and waits until it becomes the active search. Event-…, Singleton manager to enforce a FIFO queue for rate searches. Since web scraping…, Returns the current position of the search in the queue. 0 means it is the…, Releases the lock so the next user can proceed. Returns True if a lock was…, SearchQueueManager (+1 more)

### Community 40 - "ChargeCategory"
Cohesion: 0.18
Nodes (23): ChargeCategory, classify_charge(), Charge Classifier — rule-based classification of freight charge line items.…, Classify a charge line item based on its name, amount, section heading, and…, Tests for charge classifier., test_basic_ocean_freight(), test_cwx_heavy_weight_charge(), test_destination_charges() (+15 more)

### Community 41 - "Frontend Redesign — Componentry Design System, Workspace & Launch Intro (2026-09-07)"
Cohesion: 0.14
Nodes (13): 1. Design system foundation (`082b43a`), 2. Bugs found and fixed during the restyle, 3. Workspace + launch intro (`21ade75`), 4. Follow-up fixes (`2f9d92b`), 5. Verification, 7. Conventions to follow from here, Dependencies added (5, all small, no runtime lib dependency on Componentry), Frontend Redesign — Componentry Design System, Workspace & Launch Intro (2026-09-07) (+5 more)

### Community 42 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 43 - "login/page.tsx"
Cohesion: 0.09
Nodes (22): nextConfig, 6. Known limitations / candidate follow-ups, LoginContent(), LoginModal(), LoginModalProps, RepairReport, SelfHealingAlerts(), SelfHealingAlertsProps (+14 more)

### Community 44 - "test_carrier_timeout.py"
Cohesion: 0.19
Nodes (10): CrashingConnector, HangingConnector, asyncio, A carrier whose browser hangs must be stopped after CARRIER_SEARCH_TIMEOUT_SEC…, Hangs on the sizes in `hang_on`; answers NO_QUOTES_AVAILABLE for the rest., Like a real connector whose tab dies: reports a crash, then never returns., _run(), test_crashed_tab_stops_the_carrier_without_waiting_for_the_timeout() (+2 more)

### Community 45 - "RateSearch"
Cohesion: 0.10
Nodes (24): get_recent_search_status_context(), Chat Service — manages conversational AI queries from the frontend user using…, Queries the database for the most recent rate search status to give the chatbot…, get_route_health(), Get carrier search reliability & route health matrix across origin-destination…, RateSearch, SQLAlchemy models for rate searches and carrier search results., Represents a rate search request from an employee. (+16 more)

### Community 46 - "dithered-logo.tsx"
Cohesion: 0.19
Nodes (15): applyMaskInversion(), buildRoundedMask(), DEFAULTS, DitherConfig, DitheredLogo(), DitheredLogoProps, drawParticles(), errorDiffusionDither() (+7 more)

### Community 47 - "👥 The 5 Agent Roles"
Cohesion: 0.13
Nodes (14): 1. Intake Agent (Email Listener), 2. Sourcing Orchestrator (The Coordinator), 3. Sourcing & Scraping Agent (Rates Engine), 4. Finance & Costing Agent (Excel Compiler), 5. Email Draft Agent (Communicator), 📋 Executive Summary, 🛠️ Implementation Stages, Phase 1: Email Integration (Week 1-2) (+6 more)

### Community 48 - "HapagLloydConnector"
Cohesion: 0.06
Nodes (33): HapagLloydConnector, HapagServiceUnavailableException, Exception, Normalize various date formats (e.g. 2026-05-31, 31.05.2026, 31 May 2026, 31…, Robustly selects options from Hapag-Lloyd custom dropdown lists. Types the…, Detects the Microsoft B2C identity/OAuth login page. Hapag can silently bounce…, Guards against the session-expiry-mid-crawl failure mode: the existing redirect…, Crawls Hapag-Lloyd sailing schedules from the Schedule tab. (+25 more)

### Community 49 - "QuoteSchema"
Cohesion: 0.10
Nodes (15): Normalize extracted data into a QuoteSchema using the normalizer. Args:…, _generate_maersk_mock_quotes(), _generate_msc_mock_quotes(), _generate_one_mock_quotes(), MockCarrierConnector, any, Mock Carrier Connector — returns realistic sample data for testing. Used when…, Generate realistic ONE sample quotes with charge breakdowns. (+7 more)

### Community 50 - "port_manager.py"
Cohesion: 0.25
Nodes (12): add_carrier_override(), add_custom_port(), delete_carrier_override(), delete_custom_port(), get_carrier_overrides(), get_custom_ports(), get_popular_ports_config(), search_port() (+4 more)

### Community 51 - "CurrencyManager"
Cohesion: 0.23
Nodes (7): convert_currency_to_usd(), CurrencyManager, get_all_exchange_rates(), Any, Currency Exchange Rate Service — manages currency conversions and custom…, update_exchange_rate(), threading

### Community 52 - "parse_msc_modal_charges"
Cohesion: 0.24
Nodes (8): parse_msc_modal_charges(), Parses charges from MSC BreakdownModal text. Correctly includes charges whose…, Test MSC charges parsing for Singapore to Conakry, Guinea (40GP). Charges with…, Test when only some surcharges have the payment condition., test_msc_charges_mixed_conditions(), test_msc_charges_singapore_to_conakry_guinea(), Verify MSC charge extraction logic parses Panama Canal Surcharge properly., test_msc_charge_extraction_logic()

### Community 53 - "test_one_premium_override.py"
Cohesion: 0.40
Nodes (3): MockCard, Unit test for ONE connector and charge classifier Premium Cargo Service…, test_premium_cargo_service_override()

### Community 54 - "🚢 Infreight Sourcing & Ocean Rate Automation System"
Cohesion: 0.14
Nodes (13): 1. Multi-Carrier Automation Engine, 2. Intelligent Surcharge & Charge Classifier Engine (`charge_classifier.py`), 3. Container Comparison Matrix & Excel Export Engine, 🚢 Infreight Sourcing & Ocean Rate Automation System, 🌟 Key Capabilities, 📄 License & Confidentiality, Prerequisites, 🛠️ Project Structure (+5 more)

### Community 55 - "AdminUsers.tsx"
Cohesion: 0.20
Nodes (14): AdminUserRecord, AdminUsers(), AdminUsersProps, ago(), AuditEntry, Avatar(), Filter, initials() (+6 more)

### Community 56 - "[2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split"
Cohesion: 0.15
Nodes (13): G2 Stress Test: "Hi, Please book the below as per your quote ref INF-2026-0842:…, H1 Stress Test: Table with 2 distinct rows: Row 1: POL Singapore, POD Jakarta,…, test_g2_booking_confirmation_guardrail(), test_h1_table_deduplication_two_pairs(), [2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split, Booking Confirmation / Instructions Intercept Guardrail G2 (`rfq_agent.py` & `RfqInputSection.tsx`), Commercial Sales Desk Intelligence (`sales_notes`), Deterministic Port Alias Resolver (`ports_aliases.json`) (+5 more)

### Community 57 - "test_self_healing.py"
Cohesion: 0.17
Nodes (16): handle_chat_query(), _local_chatbot_fallback(), Intelligent responder for search status, carrier guidance, air/sea info, and…, Sends the chat message and history to native Gemini 2.5 Flash API. If Gemini…, detect_manual_action_required(), Scans the current Playwright page to see if a CAPTCHA, Cloudflare challenge,…, clean_selector_memory(), asyncio (+8 more)

### Community 58 - "🛠 Detailed Carrier Log"
Cohesion: 0.15
Nodes (12): 🛠 Detailed Carrier Log, 🟢 GreenX, 🟠 Hapag-Lloyd, Infreight Ocean Carrier Rate Automation — Development Log, 🚀 Key Highlights & Architectural Changes, 🔌 Local Laptop Deployment (Self-Hosted Worker), 🔵 Maersk, 💗 ONE (Ocean Network Express) (+4 more)

### Community 59 - "._fs_pair_and_select"
Cohesion: 0.33
Nodes (4): get_booking_start_date(), date, Applies the business rules and pairs FreightSmart prices with crawled…, OOCL — FreightSmart Price Quotes (E-Quote / E-Spot) Paired With Sailing Schedules

### Community 60 - "safe_step.py"
Cohesion: 0.18
Nodes (10): capture_failure_context(), Exception, Failure Detector — parses and structures error context from failed Playwright…, Assembles a standardized diagnostic dictionary containing all available details…, generate_report(), Repair Report — generates and saves diagnosis reports on Playwright selector…, Assembles a comprehensive repair report and writes it as JSON and Markdown…, Safe Step — Playwright action execution wrapper with manual intervention pause… (+2 more)

### Community 61 - ".search_quotes"
Cohesion: 0.17
Nodes (8): extract_locode_and_country(), prepare_maersk_query(), Extracts LOCODE and country name from text like 'CASABLANCA, MOROCCO (MACAS)'…, Maps standard container search codes (e.g. 'DRY 20', '20GP') to Maersk Spot…, Scores a Maersk autocomplete dropdown suggestion. NOTE: The nested/indented…, Fills an autocomplete field using the proven original element-level…, get_cached_carrier_port(), set_cached_carrier_port()

### Community 62 - "[2026-05-18 – 2026-05-19] — Railway Deployment & Docker"
Cohesion: 0.67
Nodes (3): [2026-05-18 – 2026-05-19] — Railway Deployment & Docker, Persistent Chrome Profiles on Railway Volume, Railway Deployment Setup

### Community 63 - "[2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup"
Cohesion: 0.22
Nodes (8): [2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup, Chromium Cache Auto-Cleanup (Railway Storage Bloat Prevention), CMA CGM — 30-Second Timeout on Sold Out Cards, CMA CGM — Free Time Regex Too Strict, CMA CGM — Routing Regex Not Matching "via LEKKI, LA, NG", Excel Export — Routing & Free Time Columns Always Empty, Excel Export — Sold Out Rows Not Showing, Maersk — Hardcoded Port Overrides

### Community 64 - "[2026-05-31] — Multi-Instance Support & Charge Classification"
Cohesion: 0.67
Nodes (3): [2026-05-31] — Multi-Instance Support & Charge Classification, Charge Classification Improvements, Multi-Instance Concurrent Searches

### Community 65 - "layout.tsx"
Cohesion: 0.22
Nodes (7): frontend_src_app_globals, instrumentSans, inter, metadata, viewport, ThemeProvider(), next-themes

### Community 66 - "GreenX — Surcharge Intake Fix (2026-06-30)"
Cohesion: 0.22
Nodes (8): Charges that must be taken into the final value (USD only), Files changed, Fix, GreenX — Surcharge Intake Fix (2026-06-30), Per-B/L charges (billed once per booking, added in full to *each* container type), Problem, Root cause, Verification

### Community 67 - "Admin Page & Port Prioritization Guide"
Cohesion: 0.25
Nodes (7): 1. Popular Ports (UN/LOCODEs), 2. Boosted Countries, Admin Page & Port Prioritization Guide, 🔒 How to Access the Admin Page, ⚙️ How to Use Port Prioritization, ⚡ Important Notes, 📝 Step-by-Step Example

### Community 68 - "._verify_price_owner_selected"
Cohesion: 0.25
Nodes (7): Verifies the "I am the price owner" radio is genuinely checked, piercing shadow…, [2026-07-03] — OOCL FreightSmart Autoclear, Hapag Price Leak & Redirect fixes, Maersk Cache Scoping, Dallas Overrides, Hapag-Lloyd — Price Leaks, Column Matching, and Redirect Recovery, Maersk — 0.0-USD / "Not Open" Card Flakiness (the "Quotes Found but Empty Excel" root causes), Maersk — Caching Scope & Selector Tuning, OOCL — FreightSmart Popup Dismissals & Input Lock Serialization, Ports — Hardcoded Dallas Override

### Community 69 - "orbit-card-stack.tsx"
Cohesion: 0.22
Nodes (13): HalftoneAvatar(), HalftoneAvatarProps, hashSeed(), pick(), clamp(), initialsFor(), laneLabel(), OrbitCardStack() (+5 more)

### Community 71 - "dependencies"
Cohesion: 0.15
Nodes (13): dependencies, class-variance-authority, clsx, exceljs, lucide-react, next, next-themes, @radix-ui/react-slot (+5 more)

### Community 72 - "deploy"
Cohesion: 0.25
Nodes (7): build, builder, deploy, restartPolicyMaxRetries, restartPolicyType, startCommand, $schema

### Community 73 - ".login"
Cohesion: 0.20
Nodes (6): _is_logged_in_url(), True once Maersk has moved past the login pages to a signed-in page., Types text character by character into a given locator or element handle with…, Clicks an element with pre-click and post-click human-like reaction pauses., Wait until the login page either redirects to a signed-in page or shows its…, test_logged_in_url()

### Community 74 - "time"
Cohesion: 0.27
Nodes (8): cleanup_old_debug_files(), Storage Cleanup Utility — automatically removes stale debug screenshots, HTML…, Deletes temporary debug screenshots (*.png), HTML dumps (*.html), and temporary…, Verify that cleanup_old_debug_files removes debug pngs/htmls older than N days…, test_storage_cleanup_deletes_old_files(), glob, tempfile, time

### Community 75 - "Summary of Changes — July 20, 2026"
Cohesion: 0.29
Nodes (6): 1. AI RFQ Front Door & Air Freight Support (Phase A), 2. Multi-Origin & Gappy List Parsing for Sea RFQs (Phase B), 3. Search Form Streamlining (Form Input Restrictions), 4. Native Gemini 2.5 Flash API & Chatbot Resiliency, 5. Verification & Test Suite, Summary of Changes — July 20, 2026

### Community 76 - "analytics_service.py"
Cohesion: 0.22
Nodes (10): compute_admin_analytics(), get_clean_lane_key(), normalize_lane_port(), Any, AsyncSession, Consolidated Analytics Service for Infreight Ocean Carrier Rate Automation.…, Normalize port string to cleanly aggregate naming variations., Returns (norm_origin, norm_dest, display_lane_key). (+2 more)

### Community 77 - "port_routes.py"
Cohesion: 0.29
Nodes (9): get_countries(), get_port(), get_suggestions(), get, Get list of countries for autocomplete dropdown., Get specific port details by UN/LOCODE., Get port suggestions for autocomplete., search() (+1 more)

### Community 78 - "resolve_port_alias"
Cohesion: 0.33
Nodes (6): _load_port_aliases_config(), Deterministically resolves a port string against ports_aliases.json and the…, resolve_port_alias(), Test that resolve_port_alias cleans 'City, Country' and parenthetical notes to…, test_resolve_city_country_format_to_clean_database_port_name(), Clean Search Dropdown Port Name Resolution (`rfq_agent.py` & `port_manager.py`)

### Community 79 - "test_brightdata.py"
Cohesion: 0.40
Nodes (5): get_title(), Script to test fetching CMA CGM pricing page using Bright Data Web Access HTTP…, test_brightdata_api(), urllib_error, urllib_request

### Community 80 - "tunnel_client.py"
Cohesion: 0.17
Nodes (11): ambiguous_python_import_b35980c0aa01, argparse, asyncio, Integration tests for authentication, legacy user password setup, pending…, test_full_auth_lifecycle(), httpx, pytest_asyncio, handle_request() (+3 more)

### Community 81 - "Design system — read before touching any UI"
Cohesion: 0.33
Nodes (5): Animation rules, Client-only preferences, Design system — read before touching any UI, This is NOT the Next.js you know, Use tokens, not raw colours

### Community 82 - "test_panama_canal_surcharge.py"
Cohesion: 0.10
Nodes (27): is_weight_surcharge_applicable(), Evaluates whether a weight-tier or overweight surcharge is applicable for the…, calculate_final_freight_value(), classify_and_organize_charges(), format_maersk_date(), normalize_quote(), Normalizer — calculates the final freight value and normalizes quote data.…, Takes raw charge line items and classifies them. Args: raw_charges: list of… (+19 more)

### Community 83 - "[2026-05-29 – 2026-05-30] — Hapag-Lloyd Full Integration"
Cohesion: 0.40
Nodes (5): [2026-05-29 – 2026-05-30] — Hapag-Lloyd Full Integration, Hapag-Lloyd — Dropdown Autocomplete Issues, Hapag-Lloyd — Live Connector Implementation, Hapag-Lloyd — Onboarding Modal Blocking Form Interaction, Hapag-Lloyd — Search Button Selector Failures

### Community 84 - "auth_service.py"
Cohesion: 0.08
Nodes (34): AuthSession, Stores hashed active session tokens., get_user_for_token(), hash_token(), AsyncSession, UUID, Authentication and security service for Infreight Sourcing. Implements the…, Validate user's display name. (+26 more)

### Community 85 - "get_me"
Cohesion: 0.67
Nodes (3): get_me(), get, Get profile of currently signed-in user.

### Community 86 - "excelExport.ts"
Cohesion: 0.13
Nodes (26): BatchProgressPanel(), BatchProgressPanelProps, cheapest(), Filter, lanePhase(), Phase, PHASE_STYLE, ResultsTable() (+18 more)

### Community 88 - "resolve_port_for_carrier"
Cohesion: 0.24
Nodes (9): Resolves input text (e.g. 'Belfast (GBBEL)' or 'GBBEL') to a tuple of…, resolve_msc_port(), Resolves input text to (location_name, locode, country_code, country_name)., resolve_oocl_port_info(), resolve_port_for_carrier(), Verify non-Maersk carriers get standard UN/LOCODE or default mappings., Verify that El Dekheila maps specifically to 'Alexandria Dekheila, Egypt' for…, test_el_dekheila_maersk_override() (+1 more)

### Community 89 - "[2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History"
Cohesion: 0.40
Nodes (5): [2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History, Admin User Search History & SGT GMT+8 Conversion (`AdminDashboard.tsx`), GreenX (Evergreen) Card Isolation & Surcharge Parsing (`greenx_connector.py`), Multi-Route Batch Execution Engine (`batch_engine.py`), OOCL FreightSmart 28-Day Calendar Expansion (`oocl_connector.py`)

### Community 90 - "devDependencies"
Cohesion: 0.22
Nodes (9): devDependencies, eslint, eslint-config-next, tailwindcss, @tailwindcss/postcss, @types/node, @types/react, @types/react-dom (+1 more)

### Community 91 - "[2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning"
Cohesion: 0.25
Nodes (6): [2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning, GreenX — "No Quotes" Reported While Quotes Visibly Loaded in VNC, Hapag-Lloyd — Configurable Pacing & Redundant-Wait Removal, Job Scheduler — Concurrency Default, Maersk — Regression: Other-Container-Type Sizes Went "Sold Out" in Multi-Container Searches, OOCL — Schedule Search Repeated Once Per Container Type

### Community 92 - "headed_login_maersk.py"
Cohesion: 0.29
Nodes (4): Interactive Headed Login Helper for Maersk. Opens real Chrome using the…, Interactive Headed Login Helper for ONE (Ocean Network Express). Opens Chrome…, patchright_async_api, shutil

### Community 93 - "[2026-06-03] — CMA CGM Routing & Free Time Extraction"
Cohesion: 0.50
Nodes (4): [2026-06-03] — CMA CGM Routing & Free Time Extraction, CMA CGM — Import Free Time from D&D Tab, CMA CGM — Routing Detection (Direct vs Transit), Maersk — Free Time Extraction from Card Text

### Community 94 - "get_port_by_code"
Cohesion: 0.32
Nodes (5): get_carrier_search_query(), get_port_by_code(), Resolves a port search text (e.g. 'Haiphong (VN HPH)', 'VN HPH', 'Hai Phong')…, Constructs the specific search query to type into carrier search boxes. If the…, test()

### Community 95 - "test_one_charge_override.py"
Cohesion: 0.40
Nodes (3): MockCard, Unit test for ONE connector charge classification override., test_emergency_surcharge_override()

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

### Community 100 - "sort_container_types"
Cohesion: 0.40
Nodes (4): Sort container types in standard order: DRY 20 (20GP) -> DRY 40 (40GP) -> DRY…, sort_container_types(), test_container_types_standard_ordering(), model_validator

### Community 101 - "[2026-05-20 – 2026-05-22] — Port Resolution & Frontend Improvements"
Cohesion: 0.50
Nodes (4): [2026-05-20 – 2026-05-22] — Port Resolution & Frontend Improvements, Excel Export — ETA Column & Container Type Header, Frontend Light Mode & CORS Fix, Port Resolution System

### Community 102 - "ai_repair_agent.py"
Cohesion: 0.33
Nodes (6): _local_fuzzy_repair(), AI Repair Agent — diagnoses Playwright step failures and suggests selector…, A local rule-based heuristic to locate reasonable buttons or inputs when Gemini…, Analyzes the failure context and DOM content to suggest a selector repair. Uses…, suggest_fix(), bs4

### Community 106 - ".search_quotes"
Cohesion: 0.29
Nodes (3): date, Type a LOCODE into the autocomplete field and click the first visible dropdown…, Find quantity input next to or below label_text and fill it.

### Community 117 - "[2026-05-23 – 2026-05-24] — Maersk Shadow DOM & Stealth Upgrades"
Cohesion: 0.50
Nodes (4): [2026-05-23 – 2026-05-24] — Maersk Shadow DOM & Stealth Upgrades, Maersk — 2FA/CAPTCHA Human-in-the-Loop via noVNC, Maersk — Login Credential Autofill Corruption, Maersk — Shadow DOM Piercing for MDS Web Components

### Community 119 - "[2026-06-01] — Hapag-Lloyd Sold Out Detection & Date Parsing"
Cohesion: 0.67
Nodes (3): [2026-06-01] — Hapag-Lloyd Sold Out Detection & Date Parsing, Hapag-Lloyd — Date String Standardization, Hapag-Lloyd — Sold Out Schedule Detection

### Community 121 - "[2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash"
Cohesion: 0.40
Nodes (5): [2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash, AI RFQ Front Door & Air Freight Support, Multi-Origin & Gappy List Parsing (Sea RFQs), Native Gemini 2.5 Flash Direct API Integration, Search Form Streamlining

### Community 122 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, dev, lint, start

### Community 123 - "diagnose_greenx_dropdown.py"
Cohesion: 0.67
Nodes (3): dump_options(), main(), Diagnostic: dump ALL dropdown options (text + innerHTML) when typing 'DEHAM'…

### Community 124 - "[2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes"
Cohesion: 0.50
Nodes (4): [2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes, CMA CGM — Chrome Profile Bypass, ONE — Date Formatting & Charge Breakdown Pollution, ONE — Date Picker Pre-selection Issue

### Community 125 - "eslint.config.mjs"
Cohesion: 0.50
Nodes (3): eslintConfig, eslint, eslint-config-next

### Community 126 - "MaerskConnector"
Cohesion: 0.09
Nodes (21): MaerskConnector, Maersk Browser Connector — Playwright automation using your real Google Chrome…, # NOTE: Bright Data Web Unlocker proxies break Playwright browser sessions…, Extracts the port/city name by removing any UN/LOCODE parentheses (e.g.,…, main(), Inspection script to dump the Maersk autocomplete dropdown structure., main(), Test script to run Belawan (IDBLW) -> Aden (YEADE) route on Maersk and MSC. (+13 more)

### Community 129 - "[2026-06-02] — Hapag-Lloyd Transshipment & Duplicate Fix"
Cohesion: 0.67
Nodes (3): [2026-06-02] — Hapag-Lloyd Transshipment & Duplicate Fix, Hapag-Lloyd — Duplicate Sailings from Transshipment Vessels, Hapag-Lloyd — Routing Not Marked as Transit

## Knowledge Gaps
- **312 isolated node(s):** `Config`, `install_pi.sh script`, `eslintConfig`, `nextConfig`, `name` (+307 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 920 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **25 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Changelog` connect `Changelog` to `[2026-06-02] — Hapag-Lloyd Transshipment & Duplicate Fix`, `._fs_dismiss_modals`, `test_hapag_freetime.py`, `[2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split`, `[2026-05-18 – 2026-05-19] — Railway Deployment & Docker`, `[2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup`, `[2026-05-31] — Multi-Instance Support & Charge Classification`, `._verify_price_owner_selected`, `[2026-05-29 – 2026-05-30] — Hapag-Lloyd Full Integration`, `[2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History`, `[2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning`, `[2026-06-03] — CMA CGM Routing & Free Time Extraction`, `[2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control`, `._save_carrier_overrides`, `[2026-05-20 – 2026-05-22] — Port Resolution & Frontend Improvements`, `[2026-05-23 – 2026-05-24] — Maersk Shadow DOM & Stealth Upgrades`, `[2026-06-01] — Hapag-Lloyd Sold Out Detection & Date Parsing`, `[2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash`, `[2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes`?**
  _High betweenness centrality (0.346) - this node is a cross-community bridge._
- **Why does `[2026-06-03] — CMA CGM Routing & Free Time Extraction` connect `[2026-06-03] — CMA CGM Routing & Free Time Extraction` to `Changelog`?**
  _High betweenness centrality (0.319) - this node is a cross-community bridge._
- **Why does `Maersk — Free Time Extraction from Card Text` connect `[2026-06-03] — CMA CGM Routing & Free Time Extraction` to `excelExport.ts`?**
  _High betweenness centrality (0.318) - this node is a cross-community bridge._
- **Are the 32 inferred relationships involving `RateSearchRequest` (e.g. with `create_batch_rate_search()` and `create_rate_search()`) actually correct?**
  _`RateSearchRequest` has 32 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `cn()` (e.g. with `Reuse the primitives` and `7. Conventions to follow from here`) actually correct?**
  _`cn()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 21 inferred relationships involving `CarrierResultStatus` (e.g. with `safe_step()` and `update_carrier_status()`) actually correct?**
  _`CarrierResultStatus` has 21 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Config`, `install_pi.sh script`, `eslintConfig` to the rest of the system?**
  _312 weakly-connected nodes found - possible documentation gaps or missing edges._