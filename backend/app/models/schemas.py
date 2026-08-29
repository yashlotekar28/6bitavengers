from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime

# Enums
class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class VerificationStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLIANT = "COMPLIANT"
    NON_COMPLIANT = "NON_COMPLIANT"
    FLAGGED_FOR_REVIEW = "FLAGGED_FOR_REVIEW"
    DEBARRED = "DEBARRED"

class DocumentType(str, Enum):
    UDYAM_CERTIFICATE = "UDYAM_CERTIFICATE"
    GST_CERTIFICATE = "GST_CERTIFICATE"
    ITR_ACKNOWLEDGMENT = "ITR_ACKNOWLEDGMENT"
    PAN_CARD = "PAN_CARD"
    BALANCE_SHEET = "BALANCE_SHEET"
    AUTHORIZATION_LETTER = "AUTHORIZATION_LETTER"
    ISO_27001_CERTIFICATE = "ISO_27001_CERTIFICATE"
    PAST_PERFORMANCE_CREDENTIAL = "PAST_PERFORMANCE_CREDENTIAL"

class ExtractionStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class OfficerActionType(str, Enum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    REQUEST_INFO = "REQUEST_INFO"
    OVERRIDE = "OVERRIDE"

# Tender Overview Schema
class Tender(BaseModel):
    tender_id: str
    title: str
    category: str
    ministry: str
    department: str
    estimated_value_cr: float
    bid_type: str
    closing_date: str
    status: str = "TECHNICAL_EVALUATION"
    total_bidders: int = 15
    compliant_bidders: int = 0
    flagged_bidders: int = 0
    debarred_bidders: int = 0
    description: str = ""
    winner_company: Optional[str] = None
    winner_bidder_id: Optional[str] = None
    standby_l2_company: Optional[str] = None
    standby_l3_company: Optional[str] = None
    finalized_at: Optional[str] = None
    finalized_by: Optional[str] = None
    finalized_by_badge: Optional[str] = None

# Feature 1: Unified Document Vault Schemas
class VaultDocument(BaseModel):
    doc_id: str
    doc_type: DocumentType
    document_name: str
    issuer: str
    issue_date: str
    expiry_date: str
    days_to_expiry: int
    is_valid: bool
    verification_badge: str = "DIGILOCKER_VERIFIED" # "DIGILOCKER_VERIFIED", "API_SETU_AUTHENTICATED", "PENDING_RECHECK"
    reuse_count: int = 1
    participated_tenders: List[str] = []
    file_size_kb: int = 420
    extracted_metadata: Dict[str, Any] = {}

class VendorVault(BaseModel):
    vendor_id: str
    company_name: str
    documents: List[VaultDocument] = []
    total_reused_tenders: int = 1
    last_synced: datetime = Field(default_factory=datetime.utcnow)
    vault_status: str = "SYNCHRONIZED"

# Feature 2: Longitudinal Trust Score (CIBIL-style 300-900)
class TrustScoreDimension(BaseModel):
    name: str
    score: int # 0 to 100
    weight_percent: int
    grade: str # AAA, AA, A, BBB, C, D
    details: str

class LongitudinalTrustScore(BaseModel):
    score: int # 300 to 900 scale (CIBIL-style)
    rating_band: str # "PRIME_AAA (850-900)", "HIGH_RELIABILITY_AA (750-849)", "MODERATE_BBB (650-749)", "SUBPRIME_D (<650)"
    delivery_sla_rate: float # e.g. 98.4%
    tax_compliance_health: float # e.g. 100%
    gem_rating: float # e.g. 4.8 / 5.0
    dispute_free_months: int # e.g. 36
    historical_trend_24m: List[Dict[str, Any]] = [] # [{month: "Jan 25", score: 810}, ...]
    dimensions: List[TrustScoreDimension] = []
    summary: str

# Feature 3: Graph-Based Entity Linking & Shell Company Detection
class EntityNodeType(str, Enum):
    BIDDER = "BIDDER"
    DIRECTOR = "DIRECTOR"
    ADDRESS = "ADDRESS"
    DEBARRED_ENTITY = "DEBARRED_ENTITY"
    BANK_BRANCH = "BANK_BRANCH"

class EntityGraphNode(BaseModel):
    id: str
    label: str
    type: EntityNodeType
    risk_level: RiskLevel = RiskLevel.LOW
    details: Dict[str, Any] = {}

class EntityGraphEdge(BaseModel):
    source: str
    target: str
    relationship: str # "DIRECTOR_OF", "REGISTERED_AT", "GUARANTOR_BANK", "COLLUSION_LINK", "PAST_DIRECTOR_DEBARRED"
    is_conflict: bool = False
    confidence: float = 0.95
    explanation: Optional[str] = None

class EntityGraph(BaseModel):
    nodes: List[EntityGraphNode] = []
    edges: List[EntityGraphEdge] = []
    cartels_detected: int = 0
    debarment_links_found: int = 0
    risk_summary: str = "Clean network topology."

# Feature 5: Natural Language Officer Assistant (Chat)
class OfficerChatRequest(BaseModel):
    query: str
    tender_id: str = "GEM/2026/B/89420"
    active_bidder_id: Optional[str] = None

class OfficerChatResponse(BaseModel):
    reply: str
    context_used: List[str] = []
    suggested_actions: List[str] = []
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# Identifiers & Financials
class BidderIdentifiers(BaseModel):
    gstin: Optional[str] = None
    pan: Optional[str] = None
    cin: Optional[str] = None
    udyam_registration_number: Optional[str] = None
    epfo_code: Optional[str] = None

class BidderFinancials(BaseModel):
    annual_turnover_inr: float = 0.0
    net_worth_inr: float = 0.0
    last_financial_year: str = "2024-25"
    itr_filed_years: List[str] = []

# --- Document Forensics & ELA Tamper Analysis Schemas ---

class TamperStatus(str, Enum):
    CLEAN = "CLEAN"                     # Low suspicion (score 0-25)
    SUSPICIOUS = "SUSPICIOUS"           # Moderate suspicion (score 26-65)
    LIKELY_TAMPERED = "LIKELY_TAMPERED" # High suspicion (score >65)

class ForensicRegionBox(BaseModel):
    x: int
    y: int
    width: int
    height: int
    anomaly_intensity: float            # 0.0 to 1.0
    description: str

class MetadataForensicCheck(BaseModel):
    creation_date: Optional[str] = None
    modification_date: Optional[str] = None
    producing_software: Optional[str] = None
    last_saved_by: Optional[str] = None
    has_exif: bool = False
    is_software_suspicious: bool = False
    is_date_inconsistent: bool = False
    flags: List[str] = []

class CopyMoveMatch(BaseModel):
    source_box: Dict[str, int]
    target_box: Dict[str, int]
    match_confidence: float
    explanation: str

class DocumentForensicReport(BaseModel):
    doc_id: str
    file_name: str
    overall_tamper_score: int                     # 0 to 100 weighted score
    status: TamperStatus                          # CLEAN / SUSPICIOUS / LIKELY_TAMPERED
    
    # 3 Detection Layer Scores
    ela_score: int                                # Layer 1: ELA Score (0-100)
    metadata_score: int                           # Layer 2: Metadata Score (0-100)
    copy_move_score: int                          # Layer 3: Copy-Move Score (0-100)
    
    # Evidence & Overlays
    ela_heatmap_base64: Optional[str] = None      # Data URI PNG for inline inspection
    flagged_regions: List[ForensicRegionBox] = []
    metadata_analysis: MetadataForensicCheck
    copy_move_matches: List[CopyMoveMatch] = []
    
    forensic_summary: str
    analyzed_at: datetime = Field(default_factory=datetime.utcnow)

# Uploaded Document Schema
class UploadedDocument(BaseModel):
    doc_id: str
    bidder_id: str
    doc_type: DocumentType
    file_name: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    extraction_status: ExtractionStatus = ExtractionStatus.COMPLETED
    extracted_fields: Dict[str, Any] = {}
    ocr_raw_text: Optional[str] = None
    confidence: float = 0.98
    
    # Document Forensics & ELA Tamper Analysis Result
    forensic_report: Optional[DocumentForensicReport] = None

# Portal Verification Output
class PortalVerificationResult(BaseModel):
    source: str
    status: str
    key_fields: Dict[str, Any]
    raw_data: Dict[str, Any] = {}
    verified_at: datetime = Field(default_factory=datetime.utcnow)
    response_time_ms: int = 120

# Cross-Verification Mismatch
class CrossCheckMismatch(BaseModel):
    field_name: str
    source_a_name: str
    source_a_value: Any
    source_b_name: str
    source_b_value: Any
    severity: RiskLevel
    discrepancy_explanation: str
    suggested_investigation: str

# Rules Engine Result
class RuleEvaluationResult(BaseModel):
    rule_id: str
    rule_name: str
    category: str
    passed: bool
    is_hard_block: bool
    expected_condition: str
    actual_value: Any
    failure_reason: Optional[str] = None

# AI Reasoning & Risk Synthesis
class RiskFactor(BaseModel):
    code: str
    title: str
    severity: RiskLevel
    is_soft_risk: bool
    explanation: str

class AIRecommendation(BaseModel):
    recommended_action: str
    executive_summary: str
    risk_factors: List[RiskFactor] = []
    mitigation_notes: Optional[str] = None
    confidence_score: float = 0.95

# Compliance Scoring
class ComplianceScore(BaseModel):
    score: int
    risk_level: RiskLevel
    hard_blocks_triggered: int
    mandatory_rules_passed: int
    mandatory_rules_total: int
    soft_factors_penalty: int
    mismatches_penalty: int
    score_breakdown: Dict[str, Any] = {}

# Audit Log Entry
class AuditLogEntry(BaseModel):
    log_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    bidder_id: str
    step: str
    actor: str
    action_type: str
    details: Dict[str, Any] = {}
    notes: Optional[str] = None

# Director & Address Info for Graph Linking
class DirectorInfo(BaseModel):
    din: str
    name: str
    designation: str
    is_flagged_debarred: bool = False

# Canonical Bidder Model (Single Source of Truth)
class Bidder(BaseModel):
    bidder_id: str
    tender_id: str
    company_name: str
    legal_structure: str
    registered_state: str
    registered_address: str = "Plot 45, Andheri East, Mumbai, MH"
    directors: List[DirectorInfo] = []
    bank_branch_code: str = "SBIN0004921"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    identifiers: BidderIdentifiers
    financials: BidderFinancials
    
    # Aggregated Pipeline States
    documents: List[UploadedDocument] = []
    vault_documents: List[VaultDocument] = []
    longitudinal_trust_score: Optional[LongitudinalTrustScore] = None
    portal_verifications: Dict[str, PortalVerificationResult] = {}
    cross_check_mismatches: List[CrossCheckMismatch] = []
    rule_results: List[RuleEvaluationResult] = []
    ai_recommendation: Optional[AIRecommendation] = None
    compliance_score: Optional[ComplianceScore] = None
    
    # Entity Linkage Risk Counter
    conflict_links_count: int = 0
    
    # Final Human Decision & Priority Contingency Allocation
    officer_status: str = "PENDING_REVIEW"
    officer_notes: Optional[str] = None
    officer_id: Optional[str] = None
    decided_at: Optional[datetime] = None
    
    # Priority Allocation Deck (L1 Primary Confirmed, L2 & L3 Standby Contingencies)
    award_priority: Optional[str] = None # "PRIORITY_1_L1", "PRIORITY_2_L2", "PRIORITY_3_L3"
    award_status: Optional[str] = "UNASSIGNED" # "CONFIRMED_L1", "CONTINGENCY_STANDBY", "REJECTED", "UNASSIGNED"
    contingency_sla_hours: int = 72

# Officer Decision Payload
class OfficerDecisionPayload(BaseModel):
    bidder_id: str
    action: OfficerActionType
    officer_id: str = "OFFICER-GEM-994"
    officer_name: str = "Rajesh Kumar (Senior Procurement Officer)"
    comments: str
    override_justification: Optional[str] = None
