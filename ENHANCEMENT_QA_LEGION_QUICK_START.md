# Enhancement & QA Management + Legion Integration - Quick Start

**Date:** November 11, 2025
**Status:** PRODUCTION READY

---

## What You Now Have

### 1. Enhanced Task & QA Management Page
**File:** `enhancement_qa_management_page.py`

A comprehensive dashboard showing:
- ✅ **All tasks with prominent QA sign-off information**
- 🎯 **Visual agent approval badges** (✅ Approved, ❌ Rejected, ⏳ Pending)
- 📊 **Progress bars** for QA approval status
- 🔴 **Open QA issues** prominently displayed
- 🔍 **Advanced filtering** by status, priority, QA status
- 📋 **Legion task tracking** (shows which tasks came from Legion)

### 2. Legion Bidirectional Sync Service
**File:** `src/legion/legion_task_sync_service.py`

Enables:
- ⬇️ **Pull tasks from Legion** → Create in Magnus automatically
- ⬆️ **Push status updates** → Keep Legion informed of progress
- ✅ **QA sign-off sync** → Legion sees QA approval status
- 🔄 **Real-time bidirectional sync**
- 🗺️ **Task ID mapping** (Legion ↔ Magnus)

---

## How to Use: Enhancement & QA Management Page

### Starting the Page

```bash
streamlit run enhancement_qa_management_page.py --server.port 8506
```

**Access at:** http://localhost:8506

### What You'll See

#### Top Metrics Dashboard
```
┌────────────┬──────────────┬──────────────┬─────────────┬──────────────┬─────────────┐
│ Total Tasks│ QA Approved  │ Awaiting QA  │ In Progress │ Pending      │ Open QA     │
│            │              │              │             │ Sign-Offs    │ Issues      │
└────────────┴──────────────┴──────────────┴─────────────┴──────────────┴─────────────┘
```

#### Filters
- **Status:** pending, in_progress, completed, qa_approved, blocked
- **Priority:** critical, high, medium, low
- **QA Status:** All, Approved, Awaiting Review, Has Issues, Ready to Finalize
- **Legion Tasks Only:** Toggle to show only tasks from Legion

#### Task Cards

Each task card shows:

```
Task #202                    Initialize ChromaDB              ✅ QA APPROVED
────────────────────────────────────────────────────────────────────────────
Priority: 🔴 CRITICAL    Type: feature    Agent: ai-engineer    Area: rag_system

🔍 QA Sign-Offs
████████████░░░░░░░░ 2/3 Approved

✅ code-reviewer (Approved)          ✅ security-auditor (Approved)
   Reviewed: 2025-11-11 15:30           Reviewed: 2025-11-11 15:45

⏳ test-automator (Pending)
   Waiting for review

📋 Task Details
   Created: 2025-11-11
   Estimated Duration: 45 min
   Tags: rag, chromadb, indexing
   Legion ID: a1b2c3d4-5678-90ab-cdef-1234567890ab
```

### Interpreting QA Status

| Status Badge | Meaning |
|--------------|---------|
| ✅ **QA APPROVED** | All agents approved, ready to deploy |
| 🎯 **READY TO FINALIZE** | All approvals complete, can call finalize |
| 🔴 **ISSUES FOUND** | QA found problems, must fix before continuing |
| ⏳ **AWAITING QA** | Completed, waiting for agent reviews |
| 🔵 **IN PROGRESS** | Currently being worked on |
| ⚪ **PENDING** | Not yet started |

---

## How to Use: Legion Integration

### Prerequisites

1. **Legion Database Connection**

Create/update `.env` file:
```env
# Legion Database (if remote)
LEGION_DB_HOST=your-legion-host.com
LEGION_DB_PORT=5432
LEGION_DB_NAME=legion
LEGION_DB_USER=legion_user
LEGION_DB_PASSWORD=your_password

# Magnus Database (local)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=magnus
DB_USER=postgres
DB_PASSWORD=your_local_password
```

2. **Legion Database Schema**

Legion must have a `legion_tasks` table:
```sql
CREATE TABLE legion_tasks (
    id UUID PRIMARY KEY,
    project_name VARCHAR(100),  -- "Magnus"
    title TEXT NOT NULL,
    description TEXT,
    task_type VARCHAR(50),
    priority VARCHAR(20),
    status VARCHAR(50),
    assigned_agent VARCHAR(100),
    feature_area VARCHAR(100),
    estimated_duration_minutes INTEGER,
    dependencies JSONB,
    metadata JSONB,
    synced_to_project BOOLEAN DEFAULT FALSE,
    synced_task_id INTEGER,
    synced_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Running the Sync

#### One-Time Manual Sync
```bash
python src/legion/legion_task_sync_service.py
```

This will:
1. ⬇️ Pull new tasks from Legion for "Magnus" project
2. ➕ Create corresponding tasks in Magnus
3. 🗺️ Store ID mappings in `legion_magnus_sync_map.json`
4. ✅ Mark tasks as synced in Legion
5. ⬆️ Push status updates for tracked tasks back to Legion

#### Automated Continuous Sync

**Option 1: Cron Job (Linux/Mac)**
```bash
# Edit crontab
crontab -e

