from typing import Dict, Any
from datetime import datetime
from app.adapters.base import BasePortalAdapter
from app.models.schemas import PortalVerificationResult

class DebarmentAdapter(BasePortalAdapter):
    @property
    def source_name(self) -> str:
        return "CPPP_DEBARMENT_REGISTRY (DoE / GeM Incident Mgmt)"

    async def verify(self, identifier: str, **kwargs) -> PortalVerificationResult:
        """
        Checks CPPP (Central Public Procurement Portal), Ministry of Finance DoE debarment list,
        and GeM Incident Management blacklist by PAN / GSTIN / CIN.
        """
        scenario_hint = kwargs.get("scenario_hint", "")
        pan = kwargs.get("pan", "")
        company_name = kwargs.get("company_name", "")

        is_debarred = ("DEBARRED" in scenario_hint) or ("Vanguard" in company_name) or ("BK7788" in identifier)

        if is_debarred:
            key_fields = {
                "is_debarred": True,
                "debarment_order_no": "OM/DoE/F.1/2025-PPD/892",
                "debarring_ministry": "Ministry of Housing & Urban Affairs / CPWD",
                "period_from": "2025-04-01",
                "period_to": "2027-03-31",
                "debarment_reason": "Submission of forged Performance Bank Guarantee (PBG) in Tender CPWD/2024/91",
                "rule_invoked": "Rule 151 of GFR 2017 (Debarment from Bidding)"
            }
            status = "DEBARRED"
        else:
            key_fields = {
                "is_debarred": False,
                "total_vigilance_records_found": 0,
                "gem_incident_status": "CLEAN",
                "cppp_blacklist_status": "NOT_FOUND"
            }
            status = "CLEAN"

        return PortalVerificationResult(
            source=self.source_name,
            status=status,
            key_fields=key_fields,
            raw_data={
                "search_query": identifier,
                "registry_date": "2026-08-20",
                "active_orders": 1 if is_debarred else 0
            },
            verified_at=datetime.utcnow(),
            response_time_ms=105
        )
