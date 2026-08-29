from typing import List, Dict, Any
from app.models.schemas import (
    UploadedDocument,
    PortalVerificationResult,
    CrossCheckMismatch,
    RiskLevel,
    DocumentType
)

class CrossVerificationEngine:
    """
    Step 4: Cross-Verification Engine (Where Process A and B meet).
    Compares extracted document OCR fields against live portal API data.
    Flags mismatches that indicate forged, altered, stale, or conflicting documentation.
    """

    @staticmethod
    def cross_check(
        documents: List[UploadedDocument],
        portal_verifications: Dict[str, PortalVerificationResult]
    ) -> List[CrossCheckMismatch]:
        mismatches: List[CrossCheckMismatch] = []

        # Find documents by type
        gst_doc = next((d for d in documents if d.doc_type == DocumentType.GST_CERTIFICATE), None)
        udyam_doc = next((d for d in documents if d.doc_type == DocumentType.UDYAM_CERTIFICATE), None)
        financial_doc = next((d for d in documents if d.doc_type in (DocumentType.BALANCE_SHEET, DocumentType.ITR_ACKNOWLEDGMENT)), None)

        gst_portal = portal_verifications.get("GST_PORTAL")
        pan_portal = portal_verifications.get("PAN_REGISTRY")
        udyam_portal = portal_verifications.get("UDYAM_PORTAL")

        # 1. GSTIN Match & Legal Name Check
        if gst_doc and gst_portal:
            gst_ef = gst_doc.extracted_fields or {}
            doc_gstin = (gst_ef.get("gstin") or "").upper().strip()
            portal_gstin = (gst_portal.key_fields.get("gstin") or "").upper().strip()
            
            if doc_gstin and portal_gstin and doc_gstin != portal_gstin:
                mismatches.append(CrossCheckMismatch(
                    field_name="GSTIN Identifier",
                    source_a_name="Uploaded GST Certificate (OCR)",
                    source_a_value=doc_gstin,
                    source_b_name="GSTN Live Registry (API Setu)",
                    source_b_value=portal_gstin,
                    severity=RiskLevel.CRITICAL,
                    discrepancy_explanation="The GSTIN on the uploaded certificate does not match the active GST registration on file.",
                    suggested_investigation="Verify if the bidder accidentally uploaded another entity's certificate or altered the document."
                ))

            doc_name = (gst_ef.get("legal_name") or "").strip().lower()
            portal_name = (gst_portal.key_fields.get("legal_name") or "").strip().lower()
            
            # Substantial name variation check
            if doc_name and portal_name and doc_name != portal_name:
                # Check for subtle or severe discrepancy
                mismatches.append(CrossCheckMismatch(
                    field_name="Company Legal Name",
                    source_a_name="Uploaded GST Certificate",
                    source_a_value=gst_ef.get("legal_name"),
                    source_b_name="GST Portal Master Record",
                    source_b_value=gst_portal.key_fields.get("legal_name"),
                    severity=RiskLevel.HIGH,
                    discrepancy_explanation=f"Name mismatch detected: '{gst_ef.get('legal_name')}' vs '{gst_portal.key_fields.get('legal_name')}'.",
                    suggested_investigation="Check MCA incorporation history for recent name changes or constitution amendments."
                ))

        # 2. Financial Turnover Discrepancy (Balance Sheet vs GST Reported Turnover)
        if financial_doc and gst_portal:
            fin_ef = financial_doc.extracted_fields or {}
            doc_turnover = float(fin_ef.get("declared_turnover_inr", 0))
            portal_turnover = float(gst_portal.key_fields.get("annual_aggregate_turnover", 0))
            
            # If discrepancy > 30%, flag as high risk financial mismatch
            if doc_turnover > 0 and portal_turnover > 0:
                diff_ratio = abs(doc_turnover - portal_turnover) / max(doc_turnover, portal_turnover)
                if diff_ratio > 0.35:
                    mismatches.append(CrossCheckMismatch(
                        field_name="Annual Revenue / Turnover",
                        source_a_name="Audited Balance Sheet (OCR)",
                        source_a_value=f"₹{doc_turnover:,.2f}",
                        source_b_name="GSTN GSTR-3B Annual Aggregate Turnover",
                        source_b_value=f"₹{portal_turnover:,.2f}",
                        severity=RiskLevel.HIGH,
                        discrepancy_explanation=f"Declared audited revenue (₹{doc_turnover/1e7:.2f} Cr) is significantly higher than GST tax-declared turnover (₹{portal_turnover/1e7:.2f} Cr).",
                        suggested_investigation="Request CA UDIN verification certificate and reconciliation statement between GSTR-9 and Audited P&L."
                    ))

        # 3. Udyam MSME Category / Registration Check
        if udyam_doc and udyam_portal:
            ef = udyam_doc.extracted_fields or {}
            doc_udyam = (ef.get("udyam_registration_number") or "").strip().upper()
            portal_udyam = (udyam_portal.key_fields.get("udyam_registration_number") or "").strip().upper()
            
            if doc_udyam and portal_udyam and doc_udyam != portal_udyam:
                mismatches.append(CrossCheckMismatch(
                    field_name="Udyam Registration Number",
                    source_a_name="Uploaded Udyam Certificate",
                    source_a_value=doc_udyam,
                    source_b_name="Ministry of MSME Database",
                    source_b_value=portal_udyam,
                    severity=RiskLevel.CRITICAL,
                    discrepancy_explanation="Udyam Registration ID on certificate does not reconcile with the MSME portal record.",
                    suggested_investigation="Check if certificate is expired or re-registered under another category."
                ))

        # 4. PAN Status & Legal Name Cross Check with PAN Registry
        if pan_portal and gst_portal:
            pan_name = (pan_portal.key_fields.get("registered_name") or "").strip().lower()
            gst_legal_name = (gst_portal.key_fields.get("legal_name") or "").strip().lower()
            if pan_name and gst_legal_name and pan_name != gst_legal_name:
                mismatches.append(CrossCheckMismatch(
                    field_name="PAN Registered Name vs GST Legal Name",
                    source_a_name="NSDL Income Tax PAN Database",
                    source_a_value=pan_portal.key_fields.get("registered_name"),
                    source_b_name="GST Portal Master Record",
                    source_b_value=gst_portal.key_fields.get("legal_name"),
                    severity=RiskLevel.MEDIUM,
                    discrepancy_explanation="Spelling or structure mismatch between PAN database and GST record.",
                    suggested_investigation="Verify PAN verification certificate from IT Department."
                ))

        return mismatches
