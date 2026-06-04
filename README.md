# Infreight Ocean Carrier Rate Automation

Internal web-based system for Infreight Logistics employees to search, compare, and analyze ocean freight quotations across multiple carriers simultaneously.

## Features

- **Multi-carrier rate search** — Search Maersk, CMA CGM, Hapag-Lloyd, ONE, and 5 more carriers simultaneously
- **Automated portal scraping** — Playwright-based stealth automation for carrier portal login and quote extraction
- **Concurrent multi-tab searches** — Run multiple searches on different browser tabs without conflicts (isolated temp profiles)
- **Charge classification** — Automatic categorization of charges (ocean freight, surcharges, excluded local charges)
- **Final freight value calculation** — BOF + Discount + Freight Surcharges only (excludes origin/destination charges)
- **Routing detection** — Automatic identification of Direct vs Transit routing with transshipment port names
- **Free time extraction** — Import detention/demurrage free time pulled from carrier D&D tabs
- **Normalized comparison table** — Side-by-side comparison across all carriers with sortable columns
- **Excel export** — One-click export to formatted `.xlsx` with POL, POD, Carrier, Rate, Transit Time, Free Time, ETD, ETA, Routing, and Remarks
- **Sold out visibility** — Carriers with no sailings are explicitly shown as "Sold out" in the Excel instead of being silently omitted
- **Human-in-the-loop 2FA** — noVNC browser viewer for manual CAPTCHA/2FA resolution when required by carriers
- **Persistent sessions** — Chrome profiles stored on Railway volume to preserve login sessions across deployments
- **Auto cache cleanup** — Chromium cache directories are automatically purged after each search to prevent storage bloat

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15 (App Router) + Tailwind CSS |
| Backend | Python FastAPI |
| Automation | Patchright (stealth Playwright fork) + Playwright |
| Proxy | Bright Data ISP/Residential proxies with sticky sessions |
| Database | PostgreSQL (Railway) / SQLite (local) |
| Deployment | Railway + Docker + supervisord + nginx |
| Display | Xvfb + noVNC for headless browser rendering |

## Supported Carriers

| Carrier | Status | Notes |
|---------|--------|-------|
| Maersk | ✅ Live | Shadow DOM piercing, Patchright stealth, 2FA via noVNC |
| CMA CGM | ✅ Live | Chrome session bypass, D&D free time extraction |
| Hapag-Lloyd | ✅ Live | Calendar grid pagination, transshipment detection |
| ONE | ✅ Live | Date picker automation, charge scoping |
| MSC | ⏳ Stub | Returns `CONNECTOR_NOT_AVAILABLE` |
| Evergreen | ⏳ Stub | Returns `CONNECTOR_NOT_AVAILABLE` |
| COSCO | ⏳ Stub | Returns `CONNECTOR_NOT_AVAILABLE` |
| OOCL | ⏳ Stub | Returns `CONNECTOR_NOT_AVAILABLE` |
| HMM | ⏳ Stub | Returns `CONNECTOR_NOT_AVAILABLE` |

## Quick Start (Local Development)

### Prerequisites

- Node.js 18+
- Python 3.12+
- PostgreSQL (or use Docker, or SQLite for local dev)

### 1. Start PostgreSQL (Optional)

```bash
# Using Docker
docker run -d --name infreight-db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=infreight \
  -p 5432:5432 \
  postgres:16-alpine
```

### 2. Backend Setup

```bash
cd backend

# Create .env from example
cp .env.example .env
# Edit .env with your credentials and database URL

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (for live mode)
playwright install chromium

# Start the API server
uvicorn main:app --reload --port 8000
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start dev server
npm run dev
```

### 4. Open the App

Visit: **http://localhost:3000**

## Configuration

### Environment Variables (Backend)

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host/db  # Omit for SQLite fallback

# Mode
USE_MOCK_CARRIERS=false  # true = mock data, false = live carrier portals

# Carrier Credentials
MAERSK_USERNAME=your_username
MAERSK_PASSWORD=your_password
ONE_USERNAME=your_username
ONE_PASSWORD=your_password
CMA_USERNAME=your_username
CMA_PASSWORD=your_password
HAPAG_USERNAME=your_username
HAPAG_PASSWORD=your_password

# Proxy (Bright Data)
PROXY_SERVER=your_proxy_server
PROXY_PORT=22225
MAERSK_PROXY_USER=your_proxy_user
MAERSK_PROXY_PASS=your_proxy_pass
CMA_PROXY_USER=your_proxy_user
CMA_PROXY_PASS=your_proxy_pass

