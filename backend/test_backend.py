import asyncio
import sys
import os

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.dirname(__file__))

from app.models.schemas import Bidder, RiskLevel
from app.main import app, BIDDERS_DB, populate_seed_scenarios, run_full_pipeline_for_bidder
from app.data.demo_scenarios import DEMO_BIDDERS_SEED

async def test_full_flow():
    print("=== Testing ProcureShield AI End-to-End Flow ===")
    
    # 1. Populate seeds
    populate_seed_scenarios()
    print(f"Loaded {len(BIDDERS_DB)} seed bidders.")
    assert len(BIDDERS_DB) == 3, "Expected 3 demo bidders"
    
    # 2. Run full pipeline for all 3 bidders
    for bidder_id, bidder in list(BIDDERS_DB.items()):
        seed_match = next(s for s in DEMO_BIDDERS_SEED if s["bidder_id"] == bidder_id)
        updated = await run_full_pipeline_for_bidder(bidder, scenario_type=seed_match["scenario_type"])
        
        print(f"\n--- Bidder: {updated.company_name} ({updated.bidder_id}) ---")
        print(f"  Score: {updated.compliance_score.score}/100 | Risk: {updated.compliance_score.risk_level}")
        print(f"  Hard Blocks Triggered: {updated.compliance_score.hard_blocks_triggered}")
        print(f"  Mismatches Detected: {len(updated.cross_check_mismatches)}")
        print(f"  Rules Passed: {sum(1 for r in updated.rule_results if r.passed)}/{len(updated.rule_results)}")
        print(f"  AI Recommended Action: {updated.ai_recommendation.recommended_action}")

    # Validate specific scenario expectations
    b1 = BIDDERS_DB["BID-2026-0891"] # Compliant
    assert b1.compliance_score.risk_level == RiskLevel.LOW
    assert b1.compliance_score.score >= 85
    assert len(b1.cross_check_mismatches) == 0

    b2 = BIDDERS_DB["BID-2026-0442"] # Mismatch
    assert b2.compliance_score.risk_level in (RiskLevel.MEDIUM, RiskLevel.HIGH)
    assert len(b2.cross_check_mismatches) > 0

    b3 = BIDDERS_DB["BID-2026-0109"] # Debarred
    assert b3.compliance_score.risk_level == RiskLevel.CRITICAL
    assert b3.compliance_score.hard_blocks_triggered > 0
    assert b3.ai_recommendation.recommended_action == "RECOMMEND_REJECTION"

    print("\n[PASS] All 10-step end-to-end pipeline checks PASSED successfully!")

if __name__ == "__main__":
    asyncio.run(test_full_flow())
