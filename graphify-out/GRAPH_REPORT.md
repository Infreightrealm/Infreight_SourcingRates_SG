# Graph Report - Infreight_Sourcing_New  (2026-10-14)

## Corpus Check
- 282 files · ~1,189,737 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 27 file(s) not represented in the graph (top: (none) 10, .bat 9, .conf 2)

## Summary
- 2554 nodes · 6289 edges · 120 communities (97 shown, 23 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 366 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `6eaa718c`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- RateSearch
- BaseCarrierConnector
- cn
- user_routes.py
- auth_routes.py
- browser_cleanup.py
- SocialWidget.tsx
- api.ts
- PortManager
- ._parse_offer_response_to_quotes
- CMAConnector
- database.py
- CarrierResultStatus
- test_hapag_freetime.py
- RateSearchRequest
- test_hapag_api_connector.py
- preferences.ts
- test_rfq_agent.py
- re
- tunnel_relay/main.py
- ._verify_price_owner_selected
- datetime
- social_routes.py
- ChargeCategory
- backend/main.py
- rate_search_routes.py
- MSCConnector
- parse_rfq
- HapagLloydAPIConnector
- AIBrowserAgent
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
- BatchProgressPanel.tsx
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
- lucide-react
- 🚢 Infreight Sourcing & Ocean Rate Automation System
- MaerskConnector
- [2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split
- run_tests
- 🛠 Detailed Carrier Log
- RfqInputSection.tsx
- sort_container_types
- [2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control
- [2026-06-30] — ONE Multi-Container & Sold-Out, GreenX Surcharge Intake, Free-Time Fixes, Maersk Diagnosis
- [2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup
- diagnose_greenx_dropdown.py
- Scraper Robustness Review — July 2026
- GreenX — Surcharge Intake Fix (2026-06-30)
- Admin Page & Port Prioritization Guide
- parse_msc_modal_charges
- test_self_healing.py
- QuoteSchema
- RFQParseResult
- deploy
- export_maersk_login.py
- revoke_user_sessions
- Summary of Changes — July 20, 2026
- ._load_data
- [2026-05-29 – 2026-05-30] — Hapag-Lloyd Full Integration
- resolve_port_alias
- test_brightdata.py
- test_one_charge_override.py
- Design system — read before touching any UI
- [2026-05-18 – 2026-05-19] — Railway Deployment & Docker
- layout.tsx
- test_one_premium_override.py
- Infreight Sourcing Automation — Run Audit (30 Jul 2026)
- [2026-06-02] — Hapag-Lloyd Transshipment & Duplicate Fix
- RateLimiter
- [2026-05-23 – 2026-05-24] — Maersk Shadow DOM & Stealth Upgrades
- test_excel_exports.js
- [2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History
- ._lookup_freetime
- frontend/README.md
- test_js.js
- get_me
- os
- fill_container_card
- .extract_charge_breakdown
- MockCard
- Working in this repository
- [2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes
- install_pi.sh
- remote_worker.py
- postcss.config.mjs
- [2026-07-03] — Robustness Review & Multi-Port Quick Search Fixes
- require_admin
- e2e_downloaded_multisheet_28ec47f9.md
- test_panama_canal_surcharge.py
- e2e_downloaded_tariff_d21a0cb7.md
- [2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash
- pytest
- ambiguous_python_import_b35980c0aa01

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

## Communities (120 total, 23 thin omitted)

### Community 0 - "RateSearch"
Cohesion: 0.08
Nodes (46): get_recent_search_status_context(), Queries the database for the most recent rate search status to give the chatbot…, get_route_health(), Get carrier search reliability & route health matrix across origin-destination…, get_async_session_maker(), init_db(), Get the session maker for use outside of FastAPI dependency injection., Create all tables on startup with automatic fallback to local SQLite if… (+38 more)

### Community 1 - "BaseCarrierConnector"
Cohesion: 0.06
Nodes (28): ABC, BaseCarrierConnector, NotAvailableConnector, Any, Open the price breakdown / detail view for a specific quote. Args: quote_ref:…, Extract individual charge line items from the price breakdown. Returns: List of…, Normalize extracted data into a QuoteSchema using the normalizer. Args:…, Abstract base class for carrier portal connectors. (+20 more)

### Community 2 - "cn"
Cohesion: 0.07
Nodes (47): Reuse the primitives, New primitives — `frontend/src/components/ui/`, SearchCompletionModal(), SearchCompletionModalProps, Segmented(), Badge(), badgeVariants, Dot() (+39 more)

### Community 3 - "user_routes.py"
Cohesion: 0.06
Nodes (84): get_current_user(), Dependency that strictly requires an authenticated active member., admin_delete_user(), AdminLoginRequest, approve_user(), CarrierOverrideRequest, CarrierSwitchRequest, Config (+76 more)

### Community 4 - "auth_routes.py"
Cohesion: 0.06
Nodes (75): clear_session_cookie(), get_current_user_optional(), login(), LoginRequest, logout(), AsyncSession, BaseModel, post (+67 more)

### Community 5 - "browser_cleanup.py"
Cohesion: 0.11
Nodes (33): _is_chrome(), _is_playwright_driver(), _kill(), kill_profile_browsers(), _proc_supported(), Cleanup for Chrome browsers and temporary profiles that a failed close leaves…, Kill every automated Chrome and Playwright driver. Only call this when no…, Delete per-search profile copies ("chrome_profile_<carrier>_tmp_<id>") and… (+25 more)

### Community 6 - "SocialWidget.tsx"
Cohesion: 0.10
Nodes (34): ACCENT_COLORS, errorMessage(), relativeTime(), resizeImageToDataUrl(), SocialWidget(), SocialWidgetProps, EMOJI_GROUPS, EmojiPicker() (+26 more)

### Community 7 - "api.ts"
Cohesion: 0.08
Nodes (63): AdminDashboard(), LoginContent(), HomeContent(), AdminCarriers(), PROFILE_NAMES, when(), LoginModal(), LoginModalProps (+55 more)

### Community 8 - "PortManager"
Cohesion: 0.06
Nodes (49): get_countries(), get_port(), get_suggestions(), get, Get list of countries for autocomplete dropdown., Get specific port details by UN/LOCODE., Get port suggestions for autocomplete., search() (+41 more)

### Community 9 - "._parse_offer_response_to_quotes"
Cohesion: 0.13
Nodes (9): Any, AsyncClient, Constructs OpenAPI compliant OfferRequest payload., Queries Hapag-Lloyd DCSA Commercial Schedules API (v1.0.2) to retrieve point-…, Correlates an offer from the Prices API to a physical solution in DCSA…, Maps a Prices API rate onto the categories the portal scraper produces (freight…, Leg locations are UnLocation/Facility objects per the spec; tolerate plain…, Renders a graduated weight tier (e.g. Heavy Lift: 18-99 TON) in the portal's… (+1 more)

### Community 10 - "CMAConnector"
Cohesion: 0.07
Nodes (19): CMAConnector, Ensures 'Ramp' is explicitly selected under 'Type of location' toggle buttons…, Scans for Route, POL (Port of Loading), or POD (Port of Discharge) dropdown…, Clears the currently selected Destination port tag/card, re-types the locode,…, Dynamically extracts any recommended 5-letter POD LOCODE mentioned in the…, Detects if CMA CGM displayed an advisory banner message: "Looking for AEJEA or…, Handles the 'Customer account' -> 'Role (you are acting as)' dropdown on CMA…, Repeatedly clicks 'More results' if visible to load ALL quotes on the page. (+11 more)

### Community 11 - "database.py"
Cohesion: 0.08
Nodes (31): alembic, _local_chatbot_fallback(), Chat Service — manages conversational AI queries from the frontend user using…, Intelligent responder for search status, carrier guidance, air/sea info, and…, get_sync_url(), run_migrations_offline(), run_migrations_online(), _create_sqlite_engine() (+23 more)

### Community 12 - "CarrierResultStatus"
Cohesion: 0.08
Nodes (19): Override to immediately return CONNECTOR_NOT_AVAILABLE., Fill in the carrier's search form and submit a quote search. Args: request: The…, Required abstract method implementation; delegates to run_full_search., Batch (RFQ) mode: the base implementation drives a browser page, so answer from…, Sends a single POST /prices request with rate-limiting and error handling., Called by job_service once per container type (request.container_type). All…, Executes full rate search against Hapag-Lloyd Prices API. Queries each…, _generate_maersk_mock_quotes() (+11 more)

### Community 13 - "test_hapag_freetime.py"
Cohesion: 0.19
Nodes (15): _apply_freetime_to_quote(), freetime_days(), match_freetime_entry(), Any, Destination free time from config/hapag_freetime.json, shared by the Hapag-…, Days for this container from a table entry ({"20GP": n, "40GP": n} or a bare…, The table entry whose country name appears in `text` as whole words. Whole…, days() (+7 more)

### Community 14 - "RateSearchRequest"
Cohesion: 0.06
Nodes (36): OOCLConnector, parse_oocl_date(), Serves one container-type cycle from the cached merged quote set: -…, One crawl serves all container-type cycles (cached), combining: 1. Sailing…, Attempts to automatically click the Cloudflare Turnstile 'Verify you are human'…, Public oocl.com Chromium sailing schedule crawl bypassed per directive. All…, RateSearchRequest, CMA CGM end-to-end test — login + search + extract quotes. (+28 more)

### Community 15 - "test_hapag_api_connector.py"
Cohesion: 0.23
Nodes (11): get_connector(), Get the appropriate connector for a carrier. If USE_MOCK_CARRIERS=true: returns…, main(), Standalone Test & Verification Suite for Hapag-Lloyd Prices REST API Connector.…, test_dcsa_commercial_schedules_cross_validation(), test_locode_resolution(), test_payload_generation(), test_registry_integration() (+3 more)

### Community 16 - "preferences.ts"
Cohesion: 0.10
Nodes (32): SearchHistoryItem, derive(), Derived, startOfDay(), UsageStats(), ChoiceCard(), Toggle(), WorkspacePanel() (+24 more)

### Community 17 - "test_rfq_agent.py"
Cohesion: 0.10
Nodes (28): asyncio, Unit tests for the Gemini AI RFQ Agent service (parse_rfq). Includes…, Test Image 2: Air rate request generates 3 drafts to Glenn (AWOT), Jing Hui…, Test Image 4: Steel Plate ex Pasir Gudang / Tanjung Pelepas for 20' & 40'., Test Guardrail: Detects Reefer container request and returns unsupported_cargo…, Test Guardrail: Detects LCL request., Test OpenFlights 6,072 IATA airport dataset and shorthand alias resolution., Test Pak Shaun email: "Hi team, need rate for 10x20GP from PK to JKT. Urgent… (+20 more)

### Community 18 - "re"
Cohesion: 0.07
Nodes (12): AI Browser Agent — Vision-based browser automation using Gemini Flash. This…, parse_hapag_pdf(), scrape_hapag_freetime(), check_and_wait_for_captcha(), login(), main(), base64, google (+4 more)

### Community 19 - "tunnel_relay/main.py"
Cohesion: 0.25
Nodes (8): api_route, fastapi_middleware_cors, health(), get, Request, websocket, relay_request(), websocket_endpoint()

### Community 20 - "._verify_price_owner_selected"
Cohesion: 0.25
Nodes (7): Verifies the "I am the price owner" radio is genuinely checked, piercing shadow…, [2026-07-03] — OOCL FreightSmart Autoclear, Hapag Price Leak & Redirect fixes, Maersk Cache Scoping, Dallas Overrides, Hapag-Lloyd — Price Leaks, Column Matching, and Redirect Recovery, Maersk — 0.0-USD / "Not Open" Card Flakiness (the "Quotes Found but Empty Excel" root causes), Maersk — Caching Scope & Selector Tuning, OOCL — FreightSmart Popup Dismissals & Input Lock Serialization, Ports — Hardcoded Dallas Override

### Community 21 - "datetime"
Cohesion: 0.08
Nodes (16): GreenXConnector, date, GreenX (Evergreen) Live Connector - Playwright automation., Overrides base search runner to query all 3 sizes at once and cache the…, Type a LOCODE into the autocomplete field and click the first visible dropdown…, Find quantity input next to or below label_text and fill it., Find the exact individual quote card container row encompassing dates, rates,…, Dismiss any cookie/alert modal that would intercept pointer events. (+8 more)

### Community 22 - "social_routes.py"
Cohesion: 0.10
Nodes (31): get_conversation(), list_colleagues(), poke_colleague(), PokeRequest, AsyncSession, BaseModel, delete, get (+23 more)

### Community 23 - "ChargeCategory"
Cohesion: 0.15
Nodes (26): CarrierCode, ChargeCategory, classify_charge(), Charge Classifier — rule-based classification of freight charge line items.…, Classify a charge line item based on its name, amount, section heading, and…, Tests for charge classifier., test_basic_ocean_freight(), test_cwx_heavy_weight_charge() (+18 more)

### Community 24 - "backend/main.py"
Cohesion: 0.07
Nodes (28): health(), lifespan(), get, websocket, Infreight Ocean Carrier Rate Automation — FastAPI Application. Main entry point…, Check if the VNC viewer is available (production only, where Xvfb runs)., Proxy WebSocket connections to legacy local x11vnc at localhost:5900., Proxy WebSocket connections to specific carrier x11vnc servers. (+20 more)

### Community 25 - "rate_search_routes.py"
Cohesion: 0.06
Nodes (55): approve_repair(), ApproveRepairRequest, carrier_switch_status(), chat_endpoint(), ChatRequest, create_batch_rate_search(), _contains(), _looks_like() (+47 more)

### Community 26 - "MSCConnector"
Cohesion: 0.17
Nodes (7): format_to_iso_date(), MSCConnector, Playwright-based automation for MSC (Mediterranean Shipping Company)., Handles the MSC login flow., Clicks Instant Quote, fills form, clicks Search., Detects and clicks the 'Ramp' delivery/haulage option if MSC displays Ramp /…, Parse '14 Jun 2026' to 'YYYY-MM-DD

### Community 27 - "parse_rfq"
Cohesion: 0.13
Nodes (25): _call_native_gemini_api(), _detect_booking_confirmation(), _detect_dual_mode_enquiry(), _detect_mode_by_hierarchy(), _detect_unsupported_cargo(), _extract_20gp_weight_priority(), generate_dual_air_drafts(), _load_airport_aliases_config() (+17 more)

### Community 28 - "HapagLloydAPIConnector"
Cohesion: 0.13
Nodes (6): HapagLloydAPIConnector, Direct REST API connector for Hapag-Lloyd Prices API v2.1.4., API connectors do not require browser login sessions., No browser session to reset between batch routes., Resolves a free-text port name or string (e.g. 'Singapore', 'Hamburg, Germany…, Hapag-Lloyd Prices API requires earliestDepartureDate to be at least 4 calendar…

### Community 29 - "AIBrowserAgent"
Cohesion: 0.12
Nodes (16): AIBrowserAgent, Capture the current page as a PNG screenshot., Build the prompt with task description and action history., Parse Gemini's response into an action dict., Call Gemini API with exponential backoff retry., Execute a parsed action on the browser page., Detect if the agent is stuck repeating the same action., Find all visible interactive elements and format them as a prompt guide. (+8 more)

### Community 30 - "job_service.py"
Cohesion: 0.07
Nodes (39): Base, CarrierSearchResult, Tracks the result of searching a specific carrier for a rate search., Job Service — orchestrates carrier search jobs. Creates background tasks per…, Copy the connector's "port not found" note onto the result row, if it made one., _store_port_not_found(), Admin carrier on/off switch: stored on the volume, and a switched-off carrier…, test_switched_off_carrier_is_skipped() (+31 more)

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
Cohesion: 0.09
Nodes (22): [2026-05-20 – 2026-05-22] — Port Resolution & Frontend Improvements, [2026-05-25 – 2026-05-26] — VNC Display Isolation & Proxy Integration, [2026-05-31] — Multi-Instance Support & Charge Classification, [2026-06-01] — Hapag-Lloyd Sold Out Detection & Date Parsing, [2026-07-08] — OOCL E-Quote Calendar Navigation, cheapest E-Spot selection, and E-Quote/E-Spot isolation refinements, [2026-07-09] — Hapag-Lloyd Quick Quotes pairing and selection simplification, Architecture Overview, Bright Data ISP Proxy Integration (+14 more)

### Community 35 - "admin/page.tsx"
Cohesion: 0.06
Nodes (50): UserRecord, AdminAnalytics, AdminOverview(), AdminOverviewProps, AdminOverviewUser, AnalyticsRange, Attention, attentionItems() (+42 more)

### Community 36 - "package.json"
Cohesion: 0.04
Nodes (46): eslintConfig, dependencies, class-variance-authority, clsx, exceljs, lucide-react, next, next-themes (+38 more)

### Community 37 - "carrier_switches.py"
Cohesion: 0.35
Nodes (10): get_switches(), off_message(), _path(), Admin on/off switch per carrier, for when a carrier's site is down or under…, Every switchable carrier: {"enabled", "reason", "updated_by", "updated_at"}; on…, The message for a switched-off carrier's result, or None when it is on., _read(), set_switch() (+2 more)

### Community 38 - "RateResults.tsx"
Cohesion: 0.07
Nodes (58): LiveSearchProgressProps, QuoteBreakdownDrawer(), QuoteBreakdownDrawerProps, Breakdown(), ChargeList(), dateValue(), freeTimeText(), isSoldOut() (+50 more)

### Community 39 - "SearchQueueManager"
Cohesion: 0.12
Nodes (11): Lock, Marks a search as completed internally so we can track the auto-release timeout., Called periodically in a background task to check if the user has held the lock…, Forcefully clears all queued searches and the active lock. Useful for…, Returns or creates an asyncio.Lock for a specific carrier code to prevent…, Adds a search to the queue and waits until it becomes the active search. Event-…, Singleton manager to enforce a FIFO queue for rate searches. Since web scraping…, Returns the current position of the search in the queue. 0 means it is the… (+3 more)

### Community 40 - "BatchProgressPanel.tsx"
Cohesion: 0.31
Nodes (8): BatchProgressPanel(), BatchProgressPanelProps, cheapest(), Filter, lanePhase(), Phase, PHASE_STYLE, BatchRouteResult

### Community 41 - "app/page.tsx"
Cohesion: 0.11
Nodes (23): nextConfig, 6. Known limitations / candidate follow-ups, AppHeader(), AppHeaderProps, initials(), systemStatus(), BackendConfigModal(), BackendConfigModalProps (+15 more)

### Community 42 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 43 - "._fs_dismiss_modals"
Cohesion: 0.07
Nodes (25): clean_vessel_name(), _dismiss_once(), _click_date_strip_item(), _open_calendar(), _parse_date(), Event, Lock, Parses one FreightSmart result card's inner text into a raw row dict. Text-… (+17 more)

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
Cohesion: 0.06
Nodes (31): HapagLloydConnector, HapagServiceUnavailableException, Exception, Normalize various date formats (e.g. 2026-05-31, 31.05.2026, 31 May 2026, 31…, Robustly selects options from Hapag-Lloyd custom dropdown lists. Types the…, Detects the Microsoft B2C identity/OAuth login page. Hapag can silently bounce…, Guards against the session-expiry-mid-crawl failure mode: the existing redirect…, Crawls Hapag-Lloyd sailing schedules from the Schedule tab. (+23 more)

### Community 49 - "[2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning"
Cohesion: 0.17
Nodes (10): get_booking_start_date(), date, Applies the business rules and pairs FreightSmart prices with crawled…, [2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning, GreenX — "No Quotes" Reported While Quotes Visibly Loaded in VNC, Hapag-Lloyd — Configurable Pacing & Redundant-Wait Removal, Job Scheduler — Concurrency Default, Maersk — Regression: Other-Container-Type Sizes Went "Sold Out" in Multi-Container Searches (+2 more)

### Community 50 - "[2026-06-03] — CMA CGM Routing & Free Time Extraction"
Cohesion: 0.50
Nodes (4): [2026-06-03] — CMA CGM Routing & Free Time Extraction, CMA CGM — Import Free Time from D&D Tab, CMA CGM — Routing Detection (Direct vs Transit), Maersk — Free Time Extraction from Card Text

### Community 51 - "carrier_sessions.py"
Cohesion: 0.11
Nodes (22): clean_storage_state(), delete_session(), load_session(), _on_domain(), _path(), Saved carrier logins uploaded by an admin. An admin logs in to a carrier in…, What the admin screen shows: who uploaded it, when, and how much it holds., Keep only this carrier's cookies and localStorage, in the shape add_cookies… (+14 more)

### Community 52 - "LiveSearchProgress.tsx"
Cohesion: 0.09
Nodes (29): ChatWidget(), ChatWidgetProps, Message, ACTION_STATUSES, ChipModel, describe(), EMPTY_STATUSES, formatElapsed() (+21 more)

### Community 53 - "lucide-react"
Cohesion: 0.09
Nodes (38): 0. The one invariant, 1. Design system foundation (`082b43a`), 2. Bugs found and fixed during the restyle, 3. Workspace + launch intro (`21ade75`), 4. Follow-up fixes (`2f9d92b`), 5. Verification, 7. Conventions to follow from here, Dependencies added (5, all small, no runtime lib dependency on Componentry) (+30 more)

### Community 54 - "🚢 Infreight Sourcing & Ocean Rate Automation System"
Cohesion: 0.14
Nodes (13): 1. Multi-Carrier Automation Engine, 2. Intelligent Surcharge & Charge Classifier Engine (`charge_classifier.py`), 3. Container Comparison Matrix & Excel Export Engine, 🚢 Infreight Sourcing & Ocean Rate Automation System, 🌟 Key Capabilities, 📄 License & Confidentiality, Prerequisites, 🛠️ Project Structure (+5 more)

### Community 55 - "MaerskConnector"
Cohesion: 0.06
Nodes (21): MaerskConnector, Fills an autocomplete field using the proven original element-level…, Execute the full search flow with Progressive Lazy Loading: 1. Login 2. Search…, Extracts freetime, demurrage, and detention from the 'Import D&D fees' tab…, Extracts the routing details from the 'Route & other details' accordion.…, Extracts the port/city name by removing any UN/LOCODE parentheses (e.g.,…, Maps standard container search codes (e.g. 'DRY 20', '20GP') to Maersk Spot…, Scores a Maersk autocomplete dropdown suggestion. NOTE: The nested/indented… (+13 more)

### Community 56 - "[2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split"
Cohesion: 0.15
Nodes (13): G2 Stress Test: "Hi, Please book the below as per your quote ref INF-2026-0842:…, H1 Stress Test: Table with 2 distinct rows: Row 1: POL Singapore, POD Jakarta,…, test_g2_booking_confirmation_guardrail(), test_h1_table_deduplication_two_pairs(), [2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split, Booking Confirmation / Instructions Intercept Guardrail G2 (`rfq_agent.py` & `RfqInputSection.tsx`), Commercial Sales Desk Intelligence (`sales_notes`), Deterministic Port Alias Resolver (`ports_aliases.json`) (+5 more)

### Community 58 - "🛠 Detailed Carrier Log"
Cohesion: 0.15
Nodes (12): 🛠 Detailed Carrier Log, 🟢 GreenX, 🟠 Hapag-Lloyd, Infreight Ocean Carrier Rate Automation — Development Log, 🚀 Key Highlights & Architectural Changes, 🔌 Local Laptop Deployment (Self-Hosted Worker), 🔵 Maersk, 💗 ONE (Ocean Network Express) (+4 more)

### Community 59 - "RfqInputSection.tsx"
Cohesion: 0.18
Nodes (13): RateSearchFormProps, DEMO_EXAMPLES, RfqInputSection(), RfqInputSectionProps, Box(), fieldName(), laneFlags(), RfqLane (+5 more)

### Community 60 - "sort_container_types"
Cohesion: 0.40
Nodes (4): Sort container types in standard order: DRY 20 (20GP) -> DRY 40 (40GP) -> DRY…, sort_container_types(), test_container_types_standard_ordering(), model_validator

### Community 61 - "[2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control"
Cohesion: 0.40
Nodes (5): [2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control, Concurrency Limit Queue & Admin Control Panel, MSC — Mediterranean Shipping Company Connector Implementation, ONE — Inbound Free Time Swap & Scraper Upgrade, OOCL — Orient Overseas Container Line Connector Implementation

### Community 62 - "[2026-06-30] — ONE Multi-Container & Sold-Out, GreenX Surcharge Intake, Free-Time Fixes, Maersk Diagnosis"
Cohesion: 0.25
Nodes (8): [2026-06-30] — ONE Multi-Container & Sold-Out, GreenX Surcharge Intake, Free-Time Fixes, Maersk Diagnosis, Free Time — GreenX blank, ONE India wrong, Hapag Nhava Sheva unresolved (Singapore → Nhava Sheva), GreenX — Only Basic Ocean Freight & LSS Folded Into Final Value, MAERSK — "Quotes Found" but Empty Excel (Diagnosis), ONE — All-Container-Type Search Returning 0 Quotes, ONE — Multi-Container Breakdown Triple-Counted / Inflated Final Value, ONE — Sold-Out ("Notify Me") Sailings Appearing as Quotes, Performance/Reliability — Stop Copying Chrome Caches During Profile Clone/Sync

### Community 63 - "[2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup"
Cohesion: 0.22
Nodes (8): [2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup, Chromium Cache Auto-Cleanup (Railway Storage Bloat Prevention), CMA CGM — 30-Second Timeout on Sold Out Cards, CMA CGM — Free Time Regex Too Strict, CMA CGM — Routing Regex Not Matching "via LEKKI, LA, NG", Excel Export — Routing & Free Time Columns Always Empty, Excel Export — Sold Out Rows Not Showing, Maersk — Hardcoded Port Overrides

### Community 64 - "diagnose_greenx_dropdown.py"
Cohesion: 0.67
Nodes (3): dump_options(), main(), Diagnostic: dump ALL dropdown options (text + innerHTML) when typing 'DEHAM'…

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
Cohesion: 0.06
Nodes (49): _local_fuzzy_repair(), AI Repair Agent — diagnoses Playwright step failures and suggests selector…, A local rule-based heuristic to locate reasonable buttons or inputs when Gemini…, Analyzes the failure context and DOM content to suggest a selector repair. Uses…, suggest_fix(), handle_chat_query(), Sends the chat message and history to native Gemini 2.5 Flash API. If Gemini…, capture_failure_context() (+41 more)

### Community 70 - "QuoteSchema"
Cohesion: 0.12
Nodes (24): Page Observer — captures page state (screenshot, DOM, visible text) on failure., Base Carrier Connector — abstract base class for all carrier connectors. Each…, CMA CGM Live Connector — Playwright automation. Credentials read from env:…, Normalize CMA CGM data into QuoteSchema. Rule: include BASIC_OCEAN_FREIGHT and…, Hapag-Lloyd Prices API Connector (REST API v2.1.4). Provides real-time rate…, # NOTE: No start date fill needed — schedule page defaults to today,, Hapag-Lloyd Live Connector -- Playwright automation. Credentials read from env:…, Splits a single raw multi-container quote card into multiple QuoteSchema… (+16 more)

### Community 71 - "RFQParseResult"
Cohesion: 0.17
Nodes (12): parse_rfq_endpoint(), post, API routes for RFQ parsing agent., Parse a free-text RFQ email or message into a structured RateSearchRequest…, RFQParseRequest, RFQParseResult, Test scenario where container size (20GP, 40GP, 40HQ) is not specified in…, Test scenario where email contains both Air freight and Ocean freight requests:… (+4 more)

### Community 72 - "deploy"
Cohesion: 0.25
Nodes (7): build, builder, deploy, restartPolicyMaxRetries, restartPolicyType, startCommand, $schema

### Community 73 - "export_maersk_login.py"
Cohesion: 0.70
Nodes (4): _logged_in(), main(), _on_login_page(), Save a Maersk login from your own PC for the server to use. Opens real Google…

### Community 74 - "revoke_user_sessions"
Cohesion: 0.67
Nodes (3): UUID, Revoke all sessions belonging to a user (used on disable, delete, or password…, revoke_user_sessions()

### Community 75 - "Summary of Changes — July 20, 2026"
Cohesion: 0.29
Nodes (6): 1. AI RFQ Front Door & Air Freight Support (Phase A), 2. Multi-Origin & Gappy List Parsing for Sea RFQs (Phase B), 3. Search Form Streamlining (Form Input Restrictions), 4. Native Gemini 2.5 Flash API & Chatbot Resiliency, 5. Verification & Test Suite, Summary of Changes — July 20, 2026

### Community 76 - "._load_data"
Cohesion: 0.12
Nodes (8): Where admin-saved port name fixes are kept. Railway rebuilds /app on every…, _user_overrides_path(), test_saved_fixes_live_on_the_persistent_volume(), [2026-08-04 - 2026-08-06] — CMA CGM Dynamic RAMP/POD Rerouting, Brand Excel Styling, Port Synonym Matching & Tunnel Relays, Brand-Aligned Excel Export Styling (`excel_export.py`), CMA CGM Dynamic RAMP / POD Advisory Banner Detection (`cma_connector.py`), Dynamic Carrier Port Overrides & Admin Registry (`PortManager`, `AdminDashboard.tsx`), Railway WebSocket Tunnel Relay & Failover (`tunnel_client.py`, `run_tunnel_client.bat`, `FailoverFetch`)

### Community 77 - "[2026-05-29 – 2026-05-30] — Hapag-Lloyd Full Integration"
Cohesion: 0.40
Nodes (5): [2026-05-29 – 2026-05-30] — Hapag-Lloyd Full Integration, Hapag-Lloyd — Dropdown Autocomplete Issues, Hapag-Lloyd — Live Connector Implementation, Hapag-Lloyd — Onboarding Modal Blocking Form Interaction, Hapag-Lloyd — Search Button Selector Failures

### Community 78 - "resolve_port_alias"
Cohesion: 0.33
Nodes (6): _load_port_aliases_config(), Deterministically resolves a port string against ports_aliases.json and the…, resolve_port_alias(), Test that resolve_port_alias cleans 'City, Country' and parenthetical notes to…, test_resolve_city_country_format_to_clean_database_port_name(), Clean Search Dropdown Port Name Resolution (`rfq_agent.py` & `port_manager.py`)

### Community 79 - "test_brightdata.py"
Cohesion: 0.40
Nodes (5): get_title(), Script to test fetching CMA CGM pricing page using Bright Data Web Access HTTP…, test_brightdata_api(), urllib_error, urllib_request

### Community 80 - "test_one_charge_override.py"
Cohesion: 0.40
Nodes (3): MockCard, Unit test for ONE connector charge classification override., test_emergency_surcharge_override()

### Community 81 - "Design system — read before touching any UI"
Cohesion: 0.33
Nodes (5): Animation rules, Client-only preferences, Design system — read before touching any UI, This is NOT the Next.js you know, Use tokens, not raw colours

### Community 82 - "[2026-05-18 – 2026-05-19] — Railway Deployment & Docker"
Cohesion: 0.67
Nodes (3): [2026-05-18 – 2026-05-19] — Railway Deployment & Docker, Persistent Chrome Profiles on Railway Volume, Railway Deployment Setup

### Community 83 - "layout.tsx"
Cohesion: 0.25
Nodes (6): frontend_src_app_globals, instrumentSans, inter, metadata, viewport, ThemeProvider()

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

### Community 91 - "test_excel_exports.js"
Cohesion: 0.33
Nodes (6): ref_fs, assert(), ExcelJS, fs, mockBatchResults, testTariffExport()

### Community 93 - "[2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History"
Cohesion: 0.40
Nodes (5): [2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History, Admin User Search History & SGT GMT+8 Conversion (`AdminDashboard.tsx`), GreenX (Evergreen) Card Isolation & Surcharge Parsing (`greenx_connector.py`), Multi-Route Batch Execution Engine (`batch_engine.py`), OOCL FreightSmart 28-Day Calendar Expansion (`oocl_connector.py`)

### Community 96 - "frontend/README.md"
Cohesion: 0.50
Nodes (3): Deploy on Vercel, Getting Started, Learn More

### Community 98 - "get_me"
Cohesion: 0.67
Nodes (3): get_me(), get, Get profile of currently signed-in user.

### Community 99 - "os"
Cohesion: 0.05
Nodes (42): argparse, asyncio, Interactive Headed Login Helper for Maersk. Opens real Chrome using the…, Interactive Headed Login Helper for ONE (Ocean Network Express). Opens Chrome…, Hapag-Lloyd form inspector., Inspection script to dump the Maersk autocomplete dropdown structure., Pydantic schemas for API request/response validation., Wrapper script to set Windows event loop policy before starting Uvicorn. This… (+34 more)

### Community 106 - "[2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes"
Cohesion: 0.50
Nodes (4): [2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes, CMA CGM — Chrome Profile Bypass, ONE — Date Formatting & Charge Breakdown Pollution, ONE — Date Picker Pre-selection Issue

### Community 108 - "remote_worker.py"
Cohesion: 0.09
Nodes (32): Models package. Note: Individual modules can be imported directly (e.g.,…, A worker machine (e.g. the office laptop) that runs some carriers' searches., WorkerHeartbeat, _claim_loop(), claim_next(), delegate_and_wait(), heartbeat_once(), _heartbeat_thread() (+24 more)

### Community 117 - "[2026-07-03] — Robustness Review & Multi-Port Quick Search Fixes"
Cohesion: 0.67
Nodes (3): [2026-07-03] — Robustness Review & Multi-Port Quick Search Fixes, Batch (168-route) Execution — Isolation, Lock Scope, Polling, Robustness Review (see `docs/ROBUSTNESS_REVIEW_2026-07.md`)

### Community 124 - "test_panama_canal_surcharge.py"
Cohesion: 0.11
Nodes (22): is_weight_surcharge_applicable(), Evaluates whether a weight-tier or overweight surcharge is applicable for the…, calculate_final_freight_value(), classify_and_organize_charges(), Takes raw charge line items and classifies them. Args: raw_charges: list of…, Calculate the final freight value from a list of classified charges. Args:…, Tests for normalizer / final freight value calculator., test_basic_calculation() (+14 more)

### Community 126 - "[2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash"
Cohesion: 0.40
Nodes (5): [2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash, AI RFQ Front Door & Air Freight Support, Multi-Origin & Gappy List Parsing (Sea RFQs), Native Gemini 2.5 Flash Direct API Integration, Search Form Streamlining

### Community 127 - "pytest"
Cohesion: 0.12
Nodes (12): asyncio, Integration tests for authentication, legacy user password setup, pending…, test_full_auth_lifecycle(), parse_hapag_card_text_mock(), Verify that multi-leg/feeder routes take the final arrival ETA and 28 days TT., Mock implementation of the JS evaluate logic inside hapag_lloyd_connector.py., test_hapag_multi_leg_schedule_extraction(), asyncio (+4 more)

## Knowledge Gaps
- **326 isolated node(s):** `Config`, `install_pi.sh script`, `eslintConfig`, `nextConfig`, `name` (+321 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1005 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **23 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Changelog` connect `Changelog` to `[2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split`, `[2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes`, `._fs_dismiss_modals`, `._load_data`, `[2026-05-29 – 2026-05-30] — Hapag-Lloyd Full Integration`, `[2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning`, `[2026-05-18 – 2026-05-19] — Railway Deployment & Docker`, `[2026-06-03] — CMA CGM Routing & Free Time Extraction`, `._verify_price_owner_selected`, `[2026-07-03] — Robustness Review & Multi-Port Quick Search Fixes`, `[2026-06-02] — Hapag-Lloyd Transshipment & Duplicate Fix`, `[2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History`, `[2026-05-23 – 2026-05-24] — Maersk Shadow DOM & Stealth Upgrades`, `[2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash`, `[2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control`, `[2026-06-30] — ONE Multi-Container & Sold-Out, GreenX Surcharge Intake, Free-Time Fixes, Maersk Diagnosis`, `[2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup`?**
  _High betweenness centrality (0.321) - this node is a cross-community bridge._
- **Why does `[2026-06-03] — CMA CGM Routing & Free Time Extraction` connect `[2026-06-03] — CMA CGM Routing & Free Time Extraction` to `Changelog`?**
  _High betweenness centrality (0.285) - this node is a cross-community bridge._
- **Why does `Maersk — Free Time Extraction from Card Text` connect `[2026-06-03] — CMA CGM Routing & Free Time Extraction` to `RateResults.tsx`?**
  _High betweenness centrality (0.284) - this node is a cross-community bridge._
- **Are the 37 inferred relationships involving `RateSearchRequest` (e.g. with `create_batch_rate_search()` and `create_rate_search()`) actually correct?**
  _`RateSearchRequest` has 37 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `cn()` (e.g. with `Reuse the primitives` and `7. Conventions to follow from here`) actually correct?**
  _`cn()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 23 inferred relationships involving `CarrierResultStatus` (e.g. with `safe_step()` and `update_carrier_status()`) actually correct?**
  _`CarrierResultStatus` has 23 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Config`, `install_pi.sh script`, `eslintConfig` to the rest of the system?**
  _326 weakly-connected nodes found - possible documentation gaps or missing edges._