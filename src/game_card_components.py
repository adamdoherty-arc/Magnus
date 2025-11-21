"""
Enhanced Game Card Components
Modular components for displaying game cards with rich data
"""

import streamlit as st
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


def calculate_team_streak(record: str) -> Tuple[str, str]:
    """
    Calculate team streak from record if available
    
    Args:
        record: Team record string (e.g., "8-2")
    
    Returns:
        Tuple of (streak_text, streak_emoji)
    """
    # TODO: This would need historical game data
    # For now, return empty
    return "", ""


def format_team_stats_display(team_name: str, record: str, streak: str = "") -> str:
    """
    Format team display with record and streak
    
    Args:
        team_name: Name of the team
        record: Win-Loss record
        streak: Current streak (e.g., "W3", "L2")
    
    Returns:
        Formatted HTML string
    """
    streak_display = f" • {streak}" if streak else ""
    record_display = f" ({record})" if record else ""
    
    return f"**{team_name}{record_display}**{streak_display}"


def render_stats_comparison(away_stats: Dict, home_stats: Dict, game: Dict) -> None:
    """
    Render side-by-side team statistics comparison
    
    Args:
        away_stats: Away team statistics
        home_stats: Home team statistics
        game: Game data dictionary
    """
    st.markdown("### 📊 Team Statistics")
    
    # Create 3-column layout for stats
    col1, col2, col3 = st.columns([2, 3, 2])
    
    with col1:
        st.markdown("#### Away")
    
    with col2:
        st.markdown("#### Category")
    
    with col3:
        st.markdown("#### Home")
    
    # Display stats rows
    stats_to_display = [
        ("Record", away_stats.get('record', 'N/A'), home_stats.get('record', 'N/A')),
        ("Points/Game", away_stats.get('ppg', 'N/A'), home_stats.get('ppg', 'N/A')),
        ("Points Against", away_stats.get('ppg_against', 'N/A'), home_stats.get('ppg_against', 'N/A')),
    ]
    
    for category, away_val, home_val in stats_to_display:
        col1, col2, col3 = st.columns([2, 3, 2])
        
        with col1:
            st.markdown(f"**{away_val}**")
        
        with col2:
            st.markdown(f"*{category}*")
        
        with col3:
            st.markdown(f"**{home_val}**")


def get_deepseek_game_analysis(
    away_team: str,
    home_team: str,
    away_record: str,
    home_record: str,
    game_context: Dict
) -> Optional[Dict]:
    """
    Get DeepSeek AI analysis for a game
    
    Args:
        away_team: Away team name
        home_team: Home team name
        away_record: Away team record
        home_record: Home team record
        game_context: Additional game context
    
    Returns:
        Dictionary with prediction data or None
    """
    try:
        from src.services.llm_service import get_llm_service
        
        prompt = f"""Analyze this football game matchup and provide a prediction:

Away Team: {away_team} ({away_record})
Home Team: {home_team} ({home_record})

Provide your analysis in this exact JSON format:
{{
    "predicted_winner": "{away_team} or {home_team}",
    "win_probability": 0.XX (as decimal, e.g., 0.65 for 65%),
    "predicted_spread": X.X (positive if away favored, negative if home favored),
    "confidence": "high|medium|low",
    "key_insight": "One sentence explaining the key factor in your prediction"
}}

Be concise and data-driven. Focus on recent performance and matchup advantages."""

        llm_service = get_llm_service()
        
        # Check if DeepSeek is available
        if "deepseek" not in llm_service.get_available_providers():
            logger.warning("DeepSeek not available")
            return None
        
        result = llm_service.generate(
            prompt=prompt,
            provider="deepseek",
            model="deepseek-chat",
            temperature=0.3,
            max_tokens=300
        )
        
        # Parse JSON response
        import json
        import re
        
        text = result['text']
        
        # Try to extract JSON from response
        json_match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
        if json_match:
            prediction_data = json.loads(json_match.group())
            
            # Validate prediction
            if prediction_data.get('predicted_winner') and \
               prediction_data.get('win_probability') and \
               prediction_data.get('confidence'):
                return prediction_data
        
        logger.warning(f"Could not parse DeepSeek response: {text[:100]}")
        return None
        
    except Exception as e:
        logger.error(f"Error getting DeepSeek analysis: {e}")
        return None


