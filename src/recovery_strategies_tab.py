"""
Recovery Strategies Tab - UI component for CSP recovery and roll strategies

This module provides the Streamlit UI for displaying:
- CSP recovery recommendations
- Roll strategy evaluations
- AI-powered analysis and recommendations
"""

import streamlit as st
import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px

# Import analysis modules
from src.csp_recovery_analyzer import CSPRecoveryAnalyzer
from src.option_roll_evaluator import OptionRollEvaluator
from src.ai_options_advisor import AIOptionsAdvisor


def display_recovery_strategies_tab(positions: List[Dict], robinhood_client=None):
    """
    Display the recovery strategies tab

    Args:
        positions: List of current option positions
        robinhood_client: Robinhood API client for fetching data
    """
    st.markdown("## 🎯 Recovery Strategies")
    st.caption("AI-powered recommendations for recovering losing CSP positions")

    # Initialize analyzers
    csp_analyzer = CSPRecoveryAnalyzer()
    roll_evaluator = OptionRollEvaluator()
    ai_advisor = AIOptionsAdvisor()

    # Filter for losing CSP positions
    losing_positions = csp_analyzer.analyze_losing_positions(positions)

    if not losing_positions:
        st.info("🎉 No losing CSP positions found! All your puts are currently profitable.")
        return

    # Display summary metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_loss = sum(pos.get('current_loss', 0) for pos in losing_positions)
        st.metric(
            "Total Unrealized Loss",
            f"${abs(total_loss):,.2f}",
            delta=f"{len(losing_positions)} positions",
            delta_color="inverse"
        )

    with col2:
        avg_loss_pct = np.mean([pos.get('loss_percentage', 0) for pos in losing_positions])
        st.metric(
            "Average Loss %",
            f"{avg_loss_pct:.1f}%",
            delta="Below strike",
            delta_color="inverse"
        )

    with col3:
        total_at_risk = sum(pos.get('current_strike', 0) * 100 * pos.get('quantity', 1)
                           for pos in losing_positions)
        st.metric(
            "Capital at Risk",
            f"${total_at_risk:,.0f}",
            delta="If assigned"
        )

    with col4:
        avg_days = np.mean([pos.get('days_to_expiry', 0) for pos in losing_positions])
        st.metric(
            "Avg Days to Expiry",
            f"{avg_days:.0f}",
            delta="Time remaining"
        )

    st.markdown("---")

    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Recovery Opportunities",
        "🔄 Roll Evaluations",
        "🤖 AI Analysis",
        "📈 Risk Dashboard"
    ])

    with tab1:
        display_recovery_opportunities(losing_positions, csp_analyzer, ai_advisor)

    with tab2:
        display_roll_evaluations(losing_positions, roll_evaluator, ai_advisor)

    with tab3:
        display_ai_analysis(losing_positions, ai_advisor)

    with tab4:
        display_risk_dashboard(losing_positions)


