# Magnus Financial Assistant - Connector Implementation Guide

**Quick Reference for Developers**
**Date:** January 10, 2025

---

## Overview

This guide shows developers **exactly how to implement a connector** for the Magnus Financial Assistant data integration layer.

---

## Connector Checklist

When implementing a new connector, you must:

- [ ] Inherit from `DataConnector` base class
- [ ] Implement `get_name()` method
- [ ] Implement `get_data_source_type()` method
- [ ] Implement `fetch_data(query)` method
- [ ] Choose appropriate `CachePolicy`
- [ ] Handle all supported query types
- [ ] Include comprehensive error handling
- [ ] Write unit tests for all query types
- [ ] Document query parameters and return formats
- [ ] Register connector in `DataIntegrationService`

---

## Template

```python
"""
[Feature Name] Connector - Brief description

Handles:
- List what this connector provides access to

Author: Your Name
Date: Date
"""

from typing import Dict, Any, List
from datetime import datetime
import os
from loguru import logger

from src.mfa.data_integration_service import DataConnector, DataSourceType, CachePolicy


class [FeatureName]Connector(DataConnector):
    """
    Connector for [Feature Name] feature.

    Provides access to:
    - List specific data points
    - List specific operations

    Cache Strategy:
    - Describe caching approach
    - Explain TTL choices
    """

    def __init__(self):
        # Choose appropriate cache policy
        cache_policy = CachePolicy.[no_cache|short_ttl|medium_ttl|long_ttl|daily]()
        super().__init__(cache_policy)

        # Initialize dependencies (lazy loading)
        self._dependency = None
        self._db_config = None

    def get_name(self) -> str:
        """Return connector name (lowercase, underscore-separated)"""
        return "[feature_name]"

    def get_data_source_type(self) -> DataSourceType:
        """Return primary data source type"""
        return DataSourceType.[DATABASE|EXTERNAL_API|CACHE|COMPUTED|HYBRID]

    def fetch_data(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetch data based on query type.

        Supported query types:
        - 'query_type_1': Description
        - 'query_type_2': Description

        Args:
            query: Query dictionary with 'type' and 'params'

        Returns:
            Query results

        Raises:
            ValueError: If query type is unknown
        """
        query_type = query.get('type')
        params = query.get('params', {})

        if query_type == 'query_type_1':
            return self._query_type_1_handler(params)
        elif query_type == 'query_type_2':
            return self._query_type_2_handler(params)
        else:
            raise ValueError(f"Unknown query type: {query_type}")

    def _query_type_1_handler(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle specific query type.

        Args:
            params: Query parameters

        Returns:
            Results dictionary
        """
        try:
            # Implementation here
            pass
        except Exception as e:
            logger.error(f"Error in {self.get_name()} query: {e}")
            return {'error': str(e)}

    # Add more query handlers as needed
```

---

## Cache Policy Selection Guide

Choose the right cache policy based on data characteristics:

| Cache Policy | TTL | Use When |
|-------------|-----|----------|
| `CachePolicy.no_cache()` | 0s | Data changes in real-time (live market data) |
| `CachePolicy.short_ttl()` | 30s | Frequently changing data (positions, balances) |
| `CachePolicy.medium_ttl()` | 5min | Moderate update frequency (options chains, scans) |
| `CachePolicy.long_ttl()` | 1hr | Expensive to compute, slow-changing (AI research) |
| `CachePolicy.daily()` | 24hr | Static data (earnings dates, stock metadata) |

**Examples:**

```python
# Real-time data - no caching
cache_policy = CachePolicy.no_cache()

# Live positions - short TTL
cache_policy = CachePolicy.short_ttl()  # 30s

# Options scans - medium TTL
cache_policy = CachePolicy.medium_ttl()  # 5min

# AI research - long TTL
cache_policy = CachePolicy.long_ttl()  # 1hr

# Earnings dates - daily refresh
cache_policy = CachePolicy.daily()  # 24hr
```

---

## Data Source Type Guide

| Type | Description | Example Features |
|------|-------------|------------------|
| `DATABASE` | Primary source is PostgreSQL | Dashboard (portfolio_balances table) |
| `EXTERNAL_API` | Primary source is external API | Robinhood, Kalshi, TradingView |
| `CACHE` | Primary source is Redis cache | Cached scan results |
| `COMPUTED` | Data calculated on demand | Portfolio metrics, Greeks calculations |
| `HYBRID` | Multiple sources combined | Dashboard (DB + Robinhood API) |

