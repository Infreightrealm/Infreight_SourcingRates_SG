# Changelog

All notable changes to the Infreight Ocean Carrier Rate Automation system are documented here.  
Entries are grouped by date and by carrier/component. Each entry describes the problem (bug), the root cause, and the fix applied.

---

## [2026-07-02] — Latency Refactor: Hapag Throttles/Inputs, Event-Driven Queue, Scheduler Tuning

### Hapag-Lloyd — Configurable Pacing & Redundant-Wait Removal
- **Governor factor:** All `_human_delay(min,max)` pacing is now scaled by `HAPAG_GOVERNOR_FACTOR` (default **1.0** = unchanged behavior, clamped 0.2–3.0). Lower it to run faster in trusted/low-latency environments; raise it if challenge rates climb. Defaults were deliberately NOT lowered — the pacing is anti-detection and Hapag is the most challenge-prone carrier.
- **Interaction throttle:** browser `slow_mo` can be overridden via `HAPAG_INTERACTION_DELAY` (ms). Default remains the randomized 80–150ms anti-detection jitter.
- **Removed redundant blind waits:** the three long post-action sleeps — after the New Quote sub-menu click (3–5s), after the schedule search submit (4–6s), and after the quote form submit (5–8s) — are each immediately followed by active element-detection loops (180s settle / 45s selector wait / 180s results poll), so they were pure added latency. Reduced to a short 1.5–2.5s settle (also governor-scaled). Saves ~8–14s per search cycle with no loss of robustness.
- **Direct field population:** container quantity and cargo weight (plain number inputs, no autocomplete) now use a single `fill()` instead of click+Ctrl-A+Backspace+fill+char-by-char typing. Location fields intentionally KEEP char-by-char typing (the autocomplete dropdown requires keystroke events), but their 3-step clears are unified to a single `fill("")`. Login fields untouched (most challenge-sensitive flow).
- **`HAPAG_QUERY_SCHEDULES` (default `true`):** set to `false` to skip the schedule crawl entirely and fetch only the pricing matrix — minutes faster; quotes fall back to the default vessel naming.
- **Orphan profile sweep:** on launch, stale `chrome_profile_hapag_tmp_*` dirs older than 6h (crash leftovers) are deleted. Normal-exit cleanup already existed in `close()`.
- **Already in place (no change needed):** onboarding-dismissal caching (`_onboarding_dismissed` + 2.5s debounce), delta-based calendar navigation in `open_price_breakdown` (arrow-clicks toward `target_idx`, no reset-to-start), and multi-container single-crawl caching in `run_full_search`.
- **Files:** `backend/carriers/hapag_lloyd_connector.py`

### Queue Manager — Event-Driven Handoff (no more 2s polling)
- Replaced the 2-second polling loop in `enqueue_and_wait` with an `asyncio.Condition` bound to the existing lock; `release_lock`, `auto_release_check`, and `force_clear_all` now `notify_all()` so the next queued search starts the instant the slot frees. Measured handoff: **~0ms** (previously up to 2000ms per transition). Cancellation and force-clear semantics verified unchanged.
- **Files:** `backend/services/queue_manager.py`

### Job Scheduler — Concurrency Default
- `CARRIER_MAX_CONCURRENCY` default raised 2 → **3** (7 Xvfb displays exist; the practical ceiling is host RAM/CPU per Chrome instance). Still env-tunable — raise toward 7 only with host headroom, watching memory and challenge rates. Integrated multi-container querying was already implemented (each connector crawls all sizes once and serves later cycles from cache).
- **Files:** `backend/services/job_service.py`

---

## [2026-06-30] — ONE Multi-Container & Sold-Out, GreenX Surcharge Intake, Free-Time Fixes, Maersk Diagnosis

