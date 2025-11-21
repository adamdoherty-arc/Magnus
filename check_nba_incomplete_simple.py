"""Simple check for incomplete NBA team names."""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    port=os.getenv('DB_PORT', '5432'),
    database=os.getenv('DB_NAME', 'magnus'),
    user=os.getenv('DB_USER', 'postgres'),
    password=os.getenv('DB_PASSWORD', '')
)
cur = conn.cursor()

print("=" * 80)
print("CHECKING FOR INCOMPLETE NBA TEAM NAMES")
print("=" * 80)

# Check for "Oklahoma" without "City Thunder"
print("\nChecking for 'Oklahoma' (should be 'Oklahoma City Thunder')...")
cur.execute("""
    SELECT ticker, title, home_team, away_team
    FROM kalshi_markets
    WHERE ticker LIKE 'KXNBAGAME%'
    AND (home_team = 'Oklahoma' OR away_team = 'Oklahoma')
""")
results = cur.fetchall()
if results:
    print(f"  [WARN] Found {len(results)} records:")
    for record in results:
        ticker, title, home, away = record
        print(f"    {away} @ {home} (Ticker: {ticker})")
else:
    print("  [OK] No incomplete 'Oklahoma' found")

# Check for "New York" without team name
print("\nChecking for 'New York' (should be 'New York Knicks' or 'Brooklyn Nets')...")
cur.execute("""
    SELECT ticker, title, home_team, away_team
    FROM kalshi_markets
    WHERE ticker LIKE 'KXNBAGAME%'
    AND (home_team = 'New York' OR away_team = 'New York')
""")
results = cur.fetchall()
if results:
    print(f"  [WARN] Found {len(results)} records:")
    for record in results:
        ticker, title, home, away = record
        print(f"    {away} @ {home} (Ticker: {ticker})")
else:
    print("  [OK] No incomplete 'New York' found")

# Check all teams with multi-word names to see if any are incomplete
print("\n" + "=" * 80)
print("ALL NBA GAMES - SAMPLE CHECK")
print("=" * 80)
cur.execute("""
    SELECT home_team, COUNT(*) as count
    FROM kalshi_markets
    WHERE ticker LIKE 'KXNBAGAME%'
    GROUP BY home_team
    ORDER BY home_team
""")
home_teams = cur.fetchall()

print("\nHome teams in database:")
for team, count in home_teams:
    print(f"  {team}: {count} games")

cur.execute("""
    SELECT away_team, COUNT(*) as count
    FROM kalshi_markets
    WHERE ticker LIKE 'KXNBAGAME%'
    GROUP BY away_team
    ORDER BY away_team
""")
away_teams = cur.fetchall()

print("\nAway teams in database:")
for team, count in away_teams:
    print(f"  {team}: {count} games")

cur.close()
conn.close()
