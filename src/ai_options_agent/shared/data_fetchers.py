"""
Shared Data Fetching Functions
Provides cached database queries and yfinance fallback
"""

import streamlit as st
import yfinance as yf
from typing import Dict, List, Any, Optional
from src.tradingview_db_manager import TradingViewDBManager


@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_database_stocks() -> List[Dict[str, Any]]:
    """
    Fetch all active stocks from database

    Returns:
        List of stock dicts with symbol, company_name, price, etc.
    """
    try:
        tv_manager = TradingViewDBManager()
        conn = tv_manager.get_connection()
        cur = conn.cursor()

        # Try stock_data table first (most complete)
        cur.execute("""
            SELECT symbol, company_name, current_price, sector, market_cap,
                   week_52_high, week_52_low, last_updated
            FROM stock_data
            WHERE current_price > 0
            ORDER BY symbol
        """)

        columns = ['symbol', 'company_name', 'current_price', 'sector', 'market_cap',
                   'week_52_high', 'week_52_low', 'last_updated']
        stocks = [dict(zip(columns, row)) for row in cur.fetchall()]

        # Fallback to stocks table if stock_data is empty
        if not stocks:
            cur.execute("""
                SELECT ticker as symbol, name as company_name, price as current_price,
                       sector, market_cap, high_52week, low_52week, last_updated
                FROM stocks
                WHERE price > 0
                ORDER BY ticker
            """)
            stocks = [dict(zip(columns, row)) for row in cur.fetchall()]

        cur.close()
        conn.close()
        return stocks

    except Exception as e:
        st.error(f"Error fetching database stocks: {e}")
        return []


@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_stock_info(symbol: str) -> Optional[Dict[str, Any]]:
    """
    Fetch comprehensive stock info from database and yfinance

    Args:
        symbol: Stock ticker symbol

    Returns:
        Dict with stock info or None if not found
    """
    data = {
        'symbol': symbol.upper(),
        'name': symbol,
        'current_price': 0,
        'sector': 'Technology',
        'market_cap': 0,
        'pe_ratio': 28.5,
        'high_52week': 0,
        'low_52week': 0,
        'volume': 0
    }

    # Try database first
    try:
        tv_manager = TradingViewDBManager()
        conn = tv_manager.get_connection()
        cur = conn.cursor()

        # Try stock_data table
        cur.execute("""
            SELECT company_name, current_price, sector, market_cap,
                   week_52_high, week_52_low, pe_ratio, volume
            FROM stock_data
            WHERE symbol = %s
        """, (symbol.upper(),))

        row = cur.fetchone()
        if row:
            data['name'] = row[0] or symbol
            data['current_price'] = float(row[1]) if row[1] else 0
            data['sector'] = row[2] or 'Technology'
            data['market_cap'] = int(row[3]) if row[3] else 0
            data['high_52week'] = float(row[4]) if row[4] else 0
            data['low_52week'] = float(row[5]) if row[5] else 0
            if row[6]:
                data['pe_ratio'] = float(row[6])
            if len(row) > 7 and row[7]:
                data['volume'] = int(row[7]) if row[7] else 0

        cur.close()
        conn.close()

    except Exception as e:
        st.warning(f"Database query failed: {e}")

    # Fallback to yfinance if data is missing or critical fields are 0
    needs_fallback = (
        data['current_price'] == 0 or
        data['market_cap'] == 0 or
        (data['high_52week'] == 0 and data['low_52week'] == 0)
    )

    if needs_fallback:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period='1y')  # Get 52-week data

            # Update with real data
            data['name'] = info.get('longName', info.get('shortName', symbol))
            data['current_price'] = info.get('currentPrice', info.get('regularMarketPrice', 0))
            data['market_cap'] = info.get('marketCap', 0)
            data['pe_ratio'] = info.get('trailingPE', 28.5)
            data['sector'] = info.get('sector', 'Technology')
            
            # Get 52-week high/low from yfinance or history
            if info.get('fiftyTwoWeekHigh'):
                data['high_52week'] = info.get('fiftyTwoWeekHigh', 0)
            elif not hist.empty:
                data['high_52week'] = float(hist['High'].max())
            
            if info.get('fiftyTwoWeekLow'):
                data['low_52week'] = info.get('fiftyTwoWeekLow', 0)
            elif not hist.empty:
                data['low_52week'] = float(hist['Low'].min())
            
            # Get volume
            data['volume'] = info.get('volume', info.get('averageVolume', 0))
            
            # Validate critical data
            if data['current_price'] == 0:
                st.error(f"⚠️ Could not fetch price for {symbol}. Data may be unavailable.")
                return None

        except Exception as e:
            st.warning(f"Could not fetch yfinance data for {symbol}: {e}")
            # Return partial data if we have some from database
            if data['current_price'] > 0:
                return data
            return None

    return data if data['current_price'] > 0 else None


