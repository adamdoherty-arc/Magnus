"""
NBA Team Database
Complete database of all 30 NBA teams with logos, colors, and info
"""

import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# All 30 NBA teams with full information
NBA_TEAMS = {
    # Eastern Conference - Atlantic Division
    'BOS': {
        'name': 'Boston Celtics',
        'full_name': 'Boston Celtics',
        'city': 'Boston',
        'abbreviation': 'BOS',
        'conference': 'Eastern',
        'division': 'Atlantic',
        'color': '#007A33',
        'alt_color': '#BA9653',
        'logo': 'https://a.espncdn.com/i/teamlogos/nba/500/bos.png'
    },
    'BKN': {
        'name': 'Brooklyn Nets',
        'full_name': 'Brooklyn Nets',
        'city': 'Brooklyn',
        'abbreviation': 'BKN',
        'conference': 'Eastern',
        'division': 'Atlantic',
        'color': '#000000',
        'alt_color': '#FFFFFF',
        'logo': 'https://a.espncdn.com/i/teamlogos/nba/500/bkn.png'
    },
    'NYK': {
        'name': 'New York Knicks',
        'full_name': 'New York Knicks',
        'city': 'New York',
        'abbreviation': 'NYK',
        'conference': 'Eastern',
        'division': 'Atlantic',
        'color': '#006BB6',
        'alt_color': '#F58426',
        'logo': 'https://a.espncdn.com/i/teamlogos/nba/500/nyk.png'
    },
    'PHI': {
        'name': 'Philadelphia 76ers',
        'full_name': 'Philadelphia 76ers',
        'city': 'Philadelphia',
        'abbreviation': 'PHI',
        'conference': 'Eastern',
        'division': 'Atlantic',
        'color': '#006BB6',
        'alt_color': '#ED174C',
        'logo': 'https://a.espncdn.com/i/teamlogos/nba/500/phi.png'
    },
    'TOR': {
        'name': 'Toronto Raptors',
        'full_name': 'Toronto Raptors',
        'city': 'Toronto',
        'abbreviation': 'TOR',
        'conference': 'Eastern',
        'division': 'Atlantic',
        'color': '#CE1141',
        'alt_color': '#000000',
        'logo': 'https://a.espncdn.com/i/teamlogos/nba/500/tor.png'
    },
    
    # Eastern Conference - Central Division
    'CHI': {
        'name': 'Chicago Bulls',
        'full_name': 'Chicago Bulls',
        'city': 'Chicago',
        'abbreviation': 'CHI',
        'conference': 'Eastern',
        'division': 'Central',
        'color': '#CE1141',
        'alt_color': '#000000',
        'logo': 'https://a.espncdn.com/i/teamlogos/nba/500/chi.png'
    },
    'CLE': {
        'name': 'Cleveland Cavaliers',
        'full_name': 'Cleveland Cavaliers',
        'city': 'Cleveland',
        'abbreviation': 'CLE',
        'conference': 'Eastern',
        'division': 'Central',
        'color': '#860038',
        'alt_color': '#FDBB30',
        'logo': 'https://a.espncdn.com/i/teamlogos/nba/500/cle.png'
    },
    'DET': {
        'name': 'Detroit Pistons',
        'full_name': 'Detroit Pistons',
        'city': 'Detroit',
        'abbreviation': 'DET',
        'conference': 'Eastern',
        'division': 'Central',
        'color': '#C8102E',
        'alt_color': '#1D42BA',
        'logo': 'https://a.espncdn.com/i/teamlogos/nba/500/det.png'
    },
    'IND': {
        'name': 'Indiana Pacers',
        'full_name': 'Indiana Pacers',
        'city': 'Indiana',
        'abbreviation': 'IND',
        'conference': 'Eastern',
        'division': 'Central',
        'color': '#002D62',
        'alt_color': '#FDBB30',
        'logo': 'https://a.espncdn.com/i/teamlogos/nba/500/ind.png'
    },
    'MIL': {
        'name': 'Milwaukee Bucks',
        'full_name': 'Milwaukee Bucks',
        'city': 'Milwaukee',
        'abbreviation': 'MIL',
        'conference': 'Eastern',
        'division': 'Central',
        'color': '#00471B',
        'alt_color': '#EEE1C6',
        'logo': 'https://a.espncdn.com/i/teamlogos/nba/500/mil.png'
    },
    
    # Eastern Conference - Southeast Division
    'ATL': {
        'name': 'Atlanta Hawks',
        'full_name': 'Atlanta Hawks',
        'city': 'Atlanta',
        'abbreviation': 'ATL',
        'conference': 'Eastern',
        'division': 'Southeast',
        'color': '#E03A3E',
        'alt_color': '#C1D32F',
        'logo': 'https://a.espncdn.com/i/teamlogos/nba/500/atl.png'
    },
    'CHA': {
        'name': 'Charlotte Hornets',
        'full_name': 'Charlotte Hornets',
        'city': 'Charlotte',
        'abbreviation': 'CHA',
        'conference': 'Eastern',
        'division': 'Southeast',
        'color': '#1D1160',
        'alt_color': '#00788C',
        'logo': 'https://a.espncdn.com/i/teamlogos/nba/500/cha.png'
    },
    'MIA': {
        'name': 'Miami Heat',
        'full_name': 'Miami Heat',
        'city': 'Miami',
        'abbreviation': 'MIA',
        'conference': 'Eastern',
        'division': 'Southeast',
        'color': '#98002E',
        'alt_color': '#F9A01B',
        'logo': 'https://a.espncdn.com/i/teamlogos/nba/500/mia.png'
    },
    'ORL': {
        'name': 'Orlando Magic',
        'full_name': 'Orlando Magic',
        'city': 'Orlando',
        'abbreviation': 'ORL',
        'conference': 'Eastern',
        'division': 'Southeast',
        'color': '#0077C0',
        'alt_color': '#C4CED4',
        'logo': 'https://a.espncdn.com/i/teamlogos/nba/500/orl.png'
    },
    'WAS': {
        'name': 'Washington Wizards',
        'full_name': 'Washington Wizards',
        'city': 'Washington',
        'abbreviation': 'WAS',
        'conference': 'Eastern',
        'division': 'Southeast',
        'color': '#002B5C',
        'alt_color': '#E31837',
        'logo': 'https://a.espncdn.com/i/teamlogos/nba/500/wsh.png'
    },
    
    # Western Conference - Northwest Division
    'DEN': {
        'name': 'Denver Nuggets',
        'full_name': 'Denver Nuggets',
        'city': 'Denver',
        'abbreviation': 'DEN',
        'conference': 'Western',
        'division': 'Northwest',
        'color': '#0E2240',
        'alt_color': '#FEC524',
        'logo': 'https://a.espncdn.com/i/teamlogos/nba/500/den.png'
    },
    'MIN': {
        'name': 'Minnesota Timberwolves',
        'full_name': 'Minnesota Timberwolves',
        'city': 'Minnesota',
        'abbreviation': 'MIN',
        'conference': 'Western',
        'division': 'Northwest',
        'color': '#0C2340',
        'alt_color': '#236192',
        'logo': 'https://a.espncdn.com/i/teamlogos/nba/500/min.png'
    },
    'OKC': {
        'name': 'Oklahoma City Thunder',
        'full_name': 'Oklahoma City Thunder',
        'city': 'Oklahoma City',
        'abbreviation': 'OKC',
        'conference': 'Western',
        'division': 'Northwest',
        'color': '#007AC1',
        'alt_color': '#EF3B24',
        'logo': 'https://a.espncdn.com/i/teamlogos/nba/500/okc.png'
    },
    'POR': {
        'name': 'Portland Trail Blazers',
        'full_name': 'Portland Trail Blazers',
        'city': 'Portland',
        'abbreviation': 'POR',
        'conference': 'Western',
        'division': 'Northwest',
        'color': '#E03A3E',
        'alt_color': '#000000',
        'logo': 'https://a.espncdn.com/i/teamlogos/nba/500/por.png'
    },
    'UTA': {
        'name': 'Utah Jazz',
        'full_name': 'Utah Jazz',
        'city': 'Utah',
        'abbreviation': 'UTA',
        'conference': 'Western',
        'division': 'Northwest',
        'color': '#002B5C',
        'alt_color': '#00471B',
        'logo': 'https://a.espncdn.com/i/teamlogos/nba/500/utah.png'
    },
    
    # Western Conference - Pacific Division
    'GSW': {
        'name': 'Golden State Warriors',
        'full_name': 'Golden State Warriors',
        'city': 'Golden State',
        'abbreviation': 'GSW',
        'conference': 'Western',
        'division': 'Pacific',
        'color': '#1D428A',
        'alt_color': '#FFC72C',
        'logo': 'https://a.espncdn.com/i/teamlogos/nba/500/gs.png'
    },
    'LAC': {
        'name': 'LA Clippers',
        'full_name': 'Los Angeles Clippers',
        'city': 'Los Angeles',
        'abbreviation': 'LAC',
        'conference': 'Western',
        'division': 'Pacific',
        'color': '#C8102E',
        'alt_color': '#1D428A',
        'logo': 'https://a.espncdn.com/i/teamlogos/nba/500/lac.png'
    },
    'LAL': {
        'name': 'Los Angeles Lakers',
        'full_name': 'Los Angeles Lakers',
        'city': 'Los Angeles',
        'abbreviation': 'LAL',
        'conference': 'Western',
        'division': 'Pacific',
        'color': '#552583',
        'alt_color': '#FDB927',
        'logo': 'https://a.espncdn.com/i/teamlogos/nba/500/lal.png'
    },
    'PHX': {
        'name': 'Phoenix Suns',
        'full_name': 'Phoenix Suns',
        'city': 'Phoenix',
        'abbreviation': 'PHX',
        'conference': 'Western',
        'division': 'Pacific',
        'color': '#1D1160',
        'alt_color': '#E56020',
        'logo': 'https://a.espncdn.com/i/teamlogos/nba/500/phx.png'
    },
    'SAC': {
        'name': 'Sacramento Kings',
        'full_name': 'Sacramento Kings',
        'city': 'Sacramento',
        'abbreviation': 'SAC',
        'conference': 'Western',
        'division': 'Pacific',
        'color': '#5A2D81',
        'alt_color': '#63727A',
        'logo': 'https://a.espncdn.com/i/teamlogos/nba/500/sac.png'
    },
    
    # Western Conference - Southwest Division
    'DAL': {
        'name': 'Dallas Mavericks',
        'full_name': 'Dallas Mavericks',
        'city': 'Dallas',
        'abbreviation': 'DAL',
        'conference': 'Western',
        'division': 'Southwest',
        'color': '#00538C',
        'alt_color': '#002B5E',
        'logo': 'https://a.espncdn.com/i/teamlogos/nba/500/dal.png'
    },
    'HOU': {
        'name': 'Houston Rockets',
        'full_name': 'Houston Rockets',
        'city': 'Houston',
        'abbreviation': 'HOU',
        'conference': 'Western',
        'division': 'Southwest',
        'color': '#CE1141',
        'alt_color': '#000000',
        'logo': 'https://a.espncdn.com/i/teamlogos/nba/500/hou.png'
    },
    'MEM': {
        'name': 'Memphis Grizzlies',
        'full_name': 'Memphis Grizzlies',
        'city': 'Memphis',
        'abbreviation': 'MEM',
        'conference': 'Western',
        'division': 'Southwest',
        'color': '#5D76A9',
        'alt_color': '#12173F',
        'logo': 'https://a.espncdn.com/i/teamlogos/nba/500/mem.png'
    },
    'NOP': {
        'name': 'New Orleans Pelicans',
        'full_name': 'New Orleans Pelicans',
        'city': 'New Orleans',
        'abbreviation': 'NOP',
        'conference': 'Western',
        'division': 'Southwest',
        'color': '#0C2340',
        'alt_color': '#C8102E',
        'logo': 'https://a.espncdn.com/i/teamlogos/nba/500/no.png'
    },
    'SAS': {
        'name': 'San Antonio Spurs',
        'full_name': 'San Antonio Spurs',
        'city': 'San Antonio',
        'abbreviation': 'SAS',
        'conference': 'Western',
        'division': 'Southwest',
        'color': '#C4CED4',
        'alt_color': '#000000',
        'logo': 'https://a.espncdn.com/i/teamlogos/nba/500/sa.png'
    },
}

