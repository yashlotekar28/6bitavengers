import asyncio
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks, Depends
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from app.models.schemas import (
    Tender,
    Bidder,
    BidderIdentifiers,
    BidderFinancials,
    DocumentType,
    OfficerDecisionPayload,
    OfficerActionType,
    AuditLogEntry,
    ComplianceScore,
    RiskLevel,
    VendorVault,
    LongitudinalTrustScore,
    EntityGraph,
    OfficerChatRequest,
    OfficerChatResponse,
    DirectorInfo,
    DocumentForensicReport,
    TamperStatus
)
from app.adapters.gst_adapter import GSTAdapter
from app.adapters.pan_adapter import PANAdapter
from app.adapters.udyam_adapter import UdyamAdapter
from app.adapters.epfo_adapter import EPFOAdapter
from app.adapters.debarment_adapter import DebarmentAdapter
from app.services.ocr_extractor import DocumentIntelligenceEngine
from app.services.cross_verification import CrossVerificationEngine
from app.services.rules_engine import DeterministicRulesEngine
from app.services.ai_recommender import AIReasoningEngine
from app.services.scoring_engine import ComplianceScoringEngine
from app.services.audit_service import audit_trail
from app.services.vault_service import VendorDocumentVaultService
from app.services.trust_scoring_service import LongitudinalTrustScoringService, VendorTrackRecordService
from app.services.entity_graph_service import EntityGraphLinkingService
from app.services.chat_service import OfficerChatAssistantService
from app.services.document_forensics_service import DocumentForensicsService
from app.services.document_viewer_service import DocumentViewerService
from app.data.demo_scenarios import DEMO_BIDDERS_SEED, DEMO_TENDERS_SEED
try:
    from app.core.auth import authenticate_user, create_access_token, require_officer, require_auditor, TokenData
    AUTH_AVAILABLE = True
except Exception:
    AUTH_AVAILABLE = False

try:
    from app.tasks.verification_tasks import run_verification_pipeline
    CELERY_AVAILABLE = True
except Exception:
    CELERY_AVAILABLE = False

