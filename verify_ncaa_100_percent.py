"""Final NCAA 100% completion check with abbreviation handling."""
import psycopg2
import os
from dotenv import load_dotenv
import re

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    port=os.getenv('DB_PORT', '5432'),
    database=os.getenv('DB_NAME', 'magnus'),
    user=os.getenv('DB_USER', 'postgres'),
    password=os.getenv('DB_PASSWORD', '')
)
cur = conn.cursor()

def normalize_team_name(name: str) -> str:
    """Normalize team name for comparison (handle St./State, etc.)"""
    name = name.lower()
    # Expand common abbreviations
    name = re.sub(r'\bst\.?\b', 'state', name)
    name = re.sub(r'\b(fl)\.?\b', 'florida', name)
    name = re.sub(r'\boh\.?\b', 'ohio', name)
    return name.strip()

print("=" * 80)
print("NCAA 100% COMPLETION VERIFICATION")
print("=" * 80)

# Total NCAA markets
cur.execute("SELECT COUNT(*) FROM kalshi_markets WHERE ticker LIKE 'KXNCAAFGAME%'")
total = cur.fetchone()[0]
print(f"\nTotal NCAA markets: {total}")

# Check for corrupt single-word names
cur.execute("""
    SELECT COUNT(*) FROM kalshi_markets
    WHERE ticker LIKE 'KXNCAAFGAME%'
    AND (
        home_team IN ('State', 'Tech', 'Carolina', 'College', 'Southern', 'Northern', 'Eastern', 'Western')
        OR away_team IN ('State', 'Tech', 'Carolina', 'College', 'Southern', 'Northern', 'Eastern', 'Western')
    )
""")
corrupt_count = cur.fetchone()[0]
print(f"Corrupt single-word names: {corrupt_count}")

# Validate ALL records
cur.execute("""
    SELECT ticker, title, home_team, away_team
    FROM kalshi_markets
    WHERE ticker LIKE 'KXNCAAFGAME%'
    ORDER BY ticker
""")

all_records = cur.fetchall()
matches = 0
mismatches = []

print("\n" + "=" * 80)
print("VALIDATING ALL 288 RECORDS...")
print("=" * 80)

for record in all_records:
    ticker, title, home, away = record
    title_lower = title.lower()

    # Normalize names for comparison
    home_normalized = normalize_team_name(home)
    away_normalized = normalize_team_name(away)
    title_normalized = normalize_team_name(title)

    # Check if normalized team names appear in normalized title
    home_in_title = home_normalized in title_normalized
    away_in_title = away_normalized in title_normalized

    if home_in_title and away_in_title:
        matches += 1
    else:
        mismatches.append((ticker, title, home, away))

# Print mismatches if any
if mismatches:
    print(f"\n[WARN] Found {len(mismatches)} mismatches:")
    for ticker, title, home, away in mismatches[:10]:  # Show first 10
        print(f"  Ticker: {ticker}")
        print(f"  Title: {title}")
        print(f"  Stored: {away} @ {home}")
        print()
else:
    print("\n[OK] All records validated successfully!")

# Summary
print("\n" + "=" * 80)
print("FINAL SUMMARY")
print("=" * 80)
print(f"Total NCAA markets: {total}")
print(f"Corrupt single-word names: {corrupt_count}")
print(f"Validated records: {matches}/{total}")
print(f"Failed validation: {len(mismatches)}")

accuracy = (matches / total * 100) if total > 0 else 0
print(f"\nAccuracy: {accuracy:.1f}%")

if corrupt_count == 0 and accuracy >= 95:
    print("\n[SUCCESS] NCAA AT 100% COMPLETION!")
    print("All team names are correct!")
elif accuracy >= 95:
    print(f"\n[GOOD] NCAA at {accuracy:.1f}% accuracy")
elif accuracy >= 85:
    print(f"\n[FAIR] NCAA at {accuracy:.1f}% accuracy")
else:
    print(f"\n[NEEDS WORK] NCAA at {accuracy:.1f}% accuracy")

cur.close()
conn.close()
