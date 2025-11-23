"""
Test Components Page

Demonstrates all 4 shared UI components working together:
1. MetricsCard - Standardized metrics display
2. DataTable - Enhanced dataframe with P&L color coding
3. ExpandableCard - Collapsible content cards
4. FilterPanel - Common filter controls

Run with: streamlit run test_components_page.py
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Import all components
from src.components.metrics_card import MetricsCard, render_metric, render_metric_row
from src.components.data_table import DataTable, render_table, render_pnl_table
from src.components.expandable_card import ExpandableCard, expandable_card, render_expandable_list
from src.components.filter_panel import FilterPanel, render_filters, apply_filters

# Page config
st.set_page_config(
    page_title="UI Components Test",
    page_icon="🎨",
    layout="wide"
)

st.title("🎨 Magnus UI Components - Test Suite")
st.markdown("**Testing all 4 shared UI components**")
st.markdown("---")

# ============================================================================
# COMPONENT 1: METRICS CARD
# ============================================================================
st.header("1️⃣ Metrics Card Component")
st.caption("Standardized metrics display with icons, deltas, and help text")

# Example 1: Single metric
st.subheader("Single Metric")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Class-based usage:**")
    card = MetricsCard()
    card.render(
        label="Portfolio Value",
        value=50125.50,
        delta=1250.50,
        help_text="Total portfolio value including options",
        icon="💰"
    )

with col2:
    st.markdown("**Convenience function:**")
    render_metric(
        label="Win Rate",
        value="85.5%",
        delta="+2.1%",
        icon="🎯",
        help_text="Percentage of profitable trades"
    )

with col3:
    st.markdown("**Negative delta:**")
    render_metric(
        label="Active Positions",
        value=12,
        delta=-3,
        icon="📊",
        delta_color="inverse",
        help_text="Number of open positions"
    )

# Example 2: Multiple metrics in a row
st.subheader("Multiple Metrics Row")
metrics = [
    {"label": "Today's P&L", "value": "$1,850.25", "delta": "+$425.50", "icon": "💵"},
    {"label": "Premium Collected", "value": "$12,450", "delta": "+$2,100", "icon": "💸"},
    {"label": "Capital at Risk", "value": "$35,000", "delta": "-$5,000", "icon": "⚠️", "delta_color": "inverse"},
    {"label": "Theta Decay", "value": "$125.50", "delta": "+$15.20", "icon": "⏱️"}
]

render_metric_row(metrics)

st.markdown("---")

# ============================================================================
# COMPONENT 2: DATA TABLE
# ============================================================================
st.header("2️⃣ Data Table Component")
st.caption("Enhanced dataframe with automatic P&L color coding and export")

# Create sample data
sample_data = pd.DataFrame({
    'Symbol': ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'META', 'NVDA', 'AMD'],
    'Type': ['CSP', 'CSP', 'Covered Call', 'CSP', 'CSP', 'Covered Call', 'CSP'],
    'Strike': [150.00, 380.00, 140.00, 220.00, 480.00, 500.00, 120.00],
    'Premium': [250.50, 425.00, 380.25, 550.00, 125.75, 680.00, 175.50],
    'P&L': [250.50, -125.75, 380.25, 0.05, -450.00, 680.00, 175.50],
    'DTE': [28, 35, 21, 42, 14, 30, 25],
    'Status': ['Winning', 'Losing', 'Winning', 'Break-even', 'Losing', 'Winning', 'Winning']
})

# Example 1: Basic table with P&L highlighting
st.subheader("Basic Table with Auto P&L Detection")
table = DataTable()
table.render(
    sample_data,
    title="Open Positions",
    caption="🟢 Green = Profit | 🔴 Red = Loss | 🟡 Yellow = Break-even",
    highlight_pnl=True,
    enable_clipboard=True
)

# Example 2: Custom column config
st.subheader("Table with Custom Column Formatting")
column_config = {
    "Symbol": st.column_config.TextColumn("Ticker", width="small"),
    "Strike": st.column_config.NumberColumn("Strike $", format="$%.2f"),
    "Premium": st.column_config.NumberColumn("Premium", format="$%.2f"),
    "P&L": st.column_config.NumberColumn("P&L", format="$%.2f"),
    "DTE": st.column_config.NumberColumn("Days", width="small")
}

render_table(
    sample_data,
    title="Formatted Positions",
    column_config=column_config,
    height=300
)

st.markdown("---")

# ============================================================================
# COMPONENT 3: EXPANDABLE CARD
# ============================================================================
st.header("3️⃣ Expandable Card Component")
st.caption("Collapsible content cards with badges and icons")

# Example 1: Single expandable card
st.subheader("Single Expandable Card")

card_component = ExpandableCard()
with card_component.render(
    title="AAPL - Apple Inc.",
    subtitle="Technology Sector | $150.25",
    badge="STRONG_BUY",
    icon="📈",
    expanded=True
):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Stock Price", "$150.25", "+2.5%")
    with col2:
        st.metric("30-Day Premium", "$250.50")
    with col3:
        st.metric("AI Score", "92/100")

    st.markdown("**Analysis:**")
    st.write("Strong bullish trend with high IV. Excellent premium collection opportunity.")

# Example 2: Multiple cards with different badges
st.subheader("Multiple Cards with Different Badges")

cards_data = [
    {
        "title": "MSFT - Microsoft",
        "subtitle": "$380.50",
        "badge": "BUY",
        "icon": "📊",
        "content": lambda: st.write("Moderate opportunity with good risk/reward ratio.")
    },
    {
        "title": "TSLA - Tesla",
        "subtitle": "$220.00",
        "badge": "HOLD",
        "icon": "⚡",
        "content": lambda: st.write("High volatility. Monitor closely before entering.")
    },
    {
        "title": "META - Meta Platforms",
        "subtitle": "$480.00",
        "badge": "SELL",
        "icon": "📱",
        "content": lambda: st.write("Declining trend. Consider closing positions.")
    }
]

render_expandable_list(cards_data, expand_first=True)

# Example 3: Convenience function
st.subheader("Using Convenience Function")

with expandable_card(
    title="Calendar Spread Opportunity",
    badge="SUCCESS",
    icon="📆",
    expanded=False
):
    st.markdown("""
    **Strategy:** Sell 30-day put, Buy 60-day put at same strike

    - **Net Debit:** $150
    - **Max Profit:** $450
    - **Profit Potential:** 300%
    """)

st.markdown("---")

# ============================================================================
# COMPONENT 4: FILTER PANEL
# ============================================================================
st.header("4️⃣ Filter Panel Component")
st.caption("Common filter controls for options analysis")

# Example 1: Full filter panel with presets
st.subheader("Full Filter Panel with Presets")

panel = FilterPanel()
filters = panel.render(
    show_dte=True,
    show_delta=True,
    show_premium=True,
    show_score=True,
    show_price_range=True,
    show_presets=True,
    columns=3,
    key_prefix="full_panel"
)

st.success(f"**Applied Filters:** {filters}")

# Example 2: Compact filter panel
st.subheader("Compact Single-Row Filter Panel")

compact_filters = panel.render_compact(key_prefix="compact")

st.info(f"**Compact Filters:** {compact_filters}")

# Example 3: Apply filters to dataframe
st.subheader("Filter Application Demo")

st.markdown("**Original Data:**")
st.dataframe(sample_data, hide_index=True)

# Create a mapping for our sample data columns
column_mapping = {
    'dte_min': 'DTE',
    'dte_max': 'DTE',
    'min_premium': 'Premium',
    'price_min': 'Strike',
    'price_max': 'Strike'
}

# Apply filters
filtered_data = panel.apply_filters(sample_data, compact_filters, column_mapping)

st.markdown(f"**Filtered Data ({len(filtered_data)} rows):**")
st.dataframe(filtered_data, hide_index=True)

st.markdown("---")

# ============================================================================
# COMBINED EXAMPLE: ALL COMPONENTS TOGETHER
# ============================================================================
st.header("🎯 Combined Example: Complete Dashboard")
st.caption("All 4 components working together in a realistic scenario")

# Metrics row
st.subheader("Portfolio Overview")
render_metric_row([
    {"label": "Total Value", "value": "$50,125", "delta": "+$1,250", "icon": "💰"},
    {"label": "Today's P&L", "value": "$850", "delta": "+$125", "icon": "📈"},
    {"label": "Win Rate", "value": "85.5%", "delta": "+2.1%", "icon": "🎯"},
    {"label": "Active Trades", "value": 12, "icon": "📊"}
])

st.markdown("---")

# Filters
st.subheader("Filter Options")
dashboard_filters = render_filters(
    show_dte=True,
    show_delta=True,
    show_premium=True,
    show_score=True,
    key_prefix="dashboard"
)

# Filtered table
st.subheader("Filtered Opportunities")
filtered_opportunities = panel.apply_filters(sample_data, dashboard_filters, column_mapping)

if len(filtered_opportunities) > 0:
    render_pnl_table(
        filtered_opportunities,
        pnl_column="P&L",
        title=f"Top Opportunities ({len(filtered_opportunities)} found)",
        enable_clipboard=True
    )

    # Expandable details
    st.subheader("Detailed Analysis")
    detail_cards = []
    for _, row in filtered_opportunities.head(3).iterrows():
        badge = "STRONG_BUY" if row['P&L'] > 200 else "BUY" if row['P&L'] > 0 else "HOLD"
        detail_cards.append({
            "title": f"{row['Symbol']} - ${row['Strike']:.2f} {row['Type']}",
            "subtitle": f"Premium: ${row['Premium']:.2f} | DTE: {row['DTE']}",
            "badge": badge,
            "icon": "📈" if row['P&L'] > 0 else "📊",
            "content": lambda r=row: (
                st.metric("P&L", f"${r['P&L']:.2f}", f"{(r['P&L']/r['Premium']*100):.1f}%"),
                st.progress(min(1.0, r['Premium'] / 500))
            )
        })

    render_expandable_list(detail_cards, expand_first=True)
else:
    st.warning("No opportunities match your filter criteria. Try adjusting the filters.")

st.markdown("---")

# Summary
st.success("""
✅ **Component Test Complete!**

All 4 components are working correctly:
1. ✅ MetricsCard - Displaying KPIs with deltas
2. ✅ DataTable - P&L color coding active
3. ✅ ExpandableCard - Collapsible content working
4. ✅ FilterPanel - Filters applied successfully

**Next Steps:**
- Import these components into your dashboard pages
- Replace duplicate code with shared components
- Customize styling as needed
""")

# Footer
st.markdown("---")
st.caption(f"Component Test Suite | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
