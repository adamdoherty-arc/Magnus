"""
Options Data Query Functions
=============================

Centralized, cached query functions for options and premium data.

Features:
- Connection pooling via db_connection_pool.py
- Automatic caching with appropriate TTL
- Graceful error handling (returns empty list/dict)
- Parameterized queries to prevent SQL injection
- Comprehensive docstrings with usage examples

Tables queried:
- stock_premiums: Options pricing and Greeks data

Usage:
    from src.data.options_queries import get_options_chain, get_premium_opportunities

    # Get options chain
    chain = get_options_chain("AAPL", dte_range=(20, 45), delta_range=(-0.35, -0.25))

    # Find CSP opportunities
    opportunities = get_premium_opportunities({
        'min_premium_pct': 1.0,
        'min_annual_return': 15.0
    })
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from psycopg2.extras import RealDictCursor

from src.xtrades_monitor.db_connection_pool import get_db_pool
from src.data.cache_manager import cache_with_ttl, CacheTier

logger = logging.getLogger(__name__)


@cache_with_ttl(CacheTier.SHORT)
def get_options_chain(
    symbol: str,
    dte_range: Tuple[int, int] = (20, 45),
    delta_range: Tuple[float, float] = (-0.50, -0.20)
) -> List[Dict[str, Any]]:
    """
    Get options chain for a symbol with specified filters.

    Note: This database contains only PUT options for cash-secured put strategies.

    Args:
        symbol: Stock ticker symbol
        dte_range: (min_dte, max_dte) tuple for days to expiration
        delta_range: (min_delta, max_delta) tuple for option delta

    Returns:
        List of option dictionaries, or empty list on error

    Example:
        # Get PUT options for CSP strategy
        chain = get_options_chain(
            "AAPL",
            dte_range=(20, 45),
            delta_range=(-0.35, -0.25)
        )
        for opt in chain:
            print(f"Strike ${opt['strike_price']}: ${opt['premium']} premium")
    """
    try:
        pool = get_db_pool()
        with pool.get_cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT
                    id,
                    symbol,
                    expiration_date,
                    dte,
                    strike_type,
                    strike_price,
                    bid,
                    ask,
                    mid,
                    premium,
                    premium_pct,
                    monthly_return,
                    annual_return,
                    implied_volatility,
                    volume,
                    open_interest,
                    delta,
                    prob_profit,
                    last_updated
                FROM stock_premiums
                WHERE UPPER(symbol) = UPPER(%s)
                  AND dte BETWEEN %s AND %s
                  AND delta BETWEEN %s AND %s
                  AND delta IS NOT NULL
                  AND premium > 0
                ORDER BY expiration_date, ABS(delta - %s)
            """, (
                symbol,
                dte_range[0],
                dte_range[1],
                delta_range[0],
                delta_range[1],
                (delta_range[0] + delta_range[1]) / 2  # Sort by closest to middle delta
            ))

            results = cursor.fetchall()
            return [dict(row) for row in results]

    except Exception as e:
        logger.error(f"Error fetching options chain for {symbol}: {e}")
        return []


