# Enhancement Manager - Setup & Usage Guide

## Overview

The **Enhancement Manager** is a comprehensive task management system for the WheelStrategy project. It provides:

- Full CRUD operations for development tasks
- Task execution tracking and logging
- Integration with autonomous agent system
- Task verification and user feedback loops
- Analytics and progress monitoring
- File change tracking per task

## Architecture

### Components

1. **enhancement_manager_page.py** - Streamlit UI for task management
2. **src/task_manager.py** - Database interface layer
3. **src/task_management_schema.sql** - PostgreSQL database schema

### Database Tables

- `development_tasks` - Core task tracking with workflow states
- `task_execution_log` - Detailed audit log of all task activities
- `task_verification` - Task verification results and user feedback
- `task_files` - File change tracking per task

## Installation

### 1. Deploy Database Schema

First, ensure PostgreSQL is running and the `magnus` database exists:

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database if needed
CREATE DATABASE magnus;

# Exit psql
\q
```

Deploy the task management schema:

```bash
# From project root
psql -U postgres -d magnus -f src/task_management_schema.sql
```

Verify schema deployment:

```sql
SELECT
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) AS column_count
FROM information_schema.tables t
WHERE table_schema = 'public'
AND table_name IN ('development_tasks', 'task_execution_log', 'task_verification', 'task_files')
ORDER BY table_name;
```

Expected output: 4 tables with their column counts.

### 2. Environment Configuration

Ensure your `.env` file contains database credentials:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=magnus
DB_USER=postgres
DB_PASSWORD=your_password_here
```

### 3. Test Database Connection

```python
from src.task_manager import TaskManager

manager = TaskManager()
if manager.connect():
    print("✅ Database connection successful")
    print(f"Tables found: {manager.get_table_count()}")
    manager.disconnect()
else:
    print("❌ Database connection failed")
```

## Usage

### Access the Enhancement Manager

1. Run the dashboard:
   ```bash
   streamlit run dashboard.py
   ```

2. Navigate to **🚀 Enhancement Manager** in the sidebar

### Creating Tasks

**Tab: ➕ Create Task**

1. Fill in task details:
   - **Title**: Clear, descriptive title (e.g., "Fix dashboard loading performance")
   - **Description**: Detailed explanation of what needs to be done
   - **Task Type**: feature, bug_fix, enhancement, qa, refactor, documentation, investigation
   - **Priority**: critical, high, medium, low
   - **Assigned Agent**: Select appropriate agent for the task
   - **Feature Area**: System area (e.g., comprehensive_strategy, dashboard, xtrades)
   - **Estimated Duration**: Time estimate in minutes
   - **Tags**: Comma-separated tags (optional)
   - **Dependencies**: Task IDs that must complete first (optional)

2. Click **✅ Create Task**

3. The task is added to the database with status `pending`

### Managing Tasks

**Tab: 📋 Task List**

**Filters:**
- **Status**: Filter by pending, in_progress, completed, failed, blocked, cancelled
- **Priority**: Filter by critical, high, medium, low
- **Feature Area**: Filter by specific feature
- **Agent**: Filter by assigned agent

**Task Cards:**

Each task displays as an expandable card with:
- Priority indicator (🔴 critical, 🟠 high, 🟡 medium, 🟢 low)
- Status indicator (⏳ pending, 🔄 in_progress, ✅ completed, ❌ failed, 🚫 blocked)
- Task details (description, feature area, agent, timing)
- Action buttons:
  - **▶️ Execute**: Start autonomous agent execution
  - **📝 Update Status**: Manually update task status
  - **📋 View Logs**: Show execution logs
  - **✅ Verify**: Verify completed tasks

### Task Execution

**Manual Execution:**
1. Open task card in Task List
2. Click **▶️ Execute** button
3. Task status changes to `in_progress`
4. Execution log entry created
5. Assigned agent processes the task (autonomous mode)

**Autonomous Execution:**
- Agents periodically check for `pending` tasks
- Dependencies are validated before execution
- Progress logged to `task_execution_log` table
- Status updated based on execution outcome

### Task Verification

**For Completed Tasks:**

1. Open completed task card
2. Click **✅ Verify** button
3. View verification status from QA agent
4. Provide user feedback:
   - **approved**: Task complete and accepted
   - **work_again**: Needs another iteration
   - **needs_changes**: Specific changes required
   - **rejected**: Task output not acceptable

5. Add optional comments
6. Click **💾 Submit Feedback**

### Analytics

**Tab: 📊 Analytics**

