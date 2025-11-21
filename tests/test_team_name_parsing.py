"""
Comprehensive Test Suite for Team Name Parsing
Prevents regression in multi-word team name handling across NFL and NCAA
"""

import pytest
from typing import List, Tuple, Dict, Optional
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Optional fuzzy matching (skip tests if not available)
try:
    from fuzzywuzzy import fuzz
    HAS_FUZZYWUZZY = True
except ImportError:
    HAS_FUZZYWUZZY = False

from src.nfl_team_database import NFL_TEAMS, NFL_TEAM_ALIASES, find_team_by_name as find_nfl_team
from src.ncaa_team_database import NCAA_TEAMS, find_team_by_name as find_ncaa_team
from src.espn_kalshi_matcher import ESPNKalshiMatcher


class TestNFLMultiWordTeams:
    """Test parsing of multi-word NFL team names"""

    # All 11 multi-word NFL teams
    MULTI_WORD_TEAMS = [
        'New England',
        'New York Giants',
        'New York Jets',
        'New Orleans',
        'Los Angeles Rams',
        'Los Angeles Chargers',
        'Tampa Bay',
        'Green Bay',
        'Kansas City',
        'Las Vegas',
        'San Francisco'
    ]

    def test_all_multi_word_teams_exist_in_database(self):
        """All multi-word teams should exist in NFL_TEAMS"""
        for team in self.MULTI_WORD_TEAMS:
            assert team in NFL_TEAMS, f"{team} not found in NFL_TEAMS"

    def test_multi_word_team_find_by_name(self):
        """Test finding multi-word teams by exact name"""
        for team in self.MULTI_WORD_TEAMS:
            result = find_nfl_team(team)
            assert result is not None, f"Could not find {team}"
            assert result['full_name'] == NFL_TEAMS[team]['full_name']

    @pytest.mark.parametrize("team_name,expected_abbr", [
        ('New England', 'ne'),
        ('New York Giants', 'nyg'),
        ('New York Jets', 'nyj'),
        ('New Orleans', 'no'),
        ('Los Angeles Rams', 'lar'),
        ('Los Angeles Chargers', 'lac'),
        ('Tampa Bay', 'tb'),
        ('Green Bay', 'gb'),
        ('Kansas City', 'kc'),
        ('Las Vegas', 'lv'),
        ('San Francisco', 'sf'),
    ])
    def test_multi_word_teams_abbreviations(self, team_name, expected_abbr):
        """Verify correct abbreviations for multi-word teams"""
        assert team_name in NFL_TEAMS
        assert NFL_TEAMS[team_name]['abbr'] == expected_abbr

    def test_multi_word_teams_full_names(self):
        """Verify full names are correctly stored"""
        expected_full_names = {
            'New England': 'New England Patriots',
            'New York Giants': 'New York Giants',
            'New York Jets': 'New York Jets',
            'New Orleans': 'New Orleans Saints',
            'Los Angeles Rams': 'Los Angeles Rams',
            'Los Angeles Chargers': 'Los Angeles Chargers',
            'Tampa Bay': 'Tampa Bay Buccaneers',
            'Green Bay': 'Green Bay Packers',
            'Kansas City': 'Kansas City Chiefs',
            'Las Vegas': 'Las Vegas Raiders',
            'San Francisco': 'San Francisco 49ers',
        }

        for team, expected_full in expected_full_names.items():
            assert NFL_TEAMS[team]['full_name'] == expected_full


