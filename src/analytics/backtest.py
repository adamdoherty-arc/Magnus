"""
Backtesting Engine for Kalshi Prediction Strategies

Simulates trading strategies on historical predictions with:
- Kelly Criterion position sizing
- Risk management (max position, max drawdown)
- Comprehensive performance metrics
"""

import os
import psycopg2
import psycopg2.extras
import pandas as pd
import numpy as np
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import logging

from .metrics import (
    calculate_sharpe_ratio,
    calculate_sortino_ratio,
    calculate_max_drawdown,
    calculate_calmar_ratio,
    calculate_brier_score,
    calculate_log_loss,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class BacktestConfig:
    """Configuration for backtesting"""
    name: str = "Default Strategy"
    strategy_name: str = "base_strategy"
    version: str = "1.0"

    # Capital
    initial_capital: float = 10000.0

    # Position sizing
    position_sizing: str = "kelly"  # 'kelly', 'fixed', 'proportional'
    kelly_fraction: float = 0.25  # Quarter Kelly (conservative)
    fixed_bet_size: float = 100.0  # For fixed sizing
    proportional_pct: float = 5.0  # % of capital for proportional

    # Risk management
    max_position_size: float = 10.0  # Max % of capital per bet
    max_drawdown_limit: float = 20.0  # Stop if DD exceeds this %
    stop_loss_pct: Optional[float] = None  # Per-trade stop loss

    # Filters
    min_confidence: float = 0.0  # 0-100
    min_edge: float = 0.0  # Minimum edge percentage
    max_price: float = 0.95  # Don't buy above this price
    min_price: float = 0.05  # Don't sell below this price
    market_types: List[str] = None  # ['nfl', 'college'] or None for all

    # Time period
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

    def __post_init__(self):
        if self.market_types is None:
            self.market_types = ['nfl', 'college']


class BacktestEngine:
    """Backtesting engine for prediction strategies"""

    def __init__(self, db_config: Optional[Dict] = None):
        """
        Initialize backtesting engine.

        Args:
            db_config: Database configuration dict. If None, uses default.
        """
        self.db_config = db_config or {
            'host': 'localhost',
            'port': '5432',
            'database': 'magnus',
            'user': 'postgres',
            'password': os.getenv('DB_PASSWORD')
        }

    def get_connection(self):
        """Get database connection"""
        return psycopg2.connect(**self.db_config)

    def load_historical_data(self, config: BacktestConfig) -> pd.DataFrame:
        """
        Load historical prediction data for backtesting.

        Args:
            config: Backtest configuration

        Returns:
            DataFrame with prediction history
        """
        conn = self.get_connection()

        query = """
            SELECT
                pp.id,
                pp.ticker,
                pp.predicted_outcome,
                pp.actual_outcome,
                pp.confidence_score,
                pp.predicted_probability,
                pp.market_price,
                pp.is_correct,
                pp.market_type,
                pp.sector,
                pp.predicted_at,
                pp.settled_at,
                p.edge_percentage
            FROM prediction_performance pp
            JOIN kalshi_predictions p ON pp.prediction_id = p.id
            WHERE pp.actual_outcome IS NOT NULL
        """

        params = []

        # Apply filters
        if config.min_confidence > 0:
            query += " AND pp.confidence_score >= %s"
            params.append(config.min_confidence)

        if config.min_edge > 0:
            query += " AND p.edge_percentage >= %s"
            params.append(config.min_edge)

        if config.market_types:
            query += " AND pp.market_type = ANY(%s)"
            params.append(config.market_types)

        if config.start_date:
            query += " AND pp.predicted_at >= %s"
            params.append(config.start_date)

        if config.end_date:
            query += " AND pp.predicted_at <= %s"
            params.append(config.end_date)

        # Price filters
        query += " AND pp.market_price >= %s AND pp.market_price <= %s"
        params.extend([config.min_price, config.max_price])

        query += " ORDER BY pp.predicted_at"

        try:
            df = pd.read_sql_query(query, conn, params=params)
            logger.info(f"Loaded {len(df)} historical predictions for backtesting")
            return df
        finally:
            conn.close()

    def calculate_kelly_bet_size(self, edge: float, price: float, capital: float,
                                 kelly_fraction: float = 0.25) -> float:
        """
        Calculate bet size using Kelly Criterion.

        Kelly % = (edge / odds)
        where edge = expected_value - 1
        and odds = (1 / price) - 1

        Args:
            edge: Edge percentage (e.g., 5 for 5% edge)
            price: Market price (0-1)
            capital: Current capital
            kelly_fraction: Fraction of Kelly to bet (0.25 = quarter Kelly)

        Returns:
            Bet size in dollars
        """
        if price <= 0 or price >= 1 or edge <= 0:
            return 0.0

        # Calculate odds
        odds = (1.0 / price) - 1.0

        # Kelly formula: f = edge / odds
        kelly_pct = (edge / 100.0) / odds

        # Apply fraction (fractional Kelly)
        kelly_pct = kelly_pct * kelly_fraction

        # Cap at reasonable maximum (e.g., 25% of capital)
        kelly_pct = min(kelly_pct, 0.25)
        kelly_pct = max(kelly_pct, 0.0)

        bet_size = capital * kelly_pct

        return bet_size

    def calculate_position_size(self, row: pd.Series, capital: float,
                               config: BacktestConfig) -> float:
        """
        Calculate position size based on strategy.

        Args:
            row: DataFrame row with prediction data
            capital: Current capital
            config: Backtest configuration

        Returns:
            Position size in dollars
        """
        if config.position_sizing == 'fixed':
            position = config.fixed_bet_size

        elif config.position_sizing == 'proportional':
            position = capital * (config.proportional_pct / 100.0)

        elif config.position_sizing == 'kelly':
            edge = row.get('edge_percentage', 0)
            price = row['market_price']
            position = self.calculate_kelly_bet_size(
                edge, price, capital, config.kelly_fraction
            )

        else:
            raise ValueError(f"Unknown position sizing: {config.position_sizing}")

        # Apply max position size limit
        max_position = capital * (config.max_position_size / 100.0)
        position = min(position, max_position)

        # Ensure position doesn't exceed capital
        position = min(position, capital)

        return position

    def calculate_trade_pnl(self, row: pd.Series, position_size: float) -> Tuple[float, float]:
        """
        Calculate P&L for a trade.

        Args:
            row: DataFrame row with prediction data
            position_size: Size of position

        Returns:
            Tuple of (pnl, roi_pct)
        """
        if position_size == 0:
            return (0.0, 0.0)

        price = row['market_price']
        is_correct = row['is_correct']

        if is_correct:
            # Win: payout = position / price
            payout = position_size / price
            pnl = payout - position_size
        else:
            # Loss: lose entire position
            pnl = -position_size

        roi_pct = (pnl / position_size * 100) if position_size > 0 else 0.0

        return (pnl, roi_pct)

    def run_backtest(self, config: BacktestConfig) -> Dict:
        """
        Run backtest simulation.

        Args:
            config: Backtest configuration

        Returns:
            Dictionary with backtest results
        """
        logger.info(f"Starting backtest: {config.name}")

        # Load historical data
        df = self.load_historical_data(config)

        if df.empty:
            logger.warning("No historical data found for backtest")
            return self._empty_results(config)

        # Initialize tracking
        capital = config.initial_capital
        trades = []
        equity_curve = [capital]
        returns_list = []

        # Track performance
        total_trades = 0
        winning_trades = 0
        losing_trades = 0

        # Simulate each trade
        for idx, row in df.iterrows():
            # Calculate position size
            position_size = self.calculate_position_size(row, capital, config)

            if position_size == 0:
                continue

            # Calculate P&L
            pnl, roi_pct = self.calculate_trade_pnl(row, position_size)

            # Update capital
            capital_before = capital
            capital += pnl
            equity_curve.append(capital)

            # Track returns
            returns_list.append(pnl / position_size)

            # Record trade
            is_win = pnl > 0
            trades.append({
                'ticker': row['ticker'],
                'market_type': row['market_type'],
                'prediction_outcome': row['predicted_outcome'],
                'actual_outcome': row['actual_outcome'],
                'confidence_score': row['confidence_score'],
                'edge_percentage': row.get('edge_percentage', 0),
                'entry_price': row['market_price'],
                'position_size': position_size,
                'position_pct': (position_size / capital_before * 100) if capital_before > 0 else 0,
                'is_win': is_win,
                'pnl': pnl,
                'roi_pct': roi_pct,
                'trade_date': row['predicted_at'],
                'settlement_date': row['settled_at'],
                'capital_before': capital_before,
                'capital_after': capital,
            })

            # Update counters
            total_trades += 1
            if is_win:
                winning_trades += 1
            else:
                losing_trades += 1

            # Check drawdown limit
            if len(equity_curve) > 1:
                peak = max(equity_curve)
                current_dd = ((capital - peak) / peak * 100)
                if current_dd <= -config.max_drawdown_limit:
                    logger.warning(f"Max drawdown limit reached: {current_dd:.2f}%. Stopping backtest.")
                    break

        # Calculate performance metrics
        results = self._calculate_results(
            config, df, trades, equity_curve, returns_list,
            total_trades, winning_trades, losing_trades
        )

        # Store results in database
        self._store_results(config, results, trades)

        logger.info(f"Backtest complete: {total_trades} trades, Final Capital: ${capital:.2f}")

        return results

    def _calculate_results(self, config: BacktestConfig, df: pd.DataFrame,
                          trades: List[Dict], equity_curve: List[float],
                          returns_list: List[float], total_trades: int,
                          winning_trades: int, losing_trades: int) -> Dict:
        """Calculate comprehensive backtest results"""

        if total_trades == 0:
            return self._empty_results(config)

        final_capital = equity_curve[-1]
        total_pnl = final_capital - config.initial_capital
        total_return_pct = (total_pnl / config.initial_capital) * 100

        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0

        # Calculate financial metrics
        trades_df = pd.DataFrame(trades)
        avg_trade_pnl = trades_df['pnl'].mean()
        avg_win = trades_df[trades_df['is_win']]['pnl'].mean() if winning_trades > 0 else 0
        avg_loss = trades_df[~trades_df['is_win']]['pnl'].mean() if losing_trades > 0 else 0

        gross_profit = trades_df[trades_df['is_win']]['pnl'].sum() if winning_trades > 0 else 0
        gross_loss = abs(trades_df[~trades_df['is_win']]['pnl'].sum()) if losing_trades > 0 else 0
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else np.inf

        # Calculate risk-adjusted metrics
        returns = np.array(returns_list)
        equity = np.array(equity_curve)

        sharpe = calculate_sharpe_ratio(returns, periods_per_year=365) if len(returns) > 1 else 0
        sortino = calculate_sortino_ratio(returns, periods_per_year=365) if len(returns) > 1 else 0

        max_dd_pct, start_idx, end_idx = calculate_max_drawdown(equity)
        max_dd_amount = equity[start_idx] - equity[end_idx] if start_idx >= 0 else 0

        calmar = calculate_calmar_ratio(returns, equity, periods_per_year=365) if len(returns) > 1 else 0

        # Calculate calibration metrics
        predicted_probs = df['predicted_probability'].values
        actual_outcomes = df['is_correct'].astype(float).values

        avg_brier = calculate_brier_score(predicted_probs, actual_outcomes)
        avg_log_loss = calculate_log_loss(predicted_probs, actual_outcomes)

        return {
            'config': config,
            'start_date': df['predicted_at'].min(),
            'end_date': df['predicted_at'].max(),
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'final_capital': final_capital,
            'total_pnl': total_pnl,
            'total_return_pct': total_return_pct,
            'sharpe_ratio': sharpe,
            'sortino_ratio': sortino,
            'calmar_ratio': calmar,
            'max_drawdown_pct': abs(max_dd_pct),
            'max_drawdown_amount': max_dd_amount,
            'avg_trade_pnl': avg_trade_pnl,
            'avg_win_amount': avg_win,
            'avg_loss_amount': avg_loss,
            'profit_factor': profit_factor,
            'avg_brier_score': avg_brier,
            'avg_log_loss': avg_log_loss,
            'trades': trades,
            'equity_curve': equity_curve,
        }

    def _empty_results(self, config: BacktestConfig) -> Dict:
        """Return empty results structure"""
        return {
            'config': config,
            'start_date': None,
            'end_date': None,
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0.0,
            'final_capital': config.initial_capital,
            'total_pnl': 0.0,
            'total_return_pct': 0.0,
            'sharpe_ratio': 0.0,
            'sortino_ratio': 0.0,
            'calmar_ratio': 0.0,
            'max_drawdown_pct': 0.0,
            'max_drawdown_amount': 0.0,
            'avg_trade_pnl': 0.0,
            'avg_win_amount': 0.0,
            'avg_loss_amount': 0.0,
            'profit_factor': 0.0,
            'avg_brier_score': 0.0,
            'avg_log_loss': 0.0,
            'trades': [],
            'equity_curve': [config.initial_capital],
        }

    def _store_results(self, config: BacktestConfig, results: Dict, trades: List[Dict]):
        """Store backtest results in database"""
        conn = self.get_connection()
        cur = conn.cursor()

        try:
            # Store backtest summary
            cur.execute("""
                INSERT INTO backtest_results (
                    backtest_name, strategy_name, version,
                    start_date, end_date,
                    initial_capital, position_sizing, kelly_fraction,
                    max_position_size, max_drawdown_limit,
                    min_confidence, min_edge, market_types,
                    total_trades, winning_trades, losing_trades, win_rate,
                    final_capital, total_pnl, total_return_pct,
                    sharpe_ratio, sortino_ratio, calmar_ratio,
                    max_drawdown_pct, max_drawdown_amount,
                    avg_trade_pnl, avg_win_amount, avg_loss_amount, profit_factor,
                    avg_brier_score, avg_log_loss
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s
                )
                RETURNING id
            """, (
                config.name, config.strategy_name, config.version,
                results['start_date'], results['end_date'],
                config.initial_capital, config.position_sizing, config.kelly_fraction,
                config.max_position_size, config.max_drawdown_limit,
                config.min_confidence, config.min_edge, config.market_types,
                results['total_trades'], results['winning_trades'], results['losing_trades'],
                results['win_rate'],
                results['final_capital'], results['total_pnl'], results['total_return_pct'],
                results['sharpe_ratio'], results['sortino_ratio'], results['calmar_ratio'],
                results['max_drawdown_pct'], results['max_drawdown_amount'],
                results['avg_trade_pnl'], results['avg_win_amount'], results['avg_loss_amount'],
                results['profit_factor'],
                results['avg_brier_score'], results['avg_log_loss']
            ))

            backtest_id = cur.fetchone()[0]

            # Store individual trades
            if trades:
                for trade in trades:
                    cur.execute("""
                        INSERT INTO backtest_trades (
                            backtest_id, ticker, market_type,
                            prediction_outcome, confidence_score, edge_percentage,
                            entry_price, position_size, position_pct,
                            actual_outcome, is_win, pnl, roi_pct,
                            trade_date, settlement_date,
                            capital_before, capital_after
                        ) VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                    """, (
                        backtest_id, trade['ticker'], trade['market_type'],
                        trade['prediction_outcome'], trade['confidence_score'],
                        trade['edge_percentage'],
                        trade['entry_price'], trade['position_size'], trade['position_pct'],
                        trade['actual_outcome'], trade['is_win'], trade['pnl'], trade['roi_pct'],
                        trade['trade_date'], trade['settlement_date'],
                        trade['capital_before'], trade['capital_after']
                    ))

            conn.commit()
            logger.info(f"Stored backtest results with ID: {backtest_id}")

        except Exception as e:
            conn.rollback()
            logger.error(f"Error storing backtest results: {e}")

        finally:
            cur.close()
            conn.close()

    def compare_strategies(self, configs: List[BacktestConfig]) -> pd.DataFrame:
        """
        Compare multiple strategies.

        Args:
            configs: List of backtest configurations

        Returns:
            DataFrame with comparison metrics
        """
        results = []

        for config in configs:
            backtest_results = self.run_backtest(config)
            results.append({
                'Strategy': config.name,
                'Total Trades': backtest_results['total_trades'],
                'Win Rate': f"{backtest_results['win_rate']:.1f}%",
                'Total Return': f"{backtest_results['total_return_pct']:.2f}%",
                'Sharpe': f"{backtest_results['sharpe_ratio']:.2f}",
                'Sortino': f"{backtest_results['sortino_ratio']:.2f}",
                'Max DD': f"{backtest_results['max_drawdown_pct']:.2f}%",
                'Profit Factor': f"{backtest_results['profit_factor']:.2f}",
            })

        return pd.DataFrame(results)


if __name__ == "__main__":
    # Test backtest engine
    print("="*80)
    print("BACKTEST ENGINE - Test")
    print("="*80)

    engine = BacktestEngine()

    # Create test configuration
    config = BacktestConfig(
        name="Conservative Kelly Strategy",
        strategy_name="kelly_conservative",
        version="1.0",
        initial_capital=10000.0,
        position_sizing="kelly",
        kelly_fraction=0.25,
        max_position_size=10.0,
        min_confidence=60.0,
        min_edge=5.0,
    )

    # Run backtest
    results = engine.run_backtest(config)

    print(f"\nBacktest Results: {config.name}")
    print(f"  Period: {results['start_date']} to {results['end_date']}")
    print(f"  Total Trades: {results['total_trades']}")
    print(f"  Win Rate: {results['win_rate']:.2f}%")
    print(f"  Final Capital: ${results['final_capital']:.2f}")
    print(f"  Total Return: {results['total_return_pct']:.2f}%")
    print(f"  Sharpe Ratio: {results['sharpe_ratio']:.2f}")
    print(f"  Sortino Ratio: {results['sortino_ratio']:.2f}")
    print(f"  Max Drawdown: {results['max_drawdown_pct']:.2f}%")
    print(f"  Profit Factor: {results['profit_factor']:.2f}")

    print("\n" + "="*80)
    print("Test Complete!")
    print("="*80)
