"""
Enhanced Prediction Markets - Comprehensive AI-Powered Sports Betting Analysis
Features: Tile-based UI, Multi-source research, AI predictions, Factor analysis
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import logging

from src.enhanced_sports_predictor import EnhancedSportsPredictor
from src.kalshi_db_manager import KalshiDBManager
# from src.nfl_data_fetcher import NFLDataFetcher  # Not needed currently

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# NFL Team Logo URLs (ESPN CDN)
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

# College Football Logos (Top 25 programs)
COLLEGE_LOGOS = {
    'Alabama': 'https://a.espncdn.com/i/teamlogos/ncaa/500/333.png',
    'Georgia': 'https://a.espncdn.com/i/teamlogos/ncaa/500/257.png',
    'Ohio State': 'https://a.espncdn.com/i/teamlogos/ncaa/500/194.png',
    'Michigan': 'https://a.espncdn.com/i/teamlogos/ncaa/500/130.png',
    'USC': 'https://a.espncdn.com/i/teamlogos/ncaa/500/30.png',
    'Texas': 'https://a.espncdn.com/i/teamlogos/ncaa/500/251.png',
    'Oklahoma': 'https://a.espncdn.com/i/teamlogos/ncaa/500/201.png',
    'Clemson': 'https://a.espncdn.com/i/teamlogos/ncaa/500/228.png',
    'LSU': 'https://a.espncdn.com/i/teamlogos/ncaa/500/99.png',
    'Oregon': 'https://a.espncdn.com/i/teamlogos/ncaa/500/2483.png',
    'Penn State': 'https://a.espncdn.com/i/teamlogos/ncaa/500/213.png',
    'Notre Dame': 'https://a.espncdn.com/i/teamlogos/ncaa/500/87.png',
    'Florida State': 'https://a.espncdn.com/i/teamlogos/ncaa/500/52.png',
    'Florida': 'https://a.espncdn.com/i/teamlogos/ncaa/500/57.png',
    'Auburn': 'https://a.espncdn.com/i/teamlogos/ncaa/500/2.png',
    'Wisconsin': 'https://a.espncdn.com/i/teamlogos/ncaa/500/275.png',
    'Iowa': 'https://a.espncdn.com/i/teamlogos/ncaa/500/2294.png',
    'Tennessee': 'https://a.espncdn.com/i/teamlogos/ncaa/500/2633.png',
    'Texas A&M': 'https://a.espncdn.com/i/teamlogos/ncaa/500/245.png',
    'Miami': 'https://a.espncdn.com/i/teamlogos/ncaa/500/2390.png',
}


def show_prediction_markets_enhanced():
    """Main enhanced prediction markets page"""

    # Page config
    st.set_page_config(page_title="Prediction Markets", layout="wide", page_icon="🎲")

    # Custom CSS for tile cards
    st.markdown("""
        <style>
        /* Game card styling */
        .game-card {
            background: white;
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            border: 2px solid #e5e7eb;
            transition: all 0.3s ease;
            cursor: pointer;
            margin-bottom: 1rem;
        }

        .game-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.15);
            border-color: #667eea;
        }

        .game-card-best {
            border: 3px solid #10b981;
            background: linear-gradient(135deg, #ffffff 0%, #d1fae5 100%);
        }

        /* Team logo styling */
        .team-logo {
            width: 80px;
            height: 80px;
            object-fit: contain;
        }

        /* Confidence badge */
        .confidence-high {
            background: #10b981;
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 700;
            font-size: 1.1rem;
        }

        .confidence-medium {
            background: #f59e0b;
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 700;
            font-size: 1.1rem;
        }

        .confidence-low {
            background: #6b7280;
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 700;
            font-size: 1.1rem;
        }

        /* Value badge */
        .value-high {
            background: #fbbf24;
            color: #000;
            padding: 4px 12px;
            border-radius: 12px;
            font-weight: 600;
            font-size: 0.85rem;
        }

        /* Winner badge */
        .winner-badge {
            background: #667eea;
            color: white;
            padding: 6px 14px;
            border-radius: 16px;
            font-weight: 700;
            font-size: 0.9rem;
        }

        /* Metric cards */
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1rem;
            border-radius: 12px;
            color: white;
            text-align: center;
        }

        .metric-value {
            font-size: 2rem;
            font-weight: 700;
        }

        .metric-label {
            font-size: 0.85rem;
            opacity: 0.9;
        }

        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 8px 8px 0 0;
            padding: 12px 24px;
            font-weight: 600;
            font-size: 1.1rem;
        }
        </style>
    """, unsafe_allow_html=True)

    # Header
    st.title("🎲 AI-Powered Sports Predictions")
    st.markdown("**Comprehensive analysis from GitHub models, expert articles, and community insights**")

    # Main tabs for NFL vs College
    tab1, tab2 = st.tabs(["🏈 NFL", "🏈 College Football"])

    with tab1:
        render_nfl_predictions()

    with tab2:
        render_college_predictions()


def render_nfl_predictions():
    """Render NFL prediction section"""

    # Controls
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

    with col1:
        st.markdown("### Filter Games")

    with col2:
        min_confidence = st.slider("Min Confidence", 0, 100, 65, key="nfl_conf")

    with col3:
        show_only_best = st.checkbox("Best Bets Only", value=False, key="nfl_best")

    with col4:
        if st.button("🔄 Refresh", type="primary", key="nfl_refresh"):
            st.cache_data.clear()
            st.rerun()

    # Fetch and predict games
    with st.spinner("🔮 Analyzing NFL games with AI..."):
        games, predictions = fetch_and_predict_nfl_games()

    if not predictions:
        st.warning("No NFL games found. Check back closer to game day!")
        st.info("💡 The system automatically pulls games from ESPN and Kalshi markets")
        return

    # Filter predictions
    filtered_predictions = [
        p for p in predictions
        if p.get('confidence', 0) >= min_confidence
    ]

    if show_only_best:
        # Show only top 25% by opportunity score
        threshold = sorted([p['opportunity_score'] for p in filtered_predictions], reverse=True)[len(filtered_predictions)//4] if filtered_predictions else 0
        filtered_predictions = [p for p in filtered_predictions if p['opportunity_score'] >= threshold]

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{len(filtered_predictions)}</div>
                <div class="metric-label">GAMES ANALYZED</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        high_conf = len([p for p in filtered_predictions if p['confidence'] >= 80])
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{high_conf}</div>
                <div class="metric-label">HIGH CONFIDENCE</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        avg_conf = sum(p['confidence'] for p in filtered_predictions) / len(filtered_predictions) if filtered_predictions else 0
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{avg_conf:.0f}%</div>
                <div class="metric-label">AVG CONFIDENCE</div>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        best_value = len([p for p in filtered_predictions if p.get('value_rating') == 'HIGH VALUE'])
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{best_value}</div>
                <div class="metric-label">HIGH VALUE BETS</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Render game cards
    st.markdown("### 🎯 Game Predictions (Best to Worst)")

    for idx, prediction in enumerate(filtered_predictions):
        render_game_card(prediction, idx, sport="nfl")


def render_college_predictions():
    """Render college football prediction section"""

    # Controls
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

    with col1:
        st.markdown("### Filter Games")

    with col2:
        min_confidence = st.slider("Min Confidence", 0, 100, 65, key="college_conf")

    with col3:
        show_only_best = st.checkbox("Best Bets Only", value=False, key="college_best")

    with col4:
        if st.button("🔄 Refresh", type="primary", key="college_refresh"):
            st.cache_data.clear()
            st.rerun()

    # Fetch and predict games
    with st.spinner("🔮 Analyzing college games with AI..."):
        games, predictions = fetch_and_predict_college_games()

    if not predictions:
        st.info("🏈 College football predictions coming soon!")
        st.markdown("""
            The system will analyze:
            - Top 25 matchups
            - Conference championship implications
            - Playoff scenarios
            - Betting value opportunities
        """)
        return

    # Filter predictions
    filtered_predictions = [
        p for p in predictions
        if p.get('confidence', 0) >= min_confidence
    ]

    if show_only_best:
        threshold = sorted([p['opportunity_score'] for p in filtered_predictions], reverse=True)[len(filtered_predictions)//4] if filtered_predictions else 0
        filtered_predictions = [p for p in filtered_predictions if p['opportunity_score'] >= threshold]

    # Summary metrics (same as NFL)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{len(filtered_predictions)}</div>
                <div class="metric-label">GAMES ANALYZED</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        high_conf = len([p for p in filtered_predictions if p['confidence'] >= 80])
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{high_conf}</div>
                <div class="metric-label">HIGH CONFIDENCE</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        avg_conf = sum(p['confidence'] for p in filtered_predictions) / len(filtered_predictions) if filtered_predictions else 0
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{avg_conf:.0f}%</div>
                <div class="metric-label">AVG CONFIDENCE</div>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        best_value = len([p for p in filtered_predictions if p.get('value_rating') == 'HIGH VALUE'])
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{best_value}</div>
                <div class="metric-label">HIGH VALUE BETS</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Render game cards
    st.markdown("### 🎯 Game Predictions (Best to Worst)")

    for idx, prediction in enumerate(filtered_predictions):
        render_game_card(prediction, idx, sport="college")


def render_game_card(prediction: Dict, index: int, sport: str = "nfl"):
    """Render a single game prediction card"""

    home_team = prediction.get('home_team', 'Unknown')
    away_team = prediction.get('away_team', 'Unknown')
    predicted_winner = prediction.get('predicted_winner', home_team)
    confidence = prediction.get('confidence', 0)
    opportunity_score = prediction.get('opportunity_score', 0)
    value_rating = prediction.get('value_rating', 'MODERATE VALUE')

    # Get team logos
    logos = TEAM_LOGOS if sport == "nfl" else COLLEGE_LOGOS
    home_logo = logos.get(home_team, 'https://via.placeholder.com/80')
    away_logo = logos.get(away_team, 'https://via.placeholder.com/80')

    # Determine card class
    is_best = value_rating == "HIGH VALUE" and confidence >= 80
    card_class = "game-card-best" if is_best else "game-card"

    # Confidence badge class
    if confidence >= 80:
        conf_class = "confidence-high"
        conf_emoji = "🔥"
    elif confidence >= 65:
        conf_class = "confidence-medium"
        conf_emoji = "✓"
    else:
        conf_class = "confidence-low"
        conf_emoji = "⚠️"

    # Create expandable game card
    with st.expander(
        f"{'⭐ ' if is_best else ''}{away_team} @ {home_team} - {conf_emoji} {confidence}% Confidence",
        expanded=(index < 3)  # Expand top 3
    ):
        # Top row: Teams and prediction
        col1, col2, col3 = st.columns([2, 1, 2])

        with col1:
            # Away team
            st.image(away_logo, width=80)
            st.markdown(f"**{away_team}**")
            away_prob = prediction.get('away_win_probability', 0)
            st.caption(f"Win Prob: {away_prob:.1%}")

        with col2:
            st.markdown(f"""
                <div style="text-align: center; padding-top: 20px;">
                    <div style="font-size: 1.5rem; font-weight: 700;">VS</div>
                    <div style="margin-top: 10px;">
                        <span class="{conf_class}">{confidence}%</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        with col3:
            # Home team
            st.image(home_logo, width=80)
            st.markdown(f"**{home_team}**")
            home_prob = prediction.get('home_win_probability', 0)
            st.caption(f"Win Prob: {home_prob:.1%}")

        st.markdown("---")

        # Prediction summary
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"""
                **🎯 PREDICTED WINNER**

                <div class="winner-badge">{predicted_winner}</div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
                **💎 VALUE RATING**

                <div class="value-high" style="{'background: #10b981; color: white;' if value_rating == 'HIGH VALUE' else ''}">{value_rating}</div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
                **📊 OPPORTUNITY SCORE**

                **{opportunity_score:.1f}/150**
            """)

        st.markdown("---")

        # AI Analysis
        st.markdown("### 🤖 AI Analysis")
        ai_analysis = prediction.get('ai_analysis', 'Analysis not available')
        st.info(ai_analysis)

        # Key Factor
        key_factor = prediction.get('key_factor', 'Multiple factors')
        st.success(f"**Key Factor:** {key_factor}")

        st.markdown("---")

        # Prediction Factors
        st.markdown("### 📊 Prediction Factors (Ranked by Weight)")

        factors = prediction.get('prediction_factors', [])
        factors_sorted = sorted(factors, key=lambda x: x.get('weight', 0), reverse=True)

        for factor in factors_sorted:
            name = factor.get('name', 'Unknown')
            weight = factor.get('weight', 0)
            description = factor.get('description', '')
            confidence_factor = factor.get('confidence', 0.5)

            # Progress bar for weight
            st.markdown(f"""
                **{name}** ({weight:.0%} weight)
                """)
            st.progress(weight)
            st.caption(f"✓ {description} (Reliability: {confidence_factor:.0%})")
            st.markdown("")

        st.markdown("---")

        # Research Sources
        st.markdown("### 🔬 Research Sources")

        research = prediction.get('research_sources', {})
        col1, col2, col3 = st.columns(3)

        with col1:
            github_count = research.get('github_models', 0)
            st.metric("GitHub Models", github_count, help="Open-source prediction models analyzed")

        with col2:
            medium_count = research.get('medium_articles', 0)
            st.metric("Expert Articles", medium_count, help="Medium articles reviewed")

        with col3:
            reddit_score = research.get('reddit_sentiment', 0)
            st.metric("Community Score", f"{reddit_score}/100", help="Reddit sentiment analysis")

        # Betting odds
        st.markdown("---")
        st.markdown("### 💰 Betting Information")

        col1, col2, col3 = st.columns(3)

        with col1:
            spread = prediction.get('spread', 'N/A')
            st.metric("Spread", spread)

        with col2:
            home_odds = prediction.get('home_odds', 'N/A')
            st.metric("Home Odds", home_odds)

        with col3:
            away_odds = prediction.get('away_odds', 'N/A')
            st.metric("Away Odds", away_odds)


