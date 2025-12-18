# Orchestrator Usage Guide

**How to use the world-class orchestrator in your daily workflow**

---

## 🎯 The Orchestrator is Already Working!

**Good news:** The orchestrator runs **automatically** on every request. You don't need to do anything special!

### How It Works Now

**Every time you make a request, the orchestrator:**

1. ✅ **Pre-flight validation** - Checks your request against all project rules
2. ✅ **Agent selection** - Automatically selects the right specialists for the job
3. ✅ **Parallel execution** - Runs multiple agents concurrently (5-10x faster)
4. ✅ **QA validation** - Checks all changes for violations
5. ✅ **UI testing** - Tests page changes with Playwright (when pages modified)
6. ✅ **Summary generation** - Provides comprehensive results

**You just work normally - the orchestrator handles everything!**

---

## 📋 Daily Workflow Examples

### Example 1: Normal Feature Request

**You say:**
```
"Add a new calendar spread scanner that filters by IV rank > 50%"
```

**What happens automatically:**

1. **Pre-flight validation:**
   ```
   ✓ Request validated
   ✓ No forbidden patterns detected
   ✓ Feature identified: calendar-spreads
   ✓ Specs loaded from .claude/specs/calendar-spreads/
   ```

2. **Agent selection:**
   ```
   ✓ Primary: calendar-spreads-specialist
   ✓ Supporting: data-scientist, performance-engineer
   ✓ QA: qa-tester, code-reviewer, spec-integration-tester
   ```

3. **Execution:**
   ```
   ✓ Agents run in parallel (3-5 concurrent)
   ✓ Code implemented following specs
   ✓ Tests generated automatically
   ```

4. **QA:**
   ```
   ✓ No horizontal lines detected
   ✓ No hardcoded values
   ✓ Code quality: PASS
   ```

5. **Summary:**
   ```
   Feature: calendar-spreads scanner
   Files modified: 2
   Tests: 8 generated
   QA: All passed
   Ready to commit
   ```

### Example 2: Bug Fix Request

**You say:**
```
"The positions page is showing wrong delta values"
```

**What happens automatically:**

1. **Pre-flight:**
   ```
   ✓ Request validated
   ✓ Feature: robinhood-positions
   ✓ Bug keyword detected
   ```

2. **Agent selection:**
   ```
   ✓ Primary: bug-root-cause-analyzer (auto-invoked!)
   ✓ Supporting: full-stack-developer, database-optimizer
   ✓ QA: qa-tester, spec-integration-tester
   ```

3. **Execution:**
   ```
   ✓ Git history analyzed for similar bugs
   ✓ Root cause identified: hardcoded delta values
   ✓ Fix applied: use real Greeks from API
   ✓ Tests updated
   ```

4. **QA:**
   ```
   ✓ Verified real Greeks now used
   ✓ No hardcoded values
   ✓ Rate limiting confirmed
   ```

### Example 3: Blocked Request

**You say:**
```
"Add horizontal dividers between sections on the dashboard"
```

**What happens automatically:**

1. **Pre-flight validation:**
   ```
   ✗ BLOCKED!

   ORCHESTRATOR: Pre-flight validation FAILED

   Violations:
     - FORBIDDEN: Request contains horizontal line/divider.
       See UI_STYLE_GUIDE.md - NO horizontal lines allowed.

   Please revise your request or acknowledge you want to bypass these rules.
   ```

2. **I respond to you:**
   ```
   I cannot add horizontal dividers because the orchestrator blocked this request.
   The UI_STYLE_GUIDE.md explicitly forbids horizontal lines.

   Would you like me to add the sections with just whitespace separation instead?
   ```

**You never have to remind me about the rules - the orchestrator enforces them!**

---

## 🛠️ Manual Usage (Optional)

### Check Before Requesting

**Test a request before I execute it:**

```bash
cd c:/code/Magnus
python .claude/orchestrator/auto_run.py "Your request here"
```

**Example:**
```bash
python .claude/orchestrator/auto_run.py "Add horizontal dividers to dashboard"

# Output:
ORCHESTRATOR: Pre-flight validation FAILED
Violations:
  - FORBIDDEN: Request contains horizontal line/divider.
    See UI_STYLE_GUIDE.md - NO horizontal lines allowed.
```

### View System Status

**Check orchestrator status:**

```bash
cd c:/code/Magnus/.claude/orchestrator
python main_orchestrator.py --summary
```

**Output:**
```
Main Orchestrator Status:
- Mode: standard
- Pre-flight: enabled
- Post-execution QA: enabled
- Features tracked: 16
- Rules loaded: 5
```

