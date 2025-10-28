"""Simplified Robinhood Integration"""

import robin_stocks.robinhood as rh
import os
from typing import Dict, List, Any
from datetime import datetime
import pandas as pd

def login_robinhood(username=None, password=None, expiresIn=86400):
    """Simple login to Robinhood with session caching"""
    username = username or os.getenv('ROBINHOOD_USERNAME')
    password = password or os.getenv('ROBINHOOD_PASSWORD')

    try:
        # First try to use cached session
        import pickle
        from pathlib import Path

        pickle_path = Path.home() / '.robinhood_token.pickle'

        # Try to load existing session
        if pickle_path.exists():
            try:
                with open(pickle_path, 'rb') as f:
                    login_data = pickle.load(f)
                    # Set the authentication token
                    rh.authentication.set_login_state(True)
                    print("Using cached session - no MFA needed!")
                    return True
            except:
                pass

        # If no cached session, do fresh login
        login = rh.authentication.login(
            username=username,
            password=password,
            expiresIn=expiresIn,
            scope='internal',
            store_session=True  # This will save the session
        )

        # Save session for next time
        if login:
            with open(pickle_path, 'wb') as f:
                pickle.dump(login, f)
            print("Login successful! Session saved for next time.")
            return True
        return False

    except Exception as e:
        # If login requires MFA, user will get prompt
        print(f"Please check your phone/email for MFA code")
        print(f"Error details: {e}")

        # Try login with MFA prompt
        try:
            login = rh.authentication.login(
                username=username,
                password=password,
                expiresIn=expiresIn,
                store_session=True
            )
            if login:
                # Save session
                pickle_path = Path.home() / '.robinhood_token.pickle'
                with open(pickle_path, 'wb') as f:
                    pickle.dump(login, f)
                print("Login successful! Session saved.")
                return True
        except:
            pass

        return False

def get_account_summary():
    """Get account summary"""
    try:
        # Get account profile
        profile = rh.profiles.load_account_profile()

        # Get portfolio value
        portfolio = rh.profiles.load_portfolio_profile()

        return {
            'buying_power': float(profile.get('buying_power', 0)),
            'cash': float(profile.get('cash', 0)),
            'portfolio_value': float(portfolio.get('market_value', 0) if portfolio else 0),
            'total_return': float(portfolio.get('total_return_today', 0) if portfolio else 0),
            'day_trades': profile.get('day_trade_count', 0)
        }
    except Exception as e:
        print(f"Error getting account: {e}")
        return {}

def get_positions():
    """Get all positions"""
    try:
        positions = []

        # Get stock positions
        stocks = rh.account.get_open_stock_positions()

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
    """Get option positions"""
    try:
        options = []

        # Get all open option positions
        option_positions = rh.options.get_open_option_positions()

        for opt in option_positions:
            if float(opt.get('quantity', 0)) != 0:
                # Get option details
                option_id = opt.get('option_id')
                if option_id:
                    market_data = rh.options.get_option_market_data_by_id(option_id)

                    if market_data:
                        options.append({
                            'type': 'option',
                            'symbol': opt.get('chain_symbol', 'Unknown'),
                            'option_type': opt.get('type', 'unknown'),  # 'call' or 'put'
                            'quantity': abs(float(opt.get('quantity', 0))),
                            'side': 'short' if float(opt.get('quantity', 0)) < 0 else 'long',
                            'strike': float(market_data.get('strike_price', 0)),
                            'expiration': market_data.get('expiration_date', ''),
                            'avg_price': float(opt.get('average_price', 0)) / 100,  # Convert cents to dollars
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
    for stock in stocks:
        if stock['quantity'] >= 100:
            wheel_positions.append({
                'strategy': 'Potential CC',
                'symbol': stock['symbol'],
                'shares': stock['quantity'],
                'contracts_available': int(stock['quantity'] / 100),
                'cost_basis': stock['avg_cost'],
                'current_price': stock['current_price'],
                'unrealized_pnl': stock['pnl']
            })

    # Find cash-secured puts
    for opt in options:
        if opt['option_type'] == 'put' and opt['side'] == 'short':
            days_to_expiry = (datetime.strptime(opt['expiration'], '%Y-%m-%d') - datetime.now()).days

            wheel_positions.append({
                'strategy': 'CSP',
                'symbol': opt['symbol'],
                'strike': opt['strike'],
                'expiration': opt['expiration'],
                'days_to_expiry': days_to_expiry,
                'premium': opt['avg_price'] * opt['quantity'] * 100,
                'current_value': opt['current_price'] * opt['quantity'] * 100
            })

    # Find covered calls
    for opt in options:
        if opt['option_type'] == 'call' and opt['side'] == 'short':
            days_to_expiry = (datetime.strptime(opt['expiration'], '%Y-%m-%d') - datetime.now()).days

            wheel_positions.append({
                'strategy': 'CC',
                'symbol': opt['symbol'],
                'strike': opt['strike'],
                'expiration': opt['expiration'],
                'days_to_expiry': days_to_expiry,
                'premium': opt['avg_price'] * opt['quantity'] * 100,
                'current_value': opt['current_price'] * opt['quantity'] * 100
            })

    return wheel_positions

# Test functions
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    print("Testing Simplified Robinhood Connection...")
    print("-" * 40)

    if login_robinhood():
        print("\n✓ Logged in successfully!")

        # Get account
        account = get_account_summary()
        if account:
            print(f"\nAccount Summary:")
            print(f"  Buying Power: ${account.get('buying_power', 0):,.2f}")
            print(f"  Portfolio Value: ${account.get('portfolio_value', 0):,.2f}")
            print(f"  Cash: ${account.get('cash', 0):,.2f}")

        # Get positions
        stocks = get_positions()
        options = get_options()

        print(f"\nPositions:")
        print(f"  Stocks: {len(stocks)}")
        print(f"  Options: {len(options)}")

        # Show wheel positions
        wheel = identify_wheel_positions(stocks, options)
        print(f"\nWheel Strategy Positions: {len(wheel)}")

        for pos in wheel:
            print(f"  {pos['strategy']}: {pos['symbol']}")

        # Logout
        rh.authentication.logout()
        print("\nLogged out.")
    else:
        print("\nFailed to login. Please check:")
        print("1. Your username and password in .env file")
        print("2. Check your email for login verification")
        print("3. Try logging in to Robinhood app first")