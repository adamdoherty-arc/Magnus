# Multi-Agent QA System - Quick Start Guide

**Get started in 5 minutes** with the comprehensive QA review system.

---

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements_qa_system.txt
```

Or install individually:
```bash
pip install psycopg2-binary python-dotenv
pip install chromadb sentence-transformers
```

### 2. Deploy Database Schema

```bash
psql -U postgres -d magnus -f src/qa_multi_agent_schema.sql
```

Verify tables created:
```bash
psql -U postgres -d magnus -c "SELECT table_name FROM information_schema.tables WHERE table_name LIKE 'qa_%';"
```

You should see:
- qa_agent_registry
- qa_sign_off_requirements
- qa_agent_sign_offs
- qa_tasks
- qa_agent_expertise
- qa_review_checklist
- qa_review_history

### 3. Seed Default Expertise (Optional)

```bash
python -m src.qa.agent_rag_expertise
```

This seeds default best practices for each agent.

---

## Basic Usage

### Complete Workflow Example

```python
from src.qa import MultiAgentQAService

qa_service = MultiAgentQAService()

# 1. Task completed → Trigger QA review
task_id = 63  # Your completed task
result = qa_service.trigger_qa_review(task_id)

print(f"Created {len(result['required_agents'])} sign-off requests")
# Output: Created 3 sign-off requests (code-reviewer, security-auditor, test-automator)

# 2. Each agent performs review
for sign_off in result['sign_offs_created']:
    review = qa_service.perform_agent_review(
        sign_off_id=sign_off['sign_off_id'],
        agent_name=sign_off['agent_name'],
        use_rag=True  # Use agent's expertise
    )

    print(f"{sign_off['agent_name']} reviewing task...")
    print(f"  RAG sources: {len(review['rag_sources'])}")
    print(f"  Checklist items: {len(review['checklist'])}")

    # Agent reviews code...

    # 3. Complete review
    qa_service.complete_agent_review(
        sign_off_id=sign_off['sign_off_id'],
        agent_name=sign_off['agent_name'],
        approved=True,  # or False if issues found
        review_notes="Code quality good, follows standards",
        confidence_score=0.95
    )

# 4. All reviews complete? Finalize task
if qa_service.check_all_sign_offs_complete(task_id):
    final = qa_service.finalize_task_completion(task_id)
    print(f"Task {task_id} is now QA approved!")
```

### If Issues Found

```python
# Agent finds issues during review
qa_service.complete_agent_review(
    sign_off_id=123,
    agent_name='security-auditor',
    approved=False,
    review_notes="Found security vulnerabilities",
    issues_found=[
        {
            'title': 'SQL Injection vulnerability',
            'description': 'User input concatenated into SQL query at line 45',
            'issue_type': 'security',
            'severity': 'critical'
        },
        {
            'title': 'Missing input validation',
            'description': 'Email field not validated',
            'issue_type': 'security',
            'severity': 'high'
        }
    ],
    confidence_score=0.98
)

# This creates 2 QA tasks that must be fixed
# Task CANNOT be finalized until all QA tasks resolved

# Later, after fixes:
qa_service.mark_qa_task_complete(
    qa_task_id=456,
    resolution_notes="Added parameterized queries and input validation",
    verified_by='security-auditor'
)

# Once all QA tasks verified, finalize
qa_service.finalize_task_completion(task_id)
```

---

## Agent Expertise

### Adding Expertise to Agent

```python
from src.qa import get_expertise_registry, ExpertiseDocument

registry = get_expertise_registry()
security = registry.get_agent_expertise('security-auditor')

# Add new expertise
security.add_expertise(ExpertiseDocument(
    title="XSS Prevention",
    content="""
    Prevent XSS by sanitizing user input:
    - Escape HTML special characters
    - Use Content Security Policy headers
    - Never use innerHTML with user data
    - Use textContent or createElement instead
    """,
    doc_type="best_practice",
    domain="security",
    tags=["xss", "input-validation", "owasp"]
))
```

### Searching Expertise

```python
# Search for relevant expertise
results = security.search_expertise("user input html output")

for result in results:
    print(f"Title: {result.document.title}")
    print(f"Similarity: {result.similarity_score:.2f}")
    print(f"Content: {result.document.content[:100]}...")
    print()
```

### Get Review Context

```python
# Get formatted context for review
context = security.get_review_context(
    task_description="Add comment feature that displays user-submitted HTML",
    code_snippet="comment_div.innerHTML = user_comment;"
)

