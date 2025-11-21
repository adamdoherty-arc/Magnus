"""
Financial Assistant Task Dashboard
View and manage all tasks for the 6-month implementation roadmap

Features:
- Phase-by-phase progress view
- Task dependency visualization
- Next available tasks
- Legion-compatible task interface
- Never deletes tasks, only marks complete
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


class FinancialAssistantTaskDashboard:
    """Dashboard for Financial Assistant implementation tasks"""

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

    def get_phase_summary(self):
        """Get summary statistics by phase"""
        query = """
            SELECT
                CASE
                    WHEN tags @> ARRAY['phase-1'] THEN 'Phase 1: Foundation'
                    WHEN tags @> ARRAY['phase-2'] THEN 'Phase 2: Intelligence'
                    WHEN tags @> ARRAY['phase-3'] THEN 'Phase 3: Autonomy'
                    WHEN tags @> ARRAY['phase-4'] THEN 'Phase 4: Production'
                    ELSE 'Other'
                END as phase,
                COUNT(*) as total_tasks,
                COUNT(*) FILTER (WHERE status = 'completed') as completed,
                COUNT(*) FILTER (WHERE status = 'in_progress') as in_progress,
                COUNT(*) FILTER (WHERE status = 'pending') as pending,
                COUNT(*) FILTER (WHERE status = 'blocked') as blocked,
                ROUND(COUNT(*) FILTER (WHERE status = 'completed')::NUMERIC / NULLIF(COUNT(*), 0) * 100, 1) as completion_pct,
                SUM(estimated_duration_minutes) FILTER (WHERE status = 'completed') as completed_minutes,
                SUM(estimated_duration_minutes) as total_minutes
            FROM development_tasks
            WHERE feature_area = 'financial_assistant'
            AND tags IS NOT NULL
            GROUP BY phase
            ORDER BY
                CASE phase
                    WHEN 'Phase 1: Foundation' THEN 1
                    WHEN 'Phase 2: Intelligence' THEN 2
                    WHEN 'Phase 3: Autonomy' THEN 3
                    WHEN 'Phase 4: Production' THEN 4
                    ELSE 5
                END;
        """

        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query)
                return cur.fetchall()

    def get_next_tasks(self, limit=20):
        """Get next available tasks (dependencies met)"""
        query = """
            SELECT
                t.id,
                t.title,
                t.description,
                t.task_type,
                t.priority,
                t.assigned_agent,
                t.estimated_duration_minutes,
                t.tags,
                CASE
                    WHEN t.tags @> ARRAY['phase-1'] THEN 'Phase 1'
                    WHEN t.tags @> ARRAY['phase-2'] THEN 'Phase 2'
                    WHEN t.tags @> ARRAY['phase-3'] THEN 'Phase 3'
                    WHEN t.tags @> ARRAY['phase-4'] THEN 'Phase 4'
                    ELSE 'Unknown'
                END as phase,
                check_task_dependencies(t.id) as dependencies_met
            FROM development_tasks t
            WHERE t.status = 'pending'
            AND t.feature_area = 'financial_assistant'
            AND check_task_dependencies(t.id) = true
            ORDER BY
                CASE t.priority
                    WHEN 'critical' THEN 1
                    WHEN 'high' THEN 2
                    WHEN 'medium' THEN 3
                    WHEN 'low' THEN 4
                END,
                t.created_at ASC
            LIMIT %s;
        """

        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (limit,))
                return cur.fetchall()

    def get_in_progress_tasks(self):
        """Get currently in-progress tasks"""
        query = """
            SELECT
                t.id,
                t.title,
                t.assigned_agent,
                t.started_at,
                t.estimated_duration_minutes,
                EXTRACT(EPOCH FROM (NOW() - t.started_at)) / 60 as minutes_elapsed,
                t.tags
            FROM development_tasks t
            WHERE t.status = 'in_progress'
            AND t.feature_area = 'financial_assistant'
            ORDER BY t.started_at ASC;
        """

        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query)
                return cur.fetchall()

    def get_blocked_tasks(self):
        """Get blocked tasks"""
        query = """
            SELECT
                t.id,
                t.title,
                t.assigned_agent,
                t.blocked_reason,
                t.dependencies,
                t.tags
            FROM development_tasks t
            WHERE t.status = 'blocked'
            AND t.feature_area = 'financial_assistant'
            ORDER BY t.priority DESC, t.created_at ASC;
        """

        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query)
                return cur.fetchall()

    def get_recent_completions(self, limit=10):
        """Get recently completed tasks"""
        query = """
            SELECT
                t.id,
                t.title,
                t.completed_at,
                t.actual_duration_minutes,
                t.estimated_duration_minutes,
                t.assigned_agent,
                t.tags
            FROM development_tasks t
            WHERE t.status = 'completed'
            AND t.feature_area = 'financial_assistant'
            ORDER BY t.completed_at DESC
            LIMIT %s;
        """

        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (limit,))
                return cur.fetchall()

    def mark_task_complete(self, task_id):
        """Mark a task as complete"""
        query = """
            UPDATE development_tasks
            SET status = 'completed',
                completed_at = NOW(),
                updated_at = NOW()
            WHERE id = %s
            RETURNING id, title;
        """

        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (task_id,))
                conn.commit()
                return cur.fetchone()

    def start_task(self, task_id):
        """Mark a task as in-progress"""
        query = """
            UPDATE development_tasks
            SET status = 'in_progress',
                started_at = NOW(),
                updated_at = NOW()
            WHERE id = %s
            RETURNING id, title;
        """

        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (task_id,))
                conn.commit()
                return cur.fetchone()


def main():
    """Main dashboard application"""
    st.set_page_config(
        page_title="Financial Assistant - Task Dashboard",
        page_icon="📋",
        layout="wide"
    )

    st.title("📋 Financial Assistant - 6-Month Implementation Roadmap")
    st.caption("Complete task tracking for autonomous AI financial advisor")

    dashboard = FinancialAssistantTaskDashboard()

    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview",
        "🎯 Next Tasks",
        "⚡ In Progress",
        "🚫 Blocked",
        "✅ Recent Completions"
    ])

    # ===== Tab 1: Overview =====
    with tab1:
        st.header("Project Overview")

        # Phase summary
        phase_data = dashboard.get_phase_summary()

        if phase_data:
            # Create metrics row
            cols = st.columns(4)

            for i, phase in enumerate(phase_data):
                with cols[i]:
                    st.metric(
                        label=phase['phase'],
                        value=f"{phase['completion_pct']:.1f}%",
                        delta=f"{phase['completed']}/{phase['total_tasks']} tasks"
                    )

            st.markdown("---")

            # Detailed phase breakdown
            st.subheader("Phase Breakdown")

            for phase in phase_data:
                with st.expander(f"{phase['phase']} - {phase['completion_pct']:.1f}% Complete", expanded=True):
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric("Total Tasks", phase['total_tasks'])
                        st.metric("Completed", phase['completed'], delta=None, delta_color="normal")

                    with col2:
                        st.metric("In Progress", phase['in_progress'])
                        st.metric("Pending", phase['pending'])

                    with col3:
                        st.metric("Blocked", phase['blocked'], delta=None, delta_color="inverse")
                        hours = (phase['completed_minutes'] or 0) / 60
                        total_hours = (phase['total_minutes'] or 0) / 60
                        st.metric("Hours Complete", f"{hours:.1f}h / {total_hours:.1f}h")

                    # Progress bar
                    st.progress(phase['completion_pct'] / 100)

            # Overall timeline visualization
            st.markdown("---")
            st.subheader("Timeline View")

            # Create DataFrame for visualization
            df = pd.DataFrame(phase_data)

            # Stacked bar chart
            fig = go.Figure(data=[
                go.Bar(name='Completed', x=df['phase'], y=df['completed'], marker_color='green'),
                go.Bar(name='In Progress', x=df['phase'], y=df['in_progress'], marker_color='yellow'),
                go.Bar(name='Pending', x=df['phase'], y=df['pending'], marker_color='gray'),
                go.Bar(name='Blocked', x=df['phase'], y=df['blocked'], marker_color='red')
            ])

            fig.update_layout(
                barmode='stack',
                title='Task Status by Phase',
                xaxis_title='Phase',
                yaxis_title='Number of Tasks',
                height=400
            )

            st.plotly_chart(fig, use_container_width=True)

        else:
            st.info("No tasks found. Run populate_financial_assistant_tasks.py to create tasks.")

    # ===== Tab 2: Next Tasks =====
    with tab2:
        st.header("🎯 Next Available Tasks")
        st.caption("Tasks ready to start (dependencies met)")

        next_tasks = dashboard.get_next_tasks(limit=20)

        if next_tasks:
            for task in next_tasks:
                priority_color = {
                    'critical': '🔴',
                    'high': '🟠',
                    'medium': '🟡',
                    'low': '🟢'
                }.get(task['priority'], '⚪')

                with st.expander(f"{priority_color} [{task['phase']}] {task['title']}", expanded=False):
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.markdown(f"**Description:**\n{task['description'][:300]}...")

                        st.markdown(f"""
                        **Details:**
                        - **Type:** {task['task_type']}
                        - **Priority:** {task['priority']}
                        - **Agent:** {task['assigned_agent']}
                        - **Est. Time:** {task['estimated_duration_minutes']} minutes ({task['estimated_duration_minutes']/60:.1f} hours)
                        - **Tags:** {', '.join(task['tags'] if task['tags'] else [])}
                        """)

                    with col2:
                        st.markdown("**Actions:**")

                        if st.button("▶️ Start Task", key=f"start_{task['id']}"):
                            result = dashboard.start_task(task['id'])
                            if result:
                                st.success(f"Started: {result['title']}")
                                st.rerun()

                        if st.button("✅ Mark Complete", key=f"complete_{task['id']}"):
                            result = dashboard.mark_task_complete(task['id'])
                            if result:
                                st.success(f"Completed: {result['title']}")
                                st.rerun()

                        st.markdown(f"**ID:** `{task['id']}`")

        else:
            st.info("No tasks available with met dependencies. Check for blocked tasks.")

    # ===== Tab 3: In Progress =====
    with tab3:
        st.header("⚡ Tasks In Progress")

        in_progress = dashboard.get_in_progress_tasks()

        if in_progress:
            for task in in_progress:
                progress_pct = (task['minutes_elapsed'] / task['estimated_duration_minutes'] * 100) if task['estimated_duration_minutes'] > 0 else 0

                with st.expander(f"🔄 {task['title']}", expanded=True):
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.markdown(f"""
                        **Agent:** {task['assigned_agent']}
                        **Started:** {task['started_at'].strftime('%Y-%m-%d %H:%M:%S')}
                        **Elapsed:** {task['minutes_elapsed']:.0f} minutes
                        **Estimated:** {task['estimated_duration_minutes']} minutes
                        """)

                        # Progress bar
                        st.progress(min(progress_pct / 100, 1.0))

                    with col2:
                        if st.button("✅ Complete", key=f"complete_inprog_{task['id']}"):
                            result = dashboard.mark_task_complete(task['id'])
                            if result:
                                st.success(f"Completed: {result['title']}")
                                st.rerun()

                        st.markdown(f"**ID:** `{task['id']}`")

        else:
            st.info("No tasks currently in progress.")

    # ===== Tab 4: Blocked =====
    with tab4:
        st.header("🚫 Blocked Tasks")

        blocked = dashboard.get_blocked_tasks()

        if blocked:
            for task in blocked:
                with st.expander(f"🚫 {task['title']}", expanded=False):
                    st.markdown(f"""
                    **Agent:** {task['assigned_agent']}
                    **Reason:** {task['blocked_reason'] or 'Not specified'}
                    **Dependencies:** {task['dependencies'] if task['dependencies'] else 'None'}
                    **ID:** `{task['id']}`
                    """)

        else:
            st.success("No blocked tasks!")

    # ===== Tab 5: Recent Completions =====
    with tab5:
        st.header("✅ Recently Completed Tasks")

        completions = dashboard.get_recent_completions(limit=20)

        if completions:
            for task in completions:
                accuracy_delta = None
                if task['actual_duration_minutes'] and task['estimated_duration_minutes']:
                    accuracy_delta = task['actual_duration_minutes'] - task['estimated_duration_minutes']

                with st.expander(f"✅ {task['title']}", expanded=False):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown(f"""
                        **Agent:** {task['assigned_agent']}
                        **Completed:** {task['completed_at'].strftime('%Y-%m-%d %H:%M:%S')}
                        """)

                    with col2:
                        st.markdown(f"""
                        **Estimated:** {task['estimated_duration_minutes']} min
                        **Actual:** {task['actual_duration_minutes'] or 'N/A'} min
                        **Tags:** {', '.join(task['tags'] if task['tags'] else [])}
                        """)

                    if accuracy_delta is not None:
                        if accuracy_delta > 0:
                            st.warning(f"⚠️ Took {accuracy_delta} minutes longer than estimated")
                        else:
                            st.success(f"✅ Completed {abs(accuracy_delta)} minutes faster than estimated")

        else:
            st.info("No completed tasks yet.")

    # Sidebar
    with st.sidebar:
        st.header("⚙️ System Info")

        # Connection test
        try:
            with dashboard.get_connection() as conn:
                st.success("✅ Database Connected")

                # Get total stats
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT
                            COUNT(*) as total,
                            COUNT(*) FILTER (WHERE status = 'completed') as completed,
                            COUNT(*) FILTER (WHERE status = 'in_progress') as in_progress,
                            COUNT(*) FILTER (WHERE status = 'pending') as pending
                        FROM development_tasks
                        WHERE feature_area = 'financial_assistant';
                    """)
                    stats = cur.fetchone()

                    st.metric("Total Tasks", stats[0])
                    st.metric("Completed", stats[1])
                    st.metric("In Progress", stats[2])
                    st.metric("Pending", stats[3])

                    if stats[0] > 0:
                        completion = (stats[1] / stats[0]) * 100
                        st.progress(completion / 100)
                        st.caption(f"Overall: {completion:.1f}% Complete")

        except Exception as e:
            st.error(f"❌ Database Error: {e}")

        st.markdown("---")

        st.markdown("""
        **Quick Actions:**
        - View tasks by phase
        - Start available tasks
        - Mark tasks complete
        - Monitor progress

        **Features:**
        - ✅ Tasks never deleted
        - ✅ Dependency tracking
        - ✅ Legion compatible
        - ✅ Real-time updates
        """)

        if st.button("🔄 Refresh Dashboard"):
            st.rerun()


if __name__ == "__main__":
    main()
