from typing import Dict, Any
from datetime import datetime
from app.adapters.base import BasePortalAdapter
from app.models.schemas import PortalVerificationResult

class UdyamAdapter(BasePortalAdapter):
    @property
    def source_name(self) -> str:
        return "UDYAM_MSME_PORTAL (Ministry of MSME)"

    async def verify(self, udyam_no: str, **kwargs) -> PortalVerificationResult:
        if not udyam_no or not udyam_no.startswith("UDYAM-"):
            return PortalVerificationResult(
                source=self.source_name,
                status="NOT_REGISTERED",
                key_fields={"udyam_number": udyam_no, "is_msme": False},
                raw_data={"error": "Not a valid Udyam Registration format"},
                response_time_ms=90
            )

        scenario_hint = kwargs.get("scenario_hint", "")
        # Scenario 2 might simulate a subtle discrepancy in unit address or enterprise type
        enterprise_type = "SMALL" if "MISMATCH" in scenario_hint else "MICRO"

        key_fields = {
            "udyam_registration_number": udyam_no,
            "enterprise_name": kwargs.get("company_name", "Apex InfraTech Private Limited"),
            "enterprise_type": enterprise_type,
            "major_activity": "SERVICES",
            "social_category": "General",
            "date_of_commencement": "2018-07-01",
            "nic_2_digit_code": "62 - Computer programming, consultancy and related activities",
            "investment_in_plant_machinery_lakhs": 42.5,
            "msme_reservation_eligible": True,
            "is_active_msme": True
        }

        return PortalVerificationResult(
            source=self.source_name,
            status="VERIFIED_MSME",
            key_fields=key_fields,
            raw_data={
                "udyam_no": udyam_no,
                "portal_validation": "SUCCESS",
                "msme_samadhaan_pending_cases": 0
            },
            verified_at=datetime.utcnow(),
            response_time_ms=130
        )
