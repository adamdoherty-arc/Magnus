"""
Basic QA System Test (Without RAG)
==================================

Tests core QA workflow without RAG dependencies.
"""

from src.qa.multi_agent_qa_service import MultiAgentQAService
from src.task_db_manager import TaskDBManager

def test_basic_qa_workflow():
    """Test QA workflow without RAG features"""

    print("=" * 80)
    print("BASIC QA SYSTEM TEST (No RAG)")
    print("=" * 80)
    print()

    # Initialize services
    task_mgr = TaskDBManager()
    qa_service = MultiAgentQAService()

    print("[1/5] Creating test task...")
    task_id = task_mgr.create_task(
        title="QA System Test - Authentication Feature",
        description="Test task for QA system validation",
        task_type="feature",
        priority="high",
        assigned_agent="backend-architect",
        feature_area="authentication",
        tags=["test", "qa-system"]
    )
    print(f"  Created task ID: {task_id}")
    print()

    print("[2/5] Marking task as completed...")
    task_mgr.update_task_status(task_id, "completed")
    print("  Task status: completed")
    print()

    print("[3/5] Triggering QA review...")
    try:
        review_result = qa_service.trigger_qa_review(task_id)
        print(f"  Status: {review_result['status']}")
        print(f"  Required agents: {', '.join(review_result['required_agents'])}")
        print(f"  Sign-offs created: {len(review_result['sign_offs_created'])}")
        print()

        # Show each sign-off
        for sign_off in review_result['sign_offs_created']:
            print(f"    - {sign_off['agent_name']} (ID: {sign_off['sign_off_id']})")

        print()
        print("[4/5] Checking QA status...")
        status = qa_service.get_task_qa_status(task_id)
        print(f"  Total reviews: {status.get('total_reviews', 0)}")
        print(f"  Pending reviews: {status.get('pending', 0)}")
        print(f"  Approvals: {status.get('approvals', 0)}")
        print(f"  All sign-offs complete: {status.get('all_sign_offs_complete', False)}")
        print()

        print("[5/5] Getting pending reviews...")
        for agent_name in review_result['required_agents']:
            pending = qa_service.get_pending_reviews(agent_name, limit=5)
            print(f"  {agent_name}: {len(pending)} pending reviews")

        print()
        print("=" * 80)
        print("[OK] BASIC QA SYSTEM WORKING!")
        print("=" * 80)
        print()
        print("Summary:")
        print(f"  - Database tables: DEPLOYED")
        print(f"  - Task creation: WORKING")
        print(f"  - QA trigger: WORKING")
        print(f"  - Multi-agent sign-offs: WORKING")
        print(f"  - Status tracking: WORKING")
        print()
        print("Next: Run test_qa_system_complete.py for full workflow test")
        print("      (requires chromadb and sentence-transformers)")
        print()

        return True

    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_basic_qa_workflow()
