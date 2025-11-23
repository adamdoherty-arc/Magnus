"""
MLB Team Database
Complete database of all 30 Major League Baseball teams with abbreviations, full names, and metadata.
"""

MLB_TEAMS = {
    # American League East
    'BAL': {
        'name': 'Baltimore Orioles',
        'full_name': 'Baltimore Orioles',
        'city': 'Baltimore',
        'abbreviation': 'BAL',
        'nickname': 'Orioles',
        'league': 'American',
        'division': 'East',
        'color': '#DF4601',
        'alt_color': '#000000',
        'stadium': 'Oriole Park at Camden Yards'
    },
    'BOS': {
        'name': 'Boston Red Sox',
        'full_name': 'Boston Red Sox',
        'city': 'Boston',
        'abbreviation': 'BOS',
        'nickname': 'Red Sox',
        'league': 'American',
        'division': 'East',
        'color': '#BD3039',
        'alt_color': '#0C2340',
        'stadium': 'Fenway Park'
    },
    'NYY': {
        'name': 'New York Yankees',
        'full_name': 'New York Yankees',
        'city': 'New York',
        'abbreviation': 'NYY',
        'nickname': 'Yankees',
        'league': 'American',
        'division': 'East',
        'color': '#003087',
        'alt_color': '#E4002C',
        'stadium': 'Yankee Stadium'
    },
    'TB': {
        'name': 'Tampa Bay Rays',
        'full_name': 'Tampa Bay Rays',
        'city': 'Tampa Bay',
        'abbreviation': 'TB',
        'nickname': 'Rays',
        'league': 'American',
        'division': 'East',
        'color': '#092C5C',
        'alt_color': '#F5D130',
        'stadium': 'Tropicana Field'
    },
    'TOR': {
        'name': 'Toronto Blue Jays',
        'full_name': 'Toronto Blue Jays',
        'city': 'Toronto',
        'abbreviation': 'TOR',
        'nickname': 'Blue Jays',
        'league': 'American',
        'division': 'East',
        'color': '#134A8E',
        'alt_color': '#1D2D5C',
        'stadium': 'Rogers Centre'
    },

    # American League Central
    'CWS': {
        'name': 'Chicago White Sox',
        'full_name': 'Chicago White Sox',
        'city': 'Chicago',
        'abbreviation': 'CWS',
        'nickname': 'White Sox',
        'league': 'American',
        'division': 'Central',
        'color': '#27251F',
        'alt_color': '#C4CED4',
        'stadium': 'Guaranteed Rate Field'
    },
    'CLE': {
        'name': 'Cleveland Guardians',
        'full_name': 'Cleveland Guardians',
        'city': 'Cleveland',
        'abbreviation': 'CLE',
        'nickname': 'Guardians',
        'league': 'American',
        'division': 'Central',
        'color': '#00385D',
        'alt_color': '#E50022',
        'stadium': 'Progressive Field'
    },
    'DET': {
        'name': 'Detroit Tigers',
        'full_name': 'Detroit Tigers',
        'city': 'Detroit',
        'abbreviation': 'DET',
        'nickname': 'Tigers',
        'league': 'American',
        'division': 'Central',
        'color': '#0C2340',
        'alt_color': '#FA4616',
        'stadium': 'Comerica Park'
    },
    'KC': {
        'name': 'Kansas City Royals',
        'full_name': 'Kansas City Royals',
        'city': 'Kansas City',
        'abbreviation': 'KC',
        'nickname': 'Royals',
        'league': 'American',
        'division': 'Central',
        'color': '#004687',
        'alt_color': '#BD9B60',
        'stadium': 'Kauffman Stadium'
    },
    'MIN': {
        'name': 'Minnesota Twins',
        'full_name': 'Minnesota Twins',
        'city': 'Minnesota',
        'abbreviation': 'MIN',
        'nickname': 'Twins',
        'league': 'American',
        'division': 'Central',
        'color': '#002B5C',
        'alt_color': '#D31145',
        'stadium': 'Target Field'
    },

    # American League West
    'HOU': {
        'name': 'Houston Astros',
        'full_name': 'Houston Astros',
        'city': 'Houston',
        'abbreviation': 'HOU',
        'nickname': 'Astros',
        'league': 'American',
        'division': 'West',
        'color': '#002D62',
        'alt_color': '#EB6E1F',
        'stadium': 'Minute Maid Park'
    },
    'LAA': {
        'name': 'Los Angeles Angels',
        'full_name': 'Los Angeles Angels',
        'city': 'Los Angeles',
        'abbreviation': 'LAA',
        'nickname': 'Angels',
        'league': 'American',
        'division': 'West',
        'color': '#BA0021',
        'alt_color': '#003263',
        'stadium': 'Angel Stadium'
    },
    'OAK': {
        'name': 'Oakland Athletics',
        'full_name': 'Oakland Athletics',
        'city': 'Oakland',
        'abbreviation': 'OAK',
        'nickname': 'Athletics',
        'league': 'American',
        'division': 'West',
        'color': '#003831',
        'alt_color': '#EFB21E',
        'stadium': 'Oakland Coliseum',
        'alternate_names': ["A's", "Athletics"]
    },
    'SEA': {
        'name': 'Seattle Mariners',
        'full_name': 'Seattle Mariners',
        'city': 'Seattle',
        'abbreviation': 'SEA',
        'nickname': 'Mariners',
        'league': 'American',
        'division': 'West',
        'color': '#0C2C56',
        'alt_color': '#005C5C',
        'stadium': 'T-Mobile Park'
    },
    'TEX': {
        'name': 'Texas Rangers',
        'full_name': 'Texas Rangers',
        'city': 'Texas',
        'abbreviation': 'TEX',
        'nickname': 'Rangers',
        'league': 'American',
        'division': 'West',
        'color': '#003278',
        'alt_color': '#C0111F',
        'stadium': 'Globe Life Field'
    },

    # National League East
    'ATL': {
        'name': 'Atlanta Braves',
        'full_name': 'Atlanta Braves',
        'city': 'Atlanta',
        'abbreviation': 'ATL',
        'nickname': 'Braves',
        'league': 'National',
        'division': 'East',
        'color': '#CE1141',
        'alt_color': '#13274F',
        'stadium': 'Truist Park'
    },
    'MIA': {
        'name': 'Miami Marlins',
        'full_name': 'Miami Marlins',
        'city': 'Miami',
        'abbreviation': 'MIA',
        'nickname': 'Marlins',
        'league': 'National',
        'division': 'East',
        'color': '#00A3E0',
        'alt_color': '#EF3340',
        'stadium': 'loanDepot park'
    },
    'NYM': {
        'name': 'New York Mets',
        'full_name': 'New York Mets',
        'city': 'New York',
        'abbreviation': 'NYM',
        'nickname': 'Mets',
        'league': 'National',
        'division': 'East',
        'color': '#002D72',
        'alt_color': '#FF5910',
        'stadium': 'Citi Field'
    },
    'PHI': {
        'name': 'Philadelphia Phillies',
        'full_name': 'Philadelphia Phillies',
        'city': 'Philadelphia',
        'abbreviation': 'PHI',
        'nickname': 'Phillies',
        'league': 'National',
        'division': 'East',
        'color': '#E81828',
        'alt_color': '#002D72',
        'stadium': 'Citizens Bank Park'
    },
    'WSH': {
        'name': 'Washington Nationals',
        'full_name': 'Washington Nationals',
        'city': 'Washington',
        'abbreviation': 'WSH',
        'nickname': 'Nationals',
        'league': 'National',
        'division': 'East',
        'color': '#AB0003',
        'alt_color': '#14225A',
        'stadium': 'Nationals Park'
    },

    # National League Central
    'CHC': {
        'name': 'Chicago Cubs',
        'full_name': 'Chicago Cubs',
        'city': 'Chicago',
        'abbreviation': 'CHC',
        'nickname': 'Cubs',
        'league': 'National',
        'division': 'Central',
        'color': '#0E3386',
        'alt_color': '#CC3433',
        'stadium': 'Wrigley Field'
    },
    'CIN': {
        'name': 'Cincinnati Reds',
        'full_name': 'Cincinnati Reds',
        'city': 'Cincinnati',
        'abbreviation': 'CIN',
        'nickname': 'Reds',
        'league': 'National',
        'division': 'Central',
        'color': '#C6011F',
        'alt_color': '#000000',
        'stadium': 'Great American Ball Park'
    },
    'MIL': {
        'name': 'Milwaukee Brewers',
        'full_name': 'Milwaukee Brewers',
        'city': 'Milwaukee',
        'abbreviation': 'MIL',
        'nickname': 'Brewers',
        'league': 'National',
        'division': 'Central',
        'color': '#12284B',
        'alt_color': '#FFC52F',
        'stadium': 'American Family Field'
    },
    'PIT': {
        'name': 'Pittsburgh Pirates',
        'full_name': 'Pittsburgh Pirates',
        'city': 'Pittsburgh',
        'abbreviation': 'PIT',
        'nickname': 'Pirates',
        'league': 'National',
        'division': 'Central',
        'color': '#27251F',
        'alt_color': '#FDB827',
        'stadium': 'PNC Park'
    },
    'STL': {
        'name': 'St. Louis Cardinals',
        'full_name': 'St. Louis Cardinals',
        'city': 'St. Louis',
        'abbreviation': 'STL',
        'nickname': 'Cardinals',
        'league': 'National',
        'division': 'Central',
        'color': '#C41E3A',
        'alt_color': '#0C2340',
        'stadium': 'Busch Stadium'
    },

    # National League West
    'AZ': {
        'name': 'Arizona Diamondbacks',
        'full_name': 'Arizona Diamondbacks',
        'city': 'Arizona',
        'abbreviation': 'AZ',
        'nickname': 'Diamondbacks',
        'league': 'National',
        'division': 'West',
        'color': '#A71930',
        'alt_color': '#E3D4AD',
        'stadium': 'Chase Field'
    },
    'COL': {
        'name': 'Colorado Rockies',
        'full_name': 'Colorado Rockies',
        'city': 'Colorado',
        'abbreviation': 'COL',
        'nickname': 'Rockies',
        'league': 'National',
        'division': 'West',
        'color': '#33006F',
        'alt_color': '#C4CED4',
        'stadium': 'Coors Field'
    },
    'LAD': {
        'name': 'Los Angeles Dodgers',
        'full_name': 'Los Angeles Dodgers',
        'city': 'Los Angeles',
        'abbreviation': 'LAD',
        'nickname': 'Dodgers',
        'league': 'National',
        'division': 'West',
        'color': '#005A9C',
        'alt_color': '#EF3E42',
        'stadium': 'Dodger Stadium'
    },
    'SD': {
        'name': 'San Diego Padres',
        'full_name': 'San Diego Padres',
        'city': 'San Diego',
        'abbreviation': 'SD',
        'nickname': 'Padres',
        'league': 'National',
        'division': 'West',
        'color': '#2F241D',
        'alt_color': '#FFC425',
        'stadium': 'Petco Park'
    },
    'SF': {
        'name': 'San Francisco Giants',
        'full_name': 'San Francisco Giants',
        'city': 'San Francisco',
        'abbreviation': 'SF',
        'nickname': 'Giants',
        'league': 'National',
        'division': 'West',
        'color': '#FD5A1E',
        'alt_color': '#27251F',
        'stadium': 'Oracle Park'
    },

    # Alternate abbreviations/names
    'ATH': {  # Oakland Athletics alternate
        'name': 'Oakland Athletics',
        'full_name': 'Oakland Athletics',
        'city': 'Oakland',
        'abbreviation': 'OAK',
        'nickname': 'Athletics',
        'league': 'American',
        'division': 'West',
        'color': '#003831',
        'alt_color': '#EFB21E',
        'stadium': 'Oakland Coliseum'
    }
}

