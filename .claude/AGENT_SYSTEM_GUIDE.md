# Agent System Guide - Wheel Strategy Project

**Last Updated**: 2025-10-27
**Version**: 2.0
**Type**: Markdown-Based Agents

---

## Overview

The Wheel Strategy project uses a **markdown-based agent system** where specialized agents are defined as prompt files that can be invoked to handle specific tasks.

### What Are Agents?

Agents are **expert specialists** defined in markdown files. Each agent:
- Has a specific domain of expertise
- Follows structured workflows
- Provides consistent output formats
- Can be invoked when needed
- Works independently or with other agents

### Why Markdown?

Markdown-based agents are:
- ✅ Easy to read and understand
- ✅ Simple to create and modify
- ✅ Version controlled with code
- ✅ Shareable and reusable
- ✅ No complex infrastructure needed

---

## Agent Directory

### Current Agents

Located in [`.claude/agents/`](.claude/agents/):

| Agent | File | Priority | Purpose |
|-------|------|----------|---------|
| **QA Tester** | [qa-tester.md](agents/qa-tester.md) | CRITICAL | Testing & verification (MANDATORY) |
| **Code Reviewer** | [code-reviewer.md](agents/code-reviewer.md) | HIGH | Code quality & best practices |
| **Architect** | [architect.md](agents/architect.md) | HIGH | System design & planning |

### Planned Agents

Coming soon:
- **Python Expert** - Python implementation & optimization
- **Database Expert** - Schema design & query optimization
- **Frontend Expert** - Streamlit UI development
- **Performance Expert** - Profiling & optimization
- **Security Expert** - Security audit & hardening
- **Error Detective** - Bug investigation & debugging

---

## How to Use Agents

### Basic Invocation

Simply reference the agent in your request:

```
"Use the QA Tester agent to test dashboard.py"
```

```
"Have the Code Reviewer agent review the new feature"
```

```
"Ask the Architect agent to design the notification system"
```

### With Context

Provide specific context for better results:

```
"Use the QA Tester agent to:
- Test the new filters in dashboard.py
- Verify the Premium column sorts numerically
- Check that all 10 filters work correctly
- Ensure no errors in logs"
```

### Multiple Agents

You can invoke agents in sequence:

```
"First, have the Architect agent design the alert system.
Then use the Python Expert to implement it.
Finally, use the QA Tester to verify it works."
```

---

## Standard Workflows

### Bug Fix Workflow

```
1. Identify the issue
2. Implement the fix
3. ✅ QA Tester agent - Test the fix (MANDATORY)
4. ✅ Code Reviewer agent - Review quality
5. Deliver to user
```

### New Feature Workflow

```
1. ✅ Architect agent - Design the solution
2. Create implementation plan with todos
3. Implement the feature (Python/Frontend/DB experts)
4. ✅ QA Tester agent - Comprehensive testing (MANDATORY)
5. ✅ Code Reviewer agent - Quality review
6. Deliver to user
```

### Optimization Workflow

```
1. ✅ Performance Expert - Profile & identify bottlenecks
2. ✅ Database Expert - Optimize queries (if DB issue)
3. Implement optimizations
4. ✅ QA Tester agent - Verify improvements (MANDATORY)
5. Deliver to user
```

---

## The Golden Rule

### NEVER Deliver Without QA Testing

**Before EVERY code delivery**:

1. ✅ Invoke QA Tester agent
2. ✅ Agent runs tests
3. ✅ Review test report
4. ✅ Verify ALL tests pass
5. ✅ **THEN** deliver to user

**Why?**
- Catches errors before users see them
- Ensures quality standards
- Prevents regressions
- Builds user trust
- Reduces debugging time

---

## Agent Protocols

### QA Tester Protocol

**When**: After ANY code change
**Tests**:
- Syntax validation
- Import checking
- Dashboard load test
- Functional verification
- Regression testing

**Output**: Pass/Fail report with details

### Code Reviewer Protocol

**When**: Major features, refactoring, security-sensitive code
**Reviews**:
- Code quality (PEP 8)
- Error handling
- Security
- Performance
- Documentation

**Output**: Scored review (0-100) with recommendations

### Architect Protocol

**When**: New features, system redesign, unclear requirements
**Delivers**:
- Architecture design
- Component breakdown
- Data flow diagrams
- Implementation plan
- Risk assessment

**Output**: Comprehensive design document

---

## Quality Gates

### Mandatory Gates

Must pass before delivery:

1. **QA Tester** - For ALL code changes
2. **Code Reviewer** - For major features
3. **Architect** - For system changes

### Optional Gates

Recommended but not required:

- **Performance Expert** - For critical paths
- **Security Expert** - For sensitive operations
- **Database Expert** - For complex queries

---

## Creating New Agents

### Agent Template

```markdown
# [Agent Name]

**Role**: [Primary function]
**Priority**: CRITICAL/HIGH/MEDIUM/LOW

## Mission
[What this agent does in 2-3 sentences]

## Responsibilities
1. [Key responsibility 1]
2. [Key responsibility 2]
3. [Key responsibility 3]

## Process
[Step-by-step workflow the agent follows]

## Output Format
```
[Expected output structure]
```

## When to Invoke
- ✅ [Scenario 1]
- ✅ [Scenario 2]
- ✅ [Scenario 3]

## Example
```
[Concrete usage example]
```
```

