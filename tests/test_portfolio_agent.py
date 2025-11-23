"""
Unit tests for PortfolioAgent
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime
from src.ava.agents.trading.portfolio_agent import (
    PortfolioAgent,
    PortfolioMetrics,
    RiskAssessment,
    SectorAllocation
)


class TestPortfolioAgent:
    """Test suite for PortfolioAgent"""

    @pytest.fixture
    def mock_robinhood_client(self):
        """Mock Robinhood client"""
        client = Mock()
        client.logged_in = True
        client.get_account_info.return_value = {
            'portfolio_value': 10000.0,
            'cash': 2000.0,
            'buying_power': 4000.0,
            'day_trade_count': 0
        }
        client.get_positions.return_value = [
            {
                'type': 'stock',
                'symbol': 'AAPL',
                'quantity': 10,
                'avg_cost': 150.0,
                'current_price': 160.0,
                'market_value': 1600.0,
                'total_return': 100.0,
                'total_return_pct': 6.67
            },
            {
                'type': 'option',
                'symbol': 'TSLA',
                'option_type': 'put',
                'position_type': 'short',
                'quantity': 1,
                'strike_price': 200.0,
                'current_price': 2.5,
                'market_value': 250.0,
                'total_return': 50.0,
                'total_return_pct': 25.0
            }
        ]
        return client

    @pytest.fixture
    def mock_llm(self):
        """Mock Local LLM"""
        llm = Mock()
        llm.query.return_value = "AI recommendation: Portfolio looks healthy."
        return llm

    @pytest.fixture
    def agent(self, mock_robinhood_client, mock_llm):
        """Create PortfolioAgent with mocked dependencies"""
        agent = PortfolioAgent()
        agent.robinhood_client = mock_robinhood_client
        agent.llm = mock_llm
        return agent

    @pytest.mark.asyncio
    async def test_get_portfolio_metrics(self, agent):
        """Test portfolio metrics calculation"""
        metrics = await agent.get_portfolio_metrics()

        assert isinstance(metrics, PortfolioMetrics)
        assert metrics.total_value == 10000.0
        assert metrics.cash == 2000.0
        assert metrics.num_positions == 2
        assert metrics.num_stock_positions == 1
        assert metrics.num_options_positions == 1

    @pytest.mark.asyncio
    async def test_greeks_calculation(self, agent):
        """Test Greeks exposure calculation"""
        options_positions = [
            {
                'quantity': 1,
                'position_type': 'short',
                'option_type': 'put',
                'strike_price': 200.0,
                'current_price': 210.0
            }
        ]

        greeks = await agent._calculate_greeks_exposure(options_positions)

        assert 'net_delta' in greeks
        assert 'net_gamma' in greeks
        assert 'net_theta' in greeks
        assert 'net_vega' in greeks

    @pytest.mark.asyncio
    async def test_concentration_risk(self, agent):
        """Test concentration risk calculation"""
        positions = [
            {'market_value': 5000.0},
            {'market_value': 3000.0},
            {'market_value': 2000.0}
        ]

        concentration = await agent._calculate_concentration_risk(positions)

        assert concentration == 50.0  # 5000/10000 * 100

    @pytest.mark.asyncio
    async def test_assess_portfolio_risk(self, agent):
        """Test risk assessment"""
        risk = await agent.assess_portfolio_risk()

        assert isinstance(risk, RiskAssessment)
        assert risk.overall_risk_level in ['low', 'medium', 'high', 'critical']
        assert 0 <= risk.risk_score <= 100
        assert isinstance(risk.recommendations, list)

    @pytest.mark.asyncio
    async def test_sector_allocation(self, agent):
        """Test sector allocation calculation"""
        allocations = await agent.get_sector_allocation()

        assert isinstance(allocations, list)
        assert len(allocations) > 0
        assert all(isinstance(a, SectorAllocation) for a in allocations)

    @pytest.mark.asyncio
    async def test_ai_recommendations(self, agent, mock_llm):
        """Test AI recommendations generation"""
        recommendations = await agent.generate_ai_recommendations()

        assert isinstance(recommendations, str)
        assert len(recommendations) > 0
        mock_llm.query.assert_called_once()

    @pytest.mark.asyncio
    async def test_hedging_strategies(self, agent, mock_llm):
        """Test hedging strategy suggestions"""
        hedging = await agent.suggest_hedging_strategies()

        assert isinstance(hedging, str)
        mock_llm.query.assert_called()

    @pytest.mark.asyncio
    async def test_execute_portfolio_summary(self, agent):
        """Test execute with portfolio summary request"""
        state = {
            'input': 'Give me a portfolio summary',
            'context': {},
            'tools': [],
            'result': None,
            'error': None,
            'metadata': {}
        }

        result_state = await agent.execute(state)

        assert result_state['error'] is None
        assert 'metrics' in result_state['result']

    @pytest.mark.asyncio
    async def test_execute_risk_assessment(self, agent):
        """Test execute with risk assessment request"""
        state = {
            'input': 'Assess my portfolio risk',
            'context': {},
            'tools': [],
            'result': None,
            'error': None,
            'metadata': {}
        }

        result_state = await agent.execute(state)

        assert result_state['error'] is None
        assert 'risk_assessment' in result_state['result']

    @pytest.mark.asyncio
    async def test_execute_greeks_analysis(self, agent):
        """Test execute with Greeks analysis request"""
        state = {
            'input': 'What is my Greeks exposure?',
            'context': {},
            'tools': [],
            'result': None,
            'error': None,
            'metadata': {}
        }

        result_state = await agent.execute(state)

        assert result_state['error'] is None
        assert 'greeks' in result_state['result']

    @pytest.mark.asyncio
    async def test_execute_comprehensive(self, agent):
        """Test execute with no specific request (comprehensive)"""
        state = {
            'input': 'Tell me about my portfolio',
            'context': {},
            'tools': [],
            'result': None,
            'error': None,
            'metadata': {}
        }

        result_state = await agent.execute(state)

        assert result_state['error'] is None
        result = result_state['result']
        assert 'metrics' in result
        assert 'risk_assessment' in result
        assert 'ai_recommendations' in result

    @pytest.mark.asyncio
    async def test_caching(self, agent):
        """Test result caching"""
        # First call - should cache
        metrics1 = await agent.get_portfolio_metrics()

        # Second call - should use cache
        metrics2 = await agent.get_portfolio_metrics()

        # Should be same object from cache
        assert metrics1 == metrics2

        # Verify Robinhood client called only once
        agent.robinhood_client.get_account_info.call_count == 1

    @pytest.mark.asyncio
    async def test_error_handling(self, agent):
        """Test error handling"""
        # Mock error
        agent.robinhood_client.get_account_info.side_effect = Exception("Connection error")

        state = {
            'input': 'portfolio summary',
            'context': {},
            'tools': [],
            'result': None,
            'error': None,
            'metadata': {}
        }

        result_state = await agent.execute(state)

        assert result_state['error'] is not None
        assert 'error' in result_state['result']


class TestDataModels:
    """Test data models"""

    def test_portfolio_metrics_creation(self):
        """Test PortfolioMetrics creation"""
        metrics = PortfolioMetrics(
            total_value=10000.0,
            cash=2000.0,
            buying_power=4000.0,
            total_positions_value=8000.0,
            total_pnl=500.0,
            total_pnl_pct=6.67,
            num_positions=5,
            num_stock_positions=3,
            num_options_positions=2,
            net_delta=50.0,
            net_gamma=0.1,
            net_theta=-10.0,
            net_vega=20.0,
            concentration_risk=30.0,
            sector_diversity=4.0,
            options_exposure_pct=25.0,
            timestamp=datetime.now().isoformat()
        )

        assert metrics.total_value == 10000.0
        assert metrics.num_positions == 5

    def test_risk_assessment_creation(self):
        """Test RiskAssessment creation"""
        risk = RiskAssessment(
            overall_risk_level='medium',
            risk_score=35,
            concentration_issues=['Issue 1'],
            correlation_warnings=['Warning 1'],
            greeks_warnings=['Greeks warning'],
            liquidity_concerns=['Liquidity concern'],
            recommendations=['Recommendation 1', 'Recommendation 2']
        )

        assert risk.overall_risk_level == 'medium'
        assert risk.risk_score == 35
        assert len(risk.recommendations) == 2

    def test_sector_allocation_creation(self):
        """Test SectorAllocation creation"""
        allocation = SectorAllocation(
            sector='Technology',
            value=5000.0,
            percentage=50.0,
            num_positions=3,
            symbols=['AAPL', 'MSFT', 'GOOGL']
        )

        assert allocation.sector == 'Technology'
        assert allocation.value == 5000.0
        assert len(allocation.symbols) == 3


# Run tests
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
