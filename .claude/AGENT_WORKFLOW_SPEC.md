# Agent Workflow Specification

## Overview
This document defines the comprehensive agent workflow for the Wheel Strategy Trading Platform. Each change follows a structured process: Plan → Code → Test → Review → Deploy → Recommend.

## Agent Roles & Responsibilities

### 1. **Architect Agent** 🏗️
**Role**: System design and planning
**Triggers**:
- New feature requests
- System redesign needs
- Performance issues
- Architecture reviews

**Responsibilities**:
- Analyze requirements
- Create high-level design
- Define component interactions
- Identify potential issues
- Create implementation plan

**Outputs**:
- Architecture diagrams (text-based)
- Component specifications
- Data flow descriptions
- Todo list with phases

---

### 2. **Planning Agent** 📋
**Role**: Break down work into actionable tasks
**Triggers**:
- After architect completes design
- Complex multi-step features
- User requests with unclear scope

**Responsibilities**:
- Create detailed todo lists
- Define task dependencies
- Estimate complexity
- Identify risks
- Define success criteria

**Outputs**:
- Detailed todo list with priorities
- Dependency graph (text)
- Risk assessment
- Testing requirements

---

### 3. **Python Pro Agent** 🐍
**Role**: Write high-quality Python code
**Triggers**:
- Implementation tasks from planner
- Bug fixes
- Code refactoring
- Performance optimization

**Responsibilities**:
- Write clean, idiomatic Python
- Follow PEP 8 standards
- Add docstrings and comments
- Handle edge cases
- Implement error handling

**Outputs**:
- Python code files
- Unit tests
- Documentation updates

---

### 4. **Database Optimizer Agent** 🗄️
**Role**: Design and optimize database operations
**Triggers**:
- Schema changes
- Query performance issues
- Data modeling tasks
- Database migrations

**Responsibilities**:
- Design efficient schemas
- Optimize SQL queries
- Create indexes
- Handle migrations
- Ensure data integrity

**Outputs**:
- Schema definitions
- Migration scripts
- Optimized queries
- Performance reports

---

### 5. **Frontend Developer Agent** 🎨
**Role**: Build Streamlit UI components
**Triggers**:
- Dashboard changes
- New UI features
- UX improvements
- Visualization needs

**Responsibilities**:
- Create responsive layouts
- Implement data visualization
- Ensure UX best practices
- Handle user interactions
- Optimize rendering

**Outputs**:
- Streamlit components
- CSS/styling
- Interactive widgets
- User flow documentation

---

### 6. **QA/Testing Agent** ✅
**Role**: Test all changes before delivery
**Triggers**:
- ALWAYS after code changes
- Before user delivery
- After bug fixes
- Scheduled testing runs

**Responsibilities**:
- Run automated tests
- Check for runtime errors
- Verify functionality
- Test edge cases
- Performance testing
- Check logs for errors

**Outputs**:
- Test results report
- Error logs
- Performance metrics
- Pass/fail status

**Testing Checklist**:
```python
# For each change:
1. Syntax check (python -m py_compile)
2. Import check (try importing)
3. Run unit tests
4. Check Streamlit dashboard (if UI change)
5. Verify database queries work
6. Check logs for errors
7. Test with sample data
8. Verify no breaking changes
```

---

### 7. **Code Reviewer Agent** 🔍
**Role**: Review code quality and best practices
**Triggers**:
- After QA testing passes
- Before merging changes
- Periodic code audits

**Responsibilities**:
- Check code quality
- Verify best practices
- Identify security issues
- Suggest improvements
- Ensure documentation

**Outputs**:
- Code review report
- Improvement suggestions
- Security findings
- Documentation gaps

---

### 8. **Error Detective Agent** 🕵️
**Role**: Debug production issues
**Triggers**:
- User reports errors
- Exception in logs
- Unexpected behavior
- Performance degradation

**Responsibilities**:
- Analyze error logs
- Trace stack traces
- Identify root cause
- Propose fixes
- Prevent recurrence

**Outputs**:
- Root cause analysis
- Fix recommendations
- Prevention strategies

---

### 9. **Performance Engineer Agent** ⚡
**Role**: Optimize system performance
**Triggers**:
- Slow queries
- High memory usage
- Long response times
- Scalability concerns

**Responsibilities**:
- Profile code execution
- Optimize bottlenecks
- Implement caching
- Optimize queries
- Reduce memory usage

**Outputs**:
- Performance report
- Optimization recommendations
- Benchmark results

---

### 10. **Documentation Agent** 📚
**Role**: Maintain comprehensive documentation
**Triggers**:
- New features added
- API changes
- User requests help
- System updates

**Responsibilities**:
- Update README files
- Write API documentation
- Create user guides
- Document workflows
- Maintain changelog

**Outputs**:
- Updated documentation
- User guides
- API references
- Architecture docs

---

### 11. **Innovation Agent** 💡
**Role**: Recommend future improvements
**Triggers**:
- After feature completion
- Periodic reviews
- User feedback
- Market research

**Responsibilities**:
- Research best practices
- Suggest new features
- Identify opportunities
- Stay current with trends
- Propose innovations

**Outputs**:
- Feature recommendations
- Research findings
- Improvement roadmap
- Competitive analysis

---

## Standard Workflow

### Phase 1: Planning
```
User Request
    ↓
Architect Agent (if complex)
    ↓
Planning Agent
    ↓
Create Todo List
```

### Phase 2: Implementation
```
Todo Item Selected
    ↓
Appropriate Specialist Agent
    (Python Pro, Database Optimizer, Frontend Developer, etc.)
    ↓
Code Written
```

