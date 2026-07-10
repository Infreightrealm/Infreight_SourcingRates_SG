# Infreight Ocean Carrier Rate Automation — Development Log
**Period Covered**: 26 June 2026 – 10 July 2026

This log documents all feature additions, anti-bot bypass integrations, database schema fixes, and server deployment updates completed during this period.

---

## 🚀 Key Highlights & Architectural Changes

1. **Self-Hosted Laptop Worker Setup**: Exchanged the unstable Railway backend environment for a 24/7 local laptop worker, routing incoming traffic via a secure, free ngrok tunnel.
2. **Date Standardization**: Unified all date formats to `DD Mon YYYY` (e.g. `16 Jul 2026`) across the frontend table and Excel exports, preventing line-breaks in the UI.
3. **Container Size Filtering**: Added interactive frontend filter buttons allowing users to filter search results by container type (`20GP`, `40GP`, `40HQ`, `All`).
4. **Queue Latency Reduction**: Replaced backend queue polling with an event-driven `asyncio.Condition` notifier, reducing queue handoff latency to **0ms**.

---

## 🛠 Detailed Carrier Log

### 🟠 Hapag-Lloyd
* **Anti-Bot & Turnstile Clear**: Added passive detection and real mouse-click simulation on Turnstile checkbox widgets, minimizing manual VNC intervention.
* **Pricing & Schedule Pairing**: Streamlined the schedules and quotes matching code into a unified loop that discards unmatched schedules, sold-out departures, and dates beyond a hard 2-week window.
* **Crawl Redirect Recoveries**: Solved a token expiration redirect bug that caused locodes to be mistyped into the email login fields.
* **Storage Optimization**: Prevented heavy temporary Chromium caches (`CacheStorage`, `DawnCache`) from copying back to master profiles, removing the primary source of volume bloat.

### 🔴 OOCL (FreightSmart)
* **Pricing Integration**: Upgraded the schedules-only connector to perform a full OOCL FreightSmart login and calendar day-by-day click loop to extract active quotes.
* **Cheapest E-Spot Selection**: Configured the E-Spot extraction to keep only the single cheapest E-Spot row per ETD.
* **Isolation Safeguards**: Prevented E-Spots from inheriting details from crawled schedules, and isolated E-Quotes from pairing with sold-out E-Spot vessels.
* **Typing Lock**: Introduced a shared lock that prevents background popup watchers from interrupting or corrupting the autocomplete port typing fields.

### 💗 ONE (Ocean Network Express)
* **Vertical Line-Rate Parsing Fix**: Corrected a parser bug that triple-counted and inflated final quote values. It now maps line-by-line container tokens and ignores redundant right-aligned totals.
* **Sold-Out Exclusions**: Excluded "Notify Me" and "Sold Out" cards from ONE crawls.
* **India Free Time Update**: Corrected the ONE India import free time configuration from 5 to 7 days.

### 🟢 GreenX
* **Surcharge Whitelist Expansion**: Configured the parser to recognize container-level charges (like **EUIS** and **ISOCC**) and fold them correctly into the final value.
* ** Nhava Sheva Free Time**: Fixed a parser fallback where Nhava Sheva (Usage only) returned blank instead of 5 days free time.

### 🔵 Maersk
* **Price-Owner Radio Selection**: Replaced the flaky label-click selector with a shadow-DOM-piercing JavaScript pass that locates and directly clicks the price-owner radio input.
* **Cache Key Reversion**: Reverted Maersk caching to be route-scoped rather than container-scoped, preventing Maersk from running 3 separate redundant crawls in multi-container searches.
* **Sold-Out Cap Skipping**: Prevented unpriced or sold-out cards from consuming slots in Maersk’s 10-quote crawl limit.

---

## 🔌 Local Laptop Deployment (Self-Hosted Worker)

### Window 1: Tunnel Setup
We created a permanent free dev domain on ngrok. The tunnel is started with:
```cmd
ngrok http --url=sloppily-payment-petition.ngrok-free.dev 8000
```
*To bypass the ngrok interstitial warning page, we injected `"ngrok-skip-browser-warning": "true"` headers across the frontend API client.*

### Window 2: Server Startup
We configured the server to run locally on Windows, bypassing the Windows-specific event loop issue (`ProactorEventLoop`) during Playwright execution:
```cmd
cd "C:\Users\Wei Kiat\Downloads\infreight_project\backend"
..\.venv\Scripts\python run_server.py
```
*We wrapped the backend runner in a `finally` block to call `connector.close()`, ensuring browser windows close automatically.*

### Windows Sleep Override
We used the Windows Command Prompt to disable sleep and suspend when plugged in, allowing the laptop to run 24/7 with the lid closed:
```cmd
powercfg /change standby-timeout-ac 0
powercfg /setacvalueindex SCHEME_CURRENT SUB_BUTTONS LIDACTION 0
powercfg /setactive SCHEME_CURRENT
```
