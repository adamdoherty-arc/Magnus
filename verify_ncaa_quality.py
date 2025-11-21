"""Verify NCAA data quality and identify remaining issues."""
import psycopg2
import os
from dotenv import load_dotenv
from collections import defaultdict

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
print("NCAA DATA QUALITY VERIFICATION")
print("=" * 80)

# Get total NCAA records
cur.execute("SELECT COUNT(*) FROM kalshi_markets WHERE ticker LIKE 'KXNCAAFGAME%'")
total_ncaa = cur.fetchone()[0]
print(f"\nTotal NCAA markets: {total_ncaa}")

# 1. Check for obviously corrupt single-word team names
print("\n" + "=" * 80)
print("1. CHECKING FOR CORRUPT SINGLE-WORD TEAM NAMES")
print("=" * 80)

corrupt_patterns = ['State', 'Tech', 'Carolina', 'College', 'Southern', 'Northern', 'Eastern', 'Western']
cur.execute(f"""
    SELECT ticker, title, home_team, away_team
    FROM kalshi_markets
    WHERE ticker LIKE 'KXNCAAFGAME%'
    AND (
        home_team IN ({','.join("'" + p + "'" for p in corrupt_patterns)})
        OR away_team IN ({','.join("'" + p + "'" for p in corrupt_patterns)})
    )
    LIMIT 10
""")

corrupt_records = cur.fetchall()
if corrupt_records:
    print(f"\n[WARN] Found {len(corrupt_records)} records with corrupt single-word names:")
    for record in corrupt_records[:10]:
        ticker, title, home, away = record
        print(f"  Ticker: {ticker}")
        print(f"  Title: {title}")
        print(f"  Home: {home} | Away: {away}")
        print()
else:
    print("\n[OK] No corrupt single-word names found")

# 2. Group all team names to identify patterns
print("\n" + "=" * 80)
print("2. ALL NCAA TEAM NAMES IN DATABASE")
print("=" * 80)

cur.execute("""
    SELECT DISTINCT home_team FROM kalshi_markets WHERE ticker LIKE 'KXNCAAFGAME%'
    UNION
    SELECT DISTINCT away_team FROM kalshi_markets WHERE ticker LIKE 'KXNCAAFGAME%'
    ORDER BY 1
""")

all_teams = [row[0] for row in cur.fetchall()]
print(f"\nTotal unique team names: {len(all_teams)}")
print("\nTeam names:")
for team in all_teams:
    print(f"  {team}")

# 3. Check for teams that might be missing parts
print("\n" + "=" * 80)
print("3. POTENTIALLY INCOMPLETE TEAM NAMES (< 5 chars or single word)")
print("=" * 80)

suspicious_teams = []
for team in all_teams:
    if len(team) < 5 or ' ' not in team:
        suspicious_teams.append(team)

if suspicious_teams:
    print(f"\n[WARN] Found {len(suspicious_teams)} potentially incomplete team names:")
    for team in suspicious_teams:
        # Count how many records use this team name
        cur.execute("""
            SELECT COUNT(*) FROM kalshi_markets
            WHERE ticker LIKE 'KXNCAAFGAME%'
            AND (home_team = %s OR away_team = %s)
        """, (team, team))
        count = cur.fetchone()[0]
        print(f"  '{team}' ({count} records)")

        # Show a sample title to understand what the full name should be
        cur.execute("""
            SELECT title FROM kalshi_markets
            WHERE ticker LIKE 'KXNCAAFGAME%'
            AND (home_team = %s OR away_team = %s)
            LIMIT 1
        """, (team, team))
        sample_title = cur.fetchone()
        if sample_title:
            print(f"    Sample title: {sample_title[0]}")
else:
    print("\n[OK] No suspicious team names found")

# 4. Check accuracy by comparing title to stored names
print("\n" + "=" * 80)
print("4. TITLE vs STORED NAME VALIDATION (Sample)")
print("=" * 80)

cur.execute("""
    SELECT ticker, title, home_team, away_team
    FROM kalshi_markets
    WHERE ticker LIKE 'KXNCAAFGAME%'
    ORDER BY RANDOM()
    LIMIT 20
""")

validation_results = {'matches': 0, 'mismatches': 0}
for record in cur.fetchall():
    ticker, title, home, away = record
    title_lower = title.lower()

    # Check if stored team names appear in title
    home_in_title = home.lower() in title_lower
    away_in_title = away.lower() in title_lower

    if home_in_title and away_in_title:
        validation_results['matches'] += 1
        print(f"  [OK] {away} @ {home}")
    else:
        validation_results['mismatches'] += 1
        print(f"  [ERROR] Mismatch!")
        print(f"    Title: {title}")
        print(f"    Stored: {away} @ {home}")
        print(f"    Home in title: {home_in_title}, Away in title: {away_in_title}")

# 5. Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Total NCAA markets: {total_ncaa}")
print(f"Unique team names: {len(all_teams)}")
print(f"Potentially incomplete names: {len(suspicious_teams)}")
print(f"Sample validation - Matches: {validation_results['matches']}, Mismatches: {validation_results['mismatches']}")

estimated_accuracy = (validation_results['matches'] / 20 * 100) if validation_results['matches'] > 0 else 0
print(f"\nEstimated accuracy: {estimated_accuracy:.1f}%")

if estimated_accuracy >= 95:
    print("[OK] NCAA data quality is GOOD (>= 95%)")
elif estimated_accuracy >= 85:
    print("[WARN] NCAA data quality is FAIR (85-95%)")
else:
    print("[ERROR] NCAA data quality is POOR (< 85%)")

cur.close()
conn.close()