@cache_with_ttl(CacheTier.MEDIUM)
def get_premium_opportunities(filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Find high-quality CSP (Cash-Secured Put) opportunities based on filters.

    Args:
        filters: Dictionary of filter criteria:
            - min_premium_pct: Minimum premium as % of strike (default: 1.0)
            - max_premium_pct: Maximum premium as % of strike (default: None)
            - min_annual_return: Minimum annualized return % (default: 15.0)
            - min_delta: Minimum delta (default: -0.40)
            - max_delta: Maximum delta (default: -0.20)
            - min_dte: Minimum days to expiration (default: 20)
            - max_dte: Maximum days to expiration (default: 45)
            - min_iv: Minimum implied volatility (default: None)
            - max_iv: Maximum implied volatility (default: None)
            - min_volume: Minimum option volume (default: 10)
            - min_open_interest: Minimum open interest (default: 100)
            - limit: Max number of results (default: 100)

    Returns:
        List of opportunity dictionaries sorted by annual return, or empty list on error

    Example:
        # Find premium CSP opportunities
        opportunities = get_premium_opportunities({
            'min_premium_pct': 1.5,
            'min_annual_return': 20.0,
            'min_delta': -0.35,
            'max_delta': -0.25,
            'min_dte': 25,
            'max_dte': 40
        })

        for opp in opportunities[:10]:
            print(f"{opp['symbol']} ${opp['strike_price']}: {opp['annual_return']:.1f}% annual")
    """
    # Default filters
    default_filters = {
        'min_premium_pct': 1.0,
        'max_premium_pct': None,
        'min_annual_return': 15.0,
        'min_delta': -0.40,
        'max_delta': -0.20,
        'min_dte': 20,
        'max_dte': 45,
        'min_iv': None,
        'max_iv': None,
        'min_volume': 10,
        'min_open_interest': 100,
        'limit': 100
    }

    # Merge user filters with defaults
    if filters:
        default_filters.update(filters)
    filters = default_filters

    try:
        pool = get_db_pool()
        with pool.get_cursor(cursor_factory=RealDictCursor) as cursor:
            # Build dynamic query based on filters
            query = """
                SELECT
                    sp.symbol,
                    sp.expiration_date,
                    sp.dte,
                    sp.strike_price,
                    sp.premium,
                    sp.premium_pct,
                    sp.monthly_return,
                    sp.annual_return,
                    sp.implied_volatility,
                    sp.delta,
                    sp.prob_profit,
                    sp.volume,
                    sp.open_interest,
                    sp.bid,
                    sp.ask,
                    sd.company_name,
                    sd.current_price,
                    sd.sector,
                    sd.market_cap
                FROM stock_premiums sp
                JOIN stock_data sd ON UPPER(sp.symbol) = UPPER(sd.symbol)
                WHERE sp.premium_pct >= %s
                  AND sp.annual_return >= %s
                  AND sp.delta BETWEEN %s AND %s
                  AND sp.dte BETWEEN %s AND %s
                  AND sp.volume >= %s
                  AND sp.open_interest >= %s
                  AND sp.premium > 0
                  AND sd.current_price > 0
                  AND sp.strike_price < sd.current_price
            """

            params = [
                filters['min_premium_pct'],
                filters['min_annual_return'],
                filters['min_delta'],
                filters['max_delta'],
                filters['min_dte'],
                filters['max_dte'],
                filters['min_volume'],
                filters['min_open_interest']
            ]

            # Optional filters
            if filters['max_premium_pct']:
                query += " AND sp.premium_pct <= %s"
                params.append(filters['max_premium_pct'])

            if filters['min_iv']:
                query += " AND sp.implied_volatility >= %s"
                params.append(filters['min_iv'])

            if filters['max_iv']:
                query += " AND sp.implied_volatility <= %s"
                params.append(filters['max_iv'])

            # Order and limit
            query += """
                ORDER BY sp.annual_return DESC, sp.premium_pct DESC
                LIMIT %s
            """
            params.append(filters['limit'])

            cursor.execute(query, params)
            results = cursor.fetchall()
            return [dict(row) for row in results]

    except Exception as e:
        logger.error(f"Error fetching premium opportunities: {e}")
        return []


@cache_with_ttl(CacheTier.SHORT)
def get_options_by_strike(
    symbol: str,
    strike: float
) -> List[Dict[str, Any]]:
    """
    Get all options for a specific strike price.

    Note: This database contains only PUT options for cash-secured put strategies.

    Args:
        symbol: Stock ticker symbol
        strike: Strike price

    Returns:
        List of option dictionaries for the strike, or empty list on error

    Example:
        # Get all PUT options at $150 strike
        options = get_options_by_strike("AAPL", 150.0)
        for opt in options:
            print(f"Exp {opt['expiration_date']}: ${opt['premium']} ({opt['dte']} DTE)")
    """
    try:
        pool = get_db_pool()
        with pool.get_cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT
                    symbol,
                    expiration_date,
                    dte,
                    strike_type,
                    strike_price,
                    bid,
                    ask,
                    mid,
                    premium,
                    premium_pct,
                    monthly_return,
                    annual_return,
                    implied_volatility,
                    volume,
                    open_interest,
                    delta,
                    prob_profit,
                    last_updated
                FROM stock_premiums
                WHERE UPPER(symbol) = UPPER(%s)
                  AND strike_price = %s
                  AND premium > 0
                ORDER BY expiration_date
            """, (symbol, strike))

            results = cursor.fetchall()
            return [dict(row) for row in results]

    except Exception as e:
        logger.error(f"Error fetching options for {symbol} at strike ${strike}: {e}")
        return []


