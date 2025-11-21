"""
NFL Football Team Database
Complete NFL team information with ESPN IDs for dynamic logo fetching

Uses ESPN CDN pattern: https://a.espncdn.com/i/teamlogos/nfl/500/[ABBR].png
"""

# Complete NFL Team Database with ESPN abbreviations
# Format: 'Team Name': {'abbr': 'ESPN Abbreviation', 'city': 'City', 'division': 'Division'}

NFL_TEAMS = {
    # AFC East
    'Buffalo': {'abbr': 'buf', 'city': 'Buffalo', 'full_name': 'Buffalo Bills', 'division': 'AFC East'},
    'Miami': {'abbr': 'mia', 'city': 'Miami', 'full_name': 'Miami Dolphins', 'division': 'AFC East'},
    'New England': {'abbr': 'ne', 'city': 'New England', 'full_name': 'New England Patriots', 'division': 'AFC East'},
    'New York Jets': {'abbr': 'nyj', 'city': 'New York', 'full_name': 'New York Jets', 'division': 'AFC East'},

    # AFC North
    'Baltimore': {'abbr': 'bal', 'city': 'Baltimore', 'full_name': 'Baltimore Ravens', 'division': 'AFC North'},
    'Cincinnati': {'abbr': 'cin', 'city': 'Cincinnati', 'full_name': 'Cincinnati Bengals', 'division': 'AFC North'},
    'Cleveland': {'abbr': 'cle', 'city': 'Cleveland', 'full_name': 'Cleveland Browns', 'division': 'AFC North'},
    'Pittsburgh': {'abbr': 'pit', 'city': 'Pittsburgh', 'full_name': 'Pittsburgh Steelers', 'division': 'AFC North'},

    # AFC South
    'Houston': {'abbr': 'hou', 'city': 'Houston', 'full_name': 'Houston Texans', 'division': 'AFC South'},
    'Indianapolis': {'abbr': 'ind', 'city': 'Indianapolis', 'full_name': 'Indianapolis Colts', 'division': 'AFC South'},
    'Jacksonville': {'abbr': 'jax', 'city': 'Jacksonville', 'full_name': 'Jacksonville Jaguars', 'division': 'AFC South'},
    'Tennessee': {'abbr': 'ten', 'city': 'Tennessee', 'full_name': 'Tennessee Titans', 'division': 'AFC South'},

    # AFC West
    'Denver': {'abbr': 'den', 'city': 'Denver', 'full_name': 'Denver Broncos', 'division': 'AFC West'},
    'Kansas City': {'abbr': 'kc', 'city': 'Kansas City', 'full_name': 'Kansas City Chiefs', 'division': 'AFC West'},
    'Las Vegas': {'abbr': 'lv', 'city': 'Las Vegas', 'full_name': 'Las Vegas Raiders', 'division': 'AFC West'},
    'Los Angeles Chargers': {'abbr': 'lac', 'city': 'Los Angeles', 'full_name': 'Los Angeles Chargers', 'division': 'AFC West'},

    # NFC East
    'Dallas': {'abbr': 'dal', 'city': 'Dallas', 'full_name': 'Dallas Cowboys', 'division': 'NFC East'},
    'New York Giants': {'abbr': 'nyg', 'city': 'New York', 'full_name': 'New York Giants', 'division': 'NFC East'},
    'Philadelphia': {'abbr': 'phi', 'city': 'Philadelphia', 'full_name': 'Philadelphia Eagles', 'division': 'NFC East'},
    'Washington': {'abbr': 'wsh', 'city': 'Washington', 'full_name': 'Washington Commanders', 'division': 'NFC East'},

    # NFC North
    'Chicago': {'abbr': 'chi', 'city': 'Chicago', 'full_name': 'Chicago Bears', 'division': 'NFC North'},
    'Detroit': {'abbr': 'det', 'city': 'Detroit', 'full_name': 'Detroit Lions', 'division': 'NFC North'},
    'Green Bay': {'abbr': 'gb', 'city': 'Green Bay', 'full_name': 'Green Bay Packers', 'division': 'NFC North'},
    'Minnesota': {'abbr': 'min', 'city': 'Minnesota', 'full_name': 'Minnesota Vikings', 'division': 'NFC North'},

    # NFC South
    'Atlanta': {'abbr': 'atl', 'city': 'Atlanta', 'full_name': 'Atlanta Falcons', 'division': 'NFC South'},
    'Carolina': {'abbr': 'car', 'city': 'Carolina', 'full_name': 'Carolina Panthers', 'division': 'NFC South'},
    'New Orleans': {'abbr': 'no', 'city': 'New Orleans', 'full_name': 'New Orleans Saints', 'division': 'NFC South'},
    'Tampa Bay': {'abbr': 'tb', 'city': 'Tampa Bay', 'full_name': 'Tampa Bay Buccaneers', 'division': 'NFC South'},

    # NFC West
    'Arizona': {'abbr': 'ari', 'city': 'Arizona', 'full_name': 'Arizona Cardinals', 'division': 'NFC West'},
    'Los Angeles Rams': {'abbr': 'lar', 'city': 'Los Angeles', 'full_name': 'Los Angeles Rams', 'division': 'NFC West'},
    'San Francisco': {'abbr': 'sf', 'city': 'San Francisco', 'full_name': 'San Francisco 49ers', 'division': 'NFC West'},
    'Seattle': {'abbr': 'sea', 'city': 'Seattle', 'full_name': 'Seattle Seahawks', 'division': 'NFC West'},
}

