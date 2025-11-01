"""
Improved Positions Page with:
- Auto-refresh controls
- Color-coded P/L (green/red)
- TradingView chart links
- Complete trade history with P/L calculations
- Performance analytics by time period
- Database caching for fast load times
"""

import streamlit as st
import robin_stocks.robinhood as rh
import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict
from src.trade_history_sync import TradeHistorySyncService
from src.ai_research_service import get_research_service


def render_star_rating(rating: float) -> str:
    """Render star rating as emoji string"""
    full_stars = int(rating)
    half_star = 1 if (rating - full_stars) >= 0.5 else 0
    empty_stars = 5 - full_stars - half_star

    stars = "⭐" * full_stars
    if half_star:
        stars += "⭐"  # Using full star for half (could use ⯨ but less common)
    stars += "☆" * empty_stars

    return f"{stars} ({rating:.1f}/5.0)"


def get_score_color(score: int) -> str:
    """Get color for score (0-100)"""
    if score >= 80:
        return "#00AA00"  # Green
    elif score >= 60:
        return "#FFA500"  # Orange
    else:
        return "#DD0000"  # Red


def get_action_color(action: str) -> str:
    """Get color for trade action"""
    action_colors = {
        "STRONG_BUY": "#00AA00",
        "BUY": "#66CC66",
        "HOLD": "#FFA500",
        "SELL": "#FF6666",
        "STRONG_SELL": "#DD0000"
    }
    return action_colors.get(action, "#888888")