---

## Query Parameter Standards

**All queries follow this format:**

```python
query = {
    "type": "query_type_name",  # Required
    "params": {                  # Optional
        "param1": value1,
        "param2": value2
    }
}
```

**Common Parameter Patterns:**

```python
# Filtering parameters
params = {
    'start_date': '2025-01-01',  # ISO format
    'end_date': '2025-01-31',
    'symbol': 'AAPL',
    'limit': 50,
    'min_score': 70
}

# Symbol list parameters
params = {
    'symbols': ['AAPL', 'NVDA', 'TSLA']
}

# Range parameters
params = {
    'dte_range': [20, 45],
    'delta_range': [-0.35, -0.25],
    'price_range': [10.0, 500.0]
}
```

---

## Return Value Standards

**All query handlers should return dictionaries:**

```python
# Success response
return {
    'data': [...],           # Main data payload
    'count': 10,             # Count of items (if applicable)
    'timestamp': datetime.now().isoformat(),
    'source': 'database'     # Data source identifier
}

# Error response
return {
    'error': 'Error message',
    'timestamp': datetime.now().isoformat()
}
```

---

## Error Handling Pattern

**Every query handler should follow this pattern:**

```python
def _query_handler(self, params: Dict[str, Any]) -> Dict[str, Any]:
    """Query handler with proper error handling"""
    try:
        # Main logic here
        result = self._fetch_from_source(params)

        return {
            'data': result,
            'count': len(result) if isinstance(result, list) else 1,
            'timestamp': datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"{self.get_name()}: Error in query - {e}")
        return {
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }
```

---

## Database Query Pattern

**For PostgreSQL-based connectors:**

```python
def _get_db_config(self) -> Dict[str, str]:
    """Get database configuration from environment"""
    if self._db_config is None:
        self._db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'database': os.getenv('DB_NAME', 'trading'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', '')
        }
    return self._db_config

def _execute_query(self, query: str, params: tuple = None) -> List[tuple]:
    """Execute database query with error handling"""
    try:
        import psycopg2
        conn = psycopg2.connect(**self._get_db_config())
        cur = conn.cursor()

        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)

        rows = cur.fetchall()
        conn.close()

        return rows

    except Exception as e:
        logger.error(f"{self.get_name()}: Database query failed - {e}")
        raise
```

---

## External API Pattern

**For external API-based connectors:**

```python
def _get_api_client(self):
    """Lazy load API client to avoid circular imports"""
    if self._api_client is None:
        try:
            from src.services.[api]_client import [API]Client
            self._api_client = [API]Client()
        except Exception as e:
            logger.warning(f"Could not load API client: {e}")
    return self._api_client

def _fetch_from_api(self, params: Dict[str, Any]) -> Any:
    """Fetch data from external API"""
    client = self._get_api_client()
    if not client:
        raise Exception("API client not available")

    try:
        # Try API call
        result = client.some_method(**params)
        return result

    except Exception as e:
        logger.error(f"API call failed: {e}")
        # Consider fallback to cached data
        raise
```

---

## Registration Pattern

**After implementing connector, register it:**

1. Add import in `src/mfa/data_integration_service.py`:

```python
def _register_all_connectors(self):
    """Register all feature connectors"""

    # Import your new connector
    from src.mfa.connectors.your_connector import YourConnector

    # Register it
    self.register_connector(YourConnector())
```

2. Add convenience methods (optional but recommended):

```python
# In DataIntegrationService class

def your_feature_method(self, param1: str) -> Dict[str, Any]:
    """
    Convenience method for accessing your feature.

    Args:
        param1: Description

    Returns:
        Result dictionary

    Example:
        service = get_data_service()
        result = service.your_feature_method("value")
    """
    result = self.query('your_feature', 'query_type', {'param1': param1})
    return result
```

---

## Testing Pattern

**Create unit tests for your connector:**

