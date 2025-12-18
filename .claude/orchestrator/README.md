# Main Orchestrator System

**Created:** November 22, 2025
**Purpose:** Automatic coordination, validation, and QA for all Claude Code interactions

---

## 🎯 **Architecture Overview**

```
User Request
    ↓
Main Orchestrator (auto-runs)
    ↓
├─→ [Pre-Flight Validation]
│   ├─ Load Project Rules (UI_STYLE_GUIDE.md, etc.)
│   ├─ Check Against Known Issues
│   └─ Validate Request Context
│
├─→ [Spec Agent Consultation] (Parallel)
│   ├─ Identify Relevant Feature(s)
│   ├─ Load Feature Specifications
│   └─ Inject Context into Request
│
├─→ [Execute Task]
│   └─ Use Appropriate Specialized Agent
│
├─→ [Post-Execution QA] (Parallel)
│   ├─ Code Quality Checks
│   ├─ Rule Compliance Validation
│   ├─ Breaking Change Detection
│   └─ Performance Analysis
│
└─→ [Report & Learn]
    ├─ Update Rule Base
    └─ Log Patterns
```

---

## 📋 **Components**

| Component | File | Purpose |
|-----------|------|---------|
| **Main Orchestrator** | `main_orchestrator.py` | Entry point, coordinates all agents |
| **Pre-Flight Validator** | `pre_flight_validator.py` | Validates before execution |
| **QA Agent** | `qa_agent.py` | Post-execution quality checks |
| **Feature Registry** | `feature_registry.yaml` | Maps features to specs |
| **Rule Engine** | `rule_engine.py` | Loads and enforces project rules |
| **Integration Bridge** | `legion_bridge.py` | Connects to existing Legion system |

---

## 🚀 **How It Works**

### **Automatic Execution**

The orchestrator runs automatically via:
1. **MCP Server Integration** - Provides orchestration as an MCP tool
2. **Git Hooks** - Pre-commit validation
3. **Manual Invocation** - For testing/debugging

### **Validation Workflow**

**Pre-Flight:**
```python
1. Load all project rules
2. Check if request matches known anti-patterns
3. Identify relevant feature specifications
4. Inject context and constraints
```

**Post-Execution:**
```python
1. Run code quality checks
2. Validate against UI style guide
3. Check for breaking changes
4. Verify test coverage
5. Report compliance status
```

---

## 🎓 **Based On**

- **LangGraph** - State machine approach for workflow control
- **AutoGen** - Conversational multi-agent coordination
- **CrewAI** - Role-based agent orchestration

---

## 📚 **Usage**

### **Manual Invocation** (for testing)
```bash
python .claude/orchestrator/main_orchestrator.py --request "Add new feature"
```

### **Automatic (Production)**
The orchestrator runs automatically - no manual invocation needed!

---

## 🔧 **Configuration**

Edit `.claude/orchestrator/config.yaml` to control:
- Which agents run automatically
- Validation strictness levels
- QA thresholds
- Feature spec mappings
