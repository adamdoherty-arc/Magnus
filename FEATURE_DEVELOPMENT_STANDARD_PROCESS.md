# Feature Development Standard Process with QA Integration

**Date:** November 11, 2025
**Status:** MANDATORY for ALL Features
**Applies To:** All developers, all agents (human and AI)

---

## Why This Process Exists

**Quality Assurance:** Every feature is reviewed by multiple expert agents before deployment

**Consistency:** All features follow the same reliable workflow

**Accountability:** Clear audit trail of who approved what

**Knowledge Preservation:** All features automatically indexed for future queries

**Never-Delete Principle:** Complete history maintained forever

---

## The 8-Phase Standard Process

Every feature MUST go through these phases. No exceptions.

```
Phase 1: Task Creation
         ↓
Phase 2: Implementation
         ↓
Phase 3: Task Completion (Auto QA Trigger)
         ↓
Phase 4: Multi-Agent QA Review
         ↓
Phase 5: Fix QA Issues (if any)
         ↓
Phase 6: Finalization (QA Approved)
         ↓
Phase 7: RAG Indexing
         ↓
Phase 8: Deployment
```

---

## Phase 1: Task Creation

**Create task in the database using TaskDBManager.**

### Required Fields

```python
from src.task_db_manager import TaskDBManager

task_mgr = TaskDBManager()

task_id = task_mgr.create_task(
    title="<Concise feature title>",
    description="""
    <Detailed description>

    **Scope:**
    - What will be built
    - What files will be modified/created
    - What behavior will change

    **Acceptance Criteria:**
    - [ ] Criterion 1
    - [ ] Criterion 2
    - [ ] Tests pass
    - [ ] Documentation updated

    **Dependencies:**
    - Any prerequisite tasks
    - Required packages
    """,
    task_type="feature",  # or "bug_fix", "refactor"
    priority="high",  # critical, high, medium, low
    assigned_agent="<agent-name>",  # who will implement
    feature_area="<area>",  # optional: authentication, rag_system, etc.
    estimated_duration_minutes=60,  # optional but recommended
    tags=["tag1", "tag2"]  # optional but helpful
)

print(f"Created task #{task_id}")
```

### Task Types

| Type | Description | QA Requirements |
|------|-------------|-----------------|
| `feature` | New functionality | 3 agents (code-reviewer, security-auditor, test-automator) |
| `bug_fix` | Fix existing issue | 1 agent (code-reviewer) |
| `refactor` | Code improvement | 2 agents (code-reviewer, backend-architect) |

---

## Phase 2: Implementation

**Implement the feature following coding standards.**

### Implementation Checklist

- [ ] Write clean, well-documented code
- [ ] Follow project coding standards
- [ ] Add inline documentation (docstrings, comments)
- [ ] Write/update tests
- [ ] Create/update user documentation (*.md files)
- [ ] Update relevant guides and specs
- [ ] Test locally

### Documentation Requirements

**For User-Facing Features:**
- Update or create README.md in feature directory
- Add usage examples
- Document all commands/API endpoints
- Include screenshots if UI feature

**For Internal Features:**
- Update architecture documentation
- Add docstrings to all functions/classes
- Document any new database tables/views
- Explain key design decisions

---

## Phase 3: Task Completion (Auto QA Trigger)

**⚠️ CRITICAL: Use TaskCompletionWithQA, NOT direct status update!**

### Correct Way ✅

```python
from src.task_completion_with_qa import TaskCompletionWithQA

completion_mgr = TaskCompletionWithQA()

# Complete task - QA AUTOMATICALLY triggered
result = completion_mgr.complete_task(
    task_id=202,
    completion_notes="Implemented RAG integration with all features tested"
)

print(f"Task completed: {result['success']}")
print(f"QA triggered: {result['qa_triggered']}")
print(f"Required agents: {result['required_agents']}")
print(f"Sign-offs created: {result['sign_offs_created']}")
```