def display_recovery_opportunities(losing_positions: List[Dict],
                                  analyzer: CSPRecoveryAnalyzer,
                                  advisor: AIOptionsAdvisor):
    """Display CSP recovery opportunities"""

    st.markdown("### 💡 Buy Better CSPs - Recovery Opportunities")
    st.caption("Recommended new positions to help recover losses")

    # Position selector with detailed information
    position_labels = []
    for pos in losing_positions:
        label = f"{pos['symbol']} ${pos['current_strike']:.2f} Put - Exp {pos.get('expiration_date', 'N/A')} ({pos['days_to_expiry']}d) - Loss: ${abs(pos['current_loss']):.0f}"
        position_labels.append(label)

    selected_position_label = st.selectbox(
        "Select position to analyze:",
        options=position_labels,
        format_func=lambda x: x,
        key="recovery_position_selector"
    )

    if selected_position_label:
        # Get selected position - extract symbol from label
        symbol = selected_position_label.split(' ')[0]
        selected_position = next(pos for pos in losing_positions if pos['symbol'] == symbol)

        # Show current position details
        with st.expander("📋 Current Position Details", expanded=True):
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Strike Price", f"${selected_position['current_strike']:.2f}")
                st.metric("Current Stock Price", f"${selected_position['current_price']:.2f}")

            with col2:
                st.metric("Premium Collected", f"${selected_position.get('premium_collected', 0):.2f}")
                st.metric("Current Loss", f"${abs(selected_position['current_loss']):.2f}")

            with col3:
                st.metric("Loss %", f"{selected_position['loss_percentage']:.1f}%")
                st.metric("Days to Expiry", selected_position['days_to_expiry'])

            with col4:
                st.metric("IV Rank", f"{selected_position.get('iv_rank', 50):.0f}")
                support_levels = selected_position.get('support_levels', [])
                if support_levels:
                    st.metric("Key Support", f"${support_levels[-1]:.2f}")

        # Find recovery opportunities
        with st.spinner(f"Finding recovery opportunities for {symbol}..."):
            opportunities = analyzer.find_recovery_opportunities(selected_position, num_strikes=5)

        if opportunities:
            # Create opportunities dataframe
            df_opportunities = pd.DataFrame(opportunities)

            # Format columns
            display_columns = [
                'strike', 'premium', 'yield_percent', 'annualized_yield',
                'probability_profit', 'recovery_percentage', 'ai_score', 'recommendation'
            ]

            # Filter and rename columns
            df_display = df_opportunities[display_columns].copy()
            df_display.columns = [
                'Strike', 'Premium', 'Yield %', 'Annual %',
                'Win Prob', 'Recovery %', 'AI Score', 'Recommendation'
            ]

            # Format numeric columns
            df_display['Strike'] = df_display['Strike'].apply(lambda x: f"${x:.2f}")
            df_display['Premium'] = df_display['Premium'].apply(lambda x: f"${x:.2f}")
            df_display['Yield %'] = df_display['Yield %'].apply(lambda x: f"{x:.2f}%")
            df_display['Annual %'] = df_display['Annual %'].apply(lambda x: f"{x:.1f}%")
            df_display['Win Prob'] = df_display['Win Prob'].apply(lambda x: f"{x*100:.1f}%")
            df_display['Recovery %'] = df_display['Recovery %'].apply(lambda x: f"{x:.1f}%")

            # Display table with color coding
            st.markdown("#### Top Recovery Opportunities")

            # Use Streamlit's dataframe with highlighting
            def highlight_scores(row):
                """Color code based on AI Score with dark text for readability"""
                score = float(row['AI Score'])
                if score >= 80:
                    # Green background with dark text
                    return ['background-color: #d4f4dd; color: #1a472a; font-weight: 500'] * len(row)
                elif score >= 60:
                    # Yellow background with dark text
                    return ['background-color: #fff4d4; color: #4a3c00; font-weight: 500'] * len(row)
                else:
                    # Pink background with dark text
                    return ['background-color: #ffd4d4; color: #4a0000; font-weight: 500'] * len(row)

            styled_df = df_display.style.apply(highlight_scores, axis=1)
            st.dataframe(styled_df, use_container_width=True, hide_index=True)

            # Detailed analysis for top opportunity
            if len(opportunities) > 0:
                best_opp = opportunities[0]

                st.markdown("#### 🏆 Best Recovery Opportunity Analysis")

                col1, col2 = st.columns([2, 1])

                with col1:
                    # AI Recommendation
                    ai_rec = advisor.recommend_strategy(selected_position, opportunities)
                    st.markdown("**AI Recommendation:**")
                    st.info(ai_rec[:500] + "..." if len(ai_rec) > 500 else ai_rec)

                with col2:
                    # Greeks Analysis
                    st.markdown("**Option Greeks:**")
                    greeks = advisor.analyze_option_greeks(
                        symbol,
                        best_opp['strike'],
                        best_opp['expiration'],
                        'put'
                    )

                    if 'values' in greeks:
                        for greek, value in greeks['values'].items():
                            st.caption(f"{greek.capitalize()}: {value:.4f}")

                # Monte Carlo Simulation
                with st.expander("🎲 Monte Carlo Simulation", expanded=False):
                    simulation = advisor.run_monte_carlo_simulation(
                        symbol,
                        best_opp['strike'],
                        best_opp['days_to_expiry']
                    )

                    if 'probability_profit' in simulation:
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.metric(
                                "Win Probability",
                                f"{simulation['probability_profit']*100:.1f}%"
                            )

                        with col2:
                            st.metric(
                                "Expected Loss if Assigned",
                                f"${simulation['expected_loss']:.2f}"
                            )

                        with col3:
                            st.metric(
                                "50th Percentile Price",
                                f"${simulation['percentile_50']:.2f}"
                            )

                        # Price distribution chart
                        fig = create_price_distribution_chart(simulation)
                        st.plotly_chart(fig, use_container_width=True)

                # Trade execution button
                st.markdown("---")
                col1, col2, col3 = st.columns([1, 1, 1])

                with col2:
                    if st.button(
                        f"🚀 Open {symbol} ${best_opp['strike']} Put in Robinhood",
                        type="primary",
                        use_container_width=True
                    ):
                        # Open Robinhood web interface
                        import webbrowser
                        webbrowser.open(f"https://robinhood.com/options/chains/{symbol}")
                        st.success("Opened Robinhood options chain")

        else:
            st.warning(f"No recovery opportunities found for {symbol}")


