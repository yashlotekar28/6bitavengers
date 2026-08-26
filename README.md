# ProcureShield AI — GeM Vendor Verification & Compliance Engine

> **AI-Powered Public Procurement Verification, Fraud Detection & Compliance Scoring Engine** for Government e-Marketplace (GeM) & CPPP Tenders.

---

## 🏗️ 10-Step Architecture Breakdown

| Step | Component | Execution Details |
|------|-----------|-------------------|
| **Step 1** | **Bidder Submission** | GeM captures company identifiers (`GSTIN`, `PAN`, `CIN`, `Udyam No`, `Tender ID`) into canonical schema. |
| **Step 2** | **Document Upload** | Uploaded statutory PDFs/Certificates (Udyam, GST, Balance Sheets) queued for async processing. |
| **Step 3A** | **Portal Adapters (Data Hub)** | Concurrent API calls to **GSTN (API Setu)**, **Income Tax PAN**, **Ministry of MSME (Udyam)**, **EPFO**, and **CPPP Debarment List**. |
| **Step 3B** | **Document Intelligence** | OCR text extraction normalized via LLM into structured JSON matching document schemas. |
| **Step 4** | **Cross-Verification** | Compares extracted OCR certificates vs live official portal records (flags turnover discrepancies, name variations, forged certs). |
| **Step 5** | **Deterministic Rules Engine** | Evaluates tender-specific YAML rules mechanically: active GST, mandatory filings, minimum turnover threshold, no debarment. **100% explainable & non-ambiguous**. |
| **Step 6** | **AI Reasoning Layer** | Contextualizes discrepancies & soft risks into a structured natural-language briefing for procurement officers. |
| **Step 7** | **Compliance Scoring** | Composite scoring function (0–100) combining hard pass/fail gates, weighted soft rules, and discrepancy penalties into categorical **Risk Levels (LOW / MEDIUM / HIGH / CRITICAL)**. |
| **Step 8** | **Officer Dashboard** | React + Tailwind interactive dashboard with side-by-side document vs portal diff viewer, score gauge, and rules checklist. |
| **Step 9** | **Human-in-the-Loop Decision** | Officer approves, rejects, requests clarification, or overrides with mandatory audit justification. |
| **Step 10** | **Immutable Audit Trail** | Every adapter call, OCR extraction, rule evaluation, and officer action logged with timestamps for CAG/GFR compliance. |

---

## 🎯 3 Pre-Loaded Judge-Ready Demo Scenarios

1. 🟢 **Apex InfraTech Private Limited (`BID-2026-0891`)**
   - *Status*: **Fully Compliant Model Vendor**
   - *Compliance Score*: **92/100 (LOW RISK)**
   - *Result*: All portals active, audited statements reconcile 100%, recommended for approval.

2. 🟡 **Bharat Heavy Logistics Solutions (`BID-2026-0442`)**
   - *Status*: **Document Mismatch & Revenue Discrepancy**
   - *Compliance Score*: **65/100 (MEDIUM RISK)**
   - *Result*: Uploaded Balance Sheet claims ₹4.5 Cr turnover, but GSTN tax filings reflect only ₹1.2 Cr; name variation flagged for officer clarification.

3. 🔴 **Vanguard Defense & Engineering Works (`BID-2026-0109`)**
   - *Status*: **Hard-Fail / Debarred Vendor**
   - *Compliance Score*: **15/100 (CRITICAL RISK)**
   - *Result*: Active debarment order under GFR 151 on CPPP for fake Bank Guarantee + Section 206AB tax proceedings. Auto-rejection recommended.

---

## 🚀 How to Run the Prototype

### 1. Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
*API Docs available at: `http://localhost:8000/docs`*

### 2. Frontend (React + Vite + Tailwind)
```bash
cd frontend
npm install
npm run dev
```
*Dashboard opens at: `http://localhost:5173`*