**Result:**
```
Task completed: True
QA triggered: True
Required agents: ['code-reviewer', 'security-auditor', 'test-automator']
Sign-offs created: 3
```

### Incorrect Way ❌

```python
# DON'T DO THIS - Bypasses QA!
task_mgr.update_task_status(task_id, "completed")  # ❌ NO QA
```

### What Happens Automatically

When you call `complete_task_with_qa()`:

1. ✅ Task status → `completed`
2. ✅ QA review **automatically triggered**
3. ✅ Required agents determined based on task type
4. ✅ Sign-off requests created for each agent
5. ✅ Status tracked in database
6. ✅ Task appears in "Awaiting QA" tab on dashboard

**You don't need to do anything else - the system handles QA triggering!**

---

## Phase 4: Multi-Agent QA Review

**QA agents review your work autonomously.**

### Review Process

Each required agent:
1. **Reviews the code** (uses RAG expertise for context)
2. **Checks acceptance criteria** (all met?)
3. **Tests the feature** (works as expected?)
4. **Decides: Approve or Reject**

### Possible Outcomes

**Scenario 1: All Agents Approve ✅**
```
code-reviewer: APPROVED ✓
security-auditor: APPROVED ✓
test-automator: APPROVED ✓

→ Status: Ready to finalize!
```

**Scenario 2: Agent Finds Issue 🔴**
```
code-reviewer: APPROVED ✓
security-auditor: REJECTED ✗
  Issue: SQL injection vulnerability in query builder
test-automator: APPROVED ✓

→ Status: QA issues open (1)
→ Must fix before finalizing
```

### Checking QA Status

```python
# Check if QA is complete
qa_status = completion_mgr.check_qa_status(task_id=202)

print(f"All sign-offs complete: {qa_status['all_sign_offs_complete']}")
print(f"Open QA issues: {qa_status['open_qa_issues']}")
print(f"Can finalize: {qa_status['can_finalize']}")

if not qa_status['can_finalize']:
    print(f"Blocking reason: {qa_status['blocking_reason']}")
```

**Output:**
```
All sign-offs complete: False
Open QA issues: 1
Can finalize: False
Blocking reason: 1 QA issue open, 0 sign-offs pending
```

### Dashboard Monitoring

**View QA status in real-time:**

http://localhost:8505

Navigate to **"Awaiting QA"** tab:
- ✅ Green = Ready to finalize
- 🔴 Red = Has open issues
- ⏳ Orange = Reviews pending

---

## Phase 5: Fix QA Issues (if any)

**If agents find issues, they're logged in the `qa_tasks` table.**

### Finding Your QA Issues

```python
from src.qa import MultiAgentQAService

qa_service = MultiAgentQAService()

# Get QA issues for your task
qa_tasks = qa_service.get_qa_tasks_for_parent(parent_task_id=202)

for qa_task in qa_tasks:
    if qa_task['status'] in ('open', 'in_progress'):
        print(f"\n Issue: {qa_task['title']}")
        print(f"   Severity: {qa_task['severity']}")
        print(f"   Type: {qa_task['issue_type']}")
        print(f"   Reported by: {qa_task['reported_by_agent']}")
        print(f"   Description: {qa_task['description']}")
```

**Output:**
```
Issue: SQL injection vulnerability in query builder
   Severity: critical
   Type: security
   Reported by: security-auditor
   Description: The query builder in src/rag/rag_service.py:245
                constructs SQL queries using string concatenation...
```

### Fixing Issues

1. **Make the fixes** in your code
2. **Test thoroughly**
3. **Mark QA task as complete:**

```python
qa_service.mark_qa_task_complete(
    qa_task_id=456,
    resolution_notes="Replaced string concatenation with parameterized queries",
    verified_by='security-auditor'
)
```

4. **Agent verifies the fix**
5. **Try finalizing again**

---

## Phase 6: Finalization (QA Approved)

