"""
Dashboard Generator for Local Orchestrator
Generates HTML dashboards from collected metrics
100% Local - no cloud services
"""
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


def generate_dashboard(metrics: Dict[str, Any], trends: Dict[str, Any] = None,
                       output_file: str = None) -> str:
    """
    Generate comprehensive HTML dashboard from metrics

    Args:
        metrics: Metrics summary from MetricsCollector
        trends: Performance trends (optional)
        output_file: Output path (auto-generated if None)

    Returns:
        Path to generated dashboard
    """
    if output_file is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f".claude/orchestrator/dashboards/dashboard_{timestamp}.html"

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    overall = metrics.get("overall", {})
    by_agent = metrics.get("by_agent", [])
    recent_errors = metrics.get("recent_errors", [])
    period_hours = metrics.get("period_hours", 24)

    # Generate HTML
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Orchestrator Dashboard - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: #0f172a;
            color: #e2e8f0;
            padding: 20px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        header {{
            margin-bottom: 30px;
        }}

        h1 {{
            color: #f1f5f9;
            font-size: 2rem;
            margin-bottom: 10px;
        }}

        .subtitle {{
            color: #94a3b8;
            font-size: 0.9rem;
        }}

        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .card {{
            background: #1e293b;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            border: 1px solid #334155;
        }}

        .card-header {{
            display: flex;
            align-items: center;
            margin-bottom: 16px;
        }}

        .icon {{
            width: 40px;
            height: 40px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 12px;
            font-size: 1.5rem;
        }}

        .icon.success {{ background: #10b981; }}
        .icon.performance {{ background: #3b82f6; }}
        .icon.tokens {{ background: #8b5cf6; }}
        .icon.agents {{ background: #f59e0b; }}
        .icon.error {{ background: #ef4444; }}

        .card-title {{
            color: #94a3b8;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .metric-value {{
            font-size: 2.5rem;
            font-weight: 700;
            color: #f1f5f9;
            margin: 12px 0;
        }}

        .metric-value.success {{ color: #10b981; }}
        .metric-value.warning {{ color: #f59e0b; }}
        .metric-value.error {{ color: #ef4444; }}

        .metric-label {{
            color: #64748b;
            font-size: 0.85rem;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            background: #1e293b;
            border-radius: 12px;
            overflow: hidden;
        }}

        th {{
            background: #334155;
            color: #f1f5f9;
            padding: 16px;
            text-align: left;
            font-weight: 600;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        td {{
            padding: 14px 16px;
            border-top: 1px solid #334155;
            color: #cbd5e1;
        }}

        tr:hover {{
            background: #2d3748;
        }}

        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
        }}

        .badge.success {{
            background: rgba(16, 185, 129, 0.2);
            color: #10b981;
        }}

        .badge.warning {{
            background: rgba(245, 158, 11, 0.2);
            color: #f59e0b;
        }}

        .badge.error {{
            background: rgba(239, 68, 68, 0.2);
            color: #ef4444;
        }}

        .progress-bar {{
            height: 8px;
            background: #334155;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 8px;
        }}

        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #10b981, #3b82f6);
            transition: width 0.3s ease;
        }}

        .error-list {{
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid rgba(239, 68, 68, 0.3);
            border-radius: 8px;
            padding: 16px;
            margin-top: 20px;
        }}

        .error-item {{
            padding: 12px;
            border-left: 3px solid #ef4444;
            background: rgba(239, 68, 68, 0.1);
            margin-bottom: 8px;
            border-radius: 4px;
        }}

        .error-time {{
            color: #94a3b8;
            font-size: 0.75rem;
            margin-bottom: 4px;
        }}

        .error-agent {{
            color: #f59e0b;
            font-weight: 600;
            margin-bottom: 4px;
        }}

        .error-message {{
            color: #cbd5e1;
            font-size: 0.9rem;
        }}

        .refresh-notice {{
            text-align: center;
            color: #64748b;
            font-size: 0.85rem;
            margin-top: 40px;
            padding: 20px;
            background: #1e293b;
            border-radius: 8px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Orchestrator Performance Dashboard</h1>
            <p class="subtitle">
                Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} |
                Period: Last {period_hours} hours |
                100% Local, Zero Cloud Costs
            </p>
        </header>

        <div class="grid">
            <div class="card">
                <div class="card-header">
                    <div class="icon success">✓</div>
                    <div class="card-title">Success Rate</div>
                </div>
                <div class="metric-value {'success' if overall.get('success_rate', 0) >= 95 else 'warning' if overall.get('success_rate', 0) >= 80 else 'error'}">
                    {overall.get('success_rate', 0):.1f}%
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {overall.get('success_rate', 0)}%"></div>
                </div>
                <div class="metric-label">
                    {overall.get('successful', 0)} / {overall.get('total_executions', 0)} executions
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <div class="icon performance">⚡</div>
                    <div class="card-title">Average Latency</div>
                </div>
                <div class="metric-value">{overall.get('avg_duration_ms', 0):.0f}ms</div>
                <div class="metric-label">Per agent execution</div>
            </div>

            <div class="card">
                <div class="card-header">
                    <div class="icon tokens">🔢</div>
                    <div class="card-title">Total Tokens</div>
                </div>
                <div class="metric-value">{overall.get('total_tokens', 0):,}</div>
                <div class="metric-label">Across all agents</div>
            </div>

            <div class="card">
                <div class="card-header">
                    <div class="icon agents">🤖</div>
                    <div class="card-title">Agents Used</div>
                </div>
                <div class="metric-value">{overall.get('unique_agents', 0)}</div>
                <div class="metric-label">Unique agents activated</div>
            </div>
        </div>

        <div class="card" style="margin-bottom: 20px;">
            <h2 style="margin-bottom: 20px; color: #f1f5f9;">Agent Performance Breakdown</h2>
            <table>
                <thead>
                    <tr>
                        <th>Agent</th>
                        <th>Executions</th>
                        <th>Success Rate</th>
                        <th>Avg Latency</th>
                        <th>Tokens Used</th>
                    </tr>
                </thead>
                <tbody>
"""

    # Add agent rows
    for agent in by_agent:
        success_rate = agent.get('success_rate', 0)
        badge_class = 'success' if success_rate >= 95 else 'warning' if success_rate >= 80 else 'error'

        html += f"""
                    <tr>
                        <td style="font-weight: 600;">{agent.get('agent_name', 'Unknown')}</td>
                        <td>{agent.get('executions', 0)}</td>
                        <td>
                            <span class="badge {badge_class}">{success_rate:.1f}%</span>
                        </td>
                        <td>{agent.get('avg_duration_ms', 0):.0f}ms</td>
                        <td>{agent.get('total_tokens', 0):,}</td>
                    </tr>
"""

    html += """
                </tbody>
            </table>
        </div>
"""

    # Add errors section if there are any
    if recent_errors:
        html += """
        <div class="card">
            <h2 style="margin-bottom: 20px; color: #f1f5f9;">Recent Errors</h2>
            <div class="error-list">
"""
        for error in recent_errors[:10]:  # Show last 10 errors
            html += f"""
                <div class="error-item">
                    <div class="error-time">{error.get('timestamp', 'Unknown')}</div>
                    <div class="error-agent">Agent: {error.get('agent', 'Unknown')}</div>
                    <div class="error-message">{error.get('error', 'No details')}</div>
                </div>
"""
        html += """
            </div>
        </div>
"""

    # Add trends if provided
    if trends and trends.get('trends'):
        html += """
        <div class="card" style="margin-top: 20px;">
            <h2 style="margin-bottom: 20px; color: #f1f5f9;">Performance Trends (Last 7 Days)</h2>
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Executions</th>
                        <th>Avg Latency</th>
                        <th>Success Rate</th>
                    </tr>
                </thead>
                <tbody>
"""
        for trend in trends['trends']:
            html += f"""
                    <tr>
                        <td>{trend.get('day', 'Unknown')}</td>
                        <td>{trend.get('executions', 0)}</td>
                        <td>{trend.get('avg_duration_ms', 0):.0f}ms</td>
                        <td>
                            <span class="badge {'success' if trend.get('success_rate', 0) >= 95 else 'warning'}">
                                {trend.get('success_rate', 0):.1f}%
                            </span>
                        </td>
                    </tr>
"""
        html += """
                </tbody>
            </table>
        </div>
"""

    html += f"""
        <div class="refresh-notice">
            <p>This is a static snapshot. For real-time metrics, regenerate the dashboard or use the Prometheus endpoint.</p>
            <p style="margin-top: 8px; color: #475569;">
                Database: .claude/orchestrator/databases/metrics.db |
                Traces: .claude/orchestrator/databases/traces.db
            </p>
        </div>
    </div>

    <script>
        // Auto-refresh every 60 seconds (optional)
        // setTimeout(() => location.reload(), 60000);
    </script>
</body>
</html>
"""

    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    logger.info(f"Dashboard generated: {output_path}")
    return str(output_path)


def generate_dashboard_from_db(hours: int = 24, days: int = 7) -> str:
    """
    Generate dashboard directly from database

    Args:
        hours: Hours of data for summary
        days: Days of data for trends

    Returns:
        Path to generated dashboard
    """
    from .metrics_collector import get_metrics_collector

    collector = get_metrics_collector()
    metrics = collector.get_summary(hours=hours)
    trends = collector.get_performance_trends(days=days)

    return generate_dashboard(metrics, trends)


if __name__ == "__main__":
    # Test dashboard generation
    print("Generating test dashboard...")
    dashboard_path = generate_dashboard_from_db()
    print(f"\nDashboard generated at: {dashboard_path}")
    print(f"Open in browser: file:///{dashboard_path}")