print(context)
# Returns formatted context with relevant security expertise
```

---

## Database Queries

### Check Task QA Status

```sql
-- View QA status for a task
SELECT * FROM v_task_qa_status WHERE task_id = 63;

-- Shows:
-- - Total reviews (e.g., 3)
-- - Approvals (e.g., 2)
-- - Rejections (e.g., 1)
-- - Pending (e.g., 0)
-- - All sign-offs complete? (true/false)
-- - Open QA issues (e.g., 2)
```

### Pending Reviews

```sql
-- Get all pending reviews
SELECT * FROM v_pending_qa_reviews
ORDER BY hours_waiting DESC;

-- Get pending reviews for specific agent
SELECT * FROM v_pending_qa_reviews
WHERE agent_name = 'code-reviewer'
ORDER BY hours_waiting DESC;
```

### Open QA Issues

```sql
-- All open QA issues
SELECT * FROM v_open_qa_tasks
ORDER BY severity, days_open DESC;

-- Critical issues only
SELECT * FROM v_open_qa_tasks
WHERE severity = 'critical';
```

### Agent Performance

```sql
-- Agent performance metrics
SELECT * FROM v_qa_agent_performance
ORDER BY total_reviews DESC;

-- Specific agent
SELECT * FROM v_qa_agent_performance
WHERE agent_name = 'security-auditor';
```

---

## Python API Reference

### MultiAgentQAService

```python
from src.qa import MultiAgentQAService

qa_service = MultiAgentQAService()

# Trigger QA review
qa_service.trigger_qa_review(task_id)

# Perform review
qa_service.perform_agent_review(sign_off_id, agent_name, use_rag=True)

# Complete review
qa_service.complete_agent_review(
    sign_off_id, agent_name, approved, review_notes,
    issues_found=None, confidence_score=1.0
)

# Check if all complete
qa_service.check_all_sign_offs_complete(task_id)

# Get pending reviews for agent
qa_service.get_pending_reviews(agent_name, limit=10)

# Get QA tasks for a parent task
qa_service.get_qa_tasks_for_parent(parent_task_id)

# Mark QA task complete
qa_service.mark_qa_task_complete(qa_task_id, resolution_notes, verified_by)

# Finalize task
qa_service.finalize_task_completion(task_id)
```

### AgentRAGExpertise

```python
from src.qa import get_expertise_registry, ExpertiseDocument

registry = get_expertise_registry()
agent = registry.get_agent_expertise('code-reviewer')

# Add expertise
agent.add_expertise(ExpertiseDocument(...))

# Search expertise
results = agent.search_expertise(query, n_results=5)

# Get review context
context = agent.get_review_context(task_description, code_snippet)

# Get checklist
checklist = agent.get_checklist_for_review(task_type, feature_area)

# Update from review learnings
agent.update_expertise_from_review(task_id, sign_off_id, learnings)

# Get stats
stats = agent.get_stats()
```

---

## Configuration

### Sign-Off Requirements

Customize which agents review which tasks:

```sql
-- Example: Security-critical features need 3 agents, unanimous
INSERT INTO qa_sign_off_requirements (
    task_type,
    feature_area,
    required_agents,
    minimum_required_sign_offs,
    requires_unanimous
) VALUES (
    'feature',
    'authentication',
    ARRAY['code-reviewer', 'security-auditor', 'backend-architect'],
    3,
    true  -- All 3 must approve
);

-- Example: Simple bug fixes need 1 agent
INSERT INTO qa_sign_off_requirements (
    task_type,
    required_agents,
    minimum_required_sign_offs
) VALUES (
    'bug_fix',
    ARRAY['code-reviewer'],
    1
);
```

### Review Checklists

Create custom checklists per agent/task type:

```sql
INSERT INTO qa_review_checklist (
    agent_name,
    task_type,
    checklist_items
) VALUES (
    'security-auditor',
    'feature',
    '[
        {"item": "No SQL injection", "category": "security", "critical": true},
        {"item": "Input validation", "category": "security", "critical": true},
        {"item": "Authentication checks", "category": "security", "critical": true},
        {"item": "No hardcoded secrets", "category": "security", "critical": true},
        {"item": "HTTPS enforced", "category": "security", "critical": false}
    ]'::jsonb
);
```

---

## Common Patterns

### Pattern 1: Automated QA Trigger

```python
# In your task completion code
from src.qa import MultiAgentQAService

