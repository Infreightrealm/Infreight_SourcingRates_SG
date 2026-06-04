# Changelog

All notable changes to the Infreight Ocean Carrier Rate Automation system are documented here.  
Entries are grouped by date and by carrier/component. Each entry describes the problem (bug), the root cause, and the fix applied.

---

## [2026-06-04] — Routing, Free Time, Sold Out Rows & Storage Cleanup

### Excel Export — Sold Out Rows Not Showing
- **Bug:** Carriers that returned zero quotes (e.g. Hapag-Lloyd with no sailings, ONE with no sailings) were silently omitted from the Excel export. The user had no way to know whether the carrier was searched or simply missing.
- **Root Cause:** `exportToExcel` in `ResultsTable.tsx` only iterated over `quoteRows` (carriers that had at least one quote). Carriers with `NO_QUOTES_AVAILABLE` or `CONNECTOR_NOT_AVAILABLE` status were filtered out entirely.
- **Fix:** Changed the Excel generator to iterate over `sortedRows` (all carriers). If a carrier has no quote object, a row is still generated with "Sold out" in the Rate column and the error message or "No quotes returned" in the Remark column.
- **Files:** `frontend/src/components/ResultsTable.tsx`

### Excel Export — Routing & Free Time Columns Always Empty
- **Bug:** The Free Time and Routing columns in the Excel were always "-" or "Direct", even though the backend logs confirmed successful extraction (e.g. `[CMA] Extracted Import Free Time: 7 days`).
- **Root Cause:** This was a **database serialization gap**. The scraper extracted `routing` and `free_time` into the `QuoteSchema` object correctly. However, `job_service.py` saved each quote to the database using explicit column mappings, and the `Quote` database table had no dedicated `routing` or `free_time` columns. These fields were silently dropped during the DB save. When the API later read the quote back from the DB, it fell back to defaults ("Direct" / null).
- **Fix:** Modified `job_service.py` to persist `routing` and `free_time` inside the existing `raw_data_json` JSON blob column. Updated `rate_search_routes.py` to extract `routing` and `free_time` from `raw_data_json` when constructing the API response.
- **Files:** `backend/services/job_service.py`, `backend/api/rate_search_routes.py`

### CMA CGM — 30-Second Timeout on Sold Out Cards
- **Bug:** When CMA CGM returned a "Sold out" sailing card (e.g. AMERIGO VESPUCCI), the connector hung for 30 seconds trying to click a "Details" button that didn't exist on sold-out cards, then threw a timeout error.
- **Root Cause:** `open_price_breakdown()` unconditionally attempted `scroll_into_view_if_needed()` on a `Details` button locator without first checking if the button was actually present. Sold-out cards on CMA CGM don't have a Details button.
- **Fix:** Added a fast 2-second visibility check (`details_btn.is_visible(timeout=2000)`) before attempting the click. If the button doesn't exist, the method returns `False` immediately, and the quote is still normalized with the data already extracted from the card text.
- **Files:** `backend/carriers/cma_connector.py`

### CMA CGM — Routing Regex Not Matching "via LEKKI, LA, NG"
- **Bug:** CMA CGM routing was always reported as "Direct" even when the card clearly showed `via LEKKI, LA, NG`.
- **Root Cause:** The regex used `\b` word boundary assertions. The text preceding `via` on the CMA CGM page contained non-word characters (special whitespace, arrows, icons) that broke the word boundary match.
- **Fix:** Removed all `\b` boundary assertions from the routing regex. Now uses a simple `(via\s+[^\r\n]+|Direct)` pattern.
- **Files:** `backend/carriers/cma_connector.py`

### CMA CGM — Free Time Regex Too Strict
- **Bug:** The Import Free Time extraction sometimes failed even when the D&D tab was successfully opened.
- **Root Cause:** The regex required the exact word `Merged` to appear between "Import free time" and the duration number. Some CMA CGM pages used different table layouts where `Merged` was absent or formatted differently.
- **Fix:** Relaxed the regex from `Import free time.*?Merged.*?\b(\d+)\s+Calendar` to `Import free time.*?(\d+)\s+Calendar` with `DOTALL` flag.
- **Files:** `backend/carriers/cma_connector.py`

### Chromium Cache Auto-Cleanup (Railway Storage Bloat Prevention)
- **Bug:** Railway volume storage was steadily growing toward the 5GB limit because Chromium cached website images, fonts, scripts, and GPU data across carrier sessions.
- **Root Cause:** After each search, the connector synced the entire temp browser profile (including cache directories) back to the master profile directory on the Railway volume. Cache directories like `Cache`, `Code Cache`, `GPUCache`, and `ScriptCache` accumulated gigabytes of data.
- **Fix:** Added automatic cache directory cleanup to the `close()` method of all three live connectors (Maersk, CMA CGM, Hapag-Lloyd). After syncing the temp profile back to master, the code iterates through the master profile and deletes `Cache`, `Code Cache`, `GPUCache`, `ScriptCache`, and `Service Worker` directories, while preserving `Cookies`, `Local Storage`, and `Login Data`.
- **Files:** `backend/carriers/maersk_connector.py`, `backend/carriers/cma_connector.py`, `backend/carriers/hapag_lloyd_connector.py`

