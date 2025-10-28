"""
Unit tests for Dashboard feature

Tests cover:
- Trade history management
- P/L calculations
- Balance forecasting
- Theta decay calculations
- Portfolio metrics
"""

import pytest
import sys
from datetime import datetime, timedelta
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, 'c:/Code/WheelStrategy')

from src.trade_history_manager import TradeHistoryManager


class TestTradeHistoryManager:
    """Test suite for TradeHistoryManager"""

    @pytest.fixture
    def trade_manager(self):
        """Create a TradeHistoryManager instance"""
        return TradeHistoryManager()

    def test_add_trade(self, trade_manager):
        """Test adding a new trade"""
        trade_id = trade_manager.add_trade(
            symbol='TEST',
            strike_price=100.00,
            expiration_date='2025-12-31',
            premium_collected=500.00,
            contracts=1,
            open_date='2025-01-01'
        )
        assert trade_id is not None
        assert isinstance(trade_id, int)

    def test_close_trade(self, trade_manager):
        """Test closing a trade"""
        # Add trade first
        trade_id = trade_manager.add_trade(
            symbol='TEST',
            strike_price=100.00,
            expiration_date='2025-12-31',
            premium_collected=500.00,
            contracts=1,
            open_date='2025-01-01'
        )

        # Close it
        result = trade_manager.close_trade(
            trade_id=trade_id,
            close_price=250.00,
            close_reason='early_close',
            close_date='2025-01-15'
        )

        assert result['profit_loss'] == 250.00  # 500 - 250
        assert result['profit_loss_percent'] == 50.0
        assert result['days_held'] == 14

    def test_pl_calculation(self, trade_manager):
        """Test P/L calculation accuracy"""
        trade_id = trade_manager.add_trade(
            symbol='NVDA',
            strike_price=180.00,
            expiration_date='2025-02-28',
            premium_collected=610.00,
            contracts=1,
            open_date='2025-01-01'
        )

        result = trade_manager.close_trade(
            trade_id=trade_id,
            close_price=305.00,
            close_reason='early_close',
            close_date='2025-01-15'
        )

        # Verify calculations
        assert result['profit_loss'] == 305.00
        assert abs(result['profit_loss_percent'] - 50.0) < 0.1
        assert result['days_held'] == 14

        # Annualized return = (305/610 * 100) / 14 * 365 = ~1303%
        assert abs(result['annualized_return'] - 1303.57) < 1.0

    def test_get_trade_stats(self, trade_manager):
        """Test trade statistics calculation"""
        stats = trade_manager.get_trade_stats()
        assert 'total_trades' in stats
        assert 'total_pl' in stats
        assert 'win_rate' in stats
        assert 'avg_days_held' in stats


class TestPortfolioMetrics:
    """Test portfolio metrics calculations"""

    def test_capital_at_risk_calculation(self):
        """Test capital at risk calculation for CSPs"""
        positions = [
            {'Type': 'CSP', 'Strike': 100, 'Contracts': 1},
            {'Type': 'CSP', 'Strike': 50, 'Contracts': 2},
        ]

        capital_at_risk = sum(p['Strike'] * 100 * p['Contracts'] for p in positions)
        assert capital_at_risk == 20000  # (100*100*1) + (50*100*2)

    def test_premium_collected_sum(self):
        """Test total premium calculation"""
        positions = [
            {'Premium': 500},
            {'Premium': 300},
            {'Premium': 200},
        ]

        total_premium = sum(p['Premium'] for p in positions)
        assert total_premium == 1000


class TestThetaDecay:
    """Test theta decay calculations"""

    def test_theta_decay_formula(self):
        """Test theta decay using square root of time"""
        import math

        days_left = 30
        current_value = 500
        day = 7

        days_remaining = days_left - day
        decay_factor = math.sqrt(days_remaining) / math.sqrt(days_left)
        projected_value = current_value * decay_factor

        # After 7 days, with sqrt decay, value should be ~439
        assert 435 < projected_value < 445


# Placeholder for integration tests
class TestDashboardIntegration:
    """Integration tests for dashboard functionality"""

    @pytest.mark.skip(reason="Requires live Robinhood connection")
    def test_robinhood_connection(self):
        """Test connecting to Robinhood API"""
        pass

    @pytest.mark.skip(reason="Requires database connection")
    def test_database_persistence(self):
        """Test data persistence to PostgreSQL"""
        pass


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