# Additional lookup mappings
TEAM_NAME_VARIATIONS = {
    "A's": "Oakland Athletics",
    "Athletics": "Oakland Athletics",
    "Oakland A's": "Oakland Athletics",
    "Chicago C": "Chicago Cubs",
    "Chicago WS": "Chicago White Sox",
    "White Sox": "Chicago White Sox",
    "Los Angeles D": "Los Angeles Dodgers",
    "Los Angeles A": "Los Angeles Angels",
    "New York Y": "New York Yankees",
    "New York M": "New York Mets",
    "San Diego": "San Diego Padres",
    "St. Louis": "St. Louis Cardinals",
    "Tampa Bay": "Tampa Bay Rays",
}

def get_team_by_abbreviation(abbr: str):
    """Get team info by abbreviation."""
    return MLB_TEAMS.get(abbr.upper())

def get_full_team_name(abbr_or_partial: str) -> str:
    """
    Get full team name from abbreviation or partial name.

    Args:
        abbr_or_partial: Team abbreviation (e.g., 'LAD') or partial name (e.g., 'Los Angeles D')

    Returns:
        Full team name (e.g., 'Los Angeles Dodgers')
    """
    # Check direct abbreviation lookup
    team = MLB_TEAMS.get(abbr_or_partial.upper())
    if team:
        return team['full_name']

    # Check variations
    if abbr_or_partial in TEAM_NAME_VARIATIONS:
        return TEAM_NAME_VARIATIONS[abbr_or_partial]

    # Fuzzy match on city
    for abbr, team_info in MLB_TEAMS.items():
        if abbr_or_partial.lower() in team_info['city'].lower():
            return team_info['full_name']

    return abbr_or_partial  # Return as-is if not found