### Maersk — Hardcoded Port Overrides
- **Bug:** Maersk autocomplete could not resolve "Shuaiba" or "Lagos" to the correct dropdown suggestion because these port names had ambiguous or missing results in Maersk's search.
- **Fix:** Added hardcoded overrides:
  - `shuaiba` → `"Shuaiba, Kuwait"`
  - `lagos` → `"Lagos, Nigeria"`
- **Files:** `backend/carriers/maersk_connector.py`

---

## [2026-06-03] — CMA CGM Routing & Free Time Extraction

### CMA CGM — Routing Detection (Direct vs Transit)
- **Feature:** CMA CGM schedule cards now have their routing extracted. If the card text contains `via JEDDAH, SA` (or any `via` text), routing is set to `"Transit - JEDDAH, SA"`. If the text contains `Direct` or no `via` text, routing is set to `"Direct"`.
- **Files:** `backend/carriers/cma_connector.py`

### CMA CGM — Import Free Time from D&D Tab
- **Feature:** After extracting the rate for each CMA CGM sailing card, the connector now clicks the "D&D" (Detention & Demurrage) tab, reads the "Import free time" section, and extracts the duration in calendar days. This value is stored as `free_time` on the quote.
- **Note:** Free time extraction is secondary to rate extraction — if it fails, the quote is still saved with the rate data.
- **Files:** `backend/carriers/cma_connector.py`

### Maersk — Free Time Extraction from Card Text
- **Feature:** Maersk cards often include text like `Incl. 5 days of detention freetime`. The connector now parses this text and extracts the free time value. The frontend `getFreeTimeValue()` helper also attempts to parse this from `service_name` as a fallback.
- **Files:** `backend/carriers/maersk_connector.py`, `frontend/src/components/ResultsTable.tsx`

---

## [2026-06-02] — Hapag-Lloyd Transshipment & Duplicate Fix

### Hapag-Lloyd — Duplicate Sailings from Transshipment Vessels
- **Bug:** For Singapore to Karachi (40GP), Hapag-Lloyd showed 4 sailings but the program reported 8. Each sailing card listed two vessel/voyage names because the route involved a vessel change (transshipment), and the scraper treated each vessel line as a separate sailing.
- **Root Cause:** The schedule card parser split on vessel lines and created one quote per vessel. A transshipment card with two vessels (e.g. vessel A departing, vessel B arriving after a change at Nhava Sheva) was interpreted as two separate sailings.
- **Fix:** Updated the parser to treat each schedule card as a single sailing regardless of how many vessels are listed. The routing is now extracted from the card's "via" text (e.g. "via Nhava Sheva, INNSA Salalah, OMSLL"), and the routing field is set to "Transit" with the transshipment ports listed.
- **Files:** `backend/carriers/hapag_lloyd_connector.py`

### Hapag-Lloyd — Routing Not Marked as Transit
- **Bug:** Even when Hapag-Lloyd showed transshipment ports, the routing was still marked as "Direct" in the output.
- **Fix:** If the card has multiple vessels or a `via` line, routing is automatically set to a transit route with the intermediate port names.
- **Files:** `backend/carriers/hapag_lloyd_connector.py`

---

## [2026-06-01] — Hapag-Lloyd Sold Out Detection & Date Parsing

### Hapag-Lloyd — Sold Out Schedule Detection
- **Bug:** Hapag-Lloyd sometimes displayed schedule cards with no price, indicating the sailing was sold out. The scraper treated these as valid quotes with a $0 price.
- **Fix:** Added explicit sold-out detection. Cards without a valid price or with "sold out" text are flagged and excluded from the quote list.
- **Files:** `backend/carriers/hapag_lloyd_connector.py`

### Hapag-Lloyd — Date String Standardization
- **Bug:** ETD and ETA dates from Hapag-Lloyd were in inconsistent formats, causing parsing failures.
- **Fix:** Implemented `standardize_date_string()` to normalize all date formats to ISO 8601 (`YYYY-MM-DD`).
- **Files:** `backend/carriers/hapag_lloyd_connector.py`

---

## [2026-05-31] — Multi-Instance Support & Charge Classification

