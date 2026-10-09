# Graph Report - Infreight_Sourcing_New  (2026-10-09)

## Corpus Check
- 277 files · ~1,184,705 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 26 file(s) not represented in the graph (top: (none) 10, .bat 8, .conf 2)

## Summary
- 2461 nodes · 6056 edges · 149 communities (123 shown, 26 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 347 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `87a56c02`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- port_manager.py
- BaseCarrierConnector
- cn
- user_routes.py
- auth_routes.py
- browser_cleanup.py
- app/page.tsx
- api.ts
- PortManager
- AdminUsers.tsx
- CMAConnector
- hapag_lloyd_connector.py
- job_service.py
- carrier_sessions.py
- RateSearchRequest
- HapagLloydAPIConnector
- preferences.ts
- test_rfq_agent.py
- OOCLConnector
- SocialWidget.tsx
- lucide-react
- GreenXConnector
- list_colleagues
- port_routes.py
- auth_service.py
- rate_search_routes.py
- msc_connector.py
- parse_rfq
- types.ts
- ai_agent.py
- CarrierSearchResult
- ONEConnector
- _Page
- Engineering Report: Sourcing Portal Enhancements & Scraping Pipeline Stability
- Changelog
- AdminOverview.tsx
- package.json
- dependencies
- RateResults.tsx
- SearchQueueManager
- ChargeCategory
- Frontend Redesign — Componentry Design System, Workspace & Launch Intro (2026-09-07)
- compilerOptions
- ._fs_dismiss_modals
- test_carrier_timeout.py
- devDependencies
- .run_full_search
- 👥 The 5 Agent Roles
- HapagLloydConnector
- CarrierResultStatus
- json
- CurrencyManager
- MockCard
- test_hapag_freetime.py
- 🚢 Infreight Sourcing & Ocean Rate Automation System
- MaerskConnector
- [2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split
- ._parse_offer_response_to_quotes
- 🛠 Detailed Carrier Log
- post
- re
- .extract_charge_breakdown
- [2026-06-30] — ONE Multi-Container & Sold-Out, GreenX Surcharge Intake, Free-Time Fixes, Maersk Diagnosis
- [2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup
- get_clean_lane_key
- time
- GreenX — Surcharge Intake Fix (2026-06-30)
- Admin Page & Port Prioritization Guide
- [2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning
- test_self_healing.py
- sort_container_types
- carrier_switches.py
- deploy
- .search_quotes
- test_browser_cleanup.py
- Summary of Changes — July 20, 2026
- _detect_port_mismatch
- [2026-05-29 – 2026-05-30] — Hapag-Lloyd Full Integration
- resolve_port_alias
- test_brightdata.py
- MockCard
- Design system — read before touching any UI
- tunnel_client.py
- layout.tsx
- ._fs_pair_and_select
- .login
- parse_msc_modal_charges
- RateLimiter
- os
- registry.py
- test_el_dekheila_maersk.py
- test_excel_exports.js
- ._mouse_glide_to
- [2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History
- Scraper Robustness Review — July 2026
- scripts
- frontend/README.md
- pytest
- [2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control
- .validate_currency
- ._fs_extract_rows
- chat_service.py
- [2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash
- websockify_carrier_proxy
- Working in this repository
- [2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes
- install_pi.sh
- models/__init__.py
- postcss.config.mjs
- ._fetch_all_container_types
- [2026-05-23 – 2026-05-24] — Maersk Shadow DOM & Stealth Upgrades
- ._query_prices_api
- test_port_fixes.py
- Architecture Overview
- .run_full_search
- [2026-05-31] — Multi-Instance Support & Charge Classification
- ._fs_iterate_calendar_dates
- [2026-06-02] — Hapag-Lloyd Transshipment & Duplicate Fix
- create_batch_rate_search
- ._parse_free_time_text
- test_auth_routes.py
- .search_port
- [2026-08-04 - 2026-08-06] — CMA CGM Dynamic RAMP/POD Rerouting, Brand Excel Styling, Port Synonym Matching & Tunnel Relays
- test_one_breakdown.py
- b381f2acc5c6_add_port_observability_columns.py
- test_one_premium_override.py
- Infreight Sourcing Automation — Run Audit (30 Jul 2026)
- ._fs_parse_card
- [2026-07-03] — Robustness Review & Multi-Port Quick Search Fixes
- _dismiss_once
- test_one_breakdown_parsing
- test_js.js
- parse_rfq_endpoint
- fill_container_card
- _user_overrides_path
- test_oocl_normalize_result_with_pcs
- clean_selector_memory
- [2026-05-18 – 2026-05-19] — Railway Deployment & Docker
- e2e_downloaded_multisheet_28ec47f9.md
- e2e_downloaded_tariff_d21a0cb7.md
- ambiguous_python_import_b35980c0aa01

## God Nodes (most connected - your core abstractions)
1. `RateSearchRequest` - 165 edges
2. `cn()` - 89 edges
3. `CarrierResultStatus` - 70 edges
4. `QuoteSchema` - 69 edges
5. `User` - 62 edges
6. `CMAConnector` - 58 edges
7. `PortManager` - 58 edges
8. `HapagLloydConnector` - 56 edges
9. `MaerskConnector` - 52 edges
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

## Communities (149 total, 26 thin omitted)

### Community 0 - "port_manager.py"
Cohesion: 0.31
Nodes (9): add_carrier_override(), delete_carrier_override(), get_carrier_overrides(), get_popular_ports_config(), Suggest top N ports for a partial query., search_port(), update_popular_ports_config(), test_dynamic_boosting() (+1 more)

### Community 1 - "BaseCarrierConnector"
Cohesion: 0.06
Nodes (26): BaseCarrierConnector, NotAvailableConnector, Any, Open the price breakdown / detail view for a specific quote. Args: quote_ref:…, Extract individual charge line items from the price breakdown. Returns: List of…, Abstract base class for carrier portal connectors., Detects if a CAPTCHA, Turnstile, hCaptcha, reCAPTCHA, or 2FA screen is…, Clean up browser resources robustly, ensuring failures or hangs never block… (+18 more)

### Community 2 - "cn"
Cohesion: 0.07
Nodes (49): Reuse the primitives, New primitives — `frontend/src/components/ui/`, LoadingState(), LoginModalProps, PortAutocompleteProps, SearchCompletionModalProps, Badge(), badgeVariants (+41 more)

### Community 3 - "user_routes.py"
Cohesion: 0.07
Nodes (82): admin_delete_user(), AdminLoginRequest, approve_user(), CarrierOverrideRequest, CarrierSwitchRequest, Config, create_custom_port_endpoint(), CustomPortRequest (+74 more)

### Community 4 - "auth_routes.py"
Cohesion: 0.08
Nodes (47): clear_session_cookie(), get_current_user(), get_current_user_optional(), get_me(), login(), LoginRequest, logout(), AsyncSession (+39 more)

### Community 5 - "browser_cleanup.py"
Cohesion: 0.22
Nodes (19): _is_chrome(), _is_playwright_driver(), _kill(), kill_profile_browsers(), _proc_supported(), Cleanup for Chrome browsers and temporary profiles that a failed close leaves…, Kill every automated Chrome and Playwright driver. Only call this when no…, pid -> (ppid, argv) for every readable process. (+11 more)

### Community 6 - "app/page.tsx"
Cohesion: 0.14
Nodes (26): 6. Known limitations / candidate follow-ups, HomeContent(), BackendConfigModal(), BackendConfigModalProps, SearchCompletionModal(), SearchHistoryModal(), RepairReport, SelfHealingAlerts() (+18 more)

### Community 7 - "api.ts"
Cohesion: 0.07
Nodes (64): AdminDashboard(), UserRecord, LoginContent(), AdminCarriers(), PROFILE_NAMES, when(), AdminPortFixes(), AdminPortFixesProps (+56 more)

### Community 8 - "PortManager"
Cohesion: 0.12
Nodes (6): PortManager, Retrieve verified carrier port name from persistent cache by UN/LOCODE,…, Cache verified carrier port name and save persistently to…, Clean and normalize user input for port searching., Retrieve port data by full UN/LOCODE (e.g., 'SGSIN')., Dynamic Carrier Port Overrides & Admin Registry (`PortManager`, `AdminDashboard.tsx`)

### Community 9 - "AdminUsers.tsx"
Cohesion: 0.11
Nodes (25): AdminUserRecord, AdminUsers(), AdminUsersProps, ago(), AuditEntry, Avatar(), Filter, initials() (+17 more)

### Community 10 - "CMAConnector"
Cohesion: 0.07
Nodes (19): CMAConnector, Ensures 'Ramp' is explicitly selected under 'Type of location' toggle buttons…, Scans for Route, POL (Port of Loading), or POD (Port of Discharge) dropdown…, Clears the currently selected Destination port tag/card, re-types the locode,…, Dynamically extracts any recommended 5-letter POD LOCODE mentioned in the…, Detects if CMA CGM displayed an advisory banner message: "Looking for AEJEA or…, Handles the 'Customer account' -> 'Role (you are acting as)' dropdown on CMA…, Repeatedly clicks 'More results' if visible to load ALL quotes on the page. (+11 more)

### Community 11 - "hapag_lloyd_connector.py"
Cohesion: 0.08
Nodes (38): ABC, Base Carrier Connector — abstract base class for all carrier connectors. Each…, Normalize CMA CGM data into QuoteSchema. Rule: include BASIC_OCEAN_FREIGHT and…, Hapag-Lloyd Prices API Connector (REST API v2.1.4). Provides real-time rate…, # NOTE: No start date fill needed — schedule page defaults to today,, Hapag-Lloyd Live Connector -- Playwright automation. Credentials read from env:…, ONE (Ocean Network Express) Live Connector — Playwright automation. Credentials…, # TODO: Verify selectors against ONE ecommerce portal (+30 more)

### Community 12 - "job_service.py"
Cohesion: 0.14
Nodes (25): close_all_active_connectors(), Force close all active carrier connectors and their Playwright Chrome windows., get_async_session_maker(), Get the session maker for use outside of FastAPI dependency injection., SearchStatus, cancel_all_active_searches(), cleanup_browsers_if_idle(), UUID (+17 more)

### Community 13 - "carrier_sessions.py"
Cohesion: 0.20
Nodes (15): clean_storage_state(), delete_session(), load_session(), _on_domain(), _path(), Saved carrier logins uploaded by an admin. An admin logs in to a carrier in…, What the admin screen shows: who uploaded it, when, and how much it holds., Keep only this carrier's cookies and localStorage, in the shape add_cookies… (+7 more)

### Community 14 - "RateSearchRequest"
Cohesion: 0.07
Nodes (28): RateSearchRequest, CMA CGM end-to-end test — login + search + extract quotes., # IMPORTANT: Clear ALL proxy env vars BEFORE any import triggers load_dotenv()…, test_cma(), run_test(), run_test(), test_montreal_ramp(), Test multi-container search and caching for Hapag-Lloyd connector. (+20 more)

### Community 15 - "HapagLloydAPIConnector"
Cohesion: 0.15
Nodes (8): HapagLloydAPIConnector, Direct REST API connector for Hapag-Lloyd Prices API v2.1.4., API connectors do not require browser login sessions., No browser session to reset between batch routes., main(), test_locode_resolution(), test_payload_generation(), test_response_parsing_and_normalization()

### Community 16 - "preferences.ts"
Cohesion: 0.09
Nodes (34): LaunchIntro(), SearchHistoryItem, derive(), Derived, startOfDay(), UsageStats(), ChoiceCard(), Toggle() (+26 more)

### Community 17 - "test_rfq_agent.py"
Cohesion: 0.10
Nodes (36): API routes for RFQ parsing agent., RFQParseResult, asyncio, Unit tests for the Gemini AI RFQ Agent service (parse_rfq). Includes…, Test Image 2: Air rate request generates 3 drafts to Glenn (AWOT), Jing Hui…, Test Image 4: Steel Plate ex Pasir Gudang / Tanjung Pelepas for 20' & 40'., Test Guardrail: Detects Reefer container request and returns unsupported_cargo…, Test Guardrail: Detects LCL request. (+28 more)

### Community 18 - "OOCLConnector"
Cohesion: 0.22
Nodes (8): OOCLConnector, Attempts to automatically click the Cloudflare Turnstile 'Verify you are human'…, asyncio, test_oocl_cwx_different_port_pair_different_amount(), test_oocl_cwx_heavy_weight_charge_not_applied_40gp(), test_oocl_cwx_heavy_weight_charge_not_applied_under_threshold(), test_oocl_cwx_port_pair_surabaya_karachi(), test_oocl_cwx_port_pair_without_cwx()

### Community 19 - "SocialWidget.tsx"
Cohesion: 0.06
Nodes (49): ACCENT_COLORS, errorMessage(), relativeTime(), resizeImageToDataUrl(), SocialWidget(), SocialWidgetProps, applyMaskInversion(), buildRoundedMask() (+41 more)

### Community 20 - "lucide-react"
Cohesion: 0.06
Nodes (40): AppHeader(), AppHeaderProps, initials(), systemStatus(), ChatWidget(), ChatWidgetProps, Message, ACTION_STATUSES (+32 more)

### Community 21 - "GreenXConnector"
Cohesion: 0.09
Nodes (14): GreenXConnector, date, Overrides base search runner to query all 3 sizes at once and cache the…, Type a LOCODE into the autocomplete field and click the first visible dropdown…, Find quantity input next to or below label_text and fill it., Find the exact individual quote card container row encompassing dates, rates,…, Dismiss any cookie/alert modal that would intercept pointer events., Splits a single raw multi-container quote card into multiple QuoteSchema… (+6 more)

### Community 22 - "list_colleagues"
Cohesion: 0.11
Nodes (23): get_conversation(), list_colleagues(), poke_colleague(), PokeRequest, AsyncSession, BaseModel, delete, get (+15 more)

### Community 23 - "port_routes.py"
Cohesion: 0.16
Nodes (14): get_countries(), get_port(), get_suggestions(), get, Get list of countries for autocomplete dropdown., Get specific port details by UN/LOCODE., Get port suggestions for autocomplete., search() (+6 more)

### Community 24 - "auth_service.py"
Cohesion: 0.05
Nodes (58): api_route, health(), lifespan(), get, Infreight Ocean Carrier Rate Automation — FastAPI Application. Main entry point…, Check if the VNC viewer is available (production only, where Xvfb runs)., Startup and shutdown events., vnc_status() (+50 more)

### Community 25 - "rate_search_routes.py"
Cohesion: 0.09
Nodes (35): carrier_switch_status(), create_rate_search(), get_admin_analytics_endpoint(), get_batch_search_status(), get_rate_search(), get_repair_reports(), get_user_search_history(), AsyncSession (+27 more)

### Community 26 - "msc_connector.py"
Cohesion: 0.13
Nodes (13): format_to_iso_date(), MSCConnector, Resolves input text (e.g. 'Belfast (GBBEL)' or 'GBBEL') to a tuple of…, Playwright-based automation for MSC (Mediterranean Shipping Company)., Handles the MSC login flow., Clicks Instant Quote, fills form, clicks Search., Detects and clicks the 'Ramp' delivery/haulage option if MSC displays Ramp /…, Parse '14 Jun 2026' to 'YYYY-MM-DD (+5 more)

### Community 27 - "parse_rfq"
Cohesion: 0.13
Nodes (25): _call_native_gemini_api(), _detect_booking_confirmation(), _detect_dual_mode_enquiry(), _detect_mode_by_hierarchy(), _detect_unsupported_cargo(), _extract_20gp_weight_priority(), generate_dual_air_drafts(), _load_airport_aliases_config() (+17 more)

### Community 28 - "types.ts"
Cohesion: 0.10
Nodes (36): 0. The one invariant, CarrierMultiSelect(), CarrierMultiSelectProps, isAllCarriers(), toggleAllCarriers(), toggleCarrierSelection(), PortAutocomplete(), RateSearchForm() (+28 more)

### Community 29 - "ai_agent.py"
Cohesion: 0.10
Nodes (20): AIBrowserAgent, AI Browser Agent — Vision-based browser automation using Gemini Flash. This…, Capture the current page as a PNG screenshot., Build the prompt with task description and action history., Parse Gemini's response into an action dict., Call Gemini API with exponential backoff retry., Execute a parsed action on the browser page., Detect if the agent is stuck repeating the same action. (+12 more)

### Community 30 - "CarrierSearchResult"
Cohesion: 0.08
Nodes (55): get_sync_url(), run_migrations_offline(), run_migrations_online(), get_route_health(), Get carrier search reliability & route health matrix across origin-destination…, Base, _create_sqlite_engine(), _get_database_url() (+47 more)

### Community 31 - "ONEConnector"
Cohesion: 0.14
Nodes (5): ONEConnector, date, Splits a single raw multi-container quote card into multiple QuoteSchema…, Tries to click a matching option from ONE's visible dropdown. Returns True only…, Extracts 5-letter UN/LOCODE from strings like 'Singapore [SGSIN]' or 'Singapore…

### Community 32 - "_Page"
Cohesion: 0.15
Nodes (8): _connector(), _Locator, _Page, Maersk's login page redirects to the Hub a few seconds after loading when the…, Sits on /portaluser/login, then redirects after `redirect_after` URL reads., test_login_uses_saved_session_after_late_redirect(), test_wait_detects_late_redirect(), test_wait_detects_login_form()

### Community 33 - "Engineering Report: Sourcing Portal Enhancements & Scraping Pipeline Stability"
Cohesion: 0.08
Nodes (23): 1. Anti-Bot Mitigation & CAPTCHA Human-in-the-Loop Recovery, 2. Sourcing Parallelization & Surcharges Optimization, 3. Autocomplete Intelligence & Location Mapping, 4. Scraper Pipeline Maintenance, 5. Infrastructure & DevSecOps Enhancements, Business Value, Business Value, Business Value (+15 more)

### Community 34 - "Changelog"
Cohesion: 0.10
Nodes (19): [2026-05-20 – 2026-05-22] — Port Resolution & Frontend Improvements, [2026-05-25 – 2026-05-26] — VNC Display Isolation & Proxy Integration, [2026-06-01] — Hapag-Lloyd Sold Out Detection & Date Parsing, [2026-06-03] — CMA CGM Routing & Free Time Extraction, [2026-07-08] — OOCL E-Quote Calendar Navigation, cheapest E-Spot selection, and E-Quote/E-Spot isolation refinements, [2026-07-09] — Hapag-Lloyd Quick Quotes pairing and selection simplification, Bright Data ISP Proxy Integration, Changelog (+11 more)

### Community 35 - "AdminOverview.tsx"
Cohesion: 0.10
Nodes (24): AdminAnalytics, AdminOverview(), AdminOverviewProps, AdminOverviewUser, AnalyticsRange, Attention, attentionItems(), CARRIER_LABELS (+16 more)

### Community 36 - "package.json"
Cohesion: 0.09
Nodes (20): eslintConfig, nextConfig, engines, node, name, packageManager, private, version (+12 more)

### Community 37 - "dependencies"
Cohesion: 0.15
Nodes (13): dependencies, class-variance-authority, clsx, exceljs, lucide-react, next, next-themes, @radix-ui/react-slot (+5 more)

### Community 38 - "RateResults.tsx"
Cohesion: 0.09
Nodes (43): LiveSearchProgressProps, QuoteBreakdownDrawer(), QuoteBreakdownDrawerProps, Breakdown(), ChargeList(), dateValue(), freeTimeText(), isSoldOut() (+35 more)

### Community 39 - "SearchQueueManager"
Cohesion: 0.12
Nodes (11): Lock, Marks a search as completed internally so we can track the auto-release timeout., Called periodically in a background task to check if the user has held the lock…, Forcefully clears all queued searches and the active lock. Useful for…, Returns or creates an asyncio.Lock for a specific carrier code to prevent…, Adds a search to the queue and waits until it becomes the active search. Event-…, Singleton manager to enforce a FIFO queue for rate searches. Since web scraping…, Returns the current position of the search in the queue. 0 means it is the… (+3 more)

### Community 40 - "ChargeCategory"
Cohesion: 0.24
Nodes (19): ChargeCategory, classify_charge(), Classify a charge line item based on its name, amount, section heading, and…, Tests for charge classifier., test_basic_ocean_freight(), test_cwx_heavy_weight_charge(), test_destination_charges(), test_discount() (+11 more)

### Community 41 - "Frontend Redesign — Componentry Design System, Workspace & Launch Intro (2026-09-07)"
Cohesion: 0.14
Nodes (13): 1. Design system foundation (`082b43a`), 2. Bugs found and fixed during the restyle, 3. Workspace + launch intro (`21ade75`), 4. Follow-up fixes (`2f9d92b`), 5. Verification, 7. Conventions to follow from here, Dependencies added (5, all small, no runtime lib dependency on Componentry), Frontend Redesign — Componentry Design System, Workspace & Launch Intro (2026-09-07) (+5 more)

### Community 42 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 43 - "._fs_dismiss_modals"
Cohesion: 0.17
Nodes (8): Lock, Full FreightSmart phase: login â†’ fill quote form â†’ search â†’ extract rows., Runs CONCURRENTLY with the rest of the FreightSmart form-filling flow and…, Closes FreightSmart popups. Order matters: 1. Cookie Notice consent ("Accept…, Two-step FreightSmart login: 1. freightsmart.oocl.com/app/login â€” email +…, Fills the origin/destination 'Enter Port or Door Point' autocomplete. The…, Opens the 'Container Type and Quantity' picker (General tab: 20GP/20RF(NOR),…, Event

### Community 44 - "test_carrier_timeout.py"
Cohesion: 0.19
Nodes (10): CrashingConnector, HangingConnector, asyncio, A carrier whose browser hangs must be stopped after CARRIER_SEARCH_TIMEOUT_SEC…, Hangs on the sizes in `hang_on`; answers NO_QUOTES_AVAILABLE for the rest., Like a real connector whose tab dies: reports a crash, then never returns., _run(), test_crashed_tab_stops_the_carrier_without_waiting_for_the_timeout() (+2 more)

### Community 45 - "devDependencies"
Cohesion: 0.22
Nodes (9): devDependencies, eslint, eslint-config-next, tailwindcss, @tailwindcss/postcss, @types/node, @types/react, @types/react-dom (+1 more)

### Community 46 - ".run_full_search"
Cohesion: 0.14
Nodes (6): flatten_tree(), Execute the full search flow with Progressive Lazy Loading: 1. Login 2. Search…, Extracts freetime, demurrage, and detention from the 'Import D&D fees' tab…, Extracts the routing details from the 'Route & other details' accordion.…, Replace `master_dir` with a copy of `source_dir` (caches and lock files left…, replace_master_profile()

### Community 47 - "👥 The 5 Agent Roles"
Cohesion: 0.13
Nodes (14): 1. Intake Agent (Email Listener), 2. Sourcing Orchestrator (The Coordinator), 3. Sourcing & Scraping Agent (Rates Engine), 4. Finance & Costing Agent (Excel Compiler), 5. Email Draft Agent (Communicator), 📋 Executive Summary, 🛠️ Implementation Stages, Phase 1: Email Integration (Week 1-2) (+6 more)

### Community 48 - "HapagLloydConnector"
Cohesion: 0.06
Nodes (35): HapagLloydConnector, HapagServiceUnavailableException, Exception, Normalize various date formats (e.g. 2026-05-31, 31.05.2026, 31 May 2026, 31…, Robustly selects options from Hapag-Lloyd custom dropdown lists. Types the…, Detects the Microsoft B2C identity/OAuth login page. Hapag can silently bounce…, Guards against the session-expiry-mid-crawl failure mode: the existing redirect…, Crawls Hapag-Lloyd sailing schedules from the Schedule tab. (+27 more)

### Community 49 - "CarrierResultStatus"
Cohesion: 0.06
Nodes (22): Normalize extracted data into a QuoteSchema using the normalizer. Args:…, Override to immediately return CONNECTOR_NOT_AVAILABLE., Fill in the carrier's search form and submit a quote search. Args: request: The…, Splits a single raw multi-container quote card into multiple QuoteSchema…, _generate_maersk_mock_quotes(), _generate_msc_mock_quotes(), _generate_one_mock_quotes(), MockCarrierConnector (+14 more)

### Community 50 - "json"
Cohesion: 0.19
Nodes (10): _local_fuzzy_repair(), AI Repair Agent — diagnoses Playwright step failures and suggests selector…, A local rule-based heuristic to locate reasonable buttons or inputs when Gemini…, Repair Report — generates and saves diagnosis reports on Playwright selector…, _logged_in(), main(), _on_login_page(), Save a Maersk login from your own PC for the server to use. Opens real Google… (+2 more)

### Community 51 - "CurrencyManager"
Cohesion: 0.26
Nodes (6): convert_currency_to_usd(), CurrencyManager, get_all_exchange_rates(), Any, Currency Exchange Rate Service — manages currency conversions and custom…, update_exchange_rate()

### Community 53 - "test_hapag_freetime.py"
Cohesion: 0.14
Nodes (17): Looks up standard destination demurrage/detention free time days., (days, estimated): estimated when the destination has no entry in the free time…, _apply_freetime_to_quote(), freetime_days(), match_freetime_entry(), Any, Destination free time from config/hapag_freetime.json, shared by the Hapag-…, Days for this container from a table entry ({"20GP": n, "40GP": n} or a bare… (+9 more)

### Community 54 - "🚢 Infreight Sourcing & Ocean Rate Automation System"
Cohesion: 0.14
Nodes (13): 1. Multi-Carrier Automation Engine, 2. Intelligent Surcharge & Charge Classifier Engine (`charge_classifier.py`), 3. Container Comparison Matrix & Excel Export Engine, 🚢 Infreight Sourcing & Ocean Rate Automation System, 🌟 Key Capabilities, 📄 License & Confidentiality, Prerequisites, 🛠️ Project Structure (+5 more)

### Community 55 - "MaerskConnector"
Cohesion: 0.08
Nodes (22): MaerskConnector, Maersk Browser Connector — Playwright automation using your real Google Chrome…, # NOTE: Bright Data Web Unlocker proxies break Playwright browser sessions…, Extracts the port/city name by removing any UN/LOCODE parentheses (e.g.,…, main(), Inspection script to dump the Maersk autocomplete dropdown structure., main(), Test script to run Belawan (IDBLW) -> Aden (YEADE) route on Maersk and MSC. (+14 more)

### Community 56 - "[2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split"
Cohesion: 0.15
Nodes (13): G2 Stress Test: "Hi, Please book the below as per your quote ref INF-2026-0842:…, H1 Stress Test: Table with 2 distinct rows: Row 1: POL Singapore, POD Jakarta,…, test_g2_booking_confirmation_guardrail(), test_h1_table_deduplication_two_pairs(), [2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split, Booking Confirmation / Instructions Intercept Guardrail G2 (`rfq_agent.py` & `RfqInputSection.tsx`), Commercial Sales Desk Intelligence (`sales_notes`), Deterministic Port Alias Resolver (`ports_aliases.json`) (+5 more)

### Community 57 - "._parse_offer_response_to_quotes"
Cohesion: 0.21
Nodes (5): Any, Maps a Prices API rate onto the categories the portal scraper produces (freight…, Leg locations are UnLocation/Facility objects per the spec; tolerate plain…, Renders a graduated weight tier (e.g. Heavy Lift: 18-99 TON) in the portal's…, Parses Hapag-Lloyd OfferResponse JSON into InFreight QuoteSchema objects.

### Community 58 - "🛠 Detailed Carrier Log"
Cohesion: 0.15
Nodes (12): 🛠 Detailed Carrier Log, 🟢 GreenX, 🟠 Hapag-Lloyd, Infreight Ocean Carrier Rate Automation — Development Log, 🚀 Key Highlights & Architectural Changes, 🔌 Local Laptop Deployment (Self-Hosted Worker), 🔵 Maersk, 💗 ONE (Ocean Network Express) (+4 more)

### Community 59 - "post"
Cohesion: 0.18
Nodes (13): approve_repair(), ApproveRepairRequest, chat_endpoint(), ChatRequest, force_stop_searches(), BaseModel, post, Chatbot helper endpoint powered by Gemini API. (+5 more)

### Community 60 - "re"
Cohesion: 0.10
Nodes (4): check_and_wait_for_captcha(), login(), main(), re

### Community 62 - "[2026-06-30] — ONE Multi-Container & Sold-Out, GreenX Surcharge Intake, Free-Time Fixes, Maersk Diagnosis"
Cohesion: 0.29
Nodes (7): [2026-06-30] — ONE Multi-Container & Sold-Out, GreenX Surcharge Intake, Free-Time Fixes, Maersk Diagnosis, GreenX — Only Basic Ocean Freight & LSS Folded Into Final Value, MAERSK — "Quotes Found" but Empty Excel (Diagnosis), ONE — All-Container-Type Search Returning 0 Quotes, ONE — Multi-Container Breakdown Triple-Counted / Inflated Final Value, ONE — Sold-Out ("Notify Me") Sailings Appearing as Quotes, Performance/Reliability — Stop Copying Chrome Caches During Profile Clone/Sync

### Community 63 - "[2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup"
Cohesion: 0.22
Nodes (8): [2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup, Chromium Cache Auto-Cleanup (Railway Storage Bloat Prevention), CMA CGM — 30-Second Timeout on Sold Out Cards, CMA CGM — Free Time Regex Too Strict, CMA CGM — Routing Regex Not Matching "via LEKKI, LA, NG", Excel Export — Routing & Free Time Columns Always Empty, Excel Export — Sold Out Rows Not Showing, Maersk — Hardcoded Port Overrides

### Community 64 - "get_clean_lane_key"
Cohesion: 0.50
Nodes (4): get_clean_lane_key(), normalize_lane_port(), Normalize port string to cleanly aggregate naming variations., Returns (norm_origin, norm_dest, display_lane_key).

### Community 65 - "time"
Cohesion: 0.13
Nodes (9): Interactive Headed Login Helper for Maersk. Opens real Chrome using the…, Interactive Headed Login Helper for ONE (Ocean Network Express). Opens Chrome…, Storage Cleanup Utility — automatically removes stale debug screenshots, HTML…, glob, patchright_async_api, shutil, subprocess, tempfile (+1 more)

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
Cohesion: 0.09
Nodes (38): Analyzes the failure context and DOM content to suggest a selector repair. Uses…, suggest_fix(), capture_failure_context(), Exception, Failure Detector — parses and structures error context from failed Playwright…, Assembles a standardized diagnostic dictionary containing all available details…, detect_manual_action_required(), Manual Action Detector — identifies pages requiring human verification (2FA,… (+30 more)

### Community 70 - "sort_container_types"
Cohesion: 0.40
Nodes (4): Sort container types in standard order: DRY 20 (20GP) -> DRY 40 (40GP) -> DRY…, sort_container_types(), test_container_types_standard_ordering(), model_validator

### Community 71 - "carrier_switches.py"
Cohesion: 0.30
Nodes (11): get_switches(), off_message(), _path(), Admin on/off switch per carrier, for when a carrier's site is down or under…, Every switchable carrier: {"enabled", "reason", "updated_by", "updated_at"}; on…, The message for a switched-off carrier's result, or None when it is on., _read(), set_switch() (+3 more)

### Community 72 - "deploy"
Cohesion: 0.25
Nodes (7): build, builder, deploy, restartPolicyMaxRetries, restartPolicyType, startCommand, $schema

### Community 73 - ".search_quotes"
Cohesion: 0.18
Nodes (7): extract_locode_and_country(), prepare_maersk_query(), Fills an autocomplete field using the proven original element-level…, Extracts LOCODE and country name from text like 'CASABLANCA, MOROCCO (MACAS)'…, Maps standard container search codes (e.g. 'DRY 20', '20GP') to Maersk Spot…, Scores a Maersk autocomplete dropdown suggestion. NOTE: The nested/indented…, get_cached_carrier_port()

### Community 74 - "test_browser_cleanup.py"
Cohesion: 0.27
Nodes (11): Delete per-search profile copies ("chrome_profile_<carrier>_tmp_<id>") and…, remove_stale_temp_profiles(), _make_profile(), profiles(), fixture, Leftover browser and profile cleanup (services/browser_cleanup.py). The profile…, test_an_interrupted_save_restores_the_master(), test_masters_are_never_deleted() (+3 more)

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

### Community 82 - "tunnel_client.py"
Cohesion: 0.40
Nodes (5): argparse, handle_request(), AsyncClient, run_client(), websockets

### Community 83 - "layout.tsx"
Cohesion: 0.25
Nodes (6): frontend_src_app_globals, instrumentSans, inter, metadata, viewport, ThemeProvider()

### Community 84 - "._fs_pair_and_select"
Cohesion: 0.29
Nodes (5): clean_vessel_name(), get_booking_start_date(), date, Applies the business rules and pairs FreightSmart prices with crawled…, OOCL — FreightSmart Price Quotes (E-Quote / E-Spot) Paired With Sailing Schedules

### Community 85 - ".login"
Cohesion: 0.20
Nodes (6): _is_logged_in_url(), Wait until the login page either redirects to a signed-in page or shows its…, True once Maersk has moved past the login pages to a signed-in page., Load the saved login an admin uploaded (Admin > Carriers on / off) into this…, Types text character by character into a given locator or element handle with…, test_logged_in_url()

### Community 86 - "parse_msc_modal_charges"
Cohesion: 0.24
Nodes (8): parse_msc_modal_charges(), Parses charges from MSC BreakdownModal text. Correctly includes charges whose…, Test MSC charges parsing for Singapore to Conakry, Guinea (40GP). Charges with…, Test when only some surcharges have the payment condition., test_msc_charges_mixed_conditions(), test_msc_charges_singapore_to_conakry_guinea(), Verify MSC charge extraction logic parses Panama Canal Surcharge properly., test_msc_charge_extraction_logic()

### Community 88 - "os"
Cohesion: 0.08
Nodes (23): asyncio, Page Observer — captures page state (screenshot, DOM, visible text) on failure., CMA CGM Live Connector — Playwright automation. Credentials read from env:…, GreenX (Evergreen) Live Connector - Playwright automation., dump_options(), main(), Diagnostic: dump ALL dropdown options (text + innerHTML) when typing 'DEHAM'…, Pydantic schemas for API request/response validation. (+15 more)

### Community 89 - "registry.py"
Cohesion: 0.16
Nodes (11): get_connector(), Carrier Registry — factory for getting the right connector per carrier. When…, Get the appropriate connector for a carrier. If USE_MOCK_CARRIERS=true: returns…, Standalone Test & Verification Suite for Hapag-Lloyd Prices REST API Connector.…, test_registry_integration(), main(), getpass, main() (+3 more)

### Community 90 - "test_el_dekheila_maersk.py"
Cohesion: 0.40
Nodes (4): Verify non-Maersk carriers get standard UN/LOCODE or default mappings., Verify that El Dekheila maps specifically to 'Alexandria Dekheila, Egypt' for…, test_el_dekheila_maersk_override(), test_el_dekheila_other_carriers_unaffected()

### Community 91 - "test_excel_exports.js"
Cohesion: 0.33
Nodes (6): ref_fs, assert(), ExcelJS, fs, mockBatchResults, testTariffExport()

### Community 92 - "._mouse_glide_to"
Cohesion: 0.24
Nodes (5): Clicks an element with pre-click and post-click human-like reaction pauses., Visible page size, read from the page., Move the real mouse pointer to (x, y) along a slightly curved, uneven path.…, Scroll with the wheel if needed, glide to the element, hover, then press and…, Small aimless pointer drift, as a person does while a page loads.

### Community 93 - "[2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History"
Cohesion: 0.40
Nodes (5): [2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History, Admin User Search History & SGT GMT+8 Conversion (`AdminDashboard.tsx`), GreenX (Evergreen) Card Isolation & Surcharge Parsing (`greenx_connector.py`), Multi-Route Batch Execution Engine (`batch_engine.py`), OOCL FreightSmart 28-Day Calendar Expansion (`oocl_connector.py`)

### Community 94 - "Scraper Robustness Review — July 2026"
Cohesion: 0.33
Nodes (5): 1. What was measured, 3. Multi-port quick search — defects found and fixed, 4. Ranked recommendations, 5. Verification of this change, Scraper Robustness Review — July 2026

### Community 95 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, dev, lint, start

### Community 96 - "frontend/README.md"
Cohesion: 0.50
Nodes (3): Deploy on Vercel, Getting Started, Learn More

### Community 97 - "pytest"
Cohesion: 0.13
Nodes (11): parse_hapag_card_text_mock(), Verify that multi-leg/feeder routes take the final arrival ETA and 28 days TT., Mock implementation of the JS evaluate logic inside hapag_lloyd_connector.py., test_hapag_multi_leg_schedule_extraction(), parse_hapag_section(), Unit test to verify Hapag-Lloyd Price Breakdown section classification logic.…, test_hapag_section_parsing_order(), Tests for rate search API endpoints. (+3 more)

### Community 98 - "[2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control"
Cohesion: 0.40
Nodes (5): [2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control, Concurrency Limit Queue & Admin Control Panel, MSC — Mediterranean Shipping Company Connector Implementation, ONE — Inbound Free Time Swap & Scraper Upgrade, OOCL — Orient Overseas Container Line Connector Implementation

### Community 100 - "._fs_extract_rows"
Cohesion: 0.20
Nodes (8): Opens the Details dialog for a card, clicks the Charge Breakdown tab, extracts…, Collects result cards from the FreightSmart quote results page., [2026-08-07] — Carrier Specific Free Time, Demurrage/Detention Splitting, MSC CDD Surcharges, OOCL Nearby Route Filtering & Favicon Cache Busting, Demurrage & Detention Split Fields Across System (`schema.py`, `msc_connector.py`, `maersk_connector.py`, `one_connector.py`, `greenx_connector.py`, `cma_connector.py`, `oocl_connector.py`, `ResultsTable.tsx`, `excel_export.py`), Favicon Cache Busting & Brand Icon (`layout.tsx`, `icon.png`, `favicon.ico`), Hapag-Lloyd MHD (Merchant Haulage Detention) PDF Tariff Scraper (`hapag_freetime_scraper.py`, `hapag_freetime.json`), MSC Cargo Data Declaration [CDD] & Working Days Free Time (`msc_connector.py`), OOCL Nearby Route Recommendations Suppression (`oocl_connector.py`)

### Community 101 - "chat_service.py"
Cohesion: 0.28
Nodes (8): get_recent_search_status_context(), handle_chat_query(), _local_chatbot_fallback(), Chat Service — manages conversational AI queries from the frontend user using…, Intelligent responder for search status, carrier guidance, air/sea info, and…, Queries the database for the most recent rate search status to give the chatbot…, Sends the chat message and history to native Gemini 2.5 Flash API. If Gemini…, test_chat_service_offline_fallback()

### Community 102 - "[2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash"
Cohesion: 0.40
Nodes (5): [2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash, AI RFQ Front Door & Air Freight Support, Multi-Origin & Gappy List Parsing (Sea RFQs), Native Gemini 2.5 Flash Direct API Integration, Search Form Streamlining

### Community 103 - "websockify_carrier_proxy"
Cohesion: 0.22
Nodes (5): websocket, Proxy WebSocket connections to legacy local x11vnc at localhost:5900., Proxy WebSocket connections to specific carrier x11vnc servers., websockify_carrier_proxy(), websockify_proxy()

### Community 106 - "[2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes"
Cohesion: 0.50
Nodes (4): [2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes, CMA CGM — Chrome Profile Bypass, ONE — Date Formatting & Charge Breakdown Pollution, ONE — Date Picker Pre-selection Issue

### Community 116 - "._fetch_all_container_types"
Cohesion: 0.25
Nodes (4): Required abstract method implementation; delegates to run_full_search., Batch (RFQ) mode: the base implementation drives a browser page, so answer from…, Called by job_service once per container type (request.container_type). All…, Executes full rate search against Hapag-Lloyd Prices API. Queries each…

### Community 117 - "[2026-05-23 – 2026-05-24] — Maersk Shadow DOM & Stealth Upgrades"
Cohesion: 0.50
Nodes (4): [2026-05-23 – 2026-05-24] — Maersk Shadow DOM & Stealth Upgrades, Maersk — 2FA/CAPTCHA Human-in-the-Loop via noVNC, Maersk — Login Credential Autofill Corruption, Maersk — Shadow DOM Piercing for MDS Web Components

### Community 118 - "._query_prices_api"
Cohesion: 0.20
Nodes (5): AsyncClient, Resolves a free-text port name or string (e.g. 'Singapore', 'Hamburg, Germany…, Hapag-Lloyd Prices API requires earliestDepartureDate to be at least 4 calendar…, Constructs OpenAPI compliant OfferRequest payload., Sends a single POST /prices request with rate-limiting and error handling.

### Community 119 - "test_port_fixes.py"
Cohesion: 0.22
Nodes (10): fetch_port_fixes(), Saved port name fixes, marked built in or admin-added, and the ports each…, Copy the connector's "port not found" note onto the result row, if it made one., _store_port_not_found(), _miss(), Port name fixes: connectors note ports their own search couldn't find, results…, test_connector_note_is_copied_onto_the_result(), test_endpoint_groups_recent_misses_and_lists_fixes() (+2 more)

### Community 120 - "Architecture Overview"
Cohesion: 0.50
Nodes (4): Architecture Overview, Carrier Connector Lifecycle, Charge Classification Rules, Search Flow

### Community 121 - ".run_full_search"
Cohesion: 0.25
Nodes (3): Serves one container-type cycle from the cached merged quote set: -…, One crawl serves all container-type cycles (cached), combining: 1. Sailing…, Public oocl.com Chromium sailing schedule crawl bypassed per directive. All…

### Community 122 - "[2026-05-31] — Multi-Instance Support & Charge Classification"
Cohesion: 0.67
Nodes (3): [2026-05-31] — Multi-Instance Support & Charge Classification, Charge Classification Improvements, Multi-Instance Concurrent Searches

### Community 123 - "._fs_iterate_calendar_dates"
Cohesion: 0.33
Nodes (4): _click_date_strip_item(), _open_calendar(), Iterates through the FreightSmart results date calendar to collect E-Quote and…, setter

### Community 124 - "[2026-06-02] — Hapag-Lloyd Transshipment & Duplicate Fix"
Cohesion: 0.67
Nodes (3): [2026-06-02] — Hapag-Lloyd Transshipment & Duplicate Fix, Hapag-Lloyd — Duplicate Sailings from Transshipment Vessels, Hapag-Lloyd — Routing Not Marked as Transit

### Community 125 - "create_batch_rate_search"
Cohesion: 0.60
Nodes (6): create_batch_rate_search(), _contains(), _looks_like(), _norm(), _resolve(), Execute a multi-route RFQ batch using Vertical Parallel Persistent Sessions.…

### Community 126 - "._parse_free_time_text"
Cohesion: 0.43
Nodes (5): Parses ONE QUOTE Free Time popover text for DESTINATION ONLY. Ignores Origin…, test_one_free_time_parser_origin_only_ignored(), test_one_free_time_parser_test_a(), test_one_free_time_parser_test_b(), test_one_free_time_parser_test_c()

### Community 127 - "test_auth_routes.py"
Cohesion: 0.33
Nodes (5): asyncio, Integration tests for authentication, legacy user password setup, pending…, test_full_auth_lifecycle(), main, pytest_asyncio

### Community 129 - "[2026-08-04 - 2026-08-06] — CMA CGM Dynamic RAMP/POD Rerouting, Brand Excel Styling, Port Synonym Matching & Tunnel Relays"
Cohesion: 0.50
Nodes (4): [2026-08-04 - 2026-08-06] — CMA CGM Dynamic RAMP/POD Rerouting, Brand Excel Styling, Port Synonym Matching & Tunnel Relays, Brand-Aligned Excel Export Styling (`excel_export.py`), CMA CGM Dynamic RAMP / POD Advisory Banner Detection (`cma_connector.py`), Railway WebSocket Tunnel Relay & Failover (`tunnel_client.py`, `run_tunnel_client.bat`, `FailoverFetch`)

### Community 132 - "test_one_premium_override.py"
Cohesion: 0.40
Nodes (3): MockCard, Unit test for ONE connector and charge classifier Premium Cargo Service…, test_premium_cargo_service_override()

### Community 133 - "Infreight Sourcing Automation — Run Audit (30 Jul 2026)"
Cohesion: 0.33
Nodes (5): Expected on this machine (not automation faults), Faults (correctness), Inefficiencies (speed), Infreight Sourcing Automation — Run Audit (30 Jul 2026), Suggested priority

### Community 134 - "._fs_parse_card"
Cohesion: 0.40
Nodes (3): _parse_date(), parse_oocl_date(), Parses one FreightSmart result card's inner text into a raw row dict. Text-…

### Community 135 - "[2026-07-03] — Robustness Review & Multi-Port Quick Search Fixes"
Cohesion: 0.67
Nodes (3): [2026-07-03] — Robustness Review & Multi-Port Quick Search Fixes, Batch (168-route) Execution — Isolation, Lock Scope, Polling, Robustness Review (see `docs/ROBUSTNESS_REVIEW_2026-07.md`)

### Community 136 - "_dismiss_once"
Cohesion: 0.40
Nodes (3): _dismiss_once(), Shadow-DOM-aware check for whether the onboarding tour heading is on screen., Position-based fallback for the onboarding tour popup: instead of guessing its…

### Community 139 - "parse_rfq_endpoint"
Cohesion: 0.67
Nodes (3): parse_rfq_endpoint(), post, Parse a free-text RFQ email or message into a structured RateSearchRequest…

### Community 141 - "_user_overrides_path"
Cohesion: 0.67
Nodes (3): Where admin-saved port name fixes are kept. Railway rebuilds /app on every…, _user_overrides_path(), test_saved_fixes_live_on_the_persistent_volume()

### Community 142 - "test_oocl_normalize_result_with_pcs"
Cohesion: 0.67
Nodes (3): asyncio, Verify OOCL normalize_result incorporates Panama Canal Surcharge (PCS)., test_oocl_normalize_result_with_pcs()

### Community 143 - "clean_selector_memory"
Cohesion: 0.67
Nodes (3): clean_selector_memory(), fixture, Wipes the selector memory JSON file before and after each test.

### Community 144 - "[2026-05-18 – 2026-05-19] — Railway Deployment & Docker"
Cohesion: 0.67
Nodes (3): [2026-05-18 – 2026-05-19] — Railway Deployment & Docker, Persistent Chrome Profiles on Railway Volume, Railway Deployment Setup

## Knowledge Gaps
- **324 isolated node(s):** `Config`, `install_pi.sh script`, `eslintConfig`, `nextConfig`, `name` (+319 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 977 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **26 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Changelog` connect `Changelog` to `[2026-08-04 - 2026-08-06] — CMA CGM Dynamic RAMP/POD Rerouting, Brand Excel Styling, Port Synonym Matching & Tunnel Relays`, `[2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control`, `[2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning`, `._fs_extract_rows`, `[2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash`, `[2026-07-03] — Robustness Review & Multi-Port Quick Search Fixes`, `[2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes`, `[2026-05-29 – 2026-05-30] — Hapag-Lloyd Full Integration`, `Architecture Overview`, `[2026-05-18 – 2026-05-19] — Railway Deployment & Docker`, `[2026-05-23 – 2026-05-24] — Maersk Shadow DOM & Stealth Upgrades`, `[2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split`, `[2026-05-31] — Multi-Instance Support & Charge Classification`, `[2026-06-02] — Hapag-Lloyd Transshipment & Duplicate Fix`, `[2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History`, `[2026-06-30] — ONE Multi-Container & Sold-Out, GreenX Surcharge Intake, Free-Time Fixes, Maersk Diagnosis`, `[2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup`?**
  _High betweenness centrality (0.329) - this node is a cross-community bridge._
- **Why does `Maersk — Free Time Extraction from Card Text` connect `Changelog` to `RateResults.tsx`?**
  _High betweenness centrality (0.291) - this node is a cross-community bridge._
- **Are the 36 inferred relationships involving `RateSearchRequest` (e.g. with `create_batch_rate_search()` and `create_rate_search()`) actually correct?**
  _`RateSearchRequest` has 36 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `cn()` (e.g. with `Reuse the primitives` and `7. Conventions to follow from here`) actually correct?**
  _`cn()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 22 inferred relationships involving `CarrierResultStatus` (e.g. with `safe_step()` and `update_carrier_status()`) actually correct?**
  _`CarrierResultStatus` has 22 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Config`, `install_pi.sh script`, `eslintConfig` to the rest of the system?**
  _324 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `BaseCarrierConnector` be split into smaller, more focused modules?**
  _Cohesion score 0.06009783368273934 - nodes in this community are weakly interconnected._