### Free Time — GreenX blank, ONE India wrong, Hapag Nhava Sheva unresolved (Singapore → Nhava Sheva)
- **GreenX — destination free time came back blank.** `open_price_breakdown` only matched `Container Detention` in the "Tariff Free Time at Destination" section, but the Nhava Sheva terminal (GATEWAY TERMINALS INDIA / GTI) labels it **`Container Usage`** (5 days). New rule: prefer `Container Detention` when the terminal lists it; otherwise fall back to the **combined** (summed) days of the other components shown (`Usage`/`Demurrage`/`Storage`/`Combined`). Nhava Sheva (Usage only) → 5; a terminal listing Detention 7 + Demurrage 3 → 7 (detention preferred). *File: `backend/carriers/greenx_connector.py`.*
- **ONE — India free time was 5, should be 7.** `one_freetime.json` values are genuine per-country figures (TW=3, CN=7, KR=10, …), so the `IN: 5` entry was simply wrong. Corrected India to **7** across all origin continents (import free time to India is origin-independent in this dataset). *File: `backend/data/one_freetime.json`.*
- **Hapag — Nhava Sheva didn't map to the logged `India` entry.** India *is* in `hapag_freetime.json` (4 days), and `INNSA → IN → India` exists in `port_codes.json`/`country_map.json`, but `_apply_freetime_to_quote` only matched by port-name substring — so `"Nhava Sheva (INNSA) [ZIP: …]"` or a bare locode never resolved. Added a locode fallback that picks the first 5-letter token which is a *known* port code (skipping "NHAVA" in favour of "INNSA"), maps it to its country name, and falls back to `resolve_port_for_carrier`. Nhava Sheva now resolves to India (4 days) for all destination forms. *File: `backend/carriers/hapag_lloyd_connector.py`.*



### ONE — All-Container-Type Search Returning 0 Quotes
- **Bug:** A combined 20GP / 40GP / 40HQ (`DRY 20` / `DRY 40` / `DRY 40H`) search logged in, found 12 quote cards, and parsed 65 charge lines per card, yet the frontend showed **no quotes** for any container type (and the Excel export had no data). Logs showed `[ONE] Returning 0 quote(s)` for all three types.
- **Root Cause:** A prior rewrite of `extract_charge_breakdown` (commit `1cd3382`) switched to "column-aware horizontal" parsing, assuming ONE prints all three container prices on a single line and assigning the container `basis` by column index. ONE actually renders **one container's amount per line**, each line carrying its own `DRY 20` / `DRY 40` / `DRY 40H` label. Every line therefore had a single amount, so each charge was tagged `basis=""` (flat). `_split_raw_quote_by_container_types` then found no container-specific charges, returned `[]`, and `run_full_search` fell back to a single untyped quote that the `container_type == request.container_type` filter discarded — yielding 0 quotes for every type. The rewrite had also dropped the per-line label extraction, which additionally overwrote charge names with "DRY 20"/etc.
- **Fix:** Detect each line's own `DRY 20` / `DRY 40` / `DRY 40H` label and use it as the charge `basis` for single-amount lines (ONE's real layout); keep the column-index assignment only for genuine multi-amount lines. Strip the container label out of the recovered charge name so the real name (e.g. "Basic Ocean Freight") is preserved. Verified with a reproduction of ONE's vertical breakdown layout: the split now yields 3 correct per-container quotes (was 0).
- **Files:** `backend/carriers/one_connector.py` (`extract_charge_breakdown`)

### ONE — Sold-Out ("Notify Me") Sailings Appearing as Quotes
- **Bug:** A sold-out sailing (Status "Sold Out", shown with a **"Notify Me"** button and no "Accept" button — e.g. FE1 / ONE ARCADIA 078W at USD 17,079.64) was being grabbed and returned as a quote even though it cannot be booked.
- **Root Cause:** `extract_quote_list` detected the sold-out state but only **relabeled** the card (appended "(Sold out)" to the vessel, set the status to "Sold Out", zeroed the price) and still appended it to the quote list. It also treated a missing/"---" vessel as sold-out, which risked dropping otherwise-valid cards.
- **Fix:** Made sold-out a **skip rule**: if a card contains "Notify Me" or a "Sold Out" status, it is excluded from the results entirely (`continue`) and never processed into a quote. Bookable cards (which display an "Accept" button) are unaffected. Narrowed the detection to the reliable "Notify Me" / "Sold Out" / status signals so a parse miss on the vessel field no longer drops a valid sailing.
- **Files:** `backend/carriers/one_connector.py` (`extract_quote_list`)

### ONE — Multi-Container Breakdown Triple-Counted / Inflated Final Value
- **Bug:** An all-container ONE search produced one massively inflated quote (e.g. BOF shown as USD 12,210 and every surcharge repeated ~3×, final USD 20,372) instead of three correct per-container quotes. Expected per container: BOF(size) + its surcharges (e.g. DRY 20 = 2,370 + 250 + 102 + 314 + 500 = 3,536; DRY 40 / DRY 40H = 5,512).
- **Root Cause:** ONE renders each container as a structured token — `DRY 20 x 1 (USD 2,370.00)` — followed by a right-aligned total that is just `qty × unit` repeated (on the same line or the next line). The parser (a) when both amounts were on one line, spread them across `column_order`, so one container's two identical amounts leaked into other columns, and (b) when the total sat on its own line, turned the bare `USD 2,370.00` into a **flat** charge, which `_split_raw_quote_by_container_types` then added to *every* container. Both paths triple-counted BOF and surcharges.
- **Fix:** Parse the structured token authoritatively — `amount = qty × unit`, assigned to the container named in the token — and **ignore the redundant right-aligned total** (a bare `USD ...` line with no container label is now skipped, never turned into a flat charge). This also cleanly handles the fully-horizontal layout (all three tokens on one line). Verified: DRY 20/40/40H come out as 3,536 / 5,512 / 5,512 with exactly five charges each and zero stray flat charges; earlier ONE split and sold-out tests still pass.
- **Files:** `backend/carriers/one_connector.py` (`extract_charge_breakdown`)

