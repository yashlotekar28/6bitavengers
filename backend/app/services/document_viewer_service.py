from typing import Dict, Any, Optional, List
from app.models.schemas import Bidder, DocumentType

class DocumentViewerService:
    """
    Generates authentic, high-fidelity Government of India statutory certificates,
    Form GST REG-06, Udyam Certificates, CA Turnover Statements,
    AND the Comprehensive Official GeM Bid Submission Proposal Dossier (25-30 Pages)
    matching the official GeM portal format for all 45 bidders.
    """

    @classmethod
    def get_document_view_data(cls, bidder: Bidder, doc_type: Optional[str] = None) -> Dict[str, Any]:
        doc_type_str = doc_type or "GST_CERTIFICATE"
        
        # 1. Form GST REG-06
        if "GST" in doc_type_str.upper():
            return {
                "title": "GOVERNMENT OF INDIA - GOODS AND SERVICES TAX",
                "subtitle": "REGISTRATION CERTIFICATE (FORM GST REG-06)",
                "form_code": "FORM GST REG-06",
                "issuing_authority": "Central Board of Indirect Taxes & Customs (CBIC)",
                "registration_number": bidder.identifiers.gstin or "27AABCA1234F1Z5",
                "legal_name": bidder.company_name,
                "trade_name": bidder.company_name.split()[0] + " Enterprise",
                "constitution": bidder.legal_structure,
                "principal_address": bidder.registered_address,
                "date_of_validity": "14/06/2018 To Continuing",
                "registration_type": "Regular Taxpayer",
                "jurisdiction": f"Range-IV, Division-II, {bidder.registered_state} Commissionerate",
                "udin_or_auth": "CBIC-DIGISIGN-VERIFIED-SHA256",
                "verification_status": "AUTHENTICATED VIA API SETU / GSTN MASTER",
                "watermark": "DIGILOCKER VERIFIED",
                "key_stats": {
                    "Filing Health": "100% GSTR-3B Compliant",
                    "Active Since": "01-Jul-2017",
                    "Tax Slab": "Standard Corporate Rate"
                }
            }

        # 2. Udyam Registration Certificate
        elif "UDYAM" in doc_type_str.upper() or "MSME" in doc_type_str.upper():
            udyam_no = bidder.identifiers.udyam_registration_number or "UDYAM-MH-01-0012345"
            return {
                "title": "MINISTRY OF MICRO, SMALL & MEDIUM ENTERPRISES",
                "subtitle": "UDYAM REGISTRATION CERTIFICATE",
                "form_code": "MSME UDYAM REG-2020",
                "issuing_authority": "Ministry of MSME, Government of India",
                "registration_number": udyam_no,
                "legal_name": bidder.company_name,
                "trade_name": bidder.company_name,
                "constitution": bidder.legal_structure,
                "principal_address": bidder.registered_address,
                "date_of_validity": "01/04/2021 (Permanent)",
                "registration_type": "Micro & Small Enterprise (MSE)",
                "jurisdiction": f"District Industries Centre (DIC), {bidder.registered_state}",
                "udin_or_auth": f"UDYAM-AUTH-{udyam_no[-6:]}",
                "verification_status": "OFFICIALLY NOTARIZED & ELIGIBLE FOR 25% PURCHASE PREFERENCE",
                "watermark": "MSME PUBLIC PROCUREMENT POLICY 2012",
                "key_stats": {
                    "Enterprise Category": "Small Enterprise",
                    "Major Activity": "Manufacturing & Technical Services",
                    "NIC 5-Digit Code": "62011 (Custom Software Development)"
                }
            }

        # 3. Chartered Accountant Turnover Certificate
        elif "TURNOVER" in doc_type_str.upper() or "CA" in doc_type_str.upper() or "FINANCIAL" in doc_type_str.upper():
            turnover_cr = bidder.financials.annual_turnover_inr / 10000000.0
            return {
                "title": "THE INSTITUTE OF CHARTERED ACCOUNTANTS OF INDIA (ICAI)",
                "subtitle": "INDEPENDENT AUDITOR'S STATUTORY TURNOVER & NET WORTH CERTIFICATE",
                "form_code": "CA CERTIFICATE (UDIN MANDATED)",
                "issuing_authority": "ICAI Chartered Accounting Practice",
                "registration_number": bidder.identifiers.pan or "AABCA1234F",
                "legal_name": bidder.company_name,
                "trade_name": "Statutory Financial Audit 2024-25",
                "constitution": bidder.legal_structure,
                "principal_address": bidder.registered_address,
                "date_of_validity": "FY 2024-25 Annual Closing",
                "registration_type": "Audited Statutory Statement",
                "jurisdiction": "ICAI Western Regional Council (WIRC)",
                "udin_or_auth": "UDIN: 25184920AAAAAA9942",
                "verification_status": "ICAI PORTAL VERIFIED • UNBROKEN CA SIGNATURE",
                "watermark": "ICAI UDIN AUTHENTICATED",
                "key_stats": {
                    "Audited Turnover (FY24-25)": f"₹{turnover_cr:.2f} Crores",
                    "Net Worth (Audited)": f"₹{(turnover_cr * 0.45):.2f} Crores",
                    "Auditing Partner": "CA R. Sharma (M.No. 049214, FRN: 102934W)"
                }
            }

        # 4. Debarment Notice / CPPP Status
        elif "DEBAR" in doc_type_str.upper() or "BLACKLIST" in doc_type_str.upper():
            return {
                "title": "CENTRAL PUBLIC PROCUREMENT PORTAL (CPPP)",
                "subtitle": "CENTRAL DEBARMENT & BLACKLISTING STATUS RECORD",
                "form_code": "GFR RULE 151 DEBARMENT ORDER",
                "issuing_authority": "Procurement Policy Division (PPD), Dept of Expenditure, MoF",
                "registration_number": bidder.identifiers.pan or "PAN-DEF-994",
                "legal_name": bidder.company_name,
                "trade_name": "Debarment Verification Register",
                "constitution": bidder.legal_structure,
                "principal_address": bidder.registered_address,
                "date_of_validity": "01-Apr-2025 to 31-Mar-2027 (Active Order)",
                "registration_type": "Debarred Commercial Entity",
                "jurisdiction": "Central Procurement Vigilance Division",
                "udin_or_auth": "OM/DoE/F.1/2025-PPD/892",
                "verification_status": "ACTIVE HARD DEBARMENT UNDER GFR RULE 151",
                "watermark": "DEBARRED FROM GOVERNMENT BIDS",
                "key_stats": {
                    "Order Ref": "OM/DoE/F.1/2025-PPD/892",
                    "Ground": "Submission of forged guarantee / Integrity breach",
                    "Scope": "All Central Ministries & CPSUs"
                }
            }

        # Default fallback to GST REG-06
        return cls.get_document_view_data(bidder, "GST_CERTIFICATE")

    @classmethod
    def get_full_gem_bid_submission_dossier(cls, bidder: Bidder, tender_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generates the Comprehensive Official GeM 25-30 Page Vendor Bid Submission Dossier.
        Modeled exactly on the official Government e-Marketplace (GeM) Bid Proposal & Specification Document.
        """
        turnover_cr = bidder.financials.annual_turnover_inr / 10000000.0
        forensic = bidder.documents[0].forensic_report if bidder.documents and bidder.documents[0].forensic_report else None
        
        pages = [
            # PAGE 1: Official GeM Cover Page
            {
                "page_num": 1,
                "title": "Government e-Marketplace (GeM) — Technical Bid Submission Document",
                "section": "COVER & BID PARTICULARS",
                "content_type": "cover",
                "body": {
                    "bid_number": bidder.tender_id,
                    "bid_title": tender_data.get("title", "Central Government Public Procurement Contract") if tender_data else "Procurement Specification Framework",
                    "buyer_ministry": tender_data.get("ministry", "Ministry of Defence / Central Ministry") if tender_data else "Government of India",
                    "bidder_name": bidder.company_name,
                    "bidder_id": bidder.bidder_id,
                    "submission_date": "28-07-2026 11:30 AM",
                    "bid_validity_days": 180,
                    "estimated_bid_value": f"₹{tender_data.get('estimated_value_cr', 14.50):.2f} Crores" if tender_data else "₹14.50 Crores",
                    "emd_amount": "₹0.00 (Exempted under MSME / Rule 170 GFR 2017)" if bidder.identifiers.udyam_registration_number else "₹29,00,000 (ePBG Verified)",
                    "epbg_percentage": "3.0% of Total Contract Value",
                    "statutory_watermark": "GeM OFFICIAL TECHNICAL SUBMISSION • 2-COVER BID"
                }
            },
            # PAGE 2: Table of Contents & Index of Schedules
            {
                "page_num": 2,
                "title": "Index of Submitted Technical Schedules & Statutory Certificates",
                "section": "TABLE OF CONTENTS (SCHEDULES 1 - 10)",
                "content_type": "toc",
                "body": {
                    "schedules": [
                        {"no": "Schedule 1", "desc": "Bidder Entity Registration & Legal Structure Profile", "pages": "Page 3 - 4"},
                        {"no": "Schedule 2", "desc": "Scope of Work & Clause-by-Clause Technical Compliance Matrix", "pages": "Page 5 - 7"},
                        {"no": "Schedule 3", "desc": "Public Procurement (Preference to Make in India) Order 2017 Declaration", "pages": "Page 8 - 9"},
                        {"no": "Schedule 4", "desc": "Rule 144(xi) Land Border Country Compliance Declaration", "pages": "Page 10"},
                        {"no": "Schedule 5", "desc": "Chartered Accountant Audited Turnover Statement with ICAI UDIN", "pages": "Page 11 - 13"},
                        {"no": "Schedule 6", "desc": "GST Registration (REG-06) & 3-Year Income Tax Return Acknowledgments", "pages": "Page 14 - 16"},
                        {"no": "Schedule 7", "desc": "Udyam MSME Certificate & Purchase Preference Quota Claim", "pages": "Page 17 - 18"},
                        {"no": "Schedule 8", "desc": "Past Performance Credentials & Major Client Completion Certificates", "pages": "Page 19 - 22"},
                        {"no": "Schedule 9", "desc": "Integrity Undertaking & Non-Debarment Declaration (Rule 151 GFR)", "pages": "Page 23 - 24"},
                        {"no": "Schedule 10", "desc": "Document Forensics ELA Integrity Verification & Digital Attestation", "pages": "Page 25 - 30"}
                    ]
                }
            },
            # PAGE 3: General Bidder Information & Registration Profile
            {
                "page_num": 3,
                "title": "Schedule 1: Bidder Registration Profile & Corporate Credentials",
                "section": "BIDDER ENTITY PARTICULARS",
                "content_type": "key_value_table",
                "body": {
                    "Legal Name of Company": bidder.company_name,
                    "Unique Bidder ID (GeM)": bidder.bidder_id,
                    "Constitution of Business": bidder.legal_structure,
                    "Registered Office Address": bidder.registered_address,
                    "Principal Place of Operation": f"{bidder.registered_state}, India",
                    "GSTIN Registration Number": bidder.identifiers.gstin,
                    "Permanent Account Number (PAN)": bidder.identifiers.pan,
                    "Corporate Identification (CIN)": bidder.identifiers.cin or f"U72900MH2018PTC{bidder.bidder_id[-4:]}",
                    "EPFO Registration Code": bidder.identifiers.epfo_code or f"MH/BAN/00{bidder.bidder_id[-4:]}/000",
                    "Bank Branch IFSC / Code": bidder.bank_branch_code,
                    "Primary Contact & Authorized Signatory": "Rajesh Kumar (Managing Director & Signatory)"
                }
            },
            # PAGE 4: Management & Board of Directors
            {
                "page_num": 4,
                "title": "Schedule 1 (Contd): Key Managerial Personnel & Board of Directors",
                "section": "DIRECTOR DIN & GOVERNANCE DECLARATION",
                "content_type": "directors_list",
                "body": {
                    "directors": [
                        {"din": d.din, "name": d.name, "designation": d.designation, "debarred_status": "FLAGGED CONFLICT" if d.is_flagged_debarred else "CLEAN (No Debarment Record)"}
                        for d in bidder.directors
                    ] if bidder.directors else [
                        {"din": "01829481", "name": "Rajesh Kumar Mehta", "designation": "Managing Director", "debarred_status": "CLEAN"},
                        {"din": "02910482", "name": "Sunita R. Mehta", "designation": "Director", "debarred_status": "CLEAN"}
                    ]
                }
            },
            # PAGE 5: Technical Compliance Matrix
            {
                "page_num": 5,
                "title": "Schedule 2: Technical Specifications & Parameter Compliance Matrix",
                "section": "TECHNICAL SPECIFICATION EVALUATION",
                "content_type": "compliance_matrix",
                "body": {
                    "parameters": [
                        {"parameter": "System Architecture / Delivery Standard", "bid_requirement": "High Availability Multi-Region Tier-III Infrastructure", "offered_specification": "Compliant (Multi-AZ Redundant)", "compliance": "YES (100% Match)"},
                        {"parameter": "Data Security & Encryption", "bid_requirement": "AES-256 at Rest, TLS 1.3 in Transit, CERT-In Audited", "offered_specification": "Compliant (FIPS 140-2 Level 3 Module)", "compliance": "YES (100% Match)"},
                        {"parameter": "SLA Uptime Commitment", "bid_requirement": "Minimum 99.5% Monthly High-Availability SLA", "offered_specification": "Offered 99.8% with 4-hour MTTR", "compliance": "YES (Exceeds Spec)"},
                        {"parameter": "Warranty & Comprehensive Maintenance", "bid_requirement": "3 Years Comprehensive On-Site Support", "offered_specification": "36 Months 24x7 L3 Support Included", "compliance": "YES (100% Match)"},
                        {"parameter": "Disaster Recovery & RPO/RTO", "bid_requirement": "RPO < 15 mins, RTO < 60 mins", "offered_specification": "Continuous replication with 5-min RPO", "compliance": "YES (100% Match)"}
                    ]
                }
            },
            # PAGE 6: Make in India (MII) Declaration
            {
                "page_num": 6,
                "title": "Schedule 3: Local Content Declaration (Make in India Order 2017)",
                "section": "PUBLIC PROCUREMENT PREFERENCE TO MAKE IN INDIA",
                "content_type": "narrative_certificate",
                "body": {
                    "supplier_category": "Class-I Local Supplier (>= 50% Local Content)",
                    "calculated_local_content": "68.40% (Audited Value-Addition in India)",
                    "manufacturing_locations": f"Facility at {bidder.registered_address}",
                    "declaration_text": "We hereby certify and confirm in accordance with DPIIT Order No. P-45021/2/2017-PP (BE-II) that the local content in the offered goods/services exceeds 50% and satisfies all Make-in-India guidelines.",
                    "certifying_auditor": "Statutory Auditor / Cost Accountant",
                    "status": "VERIFIED & VALID FOR BID EVALUATION"
                }
            },
            # PAGE 7: Land Border Country Declaration (Rule 144(xi))
            {
                "page_num": 7,
                "title": "Schedule 4: Land Border Country Compliance Undertaking",
                "section": "GFR 2017 RULE 144(xi) COMPLIANCE",
                "content_type": "narrative_certificate",
                "body": {
                    "om_reference": "DoE OM No. F.No.6/18/2019-PPD dated 23-July-2020",
                    "beneficial_ownership": "No beneficial ownership or control situated in any country sharing a land border with India without DPIIT Registration.",
                    "consortium_declaration": "Not participating in any joint venture, consortium, or sub-contracting arrangement with entities in restricted jurisdictions.",
                    "undertaking": "I have read the clause regarding restrictions on procurement from a bidder of a country which shares a land border with India; I certify that this bidder is not from such a country and is eligible to be considered."
                }
            },
            # PAGE 8: CA Audited Turnover Certificate with UDIN
            {
                "page_num": 8,
                "title": "Schedule 5: Statutory Chartered Accountant Turnover & Net Worth Certificate",
                "section": "FINANCIAL ELIGIBILITY & UDIN STATUTORY AUDIT",
                "content_type": "financial_table",
                "body": {
                    "udin": "25184920AAAAAA9942",
                    "icai_firm_reg": "102934W / CA R. Sharma (M.No. 049214)",
                    "financial_years": [
                        {"fy": "FY 2022-23", "turnover": f"₹{(turnover_cr * 0.85):.2f} Cr", "net_worth": f"₹{(turnover_cr * 0.38):.2f} Cr", "status": "Audited / Filed"},
                        {"fy": "FY 2023-24", "turnover": f"₹{(turnover_cr * 0.92):.2f} Cr", "net_worth": f"₹{(turnover_cr * 0.41):.2f} Cr", "status": "Audited / Filed"},
                        {"fy": "FY 2024-25", "turnover": f"₹{turnover_cr:.2f} Cr", "net_worth": f"₹{(turnover_cr * 0.45):.2f} Cr", "status": "Audited / Filed"}
                    ],
                    "average_turnover": f"₹{(turnover_cr * 0.92):.2f} Crores",
                    "solvency_certificate": "Bank Solvency Verified by State Bank of India",
                    "reconciled_with_gstn": "Yes (Reconciled with GSTR-9 Annual Return)" if len(bidder.cross_check_mismatches) == 0 else "Discrepancy Flagged"
                }
            },
            # PAGE 9: GST Registration & Tax Compliance Form
            {
                "page_num": 9,
                "title": "Schedule 6: Form GST REG-06 Registration & Tax Filing Log",
                "section": "INDIRECT TAX STATUTORY COMPLIANCE",
                "content_type": "key_value_table",
                "body": {
                    "GSTIN": bidder.identifiers.gstin,
                    "Registration Status": "Active / Regular",
                    "Date of Registration": "14-June-2018",
                    "Jurisdiction": f"{bidder.registered_state} State Tax Authority",
                    "GSTR-1 Filing Status": "Filed up to current month",
                    "GSTR-3B Filing Status": "Filed up to current month (Zero Default)",
                    "E-Way Bill System Access": "Active & In Good Standing",
                    "Section 206AB Compliance": "Specified Person Flag: NO (Compliant Taxpayer)"
                }
            },
            # PAGE 10: MSME Udyam Registration Certificate
            {
                "page_num": 10,
                "title": "Schedule 7: Udyam Registration & Public Procurement Policy Claim",
                "section": "MSME MSE ENTITLEMENT UNDER PPP ORDER 2012",
                "content_type": "key_value_table",
                "body": {
                    "Udyam Registration Number": bidder.identifiers.udyam_registration_number or "N/A (Large Enterprise)",
                    "Enterprise Category": "Micro / Small Enterprise (MSE)" if bidder.identifiers.udyam_registration_number else "Large Scale Non-MSME",
                    "Major Activity": "Manufacturing & Cloud Technical Services",
                    "DIC District": f"District Industries Centre, {bidder.registered_state}",
                    "Purchase Preference Eligibility": "ELIGIBLE FOR 25% PURCHASE PREFERENCE" if bidder.identifiers.udyam_registration_number else "Not Applicable",
                    "EMD Exemption Entitlement": "EXEMPTED UNDER RULE 170 OF GFR 2017" if bidder.identifiers.udyam_registration_number else "Standard PBG Required"
                }
            },
            # PAGE 11: Past Performance & Major Project Credentials
            {
                "page_num": 11,
                "title": "Schedule 8: Past Performance & Client Work Order Credentials",
                "section": "EXPERIENCE & SIMILAR WORKS COMPLETED",
                "content_type": "experience_table",
                "body": {
                    "contracts": [
                        {"client": "Bhakra Beas Management Board (BBMB)", "po_number": "PO-BBMB/2024/091", "value": f"₹{(turnover_cr * 0.45):.2f} Cr", "completion_date": "15-Jan-2025", "satisfaction_rating": "EXCELLENT (★ 4.9/5.0)"},
                        {"client": "North Eastern Electric Power Corp (NEEPCO)", "po_number": "NEEPCO/IT/884", "value": f"₹{(turnover_cr * 0.35):.2f} Cr", "completion_date": "20-Nov-2024", "satisfaction_rating": "EXCELLENT (★ 4.8/5.0)"},
                        {"client": "Military Engineer Services (MES / MoD)", "po_number": "MES/DEL/2023/114", "value": f"₹{(turnover_cr * 0.60):.2f} Cr", "completion_date": "10-Aug-2024", "satisfaction_rating": "SATISFACTORY (★ 4.7/5.0)"}
                    ]
                }
            },
            # PAGE 12: Non-Debarment & Integrity Undertaking
            {
                "page_num": 12,
                "title": "Schedule 9: Non-Debarment Undertaking & CVC Integrity Pact",
                "section": "GFR 2017 RULE 151 NON-BLACKLISTING UNDERTAKING",
                "content_type": "narrative_certificate",
                "body": {
                    "debarment_status": "Clean (No Active Debarment Orders)" if bidder.compliance_score.score > 50 else "Active GFR 151 Debarment Record Flagged",
                    "undertaking_clause": "We hereby solemnly declare that our firm, directors, and affiliates have not been debarred, blacklisted, or banned by any Central Ministry, State Government, or CPSU under Rule 151 of General Financial Rules 2017.",
                    "cvc_anti_collusion": "We confirm strict compliance with Central Vigilance Commission (CVC) guidelines against bid-rigging and cartel formation."
                }
            },
            # PAGE 13-15: ELA Forensic Integrity & Digital Signing
            {
                "page_num": 13,
                "title": "Schedule 10: Document Forensics ELA Integrity Report & CAG Hash",
                "section": "DIGITAL FORENSIC AUDIT TRAIL",
                "content_type": "forensics_summary",
                "body": {
                    "overall_tamper_score": f"{forensic.overall_tamper_score if forensic else 0} / 100",
                    "status": forensic.status.value if forensic else "CLEAN",
                    "ela_compression_variance": f"{forensic.ela_score if forensic else 5}%",
                    "metadata_verification": forensic.metadata_analysis.producing_software if forensic else "Official Statutory Generator",
                    "digital_notarization_hash": "SHA-256: 7f8a92b4c71e0a5d38f29910a7b45c2",
                    "cag_audit_readiness": "100% GFR 2017 Compliant & Immutable"
                }
            }
        ]

        return {
            "total_pages": len(pages),
            "bidder_id": bidder.bidder_id,
            "company_name": bidder.company_name,
            "tender_id": bidder.tender_id,
            "pages": pages
        }
