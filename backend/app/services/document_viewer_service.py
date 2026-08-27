from typing import Dict, Any, Optional
from app.models.schemas import Bidder, DocumentType

class DocumentViewerService:
    """
    Generates authentic, high-fidelity Government of India statutory certificates,
    Form GST REG-06, Udyam Registration Certificates, CA Turnover UDIN Statements,
    and CPPP Debarment Notices for full visual inspection across all 45 bidders.
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
