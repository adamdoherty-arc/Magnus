"""
Utility functions for safe yfinance API calls with robust error handling.

This module provides wrapper functions around yfinance to gracefully handle:
- Delisted symbols
- Symbols with no data
- API timeouts and failures
- Invalid ticker symbols
- JSON parsing errors

All functions return None or empty data structures on failure, with proper logging.
"""

import logging
import yfinance as yf
from typing import Optional, Dict, Any, List
from datetime import datetime
import pandas as pd

logger = logging.getLogger(__name__)

# Known delisted or problematic symbols - can be extended
KNOWN_DELISTED_SYMBOLS = {'BMNR', 'PLUG', 'BBAI'}  # Add more as discovered


class DelistedSymbolError(Exception):
    """Raised when a symbol is known to be delisted or unavailable."""
    pass


def is_symbol_delisted(symbol: str) -> bool:
    """
    Check if a symbol is in the known delisted symbols list.

    Args:
        symbol: Stock ticker symbol

    Returns:
        True if symbol is known to be delisted
    """
    return symbol.upper() in KNOWN_DELISTED_SYMBOLS


def safe_get_ticker(symbol: str, suppress_warnings: bool = False) -> Optional[yf.Ticker]:
    """
    Safely create a yfinance Ticker object with error handling.

    Args:
        symbol: Stock ticker symbol
        suppress_warnings: If True, only log errors, not warnings

    Returns:
        yf.Ticker object or None if creation fails
    """
    try:
        # Check if symbol is known to be delisted
        if is_symbol_delisted(symbol):
            if not suppress_warnings:
                logger.info(f"Symbol {symbol} is known to be delisted - skipping")
            return None

        ticker = yf.Ticker(symbol)
        return ticker

    except Exception as e:
        logger.error(f"Failed to create ticker for {symbol}: {str(e)}")
        return None


def safe_get_history(
    symbol: str,
    period: str = "1d",
    retry_periods: Optional[List[str]] = None,
    suppress_warnings: bool = False
) -> Optional[pd.DataFrame]:
    """
    Safely fetch price history with fallback periods.

    Args:
        symbol: Stock ticker symbol
        period: Time period (1d, 5d, 1mo, etc.)
        retry_periods: List of fallback periods to try if main period fails
        suppress_warnings: If True, only log errors

    Returns:
        DataFrame with price history or None if all attempts fail
    """
    if is_symbol_delisted(symbol):
        if not suppress_warnings:
            logger.info(f"Symbol {symbol} is known to be delisted")
        return None

    ticker = safe_get_ticker(symbol, suppress_warnings=True)
    if ticker is None:
        return None

    periods_to_try = [period]
    if retry_periods:
        periods_to_try.extend(retry_periods)

    for period_attempt in periods_to_try:
        try:
            hist = ticker.history(period=period_attempt)

            if not hist.empty:
                return hist
            else:
                if not suppress_warnings:
                    logger.warning(f"No price data for {symbol} (period={period_attempt}) - may be delisted")

        except ValueError as e:
            # Expecting value errors are common for delisted stocks
            if "Expecting value" in str(e):
                if not suppress_warnings:
                    logger.warning(f"Symbol {symbol} returned empty JSON - likely delisted")
                KNOWN_DELISTED_SYMBOLS.add(symbol.upper())
                return None
            else:
                logger.error(f"ValueError fetching history for {symbol}: {str(e)}")

        except Exception as e:
            logger.error(f"Error fetching history for {symbol} (period={period_attempt}): {str(e)}")

    # All attempts failed
    if not suppress_warnings:
        logger.warning(f"All attempts to fetch history for {symbol} failed")
    return None


def safe_get_current_price(
    symbol: str,
    fallback_to_previous: bool = True,
    suppress_warnings: bool = False
) -> Optional[float]:
    """
    Safely fetch current stock price with multiple fallback methods.

    Args:
        symbol: Stock ticker symbol
        fallback_to_previous: If True, try to get previous close if current fails
        suppress_warnings: If True, only log errors

    Returns:
        Current price as float or None if unavailable
    """
    if is_symbol_delisted(symbol):
        if not suppress_warnings:
            logger.info(f"Symbol {symbol} is known to be delisted")
        return None

    ticker = safe_get_ticker(symbol, suppress_warnings=True)
    if ticker is None:
        return None

    try:
        # Method 1: Try to get from info
        info = ticker.info
        price = info.get('currentPrice') or info.get('regularMarketPrice')

        if price and price > 0:
            return float(price)

        # Method 2: Try to get from history
        hist = safe_get_history(symbol, period="1d", retry_periods=["5d"], suppress_warnings=True)

        if hist is not None and not hist.empty:
            if 'Close' in hist.columns:
                price = hist['Close'].iloc[-1]
                if price > 0:
                    return float(price)

        if not suppress_warnings:
            logger.warning(f"No valid price data found for {symbol}")
        return None

    except Exception as e:
        logger.error(f"Error fetching current price for {symbol}: {str(e)}")
        return None


