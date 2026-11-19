import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Text, Integer, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Index, JSON, Float
)
from sqlalchemy.orm import relationship
from app.core.database import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class UserRole(str, enum.Enum):
    """Canonical role identifiers. DB stores role as plain String(50) for flexibility."""
    ORGANISATION_ADMIN = "ORGANISATION_ADMIN"
    BRAND_MANAGER = "BRAND_MANAGER"
    CONTENT_CREATOR = "CONTENT_CREATOR"
    REVIEWER = "REVIEWER"
    ANALYST = "ANALYST"

def normalize_role(role_str: str) -> str:
    """Map legacy DB values (admin/creator/reviewer) to canonical new strings."""
    if not role_str:
        return "CONTENT_CREATOR"
    val = role_str.value if hasattr(role_str, "value") else str(role_str)
    val_upper = val.upper()
    mapping = {
        "ADMIN": "ORGANISATION_ADMIN",
        "ORGANISATION_ADMIN": "ORGANISATION_ADMIN",
        "BRAND_MANAGER": "BRAND_MANAGER",
        "BRANDMANAGER": "BRAND_MANAGER",
        "CREATOR": "CONTENT_CREATOR",
        "CONTENT_CREATOR": "CONTENT_CREATOR",
        "REPORTER": "CONTENT_CREATOR",
        "REVIEWER": "REVIEWER",
        "ANALYST": "ANALYST",
    }
    return mapping.get(val_upper, "CONTENT_CREATOR")

class SubmissionStatus(str, enum.Enum):
    DRAFT = "draft"
    ANALYSED = "analysed"
    NEEDS_CHANGES = "needs_changes"
    READY_FOR_REVIEW = "ready_for_review"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    CHANGES_REQUESTED = "changes_requested"

