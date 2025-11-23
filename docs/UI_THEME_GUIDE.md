# UI Theme System Guide

## Overview

The Magnus Trading Platform now has a unified UI theme system that provides:
- ✅ Consistent colors, typography, and spacing across all pages
- ✅ Reusable components (cards, badges, status boxes)
- ✅ Standardized page configuration
- ✅ Pre-configured Plotly chart templates
- ✅ Easy maintenance and updates

## Quick Start

### Basic Page Setup

Instead of manually configuring each page, use the theme system:

**Before:**
```python
import streamlit as st

st.set_page_config(
    page_title="My Page",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
.stMetric {
    background-color: #f0f2f6;
    padding: 1rem;
}
</style>
""", unsafe_allow_html=True)
```

**After:**
```python
from src.ui_theme import init_page, UIComponents

# Initialize page with theme
theme = init_page("My Page", "📊", "wide")
components = UIComponents(theme)

# Theme CSS is automatically applied!
```

## Components

### Status Boxes

Display success, warning, error, or info messages with consistent styling:

```python
components.success_box("Operation completed successfully!")
components.warning_box("Please review these settings")
components.error_box("Failed to connect to database")
components.info_box("New features available")
```

**Output:**
- ✅ Green box with checkmark for success
- ⚠️ Yellow box with warning icon
- ❌ Red box with error icon
- ℹ️ Blue box with info icon

### Cards

Create styled card components:

```python
components.card(
    title="Portfolio Summary",
    content="Your current holdings and performance metrics"
)
```

### Badges

Add status badges inline:

```python
st.markdown(
    f"Status: {components.status_badge('success', 'Active')}",
    unsafe_allow_html=True
)
```

Available badge types: `success`, `warning`, `error`, `info`

### Live Indicators

Add animated live indicators:

```python
st.markdown(
    components.live_indicator("LIVE TRADING"),
    unsafe_allow_html=True
)
```

Creates a pulsing red dot animation before the text.

## Colors

Access theme colors consistently:

```python
theme = get_theme()

# Primary colors
theme.colors.primary         # #4F46E5 (Indigo)
theme.colors.secondary       # #10B981 (Green)
theme.colors.accent          # #F59E0B (Amber)

# Status colors
theme.colors.success         # Green
theme.colors.warning         # Amber
theme.colors.error           # Red
theme.colors.info            # Blue

# Background colors
theme.colors.background
theme.colors.background_secondary
theme.colors.background_tertiary

# Text colors
theme.colors.text_primary
theme.colors.text_secondary
theme.colors.text_tertiary
```

## Typography

Access consistent typography:

```python
# Font sizes
theme.typography.size_xs     # 12px
theme.typography.size_sm     # 14px
theme.typography.size_base   # 16px
theme.typography.size_lg     # 18px
theme.typography.size_xl     # 20px

# Font weights
theme.typography.weight_normal
theme.typography.weight_medium
theme.typography.weight_semibold
theme.typography.weight_bold
```

## Spacing

Use consistent spacing:

```python
theme.spacing.xs    # 4px
theme.spacing.sm    # 8px
theme.spacing.base  # 16px
theme.spacing.md    # 24px
theme.spacing.lg    # 32px
theme.spacing.xl    # 48px
```

## Plotly Charts

Get consistent chart styling:

```python
import plotly.graph_objects as go

# Get chart template
template = theme.get_chart_template()

# Create chart with theme
fig = go.Figure(data=[...])
fig.update_layout(**template['layout'])
```

The template includes:
- Consistent color palette
- Grid styling
- Font settings
- Background colors
- Hover styling

## Metrics

Standard Streamlit metrics automatically get themed styling:

```python
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Value", "$1,234.56", "+5.2%")
with col2:
    st.metric("Active Trades", "12", "-2")
with col3:
    st.metric("Win Rate", "68%", "+3%")
```

Metrics automatically have:
- Gray background with border
- Consistent padding
- Styled delta indicators

## Buttons

Buttons are automatically themed:

```python
# Primary button
if st.button("Execute Trade", type="primary"):
    pass

# Secondary button
if st.button("View Details", type="secondary"):
    pass

# Default button
if st.button("Cancel"):
    pass
```

Features:
- Hover effects with border color change
- Smooth transitions
- Lift effect on hover

## Sidebar

Sidebar automatically gets themed styling:
- Light gray background
- Hover effects on navigation buttons
- Consistent spacing

## Data Tables

DataFrames automatically get themed:
- Header with primary color background
- Alternating row colors
- Hover effect on rows
- Rounded corners

```python
import pandas as pd

df = pd.DataFrame({
    'Symbol': ['AAPL', 'GOOGL', 'MSFT'],
    'Price': [150.00, 2800.00, 300.00]
})

st.dataframe(df)  # Automatically themed!
```

## Migration Guide

