"""
Improved Positions Page with:
- Auto-refresh controls
- Color-coded P/L (green/red)
- TradingView chart links
- Complete trade history with P/L calculations
- Performance analytics by time period
"""

import streamlit as st
import robin_stocks.robinhood as rh
import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict

def show_positions_page():
    """Main positions page with all improvements"""

    st.title("💼 Active Positions")
    st.caption("Live option positions from Robinhood with auto-refresh")

    # Auto-Refresh Controls
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        auto_refresh = st.checkbox("🔄 Auto-Refresh", value=False, key="pos_auto_refresh")
    with col2:
        refresh_freq = st.selectbox(
            "Frequency",
            ["30s", "1m", "2m", "5m", "10m"],
            index=2,
            key="pos_refresh_freq",
            label_visibility="collapsed"
        )
    with col3:
        if st.button("🔄 Refresh Now", type="primary"):
            st.rerun()

    # Auto-refresh logic
    if auto_refresh:
        freq_map = {"30s": 30, "1m": 60, "2m": 120, "5m": 300, "10m": 600}
        st.markdown(
            f'<meta http-equiv="refresh" content="{freq_map[refresh_freq]}">',
            unsafe_allow_html=True
        )

    st.markdown("---")

    # === LOGIN TO ROBINHOOD (once for entire page) ===
    rh_session = None
    try:
        rh.login(username='brulecapital@gmail.com', password='FortKnox')
        rh_session = rh  # Store the logged-in session
    except Exception as e:
        st.error(f"Failed to connect to Robinhood: {e}")
        st.info("Please refresh the page to try again")
        return

    # === ACTIVE POSITIONS ===
    st.markdown("### 🎯 Your Current Option Positions")

    try:
        # Get total account value
        account_profile = rh.load_account_profile()
        portfolio = rh.load_portfolio_profile()
        total_equity = float(portfolio.get('equity', 0)) if portfolio else 0

        # Get all open option positions
        positions_raw = rh.get_open_option_positions()

        if positions_raw:
            positions_data = []

            for pos in positions_raw:
                # Get option details
                opt_id = pos.get('option_id')
                if not opt_id:
                    continue

                opt_data = rh.get_option_instrument_data_by_id(opt_id)
                symbol = opt_data.get('chain_symbol', 'Unknown')
                strike = float(opt_data.get('strike_price', 0))
                exp_date = opt_data.get('expiration_date', 'Unknown')
                opt_type = opt_data.get('type', 'unknown')

                # Position details
                position_type = pos.get('type', 'unknown')
                quantity = float(pos.get('quantity', 0))
                avg_price = abs(float(pos.get('average_price', 0)))

                # Calculate values
                total_premium = avg_price * quantity

                # Get current market price
                market_data = rh.get_option_market_data_by_id(opt_id)
                if market_data and len(market_data) > 0:
                    current_price = float(market_data[0].get('adjusted_mark_price', 0)) * 100
                else:
                    current_price = 0

                current_value = current_price * quantity

                # Calculate P/L
                if position_type == 'short':
                    pl = total_premium - current_value
                else:
                    pl = current_value - total_premium

                # Calculate DTE
                if exp_date != 'Unknown':
                    exp_dt = datetime.strptime(exp_date, '%Y-%m-%d')
                    dte = (exp_dt - datetime.now()).days
                else:
                    dte = 0

                # Determine strategy type
                if position_type == 'short' and opt_type == 'put':
                    strategy = 'CSP'
                elif position_type == 'short' and opt_type == 'call':
                    strategy = 'CC'
                elif position_type == 'long' and opt_type == 'call':
                    strategy = 'Long Call'
                elif position_type == 'long' and opt_type == 'put':
                    strategy = 'Long Put'
                else:
                    strategy = 'Other'

                # Create TradingView link
                tv_link = f"https://www.tradingview.com/chart/?symbol={symbol}"

                positions_data.append({
                    'Symbol': symbol,
                    'Strategy': strategy,
                    'Strike': strike,
                    'Expiration': exp_date,
                    'DTE': dte,
                    'Contracts': int(quantity),
                    'Premium': total_premium,
                    'Current': current_value,
                    'P/L': pl,
                    'P/L %': (pl/total_premium*100) if total_premium > 0 else 0,
                    'TradingView': tv_link,
                    'pl_raw': pl  # For color coding
                })

            if positions_data:
                # Display metrics
                total_pl = sum([p['P/L'] for p in positions_data])
                total_premium = sum([p['Premium'] for p in positions_data])

                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    st.metric("Total Account Value", f'${total_equity:,.2f}')
                with col2:
                    st.metric("Active Positions", len(positions_data))
                with col3:
                    st.metric("Total Premium", f'${total_premium:,.2f}')
                with col4:
                    pl_color = "normal" if total_pl >= 0 else "inverse"
                    st.metric(
                        "Total P/L",
                        f'${total_pl:,.2f}',
                        delta=f'{(total_pl/total_premium*100):.1f}%' if total_premium > 0 else '0%',
                        delta_color=pl_color
                    )
                with col5:
                    csps = len([p for p in positions_data if 'CSP' in p['Strategy']])
                    st.metric("CSPs", csps)

                # Create dataframe
                df = pd.DataFrame(positions_data)

                # Format display columns
                display_df = df.copy()
                display_df['Strike'] = display_df['Strike'].apply(lambda x: f'${x:.2f}')
                display_df['Premium'] = display_df['Premium'].apply(lambda x: f'${x:,.2f}')
                display_df['Current'] = display_df['Current'].apply(lambda x: f'${x:,.2f}')

                # Store raw P/L values for coloring before formatting
                pl_vals = display_df['P/L'].copy()
                pl_pct_vals = display_df['P/L %'].copy()

                display_df['P/L'] = display_df['P/L'].apply(lambda x: f'${x:,.2f}')
                display_df['P/L %'] = display_df['P/L %'].apply(lambda x: f'{x:.1f}%')

                # Drop helper column
                display_df = display_df.drop(columns=['pl_raw'])

                # Function to apply text color
                def highlight_pl(row):
                    """Apply row-wise styling based on P/L value"""
                    idx = row.name
                    pl_val = pl_vals.iloc[idx] if idx < len(pl_vals) else 0

                    styles = [''] * len(row)

                    # Find P/L and P/L % column indices
                    pl_idx = list(display_df.columns).index('P/L')
                    pl_pct_idx = list(display_df.columns).index('P/L %')

                    # Profit (positive P/L) = GREEN TEXT, Loss (negative P/L) = RED TEXT
                    if pl_val > 0:
                        styles[pl_idx] = 'color: #00AA00; font-weight: bold'  # Green text for profit
                        styles[pl_pct_idx] = 'color: #00AA00; font-weight: bold'
                    elif pl_val < 0:
                        styles[pl_idx] = 'color: #DD0000; font-weight: bold'  # Red text for loss
                        styles[pl_pct_idx] = 'color: #DD0000; font-weight: bold'
                    # else pl_val == 0, no styling (neutral)

                    return styles

                # Apply styling
                styled_df = display_df.style.apply(highlight_pl, axis=1)

                # Display table
                st.dataframe(
                    styled_df,
                    hide_index=True,
                    use_container_width=True,
                    column_config={
                        "TradingView": st.column_config.LinkColumn(
                            "Chart",
                            display_text="📈"
                        )
                    }
                )

            else:
                st.info("No open option positions found in Robinhood")

        else:
            st.info("No open option positions found")

    except Exception as e:
        st.error(f"Error loading positions: {e}")

    # === TRADE HISTORY ===
    st.markdown("---")
    st.markdown("### 📊 Trade History")
    st.caption("Closed trades with P/L calculations")

    closed_trades = []  # Initialize outside try block for use in performance analytics
    try:
        closed_trades = get_closed_trades_with_pl(rh_session)

        if closed_trades:
            # Calculate summary metrics
            total_pl = sum([t['P/L'] for t in closed_trades])
            winning_trades = [t for t in closed_trades if t['P/L'] > 0]
            win_rate = (len(winning_trades) / len(closed_trades) * 100) if closed_trades else 0
            avg_pl = total_pl / len(closed_trades) if closed_trades else 0

            # Display summary
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Closed", len(closed_trades))
            with col2:
                pl_color = "normal" if total_pl >= 0 else "inverse"
                st.metric("Total P/L", f'${total_pl:,.2f}', delta_color=pl_color)
            with col3:
                st.metric("Win Rate", f'{win_rate:.1f}%')
            with col4:
                st.metric("Avg P/L", f'${avg_pl:.2f}')

            # Display trades table with color coding
            df_history = pd.DataFrame(closed_trades[:50])  # Show last 50

            # Add TradingView links
            df_history['TradingView'] = df_history['Symbol'].apply(
                lambda x: f"https://www.tradingview.com/chart/?symbol={x}"
            )

            # Format display columns
            display_cols = ['Close Date', 'Symbol', 'Strategy', 'Strike',
                          'Open Premium', 'Close Cost', 'P/L', 'P/L %', 'Days Held', 'TradingView']

            # Store raw P/L values before formatting
            pl_raw_vals = df_history['P/L'].copy()

            # Format numeric columns
            df_display = df_history[display_cols].copy()
            df_display['Open Premium'] = df_display['Open Premium'].apply(lambda x: f'${x:,.2f}')
            df_display['Close Cost'] = df_display['Close Cost'].apply(lambda x: f'${x:,.2f}')
            df_display['P/L'] = df_display['P/L'].apply(lambda x: f'${x:,.2f}')
            df_display['P/L %'] = df_display['P/L %'].apply(lambda x: f'{x:.1f}%')

            # Function to apply row-wise styling
            def highlight_history_pl(row):
                """Apply row-wise styling based on P/L value"""
                idx = row.name
                pl_val = pl_raw_vals.iloc[idx] if idx < len(pl_raw_vals) else 0

                styles = [''] * len(row)

                # Find P/L and P/L % column indices
                pl_idx = list(df_display.columns).index('P/L')
                pl_pct_idx = list(df_display.columns).index('P/L %')

                # Profit (positive P/L) = GREEN TEXT, Loss (negative P/L) = RED TEXT
                if pl_val > 0:
                    styles[pl_idx] = 'color: #00AA00; font-weight: bold'  # Green text for profit
                    styles[pl_pct_idx] = 'color: #00AA00; font-weight: bold'
                elif pl_val < 0:
                    styles[pl_idx] = 'color: #DD0000; font-weight: bold'  # Red text for loss
                    styles[pl_pct_idx] = 'color: #DD0000; font-weight: bold'
                # else pl_val == 0, no styling (neutral)

                return styles

            # Apply styling
            styled_history = df_display.style.apply(highlight_history_pl, axis=1)

            st.dataframe(
                styled_history,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "TradingView": st.column_config.LinkColumn(
                        "Chart",
                        display_text="📈"
                    )
                }
            )

        else:
            st.info("No closed trades found")

    except Exception as e:
        st.error(f"Error loading trade history: {e}")

    # === PERFORMANCE ANALYTICS ===
    st.markdown("---")
    st.markdown("### 📈 Performance Analytics")
    st.caption("Profit breakdown by time period")

    try:
        if closed_trades:
            performance_data = calculate_performance_by_period(closed_trades)

            df_perf = pd.DataFrame(performance_data)

            # Apply color coding to Total P/L column
            def color_perf_pl(val):
                """Apply text color to P/L cells"""
                try:
                    if '$' in str(val):
                        num_val = float(str(val).replace('$', '').replace(',', ''))
                    else:
                        num_val = float(val)

                    if num_val > 0:
                        return 'color: #00AA00; font-weight: bold'  # Green text for profit
                    elif num_val < 0:
                        return 'color: #DD0000; font-weight: bold'  # Red text for loss
                    else:
                        return 'font-weight: bold'  # Neutral for zero
                except:
                    return ''

            styled_perf = df_perf.style.applymap(
                color_perf_pl,
                subset=['Total P/L']
            )

            # Display styled table
            st.dataframe(
                styled_perf,
                hide_index=True,
                use_container_width=True
            )

        else:
            st.info("No performance data available yet")

    except Exception as e:
        st.error(f"Error calculating performance: {e}")