# Alternate team name mappings for matching Kalshi market data
NFL_TEAM_ALIASES = {
    'Bills': 'Buffalo',
    'Dolphins': 'Miami',
    'Patriots': 'New England',
    'Jets': 'New York Jets',
    'Ravens': 'Baltimore',
    'Bengals': 'Cincinnati',
    'Browns': 'Cleveland',
    'Steelers': 'Pittsburgh',
    'Texans': 'Houston',
    'Colts': 'Indianapolis',
    'Jaguars': 'Jacksonville',
    'Titans': 'Tennessee',
    'Broncos': 'Denver',
    'Chiefs': 'Kansas City',
    'Raiders': 'Las Vegas',
    'Chargers': 'Los Angeles Chargers',
    'Cowboys': 'Dallas',
    'Giants': 'New York Giants',
    'Eagles': 'Philadelphia',
    'Commanders': 'Washington',
    'Washington Commanders': 'Washington',
    'Bears': 'Chicago',
    'Lions': 'Detroit',
    'Packers': 'Green Bay',
    'Vikings': 'Minnesota',
    'Falcons': 'Atlanta',
    'Panthers': 'Carolina',
    'Saints': 'New Orleans',
    'Buccaneers': 'Tampa Bay',
    'Cardinals': 'Arizona',
    'Rams': 'Los Angeles Rams',
    '49ers': 'San Francisco',
    'Seahawks': 'Seattle',
    # City names
    'Buffalo Bills': 'Buffalo',
    'Miami Dolphins': 'Miami',
    'New England Patriots': 'New England',
    'Baltimore Ravens': 'Baltimore',
    'Cincinnati Bengals': 'Cincinnati',
    'Cleveland Browns': 'Cleveland',
    'Pittsburgh Steelers': 'Pittsburgh',
    'Houston Texans': 'Houston',
    'Indianapolis Colts': 'Indianapolis',
    'Jacksonville Jaguars': 'Jacksonville',
    'Tennessee Titans': 'Tennessee',
    'Denver Broncos': 'Denver',
    'Kansas City Chiefs': 'Kansas City',
    'Las Vegas Raiders': 'Las Vegas',
    'Los Angeles Chargers': 'Los Angeles Chargers',
    'Dallas Cowboys': 'Dallas',
    'New York Giants': 'New York Giants',
    'Philadelphia Eagles': 'Philadelphia',
    'Chicago Bears': 'Chicago',
    'Detroit Lions': 'Detroit',
    'Green Bay Packers': 'Green Bay',
    'Minnesota Vikings': 'Minnesota',
    'Atlanta Falcons': 'Atlanta',
    'Carolina Panthers': 'Carolina',
    'New Orleans Saints': 'New Orleans',
    'Tampa Bay Buccaneers': 'Tampa Bay',
    'Arizona Cardinals': 'Arizona',
    'Los Angeles Rams': 'Los Angeles Rams',
    'San Francisco 49ers': 'San Francisco',
    'Seattle Seahawks': 'Seattle',
}

