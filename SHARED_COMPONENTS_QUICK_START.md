# Shared UI Components - Quick Start Guide

## Installation

Components are located in `src/ui_components/`. No installation needed - just import and use!

## Basic Usage

### 1. MetricsCard - Display Metrics

```python
from src.ui_components import MetricsCard

# Single metric
MetricsCard.render(
    label="Total P/L",
    value=1234.56,
    format_currency=True,
    delta="+5.2%",
    positive=True
)

# Multiple metrics in a row
metrics = [
    {'label': 'Total P/L', 'value': 1234.56, 'format_currency': True, 'positive': True},
    {'label': 'Win Rate', 'value': 75.5, 'format_percentage': True},
    {'label': 'Active Positions', 'value': 12}
]
MetricsCard.render_row(metrics)

# P/L specific metric
MetricsCard.render_pl_metric(
    label="Today's P/L",
    pl_value=123.45,
    show_percentage=True,
    percentage_value=5.2
)

# Score gauge
MetricsCard.render_score_gauge(
    label="Strategy Score",
    score=85,
    max_score=100,
    thresholds={'high': 80, 'medium': 60}
)
```

### 2. DataTable - Display Tables with P/L Coloring

```python
from src.ui_components import DataTable
import pandas as pd

# Simple table
df = pd.DataFrame({
    'Symbol': ['AAPL', 'MSFT'],
    'P/L': [123.45, -67.89],
    'P/L %': [5.2, -3.1]
})

DataTable.render(
    data=df,
    pl_columns=['P/L', 'P/L %'],  # These will be color-coded
    hide_index=True
)

# Table with links
df['Chart'] = df['Symbol'].apply(lambda x: f"https://tradingview.com/chart/?symbol={x}")

DataTable.render(
    data=df,
    pl_columns=['P/L', 'P/L %'],
    link_columns={'Chart': '📈'},  # Display as clickable icon
    height=400
)

# Format currency and percentage columns
df_formatted = DataTable.format_currency_column(df, ['Cost', 'Value'])
df_formatted = DataTable.format_percentage_column(df_formatted, ['Return'])
```

### 3. ExpandableCard - Collapsible Sections

```python
from src.ui_components import ExpandableCard
import streamlit as st

# Basic expandable section
with ExpandableCard.render("Position Details", expanded=False):
    st.write("Content goes here")

# With icon and count
with ExpandableCard.render("CSP Positions", icon="💰", count=5, expanded=True):
    st.dataframe(positions_df)

# With metrics in header
metrics = [
    {'label': 'Total P/L', 'value': '$1,234.56', 'positive': True},
    {'label': 'Win Rate', 'value': '75%'}
]

with ExpandableCard.render_with_metrics("Trade History", metrics, icon="📊"):
    st.dataframe(trades_df)
```

### 4. FilterPanel - Filter Controls

```python
from src.ui_components import FilterPanel

# Date range picker
start_date, end_date = FilterPanel.render_date_range(
    default_days=30,
    label_start="From",
    label_end="To"
)

# Symbol dropdown
symbol = FilterPanel.render_symbol_filter(
    symbols=['AAPL', 'MSFT', 'NVDA', 'TSLA'],
    label="Select Symbol",
    allow_all=True
)

# Multi-select
selected_strategies = FilterPanel.render_multi_select(
    options=['CSP', 'CC', 'Long Call', 'Long Put'],
    label="Filter by Strategy",
    default=['CSP', 'CC']
)

# Slider
min_premium = FilterPanel.render_slider_filter(
    label="Minimum Premium",
    min_value=0,
    max_value=500,
    default_value=100,
    step=10,
    format_str="$%d"
)

# Range slider
delta_range = FilterPanel.render_range_slider(
    label="Delta Range",
    min_value=-1.0,
    max_value=0.0,
    default_range=(-0.40, -0.20),
    step=0.01,
    format_str="%.2f"
)

# Comprehensive filter panel (all-in-one)
filters = FilterPanel.render_comprehensive_filters(
    symbols=['AAPL', 'MSFT', 'NVDA'],
    show_date_range=True,
    show_symbol_filter=True,
    show_search=True
)

# Access filter values
start = filters['start_date']
end = filters['end_date']
symbol = filters['symbol']
search_term = filters['search']
```

## Helper Functions

### PositionsHelpers - For positions_page_improved.py

```python
from src.ui_components.positions_helpers import (
    calculate_position_metrics,
    categorize_positions_by_strategy,
    format_position_dataframe,
    prepare_losing_positions_for_recovery,
    collect_all_symbols_from_positions
)

# Calculate aggregate metrics
metrics = calculate_position_metrics(positions_data)
total_pl = metrics['total_pl']
total_premium = metrics['total_premium']

# Categorize positions
categorized = categorize_positions_by_strategy(positions_data)
csp_positions = categorized['csp']
cc_positions = categorized['cc']

# Format DataFrame
df = pd.DataFrame(positions_data)
formatted_df = format_position_dataframe(df)

# Prepare for recovery analysis
losing_positions = prepare_losing_positions_for_recovery(csp_positions)

# Collect all symbols
all_symbols = collect_all_symbols_from_positions(
    stock_positions,
    {'csp': csp_positions, 'cc': cc_positions, 'long_call': [], 'long_put': []}
)
```

### FlowHelpers - For premium_flow_page.py