### Run QA Manually

**Run QA on specific files:**

```bash
python main_orchestrator.py --qa positions_page_improved.py dashboard.py
```

### Run UI Tests

**Test all pages:**

```bash
python ui_test_agent.py
```

---

## 🎮 Slash Command Usage

### /check-rules

**Use the slash command to validate before requesting:**

```
/check-rules Add a new earnings calendar feature
```

**What it does:**
1. Runs pre-flight validation
2. Shows you if the request passes or fails
3. Displays which agents will be involved
4. Shows relevant specs and rules

**Example:**
```
You: /check-rules Add horizontal dividers

Response:
[FAIL] Pre-flight validation FAILED

ERROR: FORBIDDEN: Request contains horizontal line/divider.
       See UI_STYLE_GUIDE.md - NO horizontal lines allowed.
```

---

## 🧠 How Agent Auto-Selection Works

The orchestrator automatically selects agents based on **keywords in your request**:

### Trading Keywords → Trading Specialists

| You say | Agent auto-invoked |
|---------|-------------------|
| "calendar spread" | calendar-spreads-specialist |
| "earnings" | earnings-specialist |
| "7 day DTE" | dte-scanner-specialist |
| "sports betting" | sports-betting-specialist |

### Development Keywords → Dev Agents

| You say | Agent auto-invoked |
|---------|-------------------|
| "UI" / "page" | frontend-developer |
| "database" / "query" | database-optimizer |
| "AI" / "RAG" / "chatbot" | ai-engineer |
| "performance" / "optimize" | performance-engineer |
| "API" / "backend" | backend-architect |

### Quality Keywords → Quality Agents

| You say | Agent auto-invoked |
|---------|-------------------|
| "bug" / "error" / "broken" | bug-root-cause-analyzer |
| "test" | qa-tester, spec-test-generator |
| "review" | code-reviewer |

### Operations Keywords → Ops Agents

| You say | Agent auto-invoked |
|---------|-------------------|
| "incident" / "outage" | devops-incident-responder |
| "deploy" / "CI/CD" | deployment-engineer |

**You don't need to specify agents - they're selected automatically!**

---

## 🔄 Parallel Execution

The orchestrator runs agents **in parallel** for maximum speed:

### Priority Groups

1. **Critical (Sequential):**
   - spec-requirements-validator
   - spec-breaking-change-detector
   - rule_engine

   **Runs:** One at a time (ensures nothing blocked)

2. **High (5 parallel):**
   - spec-design-validator
   - code-reviewer
   - qa-tester
   - bug-root-cause-analyzer

   **Runs:** Up to 5 at once → **5x faster**

3. **Medium (10 parallel):**
   - spec-test-generator
   - spec-performance-analyzer
   - performance-engineer
   - database-optimizer

   **Runs:** Up to 10 at once → **10x faster**

4. **Low (3 parallel):**
   - spec-documentation-generator
   - steering-document-updater

   **Runs:** Up to 3 at once, non-blocking

**Total speedup: 5-10x faster than sequential execution**

---

## 📊 Understanding Orchestrator Output

### What You'll See

**During execution, you'll see:**

```
ORCHESTRATOR: Pre-flight validation PASSED
Features: calendar-spreads
Recommended agents: calendar-spreads-specialist, data-scientist, performance-engineer
Rules active: no_horizontal_lines, accurate_spread_pricing
```

**What this means:**
- ✅ Your request passed validation
- ✅ Feature "calendar-spreads" was identified
- ✅ 3 agents will be involved
- ✅ 2 critical rules are active for this feature

### After Completion

```
ORCHESTRATOR: Execution Complete

Summary:
- Primary agent: calendar-spreads-specialist
- Supporting agents: 3
- QA agents: 2
- Files modified: 4
- Tests generated: 12
- QA status: All passed
- UI tests: Passed (1 page tested)
- Ready to commit: Yes
```

---

## ⚙️ Configuration

### Changing Orchestrator Behavior

**Edit:** `.claude/orchestrator/config.yaml`

**Common changes:**

```yaml
# Enable/disable features
orchestrator:
  auto_run_on_request: true  # Set to false to disable auto-run
  auto_qa_on_completion: true  # Set to false to skip automatic QA

# Enable/disable auto-fix
post_execution:
  auto_fix: false  # Set to true to auto-fix simple violations (USE WITH CAUTION!)

# Adjust parallel limits
performance:
  max_parallel_agents: 10  # Reduce if system is slow
  timeout_seconds: 300  # Increase for long-running operations
```

