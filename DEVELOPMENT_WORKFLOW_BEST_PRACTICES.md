# Development Workflow - Best Practices

**Date**: 2025-11-13
**Status**: ACTIVE WORKFLOW STANDARD

---

## PRIMARY RULE: CHECK GITHUB FIRST

**ALWAYS check GitHub for open-source solutions BEFORE building custom implementations.**

This rule was established after spending unnecessary time building custom JavaScript solutions when a perfect open-source component already existed.

---

## Workflow Steps

### 1. Identify the Problem
- Clearly define what you need to accomplish
- Document the specific requirements
- Note any constraints or integration points

### 2. Search for Existing Solutions (REQUIRED FIRST STEP)

**Search Locations** (in order of priority):
1. **GitHub** - Search for:
   - Streamlit components
   - Python packages
   - JavaScript libraries
   - Complete implementations

2. **PyPI** - Search for:
   - Official packages
   - Community components
   - Framework-specific libraries

3. **Reddit** - Check subreddits:
   - r/streamlit
   - r/Python
   - r/webdev

4. **Medium** - Search for:
   - Tutorial articles
   - Implementation guides
   - Best practices

5. **Stack Overflow** - Look for:
   - Similar problems solved
   - Recommended approaches
   - Common patterns

### 3. Evaluate Found Solutions

**Criteria for Selection**:
- ✅ Actively maintained (recent commits/releases)
- ✅ Good documentation
- ✅ Positive community feedback
- ✅ Compatible with current stack
- ✅ Reasonable dependencies
- ✅ Open-source license

**Red Flags**:
- ❌ Abandoned (no updates in 1+ years)
- ❌ No documentation
- ❌ Security vulnerabilities
- ❌ Excessive dependencies
- ❌ Restrictive license

### 4. Only Build Custom If:
- No suitable open-source solution exists
- Existing solutions have deal-breaking limitations
- Requirements are highly specialized
- Integration complexity outweighs benefits

### 5. Document Decision
- Record what was searched
- Note why chosen solution was selected
- Document alternatives considered
- Save installation/setup instructions

---

## Case Study: AVA Chat Interface Send Button

### The Problem:
Send button appearing outside textarea instead of inside at bottom-right corner (Claude-style).

### Failed Approach (4 hours wasted):
1. Attempted CSS wrapper with absolute positioning
2. Tried JavaScript DOM manipulation via st.markdown()
3. Used components.html() with retry logic
4. All attempts failed due to Streamlit's rendering model

### Correct Approach (15 minutes):
1. Searched GitHub: "streamlit custom chat input component button inside textarea"
2. Found `streamlit_custom_input` by Farah-S
3. Installed component from PyPI
4. Replaced custom form with 20 lines of component configuration
5. ✅ Problem solved

### Time Saved:
- Custom approach: 4+ hours of trial and error
- Open-source approach: 15 minutes to find and implement
- **Savings: 3.75 hours**

---

## Search Query Templates

### For Streamlit Components:
```
streamlit [functionality] component
streamlit custom [component type]
streamlit [feature] github
```

### For Python Packages:
```
python [functionality] library
pypi [feature] package
[framework] [functionality] implementation
```

### For JavaScript Libraries:
```
javascript [functionality] library
[framework] [feature] component
vanilla js [functionality]
```

---

## Installation Best Practices

### 1. Check Multiple Package Sources:
- **PyPI**: `pip search [package]` or https://pypi.org
- **Test PyPI**: https://test.pypi.org (for pre-release)
- **GitHub Releases**: Direct from repository
- **Conda**: `conda search [package]`

### 2. Verify Package Integrity:
```bash
# Check package details before installing
pip show [package]

# Install with verification
pip install [package] --no-cache-dir

# Install from specific source
pip install --index-url https://test.pypi.org/simple/ [package]
```

### 3. Document Installation:
```python
# requirements.txt
streamlit_custom_input==0.1.0  # Chat input with embedded button - see DEVELOPMENT_WORKFLOW_BEST_PRACTICES.md
```

---

## Documentation Standards

When using an open-source component:

### 1. Code Comments:
```python
# Using open-source component from https://github.com/user/repo
# Selected because: [reason]
# Alternatives considered: [alternatives]
from package import Component
```

### 2. Create Implementation Doc:
```markdown
# [Component Name] Integration

**Source**: [GitHub URL]
**Version**: [version]
**Installation**: [command]

## Why This Component:
- [Reason 1]
- [Reason 2]

## Alternatives Considered:
- [Alternative 1]: [Why rejected]
- [Alternative 2]: [Why rejected]

## Setup Instructions:
1. [Step 1]
2. [Step 2]
```

### 3. Update Project README:
```markdown
## Third-Party Components

- **streamlit_custom_input** - Chat input with embedded send button
  - Source: https://github.com/Farah-S/streamlit_custom_input
  - Docs: See CLAUDE_INTERFACE_SEND_BUTTON_FIX_COMPLETE.md
```