def get_closed_trades_with_pl(rh_session):
    """
    Get closed trades with full P/L calculations
    Matches opening and closing orders
    """
    all_orders = rh_session.get_all_option_orders()

    # Separate opens and closes
    open_orders = {}  # key: (symbol, strike, exp, type) -> order
    closed_trades = []

    for order in all_orders:
        if order.get('state') != 'filled':
            continue

        legs = order.get('legs', [])
        if not legs:
            continue

        leg = legs[0]
        side = leg.get('side')
        position_effect = leg.get('position_effect')

        opt_url = leg.get('option')
        if not opt_url:
            continue

        # Extract option ID
        if isinstance(opt_url, str) and 'options/instruments/' in opt_url:
            opt_id = opt_url.split('/')[-2]
        else:
            opt_id = opt_url

        # Get option details
        opt_data = rh_session.get_option_instrument_data_by_id(opt_id)
        if not opt_data:
            continue

        symbol = opt_data.get('chain_symbol', 'Unknown')
        strike = float(opt_data.get('strike_price', 0))
        exp_date = opt_data.get('expiration_date', 'Unknown')
        opt_type = opt_data.get('type', 'unknown')

        # Trade details
        quantity = float(order.get('quantity', 0))

        # Use processed_premium (total premium) and divide by quantity to get per-contract price
        processed_premium = float(order.get('processed_premium', 0))
        price = (processed_premium / quantity) if quantity > 0 else 0

        date_str = order.get('updated_at', '')

        if date_str:
            trade_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        else:
            # Make sure we use timezone-aware datetime
            from datetime import timezone
            trade_date = datetime.now(timezone.utc)

        # Key for matching
        trade_key = (symbol, strike, exp_date, opt_type)

        if position_effect == 'open':
            # Store opening order
            open_orders[trade_key] = {
                'open_price': price,  # Per-contract price
                'open_date': trade_date,
                'quantity': quantity,
                'side': side
            }
        elif position_effect == 'close':
            # Match with opening order
            if trade_key in open_orders:
                open_order = open_orders[trade_key]

                # Calculate P/L (both prices are per-contract already)
                open_premium = abs(open_order['open_price']) * quantity
                close_cost = abs(price) * quantity

                # For short positions: profit = premium - close_cost
                # For long positions: profit = close_cost - premium
                if side == 'buy':  # Closing a short position
                    pl = open_premium - close_cost
                    strategy = 'CSP' if opt_type == 'put' else 'CC'
                else:  # Closing a long position
                    pl = close_cost - open_premium
                    strategy = 'Long Call' if opt_type == 'call' else 'Long Put'

                pl_pct = (pl / open_premium * 100) if open_premium > 0 else 0

                # Days held
                days_held = (trade_date - open_order['open_date']).days

                closed_trades.append({
                    'Close Date': trade_date.strftime('%Y-%m-%d'),
                    'Symbol': symbol,
                    'Strategy': strategy,
                    'Strike': f'${strike:.2f}',
                    'Open Premium': open_premium,
                    'Close Cost': close_cost,
                    'P/L': pl,
                    'P/L %': pl_pct,
                    'Days Held': days_held,
                    'close_timestamp': trade_date  # For sorting/filtering
                })

                # Remove from open orders
                del open_orders[trade_key]

    # Sort by close date (newest first)
    closed_trades.sort(key=lambda x: x['close_timestamp'], reverse=True)

    return closed_trades


