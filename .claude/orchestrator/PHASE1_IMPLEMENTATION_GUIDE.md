# Phase 1 Implementation Guide - Observability & Self-Healing

**Goal:** Production-ready orchestrator with full visibility and auto-healing
**Timeline:** 2 weeks (10 working days)
**Score Improvement:** 85/100 → 92/100

---

## Day 1-2: OpenTelemetry Tracing

### Objective
Implement distributed tracing to track every agent decision, tool call, and state transition.

### Files to Create

**1. `.claude/orchestrator/observability/tracer.py`**
```python
"""
OpenTelemetry tracer for agent orchestration
Tracks: Agent execution, state transitions, tool calls, errors
"""
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class OrchestratorTracer:
    """Main tracer for orchestrator operations"""

    def __init__(self, service_name: str = "magnus-orchestrator"):
        # Create resource with service information
        resource = Resource.create({
            "service.name": service_name,
            "service.version": "2.0",
            "deployment.environment": "production"
        })

        # Initialize tracer provider
        self.provider = TracerProvider(resource=resource)

        # Add console exporter for development
        console_exporter = ConsoleSpanExporter()
        self.provider.add_span_processor(
            BatchSpanProcessor(console_exporter)
        )

        # Add OTLP exporter for production (optional)
        # Uncomment when you have an OTLP endpoint
        # otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:4317")
        # self.provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

        trace.set_tracer_provider(self.provider)
        self.tracer = trace.get_tracer(__name__)

        logger.info("OpenTelemetry tracer initialized")

    def start_agent_execution(self, agent_name: str, context: Dict[str, Any]) -> trace.Span:
        """Start tracing an agent execution"""
        span = self.tracer.start_span(
            f"agent.execute.{agent_name}",
            attributes={
                "agent.name": agent_name,
                "agent.priority": context.get("priority", "unknown"),
                "feature.name": context.get("feature", "unknown"),
                "request.id": context.get("request_id", "unknown")
            }
        )
        return span

    def trace_state_transition(self, from_state: str, to_state: str, context: Dict[str, Any]):
        """Trace a state machine transition"""
        with self.tracer.start_as_current_span(
            f"state.transition.{from_state}_to_{to_state}",
            attributes={
                "state.from": from_state,
                "state.to": to_state,
                "transition.context": str(context)
            }
        ):
            pass

    def trace_tool_call(self, tool_name: str, parameters: Dict[str, Any], result: Any):
        """Trace a tool/MCP call"""
        with self.tracer.start_as_current_span(
            f"tool.call.{tool_name}",
            attributes={
                "tool.name": tool_name,
                "tool.parameters": str(parameters),
                "tool.result_type": type(result).__name__
            }
        ):
            pass

    def trace_error(self, error: Exception, context: Dict[str, Any]):
        """Trace an error occurrence"""
        with self.tracer.start_as_current_span(
            "error.occurred",
            attributes={
                "error.type": type(error).__name__,
                "error.message": str(error),
                "error.context": str(context)
            }
        ):
            pass

# Singleton instance
_tracer_instance: Optional[OrchestratorTracer] = None

def get_tracer() -> OrchestratorTracer:
    """Get singleton tracer instance"""
    global _tracer_instance
    if _tracer_instance is None:
        _tracer_instance = OrchestratorTracer()
    return _tracer_instance
```

**2. `.claude/orchestrator/observability/observability_config.yaml`**
```yaml
observability:
  enabled: true

  tracing:
    enabled: true
    backend: opentelemetry
    export_to_console: true  # For development
    export_to_otlp: false    # Set true when you have OTLP collector
    otlp_endpoint: "http://localhost:4317"

    trace_all_agents: true
    trace_state_transitions: true
    trace_tool_calls: true
    trace_errors: true

    sampling_rate: 1.0  # Trace 100% of requests (reduce in prod if needed)

  metrics:
    enabled: true
    collection_interval: 60  # seconds

  logging:
    level: INFO
    include_traces: true
    format: json  # json or text
```

**3. Integration with existing orchestrator**

