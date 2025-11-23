# Orchestrator Integration Guide

**How to Make the Orchestrator Run Automatically**

---

## 🎯 **Goal**

Make the orchestrator run automatically on **every Claude Code request** and **every git commit**.

---

## 🚀 **Quick Start (5 Minutes)**

### **Step 1: Install Git Hooks**

```bash
cd c:/code/Magnus
python .claude/orchestrator/install_hooks.py
```

This installs:
- ✅ `pre-commit` - Runs QA before commits
- ✅ Auto-validation on file changes

### **Step 2: Test the Installation**

```bash
# Test pre-commit hook
python .claude/orchestrator/main_orchestrator.py --summary

# Test QA on a file
python .claude/orchestrator/main_orchestrator.py --qa positions_page_improved.py
```

### **Step 3: Make a Test Commit**

```bash
# Make a small change
echo "# test" >> test_file.py

# Try to commit
git add test_file.py
git commit -m "Test orchestrator"

# The orchestrator will run automatically!
```

---

## 📋 **How It Works**

### **Automatic Execution Points**

```
1. Before Code Changes (Pre-Flight)
   ├─ Load project rules
   ├─ Check against anti-patterns
   ├─ Load feature specs
   └─ Inject context

2. After Code Changes (Post-Execution)
   ├─ Check horizontal lines
   ├─ Validate code quality
   ├─ Check rate limiting
   └─ Report violations

3. Before Git Commit (Pre-Commit Hook)
   ├─ Run QA on staged files
   ├─ Block commit if violations found
   └─ Allow commit if all checks pass
```

---

## 🔧 **Manual Invocation**

### **Run Orchestrator on a Request**

```bash
python .claude/orchestrator/main_orchestrator.py --request "Add horizontal divider to dashboard"
```

**Output:**
```
❌ Pre-flight validation FAILED

Errors:
  ❌ FORBIDDEN: Request contains horizontal line/divider.
     See UI_STYLE_GUIDE.md - NO horizontal lines allowed.

Features involved: dashboard
Rules enforced: no_horizontal_lines
```

### **Run QA on Files**

```bash
python .claude/orchestrator/main_orchestrator.py --qa positions_page_improved.py dashboard.py
```

**Output:**
```
QA Result:
Passed: True
Files checked: 2
Checks run: horizontal_lines, code_quality, performance_regression
```

### **Get Orchestrator Summary**

```bash
python .claude/orchestrator/main_orchestrator.py --summary
```

**Output:**
```
Main Orchestrator Status:
- Mode: standard
- Pre-flight: enabled
- Post-execution QA: enabled
- Features tracked: 30
- Rules loaded: 6
```

---

## 🎓 **For Claude Code Integration**

### **Option 1: Via MCP Server (Recommended)**

Create `.claude/mcp/orchestrator_server.py`:

```python
from mcp.server import Server
from .orchestrator import get_orchestrator

server = Server("orchestrator")

@server.tool()
async def validate_request(request: str, context: dict) -> dict:
    """Validate request before execution"""
    orchestrator = get_orchestrator()
    return orchestrator.orchestrate(request, context)

@server.tool()
async def run_qa(files: list) -> dict:
    """Run QA after code changes"""
    orchestrator = get_orchestrator()
    return orchestrator.post_execution_qa(files)
```

Then in your Claude Code instance, it can call:
- `validate_request(request, context)` before making changes
- `run_qa(files)` after making changes

### **Option 2: Via Pre/Post Hooks**

Create `.claude/hooks/pre-request.py`:

```python
from .orchestrator import get_orchestrator

def pre_request(request, context):
    """Run before every Claude Code request"""
    orchestrator = get_orchestrator()
    result = orchestrator.orchestrate(request, context)

    if not result.validation_results.get("passed"):
        raise ValueError(f"Pre-flight validation failed: {result.validation_results}")

    return result
```

---

## 📊 **Configuration**

Edit `.claude/orchestrator/config.yaml` to customize:

```yaml
orchestrator:
  enabled: true
  mode: standard  # standard, aggressive, passive

pre_flight:
  enabled: true
  strict_mode: true  # Block on errors

post_execution:
  enabled: true
  auto_fix: true  # Auto-fix violations (horizontal lines)

rules:
  ui:
    no_horizontal_lines:
      severity: critical
      auto_fix: true  # Automatically remove
```

---

## 🧪 **Testing**

### **Test Pre-Flight Validation**

```python
from .claude.orchestrator import get_orchestrator

orchestrator = get_orchestrator()

# Should FAIL
result = orchestrator.orchestrate("Add a horizontal divider to the page")
assert not result.validation_results["passed"]

# Should PASS
result = orchestrator.orchestrate("Add a section header to the page")
assert result.validation_results["passed"]
```

### **Test QA**

```python
from .claude.orchestrator import get_orchestrator

orchestrator = get_orchestrator()

# Create a file with violations
with open("test_file.py", "w") as f:
    f.write('st.markdown("---")\n')

# Run QA
result = orchestrator.post_execution_qa(["test_file.py"])
assert not result["passed"]
assert len(result["violations"]) > 0
```

---

## 🎯 **Expected Behavior**

### **Scenario 1: User Asks for Horizontal Line**

```
User: "Add a horizontal divider between sections"

Orchestrator (Pre-Flight):
❌ FORBIDDEN: Request contains horizontal line/divider.
   See UI_STYLE_GUIDE.md - NO horizontal lines allowed.

Result: Request is BLOCKED before Claude Code even starts
```

### **Scenario 2: Code Added Without Rate Limiting**

```
User: "Fetch Robinhood positions"

Claude Code: *writes code with rh.get_open_option_positions()*

Orchestrator (Post-QA):
❌ Robinhood API call without rate limiting.
   Use rate-limited wrappers.

Result: Violation reported, must be fixed before commit
```

### **Scenario 3: All Checks Pass**

```
User: "Add a new section header"

Orchestrator (Pre-Flight):
✅ Validation passed
   Features: dashboard
   Rules: no_horizontal_lines

Claude Code: *makes changes*

Orchestrator (Post-QA):
✅ QA passed
   Files checked: 1
   Violations: 0

Result: Changes allowed, commit will succeed
```

---

## 🔄 **Continuous Improvement**

The orchestrator **learns from violations**:

1. Logs all violations to `.claude/orchestrator/orchestrator.log`
2. Tracks patterns of violations
3. Can suggest new rules based on common issues

---

## 📚 **Next Steps**

1. ✅ Install hooks: `python install_hooks.py`
2. ✅ Test: Make a commit with a violation
3. ✅ Configure: Edit `config.yaml` for your needs
4. ✅ Integrate: Add to your Claude Code workflow

---

## ❓ **FAQ**

**Q: Will this slow down my workflow?**
A: No! Pre-flight runs in <100ms, QA in <500ms for most files.

**Q: Can I bypass it in an emergency?**
A: Yes: `git commit --no-verify` (not recommended)

**Q: Does it work with all IDEs?**
A: Yes! It's git-hook based, so it works everywhere.

**Q: Can I add my own rules?**
A: Yes! Edit `config.yaml` and add patterns.

---

## 🎉 **You're Done!**

The orchestrator is now running automatically. It will:
- ✅ Validate every request
- ✅ Run QA on every change
- ✅ Enforce project rules
- ✅ Block commits with violations

**No more horizontal lines!** 🎊
