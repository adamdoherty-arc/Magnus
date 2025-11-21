"""
Mark Task Complete
==================

After Claude Code implements a task, run this to mark it complete in database.
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

def mark_task_complete(task_id, actual_hours=1.0, notes="Implemented by Claude Code"):
    """Mark task as completed"""
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE ci_enhancements
        SET status = 'completed',
            completed_at = NOW(),
            actual_hours = %s,
            completion_percentage = 100,
            user_comments = ARRAY[%s]
        WHERE id = %s
    """, (actual_hours, notes, task_id))

    conn.commit()
    cursor.close()
    conn.close()

    print(f"\n✅ Task {task_id} marked as COMPLETED!")
    print(f"   Actual hours: {actual_hours}")
    print(f"   Notes: {notes}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python mark_task_complete.py <task_id> [hours] [notes]")
        print("Example: python mark_task_complete.py 133 2.5 'Fixed the bug'")
        sys.exit(1)

    task_id = int(sys.argv[1])
    hours = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
    notes = sys.argv[3] if len(sys.argv) > 3 else "Implemented by Claude Code"

    mark_task_complete(task_id, hours, notes)
