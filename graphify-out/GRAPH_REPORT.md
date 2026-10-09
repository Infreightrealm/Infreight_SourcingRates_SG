# Graph Report - Infreight_SourcingRates_SG  (2026-10-09)

## Corpus Check
- 249 files · ~1,165,139 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 24 file(s) not represented in the graph (top: (none) 10, .bat 7, .conf 2)

## Summary
- 2402 nodes · 5940 edges · 136 communities (111 shown, 25 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 337 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b7cd63b2`
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
- cma_connector.py
- job_service.py
- database.py
- RateSearchRequest
- HapagLloydAPIConnector
- preferences.ts
- test_rfq_agent.py
- .run_full_search
- SocialWidget.tsx
- lucide-react
- GreenXConnector
- social_routes.py
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
- dependencies
- RateResults.tsx
- SearchQueueManager
- schemas.py
- Frontend Redesign — Componentry Design System, Workspace & Launch Intro (2026-09-07)
- compilerOptions
- ._fs_dismiss_modals
- test_carrier_timeout.py
- devDependencies
- dithered-logo.tsx
- 👥 The 5 Agent Roles
- HapagLloydConnector
- CarrierResultStatus
- ._dismiss_hapag_modals
- CurrencyManager
- MockCard
- test_hapag_freetime.py
- 🚢 Infreight Sourcing & Ocean Rate Automation System
- MaerskConnector
- [2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split
- ._parse_offer_response_to_quotes
- 🛠 Detailed Carrier Log
- silk-aurora.tsx
- json
- .extract_charge_breakdown
- [2026-06-30] — ONE Multi-Container & Sold-Out, GreenX Surcharge Intake, Free-Time Fixes, Maersk Diagnosis
- [2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup
- compute_admin_analytics
- export_maersk_login.py
- GreenX — Surcharge Intake Fix (2026-06-30)
- Admin Page & Port Prioritization Guide
- ._verify_price_owner_selected
- test_self_healing.py
- sort_container_types
- carrier_switches.py
- deploy
- .search_quotes
- .build_quick_quotes
- Summary of Changes — July 20, 2026
- test_port_logging_and_mismatch.py
- [2026-05-29 – 2026-05-30] — Hapag-Lloyd Full Integration
- resolve_port_alias
- test_brightdata.py
- MockCard
- Design system — read before touching any UI
- tunnel_client.py
- layout.tsx
- [2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning
- .select_cheapest_per_window
- .run_batch_persistent_search
- RateLimiter
- os
- get_connector
- search_port
- ref_fs
- ._mouse_glide_to
- [2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History
- ._split_or_none
- scripts
- frontend/README.md
- pytest
- [2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control
- .validate_currency
- NotAvailableConnector
- ._wait_for_captcha_resolution
- [2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash
- ._lookup_freetime
- Working in this repository
- [2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes
- install_pi.sh
- models/__init__.py
- postcss.config.mjs
- test_hapag_schedule_debug.py
- [2026-05-23 – 2026-05-24] — Maersk Shadow DOM & Stealth Upgrades
- ._execute_single_price_request
- User
- Architecture Overview
- [2026-05-20 – 2026-05-22] — Port Resolution & Frontend Improvements
- [2026-05-31] — Multi-Instance Support & Charge Classification
- [2026-06-03] — CMA CGM Routing & Free Time Extraction
- [2026-06-02] — Hapag-Lloyd Transshipment & Duplicate Fix
- HapagServiceUnavailableException
- ._parse_free_time_text
- main
- .search_port
- [2026-08-04 - 2026-08-06] — CMA CGM Dynamic RAMP/POD Rerouting, Brand Excel Styling, Port Synonym Matching & Tunnel Relays
- test_one_breakdown.py
- test_debug_cma_jebel_ali.py
- [2026-05-25 – 2026-05-26] — VNC Display Isolation & Proxy Integration
- alembic
- [2026-07-03] — Robustness Review & Multi-Port Quick Search Fixes

## God Nodes (most connected - your core abstractions)
1. `RateSearchRequest` - 161 edges
2. `cn()` - 89 edges
3. `CarrierResultStatus` - 69 edges
4. `QuoteSchema` - 67 edges
5. `User` - 62 edges
6. `PortManager` - 58 edges
7. `HapagLloydConnector` - 56 edges
8. `CMAConnector` - 55 edges
9. `MaerskConnector` - 52 edges
10. `BaseCarrierConnector` - 50 edges

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

## Communities (136 total, 25 thin omitted)

### Community 0 - "port_manager.py"
Cohesion: 0.26
Nodes (11): add_carrier_override(), add_custom_port(), delete_carrier_override(), delete_custom_port(), get_carrier_overrides(), get_custom_ports(), get_popular_ports_config(), update_popular_ports_config() (+3 more)

### Community 1 - "BaseCarrierConnector"
Cohesion: 0.10
Nodes (11): ABC, BaseCarrierConnector, Open the price breakdown / detail view for a specific quote. Args: quote_ref:…, Extract individual charge line items from the price breakdown. Returns: List of…, Normalize extracted data into a QuoteSchema using the normalizer. Args:…, Abstract base class for carrier portal connectors., Detects if a CAPTCHA, Turnstile, hCaptcha, reCAPTCHA, or 2FA screen is…, The card's summary price. NOTE: on multi-container cards this is the SUM across… (+3 more)

### Community 2 - "cn"
Cohesion: 0.07
Nodes (52): Reuse the primitives, New primitives — `frontend/src/components/ui/`, BatchProgressPanel(), BatchProgressPanelProps, cheapest(), Filter, lanePhase(), Phase (+44 more)

### Community 3 - "user_routes.py"
Cohesion: 0.09
Nodes (56): admin_delete_user(), AdminLoginRequest, approve_user(), CarrierOverrideRequest, CarrierSwitchRequest, create_custom_port_endpoint(), CustomPortRequest, delete_carrier_override_endpoint() (+48 more)

### Community 4 - "auth_routes.py"
Cohesion: 0.06
Nodes (73): clear_session_cookie(), get_current_user_optional(), login(), LoginRequest, logout(), AsyncSession, BaseModel, post (+65 more)

### Community 5 - "browser_cleanup.py"
Cohesion: 0.12
Nodes (32): _is_chrome(), _is_playwright_driver(), _kill(), kill_profile_browsers(), _proc_supported(), Cleanup for Chrome browsers and temporary profiles that a failed close leaves…, Kill every automated Chrome and Playwright driver. Only call this when no…, Delete per-search profile copies ("chrome_profile_<carrier>_tmp_<id>") and… (+24 more)

### Community 6 - "app/page.tsx"
Cohesion: 0.15
Nodes (24): 6. Known limitations / candidate follow-ups, HomeContent(), BackendConfigModal(), BackendConfigModalProps, SearchHistoryModal(), RepairReport, SelfHealingAlerts(), SelfHealingAlertsProps (+16 more)

### Community 7 - "api.ts"
Cohesion: 0.07
Nodes (65): AdminDashboard(), UserRecord, LoginContent(), AdminCarriers(), PROFILE_NAMES, when(), AnalyticsRange, AdminPortFixes() (+57 more)

### Community 8 - "PortManager"
Cohesion: 0.11
Nodes (8): PortManager, Where admin-saved port name fixes are kept. Railway rebuilds /app on every…, Retrieve verified carrier port name from persistent cache by UN/LOCODE,…, Cache verified carrier port name and save persistently to…, Clean and normalize user input for port searching., Retrieve port data by full UN/LOCODE (e.g., 'SGSIN')., _user_overrides_path(), test_saved_fixes_live_on_the_persistent_volume()

### Community 9 - "AdminUsers.tsx"
Cohesion: 0.20
Nodes (14): AdminUserRecord, AdminUsers(), AdminUsersProps, ago(), AuditEntry, Avatar(), Filter, initials() (+6 more)

### Community 10 - "CMAConnector"
Cohesion: 0.08
Nodes (18): CMAConnector, Ensures 'Ramp' is explicitly selected under 'Type of location' toggle buttons…, Scans for Route, POL (Port of Loading), or POD (Port of Discharge) dropdown…, Clears the currently selected Destination port tag/card, re-types the locode,…, Dynamically extracts any recommended 5-letter POD LOCODE mentioned in the…, Detects if CMA CGM displayed an advisory banner message: "Looking for AEJEA or…, Handles the 'Customer account' -> 'Role (you are acting as)' dropdown on CMA…, Repeatedly clicks 'More results' if visible to load ALL quotes on the page. (+10 more)

### Community 11 - "cma_connector.py"
Cohesion: 0.09
Nodes (32): CMA CGM Live Connector — Playwright automation. Credentials read from env:…, Normalize CMA CGM data into QuoteSchema. Rule: include BASIC_OCEAN_FREIGHT and…, ChargeSchema, is_weight_surcharge_applicable(), Evaluates whether a weight-tier or overweight surcharge is applicable for the…, calculate_final_freight_value(), classify_and_organize_charges(), format_maersk_date() (+24 more)

### Community 12 - "job_service.py"
Cohesion: 0.15
Nodes (25): close_all_active_connectors(), Force close all active carrier connectors and their Playwright Chrome windows., get_async_session_maker(), Get the session maker for use outside of FastAPI dependency injection., SearchStatus, cancel_all_active_searches(), cleanup_browsers_if_idle(), UUID (+17 more)

### Community 13 - "database.py"
Cohesion: 0.18
Nodes (15): get_sync_url(), run_migrations_offline(), run_migrations_online(), _create_sqlite_engine(), _get_database_url(), _get_engine(), _get_session_maker(), init_db() (+7 more)

### Community 14 - "RateSearchRequest"
Cohesion: 0.07
Nodes (34): clean_vessel_name(), OOCLConnector, _parse_date(), parse_oocl_date(), OOCL Live Connector â€” Playwright automation for Sailing Schedules., Parses one FreightSmart result card's inner text into a raw row dict. Text-…, Opens the Details dialog for a card, clicks the Charge Breakdown tab, extracts…, Collects result cards from the FreightSmart quote results page. (+26 more)

### Community 15 - "HapagLloydAPIConnector"
Cohesion: 0.13
Nodes (6): HapagLloydAPIConnector, Direct REST API connector for Hapag-Lloyd Prices API v2.1.4., API connectors do not require browser login sessions., No browser session to reset between batch routes., Resolves a free-text port name or string (e.g. 'Singapore', 'Hamburg, Germany…, Hapag-Lloyd Prices API requires earliestDepartureDate to be at least 4 calendar…

### Community 16 - "preferences.ts"
Cohesion: 0.09
Nodes (34): LaunchIntro(), RfqInputSection(), SearchHistoryItem, derive(), Derived, startOfDay(), UsageStats(), ChoiceCard() (+26 more)

### Community 17 - "test_rfq_agent.py"
Cohesion: 0.10
Nodes (36): API routes for RFQ parsing agent., RFQParseResult, asyncio, Unit tests for the Gemini AI RFQ Agent service (parse_rfq). Includes…, Test Image 2: Air rate request generates 3 drafts to Glenn (AWOT), Jing Hui…, Test Image 4: Steel Plate ex Pasir Gudang / Tanjung Pelepas for 20' & 40'., Test Guardrail: Detects Reefer container request and returns unsupported_cargo…, Test Guardrail: Detects LCL request. (+28 more)

### Community 18 - ".run_full_search"
Cohesion: 0.17
Nodes (3): Normalize various date formats (e.g. 2026-05-31, 31.05.2026, 31 May 2026, 31…, Parses Hapag-Lloyd left search/summary panel for: - PoD (Port of Discharge),…, Normalize raw Hapag-Lloyd quotes into unified QuoteSchema.

### Community 19 - "SocialWidget.tsx"
Cohesion: 0.10
Nodes (34): ACCENT_COLORS, errorMessage(), relativeTime(), resizeImageToDataUrl(), SocialWidget(), SocialWidgetProps, EMOJI_GROUPS, EmojiPicker() (+26 more)

### Community 20 - "lucide-react"
Cohesion: 0.07
Nodes (39): AppHeader(), AppHeaderProps, initials(), systemStatus(), ChatWidget(), ChatWidgetProps, Message, ACTION_STATUSES (+31 more)

### Community 21 - "GreenXConnector"
Cohesion: 0.11
Nodes (9): GreenXConnector, date, Overrides base search runner to query all 3 sizes at once and cache the…, Type a LOCODE into the autocomplete field and click the first visible dropdown…, Find quantity input next to or below label_text and fill it., Find the exact individual quote card container row encompassing dates, rates,…, Dismiss any cookie/alert modal that would intercept pointer events., Splits a single raw multi-container quote card into multiple QuoteSchema… (+1 more)

### Community 22 - "social_routes.py"
Cohesion: 0.10
Nodes (33): get_current_user(), Dependency that strictly requires an authenticated active member., get_conversation(), list_colleagues(), poke_colleague(), PokeRequest, AsyncSession, BaseModel (+25 more)

### Community 23 - "port_routes.py"
Cohesion: 0.29
Nodes (9): get_countries(), get_port(), get_suggestions(), get, Get list of countries for autocomplete dropdown., Get specific port details by UN/LOCODE., Get port suggestions for autocomplete., search() (+1 more)

### Community 24 - "backend/main.py"
Cohesion: 0.07
Nodes (31): api_route, health(), lifespan(), get, websocket, Infreight Ocean Carrier Rate Automation — FastAPI Application. Main entry point…, Check if the VNC viewer is available (production only, where Xvfb runs)., Proxy WebSocket connections to legacy local x11vnc at localhost:5900. (+23 more)

### Community 25 - "rate_search_routes.py"
Cohesion: 0.07
Nodes (52): approve_repair(), ApproveRepairRequest, carrier_switch_status(), chat_endpoint(), ChatRequest, create_batch_rate_search(), _contains(), _looks_like() (+44 more)

### Community 26 - "MSCConnector"
Cohesion: 0.10
Nodes (15): format_to_iso_date(), MSCConnector, parse_msc_modal_charges(), Playwright-based automation for MSC (Mediterranean Shipping Company)., Handles the MSC login flow., Clicks Instant Quote, fills form, clicks Search., Parses charges from MSC BreakdownModal text. Correctly includes charges whose…, Detects and clicks the 'Ramp' delivery/haulage option if MSC displays Ramp /… (+7 more)

### Community 27 - "parse_rfq"
Cohesion: 0.12
Nodes (27): parse_rfq_endpoint(), post, Parse a free-text RFQ email or message into a structured RateSearchRequest…, _call_native_gemini_api(), _detect_booking_confirmation(), _detect_dual_mode_enquiry(), _detect_mode_by_hierarchy(), _detect_unsupported_cargo() (+19 more)

### Community 28 - "types.ts"
Cohesion: 0.10
Nodes (35): 0. The one invariant, CarrierMultiSelect(), CarrierMultiSelectProps, isAllCarriers(), toggleAllCarriers(), toggleCarrierSelection(), PortAutocomplete(), RateSearchForm() (+27 more)

### Community 29 - "AIBrowserAgent"
Cohesion: 0.13
Nodes (15): AIBrowserAgent, Capture the current page as a PNG screenshot., Build the prompt with task description and action history., Parse Gemini's response into an action dict., Call Gemini API with exponential backoff retry., Execute a parsed action on the browser page., Detect if the agent is stuck repeating the same action., Find all visible interactive elements and format them as a prompt guide. (+7 more)

### Community 30 - "CarrierSearchResult"
Cohesion: 0.10
Nodes (33): get_recent_search_status_context(), handle_chat_query(), _local_chatbot_fallback(), Chat Service — manages conversational AI queries from the frontend user using…, Intelligent responder for search status, carrier guidance, air/sea info, and…, Queries the database for the most recent rate search status to give the chatbot…, Sends the chat message and history to native Gemini 2.5 Flash API. If Gemini…, Base (+25 more)

### Community 31 - "ONEConnector"
Cohesion: 0.18
Nodes (3): ONEConnector, date, Splits a single raw multi-container quote card into multiple QuoteSchema…

### Community 32 - "_Page"
Cohesion: 0.06
Nodes (29): _is_logged_in_url(), Wait until the login page either redirects to a signed-in page or shows its…, True once Maersk has moved past the login pages to a signed-in page., Load the saved login an admin uploaded (Admin > Carriers on / off) into this…, Types text character by character into a given locator or element handle with…, clean_storage_state(), delete_session(), load_session() (+21 more)

### Community 33 - "Engineering Report: Sourcing Portal Enhancements & Scraping Pipeline Stability"
Cohesion: 0.08
Nodes (23): 1. Anti-Bot Mitigation & CAPTCHA Human-in-the-Loop Recovery, 2. Sourcing Parallelization & Surcharges Optimization, 3. Autocomplete Intelligence & Location Mapping, 4. Scraper Pipeline Maintenance, 5. Infrastructure & DevSecOps Enhancements, Business Value, Business Value, Business Value (+15 more)

### Community 34 - "Changelog"
Cohesion: 0.17
Nodes (11): [2026-05-18 – 2026-05-19] — Railway Deployment & Docker, [2026-06-01] — Hapag-Lloyd Sold Out Detection & Date Parsing, [2026-07-08] — OOCL E-Quote Calendar Navigation, cheapest E-Spot selection, and E-Quote/E-Spot isolation refinements, [2026-07-09] — Hapag-Lloyd Quick Quotes pairing and selection simplification, Changelog, Hapag-Lloyd — Date String Standardization, Hapag-Lloyd — Quick Quotes Simplification & Clean Pairing, Hapag-Lloyd — Sold Out Schedule Detection (+3 more)

### Community 35 - "AdminOverview.tsx"
Cohesion: 0.11
Nodes (23): AdminAnalytics, AdminOverview(), AdminOverviewProps, AdminOverviewUser, Attention, attentionItems(), CARRIER_LABELS, CarrierStat (+15 more)

### Community 36 - "package.json"
Cohesion: 0.09
Nodes (20): eslintConfig, nextConfig, engines, node, name, packageManager, private, version (+12 more)

### Community 37 - "dependencies"
Cohesion: 0.15
Nodes (13): dependencies, class-variance-authority, clsx, exceljs, lucide-react, next, next-themes, @radix-ui/react-slot (+5 more)

### Community 38 - "RateResults.tsx"
Cohesion: 0.08
Nodes (46): LiveSearchProgressProps, QuoteBreakdownDrawer(), QuoteBreakdownDrawerProps, Breakdown(), ChargeList(), dateValue(), freeTimeText(), isSoldOut() (+38 more)

### Community 39 - "SearchQueueManager"
Cohesion: 0.12
Nodes (11): Lock, Marks a search as completed internally so we can track the auto-release timeout., Called periodically in a background task to check if the user has held the lock…, Forcefully clears all queued searches and the active lock. Useful for…, Returns or creates an asyncio.Lock for a specific carrier code to prevent…, Adds a search to the queue and waits until it becomes the active search. Event-…, Singleton manager to enforce a FIFO queue for rate searches. Since web scraping…, Returns the current position of the search in the queue. 0 means it is the… (+3 more)

### Community 40 - "schemas.py"
Cohesion: 0.11
Nodes (33): ONE (Ocean Network Express) Live Connector — Playwright automation. Credentials…, # TODO: Verify selectors against ONE ecommerce portal, CarrierCode, ChargeCategory, Pydantic schemas for API request/response validation., classify_charge(), Charge Classifier — rule-based classification of freight charge line items.…, Classify a charge line item based on its name, amount, section heading, and… (+25 more)

### Community 41 - "Frontend Redesign — Componentry Design System, Workspace & Launch Intro (2026-09-07)"
Cohesion: 0.14
Nodes (13): 1. Design system foundation (`082b43a`), 2. Bugs found and fixed during the restyle, 3. Workspace + launch intro (`21ade75`), 4. Follow-up fixes (`2f9d92b`), 5. Verification, 7. Conventions to follow from here, Dependencies added (5, all small, no runtime lib dependency on Componentry), Frontend Redesign — Componentry Design System, Workspace & Launch Intro (2026-09-07) (+5 more)

### Community 42 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 43 - "._fs_dismiss_modals"
Cohesion: 0.08
Nodes (21): _dismiss_once(), _click_date_strip_item(), _open_calendar(), Lock, Iterates through the FreightSmart results date calendar to collect E-Quote and…, Full FreightSmart phase: login â†’ fill quote form â†’ search â†’ extract rows., Shadow-DOM-aware check for whether the onboarding tour heading is on screen., Runs CONCURRENTLY with the rest of the FreightSmart form-filling flow and… (+13 more)

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
Cohesion: 0.11
Nodes (15): HapagLloydConnector, Fuzzy match quote ETD with crawled schedules within a window of +/- 2 days., Performs a single modal dismissal check and attempt., inspect(), parse_hapag_pdf(), scrape_hapag_freetime(), check(), test_mapping() (+7 more)

### Community 49 - "CarrierResultStatus"
Cohesion: 0.07
Nodes (26): Base Carrier Connector — abstract base class for all carrier connectors. Each…, Override to immediately return CONNECTOR_NOT_AVAILABLE., Fill in the carrier's search form and submit a quote search. Args: request: The…, Required abstract method implementation; delegates to run_full_search., Batch (RFQ) mode: the base implementation drives a browser page, so answer from…, Hapag-Lloyd Prices API Connector (REST API v2.1.4). Provides real-time rate…, Called by job_service once per container type (request.container_type). All…, Executes full rate search against Hapag-Lloyd Prices API. Queries each… (+18 more)

### Community 50 - "._dismiss_hapag_modals"
Cohesion: 0.26
Nodes (6): Robustly selects options from Hapag-Lloyd custom dropdown lists. Types the…, Guards against the session-expiry-mid-crawl failure mode: the existing redirect…, Crawls Hapag-Lloyd sailing schedules from the Schedule tab., Dismisses any obscuring modal popups (including multi-step tutorial dialogs)., Ensures the browser is actively on the Quick Quote form (SPA)., Checks if Hapag-Lloyd API Gateway has returned 'This service is currently…

### Community 51 - "CurrencyManager"
Cohesion: 0.26
Nodes (6): convert_currency_to_usd(), CurrencyManager, get_all_exchange_rates(), Any, Currency Exchange Rate Service — manages currency conversions and custom…, update_exchange_rate()

### Community 53 - "test_hapag_freetime.py"
Cohesion: 0.20
Nodes (14): _apply_freetime_to_quote(), freetime_days(), match_freetime_entry(), Any, Destination free time from config/hapag_freetime.json, shared by the Hapag-…, Days for this container from a table entry ({"20GP": n, "40GP": n} or a bare…, The table entry whose country name appears in `text` as whole words. Whole…, days() (+6 more)

### Community 54 - "🚢 Infreight Sourcing & Ocean Rate Automation System"
Cohesion: 0.14
Nodes (13): 1. Multi-Carrier Automation Engine, 2. Intelligent Surcharge & Charge Classifier Engine (`charge_classifier.py`), 3. Container Comparison Matrix & Excel Export Engine, 🚢 Infreight Sourcing & Ocean Rate Automation System, 🌟 Key Capabilities, 📄 License & Confidentiality, Prerequisites, 🛠️ Project Structure (+5 more)

### Community 55 - "MaerskConnector"
Cohesion: 0.06
Nodes (28): MaerskConnector, flatten_tree(), Maersk Browser Connector — Playwright automation using your real Google Chrome…, Execute the full search flow with Progressive Lazy Loading: 1. Login 2. Search…, Extracts freetime, demurrage, and detention from the 'Import D&D fees' tab…, Extracts the routing details from the 'Route & other details' accordion.…, Splits a single raw multi-container quote card into multiple QuoteSchema…, # NOTE: Bright Data Web Unlocker proxies break Playwright browser sessions… (+20 more)

### Community 56 - "[2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split"
Cohesion: 0.15
Nodes (13): G2 Stress Test: "Hi, Please book the below as per your quote ref INF-2026-0842:…, H1 Stress Test: Table with 2 distinct rows: Row 1: POL Singapore, POD Jakarta,…, test_g2_booking_confirmation_guardrail(), test_h1_table_deduplication_two_pairs(), [2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split, Booking Confirmation / Instructions Intercept Guardrail G2 (`rfq_agent.py` & `RfqInputSection.tsx`), Commercial Sales Desk Intelligence (`sales_notes`), Deterministic Port Alias Resolver (`ports_aliases.json`) (+5 more)

### Community 57 - "._parse_offer_response_to_quotes"
Cohesion: 0.17
Nodes (6): Any, Constructs OpenAPI compliant OfferRequest payload., Maps a Prices API rate onto the categories the portal scraper produces (freight…, Leg locations are UnLocation/Facility objects per the spec; tolerate plain…, Renders a graduated weight tier (e.g. Heavy Lift: 18-99 TON) in the portal's…, Parses Hapag-Lloyd OfferResponse JSON into InFreight QuoteSchema objects.

### Community 58 - "🛠 Detailed Carrier Log"
Cohesion: 0.15
Nodes (12): 🛠 Detailed Carrier Log, 🟢 GreenX, 🟠 Hapag-Lloyd, Infreight Ocean Carrier Rate Automation — Development Log, 🚀 Key Highlights & Architectural Changes, 🔌 Local Laptop Deployment (Self-Hosted Worker), 🔵 Maersk, 💗 ONE (Ocean Network Express) (+4 more)

### Community 59 - "silk-aurora.tsx"
Cohesion: 0.19
Nodes (9): hexToRgb01(), sanitizeHexColor(), SilkAurora(), SilkAuroraProps, WebGLErrorBoundary, WebGLErrorBoundaryProps, WebGLErrorBoundaryState, WebGLFallback() (+1 more)

### Community 60 - "json"
Cohesion: 0.15
Nodes (11): Repair Report — generates and saves diagnosis reports on Playwright selector…, check_and_wait_for_captcha(), login(), main(), Hapag-Lloyd end-to-end test using run_full_search., test_hapag(), main(), Verification script for ONE multi-container implementation. (+3 more)

### Community 62 - "[2026-06-30] — ONE Multi-Container & Sold-Out, GreenX Surcharge Intake, Free-Time Fixes, Maersk Diagnosis"
Cohesion: 0.25
Nodes (8): [2026-06-30] — ONE Multi-Container & Sold-Out, GreenX Surcharge Intake, Free-Time Fixes, Maersk Diagnosis, Free Time — GreenX blank, ONE India wrong, Hapag Nhava Sheva unresolved (Singapore → Nhava Sheva), GreenX — Only Basic Ocean Freight & LSS Folded Into Final Value, MAERSK — "Quotes Found" but Empty Excel (Diagnosis), ONE — All-Container-Type Search Returning 0 Quotes, ONE — Multi-Container Breakdown Triple-Counted / Inflated Final Value, ONE — Sold-Out ("Notify Me") Sailings Appearing as Quotes, Performance/Reliability — Stop Copying Chrome Caches During Profile Clone/Sync

### Community 63 - "[2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup"
Cohesion: 0.22
Nodes (8): [2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup, Chromium Cache Auto-Cleanup (Railway Storage Bloat Prevention), CMA CGM — 30-Second Timeout on Sold Out Cards, CMA CGM — Free Time Regex Too Strict, CMA CGM — Routing Regex Not Matching "via LEKKI, LA, NG", Excel Export — Routing & Free Time Columns Always Empty, Excel Export — Sold Out Rows Not Showing, Maersk — Hardcoded Port Overrides

### Community 64 - "compute_admin_analytics"
Cohesion: 0.25
Nodes (8): compute_admin_analytics(), get_clean_lane_key(), normalize_lane_port(), Any, AsyncSession, Normalize port string to cleanly aggregate naming variations., Returns (norm_origin, norm_dest, display_lane_key)., Compute full consolidated analytics payload for the admin dashboard.

### Community 65 - "export_maersk_login.py"
Cohesion: 0.16
Nodes (10): Interactive Headed Login Helper for Maersk. Opens real Chrome using the…, Interactive Headed Login Helper for ONE (Ocean Network Express). Opens Chrome…, _logged_in(), main(), _on_login_page(), Save a Maersk login from your own PC for the server to use. Opens real Google…, Storage Cleanup Utility — automatically removes stale debug screenshots, HTML…, glob (+2 more)

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
Cohesion: 0.07
Nodes (46): _local_fuzzy_repair(), AI Repair Agent — diagnoses Playwright step failures and suggests selector…, A local rule-based heuristic to locate reasonable buttons or inputs when Gemini…, Analyzes the failure context and DOM content to suggest a selector repair. Uses…, suggest_fix(), capture_failure_context(), Exception, Failure Detector — parses and structures error context from failed Playwright… (+38 more)

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
Cohesion: 0.13
Nodes (9): extract_locode_and_country(), prepare_maersk_query(), Fills an autocomplete field using the proven original element-level…, Extracts LOCODE and country name from text like 'CASABLANCA, MOROCCO (MACAS)'…, Maps standard container search codes (e.g. 'DRY 20', '20GP') to Maersk Spot…, Scores a Maersk autocomplete dropdown suggestion. NOTE: The nested/indented…, Tries to click a matching option from ONE's visible dropdown. Returns True only…, get_cached_carrier_port() (+1 more)

### Community 74 - ".build_quick_quotes"
Cohesion: 0.31
Nodes (3): Quick-mode quote builder shared by every connector and both search paths. Fixes…, Execute the full search flow: 1. Login 2. Search quotes 3. Extract quote list…, One route of a persistent batch on the already-open session (no login/close).

### Community 75 - "Summary of Changes — July 20, 2026"
Cohesion: 0.29
Nodes (6): 1. AI RFQ Front Door & Air Freight Support (Phase A), 2. Multi-Origin & Gappy List Parsing for Sea RFQs (Phase B), 3. Search Form Streamlining (Form Input Restrictions), 4. Native Gemini 2.5 Flash API & Chatbot Resiliency, 5. Verification & Test Suite, Summary of Changes — July 20, 2026

### Community 76 - "test_port_logging_and_mismatch.py"
Cohesion: 0.16
Nodes (16): get_route_health(), Get carrier search reliability & route health matrix across origin-destination…, _detect_port_mismatch(), Detects port mismatch for origin or destination. Returns: - True if verified…, asyncio, Unit tests for Port Search Reliability Logging and Mismatch Detection., Test that /api/admin/route-health endpoint returns formatted route health…, Test that matching LOCODE or City + Country code returns False (Verified Match). (+8 more)

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
Cohesion: 0.17
Nodes (11): ambiguous_python_import_b35980c0aa01, argparse, asyncio, Integration tests for authentication, legacy user password setup, pending…, test_full_auth_lifecycle(), httpx, pytest_asyncio, handle_request() (+3 more)

### Community 83 - "layout.tsx"
Cohesion: 0.25
Nodes (6): frontend_src_app_globals, instrumentSans, inter, metadata, viewport, ThemeProvider()

### Community 84 - "[2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning"
Cohesion: 0.13
Nodes (12): Detects the Microsoft B2C identity/OAuth login page. Hapag can silently bounce…, get_booking_start_date(), date, Applies the business rules and pairs FreightSmart prices with crawled…, [2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning, GreenX — "No Quotes" Reported While Quotes Visibly Loaded in VNC, Hapag-Lloyd — Configurable Pacing & Redundant-Wait Removal, Hapag-Lloyd — Crawl Stalls by Typing a Port Locode Into the Login Email Field (+4 more)

### Community 85 - ".select_cheapest_per_window"
Cohesion: 0.25
Nodes (4): Best-effort ETD date from a raw card dict (ISO, MM/DD/YYYY)., Picks the cheapest card in EACH tariff window the customer RFQ sheet needs:…, Backward-compatible: the single cheapest card (1ST window, else 2ND)., Quick Search (multi-port RFQ) — Per-Container Pricing Was Wrong

### Community 86 - ".run_batch_persistent_search"
Cohesion: 0.29
Nodes (4): Any, Clean up browser resources robustly, ensuring failures or hangs never block…, Returns the open session to a clean search page for the next route. With…, Executes a vertical batch search over multiple route requests using a SINGLE…

### Community 88 - "os"
Cohesion: 0.05
Nodes (40): asyncio, Page Observer — captures page state (screenshot, DOM, visible text) on failure., GreenX (Evergreen) Live Connector - Playwright automation., # NOTE: No start date fill needed — schedule page defaults to today,, Hapag-Lloyd Live Connector -- Playwright automation. Credentials read from env:…, dump_options(), main(), Diagnostic: dump ALL dropdown options (text + innerHTML) when typing 'DEHAM'… (+32 more)

### Community 89 - "get_connector"
Cohesion: 0.25
Nodes (7): get_connector(), Get the appropriate connector for a carrier. If USE_MOCK_CARRIERS=true: returns…, main(), test_locode_resolution(), test_payload_generation(), test_registry_integration(), test_response_parsing_and_normalization()

### Community 90 - "search_port"
Cohesion: 0.12
Nodes (17): Resolves input text (e.g. 'Belfast (GBBEL)' or 'GBBEL') to a tuple of…, resolve_msc_port(), fill_container_card(), Resolves input text to (location_name, locode, country_code, country_name)., resolve_oocl_port_info(), get_carrier_search_query(), get_port_by_code(), Suggest top N ports for a partial query. (+9 more)

### Community 92 - "._mouse_glide_to"
Cohesion: 0.24
Nodes (5): Clicks an element with pre-click and post-click human-like reaction pauses., Visible page size, read from the page., Move the real mouse pointer to (x, y) along a slightly curved, uneven path.…, Scroll with the wheel if needed, glide to the element, hover, then press and…, Small aimless pointer drift, as a person does while a page loads.

### Community 93 - "[2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History"
Cohesion: 0.40
Nodes (5): [2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History, Admin User Search History & SGT GMT+8 Conversion (`AdminDashboard.tsx`), GreenX (Evergreen) Card Isolation & Surcharge Parsing (`greenx_connector.py`), Multi-Route Batch Execution Engine (`batch_engine.py`), OOCL FreightSmart 28-Day Calendar Expansion (`oocl_connector.py`)

### Community 94 - "._split_or_none"
Cohesion: 0.25
Nodes (7): Calls the connector's per-container splitter whether it is sync or async…, 1. What was measured, 2. Why the scrapers break when a site changes, 3. Multi-port quick search — defects found and fixed, 4. Ranked recommendations, 5. Verification of this change, Scraper Robustness Review — July 2026

### Community 95 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, dev, lint, start

### Community 96 - "frontend/README.md"
Cohesion: 0.50
Nodes (3): Deploy on Vercel, Getting Started, Learn More

### Community 97 - "pytest"
Cohesion: 0.17
Nodes (8): parse_hapag_card_text_mock(), Verify that multi-leg/feeder routes take the final arrival ETA and 28 days TT., Mock implementation of the JS evaluate logic inside hapag_lloyd_connector.py., test_hapag_multi_leg_schedule_extraction(), Tests for rate search API endpoints., Placeholder test — integration tests require DB setup., test_placeholder(), pytest

### Community 98 - "[2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control"
Cohesion: 0.40
Nodes (5): [2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control, Concurrency Limit Queue & Admin Control Panel, MSC — Mediterranean Shipping Company Connector Implementation, ONE — Inbound Free Time Swap & Scraper Upgrade, OOCL — Orient Overseas Container Line Connector Implementation

### Community 100 - "NotAvailableConnector"
Cohesion: 0.33
Nodes (4): NotAvailableConnector, Placeholder connector for carriers not yet implemented., CMACGMConnector, CMA CGM Connector — not yet implemented. Returns CONNECTOR_NOT_AVAILABLE.

### Community 101 - "._wait_for_captcha_resolution"
Cohesion: 0.33
Nodes (4): Best-effort automated CAPTCHA/Turnstile clearing, tried BEFORE escalating to a…, Locate the Cloudflare Turnstile / challenge widget and click its checkbox using…, Helper that pauses execution if a CAPTCHA challenge is detected, and waits up…, Hapag-Lloyd — Best-Effort Automated CAPTCHA Clear + Per-Sailing Speedup

### Community 102 - "[2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash"
Cohesion: 0.40
Nodes (5): [2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash, AI RFQ Front Door & Air Freight Support, Multi-Origin & Gappy List Parsing (Sea RFQs), Native Gemini 2.5 Flash Direct API Integration, Search Form Streamlining

### Community 106 - "[2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes"
Cohesion: 0.50
Nodes (4): [2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes, CMA CGM — Chrome Profile Bypass, ONE — Date Formatting & Charge Breakdown Pollution, ONE — Date Picker Pre-selection Issue

### Community 116 - "test_hapag_schedule_debug.py"
Cohesion: 0.67
Nodes (3): Debug script: Reuse HapagLloydConnector login, then step through the Schedule…, run(), ss()

### Community 117 - "[2026-05-23 – 2026-05-24] — Maersk Shadow DOM & Stealth Upgrades"
Cohesion: 0.50
Nodes (4): [2026-05-23 – 2026-05-24] — Maersk Shadow DOM & Stealth Upgrades, Maersk — 2FA/CAPTCHA Human-in-the-Loop via noVNC, Maersk — Login Credential Autofill Corruption, Maersk — Shadow DOM Piercing for MDS Web Components

### Community 119 - "User"
Cohesion: 0.09
Nodes (30): get_me(), get, Dependency that strictly requires an active admin user., Get profile of currently signed-in user., require_admin(), Config, fetch_carrier_overrides(), fetch_port_fixes() (+22 more)

### Community 120 - "Architecture Overview"
Cohesion: 0.50
Nodes (4): Architecture Overview, Carrier Connector Lifecycle, Charge Classification Rules, Search Flow

### Community 121 - "[2026-05-20 – 2026-05-22] — Port Resolution & Frontend Improvements"
Cohesion: 0.50
Nodes (4): [2026-05-20 – 2026-05-22] — Port Resolution & Frontend Improvements, Excel Export — ETA Column & Container Type Header, Frontend Light Mode & CORS Fix, Port Resolution System

### Community 122 - "[2026-05-31] — Multi-Instance Support & Charge Classification"
Cohesion: 0.67
Nodes (3): [2026-05-31] — Multi-Instance Support & Charge Classification, Charge Classification Improvements, Multi-Instance Concurrent Searches

### Community 123 - "[2026-06-03] — CMA CGM Routing & Free Time Extraction"
Cohesion: 0.50
Nodes (4): [2026-06-03] — CMA CGM Routing & Free Time Extraction, CMA CGM — Import Free Time from D&D Tab, CMA CGM — Routing Detection (Direct vs Transit), Maersk — Free Time Extraction from Card Text

### Community 124 - "[2026-06-02] — Hapag-Lloyd Transshipment & Duplicate Fix"
Cohesion: 0.67
Nodes (3): [2026-06-02] — Hapag-Lloyd Transshipment & Duplicate Fix, Hapag-Lloyd — Duplicate Sailings from Transshipment Vessels, Hapag-Lloyd — Routing Not Marked as Transit

### Community 125 - "HapagServiceUnavailableException"
Cohesion: 0.67
Nodes (3): HapagServiceUnavailableException, Exception, Exception raised when Hapag-Lloyd API Gateway reports service is unavailable.

### Community 126 - "._parse_free_time_text"
Cohesion: 0.43
Nodes (5): Parses ONE QUOTE Free Time popover text for DESTINATION ONLY. Ignores Origin…, test_one_free_time_parser_origin_only_ignored(), test_one_free_time_parser_test_a(), test_one_free_time_parser_test_b(), test_one_free_time_parser_test_c()

### Community 129 - "[2026-08-04 - 2026-08-06] — CMA CGM Dynamic RAMP/POD Rerouting, Brand Excel Styling, Port Synonym Matching & Tunnel Relays"
Cohesion: 0.40
Nodes (5): [2026-08-04 - 2026-08-06] — CMA CGM Dynamic RAMP/POD Rerouting, Brand Excel Styling, Port Synonym Matching & Tunnel Relays, Brand-Aligned Excel Export Styling (`excel_export.py`), CMA CGM Dynamic RAMP / POD Advisory Banner Detection (`cma_connector.py`), Dynamic Carrier Port Overrides & Admin Registry (`PortManager`, `AdminDashboard.tsx`), Railway WebSocket Tunnel Relay & Failover (`tunnel_client.py`, `run_tunnel_client.bat`, `FailoverFetch`)

### Community 133 - "[2026-05-25 – 2026-05-26] — VNC Display Isolation & Proxy Integration"
Cohesion: 0.67
Nodes (3): [2026-05-25 – 2026-05-26] — VNC Display Isolation & Proxy Integration, Bright Data ISP Proxy Integration, VNC Display Isolation for Concurrent Carriers

### Community 135 - "[2026-07-03] — Robustness Review & Multi-Port Quick Search Fixes"
Cohesion: 0.67
Nodes (3): [2026-07-03] — Robustness Review & Multi-Port Quick Search Fixes, Batch (168-route) Execution — Isolation, Lock Scope, Polling, Robustness Review (see `docs/ROBUSTNESS_REVIEW_2026-07.md`)

## Knowledge Gaps
- **313 isolated node(s):** `Config`, `install_pi.sh script`, `eslintConfig`, `nextConfig`, `name` (+308 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 945 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **25 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Changelog` connect `Changelog` to `[2026-08-04 - 2026-08-06] — CMA CGM Dynamic RAMP/POD Rerouting, Brand Excel Styling, Port Synonym Matching & Tunnel Relays`, `[2026-05-25 – 2026-05-26] — VNC Display Isolation & Proxy Integration`, `[2026-07-03] — Robustness Review & Multi-Port Quick Search Fixes`, `._fs_dismiss_modals`, `[2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split`, `[2026-06-30] — ONE Multi-Container & Sold-Out, GreenX Surcharge Intake, Free-Time Fixes, Maersk Diagnosis`, `[2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup`, `._verify_price_owner_selected`, `[2026-05-29 – 2026-05-30] — Hapag-Lloyd Full Integration`, `[2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning`, `[2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History`, `[2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control`, `[2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash`, `[2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes`, `[2026-05-23 – 2026-05-24] — Maersk Shadow DOM & Stealth Upgrades`, `Architecture Overview`, `[2026-05-20 – 2026-05-22] — Port Resolution & Frontend Improvements`, `[2026-05-31] — Multi-Instance Support & Charge Classification`, `[2026-06-03] — CMA CGM Routing & Free Time Extraction`, `[2026-06-02] — Hapag-Lloyd Transshipment & Duplicate Fix`?**
  _High betweenness centrality (0.331) - this node is a cross-community bridge._
- **Why does `[2026-06-03] — CMA CGM Routing & Free Time Extraction` connect `[2026-06-03] — CMA CGM Routing & Free Time Extraction` to `Changelog`?**
  _High betweenness centrality (0.302) - this node is a cross-community bridge._
- **Why does `Maersk — Free Time Extraction from Card Text` connect `[2026-06-03] — CMA CGM Routing & Free Time Extraction` to `RateResults.tsx`?**
  _High betweenness centrality (0.301) - this node is a cross-community bridge._
- **Are the 32 inferred relationships involving `RateSearchRequest` (e.g. with `create_batch_rate_search()` and `create_rate_search()`) actually correct?**
  _`RateSearchRequest` has 32 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `cn()` (e.g. with `Reuse the primitives` and `7. Conventions to follow from here`) actually correct?**
  _`cn()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 21 inferred relationships involving `CarrierResultStatus` (e.g. with `safe_step()` and `update_carrier_status()`) actually correct?**
  _`CarrierResultStatus` has 21 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Config`, `install_pi.sh script`, `eslintConfig` to the rest of the system?**
  _313 weakly-connected nodes found - possible documentation gaps or missing edges._