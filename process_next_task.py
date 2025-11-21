"""
Process Next Task - Direct Integration with Claude Code
========================================================

Instead of making API calls, this script just identifies the next task
and Claude Code (running in VSCode) will implement it directly using
its built-in tools (Read, Write, Edit, Bash, Task).

This approach:
- ✅ Uses Claude Code's existing terminal access
- ✅ No API calls needed (FREE!)
- ✅ Database stays updated
- ✅ Full tool access (Bash, Read, Write, Edit, Task, etc.)
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

def get_next_task():
    """Get the highest priority pending task"""
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id, title, description, category, priority,
            complexity, feature_area, estimated_hours
        FROM ci_enhancements
        WHERE status IN ('proposed', 'approved')
          AND (complexity IS NULL OR complexity != 'epic')
          AND (depends_on_enhancement_ids IS NULL
               OR array_length(depends_on_enhancement_ids, 1) = 0)
        ORDER BY
            CASE priority
                WHEN 'critical' THEN 1
                WHEN 'high' THEN 2
                WHEN 'medium' THEN 3
                WHEN 'low' THEN 4
            END,
            ai_priority_score DESC NULLS LAST,
            created_at ASC
        LIMIT 1
    """)

    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if not result:
        return None

    return {
        'id': result[0],
        'title': result[1],
        'description': result[2],
        'category': result[3],
        'priority': result[4],
        'complexity': result[5],
        'feature_area': result[6],
        'estimated_hours': result[7]
    }

def mark_task_in_progress(task_id):
    """Mark task as in progress"""
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE ci_enhancements
        SET status = 'in_progress',
            started_at = NOW()
        WHERE id = %s
    """, (task_id,))

    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    task = get_next_task()

    if not task:
        print("\nNo pending tasks found!")
        print("All caught up! ✅")
        exit(0)

    print("\n" + "="*80)
    print("NEXT TASK FOR CLAUDE CODE")
    print("="*80)
    print(f"\nTask ID: {task['id']}")
    print(f"Title: {task['title']}")
    print(f"Priority: {task['priority']}")
    print(f"Category: {task['category']}")
    print(f"Feature: {task['feature_area']}")
    print(f"\nDescription:")
    print(task['description'])
    print("\n" + "="*80)

    # Mark as in progress
    mark_task_in_progress(task['id'])
    print(f"\n✅ Task {task['id']} marked as IN PROGRESS in database")
    print("\nClaude Code can now implement this task using built-in tools!")
    print("(Read, Write, Edit, Bash, Task, etc.)")
    print("\n" + "="*80)
