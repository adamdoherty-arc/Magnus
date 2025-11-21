"""
AVA Betting Recommendations Page
AI-Powered Game Analysis with Multi-Agent Ranking
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging
import json

# Import necessary modules
from src.espn_live_data import get_espn_client
from src.espn_nba_live_data import get_espn_nba_client
from src.espn_ncaa_live_data import get_espn_ncaa_client
from src.espn_kalshi_matcher_optimized import enrich_games_with_kalshi_odds_optimized as enrich_games_with_kalshi_odds, enrich_games_with_kalshi_odds_nba
from src.advanced_betting_ai_agent import AdvancedBettingAIAgent
from src.kalshi_db_manager import KalshiDBManager

# Import agent system
try:
    from src.ava.core.agent_initializer import ensure_agents_initialized, get_registry
    from src.ava.agents.sports.sports_betting_agent import SportsBettingAgent
    AGENTS_AVAILABLE = True
except ImportError:
    AGENTS_AVAILABLE = False

logger = logging.getLogger(__name__)


def calculate_expected_value(win_prob: float, odds: float) -> float:
    """Calculate expected value of a bet"""
    if not win_prob or not odds or odds >= 100:
        return 0

    # EV = (Win Probability × Payout) - (Loss Probability × Stake)
    # Payout = (100 / Odds) - 1 (since Kalshi odds are in cents)
    # Assuming $100 bet
    stake = 100
    payout = (100 / odds) * stake if odds > 0 else 0
    loss_prob = 1 - win_prob

    ev = (win_prob * payout) - (loss_prob * stake)
    return ev


def calculate_kelly_criterion(win_prob: float, odds: float) -> float:
    """Calculate Kelly Criterion bet size as % of bankroll"""
    if not win_prob or not odds or odds >= 100 or odds <= 0:
        return 0

    # Kelly % = (bp - q) / b
    # b = decimal odds - 1
    # p = win probability
    # q = loss probability (1 - p)
    decimal_odds = 100 / odds
    b = decimal_odds - 1
    p = win_prob
    q = 1 - p

    if b <= 0:
        return 0

    kelly = (b * p - q) / b

    # Use fractional Kelly for safety (1/4 Kelly)
    kelly = max(0, min(kelly * 0.25, 0.25))  # Cap at 25% of bankroll

    return kelly


@st.cache_data(ttl=300)  # Cache for 5 minutes - games don't change that fast
def analyze_all_games(days_ahead: int = 8) -> List[Dict[str, Any]]:
    """Fetch and analyze all games from NFL, NBA, and NCAA with Kalshi odds

    Args:
        days_ahead: Number of days ahead to fetch games (default 8)

    Note: Cached for 5 minutes to avoid repeated API calls
    """

    all_games = []
    today = datetime.now()
    cutoff_date = today + timedelta(days=days_ahead)

    # Fetch NFL games (only upcoming games within date range)
    try:
        espn = get_espn_client()
        nfl_games = []
        # Try current and next 2 weeks only
        current_week = 12  # Current NFL week as of Nov 17, 2025
        for week in range(current_week, current_week + 3):
            try:
                week_games = espn.get_scoreboard(week=week)
                if week_games:
                    for game in week_games:
                        game['sport'] = 'NFL'
                        # Filter by date
                        try:
                            game_time = game.get('game_time', '')
                            if game_time:
                                game_date = datetime.strptime(game_time[:10], '%Y-%m-%d')
                                if game_date <= cutoff_date:
                                    nfl_games.append(game)
                        except:
                            nfl_games.append(game)  # Include if can't parse date
            except:
                pass

        # Enrich with Kalshi odds
        nfl_games = enrich_games_with_kalshi_odds(nfl_games)
        all_games.extend(nfl_games)

        logger.info(f"Fetched {len(nfl_games)} NFL games within {days_ahead} days")
    except Exception as e:
        logger.error(f"Error fetching NFL games: {e}")

    # Fetch NCAA games (only upcoming games within date range)
    try:
        espn_ncaa = get_espn_ncaa_client()
        ncaa_games = []
        # Try current and next week only
        current_week = 12
        for week in range(current_week, current_week + 2):
            try:
                week_games = espn_ncaa.get_scoreboard(week=week)
                if week_games:
                    for game in week_games:
                        game['sport'] = 'NCAA'
                        # Filter by date
                        try:
                            game_time = game.get('game_time', '')
                            if game_time:
                                game_date = datetime.strptime(game_time[:10], '%Y-%m-%d')
                                if game_date <= cutoff_date:
                                    ncaa_games.append(game)
                        except:
                            ncaa_games.append(game)  # Include if can't parse date
            except:
                pass

        # Enrich with Kalshi odds (NCAA uses same function as NFL)
        ncaa_games = enrich_games_with_kalshi_odds(ncaa_games)
        all_games.extend(ncaa_games)

        logger.info(f"Fetched {len(ncaa_games)} NCAA games within {days_ahead} days")
    except Exception as e:
        logger.error(f"Error fetching NCAA games: {e}")

    # Fetch NBA games (within date range)
    try:
        espn_nba = get_espn_nba_client()
        nba_games = []
        for i in range(min(days_ahead, 14)):  # Cap at 14 days
            date = today + timedelta(days=i)
            date_str = date.strftime('%Y%m%d')
            try:
                daily_games = espn_nba.get_scoreboard(date=date_str)
                if daily_games:
                    for game in daily_games:
                        game['sport'] = 'NBA'
                    nba_games.extend(daily_games)
            except:
                pass

        # Enrich with Kalshi odds
        nba_games = enrich_games_with_kalshi_odds_nba(nba_games)
        all_games.extend(nba_games)

        logger.info(f"Fetched {len(nba_games)} NBA games within {days_ahead} days")
    except Exception as e:
        logger.error(f"Error fetching NBA games: {e}")

    return all_games


def analyze_betting_opportunity(game: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze a single game for betting opportunity using AI analysis"""

    kalshi_odds = game.get('kalshi_odds', {})
    away_team = game.get('away_team', '')
    home_team = game.get('home_team', '')

    # Get Kalshi market odds (as probabilities 0-1)
    away_market_prob = float(kalshi_odds.get('away_win_price', 0)) if kalshi_odds else 0
    home_market_prob = float(kalshi_odds.get('home_win_price', 0)) if kalshi_odds else 0

    # Skip games without Kalshi odds
    if not away_market_prob or not home_market_prob:
        return None

    # Skip completed games
    if game.get('is_completed', False):
        return None

    # Convert to cents for display (0-100)
    away_odds_cents = away_market_prob * 100
    home_odds_cents = home_market_prob * 100

    # Filter out terrible value bets (odds > 95¢ = 95% probability)
    # At 95¢+, profit is too low to be worth the risk
    if away_odds_cents > 95 or home_odds_cents > 95:
        logger.debug(f"Skipping {away_team} @ {home_team} - odds too high ({away_odds_cents:.0f}¢/{home_odds_cents:.0f}¢)")
        return None

    # Use AdvancedBettingAIAgent to get AI's prediction
    try:
        agent = AdvancedBettingAIAgent()
        analysis = agent.analyze_betting_opportunity(game, kalshi_odds)

        if not analysis or not analysis.get('predicted_winner'):
            return None

        # Get AI's predicted winner and confidence
        ai_winner = analysis.get('predicted_winner', '')  # 'away' or 'home'
        ai_win_prob = analysis.get('win_probability', 0.5)

        # Determine which team AI recommends and what market thinks
        if ai_winner == 'away':
            recommended_team = away_team
            ai_team_prob = ai_win_prob
            market_team_prob = away_market_prob
            team_odds_cents = away_odds_cents
        else:
            recommended_team = home_team
            ai_team_prob = ai_win_prob
            market_team_prob = home_market_prob
            team_odds_cents = home_odds_cents

        # Calculate EDGE: AI probability - Market probability
        # Positive edge = AI thinks team is undervalued
        edge = ai_team_prob - market_team_prob

        # Only recommend if AI sees value (edge > 2%)
        # Lowered from 5% to 2% - market is often efficient, 2-3% edge is valuable
        if edge < 0.02:
            logger.debug(f"Skipping {away_team} @ {home_team} - no edge ({edge:.1%})")
            return None

        # Calculate expected value based on AI's probability vs market odds
        # EV = (AI Win Prob × Payout) - (AI Loss Prob × Stake)
        stake = 100
        payout = (1.0 / market_team_prob) * stake if market_team_prob > 0 else 0
        ev = (ai_team_prob * payout) - ((1 - ai_team_prob) * stake)

        # Calculate Kelly criterion
        kelly = calculate_kelly_criterion(ai_team_prob, market_team_prob)

        # Calculate potential profit on $100 bet
        potential_profit = payout - stake if payout > stake else 0

        # Determine confidence based on edge and AI confidence
        ai_confidence = analysis.get('confidence_score', 50)
        if edge >= 0.15 and ai_confidence >= 75:
            confidence = 'HIGH'
            confidence_score = min(95, 70 + (edge * 100))
        elif edge >= 0.08 and ai_confidence >= 60:
            confidence = 'MEDIUM'
            confidence_score = min(80, 60 + (edge * 100))
        else:
            confidence = 'LOW'
            confidence_score = min(70, 50 + (edge * 100))

        return {
            'game_id': game.get('game_id', ''),
            'sport': game.get('sport', 'NFL'),
            'away_team': away_team,
            'home_team': home_team,
            'favorite': recommended_team,
            'favorite_odds': team_odds_cents,
            'favorite_prob': ai_team_prob,
            'market_prob': market_team_prob,
            'edge': edge,
            'confidence': confidence,
            'confidence_score': confidence_score,
            'expected_value': ev,
            'kelly_pct': kelly,
            'potential_profit': potential_profit,
            'game_time': game.get('game_time', ''),
            'is_live': game.get('is_live', False),
            'kalshi_ticker': kalshi_odds.get('ticker', ''),
            'recommendation': analysis.get('recommendation', 'PASS'),
            'ai_confidence': ai_confidence,
            'ai_predicted_winner': ai_winner,
            'ai_reasoning': analysis.get('reasoning', [])
        }

    except Exception as e:
        logger.error(f"Error analyzing game {away_team} @ {home_team}: {e}")
        return None


