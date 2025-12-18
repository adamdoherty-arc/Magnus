"""
Earnings Manager - Handles earnings data operations and Robinhood API integration
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd
import robin_stocks.robinhood as rh
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Any, Tuple
import os
from dotenv import load_dotenv
import logging
from src.services.rate_limiter import rate_limit

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv(override=True)

# PERFORMANCE FIX: Rate-limited Robinhood API wrapper
@rate_limit("robinhood", tokens=1, timeout=30)
def get_earnings_rate_limited(symbol: str):
    """Rate-limited wrapper for rh.get_earnings()"""
    return rh.get_earnings(symbol)


class EarningsManager:
    """Manages earnings calendar data and Robinhood sync operations"""

    def __init__(self, db_config: Optional[Dict] = None):
        """Initialize with database configuration"""
        if db_config is None:
            db_config = {
                'host': os.getenv('DB_HOST', 'localhost'),
                'port': os.getenv('DB_PORT', '5432'),
                'user': os.getenv('DB_USER', 'postgres'),
                'password': os.getenv('DB_PASSWORD', 'postgres123!'),
                'database': os.getenv('DB_NAME', 'magnus')
            }

        self.db_config = db_config
        self.conn = psycopg2.connect(**db_config)
        self.robinhood_logged_in = False
        self._ensure_tables()

    def _ensure_tables(self):
        """Ensure earnings tables exist"""
        cur = self.conn.cursor()

        # Create earnings_events table if not exists
        cur.execute("""
            CREATE TABLE IF NOT EXISTS earnings_events (
                id SERIAL PRIMARY KEY,
                symbol VARCHAR(20) NOT NULL,
                earnings_date TIMESTAMP WITH TIME ZONE NOT NULL,
                earnings_time VARCHAR(10),  -- BMO, AMC, or NULL
                eps_estimate NUMERIC(10, 4),
                eps_actual NUMERIC(10, 4),
                revenue_estimate NUMERIC(20, 2),
                revenue_actual NUMERIC(20, 2),
                surprise_percent NUMERIC(10, 2),
                pre_earnings_iv NUMERIC(10, 4),
                post_earnings_iv NUMERIC(10, 4),
                pre_earnings_price NUMERIC(10, 2),
                post_earnings_price NUMERIC(10, 2),
                price_move_percent NUMERIC(10, 2),
                volume_ratio NUMERIC(10, 2),
                options_volume INTEGER,
                whisper_number NUMERIC(10, 4),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                UNIQUE(symbol, earnings_date)
            )
        """)

        # Create earnings_history table for Robinhood synced data
        cur.execute("""
            CREATE TABLE IF NOT EXISTS earnings_history (
                id SERIAL PRIMARY KEY,
                symbol VARCHAR(20) NOT NULL,
                report_date DATE NOT NULL,
                quarter INTEGER,
                year INTEGER,
                eps_actual NUMERIC(10, 4),
                eps_estimate NUMERIC(10, 4),
                call_datetime TIMESTAMP WITH TIME ZONE,
                call_replay_url TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                UNIQUE(symbol, report_date)
            )
        """)

        # Create indexes
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_earnings_events_symbol
            ON earnings_events(symbol)
        """)

        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_earnings_events_date
            ON earnings_events(earnings_date)
        """)

        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_earnings_history_symbol
            ON earnings_history(symbol)
        """)

        self.conn.commit()
        cur.close()

    def get_earnings_events(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        time_filter: str = "all",
        sector_filter: Optional[str] = None,
        symbols: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Fetch earnings events with optional filters

        Args:
            start_date: Filter events >= this date
            end_date: Filter events <= this date
            time_filter: 'all', 'BMO', or 'AMC'
            sector_filter: Filter by sector
            symbols: List of specific symbols to fetch

        Returns:
            DataFrame with earnings events
        """
        query = """
            SELECT
                e.*,
                s.company_name,
                s.sector,
                s.industry,
                s.market_cap,
                s.last_price as current_price
            FROM earnings_events e
            LEFT JOIN stocks s ON e.symbol = s.symbol
            WHERE 1=1
        """
        params = []

        if start_date:
            query += " AND e.earnings_date >= %s"
            params.append(start_date)

        if end_date:
            query += " AND e.earnings_date <= %s"
            params.append(end_date)

        if time_filter != "all":
            query += " AND e.earnings_time = %s"
            params.append(time_filter.upper())

        if sector_filter and sector_filter != "All Sectors":
            query += " AND s.sector = %s"
            params.append(sector_filter)

        if symbols:
            placeholders = ','.join(['%s'] * len(symbols))
            query += f" AND e.symbol IN ({placeholders})"
            params.extend(symbols)

        query += " ORDER BY e.earnings_date ASC, e.symbol ASC"

        df = pd.read_sql_query(query, self.conn, params=params)

        if not df.empty:
            # Calculate derived fields
            df['status'] = df.apply(self._calculate_status, axis=1)
            df['surprise_pct'] = df.apply(self._calculate_surprise, axis=1)
            df['expected_move'] = df.apply(self._calculate_expected_move, axis=1)

        return df

    def _calculate_status(self, row) -> str:
        """Determine earnings status: beat, miss, inline, or pending"""
        if pd.isna(row['eps_actual']):
            return 'pending'
        elif pd.isna(row['eps_estimate']):
            return 'reported'
        elif row['eps_actual'] > row['eps_estimate']:
            return 'beat'
        elif row['eps_actual'] < row['eps_estimate']:
            return 'miss'
        else:
            return 'inline'

    def _calculate_surprise(self, row) -> float:
        """Calculate EPS surprise percentage"""
        if pd.isna(row['eps_actual']) or pd.isna(row['eps_estimate']):
            return 0.0
        if row['eps_estimate'] == 0:
            return 0.0
        return ((row['eps_actual'] - row['eps_estimate']) / abs(row['eps_estimate'])) * 100

    def _calculate_expected_move(self, row) -> float:
        """Calculate expected move from IV (straddle pricing)"""
        if pd.isna(row['pre_earnings_iv']) or pd.isna(row.get('current_price')):
            return 0.0

        # Expected move = Stock Price * IV * sqrt(DTE / 365)
        # For earnings (typically ~1 day event), we use simplified formula
        # Expected move ≈ Stock Price * IV
        return row['current_price'] * row['pre_earnings_iv']

    def get_historical_earnings(self, symbol: str, limit: int = 12) -> pd.DataFrame:
        """Get historical earnings for a specific symbol"""
        query = """
            SELECT * FROM earnings_history
            WHERE symbol = %s
            ORDER BY report_date DESC
            LIMIT %s
        """
        df = pd.read_sql_query(query, self.conn, params=[symbol, limit])

        if not df.empty:
            df['surprise_pct'] = df.apply(
                lambda row: ((row['eps_actual'] - row['eps_estimate']) / abs(row['eps_estimate']) * 100)
                if pd.notna(row['eps_actual']) and pd.notna(row['eps_estimate']) and row['eps_estimate'] != 0
                else 0.0,
                axis=1
            )

        return df

    def get_analytics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate analytics from earnings data

        Returns:
            Dictionary with analytics metrics
        """
        if df.empty:
            return {
                'total_events': 0,
                'pending': 0,
                'beat': 0,
                'miss': 0,
                'inline': 0,
                'avg_surprise': 0.0,
                'beat_rate': 0.0,
                'avg_move': 0.0
            }

        reported = df[df['status'] != 'pending']

        return {
            'total_events': len(df),
            'pending': len(df[df['status'] == 'pending']),
            'beat': len(df[df['status'] == 'beat']),
            'miss': len(df[df['status'] == 'miss']),
            'inline': len(df[df['status'] == 'inline']),
            'avg_surprise': reported['surprise_pct'].mean() if not reported.empty else 0.0,
            'beat_rate': (len(df[df['status'] == 'beat']) / len(reported) * 100) if len(reported) > 0 else 0.0,
            'avg_move': df['price_move_percent'].mean() if 'price_move_percent' in df.columns else 0.0
        }

    def sync_robinhood_earnings(
        self,
        symbols: List[str],
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Sync earnings data from Robinhood API

        Args:
            symbols: List of stock symbols to sync
            progress_callback: Optional callback(current, total, symbol)

        Returns:
            Dictionary with sync results
        """
        # Login to Robinhood
        if not self.robinhood_logged_in:
            try:
                username = os.getenv('ROBINHOOD_USERNAME')
                password = os.getenv('ROBINHOOD_PASSWORD')

                if not username or not password:
                    return {
                        'success': False,
                        'error': 'Robinhood credentials not configured in .env'
                    }

                rh.login(username, password)
                self.robinhood_logged_in = True
                logger.info("Logged in to Robinhood")

            except Exception as e:
                return {
                    'success': False,
                    'error': f'Robinhood login failed: {str(e)}'
                }

        synced = 0
        errors = 0
        error_symbols = []

        for i, symbol in enumerate(symbols):
            try:
                if progress_callback:
                    progress_callback(i + 1, len(symbols), symbol)

                # Fetch earnings from Robinhood
                # PERFORMANCE: Rate-limited API call
                earnings_data = get_earnings_rate_limited(symbol)

                if earnings_data and isinstance(earnings_data, list):
                    # Process each earnings record (last 8 quarters)
                    for earning in earnings_data[:8]:
                        self._insert_earnings_history(symbol, earning)
                    synced += 1
                    logger.info(f"Synced {symbol}: {len(earnings_data[:8])} records")

            except Exception as e:
                errors += 1
                error_symbols.append(symbol)
                logger.error(f"Error syncing {symbol}: {str(e)}")
                continue

        # Logout
        try:
            rh.logout()
            self.robinhood_logged_in = False
            logger.info("Logged out from Robinhood")
        except:
            pass

        return {
            'success': True,
            'synced': synced,
            'errors': errors,
            'total': len(symbols),
            'error_symbols': error_symbols
        }

    def _insert_earnings_history(self, symbol: str, earning_data: dict):
        """Insert earnings history record from Robinhood data"""
        try:
            # Extract data from Robinhood format
            report = earning_data.get('report', {})
            eps = earning_data.get('eps', {})
            call_info = earning_data.get('call', {})

            report_date = report.get('date')
            eps_actual = eps.get('actual')
            eps_estimate = eps.get('estimate')
            quarter = earning_data.get('quarter')
            year = earning_data.get('year')

            call_datetime = call_info.get('datetime') if call_info else None
            call_replay_url = call_info.get('replay_url') if call_info else None

            if not report_date:
                return

            cur = self.conn.cursor()

            # Insert or update earnings_history
            cur.execute("""
                INSERT INTO earnings_history (
                    symbol, report_date, quarter, year,
                    eps_actual, eps_estimate,
                    call_datetime, call_replay_url
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (symbol, report_date)
                DO UPDATE SET
                    quarter = EXCLUDED.quarter,
                    year = EXCLUDED.year,
                    eps_actual = EXCLUDED.eps_actual,
                    eps_estimate = EXCLUDED.eps_estimate,
                    call_datetime = EXCLUDED.call_datetime,
                    call_replay_url = EXCLUDED.call_replay_url
            """, (
                symbol, report_date, quarter, year,
                eps_actual, eps_estimate,
                call_datetime, call_replay_url
            ))

            self.conn.commit()
            cur.close()

        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error inserting earnings history for {symbol}: {str(e)}")

    def get_sectors(self) -> List[str]:
        """Get unique sectors with earnings data"""
        query = """
            SELECT DISTINCT s.sector
            FROM earnings_events e
            JOIN stocks s ON e.symbol = s.symbol
            WHERE s.sector IS NOT NULL
            ORDER BY s.sector
        """
        df = pd.read_sql_query(query, self.conn)
        return ['All Sectors'] + df['sector'].tolist()

    def add_earnings_event(
        self,
        symbol: str,
        earnings_date: datetime,
        earnings_time: Optional[str] = None,
        eps_estimate: Optional[float] = None,
        **kwargs
    ) -> bool:
        """
        Add or update an earnings event

        Args:
            symbol: Stock symbol
            earnings_date: Date and time of earnings
            earnings_time: 'BMO' or 'AMC'
            eps_estimate: EPS estimate
            **kwargs: Additional fields

        Returns:
            True if successful
        """
        try:
            cur = self.conn.cursor()

            fields = ['symbol', 'earnings_date', 'earnings_time', 'eps_estimate', 'updated_at']
            values = [symbol, earnings_date, earnings_time, eps_estimate, datetime.now()]

            # Add optional fields
            for key, value in kwargs.items():
                if value is not None:
                    fields.append(key)
                    values.append(value)

            placeholders = ','.join(['%s'] * len(values))
            field_str = ','.join(fields)

            # Build ON CONFLICT update clause
            update_fields = [f"{f} = EXCLUDED.{f}" for f in fields if f not in ['symbol', 'earnings_date']]
            update_clause = ','.join(update_fields)

            cur.execute(f"""
                INSERT INTO earnings_events ({field_str})
                VALUES ({placeholders})
                ON CONFLICT (symbol, earnings_date)
                DO UPDATE SET {update_clause}
            """, values)

            self.conn.commit()
            cur.close()

            logger.info(f"Added/updated earnings event for {symbol} on {earnings_date}")
            return True

        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error adding earnings event: {str(e)}")
            return False

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
