"""
Unified Database Connection Pool for Magnus
Prevents connection exhaustion and provides connection reuse

Usage:
    from src.database import get_db_connection

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM stocks")
        results = cursor.fetchall()
"""

import os
import logging
from contextlib import contextmanager
from typing import Optional, Dict
from psycopg2 import pool
from psycopg2.extensions import connection as Connection
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


class DatabaseConnectionPool:
    """
    Thread-safe singleton connection pool for PostgreSQL

    Features:
    - Connection reuse (prevents connection exhaustion)
    - Automatic connection cleanup
    - Health monitoring and statistics
    - Thread-safe operations
    """

    _instance: Optional['DatabaseConnectionPool'] = None
    _pool: Optional[pool.ThreadedConnectionPool] = None
    _stats: Dict[str, int] = {
        'connections_created': 0,
        'connections_reused': 0,
        'connections_closed': 0,
        'active_connections': 0,
        'errors': 0
    }

    def __new__(cls):
        """Singleton pattern - only one pool instance"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._initialize_pool()
        return cls._instance

    @classmethod
    def _initialize_pool(cls):
        """Initialize the connection pool with environment configuration"""
        try:
            cls._pool = pool.ThreadedConnectionPool(
                minconn=2,  # Minimum idle connections
                maxconn=20,  # Maximum connections (reduced from 50 to prevent exhaustion)
                host=os.getenv("DB_HOST", "localhost"),
                port=int(os.getenv("DB_PORT", 5432)),
                database=os.getenv("DB_NAME", "magnus"),
                user=os.getenv("DB_USER", "postgres"),
                password=os.getenv("DB_PASSWORD", ""),
                # Connection settings for better stability
                connect_timeout=10,
                options="-c statement_timeout=30000"  # 30 second query timeout
            )
            cls._stats['connections_created'] = 2  # Initial minconn
            logger.info(f"Database connection pool initialized (min=2, max=20)")
        except Exception as e:
            logger.error(f"Failed to initialize connection pool: {e}")
            raise

    @contextmanager
    def get_connection(self):
        """
        Get a database connection from the pool

        Automatically handles:
        - Connection acquisition
        - Transaction commit on success
        - Transaction rollback on error
        - Connection return to pool

        Example:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM stocks")
                return cursor.fetchall()
        """
        conn = None
        try:
            # Get connection from pool
            conn = self._pool.getconn()
            self._stats['connections_reused'] += 1
            self._stats['active_connections'] += 1

            yield conn

            # Commit transaction on success
            conn.commit()

        except Exception as e:
            # Rollback on error
            if conn:
                conn.rollback()
            self._stats['errors'] += 1
            logger.error(f"Database error: {e}")
            raise

        finally:
            # Always return connection to pool
            if conn:
                self._pool.putconn(conn)
                self._stats['active_connections'] -= 1

    def get_stats(self) -> Dict[str, int]:
        """Get connection pool statistics"""
        return {
            **self._stats,
            'pool_size': len(self._pool._pool) if self._pool else 0,
            'available': len(self._pool._pool) - self._stats['active_connections'] if self._pool else 0
        }

    def close_all(self):
        """Close all connections in the pool (for cleanup/testing)"""
        if self._pool:
            self._pool.closeall()
            logger.info("All database connections closed")


# Global pool instance
_pool_instance = None


def get_db_connection():
    """
    Convenient function to get a database connection

    Usage:
        from src.database import get_db_connection

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM stocks")
            return cursor.fetchall()
    """
    global _pool_instance
    if _pool_instance is None:
        _pool_instance = DatabaseConnectionPool()
    return _pool_instance.get_connection()


def get_pool_stats() -> Dict[str, int]:
    """Get connection pool statistics"""
    global _pool_instance
    if _pool_instance is None:
        _pool_instance = DatabaseConnectionPool()
    return _pool_instance.get_stats()


# Backward compatibility wrapper
class LegacyDBManager:
    """
    Compatibility wrapper for existing code that uses:
        db = DBManager()
        conn = db.get_connection()

    Migrates to pooled connections automatically
    """
    def __init__(self):
        global _pool_instance
        if _pool_instance is None:
            _pool_instance = DatabaseConnectionPool()
        self._pool = _pool_instance

    def get_connection(self) -> Connection:
        """
        Legacy method - returns a connection (not recommended, use context manager)
        WARNING: Caller must manually return connection with putconn()
        """
        logger.warning("Using legacy get_connection() - migrate to context manager")
        return self._pool._pool.getconn()

    def putconn(self, conn: Connection):
        """Return connection to pool"""
        self._pool._pool.putconn(conn)
