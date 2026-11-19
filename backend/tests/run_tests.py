import sys
import os

# Add backend to sys.path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, backend_path)

from tests.test_backend import (
    setup_db,
    test_health_check,
    test_demo_login_reviewer,
    test_demo_login_creator,
    test_deterministic_brand_checker,
    test_intent_preserving_correction_engine,
    test_evidence_validator_unsupported_claim,
    test_full_content_submission_and_analysis_workflow
)

def run_all_tests():
    print("=" * 60)
    print("INKLOOM AI — BACKEND AUTOMATED TEST SUITE")
    print("=" * 60)

    # Run fixture
    gen = setup_db()
    next(gen)

    tests = [
        ("Health Check Endpoint", test_health_check),
        ("Demo Login (Reviewer Role)", test_demo_login_reviewer),
        ("Demo Login (Creator Role)", test_demo_login_creator),
        ("Deterministic Brand Checker", test_deterministic_brand_checker),
        ("Intent-Preserving Correction Engine", test_intent_preserving_correction_engine),
        ("Evidence Validator (Unsupported Claims)", test_evidence_validator_unsupported_claim),
        ("Full End-to-End Submission & Governance Lifecycle", test_full_content_submission_and_analysis_workflow)
    ]

    passed = 0
    failed = 0

    for name, test_fn in tests:
        try:
            print(f"Running: {name}...", flush=True)
            test_fn()
            print(f" [PASS] {name}", flush=True)
            passed += 1
        except Exception as e:
            print(f" [FAIL] {name}: {str(e)}", flush=True)
            import traceback
            traceback.print_exc()
            failed += 1

    try:
        next(gen, None)
    except StopIteration:
        pass

    print("=" * 60, flush=True)
    print(f"TOTAL: {passed + failed} | PASSED: {passed} | FAILED: {failed}", flush=True)
    print("=" * 60, flush=True)

    if failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    run_all_tests()