def calculate_performance_by_period(closed_trades):
    """Calculate performance metrics for different time periods"""
    from datetime import timezone
    now = datetime.now(timezone.utc)

    periods = {
        'Last 7 Days': timedelta(days=7),
        'Last 30 Days': timedelta(days=30),
        'Last 3 Months': timedelta(days=90),
        'Last 6 Months': timedelta(days=180),
        'Last 1 Year': timedelta(days=365),
        'All Time': None
    }

    performance = []

    for period_name, delta in periods.items():
        if delta:
            cutoff = now - delta
            period_trades = [t for t in closed_trades if t['close_timestamp'] >= cutoff]
        else:
            period_trades = closed_trades

        if period_trades:
            total_pl = sum([t['P/L'] for t in period_trades])
            winning = [t for t in period_trades if t['P/L'] > 0]
            win_rate = (len(winning) / len(period_trades) * 100)
            avg_pl = total_pl / len(period_trades)
            best_trade = max([t['P/L'] for t in period_trades])

            # Simple ROI estimate (assumes $10k capital)
            roi = (total_pl / 10000 * 100)

            performance.append({
                'Period': period_name,
                'Trades': len(period_trades),
                'Total P/L': f'${total_pl:,.2f}',
                'Win Rate': f'{win_rate:.1f}%',
                'Avg P/L': f'${avg_pl:.2f}',
                'Best Trade': f'${best_trade:.2f}',
                'ROI': f'{roi:.1f}%'
            })
        else:
            performance.append({
                'Period': period_name,
                'Trades': 0,
                'Total P/L': '$0.00',
                'Win Rate': '0%',
                'Avg P/L': '$0.00',
                'Best Trade': '$0.00',
                'ROI': '0%'
            })

    return performance
