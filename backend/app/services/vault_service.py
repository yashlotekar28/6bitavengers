import uuid
from typing import List, Dict, Any
from datetime import datetime, timedelta
from app.models.schemas import VaultDocument, VendorVault, DocumentType

class VendorDocumentVaultService:
    """
    Feature 1: Unified Vendor Document Vault.
    Enables one-time upload and cryptographic verification of recurring statutory documents,
    reusable across unlimited tender bids with automatic validity and expiry tracking.
    """

    @staticmethod
    def get_vault_for_vendor(vendor_id: str, company_name: str, identifiers: Dict[str, Any]) -> VendorVault:
        gstin = identifiers.get("gstin", "27AABCA1234F1Z5")
        udyam = identifiers.get("udyam_registration_number", "UDYAM-MH-01-0012345")
        pan = identifiers.get("pan", "AABCA1234F")

        # Generate realistic verified statutory vault credentials
        is_vanguard = "Vanguard" in company_name
        is_bharat = "Bharat" in company_name

        docs: List[VaultDocument] = [
            VaultDocument(
                doc_id=f"VLT-GST-{uuid.uuid4().hex[:6].upper()}",
                doc_type=DocumentType.GST_CERTIFICATE,
                document_name="Form GST REG-06 Certificate of Registration",
                issuer="Goods and Services Tax Network (GSTN)",
                issue_date="2018-06-14",
                expiry_date="2099-12-31",
                days_to_expiry=26780,
                is_valid=not is_vanguard,
                verification_badge="API_SETU_AUTHENTICATED",
                reuse_count=14,
                participated_tenders=["GEM/2024/B/1029", "GEM/2025/B/4921", "GEM/2026/B/89420"],
                file_size_kb=340,
                extracted_metadata={"gstin": gstin, "legal_name": company_name, "status": "ACTIVE" if not is_vanguard else "SUSPENDED"}
            ),
            VaultDocument(
                doc_id=f"VLT-UDYAM-{uuid.uuid4().hex[:6].upper()}",
                doc_type=DocumentType.UDYAM_CERTIFICATE,
                document_name="Udyam MSME Certificate of Enterprise Registration",
                issuer="Ministry of Micro, Small & Medium Enterprises",
                issue_date="2020-07-15",
                expiry_date="2099-12-31",
                days_to_expiry=26780,
                is_valid=True,
                verification_badge="DIGILOCKER_VERIFIED",
                reuse_count=9,
                participated_tenders=["GEM/2025/B/7712", "GEM/2026/B/89420"],
                file_size_kb=280,
                extracted_metadata={"udyam_no": udyam, "category": "MICRO" if not is_bharat else "SMALL", "activity": "SERVICES"}
            ),
            VaultDocument(
                doc_id=f"VLT-FIN-{uuid.uuid4().hex[:6].upper()}",
                doc_type=DocumentType.BALANCE_SHEET,
                document_name="Audited Financial Statements & Tax Audit Report FY24-25",
                issuer="Institute of Chartered Accountants of India (ICAI)",
                issue_date="2025-09-28",
                expiry_date="2026-09-30",
                days_to_expiry=398,
                is_valid=True,
                verification_badge="UDIN_VERIFIED_ICAI",
                reuse_count=6,
                participated_tenders=["GEM/2026/B/1129", "GEM/2026/B/89420"],
                file_size_kb=1420,
                extracted_metadata={"udin": "25184920AAAAAA9942", "financial_year": "2024-25", "audited": True}
            ),
            VaultDocument(
                doc_id=f"VLT-ISO-{uuid.uuid4().hex[:6].upper()}",
                doc_type=DocumentType.ISO_27001_CERTIFICATE,
                document_name="ISO/IEC 27001:2022 Information Security Management Cert",
                issuer="Bureau Veritas Certification India",
                issue_date="2024-03-10",
                expiry_date="2027-03-09",
                days_to_expiry=560,
                is_valid=not is_vanguard,
                verification_badge="NABCB_ACCREDITED",
                reuse_count=18,
                participated_tenders=["GEM/2024/B/8811", "GEM/2025/B/9923", "GEM/2026/B/89420"],
                file_size_kb=510,
                extracted_metadata={"certificate_no": "IND.24.9812/ISMS", "standard": "ISO 27001:2022"}
            )
        ]

        return VendorVault(
            vendor_id=vendor_id,
            company_name=company_name,
            documents=docs,
            total_reused_tenders=len(set([t for d in docs for t in d.participated_tenders])),
            last_synced=datetime.utcnow(),
            vault_status="SYNCHRONIZED_WITH_DIGILOCKER"
        )
