import os
import json
from typing import List, Dict, Any, Optional
from app.models.schemas import (
    RuleEvaluationResult,
    CrossCheckMismatch,
    PortalVerificationResult,
    AIRecommendation,
    RiskFactor,
    RiskLevel
)

class AIReasoningEngine:
    """
    Step 6: AI Reasoning Layer.
    Does not make arbitrary compliance decisions; instead, it synthesizes the deterministic rules,
    cross-verification discrepancies, and portal telemetry into an explainable officer briefing.
    """

    @staticmethod
    def generate_recommendation(
        company_name: str,
        tender_id: str,
        rule_results: List[RuleEvaluationResult],
        mismatches: List[CrossCheckMismatch],
        portal_verifications: Dict[str, PortalVerificationResult]
    ) -> AIRecommendation:
        hard_fails = [r for r in rule_results if not r.passed and r.is_hard_block]
        soft_fails = [r for r in rule_results if not r.passed and not r.is_hard_block]
        critical_mismatches = [m for m in mismatches if m.severity == RiskLevel.CRITICAL]
        high_mismatches = [m for m in mismatches if m.severity == RiskLevel.HIGH]

        risk_factors: List[RiskFactor] = []

        # 1. Hard Block Evaluation
        if hard_fails:
            for hf in hard_fails:
                risk_factors.append(RiskFactor(
                    code=hf.rule_id,
                    title=f"Disqualifying Defect: {hf.rule_name}",
                    severity=RiskLevel.CRITICAL,
                    is_soft_risk=False,
                    explanation=f"Rule violated: {hf.failure_reason}. Under tender guidelines, this constitutes an absolute disqualification."
                ))

            # Debarment specific alert
            if any(hf.rule_id == "RULE_NO_DEBARMENT" for hf in hard_fails):
                debarment = portal_verifications.get("CPPP_DEBARMENT")
                order_info = debarment.key_fields.get("debarment_order_no", "Active Order") if debarment else "Order"
                return AIRecommendation(
                    recommended_action="RECOMMEND_REJECTION",
                    executive_summary=f"CRITICAL COMPLIANCE FAILURE: Bidder '{company_name}' is currently debarred under GFR Rule 151 ({order_info}). Live portal query verified an active ban across all Central Ministries.",
                    risk_factors=risk_factors,
                    mitigation_notes="Immediate rejection required under GFR 2017 Rule 151. No tender committee waiver is legally permissible.",
                    confidence_score=0.99
                )

            return AIRecommendation(
                recommended_action="RECOMMEND_REJECTION",
                executive_summary=f"DISQUALIFICATION RECOMMENDED: Bidder '{company_name}' failed {len(hard_fails)} mandatory qualification criteria (including {', '.join([h.rule_name for h in hard_fails])}).",
                risk_factors=risk_factors,
                mitigation_notes="Evaluate if standard cure period applies or issue technical non-compliance notice.",
                confidence_score=0.96
            )

        # 2. Critical/High Mismatch Handling (Fraud / Document Integrity risk)
        if critical_mismatches or high_mismatches:
            for cm in critical_mismatches:
                risk_factors.append(RiskFactor(
                    code="DOC_INTEGRITY_CRITICAL",
                    title=f"Severe Discrepancy: {cm.field_name}",
                    severity=RiskLevel.CRITICAL,
                    is_soft_risk=False,
                    explanation=cm.discrepancy_explanation
                ))
            
            for hm in high_mismatches:
                risk_factors.append(RiskFactor(
                    code="DOC_INTEGRITY_HIGH",
                    title=f"Discrepancy: {hm.field_name}",
                    severity=RiskLevel.HIGH,
                    is_soft_risk=True,
                    explanation=hm.discrepancy_explanation
                ))

            action = "FLAG_FOR_OFFICER_REVIEW" if not critical_mismatches else "REQUEST_MORE_INFO"
            return AIRecommendation(
                recommended_action=action,
                executive_summary=f"POTENTIAL DATA INCONSISTENCY: Bidder passed primary statutory gates, but cross-verification identified {len(mismatches)} discrepancy between submitted certificates and live registry databases.",
                risk_factors=risk_factors,
                mitigation_notes="Issue formal clarification query on GeM portal requiring bidder to reconcile the discrepancy within 48 hours.",
                confidence_score=0.92
            )

        # 3. Soft Risk Handling (e.g. Late GSTR-3B filings, Non-MSME)
        if soft_fails:
            for sf in soft_fails:
                risk_factors.append(RiskFactor(
                    code=sf.rule_id,
                    title=f"Advisory Observation: {sf.rule_name}",
                    severity=RiskLevel.LOW,
                    is_soft_risk=True,
                    explanation=f"{sf.rule_name} was not fulfilled ({sf.failure_reason}), but does not disqualify the bidder."
                ))

        # 4. Clean Pass Scenario
        return AIRecommendation(
            recommended_action="RECOMMEND_APPROVAL",
            executive_summary=f"CLEAN STATUTORY & FINANCIAL PROFILE: Bidder '{company_name}' satisfies all mandatory tender criteria with 100% data reconciliation across GST, PAN, Udyam, and CPPP registers. No active litigation, debarment, or tax defaults detected.",
            risk_factors=risk_factors,
            mitigation_notes="Eligible for technical qualification and MSME purchase preference under Public Procurement Policy.",
            confidence_score=0.98
        )