### Adding Custom Rules

**Edit:** `.claude/orchestrator/config.yaml`

```yaml
rules:
  code:
    your_custom_rule:
      severity: high  # critical, high, medium, low
      message: "Your rule description"
      patterns:
        - "pattern_to_match"
      auto_fix: false
```

### Disabling Specific Agents

**Edit:** `.claude/orchestrator/config.yaml`

```yaml
agents:
  priority_groups:
    critical:
      # Remove agents you don't want to run
      - spec-requirements-validator
      # - spec-breaking-change-detector  # Commented out = disabled
```

---

## 🚨 Troubleshooting

### Orchestrator Not Running

**Check status:**
```bash
cd c:/code/Magnus/.claude/orchestrator
python main_orchestrator.py --summary
```

**Verify enabled:**
```yaml
# In config.yaml
orchestrator:
  enabled: true  # Must be true
```

### False Positives

**If orchestrator blocks valid requests:**

1. Check the rule in `config.yaml`
2. Adjust the pattern or severity
3. Or acknowledge you want to bypass:
   ```
   "Add this feature (bypass horizontal line rule)"
   ```

### Slow Performance

**If orchestrator is slow:**

1. Reduce parallel agents:
   ```yaml
   performance:
     max_parallel_agents: 5  # Reduce from 10
   ```

2. Increase timeouts:
   ```yaml
   performance:
     timeout_seconds: 600  # Increase from 300
   ```

3. Disable non-critical agents

---

## 📈 Advanced Usage

### State Machine Inspection

**View current state:**
```python
from state_machine import get_state_machine

sm = get_state_machine()
print(sm.get_state_summary())
```

**Rollback last operation:**
```python
sm.rollback(steps=1)  # Roll back 1 state change
```

**Load checkpoint:**
```python
sm.load_checkpoint("checkpoint_20251122_183000.json")
```

### Custom Agent Execution

**Run specific agent directly:**
```bash
# Using the Task tool
Task(
    subagent_type="calendar-spreads-specialist",
    description="Analyze calendar spreads",
    prompt="Find top 10 calendar spread opportunities"
)
```

---

## 💡 Pro Tips

### 1. Let the Orchestrator Guide You

**Instead of:**
```
"I need to add a feature... which agent should I use?"
```

**Just say:**
```
"Add a feature that tracks earnings and suggests avoidance strategies"
```

**The orchestrator will:**
- Identify it's an earnings-related feature
- Auto-select earnings-specialist
- Load earnings-calendar specs
- Apply relevant rules

### 2. Trust the Blocking

**If orchestrator blocks your request, there's a good reason:**
- Rule violation detected
- Breaking change identified
- Deprecated pattern found

**Either:**
- Revise the request, OR
- Acknowledge you want to bypass

### 3. Use Parallel Execution

**The orchestrator is optimized for speed:**
- Multiple agents run simultaneously
- State machine ensures consistency
- Checkpointing prevents data loss

**You get 5-10x faster execution automatically!**

### 4. Check Specs Before Building

**Before requesting a new feature:**
```
/check-rules Implement XYZ feature
```

**This shows you:**
- If similar feature exists
- Which specs are relevant
- What rules apply
- Which agents will be involved

---

## 🎓 Learning More

**Documentation:**
- [QUICK_START.md](./QUICK_START.md) - Quick reference
- [WORLD_CLASS_ORCHESTRATOR_COMPLETE.md](./WORLD_CLASS_ORCHESTRATOR_COMPLETE.md) - Full details
- [config.yaml](./config.yaml) - Configuration reference
- [feature_registry.yaml](./feature_registry.yaml) - Feature mapping

**Test It:**
```bash
# Run the test suite
cd c:/code/Magnus/.claude/orchestrator
python test_orchestrator.py
```

---

## ✅ Summary

**The orchestrator is working automatically right now!**

**You can:**
- ✅ Just make requests normally (recommended)
- ✅ Use `/check-rules` to validate first (optional)
- ✅ Run manual tests (optional)
- ✅ Customize configuration (advanced)

**The orchestrator handles:**
- ✅ Request validation
- ✅ Agent selection
- ✅ Parallel execution
- ✅ QA validation
- ✅ Rule enforcement
- ✅ Everything automatically!

**You never have to:**
- ❌ Manually select agents
- ❌ Remember project rules
- ❌ Coordinate execution
- ❌ Run QA manually

**Just work normally - the orchestrator does the rest!** 🚀
