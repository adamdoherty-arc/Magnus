"""
NCAA Football Team Database
Complete FBS team information with ESPN IDs for dynamic logo fetching
"""

# Complete FBS Team Database with ESPN IDs
# Format: 'Team Name': {'id': 'ESPN ID', 'abbr': 'Abbreviation', 'conference': 'Conference'}

NCAA_TEAMS = {
    # ACC
    'Boston College': {'id': '103', 'abbr': 'BC', 'conference': 'ACC'},
    'Clemson': {'id': '228', 'abbr': 'CLEM', 'conference': 'ACC'},
    'Duke': {'id': '150', 'abbr': 'DUKE', 'conference': 'ACC'},
    'Florida State': {'id': '52', 'abbr': 'FSU', 'conference': 'ACC'},
    'Georgia Tech': {'id': '59', 'abbr': 'GT', 'conference': 'ACC'},
    'Louisville': {'id': '97', 'abbr': 'LOU', 'conference': 'ACC'},
    'Miami': {'id': '2390', 'abbr': 'MIA', 'conference': 'ACC'},
    'North Carolina': {'id': '153', 'abbr': 'UNC', 'conference': 'ACC'},
    'NC State': {'id': '152', 'abbr': 'NCST', 'conference': 'ACC'},
    'Pittsburgh': {'id': '221', 'abbr': 'PITT', 'conference': 'ACC'},
    'Syracuse': {'id': '183', 'abbr': 'SYR', 'conference': 'ACC'},
    'Virginia': {'id': '258', 'abbr': 'UVA', 'conference': 'ACC'},
    'Virginia Tech': {'id': '259', 'abbr': 'VT', 'conference': 'ACC'},
    'Wake Forest': {'id': '154', 'abbr': 'WAKE', 'conference': 'ACC'},

    # Big Ten
    'Illinois': {'id': '356', 'abbr': 'ILL', 'conference': 'Big Ten'},
    'Indiana': {'id': '84', 'abbr': 'IND', 'conference': 'Big Ten'},
    'Iowa': {'id': '2294', 'abbr': 'IOWA', 'conference': 'Big Ten'},
    'Maryland': {'id': '120', 'abbr': 'MD', 'conference': 'Big Ten'},
    'Michigan': {'id': '130', 'abbr': 'MICH', 'conference': 'Big Ten'},
    'Michigan State': {'id': '127', 'abbr': 'MSU', 'conference': 'Big Ten'},
    'Minnesota': {'id': '135', 'abbr': 'MINN', 'conference': 'Big Ten'},
    'Nebraska': {'id': '158', 'abbr': 'NEB', 'conference': 'Big Ten'},
    'Northwestern': {'id': '77', 'abbr': 'NW', 'conference': 'Big Ten'},
    'Ohio State': {'id': '194', 'abbr': 'OSU', 'conference': 'Big Ten'},
    'Oregon': {'id': '2483', 'abbr': 'ORE', 'conference': 'Big Ten'},
    'Penn State': {'id': '213', 'abbr': 'PSU', 'conference': 'Big Ten'},
    'Purdue': {'id': '2509', 'abbr': 'PUR', 'conference': 'Big Ten'},
    'Rutgers': {'id': '164', 'abbr': 'RU', 'conference': 'Big Ten'},
    'UCLA': {'id': '26', 'abbr': 'UCLA', 'conference': 'Big Ten'},
    'USC': {'id': '30', 'abbr': 'USC', 'conference': 'Big Ten'},
    'Washington': {'id': '264', 'abbr': 'WASH', 'conference': 'Big Ten'},
    'Wisconsin': {'id': '275', 'abbr': 'WIS', 'conference': 'Big Ten'},

    # Big 12
    'Arizona': {'id': '12', 'abbr': 'ARIZ', 'conference': 'Big 12'},
    'Arizona State': {'id': '9', 'abbr': 'ASU', 'conference': 'Big 12'},
    'Baylor': {'id': '239', 'abbr': 'BAY', 'conference': 'Big 12'},
    'BYU': {'id': '252', 'abbr': 'BYU', 'conference': 'Big 12'},
    'UCF': {'id': '2116', 'abbr': 'UCF', 'conference': 'Big 12'},
    'Cincinnati': {'id': '2132', 'abbr': 'CIN', 'conference': 'Big 12'},
    'Colorado': {'id': '38', 'abbr': 'COLO', 'conference': 'Big 12'},
    'Houston': {'id': '248', 'abbr': 'HOU', 'conference': 'Big 12'},
    'Iowa State': {'id': '66', 'abbr': 'ISU', 'conference': 'Big 12'},
    'Kansas': {'id': '2305', 'abbr': 'KU', 'conference': 'Big 12'},
    'Kansas State': {'id': '2306', 'abbr': 'KSU', 'conference': 'Big 12'},
    'Oklahoma State': {'id': '197', 'abbr': 'OKST', 'conference': 'Big 12'},
    'TCU': {'id': '2628', 'abbr': 'TCU', 'conference': 'Big 12'},
    'Texas Tech': {'id': '2641', 'abbr': 'TTU', 'conference': 'Big 12'},
    'Utah': {'id': '254', 'abbr': 'UTAH', 'conference': 'Big 12'},
    'West Virginia': {'id': '277', 'abbr': 'WVU', 'conference': 'Big 12'},

    # SEC
    'Alabama': {'id': '333', 'abbr': 'ALA', 'conference': 'SEC'},
    'Arkansas': {'id': '8', 'abbr': 'ARK', 'conference': 'SEC'},
    'Auburn': {'id': '2', 'abbr': 'AUB', 'conference': 'SEC'},
    'Florida': {'id': '57', 'abbr': 'FLA', 'conference': 'SEC'},
    'Georgia': {'id': '61', 'abbr': 'UGA', 'conference': 'SEC'},
    'Kentucky': {'id': '96', 'abbr': 'UK', 'conference': 'SEC'},
    'LSU': {'id': '99', 'abbr': 'LSU', 'conference': 'SEC'},
    'Ole Miss': {'id': '145', 'abbr': 'MISS', 'conference': 'SEC'},
    'Mississippi State': {'id': '344', 'abbr': 'MSST', 'conference': 'SEC'},
    'Missouri': {'id': '142', 'abbr': 'MIZ', 'conference': 'SEC'},
    'Oklahoma': {'id': '201', 'abbr': 'OU', 'conference': 'SEC'},
    'South Carolina': {'id': '2579', 'abbr': 'SC', 'conference': 'SEC'},
    'Tennessee': {'id': '2633', 'abbr': 'TENN', 'conference': 'SEC'},
    'Texas': {'id': '251', 'abbr': 'TEX', 'conference': 'SEC'},
    'Texas A&M': {'id': '245', 'abbr': 'TAMU', 'conference': 'SEC'},
    'Vanderbilt': {'id': '238', 'abbr': 'VAN', 'conference': 'SEC'},

    # American Athletic Conference
    'Army': {'id': '349', 'abbr': 'ARMY', 'conference': 'AAC'},
    'Charlotte': {'id': '2429', 'abbr': 'CHAR', 'conference': 'AAC'},
    'East Carolina': {'id': '151', 'abbr': 'ECU', 'conference': 'AAC'},
    'Florida Atlantic': {'id': '2226', 'abbr': 'FAU', 'conference': 'AAC'},
    'Memphis': {'id': '235', 'abbr': 'MEM', 'conference': 'AAC'},
    'Navy': {'id': '2426', 'abbr': 'NAVY', 'conference': 'AAC'},
    'North Texas': {'id': '249', 'abbr': 'UNT', 'conference': 'AAC'},
    'Rice': {'id': '242', 'abbr': 'RICE', 'conference': 'AAC'},
    'South Florida': {'id': '58', 'abbr': 'USF', 'conference': 'AAC'},
    'Temple': {'id': '218', 'abbr': 'TEM', 'conference': 'AAC'},
    'Tulane': {'id': '2655', 'abbr': 'TULN', 'conference': 'AAC'},
    'Tulsa': {'id': '202', 'abbr': 'TLSA', 'conference': 'AAC'},
    'UAB': {'id': '5', 'abbr': 'UAB', 'conference': 'AAC'},
    'UTSA': {'id': '2636', 'abbr': 'UTSA', 'conference': 'AAC'},

    # Mountain West
    'Air Force': {'id': '2005', 'abbr': 'AF', 'conference': 'Mountain West'},
    'Boise State': {'id': '68', 'abbr': 'BSU', 'conference': 'Mountain West'},
    'Colorado State': {'id': '36', 'abbr': 'CSU', 'conference': 'Mountain West'},
    'Fresno State': {'id': '278', 'abbr': 'FRES', 'conference': 'Mountain West'},
    'Hawaii': {'id': '62', 'abbr': 'HAW', 'conference': 'Mountain West'},
    'Nevada': {'id': '2440', 'abbr': 'NEV', 'conference': 'Mountain West'},
    'New Mexico': {'id': '167', 'abbr': 'UNM', 'conference': 'Mountain West'},
    'San Diego State': {'id': '21', 'abbr': 'SDSU', 'conference': 'Mountain West'},
    'San Jose State': {'id': '23', 'abbr': 'SJSU', 'conference': 'Mountain West'},
    'UNLV': {'id': '2439', 'abbr': 'UNLV', 'conference': 'Mountain West'},
    'Utah State': {'id': '328', 'abbr': 'USU', 'conference': 'Mountain West'},
    'Wyoming': {'id': '2757', 'abbr': 'WYO', 'conference': 'Mountain West'},

    # Sun Belt
    'Appalachian State': {'id': '2026', 'abbr': 'APP', 'conference': 'Sun Belt'},
    'Arkansas State': {'id': '2032', 'abbr': 'ARST', 'conference': 'Sun Belt'},
    'Coastal Carolina': {'id': '324', 'abbr': 'CCU', 'conference': 'Sun Belt'},
    'Georgia Southern': {'id': '290', 'abbr': 'GASO', 'conference': 'Sun Belt'},
    'Georgia State': {'id': '2247', 'abbr': 'GAST', 'conference': 'Sun Belt'},
    'James Madison': {'id': '256', 'abbr': 'JMU', 'conference': 'Sun Belt'},
    'Louisiana': {'id': '309', 'abbr': 'ULL', 'conference': 'Sun Belt'},
    'Louisiana Monroe': {'id': '2433', 'abbr': 'ULM', 'conference': 'Sun Belt'},
    'Marshall': {'id': '276', 'abbr': 'MRSH', 'conference': 'Sun Belt'},
    'Old Dominion': {'id': '295', 'abbr': 'ODU', 'conference': 'Sun Belt'},
    'South Alabama': {'id': '6', 'abbr': 'USA', 'conference': 'Sun Belt'},
    'Southern Mississippi': {'id': '2572', 'abbr': 'USM', 'conference': 'Sun Belt'},
    'Texas State': {'id': '326', 'abbr': 'TXST', 'conference': 'Sun Belt'},
    'Troy': {'id': '2653', 'abbr': 'TROY', 'conference': 'Sun Belt'},

    # MAC
    'Akron': {'id': '2006', 'abbr': 'AKR', 'conference': 'MAC'},
    'Ball State': {'id': '2050', 'abbr': 'BALL', 'conference': 'MAC'},
    'Bowling Green': {'id': '189', 'abbr': 'BGSU', 'conference': 'MAC'},
    'Buffalo': {'id': '2084', 'abbr': 'BUFF', 'conference': 'MAC'},
    'Central Michigan': {'id': '2117', 'abbr': 'CMU', 'conference': 'MAC'},
    'Eastern Michigan': {'id': '2199', 'abbr': 'EMU', 'conference': 'MAC'},
    'Kent State': {'id': '2309', 'abbr': 'KENT', 'conference': 'MAC'},
    'Miami (OH)': {'id': '193', 'abbr': 'M-OH', 'conference': 'MAC'},
    'Northern Illinois': {'id': '2459', 'abbr': 'NIU', 'conference': 'MAC'},
    'Ohio': {'id': '195', 'abbr': 'OHIO', 'conference': 'MAC'},
    'Toledo': {'id': '2649', 'abbr': 'TOL', 'conference': 'MAC'},
    'Western Michigan': {'id': '2711', 'abbr': 'WMU', 'conference': 'MAC'},

    # Conference USA
    'Florida International': {'id': '2229', 'abbr': 'FIU', 'conference': 'CUSA'},
    'Jacksonville State': {'id': '55', 'abbr': 'JVST', 'conference': 'CUSA'},
    'Kennesaw State': {'id': '338', 'abbr': 'KENN', 'conference': 'CUSA'},
    'Liberty': {'id': '2335', 'abbr': 'LIB', 'conference': 'CUSA'},
    'Louisiana Tech': {'id': '2348', 'abbr': 'LT', 'conference': 'CUSA'},
    'Middle Tennessee': {'id': '2393', 'abbr': 'MTSU', 'conference': 'CUSA'},
    'New Mexico State': {'id': '166', 'abbr': 'NMSU', 'conference': 'CUSA'},
    'Sam Houston': {'id': '2534', 'abbr': 'SHSU', 'conference': 'CUSA'},
    'UTEP': {'id': '2638', 'abbr': 'UTEP', 'conference': 'CUSA'},
    'Western Kentucky': {'id': '98', 'abbr': 'WKU', 'conference': 'CUSA'},

    # Independent
    'Connecticut': {'id': '41', 'abbr': 'CONN', 'conference': 'Independent'},
    'Massachusetts': {'id': '113', 'abbr': 'UMASS', 'conference': 'Independent'},
    'Notre Dame': {'id': '87', 'abbr': 'ND', 'conference': 'Independent'},
}


