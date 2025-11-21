"""
Check QA Sign-Off Status for RAG Integration Tasks
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    port=os.getenv('DB_PORT', '5432'),
    database=os.getenv('DB_NAME', 'magnus'),
    user=os.getenv('DB_USER', 'postgres'),
    password=os.getenv('DB_PASSWORD', '')
)

print("=" * 80)
print("RAG INTEGRATION TASKS - QA STATUS CHECK")
print("=" * 80)
print()

with conn.cursor(cursor_factory=RealDictCursor) as cur:
    # Check tasks
    cur.execute('''
        SELECT id, title, status, task_type, priority, created_at, completed_at
        FROM development_tasks
        WHERE id IN (202, 203)
        ORDER BY id;
    ''')
    tasks = cur.fetchall()

    print("TASKS:")
    print("-" * 80)
    for task in tasks:
        print(f"Task #{task['id']}: {task['title']}")
        print(f"  Status: {task['status']}")
        print(f"  Type: {task['task_type']} | Priority: {task['priority']}")
        if task['completed_at']:
            print(f"  Completed: {task['completed_at']}")
        print()

    # Check QA sign-offs
    cur.execute('''
        SELECT
            task_id,
            agent_name,
            sign_off_status,
            review_completed_at,
            review_notes,
            issues_found,
            confidence_score,
            rag_context_used
        FROM qa_agent_sign_offs
        WHERE task_id IN (202, 203)
        ORDER BY task_id, agent_name;
    ''')
    signoffs = cur.fetchall()

    print("=" * 80)
    print("QA AGENT SIGN-OFFS:")
    print("=" * 80)

    if signoffs:
        task_summary = {}
        current_task = None

        for so in signoffs:
            tid = so['task_id']

            # Track summary
            if tid not in task_summary:
                task_summary[tid] = {'total': 0, 'approved': 0, 'pending': 0, 'rejected': 0}
            task_summary[tid]['total'] += 1
            status = so['sign_off_status']
            if status in task_summary[tid]:
                task_summary[tid][status] += 1

            # Print details
            if current_task != tid:
                if current_task:
                    print()
                print(f"\nTask #{tid}:")
                print("-" * 80)
                current_task = tid

            status_marker = "[X]" if status == "approved" else "[ ]"
            print(f"  {status_marker} {so['agent_name']}: {status.upper()}")

            if so['review_completed_at']:
                print(f"       Reviewed: {so['review_completed_at']}")

            if so['confidence_score'] is not None:
                conf = float(so['confidence_score']) * 100
                print(f"       Confidence: {conf:.0f}%")

            if so['issues_found']:
                print(f"       Issues Found: {so['issues_found']}")

            if so['rag_context_used']:
                print(f"       RAG Context: Used")

            if so['review_notes']:
                notes = so['review_notes'][:100]
                if len(so['review_notes']) > 100:
                    notes += "..."
                print(f"       Notes: {notes}")

        # Print summary
        print()
        print("=" * 80)
        print("SUMMARY:")
        print("=" * 80)
        for tid in sorted(task_summary.keys()):
            s = task_summary[tid]
            print(f"\nTask #{tid}: {s['total']} QA sign-offs")
            print(f"  [X] Approved: {s.get('approved', 0)}")
            print(f"  [ ] Pending: {s.get('pending', 0)}")
            print(f"  [!] Rejected: {s.get('rejected', 0)}")

            # Overall status
            if s.get('approved', 0) == s['total'] and s['total'] > 0:
                print(f"  STATUS: ALL AGENTS APPROVED - READY FOR FINALIZATION")
            elif s.get('pending', 0) > 0:
                print(f"  STATUS: AWAITING {s.get('pending', 0)} AGENT REVIEW(S)")
            elif s.get('rejected', 0) > 0:
                print(f"  STATUS: HAS REJECTIONS - NEEDS FIXES")
    else:
        print("\n[INFO] No QA sign-offs found for these tasks.")
        print("\nPossible reasons:")
        print("  - Task #202 is still executing (status: pending)")
        print("  - QA was not triggered when tasks were completed")
        print("\nTo trigger QA, use: TaskCompletionWithQA().complete_task(task_id)")

conn.close()

print("\n" + "=" * 80)
print("CHECK COMPLETE")
print("=" * 80)
