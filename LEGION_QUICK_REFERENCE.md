# Legion Integration - Quick Reference

**For:** Magnus Trading Platform
**Date:** January 10, 2025
**Status:** ✅ Production Ready

---

## 🚀 Quick Start (5 Minutes)

### From Legion - Send a Task

```python
from src.legion import process_legion_task
import json

# Create task
task = {
    "legion_task_id": "uuid-from-legion",
    "project_name": "Magnus",  # MUST be "Magnus"
    "title": "Add feature X",
    "description": "Detailed description...",
    "task_type": "feature",  # feature, bug_fix, enhancement, refactor
    "priority": "medium",  # low, medium, high, critical
    "estimated_duration_minutes": 90
}

# Send to Magnus
response = process_legion_task(json.dumps(task))

# Check response
if response['status'] == 'accepted':
    print(f"✅ Task created: Magnus ID {response['magnus_task_id']}")
else:
    print(f"❌ Error: {response.get('error')}")
```

### From Legion - Check Progress

```python
from src.legion import LegionOperatorAgent

operator = LegionOperatorAgent()
progress = operator.get_task_progress("uuid-from-legion")

print(f"Status: {progress.status}")
print(f"Progress: {progress.progress_percentage}%")
print(f"Files: {progress.files_modified}")
```

---

## 📋 Task Format

### Minimal Task (Required Fields Only)
```json
{
    "legion_task_id": "uuid-12345",
    "project_name": "Magnus",
    "title": "Brief title",
    "description": "What needs to be done",
    "task_type": "feature",
    "priority": "medium"
}
```

### Complete Task (All Fields)
```json
{
    "legion_task_id": "uuid-12345",
    "project_name": "Magnus",
    "title": "Add RSI indicator to premium scanner",
    "description": "Implement 14-period RSI calculation...",
    "task_type": "feature",
    "priority": "high",
    "assigned_agent": "frontend-developer",
    "feature_area": "premium_scanner",
    "estimated_duration_minutes": 120,
    "dependencies": ["uuid-dep-1", "uuid-dep-2"],
    "metadata": {
        "requested_by": "user@example.com",
        "deadline": "2025-01-15"
    }
}
```

---

## 🎯 Task Types

| Type | When to Use | Example |
|------|-------------|---------|
| `feature` | New functionality | "Add calendar spread analyzer" |
| `bug_fix` | Fix broken behavior | "Fix position P&L calculation" |
| `enhancement` | Improve existing feature | "Add sorting to opportunities table" |
| `refactor` | Code improvement | "Refactor database queries for performance" |
| `qa` | Testing/verification | "Add tests for CSP finder" |
| `documentation` | Docs only | "Document Kalshi integration API" |

---

## ⚡ Priority Levels

| Priority | Meaning | Response Time |
|----------|---------|---------------|
| `critical` | Production broken | <1 hour |
| `high` | Important feature/bug | <4 hours |
| `medium` | Standard work | <24 hours |
| `low` | Nice-to-have | <1 week |

---

## 🏗️ Magnus Features

### Core Trading Features:
1. **dashboard** - Portfolio overview and metrics
2. **opportunities** - CSP and covered call finder
3. **positions** - Active options tracking
4. **premium_scanner** - Advanced options screening
5. **database_scan** - Stock database management
6. **calendar_spreads** - Spread analysis with AI

### Analytics Features:
7. **ai_research** - Multi-agent stock analysis
8. **earnings_calendar** - Earnings date tracking

### Integration Features:
9. **tradingview_watchlists** - TradingView sync
10. **prediction_markets** - Kalshi integration

### Infrastructure:
11. **settings** - Configuration management
12. **enhancement_agent** - Autonomous improvement system

---

## 🤖 Agent Types

Legion can specify which Magnus agent to use:

| Agent | Use For |
|-------|---------|
| `postgresql-pglite-pro` | Database/SQL changes |
| `ai-engineer` | AI/ML features |
| `frontend-developer` | Streamlit UI changes |
| `backend-architect` | API/backend logic |
| `full-stack-developer` | General features |
| `debugger` | Bug fixes |
| `performance-engineer` | Optimization |
| `test-automator` | Testing |