def get_team_logo_url(team_name: str, size: int = 500) -> str:
    """
    Get ESPN logo URL for a team

    Args:
        team_name: Full team name (e.g., "Alabama", "Ohio State")
        size: Logo size (default 500px, can use 100, 200, 500)

    Returns:
        ESPN CDN URL for team logo
    """
    team_data = NCAA_TEAMS.get(team_name)

    if not team_data:
        # Try partial match
        for name, data in NCAA_TEAMS.items():
            if team_name.lower() in name.lower() or name.lower() in team_name.lower():
                team_data = data
                break

    if team_data:
        team_id = team_data['id']
        return f"https://a.espncdn.com/i/teamlogos/ncaa/500/{team_id}.png"

    # Return placeholder if team not found
    return ""


def get_all_team_logos(size: int = 500) -> dict:
    """
    Get logo URLs for all teams

    Args:
        size: Logo size (default 500px)

    Returns:
        Dictionary of team_name: logo_url
    """
    logos = {}

    for team_name, team_data in NCAA_TEAMS.items():
        team_id = team_data['id']
        logos[team_name] = f"https://a.espncdn.com/i/teamlogos/ncaa/{size}/{team_id}.png"

    return logos


def find_team_by_name(partial_name: str) -> dict:
    """
    Find team by partial name match

    Args:
        partial_name: Partial team name to search for

    Returns:
        Team data dictionary or None
    """
    partial_lower = partial_name.lower()

    # Exact match first
    if partial_name in NCAA_TEAMS:
        return NCAA_TEAMS[partial_name]

    # Partial match
    for team_name, team_data in NCAA_TEAMS.items():
        if partial_lower in team_name.lower():
            return {**team_data, 'name': team_name}

    # Check abbreviations
    for team_name, team_data in NCAA_TEAMS.items():
        if partial_lower == team_data['abbr'].lower():
            return {**team_data, 'name': team_name}

    return None