### Multi-Instance Concurrent Searches
- **Bug:** Running two searches simultaneously (e.g. on two browser tabs) caused browser profile corruption because both carrier instances tried to use the same Chromium profile directory.
- **Fix:** Each search now creates an isolated temporary Chromium profile cloned from the master profile. The temp profile is used for the search, then synced back to the master after completion and deleted. This allows unlimited concurrent searches without conflicts.
- **Files:** `backend/carriers/maersk_connector.py`, `backend/carriers/cma_connector.py`, `backend/carriers/hapag_lloyd_connector.py`

### Charge Classification Improvements
- **Bug:** Freight surcharges marked with destination or origin keywords (e.g. "Destination Terminal Handling") were incorrectly classified as `FREIGHT_SURCHARGE_INCLUDED`, inflating the final freight value.
- **Fix:** Updated the charge classifier to check for destination/origin keywords first before classifying as a freight surcharge. Added word boundary matching to prevent false positives (e.g. "ees" matching inside "fees").
- **Files:** `backend/services/charge_classifier.py`

---

## [2026-05-29 – 2026-05-30] — Hapag-Lloyd Full Integration

### Hapag-Lloyd — Live Connector Implementation
- **Feature:** Built a complete Hapag-Lloyd carrier connector with:
  - Login automation with credential filling and session persistence
  - Search form automation (origin, destination, container type, quantity, weight)
  - Calendar grid pagination to find all available departure dates
  - Schedule card extraction with ETD, ETA, transit time, vessel, and voyage
  - Price breakdown modal interaction and charge extraction
  - Transshipment detection and routing classification
- **Files:** `backend/carriers/hapag_lloyd_connector.py`

### Hapag-Lloyd — Dropdown Autocomplete Issues
- **Bug:** The Hapag-Lloyd search form's autocomplete dropdown was unreliable. Short port codes like "KG" were matching inside longer strings like "MYPKG". The dropdown sometimes showed "Your Door" options that crashed the search.
- **Fix:** Implemented regex word boundary matching for dropdown suggestion filtering. Added fallback logic to skip "Your Door" options. Added retry loops for selection verification.
- **Files:** `backend/carriers/hapag_lloyd_connector.py`

### Hapag-Lloyd — Onboarding Modal Blocking Form Interaction
- **Bug:** Hapag-Lloyd showed a "Recently Searched" modal popup and multi-step onboarding wizard that blocked form interaction.
- **Fix:** Added automated detection and dismissal of these modals before and after form interaction. Handles up to 5 sequential popup steps.
- **Files:** `backend/carriers/hapag_lloyd_connector.py`

### Hapag-Lloyd — Search Button Selector Failures
- **Bug:** The search button used custom web components that standard CSS selectors couldn't target.
- **Fix:** Implemented multiple fallback selectors including `button:has-text("Search")`, custom element queries, and XPath. Added filtering to exclude page header elements.
- **Files:** `backend/carriers/hapag_lloyd_connector.py`

---

## [2026-05-27 – 2026-05-28] — ONE & CMA CGM Connector Fixes

### ONE — Date Formatting & Charge Breakdown Pollution
- **Bug:** ONE dates were returned in non-standard formats. Charge breakdowns from one card were "bleeding" into adjacent cards.
- **Fix:** Standardized all ONE dates to ISO format. Scoped charge extraction strictly to the currently opened card's DOM subtree.
- **Files:** `backend/carriers/one_connector.py`

### ONE — Date Picker Pre-selection Issue
- **Bug:** When a departure date was already pre-selected in the ONE date picker, the connector failed to change it.
- **Fix:** Clear any pre-selected date before making a new selection.
- **Files:** `backend/carriers/one_connector.py`

### CMA CGM — Chrome Profile Bypass
- **Feature:** Implemented persistent Chrome profile with cookie/session reuse to bypass repeated login and anti-bot challenges.
- **Files:** `backend/carriers/cma_connector.py`

---

## [2026-05-25 – 2026-05-26] — VNC Display Isolation & Proxy Integration

### VNC Display Isolation for Concurrent Carriers
- **Bug:** When multiple carriers ran simultaneously, they competed for the same virtual display, causing rendering conflicts and crashes.
- **Fix:** Each carrier connector now launches its Chromium browser on an isolated VNC display using the Playwright `DISPLAY` environment parameter. Displays are allocated thread-safely to prevent collisions.
- **Files:** `backend/carriers/maersk_connector.py`, `backend/carriers/cma_connector.py`, `backend/carriers/one_connector.py`, `backend/carriers/hapag_lloyd_connector.py`

### Bright Data ISP Proxy Integration
- **Feature:** Integrated Bright Data residential/ISP proxy routing for Maersk and CMA CGM to avoid IP-based blocks. Added sticky session ID pinning for consistent IP assignment.
- **Files:** `backend/carriers/maersk_connector.py`, `backend/carriers/cma_connector.py`

