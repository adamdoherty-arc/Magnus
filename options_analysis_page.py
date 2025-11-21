"""
Unified Options Analysis Page
Combines AI Options Agent (screening) + Comprehensive Strategy (deep analysis)
With current positions integration and AVA chatbot support
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from typing import Dict, Any

# Import unified analyzer
from src.options_analysis.unified_analyzer import UnifiedOptionsAnalyzer

# Import positions manager
from src.data.positions_manager import PositionsManager

# Import shared components
from src.ai_options_agent.shared.stock_selector import StockSelector
from src.ai_options_agent.shared.llm_config_ui import LLMConfigUI
from src.ai_options_agent.shared.data_fetchers import (
    fetch_stock_info,
    fetch_options_suggestions,
    calculate_iv_for_stock
)
from src.ai_options_agent.shared.data_validator import (
    display_data_validation,
    create_refresh_button
)

# Import AVA integration (not needed here - AVA is shown globally in dashboard.py)
# from src.ava.omnipresent_ava_enhanced import show_enhanced_ava


def generate_trade_execution_details(strategy_name: str, stock_price: float, options_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate detailed trade execution instructions for a given strategy

    Args:
        strategy_name: Name of the options strategy
        stock_price: Current stock price
        options_data: Options data (strike, premium, DTE, delta, etc.)

    Returns:
        Dict with trade execution details including legs, prices, risks/rewards
    """
    strike = options_data.get('strike_price', stock_price)
    premium = options_data.get('premium', 2.50)
    dte = options_data.get('dte', 30)

    # Generate execution details based on strategy type
    if 'Cash-Secured Put' in strategy_name or 'CSP' in strategy_name:
        return {
            'legs': [
                {
                    'action': 'SELL',
                    'type': 'PUT',
                    'strike': strike,
                    'quantity': 1,
                    'expiration': f'{dte} days',
                    'premium': premium,
                    'description': f'Sell 1 ${strike:.2f} Put expiring in {dte} days'
                }
            ],
            'total_credit': premium * 100,  # Premium per contract
            'max_profit': premium * 100,
            'max_loss': (strike - premium) * 100,
            'breakeven': strike - premium,
            'capital_required': strike * 100,
            'examples': [
                {
                    'name': 'Conservative (Further OTM)',
                    'strike': strike * 0.95,
                    'premium': premium * 0.7,
                    'win_probability': '75%',
                    'max_profit': premium * 0.7 * 100,
                    'breakeven': (strike * 0.95) - (premium * 0.7)
                },
                {
                    'name': 'Standard (Current)',
                    'strike': strike,
                    'premium': premium,
                    'win_probability': '65%',
                    'max_profit': premium * 100,
                    'breakeven': strike - premium
                },
                {
                    'name': 'Aggressive (Closer ITM)',
                    'strike': strike * 1.02,
                    'premium': premium * 1.4,
                    'win_probability': '55%',
                    'max_profit': premium * 1.4 * 100,
                    'breakeven': (strike * 1.02) - (premium * 1.4)
                }
            ]
        }

    elif 'Iron Condor' in strategy_name:
        otm_put_strike = strike * 0.95
        itm_put_strike = strike * 0.90
        otm_call_strike = strike * 1.05
        itm_call_strike = strike * 1.10

        return {
            'legs': [
                {
                    'action': 'SELL',
                    'type': 'PUT',
                    'strike': otm_put_strike,
                    'quantity': 1,
                    'expiration': f'{dte} days',
                    'premium': premium * 0.8,
                    'description': f'Sell 1 ${otm_put_strike:.2f} Put'
                },
                {
                    'action': 'BUY',
                    'type': 'PUT',
                    'strike': itm_put_strike,
                    'quantity': 1,
                    'expiration': f'{dte} days',
                    'premium': premium * 0.3,
                    'description': f'Buy 1 ${itm_put_strike:.2f} Put (protection)'
                },
                {
                    'action': 'SELL',
                    'type': 'CALL',
                    'strike': otm_call_strike,
                    'quantity': 1,
                    'expiration': f'{dte} days',
                    'premium': premium * 0.8,
                    'description': f'Sell 1 ${otm_call_strike:.2f} Call'
                },
                {
                    'action': 'BUY',
                    'type': 'CALL',
                    'strike': itm_call_strike,
                    'quantity': 1,
                    'expiration': f'{dte} days',
                    'premium': premium * 0.3,
                    'description': f'Buy 1 ${itm_call_strike:.2f} Call (protection)'
                }
            ],
            'total_credit': (premium * 0.8 - premium * 0.3 + premium * 0.8 - premium * 0.3) * 100,
            'max_profit': (premium * 0.8 - premium * 0.3 + premium * 0.8 - premium * 0.3) * 100,
            'max_loss': ((otm_put_strike - itm_put_strike) - (premium * 0.8 - premium * 0.3 + premium * 0.8 - premium * 0.3)) * 100,
            'breakeven_lower': otm_put_strike - (premium * 1.0),
            'breakeven_upper': otm_call_strike + (premium * 1.0),
            'capital_required': ((otm_put_strike - itm_put_strike) * 100),
            'examples': [
                {
                    'name': 'Narrow Wings (Tighter Range)',
                    'put_strikes': f'${strike * 0.97:.2f}/${strike * 0.93:.2f}',
                    'call_strikes': f'${strike * 1.03:.2f}/${strike * 1.07:.2f}',
                    'credit': premium * 1.2 * 100,
                    'max_profit': premium * 1.2 * 100,
                    'win_probability': '60%'
                },
                {
                    'name': 'Standard (Current)',
                    'put_strikes': f'${otm_put_strike:.2f}/${itm_put_strike:.2f}',
                    'call_strikes': f'${otm_call_strike:.2f}/${itm_call_strike:.2f}',
                    'credit': premium * 1.0 * 100,
                    'max_profit': premium * 1.0 * 100,
                    'win_probability': '70%'
                },
                {
                    'name': 'Wide Wings (Safer)',
                    'put_strikes': f'${strike * 0.92:.2f}/${strike * 0.85:.2f}',
                    'call_strikes': f'${strike * 1.08:.2f}/${strike * 1.15:.2f}',
                    'credit': premium * 0.6 * 100,
                    'max_profit': premium * 0.6 * 100,
                    'win_probability': '80%'
                }
            ]
        }

    elif 'Bull Put Spread' in strategy_name:
        short_put_strike = strike * 0.97
        long_put_strike = strike * 0.93

        return {
            'legs': [
                {
                    'action': 'SELL',
                    'type': 'PUT',
                    'strike': short_put_strike,
                    'quantity': 1,
                    'expiration': f'{dte} days',
                    'premium': premium,
                    'description': f'Sell 1 ${short_put_strike:.2f} Put'
                },
                {
                    'action': 'BUY',
                    'type': 'PUT',
                    'strike': long_put_strike,
                    'quantity': 1,
                    'expiration': f'{dte} days',
                    'premium': premium * 0.4,
                    'description': f'Buy 1 ${long_put_strike:.2f} Put (protection)'
                }
            ],
            'total_credit': (premium - premium * 0.4) * 100,
            'max_profit': (premium - premium * 0.4) * 100,
            'max_loss': ((short_put_strike - long_put_strike) - (premium - premium * 0.4)) * 100,
            'breakeven': short_put_strike - (premium - premium * 0.4),
            'capital_required': (short_put_strike - long_put_strike) * 100,
            'examples': [
                {
                    'name': 'Tight Spread ($2 wide)',
                    'strikes': f'${strike * 0.98:.2f}/${strike * 0.96:.2f}',
                    'credit': premium * 0.5 * 100,
                    'max_profit': premium * 0.5 * 100,
                    'max_loss': (strike * 0.02 - premium * 0.5) * 100,
                    'win_probability': '65%'
                },
                {
                    'name': 'Standard ($4 wide)',
                    'strikes': f'${short_put_strike:.2f}/${long_put_strike:.2f}',
                    'credit': (premium - premium * 0.4) * 100,
                    'max_profit': (premium - premium * 0.4) * 100,
                    'max_loss': ((short_put_strike - long_put_strike) - (premium - premium * 0.4)) * 100,
                    'win_probability': '70%'
                },
                {
                    'name': 'Wide Spread ($6 wide)',
                    'strikes': f'${strike * 0.96:.2f}/${strike * 0.90:.2f}',
                    'credit': premium * 0.8 * 100,
                    'max_profit': premium * 0.8 * 100,
                    'max_loss': (strike * 0.06 - premium * 0.8) * 100,
                    'win_probability': '75%'
                }
            ]
        }

    elif 'Covered Call' in strategy_name:
        call_strike = strike * 1.05

        return {
            'legs': [
                {
                    'action': 'OWN',
                    'type': 'STOCK',
                    'strike': stock_price,
                    'quantity': 100,
                    'expiration': 'N/A',
                    'premium': 0,
                    'description': f'Own 100 shares @ ${stock_price:.2f}'
                },
                {
                    'action': 'SELL',
                    'type': 'CALL',
                    'strike': call_strike,
                    'quantity': 1,
                    'expiration': f'{dte} days',
                    'premium': premium,
                    'description': f'Sell 1 ${call_strike:.2f} Call'
                }
            ],
            'total_credit': premium * 100,
            'max_profit': (call_strike - stock_price + premium) * 100,
            'max_loss': (stock_price - premium) * 100,
            'breakeven': stock_price - premium,
            'capital_required': stock_price * 100,
            'examples': [
                {
                    'name': 'Conservative (5% OTM)',
                    'strike': stock_price * 1.05,
                    'premium': premium * 0.7,
                    'max_profit': (stock_price * 0.05 + premium * 0.7) * 100,
                    'annualized_return': '15-20%'
                },
                {
                    'name': 'Standard (3% OTM)',
                    'strike': stock_price * 1.03,
                    'premium': premium,
                    'max_profit': (stock_price * 0.03 + premium) * 100,
                    'annualized_return': '20-25%'
                },
                {
                    'name': 'Aggressive (ATM)',
                    'strike': stock_price,
                    'premium': premium * 1.5,
                    'max_profit': premium * 1.5 * 100,
                    'annualized_return': '25-30%'
                }
            ]
        }

    else:
        # Default/generic execution details
        return {
            'legs': [
                {
                    'action': 'STRATEGY SPECIFIC',
                    'type': 'OPTIONS',
                    'strike': strike,
                    'quantity': 1,
                    'expiration': f'{dte} days',
                    'premium': premium,
                    'description': f'See strategy details for specific execution'
                }
            ],
            'total_credit': premium * 100,
            'max_profit': 'Varies by strategy',
            'max_loss': 'Varies by strategy',
            'breakeven': 'Varies by strategy',
            'capital_required': 'Varies by strategy',
            'examples': []
        }


