"""Complete MLB team name fix based on ticker abbreviations."""
import psycopg2
import os
import re
from dotenv import load_dotenv
import json
from datetime import datetime

load_dotenv()

# MLB team mapping from ticker abbreviations to full names
MLB_TEAM_MAPPING = {
    # American League East
    'BAL': 'Baltimore Orioles',
    'BOS': 'Boston Red Sox',
    'NYY': 'New York Yankees',
    'TB': 'Tampa Bay Rays',
    'TOR': 'Toronto Blue Jays',

    # American League Central
    'CWS': 'Chicago White Sox',
    'CLE': 'Cleveland Guardians',
    'DET': 'Detroit Tigers',
    'KC': 'Kansas City Royals',
    'MIN': 'Minnesota Twins',

    # American League West
    'HOU': 'Houston Astros',
    'LAA': 'Los Angeles Angels',
    'OAK': 'Oakland Athletics',
    'ATH': 'Oakland Athletics',  # Alternate
    'SEA': 'Seattle Mariners',
    'TEX': 'Texas Rangers',

    # National League East
    'ATL': 'Atlanta Braves',
    'MIA': 'Miami Marlins',
    'NYM': 'New York Mets',
    'PHI': 'Philadelphia Phillies',
    'WSH': 'Washington Nationals',

    # National League Central
    'CHC': 'Chicago Cubs',
    'CIN': 'Cincinnati Reds',
    'MIL': 'Milwaukee Brewers',
    'PIT': 'Pittsburgh Pirates',
    'STL': 'St. Louis Cardinals',

    # National League West
    'AZ': 'Arizona Diamondbacks',
    'COL': 'Colorado Rockies',
    'LAD': 'Los Angeles Dodgers',
    'SD': 'San Diego Padres',
    'SF': 'San Francisco Giants',
}

def parse_mlb_ticker_teams(ticker: str) -> tuple:
    """
    Extract team abbreviations from MLB ticker.

    Examples:
        KXMLBGAME-25APR18ATHMIL-ATH → (ATH, MIL) → (Oakland Athletics, Milwaukee Brewers)
        KXMLBGAME-25APR18AZCHC-AZ → (AZ, CHC) → (Arizona Diamondbacks, Chicago Cubs)
        KXMLBGAME-25APR18LADTEX-LAD → (LAD, TEX) → (Los Angeles Dodgers, Texas Rangers)

    Args:
        ticker: Kalshi MLB market ticker

    Returns:
        Tuple of (away_team_abbr, home_team_abbr) or (None, None) if parsing fails
    """
    # Pattern: KXMLBGAME-DDmmmYYTEAMS-RESULT
    # Extract the concatenated team string after the date
    match = re.search(r'KXMLBGAME-\d{2}[A-Z]{3}\d{2}([A-Z]+)-', ticker)

    if not match:
        return None, None

    teams_str = match.group(1)

    # Try all possible split points to find valid team abbreviations
    for i in range(2, len(teams_str)):
        team1 = teams_str[:i]
        team2 = teams_str[i:]

        # Check if both are valid MLB team abbreviations
        if (2 <= len(team1) <= 3 and 2 <= len(team2) <= 3):
            if team1 in MLB_TEAM_MAPPING and team2 in MLB_TEAM_MAPPING:
                # Return in order: team1 = away, team2 = home
                return (team1, team2)

    return None, None

def fix_mlb_team_names():
    """Fix all MLB team names in database based on ticker abbreviations."""

    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        database=os.getenv('DB_NAME', 'magnus'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', '')
    )
    cur = conn.cursor()

    print("=" * 80)
    print("MLB TEAM NAME FIX - COMPREHENSIVE REPAIR")
    print("=" * 80)

    # Get all MLB game markets
    cur.execute("""
        SELECT id, ticker, title, home_team, away_team
        FROM kalshi_markets
        WHERE ticker LIKE 'KXMLBGAME%'
        ORDER BY ticker
    """)

    records = cur.fetchall()
    print(f"\nTotal MLB game markets to process: {len(records)}")

    if len(records) == 0:
        print("No MLB game markets found!")
        cur.close()
        conn.close()
        return

    # Backup data
    backup_file = f"mlb_team_names_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    backup_data = []
    for record in records:
        rec_id, ticker, title, home, away = record
        backup_data.append({
            'id': rec_id,
            'ticker': ticker,
            'title': title,
            'home_team': home,
            'away_team': away
        })

    with open(backup_file, 'w') as f:
        json.dump(backup_data, f, indent=2)
    print(f"Backup saved to: {backup_file}")

    # Process each record
    print("\n" + "-" * 80)
    print("PROCESSING RECORDS...")
    print("-" * 80)

    fixes_applied = 0
    fixes_failed = 0

    for record in records:
        rec_id, ticker, title, old_home, old_away = record

        # Parse ticker to get team abbreviations
        away_abbr, home_abbr = parse_mlb_ticker_teams(ticker)

        if away_abbr and home_abbr:
            # Get full team names
            new_away = MLB_TEAM_MAPPING.get(away_abbr, old_away)
            new_home = MLB_TEAM_MAPPING.get(home_abbr, old_home)

            # Only update if names changed
            if new_away != old_away or new_home != old_home:
                cur.execute("""
                    UPDATE kalshi_markets
                    SET home_team = %s, away_team = %s
                    WHERE id = %s
                """, (new_home, new_away, rec_id))

                fixes_applied += 1
                print(f"Fixed: {ticker}")
                print(f"  Title: {title}")
                print(f"  Old: {old_away} @ {old_home}")
                print(f"  New: {new_away} @ {new_home}")
                print()
        else:
            fixes_failed += 1
            print(f"[WARN] Could not parse ticker: {ticker}")
            print(f"  Title: {title}")
            print(f"  Current: {old_away} @ {old_home}")
            print()

    # Commit changes
    conn.commit()

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total records processed: {len(records)}")
    print(f"Fixes applied: {fixes_applied}")
    print(f"Fixes failed: {fixes_failed}")
    print(f"Backup file: {backup_file}")

    if fixes_applied > 0:
        print("\n[SUCCESS] MLB team name fix completed!")
    else:
        print("\n[INFO] No fixes needed - all team names already correct!")

    cur.close()
    conn.close()

if __name__ == "__main__":
    fix_mlb_team_names()