@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_and_predict_nfl_games() -> Tuple[List[Dict], List[Dict]]:
    """Fetch NFL games and generate predictions"""
    try:
        # Initialize components
        db = KalshiDBManager()
        nfl_fetcher = NFLDataFetcher()
        predictor = EnhancedSportsPredictor()

        # Fetch games from multiple sources
        games = []

        # Get games from Kalshi database
        markets = db.get_active_markets(market_type='nfl')

        # Convert Kalshi markets to game format
        for market in markets:
            game_data = parse_kalshi_market_to_game(market)
            if game_data:
                games.append(game_data)

        # Get additional games from ESPN
        espn_games = nfl_fetcher.get_upcoming_games(days=7)
        for espn_game in espn_games:
            game_data = parse_espn_game(espn_game)
            if game_data and not any(g['home_team'] == game_data['home_team'] for g in games):
                games.append(game_data)

        # Generate predictions
        predictions = predictor.predict_all_games(games)

        logger.info(f"Generated {len(predictions)} NFL predictions from {len(games)} games")

        return games, predictions

    except Exception as e:
        logger.error(f"Error fetching/predicting NFL games: {e}")
        return [], []


@st.cache_data(ttl=300)
def fetch_and_predict_college_games() -> Tuple[List[Dict], List[Dict]]:
    """Fetch college football games and generate predictions"""
    try:
        # College football predictions coming soon
        return [], []

    except Exception as e:
        logger.error(f"Error fetching/predicting college games: {e}")
        return [], []


