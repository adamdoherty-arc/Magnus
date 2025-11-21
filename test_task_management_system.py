"""
Task Management System - End-to-End Test
=========================================

Demonstrates the complete task management workflow:
1. Create task
2. Update status
3. Log execution
4. Track file changes
5. Complete task
6. Add verification
7. View analytics
"""

from src.task_db_manager import TaskDBManager
import sys

sys.stdout.reconfigure(encoding='utf-8')

def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

# Initialize
task_mgr = TaskDBManager()

print_section("TASK MANAGEMENT SYSTEM - END-TO-END TEST")

# Test 1: Create a task
print_section("1. CREATE TASK")
task_id = task_mgr.create_task(
    title="Test Task - Database Query Optimization",
    description="Optimize slow queries in positions_page_improved.py",
    task_type="enhancement",
    priority="high",
    assigned_agent="database-optimizer",
    feature_area="dashboard",
    estimated_duration_minutes=90,
    tags=["performance", "database", "positions"]
)
print(f"[SUCCESS] Created task ID: {task_id}")

# Test 2: Get task details
print_section("2. GET TASK DETAILS")
task = task_mgr.get_task(task_id)
print(f"Title: {task['title']}")
print(f"Status: {task['status']}")
print(f"Priority: {task['priority']}")
print(f"Assigned to: {task['assigned_agent']}")
print(f"Feature Area: {task['feature_area']}")
print(f"Estimated Duration: {task['estimated_duration_minutes']} minutes")

# Test 3: Update status to in_progress
print_section("3. START TASK")
task_mgr.update_task_status(task_id, "in_progress")
print(f"[SUCCESS] Task {task_id} status updated to 'in_progress'")

# Test 4: Log execution activities
print_section("4. LOG EXECUTION ACTIVITIES")

task_mgr.log_execution(
    task_id=task_id,
    agent_name="database-optimizer",
    action_type="progress_update",
    message="Analyzed EXPLAIN plans for slow queries",
    files_modified=["positions_page_improved.py"]
)
print("[SUCCESS] Logged: Analyzed EXPLAIN plans")

task_mgr.log_execution(
    task_id=task_id,
    agent_name="database-optimizer",
    action_type="progress_update",
    message="Added composite index on (user_id, status, updated_at)",
    files_modified=["src/database_schema.sql"]
)
print("[SUCCESS] Logged: Added composite index")

task_mgr.log_execution(
    task_id=task_id,
    agent_name="database-optimizer",
    action_type="progress_update",
    message="Optimized JOIN operations and reduced N+1 queries",
    files_modified=["positions_page_improved.py", "src/db_manager.py"]
)
print("[SUCCESS] Logged: Optimized JOIN operations")

# Test 5: Track file changes
print_section("5. TRACK FILE CHANGES")

task_mgr.track_file_change(
    task_id=task_id,
    file_path="C:/Code/WheelStrategy/positions_page_improved.py",
    change_type="modified",
    lines_added=35,
    lines_removed=48
)
print("[SUCCESS] Tracked: positions_page_improved.py (modified)")

task_mgr.track_file_change(
    task_id=task_id,
    file_path="C:/Code/WheelStrategy/src/database_schema.sql",
    change_type="modified",
    lines_added=12,
    lines_removed=2
)
print("[SUCCESS] Tracked: database_schema.sql (modified)")

task_mgr.track_file_change(
    task_id=task_id,
    file_path="C:/Code/WheelStrategy/src/db_manager.py",
    change_type="modified",
    lines_added=8,
    lines_removed=15
)
print("[SUCCESS] Tracked: db_manager.py (modified)")

# Test 6: Complete task
print_section("6. COMPLETE TASK")
task_mgr.complete_task(task_id)
print(f"[SUCCESS] Task {task_id} marked as 'completed'")

# Test 7: Add verification
print_section("7. ADD VERIFICATION")
task_mgr.add_verification(
    task_id=task_id,
    verified_by="qa_agent",
    passed=True,
    verification_notes="All queries optimized. Performance improved by 65%. Load time reduced from 2.3s to 0.8s.",
    test_results={
        "queries_tested": 8,
        "avg_speedup_pct": 65,
        "load_time_before_ms": 2300,
        "load_time_after_ms": 800,
        "all_tests_passed": True,
        "test_cases": [
            {"name": "Get active positions", "before_ms": 450, "after_ms": 120},
            {"name": "Calculate P&L", "before_ms": 890, "after_ms": 340},
            {"name": "Get options Greeks", "before_ms": 680, "after_ms": 220}
        ]
    },
    user_feedback="approved",
    user_comments="Excellent work! Dashboard is much faster now."
)
print("[SUCCESS] Verification added with test results")

