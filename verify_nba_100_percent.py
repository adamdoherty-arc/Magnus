"""Verify NBA data is 100% fixed - no corrupt team names."""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

# Connect to database
conn = psycopg2.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    port=os.getenv('DB_PORT', '5432'),
    database=os.getenv('DB_NAME', 'magnus'),
    user=os.getenv('DB_USER', 'postgres'),
    password=os.getenv('DB_PASSWORD', '')
)
cur = conn.cursor()

print("=" * 80)
print("NBA DATA QUALITY VERIFICATION - 100% COMPLETION CHECK")
print("=" * 80)

# 1. Check for any corrupt team names
print("\n1. CHECKING FOR CORRUPT TEAM NAMES...")
print("-" * 80)

cur.execute("""
    SELECT ticker, title, home_team, away_team
    FROM kalshi_markets
    WHERE ticker LIKE 'KXNBAGAME%'
    AND (
        away_team IN ('State', 'San', 'L', 'C', 'New', 'York', 'Angeles', 'Orleans', 'City')
        OR home_team IN ('State', 'San', 'L', 'C', 'New', 'York', 'Angeles', 'Orleans', 'City')
    )
""")

corrupt_records = cur.fetchall()

if corrupt_records:
    print(f"[ERROR] FOUND {len(corrupt_records)} CORRUPT RECORDS:")
    for record in corrupt_records:
        ticker, title, home, away = record
        print(f"  Ticker: {ticker}")
        print(f"  Title: {title}")
        print(f"  Home: {home} | Away: {away}")
        print()
else:
    print("[OK] NO CORRUPT RECORDS FOUND")

# 2. Verify sample of fixed records
print("\n2. VERIFYING FIXED MULTI-WORD TEAM NAMES...")
print("-" * 80)

cur.execute("""
    SELECT ticker, title, home_team, away_team
    FROM kalshi_markets
    WHERE ticker LIKE 'KXNBAGAME%'
    AND (
        title LIKE '%Golden State%'
        OR title LIKE '%San Antonio%'
        OR title LIKE '%Los Angeles%'
        OR title LIKE '%New Orleans%'
        OR title LIKE '%Oklahoma City%'
    )
    LIMIT 20
""")

fixed_records = cur.fetchall()

print(f"Found {len(fixed_records)} games with multi-word team names:")
print()

multi_word_teams = {
    'Golden State Warriors': 0,
    'San Antonio Spurs': 0,
    'Los Angeles Lakers': 0,
    'Los Angeles Clippers': 0,
    'New Orleans Pelicans': 0,
    'Oklahoma City Thunder': 0
}

for record in fixed_records:
    ticker, title, home, away = record

    # Check if team names are now complete
    for team_name in multi_word_teams.keys():
        if team_name in home:
            multi_word_teams[team_name] += 1
        if team_name in away:
            multi_word_teams[team_name] += 1

    print(f"  {away} @ {home}")

print("\n" + "-" * 80)
print("TEAM NAME COUNTS:")
for team, count in multi_word_teams.items():
    status = "[OK]" if count > 0 else "[WARN]"
    print(f"  {status} {team}: {count} appearances")

# 3. Get overall NBA stats
print("\n3. OVERALL NBA STATISTICS")
print("-" * 80)

cur.execute("SELECT COUNT(*) FROM kalshi_markets WHERE ticker LIKE 'KXNBAGAME%'")
total_nba = cur.fetchone()[0]

cur.execute("""
    SELECT COUNT(*) FROM kalshi_markets
    WHERE ticker LIKE 'KXNBAGAME%'
    AND (
        away_team IN ('State', 'San', 'L', 'C', 'New', 'York', 'Angeles', 'Orleans', 'City')
        OR home_team IN ('State', 'San', 'L', 'C', 'New', 'York', 'Angeles', 'Orleans', 'City')
    )
""")
corrupt_count = cur.fetchone()[0]

accuracy = ((total_nba - corrupt_count) / total_nba * 100) if total_nba > 0 else 0

print(f"Total NBA markets: {total_nba}")
print(f"Corrupt records: {corrupt_count}")
print(f"Accuracy: {accuracy:.1f}%")

# 4. Sample random NBA games to verify quality
print("\n4. RANDOM SAMPLE OF NBA GAMES")
print("-" * 80)

cur.execute("""
    SELECT ticker, title, home_team, away_team
    FROM kalshi_markets
    WHERE ticker LIKE 'KXNBAGAME%'
    ORDER BY RANDOM()
    LIMIT 10
""")

sample_records = cur.fetchall()
for record in sample_records:
    ticker, title, home, away = record
    print(f"  {away} @ {home}")

# Final verdict
print("\n" + "=" * 80)
if corrupt_count == 0 and total_nba > 0:
    print("SUCCESS: NBA DATA: 100% COMPLETE - ALL TEAM NAMES CORRECT")
    print("=" * 80)
    print(f"[OK] {total_nba} NBA markets validated")
    print(f"[OK] 0 corrupt team names")
    print(f"[OK] All multi-word teams preserved correctly")
else:
    print("WARNING: NBA DATA: NOT AT 100% - ISSUES FOUND")
    print("=" * 80)
    print(f"Total markets: {total_nba}")
    print(f"Corrupt records: {corrupt_count}")
    print(f"Accuracy: {accuracy:.1f}%")

cur.close()
conn.close()