def display_roll_evaluations(losing_positions: List[Dict],
                            evaluator: OptionRollEvaluator,
                            advisor: AIOptionsAdvisor):
    """Display roll strategy evaluations"""

    st.markdown("### 🔄 Roll Strategy Evaluations")
    st.caption("Compare different roll strategies for each losing position")

    # Position selector with detailed information
    position_options = [
        f"{pos['symbol']} ${pos['current_strike']:.2f} Put - Exp {pos.get('expiration_date', 'N/A')} ({pos['days_to_expiry']}d) - {pos.get('quantity', 1)} contracts - Loss: ${abs(pos['current_loss']):.0f}"
        for pos in losing_positions
    ]

    selected_position_str = st.selectbox(
        "Select position to evaluate rolls:",
        options=position_options,
        key="roll_position_selector"
    )

    if selected_position_str:
        # Get selected position
        symbol = selected_position_str.split(' ')[0]
        selected_position = next(pos for pos in losing_positions if pos['symbol'] == symbol)

        # Evaluate all strategies
        with st.spinner(f"Evaluating roll strategies for {symbol}..."):
            comparison = evaluator.compare_strategies(selected_position)

        # Display strategy cards
        strategies = comparison['strategies']

        # Create columns for strategy comparison
        st.markdown("#### Strategy Comparison")

        # Strategy metrics in a comparison table
        strategy_data = []

        for key, strategy in strategies.items():
            if strategy.get('feasible', False):
                strategy_data.append({
                    'Strategy': strategy['strategy'],
                    'New Strike': f"${strategy.get('new_strike', selected_position['current_strike']):.2f}",
                    'Days Added': strategy.get('days_added', 0),
                    'Net Credit': f"${strategy.get('net_credit', 0):.2f}" if 'net_credit' in strategy else 'N/A',
                    'Win Prob': f"{strategy.get('probability_profit', 0)*100:.1f}%" if 'probability_profit' in strategy else 'N/A',
                    'Score': strategy.get('score', 0)
                })

        if strategy_data:
            df_strategies = pd.DataFrame(strategy_data)
            df_strategies = df_strategies.sort_values('Score', ascending=False)

            # Highlight best strategy
            def highlight_best(s):
                is_max = s == s.max()
                return ['background-color: #d4f4dd' if v else '' for v in is_max]

            styled_strategies = df_strategies.style.apply(
                highlight_best,
                subset=['Score'],
                axis=0
            )

            st.dataframe(styled_strategies, use_container_width=True, hide_index=True)

        # Detailed strategy cards
        st.markdown("#### Detailed Strategy Analysis")

        # Create expandable cards for each strategy
        for strategy_key, strategy in strategies.items():
            if strategy.get('feasible', False):
                with st.expander(
                    f"📊 {strategy['strategy']} (Score: {strategy.get('score', 0):.2f})",
                    expanded=(strategy_key == comparison['recommendation']['recommended_strategy'].lower().replace(' ', '_'))
                ):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("**Strategy Details:**")
                        st.write(strategy.get('description', ''))

                        # Key metrics
                        metrics = {
                            'New Strike': f"${strategy.get('new_strike', 'Same'):.2f}" if 'new_strike' in strategy else 'Same',
                            'New Expiration': strategy.get('new_expiration', 'Same'),
                            'Days Added': strategy.get('days_added', 0),
                            'Net Credit/Debit': f"${strategy.get('net_credit', 0):.2f}" if 'net_credit' in strategy else 'N/A',
                            'New Breakeven': f"${strategy.get('new_breakeven', 0):.2f}" if 'new_breakeven' in strategy else 'N/A',
                            'Capital at Risk': f"${strategy.get('capital_at_risk', 0):,.0f}" if 'capital_at_risk' in strategy else 'N/A'
                        }

                        for metric, value in metrics.items():
                            st.caption(f"**{metric}:** {value}")

                    with col2:
                        st.markdown("**Pros & Cons:**")

                        # Pros
                        if 'pros' in strategy:
                            st.markdown("✅ **Pros:**")
                            for pro in strategy['pros']:
                                st.caption(f"• {pro}")

                        # Cons
                        if 'cons' in strategy:
                            st.markdown("❌ **Cons:**")
                            for con in strategy['cons']:
                                st.caption(f"• {con}")

        # AI Recommendation
        st.markdown("---")
        st.markdown("#### 🤖 AI Recommendation")

        recommendation = comparison['recommendation']

        # Recommendation box with color based on confidence
        confidence_colors = {
            'High': 'success',
            'Medium': 'info',
            'Low': 'warning'
        }

        if recommendation['confidence'] == 'High':
            st.success(f"**{recommendation['recommended_strategy']}** - {recommendation['confidence']} Confidence")
        elif recommendation['confidence'] == 'Medium':
            st.info(f"**{recommendation['recommended_strategy']}** - {recommendation['confidence']} Confidence")
        else:
            st.warning(f"**{recommendation['recommended_strategy']}** - {recommendation['confidence']} Confidence")

        st.write(recommendation['reasoning'])

        col1, col2 = st.columns(2)
        with col1:
            st.caption(f"**Expected Outcome:** {recommendation.get('expected_outcome', 'N/A')}")
        with col2:
            st.caption(f"**Risk Assessment:** {recommendation.get('risk_assessment', 'N/A')}")

        # Execute button
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 1])

        with col2:
            if st.button(
                f"🚀 Execute {recommendation['recommended_strategy']} in Robinhood",
                type="primary",
                use_container_width=True
            ):
                import webbrowser
                webbrowser.open(f"https://robinhood.com/options/chains/{symbol}")
                st.success("Opened Robinhood for strategy execution")


