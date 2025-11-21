"""Check for any incomplete NBA team names."""
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

# Check for teams that might be incomplete (too short or missing key words)
suspicious_patterns = [
    ("Oklahoma", "Oklahoma City Thunder"),
    ("Golden State", "Golden State Warriors"),
    ("San Antonio", "San Antonio Spurs"),
    ("Los Angeles", "Los Angeles Lakers OR Los Angeles Clippers"),
    ("New Orleans", "New Orleans Pelicans"),
    ("New York", "New York Knicks OR New York Nets")
]

for short_name, full_name in suspicious_patterns:
    print(f"\n{'-' * 80}")
    print(f"Checking for incomplete '{short_name}' (should be {full_name})...")
    print(f"{'-' * 80}")

    # Check home team
    cur.execute("""
        SELECT ticker, title, home_team, away_team
        FROM kalshi_markets
        WHERE ticker LIKE 'KXNBAGAME%'
        AND home_team = %s
    """, (short_name,))

    home_results = cur.fetchall()
    if home_results:
        print(f"  [WARN] Found {len(home_results)} records with HOME team = '{short_name}':")
        for record in home_results[:5]:  # Show first 5
            ticker, title, home, away = record
            print(f"    Ticker: {ticker}")
            print(f"    Title: {title}")
            print(f"    Home: {home} | Away: {away}")

    # Check away team
    cur.execute("""
        SELECT ticker, title, home_team, away_team
        FROM kalshi_markets
        WHERE ticker LIKE 'KXNBAGAME%'
        AND away_team = %s
    """, (short_name,))

    away_results = cur.fetchall()
    if away_results:
        print(f"  [WARN] Found {len(away_results)} records with AWAY team = '{short_name}':")
        for record in away_results[:5]:  # Show first 5
            ticker, title, home, away = record
            print(f"    Ticker: {ticker}")
            print(f"    Title: {title}")
            print(f"    Home: {home} | Away: {away}")

    if not home_results and not away_results:
        print(f"  [OK] No incomplete '{short_name}' found")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

# Get total count of records with multi-word team names that might be incomplete
cur.execute("""
    SELECT COUNT(*) FROM kalshi_markets
    WHERE ticker LIKE 'KXNBAGAME%'
    AND (
        home_team IN ('Oklahoma', 'Golden State', 'San Antonio', 'Los Angeles', 'New Orleans', 'New York')
        OR away_team IN ('Oklahoma', 'Golden State', 'San Antonio', 'Los Angeles', 'New Orleans', 'New York')
    )
""")

incomplete_count = cur.fetchone()[0]
print(f"Total records with potentially incomplete team names: {incomplete_count}")

cur.close()
conn.close()