# Team name variations for matching
TEAM_NAME_VARIATIONS = {
    'Lakers': 'LAL',
    'L.A. Lakers': 'LAL',
    'Los Angeles Lakers': 'LAL',
    'Celtics': 'BOS',
    'Warriors': 'GSW',
    'Golden State': 'GSW',
    'Nets': 'BKN',
    'Bucks': 'MIL',
    'Heat': 'MIA',
    'Suns': 'PHX',
    'Clippers': 'LAC',
    'L.A. Clippers': 'LAC',
    'Nuggets': 'DEN',
    'Mavericks': 'DAL',
    'Mavs': 'DAL',
    '76ers': 'PHI',
    'Sixers': 'PHI',
    # Add more variations as needed
}


def get_team_logo_url(team_name: str, size: int = 500) -> str:
    """
    Get team logo URL from ESPN CDN
    
    Args:
        team_name: Team name or abbreviation
        size: Logo size (100, 200, 500)
    
    Returns:
        Logo URL
    """
    # Try to find team by abbreviation or name
    team_abbr = None
    
    # Check if it's already an abbreviation
    if team_name.upper() in NBA_TEAMS:
        team_abbr = team_name.upper()
    else:
        # Check variations
        if team_name in TEAM_NAME_VARIATIONS:
            team_abbr = TEAM_NAME_VARIATIONS[team_name]
        else:
            # Search by full name
            for abbr, info in NBA_TEAMS.items():
                if team_name.lower() in info['name'].lower() or team_name.lower() in info['full_name'].lower():
                    team_abbr = abbr
                    break
    
    if team_abbr:
        return NBA_TEAMS[team_abbr]['logo'].replace('/500/', f'/{size}/')
    
    # Default fallback
    logger.warning(f"Could not find logo for team: {team_name}")
    return f"https://a.espncdn.com/i/teamlogos/nba/{size}/nba.png"


