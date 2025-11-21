"""
Sample Backtest Script for Kalshi Predictions

Demonstrates how to run backtests with different strategies and compare results.

Usage:
    python run_sample_backtest.py
"""

import sys
import os
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from analytics.backtest import BacktestEngine, BacktestConfig


def run_sample_backtests():
    """Run multiple backtest strategies and compare results"""

    print("="*80)
    print("KALSHI PREDICTION BACKTESTING")
    print("="*80)
    print()

    # Initialize backtest engine
    engine = BacktestEngine()

    # Define multiple strategies to test
    strategies = []

    # Strategy 1: Conservative Kelly (Quarter Kelly)
    strategies.append(BacktestConfig(
        name="Conservative Kelly",
        strategy_name="kelly_conservative",
        version="1.0",
        initial_capital=10000.0,
        position_sizing="kelly",
        kelly_fraction=0.25,
        max_position_size=10.0,
        max_drawdown_limit=20.0,
        min_confidence=60.0,
        min_edge=5.0,
        market_types=["nfl", "college"]
    ))

    # Strategy 2: Aggressive Kelly (Half Kelly)
    strategies.append(BacktestConfig(
        name="Aggressive Kelly",
        strategy_name="kelly_aggressive",
        version="1.0",
        initial_capital=10000.0,
        position_sizing="kelly",
        kelly_fraction=0.5,
        max_position_size=15.0,
        max_drawdown_limit=30.0,
        min_confidence=55.0,
        min_edge=3.0,
        market_types=["nfl", "college"]
    ))

    # Strategy 3: Fixed Size (Conservative)
    strategies.append(BacktestConfig(
        name="Fixed Size Conservative",
        strategy_name="fixed_conservative",
        version="1.0",
        initial_capital=10000.0,
        position_sizing="fixed",
        fixed_bet_size=100.0,
        max_position_size=10.0,
        max_drawdown_limit=25.0,
        min_confidence=65.0,
        min_edge=7.0,
        market_types=["nfl", "college"]
    ))

    # Strategy 4: High Confidence Only
    strategies.append(BacktestConfig(
        name="High Confidence Only",
        strategy_name="high_confidence",
        version="1.0",
        initial_capital=10000.0,
        position_sizing="kelly",
        kelly_fraction=0.25,
        max_position_size=12.0,
        max_drawdown_limit=20.0,
        min_confidence=75.0,
        min_edge=8.0,
        market_types=["nfl", "college"]
    ))

    # Strategy 5: NFL Only
    strategies.append(BacktestConfig(
        name="NFL Only - Kelly",
        strategy_name="nfl_only",
        version="1.0",
        initial_capital=10000.0,
        position_sizing="kelly",
        kelly_fraction=0.25,
        max_position_size=10.0,
        max_drawdown_limit=20.0,
        min_confidence=60.0,
        min_edge=5.0,
        market_types=["nfl"]
    ))

    # Run backtests
    results_list = []

    for i, config in enumerate(strategies, 1):
        print(f"\nRunning Backtest {i}/{len(strategies)}: {config.name}")
        print("-" * 80)

        try:
            results = engine.run_backtest(config)

            # Display results
            print(f"\n  Strategy: {config.name}")
            print(f"  Period: {results['start_date']} to {results['end_date']}")
            print(f"  Total Trades: {results['total_trades']}")
            print(f"  Win Rate: {results['win_rate']:.2f}%")
            print(f"  Final Capital: ${results['final_capital']:,.2f}")
            print(f"  Total P&L: ${results['total_pnl']:,.2f}")
            print(f"  Total Return: {results['total_return_pct']:.2f}%")
            print(f"  Sharpe Ratio: {results['sharpe_ratio']:.2f}")
            print(f"  Sortino Ratio: {results['sortino_ratio']:.2f}")
            print(f"  Max Drawdown: {results['max_drawdown_pct']:.2f}%")
            print(f"  Profit Factor: {results['profit_factor']:.2f}")
            print(f"  Avg Brier Score: {results['avg_brier_score']:.4f}")

            results_list.append({
                'strategy': config.name,
                'trades': results['total_trades'],
                'win_rate': results['win_rate'],
                'total_return': results['total_return_pct'],
                'sharpe': results['sharpe_ratio'],
                'sortino': results['sortino_ratio'],
                'max_dd': results['max_drawdown_pct'],
                'profit_factor': results['profit_factor'],
            })

        except Exception as e:
            print(f"  ERROR: {e}")
            continue

    # Comparison summary
    print("\n" + "="*80)
    print("STRATEGY COMPARISON SUMMARY")
    print("="*80)

    if results_list:
        # Header
        print(f"\n{'Strategy':<30} {'Trades':<8} {'Win Rate':<10} {'Return':<10} {'Sharpe':<8} {'Max DD':<10}")
        print("-" * 80)

        # Sort by total return
        results_list.sort(key=lambda x: x['total_return'], reverse=True)

        for result in results_list:
            print(f"{result['strategy']:<30} "
                  f"{result['trades']:<8} "
                  f"{result['win_rate']:>6.1f}%   "
                  f"{result['total_return']:>7.2f}%  "
                  f"{result['sharpe']:>6.2f}  "
                  f"{result['max_dd']:>7.2f}%")

        # Best strategy
        best = results_list[0]
        print(f"\n🏆 Best Strategy: {best['strategy']}")
        print(f"   Return: {best['total_return']:.2f}% | Sharpe: {best['sharpe']:.2f} | Max DD: {best['max_dd']:.2f}%")

    else:
        print("\nNo results available")

    print("\n" + "="*80)
    print("Backtest Complete! Results stored in database.")
    print("View detailed analytics at: http://localhost:8501 (Analytics Performance page)")
    print("="*80)