def rank_betting_opportunities(opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Rank betting opportunities by edge and expected value

    Prioritizes:
    1. Large edge (AI probability >> market odds)
    2. High expected value
    3. AI confidence
    """

    if not opportunities:
        return []

    # Calculate combined score
    for opp in opportunities:
        # Score = (Edge × 40%) + (EV × 40%) + (AI Confidence × 20%)
        edge_pct = opp.get('edge', 0) * 100  # Convert to percentage
        ev_normalized = min(max(opp['expected_value'] / 100, 0), 1)  # Normalize
        ai_conf = opp.get('ai_confidence', 50) / 100  # Normalize to 0-1

        combined_score = (edge_pct * 0.4) + (ev_normalized * 40) + (ai_conf * 20)
        opp['combined_score'] = combined_score

    # Sort by combined score (highest first)
    ranked = sorted(opportunities, key=lambda x: x['combined_score'], reverse=True)

    return ranked


def main():
    """Main betting recommendations page"""

    st.title("🎯 AVA Betting Recommendations")
    st.markdown("AI finds VALUE bets where AI prediction disagrees with market odds")

    # Filters in sidebar
    with st.sidebar:
        st.header("⚙️ Filters")

        days_ahead = st.slider(
            "Days Ahead",
            min_value=1,
            max_value=14,
            value=8,
            help="Only show games within this many days"
        )

        sports_filter = st.multiselect(
            "Sports",
            options=['NFL', 'NBA', 'NCAA'],
            default=['NFL', 'NBA', 'NCAA'],
            help="Filter by sport"
        )

        min_edge = st.slider(
            "Min Edge %",
            min_value=0,
            max_value=20,
            value=2,
            help="Minimum edge required (AI prob - market prob). Lower = more opportunities."
        )

        st.info("💡 Tip: 2-3% edge is valuable! Market is often efficient.")

        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.rerun()

        st.markdown("---")

        # HTML Report Generation
        if st.button("📄 Generate HTML Report", help="Create printable HTML report"):
            with st.spinner("Generating report..."):
                try:
                    from src.email_game_reports import EmailGameReportService
                    service = EmailGameReportService()
                    html_content = service.generate_game_report(include_all_games=False)

                    # Add print CSS
                    html_content = html_content.replace(
                        '</style>',
                        """
                        @media print {
                            body { background-color: white !important; }
                            .container { box-shadow: none !important; }
                            .game-card { page-break-inside: avoid; }
                        }
                        </style>
                        """
                    )

                    # Offer download
                    st.download_button(
                        label="📥 Download HTML Report",
                        data=html_content,
                        file_name=f"nfl_betting_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                        mime="text/html",
                        help="Download and open in browser, then Ctrl+P to print or save as PDF"
                    )
                    st.success("✅ Report ready! Click download button above.")
                except Exception as e:
                    st.error(f"Error generating report: {e}")

    # Header metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Analysis Method", "AI vs Market")
    with col2:
        st.metric("Data Source", "Kalshi Markets")
    with col3:
        st.metric("Ranking", "Edge + EV")
    with col4:
        st.metric("Days Ahead", f"{days_ahead} days")

    st.markdown("---")

    # Fetch and analyze games
    with st.spinner("🤖 AVA is finding value bets across all sports..."):

        # Fetch all games
        all_games = analyze_all_games(days_ahead=days_ahead)

        if not all_games:
            st.warning("No games found with Kalshi odds")
            return

        # Filter by sport
        all_games = [g for g in all_games if g.get('sport') in sports_filter]

        # Count games with Kalshi odds
        games_with_odds = sum(1 for g in all_games if g.get('kalshi_odds'))
        games_without_odds = len(all_games) - games_with_odds

        st.info(f"📊 Analyzing {len(all_games)} games | ✅ {games_with_odds} with Kalshi odds | ❌ {games_without_odds} without odds")

        # Analyze each game
        opportunities = []
        progress_bar = st.progress(0)

        for idx, game in enumerate(all_games):
            analysis = analyze_betting_opportunity(game)
            if analysis:
                # Apply min edge filter
                if analysis.get('edge', 0) * 100 >= min_edge:
                    opportunities.append(analysis)

            # Update progress
            progress_bar.progress((idx + 1) / len(all_games))

        progress_bar.empty()

        if not opportunities:
            st.warning(f"No value bets found with edge >= {min_edge}%. Try lowering the min edge filter.")
            return

        # Rank opportunities
        ranked_opportunities = rank_betting_opportunities(opportunities)

        st.success(f"✅ Found {len(ranked_opportunities)} value betting opportunities")

    # Display tabs for different views
    tab1, tab2, tab3 = st.tabs(["🏆 Top Picks", "📊 All Opportunities", "📈 Analytics"])

    with tab1:
        st.markdown("### 🏆 Top 10 Value Betting Opportunities")
        st.markdown("Ranked by **EDGE** (AI probability vs Market odds) + Expected Value")

        top_picks = ranked_opportunities[:10]

        for idx, opp in enumerate(top_picks, 1):
            edge_pct = opp.get('edge', 0) * 100

            # Color based on edge size
            if edge_pct >= 15:
                border_color = '#00ff00'
                bg_color = 'rgba(0, 255, 0, 0.1)'
            elif edge_pct >= 8:
                border_color = '#ffd700'
                bg_color = 'rgba(255, 215, 0, 0.1)'
            else:
                border_color = '#888888'
                bg_color = 'rgba(136, 136, 136, 0.1)'

            st.markdown(f"""
                <div style="border-left: 4px solid {border_color}; background: {bg_color};
                            padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                    <h3 style="margin: 0;">#{idx} - {opp['sport']} | {opp['away_team']} @ {opp['home_team']}</h3>
                    <p style="margin: 5px 0; color: #aaa;">{opp['game_time']}</p>
                </div>
            """, unsafe_allow_html=True)

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "AI Recommends",
                    opp['favorite'],
                    f"AI: {opp['favorite_prob']:.0%} | Market: {opp['market_prob']:.0%}"
                )

            with col2:
                # Get both teams' Kalshi odds from the game data
                away_odds = int(opp.get('market_prob', 0.5) * 100) if opp.get('ai_predicted_winner') == 'home' else int((1 - opp.get('market_prob', 0.5)) * 100)
                home_odds = int(opp.get('market_prob', 0.5) * 100) if opp.get('ai_predicted_winner') != 'home' else int((1 - opp.get('market_prob', 0.5)) * 100)

                st.metric(
                    "Edge",
                    f"{edge_pct:+.1f}%",
                    f"Kalshi: {opp['away_team'][:3].upper()} {away_odds}¢ | {opp['home_team'][:3].upper()} {home_odds}¢"
                )

            with col3:
                st.metric(
                    "Expected Value",
                    f"${opp['expected_value']:.2f}",
                    f"Profit: ${opp['potential_profit']:.2f}"
                )

            with col4:
                st.metric(
                    "Score",
                    f"{opp['combined_score']:.1f}",
                    f"Kelly: {opp['kelly_pct']:.1%}"
                )

            # AI Reasoning
            reasoning = opp.get('ai_reasoning', [])
            if reasoning:
                with st.expander("🤖 AI Analysis"):
                    for reason in reasoning[:3]:  # Show top 3 reasons
                        st.write(f"• {reason}")

            # Recommendation - More nuanced thresholds
            if edge_pct >= 10:
                st.success(f"🚀 **STRONG BUY** - AI sees {edge_pct:.1f}% edge over market | Confidence: {opp['ai_confidence']:.0f}%")
            elif edge_pct >= 5:
                st.info(f"💰 **BUY** - Good value detected ({edge_pct:.1f}% edge) | Confidence: {opp['ai_confidence']:.0f}%")
            elif edge_pct >= 2:
                st.warning(f"👀 **HOLD** - Worth watching ({edge_pct:.1f}% edge) | Confidence: {opp['ai_confidence']:.0f}%")
            else:
                st.error(f"❌ **PASS** - Minimal edge ({edge_pct:.1f}%)")

            st.markdown("---")

    with tab2:
        st.markdown("### 📊 All Betting Opportunities")

        # Convert to DataFrame
        df = pd.DataFrame(ranked_opportunities)

        # Format columns
        df_display = df[[
            'sport', 'away_team', 'home_team', 'favorite',
            'edge', 'favorite_odds', 'favorite_prob', 'market_prob',
            'expected_value', 'combined_score'
        ]].copy()

        df_display.columns = [
            'Sport', 'Away', 'Home', 'AI Pick',
            'Edge %', 'Market Odds', 'AI Prob', 'Market Prob',
            'EV ($)', 'Score'
        ]

        # Format numeric columns
        df_display['Edge %'] = df_display['Edge %'].apply(lambda x: f"{x*100:+.1f}%")
        df_display['Market Odds'] = df_display['Market Odds'].apply(lambda x: f"{x:.0f}¢")
        df_display['AI Prob'] = df_display['AI Prob'].apply(lambda x: f"{x:.0%}")
        df_display['Market Prob'] = df_display['Market Prob'].apply(lambda x: f"{x:.0%}")
        df_display['EV ($)'] = df_display['EV ($)'].apply(lambda x: f"${x:.2f}")
        df_display['Score'] = df_display['Score'].apply(lambda x: f"{x:.1f}")

        st.dataframe(
            df_display,
            use_container_width=True,
            height=600
        )

        # Download button
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Full Analysis (CSV)",
            data=csv,
            file_name=f"ava_betting_recommendations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

    with tab3:
        st.markdown("### 📈 Analytics & Insights")

        # Summary statistics
        col1, col2, col3 = st.columns(3)

        with col1:
            avg_edge = sum(opp.get('edge', 0) for opp in ranked_opportunities) / len(ranked_opportunities) * 100
            st.metric("Avg Edge", f"{avg_edge:.1f}%", help="Average edge across all opportunities")

        with col2:
            avg_ev = sum(opp['expected_value'] for opp in ranked_opportunities) / len(ranked_opportunities)
            st.metric("Avg EV", f"${avg_ev:.2f}", help="Average expected value")

        with col3:
            total_potential = sum(opp['potential_profit'] for opp in ranked_opportunities)
            st.metric("Total Potential Profit", f"${total_potential:.2f}", help="If all bets win")

        st.markdown("---")

        # Edge distribution
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 🎯 Edge Distribution")
            edge_values = [opp.get('edge', 0) * 100 for opp in ranked_opportunities]
            st.line_chart(edge_values)

        with col2:
            st.markdown("#### 💰 Expected Value Distribution")
            ev_values = [opp['expected_value'] for opp in ranked_opportunities]
            st.line_chart(ev_values)

        # Sport breakdown
        st.markdown("#### 🏈🎓🏀 Sport Breakdown")
        sport_counts = pd.Series([opp['sport'] for opp in ranked_opportunities]).value_counts()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("NFL Games", sport_counts.get('NFL', 0))
        with col2:
            st.metric("NCAA Games", sport_counts.get('NCAA', 0))
        with col3:
            st.metric("NBA Games", sport_counts.get('NBA', 0))

        # Top insights
        st.markdown("#### 🔍 Key Insights")

        high_edge = [opp for opp in ranked_opportunities if opp.get('edge', 0) >= 0.15]
        positive_ev = [opp for opp in ranked_opportunities if opp['expected_value'] > 0]

        st.info(f"⚡ **{len(high_edge)}** high-edge opportunities (≥15% edge)")
        st.info(f"💵 **{len(positive_ev)}** positive EV bets ({len(positive_ev)/len(ranked_opportunities):.0%} of total)")

        if high_edge:
            avg_ev = sum(opp['expected_value'] for opp in high_edge) / len(high_edge)
            avg_edge_pct = sum(opp.get('edge', 0) for opp in high_edge) / len(high_edge) * 100
            st.success(f"📊 High-edge bets: Avg edge {avg_edge_pct:.1f}%, Avg EV ${avg_ev:.2f}")


if __name__ == "__main__":
    main()
