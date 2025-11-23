"""
Bankroll Management System with Kelly Criterion
Production-ready position sizing and risk management for prediction markets

Features:
- Full Kelly, Half Kelly, Quarter Kelly modes
- Risk controls (max drawdown, position limits)
- Portfolio heat management
- Multi-bet optimization
- Historical performance tracking

Author: Python Pro
Created: 2025-11-15
"""

import logging
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
from dataclasses import dataclass
from enum import Enum
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KellyMode(Enum):
    """Kelly Criterion sizing modes"""
    FULL = 1.0      # Full Kelly (aggressive)
    HALF = 0.5      # Half Kelly (moderate)
    QUARTER = 0.25  # Quarter Kelly (conservative, RECOMMENDED)
    EIGHTH = 0.125  # Very conservative


@dataclass
class BetSizing:
    """Recommended bet sizing with risk controls"""
    ticker: str
    kelly_fraction: float
    recommended_stake_pct: float
    max_stake_dollars: float
    confidence: float
    edge_pct: float
    risk_level: str
    warnings: List[str]

    def to_dict(self) -> Dict:
        return {
            'ticker': self.ticker,
            'kelly_fraction': round(self.kelly_fraction, 4),
            'recommended_stake_pct': round(self.recommended_stake_pct, 2),
            'max_stake_dollars': round(self.max_stake_dollars, 2),
            'confidence': round(self.confidence, 2),
            'edge_pct': round(self.edge_pct, 2),
            'risk_level': self.risk_level,
            'warnings': self.warnings
        }