---

## GitHub Search Tips

### Search Syntax:
```
# Search in repositories
streamlit chat input in:name,description,readme

# Filter by language
streamlit custom component language:python

# Filter by stars
streamlit component stars:>100

# Filter by recent activity
streamlit component pushed:>2024-01-01

# Combine filters
streamlit chat input language:python stars:>10 pushed:>2024-01-01
```

### Search Locations:
1. **Awesome Lists**: Search for "awesome streamlit" or "awesome python"
2. **Topic Tags**: Browse GitHub topics like #streamlit, #component, #chat
3. **Organization Repos**: Check Streamlit's official GitHub org
4. **Developer Profiles**: Search repos by known Streamlit developers

---

## Time Estimation Guidelines

### Before Building Custom:
- Minimum 30 minutes of open-source research
- Check at least 3 different sources
- Evaluate at least 2-3 alternatives
- Document findings even if building custom

### If Building Custom:
- Add 2x time estimate for testing
- Add 1x time estimate for documentation
- Add 0.5x time estimate for maintenance
- **Total = Implementation + 2x Testing + 1x Docs + 0.5x Maintenance**

### If Using Open-Source:
- Installation: 5-15 minutes
- Integration: 15-30 minutes
- Testing: 15-30 minutes
- Documentation: 10-15 minutes
- **Total = ~1 hour average**

---

## Common Mistakes to Avoid

### ❌ DON'T:
- Start coding without searching first
- Assume no solution exists for common problems
- Skip documentation when using open-source
- Ignore security vulnerabilities in dependencies
- Use abandoned packages without vetting
- Copy code without understanding it
- Install packages from unknown sources

### ✅ DO:
- Search multiple sources (GitHub, Reddit, Medium, SO)
- Read package documentation thoroughly
- Check issue tracker for known problems
- Verify package is actively maintained
- Test in isolated environment first
- Document why you chose specific solution
- Keep dependencies updated
- Contribute back to open-source projects

---

## Quality Checklist

Before finalizing an open-source solution:

- [ ] Package actively maintained (commits in last 6 months)
- [ ] Good documentation exists
- [ ] Examples/demos available
- [ ] Reasonable test coverage
- [ ] Clear license (MIT, Apache, BSD preferred)
- [ ] No critical security vulnerabilities
- [ ] Compatible with current Python/framework versions
- [ ] Reasonable dependency count (<10 new dependencies)
- [ ] Positive community feedback (stars, issues, PRs)
- [ ] Author responsive to issues/PRs

---

## Resources

### Streamlit:
- **Official Components**: https://streamlit.io/components
- **Community Components**: https://discuss.streamlit.io/c/community-components
- **GitHub Topic**: https://github.com/topics/streamlit-component

### Python Packages:
- **PyPI**: https://pypi.org
- **Awesome Python**: https://github.com/vinta/awesome-python
- **Python Libraries**: https://github.com/topics/python

### General:
- **Awesome Lists**: https://github.com/topics/awesome
- **GitHub Explore**: https://github.com/explore
- **Libraries.io**: https://libraries.io (package search across ecosystems)

---

## Success Metrics

Track time saved by using open-source solutions:

```markdown
## Time Saved Log

| Date | Problem | Custom Estimate | Open-Source Time | Savings |
|------|---------|----------------|------------------|---------|
| 2025-11-13 | Chat button positioning | 4+ hours | 15 min | 3.75 hrs |
```

---

## Exceptions

Build custom solutions when:

1. **Security/Privacy**: Handling sensitive data that shouldn't use third-party code
2. **Performance**: Open-source solution has unacceptable performance
3. **Licensing**: Open-source license incompatible with project
4. **Maintenance**: Package abandoned and no alternatives exist
5. **Complexity**: Integration overhead exceeds build time
6. **Highly Specific**: Requirements too specialized for general solution

**Document exception reasoning in project docs.**

---

## Review Cadence

### Weekly:
- Review new dependencies added
- Check for security advisories
- Update outdated packages

### Monthly:
- Audit all third-party components
- Verify licenses still compatible
- Check for better alternatives

### Quarterly:
- Full dependency tree audit
- Remove unused dependencies
- Evaluate switching costs for major updates

---

## Conclusion

**The Golden Rule**: Assume someone else has already solved your problem. Search for it FIRST before writing code.

This saves:
- ⏱️ Development time
- 🐛 Debugging effort
- 📚 Documentation work
- 🔧 Maintenance burden
- 💰 Project costs

**When in doubt, search GitHub.**

---

**Status**: ✅ ACTIVE STANDARD
**Applies To**: All development work
**Review**: Quarterly
**Last Updated**: 2025-11-13
