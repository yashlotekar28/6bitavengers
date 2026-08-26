import uuid
from typing import Dict, Any, List
from datetime import datetime
from app.models.schemas import UploadedDocument, DocumentType, ExtractionStatus

class DocumentIntelligenceEngine:
    """
    Simulates / Executes OCR extraction + LLM structured JSON normalization
    from uploaded PDFs and image certificates.
    """

    @staticmethod
    def extract_document(
        bidder_id: str,
        doc_type: DocumentType,
        file_name: str,
        scenario_hint: str = "",
        custom_fields: Dict[str, Any] = None
    ) -> UploadedDocument:
        doc_id = f"DOC-{uuid.uuid4().hex[:8].upper()}"
        
        extracted_fields = {}
        raw_ocr_text = ""
        
        if doc_type == DocumentType.GST_CERTIFICATE:
            gstin = custom_fields.get("gstin", "27AABCA1234F1Z5") if custom_fields else "27AABCA1234F1Z5"
            legal_name = custom_fields.get("company_name", "Apex InfraTech Private Limited") if custom_fields else "Apex InfraTech Private Limited"
            
            # Scenario 2 might have mismatch in name or date
            if "MISMATCH" in scenario_hint:
                legal_name_doc = "Apex Infrastructure Tech LLP" # Mismatch with Private Limited
            else:
                legal_name_doc = legal_name

            raw_ocr_text = f"""
            GOVERNMENT OF INDIA - GOODS AND SERVICES TAX
            REGISTRATION CERTIFICATE (FORM GST REG-06)
            Registration Number : {gstin}
            Legal Name : {legal_name_doc}
            Trade Name : Apex InfraTech
            Constitution of Business : Private Limited Company
            Principal Place of Business : Plot 45, Andheri East, Mumbai, Maharashtra, 400069
            Date of Liability : 01/07/2017
            Date of Validity : From 14/06/2018 To Continuing
            Type of Registration : Regular
            """
            extracted_fields = {
                "gstin": gstin,
                "legal_name": legal_name_doc,
                "state": "Maharashtra",
                "constitution": "Private Limited Company",
                "registration_date": "2018-06-14",
                "status": "ACTIVE"
            }

        elif doc_type == DocumentType.UDYAM_CERTIFICATE:
            udyam_no = custom_fields.get("udyam_number", "UDYAM-MH-01-0012345") if custom_fields else "UDYAM-MH-01-0012345"
            company_name = custom_fields.get("company_name", "Apex InfraTech Private Limited") if custom_fields else "Apex InfraTech Private Limited"
            
            raw_ocr_text = f"""
            UDYAM REGISTRATION CERTIFICATE
            MINISTRY OF MICRO, SMALL & MEDIUM ENTERPRISES
            UDYAM REGISTRATION NUMBER : {udyam_no}
            NAME OF ENTERPRISE : {company_name}
            TYPE OF ENTERPRISE : MICRO
            MAJOR ACTIVITY : SERVICES
            DATE OF INCORPORATION : 18/05/2018
            NATIONAL INDUSTRY CLASSIFICATION CODE(S) : 62011, 62020
            """
            extracted_fields = {
                "udyam_registration_number": udyam_no,
                "enterprise_name": company_name,
                "enterprise_type": "MICRO",
                "major_activity": "SERVICES",
                "date_of_commencement": "2018-07-01",
                "nic_codes": ["62011", "62020"]
            }

        elif doc_type == DocumentType.BALANCE_SHEET or doc_type == DocumentType.ITR_ACKNOWLEDGMENT:
            # For scenario 2, document claims 45,000,000 INR turnover while GST portal only shows 12,000,000 INR
            turnover = 45000000.0 if not custom_fields else custom_fields.get("annual_turnover_inr", 45000000.0)
            
            raw_ocr_text = f"""
            INDEPENDENT AUDITOR'S REPORT & STATEMENT OF ACCOUNTS
            FINANCIAL YEAR 2024-2025
            ASSESSMENT YEAR 2025-2026
            REVENUE FROM OPERATIONS (ANNUAL TURNOVER): INR {turnover:,.2f}
            NET PROFIT AFTER TAX: INR 6,800,000.00
            NET WORTH: INR 12,000,000.00
            UDIN: 25184920AAAAAA9942
            """
            extracted_fields = {
                "financial_year": "2024-25",
                "declared_turnover_inr": turnover,
                "net_worth_inr": 12000000.0,
                "auditor_udin": "25184920AAAAAA9942",
                "itr_form": "ITR-6"
            }

        else:
            raw_ocr_text = f"SUPPORTING STATUTORY FILING DOCUMENT - {file_name}"
            extracted_fields = {"document_reference": file_name, "verified": True}

        return UploadedDocument(
            doc_id=doc_id,
            bidder_id=bidder_id,
            doc_type=doc_type,
            file_name=file_name,
            uploaded_at=datetime.utcnow(),
            extraction_status=ExtractionStatus.COMPLETED,
            extracted_fields=extracted_fields,
            ocr_raw_text=raw_ocr_text.strip(),
            confidence=0.98
        )