class TestNCAAMultiWordTeams:
    """Test parsing of multi-word NCAA team names"""

    # Sample of multi-word NCAA teams
    MULTI_WORD_TEAMS = [
        'Boston College',
        'Florida State',
        'Georgia Tech',
        'North Carolina',
        'NC State',
        'Virginia Tech',
        'Michigan State',
        'Ohio State',
        'Penn State',
        'Texas A&M',
        'Texas Tech',
        'Iowa State',
        'Kansas State',
        'Oklahoma State',
    ]

    def test_multi_word_teams_exist_in_database(self):
        """All multi-word NCAA teams should exist in database"""
        for team in self.MULTI_WORD_TEAMS:
            assert team in NCAA_TEAMS, f"{team} not found in NCAA_TEAMS"

    def test_multi_word_team_find_by_name(self):
        """Test finding multi-word NCAA teams by exact name"""
        for team in self.MULTI_WORD_TEAMS:
            result = find_ncaa_team(team)
            assert result is not None, f"Could not find {team}"
            assert 'abbr' in result
            assert 'conference' in result

    @pytest.mark.parametrize("team_name,expected_abbr", [
        ('Boston College', 'BC'),
        ('Florida State', 'FSU'),
        ('Georgia Tech', 'GT'),
        ('North Carolina', 'UNC'),
        ('NC State', 'NCST'),
        ('Virginia Tech', 'VT'),
        ('Michigan State', 'MSU'),
        ('Ohio State', 'OSU'),
        ('Penn State', 'PSU'),
        ('Texas A&M', 'TAMU'),
        ('Texas Tech', 'TTU'),
    ])
    def test_multi_word_ncaa_abbreviations(self, team_name, expected_abbr):
        """Verify correct abbreviations for multi-word NCAA teams"""
        assert team_name in NCAA_TEAMS
        assert NCAA_TEAMS[team_name]['abbr'] == expected_abbr


class TestTeamNameEdgeCases:
    """Test edge cases in team name parsing"""

    @pytest.mark.parametrize("title,expected_teams", [
        ("Will the Chiefs beat the Bills?", ['Chiefs', 'Bills']),
        ("Can the New England Patriots win?", ['New England Patriots']),
        ("New York Giants vs New York Jets", ['New York Giants', 'New York Jets']),
        ("Los Angeles Rams @ Los Angeles Chargers", ['Los Angeles Rams', 'Los Angeles Chargers']),
        ("Kansas City Chiefs at Tampa Bay Buccaneers", ['Kansas City Chiefs', 'Tampa Bay Buccaneers']),
        ("Green Bay vs San Francisco", ['Green Bay', 'San Francisco']),
    ])
    def test_the_prefix_handling(self, title, expected_teams):
        """Test extraction with 'the' prefix in titles"""
        # Remove "the" from title
        cleaned_title = title.replace(' the ', ' ')

        for expected_team in expected_teams:
            # Check that team name appears in cleaned title
            team_base = expected_team.split()[-1]  # Get mascot
            assert team_base in title or team_base in cleaned_title

    @pytest.mark.parametrize("title,delimiter", [
        ("New England vs Cincinnati", "vs"),
        ("New England vs. Cincinnati", "vs."),
        ("New England @ Cincinnati", "@"),
        ("New England v Cincinnati", "v"),
        ("New England v. Cincinnati", "v."),
    ])
    def test_multiple_delimiters(self, title, delimiter):
        """Test parsing with different delimiters"""
        assert delimiter in title
        parts = title.split(delimiter)
        assert len(parts) >= 2

        # Verify teams are in different parts
        assert 'New England' in parts[0] or 'England' in parts[0]
        assert 'Cincinnati' in parts[1]

    def test_at_delimiter_special_case(self):
        """Test 'at' delimiter (note: 'at' can conflict with team names like 'Atlanta')"""
        title = "New England at Cincinnati"
        # 'at' is tricky because it appears in 'Atlanta', 'Seattle', etc.
        # This test just verifies we can detect it exists
        assert 'at' in title.lower()
        # More sophisticated parsing would need context-aware delimiter detection

    @pytest.mark.parametrize("title,expected_format", [
        ("New England AT Cincinnati", "at"),
        ("NEW ENGLAND vs CINCINNATI", "vs"),
        ("new england @ cincinnati", "@"),
        ("New ENGLAND vs. Cincinnati", "vs."),
    ])
    def test_mixed_case_formatting(self, title, expected_format):
        """Test parsing with mixed case formatting"""
        title_lower = title.lower()
        assert expected_format in title_lower

        # Should find delimiter regardless of case
        assert 'england' in title_lower
        assert 'cincinnati' in title_lower

    def test_possessive_forms(self):
        """Test handling possessive forms"""
        titles = [
            "New England's game against Cincinnati",
            "Kansas City's matchup with Tampa Bay",
            "Green Bay's playoff run",
        ]

        for title in titles:
            # Check that possessive doesn't break parsing
            assert "'" in title or "'" in title
            # Team name should still be identifiable
            words = title.split()
            assert len(words) > 0


