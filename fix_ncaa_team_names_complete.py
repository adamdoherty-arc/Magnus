"""Complete NCAA team name fix based on ticker abbreviations."""
import psycopg2
import os
import re
from dotenv import load_dotenv
import json
from datetime import datetime

load_dotenv()

# Comprehensive NCAA team mapping from ticker abbreviations to full names
NCAA_TEAM_MAPPING = {
    # ACC
    'BC': 'Boston College',
    'CLEM': 'Clemson',
    'DUKE': 'Duke',
    'FSU': 'Florida State',
    'FST': 'Florida State',
    'GT': 'Georgia Tech',
    'LOU': 'Louisville',
    'MIA': 'Miami',
    'MIAF': 'Miami (FL)',
    'UNC': 'North Carolina',
    'NCST': 'NC State',
    'NCS': 'NC State',
    'PITT': 'Pittsburgh',
    'SYR': 'Syracuse',
    'UVA': 'Virginia',
    'VT': 'Virginia Tech',
    'WAKE': 'Wake Forest',
    'CAL': 'California',
    'SMU': 'SMU',
    'STAN': 'Stanford',

    # Big Ten
    'ILL': 'Illinois',
    'IND': 'Indiana',
    'IOWA': 'Iowa',
    'MD': 'Maryland',
    'MICH': 'Michigan',
    'MSU': 'Michigan State',
    'MINN': 'Minnesota',
    'NEB': 'Nebraska',
    'NU': 'Northwestern',
    'NW': 'Northwestern',
    'NWEST': 'Northwestern',
    'OSU': 'Ohio State',
    'OHST': 'Ohio State',
    'PSU': 'Penn State',
    'PUR': 'Purdue',
    'RUT': 'Rutgers',
    'WIS': 'Wisconsin',
    'WISC': 'Wisconsin',

    # Big 12
    'ARIZ': 'Arizona',
    'ASU': 'Arizona State',
    'AZST': 'Arizona State',
    'BAY': 'Baylor',
    'BYU': 'BYU',
    'CIN': 'Cincinnati',
    'COL': 'Colorado',
    'COLO': 'Colorado',
    'HOU': 'Houston',
    'IOSU': 'Iowa State',
    'ISU': 'Iowa State',
    'KU': 'Kansas',
    'KAN': 'Kansas',
    'KSU': 'Kansas State',
    'KASU': 'Kansas State',
    'OKST': 'Oklahoma State',
    'TCU': 'TCU',
    'TT': 'Texas Tech',
    'TTU': 'Texas Tech',
    'UCF': 'UCF',
    'UTAH': 'Utah',
    'WVU': 'West Virginia',

    # SEC
    'ALA': 'Alabama',
    'BAMA': 'Alabama',
    'ARK': 'Arkansas',
    'AUB': 'Auburn',
    'FLA': 'Florida',
    'UF': 'Florida',
    'UGA': 'Georgia',
    'GA': 'Georgia',
    'UK': 'Kentucky',
    'KY': 'Kentucky',
    'LSU': 'LSU',
    'MISS': 'Ole Miss',
    'MSST': 'Mississippi State',
    'MIST': 'Mississippi State',
    'MIZZ': 'Missouri',
    'MIZ': 'Missouri',
    'MOSU': 'Missouri State',
    'SC': 'South Carolina',
    'SCAR': 'South Carolina',
    'TENN': 'Tennessee',
    'UT': 'Tennessee',
    'TAMU': 'Texas A&M',
    'TAM': 'Texas A&M',
    'TEX': 'Texas',
    'UTEX': 'Texas',
    'VAN': 'Vanderbilt',
    'VAND': 'Vanderbilt',
    'OU': 'Oklahoma',
    'OKLA': 'Oklahoma',

    # Pac-12 / Other Power 5
    'ORE': 'Oregon',
    'ORST': 'Oregon State',
    'OST': 'Oregon State',
    'USC': 'USC',
    'UCLA': 'UCLA',
    'WASH': 'Washington',
    'UW': 'Washington',
    'WSU': 'Washington State',
    'WAST': 'Washington State',

    # Group of 5 - American
    'USF': 'South Florida',
    'ARMY': 'Army',
    'NAVY': 'Navy',
    'AF': 'Air Force',
    'AIRFO': 'Air Force',
    'CHAR': 'Charlotte',
    'ECU': 'East Carolina',
    'FAU': 'Florida Atlantic',
    'MEM': 'Memphis',
    'RICE': 'Rice',
    'TUL': 'Tulane',
    'TULSA': 'Tulsa',
    'TULN': 'Tulane',
    'TEMP': 'Temple',
    'UTSA': 'UTSA',

    # Group of 5 - C-USA
    'FIU': 'FIU',
    'JVST': 'Jacksonville State',
    'JSU': 'Jacksonville State',
    'LT': 'Louisiana Tech',
    'LA TECH': 'Louisiana Tech',
    'LATECH': 'Louisiana Tech',
    'MTSU': 'Middle Tennessee',
    'MT': 'Middle Tennessee',
    'NMSU': 'New Mexico State',
    'NM': 'New Mexico',
    'NMX': 'New Mexico',
    'SAM': 'Sam Houston State',
    'SHSU': 'Sam Houston State',
    'WKU': 'Western Kentucky',

    # Group of 5 - MAC
    'AKR': 'Akron',
    'BALL': 'Ball State',
    'BSU': 'Ball State',
    'BG': 'Bowling Green',
    'BGSU': 'Bowling Green',
    'BUFF': 'Buffalo',
    'CMU': 'Central Michigan',
    'EMU': 'Eastern Michigan',
    'KENT': 'Kent State',
    'KST': 'Kent State',
    'MIA OH': 'Miami (OH)',
    'MIAOH': 'Miami (OH)',
    'NIU': 'Northern Illinois',
    'OHIO': 'Ohio',
    'TOL': 'Toledo',
    'WMU': 'Western Michigan',

    # Group of 5 - Mountain West
    'BST': 'Boise State',
    'BOIS': 'Boise State',
    'BOST': 'Boise State',
    'CSU': 'Colorado State',
    'COST': 'Colorado State',
    'FRES': 'Fresno State',
    'FST': 'Fresno State',
    'HAW': "Hawai'i",
    'HAWAII': "Hawai'i",
    'NEV': 'Nevada',
    'SDSU': 'San Diego State',
    'SJSU': 'San Jose State',
    'SJS': 'San Jose State',
    'UNLV': 'UNLV',
    'USU': 'Utah State',
    'UTST': 'Utah State',
    'WYOM': 'Wyoming',
    'WYO': 'Wyoming',

    # Group of 5 - Sun Belt
    'APP': 'Appalachian State',
    'APST': 'Appalachian State',
    'ARST': 'Arkansas State',
    'CCAR': 'Coastal Carolina',
    'CC': 'Coastal Carolina',
    'GASO': 'Georgia Southern',
    'GS': 'Georgia Southern',
    'GAST': 'Georgia State',
    'GSU': 'Georgia State',
    'JMU': 'James Madison',
    'MARS': 'Marshall',
    'ODU': 'Old Dominion',
    'SLOU': 'South Alabama',
    'USA': 'South Alabama',
    'SOUT': 'Southern Miss',
    'USM': 'Southern Miss',
    'ULM': 'Louisiana Monroe',
    'ULL': 'Louisiana',
    'TXST': 'Texas State',

    # FCS / Other
    'UMass': 'UMass',
    'UMASS': 'UMass',
    'MASS': 'UMass',
    'UCONN': 'UConn',
    'CONN': 'UConn',
    'ND': 'Notre Dame',
    'NOTRE': 'Notre Dame',
    'NOTDA': 'Notre Dame',
    'LIB': 'Liberty',
    'LIBY': 'Liberty',
    'MERC': 'Mercer',
    'MER': 'Mercer',
    'SAM': 'Samford',
    'SAMF': 'Samford',
    'FUR': 'Furman',
    'KENN': 'Kennesaw State',
    'DEL': 'Delaware',
    'JMU': 'James Madison',
    'UAB': 'UAB',
    'UTEP': 'UTEP',
    'TROP': 'Troy',
    'TROY': 'Troy',
    'EIU': 'Eastern Illinois',
    'MRSH': 'Marshall',
    'RUTG': 'Rutgers',
    'MTU': 'Middle Tennessee',
    'TLSA': 'Tulsa',
    'AFA': 'Air Force',
    'UNM': 'New Mexico',
    'TEM': 'Temple',
    'MOH': 'Miami (OH)',

    # Additional variations
    'TEXAS': 'Texas',
    'OKLA': 'Oklahoma',
    'NEBR': 'Nebraska',
    'MINN': 'Minnesota',
    'PURDUE': 'Purdue',
}

