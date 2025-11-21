"""
Quantitative Position Analyzer
Rule-based analysis engine for options positions
"""

import logging
from dataclasses import dataclass
from typing import Dict, Optional
import math

from src.ai.position_data_aggregator import EnrichedPosition

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class QuantitativeAnalysis:
    """Quantitative analysis results"""

    # Risk metrics
    max_loss: float
    max_profit: float
    risk_reward_ratio: float
    probability_profit: float
    expected_value: float

    # Greeks analysis
    theta_efficiency: float  # daily theta / capital at risk
    gamma_risk_level: str  # 'low', 'medium', 'high'
    vega_exposure: float  # sensitivity to IV changes

    # Position health
    breakeven_price: float
    breakeven_distance_pct: float
    days_to_profitable_decay: int

    # Recommendation
    recommended_action: str
    confidence: int
    reasoning: str
    risk_level: str

    # Targets
    optimal_exit_price: Optional[float]
    stop_loss_price: Optional[float]
    roll_threshold_dte: int


class PositionQuantitativeAnalyzer:
    """
    Rule-based quantitative analysis engine

    Provides deterministic recommendations based on:
    - Position P/L and Greeks
    - DTE thresholds
    - Moneyness
    - Risk metrics
    """

    # Configuration thresholds
    THRESHOLDS = {
        'profit_target_pct': 50,  # Take profit at 50% of max
        'loss_threshold_pct': -100,  # Cut loss at -100%
        'roll_dte': 7,  # Roll when DTE < 7
        'critical_dte': 3,  # Critical action needed
        'atm_threshold_pct': 2,  # +/- 2% for ATM
        'high_gamma_threshold': 0.10,
        'theta_efficiency_target': 0.001,  # 0.1% per day
    }

    def analyze(self, position: EnrichedPosition) -> QuantitativeAnalysis:
        """
        Perform quantitative analysis on a position

        Args:
            position: Enriched position data

        Returns:
            QuantitativeAnalysis object
        """
        try:
            # Calculate risk metrics
            risk_metrics = self._calculate_risk_metrics(position)

            # Analyze Greeks
            greeks_analysis = self._analyze_greeks(position)

            # Calculate position health
            position_health = self._calculate_position_health(position)

            # Generate recommendation
            recommendation = self._generate_recommendation(
                position, risk_metrics, greeks_analysis, position_health
            )

            return QuantitativeAnalysis(
                # Risk metrics
                max_loss=risk_metrics['max_loss'],
                max_profit=risk_metrics['max_profit'],
                risk_reward_ratio=risk_metrics['risk_reward_ratio'],
                probability_profit=risk_metrics['probability_profit'],
                expected_value=risk_metrics['expected_value'],
                # Greeks
                theta_efficiency=greeks_analysis['theta_efficiency'],
                gamma_risk_level=greeks_analysis['gamma_risk_level'],
                vega_exposure=greeks_analysis['vega_exposure'],
                # Position health
                breakeven_price=position_health['breakeven_price'],
                breakeven_distance_pct=position_health['breakeven_distance_pct'],
                days_to_profitable_decay=position_health['days_to_profitable_decay'],
                # Recommendation
                recommended_action=recommendation['action'],
                confidence=recommendation['confidence'],
                reasoning=recommendation['reasoning'],
                risk_level=recommendation['risk_level'],
                # Targets
                optimal_exit_price=recommendation.get('optimal_exit_price'),
                stop_loss_price=recommendation.get('stop_loss_price'),
                roll_threshold_dte=self.THRESHOLDS['roll_dte']
            )

        except Exception as e:
            logger.error(f"Error in quantitative analysis: {e}")
            # Return conservative default
            return self._get_default_analysis(position)

    def _calculate_risk_metrics(self, position: EnrichedPosition) -> Dict:
        """Calculate position risk metrics"""

        # Position type determines max profit/loss
        if position.position_type in ['CSP', 'CC']:  # Short options
            # Max profit = premium collected
            max_profit = position.premium_collected

            # Max loss = strike * 100 - premium (for puts) or unlimited (for calls)
            if position.position_type == 'CSP':
                max_loss = (position.strike * 100 * abs(position.quantity)) - position.premium_collected
            else:  # CC
                # Max loss is capped by stock ownership, but simplified here
                max_loss = position.premium_collected * 5  # Rough estimate

        else:  # Long options
            # Max loss = premium paid
            max_loss = position.premium_collected  # Should be negative for long

            # Max profit = unlimited (calls) or strike - premium (puts)
            if 'Call' in position.position_type:
                max_profit = position.premium_collected * 3  # Conservative estimate
            else:  # Long Put
                max_profit = (position.strike * 100 * abs(position.quantity)) - abs(position.premium_collected)

        # Risk/reward ratio
        risk_reward_ratio = max_profit / abs(max_loss) if max_loss != 0 else 0

        # Probability of profit (simplified - use delta as proxy)
        if position.position_type in ['CSP', 'CC']:
            probability_profit = 100 - position.probability_itm
        else:
            probability_profit = position.probability_itm

        # Expected value
        expected_value = (max_profit * probability_profit / 100) - (abs(max_loss) * (100 - probability_profit) / 100)

        return {
            'max_loss': max_loss,
            'max_profit': max_profit,
            'risk_reward_ratio': risk_reward_ratio,
            'probability_profit': probability_profit,
            'expected_value': expected_value
        }

    def _analyze_greeks(self, position: EnrichedPosition) -> Dict:
        """Analyze position Greeks"""

        # Theta efficiency: daily theta / capital at risk
        capital_at_risk = abs(position.strike * 100 * position.quantity)
        daily_theta_dollars = abs(position.theta * position.quantity * 100)
        theta_efficiency = daily_theta_dollars / capital_at_risk if capital_at_risk > 0 else 0

        # Gamma risk level
        abs_gamma = abs(position.gamma)
        if abs_gamma < 0.05:
            gamma_risk_level = 'low'
        elif abs_gamma < 0.10:
            gamma_risk_level = 'medium'
        else:
            gamma_risk_level = 'high'

        # Vega exposure (sensitivity to IV changes)
        vega_exposure = abs(position.vega * position.quantity * 100)

        return {
            'theta_efficiency': theta_efficiency,
            'gamma_risk_level': gamma_risk_level,
            'vega_exposure': vega_exposure
        }

    def _calculate_position_health(self, position: EnrichedPosition) -> Dict:
        """Calculate position health metrics"""

        # Breakeven price
        if position.position_type == 'CSP':
            breakeven_price = position.strike - (position.premium_collected / (100 * abs(position.quantity)))
        elif position.position_type == 'CC':
            breakeven_price = position.strike + (position.premium_collected / (100 * abs(position.quantity)))
        elif 'Call' in position.position_type:
            breakeven_price = position.strike + (abs(position.premium_collected) / (100 * abs(position.quantity)))
        else:  # Long Put
            breakeven_price = position.strike - (abs(position.premium_collected) / (100 * abs(position.quantity)))

        # Distance to breakeven
        breakeven_distance_pct = ((position.stock_price - breakeven_price) / breakeven_price * 100)

        # Days to profitable decay (for short positions)
        if position.position_type in ['CSP', 'CC']:
            daily_theta_dollars = abs(position.theta * position.quantity * 100)
            remaining_loss = abs(position.pnl_dollar) if position.pnl_dollar < 0 else 0
            days_to_profitable = int(remaining_loss / daily_theta_dollars) if daily_theta_dollars > 0 else position.dte
        else:
            days_to_profitable = position.dte  # For long positions, time works against us

        return {
            'breakeven_price': breakeven_price,
            'breakeven_distance_pct': breakeven_distance_pct,
            'days_to_profitable_decay': min(days_to_profitable, position.dte)
        }

    def _generate_recommendation(
        self,
        position: EnrichedPosition,
        risk_metrics: Dict,
        greeks_analysis: Dict,
        position_health: Dict
    ) -> Dict:
        """
        Generate rule-based recommendation

        Decision tree:
        1. Check P/L status
        2. Check DTE
        3. Check moneyness
        4. Check Greeks
        5. Determine action
        """

        action = 'hold'
        confidence = 70
        reasoning = ''
        risk_level = 'medium'
        optimal_exit_price = None
        stop_loss_price = None

        # Rule 1: Take profit if > 50% of max profit
        if position.pnl_percent > self.THRESHOLDS['profit_target_pct']:
            action = 'close_now'
            confidence = 85
            reasoning = f"Position is up {position.pnl_percent:.1f}%, exceeding profit target. Lock in gains."
            risk_level = 'low'
            optimal_exit_price = position.current_value

        # Rule 2: Cut loss if down > 100%
        elif position.pnl_percent < self.THRESHOLDS['loss_threshold_pct']:
            action = 'cut_loss'
            confidence = 80
            reasoning = f"Position is down {position.pnl_percent:.1f}%. Cut loss to prevent further damage."
            risk_level = 'high'
            stop_loss_price = position.current_value

        # Rule 3: Roll if DTE < 7 and position is ITM
        elif position.dte < self.THRESHOLDS['roll_dte'] and position.moneyness == 'ITM':
            action = 'roll_out'
            confidence = 90
            reasoning = f"Only {position.dte} DTE remaining and position is ITM. Roll to avoid assignment."
            risk_level = 'high'

        # Rule 4: Close if DTE < 3 and position is near max profit
        elif position.dte < self.THRESHOLDS['critical_dte'] and position.pnl_percent > 30:
            action = 'close_now'
            confidence = 85
            reasoning = f"Only {position.dte} DTE left with {position.pnl_percent:.1f}% profit. Close to avoid gamma risk."
            risk_level = 'medium'

        # Rule 5: Hold if position is profitable and OTM with time remaining
        elif position.pnl_percent > 0 and position.moneyness == 'OTM' and position.dte > 14:
            action = 'hold'
            confidence = 80
            reasoning = f"Position is profitable ({position.pnl_percent:+.1f}%) and OTM with {position.dte} DTE. Let theta work."
            risk_level = 'low'

        # Rule 6: Add hedge if ITM with high gamma risk
        elif position.moneyness == 'ITM' and greeks_analysis['gamma_risk_level'] == 'high':
            action = 'add_hedge'
            confidence = 75
            reasoning = f"Position is ITM with high gamma risk. Consider protective hedge."
            risk_level = 'high'

        # Rule 7: Roll strike if position is losing but thesis is still valid
        elif position.pnl_percent < -30 and position.dte > 21:
            action = 'roll_strike'
            confidence = 70
            reasoning = f"Position down {position.pnl_percent:.1f}% but has time. Consider rolling strike."
            risk_level = 'medium'

        # Default: Hold
        else:
            action = 'hold'
            confidence = 70
            reasoning = f"Position is within normal parameters. Monitor and let strategy play out."
            risk_level = 'medium'

        return {
            'action': action,
            'confidence': confidence,
            'reasoning': reasoning,
            'risk_level': risk_level,
            'optimal_exit_price': optimal_exit_price,
            'stop_loss_price': stop_loss_price
        }

    def _get_default_analysis(self, position: EnrichedPosition) -> QuantitativeAnalysis:
        """Return conservative default analysis"""
        return QuantitativeAnalysis(
            max_loss=1000.0,
            max_profit=100.0,
            risk_reward_ratio=0.1,
            probability_profit=50.0,
            expected_value=0.0,
            theta_efficiency=0.0,
            gamma_risk_level='medium',
            vega_exposure=0.0,
            breakeven_price=position.strike,
            breakeven_distance_pct=0.0,
            days_to_profitable_decay=position.dte,
            recommended_action='hold',
            confidence=50,
            reasoning='Default analysis - insufficient data',
            risk_level='medium',
            optimal_exit_price=None,
            stop_loss_price=None,
            roll_threshold_dte=7
        )


