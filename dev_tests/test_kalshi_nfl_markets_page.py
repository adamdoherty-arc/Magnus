"""
Test Suite for Kalshi NFL Markets Dashboard
Comprehensive testing for all components and functionality

Run with: pytest test_kalshi_nfl_markets_page.py -v
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import sys

# Import components to test
# Note: This assumes the file is in the project root
try:
    from kalshi_nfl_markets_page import (
        MarketDataManager,
        ChartBuilder,
        apply_filters,
        add_to_watchlist,
        remove_from_watchlist,
        initialize_watchlist
    )
except ImportError:
    print("Warning: Could not import kalshi_nfl_markets_page. Some tests may fail.")


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def sample_market_data():
    """Create sample market data for testing"""
    return {
        'id': 1,
        'ticker': 'NFL-TEST-001',
        'title': 'Will the Chiefs beat the Bills by more than 3 points?',
        'market_type': 'nfl',
        'home_team': 'Chiefs',
        'away_team': 'Bills',
        'yes_price': 0.65,
        'no_price': 0.35,
        'volume': 5000.0,
        'close_time': datetime.now() + timedelta(days=2),
        'confidence_score': 85.0,
        'edge_percentage': 5.5,
        'recommended_action': 'buy',
        'reasoning': 'Strong value opportunity based on team performance'
    }


@pytest.fixture
def sample_dataframe():
    """Create sample DataFrame for testing"""
    data = {
        'ticker': ['NFL-001', 'NFL-002', 'NFL-003', 'NFL-004'],
        'title': [
            'Chiefs -3.5 spread vs Bills',
            'Patrick Mahomes over 2.5 TD passes',
            'Total points over 47.5',
            'Packers to win moneyline'
        ],
        'home_team': ['Chiefs', 'Chiefs', 'Bills', 'Packers'],
        'away_team': ['Bills', 'Bills', 'Chiefs', 'Bears'],
        'yes_price': [0.65, 0.58, 0.52, 0.71],
        'no_price': [0.35, 0.42, 0.48, 0.29],
        'volume': [5000, 3000, 8000, 2000],
        'confidence': [85, 72, 68, 91],
        'edge_pct': [5.5, 3.2, 1.8, 7.2],
        'days_to_close': [2, 2, 3, 1],
        'bet_type': ['Spread', 'Player Prop', 'Total', 'Moneyline'],
        'player_name': [None, 'Patrick Mahomes', None, None],
        'risk_level': ['Low', 'Medium', 'Medium', 'Low']
    }
    return pd.DataFrame(data)


@pytest.fixture
def sample_price_history():
    """Create sample price history data"""
    dates = pd.date_range(start='2025-11-01', periods=10, freq='H')
    data = {
        'snapshot_time': dates,
        'yes_price': np.linspace(0.50, 0.65, 10),
        'no_price': np.linspace(0.50, 0.35, 10),
        'volume': np.random.randint(100, 1000, 10)
    }
    return pd.DataFrame(data)


@pytest.fixture
def mock_db_manager():
    """Create mock database manager"""
    mock = Mock()
    mock.get_connection.return_value = Mock()
    return mock


# ============================================================================
# TEST: MarketDataManager
# ============================================================================

class TestMarketDataManager:
    """Test MarketDataManager class"""

    def test_calculate_days_to_close_future(self):
        """Test days calculation for future dates"""
        future_date = datetime.now() + timedelta(days=5)
        days = MarketDataManager._calculate_days_to_close(future_date)
        assert days == 5

    def test_calculate_days_to_close_today(self):
        """Test days calculation for today"""
        today = datetime.now()
        days = MarketDataManager._calculate_days_to_close(today)
        assert days == 0

    def test_calculate_days_to_close_past(self):
        """Test days calculation for past dates (should return 0)"""
        past_date = datetime.now() - timedelta(days=2)
        days = MarketDataManager._calculate_days_to_close(past_date)
        assert days == 0

    def test_calculate_days_to_close_with_timezone(self):
        """Test days calculation with timezone-aware datetime"""
        from datetime import timezone
        future_date = datetime.now(timezone.utc) + timedelta(days=3)
        days = MarketDataManager._calculate_days_to_close(future_date)
        assert days == 3

    def test_calculate_days_to_close_string_input(self):
        """Test days calculation with ISO string input"""
        future_date = (datetime.now() + timedelta(days=7)).isoformat()
        days = MarketDataManager._calculate_days_to_close(future_date)
        assert days == 7

    def test_calculate_days_to_close_none(self):
        """Test days calculation with None input"""
        days = MarketDataManager._calculate_days_to_close(None)
        assert days == 0

    def test_extract_bet_type_spread(self):
        """Test bet type extraction for spread"""
        assert MarketDataManager._extract_bet_type("Chiefs -3.5 spread") == "Spread"
        assert MarketDataManager._extract_bet_type("Bills to cover 7 points") == "Spread"

    def test_extract_bet_type_total(self):
        """Test bet type extraction for totals"""
        assert MarketDataManager._extract_bet_type("Over 47.5 total points") == "Total"
        assert MarketDataManager._extract_bet_type("Under 52 points") == "Total"

    def test_extract_bet_type_moneyline(self):
        """Test bet type extraction for moneyline"""
        assert MarketDataManager._extract_bet_type("Chiefs to win outright") == "Moneyline"
        assert MarketDataManager._extract_bet_type("Bills moneyline") == "Moneyline"

    def test_extract_bet_type_player_prop(self):
        """Test bet type extraction for player props"""
        assert MarketDataManager._extract_bet_type("Mahomes over 2.5 touchdown passes") == "Player Prop"
        assert MarketDataManager._extract_bet_type("300+ yards passing") == "Player Prop"

    def test_extract_bet_type_parlay(self):
        """Test bet type extraction for parlays"""
        assert MarketDataManager._extract_bet_type("Chiefs and Bills parlay") == "Parlay"

    def test_extract_bet_type_other(self):
        """Test bet type extraction for unknown types"""
        assert MarketDataManager._extract_bet_type("Will it rain during the game?") == "Other"

    def test_extract_player_name_found(self):
        """Test player name extraction when present"""
        result = MarketDataManager._extract_player_name("Patrick Mahomes to throw 3 TDs")
        assert result == "Patrick Mahomes"

    def test_extract_player_name_not_found(self):
        """Test player name extraction when not present"""
        result = MarketDataManager._extract_player_name("Chiefs to win by 7")
        assert result is None

    def test_get_risk_level_low(self):
        """Test risk level for high confidence"""
        assert MarketDataManager._get_risk_level(85) == "Low"
        assert MarketDataManager._get_risk_level(80) == "Low"

    def test_get_risk_level_medium(self):
        """Test risk level for medium confidence"""
        assert MarketDataManager._get_risk_level(70) == "Medium"
        assert MarketDataManager._get_risk_level(60) == "Medium"

    def test_get_risk_level_high(self):
        """Test risk level for low confidence"""
        assert MarketDataManager._get_risk_level(55) == "High"
        assert MarketDataManager._get_risk_level(40) == "High"

    def test_get_team_list(self, sample_dataframe):
        """Test team list extraction"""
        manager = MarketDataManager()
        teams = manager.get_team_list(sample_dataframe)

        assert isinstance(teams, list)
        assert 'Chiefs' in teams
        assert 'Bills' in teams
        assert 'Packers' in teams
        assert 'Bears' in teams
        assert len(teams) == 4  # 4 unique teams

    def test_get_team_list_sorted(self, sample_dataframe):
        """Test team list is alphabetically sorted"""
        manager = MarketDataManager()
        teams = manager.get_team_list(sample_dataframe)

        assert teams == sorted(teams)


# ============================================================================
# TEST: ChartBuilder
# ============================================================================

class TestChartBuilder:
    """Test ChartBuilder class"""

    def test_create_odds_movement_chart(self, sample_price_history):
        """Test odds movement chart creation"""
        fig = ChartBuilder.create_odds_movement_chart(
            sample_price_history,
            "Test Market"
        )

        assert fig is not None
        assert len(fig.data) == 2  # Yes and No traces
        assert fig.data[0].name == 'Yes Price'
        assert fig.data[1].name == 'No Price'

    def test_create_odds_movement_chart_empty(self):
        """Test odds movement chart with empty data"""
        empty_df = pd.DataFrame()
        fig = ChartBuilder.create_odds_movement_chart(empty_df, "Empty")

        assert fig is not None
        assert len(fig.data) == 0  # No traces for empty data

    def test_create_volume_chart(self, sample_dataframe):
        """Test volume chart creation"""
        fig = ChartBuilder.create_volume_chart(sample_dataframe)

        assert fig is not None
        assert len(fig.data) == 1  # Single bar trace
        assert fig.layout.title.text == "Top 10 Markets by Volume"

    def test_create_volume_chart_sorting(self, sample_dataframe):
        """Test volume chart shows highest volume markets"""
        fig = ChartBuilder.create_volume_chart(sample_dataframe)

        # Should show markets sorted by volume (descending)
        # Our sample data has Bills-Chiefs total with 8000 volume as highest
        assert fig.data[0].y[0] == 8000  # Highest volume first

    def test_create_confidence_distribution(self, sample_dataframe):
        """Test confidence distribution chart"""
        fig = ChartBuilder.create_confidence_distribution(sample_dataframe)

        assert fig is not None
        assert len(fig.data) == 1  # Single histogram trace
        assert fig.layout.title.text == "Confidence Score Distribution"

    def test_create_opportunity_heatmap_with_data(self, sample_dataframe):
        """Test opportunity heatmap creation"""
        fig = ChartBuilder.create_opportunity_heatmap(sample_dataframe)

        assert fig is not None
        # Should have data since we have teams and bet types

    def test_create_opportunity_heatmap_empty(self):
        """Test opportunity heatmap with no team data"""
        df = pd.DataFrame({
            'home_team': [None, None],
            'bet_type': ['Spread', 'Total'],
            'edge_pct': [5.0, 3.0]
        })
        fig = ChartBuilder.create_opportunity_heatmap(df)

        assert fig is not None
        # Should handle gracefully

    def test_create_edge_scatter(self, sample_dataframe):
        """Test edge vs confidence scatter plot"""
        fig = ChartBuilder.create_edge_scatter(sample_dataframe)

        assert fig is not None
        assert len(fig.data) == 1  # Single scatter trace
        assert fig.layout.title.text == "Market Quality: Edge vs Confidence"

    def test_create_edge_scatter_bubble_sizes(self, sample_dataframe):
        """Test scatter plot bubble sizes correlate with volume"""
        fig = ChartBuilder.create_edge_scatter(sample_dataframe)

        # Marker sizes should be based on volume
        # Largest volume (8000) should have largest marker
        marker_sizes = fig.data[0].marker.size
        assert max(marker_sizes) == 8000 / 100  # Volume divided by 100


# ============================================================================
# TEST: Filtering
# ============================================================================

class TestFiltering:
    """Test filter application logic"""

    def test_apply_search_filter(self, sample_dataframe):
        """Test search filter application"""
        filters = {'search': 'chiefs'}
        result = apply_filters(sample_dataframe, filters)

        assert len(result) == 3  # 3 markets mention Chiefs
        assert all('chiefs' in title.lower() or 'Chiefs' in str(home) or 'Chiefs' in str(away)
                   for title, home, away in zip(result['title'], result['home_team'], result['away_team']))

    def test_apply_search_filter_case_insensitive(self, sample_dataframe):
        """Test search is case-insensitive"""
        filters_lower = {'search': 'chiefs'}
        filters_upper = {'search': 'CHIEFS'}
        filters_mixed = {'search': 'ChIeFs'}

        result_lower = apply_filters(sample_dataframe, filters_lower)
        result_upper = apply_filters(sample_dataframe, filters_upper)
        result_mixed = apply_filters(sample_dataframe, filters_mixed)

        assert len(result_lower) == len(result_upper) == len(result_mixed)

    def test_apply_search_filter_player_name(self, sample_dataframe):
        """Test search by player name"""
        filters = {'search': 'mahomes'}
        result = apply_filters(sample_dataframe, filters)

        assert len(result) == 1
        assert result.iloc[0]['player_name'] == 'Patrick Mahomes'

    def test_apply_team_filter(self, sample_dataframe):
        """Test team filter application"""
        filters = {'teams': ['Chiefs']}
        result = apply_filters(sample_dataframe, filters)

        assert len(result) == 3  # Chiefs is home or away in 3 markets
        assert all('Chiefs' in [home, away]
                   for home, away in zip(result['home_team'], result['away_team']))

    def test_apply_team_filter_multiple(self, sample_dataframe):
        """Test multiple team filter"""
        filters = {'teams': ['Chiefs', 'Packers']}
        result = apply_filters(sample_dataframe, filters)

        assert len(result) == 4  # All markets involve either team

    def test_apply_bet_type_filter(self, sample_dataframe):
        """Test bet type filter"""
        filters = {'bet_types': ['Spread']}
        result = apply_filters(sample_dataframe, filters)

        assert len(result) == 1
        assert all(result['bet_type'] == 'Spread')

    def test_apply_bet_type_filter_multiple(self, sample_dataframe):
        """Test multiple bet type filter"""
        filters = {'bet_types': ['Spread', 'Total']}
        result = apply_filters(sample_dataframe, filters)

        assert len(result) == 2
        assert all(bt in ['Spread', 'Total'] for bt in result['bet_type'])

    def test_apply_confidence_filter(self, sample_dataframe):
        """Test confidence minimum filter"""
        filters = {'confidence_min': 75}
        result = apply_filters(sample_dataframe, filters)

        assert len(result) == 2  # Only markets with confidence >= 75
        assert all(result['confidence'] >= 75)

    def test_apply_edge_filter(self, sample_dataframe):
        """Test edge percentage filter"""
        filters = {'edge_min': 5.0}
        result = apply_filters(sample_dataframe, filters)

        assert len(result) == 2  # Markets with edge >= 5.0%
        assert all(result['edge_pct'] >= 5.0)

    def test_apply_time_filter_today(self, sample_dataframe):
        """Test time filter for today"""
        filters = {'time_filter': 'Today'}
        result = apply_filters(sample_dataframe, filters)

        assert all(result['days_to_close'] == 0)

    def test_apply_time_filter_tomorrow(self, sample_dataframe):
        """Test time filter for tomorrow"""
        filters = {'time_filter': 'Tomorrow'}
        result = apply_filters(sample_dataframe, filters)

        assert all(result['days_to_close'] == 1)

    def test_apply_time_filter_this_week(self, sample_dataframe):
        """Test time filter for this week"""
        filters = {'time_filter': 'This Week'}
        result = apply_filters(sample_dataframe, filters)

        assert all(result['days_to_close'] <= 7)

    def test_apply_time_filter_this_month(self, sample_dataframe):
        """Test time filter for this month"""
        filters = {'time_filter': 'This Month'}
        result = apply_filters(sample_dataframe, filters)

        assert all(result['days_to_close'] <= 30)

    def test_apply_risk_level_filter(self, sample_dataframe):
        """Test risk level filter"""
        filters = {'risk_levels': ['Low']}
        result = apply_filters(sample_dataframe, filters)

        assert all(result['risk_level'] == 'Low')

    def test_apply_risk_level_filter_multiple(self, sample_dataframe):
        """Test multiple risk level filter"""
        filters = {'risk_levels': ['Low', 'Medium']}
        result = apply_filters(sample_dataframe, filters)

        assert len(result) == 4  # All markets are Low or Medium in sample data

    def test_apply_multiple_filters(self, sample_dataframe):
        """Test applying multiple filters simultaneously"""
        filters = {
            'confidence_min': 70,
            'edge_min': 3.0,
            'teams': ['Chiefs'],
            'risk_levels': ['Low', 'Medium']
        }
        result = apply_filters(sample_dataframe, filters)

        assert all(result['confidence'] >= 70)
        assert all(result['edge_pct'] >= 3.0)
        assert all('Chiefs' in [home, away]
                   for home, away in zip(result['home_team'], result['away_team']))

    def test_apply_no_filters(self, sample_dataframe):
        """Test with no filters applied"""
        filters = {}
        result = apply_filters(sample_dataframe, filters)

        assert len(result) == len(sample_dataframe)  # All data returned


# ============================================================================
# TEST: Watchlist
# ============================================================================

class TestWatchlist:
    """Test watchlist functionality"""

    def test_initialize_watchlist(self):
        """Test watchlist initialization"""
        import streamlit as st

        # Clear session state
        if 'watchlist' in st.session_state:
            del st.session_state.watchlist

        initialize_watchlist()

        assert 'watchlist' in st.session_state
        assert isinstance(st.session_state.watchlist, list)
        assert len(st.session_state.watchlist) == 0

    @patch('streamlit.session_state', {'watchlist': []})
    def test_add_to_watchlist_new(self):
        """Test adding new item to watchlist"""
        import streamlit as st

        add_to_watchlist('NFL-TEST-001')

        assert 'NFL-TEST-001' in st.session_state.watchlist
        assert len(st.session_state.watchlist) == 1

    @patch('streamlit.session_state', {'watchlist': ['NFL-TEST-001']})
    def test_add_to_watchlist_duplicate(self):
        """Test adding duplicate item to watchlist"""
        import streamlit as st

        add_to_watchlist('NFL-TEST-001')

        # Should not add duplicate
        assert st.session_state.watchlist.count('NFL-TEST-001') == 1

    @patch('streamlit.session_state', {'watchlist': ['NFL-TEST-001', 'NFL-TEST-002']})
    def test_remove_from_watchlist(self):
        """Test removing item from watchlist"""
        import streamlit as st

        remove_from_watchlist('NFL-TEST-001')

        assert 'NFL-TEST-001' not in st.session_state.watchlist
        assert 'NFL-TEST-002' in st.session_state.watchlist
        assert len(st.session_state.watchlist) == 1


# ============================================================================
# TEST: Edge Cases
# ============================================================================

class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_empty_dataframe(self):
        """Test handling of empty DataFrame"""
        empty_df = pd.DataFrame()
        filters = {'confidence_min': 75}

        result = apply_filters(empty_df, filters)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0

    def test_none_values_in_data(self):
        """Test handling of None values"""
        data = {
            'ticker': ['NFL-001'],
            'title': [None],
            'confidence': [None],
            'edge_pct': [None],
            'home_team': [None],
            'away_team': [None]
        }
        df = pd.DataFrame(data)

        # Should not crash
        filters = {'search': 'test'}
        result = apply_filters(df, filters)

        assert isinstance(result, pd.DataFrame)

    def test_invalid_date_formats(self):
        """Test handling of invalid date formats"""
        result = MarketDataManager._calculate_days_to_close("invalid-date")
        assert result == 0  # Should return 0 for invalid dates

    def test_extreme_confidence_values(self):
        """Test risk level calculation with extreme values"""
        assert MarketDataManager._get_risk_level(100) == "Low"
        assert MarketDataManager._get_risk_level(0) == "High"
        assert MarketDataManager._get_risk_level(-10) == "High"  # Invalid but handled


# ============================================================================
# TEST: Integration
# ============================================================================

class TestIntegration:
    """Integration tests for complete workflows"""

    def test_full_filter_workflow(self, sample_dataframe):
        """Test complete filtering workflow"""
        # Step 1: Apply search
        filters = {'search': 'chiefs'}
        result = apply_filters(sample_dataframe, filters)
        assert len(result) > 0

        # Step 2: Add confidence filter
        filters['confidence_min'] = 80
        result = apply_filters(sample_dataframe, filters)

        # Step 3: Verify results meet all criteria
        assert all('chiefs' in title.lower() or 'Chiefs' in str(home) or 'Chiefs' in str(away)
                   for title, home, away in zip(result['title'], result['home_team'], result['away_team']))
        assert all(result['confidence'] >= 80)

    def test_watchlist_workflow(self):
        """Test complete watchlist workflow"""
        import streamlit as st

        # Initialize
        if 'watchlist' in st.session_state:
            del st.session_state.watchlist
        initialize_watchlist()

        # Add items
        add_to_watchlist('NFL-001')
        add_to_watchlist('NFL-002')
        add_to_watchlist('NFL-003')

        assert len(st.session_state.watchlist) == 3

        # Remove item
        remove_from_watchlist('NFL-002')

        assert len(st.session_state.watchlist) == 2
        assert 'NFL-002' not in st.session_state.watchlist


# ============================================================================
# TEST EXECUTION
# ============================================================================

if __name__ == "__main__":
    """Run tests directly"""
    print("Running Kalshi NFL Markets Dashboard Tests...")
    print("=" * 80)

    # Run pytest
    pytest.main([__file__, "-v", "--tb=short"])