def display_ai_analysis(losing_positions: List[Dict], advisor: AIOptionsAdvisor):
    """Display comprehensive AI analysis"""

    st.markdown("### 🤖 AI Market Analysis")
    st.caption("Deep analysis using fundamental, technical, and sentiment data")

    # Select position for analysis with detailed information
    # Group positions by symbol and show summary info
    position_details = {}
    for pos in losing_positions:
        symbol = pos['symbol']
        if symbol not in position_details:
            position_details[symbol] = {
                'count': 0,
                'total_loss': 0,
                'strikes': [],
                'expirations': []
            }
        position_details[symbol]['count'] += 1
        position_details[symbol]['total_loss'] += abs(pos.get('current_loss', 0))
        position_details[symbol]['strikes'].append(pos['current_strike'])
        if pos.get('expiration_date'):
            position_details[symbol]['expirations'].append(pos['expiration_date'])

    # Create detailed labels
    symbol_labels = []
    for symbol, details in position_details.items():
        if details['count'] > 1:
            label = f"{symbol} - {details['count']} positions - Total Loss: ${details['total_loss']:.0f}"
        else:
            label = f"{symbol} - ${details['strikes'][0]:.2f} Put - Loss: ${details['total_loss']:.0f}"
        symbol_labels.append(label)

    selected_symbol_label = st.selectbox(
        "Select position for deep analysis:",
        options=symbol_labels,
        key="ai_analysis_symbol"
    )

    if selected_symbol_label:
        # Extract symbol from label
        selected_symbol = selected_symbol_label.split(' - ')[0].strip()
        # Get position details
        position = next(pos for pos in losing_positions if pos['symbol'] == selected_symbol)

        # Create analysis tabs
        analysis_tab1, analysis_tab2, analysis_tab3 = st.tabs([
            "📊 Fundamental Analysis",
            "📈 Technical Analysis",
            "🎯 Greeks & Probabilities"
        ])

        with analysis_tab1:
            with st.spinner(f"Analyzing fundamentals for {selected_symbol}..."):
                fundamentals = advisor.fundamental_analyzer.analyze_sync(selected_symbol)

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Valuation Metrics:**")
                metrics = {
                    'P/E Ratio': fundamentals.get('pe_ratio', 'N/A'),
                    'PEG Ratio': fundamentals.get('peg_ratio', 'N/A'),
                    'Price/Book': fundamentals.get('price_to_book', 'N/A'),
                    'Debt/Equity': fundamentals.get('debt_to_equity', 'N/A')
                }
                for metric, value in metrics.items():
                    if value != 'N/A' and value is not None:
                        st.metric(metric, f"{value:.2f}")
                    else:
                        st.metric(metric, value)

            with col2:
                st.markdown("**Growth & Profitability:**")
                growth_metrics = {
                    'Revenue Growth': f"{fundamentals.get('revenue_growth', 0):.1f}%" if fundamentals.get('revenue_growth') else 'N/A',
                    'Profit Margin': f"{fundamentals.get('profit_margin', 0):.1f}%" if fundamentals.get('profit_margin') else 'N/A',
                    'Analyst Rating': fundamentals.get('analyst_rating', 'N/A'),
                    'Next Earnings': fundamentals.get('next_earnings', 'N/A')
                }
                for metric, value in growth_metrics.items():
                    st.caption(f"**{metric}:** {value}")

        with analysis_tab2:
            with st.spinner(f"Analyzing technicals for {selected_symbol}..."):
                technicals = advisor.technical_analyzer.analyze_sync(selected_symbol)

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Price Action:**")
                st.metric("Current Price", f"${technicals.get('current_price', 0):.2f}")
                st.metric("Trend", technicals.get('trend', 'N/A'))
                st.metric("Support", f"${technicals.get('support', 0):.2f}")
                st.metric("Resistance", f"${technicals.get('resistance', 0):.2f}")

            with col2:
                st.markdown("**Technical Indicators:**")
                st.metric("RSI", f"{technicals.get('rsi', 50):.1f} - {technicals.get('rsi_signal', '')}")
                st.metric("MACD Signal", technicals.get('macd_signal', 'N/A'))
                st.metric("50-Day MA", f"${technicals.get('ma_50', 0):.2f}")
                if technicals.get('ma_200'):
                    st.metric("200-Day MA", f"${technicals.get('ma_200', 0):.2f}")

            # Technical chart
            if st.checkbox("Show technical chart", value=False):
                fig = create_technical_chart(selected_symbol, technicals)
                st.plotly_chart(fig, use_container_width=True)

        with analysis_tab3:
            st.markdown("**Option Greeks Analysis:**")

            # Get Greeks for current position
            greeks_analysis = advisor.analyze_option_greeks(
                selected_symbol,
                position['current_strike'],
                position.get('expiration', '2024-01-19'),
                'put'
            )

            if 'values' in greeks_analysis:
                col1, col2, col3 = st.columns(3)

                greeks = greeks_analysis['values']
                interpretations = greeks_analysis['interpretations']

                with col1:
                    st.metric("Delta", f"{greeks['delta']:.4f}")
                    st.caption(interpretations['delta'])

                    st.metric("Gamma", f"{greeks['gamma']:.4f}")
                    st.caption(interpretations['gamma'])

                with col2:
                    st.metric("Theta", f"{greeks['theta']:.4f}")
                    st.caption(interpretations['theta'])

                    st.metric("Vega", f"{greeks['vega']:.4f}")
                    st.caption(interpretations['vega'])

                with col3:
                    st.metric("Rho", f"{greeks['rho']:.4f}")
                    st.caption(interpretations['rho'])

                    st.markdown("**Overall Assessment:**")
                    st.info(greeks_analysis.get('overall_assessment', ''))


