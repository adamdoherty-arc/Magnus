# Agent Coordination Prompt Template

## Standard Prompt for Multi-Agent Task Execution with QA

Use this prompt template **every time** you need coordinated work with automatic agent selection, task tracking, and QA signoff.

---

## PROMPT TEMPLATE

```
I need help with [DESCRIBE YOUR TASK/FEATURE/FIX].

**Requirements:**
1. [List specific requirements]
2. [List any constraints or preferences]
3. [Expected outcome]

**Instructions:**
- Use the main agent to coordinate all work
- Automatically delegate to specialized agents as needed
- Track all tasks in the database
- Require QA agent signoff before marking complete
- Report back with summary when done

**Context:**
[Any relevant context about files, features, or recent changes]
```

---

## HOW IT WORKS

### 1. Main Agent Coordination
The main agent (Claude Code) acts as the **orchestrator**:
- Analyzes your request
- Determines which specialized agents are needed
- Delegates work to appropriate agents
- Manages task dependencies
- Coordinates QA verification

### 2. Automatic Agent Selection
Based on your request, the main agent automatically calls:

| Task Type | Agent Called | Purpose |
|-----------|--------------|---------|
| Code changes | `code-reviewer` | Review code quality, security, patterns |
| Bug fixing | `debugger` | Debug and fix issues |
| Frontend work | `frontend-developer` | React/UI components |
| Backend work | `backend-architect` | Server logic, APIs, database |
| Database work | `database-optimizer` | Schema, queries, performance |
| Testing | `test-automator` | Create/run tests |
| Documentation | `docs-architect` | Technical documentation |
| QA verification | `qa-agent` | Final verification and signoff |

### 3. Database Task Tracking

All tasks are stored in the PostgreSQL database:

**Table: `financial_assistant_tasks`**
```sql
CREATE TABLE financial_assistant_tasks (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT,
    status TEXT DEFAULT 'pending',  -- pending, in_progress, completed, blocked
    priority TEXT DEFAULT 'medium',  -- low, medium, high, critical
    assigned_agent TEXT,
    dependencies INTEGER[],
    acceptance_criteria TEXT[],
    qa_status TEXT DEFAULT 'not_reviewed',  -- not_reviewed, under_review, approved, rejected
    qa_agent TEXT,
    qa_notes TEXT,
    qa_timestamp TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);
```

### 4. QA Signoff Process

**Before a task is marked `completed`:**
1. Work is completed by assigned agent
2. Task status → `under_review`
3. QA agent is automatically invoked
4. QA agent performs verification:
   - Code review
   - Test execution
   - Requirements validation
   - Integration checks
5. QA agent updates:
   - `qa_status` → `approved` or `rejected`
   - `qa_agent` → Agent name
   - `qa_notes` → Detailed feedback
   - `qa_timestamp` → Time of review
6. If approved: status → `completed`
7. If rejected: status → `blocked`, create follow-up task

---

## EXAMPLE USAGE

### Example 1: Simple UI Fix
```
I need help with the AVA chatbox styling.

**Requirements:**
1. Change background to dark gray
2. Remove all borders
3. Make send button circular and position inside chatbox

**Instructions:**
- Use the main agent to coordinate all work
- Automatically delegate to specialized agents as needed
- Track all tasks in the database
- Require QA agent signoff before marking complete
- Report back with summary when done

**Context:**
- Files: dashboard.py, src/ava/omnipresent_ava_enhanced.py
- Recent work: Already moved AVA to top of page
```

**What Happens:**
1. Main agent creates tasks in database
2. Delegates to `frontend-developer` agent
3. Frontend agent makes CSS changes
4. Main agent calls `qa-agent` for review
5. QA agent verifies changes, updates database
6. Main agent reports completion with summary

### Example 2: Complex Feature
```
I need help adding a new "NCAA Football Cards" feature to the Sports Game Cards page.

**Requirements:**
1. Rename "College Football" tab to "NCAA"
2. Add 60+ NCAA team logos from ESPN CDN
3. Update logo fetching to work with both NFL and NCAA
4. Show helpful error if no games found
5. Test with real data

**Instructions:**
- Use the main agent to coordinate all work
- Automatically delegate to specialized agents as needed
- Track all tasks in the database
- Require QA agent signoff before marking complete
- Report back with summary when done

**Context:**
- File: game_cards_visual_page.py
- Already has NFL logos working
- Uses Kalshi database for game data
```

**What Happens:**
1. Main agent breaks down into 5 tasks
2. Tasks created in database with dependencies
3. Delegates to:
   - `frontend-developer` for UI changes
   - `data-engineer` for logo URLs
   - `code-reviewer` for logic review
   - `test-automator` for testing
4. Tasks executed in order respecting dependencies
5. QA agent reviews each completed task
6. Main agent provides final summary with links to code

### Example 3: Bug Fix
```
I need help fixing the Robinhood authentication error.

**Requirements:**
1. Users getting "not logged in" error after approval
2. Fix session persistence
3. Ensure MFA works correctly

**Instructions:**
- Use the main agent to coordinate all work
- Automatically delegate to specialized agents as needed
- Track all tasks in the database
- Require QA agent signoff before marking complete
- Report back with summary when done

**Context:**
- File: positions_page_improved.py
- Using robin_stocks library
- Session should persist with pickle file
```

