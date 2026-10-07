# Graph Report - Infreight_SourcingRates_SG  (2026-10-07)

## Corpus Check
- 233 files · ~1,151,977 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 21 file(s) not represented in the graph (top: (none) 8, .bat 6, .conf 2)

## Summary
- 2241 nodes · 5444 edges · 128 communities (102 shown, 26 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 314 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `4bff2f91`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- os
- CarrierResultStatus
- cn
- user_routes.py
- auth_routes.py
- browser_cleanup.py
- RateSearchRequest
- api.ts
- PortManager
- test_self_healing.py
- CMAConnector
- sys
- auth_service.py
- ._split_or_none
- ._fs_dismiss_modals
- HapagLloydAPIConnector
- preferences.ts
- test_rfq_agent.py
- react
- SocialWidget.tsx
- types.ts
- GreenXConnector
- social_routes.py
- AdminUsers.tsx
- backend/main.py
- rate_search_routes.py
- MSCConnector
- parse_rfq
- post
- ai_agent.py
- job_service.py
- ONEConnector
- .run_full_search
- Engineering Report: Sourcing Portal Enhancements & Scraping Pipeline Stability
- Changelog
- AdminOverview.tsx
- package.json
- LiveSearchProgress.tsx
- RateResults.tsx
- SearchQueueManager
- ChargeCategory
- Frontend Redesign — Componentry Design System, Workspace & Launch Intro (2026-09-07)
- compilerOptions
- safe_step.py
- HangingConnector
- tunnel_client.py
- dithered-logo.tsx
- 👥 The 5 Agent Roles
- HapagLloydConnector
- RFQParseResult
- .run_full_search
- CurrencyManager
- test_persistence_check.py
- dependencies
- 🚢 Infreight Sourcing & Ocean Rate Automation System
- selector_memory.py
- [2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split
- .normalize_result
- 🛠 Detailed Carrier Log
- [2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning
- .search_quotes
- test_normalizer.py
- ._wait_for_captcha_resolution
- [2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup
- [2026-06-30] — ONE Multi-Container & Sold-Out, GreenX Surcharge Intake, Free-Time Fixes, Maersk Diagnosis
- layout.tsx
- GreenX — Surcharge Intake Fix (2026-06-30)
- Admin Page & Port Prioritization Guide
- ._verify_price_owner_selected
- port_routes.py
- .select_cheapest_per_window
- parse_msc_modal_charges
- deploy
- websockify_carrier_proxy
- tunnel_relay/main.py
- Summary of Changes — July 20, 2026
- compute_admin_analytics
- create_batch_rate_search
- resolve_port_alias
- test_brightdata.py
- devDependencies
- Design system — read before touching any UI
- test_panama_canal_surcharge.py
- [2026-05-29 – 2026-05-30] — Hapag-Lloyd Full Integration
- [2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control
- [2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash
- .search_port
- RateLimiter
- .validate_currency
- [2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History
- hapag_freetime_scraper.py
- get_port_by_code
- scripts
- [2026-06-03] — CMA CGM Routing & Free Time Extraction
- [2026-08-04 - 2026-08-06] — CMA CGM Dynamic RAMP/POD Rerouting, Brand Excel Styling, Port Synonym Matching & Tunnel Relays
- MockCard
- frontend/README.md
- pytest
- get_me
- diagnose_greenx_dropdown.py
- test_one_premium_override.py
- ._save_carrier_overrides
- .search_sailing_schedules
- [2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes
- Working in this repository
- install_pi.sh
- models/__init__.py
- postcss.config.mjs
- fill_container_card
- verify_admin_access
- clean_selector_memory
- [2026-05-18 – 2026-05-19] — Railway Deployment & Docker
- [2026-05-31] — Multi-Instance Support & Charge Classification
- [2026-06-01] — Hapag-Lloyd Sold Out Detection & Date Parsing
- .get_port_by_code
- .normalize_port_input
- .set_cached_carrier_port
- .suggest_ports

## God Nodes (most connected - your core abstractions)
1. `RateSearchRequest` - 149 edges
2. `cn()` - 77 edges
3. `CarrierResultStatus` - 69 edges
4. `QuoteSchema` - 67 edges
5. `HapagLloydConnector` - 56 edges
6. `User` - 56 edges
7. `PortManager` - 56 edges
8. `CMAConnector` - 55 edges
9. `BaseCarrierConnector` - 49 edges
10. `MaerskConnector` - 47 edges

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

## Communities (128 total, 26 thin omitted)

### Community 0 - "os"
Cohesion: 0.08
Nodes (42): asyncio, Base Carrier Connector — abstract base class for all carrier connectors. Each…, CMA CGM Live Connector — Playwright automation. Credentials read from env:…, Normalize CMA CGM data into QuoteSchema. Rule: include BASIC_OCEAN_FREIGHT and…, GreenX (Evergreen) Live Connector - Playwright automation., Hapag-Lloyd Prices API Connector (REST API v2.1.4). Provides real-time rate…, # NOTE: No start date fill needed — schedule page defaults to today,, Hapag-Lloyd Live Connector -- Playwright automation. Credentials read from env:… (+34 more)

### Community 1 - "CarrierResultStatus"
Cohesion: 0.04
Nodes (43): ABC, BaseCarrierConnector, NotAvailableConnector, Any, Extract individual charge line items from the price breakdown. Returns: List of…, Normalize extracted data into a QuoteSchema using the normalizer. Args:…, Detects if a CAPTCHA, Turnstile, hCaptcha, reCAPTCHA, or 2FA screen is…, Abstract base class for carrier portal connectors. (+35 more)

### Community 2 - "cn"
Cohesion: 0.08
Nodes (45): Reuse the primitives, New primitives — `frontend/src/components/ui/`, BatchProgressPanel(), BatchProgressPanelProps, cheapest(), Filter, lanePhase(), Phase (+37 more)

### Community 3 - "user_routes.py"
Cohesion: 0.08
Nodes (66): get_current_user(), Dependency that strictly requires an authenticated active member., admin_delete_user(), AdminLoginRequest, approve_user(), CarrierOverrideRequest, Config, create_custom_port_endpoint() (+58 more)

### Community 4 - "auth_routes.py"
Cohesion: 0.09
Nodes (44): clear_session_cookie(), get_current_user_optional(), login(), LoginRequest, logout(), AsyncSession, BaseModel, post (+36 more)

### Community 5 - "browser_cleanup.py"
Cohesion: 0.10
Nodes (35): _is_chrome(), _is_playwright_driver(), _kill(), kill_profile_browsers(), _proc_supported(), profile_base_dirs(), Cleanup for Chrome browsers and temporary profiles that a failed close leaves…, Kill every automated Chrome and Playwright driver. Only call this when no… (+27 more)

### Community 6 - "RateSearchRequest"
Cohesion: 0.04
Nodes (43): OOCLConnector, parse_oocl_date(), Serves one container-type cycle from the cached merged quote set: -…, One crawl serves all container-type cycles (cached), combining: 1. Sailing…, Attempts to automatically click the Cloudflare Turnstile 'Verify you are human'…, Public oocl.com Chromium sailing schedule crawl bypassed per directive. All…, RateSearchRequest, CMA CGM end-to-end test — login + search + extract quotes. (+35 more)

### Community 7 - "api.ts"
Cohesion: 0.09
Nodes (56): AdminDashboard(), UserRecord, HomeContent(), BackendConfigModal(), BackendConfigModalProps, LoadingState(), SearchCompletionModal(), addCarrierOverride() (+48 more)

### Community 9 - "test_self_healing.py"
Cohesion: 0.11
Nodes (27): _local_fuzzy_repair(), AI Repair Agent — diagnoses Playwright step failures and suggests selector…, A local rule-based heuristic to locate reasonable buttons or inputs when Gemini…, Analyzes the failure context and DOM content to suggest a selector repair. Uses…, suggest_fix(), handle_chat_query(), _local_chatbot_fallback(), Intelligent responder for search status, carrier guidance, air/sea info, and… (+19 more)

### Community 10 - "CMAConnector"
Cohesion: 0.08
Nodes (18): CMAConnector, Ensures 'Ramp' is explicitly selected under 'Type of location' toggle buttons…, Scans for Route, POL (Port of Loading), or POD (Port of Discharge) dropdown…, Clears the currently selected Destination port tag/card, re-types the locode,…, Dynamically extracts any recommended 5-letter POD LOCODE mentioned in the…, Detects if CMA CGM displayed an advisory banner message: "Looking for AEJEA or…, Handles the 'Customer account' -> 'Role (you are acting as)' dropdown on CMA…, Repeatedly clicks 'More results' if visible to load ALL quotes on the page. (+10 more)

### Community 11 - "sys"
Cohesion: 0.05
Nodes (34): Repair Report — generates and saves diagnosis reports on Playwright selector…, MaerskConnector, Splits a single raw multi-container quote card into multiple QuoteSchema…, Extracts the port/city name by removing any UN/LOCODE parentheses (e.g.,…, Interactive Headed Login Helper for Maersk. Opens real Chrome using the…, Interactive Headed Login Helper for ONE (Ocean Network Express). Opens Chrome…, main(), Inspection script to dump the Maersk autocomplete dropdown structure. (+26 more)

### Community 12 - "auth_service.py"
Cohesion: 0.07
Nodes (39): Base, AuditLog, AuthSession, DirectMessage, Stores hashed active session tokens., Stores security and operational audit trail entries., Stores private direct text messages between colleagues., get_user_for_token() (+31 more)

### Community 13 - "._split_or_none"
Cohesion: 0.25
Nodes (7): Calls the connector's per-container splitter whether it is sync or async…, 1. What was measured, 2. Why the scrapers break when a site changes, 3. Multi-port quick search — defects found and fixed, 4. Ranked recommendations, 5. Verification of this change, Scraper Robustness Review — July 2026

### Community 14 - "._fs_dismiss_modals"
Cohesion: 0.06
Nodes (26): clean_vessel_name(), _dismiss_once(), _click_date_strip_item(), _open_calendar(), _parse_date(), Lock, Parses one FreightSmart result card's inner text into a raw row dict. Text-…, Opens the Details dialog for a card, clicks the Charge Breakdown tab, extracts… (+18 more)

### Community 15 - "HapagLloydAPIConnector"
Cohesion: 0.07
Nodes (20): HapagLloydAPIConnector, Any, AsyncClient, Direct REST API connector for Hapag-Lloyd Prices API v2.1.4., API connectors do not require browser login sessions., No browser session to reset between batch routes., Resolves a free-text port name or string (e.g. 'Singapore', 'Hamburg, Germany…, Hapag-Lloyd Prices API requires earliestDepartureDate to be at least 4 calendar… (+12 more)

### Community 16 - "preferences.ts"
Cohesion: 0.09
Nodes (33): LaunchIntro(), SearchHistoryItem, derive(), Derived, startOfDay(), UsageStats(), ChoiceCard(), Toggle() (+25 more)

### Community 17 - "test_rfq_agent.py"
Cohesion: 0.10
Nodes (28): asyncio, Unit tests for the Gemini AI RFQ Agent service (parse_rfq). Includes…, Test Image 4: Steel Plate ex Pasir Gudang / Tanjung Pelepas for 20' & 40'., Test Guardrail: Detects LCL request., Test OpenFlights 6,072 IATA airport dataset and shorthand alias resolution., Test Pak Shaun email: "Hi team, need rate for 10x20GP from PK to JKT. Urgent…, Test Multimodal Image Input validation and parsing., Test Stress Test Scenario: "Dear Sir, Pls quote 3 x 20'FCL Singapore to… (+20 more)

### Community 18 - "react"
Cohesion: 0.10
Nodes (22): LoginContent(), ChatWidget(), ChatWidgetProps, Message, LoginModal(), LoginModalProps, RepairReport, SelfHealingAlertsProps (+14 more)

### Community 19 - "SocialWidget.tsx"
Cohesion: 0.10
Nodes (34): ACCENT_COLORS, errorMessage(), relativeTime(), resizeImageToDataUrl(), SocialWidget(), SocialWidgetProps, EMOJI_GROUPS, EmojiPicker() (+26 more)

### Community 20 - "types.ts"
Cohesion: 0.09
Nodes (42): 0. The one invariant, CarrierMultiSelect(), CarrierMultiSelectProps, isAllCarriers(), toggleAllCarriers(), toggleCarrierSelection(), PortAutocomplete(), PortAutocompleteProps (+34 more)

### Community 21 - "GreenXConnector"
Cohesion: 0.11
Nodes (9): GreenXConnector, date, Overrides base search runner to query all 3 sizes at once and cache the…, Type a LOCODE into the autocomplete field and click the first visible dropdown…, Find quantity input next to or below label_text and fill it., Find the exact individual quote card container row encompassing dates, rates,…, Dismiss any cookie/alert modal that would intercept pointer events., Splits a single raw multi-container quote card into multiple QuoteSchema… (+1 more)

### Community 22 - "social_routes.py"
Cohesion: 0.11
Nodes (28): get_conversation(), list_colleagues(), poke_colleague(), PokeRequest, AsyncSession, BaseModel, delete, get (+20 more)

### Community 23 - "AdminUsers.tsx"
Cohesion: 0.20
Nodes (14): AdminUserRecord, AdminUsers(), AdminUsersProps, ago(), AuditEntry, Avatar(), Filter, initials() (+6 more)

### Community 24 - "backend/main.py"
Cohesion: 0.10
Nodes (21): health(), lifespan(), get, Infreight Ocean Carrier Rate Automation — FastAPI Application. Main entry point…, Check if the VNC viewer is available (production only, where Xvfb runs)., Startup and shutdown events., vnc_status(), hash_password() (+13 more)

### Community 25 - "rate_search_routes.py"
Cohesion: 0.11
Nodes (29): get_admin_analytics_endpoint(), get_batch_search_status(), get_rate_search(), get_repair_reports(), get_route_health(), get_user_search_history(), AsyncSession, get (+21 more)

### Community 26 - "MSCConnector"
Cohesion: 0.17
Nodes (7): format_to_iso_date(), MSCConnector, Playwright-based automation for MSC (Mediterranean Shipping Company)., Handles the MSC login flow., Clicks Instant Quote, fills form, clicks Search., Detects and clicks the 'Ramp' delivery/haulage option if MSC displays Ramp /…, Parse '14 Jun 2026' to 'YYYY-MM-DD

### Community 27 - "parse_rfq"
Cohesion: 0.14
Nodes (24): _call_native_gemini_api(), _detect_booking_confirmation(), _detect_dual_mode_enquiry(), _detect_mode_by_hierarchy(), _detect_unsupported_cargo(), _extract_20gp_weight_priority(), generate_dual_air_drafts(), _load_airport_aliases_config() (+16 more)

### Community 28 - "post"
Cohesion: 0.15
Nodes (15): approve_repair(), ApproveRepairRequest, chat_endpoint(), ChatRequest, force_stop_searches(), BaseModel, post, Chatbot helper endpoint powered by Gemini API. (+7 more)

### Community 29 - "ai_agent.py"
Cohesion: 0.10
Nodes (20): AIBrowserAgent, AI Browser Agent — Vision-based browser automation using Gemini Flash. This…, Capture the current page as a PNG screenshot., Build the prompt with task description and action history., Parse Gemini's response into an action dict., Call Gemini API with exponential backoff retry., Execute a parsed action on the browser page., Detect if the agent is stuck repeating the same action. (+12 more)

### Community 30 - "job_service.py"
Cohesion: 0.05
Nodes (79): get_recent_search_status_context(), Chat Service — manages conversational AI queries from the frontend user using…, Queries the database for the most recent rate search status to give the chatbot…, Updates the status of a carrier search in the database., update_carrier_status(), get_sync_url(), run_migrations_offline(), run_migrations_online() (+71 more)

### Community 31 - "ONEConnector"
Cohesion: 0.09
Nodes (11): ONEConnector, _classify(), date, Parses ONE QUOTE Free Time popover text for DESTINATION ONLY. Ignores Origin…, Splits a single raw multi-container quote card into multiple QuoteSchema…, Tries to click a matching option from ONE's visible dropdown. Returns True only…, Extracts 5-letter UN/LOCODE from strings like 'Singapore [SGSIN]' or 'Singapore…, test_one_free_time_parser_origin_only_ignored() (+3 more)

### Community 32 - ".run_full_search"
Cohesion: 0.06
Nodes (20): capture_page_state(), Captures screenshot, DOM HTML, and inner text of the current page. Saves…, _is_logged_in_url(), flatten_tree(), Execute the full search flow with Progressive Lazy Loading: 1. Login 2. Search…, Extracts freetime, demurrage, and detention from the 'Import D&D fees' tab…, Extracts the routing details from the 'Route & other details' accordion.…, True once Maersk has moved past the login pages to a signed-in page. (+12 more)

### Community 33 - "Engineering Report: Sourcing Portal Enhancements & Scraping Pipeline Stability"
Cohesion: 0.08
Nodes (23): 1. Anti-Bot Mitigation & CAPTCHA Human-in-the-Loop Recovery, 2. Sourcing Parallelization & Surcharges Optimization, 3. Autocomplete Intelligence & Location Mapping, 4. Scraper Pipeline Maintenance, 5. Infrastructure & DevSecOps Enhancements, Business Value, Business Value, Business Value (+15 more)

### Community 34 - "Changelog"
Cohesion: 0.08
Nodes (23): [2026-05-20 – 2026-05-22] — Port Resolution & Frontend Improvements, [2026-05-23 – 2026-05-24] — Maersk Shadow DOM & Stealth Upgrades, [2026-05-25 – 2026-05-26] — VNC Display Isolation & Proxy Integration, [2026-06-02] — Hapag-Lloyd Transshipment & Duplicate Fix, [2026-07-08] — OOCL E-Quote Calendar Navigation, cheapest E-Spot selection, and E-Quote/E-Spot isolation refinements, [2026-07-09] — Hapag-Lloyd Quick Quotes pairing and selection simplification, Architecture Overview, Bright Data ISP Proxy Integration (+15 more)

### Community 35 - "AdminOverview.tsx"
Cohesion: 0.11
Nodes (23): AdminAnalytics, AdminOverview(), AdminOverviewProps, AdminOverviewUser, AnalyticsRange, Attention, attentionItems(), CarrierStat (+15 more)

### Community 36 - "package.json"
Cohesion: 0.08
Nodes (24): eslintConfig, nextConfig, engines, node, name, packageManager, private, version (+16 more)

### Community 37 - "LiveSearchProgress.tsx"
Cohesion: 0.13
Nodes (19): ACTION_STATUSES, ChipModel, describe(), EMPTY_STATUSES, formatElapsed(), LiveSearchProgress(), parseServerTime(), Phase (+11 more)

### Community 38 - "RateResults.tsx"
Cohesion: 0.10
Nodes (37): LiveSearchProgressProps, QuoteBreakdownDrawer(), QuoteBreakdownDrawerProps, Breakdown(), ChargeList(), dateValue(), freeTimeText(), isSoldOut() (+29 more)

### Community 39 - "SearchQueueManager"
Cohesion: 0.12
Nodes (11): Lock, Marks a search as completed internally so we can track the auto-release timeout., Called periodically in a background task to check if the user has held the lock…, Forcefully clears all queued searches and the active lock. Useful for…, Returns or creates an asyncio.Lock for a specific carrier code to prevent…, Adds a search to the queue and waits until it becomes the active search. Event-…, Singleton manager to enforce a FIFO queue for rate searches. Since web scraping…, Returns the current position of the search in the queue. 0 means it is the… (+3 more)

### Community 40 - "ChargeCategory"
Cohesion: 0.21
Nodes (20): ChargeCategory, classify_charge(), Charge Classifier — rule-based classification of freight charge line items.…, Classify a charge line item based on its name, amount, section heading, and…, Tests for charge classifier., test_basic_ocean_freight(), test_destination_charges(), test_discount() (+12 more)

### Community 41 - "Frontend Redesign — Componentry Design System, Workspace & Launch Intro (2026-09-07)"
Cohesion: 0.12
Nodes (15): 1. Design system foundation (`082b43a`), 2. Bugs found and fixed during the restyle, 3. Workspace + launch intro (`21ade75`), 4. Follow-up fixes (`2f9d92b`), 5. Verification, 6. Known limitations / candidate follow-ups, 7. Conventions to follow from here, Dependencies added (5, all small, no runtime lib dependency on Componentry) (+7 more)

### Community 42 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 43 - "safe_step.py"
Cohesion: 0.12
Nodes (10): Failure Detector — parses and structures error context from failed Playwright…, Manual Action Detector — identifies pages requiring human verification (2FA,…, Page Observer — captures page state (screenshot, DOM, visible text) on failure., Safe Step — Playwright action execution wrapper with manual intervention pause…, check_and_wait_for_captcha(), login(), main(), Script to test Playwright browser launching using your REAL Google Chrome… (+2 more)

### Community 44 - "HangingConnector"
Cohesion: 0.20
Nodes (4): CrashingConnector, HangingConnector, Hangs on the sizes in `hang_on`; answers NO_QUOTES_AVAILABLE for the rest., Like a real connector whose tab dies: reports a crash, then never returns.

### Community 45 - "tunnel_client.py"
Cohesion: 0.17
Nodes (11): ambiguous_python_import_b35980c0aa01, argparse, asyncio, Integration tests for authentication, legacy user password setup, pending…, test_full_auth_lifecycle(), httpx, pytest_asyncio, handle_request() (+3 more)

### Community 46 - "dithered-logo.tsx"
Cohesion: 0.19
Nodes (15): applyMaskInversion(), buildRoundedMask(), DEFAULTS, DitherConfig, DitheredLogo(), DitheredLogoProps, drawParticles(), errorDiffusionDither() (+7 more)

### Community 47 - "👥 The 5 Agent Roles"
Cohesion: 0.13
Nodes (14): 1. Intake Agent (Email Listener), 2. Sourcing Orchestrator (The Coordinator), 3. Sourcing & Scraping Agent (Rates Engine), 4. Finance & Costing Agent (Excel Compiler), 5. Email Draft Agent (Communicator), 📋 Executive Summary, 🛠️ Implementation Stages, Phase 1: Email Integration (Week 1-2) (+6 more)

### Community 48 - "HapagLloydConnector"
Cohesion: 0.13
Nodes (13): HapagLloydConnector, Fuzzy match quote ETD with crawled schedules within a window of +/- 2 days., Performs a single modal dismissal check and attempt., inspect(), check(), test_mapping(), test(), asyncio (+5 more)

### Community 49 - "RFQParseResult"
Cohesion: 0.17
Nodes (12): parse_rfq_endpoint(), post, API routes for RFQ parsing agent., Parse a free-text RFQ email or message into a structured RateSearchRequest…, RFQParseRequest, RFQParseResult, Test Image 2: Air rate request generates 3 drafts to Glenn (AWOT), Jing Hui…, Test Guardrail: Detects Reefer container request and returns unsupported_cargo… (+4 more)

### Community 50 - ".run_full_search"
Cohesion: 0.20
Nodes (4): Normalize various date formats (e.g. 2026-05-31, 31.05.2026, 31 May 2026, 31…, Robustly selects options from Hapag-Lloyd custom dropdown lists. Types the…, Dismisses any obscuring modal popups (including multi-step tutorial dialogs)., Ensures the browser is actively on the Quick Quote form (SPA).

### Community 51 - "CurrencyManager"
Cohesion: 0.23
Nodes (7): convert_currency_to_usd(), CurrencyManager, get_all_exchange_rates(), Any, Currency Exchange Rate Service — manages currency conversions and custom…, update_exchange_rate(), threading

### Community 52 - "test_persistence_check.py"
Cohesion: 0.39
Nodes (7): add_carrier_override(), delete_carrier_override(), get_carrier_overrides(), get_popular_ports_config(), update_popular_ports_config(), test_dynamic_boosting(), test_persistence()

### Community 53 - "dependencies"
Cohesion: 0.15
Nodes (13): dependencies, class-variance-authority, clsx, exceljs, lucide-react, next, next-themes, @radix-ui/react-slot (+5 more)

### Community 54 - "🚢 Infreight Sourcing & Ocean Rate Automation System"
Cohesion: 0.14
Nodes (13): 1. Multi-Carrier Automation Engine, 2. Intelligent Surcharge & Charge Classifier Engine (`charge_classifier.py`), 3. Container Comparison Matrix & Excel Export Engine, 🚢 Infreight Sourcing & Ocean Rate Automation System, 🌟 Key Capabilities, 📄 License & Confidentiality, Prerequisites, 🛠️ Project Structure (+5 more)

### Community 55 - "selector_memory.py"
Cohesion: 0.24
Nodes (12): get_approved_selector(), _load_memory(), Selector Memory — stores and retrieves human-approved selector patches., Loads memory JSON file. Returns empty dict if file is missing or invalid., Saves memory dict back to JSON file., Looks up if there is an approved replacement selector for the given carrier and…, Stores an approved replacement selector., Marks any proposed selector for this step as REJECTED. (+4 more)

### Community 56 - "[2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split"
Cohesion: 0.15
Nodes (13): G2 Stress Test: "Hi, Please book the below as per your quote ref INF-2026-0842:…, H1 Stress Test: Table with 2 distinct rows: Row 1: POL Singapore, POD Jakarta,…, test_g2_booking_confirmation_guardrail(), test_h1_table_deduplication_two_pairs(), [2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split, Booking Confirmation / Instructions Intercept Guardrail G2 (`rfq_agent.py` & `RfqInputSection.tsx`), Commercial Sales Desk Intelligence (`sales_notes`), Deterministic Port Alias Resolver (`ports_aliases.json`) (+5 more)

### Community 58 - "🛠 Detailed Carrier Log"
Cohesion: 0.15
Nodes (12): 🛠 Detailed Carrier Log, 🟢 GreenX, 🟠 Hapag-Lloyd, Infreight Ocean Carrier Rate Automation — Development Log, 🚀 Key Highlights & Architectural Changes, 🔌 Local Laptop Deployment (Self-Hosted Worker), 🔵 Maersk, 💗 ONE (Ocean Network Express) (+4 more)

### Community 59 - "[2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning"
Cohesion: 0.17
Nodes (10): get_booking_start_date(), date, Applies the business rules and pairs FreightSmart prices with crawled…, [2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning, GreenX — "No Quotes" Reported While Quotes Visibly Loaded in VNC, Hapag-Lloyd — Configurable Pacing & Redundant-Wait Removal, Job Scheduler — Concurrency Default, Maersk — Regression: Other-Container-Type Sizes Went "Sold Out" in Multi-Container Searches (+2 more)

### Community 60 - ".search_quotes"
Cohesion: 0.18
Nodes (7): extract_locode_and_country(), prepare_maersk_query(), Extracts LOCODE and country name from text like 'CASABLANCA, MOROCCO (MACAS)'…, Maps standard container search codes (e.g. 'DRY 20', '20GP') to Maersk Spot…, Scores a Maersk autocomplete dropdown suggestion. NOTE: The nested/indented…, Fills an autocomplete field using the proven original element-level…, get_cached_carrier_port()

### Community 61 - "test_normalizer.py"
Cohesion: 0.13
Nodes (17): is_weight_surcharge_applicable(), Evaluates whether a weight-tier or overweight surcharge is applicable for the…, calculate_final_freight_value(), classify_and_organize_charges(), Takes raw charge line items and classifies them. Args: raw_charges: list of…, Calculate the final freight value from a list of classified charges. Args:…, Tests for normalizer / final freight value calculator., test_basic_calculation() (+9 more)

### Community 62 - "._wait_for_captcha_resolution"
Cohesion: 0.33
Nodes (4): Best-effort automated CAPTCHA/Turnstile clearing, tried BEFORE escalating to a…, Locate the Cloudflare Turnstile / challenge widget and click its checkbox using…, Helper that pauses execution if a CAPTCHA challenge is detected, and waits up…, Hapag-Lloyd — Best-Effort Automated CAPTCHA Clear + Per-Sailing Speedup

### Community 63 - "[2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup"
Cohesion: 0.12
Nodes (10): MockCard, MockLocator, [2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup, Chromium Cache Auto-Cleanup (Railway Storage Bloat Prevention), CMA CGM — 30-Second Timeout on Sold Out Cards, CMA CGM — Free Time Regex Too Strict, CMA CGM — Routing Regex Not Matching "via LEKKI, LA, NG", Excel Export — Routing & Free Time Columns Always Empty (+2 more)

### Community 64 - "[2026-06-30] — ONE Multi-Container & Sold-Out, GreenX Surcharge Intake, Free-Time Fixes, Maersk Diagnosis"
Cohesion: 0.22
Nodes (9): _apply_freetime_to_quote(), [2026-06-30] — ONE Multi-Container & Sold-Out, GreenX Surcharge Intake, Free-Time Fixes, Maersk Diagnosis, Free Time — GreenX blank, ONE India wrong, Hapag Nhava Sheva unresolved (Singapore → Nhava Sheva), GreenX — Only Basic Ocean Freight & LSS Folded Into Final Value, MAERSK — "Quotes Found" but Empty Excel (Diagnosis), ONE — All-Container-Type Search Returning 0 Quotes, ONE — Multi-Container Breakdown Triple-Counted / Inflated Final Value, ONE — Sold-Out ("Notify Me") Sailings Appearing as Quotes (+1 more)

### Community 65 - "layout.tsx"
Cohesion: 0.25
Nodes (6): frontend_src_app_globals, instrumentSans, inter, metadata, viewport, ThemeProvider()

### Community 66 - "GreenX — Surcharge Intake Fix (2026-06-30)"
Cohesion: 0.22
Nodes (8): Charges that must be taken into the final value (USD only), Files changed, Fix, GreenX — Surcharge Intake Fix (2026-06-30), Per-B/L charges (billed once per booking, added in full to *each* container type), Problem, Root cause, Verification

### Community 67 - "Admin Page & Port Prioritization Guide"
Cohesion: 0.25
Nodes (7): 1. Popular Ports (UN/LOCODEs), 2. Boosted Countries, Admin Page & Port Prioritization Guide, 🔒 How to Access the Admin Page, ⚙️ How to Use Port Prioritization, ⚡ Important Notes, 📝 Step-by-Step Example

### Community 68 - "._verify_price_owner_selected"
Cohesion: 0.25
Nodes (7): Verifies the "I am the price owner" radio is genuinely checked, piercing shadow…, [2026-07-03] — OOCL FreightSmart Autoclear, Hapag Price Leak & Redirect fixes, Maersk Cache Scoping, Dallas Overrides, Hapag-Lloyd — Price Leaks, Column Matching, and Redirect Recovery, Maersk — 0.0-USD / "Not Open" Card Flakiness (the "Quotes Found but Empty Excel" root causes), Maersk — Caching Scope & Selector Tuning, OOCL — FreightSmart Popup Dismissals & Input Lock Serialization, Ports — Hardcoded Dallas Override

### Community 69 - "port_routes.py"
Cohesion: 0.29
Nodes (9): get_countries(), get_port(), get_suggestions(), get, Get list of countries for autocomplete dropdown., Get specific port details by UN/LOCODE., Get port suggestions for autocomplete., search() (+1 more)

### Community 70 - ".select_cheapest_per_window"
Cohesion: 0.20
Nodes (6): Best-effort ETD date from a raw card dict (ISO, MM/DD/YYYY)., Picks the cheapest card in EACH tariff window the customer RFQ sheet needs:…, Backward-compatible: the single cheapest card (1ST window, else 2ND)., [2026-07-03] — Robustness Review & Multi-Port Quick Search Fixes, Quick Search (multi-port RFQ) — Per-Container Pricing Was Wrong, Robustness Review (see `docs/ROBUSTNESS_REVIEW_2026-07.md`)

### Community 71 - "parse_msc_modal_charges"
Cohesion: 0.24
Nodes (8): parse_msc_modal_charges(), Parses charges from MSC BreakdownModal text. Correctly includes charges whose…, Test MSC charges parsing for Singapore to Conakry, Guinea (40GP). Charges with…, Test when only some surcharges have the payment condition., test_msc_charges_mixed_conditions(), test_msc_charges_singapore_to_conakry_guinea(), Verify MSC charge extraction logic parses Panama Canal Surcharge properly., test_msc_charge_extraction_logic()

### Community 72 - "deploy"
Cohesion: 0.25
Nodes (7): build, builder, deploy, restartPolicyMaxRetries, restartPolicyType, startCommand, $schema

### Community 73 - "websockify_carrier_proxy"
Cohesion: 0.22
Nodes (5): websocket, Proxy WebSocket connections to legacy local x11vnc at localhost:5900., Proxy WebSocket connections to specific carrier x11vnc servers., websockify_carrier_proxy(), websockify_proxy()

### Community 74 - "tunnel_relay/main.py"
Cohesion: 0.25
Nodes (8): api_route, fastapi_middleware_cors, health(), get, Request, websocket, relay_request(), websocket_endpoint()

### Community 75 - "Summary of Changes — July 20, 2026"
Cohesion: 0.29
Nodes (6): 1. AI RFQ Front Door & Air Freight Support (Phase A), 2. Multi-Origin & Gappy List Parsing for Sea RFQs (Phase B), 3. Search Form Streamlining (Form Input Restrictions), 4. Native Gemini 2.5 Flash API & Chatbot Resiliency, 5. Verification & Test Suite, Summary of Changes — July 20, 2026

### Community 76 - "compute_admin_analytics"
Cohesion: 0.25
Nodes (8): compute_admin_analytics(), get_clean_lane_key(), normalize_lane_port(), Any, AsyncSession, Normalize port string to cleanly aggregate naming variations., Returns (norm_origin, norm_dest, display_lane_key)., Compute full consolidated analytics payload for the admin dashboard.

### Community 77 - "create_batch_rate_search"
Cohesion: 0.33
Nodes (9): create_batch_rate_search(), _contains(), _looks_like(), _norm(), _resolve(), create_rate_search(), Execute a multi-route RFQ batch using Vertical Parallel Persistent Sessions.…, Create a new rate search and dispatch carrier jobs. (+1 more)

### Community 78 - "resolve_port_alias"
Cohesion: 0.33
Nodes (6): _load_port_aliases_config(), Deterministically resolves a port string against ports_aliases.json and the…, resolve_port_alias(), Test that resolve_port_alias cleans 'City, Country' and parenthetical notes to…, test_resolve_city_country_format_to_clean_database_port_name(), Clean Search Dropdown Port Name Resolution (`rfq_agent.py` & `port_manager.py`)

### Community 79 - "test_brightdata.py"
Cohesion: 0.40
Nodes (5): get_title(), Script to test fetching CMA CGM pricing page using Bright Data Web Access HTTP…, test_brightdata_api(), urllib_error, urllib_request

### Community 80 - "devDependencies"
Cohesion: 0.22
Nodes (9): devDependencies, eslint, eslint-config-next, tailwindcss, @tailwindcss/postcss, @types/node, @types/react, @types/react-dom (+1 more)

### Community 81 - "Design system — read before touching any UI"
Cohesion: 0.33
Nodes (5): Animation rules, Client-only preferences, Design system — read before touching any UI, This is NOT the Next.js you know, Use tokens, not raw colours

### Community 82 - "test_panama_canal_surcharge.py"
Cohesion: 0.18
Nodes (11): Sort container types in standard order: DRY 20 (20GP) -> DRY 40 (40GP) -> DRY…, sort_container_types(), asyncio, Verify charge_classifier classifies Panama Canal Surcharge as…, Verify regex extraction of Estimated Transportation Days from Hapag-Lloyd modal…, Verify OOCL normalize_result incorporates Panama Canal Surcharge (PCS)., test_charge_classifier_panama_canal_surcharge(), test_container_types_standard_ordering() (+3 more)

### Community 83 - "[2026-05-29 – 2026-05-30] — Hapag-Lloyd Full Integration"
Cohesion: 0.40
Nodes (5): [2026-05-29 – 2026-05-30] — Hapag-Lloyd Full Integration, Hapag-Lloyd — Dropdown Autocomplete Issues, Hapag-Lloyd — Live Connector Implementation, Hapag-Lloyd — Onboarding Modal Blocking Form Interaction, Hapag-Lloyd — Search Button Selector Failures

### Community 84 - "[2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control"
Cohesion: 0.40
Nodes (5): [2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control, Concurrency Limit Queue & Admin Control Panel, MSC — Mediterranean Shipping Company Connector Implementation, ONE — Inbound Free Time Swap & Scraper Upgrade, OOCL — Orient Overseas Container Line Connector Implementation

### Community 85 - "[2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash"
Cohesion: 0.40
Nodes (5): [2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash, AI RFQ Front Door & Air Freight Support, Multi-Origin & Gappy List Parsing (Sea RFQs), Native Gemini 2.5 Flash Direct API Integration, Search Form Streamlining

### Community 89 - "[2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History"
Cohesion: 0.40
Nodes (5): [2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History, Admin User Search History & SGT GMT+8 Conversion (`AdminDashboard.tsx`), GreenX (Evergreen) Card Isolation & Surcharge Parsing (`greenx_connector.py`), Multi-Route Batch Execution Engine (`batch_engine.py`), OOCL FreightSmart 28-Day Calendar Expansion (`oocl_connector.py`)

### Community 90 - "hapag_freetime_scraper.py"
Cohesion: 0.50
Nodes (4): parse_hapag_pdf(), scrape_hapag_freetime(), pdfplumber, traceback

### Community 91 - "get_port_by_code"
Cohesion: 0.40
Nodes (3): get_port_by_code(), Resolves a port search text (e.g. 'Haiphong (VN HPH)', 'VN HPH', 'Hai Phong')…, Constructs the specific search query to type into carrier search boxes. If the…

### Community 92 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, dev, lint, start

### Community 93 - "[2026-06-03] — CMA CGM Routing & Free Time Extraction"
Cohesion: 0.50
Nodes (4): [2026-06-03] — CMA CGM Routing & Free Time Extraction, CMA CGM — Import Free Time from D&D Tab, CMA CGM — Routing Detection (Direct vs Transit), Maersk — Free Time Extraction from Card Text

### Community 94 - "[2026-08-04 - 2026-08-06] — CMA CGM Dynamic RAMP/POD Rerouting, Brand Excel Styling, Port Synonym Matching & Tunnel Relays"
Cohesion: 0.50
Nodes (4): [2026-08-04 - 2026-08-06] — CMA CGM Dynamic RAMP/POD Rerouting, Brand Excel Styling, Port Synonym Matching & Tunnel Relays, Brand-Aligned Excel Export Styling (`excel_export.py`), CMA CGM Dynamic RAMP / POD Advisory Banner Detection (`cma_connector.py`), Railway WebSocket Tunnel Relay & Failover (`tunnel_client.py`, `run_tunnel_client.bat`, `FailoverFetch`)

### Community 96 - "frontend/README.md"
Cohesion: 0.50
Nodes (3): Deploy on Vercel, Getting Started, Learn More

### Community 97 - "pytest"
Cohesion: 0.12
Nodes (11): Verify non-Maersk carriers get standard UN/LOCODE or default mappings., Verify that El Dekheila maps specifically to 'Alexandria Dekheila, Egypt' for…, test_el_dekheila_maersk_override(), test_el_dekheila_other_carriers_unaffected(), parse_hapag_card_text_mock(), Verify that multi-leg/feeder routes take the final arrival ETA and 28 days TT., Mock implementation of the JS evaluate logic inside hapag_lloyd_connector.py., test_hapag_multi_leg_schedule_extraction() (+3 more)

### Community 98 - "get_me"
Cohesion: 0.67
Nodes (3): get_me(), get, Get profile of currently signed-in user.

### Community 99 - "diagnose_greenx_dropdown.py"
Cohesion: 0.67
Nodes (3): dump_options(), main(), Diagnostic: dump ALL dropdown options (text + innerHTML) when typing 'DEHAM'…

### Community 100 - "test_one_premium_override.py"
Cohesion: 0.40
Nodes (3): MockCard, Unit test for ONE connector and charge classifier Premium Cargo Service…, test_premium_cargo_service_override()

### Community 102 - ".search_sailing_schedules"
Cohesion: 0.16
Nodes (8): HapagServiceUnavailableException, Exception, Detects the Microsoft B2C identity/OAuth login page. Hapag can silently bounce…, Guards against the session-expiry-mid-crawl failure mode: the existing redirect…, Crawls Hapag-Lloyd sailing schedules from the Schedule tab., Exception raised when Hapag-Lloyd API Gateway reports service is unavailable., Checks if Hapag-Lloyd API Gateway has returned 'This service is currently…, Hapag-Lloyd — Crawl Stalls by Typing a Port Locode Into the Login Email Field

### Community 103 - "[2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes"
Cohesion: 0.50
Nodes (4): [2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes, CMA CGM — Chrome Profile Bypass, ONE — Date Formatting & Charge Breakdown Pollution, ONE — Date Picker Pre-selection Issue

### Community 117 - "verify_admin_access"
Cohesion: 0.67
Nodes (3): Request, Verify that caller has admin privileges via session cookie, Bearer token, or…, verify_admin_access()

### Community 118 - "clean_selector_memory"
Cohesion: 0.67
Nodes (3): clean_selector_memory(), fixture, Wipes the selector memory JSON file before and after each test.

### Community 119 - "[2026-05-18 – 2026-05-19] — Railway Deployment & Docker"
Cohesion: 0.67
Nodes (3): [2026-05-18 – 2026-05-19] — Railway Deployment & Docker, Persistent Chrome Profiles on Railway Volume, Railway Deployment Setup

### Community 120 - "[2026-05-31] — Multi-Instance Support & Charge Classification"
Cohesion: 0.67
Nodes (3): [2026-05-31] — Multi-Instance Support & Charge Classification, Charge Classification Improvements, Multi-Instance Concurrent Searches

### Community 121 - "[2026-06-01] — Hapag-Lloyd Sold Out Detection & Date Parsing"
Cohesion: 0.67
Nodes (3): [2026-06-01] — Hapag-Lloyd Sold Out Detection & Date Parsing, Hapag-Lloyd — Date String Standardization, Hapag-Lloyd — Sold Out Schedule Detection

## Knowledge Gaps
- **307 isolated node(s):** `Config`, `install_pi.sh script`, `eslintConfig`, `nextConfig`, `name` (+302 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 905 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **26 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Changelog` connect `Changelog` to `[2026-06-30] — ONE Multi-Container & Sold-Out, GreenX Surcharge Intake, Free-Time Fixes, Maersk Diagnosis`, `[2026-07-28 - 2026-07-31] — GreenX Card Isolation, OOCL 28-Day Search Window, Multi-Route Batch Execution Engine & Admin Search History`, `._verify_price_owner_selected`, `.select_cheapest_per_window`, `[2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes`, `._fs_dismiss_modals`, `[2026-05-29 – 2026-05-30] — Hapag-Lloyd Full Integration`, `[2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control`, `[2026-07-20] — Air/Sea RFQ Classification, Dual Forwarder Routing, Multi-Origin Gappy Parsing, Search Form Streamlining & Chatbot Gemini 2.5 Flash`, `[2026-05-18 – 2026-05-19] — Railway Deployment & Docker`, `[2026-05-31] — Multi-Instance Support & Charge Classification`, `[2026-06-01] — Hapag-Lloyd Sold Out Detection & Date Parsing`, `[2026-07-22] — Mode-Branching Required Field Validation & Total Weight Division Split`, `[2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning`, `[2026-06-03] — CMA CGM Routing & Free Time Extraction`, `[2026-08-04 - 2026-08-06] — CMA CGM Dynamic RAMP/POD Rerouting, Brand Excel Styling, Port Synonym Matching & Tunnel Relays`, `[2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup`?**
  _High betweenness centrality (0.359) - this node is a cross-community bridge._
- **Why does `[2026-06-03] — CMA CGM Routing & Free Time Extraction` connect `[2026-06-03] — CMA CGM Routing & Free Time Extraction` to `Changelog`?**
  _High betweenness centrality (0.317) - this node is a cross-community bridge._
- **Why does `Maersk — Free Time Extraction from Card Text` connect `[2026-06-03] — CMA CGM Routing & Free Time Extraction` to `RateResults.tsx`?**
  _High betweenness centrality (0.316) - this node is a cross-community bridge._
- **Are the 27 inferred relationships involving `RateSearchRequest` (e.g. with `create_batch_rate_search()` and `create_rate_search()`) actually correct?**
  _`RateSearchRequest` has 27 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `cn()` (e.g. with `Reuse the primitives` and `7. Conventions to follow from here`) actually correct?**
  _`cn()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 21 inferred relationships involving `CarrierResultStatus` (e.g. with `safe_step()` and `update_carrier_status()`) actually correct?**
  _`CarrierResultStatus` has 21 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Config`, `install_pi.sh script`, `eslintConfig` to the rest of the system?**
  _307 weakly-connected nodes found - possible documentation gaps or missing edges._