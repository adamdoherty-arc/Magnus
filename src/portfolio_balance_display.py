"""Portfolio Balance Display - Visualizations and Data Tables"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, date
import logging
from src.portfolio_balance_tracker import PortfolioBalanceTracker

logger = logging.getLogger(__name__)


def display_portfolio_balance_dashboard(days_back: int = 90, expanded: bool = True):
    """
    Display comprehensive portfolio balance dashboard with charts and data

    Args:
        days_back: Number of days of history to display
        expanded: Whether the expander starts expanded
    """
    tracker = PortfolioBalanceTracker()

    # Get balance history
    history = tracker.get_balance_history(days_back=days_back)

    if not history:
        with st.expander("📊 Portfolio Balance History", expanded=expanded):
            st.info("📊 Balance history will be automatically recorded daily as you view your positions.")
            st.caption("First balance record will be created automatically when you load the positions page.")
        return

    # Convert to DataFrame
    df = pd.DataFrame(history)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')

    # Get summary stats for multiple periods
    stats_30d = tracker.get_summary_stats(days_back=30)
    stats_90d = tracker.get_summary_stats(days_back=90)
    stats_365d = tracker.get_summary_stats(days_back=365)

    with st.expander(f"📊 Portfolio Balance History ({len(df)} days)", expanded=expanded):
        # === SUMMARY METRICS ===
        st.markdown("#### Performance Summary")

        # Period selector
        period_option = st.radio(
            "Time Period",
            ["Last 30 Days", "Last 90 Days", "Last Year", "All Time"],
            horizontal=True,
            key="balance_period_selector"
        )

        # Select stats based on period
        if period_option == "Last 30 Days":
            stats = stats_30d
        elif period_option == "Last 90 Days":
            stats = stats_90d
        elif period_option == "Last Year":
            stats = stats_365d
        else:  # All Time
            stats = tracker.get_summary_stats(days_back=len(df) * 2)  # Get all

        if stats:
            col1, col2, col3, col4, col5 = st.columns(5)

            with col1:
                start_bal = stats.get('period_start_balance', 0)
                st.metric("Start Balance", f"${start_bal:,.2f}")

            with col2:
                end_bal = stats.get('period_end_balance', 0)
                st.metric("Current Balance", f"${end_bal:,.2f}")

            with col3:
                total_pl = stats.get('period_return', 0)
                pl_pct = stats.get('period_return_percent', 0)
                delta_color = "normal" if total_pl >= 0 else "inverse"
                st.metric(
                    "Total P/L",
                    f"${total_pl:,.2f}",
                    delta=f"{pl_pct:.2f}%",
                    delta_color=delta_color
                )

            with col4:
                win_rate = stats.get('win_rate', 0)
                st.metric("Win Rate", f"{win_rate:.1f}%")

            with col5:
                avg_daily = stats.get('avg_daily_pl', 0)
                st.metric("Avg Daily P/L", f"${avg_daily:,.2f}")

        st.markdown("---")

        # === BALANCE CHART ===
        st.markdown("#### Balance Over Time")

        fig_balance = go.Figure()

        # Balance line
        fig_balance.add_trace(go.Scatter(
            x=df['date'],
            y=df['ending_balance'],
            mode='lines+markers',
            name='Portfolio Balance',
            line=dict(color='#00D4FF', width=3),
            marker=dict(size=6),
            hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Balance: $%{y:,.2f}<extra></extra>'
        ))

        fig_balance.update_layout(
            title="Portfolio Balance History",
            xaxis_title="Date",
            yaxis_title="Balance ($)",
            height=400,
            hovermode='x unified',
            template='plotly_dark',
            showlegend=False
        )

        st.plotly_chart(fig_balance, use_container_width=True, key="balance_chart")

        # === DAILY P/L CHART ===
        st.markdown("#### Daily Profit/Loss")

        fig_pl = go.Figure()

        # Color bars based on positive/negative
        colors = ['#00AA00' if pl > 0 else '#DD0000' for pl in df['daily_pl']]

        fig_pl.add_trace(go.Bar(
            x=df['date'],
            y=df['daily_pl'],
            name='Daily P/L',
            marker_color=colors,
            hovertemplate='<b>%{x|%Y-%m-%d}</b><br>P/L: $%{y:,.2f}<extra></extra>'
        ))

        # Add zero line
        fig_pl.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)

        fig_pl.update_layout(
            title="Daily Profit/Loss",
            xaxis_title="Date",
            yaxis_title="P/L ($)",
            height=300,
            hovermode='x unified',
            template='plotly_dark',
            showlegend=False
        )

        st.plotly_chart(fig_pl, use_container_width=True, key="pl_chart")

        # === CUMULATIVE P/L CHART ===
        st.markdown("#### Cumulative Returns")

        # Calculate cumulative P/L from first balance
        if len(df) > 0:
            first_balance = df.iloc[0]['starting_balance']
            df['cumulative_pl'] = df['ending_balance'] - first_balance
            df['cumulative_pl_pct'] = (df['cumulative_pl'] / first_balance * 100) if first_balance > 0 else 0

            fig_cumulative = go.Figure()

            fig_cumulative.add_trace(go.Scatter(
                x=df['date'],
                y=df['cumulative_pl'],
                mode='lines',
                name='Cumulative P/L',
                fill='tozeroy',
                line=dict(color='#FFD700', width=2),
                hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Cumulative P/L: $%{y:,.2f}<extra></extra>'
            ))

            # Add zero line
            fig_cumulative.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)

            fig_cumulative.update_layout(
                title="Cumulative Profit/Loss",
                xaxis_title="Date",
                yaxis_title="Cumulative P/L ($)",
                height=300,
                hovermode='x unified',
                template='plotly_dark',
                showlegend=False
            )

            st.plotly_chart(fig_cumulative, use_container_width=True, key="cumulative_chart")

        st.markdown("---")

        # === DATA TABLE ===
        st.markdown("#### Balance History Data")

        # Format data for display
        display_df = df[['date', 'starting_balance', 'ending_balance', 'daily_pl',
                        'daily_pl_percent', 'buying_power', 'total_positions']].copy()

        # Format columns
        display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
        display_df = display_df.rename(columns={
            'date': 'Date',
            'starting_balance': 'Starting',
            'ending_balance': 'Ending',
            'daily_pl': 'Daily P/L',
            'daily_pl_percent': 'P/L %',
            'buying_power': 'Buying Power',
            'total_positions': 'Positions'
        })

        # Store raw P/L for coloring
        pl_raw = display_df['Daily P/L'].copy()

        # Format numeric columns
        display_df['Starting'] = display_df['Starting'].apply(lambda x: f'${x:,.2f}' if pd.notna(x) else '-')
        display_df['Ending'] = display_df['Ending'].apply(lambda x: f'${x:,.2f}')
        display_df['Daily P/L'] = display_df['Daily P/L'].apply(lambda x: f'${x:,.2f}' if pd.notna(x) else '-')
        display_df['P/L %'] = display_df['P/L %'].apply(lambda x: f'{x:.2f}%' if pd.notna(x) else '-')
        display_df['Buying Power'] = display_df['Buying Power'].apply(lambda x: f'${x:,.2f}' if pd.notna(x) else '-')
        display_df['Positions'] = display_df['Positions'].apply(lambda x: int(x) if pd.notna(x) else '-')

        # Apply color coding
        def highlight_pl(row):
            idx = row.name
            pl_val = pl_raw.iloc[idx] if idx < len(pl_raw) and pd.notna(pl_raw.iloc[idx]) else 0

            styles = [''] * len(row)

            pl_idx = list(display_df.columns).index('Daily P/L')
            pl_pct_idx = list(display_df.columns).index('P/L %')

            if pl_val > 0:
                styles[pl_idx] = 'color: #00AA00; font-weight: bold'
                styles[pl_pct_idx] = 'color: #00AA00; font-weight: bold'
            elif pl_val < 0:
                styles[pl_idx] = 'color: #DD0000; font-weight: bold'
                styles[pl_pct_idx] = 'color: #DD0000; font-weight: bold'

            return styles

        styled_df = display_df.style.apply(highlight_pl, axis=1)

        st.dataframe(
            styled_df,
            hide_index=True,
            use_container_width=True,
            key="balance_history_table"
        )

        st.caption("💡 Balance is automatically recorded once per day when you view the Positions page.")


def _display_manual_entry_form(tracker: PortfolioBalanceTracker):
    """Display form to manually record daily balance"""
    st.markdown("#### 📝 Record Daily Balance")

    with st.form("record_balance_form", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            balance_date = st.date_input(
                "Date",
                value=date.today(),
                max_value=date.today(),
                key="balance_date_input"
            )

        with col2:
            ending_balance = st.number_input(
                "Ending Balance ($)",
                min_value=0.0,
                value=0.0,
                step=100.0,
                key="ending_balance_input"
            )

        with col3:
            starting_balance = st.number_input(
                "Starting Balance ($) [Optional]",
                min_value=0.0,
                value=0.0,
                step=100.0,
                key="starting_balance_input",
                help="Leave at 0 to auto-calculate from previous day"
            )

        col4, col5, col6 = st.columns(3)

        with col4:
            buying_power = st.number_input(
                "Buying Power ($) [Optional]",
                min_value=0.0,
                value=0.0,
                step=100.0,
                key="buying_power_input"
            )

        with col5:
            options_value = st.number_input(
                "Options Value ($) [Optional]",
                value=0.0,
                step=100.0,
                key="options_value_input"
            )

        with col6:
            total_positions = st.number_input(
                "# Positions [Optional]",
                min_value=0,
                value=0,
                step=1,
                key="positions_input"
            )

        notes = st.text_area(
            "Notes (Optional)",
            placeholder="Any notes about today's trading...",
            key="balance_notes_input"
        )

        col_submit, col_delete = st.columns([1, 1])

        with col_submit:
            submitted = st.form_submit_button("💾 Save Balance", type="primary", use_container_width=True)

        with col_delete:
            delete = st.form_submit_button("🗑️ Delete This Date", type="secondary", use_container_width=True)

        if submitted:
            if ending_balance > 0:
                success = tracker.record_daily_balance(
                    balance_date=balance_date,
                    ending_balance=ending_balance,
                    starting_balance=starting_balance if starting_balance > 0 else None,
                    buying_power=buying_power if buying_power > 0 else None,
                    options_value=options_value if options_value != 0 else None,
                    total_positions=total_positions if total_positions > 0 else None,
                    notes=notes if notes else None
                )

                if success:
                    st.success(f"✅ Balance recorded for {balance_date}")
                    st.rerun()
                else:
                    st.error("Failed to record balance")
            else:
                st.error("Please enter a valid ending balance")

        if delete:
            success = tracker.delete_balance(balance_date)
            if success:
                st.success(f"🗑️ Deleted balance for {balance_date}")
                st.rerun()
            else:
                st.error("Failed to delete balance")


def record_balance_from_positions(
    total_equity: float,
    buying_power: float,
    options_value: float,
    stock_value: float,
    total_positions: int
) -> bool:
    """
    Helper function to automatically record today's balance from positions data

    Args:
        total_equity: Total account equity
        buying_power: Available buying power
        options_value: Total value of options
        stock_value: Total value of stocks
        total_positions: Number of positions

    Returns:
        True if successful
    """
    tracker = PortfolioBalanceTracker()

    try:
        success = tracker.record_daily_balance(
            balance_date=date.today(),
            ending_balance=total_equity,
            buying_power=buying_power,
            options_value=options_value,
            stock_value=stock_value,
            cash_value=buying_power,  # Approximate cash as buying power
            total_positions=total_positions
        )
        return success
    except Exception as e:
        logger.error(f"Error auto-recording balance: {e}")
        return False
