"""Check test-automator sign-off status details"""
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
print("TEST-AUTOMATOR SIGN-OFF DETAILS")
print("=" * 80)
print()

with conn.cursor(cursor_factory=RealDictCursor) as cur:
    cur.execute("""
        SELECT
            id,
            task_id,
            agent_name,
            sign_off_status,
            review_started_at,
            review_completed_at,
            is_final,
            review_notes,
            confidence_score,
            issues_found
        FROM qa_agent_sign_offs
        WHERE task_id = 203 AND agent_name = 'test-automator'
        ORDER BY id;
    """)
    signoffs = cur.fetchall()

    for so in signoffs:
        print(f"Sign-off ID: {so['id']}")
        print(f"  Status: {so['sign_off_status']}")
        print(f"  Is Final: {so.get('is_final', 'N/A')}")
        print(f"  Started: {so['review_started_at']}")
        print(f"  Completed: {so['review_completed_at']}")
        print(f"  Confidence: {so['confidence_score']}")
        print(f"  Issues Found: {so['issues_found']}")
        if so['review_notes']:
            notes = so['review_notes'][:150]
            print(f"  Notes: {notes}...")
        print()

conn.close()