### Step 1: Update Imports

Replace:
```python
import streamlit as st

st.set_page_config(page_title="...", page_icon="...", layout="...")
```

With:
```python
from src.ui_theme import init_page, UIComponents

theme = init_page("Page Title", "📊", "wide")
components = UIComponents(theme)
```

### Step 2: Replace Custom CSS

Remove custom CSS blocks like:
```python
st.markdown("""
<style>
.stMetric { ... }
.success-box { ... }
</style>
""", unsafe_allow_html=True)
```

The theme handles this automatically.

### Step 3: Use Components

Replace custom HTML/CSS with components:

**Before:**
```python
st.markdown("""
<div style="background-color: #d4edda; border-left: 4px solid #10B981; padding: 1rem;">
✅ Success message
</div>
""", unsafe_allow_html=True)
```

**After:**
```python
components.success_box("Success message")
```

### Step 4: Update Charts

**Before:**
```python
fig.update_layout(
    font=dict(family="Arial", color="#111827"),
    plot_bgcolor="#FFFFFF",
    # ... many lines of styling
)
```

**After:**
```python
template = theme.get_chart_template()
fig.update_layout(**template['layout'])
```

## Advanced Customization

### Custom Colors

If you need custom colors for specific use cases:

```python
custom_color = "#FF6B6B"  # Your custom color

st.markdown(
    f'<div style="color: {custom_color};">Custom text</div>',
    unsafe_allow_html=True
)
```

### Custom Cards

Create custom card variations:

```python
st.markdown(f'''
<div class="card" style="border-left: 4px solid {theme.colors.primary};">
    <div class="card-header">Featured Card</div>
    <div>Special content here</div>
</div>
''', unsafe_allow_html=True)
```

## Best Practices

1. **Always use `init_page()`** at the start of every page file
2. **Use theme colors** instead of hardcoded hex values
3. **Use components** instead of custom HTML when possible
4. **Keep custom CSS minimal** - extend the theme, don't override it
5. **Test on different screen sizes** - the theme is responsive

## Examples

### Complete Page Example

```python
from src.ui_theme import init_page, UIComponents
import streamlit as st
import pandas as pd

# Initialize page
theme = init_page("Portfolio Dashboard", "💼", "wide")
components = UIComponents(theme)

# Header
st.title("Portfolio Dashboard")
st.markdown(
    components.live_indicator("LIVE"),
    unsafe_allow_html=True
)

# Metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Value", "$125,432", "+$1,234")
with col2:
    st.metric("Day P&L", "+$542", "+0.43%")
with col3:
    st.metric("Open Positions", "8", "-2")
with col4:
    st.metric("Win Rate", "72%", "+5%")

# Status messages
if st.session_state.get('trade_executed'):
    components.success_box("Trade executed successfully!")

# Warning
if risk_level > 0.8:
    components.warning_box("Portfolio risk is elevated")

# Data table
st.subheader("Open Positions")
st.dataframe(positions_df)

# Chart
import plotly.graph_objects as go

fig = go.Figure(data=[...])
template = theme.get_chart_template()
fig.update_layout(**template['layout'])
st.plotly_chart(fig, use_container_width=True)
```

### Custom Component Example

```python
def custom_trade_card(symbol: str, action: str, pnl: float):
    """Custom trade card component"""
    pnl_color = theme.colors.success if pnl > 0 else theme.colors.error

    st.markdown(f'''
    <div class="card">
        <div class="card-header">
            {symbol}
            {components.status_badge('success' if action == 'BUY' else 'error', action)}
        </div>
        <div style="color: {pnl_color}; font-size: {theme.typography.size_xl}; font-weight: {theme.typography.weight_bold};">
            ${pnl:+.2f}
        </div>
    </div>
    ''', unsafe_allow_html=True)

# Usage
custom_trade_card("AAPL", "BUY", 125.50)
```

## Troubleshooting

### Theme not applying

Make sure you call `init_page()` with `apply_theme=True` (default):
```python
theme = init_page("My Page", apply_theme=True)
```

### Custom CSS conflicts

If you have custom CSS that conflicts, apply the theme CSS first, then add custom CSS after:
```python
theme = init_page("My Page")

# Now add custom CSS
st.markdown("""
<style>
/* Your custom CSS */
</style>
""", unsafe_allow_html=True)
```

### Colors not showing

Access colors through the theme object:
```python
theme = init_page("My Page")
print(theme.colors.primary)  # Correct
```

## Support

For issues or questions:
- Check existing pages for examples (dashboard.py, ava_chatbot_page.py)
- Review this guide
- Test in the example page: `python -m src.ui_theme`

## Future Enhancements

Planned features:
- Dark mode toggle
- Multiple color themes (blue, green, purple)
- More component types (modals, tooltips)
- Animated transitions
- Accessibility improvements (WCAG 2.1 AA compliance)