**What Happens:**
1. Main agent creates task in database
2. Delegates to `debugger` agent
3. Debugger identifies 2 issues:
   - Wrong method calls
   - Missing `store_session=True`
4. Debugger fixes both issues
5. Main agent calls `test-automator` to verify
6. QA agent reviews the fix
7. Main agent reports completion

---

## TASK MANAGEMENT COMMANDS

### View All Tasks
```sql
SELECT
    id, title, status, priority,
    qa_status, assigned_agent
FROM financial_assistant_tasks
ORDER BY created_at DESC
LIMIT 20;
```

### View Pending Tasks
```sql
SELECT id, title, category, priority
FROM financial_assistant_tasks
WHERE status = 'pending'
ORDER BY priority DESC, created_at ASC;
```

### View Tasks Needing QA
```sql
SELECT id, title, assigned_agent
FROM financial_assistant_tasks
WHERE status = 'in_progress'
  AND qa_status = 'not_reviewed'
ORDER BY updated_at DESC;
```

### View QA Approved Tasks
```sql
SELECT
    id, title, qa_agent, qa_notes, qa_timestamp
FROM financial_assistant_tasks
WHERE qa_status = 'approved'
ORDER BY qa_timestamp DESC
LIMIT 10;
```

### Mark Task Complete (Manual Override)
```sql
UPDATE financial_assistant_tasks
SET status = 'completed',
    completed_at = CURRENT_TIMESTAMP
WHERE id = [TASK_ID];
```

---

## QA AGENT CAPABILITIES

The QA agent automatically checks:

### Code Quality
- ✅ Syntax errors
- ✅ Code style and conventions
- ✅ Best practices
- ✅ Security vulnerabilities
- ✅ Performance issues

### Functionality
- ✅ Requirements met
- ✅ Edge cases handled
- ✅ Error handling present
- ✅ No regressions introduced

### Integration
- ✅ Dependencies resolved
- ✅ Database changes applied
- ✅ APIs working
- ✅ UI rendering correctly

### Testing
- ✅ Unit tests pass
- ✅ Integration tests pass
- ✅ Manual testing performed

---

## BENEFITS

### 1. Automatic Agent Selection
No need to manually choose which agent to use - the main agent determines this based on your request.

### 2. Task Persistence
All work is tracked in the database, survives restarts, can be queried anytime.

### 3. Quality Assurance
Every task gets QA review before being marked complete, reducing bugs.

### 4. Clear Audit Trail
Database records who did what, when, and QA approval status.

### 5. Dependency Management
Tasks can depend on other tasks, ensuring correct execution order.

### 6. Prioritization
Tasks have priority levels, ensuring urgent work gets done first.

---

## ADVANCED FEATURES

### Task Dependencies
```python
# Task 2 depends on Task 1 being completed
INSERT INTO financial_assistant_tasks
(title, dependencies, status)
VALUES
('Add NCAA logos', NULL, 'pending'),  -- Task 1, no deps
('Update display function', ARRAY[1], 'pending');  -- Task 2, depends on Task 1
```

### Acceptance Criteria
```python
# Define what "done" means
UPDATE financial_assistant_tasks
SET acceptance_criteria = ARRAY[
    'All 60 NCAA logos added',
    'Logos display correctly on page',
    'Fallback shows for missing logos',
    'No console errors'
]
WHERE id = 1;
```

### QA Rejection Flow
```python
# If QA rejects:
1. qa_status → 'rejected'
2. status → 'blocked'
3. qa_notes contains reasons
4. New task created to fix issues
5. Original task references new task
```

---

## QUICK START

### 1-Minute Setup
```sql
-- Verify table exists
SELECT COUNT(*) FROM financial_assistant_tasks;

-- If table doesn't exist, run:
CREATE TABLE IF NOT EXISTS financial_assistant_tasks (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT,
    status TEXT DEFAULT 'pending',
    priority TEXT DEFAULT 'medium',
    assigned_agent TEXT,
    dependencies INTEGER[],
    acceptance_criteria TEXT[],
    qa_status TEXT DEFAULT 'not_reviewed',
    qa_agent TEXT,
    qa_notes TEXT,
    qa_timestamp TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);
```

### First Request
Use the template prompt above with your actual task. The system handles the rest automatically.

---

## PROMPT TEMPLATE (Copy-Paste)

```
I need help with [YOUR TASK HERE].

**Requirements:**
1. [Requirement 1]
2. [Requirement 2]
3. [Requirement 3]

**Instructions:**
- Use the main agent to coordinate all work
- Automatically delegate to specialized agents as needed
- Track all tasks in the database
- Require QA agent signoff before marking complete
- Report back with summary when done

**Context:**
[Any relevant files, recent changes, or background]
```

---

**That's it!** Use this prompt format every time, and the system will:
1. ✅ Coordinate all agents automatically
2. ✅ Track everything in the database
3. ✅ Ensure QA signoff
4. ✅ Provide clear summaries

**Questions?** Just ask the main agent for help with the task system.