def display_risk_dashboard(losing_positions: List[Dict]):
    """Display risk metrics dashboard"""

    st.markdown("### 📊 Risk Dashboard")
    st.caption("Portfolio-level risk analysis and metrics")

    # Calculate portfolio metrics
    total_at_risk = sum(pos['current_strike'] * 100 * pos.get('quantity', 1)
                       for pos in losing_positions)
    total_loss = sum(pos['current_loss'] for pos in losing_positions)

    # Group by symbol
    by_symbol = {}
    for pos in losing_positions:
        symbol = pos['symbol']
        if symbol not in by_symbol:
            by_symbol[symbol] = {
                'positions': 0,
                'total_loss': 0,
                'capital_at_risk': 0,
                'avg_days_to_expiry': []
            }
        by_symbol[symbol]['positions'] += 1
        by_symbol[symbol]['total_loss'] += pos['current_loss']
        by_symbol[symbol]['capital_at_risk'] += pos['current_strike'] * 100 * pos.get('quantity', 1)
        by_symbol[symbol]['avg_days_to_expiry'].append(pos['days_to_expiry'])

    # Display portfolio summary
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Positions at Risk", len(losing_positions))
        st.metric("Unique Symbols", len(by_symbol))

    with col2:
        st.metric("Total Unrealized Loss", f"${abs(total_loss):,.2f}")
        st.metric("Total Capital at Risk", f"${total_at_risk:,.2f}")

    with col3:
        avg_loss_pct = np.mean([pos['loss_percentage'] for pos in losing_positions])
        st.metric("Average Loss %", f"{avg_loss_pct:.1f}%")

        concentration = max(s['capital_at_risk'] for s in by_symbol.values()) / total_at_risk * 100
        st.metric("Max Concentration", f"{concentration:.1f}%")

    # Risk by symbol chart
    st.markdown("#### Risk Distribution by Symbol")

    # Create dataframe for visualization
    risk_data = []
    for symbol, data in by_symbol.items():
        risk_data.append({
            'Symbol': symbol,
            'Positions': data['positions'],
            'Loss': abs(data['total_loss']),
            'Capital at Risk': data['capital_at_risk'],
            'Avg Days': np.mean(data['avg_days_to_expiry'])
        })

    df_risk = pd.DataFrame(risk_data)

    # Create risk chart
    fig = px.scatter(
        df_risk,
        x='Capital at Risk',
        y='Loss',
        size='Positions',
        hover_data=['Symbol', 'Avg Days'],
        title='Risk vs Loss by Symbol',
        labels={'Capital at Risk': 'Capital at Risk ($)', 'Loss': 'Current Loss ($)'}
    )

    # Add diagonal line for reference
    max_val = max(df_risk['Capital at Risk'].max(), df_risk['Loss'].max())
    fig.add_trace(
        go.Scatter(
            x=[0, max_val],
            y=[0, max_val * 0.1],  # 10% loss line
            mode='lines',
            line=dict(dash='dash', color='red'),
            name='10% Loss Line',
            showlegend=True
        )
    )

    st.plotly_chart(fig, use_container_width=True)

    # Time decay analysis
    st.markdown("#### Time Decay Analysis")

    # Group by days to expiry
    expiry_buckets = {
        '0-7 days': [],
        '8-14 days': [],
        '15-30 days': [],
        '30+ days': []
    }

    for pos in losing_positions:
        days = pos['days_to_expiry']
        if days <= 7:
            expiry_buckets['0-7 days'].append(pos)
        elif days <= 14:
            expiry_buckets['8-14 days'].append(pos)
        elif days <= 30:
            expiry_buckets['15-30 days'].append(pos)
        else:
            expiry_buckets['30+ days'].append(pos)

    # Display expiry distribution
    col1, col2, col3, col4 = st.columns(4)

    for col, (bucket, positions) in zip([col1, col2, col3, col4], expiry_buckets.items()):
        with col:
            count = len(positions)
            if count > 0:
                total = sum(p['current_loss'] for p in positions)
                st.metric(
                    bucket,
                    f"{count} position{'s' if count != 1 else ''}",
                    f"${abs(total):,.0f} loss"
                )
            else:
                st.metric(bucket, "0 positions", "No exposure")

    # Risk recommendations
    st.markdown("---")
    st.markdown("#### 🎯 Risk Management Recommendations")

    recommendations = generate_risk_recommendations(losing_positions, by_symbol)

    for i, rec in enumerate(recommendations, 1):
        if rec['priority'] == 'High':
            st.error(f"{i}. {rec['text']}")
        elif rec['priority'] == 'Medium':
            st.warning(f"{i}. {rec['text']}")
        else:
            st.info(f"{i}. {rec['text']}")


