# 📊 GeM Nirikshan AI — Public Procurement & Vendor Verification Dataset

## Overview
This dataset contains official statutory procurement records, tender details, and multi-dimensional vendor compliance dossiers designed for the **GeM Nirikshan AI** compliance and fraud intelligence system under **General Financial Rules (GFR 2017)**.

---

## 📁 Dataset Files Included in this Bundle

| File Name | Format | Description |
|---|---|---|
| **gem_tenders_dataset.csv** | CSV | Active Government of India Tenders with sanctioned values, categories, and ministries. |
| **gem_bidders_45_vendors_dataset.csv** | CSV | 45 Ingested Vendor / Bidder Dossiers across 3 central tenders with tax, legal, and risk indicators. |
| **gem_nirikshan_complete_dataset.json** | JSON | Full unified hierarchical dataset including document hashes, ELA forensic reports, and entity linkages. |
| **gem_nirikshan_procurement_dataset.zip** | ZIP | Ready-to-upload archive bundle containing all CSV and JSON datasets. |

---

## 📋 Data Dictionary & Field Definitions

### 1. gem_tenders_dataset.csv
- **	ender_id**: Official GeM Bid Identification Number (e.g. GEM/2026/B/89420).
- **	itle**: Procurement subject description and technical scope.
- **category**: Category of procurement (Cloud Infrastructure, Medical Diagnostics, EV Fleets).
- **ministry**: Central Government Ministry (Ministry of Defence, Ministry of Health, Ministry of Heavy Industries).
- **department**: Sponsoring armed force or national mission command.
- **estimated_value_cr**: Sanctioned procurement budget in INR Crores (₹ Cr).
- **id_type**: GeM bid classification (PRODUCT_BID, SERVICE_BID, CUSTOM_BID).
- **closing_date**: Statutory bid submission deadline.
- **status**: Current statutory phase (TECHNICAL_EVALUATION, EVALUATION_COMPLETED).

### 2. gem_bidders_45_vendors_dataset.csv
- **idder_id**: Unique vendor submission token (e.g. BID-2026-0891).
- **	ender_id**: Associated GeM tender reference.
- **company_name**: Registered corporate legal entity name.
- **legal_structure**: Constitution (Private Limited, Public Limited, LLP, Partnership).
- **
egistered_state**: State of primary incorporation.
- **
egistered_address**: Physical operational headquarters address.
- **ank_branch_code**: IFSC / statutory banking identifier for EMD & PBG processing.
- **conflict_links_count**: Number of shared directors / common premises detected with competing bidders.
- **scenario_type**: Benchmark risk classification:
  - COMPLIANT_MODEL_BIDDER: High-integrity vendor meeting all statutory gates.
  - DOCUMENT_MISMATCH_SUSPICIOUS: OCR/Tax identity discrepancy or ELA tamper suspicion.
  - HARD_FAIL_DEBARRED_VENDOR: Director on Ministry of Finance / CVC debarment blacklist.
- **cibil_trust_score**: Longitudinal statutory trust rating (300–900 scale).
- **nnual_turnover_inr**: Audited annual turnover in INR (meets turnover thresholds).
- **gstin**: 15-character Goods and Services Tax Identification Number.
- **pan**: 10-character Permanent Account Number.
- **cin**: Corporate Identification Number (MCA registry).
- **udyam_number**: MSME / MSE registration certificate number.
- **epfo_code**: Employee Provident Fund Organisation establishment code.
- **managing_director_name**: Name of primary executive director.
- **managing_director_din**: 8-digit Director Identification Number (DIN).
- **is_director_debarred**: Boolean statutory debarment flag under GFR Rule 151.
- **submitted_documents_count**: Total statutory certificates submitted for verification (GST, Udyam, Balance Sheet, ISO).

---

## 🎯 Primary Use Cases & Analytics
1. **Automated Procurement Compliance**: Evaluating bidders against GFR 2017 mandatory rules.
2. **Cartel & Collusion Detection**: Identifying circular director networks and shell company bidding rings.
3. **Forensic Document Analysis**: Detecting digitally tampered certificates via Error Level Analysis (ELA).
4. **Machine Learning**: Training risk classification, anomaly detection, and automated L1/L2/L3 award recommendation models.