**Overall Metrics:**
- Total tasks count
- Completed tasks count
- In-progress tasks count
- Pending tasks count

**Visualizations:**
- Tasks by Status (bar chart)
- Tasks by Priority (bar chart)
- Feature Area Progress (table with completion percentages)
- Agent Workload Distribution (table with task counts and avg completion time)

### System Status

**Tab: ⚙️ System Status**

**Database Status:**
- Connection status
- Table count
- Last activity timestamp

**Maintenance Actions:**
- **🗑️ Clean Old Logs**: Remove execution logs older than 30 days
- **📊 Refresh Analytics**: Rebuild analytics views
- **🔍 Verify Schema**: Check database schema integrity

## API Reference

### TaskManager Class

```python
from src.task_manager import TaskManager

manager = TaskManager()
```

**Connection Management:**
```python
manager.connect()           # Establish connection
manager.disconnect()        # Close connection
manager.is_connected()      # Check connection status
```

**Task Operations:**
```python
# Create task
task_id = manager.create_task(
    title="Fix bug in dashboard",
    description="Detailed description...",
    task_type="bug_fix",
    priority="high",
    assigned_agent="backend-architect",
    feature_area="dashboard",
    estimated_duration_minutes=60,
    tags=["urgent", "frontend"],
    dependencies=[1, 3]  # Optional
)

# Fetch tasks
tasks = manager.fetch_tasks(
    status=["pending", "in_progress"],
    priority=["critical", "high"],
    feature_area="dashboard",
    assigned_agent="backend-architect"
)

# Get single task
task = manager.get_task_by_id(task_id)

# Update task status
manager.update_task_status(
    task_id=task_id,
    new_status="in_progress",
    message="Started working on task"
)

# Update task fields
manager.update_task(
    task_id=task_id,
    priority="critical",
    estimated_duration_minutes=120
)
```

**Execution Logging:**
```python
manager.log_execution(
    task_id=task_id,
    agent_name="backend-architect",
    action_type="progress_update",
    message="Completed step 1 of 3",
    files_modified=["src/dashboard.py", "src/utils.py"],
    duration_seconds=300
)

# Fetch logs
logs = manager.fetch_task_logs(task_id, limit=50)
```

**Verification:**
```python
# Create verification
manager.create_verification(
    task_id=task_id,
    verified_by="qa_agent",
    passed=True,
    verification_notes="All tests passed",
    test_results={"total": 10, "passed": 10, "failed": 0}
)

# Save user feedback
manager.save_user_feedback(
    task_id=task_id,
    user_feedback="approved",
    user_comments="Great work!"
)
```

**File Tracking:**
```python
manager.track_file_change(
    task_id=task_id,
    file_path="/absolute/path/to/file.py",
    change_type="modified",
    lines_added=50,
    lines_removed=20,
    git_commit_hash="abc123def456"
)

# Fetch file changes
files = manager.fetch_task_files(task_id)
```

**Analytics:**
```python
# Overall metrics
metrics = manager.get_overall_metrics()

# Status distribution
status_dist = manager.get_status_distribution()

# Priority distribution
priority_dist = manager.get_priority_distribution()

# Feature progress
feature_progress = manager.get_feature_progress()

# Agent workload
agent_workload = manager.get_agent_workload()
```

## Task Workflow

### Task Lifecycle

```
┌─────────┐
│ pending │ ──────────────────────────────┐
└────┬────┘                               │
     │ Dependencies met                   │
     │ Agent picks up task                │
     ▼                                    │
┌────────────┐                            │
│in_progress │                            │
└────┬───┬───┘                            │
     │   │                                │
     │   └──────────► ┌─────────┐        │
     │                │ blocked  │        │
     │                └────┬─────┘        │
     │                     │              │
     │ Task complete       │ Unblocked    │
     ▼                     ▼              │
┌───────────┐         ┌─────────┐        │
│ completed │         │ pending │◄───────┘
└─────┬─────┘         └─────────┘
      │
      │ QA verification
      ▼
┌──────────────┐
│ verification │
└──────┬───────┘
       │
       │ User feedback
       ▼
┌────────────┐
│  approved  │
│  rejected  │
│work_again  │
└────────────┘
```

### Status Transitions

- **pending → in_progress**: Agent starts task execution
- **in_progress → completed**: Task finished successfully
- **in_progress → failed**: Task encountered errors
- **in_progress → blocked**: Task blocked by dependencies or external factors
- **blocked → pending**: Block resolved, task queued again
- **any → cancelled**: Task manually cancelled

## Database Schema Details

### development_tasks