class FindingSeverity(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"

class FindingType(str, enum.Enum):
    TERMINOLOGY = "terminology"
    RESTRICTED_PHRASE = "restricted_phrase"
    UNSUPPORTED_CLAIM = "unsupported_claim"
    TONE_INCONSISTENCY = "tone_inconsistency"
    GUIDELINE_VIOLATION = "guideline_violation"

class RuleType(str, enum.Enum):
    TERMINOLOGY = "terminology"
    RESTRICTED_PHRASE = "restricted_phrase"
    TONE = "tone"
    REGEX = "regex"

class CorrectionStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EDITED = "edited"

class ReviewDecision(str, enum.Enum):
    APPROVED = "approved"
    CHANGES_REQUESTED = "changes_requested"

# 1. User Model
class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    memberships = relationship("OrganisationMembership", back_populates="user", cascade="all, delete-orphan")
    submissions = relationship("Submission", back_populates="author")
    revisions = relationship("Revision", back_populates="author")
    reviews = relationship("Review", back_populates="reviewer")
    audit_logs = relationship("AuditLog", back_populates="user")

# 2. Organisation Model
class Organisation(Base):
    __tablename__ = "organisations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    memberships = relationship("OrganisationMembership", back_populates="organisation", cascade="all, delete-orphan")
    guidelines = relationship("BrandGuideline", back_populates="organisation", cascade="all, delete-orphan")
    facts = relationship("ApprovedFact", back_populates="organisation", cascade="all, delete-orphan")
    rules = relationship("BrandRule", back_populates="organisation", cascade="all, delete-orphan")
    submissions = relationship("Submission", back_populates="organisation", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="organisation", cascade="all, delete-orphan")

# 3. OrganisationMembership Model
class OrganisationMembership(Base):
    __tablename__ = "organisation_memberships"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    organisation_id = Column(String(36), ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(50), default="CONTENT_CREATOR", nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    user = relationship("User", back_populates="memberships")
    organisation = relationship("Organisation", back_populates="memberships")

    __table_args__ = (
        Index("idx_org_user_unique", "organisation_id", "user_id", unique=True),
    )

# 4. BrandGuideline Model
class BrandGuideline(Base):
    __tablename__ = "brand_guidelines"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organisation_id = Column(String(36), ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False, default="General") # e.g. Voice & Tone, Visual, Legal, Product
    description = Column(Text, nullable=True)
    source_document_name = Column(String(255), nullable=True)
    status = Column(String(50), default="active")
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    organisation = relationship("Organisation", back_populates="guidelines")
    chunks = relationship("GuidelineChunk", back_populates="guideline", cascade="all, delete-orphan")

# 5. GuidelineChunk Model
class GuidelineChunk(Base):
    __tablename__ = "guideline_chunks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    guideline_id = Column(String(36), ForeignKey("brand_guidelines.id", ondelete="CASCADE"), nullable=False, index=True)
    section_name = Column(String(255), nullable=False, default="General")
    page_number = Column(Integer, nullable=True)
    content = Column(Text, nullable=False)
    chunk_index = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    guideline = relationship("BrandGuideline", back_populates="chunks")
    findings = relationship("Finding", back_populates="guideline_chunk")

# 6. ApprovedFact Model
class ApprovedFact(Base):
    __tablename__ = "approved_facts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organisation_id = Column(String(36), ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False, index=True)
    statement = Column(Text, nullable=False)
    category = Column(String(100), default="General") # e.g. Financials, Performance, Security, Compliance
    verification_source = Column(String(255), nullable=False)
    valid_from = Column(DateTime(timezone=True), nullable=True)
    valid_until = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    organisation = relationship("Organisation", back_populates="facts")

# 7. BrandRule Model
class BrandRule(Base):
    __tablename__ = "brand_rules"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organisation_id = Column(String(36), ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False, index=True)
    rule_type = Column(SQLEnum(RuleType), default=RuleType.TERMINOLOGY, nullable=False)
    prohibited_term = Column(String(255), nullable=True)
    preferred_term = Column(String(255), nullable=True)
    pattern = Column(String(500), nullable=True) # regex pattern if regex type
    explanation = Column(Text, nullable=False)
    severity = Column(SQLEnum(FindingSeverity), default=FindingSeverity.HIGH, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    organisation = relationship("Organisation", back_populates="rules")
    findings = relationship("Finding", back_populates="rule")

# 8. Submission Model
class Submission(Base):
    __tablename__ = "submissions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organisation_id = Column(String(36), ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    content_type = Column(String(100), default="general") # blog, press_release, marketing_copy, technical_doc, social_post
    original_text = Column(Text, nullable=False)
    current_text = Column(Text, nullable=False)
    status = Column(SQLEnum(SubmissionStatus), default=SubmissionStatus.DRAFT, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    organisation = relationship("Organisation", back_populates="submissions")
    author = relationship("User", back_populates="submissions")
    reports = relationship("AnalysisReport", back_populates="submission", cascade="all, delete-orphan", order_by="desc(AnalysisReport.created_at)")
    revisions = relationship("Revision", back_populates="submission", cascade="all, delete-orphan", order_by="Revision.revision_number")
    reviews = relationship("Review", back_populates="submission", cascade="all, delete-orphan", order_by="desc(Review.created_at)")

# 9. AnalysisReport Model
class AnalysisReport(Base):
    __tablename__ = "analysis_reports"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    submission_id = Column(String(36), ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False, index=True)
    organisation_id = Column(String(36), ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False, index=True)
    overall_score = Column(Float, default=100.0) # Brand adherence score 0-100
    summary = Column(Text, nullable=True)
    rules_checked_count = Column(Integer, default=0)
    violations_count = Column(Integer, default=0)
    unverified_claims_count = Column(Integer, default=0)
    model_used = Column(String(100), default="Nemotron-70B")
    created_at = Column(DateTime(timezone=True), default=utc_now)

    submission = relationship("Submission", back_populates="reports")
    findings = relationship("Finding", back_populates="report", cascade="all, delete-orphan")

# 10. Finding Model
class Finding(Base):
    __tablename__ = "findings"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    report_id = Column(String(36), ForeignKey("analysis_reports.id", ondelete="CASCADE"), nullable=False, index=True)
    rule_id = Column(String(36), ForeignKey("brand_rules.id", ondelete="SET NULL"), nullable=True)
    guideline_chunk_id = Column(String(36), ForeignKey("guideline_chunks.id", ondelete="SET NULL"), nullable=True)
    finding_type = Column(SQLEnum(FindingType), nullable=False)
    severity = Column(SQLEnum(FindingSeverity), default=FindingSeverity.MEDIUM, nullable=False)
    problematic_text = Column(Text, nullable=False)
    start_pos = Column(Integer, nullable=True)
    end_pos = Column(Integer, nullable=True)
    explanation = Column(Text, nullable=False)
    citation_source = Column(String(255), nullable=True)
    citation_section = Column(String(255), nullable=True)
    citation_chunk_id = Column(String(36), nullable=True)
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    report = relationship("AnalysisReport", back_populates="findings")
    rule = relationship("BrandRule", back_populates="findings")
    guideline_chunk = relationship("GuidelineChunk", back_populates="findings")
    suggestions = relationship("CorrectionSuggestion", back_populates="finding", cascade="all, delete-orphan")

# 11. CorrectionSuggestion Model
class CorrectionSuggestion(Base):
    __tablename__ = "correction_suggestions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    finding_id = Column(String(36), ForeignKey("findings.id", ondelete="CASCADE"), nullable=False, index=True)
    original_sentence = Column(Text, nullable=False)
    suggested_replacement = Column(Text, nullable=False)
    intent_explanation = Column(Text, nullable=True)
    status = Column(SQLEnum(CorrectionStatus), default=CorrectionStatus.PENDING, nullable=False)
    user_edited_text = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    finding = relationship("Finding", back_populates="suggestions")

# 12. Revision Model
class Revision(Base):
    __tablename__ = "revisions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    submission_id = Column(String(36), ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    revision_number = Column(Integer, nullable=False)
    text_content = Column(Text, nullable=False)
    change_summary = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    submission = relationship("Submission", back_populates="revisions")
    author = relationship("User", back_populates="revisions")

# 13. Review Model
class Review(Base):
    __tablename__ = "reviews"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    submission_id = Column(String(36), ForeignKey("submissions.id", ondelete="CASCADE"), nullable=False, index=True)
    reviewer_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    decision = Column(SQLEnum(ReviewDecision), nullable=False)
    comments = Column(Text, nullable=True)
    feedback_tags = Column(JSON, nullable=True) # e.g. ["Tone check passed", "Fact verified"]
    created_at = Column(DateTime(timezone=True), default=utc_now)

    submission = relationship("Submission", back_populates="reviews")
    reviewer = relationship("User", back_populates="reviews")

# 14. AuditLog Model
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organisation_id = Column(String(36), ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String(100), nullable=False) # e.g. "SUBMISSION_ANALYSED", "RULE_CREATED", "CONTENT_APPROVED"
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String(36), nullable=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    organisation = relationship("Organisation", back_populates="audit_logs")
    user = relationship("User", back_populates="audit_logs")

# 15. Invitation Model
class Invitation(Base):
    __tablename__ = "invitations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    organisation_id = Column(String(36), ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False, index=True)
    invited_email = Column(String(255), nullable=False, index=True)
    role = Column(String(50), default="CONTENT_CREATOR", nullable=False)
    token = Column(String(100), unique=True, nullable=False, index=True)
    invited_by_user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    is_used = Column(Boolean, default=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    organisation = relationship("Organisation")
    invited_by = relationship("User", foreign_keys=[invited_by_user_id])