### Steps to Add

1. Create `agent-name.md` in `.claude/agents/`
2. Fill in the template
3. Add to [agents/README.md](agents/README.md)
4. Update this guide
5. Test the agent

---

## Best Practices

### For Effective Agent Use

1. **Be Specific**
   - Clear, detailed requests
   - Provide context and files
   - State expected outcomes

2. **Provide Context**
   - Share relevant code
   - Mention related issues
   - Include error messages

3. **Follow Workflows**
   - Use standard workflows
   - Don't skip QA Tester
   - Review agent outputs

4. **Trust but Verify**
   - Agents provide expert guidance
   - You make final decisions
   - Double-check critical changes

### For Creating Agents

1. **Single Responsibility**
   - One clear purpose
   - Focused expertise
   - Well-defined scope

2. **Clear Protocols**
   - Step-by-step processes
   - Consistent output formats
   - Specific trigger conditions

3. **Actionable Output**
   - Clear recommendations
   - Specific next steps
   - Measurable criteria

4. **Collaboration Ready**
   - Can work with other agents
   - Knows when to escalate
   - Provides handoff info

---

## Agent Evolution

### Current State

**Version**: 2.0
**Type**: Markdown-based
**Location**: `.claude/agents/`
**Count**: 3 active, 6 planned

### Previous Iterations

**Version 1.0**: Python-based orchestration (deprecated)
- Complex infrastructure
- Hard to maintain
- Overkill for needs

**Version 2.0**: Markdown prompts (current)
- Simple and effective
- Easy to create/modify
- No infrastructure needed

### Future Enhancements

1. **More Specialists**
   - Domain-specific experts
   - Advanced capabilities
   - Specialized workflows

2. **Agent Metrics**
   - Track usage
   - Measure effectiveness
   - Optimize workflows

3. **Workflow Automation**
   - Auto-invoke agents
   - Smart routing
   - Parallel execution

---

## Troubleshooting

### Agent Not Responding

✅ Check agent file exists
✅ Verify markdown syntax
✅ Provide clear invocation
✅ Include necessary context

### Unclear Output

✅ Be more specific in request
✅ Provide more context
✅ Reference specific sections
✅ Ask for clarification

### Wrong Agent

✅ Review agent responsibilities
✅ Check [agents/README.md](agents/README.md)
✅ Use multiple agents if needed
✅ Ask which agent is appropriate

---

## Examples

### Example 1: Testing Code

**Request**:
```
Use the QA Tester agent to test the new filters in dashboard.py.
Check that:
- All 10 filter inputs work
- Numerical sorting is correct
- No errors in console
- Data displays properly
```

**Agent Output**:
```
## TEST REPORT

Files Tested: dashboard.py
Test Date: 2025-10-27

### Test Results

✅ PASSED
- Syntax validation: OK
- All 10 filters functional: OK
- Numerical sorting: OK (50, 100, 500 NOT 100, 50, 500)
- Console errors: None
- Data display: Correct

### Summary
ALL TESTS PASSED - Safe to deliver
```

### Example 2: Designing Feature

**Request**:
```
Ask the Architect agent to design a real-time alert system that:
- Monitors option prices
- Sends notifications when opportunities arise
- Supports multiple alert channels
- Doesn't block the UI
```

**Agent Output**:
```
## ARCHITECTURE DESIGN: Real-Time Alert System

### Proposed Architecture

Components:
1. Background Monitor Service
   - Polls prices every 30s
   - Detects threshold crosses
   - Publishes to event queue

2. Alert Rule Engine
   - Evaluates user rules
   - Filters false positives
   - Triggers notifications

3. Multi-Channel Notifier
   - Email, Discord, Telegram
   - Rate limiting
   - Delivery tracking

Data Flow:
Price API → Monitor → Queue → Rule Engine → Notifier → User

[Full design document...]
```

### Example 3: Code Review

**Request**:
```
Have the Code Reviewer agent review the premium_hunter.py file.
Focus on:
- Code quality
- Security
- Performance
- Best practices
```

**Agent Output**:
```
## CODE REVIEW REPORT

File: premium_hunter.py
Score: 85/100
Status: APPROVED (with minor suggestions)

### Strengths
- Clean, readable code
- Good error handling
- Proper SQL parameterization

### 🟡 Medium Issues
- Large function at line 48 (consider splitting)
- Cache TTL could be configurable

### 🟢 Recommendations
- Add type hints
- Extract magic numbers to constants

[Full review...]
```

---

## Summary

### Key Takeaways

1. **Agents are markdown prompts** - Simple and effective
2. **QA Tester is MANDATORY** - Never skip testing
3. **Standard workflows exist** - Follow them
4. **Agents collaborate** - Use multiple when needed
5. **Keep evolving** - Add agents as needed

### Quick Reference

- **Location**: `.claude/agents/`
- **How to Use**: "Use the [Agent Name] agent to [task]"
- **Mandatory**: QA Tester before delivery
- **Template**: See "Creating New Agents" section
- **Help**: See [agents/README.md](agents/README.md)

---

**Remember**: Good agents make good code great! 🤖✨