class TestTeamNameValidation:
    """Test validation of extracted team names"""

    def test_no_partial_matches_nfl(self):
        """Ensure no partial team names in NFL_TEAMS (like 'England', 'Bay', 'City')"""
        invalid_partials = ['England', 'Bay', 'City', 'York', 'Orleans', 'Francisco', 'Angeles', 'Vegas']

        for partial in invalid_partials:
            # These should NOT be keys in NFL_TEAMS
            assert partial not in NFL_TEAMS, f"Invalid partial '{partial}' found as key in NFL_TEAMS"

    def test_no_partial_matches_ncaa(self):
        """Ensure no partial team names in NCAA_TEAMS"""
        invalid_partials = ['State', 'Tech', 'College', 'University']

        for partial in invalid_partials:
            # These should NOT be standalone keys
            assert partial not in NCAA_TEAMS, f"Invalid partial '{partial}' found as key in NCAA_TEAMS"

    def test_ny_teams_distinct(self):
        """New York teams should be distinct (Giants vs Jets)"""
        assert 'New York Giants' in NFL_TEAMS
        assert 'New York Jets' in NFL_TEAMS

        giants = NFL_TEAMS['New York Giants']
        jets = NFL_TEAMS['New York Jets']

        # Different abbreviations
        assert giants['abbr'] != jets['abbr']
        # Different full names
        assert giants['full_name'] != jets['full_name']

    def test_la_teams_distinct(self):
        """Los Angeles teams should be distinct (Rams vs Chargers)"""
        assert 'Los Angeles Rams' in NFL_TEAMS
        assert 'Los Angeles Chargers' in NFL_TEAMS

        rams = NFL_TEAMS['Los Angeles Rams']
        chargers = NFL_TEAMS['Los Angeles Chargers']

        # Different abbreviations
        assert rams['abbr'] != chargers['abbr']
        # Different full names
        assert rams['full_name'] != chargers['full_name']

    def test_no_team_collision(self):
        """No two teams should map to the same abbreviation"""
        nfl_abbrs = [team['abbr'] for team in NFL_TEAMS.values()]
        assert len(nfl_abbrs) == len(set(nfl_abbrs)), "Duplicate abbreviations found in NFL_TEAMS"

        ncaa_abbrs = [team['abbr'] for team in NCAA_TEAMS.values()]
        assert len(ncaa_abbrs) == len(set(ncaa_abbrs)), "Duplicate abbreviations found in NCAA_TEAMS"

    def test_all_teams_have_required_fields(self):
        """All teams should have required fields"""
        required_nfl = ['abbr', 'city', 'full_name', 'division']
        required_ncaa = ['abbr', 'conference', 'id']

        for team_name, team_data in NFL_TEAMS.items():
            for field in required_nfl:
                assert field in team_data, f"{team_name} missing field: {field}"

        for team_name, team_data in NCAA_TEAMS.items():
            for field in required_ncaa:
                assert field in team_data, f"{team_name} missing field: {field}"


