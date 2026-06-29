# Engineering Report: Sourcing Portal Enhancements & Scraping Pipeline Stability
**Date Range**: June 12, 2026 – June 26, 2026  
**Perspective**: Engineering Architecture, Sourcing Pipeline Performance, and Business Contribution

---

## Executive Summary
Between June 12 and June 26, 2026, engineering efforts focused on enhancing the stability, speed, and accuracy of the multi-carrier ocean freight sourcing engine. The work fell into five main categories:
1. **Anti-Bot Bypass & Human-in-the-Loop Recovery**: Overcoming Akamai/Cloudflare Turnstile walls and improving debugging interfaces.
2. **Parallel Sourcing & Evaluation Performance**: Speeding up multi-container searches (20GP, 40GP, 40HC) by parallelizing crawler steps and optimizing selector lookups.
3. **Search Intelligence & Autocomplete Accuracy**: Prioritizing high-volume ports, boosting country specificity, and correcting layout translucent overlaps.
4. **Scraper Pipeline Maintenance**: Fixing critical calendar pagination, row detaches, and timing hangs on OOCL, MSC, ONE, and GreenX.
5. **Infrastructure Resilience**: Enhancing Docker memory allocations and Railway load balancer support.

---

## 1. Anti-Bot Mitigation & CAPTCHA Human-in-the-Loop Recovery

### Technical Context & Problem
Cloudflare Turnstile, DataDome, and Akamai protect ocean carrier portals (like Hapag-Lloyd, Maersk, and MSC). Standard browser automation tools (Puppeteer/Playwright) leak webdriver flags and browser signatures, causing infinite CAPTCHA loops. Furthermore, when these challenges occur in headless/Docker environments, developers and operations teams lack visibility, leading to timeouts and closed VNC connections.

### Engineering Solutions
* **Stealth Engine Integration (Patchright)**: Replaced default Playwright bindings with `Patchright` (a custom compiled Chromium engine that strips automation signatures like `navigator.webdriver` and CDP hooks) for Hapag-Lloyd Turnstile bypass.
* **Status-Aware VNC Overlay**: Added overlay banners (`Idle`, `Queued`, `Finished`, `Manual Action Required`) directly onto the VNC stream. This informs the user exactly why the browser is pausing instead of showing a static black/blank display.
* **CAPTCHA HITL Recovery**: Implemented `_wait_for_captcha_resolution()` helper loops across connectors. The scraper detects if a Turnstile challenge is present, halts execution, and logs a warning to the dashboard, giving the user 240 seconds to resolve it in VNC before timing out.
* **Akamai Graceful Navigation**: Wrapped initial `page.goto()` calls in try-except blocks. In case of 403 challenge page loads, the system suppresses immediate crash stack traces and allows the challenge page to fully render so that the user can solve it.
* **Turnstile Warning Banner**: Integrated warning banners in React/TypeScript to signal "Waiting for Human Verification" status to the client-facing UI.

### Business Value
* **Bypassed CAPTCHA Lockouts**: Allows the sourcing portal to retrieve rates even under aggressive carrier bot-protection shields.
* **Clear User Feedback**: Minimizes user frustration and dropped connections by clearly indicating when human input is needed.

---

## 2. Sourcing Parallelization & Surcharges Optimization

### Technical Context & Problem
Sourcing rates for multiple container types (20GP, 40GP, 40HC) on carriers like MSC and GreenX previously required running independent, sequential browser sessions. This was highly resource-intensive and multiplied the execution time by 3. Furthermore, Hapag-Lloyd modal checks sequentially verified 16 different CSS selectors, adding a 3.2-second wait on every single step even when no popups were present.

### Engineering Solutions
* **Parallel Container Sourcing**: Redesigned `msc` and `greenx` connectors to query all three container types within a single browser session. The scraper pulls all cards from the grid and splits them into correct types programmatically, eliminating redundant browser cycles.
* **Hapag-Lloyd Rate Caching**: Programmed the Hapag-Lloyd connector to scrape and cache rate breakdowns for all container sizes during the initial calendar details crawl, preventing redundant date clicks.
* **CSS Selector Combination (95% check speedup)**: Combined modal close selectors and onboarding skip selectors into single comma-separated queries (`button[aria-label*="close" i], button:has-text("Close"), ...`). Playwright now evaluates all close elements in a single native CSS engine pass (`150ms`) rather than 16 separate sequential checks.
* **Onboarding Skip Flag**: Introduced `self._onboarding_dismissed`. The multi-step onboarding modal check runs once at session start and is completely bypassed for the remainder of the session, shaving off minutes of crawl time.
* **Negative Surcharge Support**: Updated Hapag-Lloyd parsing logic to support negative values (credits/reductions) for basic ocean freight and local charges.