Main task tracking table.

**Key Columns:**
- `id`: Primary key (auto-increment)
- `title`: Task title (required)
- `description`: Detailed task description
- `task_type`: bug_fix, feature, enhancement, qa, refactor, documentation, investigation
- `priority`: low, medium, high, critical
- `status`: pending, in_progress, completed, failed, blocked, cancelled
- `assigned_agent`: Agent responsible for execution
- `feature_area`: System component affected
- `dependencies`: Array of task IDs (prerequisites)
- `tags`: Array of tags for categorization
- `created_at`, `started_at`, `updated_at`, `completed_at`: Timestamps

**Indexes:**
- `idx_tasks_status`: Fast filtering by status
- `idx_tasks_priority_status`: Combined priority/status queries
- `idx_tasks_feature_area`: Feature-based filtering
- `idx_tasks_assigned_agent`: Agent workload queries

### task_execution_log

Audit log of all task activities.

**Key Columns:**
- `id`: Primary key
- `task_id`: Foreign key to development_tasks
- `execution_timestamp`: When action occurred
- `agent_name`: Agent that performed action
- `action_type`: started, progress_update, completed, failed, verification, blocked, resumed, cancelled
- `message`: Action description
- `files_modified`: Array of file paths
- `error_details`: Error messages if action failed
- `duration_seconds`: Action duration

### task_verification

Task verification and user feedback.

**Key Columns:**
- `id`: Primary key
- `task_id`: Foreign key to development_tasks
- `verified_by`: qa_agent, user, automated_test
- `verification_timestamp`: When verified
- `passed`: Boolean (true/false)
- `verification_notes`: Detailed findings
- `test_results`: JSONB field with test data
- `user_feedback`: approved, rejected, work_again, needs_changes
- `user_comments`: User's additional comments

### task_files

File change tracking.

**Key Columns:**
- `id`: Primary key
- `task_id`: Foreign key to development_tasks
- `file_path`: Absolute path to modified file
- `change_type`: created, modified, deleted, renamed
- `lines_added`, `lines_removed`: Code change metrics
- `git_commit_hash`: Git SHA if committed

## Database Functions

### calculate_task_duration(task_id)

Returns task duration in minutes from `started_at` to `completed_at`.

```sql
SELECT calculate_task_duration(123);
```

### check_task_dependencies(task_id)

Returns TRUE if all dependencies are completed, FALSE otherwise.

```sql
SELECT check_task_dependencies(456);
```

### get_feature_completion_percentage(feature_area)

Returns completion percentage for a feature area.

```sql
SELECT get_feature_completion_percentage('comprehensive_strategy');
```

## Views

### v_active_tasks

Lists all active tasks (pending, in_progress, blocked) with priority ordering and dependency status.

```sql
SELECT * FROM v_active_tasks;
```

### v_task_metrics

Performance metrics for completed tasks including duration accuracy, files changed, and verification status.

```sql
SELECT * FROM v_task_metrics
WHERE feature_area = 'dashboard'
ORDER BY completed_at DESC;
```

### v_feature_progress

Progress dashboard by feature area showing total, completed, in-progress, pending, and blocked task counts.

```sql
SELECT * FROM v_feature_progress
ORDER BY completion_percentage ASC;
```

### v_agent_workload

Agent workload distribution showing assigned, active, pending, completed, and failed task counts plus average completion time.

```sql
SELECT * FROM v_agent_workload
ORDER BY active_tasks DESC;
```

## Integration with Autonomous Agents

### Agent Workflow

1. **Task Discovery**: Agent queries for pending tasks assigned to it
2. **Dependency Check**: Validates all dependencies are completed
3. **Task Execution**: Performs work and logs progress
4. **Status Updates**: Updates task status based on execution outcome
5. **File Tracking**: Records all file modifications
6. **Verification**: QA agent verifies completed tasks
7. **User Feedback**: User approves or requests changes

### Agent Implementation Example

