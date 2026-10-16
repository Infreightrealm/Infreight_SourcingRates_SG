# Graph Report - Infreight_Sourcing_New  (2026-10-16)

## Corpus Check
- 284 files · ~1,192,084 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 27 file(s) not represented in the graph (top: (none) 10, .bat 9, .conf 2)

## Summary
- 2583 nodes · 6360 edges · 137 communities (112 shown, 25 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 378 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `4ce4987f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- _detect_port_mismatch
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
- database.py
- PortManager
- test_hapag_freetime.py
- HapagLloydAPIConnector
- pytest
- app/page.tsx
- test_rfq_agent.py
- re
- test_self_healing.py
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
- test_remote_worker.py
- ONEConnector
- _Page
- Engineering Report: Sourcing Portal Enhancements & Scraping Pipeline Stability
- Changelog
- AdminOverview.tsx
- package.json
- carrier_switches.py
- RateResults.tsx
- SearchQueueManager
- get_async_session_maker
- test_normalizer.py
- compilerOptions
- ._fs_dismiss_modals
- test_carrier_timeout.py
- RateSearchRequest
- dithered-logo.tsx
- 👥 The 5 Agent Roles
- HapagLloydConnector
- test_hapag_api_connector.py
- parse_msc_modal_charges
- carrier_sessions.py
- LiveSearchProgress.tsx
- lucide-react
- 🚢 Infreight Sourcing & Ocean Rate Automation System
- ._execute_single_price_request
- [2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split
- test_ai_maersk.py
- 🛠 Detailed Carrier Log
- tunnel_relay/main.py
- test_panama_canal_surcharge.py
- [2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control
- [2026-06-30] — ONE Multi-Container & Sold-Out, GreenX Surcharge Intake, Free-Time Fixes, Maersk Diagnosis
- [2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup
- websockify_carrier_proxy
- Scraper Robustness Review — July 2026
- GreenX — Surcharge Intake Fix (2026-06-30)
- Admin Page & Port Prioritization Guide
- post
- selector_memory.py
- schemas.py
- RFQParseResult
- deploy
- Frontend Redesign — Componentry Design System, Workspace & Launch Intro (2026-09-07)
- .extract_charge_breakdown
- Summary of Changes — July 20, 2026
- silk-aurora.tsx
- [2026-05-29 – 2026-05-30] — Hapag-Lloyd Full Integration
- resolve_port_alias
- json
- fetch_port_fixes
- Design system — read before touching any UI
- [2026-05-18 – 2026-05-19] — Railway Deployment & Docker
- layout.tsx
- port_routes.py
- Infreight Sourcing Automation — Run Audit (30 Jul 2026)
- .filter_cheapest_in_14d_window
- RateLimiter
- [2026-05-23 – 2026-05-24] — Maersk Shadow DOM & Stealth Upgrades
- dependencies
- .search_port
- test_excel_exports.js
- ai_agent.py
- [2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History
- chat_service.py
- devDependencies
- frontend/README.md
- test_js.js
- get_me
- os
- export_maersk_login.py
- .extract_charge_breakdown
- test_el_dekheila_maersk.py
- test_cma_freetime.py
- Working in this repository
- [2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes
- install_pi.sh
- remote_worker.py
- postcss.config.mjs
- test_hapag_schedule.py
- [2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash
- scripts
- job_service.py
- ._lookup_freetime
- Architecture Overview
- e2e_downloaded_multisheet_28ec47f9.md
- create_batch_rate_search
- scrape_one_freetime.py
- e2e_downloaded_tariff_d21a0cb7.md
- .suggest_ports
- MockCard
- ._save_carrier_overrides
- ambiguous_python_import_b35980c0aa01
- eslint.config.mjs
- fill_container_card
- [2026-05-31] — Multi-Instance Support & Charge Classification
- .get_cached_carrier_port
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
9. `MaerskConnector` - 55 edges
10. `OOCLConnector` - 54 edges

## Surprising Connections (you probably didn't know these)
- `4. Ranked recommendations` --references--> `safe_step()`  [INFERRED]
  docs/ROBUSTNESS_REVIEW_2026-07.md → backend/agent/safe_step.py
- `Free Time — GreenX blank, ONE India wrong, Hapag Nhava Sheva unresolved (Singapore → Nhava Sheva)` --references--> `_apply_freetime_to_quote()`  [INFERRED]
  CHANGELOG.md → backend/carriers/hapag_lloyd_connector.py
- `Excel Export — Routing & Free Time Columns Always Empty` --references--> `Quote`  [INFERRED]
  CHANGELOG.md → backend/models/quote.py
- `Hapag-Lloyd — Date String Standardization` --references--> `standardize_date_string()`  [INFERRED]
  CHANGELOG.md → backend/services/normalizer.py
- `2. Bugs found and fixed during the restyle` --references--> `BackendConfigModal()`  [INFERRED]
  FRONTEND_REDESIGN_2026-09-07.md → frontend/src/components/BackendConfigModal.tsx

## Import Cycles
- None detected.

## Communities (137 total, 25 thin omitted)

### Community 0 - "_detect_port_mismatch"
Cohesion: 0.25
Nodes (8): _detect_port_mismatch(), Detects port mismatch for origin or destination. Returns: - True if verified…, Test that matching LOCODE or City + Country code returns False (Verified Match)., Test that differing port strings return True (Verified Mismatch)., Test that null/empty matched port strings return None (Unknown / Could Not…, test_detect_port_mismatch_unknown_null(), test_detect_port_mismatch_verified_match(), test_detect_port_mismatch_verified_mismatch()

### Community 1 - "CarrierResultStatus"
Cohesion: 0.04
Nodes (46): ABC, BaseCarrierConnector, NotAvailableConnector, Any, Open the price breakdown / detail view for a specific quote. Args: quote_ref:…, Extract individual charge line items from the price breakdown. Returns: List of…, Normalize extracted data into a QuoteSchema using the normalizer. Args:…, Abstract base class for carrier portal connectors. (+38 more)

### Community 2 - "cn"
Cohesion: 0.06
Nodes (59): Reuse the primitives, New primitives — `frontend/src/components/ui/`, AdminUserRecord, AdminUsers(), AdminUsersProps, ago(), AuditEntry, Avatar() (+51 more)

### Community 3 - "user_routes.py"
Cohesion: 0.07
Nodes (81): admin_delete_user(), AdminLoginRequest, approve_user(), CarrierOverrideRequest, CarrierSwitchRequest, Config, create_custom_port_endpoint(), CustomPortRequest (+73 more)

### Community 4 - "auth_routes.py"
Cohesion: 0.05
Nodes (75): clear_session_cookie(), get_current_user_optional(), login(), LoginRequest, logout(), AsyncSession, BaseModel, post (+67 more)

### Community 5 - "browser_cleanup.py"
Cohesion: 0.11
Nodes (33): _is_chrome(), _is_playwright_driver(), _kill(), kill_profile_browsers(), _proc_supported(), Cleanup for Chrome browsers and temporary profiles that a failed close leaves…, Kill every automated Chrome and Playwright driver. Only call this when no…, Delete per-search profile copies ("chrome_profile_<carrier>_tmp_<id>") and… (+25 more)

### Community 6 - "SocialWidget.tsx"
Cohesion: 0.10
Nodes (34): ACCENT_COLORS, errorMessage(), relativeTime(), resizeImageToDataUrl(), SocialWidget(), SocialWidgetProps, EMOJI_GROUPS, EmojiPicker() (+26 more)

### Community 7 - "api.ts"
Cohesion: 0.06
Nodes (76): AdminDashboard(), UserRecord, LoginContent(), HomeContent(), AdminCarriers(), PROFILE_NAMES, when(), AdminPortFixes() (+68 more)

### Community 8 - "MaerskConnector"
Cohesion: 0.04
Nodes (45): extract_locode_and_country(), MaerskConnector, Maersk Browser Connector — Playwright automation using your real Google Chrome…, Fills an autocomplete field using the proven original element-level…, Execute the full search flow with Progressive Lazy Loading: 1. Login 2. Search…, Extracts freetime, demurrage, and detention from the 'Import D&D fees' tab…, Extracts LOCODE and country name from text like 'CASABLANCA, MOROCCO (MACAS)'…, Extracts the routing details from the 'Route & other details' accordion.… (+37 more)

### Community 9 - "._parse_offer_response_to_quotes"
Cohesion: 0.15
Nodes (7): Any, Constructs OpenAPI compliant OfferRequest payload., Correlates an offer from the Prices API to a physical solution in DCSA…, Maps a Prices API rate onto the categories the portal scraper produces (freight…, Leg locations are UnLocation/Facility objects per the spec; tolerate plain…, Renders a graduated weight tier (e.g. Heavy Lift: 18-99 TON) in the portal's…, Parses Hapag-Lloyd OfferResponse JSON into InFreight QuoteSchema objects,…

### Community 10 - "CMAConnector"
Cohesion: 0.07
Nodes (19): CMAConnector, Ensures 'Ramp' is explicitly selected under 'Type of location' toggle buttons…, Scans for Route, POL (Port of Loading), or POD (Port of Discharge) dropdown…, Clears the currently selected Destination port tag/card, re-types the locode,…, Dynamically extracts any recommended 5-letter POD LOCODE mentioned in the…, Detects if CMA CGM displayed an advisory banner message: "Looking for AEJEA or…, Handles the 'Customer account' -> 'Role (you are acting as)' dropdown on CMA…, Repeatedly clicks 'More results' if visible to load ALL quotes on the page. (+11 more)

### Community 11 - "database.py"
Cohesion: 0.09
Nodes (34): alembic, get_sync_url(), run_migrations_offline(), run_migrations_online(), Base, _get_database_url(), _get_engine(), get_session() (+26 more)

### Community 12 - "PortManager"
Cohesion: 0.14
Nodes (6): prepare_maersk_query(), get_custom_ports(), PortManager, Constructs the specific search query to type into carrier search boxes. If the…, Cache verified carrier port name and save persistently to…, Clean and normalize user input for port searching.

### Community 13 - "test_hapag_freetime.py"
Cohesion: 0.19
Nodes (15): _apply_freetime_to_quote(), freetime_days(), match_freetime_entry(), Any, Destination free time from config/hapag_freetime.json, shared by the Hapag-…, Days for this container from a table entry ({"20GP": n, "40GP": n} or a bare…, The table entry whose country name appears in `text` as whole words. Whole…, days() (+7 more)

### Community 14 - "HapagLloydAPIConnector"
Cohesion: 0.13
Nodes (6): HapagLloydAPIConnector, Direct REST API connector for Hapag-Lloyd Prices API v2.1.4., API connectors do not require browser login sessions., No browser session to reset between batch routes., Resolves a free-text port name or string (e.g. 'Singapore', 'Hamburg, Germany…, Hapag-Lloyd Prices API requires earliestDepartureDate to be at least 4 calendar…

### Community 15 - "pytest"
Cohesion: 0.15
Nodes (11): asyncio, Integration tests for authentication, legacy user password setup, pending…, test_full_auth_lifecycle(), parse_hapag_section(), Unit test to verify Hapag-Lloyd Price Breakdown section classification logic.…, test_hapag_section_parsing_order(), asyncio, test_one_breakdown_currency_and_arbitrary_destination_classification() (+3 more)

### Community 16 - "app/page.tsx"
Cohesion: 0.06
Nodes (51): nextConfig, AppHeader(), AppHeaderProps, initials(), systemStatus(), BackendConfigModal(), BackendConfigModalProps, LaunchIntro() (+43 more)

### Community 17 - "test_rfq_agent.py"
Cohesion: 0.10
Nodes (28): asyncio, Unit tests for the Gemini AI RFQ Agent service (parse_rfq). Includes…, Test Image 2: Air rate request generates 3 drafts to Glenn (AWOT), Jing Hui…, Test Image 4: Steel Plate ex Pasir Gudang / Tanjung Pelepas for 20' & 40'., Test Guardrail: Detects Reefer container request and returns unsupported_cargo…, Test Guardrail: Detects LCL request., Test OpenFlights 6,072 IATA airport dataset and shorthand alias resolution., Test Pak Shaun email: "Hi team, need rate for 10x20GP from PK to JKT. Urgent… (+20 more)

### Community 19 - "test_self_healing.py"
Cohesion: 0.11
Nodes (27): Analyzes the failure context and DOM content to suggest a selector repair. Uses…, suggest_fix(), capture_failure_context(), Exception, Failure Detector — parses and structures error context from failed Playwright…, Assembles a standardized diagnostic dictionary containing all available details…, detect_manual_action_required(), Manual Action Detector — identifies pages requiring human verification (2FA,… (+19 more)

### Community 20 - "[2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning"
Cohesion: 0.14
Nodes (13): Verifies the "I am the price owner" radio is genuinely checked, piercing shadow…, [2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning, [2026-07-03] — OOCL FreightSmart Autoclear, Hapag Price Leak & Redirect fixes, Maersk Cache Scoping, Dallas Overrides, GreenX — "No Quotes" Reported While Quotes Visibly Loaded in VNC, Hapag-Lloyd — Configurable Pacing & Redundant-Wait Removal, Hapag-Lloyd — Price Leaks, Column Matching, and Redirect Recovery, Job Scheduler — Concurrency Default, Maersk — 0.0-USD / "Not Open" Card Flakiness (the "Quotes Found but Empty Excel" root causes) (+5 more)

### Community 21 - "GreenXConnector"
Cohesion: 0.09
Nodes (14): GreenXConnector, date, Overrides base search runner to query all 3 sizes at once and cache the…, Type a LOCODE into the autocomplete field and click the first visible dropdown…, Find quantity input next to or below label_text and fill it., Find the exact individual quote card container row encompassing dates, rates,…, Dismiss any cookie/alert modal that would intercept pointer events., Splits a single raw multi-container quote card into multiple QuoteSchema… (+6 more)

### Community 22 - "social_routes.py"
Cohesion: 0.12
Nodes (26): get_current_user(), Dependency that strictly requires an authenticated active member., get_conversation(), list_colleagues(), poke_colleague(), PokeRequest, AsyncSession, BaseModel (+18 more)

### Community 23 - "ChargeCategory"
Cohesion: 0.18
Nodes (21): ChargeCategory, classify_charge(), Charge Classifier — rule-based classification of freight charge line items.…, Classify a charge line item based on its name, amount, section heading, and…, Tests for charge classifier., test_basic_ocean_freight(), test_cwx_heavy_weight_charge(), test_destination_charges() (+13 more)

### Community 24 - "backend/main.py"
Cohesion: 0.11
Nodes (21): health(), lifespan(), get, Infreight Ocean Carrier Rate Automation — FastAPI Application. Main entry point…, Check if the VNC viewer is available (production only, where Xvfb runs)., Startup and shutdown events., vnc_status(), profile_base_dirs() (+13 more)

### Community 25 - "rate_search_routes.py"
Cohesion: 0.10
Nodes (31): carrier_switch_status(), get_admin_analytics_endpoint(), get_batch_search_status(), get_rate_search(), get_repair_reports(), get_user_search_history(), AsyncSession, get (+23 more)

### Community 26 - "MSCConnector"
Cohesion: 0.08
Nodes (23): format_to_iso_date(), is_same_container_type(), map_requested_containers_to_msc_sizes(), MSCConnector, Parse '14 Jun 2026' to 'YYYY-MM-DD, Map requested container type strings (e.g. '20GP', 'DRY 20', '40HQ', 'DRY 40H')…, Checks whether two container type representations map to the same MSC equipment…, Playwright-based automation for MSC (Mediterranean Shipping Company). (+15 more)

### Community 27 - "parse_rfq"
Cohesion: 0.13
Nodes (25): _call_native_gemini_api(), _detect_booking_confirmation(), _detect_dual_mode_enquiry(), _detect_mode_by_hierarchy(), _detect_unsupported_cargo(), _extract_20gp_weight_priority(), generate_dual_air_drafts(), _load_airport_aliases_config() (+17 more)

### Community 28 - "port_manager.py"
Cohesion: 0.29
Nodes (10): add_carrier_override(), add_custom_port(), delete_carrier_override(), delete_custom_port(), get_carrier_overrides(), get_popular_ports_config(), update_popular_ports_config(), test_dynamic_boosting() (+2 more)

### Community 29 - "AIBrowserAgent"
Cohesion: 0.17
Nodes (10): AIBrowserAgent, Capture the current page as a PNG screenshot., Build the prompt with task description and action history., Parse Gemini's response into an action dict., Call Gemini API with exponential backoff retry., Execute a parsed action on the browser page., Detect if the agent is stuck repeating the same action., Find all visible interactive elements and format them as a prompt guide. (+2 more)

### Community 30 - "test_remote_worker.py"
Cohesion: 0.10
Nodes (24): A worker machine (e.g. the office laptop) that runs some carriers' searches., WorkerHeartbeat, db(), row(), setup(), FakeConnector, fixture, Handing a carrier (Maersk) to a worker machine through the shared database. (+16 more)

### Community 31 - "ONEConnector"
Cohesion: 0.12
Nodes (9): ONEConnector, date, Parses ONE QUOTE Free Time popover text for DESTINATION ONLY. Ignores Origin…, Splits a single raw multi-container quote card into multiple QuoteSchema…, Tries to click a matching option from ONE's visible dropdown. Returns True only…, test_one_free_time_parser_origin_only_ignored(), test_one_free_time_parser_test_a(), test_one_free_time_parser_test_b() (+1 more)

### Community 32 - "_Page"
Cohesion: 0.06
Nodes (26): _is_logged_in_url(), maersk_proxy_settings(), Small aimless pointer drift, as a person does while a page loads., Clicks an element with pre-click and post-click human-like reaction pauses., Maersk's "You are authenticated / Continue as <name>" page: the account is…, Wait until the login page either redirects to a signed-in page or shows its…, True once Maersk has moved past the login pages to a signed-in page., Load the saved login an admin uploaded (Admin > Carriers on / off) into this… (+18 more)

### Community 33 - "Engineering Report: Sourcing Portal Enhancements & Scraping Pipeline Stability"
Cohesion: 0.08
Nodes (23): 1. Anti-Bot Mitigation & CAPTCHA Human-in-the-Loop Recovery, 2. Sourcing Parallelization & Surcharges Optimization, 3. Autocomplete Intelligence & Location Mapping, 4. Scraper Pipeline Maintenance, 5. Infrastructure & DevSecOps Enhancements, Business Value, Business Value, Business Value (+15 more)

### Community 34 - "Changelog"
Cohesion: 0.11
Nodes (18): [2026-05-25 – 2026-05-26] — VNC Display Isolation & Proxy Integration, [2026-06-01] — Hapag-Lloyd Sold Out Detection & Date Parsing, [2026-06-02] — Hapag-Lloyd Transshipment & Duplicate Fix, [2026-06-03] — CMA CGM Routing & Free Time Extraction, [2026-07-08] — OOCL E-Quote Calendar Navigation, cheapest E-Spot selection, and E-Quote/E-Spot isolation refinements, [2026-07-09] — Hapag-Lloyd Quick Quotes pairing and selection simplification, Bright Data ISP Proxy Integration, Changelog (+10 more)

### Community 35 - "AdminOverview.tsx"
Cohesion: 0.10
Nodes (24): AdminAnalytics, AdminOverview(), AdminOverviewProps, AdminOverviewUser, AnalyticsRange, Attention, attentionItems(), CARRIER_LABELS (+16 more)

### Community 36 - "package.json"
Cohesion: 0.12
Nodes (16): engines, node, name, packageManager, private, version, clsx, react-dom (+8 more)

### Community 37 - "carrier_switches.py"
Cohesion: 0.35
Nodes (10): get_switches(), off_message(), _path(), Admin on/off switch per carrier, for when a carrier's site is down or under…, Every switchable carrier: {"enabled", "reason", "updated_by", "updated_at"}; on…, The message for a switched-off carrier's result, or None when it is on., _read(), set_switch() (+2 more)

### Community 38 - "RateResults.tsx"
Cohesion: 0.07
Nodes (58): LiveSearchProgressProps, QuoteBreakdownDrawer(), QuoteBreakdownDrawerProps, Breakdown(), ChargeList(), dateValue(), freeTimeText(), isSoldOut() (+50 more)

### Community 39 - "SearchQueueManager"
Cohesion: 0.12
Nodes (11): Lock, Marks a search as completed internally so we can track the auto-release timeout., Called periodically in a background task to check if the user has held the lock…, Forcefully clears all queued searches and the active lock. Useful for…, Returns or creates an asyncio.Lock for a specific carrier code to prevent…, Adds a search to the queue and waits until it becomes the active search. Event-…, Singleton manager to enforce a FIFO queue for rate searches. Since web scraping…, Returns the current position of the search in the queue. 0 means it is the… (+3 more)

### Community 40 - "get_async_session_maker"
Cohesion: 0.16
Nodes (21): get_async_session_maker(), Get the session maker for use outside of FastAPI dependency injection., cancel_all_active_searches(), cleanup_browsers_if_idle(), UUID, Run a single carrier search job. Updates the CarrierSearchResult record…, Check all carrier results and update the overall search status., Run search jobs for all selected carriers concurrently, updating overall status… (+13 more)

### Community 41 - "test_normalizer.py"
Cohesion: 0.23
Nodes (8): calculate_final_freight_value(), Calculate the final freight value from a list of classified charges. Args:…, Tests for normalizer / final freight value calculator., test_basic_calculation(), test_no_charges(), test_one_breakdown_parsing(), test_only_excluded(), test_positive_discount_normalized()

### Community 42 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 43 - "._fs_dismiss_modals"
Cohesion: 0.06
Nodes (26): clean_vessel_name(), _dismiss_once(), _click_date_strip_item(), _open_calendar(), _parse_date(), Event, Lock, Parses one FreightSmart result card's inner text into a raw row dict. Text-… (+18 more)

### Community 44 - "test_carrier_timeout.py"
Cohesion: 0.19
Nodes (10): CrashingConnector, HangingConnector, asyncio, A carrier whose browser hangs must be stopped after CARRIER_SEARCH_TIMEOUT_SEC…, Hangs on the sizes in `hang_on`; answers NO_QUOTES_AVAILABLE for the rest., Like a real connector whose tab dies: reports a crash, then never returns., _run(), test_crashed_tab_stops_the_carrier_without_waiting_for_the_timeout() (+2 more)

### Community 45 - "RateSearchRequest"
Cohesion: 0.06
Nodes (42): get_booking_start_date(), OOCLConnector, parse_oocl_date(), date, Applies the business rules and pairs FreightSmart prices with crawled…, Serves one container-type cycle from the cached merged quote set: -…, One crawl serves all container-type cycles (cached), combining: 1. Sailing…, Attempts to automatically click the Cloudflare Turnstile 'Verify you are human'… (+34 more)

### Community 46 - "dithered-logo.tsx"
Cohesion: 0.19
Nodes (15): applyMaskInversion(), buildRoundedMask(), DEFAULTS, DitherConfig, DitheredLogo(), DitheredLogoProps, drawParticles(), errorDiffusionDither() (+7 more)

### Community 47 - "👥 The 5 Agent Roles"
Cohesion: 0.13
Nodes (14): 1. Intake Agent (Email Listener), 2. Sourcing Orchestrator (The Coordinator), 3. Sourcing & Scraping Agent (Rates Engine), 4. Finance & Costing Agent (Excel Compiler), 5. Email Draft Agent (Communicator), 📋 Executive Summary, 🛠️ Implementation Stages, Phase 1: Email Integration (Week 1-2) (+6 more)

### Community 48 - "HapagLloydConnector"
Cohesion: 0.06
Nodes (35): HapagLloydConnector, HapagServiceUnavailableException, Exception, Normalize various date formats (e.g. 2026-05-31, 31.05.2026, 31 May 2026, 31…, Robustly selects options from Hapag-Lloyd custom dropdown lists. Types the…, Detects the Microsoft B2C identity/OAuth login page. Hapag can silently bounce…, Guards against the session-expiry-mid-crawl failure mode: the existing redirect…, Crawls Hapag-Lloyd sailing schedules from the Schedule tab. (+27 more)

### Community 49 - "test_hapag_api_connector.py"
Cohesion: 0.31
Nodes (10): get_connector(), Get the appropriate connector for a carrier. If USE_MOCK_CARRIERS=true: returns…, main(), Standalone Test & Verification Suite for Hapag-Lloyd Prices REST API Connector.…, test_dcsa_commercial_schedules_cross_validation(), test_locode_resolution(), test_origin_landfreight_inclusion(), test_payload_generation() (+2 more)

### Community 50 - "parse_msc_modal_charges"
Cohesion: 0.24
Nodes (8): parse_msc_modal_charges(), Parses charges from MSC BreakdownModal text. Correctly includes charges whose…, Test MSC charges parsing for Singapore to Conakry, Guinea (40GP). Charges with…, Test when only some surcharges have the payment condition., test_msc_charges_mixed_conditions(), test_msc_charges_singapore_to_conakry_guinea(), Verify MSC charge extraction logic parses Panama Canal Surcharge properly., test_msc_charge_extraction_logic()

### Community 51 - "carrier_sessions.py"
Cohesion: 0.11
Nodes (20): clean_storage_state(), delete_session(), load_session(), _on_domain(), _path(), Saved carrier logins uploaded by an admin. An admin logs in to a carrier in…, What the admin screen shows: who uploaded it, when, and how much it holds., Keep only this carrier's cookies and localStorage, in the shape add_cookies… (+12 more)

### Community 52 - "LiveSearchProgress.tsx"
Cohesion: 0.09
Nodes (29): ChatWidget(), ChatWidgetProps, Message, ACTION_STATUSES, ChipModel, describe(), EMPTY_STATUSES, formatElapsed() (+21 more)

### Community 53 - "lucide-react"
Cohesion: 0.09
Nodes (37): 0. The one invariant, CarrierMultiSelect(), CarrierMultiSelectProps, isAllCarriers(), toggleAllCarriers(), toggleCarrierSelection(), PortAutocomplete(), PortAutocompleteProps (+29 more)

### Community 54 - "🚢 Infreight Sourcing & Ocean Rate Automation System"
Cohesion: 0.14
Nodes (13): 1. Multi-Carrier Automation Engine, 2. Intelligent Surcharge & Charge Classifier Engine (`charge_classifier.py`), 3. Container Comparison Matrix & Excel Export Engine, 🚢 Infreight Sourcing & Ocean Rate Automation System, 🌟 Key Capabilities, 📄 License & Confidentiality, Prerequisites, 🛠️ Project Structure (+5 more)

### Community 55 - "._execute_single_price_request"
Cohesion: 0.40
Nodes (3): AsyncClient, Sends a single POST /prices request with rate-limiting and error handling., Queries Hapag-Lloyd DCSA Commercial Schedules API (v1.0.2) to retrieve point-…

### Community 56 - "[2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split"
Cohesion: 0.15
Nodes (13): G2 Stress Test: "Hi, Please book the below as per your quote ref INF-2026-0842:…, H1 Stress Test: Table with 2 distinct rows: Row 1: POL Singapore, POD Jakarta,…, test_g2_booking_confirmation_guardrail(), test_h1_table_deduplication_two_pairs(), [2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split, Booking Confirmation / Instructions Intercept Guardrail G2 (`rfq_agent.py` & `RfqInputSection.tsx`), Commercial Sales Desk Intelligence (`sales_notes`), Deterministic Port Alias Resolver (`ports_aliases.json`) (+5 more)

### Community 57 - "test_ai_maersk.py"
Cohesion: 0.43
Nodes (6): _cleanup_profile(), main(), Experimental AI Agent Test -- Maersk Quote Search This script tests the AI…, Remove temporary chrome profile directory., Print with ASCII-safe encoding for Windows console., safe_print()

### Community 58 - "🛠 Detailed Carrier Log"
Cohesion: 0.15
Nodes (12): 🛠 Detailed Carrier Log, 🟢 GreenX, 🟠 Hapag-Lloyd, Infreight Ocean Carrier Rate Automation — Development Log, 🚀 Key Highlights & Architectural Changes, 🔌 Local Laptop Deployment (Self-Hosted Worker), 🔵 Maersk, 💗 ONE (Ocean Network Express) (+4 more)

### Community 59 - "tunnel_relay/main.py"
Cohesion: 0.25
Nodes (8): api_route, fastapi_middleware_cors, health(), get, Request, websocket, relay_request(), websocket_endpoint()

### Community 60 - "test_panama_canal_surcharge.py"
Cohesion: 0.12
Nodes (20): Sort container types in standard order: DRY 20 (20GP) -> DRY 40 (40GP) -> DRY…, sort_container_types(), is_weight_surcharge_applicable(), Evaluates whether a weight-tier or overweight surcharge is applicable for the…, classify_and_organize_charges(), Takes raw charge line items and classifies them. Args: raw_charges: list of…, test_classify_and_organize(), asyncio (+12 more)

### Community 61 - "[2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control"
Cohesion: 0.40
Nodes (5): [2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control, Concurrency Limit Queue & Admin Control Panel, MSC — Mediterranean Shipping Company Connector Implementation, ONE — Inbound Free Time Swap & Scraper Upgrade, OOCL — Orient Overseas Container Line Connector Implementation

### Community 62 - "[2026-06-30] — ONE Multi-Container & Sold-Out, GreenX Surcharge Intake, Free-Time Fixes, Maersk Diagnosis"
Cohesion: 0.25
Nodes (8): [2026-06-30] — ONE Multi-Container & Sold-Out, GreenX Surcharge Intake, Free-Time Fixes, Maersk Diagnosis, Free Time — GreenX blank, ONE India wrong, Hapag Nhava Sheva unresolved (Singapore → Nhava Sheva), GreenX — Only Basic Ocean Freight & LSS Folded Into Final Value, MAERSK — "Quotes Found" but Empty Excel (Diagnosis), ONE — All-Container-Type Search Returning 0 Quotes, ONE — Multi-Container Breakdown Triple-Counted / Inflated Final Value, ONE — Sold-Out ("Notify Me") Sailings Appearing as Quotes, Performance/Reliability — Stop Copying Chrome Caches During Profile Clone/Sync

### Community 63 - "[2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup"
Cohesion: 0.22
Nodes (8): [2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup, Chromium Cache Auto-Cleanup (Railway Storage Bloat Prevention), CMA CGM — 30-Second Timeout on Sold Out Cards, CMA CGM — Free Time Regex Too Strict, CMA CGM — Routing Regex Not Matching "via LEKKI, LA, NG", Excel Export — Routing & Free Time Columns Always Empty, Excel Export — Sold Out Rows Not Showing, Maersk — Hardcoded Port Overrides

### Community 64 - "websockify_carrier_proxy"
Cohesion: 0.22
Nodes (5): websocket, Proxy WebSocket connections to legacy local x11vnc at localhost:5900., Proxy WebSocket connections to specific carrier x11vnc servers., websockify_carrier_proxy(), websockify_proxy()

### Community 65 - "Scraper Robustness Review — July 2026"
Cohesion: 0.33
Nodes (5): 1. What was measured, 3. Multi-port quick search — defects found and fixed, 4. Ranked recommendations, 5. Verification of this change, Scraper Robustness Review — July 2026

### Community 66 - "GreenX — Surcharge Intake Fix (2026-06-30)"
Cohesion: 0.22
Nodes (8): Charges that must be taken into the final value (USD only), Files changed, Fix, GreenX — Surcharge Intake Fix (2026-06-30), Per-B/L charges (billed once per booking, added in full to *each* container type), Problem, Root cause, Verification

### Community 67 - "Admin Page & Port Prioritization Guide"
Cohesion: 0.25
Nodes (7): 1. Popular Ports (UN/LOCODEs), 2. Boosted Countries, Admin Page & Port Prioritization Guide, 🔒 How to Access the Admin Page, ⚙️ How to Use Port Prioritization, ⚡ Important Notes, 📝 Step-by-Step Example

### Community 68 - "post"
Cohesion: 0.18
Nodes (13): approve_repair(), ApproveRepairRequest, chat_endpoint(), ChatRequest, force_stop_searches(), BaseModel, post, Chatbot helper endpoint powered by Gemini API. (+5 more)

### Community 69 - "selector_memory.py"
Cohesion: 0.24
Nodes (12): get_approved_selector(), _load_memory(), Selector Memory — stores and retrieves human-approved selector patches., Loads memory JSON file. Returns empty dict if file is missing or invalid., Saves memory dict back to JSON file., Looks up if there is an approved replacement selector for the given carrier and…, Stores an approved replacement selector., Marks any proposed selector for this step as REJECTED. (+4 more)

### Community 70 - "schemas.py"
Cohesion: 0.08
Nodes (30): Base Carrier Connector — abstract base class for all carrier connectors. Each…, Normalize CMA CGM data into QuoteSchema. Rule: include BASIC_OCEAN_FREIGHT and…, GreenX (Evergreen) Live Connector - Playwright automation., Hapag-Lloyd Prices API Connector (REST API v2.1.4). Provides real-time rate…, Mock Carrier Connector — returns realistic sample data for testing. Used when…, OOCL Live Connector â€” Playwright automation for Sailing Schedules., close_all_active_connectors(), Carrier Registry — factory for getting the right connector per carrier. When… (+22 more)

### Community 71 - "RFQParseResult"
Cohesion: 0.17
Nodes (12): parse_rfq_endpoint(), post, API routes for RFQ parsing agent., Parse a free-text RFQ email or message into a structured RateSearchRequest…, RFQParseRequest, RFQParseResult, Test Multimodal Image Input validation and parsing., Test Stress Test Scenario: "Dear Sir, Pls quote 3 x 20'FCL Singapore to… (+4 more)

### Community 72 - "deploy"
Cohesion: 0.25
Nodes (7): build, builder, deploy, restartPolicyMaxRetries, restartPolicyType, startCommand, $schema

### Community 73 - "Frontend Redesign — Componentry Design System, Workspace & Launch Intro (2026-09-07)"
Cohesion: 0.11
Nodes (17): 1. Design system foundation (`082b43a`), 2. Bugs found and fixed during the restyle, 3. Workspace + launch intro (`21ade75`), 4. Follow-up fixes (`2f9d92b`), 5. Verification, 6. Known limitations / candidate follow-ups, 7. Conventions to follow from here, Dependencies added (5, all small, no runtime lib dependency on Componentry) (+9 more)

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

### Community 79 - "json"
Cohesion: 0.15
Nodes (11): _local_fuzzy_repair(), AI Repair Agent — diagnoses Playwright step failures and suggests selector…, A local rule-based heuristic to locate reasonable buttons or inputs when Gemini…, Repair Report — generates and saves diagnosis reports on Playwright selector…, get_title(), Script to test fetching CMA CGM pricing page using Bright Data Web Access HTTP…, test_brightdata_api(), bs4 (+3 more)

### Community 80 - "fetch_port_fixes"
Cohesion: 0.40
Nodes (4): fetch_port_fixes(), Saved port name fixes, marked built in or admin-added, and the ports each…, test_endpoint_groups_recent_misses_and_lists_fixes(), run()

### Community 81 - "Design system — read before touching any UI"
Cohesion: 0.33
Nodes (5): Animation rules, Client-only preferences, Design system — read before touching any UI, This is NOT the Next.js you know, Use tokens, not raw colours

### Community 82 - "[2026-05-18 – 2026-05-19] — Railway Deployment & Docker"
Cohesion: 0.67
Nodes (3): [2026-05-18 – 2026-05-19] — Railway Deployment & Docker, Persistent Chrome Profiles on Railway Volume, Railway Deployment Setup

### Community 83 - "layout.tsx"
Cohesion: 0.22
Nodes (7): frontend_src_app_globals, instrumentSans, inter, metadata, viewport, ThemeProvider(), next-themes

### Community 84 - "port_routes.py"
Cohesion: 0.29
Nodes (9): get_countries(), get_port(), get_suggestions(), get, Get list of countries for autocomplete dropdown., Get specific port details by UN/LOCODE., Get port suggestions for autocomplete., search() (+1 more)

### Community 85 - "Infreight Sourcing Automation — Run Audit (30 Jul 2026)"
Cohesion: 0.33
Nodes (5): Expected on this machine (not automation faults), Faults (correctness), Inefficiencies (speed), Infreight Sourcing Automation — Run Audit (30 Jul 2026), Suggested priority

### Community 86 - ".filter_cheapest_in_14d_window"
Cohesion: 0.33
Nodes (5): Backward-compatible: the single cheapest card (1ST window, else 2ND)., [2026-07-03] — Robustness Review & Multi-Port Quick Search Fixes, Batch (168-route) Execution — Isolation, Lock Scope, Polling, Quick Search (multi-port RFQ) — Per-Container Pricing Was Wrong, Robustness Review (see `docs/ROBUSTNESS_REVIEW_2026-07.md`)

### Community 88 - "[2026-05-23 – 2026-05-24] — Maersk Shadow DOM & Stealth Upgrades"
Cohesion: 0.50
Nodes (4): [2026-05-23 – 2026-05-24] — Maersk Shadow DOM & Stealth Upgrades, Maersk — 2FA/CAPTCHA Human-in-the-Loop via noVNC, Maersk — Login Credential Autofill Corruption, Maersk — Shadow DOM Piercing for MDS Web Components

### Community 89 - "dependencies"
Cohesion: 0.15
Nodes (13): dependencies, class-variance-authority, clsx, exceljs, lucide-react, next, next-themes, @radix-ui/react-slot (+5 more)

### Community 91 - "test_excel_exports.js"
Cohesion: 0.33
Nodes (6): ref_fs, assert(), ExcelJS, fs, mockBatchResults, testTariffExport()

### Community 92 - "ai_agent.py"
Cohesion: 0.40
Nodes (4): AI Browser Agent — Vision-based browser automation using Gemini Flash. This…, base64, google, google_genai

### Community 93 - "[2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History"
Cohesion: 0.40
Nodes (5): [2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History, Admin User Search History & SGT GMT+8 Conversion (`AdminDashboard.tsx`), GreenX (Evergreen) Card Isolation & Surcharge Parsing (`greenx_connector.py`), Multi-Route Batch Execution Engine (`batch_engine.py`), OOCL FreightSmart 28-Day Calendar Expansion (`oocl_connector.py`)

### Community 94 - "chat_service.py"
Cohesion: 0.32
Nodes (7): get_recent_search_status_context(), handle_chat_query(), _local_chatbot_fallback(), Chat Service — manages conversational AI queries from the frontend user using…, Intelligent responder for search status, carrier guidance, air/sea info, and…, Queries the database for the most recent rate search status to give the chatbot…, Sends the chat message and history to native Gemini 2.5 Flash API. If Gemini…

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
Nodes (51): argparse, asyncio, Page Observer — captures page state (screenshot, DOM, visible text) on failure., CMA CGM Live Connector — Playwright automation. Credentials read from env:…, # NOTE: No start date fill needed — schedule page defaults to today,, Hapag-Lloyd Live Connector -- Playwright automation. Credentials read from env:…, dump_options(), main() (+43 more)

### Community 100 - "export_maersk_login.py"
Cohesion: 0.70
Nodes (4): _logged_in(), main(), _on_login_page(), Save a Maersk login from your own PC for the server to use. Opens real Google…

### Community 102 - "test_el_dekheila_maersk.py"
Cohesion: 0.40
Nodes (4): Verify non-Maersk carriers get standard UN/LOCODE or default mappings., Verify that El Dekheila maps specifically to 'Alexandria Dekheila, Egypt' for…, test_el_dekheila_maersk_override(), test_el_dekheila_other_carriers_unaffected()

### Community 103 - "test_cma_freetime.py"
Cohesion: 0.20
Nodes (3): MockCard, MockLocator, Unit test for CMA CGM demurrage and detention combined free time parsing logic.

### Community 106 - "[2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes"
Cohesion: 0.50
Nodes (4): [2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes, CMA CGM — Chrome Profile Bypass, ONE — Date Formatting & Charge Breakdown Pollution, ONE — Date Picker Pre-selection Issue

### Community 108 - "remote_worker.py"
Cohesion: 0.10
Nodes (31): Models package. Note: Individual modules can be imported directly (e.g.,…, _claim_loop(), claim_next(), delegate_and_wait(), heartbeat_once(), _heartbeat_thread(), beat(), is_worker() (+23 more)

### Community 116 - "test_hapag_schedule.py"
Cohesion: 0.50
Nodes (4): parse_hapag_card_text_mock(), Verify that multi-leg/feeder routes take the final arrival ETA and 28 days TT., Mock implementation of the JS evaluate logic inside hapag_lloyd_connector.py., test_hapag_multi_leg_schedule_extraction()

### Community 117 - "[2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash"
Cohesion: 0.40
Nodes (5): [2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash, AI RFQ Front Door & Air Freight Support, Multi-Origin & Gappy List Parsing (Sea RFQs), Native Gemini 2.5 Flash Direct API Integration, Search Form Streamlining

### Community 118 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, dev, lint, start

### Community 119 - "job_service.py"
Cohesion: 0.12
Nodes (29): get_route_health(), Get carrier search reliability & route health matrix across origin-destination…, _create_sqlite_engine(), init_db(), Create all tables on startup with automatic fallback to local SQLite if…, CarrierSearchResult, RateSearch, SQLAlchemy models for rate searches and carrier search results. (+21 more)

### Community 121 - "Architecture Overview"
Cohesion: 0.50
Nodes (4): Architecture Overview, Carrier Connector Lifecycle, Charge Classification Rules, Search Flow

### Community 123 - "create_batch_rate_search"
Cohesion: 0.33
Nodes (9): create_batch_rate_search(), _contains(), _looks_like(), _norm(), _resolve(), create_rate_search(), Execute a multi-route RFQ batch using Vertical Parallel Persistent Sessions.…, Create a new rate search and dispatch carrier jobs. (+1 more)

### Community 124 - "scrape_one_freetime.py"
Cohesion: 1.00
Nodes (3): check_and_wait_for_captcha(), login(), main()

### Community 128 - "._save_carrier_overrides"
Cohesion: 0.18
Nodes (8): Where admin-saved port name fixes are kept. Railway rebuilds /app on every…, _user_overrides_path(), test_saved_fixes_live_on_the_persistent_volume(), [2026-08-04 - 2026-08-06] — CMA CGM Dynamic RAMP/POD Rerouting, Brand Excel Styling, Port Synonym Matching & Tunnel Relays, Brand-Aligned Excel Export Styling (`excel_export.py`), CMA CGM Dynamic RAMP / POD Advisory Banner Detection (`cma_connector.py`), Dynamic Carrier Port Overrides & Admin Registry (`PortManager`, `AdminDashboard.tsx`), Railway WebSocket Tunnel Relay & Failover (`tunnel_client.py`, `run_tunnel_client.bat`, `FailoverFetch`)

### Community 131 - "eslint.config.mjs"
Cohesion: 0.50
Nodes (3): eslintConfig, eslint, eslint-config-next

### Community 133 - "[2026-05-31] — Multi-Instance Support & Charge Classification"
Cohesion: 0.67
Nodes (3): [2026-05-31] — Multi-Instance Support & Charge Classification, Charge Classification Improvements, Multi-Instance Concurrent Searches

### Community 135 - "[2026-05-20 – 2026-05-22] — Port Resolution & Frontend Improvements"
Cohesion: 0.50
Nodes (4): [2026-05-20 – 2026-05-22] — Port Resolution & Frontend Improvements, Excel Export — ETA Column & Container Type Header, Frontend Light Mode & CORS Fix, Port Resolution System

### Community 136 - "clean_selector_memory"
Cohesion: 0.67
Nodes (3): clean_selector_memory(), fixture, Wipes the selector memory JSON file before and after each test.

## Knowledge Gaps
- **326 isolated node(s):** `Config`, `install_pi.sh script`, `eslintConfig`, `nextConfig`, `name` (+321 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1015 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **25 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Changelog` connect `Changelog` to `._save_carrier_overrides`, `[2026-05-31] — Multi-Instance Support & Charge Classification`, `[2026-05-20 – 2026-05-22] — Port Resolution & Frontend Improvements`, `[2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes`, `._fs_dismiss_modals`, `[2026-05-29 – 2026-05-30] — Hapag-Lloyd Full Integration`, `[2026-05-18 – 2026-05-19] — Railway Deployment & Docker`, `[2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning`, `[2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash`, `.filter_cheapest_in_14d_window`, `[2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History`, `[2026-05-23 – 2026-05-24] — Maersk Shadow DOM & Stealth Upgrades`, `Architecture Overview`, `[2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split`, `[2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control`, `[2026-06-30] — ONE Multi-Container & Sold-Out, GreenX Surcharge Intake, Free-Time Fixes, Maersk Diagnosis`, `[2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup`?**
  _High betweenness centrality (0.309) - this node is a cross-community bridge._
- **Why does `Maersk — Free Time Extraction from Card Text` connect `Changelog` to `RateResults.tsx`?**
  _High betweenness centrality (0.266) - this node is a cross-community bridge._
- **Are the 39 inferred relationships involving `RateSearchRequest` (e.g. with `create_batch_rate_search()` and `create_rate_search()`) actually correct?**
  _`RateSearchRequest` has 39 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `cn()` (e.g. with `Reuse the primitives` and `7. Conventions to follow from here`) actually correct?**
  _`cn()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 23 inferred relationships involving `CarrierResultStatus` (e.g. with `safe_step()` and `update_carrier_status()`) actually correct?**
  _`CarrierResultStatus` has 23 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Config`, `install_pi.sh script`, `eslintConfig` to the rest of the system?**
  _326 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `CarrierResultStatus` be split into smaller, more focused modules?**
  _Cohesion score 0.036058230683090706 - nodes in this community are weakly interconnected._