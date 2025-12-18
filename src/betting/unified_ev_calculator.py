"""
Unified Expected Value Calculator
Ensures consistent EV and confidence calculations across all betting components

This module standardizes the formulas used to calculate:
- Expected Value (EV) - profitability of a bet
- Confidence Score - reliability of the prediction
- Edge Size - how much the AI disagrees with the market
"""

import logging
from typing import Dict, Tuple

logger = logging.getLogger(__name__)


class UnifiedEVCalculator:
    """
    Standardized Expected Value calculation for probability-based markets (like Kalshi)

    Formula: EV = (Win_Prob × Potential_Profit) - (Lose_Prob × Stake)
    Where:
        - Win_Prob: AI predicted probability of winning (0-1)
        - Potential_Profit: How much you win per $1 bet
        - Lose_Prob: Probability of losing (1 - Win_Prob)
        - Stake: Amount bet (always 1.0 for normalized calculation)

    For Kalshi-style markets:
        - You buy YES for X cents (as probability: 0-1)
        - If YES wins, you get $1 (100 cents)
        - Net profit = $1 - X = (1 - X)
        - Profit ratio = (1 - X) / X
    """

    @staticmethod
    def calculate_ev(ai_win_prob: float, market_price: float) -> float:
        """
        Calculate Expected Value for a binary prediction market

        Args:
            ai_win_prob: AI predicted win probability (0-1)
            market_price: Market implied probability / price (0-1)

        Returns:
            Expected value as decimal (-1.0 to +∞)
            Positive = profitable bet
            Negative = unprofitable bet

        Example:
            AI thinks 60% chance (ai_win_prob=0.6)
            Market priced at 45% (market_price=0.45)

            Potential profit = (1.0 - 0.45) / 0.45 = 1.222
            EV = (0.6 * 1.222) - (0.4 * 1.0) = 0.733 - 0.4 = 0.333
            EV% = 33.3% (very profitable!)
        """
        if market_price <= 0 or market_price >= 1:
            logger.warning(f"Invalid market_price: {market_price} (must be between 0 and 1)")
            return 0.0

        if ai_win_prob < 0 or ai_win_prob > 1:
            logger.warning(f"Invalid ai_win_prob: {ai_win_prob} (must be between 0 and 1)")
            return 0.0

        # Calculate potential profit if bet wins
        # For a YES bet at market_price, you pay market_price and get $1 if you win
        # Profit = $1 - market_price
        # Profit ratio = ($1 - market_price) / market_price
        potential_profit = (1.0 - market_price) / market_price

        # Expected Value formula
        # EV = (Probability of Win × Profit if Win) - (Probability of Loss × Loss if Loss)
        ev = (ai_win_prob * potential_profit) - ((1 - ai_win_prob) * 1.0)

        return ev

    @staticmethod
    def calculate_ev_percentage(ai_win_prob: float, market_price: float) -> float:
        """
        Calculate Expected Value as a percentage (for display)

        Returns:
            EV as percentage (-100% to +∞)
        """
        ev = UnifiedEVCalculator.calculate_ev(ai_win_prob, market_price)
        return ev * 100

    @staticmethod
    def calculate_edge(ai_win_prob: float, market_price: float) -> float:
        """
        Calculate edge (how much AI disagrees with market)

        Args:
            ai_win_prob: AI predicted probability (0-1)
            market_price: Market implied probability (0-1)

        Returns:
            Edge as decimal (can be positive or negative)
            Positive = AI is more bullish than market
            Negative = AI is more bearish than market
        """
        return ai_win_prob - market_price

    @staticmethod
    def calculate_edge_percentage(ai_win_prob: float, market_price: float) -> float:
        """
        Calculate edge as a percentage (for display)

        Returns:
            Edge as percentage (-100% to +100%)
        """
        return UnifiedEVCalculator.calculate_edge(ai_win_prob, market_price) * 100

    @staticmethod
    def calculate_confidence(
        ev: float,
        edge: float,
        ai_win_prob: float,
        market_efficiency: float = 0.0
    ) -> float:
        """
        Calculate confidence score (0-100) based on multiple factors

        Args:
            ev: Expected value as decimal
            edge: How much AI disagrees with market (decimal)
            ai_win_prob: AI predicted win probability (0-1)
            market_efficiency: Market inefficiency indicator (0-1, default 0)

        Returns:
            Confidence score (0-100)

        Methodology:
            - Base confidence: 50 (neutral starting point)
            - Edge contribution: ±30 points (bigger disagreement = higher confidence)
            - Win probability contribution: ±20 points (extreme probabilities = higher confidence)
            - Market efficiency penalty: -10 points if market is very inefficient
        """
        # Start at neutral
        confidence = 50.0

        # Edge contribution (up to ±30 points)
        # Large edge (0.3 = 30%) → +30 points
        # No edge (0.0) → 0 points
        edge_contribution = min(abs(edge) * 100, 30.0)
        if ev > 0:  # Only add to confidence if EV is positive
            confidence += edge_contribution
        else:  # Reduce confidence if EV is negative
            confidence -= edge_contribution * 0.5  # Penalize less for negative EV

        # Win probability contribution (up to ±20 points)
        # Very confident (90%+) or very unconfident (10%-) → +20 points
        # Close to 50/50 → 0 points
        prob_distance_from_half = abs(ai_win_prob - 0.5)
        prob_contribution = min(prob_distance_from_half * 40, 20.0)
        confidence += prob_contribution

        # Market efficiency penalty
        # If market is very inefficient (prices don't sum to 1.0), reduce confidence
        if market_efficiency > 0.05:  # >5% inefficiency
            confidence -= min(market_efficiency * 100, 10.0)

        # Clamp to 0-100 range
        return max(0.0, min(100.0, confidence))

    @staticmethod
    def calculate_all(
        ai_win_prob: float,
        market_price: float,
        market_efficiency: float = 0.0
    ) -> Dict[str, float]:
        """
        Calculate all metrics at once (convenience method)

        Args:
            ai_win_prob: AI predicted win probability (0-1)
            market_price: Market implied probability (0-1)
            market_efficiency: Market inefficiency indicator (0-1, default 0)

        Returns:
            Dictionary with all calculated metrics:
            {
                'ev': Expected value as decimal,
                'ev_percentage': EV as percentage,
                'edge': Edge as decimal,
                'edge_percentage': Edge as percentage,
                'confidence': Confidence score (0-100)
            }
        """
        ev = UnifiedEVCalculator.calculate_ev(ai_win_prob, market_price)
        edge = UnifiedEVCalculator.calculate_edge(ai_win_prob, market_price)
        confidence = UnifiedEVCalculator.calculate_confidence(
            ev, edge, ai_win_prob, market_efficiency
        )

        return {
            'ev': ev,
            'ev_percentage': ev * 100,
            'edge': edge,
            'edge_percentage': edge * 100,
            'confidence': confidence
        }

    @staticmethod
    def validate_inputs(ai_win_prob: float, market_price: float) -> Tuple[bool, str]:
        """
        Validate inputs to ensure they're in valid ranges

        Returns:
            (is_valid, error_message)
        """
        if not (0 <= ai_win_prob <= 1):
            return False, f"ai_win_prob must be between 0 and 1, got {ai_win_prob}"

        if not (0 < market_price < 1):
            return False, f"market_price must be between 0 and 1 (exclusive), got {market_price}"

        return True, ""


# Convenience functions for backward compatibility
def calculate_expected_value(ai_win_prob: float, market_price: float) -> float:
    """Legacy function name for backward compatibility"""
    return UnifiedEVCalculator.calculate_ev(ai_win_prob, market_price)


def calculate_confidence_score(
    ev: float,
    edge: float,
    ai_win_prob: float,
    market_efficiency: float = 0.0
) -> float:
    """Legacy function name for backward compatibility"""
    return UnifiedEVCalculator.calculate_confidence(ev, edge, ai_win_prob, market_efficiency)