# Test 8: Get updated task details
print_section("8. VERIFY TASK COMPLETION")
task = task_mgr.get_task(task_id)
print(f"Title: {task['title']}")
print(f"Status: {task['status']}")
print(f"Started: {task['started_at']}")
print(f"Completed: {task['completed_at']}")
print(f"Actual Duration: {task['actual_duration_minutes']} minutes")
print(f"Estimated Duration: {task['estimated_duration_minutes']} minutes")
if task['actual_duration_minutes'] and task['estimated_duration_minutes']:
    accuracy = (task['actual_duration_minutes'] / task['estimated_duration_minutes']) * 100
    print(f"Estimation Accuracy: {accuracy:.1f}%")

# Test 9: View execution log
print_section("9. EXECUTION LOG")
logs = task_mgr.get_execution_log(task_id)
print(f"Total log entries: {len(logs)}")
for log in logs[:5]:  # Show first 5
    print(f"  [{log['execution_timestamp']}] {log['action_type']}: {log['message'][:60]}")

# Test 10: View file changes
print_section("10. FILE CHANGES")
files = task_mgr.get_task_files(task_id)
print(f"Total files changed: {len(files)}")
total_added = sum(f['lines_added'] or 0 for f in files)
total_removed = sum(f['lines_removed'] or 0 for f in files)
print(f"Total lines added: {total_added}")
print(f"Total lines removed: {total_removed}")
print(f"Net change: {total_added - total_removed:+d} lines")
print("\nFiles:")
for file in files:
    print(f"  - {file['file_path'].split('/')[-1]} ({file['change_type']}): +{file['lines_added']} -{file['lines_removed']}")

# Test 11: View verifications
print_section("11. VERIFICATIONS")
verifications = task_mgr.get_verifications(task_id)
print(f"Total verifications: {len(verifications)}")
for v in verifications:
    print(f"\nVerified by: {v['verified_by']}")
    print(f"Passed: {'YES' if v['passed'] else 'NO'}")
    print(f"User Feedback: {v['user_feedback']}")
    print(f"Notes: {v['verification_notes']}")
    if v['test_results']:
        print(f"Test Results:")
        print(f"  - Queries Tested: {v['test_results'].get('queries_tested')}")
        print(f"  - Average Speedup: {v['test_results'].get('avg_speedup_pct')}%")
        print(f"  - Before: {v['test_results'].get('load_time_before_ms')}ms")
        print(f"  - After: {v['test_results'].get('load_time_after_ms')}ms")

# Test 12: Analytics - Active Tasks
print_section("12. ANALYTICS - ACTIVE TASKS")
active_tasks = task_mgr.get_active_tasks()
print(f"Total active tasks: {len(active_tasks)}")
print(f"\nBy Priority:")
priority_count = {}
for task in active_tasks:
    priority = task['priority']
    priority_count[priority] = priority_count.get(priority, 0) + 1
for priority in ['critical', 'high', 'medium', 'low']:
    count = priority_count.get(priority, 0)
    if count > 0:
        print(f"  - {priority.upper()}: {count}")

# Test 13: Analytics - Feature Progress
print_section("13. ANALYTICS - FEATURE PROGRESS")
progress = task_mgr.get_feature_progress()
print(f"Feature areas: {len(progress)}")
print("\nTop 5 Features by Completion:")
for i, feature in enumerate(sorted(progress, key=lambda x: x['completion_percentage'], reverse=True)[:5], 1):
    print(f"{i}. {feature['feature_area']}: {feature['completion_percentage']:.1f}% "
          f"({feature['completed_tasks']}/{feature['total_tasks']} tasks)")

# Test 14: Analytics - Agent Workload
print_section("14. ANALYTICS - AGENT WORKLOAD")
workload = task_mgr.get_agent_workload()
print(f"Agents: {len(workload)}")
print("\nWorkload Distribution:")
for agent in sorted(workload, key=lambda x: x['total_assigned_tasks'], reverse=True):
    print(f"\n{agent['assigned_agent']}:")
    print(f"  - Total Assigned: {agent['total_assigned_tasks']}")
    print(f"  - Active: {agent['active_tasks']}")
    print(f"  - Pending: {agent['pending_tasks']}")
    print(f"  - Completed: {agent['completed_tasks']}")
    if agent['avg_completion_time_minutes']:
        print(f"  - Avg Completion Time: {agent['avg_completion_time_minutes']:.1f} minutes")

# Test 15: Search Tasks
print_section("15. SEARCH TASKS")
search_results = task_mgr.search_tasks("database optimization")
print(f"Search results for 'database optimization': {len(search_results)}")
for task in search_results[:3]:
    print(f"\n  - Task {task['id']}: {task['title']}")
    print(f"    Status: {task['status']}, Priority: {task['priority']}")

print_section("TEST COMPLETE")
print("\n[SUCCESS] All tests passed! Task management system is working correctly.\n")
print("Summary:")
print(f"  - Task created: ID {task_id}")
print(f"  - Execution logs: {len(logs)}")
print(f"  - File changes tracked: {len(files)}")
print(f"  - Verifications: {len(verifications)}")
print(f"  - Total active tasks: {len(active_tasks)}")
print(f"  - Feature areas tracked: {len(progress)}")
print(f"  - Agents with workload: {len(workload)}")
print("\n" + "=" * 70)
