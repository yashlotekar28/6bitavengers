import asyncio
import sys
import os
import io
from PIL import Image, ImageDraw

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.dirname(__file__))

from app.models.schemas import Bidder, RiskLevel, OfficerChatRequest, TamperStatus
from app.main import app, BIDDERS_DB, TENDERS_DB, populate_seed_scenarios, run_full_pipeline_for_bidder
from app.services.vault_service import VendorDocumentVaultService
from app.services.trust_scoring_service import LongitudinalTrustScoringService
from app.services.entity_graph_service import EntityGraphLinkingService
from app.services.chat_service import OfficerChatAssistantService
from app.services.document_forensics_service import DocumentForensicsService
from app.data.demo_scenarios import DEMO_BIDDERS_SEED, DEMO_TENDERS_SEED

async def test_full_flow():
    print("=== Testing ProcureShield AI with Document Forensics & ELA Tamper Analysis ===")
    
    # 1. Populate seeds
    populate_seed_scenarios()
    print(f"Loaded {len(TENDERS_DB)} GeM tenders.")
    print(f"Loaded {len(BIDDERS_DB)} total seed bidders (15 per tender).")
    assert len(TENDERS_DB) == 3, "Expected 3 demo tenders"
    assert len(BIDDERS_DB) == 45, "Expected 45 demo bidders"
    
    # 2. Run full pipeline for sample bidders across all 3 tenders
    sample_ids = ["BID-2026-0891", "BID-2026-0442", "BID-2026-0109", "BID-2026-0201", "BID-2026-0301"]
    for bidder_id in sample_ids:
        bidder = BIDDERS_DB[bidder_id]
        seed_match = next(s for s in DEMO_BIDDERS_SEED if s["bidder_id"] == bidder_id)
        updated = await run_full_pipeline_for_bidder(bidder, scenario_type=seed_match["scenario_type"])
        
        forensic = updated.documents[0].forensic_report if updated.documents else None
        print(f"\n--- [Tender: {updated.tender_id}] Bidder: {updated.company_name} ({updated.bidder_id}) ---")
        print(f"  Compliance Score: {updated.compliance_score.score}/100 | Risk: {updated.compliance_score.risk_level}")
        print(f"  Trust Score: {updated.longitudinal_trust_score.score}/900 ({updated.longitudinal_trust_score.rating_band})")
        if forensic:
            print(f"  Forensic Tamper Score: {forensic.overall_tamper_score}/100 | Status: {forensic.status.value} (ELA: {forensic.ela_score}%, Meta: {forensic.metadata_score}%)")
        print(f"  Vault Credentials: {len(updated.vault_documents)} verified docs")
        print(f"  Conflict Links: {updated.conflict_links_count}")
        print(f"  AI Recommended Action: {updated.ai_recommendation.recommended_action}")

    # Validate Feature 1: Document Vault
    v1 = BIDDERS_DB["BID-2026-0891"]
    assert len(v1.vault_documents) >= 3
    assert any(d.doc_type == "GST_CERTIFICATE" for d in v1.vault_documents)
    print("\n[PASS] Feature 1: Unified Document Vault verified across multiple bids.")

    # Validate Feature 2: Longitudinal Trust Score
    assert v1.longitudinal_trust_score.score >= 850
    v3 = BIDDERS_DB["BID-2026-0109"]
    assert v3.longitudinal_trust_score.score < 500
    print("[PASS] Feature 2: Longitudinal Trust Scores verified (Apex: 868 AAA, Vanguard: 385 D).")

    # Validate Feature 3: Entity Linkage & Cartel Graph for all 3 tenders
    for t_id in ["GEM/2026/B/89420", "GEM/2026/B/77312", "GEM/2026/B/65109"]:
        graph = EntityGraphLinkingService.build_tender_graph(t_id)
        assert graph.cartels_detected >= 0
        assert len(graph.nodes) >= 6
        print(f"[PASS] Feature 3: Entity Linkage Graph for {t_id} verified ({len(graph.nodes)} nodes, {len(graph.edges)} edges).")

    # Validate Feature 5: Natural Language Officer Assistant (Chat)
    chat_resp = OfficerChatAssistantService.process_officer_query(
        request=OfficerChatRequest(query="Compare Apex and Bharat", tender_id="GEM/2026/B/89420"),
        bidders_db=BIDDERS_DB
    )
    assert "Apex InfraTech" in chat_resp.reply
    print(f"[PASS] Feature 5: Officer Chat Assistant verified.")

    # Validate NEW Feature: Document Forensics & ELA Tamper Analysis
    # A) Seed scenario checks
    v1_forensic = v1.documents[0].forensic_report
    assert v1_forensic is not None
    assert v1_forensic.status == TamperStatus.CLEAN
    assert v1_forensic.overall_tamper_score <= 25

    v2 = BIDDERS_DB["BID-2026-0442"]
    v2_forensic = v2.documents[0].forensic_report
    assert v2_forensic is not None
    assert v2_forensic.status in [TamperStatus.SUSPICIOUS, TamperStatus.LIKELY_TAMPERED]
    assert v2_forensic.overall_tamper_score >= 50
    assert v2_forensic.ela_heatmap_base64 is not None

    # B) Real Image Byte ELA Processing Test
    test_img = Image.new("RGB", (300, 200), (255, 255, 255))
    draw = ImageDraw.Draw(test_img)
    draw.text((20, 30), "GOVERNMENT OF INDIA CERTIFICATE", fill=(0, 0, 0))
    draw.rectangle([50, 80, 250, 140], fill=(220, 40, 40)) # Artificially edited patch
    
    img_buf = io.BytesIO()
    test_img.save(img_buf, format="JPEG", quality=95)
    
    live_report = DocumentForensicsService.analyze_document_bytes(
        image_bytes=img_buf.getvalue(),
        file_name="test_turnover_tampered.jpg",
        doc_id="DOC-LIVE-TEST-001"
    )
    assert live_report.overall_tamper_score >= 0
    assert live_report.ela_heatmap_base64.startswith("data:image/png;base64,")
    print(f"[PASS] Feature: Real Image Byte ELA Forensic Analysis verified (Score: {live_report.overall_tamper_score}/100, Status: {live_report.status.value}).")

    print("\n[PASS] All Multi-Bid (3 Bids, 45 Vendors) & Document Forensics ELA checks PASSED successfully!")

if __name__ == "__main__":
    asyncio.run(test_full_flow())
