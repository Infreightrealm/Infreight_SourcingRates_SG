# Graph Report - Infreight_SourcingRates_SG  (2026-10-08)

## Corpus Check
- 241 files · ~1,159,914 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 23 file(s) not represented in the graph (top: (none) 10, .bat 6, .conf 2)

## Summary
- 2323 nodes · 5696 edges · 132 communities (109 shown, 23 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 331 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `62679300`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- BaseCarrierConnector
- cn
- user_routes.py
- auth_routes.py
- browser_cleanup.py
- OOCLConnector
- api.ts
- PortManager
- safe_step.py
- CMAConnector
- sys
- CarrierSearchResult
- auth_service.py
- ._fs_dismiss_modals
- HapagLloydAPIConnector
- preferences.ts
- test_rfq_agent.py
- database.py
- SocialWidget.tsx
- LiveSearchProgress.tsx
- RateSearchRequest
- social_routes.py
- playwright_async_api
- backend/main.py
- rate_search_routes.py
- MSCConnector
- parse_rfq
- RateSearchForm.tsx
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
- test_port_logging_and_mismatch.py
- dithered-logo.tsx
- 👥 The 5 Agent Roles
- HapagLloydConnector
- CarrierResultStatus
- test_self_healing.py
- CurrencyManager
- parse_msc_modal_charges
- charge_classifier.py
- 🚢 Infreight Sourcing & Ocean Rate Automation System
- AdminUsers.tsx
- [2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split
- RateSearch
- 🛠 Detailed Carrier Log
- ._fs_pair_and_select
- .login
- ._fs_extract_rows
- .run_full_search
- [2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup
- ai_repair_agent.py
- layout.tsx
- GreenX — Surcharge Intake Fix (2026-06-30)
- Admin Page & Port Prioritization Guide
- [2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning
- detect_manual_action_required
- MockCard
- dependencies
- deploy
- ._fs_iterate_calendar_dates
- test_oocl_cwx.py
- Summary of Changes — July 20, 2026
- capture_failure_context
- test_one_premium_override.py
- resolve_port_alias
- json
- test_auth_routes.py
- Design system — read before touching any UI
- test_panama_canal_surcharge.py
- handle_chat_query
- _dismiss_once
- get_me
- BatchProgressPanel.tsx
- RateLimiter
- os
- [2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History
- devDependencies
- ref_fs
- [2026-08-07] — Carrier Specific Free Time, Demurrage/Detention Splitting, MSC CDD Surcharges, OOCL Nearby Route Filtering & Favicon Cache Busting
- cma_cgm_connector.py
- MockCard
- eslint.config.mjs
- frontend/README.md
- pytest
- [2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control
- [2026-08-04 - 2026-08-06] — CMA CGM Dynamic RAMP/POD Rerouting, Brand Excel Styling, Port Synonym Matching & Tunnel Relays
- sort_container_types
- [2026-05-20 – 2026-05-22] — Port Resolution & Frontend Improvements
- verify_admin_access
- Enum
- Working in this repository
- [2026-05-18 – 2026-05-19] — Railway Deployment & Docker
- install_pi.sh
- models/__init__.py
- postcss.config.mjs
- .validate_currency
- [2026-05-23 – 2026-05-24] — Maersk Shadow DOM & Stealth Upgrades
- test_normalizer.py
- [2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash
- scripts
- Architecture Overview
- [2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes
- alembic
- MaerskConnector
- main
- .extract_charge_breakdown
- [2026-06-02] — Hapag-Lloyd Transshipment & Duplicate Fix
- clean_selector_memory
- [2026-05-25 – 2026-05-26] — VNC Display Isolation & Proxy Integration

## God Nodes (most connected - your core abstractions)
1. `RateSearchRequest` - 158 edges
2. `cn()` - 87 edges
3. `CarrierResultStatus` - 69 edges
4. `QuoteSchema` - 67 edges
5. `User` - 58 edges
6. `PortManager` - 58 edges
7. `HapagLloydConnector` - 56 edges
8. `CMAConnector` - 55 edges
9. `BaseCarrierConnector` - 50 edges
10. `OOCLConnector` - 49 edges

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

## Communities (132 total, 23 thin omitted)

### Community 1 - "BaseCarrierConnector"
Cohesion: 0.05
Nodes (32): ABC, BaseCarrierConnector, NotAvailableConnector, Any, Open the price breakdown / detail view for a specific quote. Args: quote_ref:…, Extract individual charge line items from the price breakdown. Returns: List of…, Normalize extracted data into a QuoteSchema using the normalizer. Args:…, Abstract base class for carrier portal connectors. (+24 more)

### Community 2 - "cn"
Cohesion: 0.10
Nodes (35): Reuse the primitives, New primitives — `frontend/src/components/ui/`, LoadingState(), Badge(), badgeVariants, Dot(), Card(), CardContent() (+27 more)

### Community 3 - "user_routes.py"
Cohesion: 0.09
Nodes (66): admin_delete_user(), AdminLoginRequest, approve_user(), CarrierOverrideRequest, Config, create_custom_port_endpoint(), CustomPortRequest, delete_carrier_override_endpoint() (+58 more)

### Community 4 - "auth_routes.py"
Cohesion: 0.09
Nodes (44): clear_session_cookie(), get_current_user_optional(), login(), LoginRequest, logout(), AsyncSession, BaseModel, post (+36 more)

### Community 5 - "browser_cleanup.py"
Cohesion: 0.11
Nodes (32): _is_chrome(), _is_playwright_driver(), _kill(), kill_profile_browsers(), _proc_supported(), Cleanup for Chrome browsers and temporary profiles that a failed close leaves…, Kill every automated Chrome and Playwright driver. Only call this when no…, Delete per-search profile copies ("chrome_profile_<carrier>_tmp_<id>") and… (+24 more)

### Community 6 - "OOCLConnector"
Cohesion: 0.17
Nodes (6): OOCLConnector, Attempts to automatically click the Cloudflare Turnstile 'Verify you are human'…, main(), main(), run_test(), main()

### Community 7 - "api.ts"
Cohesion: 0.09
Nodes (54): AdminDashboard(), HomeContent(), BackendConfigModal(), BackendConfigModalProps, addCarrierOverride(), addCustomPort(), adminUserAction(), AuthUser (+46 more)

### Community 8 - "PortManager"
Cohesion: 0.05
Nodes (47): get_countries(), get_port(), get_suggestions(), get, Get list of countries for autocomplete dropdown., Get specific port details by UN/LOCODE., Get port suggestions for autocomplete., search() (+39 more)

### Community 9 - "safe_step.py"
Cohesion: 0.18
Nodes (12): capture_page_state(), Page Observer — captures page state (screenshot, DOM, visible text) on failure., Captures screenshot, DOM HTML, and inner text of the current page. Saves…, generate_report(), Repair Report — generates and saves diagnosis reports on Playwright selector…, Assembles a comprehensive repair report and writes it as JSON and Markdown…, Safe Step — Playwright action execution wrapper with manual intervention pause…, Updates the status of a carrier search in the database. (+4 more)

### Community 10 - "CMAConnector"
Cohesion: 0.06
Nodes (25): CMAConnector, Ensures 'Ramp' is explicitly selected under 'Type of location' toggle buttons…, Scans for Route, POL (Port of Loading), or POD (Port of Discharge) dropdown…, Clears the currently selected Destination port tag/card, re-types the locode,…, Dynamically extracts any recommended 5-letter POD LOCODE mentioned in the…, Detects if CMA CGM displayed an advisory banner message: "Looking for AEJEA or…, Handles the 'Customer account' -> 'Role (you are acting as)' dropdown on CMA…, Repeatedly clicks 'More results' if visible to load ALL quotes on the page. (+17 more)

### Community 11 - "sys"
Cohesion: 0.07
Nodes (22): # NOTE: No start date fill needed — schedule page defaults to today,, Hapag-Lloyd Live Connector -- Playwright automation. Credentials read from env:…, Interactive Headed Login Helper for Maersk. Opens real Chrome using the…, Interactive Headed Login Helper for ONE (Ocean Network Express). Opens Chrome…, Wrapper script to set Windows event loop policy before starting Uvicorn. This…, parse_hapag_pdf(), scrape_hapag_freetime(), debug_cma() (+14 more)

### Community 12 - "CarrierSearchResult"
Cohesion: 0.23
Nodes (12): fetch_port_fixes(), Saved port name fixes, marked built in or admin-added, and the ports each…, CarrierSearchResult, Tracks the result of searching a specific carrier for a rate search., Copy the connector's "port not found" note onto the result row, if it made one., _store_port_not_found(), _miss(), Port name fixes: connectors note ports their own search couldn't find, results… (+4 more)

### Community 13 - "auth_service.py"
Cohesion: 0.08
Nodes (37): AuditLog, AuthSession, Stores hashed active session tokens., Stores security and operational audit trail entries., create_session(), get_user_for_token(), hash_token(), AsyncSession (+29 more)

### Community 14 - "._fs_dismiss_modals"
Cohesion: 0.17
Nodes (8): Lock, Full FreightSmart phase: login â†’ fill quote form â†’ search â†’ extract rows., Runs CONCURRENTLY with the rest of the FreightSmart form-filling flow and…, Closes FreightSmart popups. Order matters: 1. Cookie Notice consent ("Accept…, Two-step FreightSmart login: 1. freightsmart.oocl.com/app/login â€” email +…, Fills the origin/destination 'Enter Port or Door Point' autocomplete. The…, Opens the 'Container Type and Quantity' picker (General tab: 20GP/20RF(NOR),…, Event

### Community 15 - "HapagLloydAPIConnector"
Cohesion: 0.06
Nodes (23): HapagLloydAPIConnector, Any, AsyncClient, Direct REST API connector for Hapag-Lloyd Prices API v2.1.4., API connectors do not require browser login sessions., Required abstract method implementation; delegates to run_full_search., Batch (RFQ) mode: the base implementation drives a browser page, so answer from…, No browser session to reset between batch routes. (+15 more)

### Community 16 - "preferences.ts"
Cohesion: 0.09
Nodes (33): LaunchIntro(), SearchHistoryItem, derive(), Derived, startOfDay(), UsageStats(), ChoiceCard(), Toggle() (+25 more)

### Community 17 - "test_rfq_agent.py"
Cohesion: 0.10
Nodes (36): API routes for RFQ parsing agent., RFQParseResult, asyncio, Unit tests for the Gemini AI RFQ Agent service (parse_rfq). Includes…, Test Image 2: Air rate request generates 3 drafts to Glenn (AWOT), Jing Hui…, Test Image 4: Steel Plate ex Pasir Gudang / Tanjung Pelepas for 20' & 40'., Test Guardrail: Detects Reefer container request and returns unsupported_cargo…, Test Guardrail: Detects LCL request. (+28 more)

### Community 18 - "database.py"
Cohesion: 0.15
Nodes (18): get_sync_url(), run_migrations_offline(), run_migrations_online(), _create_sqlite_engine(), _get_database_url(), _get_engine(), get_session(), _get_session_maker() (+10 more)

### Community 19 - "SocialWidget.tsx"
Cohesion: 0.10
Nodes (34): ACCENT_COLORS, errorMessage(), relativeTime(), resizeImageToDataUrl(), SocialWidget(), SocialWidgetProps, EMOJI_GROUPS, EmojiPicker() (+26 more)

### Community 20 - "LiveSearchProgress.tsx"
Cohesion: 0.07
Nodes (33): ChatWidget(), ChatWidgetProps, Message, ACTION_STATUSES, ChipModel, describe(), EMPTY_STATUSES, formatElapsed() (+25 more)

### Community 21 - "RateSearchRequest"
Cohesion: 0.08
Nodes (21): GreenXConnector, date, Overrides base search runner to query all 3 sizes at once and cache the…, Type a LOCODE into the autocomplete field and click the first visible dropdown…, Find quantity input next to or below label_text and fill it., Find the exact individual quote card container row encompassing dates, rates,…, Dismiss any cookie/alert modal that would intercept pointer events., Splits a single raw multi-container quote card into multiple QuoteSchema… (+13 more)

### Community 22 - "social_routes.py"
Cohesion: 0.12
Nodes (28): get_current_user(), Dependency that strictly requires an authenticated active member., get_conversation(), list_colleagues(), poke_colleague(), PokeRequest, AsyncSession, BaseModel (+20 more)

### Community 23 - "playwright_async_api"
Cohesion: 0.16
Nodes (8): dump_options(), main(), Diagnostic: dump ALL dropdown options (text + innerHTML) when typing 'DEHAM'…, check_and_wait_for_captcha(), login(), main(), Script to test Playwright browser launching using your REAL Google Chrome…, playwright_async_api

### Community 24 - "backend/main.py"
Cohesion: 0.06
Nodes (34): api_route, health(), lifespan(), get, websocket, Infreight Ocean Carrier Rate Automation — FastAPI Application. Main entry point…, Check if the VNC viewer is available (production only, where Xvfb runs)., Proxy WebSocket connections to legacy local x11vnc at localhost:5900. (+26 more)

### Community 25 - "rate_search_routes.py"
Cohesion: 0.07
Nodes (48): approve_repair(), ApproveRepairRequest, chat_endpoint(), ChatRequest, create_batch_rate_search(), _contains(), _looks_like(), _norm() (+40 more)

### Community 26 - "MSCConnector"
Cohesion: 0.16
Nodes (8): format_to_iso_date(), MSCConnector, Playwright-based automation for MSC (Mediterranean Shipping Company)., Handles the MSC login flow., Clicks Instant Quote, fills form, clicks Search., Detects and clicks the 'Ramp' delivery/haulage option if MSC displays Ramp /…, Parse '14 Jun 2026' to 'YYYY-MM-DD, test_msc()

### Community 27 - "parse_rfq"
Cohesion: 0.12
Nodes (27): parse_rfq_endpoint(), post, Parse a free-text RFQ email or message into a structured RateSearchRequest…, _call_native_gemini_api(), _detect_booking_confirmation(), _detect_dual_mode_enquiry(), _detect_mode_by_hierarchy(), _detect_unsupported_cargo() (+19 more)

### Community 28 - "RateSearchForm.tsx"
Cohesion: 0.11
Nodes (29): 0. The one invariant, CarrierMultiSelect(), CarrierMultiSelectProps, isAllCarriers(), toggleAllCarriers(), toggleCarrierSelection(), RateSearchForm(), RateSearchFormProps (+21 more)

### Community 29 - "AIBrowserAgent"
Cohesion: 0.13
Nodes (15): AIBrowserAgent, Capture the current page as a PNG screenshot., Build the prompt with task description and action history., Parse Gemini's response into an action dict., Call Gemini API with exponential backoff retry., Execute a parsed action on the browser page., Detect if the agent is stuck repeating the same action., Find all visible interactive elements and format them as a prompt guide. (+7 more)

### Community 30 - "job_service.py"
Cohesion: 0.11
Nodes (33): close_all_active_connectors(), get_connector(), Get the appropriate connector for a carrier. If USE_MOCK_CARRIERS=true: returns…, Force close all active carrier connectors and their Playwright Chrome windows., get_async_session_maker(), Get the session maker for use outside of FastAPI dependency injection., Quote, Represents a single freight quote from a carrier. (+25 more)

### Community 31 - "ONEConnector"
Cohesion: 0.08
Nodes (15): ONEConnector, _classify(), fill_container_card(), date, Parses ONE QUOTE Free Time popover text for DESTINATION ONLY. Ignores Origin…, Splits a single raw multi-container quote card into multiple QuoteSchema…, Tries to click a matching option from ONE's visible dropdown. Returns True only…, Extracts 5-letter UN/LOCODE from strings like 'Singapore [SGSIN]' or 'Singapore… (+7 more)

### Community 32 - "_Page"
Cohesion: 0.15
Nodes (8): _connector(), _Locator, _Page, Maersk's login page redirects to the Hub a few seconds after loading when the…, Sits on /portaluser/login, then redirects after `redirect_after` URL reads., test_login_uses_saved_session_after_late_redirect(), test_wait_detects_late_redirect(), test_wait_detects_login_form()

### Community 33 - "Engineering Report: Sourcing Portal Enhancements & Scraping Pipeline Stability"
Cohesion: 0.08
Nodes (23): 1. Anti-Bot Mitigation & CAPTCHA Human-in-the-Loop Recovery, 2. Sourcing Parallelization & Surcharges Optimization, 3. Autocomplete Intelligence & Location Mapping, 4. Scraper Pipeline Maintenance, 5. Infrastructure & DevSecOps Enhancements, Business Value, Business Value, Business Value (+15 more)

### Community 34 - "Changelog"
Cohesion: 0.09
Nodes (22): [2026-05-29 – 2026-05-30] — Hapag-Lloyd Full Integration, [2026-05-31] — Multi-Instance Support & Charge Classification, [2026-06-01] — Hapag-Lloyd Sold Out Detection & Date Parsing, [2026-06-03] — CMA CGM Routing & Free Time Extraction, [2026-07-03] — Robustness Review & Multi-Port Quick Search Fixes, [2026-07-08] — OOCL E-Quote Calendar Navigation, cheapest E-Spot selection, and E-Quote/E-Spot isolation refinements, [2026-07-09] — Hapag-Lloyd Quick Quotes pairing and selection simplification, Changelog (+14 more)

### Community 35 - "react"
Cohesion: 0.06
Nodes (51): UserRecord, AdminAnalytics, AdminOverview(), AdminOverviewProps, AdminOverviewUser, AnalyticsRange, Attention, attentionItems() (+43 more)

### Community 36 - "package.json"
Cohesion: 0.12
Nodes (15): engines, node, name, packageManager, private, version, react-dom, tailwind-merge (+7 more)

### Community 37 - "test_hapag_freetime.py"
Cohesion: 0.10
Nodes (23): Looks up standard destination demurrage/detention free time days., (days, estimated): estimated when the destination has no entry in the free time…, _apply_freetime_to_quote(), freetime_days(), match_freetime_entry(), Any, Days for this container from a table entry ({"20GP": n, "40GP": n} or a bare…, The table entry whose country name appears in `text` as whole words. Whole… (+15 more)

### Community 38 - "RateResults.tsx"
Cohesion: 0.08
Nodes (46): QuoteBreakdownDrawer(), QuoteBreakdownDrawerProps, Breakdown(), ChargeList(), dateValue(), freeTimeText(), isSoldOut(), isSpot() (+38 more)

### Community 39 - "SearchQueueManager"
Cohesion: 0.12
Nodes (11): Lock, Marks a search as completed internally so we can track the auto-release timeout., Called periodically in a background task to check if the user has held the lock…, Forcefully clears all queued searches and the active lock. Useful for…, Returns or creates an asyncio.Lock for a specific carrier code to prevent…, Adds a search to the queue and waits until it becomes the active search. Event-…, Singleton manager to enforce a FIFO queue for rate searches. Since web scraping…, Returns the current position of the search in the queue. 0 means it is the… (+3 more)

### Community 40 - "ChargeCategory"
Cohesion: 0.26
Nodes (18): ChargeCategory, classify_charge(), Classify a charge line item based on its name, amount, section heading, and…, Tests for charge classifier., test_basic_ocean_freight(), test_cwx_heavy_weight_charge(), test_destination_charges(), test_discount() (+10 more)

### Community 41 - "Frontend Redesign — Componentry Design System, Workspace & Launch Intro (2026-09-07)"
Cohesion: 0.11
Nodes (17): 1. Design system foundation (`082b43a`), 2. Bugs found and fixed during the restyle, 3. Workspace + launch intro (`21ade75`), 4. Follow-up fixes (`2f9d92b`), 5. Verification, 6. Known limitations / candidate follow-ups, 7. Conventions to follow from here, Dependencies added (5, all small, no runtime lib dependency on Componentry) (+9 more)

### Community 42 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 43 - "login/page.tsx"
Cohesion: 0.11
Nodes (18): nextConfig, LoginContent(), LoginModal(), LoginModalProps, hexToRgb01(), sanitizeHexColor(), SilkAurora(), SilkAuroraProps (+10 more)

### Community 44 - "test_carrier_timeout.py"
Cohesion: 0.19
Nodes (10): CrashingConnector, HangingConnector, asyncio, A carrier whose browser hangs must be stopped after CARRIER_SEARCH_TIMEOUT_SEC…, Hangs on the sizes in `hang_on`; answers NO_QUOTES_AVAILABLE for the rest., Like a real connector whose tab dies: reports a crash, then never returns., _run(), test_crashed_tab_stops_the_carrier_without_waiting_for_the_timeout() (+2 more)

### Community 45 - "test_port_logging_and_mismatch.py"
Cohesion: 0.16
Nodes (16): get_route_health(), Get carrier search reliability & route health matrix across origin-destination…, _detect_port_mismatch(), Detects port mismatch for origin or destination. Returns: - True if verified…, asyncio, Unit tests for Port Search Reliability Logging and Mismatch Detection., Test that /api/admin/route-health endpoint returns formatted route health…, Test that matching LOCODE or City + Country code returns False (Verified Match). (+8 more)

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
Cohesion: 0.08
Nodes (20): Override to immediately return CONNECTOR_NOT_AVAILABLE., Execute the full search flow with Progressive Lazy Loading: 1. Login 2. Search…, Extracts freetime, demurrage, and detention from the 'Import D&D fees' tab…, Extracts the routing details from the 'Route & other details' accordion.…, Splits a single raw multi-container quote card into multiple QuoteSchema…, _generate_maersk_mock_quotes(), _generate_msc_mock_quotes(), _generate_one_mock_quotes() (+12 more)

### Community 50 - "test_self_healing.py"
Cohesion: 0.24
Nodes (13): get_approved_selector(), _load_memory(), Selector Memory — stores and retrieves human-approved selector patches., Loads memory JSON file. Returns empty dict if file is missing or invalid., Saves memory dict back to JSON file., Looks up if there is an approved replacement selector for the given carrier and…, Stores an approved replacement selector., Marks any proposed selector for this step as REJECTED. (+5 more)

### Community 51 - "CurrencyManager"
Cohesion: 0.23
Nodes (7): convert_currency_to_usd(), CurrencyManager, get_all_exchange_rates(), Any, Currency Exchange Rate Service — manages currency conversions and custom…, update_exchange_rate(), threading

### Community 52 - "parse_msc_modal_charges"
Cohesion: 0.24
Nodes (8): parse_msc_modal_charges(), Parses charges from MSC BreakdownModal text. Correctly includes charges whose…, Test MSC charges parsing for Singapore to Conakry, Guinea (40GP). Charges with…, Test when only some surcharges have the payment condition., test_msc_charges_mixed_conditions(), test_msc_charges_singapore_to_conakry_guinea(), Verify MSC charge extraction logic parses Panama Canal Surcharge properly., test_msc_charge_extraction_logic()

### Community 53 - "charge_classifier.py"
Cohesion: 0.33
Nodes (5): Charge Classifier — rule-based classification of freight charge line items.…, parse_hapag_section(), Unit test to verify Hapag-Lloyd Price Breakdown section classification logic.…, test_hapag_section_parsing_order(), test_hapag_surcharges_classification()

### Community 54 - "🚢 Infreight Sourcing & Ocean Rate Automation System"
Cohesion: 0.14
Nodes (13): 1. Multi-Carrier Automation Engine, 2. Intelligent Surcharge & Charge Classifier Engine (`charge_classifier.py`), 3. Container Comparison Matrix & Excel Export Engine, 🚢 Infreight Sourcing & Ocean Rate Automation System, 🌟 Key Capabilities, 📄 License & Confidentiality, Prerequisites, 🛠️ Project Structure (+5 more)

### Community 55 - "AdminUsers.tsx"
Cohesion: 0.20
Nodes (14): AdminUserRecord, AdminUsers(), AdminUsersProps, ago(), AuditEntry, Avatar(), Filter, initials() (+6 more)

### Community 56 - "[2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split"
Cohesion: 0.15
Nodes (13): G2 Stress Test: "Hi, Please book the below as per your quote ref INF-2026-0842:…, H1 Stress Test: Table with 2 distinct rows: Row 1: POL Singapore, POD Jakarta,…, test_g2_booking_confirmation_guardrail(), test_h1_table_deduplication_two_pairs(), [2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split, Booking Confirmation / Instructions Intercept Guardrail G2 (`rfq_agent.py` & `RfqInputSection.tsx`), Commercial Sales Desk Intelligence (`sales_notes`), Deterministic Port Alias Resolver (`ports_aliases.json`) (+5 more)

### Community 57 - "RateSearch"
Cohesion: 0.10
Nodes (24): get_recent_search_status_context(), Chat Service — manages conversational AI queries from the frontend user using…, Queries the database for the most recent rate search status to give the chatbot…, Base, SQLAlchemy models for quotes and individual charge line items., RateSearch, SQLAlchemy models for rate searches and carrier search results., Represents a rate search request from an employee. (+16 more)

### Community 58 - "🛠 Detailed Carrier Log"
Cohesion: 0.15
Nodes (12): 🛠 Detailed Carrier Log, 🟢 GreenX, 🟠 Hapag-Lloyd, Infreight Ocean Carrier Rate Automation — Development Log, 🚀 Key Highlights & Architectural Changes, 🔌 Local Laptop Deployment (Self-Hosted Worker), 🔵 Maersk, 💗 ONE (Ocean Network Express) (+4 more)

### Community 59 - "._fs_pair_and_select"
Cohesion: 0.33
Nodes (4): get_booking_start_date(), date, Applies the business rules and pairs FreightSmart prices with crawled…, OOCL — FreightSmart Price Quotes (E-Quote / E-Spot) Paired With Sailing Schedules

### Community 60 - ".login"
Cohesion: 0.20
Nodes (6): _is_logged_in_url(), True once Maersk has moved past the login pages to a signed-in page., Types text character by character into a given locator or element handle with…, Clicks an element with pre-click and post-click human-like reaction pauses., Wait until the login page either redirects to a signed-in page or shows its…, test_logged_in_url()

### Community 61 - "._fs_extract_rows"
Cohesion: 0.18
Nodes (7): clean_vessel_name(), _parse_date(), parse_oocl_date(), Parses one FreightSmart result card's inner text into a raw row dict. Text-…, Opens the Details dialog for a card, clicks the Charge Breakdown tab, extracts…, Collects result cards from the FreightSmart quote results page., OOCL Nearby Route Recommendations Suppression (`oocl_connector.py`)

### Community 62 - ".run_full_search"
Cohesion: 0.22
Nodes (3): Serves one container-type cycle from the cached merged quote set: -…, One crawl serves all container-type cycles (cached), combining: 1. Sailing…, Public oocl.com Chromium sailing schedule crawl bypassed per directive. All…

### Community 63 - "[2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup"
Cohesion: 0.22
Nodes (8): [2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup, Chromium Cache Auto-Cleanup (Railway Storage Bloat Prevention), CMA CGM — 30-Second Timeout on Sold Out Cards, CMA CGM — Free Time Regex Too Strict, CMA CGM — Routing Regex Not Matching "via LEKKI, LA, NG", Excel Export — Routing & Free Time Columns Always Empty, Excel Export — Sold Out Rows Not Showing, Maersk — Hardcoded Port Overrides

### Community 64 - "ai_repair_agent.py"
Cohesion: 0.29
Nodes (7): _local_fuzzy_repair(), AI Repair Agent — diagnoses Playwright step failures and suggests selector…, A local rule-based heuristic to locate reasonable buttons or inputs when Gemini…, Analyzes the failure context and DOM content to suggest a selector repair. Uses…, suggest_fix(), test_ai_repair_agent_offline_fallback(), bs4

### Community 65 - "layout.tsx"
Cohesion: 0.22
Nodes (7): frontend_src_app_globals, instrumentSans, inter, metadata, viewport, ThemeProvider(), next-themes

### Community 66 - "GreenX — Surcharge Intake Fix (2026-06-30)"
Cohesion: 0.22
Nodes (8): Charges that must be taken into the final value (USD only), Files changed, Fix, GreenX — Surcharge Intake Fix (2026-06-30), Per-B/L charges (billed once per booking, added in full to *each* container type), Problem, Root cause, Verification

### Community 67 - "Admin Page & Port Prioritization Guide"
Cohesion: 0.25
Nodes (7): 1. Popular Ports (UN/LOCODEs), 2. Boosted Countries, Admin Page & Port Prioritization Guide, 🔒 How to Access the Admin Page, ⚙️ How to Use Port Prioritization, ⚡ Important Notes, 📝 Step-by-Step Example

### Community 68 - "[2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning"
Cohesion: 0.15
Nodes (12): Verifies the "I am the price owner" radio is genuinely checked, piercing shadow…, [2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning, [2026-07-03] — OOCL FreightSmart Autoclear, Hapag Price Leak & Redirect fixes, Maersk Cache Scoping, Dallas Overrides, Hapag-Lloyd — Configurable Pacing & Redundant-Wait Removal, Hapag-Lloyd — Price Leaks, Column Matching, and Redirect Recovery, Job Scheduler — Concurrency Default, Maersk — 0.0-USD / "Not Open" Card Flakiness (the "Quotes Found but Empty Excel" root causes), Maersk — Caching Scope & Selector Tuning (+4 more)

### Community 69 - "detect_manual_action_required"
Cohesion: 0.29
Nodes (7): detect_manual_action_required(), Manual Action Detector — identifies pages requiring human verification (2FA,…, Scans the current Playwright page to see if a CAPTCHA, Cloudflare challenge,…, asyncio, test_manual_action_detector_captcha(), test_manual_action_detector_text(), test_safe_step_success()

### Community 71 - "dependencies"
Cohesion: 0.15
Nodes (13): dependencies, class-variance-authority, clsx, exceljs, lucide-react, next, next-themes, @radix-ui/react-slot (+5 more)

### Community 72 - "deploy"
Cohesion: 0.25
Nodes (7): build, builder, deploy, restartPolicyMaxRetries, restartPolicyType, startCommand, $schema

### Community 73 - "._fs_iterate_calendar_dates"
Cohesion: 0.33
Nodes (4): _click_date_strip_item(), _open_calendar(), Iterates through the FreightSmart results date calendar to collect E-Quote and…, setter

### Community 74 - "test_oocl_cwx.py"
Cohesion: 0.48
Nodes (6): asyncio, test_oocl_cwx_different_port_pair_different_amount(), test_oocl_cwx_heavy_weight_charge_not_applied_40gp(), test_oocl_cwx_heavy_weight_charge_not_applied_under_threshold(), test_oocl_cwx_port_pair_surabaya_karachi(), test_oocl_cwx_port_pair_without_cwx()

### Community 75 - "Summary of Changes — July 20, 2026"
Cohesion: 0.29
Nodes (6): 1. AI RFQ Front Door & Air Freight Support (Phase A), 2. Multi-Origin & Gappy List Parsing for Sea RFQs (Phase B), 3. Search Form Streamlining (Form Input Restrictions), 4. Native Gemini 2.5 Flash API & Chatbot Resiliency, 5. Verification & Test Suite, Summary of Changes — July 20, 2026

### Community 76 - "capture_failure_context"
Cohesion: 0.33
Nodes (5): capture_failure_context(), Exception, Failure Detector — parses and structures error context from failed Playwright…, Assembles a standardized diagnostic dictionary containing all available details…, test_failure_detector()

### Community 77 - "test_one_premium_override.py"
Cohesion: 0.40
Nodes (3): MockCard, Unit test for ONE connector and charge classifier Premium Cargo Service…, test_premium_cargo_service_override()

### Community 78 - "resolve_port_alias"
Cohesion: 0.33
Nodes (6): _load_port_aliases_config(), Deterministically resolves a port string against ports_aliases.json and the…, resolve_port_alias(), Test that resolve_port_alias cleans 'City, Country' and parenthetical notes to…, test_resolve_city_country_format_to_clean_database_port_name(), Clean Search Dropdown Port Name Resolution (`rfq_agent.py` & `port_manager.py`)

### Community 79 - "json"
Cohesion: 0.09
Nodes (18): AI Browser Agent — Vision-based browser automation using Gemini Flash. This…, Experimental AI Agent Test -- Maersk Quote Search This script tests the AI…, get_title(), Script to test fetching CMA CGM pricing page using Bright Data Web Access HTTP…, test_brightdata_api(), Hapag-Lloyd end-to-end test using run_full_search., Verification script for ONE multi-container implementation., Test ONE connector with Taichung -> New York route. (+10 more)

### Community 80 - "test_auth_routes.py"
Cohesion: 0.29
Nodes (6): ambiguous_python_import_b35980c0aa01, asyncio, Integration tests for authentication, legacy user password setup, pending…, test_full_auth_lifecycle(), httpx, pytest_asyncio

### Community 81 - "Design system — read before touching any UI"
Cohesion: 0.33
Nodes (5): Animation rules, Client-only preferences, Design system — read before touching any UI, This is NOT the Next.js you know, Use tokens, not raw colours

### Community 82 - "test_panama_canal_surcharge.py"
Cohesion: 0.18
Nodes (14): is_weight_surcharge_applicable(), Evaluates whether a weight-tier or overweight surcharge is applicable for the…, classify_and_organize_charges(), Takes raw charge line items and classifies them. Args: raw_charges: list of…, test_classify_and_organize(), asyncio, Verify non-applicable weight tier surcharges are excluded from final value for…, Verify regex extraction of Estimated Transportation Days from Hapag-Lloyd modal… (+6 more)

### Community 83 - "handle_chat_query"
Cohesion: 0.40
Nodes (5): handle_chat_query(), _local_chatbot_fallback(), Intelligent responder for search status, carrier guidance, air/sea info, and…, Sends the chat message and history to native Gemini 2.5 Flash API. If Gemini…, test_chat_service_offline_fallback()

### Community 84 - "_dismiss_once"
Cohesion: 0.40
Nodes (3): _dismiss_once(), Shadow-DOM-aware check for whether the onboarding tour heading is on screen., Position-based fallback for the onboarding tour popup: instead of guessing its…

### Community 85 - "get_me"
Cohesion: 0.67
Nodes (3): get_me(), get, Get profile of currently signed-in user.

### Community 86 - "BatchProgressPanel.tsx"
Cohesion: 0.31
Nodes (8): BatchProgressPanel(), BatchProgressPanelProps, cheapest(), Filter, lanePhase(), Phase, PHASE_STYLE, BatchRouteResult

### Community 88 - "os"
Cohesion: 0.10
Nodes (28): argparse, asyncio, Base Carrier Connector — abstract base class for all carrier connectors. Each…, CMA CGM Live Connector — Playwright automation. Credentials read from env:…, GreenX (Evergreen) Live Connector - Playwright automation., Hapag-Lloyd Prices API Connector (REST API v2.1.4). Provides real-time rate…, OOCL Live Connector â€” Playwright automation for Sailing Schedules., Carrier Registry — factory for getting the right connector per carrier. When… (+20 more)

### Community 89 - "[2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History"
Cohesion: 0.40
Nodes (5): [2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History, Admin User Search History & SGT GMT+8 Conversion (`AdminDashboard.tsx`), GreenX (Evergreen) Card Isolation & Surcharge Parsing (`greenx_connector.py`), Multi-Route Batch Execution Engine (`batch_engine.py`), OOCL FreightSmart 28-Day Calendar Expansion (`oocl_connector.py`)

### Community 90 - "devDependencies"
Cohesion: 0.22
Nodes (9): devDependencies, eslint, eslint-config-next, tailwindcss, @tailwindcss/postcss, @types/node, @types/react, @types/react-dom (+1 more)

### Community 92 - "[2026-08-07] — Carrier Specific Free Time, Demurrage/Detention Splitting, MSC CDD Surcharges, OOCL Nearby Route Filtering & Favicon Cache Busting"
Cohesion: 0.40
Nodes (5): [2026-08-07] — Carrier Specific Free Time, Demurrage/Detention Splitting, MSC CDD Surcharges, OOCL Nearby Route Filtering & Favicon Cache Busting, Demurrage & Detention Split Fields Across System (`schema.py`, `msc_connector.py`, `maersk_connector.py`, `one_connector.py`, `greenx_connector.py`, `cma_connector.py`, `oocl_connector.py`, `ResultsTable.tsx`, `excel_export.py`), Favicon Cache Busting & Brand Icon (`layout.tsx`, `icon.png`, `favicon.ico`), Hapag-Lloyd MHD (Merchant Haulage Detention) PDF Tariff Scraper (`hapag_freetime_scraper.py`, `hapag_freetime.json`), MSC Cargo Data Declaration [CDD] & Working Days Free Time (`msc_connector.py`)

### Community 95 - "eslint.config.mjs"
Cohesion: 0.50
Nodes (3): eslintConfig, eslint, eslint-config-next

### Community 96 - "frontend/README.md"
Cohesion: 0.50
Nodes (3): Deploy on Vercel, Getting Started, Learn More

### Community 97 - "pytest"
Cohesion: 0.18
Nodes (7): parse_hapag_card_text_mock(), Verify that multi-leg/feeder routes take the final arrival ETA and 28 days TT., Mock implementation of the JS evaluate logic inside hapag_lloyd_connector.py., test_hapag_multi_leg_schedule_extraction(), asyncio, test_one_breakdown_currency_and_arbitrary_destination_classification(), pytest

### Community 98 - "[2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control"
Cohesion: 0.40
Nodes (5): [2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control, Concurrency Limit Queue & Admin Control Panel, MSC — Mediterranean Shipping Company Connector Implementation, ONE — Inbound Free Time Swap & Scraper Upgrade, OOCL — Orient Overseas Container Line Connector Implementation

### Community 99 - "[2026-08-04 - 2026-08-06] — CMA CGM Dynamic RAMP/POD Rerouting, Brand Excel Styling, Port Synonym Matching & Tunnel Relays"
Cohesion: 0.40
Nodes (5): [2026-08-04 - 2026-08-06] — CMA CGM Dynamic RAMP/POD Rerouting, Brand Excel Styling, Port Synonym Matching & Tunnel Relays, Brand-Aligned Excel Export Styling (`excel_export.py`), CMA CGM Dynamic RAMP / POD Advisory Banner Detection (`cma_connector.py`), Dynamic Carrier Port Overrides & Admin Registry (`PortManager`, `AdminDashboard.tsx`), Railway WebSocket Tunnel Relay & Failover (`tunnel_client.py`, `run_tunnel_client.bat`, `FailoverFetch`)

### Community 100 - "sort_container_types"
Cohesion: 0.40
Nodes (4): Sort container types in standard order: DRY 20 (20GP) -> DRY 40 (40GP) -> DRY…, sort_container_types(), test_container_types_standard_ordering(), model_validator

### Community 101 - "[2026-05-20 – 2026-05-22] — Port Resolution & Frontend Improvements"
Cohesion: 0.50
Nodes (4): [2026-05-20 – 2026-05-22] — Port Resolution & Frontend Improvements, Excel Export — ETA Column & Container Type Header, Frontend Light Mode & CORS Fix, Port Resolution System

### Community 102 - "verify_admin_access"
Cohesion: 0.67
Nodes (3): Request, Verify that caller has admin privileges via session cookie, Bearer token, or…, verify_admin_access()

### Community 103 - "Enum"
Cohesion: 0.67
Nodes (3): CarrierCode, Enum, str

### Community 106 - "[2026-05-18 – 2026-05-19] — Railway Deployment & Docker"
Cohesion: 0.67
Nodes (3): [2026-05-18 – 2026-05-19] — Railway Deployment & Docker, Persistent Chrome Profiles on Railway Volume, Railway Deployment Setup

### Community 117 - "[2026-05-23 – 2026-05-24] — Maersk Shadow DOM & Stealth Upgrades"
Cohesion: 0.50
Nodes (4): [2026-05-23 – 2026-05-24] — Maersk Shadow DOM & Stealth Upgrades, Maersk — 2FA/CAPTCHA Human-in-the-Loop via noVNC, Maersk — Login Credential Autofill Corruption, Maersk — Shadow DOM Piercing for MDS Web Components

### Community 118 - "test_normalizer.py"
Cohesion: 0.21
Nodes (9): calculate_final_freight_value(), Calculate the final freight value from a list of classified charges. Args:…, Tests for normalizer / final freight value calculator., test_basic_calculation(), test_date_standardization(), test_no_charges(), test_one_breakdown_parsing(), test_only_excluded() (+1 more)

### Community 121 - "[2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash"
Cohesion: 0.40
Nodes (5): [2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash, AI RFQ Front Door & Air Freight Support, Multi-Origin & Gappy List Parsing (Sea RFQs), Native Gemini 2.5 Flash Direct API Integration, Search Form Streamlining

### Community 122 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, dev, lint, start

### Community 123 - "Architecture Overview"
Cohesion: 0.50
Nodes (4): Architecture Overview, Carrier Connector Lifecycle, Charge Classification Rules, Search Flow

### Community 124 - "[2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes"
Cohesion: 0.50
Nodes (4): [2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes, CMA CGM — Chrome Profile Bypass, ONE — Date Formatting & Charge Breakdown Pollution, ONE — Date Picker Pre-selection Issue

### Community 126 - "MaerskConnector"
Cohesion: 0.07
Nodes (28): extract_locode_and_country(), MaerskConnector, Maersk Browser Connector — Playwright automation using your real Google Chrome…, Extracts LOCODE and country name from text like 'CASABLANCA, MOROCCO (MACAS)'…, # NOTE: Bright Data Web Unlocker proxies break Playwright browser sessions…, Extracts the port/city name by removing any UN/LOCODE parentheses (e.g.,…, Maps standard container search codes (e.g. 'DRY 20', '20GP') to Maersk Spot…, Scores a Maersk autocomplete dropdown suggestion. NOTE: The nested/indented… (+20 more)

### Community 129 - "[2026-06-02] — Hapag-Lloyd Transshipment & Duplicate Fix"
Cohesion: 0.67
Nodes (3): [2026-06-02] — Hapag-Lloyd Transshipment & Duplicate Fix, Hapag-Lloyd — Duplicate Sailings from Transshipment Vessels, Hapag-Lloyd — Routing Not Marked as Transit

### Community 131 - "clean_selector_memory"
Cohesion: 0.67
Nodes (3): clean_selector_memory(), fixture, Wipes the selector memory JSON file before and after each test.

### Community 132 - "[2026-05-25 – 2026-05-26] — VNC Display Isolation & Proxy Integration"
Cohesion: 0.67
Nodes (3): [2026-05-25 – 2026-05-26] — VNC Display Isolation & Proxy Integration, Bright Data ISP Proxy Integration, VNC Display Isolation for Concurrent Carriers

## Knowledge Gaps
- **312 isolated node(s):** `Config`, `install_pi.sh script`, `eslintConfig`, `nextConfig`, `name` (+307 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 926 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **23 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Changelog` connect `Changelog` to `[2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History`, `[2026-06-02] — Hapag-Lloyd Transshipment & Duplicate Fix`, `[2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control`, `[2026-08-04 - 2026-08-06] — CMA CGM Dynamic RAMP/POD Rerouting, Brand Excel Styling, Port Synonym Matching & Tunnel Relays`, `[2026-05-25 – 2026-05-26] — VNC Display Isolation & Proxy Integration`, `[2026-05-20 – 2026-05-22] — Port Resolution & Frontend Improvements`, `test_hapag_freetime.py`, `[2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning`, `[2026-05-18 – 2026-05-19] — Railway Deployment & Docker`, `[2026-08-07] — Carrier Specific Free Time, Demurrage/Detention Splitting, MSC CDD Surcharges, OOCL Nearby Route Filtering & Favicon Cache Busting`, `[2026-05-23 – 2026-05-24] — Maersk Shadow DOM & Stealth Upgrades`, `[2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split`, `[2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash`, `Architecture Overview`, `[2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes`, `[2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup`?**
  _High betweenness centrality (0.340) - this node is a cross-community bridge._
- **Why does `Maersk — Free Time Extraction from Card Text` connect `Changelog` to `RateResults.tsx`?**
  _High betweenness centrality (0.318) - this node is a cross-community bridge._
- **Are the 32 inferred relationships involving `RateSearchRequest` (e.g. with `create_batch_rate_search()` and `create_rate_search()`) actually correct?**
  _`RateSearchRequest` has 32 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `cn()` (e.g. with `Reuse the primitives` and `7. Conventions to follow from here`) actually correct?**
  _`cn()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 21 inferred relationships involving `CarrierResultStatus` (e.g. with `safe_step()` and `update_carrier_status()`) actually correct?**
  _`CarrierResultStatus` has 21 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Config`, `install_pi.sh script`, `eslintConfig` to the rest of the system?**
  _312 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `BaseCarrierConnector` be split into smaller, more focused modules?**
  _Cohesion score 0.05081967213114754 - nodes in this community are weakly interconnected._