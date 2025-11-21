"""Automated Daily Balance Recorder - Records portfolio balances once per day"""

from datetime import date
from typing import Optional, Dict
import logging
from src.portfolio_balance_tracker import PortfolioBalanceTracker

logger = logging.getLogger(__name__)


class AutoBalanceRecorder:
    """Automatically records daily portfolio balances once per day"""

    def __init__(self):
        self.tracker = PortfolioBalanceTracker()

    def should_record_today(self) -> bool:
        """
        Check if we need to record balance for today

        Returns:
            True if no record exists for today
        """
        try:
            latest = self.tracker.get_latest_balance()

            if not latest:
                # No records at all, should record
                return True

            latest_date = latest.get('date')

            if isinstance(latest_date, str):
                from datetime import datetime
                latest_date = datetime.strptime(latest_date, '%Y-%m-%d').date()

            # Record if latest is not today
            return latest_date < date.today()

        except Exception as e:
            logger.error(f"Error checking if should record: {e}")
            return True  # Default to recording if error

    def auto_record_balance(
        self,
        total_equity: float,
        buying_power: float,
        options_value: float,
        stock_value: float,
        total_positions: int
    ) -> Dict[str, any]:
        """
        Automatically record today's balance if not already recorded

        Args:
            total_equity: Total account equity
            buying_power: Available buying power
            options_value: Total value of options
            stock_value: Total value of stocks
            total_positions: Number of positions

        Returns:
            Dictionary with status and message
        """
        try:
            # Check if we should record
            if not self.should_record_today():
                return {
                    'recorded': False,
                    'reason': 'already_recorded',
                    'message': 'Balance already recorded for today'
                }

            # Record the balance
            success = self.tracker.record_daily_balance(
                balance_date=date.today(),
                ending_balance=total_equity,
                buying_power=buying_power,
                options_value=options_value,
                stock_value=stock_value,
                cash_value=buying_power,
                total_positions=total_positions
            )

            if success:
                logger.info(f"✅ Auto-recorded balance for {date.today()}: ${total_equity:,.2f}")
                return {
                    'recorded': True,
                    'reason': 'success',
                    'message': f'Balance recorded for {date.today()}',
                    'balance': total_equity
                }
            else:
                return {
                    'recorded': False,
                    'reason': 'error',
                    'message': 'Failed to record balance'
                }

        except Exception as e:
            logger.error(f"Error auto-recording balance: {e}")
            return {
                'recorded': False,
                'reason': 'exception',
                'message': str(e)
            }

    def get_recording_status(self) -> str:
        """
        Get a human-readable status message

        Returns:
            Status message string
        """
        try:
            latest = self.tracker.get_latest_balance()

            if not latest:
                return "⏳ No balance history yet"

            latest_date = latest.get('date')

            if isinstance(latest_date, str):
                from datetime import datetime
                latest_date = datetime.strptime(latest_date, '%Y-%m-%d').date()

            if latest_date == date.today():
                balance = latest.get('ending_balance', 0)
                return f"✅ Today's balance recorded: ${float(balance):,.2f}"
            else:
                return f"⏳ Last recorded: {latest_date}"

        except Exception as e:
            logger.error(f"Error getting status: {e}")
            return "⚠️ Status unavailable"
