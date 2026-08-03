# Infreight Ocean Carrier Rate Automation

Internal web-based system for Infreight Logistics employees to search, compare, and analyze ocean freight quotations across multiple ocean carriers simultaneously.

---

## Key Features

- **Multi-Carrier Live Rate Search** — Search Maersk, CMA CGM, Hapag-Lloyd, ONE, OOCL, GreenX (Evergreen), and MSC simultaneously.
- **Stealth Browser Automation** — Playwright & Patchright automation for carrier portal logins, automated date-strip scanning, and quote extraction.
- **OOCL FreightSmart Multi-Month Calendar Scraper** — Dual-panel date extraction handling both E-Quote and E-Spot pricing side-by-side.
- **Railway Cloud WebSocket Tunnel Relay** — Seamless 1-click tunnel (`run_tunnel_client.bat`) connecting Railway Cloud frontend to your local residential IP machine, bypassing DataDome and Cloudflare anti-bot CAPTCHAs with zero cost and zero time limits.
- **Dynamic Backend Server Switcher & Auto-Recovery** — Automatic failover to Cloud Backup if local server drops, and seamless auto-recovery back to Local/Tunnel when online.
- **Admin Port Code & City Registry** — Admin interface (`/admin`) to register, amend, or boost UN/LOCODEs, custom city names, and carrier-specific port overrides.
- **Smart City Synonym Matching** — Built-in synonym engine matching port aliases (`Kochi` $\leftrightarrow$ `Cochin`, `Nhava Sheva` $\leftrightarrow$ `Jawaharlal Nehru`, `Haiphong` $\leftrightarrow$ `Hai Phong`, `Ho Chi Minh` $\leftrightarrow$ `Sai Gon`).
- **Charge Classification & Value Normalization** — Automatic separation of ocean freight, surcharges, and local fees to calculate true final freight cost.
- **Formatted Excel Export** — Brand-styled `.xlsx` exports with official color palette (`#323296`, `#FA8C3C`), sortable columns, and explicit "Sold Out" visibility.
- **Human-in-the-Loop (HITL) 2FA** — Integrated noVNC viewer for manual 2FA/CAPTCHA resolution when required by carriers.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js 15 (App Router) + Tailwind CSS + Lucide Icons + Sonner Toasts |
| **Backend** | Python FastAPI + Uvicorn |
| **Automation** | Patchright (Stealth Playwright fork) + Real Google Chrome Stable |
| **Tunnel Relay** | Railway WebSocket Tunnel Relay (`scripts/tunnel_relay` + `run_tunnel_client.bat`) |
| **Database** | PostgreSQL (Production) / SQLite (Local) |
| **Deployment** | Railway + Docker + Supervisord |

---

## Supported Carriers

| Carrier | Status | Automation Method & Capabilities |
|---------|--------|----------------------------------|
| **Maersk** | ✅ Live | Shadow DOM piercing, Patchright stealth, 2FA via noVNC |
| **CMA CGM** | ✅ Live | Chrome session preservation, D&D free time extraction |
| **Hapag-Lloyd** | ✅ Live | Calendar grid pagination, transshipment detection |
| **ONE** | ✅ Live | Date picker automation, container charge scoping |
| **OOCL** | ✅ Live | FreightSmart E-Quote & E-Spot calendar scraper, side-by-side date matrix |
| **GreenX (Evergreen)** | ✅ Live | Accordion fee breakdown parser, free time extraction |
| **MSC** | ✅ Live | Form automation & rate schedule fallbacks |

---

## Hybrid Architecture (Cloud + Local Tunnel Relay)

```
[ User Browser / Railway Frontend ]
              │
              ▼ (Calls fixed domain: https://your-railway-tunnel.up.railway.app)
[ Railway Cloud WebSocket Tunnel Relay ]
              │  ▲ (Persistent background WSS connection)
              ▼  │
 [ Local Machine (`run_tunnel_client.bat`) ]
              └──► Executes Playwright using Local Residential IP (Bypasses DataDome / CAPTCHAs!)
```

### Why This Hybrid Setup?
1. **Anti-Bot Bypass**: Scrapers run from your local machine's residential ISP IP, preventing Cloud IP blocks by DataDome & Cloudflare.
2. **Fixed Domain**: The Railway Tunnel domain never changes, eliminating constant URL updating.
3. **No 60-Minute Limits**: Unlike free ngrok or pinggy, the Railway WebSocket Tunnel Relay runs 24/7 with zero time limits and zero extra costs.

---

## Quick Start Guide

### Option 1: Running Fully Local (Local Frontend + Local Backend)

#### 1. Backend Setup
```cmd
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
playwright install chromium
python main.py
```

#### 2. Frontend Setup
```cmd
cd frontend
npm install
npm run dev
```
Open **`http://localhost:3000`** in your browser.

---

### Option 2: Running Cloud Frontend + Local Backend (Recommended Workflow)

1. **Start Local Backend**:
   Double-click **`run_live_loop.bat`** (or `python main.py` in `backend`).
2. **Start Railway Cloud Tunnel**:
   Double-click **`run_tunnel_client.bat`** on your desktop.
3. **Open Cloud Frontend**:
   Visit your Railway deployed frontend website (e.g., `https://frontend-production-xxxx.up.railway.app`).
   The top bar badge will display 🟢 **`Local Tunnel Relay`**!

---

## Admin Dashboard (`/admin`)

Visit `/admin` on your frontend to access system management tools:

- **Register / Amend Custom City & Port Code**: Add new UN/LOCODEs, override city display names, and bind custom port mappings stored in `backend/data/custom_ports.json`.
- **Carrier Overrides**: Manage carrier-specific port aliases (e.g. `KHKOS` $\rightarrow$ `Sihanoukville` for OOCL, `INCOK` $\rightarrow$ `Cochin (KERALA), India` for Maersk).
- **Search History & Route Health**: Monitor carrier success rates and execution logs across searches.

---

## Project Structure

```
├── backend/
│   ├── main.py                     # FastAPI entry point
│   ├── Dockerfile                  # Production Railway Dockerfile
│   ├── api/                        # REST API routes (user, admin, rate search)
│   ├── carriers/                   # Live carrier connectors (Maersk, OOCL, ONE, etc.)
│   ├── services/                   # Port manager, job service, charge classifier
│   └── data/                       # custom_ports.json & port database
├── frontend/
│   ├── src/app/                    # Next.js pages (main search, admin)
│   ├── src/components/             # UI components, status badges, config modal
│   └── src/lib/                    # API client, failover/recovery logic, Excel exporter
├── scripts/
│   ├── tunnel_relay/               # Railway WebSocket Tunnel Relay server
│   └── tunnel_client.py            # Local machine tunnel client script
├── run_tunnel_client.bat           # 1-Click launcher for Railway Cloud Tunnel
├── run_live_loop.bat               # 1-Click launcher for local backend
├── CHANGELOG.md                    # System change log
└── README.md                       # Product documentation
```

---

## Security & Best Practices

- **Never commit credentials** — Credentials and private keys are managed via environment variables (`.env`).
- **Data Privacy** — Local session profiles are stored in `.gitignored` directories (`backend/chrome_profile_*`).

---

## License

Internal Proprietary — **Infreight Logistics**. All Rights Reserved.
