"""
Feature Store for Kalshi Prediction Markets

Versioned storage and retrieval of computed features for ML training and prediction.
Uses PostgreSQL with JSONB for flexible feature storage and fast retrieval.
"""

import os
import psycopg2
import psycopg2.extras
import pandas as pd
import numpy as np
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FeatureStore:
    """Manages feature storage and retrieval with versioning"""

    def __init__(self, db_config: Optional[Dict] = None):
        """
        Initialize feature store.

        Args:
            db_config: Database configuration dict. If None, uses default.
        """
        self.db_config = db_config or {
            'host': 'localhost',
            'port': '5432',
            'database': 'magnus',
            'user': 'postgres',
            'password': os.getenv('DB_PASSWORD')
        }
        self._cache = {}  # In-memory cache for frequently accessed features

    def get_connection(self):
        """Get database connection"""
        return psycopg2.connect(**self.db_config)

    def store_features(self, market_id: int, ticker: str, features: Dict[str, Any],
                      feature_version: str = "v1.0", feature_set: str = "base",
                      market_type: Optional[str] = None,
                      close_time: Optional[datetime] = None) -> bool:
        """
        Store computed features for a market.

        Args:
            market_id: Market database ID
            ticker: Market ticker
            features: Dictionary of computed features
            feature_version: Version string (e.g., 'v1.0', 'v2.0')
            feature_set: Feature set name (e.g., 'base', 'advanced', 'ensemble')
            market_type: Market type for filtering
            close_time: Market close time

        Returns:
            True if successful
        """
        conn = self.get_connection()
        cur = conn.cursor()

        try:
            # Convert features to JSONB-compatible format
            features_json = self._serialize_features(features)
            feature_names = list(features.keys())
            feature_count = len(feature_names)

            cur.execute("""
                INSERT INTO feature_store (
                    market_id, ticker, feature_version, feature_set,
                    features, feature_names, feature_count,
                    market_type, close_time
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (market_id, feature_version, feature_set) DO UPDATE SET
                    features = EXCLUDED.features,
                    feature_names = EXCLUDED.feature_names,
                    feature_count = EXCLUDED.feature_count,
                    computed_at = NOW()
            """, (
                market_id, ticker, feature_version, feature_set,
                json.dumps(features_json), feature_names, feature_count,
                market_type, close_time
            ))

            conn.commit()
            logger.debug(f"Stored {feature_count} features for {ticker} ({feature_set} {feature_version})")
            return True

        except Exception as e:
            conn.rollback()
            logger.error(f"Error storing features for {ticker}: {e}")
            return False

        finally:
            cur.close()
            conn.close()

    def get_features(self, ticker: str, feature_version: str = "v1.0",
                    feature_set: str = "base", use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """
        Retrieve features for a market.

        Args:
            ticker: Market ticker
            feature_version: Version string
            feature_set: Feature set name
            use_cache: Use in-memory cache if available

        Returns:
            Dictionary of features or None if not found
        """
        cache_key = f"{ticker}:{feature_version}:{feature_set}"

        # Check cache
        if use_cache and cache_key in self._cache:
            logger.debug(f"Cache hit for {cache_key}")
            return self._cache[cache_key]

        conn = self.get_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        try:
            cur.execute("""
                SELECT features
                FROM feature_store
                WHERE ticker = %s
                  AND feature_version = %s
                  AND feature_set = %s
            """, (ticker, feature_version, feature_set))

            result = cur.fetchone()

            if result:
                features = dict(result['features'])
                features = self._deserialize_features(features)

                # Update cache
                if use_cache:
                    self._cache[cache_key] = features

                return features

            return None

        finally:
            cur.close()
            conn.close()

    def get_features_bulk(self, tickers: List[str], feature_version: str = "v1.0",
                         feature_set: str = "base") -> Dict[str, Dict[str, Any]]:
        """
        Retrieve features for multiple markets at once.

        Args:
            tickers: List of market tickers
            feature_version: Version string
            feature_set: Feature set name

        Returns:
            Dictionary mapping ticker -> features
        """
        if not tickers:
            return {}

        conn = self.get_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        try:
            cur.execute("""
                SELECT ticker, features
                FROM feature_store
                WHERE ticker = ANY(%s)
                  AND feature_version = %s
                  AND feature_set = %s
            """, (tickers, feature_version, feature_set))

            results = cur.fetchall()

            features_dict = {}
            for row in results:
                ticker = row['ticker']
                features = dict(row['features'])
                features_dict[ticker] = self._deserialize_features(features)

            return features_dict

        finally:
            cur.close()
            conn.close()

    def get_features_dataframe(self, feature_version: str = "v1.0",
                              feature_set: str = "base",
                              market_type: Optional[str] = None,
                              start_date: Optional[datetime] = None,
                              end_date: Optional[datetime] = None) -> pd.DataFrame:
        """
        Get features as a DataFrame for ML training.

        Args:
            feature_version: Version string
            feature_set: Feature set name
            market_type: Filter by market type
            start_date: Filter by close time >= start_date
            end_date: Filter by close time <= end_date

        Returns:
            DataFrame with features
        """
        conn = self.get_connection()

        query = """
            SELECT
                ticker,
                market_id,
                market_type,
                close_time,
                features,
                computed_at
            FROM feature_store
            WHERE feature_version = %s
              AND feature_set = %s
        """

        params = [feature_version, feature_set]

        if market_type:
            query += " AND market_type = %s"
            params.append(market_type)

        if start_date:
            query += " AND close_time >= %s"
            params.append(start_date)

        if end_date:
            query += " AND close_time <= %s"
            params.append(end_date)

        query += " ORDER BY close_time"

        try:
            df = pd.read_sql_query(query, conn, params=params)

            if df.empty:
                return pd.DataFrame()

            # Expand JSONB features into columns
            features_df = pd.json_normalize(df['features'])

            # Combine with metadata
            result_df = pd.concat([
                df[['ticker', 'market_id', 'market_type', 'close_time', 'computed_at']].reset_index(drop=True),
                features_df
            ], axis=1)

            return result_df

        finally:
            conn.close()

    def delete_features(self, ticker: str, feature_version: Optional[str] = None,
                       feature_set: Optional[str] = None) -> int:
        """
        Delete features for a market.

        Args:
            ticker: Market ticker
            feature_version: Version string (None = all versions)
            feature_set: Feature set name (None = all sets)

        Returns:
            Number of records deleted
        """
        conn = self.get_connection()
        cur = conn.cursor()

        try:
            query = "DELETE FROM feature_store WHERE ticker = %s"
            params = [ticker]

            if feature_version:
                query += " AND feature_version = %s"
                params.append(feature_version)

            if feature_set:
                query += " AND feature_set = %s"
                params.append(feature_set)

            cur.execute(query, params)
            deleted_count = cur.rowcount

            conn.commit()

            # Clear cache
            self._clear_cache(ticker)

            logger.info(f"Deleted {deleted_count} feature records for {ticker}")
            return deleted_count

        except Exception as e:
            conn.rollback()
            logger.error(f"Error deleting features for {ticker}: {e}")
            return 0

        finally:
            cur.close()
            conn.close()

    def list_versions(self) -> List[str]:
        """List all feature versions in the store"""
        conn = self.get_connection()
        cur = conn.cursor()

        try:
            cur.execute("""
                SELECT DISTINCT feature_version
                FROM feature_store
                ORDER BY feature_version DESC
            """)

            versions = [row[0] for row in cur.fetchall()]
            return versions

        finally:
            cur.close()
            conn.close()

    def list_feature_sets(self, feature_version: Optional[str] = None) -> List[str]:
        """List all feature sets, optionally filtered by version"""
        conn = self.get_connection()
        cur = conn.cursor()

        try:
            if feature_version:
                cur.execute("""
                    SELECT DISTINCT feature_set
                    FROM feature_store
                    WHERE feature_version = %s
                    ORDER BY feature_set
                """, (feature_version,))
            else:
                cur.execute("""
                    SELECT DISTINCT feature_set
                    FROM feature_store
                    ORDER BY feature_set
                """)

            feature_sets = [row[0] for row in cur.fetchall()]
            return feature_sets

        finally:
            cur.close()
            conn.close()

    def get_feature_names(self, feature_version: str = "v1.0",
                         feature_set: str = "base") -> List[str]:
        """Get list of feature names for a version/set"""
        conn = self.get_connection()
        cur = conn.cursor()

        try:
            cur.execute("""
                SELECT feature_names
                FROM feature_store
                WHERE feature_version = %s
                  AND feature_set = %s
                LIMIT 1
            """, (feature_version, feature_set))

            result = cur.fetchone()
            return result[0] if result else []

        finally:
            cur.close()
            conn.close()

    def get_stats(self) -> Dict[str, Any]:
        """Get feature store statistics"""
        conn = self.get_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        try:
            stats = {}

            # Total features
            cur.execute("SELECT COUNT(*) as total FROM feature_store")
            stats['total_records'] = cur.fetchone()['total']

            # By version
            cur.execute("""
                SELECT feature_version, COUNT(*) as count
                FROM feature_store
                GROUP BY feature_version
                ORDER BY feature_version DESC
            """)
            stats['by_version'] = {row['feature_version']: row['count'] for row in cur.fetchall()}

            # By feature set
            cur.execute("""
                SELECT feature_set, COUNT(*) as count
                FROM feature_store
                GROUP BY feature_set
                ORDER BY count DESC
            """)
            stats['by_feature_set'] = {row['feature_set']: row['count'] for row in cur.fetchall()}

            # Average feature count
            cur.execute("SELECT AVG(feature_count) as avg_count FROM feature_store")
            result = cur.fetchone()
            stats['avg_feature_count'] = float(result['avg_count']) if result['avg_count'] else 0

            # Latest computation
            cur.execute("""
                SELECT MAX(computed_at) as latest
                FROM feature_store
            """)
            result = cur.fetchone()
            stats['latest_computation'] = result['latest']

            return stats

        finally:
            cur.close()
            conn.close()

    def clear_cache(self):
        """Clear the in-memory cache"""
        self._cache.clear()
        logger.info("Feature cache cleared")

    def _clear_cache(self, ticker: str):
        """Clear cache entries for a specific ticker"""
        keys_to_remove = [k for k in self._cache.keys() if k.startswith(f"{ticker}:")]
        for key in keys_to_remove:
            del self._cache[key]

    def _serialize_features(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Convert features to JSON-serializable format"""
        serialized = {}
        for key, value in features.items():
            if isinstance(value, (np.integer, np.floating)):
                serialized[key] = float(value)
            elif isinstance(value, np.ndarray):
                serialized[key] = value.tolist()
            elif pd.isna(value):
                serialized[key] = None
            else:
                serialized[key] = value
        return serialized

    def _deserialize_features(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Convert JSON features back to appropriate types"""
        # Currently just returns as-is, but can add custom deserialization logic
        return features

    def compute_and_store_features(self, market_id: int, ticker: str,
                                  market_data: Dict[str, Any],
                                  feature_version: str = "v1.0",
                                  feature_set: str = "base") -> bool:
        """
        Compute and store features for a market.

        This is a convenience method that computes features and stores them.

        Args:
            market_id: Market database ID
            ticker: Market ticker
            market_data: Raw market data dictionary
            feature_version: Version string
            feature_set: Feature set name

        Returns:
            True if successful
        """
        # Compute features based on market data
        features = self._compute_features(market_data, feature_set)

        # Store features
        return self.store_features(
            market_id=market_id,
            ticker=ticker,
            features=features,
            feature_version=feature_version,
            feature_set=feature_set,
            market_type=market_data.get('market_type'),
            close_time=market_data.get('close_time')
        )

    def _compute_features(self, market_data: Dict[str, Any], feature_set: str) -> Dict[str, Any]:
        """
        Compute features from raw market data.

        This is a placeholder. In production, you'd implement specific
        feature engineering logic here.

        Args:
            market_data: Raw market data
            feature_set: Feature set to compute

        Returns:
            Dictionary of computed features
        """
        features = {}

        if feature_set == "base":
            # Basic features
            features['yes_price'] = market_data.get('yes_price', 0.5)
            features['no_price'] = market_data.get('no_price', 0.5)
            features['volume'] = market_data.get('volume', 0)
            features['open_interest'] = market_data.get('open_interest', 0)

            # Derived features
            yes_price = features['yes_price']
            features['implied_prob'] = yes_price
            features['log_odds'] = np.log(yes_price / (1 - yes_price)) if 0 < yes_price < 1 else 0

        elif feature_set == "advanced":
            # Advanced features (placeholder)
            features['price_momentum'] = 0.0
            features['volume_profile'] = 0.0
            features['liquidity_score'] = 0.0

        # Handle missing values
        features = self._handle_missing_values(features)

        return features

    def _handle_missing_values(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle missing values in features.

        Args:
            features: Dictionary of features

        Returns:
            Features with missing values handled
        """
        for key, value in features.items():
            if value is None or (isinstance(value, float) and np.isnan(value)):
                # Replace with 0 or appropriate default
                features[key] = 0.0

        return features


if __name__ == "__main__":
    # Test feature store
    print("="*80)
    print("FEATURE STORE - Test")
    print("="*80)

    store = FeatureStore()

    # Test storing features
    test_features = {
        'yes_price': 0.65,
        'no_price': 0.35,
        'volume': 1000.0,
        'open_interest': 500,
        'implied_prob': 0.65,
        'log_odds': 0.619,
    }

    success = store.store_features(
        market_id=1,
        ticker="TEST-001",
        features=test_features,
        feature_version="v1.0",
        feature_set="base",
        market_type="nfl"
    )

    print(f"\nStore features: {'Success' if success else 'Failed'}")

    # Test retrieving features
    retrieved = store.get_features("TEST-001", "v1.0", "base")
    print(f"\nRetrieved features: {retrieved}")

    # Test stats
    stats = store.get_stats()
    print(f"\nFeature Store Stats:")
    print(f"  Total Records: {stats['total_records']}")
    print(f"  Versions: {stats['by_version']}")
    print(f"  Feature Sets: {stats['by_feature_set']}")
    print(f"  Avg Features: {stats['avg_feature_count']:.1f}")

    # Test list versions
    versions = store.list_versions()
    print(f"\nAvailable Versions: {versions}")

    # Test list feature sets
    feature_sets = store.list_feature_sets()
    print(f"Available Feature Sets: {feature_sets}")

    print("\n" + "="*80)
    print("Test Complete!")
    print("="*80)
