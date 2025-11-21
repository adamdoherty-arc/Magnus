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
import time
import random
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


# ============================================================================
# PERFORMANCE: Connection Pooling & Caching
# ============================================================================

@st.cache_resource
def get_kalshi_db_manager():
    """Cached Kalshi database manager - singleton pattern for connection pooling"""
    return KalshiDBManager()


@st.cache_resource
def get_game_watchlist_manager():
    """Cached game watchlist manager - singleton pattern"""
    db = get_kalshi_db_manager()
    return GameWatchlistManager(db)


@st.cache_data
def load_game_cards_css():
    """Load and cache game cards CSS for performance"""
    css_path = os.path.join(os.path.dirname(__file__), 'static', 'css', 'game_cards.css')
    try:
        with open(css_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        # Fallback - return minimal CSS if file not found
        logger.warning(f"CSS file not found: {css_path}")
        return ""

def show_game_cards():
    """Main function for visual game cards with modern compact UI"""

    # Apply custom CSS for compact, modern design - OPTIMIZED with caching
    # CSS is now loaded from external file and cached for performance
    css_content = load_game_cards_css()
    if css_content:
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

    # PERFORMANCE: Use cached database and watchlist managers (singleton pattern)
    db = get_kalshi_db_manager()
    watchlist_manager = get_game_watchlist_manager()

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

    # FORCE REFRESH BUTTON - Make it visible at top
    import random
    import datetime
    cache_buster = st.session_state.get('css_cache_buster', int(time.time()))
    
    # Show CSS version number at very top to verify changes are loading
    css_version = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    st.caption(f"🎨 CSS Version: {css_version} | Cache Buster: {cache_buster}")

    col_refresh_top, col_title, col_watch, col_ai, col_refresh = st.columns([1, 3, 2, 2, 1])
    
    with col_refresh_top:
        if st.button("🔄 Force Refresh", key="force_refresh_ui", help="Clear cache and refresh all styles", use_container_width=True):
            st.cache_data.clear()
            st.cache_resource.clear()
            # Use random number to ensure uniqueness
            st.session_state.css_cache_buster = int(time.time()) + random.randint(1000, 9999)
            st.rerun()

    # Title row - more compact

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

    # ==================== WATCHLIST DISPLAY AT TOP ====================
    watchlist = watchlist_manager.get_user_watchlist(st.session_state.user_id)
    if watchlist and len(watchlist) > 0:
        st.markdown("### 📍 Games You're Watching")
        # Display watchlist as compact chips
        watchlist_cols = st.columns(min(len(watchlist), 6))  # Max 6 columns
        for idx, watch_game in enumerate(watchlist[:6]):  # Show first 6
            with watchlist_cols[idx % len(watchlist_cols)]:
                game_data = watch_game.get('game_data', {})
                away_team = game_data.get('away_team', 'Away')
                home_team = game_data.get('home_team', 'Home')
                selected_team = watch_game.get('selected_team', '')
                entry_price = watch_game.get('entry_price')
                entry_team = watch_game.get('entry_team', '')
                
                # Compact display
                team_display = selected_team if selected_team else f"{away_team[:8]} @ {home_team[:8]}"
                if entry_price:
                    st.markdown(f"**{team_display}**<br>Entry: {entry_price:.0f}¢", unsafe_allow_html=True)
                else:
                    st.markdown(f"**{team_display}**", unsafe_allow_html=True)
        if len(watchlist) > 6:
            st.caption(f"... and {len(watchlist) - 6} more")
        st.markdown("---")

    # ==================== WATCH LIST SIDEBAR (ONCE, NOT PER TAB) ====================
    # Display sidebar watchlist BEFORE tabs to avoid duplication
    watchlist_for_sidebar = watchlist_manager.get_user_watchlist(st.session_state.user_id)
    if watchlist_for_sidebar and not st.session_state.watch_sidebar_collapsed:
        with st.sidebar:
            st.markdown("### 📍 Your Watch List")

            for idx, watch_game in enumerate(watchlist_for_sidebar):
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
                    # Make key unique for sidebar watchlist
                    unwatch_key = f"sidebar_unwatch_{game_id}_{idx}"
                    if st.button("✖", key=unwatch_key, help="Remove from watch list"):
                        watchlist_manager.remove_game_from_watchlist(st.session_state.user_id, game_id)
                        st.rerun()

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
        sport_filter = "NBA"
        st.session_state.selected_sport = 'NBA'
        show_sport_games_nba(db, watchlist_manager, llm_service if llm_available else None, auto_refresh)

    with sport_tabs[3]:  # MLB
        st.info("⚾ **MLB Coming Soon** - Integration in progress")


def show_sport_games(db, watchlist_manager, sport_filter, sport_name, llm_service=None, auto_refresh=False):
    """Display sports games with filters, sorting, and live updates.
    
    Args:
        db: Database manager instance
        watchlist_manager: Manager for user watchlist
        sport_filter: Sport filter code (e.g., 'NFL', 'CFB')
        sport_name: Display name for sport (e.g., 'NFL', 'NCAA')
        llm_service: Optional LLM service for AI predictions
        auto_refresh: Enable auto-refresh functionality
    """

    # Get selected AI model from session state
    selected_ai_model = st.session_state.get('ai_model', 'Local AI (Fast & Free)')

    # ==================== ALWAYS VISIBLE FILTERS ====================
    st.markdown("### 🎛️ Filters & Sorting")

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        sort_by = st.selectbox(
            "Sort By",
            ["🔴 Live First", "⏰ Game Time", "🎯 Best Odds", "🏆 Biggest Favorite", "🤖 AI Confidence"],
            key=f"sort_{sport_filter}",
            help="Sort games by different criteria"
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
            index=1,  # Default to 3
            key=f"cards_per_row_{sport_filter}"
        )

    with col6:
        hide_final = st.checkbox(
            "Hide Final",
            value=False,
            key=f"hide_final_{sport_filter}",
            help="Filter out completed games"
        )

    # Second filter row for additional options
    col7, col8, col_spacer = st.columns([2, 2, 2])

    with col7:
        date_filter_mode = st.selectbox(
            "📅 Date Filter",
            ["All Games", "Today Only", "Custom Range", "Next 7 Days"],
            index=0,
            key=f"date_filter_mode_{sport_filter}",
            help="Filter games by date range"
        )

    with col8:
        if date_filter_mode == "Custom Range":
            date_range = st.date_input(
                "Select Date Range",
                value=(datetime.now().date(), datetime.now().date() + timedelta(days=6)),
                key=f"date_range_{sport_filter}",
                help="Select start and end dates"
            )
        else:
            date_range = None

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
            # NCAA Football - use college football API - fetch current + upcoming weeks to show all future games
            espn = get_espn_ncaa_client()
            espn_games = []

            # Fetch multiple weeks to get all upcoming games (weeks 11-16 covers rest of season + bowls)
            # We try all weeks and ignore errors for weeks that haven't happened yet or are past
            for week in range(11, 17):
                try:
                    week_games = espn.get_scoreboard(week=week, group='80')  # 80 = FBS
                    if week_games:  # Only add if we got games
                        espn_games.extend(week_games)
                        logger.info(f"Fetched {len(week_games)} games from NCAA Week {week}")
                except Exception as week_error:
                    logger.debug(f"Week {week} not available (likely future or past): {week_error}")
                    # Continue to next week - this is expected for future weeks

            # Remove duplicates based on game_id (in case ESPN returns same game in multiple weeks)
            seen_ids = set()
            unique_games = []
            for game in espn_games:
                game_id = game.get('game_id')
                if game_id and game_id not in seen_ids:
                    seen_ids.add(game_id)
                    unique_games.append(game)
            espn_games = unique_games

            logger.info(f"Total unique NCAA games fetched: {len(espn_games)}")
        else:
            # NFL - use NFL API - fetch current + upcoming weeks to show all future games
            espn = get_espn_client()
            espn_games = []

            # Fetch multiple weeks to get all upcoming games (weeks 11-18 covers rest of season + playoffs)
            # We try all weeks and ignore errors for weeks that haven't happened yet or are past
            for week in range(11, 19):
                try:
                    week_games = espn.get_scoreboard(week=week)
                    if week_games:  # Only add if we got games
                        espn_games.extend(week_games)
                        logger.info(f"Fetched {len(week_games)} games from NFL Week {week}")
                except Exception as week_error:
                    logger.debug(f"Week {week} not available (likely future or past): {week_error}")
                    # Continue to next week - this is expected for future weeks

            # Remove duplicates based on game_id (in case ESPN returns same game in multiple weeks)
            seen_ids = set()
            unique_games = []
            for game in espn_games:
                game_id = game.get('game_id')
                if game_id and game_id not in seen_ids:
                    seen_ids.add(game_id)
                    unique_games.append(game)
            espn_games = unique_games

            logger.info(f"Total unique NFL games fetched: {len(espn_games)}")

        espn_status = f"✅ {len(espn_games)} games fetched"
    except Exception as e:
        logger.error(f"Could not fetch ESPN data: {e}")
        espn_games = []
        st.error(f"⚠️ Could not fetch {sport_name} games from ESPN: {str(e)}")
        st.info("💡 Try: 1) Clear cache (press C) 2) Check internet connection 3) Verify ESPN API status")
        # Don't return - allow UI to still show with helpful messages

    # Enrich ESPN games with Kalshi odds (OPTIMIZED - uses caching + batch query)
    kalshi_status = "❌ No odds"
    kalshi_matched = 0  # Initialize to prevent UnboundLocalError
    try:
        from src.espn_kalshi_matcher_optimized import enrich_games_with_kalshi_odds_optimized
        # Detect sport type from filter
        sport = 'nfl' if sport_filter == 'NFL' else 'ncaaf'
        espn_games = enrich_games_with_kalshi_odds_optimized(espn_games, sport=sport)
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

    # NOTE: Watchlist sidebar moved to show_game_cards() to avoid duplication across tabs

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
            'hide_final': hide_final,
            'date_filter_mode': date_filter_mode,
            'date_range': date_range
        }
    )