---

## [2026-05-23 – 2026-05-24] — Maersk Shadow DOM & Stealth Upgrades

### Maersk — Shadow DOM Piercing for MDS Web Components
- **Bug:** Maersk redesigned their portal using MDS web components with Shadow DOM encapsulation. Standard selectors could not access input fields inside shadow roots.
- **Fix:** Implemented shadow DOM piercing selectors and wait-click patterns for MDS web component host elements. Upgraded to Patchright (stealth Playwright fork) for better anti-bot evasion.
- **Files:** `backend/carriers/maersk_connector.py`

### Maersk — Login Credential Autofill Corruption
- **Bug:** Browser autofill sometimes pre-populated the login fields, and the connector's typed credentials were appended to the autofilled text, corrupting the login.
- **Fix:** Added keyboard shortcut clear (Ctrl+A → Delete) before typing each credential field.
- **Files:** `backend/carriers/maersk_connector.py`

### Maersk — 2FA/CAPTCHA Human-in-the-Loop via noVNC
- **Feature:** When Maersk requires 2FA or CAPTCHA verification, the system exposes the browser session via a noVNC web viewer. The user can visually see and interact with the browser to complete verification, then the automation resumes.
- **Files:** `backend/carriers/maersk_connector.py`

---

## [2026-05-20 – 2026-05-22] — Port Resolution & Frontend Improvements

### Port Resolution System
- **Feature:** Built a carrier-specific port resolution system. Each carrier has its own port name conventions:
  - Maersk expects `"Singapore"` while CMA CGM expects `"Singapore, SG"`
  - Bangkok needs to be `"Bangkok PAT, Thailand"` for Maersk
  - Batam triggers a warning since it's not a standard port for most carriers
- **Files:** `backend/carriers/maersk_connector.py`, `backend/carriers/cma_connector.py`, `backend/carriers/one_connector.py`

### Frontend Light Mode & CORS Fix
- **Feature:** Redesigned the frontend with a clean light mode UI. Fixed CORS configuration to allow the Railway-hosted frontend to communicate with the backend.
- **Files:** `frontend/`, `backend/main.py`

### Excel Export — ETA Column & Container Type Header
- **Feature:** Added ETA column to the Excel export. Made the container type column header dynamic (e.g. "40GP (USD)") based on the actual search parameters.
- **Files:** `frontend/src/components/ResultsTable.tsx`

---

## [2026-05-18 – 2026-05-19] — Railway Deployment & Docker

### Railway Deployment Setup
- **Feature:** Dockerized the backend with Playwright, Chromium, and all dependencies. Configured supervisord to manage the FastAPI server and noVNC display server. Set up nginx as a reverse proxy.
- **Files:** `backend/Dockerfile`, `backend/supervisord.conf`, `backend/nginx.conf`

### Persistent Chrome Profiles on Railway Volume
- **Feature:** Chrome profiles are stored on a Railway persistent volume so carrier login sessions and cookies survive redeployments. The `PERSISTENT_PROFILES_DIR` environment variable controls the storage path.
- **Files:** `backend/carriers/maersk_connector.py`, `backend/carriers/cma_connector.py`

---

## Architecture Overview

### Search Flow
```
User (Frontend) → POST /api/rate-search → Backend creates DB records
                                         → Spawns background tasks per carrier
                                         → Each carrier: Login → Search → Extract → Normalize → Save
User polls GET /api/rate-search/{id}    ← Returns results as carriers complete
User clicks "Export Excel"              → Frontend generates .xlsx from API data
```

### Carrier Connector Lifecycle
```
1. Clone master Chrome profile → temp profile
2. Launch Chromium with temp profile on isolated VNC display
3. Login (or reuse session from cookies)
4. Fill search form → Submit
5. Wait for results → Extract quote cards
6. For each card:
   a. Extract ETD, ETA, transit time, vessel, routing
   b. Click "Details" → Extract charge breakdown
   c. Click "D&D" tab → Extract free time (CMA CGM)
   d. Normalize charges → Calculate final freight value
7. Save all quotes to database
8. Sync temp profile back to master (preserving session)
9. Delete temp profile + clean cache directories
```

### Charge Classification Rules
```
INCLUDED in Final Freight Value:
  - Basic Ocean Freight (BOF)
  - Freight Surcharges (BAF, LSS, EBS, GRI, PSS, WRS, CAF, etc.)
  - Discounts (negative values)

EXCLUDED from Final Freight Value:
  - Origin charges (THC, handling, documentation, seal, VGM)
  - Destination charges (THC, delivery, handling)
  - Uncertain charges (ambiguous classification)
```
