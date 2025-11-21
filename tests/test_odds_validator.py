"""
Comprehensive Unit Tests for Odds Validation System

Tests all validation rules, edge cases, and error handling
to ensure bulletproof odds validation
"""

import pytest
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.odds_validator import (
    OddsValidator,
    ValidationResult,
    ValidationSeverity,
    ValidationRuleType,
    validate_kalshi_market
)


# Test fixtures
@pytest.fixture
def db_config():
    """Database configuration for testing"""
    return {
        'host': 'localhost',
        'port': '5432',
        'database': 'magnus',
        'user': 'postgres',
        'password': os.getenv('DB_PASSWORD', 'test_password')
    }


@pytest.fixture
def validator(db_config):
    """Create validator instance"""
    return OddsValidator(db_config)


class TestOddsRangeValidation:
    """Test odds range validation"""

    def test_valid_odds_range(self, validator):
        """Test that valid odds pass range validation"""
        result = validator._validate_odds_range(
            ticker="TEST-1",
            away_team="Team A",
            home_team="Team B",
            away_price=0.45,
            home_price=0.55
        )

        assert result.passed is True
        assert result.severity == ValidationSeverity.CRITICAL
        assert result.rule_type == ValidationRuleType.ODDS_RANGE

    def test_odds_too_low(self, validator):
        """Test that odds below minimum fail validation"""
        result = validator._validate_odds_range(
            ticker="TEST-2",
            away_team="Team A",
            home_team="Team B",
            away_price=0.005,  # Below minimum (0.01)
            home_price=0.55
        )

        assert result.passed is False
        assert result.severity == ValidationSeverity.CRITICAL

    def test_odds_too_high(self, validator):
        """Test that odds above maximum fail validation"""
        result = validator._validate_odds_range(
            ticker="TEST-3",
            away_team="Team A",
            home_team="Team B",
            away_price=0.45,
            home_price=0.995  # Above maximum (0.99)
        )

        assert result.passed is False
        assert result.severity == ValidationSeverity.CRITICAL

    def test_both_odds_invalid(self, validator):
        """Test that both invalid odds are detected"""
        result = validator._validate_odds_range(
            ticker="TEST-4",
            away_team="Team A",
            home_team="Team B",
            away_price=1.5,  # Way too high
            home_price=-0.1  # Negative
        )

        assert result.passed is False
        assert len(result.details.get('invalid_prices', [])) == 2


class TestProbabilitySumValidation:
    """Test probability sum validation"""

    def test_valid_probability_sum(self, validator):
        """Test that valid sum passes (accounting for market spread)"""
        result = validator._validate_probability_sum(
            ticker="TEST-5",
            away_price=0.48,
            home_price=0.52
        )

        assert result.passed is True
        assert 0.95 <= result.details['sum'] <= 1.05

    def test_probability_sum_too_low(self, validator):
        """Test that sum below minimum fails"""
        result = validator._validate_probability_sum(
            ticker="TEST-6",
            away_price=0.40,
            home_price=0.40
        )

        assert result.passed is False
        assert result.severity == ValidationSeverity.CRITICAL
        assert result.details['sum'] < 0.95

    def test_probability_sum_too_high(self, validator):
        """Test that sum above maximum triggers warning"""
        result = validator._validate_probability_sum(
            ticker="TEST-7",
            away_price=0.60,
            home_price=0.60
        )

        assert result.passed is False
        assert result.severity == ValidationSeverity.WARNING
        assert result.details['sum'] > 1.05

    def test_exact_sum_of_one(self, validator):
        """Test that exact sum of 1.0 passes"""
        result = validator._validate_probability_sum(
            ticker="TEST-8",
            away_price=0.45,
            home_price=0.55
        )

        assert result.passed is True
        assert result.details['sum'] == 1.0


class TestRecordCorrelationValidation:
    """Test team record correlation validation"""

    def test_better_team_has_higher_odds(self, validator):
        """Test that better record correlates with higher odds"""
        result = validator._validate_record_correlation(
            ticker="TEST-9",
            away_team="Dallas Cowboys",
            home_team="New York Jets",
            away_price=0.65,  # Better team (9-1)
            home_price=0.35,
            away_record="9-1",
            home_record="3-7"
        )

        assert result.passed is True
        assert result.details.get('reversed') is False

    def test_reversed_odds_critical_failure(self, validator):
        """Test that reversed odds trigger CRITICAL failure"""
        result = validator._validate_record_correlation(
            ticker="TEST-10",
            away_team="Buffalo Bills",
            home_team="New York Jets",
            away_price=0.35,  # REVERSED: Better team has LOWER odds
            home_price=0.65,
            away_record="9-1",
            home_record="3-7"
        )

        assert result.passed is False
        assert result.severity == ValidationSeverity.CRITICAL
        assert result.details.get('reversed') is True
        assert "REVERSED" in result.message.upper()

    def test_similar_records_any_odds_acceptable(self, validator):
        """Test that similar records allow any reasonable odds"""
        result = validator._validate_record_correlation(
            ticker="TEST-11",
            away_team="Team A",
            home_team="Team B",
            away_price=0.48,
            home_price=0.52,
            away_record="6-4",
            home_record="5-5"
        )

        assert result.passed is True
        assert result.details['win_pct_diff'] < 0.10

    def test_invalid_record_format_handled(self, validator):
        """Test that invalid record formats are handled gracefully"""
        result = validator._validate_record_correlation(
            ticker="TEST-12",
            away_team="Team A",
            home_team="Team B",
            away_price=0.50,
            home_price=0.50,
            away_record="invalid",
            home_record="also-invalid"
        )

        # Should pass with INFO severity (cannot validate)
        assert result.passed is True
        assert result.severity == ValidationSeverity.INFO


