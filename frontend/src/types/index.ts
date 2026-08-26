export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export type OfficerStatus = 'APPROVED' | 'REJECTED' | 'REQUEST_INFO' | 'OVERRIDDEN' | 'PENDING_REVIEW';

export interface BidderIdentifiers {
  gstin?: string;
  pan?: string;
  cin?: string;
  udyam_registration_number?: string;
  epfo_code?: string;
}

export interface BidderFinancials {
  annual_turnover_inr: number;
  net_worth_inr: number;
  last_financial_year: string;
  itr_filed_years: string[];
}

export interface UploadedDocument {
  doc_id: string;
  bidder_id: string;
  doc_type: string;
  file_name: string;
  uploaded_at: string;
  extraction_status: string;
  extracted_fields: Record<string, any>;
  ocr_raw_text?: string;
  confidence: number;
}

export interface PortalVerificationResult {
  source: string;
  status: string;
  key_fields: Record<string, any>;
  raw_data: Record<string, any>;
  verified_at: string;
  response_time_ms: number;
}

export interface CrossCheckMismatch {
  field_name: string;
  source_a_name: string;
  source_a_value: any;
  source_b_name: string;
  source_b_value: any;
  severity: RiskLevel;
  discrepancy_explanation: string;
  suggested_investigation: string;
}

export interface RuleEvaluationResult {
  rule_id: string;
  rule_name: string;
  category: string;
  passed: boolean;
  is_hard_block: boolean;
  expected_condition: string;
  actual_value: any;
  failure_reason?: string;
}

export interface RiskFactor {
  code: string;
  title: string;
  severity: RiskLevel;
  is_soft_risk: boolean;
  explanation: string;
}

export interface AIRecommendation {
  recommended_action: string;
  executive_summary: string;
  risk_factors: RiskFactor[];
  mitigation_notes?: string;
  confidence_score: number;
}

export interface ComplianceScore {
  score: number;
  risk_level: RiskLevel;
  hard_blocks_triggered: number;
  mandatory_rules_passed: number;
  mandatory_rules_total: number;
  soft_factors_penalty: number;
  mismatches_penalty: number;
  score_breakdown: Record<string, any>;
}

export interface AuditLogEntry {
  log_id: string;
  timestamp: string;
  bidder_id: string;
  step: string;
  actor: string;
  action_type: string;
  details: Record<string, any>;
  notes?: string;
}

export interface Bidder {
  bidder_id: string;
  tender_id: string;
  company_name: string;
  legal_structure: string;
  registered_state: string;
  created_at: string;
  identifiers: BidderIdentifiers;
  financials: BidderFinancials;
  documents: UploadedDocument[];
  portal_verifications: Record<string, PortalVerificationResult>;
  cross_check_mismatches: CrossCheckMismatch[];
  rule_results: RuleEvaluationResult[];
  ai_recommendation?: AIRecommendation;
  compliance_score?: ComplianceScore;
  officer_status: OfficerStatus;
  officer_notes?: string;
  officer_id?: string;
  decided_at?: string;
}

export interface DashboardMetrics {
  total_bidders: number;
  compliant_count: number;
  flagged_count: number;
  debarred_count: number;
  automated_verification_time_sec: number;
  manual_verification_baseline_days: number;
  time_saved_percentage: string;
}

// Feature 1: Unified Vendor Document Vault
export interface VaultDocument {
  doc_id: string;
  doc_type: string;
  document_name: string;
  issuer: string;
  issue_date: string;
  expiry_date: string;
  days_to_expiry: number;
  is_valid: boolean;
  verification_badge: string;
  reuse_count: number;
}

export interface VendorVault {
  vendor_id: string;
  company_name: string;
  documents: VaultDocument[];
  total_reused_tenders: number;
  last_synced: string;
  vault_status: string;
}

// Feature 2: Longitudinal Trust Score
export interface TrustScoreDimension {
  name: string;
  score: number;
  weight_percent: number;
  grade: string;
  details: string;
}

export interface LongitudinalTrustScore {
  score: number;
  rating_band: string;
  delivery_sla_rate: number;
  tax_compliance_health: number;
  gem_rating: number;
  dispute_free_months: number;
  historical_trend_24m: { month: string; score: number }[];
  dimensions: TrustScoreDimension[];
  summary: string;
}

// Feature 3: Graph-Based Entity Linking
export type EntityNodeType = 'BIDDER' | 'DIRECTOR' | 'ADDRESS' | 'BANK';

export interface EntityGraphNode {
  id: string;
  label: string;
  type: EntityNodeType;
  risk_level: RiskLevel;
  details: Record<string, any>;
}

export interface EntityGraphEdge {
  source: string;
  target: string;
  relationship: string;
  is_conflict: boolean;
  confidence: number;
  explanation?: string;
}

export interface EntityGraph {
  nodes: EntityGraphNode[];
  edges: EntityGraphEdge[];
  cartels_detected: number;
  debarment_links_found: number;
  risk_summary: string;
}

// Feature 5: Natural Language Officer Assistant
export interface OfficerChatRequest {
  query: string;
  tender_id: string;
  active_bidder_id?: string;
}

export interface OfficerChatResponse {
  reply: string;
  context_used: string[];
  suggested_actions: string[];
  timestamp: string;
}
