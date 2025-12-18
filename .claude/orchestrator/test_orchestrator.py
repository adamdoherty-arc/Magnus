#!/usr/bin/env python3
"""
Test Orchestrator - Verify all components work correctly
"""
import sys
from pathlib import Path

# Add orchestrator directory to path
sys.path.insert(0, str(Path(__file__).parent))

from main_orchestrator import get_orchestrator


def test_pre_flight_validation():
    """Test pre-flight validation"""
    print("\n" + "="*60)
    print("TEST 1: Pre-Flight Validation")
    print("="*60)

    orchestrator = get_orchestrator()

    # Test 1: Should FAIL (horizontal line request)
    print("\n[1.1] Testing forbidden horizontal line request...")
    result = orchestrator.orchestrate("Add a horizontal divider to the dashboard")

    if not result.validation_results.get("passed"):
        print("PASS: Correctly blocked horizontal line request")
    else:
        print("FAIL: Should have blocked horizontal line request")
        return False

    # Test 2: Should PASS (normal request)
    print("\n[1.2] Testing normal request...")
    result = orchestrator.orchestrate("Add a section header to the page")

    if result.validation_results.get("passed"):
        print("PASS: Correctly allowed normal request")
    else:
        print("FAIL: Should have allowed normal request")
        return False

    # Test 3: Feature identification
    print("\n[1.3] Testing feature identification...")
    result = orchestrator.orchestrate(
        "Update positions page",
        context={"files": ["positions_page_improved.py"]}
    )

    if "robinhood-positions" in result.features_involved:
        print("PASS: Correctly identified robinhood-positions feature")
    else:
        print(f"FAIL: Feature identification failed. Got: {result.features_involved}")
        return False

    print("\nAll pre-flight validation tests passed!")
    return True


def test_qa_validation():
    """Test QA validation"""
    print("\n" + "="*60)
    print("TEST 2: QA Validation")
    print("="*60)

    orchestrator = get_orchestrator()

    # Create a test file with violations
    test_file = Path(__file__).parent / "test_violations.py"

    print("\n[2.1] Creating test file with violations...")
    with open(test_file, 'w') as f:
        f.write('import streamlit as st\n')
        f.write('st.markdown("---")\n')  # Violation
        f.write('st.divider()\n')  # Violation

    # Run QA
    print("\n[2.2] Running QA...")
    result = orchestrator.post_execution_qa([str(test_file)])

    if not result.get("passed"):
        print("PASS: Correctly detected violations")
        print(f"   Found {len(result.get('violations', []))} violations")
    else:
        print("FAIL: Should have detected violations")
        test_file.unlink()
        return False

    # Clean up
    test_file.unlink()

    print("\nAll QA validation tests passed!")
    return True


def test_rule_engine():
    """Test rule engine"""
    print("\n" + "="*60)
    print("TEST 3: Rule Engine")
    print("="*60)

    orchestrator = get_orchestrator()

    print("\n[3.1] Testing rule loading...")
    summary = orchestrator.rule_engine.get_rule_summary()
    print(summary)

    if "UI rules:" in summary and "Code rules:" in summary:
        print("PASS: Rules loaded successfully")
    else:
        print("FAIL: Rules not loaded")
        return False

    print("\nAll rule engine tests passed!")
    return True


def test_feature_registry():
    """Test feature registry"""
    print("\n" + "="*60)
    print("TEST 4: Feature Registry")
    print("="*60)

    orchestrator = get_orchestrator()

    print("\n[4.1] Testing feature identification...")
    features = orchestrator.identify_features(["positions_page_improved.py"])

    if "robinhood-positions" in features:
        print("PASS: Feature registry works")
        print(f"   Found features: {features}")
    else:
        print("FAIL: Feature registry not working")
        return False

    print("\n[4.2] Testing specialist agent mapping...")
    agents = orchestrator.get_specialist_agents(features)

    if agents:
        print("PASS: Specialist agents identified")
        print(f"   Agents: {agents}")
    else:
        print("WARNING: No specialist agents found")

    print("\nAll feature registry tests passed!")
    return True


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*80)
    print("ORCHESTRATOR TEST SUITE")
    print("="*80)

    tests = [
        ("Pre-Flight Validation", test_pre_flight_validation),
        ("QA Validation", test_qa_validation),
        ("Rule Engine", test_rule_engine),
        ("Feature Registry", test_feature_registry)
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                print(f"\nFAILED: {test_name}")
        except Exception as e:
            failed += 1
            print(f"\nERROR in {test_name}: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")

    if failed == 0:
        print("\nALL TESTS PASSED! Orchestrator is ready to use.")
        return True
    else:
        print(f"\n{failed} test(s) failed. Please review output above.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