# Browser Profiles
PERSISTENT_PROFILES_DIR=/data/chrome_profiles  # Railway volume path

# Display
RESET_CHROME_PROFILES=false  # Set to true to wipe all saved sessions on restart
```

### Environment Variables (Frontend)

```env
NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
```

## Railway Deployment

1. Create a Railway project with a PostgreSQL database service
2. Add backend service from Git repo (uses `backend/Dockerfile`)
3. Add frontend service from Git repo
4. Set environment variables as listed above
5. Add a persistent volume mounted at `/data` for Chrome profiles
6. Railway auto-deploys on every `git push`

## Project Structure

```
├── backend/
│   ├── main.py                    # FastAPI application entry
│   ├── Dockerfile                 # Railway-ready with Playwright + Xvfb + noVNC
│   ├── supervisord.conf           # Process manager for server + display
│   ├── nginx.conf                 # Reverse proxy config
│   ├── api/
│   │   ├── rate_search_routes.py  # Search create/get endpoints
│   │   └── port_routes.py         # Port lookup endpoint
│   ├── models/
│   │   ├── database.py            # SQLAlchemy async setup
│   │   ├── schemas.py             # Pydantic request/response models
│   │   ├── rate_search.py         # Search & carrier result DB models
│   │   └── quote.py               # Quote & charge DB models
│   ├── services/
│   │   ├── charge_classifier.py   # Rule-based charge classification
│   │   ├── normalizer.py          # Final freight value calculation
│   │   └── job_service.py         # Search job orchestration
│   ├── carriers/
│   │   ├── base_connector.py      # Abstract base connector
│   │   ├── registry.py            # Connector factory
│   │   ├── mock_connector.py      # Mock data for testing
│   │   ├── maersk_connector.py    # Maersk live automation
│   │   ├── cma_connector.py       # CMA CGM live automation
│   │   ├── hapag_lloyd_connector.py # Hapag-Lloyd live automation
│   │   └── one_connector.py       # ONE live automation
│   └── tests/
├── frontend/
│   └── src/
│       ├── app/page.tsx           # Main search page
│       ├── components/
│       │   └── ResultsTable.tsx   # Results table + Excel export
│       └── lib/
│           └── types.ts           # TypeScript type definitions
├── docker/
│   └── docker-compose.yml         # Local dev stack
├── CHANGELOG.md                   # Detailed bug/fix documentation
└── README.md                      # This file
```

## How It Works

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
1. Clone master Chrome profile → isolated temp profile
2. Launch Chromium on isolated VNC display (thread-safe)
3. Login (or reuse session from cookies)
4. Fill search form → Submit
5. Wait for results → Extract quote cards
6. For each card:
   a. Extract ETD, ETA, transit time, vessel, routing
   b. Click "Details" → Extract charge breakdown
   c. Click "D&D" tab → Extract free time (carrier-specific)
   d. Normalize charges → Calculate final freight value
7. Save all quotes + routing + free time to database
8. Sync temp profile back to master (preserving cookies/session)
9. Delete temp profile + purge cache directories
```

### Final Freight Value Calculation

```
Final Freight Value =
    Basic Ocean Freight (BOF)
    + Discount (normalized to negative)
    + Freight Surcharges (BAF, LSS, EBS, GRI, PSS, WRS, CAF, etc.)

EXCLUDED from final value:
    - Origin charges (THC, handling, documentation, seal, VGM)
    - Destination charges (THC, delivery, handling)
    - Uncertain charges (classified separately)
```

## Adding a New Carrier Connector

1. Create `backend/carriers/your_carrier_connector.py`
2. Inherit from `BaseCarrierConnector`
3. Implement all abstract methods: `login()`, `search_quotes()`, `extract_quote_list()`, `open_price_breakdown()`, `extract_charge_breakdown()`, `normalize_result()`
4. Register in `backend/carriers/registry.py`
5. Add credentials to `.env.example` and `.env`
6. Test with a real search before deploying

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/rate-search` | Create a new multi-carrier rate search |
| `GET` | `/api/rate-search/{search_id}` | Poll search status and results |
| `GET` | `/health` | Health check |

## Security

> ⚠️ **NEVER commit credentials to Git.**

- All carrier credentials are stored as environment variables only
- Use Railway environment variables for production
- Use `.env` file for local development (`.gitignore`'d)
- The `.env.example` file contains placeholders only
- Chrome profiles are excluded from Git via `.gitignore`

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a detailed history of all bugs, fixes, and features.
