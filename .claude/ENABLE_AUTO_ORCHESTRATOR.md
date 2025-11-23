# How to Enable Automatic Orchestrator on Every Claude Code Request

**Goal:** Make the orchestrator run AUTOMATICALLY on every single chat/request, not just git commits.

---

## 🎯 Current Status

✅ **Git Commits:** Orchestrator runs automatically
❌ **Chat Requests:** Must be manually invoked

**Let's fix this!**

---

## 🚀 Method 1: Use Slash Command (Recommended - Easiest)

### **Setup (One Time)**

The slash command is already created at `.claude/commands/check-rules.md`

### **Usage (Every Request)**

Before making changes, type:
```
/check-rules Add horizontal dividers between sections
```

Claude Code will:
1. Run the orchestrator
2. Show validation result
3. Proceed only if validation passes

**Pros:** Simple, explicit, full control
**Cons:** Must remember to type `/check-rules` each time

---

## 🚀 Method 2: Python Wrapper (Auto-Run)

### **Setup**

Create a wrapper that Claude Code calls before every request:

**File:** `.claude/orchestrator/auto_run.py` ✅ Already created

### **Integration with Claude Code**

Add to your prompt/instructions:
```
Before executing any request that modifies code, run:
python .claude/orchestrator/auto_run.py "{{request}}"

If this returns error (exit code 1), validation failed - explain violations and ask user.
If this returns success (exit code 0), proceed with the request.
```

### **Testing**

```bash
cd c:/code/Magnus

# Test with forbidden request
python .claude/orchestrator/auto_run.py "Add horizontal divider"
# Output: ORCHESTRATOR: Pre-flight validation FAILED
#         Violations:
#           - FORBIDDEN: Request contains horizontal line/divider...
# Exit code: 1

# Test with normal request
python .claude/orchestrator/auto_run.py "Add section header"
# Output: ORCHESTRATOR: Pre-flight validation PASSED
# Exit code: 0
```

---

## 🚀 Method 3: MCP Server (Most Powerful)

### **What is MCP?**

Model Context Protocol - allows Claude Code to call external tools automatically.

### **Setup**

**File:** `.claude/orchestrator/mcp_server.py` ✅ Already created

### **Testing MCP Server**

```bash
cd c:/code/Magnus/.claude/orchestrator

# Test validation
python mcp_server.py --validate "Add horizontal divider"

# Test QA
python mcp_server.py --qa positions_page_improved.py

# Test context lookup
python mcp_server.py --context positions_page_improved.py
```

### **Integration**

Configure Claude Code to use the MCP server in `.claude/mcp_config.json`:

```json
{
  "mcpServers": {
    "orchestrator": {
      "command": "python",
      "args": [".claude/orchestrator/mcp_server.py"],
      "tools": [
        {
          "name": "validate_request",
          "description": "Validate request against project rules before execution"
        },
        {
          "name": "run_qa",
          "description": "Run QA checks on modified files"
        },
        {
          "name": "get_feature_context",
          "description": "Get feature context and specs for files"
        }
      ]
    }
  }
}
```

---

## 🎯 Recommended Approach: Combination

### **For You (Manual Control)**

Use the **slash command** when you want to check:
```
/check-rules Your request here
```

### **For Me (Claude Code - Auto)**

I should proactively run the orchestrator before making changes:

```python
# Before modifying any page file
python .claude/orchestrator/auto_run.py "{{request}}"

# If validation fails, explain to user
# If validation passes, proceed
```

---

## 📝 Adding to My Workflow

### **Option A: Update My System Prompt**

Add this to my instructions (you configure this in Claude Code settings):

```
CRITICAL RULE: Before modifying any code, you MUST run:

python .claude/orchestrator/auto_run.py "{{user_request}}"

If validation FAILS (exit code 1):
- Explain the violations to the user
- Ask how they want to proceed
- Do NOT make the changes unless explicitly told to bypass

If validation PASSES (exit code 0):
- Note the features/agents/rules from output
- Proceed with the request using that context
```

