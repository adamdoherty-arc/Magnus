"""
Populate Initial Development Tasks

This script adds the initial set of development tasks to track
the WheelStrategy project's pending work.
"""

from src.task_db_manager import TaskDBManager
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Initialize task manager
task_mgr = TaskDBManager()

# Define initial tasks based on project status and broken features
initial_tasks = [
    {
        "title": "Fix Xtrades Scraper - Chrome Driver Compatibility",
        "description": "Resolve Chrome driver version mismatch causing scraper failures. Update to use compatible Chrome driver version.",
        "task_type": "bug_fix",
        "priority": "high",
        "assigned_agent": "backend-architect",
        "feature_area": "xtrades",
        "estimated_duration_minutes": 60,
        "tags": ["scraper", "selenium", "chrome_driver"]
    },
    {
        "title": "Fix CSP Opportunities - Schema Mismatch",
        "description": "Resolve delta range calculation and schema mismatch issues in CSP opportunities finder.",
        "task_type": "bug_fix",
        "priority": "high",
        "assigned_agent": "database-optimizer",
        "feature_area": "comprehensive_strategy",
        "estimated_duration_minutes": 90,
        "tags": ["csp", "database", "schema"]
    },
    {
        "title": "Implement Premium Options Flow Feature",
        "description": "Add institutional money tracking feature to identify large options orders and premium flow patterns.",
        "task_type": "feature",
        "priority": "medium",
        "assigned_agent": "backend-architect",
        "feature_area": "options_flow",
        "estimated_duration_minutes": 240,
        "tags": ["options", "premium_flow", "analytics"]
    },
    {
        "title": "Dashboard Performance Optimization",
        "description": "Optimize slow queries in positions page and comprehensive strategy dashboard. Add appropriate indexes.",
        "task_type": "enhancement",
        "priority": "high",
        "assigned_agent": "database-optimizer",
        "feature_area": "dashboard",
        "estimated_duration_minutes": 120,
        "tags": ["performance", "dashboard", "indexing"]
    },
    {
        "title": "Kalshi Integration - Market Sync",
        "description": "Complete Kalshi market synchronization and display prediction markets in dashboard.",
        "task_type": "feature",
        "priority": "medium",
        "assigned_agent": "backend-architect",
        "feature_area": "kalshi",
        "estimated_duration_minutes": 180,
        "tags": ["kalshi", "api", "markets"]
    },
    {
        "title": "AVA Telegram Bot - Enhanced Portfolio Tracking",
        "description": "Add portfolio balance tracking and real-time position updates to AVA bot.",
        "task_type": "enhancement",
        "priority": "medium",
        "assigned_agent": "backend-architect",
        "feature_area": "ava",
        "estimated_duration_minutes": 150,
        "tags": ["telegram", "bot", "portfolio"]
    },
    {
        "title": "QA - Comprehensive Testing of All Features",
        "description": "Perform end-to-end testing of all major features: dashboard, xtrades scraper, CSP opportunities, positions tracking.",
        "task_type": "qa",
        "priority": "high",
        "assigned_agent": "qa-agent",
        "feature_area": "dashboard",
        "estimated_duration_minutes": 180,
        "tags": ["qa", "testing", "integration"]
    },
    {
        "title": "Database Schema Refactoring - Normalize Positions Table",
        "description": "Refactor positions table to eliminate redundancy and improve data integrity.",
        "task_type": "refactor",
        "priority": "low",
        "assigned_agent": "database-optimizer",
        "feature_area": "database",
        "estimated_duration_minutes": 120,
        "tags": ["database", "normalization", "schema"]
    },
    {
        "title": "After-Hours Pricing - Fix Data Fetch Issues",
        "description": "Resolve issues with fetching after-hours stock prices from Robinhood API.",
        "task_type": "bug_fix",
        "priority": "medium",
        "assigned_agent": "backend-architect",
        "feature_area": "dashboard",
        "estimated_duration_minutes": 90,
        "tags": ["pricing", "robinhood", "api"]
    },
    {
        "title": "Documentation - API and Database Schema",
        "description": "Create comprehensive documentation for database schema, API endpoints, and system architecture.",
        "task_type": "documentation",
        "priority": "low",
        "assigned_agent": "backend-architect",
        "feature_area": "documentation",
        "estimated_duration_minutes": 240,
        "tags": ["docs", "api", "architecture"]
    }
]

print("Populating initial development tasks...")
print("=" * 60)

created_tasks = []

for task_data in initial_tasks:
    try:
        task_id = task_mgr.create_task(**task_data)
        created_tasks.append((task_id, task_data['title']))
        print(f"[CREATED] Task {task_id}: {task_data['title']}")

        # Log initial creation
        task_mgr.log_execution(
            task_id=task_id,
            agent_name="system",
            action_type="started",
            message=f"Task created and queued for {task_data['assigned_agent']}"
        )

    except Exception as e:
        print(f"[ERROR] Failed to create task '{task_data['title']}': {e}")

print()
print("=" * 60)
print(f"[SUCCESS] Created {len(created_tasks)} tasks")
print()

# Display summary
print("Task Summary:")
print()

# Get active tasks
active_tasks = task_mgr.get_active_tasks()
print(f"Total Active Tasks: {len(active_tasks)}")
print()

# Group by priority
priority_counts = {}
for task in active_tasks:
    priority = task['priority']
    priority_counts[priority] = priority_counts.get(priority, 0) + 1

print("By Priority:")
for priority in ['critical', 'high', 'medium', 'low']:
    count = priority_counts.get(priority, 0)
    if count > 0:
        print(f"  - {priority.upper()}: {count} tasks")

print()

# Group by agent
agent_workload = task_mgr.get_agent_workload()
print("Agent Workload:")
for agent in agent_workload:
    print(f"  - {agent['assigned_agent']}: {agent['pending_tasks']} pending tasks")

print()

# Feature progress
feature_progress = task_mgr.get_feature_progress()
print("Feature Areas:")
for feature in feature_progress:
    print(f"  - {feature['feature_area']}: {feature['pending_tasks']} pending, {feature['completion_percentage']}% complete")

print()
print("=" * 60)
print("[COMPLETE] Initial task population finished!")