**Auto-Selection:** Leave `assigned_agent` empty and Magnus will choose based on task description.

---

## 📊 Progress Tracking

### Progress Object
```python
{
    "legion_task_id": "uuid-12345",
    "magnus_task_id": 42,
    "status": "in_progress",  # pending, in_progress, completed, failed, blocked
    "progress_percentage": 50,  # 0-100
    "message": "Implementing feature...",
    "files_modified": ["dashboard.py", "src/indicators.py"],
    "error_details": null,
    "estimated_completion": "2025-01-10T15:30:00Z",
    "actual_duration_minutes": 45
}
```

### Status Values
- `pending` - Queued, not started
- `in_progress` - Currently being worked on
- `completed` - Successfully finished
- `failed` - Error occurred
- `blocked` - Waiting on dependencies

---

## 🔍 Get Magnus Context

### For Any Task Description
```python
from src.legion import get_context_for_legion

context = get_context_for_legion(
    "Add momentum indicators to dashboard"
)

# Returns detailed context:
# - Affected features
# - Files to modify
# - Best practices
# - Anti-patterns
# - Database schema
# - Implementation guidance
```

### Query Feature Details
```python
from src.legion import FeatureSpecRegistry

registry = FeatureSpecRegistry()

# Get spec for a feature
spec = registry.get_feature_spec("dashboard")

print(f"Entry Point: {spec.entry_point}")
print(f"Database Tables: {spec.database_schema.tables}")
print(f"Key Files: {spec.key_files}")
print(f"Dependencies: {spec.dependencies}")
print(f"Best Practices: {spec.best_practices}")
```

---

## 🛡️ Error Handling

### Task Rejection
```python
response = {
    "status": "rejected",
    "reason": "Task is for different project",
    "legion_task_id": "uuid-12345"
}
```

### Task Error
```python
response = {
    "status": "error",
    "legion_task_id": "uuid-12345",
    "error": "Database connection failed",
    "message": "Failed to process task"
}
```

### Progress Error
```python
progress = {
    "status": "failed",
    "error_details": "Unit tests failed: test_calculations",
    "files_modified": ["dashboard.py"],
    "actual_duration_minutes": 30
}
```

---

## 🔄 Sync Configuration

### Auto-Sync Daemon
```python
# Run this in background to sync Magnus → Legion
from src.legion import LegionOperatorAgent
import time

operator = LegionOperatorAgent(
    legion_db_url="postgresql://...",
    magnus_db_url="postgresql://..."
)

while True:
    # Get all active Legion tasks
    active_tasks = get_legion_tasks()  # Your function

    for legion_id in active_tasks:
        operator.sync_progress_to_legion(legion_id)

    time.sleep(30)  # Sync every 30 seconds
```

---

## 📈 Best Practices

### 1. Good Task Descriptions
```python
# ✅ GOOD - Specific and actionable
{
    "title": "Add RSI filter to premium scanner",
    "description": """
        Add RSI (14-period) calculation and filter to premium scanner.
        - Add RSI column to results table
        - Add filter: Show only RSI < 30 (oversold) or RSI > 70 (overbought)
        - Cache RSI data for 5 minutes
    """
}

# ❌ BAD - Vague
{
    "title": "Make scanner better",
    "description": "Add some technical indicators"
}
```

### 2. Specify Feature Area
```python
# Helps routing and context
{
    "feature_area": "dashboard",
    "description": "Add new metric..."
}
```

### 3. Realistic Duration Estimates
```python
# Guidelines:
{
    "estimated_duration_minutes": 60  # Small feature
}
{
    "estimated_duration_minutes": 120  # Medium feature
}
{
    "estimated_duration_minutes": 240  # Large feature
}
```

### 4. Use Dependencies
```python
# If task depends on others
{
    "dependencies": ["uuid-task-1", "uuid-task-2"]
}
# Magnus won't start until dependencies complete
```