class TestHomeAdvantageValidation:
    """Test home field advantage validation"""

    def test_home_advantage_for_evenly_matched_teams(self, validator):
        """Test that home team gets advantage for even matchups"""
        result = validator._validate_home_advantage(
            ticker="TEST-13",
            away_team="Team A",
            home_team="Team B",
            away_price=0.47,
            home_price=0.53,  # Home team has slight edge
            away_record="6-4",
            home_record="6-4"
        )

        assert result.passed is True
        assert 0.02 <= result.details.get('home_advantage', 0) <= 0.15

    def test_missing_home_advantage_warning(self, validator):
        """Test that missing home advantage triggers warning"""
        result = validator._validate_home_advantage(
            ticker="TEST-14",
            away_team="Team A",
            home_team="Team B",
            away_price=0.51,  # AWAY team has advantage (wrong!)
            home_price=0.49,
            away_record="6-4",
            home_record="6-4"
        )

        assert result.passed is False
        assert result.severity == ValidationSeverity.WARNING
        assert result.details.get('missing_home_advantage') is True

    def test_excessive_home_advantage_warning(self, validator):
        """Test that excessive home advantage is flagged"""
        result = validator._validate_home_advantage(
            ticker="TEST-15",
            away_team="Team A",
            home_team="Team B",
            away_price=0.30,
            home_price=0.70,  # 40% advantage (too high for even teams)
            away_record="6-4",
            home_record="6-4"
        )

        assert result.passed is False
        assert result.severity == ValidationSeverity.WARNING


class TestDataFreshnessValidation:
    """Test data freshness validation"""

    def test_fresh_data_passes(self, validator):
        """Test that recently updated data passes"""
        last_updated = datetime.now() - timedelta(hours=1)

        result = validator._validate_data_freshness(
            ticker="TEST-16",
            last_updated=last_updated
        )

        assert result.passed is True
        assert result.details['age_hours'] < 24

    def test_stale_data_warning(self, validator):
        """Test that stale data triggers warning"""
        last_updated = datetime.now() - timedelta(hours=48)

        result = validator._validate_data_freshness(
            ticker="TEST-17",
            last_updated=last_updated
        )

        assert result.passed is False
        assert result.severity == ValidationSeverity.WARNING
        assert result.details['age_hours'] > 24


class TestUpsetDetection:
    """Test upset detection (informational)"""

    def test_no_upset_detected(self, validator):
        """Test normal matchup (no upset)"""
        result = validator._detect_upset(
            ticker="TEST-18",
            away_team="Strong Team",
            home_team="Weak Team",
            away_price=0.65,  # Favorite
            home_price=0.35,
            away_record="9-1",
            home_record="3-7"
        )

        assert result.passed is True
        assert result.details.get('is_upset_alert') is False

    def test_upset_detected(self, validator):
        """Test potential upset (underdog has better record)"""
        result = validator._detect_upset(
            ticker="TEST-19",
            away_team="Strong Team",
            home_team="Weak Team",
            away_price=0.35,  # Underdog in odds
            home_price=0.65,  # Favorite in odds
            away_record="9-1",  # But actually has better record!
            home_record="3-7"
        )

        assert result.passed is True  # INFO only, not a failure
        assert result.severity == ValidationSeverity.INFO
        assert result.details.get('is_upset_alert') is True
        assert "UPSET" in result.message.upper()


class TestRecordParsing:
    """Test team record parsing utility"""

    def test_parse_standard_record(self, validator):
        """Test parsing standard W-L record"""
        wins, losses = validator._parse_record("7-3")
        assert wins == 7
        assert losses == 3

    def test_parse_record_with_ties(self, validator):
        """Test parsing W-L-T record"""
        wins, losses = validator._parse_record("7-3-1")
        assert wins == 7
        assert losses == 3  # Ties ignored

    def test_parse_invalid_record(self, validator):
        """Test parsing invalid record"""
        wins, losses = validator._parse_record("invalid")
        assert wins is None
        assert losses is None

    def test_parse_empty_record(self, validator):
        """Test parsing empty record"""
        wins, losses = validator._parse_record("")
        assert wins is None
        assert losses is None


