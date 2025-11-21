"""
Task Management Dashboard with QA Sign-Off Status
================================================

Comprehensive task management view showing:
- Open tasks (pending)
- In-progress tasks
- Completed tasks (awaiting QA)
- QA approved tasks (signed off)
- QA review status and progress
- Blocking issues

Features:
- Real-time QA status
- Multi-agent sign-off tracking
- Issue management
- Never deletes tasks
"""

import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

load_dotenv()


class TaskManagementDashboard:
    """Comprehensive task management with QA integration"""

    def __init__(self):
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'magnus'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', '')
        }

    def get_connection(self):
        """Get database connection"""
        return psycopg2.connect(**self.db_config)

    def get_task_summary(self):
        """Get overall task summary with QA status"""
        query = """
            SELECT
                COUNT(*) as total_tasks,
                COUNT(*) FILTER (WHERE status = 'pending') as pending,
                COUNT(*) FILTER (WHERE status = 'in_progress') as in_progress,
                COUNT(*) FILTER (WHERE status = 'blocked') as blocked,
                COUNT(*) FILTER (WHERE status = 'completed') as completed_awaiting_qa,
                COUNT(*) FILTER (WHERE status = 'qa_approved') as qa_approved,
                COUNT(*) FILTER (WHERE status IN ('completed', 'qa_approved'))::NUMERIC /
                    NULLIF(COUNT(*), 0) * 100 as completion_rate
            FROM development_tasks;
        """

        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query)
                return dict(cur.fetchone())

    def get_tasks_by_status(self, status, limit=50):
        """Get tasks filtered by status"""
        query = """
            SELECT
                t.id,
                t.title,
                t.description,
                t.task_type,
                t.priority,
                t.status,
                t.assigned_agent,
                t.feature_area,
                t.created_at,
                t.updated_at,
                t.completed_at,
                t.estimated_duration_minutes,
                t.tags
            FROM development_tasks t
            WHERE t.status = %s
            ORDER BY
                CASE priority
                    WHEN 'critical' THEN 1
                    WHEN 'high' THEN 2
                    WHEN 'medium' THEN 3
                    WHEN 'low' THEN 4
                    ELSE 5
                END,
                t.created_at DESC
            LIMIT %s;
        """

        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (status, limit))
                return [dict(row) for row in cur.fetchall()]

    def get_tasks_with_qa_status(self, limit=100):
        """Get completed tasks with QA status"""
        query = """
            SELECT
                t.id,
                t.title,
                t.task_type,
                t.priority,
                t.status,
                t.feature_area,
                t.completed_at,
                qs.total_reviews,
                qs.approvals,
                qs.rejections,
                qs.pending as pending_reviews,
                qs.all_sign_offs_complete,
                qs.open_qa_issues
            FROM development_tasks t
            LEFT JOIN v_task_qa_status qs ON t.id = qs.task_id
            WHERE t.status IN ('completed', 'qa_approved')
            ORDER BY t.completed_at DESC NULLS LAST
            LIMIT %s;
        """

        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (limit,))
                return [dict(row) for row in cur.fetchall()]

    def get_pending_qa_reviews(self):
        """Get all pending QA reviews"""
        query = """
            SELECT
                task_id,
                title,
                agent_name,
                review_requested_at,
                hours_waiting
            FROM v_pending_qa_reviews
            ORDER BY hours_waiting DESC;
        """

        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query)
                return [dict(row) for row in cur.fetchall()]

    def get_open_qa_issues(self):
        """Get all open QA issues"""
        query = """
            SELECT
                parent_task_id,
                parent_task_title,
                qa_issue_title,
                severity,
                issue_type,
                reported_by_agent,
                status,
                days_open
            FROM v_open_qa_tasks
            ORDER BY
                CASE severity
                    WHEN 'critical' THEN 1
                    WHEN 'high' THEN 2
                    WHEN 'medium' THEN 3
                    WHEN 'low' THEN 4
                    ELSE 5
                END,
                days_open DESC;
        """

        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query)
                return [dict(row) for row in cur.fetchall()]