def run_custom_backtest():
    """Run a single custom backtest with user-defined parameters"""

    print("="*80)
    print("CUSTOM BACKTEST")
    print("="*80)
    print()

    # Custom configuration
    config = BacktestConfig(
        name="Custom Strategy",
        strategy_name="custom",
        version="1.0",
        initial_capital=10000.0,
        position_sizing="kelly",
        kelly_fraction=0.25,
        max_position_size=10.0,
        max_drawdown_limit=20.0,
        min_confidence=60.0,
        min_edge=5.0,
        market_types=["nfl", "college"]
    )

    # Run backtest
    engine = BacktestEngine()
    results = engine.run_backtest(config)

    # Display detailed results
    print(f"\nBacktest Results: {config.name}")
    print("=" * 80)
    print(f"  Period: {results['start_date']} to {results['end_date']}")
    print(f"  Initial Capital: ${config.initial_capital:,.2f}")
    print(f"  Final Capital: ${results['final_capital']:,.2f}")
    print(f"  Total P&L: ${results['total_pnl']:,.2f}")
    print(f"  Total Return: {results['total_return_pct']:.2f}%")
    print()
    print(f"  Total Trades: {results['total_trades']}")
    print(f"  Winning Trades: {results['winning_trades']}")
    print(f"  Losing Trades: {results['losing_trades']}")
    print(f"  Win Rate: {results['win_rate']:.2f}%")
    print()
    print(f"  Average Trade P&L: ${results['avg_trade_pnl']:,.2f}")
    print(f"  Average Win: ${results['avg_win_amount']:,.2f}")
    print(f"  Average Loss: ${results['avg_loss_amount']:,.2f}")
    print(f"  Profit Factor: {results['profit_factor']:.2f}")
    print()
    print(f"  Sharpe Ratio: {results['sharpe_ratio']:.2f}")
    print(f"  Sortino Ratio: {results['sortino_ratio']:.2f}")
    print(f"  Calmar Ratio: {results['calmar_ratio']:.2f}")
    print(f"  Max Drawdown: {results['max_drawdown_pct']:.2f}% (${results['max_drawdown_amount']:,.2f})")
    print()
    print(f"  Average Brier Score: {results['avg_brier_score']:.4f}")
    print(f"  Average Log Loss: {results['avg_log_loss']:.4f}")
    print("=" * 80)


if __name__ == "__main__":
    print("\nKalshi Prediction Backtesting System")
    print("====================================\n")

    print("Select mode:")
    print("1. Run comparison of multiple strategies (recommended)")
    print("2. Run single custom backtest")
    print()

    try:
        choice = input("Enter choice (1 or 2): ").strip()

        if choice == "1":
            run_sample_backtests()
        elif choice == "2":
            run_custom_backtest()
        else:
            print("Invalid choice. Running comparison mode by default.")
            run_sample_backtests()

    except KeyboardInterrupt:
        print("\n\nBacktest cancelled by user.")
    except Exception as e:
        print(f"\n\nError running backtest: {e}")
        import traceback
        traceback.print_exc()