def create_price_distribution_chart(simulation: Dict) -> go.Figure:
    """Create price distribution chart from Monte Carlo simulation"""

    fig = go.Figure()

    # Add percentile markers
    percentiles = [
        ('5th', simulation.get('percentile_5', 0), 'red'),
        ('25th', simulation.get('percentile_25', 0), 'orange'),
        ('50th', simulation.get('percentile_50', 0), 'green'),
        ('75th', simulation.get('percentile_75', 0), 'orange'),
        ('95th', simulation.get('percentile_95', 0), 'red')
    ]

    for label, value, color in percentiles:
        fig.add_vline(
            x=value,
            line_dash="dash",
            line_color=color,
            annotation_text=f"{label}: ${value:.2f}"
        )

    # Add strike price line
    fig.add_vline(
        x=simulation.get('strike', 0),
        line_color="blue",
        line_width=2,
        annotation_text=f"Strike: ${simulation.get('strike', 0):.2f}"
    )

    # Add current price line
    fig.add_vline(
        x=simulation.get('current_price', 0),
        line_color="black",
        line_width=2,
        annotation_text=f"Current: ${simulation.get('current_price', 0):.2f}"
    )

    fig.update_layout(
        title="Monte Carlo Price Distribution at Expiry",
        xaxis_title="Stock Price",
        yaxis_title="Probability",
        showlegend=True
    )

    return fig


