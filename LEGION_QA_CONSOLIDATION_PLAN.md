# Legion QA Consolidation Plan
**Date:** 2025-11-11
**Purpose:** Consolidate Magnus QA under Legion as lead architect

---

## Current Situation

### Duplicate QA Systems

**Problem:** Magnus and Legion both have separate QA systems

**Magnus QA System:**
- Location: `src/qa/`
- Tables: `development_tasks`, `qa_agent_sign_offs`, `qa_tasks`
- Agents: `code-reviewer`, `security-auditor`, `test-automator`
- Process: Tasks created → Agents review → Sign-offs → Completion

**Legion QA System:**
- Location: Legion repository
- Similar multi-agent structure
- Manages multiple projects (Magnus, others)
- Centralized oversight

**Issue:** Duplication of effort, inconsistent standards, harder for Legion to review Magnus changes

---

## Solution: Consolidate to Legion

### Why Legion as Lead Architect

1. **Legion is Project Manager**
   - Magnus is ONE project among many
   - Legion orchestrates across projects
   - Centralized control and visibility

2. **Avoid Duplication**
   - Single QA process for all projects
   - Consistent quality standards
   - Reduced maintenance overhead

3. **Better for Legion**
   - Easy to review all Magnus features
   - Update Magnus from Legion dashboard
   - Track cross-project dependencies

4. **Cleaner Architecture**
   - Magnus focuses on trading features
   - Legion handles project management
   - Clear separation of concerns

---

## Implementation Plan

### Phase 1: Bidirectional Task Sync (ALREADY EXISTS!)

**File:** `src/legion/legion_task_sync_service.py`

```python
class LegionTaskSyncService:
    """Bidirectional sync between Legion and Magnus"""

    def pull_tasks_from_legion(project_name='Magnus') -> List[Dict]:
        """Get tasks assigned to Magnus from Legion"""

    def push_task_to_legion(magnus_task_id, status, metadata) -> int:
        """Push Magnus task to Legion for QA"""

    def sync_qa_status(legion_task_id, magnus_task_id):
        """Sync QA sign-offs between systems"""
```

**Status:** ✅ Already implemented

**Usage:**
```python
# When Magnus task completes, push to Legion
sync = LegionTaskSyncService()
legion_task_id = sync.push_task_to_legion(
    magnus_task_id=123,
    status='awaiting_qa',
    metadata={'source': 'magnus', 'feature_area': 'AVA'}
)

# Legion QA agents review
# When approved, syncs back to Magnus
sync.sync_qa_status(legion_task_id, magnus_task_id=123)
```

---

### Phase 2: Auto-Sync All Magnus Tasks

**Modify:** `src/task_completion_with_qa.py`

```python
class TaskCompletionWithQA:
    def complete_task_with_qa(self, task_id: int) -> Dict:
        # Existing code...

        # NEW: Auto-push to Legion for QA
        from src.legion.legion_task_sync_service import LegionTaskSyncService

        legion_sync = LegionTaskSyncService()
        legion_task_id = legion_sync.push_task_to_legion(
            magnus_task_id=task_id,
            status='awaiting_qa',
            metadata={
                'source': 'magnus',
                'requires_qa': True,
                'agents': ['code-reviewer', 'security-auditor', 'test-automator']
            }
        )

        # Store mapping
        self.db_manager.update_task(
            task_id,
            metadata={'legion_task_id': legion_task_id}
        )

        return {
            'task_id': task_id,
            'legion_task_id': legion_task_id,
            'status': 'synced_to_legion',
            'message': 'Task pushed to Legion for QA review'
        }
```

**Benefits:**
- All Magnus tasks automatically go to Legion
- No manual sync needed
- Legion has full visibility

---

### Phase 3: Legion QA Dashboard Integration

**Create:** `legion_magnus_qa_dashboard.py` (in Legion repo)