def render_options_analysis_page():
    """Main unified Options Analysis page"""

    st.set_page_config(page_title="Options Analysis", layout="wide")

    # Page header
    st.title("📊 Options Analysis")
    st.markdown("**Unified screening, strategy analysis, and position management**")
    
    # Sync status widgets
    from src.components.sync_status_widget import SyncStatusWidget
    sync_widget = SyncStatusWidget()
    
    col1, col2 = st.columns([3, 1])
    with col1:
        sync_widget.display(
            table_name="stock_premiums",
            title="Options Data Sync",
            compact=True
        )
    with col2:
        sync_widget.display(
            table_name="stock_data",
            title="Stock Data Sync",
            compact=True
        )

    # Note: AVA chatbot is already shown globally in dashboard.py
    # No need to call show_enhanced_ava() here to avoid duplication

    st.markdown("---")

    # Initialize components
    @st.cache_resource
    def init_components():
        """Initialize analyzer and positions manager"""
        from src.ai_options_agent.llm_manager import get_llm_manager
        llm_manager = get_llm_manager()
        analyzer = UnifiedOptionsAnalyzer(llm_manager)
        positions_mgr = PositionsManager()
        return analyzer, positions_mgr, llm_manager

    analyzer, positions_mgr, llm_manager = init_components()

    # Initialize session state
    if 'selected_stock' not in st.session_state:
        st.session_state.selected_stock = None
    if 'scan_results' not in st.session_state:
        st.session_state.scan_results = None
    if 'selected_opportunity' not in st.session_state:
        st.session_state.selected_opportunity = None
    if 'strategy_analysis' not in st.session_state:
        st.session_state.strategy_analysis = None
    if 'manual_override' not in st.session_state:
        st.session_state.manual_override = False
    if 'cached_loaded' not in st.session_state:
        st.session_state.cached_loaded = False

    # ========== LOAD CACHED RESULTS ON FIRST LOAD ==========
    if not st.session_state.cached_loaded and not st.session_state.scan_results:
        try:
            # Try to load recent analyses from database (last 24 hours)
            from src.ai_options_agent.options_analysis_agent import OptionsAnalysisAgent
            agent = OptionsAnalysisAgent(llm_manager=llm_manager)
            cached_analyses = agent.get_top_recommendations(days=1, min_score=60)

            if cached_analyses and len(cached_analyses) > 0:
                # Format cached results to match scan_results structure
                st.session_state.scan_results = {
                    'opportunities': cached_analyses,
                    'summary': {
                        'total': len(cached_analyses),
                        'strong_buys': len([a for a in cached_analyses if a.get('recommendation') == 'STRONG_BUY']),
                        'avg_score': sum(a.get('final_score', 0) for a in cached_analyses) / len(cached_analyses) if cached_analyses else 0
                    },
                    'metadata': {
                        'source': 'cached',
                        'loaded_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                }
                st.info(f"📂 Loaded {len(cached_analyses)} cached analyses from the last 24 hours")
        except Exception as e:
            # Silently fail if can't load cached results
            pass
        finally:
            st.session_state.cached_loaded = True

    # ========== THREE-PANEL LAYOUT ==========

    # Create three columns
    left_col, center_col, right_col = st.columns([3, 5, 2])

    # ========== LEFT PANEL: Stock Selection + Screening ==========
    with left_col:
        st.subheader("🔍 Stock Selection & Screening")

        # === Stock Selection Mode ===
        selection_mode = st.radio(
            "Selection Mode:",
            ["Manual Entry", "Watchlist", "Database Search", "Current Positions"],
            horizontal=True
        )

        selected_symbol = None
        selected_position = None

        # Manual Entry
        if selection_mode == "Manual Entry":
            selected_symbol = st.text_input(
                "Enter Symbol",
                placeholder="AAPL",
                key="manual_symbol_input"
            ).upper()

        # Watchlist Selection
        elif selection_mode == "Watchlist":
            selector = StockSelector()
            watchlist_name, symbols = selector.render_watchlist_selector()

            if symbols and len(symbols) > 0:
                selected_symbol = st.selectbox(
                    "Select Stock from Watchlist",
                    symbols,
                    key="watchlist_stock_select"
                )

        # Database Search
        elif selection_mode == "Database Search":
            from src.ai_options_agent.shared.data_fetchers import fetch_database_stocks
            db_stocks = fetch_database_stocks()

            if db_stocks:
                selected_symbol = st.selectbox(
                    "Select Stock from Database",
                    db_stocks,
                    key="database_stock_select"
                )

        # Current Positions
        elif selection_mode == "Current Positions":
            positions = positions_mgr.get_current_positions()

            if positions:
                formatted_positions = positions_mgr.format_for_dropdown(positions)

                position_idx = st.selectbox(
                    "Select Position",
                    range(len(formatted_positions)),
                    format_func=lambda i: formatted_positions[i][0],
                    key="position_select"
                )

                selected_position = formatted_positions[position_idx][1]
                selected_symbol = selected_position.get('symbol')

                # Show position details
                st.info(f"""
                **Current Position:**
                - Strike: ${selected_position.get('strike', 0):.2f}
                - Type: {selected_position.get('option_type', 'N/A').upper()}
                - DTE: {selected_position.get('dte', 0)} days
                - P&L: ${selected_position.get('pnl', 0):.2f} ({selected_position.get('pnl_pct', 0):.1f}%)
                """)
            else:
                st.warning("No current positions found. Log in to Robinhood to see positions.")

        # Update session state
        if selected_symbol:
            st.session_state.selected_stock = selected_symbol

        st.markdown("---")

        # === Screening Filters ===
        st.markdown("### 🎯 Screening Filters")

        with st.expander("Filter Settings", expanded=False):
            # DTE Range
            col1, col2 = st.columns(2)
            with col1:
                min_dte = st.number_input("Min DTE", 1, 90, 20, 1, key="min_dte_filter")
            with col2:
                max_dte = st.number_input("Max DTE", 1, 90, 40, 1, key="max_dte_filter")

            # Delta Range
            col1, col2 = st.columns(2)
            with col1:
                min_delta = st.number_input("Min Delta", -0.50, -0.01, -0.45, 0.01, key="min_delta_filter")
            with col2:
                max_delta = st.number_input("Max Delta", -0.50, -0.01, -0.15, 0.01, key="max_delta_filter")

            # Premium and Score
            col1, col2 = st.columns(2)
            with col1:
                min_premium = st.number_input("Min Premium ($)", 0.0, 1000.0, 100.0, 10.0, key="min_premium_filter")
            with col2:
                min_score = st.slider("Min Score", 0, 100, 50, 5, key="min_score_filter")

            # Max Results
            max_results = st.number_input("Max Results", 10, 1000, 200, 50, key="max_results_filter")

            # LLM Reasoning
            use_llm = st.checkbox("🤖 Use LLM Reasoning (slower)", value=False, key="use_llm_filter")

        # === Run Scan Button ===
        scan_source = "watchlist" if selection_mode == "Watchlist" else "all"

        # Show "Analyze Entire Watchlist" button if watchlist mode
        watchlist_name = watchlist_name if selection_mode == "Watchlist" else None
        if selection_mode == "Watchlist" and watchlist_name and symbols and len(symbols) > 0:
            analyze_watchlist_btn = st.button(
                "📊 Analyze Entire Watchlist",
                type="primary",
                use_container_width=True,
                help=f"Find best trades across all {len(symbols)} stocks in {watchlist_name}"
            )
            
            if analyze_watchlist_btn:
                with st.spinner(f"🔍 Analyzing {len(symbols)} stocks in {watchlist_name}... This may take a minute."):
                    # Run comprehensive batch analysis with higher limit
                    results = analyzer.screen_opportunities(
                        source="watchlist",
                        watchlist_name=watchlist_name,
                        dte_range=(min_dte, max_dte),
                        delta_range=(min_delta, max_delta),
                        min_premium=min_premium,
                        limit=500,  # Analyze all stocks in watchlist
                        min_score=min_score,
                        use_llm=use_llm
                    )
                    
                    # Store results
                    st.session_state.watchlist_analysis = results
                    st.session_state.scan_results = results
                    st.success(f"✅ Found {len(results.get('opportunities', []))} opportunities across {len(symbols)} stocks!")
                    st.rerun()

        col1, col2 = st.columns(2)
        with col1:
            run_scan = st.button("🚀 Run Scan", type="primary", use_container_width=True)
        with col2:
            if st.button("🔄 Clear Results", use_container_width=True):
                st.session_state.scan_results = None
                st.session_state.watchlist_analysis = None
                st.rerun()

        # Execute scan
        if run_scan:
            with st.spinner("🔍 Scanning for opportunities..."):
                scan_params = {
                    'source': scan_source,
                    'watchlist_name': watchlist_name if selection_mode == "Watchlist" else None,
                    'dte_range': (min_dte, max_dte),
                    'delta_range': (min_delta, max_delta),
                    'min_premium': min_premium,
                    'limit': max_results,
                    'min_score': min_score,
                    'use_llm': use_llm
                }

                results = analyzer.screen_opportunities(**scan_params)
                st.session_state.scan_results = results

        # === Display Scan Results ===
        if st.session_state.scan_results:
            results = st.session_state.scan_results
            opportunities = results.get('opportunities', [])
            summary = results.get('summary', {})

            st.markdown("### 📊 Scan Results")

            # Summary metrics
            col1, col2, col3 = st.columns(3)
            col1.metric("Total", summary.get('total', 0))
            col2.metric("Strong Buy", summary.get('strong_buys', 0))
            col3.metric("Avg Score", f"{summary.get('avg_score', 0):.0f}")

            # Check if this is from cache
            if results.get('metadata', {}).get('source') == 'cached':
                st.caption(f"📂 Cached from: {results.get('metadata', {}).get('loaded_at', 'N/A')}")

            # Organize results in tabs
            # Add watchlist comparison tab if this is a watchlist analysis
            is_watchlist_analysis = (
                st.session_state.get('watchlist_analysis') is not None or
                results.get('metadata', {}).get('filters', {}).get('source') == 'watchlist'
            )
            
            if is_watchlist_analysis:
                tab1, tab2, tab3, tab4 = st.tabs(["📋 All Results", "🏆 Top Picks", "📊 Watchlist Comparison", "📈 Summary"])
            else:
                tab1, tab2, tab3 = st.tabs(["📋 All Results", "🏆 Top Picks", "📊 Summary"])

            with tab1:
                # All Results
                if opportunities:
                    st.markdown(f"**Showing {min(len(opportunities), 20)} of {len(opportunities)} opportunities:**")

                    # Create scrollable container
                    for idx, opp in enumerate(opportunities[:20]):  # Show top 20
                        symbol = opp.get('symbol', 'N/A')
                        score = opp.get('final_score', 0)
                        strike = float(opp.get('strike_price', 0))
                        dte = opp.get('dte', 0)
                        premium = float(opp.get('premium', 0)) / 100
                        rec = opp.get('recommendation', 'HOLD')

                        # Color code by recommendation
                        if rec == 'STRONG_BUY':
                            emoji = "🟢"
                        elif rec == 'BUY':
                            emoji = "🔵"
                        else:
                            emoji = "⚪"

                        # Clickable row
                        if st.button(
                            f"{emoji} {idx+1}. {symbol} - {score}/100 | ${strike:.0f} {dte}d ${premium:.2f}",
                            key=f"opp_all_{idx}",
                            use_container_width=True
                        ):
                            st.session_state.selected_opportunity = opp
                            st.session_state.selected_stock = symbol
                            st.rerun()

                    if len(opportunities) > 20:
                        st.info(f"Showing top 20 of {len(opportunities)} results. Adjust filters to refine.")
                else:
                    st.info("No opportunities found with current filters")

            with tab2:
                # Top Picks (STRONG BUY only)
                top_picks = [opp for opp in opportunities if opp.get('recommendation') == 'STRONG_BUY']

                if top_picks:
                    st.markdown(f"**🏆 {len(top_picks)} STRONG BUY Recommendations:**")

                    for idx, opp in enumerate(top_picks[:15]):  # Show top 15
                        symbol = opp.get('symbol', 'N/A')
                        score = opp.get('final_score', 0)
                        strike = float(opp.get('strike_price', 0))
                        dte = opp.get('dte', 0)
                        premium = float(opp.get('premium', 0)) / 100

                        # Expanded details for top picks
                        with st.expander(
                            f"🟢 {idx+1}. {symbol} - **{score}/100** | ${strike:.0f} {dte}d ${premium:.2f}",
                            expanded=(idx < 3)  # Expand top 3
                        ):
                            col1, col2, col3 = st.columns(3)
                            col1.metric("Strike", f"${strike:.2f}")
                            col2.metric("DTE", dte)
                            col3.metric("Premium", f"${premium:.2f}")

                            # Score breakdown
                            st.markdown("**Score Breakdown:**")
                            score_col1, score_col2, score_col3 = st.columns(3)
                            score_col1.caption(f"📊 Fundamental: {opp.get('fundamental_score', 0)}")
                            score_col2.caption(f"📈 Technical: {opp.get('technical_score', 0)}")
                            score_col3.caption(f"⚙️ Greeks: {opp.get('greeks_score', 0)}")

                            if st.button("🔍 Analyze This", key=f"analyze_pick_{idx}"):
                                st.session_state.selected_opportunity = opp
                                st.session_state.selected_stock = symbol
                                st.rerun()
                else:
                    st.info("No STRONG BUY recommendations. Try lowering the min score filter.")

            # Watchlist Comparison Tab (only shown for watchlist analyses)
            if is_watchlist_analysis:
                with tab3:
                    st.markdown("### 🏆 Top Watchlist Opportunities")
                    st.markdown(f"**Ranked by score across all {len(opportunities)} opportunities in watchlist**")
                    
                    if opportunities:
                        # Create comparison DataFrame
                        comparison_data = []
                        for idx, opp in enumerate(opportunities[:50]):  # Show top 50
                            comparison_data.append({
                                'Rank': idx + 1,
                                'Symbol': opp.get('symbol', 'N/A'),
                                'Score': opp.get('final_score', 0),
                                'Recommendation': opp.get('recommendation', 'HOLD'),
                                'Strike': f"${float(opp.get('strike_price', 0)):.2f}",
                                'Premium': f"${float(opp.get('premium', 0))/100:.2f}",
                                'DTE': opp.get('dte', 0),
                                'Delta': f"{float(opp.get('delta', 0)):.2f}",
                                'IV': f"{float(opp.get('iv', 0))*100:.1f}%" if float(opp.get('iv', 0)) > 0 else "N/A"
                            })
                        
                        comparison_df = pd.DataFrame(comparison_data)
                        
                        # Display with styling
                        st.dataframe(
                            comparison_df,
                            use_container_width=True,
                            hide_index=True
                        )
                        
                        # Summary statistics
                        st.markdown("---")
                        col1, col2, col3, col4 = st.columns(4)
                        col1.metric("Total Opportunities", len(opportunities))
                        col2.metric("Strong Buys", len([o for o in opportunities if o.get('recommendation') == 'STRONG_BUY']))
                        col3.metric("Avg Score", f"{sum(o.get('final_score', 0) for o in opportunities) / len(opportunities):.1f}")
                        col4.metric("Top Score", f"{max(o.get('final_score', 0) for o in opportunities)}")
                        
                        # Best opportunities by category
                        st.markdown("---")
                        st.markdown("### 🎯 Best Opportunities by Category")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**💰 Highest Premium:**")
                            highest_premium = max(opportunities, key=lambda x: float(x.get('premium', 0)))
                            st.info(f"**{highest_premium.get('symbol')}** - ${float(highest_premium.get('premium', 0))/100:.2f} premium | Score: {highest_premium.get('final_score', 0)}/100")

                            st.markdown("**⚡ Highest Score:**")
                            highest_score = max(opportunities, key=lambda x: float(x.get('final_score', 0)))
                            st.success(f"**{highest_score.get('symbol')}** - Score: {highest_score.get('final_score', 0)}/100 | Premium: ${float(highest_score.get('premium', 0))/100:.2f}")

                        with col2:
                            st.markdown("**📊 Best Risk/Reward:**")
                            # Calculate risk/reward (premium / strike) - Convert Decimals to float
                            best_rr = max(opportunities, key=lambda x: (float(x.get('premium', 0)) / float(x.get('strike_price', 1))) if float(x.get('strike_price', 0)) > 0 else 0)
                            rr_ratio = (float(best_rr.get('premium', 0)) / float(best_rr.get('strike_price', 1))) * 100 if float(best_rr.get('strike_price', 0)) > 0 else 0
                            st.info(f"**{best_rr.get('symbol')}** - {rr_ratio:.2f}% R/R | Score: {best_rr.get('final_score', 0)}/100")

                            st.markdown("**🎯 Best Delta:**")
                            # Find closest to -0.30 delta - Convert Decimal to float
                            best_delta = min(opportunities, key=lambda x: abs(float(x.get('delta', 0)) + 0.30))
                            st.success(f"**{best_delta.get('symbol')}** - Δ{float(best_delta.get('delta', 0)):.2f} | Score: {best_delta.get('final_score', 0)}/100")
                    else:
                        st.info("No opportunities found in watchlist. Try adjusting filters.")

            # Summary Tab (tab3 if not watchlist, tab4 if watchlist)
            summary_tab = tab3 if not is_watchlist_analysis else tab4
            with summary_tab:
                # Summary Statistics
                st.markdown("**📊 Scan Summary**")

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**Recommendation Breakdown:**")
                    strong_buy_count = len([o for o in opportunities if o.get('recommendation') == 'STRONG_BUY'])
                    buy_count = len([o for o in opportunities if o.get('recommendation') == 'BUY'])
                    hold_count = len([o for o in opportunities if o.get('recommendation') == 'HOLD'])
                    avoid_count = len([o for o in opportunities if o.get('recommendation') == 'AVOID'])

                    st.metric("🟢 STRONG BUY", strong_buy_count)
                    st.metric("🔵 BUY", buy_count)
                    st.metric("⚪ HOLD", hold_count)
                    st.metric("🔴 AVOID", avoid_count)

                with col2:
                    st.markdown("**Score Statistics:**")
                    if opportunities:
                        scores = [o.get('final_score', 0) for o in opportunities]
                        st.metric("Average Score", f"{sum(scores)/len(scores):.1f}")
                        st.metric("Highest Score", f"{max(scores)}")
                        st.metric("Lowest Score", f"{min(scores)}")
                        st.metric("Median Score", f"{sorted(scores)[len(scores)//2]}")

    # ========== CENTER PANEL: Strategy Analysis ==========
    with center_col:
        st.subheader("🎯 Strategy Analysis")

        # Check if we have a selected stock or opportunity
        if st.session_state.selected_stock or st.session_state.selected_opportunity:

            # Determine what we're analyzing
            if selected_position:
                # Analyzing a current position
                st.markdown(f"### Analyzing Position: {selected_position.get('symbol')}")

                if st.button("🔍 Analyze Position Strategies", type="primary", use_container_width=True):
                    with st.spinner(f"Analyzing position for {selected_position.get('symbol')}..."):
                        analysis = analyzer.analyze_position(
                            position=selected_position,
                            use_multi_model=True
                        )
                        st.session_state.strategy_analysis = analysis

            elif st.session_state.selected_opportunity:
                # Analyzing from scan results
                opp = st.session_state.selected_opportunity
                symbol = opp.get('symbol')

                st.markdown(f"### Analyzing: {symbol}")

                # Show opportunity details
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Score", f"{opp.get('final_score', 0)}/100")
                col2.metric("Strike", f"${float(opp.get('strike_price', 0)):.2f}")
                col3.metric("DTE", opp.get('dte', 0))
                col4.metric("Premium", f"${float(opp.get('premium', 0))/100:.2f}")

                # Analyze button
                if st.button("🔍 Analyze All Strategies", type="primary", use_container_width=True):
                    with st.spinner(f"Analyzing all strategies for {symbol}..."):
                        # Prepare data
                        stock_info = fetch_stock_info(symbol)

                        if stock_info:
                            # Store actual stock price in session state
                            if stock_info.get('current_price', 0) > 0:
                                st.session_state.selected_stock_price = stock_info.get('current_price')
                            
                            stock_data = {
                                'symbol': symbol,
                                'current_price': stock_info.get('current_price', 0),
                                'iv': opp.get('iv', 0.35),
                                'price_52w_high': stock_info.get('high_52week', 0),
                                'price_52w_low': stock_info.get('low_52week', 0),
                                'market_cap': stock_info.get('market_cap', 0),
                                'pe_ratio': stock_info.get('pe_ratio', 28.5),
                                'sector': stock_info.get('sector', 'Unknown')
                            }

                            options_data = {
                                'strike_price': opp.get('strike_price', 0),
                                'dte': opp.get('dte', 0),
                                'delta': opp.get('delta', -0.30),
                                'premium': opp.get('premium', 0)
                            }

                            analysis = analyzer.analyze_stock_strategies(
                                symbol=symbol,
                                stock_data=stock_data,
                                options_data=options_data,
                                use_multi_model=True
                            )
                            st.session_state.strategy_analysis = analysis

            elif st.session_state.selected_stock:
                # Manual stock selection
                symbol = st.session_state.selected_stock
                st.markdown(f"### Analyzing: {symbol}")

                # Data refresh button
                if create_refresh_button(key="refresh_stock_data"):
                    # Clear cache and refetch
                    fetch_stock_info.clear()
                    fetch_options_suggestions.clear()
                    calculate_iv_for_stock.clear()
                    st.success("🔄 Data refreshed!")
                    st.rerun()
                
                # Fetch stock info
                stock_info = fetch_stock_info(symbol)

                if stock_info:
                    # Store actual stock price in session state for trade execution
                    if stock_info.get('current_price', 0) > 0:
                        st.session_state.selected_stock_price = stock_info.get('current_price')
                    
                    # Display data validation
                    display_data_validation(stock_info)
                    
                    # Manual override toggle
                    manual_override = st.checkbox(
                        "✏️ Manually Edit Auto-Filled Values",
                        value=st.session_state.manual_override,
                        help="Check this to customize stock and options parameters",
                        key="manual_override_toggle"
                    )
                    st.session_state.manual_override = manual_override

                    if not manual_override:
                        # Show quick stats (auto-filled)
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Price", f"${stock_info.get('current_price', 0):.2f}")
                        col2.metric("Market Cap", f"${stock_info.get('market_cap', 0)/1e9:.1f}B")
                        col3.metric("P/E", f"{stock_info.get('pe_ratio', 0):.1f}")
                    else:
                        # Editable stock data
                        st.markdown("**📈 Stock Data (Editable)**")
                        col1, col2 = st.columns(2)
                        with col1:
                            current_price = st.number_input(
                                "Current Price",
                                value=float(stock_info.get('current_price', 100)),
                                min_value=0.01,
                                step=0.01,
                                key="manual_price"
                            )
                            market_cap = st.number_input(
                                "Market Cap (B)",
                                value=float(stock_info.get('market_cap', 0)/1e9),
                                min_value=0.0,
                                step=0.1,
                                key="manual_market_cap"
                            )
                        with col2:
                            pe_ratio = st.number_input(
                                "P/E Ratio",
                                value=float(stock_info.get('pe_ratio', 28.5)),
                                min_value=0.0,
                                step=0.1,
                                key="manual_pe"
                            )
                            iv_override = st.number_input(
                                "IV (%)",
                                value=float(calculate_iv_for_stock(symbol) * 100),
                                min_value=0.0,
                                max_value=500.0,
                                step=1.0,
                                key="manual_iv"
                            )

                        # Update stock_info with manual values
                        stock_info['current_price'] = current_price
                        stock_info['market_cap'] = market_cap * 1e9
                        stock_info['pe_ratio'] = pe_ratio

                    # Get suggested options
                    options_suggestions = fetch_options_suggestions(symbol)
                    
                    # Validate options data if available (after manual override section)

                    if not manual_override:
                        # Auto-filled options (with dropdown)
                        if options_suggestions:
                            st.markdown("**Suggested Options:**")
                            option_idx = st.selectbox(
                                "Select Option",
                                range(len(options_suggestions)),
                                format_func=lambda i: (
                                    f"${options_suggestions[i]['strike']:.0f} | "
                                    f"Δ{options_suggestions[i]['delta']:.2f} | "
                                    f"{options_suggestions[i]['dte']}d"
                                ),
                                key="option_suggestion_select"
                            )

                            selected_option = options_suggestions[option_idx]
                        else:
                            st.info("Using default option parameters")
                            selected_option = {
                                'strike': stock_info.get('current_price', 100) * 0.95,
                                'dte': 30,
                                'delta': -0.30,
                                'premium': 250
                            }
                    else:
                        # Manual options data
                        st.markdown("**📊 Options Data (Editable)**")
                        default_option = options_suggestions[0] if options_suggestions else {
                            'strike': stock_info.get('current_price', 100) * 0.95,
                            'dte': 30,
                            'delta': -0.30,
                            'premium': 250
                        }

                        col1, col2 = st.columns(2)
                        with col1:
                            strike_override = st.number_input(
                                "Strike Price",
                                value=float(default_option['strike']),
                                min_value=0.01,
                                step=0.50,
                                key="manual_strike"
                            )
                            delta_override = st.number_input(
                                "Delta",
                                value=float(default_option['delta']),
                                min_value=-1.0,
                                max_value=1.0,
                                step=0.01,
                                key="manual_delta"
                            )
                        with col2:
                            dte_override = st.number_input(
                                "DTE",
                                value=int(default_option['dte']),
                                min_value=1,
                                max_value=365,
                                step=1,
                                key="manual_dte"
                            )
                            premium_override = st.number_input(
                                "Premium ($)",
                                value=float(default_option['premium']),
                                min_value=0.01,
                                step=10.0,
                                key="manual_premium"
                            )

                        selected_option = {
                            'strike': strike_override,
                            'dte': dte_override,
                            'delta': delta_override,
                            'premium': premium_override
                        }

                    # Analyze button
                    if st.button("🔍 Analyze All Strategies", type="primary", use_container_width=True):
                        with st.spinner(f"Analyzing all strategies for {symbol}..."):
                            # Use manual IV if override is enabled, otherwise calculate
                            iv_value = (iv_override / 100.0) if manual_override else calculate_iv_for_stock(symbol)

                            stock_data = {
                                'symbol': symbol,
                                'current_price': stock_info.get('current_price', 0),
                                'iv': iv_value,
                                'price_52w_high': stock_info.get('high_52week', 0),
                                'price_52w_low': stock_info.get('low_52week', 0),
                                'market_cap': stock_info.get('market_cap', 0),
                                'pe_ratio': stock_info.get('pe_ratio', 28.5),
                                'sector': stock_info.get('sector', 'Unknown')
                            }

                            options_data = {
                                'strike_price': selected_option.get('strike', 0),
                                'dte': selected_option.get('dte', 0),
                                'delta': selected_option.get('delta', -0.30),
                                'premium': selected_option.get('premium', 0)
                            }

                            analysis = analyzer.analyze_stock_strategies(
                                symbol=symbol,
                                stock_data=stock_data,
                                options_data=options_data,
                                use_multi_model=True
                            )
                            st.session_state.strategy_analysis = analysis
                else:
                    st.error(f"Could not fetch data for {symbol}")

            # === Display Strategy Analysis ===
            if st.session_state.strategy_analysis:
                analysis = st.session_state.strategy_analysis

                st.markdown("---")
                st.markdown("### 🌍 Market Environment")

                env = analysis.get('environment_analysis', {})

                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Volatility", env.get('volatility_regime', 'N/A').upper())
                col2.metric("Trend", env.get('trend', 'N/A').upper())
                # IV should already be decimal (0.35), multiply by 100 for display
                iv_display = env.get('iv', 0.35)
                # Ensure IV is in decimal format (not already percentage)
                if iv_display > 1.0:
                    iv_display = iv_display / 100.0
                col3.metric("IV", f"{iv_display*100:.1f}%")
                col4.metric("Market Regime", env.get('market_regime', 'N/A').replace('_', ' ').title())

                st.markdown("---")
                st.markdown("### 📊 Strategy Rankings")

                strategies = analysis.get('strategy_rankings', [])

                if strategies:
                    # Show top 3 strategies prominently
                    st.markdown("**Top 3 Strategies:**")

                    for idx, strategy in enumerate(strategies[:3]):
                        with st.expander(
                            f"{idx+1}. {strategy.get('name', 'Unknown')} - Score: {strategy.get('score', 0)}/100",
                            expanded=(idx == 0)
                        ):
                            col1, col2, col3 = st.columns(3)
                            col1.metric("Score", f"{strategy.get('score', 0)}/100")
                            col2.metric("Win Rate", f"{strategy.get('win_rate', 0)}")
                            col3.metric("Type", strategy.get('strategy_type', 'N/A'))

                            st.markdown(f"**Best When:** {strategy.get('best_when', 'N/A')}")
                            st.markdown(f"**Risk Profile:** {strategy.get('risk_profile', 'N/A')}")

                            # Add detailed trade execution instructions
                            st.markdown("---")
                            st.markdown("### 📋 Trade Execution Details")

                            # Get stock price and options data from analysis
                            # Use actual stock price from multiple sources, not default
                            stock_price = None
                            
                            # Try to get from analysis first
                            if 'stock_data' in analysis:
                                stock_price = analysis['stock_data'].get('current_price')
                            
                            # Fallback to session state
                            if not stock_price or stock_price == 0:
                                stock_price = st.session_state.get('selected_stock_price')
                            
                            # Fallback to stock_info if available
                            if (not stock_price or stock_price == 0) and st.session_state.selected_stock:
                                stock_info_fallback = fetch_stock_info(st.session_state.selected_stock)
                                if stock_info_fallback:
                                    stock_price = stock_info_fallback.get('current_price', 0)
                            
                            if not stock_price or stock_price == 0:
                                st.error("⚠️ Stock price not available. Cannot generate trade details.")
                                st.stop()
                            
                            options_data = {
                                'strike_price': analysis.get('strike', stock_price * 0.95),
                                'premium': analysis.get('premium', 2.50),
                                'dte': analysis.get('dte', 30),
                                'delta': analysis.get('delta', -0.30)
                            }

                            # Generate execution details for this strategy
                            execution = generate_trade_execution_details(
                                strategy.get('name', ''),
                                stock_price,
                                options_data
                            )

                            # Display trade legs
                            st.markdown("**Trade Legs:**")
                            for leg in execution.get('legs', []):
                                action = leg.get('action', '')
                                action_color = '🔴' if action == 'SELL' else '🟢' if action == 'BUY' else '⚪'
                                st.markdown(f"- {action_color} **{action}** {leg.get('quantity', 1)} {leg.get('type', '')} @ ${leg.get('strike', 0):.2f} (${leg.get('premium', 0):.2f} premium) - Exp: {leg.get('expiration', 'N/A')}")

                            # Display risk/reward metrics
                            st.markdown("**Risk/Reward:**")
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                total_credit = execution.get('total_credit', 0)
                                if isinstance(total_credit, (int, float)):
                                    st.metric("Total Credit", f"${total_credit:.2f}")
                                else:
                                    st.metric("Total Credit", str(total_credit))
                            with col2:
                                max_profit = execution.get('max_profit', 0)
                                if isinstance(max_profit, (int, float)):
                                    st.metric("Max Profit", f"${max_profit:.2f}")
                                else:
                                    st.metric("Max Profit", str(max_profit))
                            with col3:
                                max_loss = execution.get('max_loss', 0)
                                if isinstance(max_loss, (int, float)):
                                    st.metric("Max Loss", f"${max_loss:.2f}")
                                else:
                                    st.metric("Max Loss", str(max_loss))

                            # Display breakeven
                            st.markdown("**Breakeven:**")
                            if 'breakeven_lower' in execution and 'breakeven_upper' in execution:
                                st.info(f"Lower: ${execution['breakeven_lower']:.2f} | Upper: ${execution['breakeven_upper']:.2f}")
                            elif 'breakeven' in execution:
                                breakeven = execution['breakeven']
                                if isinstance(breakeven, (int, float)):
                                    st.info(f"${breakeven:.2f}")
                                else:
                                    st.info(str(breakeven))

                            # Display capital required
                            capital_required = execution.get('capital_required', 0)
                            if isinstance(capital_required, (int, float)):
                                st.info(f"💰 **Capital Required:** ${capital_required:.2f}")
                            else:
                                st.info(f"💰 **Capital Required:** {capital_required}")

                            # Display alternative examples
                            examples = execution.get('examples', [])
                            if examples:
                                st.markdown("---")
                                st.markdown("**📊 Alternative Strike Examples:**")
                                for example in examples:
                                    with st.expander(f"💡 {example.get('name', 'Example')}", expanded=False):
                                        if 'strike' in example:
                                            st.markdown(f"**Strike:** ${example.get('strike', 0):.2f}")
                                            st.markdown(f"**Premium:** ${example.get('premium', 0):.2f}")
                                        if 'strikes' in example:
                                            st.markdown(f"**Strikes:** {example.get('strikes', 'N/A')}")
                                        if 'put_strikes' in example:
                                            st.markdown(f"**Put Strikes:** {example.get('put_strikes', 'N/A')}")
                                            st.markdown(f"**Call Strikes:** {example.get('call_strikes', 'N/A')}")
                                        if 'credit' in example:
                                            st.markdown(f"**Credit:** ${example.get('credit', 0):.2f}")
                                        if 'max_profit' in example:
                                            st.markdown(f"**Max Profit:** ${example.get('max_profit', 0):.2f}")
                                        if 'max_loss' in example:
                                            st.markdown(f"**Max Loss:** ${example.get('max_loss', 0):.2f}")
                                        if 'breakeven' in example:
                                            st.markdown(f"**Breakeven:** ${example.get('breakeven', 0):.2f}")
                                        if 'win_probability' in example:
                                            st.markdown(f"**Win Probability:** {example.get('win_probability', 'N/A')}")
                                        if 'annualized_return' in example:
                                            st.markdown(f"**Annualized Return:** {example.get('annualized_return', 'N/A')}")

                    # Show all 10 strategies in table
                    st.markdown("**All Strategies:**")

                    strategy_df = pd.DataFrame([
                        {
                            'Rank': idx + 1,
                            'Strategy': s.get('name', 'Unknown'),
                            'Score': s.get('score', 0),
                            'Win Rate': s.get('win_rate', 'N/A')
                        }
                        for idx, s in enumerate(strategies)
                    ])

                    st.dataframe(strategy_df, use_container_width=True, hide_index=True)

                    # Show AI consensus if available
                    consensus = analysis.get('multi_model_consensus', {})
                    if consensus:
                        st.markdown("---")
                        st.markdown("### 🤖 Multi-Model AI Consensus")

                        for model_name, response in consensus.items():
                            if model_name != 'consensus_vote':
                                with st.expander(f"**{model_name.title()}**"):
                                    st.write(response)

                # Show position recommendation if analyzing a position
                if selected_position and 'recommendation' in analysis:
                    st.markdown("---")
                    st.markdown("### 💡 Position Recommendation")

                    recommendation = analysis.get('recommendation', 'KEEP')

                    if recommendation == 'KEEP':
                        st.success("✅ **KEEP** - Current strategy is still optimal")
                    elif recommendation == 'ADJUST':
                        st.warning("⚠️ **ADJUST** - Consider rolling or modifying position")
                    else:
                        st.error("❌ **CLOSE** - Exit this position")

                    # Cross-navigation button to Positions page
                    if st.button("📊 Go to Positions", type="secondary", help="View this position in the Positions page with full theta decay and P&L tracking"):
                        st.session_state.page = "Positions Page"
                        st.session_state.positions_highlight_symbol = symbol
                        st.rerun()

        else:
            # No stock selected
            st.info("👈 Select a stock from the left panel to begin analysis")

    # ========== RIGHT PANEL: Context & Info ==========
    with right_col:
        st.subheader("📰 Context")

        # LLM Provider Info
        with st.expander("🤖 AI Models", expanded=False):
            llm_config = LLMConfigUI(llm_manager)
            llm_config.render_simple_provider_list()

        # Quick Stats
        if st.session_state.selected_stock:
            symbol = st.session_state.selected_stock

            with st.expander("📊 Quick Stats", expanded=True):
                stock_info = fetch_stock_info(symbol)

                if stock_info:
                    volume = stock_info.get('volume', 0)
                    high_52w = stock_info.get('high_52week', 0)
                    low_52w = stock_info.get('low_52week', 0)
                    
                    st.metric("Volume", f"{volume:,.0f}" if volume > 0 else "N/A")
                    st.metric("52W High", f"${high_52w:.2f}" if high_52w > 0 else "N/A")
                    st.metric("52W Low", f"${low_52w:.2f}" if low_52w > 0 else "N/A")
                    
                    # Show warnings if data is missing
                    if volume == 0:
                        st.caption("⚠️ Volume data not available")
                    if high_52w == 0 or low_52w == 0:
                        st.caption("⚠️ 52-week data not available")
                else:
                    st.info("No data available")

        # Performance Metrics
        with st.expander("⚡ Performance", expanded=False):
            if st.session_state.scan_results:
                metadata = st.session_state.scan_results.get('metadata', {})
                exec_time = metadata.get('execution_time', 0)
                total_analyzed = metadata.get('total_analyzed', 0)

                st.metric("Scan Time", f"{exec_time:.1f}s")
                st.metric("Analyzed", f"{total_analyzed}")

                if exec_time > 0:
                    rate = total_analyzed / exec_time
                    st.metric("Rate", f"{rate:.0f}/sec")
            else:
                st.info("Run a scan to see performance metrics")

        # Help
        with st.expander("❓ Help", expanded=False):
            st.markdown("""
            **Quick Start:**
            1. Select a stock (manual, watchlist, or position)
            2. Adjust filters in left panel
            3. Click 'Run Scan' to find opportunities
            4. Click any result to analyze strategies
            5. Review all 10 strategies with AI consensus

            **Tip:** Use Current Positions mode to analyze your existing trades!
            """)

    # Footer
    st.markdown("---")
    st.caption("Options Analysis | Unified Screening + Strategy Analysis + Position Management")


if __name__ == "__main__":
    render_options_analysis_page()


