# Coding Guidelines for Magnus Dashboard

## UI/UX Preferences

### ❌ DO NOT USE Horizontal Lines
**NEVER** add horizontal lines (`st.markdown("---")`) in the dashboard UI.

**Why:** The user prefers clean, uncluttered interfaces without visual separators.

**Instead:**
- Use expanders to group content
- Use spacing with `st.write("")` if needed
- Rely on section headers and visual hierarchy

### ✅ DO USE Expanders
- Use `st.expander()` for collapsible sections
- Set `expanded=False` by default for secondary content
- Set `expanded=True` only for primary/most important sections

### ℹ️ Info Icons for Complex Features
- Add hover-tooltip info icons for features that need explanation
- Use HTML with `title` attribute for tooltips
- Example:
```python
st.markdown('<div title="Explanation here">ℹ️</div>', unsafe_allow_html=True)
```

## Code Quality

### Database Queries
- Always use prepared statements with parameterized queries
- Close connections properly with try/finally or context managers
- Use `DISTINCT ON` for getting one row per group efficiently

### Performance
- Load data from database cache when available
- Use background sync for data updates
- Avoid blocking operations in the UI thread

### Error Handling
- Always wrap risky operations in try/except
- Log errors with descriptive messages
- Show user-friendly error messages in UI

## Project-Specific Patterns

### Options Data
- Prefer database cache (stock_premiums table) over live API calls
- Use Robinhood as fallback when Yahoo Finance fails
- Target delta of -0.30 for CSP opportunities (25-35 range acceptable)

### Table Styling
- Match TradingView watchlist table format:
  - Use `st.dataframe()` with `column_config`
  - Set `hide_index=True`
  - Use `use_container_width=True`
  - Format numbers appropriately (currency, percentages)
  - Enable sorting by making headers clickable

### Git Commits
- Use detailed commit messages
- Include problem, solution, and impact
- Add "🤖 Generated with Claude Code" footer
- Include "Co-Authored-By: Claude <noreply@anthropic.com>"

## Remember
- User wants clean, professional UI
- Minimize visual clutter
- Use database for speed
- Provide helpful tooltips for complex features
