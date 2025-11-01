"""
Modular AI Research Widget
Reusable across all Magnus pages
"""

import streamlit as st
from datetime import datetime
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


def display_ai_research_button(symbol: str, key_prefix: str = ""):
    """
    Display a single AI Research button

    Args:
        symbol: Stock ticker
        key_prefix: Unique prefix for button key (e.g., 'watchlist', 'positions', 'strategies')

    Returns:
        True if button was clicked
    """
    button_key = f"{key_prefix}_ai_btn_{symbol}" if key_prefix else f"ai_btn_{symbol}"
    if st.button(f"🤖 {symbol}", key=button_key):
        session_key = f'show_research_{key_prefix}_{symbol}' if key_prefix else f'show_research_{symbol}'
        st.session_state[session_key] = True
        return True
    return False


def display_ai_research_analysis(symbol: str, position_type: str = None):
    """
    Display full AI research analysis for a symbol

    Args:
        symbol: Stock ticker
        position_type: Optional context ('cash_secured_put', 'covered_call', etc.)
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
                st.markdown(
                    f"<div style='background-color: {action_color}; color: white; padding: 10px; "
                    f"border-radius: 5px; text-align: center; font-weight: bold; font-size: 18px;'>"
                    f"{rec['action'].replace('_', ' ')}</div>",
                    unsafe_allow_html=True
                )
            with col2:
                st.markdown(f"**Confidence:** {int(rec['confidence']*100)}%")
                st.write(rec['reasoning'])

            # Time-Sensitive Factors
            if rec.get('time_sensitive_factors'):
                st.warning("⏰ **Time-Sensitive Factors:**")
                for factor in rec['time_sensitive_factors']:
                    st.write(f"- {factor}")

            # Position-Specific Advice (if position type provided)
            if position_type and rec.get('specific_position_advice') and position_type in rec['specific_position_advice']:
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


def display_ai_research_expander(symbol: str, key_prefix: str = "", position_type: str = None):
    """
    Display AI Research in an expander if activated

    Args:
        symbol: Stock ticker
        key_prefix: Unique prefix for session state
        position_type: Type of position for context-aware advice
    """
    session_key = f'show_research_{key_prefix}_{symbol}' if key_prefix else f'show_research_{symbol}'

    if st.session_state.get(session_key, False):
        with st.expander(f"🤖 AI Research: {symbol}", expanded=True):
            display_ai_research_analysis(symbol, position_type)


def display_consolidated_ai_research_section(symbols: list, key_prefix: str = ""):
    """
    Display consolidated AI Research section for multiple symbols

    Args:
        symbols: List of stock tickers (will be deduplicated)
        key_prefix: Unique prefix for this section (e.g., 'positions', 'watchlist', 'strategies')

    Usage:
        # In any page
        from src.components.ai_research_widget import display_consolidated_ai_research_section

        symbols = ['AAPL', 'MSFT', 'GOOGL']
        display_consolidated_ai_research_section(symbols, key_prefix="my_page")
    """
    if not symbols:
        return

    # Deduplicate and sort
    unique_symbols = sorted(list(set(symbols)))

    st.markdown("---")
    st.markdown("### 🤖 AI Research for All Positions")
    st.caption(f"Analyzing {len(unique_symbols)} unique symbol(s)")

    # Display buttons in rows of 5
    num_rows = (len(unique_symbols) + 4) // 5
    for row in range(num_rows):
        start_idx = row * 5
        end_idx = min(start_idx + 5, len(unique_symbols))
        row_symbols = unique_symbols[start_idx:end_idx]

        cols = st.columns(len(row_symbols))
        for idx, symbol in enumerate(row_symbols):
            with cols[idx]:
                display_ai_research_button(symbol, key_prefix)

    # Display research expanders
    for symbol in unique_symbols:
        display_ai_research_expander(symbol, key_prefix)


def generate_external_links(symbol: str) -> dict:
    """Generate external research links for a symbol"""
    return {
        'Company Info': {
            'Yahoo Finance': f"https://finance.yahoo.com/quote/{symbol}",
            'TradingView': f"https://www.tradingview.com/symbols/{symbol}",
            'Finviz': f"https://finviz.com/quote.ashx?t={symbol}",
            'MarketWatch': f"https://www.marketwatch.com/investing/stock/{symbol}"
        },
        'Research': {
            'Seeking Alpha': f"https://seekingalpha.com/symbol/{symbol}",
            'SEC Filings': f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={symbol}",
            'Earnings Whispers': f"https://www.earningswhispers.com/stocks/{symbol}"
        },
        'Options': {
            'Options Chain': f"https://finance.yahoo.com/quote/{symbol}/options",
            'Barchart': f"https://www.barchart.com/stocks/quotes/{symbol}/options"
        },
        'News': {
            'Google News': f"https://news.google.com/search?q={symbol}+stock",
            'Benzinga': f"https://www.benzinga.com/quote/{symbol}"
        }
    }


def display_quick_links_section(symbols: list, key_prefix: str = ""):
    """
    Display Quick Research Links section

    Args:
        symbols: List of stock tickers
        key_prefix: Unique prefix for widget keys
    """
    if not symbols:
        return

    unique_symbols = sorted(list(set(symbols)))

    st.markdown("---")
    st.markdown("### 🔗 Quick Research Links")
    st.caption("Access external research tools and data sources")

    selected_symbol = st.selectbox(
        "Select symbol for links:",
        options=unique_symbols,
        key=f"{key_prefix}_links_selector"
    )

    if selected_symbol:
        links = generate_external_links(selected_symbol)

        tabs = st.tabs(["📊 Company Info", "📚 Research", "📈 Options", "📰 News"])

        with tabs[0]:
            st.markdown("**Company Information & Charts**")
            for name, url in links['Company Info'].items():
                st.markdown(f"- [{name}]({url})")

        with tabs[1]:
            st.markdown("**Research & Filings**")
            for name, url in links['Research'].items():
                st.markdown(f"- [{name}]({url})")

        with tabs[2]:
            st.markdown("**Options Analysis**")
            for name, url in links['Options'].items():
                st.markdown(f"- [{name}]({url})")

        with tabs[3]:
            st.markdown("**News & Social Sentiment**")
            for name, url in links['News'].items():
                st.markdown(f"- [{name}]({url})")
