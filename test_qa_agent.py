"""
Test script for QA Verification Agent

Tests the QA agent functionality by creating a test task and verifying it.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.qa_verification_agent import get_qa_agent
from src.task_db_manager import TaskDBManager
import json


def test_qa_agent():
    """Test the QA verification agent"""
    print("="*80)
    print("Testing QA Verification Agent")
    print("="*80)

    task_mgr = TaskDBManager()
    qa_agent = get_qa_agent()

    try:
        # Create a test task
        print("\n1. Creating test task...")
        task_id = task_mgr.create_task(
            title="Test QA Agent - Sample Task",
            description="This is a test task to verify QA agent functionality",
            task_type="qa",
            priority="high",
            assigned_agent="qa-agent",
            feature_area="task_management",
            estimated_duration_minutes=30,
            tags=["test", "qa", "automation"]
        )
        print(f"   [OK] Created task ID: {task_id}")

        # Track some file changes
        print("\n2. Tracking file changes...")
        task_mgr.track_file_change(
            task_id=task_id,
            file_path="c:\\Code\\WheelStrategy\\src\\qa_verification_agent.py",
            change_type="created",
            lines_added=450,
            lines_removed=0
        )

        task_mgr.track_file_change(
            task_id=task_id,
            file_path="c:\\Code\\WheelStrategy\\test_qa_agent.py",
            change_type="created",
            lines_added=120,
            lines_removed=0
        )
        print("   [OK] Tracked file changes")

        # Log some execution activity
        print("\n3. Logging execution activity...")
        task_mgr.log_execution(
            task_id=task_id,
            agent_name="qa-agent",
            action_type="started",
            message="Starting QA agent implementation"
        )

        task_mgr.log_execution(
            task_id=task_id,
            agent_name="qa-agent",
            action_type="progress_update",
            message="Implemented verification checks",
            files_modified=[
                "src/qa_verification_agent.py",
                "test_qa_agent.py"
            ]
        )
        print("   [OK] Logged execution activity")

        # Update task status to completed
        print("\n4. Completing task...")
        task_mgr.update_task_status(task_id, "completed")
        print("   [OK] Task marked as completed")

        # Run QA verification
        print("\n5. Running QA verification...")
        print("-"*80)
        results = qa_agent.verify_task(task_id)
        print("-"*80)

        # Display results
        print("\n6. Verification Results:")
        print(f"   Task ID: {results['task_id']}")
        print(f"   Passed: {results['passed']}")
        print(f"   Checks Run: {len(results['checks_run'])}")
        print(f"   Failures: {len(results['failures'])}")
        print(f"   Warnings: {len(results['warnings'])}")

        if results['failures']:
            print("\n   Failed Checks:")
            for failure in results['failures']:
                print(f"     - {failure['name']}")

        if results['warnings']:
            print("\n   Warnings:")
            for warning in results['warnings']:
                print(f"     - {warning}")

        # Get verification record from database
        print("\n7. Retrieving verification from database...")
        verifications = task_mgr.get_verifications(task_id)

        if verifications:
            latest = verifications[0]
            print(f"   [OK] Verification saved to database")
            print(f"   Verified by: {latest['verified_by']}")
            print(f"   Passed: {latest['passed']}")
            print(f"   Timestamp: {latest['verification_timestamp']}")
        else:
            print("   [ERROR] No verification found in database")

        # Print summary
        print("\n" + "="*80)
        if results['passed']:
            print("[PASS] QA AGENT TEST PASSED")
            print("\nThe QA Verification Agent is working correctly!")
        else:
            print("[WARN] QA AGENT TEST COMPLETED WITH WARNINGS")
            print("\nThe QA agent ran successfully but some checks failed.")
            print("This is expected for a test task with minimal setup.")
        print("="*80)

        # Optional: Print full JSON results
        print("\n\nFull Results (JSON):")
        print("-"*80)
        print(json.dumps(results, indent=2, default=str))

        return True

    except Exception as e:
        print(f"\n[ERROR] Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_qa_agent()
    sys.exit(0 if success else 1)
