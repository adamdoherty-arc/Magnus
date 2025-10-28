# Agent Usage Guide - Practical Implementation

## Quick Start: Using Agents for Development

### ✅ The Fixed SQL Error Example (What Just Happened)

**Problem**: Dashboard had SQL error `IndexError: tuple index out of range`

**Agent Workflow Used**:
1. **Debugger Agent** - Identified the root cause (unescaped `%` in SQL query)
2. **I Fixed** - Changed `'5%_OTM'` to `'5%%_OTM'`
3. **Debugger Agent** - Verified fix works, no new errors

**Result**: Dashboard now works perfectly! ✓

---

## Mandatory: ALWAYS Test Before Delivering

### The Golden Rule
**After ANY code change, invoke the QA/Debugger agent BEFORE telling the user it's done.**

### Example Command
```
Use the debugger agent to:
1. Check if file X has any syntax errors
2. Test if the dashboard loads without errors
3. Verify feature Y works as expected
4. Check logs for any warnings or errors
```

---

## Agent Usage Patterns

### Pattern 1: Simple Bug Fix
```
User: "Dashboard shows error XYZ"

You:
1. Use debugger agent to analyze error
2. Make fix based on analysis
3. Use debugger agent to verify fix works
4. Report success to user
```

### Pattern 2: New Feature Request
```
User: "Add ability to filter by IV > 50%"

You:
1. Use architect-reviewer agent for design (if complex)
2. Create todos with planning
3. Write code (python-pro if needed)
4. Use debugger agent to test
5. Use code-reviewer agent for quality check
6. Deploy and report to user
```

### Pattern 3: Performance Issue
```
User: "Dashboard is slow"

You:
1. Use performance-engineer agent to profile
2. Identify bottleneck
3. Use database-optimizer agent if DB issue
4. Implement fix
5. Use debugger agent to verify improvement
6. Report results to user
```

---

## When to Use Each Agent

### Debugger Agent (Most Used)
**Use for**:
- Testing after code changes
- Investigating errors
- Verifying fixes work
- Checking logs
- Finding root causes

**Don't use for**:
- Writing code
- Design decisions
- Documentation

### Code-Reviewer Agent
**Use for**:
- Major feature completion
- Before production deploy
- Security-sensitive code
- Complex refactoring

**Don't use for**:
- Simple bug fixes
- Quick changes
- Documentation

### Architect-Reviewer Agent
**Use for**:
- New major features
- System redesign
- Unclear requirements
- Breaking changes

**Don't use for**:
- Simple features
- Bug fixes
- UI tweaks

### Python-Pro Agent
**Use for**:
- Complex Python code
- Algorithm implementation
- Advanced patterns
- Optimization

**Don't use for**:
- Simple changes
- SQL queries
- UI layout

### Database-Optimizer Agent
**Use for**:
- Schema design
- Query optimization
- Indexing strategy
- Migration planning

**Don't use for**:
- Simple SELECT queries
- UI code
- Business logic

### Performance-Engineer Agent
**Use for**:
- Slow queries (>1s)
- High memory usage
- Profiling needed
- Scalability

**Don't use for**:
- Functional bugs
- UI issues
- Simple optimizations

---

## Practical Examples

### Example 1: "Fix This Error"
```
User provides error screenshot

Your workflow:
1. Read error carefully
2. Use debugger agent: "Analyze this error in file X, line Y"
3. Agent reports: "Issue is Z"
4. Make fix
5. Use debugger agent: "Verify fix works and no new errors"
6. Tell user: "Fixed! The issue was Z. Tested and working."
```

### Example 2: "Add New Feature"
```
User: "I want to see ROI column in the table"

Your workflow:
1. Plan the change (simple, no agent needed)
2. Add ROI calculation and column
3. Use debugger agent: "Test that dashboard loads and ROI column displays correctly"
4. Agent confirms: "Working perfectly"
5. Tell user: "Added ROI column! Shows in table now."
```

### Example 3: "Dashboard Broken"
```
User: "Dashboard won't load"

Your workflow:
1. Use debugger agent: "Check dashboard logs for errors"
2. Agent finds: "SQL syntax error at line 123"
3. Fix the SQL
4. Use debugger agent: "Verify dashboard loads"
5. Agent confirms: "Dashboard loads successfully"
6. Tell user: "Fixed! Dashboard working now."
```

---

## Agent Invocation Checklist

### Before Every User Response:
- [ ] Did I make code changes?
  - If YES → Run debugger agent
- [ ] Did I fix a bug?
  - If YES → Run debugger agent to verify