def get_team_info(team_identifier: str) -> Optional[Dict]:
    """
    Get complete team information
    
    Args:
        team_identifier: Team name or abbreviation
    
    Returns:
        Dictionary with team info or None
    """
    team_abbr = None
    
    # Check if it's an abbreviation
    if team_identifier.upper() in NBA_TEAMS:
        team_abbr = team_identifier.upper()
    else:
        # Check variations
        if team_identifier in TEAM_NAME_VARIATIONS:
            team_abbr = TEAM_NAME_VARIATIONS[team_identifier]
        else:
            # Search by name
            for abbr, info in NBA_TEAMS.items():
                if team_identifier.lower() in info['name'].lower():
                    team_abbr = abbr
                    break
    
    if team_abbr:
        return NBA_TEAMS[team_abbr].copy()
    
    return None


def get_all_teams() -> Dict:
    """Get all NBA teams"""
    return NBA_TEAMS.copy()


def get_teams_by_conference(conference: str) -> Dict:
    """
    Get teams by conference
    
    Args:
        conference: 'Eastern' or 'Western'
    
    Returns:
        Dictionary of teams in that conference
    """
    return {
        abbr: info for abbr, info in NBA_TEAMS.items()
        if info['conference'] == conference
    }


def get_teams_by_division(division: str) -> Dict:
    """
    Get teams by division
    
    Args:
        division: Division name (e.g., 'Atlantic', 'Pacific')
    
    Returns:
        Dictionary of teams in that division
    """
    return {
        abbr: info for abbr, info in NBA_TEAMS.items()
        if info['division'] == division
    }