class TestFullGameValidation:
    """Test full game validation with all rules"""

    def test_valid_game_all_rules_pass(self, validator):
        """Test that valid game passes all validation rules"""
        is_valid, results = validator.validate_game_odds(
            ticker="TEST-FULL-1",
            away_team="Dallas Cowboys",
            home_team="Philadelphia Eagles",
            away_win_price=0.45,
            home_win_price=0.55,
            away_record="7-3",
            home_record="9-1",
            last_updated=datetime.now()
        )

        assert is_valid is True
        # Should have results for all applicable rules
        assert len(results) >= 5

    def test_critical_failure_invalidates_game(self, validator):
        """Test that critical failure invalidates entire game"""
        is_valid, results = validator.validate_game_odds(
            ticker="TEST-FULL-2",
            away_team="Buffalo Bills",
            home_team="New York Jets",
            away_win_price=0.35,  # REVERSED
            home_win_price=0.65,
            away_record="9-1",
            home_record="3-7",
            last_updated=datetime.now()
        )

        assert is_valid is False
        # Should have at least one CRITICAL failure
        critical_failures = [r for r in results if not r.passed and r.severity == ValidationSeverity.CRITICAL]
        assert len(critical_failures) >= 1

    def test_warnings_dont_invalidate_game(self, validator):
        """Test that warnings alone don't invalidate game"""
        is_valid, results = validator.validate_game_odds(
            ticker="TEST-FULL-3",
            away_team="Team A",
            home_team="Team B",
            away_win_price=0.50,
            home_win_price=0.50,
            away_record="6-4",
            home_record="6-4",
            last_updated=datetime.now() - timedelta(hours=48)  # Stale data warning
        )

        # Should still be valid despite warnings
        assert is_valid is True


class TestValidationResultStorage:
    """Test validation result storage"""

    @patch('src.odds_validator.psycopg2.connect')
    def test_store_validation_results(self, mock_connect, validator):
        """Test storing validation results in database"""
        # Mock database connection
        mock_conn = MagicMock()
        mock_cur = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cur

        # Create sample results
        results = [
            ValidationResult(
                rule_type=ValidationRuleType.ODDS_RANGE,
                severity=ValidationSeverity.INFO,
                passed=True,
                message="Test message",
                details={'test': 'data'},
                timestamp=datetime.now()
            )
        ]

        # Store results
        validator.store_validation_results("TEST-TICKER", results)

        # Verify database calls
        assert mock_cur.execute.called
        assert mock_conn.commit.called


class TestConvenienceFunction:
    """Test convenience function"""

    def test_validate_kalshi_market_function(self, db_config):
        """Test quick validation function"""
        is_valid, results = validate_kalshi_market(
            ticker="TEST-CONV-1",
            away_team="Team A",
            home_team="Team B",
            away_win_price=0.48,
            home_win_price=0.52,
            db_config=db_config,
            away_record="6-4",
            home_record="6-4"
        )

        assert isinstance(is_valid, bool)
        assert isinstance(results, list)
        assert all(isinstance(r, ValidationResult) for r in results)


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_zero_odds(self, validator):
        """Test handling of zero odds"""
        result = validator._validate_odds_range(
            ticker="EDGE-1",
            away_team="Team A",
            home_team="Team B",
            away_price=0.0,
            home_price=1.0
        )

        assert result.passed is False

    def test_exactly_one_odds(self, validator):
        """Test handling of 100% odds"""
        result = validator._validate_odds_range(
            ticker="EDGE-2",
            away_team="Team A",
            home_team="Team B",
            away_price=1.0,
            home_price=0.0
        )

        assert result.passed is False

    def test_negative_odds(self, validator):
        """Test handling of negative odds"""
        result = validator._validate_odds_range(
            ticker="EDGE-3",
            away_team="Team A",
            home_team="Team B",
            away_price=-0.1,
            home_price=1.1
        )

        assert result.passed is False

    def test_none_values(self, validator):
        """Test handling of None values gracefully"""
        # Should not crash, should handle gracefully
        try:
            result = validator._validate_record_correlation(
                ticker="EDGE-4",
                away_team="Team A",
                home_team="Team B",
                away_price=0.50,
                home_price=0.50,
                away_record=None,
                home_record=None
            )
            # Should pass with INFO (cannot validate)
            assert result.passed is True
        except Exception as e:
            pytest.fail(f"Should handle None gracefully, but raised: {e}")


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