def parse_kalshi_market_to_game(market: Dict) -> Optional[Dict]:
    """Convert Kalshi market to game format"""
    try:
        title = market.get('title', '')

        # Extract teams from title (format: "Will TEAM1 beat TEAM2...")
        if 'beat' in title.lower():
            parts = title.split('beat')
            if len(parts) >= 2:
                away_team = parts[0].replace('Will', '').strip()
                home_team = parts[1].split('on')[0].strip() if 'on' in parts[1] else parts[1].strip()

                return {
                    'home_team': home_team,
                    'away_team': away_team,
                    'home_odds': float(market.get('yes_price', 0.5)) if market.get('yes_price') else None,
                    'away_odds': float(market.get('no_price', 0.5)) if market.get('no_price') else None,
                    'spread': None,
                    'over_under': None,
                    'sport': 'nfl',
                    'game_time': market.get('close_time'),
                    'source': 'kalshi'
                }

        return None

    except Exception as e:
        logger.error(f"Error parsing Kalshi market: {e}")
        return None


def parse_espn_game(espn_game: Dict) -> Optional[Dict]:
    """Convert ESPN game to standard format"""
    try:
        competitions = espn_game.get('competitions', [{}])[0]
        competitors = competitions.get('competitors', [])

        if len(competitors) >= 2:
            home = next((c for c in competitors if c.get('homeAway') == 'home'), {})
            away = next((c for c in competitors if c.get('homeAway') == 'away'), {})

            return {
                'home_team': home.get('team', {}).get('displayName', 'Unknown'),
                'away_team': away.get('team', {}).get('displayName', 'Unknown'),
                'home_odds': None,  # ESPN doesn't provide odds
                'away_odds': None,
                'spread': None,
                'over_under': None,
                'sport': 'nfl',
                'game_time': espn_game.get('date'),
                'source': 'espn'
            }

        return None

    except Exception as e:
        logger.error(f"Error parsing ESPN game: {e}")
        return None


if __name__ == "__main__":
    show_prediction_markets_enhanced()