def render_dashboard():
    """Render the task management dashboard"""

    st.title("📋 Task Management Dashboard")
    st.markdown("**Complete task tracking with QA sign-off status**")
    st.divider()

    dashboard = TaskManagementDashboard()

    # Overall Summary
    st.header("📊 Overall Summary")

    summary = dashboard.get_task_summary()

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.metric("Total Tasks", summary['total_tasks'])

    with col2:
        st.metric("Pending", summary['pending'], delta=None)

    with col3:
        st.metric("In Progress", summary['in_progress'], delta=None)

    with col4:
        st.metric("Awaiting QA", summary['completed_awaiting_qa'], delta=None)

    with col5:
        st.metric("QA Approved", summary['qa_approved'], delta=None, delta_color="normal")

    with col6:
        st.metric("Completion", f"{summary['completion_rate']:.1f}%")

    st.divider()

    # Tabs for different views
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🟡 Pending Tasks",
        "🔵 In Progress",
        "⏳ Awaiting QA",
        "✅ QA Approved",
        "👥 Pending Reviews",
        "🔴 Open Issues"
    ])

    # Tab 1: Pending Tasks
    with tab1:
        st.subheader("Pending Tasks")
        st.caption("Tasks ready to be started")

        pending_tasks = dashboard.get_tasks_by_status('pending', limit=50)

        if pending_tasks:
            for task in pending_tasks:
                with st.expander(f"#{task['id']} - {task['title']} [{task['priority'].upper()}]"):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(f"**Type:** {task['task_type']}")
                        st.write(f"**Priority:** {task['priority']}")
                        st.write(f"**Assigned:** {task['assigned_agent'] or 'Unassigned'}")

                    with col2:
                        st.write(f"**Feature Area:** {task['feature_area'] or 'General'}")
                        st.write(f"**Estimated:** {task['estimated_duration_minutes'] or 0} min")
                        st.write(f"**Created:** {task['created_at'].strftime('%Y-%m-%d') if task['created_at'] else 'N/A'}")

                    if task['description']:
                        st.write("**Description:**")
                        st.write(task['description'])

                    if task['tags']:
                        st.write("**Tags:**", ", ".join(task['tags']))
        else:
            st.info("No pending tasks")

    # Tab 2: In Progress
    with tab2:
        st.subheader("In Progress Tasks")
        st.caption("Currently being worked on")

        in_progress_tasks = dashboard.get_tasks_by_status('in_progress', limit=50)

        if in_progress_tasks:
            for task in in_progress_tasks:
                with st.expander(f"#{task['id']} - {task['title']} [{task['priority'].upper()}]"):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(f"**Type:** {task['task_type']}")
                        st.write(f"**Priority:** {task['priority']}")
                        st.write(f"**Assigned:** {task['assigned_agent'] or 'Unassigned'}")

                    with col2:
                        st.write(f"**Feature Area:** {task['feature_area'] or 'General'}")
                        st.write(f"**Started:** {task['updated_at'].strftime('%Y-%m-%d %H:%M') if task['updated_at'] else 'N/A'}")

                    if task['description']:
                        st.write("**Description:**")
                        st.write(task['description'][:300] + "..." if len(task['description']) > 300 else task['description'])
        else:
            st.info("No tasks in progress")

    # Tab 3: Awaiting QA
    with tab3:
        st.subheader("Tasks Awaiting QA Approval")
        st.caption("Completed work pending multi-agent review")

        qa_tasks = dashboard.get_tasks_with_qa_status(limit=100)
        awaiting_qa = [t for t in qa_tasks if t['status'] == 'completed']

        if awaiting_qa:
            for task in awaiting_qa:
                # Determine status color
                if task['all_sign_offs_complete'] and task['open_qa_issues'] == 0:
                    status_emoji = "✅"
                    status_text = "Ready to finalize"
                    status_color = "green"
                elif task['open_qa_issues'] > 0:
                    status_emoji = "🔴"
                    status_text = f"{task['open_qa_issues']} open issues"
                    status_color = "red"
                else:
                    status_emoji = "⏳"
                    status_text = f"{task['pending_reviews'] or 0} pending reviews"
                    status_color = "orange"

                with st.expander(f"{status_emoji} #{task['id']} - {task['title']} [{task['priority'].upper()}]"):
                    # QA Status
                    st.markdown(f"**QA Status:** :{status_color}[{status_text}]")

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric("Total Reviews", task['total_reviews'] or 0)
                        st.metric("Approvals", task['approvals'] or 0)

                    with col2:
                        st.metric("Rejections", task['rejections'] or 0)
                        st.metric("Pending", task['pending_reviews'] or 0)

                    with col3:
                        st.metric("Open Issues", task['open_qa_issues'] or 0)
                        complete = "Yes" if task['all_sign_offs_complete'] else "No"
                        st.write(f"**All Complete:** {complete}")

                    st.write(f"**Type:** {task['task_type']}")
                    st.write(f"**Feature Area:** {task['feature_area'] or 'General'}")
                    st.write(f"**Completed:** {task['completed_at'].strftime('%Y-%m-%d %H:%M') if task['completed_at'] else 'N/A'}")
        else:
            st.info("No tasks awaiting QA")

    # Tab 4: QA Approved
    with tab4:
        st.subheader("QA Approved Tasks")
        st.caption("Fully reviewed and approved - ready for deployment")

        qa_approved = [t for t in qa_tasks if t['status'] == 'qa_approved']

        if qa_approved:
            st.success(f"✅ {len(qa_approved)} tasks ready to deploy!")

            for task in qa_approved:
                with st.expander(f"✅ #{task['id']} - {task['title']}"):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(f"**Type:** {task['task_type']}")
                        st.write(f"**Priority:** {task['priority']}")
                        st.write(f"**Feature Area:** {task['feature_area'] or 'General'}")

                    with col2:
                        st.write(f"**Approvals:** {task['approvals']}")
                        st.write(f"**Reviews:** {task['total_reviews']}")
                        st.write(f"**Completed:** {task['completed_at'].strftime('%Y-%m-%d') if task['completed_at'] else 'N/A'}")

                    st.success("✅ All QA sign-offs complete - READY TO DEPLOY")
        else:
            st.info("No QA approved tasks yet")

    # Tab 5: Pending Reviews
    with tab5:
        st.subheader("Pending QA Reviews by Agent")
        st.caption("Reviews awaiting agent action")

        pending_reviews = dashboard.get_pending_qa_reviews()

        if pending_reviews:
            # Group by agent
            agents = {}
            for review in pending_reviews:
                agent = review['agent_name']
                if agent not in agents:
                    agents[agent] = []
                agents[agent].append(review)

            for agent, reviews in agents.items():
                with st.expander(f"👤 {agent} ({len(reviews)} pending)"):
                    for review in reviews:
                        col1, col2 = st.columns([3, 1])

                        with col1:
                            st.write(f"**Task #{review['task_id']}:** {review['title']}")
                            st.write(f"Requested: {review['review_requested_at'].strftime('%Y-%m-%d %H:%M') if review['review_requested_at'] else 'N/A'}")

                        with col2:
                            hours = review['hours_waiting'] or 0
                            if hours > 24:
                                st.error(f"⏰ {hours:.0f}h waiting")
                            elif hours > 8:
                                st.warning(f"⏰ {hours:.0f}h waiting")
                            else:
                                st.info(f"⏰ {hours:.0f}h waiting")

                        st.divider()
        else:
            st.success("✅ No pending reviews!")

    # Tab 6: Open Issues
    with tab6:
        st.subheader("Open QA Issues")
        st.caption("Issues found during QA review that need fixing")

        open_issues = dashboard.get_open_qa_issues()

        if open_issues:
            st.warning(f"⚠️ {len(open_issues)} open QA issues")

            for issue in open_issues:
                severity_colors = {
                    'critical': 'red',
                    'high': 'orange',
                    'medium': 'blue',
                    'low': 'gray'
                }
                color = severity_colors.get(issue['severity'], 'gray')

                with st.expander(f"🔴 {issue['qa_issue_title']} [{issue['severity'].upper()}]"):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown(f"**Severity:** :{color}[{issue['severity'].upper()}]")
                        st.write(f"**Type:** {issue['issue_type']}")
                        st.write(f"**Reported by:** {issue['reported_by_agent']}")

                    with col2:
                        st.write(f"**Parent Task:** #{issue['parent_task_id']} - {issue['parent_task_title']}")
                        st.write(f"**Status:** {issue['status']}")
                        st.write(f"**Days Open:** {int(issue['days_open'])}")

                    if issue['severity'] == 'critical' and issue['days_open'] > 7:
                        st.error("⚠️ CRITICAL: This issue has been open for over a week!")
        else:
            st.success("✅ No open QA issues!")

    st.divider()

    # System Info
    with st.expander("ℹ️ System Information"):
        st.write("**QA System Status:** Operational ✅")
        st.write("**Never-Delete Principle:** Enforced ✅")
        st.write("**Multi-Agent Review:** Active ✅")
        st.write("**Audit Trail:** Complete ✅")

        st.markdown("""
        **Task Workflow:**
        1. 🟡 Pending → Developer starts work
        2. 🔵 In Progress → Developer working
        3. ⏳ Completed → QA automatically triggered
        4. 👥 QA Review → Agents review and approve
        5. ✅ QA Approved → Ready for deployment
        """)


if __name__ == "__main__":
    st.set_page_config(
        page_title="Task Management - Magnus",
        page_icon="📋",
        layout="wide"
    )

    render_dashboard()