# Testing
if __name__ == "__main__":
    print("NBA Team Database Test")
    print("=" * 60)
    
    # Test 1: Get all teams
    print(f"\nTotal NBA Teams: {len(NBA_TEAMS)}")
    
    # Test 2: Get team by abbreviation
    print("\nTest: Get Lakers info")
    lakers = get_team_info('LAL')
    if lakers:
        print(f"  Name: {lakers['name']}")
        print(f"  Conference: {lakers['conference']}")
        print(f"  Division: {lakers['division']}")
        print(f"  Color: {lakers['color']}")
    
    # Test 3: Get logo URL
    print("\nTest: Get team logos")
    for team_abbr in ['LAL', 'BOS', 'GSW', 'CHI']:
        logo_url = get_team_logo_url(team_abbr)
        print(f"  {team_abbr}: {logo_url}")
    
    # Test 4: Get teams by conference
    print("\nEastern Conference Teams:")
    eastern = get_teams_by_conference('Eastern')
    print(f"  Count: {len(eastern)}")
    print(f"  Teams: {', '.join(eastern.keys())}")
    
    print("\nWestern Conference Teams:")
    western = get_teams_by_conference('Western')
    print(f"  Count: {len(western)}")
    print(f"  Teams: {', '.join(western.keys())}")
    
    # Test 5: Team name variations
    print("\nTest: Name variations")
    test_names = ['Lakers', 'Golden State', 'Sixers', 'Mavs']
    for name in test_names:
        info = get_team_info(name)
        if info:
            print(f"  '{name}' -> {info['abbreviation']} ({info['name']})")
    
    print("\n" + "=" * 60)
    print("NBA Team Database test complete!")

