"""
Enhancement & Task Manager Page
Streamlit page for managing development tasks, tracking execution, and monitoring progress
Integrates with autonomous agent system for automated task execution
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json

# Import task manager
from src.task_manager import TaskManager


def render_enhancement_manager_page():
    """Main Enhancement & Task Manager page"""
    st.title("🚀 Enhancement & Task Manager")
    st.caption("Manage development tasks, track execution, and monitor autonomous agent progress")

    # Initialize task manager
    task_manager = TaskManager()

    # Check database connection
    if not task_manager.connect():
        st.error("❌ Failed to connect to database. Please check your database configuration.")
        st.info("Ensure PostgreSQL is running and the magnus database is accessible.")
        return

    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Task List", "➕ Create Task", "📊 Analytics", "⚙️ System Status"])

    # ========================================================================
    # TAB 1: TASK LIST
    # ========================================================================
    with tab1:
        st.subheader("📋 Development Tasks")

        # Filters
        col_f1, col_f2, col_f3, col_f4 = st.columns(4)

        with col_f1:
            status_filter = st.multiselect(
                "Status",
                ["pending", "in_progress", "completed", "failed", "blocked", "cancelled"],
                default=["pending", "in_progress", "blocked"],
                key="status_filter"
            )

        with col_f2:
            priority_filter = st.multiselect(
                "Priority",
                ["low", "medium", "high", "critical"],
                default=["critical", "high", "medium"],
                key="priority_filter"
            )

        with col_f3:
            # Get unique feature areas from database
            feature_areas = task_manager.get_feature_areas()
            feature_filter = st.selectbox(
                "Feature Area",
                ["All"] + feature_areas,
                key="feature_filter"
            )

        with col_f4:
            agent_filter = st.selectbox(
                "Agent",
                ["All", "database-optimizer", "backend-architect", "frontend-developer",
                 "qa-agent", "devops-engineer", "full-stack-developer"],
                key="agent_filter"
            )

        # Fetch tasks with filters
        filters = {
            'status': status_filter if status_filter else None,
            'priority': priority_filter if priority_filter else None,
            'feature_area': feature_filter if feature_filter != "All" else None,
            'assigned_agent': agent_filter if agent_filter != "All" else None
        }

        tasks = task_manager.fetch_tasks(**filters)

        if not tasks:
            st.info("No tasks found matching the current filters.")
        else:
            st.success(f"Found {len(tasks)} task(s)")

            # Display tasks as expandable cards
            for task in tasks:
                render_task_card(task, task_manager)

        # Refresh button
        if st.button("🔄 Refresh Task List", key="refresh_tasks"):
            st.rerun()

    # ========================================================================
    # TAB 2: CREATE TASK
    # ========================================================================
    with tab2:
        st.subheader("➕ Create New Development Task")

        with st.form("create_task_form"):
            # Task details
            col1, col2 = st.columns(2)

            with col1:
                task_title = st.text_input(
                    "Task Title *",
                    placeholder="e.g., Fix dashboard loading performance",
                    key="task_title"
                )

                task_type = st.selectbox(
                    "Task Type *",
                    ["feature", "bug_fix", "enhancement", "qa", "refactor", "documentation", "investigation"],
                    key="task_type"
                )

                priority = st.selectbox(
                    "Priority *",
                    ["low", "medium", "high", "critical"],
                    index=1,
                    key="task_priority"
                )

            with col2:
                assigned_agent = st.selectbox(
                    "Assign to Agent *",
                    ["database-optimizer", "backend-architect", "frontend-developer",
                     "qa-agent", "devops-engineer", "full-stack-developer"],
                    key="task_agent"
                )

                feature_area = st.text_input(
                    "Feature Area *",
                    placeholder="e.g., comprehensive_strategy, dashboard, xtrades",
                    key="task_feature"
                )

                estimated_duration = st.number_input(
                    "Estimated Duration (minutes)",
                    min_value=5,
                    max_value=480,
                    value=60,
                    step=15,
                    key="task_duration"
                )

            # Description
            task_description = st.text_area(
                "Task Description *",
                placeholder="Detailed description of what needs to be done...",
                height=150,
                key="task_description"
            )

            # Tags
            tags_input = st.text_input(
                "Tags (comma-separated)",
                placeholder="urgent, frontend, api, bug",
                key="task_tags"
            )

            # Dependencies
            st.markdown("**Dependencies (optional)**")
            st.caption("Enter task IDs that must be completed before this task can start")
            dependencies_input = st.text_input(
                "Dependency Task IDs",
                placeholder="e.g., 1,3,5",
                key="task_dependencies"
            )

            # Submit button
            submit_button = st.form_submit_button("✅ Create Task", type="primary")

            if submit_button:
                # Validate inputs
                if not task_title or not task_description or not feature_area:
                    st.error("❌ Please fill in all required fields (marked with *)")
                else:
                    # Parse tags
                    tags = [tag.strip() for tag in tags_input.split(',') if tag.strip()] if tags_input else None

                    # Parse dependencies
                    dependencies = None
                    if dependencies_input:
                        try:
                            dependencies = [int(dep.strip()) for dep in dependencies_input.split(',') if dep.strip()]
                        except ValueError:
                            st.error("❌ Invalid dependency format. Please enter comma-separated task IDs (numbers only)")
                            dependencies = None

                    # Create task
                    task_id = task_manager.create_task(
                        title=task_title,
                        description=task_description,
                        task_type=task_type,
                        priority=priority,
                        assigned_agent=assigned_agent,
                        feature_area=feature_area,
                        estimated_duration_minutes=estimated_duration,
                        tags=tags,
                        dependencies=dependencies
                    )

                    if task_id:
                        st.success(f"✅ Task created successfully! Task ID: {task_id}")
                        st.info("The autonomous agent will pick up this task based on priority and dependencies.")

                        # Log task creation
                        task_manager.log_execution(
                            task_id=task_id,
                            agent_name="user",
                            action_type="started",
                            message=f"Task created by user via Enhancement Manager UI"
                        )
                    else:
                        st.error("❌ Failed to create task. Please check database connection.")

    # ========================================================================
    # TAB 3: ANALYTICS
    # ========================================================================
    with tab3:
        st.subheader("📊 Task Analytics & Insights")

        # Overall metrics
        st.markdown("### 📈 Overall Metrics")
        col1, col2, col3, col4 = st.columns(4)

        metrics = task_manager.get_overall_metrics()

        with col1:
            st.metric("Total Tasks", metrics.get('total_tasks', 0))
        with col2:
            st.metric("Completed", metrics.get('completed_tasks', 0))
        with col3:
            st.metric("In Progress", metrics.get('in_progress_tasks', 0))
        with col4:
            st.metric("Pending", metrics.get('pending_tasks', 0))

        st.markdown("---")

        # Charts
        col_chart1, col_chart2 = st.columns(2)

        with col_chart1:
            st.markdown("#### 📊 Tasks by Status")
            status_dist = task_manager.get_status_distribution()
            if status_dist and len(status_dist) > 0:
                df_status = pd.DataFrame(list(status_dist.items()), columns=['Status', 'Count'])
                if len(df_status) > 0 and not df_status.empty:
                    # Use plotly to avoid Vega-Lite warnings
                    import plotly.express as px
                    fig = px.bar(df_status, x='Status', y='Count')
                    fig.update_layout(showlegend=False, height=300)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No task data available")
            else:
                st.info("No task data available")

        with col_chart2:
            st.markdown("#### 🎯 Tasks by Priority")
            priority_dist = task_manager.get_priority_distribution()
            if priority_dist and len(priority_dist) > 0:
                df_priority = pd.DataFrame(list(priority_dist.items()), columns=['Priority', 'Count'])
                if len(df_priority) > 0 and not df_priority.empty:
                    # Use plotly to avoid Vega-Lite warnings
                    import plotly.express as px
                    fig = px.bar(df_priority, x='Priority', y='Count')
                    fig.update_layout(showlegend=False, height=300)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No task data available")
            else:
                st.info("No task data available")

        st.markdown("---")

        # Feature area progress
        st.markdown("### 🏗️ Feature Area Progress")
        feature_progress = task_manager.get_feature_progress()

        if feature_progress:
            df_features = pd.DataFrame(feature_progress)

            st.dataframe(
                df_features,
                hide_index=True,
                width='stretch',
                column_config={
                    "feature_area": st.column_config.TextColumn("Feature Area", width="medium"),
                    "total_tasks": st.column_config.NumberColumn("Total Tasks"),
                    "completed_tasks": st.column_config.NumberColumn("Completed"),
                    "in_progress_tasks": st.column_config.NumberColumn("In Progress"),
                    "pending_tasks": st.column_config.NumberColumn("Pending"),
                    "blocked_tasks": st.column_config.NumberColumn("Blocked"),
                    "completion_percentage": st.column_config.ProgressColumn(
                        "Completion %",
                        format="%.1f%%",
                        min_value=0,
                        max_value=100
                    )
                }
            )
        else:
            st.info("No feature area data available")

        st.markdown("---")

        # Agent workload
        st.markdown("### 🤖 Agent Workload Distribution")
        agent_workload = task_manager.get_agent_workload()

        if agent_workload:
            df_agents = pd.DataFrame(agent_workload)

            st.dataframe(
                df_agents,
                hide_index=True,
                width='stretch',
                column_config={
                    "assigned_agent": st.column_config.TextColumn("Agent", width="medium"),
                    "total_assigned_tasks": st.column_config.NumberColumn("Total Assigned"),
                    "active_tasks": st.column_config.NumberColumn("Active"),
                    "pending_tasks": st.column_config.NumberColumn("Pending"),
                    "completed_tasks": st.column_config.NumberColumn("Completed"),
                    "avg_completion_time_minutes": st.column_config.NumberColumn(
                        "Avg Time (min)",
                        format="%.1f"
                    )
                }
            )
        else:
            st.info("No agent workload data available")

    # ========================================================================
    # TAB 4: SYSTEM STATUS
    # ========================================================================
    with tab4:
        st.subheader("⚙️ System Status & Configuration")

        # Database status
        st.markdown("### 💾 Database Status")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Connection", "✅ Connected" if task_manager.is_connected() else "❌ Disconnected")

        with col2:
            table_count = task_manager.get_table_count()
            st.metric("Tables", table_count)

        with col3:
            last_activity = task_manager.get_last_activity_time()
            if last_activity:
                # Handle timezone-aware datetime
                if last_activity.tzinfo is not None:
                    last_activity = last_activity.replace(tzinfo=None)

                time_ago = datetime.now() - last_activity
                if time_ago.total_seconds() < 60:
                    st.metric("Last Activity", "Just now")
                elif time_ago.total_seconds() < 3600:
                    st.metric("Last Activity", f"{int(time_ago.total_seconds() / 60)} min ago")
                else:
                    st.metric("Last Activity", f"{int(time_ago.total_seconds() / 3600)} hours ago")
            else:
                st.metric("Last Activity", "N/A")

        st.markdown("---")

        # System configuration
        st.markdown("### 🔧 Configuration")

        with st.expander("📄 Available Agents"):
            agents = [
                "**database-optimizer**: Optimizes database queries, schemas, and indexes",
                "**backend-architect**: Designs and implements backend services and APIs",
                "**frontend-developer**: Builds UI components and user experiences",
                "**qa-agent**: Tests features and verifies quality",
                "**devops-engineer**: Manages deployment, CI/CD, and infrastructure",
                "**full-stack-developer**: End-to-end feature development"
            ]
            for agent in agents:
                st.markdown(f"- {agent}")

        with st.expander("📋 Task Workflow States"):
            st.markdown("""
            - **pending**: Task is waiting to be started (checking dependencies)
            - **in_progress**: Agent is actively working on the task
            - **completed**: Task finished successfully
            - **failed**: Task encountered errors and could not complete
            - **blocked**: Task is blocked by dependencies or external factors
            - **cancelled**: Task was manually cancelled
            """)

        with st.expander("🎯 Priority Levels"):
            st.markdown("""
            - **critical**: Must be done immediately (P0)
            - **high**: Important and urgent (P1)
            - **medium**: Normal priority (P2)
            - **low**: Nice to have (P3)
            """)

        st.markdown("---")

        # Maintenance actions
        st.markdown("### 🛠️ Maintenance Actions")

        col_maint1, col_maint2, col_maint3 = st.columns(3)

        with col_maint1:
            if st.button("🗑️ Clean Old Logs", help="Remove execution logs older than 30 days"):
                deleted = task_manager.clean_old_logs(days=30)
                if deleted >= 0:
                    st.success(f"✅ Cleaned {deleted} old log entries")
                else:
                    st.error("❌ Failed to clean logs")

        with col_maint2:
            if st.button("📊 Refresh Analytics", help="Rebuild analytics views"):
                if task_manager.refresh_analytics_views():
                    st.success("✅ Analytics refreshed successfully")
                else:
                    st.error("❌ Failed to refresh analytics")

        with col_maint3:
            if st.button("🔍 Verify Schema", help="Check database schema integrity"):
                schema_ok = task_manager.verify_schema()
                if schema_ok:
                    st.success("✅ Schema verified - all tables present")
                else:
                    st.error("❌ Schema verification failed - missing tables")

    # Disconnect from database
    task_manager.disconnect()


def render_task_card(task: Dict, task_manager: TaskManager):
    """Render an individual task as an expandable card"""

    # Priority emoji
    priority_emoji = {
        'critical': '🔴',
        'high': '🟠',
        'medium': '🟡',
        'low': '🟢'
    }

    # Status emoji
    status_emoji = {
        'pending': '⏳',
        'in_progress': '🔄',
        'completed': '✅',
        'failed': '❌',
        'blocked': '🚫',
        'cancelled': '🗑️'
    }

    task_id = task['id']
    priority = task.get('priority', 'medium')
    status = task.get('status', 'pending')
    title = task.get('title', 'Untitled Task')

    # Card header
    with st.expander(
        f"{priority_emoji.get(priority, '⚪')} {status_emoji.get(status, '⚪')} "
        f"**[#{task_id}]** {title} | {status.upper()}"
    ):
        # Task details
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown(f"**Description:**")
            st.markdown(task.get('description', 'No description provided'))

            st.markdown(f"**Feature Area:** `{task.get('feature_area', 'N/A')}`")
            st.markdown(f"**Task Type:** `{task.get('task_type', 'N/A')}`")

            # Tags
            if task.get('tags'):
                tags_html = " ".join([f"<span style='background-color: #e0e0e0; padding: 2px 8px; border-radius: 3px; margin-right: 5px;'>{tag}</span>" for tag in task['tags']])
                st.markdown(f"**Tags:** {tags_html}", unsafe_allow_html=True)

        with col2:
            st.markdown(f"**Assigned Agent:**")
            st.code(task.get('assigned_agent', 'Unassigned'))

            st.markdown(f"**Priority:** {priority.upper()}")
            st.markdown(f"**Status:** {status.upper()}")

            # Timing info
            created_at = task.get('created_at')
            if created_at:
                st.caption(f"Created: {created_at.strftime('%Y-%m-%d %H:%M')}")

            started_at = task.get('started_at')
            if started_at:
                st.caption(f"Started: {started_at.strftime('%Y-%m-%d %H:%M')}")

            completed_at = task.get('completed_at')
            if completed_at:
                st.caption(f"Completed: {completed_at.strftime('%Y-%m-%d %H:%M')}")

        st.markdown("---")

        # Action buttons
        col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)

        with col_btn1:
            if st.button("▶️ Execute", key=f"exec_{task_id}", disabled=(status == 'in_progress' or status == 'completed')):
                execute_task_autonomously(task, task_manager)

        with col_btn2:
            if st.button("📝 Update Status", key=f"update_{task_id}"):
                st.session_state[f'show_update_form_{task_id}'] = True

        with col_btn3:
            if st.button("📋 View Logs", key=f"logs_{task_id}"):
                st.session_state[f'show_logs_{task_id}'] = True

        with col_btn4:
            if status == 'completed':
                if st.button("✅ Verify", key=f"verify_{task_id}"):
                    st.session_state[f'show_verification_{task_id}'] = True

        # Show update form if requested
        if st.session_state.get(f'show_update_form_{task_id}', False):
            st.markdown("#### Update Task Status")
            new_status = st.selectbox(
                "New Status",
                ["pending", "in_progress", "completed", "failed", "blocked", "cancelled"],
                key=f"new_status_{task_id}"
            )

            update_message = st.text_area(
                "Update Message",
                placeholder="Describe what changed...",
                key=f"update_msg_{task_id}"
            )

            if st.button("💾 Save Update", key=f"save_update_{task_id}"):
                if task_manager.update_task_status(task_id, new_status, update_message):
                    st.success(f"✅ Task status updated to: {new_status}")
                    st.session_state[f'show_update_form_{task_id}'] = False
                    st.rerun()
                else:
                    st.error("❌ Failed to update task status")

        # Show execution logs if requested
        if st.session_state.get(f'show_logs_{task_id}', False):
            st.markdown("#### 📋 Execution Log")
            logs = task_manager.fetch_task_logs(task_id)

            if logs:
                for log in logs:
                    timestamp = log['execution_timestamp'].strftime('%Y-%m-%d %H:%M:%S')
                    action_type = log['action_type']
                    message = log['message']
                    agent = log.get('agent_name', 'unknown')

                    st.caption(f"**[{timestamp}]** `{action_type}` by `{agent}`: {message}")
            else:
                st.info("No execution logs yet")

            if st.button("❌ Close Logs", key=f"close_logs_{task_id}"):
                st.session_state[f'show_logs_{task_id}'] = False
                st.rerun()

        # Show verification form if requested
        if st.session_state.get(f'show_verification_{task_id}', False):
            st.markdown("#### ✅ Task Verification")

            # Check if already verified
            verification = task_manager.fetch_task_verification(task_id)

            if verification:
                st.info(f"**Verification Status:** {'✅ Passed' if verification['passed'] else '❌ Failed'}")
                st.markdown(f"**Notes:** {verification.get('verification_notes', 'N/A')}")

                # User feedback
                st.markdown("#### 👤 User Feedback")
                user_feedback = st.radio(
                    "Confirm task completion:",
                    ["approved", "work_again", "needs_changes", "rejected"],
                    key=f"feedback_{task_id}"
                )

                user_comments = st.text_area(
                    "Comments (optional)",
                    placeholder="Provide additional feedback...",
                    key=f"comments_{task_id}"
                )

                if st.button("💾 Submit Feedback", key=f"submit_feedback_{task_id}"):
                    if task_manager.save_user_feedback(task_id, user_feedback, user_comments):
                        st.success("✅ Feedback saved successfully!")
                        st.session_state[f'show_verification_{task_id}'] = False
                        st.rerun()
                    else:
                        st.error("❌ Failed to save feedback")
            else:
                st.warning("⚠️ This task has not been verified yet by QA agent")

            if st.button("❌ Close Verification", key=f"close_verify_{task_id}"):
                st.session_state[f'show_verification_{task_id}'] = False
                st.rerun()


def execute_task_autonomously(task: Dict, task_manager: TaskManager):
    """Execute a task using the appropriate autonomous agent"""
    task_id = task['id']
    assigned_agent = task.get('assigned_agent', 'unknown')

    st.info(f"🚀 Launching {assigned_agent} to execute task #{task_id}...")

    # Update task status to in_progress
    if task_manager.update_task_status(task_id, 'in_progress', f"Task execution started via UI"):
        # Log execution start
        task_manager.log_execution(
            task_id=task_id,
            agent_name=assigned_agent,
            action_type="started",
            message=f"Task execution initiated by user from Enhancement Manager UI"
        )

        st.success("✅ Task marked as in_progress. The autonomous agent will process this task.")
        st.info("💡 Refresh the page to see execution progress and logs.")

        # In a real implementation, you would trigger the actual agent here
        # For example: trigger_agent_execution(task_id, assigned_agent)
    else:
        st.error("❌ Failed to update task status")


# Entry point
if __name__ == "__main__":
    render_enhancement_manager_page()
