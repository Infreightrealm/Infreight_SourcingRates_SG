# Infreight Ocean Carrier Rate Automation

Internal web-based system for Infreight Logistics employees to search, compare, and analyze ocean freight quotations across multiple carriers.

## Features

- **Multi-carrier rate search** — Search Maersk, ONE, and 7 more carriers simultaneously
- **Automated portal scraping** — Playwright-based automation for carrier portal login and quote extraction
- **Charge classification** — Automatic categorization of charges (ocean freight, surcharges, excluded local charges)
- **Final freight value calculation** — BOF + Discount + Freight Surcharges only
- **Normalized comparison table** — Side-by-side comparison across all carriers
- **Mock mode** — Test locally without real carrier portal access

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15 (App Router) + Tailwind CSS |
| Backend | Python FastAPI |
| Automation | Playwright Python |
| Database | PostgreSQL (Railway) |
| Deployment | Railway + Docker |

## Quick Start (Local Development)

### Prerequisites

- Node.js 18+
- Python 3.12+
- PostgreSQL (or use Docker)

### 1. Start PostgreSQL

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
# Edit .env with your database URL

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

## Mock Mode

Mock mode is **enabled by default** for local development.

```env
# backend/.env
USE_MOCK_CARRIERS=true   # Mock mode (default)
USE_MOCK_CARRIERS=false  # Live mode — uses real carrier portals
```

When mock mode is enabled:
- No real carrier portal login happens
- Realistic sample Maersk and ONE quote data is returned
- Data passes through the same normalizer/classifier pipeline
- Other carriers return `CONNECTOR_NOT_AVAILABLE`

## Live Mode

To enable live carrier portal automation:

1. Set `USE_MOCK_CARRIERS=false` in your `.env`
2. Set carrier credentials:
   ```env
   MAERSK_USERNAME=your_username
   MAERSK_PASSWORD=your_password
   ONE_USERNAME=your_username
   ONE_PASSWORD=your_password
   ```
3. Restart the backend

## Railway Deployment

### 1. Create a Railway Project

1. Go to [railway.app](https://railway.app)
2. Create a new project
3. Add a PostgreSQL database service
4. Add a new service from your Git repo (backend)
5. Add a new service from your Git repo (frontend)

### 2. Set Environment Variables

In Railway, set these variables for the **backend** service:

```
DATABASE_URL          → Provided by Railway PostgreSQL plugin
USE_MOCK_CARRIERS     → false (for live mode)
FRONTEND_URL          → Your frontend Railway URL
MAERSK_USERNAME       → Your Maersk portal username
MAERSK_PASSWORD       → Your Maersk portal password
ONE_USERNAME          → Your ONE portal username
ONE_PASSWORD          → Your ONE portal password
```

For the **frontend** service:

```
NEXT_PUBLIC_API_URL   → Your backend Railway URL
```

### 3. Deploy

Railway will auto-deploy from your Git repo using the Dockerfiles.

## Project Structure

```
├── backend/
│   ├── main.py                    # FastAPI application
│   ├── Dockerfile                 # Railway-ready with Playwright
│   ├── api/
│   │   └── rate_search_routes.py  # API endpoints
│   ├── models/
│   │   ├── database.py            # SQLAlchemy async setup
│   │   ├── schemas.py             # Pydantic models
│   │   ├── rate_search.py         # Search & carrier result models
│   │   └── quote.py               # Quote & charge models
│   ├── services/
│   │   ├── charge_classifier.py   # Rule-based charge classification
│   │   ├── normalizer.py          # Final freight value calculation
│   │   └── job_service.py         # Search job orchestration
│   ├── carriers/
│   │   ├── base_connector.py      # Abstract base connector
│   │   ├── mock_connector.py      # Mock data for testing
│   │   ├── registry.py            # Connector factory
│   │   ├── maersk_connector.py    # Live Maersk automation
│   │   ├── one_connector.py       # Live ONE automation
│   │   └── ...                    # Stub connectors
│   └── tests/
├── frontend/
│   └── src/
│       ├── app/page.tsx           # Main search page
│       ├── components/            # React components
│       └── lib/                   # API client & types
└── docker/
    └── docker-compose.yml         # Local dev stack
```

## Adding a New Carrier Connector

1. Create `backend/carriers/your_carrier_connector.py`
2. Inherit from `BaseCarrierConnector`
3. Implement all abstract methods (login, search, extract, normalize)
4. Register in `backend/carriers/registry.py`
5. Add credentials to `.env.example`

## Final Freight Value Calculation

```
Final Freight Value =
    Basic Ocean Freight
    + Discount (normalized to negative)
    + Freight Surcharges (fuel, bunker, environmental, peak season, war risk, etc.)

EXCLUDED:
    - Origin charges (THC, handling, documentation)
    - Destination charges (THC, handling, delivery)
    - Uncertain charges (classified separately)
```

## Security

> ⚠️ **NEVER commit credentials to Git.**

- All carrier credentials are stored as environment variables only
- Use Railway environment variables for production
- Use `.env` file for local development (`.gitignore`'d)
- The `.env.example` file contains placeholders only

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/rate-search` | Create a new rate search |
| `GET` | `/api/rate-search/{search_id}` | Get search status and results |
| `GET` | `/health` | Health check |

## Supported Carriers

| Carrier | Status |
|---------|--------|
| Maersk | ✅ Mock + Live connector |
| ONE | ✅ Mock + Live connector |
| CMA CGM | ⏳ Stub (NOT_AVAILABLE) |
| Hapag-Lloyd | ⏳ Stub (NOT_AVAILABLE) |
| MSC | ⏳ Stub (NOT_AVAILABLE) |
| Evergreen | ⏳ Stub (NOT_AVAILABLE) |
| COSCO | ⏳ Stub (NOT_AVAILABLE) |
| OOCL | ⏳ Stub (NOT_AVAILABLE) |
| HMM | ⏳ Stub (NOT_AVAILABLE) |
