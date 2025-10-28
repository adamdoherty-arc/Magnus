"""Database Scanner - Pull and analyze stocks from PostgreSQL database"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import yfinance as yf
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseScanner:
    """Scan PostgreSQL database for stocks and analyze option premiums"""

    def __init__(self):
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'wheel_strategy'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'postgres123!')
        }
        self.conn = None
        self.cursor = None

    def connect(self):
        """Connect to PostgreSQL database"""
        try:
            self.conn = psycopg2.connect(**self.db_config)
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            return True
        except Exception as e:
            print(f"Database connection error: {e}")
            return False

    def disconnect(self):
        """Disconnect from database"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def create_tables(self):
        """Create necessary tables if they don't exist"""
        try:
            # Create stocks table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS stocks (
                    id SERIAL PRIMARY KEY,
                    symbol VARCHAR(10) UNIQUE NOT NULL,
                    name VARCHAR(255),
                    sector VARCHAR(100),
                    industry VARCHAR(100),
                    market_cap BIGINT,
                    current_price DECIMAL(10,2),
                    avg_volume BIGINT,
                    last_updated TIMESTAMP DEFAULT NOW()
                )
            """)

            # Create options_data table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS options_data (
                    id SERIAL PRIMARY KEY,
                    symbol VARCHAR(10) NOT NULL,
                    expiration_date DATE,
                    strike_price DECIMAL(10,2),
                    option_type VARCHAR(4),
                    bid DECIMAL(10,2),
                    ask DECIMAL(10,2),
                    volume INTEGER,
                    open_interest INTEGER,
                    implied_volatility DECIMAL(5,2),
                    last_updated TIMESTAMP DEFAULT NOW(),
                    FOREIGN KEY (symbol) REFERENCES stocks(symbol)
                )
            """)

            # Create watchlist table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS watchlist (
                    id SERIAL PRIMARY KEY,
                    symbol VARCHAR(10) NOT NULL,
                    added_date TIMESTAMP DEFAULT NOW(),
                    notes TEXT,
                    target_price DECIMAL(10,2),
                    stop_loss DECIMAL(10,2),
                    FOREIGN KEY (symbol) REFERENCES stocks(symbol)
                )
            """)

            # Create trade_history table
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS trade_history (
                    id SERIAL PRIMARY KEY,
                    symbol VARCHAR(10) NOT NULL,
                    trade_type VARCHAR(20),
                    quantity INTEGER,
                    price DECIMAL(10,2),
                    premium DECIMAL(10,2),
                    trade_date TIMESTAMP DEFAULT NOW(),
                    expiration_date DATE,
                    strike_price DECIMAL(10,2),
                    status VARCHAR(20),
                    profit_loss DECIMAL(10,2)
                )
            """)

            self.conn.commit()
            return True

        except Exception as e:
            print(f"Error creating tables: {e}")
            self.conn.rollback()
            return False

    def add_stock(self, symbol: str, fetch_data: bool = True) -> bool:
        """Add a stock to the database"""
        try:
            if fetch_data:
                # Fetch stock data from yfinance
                ticker = yf.Ticker(symbol.upper())
                info = ticker.info

                name = info.get('longName', symbol)
                sector = info.get('sector', 'Unknown')
                industry = info.get('industry', 'Unknown')
                market_cap = info.get('marketCap', 0)
                current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)
                avg_volume = info.get('averageVolume', 0)

            else:
                name = symbol
                sector = 'Unknown'
                industry = 'Unknown'
                market_cap = 0
                current_price = 0
                avg_volume = 0

            # Insert or update stock
            self.cursor.execute("""
                INSERT INTO stocks (symbol, name, sector, industry, market_cap, current_price, avg_volume)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (symbol) DO UPDATE SET
                    name = EXCLUDED.name,
                    sector = EXCLUDED.sector,
                    industry = EXCLUDED.industry,
                    market_cap = EXCLUDED.market_cap,
                    current_price = EXCLUDED.current_price,
                    avg_volume = EXCLUDED.avg_volume,
                    last_updated = NOW()
            """, (symbol.upper(), name, sector, industry, market_cap, current_price, avg_volume))

            self.conn.commit()
            return True

        except Exception as e:
            print(f"Error adding stock {symbol}: {e}")
            self.conn.rollback()
            return False

    def bulk_add_stocks(self, symbols: List[str]) -> int:
        """Add multiple stocks to the database"""
        added = 0
        for symbol in symbols:
            if self.add_stock(symbol):
                added += 1
                print(f"Added {symbol} to database")
        return added

    def get_all_stocks(self) -> List[Dict]:
        """Get all stocks from database"""
        try:
            self.cursor.execute("""
                SELECT * FROM stocks
                ORDER BY symbol
            """)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error fetching stocks: {e}")
            return []

    def get_stocks_by_criteria(self,
                               max_price: Optional[float] = None,
                               min_volume: Optional[int] = None,
                               sector: Optional[str] = None) -> List[Dict]:
        """Get stocks matching specific criteria"""
        try:
            query = "SELECT * FROM stocks WHERE 1=1"
            params = []

            if max_price:
                query += " AND current_price <= %s"
                params.append(max_price)

            if min_volume:
                query += " AND avg_volume >= %s"
                params.append(min_volume)

            if sector:
                query += " AND sector = %s"
                params.append(sector)

            query += " ORDER BY symbol"

            self.cursor.execute(query, params)
            return self.cursor.fetchall()

        except Exception as e:
            print(f"Error fetching filtered stocks: {e}")
            return []

    def update_stock_prices(self) -> int:
        """Update all stock prices in database"""
        updated = 0
        stocks = self.get_all_stocks()

        for stock in stocks:
            try:
                ticker = yf.Ticker(stock['symbol'])
                info = ticker.info
                current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0)

                if current_price > 0:
                    self.cursor.execute("""
                        UPDATE stocks
                        SET current_price = %s, last_updated = NOW()
                        WHERE symbol = %s
                    """, (current_price, stock['symbol']))
                    updated += 1

            except Exception as e:
                print(f"Error updating {stock['symbol']}: {e}")

        self.conn.commit()
        return updated

    def save_option_data(self, symbol: str, expiration: str, option_data: Dict) -> bool:
        """Save option data to database"""
        try:
            self.cursor.execute("""
                INSERT INTO options_data
                (symbol, expiration_date, strike_price, option_type, bid, ask, volume, open_interest, implied_volatility)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                symbol,
                expiration,
                option_data.get('strike', 0),
                option_data.get('type', 'PUT'),
                option_data.get('bid', 0),
                option_data.get('ask', 0),
                option_data.get('volume', 0),
                option_data.get('openInterest', 0),
                option_data.get('impliedVolatility', 0) * 100 if option_data.get('impliedVolatility') else 0
            ))
            self.conn.commit()
            return True

        except Exception as e:
            print(f"Error saving option data: {e}")
            self.conn.rollback()
            return False

    def get_stocks_with_best_premiums(self, max_price: float = 50, days_to_expiry: int = 30) -> List[Dict]:
        """Get stocks with best option premiums from database"""
        stocks = self.get_stocks_by_criteria(max_price=max_price)
        results = []

        for stock in stocks:
            try:
                symbol = stock['symbol']
                current_price = stock['current_price']

                if current_price <= 0:
                    continue

                ticker = yf.Ticker(symbol)
                expirations = ticker.options

                if not expirations:
                    continue

                # Find expiration closest to target days
                target_date = datetime.now() + timedelta(days=days_to_expiry)
                best_expiry = None
                min_diff = float('inf')

                for exp in expirations:
                    exp_date = datetime.strptime(exp, '%Y-%m-%d')
                    diff = abs((exp_date - target_date).days)
                    if diff < min_diff:
                        min_diff = diff
                        best_expiry = exp

                if best_expiry:
                    opt_chain = ticker.option_chain(best_expiry)
                    puts = opt_chain.puts

                    # Find 5% OTM put
                    target_strike = current_price * 0.95
                    otm_puts = puts[puts['strike'] <= target_strike]

                    if not otm_puts.empty:
                        best_put = otm_puts.iloc[-1]

                        strike = best_put['strike']
                        bid = best_put['bid']
                        ask = best_put['ask']
                        premium = (bid + ask) / 2 if bid > 0 and ask > 0 else bid

                        if premium > 0:
                            return_pct = (premium * 100 / (strike * 100)) * 100

                            results.append({
                                'symbol': symbol,
                                'name': stock['name'],
                                'sector': stock['sector'],
                                'current_price': current_price,
                                'strike': strike,
                                'premium': premium,
                                'return_pct': return_pct,
                                'expiration': best_expiry,
                                'days_to_expiry': min_diff
                            })

            except Exception as e:
                print(f"Error processing {symbol}: {e}")

        # Sort by return percentage
        results.sort(key=lambda x: x['return_pct'], reverse=True)
        return results[:20]  # Return top 20

    def initialize_default_stocks(self):
        """Initialize database - no default stocks"""
        # No default stocks - user must add their own
        return 0