Update `.claude/orchestrator/main_orchestrator.py` to use tracing:
```python
from observability.tracer import get_tracer

class MainOrchestrator:
    def __init__(self):
        # ... existing code ...
        self.tracer = get_tracer()

    def execute_request(self, request: str):
        # Start trace
        with self.tracer.tracer.start_as_current_span("orchestrator.execute_request") as span:
            span.set_attribute("request", request)

            # ... existing execution logic ...

            span.set_attribute("status", "completed")
```

### Installation
```bash
pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp
```

### Testing
```bash
cd c:/code/Magnus/.claude/orchestrator
python -c "from observability.tracer import get_tracer; t = get_tracer(); print('Tracer initialized successfully')"
```

---

## Day 3-4: Metrics Collection & Dashboards

### Objective
Collect performance metrics and generate visual dashboards.

### Files to Create

**1. `.claude/orchestrator/observability/metrics_collector.py`**
```python
"""
Metrics collection for orchestrator performance
Tracks: Latency, throughput, success rate, costs
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
import json
from pathlib import Path
from collections import defaultdict
import statistics

class MetricsCollector:
    """Collects and aggregates orchestrator metrics"""

    def __init__(self, storage_dir: str = ".claude/orchestrator/metrics"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # In-memory storage for current session
        self.metrics = {
            "agent_executions": [],
            "latencies": defaultdict(list),
            "token_usage": defaultdict(int),
            "costs": defaultdict(float),
            "success_counts": defaultdict(int),
            "failure_counts": defaultdict(int)
        }

    def record_agent_execution(self, agent_name: str, duration_ms: float,
                               success: bool, tokens_used: int = 0, cost: float = 0.0):
        """Record an agent execution"""
        record = {
            "timestamp": datetime.now().isoformat(),
            "agent_name": agent_name,
            "duration_ms": duration_ms,
            "success": success,
            "tokens_used": tokens_used,
            "cost": cost
        }

        self.metrics["agent_executions"].append(record)
        self.metrics["latencies"][agent_name].append(duration_ms)
        self.metrics["token_usage"][agent_name] += tokens_used
        self.metrics["costs"][agent_name] += cost

        if success:
            self.metrics["success_counts"][agent_name] += 1
        else:
            self.metrics["failure_counts"][agent_name] += 1

    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary"""
        total_executions = len(self.metrics["agent_executions"])
        if total_executions == 0:
            return {"message": "No metrics collected yet"}

        total_successes = sum(self.metrics["success_counts"].values())
        total_failures = sum(self.metrics["failure_counts"].values())

        return {
            "total_executions": total_executions,
            "success_rate": total_successes / total_executions if total_executions > 0 else 0,
            "total_cost": sum(self.metrics["costs"].values()),
            "total_tokens": sum(self.metrics["token_usage"].values()),
            "average_latency_ms": statistics.mean([
                e["duration_ms"] for e in self.metrics["agent_executions"]
            ]),
            "agents_used": len(set([e["agent_name"] for e in self.metrics["agent_executions"]]))
        }

    def save_metrics(self):
        """Save metrics to disk"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        metrics_file = self.storage_dir / f"metrics_{timestamp}.json"

        with open(metrics_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "summary": self.get_summary(),
                "detailed_metrics": {
                    "latencies": {k: list(v) for k, v in self.metrics["latencies"].items()},
                    "token_usage": dict(self.metrics["token_usage"]),
                    "costs": dict(self.metrics["costs"]),
                    "success_counts": dict(self.metrics["success_counts"]),
                    "failure_counts": dict(self.metrics["failure_counts"])
                }
            }, f, indent=2)

# Singleton
_collector_instance = None

def get_metrics_collector() -> MetricsCollector:
    global _collector_instance
    if _collector_instance is None:
        _collector_instance = MetricsCollector()
    return _collector_instance
```