### Phase 3: Quality Assurance
```
Code Complete
    ↓
QA/Testing Agent (MANDATORY)
    ↓
Tests Pass?
    ├─ NO → Error Detective Agent → Fix → Retest
    └─ YES → Continue
```

### Phase 4: Review
```
Tests Passed
    ↓
Code Reviewer Agent
    ↓
Review Pass?
    ├─ NO → Python Pro fixes issues → Retest
    └─ YES → Continue
```

### Phase 5: Deployment
```
Review Passed
    ↓
Deploy Changes
    ↓
Verify in Production
    ↓
Update Documentation Agent
```

### Phase 6: Future Planning
```
Feature Complete
    ↓
Innovation Agent
    ↓
Recommend Improvements
    ↓
Add to Backlog
```

---

## Workflow Examples

### Example 1: Simple Bug Fix
```
1. User reports error
2. Error Detective identifies issue
3. Python Pro implements fix
4. QA Agent tests fix
5. Code Reviewer checks quality
6. Deploy
7. Documentation Agent updates changelog
```

### Example 2: New Feature
```
1. User requests feature
2. Architect designs solution
3. Planning Agent creates tasks
4. Python Pro + Frontend Developer implement
5. Database Optimizer handles DB changes
6. QA Agent comprehensive testing
7. Code Reviewer final check
8. Deploy
9. Documentation Agent writes guide
10. Innovation Agent suggests related improvements
```

### Example 3: Performance Issue
```
1. User reports slow dashboard
2. Performance Engineer profiles code
3. Identifies bottleneck
4. Database Optimizer optimizes query
5. QA Agent verifies performance
6. Deploy
7. Performance Engineer monitors
```

---

## Agent Invocation Rules

### ALWAYS invoke QA Agent when:
- Writing or modifying code
- Making database changes
- Updating UI components
- Fixing bugs
- Before delivering to user

### ALWAYS invoke Code Reviewer when:
- Implementing new features
- Major refactoring
- Security-sensitive code
- Before production deploy

### Invoke Architect when:
- New major feature
- System redesign
- Unclear requirements
- Complex integrations

### Invoke Performance Engineer when:
- Response time > 3 seconds
- Database queries > 1 second
- Memory usage concerns
- Scalability planning

### Invoke Innovation Agent:
- After completing features
- Quarterly reviews
- User requests "make it better"
- Competitive pressure

---

## Quality Gates

### Gate 1: Syntax & Imports
- Code must parse without errors
- All imports must resolve
- No obvious syntax issues

### Gate 2: Functional Testing
- Feature works as expected
- Edge cases handled
- Error messages clear
- No crashes

### Gate 3: Performance
- Queries < 1 second
- Page load < 3 seconds
- Memory usage reasonable
- No resource leaks

### Gate 4: Code Quality
- Follows Python best practices
- Properly documented
- Error handling present
- No security issues

### Gate 5: User Experience
- UI is intuitive
- Data is clear
- No confusing errors
- Meets requirements

---

## Continuous Improvement Cycle

```
Deploy Feature
    ↓
Monitor Usage & Performance
    ↓
Collect User Feedback
    ↓
Innovation Agent Analysis
    ↓
Planning Agent Roadmap
    ↓
Implement Improvements
    ↓
Repeat
```

---

## Emergency Procedures

### Critical Production Error
```
1. Error Detective (immediate analysis)
2. Identify root cause
3. Python Pro (hotfix)
4. QA Agent (quick test)
5. Deploy immediately
6. Full retrospective with Code Reviewer
7. Prevent recurrence
```

### Performance Emergency
```
1. Performance Engineer (immediate profiling)
2. Identify bottleneck
3. Database Optimizer (if DB issue)
4. Implement quick fix
5. QA Agent verify
6. Deploy
7. Plan long-term solution
```

---

## Success Metrics

### Code Quality
- All tests pass
- No runtime errors
- Code review score > 90%
- Documentation complete

### Performance
- Response time < 3s
- Query time < 1s
- 99.9% uptime
- No memory leaks

### User Satisfaction
- Features work as expected
- No user-reported errors
- Positive feedback
- Feature adoption

---

## Agent Communication Protocol

### Standard Format
```
Agent: [Name]
Status: [Starting|In Progress|Complete|Failed]
Task: [Description]
Findings: [Key discoveries]
Outputs: [Deliverables]
Next Step: [Recommendation]
```

### Handoff Format
```
From: [Agent Name]
To: [Next Agent]
Context: [What was done]
Deliverables: [Files/results]
Action Required: [What to do next]
Priority: [High|Medium|Low]
```

---

## Future Enhancements

### Planned Agent Additions
1. **Security Auditor Agent** - Continuous security scanning
2. **ML Ops Agent** - If we add ML features
3. **API Integration Agent** - External service management
4. **Cost Optimizer Agent** - Monitor and optimize costs
5. **User Analytics Agent** - Track usage patterns

### Workflow Improvements
1. Automated agent orchestration
2. Parallel agent execution
3. Smart agent selection based on task type
4. Learning from past successes/failures
5. Automated rollback on failures

---

## Implementation Notes

### Current Implementation
- Agents invoked via Task tool
- Manual workflow orchestration
- Documentation-based coordination
- Human-in-the-loop for critical decisions

### Future Vision
- Automated workflow engine
- Agent collaboration protocols
- Continuous deployment pipeline
- Self-healing systems
- Predictive maintenance

---

**Last Updated**: 2025-10-27
**Version**: 1.0
**Status**: Active