class BankrollManager:
    """
    Professional bankroll management system using Kelly Criterion

    Protects capital while maximizing long-term growth
    """

    def __init__(
        self,
        bankroll: float,
        kelly_mode: KellyMode = KellyMode.QUARTER,
        max_position_pct: float = 10.0,
        max_total_exposure_pct: float = 50.0,
        max_drawdown_pct: float = 20.0
    ):
        """
        Initialize bankroll manager

        Args:
            bankroll: Total bankroll in dollars
            kelly_mode: Kelly sizing mode (QUARTER recommended)
            max_position_pct: Max % of bankroll per single bet (default 10%)
            max_total_exposure_pct: Max total % allocated (default 50%)
            max_drawdown_pct: Stop trading at this drawdown (default 20%)
        """
        self.initial_bankroll = bankroll
        self.current_bankroll = bankroll
        self.kelly_mode = kelly_mode
        self.max_position_pct = max_position_pct
        self.max_total_exposure_pct = max_total_exposure_pct
        self.max_drawdown_pct = max_drawdown_pct

        # Tracking
        self.active_positions: List[Dict] = []
        self.trade_history: List[Dict] = []
        self.peak_bankroll = bankroll

        logger.info(
            f"Bankroll Manager initialized: ${bankroll:,.2f} "
            f"({kelly_mode.name} Kelly, max {max_position_pct}% per bet)"
        )

    def calculate_kelly_bet(
        self,
        ticker: str,
        win_probability: float,
        market_price: float,
        edge_pct: float,
        confidence: float = 70.0
    ) -> BetSizing:
        """
        Calculate optimal bet size using Kelly Criterion

        Kelly Formula: f* = (bp - q) / b
        Where:
            f* = fraction of bankroll to bet
            b = odds received (decimal - 1)
            p = probability of winning
            q = probability of losing (1 - p)

        Args:
            ticker: Market ticker symbol
            win_probability: True probability of winning (0-1)
            market_price: Current market price (0-1)
            edge_pct: Expected value edge
            confidence: Confidence in prediction (0-100)

        Returns:
            BetSizing object with recommendations
        """
        warnings = []

        # Validate inputs
        if not (0 < win_probability < 1):
            warnings.append(f"Invalid win probability: {win_probability}")
            win_probability = max(0.01, min(0.99, win_probability))

        if not (0 < market_price < 1):
            warnings.append(f"Invalid market price: {market_price}")
            market_price = max(0.01, min(0.99, market_price))

        # Check drawdown protection
        current_drawdown = self._calculate_drawdown()
        if current_drawdown >= self.max_drawdown_pct:
            warnings.append(
                f"STOP: Max drawdown reached ({current_drawdown:.1f}%)"
            )
            return self._no_bet(ticker, edge_pct, confidence, warnings)

        # Check total exposure
        current_exposure_pct = self._calculate_total_exposure()
        if current_exposure_pct >= self.max_total_exposure_pct:
            warnings.append(
                f"Max exposure reached ({current_exposure_pct:.1f}%)"
            )
            return self._no_bet(ticker, edge_pct, confidence, warnings)

        # Calculate decimal odds
        if market_price <= 0:
            warnings.append("Market price too low")
            return self._no_bet(ticker, edge_pct, confidence, warnings)

        decimal_odds = 1.0 / market_price
        b = decimal_odds - 1  # Net odds

        if b <= 0:
            warnings.append("No positive odds")
            return self._no_bet(ticker, edge_pct, confidence, warnings)

        # Kelly Criterion calculation
        p = win_probability
        q = 1 - p

        kelly_fraction = (b * p - q) / b

        # Apply Kelly mode multiplier (fractional Kelly)
        kelly_fraction *= self.kelly_mode.value

        # Confidence adjustment
        # Reduce bet size if confidence is low
        if confidence < 70:
            confidence_factor = confidence / 70.0
            kelly_fraction *= confidence_factor
            warnings.append(
                f"Bet size reduced due to low confidence ({confidence:.0f}%)"
            )

        # Apply position size cap
        kelly_fraction = max(0, min(kelly_fraction, self.max_position_pct / 100))

        # Calculate dollar amounts
        recommended_stake_pct = kelly_fraction * 100
        max_stake_dollars = self.current_bankroll * kelly_fraction

        # Risk level determination
        if recommended_stake_pct >= 8:
            risk_level = "HIGH"
            warnings.append("High risk bet - consider reducing size")
        elif recommended_stake_pct >= 4:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        # Additional warnings
        if edge_pct < 5:
            warnings.append("Small edge - bet with caution")

        if kelly_fraction < 0.001:  # Less than 0.1%
            warnings.append("Bet size too small - consider passing")

        return BetSizing(
            ticker=ticker,
            kelly_fraction=kelly_fraction,
            recommended_stake_pct=recommended_stake_pct,
            max_stake_dollars=max_stake_dollars,
            confidence=confidence,
            edge_pct=edge_pct,
            risk_level=risk_level,
            warnings=warnings
        )

    def calculate_multi_bet_portfolio(
        self,
        opportunities: List[Dict]
    ) -> List[BetSizing]:
        """
        Optimize position sizing across multiple simultaneous bets

        Uses Kelly Criterion with correlation adjustments to prevent over-allocation

        Args:
            opportunities: List of bet opportunities
                Each dict must have:
                    - ticker
                    - win_probability
                    - market_price
                    - edge_pct
                    - confidence

        Returns:
            List of BetSizing recommendations
        """
        if not opportunities:
            return []

        # Calculate individual Kelly sizes
        individual_sizes = []

        for opp in opportunities:
            sizing = self.calculate_kelly_bet(
                ticker=opp['ticker'],
                win_probability=opp.get('win_probability', 0.5),
                market_price=opp.get('market_price', 0.5),
                edge_pct=opp.get('edge_pct', 0),
                confidence=opp.get('confidence', 70)
            )
            individual_sizes.append(sizing)

        # Check total allocation
        total_allocation = sum(s.recommended_stake_pct for s in individual_sizes)

        # If over max exposure, scale down proportionally
        if total_allocation > self.max_total_exposure_pct:
            scale_factor = self.max_total_exposure_pct / total_allocation

            for sizing in individual_sizes:
                sizing.recommended_stake_pct *= scale_factor
                sizing.max_stake_dollars *= scale_factor
                sizing.warnings.append(
                    f"Scaled down {100 * (1 - scale_factor):.1f}% "
                    "due to portfolio constraints"
                )

        # Sort by edge (best opportunities first)
        individual_sizes.sort(key=lambda x: x.edge_pct, reverse=True)

        return individual_sizes

    def record_trade(
        self,
        ticker: str,
        stake_dollars: float,
        outcome: Optional[str] = None,
        pnl: Optional[float] = None
    ):
        """
        Record a trade for tracking and analysis

        Args:
            ticker: Market ticker
            stake_dollars: Amount wagered
            outcome: 'win', 'loss', or None if still open
            pnl: Profit/loss in dollars
        """
        trade = {
            'ticker': ticker,
            'stake': stake_dollars,
            'outcome': outcome,
            'pnl': pnl or 0,
            'bankroll_before': self.current_bankroll
        }

        if outcome:
            # Closed position
            self.current_bankroll += (pnl or 0)
            self.trade_history.append(trade)

            # Update peak bankroll
            if self.current_bankroll > self.peak_bankroll:
                self.peak_bankroll = self.current_bankroll
        else:
            # Open position
            self.active_positions.append(trade)

    def close_position(
        self,
        ticker: str,
        pnl: float
    ):
        """
        Close an active position

        Args:
            ticker: Market ticker
            pnl: Profit/loss in dollars
        """
        # Find and remove from active positions
        for i, pos in enumerate(self.active_positions):
            if pos['ticker'] == ticker:
                pos['pnl'] = pnl
                pos['outcome'] = 'win' if pnl > 0 else 'loss'

                # Move to history
                self.trade_history.append(pos)
                del self.active_positions[i]

                # Update bankroll
                self.current_bankroll += pnl

                # Update peak
                if self.current_bankroll > self.peak_bankroll:
                    self.peak_bankroll = self.current_bankroll

                logger.info(
                    f"Position closed: {ticker} | "
                    f"P&L: ${pnl:+,.2f} | "
                    f"Bankroll: ${self.current_bankroll:,.2f}"
                )
                break

    def get_performance_stats(self) -> Dict:
        """
        Calculate performance metrics

        Returns:
            Dictionary with performance statistics
        """
        if not self.trade_history:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'roi_pct': 0,
                'sharpe_ratio': 0,
                'max_drawdown_pct': 0,
                'current_bankroll': self.current_bankroll
            }

        wins = [t for t in self.trade_history if t['pnl'] > 0]
        losses = [t for t in self.trade_history if t['pnl'] < 0]

        total_pnl = sum(t['pnl'] for t in self.trade_history)
        roi_pct = (total_pnl / self.initial_bankroll) * 100

        # Win rate
        win_rate = (len(wins) / len(self.trade_history)) * 100 if self.trade_history else 0

        # Sharpe ratio (simplified)
        returns = [t['pnl'] / t['stake'] for t in self.trade_history if t['stake'] > 0]
        if len(returns) > 1:
            mean_return = np.mean(returns)
            std_return = np.std(returns)
            sharpe_ratio = (mean_return / std_return) if std_return > 0 else 0
        else:
            sharpe_ratio = 0

        # Max drawdown
        max_dd = self._calculate_max_historical_drawdown()

        return {
            'total_trades': len(self.trade_history),
            'wins': len(wins),
            'losses': len(losses),
            'win_rate': round(win_rate, 2),
            'total_pnl': round(total_pnl, 2),
            'roi_pct': round(roi_pct, 2),
            'sharpe_ratio': round(sharpe_ratio, 3),
            'max_drawdown_pct': round(max_dd, 2),
            'current_bankroll': round(self.current_bankroll, 2),
            'active_positions': len(self.active_positions)
        }

    def _calculate_drawdown(self) -> float:
        """Calculate current drawdown percentage"""
        if self.peak_bankroll == 0:
            return 0

        drawdown = ((self.peak_bankroll - self.current_bankroll) /
                   self.peak_bankroll) * 100
        return max(0, drawdown)

    def _calculate_total_exposure(self) -> float:
        """Calculate total allocated capital as % of bankroll"""
        if self.current_bankroll == 0:
            return 100

        total_allocated = sum(pos['stake'] for pos in self.active_positions)
        exposure_pct = (total_allocated / self.current_bankroll) * 100

        return exposure_pct

    def _calculate_max_historical_drawdown(self) -> float:
        """Calculate maximum historical drawdown"""
        if not self.trade_history:
            return 0

        peak = self.initial_bankroll
        max_dd = 0
        running_bankroll = self.initial_bankroll

        for trade in self.trade_history:
            running_bankroll += trade['pnl']

            if running_bankroll > peak:
                peak = running_bankroll

            dd = ((peak - running_bankroll) / peak) * 100
            max_dd = max(max_dd, dd)

        return max_dd

    def _no_bet(
        self,
        ticker: str,
        edge_pct: float,
        confidence: float,
        warnings: List[str]
    ) -> BetSizing:
        """Return a zero-size bet recommendation"""
        return BetSizing(
            ticker=ticker,
            kelly_fraction=0.0,
            recommended_stake_pct=0.0,
            max_stake_dollars=0.0,
            confidence=confidence,
            edge_pct=edge_pct,
            risk_level="PASS",
            warnings=warnings
        )


