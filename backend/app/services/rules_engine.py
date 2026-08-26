import os
import yaml
from typing import List, Dict, Any
from app.models.schemas import (
    RuleEvaluationResult,
    PortalVerificationResult,
    CrossCheckMismatch,
    BidderFinancials,
    RiskLevel
)

class DeterministicRulesEngine:
    """
    Step 5: Deterministic Rules Engine (Mechanical Pass/Fail Evaluation).
    Evaluates tender rules against normalized bidder profile data with zero ambiguity or hallucination.
    """

    def __init__(self, rules_file_path: str = None):
        if not rules_file_path:
            base_dir = os.path.dirname(os.path.dirname(__file__))
            rules_file_path = os.path.join(base_dir, "rules", "tender_rules_default.yaml")
        
        self.rules_file_path = rules_file_path
        self.rules_config = self._load_rules()

    def _load_rules(self) -> Dict[str, Any]:
        if os.path.exists(self.rules_file_path):
            with open(self.rules_file_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        return {"rules": [], "min_annual_turnover_inr": 20000000.0}

    def evaluate_rules(
        self,
        portal_verifications: Dict[str, PortalVerificationResult],
        financials: BidderFinancials,
        mismatches: List[CrossCheckMismatch]
    ) -> List[RuleEvaluationResult]:
        results: List[RuleEvaluationResult] = []
        rules = self.rules_config.get("rules", [])

        gst_portal = portal_verifications.get("GST_PORTAL")
        pan_portal = portal_verifications.get("PAN_REGISTRY")
        debarment_portal = portal_verifications.get("CPPP_DEBARMENT")
        udyam_portal = portal_verifications.get("UDYAM_PORTAL")

        for r in rules:
            rule_id = r.get("id")
            rule_name = r.get("name")
            category = r.get("category", "STATUTORY")
            is_hard_block = r.get("is_hard_block", False)
            failure_message = r.get("failure_message", "Requirement condition not satisfied.")

            if rule_id == "RULE_NO_DEBARMENT":
                is_debarred = debarment_portal.key_fields.get("is_debarred", False) if debarment_portal else False
                passed = (is_debarred is False)
                results.append(RuleEvaluationResult(
                    rule_id=rule_id,
                    rule_name=rule_name,
                    category=category,
                    passed=passed,
                    is_hard_block=is_hard_block,
                    expected_condition="is_debarred == False",
                    actual_value=f"is_debarred={is_debarred}",
                    failure_reason=failure_message if not passed else None
                ))

            elif rule_id == "RULE_ACTIVE_GST":
                gst_status = gst_portal.key_fields.get("status", "INACTIVE") if gst_portal else "NOT_FOUND"
                passed = (gst_status == "Active" or gst_status == "ACTIVE")
                results.append(RuleEvaluationResult(
                    rule_id=rule_id,
                    rule_name=rule_name,
                    category=category,
                    passed=passed,
                    is_hard_block=is_hard_block,
                    expected_condition="status == 'Active'",
                    actual_value=gst_status,
                    failure_reason=failure_message if not passed else None
                ))

            elif rule_id == "RULE_GSTR3B_FILING":
                gstr3b_ok = gst_portal.key_fields.get("last_3_gstr3b_filed", False) if gst_portal else False
                results.append(RuleEvaluationResult(
                    rule_id=rule_id,
                    rule_name=rule_name,
                    category=category,
                    passed=gstr3b_ok,
                    is_hard_block=is_hard_block,
                    expected_condition="last_3_gstr3b_filed == True",
                    actual_value=f"filed={gstr3b_ok}",
                    failure_reason=failure_message if not gstr3b_ok else None
                ))

            elif rule_id == "RULE_VALID_PAN":
                pan_status = pan_portal.key_fields.get("pan_status", "INVALID") if pan_portal else "NOT_FOUND"
                is_defaulter = pan_portal.key_fields.get("tax_defaulter_section_206ab", False) if pan_portal else False
                passed = (pan_status == "EXISTING_AND_VALID" and not is_defaulter)
                results.append(RuleEvaluationResult(
                    rule_id=rule_id,
                    rule_name=rule_name,
                    category=category,
                    passed=passed,
                    is_hard_block=is_hard_block,
                    expected_condition="pan_status == 'VALID' AND sec_206ab_defaulter == False",
                    actual_value=f"{pan_status} (Defaulter: {is_defaulter})",
                    failure_reason=failure_message if not passed else None
                ))

            elif rule_id == "RULE_MIN_TURNOVER":
                min_threshold = float(r.get("threshold_min", 20000000.0))
                # Check verified turnover or declared turnover
                turnover = financials.annual_turnover_inr
                passed = (turnover >= min_threshold)
                results.append(RuleEvaluationResult(
                    rule_id=rule_id,
                    rule_name=rule_name,
                    category=category,
                    passed=passed,
                    is_hard_block=is_hard_block,
                    expected_condition=f"turnover >= ₹{min_threshold/1e7:.2f} Cr",
                    actual_value=f"₹{turnover/1e7:.2f} Cr",
                    failure_reason=failure_message if not passed else None
                ))

            elif rule_id == "RULE_MSME_BENEFITS":
                udyam_status = udyam_portal.status if udyam_portal else "NOT_REGISTERED"
                is_msme = (udyam_status == "VERIFIED_MSME")
                results.append(RuleEvaluationResult(
                    rule_id=rule_id,
                    rule_name=rule_name,
                    category=category,
                    passed=is_msme,
                    is_hard_block=is_hard_block,
                    expected_condition="status == 'VERIFIED_MSME'",
                    actual_value=udyam_status,
                    failure_reason=failure_message if not is_msme else None
                ))

            elif rule_id == "RULE_DOC_PORTAL_INTEGRITY":
                critical_mismatches = [m for m in mismatches if m.severity == RiskLevel.CRITICAL]
                passed = (len(critical_mismatches) == 0)
                results.append(RuleEvaluationResult(
                    rule_id=rule_id,
                    rule_name=rule_name,
                    category=category,
                    passed=passed,
                    is_hard_block=is_hard_block,
                    expected_condition="critical_mismatches == 0",
                    actual_value=f"{len(critical_mismatches)} critical mismatch(es)",
                    failure_reason=failure_message if not passed else None
                ))

        return results
