from typing import Dict, Any
from datetime import datetime
from app.adapters.base import BasePortalAdapter
from app.models.schemas import PortalVerificationResult

class PANAdapter(BasePortalAdapter):
    @property
    def source_name(self) -> str:
        return "PAN_REGISTRY (Income Tax Dept / NSDL)"

    async def verify(self, pan: str, **kwargs) -> PortalVerificationResult:
        if not pan or len(pan) != 10:
            return PortalVerificationResult(
                source=self.source_name,
                status="INVALID_FORMAT",
                key_fields={"pan": pan, "valid": False},
                raw_data={"error": "PAN must be a 10-character alphanumeric string"},
                response_time_ms=70
            )

        is_blacklisted = kwargs.get("is_blacklisted", False)
        scenario_hint = kwargs.get("scenario_hint", "")
        
        # Determine status
        if is_blacklisted or "DEBARRED" in scenario_hint:
            pan_status = "OPERATIVE_WITH_PROCEEDINGS"
            aadhaar_seeding = "FAILED"
        else:
            pan_status = "EXISTING_AND_VALID"
            aadhaar_seeding = "LINKED"

        key_fields = {
            "pan": pan,
            "pan_status": pan_status,
            "category": "Company" if pan[3].upper() == 'C' else "Firm" if pan[3].upper() == 'F' else "Individual",
            "registered_name": kwargs.get("company_name", "Apex InfraTech Private Limited"),
            "pan_allotment_date": "2018-05-10",
            "aadhaar_seeding_status": aadhaar_seeding,
            "tax_defaulter_section_206ab": False if not is_blacklisted else True
        }

        return PortalVerificationResult(
            source=self.source_name,
            status="VALID" if pan_status == "EXISTING_AND_VALID" else "FLAGGED",
            key_fields=key_fields,
            raw_data={
                "pan": pan,
                "response_code": "200",
                "nsdl_trace_id": f"NSDL-{pan}-2026",
                "sec_206ab_compliant": not is_blacklisted
            },
            verified_at=datetime.utcnow(),
            response_time_ms=110
        )
