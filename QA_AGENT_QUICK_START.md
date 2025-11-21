# QA Verification Agent - Quick Start Guide

## What is it?

An intelligent automated testing agent that verifies task completion by running:
- File existence checks
- Python syntax validation
- Feature-specific tests
- Integration tests (page loads)
- Database schema validation

## 5-Minute Quick Start

### 1. Basic Usage (Command Line)

```bash
# Verify a task by ID
python src/qa_verification_agent.py 123

# Get JSON output
python src/qa_verification_agent.py 123 --json
```

### 2. Basic Usage (Python)

```python
from src.qa_verification_agent import get_qa_agent

qa_agent = get_qa_agent()
results = qa_agent.verify_task(task_id=123)

if results['passed']:
    print("✓ All checks passed!")
else:
    print(f"✗ {len(results['failures'])} checks failed")
```

### 3. Complete Workflow

```python
from src.task_db_manager import TaskDBManager
from src.qa_verification_agent import get_qa_agent

task_mgr = TaskDBManager()
qa_agent = get_qa_agent()

# 1. Create task
task_id = task_mgr.create_task(
    title="Fix dashboard bug",
    feature_area="dashboard",
    task_type="bug_fix",
    priority="high",
    assigned_agent="backend-architect"
)

# 2. Track file changes
task_mgr.track_file_change(
    task_id=task_id,
    file_path="c:\\Code\\WheelStrategy\\dashboard.py",
    change_type="modified",
    lines_added=15,
    lines_removed=5
)

# 3. Log execution
task_mgr.log_execution(
    task_id=task_id,
    agent_name="backend-architect",
    action_type="completed",
    message="Fixed CSP display logic"
)

# 4. Complete task
task_mgr.update_task_status(task_id, "completed")

# 5. Run QA verification
results = qa_agent.verify_task(task_id)

# 6. Review results
print(f"Task #{task_id} verification: {'PASSED' if results['passed'] else 'FAILED'}")
print(f"Checks: {len(results['checks_run'])}")
print(f"Failures: {len(results['failures'])}")
```

## Understanding Results

### Status Codes

