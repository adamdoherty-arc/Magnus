"""
Create the 3 missing Financial Assistant tasks with corrected task types.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

def create_missing_tasks():
    """Create the 3 tasks that failed due to invalid task_type."""

    # Connect to database
    conn = psycopg2.connect(
        dbname=os.getenv('DB_NAME', 'trading'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres'),
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432')
    )

    cursor = conn.cursor(cursor_factory=RealDictCursor)

    tasks = [
        {
            "title": "Conduct security audit and fixes",
            "description": """
Perform security audit and address findings.

Requirements:
- Audit API key storage
- Check for SQL injection vectors
- Verify authentication/authorization
- Test input validation
- Check for XSS vulnerabilities
- Implement security headers
- Fix all critical/high findings

Acceptance Criteria:
- No critical vulnerabilities
- All API keys encrypted
- Input validation robust
- Security best practices followed

Documentation: FINANCIAL_ASSISTANT_MASTER_PLAN.md (Security section)
Spec: features/financial_assistant/SPEC.md (NFR-3.4)
""",
            "task_type": "qa",
            "priority": "critical",
            "assigned_agent": "security-auditor",
            "feature_area": "financial_assistant",
            "estimated_duration_minutes": 240,
            "tags": ["phase-4", "security", "audit"]
        },
        {
            "title": "Prepare for production deployment",
            "description": """
Finalize production deployment preparation.

Requirements:
- Create deployment checklist
- Set up production environment
- Configure monitoring/alerting
- Prepare rollback plan
- Create runbook for operations
- Conduct deployment dry-run

Acceptance Criteria:
- All deployment steps documented
- Production environment ready
- Rollback plan tested
- Team trained on runbook

Documentation: FINANCIAL_ASSISTANT_MASTER_PLAN.md (Deployment section)
Spec: features/financial_assistant/SPEC.md (Section 10)
""",
            "task_type": "feature",
            "priority": "high",
            "assigned_agent": "deployment-engineer",
            "feature_area": "financial_assistant",
            "estimated_duration_minutes": 240,
            "tags": ["phase-4", "deployment", "production"]
        },
        {
            "title": "Launch MFA v1.0 to production",
            "description": """
Execute production launch of Financial Assistant.

Requirements:
- Deploy to production
- Monitor for 24 hours
- Verify all features working
- Monitor error rates
- Track user adoption
- Be ready for rollback
- Announce launch to users

Acceptance Criteria:
- Deployment successful
- No critical errors in first 24h
- Users can access MFA
- Monitoring shows healthy metrics

Documentation: FINANCIAL_ASSISTANT_MASTER_PLAN.md (Deployment section)
Spec: features/financial_assistant/SPEC.md (Section 10.1)
""",
            "task_type": "feature",
            "priority": "critical",
            "assigned_agent": "deployment-engineer",
            "feature_area": "financial_assistant",
            "estimated_duration_minutes": 180,
            "tags": ["phase-4", "deployment", "launch"]
        }
    ]

    created_count = 0

    for task_data in tasks:
        try:
            cursor.execute("""
                INSERT INTO development_tasks (
                    title, description, task_type, priority, status,
                    assigned_agent, feature_area, estimated_duration_minutes,
                    tags
                )
                VALUES (
                    %(title)s, %(description)s, %(task_type)s, %(priority)s, 'pending',
                    %(assigned_agent)s, %(feature_area)s, %(estimated_duration_minutes)s,
                    %(tags)s
                )
                RETURNING id, title
            """, task_data)

            result = cursor.fetchone()
            print(f"[OK] Created task {result['id']}: {result['title']}")
            created_count += 1

        except Exception as e:
            print(f"[ERROR] Error creating task '{task_data['title']}': {e}")
            conn.rollback()
            continue

    conn.commit()
    cursor.close()
    conn.close()

    print(f"\n[SUCCESS] Created {created_count} missing tasks!")
    print(f"Total Financial Assistant tasks: 37 + {created_count} = {37 + created_count}")

if __name__ == "__main__":
    print("="*80)
    print("CREATING 3 MISSING FINANCIAL ASSISTANT TASKS")
    print("="*80)
    print()

    create_missing_tasks()
