"""
Prediction Markets Page - AI-Powered Event Contract Opportunities
Displays prediction markets from Kalshi with quantitative scoring
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from src.kalshi_db_manager import KalshiDBManager
from src.kalshi_ai_evaluator import KalshiAIEvaluator

def show_prediction_markets():
    """Main function to display prediction markets page"""

    st.title("🎲 Prediction Markets")
    st.caption("AI-powered event contract opportunities from Kalshi")

    # Initialize integrations
    db = KalshiDBManager()
    evaluator = KalshiAIEvaluator()

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

    # Fetch and analyze markets from database
    with st.spinner("Loading markets from database..."):
        markets = fetch_and_score_markets(db, evaluator, category_filter, limit=50)

    if not markets:
        st.warning("No markets found in database.")
        st.info("💡 Run the sync script to pull NFL markets: `python pull_nfl_games.py`")

        # Show database stats
        stats = db.get_stats()
        st.write(f"**Database Status:** {stats.get('total_markets', 0)} total markets, {stats.get('active_markets', 0)} active")
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

@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_and_score_markets(_db, _evaluator, category, limit=50):
    """Fetch markets from database with AI predictions"""
    try:
        # Fetch markets with predictions from database
        market_type = None
        if category == "Sports":
            market_type = "nfl"  # We only have NFL for now

        # Get markets with predictions (already scored by AI)
        markets_with_predictions = _db.get_top_opportunities(limit=limit)

        if markets_with_predictions:
            # Convert to format expected by display
            scored_markets = []
            for m in markets_with_predictions:
                scored_market = {
                    'ticker': m.get('ticker', ''),
                    'title': m.get('title', ''),
                    'category': 'Sports' if m.get('market_type') == 'nfl' else 'Other',
                    'yes_price': float(m.get('yes_price', 0)) if m.get('yes_price') else 0,
                    'no_price': float(m.get('no_price', 0)) if m.get('no_price') else 0,
                    'volume_24h': float(m.get('volume', 0)) if m.get('volume') else 0,
                    'days_to_close': calculate_days_to_close(m.get('close_time')),
                    'ai_score': float(m.get('confidence_score', 0)) if m.get('confidence_score') else 0,
                    'ai_reasoning': m.get('reasoning', 'No analysis available'),
                    'recommended_position': m.get('recommended_action', 'pass').upper(),
                    'risk_level': get_risk_level(m.get('confidence_score', 0)),
                    'expected_value': float(m.get('edge_percentage', 0)) if m.get('edge_percentage') else 0,
                    'bid_ask_spread': 0,  # Not available in current data
                    'close_date': m.get('close_time', ''),
                    'description': m.get('title', '')
                }
                scored_markets.append(scored_market)
            return scored_markets

        # If no predictions, get raw markets and analyze them
        active_markets = _db.get_active_markets(market_type=market_type)

        if not active_markets:
            return []

        # Generate predictions if needed
        predictions = _evaluator.evaluate_markets(active_markets[:limit])

        # Store predictions in database
        if predictions:
            _db.store_predictions(predictions)

        # Convert to display format
        scored_markets = []
        for i, pred in enumerate(predictions):
            market = active_markets[i] if i < len(active_markets) else {}
            scored_market = {
                'ticker': pred.get('ticker', ''),
                'title': market.get('title', ''),
                'category': 'Sports',
                'yes_price': float(market.get('yes_price', 0)) if market.get('yes_price') else 0,
                'no_price': float(market.get('no_price', 0)) if market.get('no_price') else 0,
                'volume_24h': float(market.get('volume', 0)) if market.get('volume') else 0,
                'days_to_close': calculate_days_to_close(market.get('close_time')),
                'ai_score': float(pred.get('confidence_score', 0)),
                'ai_reasoning': pred.get('reasoning', ''),
                'recommended_position': pred.get('recommended_action', 'pass').upper(),
                'risk_level': get_risk_level(pred.get('confidence_score', 0)),
                'expected_value': float(pred.get('edge_percentage', 0)),
                'bid_ask_spread': 0,
                'close_date': market.get('close_time', ''),
                'description': market.get('title', '')
            }
            scored_markets.append(scored_market)

        return scored_markets

    except Exception as e:
        st.error(f"Error fetching markets: {e}")
        import traceback
        st.code(traceback.format_exc())
        return []

def calculate_days_to_close(close_time):
    """Calculate days until market closes"""
    if not close_time:
        return 0
    try:
        from datetime import datetime, timezone
        import re

        if isinstance(close_time, str):
            # Fix timezone format: -05 -> -05:00
            close_time_fixed = re.sub(r'([-+]\d{2})$', r'\1:00', close_time)
            # Also handle Z suffix
            close_time_fixed = close_time_fixed.replace('Z', '+00:00')
            close_dt = datetime.fromisoformat(close_time_fixed)
        else:
            close_dt = close_time

        # Convert to UTC for consistent calculation
        if close_dt.tzinfo is not None:
            close_dt_utc = close_dt.astimezone(timezone.utc)
        else:
            close_dt_utc = close_dt.replace(tzinfo=timezone.utc)

        now_utc = datetime.now(timezone.utc)
        delta = (close_dt_utc - now_utc).total_seconds() / 86400  # Convert to days
        return max(0, int(delta))
    except Exception as e:
        # Log error for debugging
        import traceback
        print(f"Error parsing close_time '{close_time}': {e}")
        traceback.print_exc()
        return 0

def get_risk_level(confidence):
    """Get risk level based on confidence score"""
    if confidence >= 80:
        return "Low"
    elif confidence >= 60:
        return "Medium"
    else:
        return "High"

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
            st.link_button("📱 View on Robinhood", robinhood_url, width='stretch')

        with col2:
            kalshi_url = f"https://kalshi.com/markets/{ticker}"
            st.link_button("📈 View on Kalshi", kalshi_url, width='stretch')

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
