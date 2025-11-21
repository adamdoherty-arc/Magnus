"""
Odds Data Quality Dashboard

Real-time monitoring and visualization of odds validation system
Shows data quality metrics, active alerts, and validation trends
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.odds_validator import OddsValidator
from src.odds_alert_system import OddsAlertSystem, AlertChannel
import psycopg2
import psycopg2.extras


# Page configuration
st.set_page_config(
    page_title="Odds Data Quality Dashboard",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': '5432',
    'database': 'magnus',
    'user': 'postgres',
    'password': os.getenv('DB_PASSWORD')
}


@st.cache_data(ttl=60)
def get_db_connection():
    """Get cached database connection"""
    return psycopg2.connect(**DB_CONFIG)


@st.cache_data(ttl=300)
def get_quality_summary(hours: int = 24):
    """Get validation summary statistics"""
    validator = OddsValidator(DB_CONFIG)
    return validator.get_validation_summary(hours=hours)


@st.cache_data(ttl=60)
def get_active_alerts(severity: str = None):
    """Get active alerts"""
    alert_system = OddsAlertSystem(DB_CONFIG)
    return alert_system.get_active_alerts(severity=severity, limit=100)


@st.cache_data(ttl=300)
def get_quality_trends(days: int = 7):
    """Get quality trends over time"""
    conn = None
    cur = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute("""
            SELECT * FROM v_odds_quality_trends
            WHERE metric_date >= CURRENT_DATE - INTERVAL '%s days'
            ORDER BY metric_date ASC
        """, (days,))

        results = cur.fetchall()
        return [dict(row) for row in results] if results else []

    except Exception as e:
        st.error(f"Error fetching quality trends: {e}")
        return []
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@st.cache_data(ttl=300)
def get_validation_by_rule():
    """Get validation statistics by rule type"""
    conn = None
    cur = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute("SELECT * FROM v_odds_validation_by_rule")
        results = cur.fetchall()
        return [dict(row) for row in results] if results else []

    except Exception as e:
        st.error(f"Error fetching validation by rule: {e}")
        return []
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@st.cache_data(ttl=60)
def get_recent_critical_failures(limit: int = 20):
    """Get recent critical validation failures"""
    conn = None
    cur = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute("""
            SELECT * FROM v_odds_critical_failures
            LIMIT %s
        """, (limit,))

        results = cur.fetchall()
        return [dict(row) for row in results] if results else []

    except Exception as e:
        st.error(f"Error fetching critical failures: {e}")
        return []
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def render_quality_overview():
    """Render data quality overview section"""
    st.header("📊 Data Quality Overview")

    # Time period selector
    time_period = st.selectbox(
        "Time Period",
        options=[24, 48, 168],  # 24h, 48h, 7 days
        format_func=lambda x: f"Last {x} hours" if x < 168 else "Last 7 days",
        index=0
    )

    # Get summary data
    summary = get_quality_summary(hours=time_period)

    if not summary or summary.get('total_checks', 0) == 0:
        st.info("No validation data available for the selected time period.")
        return

    # Calculate metrics
    total_checks = summary.get('total_checks', 0)
    failures_by_severity = summary.get('failures_by_severity', {})
    critical_failures = failures_by_severity.get('critical', 0)
    warning_failures = failures_by_severity.get('warning', 0)

    # Calculate quality score
    total_failures = critical_failures + warning_failures
    quality_score = ((total_checks - total_failures) / total_checks * 100) if total_checks > 0 else 0

    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Quality Score",
            f"{quality_score:.1f}%",
            delta=None,
            help="Percentage of validations that passed (100% = perfect)"
        )

    with col2:
        st.metric(
            "Total Validations",
            f"{total_checks:,}",
            help=f"Total validation checks performed in last {time_period} hours"
        )

    with col3:
        delta_color = "inverse" if critical_failures > 0 else "normal"
        st.metric(
            "🚨 Critical Failures",
            f"{critical_failures}",
            delta=f"-{critical_failures}" if critical_failures > 0 else None,
            delta_color=delta_color,
            help="Blocking issues that prevent odds from being displayed"
        )

    with col4:
        st.metric(
            "⚠️ Warnings",
            f"{warning_failures}",
            help="Suspicious data requiring review"
        )

    # Failure breakdown by rule type
    st.subheader("Failures by Rule Type")

    failures_by_rule = summary.get('failures_by_rule', {})
    if failures_by_rule:
        # Create DataFrame
        df_failures = pd.DataFrame([
            {'Rule Type': k.replace('_', ' ').title(), 'Failures': v}
            for k, v in failures_by_rule.items()
        ]).sort_values('Failures', ascending=True)

        # Horizontal bar chart
        fig = px.bar(
            df_failures,
            x='Failures',
            y='Rule Type',
            orientation='h',
            title=f"Validation Failures by Rule Type (Last {time_period}h)",
            color='Failures',
            color_continuous_scale='Reds'
        )
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.success("✅ No validation failures detected!")


def render_active_alerts():
    """Render active alerts section"""
    st.header("🚨 Active Alerts")

    # Severity filter
    col1, col2 = st.columns([3, 1])
    with col1:
        severity_filter = st.selectbox(
            "Filter by Severity",
            options=[None, "critical", "warning", "info"],
            format_func=lambda x: "All Severities" if x is None else x.title(),
            index=0
        )
    with col2:
        auto_refresh = st.checkbox("Auto-refresh", value=True)

    # Get active alerts
    alerts = get_active_alerts(severity=severity_filter)

    if not alerts:
        st.success("✅ No active alerts! All odds data is clean.")
        return

    # Display alert count
    st.write(f"**{len(alerts)} active alert(s)**")

    # Display alerts
    for alert in alerts:
        alert_id = alert.get('id')
        ticker = alert.get('ticker')
        alert_type = alert.get('alert_type', '').replace('_', ' ').title()
        severity = alert.get('severity', 'info')
        title = alert.get('title')
        description = alert.get('description')
        away_team = alert.get('away_team')
        home_team = alert.get('home_team')
        away_price = alert.get('away_win_price')
        home_price = alert.get('home_win_price')
        created_at = alert.get('created_at')

        # Alert color based on severity
        if severity == 'critical':
            border_color = '#cc0000'
            emoji = '🚨'
        elif severity == 'warning':
            border_color = '#ff9900'
            emoji = '⚠️'
        else:
            border_color = '#0066cc'
            emoji = 'ℹ️'

        # Render alert card
        with st.expander(f"{emoji} Alert #{alert_id}: {title}", expanded=(severity == 'critical')):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.markdown(f"""
                    <div style="border-left: 4px solid {border_color}; padding-left: 12px;">
                        <p><strong>Ticker:</strong> {ticker}</p>
                        <p><strong>Type:</strong> {alert_type}</p>
                        <p><strong>Severity:</strong> <span style="color: {border_color}; font-weight: bold;">{severity.upper()}</span></p>
                        <p><strong>Created:</strong> {created_at}</p>
                    </div>
                """, unsafe_allow_html=True)

                st.write("**Description:**")
                st.write(description)

            with col2:
                if away_team and home_team:
                    st.write("**Game Details:**")
                    st.write(f"Away: {away_team}")
                    st.write(f"Odds: {away_price:.1%}" if away_price else "")
                    st.write(f"Home: {home_team}")
                    st.write(f"Odds: {home_price:.1%}" if home_price else "")

            # Action buttons
            col_ack, col_resolve, col_false = st.columns(3)

            with col_ack:
                if st.button(f"✅ Acknowledge", key=f"ack_{alert_id}"):
                    alert_system = OddsAlertSystem(DB_CONFIG)
                    if alert_system.acknowledge_alert(alert_id, "dashboard_user"):
                        st.success(f"Alert #{alert_id} acknowledged")
                        st.rerun()

            with col_resolve:
                if st.button(f"✔️ Resolve", key=f"resolve_{alert_id}"):
                    alert_system = OddsAlertSystem(DB_CONFIG)
                    if alert_system.resolve_alert(alert_id, "Resolved from dashboard"):
                        st.success(f"Alert #{alert_id} resolved")
                        st.rerun()

            with col_false:
                if st.button(f"❌ False Positive", key=f"false_{alert_id}"):
                    # Mark as false positive
                    conn = psycopg2.connect(**DB_CONFIG)
                    cur = conn.cursor()
                    cur.execute("""
                        UPDATE odds_anomaly_alerts
                        SET status = 'false_positive', updated_at = NOW()
                        WHERE id = %s
                    """, (alert_id,))
                    conn.commit()
                    cur.close()
                    conn.close()
                    st.success(f"Alert #{alert_id} marked as false positive")
                    st.rerun()


def render_quality_trends():
    """Render quality trends over time"""
    st.header("📈 Quality Trends")

    # Get trend data
    trends = get_quality_trends(days=7)

    if not trends or len(trends) == 0:
        st.info("No trend data available. Data quality tracking will populate over time.")
        return

    # Convert to DataFrame
    df_trends = pd.DataFrame(trends)
    df_trends['metric_date'] = pd.to_datetime(df_trends['metric_date'])

    # Quality score trend
    fig_quality = go.Figure()

    fig_quality.add_trace(go.Scatter(
        x=df_trends['metric_date'],
        y=df_trends['quality_score'],
        mode='lines+markers',
        name='Quality Score',
        line=dict(color='#00cc66', width=3),
        marker=dict(size=8),
        fill='tozeroy',
        fillcolor='rgba(0, 204, 102, 0.1)'
    ))

    fig_quality.update_layout(
        title="Quality Score Trend (Last 7 Days)",
        xaxis_title="Date",
        yaxis_title="Quality Score (%)",
        yaxis=dict(range=[0, 100]),
        height=400,
        hovermode='x unified'
    )

    st.plotly_chart(fig_quality, use_container_width=True)

    # Failure trends
    fig_failures = go.Figure()

    fig_failures.add_trace(go.Bar(
        x=df_trends['metric_date'],
        y=df_trends['critical_failures'],
        name='Critical',
        marker_color='#cc0000'
    ))

    fig_failures.add_trace(go.Bar(
        x=df_trends['metric_date'],
        y=df_trends['warning_failures'],
        name='Warnings',
        marker_color='#ff9900'
    ))

    fig_failures.update_layout(
        title="Validation Failures by Severity (Last 7 Days)",
        xaxis_title="Date",
        yaxis_title="Number of Failures",
        barmode='stack',
        height=400,
        hovermode='x unified'
    )

    st.plotly_chart(fig_failures, use_container_width=True)


def render_validation_by_rule():
    """Render validation statistics by rule type"""
    st.header("🔍 Validation by Rule Type")

    validation_stats = get_validation_by_rule()

    if not validation_stats:
        st.info("No validation statistics available.")
        return

    # Convert to DataFrame
    df_validation = pd.DataFrame(validation_stats)
    df_validation['rule_type'] = df_validation['rule_type'].str.replace('_', ' ').str.title()

    # Display as table with color coding
    st.dataframe(
        df_validation[['rule_type', 'total_checks', 'passed', 'failed', 'pass_rate']],
        column_config={
            'rule_type': st.column_config.TextColumn('Rule Type', width='large'),
            'total_checks': st.column_config.NumberColumn('Total Checks', format='%d'),
            'passed': st.column_config.NumberColumn('Passed', format='%d'),
            'failed': st.column_config.NumberColumn('Failed', format='%d'),
            'pass_rate': st.column_config.ProgressColumn('Pass Rate', format='%.1f%%', min_value=0, max_value=100)
        },
        hide_index=True,
        use_container_width=True
    )


def render_recent_critical_failures():
    """Render recent critical failures"""
    st.header("⚠️ Recent Critical Failures")

    failures = get_recent_critical_failures(limit=10)

    if not failures:
        st.success("✅ No critical failures detected!")
        return

    for failure in failures:
        ticker = failure.get('ticker')
        rule_type = failure.get('rule_type', '').replace('_', ' ').title()
        message = failure.get('message')
        checked_at = failure.get('checked_at')

        with st.expander(f"{ticker} - {rule_type} ({checked_at})", expanded=False):
            st.write(message)
            if failure.get('details'):
                st.json(failure['details'])


def main():
    """Main dashboard function"""

    # Title
    st.title("🎯 Odds Data Quality Dashboard")
    st.markdown("Real-time monitoring of betting odds validation and data quality")

    # Sidebar
    with st.sidebar:
        st.header("Dashboard Settings")

        # Refresh button
        if st.button("🔄 Refresh Data", type="primary"):
            st.cache_data.clear()
            st.rerun()

        st.divider()

        # Database status
        st.subheader("System Status")
        try:
            conn = psycopg2.connect(**DB_CONFIG)
            conn.close()
            st.success("✅ Database Connected")
        except Exception as e:
            st.error(f"❌ Database Error: {str(e)[:50]}...")

        st.divider()

        # Information
        st.subheader("About")
        st.info("""
        This dashboard monitors the quality of betting odds data in real-time.

        **Features:**
        - Real-time validation monitoring
        - Automated anomaly detection
        - Alert management
        - Quality trends and analytics
        """)

    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Overview",
        "🚨 Active Alerts",
        "📈 Trends",
        "🔍 By Rule Type",
        "⚠️ Critical Failures"
    ])

    with tab1:
        render_quality_overview()

    with tab2:
        render_active_alerts()

    with tab3:
        render_quality_trends()

    with tab4:
        render_validation_by_rule()

    with tab5:
        render_recent_critical_failures()

    # Footer
    st.divider()
    st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Odds Data Quality Monitoring System")


if __name__ == "__main__":
    main()
