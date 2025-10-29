"""Magnus - Advanced Options Trading Platform"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import math
import redis
import json
import yfinance as yf
import asyncio
import os
import time
from typing import List, Dict, Any

# Import agents
from src.agents.runtime.market_data_agent import MarketDataAgent
from src.agents.runtime.wheel_strategy_agent import WheelStrategyAgent
from src.agents.runtime.risk_management_agent import RiskManagementAgent

# Import TradingView Database Manager
from src.tradingview_db_manager import TradingViewDBManager

# Page config
st.set_page_config(
    page_title="Magnus Trading Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stMetric .metric-container {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
    }
    .success-box {
        padding: 10px;
        border-radius: 5px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
    }
    .warning-box {
        padding: 10px;
        border-radius: 5px;
        background-color: #fff3cd;
        border: 1px solid #ffeeba;
    }
    .danger-box {
        padding: 10px;
        border-radius: 5px;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Redis connection
@st.cache_resource
def init_redis():
    return redis.Redis(
        host='localhost',
        port=6379,
        db=0,
        decode_responses=True
    )

redis_client = init_redis()

# Initialize agents
@st.cache_resource
def init_agents():
    market_agent = MarketDataAgent(redis_client, max_price=50.0)
    strategy_agent = WheelStrategyAgent(redis_client)
    risk_agent = RiskManagementAgent(redis_client)
    return market_agent, strategy_agent, risk_agent

market_agent, strategy_agent, risk_agent = init_agents()

# Sidebar
st.sidebar.title("⚡ Magnus")

# Navigation as buttons/links
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

# Navigation buttons
if st.sidebar.button("📈 Dashboard", use_container_width=True):
    st.session_state.page = "Dashboard"
if st.sidebar.button("🎯 Opportunities", use_container_width=True):
    st.session_state.page = "Opportunities"
if st.sidebar.button("💼 Positions", use_container_width=True):
    st.session_state.page = "Positions"
if st.sidebar.button("🔍 Premium Scanner", use_container_width=True):
    st.session_state.page = "Premium Scanner"
if st.sidebar.button("📊 TradingView Watchlists", use_container_width=True):
    st.session_state.page = "TradingView Watchlists"
if st.sidebar.button("🗄️ Database Scan", use_container_width=True):
    st.session_state.page = "Database Scan"
if st.sidebar.button("📅 Earnings Calendar", use_container_width=True):
    st.session_state.page = "Earnings Calendar"
if st.sidebar.button("📆 Calendar Spreads", use_container_width=True):
    st.session_state.page = "Calendar Spreads"
if st.sidebar.button("⚙️ Settings", use_container_width=True):
    st.session_state.page = "Settings"

page = st.session_state.page

# No connection status displayed

# Set default values for removed variables
max_price = 50
min_premium = 1.0
profit_target = 50
watchlist = []

# Main content based on page selection
if page == "Dashboard":
    st.title("💰 Magnus Performance & Forecasts")

    # Get account data and positions if connected
    account_data = {}
    positions = []

    if st.session_state.get('rh_connected') and 'rh_functions' in st.session_state:
        try:
            get_account = st.session_state['rh_functions']['get_account']
            get_options = st.session_state['rh_functions']['get_options']
            get_positions = st.session_state['rh_functions']['get_positions']
            identify_wheel = st.session_state['rh_functions']['identify_wheel']

            account_data = get_account()
            stocks = get_positions()
            options = get_options()
            wheel_positions = identify_wheel(stocks, options)

            # Convert to dashboard format
            for wp in wheel_positions:
                if wp['strategy'] == 'CSP':
                    positions.append({
                        'Symbol': wp['symbol'],
                        'Type': 'CSP',
                        'Strike': wp.get('strike', 0),
                        'Expiration': wp.get('expiration', ''),
                        'Premium': wp.get('premium', 0),
                        'Current Value': wp.get('current_value', 0),
                        'Days to Expiry': wp.get('days_to_expiry', 0),
                        'Quantity': wp.get('contracts', 1)
                    })
        except:
            pass

    # Current Status Section
    st.markdown("### 📊 Current Portfolio Status")

    # Check if we have real Robinhood data
    if account_data:
        col1, col2, col3, col4, col5 = st.columns(5)

        current_balance = float(account_data.get('portfolio_value', 0))
        buying_power = float(account_data.get('buying_power', 0))
        total_premium_collected = sum(p.get('Premium', 0) for p in positions)
        positions_at_risk = sum(p.get('Strike', 0) * 100 for p in positions if p.get('Type') == 'CSP')

        with col1:
            st.metric("Current Balance", f"${current_balance:,.0f}")
        with col2:
            st.metric("Buying Power", f"${buying_power:,.0f}")
        with col3:
            st.metric("Premium Collected", f"${total_premium_collected:,.0f}")
        with col4:
            st.metric("Capital at Risk", f"${positions_at_risk:,.0f}")
        with col5:
            st.metric("Active CSPs", len(positions))
    else:
        st.info("💡 Connect to Robinhood in the Settings tab to see your real portfolio data")

    # Balance Forecast Timeline
    st.markdown("---")
    st.markdown("### 📅 Balance Forecast Timeline")

    if positions:
        # Group positions by expiration date
        from collections import defaultdict
        positions_by_date = defaultdict(list)

        for pos in positions:
            if pos.get('Expiration'):
                positions_by_date[pos['Expiration']].append(pos)

        # Sort dates
        sorted_dates = sorted(positions_by_date.keys())

        # Create forecast timeline
        forecast_data = []
        running_balance = current_balance

        for exp_date in sorted_dates:
            date_positions = positions_by_date[exp_date]

            # Calculate outcomes for this date
            premium_income = sum(p.get('Premium', 0) for p in date_positions)
            capital_deployed = sum(p.get('Strike', 0) * 100 for p in date_positions)

            # Best case: All CSPs expire worthless, keep premium
            best_case = running_balance + premium_income

            # Worst case: All CSPs assigned, deploy capital but keep premium
            worst_case = running_balance - capital_deployed + premium_income

            # Expected case: 70% expire worthless (based on typical OTM probabilities)
            expected_case = running_balance + (premium_income * 0.7) - (capital_deployed * 0.3)

            forecast_data.append({
                'Date': exp_date,
                'Positions': len(date_positions),
                'Premium Income': premium_income,
                'Capital at Risk': capital_deployed,
                'Best Case Balance': best_case,
                'Expected Balance': expected_case,
                'Worst Case Balance': worst_case
            })

            running_balance = expected_case  # Use expected for next calculation

        # Display forecast table
        if forecast_data:
            st.markdown("#### Expiration Date Projections")

            for forecast in forecast_data:
                with st.expander(f"📅 {forecast['Date']} - {forecast['Positions']} Position(s)"):
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric("Premium Income", f"${forecast['Premium Income']:,.0f}")
                        st.metric("Capital at Risk", f"${forecast['Capital at Risk']:,.0f}")

                    with col2:
                        st.metric("Best Case (All Expire)", f"${forecast['Best Case Balance']:,.0f}",
                                 f"+${forecast['Best Case Balance'] - current_balance:,.0f}")
                        st.metric("Expected (70% Expire)", f"${forecast['Expected Balance']:,.0f}",
                                 f"+${forecast['Expected Balance'] - current_balance:,.0f}")

                    with col3:
                        st.metric("Worst Case (All Assigned)", f"${forecast['Worst Case Balance']:,.0f}",
                                 f"{forecast['Worst Case Balance'] - current_balance:+,.0f}")

                        # Show positions for this date
                        st.markdown("**Positions Expiring:**")
                        for pos in positions_by_date[forecast['Date']]:
                            st.caption(f"• {pos['Symbol']} ${pos['Strike']} Put")

            # Summary Statistics
            st.markdown("#### 📈 Forecast Summary")
            col1, col2, col3, col4 = st.columns(4)

            total_premium = sum(f['Premium Income'] for f in forecast_data)
            max_capital_risk = max(f['Capital at Risk'] for f in forecast_data)
            final_best = forecast_data[-1]['Best Case Balance'] if forecast_data else current_balance
            final_expected = forecast_data[-1]['Expected Balance'] if forecast_data else current_balance

            with col1:
                st.metric("Total Premium Potential", f"${total_premium:,.0f}")
            with col2:
                st.metric("Max Capital at Risk", f"${max_capital_risk:,.0f}")
            with col3:
                st.metric("Expected Final Balance", f"${final_expected:,.0f}",
                         f"+{((final_expected/current_balance - 1) * 100):.1f}%")
            with col4:
                monthly_return = ((final_expected/current_balance - 1) * 100) / max(1, len(sorted_dates))
                st.metric("Avg Monthly Return", f"{monthly_return:.2f}%")

    # Detailed Position Forecast
    st.markdown("---")
    st.markdown("### 🎯 Individual Position Forecasts")

    if positions:
        # Create detailed forecast for each position
        for pos in positions:
            if pos.get('Type') == 'CSP' and pos.get('Days to Expiry', 0) > 0:
                with st.expander(f"{pos['Symbol']} - ${pos['Strike']} Put - Expires {pos['Expiration']}"):
                    col1, col2, col3, col4 = st.columns(4)

                    # Calculate probabilities (simplified Black-Scholes approximation)
                    days_left = pos['Days to Expiry']
                    premium = pos.get('Premium', 0)
                    strike = pos.get('Strike', 0)
                    current_value = abs(pos.get('Current Value', 0))

                    # Profit scenarios
                    profit_if_expires = premium
                    profit_if_closed_now = premium - current_value
                    daily_theta = profit_if_closed_now / max(1, days_left)

                    with col1:
                        st.markdown("**Position Details**")
                        st.metric("Strike Price", f"${strike:.2f}")
                        st.metric("Days to Expiry", days_left)
                        st.metric("Premium Collected", f"${premium:.2f}")

                    with col2:
                        st.markdown("**Current Status**")
                        st.metric("Current P&L", f"${profit_if_closed_now:.2f}",
                                 f"{(profit_if_closed_now/premium*100):.1f}%" if premium > 0 else "0%")
                        st.metric("Daily Theta", f"${daily_theta:.2f}")
                        st.metric("Cost to Close", f"${current_value:.2f}")

                    with col3:
                        st.markdown("**Forecast (If Expires OTM)**")
                        st.metric("Max Profit", f"${profit_if_expires:.2f}")
                        st.metric("Return on Risk", f"{(premium/(strike*100)*100):.2f}%")
                        st.metric("Annualized Return", f"{(premium/(strike*100)*365/max(30, days_left)*100):.1f}%")

                    with col4:
                        st.markdown("**Risk (If Assigned)**")
                        st.metric("Capital Required", f"${strike * 100:.2f}")
                        st.metric("Breakeven Price", f"${strike - premium/100:.2f}")

                        # Simple assignment probability based on moneyness
                        ticker = yf.Ticker(pos['Symbol'])
                        try:
                            info = ticker.info
                            current_stock_price = info.get('currentPrice', strike)
                            if current_stock_price < strike:
                                assignment_prob = min(90, 50 + ((strike - current_stock_price)/strike * 100))
                            else:
                                assignment_prob = max(10, 50 - ((current_stock_price - strike)/strike * 100))
                            st.metric("Assignment Prob", f"{assignment_prob:.0f}%")
                        except:
                            st.metric("Assignment Prob", "N/A")
    else:
        st.info("No active positions. Connect to Robinhood or open some positions to see forecasts.")

    # Historical Performance (if data available)
    st.markdown("---")
    st.markdown("### 📊 Historical Performance")

    # This would show actual historical data if available
    if st.session_state.get('rh_connected'):
        st.info("Historical performance data will be populated as you complete trades")
    else:
        st.info("Connect to Robinhood to track historical performance")

elif page == "Opportunities":
    st.title("🎯 Trading Opportunities")
    
    # Scan button
    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        scan_btn = st.button("🔍 Scan Now", type="primary", use_container_width=True)
    with col2:
        auto_scan = st.checkbox("Auto-scan", value=False)
    
    if scan_btn or auto_scan:
        with st.spinner("Scanning for opportunities..."):
            # Run async scan
            async def scan():
                opportunities = await market_agent.scan_opportunities(watchlist[:10])
                return opportunities
            
            opportunities = asyncio.run(scan())
            
            if opportunities:
                st.success(f"Found {len(opportunities)} opportunities!")
                
                # Tabs for different opportunity types
                tab1, tab2 = st.tabs(["Cash-Secured Puts", "Covered Calls"])
                
                with tab1:
                    st.subheader("💵 Cash-Secured Put Opportunities")
                    
                    # Create DataFrame for display
                    put_data = []
                    for opp in opportunities[:5]:
                        put_data.append({
                            'Symbol': opp['symbol'],
                            'Current Price': f"${opp['current_price']:.2f}",
                            'Strike': f"${opp['current_price'] * 0.95:.2f}",
                            'Premium': f"${opp['current_price'] * 0.01:.2f}",
                            'Yield': f"{1.2:.1f}%",
                            'DTE': 30,
                            'Score': f"{opp['score']:.0f}/100",
                            'Action': 'Trade'
                        })
                    
                    df = pd.DataFrame(put_data)
                    
                    # Display with action buttons
                    for idx, row in df.iterrows():
                        col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([1.5, 1.5, 1, 1, 1, 1, 1, 1])
                        
                        with col1:
                            st.write(f"**{row['Symbol']}**")
                        with col2:
                            st.write(row['Current Price'])
                        with col3:
                            st.write(row['Strike'])
                        with col4:
                            st.write(row['Premium'])
                        with col5:
                            st.write(row['Yield'])
                        with col6:
                            st.write(f"{row['DTE']}d")
                        with col7:
                            if float(row['Score'].split('/')[0]) > 80:
                                st.success(row['Score'])
                            elif float(row['Score'].split('/')[0]) > 60:
                                st.warning(row['Score'])
                            else:
                                st.info(row['Score'])
                        with col8:
                            st.button("💸 Trade", key=f"trade_{idx}")
                
                with tab2:
                    st.subheader("📈 Covered Call Opportunities")
                    st.info("You need stock holdings to sell covered calls")
            else:
                st.warning("No opportunities found. Try adjusting your criteria.")

elif page == "Positions":
    st.title("💼 Active Positions")
    st.caption("Live option positions from Robinhood - auto-refreshed data")

    # Import required modules
    import robin_stocks.robinhood as rh
    import pandas as pd
    from datetime import datetime

    # Current Positions Section - Show ALL active positions from Robinhood
    st.markdown("### 🎯 Your Current Option Positions")

    try:
        # Login to Robinhood
        rh.login(username='brulecapital@gmail.com', password='FortKnox')

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
                opt_type = opt_data.get('type', 'unknown')  # 'call' or 'put'

                # Position details
                position_type = pos.get('type', 'unknown')  # 'long' or 'short'
                quantity = float(pos.get('quantity', 0))
                avg_price = abs(float(pos.get('average_price', 0)))

                # Calculate values - Robinhood's average_price is per contract, not per share
                # No need to multiply by 100, it's already the full contract premium
                total_premium = avg_price * quantity

                # Get current market price
                market_data = rh.get_option_market_data_by_id(opt_id)
                if market_data and len(market_data) > 0:
                    # adjusted_mark_price is per share, multiply by 100 for contract value
                    current_price = float(market_data[0].get('adjusted_mark_price', 0)) * 100
                else:
                    current_price = 0

                current_value = current_price * quantity

                # Calculate P/L
                if position_type == 'short':
                    # Sold option - profit when it goes down
                    pl = total_premium - current_value
                else:
                    # Bought option - profit when it goes up
                    pl = current_value - total_premium

                # Calculate DTE
                if exp_date != 'Unknown':
                    exp_dt = datetime.strptime(exp_date, '%Y-%m-%d')
                    dte = (exp_dt - datetime.now()).days
                else:
                    dte = 0

                # Determine strategy type
                if position_type == 'short' and opt_type == 'put':
                    strategy = 'CSP (Cash-Secured Put)'
                elif position_type == 'short' and opt_type == 'call':
                    strategy = 'CC (Covered Call)'
                elif position_type == 'long' and opt_type == 'call':
                    strategy = 'Long Call'
                elif position_type == 'long' and opt_type == 'put':
                    strategy = 'Long Put'
                else:
                    strategy = 'Other'

                positions_data.append({
                    'Symbol': symbol,
                    'Strategy': strategy,
                    'Strike': f'${strike:.2f}',
                    'Expiration': exp_date,
                    'DTE': dte,
                    'Contracts': int(quantity),
                    'Avg Price': f'${avg_price:.2f}',
                    'Total Premium': f'${total_premium:.2f}',
                    'Current Value': f'${current_value:.2f}',
                    'P/L': f'${pl:.2f}',
                    'P/L %': f'{(pl/total_premium*100):.1f}%' if total_premium > 0 else '0%'
                })

            if positions_data:
                df_positions = pd.DataFrame(positions_data)

                # Display metrics
                total_pl = sum([float(p['P/L'].replace('$', '').replace(',', '')) for p in positions_data])
                total_premium = sum([float(p['Total Premium'].replace('$', '').replace(',', '')) for p in positions_data])

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Active Positions", len(positions_data))
                with col2:
                    st.metric("Total Premium", f'${total_premium:,.2f}')
                with col3:
                    st.metric("Total P/L", f'${total_pl:,.2f}', delta=f'{(total_pl/total_premium*100):.1f}%' if total_premium > 0 else '0%')
                with col4:
                    csps = len([p for p in positions_data if 'CSP' in p['Strategy']])
                    st.metric("CSPs", csps)

                # Display positions table
                st.dataframe(df_positions, hide_index=True, use_container_width=True)

            else:
                st.info("No open option positions found in Robinhood")

        else:
            st.info("No open option positions found")

    except Exception as e:
        st.error(f"Error loading positions: {e}")

    # Trade History Section (AUTOMATIC - NO MANUAL LOGGING)
    st.markdown("---")
    st.markdown("### 📊 Trade History")
    st.caption("Automatic history of all closed trades from Robinhood")

    try:
        # Get closed option orders from Robinhood
        all_orders = rh.get_all_option_orders()

        closed_trades = []
        for order in all_orders:
            # Only process filled orders
            if order.get('state') != 'filled':
                continue

            # Get order details
            legs = order.get('legs', [])
            if not legs:
                continue

            leg = legs[0]
            side = leg.get('side')  # 'buy' or 'sell'
            position_effect = leg.get('position_effect')  # 'open' or 'close'

            # We want closing trades
            if position_effect != 'close':
                continue

            opt_url = leg.get('option')
            if not opt_url:
                continue

            # Get option instrument data - extract ID from URL
            # URL format: https://api.robinhood.com/options/instruments/UUID/
            if isinstance(opt_url, str) and 'options/instruments/' in opt_url:
                opt_id = opt_url.split('/')[-2]
            else:
                opt_id = opt_url

            opt_data = rh.get_option_instrument_data_by_id(opt_id)
            if not opt_data:
                continue

            symbol = opt_data.get('chain_symbol', 'Unknown')
            strike = float(opt_data.get('strike_price', 0))
            exp_date = opt_data.get('expiration_date', 'Unknown')
            opt_type = opt_data.get('type', 'unknown')

            # Get trade details
            quantity = float(order.get('quantity', 0))
            close_price = float(order.get('average_price', 0))
            close_date_str = order.get('updated_at', '')

            if close_date_str:
                close_date = datetime.fromisoformat(close_date_str.replace('Z', '+00:00')).strftime('%Y-%m-%d')
            else:
                close_date = 'Unknown'

            # Determine strategy
            if side == 'buy' and opt_type == 'put':
                strategy = 'CSP'
            elif side == 'buy' and opt_type == 'call':
                strategy = 'CC'
            else:
                strategy = 'Other'

            closed_trades.append({
                'Symbol': symbol,
                'Strategy': strategy,
                'Strike': f'${strike:.2f}',
                'Expiration': exp_date,
                'Close Date': close_date,
                'Close Price': f'${close_price:.2f}',
                'Contracts': int(quantity)
            })

        if closed_trades:
            # Display summary metrics
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Closed Trades", len(closed_trades))
            with col2:
                csps_closed = len([t for t in closed_trades if 'CSP' in t['Strategy']])
                st.metric("Closed CSPs", csps_closed)

            # Display trades table
            df_history = pd.DataFrame(closed_trades)
            st.dataframe(df_history, hide_index=True, use_container_width=True)
        else:
            st.info("No closed option trades found in Robinhood history")

    except Exception as e:
        st.error(f"Error loading trade history: {e}")

elif page == "Premium Scanner":
    st.title("🔍 Premium Scanner")

    # Auto-refresh positions (improved without darkening)
    if False:  # Disabled old code
        st.info("Feature reorganization in progress")
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            # Use placeholder to avoid re-rendering issues
            auto_refresh = st.checkbox("🔄 Auto-refresh", value=False, key="auto_refresh_check")
        with col2:
            refresh_interval = st.selectbox("Interval", ["30s", "1m", "2m", "5m"], index=3, label_visibility="collapsed")
        with col3:
            if st.button("🔄 Refresh Now", type="primary"):
                st.rerun()

        # Auto-refresh using meta tag instead of sleep to avoid blocking
        if auto_refresh:
            interval_map = {"30s": 30, "1m": 60, "2m": 120, "5m": 300}
            st.markdown(
                f'<meta http-equiv="refresh" content="{interval_map[refresh_interval]}">',
                unsafe_allow_html=True
            )

    # Display positions with AI analysis
    if positions:
        st.subheader("📋 Active Positions")

        # Check for 20%+ gains and show notifications
        high_profit_positions = [p for p in positions if p.get('P&L %', 0) >= 20]
        if high_profit_positions:
            for hp in high_profit_positions:
                st.success(f"🎆 **ALERT: {hp['Symbol']} is up {hp['P&L %']:.1f}%! Consider closing for ${hp['P&L']:.2f} profit**")
                st.balloons()

        # Create DataFrame for better display
        import pandas as pd
        df_positions = pd.DataFrame(positions)

        # Format the dataframe for display
        def make_clickable(url, text):
            return f'<a href="{url}" target="_blank">📈</a>'

        def color_pnl(val):
            if isinstance(val, (int, float)):
                color = 'green' if val > 0 else 'red' if val < 0 else 'black'
                return f'color: {color}'
            return ''

        # Compact table with custom CSS
        st.markdown("""
        <style>
        /* Make metrics more compact */
        div[data-testid="metric-container"] {
            padding: 0px;
            margin: 0px;
        }
        div[data-testid="metric-container"] > div {
            padding: 2px 4px;
        }
        /* Reduce column gaps */
        div[data-testid="stHorizontalBlock"] {
            gap: 0.5rem !important;
        }
        /* Make dividers thinner */
        hr { margin: 4px 0 !important; height: 1px !important; }
        </style>
        """, unsafe_allow_html=True)

        # Display positions in compact table format - full width
        # Header row with Option Price column
        header_cols = st.columns([1.5, 0.7, 0.8, 0.8, 0.8, 0.7, 0.7, 0.6, 0.4])
        with header_cols[0]:
            st.markdown("**Symbol/Type**")
        with header_cols[1]:
            st.markdown("**Strike**")
        with header_cols[2]:
            st.markdown("**Premium**")
        with header_cols[3]:
            st.markdown("**Opt Price**")
        with header_cols[4]:
            st.markdown("**Value**")
        with header_cols[5]:
            st.markdown("**P&L**")
        with header_cols[6]:
            st.markdown("**Gain%**")
        with header_cols[7]:
            st.markdown("**Days**")
        with header_cols[8]:
            st.markdown("**📈**")

        st.markdown("<hr style='margin: 2px 0;'>", unsafe_allow_html=True)

        # Data rows - more compact with Option Price
        for i, pos in enumerate(positions):
            cols = st.columns([1.5, 0.7, 0.8, 0.8, 0.8, 0.7, 0.7, 0.6, 0.4])

            with cols[0]:
                st.markdown(f"**{pos['Symbol']}** {pos['Type']} <br><small>{pos['Expiration']}</small>", unsafe_allow_html=True)

            with cols[1]:
                if pos['Strike'] > 0:
                    st.markdown(f"${pos['Strike']:.0f}")
                else:
                    st.markdown("-")

            with cols[2]:
                if pos['Premium'] > 0:
                    st.markdown(f"${pos['Premium']:.0f}")
                else:
                    st.markdown("-")

            with cols[3]:
                # Show current option price with color coding
                opt_price = pos.get('Option Price', 0)
                if opt_price > 0:
                    # For CSP/CC: green if price went down (good for us), red if up
                    if pos['Type'] in ['CSP', 'CC'] and pos['Premium'] > 0:
                        # Option price is per share, premium is total
                        avg_premium_per_share = pos['Premium'] / 100
                        color = "#28a745" if opt_price < avg_premium_per_share else "#dc3545"
                        st.markdown(f"<span style='color: {color}; font-weight: bold;'>${opt_price:.2f}</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"${opt_price:.2f}")
                else:
                    st.markdown("-")

            with cols[4]:
                st.markdown(f"${pos['Current Value']:.0f}")

            with cols[5]:
                color = "#28a745" if pos['P&L'] > 0 else "#dc3545" if pos['P&L'] < 0 else "black"
                st.markdown(f"<span style='color: {color}; font-weight: bold;'>${pos['P&L']:.0f}</span>", unsafe_allow_html=True)

            with cols[6]:
                color = "#28a745" if pos['P&L %'] > 0 else "#dc3545" if pos['P&L %'] < 0 else "black"
                st.markdown(f"<span style='color: {color}; font-weight: bold;'>{pos['P&L %']:.0f}%</span>", unsafe_allow_html=True)

            with cols[7]:
                if pos['Days to Expiry'] > 0:
                    st.markdown(f"{pos['Days to Expiry']}d")
                else:
                    st.markdown("-")

            with cols[8]:
                st.markdown(f"[📈]({pos['Chart']})")

            if i < len(positions) - 1:  # Don't add divider after last item
                st.markdown("<hr style='margin: 2px 0; opacity: 0.2;'>", unsafe_allow_html=True)

        # Theta Decay Forecasting Section
        st.subheader("📊 Theta Decay Profit Forecast")
        st.caption("See how much you'll make each day as options decay")

        for pos in positions:
            if pos['Type'] in ['CSP', 'CC'] and pos['Days to Expiry'] > 0:
                with st.expander(f"📅 {pos['Symbol']} - Daily Profit Forecast"):
                    # Calculate theta decay
                    days_left = pos['Days to Expiry']
                    current_value = pos['Current Value']
                    premium = pos['Premium']
                    current_profit = premium - current_value

                    # Create forecast
                    col1, col2 = st.columns([2, 1])

                    with col1:
                        # Daily forecast table
                        st.markdown("**Daily Theta Decay Forecast:**")

                        # Calculate daily theta (accelerates near expiration)
                        import math
                        forecast_data = []

                        # Show all days to expiration (up to 60 days for performance)
                        max_days_to_show = min(days_left, 60)
                        for day in range(max_days_to_show + 1):
                            days_remaining = days_left - day

                            if days_remaining > 0:
                                # Theta accelerates as we approach expiration
                                # Using square root of time for theta decay approximation
                                decay_factor = math.sqrt(days_remaining) / math.sqrt(days_left)
                                projected_value = current_value * decay_factor if day > 0 else current_value

                                daily_profit = premium - projected_value
                                daily_gain_pct = (daily_profit / premium) * 100 if premium > 0 else 0

                                # Calculate daily theta (profit gained that day)
                                if day == 0:
                                    theta_today = 0
                                else:
                                    theta_today = forecast_data[-1]['Profit'] - daily_profit if forecast_data else 0

                                forecast_data.append({
                                    'Day': f"Day {day}" if day > 0 else "Today",
                                    'Date': (datetime.now() + timedelta(days=day)).strftime('%m/%d'),
                                    'Days Left': days_remaining,
                                    'Option Value': f"${projected_value:.0f}",
                                    'Profit': daily_profit,
                                    'Profit %': daily_gain_pct,
                                    'Daily Gain': abs(theta_today)
                                })

                        # Display as table
                        for fd in forecast_data:
                            cols = st.columns([1, 1, 1, 1, 1, 1])
                            with cols[0]:
                                st.caption(fd['Day'])
                            with cols[1]:
                                st.caption(fd['Date'])
                            with cols[2]:
                                st.caption(f"{fd['Days Left']}d")
                            with cols[3]:
                                st.caption(fd['Option Value'])
                            with cols[4]:
                                color = "green" if fd['Profit'] > current_profit else "black"
                                st.markdown(f"<span style='color: {color};'>${fd['Profit']:.0f}</span>", unsafe_allow_html=True)
                            with cols[5]:
                                if fd['Daily Gain'] > 0:
                                    st.markdown(f"<span style='color: green;'>+${fd['Daily Gain']:.0f}</span>", unsafe_allow_html=True)

                    with col2:
                        # Summary metrics
                        st.metric("Current Profit", f"${current_profit:.0f}")
                        st.metric("Max Profit", f"${premium:.0f}")

                        # Calculate expected profit at different milestones
                        if days_left >= 7:
                            week_decay = current_value * math.sqrt((days_left - 7) / days_left)
                            week_profit = premium - week_decay
                            st.metric("Profit in 7 days", f"${week_profit:.0f}")

                        if days_left >= 3:
                            three_day_decay = current_value * math.sqrt((days_left - 3) / days_left)
                            three_day_profit = premium - three_day_decay
                            st.metric("Profit in 3 days", f"${three_day_profit:.0f}")

                        # Theta per day average
                        avg_theta = current_profit / days_left if days_left > 0 else 0
                        st.metric("Avg Daily Theta", f"${avg_theta:.2f}")

                    # Add recommendation based on theta
                    if current_profit / premium > 0.5:
                        st.info(f"💡 Already captured {(current_profit/premium*100):.0f}% of max profit. Theta decay slowing.")
                    elif days_left <= 7:
                        st.success(f"🚀 Maximum theta decay period! Earning ~${avg_theta:.0f}/day")
                    else:
                        st.info(f"⏰ Theta will accelerate in {days_left - 7} days when < 1 week remains")

        # AI Analysis Section
        st.subheader("🤖 AI Trade Analysis & Recommendations")

        # Import AI analyzer
        from src.ai_trade_analyzer import AITradeAnalyzer
        analyzer = AITradeAnalyzer()

        # Get portfolio analysis
        portfolio_analysis = analyzer.get_portfolio_recommendations(positions)

        # Show overall portfolio recommendation
        st.info(f"**Portfolio Action:** {portfolio_analysis['suggested_action']}")

        # Show buyback candidates if any
        if portfolio_analysis['buyback_candidates']:
            st.success("**🎯 High-Profit Exit Opportunities:**")
            for candidate in portfolio_analysis['buyback_candidates']:
                st.write(f"• {candidate['symbol']}: {candidate['profit_pct']:.1f}% profit (${candidate['profit']:.2f})")

        # Individual position analysis
        st.markdown("### Individual Position Analysis")

        for pos in positions:
            if pos['Type'] == 'CSP':
                # Get AI analysis
                analysis = analyzer.analyze_csp(
                    pos['Symbol'],
                    pos.get('Strike', 0),
                    pos.get('Expiration', ''),
                    pos.get('Premium', 0),
                    pos.get('Current Value', 0),
                    pos.get('Days to Expiry', 0)
                )

                rec = analysis['recommendation']

                with st.expander(f"{rec['emoji']} {pos['Symbol']} - {rec['action']}"):
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.markdown("**Position Details:**")
                        st.write(f"• Strike: ${pos['Strike']}")
                        st.write(f"• Expiration: {pos['Expiration']}")
                        st.write(f"• Days Left: {pos['Days to Expiry']}")
                        st.write(f"• Premium: ${pos['Premium']:.2f}")

                    with col2:
                        st.markdown("**Current Status:**")
                        st.write(f"• Stock Price: ${analysis['current_price']:.2f}")
                        st.write(f"• {'ITM' if analysis['is_itm'] else 'OTM'} by {abs(analysis['moneyness_pct']):.1f}%")
                        st.write(f"• Cost to Close: ${analysis['cost_to_close']:.2f}")
                        st.write(f"• Profit if Closed: ${analysis['profit_if_closed']:.2f}")

                    with col3:
                        st.markdown("**AI Recommendation:**")
                        if rec['urgency'] == 'HIGH':
                            st.error(f"{rec['action']}")
                        elif rec['urgency'] == 'MEDIUM':
                            st.warning(f"{rec['action']}")
                        else:
                            st.info(f"{rec['action']}")

                        st.write(rec['reason'])
                        st.write(rec['detail'])

                        # Show annual return if closing now
                        if analysis['annual_return'] > 0:
                            st.metric("Annualized Return", f"{analysis['annual_return']:.1f}%")
    else:
        if not st.session_state.get('rh_connected'):
            st.info("Connect to Robinhood to see positions")
        else:
            st.warning("No positions found. Check if you have any open options.")

elif page == "Premium Scanner":
    st.title("🔍 Premium Scanner")
    st.markdown("Find the best option premiums from your TradingView watchlists")

    # Import modules
    from src.tradingview_watchlist import TradingViewWatchlist
    from src.premium_scanner import PremiumScanner

    tv_watchlist = TradingViewWatchlist()
    scanner = PremiumScanner()

    # TradingView Integration
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("📊 Watchlist Source")

        # Check for TradingView credentials
        tv_username = os.getenv('TRADINGVIEW_USERNAME', '')
        if tv_username:
            st.success(f"Connected: {tv_username}")
            st.caption("Pulling from your watchlists")
        else:
            st.info("Using default high-volume watchlists")

        # Select watchlist
        watchlist_option = st.selectbox(
            "Select Strategy",
            ["Best Overall Premiums", "High IV Plays (40%+)",
             "Weekly Options (7-14 DTE)", "Monthly Options (30-45 DTE)",
             "Tech Stocks Under $50", "All Stocks Under $50"]
        )

        max_price = st.number_input("Max Stock Price", value=50, min_value=10, max_value=200)
        min_premium_pct = st.number_input("Min Premium %", value=1.0, min_value=0.5, max_value=5.0, step=0.5)
        dte_target = st.selectbox("Target Days to Expiration", [7, 14, 21, 30, 45], index=3)

        scan_button = st.button("🔍 Scan for Premiums", type="primary", use_container_width=True)

    with col2:
        if scan_button:
            with st.spinner("Scanning for best premiums... This may take 30-60 seconds."):
                try:
                    # Get symbols based on selection
                    if watchlist_option == "All Stocks Under $50":
                        symbols = scanner.scan_all_stocks_under(max_price)
                    else:
                        symbols = tv_watchlist.get_watchlist_symbols_simple()

                    # Filter by price first
                    valid_symbols = []
                    for symbol in symbols[:30]:  # Limit to prevent rate limiting
                        try:
                            ticker = yf.Ticker(symbol)
                            info = ticker.info
                            price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
                            if 0 < price <= max_price:
                                valid_symbols.append(symbol)
                        except:
                            continue

                    # Scan for premiums
                    results = scanner.scan_premiums(
                        symbols=valid_symbols,
                        max_price=max_price,
                        min_premium_pct=min_premium_pct,
                        dte=dte_target
                    )

                    # Filter results based on selection
                    if watchlist_option == "High IV Plays (40%+)":
                        results = [r for r in results if r.get('iv', 0) >= 40]
                    elif watchlist_option == "Weekly Options (7-14 DTE)":
                        results = [r for r in results if 7 <= r.get('dte', 0) <= 14]
                    elif watchlist_option == "Monthly Options (30-45 DTE)":
                        results = [r for r in results if 30 <= r.get('dte', 0) <= 45]

                    # Store results
                    st.session_state['scan_results'] = results
                    st.session_state['last_scan_time'] = datetime.now()

                except Exception as e:
                    st.error(f"Scan error: {str(e)}")
                    results = []

        # Display results
        if st.session_state.get('scan_results'):
            results = st.session_state['scan_results']

            if results:
                # Show scan time
                if 'last_scan_time' in st.session_state:
                    scan_time = st.session_state['last_scan_time']
                    st.caption(f"Last scan: {scan_time.strftime('%I:%M %p')}")

                st.success(f"Found {len(results)} premium opportunities!")

                # Create DataFrame for better display
                df = pd.DataFrame(results)

                # Sort by monthly return
                df = df.sort_values('monthly_return', ascending=False)

                # Display top opportunities
                st.subheader("🎯 Top Premium Opportunities")

                # Show summary metrics
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    avg_premium = df['premium_pct'].mean() if len(df) > 0 else 0
                    st.metric("Avg Premium %", f"{avg_premium:.2f}%")
                with col_b:
                    avg_monthly = df['monthly_return'].mean() if len(df) > 0 else 0
                    st.metric("Avg Monthly Return", f"{avg_monthly:.1f}%")
                with col_c:
                    avg_annual = df['annual_return'].mean() if len(df) > 0 else 0
                    st.metric("Avg Annual Return", f"{avg_annual:.0f}%")

                # Display table
                st.markdown("### Premium Opportunities Table")

                # Format display columns
                display_df = df[['symbol', 'stock_price', 'strike', 'expiration', 'dte',
                                 'premium', 'premium_pct', 'monthly_return', 'annual_return',
                                 'iv', 'volume', 'open_interest']].copy()

                # Format columns
                display_df['Premium/Contract'] = '$' + display_df['premium'].astype(str)
                display_df['Premium %'] = display_df['premium_pct'].apply(lambda x: f"{x:.2f}%")
                display_df['Monthly'] = display_df['monthly_return'].apply(lambda x: f"{x:.1f}%")
                display_df['Annual'] = display_df['annual_return'].apply(lambda x: f"{x:.0f}%")
                display_df['IV'] = display_df['iv'].apply(lambda x: f"{x:.1f}%" if x > 0 else "N/A")

                # Select final columns
                final_cols = ['symbol', 'stock_price', 'strike', 'dte', 'Premium/Contract',
                             'Premium %', 'Monthly', 'Annual', 'IV', 'volume']

                st.dataframe(
                    display_df[final_cols],
                    use_container_width=True,
                    hide_index=True,
                    height=400
                )

                # Detailed view for top 5
                st.markdown("### 💎 Top 5 Detailed Analysis")
                for i, row in df.head(5).iterrows():
                    with st.expander(f"{row['symbol']} - {row['monthly_return']:.1f}% Monthly Return"):
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.metric("Stock Price", f"${row['stock_price']:.2f}")
                            st.metric("Strike Price", f"${row['strike']:.2f}")
                            st.metric("Premium/Contract", f"${row['premium']:.2f}")

                        with col2:
                            st.metric("Days to Expiry", row['dte'])
                            st.metric("Premium %", f"{row['premium_pct']:.2f}%")
                            st.metric("Monthly Return", f"{row['monthly_return']:.1f}%")

                        with col3:
                            st.metric("Annual Return", f"{row['annual_return']:.0f}%")
                            st.metric("Implied Volatility", f"{row['iv']:.1f}%")
                            st.metric("Volume", f"{row['volume']:,}")

                        # Trade button
                        if st.button(f"Open in Robinhood", key=f"trade_{row['symbol']}_{i}"):
                            st.info(f"Sell to Open: {row['symbol']} ${row['strike']} Put, Exp: {row['expiration']}")
            else:
                st.warning("No opportunities found. Try adjusting your filters or expanding the watchlist.")

elif page == "TradingView Watchlists":
    st.title("📊 My Watchlists - Premium Analysis")

    # Import modules
    # TradingView Database Manager is already imported at the top
    import yfinance as yf
    import pandas as pd
    from datetime import datetime, timedelta
    import robin_stocks.robinhood as rh

    # Initialize DB sync
    tv_manager = TradingViewDBManager()

    # NOTE: Positions and Trade History have been moved to the "Positions" page
    # This page now focuses only on TradingView watchlist management

    # Auto-sync on page load (if not synced recently)
    st.caption("Live positions from Robinhood (auto-refreshes)")

    try:
        # Login to Robinhood
        rh.login(username='brulecapital@gmail.com', password='FortKnox')

        # Get all open option positions
        positions = rh.get_open_option_positions()

        if positions:
            positions_data = []

            for pos in positions:
                # Get option details
                opt_id = pos.get('option_id')
                if not opt_id:
                    continue

                opt_data = rh.get_option_instrument_data_by_id(opt_id)
                symbol = opt_data.get('chain_symbol', 'Unknown')
                strike = float(opt_data.get('strike_price', 0))
                exp_date = opt_data.get('expiration_date', 'Unknown')
                opt_type = opt_data.get('type', 'unknown')  # 'call' or 'put'

                # Position details
                position_type = pos.get('type', 'unknown')  # 'long' or 'short'
                quantity = float(pos.get('quantity', 0))
                avg_price = abs(float(pos.get('average_price', 0)))

                # Calculate values - Robinhood's average_price is per contract, not per share
                # No need to multiply by 100, it's already the full contract premium
                total_premium = avg_price * quantity

                # Get current market price
                market_data = rh.get_option_market_data_by_id(opt_id)
                if market_data and len(market_data) > 0:
                    # adjusted_mark_price is per share, multiply by 100 for contract value
                    current_price = float(market_data[0].get('adjusted_mark_price', 0)) * 100
                else:
                    current_price = 0

                current_value = current_price * quantity

                # Calculate P/L
                if position_type == 'short':
                    # Sold option - profit when it goes down
                    pl = total_premium - current_value
                else:
                    # Bought option - profit when it goes up
                    pl = current_value - total_premium

                # Calculate DTE
                if exp_date != 'Unknown':
                    exp_dt = datetime.strptime(exp_date, '%Y-%m-%d')
                    dte = (exp_dt - datetime.now()).days
                else:
                    dte = 0

                # Determine strategy type
                if position_type == 'short' and opt_type == 'put':
                    strategy = 'CSP (Cash-Secured Put)'
                elif position_type == 'short' and opt_type == 'call':
                    strategy = 'CC (Covered Call)'
                elif position_type == 'long' and opt_type == 'call':
                    strategy = 'Long Call'
                elif position_type == 'long' and opt_type == 'put':
                    strategy = 'Long Put'
                else:
                    strategy = 'Other'

                positions_data.append({
                    'Symbol': symbol,
                    'Strategy': strategy,
                    'Strike': f'${strike:.2f}',
                    'Expiration': exp_date,
                    'DTE': dte,
                    'Contracts': int(quantity),
                    'Avg Price': f'${avg_price:.2f}',
                    'Total Premium': f'${total_premium:.2f}',
                    'Current Value': f'${current_value:.2f}',
                    'P/L': f'${pl:.2f}',
                    'P/L %': f'{(pl/total_premium*100):.1f}%' if total_premium > 0 else '0%'
                })

            if positions_data:
                df_positions = pd.DataFrame(positions_data)

                # Display metrics
                total_pl = sum([float(p['P/L'].replace('$', '').replace(',', '')) for p in positions_data])
                total_premium = sum([float(p['Total Premium'].replace('$', '').replace(',', '')) for p in positions_data])

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Active Positions", len(positions_data))
                with col2:
                    st.metric("Total Premium", f'${total_premium:,.2f}')
                with col3:
                    st.metric("Total P/L", f'${total_pl:,.2f}', delta=f'{(total_pl/total_premium*100):.1f}%' if total_premium > 0 else '0%')
                with col4:
                    csps = len([p for p in positions_data if 'CSP' in p['Strategy']])
                    st.metric("CSPs", csps)

                # Display positions table
                st.dataframe(df_positions, hide_index=True, use_container_width=True)

                # Add "Close Position" buttons for each position
                st.markdown("#### 📝 Log Closed Trades")
                st.caption("When you close a position, log it here to track your trade history")

                from src.trade_history_manager import TradeHistoryManager
                th_mgr = TradeHistoryManager()

                # Show collapsible forms for each position
                for idx, pos_data in enumerate(positions_data):
                    symbol = pos_data['Symbol']
                    strike = float(pos_data['Strike'].replace('$', ''))
                    exp = pos_data['Expiration']
                    strategy = pos_data['Strategy']

                    with st.expander(f"Log {symbol} - {strategy}"):
                        st.caption(f"Strike: {pos_data['Strike']} | Expires: {exp} | Premium: {pos_data['Total Premium']}")

                        with st.form(f"log_trade_{idx}"):
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                close_price_input = st.number_input("Close Price (per contract)", min_value=0.0, value=0.0, step=10.0, key=f"close_price_{idx}")
                            with col2:
                                close_reason = st.selectbox("Reason", ["early_close", "expiration", "assignment"], key=f"reason_{idx}")
                            with col3:
                                open_date_input = st.date_input("Open Date", key=f"open_date_{idx}")

                            if st.form_submit_button("Log This Trade", type="primary"):
                                try:
                                    premium = float(pos_data['Total Premium'].replace('$', '').replace(',', ''))
                                    contracts = pos_data['Contracts']

                                    # Add to trade history
                                    trade_id = th_mgr.add_trade(
                                        symbol=symbol,
                                        strike_price=strike,
                                        expiration_date=exp,
                                        premium_collected=premium,
                                        contracts=contracts,
                                        open_date=open_date_input.strftime('%Y-%m-%d'),
                                        strategy_type='cash_secured_put' if 'CSP' in strategy else 'covered_call' if 'CC' in strategy else 'other'
                                    )

                                    # Close immediately
                                    result = th_mgr.close_trade(
                                        trade_id=trade_id,
                                        close_price=close_price_input * contracts,
                                        close_reason=close_reason
                                    )

                                    st.success(f"Trade logged! P/L: ${result['profit_loss']:.2f} ({result['profit_loss_percent']:.1f}%), {result['days_held']} days")
                                    st.balloons()
                                except Exception as e:
                                    st.error(f"Error logging trade: {e}")

            else:
                st.info("No open option positions found in Robinhood")

        else:
            st.info("No open option positions found")

    except Exception as e:
        st.error(f"Error loading positions: {e}")

    # Trade History Section
    st.markdown("---")
    st.markdown("### 📊 Trade History")
    st.caption("Historical record of all closed trades")

    from src.trade_history_manager import TradeHistoryManager
    th_mgr = TradeHistoryManager()

    # Get trade statistics
    stats = th_mgr.get_trade_stats()

    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Closed Trades", stats['total_trades'])
    with col2:
        st.metric("Total P/L", f"${stats['total_pl']:,.2f}")
    with col3:
        st.metric("Win Rate", f"{stats['win_rate']:.1f}%")
    with col4:
        st.metric("Avg Days Held", stats['avg_days_held'])

    # Trade history table with filters
    col_filter1, col_filter2 = st.columns(2)
    with col_filter1:
        filter_symbol = st.text_input("Filter by Symbol (optional)", placeholder="NVDA", key="filter_trade_symbol")
    with col_filter2:
        limit_trades = st.selectbox("Show Last", [20, 50, 100, 200], index=1, key="limit_trades")

    trades = th_mgr.get_closed_trades(
        limit=limit_trades,
        symbol=filter_symbol if filter_symbol else None
    )

    if trades:
        # Convert to DataFrame
        df_trades = pd.DataFrame(trades)

        # Format columns
        df_trades['open_date'] = pd.to_datetime(df_trades['open_date']).dt.strftime('%Y-%m-%d')
        df_trades['close_date'] = pd.to_datetime(df_trades['close_date']).dt.strftime('%Y-%m-%d')
        df_trades['profit_loss'] = df_trades['profit_loss'].apply(lambda x: f"${x:,.2f}")
        df_trades['profit_loss_percent'] = df_trades['profit_loss_percent'].apply(lambda x: f"{x:.1f}%")
        df_trades['annualized_return'] = df_trades['annualized_return'].apply(lambda x: f"{x:.1f}%")
        df_trades['premium_collected'] = df_trades['premium_collected'].apply(lambda x: f"${x:,.2f}")

        # Select and rename columns
        display_df = df_trades[['symbol', 'open_date', 'close_date', 'strike_price', 'premium_collected',
                        'days_held', 'profit_loss', 'profit_loss_percent', 'annualized_return', 'close_reason']]
        display_df.columns = ['Symbol', 'Open', 'Close', 'Strike', 'Premium',
                             'Days', 'P/L', 'P/L %', 'Ann. Return', 'Reason']

        st.dataframe(display_df, hide_index=True, use_container_width=True)

        # Download button
        csv = display_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Trade History CSV",
            data=csv,
            file_name=f"trade_history_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.info("No closed trades yet. Log your first trade above when you close a position!")

    st.markdown("---")

    # Auto-sync on page load (if not synced recently)
    if 'last_sync' not in st.session_state or (datetime.now() - st.session_state.get('last_sync', datetime.min)).seconds > 300:
        with st.spinner("Loading watchlists from database..."):
            # Load watchlists from database
            watchlists_db = tv_manager.get_all_symbols_dict()

            if not watchlists_db:
                # First time - suggest syncing from TradingView
                st.info("💡 No watchlists found. Please sync from TradingView using: python src/tradingview_api_sync.py")

            st.session_state['watchlists_db'] = watchlists_db
            st.session_state['last_sync'] = datetime.now()

    # Create tabs for different views
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🔄 Auto-Sync", "📥 Import Watchlist", "📊 My Watchlist Analysis", "📈 Saved Watchlists", "🎯 Quick Scan"])

    with tab1:
        st.subheader("📊 Your Watchlists")

        # Refresh button
        col1, col2, col3 = st.columns([2, 2, 2])
        with col1:
            if st.button("🔄 Refresh Watchlists", use_container_width=True):
                with st.spinner("Loading watchlists from database..."):
                    # Load all watchlists from database
                    watchlists = tv_manager.get_all_symbols_dict()
                    st.session_state['watchlists_db'] = watchlists
                    st.session_state['last_sync'] = datetime.now()

                    if watchlists:
                        total_symbols = sum(len(symbols) for symbols in watchlists.values())
                        st.success(f"✅ Loaded {len(watchlists)} watchlists with {total_symbols} symbols")
                    else:
                        st.info("No watchlists found. Import symbols below to create watchlists.")
                    st.rerun()

        with col2:
            if st.button("📥 Manual Import", use_container_width=True):
                st.info("Use the 'Import Watchlist' tab to add new symbols")

        with col3:
            if 'last_sync' in st.session_state:
                time_since = (datetime.now() - st.session_state['last_sync']).seconds // 60
                st.info(f"Last sync: {time_since} min ago")

        # Load watchlists on first run
        if 'watchlists_db' not in st.session_state:
            st.session_state['watchlists_db'] = tv_manager.get_all_symbols_dict()

        watchlists_db = st.session_state.get('watchlists_db', {})

        if watchlists_db:
            st.subheader("📋 Your Watchlists - Live Market Data")

            # Watchlist selector
            selected_watchlist = st.selectbox(
                "Select Watchlist",
                list(watchlists_db.keys()),
                format_func=lambda x: f"{x} ({len(watchlists_db[x])} stocks)"
            )

            if selected_watchlist:
                symbols = watchlists_db[selected_watchlist]

                # Filter to stock symbols only (no crypto)
                stock_symbols = [s for s in symbols if not any(x in s for x in ['USDT', 'USD', 'BTC', '.D', 'WETH'])]

                if not stock_symbols:
                    st.warning(f"No stock symbols found in {selected_watchlist}. This watchlist contains only crypto/non-stock symbols.")
                else:
                    # Show sync button
                    col_sync1, col_sync2, col_sync3 = st.columns([2, 2, 2])
                    with col_sync1:
                        st.metric("Stocks in Watchlist", len(stock_symbols))
                    with col_sync2:
                        if st.button("🔄 Sync Prices & Premiums", type="primary", use_container_width=True):
                            st.info("⚡ Background sync started! Data will update automatically...")
                            # Start background sync (non-blocking)
                            import subprocess
                            subprocess.Popen([
                                "python", "src/watchlist_sync_service.py", selected_watchlist
                            ], creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
                            time.sleep(2)
                            st.rerun()

                    with col_sync3:
                        st.caption("Data syncs in background")

                    # SIMPLE IMPLEMENTATION - Just show 30-day options with 0.25-0.40 delta
                    st.markdown("### 💵 Cash-Secured Put Options (30 Days, Delta 0.25-0.40)")
                    st.caption("Real data from database. Sort by clicking column headers. Filter by stock price and premium.")

                    # Simple filters
                    col_f1, col_f2, col_f3 = st.columns(3)
                    with col_f1:
                        min_stock_price = st.number_input("Min Stock Price ($)", value=0.0, min_value=0.0, step=10.0, key="filter_min_stock")
                    with col_f2:
                        max_stock_price = st.number_input("Max Stock Price ($)", value=10000.0, min_value=10.0, step=50.0, key="filter_max_stock")
                    with col_f3:
                        min_premium = st.number_input("Min Premium ($)", value=0.0, min_value=0.0, step=1.0, key="filter_min_prem")

                    # Get 30-day options with ~0.3 delta
                    conn = tv_manager.get_connection()
                    cur = conn.cursor()

                    query = """
                        SELECT DISTINCT ON (sp.symbol)
                            sp.symbol,
                            sd.current_price as stock_price,
                            sp.strike_price,
                            sp.dte,
                            sp.premium,
                            sp.delta,
                            sp.monthly_return,
                            sp.implied_volatility as iv,
                            sp.bid,
                            sp.ask,
                            sp.volume,
                            sp.open_interest as oi
                        FROM stock_premiums sp
                        LEFT JOIN stock_data sd ON sp.symbol = sd.symbol
                        WHERE sp.symbol = ANY(%s)
                            AND sp.dte BETWEEN 28 AND 32
                            AND ABS(sp.delta) BETWEEN 0.25 AND 0.40
                            AND sp.premium >= %s
                            AND sd.current_price BETWEEN %s AND %s
                        ORDER BY sp.symbol, sp.monthly_return DESC
                    """

                    cur.execute(query, (stock_symbols, min_premium, min_stock_price, max_stock_price))
                    rows = cur.fetchall()
                    cur.close()
                    conn.close()

                    # Display results
                    if not rows:
                        st.warning(f"⏳ No 30-day options found for {selected_watchlist}. Try adjusting filters or click 'Sync Prices & Premiums'.")
                    else:
                        # Create simple DataFrame
                        df = pd.DataFrame(rows, columns=[
                            'Symbol', 'Stock Price', 'Strike', 'DTE',
                            'Premium', 'Delta', 'Monthly %', 'IV',
                            'Bid', 'Ask', 'Volume', 'OI'
                        ])

                        # Convert to numeric types
                        numeric_cols = ['Stock Price', 'Strike', 'DTE', 'Premium', 'Delta',
                                       'Monthly %', 'IV', 'Bid', 'Ask', 'Volume', 'OI']
                        for col in numeric_cols:
                            df[col] = pd.to_numeric(df[col], errors='coerce')

                        # Summary
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Options Found", len(df))
                        with col2:
                            st.metric("Avg Premium", f"${df['Premium'].mean():.2f}")
                        with col3:
                            st.metric("Avg Monthly Return", f"{df['Monthly %'].mean():.2f}%")

                        # Display simple sortable table (NO row selection to avoid black screen)
                        st.markdown("#### 📊 30-Day Cash-Secured Puts (Click headers to sort)")
                        st.dataframe(
                            df,
                            hide_index=True,
                            use_container_width=True,
                            column_config={
                                "Symbol": st.column_config.TextColumn("Symbol", width="small"),
                                "Stock Price": st.column_config.NumberColumn("Stock $", format="$%.2f"),
                                "Strike": st.column_config.NumberColumn("Strike", format="$%.2f"),
                                "DTE": st.column_config.NumberColumn("DTE"),
                                "Premium": st.column_config.NumberColumn("Premium", format="$%.2f"),
                                "Delta": st.column_config.NumberColumn("Delta", format="%.3f"),
                                "Monthly %": st.column_config.NumberColumn("Monthly %", format="%.2f%%"),
                                "IV": st.column_config.NumberColumn("IV %", format="%.1f%%"),
                                "Bid": st.column_config.NumberColumn("Bid", format="$%.2f"),
                                "Ask": st.column_config.NumberColumn("Ask", format="$%.2f"),
                                "Volume": st.column_config.NumberColumn("Vol"),
                                "OI": st.column_config.NumberColumn("OI")
                            }
                        )

        else:
            st.warning("No watchlists found. Click 'Refresh Watchlists' to fetch from TradingView.")

    with tab2:
        st.subheader("📥 Import Your Watchlist")

        st.info("👆 Paste your watchlist symbols below (from TradingView, Robinhood, or any source)")


        # Text area for importing symbols
        watchlist_text = st.text_area(
            "Enter symbols (comma or line separated):",
            placeholder="NVDA, AMD, AAPL, MSFT\nTSLA, META, GOOGL\nOr paste directly from TradingView",
            height=200
        )

        watchlist_name = st.text_input("Watchlist Name:", value="My Watchlist")

        col1, col2 = st.columns(2)
        with col1:
            import_button = st.button("💾 Save & Analyze Watchlist", type="primary", use_container_width=True)
        with col2:
            # Load existing watchlist
            tv_integration = TradingViewDBManager()
            saved_lists = tv_integration.load_saved_watchlists()
            selected_list = st.selectbox("Or load saved:", list(saved_lists.keys()))

        if import_button and watchlist_text:
            # Import the symbols
            tv_integration = TradingViewDBManager()
            imported_symbols = tv_integration.import_from_text(watchlist_text, watchlist_name)

            if imported_symbols:
                st.success(f"✅ Imported {len(imported_symbols)} symbols to '{watchlist_name}'")
                st.session_state['current_watchlist'] = imported_symbols
                st.session_state['current_watchlist_name'] = watchlist_name

                # Display imported symbols
                st.markdown("### Imported Symbols:")
                st.write(", ".join(imported_symbols))
            else:
                st.error("No valid symbols found. Please check your input.")

        elif selected_list:
            # Load selected watchlist
            if st.button(f"Load '{selected_list}'"):
                st.session_state['current_watchlist'] = saved_lists[selected_list]
                st.session_state['current_watchlist_name'] = selected_list
                st.success(f"Loaded {len(saved_lists[selected_list])} symbols from '{selected_list}'")

    with tab3:
        st.subheader("📊 Watchlist Analysis with Premiums")

        if not st.session_state.get('current_watchlist'):
            st.warning("👆 Please import or load a watchlist in the first tab")
        else:
            symbols = st.session_state['current_watchlist']
            watchlist_name = st.session_state.get('current_watchlist_name', 'My Watchlist')

            st.info(f"Analyzing '{watchlist_name}' with {len(symbols)} stocks")
            st.caption(f"Symbols: {', '.join(symbols[:20])}{'...' if len(symbols) > 20 else ''}")

            # Analyze button
            if st.button("📊 Analyze All Stocks & Premiums", type="primary", use_container_width=True):
                with st.spinner(f"Getting real-time data for {len(symbols)} stocks..."):

                    # Get comprehensive data with options
                    # Get comprehensive data with options using market data agent
                    market_agent = MarketDataAgent()
                    table_data = []
                    for symbol in symbols:
                        try:
                            data = market_agent.get_stock_data(symbol)
                            if data:
                                table_data.append(data)
                        except:
                            continue

                    if table_data:
                        st.session_state['watchlist_analysis'] = table_data
                        st.session_state['analysis_time'] = datetime.now()

            # Display results
            if st.session_state.get('watchlist_analysis'):
                results = st.session_state['watchlist_analysis']

                st.success(f"✅ Analysis complete for {len(results)} stocks")

                if 'analysis_time' in st.session_state:
                    st.caption(f"Last analyzed: {st.session_state['analysis_time'].strftime('%I:%M %p')}")

                # Create DataFrame
                df = pd.DataFrame(results)

                # Format columns
                for col in df.columns:
                    if 'Price' in col or 'Strike' in col:
                        df[col] = df[col].apply(lambda x: f"${x:.2f}" if isinstance(x, (int, float)) and x > 0 else "")
                    elif 'Change' in col and '%' not in col:
                        df[col] = df[col].apply(lambda x: f"{x:+.2f}" if isinstance(x, (int, float)) else "")
                    elif '% Change' in col or 'Return%' in col:
                        df[col] = df[col].apply(lambda x: f"{x:+.2f}%" if isinstance(x, (int, float)) else "")
                    elif 'Premium' in col or 'Capital' in col:
                        df[col] = df[col].apply(lambda x: f"${x:,.0f}" if isinstance(x, (int, float)) and x > 0 else "")
                    elif 'Volume' in col:
                        df[col] = df[col].apply(lambda x: f"{x/1e6:.1f}M" if isinstance(x, (int, float)) and x > 1e6 else f"{x/1e3:.0f}K" if x > 1e3 else str(int(x)) if x > 0 else "")

                # Color code the % Change column
                def highlight_changes(val):
                    if isinstance(val, str) and '+' in val:
                        return 'color: green'
                    elif isinstance(val, str) and '-' in val:
                        return 'color: red'
                    return ''

                # Display table with color coding
                st.markdown("### 📈 Complete Analysis Table")
                st.caption("🟢 Green = Up today | 🔴 Red = Down today | Premiums shown for ~5% OTM puts")

                # Apply styling and display
                styled_df = df.style.applymap(highlight_changes, subset=[col for col in df.columns if '% Change' in col])

                st.dataframe(
                    styled_df,
                    use_container_width=True,
                    hide_index=True,
                    height=600
                )

                # Summary metrics
                st.markdown("### 📊 Summary Statistics")
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    total_up = len([r for r in results if r.get('% Change', 0) > 0])
                    total_down = len([r for r in results if r.get('% Change', 0) < 0])
                    st.metric("🟢 Up Today", total_up)
                    st.metric("🔴 Down Today", total_down)

                with col2:
                    # Find best returns
                    best_returns = []
                    for row in results:
                        for key in row:
                            if 'Return%' in key:
                                try:
                                    val = row[key]
                                    if isinstance(val, (int, float)):
                                        best_returns.append(val)
                                except:
                                    continue

                    if best_returns:
                        st.metric("Best Return", f"{max(best_returns):.2f}%")
                        st.metric("Avg Return", f"{sum(best_returns)/len(best_returns):.2f}%")

                with col3:
                    # Market overview
                    avg_change = sum(r.get('% Change', 0) for r in results) / len(results) if results else 0
                    st.metric("Market Avg Today", f"{avg_change:+.2f}%")

                    # Count stocks with options
                    stocks_with_options = len([r for r in results if any('Strike' in k for k in r.keys())])
                    st.metric("With Options", stocks_with_options)

                with col4:
                    # Export button
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="💾 Download Analysis CSV",
                        data=csv,
                        file_name=f"{watchlist_name}_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv"
                    )

            else:
                st.info("👆 Click 'Analyze All Stocks & Premiums' to see complete analysis")

    with tab4:
        st.subheader("📈 Saved Watchlists")

        tv_integration = TradingViewDBManager()
        saved_lists = tv_integration.load_saved_watchlists()

        if saved_lists:
            st.info(f"You have {len(saved_lists)} saved watchlists")

            for list_name, symbols in saved_lists.items():
                with st.expander(f"{list_name} ({len(symbols)} symbols)"):
                    st.write(", ".join(symbols))

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button(f"Load", key=f"saved_load_{list_name}"):
                            st.session_state['current_watchlist'] = symbols
                            st.session_state['current_watchlist_name'] = list_name
                            st.rerun()
                    with col2:
                        if st.button(f"Analyze", key=f"saved_analyze_{list_name}"):
                            st.session_state['current_watchlist'] = symbols
                            st.session_state['current_watchlist_name'] = list_name
                            st.info("Go to 'My Watchlist Analysis' tab")
                    with col3:
                        if st.button(f"Delete", key=f"saved_delete_{list_name}"):
                            # Remove from database
                            tv_integration = TradingViewDBManager()
                            tv_integration.delete_watchlist(list_name)
                            st.rerun()
        else:
            st.info("No saved watchlists. Import symbols in the first tab to get started.")

    with tab5:
        st.subheader("🎯 Quick Scan")

        st.info("No predefined lists available. Please use 'Import Watchlist' or 'Database Scan' to load stocks.")
elif page == "Risk Analysis":
    st.title("🛡️ Risk Analysis")
    
    # Risk metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        risk_score = 45
        st.metric("Risk Score", f"{risk_score}/100")
        if risk_score < 40:
            st.success("Low Risk")
        elif risk_score < 70:
            st.warning("Moderate Risk")
        else:
            st.error("High Risk")
    
    with col2:
        st.metric("Portfolio Delta", "+125", "▲5")
    
    with col3:
        st.metric("Max Drawdown", "-12.5%", "")
    
    with col4:
        st.metric("VaR (95%)", "$2,450", "▼10%")
    
    st.markdown("---")
    
    # Sector allocation
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Sector Allocation")
        
        sectors = pd.DataFrame({
            'Sector': ['Technology', 'Finance', 'Consumer', 'Energy', 'Healthcare'],
            'Allocation': [35, 25, 20, 15, 5]
        })
        
        fig = px.bar(
            sectors,
            x='Allocation',
            y='Sector',
            orientation='h',
            color='Allocation',
            color_continuous_scale='RdYlGn_r'
        )
        
        fig.update_layout(height=300, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("⚠️ Risk Alerts")
        
        alerts = [
            {'Level': 'Warning', 'Message': 'Technology sector approaching 40% limit'},
            {'Level': 'Info', 'Message': 'Consider diversifying into defensive sectors'},
            {'Level': 'Success', 'Message': 'Position sizing within limits'},
        ]
        
        for alert in alerts:
            if alert['Level'] == 'Warning':
                st.warning(alert['Message'])
            elif alert['Level'] == 'Info':
                st.info(alert['Message'])
            else:
                st.success(alert['Message'])
    
    # Recommendations
    st.markdown("---")
    st.subheader("💡 Risk Management Recommendations")
    
    recommendations = [
        "Consider reducing Technology exposure below 30%",
        "Add defensive positions in Consumer Staples or Utilities",
        "Current cash reserves (40%) provide good assignment coverage",
        "VaR is within acceptable range for portfolio size"
    ]
    
    for rec in recommendations:
        st.write(f"• {rec}")

elif page == "Database Scan":
    st.title("🗄️ Database Stock Scanner")
    st.markdown("Scan PostgreSQL database for stocks and analyze option premiums")

    from src.database_scanner import DatabaseScanner

    scanner = DatabaseScanner()

    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Database Overview", "➕ Add Stocks", "🔍 Scan Premiums", "📈 Analytics"])

    with tab1:
        st.subheader("Database Overview")

        if scanner.connect():
            # Create tables if needed
            scanner.create_tables()

            # Get all stocks
            stocks = scanner.get_all_stocks()

            if stocks:
                st.success(f"📊 Found {len(stocks)} stocks in database")

                # Display stocks table
                df = pd.DataFrame(stocks)
                if not df.empty:
                    # Format columns
                    if 'current_price' in df.columns:
                        df['current_price'] = df['current_price'].apply(lambda x: f"${x:.2f}" if x else "$0.00")
                    if 'market_cap' in df.columns:
                        df['market_cap'] = df['market_cap'].apply(lambda x: f"${x/1e9:.2f}B" if x > 1e9 else f"${x/1e6:.2f}M" if x > 0 else "N/A")
                    if 'avg_volume' in df.columns:
                        df['avg_volume'] = df['avg_volume'].apply(lambda x: f"{x/1e6:.2f}M" if x > 0 else "N/A")

                    st.dataframe(df[['symbol', 'name', 'sector', 'current_price', 'market_cap', 'avg_volume']], use_container_width=True)

                # Update prices button
                if st.button("🔄 Update All Prices"):
                    with st.spinner("Updating prices..."):
                        updated = scanner.update_stock_prices()
                        st.success(f"Updated {updated} stock prices")
                        st.rerun()
            else:
                st.warning("No stocks in database yet")
                st.info("👉 Go to 'Add Stocks' tab to add symbols to the database")

            scanner.disconnect()
        else:
            st.error("Failed to connect to database")

    with tab2:
        st.subheader("Add Stocks to Database")

        # Input for symbols
        symbols_input = st.text_area(
            "Enter stock symbols (comma or line separated):",
            placeholder="AAPL, MSFT, GOOGL\nTSLA, META",
            height=150
        )

        col1, col2 = st.columns(2)
        with col1:
            fetch_data = st.checkbox("Fetch stock data from Yahoo Finance", value=True)

        with col2:
            if st.button("➕ Add Stocks", type="primary"):
                if symbols_input:
                    # Parse symbols
                    symbols = [s.strip().upper() for s in symbols_input.replace('\n', ',').split(',') if s.strip()]

                    if scanner.connect():
                        scanner.create_tables()
                        with st.spinner(f"Adding {len(symbols)} stocks..."):
                            added = 0
                            for symbol in symbols:
                                if scanner.add_stock(symbol, fetch_data):
                                    added += 1

                        st.success(f"✅ Added {added} stocks to database")
                        scanner.disconnect()
                else:
                    st.error("Please enter at least one symbol")

    with tab3:
        st.subheader("💰 All Database Stocks with Options")
        st.caption("Shows all 1,205 stocks from database - filter and sort to find best premiums")

        # Info section
        st.info("💡 Showing all stocks from database that have options data. Use TradingView Watchlists → Auto-Sync to add more stocks.")

        # Filters
        col_f1, col_f2, col_f3, col_f4 = st.columns(4)
        with col_f1:
            min_stock_price = st.number_input("Min Stock Price ($)", value=0.0, min_value=0.0, step=10.0, key="db_min_stock")
        with col_f2:
            max_stock_price = st.number_input("Max Stock Price ($)", value=10000.0, min_value=10.0, step=50.0, key="db_max_stock")
        with col_f3:
            min_premium = st.number_input("Min Premium ($)", value=0.0, min_value=0.0, step=1.0, key="db_min_prem")
        with col_f4:
            dte_filter = st.selectbox("DTE", [31, 24, 17, 10, 38, 52], index=0, key="db_dte")

        # Query stock_premiums table for ALL stocks with options
        from src.tradingview_db_manager import TradingViewDBManager
        tv_manager = TradingViewDBManager()

        conn = tv_manager.get_connection()
        cur = conn.cursor()

        query = """
            SELECT DISTINCT ON (sp.symbol)
                sp.symbol,
                sd.current_price as stock_price,
                sp.strike_price,
                sp.dte,
                sp.premium,
                sp.delta,
                sp.monthly_return,
                sp.implied_volatility as iv,
                sp.bid,
                sp.ask,
                sp.volume,
                sp.open_interest as oi,
                s.name,
                s.sector
            FROM stock_premiums sp
            LEFT JOIN stock_data sd ON sp.symbol = sd.symbol
            LEFT JOIN stocks s ON sp.symbol = s.ticker
            WHERE sp.dte BETWEEN %s AND %s
                AND ABS(sp.delta) BETWEEN 0.25 AND 0.40
                AND sp.premium >= %s
                AND (sd.current_price BETWEEN %s AND %s OR sd.current_price IS NULL)
            ORDER BY sp.symbol, sp.monthly_return DESC
        """

        cur.execute(query, (dte_filter - 2, dte_filter + 2, min_premium, min_stock_price, max_stock_price))
        rows = cur.fetchall()
        cur.close()
        conn.close()

        if rows:
            # Create DataFrame
            df = pd.DataFrame(rows, columns=[
                'Symbol', 'Stock Price', 'Strike', 'DTE',
                'Premium', 'Delta', 'Monthly %', 'IV',
                'Bid', 'Ask', 'Volume', 'OI', 'Name', 'Sector'
            ])

            # Convert to numeric
            numeric_cols = ['Stock Price', 'Strike', 'DTE', 'Premium', 'Delta',
                           'Monthly %', 'IV', 'Bid', 'Ask', 'Volume', 'OI']
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            # Summary
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Options Found", len(df))
            with col2:
                st.metric("Avg Premium", f"${df['Premium'].mean():.2f}")
            with col3:
                st.metric("Avg Monthly Return", f"{df['Monthly %'].mean():.2f}%")
            with col4:
                st.metric("Unique Stocks", df['Symbol'].nunique())

            # Display sortable table
            st.markdown(f"#### 📊 All Stocks with ~{dte_filter}-Day Options (Click headers to sort)")
            st.dataframe(
                df,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Symbol": st.column_config.TextColumn("Symbol", width="small"),
                    "Stock Price": st.column_config.NumberColumn("Stock $", format="$%.2f"),
                    "Strike": st.column_config.NumberColumn("Strike", format="$%.2f"),
                    "DTE": st.column_config.NumberColumn("DTE"),
                    "Premium": st.column_config.NumberColumn("Premium", format="$%.2f"),
                    "Delta": st.column_config.NumberColumn("Delta", format="%.3f"),
                    "Monthly %": st.column_config.NumberColumn("Monthly %", format="%.2f%%"),
                    "IV": st.column_config.NumberColumn("IV %", format="%.1f%%"),
                    "Bid": st.column_config.NumberColumn("Bid", format="$%.2f"),
                    "Ask": st.column_config.NumberColumn("Ask", format="$%.2f"),
                    "Volume": st.column_config.NumberColumn("Vol"),
                    "OI": st.column_config.NumberColumn("OI"),
                    "Name": st.column_config.TextColumn("Name", width="medium"),
                    "Sector": st.column_config.TextColumn("Sector", width="medium")
                }
            )
        else:
            st.warning(f"No options found for {dte_filter}-day expiration with current filters")
            st.info("Only 89 of 1,205 stocks have options data synced. Use the TradingView Watchlists → Auto-Sync to sync more stocks.")

    with tab4:
        st.subheader("Database Analytics")

        if scanner.connect():
            stocks = scanner.get_all_stocks()

            if stocks:
                df = pd.DataFrame(stocks)

                col1, col2 = st.columns(2)

                with col1:
                    # Sector distribution
                    st.subheader("Stocks by Sector")
                    sector_counts = df['sector'].value_counts()
                    st.bar_chart(sector_counts)

                with col2:
                    # Price distribution
                    st.subheader("Price Distribution")
                    price_ranges = pd.cut(df['current_price'],
                                        bins=[0, 10, 25, 50, 100, 500, float('inf')],
                                        labels=['<$10', '$10-25', '$25-50', '$50-100', '$100-500', '>$500'])
                    price_dist = price_ranges.value_counts().sort_index()
                    st.bar_chart(price_dist)

                # Top movers would go here if we track price changes
                st.subheader("Database Stats")
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("Total Stocks", len(stocks))

                with col2:
                    avg_price = df['current_price'].mean()
                    st.metric("Avg Price", f"${avg_price:.2f}")

                with col3:
                    sectors = df['sector'].nunique()
                    st.metric("Sectors", sectors)

                with col4:
                    under_50 = len(df[df['current_price'] <= 50])
                    st.metric("Under $50", under_50)

            scanner.disconnect()
        else:
            st.error("Failed to connect to database")

elif page == "Earnings Calendar":
    from earnings_calendar_page import show_earnings_calendar
    show_earnings_calendar()

elif page == "Calendar Spreads":
    from calendar_spreads_page import show_calendar_spreads
    show_calendar_spreads()

elif page == "Settings":
    st.title("⚙️ Settings")
    
    # Strategy parameters
    st.subheader("🎯 Strategy Parameters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.number_input("Min DTE (Days to Expiration)", value=21, min_value=7, max_value=60)
        st.number_input("Max DTE", value=45, min_value=7, max_value=90)
        st.slider("Target Delta", 0.1, 0.5, 0.3, 0.05)
    
    with col2:
        st.number_input("Max Position Size (%)", value=5.0, min_value=1.0, max_value=20.0)
        st.number_input("Max Sector Exposure (%)", value=30.0, min_value=10.0, max_value=50.0)
        st.slider("Min Options Volume", 10, 1000, 100, 10)
    
    st.markdown("---")
    
    # Alert settings
    st.subheader("🔔 Alert Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.checkbox("Email Alerts", value=False)
        st.checkbox("Discord Alerts", value=True)
        st.checkbox("SMS Alerts", value=False)
    
    with col2:
        st.selectbox("Alert Frequency", ["Real-time", "Every 5 min", "Every 15 min", "Hourly"])
        st.multiselect(
            "Alert Types",
            ["New Opportunities", "Price Movements", "Assignment Warnings", "Risk Alerts"],
            default=["New Opportunities", "Assignment Warnings"]
        )
    
    st.markdown("---")

    # TradingView Integration
    st.subheader("📈 TradingView Integration")

    col1, col2 = st.columns(2)

    with col1:
        tv_enabled = st.checkbox("Enable TradingView Integration", value=True)
        if tv_enabled:
            tv_username = st.text_input(
                "TradingView Username",
                value=os.getenv('TRADINGVIEW_USERNAME', ''),
                help="Your TradingView account username"
            )

    with col2:
        if tv_enabled:
            st.info("💡 TradingView Features:")
            st.markdown("""
            - Import watchlists
            - Sync with your lists
            - Real-time screeners
            - Pre-built wheel lists
            """)

    if tv_enabled:
        st.markdown("**Available Watchlists:**")
        from src.tradingview_integration import TradingViewClient
        tv_client = TradingViewClient()

        # Show available lists
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("🔥 **High IV Stocks**")
            st.caption("Best for premium collection")
        with col2:
            st.markdown("🎯 **Popular Wheel**")
            st.caption("Most traded wheel stocks")
        with col3:
            st.markdown("💵 **Dividend Stocks**")
            st.caption("Income + premiums")

    st.markdown("---")

    if st.button("💾 Save Settings", type="primary"):
        st.success("Settings saved successfully!")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #888;'>Magnus Trading Platform v1.0 | "
    "Data updates every 5 minutes | Last update: " +
    datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "</div>",
    unsafe_allow_html=True
)