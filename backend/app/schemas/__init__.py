from typing import List, Optional, Any, Dict, Annotated
from datetime import datetime, timezone
from pydantic import BaseModel, EmailStr, Field, PlainSerializer
from app.models import (
    UserRole, SubmissionStatus, FindingSeverity, FindingType,
    RuleType, CorrectionStatus, ReviewDecision
)

def serialize_utc_datetime(dt: Optional[datetime]) -> Optional[str]:
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt.isoformat().replace("+00:00", "Z")

UtcDateTime = Annotated[datetime, PlainSerializer(serialize_utc_datetime, return_type=str, when_used='json')]
OptionalUtcDateTime = Annotated[Optional[datetime], PlainSerializer(serialize_utc_datetime, return_type=Optional[str], when_used='json')]

# --- AUTH SCHEMAS ---
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserRead"
    organisation: Optional["OrganisationRead"] = None
    role: Optional[str] = None

class TokenPayload(BaseModel):
    sub: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    organisation_name: Optional[str] = None

class UserRead(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    is_active: bool
    is_superuser: bool
    created_at: UtcDateTime

    class Config:
        from_attributes = True

# --- ORGANISATION SCHEMAS ---
class OrganisationCreate(BaseModel):
    name: str
    description: Optional[str] = None

class OrganisationRead(BaseModel):
    id: str
    name: str
    slug: str
    description: Optional[str] = None
    created_at: UtcDateTime

    class Config:
        from_attributes = True

class OrganisationMemberRead(BaseModel):
    id: str
    user_id: str
    organisation_id: str
    role: str
    is_active: bool
    user: UserRead

    class Config:
        from_attributes = True

class AddMemberRequest(BaseModel):
    email: EmailStr
    role: str = "CONTENT_CREATOR"

# --- INVITATION SCHEMAS ---
class InvitationCreate(BaseModel):
    invited_email: EmailStr
    role: str = "CONTENT_CREATOR"

class InvitationRead(BaseModel):
    id: str
    organisation_id: str
    invited_email: EmailStr
    role: str
    token: str
    is_used: bool
    expires_at: UtcDateTime
    created_at: UtcDateTime

    class Config:
        from_attributes = True

class InvitationValidateResponse(BaseModel):
    organisation_name: str
    organisation_id: str
    invited_email: str
    role: str
    expires_at: UtcDateTime

class InvitationAccept(BaseModel):
    full_name: str
    password: str

# --- BRAND GUIDELINES & CHUNKS ---
class GuidelineChunkCreate(BaseModel):
    section_name: str = "General"
    page_number: Optional[int] = None
    content: str
    chunk_index: int = 0

class GuidelineChunkRead(BaseModel):
    id: str
    guideline_id: str
    section_name: str
    page_number: Optional[int]
    content: str
    chunk_index: int
    created_at: UtcDateTime

    class Config:
        from_attributes = True

class BrandGuidelineCreate(BaseModel):
    title: str
    category: str = "Voice & Tone"
    description: Optional[str] = None
    source_document_name: Optional[str] = None
    chunks: Optional[List[GuidelineChunkCreate]] = []

class BrandGuidelineUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class BrandGuidelineRead(BaseModel):
    id: str
    organisation_id: str
    title: str
    category: str
    description: Optional[str]
    source_document_name: Optional[str]
    status: str
    created_at: UtcDateTime
    updated_at: UtcDateTime
    chunks: List[GuidelineChunkRead] = []

    class Config:
        from_attributes = True

# --- APPROVED FACTS ---
class ApprovedFactCreate(BaseModel):
    statement: str
    category: str = "General"
    verification_source: str
    valid_from: OptionalUtcDateTime = None
    valid_until: OptionalUtcDateTime = None

class ApprovedFactUpdate(BaseModel):
    statement: Optional[str] = None
    category: Optional[str] = None
    verification_source: Optional[str] = None
    is_active: Optional[bool] = None

class ApprovedFactRead(BaseModel):
    id: str
    organisation_id: str
    statement: str
    category: str
    verification_source: str
    valid_from: OptionalUtcDateTime
    valid_until: OptionalUtcDateTime
    is_active: bool
    created_at: UtcDateTime

    class Config:
        from_attributes = True

# --- BRAND RULES ---
class BrandRuleCreate(BaseModel):
    rule_type: RuleType = RuleType.TERMINOLOGY
    prohibited_term: Optional[str] = None
    preferred_term: Optional[str] = None
    pattern: Optional[str] = None
    explanation: str
    severity: FindingSeverity = FindingSeverity.HIGH

class BrandRuleUpdate(BaseModel):
    rule_type: Optional[RuleType] = None
    prohibited_term: Optional[str] = None
    preferred_term: Optional[str] = None
    pattern: Optional[str] = None
    explanation: Optional[str] = None
    severity: Optional[FindingSeverity] = None
    is_active: Optional[bool] = None

class BrandRuleRead(BaseModel):
    id: str
    organisation_id: str
    rule_type: RuleType
    prohibited_term: Optional[str]
    preferred_term: Optional[str]
    pattern: Optional[str]
    explanation: str
    severity: FindingSeverity
    is_active: bool
    created_at: UtcDateTime

    class Config:
        from_attributes = True

# --- CORRECTIONS & FINDINGS ---
class CorrectionSuggestionUpdate(BaseModel):
    status: CorrectionStatus
    user_edited_text: Optional[str] = None

class CorrectionSuggestionRead(BaseModel):
    id: str
    finding_id: str
    original_sentence: str
    suggested_replacement: str
    intent_explanation: Optional[str]
    status: CorrectionStatus
    user_edited_text: Optional[str]
    created_at: UtcDateTime

    class Config:
        from_attributes = True

class FindingRead(BaseModel):
    id: str
    report_id: str
    rule_id: Optional[str]
    guideline_chunk_id: Optional[str]
    finding_type: FindingType
    severity: FindingSeverity
    problematic_text: str
    start_pos: Optional[int]
    end_pos: Optional[int]
    explanation: str
    citation_source: Optional[str]
    citation_section: Optional[str]
    citation_chunk_id: Optional[str]
    is_resolved: bool
    created_at: UtcDateTime
    suggestions: List[CorrectionSuggestionRead] = []

    class Config:
        from_attributes = True

# --- ANALYSIS REPORT ---
class AnalysisReportRead(BaseModel):
    model_config = {"protected_namespaces": (), "from_attributes": True}

    id: str
    submission_id: str
    organisation_id: str
    overall_score: float
    summary: Optional[str]
    rules_checked_count: int
    violations_count: int
    unverified_claims_count: int
    model_used: str
    created_at: UtcDateTime
    findings: List[FindingRead] = []

# --- SUBMISSION SCHEMAS ---
class SubmissionCreate(BaseModel):
    title: str
    content_type: str = "blog"
    content: str

class SubmissionUpdate(BaseModel):
    title: Optional[str] = None
    current_text: Optional[str] = None
    status: Optional[SubmissionStatus] = None

class RevisionRead(BaseModel):
    id: str
    submission_id: str
    user_id: str
    revision_number: int
    text_content: str
    change_summary: Optional[str]
    created_at: UtcDateTime

    class Config:
        from_attributes = True

class ReviewCreate(BaseModel):
    decision: ReviewDecision
    comments: Optional[str] = None
    feedback_tags: Optional[List[str]] = []

class ReviewRead(BaseModel):
    id: str
    submission_id: str
    reviewer_id: str
    decision: ReviewDecision
    comments: Optional[str]
    feedback_tags: Optional[List[str]]
    created_at: UtcDateTime
    reviewer_name: Optional[str] = None

    class Config:
        from_attributes = True

class SubmissionRead(BaseModel):
    id: str
    organisation_id: str
    user_id: str
    title: str
    content_type: str
    original_text: str
    current_text: str
    status: SubmissionStatus
    created_at: UtcDateTime
    updated_at: UtcDateTime
    author: Optional[UserRead] = None
    reports: List[AnalysisReportRead] = []
    revisions: List[RevisionRead] = []
    reviews: List[ReviewRead] = []

    class Config:
        from_attributes = True

# --- ANALYTICS ---
class AnalyticsSummary(BaseModel):
    total_submissions: int
    approved_submissions: int
    pending_submissions: int
    average_adherence_score: float
    violations_by_category: Dict[str, int]
    violations_by_severity: Dict[str, int]
    top_recurring_prohibited_terms: List[Dict[str, Any]]
    recent_activity: List[Dict[str, Any]]
    actionable_recommendations: List[str]

# Rebuild forward refs
Token.model_rebuild()
