# Graph Report - Infreight_SourcingRates_SG  (2026-10-09)

## Corpus Check
- 250 files · ~1,165,265 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 24 file(s) not represented in the graph (top: (none) 10, .bat 7, .conf 2)

## Summary
- 2409 nodes · 5955 edges · 141 communities (117 shown, 24 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 337 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `49158494`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- auth_service.py
- BaseCarrierConnector
- cn
- user_routes.py
- auth_routes.py
- browser_cleanup.py
- app/page.tsx
- api.ts
- PortManager
- MaerskConnector
- CMAConnector
- test_normalizer.py
- reject_selector
- orbit-card-stack.tsx
- OOCLConnector
- HapagLloydAPIConnector
- preferences.ts
- test_rfq_agent.py
- time
- SocialWidget.tsx
- LiveSearchProgress.tsx
- GreenXConnector
- social_routes.py
- ._fs_extract_rows
- backend/main.py
- QuoteSchema
- MSCConnector
- parse_rfq
- types.ts
- AIBrowserAgent
- CarrierResultStatus
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
- HangingConnector
- devDependencies
- dithered-logo.tsx
- 👥 The 5 Agent Roles
- HapagLloydConnector
- MockCarrierConnector
- post
- carrier_sessions.py
- MockCard
- websockify_carrier_proxy
- 🚢 Infreight Sourcing & Ocean Rate Automation System
- .run_full_search
- [2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split
- handle_chat_query
- 🛠 Detailed Carrier Log
- silk-aurora.tsx
- scrape_one_freetime.py
- .extract_charge_breakdown
- [2026-06-30] — ONE Multi-Container & Sold-Out, GreenX Surcharge Intake, Free-Time Fixes, Maersk Diagnosis
- [2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup
- compute_admin_analytics
- export_maersk_login.py
- GreenX — Surcharge Intake Fix (2026-06-30)
- Admin Page & Port Prioritization Guide
- [2026-07-03] — OOCL FreightSmart Autoclear, Hapag Price Leak & Redirect fixes, Maersk Cache Scoping, Dallas Overrides
- test_self_healing.py
- sort_container_types
- carrier_switches.py
- deploy
- .search_quotes
- .run_full_search
- Summary of Changes — July 20, 2026
- create_batch_rate_search
- [2026-05-29 – 2026-05-30] — Hapag-Lloyd Full Integration
- resolve_port_alias
- test_brightdata.py
- MockCard
- Design system — read before touching any UI
- test_auth_routes.py
- layout.tsx
- [2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning
- ._fs_iterate_calendar_dates
- .extract_quote_list
- RateLimiter
- RateSearchRequest
- .search_quotes
- maersk_connector.py
- ref_fs
- ._mouse_glide_to
- [2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History
- Scraper Robustness Review — July 2026
- scripts
- frontend/README.md
- pytest
- [2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control
- .validate_currency
- maersk_proxy_settings
- capture_failure_context
- [2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash
- ._fs_pair_and_select
- Working in this repository
- [2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes
- install_pi.sh
- models/__init__.py
- postcss.config.mjs
- _dismiss_once
- [2026-05-23 – 2026-05-24] — Maersk Shadow DOM & Stealth Upgrades
- ai_agent.py
- User
- Architecture Overview
- [2026-05-20 – 2026-05-22] — Port Resolution & Frontend Improvements
- test_el_dekheila_maersk.py
- [2026-08-07] — Carrier Specific Free Time, Demurrage/Detention Splitting, MSC CDD Surcharges, OOCL Nearby Route Filtering & Favicon Cache Busting
- [2026-06-02] — Hapag-Lloyd Transshipment & Duplicate Fix
- ai_repair_agent.py
- ._parse_free_time_text
- main
- repair_report.py
- diagnose_greenx_dropdown.py
- test_hapag_surcharge_section_parser.py
- test_premium_cargo_service_override
- replace_master_profile
- fill_container_card
- alembic
- .get_carrier_lock
- test_oocl_normalize_result_with_pcs
- clean_selector_memory
- [2026-05-18 – 2026-05-19] — Railway Deployment & Docker
- [2026-06-01] — Hapag-Lloyd Sold Out Detection & Date Parsing
- handle_request

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

## Communities (141 total, 24 thin omitted)

### Community 0 - "auth_service.py"
Cohesion: 0.13
Nodes (19): AuditLog, AuthSession, Stores hashed active session tokens., Stores security and operational audit trail entries., get_client_ip(), get_user_for_token(), hash_token(), AsyncSession (+11 more)

### Community 1 - "BaseCarrierConnector"
Cohesion: 0.05
Nodes (29): ABC, BaseCarrierConnector, NotAvailableConnector, Any, Open the price breakdown / detail view for a specific quote. Args: quote_ref:…, Extract individual charge line items from the price breakdown. Returns: List of…, Normalize extracted data into a QuoteSchema using the normalizer. Args:…, Abstract base class for carrier portal connectors. (+21 more)

### Community 2 - "cn"
Cohesion: 0.06
Nodes (54): AdminUserRecord, AdminUsers(), AdminUsersProps, ago(), AuditEntry, Avatar(), Filter, initials() (+46 more)

### Community 3 - "user_routes.py"
Cohesion: 0.08
Nodes (65): admin_delete_user(), AdminLoginRequest, approve_user(), CarrierOverrideRequest, CarrierSwitchRequest, Config, create_custom_port_endpoint(), CustomPortRequest (+57 more)

### Community 4 - "auth_routes.py"
Cohesion: 0.07
Nodes (56): clear_session_cookie(), get_current_user_optional(), login(), LoginRequest, logout(), AsyncSession, BaseModel, post (+48 more)

### Community 5 - "browser_cleanup.py"
Cohesion: 0.13
Nodes (30): _is_chrome(), _is_playwright_driver(), _kill(), kill_profile_browsers(), _proc_supported(), Cleanup for Chrome browsers and temporary profiles that a failed close leaves…, Kill every automated Chrome and Playwright driver. Only call this when no…, Delete per-search profile copies ("chrome_profile_<carrier>_tmp_<id>") and… (+22 more)

### Community 6 - "app/page.tsx"
Cohesion: 0.12
Nodes (30): Reuse the primitives, 6. Known limitations / candidate follow-ups, New primitives — `frontend/src/components/ui/`, BackendConfigModal(), BackendConfigModalProps, LoginModalProps, SearchCompletionModal(), SearchCompletionModalProps (+22 more)

### Community 7 - "api.ts"
Cohesion: 0.07
Nodes (72): AdminDashboard(), UserRecord, LoginContent(), HomeContent(), AdminCarriers(), PROFILE_NAMES, when(), AdminPortFixes() (+64 more)

### Community 8 - "PortManager"
Cohesion: 0.06
Nodes (26): prepare_maersk_query(), add_carrier_override(), delete_carrier_override(), get_cached_carrier_port(), get_carrier_overrides(), get_popular_ports_config(), normalize_port_input(), PortManager (+18 more)

### Community 9 - "MaerskConnector"
Cohesion: 0.14
Nodes (8): MaerskConnector, Clicks an element with pre-click and post-click human-like reaction pauses., Wait until the login page either redirects to a signed-in page or shows its…, Load the saved login an admin uploaded (Admin > Carriers on / off) into this…, Extracts the port/city name by removing any UN/LOCODE parentheses (e.g.,…, Types text character by character into a given locator or element handle with…, main(), main()

### Community 10 - "CMAConnector"
Cohesion: 0.07
Nodes (19): CMAConnector, Ensures 'Ramp' is explicitly selected under 'Type of location' toggle buttons…, Scans for Route, POL (Port of Loading), or POD (Port of Discharge) dropdown…, Clears the currently selected Destination port tag/card, re-types the locode,…, Dynamically extracts any recommended 5-letter POD LOCODE mentioned in the…, Detects if CMA CGM displayed an advisory banner message: "Looking for AEJEA or…, Handles the 'Customer account' -> 'Role (you are acting as)' dropdown on CMA…, Repeatedly clicks 'More results' if visible to load ALL quotes on the page. (+11 more)

### Community 11 - "test_normalizer.py"
Cohesion: 0.21
Nodes (9): calculate_final_freight_value(), Calculate the final freight value from a list of classified charges. Args:…, Tests for normalizer / final freight value calculator., test_basic_calculation(), test_classify_and_organize(), test_no_charges(), test_one_breakdown_parsing(), test_only_excluded() (+1 more)

### Community 12 - "reject_selector"
Cohesion: 0.16
Nodes (15): get_approved_selector(), _load_memory(), Loads memory JSON file. Returns empty dict if file is missing or invalid., Saves memory dict back to JSON file., Looks up if there is an approved replacement selector for the given carrier and…, Stores an approved replacement selector., Marks any proposed selector for this step as REJECTED., reject_selector() (+7 more)

### Community 13 - "orbit-card-stack.tsx"
Cohesion: 0.22
Nodes (13): HalftoneAvatar(), HalftoneAvatarProps, hashSeed(), pick(), clamp(), initialsFor(), laneLabel(), OrbitCardStack() (+5 more)

### Community 14 - "OOCLConnector"
Cohesion: 0.22
Nodes (8): OOCLConnector, Attempts to automatically click the Cloudflare Turnstile 'Verify you are human'…, asyncio, test_oocl_cwx_different_port_pair_different_amount(), test_oocl_cwx_heavy_weight_charge_not_applied_40gp(), test_oocl_cwx_heavy_weight_charge_not_applied_under_threshold(), test_oocl_cwx_port_pair_surabaya_karachi(), test_oocl_cwx_port_pair_without_cwx()

### Community 15 - "HapagLloydAPIConnector"
Cohesion: 0.05
Nodes (36): HapagLloydAPIConnector, Any, AsyncClient, Direct REST API connector for Hapag-Lloyd Prices API v2.1.4., API connectors do not require browser login sessions., No browser session to reset between batch routes., Resolves a free-text port name or string (e.g. 'Singapore', 'Hamburg, Germany…, Hapag-Lloyd Prices API requires earliestDepartureDate to be at least 4 calendar… (+28 more)

### Community 16 - "preferences.ts"
Cohesion: 0.10
Nodes (31): LaunchIntro(), derive(), startOfDay(), UsageStats(), ChoiceCard(), Toggle(), WorkspacePanel(), WorkspacePanelProps (+23 more)

### Community 17 - "test_rfq_agent.py"
Cohesion: 0.10
Nodes (36): API routes for RFQ parsing agent., RFQParseResult, asyncio, Unit tests for the Gemini AI RFQ Agent service (parse_rfq). Includes…, Test Image 2: Air rate request generates 3 drafts to Glenn (AWOT), Jing Hui…, Test Image 4: Steel Plate ex Pasir Gudang / Tanjung Pelepas for 20' & 40'., Test Guardrail: Detects Reefer container request and returns unsupported_cargo…, Test Guardrail: Detects LCL request. (+28 more)

### Community 18 - "time"
Cohesion: 0.19
Nodes (9): cleanup_old_debug_files(), Storage Cleanup Utility — automatically removes stale debug screenshots, HTML…, Deletes temporary debug screenshots (*.png), HTML dumps (*.html), and temporary…, Verify that cleanup_old_debug_files removes debug pngs/htmls older than N days…, test_storage_cleanup_deletes_old_files(), glob, subprocess, tempfile (+1 more)

### Community 19 - "SocialWidget.tsx"
Cohesion: 0.16
Nodes (21): ACCENT_COLORS, errorMessage(), relativeTime(), resizeImageToDataUrl(), SocialWidget(), SocialWidgetProps, EMOJI_GROUPS, EmojiPicker() (+13 more)

### Community 20 - "LiveSearchProgress.tsx"
Cohesion: 0.08
Nodes (31): ChatWidget(), ChatWidgetProps, Message, ACTION_STATUSES, ChipModel, describe(), EMPTY_STATUSES, formatElapsed() (+23 more)

### Community 21 - "GreenXConnector"
Cohesion: 0.21
Nodes (4): GreenXConnector, Overrides base search runner to query all 3 sizes at once and cache the…, Splits a single raw multi-container quote card into multiple QuoteSchema…, inspect()

### Community 22 - "social_routes.py"
Cohesion: 0.11
Nodes (31): get_current_user(), Dependency that strictly requires an authenticated active member., get_conversation(), list_colleagues(), poke_colleague(), PokeRequest, AsyncSession, BaseModel (+23 more)

### Community 23 - "._fs_extract_rows"
Cohesion: 0.18
Nodes (7): clean_vessel_name(), _parse_date(), parse_oocl_date(), Parses one FreightSmart result card's inner text into a raw row dict. Text-…, Opens the Details dialog for a card, clicks the Charge Breakdown tab, extracts…, Collects result cards from the FreightSmart quote results page., OOCL Nearby Route Recommendations Suppression (`oocl_connector.py`)

### Community 24 - "backend/main.py"
Cohesion: 0.11
Nodes (22): api_route, health(), lifespan(), get, Infreight Ocean Carrier Rate Automation — FastAPI Application. Main entry point…, Check if the VNC viewer is available (production only, where Xvfb runs)., Startup and shutdown events., vnc_status() (+14 more)

### Community 25 - "QuoteSchema"
Cohesion: 0.06
Nodes (52): carrier_switch_status(), create_rate_search(), get_admin_analytics_endpoint(), get_batch_search_status(), get_rate_search(), get_route_health(), get_user_search_history(), AsyncSession (+44 more)

### Community 26 - "MSCConnector"
Cohesion: 0.10
Nodes (15): format_to_iso_date(), MSCConnector, parse_msc_modal_charges(), Playwright-based automation for MSC (Mediterranean Shipping Company)., Handles the MSC login flow., Clicks Instant Quote, fills form, clicks Search., Parses charges from MSC BreakdownModal text. Correctly includes charges whose…, Detects and clicks the 'Ramp' delivery/haulage option if MSC displays Ramp /… (+7 more)

### Community 27 - "parse_rfq"
Cohesion: 0.12
Nodes (27): parse_rfq_endpoint(), post, Parse a free-text RFQ email or message into a structured RateSearchRequest…, _call_native_gemini_api(), _detect_booking_confirmation(), _detect_dual_mode_enquiry(), _detect_mode_by_hierarchy(), _detect_unsupported_cargo() (+19 more)

### Community 28 - "types.ts"
Cohesion: 0.09
Nodes (41): 0. The one invariant, CarrierMultiSelect(), CarrierMultiSelectProps, isAllCarriers(), toggleAllCarriers(), toggleCarrierSelection(), PortAutocomplete(), PortAutocompleteProps (+33 more)

### Community 29 - "AIBrowserAgent"
Cohesion: 0.12
Nodes (16): AIBrowserAgent, Capture the current page as a PNG screenshot., Build the prompt with task description and action history., Parse Gemini's response into an action dict., Call Gemini API with exponential backoff retry., Execute a parsed action on the browser page., Detect if the agent is stuck repeating the same action., Find all visible interactive elements and format them as a prompt guide. (+8 more)

### Community 30 - "CarrierResultStatus"
Cohesion: 0.05
Nodes (99): get_recent_search_status_context(), Chat Service — manages conversational AI queries from the frontend user using…, Queries the database for the most recent rate search status to give the chatbot…, Safe Step — Playwright action execution wrapper with manual intervention pause…, Updates the status of a carrier search in the database., update_carrier_status(), get_sync_url(), run_migrations_offline() (+91 more)

### Community 31 - "ONEConnector"
Cohesion: 0.14
Nodes (5): ONEConnector, date, Splits a single raw multi-container quote card into multiple QuoteSchema…, Tries to click a matching option from ONE's visible dropdown. Returns True only…, Extracts 5-letter UN/LOCODE from strings like 'Singapore [SGSIN]' or 'Singapore…

### Community 32 - "_Page"
Cohesion: 0.11
Nodes (13): capture_page_state(), Captures screenshot, DOM HTML, and inner text of the current page. Saves…, _is_logged_in_url(), True once Maersk has moved past the login pages to a signed-in page., _connector(), _Locator, _Page, Maersk's login page redirects to the Hub a few seconds after loading when the… (+5 more)

### Community 33 - "Engineering Report: Sourcing Portal Enhancements & Scraping Pipeline Stability"
Cohesion: 0.08
Nodes (23): 1. Anti-Bot Mitigation & CAPTCHA Human-in-the-Loop Recovery, 2. Sourcing Parallelization & Surcharges Optimization, 3. Autocomplete Intelligence & Location Mapping, 4. Scraper Pipeline Maintenance, 5. Infrastructure & DevSecOps Enhancements, Business Value, Business Value, Business Value (+15 more)

### Community 34 - "Changelog"
Cohesion: 0.11
Nodes (17): [2026-05-25 – 2026-05-26] — VNC Display Isolation & Proxy Integration, [2026-05-31] — Multi-Instance Support & Charge Classification, [2026-06-03] — CMA CGM Routing & Free Time Extraction, [2026-07-03] — Robustness Review & Multi-Port Quick Search Fixes, [2026-07-08] — OOCL E-Quote Calendar Navigation, cheapest E-Spot selection, and E-Quote/E-Spot isolation refinements, [2026-07-09] — Hapag-Lloyd Quick Quotes pairing and selection simplification, Bright Data ISP Proxy Integration, Changelog (+9 more)

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
Cohesion: 0.08
Nodes (49): BatchProgressPanelProps, LiveSearchProgressProps, QuoteBreakdownDrawer(), QuoteBreakdownDrawerProps, Breakdown(), ChargeList(), dateValue(), freeTimeText() (+41 more)

### Community 39 - "SearchQueueManager"
Cohesion: 0.14
Nodes (9): Marks a search as completed internally so we can track the auto-release timeout., Called periodically in a background task to check if the user has held the lock…, Forcefully clears all queued searches and the active lock. Useful for…, Adds a search to the queue and waits until it becomes the active search. Event-…, Singleton manager to enforce a FIFO queue for rate searches. Since web scraping…, Returns the current position of the search in the queue. 0 means it is the…, Releases the lock so the next user can proceed. Returns True if a lock was…, SearchQueueManager (+1 more)

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

### Community 44 - "HangingConnector"
Cohesion: 0.20
Nodes (4): CrashingConnector, HangingConnector, Hangs on the sizes in `hang_on`; answers NO_QUOTES_AVAILABLE for the rest., Like a real connector whose tab dies: reports a crash, then never returns.

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
Cohesion: 0.08
Nodes (16): _generate_maersk_mock_quotes(), _generate_msc_mock_quotes(), _generate_one_mock_quotes(), MockCarrierConnector, any, Mock Carrier Connector — returns realistic sample data for testing. Used when…, Generate realistic ONE sample quotes with charge breakdowns., Generate realistic MSC sample quotes with validity_till. (+8 more)

### Community 50 - "post"
Cohesion: 0.20
Nodes (10): approve_repair(), ApproveRepairRequest, force_stop_searches(), BaseModel, post, Release the queue lock for a completed or queued search., Approves a suggested AI selector fix and saves it to memory., Forcefully clears the queue and cancels all active search tasks. (+2 more)

### Community 51 - "carrier_sessions.py"
Cohesion: 0.11
Nodes (22): clean_storage_state(), delete_session(), load_session(), _on_domain(), _path(), Saved carrier logins uploaded by an admin. An admin logs in to a carrier in…, What the admin screen shows: who uploaded it, when, and how much it holds., Keep only this carrier's cookies and localStorage, in the shape add_cookies… (+14 more)

### Community 53 - "websockify_carrier_proxy"
Cohesion: 0.22
Nodes (5): websocket, Proxy WebSocket connections to legacy local x11vnc at localhost:5900., Proxy WebSocket connections to specific carrier x11vnc servers., websockify_carrier_proxy(), websockify_proxy()

### Community 54 - "🚢 Infreight Sourcing & Ocean Rate Automation System"
Cohesion: 0.14
Nodes (13): 1. Multi-Carrier Automation Engine, 2. Intelligent Surcharge & Charge Classifier Engine (`charge_classifier.py`), 3. Container Comparison Matrix & Excel Export Engine, 🚢 Infreight Sourcing & Ocean Rate Automation System, 🌟 Key Capabilities, 📄 License & Confidentiality, Prerequisites, 🛠️ Project Structure (+5 more)

### Community 55 - ".run_full_search"
Cohesion: 0.15
Nodes (5): flatten_tree(), Execute the full search flow with Progressive Lazy Loading: 1. Login 2. Search…, Extracts freetime, demurrage, and detention from the 'Import D&D fees' tab…, Extracts the routing details from the 'Route & other details' accordion.…, Splits a single raw multi-container quote card into multiple QuoteSchema…

### Community 56 - "[2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split"
Cohesion: 0.15
Nodes (13): G2 Stress Test: "Hi, Please book the below as per your quote ref INF-2026-0842:…, H1 Stress Test: Table with 2 distinct rows: Row 1: POL Singapore, POD Jakarta,…, test_g2_booking_confirmation_guardrail(), test_h1_table_deduplication_two_pairs(), [2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split, Booking Confirmation / Instructions Intercept Guardrail G2 (`rfq_agent.py` & `RfqInputSection.tsx`), Commercial Sales Desk Intelligence (`sales_notes`), Deterministic Port Alias Resolver (`ports_aliases.json`) (+5 more)

### Community 57 - "handle_chat_query"
Cohesion: 0.25
Nodes (8): handle_chat_query(), _local_chatbot_fallback(), Intelligent responder for search status, carrier guidance, air/sea info, and…, Sends the chat message and history to native Gemini 2.5 Flash API. If Gemini…, chat_endpoint(), ChatRequest, Chatbot helper endpoint powered by Gemini API., test_chat_service_offline_fallback()

### Community 58 - "🛠 Detailed Carrier Log"
Cohesion: 0.15
Nodes (12): 🛠 Detailed Carrier Log, 🟢 GreenX, 🟠 Hapag-Lloyd, Infreight Ocean Carrier Rate Automation — Development Log, 🚀 Key Highlights & Architectural Changes, 🔌 Local Laptop Deployment (Self-Hosted Worker), 🔵 Maersk, 💗 ONE (Ocean Network Express) (+4 more)

### Community 59 - "silk-aurora.tsx"
Cohesion: 0.19
Nodes (9): hexToRgb01(), sanitizeHexColor(), SilkAurora(), SilkAuroraProps, WebGLErrorBoundary, WebGLErrorBoundaryProps, WebGLErrorBoundaryState, WebGLFallback() (+1 more)

### Community 60 - "scrape_one_freetime.py"
Cohesion: 1.00
Nodes (3): check_and_wait_for_captcha(), login(), main()

### Community 62 - "[2026-06-30] — ONE Multi-Container & Sold-Out, GreenX Surcharge Intake, Free-Time Fixes, Maersk Diagnosis"
Cohesion: 0.29
Nodes (7): [2026-06-30] — ONE Multi-Container & Sold-Out, GreenX Surcharge Intake, Free-Time Fixes, Maersk Diagnosis, GreenX — Only Basic Ocean Freight & LSS Folded Into Final Value, MAERSK — "Quotes Found" but Empty Excel (Diagnosis), ONE — All-Container-Type Search Returning 0 Quotes, ONE — Multi-Container Breakdown Triple-Counted / Inflated Final Value, ONE — Sold-Out ("Notify Me") Sailings Appearing as Quotes, Performance/Reliability — Stop Copying Chrome Caches During Profile Clone/Sync

### Community 63 - "[2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup"
Cohesion: 0.22
Nodes (8): [2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup, Chromium Cache Auto-Cleanup (Railway Storage Bloat Prevention), CMA CGM — 30-Second Timeout on Sold Out Cards, CMA CGM — Free Time Regex Too Strict, CMA CGM — Routing Regex Not Matching "via LEKKI, LA, NG", Excel Export — Routing & Free Time Columns Always Empty, Excel Export — Sold Out Rows Not Showing, Maersk — Hardcoded Port Overrides

### Community 64 - "compute_admin_analytics"
Cohesion: 0.25
Nodes (8): compute_admin_analytics(), get_clean_lane_key(), normalize_lane_port(), Any, AsyncSession, Normalize port string to cleanly aggregate naming variations., Returns (norm_origin, norm_dest, display_lane_key)., Compute full consolidated analytics payload for the admin dashboard.

### Community 65 - "export_maersk_login.py"
Cohesion: 0.70
Nodes (4): _logged_in(), main(), _on_login_page(), Save a Maersk login from your own PC for the server to use. Opens real Google…

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
Cohesion: 0.20
Nodes (15): _local_fuzzy_repair(), A local rule-based heuristic to locate reasonable buttons or inputs when Gemini…, Analyzes the failure context and DOM content to suggest a selector repair. Uses…, suggest_fix(), detect_manual_action_required(), Scans the current Playwright page to see if a CAPTCHA, Cloudflare challenge,…, Executes a Playwright action. If it fails: 1. Detects CAPTCHA/bot challenges…, safe_step() (+7 more)

### Community 70 - "sort_container_types"
Cohesion: 0.40
Nodes (4): Sort container types in standard order: DRY 20 (20GP) -> DRY 40 (40GP) -> DRY…, sort_container_types(), test_container_types_standard_ordering(), model_validator

### Community 71 - "carrier_switches.py"
Cohesion: 0.35
Nodes (10): get_switches(), off_message(), _path(), Admin on/off switch per carrier, for when a carrier's site is down or under…, Every switchable carrier: {"enabled", "reason", "updated_by", "updated_at"}; on…, The message for a switched-off carrier's result, or None when it is on., _read(), set_switch() (+2 more)

### Community 72 - "deploy"
Cohesion: 0.25
Nodes (7): build, builder, deploy, restartPolicyMaxRetries, restartPolicyType, startCommand, $schema

### Community 73 - ".search_quotes"
Cohesion: 0.14
Nodes (8): extract_locode_and_country(), Fills an autocomplete field using the proven original element-level…, Verifies the "I am the price owner" radio is genuinely checked, piercing shadow…, Extracts LOCODE and country name from text like 'CASABLANCA, MOROCCO (MACAS)'…, Maps standard container search codes (e.g. 'DRY 20', '20GP') to Maersk Spot…, Scores a Maersk autocomplete dropdown suggestion. NOTE: The nested/indented…, Maersk — 0.0-USD / "Not Open" Card Flakiness (the "Quotes Found but Empty Excel" root causes), Maersk — Caching Scope & Selector Tuning

### Community 74 - ".run_full_search"
Cohesion: 0.25
Nodes (3): Serves one container-type cycle from the cached merged quote set: -…, One crawl serves all container-type cycles (cached), combining: 1. Sailing…, Public oocl.com Chromium sailing schedule crawl bypassed per directive. All…

### Community 75 - "Summary of Changes — July 20, 2026"
Cohesion: 0.29
Nodes (6): 1. AI RFQ Front Door & Air Freight Support (Phase A), 2. Multi-Origin & Gappy List Parsing for Sea RFQs (Phase B), 3. Search Form Streamlining (Form Input Restrictions), 4. Native Gemini 2.5 Flash API & Chatbot Resiliency, 5. Verification & Test Suite, Summary of Changes — July 20, 2026

### Community 76 - "create_batch_rate_search"
Cohesion: 0.48
Nodes (7): create_batch_rate_search(), _contains(), _looks_like(), _norm(), _resolve(), Execute a multi-route RFQ batch using Vertical Parallel Persistent Sessions.…, BackgroundTasks

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

### Community 82 - "test_auth_routes.py"
Cohesion: 0.33
Nodes (5): ambiguous_python_import_b35980c0aa01, asyncio, Integration tests for authentication, legacy user password setup, pending…, test_full_auth_lifecycle(), pytest_asyncio

### Community 83 - "layout.tsx"
Cohesion: 0.25
Nodes (6): frontend_src_app_globals, instrumentSans, inter, metadata, viewport, ThemeProvider()

### Community 84 - "[2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning"
Cohesion: 0.25
Nodes (6): [2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning, GreenX — "No Quotes" Reported While Quotes Visibly Loaded in VNC, Hapag-Lloyd — Configurable Pacing & Redundant-Wait Removal, Job Scheduler — Concurrency Default, Maersk — Regression: Other-Container-Type Sizes Went "Sold Out" in Multi-Container Searches, OOCL — Schedule Search Repeated Once Per Container Type

### Community 85 - "._fs_iterate_calendar_dates"
Cohesion: 0.33
Nodes (4): _click_date_strip_item(), _open_calendar(), Iterates through the FreightSmart results date calendar to collect E-Quote and…, setter

### Community 88 - "RateSearchRequest"
Cohesion: 0.04
Nodes (80): argparse, asyncio, Page Observer — captures page state (screenshot, DOM, visible text) on failure., Selector Memory — stores and retrieves human-approved selector patches., GreenX (Evergreen) Live Connector - Playwright automation., # NOTE: No start date fill needed — schedule page defaults to today,, Hapag-Lloyd Live Connector -- Playwright automation. Credentials read from env:…, Interactive Headed Login Helper for Maersk. Opens real Chrome using the… (+72 more)

### Community 89 - ".search_quotes"
Cohesion: 0.29
Nodes (3): date, Type a LOCODE into the autocomplete field and click the first visible dropdown…, Find quantity input next to or below label_text and fill it.

### Community 90 - "maersk_connector.py"
Cohesion: 0.07
Nodes (36): Manual Action Detector — identifies pages requiring human verification (2FA,…, get_countries(), get_port(), get_suggestions(), get, Get list of countries for autocomplete dropdown., Get specific port details by UN/LOCODE., Get port suggestions for autocomplete. (+28 more)

### Community 92 - "._mouse_glide_to"
Cohesion: 0.32
Nodes (4): Small aimless pointer drift, as a person does while a page loads., Visible page size, read from the page., Move the real mouse pointer to (x, y) along a slightly curved, uneven path.…, Scroll with the wheel if needed, glide to the element, hover, then press and…

### Community 93 - "[2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History"
Cohesion: 0.40
Nodes (5): [2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History, Admin User Search History & SGT GMT+8 Conversion (`AdminDashboard.tsx`), GreenX (Evergreen) Card Isolation & Surcharge Parsing (`greenx_connector.py`), Multi-Route Batch Execution Engine (`batch_engine.py`), OOCL FreightSmart 28-Day Calendar Expansion (`oocl_connector.py`)

### Community 94 - "Scraper Robustness Review — July 2026"
Cohesion: 0.40
Nodes (4): 1. What was measured, 3. Multi-port quick search — defects found and fixed, 5. Verification of this change, Scraper Robustness Review — July 2026

### Community 95 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, dev, lint, start

### Community 96 - "frontend/README.md"
Cohesion: 0.50
Nodes (3): Deploy on Vercel, Getting Started, Learn More

### Community 97 - "pytest"
Cohesion: 0.13
Nodes (10): parse_hapag_card_text_mock(), Verify that multi-leg/feeder routes take the final arrival ETA and 28 days TT., Mock implementation of the JS evaluate logic inside hapag_lloyd_connector.py., test_hapag_multi_leg_schedule_extraction(), asyncio, test_one_breakdown_currency_and_arbitrary_destination_classification(), Tests for rate search API endpoints., Placeholder test — integration tests require DB setup. (+2 more)

### Community 98 - "[2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control"
Cohesion: 0.40
Nodes (5): [2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control, Concurrency Limit Queue & Admin Control Panel, MSC — Mediterranean Shipping Company Connector Implementation, ONE — Inbound Free Time Swap & Scraper Upgrade, OOCL — Orient Overseas Container Line Connector Implementation

### Community 100 - "maersk_proxy_settings"
Cohesion: 0.57
Nodes (6): maersk_proxy_settings(), Proxy for the Maersk browser, from environment variables, or None. Any…, _clear(), test_any_provider_uses_server_and_login_as_given(), test_bright_data_defaults_unchanged(), test_no_proxy_without_credentials()

### Community 101 - "capture_failure_context"
Cohesion: 0.33
Nodes (5): capture_failure_context(), Exception, Failure Detector — parses and structures error context from failed Playwright…, Assembles a standardized diagnostic dictionary containing all available details…, test_failure_detector()

### Community 102 - "[2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash"
Cohesion: 0.40
Nodes (5): [2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash, AI RFQ Front Door & Air Freight Support, Multi-Origin & Gappy List Parsing (Sea RFQs), Native Gemini 2.5 Flash Direct API Integration, Search Form Streamlining

### Community 103 - "._fs_pair_and_select"
Cohesion: 0.33
Nodes (4): get_booking_start_date(), date, Applies the business rules and pairs FreightSmart prices with crawled…, OOCL — FreightSmart Price Quotes (E-Quote / E-Spot) Paired With Sailing Schedules

### Community 106 - "[2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes"
Cohesion: 0.50
Nodes (4): [2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes, CMA CGM — Chrome Profile Bypass, ONE — Date Formatting & Charge Breakdown Pollution, ONE — Date Picker Pre-selection Issue

### Community 116 - "_dismiss_once"
Cohesion: 0.40
Nodes (3): _dismiss_once(), Shadow-DOM-aware check for whether the onboarding tour heading is on screen., Position-based fallback for the onboarding tour popup: instead of guessing its…

### Community 117 - "[2026-05-23 – 2026-05-24] — Maersk Shadow DOM & Stealth Upgrades"
Cohesion: 0.50
Nodes (4): [2026-05-23 – 2026-05-24] — Maersk Shadow DOM & Stealth Upgrades, Maersk — 2FA/CAPTCHA Human-in-the-Loop via noVNC, Maersk — Login Credential Autofill Corruption, Maersk — Shadow DOM Piercing for MDS Web Components

### Community 118 - "ai_agent.py"
Cohesion: 0.40
Nodes (4): AI Browser Agent — Vision-based browser automation using Gemini Flash. This…, base64, google, google_genai

### Community 119 - "User"
Cohesion: 0.10
Nodes (26): get_me(), get, Dependency that strictly requires an active admin user., Get profile of currently signed-in user., require_admin(), fetch_carrier_overrides(), fetch_port_fixes(), get_admin_custom_ports() (+18 more)

### Community 120 - "Architecture Overview"
Cohesion: 0.50
Nodes (4): Architecture Overview, Carrier Connector Lifecycle, Charge Classification Rules, Search Flow

### Community 121 - "[2026-05-20 – 2026-05-22] — Port Resolution & Frontend Improvements"
Cohesion: 0.50
Nodes (4): [2026-05-20 – 2026-05-22] — Port Resolution & Frontend Improvements, Excel Export — ETA Column & Container Type Header, Frontend Light Mode & CORS Fix, Port Resolution System

### Community 122 - "test_el_dekheila_maersk.py"
Cohesion: 0.40
Nodes (4): Verify non-Maersk carriers get standard UN/LOCODE or default mappings., Verify that El Dekheila maps specifically to 'Alexandria Dekheila, Egypt' for…, test_el_dekheila_maersk_override(), test_el_dekheila_other_carriers_unaffected()

### Community 123 - "[2026-08-07] — Carrier Specific Free Time, Demurrage/Detention Splitting, MSC CDD Surcharges, OOCL Nearby Route Filtering & Favicon Cache Busting"
Cohesion: 0.40
Nodes (5): [2026-08-07] — Carrier Specific Free Time, Demurrage/Detention Splitting, MSC CDD Surcharges, OOCL Nearby Route Filtering & Favicon Cache Busting, Demurrage & Detention Split Fields Across System (`schema.py`, `msc_connector.py`, `maersk_connector.py`, `one_connector.py`, `greenx_connector.py`, `cma_connector.py`, `oocl_connector.py`, `ResultsTable.tsx`, `excel_export.py`), Favicon Cache Busting & Brand Icon (`layout.tsx`, `icon.png`, `favicon.ico`), Hapag-Lloyd MHD (Merchant Haulage Detention) PDF Tariff Scraper (`hapag_freetime_scraper.py`, `hapag_freetime.json`), MSC Cargo Data Declaration [CDD] & Working Days Free Time (`msc_connector.py`)

### Community 124 - "[2026-06-02] — Hapag-Lloyd Transshipment & Duplicate Fix"
Cohesion: 0.67
Nodes (3): [2026-06-02] — Hapag-Lloyd Transshipment & Duplicate Fix, Hapag-Lloyd — Duplicate Sailings from Transshipment Vessels, Hapag-Lloyd — Routing Not Marked as Transit

### Community 125 - "ai_repair_agent.py"
Cohesion: 0.50
Nodes (3): AI Repair Agent — diagnoses Playwright step failures and suggests selector…, bs4, httpx

### Community 126 - "._parse_free_time_text"
Cohesion: 0.43
Nodes (5): Parses ONE QUOTE Free Time popover text for DESTINATION ONLY. Ignores Origin…, test_one_free_time_parser_origin_only_ignored(), test_one_free_time_parser_test_a(), test_one_free_time_parser_test_b(), test_one_free_time_parser_test_c()

### Community 128 - "repair_report.py"
Cohesion: 0.50
Nodes (3): generate_report(), Repair Report — generates and saves diagnosis reports on Playwright selector…, Assembles a comprehensive repair report and writes it as JSON and Markdown…

### Community 129 - "diagnose_greenx_dropdown.py"
Cohesion: 0.67
Nodes (3): dump_options(), main(), Diagnostic: dump ALL dropdown options (text + innerHTML) when typing 'DEHAM'…

### Community 130 - "test_hapag_surcharge_section_parser.py"
Cohesion: 0.67
Nodes (3): parse_hapag_section(), Unit test to verify Hapag-Lloyd Price Breakdown section classification logic.…, test_hapag_section_parsing_order()

### Community 136 - "test_oocl_normalize_result_with_pcs"
Cohesion: 0.67
Nodes (3): asyncio, Verify OOCL normalize_result incorporates Panama Canal Surcharge (PCS)., test_oocl_normalize_result_with_pcs()

### Community 137 - "clean_selector_memory"
Cohesion: 0.67
Nodes (3): clean_selector_memory(), fixture, Wipes the selector memory JSON file before and after each test.

### Community 138 - "[2026-05-18 – 2026-05-19] — Railway Deployment & Docker"
Cohesion: 0.67
Nodes (3): [2026-05-18 – 2026-05-19] — Railway Deployment & Docker, Persistent Chrome Profiles on Railway Volume, Railway Deployment Setup

### Community 139 - "[2026-06-01] — Hapag-Lloyd Sold Out Detection & Date Parsing"
Cohesion: 0.67
Nodes (3): [2026-06-01] — Hapag-Lloyd Sold Out Detection & Date Parsing, Hapag-Lloyd — Date String Standardization, Hapag-Lloyd — Sold Out Schedule Detection

### Community 140 - "handle_request"
Cohesion: 0.67
Nodes (3): handle_request(), AsyncClient, run_client()

## Knowledge Gaps
- **313 isolated node(s):** `Config`, `install_pi.sh script`, `eslintConfig`, `nextConfig`, `name` (+308 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 946 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **24 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Changelog` connect `Changelog` to `[2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control`, `[2026-07-03] — OOCL FreightSmart Autoclear, Hapag Price Leak & Redirect fixes, Maersk Cache Scoping, Dallas Overrides`, `[2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash`, `PortManager`, `[2026-05-18 – 2026-05-19] — Railway Deployment & Docker`, `[2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes`, `[2026-06-01] — Hapag-Lloyd Sold Out Detection & Date Parsing`, `[2026-05-29 – 2026-05-30] — Hapag-Lloyd Full Integration`, `Architecture Overview`, `[2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning`, `[2026-05-23 – 2026-05-24] — Maersk Shadow DOM & Stealth Upgrades`, `[2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split`, `[2026-05-20 – 2026-05-22] — Port Resolution & Frontend Improvements`, `[2026-08-07] — Carrier Specific Free Time, Demurrage/Detention Splitting, MSC CDD Surcharges, OOCL Nearby Route Filtering & Favicon Cache Busting`, `[2026-06-02] — Hapag-Lloyd Transshipment & Duplicate Fix`, `[2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History`, `[2026-06-30] — ONE Multi-Container & Sold-Out, GreenX Surcharge Intake, Free-Time Fixes, Maersk Diagnosis`, `[2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup`?**
  _High betweenness centrality (0.356) - this node is a cross-community bridge._
- **Why does `Maersk — Free Time Extraction from Card Text` connect `Changelog` to `RateResults.tsx`?**
  _High betweenness centrality (0.303) - this node is a cross-community bridge._
- **Are the 32 inferred relationships involving `RateSearchRequest` (e.g. with `create_batch_rate_search()` and `create_rate_search()`) actually correct?**
  _`RateSearchRequest` has 32 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `cn()` (e.g. with `Reuse the primitives` and `7. Conventions to follow from here`) actually correct?**
  _`cn()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 21 inferred relationships involving `CarrierResultStatus` (e.g. with `safe_step()` and `update_carrier_status()`) actually correct?**
  _`CarrierResultStatus` has 21 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Config`, `install_pi.sh script`, `eslintConfig` to the rest of the system?**
  _313 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `auth_service.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12857142857142856 - nodes in this community are weakly interconnected._