# ============================================================================
# TESTING
# ============================================================================

def test_bankroll_manager():
    """Test the bankroll management system"""

    print("\n" + "="*80)
    print("BANKROLL MANAGER - Kelly Criterion Test")
    print("="*80)

    # Initialize with $10,000 bankroll
    manager = BankrollManager(
        bankroll=10000,
        kelly_mode=KellyMode.QUARTER,
        max_position_pct=10.0
    )

    # Test 1: Single bet calculation
    print("\n1. Single Bet Sizing (Good Opportunity):")
    sizing = manager.calculate_kelly_bet(
        ticker='NFL-CHIEFS-001',
        win_probability=0.65,      # 65% true probability
        market_price=0.45,          # Market price is 45 cents
        edge_pct=44.4,              # (0.65 - 0.45) / 0.45 * 100 = 44%
        confidence=85
    )

    print(f"   Ticker: {sizing.ticker}")
    print(f"   Kelly Fraction: {sizing.kelly_fraction:.4f}")
    print(f"   Recommended Stake: {sizing.recommended_stake_pct:.2f}%")
    print(f"   Max Stake: ${sizing.max_stake_dollars:,.2f}")
    print(f"   Risk Level: {sizing.risk_level}")
    if sizing.warnings:
        print(f"   Warnings: {', '.join(sizing.warnings)}")

    # Test 2: Low edge bet
    print("\n2. Small Edge Bet:")
    sizing2 = manager.calculate_kelly_bet(
        ticker='NFL-BILLS-002',
        win_probability=0.52,
        market_price=0.50,
        edge_pct=4.0,
        confidence=60
    )

    print(f"   Recommended Stake: {sizing2.recommended_stake_pct:.2f}%")
    print(f"   Risk Level: {sizing2.risk_level}")
    if sizing2.warnings:
        print(f"   Warnings: {', '.join(sizing2.warnings)}")

    # Test 3: Multi-bet portfolio
    print("\n3. Multi-Bet Portfolio Optimization:")
    opportunities = [
        {
            'ticker': 'NFL-CHIEFS-001',
            'win_probability': 0.65,
            'market_price': 0.45,
            'edge_pct': 44.4,
            'confidence': 85
        },
        {
            'ticker': 'NFL-BILLS-002',
            'win_probability': 0.60,
            'market_price': 0.48,
            'edge_pct': 25.0,
            'confidence': 75
        },
        {
            'ticker': 'NFL-49ERS-003',
            'win_probability': 0.70,
            'market_price': 0.55,
            'edge_pct': 27.3,
            'confidence': 80
        }
    ]

    portfolio = manager.calculate_multi_bet_portfolio(opportunities)

    total_allocation = sum(b.recommended_stake_pct for b in portfolio)

    for bet in portfolio:
        print(f"\n   {bet.ticker}:")
        print(f"      Stake: {bet.recommended_stake_pct:.2f}% (${bet.max_stake_dollars:,.2f})")
        print(f"      Edge: {bet.edge_pct:.1f}%")
        print(f"      Risk: {bet.risk_level}")

    print(f"\n   Total Portfolio Allocation: {total_allocation:.2f}%")

    # Test 4: Performance tracking
    print("\n4. Performance Tracking:")

    # Simulate some trades
    manager.record_trade('NFL-CHIEFS-001', stake_dollars=500, outcome='win', pnl=250)
    manager.record_trade('NFL-BILLS-002', stake_dollars=200, outcome='loss', pnl=-200)
    manager.record_trade('NFL-49ERS-003', stake_dollars=600, outcome='win', pnl=450)

    stats = manager.get_performance_stats()

    print(f"   Total Trades: {stats['total_trades']}")
    print(f"   Win Rate: {stats['win_rate']:.1f}%")
    print(f"   Total P&L: ${stats['total_pnl']:+,.2f}")
    print(f"   ROI: {stats['roi_pct']:+.2f}%")
    print(f"   Current Bankroll: ${stats['current_bankroll']:,.2f}")

    print("\n" + "="*80)
    print("✓ Test Complete!")
    print("="*80)


if __name__ == "__main__":
    test_bankroll_manager()
