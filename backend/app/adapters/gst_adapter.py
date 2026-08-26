from typing import Dict, Any
from datetime import datetime
from app.adapters.base import BasePortalAdapter
from app.models.schemas import PortalVerificationResult

class GSTAdapter(BasePortalAdapter):
    @property
    def source_name(self) -> str:
        return "GST_PORTAL (API Setu / GSTN)"

    async def verify(self, gstin: str, **kwargs) -> PortalVerificationResult:
        if not gstin or len(gstin) != 15:
            return PortalVerificationResult(
                source=self.source_name,
                status="INVALID_FORMAT",
                key_fields={"gstin": gstin, "valid": False, "status": "INVALID"},
                raw_data={"error": "GSTIN must be a 15-character alphanumeric code"},
                response_time_ms=85
            )

        # Realistic simulated live API response logic (matches real GSTN schema via API Setu)
        is_active = not gstin.endswith("999") # Demo condition for inactive test
        state_code = gstin[:2]
        pan_in_gst = gstin[2:12]
        
        # Check simulated turnover and filing records
        filing_history = [
            {"return_type": "GSTR-3B", "tax_period": "012026", "status": "Filed", "filed_on": "2026-02-18"},
            {"return_type": "GSTR-3B", "tax_period": "122025", "status": "Filed", "filed_on": "2026-01-20"},
            {"return_type": "GSTR-3B", "tax_period": "112025", "status": "Filed", "filed_on": "2025-12-19"}
        ]
        
        # Simulate late filing or default scenario for demo
        if "MISMATCH" in kwargs.get("scenario_hint", ""):
            filing_history[0]["filed_on"] = "2026-03-05" # Late filed
            annual_turnover_declared = 12000000.0 # 1.2 Cr in GST vs 4.5 Cr in Balance Sheet
        else:
            annual_turnover_declared = kwargs.get("expected_turnover", 45000000.0)

        key_fields = {
            "gstin": gstin,
            "legal_name": kwargs.get("company_name", "Apex InfraTech Private Limited"),
            "trade_name": kwargs.get("company_name", "Apex InfraTech"),
            "status": "Active" if is_active else "Suspended/Cancelled",
            "registration_date": "2018-06-14",
            "taxpayer_type": "Regular",
            "state_jurisdiction": f"State Code {state_code}",
            "pan_extracted": pan_in_gst,
            "turnover_bracket": "1.5 Cr to 5 Cr" if annual_turnover_declared < 50000000 else "5 Cr to 25 Cr",
            "annual_aggregate_turnover": annual_turnover_declared,
            "last_3_gstr3b_filed": True,
            "e_way_bill_blocked": False
        }

        return PortalVerificationResult(
            source=self.source_name,
            status="ACTIVE" if is_active else "SUSPENDED",
            key_fields=key_fields,
            raw_data={
                "gstin": gstin,
                "auth_status": "AUTHENTICATED_API_SETU",
                "filings": filing_history,
                "compliance_rating": "HIGH" if is_active else "LOW"
            },
            verified_at=datetime.utcnow(),
            response_time_ms=145
        )
