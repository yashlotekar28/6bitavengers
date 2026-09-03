# 🛡️ GeM Nirikshan AI — Internal Hackathon Documentation

> **Project**: GeM Nirikshan AI — Government e-Marketplace Procurement Intelligence & Fraud Detection System
> **Repository**: [github.com/yashlotekar28/6bitavengers](https://github.com/yashlotekar28/6bitavengers)
> **Framework**: GFR 2017 | MCA21 | GSTN | EPFO | Udyam | ELA Forensics | Gemini AI

---

## 📌 Project in One Line

> *An AI-powered, GFR-2017-compliant bid evaluation platform that automatically verifies 45 vendor dossiers across 3 Central Government tenders — detecting document forgery, cartel rings, and statutory violations in real-time.*

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                      OFFICER BROWSER (React + Babel)                 │
│  Login → Tender Selection → Bid Opening → Evaluation Cockpit →      │
│  Bid Results → AI Chat → Document Forensics → CAG Audit Trail       │
└────────────────────────────┬────────────────────────────────────────┘
                             │  HTTP REST API
┌────────────────────────────▼────────────────────────────────────────┐
│              FASTAPI BACKEND  (Python 3.11)                          │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                  VERIFICATION PIPELINE                       │    │
│  │  OCR Extract → Cross-Verify → Rules Engine → AI Recommend   │    │
│  │  → Score → Forensics → Trust Score → Entity Graph           │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                       │
│  ┌─────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────┐  │
│  │  Adapters   │ │  Services    │ │  AI Engine   │ │  Audit     │  │
│  │ GST/PAN/CIN │ │ Forensics    │ │ Gemini 2.0   │ │ CAG Trail  │  │
│  │ Udyam/EPFO  │ │ TrustScore   │ │ Flash API    │ │ GFR Audit  │  │
│  │ Debarment   │ │ EntityGraph  │ │              │ │            │  │
│  └─────────────┘ └──────────────┘ └──────────────┘ └────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                             │
                ┌────────────▼─────────────┐
                │   In-Memory Database     │
                │  BIDDERS_DB + TENDERS_DB │
                │  (45 Vendors, 3 Tenders) │
                └──────────────────────────┘
```

---

## 📁 GitHub Repository Tree — Fully Elaborated

```
6bitavengers/  (GitHub Root)
│
├── 📄 .env                         # Environment secrets (GEMINI_API_KEY, DB credentials)
├── 📄 .env.example                 # Template showing which env vars are required
├── 📄 .gitignore                   # Git ignore rules (venv, __pycache__, .env, etc.)
├── 📄 Dockerfile                   # Root-level Docker image for Render/cloud deployment
├── 📄 Procfile                     # Heroku/Render process declaration: `web: uvicorn`
├── 📄 README.md                    # Project overview, setup instructions, tech stack
├── 📄 main.py                      # Root-level entry point — imports & boots FastAPI app
├── 📄 requirements.txt             # Python dependencies (fastapi, uvicorn, pillow, etc.)
├── 📄 run.ps1                      # Windows PowerShell server startup script
├── 📄 run_server.py                # Cross-platform Python server runner (uvicorn wrapper)
├── 📄 render.yaml                  # Render.com deployment config (auto-deploy on push)
├── 📄 vercel.json                  # Vercel serverless deployment config (route rewrites)
├── 📄 docker-compose.yml           # Multi-container Docker orchestration (app + redis)
│
├── 📁 api/                         # ── VERCEL SERVERLESS ENTRYPOINT ──────────────────
│   └── 📄 index.py                 # Mangum ASGI adapter wrapping FastAPI for Vercel Edge
│
├── 📁 backend/                     # ── CORE BACKEND APPLICATION ───────────────────────
│   ├── 📄 Dockerfile               # Backend-specific Docker image
│   ├── 📄 requirements.txt         # Backend Python dependencies
│   ├── 📄 test_backend.py          # Automated test suite (API route integration tests)
│   │
│   └── 📁 app/                     # FastAPI application package
│       ├── 📄 main.py              # 🔑 MAIN APP — all API routes, startup, pipeline
│       │                           #    • /api/tenders       → list/get tenders
│       │                           #    • /api/bidders       → list/get vendors
│       │                           #    • /api/chat/officer  → AI chat assistant
│       │                           #    • /api/forensics     → ELA tamper scan
│       │                           #    • /api/vault         → document vault
│       │                           #    • /api/trust-score   → CIBIL score
│       │                           #    • /api/graph         → cartel graph
│       │                           #    • /api/officer/decision → approve/reject
│       │                           #    • /api/tenders/finalize-evaluation → finalize bids
│       │                           #    • /api/audit         → CAG audit trail
│       │
│       ├── 📁 adapters/            # ── GOVERNMENT API ADAPTERS ────────────────────────
│       │   ├── 📄 base.py          # Abstract base class with shared fetch/validate logic
│       │   ├── 📄 gst_adapter.py   # GSTN portal adapter — verifies GSTIN validity & status
│       │   ├── 📄 pan_adapter.py   # Income Tax PAN adapter — validates PAN against company
│       │   ├── 📄 udyam_adapter.py # Ministry of MSME Udyam portal — MSME cert verification
│       │   ├── 📄 epfo_adapter.py  # EPFO adapter — employer code & headcount verification
│       │   └── 📄 debarment_adapter.py  # CVC/MoF blacklist — director debarment check
│       │
│       ├── 📁 core/                # ── AUTH & SECURITY CORE ───────────────────────────
│       │   ├── 📄 __init__.py
│       │   └── 📄 auth.py          # JWT-based officer authentication
│       │                           #    • authenticate_user() — validates officer credentials
│       │                           #    • create_access_token() — JWT token generator
│       │                           #    • require_officer / require_auditor — route guards
│       │
│       ├── 📁 data/                # ── SEED DATA ──────────────────────────────────────
│       │   └── 📄 demo_scenarios.py # 🔑 ALL 3 TENDERS + 45 VENDOR DOSSIERS generated here
│       │                           #    • DEMO_TENDERS_SEED  → 3 Central Govt. tenders
│       │                           #    • DEMO_BIDDERS_SEED  → 45 vendors (15 per tender)
│       │                           #    • Scenario types: COMPLIANT / MISMATCH / DEBARRED
│       │                           #    • Each vendor has: GSTIN, PAN, CIN, DIN, Udyam,
│       │                           #      EPFO, financials, directors, documents
│       │
│       ├── 📁 db/                  # ── DATABASE LAYER ─────────────────────────────────
│       │   ├── 📄 __init__.py
│       │   ├── 📄 database.py      # SQLAlchemy engine + session factory (optional SQL DB)
│       │   └── 📄 models.py        # ORM table definitions (Tender, Bidder, AuditLog)
│       │
│       ├── 📁 models/              # ── PYDANTIC SCHEMAS ───────────────────────────────
│       │   └── 📄 schemas.py       # 🔑 All data models:
│       │                           #    • Tender, Bidder, BidderIdentifiers
│       │                           #    • BidderFinancials, DirectorInfo
│       │                           #    • ComplianceScore, RiskLevel
│       │                           #    • DocumentForensicReport, TamperStatus
│       │                           #    • LongitudinalTrustScore, EntityGraph
│       │                           #    • AuditLogEntry, OfficerDecisionPayload
│       │                           #    • OfficerChatRequest/Response
│       │
│       ├── 📁 rules/               # ── CONFIGURABLE RULES ─────────────────────────────
│       │   └── 📄 tender_rules_default.yaml   # YAML rule config:
│       │                           #    • min_turnover_cr, gfr_rules, scoring weights
│       │                           #    • disqualification triggers, MSME preference rules
│       │
│       ├── 📁 services/            # ── CORE INTELLIGENCE SERVICES ─────────────────────
│       │   │
│       │   ├── 📄 ocr_extractor.py          # OCR INTELLIGENCE ENGINE
│       │   │                                #  Simulates document OCR extraction:
│       │   │                                #  reads GSTIN, PAN, CIN, turnover from PDFs
│       │   │                                #  and returns structured extracted fields
│       │   │
│       │   ├── 📄 cross_verification.py     # CROSS-VERIFICATION ENGINE
│       │   │                                #  Compares OCR-extracted values against
│       │   │                                #  5 live adapter responses (GST/PAN/Udyam/
│       │   │                                #  EPFO/Debarment) — flags mismatches
│       │   │
│       │   ├── 📄 rules_engine.py           # DETERMINISTIC GFR 2017 RULES ENGINE
│       │   │                                #  Checks all mandatory statutory gates:
│       │   │                                #  - Is vendor debarred?
│       │   │                                #  - Does GSTIN match PAN-linked entity?
│       │   │                                #  - Is turnover ≥ ₹2 Cr threshold?
│       │   │                                #  - Is CIN active in MCA21?
│       │   │                                #  Returns pass/fail per rule
│       │   │
│       │   ├── 📄 scoring_engine.py         # COMPLIANCE SCORING ENGINE
│       │   │                                #  Converts rule results → 0-100 score
│       │   │                                #  Assigns RiskLevel: LOW/MEDIUM/HIGH/CRITICAL
│       │   │                                #  Weighted by: debarment > cartel > ELA > mismatch
│       │   │
│       │   ├── 📄 ai_recommender.py         # AI REASONING ENGINE
│       │   │                                #  Generates recommended action:
│       │   │                                #  RECOMMEND_APPROVAL / FLAG_FOR_REVIEW /
│       │   │                                #  RECOMMEND_REJECTION
│       │   │                                #  + executive_summary (natural language rationale)
│       │   │
│       │   ├── 📄 document_forensics_service.py  # 3-LAYER ELA FORENSICS ENGINE
│       │   │                                #  Layer 1: Error Level Analysis (JPEG Q90)
│       │   │                                #  Layer 2: EXIF metadata & software artefacts
│       │   │                                #  Layer 3: Copy-move splice detection
│       │   │                                #  → overall_tamper_score (0-100%)
│       │   │                                #  → heatmap base64 image for UI display
│       │   │
│       │   ├── 📄 trust_scoring_service.py  # LONGITUDINAL CIBIL TRUST SCORING
│       │   │                                #  24-month track record score (300–900 scale)
│       │   │                                #  Like CIBIL for vendors:
│       │   │                                #  - GeM delivery SLA rates
│       │   │                                #  - Star ratings history
│       │   │                                #  - Dispute/penalty history
│       │   │                                #  → rating_band: PRIME_AAA / HIGH_AA / LOW_CCC
│       │   │
│       │   ├── 📄 entity_graph_service.py   # ENTITY GRAPH CARTEL DETECTION
│       │   │                                #  Builds a director/address linkage graph
│       │   │                                #  Detects shared DINs, common premises,
│       │   │                                #  circular shell company structures
│       │   │                                #  across all competing bidders
│       │   │
│       │   ├── 📄 chat_service.py           # AI OFFICER CHAT ASSISTANT
│       │   │                                #  Primary: Google Gemini 2.0 Flash API
│       │   │                                #  - Full vendor database as context
│       │   │                                #  - Answers natural language questions
│       │   │                                #  Fallback: Rule-based reasoning engine
│       │   │                                #  (10 intents: list vendors, MSME, disqualified,
│       │   │                                #   turnover, CIBIL, forensics, cartel, etc.)
│       │   │
│       │   ├── 📄 vault_service.py          # VENDOR DOCUMENT VAULT
│       │   │                                #  Generates 4-document secure dossier:
│       │   │                                #  GST REG-06 Certificate
│       │   │                                #  Udyam MSME Registration
│       │   │                                #  CA Audited Balance Sheet (ICAI UDIN)
│       │   │                                #  ISO 27001 Quality Certificate
│       │   │
│       │   ├── 📄 document_viewer_service.py # VISUAL DOCUMENT VIEWER
│       │   │                                #  Renders authentic-looking GoI certificate
│       │   │                                #  layout data for viewing in the browser
│       │   │                                #  Also generates full 25-30 page GeM Bid
│       │   │                                #  Proposal Submission Dossier
│       │   │
│       │   └── 📄 audit_service.py          # CAG AUDIT TRAIL SERVICE
│       │                                    #  Appends immutable audit events to log
│       │                                    #  Every decision, scan, login, finalization
│       │                                    #  is recorded with timestamp, actor, details
│       │                                    #  Ready for CAG/CVC inspection
│       │
│       ├── 📁 static/              # ── FRONTEND (Single-Page App) ─────────────────────
│       │   ├── 📄 index.html       # 🔑 ENTIRE REACT FRONTEND (React 18 + Babel + Tailwind CDN)
│       │   │                       #    8 pages in one file:
│       │   │                       #    1. Login Screen (GFR officer auth)
│       │   │                       #    2. Tender Selection (3 Tenders dashboard)
│       │   │                       #    3. Bid Opening (15 vendor cards per tender)
│       │   │                       #    4. Evaluation Cockpit (detailed compliance view)
│       │   │                       #    5. Bid Results & Status
│       │   │                       #    6. AI Chat Assistant drawer
│       │   │                       #    7. Document Forensics Modal (ELA Lab)
│       │   │                       #    8. CAG Audit Trail drawer
│       │   │
│       │   │                       #    Key state machines:
│       │   │                       #    • Officer Login Gate (OFFICERS dict + JWT)
│       │   │                       #    • Re-Authentication Gate (before Finalize)
│       │   │                       #    • Hindi/English Translation (T dictionary)
│       │   │                       #    • Dark/Light Mode
│       │   │                       #    • Contingency L1/L2/L3 Priority Assignment
│       │   │
│       │   └── 📄 login-bg.png     # Background image for login screen
│       │
│       └── 📁 tasks/              # ── CELERY ASYNC TASKS (optional) ──────────────────
│           ├── 📄 __init__.py
│           ├── 📄 celery_app.py    # Celery application instance (Redis broker)
│           └── 📄 verification_tasks.py  # Async task: run_verification_pipeline()
│                                   #  Runs full 8-step pipeline in background worker
│
├── 📁 dataset/                     # ── OPEN DATASET FOR RESEARCH ──────────────────────
│   ├── 📄 DATASET_DOCUMENTATION.md    # Data dictionary, field definitions, use cases
│   ├── 📄 gem_tenders_dataset.csv     # 3 GoI tenders with all metadata
│   ├── 📄 gem_bidders_45_vendors_dataset.csv  # 45 vendors: GSTIN, PAN, risk, CIBIL
│   ├── 📄 gem_nirikshan_complete_dataset.json # Full hierarchical JSON dataset
│   └── 📄 gem_nirikshan_procurement_dataset.zip  # All-in-one ZIP bundle
│
└── 📁 frontend/                    # ── STANDALONE REACT+VITE FRONTEND (unused in prod) ──
    ├── 📄 index.html               # Vite app root HTML
    ├── 📄 package.json             # npm dependencies (React, Vite, Tailwind)
    ├── 📄 tailwind.config.js       # Tailwind CSS configuration
    ├── 📄 tsconfig.json            # TypeScript config
    ├── 📄 vite.config.ts           # Vite bundler config
    ├── 📄 postcss.config.js        # PostCSS for Tailwind processing
    └── 📁 src/
        ├── 📄 App.tsx              # Root React component
        ├── 📄 main.tsx             # ReactDOM render entrypoint
        ├── 📄 index.css            # Global CSS / Tailwind directives
        ├── 📁 components/          # Reusable UI components
        │   ├── 📄 AIRecommendationCard.tsx   # AI verdict badge component
        │   ├── 📄 AuditTrailDrawer.tsx       # CAG Audit sidebar
        │   ├── 📄 BidderDetailView.tsx       # Full vendor detail panel
        │   ├── 📄 BidderListView.tsx         # Vendor list cards
        │   ├── 📄 MetricsOverview.tsx        # KPI counter cards
        │   ├── 📄 Navbar.tsx                 # Top navigation bar
        │   ├── 📄 OfficerActionPanel.tsx     # Approve/Reject action panel
        │   ├── 📄 RulesChecklistView.tsx     # GFR rule pass/fail checklist
        │   ├── 📄 ScoreGauge.tsx             # Circular compliance score gauge
        │   └── 📄 SideBySideDiffViewer.tsx   # OCR vs Live portal diff view
        ├── 📁 services/
        │   └── 📄 api.ts           # Typed API client (fetch wrappers for all routes)
        └── 📁 types/
            └── 📄 index.ts         # TypeScript type definitions (mirrors backend schemas)
```

---

## 🔩 Component Deep-Dive

### 1️⃣ `backend/app/main.py` — FastAPI Application Core
The brain of the backend. Registers **all 20+ API routes**, runs the startup pipeline (seeds 45 vendor dossiers through the full 8-step verification engine), and handles:
- **Finalization Gate**: Dynamically generates per-vendor rejection reasons based on debarment, cartel links, tamper scores, OCR mismatches, and AI recommendation.
- **Contingency L1/L2/L3**: Auto-assigns Priority 1/2/3 winners on officer approval.
- **Officer Re-Authentication**: Validates credentials against `OFFICERS` dict before allowing finalization.

---

### 2️⃣ `backend/app/adapters/` — Government Portal Adapters
Each adapter simulates a live government API call:

| Adapter | Portal Simulated | What It Checks |
|---|---|---|
| `gst_adapter.py` | GSTN (gstin.gov.in) | GSTIN active, company name match |
| `pan_adapter.py` | Income Tax PAN | PAN linked to correct entity name |
| `udyam_adapter.py` | Udyam (udyamregistration.gov.in) | MSME certificate valid & active |
| `epfo_adapter.py` | EPFO (epfindia.gov.in) | Employer code, headcount |
| `debarment_adapter.py` | CVC + MoF Blacklist | Director on debarment register |

---

### 3️⃣ `backend/app/services/` — Intelligence Services Pipeline

The **8-Step Verification Pipeline** runs sequentially on every vendor:

```
Step 1  → ocr_extractor.py          Extract fields from submitted PDFs
Step 2  → cross_verification.py     Compare OCR vs 5 live gov't portals
Step 3  → rules_engine.py           Apply GFR 2017 hard pass/fail rules
Step 4  → ai_recommender.py         Generate AI recommended action
Step 5  → scoring_engine.py         Compute 0-100 compliance score
Step 6  → document_forensics_service.py  ELA + EXIF + splice tamper scan
Step 7  → trust_scoring_service.py  Longitudinal 300-900 CIBIL trust score
Step 8  → entity_graph_service.py   Build director/premises cartel graph
```

---

### 4️⃣ `backend/app/static/index.html` — The Entire Frontend
A **3,600-line single-file React app** (React 18 + Babel CDN + Tailwind CDN) with 8 fully functional pages:

| Page | Route State | Purpose |
|---|---|---|
| **Login** | `!isLoggedIn` | Officer credential gate (GFR 2017) |
| **Tender Selection** | `SELECT_TENDER` | Browse 3 active GoI tenders |
| **Bid Opening** | `BID_OPENING` | View all 15 vendor cards per tender |
| **Evaluation Cockpit** | `EVALUATION_COCKPIT` | Deep compliance analysis per vendor |
| **Bid Results** | `BID_RESULTS_STATUS` | Final L1/L2/L3 results + rejected list |
| **AI Chat** | `isChatOpen` | Gemini-powered procurement assistant |
| **Forensics Lab** | `isForensicLabOpen` | Upload & scan any certificate for ELA |
| **CAG Audit Trail** | `isAuditOpen` | Full immutable audit log |

---

### 5️⃣ `backend/app/data/demo_scenarios.py` — The Dataset Engine
Procedurally generates all 45 vendor dossiers in 3 scenario classes:

| Scenario Type | Count | Description |
|---|---|---|
| `COMPLIANT_MODEL_BIDDER` | ~10/tender | Perfect vendor — all docs clean, score 100/100 |
| `DOCUMENT_MISMATCH_SUSPICIOUS` | ~3/tender | OCR vs portal mismatches, ELA tamper suspicion |
| `HARD_FAIL_DEBARRED_VENDOR` | ~2/tender | Director on MoF blacklist — instant disqualification |

---

### 6️⃣ `api/index.py` — Vercel Serverless Entrypoint
Wraps the FastAPI app with **Mangum** (ASGI-to-Lambda adapter) so the entire backend runs as a Vercel serverless function — eliminating the 50-second cold-start of Render.

---

### 7️⃣ `dataset/` — Open Research Dataset
Published with the repo for academic use:
- **45 vendor profiles** with 20+ fields each (GSTIN, PAN, CIN, DIN, CIBIL, risk flags)
- **3 Central Government tenders** (Defence Cloud, AIIMS Medical, EV Fleet)
- Available in CSV, JSON, and ZIP

---

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 18, Babel (in-browser), Tailwind CSS v3 CDN, marked.js |
| **Backend** | Python 3.11, FastAPI, Uvicorn, Pydantic v2 |
| **AI Engine** | Google Gemini 2.0 Flash API (`google-genai` SDK) |
| **Document Forensics** | Pillow (PIL) — real Error Level Analysis on uploaded images |
| **Database** | In-memory Python dict (BIDDERS_DB, TENDERS_DB) |
| **Auth** | JWT (python-jose) + in-app officer credential store |
| **Async Tasks** | Celery + Redis (optional background verification) |
| **Deployment** | Vercel (serverless, free) / Render (web service) / Docker |
| **Version Control** | Git + GitHub — Auto-deploy on every push to `main` |

---

## 🚀 Deployment & Access

| Platform | URL | Status |
|---|---|---|
| **Local** | `http://localhost:8000` | Run `python run_server.py` |
| **GitHub Repo** | [github.com/yashlotekar28/6bitavengers](https://github.com/yashlotekar28/6bitavengers) | Public |
| **Vercel (prod)** | Auto-deploy from GitHub `main` | Import once at vercel.com |

---

## 🔐 Demo Officer Credentials

| User ID | Password | Officer | Ministry |
|---|---|---|---|
| `officer001` | `GeM@2026` | Rajesh Kumar Sharma | Ministry of Defence |
| `officer002` | `Shield@123` | Priya Nair | Ministry of Finance |
| `officer003` | `Procure@456` | Arjun Mehta | Ministry of Railways |
| `admin` | `Admin@2026` | System Administrator | GeM PMU |

---

## 📊 By The Numbers

| Metric | Value |
|---|---|
| Active Tenders | 3 Central Government Bids |
| Vendor Dossiers | 45 (15 per tender) |
| Verification Checks per Vendor | 8 pipeline stages |
| Government Portals Simulated | 5 (GSTN, PAN, Udyam, EPFO, CVC) |
| ELA Forensic Layers | 3 (ELA Q90 + EXIF + Splice) |
| API Routes | 20+ |
| Lines of Code | ~3,600 (frontend) + ~3,200 (backend) |
| Dataset Size | 45 vendors × 20+ fields each |
| Statutory Framework | GFR 2017, PPP 2012, CVC Anti-Collusion |