- `[PASS]` - Check passed successfully
- `[FAIL]` - Check failed (verification fails)
- `[WARN]` - Warning (doesn't fail verification)
- `[SKIP]` - Check skipped (doesn't affect pass/fail)

### Result Structure

```json
{
  "task_id": 123,
  "passed": true/false,
  "checks_run": [
    {
      "name": "File Existence Check",
      "passed": true,
      "details": ["[PASS] Found: file.py"]
    }
  ],
  "failures": [...],  // Checks that failed
  "warnings": [...],  // Things to be aware of
  "summary": "..."    // Human-readable summary
}
```

## 5 Verification Checks

### 1. File Existence Check
Verifies all tracked files exist

**Example Output:**
```
[PASS] Found: dashboard.py (15,234 bytes)
[FAIL] Missing: deleted_file.py
```

### 2. Python Syntax Validation
Compiles Python files to detect errors

**Example Output:**
```
[PASS] Valid syntax: dashboard.py
[FAIL] Syntax error in broken.py: Line 45: invalid syntax
```

### 3. Test Execution
Runs feature-specific test suites

**Example Output:**
```
[PASS] Tests passed: test_dashboard_display.py
[FAIL] Tests failed: test_feature.py (Return code: 1)
```

### 4. Integration Testing
Tests page imports and render functions

**Example Output:**
```
[PASS] dashboard_page imports successfully
[FAIL] Import failed: missing_module
```

### 5. Database Schema Validation
Verifies database tables exist (for DB tasks)

**Example Output:**
```
[PASS] Table 'development_tasks' exists (45 rows)
[FAIL] Database connection failed
```

## Common Use Cases

### Verify Single Task

```python
qa_agent = get_qa_agent()
results = qa_agent.verify_task(123)
print(results['summary'])
```

### Verify After Task Completion

```python
# In your completion workflow
def complete_and_verify(task_id):
    task_mgr.update_task_status(task_id, "completed")
    results = qa_agent.verify_task(task_id)
    return results['passed']
```

### Batch Verification

```python
task_mgr = TaskDBManager()
qa_agent = get_qa_agent()

# Get all completed tasks
completed = task_mgr.get_tasks_by_status("completed")

for task in completed:
    results = qa_agent.verify_task(task['id'])
    print(f"Task #{task['id']}: {'PASS' if results['passed'] else 'FAIL'}")
```

### Get Verification History

```python
task_mgr = TaskDBManager()

# Get all verifications for a task
verifications = task_mgr.get_verifications(task_id=123)

for v in verifications:
    print(f"{v['verification_timestamp']}: {v['passed']}")
    print(f"  Verified by: {v['verified_by']}")
```

## Feature Test Mapping

The agent automatically runs tests for these feature areas:

| Feature Area | Test File |
|-------------|-----------|
| `comprehensive_strategy` | `test_comprehensive_integration_live.py` |
| `xtrades` | `test_xtrades_complete.py` |
| `dashboard` | `test_dashboard_display.py` |
| `task_management` | `test_task_management_system.py` |
| `ai_options_agent` | `test_ai_options_agent.py` |

## Page Integration Test Mapping

For integration tests, the agent checks these pages:

| Feature Area | Page Module |
|-------------|-------------|
| `comprehensive_strategy` | `comprehensive_strategy_page` |
| `enhancement_manager` | `enhancement_manager_page` |
| `ai_options_agent` | `ai_options_agent_page` |

## Troubleshooting

### Test File Not Found

**Error**: `[WARN] Test file not found: test_feature.py`

**Fix**: Create the test file or add to test mapping

### Database Connection Failed

**Error**: `[FAIL] Database connection failed`

**Fix**:
1. Check PostgreSQL is running
2. Verify `.env` credentials
3. Confirm database exists

### Import Error

**Error**: `[FAIL] Import failed: module_name`

**Fix**:
1. Install missing dependencies
2. Check module exists
3. Fix circular imports

### Syntax Error

**Error**: `[FAIL] Syntax error in file.py: Line 42`

**Fix**: Open file and fix syntax at line 42

## Configuration

### Add New Feature Test Mapping

Edit `src/qa_verification_agent.py`:

```python
# In _run_tests method, update test_mapping:
test_mapping = {
    'comprehensive_strategy': 'test_comprehensive_integration_live.py',
    'your_feature': 'test_your_feature.py',  # Add here
}
```

### Add New Page Test Mapping

Edit `src/qa_verification_agent.py`:

```python
# In _test_page_loads method, update page_mapping:
page_mapping = {
    'comprehensive_strategy': 'comprehensive_strategy_page',
    'your_page': 'your_page_module',  # Add here
}
```

### Change Test Timeout

Default is 120 seconds. To change:

```python
# In _run_tests method
result = subprocess.run(
    [sys.executable, test_path],
    timeout=180,  # Change to 180 seconds
    # ...
)
```

## Best Practices

### 1. Always Track Files

```python
task_mgr.track_file_change(
    task_id=task_id,
    file_path="absolute/path/to/file.py",  # Use absolute paths
    change_type="modified"
)
```

### 2. Write Tests for Every Feature

Create `test_<feature>.py` for each feature area

### 3. Review Details, Not Just Pass/Fail

```python
results = qa_agent.verify_task(task_id)

# Don't just check passed
if not results['passed']:
    # Review what failed
    for failure in results['failures']:
        print(f"Failed: {failure['name']}")
        for detail in failure['details']:
            print(f"  {detail}")
```

### 4. Use Meaningful Task Descriptions

Include keywords to help categorization:
- Database tasks: "database", "schema", "table"
- UI tasks: "page", "dashboard", "display"
- API tasks: "api", "endpoint", "route"

### 5. Automate in Your Workflow

```python
def my_task_completion_workflow(task_id):
    # Complete task
    task_mgr.update_task_status(task_id, "completed")

    # Auto-verify
    results = qa_agent.verify_task(task_id)

    # Handle failures
    if not results['passed']:
        send_alert(f"Task {task_id} verification failed")
        task_mgr.update_task_status(task_id, "failed")

    return results
```

## Exit Codes (Command Line)

```bash
python src/qa_verification_agent.py 123
echo $?  # Exit code
```

- `0` - All checks passed
- `1` - One or more checks failed

## Logging

Enable debug logging for detailed output:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from src.qa_verification_agent import get_qa_agent
qa_agent = get_qa_agent()
```

## Next Steps

1. **Read Full Documentation**: See `QA_AGENT_DOCUMENTATION.md`
2. **Run Test**: `python test_qa_agent.py`
3. **Verify Your Tasks**: `python src/qa_verification_agent.py <task_id>`
4. **Integrate in Workflow**: Add to your task completion process
5. **Customize**: Add feature-specific test mappings

## Example: Complete Task Workflow

```python
#!/usr/bin/env python
"""
Complete task workflow with automatic QA verification
"""

from src.task_db_manager import TaskDBManager
from src.qa_verification_agent import get_qa_agent
import sys

def complete_task_workflow(task_id: int) -> bool:
    """Complete task and verify automatically"""
    task_mgr = TaskDBManager()
    qa_agent = get_qa_agent()

    # Get task
    task = task_mgr.get_task(task_id)
    if not task:
        print(f"Task {task_id} not found")
        return False

    print(f"Completing task #{task_id}: {task['title']}")

    # Complete task
    task_mgr.update_task_status(task_id, "completed")

    # Run QA verification
    print("\nRunning QA verification...")
    results = qa_agent.verify_task(task_id)

    # Print summary
    print(f"\n{'='*80}")
    if results['passed']:
        print("[SUCCESS] Task completed and verified")
        return True
    else:
        print("[FAILED] Task verification failed")
        print(f"\nFailed checks: {len(results['failures'])}")
        for failure in results['failures']:
            print(f"  - {failure['name']}")

        # Revert to in_progress
        task_mgr.update_task_status(task_id, "in_progress")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python complete_task.py <task_id>")
        sys.exit(1)

    task_id = int(sys.argv[1])
    success = complete_task_workflow(task_id)
    sys.exit(0 if success else 1)
```

Save as `complete_task.py` and run:

```bash
python complete_task.py 123
```

---

**For complete documentation, see**: `QA_AGENT_DOCUMENTATION.md`

**Test the agent**: `python test_qa_agent.py`

**Run verification**: `python src/qa_verification_agent.py <task_id>`
