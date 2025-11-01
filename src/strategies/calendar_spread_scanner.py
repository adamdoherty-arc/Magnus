"""
Calendar Spread Scanner
Scans multiple symbols for calendar spread opportunities
"""

import time
import pandas as pd
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from .calendar_spread_finder import CalendarSpreadFinder
from .calendar_spread_models import CalendarSpreadOpportunity


class CalendarSpreadScanner:
    """Scan multiple symbols for calendar spread opportunities"""

    def __init__(self, max_workers: int = 5):
        """
        Initialize scanner

        Args:
            max_workers: Maximum number of concurrent threads
        """
        self.finder = CalendarSpreadFinder()
        self.max_workers = max_workers

    def scan_watchlist(self, symbols: List[str],
                       near_dte_range: tuple = (30, 45),
                       far_dte_range: tuple = (60, 90),
                       option_type: str = 'call',
                       min_score: float = 30.0) -> Dict[str, List[CalendarSpreadOpportunity]]:
        """
        Scan a watchlist for calendar spread opportunities

        Args:
            symbols: List of stock symbols to scan
            near_dte_range: DTE range for near-term leg
            far_dte_range: DTE range for far-term leg
            option_type: 'call' or 'put'
            min_score: Minimum opportunity score to include

        Returns:
            Dictionary mapping symbols to their opportunities
        """
        results = {}
        scan_stats = {
            'total_symbols': len(symbols),
            'symbols_with_opportunities': 0,
            'total_opportunities': 0,
            'scan_time': 0,
            'errors': []
        }

        print(f"Scanning {len(symbols)} symbols for calendar spreads...")
        start_time = time.time()

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_symbol = {
                executor.submit(
                    self._scan_single_symbol,
                    symbol,
                    near_dte_range,
                    far_dte_range,
                    option_type,
                    min_score
                ): symbol
                for symbol in symbols
            }

            # Process completed tasks
            for future in as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                try:
                    opportunities = future.result(timeout=30)
                    if opportunities:
                        results[symbol] = opportunities
                        scan_stats['symbols_with_opportunities'] += 1
                        scan_stats['total_opportunities'] += len(opportunities)
                        print(f"  ✓ {symbol}: Found {len(opportunities)} opportunities")
                    else:
                        print(f"  - {symbol}: No opportunities found")
                except Exception as e:
                    scan_stats['errors'].append(f"{symbol}: {str(e)}")
                    print(f"  ✗ {symbol}: Error - {str(e)}")

        scan_stats['scan_time'] = time.time() - start_time

        # Print summary
        self._print_scan_summary(scan_stats, results)

        return results

    def _scan_single_symbol(self, symbol: str,
                           near_dte_range: tuple,
                           far_dte_range: tuple,
                           option_type: str,
                           min_score: float) -> List[CalendarSpreadOpportunity]:
        """Scan a single symbol for opportunities"""
        try:
            opportunities = self.finder.find_opportunities(
                symbol,
                near_dte_range=near_dte_range,
                far_dte_range=far_dte_range,
                option_type=option_type
            )

            # Filter by minimum score
            filtered = [opp for opp in opportunities if opp.opportunity_score >= min_score]
            return filtered

        except Exception as e:
            print(f"Error scanning {symbol}: {e}")
            return []

    def _print_scan_summary(self, stats: Dict, results: Dict):
        """Print scan summary statistics"""
        print("\n" + "="*60)
        print("SCAN SUMMARY")
        print("="*60)
        print(f"Symbols Scanned: {stats['total_symbols']}")
        print(f"Symbols with Opportunities: {stats['symbols_with_opportunities']}")
        print(f"Total Opportunities Found: {stats['total_opportunities']}")
        print(f"Scan Time: {stats['scan_time']:.2f} seconds")

        if stats['errors']:
            print(f"\nErrors: {len(stats['errors'])}")
            for error in stats['errors'][:5]:  # Show first 5 errors
                print(f"  - {error}")

        if results:
            # Find best opportunities across all symbols
            all_opportunities = []
            for symbol_opps in results.values():
                all_opportunities.extend(symbol_opps)

            all_opportunities.sort(key=lambda x: x.opportunity_score, reverse=True)

            print("\n" + "-"*60)
            print("TOP 5 OPPORTUNITIES ACROSS ALL SYMBOLS")
            print("-"*60)

            for i, opp in enumerate(all_opportunities[:5], 1):
                print(f"{i}. {opp.symbol} ${opp.near_strike:.2f}")
                print(f"   Score: {opp.opportunity_score:.1f}/100")
                print(f"   Max Profit: ${opp.max_profit:.2f} ({opp.profit_potential*100:.1f}%)")
                print(f"   Probability: {opp.probability_profit:.1f}%")
                print(f"   Net Debit: ${opp.net_debit:.2f}")

    def get_top_opportunities(self, results: Dict[str, List[CalendarSpreadOpportunity]],
                            top_n: int = 10) -> List[CalendarSpreadOpportunity]:
        """
        Get the top N opportunities across all symbols

        Args:
            results: Results from scan_watchlist
            top_n: Number of top opportunities to return

        Returns:
            List of top opportunities sorted by score
        """
        all_opportunities = []
        for symbol_opps in results.values():
            all_opportunities.extend(symbol_opps)

        # Sort by opportunity score
        all_opportunities.sort(key=lambda x: x.opportunity_score, reverse=True)

        # Re-rank
        for idx, opp in enumerate(all_opportunities[:top_n], 1):
            opp.rank = idx

        return all_opportunities[:top_n]

    def export_to_dataframe(self, results: Dict[str, List[CalendarSpreadOpportunity]]) -> pd.DataFrame:
        """
        Export scan results to a pandas DataFrame

        Args:
            results: Results from scan_watchlist

        Returns:
            DataFrame with all opportunities
        """
        data = []
        for opportunities in results.values():
            for opp in opportunities:
                data.append({
                    'Symbol': opp.symbol,
                    'Stock Price': opp.stock_price,
                    'Strike': opp.near_strike,
                    'Near DTE': opp.near_dte,
                    'Far DTE': opp.far_dte,
                    'Near Expiration': opp.near_expiration,
                    'Far Expiration': opp.far_expiration,
                    'Net Debit': opp.net_debit,
                    'Max Profit': opp.max_profit,
                    'Profit %': opp.profit_potential * 100,
                    'Probability %': opp.probability_profit,
                    'Net Theta': opp.net_theta,
                    'IV Diff %': opp.iv_differential,
                    'Liquidity Score': opp.liquidity_score,
                    'Opportunity Score': opp.opportunity_score
                })

        df = pd.DataFrame(data)
        if not df.empty:
            df = df.sort_values('Opportunity Score', ascending=False)
            df = df.reset_index(drop=True)
            df.index = df.index + 1  # Start ranking from 1

        return df