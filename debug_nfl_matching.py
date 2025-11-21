"""Debug NFL team name matching between ESPN and Kalshi"""
import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

# Get ESPN data first
from src.espn_live_data import get_espn_client

print("=" * 80)
print("ESPN NFL GAMES")
print("=" * 80)

espn = get_espn_client()
games = espn.get_scoreboard()

print(f"\nFetched {len(games)} games from ESPN\n")

# Show first 3 games with their exact team names
for i, game in enumerate(games[:3], 1):
    print(f"{i}. {game['away_team']} @ {game['home_team']}")
    print(f"   Game time: {game.get('game_time')}")
    print(f"   Status: {game.get('status_detail')}")
    print()

# Now check Kalshi for those exact teams
conn = psycopg2.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    port=os.getenv('DB_PORT', '5432'),
    database=os.getenv('DB_NAME', 'magnus'),
    user=os.getenv('DB_USER', 'postgres'),
    password=os.getenv('DB_PASSWORD', ''),
)

cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

print("=" * 80)
print("KALSHI MARKETS FOR THESE TEAMS")
print("=" * 80)

for i, game in enumerate(games[:3], 1):
    away = game['away_team']
    home = game['home_team']

    print(f"\n{i}. Searching for: {away} @ {home}")

    # Try exact match
    cur.execute("""
        SELECT ticker, title, home_team, away_team, close_time, yes_price, no_price
        FROM kalshi_markets
        WHERE status != 'closed'
          AND raw_data->>'market_type' = 'nfl'
          AND (
              title ILIKE %s
              OR title ILIKE %s
          )
        ORDER BY close_time ASC
        LIMIT 3
    """, (f'%{away}%', f'%{home}%'))

    markets = cur.fetchall()

    if markets:
        print(f"   Found {len(markets)} markets:")
        for m in markets:
            print(f"   - {m['title']}")
            print(f"     Ticker: {m['ticker']}")
            print(f"     DB Teams: {m['home_team']} / {m['away_team']}")
            print(f"     Close: {m['close_time']}")
    else:
        print("   NO MARKETS FOUND")

        # Try just the city name
        away_city = away.split()[0] if ' ' in away else away
        home_city = home.split()[0] if ' ' in home else home

        print(f"\n   Trying city names: {away_city} / {home_city}")

        cur.execute("""
            SELECT ticker, title, home_team, away_team, close_time
            FROM kalshi_markets
            WHERE status != 'closed'
              AND raw_data->>'market_type' = 'nfl'
              AND (
                  title ILIKE %s
                  OR title ILIKE %s
              )
            ORDER BY close_time ASC
            LIMIT 3
        """, (f'%{away_city}%', f'%{home_city}%'))

        markets = cur.fetchall()
        if markets:
            print(f"   Found {len(markets)} markets with city names:")
            for m in markets:
                print(f"   - {m['title']}")
                print(f"     DB Teams: {m['home_team']} / {m['away_team']}")
        else:
            print("   STILL NO MARKETS FOUND")

# Show all NFL markets available
print("\n" + "=" * 80)
print("ALL AVAILABLE NFL MARKETS")
print("=" * 80)

cur.execute("""
    SELECT ticker, title, home_team, away_team, close_time
    FROM kalshi_markets
    WHERE status != 'closed'
      AND raw_data->>'market_type' = 'nfl'
    ORDER BY close_time ASC
    LIMIT 10
""")

all_markets = cur.fetchall()
print(f"\nTotal NFL markets: {len(all_markets)}\n")

for m in all_markets:
    print(f"{m['title']}")
    print(f"  Teams in DB: Home={m['home_team']} / Away={m['away_team']}")
    print(f"  Close: {m['close_time']}")
    print()

cur.close()
conn.close()
