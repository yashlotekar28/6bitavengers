from typing import List, Dict, Any
from app.models.schemas import (
    RuleEvaluationResult,
    CrossCheckMismatch,
    ComplianceScore,
    RiskLevel
)

class ComplianceScoringEngine:
    """
    Step 7: Compliance Scoring Function.
    Combines deterministic rules (mandatory gates) with soft factors and AI-detected risk mismatches.
    Produces a composite 0-100 score and categorical Risk Tier.
    """

    @staticmethod
    def calculate_score(
        rule_results: List[RuleEvaluationResult],
        mismatches: List[CrossCheckMismatch]
    ) -> ComplianceScore:
        base_score = 100
        
        mandatory_rules = [r for r in rule_results if r.is_hard_block]
        mandatory_passed = [r for r in mandatory_rules if r.passed]
        hard_blocks_triggered = len(mandatory_rules) - len(mandatory_passed)
        
        soft_rules = [r for r in rule_results if not r.is_hard_block]
        soft_failed = [r for r in soft_rules if not r.passed]
        
        # Calculate penalties
        soft_penalty = len(soft_failed) * 10
        
        critical_mismatches = [m for m in mismatches if m.severity == RiskLevel.CRITICAL]
        high_mismatches = [m for m in mismatches if m.severity == RiskLevel.HIGH]
        medium_mismatches = [m for m in mismatches if m.severity == RiskLevel.MEDIUM]
        
        mismatches_penalty = (len(critical_mismatches) * 30) + (len(high_mismatches) * 15) + (len(medium_mismatches) * 5)
        
        calculated = base_score - soft_penalty - mismatches_penalty

        # Hard blocks strictly cap the score
        if hard_blocks_triggered > 0:
            final_score = min(25, max(5, calculated - (hard_blocks_triggered * 40)))
            risk_level = RiskLevel.CRITICAL
        else:
            final_score = max(10, min(100, calculated))
            if final_score >= 85:
                risk_level = RiskLevel.LOW
            elif final_score >= 65:
                risk_level = RiskLevel.MEDIUM
            elif final_score >= 40:
                risk_level = RiskLevel.HIGH
            else:
                risk_level = RiskLevel.CRITICAL

        score_breakdown = {
            "base_points": 100,
            "mandatory_compliance_status": "ALL_PASSED" if hard_blocks_triggered == 0 else f"{hard_blocks_triggered}_FAILED",
            "soft_rules_penalty": f"-{soft_penalty}",
            "data_mismatch_penalty": f"-{mismatches_penalty}",
            "final_computed_score": final_score
        }

        return ComplianceScore(
            score=final_score,
            risk_level=risk_level,
            hard_blocks_triggered=hard_blocks_triggered,
            mandatory_rules_passed=len(mandatory_passed),
            mandatory_rules_total=len(mandatory_rules),
            soft_factors_penalty=soft_penalty,
            mismatches_penalty=mismatches_penalty,
            score_breakdown=score_breakdown
        )
