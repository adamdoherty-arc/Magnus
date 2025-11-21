"""
Stock Data Query Functions
===========================

Centralized, cached query functions for stock data.

Features:
- Connection pooling via db_connection_pool.py
- Automatic caching with appropriate TTL
- Graceful error handling (returns empty list/dict)
- Parameterized queries to prevent SQL injection
- Comprehensive docstrings with usage examples

Tables queried:
- stock_data: Main stock information table
- tradingview_watchlists: Watchlist data

Usage:
    from src.data.stock_queries import get_stock_info, get_all_stocks

    # Get single stock info
    stock = get_stock_info("AAPL")
    print(f"{stock['name']}: ${stock['current_price']}")

    # Get all active stocks
    stocks = get_all_stocks(active_only=True)
    print(f"Found {len(stocks)} active stocks")
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from psycopg2.extras import RealDictCursor

from src.xtrades_monitor.db_connection_pool import get_db_pool
from src.data.cache_manager import cache_with_ttl, CacheTier

logger = logging.getLogger(__name__)


@cache_with_ttl(CacheTier.SHORT)
def get_stock_info(symbol: str) -> Dict[str, Any]:
    """
    Get comprehensive stock information for a single symbol.

    Fetches current price, market cap, sector, 52-week range, and other key metrics.

    Args:
        symbol: Stock ticker symbol (e.g., "AAPL", "TSLA")

    Returns:
        Dictionary with stock details, or empty dict on error

    Example:
        stock = get_stock_info("AAPL")
        if stock:
            print(f"{stock['company_name']}: ${stock['current_price']}")
            print(f"Sector: {stock['sector']}, Market Cap: ${stock['market_cap']:,}")
    """
    try:
        pool = get_db_pool()
        with pool.get_cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT
                    symbol,
                    company_name,
                    current_price,
                    price_change,
                    price_change_pct,
                    day_high,
                    day_low,
                    volume,
                    avg_volume,
                    market_cap,
                    pe_ratio,
                    dividend_yield,
                    beta,
                    week_52_high,
                    week_52_low,
                    sector,
                    industry,
                    last_updated
                FROM stock_data
                WHERE UPPER(symbol) = UPPER(%s)
            """, (symbol,))

            result = cursor.fetchone()
            if result:
                return dict(result)
            else:
                logger.warning(f"Stock not found: {symbol}")
                return {}

    except Exception as e:
        logger.error(f"Error fetching stock info for {symbol}: {e}")
        return {}


@cache_with_ttl(CacheTier.MEDIUM)
def get_all_stocks(active_only: bool = True) -> List[Dict[str, Any]]:
    """
    Get all stocks from the database.

    Args:
        active_only: If True, only return stocks with current_price > 0

    Returns:
        List of stock dictionaries, or empty list on error

    Example:
        stocks = get_all_stocks(active_only=True)
        for stock in stocks:
            print(f"{stock['symbol']}: {stock['company_name']}")
    """
    try:
        pool = get_db_pool()
        with pool.get_cursor(cursor_factory=RealDictCursor) as cursor:
            query = """
                SELECT
                    symbol,
                    company_name,
                    current_price,
                    market_cap,
                    sector,
                    industry,
                    pe_ratio,
                    dividend_yield,
                    week_52_high,
                    week_52_low,
                    last_updated
                FROM stock_data
            """

            if active_only:
                query += " WHERE current_price > 0"

            query += " ORDER BY symbol"

            cursor.execute(query)
            results = cursor.fetchall()
            return [dict(row) for row in results]

    except Exception as e:
        logger.error(f"Error fetching all stocks: {e}")
        return []