@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_options_suggestions(
    symbol: str,
    dte_min: int = 20,
    dte_max: int = 45,
    delta_min: float = -0.35,
    delta_max: float = -0.25
) -> List[Dict[str, Any]]:
    """
    Fetch suggested options from database

    Args:
        symbol: Stock ticker symbol
        dte_min: Minimum days to expiration
        dte_max: Maximum days to expiration
        delta_min: Minimum delta (negative for puts)
        delta_max: Maximum delta (negative for puts)

    Returns:
        List of option suggestion dicts
    """
    try:
        tv_manager = TradingViewDBManager()
        conn = tv_manager.get_connection()
        cur = conn.cursor()

        # Query stock_premiums table for PUT options
        cur.execute("""
            SELECT strike_price, expiration_date, delta, premium, implied_volatility, dte
            FROM stock_premiums
            WHERE symbol = %s
              AND strike_type = 'put'
              AND dte BETWEEN %s AND %s
              AND delta BETWEEN %s AND %s
              AND delta IS NOT NULL
            ORDER BY ABS(delta + 0.30), dte
            LIMIT 5
        """, (symbol.upper(), dte_min, dte_max, delta_min, delta_max))

        options = []
        for row in cur.fetchall():
            options.append({
                'strike': float(row[0]) if row[0] else 0,
                'expiration': row[1],
                'delta': float(row[2]) if row[2] else -0.30,
                'premium': float(row[3]) if row[3] else 0,
                'iv': float(row[4]) if row[4] else 0.35,
                'dte': int(row[5]) if row[5] else 30
            })

        cur.close()
        conn.close()
        return options

    except Exception as e:
        # Silently fail - options suggestions are optional
        return []


@st.cache_data(ttl=300)  # Cache for 5 minutes
def calculate_iv_for_stock(symbol: str) -> float:
    """
    Calculate implied volatility from options data

    Args:
        symbol: Stock ticker symbol

    Returns:
        Average IV as decimal (0.35 = 35%) or 0.35 as fallback
    """
    try:
        tv_manager = TradingViewDBManager()
        conn = tv_manager.get_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT AVG(implied_volatility) as avg_iv
            FROM stock_premiums
            WHERE symbol = %s
              AND dte BETWEEN 20 AND 45
              AND implied_volatility IS NOT NULL
              AND implied_volatility > 0
        """, (symbol.upper(),))

        row = cur.fetchone()
        cur.close()
        conn.close()

        if row and row[0]:
            iv_value = float(row[0])
            # Normalize IV: if > 1.0, assume it's stored as percentage (73.49), convert to decimal (0.7349)
            # If <= 1.0, assume it's already decimal (0.35)
            if iv_value > 1.0:
                iv_value = iv_value / 100.0
            # Clamp to reasonable range (0.01 to 5.0 = 1% to 500%)
            if iv_value > 5.0:
                iv_value = 5.0
            elif iv_value < 0.01:
                iv_value = 0.01
            return iv_value
        else:
            return 0.35  # Default fallback (35%)

    except Exception as e:
        return 0.35  # Default fallback
