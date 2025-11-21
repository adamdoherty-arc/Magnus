"""
Game-by-Game Analysis Page - NFL Winner Predictions
Focus on game outcomes, price action, and quick betting opportunities
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timezone
import re
from src.kalshi_db_manager import KalshiDBManager
from src.kalshi_client import KalshiClient
import time

def show_game_by_game():
    """Main function for game-by-game analysis"""

    st.title("🏈 Game-by-Game Analysis")
    st.caption("NFL winner predictions sorted by game time - Focus on outcomes and price action")

    # Initialize
    db = KalshiDBManager()
    client = KalshiClient()

    # Top controls
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

    with col1:
        st.markdown("**Quick Filters:**")

    with col2:
        min_confidence = st.slider("Min Confidence", 0, 100, 70, 5)

    with col3:
        min_volume = st.number_input("Min Volume ($)", 0, 10000, 50, 50)

    with col4:
        if st.button("🔄 Refresh Prices", type="primary"):
            st.cache_data.clear()
            st.rerun()

    # Fetch games
    with st.spinner("Loading games and markets..."):
        games = fetch_games_with_markets(db, min_confidence, min_volume)

    if not games:
        st.warning("No games found. Run `python pull_nfl_games.py` to sync markets.")
        return

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Games Today", len(games))
    with col2:
        total_opportunities = sum(len(g['markets']) for g in games)
        st.metric("Total Opportunities", total_opportunities)
    with col3:
        high_conf = sum(1 for g in games for m in g['markets'] if m.get('confidence', 0) >= 80)
        st.metric("High Confidence (≥80)", high_conf)
    with col4:
        next_game = games[0] if games else None
        if next_game:
            mins_until = next_game.get('minutes_until_game', 0)
            st.metric("Next Game In", f"{mins_until // 60}h {mins_until % 60}m")

    st.markdown("---")

    # Export button at top
    if st.button("📊 Export Daily Report to CSV"):
        export_daily_report(games)
        st.success("✓ Report exported to kalshi_daily_games_report.csv")

    # Display each game
    for i, game in enumerate(games):
        display_game_card(game, i)

    # Auto-refresh for live games
    if any(g.get('is_live', False) for g in games):
        st.info("🔴 LIVE: Games in progress - Refreshing every 60 seconds")
        time.sleep(60)
        st.rerun()


def fetch_games_with_markets(db, min_confidence=70, min_volume=50):
    """Fetch games grouped by time with their markets"""

    # Get all active markets with predictions
    query = """
    SELECT
        m.ticker,
        m.title,
        m.close_time,
        m.yes_price,
        m.no_price,
        m.volume,
        m.status,
        p.confidence_score,
        p.predicted_outcome,
        p.edge_percentage,
        p.reasoning
    FROM kalshi_markets m
    LEFT JOIN kalshi_predictions p ON m.id = p.market_id
    WHERE m.status = 'active'
        AND (p.confidence_score >= %s OR p.confidence_score IS NULL)
        AND m.close_time IS NOT NULL
    ORDER BY m.close_time ASC, m.volume DESC
    """

    markets = db.execute_query(query, (min_confidence,))

    if not markets:
        return []

    # Group by game time
    games_dict = {}

    for market in markets:
        close_time = market.get('close_time')
        if not close_time:
            continue

        # Parse time
        if isinstance(close_time, str):
            close_time_fixed = re.sub(r'([-+]\d{2})$', r'\1:00', close_time)
            close_dt = datetime.fromisoformat(close_time_fixed)
        else:
            close_dt = close_time

        game_key = close_dt.strftime('%Y-%m-%d %H:%M')

        if game_key not in games_dict:
            games_dict[game_key] = {
                'game_time': close_dt,
                'game_time_str': close_dt.strftime('%a %b %d, %I:%M %p %Z'),
                'markets': [],
                'teams': set()
            }

        # Filter by volume
        volume = float(market.get('volume', 0) or 0)
        if volume < min_volume:
            continue

        # Extract teams from title
        title = market.get('title', '')
        teams = extract_teams(title)

        # Add market
        market_data = {
            'ticker': market.get('ticker'),
            'title': title,
            'yes_price': float(market.get('yes_price', 0) or 0),
            'no_price': float(market.get('no_price', 0) or 0),
            'volume': volume,
            'confidence': float(market.get('confidence_score', 0) or 0),
            'predicted_outcome': market.get('predicted_outcome', 'unknown'),
            'edge': float(market.get('edge_percentage', 0) or 0),
            'reasoning': market.get('reasoning', 'No analysis'),
            'teams': teams
        }

        games_dict[game_key]['markets'].append(market_data)
        games_dict[game_key]['teams'].update(teams)

    # Convert to sorted list
    games = []
    now_utc = datetime.now(timezone.utc)

    for game_key, game_data in sorted(games_dict.items()):
        game_time = game_data['game_time']

        # Calculate minutes until game
        if game_time.tzinfo:
            game_time_utc = game_time.astimezone(timezone.utc)
        else:
            game_time_utc = game_time.replace(tzinfo=timezone.utc)

        delta = (game_time_utc - now_utc).total_seconds() / 60
        minutes_until = max(0, int(delta))

        # Determine if game is live (within 3.5 hours of start time)
        is_live = -30 < delta < 210

        game_data['minutes_until_game'] = minutes_until
        game_data['is_live'] = is_live
        game_data['teams_str'] = ' vs '.join(sorted(game_data['teams']))[:50] if game_data['teams'] else 'Multiple Games'

        # Sort markets by confidence
        game_data['markets'].sort(key=lambda x: x.get('confidence', 0), reverse=True)

        games.append(game_data)

    return games


def extract_teams(title):
    """Extract team names from market title"""
    teams = set()

    # Common team names
    team_keywords = [
        'Indianapolis', 'Atlanta', 'Buffalo', 'Cleveland', 'Detroit',
        'Tampa Bay', 'Carolina', 'Chicago', 'Seattle', 'Jacksonville',
        'Baltimore', 'Minnesota', 'Green Bay', 'Los Angeles', 'New York',
        'Arizona', 'Washington', 'Houston', 'Miami', 'Kansas City',
        'Las Vegas', 'Denver', 'San Francisco', 'Dallas', 'Philadelphia',
        'New England', 'Cincinnati', 'Pittsburgh', 'Tennessee'
    ]

    for team in team_keywords:
        if team in title:
            teams.add(team)

    # Handle abbreviations
    if 'LA' in title or 'L.A.' in title:
        teams.add('Los Angeles')
    if 'KC' in title:
        teams.add('Kansas City')
    if 'SF' in title:
        teams.add('San Francisco')

    return teams


def display_game_card(game, index):
    """Display a single game with its markets"""

    game_time_str = game['game_time_str']
    minutes_until = game['minutes_until_game']
    is_live = game['is_live']
    teams = game['teams_str']
    markets = game['markets']

    # Header styling
    if is_live:
        header_emoji = "🔴 LIVE"
        header_color = "#ff4444"
    elif minutes_until < 180:  # < 3 hours
        header_emoji = "⚡ STARTING SOON"
        header_color = "#ff9900"
    else:
        header_emoji = "📅"
        header_color = "#4444ff"

    # Time display
    if minutes_until < 60:
        time_str = f"{minutes_until}m"
    else:
        time_str = f"{minutes_until // 60}h {minutes_until % 60}m"

    # Main card
    with st.expander(
        f"{header_emoji} **{game_time_str}** (in {time_str}) | {len(markets)} Opportunities | {teams}",
        expanded=(index == 0)  # Expand first game
    ):

        # Quick stats
        if markets:
            avg_conf = sum(m['confidence'] for m in markets) / len(markets)
            max_edge = max(m['edge'] for m in markets)
            total_vol = sum(m['volume'] for m in markets)

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Avg Confidence", f"{avg_conf:.0f}%")
            with col2:
                st.metric("Max Edge", f"{max_edge:.1f}%")
            with col3:
                st.metric("Total Volume", f"${total_vol:,.0f}")
            with col4:
                high_conf_count = sum(1 for m in markets if m['confidence'] >= 80)
                st.metric("High Confidence", high_conf_count)

        st.markdown("---")

        # Show top markets
        st.markdown("### 🎯 Top Opportunities")

        for i, market in enumerate(markets[:10], 1):  # Top 10
            display_market_row(market, i, is_live)

        # Show all link
        if len(markets) > 10:
            with st.expander(f"📋 View All {len(markets)} Markets"):
                for i, market in enumerate(markets[10:], 11):
                    display_market_row(market, i, is_live)


def display_market_row(market, index, is_live=False):
    """Display a single market opportunity"""

    ticker = market['ticker']
    title = market['title']
    yes_price = market['yes_price']
    no_price = market['no_price']
    volume = market['volume']
    confidence = market['confidence']
    predicted = market['predicted_outcome']
    edge = market['edge']
    reasoning = market['reasoning']

    # Confidence color
    if confidence >= 85:
        conf_color = "🟢"
    elif confidence >= 70:
        conf_color = "🟡"
    else:
        conf_color = "🔴"

    # Price display
    if yes_price > 0:
        yes_prob = yes_price * 100
        no_prob = no_price * 100
        price_str = f"YES: {yes_prob:.1f}% | NO: {no_prob:.1f}%"
    else:
        price_str = "No pricing available"

    # Recommendation
    if predicted == 'yes':
        rec = "✅ BUY YES"
        rec_color = "green"
    elif predicted == 'no':
        rec = "❌ BUY NO"
        rec_color = "red"
    else:
        rec = "⏸️ PASS"
        rec_color = "gray"

    # Display
    with st.container():
        col1, col2, col3 = st.columns([3, 1, 1])

        with col1:
            st.markdown(f"**{index}. {conf_color} {title[:80]}...**" if len(title) > 80 else f"**{index}. {conf_color} {title}**")
            st.caption(f"Vol: ${volume:,.0f} | {price_str}")

        with col2:
            st.markdown(f"**Conf:** {confidence:.0f}%")
            st.markdown(f"**Edge:** {edge:.1f}%")

        with col3:
            st.markdown(f":{rec_color}[**{rec}**]")
            if is_live:
                st.markdown("🔴 **LIVE**")

        # Details expander
        with st.expander("📊 Analysis & Links"):
            st.markdown(f"**AI Reasoning:** {reasoning}")

            col1, col2 = st.columns(2)
            with col1:
                kalshi_url = f"https://kalshi.com/markets/{ticker}"
                st.link_button("📈 Open on Kalshi", kalshi_url, use_container_width=True)
            with col2:
                st.link_button("🔔 Set Alert", f"#alert-{ticker}", use_container_width=True, disabled=True)

        st.markdown("---")


def export_daily_report(games):
    """Export games to CSV"""

    rows = []

    for game in games:
        game_time = game['game_time_str']
        minutes_until = game['minutes_until_game']
        is_live = game['is_live']

        for market in game['markets']:
            rows.append({
                'Game_Time': game_time,
                'Minutes_Until_Game': minutes_until,
                'Is_Live': is_live,
                'Teams': game['teams_str'],
                'Ticker': market['ticker'],
                'Market_Title': market['title'],
                'Confidence': market['confidence'],
                'Predicted_Outcome': market['predicted_outcome'],
                'Edge_Percentage': market['edge'],
                'YES_Price': market['yes_price'],
                'NO_Price': market['no_price'],
                'Volume': market['volume'],
                'Kalshi_URL': f"https://kalshi.com/markets/{market['ticker']}"
            })

    if rows:
        df = pd.DataFrame(rows)

        # Sort by game time, then confidence
        df = df.sort_values(['Minutes_Until_Game', 'Confidence'], ascending=[True, False])

        # Export
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        filename = f'kalshi_daily_games_report_{timestamp}.csv'
        df.to_csv(filename, index=False)

        st.success(f"✓ Exported {len(df)} opportunities to {filename}")

        # Show preview
        st.dataframe(df.head(10), use_container_width=True)
    else:
        st.warning("No data to export")


def show():
    """Entry point for dashboard integration"""
    show_game_by_game()


if __name__ == "__main__":
    show_game_by_game()
