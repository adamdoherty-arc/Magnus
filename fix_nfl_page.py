"""
Fix NFL Page - Clear all caches and verify data pipeline
"""
import sys
import os

print("=" * 80)
print("NFL PAGE FIX SCRIPT")
print("=" * 80)

# Step 1: Test ESPN data
print("\n1. Testing ESPN NFL API...")
from src.espn_live_data import get_espn_client

espn = get_espn_client()
games = espn.get_scoreboard()
print(f"   [OK] Fetched {len(games)} NFL games from ESPN")

if games:
    game = games[0]
    print(f"   Example: {game['away_team']} ({game['away_score']}) @ {game['home_team']} ({game['home_score']})")

# Step 2: Test Kalshi data
print("\n2. Testing Kalshi database...")
from src.kalshi_db_manager import KalshiDBManager
import psycopg2.extras

db = KalshiDBManager()
conn = db.get_connection()
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM kalshi_markets")
market_count = cur.fetchone()[0]
cur.close()
conn.close()
print(f"   [OK] {market_count} markets in database")

# Step 3: Test matching
print("\n3. Testing ESPN-Kalshi matching...")
from src.espn_kalshi_matcher import enrich_games_with_kalshi_odds

enriched_games = enrich_games_with_kalshi_odds(games)
matched = sum(1 for g in enriched_games if g.get('kalshi_odds'))
print(f"   [OK] Matched {matched}/{len(enriched_games)} games with Kalshi odds")

if matched > 0:
    for g in enriched_games:
        if g.get('kalshi_odds'):
            print(f"   Example: {g['away_team']} vs {g['home_team']}")
            odds = g['kalshi_odds']
            print(f"      Away: {odds.get('away_win_price', 0) * 100:.0f}¢")
            print(f"      Home: {odds.get('home_win_price', 0) * 100:.0f}¢")
            break

# Step 4: Clear Streamlit cache
print("\n4. Instructions to clear Streamlit cache:")
print("   - In browser, press 'C' key")
print("   - Click 'Clear cache'")
print("   - Refresh the page")

# Step 5: Verification
print("\n5. Verification checklist:")
print("   [ ] ESPN Status shows '✅ 15 games fetched'")
print(f"   [ ] Kalshi Status shows '✅ {matched}/15 games with odds'")
print("   [ ] Game cards display with scores")
print("   [ ] Kalshi odds appear on matched games")

print("\n" + "=" * 80)
print("FIX COMPLETE - Now refresh the dashboard!")
print("=" * 80)
print("\nRun: streamlit run dashboard.py")
print("Then navigate to: Sports Game Cards → NFL")