def parse_ncaa_ticker_teams(ticker: str) -> tuple:
    """
    Extract team abbreviations from NCAA ticker.

    Example: KXNCAAFGAME-25NOV15VTFSU-VT → (VT, FSU)
    Pattern: KXNCAAFGAME-DDmmmYYTEAMS-RESULT
    """
    # Extract the concatenated team string after the date
    match = re.search(r'KXNCAAFGAME-\d{2}[A-Z]{3}\d{2}([A-Z]+)-', ticker)

    if not match:
        return None, None

    teams_str = match.group(1)

    # Try all possible split points to find valid team abbreviations
    for i in range(2, len(teams_str)):
        team1 = teams_str[:i]
        team2 = teams_str[i:]

        # Check if both are valid NCAA team abbreviations
        if team1 in NCAA_TEAM_MAPPING and team2 in NCAA_TEAM_MAPPING:
            # Return in order: team1 = away, team2 = home
            return team1, team2

    return None, None

def fix_ncaa_team_names():
    """Fix all NCAA team names in database based on ticker abbreviations."""

    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        database=os.getenv('DB_NAME', 'magnus'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', '')
    )
    cur = conn.cursor()

    print("=" * 80)
    print("NCAA TEAM NAME FIX - COMPREHENSIVE REPAIR")
    print("=" * 80)

    # Get all NCAA markets
    cur.execute("""
        SELECT id, ticker, title, home_team, away_team
        FROM kalshi_markets
        WHERE ticker LIKE 'KXNCAAFGAME%'
        ORDER BY ticker
    """)

    records = cur.fetchall()
    print(f"\nTotal NCAA markets to process: {len(records)}")

    # Backup data
    backup_file = f"ncaa_team_names_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
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
        away_abbr, home_abbr = parse_ncaa_ticker_teams(ticker)

        if away_abbr and home_abbr:
            # Get full team names
            new_away = NCAA_TEAM_MAPPING.get(away_abbr, old_away)
            new_home = NCAA_TEAM_MAPPING.get(home_abbr, old_home)

            # Only update if names changed
            if new_away != old_away or new_home != old_home:
                cur.execute("""
                    UPDATE kalshi_markets
                    SET home_team = %s, away_team = %s
                    WHERE id = %s
                """, (new_home, new_away, rec_id))

                fixes_applied += 1
                print(f"Fixed: {ticker}")
                print(f"  Old: {old_away} @ {old_home}")
                print(f"  New: {new_away} @ {new_home}")
        else:
            fixes_failed += 1
            print(f"[WARN] Could not parse ticker: {ticker}")
            print(f"  Title: {title}")
            print(f"  Current: {old_away} @ {old_home}")

    # Commit changes
    conn.commit()

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total records processed: {len(records)}")
    print(f"Fixes applied: {fixes_applied}")
    print(f"Fixes failed: {fixes_failed}")
    print(f"Backup file: {backup_file}")

    cur.close()
    conn.close()

    print("\n[SUCCESS] NCAA team name fix completed!")

if __name__ == "__main__":
    fix_ncaa_team_names()