app = FastAPI(
    title="Nirikshan AI - GeM Bidder Verification Engine",
    description="Deterministic Rules & AI-powered Public Procurement Compliance Scoring System",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory databases
BIDDERS_DB: Dict[str, Bidder] = {}
TENDERS_DB: Dict[str, Tender] = {}

# Initialize Adapters & Services
gst_adapter = GSTAdapter()
pan_adapter = PANAdapter()
udyam_adapter = UdyamAdapter()
epfo_adapter = EPFOAdapter()
debarment_adapter = DebarmentAdapter()
rules_engine = DeterministicRulesEngine()

async def run_full_pipeline_for_bidder(bidder: Bidder, scenario_type: str = "") -> Bidder:
    """
    Executes the End-to-End 10-Step Verification Workflow with new capabilities.
    """
    # Feature 1: Populate & Sync Document Vault
    vault = VendorDocumentVaultService.get_vault_for_vendor(
        vendor_id=bidder.bidder_id,
        company_name=bidder.company_name,
        identifiers=bidder.identifiers.dict()
    )
    bidder.vault_documents = vault.documents

    # Feature 2: Compute Longitudinal Trust Score (CIBIL-style 300-900)
    trust_score = LongitudinalTrustScoringService.compute_trust_score(
        company_name=bidder.company_name,
        scenario_type=scenario_type
    )
    bidder.longitudinal_trust_score = trust_score

    # Feature: Multi-Year Historical Bidding & Contract Track Record
    track_record = VendorTrackRecordService.get_track_record_for_vendor(
        company_name=bidder.company_name,
        scenario_type=scenario_type,
        annual_turnover_inr=bidder.financials.annual_turnover_inr,
        registered_state=bidder.registered_state
    )
    bidder.track_record = track_record

    # Step 3: Concurrent Portal Verification (Process A)
    gst_task = gst_adapter.verify(
        bidder.identifiers.gstin or "",
        company_name=bidder.company_name,
        scenario_hint=scenario_type,
        expected_turnover=bidder.financials.annual_turnover_inr
    )
    pan_task = pan_adapter.verify(
        bidder.identifiers.pan or "",
        company_name=bidder.company_name,
        scenario_hint=scenario_type
    )
    udyam_task = udyam_adapter.verify(
        bidder.identifiers.udyam_registration_number or "",
        company_name=bidder.company_name,
        scenario_hint=scenario_type
    )
    epfo_task = epfo_adapter.verify(
        bidder.identifiers.epfo_code or "",
        company_name=bidder.company_name
    )
    debarment_task = debarment_adapter.verify(
        bidder.identifiers.pan or bidder.identifiers.gstin or "",
        company_name=bidder.company_name,
        scenario_hint=scenario_type
    )

    results = await asyncio.gather(gst_task, pan_task, udyam_task, epfo_task, debarment_task)

    bidder.portal_verifications = {
        "GST_PORTAL": results[0],
        "PAN_REGISTRY": results[1],
        "UDYAM_PORTAL": results[2],
        "EPFO_PORTAL": results[3],
        "CPPP_DEBARMENT": results[4]
    }

    # Step 4: Cross-Verification
    mismatches = CrossVerificationEngine.cross_check(bidder.documents, bidder.portal_verifications)
    bidder.cross_check_mismatches = mismatches

    # Step 5: Deterministic Rules Engine
    rule_results = rules_engine.evaluate_rules(
        portal_verifications=bidder.portal_verifications,
        financials=bidder.financials,
        mismatches=bidder.cross_check_mismatches
    )
    bidder.rule_results = rule_results

    # Step 6: AI Reasoning Layer
    ai_recommendation = AIReasoningEngine.generate_recommendation(
        company_name=bidder.company_name,
        tender_id=bidder.tender_id,
        rule_results=bidder.rule_results,
        mismatches=bidder.cross_check_mismatches,
        portal_verifications=bidder.portal_verifications
    )
    bidder.ai_recommendation = ai_recommendation

    # Step 7: Compliance Scoring
    compliance_score = ComplianceScoringEngine.calculate_score(
        rule_results=bidder.rule_results,
        mismatches=bidder.cross_check_mismatches
    )
    bidder.compliance_score = compliance_score

    # Step 10: Audit Log
    audit_trail.log_event(
        bidder_id=bidder.bidder_id,
        step="STEP_7_COMPLIANCE_EVALUATION",
        actor="SCORING_ENGINE",
        action_type="PIPELINE_COMPLETED",
        details={
            "compliance_score": compliance_score.score,
            "trust_score": trust_score.score,
            "risk_level": compliance_score.risk_level.value,
            "vault_docs_count": len(bidder.vault_documents),
            "conflict_links": bidder.conflict_links_count
        }
    )

    return bidder

def populate_seed_scenarios():
    """Initializes the 3 GeM Bids and 15 Vendors per Bid (45 Vendors Total)."""
    BIDDERS_DB.clear()
    TENDERS_DB.clear()

    # Seed Tenders
    for t_seed in DEMO_TENDERS_SEED:
        TENDERS_DB[t_seed["tender_id"]] = Tender(**t_seed)

    # Seed Bidders
    for seed in DEMO_BIDDERS_SEED:
        bidder_id = seed["bidder_id"]
        identifiers = BidderIdentifiers(**seed["identifiers"])
        financials = BidderFinancials(**seed["financials"])
        directors = [DirectorInfo(**d) for d in seed.get("directors", [])]
        
        # Step 2: Seed documents
        docs = []
        for doc_item in seed["documents_to_seed"]:
            doc = DocumentIntelligenceEngine.extract_document(
                bidder_id=bidder_id,
                doc_type=doc_item["type"],
                file_name=doc_item["name"],
                scenario_hint=seed["scenario_type"],
                custom_fields={
                    "company_name": seed["company_name"],
                    "gstin": identifiers.gstin,
                    "udyam_number": identifiers.udyam_registration_number,
                    "annual_turnover_inr": financials.annual_turnover_inr
                }
            )
            docs.append(doc)

        bidder = Bidder(
            bidder_id=bidder_id,
            tender_id=seed["tender_id"],
            company_name=seed["company_name"],
            legal_structure=seed["legal_structure"],
            registered_state=seed["registered_state"],
            registered_address=seed.get("registered_address", "Plot 45, Andheri East, Mumbai"),
            bank_branch_code=seed.get("bank_branch_code", "SBIN0004921"),
            conflict_links_count=seed.get("conflict_links_count", 0),
            directors=directors,
            identifiers=identifiers,
            financials=financials,
            documents=docs,
            officer_status="PENDING_REVIEW"
        )
        BIDDERS_DB[bidder_id] = bidder

def refresh_tender_statistics():
    """Recalculates dynamic compliance counts for each tender."""
    for t_id, tender in TENDERS_DB.items():
        tender_bidders = [b for b in BIDDERS_DB.values() if b.tender_id == t_id]
        tender.total_bidders = len(tender_bidders)
        tender.compliant_bidders = sum(1 for b in tender_bidders if b.compliance_score and b.compliance_score.risk_level == RiskLevel.LOW)
        tender.flagged_bidders = sum(1 for b in tender_bidders if b.compliance_score and b.compliance_score.risk_level in (RiskLevel.MEDIUM, RiskLevel.HIGH))
        tender.debarred_bidders = sum(1 for b in tender_bidders if b.compliance_score and b.compliance_score.risk_level == RiskLevel.CRITICAL)

@app.on_event("startup")
async def startup_event():
    populate_seed_scenarios()
    for bidder in list(BIDDERS_DB.values()):
        scenario_hint = next((s["scenario_type"] for s in DEMO_BIDDERS_SEED if s["bidder_id"] == bidder.bidder_id), "")
        await run_full_pipeline_for_bidder(bidder, scenario_type=scenario_hint)
    refresh_tender_statistics()

# --- Routes ---

@app.get("/", response_class=FileResponse)
async def serve_dashboard():
    static_file = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(static_file):
        return FileResponse(static_file)
    return {"message": "Nirikshan AI API Running"}

@app.get("/dashboard", response_class=FileResponse)
async def serve_dashboard_alias():
    static_file = os.path.join(os.path.dirname(__file__), "static", "index.html")
    return FileResponse(static_file)

@app.get("/login-bg.png")
@app.get("/static/login-bg.png")
async def serve_login_bg():
    bg_file = os.path.join(os.path.dirname(__file__), "static", "login-bg.png")
    if os.path.exists(bg_file):
        return FileResponse(bg_file, media_type="image/png")
    raise HTTPException(status_code=404, detail="Background image not found")


# Tender Endpoints
@app.get("/api/tenders", response_model=List[Tender])
async def list_tenders():
    refresh_tender_statistics()
    return list(TENDERS_DB.values())

@app.get("/api/tenders/{tender_id:path}", response_model=Tender)
async def get_tender(tender_id: str):
    refresh_tender_statistics()
    if tender_id not in TENDERS_DB:
        raise HTTPException(status_code=404, detail="Tender not found")
    return TENDERS_DB[tender_id]

@app.get("/api/tenders/{tender_id:path}/bidders", response_model=List[Bidder])
async def get_tender_bidders(tender_id: str):
    return [b for b in BIDDERS_DB.values() if b.tender_id == tender_id]

@app.get("/api/bidders", response_model=List[Bidder])
async def list_bidders(tender_id: Optional[str] = None):
    if tender_id:
        return [b for b in BIDDERS_DB.values() if b.tender_id == tender_id]
    return list(BIDDERS_DB.values())

@app.get("/api/bidders/{bidder_id}", response_model=Bidder)
async def get_bidder(bidder_id: str):
    if bidder_id not in BIDDERS_DB:
        raise HTTPException(status_code=404, detail="Bidder not found")
    return BIDDERS_DB[bidder_id]

@app.post("/api/bidders/verify/{bidder_id}", response_model=Bidder)
async def trigger_verification(bidder_id: str):
    if bidder_id not in BIDDERS_DB:
        raise HTTPException(status_code=404, detail="Bidder not found")
    bidder = BIDDERS_DB[bidder_id]
    scenario_hint = next((s["scenario_type"] for s in DEMO_BIDDERS_SEED if s["bidder_id"] == bidder.bidder_id), "")
    updated_bidder = await run_full_pipeline_for_bidder(bidder, scenario_type=scenario_hint)
    BIDDERS_DB[bidder_id] = updated_bidder
    return updated_bidder

@app.post("/api/bidders/reset-demo")
async def reset_demo():
    populate_seed_scenarios()
    for bidder in list(BIDDERS_DB.values()):
        scenario_hint = next((s["scenario_type"] for s in DEMO_BIDDERS_SEED if s["bidder_id"] == bidder.bidder_id), "")
        await run_full_pipeline_for_bidder(bidder, scenario_type=scenario_hint)
    return {"message": "Demo scenarios successfully reset and re-verified"}

# Feature 1 Endpoint: Vendor Document Vault
@app.get("/api/vault/{bidder_id}", response_model=VendorVault)
async def get_vendor_vault(bidder_id: str):
    if bidder_id not in BIDDERS_DB:
        raise HTTPException(status_code=404, detail="Bidder not found")
    bidder = BIDDERS_DB[bidder_id]
    return VendorDocumentVaultService.get_vault_for_vendor(
        vendor_id=bidder.bidder_id,
        company_name=bidder.company_name,
        identifiers=bidder.identifiers.dict()
    )

# Feature 2 Endpoint: Longitudinal Trust Score
@app.get("/api/trust-score/{bidder_id}", response_model=LongitudinalTrustScore)
async def get_vendor_trust_score(bidder_id: str):
    if bidder_id not in BIDDERS_DB:
        raise HTTPException(status_code=404, detail="Bidder not found")
    bidder = BIDDERS_DB[bidder_id]
    scenario_hint = next((s["scenario_type"] for s in DEMO_BIDDERS_SEED if s["bidder_id"] == bidder.bidder_id), "")
    return LongitudinalTrustScoringService.compute_trust_score(
        company_name=bidder.company_name,
        scenario_type=scenario_hint
    )

# Feature 3 Endpoint: Graph-Based Entity Linking
@app.get("/api/graph/tender/{tender_id:path}", response_model=EntityGraph)
async def get_tender_entity_graph(tender_id: str):
    return EntityGraphLinkingService.build_tender_graph(tender_id)

# --- Feature: Document Forensics & ELA Tamper Analysis Endpoints ---

@app.post("/api/forensics/analyze/{bidder_id}/{doc_id}", response_model=DocumentForensicReport, tags=["Forensics"])
async def analyze_document_forensics(bidder_id: str, doc_id: str):
    """
    Retrieves or executes 3-layer forensic tamper analysis (ELA + Metadata + Splice)
    for a specific uploaded document in a bidder dossier.
    """
    if bidder_id not in BIDDERS_DB:
        raise HTTPException(status_code=404, detail="Bidder not found")
    
    bidder = BIDDERS_DB[bidder_id]
    doc = next((d for d in bidder.documents if d.doc_id == doc_id), None)
    if not doc:
        if bidder.documents:
            doc = bidder.documents[0]
        else:
            raise HTTPException(status_code=404, detail="Document not found")
    
    if not doc.forensic_report:
        scenario_hint = next((s["scenario_type"] for s in DEMO_BIDDERS_SEED if s["bidder_id"] == bidder_id), "")
        doc.forensic_report = DocumentForensicsService.analyze_document_scenario(
            doc_id=doc.doc_id,
            doc_type=doc.doc_type,
            file_name=doc.file_name,
            scenario_hint=scenario_hint
        )
    
    return doc.forensic_report

@app.post("/api/forensics/upload-test", response_model=DocumentForensicReport, tags=["Forensics"])
async def upload_and_analyze_forensics(
    file: UploadFile = File(...),
    claimed_date: Optional[str] = Form(None)
):
    """
    LIVE DEMO FORENSIC LAB:
    Accepts real user-uploaded image/certificate (JPEG, PNG, etc.)
    and executes real Error Level Analysis (ELA), EXIF/metadata inspection,
    and copy-move splice detection in real-time.
    """
    content = await file.read()
    doc_id = f"TEST-FORENSIC-{datetime.utcnow().strftime('%M%S')}"
    
    report = DocumentForensicsService.analyze_document_bytes(
        image_bytes=content,
        file_name=file.filename or "uploaded_certificate.jpg",
        doc_id=doc_id,
        claimed_issue_date=claimed_date
    )
    
    # Append event to CAG Audit Trail
    audit_trail.log_event(
        bidder_id="LIVE_USER_UPLOAD",
        step="FORENSIC_TAMPER_ANALYSIS",
        actor="FORENSIC_ENGINE",
        action_type=f"SCAN_{report.status.value}",
        details={
            "file_name": file.filename,
            "overall_tamper_score": report.overall_tamper_score,
            "ela_score": report.ela_score,
            "metadata_score": report.metadata_score,
            "copy_move_score": report.copy_move_score,
            "flagged_regions": len(report.flagged_regions)
        },
        notes=report.forensic_summary
    )
    
    return report

# --- Feature: Visual Document Inspection Endpoint ---
@app.get("/api/documents/view/{bidder_id}", tags=["Documents"])
async def view_bidder_document(bidder_id: str, doc_type: Optional[str] = None):
    """
    Returns authentic rendered certificate layout data for Form GST REG-06,
    Udyam Registration, CA Turnover UDIN Statement, or Debarment Record.
    """
    if bidder_id not in BIDDERS_DB:
        raise HTTPException(status_code=404, detail="Bidder not found")
    
    bidder = BIDDERS_DB[bidder_id]
    return DocumentViewerService.get_document_view_data(bidder, doc_type)

@app.get("/api/bidders/{bidder_id}/gem-proposal-dossier", tags=["Documents"])
async def get_bidder_gem_proposal_dossier(bidder_id: str):
    """
    Returns the full, official 25-30 Page GeM Bid Proposal / Submission Document
    submitted by the vendor for the active bid, matching official GeM portal specs.
    """
    if bidder_id not in BIDDERS_DB:
        raise HTTPException(status_code=404, detail="Bidder not found")
    
    bidder = BIDDERS_DB[bidder_id]
    tender = TENDERS_DB.get(bidder.tender_id)
    tender_data = tender.dict() if tender else {}
    return DocumentViewerService.get_full_gem_bid_submission_dossier(bidder, tender_data)

# Feature 5 Endpoint: Natural Language Officer Assistant (Chat)
@app.post("/api/chat/officer", response_model=OfficerChatResponse)
async def chat_with_officer_assistant(request: OfficerChatRequest):
    # Fast-path: instant greeting response without thread overhead
    q_lower = request.query.strip().lower().strip("?.!, ")
    for greeting, resp_text in OfficerChatAssistantService._GREETINGS.items():
        if q_lower == greeting or q_lower.startswith(greeting + " ") or q_lower.endswith(" " + greeting):
            return OfficerChatResponse(
                reply=resp_text,
                context_used=["Nirikshan AI", "Instant Response"],
                suggested_actions=[
                    "List all vendors and their compliance scores",
                    "Which vendors are MSME eligible?",
                    "Who has the highest risk rating?"
                ]
            )
    # Slow-path: run in thread pool so Gemini's blocking HTTP call doesn't freeze the event loop
    return await asyncio.to_thread(
        OfficerChatAssistantService.process_officer_query,
        request=request,
        bidders_db=BIDDERS_DB
    )


@app.post("/api/officer/decision")
async def record_officer_decision(payload: OfficerDecisionPayload):
    if payload.bidder_id not in BIDDERS_DB:
        raise HTTPException(status_code=404, detail="Bidder not found")
    
    bidder = BIDDERS_DB[payload.bidder_id]
    bidder.officer_status = payload.action.value
    bidder.officer_notes = payload.comments
    bidder.officer_id = payload.officer_id
    bidder.decided_at = datetime.utcnow()

    # If action is APPROVE -> Automatically assign Priority 1 (L1 Confirmed) and queue eligible L2 & L3 Contingencies!
    if payload.action.value == "APPROVE":
        tender_id = bidder.tender_id
        
        # 1. Set Primary Confirmed L1
        bidder.award_priority = "PRIORITY_1_L1"
        bidder.award_status = "CONFIRMED_L1"
        
        # 2. Reset any previous contingency allocations in this tender
        other_bidders = [b for b in BIDDERS_DB.values() if b.tender_id == tender_id and b.bidder_id != bidder.bidder_id]
        for ob in other_bidders:
            if ob.award_status in ["CONFIRMED_L1", "CONTINGENCY_STANDBY"]:
                ob.award_priority = None
                ob.award_status = "UNASSIGNED"
        
        # 3. Find eligible compliant bidders for L2 & L3 standby contingency
        eligible_standbys = [
            b for b in other_bidders
            if (b.compliance_score and b.compliance_score.score >= 90)
            and b.conflict_links_count == 0
            and (not b.documents or not b.documents[0].forensic_report or b.documents[0].forensic_report.overall_tamper_score <= 25)
            and (b.compliance_score and b.compliance_score.risk_level.value == "LOW")
        ]
        
        # Sort by CIBIL Trust Score and Turnover
        eligible_standbys.sort(
            key=lambda x: (
                x.longitudinal_trust_score.score if x.longitudinal_trust_score else 800,
                x.financials.annual_turnover_inr
            ),
            reverse=True
        )

        if len(eligible_standbys) > 0:
            eligible_standbys[0].award_priority = "PRIORITY_2_L2"
            eligible_standbys[0].award_status = "CONTINGENCY_STANDBY"
            eligible_standbys[0].officer_status = "CONTINGENCY_L2"
            eligible_standbys[0].contingency_sla_hours = 72

        if len(eligible_standbys) > 1:
            eligible_standbys[1].award_priority = "PRIORITY_3_L3"
            eligible_standbys[1].award_status = "CONTINGENCY_STANDBY"
            eligible_standbys[1].officer_status = "CONTINGENCY_L3"
            eligible_standbys[1].contingency_sla_hours = 72

    elif payload.action.value in ["REJECT", "DISQUALIFY"]:
        bidder.award_priority = None
        bidder.award_status = "REJECTED"

    audit_trail.log_event(
        bidder_id=bidder.bidder_id,
        step="STEP_9_OFFICER_DECISION",
        actor="OFFICER",
        action_type=f"OFFICER_{payload.action.value}",
        details={
            "officer_name": payload.officer_name,
            "officer_id": payload.officer_id,
            "action": payload.action.value,
            "award_priority": bidder.award_priority,
            "award_status": bidder.award_status,
            "comments": payload.comments,
            "override_justification": payload.override_justification
        },
        notes=payload.comments
    )
    return {"success": True, "bidder": bidder}

@app.get("/api/bidders/contingency-roster/{tender_id:path}", tags=["Contingency"])
async def get_tender_contingency_roster(tender_id: str):
    """
    Retrieves the confirmed Priority 1 (L1) Awardee and Priority 2 (L2) & Priority 3 (L3)
    Standby Contingencies for a specific tender.
    """
    tender_bidders = [b for b in BIDDERS_DB.values() if b.tender_id == tender_id]
    
    primary_l1 = next((b for b in tender_bidders if b.award_priority == "PRIORITY_1_L1"), None)
    standby_l2 = next((b for b in tender_bidders if b.award_priority == "PRIORITY_2_L2"), None)
    standby_l3 = next((b for b in tender_bidders if b.award_priority == "PRIORITY_3_L3"), None)
    
    return {
        "tender_id": tender_id,
        "primary_l1": primary_l1,
        "standby_l2": standby_l2,
        "standby_l3": standby_l3,
        "is_awarded": primary_l1 is not None,
        "contingency_sla_hours": 72
    }

class SetPriorityPayload(BaseModel):
    bidder_id: str
    priority: Optional[str] = None # "PRIORITY_1_L1", "PRIORITY_2_L2", "PRIORITY_3_L3", or None

@app.post("/api/bidders/set-priority", tags=["Contingency"])
async def set_bidder_priority(payload: SetPriorityPayload):
    """
    Allows the procurement officer to manually assign or change the priority
    (Priority 1 L1, Priority 2 L2, Priority 3 L3) for any vendor with immediate effect.
    """
    if payload.bidder_id not in BIDDERS_DB:
        raise HTTPException(status_code=404, detail="Bidder not found")
    
    bidder = BIDDERS_DB[payload.bidder_id]
    tender_id = bidder.tender_id
    new_priority = payload.priority if payload.priority in ["PRIORITY_1_L1", "PRIORITY_2_L2", "PRIORITY_3_L3"] else None
    
    # If assigning a priority that was already held by another vendor in this tender, clear it from that vendor
    if new_priority:
        for ob in BIDDERS_DB.values():
            if ob.tender_id == tender_id and ob.bidder_id != bidder.bidder_id and ob.award_priority == new_priority:
                ob.award_priority = None
                ob.award_status = "UNASSIGNED"
                ob.officer_status = "PENDING_REVIEW"

    bidder.award_priority = new_priority
    if new_priority == "PRIORITY_1_L1":
        bidder.award_status = "CONFIRMED_L1"
        bidder.officer_status = "APPROVED"
    elif new_priority in ["PRIORITY_2_L2", "PRIORITY_3_L3"]:
        bidder.award_status = "CONTINGENCY_STANDBY"
        bidder.officer_status = "CONTINGENCY_STANDBY"
    else:
        bidder.award_status = "UNASSIGNED"
        bidder.officer_status = "PENDING_REVIEW"

    audit_trail.log_event(
        bidder_id=bidder.bidder_id,
        step="MANUAL_PRIORITY_ASSIGNMENT",
        actor="OFFICER",
        action_type=f"SET_{new_priority or 'CLEAR'}",
        details={
            "bidder_name": bidder.company_name,
            "assigned_priority": new_priority,
            "award_status": bidder.award_status
        },
        notes=f"Officer manually updated award priority to {new_priority or 'None'} for {bidder.company_name}."
    )

    return {"success": True, "bidder": bidder}

class FinalizeEvaluationPayload(BaseModel):
    tender_id: str
    officer_id: Optional[str] = "officer001"
    officer_name: Optional[str] = "Rajesh Kumar Sharma"
    officer_badge: Optional[str] = "IAS-2018-RK"

@app.post("/api/tenders/finalize-evaluation", tags=["Evaluation"])
async def finalize_tender_evaluation(payload: FinalizeEvaluationPayload):
    """
    Finalizes the technical evaluation for a tender:
    1. Confirms the Bid Winner (Priority 1 / L1) and Standbys (Priority 2 & 3).
    2. Automatically marks all remaining non-priority bidders as REJECTED.
    3. Updates tender status to 'EVALUATION_COMPLETED'.
    4. Logs formal finalization event in CAG Audit Trail.
    """
    tender_id = payload.tender_id
    if tender_id not in TENDERS_DB:
        raise HTTPException(status_code=404, detail="Tender not found")
    
    tender = TENDERS_DB[tender_id]
    tender_bidders = [b for b in BIDDERS_DB.values() if b.tender_id == tender_id]
    
    primary_l1 = next((b for b in tender_bidders if b.award_priority == "PRIORITY_1_L1"), None)
    standby_l2 = next((b for b in tender_bidders if b.award_priority == "PRIORITY_2_L2"), None)
    standby_l3 = next((b for b in tender_bidders if b.award_priority == "PRIORITY_3_L3"), None)
    
    # If no L1 assigned yet, auto-assign top compliant bidder
    if not primary_l1:
        eligible = [b for b in tender_bidders if (b.compliance_score and b.compliance_score.risk_level != RiskLevel.CRITICAL and b.conflict_links_count == 0)]
        eligible.sort(key=lambda x: (x.longitudinal_trust_score.score if x.longitudinal_trust_score else 0), reverse=True)
        if eligible:
            primary_l1 = eligible[0]
            primary_l1.award_priority = "PRIORITY_1_L1"
    
    now_str = datetime.utcnow().strftime("%d %b %Y, %I:%M %p UTC")
    
    # Process all bidders for this tender
    for b in tender_bidders:
        if primary_l1 and b.bidder_id == primary_l1.bidder_id:
            b.award_priority = "PRIORITY_1_L1"
            b.award_status = "CONFIRMED_L1"
            b.officer_status = "APPROVED"
            b.decided_at = now_str
            b.officer_id = payload.officer_id
            b.officer_notes = "Awarded as Primary Bid Winner (L1) upon technical evaluation completion."
        elif standby_l2 and b.bidder_id == standby_l2.bidder_id:
            b.award_priority = "PRIORITY_2_L2"
            b.award_status = "CONTINGENCY_STANDBY"
            b.officer_status = "CONTINGENCY_L2"
            b.decided_at = now_str
            b.officer_id = payload.officer_id
            b.officer_notes = "Designated Priority 2 Standby (72-hour SLA contingency)."
        elif standby_l3 and b.bidder_id == standby_l3.bidder_id:
            b.award_priority = "PRIORITY_3_L3"
            b.award_status = "CONTINGENCY_STANDBY"
            b.officer_status = "CONTINGENCY_L3"
            b.decided_at = now_str
            b.officer_id = payload.officer_id
            b.officer_notes = "Designated Priority 3 Standby (72-hour SLA contingency)."
        else:
            b.award_priority = None
            b.award_status = "REJECTED"
            b.officer_status = "REJECTED"
            b.decided_at = now_str
            b.officer_id = payload.officer_id

            # --- Build dynamic, per-vendor rejection rationale from actual data ---
            grounds = []

            # 1. Director debarment (GFR 151)
            if b.directors:
                debarred_dirs = [d for d in b.directors if getattr(d, "is_flagged_debarred", False)]
                if debarred_dirs:
                    grounds.append(
                        f"Director debarment under GFR Rule 151: {debarred_dirs[0].name} (DIN: {debarred_dirs[0].din}) "
                        f"is on the MoF/CVC statutory blacklist — compulsory disqualification."
                    )

            # 2. Critical / HIGH compliance risk
            if b.compliance_score:
                if b.compliance_score.risk_level.value == "CRITICAL":
                    grounds.append(
                        f"Critical statutory risk (Compliance Score: {b.compliance_score.score}/100) — "
                        f"vendor failed mandatory GoI procurement eligibility gate."
                    )
                elif b.compliance_score.risk_level.value in ["HIGH", "MEDIUM"]:
                    grounds.append(
                        f"Elevated compliance risk (Score: {b.compliance_score.score}/100, "
                        f"Risk: {b.compliance_score.risk_level.value}) — below the minimum acceptable threshold for this tender."
                    )

            # 3. Cartel / entity conflict links
            if b.conflict_links_count > 0:
                grounds.append(
                    f"Entity-graph cartel linkage: {b.conflict_links_count} shared director/premises link(s) "
                    f"with competing bidders — violates CVC Anti-Collusion Directive."
                )

            # 4. Cross-verification mismatches (OCR vs live govt portals)
            if b.cross_check_mismatches:
                mismatch_fields = ", ".join(m.field_name for m in b.cross_check_mismatches[:3])
                grounds.append(
                    f"Document OCR cross-check mismatch(es) against GSTN/MCA21 live portal: "
                    f"{len(b.cross_check_mismatches)} discrepancy flag(s) on [{mismatch_fields}]."
                )

            # 5. ELA digital tamper suspicion
            if b.documents and b.documents[0].forensic_report:
                fr = b.documents[0].forensic_report
                if fr.overall_tamper_score > 60:
                    grounds.append(
                        f"High-confidence certificate forgery detected via ELA Q90 analysis — "
                        f"Tamper Suspicion Score: {fr.overall_tamper_score}% ({fr.status.value}). "
                        f"Software artefact: {fr.metadata_analysis.producing_software if fr.metadata_analysis else 'Unknown'}."
                    )
                elif fr.overall_tamper_score > 25:
                    grounds.append(
                        f"Moderate ELA tamper suspicion ({fr.overall_tamper_score}%, {fr.status.value}) — "
                        f"pixel residue inconsistency in submitted certificates. Clarification notice issued but not resolved."
                    )

            # 6. Financial turnover below threshold
            if b.financials:
                turnover_cr = b.financials.annual_turnover_inr / 10_000_000
                if turnover_cr < 2.0:
                    grounds.append(
                        f"Annual turnover ₹{turnover_cr:.2f} Cr falls below mandatory eligibility threshold of ₹2.00 Cr."
                    )

            # 7. AI engine recommendation
            if b.ai_recommendation and b.ai_recommendation.recommended_action in ["RECOMMEND_REJECTION", "FLAG_FOR_REVIEW"]:
                grounds.append(
                    f"Nirikshan AI Determination: {b.ai_recommendation.recommended_action} — "
                    f"{b.ai_recommendation.executive_summary[:120] if b.ai_recommendation.executive_summary else 'Vendor profile does not meet technical qualification criteria.'}."
                )

            # Default fallback if no specific flag applies
            if not grounds:
                grounds.append(
                    "Not selected as Primary L1 awardee or Standby Contingency following merit-based technical evaluation ranking."
                )

            rejection_note = (
                f"TECHNICAL EVALUATION REJECTION | GFR 2017 Grounds:\n"
                + "\n".join(f"  [{i+1}] {g}" for i, g in enumerate(grounds))
            )
            b.officer_notes = rejection_note

    # Update tender record
    tender.status = "EVALUATION_COMPLETED"
    tender.winner_company = primary_l1.company_name if primary_l1 else "N/A"
    tender.winner_bidder_id = primary_l1.bidder_id if primary_l1 else "N/A"
    tender.standby_l2_company = standby_l2.company_name if standby_l2 else None
    tender.standby_l3_company = standby_l3.company_name if standby_l3 else None
    tender.finalized_at = now_str
    tender.finalized_by = payload.officer_name or "Procurement Officer"
    tender.finalized_by_badge = payload.officer_badge or "IAS-2018-RK"

    # Audit log
    audit_trail.log_event(
        bidder_id=primary_l1.bidder_id if primary_l1 else tender_id,
        step="EVALUATION_FINALIZATION",
        actor="OFFICER",
        action_type="FINALIZE_TENDER_RESULT",
        details={
            "tender_id": tender_id,
            "officer_name": payload.officer_name,
            "officer_id": payload.officer_id,
            "winner_company": tender.winner_company,
            "standby_l2": tender.standby_l2_company,
            "standby_l3": tender.standby_l3_company,
            "rejected_count": len([b for b in tender_bidders if b.award_status == "REJECTED"])
        },
        notes=f"Tender {tender_id} technical evaluation finalized. Winner: {tender.winner_company}."
    )

    return {
        "success": True,
        "tender": tender,
        "primary_l1": primary_l1,
        "standby_l2": standby_l2,
        "standby_l3": standby_l3,
        "rejected_count": len([b for b in tender_bidders if b.award_status == "REJECTED"])
    }

@app.post("/api/tenders/reopen-evaluation", tags=["Evaluation"])
async def reopen_tender_evaluation(payload: FinalizeEvaluationPayload):
    """
    Reopens a finalized tender for further evaluation adjustments.
    """
    tender_id = payload.tender_id
    if tender_id not in TENDERS_DB:
        raise HTTPException(status_code=404, detail="Tender not found")
    
    tender = TENDERS_DB[tender_id]
    tender.status = "TECHNICAL_EVALUATION"
    
    audit_trail.log_event(
        bidder_id=tender_id,
        step="EVALUATION_REOPENED",
        actor="OFFICER",
        action_type="REOPEN_TENDER_EVALUATION",
        details={"tender_id": tender_id, "officer_name": payload.officer_name},
        notes=f"Tender {tender_id} evaluation reopened by {payload.officer_name}."
    )
    return {"success": True, "tender": tender}

@app.get("/api/audit")
async def get_audit_logs(bidder_id: Optional[str] = None):
    if bidder_id:
        return audit_trail.get_logs_for_bidder(bidder_id)
    return audit_trail.get_all_logs()

@app.get("/api/metrics")
async def get_dashboard_metrics(tender_id: Optional[str] = None):
    if tender_id:
        bidders = [b for b in BIDDERS_DB.values() if b.tender_id == tender_id]
    else:
        bidders = list(BIDDERS_DB.values())
    total = len(bidders)
    compliant_count = sum(1 for b in bidders if b.compliance_score and b.compliance_score.risk_level == RiskLevel.LOW)
    flagged_count = sum(1 for b in bidders if b.compliance_score and b.compliance_score.risk_level in (RiskLevel.MEDIUM, RiskLevel.HIGH))
    debarred_count = sum(1 for b in bidders if b.compliance_score and b.compliance_score.risk_level == RiskLevel.CRITICAL)

    return {
        "total_bidders": total,
        "compliant_count": compliant_count,
        "flagged_count": flagged_count,
        "debarred_count": debarred_count,
        "automated_verification_time_sec": 1.45,
        "manual_verification_baseline_days": 4.5,
        "time_saved_percentage": "99.8%"
    }

# ---------------------------------------------------------------------------
# AUTH ENDPOINTS (Day 4 — Person A)
# ---------------------------------------------------------------------------

from fastapi.security import OAuth2PasswordRequestForm

@app.post("/api/auth/login", tags=["Auth"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticate and receive a JWT Bearer token.
    Demo credentials:
      Officer  — username: officer.sharma / password: officer123
      Admin    — username: admin.procure  / password: admin123
      Auditor  — username: auditor.cag    / password: auditor123
    """
    from fastapi.security import OAuth2PasswordRequestForm
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_access_token(username=user["username"], role=user["role"])
    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user["role"],
        "full_name": user["full_name"],
    }


# ---------------------------------------------------------------------------
# ASYNC CELERY VERIFICATION ENDPOINTS (Person A)
# ---------------------------------------------------------------------------

@app.post("/api/verify/{bidder_id}", tags=["Verification"])
async def trigger_async_verification(
    bidder_id: str,
    tender_id: str = "GEM/2026/B/89420",
    scenario_type: str = "apex",
):
    """
    Enqueue a full background verification job for the given bidder.
    Returns immediately with a Celery task_id.
    The React frontend polls /api/verify/status/{task_id} for progress.
    """
    task = run_verification_pipeline.delay(bidder_id, tender_id, scenario_type)
    return {
        "task_id": task.id,
        "bidder_id": bidder_id,
        "status": "QUEUED",
        "message": f"Verification pipeline queued. Poll /api/verify/status/{task.id} for progress.",
    }


@app.get("/api/verify/status/{task_id}", tags=["Verification"])
async def get_verification_status(task_id: str):
    """
    Poll Celery task status for the React frontend WebSocket/polling loop.
    States: PENDING → STARTED → PROGRESS → SUCCESS / FAILURE
    """
    from app.tasks.celery_app import celery as celery_app
    task = celery_app.AsyncResult(task_id)
    response = {
        "task_id": task_id,
        "state": task.state,
        "info": task.info if isinstance(task.info, dict) else str(task.info),
    }
    if task.state == "SUCCESS":
        response["result"] = task.result
    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
