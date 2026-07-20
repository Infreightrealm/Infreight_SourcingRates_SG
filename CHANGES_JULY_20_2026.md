# Summary of Changes — July 20, 2026

Complete record of all features, fixes, and optimizations implemented today across the Infreight Ocean & Air Rate Automation platform.

---

## 1. AI RFQ Front Door & Air Freight Support (Phase A)
- **Air vs Sea Mode Classification**:
  - Classifies incoming RFQ emails or inquiries into `AIR` vs `SEA` mode based on keyword signals (`"air rate"`, `"airfreight"`, `"flight schedule"`, `"EXW airfreight"`, airport codes vs `"ocean"`, `"sailing"`, `"20'"/40'"`, `"Pasir Gudang"`).
  - Returns `mode: "air" | "sea"`, confidence score, and matched keyword signals.
- **Dual Partner Air Draft Emails**:
  - For ANY Air RFQ, the system automatically generates **TWO competing draft emails** with identical shipment specifications:
    1. **AWOT Global Logistics** (Contact: **Glenn**) — `glenn@awotglobal.com`
    2. **ASPAC International Logistics** (Contact: **Jing Hui**) — `jinghui@aspac.com`
- **Dangerous Goods & Compliance Preservation**:
  - Preserves hazardous cargo notes and customs codes without flattening (e.g. `LITHIUM METAL BATTERIES IN COMPLIANCE WITH SECTION II OF PI 970`, `HS CODE: 84433100`).
- **No Automatic Sending / No Carrier Scrape**:
  - Air RFQs do **NOT** trigger ocean carrier scraping. Draft emails are rendered side-by-side in the UI with **"📋 Copy Draft Email"** buttons for human review.

---

## 2. Multi-Origin & Gappy List Parsing for Sea RFQs (Phase B)
- **Multi-Origin Expansion**:
  - Parses multiple origin ports (e.g. `ex Pasir Gudang / Tanjung Pelepas` -> `["Pasir Gudang", "Tanjung Pelepas"]`).
- **Gappy List Parsing**:
  - Numbered destination lists with skipped items (e.g. 1, 2, 4, 5... skipping #3 in Image 4) strictly parse existing destinations without hallucinating missing numbers (2 origins × 17 destinations = **34 expanded pairs**).
- **Explicit UI Omission Counter**:
  - Search execution is capped at 10 pairs to protect carrier rate-limiting. The UI explicitly displays:
    > **"Showing 10 of 34 expanded pairs (24 pairs omitted due to search cap)"**

---

## 3. Search Form Streamlining (Form Input Restrictions)
- **Removed Departure Date Field**: Automatically defaults to `tomorrow` (or earliest carrier schedule).
- **Removed Commodity Field**: Automatically defaults to `Furniture` (accepted universally by all 7 ocean carriers).
- **Removed Container Quantity Field**: Automatically defaults to `1`.
- **Streamlined UI Layout**: Focuses cleanly on Carriers, Origin & Destination Autocomplete, Container Types (20GP, 40GP, 40HQ), and Weight per Container (KG).

---

## 4. Native Gemini 2.5 Flash API & Chatbot Resiliency
- **Direct HTTP API Endpoint**: Standardized `rfq_agent.py` and `chat_service.py` to use `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent` with raw unmodified `GEMINI_API_KEY` and header/query fallbacks.
- **Chatbot Resiliency**: Upgraded `chat_service.py` with multi-header authentication and intelligent fallback responder for search status, carrier guidance, VNC/CAPTCHA troubleshooting, and Air/Sea automation help.

---

## 5. Verification & Test Suite
- **Automated Pytest Suite**: All 4 real RFQ email test cases pass under pytest (`pytest backend/tests/test_rfq_agent.py` -> 4 passed in 0.69s).
- **Frontend Build Verification**: Ran `npm run build` — compiled successfully with zero TypeScript or JSX syntax errors.
