"""Fixed Robinhood Integration that properly handles your positions"""

import robin_stocks.robinhood as rh
import os
from typing import Dict, List, Any
from datetime import datetime
import time
from pathlib import Path
import pickle

def login_robinhood(username=None, password=None):
    """Simple login to Robinhood"""
    username = username or os.getenv('ROBINHOOD_USERNAME')
    password = password or os.getenv('ROBINHOOD_PASSWORD')

    if not username or not password:
        return False

    try:
        login = rh.authentication.login(
            username=username,
            password=password,
            expiresIn=86400,
            store_session=True
        )
        if login:
            print("Login successful!")
            return True
        return False
    except Exception as e:
        print(f"Login error: {e}")
        return False

def get_account_summary():
    """Get account summary"""
    try:
        profile = rh.profiles.load_account_profile()
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
    """Get all stock positions"""
    try:
        positions = []
        stocks = rh.account.get_open_stock_positions()

        if not stocks:
            return []

        for stock in stocks:
            if float(stock.get('quantity', 0)) > 0:
                # Get symbol from instrument URL
                instrument_data = rh.stocks.get_instrument_by_url(stock['instrument'])
                symbol = instrument_data['symbol'] if instrument_data else 'Unknown'

                # Get current price
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
    """Get option positions - FIXED VERSION"""
    try:
        options = []
        option_positions = rh.options.get_open_option_positions()

        if not option_positions or not isinstance(option_positions, list):
            return []

        for opt in option_positions:
            # Skip if not a dict or quantity is 0
            if not isinstance(opt, dict):
                continue

            quantity = float(opt.get('quantity', 0))
            if quantity == 0:
                continue

            # Get basic info
            symbol = opt.get('chain_symbol', 'Unknown')
            option_type = opt.get('type', 'unknown')  # 'short' or 'long'

            # For short positions, quantity might be negative
            is_short = option_type == 'short' or quantity < 0
            abs_quantity = abs(quantity)

            # Get option details
            option_url = opt.get('option')
            strike = 0
            expiration = ''
            current_price = 0
            option_type_str = 'unknown'

            # Get option details from the URL
            if option_url:
                try:
                    option_details = rh.helper.request_get(option_url)
                    if option_details:
                        option_type_str = option_details.get('type', 'unknown')  # 'call' or 'put'
                        strike = float(option_details.get('strike_price', 0))
                        expiration = option_details.get('expiration_date', '')
                except Exception as e:
                    print(f"Error getting option details: {e}")

            # Get current market price
            option_id = opt.get('option_id')
            if option_id:
                try:
                    market_data = rh.options.get_option_market_data_by_id(option_id)
                    if market_data and isinstance(market_data, list) and len(market_data) > 0:
                        current_price = float(market_data[0].get('mark_price', 0))
                    elif isinstance(market_data, dict):
                        current_price = float(market_data.get('mark_price', 0))
                except:
                    pass

            options.append({
                'type': 'option',
                'symbol': symbol,
                'option_type': option_type_str,  # 'call' or 'put'
                'quantity': abs_quantity,
                'side': 'short' if is_short else 'long',
                'strike': strike,
                'expiration': expiration,
                'avg_price': abs(float(opt.get('average_price', 0)) / 100),  # Convert cents to dollars
                'current_price': current_price
            })

        return options
    except Exception as e:
        print(f"Error getting options: {e}")
        import traceback
        traceback.print_exc()
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

    # Process options
    if options:
        for opt in options:
            # Cash-secured puts (short puts)
            if opt.get('option_type') == 'put' and opt.get('side') == 'short':
                try:
                    days_to_expiry = (datetime.strptime(opt['expiration'], '%Y-%m-%d') - datetime.now()).days if opt.get('expiration') else 0
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

            # Covered calls (short calls)
            elif opt.get('option_type') == 'call' and opt.get('side') == 'short':
                try:
                    days_to_expiry = (datetime.strptime(opt['expiration'], '%Y-%m-%d') - datetime.now()).days if opt.get('expiration') else 0
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