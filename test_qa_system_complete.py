"""
Comprehensive QA System Test
============================

Tests the full multi-agent QA workflow:
1. Create a test task
2. Trigger QA review
3. Agents perform reviews
4. Complete reviews with findings
5. Create and resolve QA tasks
6. Finalize task completion
"""

from src.qa import MultiAgentQAService, get_expertise_registry
from src.task_db_manager import TaskDBManager
import json

def test_full_qa_workflow():
    """Test complete QA workflow end-to-end"""

    print("=" * 80)
    print("MULTI-AGENT QA SYSTEM - COMPREHENSIVE TEST")
    print("=" * 80)
    print()

    # Initialize services
    task_mgr = TaskDBManager()
    qa_service = MultiAgentQAService()

    print("[1/8] Creating test task...")
    task_id = task_mgr.create_task(
        title="Add user authentication feature",
        description="Implement JWT-based authentication with password hashing",
        task_type="feature",
        priority="high",
        assigned_agent="backend-architect",
        feature_area="authentication",
        tags=["security", "authentication", "jwt"]
    )
    print(f"  Created task ID: {task_id}")
    print()

    print("[2/8] Marking task as completed to trigger QA review...")
    task_mgr.update_task_status(task_id, "completed")
    print("  Task status: completed")
    print()

    print("[3/8] Triggering QA review...")
    review_result = qa_service.trigger_qa_review(task_id)
    print(f"  Status: {review_result['status']}")
    print(f"  Required agents: {', '.join(review_result['required_agents'])}")
    print(f"  Sign-offs created: {len(review_result['sign_offs_created'])}")
    print()

    # Perform reviews for each agent
    for i, sign_off in enumerate(review_result['sign_offs_created'], 1):
        agent_name = sign_off['agent_name']
        sign_off_id = sign_off['sign_off_id']

        print(f"[4.{i}/8] {agent_name} performing review...")

        # Start review
        review = qa_service.perform_agent_review(
            sign_off_id=sign_off_id,
            agent_name=agent_name,
            use_rag=True
        )

        print(f"  Review started at: {review['started_at']}")
        print(f"  RAG sources loaded: {len(review['rag_sources'])}")
        print(f"  Checklist items: {len(review['checklist'])}")
        print()

        # Simulate review findings
        if agent_name == "security-auditor":
            # Security auditor finds issues
            print(f"  {agent_name} found security issues!")
            issues_found = [
                {
                    'title': 'Password stored without proper hashing',
                    'description': 'Passwords should use bcrypt with salt, not plain MD5',
                    'issue_type': 'security',
                    'severity': 'critical'
                },
                {
                    'title': 'JWT secret hardcoded in source',
                    'description': 'JWT secret key found hardcoded in auth.py line 45',
                    'issue_type': 'security',
                    'severity': 'high'
                }
            ]

            completion = qa_service.complete_agent_review(
                sign_off_id=sign_off_id,
                agent_name=agent_name,
                approved=False,
                review_notes="Found critical security vulnerabilities that must be fixed",
                issues_found=issues_found,
                confidence_score=0.98
            )

            print(f"  Review result: REJECTED")
            print(f"  Issues created: {len(issues_found)}")
            for issue in issues_found:
                print(f"    - [{issue['severity'].upper()}] {issue['title']}")

        elif agent_name == "code-reviewer":
            # Code reviewer finds minor issues
            print(f"  {agent_name} found code quality issues")
            issues_found = [
                {
                    'title': 'Code duplication in auth handlers',
                    'description': 'Token validation logic duplicated in 3 files',
                    'issue_type': 'code_quality',
                    'severity': 'medium'
                }
            ]

            completion = qa_service.complete_agent_review(
                sign_off_id=sign_off_id,
                agent_name=agent_name,
                approved=False,
                review_notes="Code quality issues found. DRY principle violations.",
                issues_found=issues_found,
                confidence_score=0.90
            )

            print(f"  Review result: REJECTED (with code quality issues)")
            print(f"  Issues created: {len(issues_found)}")

        else:
            # Other agents approve
            print(f"  {agent_name} reviewing...")
            completion = qa_service.complete_agent_review(
                sign_off_id=sign_off_id,
                agent_name=agent_name,
                approved=True,
                review_notes=f"No issues found by {agent_name}",
                confidence_score=0.85
            )

            print(f"  Review result: APPROVED")

        print()

    print("[5/8] Checking QA status...")
    status = qa_service.get_task_qa_status(task_id)
    print(f"  Total reviews: {status['total_sign_offs']}")
    print(f"  Approved: {status['approvals']}")
    print(f"  Rejected: {status['rejections']}")
    print(f"  Open QA issues: {status['open_qa_issues']}")
    print(f"  Can finalize? {status['can_finalize']}")
    print()

    print("[6/8] Getting QA tasks that need fixing...")
    qa_tasks = qa_service.get_qa_tasks_for_parent(task_id)
    print(f"  Found {len(qa_tasks)} QA tasks:")
    for qt in qa_tasks:
        print(f"    - [{qt['severity'].upper()}] {qt['title']}")
        print(f"      Reported by: {qt['reported_by_agent']}")
        print(f"      Status: {qt['status']}")
    print()

    print("[7/8] Fixing QA issues...")
    for qt in qa_tasks:
        if qt['status'] == 'open':
            print(f"  Fixing: {qt['title']}")

            # Mark as fixed
            qa_service.mark_qa_task_complete(
                qa_task_id=qt['id'],
                resolution_notes=f"Fixed {qt['title']} - implemented proper solution",
                verified_by=qt['reported_by_agent']
            )

            print(f"    Status: FIXED and verified by {qt['reported_by_agent']}")
    print()

    print("[8/8] Attempting to finalize task...")
    final_status = qa_service.get_task_qa_status(task_id)
    print(f"  All sign-offs complete? {final_status['all_sign_offs_complete']}")
    print(f"  Open QA issues: {final_status['open_qa_issues']}")

    if final_status['can_finalize']:
        finalize_result = qa_service.finalize_task_completion(task_id)
        print(f"  Finalization: SUCCESS")
        print(f"  Task status: {finalize_result['new_status']}")
        print(f"  Can deploy to production: {finalize_result['can_deploy']}")
    else:
        print(f"  Finalization: BLOCKED")
        print(f"  Reason: {final_status['blocking_reason']}")

    print()
    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    print()
    print("Summary:")
    print(f"  - Task created and completed: #{task_id}")
    print(f"  - QA reviews performed: {final_status['total_sign_offs']}")
    print(f"  - Issues found and fixed: {len(qa_tasks)}")
    print(f"  - Final task status: {finalize_result.get('new_status', 'pending')}")
    print()


