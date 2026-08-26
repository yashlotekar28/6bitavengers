# ProcureShield AI — GeM Vendor Verification & Compliance Scoring Engine (v2.0)

> **AI-Powered Public Procurement Verification, Entity Linkage & Longitudinal Trust Scoring System** for Government e-Marketplace (GeM) & CPPP Tenders.

---

## 🌟 5 Core Upgrades (v2.0)

1. 🗄️ **Unified Vendor Document Vault**: Centralized DigiLocker-synced credential vault (`GST REG-06`, `Udyam`, `Balance Sheet FY24/25`, `ISO 27001`) with expiration countdowns and multi-bid reuse tracking.
2. 📈 **Longitudinal Trust Score (CIBIL-Style 300–900)**: Multi-year vendor reliability index computed across 4 dimensions: On-time delivery SLA (35%), Tax compliance health (25%), GeM inspection pass rate (20%), and Dispute-free track record (20%). Includes 24-month historical trajectory.
3. 🕸️ **Graph-Based Entity Linking & Shell Company / Cartel Detection**: Interactive SVG network graph mapping Director DINs, common physical addresses, and hidden linkages to debarred promoters under **GFR Rule 151** with confidence scoring.
4. 🎛️ **Officer Review & Constraint Filtering Panel**: Dynamic multi-parameter filtering on CIBIL Trust Scores, MSME reservations, minimum turnover thresholds, and entity risk exclusions.
5. 💬 **Natural Language Officer Assistant (Interactive AI Chat)**: Conversational assistant supporting cross-bidder comparative analysis (*"Compare Apex vs Bharat"*), cartel investigations, and automated Technical Evaluation Committee (TEC) briefing note drafting.

---

## 🏗️ 10-Step Architecture

| Step | Component | Execution Details |
|------|-----------|-------------------|
| **Step 1** | **Bidder Intake** | GeM captures identifiers (`GSTIN`, `PAN`, `CIN`, `Udyam No`, `Tender ID`) into canonical schema. |
| **Step 2** | **Document Upload & Vault** | Uploaded statutory certificates verified on chain & linked to Unified Document Vault. |
| **Step 3A** | **Portal Adapters (Data Hub)** | Concurrent API calls to **GSTN (API Setu)**, **Income Tax PAN**, **Ministry of MSME (Udyam)**, **EPFO**, and **CPPP Debarment List**. |
| **Step 3B** | **Document Intelligence** | OCR text extraction normalized via LLM into structured JSON matching document schemas. |
| **Step 4** | **Cross-Verification** | Compares extracted OCR certificates vs live official portal records (flags turnover discrepancies, name variations, forged certs). |
| **Step 5** | **Deterministic Rules Engine** | Evaluates tender-specific YAML rules mechanically: active GST, mandatory filings, minimum turnover threshold, no debarment. **100% explainable & non-ambiguous**. |
| **Step 6** | **AI Reasoning Layer** | Contextualizes discrepancies & soft risks into a structured natural-language briefing for procurement officers. |
| **Step 7** | **Dual Scoring (Compliance + Trust)** | Computes 0–100 Compliance Score + 300–900 CIBIL-style Trust Score. |
| **Step 8** | **Executive Cockpit Dashboard** | React + Tailwind interactive dashboard with score gauges, entity linkage graph, document vault, and side-by-side diff viewer. |
| **Step 9** | **Human-in-the-Loop Decision** | Officer approves, rejects, requests clarification, or overrides with mandatory CAG justification. |
| **Step 10** | **CAG & GFR Immutable Audit Trail** | Every adapter call, OCR extraction, rule evaluation, chat query, and officer action logged with timestamps for CAG/GFR compliance. |

---

## 🎯 3 Pre-Loaded Judge-Ready Demo Scenarios

1. 🟢 **Apex InfraTech Private Limited (`BID-2026-0891`)**
   - *Compliance Score*: **100 / 100 (LOW RISK)** • *Trust Score*: **868 / 900 (AAA Prime)**
   - *Result*: All portals active, audited statements reconcile 100%, 0 entity conflicts, recommended for approval.

2. 🟡 **Bharat Heavy Logistics Solutions (`BID-2026-0442`)**
   - *Compliance Score*: **70 / 100 (MEDIUM RISK)** • *Trust Score*: **720 / 900 (BBB Moderate)**
   - *Result*: Balance Sheet claims ₹4.5 Cr turnover, but GSTN tax filings reflect only ₹1.2 Cr; name variation flagged for officer clarification.

3. 🔴 **Vanguard Defense & Engineering Works (`BID-2026-0109`)**
   - *Compliance Score*: **20 / 100 (CRITICAL RISK)** • *Trust Score*: **385 / 900 (D Subprime)**
   - *Result*: Active debarment order under GFR 151 on CPPP for fake Bank Guarantee + shared director & address links to blacklisted firm. Auto-rejection recommended.

---

## 🚀 How to Run the Prototype

```bash
# 1-Click Launch (Starts FastAPI Backend + Opens Dashboard in Browser):
python run_server.py
```
* Dashboard: `http://localhost:8000`
* Swagger API Docs: `http://localhost:8000/docs`