**Once all QA approvals are complete, finalize the task.**

### Checking if Ready

```python
qa_status = completion_mgr.check_qa_status(task_id=202)

if qa_status['can_finalize']:
    print("Ready to finalize!")
else:
    print(f"Not ready: {qa_status['blocking_reason']}")
```

### Finalizing

```python
# Finalize task - only succeeds if all QA complete
result = completion_mgr.finalize_task(task_id=202)

if result['success']:
    print(f"Task #{task_id} is now QA APPROVED!")
    print(f"New status: {result['new_status']}")
    print(f"Ready to deploy: {result['can_deploy']}")
else:
    print(f"Cannot finalize: {result['error']}")
    print(f"Reason: {result['blocking_reason']}")
```

**Success:**
```
Task #202 is now QA APPROVED!
New status: qa_approved
Ready to deploy: True
```

**The task moves to "QA Approved" tab on the dashboard.**

---

## Phase 7: RAG Indexing

**⭐ NEW REQUIREMENT: Index feature documentation in RAG system**

This makes your feature knowledge queryable via AVA!

### Why Index?

After QA approval, your feature documentation should be indexed so:
- AVA can answer questions about your feature
- Future developers can query implementation details
- Knowledge is preserved and accessible

### How to Index

```python
from src.rag import RAGService, DocumentIndexer

# Initialize RAG
rag = RAGService(collection_name="magnus_knowledge")
indexer = DocumentIndexer(rag_service=rag)

# Index your new/updated documentation
files_to_index = [
    "features/my_feature/README.md",
    "features/my_feature/SPEC.md",
    "src/my_feature/implementation.py",  # if has good docstrings
]

for file_path in files_to_index:
    chunks = indexer.index_file(Path(file_path))
    print(f"Indexed {file_path}: {len(chunks)} chunks")

# Verify indexing
result = rag.query("How does my feature work?")
print(f"Confidence: {result.confidence}")
print(f"Answer: {result.answer[:200]}...")
```

### What to Index

✅ **Always Index:**
- README.md files
- SPEC.md files
- Quick Start guides
- Implementation summaries
- API documentation

✅ **Consider Indexing:**
- Python files with extensive docstrings
- SQL schemas with detailed comments
- Architecture diagrams (as markdown descriptions)

❌ **Don't Index:**
- Test files
- Temporary notes
- Personal todos
- Unfinished drafts

---

## Phase 8: Deployment

**Deploy to production safely.**

### Pre-Deployment Checklist

```
[ ] Task status = qa_approved
[ ] All tests passing
[ ] Documentation indexed in RAG
[ ] Tested in staging (if available)
[ ] Deployment plan reviewed
[ ] Rollback plan ready
[ ] Monitoring configured
```

### Deployment Steps

1. **Merge to main branch:**
   ```bash
   git checkout main
   git merge feature/your-feature
   git push origin main
   ```

2. **Deploy application:**
   ```bash
   # Restart services
   # Run migrations if needed
   # Verify deployment
   ```

3. **Post-Deployment Verification:**
   - Check feature works in production
   - Monitor logs for errors
   - Test via AVA if user-facing
   - Update status if needed

---

## Complete Code Example

Here's a complete example of the entire workflow:

