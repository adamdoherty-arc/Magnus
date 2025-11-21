"""
Database Fix Script - Correct Team Names in kalshi_markets Table
Fixes Bug #1: Team name parsing errors causing wrong team storage
"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def fix_team_names():
    """Fix incorrectly parsed team names in kalshi_markets table"""

    # Database connection
    conn = psycopg2.connect(
        host='localhost',
        port='5432',
        database='magnus',
        user='postgres',
        password=os.getenv('DB_PASSWORD')
    )
    cur = conn.cursor()

    print("=" * 80)
    print("FIXING TEAM NAMES IN kalshi_markets TABLE")
    print("=" * 80)

    # Fix 1: "England" → "New England"
    print("\n1. Fixing 'England' → 'New England'...")
    cur.execute("""
        UPDATE kalshi_markets
        SET away_team = 'New England'
        WHERE away_team = 'England'
          AND (title ILIKE '%New England%' OR title ILIKE '%Patriots%')
    """)
    rows_updated = cur.rowcount
    print(f"   Updated {rows_updated} rows")

    # Fix 2: "Los Angeles" needs disambiguation
    print("\n2. Checking 'Los Angeles' teams (Rams vs Chargers)...")
    cur.execute("""
        SELECT ticker, title, home_team, away_team
        FROM kalshi_markets
        WHERE (home_team = 'Los Angeles' OR away_team = 'Los Angeles')
          AND title ILIKE '%angeles%'
        LIMIT 5
    """)
    la_teams = cur.fetchall()
    for row in la_teams:
        ticker, title, home_team, away_team = row
        print(f"   {ticker}: {title}")
        print(f"     Home: {home_team}, Away: {away_team}")

        # Check if Rams or Chargers
        if 'rams' in title.lower():
            if home_team == 'Los Angeles':
                cur.execute("UPDATE kalshi_markets SET home_team = 'Los Angeles Rams' WHERE ticker = %s", (ticker,))
            if away_team == 'Los Angeles':
                cur.execute("UPDATE kalshi_markets SET away_team = 'Los Angeles Rams' WHERE ticker = %s", (ticker,))
            print(f"     → Fixed to 'Los Angeles Rams'")
        elif 'chargers' in title.lower():
            if home_team == 'Los Angeles':
                cur.execute("UPDATE kalshi_markets SET home_team = 'Los Angeles Chargers' WHERE ticker = %s", (ticker,))
            if away_team == 'Los Angeles':
                cur.execute("UPDATE kalshi_markets SET away_team = 'Los Angeles Chargers' WHERE ticker = %s", (ticker,))
            print(f"     → Fixed to 'Los Angeles Chargers'")

    # Fix 3: "New York" needs disambiguation (Giants vs Jets)
    print("\n3. Checking 'New York' teams (Giants vs Jets)...")
    cur.execute("""
        SELECT ticker, title, home_team, away_team
        FROM kalshi_markets
        WHERE (home_team = 'New York' OR away_team = 'New York' OR home_team = 'York' OR away_team = 'York')
          AND title ILIKE '%york%'
        LIMIT 5
    """)
    ny_teams = cur.fetchall()
    for row in ny_teams:
        ticker, title, home_team, away_team = row
        print(f"   {ticker}: {title}")
        print(f"     Home: {home_team}, Away: {away_team}")

        # Check if Giants or Jets
        if 'giants' in title.lower():
            if home_team in ['New York', 'York']:
                cur.execute("UPDATE kalshi_markets SET home_team = 'New York Giants' WHERE ticker = %s", (ticker,))
            if away_team in ['New York', 'York']:
                cur.execute("UPDATE kalshi_markets SET away_team = 'New York Giants' WHERE ticker = %s", (ticker,))
            print(f"     → Fixed to 'New York Giants'")
        elif 'jets' in title.lower():
            if home_team in ['New York', 'York']:
                cur.execute("UPDATE kalshi_markets SET home_team = 'New York Jets' WHERE ticker = %s", (ticker,))
            if away_team in ['New York', 'York']:
                cur.execute("UPDATE kalshi_markets SET away_team = 'New York Jets' WHERE ticker = %s", (ticker,))
            print(f"     → Fixed to 'New York Jets'")

    # Fix 4: "Bay" → "Tampa Bay" or "Green Bay"
    print("\n4. Fixing 'Bay' → 'Tampa Bay' or 'Green Bay'...")
    cur.execute("""
        SELECT ticker, title, home_team, away_team
        FROM kalshi_markets
        WHERE (home_team = 'Bay' OR away_team = 'Bay')
          AND (title ILIKE '%Tampa%' OR title ILIKE '%Green%')
    """)
    bay_teams = cur.fetchall()
    for row in bay_teams:
        ticker, title, home_team, away_team = row
        if 'tampa' in title.lower():
            if home_team == 'Bay':
                cur.execute("UPDATE kalshi_markets SET home_team = 'Tampa Bay' WHERE ticker = %s", (ticker,))
            if away_team == 'Bay':
                cur.execute("UPDATE kalshi_markets SET away_team = 'Tampa Bay' WHERE ticker = %s", (ticker,))
            print(f"   {ticker}: Fixed 'Bay' → 'Tampa Bay'")
        elif 'green' in title.lower():
            if home_team == 'Bay':
                cur.execute("UPDATE kalshi_markets SET home_team = 'Green Bay' WHERE ticker = %s", (ticker,))
            if away_team == 'Bay':
                cur.execute("UPDATE kalshi_markets SET away_team = 'Green Bay' WHERE ticker = %s", (ticker,))
            print(f"   {ticker}: Fixed 'Bay' → 'Green Bay'")

    # Fix 5: "Kansas" → "Kansas City"
    print("\n5. Fixing 'Kansas' → 'Kansas City'...")
    cur.execute("""
        UPDATE kalshi_markets
        SET home_team = 'Kansas City',
            away_team = CASE WHEN away_team = 'Kansas' THEN 'Kansas City' ELSE away_team END
        WHERE home_team = 'Kansas'
          AND title ILIKE '%Kansas City%'
    """)
    cur.execute("""
        UPDATE kalshi_markets
        SET away_team = 'Kansas City',
            home_team = CASE WHEN home_team = 'Kansas' THEN 'Kansas City' ELSE home_team END
        WHERE away_team = 'Kansas'
          AND title ILIKE '%Kansas City%'
    """)
    rows_updated = cur.rowcount
    print(f"   Updated {rows_updated} rows")

    # Fix 6: "Las" → "Las Vegas"
    print("\n6. Fixing 'Las' → 'Las Vegas'...")
    cur.execute("""
        UPDATE kalshi_markets
        SET home_team = 'Las Vegas',
            away_team = CASE WHEN away_team = 'Las' THEN 'Las Vegas' ELSE away_team END
        WHERE home_team = 'Las'
          AND title ILIKE '%Las Vegas%'
    """)
    cur.execute("""
        UPDATE kalshi_markets
        SET away_team = 'Las Vegas',
            home_team = CASE WHEN home_team = 'Las' THEN 'Las Vegas' ELSE home_team END
        WHERE away_team = 'Las'
          AND title ILIKE '%Las Vegas%'
    """)
    rows_updated = cur.rowcount
    print(f"   Updated {rows_updated} rows")

    # Commit changes
    conn.commit()

    # Verify fixes
    print("\n" + "=" * 80)
    print("VERIFICATION - Checking Patriots vs Bengals market")
    print("=" * 80)
    cur.execute("""
        SELECT ticker, title, home_team, away_team, yes_price, no_price
        FROM kalshi_markets
        WHERE title ILIKE '%england%' AND title ILIKE '%cincinnati%'
        ORDER BY volume DESC
        LIMIT 1
    """)
    result = cur.fetchone()
    if result:
        ticker, title, home_team, away_team, yes_price, no_price = result
        print(f"\nTicker: {ticker}")
        print(f"Title: {title}")
        print(f"Home Team: {home_team} (should be 'Cincinnati')")
        print(f"Away Team: {away_team} (should be 'New England')")
        print(f"Yes Price: {yes_price:.2f}, No Price: {no_price:.2f}")

        if away_team == 'New England':
            print("\n✓ SUCCESS: Team names are now correct!")
        else:
            print(f"\n✗ WARNING: Away team is still '{away_team}' (expected 'New England')")
    else:
        print("\n✗ No market found for verification")

    cur.close()
    conn.close()

    print("\n" + "=" * 80)
    print("DATABASE FIX COMPLETE")
    print("=" * 80)
    print("\nNEXT STEPS:")
    print("1. Re-run sync_kalshi_team_winners.py to fetch new markets with fixed parser")
    print("2. Test ESPN matcher with: python test_patriots_bengals_odds_simple.py")
    print("3. Verify odds display correctly in game cards UI")


if __name__ == "__main__":
    fix_team_names()