def complete_task(task_id):
    # Mark task complete
    update_task_status(task_id, 'completed')

    # Automatically trigger QA
    qa_service = MultiAgentQAService()
    qa_result = qa_service.trigger_qa_review(task_id)

    if qa_result['status'] == 'qa_review_triggered':
        print(f"QA review started with {len(qa_result['required_agents'])} agents")
    elif qa_result['status'] == 'no_qa_required':
        # No QA needed, mark as approved
        finalize_task(task_id)
```

### Pattern 2: Agent Review Loop

```python
def agent_review_loop(agent_name):
    """Process all pending reviews for an agent"""
    qa_service = MultiAgentQAService()

    while True:
        # Get next pending review
        pending = qa_service.get_pending_reviews(agent_name, limit=1)

        if not pending:
            break

        review = pending[0]

        # Perform review with RAG
        result = qa_service.perform_agent_review(
            sign_off_id=review['sign_off_id'],
            agent_name=agent_name,
            use_rag=True
        )

        # Analyze code using RAG context
        # ... your review logic here ...

        # Complete review
        qa_service.complete_agent_review(
            sign_off_id=review['sign_off_id'],
            agent_name=agent_name,
            approved=approved,
            review_notes=notes,
            issues_found=issues
        )
```

### Pattern 3: QA Issue Resolution Workflow

```python
def resolve_qa_issues(task_id):
    """Fix all QA issues for a task"""
    qa_service = MultiAgentQAService()

    # Get all open QA issues
    qa_tasks = qa_service.get_qa_tasks_for_parent(task_id)
    open_tasks = [t for t in qa_tasks if t['status'] in ('open', 'in_progress')]

    for qa_task in open_tasks:
        print(f"QA Issue: {qa_task['title']}")
        print(f"  Severity: {qa_task['severity']}")
        print(f"  Type: {qa_task['issue_type']}")
        print(f"  Reported by: {qa_task['reported_by_agent']}")

        # Fix the issue
        # ... your fix code here ...

        # Mark as fixed
        qa_service.mark_qa_task_complete(
            qa_task_id=qa_task['id'],
            resolution_notes="Fixed: ...",
            verified_by=qa_task['reported_by_agent']
        )

    # Check if task can be finalized
    if qa_service.check_all_sign_offs_complete(task_id):
        qa_service.finalize_task_completion(task_id)
```

---

## Troubleshooting

### Issue: No tables created

**Check:**
```bash
psql -U postgres -d magnus -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_name LIKE 'qa_%';"
```

Should return 7. If not, redeploy schema:
```bash
psql -U postgres -d magnus -f src/qa_multi_agent_schema.sql
```

### Issue: Import errors

**Error:** `ModuleNotFoundError: No module named 'src.qa'`

**Fix:** Ensure you're in the project root and `src/qa/__init__.py` exists:
```bash
cd /path/to/WheelStrategy
ls src/qa/__init__.py  # Should exist
python -c "from src.qa import MultiAgentQAService"  # Should work
```

### Issue: RAG not working

**Error:** `sentence-transformers required`

**Fix:**
```bash
pip install sentence-transformers chromadb
```

For CPU-only (lighter):
```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install sentence-transformers chromadb
```

### Issue: Can't finalize task

**Check QA status:**
```sql
SELECT * FROM v_task_qa_status WHERE task_id = YOUR_TASK_ID;
```

Look for:
- `pending` > 0 → Some agents haven't reviewed yet
- `open_qa_issues` > 0 → QA issues need to be fixed

**Fix pending reviews:**
```python
qa_service.perform_agent_review(...)
qa_service.complete_agent_review(...)
```

**Fix open issues:**
```python
qa_service.mark_qa_task_complete(...)
```

---

## Next Steps

### For Development
1. Add project-specific expertise to agents
2. Customize sign-off requirements
3. Create custom checklists
4. Integrate with CI/CD

### For Production
1. Set up automated QA triggers
2. Create QA metrics dashboard
3. Train team on QA workflow
4. Document project-specific QA procedures

### For Legion Integration
1. Connect Legion agents to QA system
2. Enable autonomous reviews
3. Set up automated issue fixing
4. Monitor QA agent performance

---

## Resources

- **Full Documentation:** `MULTI_AGENT_QA_SYSTEM_COMPLETE.md`
- **Database Schema:** `src/qa_multi_agent_schema.sql`
- **Python Services:** `src/qa/`
- **Requirements:** `requirements_qa_system.txt`

---

**Questions?** Check the full documentation or database views for detailed information.

**Status:** Production Ready ✅
**Get Started:** Install dependencies and deploy schema (5 minutes)
