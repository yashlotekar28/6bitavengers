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

class ExtractionStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class OfficerActionType(str, Enum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    REQUEST_INFO = "REQUEST_INFO"
    OVERRIDE = "OVERRIDE"

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

# Step 2: Uploaded Document Schema
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

# Step 3: Process A - Portal Verification Output
class PortalVerificationResult(BaseModel):
    source: str # e.g. "GST_PORTAL (API Setu)", "PAN_REGISTRY", "CPPP_DEBARMENT"
    status: str # "ACTIVE", "VALID", "DEBARRED", "INACTIVE"
    key_fields: Dict[str, Any]
    raw_data: Dict[str, Any] = {}
    verified_at: datetime = Field(default_factory=datetime.utcnow)
    response_time_ms: int = 120

# Step 4: Cross-Verification Mismatch
class CrossCheckMismatch(BaseModel):
    field_name: str
    source_a_name: str
    source_a_value: Any
    source_b_name: str
    source_b_value: Any
    severity: RiskLevel
    discrepancy_explanation: str
    suggested_investigation: str

# Step 5: Rules Engine Result
class RuleEvaluationResult(BaseModel):
    rule_id: str
    rule_name: str
    category: str # "STATUTORY", "TECHNICAL", "FINANCIAL", "DEBARMENT"
    passed: bool
    is_hard_block: bool # If True and passed=False, vendor is disqualified regardless of score
    expected_condition: str
    actual_value: Any
    failure_reason: Optional[str] = None

# Step 6: AI Reasoning & Risk Synthesis
class RiskFactor(BaseModel):
    code: str
    title: str
    severity: RiskLevel
    is_soft_risk: bool
    explanation: str

class AIRecommendation(BaseModel):
    recommended_action: str # "RECOMMEND_APPROVAL", "RECOMMEND_REJECTION", "FLAG_FOR_OFFICER_REVIEW", "REQUEST_MORE_INFO"
    executive_summary: str
    risk_factors: List[RiskFactor] = []
    mitigation_notes: Optional[str] = None
    confidence_score: float = 0.95

# Step 7: Compliance Scoring
class ComplianceScore(BaseModel):
    score: int # 0 to 100
    risk_level: RiskLevel
    hard_blocks_triggered: int
    mandatory_rules_passed: int
    mandatory_rules_total: int
    soft_factors_penalty: int
    mismatches_penalty: int
    score_breakdown: Dict[str, Any] = {}

# Step 10: Audit Log Entry
class AuditLogEntry(BaseModel):
    log_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    bidder_id: str
    step: str # "STEP_1_SUBMIT", "STEP_2_UPLOAD", "STEP_3_PORTAL", "STEP_4_CROSS_CHECK", etc.
    actor: str # "SYSTEM", "CELERY_WORKER", "RULES_ENGINE", "AI_ENGINE", "OFFICER"
    action_type: str
    details: Dict[str, Any] = {}
    notes: Optional[str] = None

# Canonical Bidder Model (Single Source of Truth)
class Bidder(BaseModel):
    bidder_id: str
    tender_id: str
    company_name: str
    legal_structure: str # "Private Limited", "Proprietorship", "Partnership", "LLP"
    registered_state: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    identifiers: BidderIdentifiers
    financials: BidderFinancials
    
    # Aggregated Pipeline States
    documents: List[UploadedDocument] = []
    portal_verifications: Dict[str, PortalVerificationResult] = {}
    cross_check_mismatches: List[CrossCheckMismatch] = []
    rule_results: List[RuleEvaluationResult] = []
    ai_recommendation: Optional[AIRecommendation] = None
    compliance_score: Optional[ComplianceScore] = None
    
    # Final Human Decision (Step 9)
    officer_status: str = "PENDING_REVIEW" # "APPROVED", "REJECTED", "INFO_REQUESTED", "OVERRIDDEN", "PENDING_REVIEW"
    officer_notes: Optional[str] = None
    officer_id: Optional[str] = None
    decided_at: Optional[datetime] = None

# Officer Decision Payload (Step 9)
class OfficerDecisionPayload(BaseModel):
    bidder_id: str
    action: OfficerActionType
    officer_id: str = "OFFICER-GEM-994"
    officer_name: str = "Rajesh Kumar (Senior Procurement Officer)"
    comments: str
    override_justification: Optional[str] = None