@cache_with_ttl(CacheTier.MEDIUM)
def get_historical_premiums(symbol: str, days: int = 30) -> List[Dict[str, Any]]:
    """
    Get historical premium data for a symbol.

    Note: Returns data from stock_premiums table over the specified time range.
    The data reflects historical snapshots, not real-time tick data.

    Args:
        symbol: Stock ticker symbol
        days: Number of days of history (default: 30)

    Returns:
        List of historical premium dictionaries, or empty list on error

    Example:
        # Get 30 days of premium history
        history = get_historical_premiums("AAPL", days=30)
        for record in history[-5:]:  # Last 5 records
            print(f"{record['last_updated']}: ${record['premium']} premium")
    """
    try:
        pool = get_db_pool()
        with pool.get_cursor(cursor_factory=RealDictCursor) as cursor:
            start_date = datetime.now() - timedelta(days=days)
            cursor.execute("""
                SELECT
                    symbol,
                    expiration_date,
                    dte,
                    strike_type,
                    strike_price,
                    premium,
                    premium_pct,
                    implied_volatility,
                    delta,
                    last_updated
                FROM stock_premiums
                WHERE UPPER(symbol) = UPPER(%s)
                  AND last_updated >= %s
                ORDER BY last_updated DESC, dte
            """, (symbol, start_date))

            results = cursor.fetchall()
            return [dict(row) for row in results]

    except Exception as e:
        logger.error(f"Error fetching historical premiums for {symbol}: {e}")
        return []


@cache_with_ttl(CacheTier.MEDIUM)
def get_high_iv_stocks(min_iv: float = 0.30, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Get stocks with high implied volatility.

    Returns stocks with average IV above the specified threshold,
    which typically offer higher premiums for option selling strategies.

    Args:
        min_iv: Minimum average implied volatility (default: 0.30 = 30%)
        limit: Maximum number of results (default: 50)

    Returns:
        List of high IV stock dictionaries, or empty list on error

    Example:
        # Find stocks with IV > 40%
        high_iv = get_high_iv_stocks(min_iv=0.40, limit=25)
        for stock in high_iv:
            print(f"{stock['symbol']}: {stock['avg_iv']:.1%} IV, ${stock['avg_premium']:.2f} avg premium")
    """
    try:
        pool = get_db_pool()
        with pool.get_cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT
                    sp.symbol,
                    sd.company_name,
                    sd.current_price,
                    sd.sector,
                    sd.market_cap,
                    AVG(sp.implied_volatility) as avg_iv,
                    AVG(sp.premium) as avg_premium,
                    AVG(sp.premium_pct) as avg_premium_pct,
                    AVG(sp.annual_return) as avg_annual_return,
                    COUNT(*) as option_count
                FROM stock_premiums sp
                JOIN stock_data sd ON UPPER(sp.symbol) = UPPER(sd.symbol)
                WHERE sp.strike_type = 'put'
                  AND sp.dte BETWEEN 20 AND 45
                  AND sp.implied_volatility IS NOT NULL
                  AND sp.implied_volatility > 0
                  AND sd.current_price > 0
                GROUP BY sp.symbol, sd.company_name, sd.current_price, sd.sector, sd.market_cap
                HAVING AVG(sp.implied_volatility) >= %s
                ORDER BY AVG(sp.implied_volatility) DESC
                LIMIT %s
            """, (min_iv, limit))

            results = cursor.fetchall()
            return [dict(row) for row in results]

    except Exception as e:
        logger.error(f"Error fetching high IV stocks: {e}")
        return []


