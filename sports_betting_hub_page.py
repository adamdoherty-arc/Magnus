"""
Sports Betting Hub - Unified Interface
======================================

Consolidated sports betting interface combining:
- Game Cards Visual (Live games + AI predictions)
- Kalshi NFL Markets (Prediction markets + trading)
- General Prediction Markets (Multi-sport coverage)

This hub provides a single, organized interface for all sports betting features.

Author: Magnus Trading Platform
Created: 2025-11-21
"""

import streamlit as st
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent))

st.set_page_config(
    page_title="Sports Betting Hub | Magnus",
    page_icon="🏈",
    layout="wide"
)

# Custom CSS for consistent styling
st.markdown("""
<style>
    .hub-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }

    .hub-stat {
        background: rgba(102, 126, 234, 0.1);
        border-left: 4px solid #667eea;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }

    .tab-content {
        padding: 1rem 0;
    }

    /* Sport type badges */
    .sport-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.25rem;
    }

    .sport-nfl { background: #013369; color: white; }
    .sport-nba { background: #C8102E; color: white; }
    .sport-ncaa { background: #00205B; color: white; }
    .sport-mlb { background: #041E42; color: white; }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# Header
# ============================================================================

st.markdown("""
<div class="hub-header">
    <h1 style="margin:0">🏈 Sports Betting Hub</h1>
    <p style="margin: 0.5rem 0 0 0; opacity: 0.9">
        Live Games • AI Predictions • Kalshi Markets • Multi-Sport Betting
    </p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# Quick Stats Summary
# ============================================================================

st.subheader("📊 Quick Stats")

try:
    # Import database managers for quick stats
    from src.nfl_db_manager import NFLDBManager
    from src.kalshi_db_manager import KalshiDBManager

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        try:
            nfl_db = NFLDBManager()
            live_games_count = nfl_db.get_live_games_count()
            st.metric("🔴 Live Games", live_games_count or 0)
        except Exception as e:
            st.metric("🔴 Live Games", "N/A")

    with col2:
        try:
            upcoming_count = nfl_db.get_upcoming_games_count()
            st.metric("📅 Upcoming", upcoming_count or 0)
        except Exception as e:
            st.metric("📅 Upcoming", "N/A")

    with col3:
        try:
            kalshi_db = KalshiDBManager()
            active_markets = kalshi_db.get_active_markets_count()
            st.metric("💹 Active Markets", active_markets or 0)
        except Exception as e:
            st.metric("💹 Active Markets", "N/A")

    with col4:
        try:
            portfolio_value = kalshi_db.get_portfolio_value()
            st.metric("💰 Portfolio", f"${portfolio_value:,.2f}" if portfolio_value else "$0.00")
        except Exception as e:
            st.metric("💰 Portfolio", "$0.00")

except Exception as e:
    st.warning(f"Could not load quick stats: {e}")

st.divider()

# ============================================================================
# Main Tabs
# ============================================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "🎮 Game Cards",
    "💹 Kalshi Markets",
    "🔮 Prediction Markets",
    "⚙️ Settings"
])

# ============================================================================
# TAB 1: Game Cards Visual
# ============================================================================

with tab1:
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)

    st.markdown("""
    ### 🎮 Live Game Cards

    Visual game cards with:
    - 📊 Live scores and odds
    - 🤖 AI-powered predictions
    - 📈 Win probability analysis
    - 💹 Kalshi market integration
    """)

    try:
        # Import and run game cards module
        from game_cards_visual_page import run_game_cards_page

        # Call the main function from game_cards_visual_page
        run_game_cards_page()

    except Exception as e:
        st.error(f"Error loading Game Cards: {e}")
        st.info("💡 Make sure game_cards_visual_page.py has a run_game_cards_page() function")

        # Fallback: Show basic interface
        st.markdown("### 🏈 NFL Games")

        sport_filter = st.selectbox(
            "Select Sport",
            ["NFL", "NBA", "NCAA Football", "NCAA Basketball", "MLB"],
            key="hub_game_cards_sport"
        )

        time_filter = st.radio(
            "Time Filter",
            ["Live", "Today", "This Week", "All Upcoming"],
            horizontal=True,
            key="hub_game_cards_time"
        )

        # Placeholder for game cards
        st.info(f"📊 Game cards for {sport_filter} ({time_filter}) will appear here")

    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# TAB 2: Kalshi Markets
# ============================================================================

with tab2:
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)

    st.markdown("""
    ### 💹 Kalshi Prediction Markets

    Trade on real-money prediction markets:
    - 🏈 NFL game outcomes
    - 📊 Point spreads and totals
    - 🏆 Season-long futures
    - 💰 Live market trading
    """)

    try:
        # Import and run Kalshi markets module
        from kalshi_nfl_markets_page import run_kalshi_markets_page

        run_kalshi_markets_page()

    except Exception as e:
        st.error(f"Error loading Kalshi Markets: {e}")
        st.info("💡 Make sure kalshi_nfl_markets_page.py has a run_kalshi_markets_page() function")

        # Fallback: Show basic interface
        st.markdown("### 🏈 NFL Markets")

        market_type = st.selectbox(
            "Market Type",
            ["Win/Loss", "Spread", "Total", "Season Futures"],
            key="hub_kalshi_market_type"
        )

        col1, col2 = st.columns([2, 1])

        with col1:
            st.info(f"📊 {market_type} markets will appear here")

        with col2:
            st.markdown("**Quick Actions**")
            if st.button("🔄 Refresh Markets", key="hub_refresh_markets"):
                st.rerun()

            if st.button("💰 View Portfolio", key="hub_view_portfolio"):
                st.info("Portfolio view coming soon")

    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# TAB 3: General Prediction Markets
# ============================================================================