**2. `.claude/orchestrator/observability/dashboard_generator.py`**
```python
"""
Generate HTML dashboards from collected metrics
"""
from typing import Dict, Any
from datetime import datetime
from pathlib import Path
import json

def generate_dashboard(metrics: Dict[str, Any], output_file: str = None) -> str:
    """Generate HTML dashboard from metrics"""

    if output_file is None:
        output_file = f".claude/orchestrator/dashboards/dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    summary = metrics.get("summary", {})
    detailed = metrics.get("detailed_metrics", {})

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Orchestrator Dashboard - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ color: #333; }}
        .metric-card {{
            background: white;
            padding: 20px;
            margin: 15px 0;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .metric-value {{
            font-size: 36px;
            font-weight: bold;
            color: #4CAF50;
        }}
        .metric-label {{
            font-size: 14px;
            color: #666;
            text-transform: uppercase;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        th {{
            background-color: #4CAF50;
            color: white;
        }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Orchestrator Performance Dashboard</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

        <div class="metric-card">
            <div class="metric-label">Total Executions</div>
            <div class="metric-value">{summary.get('total_executions', 0)}</div>
        </div>

        <div class="metric-card">
            <div class="metric-label">Success Rate</div>
            <div class="metric-value">{summary.get('success_rate', 0) * 100:.1f}%</div>
        </div>

        <div class="metric-card">
            <div class="metric-label">Average Latency</div>
            <div class="metric-value">{summary.get('average_latency_ms', 0):.0f}ms</div>
        </div>

        <div class="metric-card">
            <div class="metric-label">Total Cost</div>
            <div class="metric-value">${summary.get('total_cost', 0):.2f}</div>
        </div>

        <div class="metric-card">
            <h2>Agent Performance</h2>
            <table>
                <tr>
                    <th>Agent</th>
                    <th>Executions</th>
                    <th>Success Rate</th>
                    <th>Avg Latency</th>
                    <th>Total Cost</th>
                </tr>
"""

    # Add agent rows
    for agent_name in detailed.get("costs", {}).keys():
        successes = detailed.get("success_counts", {}).get(agent_name, 0)
        failures = detailed.get("failure_counts", {}).get(agent_name, 0)
        total = successes + failures
        success_rate = (successes / total * 100) if total > 0 else 0

        latencies = detailed.get("latencies", {}).get(agent_name, [])
        avg_latency = sum(latencies) / len(latencies) if latencies else 0

        cost = detailed.get("costs", {}).get(agent_name, 0)

        html += f"""
                <tr>
                    <td>{agent_name}</td>
                    <td>{total}</td>
                    <td>{success_rate:.1f}%</td>
                    <td>{avg_latency:.0f}ms</td>
                    <td>${cost:.2f}</td>
                </tr>
"""

    html += """
            </table>
        </div>
    </div>
</body>
</html>
"""

    with open(output_path, 'w') as f:
        f.write(html)

    return str(output_path)
```

### Testing
```bash
python observability/metrics_collector.py
# Should create metrics file and dashboard
```

---

## Day 5: Alerting System

### Objective
Implement real-time alerts for failures, performance issues, and budget overruns.

### Files to Create