### **Option B: Create a Pre-Request Hook**

If Claude Code supports pre-request hooks, configure:

**File:** `.claude/hooks/pre-request.sh`
```bash
#!/bin/bash
python .claude/orchestrator/auto_run.py "$1"
exit $?
```

---

## 🧪 Testing the Integration

### **Test 1: Forbidden Request**

```bash
python .claude/orchestrator/auto_run.py "Add horizontal dividers to dashboard"
```

**Expected Output:**
```
ORCHESTRATOR: Pre-flight validation FAILED

Violations:
  - FORBIDDEN: Request contains horizontal line/divider.
    See UI_STYLE_GUIDE.md - NO horizontal lines allowed.

Please revise your request or acknowledge you want to bypass these rules.
```

**Exit Code:** 1 (failure)

### **Test 2: Valid Request**

```bash
python .claude/orchestrator/auto_run.py "Add section headers to dashboard"
```

**Expected Output:**
```
ORCHESTRATOR: Pre-flight validation PASSED
Features: dashboard
Recommended agents: frontend-developer
Rules active: no_horizontal_lines
```

**Exit Code:** 0 (success)

### **Test 3: Feature Context**

```bash
python .claude/orchestrator/mcp_server.py --context positions_page_improved.py
```

**Expected Output:**
```json
{
  "features": ["robinhood-positions"],
  "specialist_agents": ["options-trading-specialist"],
  "specs": {
    "robinhood-positions": {
      "requirements.md": "c:/code/Magnus/.claude/specs/robinhood-positions/requirements.md",
      "design.md": "c:/code/Magnus/.claude/specs/robinhood-positions/design.md"
    }
  }
}
```

---

## 🎊 What This Achieves

### **Before (Current State)**

- ✅ Orchestrator runs on git commits
- ❌ Orchestrator does NOT run on chat requests
- ❌ Must manually remember to check rules

### **After (With Integration)**

- ✅ Orchestrator runs on git commits
- ✅ Orchestrator runs on EVERY chat request (auto)
- ✅ Validation happens BEFORE any code is written
- ✅ Full context (features, specs, agents) injected automatically
- ✅ You never have to remind me about rules

---

## 📚 Which Method Should You Use?

| Method | Ease | Automation | Best For |
|--------|------|------------|----------|
| **Slash Command** | ⭐⭐⭐ Very Easy | Manual | You want control over when to check |
| **Python Wrapper** | ⭐⭐ Medium | Semi-Auto | I proactively call it before changes |
| **MCP Server** | ⭐ Advanced | Fully Auto | Integration with Claude Code tools |

**Recommended:** Start with **Slash Command** + have me proactively use **Python Wrapper**

---

## 🚀 Quick Start

### **For Immediate Use:**

```bash
# Test it works
cd c:/code/Magnus
python .claude/orchestrator/auto_run.py "Add horizontal divider"

# If that blocks correctly, you're ready!
```

### **For Me to Use Automatically:**

Tell me:
> "Before modifying any code, always run:
> python .claude/orchestrator/auto_run.py with my request.
> If validation fails, tell me the violations and ask how to proceed."

I'll remember that instruction and do it automatically!

---

## ✅ Summary

**Files Created:**
- ✅ `.claude/orchestrator/auto_run.py` - Auto-validation wrapper
- ✅ `.claude/orchestrator/mcp_server.py` - MCP server (advanced)
- ✅ `.claude/commands/check-rules.md` - Slash command

**How to Enable:**
1. **Option 1:** Type `/check-rules` before requests (manual)
2. **Option 2:** Tell me to run `auto_run.py` before changes (semi-auto)
3. **Option 3:** Configure MCP server in Claude Code (fully auto)

**Recommended:** Use Option 2 - I'll proactively validate every request!

---

**Ready to enable? Just tell me which method you prefer!**