```python
"""
Legion Dashboard - Magnus QA Review
====================================

Centralized view of all Magnus tasks awaiting QA.
Legion can review, approve, or request changes.
"""

import streamlit as st
from src.legion.legion_task_sync_service import LegionTaskSyncService

def show_magnus_qa_dashboard():
    st.title("🔍 Magnus - QA Review")

    sync = LegionTaskSyncService()

    # Get all Magnus tasks awaiting QA
    tasks = sync.get_tasks_by_project('Magnus', status='awaiting_qa')

    for task in tasks:
        with st.expander(f"Task #{task['id']}: {task['title']}"):
            st.markdown(task['description'])

            # Show code changes
            st.subheader("Code Changes")
            st.code(task['diff'], language='python')

            # QA Agent status
            st.subheader("QA Status")
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("code-reviewer", task['code_review_status'])
            with col2:
                st.metric("security-auditor", task['security_status'])
            with col3:
                st.metric("test-automator", task['test_status'])

            # Actions
            if st.button("Approve & Deploy", key=f"approve_{task['id']}"):
                sync.approve_task(task['id'])
                st.success("Task approved! Syncing to Magnus...")

            if st.button("Request Changes", key=f"reject_{task['id']}"):
                sync.request_changes(task['id'])
                st.warning("Changes requested. Syncing to Magnus...")
```

**Benefits:**
- Legion sees all Magnus tasks in one place
- Easy approval/rejection workflow
- Syncs status back to Magnus automatically

---

### Phase 4: Deprecate Magnus Local QA

**Timeline:** After Phase 1-3 tested and stable

**Steps:**

1. **Mark Magnus QA as deprecated**
   ```python
   # In src/qa/__init__.py
   import warnings
   warnings.warn(
       "Magnus local QA is deprecated. Use Legion QA system instead.",
       DeprecationWarning
   )
   ```

2. **Redirect to Legion**
   ```python
   # In task_completion_with_qa.py
   def complete_task_with_qa(self, task_id):
       # Don't use local QA, push to Legion
       return self._complete_via_legion(task_id)
   ```

3. **Keep tables for history**
   - Don't drop `qa_agent_sign_offs` table
   - Maintain historical data
   - New tasks go to Legion only

4. **Documentation update**
   - Update README to reference Legion QA
   - Add migration guide
   - Document Legion workflow

---

## Data Flow (After Consolidation)

```
┌──────────────────────────────────────────────────────────────┐
│  1. Magnus Developer Completes Task                         │
│     - Implements feature                                     │
│     - Runs local tests                                       │
│     - Calls task_completion_with_qa.complete_task(task_id)  │
└────────────────┬─────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────┐
│  2. Auto-Sync to Legion                                      │
│     - LegionTaskSyncService.push_task_to_legion()           │
│     - Task details, code diff, test results synced          │
│     - Status: 'awaiting_qa'                                  │
└────────────────┬─────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────┐
│  3. Legion QA Dashboard                                      │
│     - Shows all Magnus tasks awaiting review                 │
│     - Legion reviews changes                                 │
│     - Can view code, tests, description                      │
└────────────────┬─────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────┐
│  4. Legion Multi-Agent QA                                    │
│     - code-reviewer: Checks code quality                     │
│     - security-auditor: Reviews security                     │
│     - test-automator: Validates tests                        │
│     - All must approve                                       │
└────────────────┬─────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────┐
│  5. Approval or Rejection                                    │
│     IF ALL APPROVE:                                          │
│       - Status: 'approved'                                   │
│       - Auto-deploy if configured                            │
│     IF ANY REJECT:                                           │
│       - Status: 'needs_changes'                              │
│       - Comments sent to developer                           │
└────────────────┬─────────────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────────────┐
│  6. Sync Back to Magnus                                      │
│     - LegionTaskSyncService.sync_qa_status()                │
│     - Updates Magnus task status                             │
│     - Stores QA results                                      │
└──────────────────────────────────────────────────────────────┘
```

---

## Benefits Summary

### For Magnus

1. **Less code to maintain** - No local QA system
2. **Consistent quality** - Same standards as all Legion projects
3. **Automatic sync** - No manual intervention needed
4. **Clear ownership** - Legion manages QA, Magnus focuses on features

### For Legion

1. **Full visibility** - See all Magnus changes
2. **Easy review** - Single dashboard for all projects
3. **Control** - Approve/reject from Legion
4. **Cross-project insights** - Track patterns across all projects

### For Development

1. **Single workflow** - Same process for all projects
2. **Faster** - No duplicate reviews
3. **Better** - Legion QA more comprehensive
4. **Scalable** - Easy to add new projects

---

## Migration Timeline

### Week 1: Setup (Current)
- [x] Legion task sync service exists
- [x] Bidirectional sync working
- [ ] Test sync with sample Magnus task

### Week 2: Auto-Sync
- [ ] Modify task_completion_with_qa to auto-push
- [ ] Test end-to-end workflow
- [ ] Document for developers