@cache_with_ttl(CacheTier.MEDIUM)
def get_stocks_by_sector(sector: str) -> List[Dict[str, Any]]:
    """
    Get all stocks in a specific sector.

    Args:
        sector: Sector name (e.g., "Technology", "Healthcare", "Energy")

    Returns:
        List of stock dictionaries in the sector, or empty list on error

    Example:
        tech_stocks = get_stocks_by_sector("Technology")
        print(f"Found {len(tech_stocks)} technology stocks")
        for stock in tech_stocks[:5]:
            print(f"  {stock['symbol']}: {stock['company_name']}")
    """
    try:
        pool = get_db_pool()
        with pool.get_cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT
                    symbol,
                    company_name,
                    current_price,
                    market_cap,
                    sector,
                    industry,
                    pe_ratio,
                    dividend_yield,
                    week_52_high,
                    week_52_low
                FROM stock_data
                WHERE UPPER(sector) = UPPER(%s)
                  AND current_price > 0
                ORDER BY market_cap DESC NULLS LAST, symbol
            """, (sector,))

            results = cursor.fetchall()
            return [dict(row) for row in results]

    except Exception as e:
        logger.error(f"Error fetching stocks for sector {sector}: {e}")
        return []


@cache_with_ttl(CacheTier.MEDIUM)
def search_stocks(query: str, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Search stocks by symbol or company name.

    Case-insensitive partial matching on both symbol and company name.

    Args:
        query: Search term (e.g., "AAPL", "Apple", "tech")
        limit: Maximum number of results to return (default: 50)

    Returns:
        List of matching stock dictionaries, or empty list on error

    Example:
        # Search by symbol
        results = search_stocks("AA")
        # Returns: AAPL, AAL, AAPLB, etc.

        # Search by company name
        results = search_stocks("Apple")
        # Returns: AAPL (Apple Inc.)
    """
    try:
        pool = get_db_pool()
        with pool.get_cursor(cursor_factory=RealDictCursor) as cursor:
            search_pattern = f"%{query}%"
            cursor.execute("""
                SELECT
                    symbol,
                    company_name,
                    current_price,
                    market_cap,
                    sector,
                    industry,
                    last_updated
                FROM stock_data
                WHERE (UPPER(symbol) LIKE UPPER(%s)
                   OR UPPER(company_name) LIKE UPPER(%s))
                  AND current_price > 0
                ORDER BY
                    CASE
                        WHEN UPPER(symbol) = UPPER(%s) THEN 1
                        WHEN UPPER(symbol) LIKE UPPER(%s) || '%%' THEN 2
                        WHEN UPPER(company_name) LIKE UPPER(%s) || '%%' THEN 3
                        ELSE 4
                    END,
                    market_cap DESC NULLS LAST
                LIMIT %s
            """, (search_pattern, search_pattern, query, query, query, limit))

            results = cursor.fetchall()
            return [dict(row) for row in results]

    except Exception as e:
        logger.error(f"Error searching stocks with query '{query}': {e}")
        return []


@cache_with_ttl(CacheTier.MEDIUM)
def get_stock_price_history(symbol: str, days: int = 30) -> List[Dict[str, Any]]:
    """
    Get historical price data for a stock.

    Note: This queries the stock_data table's last_updated field and historical_prices
    table if available. If historical_prices doesn't exist, returns current price only.

    Args:
        symbol: Stock ticker symbol
        days: Number of days of history to retrieve (default: 30)

    Returns:
        List of price history dictionaries, or empty list on error

    Example:
        history = get_stock_price_history("AAPL", days=7)
        for entry in history:
            print(f"{entry['date']}: ${entry['price']}")
    """
    try:
        pool = get_db_pool()
        with pool.get_cursor(cursor_factory=RealDictCursor) as cursor:
            # Try historical_prices table first
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = 'historical_prices'
                )
            """)
            has_historical = cursor.fetchone()['exists']

            if has_historical:
                start_date = datetime.now() - timedelta(days=days)
                cursor.execute("""
                    SELECT
                        date,
                        symbol,
                        open,
                        high,
                        low,
                        close as price,
                        volume
                    FROM historical_prices
                    WHERE UPPER(symbol) = UPPER(%s)
                      AND date >= %s
                    ORDER BY date DESC
                """, (symbol, start_date))

                results = cursor.fetchall()
                return [dict(row) for row in results]
            else:
                # Fallback: return current price from stock_data
                cursor.execute("""
                    SELECT
                        last_updated as date,
                        symbol,
                        current_price as price,
                        volume
                    FROM stock_data
                    WHERE UPPER(symbol) = UPPER(%s)
                """, (symbol,))

                result = cursor.fetchone()
                if result:
                    return [dict(result)]
                else:
                    return []

    except Exception as e:
        logger.error(f"Error fetching price history for {symbol}: {e}")
        return []


@cache_with_ttl(CacheTier.MEDIUM)
def get_watchlist_stocks(watchlist_name: str) -> List[str]:
    """
    Get list of stock symbols from a TradingView watchlist.

    Args:
        watchlist_name: Name of the watchlist (e.g., "Tech Stocks", "Dividend Kings")

    Returns:
        List of stock symbols, or empty list on error

    Example:
        symbols = get_watchlist_stocks("Tech Stocks")
        print(f"Found {len(symbols)} symbols: {', '.join(symbols[:5])}")
    """
    try:
        pool = get_db_pool()
        with pool.get_cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT symbols
                FROM tradingview_watchlists
                WHERE UPPER(watchlist_name) = UPPER(%s)
            """, (watchlist_name,))

            result = cursor.fetchone()
            if result and result['symbols']:
                # symbols column is stored as text array or comma-separated
                symbols = result['symbols']
                if isinstance(symbols, str):
                    return [s.strip() for s in symbols.split(',') if s.strip()]
                elif isinstance(symbols, list):
                    return symbols
                else:
                    return []
            else:
                logger.warning(f"Watchlist not found: {watchlist_name}")
                return []

    except Exception as e:
        logger.error(f"Error fetching watchlist '{watchlist_name}': {e}")
        return []


