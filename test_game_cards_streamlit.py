"""
Minimal Streamlit test for game cards page
"""

import streamlit as st
from game_cards_visual_page import fetch_games_grouped
from src.kalshi_db_manager import KalshiDBManager

st.set_page_config(page_title="Test Game Cards", layout="wide")

st.title("🏈 Test Game Cards Page")

# Initialize
db = KalshiDBManager()

# Simple sport selector
st.markdown("### Select Sport")
sport = st.radio("Sport", ["NFL", "CFB (NCAA)"], horizontal=True)

sport_filter = "CFB" if "CFB" in sport else "NFL"

st.markdown(f"**Selected sport filter:** `{sport_filter}`")

# Fetch games
with st.spinner("Loading games..."):
    games = fetch_games_grouped(db, min_confidence=70, sport=sport_filter)

st.success(f"✅ Backend returned **{len(games)} games**")

# Display summary
if games:
    st.markdown(f"### 📊 Found {len(games)} {sport_filter} Games")

    for i, game in enumerate(games[:5], 1):
        with st.expander(f"Game {i}: {game['team1']} vs {game['team2']}", expanded=(i==1)):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Team 1", game['team1'])
            with col2:
                st.markdown("**VS**")
            with col3:
                st.metric("Team 2", game['team2'])

            st.caption(f"Time: {game['game_time_str']}")
            st.caption(f"Markets: {len(game['markets'])}")
            st.caption(f"Confidence: {game['best_confidence']:.1f}%")
else:
    st.error(f"❌ No {sport_filter} games found")
    st.info("Backend returned 0 games. Check database or query logic.")