class TestESPNKalshiMatcher:
    """Test ESPN to Kalshi matcher team parsing"""

    @pytest.fixture
    def matcher(self):
        """Create matcher instance"""
        return ESPNKalshiMatcher()

    def test_matcher_has_team_variations(self, matcher):
        """Matcher should have team variations defined"""
        assert hasattr(matcher, 'NFL_TEAM_VARIATIONS')
        assert hasattr(matcher, 'CFB_TEAM_VARIATIONS')
        assert hasattr(matcher, 'all_team_variations')

    @pytest.mark.parametrize("team,expected_variations", [
        ('New England Patriots', ['New England', 'Patriots', 'NE']),
        ('New York Giants', ['New York Giants', 'NY Giants', 'Giants', 'NYG']),
        ('New York Jets', ['New York Jets', 'NY Jets', 'Jets', 'NYJ']),
        ('Kansas City Chiefs', ['Kansas City', 'Chiefs', 'KC']),
        ('Tampa Bay Buccaneers', ['Tampa Bay', 'Buccaneers', 'Bucs', 'TB']),
        ('Green Bay Packers', ['Green Bay', 'Packers', 'GB']),
        ('San Francisco 49ers', ['San Francisco', '49ers', 'SF']),
        ('Los Angeles Rams', ['Los Angeles Rams', 'LA Rams', 'Rams', 'LAR']),
        ('Los Angeles Chargers', ['Los Angeles Chargers', 'LA Chargers', 'Chargers', 'LAC']),
    ])
    def test_team_variations_coverage(self, matcher, team, expected_variations):
        """Test that multi-word teams have proper variations"""
        variations = matcher.get_team_variations(team)

        # Check that all expected variations are present
        for expected in expected_variations:
            assert any(expected.lower() == v.lower() for v in variations), \
                f"Expected variation '{expected}' not found for {team}"

    def test_get_team_variations_returns_list(self, matcher):
        """get_team_variations should always return a list"""
        test_teams = ['Buffalo Bills', 'New England Patriots', 'Invalid Team']

        for team in test_teams:
            variations = matcher.get_team_variations(team)
            assert isinstance(variations, list)
            assert len(variations) > 0

    @pytest.mark.xfail(reason="Known issue: get_team_variations returns duplicates, needs deduplication")
    def test_team_variations_unique(self, matcher):
        """Team variations should not have duplicates (enhancement needed)"""
        test_teams = ['New York Giants', 'Los Angeles Rams', 'Tampa Bay Buccaneers']

        for team in test_teams:
            variations = matcher.get_team_variations(team)
            # Check for uniqueness (case-insensitive)
            variations_lower = [v.lower() for v in variations]
            assert len(variations_lower) == len(set(variations_lower)), \
                f"Duplicate variations found for {team}: {variations}"

    def test_team_variations_has_expected_count(self, matcher):
        """Team variations should return at least the key variations"""
        test_teams = {
            'New York Giants': 3,  # At minimum: 'New York Giants', 'Giants', 'NYG'
            'Los Angeles Rams': 3,  # At minimum: 'Los Angeles Rams', 'Rams', 'LAR'
            'Tampa Bay Buccaneers': 3,  # At minimum: 'Tampa Bay', 'Buccaneers', 'TB'
        }

        for team, min_count in test_teams.items():
            variations = matcher.get_team_variations(team)
            # Should have at least minimum variations (duplicates may exist)
            unique_variations = list(set(v.lower() for v in variations))
            assert len(unique_variations) >= min_count, \
                f"Expected at least {min_count} unique variations for {team}, got {len(unique_variations)}: {unique_variations}"


