"""
Kalshi API Client for Sports Markets
Fetches NFL and College Football game markets with automatic token refresh
"""

import os
import requests
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KalshiClient:
    """Client for Kalshi prediction market API"""

    BASE_URL = "https://trading-api.kalshi.com/trade-api/v2"

    def __init__(self, email: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize Kalshi client

        Args:
            email: Kalshi account email (or set KALSHI_EMAIL env var)
            password: Kalshi account password (or set KALSHI_PASSWORD env var)
        """
        self.email = email or os.getenv('KALSHI_EMAIL')
        self.password = password or os.getenv('KALSHI_PASSWORD')
        self.bearer_token = None
        self.token_expires_at = None

    def _needs_token_refresh(self) -> bool:
        """Check if token needs refresh (expires in 30 min, refresh after 25)"""
        if not self.bearer_token or not self.token_expires_at:
            return True

        # Refresh 5 minutes before expiration
        return datetime.now() >= (self.token_expires_at - timedelta(minutes=5))

    def login(self) -> bool:
        """
        Login to Kalshi and get bearer token

        Returns:
            True if login successful, False otherwise
        """
        if not self.email or not self.password:
            logger.error("Kalshi credentials not provided. Set KALSHI_EMAIL and KALSHI_PASSWORD env vars.")
            return False

        try:
            url = f"{self.BASE_URL}/login"
            headers = {
                "accept": "application/json",
                "content-type": "application/json"
            }
            body = {
                "email": self.email,
                "password": self.password
            }

            response = requests.post(url, headers=headers, json=body, timeout=10)
            response.raise_for_status()

            token = response.json().get('token')
            if not token:
                logger.error("No token in login response")
                return False

            self.bearer_token = f"Bearer {token}"
            self.token_expires_at = datetime.now() + timedelta(minutes=30)
            logger.info("Successfully logged into Kalshi API")
            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"Kalshi login failed: {e}")
            return False

    def _ensure_authenticated(self) -> bool:
        """Ensure we have a valid token, refresh if needed"""
        if self._needs_token_refresh():
            return self.login()
        return True

    def get_all_markets(self, status: str = "open", limit: int = 1000) -> List[Dict]:
        """
        Get all markets from Kalshi

        Args:
            status: Market status filter ('open', 'closed', 'settled')
            limit: Results per page (max 1000)

        Returns:
            List of market dictionaries
        """
        if not self._ensure_authenticated():
            return []

        all_markets = []
        cursor = None

        try:
            while True:
                url = f"{self.BASE_URL}/markets"
                params = {
                    "limit": limit,
                    "status": status
                }

                if cursor:
                    params['cursor'] = cursor

                headers = {
                    "accept": "application/json",
                    "Authorization": self.bearer_token
                }

                response = requests.get(url, headers=headers, params=params, timeout=10)
                response.raise_for_status()

                data = response.json()
                markets = data.get('markets', [])
                all_markets.extend(markets)

                # Check for next page
                cursor = data.get('cursor')
                if not cursor:
                    break

                # Small delay to avoid rate limits
                time.sleep(0.5)

            logger.info(f"Retrieved {len(all_markets)} markets from Kalshi")
            return all_markets

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching markets: {e}")
            return []

    def filter_football_markets(self, markets: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Filter markets to only NFL and college football games

        Args:
            markets: List of all markets

        Returns:
            Dictionary with 'nfl' and 'college' keys containing filtered markets
        """
        nfl_markets = []
        college_markets = []

        # Keywords to identify football markets
        nfl_keywords = ['nfl', 'super bowl', 'playoffs', 'chiefs', 'bills', 'ravens',
                        'packers', '49ers', 'cowboys', 'eagles', 'lions', 'rams']
        college_keywords = ['college football', 'ncaa football', 'cfp', 'alabama',
                           'georgia', 'ohio state', 'michigan', 'texas', 'clemson']

        for market in markets:
            title = market.get('title', '').lower()
            ticker = market.get('ticker', '').lower()
            subtitle = market.get('subtitle', '').lower()
            series_ticker = market.get('series_ticker', '').lower()

            # Combine all text fields for searching
            combined_text = f"{title} {ticker} {subtitle} {series_ticker}"

            # Check for NFL
            if any(keyword in combined_text for keyword in nfl_keywords):
                nfl_markets.append(market)
            # Check for college football
            elif any(keyword in combined_text for keyword in college_keywords):
                college_markets.append(market)

        logger.info(f"Found {len(nfl_markets)} NFL markets and {len(college_markets)} college football markets")

        return {
            'nfl': nfl_markets,
            'college': college_markets
        }

    def get_football_markets(self) -> Dict[str, List[Dict]]:
        """
        Get all NFL and college football markets

        Returns:
            Dictionary with 'nfl' and 'college' keys
        """
        all_markets = self.get_all_markets(status='open')
        return self.filter_football_markets(all_markets)

    def get_market_details(self, market_ticker: str) -> Optional[Dict]:
        """
        Get detailed information for a specific market

        Args:
            market_ticker: Market ticker symbol

        Returns:
            Market details dictionary or None
        """
        if not self._ensure_authenticated():
            return None

        try:
            url = f"{self.BASE_URL}/markets/{market_ticker}"
            headers = {
                "accept": "application/json",
                "Authorization": self.bearer_token
            }

            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            market_data = response.json()

            # Extract market from response if nested
            if 'market' in market_data:
                return market_data['market']
            return market_data

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching market details for {market_ticker}: {e}")
            return None

    def get_market(self, market_ticker: str) -> Optional[Dict]:
        """Alias for get_market_details for consistency"""
        return self.get_market_details(market_ticker)

    def get_market_orderbook(self, market_ticker: str) -> Optional[Dict]:
        """
        Get current orderbook (bids/asks) for a market

        Args:
            market_ticker: Market ticker symbol

        Returns:
            Orderbook data or None
        """
        if not self._ensure_authenticated():
            return None

        try:
            url = f"{self.BASE_URL}/markets/{market_ticker}/orderbook"
            headers = {
                "accept": "application/json",
                "Authorization": self.bearer_token
            }

            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching orderbook for {market_ticker}: {e}")
            return None

    # Portfolio Methods

    def get_portfolio_balance(self) -> Optional[Dict]:
        """
        Get account balance and portfolio value

        Returns:
            Dict with balance info in cents:
            {
                'balance': int,  # Cash balance in cents
                'payout': int    # Portfolio value in cents
            }
        """
        if not self._ensure_authenticated():
            return None

        try:
            url = f"{self.BASE_URL}/portfolio/balance"
            headers = {
                "accept": "application/json",
                "Authorization": self.bearer_token
            }

            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            balance_data = response.json()
            logger.info(f"Retrieved Kalshi balance: ${balance_data.get('balance', 0) / 100:.2f}")
            return balance_data

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching portfolio balance: {e}")
            return None

    def get_portfolio_positions(self, ticker: Optional[str] = None,
                               event_ticker: Optional[str] = None,
                               limit: int = 1000) -> List[Dict]:
        """
        Get current portfolio positions (non-zero positions only)

        Args:
            ticker: Filter by market ticker (optional)
            event_ticker: Filter by event ticker (optional)
            limit: Maximum positions to return (default 1000)

        Returns:
            List of position dicts with:
            {
                'ticker': str,           # Market ticker
                'event_ticker': str,     # Event ticker
                'position': int,         # Number of contracts held
                'market_exposure': int,  # Value at risk in cents
                'total_traded': int,     # Total contracts traded
                'realized_pnl': int,     # Realized P&L in cents
                'fees_paid': int,        # Fees paid in cents
                'rest_pnl': int,         # Unrealized P&L in cents
                'total_cost_shares': int # Total cost of shares
            }
        """
        if not self._ensure_authenticated():
            return []

        try:
            url = f"{self.BASE_URL}/portfolio/positions"
            headers = {
                "accept": "application/json",
                "Authorization": self.bearer_token
            }

            params = {"limit": limit}
            if ticker:
                params['ticker'] = ticker
            if event_ticker:
                params['event_ticker'] = event_ticker

            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            positions = data.get('market_positions', [])

            logger.info(f"Retrieved {len(positions)} portfolio positions from Kalshi")
            return positions

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching portfolio positions: {e}")
            return []

    def get_fills(self, ticker: Optional[str] = None,
                  limit: int = 1000,
                  cursor: Optional[str] = None) -> Dict:
        """
        Get trade fills (executed orders) for the logged-in user

        Args:
            ticker: Filter by market ticker (optional)
            limit: Maximum fills to return (default 1000)
            cursor: Pagination cursor (optional)

        Returns:
            Dict with:
            {
                'fills': List[Dict],  # List of fill dictionaries
                'cursor': str         # Next page cursor if more results
            }

            Each fill contains:
            {
                'ticker': str,
                'is_yes': bool,          # True if YES position, False if NO
                'action': str,           # 'buy' or 'sell'
                'count': int,            # Number of contracts
                'price': int,            # Price in cents
                'created_time': str,     # ISO timestamp
                'no_price': int,         # NO price in cents
                'yes_price': int,        # YES price in cents
                'purchased_side': str    # 'YES' or 'NO'
            }
        """
        if not self._ensure_authenticated():
            return {'fills': [], 'cursor': None}

        try:
            url = f"{self.BASE_URL}/portfolio/fills"
            headers = {
                "accept": "application/json",
                "Authorization": self.bearer_token
            }

            params = {"limit": limit}
            if ticker:
                params['ticker'] = ticker
            if cursor:
                params['cursor'] = cursor

            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            fills = data.get('fills', [])

            logger.info(f"Retrieved {len(fills)} fills from Kalshi")
            return {
                'fills': fills,
                'cursor': data.get('cursor')
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching fills: {e}")
            return {'fills': [], 'cursor': None}

    def get_all_positions_with_details(self) -> List[Dict]:
        """
        Get all positions with market details included

        Returns:
            List of positions with enhanced market information:
            {
                # Position data
                'ticker': str,
                'position': int,
                'market_exposure': int,
                'realized_pnl': int,
                'unrealized_pnl': int,

                # Market data (fetched separately)
                'title': str,
                'yes_price': float,
                'no_price': float,
                'close_time': str,
                'status': str
            }
        """
        positions = self.get_portfolio_positions()

        if not positions:
            return []

        enhanced_positions = []

        for position in positions:
            # Get market details
            ticker = position.get('ticker')
            market = self.get_market_details(ticker)

            if market:
                enhanced_pos = {
                    **position,  # Include all position data
                    'title': market.get('title', 'Unknown'),
                    'yes_price': market.get('yes_bid', 0),
                    'no_price': market.get('no_bid', 0),
                    'close_time': market.get('close_time'),
                    'status': market.get('status'),
                    'market_type': market.get('market_type'),
                    'category': market.get('category')
                }
                enhanced_positions.append(enhanced_pos)
            else:
                # Include position even if market details fail
                enhanced_positions.append(position)

        logger.info(f"Enhanced {len(enhanced_positions)} positions with market details")
        return enhanced_positions


if __name__ == "__main__":
    # Test the Kalshi client
    from dotenv import load_dotenv
    load_dotenv()

    client = KalshiClient()

    print("\n" + "="*80)
    print("KALSHI API CLIENT - Football Markets Test")
    print("="*80)

    # Login
    if not client.login():
        print("\n❌ Login failed. Check credentials.")
        exit(1)

    print("\n✅ Login successful!")

    # Get football markets
    print("\n📊 Fetching all football markets...")
    football_markets = client.get_football_markets()

    # Display NFL markets
    print(f"\n{'='*80}")
    print(f"NFL MARKETS ({len(football_markets['nfl'])} found)")
    print(f"{'='*80}")

    for market in football_markets['nfl'][:10]:  # Show first 10
        print(f"\n{market.get('title', 'N/A')}")
        print(f"  Ticker: {market.get('ticker', 'N/A')}")
        print(f"  Close Time: {market.get('close_time', 'N/A')}")
        print(f"  Volume: ${market.get('volume', 0):,.0f}")

    # Display College markets
    print(f"\n{'='*80}")
    print(f"COLLEGE FOOTBALL MARKETS ({len(football_markets['college'])} found)")
    print(f"{'='*80}")

    for market in football_markets['college'][:10]:  # Show first 10
        print(f"\n{market.get('title', 'N/A')}")
        print(f"  Ticker: {market.get('ticker', 'N/A')}")
        print(f"  Close Time: {market.get('close_time', 'N/A')}")
        print(f"  Volume: ${market.get('volume', 0):,.0f}")

    print("\n" + "="*80)
    print("Test Complete!")
    print("="*80)
