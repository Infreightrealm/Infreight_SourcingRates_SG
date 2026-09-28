# Graph Report - backend  (2026-09-26)

## Corpus Check
- 143 files · ~1,906,388 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 9 file(s) not represented in the graph (top: (none) 2, .conf 2, .example 1)

## Summary
- 1368 nodes · 3589 edges · 71 communities (61 shown, 10 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 216 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `74e8849c`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- parse_rfq
- user_routes.py
- HapagLloydConnector
- auth_routes.py
- OOCLConnector
- MaerskConnector
- CMAConnector
- rate_search_routes.py
- ONEConnector
- os
- HapagLloydAPIConnector
- RateSearchRequest
- CarrierSearchResult
- social_routes.py
- GreenXConnector
- BaseCarrierConnector
- database.py
- AIBrowserAgent
- schemas.py
- PortManager
- QuoteSchema
- auth_service.py
- search_port
- job_service.py
- hapag_lloyd_connector.py
- MSCConnector
- ChargeCategory
- SearchQueueManager
- CarrierResultStatus
- dotenv
- oocl_connector.py
- pytest
- one_connector.py
- main.py
- port_manager.py
- test_panama_canal_surcharge.py
- test_self_healing.py
- registry.py
- .search_quotes
- CurrencyManager
- safe_step.py
- selector_memory.py
- test_normalizer.py
- analytics_service.py
- port_routes.py
- ai_agent.py
- resolve_port_for_carrier
- json
- headed_login_maersk.py
- websockify_carrier_proxy
- MockCard
- ai_repair_agent.py
- safe_step
- .run_batch_persistent_search
- _detect_port_mismatch
- verify_admin_access
- create_batch_rate_search
- test_auth_routes.py
- test_brightdata.py
- test_hapag_schedule.py
- diagnose_greenx_dropdown.py
- .validate_currency
- clean_selector_memory
- require_admin
- install_pi.sh
- models/__init__.py

## God Nodes (most connected - your core abstractions)
1. `RateSearchRequest` - 138 edges
2. `QuoteSchema` - 64 edges
3. `CarrierResultStatus` - 60 edges
4. `HapagLloydConnector` - 56 edges
5. `User` - 56 edges
6. `PortManager` - 53 edges
7. `CMAConnector` - 51 edges
8. `BaseCarrierConnector` - 46 edges
9. `MaerskConnector` - 44 edges
10. `ONEConnector` - 43 edges

## Surprising Connections (you probably didn't know these)
- `update_carrier_status()` --uses--> `CarrierResultStatus`  [INFERRED]
  backend/agent/safe_step.py → backend/models/schemas.py
- `safe_step()` --uses--> `CarrierResultStatus`  [INFERRED]
  backend/agent/safe_step.py → backend/models/schemas.py
- `get_current_user_optional()` --uses--> `User`  [INFERRED]
  backend/api/auth_routes.py → backend/models/user.py
- `get_current_user()` --uses--> `User`  [INFERRED]
  backend/api/auth_routes.py → backend/models/user.py
- `require_admin()` --uses--> `User`  [INFERRED]
  backend/api/auth_routes.py → backend/models/user.py

## Import Cycles
- None detected.

## Communities (71 total, 10 thin omitted)

### Community 0 - "parse_rfq"
Cohesion: 0.05
Nodes (76): parse_rfq_endpoint(), post, API routes for RFQ parsing agent., Parse a free-text RFQ email or message into a structured RateSearchRequest…, model_validator, Sort container types in standard order: DRY 20 (20GP) -> DRY 40 (40GP) -> DRY…, RFQParseResult, sort_container_types() (+68 more)

### Community 1 - "user_routes.py"
Cohesion: 0.09
Nodes (63): admin_delete_user(), AdminLoginRequest, approve_user(), CarrierOverrideRequest, Config, create_custom_port_endpoint(), CustomPortRequest, delete_carrier_override_endpoint() (+55 more)

### Community 2 - "HapagLloydConnector"
Cohesion: 0.06
Nodes (30): HapagLloydConnector, _apply_freetime_to_quote(), HapagServiceUnavailableException, Exception, Normalize various date formats (e.g. 2026-05-31, 31.05.2026, 31 May 2026, 31…, Robustly selects options from Hapag-Lloyd custom dropdown lists. Types the…, Detects the Microsoft B2C identity/OAuth login page. Hapag can silently bounce…, Guards against the session-expiry-mid-crawl failure mode: the existing redirect… (+22 more)

### Community 3 - "auth_routes.py"
Cohesion: 0.07
Nodes (57): clear_session_cookie(), get_current_user_optional(), login(), LoginRequest, logout(), AsyncSession, BaseModel, post (+49 more)

### Community 4 - "OOCLConnector"
Cohesion: 0.05
Nodes (28): clean_vessel_name(), get_booking_start_date(), OOCLConnector, _dismiss_once(), _click_date_strip_item(), _open_calendar(), _parse_date(), parse_oocl_date() (+20 more)

### Community 5 - "MaerskConnector"
Cohesion: 0.06
Nodes (23): MaerskConnector, flatten_tree(), Maersk Browser Connector — Playwright automation using your real Google Chrome…, Extracts freetime, demurrage, and detention from the 'Import D&D fees' tab…, Extracts the routing details from the 'Route & other details' accordion.…, Splits a single raw multi-container quote card into multiple QuoteSchema…, # NOTE: Bright Data Web Unlocker proxies break Playwright browser sessions…, Extracts the port/city name by removing any UN/LOCODE parentheses (e.g.,… (+15 more)

### Community 6 - "CMAConnector"
Cohesion: 0.08
Nodes (17): CMAConnector, Ensures 'Ramp' is explicitly selected under 'Type of location' toggle buttons…, Scans for Route, POL (Port of Loading), or POD (Port of Discharge) dropdown…, Clears the currently selected Destination port tag/card, re-types the locode,…, Dynamically extracts any recommended 5-letter POD LOCODE mentioned in the…, Detects if CMA CGM displayed an advisory banner message: "Looking for AEJEA or…, Handles the 'Customer account' -> 'Role (you are acting as)' dropdown on CMA…, Repeatedly clicks 'More results' if visible to load ALL quotes on the page. (+9 more)

### Community 7 - "rate_search_routes.py"
Cohesion: 0.08
Nodes (42): approve_repair(), ApproveRepairRequest, chat_endpoint(), ChatRequest, create_rate_search(), force_stop_searches(), get_admin_analytics_endpoint(), get_batch_search_status() (+34 more)

### Community 8 - "ONEConnector"
Cohesion: 0.08
Nodes (13): ONEConnector, _classify(), date, Parses ONE QUOTE Free Time popover text for DESTINATION ONLY. Ignores Origin…, Splits a single raw multi-container quote card into multiple QuoteSchema…, Tries to click a matching option from ONE's visible dropdown. Returns True only…, Extracts 5-letter UN/LOCODE from strings like 'Singapore (SGSIN)'., MockCard (+5 more)

### Community 9 - "os"
Cohesion: 0.10
Nodes (14): asyncio, os, Wrapper script to set Windows event loop policy before starting Uvicorn. This…, sys, Script to test Playwright browser launching using your REAL Google Chrome…, Quick CMA test with ALL proxy env vars forcibly cleared BEFORE any import…, debug_cma(), safe_str() (+6 more)

### Community 10 - "HapagLloydAPIConnector"
Cohesion: 0.09
Nodes (19): AsyncClient, HapagLloydAPIConnector, Any, Direct REST API connector for Hapag-Lloyd Prices API v2.1.4., API connectors do not require browser login sessions., Required abstract method implementation; delegates to run_full_search., Resolves a free-text port name or string (e.g. 'Singapore', 'Hamburg, Germany…, Hapag-Lloyd Prices API requires earliestDepartureDate to be at least 4 calendar… (+11 more)

### Community 11 - "RateSearchRequest"
Cohesion: 0.08
Nodes (27): RateSearchRequest, main(), Test script to run Belawan (IDBLW) -> Aden (YEADE) route on Maersk and MSC., test_maersk(), test_msc(), CMA CGM end-to-end test — login + search + extract quotes., # IMPORTANT: Clear ALL proxy env vars BEFORE any import triggers load_dotenv()…, test_cma() (+19 more)

### Community 12 - "CarrierSearchResult"
Cohesion: 0.14
Nodes (27): get_recent_search_status_context(), Chat Service — manages conversational AI queries from the frontend user using…, Queries the database for the most recent rate search status to give the chatbot…, Updates the status of a carrier search in the database., update_carrier_status(), get_route_health(), Get carrier search reliability & route health matrix across origin-destination…, get_async_session_maker() (+19 more)

### Community 13 - "social_routes.py"
Cohesion: 0.12
Nodes (28): get_current_user(), Dependency that strictly requires an authenticated active member., get_conversation(), list_colleagues(), poke_colleague(), PokeRequest, AsyncSession, BaseModel (+20 more)

### Community 14 - "GreenXConnector"
Cohesion: 0.11
Nodes (9): GreenXConnector, date, Overrides base search runner to query all 3 sizes at once and cache the…, Type a LOCODE into the autocomplete field and click the first visible dropdown…, Find quantity input next to or below label_text and fill it., Find the exact individual quote card container row encompassing dates, rates,…, Dismiss any cookie/alert modal that would intercept pointer events., Splits a single raw multi-container quote card into multiple QuoteSchema… (+1 more)

### Community 15 - "BaseCarrierConnector"
Cohesion: 0.08
Nodes (14): ABC, BaseCarrierConnector, Detects if a CAPTCHA, Turnstile, hCaptcha, reCAPTCHA, or 2FA screen is…, Abstract base class for carrier portal connectors., Best-effort ETD date from a raw card dict (ISO, MM/DD/YYYY)., The card's summary price. NOTE: on multi-container cards this is the SUM across…, Picks the cheapest card in EACH tariff window the customer RFQ sheet needs:…, Log into the carrier portal. Returns: True if login successful, False otherwise. (+6 more)

### Community 16 - "database.py"
Cohesion: 0.13
Nodes (22): get_sync_url(), run_migrations_offline(), run_migrations_online(), DeclarativeBase, logging_config, Base, _create_sqlite_engine(), _get_database_url() (+14 more)

### Community 17 - "AIBrowserAgent"
Cohesion: 0.12
Nodes (16): AIBrowserAgent, Capture the current page as a PNG screenshot., Build the prompt with task description and action history., Parse Gemini's response into an action dict., Call Gemini API with exponential backoff retry., Execute a parsed action on the browser page., Detect if the agent is stuck repeating the same action., Find all visible interactive elements and format them as a prompt guide. (+8 more)

### Community 18 - "schemas.py"
Cohesion: 0.15
Nodes (6): GreenX (Evergreen) Live Connector - Playwright automation., datetime, Pydantic schemas for API request/response validation., re, subprocess, time

### Community 19 - "PortManager"
Cohesion: 0.12
Nodes (5): PortManager, Retrieve verified carrier port name from persistent cache by UN/LOCODE,…, Cache verified carrier port name and save persistently to…, Clean and normalize user input for port searching., Retrieve port data by full UN/LOCODE (e.g., 'SGSIN').

### Community 20 - "QuoteSchema"
Cohesion: 0.11
Nodes (11): _generate_maersk_mock_quotes(), _generate_msc_mock_quotes(), _generate_one_mock_quotes(), MockCarrierConnector, any, Generate realistic ONE sample quotes with charge breakdowns., Generate realistic MSC sample quotes with validity_till., Generate realistic Maersk sample quotes with charge breakdowns. (+3 more)

### Community 21 - "auth_service.py"
Cohesion: 0.13
Nodes (21): hashlib, hmac, AuditLog, AuthSession, Stores hashed active session tokens., Stores security and operational audit trail entries., secrets, get_client_ip() (+13 more)

### Community 22 - "search_port"
Cohesion: 0.12
Nodes (10): fill_container_card(), get_carrier_search_query(), get_port_by_code(), normalize_port_input(), Suggest top N ports for a partial query., Resolves a port search text (e.g. 'Haiphong (VN HPH)', 'VN HPH', 'Hai Phong')…, Constructs the specific search query to type into carrier search boxes. If the…, Search for ports by code, name, or alias. Returns top matches ranked by… (+2 more)

### Community 23 - "job_service.py"
Cohesion: 0.14
Nodes (19): close_all_active_connectors(), Force close all active carrier connectors and their Playwright Chrome windows., Quote, Represents a single freight quote from a carrier., cancel_all_active_searches(), UUID, Job Service — orchestrates carrier search jobs. Creates background tasks per…, Check all carrier results and update the overall search status. (+11 more)

### Community 24 - "hapag_lloyd_connector.py"
Cohesion: 0.19
Nodes (14): CMA CGM Live Connector — Playwright automation. Credentials read from env:…, # NOTE: No start date fill needed — schedule page defaults to today,, Hapag-Lloyd Live Connector -- Playwright automation. Credentials read from env:…, Mock Carrier Connector — returns realistic sample data for testing. Used when…, ChargeSchema, patchright_async_api, random, format_maersk_date() (+6 more)

### Community 25 - "MSCConnector"
Cohesion: 0.18
Nodes (7): format_to_iso_date(), MSCConnector, Playwright-based automation for MSC (Mediterranean Shipping Company)., Handles the MSC login flow., Clicks Instant Quote, fills form, clicks Search., Detects and clicks the 'Ramp' delivery/haulage option if MSC displays Ramp /…, Parse '14 Jun 2026' to 'YYYY-MM-DD

### Community 26 - "ChargeCategory"
Cohesion: 0.25
Nodes (18): ChargeCategory, classify_charge(), Classify a charge line item based on its name, amount, section heading, and…, Tests for charge classifier., test_basic_ocean_freight(), test_destination_charges(), test_discount(), test_freight_surcharges() (+10 more)

### Community 27 - "SearchQueueManager"
Cohesion: 0.11
Nodes (10): Lock, Marks a search as completed internally so we can track the auto-release timeout., Called periodically in a background task to check if the user has held the lock…, Forcefully clears all queued searches and the active lock. Useful for…, Returns or creates an asyncio.Lock for a specific carrier code to prevent…, Adds a search to the queue and waits until it becomes the active search. Event-…, Singleton manager to enforce a FIFO queue for rate searches. Since web scraping…, Returns the current position of the search in the queue. 0 means it is the… (+2 more)

### Community 28 - "CarrierResultStatus"
Cohesion: 0.19
Nodes (9): Calls the connector's per-container splitter whether it is sync or async…, Quick-mode quote builder shared by every connector and both search paths. Fixes…, Execute the full search flow: 1. Login 2. Search quotes 3. Extract quote list…, One route of a persistent batch on the already-open session (no login/close)., Enum, CarrierCode, CarrierResultStatus, SearchStatus (+1 more)

### Community 29 - "dotenv"
Cohesion: 0.13
Nodes (11): dotenv, getpass, Hapag-Lloyd form inspector., Test multi-container search and caching for Hapag-Lloyd connector., test_caching(), Debug script: Reuse HapagLloydConnector login, then step through the Schedule…, run(), ss() (+3 more)

### Community 30 - "oocl_connector.py"
Cohesion: 0.16
Nodes (6): Base Carrier Connector — abstract base class for all carrier connectors. Each…, RateLimiter, Hapag-Lloyd Prices API Connector (REST API v2.1.4). Provides real-time rate…, Token-bucket rate limiter to strictly respect Tryout/Production rate limits., OOCL Live Connector â€” Playwright automation for Sailing Schedules., typing

### Community 31 - "pytest"
Cohesion: 0.16
Nodes (12): parse_msc_modal_charges(), Parses charges from MSC BreakdownModal text. Correctly includes charges whose…, pytest, parse_hapag_section(), Unit test to verify Hapag-Lloyd Price Breakdown section classification logic.…, test_hapag_section_parsing_order(), Test MSC charges parsing for Singapore to Conakry, Guinea (40GP). Charges with…, Test when only some surcharges have the payment condition. (+4 more)

### Community 32 - "one_connector.py"
Cohesion: 0.16
Nodes (8): ONE (Ocean Network Express) Live Connector — Playwright automation. Credentials…, # TODO: Verify selectors against ONE ecommerce portal, Charge Classifier — rule-based classification of freight charge line items.…, asyncio, test_one_breakdown_currency_and_arbitrary_destination_classification(), MockCard, Unit test for ONE connector and charge classifier Premium Cargo Service…, test_premium_cargo_service_override()

### Community 33 - "main.py"
Cohesion: 0.15
Nodes (14): contextlib, fastapi_middleware_cors, fastapi_staticfiles, health(), lifespan(), get, Infreight Ocean Carrier Rate Automation — FastAPI Application. Main entry point…, Check if the VNC viewer is available (production only, where Xvfb runs). (+6 more)

### Community 34 - "port_manager.py"
Cohesion: 0.26
Nodes (11): difflib, add_carrier_override(), add_custom_port(), delete_carrier_override(), delete_custom_port(), get_carrier_overrides(), get_custom_ports(), get_popular_ports_config() (+3 more)

### Community 35 - "test_panama_canal_surcharge.py"
Cohesion: 0.18
Nodes (14): is_weight_surcharge_applicable(), Evaluates whether a weight-tier or overweight surcharge is applicable for the…, classify_and_organize_charges(), Takes raw charge line items and classifies them. Args: raw_charges: list of…, test_classify_and_organize(), asyncio, Verify non-applicable weight tier surcharges are excluded from final value for…, Verify regex extraction of Estimated Transportation Days from Hapag-Lloyd modal… (+6 more)

### Community 36 - "test_self_healing.py"
Cohesion: 0.21
Nodes (13): handle_chat_query(), _local_chatbot_fallback(), Intelligent responder for search status, carrier guidance, air/sea info, and…, Sends the chat message and history to native Gemini 2.5 Flash API. If Gemini…, detect_manual_action_required(), Page, Scans the current Playwright page to see if a CAPTCHA, Cloudflare challenge,…, asyncio (+5 more)

### Community 37 - "registry.py"
Cohesion: 0.18
Nodes (8): NotAvailableConnector, Placeholder connector for carriers not yet implemented., Override to immediately return CONNECTOR_NOT_AVAILABLE., CMACGMConnector, CMA CGM Connector — not yet implemented. Returns CONNECTOR_NOT_AVAILABLE., get_connector(), Carrier Registry — factory for getting the right connector per carrier. When…, Get the appropriate connector for a carrier. If USE_MOCK_CARRIERS=true: returns…

### Community 38 - ".search_quotes"
Cohesion: 0.15
Nodes (8): extract_locode_and_country(), prepare_maersk_query(), Verifies the "I am the price owner" radio is genuinely checked, piercing shadow…, Extracts LOCODE and country name from text like 'CASABLANCA, MOROCCO (MACAS)'…, Maps standard container search codes (e.g. 'DRY 20', '20GP') to Maersk Spot…, Scores a Maersk autocomplete dropdown suggestion. NOTE: The nested/indented…, Fills an autocomplete field using the proven original element-level…, get_cached_carrier_port()

### Community 39 - "CurrencyManager"
Cohesion: 0.23
Nodes (7): convert_currency_to_usd(), CurrencyManager, get_all_exchange_rates(), Any, Currency Exchange Rate Service — manages currency conversions and custom…, update_exchange_rate(), threading

### Community 40 - "safe_step.py"
Cohesion: 0.21
Nodes (9): Failure Detector — parses and structures error context from failed Playwright…, Manual Action Detector — identifies pages requiring human verification (2FA,…, capture_page_state(), Page, Page Observer — captures page state (screenshot, DOM, visible text) on failure., Captures screenshot, DOM HTML, and inner text of the current page. Saves…, Safe Step — Playwright action execution wrapper with manual intervention pause…, inspect (+1 more)

### Community 41 - "selector_memory.py"
Cohesion: 0.24
Nodes (12): get_approved_selector(), _load_memory(), Selector Memory — stores and retrieves human-approved selector patches., Loads memory JSON file. Returns empty dict if file is missing or invalid., Saves memory dict back to JSON file., Looks up if there is an approved replacement selector for the given carrier and…, Stores an approved replacement selector., Marks any proposed selector for this step as REJECTED. (+4 more)

### Community 42 - "test_normalizer.py"
Cohesion: 0.23
Nodes (8): calculate_final_freight_value(), Calculate the final freight value from a list of classified charges. Args:…, Tests for normalizer / final freight value calculator., test_basic_calculation(), test_no_charges(), test_one_breakdown_parsing(), test_only_excluded(), test_positive_discount_normalized()

### Community 43 - "analytics_service.py"
Cohesion: 0.22
Nodes (10): compute_admin_analytics(), get_clean_lane_key(), normalize_lane_port(), Any, AsyncSession, Consolidated Analytics Service for Infreight Ocean Carrier Rate Automation.…, Normalize port string to cleanly aggregate naming variations., Returns (norm_origin, norm_dest, display_lane_key). (+2 more)

### Community 44 - "port_routes.py"
Cohesion: 0.29
Nodes (9): get_countries(), get_port(), get_suggestions(), get, Get list of countries for autocomplete dropdown., Get specific port details by UN/LOCODE., Get port suggestions for autocomplete., search() (+1 more)

### Community 45 - "ai_agent.py"
Cohesion: 0.22
Nodes (8): base64, AI Browser Agent — Vision-based browser automation using Gemini Flash. This…, google, google_genai, pdfplumber, parse_hapag_pdf(), scrape_hapag_freetime(), traceback

### Community 46 - "resolve_port_for_carrier"
Cohesion: 0.24
Nodes (9): Resolves input text (e.g. 'Belfast (GBBEL)' or 'GBBEL') to a tuple of…, resolve_msc_port(), Resolves input text to (location_name, locode, country_code, country_name)., resolve_oocl_port_info(), resolve_port_for_carrier(), Verify non-Maersk carriers get standard UN/LOCODE or default mappings., Verify that El Dekheila maps specifically to 'Alexandria Dekheila, Egypt' for…, test_el_dekheila_maersk_override() (+1 more)

### Community 47 - "json"
Cohesion: 0.31
Nodes (7): generate_report(), Repair Report — generates and saves diagnosis reports on Playwright selector…, Assembles a comprehensive repair report and writes it as JSON and Markdown…, json, check_and_wait_for_captcha(), login(), main()

### Community 48 - "headed_login_maersk.py"
Cohesion: 0.22
Nodes (5): glob, Interactive Headed Login Helper for Maersk. Opens real Chrome using the…, Storage Cleanup Utility — automatically removes stale debug screenshots, HTML…, shutil, tempfile

### Community 49 - "websockify_carrier_proxy"
Cohesion: 0.22
Nodes (5): Proxy WebSocket connections to legacy local x11vnc at localhost:5900., Proxy WebSocket connections to specific carrier x11vnc servers., websockify_carrier_proxy(), websockify_proxy(), websocket

### Community 51 - "ai_repair_agent.py"
Cohesion: 0.29
Nodes (7): _local_fuzzy_repair(), AI Repair Agent — diagnoses Playwright step failures and suggests selector…, A local rule-based heuristic to locate reasonable buttons or inputs when Gemini…, Analyzes the failure context and DOM content to suggest a selector repair. Uses…, suggest_fix(), bs4, test_ai_repair_agent_offline_fallback()

### Community 52 - "safe_step"
Cohesion: 0.25
Nodes (8): capture_failure_context(), Exception, Page, Assembles a standardized diagnostic dictionary containing all available details…, Page, Executes a Playwright action. If it fails: 1. Detects CAPTCHA/bot challenges…, safe_step(), test_failure_detector()

### Community 53 - ".run_batch_persistent_search"
Cohesion: 0.29
Nodes (4): Any, Clean up browser resources robustly, ensuring failures or hangs never block…, Returns the open session to a clean search page for the next route. With…, Executes a vertical batch search over multiple route requests using a SINGLE…

### Community 54 - "_detect_port_mismatch"
Cohesion: 0.25
Nodes (8): _detect_port_mismatch(), Detects port mismatch for origin or destination. Returns: - True if verified…, Test that matching LOCODE or City + Country code returns False (Verified Match)., Test that differing port strings return True (Verified Mismatch)., Test that null/empty matched port strings return None (Unknown / Could Not…, test_detect_port_mismatch_unknown_null(), test_detect_port_mismatch_verified_match(), test_detect_port_mismatch_verified_mismatch()

### Community 55 - "verify_admin_access"
Cohesion: 0.27
Nodes (6): get_me(), get, Get profile of currently signed-in user., Request, Verify that caller has admin privileges via session cookie, Bearer token, or…, verify_admin_access()

### Community 56 - "create_batch_rate_search"
Cohesion: 0.60
Nodes (6): create_batch_rate_search(), _contains(), _looks_like(), _norm(), _resolve(), Execute a multi-route RFQ batch using Vertical Parallel Persistent Sessions.…

### Community 57 - "test_auth_routes.py"
Cohesion: 0.33
Nodes (5): httpx, pytest_asyncio, asyncio, Integration tests for authentication, legacy user password setup, pending…, test_full_auth_lifecycle()

### Community 58 - "test_brightdata.py"
Cohesion: 0.40
Nodes (5): get_title(), Script to test fetching CMA CGM pricing page using Bright Data Web Access HTTP…, test_brightdata_api(), urllib_error, urllib_request

### Community 59 - "test_hapag_schedule.py"
Cohesion: 0.50
Nodes (4): parse_hapag_card_text_mock(), Verify that multi-leg/feeder routes take the final arrival ETA and 28 days TT., Mock implementation of the JS evaluate logic inside hapag_lloyd_connector.py., test_hapag_multi_leg_schedule_extraction()

### Community 60 - "diagnose_greenx_dropdown.py"
Cohesion: 0.67
Nodes (3): dump_options(), main(), Diagnostic: dump ALL dropdown options (text + innerHTML) when typing 'DEHAM'…

### Community 62 - "clean_selector_memory"
Cohesion: 0.67
Nodes (3): fixture, clean_selector_memory(), Wipes the selector memory JSON file before and after each test.

## Knowledge Gaps
- **2 isolated node(s):** `Config`, `install_pi.sh script`
  These have ≤1 connection - possible missing edges. (Counts symbols only; 529 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `RateSearchRequest` connect `RateSearchRequest` to `parse_rfq`, `HapagLloydConnector`, `OOCLConnector`, `MaerskConnector`, `CMAConnector`, `rate_search_routes.py`, `ONEConnector`, `os`, `HapagLloydAPIConnector`, `CarrierSearchResult`, `GreenXConnector`, `BaseCarrierConnector`, `schemas.py`, `QuoteSchema`, `search_port`, `job_service.py`, `hapag_lloyd_connector.py`, `MSCConnector`, `CarrierResultStatus`, `dotenv`, `oocl_connector.py`, `one_connector.py`, `registry.py`, `.search_quotes`, `.run_batch_persistent_search`, `create_batch_rate_search`?**
  _High betweenness centrality (0.159) - this node is a cross-community bridge._
- **Why does `HapagLloydConnector` connect `HapagLloydConnector` to `registry.py`, `os`, `RateSearchRequest`, `ai_agent.py`, `BaseCarrierConnector`, `QuoteSchema`, `hapag_lloyd_connector.py`, `CarrierResultStatus`, `dotenv`?**
  _High betweenness centrality (0.089) - this node is a cross-community bridge._
- **Why does `QuoteSchema` connect `QuoteSchema` to `HapagLloydConnector`, `OOCLConnector`, `MaerskConnector`, `CMAConnector`, `rate_search_routes.py`, `ONEConnector`, `HapagLloydAPIConnector`, `GreenXConnector`, `BaseCarrierConnector`, `schemas.py`, `job_service.py`, `hapag_lloyd_connector.py`, `MSCConnector`, `CarrierResultStatus`, `oocl_connector.py`, `one_connector.py`, `test_panama_canal_surcharge.py`, `registry.py`, `.run_batch_persistent_search`, `.validate_currency`?**
  _High betweenness centrality (0.076) - this node is a cross-community bridge._
- **Are the 25 inferred relationships involving `RateSearchRequest` (e.g. with `create_batch_rate_search()` and `create_rate_search()`) actually correct?**
  _`RateSearchRequest` has 25 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `QuoteSchema` (e.g. with `get_rate_search()` and `BaseCarrierConnector`) actually correct?**
  _`QuoteSchema` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `CarrierResultStatus` (e.g. with `safe_step()` and `update_carrier_status()`) actually correct?**
  _`CarrierResultStatus` has 16 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Config`, `install_pi.sh script` to the rest of the system?**
  _2 weakly-connected nodes found - possible documentation gaps or missing edges._