# Add line to run every 5 minutes
*/5 * * * * cd /path/to/WheelStrategy && /path/to/venv/bin/python src/legion/legion_task_sync_service.py >> legion_sync.log 2>&1
```

**Option 2: Windows Task Scheduler**
```powershell
# Create scheduled task
$action = New-ScheduledTaskAction -Execute "C:\Code\WheelStrategy\venv\Scripts\python.exe" -Argument "src\legion\legion_task_sync_service.py"
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 5)
Register-ScheduledTask -TaskName "LegionMagnusSync" -Action $action -Trigger $trigger
```

**Option 3: Background Service**
```python
# create_legion_sync_daemon.py
from legion.legion_task_sync_service import LegionTaskSyncService
import time

service = LegionTaskSyncService()

while True:
    try:
        service.sync_all()
        print(f"Sync complete at {datetime.now()}")
    except Exception as e:
        print(f"Sync error: {e}")

    # Wait 5 minutes
    time.sleep(300)
```

---

## Workflow: Creating Tasks from Legion

### In Legion System

1. **Create a task** in Legion with:
   - `project_name = "Magnus"`
   - All required fields (title, description, etc.)
   - `synced_to_project = false`

2. **Sync runs** (automatically or manually)

3. **Task appears in Magnus:**
   - New task created in `development_tasks`
   - Metadata includes `legion_task_id`
   - Tagged with `legion-sync`
   - Visible in Enhancement & QA Management Page

### In Magnus

4. **Work on the task:**
   - Update status to `in_progress`
   - Complete the work
   - Call `completion_mgr.complete_task(task_id)` → **QA auto-triggers!**

5. **QA Review:**
   - Agents review and approve/reject
   - Visible in Enhancement & QA Management Page
   - Status updates automatically

6. **Finalize:**
   - When all QA complete: `completion_mgr.finalize_task(task_id)`
   - Status becomes `qa_approved`

### Back in Legion

7. **Legion sees updates:**
   - Status synced: `qa_approved`
   - Progress: 100%
   - Metadata includes QA sign-off count
   - `updated_at` timestamp updated

---

## Programmatic Usage

### Pull Tasks from Legion

```python
from src.legion.legion_task_sync_service import LegionTaskSyncService

service = LegionTaskSyncService()

# Pull new tasks
new_tasks = service.pull_tasks_from_legion(project_name="Magnus")
print(f"Found {len(new_tasks)} new tasks from Legion")

# Create them in Magnus
for legion_task in new_tasks:
    magnus_id = service.create_magnus_task_from_legion(legion_task)
    if magnus_id:
        print(f"Created Magnus task #{magnus_id}")
        service.mark_legion_task_synced(
            str(legion_task['legion_task_id']),
            magnus_id
        )
```

### Push Status to Legion

```python
# After updating a Magnus task
magnus_task_id = 202

# Push update to Legion
service.push_status_to_legion(magnus_task_id)
```

### Full Bidirectional Sync

```python
# Do everything in one call
service.sync_all()

# Check status
status = service.get_sync_status()
print(f"Tracking {status['total_tracked_tasks']} tasks")
```

---

## Integration with Existing Task Management

### Existing Dashboard (Port 8505)
**File:** `task_management_dashboard.py`
**URL:** http://localhost:8505

Shows:
- 6 tabs: Pending, In Progress, Awaiting QA, QA Approved, Pending Reviews, Open Issues
- Quick task overview
- Basic QA status

### New Enhancement Page (Port 8506)
**File:** `enhancement_qa_management_page.py`
**URL:** http://localhost:8506

Shows:
- **Enhanced QA details** with agent-specific sign-offs
- **Visual progress bars** and badges
- **Legion integration status**
- **Advanced filtering**
- **Open QA issues** prominently displayed

**Use Together:**
- Port 8505: Quick task management and updates
- Port 8506: Detailed QA review and Legion tracking

---

## Example: Complete Workflow

### 1. Legion creates a task

```sql
-- In Legion database
INSERT INTO legion_tasks (
    id, project_name, title, description,
    task_type, priority, status
) VALUES (
    gen_random_uuid(),
    'Magnus',
    'Add Dark Mode to Dashboard',
    'Implement dark mode toggle for all dashboard pages',
    'feature',
    'medium',
    'pending'
);
```

### 2. Run sync

```bash
python src/legion/legion_task_sync_service.py
```

**Output:**
```
INFO - Pulled 1 new tasks from Legion for Magnus
INFO - Created Magnus task #210 from Legion task a1b2c3...
INFO - Marked Legion task a1b2c3... as synced
INFO - Sync complete: 1 new tasks pulled
```

### 3. View in Enhancement Page

Access http://localhost:8506

See new task:
```
Task #210               Add Dark Mode to Dashboard         ⚪ PENDING
────────────────────────────────────────────────────────────────────────
Priority: 🟡 MEDIUM    Type: feature    Area: ui-enhancement
Legion ID: a1b2c3d4-5678-90ab-cdef-1234567890ab
```

### 4. Work on the task

```python
from src.task_db_manager import TaskDBManager