- [ ] Is this a major feature?
  - If YES → Run code-reviewer agent
- [ ] Am I unsure if it works?
  - If YES → Test it with debugger agent!

### The "Don't Be Embarrassed" Rule
**It's better to find errors with agents than have the user find them!**

---

## Common Mistakes to Avoid

### ❌ DON'T: Tell user "it's fixed" without testing
```
User: "Error in dashboard"
You: "Fixed line 123, should work now!"
User: "Still broken, different error now"
```

### ✅ DO: Test before reporting
```
User: "Error in dashboard"
You: [fixes code]
You: [uses debugger agent to verify]
Agent: "Tested successfully, no errors"
You: "Fixed! Tested and working perfectly."
```

### ❌ DON'T: Assume code works
```
You: "Added new feature X"
User: "It crashes when I click the button"
```

### ✅ DO: Verify functionality
```
You: [adds feature]
You: [uses debugger agent to test]
Agent: "Feature works, button responds correctly"
You: "Added feature X, tested and working!"
```

---

## Agent Collaboration

### Sequential Pattern (Most Common)
```
1. Debugger finds issue
   ↓
2. You fix it
   ↓
3. Debugger verifies fix
```

### Parallel Pattern (Complex Features)
```
1. Architect designs
   ↓
2. Python-Pro codes + Database-Optimizer handles DB
   ↓
3. Debugger tests both
   ↓
4. Code-Reviewer checks quality
```

---

## Testing Standards

### Minimum Testing Requirements
Every change must pass:
1. **Syntax Check** - Code parses without errors
2. **Import Check** - No import errors
3. **Runtime Check** - Application starts successfully
4. **Functional Check** - Feature works as intended
5. **No Regressions** - Nothing else broke

### How to Test with Debugger Agent
```
Prompt template:
"Test the following:
1. Check [file.py] for syntax errors
2. Verify [feature X] works correctly
3. Check dashboard loads without errors
4. Look for any warnings or errors in logs
5. Confirm no breaking changes to existing features"
```

---

## Emergency Procedures

### Production is Down
```
1. Use debugger agent IMMEDIATELY
   "Analyze production logs, find critical error"
2. Agent identifies issue
3. Implement hotfix
4. Use debugger agent to verify fix
5. Deploy
6. Use code-reviewer after for post-mortem
```

### User Found Bug
```
1. Reproduce the issue
2. Use debugger agent to analyze
3. Fix based on findings
4. Use debugger agent to verify fix
5. Test edge cases
6. Report fix to user with explanation
```

---

## Pro Tips

### Tip 1: Detailed Agent Prompts
❌ Bad: "Test this"
✅ Good: "Test dashboard.py: verify it loads without errors, check all database queries work, ensure UI displays correctly"

### Tip 2: Agent Output is Data
Save agent findings for documentation:
```
Agent found: "SQL performance issue in query X"
→ Document this for future reference
→ Add to technical debt backlog
```

### Tip 3: Trust But Verify
Even if agent says it's good, do a quick manual check of critical features.

### Tip 4: Learn from Agent Feedback
If agents find issues frequently in area X:
→ That area needs refactoring
→ Add tests for that area
→ Document common pitfalls

---

## Quick Reference

### Most Used Agents
1. **Debugger** (90% of the time) - Test everything!
2. **Code-Reviewer** (10% of time) - Quality check
3. **Architect** (5% of time) - Complex designs

### Agent Speed Guide
- Debugger: Fast (10-30s)
- Code-Reviewer: Medium (30-60s)
- Architect: Slow (1-3 min)
- Database-Optimizer: Medium (30-60s)

### When in Doubt
**Use the debugger agent!** It's fast and catches most issues.

---

## Success Metrics

### Green Light Criteria (Before User Delivery)
- ✅ No syntax errors
- ✅ No import errors
- ✅ No runtime errors
- ✅ Feature works as described
- ✅ No breaking changes
- ✅ Agent-verified testing passed

### Red Flags (Need More Testing)
- ⚠️ "I think it should work"
- ⚠️ "Looks good to me"
- ⚠️ "Probably fine"
- ⚠️ "Let's see if user finds issues"

**If you see red flags → RUN DEBUGGER AGENT!**

---

## Conclusion

**The One Rule to Rule Them All:**
> Test with agents BEFORE delivery, not after user complaints.

**Remember:**
- Agents are fast (seconds)
- Users finding bugs is slow (frustration)
- Always test first, deliver second
- Trust but verify

---

**Last Updated**: 2025-10-27
**Version**: 1.0
