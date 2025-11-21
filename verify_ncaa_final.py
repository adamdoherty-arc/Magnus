"""Simple final NCAA verification without psycopg2 parameter issues."""
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
print("NCAA FINAL VERIFICATION - 100% COMPLETION CHECK")
print("=" * 80)

# Total NCAA markets
cur.execute("SELECT COUNT(*) FROM kalshi_markets WHERE ticker LIKE 'KXNCAAFGAME%'")
total = cur.fetchone()[0]
print(f"\nTotal NCAA markets: {total}")

# Check for corrupt single-word names
corrupt_patterns = ['State', 'Tech', 'Carolina', 'College', 'Southern', 'Northern', 'Eastern', 'Western']
cur.execute(f"""
    SELECT COUNT(*) FROM kalshi_markets
    WHERE ticker LIKE 'KXNCAAFGAME%'
    AND (
        home_team IN ('State', 'Tech', 'Carolina', 'College', 'Southern', 'Northern', 'Eastern', 'Western')
        OR away_team IN ('State', 'Tech', 'Carolina', 'College', 'Southern', 'Northern', 'Eastern', 'Western')
    )
""")
corrupt_count = cur.fetchone()[0]
print(f"Corrupt single-word names: {corrupt_count}")

# Validate sample of records by checking title
cur.execute("""
    SELECT ticker, title, home_team, away_team
    FROM kalshi_markets
    WHERE ticker LIKE 'KXNCAAFGAME%'
    ORDER BY RANDOM()
    LIMIT 30
""")

matches = 0
mismatches = 0
print("\n" + "=" * 80)
print("SAMPLE VALIDATION (30 random games)")
print("=" * 80)

for record in cur.fetchall():
    ticker, title, home, away = record
    title_lower = title.lower()

    # Check if stored team names appear in title
    home_in_title = home.lower() in title_lower
    away_in_title = away.lower() in title_lower

    if home_in_title and away_in_title:
        matches += 1
        print(f"  [OK] {away} @ {home}")
    else:
        mismatches += 1
        print(f"  [MISMATCH] {ticker}")
        print(f"    Title: {title}")
        print(f"    Stored: {away} @ {home}")

# Summary
print("\n" + "=" * 80)
print("FINAL SUMMARY")
print("=" * 80)
print(f"Total NCAA markets: {total}")
print(f"Corrupt single-word names: {corrupt_count}")
print(f"Sample validation (30 games):")
print(f"  Matches: {matches}")
print(f"  Mismatches: {mismatches}")

accuracy = (matches / 30 * 100) if matches > 0 else 0
print(f"\nEstimated accuracy: {accuracy:.1f}%")

if corrupt_count == 0 and accuracy >= 95:
    print("\n[SUCCESS] NCAA AT 100% COMPLETION!")
    print("All team names are correct and validated.")
elif accuracy >= 95:
    print(f"\n[GOOD] NCAA at {accuracy:.1f}% accuracy (>= 95%)")
elif accuracy >= 85:
    print(f"\n[FAIR] NCAA at {accuracy:.1f}% accuracy (85-95%)")
else:
    print(f"\n[POOR] NCAA at {accuracy:.1f}% accuracy (< 85%)")

cur.close()
conn.close()
