from typing import List, Dict, Any
from app.models.schemas import (
    Bidder,
    BidderIdentifiers,
    BidderFinancials,
    DocumentType,
    DirectorInfo
)

DEMO_BIDDERS_SEED: List[Dict[str, Any]] = [
    {
        "bidder_id": "BID-2026-0891",
        "tender_id": "GEM/2026/B/89420",
        "company_name": "Apex InfraTech Private Limited",
        "legal_structure": "Private Limited",
        "registered_state": "Maharashtra",
        "registered_address": "Plot 45, Andheri East, Mumbai, Maharashtra, 400069",
        "bank_branch_code": "SBIN0004921",
        "conflict_links_count": 0,
        "directors": [
            {"din": "08412910", "name": "Rajiv Mehta", "designation": "Managing Director", "is_flagged_debarred": False},
            {"din": "08412911", "name": "Pooja Mehta", "designation": "Director", "is_flagged_debarred": False}
        ],
        "identifiers": {
            "gstin": "27AABCA1234F1Z5",
            "pan": "AABCA1234F",
            "cin": "U72200MH2018PTC123456",
            "udyam_registration_number": "UDYAM-MH-01-0012345",
            "epfo_code": "MH/BAN/0045892/000"
        },
        "financials": {
            "annual_turnover_inr": 45000000.0,
            "net_worth_inr": 12000000.0,
            "last_financial_year": "2024-25",
            "itr_filed_years": ["2022-23", "2023-24", "2024-25"]
        },
        "scenario_type": "COMPLIANT_MODEL_BIDDER",
        "scenario_description": "Model MSME vendor: Fully compliant across GST, PAN, Udyam, EPFO, and CPPP registries. Trust Score 868 (AAA Prime). All documents match official data.",
        "documents_to_seed": [
            {"type": DocumentType.GST_CERTIFICATE, "name": "Apex_GST_Registration_Certificate.pdf"},
            {"type": DocumentType.UDYAM_CERTIFICATE, "name": "Apex_Udyam_MSME_Certificate.pdf"},
            {"type": DocumentType.BALANCE_SHEET, "name": "Apex_Audited_Financials_FY25.pdf"},
            {"type": DocumentType.ISO_27001_CERTIFICATE, "name": "Apex_ISO_27001_Certificate.pdf"}
        ]
    },
    {
        "bidder_id": "BID-2026-0442",
        "tender_id": "GEM/2026/B/89420",
        "company_name": "Bharat Heavy Logistics Solutions",
        "legal_structure": "LLP",
        "registered_state": "Gujarat",
        "registered_address": "B-402, SG Highway, Ahmedabad, Gujarat, 380054",
        "bank_branch_code": "HDFC0001842",
        "conflict_links_count": 0,
        "directors": [
            {"din": "07198234", "name": "Suresh Patel", "designation": "Designated Partner", "is_flagged_debarred": False},
            {"din": "07198235", "name": "Kiran Patel", "designation": "Partner", "is_flagged_debarred": False}
        ],
        "identifiers": {
            "gstin": "24AAACB9876Q1Z3",
            "pan": "AAACB9876Q",
            "cin": "AAH-8942",
            "udyam_registration_number": "UDYAM-GJ-04-0098412",
            "epfo_code": "GJ/AHM/0078129/000"
        },
        "financials": {
            "annual_turnover_inr": 45000000.0, # Claimed on balance sheet
            "net_worth_inr": 8500000.0,
            "last_financial_year": "2024-25",
            "itr_filed_years": ["2023-24", "2024-25"]
        },
        "scenario_type": "DOCUMENT_MISMATCH_SUSPICIOUS",
        "scenario_description": "Data Discrepancy Case: Audited balance sheet claims ₹4.5 Cr turnover, but GSTN tax filings reflect only ₹1.2 Cr. Trust Score 720 (BBB).",
        "documents_to_seed": [
            {"type": DocumentType.GST_CERTIFICATE, "name": "Bharat_Logistics_GST_Form.pdf"},
            {"type": DocumentType.UDYAM_CERTIFICATE, "name": "Bharat_Udyam_Registration.pdf"},
            {"type": DocumentType.BALANCE_SHEET, "name": "Bharat_Audited_BalanceSheet_2025.pdf"}
        ]
    },
    {
        "bidder_id": "BID-2026-0109",
        "tender_id": "GEM/2026/B/89420",
        "company_name": "Vanguard Defense & Engineering Works",
        "legal_structure": "Private Limited",
        "registered_state": "Delhi",
        "registered_address": "Plot 12, Phase-II, Okhla Industrial Area, New Delhi, 110020",
        "bank_branch_code": "SBIN0004921",
        "conflict_links_count": 3,
        "directors": [
            {"din": "01928374", "name": "Vikram Malhotra", "designation": "Managing Director", "is_flagged_debarred": True},
            {"din": "03849102", "name": "Anil Sharma", "designation": "Director", "is_flagged_debarred": False}
        ],
        "identifiers": {
            "gstin": "07AAACV7788P1Z8",
            "pan": "AAACV7788P",
            "cin": "U29100DL2012PTC892144",
            "udyam_registration_number": "UDYAM-DL-02-0056123",
            "epfo_code": "DL/CPM/0091823/000"
        },
        "financials": {
            "annual_turnover_inr": 85000000.0,
            "net_worth_inr": 25000000.0,
            "last_financial_year": "2024-25",
            "itr_filed_years": ["2022-23", "2023-24"]
        },
        "scenario_type": "HARD_FAIL_DEBARRED_VENDOR",
        "scenario_description": "Hard-Fail / Blacklisted Vendor: Active debarment order under GFR 151 on CPPP. Trust Score 385 (D Subprime). High-risk cartel linkage to debarred firm.",
        "documents_to_seed": [
            {"type": DocumentType.GST_CERTIFICATE, "name": "Vanguard_GST_Cert.pdf"},
            {"type": DocumentType.BALANCE_SHEET, "name": "Vanguard_Financial_Summary.pdf"}
        ]
    }
]
