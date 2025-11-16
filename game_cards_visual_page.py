"""
Visual Game Cards - Sports Betting Dashboard with Modern UI
Compact, responsive design inspired by DraftKings, FanDuel, and ESPN
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta
import re
import psycopg2
import psycopg2.extras
import logging
import os
from src.kalshi_db_manager import KalshiDBManager
from src.kalshi_client import KalshiClient
from src.espn_live_data import get_espn_client
from src.espn_ncaa_live_data import get_espn_ncaa_client
from src.ncaa_team_database import NCAA_LOGOS, get_team_logo_url, find_team_by_name
from src.game_watchlist_manager import GameWatchlistManager
from src.prediction_agents import NFLPredictor, NCAAPredictor

# Initialize logger first
logger = logging.getLogger(__name__)

# Optional auto-refresh (graceful degradation if not installed)
try:
    from streamlit_autorefresh import st_autorefresh
    AUTOREFRESH_AVAILABLE = True
except ImportError:
    AUTOREFRESH_AVAILABLE = False
    logger.warning("streamlit-autorefresh not installed. Auto-refresh feature disabled.")

# NFL Team Logo URLs (ESPN)
TEAM_LOGOS = {
    'Arizona': 'https://a.espncdn.com/i/teamlogos/nfl/500/ari.png',
    'Atlanta': 'https://a.espncdn.com/i/teamlogos/nfl/500/atl.png',
    'Baltimore': 'https://a.espncdn.com/i/teamlogos/nfl/500/bal.png',
    'Buffalo': 'https://a.espncdn.com/i/teamlogos/nfl/500/buf.png',
    'Carolina': 'https://a.espncdn.com/i/teamlogos/nfl/500/car.png',
    'Chicago': 'https://a.espncdn.com/i/teamlogos/nfl/500/chi.png',
    'Cincinnati': 'https://a.espncdn.com/i/teamlogos/nfl/500/cin.png',
    'Cleveland': 'https://a.espncdn.com/i/teamlogos/nfl/500/cle.png',
    'Dallas': 'https://a.espncdn.com/i/teamlogos/nfl/500/dal.png',
    'Denver': 'https://a.espncdn.com/i/teamlogos/nfl/500/den.png',
    'Detroit': 'https://a.espncdn.com/i/teamlogos/nfl/500/det.png',
    'Green Bay': 'https://a.espncdn.com/i/teamlogos/nfl/500/gb.png',
    'Houston': 'https://a.espncdn.com/i/teamlogos/nfl/500/hou.png',
    'Indianapolis': 'https://a.espncdn.com/i/teamlogos/nfl/500/ind.png',
    'Jacksonville': 'https://a.espncdn.com/i/teamlogos/nfl/500/jax.png',
    'Kansas City': 'https://a.espncdn.com/i/teamlogos/nfl/500/kc.png',
    'Las Vegas': 'https://a.espncdn.com/i/teamlogos/nfl/500/lv.png',
    'Los Angeles Chargers': 'https://a.espncdn.com/i/teamlogos/nfl/500/lac.png',
    'Los Angeles Rams': 'https://a.espncdn.com/i/teamlogos/nfl/500/lar.png',
    'Miami': 'https://a.espncdn.com/i/teamlogos/nfl/500/mia.png',
    'Minnesota': 'https://a.espncdn.com/i/teamlogos/nfl/500/min.png',
    'New England': 'https://a.espncdn.com/i/teamlogos/nfl/500/ne.png',
    'New Orleans': 'https://a.espncdn.com/i/teamlogos/nfl/500/no.png',
    'New York Giants': 'https://a.espncdn.com/i/teamlogos/nfl/500/nyg.png',
    'New York Jets': 'https://a.espncdn.com/i/teamlogos/nfl/500/nyj.png',
    'Philadelphia': 'https://a.espncdn.com/i/teamlogos/nfl/500/phi.png',
    'Pittsburgh': 'https://a.espncdn.com/i/teamlogos/nfl/500/pit.png',
    'San Francisco': 'https://a.espncdn.com/i/teamlogos/nfl/500/sf.png',
    'Seattle': 'https://a.espncdn.com/i/teamlogos/nfl/500/sea.png',
    'Tampa Bay': 'https://a.espncdn.com/i/teamlogos/nfl/500/tb.png',
    'Tennessee': 'https://a.espncdn.com/i/teamlogos/nfl/500/ten.png',
    'Washington': 'https://a.espncdn.com/i/teamlogos/nfl/500/wsh.png',
}

# NCAA Team Logo URLs - Now imported from comprehensive team database
# NCAA_LOGOS contains 130+ FBS teams with dynamic logo fetching from ESPN API
# See src/ncaa_team_database.py for complete team list

# Shortened team names for display
TEAM_SHORT_NAMES = {
    'Arizona': 'ARI',
    'Atlanta': 'ATL',
    'Baltimore': 'BAL',
    'Buffalo': 'BUF',
    'Carolina': 'CAR',
    'Chicago': 'CHI',
    'Cincinnati': 'CIN',
    'Cleveland': 'CLE',
    'Dallas': 'DAL',
    'Denver': 'DEN',
    'Detroit': 'DET',
    'Green Bay': 'GB',
    'Houston': 'HOU',
    'Indianapolis': 'IND',
    'Jacksonville': 'JAX',
    'Kansas City': 'KC',
    'Las Vegas': 'LV',
    'Los Angeles Chargers': 'LAC',
    'Los Angeles Rams': 'LAR',
    'Miami': 'MIA',
    'Minnesota': 'MIN',
    'New England': 'NE',
    'New Orleans': 'NO',
    'New York Giants': 'NYG',
    'New York Jets': 'NYJ',
    'Philadelphia': 'PHI',
    'Pittsburgh': 'PIT',
    'San Francisco': 'SF',
    'Seattle': 'SEA',
    'Tampa Bay': 'TB',
    'Tennessee': 'TEN',
    'Washington': 'WSH',
}


def show_game_cards():
    """Main function for visual game cards with modern compact UI"""

    # Apply custom CSS for compact, modern design
    st.markdown("""
        <style>
        /* Compact header spacing */
        .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }

        /* Sticky header */
        .sticky-header {
            position: sticky;
            top: 0;
            z-index: 999;
            background: var(--background-color);
            padding: 0.5rem 0;
            border-bottom: 1px solid var(--secondary-background-color);
        }

        /* Sport tabs - horizontal compact design */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }

        .stTabs [data-baseweb="tab"] {
            padding: 8px 16px;
            font-size: 14px;
            font-weight: 600;
        }

        /* Collapsible sections */
        .streamlit-expanderHeader {
            font-size: 14px;
            font-weight: 600;
        }

        /* Compact metrics */
        [data-testid="stMetricValue"] {
            font-size: 20px;
        }

        /* Game cards with visible border on all 4 sides - TILE EFFECT */
        .game-card {
            padding: 12px 16px;
            margin-bottom: 16px;
            background: var(--secondary-background-color);
            border: 2px solid rgba(128, 128, 128, 0.5);
            border-radius: 12px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2),
                        inset 0 1px 0 rgba(255, 255, 255, 0.1);
            transition: all 0.3s ease;
        }

        .game-card:hover {
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3),
                        inset 0 1px 0 rgba(255, 255, 255, 0.15);
            transform: translateY(-2px);
        }

        /* Live indicator */
        .live-indicator {
            display: inline-block;
            width: 8px;
            height: 8px;
            background: #ff4444;
            border-radius: 50%;
            animation: pulse 2s infinite;
            margin-right: 6px;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.4; }
        }

        /* Card action buttons (Subscribe/Unsubscribe) */
        .game-card .stButton button {
            padding: 8px 14px;
            font-size: 13px;
            font-weight: 500;
        }

        /* Filter and control buttons */
        .filter-buttons .stButton button {
            padding: 6px 12px;
            font-size: 12px;
        }

        /* Pagination buttons */
        .pagination-buttons .stButton button {
            padding: 8px 16px;
            font-size: 13px;
        }

        /* Watch list sidebar */
        .watch-sidebar {
            background: var(--secondary-background-color);
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 16px;
        }

        /* Hide excessive spacing - make cards compact */
        .element-container {
            margin-bottom: 0.3rem;
        }

        /* Reduce spacing in game cards specifically */
        .game-card .element-container {
            margin-bottom: 0.2rem;
        }

        /* Compact metrics in cards */
        .game-card [data-testid="stMetricValue"] {
            font-size: 18px;
            line-height: 1.2;
        }

        .game-card [data-testid="stMetricLabel"] {
            font-size: 11px;
        }

        /* Reduce button padding in cards */
        .game-card .stButton button {
            padding: 6px 12px;
            font-size: 12px;
        }

        /* Responsive grid */
        @media (max-width: 768px) {
            .block-container {
                padding: 0.5rem;
            }
        }

        /* Predicted winner highlighting - HIGH CONFIDENCE */
        .predicted-winner-high {
            border: 3px solid #00ff00 !important;
            background: linear-gradient(135deg, rgba(0, 255, 0, 0.12) 0%, rgba(0, 255, 0, 0.05) 100%) !important;
            box-shadow: 0 0 25px rgba(0, 255, 0, 0.6),
                        0 4px 12px rgba(0, 0, 0, 0.3),
                        inset 0 1px 0 rgba(0, 255, 0, 0.2) !important;
            animation: pulse-green 2s infinite;
        }

        /* Predicted winner highlighting - MEDIUM CONFIDENCE */
        .predicted-winner-medium {
            border: 3px solid #ffd700 !important;
            background: linear-gradient(135deg, rgba(255, 215, 0, 0.1) 0%, rgba(255, 215, 0, 0.04) 100%) !important;
            box-shadow: 0 0 20px rgba(255, 215, 0, 0.5),
                        0 4px 12px rgba(0, 0, 0, 0.3),
                        inset 0 1px 0 rgba(255, 215, 0, 0.15) !important;
            animation: pulse-yellow 2s infinite;
        }

        /* Predicted winner highlighting - LOW CONFIDENCE */
        .predicted-winner-low {
            border: 2px solid rgba(150, 150, 150, 0.6) !important;
            background: var(--secondary-background-color) !important;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2),
                        inset 0 1px 0 rgba(255, 255, 255, 0.05) !important;
        }

        /* Pulse animations */
        @keyframes pulse-green {
            0%, 100% {
                box-shadow: 0 0 25px rgba(0, 255, 0, 0.6),
                            0 4px 12px rgba(0, 0, 0, 0.3),
                            inset 0 1px 0 rgba(0, 255, 0, 0.2);
            }
            50% {
                box-shadow: 0 0 35px rgba(0, 255, 0, 0.8),
                            0 6px 16px rgba(0, 0, 0, 0.4),
                            inset 0 1px 0 rgba(0, 255, 0, 0.3);
            }
        }

        @keyframes pulse-yellow {
            0%, 100% {
                box-shadow: 0 0 20px rgba(255, 215, 0, 0.5),
                            0 4px 12px rgba(0, 0, 0, 0.3),
                            inset 0 1px 0 rgba(255, 215, 0, 0.15);
            }
            50% {
                box-shadow: 0 0 30px rgba(255, 215, 0, 0.7),
                            0 6px 16px rgba(0, 0, 0, 0.4),
                            inset 0 1px 0 rgba(255, 215, 0, 0.25);
            }
        }

        /* Glowing bar above predicted winner - replaces team logo highlighting */
        .winner-column-high {
            position: relative;
            border-top: 4px solid #00ff00;
            box-shadow: 0 -3px 15px rgba(0, 255, 0, 0.8);
            animation: pulse-top-bar-green 2s infinite;
            padding-top: 8px;
        }

        .winner-column-medium {
            position: relative;
            border-top: 4px solid #ffd700;
            box-shadow: 0 -3px 12px rgba(255, 215, 0, 0.7);
            animation: pulse-top-bar-yellow 2s infinite;
            padding-top: 8px;
        }

        .winner-column-low {
            padding-top: 8px;
        }

        /* Pulse animations for top bars */
        @keyframes pulse-top-bar-green {
            0%, 100% {
                box-shadow: 0 -3px 15px rgba(0, 255, 0, 0.8);
                border-top-color: #00ff00;
            }
            50% {
                box-shadow: 0 -5px 25px rgba(0, 255, 0, 1.0);
                border-top-color: #00ff88;
            }
        }

        @keyframes pulse-top-bar-yellow {
            0%, 100% {
                box-shadow: 0 -3px 12px rgba(255, 215, 0, 0.7);
                border-top-color: #ffd700;
            }
            50% {
                box-shadow: 0 -5px 20px rgba(255, 215, 0, 0.9);
                border-top-color: #ffea00;
            }
        }

        /* Confidence badge styling */
        .confidence-badge {
            display: inline-block;
            padding: 6px 12px;
            border-radius: 20px;
            font-weight: 700;
            font-size: 14px;
            text-align: center;
            margin: 8px 0;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .confidence-high {
            background: linear-gradient(135deg, #00ff00 0%, #00cc00 100%);
            color: #000;
            box-shadow: 0 0 15px rgba(0, 255, 0, 0.6);
            animation: pulse-badge-green 2s infinite;
        }

        .confidence-medium {
            background: linear-gradient(135deg, #ffd700 0%, #ffaa00 100%);
            color: #000;
            box-shadow: 0 0 12px rgba(255, 215, 0, 0.5);
            animation: pulse-badge-yellow 2s infinite;
        }

        .confidence-low {
            background: linear-gradient(135deg, #888 0%, #666 100%);
            color: #fff;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        }

        @keyframes pulse-badge-green {
            0%, 100% { box-shadow: 0 0 15px rgba(0, 255, 0, 0.6); }
            50% { box-shadow: 0 0 25px rgba(0, 255, 0, 0.9); }
        }

        @keyframes pulse-badge-yellow {
            0%, 100% { box-shadow: 0 0 12px rgba(255, 215, 0, 0.5); }
            50% { box-shadow: 0 0 20px rgba(255, 215, 0, 0.8); }
        }
        </style>
    """, unsafe_allow_html=True)

    # Initialize
    db = KalshiDBManager()
    watchlist_manager = GameWatchlistManager(db)

    # Initialize prediction agents (cached in session state)
    if 'nfl_predictor' not in st.session_state:
        try:
            st.session_state.nfl_predictor = NFLPredictor()
            logger.info("NFL Predictor initialized")
        except Exception as e:
            logger.warning(f"Could not initialize NFL Predictor: {e}")
            st.session_state.nfl_predictor = None

    if 'ncaa_predictor' not in st.session_state:
        try:
            st.session_state.ncaa_predictor = NCAAPredictor()
            logger.info("NCAA Predictor initialized")
        except Exception as e:
            logger.warning(f"Could not initialize NCAA Predictor: {e}")
            st.session_state.ncaa_predictor = None

    # Initialize user ID (from Telegram or default)
    if 'user_id' not in st.session_state:
        telegram_user_id = os.getenv('TELEGRAM_AUTHORIZED_USERS', 'default_user').split(',')[0]
        st.session_state.user_id = telegram_user_id

    # Store selected sport in session state
    if 'selected_sport' not in st.session_state:
        st.session_state.selected_sport = 'NFL'

    # Initialize filters collapsed state
    if 'filters_collapsed' not in st.session_state:
        st.session_state.filters_collapsed = True

    # Initialize watch sidebar collapsed state
    if 'watch_sidebar_collapsed' not in st.session_state:
        st.session_state.watch_sidebar_collapsed = False

    # ==================== COMPACT STICKY HEADER ====================
    st.markdown('<div class="sticky-header">', unsafe_allow_html=True)

    # Title row - more compact
    col_title, col_watch, col_ai, col_refresh = st.columns([3, 2, 2, 1])

    with col_title:
        st.markdown("## 🏟️ Sports Game Cards")

    with col_watch:
        # Watch list count
        watchlist = watchlist_manager.get_user_watchlist(st.session_state.user_id)
        watch_count = len(watchlist) if watchlist else 0

        # Auto-cleanup: Remove finished games from watchlist
        if watchlist:
            cleaned_count = watchlist_manager.cleanup_finished_games(st.session_state.user_id)
            if cleaned_count > 0:
                watch_count = len(watchlist_manager.get_user_watchlist(st.session_state.user_id))

        if watch_count > 0:
            if st.button(f"📍 Watching: {watch_count}", key="toggle_watch_sidebar", use_container_width=True):
                st.session_state.watch_sidebar_collapsed = not st.session_state.watch_sidebar_collapsed
        else:
            st.caption("📍 Watch games for updates")

    with col_ai:
        # Initialize LLM Service
        try:
            from src.services.llm_service import LLMService
            llm_service = LLMService()
            available_providers = llm_service.get_available_providers()
            llm_available = True
        except Exception as e:
            logger.warning(f"LLM Service not available: {e}")
            llm_available = False
            available_providers = []

        # Compact AI model selector
        model_options = ["Local AI"]
        if llm_available and "groq" in available_providers:
            model_options.append("Groq")
        if llm_available and "deepseek" in available_providers:
            model_options.append("DeepSeek")

        selected_model = st.selectbox(
            "AI Model",
            model_options,
            label_visibility="collapsed",
            key="ai_model_selector"
        )
        st.session_state.ai_model = f"{selected_model} (Fast & Free)" if selected_model == "Local AI" else selected_model

    with col_refresh:
        # Auto-refresh toggle
        auto_refresh = st.checkbox("🔄", value=False, key="auto_refresh_header", help="Auto-refresh")

    st.markdown('</div>', unsafe_allow_html=True)

    # ==================== SPORT TABS (Horizontal at top) ====================
    sport_tabs = st.tabs(["🏈 NFL", "🎓 NCAA", "🏀 NBA", "⚾ MLB"])

    with sport_tabs[0]:  # NFL
        sport_filter = "NFL"
        st.session_state.selected_sport = 'NFL'
        show_sport_games(db, watchlist_manager, sport_filter, "NFL", llm_service if llm_available else None, auto_refresh)

    with sport_tabs[1]:  # NCAA
        sport_filter = "CFB"
        st.session_state.selected_sport = 'NCAA'
        show_sport_games(db, watchlist_manager, sport_filter, "NCAA", llm_service if llm_available else None, auto_refresh)

    with sport_tabs[2]:  # NBA
        st.info("🏀 **NBA Coming Soon** - Integration in progress")

    with sport_tabs[3]:  # MLB
        st.info("⚾ **MLB Coming Soon** - Integration in progress")


def show_sport_games(db, watchlist_manager, sport_filter, sport_name, llm_service=None, auto_refresh=False):
    """Display games for a specific sport with compact UI"""

    # Get selected AI model from session state
    selected_ai_model = st.session_state.get('ai_model', 'Local AI (Fast & Free)')

    # ==================== ALWAYS VISIBLE FILTERS ====================
    st.markdown("### 🎛️ Filters & Sorting")

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        sort_by = st.selectbox(
            "Sort By",
            ["🔴 Live First", "⏰ Game Time", "🎯 Best Odds"],
            key=f"sort_{sport_filter}",
            help="Sort games (AI sorting disabled for performance)"
        )

    with col2:
        filter_status = st.selectbox(
            "Game Status",
            ["All Games", "Live Only", "Upcoming", "Final"],
            key=f"filter_{sport_filter}"
        )

    with col3:
        odds_filter = st.selectbox(
            "Money Filter",
            ["All Games", "💰 EV > 5%", "💰 EV > 10%", "🎯 High Confidence"],
            key=f"odds_filter_{sport_filter}"
        )

    with col4:
        min_opportunity = st.slider(
            "Min EV %",
            0, 50, 0,
            key=f"min_opp_{sport_filter}"
        )

    with col5:
        cards_per_row = st.selectbox(
            "Cards/Row",
            [2, 3, 4],
            index=2,  # Default to 4
            key=f"cards_per_row_{sport_filter}"
        )

    with col6:
        hide_final = st.checkbox(
            "Hide Final",
            value=False,
            key=f"hide_final_{sport_filter}",
            help="Filter out completed games"
        )

    # Auto-refresh settings row
    col_auto1, col_auto2 = st.columns([1, 1])
    with col_auto1:
        auto_refresh_enabled = st.checkbox(
            "⚡ Auto-Refresh",
            value=False,
            key=f"auto_refresh_{sport_filter}",
            help="Automatically sync live data at set interval"
        )
    with col_auto2:
        if auto_refresh_enabled:
            refresh_interval = st.selectbox(
                "Interval",
                ["30 sec", "1 min", "2 min", "5 min"],
                index=2,  # Default to 2 min
                key=f"refresh_interval_{sport_filter}"
            )
        else:
            refresh_interval = None

    # Manual sync buttons and status
    col_sync1, col_sync2, col_sync3, col_sync4 = st.columns([2, 2, 2, 1])
    with col_sync1:
        if st.button("🔄 Sync ESPN Data", key=f"sync_espn_{sport_filter}", help="Refresh live scores from ESPN", use_container_width=True):
            with st.spinner(f"Syncing {sport_name} data from ESPN..."):
                st.cache_data.clear()
                import time
                time.sleep(0.5)  # Brief pause to show spinner
            st.success(f"✅ {sport_name} data refreshed!")
            st.rerun()
    with col_sync2:
        if st.button("💰 Sync Kalshi Odds", key=f"sync_kalshi_{sport_filter}", help="Refresh betting odds from Kalshi", use_container_width=True):
            with st.spinner("Syncing Kalshi betting odds..."):
                st.cache_data.clear()
                import time
                time.sleep(0.5)
            st.success("✅ Kalshi odds refreshed!")
            st.rerun()
    with col_sync3:
        if st.button("🤖 Refresh AI Analysis", key=f"sync_ai_{sport_filter}", help="Regenerate AI predictions", use_container_width=True):
            with st.spinner("Regenerating AI predictions..."):
                st.cache_data.clear()
                import time
                time.sleep(0.5)
            st.success("✅ AI analysis refreshed!")
            st.rerun()
    with col_sync4:
        # Last sync indicator
        import datetime
        current_time = datetime.datetime.now().strftime("%H:%M")
        st.caption(f"🕐 {current_time}")

    st.markdown("---")

    # Auto-refresh logic
    if auto_refresh_enabled and refresh_interval:
        import time
        # Convert interval to seconds
        interval_map = {"30 sec": 30, "1 min": 60, "2 min": 120, "5 min": 300}
        interval_seconds = interval_map.get(refresh_interval, 120)

        # Use Streamlit's experimental rerun to auto-refresh
        if 'last_refresh' not in st.session_state:
            st.session_state.last_refresh = time.time()

        time_since_refresh = time.time() - st.session_state.last_refresh
        if time_since_refresh >= interval_seconds:
            st.session_state.last_refresh = time.time()
            st.cache_data.clear()
            st.rerun()

    # Fetch live ESPN data first (primary data source)
    espn_status = "❌ Failed"
    try:
        if sport_filter == 'CFB':
            # NCAA Football - use college football API
            espn = get_espn_ncaa_client()
            espn_games = espn.get_scoreboard(group='80')  # 80 = FBS
        else:
            # NFL - use NFL API
            espn = get_espn_client()
            espn_games = espn.get_scoreboard()
        espn_status = f"✅ {len(espn_games)} games fetched"
    except Exception as e:
        logger.error(f"Could not fetch ESPN data: {e}")
        espn_games = []
        st.error(f"⚠️ Could not fetch {sport_name} games from ESPN: {str(e)}")
        st.info("💡 Try: 1) Clear cache (press C) 2) Check internet connection 3) Verify ESPN API status")
        # Don't return - allow UI to still show with helpful messages

    # Enrich ESPN games with Kalshi odds
    kalshi_status = "❌ No odds"
    try:
        from src.espn_kalshi_matcher import enrich_games_with_kalshi_odds
        espn_games = enrich_games_with_kalshi_odds(espn_games)
        kalshi_matched = sum(1 for g in espn_games if g.get('kalshi_odds'))
        if kalshi_matched > 0:
            logger.info(f"Matched {kalshi_matched}/{len(espn_games)} ESPN games with Kalshi odds")
            kalshi_status = f"✅ {kalshi_matched}/{len(espn_games)} games with odds"
        else:
            kalshi_status = f"⚠️ 0/{len(espn_games)} games matched"
    except Exception as e:
        logger.warning(f"Could not enrich with Kalshi odds: {e}")
        kalshi_status = f"❌ Error: {str(e)[:50]}"

    # Display sync status
    col_status1, col_status2, col_status3 = st.columns(3)
    with col_status1:
        st.info(f"**ESPN Status:** {espn_status}")
    with col_status2:
        st.info(f"**Kalshi Status:** {kalshi_status}")
    with col_status3:
        ai_status = "✅ Active" if llm_service else "⚠️ Local only"
        st.info(f"**AI Status:** {ai_status}")

    # Show help if Kalshi data is missing
    if kalshi_matched == 0:
        with st.expander("💡 How to sync Kalshi odds", expanded=False):
            st.markdown("""
            **To get Kalshi betting odds, run one of these scripts:**

            1. **Quick Sync (NFL only):**
               ```bash
               python sync_kalshi_team_winners.py
               ```

            2. **Complete Sync (All markets):**
               ```bash
               python sync_kalshi_complete.py
               ```

            3. **Real-time Sync (Keep running):**
               ```bash
               python sync_kalshi_prices_realtime.py
               ```

            Make sure your Kalshi credentials are set in `.env` file:
            ```
            KALSHI_EMAIL=your@email.com
            KALSHI_PASSWORD=your_password
            ```
            """)

            if st.button("🔧 Open Kalshi Setup Guide", key=f"kalshi_setup_{sport_filter}"):
                st.info("Check KALSHI_SETUP_GUIDE.md for detailed setup instructions")

    # Check if games exist
    if not espn_games:
        st.warning(f"No live {sport_name} games available at this time")
        return

    # Calculate live count for display in pagination
    live_count = sum(1 for g in espn_games if g.get('is_live', False))

    # ==================== WATCH LIST SIDEBAR ====================
    watchlist = watchlist_manager.get_user_watchlist(st.session_state.user_id)

    if watchlist and not st.session_state.watch_sidebar_collapsed:
        with st.sidebar:
            st.markdown("### 📍 Your Watch List")

            for watch_game in watchlist:
                game_id = watch_game.get('game_id', '')
                game_data = watch_game.get('game_data', {})
                selected_team = watch_game.get('selected_team', '')

                away_team = game_data.get('away_team', 'Away')
                home_team = game_data.get('home_team', 'Home')
                away_score = game_data.get('away_score', 0)
                home_score = game_data.get('home_score', 0)
                status = game_data.get('status_detail', 'Scheduled')
                is_live = game_data.get('is_live', False)

                # Highlight selected team
                team_display = f"**{selected_team}**" if selected_team else f"{away_team} @ {home_team}"

                col_watch1, col_watch2 = st.columns([4, 1])
                with col_watch1:
                    if is_live:
                        st.markdown(f'<span class="live-indicator"></span>{team_display}', unsafe_allow_html=True)
                        st.caption(f"{away_score} - {home_score} • {status}")
                    else:
                        st.markdown(team_display)
                        st.caption(status)

                with col_watch2:
                    if st.button("✖", key=f"unwatch_{game_id}", help="Remove from watch list"):
                        watchlist_manager.remove_game_from_watchlist(st.session_state.user_id, game_id)
                        st.rerun()

    # ==================== DISPLAY ESPN LIVE GAMES ====================
    display_espn_live_games(
        espn_games,
        sport_name,
        sport_filter,
        watchlist_manager,
        cards_per_row,
        llm_service,
        live_count,
        filter_settings={
            'sort_by': sort_by,
            'filter_status': filter_status,
            'odds_filter': odds_filter,
            'min_opportunity': min_opportunity,
            'hide_final': hide_final
        }
    )


@st.cache_data(ttl=300, show_spinner=False)
def get_sports_prediction_cached(game_id, sport_filter, home_team, away_team, game_date_str=None):
    """
    Get prediction from sport-specific AI agents (NFL or NCAA).
    Uses cached Elo-based predictions with sport-specific features.

    Returns:
        dict: Prediction with winner, probability, confidence, spread, etc.
    """
    try:
        # Parse game date if provided
        game_date = None
        if game_date_str:
            try:
                from dateutil import parser
                game_date = parser.parse(game_date_str)
            except:
                pass

        # Get appropriate predictor
        if sport_filter == 'NFL':
            predictor = st.session_state.get('nfl_predictor')
        else:  # CFB / NCAA
            predictor = st.session_state.get('ncaa_predictor')

        if not predictor:
            return None

        # Get prediction
        prediction = predictor.predict_winner(
            home_team=home_team,
            away_team=away_team,
            game_date=game_date
        )

        return prediction

    except Exception as e:
        logger.warning(f"Sports prediction error for {home_team} vs {away_team}: {e}")
        return None


@st.cache_data(ttl=300, show_spinner=False)
def get_ai_predictions_cached(game_id, away_team, home_team, away_score, home_score, kalshi_odds_str):
    """Cached AI predictions to avoid redundant calls"""
    try:
        from src.advanced_betting_ai_agent import AdvancedBettingAIAgent
        ai_agent = AdvancedBettingAIAgent()

        # Reconstruct game and market data from hashable parameters
        game = {
            'game_id': game_id,
            'away_team': away_team,
            'home_team': home_team,
            'away_score': away_score,
            'home_score': home_score
        }

        import json
        kalshi_odds = json.loads(kalshi_odds_str) if kalshi_odds_str else {}

        ai_pred = ai_agent.analyze_betting_opportunity(game, kalshi_odds)
        return ai_pred
    except:
        return {
            'expected_value': 0,
            'confidence_score': 0,
            'recommendation': 'PASS',
            'predicted_winner': 'away',
            'win_probability': 0.5
        }


def display_espn_live_games(espn_games, sport_name, sport_filter, watchlist_manager, cards_per_row=4, llm_service=None, live_count=0, filter_settings=None):
    """Display ESPN live games in a compact visual grid format"""
    from src.nfl_team_database import NFL_LOGOS, get_team_logo_url as get_nfl_logo
    from src.ncaa_team_database import get_team_logo_url as get_ncaa_logo
    import json

    if not espn_games:
        st.warning(f"No live {sport_name} games available from ESPN at this time")
        return

    # OPTIMIZATION: Skip heavy AI analysis for initial filtering
    # Just use basic game data for filtering, AI will be loaded per-card on-demand
    games_with_ev = []
    for game in espn_games:
        # Set defaults for sorting (will be computed on-demand per card)
        game['expected_value'] = 0
        game['confidence'] = 0
        game['recommendation'] = 'PASS'
        games_with_ev.append(game)

    # Filter games by status
    filtered_games = games_with_ev
    if filter_settings:
        filter_status = filter_settings.get('filter_status', 'All Games')
        hide_final = filter_settings.get('hide_final', False)

        if filter_status == "Live Only":
            filtered_games = [g for g in games_with_ev if g.get('is_live', False)]
        elif filter_status == "Upcoming":
            filtered_games = [g for g in games_with_ev if not g.get('is_live', False) and not g.get('is_completed', False)]
        elif filter_status == "Final":
            filtered_games = [g for g in games_with_ev if g.get('is_completed', False)]

        # Apply "Hide Final Games" checkbox filter
        if hide_final:
            filtered_games = [g for g in filtered_games if not g.get('is_completed', False)]

        # Apply money-making filters (simplified - no AI required for initial filter)
        odds_filter = filter_settings.get('odds_filter', 'All Games')

        # NOTE: AI-based filters disabled for performance - games will show all, sorted by time
        # AI predictions load on-demand per card for better performance

        # Apply sorting (simplified for performance)
        sort_by = filter_settings.get('sort_by', '🔴 Live First')
        if sort_by == "⏰ Game Time":
            filtered_games.sort(key=lambda x: x.get('game_time') or datetime.max)
        elif sort_by == "🎯 Best Odds":
            # Sort by Kalshi odds (no AI needed)
            filtered_games.sort(key=lambda x: min(
                x.get('kalshi_odds', {}).get('away_win_price', 1) * 100 if x.get('kalshi_odds') else 100,
                x.get('kalshi_odds', {}).get('home_win_price', 1) * 100 if x.get('kalshi_odds') else 100
            ))
        else:
            # Default: Show live games first, then upcoming, then completed
            live_games = [g for g in filtered_games if g.get('is_live', False)]
            upcoming_games = [g for g in filtered_games if not g.get('is_live', False) and not g.get('is_completed', False)]
            completed_games = [g for g in filtered_games if g.get('is_completed', False)]
            filtered_games = live_games + upcoming_games + completed_games

    if not filtered_games:
        st.info(f"No games match your filters at this time")
        return

    # PAGINATION: Limit initial display for performance
    games_per_page = 12  # Show 12 games initially (3 rows of 4)
    total_games = len(filtered_games)

    # Initialize pagination state (sport-specific)
    page_key = f'games_page_{sport_filter}'
    if page_key not in st.session_state:
        st.session_state[page_key] = 0

    start_idx = st.session_state[page_key] * games_per_page
    end_idx = min(start_idx + games_per_page, total_games)
    paginated_games = filtered_games[start_idx:end_idx]

    # Show pagination info - all in one line
    col_count, col_nav, col_refresh = st.columns([3, 4, 2])
    with col_count:
        st.markdown(f"**{sport_name}** • Showing {start_idx + 1}-{end_idx} of {total_games} games • Live Now: {live_count}")
    with col_nav:
        if total_games > games_per_page:
            col_prev, col_next = st.columns(2)
            with col_prev:
                if st.button("⬅️ Previous", disabled=st.session_state[page_key] == 0, key=f"prev_{sport_filter}"):
                    st.session_state[page_key] -= 1
                    st.rerun()
            with col_next:
                if st.button("Next ➡️", disabled=end_idx >= total_games, key=f"next_{sport_filter}"):
                    st.session_state[page_key] += 1
                    st.rerun()
    with col_refresh:
        if st.button("🔄 Refresh", key=f"refresh_{sport_filter}"):
            st.cache_data.clear()
            st.rerun()

    # Display in grid (dynamic columns based on user selection)
    for i in range(0, len(paginated_games), cards_per_row):
        cols = st.columns(cards_per_row)

        for col_idx, game in enumerate(paginated_games[i:i+cards_per_row]):
            with cols[col_idx]:
                display_espn_game_card(game, sport_filter, watchlist_manager, llm_service)


def display_espn_game_card(game, sport_filter, watchlist_manager, llm_service=None):
    """Display a single ESPN game as a compact card with AI prediction"""
    from src.nfl_team_database import get_team_logo_url as get_nfl_logo
    from src.ncaa_team_database import get_team_logo_url as get_ncaa_logo
    from src.advanced_betting_ai_agent import AdvancedBettingAIAgent

    away_team = game.get('away_team', '')
    home_team = game.get('home_team', '')
    away_score = game.get('away_score', 0)
    home_score = game.get('home_score', 0)
    status = game.get('status_detail', 'Scheduled')
    is_live = game.get('is_live', False)
    is_completed = game.get('is_completed', False)

    # Get game ID
    game_id = game.get('game_id', '')
    if game_id:
        game_id = str(game_id)
    else:
        game_time = game.get('game_time', '').replace(' ', '_').replace(':', '')
        game_id = f"{sport_filter}_{away_team}_{home_team}_{game_time}"

    # Create unique key for Streamlit widgets
    unique_key = f"{sport_filter}_{away_team}_{home_team}_{game_id}".replace(' ', '_').replace('@', 'at')

    # Get team logos
    if sport_filter == 'CFB':
        away_logo = get_ncaa_logo(away_team)
        home_logo = get_ncaa_logo(home_team)
        # Get rankings for NCAA
        away_rank = game.get('away_rank')
        home_rank = game.get('home_rank')
    else:
        away_logo = get_nfl_logo(away_team)
        home_logo = get_nfl_logo(home_team)
        away_rank = None
        home_rank = None

    # Get user ID from session state
    user_id = st.session_state.get('user_id', 'default_user')

    # Check if game is in watchlist
    is_watched = watchlist_manager.is_game_watched(user_id, game_id) if game_id else False

    # ==================== CARD CONTAINER WITH BORDER ====================
    st.markdown('<div class="game-card">', unsafe_allow_html=True)
    with st.container():
        # Compact top row: Status + Quick Telegram Subscribe
        col_status, col_quick_tg = st.columns([2.5, 1])
        with col_status:
            if is_live:
                st.markdown(f'<span class="live-indicator"></span><strong style="font-size:13px;">LIVE • {status}</strong>', unsafe_allow_html=True)
            elif is_completed:
                st.markdown(f"<strong style='font-size:13px;'>FINAL • {status}</strong>", unsafe_allow_html=True)
            else:
                st.markdown(f"<strong style='font-size:13px;'>{status}</strong>", unsafe_allow_html=True)
        with col_quick_tg:
            # Subscribe button - gray text that turns green when subscribed
            button_label = "Subscribe" if not is_watched else "Subscribed"
            button_key = f"subscribe_{unique_key}"

            # Custom CSS for neutral gray/green subscribe button
            btn_bg_color = '#4CAF50' if is_watched else '#6c757d'
            btn_hover_color = '#45a049' if is_watched else '#5a6268'

            st.markdown(f"""
                <style>
                button[kind="secondary"].subscribe-btn {{
                    background-color: {btn_bg_color} !important;
                    color: white !important;
                    font-size: 11px !important;
                    font-weight: 500 !important;
                    padding: 6px 12px !important;
                    border: none !important;
                    border-radius: 4px !important;
                    transition: all 0.3s ease !important;
                }}
                button[kind="secondary"].subscribe-btn:hover {{
                    background-color: {btn_hover_color} !important;
                    transform: scale(1.03);
                }}
                </style>
            """, unsafe_allow_html=True)

            if st.button(button_label, key=button_key, use_container_width=True, help="Subscribe for live game updates"):
                if not is_watched:
                    watchlist_manager.add_game_to_watchlist(user_id, game, selected_team=None)
                    try:
                        from src.telegram_notifier import TelegramNotifier
                        notifier = TelegramNotifier()
                        message = f"🏈 Subscribed: {away_team} @ {home_team}\nYou'll get live updates via Telegram!"
                        notifier.send_message(message)
                    except: pass
                    st.rerun()

        # Get sports-specific AI prediction FIRST (for visual highlighting)
        game_date_str = game.get('game_time', '')
        sports_prediction = get_sports_prediction_cached(
            game_id=str(game_id),
            sport_filter=sport_filter,
            home_team=home_team,
            away_team=away_team,
            game_date_str=game_date_str if game_date_str else None
        )

        # Determine predicted winner and confidence
        if sports_prediction:
            predicted_winner = sports_prediction.get('winner', '')
            win_probability = sports_prediction.get('probability', 0.5)
            confidence_level = sports_prediction.get('confidence', 'low')  # 'high', 'medium', 'low'
            predicted_spread = sports_prediction.get('spread', 0)
        else:
            predicted_winner = ''
            win_probability = 0.5
            confidence_level = 'low'
            predicted_spread = 0

        # Determine CSS class for visual highlighting
        if confidence_level == 'high':
            highlight_class = 'team-logo-high-confidence'
            confidence_emoji = '🟢'
            confidence_text = 'HIGH CONFIDENCE'
        elif confidence_level == 'medium':
            highlight_class = 'team-logo-medium-confidence'
            confidence_emoji = '🟡'
            confidence_text = 'MEDIUM CONFIDENCE'
        else:
            highlight_class = 'team-logo-low-confidence'
            confidence_emoji = '⚪'
            confidence_text = 'Low Confidence'

        # Get Kalshi odds
        kalshi_odds = game.get('kalshi_odds', {})
        away_odds = kalshi_odds.get('away_win_price', 0) * 100 if kalshi_odds else 0
        home_odds = kalshi_odds.get('home_win_price', 0) * 100 if kalshi_odds else 0

        # Team matchup with logos and scores - WITH GLOWING TOP BAR

        # Determine CSS class for winner column
        is_away_winner = (predicted_winner == away_team)
        is_home_winner = (predicted_winner == home_team)

        if confidence_level == 'high':
            winner_col_class = 'winner-column-high'
        elif confidence_level == 'medium':
            winner_col_class = 'winner-column-medium'
        else:
            winner_col_class = 'winner-column-low'

        # Start columns with glowing top bar for predicted winner
        st.markdown('<div style="display: flex; align-items: flex-start; gap: 8px;">', unsafe_allow_html=True)

        # Away team column
        if is_away_winner and confidence_level != 'low':
            st.markdown(f'<div class="{winner_col_class}" style="flex: 2; text-align: center;">', unsafe_allow_html=True)
        else:
            st.markdown('<div style="flex: 2; text-align: center; padding-top: 8px;">', unsafe_allow_html=True)

        if away_logo:
            st.image(away_logo, width=70)
        rank_display = f"#{away_rank} " if away_rank and away_rank <= 25 else ""
        st.markdown(f"**{rank_display}{away_team[:20]}**")
        if is_away_winner and sports_prediction:
            st.markdown(f"{confidence_emoji} **{int(win_probability * 100)}%**")
        st.markdown(f"<h2 style='margin:0; font-weight:bold;'>{away_score}</h2>", unsafe_allow_html=True)
        if away_odds > 0:
            st.markdown(f"<p style='font-size:18px; font-weight:bold; color:#4CAF50; margin:0;'>{away_odds:.0f}¢</p>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # VS column
        st.markdown('<div style="flex: 1; text-align: center; padding-top: 43px;"><p style="font-size:18px;">@</p></div>', unsafe_allow_html=True)

        # Home team column
        if is_home_winner and confidence_level != 'low':
            st.markdown(f'<div class="{winner_col_class}" style="flex: 2; text-align: center;">', unsafe_allow_html=True)
        else:
            st.markdown('<div style="flex: 2; text-align: center; padding-top: 8px;">', unsafe_allow_html=True)

        if home_logo:
            st.image(home_logo, width=70)
        rank_display = f"#{home_rank} " if home_rank and home_rank <= 25 else ""
        st.markdown(f"**{rank_display}{home_team[:20]}**")
        if is_home_winner and sports_prediction:
            st.markdown(f"{confidence_emoji} **{int(win_probability * 100)}%**")
        st.markdown(f"<h2 style='margin:0; font-weight:bold;'>{home_score}</h2>", unsafe_allow_html=True)
        if home_odds > 0:
            st.markdown(f"<p style='font-size:18px; font-weight:bold; color:#4CAF50; margin:0;'>{home_odds:.0f}¢</p>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)  # Close flex container

        # Get AI prediction (CACHED for performance)
        try:
            import json
            kalshi_odds = game.get('kalshi_odds', {})
            kalshi_odds_str = json.dumps(kalshi_odds) if kalshi_odds else ""

            ai_prediction = get_ai_predictions_cached(
                game_id=str(game_id),
                away_team=away_team,
                home_team=home_team,
                away_score=away_score,
                home_score=home_score,
                kalshi_odds_str=kalshi_odds_str
            )
        except:
            ai_prediction = {
                'predicted_winner': 'home' if home_score > away_score else 'away',
                'win_probability': 0.5,
                'confidence_score': 0,
                'expected_value': 0,
                'recommendation': 'PASS'
            }

        # Display ENHANCED AI prediction with sports-specific analysis
        st.markdown("<p style='font-size:15px; font-weight:600; margin:8px 0 4px 0;'>🤖 AI Prediction</p>", unsafe_allow_html=True)

        if sports_prediction:
            # Show prediction from sport-specific agent (NFL/NCAA) with styled badge
            if confidence_level == 'high':
                badge_class = 'confidence-high'
            elif confidence_level == 'medium':
                badge_class = 'confidence-medium'
            else:
                badge_class = 'confidence-low'

            st.markdown(f'<div class="confidence-badge {badge_class}">{confidence_emoji} {confidence_text}</div>', unsafe_allow_html=True)

            # Show key prediction details
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    "Predicted Winner",
                    predicted_winner[:15],
                    help="AI predicted winner using Elo ratings and advanced stats"
                )
            with col2:
                st.metric(
                    "Win Probability",
                    f"{int(win_probability * 100)}%",
                    help="Likelihood of predicted outcome"
                )
            with col3:
                st.metric(
                    "Predicted Spread",
                    f"{abs(predicted_spread):.1f}" if predicted_spread != 0 else "-",
                    help="Expected point difference"
                )

            # Show detailed explanation in expandable section
            explanation = sports_prediction.get('explanation', '')
            if explanation:
                with st.expander("📊 Why this prediction?"):
                    st.markdown(explanation)

                    # Show key features
                    features = sports_prediction.get('features', {})
                    adjustments = sports_prediction.get('adjustments', {})

                    if features:
                        st.markdown("**Key Factors:**")

                        if sport_filter == 'NFL':
                            # NFL-specific features
                            st.markdown(f"- **Elo Ratings:** {home_team} ({features.get('home_elo', 0):.0f}) vs {away_team} ({features.get('away_elo', 0):.0f})")
                            st.markdown(f"- **Home Field:** +{features.get('home_field_advantage', 0):.1f} pts")

                            if features.get('is_divisional') == 1.0:
                                st.markdown("- **🔥 Divisional Rivalry** (typically more competitive)")

                            if adjustments.get('injury_impact', 0) != 0:
                                injury_text = "favors home" if adjustments['injury_impact'] > 0 else "favors away"
                                st.markdown(f"- **Injury Impact:** {injury_text}")

                        else:  # NCAA
                            # NCAA-specific features
                            st.markdown(f"- **Elo Ratings:** {home_team} ({features.get('home_elo', 0):.0f}) vs {away_team} ({features.get('away_elo', 0):.0f})")
                            st.markdown(f"- **Conference Power:** {home_team} ({features.get('home_conf_power', 0):.2f}) vs {away_team} ({features.get('away_conf_power', 0):.2f})")
                            st.markdown(f"- **Recruiting:** {home_team} ({features.get('home_recruiting', 0):.0f}/100) vs {away_team} ({features.get('away_recruiting', 0):.0f}/100)")

                            if features.get('is_rivalry') == 1.0:
                                st.markdown("- **🔥 RIVALRY GAME** (expect closer contest)")

                            if adjustments.get('crowd_size', 0) > 80000:
                                st.markdown(f"- **Massive Home Crowd:** {adjustments['crowd_size']:,} fans")
        else:
            # Fallback: Show traditional AI analysis if sports prediction unavailable
            st.caption("⚠️ Sports-specific prediction unavailable. Using fallback analysis.")

            # Get traditional AI prediction
            predicted_winner_fallback = ai_prediction.get('predicted_winner', 'away')
            win_prob_fallback = ai_prediction.get('win_probability', 0.5)
            confidence_fallback = ai_prediction.get('confidence_score', 0)
            ev = ai_prediction.get('expected_value', 0)
            recommendation = ai_prediction.get('recommendation', 'PASS')

            winner_name = away_team if predicted_winner_fallback == 'away' else home_team

            # Display fallback prediction
            display_win_prob = win_prob_fallback if win_prob_fallback > 1 else win_prob_fallback * 100
            display_confidence = confidence_fallback if confidence_fallback > 1 else confidence_fallback * 100

            # Recommendation
            if recommendation == 'STRONG_BUY':
                st.success("🚀 **STRONG BUY** - High confidence opportunity")
            elif recommendation == 'BUY':
                st.info("💰 **BUY** - Good betting value")
            else:
                st.info("⏸️ **PASS** - No strong value detected")

            # Metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Predicted", winner_name[:12])
            with col2:
                st.metric("Win Prob", f"{display_win_prob:.1f}%")
            with col3:
                st.metric("EV", f"{ev:.1f}%")

        # Unsubscribe button (only if subscribed)
        if is_watched:
            if st.button("🗑️ Unsubscribe", key=f"unsub_{unique_key}", use_container_width=True):
                watchlist_manager.remove_game_from_watchlist(user_id, game_id)
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)  # Close game-card div
    # Removed horizontal separator to save space


# Helper functions
def calculate_expected_value(game):
    """
    Calculate Expected Value (EV) for a game
    EV = (Win Probability × Payout) - (Loss Probability × Stake)
    """
    confidence = game.get('confidence', 50) / 100
    yes_price = game.get('yes_price', 0.5)
    no_price = game.get('no_price', 0.5)

    if game.get('predicted', '').upper() == 'YES':
        bet_price = yes_price
    else:
        bet_price = no_price

    if bet_price == 0 or bet_price == 1:
        return 0

    stake = 100
    payout = stake * (1 / bet_price - 1)
    ev = (confidence * payout) - ((1 - confidence) * stake)

    return (ev / stake) * 100


def fetch_games_grouped(db, min_confidence=70, sport='NFL'):
    """Fetch games from Kalshi database (fallback)"""
    try:
        conn = db.get_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        query = """
            SELECT *
            FROM kalshi_markets
            WHERE status = 'active'
            AND ticker LIKE %s
            ORDER BY close_time ASC
        """

        cur.execute(query, (f'%{sport}%',))
        markets = cur.fetchall()
        cur.close()
        conn.close()

        return markets
    except Exception as e:
        logger.error(f"Error fetching Kalshi markets: {e}")
        return []


def find_matching_live_game(market, live_scores):
    """Match Kalshi market to live ESPN game"""
    # Simple team name matching
    market_title = market.get('title', '').lower()

    for game_id, game in live_scores.items():
        away = game.get('away_team', '').lower()
        home = game.get('home_team', '').lower()

        if away in market_title and home in market_title:
            return game

    return None


if __name__ == "__main__":
    show_game_cards()