def safe_get_info(
    symbol: str,
    suppress_warnings: bool = False
) -> Dict[str, Any]:
    """
    Safely fetch ticker info with error handling.

    Args:
        symbol: Stock ticker symbol
        suppress_warnings: If True, only log errors

    Returns:
        Dictionary with ticker info or empty dict if unavailable
    """
    if is_symbol_delisted(symbol):
        if not suppress_warnings:
            logger.info(f"Symbol {symbol} is known to be delisted")
        return {}

    ticker = safe_get_ticker(symbol, suppress_warnings=True)
    if ticker is None:
        return {}

    try:
        info = ticker.info

        # Check if info is empty or has minimal data
        if not info or len(info) < 3:
            if not suppress_warnings:
                logger.warning(f"Minimal or no info data for {symbol} - may be delisted")
            KNOWN_DELISTED_SYMBOLS.add(symbol.upper())
            return {}

        return info

    except ValueError as e:
        if "Expecting value" in str(e):
            if not suppress_warnings:
                logger.warning(f"Symbol {symbol} returned empty JSON - likely delisted")
            KNOWN_DELISTED_SYMBOLS.add(symbol.upper())
        else:
            logger.error(f"ValueError fetching info for {symbol}: {str(e)}")
        return {}

    except Exception as e:
        logger.error(f"Error fetching info for {symbol}: {str(e)}")
        return {}


def safe_get_options_expirations(
    symbol: str,
    suppress_warnings: bool = False
) -> List[str]:
    """
    Safely fetch available options expiration dates.

    Args:
        symbol: Stock ticker symbol
        suppress_warnings: If True, only log errors

    Returns:
        List of expiration dates as strings, or empty list if unavailable
    """
    if is_symbol_delisted(symbol):
        if not suppress_warnings:
            logger.info(f"Symbol {symbol} is known to be delisted")
        return []

    ticker = safe_get_ticker(symbol, suppress_warnings=True)
    if ticker is None:
        return []

    try:
        expirations = ticker.options

        if not expirations:
            if not suppress_warnings:
                logger.info(f"No options available for {symbol}")
            return []

        return list(expirations)

    except Exception as e:
        if not suppress_warnings:
            logger.error(f"Error fetching options expirations for {symbol}: {str(e)}")
        return []


def safe_get_option_chain(
    symbol: str,
    expiration: str,
    suppress_warnings: bool = False
) -> Optional[Any]:
    """
    Safely fetch options chain for a specific expiration.

    Args:
        symbol: Stock ticker symbol
        expiration: Expiration date string (YYYY-MM-DD format)
        suppress_warnings: If True, only log errors

    Returns:
        Options chain object or None if unavailable
    """
    if is_symbol_delisted(symbol):
        if not suppress_warnings:
            logger.info(f"Symbol {symbol} is known to be delisted")
        return None

    ticker = safe_get_ticker(symbol, suppress_warnings=True)
    if ticker is None:
        return None

    try:
        option_chain = ticker.option_chain(expiration)

        if option_chain is None:
            if not suppress_warnings:
                logger.warning(f"No option chain data for {symbol} expiring {expiration}")
            return None

        return option_chain

    except Exception as e:
        if not suppress_warnings:
            logger.error(f"Error fetching option chain for {symbol} ({expiration}): {str(e)}")
        return None


def get_delisted_symbols() -> set:
    """
    Get the current set of known delisted symbols.

    Returns:
        Set of delisted symbol strings
    """
    return KNOWN_DELISTED_SYMBOLS.copy()


def add_delisted_symbol(symbol: str) -> None:
    """
    Add a symbol to the delisted symbols list.

    Args:
        symbol: Stock ticker symbol to mark as delisted
    """
    KNOWN_DELISTED_SYMBOLS.add(symbol.upper())
    logger.info(f"Added {symbol} to delisted symbols list")


def remove_delisted_symbol(symbol: str) -> None:
    """
    Remove a symbol from the delisted symbols list.

    Args:
        symbol: Stock ticker symbol to remove from delisted list
    """
    KNOWN_DELISTED_SYMBOLS.discard(symbol.upper())
    logger.info(f"Removed {symbol} from delisted symbols list")
