from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base, get_db
import app.models
from app.main import app
from app.services.demo_seed import seed_demo_data
from app.services.brand_checker import BrandChecker
from app.models import BrandRule, RuleType, FindingSeverity
from app.services.evidence_validator import EvidenceValidator
from app.services.correction_engine import CorrectionEngine

# In-memory test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_inkloom.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    seed_demo_data(db)
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_demo_login_reviewer():
    response = client.post("/api/v1/auth/demo-login", json={"role": "reviewer"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "reviewer"
    assert data["user"]["email"] == "reviewer@inkloom.ai"

def test_demo_login_creator():
    response = client.post("/api/v1/auth/demo-login", json={"role": "creator"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "creator"
    assert data["user"]["email"] == "creator@inkloom.ai"

def test_deterministic_brand_checker():
    rules = [
        BrandRule(
            id="r1",
            organisation_id="org1",
            rule_type=RuleType.RESTRICTED_PHRASE,
            prohibited_term="100% risk-free",
            preferred_term="rigorously risk-managed",
            explanation="Prohibited by compliance",
            severity=FindingSeverity.CRITICAL,
            is_active=True
        ),
        BrandRule(
            id="r2",
            organisation_id="org1",
            rule_type=RuleType.TERMINOLOGY,
            prohibited_term="crypto wallet",
            preferred_term="institutional digital asset vault",
            explanation="Brand terminology standard",
            severity=FindingSeverity.HIGH,
            is_active=True
        )
    ]

    test_content = "Our crypto wallet provides 100% risk-free yield."
    matches = BrandChecker.check_content(test_content, rules)

    assert len(matches) == 2
    assert matches[0].problematic_text == "crypto wallet"
    assert matches[1].problematic_text == "100% risk-free"

def test_intent_preserving_correction_engine():
    sentence = "Our new crypto wallet guarantees instantaneous settlement."
    corrected = CorrectionEngine.build_deterministic_correction(
        sentence=sentence,
        problematic_text="crypto wallet",
        preferred_term="institutional digital asset vault",
        rule_explanation="Use institutional terminology"
    )
    assert "institutional digital asset vault" in corrected
    assert "instantaneous settlement" in corrected  # Author intent preserved

def test_evidence_validator_unsupported_claim():
    is_valid, source, section, chunk_id = EvidenceValidator.validate_citation(
        citation_source=None,
        citation_section=None,
        claimed_evidence_text=None,
        available_chunks=[],
        available_facts=[]
    )
    assert is_valid is False
    assert "Unverified" in source

def test_full_content_submission_and_analysis_workflow():
    # 1. Login as creator
    login_res = client.post("/api/v1/auth/demo-login", json={"role": "creator"})
    token = login_res.json()["access_token"]
    org_id = login_res.json()["organisation"]["id"]

    headers = {
        "Authorization": f"Bearer {token}",
        "X-Organisation-Id": org_id
    }

    # 2. Create submission
    sub_payload = {
        "title": "Automated Test Press Release",
        "content_type": "press_release",
        "content": "Aura Global provides unbreakable security with our new crypto wallet."
    }
    sub_res = client.post("/api/v1/submissions", json=sub_payload, headers=headers)
    assert sub_res.status_code == 200
    sub_data = sub_res.json()
    submission_id = sub_data["id"]

    # 3. Run analysis
    analysis_res = client.post("/api/v1/analysis/run", json={"submission_id": submission_id}, headers=headers)
    assert analysis_res.status_code == 200
    report = analysis_res.json()

    assert report["violations_count"] >= 1
    assert report["overall_score"] < 100.0

    # 4. Verify findings and suggestions
    assert len(report["findings"]) >= 1
    finding = report["findings"][0]
    assert len(finding["suggestions"]) >= 1
    suggestion = finding["suggestions"][0]

    # 5. Accept correction
    corr_res = client.put(
        f"/api/v1/corrections/{suggestion['id']}",
        json={"status": "accepted"},
        headers=headers
    )
    assert corr_res.status_code == 200
    assert corr_res.json()["status"] == "accepted"

    # 6. Check updated submission has new revision
    updated_sub = client.get(f"/api/v1/submissions/{submission_id}", headers=headers).json()
    assert len(updated_sub["revisions"]) >= 2

    # 7. Submit for review
    submit_review_res = client.post(f"/api/v1/submissions/{submission_id}/submit-for-review", headers=headers)
    assert submit_review_res.status_code == 200
    assert submit_review_res.json()["status"] == "in_review"

    # 8. Login as Reviewer and Approve
    rev_login = client.post("/api/v1/auth/demo-login", json={"role": "reviewer"})
    rev_token = rev_login.json()["access_token"]
    rev_headers = {
        "Authorization": f"Bearer {rev_token}",
        "X-Organisation-Id": org_id
    }

    review_res = client.post(
        f"/api/v1/reviews?submission_id={submission_id}",
        json={
            "decision": "approved",
            "comments": "All brand rules verified and aligned with Aura governance.",
            "feedback_tags": ["Compliant", "Verified"]
        },
        headers=rev_headers
    )
    assert review_res.status_code == 200
    assert review_res.json()["decision"] == "approved"

    # 9. Verify final submission status is approved
    final_sub = client.get(f"/api/v1/submissions/{submission_id}", headers=headers).json()
    assert final_sub["status"] == "approved"
