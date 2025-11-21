"""
Positions Manager for Options Analysis
Fetches and formats current Robinhood positions for stock selector dropdown
"""

import logging
from typing import List, Dict, Any, Optional
from src.services.positions_connector import PositionsConnector

logger = logging.getLogger(__name__)


class PositionsManager:
    """Manage current options positions for Options Analysis page"""

    def __init__(self):
        """Initialize positions manager with Robinhood connector"""
        try:
            self.connector = PositionsConnector(cache_ttl=60)  # Cache for 60 seconds
        except Exception as e:
            logger.error(f"Failed to initialize PositionsConnector: {e}")
            self.connector = None

    def get_current_positions(self) -> List[Dict[str, Any]]:
        """
        Fetch all current option positions from Robinhood

        Returns:
            List of position dictionaries with format:
            [
                {
                    'symbol': 'AAPL',
                    'strike': 150.0,
                    'expiry': '2025-12-15',
                    'option_type': 'put',
                    'dte': 30,
                    'quantity': 5,
                    'entry_price': 2.50,
                    'current_price': 3.10,
                    'pnl': 300.0,
                    'pnl_pct': 24.0,
                    'delta': -0.35,
                    'theta': -0.05,
                    'gamma': 0.02,
                    'vega': 0.15
                },
                ...
            ]
        """
        if not self.connector:
            logger.warning("PositionsConnector not available")
            return []

        try:
            # Fetch all positions (no filters)
            response = self.connector.get_data()

            if response.get("success", False):
                positions = response.get("data", [])
                logger.info(f"Fetched {len(positions)} positions from Robinhood")
                return positions
            else:
                error_msg = response.get("error", "Unknown error")
                logger.error(f"Failed to fetch positions: {error_msg}")
                return []

        except Exception as e:
            logger.error(f"Error fetching positions: {e}")
            return []

    def format_for_dropdown(self, positions: List[Dict[str, Any]]) -> List[tuple]:
        """
        Format positions for stock selector dropdown

        Args:
            positions: List of position dictionaries from get_current_positions()

        Returns:
            List of tuples: (display_text, position_data)
            Example:
            [
                ("AAPL - $150 PUT 30 DTE (+$300 | +24%)", {...position_data...}),
                ("TSLA - $700 CALL 45 DTE (-$150 | -10%)", {...position_data...}),
                ...
            ]
        """
        formatted = []

        for pos in positions:
            symbol = pos.get('symbol', 'UNKNOWN')
            strike = pos.get('strike', 0)
            option_type = pos.get('option_type', 'unknown').upper()
            dte = pos.get('dte', 0)
            pnl = pos.get('pnl', 0)
            pnl_pct = pos.get('pnl_pct', 0)

            # Format P&L with + or - sign
            pnl_sign = '+' if pnl >= 0 else ''
            pnl_pct_sign = '+' if pnl_pct >= 0 else ''

            # Create display text
            display_text = (
                f"{symbol} - ${strike:.0f} {option_type} {dte} DTE "
                f"({pnl_sign}${pnl:.0f} | {pnl_pct_sign}{pnl_pct:.1f}%)"
            )

            formatted.append((display_text, pos))

        # Sort by DTE (positions expiring soonest first)
        formatted.sort(key=lambda x: x[1].get('dte', 999))

        return formatted

    def get_position_by_symbol(self, symbol: str) -> List[Dict[str, Any]]:
        """
        Get all positions for a specific symbol

        Args:
            symbol: Stock ticker (e.g., 'AAPL')

        Returns:
            List of positions for that symbol
        """
        if not self.connector:
            return []

        try:
            response = self.connector.get_data(symbol=symbol.upper())

            if response.get("success", False):
                return response.get("data", [])
            else:
                return []

        except Exception as e:
            logger.error(f"Error fetching positions for {symbol}: {e}")
            return []

    def has_positions(self) -> bool:
        """
        Check if user has any current positions

        Returns:
            True if user has at least one position, False otherwise
        """
        positions = self.get_current_positions()
        return len(positions) > 0
