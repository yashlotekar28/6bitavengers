from typing import Dict, Any
from datetime import datetime
from app.adapters.base import BasePortalAdapter
from app.models.schemas import PortalVerificationResult

class EPFOAdapter(BasePortalAdapter):
    @property
    def source_name(self) -> str:
        return "EPFO_PORTAL (Employees' Provident Fund Organisation)"

    async def verify(self, epfo_code: str, **kwargs) -> PortalVerificationResult:
        if not epfo_code:
            return PortalVerificationResult(
                source=self.source_name,
                status="NOT_APPLICABLE",
                key_fields={"epfo_code": None, "compliance_status": "EXEMPT_OR_NOT_PROVIDED"},
                raw_data={},
                response_time_ms=65
            )

        key_fields = {
            "establishment_code": epfo_code,
            "establishment_name": kwargs.get("company_name", "Apex InfraTech"),
            "status": "LIVE",
            "active_contributing_members": 48,
            "electronic_challan_cum_return_ecr_status": "UP_TO_DATE",
            "last_remittance_month": "July 2026",
            "statutory_dues_pending": False
        }

        return PortalVerificationResult(
            source=self.source_name,
            status="COMPLIANT",
            key_fields=key_fields,
            raw_data={"remittance_compliance_score": 100},
            verified_at=datetime.utcnow(),
            response_time_ms=115
        )

class MCA21Adapter(BasePortalAdapter):
    @property
    def source_name(self) -> str:
        return "MCA21 (Ministry of Corporate Affairs)"

    async def verify(self, cin: str, **kwargs) -> PortalVerificationResult:
        if not cin or len(cin) != 21:
            return PortalVerificationResult(
                source=self.source_name,
                status="NOT_REGISTERED_AS_CORP",
                key_fields={"cin": cin, "status": "NOT_APPLICABLE_OR_INVALID"},
                raw_data={},
                response_time_ms=50
            )

        key_fields = {
            "cin": cin,
            "company_name": kwargs.get("company_name", "Apex InfraTech Private Limited"),
            "roc_code": "ROC Mumbai",
            "company_status": "ACTIVE",
            "authorized_capital_inr": 20000000.0,
            "paid_up_capital_inr": 10000000.0,
            "date_of_incorporation": "2018-05-18",
            "active_charges_registered": 1,
            "defaulter_directors_count": 0,
            "annual_return_filed_fy": "2024-25"
        }

        return PortalVerificationResult(
            source=self.source_name,
            status="ACTIVE",
            key_fields=key_fields,
            raw_data={"roc_compliance_rate": "100%"},
            verified_at=datetime.utcnow(),
            response_time_ms=135
        )