task_mgr = TaskDBManager()
task_mgr.update_task_status(210, 'in_progress')
```

### 5. Complete with QA

```python
from src.task_completion_with_qa import TaskCompletionWithQA

completion_mgr = TaskCompletionWithQA()
result = completion_mgr.complete_task(
    task_id=210,
    completion_notes="Implemented dark mode for all pages with toggle"
)

print(f"QA triggered: {result['qa_triggered']}")
print(f"Required agents: {result['required_agents']}")
# Output: QA triggered: True
#         Required agents: ['code-reviewer', 'security-auditor', 'test-automator']
```

### 6. View QA status

http://localhost:8506 now shows:
```
Task #210               Add Dark Mode to Dashboard      ⏳ AWAITING QA
────────────────────────────────────────────────────────────────────────
🔍 QA Sign-Offs
████░░░░░░░░░░░░ 0/3 Approved

⏳ code-reviewer (Pending)
⏳ security-auditor (Pending)
⏳ test-automator (Pending)
```

### 7. Agents approve

```python
from src.qa import MultiAgentQAService

qa_service = MultiAgentQAService()

# code-reviewer approves
qa_service.approve_sign_off(
    task_id=210,
    agent_name='code-reviewer',
    notes="Clean implementation, follows conventions"
)

# security-auditor approves
qa_service.approve_sign_off(
    task_id=210,
    agent_name='security-auditor',
    notes="No security concerns found"
)

# test-automator approves
qa_service.approve_sign_off(
    task_id=210,
    agent_name='test-automator',
    notes="All tests passing"
)
```

### 8. Finalize

```python
result = completion_mgr.finalize_task(task_id=210)
print(f"Status: {result['new_status']}")  # qa_approved
```

### 9. Legion receives update

Next sync run pushes status:
```
Legion task a1b2c3...
- status: qa_approved
- progress_percentage: 100
- metadata.magnus_sync.qa_sign_offs: "3/3"
- updated_at: 2025-11-11 16:00:00
```

---

## Troubleshooting

### Issue: Tasks not syncing from Legion

**Check:**
1. Legion database connection in `.env`
2. `synced_to_project` is `false` in Legion
3. `project_name` is exactly "Magnus"
4. Task status is not 'completed' or 'cancelled'

**Debug:**
```python
service = LegionTaskSyncService()
tasks = service.pull_tasks_from_legion()
print(f"Found {len(tasks)} tasks")
for task in tasks:
    print(f"- {task['title']}")
```

### Issue: Status not pushing to Legion

**Check:**
1. Task exists in sync map: `cat legion_magnus_sync_map.json`
2. Legion database writable
3. Magnus task ID in sync map

**Debug:**
```python
service = LegionTaskSyncService()
status = service.get_sync_status()
print(json.dumps(status, indent=2))
```

### Issue: QA not showing in Enhancement Page

**Check:**
1. Task completed via `TaskCompletionWithQA.complete_task()`
2. QA sign-offs exist in `qa_agent_sign_offs` table
3. Database connection working

**Query:**
```sql
SELECT * FROM qa_agent_sign_offs WHERE task_id = 210;
```

---

## Summary

You now have:

✅ **Enhanced Task & QA Management Page**
- Visual QA approval tracking
- Agent-specific sign-offs
- Progress bars and badges
- Advanced filtering

✅ **Legion Bidirectional Sync**
- Pull tasks from Legion automatically
- Push status updates back
- Track QA approvals in both systems
- Maintain sync mapping

✅ **Integrated Workflow**
- Create tasks in Legion
- Work on them in Magnus
- QA approval tracked visually
- Legion stays informed

**Next Steps:**
1. Run the Enhancement & QA Management Page: `streamlit run enhancement_qa_management_page.py --server.port 8506`
2. Configure Legion database connection (if needed)
3. Run first sync: `python src/legion/legion_task_sync_service.py`
4. Set up automated sync (cron/task scheduler)
5. View tasks at http://localhost:8506

---

**Questions?** Check the existing task management dashboard at http://localhost:8505 for comparison.