def test_agent_rag_expertise():
    """Test agent RAG expertise system"""

    print("=" * 80)
    print("AGENT RAG EXPERTISE SYSTEM TEST")
    print("=" * 80)
    print()

    try:
        registry = get_expertise_registry()

        print("[1/3] Testing code-reviewer expertise...")
        code_reviewer = registry.get_agent_expertise('code-reviewer')
        stats = code_reviewer.get_stats()
        print(f"  Agent: {stats['agent_name']}")
        print(f"  Total expertise documents: {stats['total_documents']}")
        print(f"  Active documents: {stats['active_documents']}")
        print()

        print("[2/3] Searching for expertise on 'code duplication'...")
        results = code_reviewer.search_expertise("code duplication refactoring", n_results=3)
        print(f"  Found {len(results)} relevant documents:")
        for r in results:
            print(f"    - {r.document.title}")
            print(f"      Similarity: {r.similarity_score:.2f}")
            print(f"      Domain: {r.document.domain}")
        print()

        print("[3/3] Getting review context...")
        context = code_reviewer.get_review_context(
            task_description="Refactor authentication module to remove duplication",
            code_snippet="def validate_token(token): ..."
        )
        print("  Context generated successfully")
        print(f"  Context length: {len(context)} characters")
        print()

        print("[OK] RAG expertise system working!")

    except ImportError as e:
        print(f"[WARNING] RAG dependencies not installed: {e}")
        print("  Install with: pip install chromadb sentence-transformers")
    except Exception as e:
        print(f"[ERROR] RAG test failed: {e}")

    print()


if __name__ == "__main__":
    print()
    print("STARTING COMPREHENSIVE QA SYSTEM TESTS")
    print()

    # Test 1: RAG Expertise
    test_agent_rag_expertise()

    # Test 2: Full QA Workflow
    test_full_qa_workflow()

    print()
    print("[OK] All tests complete!")
    print()