### Week 3: Legion Dashboard
- [ ] Create Magnus QA view in Legion
- [ ] Test approval/rejection flow
- [ ] Train Legion operators

### Week 4: Deprecation
- [ ] Mark Magnus QA as deprecated
- [ ] Redirect all new tasks to Legion
- [ ] Monitor for issues

### Week 5+: Full Migration
- [ ] All Magnus tasks go through Legion
- [ ] Magnus QA system mothballed (kept for history)
- [ ] Documentation complete

---

## Developer Experience

### Before (Magnus Local QA)

```python
# Developer completes task
task_completion = TaskCompletionWithQA()
result = task_completion.complete_task_with_qa(task_id=123)

# Wait for Magnus QA agents (code-reviewer, security-auditor, test-automator)
# Check qa_agent_sign_offs table
# All agents approve
# Task marked complete
```

**Pain Points:**
- Separate QA for each project
- Legion can't see Magnus changes
- Inconsistent standards

### After (Legion QA)

```python
# Developer completes task (SAME API!)
task_completion = TaskCompletionWithQA()
result = task_completion.complete_task_with_qa(task_id=123)

# Behind the scenes:
#   1. Auto-pushes to Legion
#   2. Legion QA agents review
#   3. Legion approves
#   4. Auto-syncs back to Magnus
#   5. Task marked complete

# Developer sees: "Task pushed to Legion for QA. Track at: https://legion.heracles.com/qa/123"
```

**Benefits:**
- Same API for developers
- Legion visibility
- Consistent standards
- Single source of truth

---

## File Changes Required

### Files to Modify

1. **`src/task_completion_with_qa.py`**
   - Add auto-push to Legion after task completion
   - Store Legion task ID in metadata

2. **`src/legion/legion_task_sync_service.py`**
   - Add `push_task_to_legion()` method (if not exists)
   - Add `sync_qa_status()` method
   - Handle QA approval/rejection

3. **`src/qa/__init__.py`**
   - Add deprecation warning
   - Update documentation

### Files to Create (in Legion repo)

1. **`legion_magnus_qa_dashboard.py`**
   - Magnus QA review interface
   - Approval/rejection workflow

2. **`docs/MAGNUS_QA_WORKFLOW.md`**
   - How Magnus tasks flow through Legion QA
   - Developer guide
   - Legion operator guide

---

## Rollback Plan

If issues arise during migration:

1. **Immediate:** Disable auto-push to Legion
   ```python
   # In task_completion_with_qa.py
   LEGION_QA_ENABLED = False  # Set to False to use local QA
   ```

2. **Temporary:** Use both systems in parallel
   - Push to Legion for visibility
   - Use local QA for actual approval
   - Compare results

3. **Fix issues:** Address any bugs in sync service

4. **Re-enable:** When stable, turn Legion QA back on

---

## Testing Checklist

Before full migration:

- [ ] Test task sync Magnus → Legion
- [ ] Test QA approval in Legion
- [ ] Test sync back Legion → Magnus
- [ ] Test rejection flow
- [ ] Test auto-deployment (if configured)
- [ ] Test with different task types
- [ ] Test with different priorities
- [ ] Load test (100+ tasks)
- [ ] Security review
- [ ] Documentation review

---

## Success Metrics

**After 1 Month:**

- [ ] 100% of Magnus tasks go through Legion QA
- [ ] Zero duplicate QA reviews
- [ ] Legion review time < 24 hours
- [ ] Developer satisfaction >= 4/5
- [ ] Zero missed tasks (all synced)

**After 3 Months:**

- [ ] Magnus local QA fully deprecated
- [ ] All projects using Legion QA
- [ ] QA consistency across projects
- [ ] Legion satisfied with oversight

---

## Summary

**Current:** Magnus has its own QA system, separate from Legion

**Future:** All Magnus tasks flow through Legion QA as lead architect

**Benefits:**
- No duplication
- Legion visibility and control
- Consistent quality across all projects
- Easier for Legion to review and update Magnus

**Status:** Bidirectional sync exists, auto-push integration in progress

---

**Next Steps:**
1. Test existing Legion task sync with sample Magnus task
2. Modify task_completion_with_qa to auto-push
3. Create Legion dashboard for Magnus QA
4. Gradually migrate all tasks to Legion QA

**Timeline:** 4-5 weeks to full migration

**Owner:** Legion (lead architect) + Magnus (implementation)