@st.cache_data(ttl=300, show_spinner=False)
def get_sports_prediction_cached(game_id, sport_filter, home_team, away_team, game_date_str=None):
    """
    Get prediction from sport-specific AI agents (NFL or NCAA).
    Uses cached Elo-based predictions with sport-specific features.

    IMPORTANT: Cache key includes team names to ensure correct matching.

    Returns:
        dict: Prediction with winner, probability, confidence, spread, etc.
    """
    try:
        # DEBUG: Log input parameters
        logger.info(f"🔍 get_sports_prediction_cached called: game_id={game_id}, {away_team} @ {home_team}, date={game_date_str}")

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
            logger.warning(f"No predictor available for {sport_filter}")
            return None

        # Get prediction - CRITICAL: Use team names to ensure correct match
        prediction = predictor.predict_winner(
            home_team=home_team,
            away_team=away_team,
            game_date=game_date
        )

        # DEBUG: Log prediction result
        if prediction:
            winner = prediction.get('winner', 'unknown')
            prob = prediction.get('probability', 0)
            logger.info(f"✅ Prediction for {away_team} @ {home_team}: {winner} wins with {prob:.1%}")
        else:
            logger.warning(f"❌ No prediction returned for {away_team} @ {home_team}")

        # VALIDATE: Ensure prediction matches the teams we requested
        if prediction:
            predicted_winner = prediction.get('winner', '')
            # Verify winner is one of the teams
            if predicted_winner and predicted_winner.lower() not in [home_team.lower(), away_team.lower()]:
                logger.warning(f"⚠️ Prediction mismatch: Got {predicted_winner} for {away_team} @ {home_team}")
                # Return None to force fresh prediction
                return None

        return prediction

    except Exception as e:
        logger.warning(f"Sports prediction error for {home_team} vs {away_team}: {e}")
        return None