@cache_with_ttl(CacheTier.LONG)
def get_all_sectors() -> List[str]:
    """
    Get list of all unique sectors in the database.

    Returns:
        List of sector names, or empty list on error

    Example:
        sectors = get_all_sectors()
        print(f"Available sectors: {', '.join(sectors)}")
    """
    try:
        pool = get_db_pool()
        with pool.get_cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT DISTINCT sector
                FROM stock_data
                WHERE sector IS NOT NULL
                  AND sector != ''
                  AND current_price > 0
                ORDER BY sector
            """)

            results = cursor.fetchall()
            return [row['sector'] for row in results if row['sector']]

    except Exception as e:
        logger.error(f"Error fetching sectors: {e}")
        return []


@cache_with_ttl(CacheTier.MEDIUM)
def get_stocks_by_market_cap(
    min_cap: int = 0,
    max_cap: Optional[int] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Get stocks filtered by market capitalization range.

    Args:
        min_cap: Minimum market cap in dollars (default: 0)
        max_cap: Maximum market cap in dollars (default: None for no limit)
        limit: Maximum number of results (default: 100)

    Returns:
        List of stock dictionaries, or empty list on error

    Example:
        # Large cap stocks (>$10B)
        large_caps = get_stocks_by_market_cap(min_cap=10_000_000_000, limit=50)

        # Mid cap stocks ($2B - $10B)
        mid_caps = get_stocks_by_market_cap(
            min_cap=2_000_000_000,
            max_cap=10_000_000_000
        )
    """
    try:
        pool = get_db_pool()
        with pool.get_cursor(cursor_factory=RealDictCursor) as cursor:
            if max_cap:
                cursor.execute("""
                    SELECT
                        symbol,
                        company_name,
                        current_price,
                        market_cap,
                        sector,
                        industry,
                        pe_ratio,
                        dividend_yield
                    FROM stock_data
                    WHERE market_cap >= %s
                      AND market_cap <= %s
                      AND current_price > 0
                    ORDER BY market_cap DESC
                    LIMIT %s
                """, (min_cap, max_cap, limit))
            else:
                cursor.execute("""
                    SELECT
                        symbol,
                        company_name,
                        current_price,
                        market_cap,
                        sector,
                        industry,
                        pe_ratio,
                        dividend_yield
                    FROM stock_data
                    WHERE market_cap >= %s
                      AND current_price > 0
                    ORDER BY market_cap DESC
                    LIMIT %s
                """, (min_cap, limit))

            results = cursor.fetchall()
            return [dict(row) for row in results]

    except Exception as e:
        logger.error(f"Error fetching stocks by market cap: {e}")
        return []


@cache_with_ttl(CacheTier.SHORT)
def get_stock_count() -> int:
    """
    Get total count of active stocks in database.

    Returns:
        Number of stocks with current_price > 0, or 0 on error

    Example:
        count = get_stock_count()
        print(f"Tracking {count} active stocks")
    """
    try:
        pool = get_db_pool()
        with pool.get_cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM stock_data
                WHERE current_price > 0
            """)

            result = cursor.fetchone()
            return result['count'] if result else 0

    except Exception as e:
        logger.error(f"Error counting stocks: {e}")
        return 0


# Example usage
if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("Testing Stock Query Functions")
    print("=" * 60)

    # Test 1: Get stock count
    count = get_stock_count()
    print(f"\n1. Total active stocks: {count}")

    # Test 2: Get single stock info
    stock = get_stock_info("AAPL")
    if stock:
        print(f"\n2. Stock Info for AAPL:")
        print(f"   Company: {stock.get('company_name')}")
        print(f"   Price: ${stock.get('current_price')}")
        print(f"   Sector: {stock.get('sector')}")
        print(f"   Market Cap: ${stock.get('market_cap'):,}")

    # Test 3: Search stocks
    results = search_stocks("tech", limit=5)
    print(f"\n3. Search 'tech' - found {len(results)} results:")
    for r in results[:3]:
        print(f"   {r['symbol']}: {r['company_name']}")

    # Test 4: Get all sectors
    sectors = get_all_sectors()
    print(f"\n4. Available sectors ({len(sectors)}):")
    print(f"   {', '.join(sectors[:5])}...")

    # Test 5: Get stocks by sector
    tech_stocks = get_stocks_by_sector("Technology")
    print(f"\n5. Technology sector - {len(tech_stocks)} stocks")
    for stock in tech_stocks[:3]:
        print(f"   {stock['symbol']}: {stock['company_name']}")

    print("\n" + "=" * 60)
    print("All tests completed!")
