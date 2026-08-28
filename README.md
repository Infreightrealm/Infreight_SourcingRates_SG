# 🚢 Infreight Sourcing & Ocean Rate Automation System

An enterprise-grade, multi-carrier ocean freight rate intelligence and sourcing platform. The system automates real-time rate extraction across major global container shipping lines, itemizes complex price breakdowns, dynamically classifies freight surcharges vs. local origin/destination fees, and renders pixel-perfect side-by-side container comparison matrices with standardized Excel export capabilities.

---

## 🌟 Key Capabilities

### 1. Multi-Carrier Automation Engine
* **Real-time Live Sourcing**: Autonomous Playwright crawlers for major ocean container lines:
  - **Maersk Line**
  - **Hapag-Lloyd**
  - **CMA CGM**
  - **Ocean Network Express (ONE Line)**
  - **OOCL**
  - **MSC (Mediterranean Shipping Company)**
  - **GreenX / Evergreen**
* **Stealth & Session Resilience**: Chrome profile state persistence, shadow-DOM handling, dynamic XPath/CSS fallback strategies, anti-bot captcha management, and optional Bright Data Web Unlocker proxy routing.

### 2. Intelligent Surcharge & Charge Classifier Engine (`charge_classifier.py`)
Automatically normalizes raw charge descriptions into strict freight accounting categories:
* **`BASIC_OCEAN_FREIGHT`**: Base ocean freight rates.
* **`FREIGHT_SURCHARGE_INCLUDED`**: Included in total ocean freight:
  - Bunker Adjustment Factor (BAF) / Fuel Surcharges
  - Low Sulphur / Environmental Surcharges (LSS, EES)
  - Peak Season Surcharges (PSS)
  - Panama Canal Surcharges (PCS)
  - Emergency Operational Cost Recovery
  - Inland Haulage / Origin Landfreight Rail Surcharges
  - Transport Additional Surcharges
* **`ORIGIN_CHARGE_EXCLUDED` / `DESTINATION_CHARGE_EXCLUDED`**: Local port & administrative fees excluded from the total ocean rate:
  - Terminal Handling Charges (THC Origin / THC Dest)
  - Documentation / Bill of Lading Fees
  - Customs Clearance & Equipment Transfer Fees
  - Gate Reservation & Storage Fees
* **Dynamic Weight / VGM Thresholding**: Evaluates container weight against carrier weight tiers (e.g. 16,000 kg vs 20,000 kg) to automatically include or exclude Heavy Lift & Overweight Surcharges.

### 3. Container Comparison Matrix & Excel Export Engine
* **Multi-Container View**: Side-by-side container pricing (20GP, 40GP, 40HQ), transit times, free time, demurrage/detention, vessel/voyage details, and routing paths.
* **Pixel-Perfect Excel Exports**: Formatted using OpenPyXL and ExcelJS with custom styling (Arial 11, Official Blue `#323296`, Brand Orange `#FA8C3C` headers, Forest Green T/T, and bold red sold-out indicators).
* **Permanent Search History Archive**: Complete database audit log of all rate searches with user-selectable retrieval limits (100, 250, 500 records) and batch export support.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            NEXT.JS 14 FRONTEND                              │
│         (React, Tailwind CSS, Container Matrix, History & Export)           │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ REST API (JSON / HTTP)
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                             FASTAPI BACKEND                                 │
│          (Async REST Endpoints, Database ORM, Task Manager)                │
└───────────────┬──────────────────────┬──────────────────────┬───────────────┘
                │                      │                      │
┌───────────────▼──────────────┐ ┌─────▼────────────────────┐ ┌▼──────────────┐
│   PLAYWRIGHT CRAWLERS        │ │ CHARGE CLASSIFIER ENGINE │ │ SQL DATABASE │
│ (Maersk, Hapag, ONE, CMA, etc│ │ (Surcharge Categorization│ │ (SQLite /    │
│  Stealth Profiles & Captcha) │ │  & Weight Thresholding)  │ │  PostgreSQL) │
└──────────────────────────────┘ └──────────────────────────┘ └──────────────┘
```

---

## 🛠️ Project Structure

```
Infreight_Sourcing_New/
├── backend/
│   ├── api/                      # FastAPI API routes & endpoints
│   │   ├── rate_search_routes.py # Rate search & history endpoints
│   │   └── export_routes.py      # Excel export endpoints
│   ├── carriers/                 # Playwright carrier connectors
│   │   ├── maersk_connector.py   # Maersk automation
│   │   ├── hapag_lloyd_connector.py # Hapag-Lloyd automation
│   │   ├── cma_cgm_connector.py  # CMA CGM automation
│   │   ├── one_connector.py      # ONE Line automation
│   │   └── oocl_connector.py     # OOCL automation
│   ├── services/                 # Core domain & intelligence services
│   │   ├── charge_classifier.py  # Surcharge classification engine
│   │   └── normalizer.py         # Rate normalization service
│   ├── models/                   # Pydantic schemas & database models
│   ├── tests/                    # Backend Pytest automated test suite
│   ├── .env.example              # Environment configuration template
│   └── requirements.txt          # Python dependencies manifest
├── frontend/
│   ├── src/
│   │   ├── components/           # React UI components
│   │   │   ├── ResultsTable.tsx  # Container rate comparison matrix
│   │   │   ├── SearchForm.tsx    # Multi-route search input form
│   │   │   └── SearchHistoryModal.tsx # Search history modal & selector
│   │   ├── lib/                  # Frontend utilities & API client
│   │   │   ├── excelExport.ts    # Excel workbook matrix generator
│   │   │   └── api.ts            # Axios backend API client
│   └── package.json              # Node.js dependencies manifest
└── README.md                     # Platform documentation
```

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python**: `3.11` or `3.12`
- **Node.js**: `v18.x` or higher
- **Browser**: Google Chrome installed locally

---

### Step 1: Backend Setup

```bash
# 1. Navigate to backend directory
cd backend

# 2. Create and activate a Python virtual environment
python -m venv .venv

# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Install Playwright browser binaries
playwright install chromium

# 5. Create your local environment configuration file
cp .env.example .env

# Edit .env with your carrier portal credentials and database settings

# 6. Start the FastAPI backend server
uvicorn main:app --port 8000 --reload
```

---

### Step 2: Frontend Setup

```bash
# 1. Open a new terminal and navigate to frontend directory
cd frontend

# 2. Install Node.js dependencies
npm install

# 3. Start Next.js development server
npm run dev
```

Access the application UI in your browser at: **`http://localhost:3000`**

---

## 🧪 Running Automated Tests

```bash
# Backend Test Suite (Charge Classifier, Panama Canal Surcharge, Storage Cleanup)
cd backend
pytest tests/

# Frontend TypeScript Type Verification
cd frontend
npx tsc --noEmit
```

---

## 📄 License & Confidentiality

Internal Proprietary Sourcing & Automation System — All Rights Reserved.