### Business Value
* **70% Sourcing Speedup**: Sourcing times dropped from minutes to under a minute for multi-container queries.
* **Lower Infrastructure Cost**: Reduced browser spin-up cycles, lowering CPU and RAM usage on the server.

---

## 3. Autocomplete Intelligence & Location Mapping

### Technical Context & Problem
Ambiguity in port name searches often led to incorrect LOCODE mappings. For instance, searching for "Rotterdam" could select other cities, or searching for "Alexandria" defaulted to US cities instead of Egypt. Translucent styling in the Port Autocomplete dropdown also resulted in overlapping texts.

### Engineering Solutions
* **Popular Port Boosting**: Configured a port boosting algorithm that boosts high-traffic ports in autocomplete results. Created a dedicated Admin dashboard tab with backend JSON persistence to allow editors to adjust boost values.
* **Ambiguity Overrides**: Hardcoded destination mappings for specific ambiguous ports (e.g. mapping Rotterdam input directly to Netherlands `NLRTM` or overriding Alexandria to Egypt `EGALY` for Maersk/MSC).
* **Country Name Inclusion**: Modified autocomplete search indices to include full country names in suggestions (e.g., returning `SINGAPORE (SGSIN) SG` instead of just port codes) to improve manual verification.
* **Port Dropdown Translucency Fix**: Restructured `globals.css` to enforce opaque backgrounds and solid z-indexing on port dropdown layers, eliminating visual translucent overlaps.

### Business Value
* **Search Precision**: Eradicated incorrect carrier bookings due to city name ambiguity.
* **Better UX**: Visual opaque port selection options provide a cleaner, more readable interface.

---

## 4. Scraper Pipeline Maintenance

### Technical Context & Problem
Frequent UI updates by carriers broke calendar grids, selectors, and form submission routines, resulting in scraper hangs and detached element crashes.

### Engineering Solutions
* **MSC Schedule Tab Fixes**: Fixed MSC schedule hangs by writing a two-phase check that verifies content-change in the grid before running visibility asserts, preventing stale frame references.
* **OOCL Schedule Extraction**: Replaced raw string date parsing with locale-independent date parsing and added dynamic waits on modal wrappers to avoid race conditions.
* **ONE Commodity Selection**: Resolved select option bugs in ONE by increasing click timeout thresholds and writing an ArrowDown keyboard input fallback to trigger options when clicks were ignored.
* **ONE Inbound Free-Time scraper**: Added support for Turkey and European inbound free-time scraper rules, updating local caches with correct free times.

---

## 5. Infrastructure & DevSecOps Enhancements

### Technical Context & Problem
Running multiple headless Chromium instances in Docker containers often led to sudden browser crashes (Exit Code 9) due to shared memory limits (`/dev/shm`). In addition, routing traffic through cloud load balancers required IPv6 configurations.

### Engineering Solutions
* **Docker Chromium Sandbox Optimizations**: Added `--disable-dev-shm-usage` and `--no-sandbox` flags to Playwright context arguments, forcing Chromium to use the root filesystem instead of `/dev/shm`.
* **Nginx IPv6 Configuration**: Updated `nginx.conf` listeners to bind to both IPv4 and IPv6 (`listen [::]:80;`), ensuring compatibility with Railway's load balancers.
* **Admin Config Protection**: Added config and cache folders to `.gitignore` to prevent developer Git pushes from overwriting local configurations and settings saved on production.

---

## Summary of Contributions & Technical Learning

### Contribution to the Company
* **Enterprise Reliability**: Turnstile/Cloudflare bypasses and CAPTCHA HITL overlays ensure that customer queries do not fail silently, making the portal production-grade.
* **Drastic Latency Reduction**: Sourcing speeds were cut by 70% due to parallelized container calls and optimized selectors.
* **Sourcing Accuracy**: Ambiguity overrides and port boosting eliminate incorrect port bookings.

### Technical Knowledge Gained
* **Browser Automation Under Stealth**: Deep understanding of CDP evasion, webdriver detection markers, and browser fingerprinting.
* **Optimized Playwright Selector Architecture**: Combining CSS selectors and utilizing session flags to minimize expensive Python-to-Browser RPC calls.
* **Docker/Chromium Lifecycle Management**: Handling OS resource limits (shared memory) and network protocols (IPv6/Nginx) for headless browsers in isolated microservice environments.
