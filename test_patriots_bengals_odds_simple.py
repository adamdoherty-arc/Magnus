"""
Test script to examine Patriots vs Bengals odds data flow - No Emoji Version
"""
from src.kalshi_db_manager import KalshiDBManager
import psycopg2.extras
import json

db = KalshiDBManager()
conn = db.get_connection()
cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

# Look for Patriots and Bengals markets
print("=" * 80)
print("SEARCHING FOR PATRIOTS vs BENGALS KALSHI MARKETS")
print("=" * 80)

cur.execute("""
    SELECT
        ticker,
        title,
        yes_price,
        no_price,
        volume,
        home_team,
        away_team,
        market_type,
        raw_data
    FROM kalshi_markets
    WHERE (title ILIKE %s AND title ILIKE %s)
       OR (title ILIKE %s AND title ILIKE %s)
    ORDER BY volume DESC
    LIMIT 5
""", ('%patriots%', '%bengals%', '%new england%', '%cincinnati%'))

results = cur.fetchall()
if results:
    for idx, row in enumerate(results):
        print(f"\n=== MARKET {idx+1} ===")
        print(f"Ticker: {row['ticker']}")
        print(f"Title: {row['title']}")
        print(f"Yes Price: {row['yes_price']:.4f} ({row['yes_price']*100:.1f} cents)")
        print(f"No Price: {row['no_price']:.4f} ({row['no_price']*100:.1f} cents)")
        print(f"Volume: ${row['volume']:,.0f}")
        print(f"Home Team (DB): {row['home_team']}")
        print(f"Away Team (DB): {row['away_team']}")

        # Parse ticker to identify which team is "yes"
        ticker = row['ticker']
        ticker_parts = ticker.split('-')
        print(f"Ticker parts: {ticker_parts}")
        if len(ticker_parts) > 1:
            ticker_suffix = ticker_parts[-1].upper()
            print(f"Ticker suffix (indicates YES team): {ticker_suffix}")

            # Analyze what this means
            if ticker_suffix == 'NE':
                print("  >> 'NE' suffix means Patriots are the YES option")
                print(f"  >> Patriots odds: {row['yes_price']*100:.1f} cents (YES)")
                print(f"  >> Bengals odds: {row['no_price']*100:.1f} cents (NO)")
            elif ticker_suffix == 'CIN':
                print("  >> 'CIN' suffix means Bengals are the YES option")
                print(f"  >> Bengals odds: {row['yes_price']*100:.1f} cents (YES)")
                print(f"  >> Patriots odds: {row['no_price']*100:.1f} cents (NO)")

        print("-" * 80)
else:
    print('\nNo Patriots/Bengals markets found')

# Now test the ESPN matcher logic
print("\n" + "=" * 80)
print("TESTING ESPN KALSHI MATCHER LOGIC")
print("=" * 80)

from src.espn_kalshi_matcher import ESPNKalshiMatcher

# Create a fake ESPN game - CRITICAL: Patriots are AWAY team (9-2), Bengals are HOME team (3-7)
fake_espn_game = {
    'away_team': 'New England Patriots',  # 9-2 (better record)
    'home_team': 'Cincinnati Bengals',     # 3-7 (worse record)
    'away_record': '9-2',
    'home_record': '3-7',
    'game_time': '2024-11-17 13:00:00'
}

print(f"\nESPN Game Setup:")
print(f"  AWAY: {fake_espn_game['away_team']} ({fake_espn_game['away_record']})")
print(f"  HOME: {fake_espn_game['home_team']} ({fake_espn_game['home_record']})")

matcher = ESPNKalshiMatcher()
result = matcher.match_game_to_kalshi(fake_espn_game)

if result:
    print(f"\nMATCH FOUND:")
    print(f"Ticker: {result['ticker']}")
    print(f"Market Title: {result['market_title']}")
    print(f"\nMATCHER OUTPUT:")
    print(f"  away_win_price: {result['away_win_price']:.4f} ({result['away_win_price']*100:.1f} cents)")
    print(f"  home_win_price: {result['home_win_price']:.4f} ({result['home_win_price']*100:.1f} cents)")
    print(f"\nINTERPRETATION:")
    print(f"  Patriots (away, 9-2): {result['away_win_price']*100:.1f} cents")
    print(f"  Bengals (home, 3-7): {result['home_win_price']*100:.1f} cents")

    # Check if this makes sense
    if result['away_win_price'] > result['home_win_price']:
        print(f"\n  RESULT: Patriots favored (makes sense - they have better record)")
    else:
        print(f"\n  ERROR: Bengals favored (DOES NOT make sense - worse record!)")
        print(f"  This indicates the odds are REVERSED in the matcher!")
else:
    print("\nNO MATCH FOUND")

cur.close()
conn.close()

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