```python
from src.task_db_manager import TaskDBManager
from src.task_completion_with_qa import TaskCompletionWithQA
from src.qa import MultiAgentQAService
from src.rag import RAGService, DocumentIndexer
from pathlib import Path

# Phase 1: Create Task
task_mgr = TaskDBManager()
task_id = task_mgr.create_task(
    title="Add Export Feature to Dashboard",
    description="Allow users to export data as CSV",
    task_type="feature",
    priority="medium",
    assigned_agent="full-stack-developer",
    tags=["dashboard", "export", "csv"]
)
print(f"[Phase 1] Created task #{task_id}")

# Phase 2: Implement
# ... write code, tests, docs ...
print("[Phase 2] Implementation complete")

# Phase 3: Complete with QA
completion_mgr = TaskCompletionWithQA()
result = completion_mgr.complete_task(
    task_id=task_id,
    completion_notes="Implemented CSV export with all features"
)
print(f"[Phase 3] QA triggered: {result['qa_triggered']}")
print(f"           Required agents: {result['required_agents']}")

# Phase 4: Wait for QA reviews
# (agents review autonomously)

# Check status
qa_status = completion_mgr.check_qa_status(task_id)
print(f"[Phase 4] Can finalize: {qa_status['can_finalize']}")

# Phase 5: Fix issues if any
if qa_status['open_qa_issues'] > 0:
    qa_service = MultiAgentQAService()
    qa_tasks = qa_service.get_qa_tasks_for_parent(task_id)
    # ... fix issues ...
    print("[Phase 5] Fixed QA issues")

# Phase 6: Finalize
if qa_status['can_finalize']:
    final_result = completion_mgr.finalize_task(task_id)
    print(f"[Phase 6] Status: {final_result['new_status']}")

# Phase 7: Index documentation
rag = RAGService(collection_name="magnus_knowledge")
indexer = DocumentIndexer(rag_service=rag)
chunks = indexer.index_file(Path("features/export/README.md"))
print(f"[Phase 7] Indexed documentation: {len(chunks)} chunks")

# Phase 8: Deploy
print("[Phase 8] Ready for deployment!")
```

---

## Quick Reference

### Do's ✅

✅ Use `TaskCompletionWithQA` for all task completions
✅ Write comprehensive documentation
✅ Fix QA issues promptly
✅ Index documentation after QA approval
✅ Check dashboard for QA status
✅ Follow the 8-phase process

### Don'ts ❌

❌ Never use direct `update_task_status()` - bypasses QA
❌ Never skip documentation
❌ Never deploy without QA approval
❌ Never ignore QA issues
❌ Never delete tasks (they're immutable)
❌ Never skip RAG indexing

---

## Helpful Commands

### Check QA Status
```python
from src.task_completion_with_qa import TaskCompletionWithQA
completion_mgr = TaskCompletionWithQA()
qa_status = completion_mgr.check_qa_status(task_id=YOUR_TASK_ID)
print(f"Can finalize: {qa_status['can_finalize']}")
```

### View All Pending QA
```python
pending = completion_mgr.get_pending_qa_tasks(limit=50)
print(f"Tasks awaiting QA: {pending['total_pending']}")
```

### View All Approved Tasks
```python
approved = completion_mgr.get_approved_tasks(limit=50)
print(f"Ready to deploy: {approved['total_approved']}")
```

### Query RAG for Feature Info
```python
from src.rag import RAGService
rag = RAGService()
result = rag.query("How does feature X work?")
print(result.answer)
```

---

## Dashboard Access

**Task Management Dashboard:**
http://localhost:8505

**Tabs:**
- 🟡 Pending Tasks - Not yet started
- 🔵 In Progress - Currently being worked on
- ⏳ Awaiting QA - Your tasks after completion
- ✅ QA Approved - Ready to deploy
- 👥 Pending Reviews - Reviews by agent
- 🔴 Open Issues - QA issues to fix

---

## Support

**Questions?** Ask AVA:
- `/docs "standard feature process"`
- `/explain "QA workflow"`
- `/howto "complete task with QA"`

**Dashboard Issues?**
Check logs in Streamlit console

**QA System Issues?**
Check `src/qa/` module documentation

---

## Summary

### The Process in One Sentence

**Create task → Implement → Complete with QA → Fix issues → Finalize → Index docs → Deploy**

### Key Takeaway

**ALWAYS use `TaskCompletionWithQA` - it automatically handles QA review!**

This ensures quality, accountability, and knowledge preservation for every feature.

---

**Last Updated:** November 11, 2025
**Mandatory For:** ALL Features
**Questions:** Ask AVA or check dashboard