# ============================================================================
# Testing
# ============================================================================

def test_quantitative_analyzer():
    """Test quantitative analysis"""
    from datetime import date, timedelta, datetime

    print("\n" + "="*80)
    print("QUANTITATIVE ANALYZER TEST")
    print("="*80)

    # Create test position (profitable CSP)
    test_position = EnrichedPosition(
        symbol='AAPL',
        position_type='CSP',
        strike=150.0,
        expiration=date.today() + timedelta(days=40),
        dte=40,
        quantity=1,
        premium_collected=250.0,
        current_value=125.0,
        pnl_dollar=125.0,
        pnl_percent=50.0,
        stock_price=165.5,
        stock_price_ah=165.8,
        stock_change_percent=2.3,
        delta=-0.15,
        gamma=0.05,
        theta=2.5,
        vega=0.10,
        implied_volatility=30.0,
        moneyness='OTM',
        distance_to_strike=10.3,
        probability_itm=15.0,
        iv_rank=25.0,
        iv_percentile=30.0,
        stock_rsi=62.0,
        stock_trend='bullish',
        support_level=160.0,
        resistance_level=170.0,
        news_sentiment=0.2,
        news_count_24h=3,
        analyzed_at=datetime.now(),
        position_id='AAPL_150_2025-12-20_put'
    )

    analyzer = PositionQuantitativeAnalyzer()
    analysis = analyzer.analyze(test_position)

    print(f"\nPosition: {test_position.symbol} ${test_position.strike} {test_position.position_type}")
    print(f"P/L: ${test_position.pnl_dollar:.2f} ({test_position.pnl_percent:+.1f}%)")
    print(f"DTE: {test_position.dte} | Moneyness: {test_position.moneyness}")

    print("\n" + "="*80)
    print("QUANTITATIVE ANALYSIS")
    print("="*80)
    print(f"Recommendation: {analysis.recommended_action.upper()}")
    print(f"Confidence: {analysis.confidence}%")
    print(f"Risk Level: {analysis.risk_level.upper()}")
    print(f"\nReasoning: {analysis.reasoning}")

    print("\n" + "="*80)
    print("RISK METRICS")
    print("="*80)
    print(f"Max Profit: ${analysis.max_profit:.2f}")
    print(f"Max Loss: ${analysis.max_loss:.2f}")
    print(f"Risk/Reward: {analysis.risk_reward_ratio:.2f}")
    print(f"Probability of Profit: {analysis.probability_profit:.1f}%")
    print(f"Expected Value: ${analysis.expected_value:.2f}")

    print("\n" + "="*80)
    print("GREEKS ANALYSIS")
    print("="*80)
    print(f"Theta Efficiency: {analysis.theta_efficiency:.4f}")
    print(f"Gamma Risk: {analysis.gamma_risk_level.upper()}")
    print(f"Vega Exposure: ${analysis.vega_exposure:.2f}")

    print("\n" + "="*80)
    print("POSITION HEALTH")
    print("="*80)
    print(f"Breakeven Price: ${analysis.breakeven_price:.2f}")
    print(f"Distance to Breakeven: {analysis.breakeven_distance_pct:+.1f}%")
    print(f"Days to Profitable Decay: {analysis.days_to_profitable_decay}")


if __name__ == "__main__":
    test_quantitative_analyzer()
