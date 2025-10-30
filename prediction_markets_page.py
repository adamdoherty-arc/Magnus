"""
Prediction Markets Page - AI-Powered Event Contract Opportunities
Displays prediction markets from Kalshi with quantitative scoring
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from src.kalshi_integration import KalshiIntegration
from src.prediction_market_analyzer import PredictionMarketAnalyzer

def show_prediction_markets():
    """Main function to display prediction markets page"""

    st.title("🎲 Prediction Markets")
    st.caption("AI-powered event contract opportunities from Kalshi")

    # Initialize integrations
    kalshi = KalshiIntegration()
    analyzer = PredictionMarketAnalyzer()

    # Filters in sidebar-style columns
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

    with col1:
        category_filter = st.selectbox(
            "Category",
            ["All", "Politics", "Sports", "Economics", "Crypto", "Companies", "Tech", "Climate", "World"],
            index=0
        )

    with col2:
        min_score = st.number_input("Min Score", min_value=0, max_value=100, value=60, step=5)

    with col3:
        max_days = st.number_input("Max Days", min_value=1, max_value=365, value=90, step=1)

    with col4:
        if st.button("🔄 Refresh", type="primary"):
            st.cache_data.clear()
            st.rerun()

    # Fetch and analyze markets
    with st.spinner("Fetching markets from Kalshi..."):
        markets = fetch_and_score_markets(kalshi, analyzer, category_filter, limit=50)

    if not markets:
        st.warning("No markets found. Kalshi API may be unavailable or rate-limited.")
        st.info("💡 Try again in a few moments. Kalshi allows 100 requests per minute.")
        return

    # Filter by score and days
    filtered_markets = [
        m for m in markets
        if m.get('ai_score', 0) >= min_score
        and m.get('days_to_close', 0) <= max_days
        and m.get('days_to_close', 0) > 0
    ]

    # Sort by score
    filtered_markets.sort(key=lambda x: x.get('ai_score', 0), reverse=True)

    # Display summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Markets", len(markets))
    with col2:
        st.metric("High Quality (>75)", len([m for m in filtered_markets if m.get('ai_score', 0) >= 75]))
    with col3:
        st.metric("Avg Score", f"{sum(m.get('ai_score', 0) for m in filtered_markets) / len(filtered_markets):.1f}" if filtered_markets else "N/A")
    with col4:
        st.metric("Showing", len(filtered_markets))

    st.markdown("---")

    # Display markets
    if not filtered_markets:
        st.info(f"No markets found with score >= {min_score} and <= {max_days} days to close.")
        return

    for market in filtered_markets[:20]:  # Show top 20
        display_market_card(market)

@st.cache_data(ttl=3600)  # Cache for 1 hour to avoid rate limiting
def fetch_and_score_markets(_kalshi, _analyzer, category, limit=50):
    """Fetch markets from Kalshi and score them"""
    try:
        # Fetch markets
        if category == "All":
            markets = _kalshi.get_enriched_markets(limit=limit)
        else:
            markets = _kalshi.get_markets_by_category(category, limit=limit)

        # Score each market
        scored_markets = []
        for market in markets:
            try:
                analysis = _analyzer.analyze_market(market)
                market.update(analysis)
                scored_markets.append(market)
            except Exception as e:
                print(f"Error scoring market {market.get('ticker')}: {e}")
                continue

        return scored_markets

    except Exception as e:
        st.error(f"Error fetching markets: {e}")
        return []

def display_market_card(market):
    """Display a single market opportunity card"""

    ticker = market.get('ticker', 'Unknown')
    title = market.get('title', 'Unknown Market')
    category = market.get('category', 'Other')
    yes_price = market.get('yes_price', 0)
    no_price = market.get('no_price', 0)
    volume_24h = market.get('volume_24h', 0)
    days_to_close = market.get('days_to_close', 0)
    ai_score = market.get('ai_score', 0)
    reasoning = market.get('ai_reasoning', 'No analysis available')
    recommendation = market.get('recommended_position', 'Skip')
    risk_level = market.get('risk_level', 'Unknown')
    expected_value = market.get('expected_value', 0)
    bid_ask_spread = market.get('bid_ask_spread', 0)

    # Score color coding
    if ai_score >= 85:
        score_color = "🔥"
        score_emoji = "🟢"
    elif ai_score >= 75:
        score_color = "⭐"
        score_emoji = "🟢"
    elif ai_score >= 60:
        score_color = "👍"
        score_emoji = "🟡"
    else:
        score_color = "👎"
        score_emoji = "🔴"

    # Create expandable card
    with st.expander(f"{score_emoji} **Score: {ai_score:.0f}** {score_color} | {category} | {days_to_close}d | {title}", expanded=False):

        # Market details in columns
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**📊 Pricing**")
            st.metric("Yes Price", f"{yes_price:.1%}" if yes_price else "N/A")
            st.metric("No Price", f"{no_price:.1%}" if no_price else "N/A")

        with col2:
            st.markdown("**💹 Volume & Liquidity**")
            st.metric("24h Volume", f"{volume_24h:,} contracts")
            st.metric("Spread", f"{bid_ask_spread:.1%}" if bid_ask_spread else "N/A")

        with col3:
            st.markdown("**🎯 Recommendation**")
            st.metric("Position", recommendation)
            st.metric("Risk Level", risk_level)

        # Analysis
        st.markdown("**🤖 Analysis:**")
        st.write(reasoning)

        # Expected value
        if expected_value and expected_value > 0:
            st.success(f"💰 Expected Value: +{expected_value:.1f}%")
        else:
            st.warning("Expected value is near zero or negative")

        # Action buttons
        col1, col2 = st.columns(2)
        with col1:
            robinhood_url = f"https://robinhood.com/markets/events/{ticker}"
            st.link_button("📱 View on Robinhood", robinhood_url, use_container_width=True)

        with col2:
            kalshi_url = f"https://kalshi.com/markets/{ticker}"
            st.link_button("📈 View on Kalshi", kalshi_url, use_container_width=True)

        # Market details
        with st.expander("📋 Market Details"):
            st.markdown(f"**Ticker:** `{ticker}`")
            st.markdown(f"**Category:** {category}")
            st.markdown(f"**Days to Close:** {days_to_close}")
            if market.get('close_date'):
                st.markdown(f"**Close Date:** {market['close_date']}")
            if market.get('description'):
                st.markdown(f"**Description:** {market['description']}")

        st.markdown("---")

def show():
    """Entry point for dashboard integration"""
    show_prediction_markets()

if __name__ == "__main__":
    show_prediction_markets()