def calculate_expected_return(premium: float, strike: float, dte: int) -> Dict[str, float]:
    """
    Calculate expected return metrics for an option position.

    This is a pure calculation function (not a database query).

    Args:
        premium: Option premium received
        strike: Strike price
        dte: Days to expiration

    Returns:
        Dictionary with return calculations

    Example:
        returns = calculate_expected_return(premium=2.50, strike=150.0, dte=30)
        print(f"Premium %: {returns['premium_pct']:.2f}%")
        print(f"Annual Return: {returns['annual_return']:.1f}%")
        print(f"Return per Day: {returns['daily_return']:.3f}%")
    """
    try:
        if strike <= 0 or dte <= 0:
            return {
                'premium': premium,
                'strike': strike,
                'dte': dte,
                'premium_pct': 0.0,
                'monthly_return': 0.0,
                'annual_return': 0.0,
                'daily_return': 0.0,
                'capital_required': strike * 100,  # Assuming 1 contract
                'max_profit': premium * 100,
                'break_even': strike - premium
            }

        premium_pct = (premium / strike) * 100
        monthly_return = premium_pct * (30 / dte)
        annual_return = premium_pct * (365 / dte)
        daily_return = premium_pct / dte

        return {
            'premium': premium,
            'strike': strike,
            'dte': dte,
            'premium_pct': round(premium_pct, 2),
            'monthly_return': round(monthly_return, 2),
            'annual_return': round(annual_return, 2),
            'daily_return': round(daily_return, 3),
            'capital_required': strike * 100,
            'max_profit': premium * 100,
            'break_even': round(strike - premium, 2)
        }

    except Exception as e:
        logger.error(f"Error calculating expected return: {e}")
        return {}