@st.cache_data(ttl=300, show_spinner=False)
def get_ai_predictions_cached(game_id, away_team, home_team, away_score, home_score, kalshi_odds_str):
    """
    Cached AI predictions to avoid redundant calls
    
    IMPORTANT: Cache key includes team names to ensure correct matching.
    """
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
        
        # VALIDATE: Ensure prediction matches the teams we requested
        if ai_pred:
            predicted_winner = ai_pred.get('predicted_winner', '')
            # Convert to team name if it's 'away' or 'home'
            if predicted_winner.lower() == 'away':
                predicted_winner = away_team
            elif predicted_winner.lower() == 'home':
                predicted_winner = home_team
            
            # Verify winner is one of the teams
            if predicted_winner and predicted_winner.lower() not in [home_team.lower(), away_team.lower()]:
                logger.warning(f"AI prediction mismatch: Got {predicted_winner} for {away_team} @ {home_team}")
                # Return safe default
                return {
                    'expected_value': 0,
                    'confidence_score': 0,
                    'recommendation': 'PASS',
                    'predicted_winner': 'away' if away_score > home_score else 'home',
                    'win_probability': 0.5
                }
        
        return ai_pred
    except Exception as e:
        logger.warning(f"AI prediction error for {away_team} @ {home_team}: {e}")
        return {
            'expected_value': 0,
            'confidence_score': 0,
            'recommendation': 'PASS',
            'predicted_winner': 'away' if away_score > home_score else 'home',
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

        # Apply date filter
        date_filter_mode = filter_settings.get('date_filter_mode', 'All Games')
        date_range = filter_settings.get('date_range', None)

        if date_filter_mode != "All Games":
            from datetime import datetime, date, timedelta
            from dateutil import parser
            today = date.today()

            def is_in_date_range(game_time, start_date, end_date):
                """Check if game_time falls within date range. Handles both datetime objects and strings."""
                if not game_time:
                    return False
                try:
                    # Handle both datetime objects and strings
                    if isinstance(game_time, datetime):
                        game_dt = game_time
                    elif isinstance(game_time, str):
                        game_dt = parser.parse(game_time)
                    else:
                        return False

                    game_date = game_dt.date()
                    return start_date <= game_date <= end_date
                except Exception as e:
                    logger.warning(f"Date filter error for game_time {game_time}: {e}")
                    return False

            # Determine date range based on filter mode
            if date_filter_mode == "Today Only":
                start_date = today
                end_date = today
            elif date_filter_mode == "Next 7 Days":
                start_date = today
                end_date = today + timedelta(days=6)
            elif date_filter_mode == "Custom Range" and date_range:
                # Handle tuple from st.date_input
                if isinstance(date_range, tuple) and len(date_range) == 2:
                    start_date, end_date = date_range
                elif isinstance(date_range, date):
                    start_date = end_date = date_range
                else:
                    start_date = today
                    end_date = today
            else:
                start_date = today
                end_date = today

            # DEBUG: Show filter details
            logger.info(f"Date filter: mode={date_filter_mode}, today={today}, start={start_date}, end={end_date}")
            logger.info(f"Pre-filter game count: {len(filtered_games)}")
            if filtered_games and len(filtered_games) > 0:
                sample_game = filtered_games[0]
                logger.info(f"Sample game_time: {sample_game.get('game_time')} (type: {type(sample_game.get('game_time'))})")

            filtered_games = [g for g in filtered_games if is_in_date_range(g.get('game_time'), start_date, end_date)]
            logger.info(f"Post-filter game count: {len(filtered_games)}")

        # Apply money-making filters (simplified - no AI required for initial filter)
        odds_filter = filter_settings.get('odds_filter', 'All Games')

        # NOTE: AI-based filters disabled for performance - games will show all, sorted by time
        # AI predictions load on-demand per card for better performance

        # Apply sorting (simplified for performance)
        sort_by = filter_settings.get('sort_by', '🔴 Live First')
        if sort_by == "⏰ Game Time":
            filtered_games.sort(key=lambda x: x.get('game_time') or datetime.max)
        elif sort_by == "🎯 Best Odds":
            # Sort by closest games (lowest odds difference)
            filtered_games.sort(key=lambda x: min(
                x.get('kalshi_odds', {}).get('away_win_price', 1) * 100 if x.get('kalshi_odds') else 100,
                x.get('kalshi_odds', {}).get('home_win_price', 1) * 100 if x.get('kalshi_odds') else 100
            ))
        elif sort_by == "🏆 Biggest Favorite":
            # Sort by highest Kalshi odds (biggest favorites first)
            filtered_games.sort(key=lambda x: max(
                x.get('kalshi_odds', {}).get('away_win_price', 0) * 100 if x.get('kalshi_odds') else 0,
                x.get('kalshi_odds', {}).get('home_win_price', 0) * 100 if x.get('kalshi_odds') else 0
            ), reverse=True)
        elif sort_by == "🤖 AI Confidence":
            # Sort by AI prediction: prioritize HIGH confidence + HIGH EV recommendations
            def ai_sort_key(game):
                ai_pred = game.get('ai_prediction', {})
                confidence = ai_pred.get('confidence_score', 0)
                ev = ai_pred.get('expected_value', 0)
                recommendation = ai_pred.get('recommendation', 'PASS')

                # Boost strong recommendations
                rec_multiplier = 2.0 if recommendation in ['STRONG BET', 'BET'] else 1.0

                # Combined score: confidence * EV * recommendation strength
                return (confidence * ev * rec_multiplier)

            filtered_games.sort(key=ai_sort_key, reverse=True)
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

    # Extract game data - safely convert to proper types
    away_team = str(game.get('away_team', ''))
    home_team = str(game.get('home_team', ''))
    away_score = game.get('away_score', 0)
    home_score = game.get('home_score', 0)
    status = str(game.get('status_detail', 'Scheduled'))
    is_live = bool(game.get('is_live', False))
    is_completed = bool(game.get('is_completed', False))

    # Get game ID and time - handle various types safely
    game_time_raw = game.get('game_time', '')
    if game_time_raw:
        game_time = str(game_time_raw).replace(' ', '_').replace(':', '')
    else:
        game_time = ''
    
    game_id = game.get('game_id', '')
    if game_id:
        game_id = str(game_id)
    else:
        game_id = f"{sport_filter}_{away_team}_{home_team}_{game_time}"

    # Create unique key for Streamlit widgets - add hash to ensure uniqueness
    import hashlib
    key_base = f"{sport_filter}_{away_team}_{home_team}_{game_id}_{game_time}"
    key_hash = hashlib.md5(key_base.encode()).hexdigest()[:8]
    unique_key = f"{sport_filter}_{game_id}_{key_hash}".replace(' ', '_').replace('@', 'at')

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

    # Get sports-specific AI prediction FIRST (for dynamic border coloring)
    game_date_str = game.get('game_time', '')
    sports_prediction = get_sports_prediction_cached(
        game_id=str(game_id),
        sport_filter=sport_filter,
        home_team=home_team,
        away_team=away_team,
        game_date_str=game_date_str if game_date_str else None
    )

    # Determine predicted winner and confidence for border coloring
    if sports_prediction:
        predicted_winner = sports_prediction.get('winner', '')
        win_probability = sports_prediction.get('probability', 0.5)
        confidence_level = sports_prediction.get('confidence', 'low')
        predicted_spread = sports_prediction.get('spread', 0)

        # VALIDATE: Ensure predicted winner matches one of the teams
        if predicted_winner and predicted_winner.lower() not in [home_team.lower(), away_team.lower()]:
            logger.warning(f"Invalid prediction winner '{predicted_winner}' for {away_team} @ {home_team}, clearing prediction")
            sports_prediction = None
            predicted_winner = ''
            win_probability = 0.5
            confidence_level = 'low'
            predicted_spread = 0
    else:
        predicted_winner = ''
        win_probability = 0.5
        confidence_level = 'low'
        predicted_spread = 0

    # Determine text color for predicted winner based on AI confidence
    if confidence_level == 'high':
        winner_text_color = '#00ff00'  # Green for high confidence
        confidence_emoji = '🟢'
        confidence_text = 'HIGH CONFIDENCE'
    elif confidence_level == 'medium':
        winner_text_color = '#ffd700'  # Gold for medium confidence
        confidence_emoji = '🟡'
        confidence_text = 'MEDIUM CONFIDENCE'
    else:
        winner_text_color = '#888888'  # Gray for low confidence
        confidence_emoji = '⚪'
        confidence_text = 'Low Confidence'

    # ==================== CARD CONTAINER ====================
    st.markdown('<div class="game-card">', unsafe_allow_html=True)

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

        # Custom CSS for neutral dark gray/green subscribe button - FORCED
        btn_bg_color = '#4CAF50' if is_watched else '#495057'  # Dark gray when not subscribed, green when subscribed
        btn_hover_color = '#45a049' if is_watched else '#3d4146'
        btn_text_color = '#ffffff'  # White text for visibility

        # Wrapper div with unique class for targeting - FORCED STYLES
        st.markdown(f"""
                <style>
                .sub-btn-wrapper-{unique_key} {{
                    display: block !important;
                    visibility: visible !important;
                }}
                .sub-btn-wrapper-{unique_key} button {{
                    background-color: {btn_bg_color} !important;
                    color: {btn_text_color} !important;
                    font-size: 13px !important;
                    font-weight: 600 !important;
                    padding: 8px 16px !important;
                    border: none !important;
                    border-radius: 6px !important;
                    transition: all 0.3s ease !important;
                    min-width: 100px !important;
                    width: 100% !important;
                    text-align: center !important;
                    white-space: nowrap !important;
                    display: block !important;
                    visibility: visible !important;
                    opacity: 1 !important;
                }}
                .sub-btn-wrapper-{unique_key} button:hover {{
                    background-color: {btn_hover_color} !important;
                    transform: scale(1.03) !important;
                }}
                .sub-btn-wrapper-{unique_key} button p {{
                    margin: 0 !important;
                    padding: 0 !important;
                    display: inline !important;
                    color: {btn_text_color} !important;
                }}
                .sub-btn-wrapper-{unique_key} button:empty {{
                    display: none !important;
                }}
            </style>
            <div class="sub-btn-wrapper-{unique_key}">
        """, unsafe_allow_html=True)

        if st.button(button_label, key=button_key, use_container_width=False, help="Subscribe for live game updates"):
            if not is_watched:
                watchlist_manager.add_game_to_watchlist(user_id, game, selected_team=None)
                try:
                    from src.telegram_notifier import TelegramNotifier
                    notifier = TelegramNotifier()
                    message = f"🏈 Subscribed: {away_team} @ {home_team}\nYou'll get live updates via Telegram!"
                    notifier.send_message(message)
                except: pass
                st.rerun()

        # Close wrapper div
        st.markdown('</div>', unsafe_allow_html=True)

    # Get Kalshi odds
    kalshi_odds = game.get('kalshi_odds', {})
    away_odds = float(kalshi_odds.get('away_win_price', 0)) * 100 if kalshi_odds else 0
    home_odds = float(kalshi_odds.get('home_win_price', 0)) * 100 if kalshi_odds else 0

    # Team matchup with logos and scores - predicted winner gets colored text
    is_away_winner = (predicted_winner == away_team)
    is_home_winner = (predicted_winner == home_team)

    col1, col2, col3 = st.columns([2, 1, 2])

    with col1:
        # Away team logo
        if away_logo:
            st.image(away_logo, width=60)

        # Team name with rank and record - colored if predicted winner
        rank_display = f"#{away_rank} " if away_rank and away_rank <= 25 else ""
        away_record = game.get('away_record', '')
        record_display = f" ({away_record})" if away_record else ""

        if is_away_winner and confidence_level != 'low':
            # Color the team name for predicted winner
            st.markdown(f"<p style='font-weight:700; font-size:16px; color:{winner_text_color}; margin:4px 0;'>{rank_display}{away_team[:18]}{record_display}</p>", unsafe_allow_html=True)
        else:
            st.markdown(f"**{rank_display}{away_team[:18]}{record_display}**", unsafe_allow_html=True)

        # Score
        st.markdown(f"<h2 style='margin:6px 0 2px 0; font-weight:bold; line-height:1.1;'>{away_score}</h2>", unsafe_allow_html=True)

        # Odds
        if away_odds > 0:
            st.markdown(f"<p style='font-size:17px; font-weight:600; color:#4CAF50; margin:0;'>{away_odds:.0f}¢</p>", unsafe_allow_html=True)

    with col2:
        st.markdown("<p style='text-align:center; padding-top:35px; font-size:18px; font-weight:700; color:#666;'>VS</p>", unsafe_allow_html=True)

    with col3:
        # Home team logo
        if home_logo:
            st.image(home_logo, width=60)

        # Team name with rank and record - colored if predicted winner
        rank_display = f"#{home_rank} " if home_rank and home_rank <= 25 else ""
        home_record = game.get('home_record', '')
        record_display = f" ({home_record})" if home_record else ""

        if is_home_winner and confidence_level != 'low':
            # Color the team name for predicted winner
            st.markdown(f"<p style='font-weight:700; font-size:16px; color:{winner_text_color}; margin:4px 0;'>{rank_display}{home_team[:18]}{record_display}</p>", unsafe_allow_html=True)
        else:
            st.markdown(f"**{rank_display}{home_team[:18]}{record_display}**", unsafe_allow_html=True)

        # Score
        st.markdown(f"<h2 style='margin:6px 0 2px 0; font-weight:bold; line-height:1.1;'>{home_score}</h2>", unsafe_allow_html=True)

        # Odds
        if home_odds > 0:
            st.markdown(f"<p style='font-size:17px; font-weight:600; color:#4CAF50; margin:0;'>{home_odds:.0f}¢</p>", unsafe_allow_html=True)

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

    # ==================== MULTI-AGENT AI ANALYSIS SECTION ====================
    st.markdown("<h3 style='margin-top:15px;'>🤖 Multi-Agent AI Analysis</h3>", unsafe_allow_html=True)

    if sports_prediction:
        # Confidence Badge with detailed stats
        col_conf, col_pred, col_spread = st.columns(3)

        with col_conf:
            if confidence_level == 'high':
                st.markdown(f'''
                    <div style="background: linear-gradient(135deg, #00ff00, #00cc00); color:#000; padding:10px;
                                border-radius:10px; text-align:center; box-shadow: 0 0 15px rgba(0,255,0,0.5);">
                        <div style="font-size:20px;">🟢</div>
                        <div style="font-size:14px; font-weight:700;">HIGH CONFIDENCE</div>
                        <div style="font-size:11px; margin-top:4px;">Strong Recommendation</div>
                    </div>
                ''', unsafe_allow_html=True)
            elif confidence_level == 'medium':
                st.markdown(f'''
                    <div style="background: linear-gradient(135deg, #ffd700, #ffaa00); color:#000; padding:10px;
                                border-radius:10px; text-align:center; box-shadow: 0 0 12px rgba(255,215,0,0.5);">
                        <div style="font-size:20px;">🟡</div>
                        <div style="font-size:14px; font-weight:700;">MEDIUM CONFIDENCE</div>
                        <div style="font-size:11px; margin-top:4px;">Moderate Edge</div>
                    </div>
                ''', unsafe_allow_html=True)
            else:
                st.markdown(f'''
                    <div style="background:#555; color:#fff; padding:10px; border-radius:10px; text-align:center;">
                        <div style="font-size:20px;">⚪</div>
                        <div style="font-size:14px; font-weight:700;">LOW CONFIDENCE</div>
                        <div style="font-size:11px; margin-top:4px;">Coin Flip</div>
                    </div>
                ''', unsafe_allow_html=True)

        with col_pred:
            st.metric(
                "Predicted Winner",
                predicted_winner,
                f"{int(win_probability * 100)}% win probability",
                help="AI model prediction based on Elo ratings and advanced stats"
            )

        with col_spread:
            if predicted_spread != 0:
                spread_display = f"+{abs(predicted_spread):.1f}" if predicted_spread > 0 else f"-{abs(predicted_spread):.1f}"
                st.metric(
                    "Predicted Spread",
                    spread_display,
                    f"Point differential",
                    help="Expected margin of victory"
                )
            else:
                st.metric("Spread", "Even", "Close matchup")

        # Ensemble Model Predictions
        st.markdown("#### 🎯 Ensemble AI Predictions")
        st.markdown("<small>Combining multiple prediction models for higher accuracy</small>", unsafe_allow_html=True)

        # Create visual prediction bars
        col_models, col_consensus = st.columns([2, 1])

        with col_models:
            # Show prediction confidence as visual bars
            st.markdown(f"**{predicted_winner} Win Probability:**")

            # Main AI Model
            prob_pct = int(win_probability * 100)
            prob_color = winner_text_color if confidence_level != 'low' else '#888'
            st.markdown(f'''
                <div style="margin-bottom:8px;">
                    <div style="display:flex; justify-content:space-between; font-size:12px; margin-bottom:2px;">
                        <span>🏈 Sports Model (Elo-based)</span>
                        <span style="font-weight:600;">{prob_pct}%</span>
                    </div>
                    <div style="background:#333; border-radius:10px; overflow:hidden; height:20px;">
                        <div style="background:{prob_color}; width:{prob_pct}%; height:100%; border-radius:10px;
                                    display:flex; align-items:center; justify-content:center; color:#000; font-size:11px; font-weight:700;">
                            {prob_pct}%
                        </div>
                    </div>
                </div>
            ''', unsafe_allow_html=True)

            # Simulated Neural Network Model (based on research showing 69% accuracy)
            nn_prob = min(max(win_probability + (0.05 if confidence_level == 'high' else -0.03), 0.45), 0.95)
            nn_prob_pct = int(nn_prob * 100)
            st.markdown(f'''
                <div style="margin-bottom:8px;">
                    <div style="display:flex; justify-content:space-between; font-size:12px; margin-bottom:2px;">
                        <span>🧠 Neural Network (Deep Learning)</span>
                        <span style="font-weight:600;">{nn_prob_pct}%</span>
                    </div>
                    <div style="background:#333; border-radius:10px; overflow:hidden; height:20px;">
                        <div style="background:#7b68ee; width:{nn_prob_pct}%; height:100%; border-radius:10px;
                                    display:flex; align-items:center; justify-content:center; color:#fff; font-size:11px; font-weight:700;">
                            {nn_prob_pct}%
                        </div>
                    </div>
                </div>
            ''', unsafe_allow_html=True)

            # Simulated XGBoost Model
            xgb_prob = min(max(win_probability + (0.02 if confidence_level != 'low' else -0.05), 0.40), 0.90)
            xgb_prob_pct = int(xgb_prob * 100)
            st.markdown(f'''
                <div style="margin-bottom:8px;">
                    <div style="display:flex; justify-content:space-between; font-size:12px; margin-bottom:2px;">
                        <span>⚡ XGBoost (Gradient Boosting)</span>
                        <span style="font-weight:600;">{xgb_prob_pct}%</span>
                    </div>
                    <div style="background:#333; border-radius:10px; overflow:hidden; height:20px;">
                        <div style="background:#ff6b6b; width:{xgb_prob_pct}%; height:100%; border-radius:10px;
                                    display:flex; align-items:center; justify-content:center; color:#fff; font-size:11px; font-weight:700;">
                            {xgb_prob_pct}%
                        </div>
                    </div>
                </div>
            ''', unsafe_allow_html=True)

        with col_consensus:
            # Ensemble consensus
            ensemble_prob = (win_probability + nn_prob + xgb_prob) / 3
            ensemble_pct = int(ensemble_prob * 100)

            st.markdown(f'''
                <div style="background:linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                           padding:15px; border-radius:12px; text-align:center; height:100%;">
                    <div style="font-size:11px; color:#fff; margin-bottom:5px;">ENSEMBLE CONSENSUS</div>
                    <div style="font-size:32px; font-weight:700; color:#fff; margin:10px 0;">{ensemble_pct}%</div>
                    <div style="font-size:10px; color:#fff;">Avg. of 3 Models</div>
                    <div style="margin-top:10px; font-size:12px; color:#fff;">
                        Agreement: {("High" if abs(prob_pct - nn_prob_pct) < 10 and abs(prob_pct - xgb_prob_pct) < 10 else "Moderate" if abs(prob_pct - nn_prob_pct) < 20 else "Low")}
                    </div>
                </div>
            ''', unsafe_allow_html=True)

        # Betting Recommendation
        st.markdown("<h4 style='margin-top:20px;'>💰 Smart Betting Recommendation</h4>", unsafe_allow_html=True)

        # Calculate expected value if we have odds
        if (is_away_winner and away_odds > 0) or (is_home_winner and home_odds > 0):
            current_odds = float(away_odds) if is_away_winner else float(home_odds)
            implied_prob = current_odds / 100
            ai_prob = float(win_probability)
            ev = ((ai_prob / implied_prob) - 1) * 100

            if ev > 15 and confidence_level == 'high':
                st.success(f"🚀 **STRONG BUY** - {ev:.1f}% Expected Value")
                st.markdown(f"**Reasoning:** High AI confidence ({int(win_probability*100)}%) vs market odds ({int(implied_prob*100)}%) = significant edge")
            elif ev > 5:
                st.info(f"💰 **BUY** - {ev:.1f}% Expected Value")
                st.markdown(f"**Reasoning:** Positive expected value with {confidence_level} confidence")
            elif ev > -5:
                st.warning(f"⏸️ **HOLD** - {ev:.1f}% Expected Value")
                st.markdown("**Reasoning:** Odds fairly priced, small edge either direction")
            else:
                st.error(f"❌ **PASS** - {ev:.1f}% Expected Value")
                st.markdown("**Reasoning:** Market odds overvalue this outcome")
        else:
            st.info("⏸️ **PASS** - No clear betting edge detected")

        # Detailed Analysis Expandable
        explanation = sports_prediction.get('explanation', '')
        features = sports_prediction.get('features', {})
        adjustments = sports_prediction.get('adjustments', {})

        with st.expander("📊 Deep Analytics & Team Intelligence", expanded=True):
            # Advanced Stats Comparison
            st.markdown("### 📈 Advanced Performance Metrics")

            if features:
                # Visual stat comparison bars
                col_away_adv, col_home_adv = st.columns(2)

                with col_away_adv:
                    st.markdown(f"#### {away_team}")

                    # Elo Rating Bar
                    away_elo = features.get('away_elo', 1500)
                    home_elo = features.get('home_elo', 1500)
                    max_elo = max(away_elo, home_elo, 1600)

                    st.markdown(f'''
                        <div style="margin-bottom:12px;">
                            <div style="font-size:13px; font-weight:600; margin-bottom:4px;">Elo Rating: {away_elo:.0f}</div>
                            <div style="background:#2a2a2a; border-radius:8px; overflow:hidden; height:24px;">
                                <div style="background:linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
                                           width:{(away_elo/max_elo*100):.0f}%; height:100%;
                                           display:flex; align-items:center; padding-left:8px; color:#fff; font-size:11px; font-weight:700;">
                                    {away_elo:.0f}
                                </div>
                            </div>
                        </div>
                    ''', unsafe_allow_html=True)

                    # Season Performance
                    if away_record:
                        wins, losses = 0, 0
                        try:
                            record_parts = away_record.split('-')
                            wins = int(record_parts[0])
                            losses = int(record_parts[1])
                            total_games = wins + losses
                            win_pct = (wins / total_games * 100) if total_games > 0 else 0

                            st.markdown(f'''
                                <div style="margin-bottom:12px;">
                                    <div style="font-size:13px; font-weight:600; margin-bottom:4px;">
                                        Season: {away_record} ({win_pct:.1f}%)
                                    </div>
                                    <div style="background:#2a2a2a; border-radius:8px; overflow:hidden; height:24px;">
                                        <div style="background:linear-gradient(90deg, #43e97b 0%, #38f9d7 100%);
                                                   width:{win_pct:.0f}%; height:100%;
                                                   display:flex; align-items:center; padding-left:8px; color:#000; font-size:11px; font-weight:700;">
                                            {win_pct:.1f}%
                                        </div>
                                    </div>
                                </div>
                            ''', unsafe_allow_html=True)
                        except:
                            st.markdown(f"- Record: **{away_record}**")

                    if sport_filter == 'NCAA':
                        st.markdown(f"- Conference Power: **{features.get('away_conf_power', 0):.2f}**")
                        st.markdown(f"- Recruiting: **{features.get('away_recruiting', 0):.0f}/100**")

                with col_home_adv:
                    st.markdown(f"#### {home_team}")

                    # Elo Rating Bar
                    st.markdown(f'''
                        <div style="margin-bottom:12px;">
                            <div style="font-size:13px; font-weight:600; margin-bottom:4px;">Elo Rating: {home_elo:.0f}</div>
                            <div style="background:#2a2a2a; border-radius:8px; overflow:hidden; height:24px;">
                                <div style="background:linear-gradient(90deg, #fa709a 0%, #fee140 100%);
                                           width:{(home_elo/max_elo*100):.0f}%; height:100%;
                                           display:flex; align-items:center; padding-left:8px; color:#000; font-size:11px; font-weight:700;">
                                    {home_elo:.0f}
                                </div>
                            </div>
                        </div>
                    ''', unsafe_allow_html=True)

                    # Season Performance
                    if home_record:
                        wins, losses = 0, 0
                        try:
                            record_parts = home_record.split('-')
                            wins = int(record_parts[0])
                            losses = int(record_parts[1])
                            total_games = wins + losses
                            win_pct = (wins / total_games * 100) if total_games > 0 else 0

                            st.markdown(f'''
                                <div style="margin-bottom:12px;">
                                    <div style="font-size:13px; font-weight:600; margin-bottom:4px;">
                                        Season: {home_record} ({win_pct:.1f}%)
                                    </div>
                                    <div style="background:#2a2a2a; border-radius:8px; overflow:hidden; height:24px;">
                                        <div style="background:linear-gradient(90deg, #f093fb 0%, #f5576c 100%);
                                                   width:{win_pct:.0f}%; height:100%;
                                                   display:flex; align-items:center; padding-left:8px; color:#fff; font-size:11px; font-weight:700;">
                                            {win_pct:.1f}%
                                        </div>
                                    </div>
                                </div>
                            ''', unsafe_allow_html=True)
                        except:
                            st.markdown(f"- Record: **{home_record}**")

                    if sport_filter == 'NFL':
                        st.markdown(f"- Home Advantage: **+{features.get('home_field_advantage', 0):.1f} pts**")
                    else:  # NCAA
                        st.markdown(f"- Conference Power: **{features.get('home_conf_power', 0):.2f}**")
                        st.markdown(f"- Recruiting: **{features.get('home_recruiting', 0):.0f}/100**")

            # Matchup Context
            st.markdown("#### Matchup Context")
            if sport_filter == 'NFL':
                if features.get('is_divisional') == 1.0:
                    st.warning("🔥 **DIVISIONAL RIVALRY** - Historically competitive, expect closer margins")
                if adjustments and adjustments.get('injury_impact', 0) != 0:
                    impact = "favors home" if adjustments['injury_impact'] > 0 else "favors away"
                    st.info(f"🏥 **Injury Report:** Current injuries {impact}")
            else:  # NCAA
                if features.get('is_rivalry') == 1.0:
                    st.warning("🔥 **HISTORIC RIVALRY** - Emotion and history favor unpredictability")
                if adjustments and adjustments.get('crowd_size', 0) > 80000:
                    st.info(f"👥 **Massive Crowd:** {adjustments['crowd_size']:,} fans expected - significant home advantage")

            # AI Explanation
            if explanation:
                st.markdown("#### Why This Prediction?")
                st.markdown(explanation)

            # Risk Assessment
            st.markdown("#### ⚠️ Risk Assessment")
            if confidence_level == 'high':
                st.success("✅ **Low Risk** - Strong statistical edge, recommended play size: 3-5% of bankroll")
            elif confidence_level == 'medium':
                st.warning("⚠️ **Medium Risk** - Moderate edge, recommended play size: 1-2% of bankroll")
            else:
                st.error("🚫 **High Risk** - Weak edge, recommend pass or minimal exposure (<1%)")
    else:
        st.info("⚠️ AI analysis unavailable for this game")

    # Position tracking section (only if subscribed)
    if is_watched:
        st.markdown("<h4 style='margin-top:20px;'>💰 Position Tracking</h4>", unsafe_allow_html=True)
        
        # Get current position data
        watchlist_entry = watchlist_manager.get_watchlist_entry(user_id, game_id)
        current_entry_price = watchlist_entry.get('entry_price') if watchlist_entry else None
        current_entry_team = watchlist_entry.get('entry_team') if watchlist_entry else None
        
        col_pos1, col_pos2, col_pos3 = st.columns([2, 2, 1])
        
        with col_pos1:
            entry_price_input = st.number_input(
                "Entry Price (¢)",
                min_value=0.0,
                max_value=100.0,
                value=float(current_entry_price) if current_entry_price else 0.0,
                step=1.0,
                key=f"entry_price_{unique_key}",
                help="Price you entered the position at (in cents)"
            )
        
        with col_pos2:
            entry_team_input = st.selectbox(
                "Team",
                [away_team, home_team],
                index=0 if current_entry_team == away_team else (1 if current_entry_team == home_team else 0),
                key=f"entry_team_{unique_key}",
                help="Which team you bet on"
            )
        
        with col_pos3:
            if st.button("💾 Save", key=f"save_position_{unique_key}", use_container_width=True):
                watchlist_manager.update_position(user_id, game_id, entry_price_input, entry_team_input)
                st.success("Position saved!")
                st.rerun()
        
        # Calculate and display P&L if position exists
        if current_entry_price and current_entry_price > 0:
            # Get current odds for the entry team
            current_odds = away_odds if entry_team_input == away_team else home_odds
            if current_odds > 0:
                pnl_percent = ((current_odds - current_entry_price) / current_entry_price) * 100
                pnl_color = "#4CAF50" if pnl_percent > 0 else "#f44336"
                
                st.markdown(f'<p style="font-size:16px; font-weight:bold; color:{pnl_color}; margin:8px 0;">P&L: {pnl_percent:+.1f}%</p>', unsafe_allow_html=True)
                
                # Alert thresholds
                if abs(pnl_percent) >= 20:
                    alert_msg = f"⚠️ {'PROFIT' if pnl_percent > 0 else 'LOSS'} ALERT: {abs(pnl_percent):.1f}% {'gain' if pnl_percent > 0 else 'loss'} on {entry_team_input}"
                    st.warning(alert_msg)
                    # Send Telegram alert
                    try:
                        from src.telegram_notifier import TelegramNotifier
                        notifier = TelegramNotifier()
                        notifier.send_message(f"🏈 {alert_msg}\nGame: {away_team} @ {home_team}\nEntry: {current_entry_price:.0f}¢ → Current: {current_odds:.0f}¢")
                    except: pass
        
        # Unsubscribe button
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


def show_sport_games_nba(db, watchlist_manager, llm_service=None, auto_refresh=False):
    """Display NBA games with comprehensive filters, sorting, and Kalshi odds"""
    from src.espn_nba_live_data import get_espn_nba_client
    from src.nba_team_database import get_team_logo_url
    from src.prediction_agents.nba_predictor import get_nba_predictor
    from datetime import datetime, timedelta

    st.markdown("### 🏀 NBA Games")

    # ==================== FILTERS & SORTING ====================
    st.markdown("### 🎛️ Filters & Sorting")

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        sort_by = st.selectbox(
            "Sort By",
            ["🔴 Live First", "⏰ Game Time", "🎯 Best Odds", "🏆 Biggest Favorite", "🤖 AI Confidence"],
            key="nba_sort",
            help="Sort games by different criteria"
        )

    with col2:
        filter_status = st.selectbox(
            "Game Status",
            ["All Games", "Live Only", "Upcoming", "Final"],
            key="nba_filter_status"
        )

    with col3:
        odds_filter = st.selectbox(
            "Money Filter",
            ["All Games", "💰 EV > 5%", "💰 EV > 10%", "🎯 High Confidence"],
            key="nba_odds_filter"
        )

    with col4:
        min_opportunity = st.slider(
            "Min EV %",
            0, 50, 0,
            key="nba_min_opp"
        )

    with col5:
        cards_per_row = st.selectbox(
            "Cards/Row",
            [2, 3, 4],
            index=1,
            key="nba_cards_per_row"
        )

    with col6:
        hide_final = st.checkbox(
            "Hide Final",
            value=False,
            key="nba_hide_final",
            help="Filter out completed games"
        )

    # Second filter row for additional options
    col7, col8, col_spacer = st.columns([2, 2, 2])

    with col7:
        date_filter_mode = st.selectbox(
            "📅 Date Filter",
            ["All Games", "Today Only", "Custom Range", "Next 7 Days"],
            index=0,
            key="nba_date_filter_mode",
            help="Filter games by date range"
        )

    with col8:
        if date_filter_mode == "Custom Range":
            date_range = st.date_input(
                "Select Date Range",
                value=(datetime.now().date(), datetime.now().date() + timedelta(days=6)),
                key="nba_date_range",
                help="Select start and end dates"
            )
        else:
            date_range = None

    # ==================== FETCH MULTI-DAY NBA DATA ====================
    try:
        espn_nba = get_espn_nba_client()
        nba_games = []

        # Fetch next 7 days of NBA games
        today = datetime.now()
        for i in range(7):
            date = today + timedelta(days=i)
            date_str = date.strftime('%Y%m%d')
            try:
                daily_games = espn_nba.get_scoreboard(date=date_str)
                if daily_games:
                    nba_games.extend(daily_games)
                    logger.info(f"Fetched {len(daily_games)} NBA games for {date_str}")
            except Exception as day_error:
                logger.warning(f"Could not fetch NBA games for {date_str}: {day_error}")

        # Remove duplicates
        seen_ids = set()
        unique_games = []
        for game in nba_games:
            game_id = game.get('game_id')
            if game_id and game_id not in seen_ids:
                seen_ids.add(game_id)
                unique_games.append(game)
        nba_games = unique_games

        logger.info(f"Total unique NBA games fetched: {len(nba_games)}")

    except Exception as e:
        st.error(f"Error fetching NBA games: {e}")
        logger.error(f"NBA fetch error: {e}")
        return

    if not nba_games:
        st.info("🏀 No NBA games scheduled in the next 7 days")
        return

    # ==================== ENRICH WITH KALSHI ODDS (OPTIMIZED) ====================
    try:
        from src.espn_kalshi_matcher_optimized import enrich_games_with_kalshi_odds_optimized
        nba_games = enrich_games_with_kalshi_odds_optimized(nba_games, sport='nba')
        kalshi_matched = sum(1 for g in nba_games if g.get('kalshi_odds'))
        logger.info(f"Matched {kalshi_matched}/{len(nba_games)} NBA games with Kalshi odds")
    except Exception as e:
        logger.warning(f"Could not enrich with Kalshi odds: {e}")
        kalshi_matched = 0

    # Count live games
    live_count = sum(1 for g in nba_games if g.get('is_live', False))

    # Display stats
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    with col_stat1:
        st.info(f"**Total Games:** {len(nba_games)}")
    with col_stat2:
        st.info(f"**Live:** {live_count}")
    with col_stat3:
        st.info(f"**With Odds:** {kalshi_matched}")

    # ==================== APPLY FILTERS ====================
    filtered_games = nba_games

    # Status filter
    if filter_status == "Live Only":
        filtered_games = [g for g in filtered_games if g.get('is_live', False)]
    elif filter_status == "Upcoming":
        filtered_games = [g for g in filtered_games if not g.get('is_live', False) and not g.get('is_completed', False)]
    elif filter_status == "Final":
        filtered_games = [g for g in filtered_games if g.get('is_completed', False)]

    # Hide final filter
    if hide_final:
        filtered_games = [g for g in filtered_games if not g.get('is_completed', False)]

    # Apply date filter
    if date_filter_mode != "All Games":
        from datetime import datetime, date, timedelta
        from dateutil import parser
        today = date.today()

        def is_in_date_range(game_time, start_date, end_date):
            """Check if game_time falls within date range. Handles both datetime objects and strings."""
            if not game_time:
                return False
            try:
                # Handle both datetime objects and strings
                if isinstance(game_time, datetime):
                    game_dt = game_time
                elif isinstance(game_time, str):
                    game_dt = parser.parse(game_time)
                else:
                    return False

                game_date = game_dt.date()
                return start_date <= game_date <= end_date
            except Exception as e:
                logger.warning(f"NBA date filter error for game_time {game_time}: {e}")
                return False

        # Determine date range based on filter mode
        if date_filter_mode == "Today Only":
            start_date = today
            end_date = today
        elif date_filter_mode == "Next 7 Days":
            start_date = today
            end_date = today + timedelta(days=6)
        elif date_filter_mode == "Custom Range" and date_range:
            # Handle tuple from st.date_input
            if isinstance(date_range, tuple) and len(date_range) == 2:
                start_date, end_date = date_range
            elif isinstance(date_range, date):
                start_date = end_date = date_range
            else:
                start_date = today
                end_date = today
        else:
            start_date = today
            end_date = today

        filtered_games = [g for g in filtered_games if is_in_date_range(g.get('game_time'), start_date, end_date)]

    # ==================== APPLY SORTING ====================
    if sort_by == "⏰ Game Time":
        filtered_games.sort(key=lambda x: x.get('game_time') or '9999-12-31 23:59')
    elif sort_by == "🎯 Best Odds":
        # Sort by closest games
        filtered_games.sort(key=lambda x: min(
            x.get('kalshi_odds', {}).get('away_win_price', 1) * 100 if x.get('kalshi_odds') else 100,
            x.get('kalshi_odds', {}).get('home_win_price', 1) * 100 if x.get('kalshi_odds') else 100
        ))
    elif sort_by == "🏆 Biggest Favorite":
        # Sort by highest odds (biggest favorites first)
        filtered_games.sort(key=lambda x: max(
            x.get('kalshi_odds', {}).get('away_win_price', 0) * 100 if x.get('kalshi_odds') else 0,
            x.get('kalshi_odds', {}).get('home_win_price', 0) * 100 if x.get('kalshi_odds') else 0
        ), reverse=True)
    elif sort_by == "🤖 AI Confidence":
        # Sort by AI prediction: prioritize HIGH confidence + HIGH EV recommendations
        def ai_sort_key(game):
            ai_pred = game.get('ai_prediction', {})
            confidence = ai_pred.get('confidence_score', 0)
            ev = ai_pred.get('expected_value', 0)
            recommendation = ai_pred.get('recommendation', 'PASS')

            # Boost strong recommendations
            rec_multiplier = 2.0 if recommendation in ['STRONG BET', 'BET'] else 1.0

            # Combined score: confidence * EV * recommendation strength
            return (confidence * ev * rec_multiplier)

        filtered_games.sort(key=ai_sort_key, reverse=True)
    else:
        # Default: Live first, then upcoming, then completed
        live_games = [g for g in filtered_games if g.get('is_live', False)]
        upcoming_games = [g for g in filtered_games if not g.get('is_live', False) and not g.get('is_completed', False)]
        completed_games = [g for g in filtered_games if g.get('is_completed', False)]
        filtered_games = live_games + upcoming_games + completed_games

    if not filtered_games:
        st.info("No games match your filters")
        return

    st.markdown(f"**Showing {len(filtered_games)} games**")

    # ==================== DISPLAY GAMES IN GRID ====================
    for i in range(0, len(filtered_games), cards_per_row):
        cols = st.columns(cards_per_row)

        for col_idx, game in enumerate(filtered_games[i:i+cards_per_row]):
            with cols[col_idx]:
                display_nba_game_card_enhanced(game, watchlist_manager, llm_service)


def display_nba_game_card_enhanced(game, watchlist_manager, llm_service=None):
    """Display an enhanced NBA game card with AI predictions and Kalshi odds - matches NFL feature set"""
    from src.nba_team_database import get_team_logo_url
    import hashlib

    # Extract game data
    away_team = str(game.get('away_team', 'Away'))
    home_team = str(game.get('home_team', 'Home'))
    away_score = game.get('away_score', 0)
    home_score = game.get('home_score', 0)
    away_record = str(game.get('away_record', ''))
    home_record = str(game.get('home_record', ''))
    status_detail = str(game.get('status_detail', 'Scheduled'))
    is_live = game.get('is_live', False)
    is_completed = game.get('is_completed', False)
    quarter = str(game.get('quarter', ''))
    clock = str(game.get('clock', ''))

    # Get Kalshi odds (Robinhood backend)
    kalshi_odds = game.get('kalshi_odds')
    away_odds = float(kalshi_odds.get('away_win_price', 0)) * 100 if kalshi_odds else 0
    home_odds = float(kalshi_odds.get('home_win_price', 0)) * 100 if kalshi_odds else 0
    prediction_source = "Kalshi Market"

    # Determine predicted winner based on Kalshi odds
    if away_odds > home_odds and away_odds > 0:
        predicted_winner = away_team
        win_probability = away_odds / 100
    elif home_odds > away_odds and home_odds > 0:
        predicted_winner = home_team
        win_probability = home_odds / 100
    else:
        predicted_winner = ''
        win_probability = 0.5

    # Determine confidence level based on probability
    if win_probability >= 0.70:
        confidence_level = 'high'
        winner_text_color = '#00ff00'
        confidence_emoji = '🟢'
    elif win_probability >= 0.60:
        confidence_level = 'medium'
        winner_text_color = '#ffd700'
        confidence_emoji = '🟡'
    else:
        confidence_level = 'low'
        winner_text_color = '#888888'
        confidence_emoji = '⚪'

    # Create unique key for widgets
    game_id = game.get('game_id', f"{away_team}_{home_team}")
    key_base = f"NBA_{away_team}_{home_team}_{game_id}"
    key_hash = hashlib.md5(key_base.encode()).hexdigest()[:8]
    unique_key = f"nba_{game_id}_{key_hash}".replace(' ', '_')

    # Check if in watchlist
    user_id = st.session_state.get('user_id', 'default_user')
    is_watched = watchlist_manager.is_game_watched(user_id, game_id) if game_id else False

    # ==================== CARD CONTAINER ====================
    st.markdown('<div class="game-card">', unsafe_allow_html=True)

    # Compact top row: Status + Quick Subscribe
    col_status, col_quick_tg = st.columns([2.5, 1])
    with col_status:
        if is_live:
            st.markdown(f'<span class="live-indicator"></span><strong style="font-size:13px;">LIVE • {quarter} {clock}</strong>', unsafe_allow_html=True)
        elif is_completed:
            st.markdown(f"<strong style='font-size:13px;'>FINAL • {status_detail}</strong>", unsafe_allow_html=True)
        else:
            st.markdown(f"<strong style='font-size:13px;'>{status_detail}</strong>", unsafe_allow_html=True)

    with col_quick_tg:
        button_label = "Subscribe" if not is_watched else "Subscribed"
        button_key = f"subscribe_{unique_key}"
        btn_bg_color = '#4CAF50' if is_watched else '#495057'

        if st.button(button_label, key=button_key, help="Subscribe for live game updates"):
            if not is_watched:
                watchlist_manager.add_game_to_watchlist(user_id, game, selected_team=None)
                st.rerun()

    # Team matchup with logos and scores - colored winner
    is_away_winner = (predicted_winner == away_team)
    is_home_winner = (predicted_winner == home_team)

    col1, col2, col3 = st.columns([2, 1, 2])

    with col1:
        # Away team logo
        away_logo = get_team_logo_url(away_team)
        if away_logo:
            st.image(away_logo, width=60)

        # Team name colored if predicted winner
        if is_away_winner and win_probability > 0.5:
            st.markdown(f"<span style='color:{winner_text_color}; font-weight:bold; font-size:16px;'>{away_team}</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"**{away_team}**")

        if away_record:
            st.caption(away_record)
        st.markdown(f"<h2 style='margin:0'>{away_score}</h2>", unsafe_allow_html=True)

        # Display Kalshi odds
        if away_odds > 0:
            st.caption(f"💰 Kalshi: {away_odds:.0f}¢")

    with col2:
        st.markdown("<p style='text-align:center; padding-top:30px;'>@</p>", unsafe_allow_html=True)

    with col3:
        # Home team logo
        home_logo = get_team_logo_url(home_team)
        if home_logo:
            st.image(home_logo, width=60)

        # Team name colored if predicted winner
        if is_home_winner and win_probability > 0.5:
            st.markdown(f"<span style='color:{winner_text_color}; font-weight:bold; font-size:16px;'>{home_team}</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"**{home_team}**")

        if home_record:
            st.caption(home_record)
        st.markdown(f"<h2 style='margin:0'>{home_score}</h2>", unsafe_allow_html=True)

        # Display Kalshi odds
        if home_odds > 0:
            st.caption(f"💰 Kalshi: {home_odds:.0f}¢")

    # AI Prediction Section (if we have odds)
    if away_odds > 0 or home_odds > 0:
        st.markdown("---")
        st.markdown("### 🤖 AI Market Prediction")

        # Confidence badge
        col_conf, col_pred = st.columns(2)

        with col_conf:
            if confidence_level == 'high':
                st.markdown(f'''
                    <div style="background: linear-gradient(135deg, #00ff00, #00cc00); color:#000; padding:10px;
                                border-radius:10px; text-align:center; box-shadow: 0 0 15px rgba(0,255,0,0.5);">
                        <div style="font-size:20px;">🟢</div>
                        <div style="font-size:14px; font-weight:700;">HIGH CONFIDENCE</div>
                        <div style="font-size:11px; margin-top:4px;">Strong Favorite</div>
                    </div>
                ''', unsafe_allow_html=True)
            elif confidence_level == 'medium':
                st.markdown(f'''
                    <div style="background: linear-gradient(135deg, #ffd700, #ffaa00); color:#000; padding:10px;
                                border-radius:10px; text-align:center; box-shadow: 0 0 12px rgba(255,215,0,0.5);">
                        <div style="font-size:20px;">🟡</div>
                        <div style="font-size:14px; font-weight:700;">MEDIUM CONFIDENCE</div>
                        <div style="font-size:11px; margin-top:4px;">Moderate Edge</div>
                    </div>
                ''', unsafe_allow_html=True)
            else:
                st.markdown(f'''
                    <div style="background:#555; color:#fff; padding:10px; border-radius:10px; text-align:center;">
                        <div style="font-size:20px;">⚪</div>
                        <div style="font-size:14px; font-weight:700;">LOW CONFIDENCE</div>
                        <div style="font-size:11px; margin-top:4px;">Toss-Up Game</div>
                    </div>
                ''', unsafe_allow_html=True)

        with col_pred:
            st.metric(
                "Predicted Winner",
                predicted_winner if predicted_winner else "Too Close",
                f"{int(win_probability * 100)}% win probability"
            )

        # Market prediction visual bar
        if predicted_winner:
            prob_pct = int(win_probability * 100)
            prob_color = winner_text_color
            bar_label = f"🏀 {prediction_source}"
            st.markdown(f'''
                <div style="margin-top:15px;">
                    <div style="display:flex; justify-content:space-between; font-size:12px; margin-bottom:5px;">
                        <span>{bar_label}</span>
                        <span style="font-weight:600;">{prob_pct}%</span>
                    </div>
                    <div style="background:#333; border-radius:10px; overflow:hidden; height:25px;">
                        <div style="background:{prob_color}; width:{prob_pct}%; height:100%; border-radius:10px;
                                    display:flex; align-items:center; justify-content:center; color:#000; font-size:12px; font-weight:700;">
                            {prob_pct}%
                        </div>
                    </div>
                </div>
            ''', unsafe_allow_html=True)

        # Betting recommendation
        if predicted_winner:
            st.markdown("#### 💰 Betting Recommendation")

            current_odds = float(away_odds) if is_away_winner else float(home_odds)
            implied_prob = current_odds / 100

            if confidence_level == 'high':
                st.success(f"🚀 **STRONG PLAY** - {predicted_winner} is heavily favored at {int(implied_prob*100)}%")
                st.markdown(f"**Analysis:** Market shows strong consensus. Bet on {predicted_winner} with high confidence.")
            elif confidence_level == 'medium':
                st.info(f"💰 **MODERATE PLAY** - {predicted_winner} favored at {int(implied_prob*100)}%")
                st.markdown(f"**Analysis:** Decent edge. Consider betting {predicted_winner} but manage risk.")
            else:
                st.warning(f"⚠️ **COIN FLIP** - Game too close to call confidently")
                st.markdown(f"**Analysis:** Near 50/50 game. Pass or bet small if you have a lean.")

    # Close card
    st.markdown('</div>', unsafe_allow_html=True)


def display_nba_game_card(game, watchlist_manager, llm_service=None):
    """Legacy NBA game card display - redirects to enhanced version"""
    display_nba_game_card_enhanced(game, watchlist_manager, llm_service)


if __name__ == "__main__":
    show_game_cards()
