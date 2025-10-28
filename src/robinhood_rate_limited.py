"""Robinhood Integration with Rate Limiting to avoid 429 errors"""

import robin_stocks.robinhood as rh
import os
from typing import Dict, List, Any
from datetime import datetime
import time
from pathlib import Path
import pickle

# Rate limiting settings
RATE_LIMIT_DELAY = 0.5  # Delay between API calls in seconds
LAST_CALL_TIME = 0

def rate_limit():
    """Simple rate limiting to avoid 429 errors"""
    global LAST_CALL_TIME
    current_time = time.time()
    time_since_last = current_time - LAST_CALL_TIME

    if time_since_last < RATE_LIMIT_DELAY:
        time.sleep(RATE_LIMIT_DELAY - time_since_last)

    LAST_CALL_TIME = time.time()

def login_robinhood(username=None, password=None, expiresIn=86400):
    """Simple login to Robinhood with session caching"""
    username = username or os.getenv('ROBINHOOD_USERNAME')
    password = password or os.getenv('ROBINHOOD_PASSWORD')

    if not username or not password:
        return False

    try:
        # First try to use cached session
        pickle_path = Path.home() / '.robinhood_token.pickle'

        # Try to load existing session
        if pickle_path.exists():
            try:
                with open(pickle_path, 'rb') as f:
                    login_data = pickle.load(f)
                    # Set the authentication token
                    rh.authentication.set_login_state(True)

                    # Verify the session is still valid
                    test = rh.profiles.load_account_profile()
                    if test:
                        print("Using cached session - no MFA needed!")
                        return True
                    else:
                        print("Cached session expired, need fresh login")
                        os.remove(pickle_path)
            except Exception as e:
                print(f"Cache invalid: {str(e)[:50]}, clearing cache...")
                if pickle_path.exists():
                    os.remove(pickle_path)

        # If no cached session, do fresh login
        login = rh.authentication.login(
            username=username,
            password=password,
            expiresIn=expiresIn,
            scope='internal',
            store_session=True
        )

        # Save session for next time
        if login:
            with open(pickle_path, 'wb') as f:
                pickle.dump(login, f)
            print("Login successful! Session saved for next time.")
            return True
        return False

    except Exception as e:
        print(f"Login error: {e}")
        return False

def get_account_summary():
    """Get account summary with rate limiting"""
    try:
        rate_limit()
        profile = rh.profiles.load_account_profile()

        rate_limit()
        portfolio = rh.profiles.load_portfolio_profile()

        return {
            'buying_power': float(profile.get('buying_power', 0)) if profile else 0,
            'cash': float(profile.get('cash', 0)) if profile else 0,
            'portfolio_value': float(portfolio.get('market_value', 0)) if portfolio else 0,
            'total_return': float(portfolio.get('total_return_today', 0)) if portfolio else 0,
            'day_trades': profile.get('day_trade_count', 0) if profile else 0
        }
    except Exception as e:
        print(f"Error getting account: {e}")
        return {}

def get_positions():
    """Get all positions with rate limiting"""
    try:
        positions = []

        rate_limit()
        stocks = rh.account.get_open_stock_positions()

        if not stocks:
            return []

        for stock in stocks:
            if float(stock.get('quantity', 0)) > 0:
                rate_limit()  # Rate limit before each API call

                # Get symbol from instrument URL
                instrument_data = rh.stocks.get_instrument_by_url(stock['instrument'])
                symbol = instrument_data['symbol'] if instrument_data else 'Unknown'

                # Get current price with rate limiting
                rate_limit()
                quote = rh.stocks.get_stock_quote_by_symbol(symbol)
                current_price = float(quote['last_trade_price']) if quote else 0

                positions.append({
                    'type': 'stock',
                    'symbol': symbol,
                    'quantity': float(stock['quantity']),
                    'avg_cost': float(stock.get('average_buy_price', 0)),
                    'current_price': current_price,
                    'market_value': current_price * float(stock['quantity']),
                    'pnl': (current_price - float(stock.get('average_buy_price', 0))) * float(stock['quantity'])
                })

        return positions
    except Exception as e:
        print(f"Error getting positions: {e}")
        return []

def get_options():
    """Get option positions with rate limiting"""
    try:
        options = []

        rate_limit()
        option_positions = rh.options.get_open_option_positions()

        if not option_positions:
            return []

        for opt in option_positions:
            # Check if opt is a dict (sometimes API returns list)
            if not isinstance(opt, dict):
                continue
            if float(opt.get('quantity', 0)) != 0:
                # Get option details with rate limiting
                option_id = opt.get('option_id')
                if option_id:
                    rate_limit()
                    market_data = rh.options.get_option_market_data_by_id(option_id)

                    if market_data:
                        options.append({
                            'type': 'option',
                            'symbol': opt.get('chain_symbol', 'Unknown'),
                            'option_type': opt.get('type', 'unknown'),
                            'quantity': abs(float(opt.get('quantity', 0))),
                            'side': 'short' if float(opt.get('quantity', 0)) < 0 else 'long',
                            'strike': float(market_data.get('strike_price', 0)),
                            'expiration': market_data.get('expiration_date', ''),
                            'avg_price': float(opt.get('average_price', 0)) / 100,
                            'current_price': float(market_data.get('mark_price', 0))
                        })

        return options
    except Exception as e:
        print(f"Error getting options: {e}")
        return []

def identify_wheel_positions(stocks, options):
    """Identify wheel strategy positions"""
    wheel_positions = []

    # Find stocks eligible for covered calls (100+ shares)
    if stocks:
        for stock in stocks:
            if stock.get('quantity', 0) >= 100:
                wheel_positions.append({
                    'strategy': 'Potential CC',
                    'symbol': stock['symbol'],
                    'shares': stock['quantity'],
                    'contracts_available': int(stock['quantity'] / 100),
                    'cost_basis': stock.get('avg_cost', 0),
                    'current_price': stock.get('current_price', 0),
                    'unrealized_pnl': stock.get('pnl', 0)
                })

    # Find cash-secured puts
    if options:
        for opt in options:
            if opt.get('option_type') == 'put' and opt.get('side') == 'short':
                try:
                    days_to_expiry = (datetime.strptime(opt['expiration'], '%Y-%m-%d') - datetime.now()).days
                except:
                    days_to_expiry = 0

                wheel_positions.append({
                    'strategy': 'CSP',
                    'symbol': opt['symbol'],
                    'strike': opt.get('strike', 0),
                    'expiration': opt.get('expiration', ''),
                    'days_to_expiry': days_to_expiry,
                    'premium': opt.get('avg_price', 0) * opt.get('quantity', 0) * 100,
                    'current_value': opt.get('current_price', 0) * opt.get('quantity', 0) * 100
                })

        # Find covered calls
        for opt in options:
            if opt.get('option_type') == 'call' and opt.get('side') == 'short':
                try:
                    days_to_expiry = (datetime.strptime(opt['expiration'], '%Y-%m-%d') - datetime.now()).days
                except:
                    days_to_expiry = 0

                wheel_positions.append({
                    'strategy': 'CC',
                    'symbol': opt['symbol'],
                    'strike': opt.get('strike', 0),
                    'expiration': opt.get('expiration', ''),
                    'days_to_expiry': days_to_expiry,
                    'premium': opt.get('avg_price', 0) * opt.get('quantity', 0) * 100,
                    'current_value': opt.get('current_price', 0) * opt.get('quantity', 0) * 100
                })

    return wheel_positions