"""Robinhood Authentication with proper MFA handling"""

import robin_stocks.robinhood as rh
import os
from pathlib import Path
import pickle
import time
from typing import Optional, Dict

def load_cached_session() -> Optional[Dict]:
    """Try to load cached session from pickle file"""
    pickle_path = Path.home() / '.robinhood_session.pickle'
    if pickle_path.exists():
        try:
            with open(pickle_path, 'rb') as f:
                return pickle.load(f)
        except:
            pass
    return None

def save_session(session_data: Dict):
    """Save session to pickle file"""
    pickle_path = Path.home() / '.robinhood_session.pickle'
    try:
        with open(pickle_path, 'wb') as f:
            pickle.dump(session_data, f)
        print("Session saved for future use")
    except Exception as e:
        print(f"Could not save session: {e}")

def login_with_cache(username: str = None, password: str = None) -> bool:
    """Login to Robinhood with session caching"""

    # Get credentials from environment if not provided
    if not username:
        username = os.getenv('ROBINHOOD_USERNAME')
    if not password:
        password = os.getenv('ROBINHOOD_PASSWORD')

    if not username or not password:
        print("ERROR: Missing credentials")
        return False

    # Try to load cached session first
    cached = load_cached_session()
    if cached:
        print("Found cached session, attempting to restore...")
        try:
            # Try to set the cached authentication
            rh.authentication.set_login_state(True)

            # Verify it works
            profile = rh.profiles.load_account_profile()
            if profile:
                print("Successfully restored cached session!")
                return True
        except:
            print("Cached session expired, need fresh login")

    # Fresh login
    print("Performing fresh login...")
    print("NOTE: You may receive an MFA request on your phone/email")

    try:
        # Attempt login - this will prompt for MFA if needed
        login_result = rh.authentication.login(
            username=username,
            password=password,
            expiresIn=86400,
            store_session=True,
            scope='internal'
        )

        if login_result:
            print("Login successful!")
            # Save the session
            save_session(login_result)
            return True
        else:
            print("Login failed - check credentials")
            return False

    except Exception as e:
        print(f"Login error: {e}")

        # Sometimes the error is due to needing MFA
        # The library should prompt automatically, but if not:
        if "mfa" in str(e).lower() or "challenge" in str(e).lower():
            print("\nMFA Required!")
            print("Please check your phone/email for the verification request")
            print("The library should prompt you for the code automatically")

        return False

def get_account_info() -> Dict:
    """Get account information"""
    try:
        profile = rh.profiles.load_account_profile()
        portfolio = rh.profiles.load_portfolio_profile()

        return {
            'buying_power': float(profile.get('buying_power', 0)),
            'cash': float(profile.get('cash', 0)),
            'portfolio_value': float(portfolio.get('market_value', 0) if portfolio else 0),
            'day_trades': profile.get('day_trade_count', 0)
        }
    except Exception as e:
        print(f"Error getting account info: {e}")
        return {}

def logout():
    """Logout from Robinhood"""
    try:
        rh.authentication.logout()
        print("Logged out")
    except:
        pass  # Already logged out

# Test the authentication
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    print("Testing Robinhood Authentication with Caching")
    print("="*50)

    if login_with_cache():
        print("\nAccount Info:")
        info = get_account_info()
        if info:
            print(f"  Buying Power: ${info['buying_power']:,.2f}")
            print(f"  Portfolio Value: ${info['portfolio_value']:,.2f}")

        logout()
    else:
        print("\nAuthentication failed")