---

## 🧪 Testing

### Test Integration
```bash
# Test feature specs
python src/legion/feature_spec_agents.py

# Test operator
python src/legion/legion_operator_agent.py
```

### Test Task Processing
```python
# Create test task
test_task = {
    "legion_task_id": "test-123",
    "project_name": "Magnus",
    "title": "Test integration",
    "description": "Verify Legion → Magnus works",
    "task_type": "feature",
    "priority": "low"
}

# Process it
from src.legion import process_legion_task
import json

response = process_legion_task(json.dumps(test_task))
print(json.dumps(response, indent=2))
```

---

## 📚 Key Files

### Integration Package
- `src/legion/__init__.py` - Package API
- `src/legion/feature_spec_agents.py` - AI specs for 12 features
- `src/legion/legion_operator_agent.py` - Operator agent

### Magnus Task System
- `src/task_manager.py` - Task management
- `src/task_db_manager.py` - Database operations
- `src/ava/autonomous_agent.py` - Execution engine

### Documentation
- `LEGION_INTEGRATION_COMPLETE.md` - Full documentation (50 pages)
- `LEGION_QUICK_REFERENCE.md` - This file

---

## 🆘 Troubleshooting

### Task Not Appearing
```python
# Check if task was created
from src.legion import LegionOperatorAgent

operator = LegionOperatorAgent()
progress = operator.get_task_progress("legion-uuid")

if not progress:
    # Check:
    # 1. project_name == "Magnus"
    # 2. DATABASE_URL set correctly
    # 3. Check operator logs
```

### Task Stuck
```sql
-- Check dependencies
SELECT id, title, status, dependencies
FROM development_tasks
WHERE id = <magnus_id>;
```

### Sync Failures
```python
# Verify Legion DB connection
operator = LegionOperatorAgent(
    legion_db_url="postgresql://..."  # Check this
)
```

---

## 🎯 Common Patterns

### Send Task + Poll Progress
```python
from src.legion import process_legion_task, LegionOperatorAgent
import json, time

# 1. Send task
task = {...}
response = process_legion_task(json.dumps(task))
legion_id = task['legion_task_id']

# 2. Poll for completion
operator = LegionOperatorAgent()
while True:
    progress = operator.get_task_progress(legion_id)

    print(f"{progress.status}: {progress.progress_percentage}%")

    if progress.status in ['completed', 'failed']:
        break

    time.sleep(30)

# 3. Handle result
if progress.status == 'completed':
    print(f"✅ Done! Files: {progress.files_modified}")
else:
    print(f"❌ Failed: {progress.error_details}")
```

### Batch Task Creation
```python
tasks = [
    {"title": "Feature 1", ...},
    {"title": "Feature 2", ...},
    {"title": "Feature 3", ...}
]

for task in tasks:
    response = process_legion_task(json.dumps(task))
    if response['status'] == 'accepted':
        print(f"✅ {task['title']}")
    else:
        print(f"❌ {task['title']}: {response.get('error')}")
```

---

## 📞 Support

### Check System Status
```python
from src.legion import LegionOperatorAgent

operator = LegionOperatorAgent()
stats = operator.get_stats()

print(f"""
Tasks Received: {stats['tasks_received']}
Tasks Translated: {stats['tasks_translated']}
Tasks Completed: {stats['tasks_completed']}
Tasks Failed: {stats['tasks_failed']}
Active Mappings: {stats['active_mappings']}
Features Known: {stats['magnus_features_known']}
""")
```

---

## ✅ Ready to Use!

**Minimum Working Example:**
```python
from src.legion import process_legion_task
import json

response = process_legion_task(json.dumps({
    "legion_task_id": "your-uuid",
    "project_name": "Magnus",
    "title": "Your task",
    "description": "What to do",
    "task_type": "feature",
    "priority": "medium"
}))

print(response)
```

That's it! Legion can now send tasks to Magnus. 🚀

---

**Created:** January 10, 2025
**Version:** 1.0.0
**Status:** Production Ready