### GreenX — Only Basic Ocean Freight & LSS Folded Into Final Value
- **Bug:** GreenX quotes only added **Basic Ocean Freight** and **LOW SULPHUR SURCHARGE (LSS)** into the final freight value. Other mandatory surcharges — **EU INNOVATION SURCHARGE (EUIS)** and **IMO SOX COMPLIANCE CHARGE (ISOCC)** — were dropped, and the per-B/L **EU ENTRY SUMMARY DECLARATION CHARGE (ENS)** / **E BOOKING FEE VIA GREENX (EBKF)** were not reliably included.
- **Root Cause:** In `_split_raw_quote_by_container_types`, the surcharge whitelist (`INCLUDED_SURCHARGES`) was applied **only to flat / per-B/L charges**. Container-specific charges were hardcoded to `ORIGIN_CHARGE_EXCLUDED` unless the name was exactly "BASIC OCEAN FREIGHT". GreenX bills EUIS/ISOCC (and often LSS) **per container**, so they fell into the container bucket and were always excluded — only the per-B/L LSS line survived.
- **Fix:** Applied the whitelist to **both** container-specific and per-B/L charges via a single `_categorize(name, currency)` helper that also enforces a **USD-only** rule: a charge is folded into the final value only when its (whitespace-normalized) name is in the whitelist **and** its currency is USD. Per-B/L charges (ENS, EBKF) continue to be added in full to every container size (a $10 ENS adds $10 to each). Verified: each of DRY 20 / DRY 40 / DRY 40H now sums BOF + EUIS + ISOCC + LSS + ENS + EBKF, while a non-USD or non-whitelisted charge is excluded.
- **Files:** `backend/carriers/greenx_connector.py` (`_split_raw_quote_by_container_types`)

### Performance/Reliability — Stop Copying Chrome Caches During Profile Clone/Sync
- **Problem:** Hapag-Lloyd, Maersk and CMA each run in an isolated Chrome profile that is cloned from a master on launch and synced back on close. Both copies included the heavy throwaway Chrome caches (`Cache`, `Code Cache`, `DawnCache`, `GPUCache`, `CacheStorage`, `ScriptCache`). The sync step then deleted them again — so every run copied hundreds of MB of cache **just to delete it**, wasting launch/teardown I/O and feeding the multi-GB storage bloat the code already warned about.
- **Fix:** Pass `ignore=shutil.ignore_patterns(...cache dirs...)` to both the clone and sync `copytree` calls so the caches are never copied in either direction. Session identity (`Cookies`, `Local Storage`, `IndexedDB`) is still copied intact, so login sessions are preserved. A safety-net cleanup of stale cache dirs in master is retained for crash-leftover cases. Verified in isolation: session files are kept, all cache dirs are skipped.
- **Impact:** Faster, lower-I/O launch and teardown for the three slowest connectors (notably Hapag-Lloyd), and removal of the main storage-bloat source. No change to session/login behavior.
- **Files:** `backend/carriers/hapag_lloyd_connector.py`, `backend/carriers/maersk_connector.py`, `backend/carriers/cma_connector.py`

