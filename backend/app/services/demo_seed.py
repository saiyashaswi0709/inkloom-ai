import logging
from sqlalchemy.orm import Session
from app.models import (
    User, Organisation, OrganisationMembership, UserRole,
    BrandGuideline, GuidelineChunk, ApprovedFact, BrandRule,
    Submission, SubmissionStatus, FindingSeverity, RuleType,
    AnalysisReport, Finding, FindingType, CorrectionSuggestion,
    CorrectionStatus, Revision, Review, ReviewDecision
)
from app.core.security import get_password_hash

logger = logging.getLogger("inkloom.seed")

def seed_demo_data(db: Session) -> None:
    # Check if demo organisation already exists
    existing_org = db.query(Organisation).filter(Organisation.slug == "aura-financial").first()
    if existing_org:
        return

    logger.info("Seeding demo organisation and initial governance data...")

    # 1. Create Demo Users
    reviewer_user = User(
        email="reviewer@inkloom.ai",
        full_name="Sarah Chen (Lead Brand Director)",
        hashed_password=get_password_hash("demo1234"),
        is_active=True,
        is_superuser=False
    )
    creator_user = User(
        email="creator@inkloom.ai",
        full_name="Alex Rivera (Content Strategist)",
        hashed_password=get_password_hash("demo1234"),
        is_active=True,
        is_superuser=False
    )
    db.add_all([reviewer_user, creator_user])
    db.flush()

    # 2. Create Demo Organisation
    org = Organisation(
        name="Aura Global Technologies",
        slug="aura-financial",
        description="Global institutional financial infrastructure and security platform."
    )
    db.add(org)
    db.flush()

    # 3. Memberships
    m1 = OrganisationMembership(user_id=reviewer_user.id, organisation_id=org.id, role=UserRole.REVIEWER)
    m2 = OrganisationMembership(user_id=creator_user.id, organisation_id=org.id, role=UserRole.CONTENT_CREATOR)
    db.add_all([m1, m2])
    db.flush()

    # 4. Brand Guidelines & Chunks
    g1 = BrandGuideline(
        organisation_id=org.id,
        title="Corporate Voice, Tone & Messaging Standards",
        category="Voice & Tone",
        description="Core principles for all customer-facing and market publications.",
        source_document_name="Aura_Brand_Book_2025.pdf",
        status="active"
    )
    db.add(g1)
    db.flush()

    c1 = GuidelineChunk(
        guideline_id=g1.id,
        section_name="Tone of Authority & Precision",
        page_number=4,
        content="Our voice is authoritative, disciplined, and measured. Never use hyperbolic language such as 'unbreakable', 'magic', or '100% risk-free'. Frame all capabilities around verifiable engineering rigor and institutional risk models.",
        chunk_index=0
    )
    c2 = GuidelineChunk(
        guideline_id=g1.id,
        section_name="Clarity & Customer Respect",
        page_number=6,
        content="Avoid hype-driven crypto jargon. When describing digital assets, refer to them as institutional digital assets or tokenized securities, not speculative tokens.",
        chunk_index=1
    )
    db.add_all([c1, c2])

    g2 = BrandGuideline(
        organisation_id=org.id,
        title="Security & Technical Governance Protocols",
        category="Security & Compliance",
        description="Mandatory disclosures and legal parameters for infrastructure descriptions.",
        source_document_name="Infosec_Public_Policy_v4.docx",
        status="active"
    )
    db.add(g2)
    db.flush()

    c3 = GuidelineChunk(
        guideline_id=g2.id,
        section_name="Cryptographic Standard Disclosures",
        page_number=2,
        content="Hardware security modules must always be described as FIPS 140-2 Level 3 validated. Never claim zero risk or immunity from cyber events; articulate defense-in-depth safeguards.",
        chunk_index=0
    )
    db.add(c3)

    # 5. Approved Facts
    facts = [
        ApprovedFact(
            organisation_id=org.id,
            statement="Aura SecureCore utilizes AES-256 GCM hardware encryption across all 14 global data centers.",
            category="Security",
            verification_source="Audited SOC-2 Type II Report 2025 (Section 3.2)"
        ),
        ApprovedFact(
            organisation_id=org.id,
            statement="Average transaction settlement latency is verified at 14 milliseconds.",
            category="Performance",
            verification_source="Q3 Engineering Benchmark Publication"
        ),
        ApprovedFact(
            organisation_id=org.id,
            statement="Over 2,400 enterprise institutions actively deploy the Aura Cloud platform.",
            category="Market Reach",
            verification_source="2025 Annual Shareholder Review"
        ),
        ApprovedFact(
            organisation_id=org.id,
            statement="Zero customer data breaches recorded since inception in 2019.",
            category="Security Track Record",
            verification_source="Chief Information Security Officer Annual Attestation"
        )
    ]
    db.add_all(facts)

    # 6. Brand Rules (Deterministic)
    rules = [
        BrandRule(
            organisation_id=org.id,
            rule_type=RuleType.RESTRICTED_PHRASE,
            prohibited_term="100% risk-free",
            preferred_term="rigorously risk-managed",
            explanation="Financial regulations prohibit absolute zero-risk claims. Use precise risk-managed terminology.",
            severity=FindingSeverity.CRITICAL
        ),
        BrandRule(
            organisation_id=org.id,
            rule_type=RuleType.RESTRICTED_PHRASE,
            prohibited_term="unbreakable security",
            preferred_term="defense-in-depth cryptographic architecture",
            explanation="Absolute security claims violate technical governance guidelines.",
            severity=FindingSeverity.CRITICAL
        ),
        BrandRule(
            organisation_id=org.id,
            rule_type=RuleType.TERMINOLOGY,
            prohibited_term="crypto wallet",
            preferred_term="institutional digital asset vault",
            explanation="Maintain institutional brand stature. 'Crypto wallet' implies retail speculation.",
            severity=FindingSeverity.HIGH
        ),
        BrandRule(
            organisation_id=org.id,
            rule_type=RuleType.TERMINOLOGY,
            prohibited_term="instantaneous settlement",
            preferred_term="sub-second settlement latency",
            explanation="Settlement occurs in 14ms; avoid scientifically inaccurate 'instantaneous' claims.",
            severity=FindingSeverity.MEDIUM
        ),
        BrandRule(
            organisation_id=org.id,
            rule_type=RuleType.TERMINOLOGY,
            prohibited_term="cheapest in the market",
            preferred_term="cost-optimized enterprise tier",
            explanation="Brand voice avoids race-to-the-bottom price rhetoric.",
            severity=FindingSeverity.HIGH
        )
    ]
    db.add_all(rules)
    db.flush()

    # 7. Sample Initial Submissions
    sub1_text = """Aura Global is thrilled to announce our new custody service. With unbreakable security and instantaneous settlement, our new crypto wallet ensures your institutional investments are 100% risk-free. Over 50,000 banks trust our system every second."""
    
    sub1 = Submission(
        organisation_id=org.id,
        user_id=creator_user.id,
        title="Institutional Custody Expansion Press Release",
        content_type="press_release",
        original_text=sub1_text,
        current_text=sub1_text,
        status=SubmissionStatus.NEEDS_CHANGES
    )
    db.add(sub1)
    db.flush()

    rev1 = Revision(
        submission_id=sub1.id,
        user_id=creator_user.id,
        revision_number=1,
        text_content=sub1_text,
        change_summary="Initial draft submitted for governance review."
    )
    db.add(rev1)

    # Initial Analysis Report for sub1
    report1 = AnalysisReport(
        submission_id=sub1.id,
        organisation_id=org.id,
        overall_score=54.0,
        summary="Draft contains 3 high-severity restricted phrase violations, 1 terminology mismatch, and an unsubstantiated factual claim regarding bank adoption.",
        rules_checked_count=len(rules),
        violations_count=4,
        unverified_claims_count=1,
        model_used="Nemotron-70B + RuleEngine"
    )
    db.add(report1)
    db.flush()

    # Pre-add findings
    f1 = Finding(
        report_id=report1.id,
        rule_id=rules[1].id,
        finding_type=FindingType.RESTRICTED_PHRASE,
        severity=FindingSeverity.CRITICAL,
        problematic_text="unbreakable security",
        start_pos=sub1_text.find("unbreakable security"),
        end_pos=sub1_text.find("unbreakable security") + len("unbreakable security"),
        explanation="Absolute security claims violate technical governance guidelines and SEC disclosures.",
        citation_source="Aura_Brand_Book_2025.pdf",
        citation_section="Tone of Authority & Precision"
    )
    db.add(f1)
    db.flush()

    cs1 = CorrectionSuggestion(
        finding_id=f1.id,
        original_sentence="With unbreakable security and instantaneous settlement, our new crypto wallet ensures your institutional investments are 100% risk-free.",
        suggested_replacement="With a defense-in-depth cryptographic architecture and sub-second settlement latency, our institutional digital asset vault ensures your institutional investments are rigorously risk-managed.",
        intent_explanation="Preserves the confident security positioning while replacing prohibited hyperbole with compliant technical terminology.",
        status=CorrectionStatus.PENDING
    )
    db.add(cs1)

    f2 = Finding(
        report_id=report1.id,
        finding_type=FindingType.UNSUPPORTED_CLAIM,
        severity=FindingSeverity.HIGH,
        problematic_text="Over 50,000 banks trust our system every second.",
        start_pos=sub1_text.find("Over 50,000 banks trust our system every second."),
        end_pos=sub1_text.find("Over 50,000 banks trust our system every second.") + len("Over 50,000 banks trust our system every second."),
        explanation="Approved corporate records confirm 2,400 enterprise institutions, not 50,000 banks.",
        citation_source="Approved Fact (2025 Annual Shareholder Review)",
        citation_section="Market Reach"
    )
    db.add(f2)
    db.flush()

    cs2 = CorrectionSuggestion(
        finding_id=f2.id,
        original_sentence="Over 50,000 banks trust our system every second.",
        suggested_replacement="Over 2,400 enterprise institutions actively deploy our systems with verified 14ms latency.",
        intent_explanation="Replaces unverified claim with officially audited corporate metrics.",
        status=CorrectionStatus.PENDING
    )
    db.add(cs2)

    db.commit()
    logger.info("Demo organisation successfully seeded!")
