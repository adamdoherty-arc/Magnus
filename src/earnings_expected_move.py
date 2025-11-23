"""
Calculate expected move from options prices
"""
import yfinance as yf
from datetime import datetime, timedelta
import math
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def round_to_nearest_strike(price, strike_interval=None):
    """Round price to nearest option strike"""
    if strike_interval is None:
        if price < 50:
            strike_interval = 2.5
        elif price < 100:
            strike_interval = 5
        else:
            strike_interval = 10

    return round(price / strike_interval) * strike_interval

def calculate_expected_move_from_yf(symbol, earnings_date):
    """
    Calculate expected move using Yahoo Finance IV

    Free alternative when you don't have options chain

    Args:
        symbol: Stock ticker
        earnings_date: Date of earnings (date object)

    Returns:
        Dictionary with expected move metrics or None
    """
    try:
        # Get stock data
        ticker = yf.Ticker(symbol)
        info = ticker.info
        stock_price = info.get('currentPrice') or info.get('regularMarketPrice')

        if not stock_price:
            logger.warning(f"{symbol}: Could not get stock price")
            return None

        # Get options chain for next expiration after earnings
        expirations = ticker.options

        if not expirations:
            logger.warning(f"{symbol}: No options available")
            return None

        # Find expiration after earnings
        expiration = None
        for exp in expirations:
            exp_date = datetime.strptime(exp, '%Y-%m-%d').date()
            if exp_date > earnings_date:
                expiration = exp
                break

        if not expiration:
            logger.warning(f"{symbol}: No expiration after earnings date")
            return None

        # Get options chain
        opt_chain = ticker.option_chain(expiration)

        # Find ATM options
        atm_strike = round_to_nearest_strike(stock_price)

        # Get ATM call and put
        atm_call = opt_chain.calls[opt_chain.calls['strike'] == atm_strike]
        atm_put = opt_chain.puts[opt_chain.puts['strike'] == atm_strike]

        if atm_call.empty or atm_put.empty:
            logger.warning(f"{symbol}: No ATM options at strike {atm_strike}")
            return None

        # Calculate expected move
        call_price = atm_call.iloc[0]['lastPrice']
        put_price = atm_put.iloc[0]['lastPrice']
        straddle_price = call_price + put_price
        expected_move_dollars = straddle_price * 0.85
        expected_move_pct = (expected_move_dollars / stock_price) * 100

        # Get IV
        iv = atm_call.iloc[0]['impliedVolatility']

        return {
            'symbol': symbol,
            'earnings_date': earnings_date,
            'expected_move_dollars': round(expected_move_dollars, 2),
            'expected_move_pct': round(expected_move_pct, 2),
            'pre_earnings_iv': round(iv, 4),
            'stock_price': round(stock_price, 2),
            'straddle_price': round(straddle_price, 2),
            'atm_strike': atm_strike,
            'expiration': expiration
        }

    except Exception as e:
        logger.error(f"Error calculating expected move for {symbol}: {e}")
        return None

def calculate_expected_move_from_iv(stock_price, implied_volatility, days_to_expiration=1):
    """
    Convert implied volatility to expected move

    Formula: EM = Stock_Price × IV × sqrt(DTE / 365)

    Args:
        stock_price: Current stock price
        implied_volatility: Annualized IV (e.g., 0.45 for 45%)
        days_to_expiration: Days until earnings (typically 1)

    Returns:
        Expected move in dollars
    """
    expected_move = stock_price * implied_volatility * math.sqrt(days_to_expiration / 365)
    return expected_move

def expected_move_percentage(stock_price, implied_volatility, days_to_expiration=1):
    """Calculate expected move as percentage"""
    move_dollars = calculate_expected_move_from_iv(stock_price, implied_volatility, days_to_expiration)
    return (move_dollars / stock_price) * 100

if __name__ == "__main__":
    # Test with a sample symbol
    from datetime import date
    result = calculate_expected_move_from_yf('AAPL', date.today() + timedelta(days=7))
    if result:
        print(f"Expected Move for {result['symbol']}:")
        print(f"  Stock Price: ${result['stock_price']}")
        print(f"  Expected Move: ±${result['expected_move_dollars']} (±{result['expected_move_pct']}%)")
        print(f"  Pre-Earnings IV: {result['pre_earnings_iv']}")
