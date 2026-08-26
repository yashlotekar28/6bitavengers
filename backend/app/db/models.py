"""
PostgreSQL ORM models — matches the canonical bidder JSON schema agreed in Day 1 sync.
Person A — Backend/Integration
"""
import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, DateTime, Text,
    Boolean, ForeignKey, Enum as SAEnum
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.database import Base


class Bidder(Base):
    """Core entity: a vendor/company submitting a tender bid."""
    __tablename__ = "bidders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bidder_id = Column(String(50), unique=True, nullable=False, index=True)
    tender_id = Column(String(100), nullable=False, index=True)
    company_name = Column(String(255), nullable=False)
    gstin = Column(String(20), nullable=True, index=True)
    pan = Column(String(10), nullable=True)
    cin = Column(String(25), nullable=True)
    udyam_number = Column(String(30), nullable=True)
    registered_address = Column(Text, nullable=True)
    is_msme = Column(Boolean, default=False)
    status = Column(String(30), default="PENDING")  # PENDING, PROCESSING, COMPLETED, FAILED
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    documents = relationship("UploadedDocument", back_populates="bidder", cascade="all, delete-orphan")
    verification_results = relationship("VerificationResult", back_populates="bidder", cascade="all, delete-orphan")
    compliance_score = relationship("ComplianceScore", back_populates="bidder", uselist=False, cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="bidder", cascade="all, delete-orphan")


class UploadedDocument(Base):
    """Vendor documents uploaded to the Unified Document Vault."""
    __tablename__ = "uploaded_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bidder_id = Column(String(50), ForeignKey("bidders.bidder_id", ondelete="CASCADE"), nullable=False)
    doc_type = Column(String(50), nullable=False)  # GST_CERTIFICATE, UDYAM, BALANCE_SHEET, etc.
    filename = Column(String(255), nullable=False)
    storage_path = Column(String(500), nullable=False)
    verification_status = Column(String(30), default="PENDING")  # PENDING, VERIFIED, REJECTED, EXPIRED
    verification_badge = Column(String(100), nullable=True)  # DIGILOCKER_VERIFIED, API_SETU_AUTHENTICATED
    expiry_date = Column(DateTime, nullable=True)
    ocr_extracted_json = Column(JSONB, nullable=True)  # Raw OCR extraction output (Person B)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    bidder = relationship("Bidder", back_populates="documents")


class VerificationResult(Base):
    """Results from each government portal adapter run."""
    __tablename__ = "verification_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bidder_id = Column(String(50), ForeignKey("bidders.bidder_id", ondelete="CASCADE"), nullable=False)
    adapter_name = Column(String(100), nullable=False)  # gst_adapter, pan_adapter, etc.
    status = Column(String(30), nullable=False)          # PASS, FAIL, WARN, ERROR
    raw_response = Column(JSONB, nullable=True)          # Full portal response JSON
    discrepancies = Column(JSONB, nullable=True)         # Cross-verification mismatches
    checked_at = Column(DateTime, default=datetime.utcnow)

    bidder = relationship("Bidder", back_populates="verification_results")


class ComplianceScore(Base):
    """Final computed compliance + trust scores for a bidder."""
    __tablename__ = "compliance_scores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bidder_id = Column(String(50), ForeignKey("bidders.bidder_id", ondelete="CASCADE"), unique=True, nullable=False)
    compliance_score = Column(Float, nullable=False)     # 0–100
    risk_level = Column(String(20), nullable=False)      # LOW, MEDIUM, HIGH, CRITICAL
    trust_score = Column(Float, nullable=True)           # 300–900 CIBIL-style (Day 3+ feature)
    trust_rating = Column(String(50), nullable=True)     # PRIME_AAA, MODERATE_BBB, etc.
    ai_recommendation = Column(String(50), nullable=True) # RECOMMEND_APPROVAL, FLAG_FOR_OFFICER_REVIEW, RECOMMEND_REJECTION
    ai_briefing_text = Column(Text, nullable=True)       # Officer-facing plain-English summary
    officer_decision = Column(String(50), nullable=True) # APPROVED, REJECTED, ESCALATED
    officer_id = Column(String(100), nullable=True)
    officer_notes = Column(Text, nullable=True)
    computed_at = Column(DateTime, default=datetime.utcnow)

    bidder = relationship("Bidder", back_populates="compliance_score")


class AuditLog(Base):
    """Immutable CAG / GFR Rule 151 audit trail."""
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    bidder_id = Column(String(50), ForeignKey("bidders.bidder_id", ondelete="CASCADE"), nullable=True)
    event_type = Column(String(100), nullable=False)  # ADAPTER_CALL, OCR_EXTRACTION, RULE_EVAL, OFFICER_DECISION, CHAT_QUERY
    actor = Column(String(100), nullable=True)         # System, officer username, etc.
    details = Column(JSONB, nullable=True)
    severity = Column(String(20), default="INFO")      # INFO, WARNING, CRITICAL
    created_at = Column(DateTime, default=datetime.utcnow)

    bidder = relationship("Bidder", back_populates="audit_logs")
