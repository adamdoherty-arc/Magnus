"""TradingView Database Manager for Magnus Database"""

import psycopg2
from psycopg2.extras import RealDictCursor
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
import yfinance as yf
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class TradingViewDBManager:
    """Manages TradingView watchlists in Magnus PostgreSQL database"""

    def __init__(self):
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'postgres123!'),
            'database': os.getenv('DB_NAME', 'magnus')
        }
        self.initialize_tables()

    def get_connection(self):
        """Get database connection"""
        return psycopg2.connect(**self.db_config)

    def initialize_tables(self):
        """Create watchlist tables if they don't exist"""
        conn = self.get_connection()
        cur = conn.cursor()

        try:
            # Master watchlists table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS tv_watchlists (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) UNIQUE NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_refresh TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    symbol_count INTEGER DEFAULT 0
                )
            """)

            # Watchlist symbols table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS tv_watchlist_symbols (
                    id SERIAL PRIMARY KEY,
                    watchlist_id INTEGER REFERENCES tv_watchlists(id) ON DELETE CASCADE,
                    symbol VARCHAR(20) NOT NULL,
                    company_name VARCHAR(255),
                    sector VARCHAR(100),
                    industry VARCHAR(100),
                    market_cap BIGINT,
                    last_price DECIMAL(10,2),
                    volume BIGINT,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(watchlist_id, symbol)
                )
            """)

            # Watchlist refresh history
            cur.execute("""
                CREATE TABLE IF NOT EXISTS tv_refresh_history (
                    id SERIAL PRIMARY KEY,
                    watchlist_id INTEGER REFERENCES tv_watchlists(id) ON DELETE CASCADE,
                    refresh_type VARCHAR(50), -- 'manual', 'scheduled', 'auto'
                    status VARCHAR(50), -- 'success', 'failed', 'partial'
                    symbols_added INTEGER DEFAULT 0,
                    symbols_removed INTEGER DEFAULT 0,
                    symbols_updated INTEGER DEFAULT 0,
                    error_message TEXT,
                    refresh_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create indexes for performance
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_watchlist_symbols_symbol
                ON tv_watchlist_symbols(symbol);
            """)

            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_watchlist_symbols_watchlist
                ON tv_watchlist_symbols(watchlist_id);
            """)

            conn.commit()
            logger.info("Database tables initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing tables: {e}")
            conn.rollback()
        finally:
            cur.close()
            conn.close()

    def create_watchlist(self, name: str, description: str = None) -> Optional[int]:
        """Create a new watchlist"""
        conn = self.get_connection()
        cur = conn.cursor()

        try:
            cur.execute("""
                INSERT INTO tv_watchlists (name, description)
                VALUES (%s, %s)
                ON CONFLICT (name)
                DO UPDATE SET updated_at = CURRENT_TIMESTAMP
                RETURNING id
            """, (name, description))

            watchlist_id = cur.fetchone()[0]
            conn.commit()
            logger.info(f"Created/updated watchlist '{name}' with ID {watchlist_id}")
            return watchlist_id

        except Exception as e:
            logger.error(f"Error creating watchlist: {e}")
            conn.rollback()
            return None
        finally:
            cur.close()
            conn.close()

    def add_symbols_to_watchlist(self, watchlist_id: int, symbols: List[str]) -> int:
        """Add symbols to a watchlist and fetch their data"""
        conn = self.get_connection()
        cur = conn.cursor()
        added_count = 0

        try:
            for symbol in symbols:
                symbol = symbol.upper().strip()

                # Fetch stock data from Yahoo Finance
                try:
                    ticker = yf.Ticker(symbol)
                    info = ticker.info

                    # Extract relevant data
                    company_name = info.get('longName', info.get('shortName', symbol))
                    sector = info.get('sector', 'Unknown')
                    industry = info.get('industry', 'Unknown')
                    market_cap = info.get('marketCap', 0)
                    last_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
                    volume = info.get('volume', info.get('regularMarketVolume', 0))

                except Exception as e:
                    logger.warning(f"Could not fetch data for {symbol}: {e}")
                    company_name = symbol
                    sector = 'Unknown'
                    industry = 'Unknown'
                    market_cap = 0
                    last_price = 0
                    volume = 0

                # Insert or update symbol
                cur.execute("""
                    INSERT INTO tv_watchlist_symbols
                    (watchlist_id, symbol, company_name, sector, industry,
                     market_cap, last_price, volume)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (watchlist_id, symbol)
                    DO UPDATE SET
                        company_name = EXCLUDED.company_name,
                        sector = EXCLUDED.sector,
                        industry = EXCLUDED.industry,
                        market_cap = EXCLUDED.market_cap,
                        last_price = EXCLUDED.last_price,
                        volume = EXCLUDED.volume,
                        updated_at = CURRENT_TIMESTAMP
                """, (watchlist_id, symbol, company_name, sector, industry,
                      market_cap, last_price, volume))

                added_count += 1

            # Update watchlist metadata
            cur.execute("""
                UPDATE tv_watchlists
                SET symbol_count = (
                    SELECT COUNT(*) FROM tv_watchlist_symbols
                    WHERE watchlist_id = %s
                ),
                last_refresh = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (watchlist_id, watchlist_id))

            conn.commit()
            logger.info(f"Added/updated {added_count} symbols to watchlist {watchlist_id}")
            return added_count

        except Exception as e:
            logger.error(f"Error adding symbols to watchlist: {e}")
            conn.rollback()
            return 0
        finally:
            cur.close()
            conn.close()

    def get_all_watchlists(self) -> List[Dict[str, Any]]:
        """Get all watchlists with their metadata"""
        conn = self.get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        try:
            cur.execute("""
                SELECT id, name, description, symbol_count,
                       last_refresh, created_at, updated_at, is_active
                FROM tv_watchlists
                WHERE is_active = TRUE
                ORDER BY name
            """)

            watchlists = cur.fetchall()
            return list(watchlists)

        except Exception as e:
            logger.error(f"Error fetching watchlists: {e}")
            return []
        finally:
            cur.close()
            conn.close()

    def get_watchlist_symbols(self, watchlist_name: str) -> List[str]:
        """Get all symbols in a watchlist"""
        conn = self.get_connection()
        cur = conn.cursor()

        try:
            cur.execute("""
                SELECT ws.symbol
                FROM tv_watchlist_symbols ws
                JOIN tv_watchlists w ON w.id = ws.watchlist_id
                WHERE w.name = %s AND w.is_active = TRUE
                ORDER BY ws.symbol
            """, (watchlist_name,))

            symbols = [row[0] for row in cur.fetchall()]
            return symbols

        except Exception as e:
            logger.error(f"Error fetching watchlist symbols: {e}")
            return []
        finally:
            cur.close()
            conn.close()

    def get_watchlist_details(self, watchlist_name: str) -> List[Dict[str, Any]]:
        """Get detailed information for all symbols in a watchlist"""
        conn = self.get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        try:
            cur.execute("""
                SELECT ws.*
                FROM tv_watchlist_symbols ws
                JOIN tv_watchlists w ON w.id = ws.watchlist_id
                WHERE w.name = %s AND w.is_active = TRUE
                ORDER BY ws.symbol
            """, (watchlist_name,))

            symbols = cur.fetchall()
            return list(symbols)

        except Exception as e:
            logger.error(f"Error fetching watchlist details: {e}")
            return []
        finally:
            cur.close()
            conn.close()

    def refresh_watchlist(self, watchlist_name: str, symbols: List[str],
                         refresh_type: str = 'manual') -> bool:
        """Refresh a watchlist with new symbols"""
        conn = self.get_connection()
        cur = conn.cursor()

        try:
            # Get watchlist ID
            cur.execute("""
                SELECT id FROM tv_watchlists WHERE name = %s
            """, (watchlist_name,))

            result = cur.fetchone()
            if not result:
                # Create new watchlist
                watchlist_id = self.create_watchlist(watchlist_name)
            else:
                watchlist_id = result[0]

            if not watchlist_id:
                return False

            # Get current symbols
            cur.execute("""
                SELECT symbol FROM tv_watchlist_symbols
                WHERE watchlist_id = %s
            """, (watchlist_id,))

            current_symbols = set(row[0] for row in cur.fetchall())
            new_symbols = set(s.upper().strip() for s in symbols)

            # Calculate changes
            added = new_symbols - current_symbols
            removed = current_symbols - new_symbols

            # Remove old symbols
            if removed:
                cur.execute("""
                    DELETE FROM tv_watchlist_symbols
                    WHERE watchlist_id = %s AND symbol = ANY(%s)
                """, (watchlist_id, list(removed)))

            # Add new symbols
            if added:
                self.add_symbols_to_watchlist(watchlist_id, list(added))

            # Log refresh history
            cur.execute("""
                INSERT INTO tv_refresh_history
                (watchlist_id, refresh_type, status, symbols_added,
                 symbols_removed, symbols_updated)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (watchlist_id, refresh_type, 'success',
                  len(added), len(removed), len(new_symbols & current_symbols)))

            conn.commit()
            logger.info(f"Refreshed watchlist '{watchlist_name}': "
                       f"+{len(added)} -{len(removed)} symbols")
            return True

        except Exception as e:
            logger.error(f"Error refreshing watchlist: {e}")
            conn.rollback()
            return False
        finally:
            cur.close()
            conn.close()

    def delete_watchlist(self, watchlist_name: str) -> bool:
        """Delete a watchlist (soft delete)"""
        conn = self.get_connection()
        cur = conn.cursor()

        try:
            cur.execute("""
                UPDATE tv_watchlists
                SET is_active = FALSE, updated_at = CURRENT_TIMESTAMP
                WHERE name = %s
            """, (watchlist_name,))

            conn.commit()
            return True

        except Exception as e:
            logger.error(f"Error deleting watchlist: {e}")
            conn.rollback()
            return False
        finally:
            cur.close()
            conn.close()

    def get_all_symbols_dict(self) -> Dict[str, List[str]]:
        """Get all watchlists as a dictionary from TradingView API sync"""
        conn = self.get_connection()
        cur = conn.cursor()

        try:
            # First try from tv_watchlists_api (TradingView synced data)
            cur.execute("""
                SELECT w.name, ARRAY_AGG(s.symbol ORDER BY s.symbol) as symbols
                FROM tv_watchlists_api w
                LEFT JOIN tv_symbols_api s ON w.watchlist_id = s.watchlist_id
                GROUP BY w.name, w.symbol_count
                ORDER BY w.symbol_count DESC, w.name
            """)

            watchlists = {}
            rows = cur.fetchall()

            if rows:
                for name, symbols in rows:
                    watchlists[name] = symbols if symbols and symbols[0] is not None else []
                return watchlists

            # Fallback to old table if API table is empty
            cur.execute("""
                SELECT w.name, ARRAY_AGG(ws.symbol ORDER BY ws.symbol) as symbols
                FROM tv_watchlists w
                LEFT JOIN tv_watchlist_symbols ws ON w.id = ws.watchlist_id
                WHERE w.is_active = TRUE
                GROUP BY w.name
                ORDER BY w.name
            """)

            for name, symbols in cur.fetchall():
                watchlists[name] = symbols if symbols and symbols[0] is not None else []

            return watchlists

        except Exception as e:
            logger.error(f"Error fetching all watchlists: {e}")
            return {}
        finally:
            cur.close()
            conn.close()

    def needs_refresh(self, watchlist_name: str, hours: int = 24) -> bool:
        """Check if a watchlist needs refresh based on time"""
        conn = self.get_connection()
        cur = conn.cursor()

        try:
            cur.execute("""
                SELECT last_refresh FROM tv_watchlists
                WHERE name = %s AND is_active = TRUE
            """, (watchlist_name,))

            result = cur.fetchone()
            if not result or not result[0]:
                return True

            last_refresh = result[0]
            time_since = datetime.now() - last_refresh

            return time_since > timedelta(hours=hours)

        except Exception as e:
            logger.error(f"Error checking refresh status: {e}")
            return True
        finally:
            cur.close()
            conn.close()

    def import_from_text(self, text: str, watchlist_name: str) -> List[str]:
        """Import symbols from text (comma or newline separated)"""
        # Parse symbols from text
        symbols = []

        # Replace common separators with commas
        text = text.replace('\n', ',').replace(';', ',').replace('\t', ',')

        # Split and clean
        for item in text.split(','):
            symbol = item.strip().upper()
            # Basic validation - symbols are typically 1-5 characters
            if symbol and len(symbol) <= 5 and symbol.replace('-', '').isalnum():
                symbols.append(symbol)

        if symbols:
            # Create or update watchlist
            watchlist_id = self.create_watchlist(watchlist_name)
            if watchlist_id:
                # Refresh with new symbols
                self.refresh_watchlist(watchlist_name, symbols, 'manual')

        return symbols

    def load_saved_watchlists(self) -> Dict[str, List[str]]:
        """Load all saved watchlists from database"""
        return self.get_all_symbols_dict()