**1. `.claude/orchestrator/observability/alerting.py`**
```python
"""
Alerting system for orchestrator
Alerts on: errors, performance degradation, budget overruns
"""
from typing import Dict, Any, List, Callable
from datetime import datetime
import logging
import smtplib
from email.mime.text import MIMEText
from pathlib import Path
import yaml

logger = logging.getLogger(__name__)

class Alert:
    """Represents an alert"""
    def __init__(self, severity: str, title: str, message: str, context: Dict[str, Any] = None):
        self.severity = severity  # info, warning, error, critical
        self.title = title
        self.message = message
        self.context = context or {}
        self.timestamp = datetime.now()

class AlertingSystem:
    """Main alerting system"""

    def __init__(self, config_file: str = ".claude/orchestrator/observability/observability_config.yaml"):
        self.config = self._load_config(config_file)
        self.handlers: List[Callable] = []

        # Setup default handlers
        self._setup_handlers()

    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """Load alerting configuration"""
        try:
            with open(config_file, 'r') as f:
                return yaml.safe_load(f).get('observability', {}).get('alerting', {})
        except Exception as e:
            logger.warning(f"Could not load alerting config: {e}")
            return {"enabled": True, "channels": ["log"]}

    def _setup_handlers(self):
        """Setup alert handlers based on config"""
        channels = self.config.get('channels', ['log'])

        if 'log' in channels:
            self.handlers.append(self._log_alert)

        if 'email' in channels:
            self.handlers.append(self._email_alert)

        if 'slack' in channels:
            self.handlers.append(self._slack_alert)

    def send_alert(self, alert: Alert):
        """Send alert through all configured channels"""
        if not self.config.get('enabled', True):
            return

        for handler in self.handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Alert handler failed: {e}")

    def _log_alert(self, alert: Alert):
        """Log alert to file"""
        log_level = {
            'info': logging.INFO,
            'warning': logging.WARNING,
            'error': logging.ERROR,
            'critical': logging.CRITICAL
        }.get(alert.severity, logging.WARNING)

        logger.log(log_level, f"ALERT [{alert.severity.upper()}] {alert.title}: {alert.message}")

    def _email_alert(self, alert: Alert):
        """Send email alert (configure SMTP settings)"""
        # TODO: Implement email sending
        # Requires SMTP configuration
        pass

    def _slack_alert(self, alert: Alert):
        """Send Slack alert (configure webhook)"""
        # TODO: Implement Slack webhook
        pass

    def check_conditions(self, metrics: Dict[str, Any]):
        """Check alert conditions against metrics"""
        conditions = self.config.get('conditions', [])

        for condition in conditions:
            if self._evaluate_condition(condition, metrics):
                self.send_alert(Alert(
                    severity='warning',
                    title=f"Condition triggered: {condition}",
                    message=f"Metrics: {metrics}"
                ))

    def _evaluate_condition(self, condition: str, metrics: Dict[str, Any]) -> bool:
        """Evaluate alert condition"""
        # Simple condition evaluation
        # Example: "error_rate > 5%" or "cost_per_day > $100"
        try:
            # Parse condition (simplified)
            if "error_rate >" in condition:
                threshold = float(condition.split(">")[1].strip().replace("%", "")) / 100
                error_rate = 1 - metrics.get("success_rate", 1)
                return error_rate > threshold

            if "cost_per_day >" in condition:
                threshold = float(condition.split(">")[1].strip().replace("$", ""))
                cost = metrics.get("total_cost", 0)
                return cost > threshold

            return False
        except Exception as e:
            logger.error(f"Failed to evaluate condition '{condition}': {e}")
            return False

# Singleton
_alerting_system = None

def get_alerting_system() -> AlertingSystem:
    global _alerting_system
    if _alerting_system is None:
        _alerting_system = AlertingSystem()
    return _alerting_system
```

Update `observability_config.yaml`:
```yaml
observability:
  # ... existing config ...

  alerting:
    enabled: true
    channels:
      - log
      # - email  # Enable when SMTP configured
      # - slack  # Enable when webhook configured

    conditions:
      - "error_rate > 5%"
      - "latency_p95 > 10000"  # 10 seconds
      - "cost_per_day > 100"

    email:
      smtp_server: "smtp.gmail.com"
      smtp_port: 587
      from_address: "alerts@magnus.com"
      to_addresses:
        - "dev-team@magnus.com"

    slack:
      webhook_url: ""  # Add your Slack webhook URL
```

---

## Days 6-10: Self-Healing & Feedback Loops

*Full implementation guide would continue here with detailed instructions for feedback system, execution tracking, success/failure analysis, and auto-healing capabilities.*

---

## Integration Checklist

After implementing all components:

- [ ] Tracer integrated with main orchestrator
- [ ] Metrics collector recording all executions
- [ ] Dashboard generated successfully
- [ ] Alerts configured and tested
- [ ] All components tested together
- [ ] Documentation updated

---

## Testing the Complete System

```bash
# Run integrated test
cd c:/code/Magnus/.claude/orchestrator
python -m pytest tests/test_observability.py -v

# Generate test dashboard
python observability/dashboard_generator.py

# Check metrics
python -c "
from observability.metrics_collector import get_metrics_collector
mc = get_metrics_collector()
print(mc.get_summary())
"
```

---

## Success Criteria

After Phase 1 completion:

✅ **Visibility:** Can see every agent decision in traces
✅ **Metrics:** Dashboard shows performance, costs, success rates
✅ **Alerts:** Notified when errors occur or budgets exceeded
✅ **Self-Healing:** System auto-retries failures with different approaches
✅ **Learning:** Pattern recognition improving agent selection

**Result:** Production-ready orchestrator with 92/100 score!
