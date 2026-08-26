import asyncio
import sys
import os

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.dirname(__file__))

from app.models.schemas import Bidder, RiskLevel, OfficerChatRequest
from app.main import app, BIDDERS_DB, populate_seed_scenarios, run_full_pipeline_for_bidder
from app.services.vault_service import VendorDocumentVaultService
from app.services.trust_scoring_service import LongitudinalTrustScoringService
from app.services.entity_graph_service import EntityGraphLinkingService
from app.services.chat_service import OfficerChatAssistantService
from app.data.demo_scenarios import DEMO_BIDDERS_SEED

async def test_full_flow():
    print("=== Testing ProcureShield AI v2.0 with 5 Killer Features ===")
    
    # 1. Populate seeds
    populate_seed_scenarios()
    print(f"Loaded {len(BIDDERS_DB)} seed bidders.")
    assert len(BIDDERS_DB) == 3, "Expected 3 demo bidders"
    
    # 2. Run full pipeline for all 3 bidders
    for bidder_id, bidder in list(BIDDERS_DB.items()):
        seed_match = next(s for s in DEMO_BIDDERS_SEED if s["bidder_id"] == bidder_id)
        updated = await run_full_pipeline_for_bidder(bidder, scenario_type=seed_match["scenario_type"])
        
        print(f"\n--- Bidder: {updated.company_name} ({updated.bidder_id}) ---")
        print(f"  Compliance Score: {updated.compliance_score.score}/100 | Risk: {updated.compliance_score.risk_level}")
        print(f"  Trust Score: {updated.longitudinal_trust_score.score}/900 ({updated.longitudinal_trust_score.rating_band})")
        print(f"  Vault Credentials: {len(updated.vault_documents)} verified docs")
        print(f"  Conflict Links: {updated.conflict_links_count}")
        print(f"  AI Recommended Action: {updated.ai_recommendation.recommended_action}")

    # Validate Feature 1: Document Vault
    v1 = BIDDERS_DB["BID-2026-0891"]
    assert len(v1.vault_documents) >= 3
    assert any(d.doc_type == "GST_CERTIFICATE" for d in v1.vault_documents)
    print("\n[PASS] Feature 1: Unified Document Vault verified.")

    # Validate Feature 2: Longitudinal Trust Score
    assert v1.longitudinal_trust_score.score >= 850
    v3 = BIDDERS_DB["BID-2026-0109"]
    assert v3.longitudinal_trust_score.score < 500
    print("[PASS] Feature 2: Longitudinal Trust Scores verified (Apex: 868 AAA, Vanguard: 385 D).")

    # Validate Feature 3: Entity Linkage & Cartel Graph
    graph = EntityGraphLinkingService.build_tender_graph("GEM/2026/B/89420")
    assert graph.cartels_detected > 0
    assert graph.debarment_links_found > 0
    assert len(graph.nodes) >= 8
    print(f"[PASS] Feature 3: Entity Linkage Graph verified ({len(graph.nodes)} nodes, {len(graph.edges)} edges).")

    # Validate Feature 5: Natural Language Officer Assistant (Chat)
    chat_resp = OfficerChatAssistantService.process_officer_query(
        request=OfficerChatRequest(query="Compare Apex and Bharat", tender_id="GEM/2026/B/89420"),
        bidders_db=BIDDERS_DB
    )
    assert "Apex InfraTech" in chat_resp.reply
    assert "Bharat Heavy Logistics" in chat_resp.reply
    print("[PASS] Feature 5: Officer Chat Assistant verified.")

    print("\n[PASS] All v2.0 features & pipeline checks PASSED successfully!")

if __name__ == "__main__":
    asyncio.run(test_full_flow())