```python
# tests/mfa/connectors/test_your_connector.py

import pytest
from src.mfa.connectors.your_connector import YourConnector


def test_connector_name():
    """Test connector name is correct"""
    connector = YourConnector()
    assert connector.get_name() == "your_feature"


def test_query_type_1():
    """Test specific query type"""
    connector = YourConnector()

    query = {
        "type": "query_type_1",
        "params": {"param1": "value1"}
    }

    result = connector.fetch_data(query)

    assert 'data' in result or 'error' in result
    assert 'timestamp' in result


def test_cache_behavior():
    """Test caching works correctly"""
    connector = YourConnector()

    # First call (cache miss)
    result1 = connector.get_cached_or_fetch("test_key", {"type": "test"})

    # Second call (cache hit)
    result2 = connector.get_cached_or_fetch("test_key", {"type": "test"})

    # Results should be identical (from cache)
    assert result1 == result2

    # Stats should show cache hit
    stats = connector.get_cache_stats()
    assert stats['cache_hits'] > 0


def test_error_handling():
    """Test connector handles errors gracefully"""
    connector = YourConnector()

    # Invalid query type
    query = {"type": "invalid_type"}

    with pytest.raises(ValueError):
        connector.fetch_data(query)
```

---

## Complete Example: Positions Connector

```python
"""
Positions Connector - Provides access to active options positions

Handles:
- Active positions from Robinhood
- Position details (Greeks, P&L, expiration)
- Portfolio-level metrics (theta, delta)

Author: Backend Architect
Date: January 10, 2025
"""

from typing import Dict, Any, List
from datetime import datetime
import os
from loguru import logger

from src.mfa.data_integration_service import DataConnector, DataSourceType, CachePolicy


class PositionsConnector(DataConnector):
    """
    Connector for Positions feature.

    Provides access to:
    - Active options positions
    - Position details (Greeks, P&L, days to expiration)
    - Portfolio-level metrics (total theta, delta exposure)

    Cache Strategy:
    - Positions: 30 second TTL (near real-time)
    - Portfolio metrics: 60 second TTL
    """

    def __init__(self):
        # Positions change frequently - short cache
        cache_policy = CachePolicy.short_ttl()
        super().__init__(cache_policy)

        self._rh_client = None
        self._db_config = None

    def _get_robinhood_client(self):
        """Lazy load Robinhood client"""
        if self._rh_client is None:
            try:
                from src.services.robinhood_client import RobinhoodClient
                self._rh_client = RobinhoodClient()
            except Exception as e:
                logger.warning(f"Could not load Robinhood client: {e}")
        return self._rh_client

    def _get_db_config(self) -> Dict[str, str]:
        """Get database configuration"""
        if self._db_config is None:
            self._db_config = {
                'host': os.getenv('DB_HOST', 'localhost'),
                'database': os.getenv('DB_NAME', 'trading'),
                'user': os.getenv('DB_USER', 'postgres'),
                'password': os.getenv('DB_PASSWORD', '')
            }
        return self._db_config

    def get_name(self) -> str:
        return "positions"

    def get_data_source_type(self) -> DataSourceType:
        return DataSourceType.HYBRID  # Robinhood API + Database

    def fetch_data(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetch positions data.

        Supported query types:
        - 'fetch_active': Get all active positions
        - 'get_details': Get details for specific position
        - 'calculate_theta': Calculate total portfolio theta

        Args:
            query: Query dictionary

        Returns:
            Query results
        """
        query_type = query.get('type')
        params = query.get('params', {})

        if query_type == 'fetch_active':
            return self._fetch_active_positions(params)
        elif query_type == 'get_details':
            return self._get_position_details(params)
        elif query_type == 'calculate_theta':
            return self._calculate_portfolio_theta(params)
        else:
            raise ValueError(f"Unknown query type: {query_type}")

    def _fetch_active_positions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch active positions"""
        try:
            import psycopg2
            conn = psycopg2.connect(**self._get_db_config())
            cur = conn.cursor()

            include_closed = params.get('include_closed', False)

            query = """
                SELECT
                    id, symbol, option_type, strike, expiration_date,
                    premium_collected, current_price, unrealized_pnl,
                    days_to_expiration, delta, theta, vega, gamma
                FROM positions
                WHERE 1=1
            """

            if not include_closed:
                query += " AND status = 'active'"

            query += " ORDER BY expiration_date ASC"

            cur.execute(query)
            rows = cur.fetchall()
            conn.close()

            positions = []
            for row in rows:
                positions.append({
                    'id': row[0],
                    'symbol': row[1],
                    'option_type': row[2],
                    'strike': float(row[3]) if row[3] else 0.0,
                    'expiration_date': row[4].isoformat() if row[4] else None,
                    'premium_collected': float(row[5]) if row[5] else 0.0,
                    'current_price': float(row[6]) if row[6] else 0.0,
                    'unrealized_pnl': float(row[7]) if row[7] else 0.0,
                    'days_to_expiration': row[8],
                    'delta': float(row[9]) if row[9] else 0.0,
                    'theta': float(row[10]) if row[10] else 0.0,
                    'vega': float(row[11]) if row[11] else 0.0,
                    'gamma': float(row[12]) if row[12] else 0.0
                })

            return {
                'positions': positions,
                'count': len(positions),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error fetching positions: {e}")
            return {
                'positions': [],
                'count': 0,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def _get_position_details(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get details for specific position"""
        # Implementation here
        pass

    def _calculate_portfolio_theta(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate total portfolio theta"""
        try:
            import psycopg2
            conn = psycopg2.connect(**self._get_db_config())
            cur = conn.cursor()

            cur.execute("""
                SELECT COALESCE(SUM(theta), 0) as total_theta
                FROM positions
                WHERE status = 'active'
            """)

            row = cur.fetchone()
            conn.close()

            return {
                'total_theta': float(row[0]) if row[0] else 0.0,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error calculating theta: {e}")
            return {
                'total_theta': 0.0,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
```