with tab3:
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)

    st.markdown("""
    ### 🔮 Multi-Sport Prediction Markets

    Cross-sport prediction market analysis:
    - 🏀 NBA
    - 🏈 NCAA Football
    - 🏀 NCAA Basketball
    - ⚾ MLB
    - 🏒 NHL
    """)

    try:
        # Import and run prediction markets module
        from prediction_markets_page import run_prediction_markets_page

        run_prediction_markets_page()

    except Exception as e:
        st.error(f"Error loading Prediction Markets: {e}")
        st.info("💡 Make sure prediction_markets_page.py has a run_prediction_markets_page() function")

        # Fallback: Show basic interface
        st.markdown("### 📊 All Sports")

        sport_tabs = st.tabs(["🏈 NFL", "🏀 NBA", "🏈 NCAA FB", "🏀 NCAA BB", "⚾ MLB"])

        for idx, sport_tab in enumerate(sport_tabs):
            with sport_tab:
                sport_names = ["NFL", "NBA", "NCAA Football", "NCAA Basketball", "MLB"]
                st.info(f"📊 {sport_names[idx]} prediction markets will appear here")

    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# TAB 4: Settings & Configuration
# ============================================================================

with tab4:
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)

    st.markdown("### ⚙️ Sports Betting Settings")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🎯 Prediction Settings")

        enable_ai_predictions = st.checkbox(
            "Enable AI Predictions",
            value=True,
            key="hub_enable_ai_predictions",
            help="Show AI-powered game predictions"
        )

        prediction_model = st.selectbox(
            "Prediction Model",
            ["Ensemble (Recommended)", "NFL Predictor", "NBA Predictor", "Simple Model"],
            key="hub_prediction_model"
        )

        confidence_threshold = st.slider(
            "Minimum Confidence to Display",
            0.5, 0.95, 0.65,
            0.05,
            key="hub_confidence_threshold",
            help="Only show predictions with confidence above this threshold"
        )

    with col2:
        st.markdown("#### 💹 Kalshi Settings")

        kalshi_enabled = st.checkbox(
            "Enable Kalshi Integration",
            value=True,
            key="hub_kalshi_enabled",
            help="Show Kalshi market data and enable trading"
        )

        auto_sync_markets = st.checkbox(
            "Auto-Sync Markets",
            value=False,
            key="hub_auto_sync_markets",
            help="Automatically sync Kalshi markets every 5 minutes"
        )

        max_position_size = st.number_input(
            "Max Position Size ($)",
            min_value=10,
            max_value=10000,
            value=100,
            step=10,
            key="hub_max_position_size",
            help="Maximum dollars per market position"
        )

    st.divider()

    st.markdown("#### 📊 Display Settings")

    col3, col4 = st.columns(2)

    with col3:
        default_sport = st.selectbox(
            "Default Sport",
            ["NFL", "NBA", "NCAA Football", "NCAA Basketball", "MLB"],
            key="hub_default_sport"
        )

        games_per_page = st.slider(
            "Games Per Page",
            5, 50, 20,
            5,
            key="hub_games_per_page"
        )

    with col4:
        sort_by = st.selectbox(
            "Sort Games By",
            ["Start Time", "AI Confidence", "Win Probability", "Kalshi Volume"],
            key="hub_sort_by"
        )

        show_expired_markets = st.checkbox(
            "Show Expired Markets",
            value=False,
            key="hub_show_expired_markets"
        )

    st.divider()

    st.markdown("#### 🔔 Alerts & Notifications")

    alert_on_live_games = st.checkbox(
        "Alert on Live Games",
        value=True,
        key="hub_alert_live_games",
        help="Show notification when games go live"
    )

    alert_on_high_confidence = st.checkbox(
        "Alert on High Confidence Predictions",
        value=True,
        key="hub_alert_high_confidence",
        help="Notify when AI prediction confidence > 80%"
    )

    alert_on_market_opportunities = st.checkbox(
        "Alert on Market Opportunities",
        value=False,
        key="hub_alert_market_opportunities",
        help="Notify when Kalshi markets have favorable odds vs AI predictions"
    )

    st.divider()

    # Save settings button
    if st.button("💾 Save Settings", type="primary", key="hub_save_settings"):
        st.success("✅ Settings saved successfully!")
        st.balloons()

    # Reset to defaults
    if st.button("🔄 Reset to Defaults", key="hub_reset_settings"):
        st.warning("⚠️ Settings reset to defaults")
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# Footer
# ============================================================================

st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **📊 Data Sources**
    - ESPN Live Data
    - Kalshi Markets API
    - TradingView Alerts
    """)

with col2:
    st.markdown("""
    **🤖 AI Models**
    - NFL Predictor
    - NBA Predictor
    - NCAA Predictor
    - Ensemble Model
    """)

with col3:
    st.markdown("""
    **🔗 Quick Links**
    - [Kalshi Dashboard](https://kalshi.com)
    - [ESPN Scoreboard](https://espn.com)
    - [TradingView](https://tradingview.com)
    """)

st.caption("Magnus Trading Platform • Sports Betting Hub v1.0")


# ============================================================================
# Helper Functions (to be called by imported modules)
# ============================================================================

def run_game_cards_page():
    """Placeholder for game cards page - to be replaced by actual implementation"""
    st.info("Game Cards module not yet integrated")


def run_kalshi_markets_page():
    """Placeholder for Kalshi markets page - to be replaced by actual implementation"""
    st.info("Kalshi Markets module not yet integrated")


def run_prediction_markets_page():
    """Placeholder for prediction markets page - to be replaced by actual implementation"""
    st.info("Prediction Markets module not yet integrated")


if __name__ == "__main__":
    # This allows the page to be run standalone for testing
    pass
