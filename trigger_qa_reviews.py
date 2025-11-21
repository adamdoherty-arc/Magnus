"""
Trigger QA Agent Reviews for Completed Tasks
"""
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
load_dotenv()

from src.qa.multi_agent_qa_service import MultiAgentQAService

print("=" * 80)
print("TRIGGERING QA AGENT REVIEWS FOR PENDING SIGN-OFFS")
print("=" * 80)
print()

qa_service = MultiAgentQAService()

# Get all pending sign-offs
conn = psycopg2.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    port=os.getenv('DB_PORT', '5432'),
    database=os.getenv('DB_NAME', 'magnus'),
    user=os.getenv('DB_USER', 'postgres'),
    password=os.getenv('DB_PASSWORD', '')
)

with conn.cursor(cursor_factory=RealDictCursor) as cur:
    cur.execute('''
        SELECT id, task_id, agent_name, sign_off_status
        FROM qa_agent_sign_offs
        WHERE task_id = 203 AND sign_off_status = 'pending'
        ORDER BY agent_name;
    ''')
    pending_signoffs = cur.fetchall()

conn.close()

print(f"Found {len(pending_signoffs)} pending sign-offs for Task #203")
print()

# Trigger review for each pending sign-off
for signoff in pending_signoffs:
    print(f"Triggering review for agent: {signoff['agent_name']}")
    print("-" * 80)

    try:
        # Perform agent review
        result = qa_service.perform_agent_review(
            sign_off_id=signoff['id'],
            agent_name=signoff['agent_name'],
            use_rag=True
        )

        print(f"  Status: {result.get('sign_off_status', 'unknown')}")
        print(f"  Confidence: {result.get('confidence_score', 0):.0%}")
        print(f"  Issues Found: {result.get('issues_found', 0)}")

        if result.get('review_notes'):
            notes = result['review_notes'][:100]
            if len(result.get('review_notes', '')) > 100:
                notes += "..."
            print(f"  Notes: {notes}")

        print()

    except Exception as e:
        print(f"  ERROR: {e}")
        print()

# Check final status
print("=" * 80)
print("FINAL QA STATUS FOR TASK #203")
print("=" * 80)

try:
    status = qa_service.get_task_qa_status(task_id=203)
    print(f"\nTotal Sign-Offs: {status['total_sign_offs']}")
    print(f"Approved: {status['approved_count']}")
    print(f"Pending: {status['pending_count']}")
    print(f"Rejected: {status['rejected_count']}")
    print(f"\nOverall Status: {status['overall_status']}")
    print(f"All Complete: {status['all_sign_offs_complete']}")

except Exception as e:
    print(f"Error getting final status: {e}")

print()
print("=" * 80)
print("REVIEW TRIGGER COMPLETE")
print("=" * 80)