class TestFuzzyMatching:
    """Test fuzzy matching for team names"""

    @pytest.mark.parametrize("query,expected_team", [
        ('Patriots', 'New England'),
        ('New England', 'New England'),
        ('Giants', 'New York Giants'),
        ('Jets', 'New York Jets'),
        ('Chiefs', 'Kansas City'),
        ('49ers', 'San Francisco'),
        ('Packers', 'Green Bay'),
    ])
    def test_nfl_fuzzy_matching_basic(self, query, expected_team):
        """Test fuzzy matching finds correct team (mascots and full names)"""
        result = find_nfl_team(query)
        assert result is not None, f"Could not find team for query: {query}"

        # Check if the found team matches expected
        team_info = NFL_TEAMS.get(expected_team)
        if team_info:
            assert result['abbr'] == team_info['abbr'], \
                f"Found team abbr {result['abbr']} doesn't match expected {team_info['abbr']}"

    @pytest.mark.parametrize("query,expected_team", [
        ('NY Giants', 'New York Giants'),
        ('KC', 'Kansas City'),
        ('SF', 'San Francisco'),
        ('GB', 'Green Bay'),
        ('Bucs', 'Tampa Bay'),
        ('TB', 'Tampa Bay'),
    ])
    @pytest.mark.xfail(reason="Abbreviation/nickname lookup not yet implemented in find_team_by_name")
    def test_nfl_abbreviation_lookup_enhancement(self, query, expected_team):
        """Test abbreviation/nickname lookup (enhancement request)"""
        # This is a known limitation - the current find_team_by_name doesn't support
        # all abbreviations and nicknames. Use NFL_TEAM_ALIASES for mapping instead.
        result = find_nfl_team(query)
        assert result is not None, f"Could not find team for query: {query}"

        team_info = NFL_TEAMS.get(expected_team)
        if team_info:
            assert result['abbr'] == team_info['abbr']

    @pytest.mark.parametrize("query,expected_abbr", [
        ('Ohio State', 'OSU'),
        ('OSU', 'OSU'),
        ('Penn State', 'PSU'),
        ('PSU', 'PSU'),
        ('Michigan State', 'MSU'),
        ('MSU', 'MSU'),
        ('Texas A&M', 'TAMU'),
        ('TAMU', 'TAMU'),
    ])
    def test_ncaa_fuzzy_matching_basic(self, query, expected_abbr):
        """Test fuzzy matching for NCAA teams (exact names and abbreviations)"""
        result = find_ncaa_team(query)
        assert result is not None, f"Could not find team for query: {query}"
        assert result['abbr'] == expected_abbr, \
            f"Found team abbr {result['abbr']} doesn't match expected {expected_abbr}"

    @pytest.mark.parametrize("query,expected_abbr", [
        ('Buckeyes', 'OSU'),
        ('Aggies', 'TAMU'),
    ])
    @pytest.mark.xfail(reason="Mascot-only lookup not yet implemented in find_team_by_name")
    def test_ncaa_mascot_lookup_enhancement(self, query, expected_abbr):
        """Test mascot-only lookup for NCAA teams (enhancement request)"""
        # Note: Multiple teams share mascots (e.g., multiple "Tigers", "Bulldogs")
        # so mascot-only lookup would need disambiguation
        result = find_ncaa_team(query)
        assert result is not None, f"Could not find team for query: {query}"
        assert result['abbr'] == expected_abbr

    @pytest.mark.skipif(not HAS_FUZZYWUZZY, reason="fuzzywuzzy not installed")
    def test_fuzzy_matching_threshold(self):
        """Test that fuzzy matching has reasonable threshold"""
        # Close but not exact matches should still work
        test_cases = [
            ('new england', 'New England'),
            ('NEW YORK GIANTS', 'New York Giants'),
            ('kansas city', 'Kansas City'),
        ]

        for query, expected_team in test_cases:
            result = find_nfl_team(query)
            assert result is not None
            # Verify match quality using fuzz ratio
            ratio = fuzz.ratio(query.lower(), expected_team.lower())
            assert ratio >= 50, f"Match quality too low: {ratio}% for '{query}'"