def display_ai_research(symbol: str, position_type: str = None):
    """
    Display AI research in an expander

    Args:
        symbol: Stock ticker symbol
        position_type: Type of position (for context-aware advice)
    """
    research_service = get_research_service()

    with st.spinner(f"Loading AI research for {symbol}..."):
        try:
            report = research_service.get_research_report(symbol)

            if not report:
                st.error("Failed to load research report")
                return

            # Header with overall rating
            st.markdown(f"### AI Research: {symbol}")
            st.markdown(f"**Overall Rating:** {render_star_rating(report['overall_rating'])}")
            st.caption(f"Last updated: {datetime.fromisoformat(report['timestamp']).strftime('%I:%M %p')}")

            # Quick Summary
            st.markdown("---")
            st.markdown("**Quick Summary**")
            st.info(report['quick_summary'])

            # Recommendation
            rec = report['recommendation']
            action_color = get_action_color(rec['action'])

            st.markdown("---")
            st.markdown("**Recommendation**")
            col1, col2 = st.columns([1, 3])
            with col1:
                st.markdown(f"<div style='background-color: {action_color}; color: white; padding: 10px; border-radius: 5px; text-align: center; font-weight: bold; font-size: 18px;'>{rec['action'].replace('_', ' ')}</div>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"**Confidence:** {int(rec['confidence']*100)}%")
                st.write(rec['reasoning'])

            # Time-Sensitive Factors
            if rec['time_sensitive_factors']:
                st.warning("⏰ **Time-Sensitive Factors:**")
                for factor in rec['time_sensitive_factors']:
                    st.write(f"- {factor}")

            # Position-Specific Advice (if position type provided)
            if position_type and position_type in rec['specific_position_advice']:
                st.markdown("---")
                st.success(f"💡 **Advice for Your {position_type.replace('_', ' ').title()} Position:**")
                st.write(rec['specific_position_advice'][position_type])

            # Detailed Analysis Tabs
            st.markdown("---")
            st.markdown("**Detailed Analysis**")

            tab1, tab2, tab3, tab4 = st.tabs(["📊 Fundamental", "📈 Technical", "💬 Sentiment", "🎯 Options"])

            with tab1:
                fund = report['fundamental']
                score_color = get_score_color(fund['score'])

                st.markdown(f"**Score:** <span style='color: {score_color}; font-weight: bold; font-size: 20px;'>{fund['score']}/100</span>", unsafe_allow_html=True)

                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Revenue Growth YoY", f"{fund['revenue_growth_yoy']*100:.1f}%")
                    st.metric("P/E Ratio", f"{fund['pe_ratio']:.1f}")
                    st.metric("Sector Avg P/E", f"{fund['sector_avg_pe']:.1f}")
                with col2:
                    st.metric("Earnings Beat Streak", fund['earnings_beat_streak'])
                    st.write(f"**Valuation:** {fund['valuation_assessment']}")

                st.markdown("**Key Strengths:**")
                for strength in fund['key_strengths']:
                    st.write(f"✅ {strength}")

                st.markdown("**Key Risks:**")
                for risk in fund['key_risks']:
                    st.write(f"⚠️ {risk}")

            with tab2:
                tech = report['technical']
                score_color = get_score_color(tech['score'])

                st.markdown(f"**Score:** <span style='color: {score_color}; font-weight: bold; font-size: 20px;'>{tech['score']}/100</span>", unsafe_allow_html=True)

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Trend", tech['trend'].upper())
                    st.metric("RSI", f"{tech['rsi']:.1f}")
                with col2:
                    st.metric("MACD Signal", tech['macd_signal'].upper())
                    st.write(f"**Support:** {', '.join([f'${s:.2f}' for s in tech['support_levels']])}")
                with col3:
                    st.write(f"**Resistance:** {', '.join([f'${r:.2f}' for r in tech['resistance_levels']])}")

                st.markdown("**Volume Analysis:**")
                st.write(tech['volume_analysis'])

                if tech['chart_patterns']:
                    st.markdown("**Chart Patterns:**")
                    for pattern in tech['chart_patterns']:
                        st.write(f"📊 {pattern}")

                st.info(f"**Recommendation:** {tech['recommendation']}")

            with tab3:
                sent = report['sentiment']
                score_color = get_score_color(sent['score'])

                st.markdown(f"**Score:** <span style='color: {score_color}; font-weight: bold; font-size: 20px;'>{sent['score']}/100</span>", unsafe_allow_html=True)

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("News Sentiment", sent['news_sentiment'].upper())
                    st.metric("News Articles (7d)", sent['news_count_7d'])
                with col2:
                    st.metric("Social Sentiment", sent['social_sentiment'].upper())
                    st.metric("Reddit Mentions (24h)", sent['reddit_mentions_24h'])
                with col3:
                    st.metric("Institutional Flow", sent['institutional_flow'].replace('_', ' ').title())
                    st.metric("Analyst Rating", sent['analyst_rating'].replace('_', ' ').title())

                st.markdown("**Analyst Consensus:**")
                consensus = sent['analyst_consensus']
                total = consensus['strong_buy'] + consensus['buy'] + consensus['hold'] + consensus['sell'] + consensus['strong_sell']

                if total > 0:
                    col1, col2, col3, col4, col5 = st.columns(5)
                    with col1:
                        st.metric("Strong Buy", consensus['strong_buy'])
                    with col2:
                        st.metric("Buy", consensus['buy'])
                    with col3:
                        st.metric("Hold", consensus['hold'])
                    with col4:
                        st.metric("Sell", consensus['sell'])
                    with col5:
                        st.metric("Strong Sell", consensus['strong_sell'])

            with tab4:
                opts = report['options']
                score_color = get_score_color(opts['score'])

                st.markdown(f"**Score:** <span style='color: {score_color}; font-weight: bold; font-size: 20px;'>{opts['score']}/100</span>", unsafe_allow_html=True)

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("IV Rank", f"{opts['iv_rank']}/100")
                    st.metric("IV Percentile", f"{opts['iv_percentile']}/100")
                with col2:
                    st.metric("Current IV", f"{opts['current_iv']*100:.1f}%")
                    st.metric("30d Avg IV", f"{opts['iv_mean_30d']*100:.1f}%")
                with col3:
                    st.metric("Days to Earnings", opts['days_to_earnings'])
                    st.metric("Avg Earnings Move", f"{opts['avg_earnings_move']*100:.1f}%")

                st.metric("Put/Call Ratio", f"{opts['put_call_ratio']:.2f}")

                if opts.get('unusual_activity'):
                    st.warning("🚨 Unusual options activity detected")

                if opts['recommended_strategies']:
                    st.markdown("**Recommended Strategies:**")
                    for strategy in opts['recommended_strategies']:
                        st.write(f"📋 **{strategy['strategy'].replace('_', ' ').title()}:** {strategy['rationale']}")

            # Metadata
            with st.expander("ℹ️ Report Metadata"):
                meta = report['metadata']
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Processing Time:** {meta['processing_time_ms']}ms")
                    st.write(f"**Agents Executed:** {meta['agents_executed']}")
                    st.write(f"**API Calls Used:** {meta['api_calls_used']}")
                with col2:
                    st.write(f"**LLM Model:** {meta['llm_model']}")
                    st.write(f"**Tokens Used:** {meta['llm_tokens_used']:,}")
                    st.write(f"**Cache Expires:** {datetime.fromisoformat(meta['cache_expires_at']).strftime('%I:%M %p')}")

        except Exception as e:
            st.error(f"Error loading AI research: {str(e)}")
            st.caption("Please try again or contact support if the issue persists")


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

        # === STOCK POSITIONS ===
        try:
            stock_positions_raw = rh.get_open_stock_positions()
            stock_positions_data = []

            for stock_pos in stock_positions_raw:
                quantity = float(stock_pos.get('quantity', 0))
                if quantity == 0:
                    continue

                # Get instrument URL and extract symbol
                instrument_url = stock_pos.get('instrument')
                if instrument_url:
                    instrument_data = rh.get_instrument_by_url(instrument_url)
                    symbol = instrument_data.get('symbol', 'Unknown')
                else:
                    continue

                # Get average buy price
                avg_buy_price = float(stock_pos.get('average_buy_price', 0))

                # Get current stock price
                try:
                    stock_quote = rh.get_latest_price(symbol)
                    current_price = float(stock_quote[0]) if stock_quote else 0
                except:
                    current_price = 0

                # Calculate values
                cost_basis = avg_buy_price * quantity
                current_value = current_price * quantity
                pl = current_value - cost_basis
                pl_pct = (pl / cost_basis * 100) if cost_basis > 0 else 0

                # TradingView link
                tv_link = f"https://www.tradingview.com/chart/?symbol={symbol}"

                stock_positions_data.append({
                    'Symbol': symbol,
                    'Shares': int(quantity),
                    'Avg Buy Price': avg_buy_price,
                    'Current Price': current_price,
                    'Cost Basis': cost_basis,
                    'Current Value': current_value,
                    'P/L': pl,
                    'P/L %': pl_pct,
                    'Chart': tv_link,
                    'symbol_raw': symbol,  # For AI research lookup
                    'pl_raw': pl
                })

            # Display stock positions if any
            if stock_positions_data:
                st.markdown("### 📊 Stock Positions")
                st.caption(f"{len(stock_positions_data)} stock position(s)")

                df_stocks = pd.DataFrame(stock_positions_data)

                # Format display
                display_stocks = df_stocks.copy()
                display_stocks['Avg Buy Price'] = display_stocks['Avg Buy Price'].apply(lambda x: f'${x:.2f}')
                display_stocks['Current Price'] = display_stocks['Current Price'].apply(lambda x: f'${x:.2f}')
                display_stocks['Cost Basis'] = display_stocks['Cost Basis'].apply(lambda x: f'${x:,.2f}')
                display_stocks['Current Value'] = display_stocks['Current Value'].apply(lambda x: f'${x:,.2f}')

                # Store raw P/L for coloring
                stock_pl_vals = display_stocks['P/L'].copy()

                display_stocks['P/L'] = display_stocks['P/L'].apply(lambda x: f'${x:,.2f}')
                display_stocks['P/L %'] = display_stocks['P/L %'].apply(lambda x: f'{x:.1f}%')
                display_stocks = display_stocks.drop(columns=['pl_raw', 'symbol_raw'])

                # Color coding function
                def highlight_stock_pl(row):
                    idx = row.name
                    pl_val = stock_pl_vals.iloc[idx] if idx < len(stock_pl_vals) else 0
                    styles = [''] * len(row)
                    pl_idx = list(display_stocks.columns).index('P/L')
                    pl_pct_idx = list(display_stocks.columns).index('P/L %')
                    if pl_val > 0:
                        styles[pl_idx] = 'color: #00AA00; font-weight: bold'
                        styles[pl_pct_idx] = 'color: #00AA00; font-weight: bold'
                    elif pl_val < 0:
                        styles[pl_idx] = 'color: #DD0000; font-weight: bold'
                        styles[pl_pct_idx] = 'color: #DD0000; font-weight: bold'
                    return styles

                styled_stocks = display_stocks.style.apply(highlight_stock_pl, axis=1)

                st.dataframe(
                    styled_stocks,
                    hide_index=True,
                    width='stretch',
                    column_config={
                        "Chart": st.column_config.LinkColumn(
                            "Chart",
                            help="Click to view TradingView chart",
                            display_text="📈"
                        )
                    },
                    key="stock_positions_table"
                )

                # AI Research buttons for each stock position
                st.markdown("**AI Research:**")
                cols = st.columns(len(stock_positions_data))
                for idx, (col, position) in enumerate(zip(cols, stock_positions_data)):
                    with col:
                        symbol = position['symbol_raw']
                        if st.button(f"🤖 {symbol}", key=f"stock_ai_{symbol}_{idx}"):
                            st.session_state[f'show_research_stock_{symbol}'] = True

                # Display research in expanders
                for position in stock_positions_data:
                    symbol = position['symbol_raw']
                    if st.session_state.get(f'show_research_stock_{symbol}', False):
                        with st.expander(f"🤖 AI Research: {symbol}", expanded=True):
                            display_ai_research(symbol, position_type="long_stock")

                st.markdown("---")

        except Exception as e:
            st.warning(f"Could not load stock positions: {e}")

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

                # Get current stock price (regular hours)
                try:
                    stock_quote = rh.get_latest_price(symbol)
                    stock_price = float(stock_quote[0]) if stock_quote else 0
                except:
                    stock_price = 0

                # Get after-hours stock price using quotes API
                after_hours_price = None
                try:
                    # Use get_quotes which includes extended hours data
                    quote_data = rh.get_quotes(symbol)
                    if quote_data and len(quote_data) > 0:
                        quote = quote_data[0]
                        # Try multiple fields for extended hours price
                        extended_price = quote.get('last_extended_hours_trade_price')
                        if extended_price:
                            after_hours_price = float(extended_price)
                            # Only use if different from regular price (threshold: $0.01)
                            if abs(after_hours_price - stock_price) < 0.01:
                                after_hours_price = None
                except:
                    after_hours_price = None

                # Create TradingView link (will display as clickable icon)
                tv_link = f"https://www.tradingview.com/chart/?symbol={symbol}"

                positions_data.append({
                    'Symbol': symbol,
                    'Stock Price': stock_price,
                    'After-Hours': after_hours_price,
                    'Strategy': strategy,
                    'Strike': strike,
                    'Expiration': exp_date,
                    'DTE': dte,
                    'Contracts': int(quantity),
                    'Premium': total_premium,
                    'Current': current_value,
                    'P/L': pl,
                    'P/L %': (pl/total_premium*100) if total_premium > 0 else 0,
                    'Chart': tv_link,  # Plain URL - will be styled by column_config
                    'symbol_raw': symbol,  # For AI research lookup
                    'pl_raw': pl  # For color coding
                })

            if positions_data:
                # Get buying power
                try:
                    account_profile = rh.profiles.load_account_profile()
                    buying_power = float(account_profile.get('buying_power', 0))
                except:
                    buying_power = 0

                # Display metrics
                total_pl = sum([p['P/L'] for p in positions_data])
                total_premium = sum([p['Premium'] for p in positions_data])

                col1, col2, col3, col4, col5 = st.columns(5)
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

                # Separate positions by strategy type
                csp_positions = [p for p in positions_data if p['Strategy'] == 'CSP']
                cc_positions = [p for p in positions_data if p['Strategy'] == 'CC']
                long_call_positions = [p for p in positions_data if p['Strategy'] == 'Long Call']
                long_put_positions = [p for p in positions_data if p['Strategy'] == 'Long Put']

                # Helper function to display a strategy table
                def display_strategy_table(title, emoji, positions, section_key):
                    """Display positions table for a specific strategy"""
                    if not positions:
                        return

                    st.markdown("---")
                    st.markdown(f"### {emoji} {title}")
                    st.caption(f"{len(positions)} active position(s)")

                    df = pd.DataFrame(positions)

                    # Format display columns
                    display_df = df.copy()
                    display_df['Stock Price'] = display_df['Stock Price'].apply(lambda x: f'${x:.2f}')
                    display_df['After-Hours'] = display_df['After-Hours'].apply(lambda x: f'${x:.2f}' if x is not None else '-')
                    display_df['Strike'] = display_df['Strike'].apply(lambda x: f'${x:.2f}')
                    display_df['Premium'] = display_df['Premium'].apply(lambda x: f'${x:,.2f}')
                    display_df['Current'] = display_df['Current'].apply(lambda x: f'${x:,.2f}')

                    # Store raw P/L values for coloring before formatting
                    pl_vals = display_df['P/L'].copy()

                    display_df['P/L'] = display_df['P/L'].apply(lambda x: f'${x:,.2f}')
                    display_df['P/L %'] = display_df['P/L %'].apply(lambda x: f'{x:.1f}%')

                    # Drop helper columns
                    display_df = display_df.drop(columns=['pl_raw', 'symbol_raw'])

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
                        width='stretch',
                        column_config={
                            "Chart": st.column_config.LinkColumn(
                                "Chart",
                                help="Click to view TradingView chart",
                                display_text="📈"
                            )
                        },
                        key=f"positions_table_{section_key}"
                    )

                    # AI Research buttons
                    st.markdown("**AI Research:**")
                    cols = st.columns(len(positions))
                    for idx, (col, position) in enumerate(zip(cols, positions)):
                        with col:
                            symbol = position['symbol_raw']
                            if st.button(f"🤖 {symbol}", key=f"{section_key}_ai_{symbol}_{idx}"):
                                st.session_state[f'show_research_{section_key}_{symbol}'] = True

                    # Display research in expanders
                    for position in positions:
                        symbol = position['symbol_raw']
                        if st.session_state.get(f'show_research_{section_key}_{symbol}', False):
                            # Determine position type for context-aware advice
                            strategy_type_map = {
                                'CSP': 'cash_secured_put',
                                'CC': 'covered_call',
                                'Long Call': 'long_call',
                                'Long Put': 'long_put'
                            }
                            position_type = strategy_type_map.get(position.get('Strategy', ''), None)

                            with st.expander(f"🤖 AI Research: {symbol}", expanded=True):
                                display_ai_research(symbol, position_type=position_type)

                # Display each strategy section
                display_strategy_table("Cash-Secured Puts", "💰", csp_positions, "csp")
                display_strategy_table("Covered Calls", "📞", cc_positions, "cc")
                display_strategy_table("Long Calls", "📈", long_call_positions, "long_calls")
                display_strategy_table("Long Puts", "📉", long_put_positions, "long_puts")

            else:
                st.info("No open option positions found in Robinhood")

        else:
            st.info("No open option positions found")

    except Exception as e:
        st.error(f"Error loading positions: {e}")

    # === TRADE HISTORY ===
    st.markdown("---")

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("### 📊 Trade History")
        st.caption("Closed trades with P/L calculations (loaded from database)")
    with col2:
        # Initialize sync service
        sync_service = TradeHistorySyncService()
        last_sync = sync_service.get_last_sync_time()

        if last_sync:
            st.caption(f"Last synced: {last_sync.strftime('%I:%M %p')}")

        if st.button("🔄 Sync Now", key="sync_trades"):
            with st.spinner("Syncing trades from Robinhood..."):
                try:
                    count = sync_service.sync_trades_from_robinhood(rh_session)
                    st.success(f"✅ Synced {count} new trades")
                    st.rerun()
                except Exception as e:
                    st.error(f"Sync failed: {e}")

    closed_trades = []  # Initialize outside try block for use in performance analytics
    try:
        # Use fast database query instead of slow Robinhood API
        sync_service = TradeHistorySyncService()
        db_trades = sync_service.get_closed_trades_from_db(days_back=365)

        # Convert to format expected by display code
        closed_trades = []
        for trade in db_trades:
            closed_trades.append({
                'Symbol': trade['symbol'],
                'Strategy': 'CSP' if trade['strategy_type'] == 'cash_secured_put' else 'CC',
                'Strike': trade['strike'],
                'Open Premium': trade['premium_collected'],
                'Close Cost': trade['close_price'],
                'P/L': trade['profit_loss'],
                'P/L %': (trade['profit_loss'] / trade['premium_collected'] * 100) if trade['premium_collected'] > 0 else 0,
                'Days Held': trade['days_held'],
                'Close Date': trade['close_date'].strftime('%Y-%m-%d') if trade['close_date'] else 'N/A'
            })

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
                width='stretch',
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

        # Use processed_premium (total premium) with direction
        processed_premium = float(order.get('processed_premium', 0))
        premium_direction = order.get('processed_premium_direction', 'debit')

        # Credit = you received money (positive), Debit = you paid money (negative)
        if premium_direction == 'credit':
            price = (processed_premium / quantity) if quantity > 0 else 0
        else:  # debit
            price = -(processed_premium / quantity) if quantity > 0 else 0

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

                # Calculate P/L using signed values
                # open_price: positive for credit (sold), negative for debit (bought)
                # price: positive for credit (sold), negative for debit (bought)
                # P/L = open_price + price (because close price already has correct sign)

                open_amount = open_order['open_price'] * quantity
                close_amount = price * quantity
                pl = open_amount + close_amount  # Simply add (signs handle the math)

                # Determine strategy
                if side == 'buy':  # Buying to close a short position
                    strategy = 'CSP' if opt_type == 'put' else 'CC'
                else:  # Selling to close a long position
                    strategy = 'Long Call' if opt_type == 'call' else 'Long Put'

                # For percentage, use absolute value of the opening amount
                pl_pct = (pl / abs(open_amount) * 100) if abs(open_amount) > 0 else 0

                # Days held
                days_held = (trade_date - open_order['open_date']).days

                closed_trades.append({
                    'Close Date': trade_date.strftime('%Y-%m-%d'),
                    'Symbol': symbol,
                    'Strategy': strategy,
                    'Strike': f'${strike:.2f}',
                    'Open Premium': abs(open_amount),  # Show as positive for display
                    'Close Cost': abs(close_amount),   # Show as positive for display
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