def render_dual_ai_predictions(
    local_prediction: Optional[Dict],
    deepseek_prediction: Optional[Dict],
    away_team: str,
    home_team: str
) -> None:
    """
    Render side-by-side AI predictions from local model and DeepSeek
    
    Args:
        local_prediction: Prediction from local NFL/NCAA model
        deepseek_prediction: Prediction from DeepSeek AI
        away_team: Away team name
        home_team: Home team name
    """
    st.markdown("### 🤖 AI Predictions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Local Model")
        if local_prediction:
            winner = local_prediction.get('winner', 'N/A')
            prob = local_prediction.get('probability', 0.5)
            conf = local_prediction.get('confidence', 'low')
            spread = local_prediction.get('spread', 0)
            
            # Confidence emoji
            conf_emoji = '🟢' if conf == 'high' else '🟡' if conf == 'medium' else '⚪'
            
            st.metric("Predicted Winner", winner)
            st.metric("Win Probability", f"{int(prob * 100)}%")
            st.metric("Spread", f"{spread:.1f}" if spread != 0 else "-")
            st.markdown(f"{conf_emoji} **{conf.upper()} CONFIDENCE**")
        else:
            st.info("No prediction available")
    
    with col2:
        st.markdown("#### DeepSeek R1")
        if deepseek_prediction:
            winner = deepseek_prediction.get('predicted_winner', 'N/A')
            prob = deepseek_prediction.get('win_probability', 0.5)
            conf = deepseek_prediction.get('confidence', 'low')
            spread = deepseek_prediction.get('predicted_spread', 0)
            insight = deepseek_prediction.get('key_insight', '')
            
            # Confidence emoji
            conf_emoji = '🟢' if conf == 'high' else '🟡' if conf == 'medium' else '⚪'
            
            st.metric("Predicted Winner", winner)
            st.metric("Win Probability", f"{int(prob * 100)}%")
            st.metric("Spread", f"{abs(spread):.1f}" if spread != 0 else "-")
            st.markdown(f"{conf_emoji} **{conf.upper()} CONFIDENCE**")
            
            # Show insight
            if insight:
                st.markdown(f"💡 *{insight}*")
        else:
            st.info("Loading DeepSeek analysis...")


def render_betting_section(
    kalshi_odds: Dict,
    expected_value: float,
    recommendation: str,
    away_team: str,
    home_team: str
) -> None:
    """
    Render betting odds and recommendations
    
    Args:
        kalshi_odds: Dictionary with Kalshi odds
        expected_value: Expected value percentage
        recommendation: BET/HOLD/PASS
        away_team: Away team name
        home_team: Home team name
    """
    st.markdown("### 💰 Betting Odds & Value")
    
    if kalshi_odds:
        away_odds = kalshi_odds.get('away_win_price', 0) * 100
        home_odds = kalshi_odds.get('home_win_price', 0) * 100
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**{away_team}:** {away_odds:.0f}¢")
        
        with col2:
            st.markdown(f"**{home_team}:** {home_odds:.0f}¢")
        
        # Show EV and recommendation
        if expected_value > 0:
            ev_color = "#4CAF50" if expected_value > 10 else "#FFA726"
            st.markdown(f"**Expected Value:** <span style='color:{ev_color};'>+{expected_value:.1f}%</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"**Expected Value:** {expected_value:.1f}%")
        
        # Recommendation
        if recommendation == "BET":
            st.success(f"🎯 **Recommendation:** {recommendation}")
        elif recommendation == "HOLD":
            st.warning(f"⚠️ **Recommendation:** {recommendation}")
        else:
            st.info(f"❌ **Recommendation:** {recommendation}")
    else:
        st.info("No betting odds available")


def render_expandable_details(game: Dict) -> None:
    """
    Render expandable section with detailed game information
    
    Args:
        game: Game data dictionary
    """
    with st.expander("📈 Detailed Statistics"):
        st.markdown("### Historical Matchups")
        st.info("Coming soon: Head-to-head record and last 5 meetings")
        
        st.markdown("### Key Players")
        st.info("Coming soon: Top players and their recent performance")
        
        st.markdown("### Venue & Conditions")
        st.info("Coming soon: Weather, stadium, and other factors")