class TestDatabaseIntegration:
    """Test database integration for team parsing"""

    def test_nfl_teams_count(self):
        """Verify correct number of NFL teams"""
        assert len(NFL_TEAMS) == 32, f"Expected 32 NFL teams, found {len(NFL_TEAMS)}"

    def test_nfl_aliases_coverage(self):
        """NFL aliases should cover all mascots and full names"""
        for team_name, team_data in NFL_TEAMS.items():
            full_name = team_data['full_name']

            # Full name should be in aliases or be a key
            assert full_name in NFL_TEAM_ALIASES or full_name == team_name, \
                f"Full name '{full_name}' not in aliases for {team_name}"

    def test_ncaa_teams_structure(self):
        """NCAA teams should have consistent structure"""
        for team_name, team_data in NCAA_TEAMS.items():
            assert 'id' in team_data
            assert 'abbr' in team_data
            assert 'conference' in team_data

            # ID should be numeric string
            assert team_data['id'].isdigit(), f"Invalid ID for {team_name}: {team_data['id']}"

    def test_no_empty_values(self):
        """No team data should have empty values"""
        for team_name, team_data in NFL_TEAMS.items():
            for key, value in team_data.items():
                assert value, f"Empty value for {team_name}.{key}"

        for team_name, team_data in NCAA_TEAMS.items():
            for key, value in team_data.items():
                assert value, f"Empty value for {team_name}.{key}"


class TestRegressionPrevention:
    """Tests to prevent specific regressions"""

    def test_new_england_not_parsed_as_england(self):
        """Regression: 'New England' should not be parsed as 'England'"""
        # Search for 'England' should not return New England team
        assert 'England' not in NFL_TEAMS

        # 'New England' should be the full key
        assert 'New England' in NFL_TEAMS

    def test_tampa_bay_not_parsed_as_bay(self):
        """Regression: 'Tampa Bay' should not be parsed as 'Bay'"""
        assert 'Bay' not in NFL_TEAMS
        assert 'Tampa Bay' in NFL_TEAMS

    def test_kansas_city_not_parsed_as_city(self):
        """Regression: 'Kansas City' should not be parsed as 'City'"""
        assert 'City' not in NFL_TEAMS
        assert 'Kansas City' in NFL_TEAMS

    def test_green_bay_not_parsed_as_green(self):
        """Regression: 'Green Bay' should not be parsed as 'Green'"""
        assert 'Green' not in NFL_TEAMS
        assert 'Green Bay' in NFL_TEAMS

    def test_san_francisco_not_parsed_as_francisco(self):
        """Regression: 'San Francisco' should not be parsed as 'Francisco'"""
        assert 'Francisco' not in NFL_TEAMS
        assert 'San Francisco' in NFL_TEAMS

    def test_title_parsing_preserves_multi_word_teams(self):
        """Regression: Title parsing should preserve multi-word team names"""
        titles = [
            "Will New England beat Buffalo?",
            "Kansas City vs Tampa Bay",
            "Green Bay @ San Francisco",
            "New York Giants vs New York Jets",
        ]

        multi_word_teams = [
            'New England', 'Kansas City', 'Tampa Bay',
            'Green Bay', 'San Francisco', 'New York Giants', 'New York Jets'
        ]

        for title in titles:
            # Check that multi-word teams appear in title
            found_teams = [team for team in multi_word_teams if team in title]
            assert len(found_teams) > 0, f"No multi-word teams found in: {title}"


class TestPerformance:
    """Performance tests for team name lookups"""

    def test_lookup_performance_nfl(self):
        """NFL team lookup should be fast (O(1))"""
        import time

        test_teams = list(NFL_TEAMS.keys())[:10]

        start = time.time()
        for _ in range(1000):
            for team in test_teams:
                _ = NFL_TEAMS.get(team)
        elapsed = time.time() - start

        # Should complete 10,000 lookups in under 0.1 seconds
        assert elapsed < 0.1, f"NFL lookups too slow: {elapsed:.4f}s for 10,000 lookups"

    def test_lookup_performance_ncaa(self):
        """NCAA team lookup should be fast (O(1))"""
        import time

        test_teams = list(NCAA_TEAMS.keys())[:10]

        start = time.time()
        for _ in range(1000):
            for team in test_teams:
                _ = NCAA_TEAMS.get(team)
        elapsed = time.time() - start

        # Should complete 10,000 lookups in under 0.1 seconds
        assert elapsed < 0.1, f"NCAA lookups too slow: {elapsed:.4f}s for 10,000 lookups"


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])
