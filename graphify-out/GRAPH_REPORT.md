# Graph Report - Infreight_SourcingRates_SG  (2026-10-09)

## Corpus Check
- 252 files · ~1,167,425 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 25 file(s) not represented in the graph (top: (none) 10, .bat 8, .conf 2)

## Summary
- 2475 nodes · 6121 edges · 121 communities (103 shown, 18 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 352 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b39f219b`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- job_service.py
- BaseCarrierConnector
- cn
- User
- auth_routes.py
- browser_cleanup.py
- app/page.tsx
- api.ts
- PortManager
- test_remote_worker.py
- CMAConnector
- get_async_session_maker
- selector_memory.py
- user_routes.py
- RateSearchRequest
- CarrierResultStatus
- preferences.ts
- test_rfq_agent.py
- tunnel_relay/main.py
- SocialWidget.tsx
- AdminUsers.tsx
- GreenXConnector
- social_routes.py
- ChargeCategory
- backend/main.py
- rate_search_routes.py
- MSCConnector
- parse_rfq
- lucide-react
- AIBrowserAgent
- database.py
- ONEConnector
- _Page
- Engineering Report: Sourcing Portal Enhancements & Scraping Pipeline Stability
- Changelog
- AdminOverview.tsx
- package.json
- dependencies
- RateResults.tsx
- SearchQueueManager
- hapag_lloyd_connector.py
- Frontend Redesign — Componentry Design System, Workspace & Launch Intro (2026-09-07)
- compilerOptions
- ._fs_dismiss_modals
- test_carrier_timeout.py
- devDependencies
- dithered-logo.tsx
- 👥 The 5 Agent Roles
- HapagLloydConnector
- MockCarrierConnector
- [2026-06-03] — CMA CGM Routing & Free Time Extraction
- carrier_sessions.py
- schemas.py
- test_hapag_freetime.py
- 🚢 Infreight Sourcing & Ocean Rate Automation System
- MaerskConnector
- [2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split
- CarrierSearchResult
- 🛠 Detailed Carrier Log
- json
- CurrencyManager
- time
- [2026-06-30] — ONE Multi-Container & Sold-Out, GreenX Surcharge Intake, Free-Time Fixes, Maersk Diagnosis
- [2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup
- tunnel_client.py
- maersk_proxy_settings
- GreenX — Surcharge Intake Fix (2026-06-30)
- Admin Page & Port Prioritization Guide
- [2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning
- test_self_healing.py
- sort_container_types
- test_one_charge_override.py
- deploy
- export_maersk_login.py
- [2026-08-04 - 2026-08-06] — CMA CGM Dynamic RAMP/POD Rerouting, Brand Excel Styling, Port Synonym Matching & Tunnel Relays
- Summary of Changes — July 20, 2026
- .validate_currency
- [2026-05-29 – 2026-05-30] — Hapag-Lloyd Full Integration
- resolve_port_alias
- test_brightdata.py
- MockCard
- Design system — read before touching any UI
- ai_repair_agent.py
- layout.tsx
- scrape_one_freetime.py
- test_hapag_schedule_debug.py
- test_rate_search_api.py
- RateLimiter
- asyncio
- run_6_ports_direct.py
- maersk_connector.py
- ref_fs
- [2026-06-02] — Hapag-Lloyd Transshipment & Duplicate Fix
- [2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History
- require_admin
- frontend/README.md
- pytest
- [2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control
- os
- capture_failure_context
- [2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash
- ._fs_extract_rows
- Working in this repository
- [2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes
- install_pi.sh
- remote_worker.py
- postcss.config.mjs
- [2026-05-23 – 2026-05-24] — Maersk Shadow DOM & Stealth Upgrades
- get_me
- Architecture Overview
- main
- safe_step.py
- alembic
- clean_selector_memory

## God Nodes (most connected - your core abstractions)
1. `RateSearchRequest` - 164 edges
2. `cn()` - 89 edges
3. `CarrierResultStatus` - 71 edges
4. `QuoteSchema` - 67 edges
5. `User` - 63 edges
6. `PortManager` - 58 edges
7. `HapagLloydConnector` - 56 edges
8. `CMAConnector` - 55 edges
9. `MaerskConnector` - 52 edges
10. `BaseCarrierConnector` - 50 edges

## Surprising Connections (you probably didn't know these)
- `Free Time — GreenX blank, ONE India wrong, Hapag Nhava Sheva unresolved (Singapore → Nhava Sheva)` --references--> `_apply_freetime_to_quote()`  [INFERRED]
  CHANGELOG.md → backend/carriers/hapag_lloyd_connector.py
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

## Communities (121 total, 18 thin omitted)

### Community 0 - "job_service.py"
Cohesion: 0.11
Nodes (33): get_connector(), Get the appropriate connector for a carrier. If USE_MOCK_CARRIERS=true: returns…, Quote, Represents a single freight quote from a carrier., SearchStatus, get_switches(), off_message(), _path() (+25 more)

### Community 1 - "BaseCarrierConnector"
Cohesion: 0.05
Nodes (29): ABC, BaseCarrierConnector, NotAvailableConnector, Any, Open the price breakdown / detail view for a specific quote. Args: quote_ref:…, Extract individual charge line items from the price breakdown. Returns: List of…, Normalize extracted data into a QuoteSchema using the normalizer. Args:…, Abstract base class for carrier portal connectors. (+21 more)

### Community 2 - "cn"
Cohesion: 0.06
Nodes (55): Reuse the primitives, New primitives — `frontend/src/components/ui/`, BackendConfigModalProps, BatchProgressPanel(), cheapest(), Filter, lanePhase(), Phase (+47 more)

### Community 3 - "User"
Cohesion: 0.11
Nodes (44): admin_delete_user(), approve_user(), CarrierOverrideRequest, create_custom_port_endpoint(), delete_carrier_override_endpoint(), delete_custom_port_endpoint(), delete_user(), disable_user() (+36 more)

### Community 4 - "auth_routes.py"
Cohesion: 0.06
Nodes (74): clear_session_cookie(), get_current_user_optional(), login(), LoginRequest, logout(), AsyncSession, BaseModel, post (+66 more)

### Community 5 - "browser_cleanup.py"
Cohesion: 0.12
Nodes (32): _is_chrome(), _is_playwright_driver(), _kill(), kill_profile_browsers(), _proc_supported(), Cleanup for Chrome browsers and temporary profiles that a failed close leaves…, Kill every automated Chrome and Playwright driver. Only call this when no…, Delete per-search profile copies ("chrome_profile_<carrier>_tmp_<id>") and… (+24 more)

### Community 6 - "app/page.tsx"
Cohesion: 0.06
Nodes (47): HomeContent(), AppHeader(), AppHeaderProps, initials(), systemStatus(), ChatWidget(), ChatWidgetProps, Message (+39 more)

### Community 7 - "api.ts"
Cohesion: 0.07
Nodes (69): AdminDashboard(), UserRecord, LoginContent(), AdminCarriers(), PROFILE_NAMES, when(), AdminPortFixes(), AdminPortFixesProps (+61 more)

### Community 8 - "PortManager"
Cohesion: 0.06
Nodes (21): add_carrier_override(), add_custom_port(), delete_carrier_override(), delete_custom_port(), get_custom_ports(), get_popular_ports_config(), normalize_port_input(), PortManager (+13 more)

### Community 9 - "test_remote_worker.py"
Cohesion: 0.10
Nodes (22): db(), row(), setup(), FakeConnector, fixture, Handing a carrier (Maersk) to a worker machine through the shared database., test_busy_online_worker_is_waited_for_then_server_takes_over(), run() (+14 more)

### Community 10 - "CMAConnector"
Cohesion: 0.06
Nodes (25): CMAConnector, Ensures 'Ramp' is explicitly selected under 'Type of location' toggle buttons…, Scans for Route, POL (Port of Loading), or POD (Port of Discharge) dropdown…, Clears the currently selected Destination port tag/card, re-types the locode,…, Dynamically extracts any recommended 5-letter POD LOCODE mentioned in the…, Detects if CMA CGM displayed an advisory banner message: "Looking for AEJEA or…, Handles the 'Customer account' -> 'Role (you are acting as)' dropdown on CMA…, Repeatedly clicks 'More results' if visible to load ALL quotes on the page. (+17 more)

### Community 11 - "get_async_session_maker"
Cohesion: 0.10
Nodes (30): get_route_health(), Get carrier search reliability & route health matrix across origin-destination…, _create_sqlite_engine(), get_async_session_maker(), _get_engine(), _get_session_maker(), init_db(), Get the session maker for use outside of FastAPI dependency injection. (+22 more)

### Community 12 - "selector_memory.py"
Cohesion: 0.24
Nodes (12): get_approved_selector(), _load_memory(), Selector Memory — stores and retrieves human-approved selector patches., Loads memory JSON file. Returns empty dict if file is missing or invalid., Saves memory dict back to JSON file., Looks up if there is an approved replacement selector for the given carrier and…, Stores an approved replacement selector., Marks any proposed selector for this step as REJECTED. (+4 more)

### Community 13 - "user_routes.py"
Cohesion: 0.07
Nodes (42): get_current_user(), Dependency that strictly requires an authenticated active member., AdminLoginRequest, CarrierSwitchRequest, Config, CustomPortRequest, ExchangeRateUpdateRequest, fetch_carrier_overrides() (+34 more)

### Community 14 - "RateSearchRequest"
Cohesion: 0.09
Nodes (26): OOCLConnector, parse_oocl_date(), Opens the Details dialog for a card, clicks the Charge Breakdown tab, extracts…, Serves one container-type cycle from the cached merged quote set: -…, One crawl serves all container-type cycles (cached), combining: 1. Sailing…, Attempts to automatically click the Cloudflare Turnstile 'Verify you are human'…, Public oocl.com Chromium sailing schedule crawl bypassed per directive. All…, RateSearchRequest (+18 more)

### Community 15 - "CarrierResultStatus"
Cohesion: 0.07
Nodes (27): Override to immediately return CONNECTOR_NOT_AVAILABLE., HapagLloydAPIConnector, Any, AsyncClient, Direct REST API connector for Hapag-Lloyd Prices API v2.1.4., API connectors do not require browser login sessions., Required abstract method implementation; delegates to run_full_search., Batch (RFQ) mode: the base implementation drives a browser page, so answer from… (+19 more)

### Community 16 - "preferences.ts"
Cohesion: 0.09
Nodes (34): LaunchIntro(), SearchHistoryItem, derive(), Derived, startOfDay(), UsageStats(), ChoiceCard(), Toggle() (+26 more)

### Community 17 - "test_rfq_agent.py"
Cohesion: 0.10
Nodes (35): RFQParseResult, asyncio, Unit tests for the Gemini AI RFQ Agent service (parse_rfq). Includes…, Test Image 2: Air rate request generates 3 drafts to Glenn (AWOT), Jing Hui…, Test Image 4: Steel Plate ex Pasir Gudang / Tanjung Pelepas for 20' & 40'., Test Guardrail: Detects Reefer container request and returns unsupported_cargo…, Test Guardrail: Detects LCL request., Test OpenFlights 6,072 IATA airport dataset and shorthand alias resolution. (+27 more)

### Community 18 - "tunnel_relay/main.py"
Cohesion: 0.25
Nodes (8): api_route, fastapi_middleware_cors, health(), get, Request, websocket, relay_request(), websocket_endpoint()

### Community 19 - "SocialWidget.tsx"
Cohesion: 0.10
Nodes (34): ACCENT_COLORS, errorMessage(), relativeTime(), resizeImageToDataUrl(), SocialWidget(), SocialWidgetProps, EMOJI_GROUPS, EmojiPicker() (+26 more)

### Community 20 - "AdminUsers.tsx"
Cohesion: 0.20
Nodes (14): AdminUserRecord, AdminUsers(), AdminUsersProps, ago(), AuditEntry, Avatar(), Filter, initials() (+6 more)

### Community 21 - "GreenXConnector"
Cohesion: 0.09
Nodes (14): GreenXConnector, date, Overrides base search runner to query all 3 sizes at once and cache the…, Type a LOCODE into the autocomplete field and click the first visible dropdown…, Find quantity input next to or below label_text and fill it., Find the exact individual quote card container row encompassing dates, rates,…, Dismiss any cookie/alert modal that would intercept pointer events., Splits a single raw multi-container quote card into multiple QuoteSchema… (+6 more)

### Community 22 - "social_routes.py"
Cohesion: 0.12
Nodes (29): get_conversation(), list_colleagues(), poke_colleague(), PokeRequest, AsyncSession, BaseModel, delete, get (+21 more)

### Community 23 - "ChargeCategory"
Cohesion: 0.12
Nodes (29): CarrierCode, ChargeCategory, classify_charge(), Charge Classifier — rule-based classification of freight charge line items.…, Classify a charge line item based on its name, amount, section heading, and…, Tests for charge classifier., test_basic_ocean_freight(), test_cwx_heavy_weight_charge() (+21 more)

### Community 24 - "backend/main.py"
Cohesion: 0.09
Nodes (23): health(), lifespan(), get, websocket, Infreight Ocean Carrier Rate Automation — FastAPI Application. Main entry point…, Check if the VNC viewer is available (production only, where Xvfb runs)., Proxy WebSocket connections to legacy local x11vnc at localhost:5900., Proxy WebSocket connections to specific carrier x11vnc servers. (+15 more)

### Community 25 - "rate_search_routes.py"
Cohesion: 0.07
Nodes (44): approve_repair(), ApproveRepairRequest, carrier_switch_status(), chat_endpoint(), ChatRequest, create_batch_rate_search(), _contains(), _looks_like() (+36 more)

### Community 26 - "MSCConnector"
Cohesion: 0.16
Nodes (8): format_to_iso_date(), MSCConnector, Playwright-based automation for MSC (Mediterranean Shipping Company)., Handles the MSC login flow., Clicks Instant Quote, fills form, clicks Search., Detects and clicks the 'Ramp' delivery/haulage option if MSC displays Ramp /…, Parse '14 Jun 2026' to 'YYYY-MM-DD, test_msc()

### Community 27 - "parse_rfq"
Cohesion: 0.14
Nodes (24): _call_native_gemini_api(), _detect_booking_confirmation(), _detect_dual_mode_enquiry(), _detect_mode_by_hierarchy(), _detect_unsupported_cargo(), _extract_20gp_weight_priority(), generate_dual_air_drafts(), _load_airport_aliases_config() (+16 more)

### Community 28 - "lucide-react"
Cohesion: 0.09
Nodes (40): 0. The one invariant, CarrierMultiSelect(), CarrierMultiSelectProps, isAllCarriers(), toggleAllCarriers(), toggleCarrierSelection(), PortAutocomplete(), PortAutocompleteProps (+32 more)

### Community 29 - "AIBrowserAgent"
Cohesion: 0.17
Nodes (10): AIBrowserAgent, Capture the current page as a PNG screenshot., Build the prompt with task description and action history., Parse Gemini's response into an action dict., Call Gemini API with exponential backoff retry., Execute a parsed action on the browser page., Detect if the agent is stuck repeating the same action., Find all visible interactive elements and format them as a prompt guide. (+2 more)

### Community 30 - "database.py"
Cohesion: 0.08
Nodes (32): get_recent_search_status_context(), handle_chat_query(), _local_chatbot_fallback(), Chat Service — manages conversational AI queries from the frontend user using…, Intelligent responder for search status, carrier guidance, air/sea info, and…, Queries the database for the most recent rate search status to give the chatbot…, Sends the chat message and history to native Gemini 2.5 Flash API. If Gemini…, get_sync_url() (+24 more)

### Community 31 - "ONEConnector"
Cohesion: 0.08
Nodes (12): ONEConnector, _classify(), fill_container_card(), date, Parses ONE QUOTE Free Time popover text for DESTINATION ONLY. Ignores Origin…, Splits a single raw multi-container quote card into multiple QuoteSchema…, Tries to click a matching option from ONE's visible dropdown. Returns True only…, Extracts 5-letter UN/LOCODE from strings like 'Singapore [SGSIN]' or 'Singapore… (+4 more)

### Community 32 - "_Page"
Cohesion: 0.15
Nodes (8): _connector(), _Locator, _Page, Maersk's login page redirects to the Hub a few seconds after loading when the…, Sits on /portaluser/login, then redirects after `redirect_after` URL reads., test_login_uses_saved_session_after_late_redirect(), test_wait_detects_late_redirect(), test_wait_detects_login_form()

### Community 33 - "Engineering Report: Sourcing Portal Enhancements & Scraping Pipeline Stability"
Cohesion: 0.08
Nodes (23): 1. Anti-Bot Mitigation & CAPTCHA Human-in-the-Loop Recovery, 2. Sourcing Parallelization & Surcharges Optimization, 3. Autocomplete Intelligence & Location Mapping, 4. Scraper Pipeline Maintenance, 5. Infrastructure & DevSecOps Enhancements, Business Value, Business Value, Business Value (+15 more)

### Community 34 - "Changelog"
Cohesion: 0.08
Nodes (23): [2026-05-18 – 2026-05-19] — Railway Deployment & Docker, [2026-05-20 – 2026-05-22] — Port Resolution & Frontend Improvements, [2026-05-25 – 2026-05-26] — VNC Display Isolation & Proxy Integration, [2026-05-31] — Multi-Instance Support & Charge Classification, [2026-06-01] — Hapag-Lloyd Sold Out Detection & Date Parsing, [2026-07-03] — Robustness Review & Multi-Port Quick Search Fixes, [2026-07-08] — OOCL E-Quote Calendar Navigation, cheapest E-Spot selection, and E-Quote/E-Spot isolation refinements, [2026-07-09] — Hapag-Lloyd Quick Quotes pairing and selection simplification (+15 more)

### Community 35 - "AdminOverview.tsx"
Cohesion: 0.10
Nodes (24): AdminAnalytics, AdminOverview(), AdminOverviewProps, AdminOverviewUser, AnalyticsRange, Attention, attentionItems(), CARRIER_LABELS (+16 more)

### Community 36 - "package.json"
Cohesion: 0.07
Nodes (25): eslintConfig, nextConfig, engines, node, name, packageManager, private, scripts (+17 more)

### Community 37 - "dependencies"
Cohesion: 0.15
Nodes (13): dependencies, class-variance-authority, clsx, exceljs, lucide-react, next, next-themes, @radix-ui/react-slot (+5 more)

### Community 38 - "RateResults.tsx"
Cohesion: 0.07
Nodes (56): BatchProgressPanelProps, LiveSearchProgressProps, QuoteBreakdownDrawer(), QuoteBreakdownDrawerProps, Breakdown(), ChargeList(), dateValue(), freeTimeText() (+48 more)

### Community 39 - "SearchQueueManager"
Cohesion: 0.12
Nodes (11): Lock, Marks a search as completed internally so we can track the auto-release timeout., Called periodically in a background task to check if the user has held the lock…, Forcefully clears all queued searches and the active lock. Useful for…, Returns or creates an asyncio.Lock for a specific carrier code to prevent…, Adds a search to the queue and waits until it becomes the active search. Event-…, Singleton manager to enforce a FIFO queue for rate searches. Since web scraping…, Returns the current position of the search in the queue. 0 means it is the… (+3 more)

### Community 40 - "hapag_lloyd_connector.py"
Cohesion: 0.08
Nodes (41): Base Carrier Connector — abstract base class for all carrier connectors. Each…, CMA CGM Live Connector — Playwright automation. Credentials read from env:…, Hapag-Lloyd Prices API Connector (REST API v2.1.4). Provides real-time rate…, # NOTE: No start date fill needed — schedule page defaults to today,, Hapag-Lloyd Live Connector -- Playwright automation. Credentials read from env:…, get_booking_start_date(), date, OOCL Live Connector â€” Playwright automation for Sailing Schedules. (+33 more)

### Community 41 - "Frontend Redesign — Componentry Design System, Workspace & Launch Intro (2026-09-07)"
Cohesion: 0.11
Nodes (17): 1. Design system foundation (`082b43a`), 2. Bugs found and fixed during the restyle, 3. Workspace + launch intro (`21ade75`), 4. Follow-up fixes (`2f9d92b`), 5. Verification, 6. Known limitations / candidate follow-ups, 7. Conventions to follow from here, Dependencies added (5, all small, no runtime lib dependency on Componentry) (+9 more)

### Community 42 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 43 - "._fs_dismiss_modals"
Cohesion: 0.11
Nodes (14): _dismiss_once(), _click_date_strip_item(), _open_calendar(), Event, Lock, Iterates through the FreightSmart results date calendar to collect E-Quote and…, Full FreightSmart phase: login â†’ fill quote form â†’ search â†’ extract rows., Shadow-DOM-aware check for whether the onboarding tour heading is on screen. (+6 more)

### Community 44 - "test_carrier_timeout.py"
Cohesion: 0.19
Nodes (10): CrashingConnector, HangingConnector, asyncio, A carrier whose browser hangs must be stopped after CARRIER_SEARCH_TIMEOUT_SEC…, Hangs on the sizes in `hang_on`; answers NO_QUOTES_AVAILABLE for the rest., Like a real connector whose tab dies: reports a crash, then never returns., _run(), test_crashed_tab_stops_the_carrier_without_waiting_for_the_timeout() (+2 more)

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
Nodes (33): HapagLloydConnector, HapagServiceUnavailableException, Exception, Normalize various date formats (e.g. 2026-05-31, 31.05.2026, 31 May 2026, 31…, Robustly selects options from Hapag-Lloyd custom dropdown lists. Types the…, Detects the Microsoft B2C identity/OAuth login page. Hapag can silently bounce…, Guards against the session-expiry-mid-crawl failure mode: the existing redirect…, Crawls Hapag-Lloyd sailing schedules from the Schedule tab. (+25 more)

### Community 49 - "MockCarrierConnector"
Cohesion: 0.12
Nodes (11): _generate_maersk_mock_quotes(), _generate_msc_mock_quotes(), _generate_one_mock_quotes(), MockCarrierConnector, any, Mock Carrier Connector — returns realistic sample data for testing. Used when…, Generate realistic ONE sample quotes with charge breakdowns., Generate realistic MSC sample quotes with validity_till. (+3 more)

### Community 50 - "[2026-06-03] — CMA CGM Routing & Free Time Extraction"
Cohesion: 0.50
Nodes (4): [2026-06-03] — CMA CGM Routing & Free Time Extraction, CMA CGM — Import Free Time from D&D Tab, CMA CGM — Routing Detection (Direct vs Transit), Maersk — Free Time Extraction from Card Text

### Community 51 - "carrier_sessions.py"
Cohesion: 0.22
Nodes (15): clean_storage_state(), delete_session(), load_session(), _on_domain(), _path(), Saved carrier logins uploaded by an admin. An admin logs in to a carrier in…, What the admin screen shows: who uploaded it, when, and how much it holds., Keep only this carrier's cookies and localStorage, in the shape add_cookies… (+7 more)

### Community 52 - "schemas.py"
Cohesion: 0.13
Nodes (18): parse_rfq_endpoint(), post, API routes for RFQ parsing agent., Parse a free-text RFQ email or message into a structured RateSearchRequest…, BatchRateSearchRequest, BatchRateSearchResponse, BatchRoutePair, BatchSearchStatusItem (+10 more)

### Community 53 - "test_hapag_freetime.py"
Cohesion: 0.15
Nodes (16): Looks up standard destination demurrage/detention free time days., (days, estimated): estimated when the destination has no entry in the free time…, _apply_freetime_to_quote(), freetime_days(), match_freetime_entry(), Any, Destination free time from config/hapag_freetime.json, shared by the Hapag-…, Days for this container from a table entry ({"20GP": n, "40GP": n} or a bare… (+8 more)

### Community 54 - "🚢 Infreight Sourcing & Ocean Rate Automation System"
Cohesion: 0.14
Nodes (13): 1. Multi-Carrier Automation Engine, 2. Intelligent Surcharge & Charge Classifier Engine (`charge_classifier.py`), 3. Container Comparison Matrix & Excel Export Engine, 🚢 Infreight Sourcing & Ocean Rate Automation System, 🌟 Key Capabilities, 📄 License & Confidentiality, Prerequisites, 🛠️ Project Structure (+5 more)

### Community 55 - "MaerskConnector"
Cohesion: 0.05
Nodes (31): _is_logged_in_url(), MaerskConnector, flatten_tree(), Small aimless pointer drift, as a person does while a page loads., Clicks an element with pre-click and post-click human-like reaction pauses., Wait until the login page either redirects to a signed-in page or shows its…, Execute the full search flow with Progressive Lazy Loading: 1. Login 2. Search…, Extracts freetime, demurrage, and detention from the 'Import D&D fees' tab… (+23 more)

### Community 56 - "[2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split"
Cohesion: 0.15
Nodes (13): G2 Stress Test: "Hi, Please book the below as per your quote ref INF-2026-0842:…, H1 Stress Test: Table with 2 distinct rows: Row 1: POL Singapore, POD Jakarta,…, test_g2_booking_confirmation_guardrail(), test_h1_table_deduplication_two_pairs(), [2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split, Booking Confirmation / Instructions Intercept Guardrail G2 (`rfq_agent.py` & `RfqInputSection.tsx`), Commercial Sales Desk Intelligence (`sales_notes`), Deterministic Port Alias Resolver (`ports_aliases.json`) (+5 more)

### Community 57 - "CarrierSearchResult"
Cohesion: 0.22
Nodes (14): Base, CarrierSearchResult, Tracks the result of searching a specific carrier for a rate search., Copy the connector's "port not found" note onto the result row, if it made one., _store_port_not_found(), test_switched_off_carrier_is_skipped(), run(), _miss() (+6 more)

### Community 58 - "🛠 Detailed Carrier Log"
Cohesion: 0.15
Nodes (12): 🛠 Detailed Carrier Log, 🟢 GreenX, 🟠 Hapag-Lloyd, Infreight Ocean Carrier Rate Automation — Development Log, 🚀 Key Highlights & Architectural Changes, 🔌 Local Laptop Deployment (Self-Hosted Worker), 🔵 Maersk, 💗 ONE (Ocean Network Express) (+4 more)

### Community 59 - "json"
Cohesion: 0.13
Nodes (16): AI Browser Agent — Vision-based browser automation using Gemini Flash. This…, _cleanup_profile(), main(), Experimental AI Agent Test -- Maersk Quote Search This script tests the AI…, Remove temporary chrome profile directory., Print with ASCII-safe encoding for Windows console., safe_print(), parse_hapag_pdf() (+8 more)

### Community 60 - "CurrencyManager"
Cohesion: 0.23
Nodes (7): convert_currency_to_usd(), CurrencyManager, get_all_exchange_rates(), Any, Currency Exchange Rate Service — manages currency conversions and custom…, update_exchange_rate(), threading

### Community 61 - "time"
Cohesion: 0.18
Nodes (7): Storage Cleanup Utility — automatically removes stale debug screenshots, HTML…, Test multi-container search and caching for Hapag-Lloyd connector., glob, shutil, subprocess, tempfile, time

### Community 62 - "[2026-06-30] — ONE Multi-Container & Sold-Out, GreenX Surcharge Intake, Free-Time Fixes, Maersk Diagnosis"
Cohesion: 0.25
Nodes (8): [2026-06-30] — ONE Multi-Container & Sold-Out, GreenX Surcharge Intake, Free-Time Fixes, Maersk Diagnosis, Free Time — GreenX blank, ONE India wrong, Hapag Nhava Sheva unresolved (Singapore → Nhava Sheva), GreenX — Only Basic Ocean Freight & LSS Folded Into Final Value, MAERSK — "Quotes Found" but Empty Excel (Diagnosis), ONE — All-Container-Type Search Returning 0 Quotes, ONE — Multi-Container Breakdown Triple-Counted / Inflated Final Value, ONE — Sold-Out ("Notify Me") Sailings Appearing as Quotes, Performance/Reliability — Stop Copying Chrome Caches During Profile Clone/Sync

### Community 63 - "[2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup"
Cohesion: 0.22
Nodes (8): [2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup, Chromium Cache Auto-Cleanup (Railway Storage Bloat Prevention), CMA CGM — 30-Second Timeout on Sold Out Cards, CMA CGM — Free Time Regex Too Strict, CMA CGM — Routing Regex Not Matching "via LEKKI, LA, NG", Excel Export — Routing & Free Time Columns Always Empty, Excel Export — Sold Out Rows Not Showing, Maersk — Hardcoded Port Overrides

### Community 64 - "tunnel_client.py"
Cohesion: 0.29
Nodes (5): argparse, handle_request(), AsyncClient, run_client(), websockets

### Community 65 - "maersk_proxy_settings"
Cohesion: 0.57
Nodes (6): maersk_proxy_settings(), Proxy for the Maersk browser, from environment variables, or None. Any…, _clear(), test_any_provider_uses_server_and_login_as_given(), test_bright_data_defaults_unchanged(), test_no_proxy_without_credentials()

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
Cohesion: 0.23
Nodes (12): Analyzes the failure context and DOM content to suggest a selector repair. Uses…, suggest_fix(), detect_manual_action_required(), Manual Action Detector — identifies pages requiring human verification (2FA,…, Scans the current Playwright page to see if a CAPTCHA, Cloudflare challenge,…, asyncio, Self-Healing Layer & Chatbot Test Suite. Tests the selector memory, failure…, test_ai_repair_agent_offline_fallback() (+4 more)

### Community 70 - "sort_container_types"
Cohesion: 0.40
Nodes (4): Sort container types in standard order: DRY 20 (20GP) -> DRY 40 (40GP) -> DRY…, sort_container_types(), test_container_types_standard_ordering(), model_validator

### Community 71 - "test_one_charge_override.py"
Cohesion: 0.40
Nodes (3): MockCard, Unit test for ONE connector charge classification override., test_emergency_surcharge_override()

### Community 72 - "deploy"
Cohesion: 0.25
Nodes (7): build, builder, deploy, restartPolicyMaxRetries, restartPolicyType, startCommand, $schema

### Community 73 - "export_maersk_login.py"
Cohesion: 0.70
Nodes (4): _logged_in(), main(), _on_login_page(), Save a Maersk login from your own PC for the server to use. Opens real Google…

### Community 74 - "[2026-08-04 - 2026-08-06] — CMA CGM Dynamic RAMP/POD Rerouting, Brand Excel Styling, Port Synonym Matching & Tunnel Relays"
Cohesion: 0.40
Nodes (5): [2026-08-04 - 2026-08-06] — CMA CGM Dynamic RAMP/POD Rerouting, Brand Excel Styling, Port Synonym Matching & Tunnel Relays, Brand-Aligned Excel Export Styling (`excel_export.py`), CMA CGM Dynamic RAMP / POD Advisory Banner Detection (`cma_connector.py`), Dynamic Carrier Port Overrides & Admin Registry (`PortManager`, `AdminDashboard.tsx`), Railway WebSocket Tunnel Relay & Failover (`tunnel_client.py`, `run_tunnel_client.bat`, `FailoverFetch`)

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

### Community 81 - "Design system — read before touching any UI"
Cohesion: 0.33
Nodes (5): Animation rules, Client-only preferences, Design system — read before touching any UI, This is NOT the Next.js you know, Use tokens, not raw colours

### Community 82 - "ai_repair_agent.py"
Cohesion: 0.17
Nodes (10): ambiguous_python_import_b35980c0aa01, _local_fuzzy_repair(), AI Repair Agent — diagnoses Playwright step failures and suggests selector…, A local rule-based heuristic to locate reasonable buttons or inputs when Gemini…, asyncio, Integration tests for authentication, legacy user password setup, pending…, test_full_auth_lifecycle(), bs4 (+2 more)

### Community 83 - "layout.tsx"
Cohesion: 0.25
Nodes (6): frontend_src_app_globals, instrumentSans, inter, metadata, viewport, ThemeProvider()

### Community 84 - "scrape_one_freetime.py"
Cohesion: 1.00
Nodes (3): check_and_wait_for_captcha(), login(), main()

### Community 85 - "test_hapag_schedule_debug.py"
Cohesion: 0.67
Nodes (3): Debug script: Reuse HapagLloydConnector login, then step through the Schedule…, run(), ss()

### Community 86 - "test_rate_search_api.py"
Cohesion: 0.50
Nodes (3): Tests for rate search API endpoints., Placeholder test — integration tests require DB setup., test_placeholder()

### Community 88 - "asyncio"
Cohesion: 0.09
Nodes (16): asyncio, Interactive Headed Login Helper for Maersk. Opens real Chrome using the…, Interactive Headed Login Helper for ONE (Ocean Network Express). Opens Chrome…, Hapag-Lloyd form inspector., Wrapper script to set Windows event loop policy before starting Uvicorn. This…, CMA CGM Montreal Ramp selection test. Verifies that when…, main(), Test Maersk connector with Singapore -> Ho Chi Minh City route. Verifies that:… (+8 more)

### Community 90 - "maersk_connector.py"
Cohesion: 0.08
Nodes (37): get_countries(), get_port(), get_suggestions(), get, Get list of countries for autocomplete dropdown., Get specific port details by UN/LOCODE., Get port suggestions for autocomplete., search() (+29 more)

### Community 92 - "[2026-06-02] — Hapag-Lloyd Transshipment & Duplicate Fix"
Cohesion: 0.67
Nodes (3): [2026-06-02] — Hapag-Lloyd Transshipment & Duplicate Fix, Hapag-Lloyd — Duplicate Sailings from Transshipment Vessels, Hapag-Lloyd — Routing Not Marked as Transit

### Community 93 - "[2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History"
Cohesion: 0.40
Nodes (5): [2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History, Admin User Search History & SGT GMT+8 Conversion (`AdminDashboard.tsx`), GreenX (Evergreen) Card Isolation & Surcharge Parsing (`greenx_connector.py`), Multi-Route Batch Execution Engine (`batch_engine.py`), OOCL FreightSmart 28-Day Calendar Expansion (`oocl_connector.py`)

### Community 96 - "frontend/README.md"
Cohesion: 0.50
Nodes (3): Deploy on Vercel, Getting Started, Learn More

### Community 97 - "pytest"
Cohesion: 0.10
Nodes (15): parse_msc_modal_charges(), Parses charges from MSC BreakdownModal text. Correctly includes charges whose…, parse_hapag_card_text_mock(), Verify that multi-leg/feeder routes take the final arrival ETA and 28 days TT., Mock implementation of the JS evaluate logic inside hapag_lloyd_connector.py., test_hapag_multi_leg_schedule_extraction(), Test MSC charges parsing for Singapore to Conakry, Guinea (40GP). Charges with…, Test when only some surcharges have the payment condition. (+7 more)

### Community 98 - "[2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control"
Cohesion: 0.40
Nodes (5): [2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control, Concurrency Limit Queue & Admin Control Panel, MSC — Mediterranean Shipping Company Connector Implementation, ONE — Inbound Free Time Swap & Scraper Upgrade, OOCL — Orient Overseas Container Line Connector Implementation

### Community 99 - "os"
Cohesion: 0.09
Nodes (10): GreenX (Evergreen) Live Connector - Playwright automation., dump_options(), main(), Diagnostic: dump ALL dropdown options (text + innerHTML) when typing 'DEHAM'…, Script to test Playwright browser launching using your REAL Google Chrome…, Unit test for CMA CGM demurrage and detention combined free time parsing logic., datetime, os (+2 more)

### Community 101 - "capture_failure_context"
Cohesion: 0.33
Nodes (5): capture_failure_context(), Exception, Failure Detector — parses and structures error context from failed Playwright…, Assembles a standardized diagnostic dictionary containing all available details…, test_failure_detector()

### Community 102 - "[2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash"
Cohesion: 0.40
Nodes (5): [2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash, AI RFQ Front Door & Air Freight Support, Multi-Origin & Gappy List Parsing (Sea RFQs), Native Gemini 2.5 Flash Direct API Integration, Search Form Streamlining

### Community 103 - "._fs_extract_rows"
Cohesion: 0.12
Nodes (12): clean_vessel_name(), _parse_date(), Parses one FreightSmart result card's inner text into a raw row dict. Text-…, Collects result cards from the FreightSmart quote results page., Applies the business rules and pairs FreightSmart prices with crawled…, [2026-08-07] — Carrier Specific Free Time, Demurrage/Detention Splitting, MSC CDD Surcharges, OOCL Nearby Route Filtering & Favicon Cache Busting, Demurrage & Detention Split Fields Across System (`schema.py`, `msc_connector.py`, `maersk_connector.py`, `one_connector.py`, `greenx_connector.py`, `cma_connector.py`, `oocl_connector.py`, `ResultsTable.tsx`, `excel_export.py`), Favicon Cache Busting & Brand Icon (`layout.tsx`, `icon.png`, `favicon.ico`) (+4 more)

### Community 106 - "[2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes"
Cohesion: 0.50
Nodes (4): [2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes, CMA CGM — Chrome Profile Bypass, ONE — Date Formatting & Charge Breakdown Pollution, ONE — Date Picker Pre-selection Issue

### Community 108 - "remote_worker.py"
Cohesion: 0.09
Nodes (33): Models package. Note: Individual modules can be imported directly (e.g.,…, A worker machine (e.g. the office laptop) that runs some carriers' searches., WorkerHeartbeat, _claim_loop(), claim_next(), delegate_and_wait(), heartbeat_once(), _heartbeat_thread() (+25 more)

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
Cohesion: 0.12
Nodes (17): capture_page_state(), Page Observer — captures page state (screenshot, DOM, visible text) on failure., Captures screenshot, DOM HTML, and inner text of the current page. Saves…, generate_report(), Repair Report — generates and saves diagnosis reports on Playwright selector…, Assembles a comprehensive repair report and writes it as JSON and Markdown…, Safe Step — Playwright action execution wrapper with manual intervention pause…, Updates the status of a carrier search in the database. (+9 more)

### Community 137 - "clean_selector_memory"
Cohesion: 0.67
Nodes (3): clean_selector_memory(), fixture, Wipes the selector memory JSON file before and after each test.

## Knowledge Gaps
- **313 isolated node(s):** `Config`, `install_pi.sh script`, `eslintConfig`, `nextConfig`, `name` (+308 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 965 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **18 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Changelog` connect `Changelog` to `[2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control`, `[2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning`, `[2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash`, `._fs_extract_rows`, `[2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes`, `[2026-08-04 - 2026-08-06] — CMA CGM Dynamic RAMP/POD Rerouting, Brand Excel Styling, Port Synonym Matching & Tunnel Relays`, `[2026-05-29 – 2026-05-30] — Hapag-Lloyd Full Integration`, `Architecture Overview`, `[2026-06-03] — CMA CGM Routing & Free Time Extraction`, `[2026-05-23 – 2026-05-24] — Maersk Shadow DOM & Stealth Upgrades`, `[2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split`, `[2026-06-02] — Hapag-Lloyd Transshipment & Duplicate Fix`, `[2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History`, `[2026-06-30] — ONE Multi-Container & Sold-Out, GreenX Surcharge Intake, Free-Time Fixes, Maersk Diagnosis`, `[2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup`?**
  _High betweenness centrality (0.331) - this node is a cross-community bridge._
- **Why does `[2026-06-03] — CMA CGM Routing & Free Time Extraction` connect `[2026-06-03] — CMA CGM Routing & Free Time Extraction` to `Changelog`?**
  _High betweenness centrality (0.275) - this node is a cross-community bridge._
- **Why does `Maersk — Free Time Extraction from Card Text` connect `[2026-06-03] — CMA CGM Routing & Free Time Extraction` to `RateResults.tsx`?**
  _High betweenness centrality (0.274) - this node is a cross-community bridge._
- **Are the 33 inferred relationships involving `RateSearchRequest` (e.g. with `create_batch_rate_search()` and `create_rate_search()`) actually correct?**
  _`RateSearchRequest` has 33 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `cn()` (e.g. with `Reuse the primitives` and `7. Conventions to follow from here`) actually correct?**
  _`cn()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 22 inferred relationships involving `CarrierResultStatus` (e.g. with `safe_step()` and `update_carrier_status()`) actually correct?**
  _`CarrierResultStatus` has 22 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Config`, `install_pi.sh script`, `eslintConfig` to the rest of the system?**
  _313 weakly-connected nodes found - possible documentation gaps or missing edges._