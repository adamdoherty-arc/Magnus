"""
Display calendar spread opportunities in Streamlit
"""

import streamlit as st
import pandas as pd
from typing import List
from .calendar_spread_models import CalendarSpreadOpportunity


def display_calendar_spreads_table(opportunities: List[CalendarSpreadOpportunity]):
    """Display sortable table of calendar spread opportunities"""

    if not opportunities:
        st.info("No calendar spread opportunities found matching criteria")
        return

    st.markdown(f"### 📊 Found {len(opportunities)} Calendar Spread Opportunities")

    # Create DataFrame
    df_data = []
    for opp in opportunities:
        df_data.append({
            'Rank': opp.rank,
            'Symbol': opp.symbol,
            'Stock $': opp.stock_price,
            'Strike': opp.near_strike,
            'Near DTE': opp.near_dte,
            'Far DTE': opp.far_dte,
            'Net Debit': opp.net_debit,
            'Max Profit': opp.max_profit,
            'Profit %': opp.profit_potential * 100,
            'Prob Profit': opp.probability_profit,
            'Theta': opp.net_theta,
            'Liquidity': opp.liquidity_score,
            'Score': opp.opportunity_score,
            'Chart': f"https://www.tradingview.com/chart/?symbol={opp.symbol}"
        })

    df = pd.DataFrame(df_data)

    # Display with column config
    st.dataframe(
        df,
        hide_index=True,
        width='stretch',
        column_config={
            "Rank": st.column_config.NumberColumn("Rank", width="small", help="Ranking by opportunity score"),
            "Symbol": st.column_config.TextColumn("Symbol", width="small"),
            "Stock $": st.column_config.NumberColumn("Stock $", format="$%.2f"),
            "Strike": st.column_config.NumberColumn("Strike", format="$%.2f"),
            "Near DTE": st.column_config.NumberColumn("Near DTE", width="small", help="Days to expiration (near leg)"),
            "Far DTE": st.column_config.NumberColumn("Far DTE", width="small", help="Days to expiration (far leg)"),
            "Net Debit": st.column_config.NumberColumn("Debit", format="$%.2f", help="Cost to open spread"),
            "Max Profit": st.column_config.NumberColumn("Max Profit", format="$%.2f"),
            "Profit %": st.column_config.NumberColumn("Profit %", format="%.1f%%", help="Max profit / net debit"),
            "Prob Profit": st.column_config.ProgressColumn(
                "Prob Profit",
                format="%.0f%%",
                min_value=0,
                max_value=100,
                help="Probability of profit"
            ),
            "Theta": st.column_config.NumberColumn("Theta", format="%.4f", help="Net theta advantage"),
            "Liquidity": st.column_config.ProgressColumn(
                "Liquidity",
                format="%.0f",
                min_value=0,
                max_value=100
            ),
            "Score": st.column_config.ProgressColumn(
                "Score",
                format="%.0f",
                min_value=0,
                max_value=100,
                help="Composite opportunity score"
            ),
            "Chart": st.column_config.LinkColumn("Chart", display_text="📈")
        }
    )

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        avg_profit = sum(o.max_profit for o in opportunities) / len(opportunities)
        st.metric("Avg Max Profit", f"${avg_profit:.2f}")
    with col2:
        avg_prob = sum(o.probability_profit for o in opportunities) / len(opportunities)
        st.metric("Avg Prob Profit", f"{avg_prob:.1f}%")
    with col3:
        avg_score = sum(o.opportunity_score for o in opportunities) / len(opportunities)
        st.metric("Avg Score", f"{avg_score:.0f}/100")
    with col4:
        best_opp = opportunities[0]
        st.metric("Best Opportunity", best_opp.symbol)


def display_spread_details(opportunity: CalendarSpreadOpportunity):
    """Display detailed information about a spread"""

    st.markdown(f"#### {opportunity.symbol} ${opportunity.near_strike} Calendar Spread")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Near-Term Leg (Sell)**")
        st.write(f"- Strike: ${opportunity.near_strike:.2f}")
        st.write(f"- Expiration: {opportunity.near_expiration.strftime('%Y-%m-%d')}")
        st.write(f"- DTE: {opportunity.near_dte} days")
        st.write(f"- Premium: ${opportunity.near_premium:.2f}")
        st.write(f"- IV: {opportunity.near_iv:.1f}%")
        st.write(f"- Theta: {opportunity.near_theta:.4f}")
        st.write(f"- Volume: {opportunity.near_volume}")

    with col2:
        st.markdown("**Far-Term Leg (Buy)**")
        st.write(f"- Strike: ${opportunity.far_strike:.2f}")
        st.write(f"- Expiration: {opportunity.far_expiration.strftime('%Y-%m-%d')}")
        st.write(f"- DTE: {opportunity.far_dte} days")
        st.write(f"- Premium: ${opportunity.far_premium:.2f}")
        st.write(f"- IV: {opportunity.far_iv:.1f}%")
        st.write(f"- Theta: {opportunity.far_theta:.4f}")
        st.write(f"- Volume: {opportunity.far_volume}")

    st.markdown("**Spread Metrics**")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Net Debit", f"${opportunity.net_debit:.2f}")
    with col2:
        st.metric("Max Profit", f"${opportunity.max_profit:.2f}")
    with col3:
        st.metric("Profit Potential", f"{opportunity.profit_potential*100:.1f}%")
    with col4:
        st.metric("Prob Profit", f"{opportunity.probability_profit:.0f}%")

    st.markdown("**Breakeven Range**")
    st.write(f"Lower: ${opportunity.breakeven_lower:.2f}")
    st.write(f"Upper: ${opportunity.breakeven_upper:.2f}")

    st.markdown("**Greeks**")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Net Theta", f"{opportunity.net_theta:.4f}", help="Daily theta advantage")
    with col2:
        st.metric("Net Vega", f"{opportunity.net_vega:.4f}", help="Vega exposure")

    st.markdown("**Quality Metrics**")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Liquidity Score", f"{opportunity.liquidity_score:.0f}/100")
    with col2:
        st.metric("IV Differential", f"{opportunity.iv_differential:.1f}%")