def create_technical_chart(symbol: str, technicals: Dict) -> go.Figure:
    """Create technical analysis chart"""

    import yfinance as yf

    # Get price data
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period='3mo')

    fig = go.Figure()

    # Add candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=hist.index,
            open=hist['Open'],
            high=hist['High'],
            low=hist['Low'],
            close=hist['Close'],
            name='Price'
        )
    )

    # Add moving averages
    if 'ma_50' in technicals:
        fig.add_hline(
            y=technicals['ma_50'],
            line_color="blue",
            line_dash="dash",
            annotation_text="50-Day MA"
        )

    if 'ma_200' in technicals and technicals['ma_200']:
        fig.add_hline(
            y=technicals['ma_200'],
            line_color="red",
            line_dash="dash",
            annotation_text="200-Day MA"
        )

    # Add support/resistance
    if 'support' in technicals:
        fig.add_hline(
            y=technicals['support'],
            line_color="green",
            line_dash="dot",
            annotation_text="Support"
        )

    if 'resistance' in technicals:
        fig.add_hline(
            y=technicals['resistance'],
            line_color="red",
            line_dash="dot",
            annotation_text="Resistance"
        )

    fig.update_layout(
        title=f"{symbol} Technical Analysis",
        xaxis_title="Date",
        yaxis_title="Price",
        template="plotly_dark"
    )

    return fig


def generate_risk_recommendations(positions: List[Dict], by_symbol: Dict) -> List[Dict]:
    """Generate risk management recommendations"""

    recommendations = []

    # Check for high concentration
    total_at_risk = sum(s['capital_at_risk'] for s in by_symbol.values())
    for symbol, data in by_symbol.items():
        concentration = data['capital_at_risk'] / total_at_risk * 100
        if concentration > 30:
            recommendations.append({
                'priority': 'High',
                'text': f"{symbol} represents {concentration:.1f}% of risk. Consider reducing concentration."
            })

    # Check for near-term expirations
    urgent_positions = [p for p in positions if p['days_to_expiry'] <= 7]
    if urgent_positions:
        recommendations.append({
            'priority': 'High',
            'text': f"{len(urgent_positions)} position(s) expire within 7 days. Immediate action required."
        })

    # Check for deep losses
    deep_losses = [p for p in positions if p['loss_percentage'] > 10]
    if deep_losses:
        recommendations.append({
            'priority': 'Medium',
            'text': f"{len(deep_losses)} position(s) are down >10%. Consider rolling or accepting assignment."
        })

    # General recommendations
    if len(positions) > 5:
        recommendations.append({
            'priority': 'Low',
            'text': "Multiple losing positions detected. Review overall portfolio strategy and position sizing."
        })

    if not recommendations:
        recommendations.append({
            'priority': 'Low',
            'text': "Risk levels are manageable. Continue monitoring positions closely."
        })

    return recommendations


# Export the main display function
__all__ = ['display_recovery_strategies_tab']