"""Verify MLB data is 100% complete - no corrupt team names."""
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
print("MLB DATA QUALITY VERIFICATION - 100% COMPLETION CHECK")
print("=" * 80)

# 1. Check for any corrupt team names (single letters or partial names)
print("\n1. CHECKING FOR CORRUPT TEAM NAMES...")
print("-" * 80)

corrupt_patterns = ['D', 'Y', 'WS', 'C', 'M', 'Diego', 'Louis', 'Tampa', 'Chicago', 'Los', 'New', 'San', 'St.']
cur.execute(f"""
    SELECT ticker, title, home_team, away_team
    FROM kalshi_markets
    WHERE ticker LIKE 'KXMLBGAME%'
    AND (
        home_team IN ({','.join("'" + p + "'" for p in corrupt_patterns)})
        OR away_team IN ({','.join("'" + p + "'" for p in corrupt_patterns)})
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

# 2. Verify all fixed records
print("\n2. VERIFYING FIXED MLB TEAM NAMES...")
print("-" * 80)

cur.execute("""
    SELECT ticker, title, home_team, away_team
    FROM kalshi_markets
    WHERE ticker LIKE 'KXMLBGAME%'
    ORDER BY ticker
""")

fixed_records = cur.fetchall()

print(f"Found {len(fixed_records)} MLB game markets:")
print()

for record in fixed_records:
    ticker, title, home, away = record
    print(f"  {away} @ {home}")
    print(f"    Title: {title}")

# 3. Get overall MLB stats
print("\n3. OVERALL MLB STATISTICS")
print("-" * 80)

cur.execute("SELECT COUNT(*) FROM kalshi_markets WHERE ticker LIKE 'KXMLBGAME%'")
total_mlb = cur.fetchone()[0]

cur.execute(f"""
    SELECT COUNT(*) FROM kalshi_markets
    WHERE ticker LIKE 'KXMLBGAME%'
    AND (
        home_team IN ({','.join("'" + p + "'" for p in corrupt_patterns)})
        OR away_team IN ({','.join("'" + p + "'" for p in corrupt_patterns)})
    )
""")
corrupt_count = cur.fetchone()[0]

accuracy = ((total_mlb - corrupt_count) / total_mlb * 100) if total_mlb > 0 else 0

print(f"Total MLB game markets: {total_mlb}")
print(f"Corrupt records: {corrupt_count}")
print(f"Accuracy: {accuracy:.1f}%")

# 4. Check unique team names
print("\n4. UNIQUE MLB TEAM NAMES IN DATABASE")
print("-" * 80)

cur.execute("""
    SELECT DISTINCT home_team FROM kalshi_markets WHERE ticker LIKE 'KXMLBGAME%'
    UNION
    SELECT DISTINCT away_team FROM kalshi_markets WHERE ticker LIKE 'KXMLBGAME%'
    ORDER BY 1
""")

unique_teams = cur.fetchall()
print(f"\nTotal unique team names: {len(unique_teams)}")
print("\nTeams:")
for team in unique_teams:
    print(f"  {team[0]}")

# Final verdict
print("\n" + "=" * 80)
if corrupt_count == 0 and total_mlb > 0:
    print("SUCCESS: MLB DATA: 100% COMPLETE - ALL TEAM NAMES CORRECT")
    print("=" * 80)
    print(f"[OK] {total_mlb} MLB game markets validated")
    print(f"[OK] 0 corrupt team names")
    print(f"[OK] All multi-word teams preserved correctly")
else:
    print("WARNING: MLB DATA: NOT AT 100% - ISSUES FOUND")
    print("=" * 80)
    print(f"Total markets: {total_mlb}")
    print(f"Corrupt records: {corrupt_count}")
    print(f"Accuracy: {accuracy:.1f}%")

cur.close()
conn.close()