### Hapag-Lloyd — Best-Effort Automated CAPTCHA Clear + Per-Sailing Speedup
- **Goal:** Hapag-Lloyd is the slowest connector and the most likely to hit a Cloudflare/Turnstile challenge. Reduce both the manual-intervention rate and redundant per-sailing work, without dropping any sailings (the crawl still returns *all* dates).
- **Automated CAPTCHA clear (steps 1–2):** Before escalating to the existing manual VNC solve, `_wait_for_captcha_resolution` now first calls `_attempt_captcha_autoclear`: (1) waits a few seconds for a *passive* challenge to resolve itself (with the existing patchright stealth + residential proxy, Turnstile frequently auto-passes with no click), then (2) if an interactive Turnstile checkbox is present, clicks it once with human-like mouse motion via a **real** mouse click at the widget's bounding box (trusted input, which Cloudflare is far more likely to accept than a synthetic `.click()`). If neither clears the challenge, it falls through to the **unchanged** manual VNC wait — so this can only help, never hurt. This is best-effort: scripted clicks are not guaranteed against Cloudflare, and no third-party solving service is used.
- **Per-sailing speedup:** `_dismiss_hapag_modals` is invoked back-to-back at several points per sailing. After onboarding is dismissed, a **debounce** now skips the repeat modal-dismissal JS pass when the previous pass ran within 2.5s *and* found nothing — so redundant work is avoided while a genuinely new popup is never missed. Human-pacing delays were deliberately left intact, since trimming them would *increase* challenge risk.
- **Note:** The auto-clear path can only be exercised on a live challenge (a chance encounter), so it ships behind its safe manual fallback rather than being load-tested here. Proxy-session rotation on challenge (the higher-yield "step 3") was intentionally deferred pending a live watch.
- **Files:** `backend/carriers/hapag_lloyd_connector.py`

### MAERSK — "Quotes Found" but Empty Excel (Diagnosis)
- **Symptom:** A Singapore→Hamburg multi-container search showed quotes "found" mid-run but the Excel/result set was empty (`[JOB] MAERSK: NO_QUOTES_AVAILABLE — 0 quote(s)`), even though a valid bookable sailing existed.
- **Findings:** (1) Every processed card parsed at **0.0 USD** and was treated as sold-out/not-open, so the price-breakdown step was skipped and `raw_charges` was empty. (2) With no per-container charges, `_split_raw_quote_by_container_types` returns `[]`, so the code falls back to a single `normalize_result` quote — but the fallback `raw_quote` has **no `container_type`**, so it is `None`, and the per-container filter (`q.container_type == request.container_type`) discards all of them → 0 quotes. (3) Sold-out/not-open cards still count toward the **10-quote cap**, so the crawl can fill its quota with not-open sailings and stop before reaching the genuinely priced one. The likely upstream trigger is the **price-owner selection** clicking the radio's `label` (not the input), so prices never render. *Fix pending live verification of the price-owner step.*
- **Files (under investigation):** `backend/carriers/maersk_connector.py`

---

## [2026-06-12] — OOCL, MSC, ONE Inbound Free Time & Concurrency Queue Control

### ONE — Inbound Free Time Swap & Scraper Upgrade
- **Feature**: Refactored the ONE connector (`one_connector.py`) to query destination-based inbound demurrage/detention limits instead of outbound export limits. Maps the origin port's country to its continent and queries the cache via `freetime_cache[dest_country].get(origin_continent)`.
- **Scraper**: Rewrote `scrape_one_freetime.py` to crawl inbound demurrage/detention tariffs. Updated country matching in autocomplete to use exact string checks instead of first-index matching, resolving false selections (like selecting *"British Indian Ocean Territory"* for *"India"*).
- **Captcha Safeguard**: Integrated custom Geetest/Cargosmart CAPTCHA detection that automatically pauses the scraper for up to 90 seconds to allow manual solving on the VNC screen.
- **Cache Database**: Expanded `one_freetime.json` to include 19 core countries, Turkey, and 31 European destinations (including Germany, UK, France, Netherlands, Belgium, Italy, Spain, Sweden, Poland, and Ukraine).

### OOCL — Orient Overseas Container Line Connector Implementation
- **Feature**: Implemented the full OOCL schedules connector and VNC display mapping (Xvfb `:105`, VNC `5906`).
- **Parsing**: Developed selectors to extract direct/transshipment route parameters from the CargoSmart schedule grids.
- **Tarpit Evasion**: Configured a 90-second wait selector on grid elements and verified grid result counts dynamically to handle CargoSmart loading tarpits.

### MSC — Mediterranean Shipping Company Connector Implementation
- **Feature**: Developed the full MSC schedules and pricing connector and VNC display mapping (Xvfb `:104`, VNC `5904`).
- **Parsing**: Built a robust regex-splitting parser to parse individual charges from React single-string MuiGrid layouts.
- **Timeout Fix**: Added a two-phase check in the schedule wait loop to confirm the search content changed before testing row visibility, preventing the extractor from picking up stale data and finishing prematurely.

### Concurrency Limit Queue & Admin Control Panel
- **FIFO Queue System**: Added a global backend FIFO queue system and locked concurrent searches to a maximum of **3 slots**, prioritizing slower carriers.
- **Admin Dashboard**: Created a name-based login registry, session tracking system, LoginModal.tsx, and a "Force Stop" override feature to clear active queues.
- **Debug Screenshots**: Mounted a static `/screenshots` route to serve browser debug screens and validation logs directly from the backend.

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
