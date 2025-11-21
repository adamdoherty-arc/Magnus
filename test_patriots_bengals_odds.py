"""
Test script to examine Patriots vs Bengals odds data flow
"""
from src.kalshi_db_manager import KalshiDBManager
import psycopg2.extras

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
    for row in results:
        print(f"\nTicker: {row['ticker']}")
        print(f"Title: {row['title']}")
        print(f"Yes Price: {row['yes_price']:.4f} ({row['yes_price']*100:.1f}¢)")
        print(f"No Price: {row['no_price']:.4f} ({row['no_price']*100:.1f}¢)")
        print(f"Volume: ${row['volume']:,.0f}")
        print(f"Home Team: {row['home_team']}")
        print(f"Away Team: {row['away_team']}")

        # Parse ticker to identify which team is "yes"
        ticker = row['ticker']
        ticker_parts = ticker.split('-')
        print(f"Ticker parts: {ticker_parts}")
        if len(ticker_parts) > 1:
            ticker_suffix = ticker_parts[-1].upper()
            print(f"Ticker suffix (YES team): {ticker_suffix}")

        print("-" * 80)
else:
    print('\nNo Patriots/Bengals markets found')

# Now test the ESPN matcher logic
print("\n" + "=" * 80)
print("TESTING ESPN KALSHI MATCHER LOGIC")
print("=" * 80)

from src.espn_kalshi_matcher import ESPNKalshiMatcher

# Create a fake ESPN game
fake_espn_game = {
    'away_team': 'New England Patriots',
    'home_team': 'Cincinnati Bengals',
    'away_record': '9-2',
    'home_record': '3-7',
    'game_time': '2024-11-17 13:00:00'
}

matcher = ESPNKalshiMatcher()
result = matcher.match_game_to_kalshi(fake_espn_game)

if result:
    print(f"\n✅ MATCH FOUND:")
    print(f"Away Team (Patriots): {result['away_win_price']:.4f} ({result['away_win_price']*100:.1f}¢)")
    print(f"Home Team (Bengals): {result['home_win_price']:.4f} ({result['home_win_price']*100:.1f}¢)")
    print(f"Ticker: {result['ticker']}")
    print(f"Market Title: {result['market_title']}")
    print(f"\nINTERPRETATION:")
    if result['away_win_price'] > result['home_win_price']:
        print(f"  Patriots favored: {result['away_win_price']*100:.1f}% vs Bengals {result['home_win_price']*100:.1f}%")
    else:
        print(f"  Bengals favored: {result['home_win_price']*100:.1f}% vs Patriots {result['away_win_price']*100:.1f}%")
else:
    print("\n❌ NO MATCH FOUND")

cur.close()
conn.close()

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