```python
from src.task_manager import TaskManager
import time

class BackendArchitectAgent:
    def __init__(self):
        self.manager = TaskManager()
        self.agent_name = "backend-architect"

    def run(self):
        """Main agent loop"""
        self.manager.connect()

        while True:
            # Find pending tasks assigned to this agent
            tasks = self.manager.fetch_tasks(
                status=["pending"],
                assigned_agent=self.agent_name,
                limit=1
            )

            if not tasks:
                print("No pending tasks. Waiting...")
                time.sleep(60)
                continue

            task = tasks[0]
            task_id = task['id']

            # Check dependencies
            if not self.manager.check_dependencies_met(task_id):
                print(f"Task {task_id} dependencies not met")
                continue

            # Execute task
            self.execute_task(task)

            time.sleep(30)

    def execute_task(self, task):
        """Execute a single task"""
        task_id = task['id']

        try:
            # Update status to in_progress
            self.manager.update_task_status(
                task_id,
                "in_progress",
                "Task execution started by agent"
            )

            # Log start
            self.manager.log_execution(
                task_id=task_id,
                agent_name=self.agent_name,
                action_type="started",
                message=f"Starting execution of: {task['title']}"
            )

            # Perform actual work here
            # ...

            # Log completion
            self.manager.update_task_status(
                task_id,
                "completed",
                "Task completed successfully"
            )

            # Track files modified
            self.manager.track_file_change(
                task_id=task_id,
                file_path="/path/to/modified/file.py",
                change_type="modified",
                lines_added=50,
                lines_removed=20
            )

        except Exception as e:
            # Log failure
            self.manager.update_task_status(
                task_id,
                "failed",
                f"Task failed: {str(e)}"
            )

            self.manager.log_execution(
                task_id=task_id,
                agent_name=self.agent_name,
                action_type="failed",
                message="Task execution failed",
                error_details=str(e)
            )

# Run agent
agent = BackendArchitectAgent()
agent.run()
```

## Troubleshooting

### Database Connection Issues

**Problem**: "Failed to connect to database"

**Solutions:**
1. Verify PostgreSQL is running: `pg_isready`
2. Check database exists: `psql -U postgres -l | grep magnus`
3. Verify credentials in `.env` file
4. Test connection manually: `psql -U postgres -d magnus`

### Schema Not Found

**Problem**: "Missing tables" error

**Solutions:**
1. Re-deploy schema: `psql -U postgres -d magnus -f src/task_management_schema.sql`
2. Verify tables exist: `\dt` in psql
3. Check permissions: `GRANT ALL ON ALL TABLES IN SCHEMA public TO postgres;`

### Task Stuck in "pending"

**Problem**: Task remains in pending status

**Solutions:**
1. Check dependencies: `SELECT check_task_dependencies(task_id);`
2. Verify agent is running and checking for tasks
3. Check task filters in agent code match task properties

### No Logs Appearing

**Problem**: Execution logs not showing in UI

**Solutions:**
1. Verify logging calls in agent code
2. Check `task_execution_log` table directly: `SELECT * FROM task_execution_log WHERE task_id = X;`
3. Ensure `task_id` is correct in log calls

## Best Practices

### Task Creation

1. **Clear Titles**: Use descriptive, actionable titles
2. **Detailed Descriptions**: Include acceptance criteria and context
3. **Realistic Estimates**: Base estimates on similar past tasks
4. **Appropriate Priority**: Reserve "critical" for true emergencies
5. **Tag Consistently**: Use consistent tag naming conventions
6. **Define Dependencies**: Link related tasks to ensure proper sequencing

### Task Execution

1. **Log Progress**: Log significant milestones during execution
2. **Track Files**: Record all file modifications for traceability
3. **Handle Errors Gracefully**: Log detailed error information
4. **Update Status Promptly**: Keep task status current
5. **Request Help When Blocked**: Set status to "blocked" with clear reason

### Verification

1. **Test Thoroughly**: Verify all acceptance criteria met
2. **Document Findings**: Provide detailed verification notes
3. **Include Test Results**: Attach test output or screenshots
4. **Provide Constructive Feedback**: Help improve future work

## Future Enhancements

Potential improvements to the Enhancement Manager:

1. **Real-time Notifications**: Telegram/Slack alerts for task status changes
2. **Task Templates**: Pre-defined task templates for common work types
3. **Time Tracking**: Automatic time tracking with start/stop functionality
4. **Kanban Board View**: Visual board with drag-and-drop task management
5. **Sprint Planning**: Group tasks into sprints with velocity tracking
6. **Code Review Integration**: Link to GitHub PRs and code reviews
7. **AI Task Suggestions**: AI-powered task prioritization and assignments
8. **Resource Allocation**: Track agent capacity and workload balancing
9. **Burndown Charts**: Visual progress tracking over time
10. **Task Dependencies Graph**: Visual dependency graph with critical path

## Support

For issues or questions:
- Review this documentation
- Check database logs: `/var/log/postgresql/`
- Review application logs in console output
- Contact development team

---

**Version**: 1.0.0
**Last Updated**: 2025-11-07
**Author**: Full Stack Developer Agent