def get_conference_teams(conference: str) -> dict:
    """
    Get all teams in a conference

    Args:
        conference: Conference name (e.g., "SEC", "Big Ten", "ACC")

    Returns:
        Dictionary of teams in that conference
    """
    teams = {}

    for team_name, team_data in NCAA_TEAMS.items():
        if team_data['conference'].lower() == conference.lower():
            teams[team_name] = team_data

    return teams


# Pre-generate all logos for quick access
NCAA_LOGOS = get_all_team_logos(size=500)


if __name__ == "__main__":
    print("="*80)
    print("NCAA TEAM DATABASE")
    print("="*80)

    print(f"\nTotal FBS Teams: {len(NCAA_TEAMS)}")

    # Show teams by conference
    conferences = set(team['conference'] for team in NCAA_TEAMS.values())

    print(f"\nConferences: {len(conferences)}")
    for conf in sorted(conferences):
        conf_teams = get_conference_teams(conf)
        print(f"\n{conf}: {len(conf_teams)} teams")
        for team_name in sorted(conf_teams.keys()):
            team_data = conf_teams[team_name]
            print(f"  - {team_name} ({team_data['abbr']})")

    # Test logo fetching
    print("\n" + "="*80)
    print("TESTING LOGO FETCHING")
    print("="*80)

    test_teams = ['Alabama', 'Ohio State', 'Michigan', 'Georgia', 'Texas']

    for team in test_teams:
        logo_url = get_team_logo_url(team)
        print(f"\n{team}:")
        print(f"  URL: {logo_url}")

    # Test partial name matching
    print("\n" + "="*80)
    print("TESTING PARTIAL NAME MATCHING")
    print("="*80)

    test_searches = ['bama', 'ohio', 'USC', 'ND', 'florida state']

    for search in test_searches:
        result = find_team_by_name(search)
        if result:
            print(f"\n'{search}' → {result.get('name', 'Found')}")
            print(f"  Abbreviation: {result['abbr']}")
            print(f"  Conference: {result['conference']}")
        else:
            print(f"\n'{search}' → Not found")