@cache_with_ttl(CacheTier.MEDIUM)
def get_options_summary_by_symbol(symbol: str) -> Dict[str, Any]:
    """
    Get aggregate statistics for all options of a symbol.

    Args:
        symbol: Stock ticker symbol

    Returns:
        Dictionary with summary statistics, or empty dict on error

    Example:
        summary = get_options_summary_by_symbol("AAPL")
        print(f"Average IV: {summary['avg_iv']:.1%}")
        print(f"Total options tracked: {summary['total_options']}")
    """
    try:
        pool = get_db_pool()
        with pool.get_cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT
                    symbol,
                    COUNT(*) as total_options,
                    COUNT(DISTINCT expiration_date) as expiration_dates,
                    AVG(implied_volatility) as avg_iv,
                    AVG(premium) as avg_premium,
                    AVG(premium_pct) as avg_premium_pct,
                    AVG(annual_return) as avg_annual_return,
                    MIN(dte) as min_dte,
                    MAX(dte) as max_dte,
                    SUM(volume) as total_volume,
                    SUM(open_interest) as total_open_interest
                FROM stock_premiums
                WHERE UPPER(symbol) = UPPER(%s)
                  AND premium > 0
            """, (symbol,))

            result = cursor.fetchone()
            return dict(result) if result else {}

    except Exception as e:
        logger.error(f"Error fetching options summary for {symbol}: {e}")
        return {}


@cache_with_ttl(CacheTier.MEDIUM)
def get_best_strikes_for_csp(
    symbol: str,
    dte_target: int = 30,
    dte_tolerance: int = 5
) -> List[Dict[str, Any]]:
    """
    Get the best strike prices for CSP strategy on a symbol.

    Finds optimal strikes around the target DTE with good premium/risk balance.

    Args:
        symbol: Stock ticker symbol
        dte_target: Target days to expiration (default: 30)
        dte_tolerance: +/- tolerance for DTE (default: 5)

    Returns:
        List of optimal strike dictionaries, or empty list on error

    Example:
        # Find best 30-day CSP strikes
        best_strikes = get_best_strikes_for_csp("AAPL", dte_target=30)
        for strike in best_strikes[:5]:
            print(f"Strike ${strike['strike_price']}: {strike['annual_return']:.1f}% annual")
    """
    try:
        pool = get_db_pool()
        with pool.get_cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT
                    sp.symbol,
                    sp.strike_price,
                    sp.expiration_date,
                    sp.dte,
                    sp.premium,
                    sp.premium_pct,
                    sp.annual_return,
                    sp.delta,
                    sp.prob_profit,
                    sp.implied_volatility,
                    sp.volume,
                    sp.open_interest,
                    sd.current_price
                FROM stock_premiums sp
                JOIN stock_data sd ON UPPER(sp.symbol) = UPPER(sd.symbol)
                WHERE UPPER(sp.symbol) = UPPER(%s)
                  AND sp.strike_type = 'put'
                  AND sp.dte BETWEEN %s AND %s
                  AND sp.delta BETWEEN -0.40 AND -0.20
                  AND sp.premium > 0
                  AND sp.volume >= 10
                  AND sp.open_interest >= 50
                  AND sp.strike_price < sd.current_price
                ORDER BY
                    ABS(sp.dte - %s),
                    sp.annual_return DESC,
                    sp.premium_pct DESC
                LIMIT 10
            """, (
                symbol,
                dte_target - dte_tolerance,
                dte_target + dte_tolerance,
                dte_target
            ))

            results = cursor.fetchall()
            return [dict(row) for row in results]

    except Exception as e:
        logger.error(f"Error fetching best CSP strikes for {symbol}: {e}")
        return []


# Example usage
if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("Testing Options Query Functions")
    print("=" * 60)

    # Test 1: Get options chain
    chain = get_options_chain("AAPL", dte_range=(20, 45), delta_range=(-0.35, -0.25))
    print(f"\n1. Options chain for AAPL: {len(chain)} options")
    if chain:
        opt = chain[0]
        print(f"   First option: ${opt['strike_price']} strike, ${opt['premium']} premium")
        print(f"   Delta: {opt['delta']}, DTE: {opt['dte']}")

    # Test 2: Find premium opportunities
    opportunities = get_premium_opportunities({
        'min_premium_pct': 1.5,
        'min_annual_return': 20.0,
        'limit': 5
    })
    print(f"\n2. Premium opportunities: {len(opportunities)}")
    for opp in opportunities[:3]:
        print(f"   {opp['symbol']} ${opp['strike_price']}: {opp['annual_return']:.1f}% annual")

    # Test 3: Calculate expected return
    returns = calculate_expected_return(premium=2.50, strike=150.0, dte=30)
    print(f"\n3. Expected return calculation:")
    print(f"   Premium %: {returns['premium_pct']:.2f}%")
    print(f"   Annual Return: {returns['annual_return']:.1f}%")
    print(f"   Break-even: ${returns['break_even']}")

    # Test 4: Get high IV stocks
    high_iv = get_high_iv_stocks(min_iv=0.35, limit=5)
    print(f"\n4. High IV stocks: {len(high_iv)}")
    for stock in high_iv[:3]:
        print(f"   {stock['symbol']}: {stock['avg_iv']:.1%} IV")

    # Test 5: Get options summary
    summary = get_options_summary_by_symbol("AAPL")
    if summary:
        print(f"\n5. Options summary for AAPL:")
        print(f"   Total options: {summary.get('total_options', 0)}")
        print(f"   Average IV: {summary.get('avg_iv', 0):.1%}")
        print(f"   Average premium: ${summary.get('avg_premium', 0):.2f}")

    print("\n" + "=" * 60)
    print("All tests completed!")