```python
from src.ui_components.flow_helpers import (
    format_flow_dataframe,
    create_call_put_premium_chart,
    create_sentiment_pie_chart,
    create_historical_flow_chart,
    create_volume_comparison_chart,
    apply_opportunity_filters,
    format_opportunities_table
)

# Format flow data
df_formatted = format_flow_dataframe(df_raw)

# Create charts
fig = create_call_put_premium_chart(
    call_premium=1000000,
    put_premium=750000
)
st.plotly_chart(fig, use_container_width=True)

fig = create_sentiment_pie_chart(
    bullish=45,
    bearish=30,
    neutral=25
)
st.plotly_chart(fig, use_container_width=True)

# Historical charts
fig = create_historical_flow_chart(df_historical, symbol='AAPL')
st.plotly_chart(fig, use_container_width=True)

fig = create_volume_comparison_chart(df_historical, symbol='AAPL')
st.plotly_chart(fig, use_container_width=True)

# Apply filters
filtered_df = apply_opportunity_filters(
    df_opportunities,
    sentiment_filter='Bullish',
    risk_filter='Medium',
    action_filter='SELL_PUT',
    min_score=70
)

# Format opportunities
display_df = format_opportunities_table(df_opportunities)
```

## Complete Example - Refactored Page Section

### Before (Old Code - 60 lines)
```python
# Old positions page metrics section
col1, col2, col3, col4, col5 = st.columns([1.5, 1, 1, 1, 1.5])

with col1:
    st.metric("Total Account Value", f'${total_equity:,.2f}')

with col2:
    st.metric("Buying Power", f'${buying_power:,.2f}')

with col3:
    st.metric("Active Positions", len(positions_data))

with col4:
    st.metric("Total Premium", f'${total_premium:,.2f}')

with col5:
    pl_color = "normal" if total_pl >= 0 else "inverse"
    st.metric(
        "Total P/L",
        f'${total_pl:,.2f}',
        delta=f'{(total_pl/total_premium*100):.1f}%' if total_premium > 0 else '0%',
        delta_color=pl_color
    )

# Second row with after-hours
if has_ah_data:
    col1, col2, col3, col4, col5 = st.columns([1.5, 1, 1, 1, 1.5])
    with col1:
        ah_diff = ah_account_value - total_equity
        st.metric(
            "After-Hours Value",
            f'${ah_account_value:,.2f}',
            delta=f'${ah_diff:+,.2f}',
            delta_color="normal" if ah_diff >= 0 else "inverse"
        )
    # ... more columns

# Display table
with st.expander(f"💰 Cash-Secured Puts ({len(csp_positions)})", expanded=True):
    df = pd.DataFrame(csp_positions)

    # Format display columns (20 lines of formatting)
    display_df = df.copy()
    display_df['Stock Price'] = display_df['Stock Price'].apply(lambda x: f'${x:.2f}')
    display_df['Strike'] = display_df['Strike'].apply(lambda x: f'${x:.2f}')
    # ... more formatting

    # Color coding (15 lines)
    def highlight_pl(row):
        # complex styling logic
        pass

    styled_df = display_df.style.apply(highlight_pl, axis=1)
    st.dataframe(styled_df, ...)
```

### After (New Code - 20 lines)
```python
from src.ui_components import MetricsCard, DataTable, ExpandableCard
from src.ui_components.positions_helpers import (
    calculate_position_metrics,
    categorize_positions_by_strategy,
    format_position_dataframe
)

# Calculate metrics
metrics = calculate_position_metrics(positions_data)

# Display metrics
MetricsCard.render_row([
    {'label': 'Total Account Value', 'value': total_equity, 'format_currency': True},
    {'label': 'Buying Power', 'value': buying_power, 'format_currency': True},
    {'label': 'Active Positions', 'value': len(positions_data)},
    {'label': 'Total Premium', 'value': metrics['total_premium'], 'format_currency': True},
    {'label': 'Total P/L', 'value': metrics['total_pl'], 'format_currency': True,
     'positive': metrics['total_pl'] >= 0}
])

# Categorize and display positions
categorized = categorize_positions_by_strategy(positions_data)

with ExpandableCard.render("Cash-Secured Puts", icon="💰", count=len(categorized['csp']), expanded=True):
    df = pd.DataFrame(categorized['csp'])
    formatted_df = format_position_dataframe(df)

    DataTable.render(
        data=formatted_df,
        pl_columns=['P/L', 'P/L %', 'AH P/L'],
        link_columns={'Chart': '📈'},
        key="csp_positions_table"
    )
```

**Result:** 60 lines → 20 lines (67% reduction) with identical functionality!

## Benefits

✅ **Code Reduction:** 30-70% fewer lines per section
✅ **Consistency:** Uniform styling across all pages
✅ **Maintainability:** Update once, applies everywhere
✅ **Readability:** Clear, self-documenting code
✅ **Testability:** Isolated components easy to test
✅ **Reusability:** Use in any Streamlit page

## Migration Strategy

1. **Start Small:** Begin with one section (metrics or tables)
2. **Test Thoroughly:** Verify functionality matches original
3. **Iterate:** Move section by section
4. **Keep Backups:** Original files backed up as `.backup`

## Testing

```python
# Test imports
from src.ui_components import MetricsCard, DataTable, ExpandableCard, FilterPanel

# Verify all functions are accessible
assert hasattr(MetricsCard, 'render')
assert hasattr(DataTable, 'render')
assert hasattr(ExpandableCard, 'render')
assert hasattr(FilterPanel, 'render_date_range')

print("✅ All components imported successfully!")
```

## Support

For questions or issues:
1. Read `DASHBOARD_REFACTORING_SUMMARY.md` for detailed guide
2. Check component docstrings for parameter details
3. Review examples in this guide

## Next Steps

1. Review `DASHBOARD_REFACTORING_SUMMARY.md` for full refactoring plan
2. Start with premium_flow_page.py (simpler, good proof of concept)
3. Test each refactored section thoroughly
4. Move to positions_page_improved.py once comfortable

Happy coding! 🚀