# Generate NFL logo URLs dictionary for easy access
NFL_LOGOS = {
    team_name: f"https://a.espncdn.com/i/teamlogos/nfl/500/{info['abbr']}.png"
    for team_name, info in NFL_TEAMS.items()
}


def get_team_logo_url(team_name: str, size: int = 500) -> str:
    """
    Get ESPN CDN logo URL for an NFL team

    Args:
        team_name: Team name (e.g., "Buffalo", "Kansas City", "New York Giants")
        size: Logo size in pixels (default: 500)

    Returns:
        str: ESPN CDN URL for team logo
    """
    # Try direct match
    if team_name in NFL_TEAMS:
        abbr = NFL_TEAMS[team_name]['abbr']
        return f"https://a.espncdn.com/i/teamlogos/nfl/{size}/{abbr}.png"

    # Try alias match
    if team_name in NFL_TEAM_ALIASES:
        canonical_name = NFL_TEAM_ALIASES[team_name]
        if canonical_name in NFL_TEAMS:
            abbr = NFL_TEAMS[canonical_name]['abbr']
            return f"https://a.espncdn.com/i/teamlogos/nfl/{size}/{abbr}.png"

    # Try fuzzy match
    team_result = find_team_by_name(team_name)
    if team_result:
        abbr = team_result['abbr']
        return f"https://a.espncdn.com/i/teamlogos/nfl/{size}/{abbr}.png"

    # Return placeholder if no match found
    return ""


def find_team_by_name(search_name: str) -> dict:
    """
    Find team by partial name match (case-insensitive)

    Args:
        search_name: Team name or partial name to search for

    Returns:
        dict: Team info dict or None if not found
    """
    search_lower = search_name.lower().strip()

    # Try exact match first
    for team_name, info in NFL_TEAMS.items():
        if team_name.lower() == search_lower:
            return info

    # Try alias match
    if search_name in NFL_TEAM_ALIASES:
        canonical_name = NFL_TEAM_ALIASES[search_name]
        if canonical_name in NFL_TEAMS:
            return NFL_TEAMS[canonical_name]

    # Try partial match on team name
    for team_name, info in NFL_TEAMS.items():
        if search_lower in team_name.lower():
            return info

    # Try partial match on full name
    for team_name, info in NFL_TEAMS.items():
        if search_lower in info['full_name'].lower():
            return info

    # Try partial match on city
    for team_name, info in NFL_TEAMS.items():
        if search_lower in info['city'].lower():
            return info

    return None


def get_all_teams_by_division(division: str = None) -> dict:
    """
    Get teams filtered by division

    Args:
        division: Division name (e.g., "AFC East", "NFC North") or None for all teams

    Returns:
        dict: Filtered teams
    """
    if division is None:
        return NFL_TEAMS

    return {
        name: info
        for name, info in NFL_TEAMS.items()
        if info['division'] == division
    }


if __name__ == "__main__":
    # Test the module
    print("="*80)
    print("NFL TEAM DATABASE TEST")
    print("="*80)
    print(f"\nTotal teams: {len(NFL_TEAMS)}")

    # Test logo URL generation
    print("\nSample logo URLs:")
    for team in list(NFL_TEAMS.keys())[:5]:
        url = get_team_logo_url(team)
        print(f"  {team:25s} -> {url}")

    # Test team search
    print("\nTeam search tests:")
    test_names = ["Buffalo", "Chiefs", "New York Giants", "49ers", "Cowboys"]
    for name in test_names:
        result = find_team_by_name(name)
        if result:
            print(f"  '{name}' -> {result['full_name']} ({result['abbr']})")
        else:
            print(f"  '{name}' -> NOT FOUND")

    # Test division filtering
    print("\nAFC East teams:")
    afc_east = get_all_teams_by_division("AFC East")
    for team, info in afc_east.items():
        print(f"  {info['full_name']}")

    print("\n" + "="*80)