---

## Connector Priority List

**Implement in this order:**

1. **Dashboard** (Core - portfolio data)
2. **Positions** (Core - active positions)
3. **Opportunities** (Core - CSP finder)
4. **TradingView** (Integration - watchlists)
5. **AI Research** (Analytics - stock analysis)
6. **Earnings** (Analytics - earnings calendar)
7. **Kalshi** (Integration - prediction markets)
8. **Xtrades** (Integration - trader alerts)
9. **Calendar Spreads** (Strategy - spread analysis)
10. **Database Scan** (Core - stock database)
11. ... (remaining 11 connectors)

---

## Quick Start Checklist

To implement a new connector:

1. [ ] Copy template above
2. [ ] Replace `[FeatureName]` with actual name
3. [ ] Choose appropriate `CachePolicy`
4. [ ] Choose appropriate `DataSourceType`
5. [ ] List all supported query types
6. [ ] Implement each query handler
7. [ ] Add error handling to all methods
8. [ ] Add lazy loading for dependencies
9. [ ] Write unit tests
10. [ ] Register in `DataIntegrationService`
11. [ ] Add convenience methods (optional)
12. [ ] Document in architecture docs

---

## Common Pitfalls

### ❌ Don't Do This

```python
# DON'T import at module level (circular imports)
from src.services.robinhood_client import RobinhoodClient

class MyConnector(DataConnector):
    def __init__(self):
        self.rh = RobinhoodClient()  # BAD - imports on init
```

### ✅ Do This Instead

```python
# DO lazy load dependencies
class MyConnector(DataConnector):
    def __init__(self):
        self._rh = None  # Initialize as None

    def _get_robinhood_client(self):
        """Lazy load on first use"""
        if self._rh is None:
            from src.services.robinhood_client import RobinhoodClient
            self._rh = RobinhoodClient()
        return self._rh
```

---

## Performance Tips

1. **Use appropriate cache TTLs** - Don't cache real-time data, do cache expensive queries
2. **Lazy load dependencies** - Avoid circular imports and reduce startup time
3. **Batch database queries** - Fetch all data in one query when possible
4. **Handle errors gracefully** - Return error dict instead of raising exceptions
5. **Log strategically** - Debug logs for cache hits/misses, error logs for failures

---

## Questions?

**Review these files:**
- `src/mfa/data_integration_service.py` - Base classes and service
- `src/mfa/connectors/dashboard_connector.py` - Example implementation
- `FINANCIAL_ASSISTANT_INTEGRATION_ARCHITECTURE.md` - Full architecture

**Contact:** Backend Architect Agent (via Magnus development team)

---

**Last Updated:** January 10, 2025
