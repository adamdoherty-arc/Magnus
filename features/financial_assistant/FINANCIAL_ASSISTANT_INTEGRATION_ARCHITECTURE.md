# Magnus Financial Assistant - Complete Integration Architecture

**Document Version:** 1.0
**Date:** January 10, 2025
**Status:** Architecture Design - Ready for Implementation
**Author:** Backend Architect Agent

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Complete Feature Integration Matrix](#complete-feature-integration-matrix)
3. [Unified Data Access Layer Architecture](#unified-data-access-layer-architecture)
4. [Action Execution Framework](#action-execution-framework)
5. [Proactive Management System](#proactive-management-system)
6. [Feature Discovery & Intent Mapping](#feature-discovery--intent-mapping)
7. [System Integration Diagrams](#system-integration-diagrams)
8. [Implementation Roadmap](#implementation-roadmap)
9. [Testing & Validation Strategy](#testing--validation-strategy)
10. [Performance & Scalability](#performance--scalability)

---

## 1. Executive Summary

### The Vision

The Magnus Financial Assistant (MFA) must serve as the **ultimate unified interface** to the entire Magnus ecosystem. Every feature, every data source, every capability must be accessible through natural conversation.

### Current State Analysis

**Magnus Platform Features (12+ identified):**

| Category | Features | Current State |
|----------|----------|---------------|
| **Core Trading** | Dashboard, Positions, Opportunities, Premium Scanner | ✅ Operational |
| **Analytics** | AI Research, Earnings Calendar, Sector Analysis, Supply/Demand Zones | ✅ Operational |
| **Integrations** | Robinhood, TradingView, Kalshi, Xtrades | ✅ Operational |
| **Advanced Strategies** | Calendar Spreads, Recovery Strategies, Comprehensive Strategy | ✅ Operational |
| **Prediction Markets** | Kalshi NFL Markets, Prediction Markets Page | ✅ Operational |
| **Automation** | Enhancement Agent, Task Management, Autonomous Systems | ✅ Operational |
| **Performance Tracking** | Analytics Performance, Balance Tracking, Trade History | ✅ Operational |

### Integration Challenges

1. **Data Fragmentation**: Data spread across 10+ database schemas (PostgreSQL)
2. **API Diversity**: Multiple external APIs (Robinhood, Kalshi, TradingView, Xtrades)
3. **Feature Isolation**: Each feature operates independently with minimal cross-feature intelligence
4. **Access Complexity**: Users must know which page/feature to use for each task
5. **No Unified State**: No single source of truth for user context across features

### Solution Architecture

We design a **three-layer integration architecture**:

```
┌─────────────────────────────────────────────────────────────┐
│         LAYER 1: CONVERSATION INTERFACE                     │
│  (Natural language input → Intent classification → Routing) │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│         LAYER 2: UNIFIED DATA INTEGRATION SERVICE           │
│  (Single API to access ALL Magnus features and data)        │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│         LAYER 3: FEATURE-SPECIFIC CONNECTORS                │
│  (12+ connectors to each Magnus feature/database)           │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Complete Feature Integration Matrix

### 2.1 Feature Catalog (Complete List)

| # | Feature Name | Category | Database Tables | External APIs | Entry Point |
|---|--------------|----------|-----------------|---------------|-------------|
| 1 | **Dashboard** | Core | `portfolio_balances`, `trade_history`, `positions` | Robinhood | `dashboard.py` |
| 2 | **Positions** | Core | `positions`, `options_quotes` | Robinhood | `positions_page_improved.py` |
| 3 | **Opportunities** | Core | `opportunities`, `stocks`, `options_chain` | Robinhood, yfinance | `opportunities_page.py` |
| 4 | **Premium Scanner** | Analytics | `premium_scans`, `options_chain` | Robinhood | `premium_scanner_page.py` |
| 5 | **TradingView Watchlists** | Integration | `tradingview_watchlists`, `watchlist_symbols` | TradingView API | `xtrades_watchlists_page.py` |
| 6 | **Database Scan** | Core | `stocks`, `scan_results` | yfinance | `database_scan_page.py` |
| 7 | **Earnings Calendar** | Analytics | `earnings_dates` | Financial APIs | `earnings_calendar_page.py` |
| 8 | **Calendar Spreads** | Strategy | `calendar_spreads`, `spread_analysis` | Robinhood | `calendar_spreads_page.py` |
| 9 | **Prediction Markets** | Integration | `kalshi_markets`, `kalshi_positions`, `kalshi_events` | Kalshi API | `prediction_markets_page.py` |
| 10 | **Kalshi NFL Markets** | Integration | `nfl_games`, `nfl_predictions`, `nfl_teams` | Kalshi, ESPN | `kalshi_nfl_markets_page.py` |
| 11 | **AI Research** | Analytics | `research_cache`, `ai_analysis` | OpenAI, Claude, Groq, Gemini | `ai_research_page.py` |
| 12 | **Comprehensive Strategy** | Strategy | (uses positions, opportunities) | Multiple LLMs | `comprehensive_strategy_page.py` |
| 13 | **AI Options Agent** | Analytics | (uses options_chain, stocks) | Multiple LLMs | `ai_options_agent_page.py` |
| 14 | **Xtrades Alerts** | Integration | `xtrades_alerts`, `xtrades_profiles`, `xtrades_watchlists` | Xtrades (scraping) | `xtrades_watchlists_page.py` |
| 15 | **Supply/Demand Zones** | Analytics | `supply_demand_zones`, `zone_history` | yfinance | `supply_demand_zones_page.py` |
| 16 | **Sector Analysis** | Analytics | `sector_allocations` | yfinance | `sector_analysis_page.py` |
| 17 | **Premium Options Flow** | Analytics | `options_flow` | Robinhood | `premium_flow_page.py` |
| 18 | **Enhancement Manager** | Automation | `development_tasks`, `task_execution_log` | None | `enhancement_manager_page.py` |
| 19 | **Analytics Performance** | Tracking | `portfolio_balances`, `trade_metrics` | Robinhood | `analytics_performance_page.py` |
| 20 | **Game-by-Game Analysis** | Sports | `nfl_games`, `game_predictions` | ESPN, Kalshi | `game_by_game_analysis_page.py` |
| 21 | **Settings** | Config | `user_settings` | None | `settings_page.py` |

### 2.2 Feature Integration Design (Per Feature)

#### Feature 1: Dashboard

**What MFA Needs to Access:**
- Current portfolio balance
- Total P&L (realized and unrealized)
- Trade history (all time, recent, filtered)
- Balance forecast timeline
- Active positions summary
- AI recommendations from research agents

**MFA Capabilities:**
```python
# Example MFA interactions
User: "What's my portfolio status?"
MFA: → fetch_dashboard_summary()
     → Returns: balance, P&L, positions count, theta decay

User: "Show me my trade history from last month"
MFA: → fetch_trade_history(start_date="2024-12-01", end_date="2025-01-01")
     → Returns: trades with P&L, win rate, best/worst trades

User: "Record a new manual trade: sold AAPL $170 put for $2.50"
MFA: → record_manual_trade(symbol="AAPL", strike=170, premium=2.50, ...)
     → Updates database, refreshes dashboard
```

**Integration Points:**
- **Data Access**: `src.portfolio_balance_tracker`, `src.portfolio_balance_display`
- **Database**: `portfolio_balances`, `trade_history`, `positions` tables
- **External API**: Robinhood (for live balance sync)
- **Cache Strategy**: 60-second TTL for balance, 5-minute for trade history

---

#### Feature 2: Positions

**What MFA Needs to Access:**
- Active positions (all options positions)
- Real-time P&L per position
- Greeks (Delta, Theta, Gamma, Vega)
- Days to expiration
- Assignment probability
- Profit-taking recommendations

**MFA Capabilities:**
```python
User: "Which positions should I close?"
MFA: → fetch_active_positions()
     → analyze_profit_targets()
     → Returns: positions at >50% profit, near expiration, or ITM

User: "What's my total theta decay today?"
MFA: → calculate_portfolio_theta()
     → Returns: sum of theta across all positions

User: "Am I at risk of assignment on any positions?"
MFA: → check_assignment_risk()
     → Returns: positions where strike < current_price (ITM puts)
```

**Integration Points:**
- **Data Access**: `positions_page_improved.py`, Robinhood client
- **Database**: `positions`, `options_quotes` tables
- **External API**: Robinhood (live positions, Greeks)
- **Real-time Updates**: Auto-refresh every 60s (configurable)
- **Cache Strategy**: 30-second TTL for positions, 60-second for Greeks

---

#### Feature 3: Opportunities (CSP Finder)

**What MFA Needs to Access:**
- CSP opportunities scanner
- AI scoring system (0-100)
- Filtering criteria (IV, Delta, Premium %, DTE)
- Options chain data
- Earnings date warnings

**MFA Capabilities:**
```python
User: "Find me a good CSP opportunity"
MFA: → scan_csp_opportunities(min_score=70, dte_range=[20,45])
     → Returns: Top 5 opportunities with reasoning

User: "What's a good strike for NVDA?"
MFA: → analyze_option_strikes(symbol="NVDA", strategy="csp")
     → Returns: recommended strikes with support levels, IV, probabilities

User: "Analyze this trade: sell TSLA $240 put 30 DTE"
MFA: → evaluate_trade_setup(symbol="TSLA", strike=240, dte=30)
     → Returns: expected value, win probability, risk/reward analysis
```

**Integration Points:**
- **Data Access**: `src.csp_opportunities_finder`, `src.options_data_fetcher`
- **Database**: `opportunities`, `stocks`, `options_chain` tables
- **External API**: Robinhood (options chains), yfinance (price data)
- **AI Integration**: Use existing AI scoring logic
- **Cache Strategy**: 5-minute TTL for opportunities scan

---

#### Feature 4: TradingView Watchlists

**What MFA Needs to Access:**
- All TradingView watchlists
- Symbols in each watchlist
- Sync status and last sync time
- Premium analysis on watchlist symbols

**MFA Capabilities:**
```python
User: "What's in my TradingView watchlist?"
MFA: → fetch_tradingview_watchlists()
     → Returns: list of watchlists with symbol counts

User: "Scan my High IV watchlist for opportunities"
MFA: → fetch_watchlist_symbols(watchlist="High IV")
     → scan_symbols_for_premium(symbols=...)
     → Returns: best opportunities from that watchlist

User: "Sync my TradingView watchlists"
MFA: → trigger_tradingview_sync()
     → Returns: sync status, new symbols added
```

**Integration Points:**
- **Data Access**: `src.tradingview_api_sync`, `src.watchlist_sync_service`
- **Database**: `tradingview_watchlists`, `watchlist_symbols` tables
- **External API**: TradingView (session-based auth)
- **Cache Strategy**: 30-minute TTL for watchlist data

---

#### Feature 5: Kalshi Prediction Markets

**What MFA Needs to Access:**
- Active Kalshi markets (all sectors)
- NFL game predictions
- Market prices (Yes/No)
- AI evaluation of market mispricing
- Kalshi positions

**MFA Capabilities:**
```python
User: "What's the prediction for Sunday's NFL games?"
MFA: → fetch_nfl_predictions()
     → Returns: game odds, AI recommendations, Kalshi market prices

User: "Find mispriced Kalshi markets"
MFA: → analyze_kalshi_markets()
     → compare_ai_vs_market_odds()
     → Returns: markets where AI disagrees with market pricing

User: "What Kalshi positions do I have?"
MFA: → fetch_kalshi_positions()
     → Returns: active positions with P&L
```

**Integration Points:**
- **Data Access**: `src.kalshi_integration`, `src.kalshi_client`, `src.kalshi_ai_evaluator`
- **Database**: `kalshi_markets`, `kalshi_positions`, `nfl_games`, `nfl_predictions` tables
- **External API**: Kalshi (market data), ESPN (live NFL scores)
- **AI Integration**: Multi-model consensus for predictions
- **Cache Strategy**: 5-minute TTL for market prices, real-time for live games

---

#### Feature 6: Xtrades Alerts

**What MFA Needs to Access:**
- Followed traders on Xtrades
- Recent alerts/trades from followed traders
- Alert parsing and analysis
- Trade idea extraction

**MFA Capabilities:**
```python
User: "What trades are the pros making today?"
MFA: → fetch_xtrades_recent_alerts()
     → parse_trade_ideas()
     → Returns: latest alerts with analysis

User: "Show me alerts from BeHappy23"
MFA: → fetch_profile_alerts(profile="BeHappy23")
     → Returns: recent alerts from that specific trader

User: "Any unusual options activity?"
MFA: → analyze_xtrades_volume()
     → Returns: stocks with high alert volume
```

**Integration Points:**
- **Data Access**: `src.xtrades_scraper`, `src.xtrades_db_manager`
- **Database**: `xtrades_alerts`, `xtrades_profiles`, `xtrades_watchlists` tables
- **External API**: Xtrades (web scraping with Selenium)
- **Real-time Monitoring**: Background scraper service
- **Cache Strategy**: Real-time (no cache), live scraping

---

#### Feature 7: AI Research Assistant

**What MFA Needs to Access:**
- Multi-agent research system (4 agents)
- Fundamental analysis
- Technical analysis
- Sentiment analysis
- Options-specific analysis
- Overall stock rating and recommendations

**MFA Capabilities:**
```python
User: "Research AAPL for me"
MFA: → trigger_ai_research(symbol="AAPL")
     → Runs 4 agents in parallel
     → Returns: comprehensive analysis with rating

User: "Is NVDA a good buy right now?"
MFA: → get_ai_recommendation(symbol="NVDA")
     → Returns: BUY/HOLD/SELL with reasoning

User: "Why did TSLA drop today?"
MFA: → analyze_price_movement(symbol="TSLA", timeframe="1d")
     → fetch_news_sentiment()
     → Returns: analysis of price drop with news context
```

**Integration Points:**
- **Data Access**: `src.ai.research_orchestrator`, multi-agent system
- **Database**: `research_cache`, `ai_analysis` tables
- **External API**: Multiple LLMs (Groq, Gemini, DeepSeek, Claude)
- **AI Agents**: 4 specialized agents (fundamental, technical, sentiment, options)
- **Cache Strategy**: 1-hour TTL for research results

---

#### Feature 8: Calendar Spreads

**What MFA Needs to Access:**
- Calendar spread scanner
- Spread builder (short/long legs)
- IV skew analysis
- Risk/reward calculations
- AI spread evaluator

**MFA Capabilities:**
```python
User: "Find good calendar spread opportunities"
MFA: → scan_calendar_spreads(min_score=60)
     → Returns: best calendar spreads with IV analysis

User: "Build a calendar spread on SPY"
MFA: → build_calendar_spread(symbol="SPY", strategy="put_calendar")
     → Returns: recommended strikes/expirations, cost, max profit

User: "Should I enter this calendar spread?"
MFA: → evaluate_calendar_spread(spread_details=...)
     → Returns: AI analysis of spread quality
```

**Integration Points:**
- **Data Access**: `src.calendar_spread_analyzer`, `src.ai_spread_evaluator`
- **Database**: `calendar_spreads`, `spread_analysis` tables
- **External API**: Robinhood (options chains for multiple expirations)
- **AI Integration**: AI evaluation of spread quality
- **Cache Strategy**: 5-minute TTL for spread opportunities

---

#### Feature 9: Earnings Calendar

**What MFA Needs to Access:**
- Upcoming earnings dates
- Positions at risk (expire after earnings)
- Estimated earnings move (%)
- Earnings date accuracy

**MFA Capabilities:**
```python
User: "When is AAPL earnings?"
MFA: → fetch_earnings_date(symbol="AAPL")
     → Returns: date, time, estimated move

User: "Which of my positions have earnings risk?"
MFA: → check_positions_earnings_risk()
     → Returns: positions that expire after upcoming earnings

User: "Show me all earnings this week"
MFA: → fetch_upcoming_earnings(days=7)
     → Returns: all earnings in next 7 days
```

**Integration Points:**
- **Data Access**: `src.earnings_fetcher`
- **Database**: `earnings_dates` table
- **External API**: Financial data API (Alpha Vantage, Yahoo Finance)
- **Cache Strategy**: Daily refresh (earnings dates don't change frequently)

---

#### Feature 10: Database Scan

**What MFA Needs to Access:**
- Stock database (all symbols)
- Database scanner for premium opportunities
- Stock metadata (sector, market cap, etc.)
- Scan results and analytics

**MFA Capabilities:**
```python
User: "Add HIMS to my database"
MFA: → add_stock_to_database(symbol="HIMS")
     → Returns: validation, metadata added

User: "Scan all tech stocks for opportunities"
MFA: → scan_database(sector="Technology", min_price=20)
     → Returns: best opportunities from tech sector

User: "How many stocks in my database?"
MFA: → get_database_stats()
     → Returns: total stocks, by sector, by price range
```

**Integration Points:**
- **Data Access**: `src.stock_data_sync`, `src.database_scanner`
- **Database**: `stocks`, `scan_results` tables
- **External API**: yfinance (stock validation and metadata)
- **Cache Strategy**: 24-hour TTL for stock metadata

---

### 2.3 Cross-Feature Intelligence

**Key Insight**: MFA must not just access features individually, but **combine data across features** for intelligent insights.

**Examples of Cross-Feature Intelligence:**

1. **Portfolio + Earnings Calendar**:
   ```python
   User: "Do I have any earnings risk?"
   MFA: → fetch_active_positions()
        → fetch_upcoming_earnings()
        → cross_reference(positions, earnings)
        → Returns: positions at risk with earnings dates
   ```

2. **Opportunities + TradingView Watchlists**:
   ```python
   User: "Scan my watchlist for CSP setups"
   MFA: → fetch_watchlist_symbols(watchlist="main")
        → scan_csp_opportunities(symbols=watchlist_symbols)
        → Returns: best opportunities from watchlist only
   ```

3. **Positions + Kalshi Markets**:
   ```python
   User: "How does the market view my TSLA position?"
   MFA: → fetch_position(symbol="TSLA")
        → fetch_kalshi_markets(ticker="TSLA")
        → Returns: position details + market sentiment from prediction markets
   ```

4. **AI Research + Opportunities**:
   ```python
   User: "Find opportunities in stocks with bullish AI ratings"
   MFA: → fetch_ai_research_results(rating="bullish")
        → scan_csp_opportunities(symbols=bullish_stocks)
        → Returns: high-conviction opportunities
   ```

---

## 3. Unified Data Access Layer Architecture

### 3.1 Design Principles

1. **Single Responsibility**: Each connector handles ONE feature/data source
2. **Uniform Interface**: All connectors implement the same base interface
3. **Caching**: Built-in intelligent caching with TTL per data type
4. **Error Handling**: Graceful degradation when data sources fail
5. **Thread Safety**: All operations are thread-safe for concurrent access
6. **Observable**: All operations logged for debugging and monitoring

### 3.2 Core Architecture

```python
# src/mfa/data_integration_service.py

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import threading
from dataclasses import dataclass
from enum import Enum


class DataSourceType(Enum):
    """Types of data sources"""
    DATABASE = "database"          # PostgreSQL direct
    EXTERNAL_API = "external_api"  # Robinhood, Kalshi, etc.
    CACHE = "cache"                # Redis cache
    COMPUTED = "computed"          # Calculated on demand


@dataclass
class CachePolicy:
    """Cache policy for data types"""
    enabled: bool = True
    ttl_seconds: int = 300  # 5 minutes default
    max_size: int = 1000     # Max items in cache


class DataConnector(ABC):
    """
    Abstract base class for all data connectors.

    Each Magnus feature has a corresponding connector that implements
    this interface for unified access.
    """

    def __init__(self, cache_policy: CachePolicy = None):
        self.cache_policy = cache_policy or CachePolicy()
        self._cache = {}
        self._cache_timestamps = {}
        self._lock = threading.Lock()

    @abstractmethod
    def get_name(self) -> str:
        """Return connector name (e.g., 'dashboard', 'positions')"""
        pass

    @abstractmethod
    def get_data_source_type(self) -> DataSourceType:
        """Return the primary data source type"""
        pass

    @abstractmethod
    def fetch_data(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetch data based on query parameters.

        Args:
            query: Dictionary with query parameters
                   Format varies by connector

        Returns:
            Dictionary with results
        """
        pass

    def get_cached_or_fetch(self, cache_key: str, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get data from cache if valid, otherwise fetch fresh.

        Args:
            cache_key: Unique key for this query
            query: Query parameters

        Returns:
            Cached or fresh data
        """
        if not self.cache_policy.enabled:
            return self.fetch_data(query)

        with self._lock:
            # Check cache validity
            if cache_key in self._cache:
                timestamp = self._cache_timestamps.get(cache_key)
                if timestamp:
                    age = (datetime.now() - timestamp).total_seconds()
                    if age < self.cache_policy.ttl_seconds:
                        return self._cache[cache_key]

            # Fetch fresh data
            data = self.fetch_data(query)

            # Update cache
            self._cache[cache_key] = data
            self._cache_timestamps[cache_key] = datetime.now()

            # Enforce max cache size (LRU-like)
            if len(self._cache) > self.cache_policy.max_size:
                oldest_key = min(self._cache_timestamps.items(), key=lambda x: x[1])[0]
                del self._cache[oldest_key]
                del self._cache_timestamps[oldest_key]

            return data

    def invalidate_cache(self, cache_key: Optional[str] = None):
        """Invalidate cache (specific key or all)"""
        with self._lock:
            if cache_key:
                self._cache.pop(cache_key, None)
                self._cache_timestamps.pop(cache_key, None)
            else:
                self._cache.clear()
                self._cache_timestamps.clear()


class DataIntegrationService:
    """
    Central service for unified data access across ALL Magnus features.

    This is the SINGLE interface that MFA uses to access any data
    from any Magnus feature.
    """

    def __init__(self):
        self._connectors: Dict[str, DataConnector] = {}
        self._register_all_connectors()

    def _register_all_connectors(self):
        """Register all feature connectors"""
        # Import and register each connector
        from src.mfa.connectors.dashboard_connector import DashboardConnector
        from src.mfa.connectors.positions_connector import PositionsConnector
        from src.mfa.connectors.opportunities_connector import OpportunitiesConnector
        from src.mfa.connectors.tradingview_connector import TradingViewConnector
        from src.mfa.connectors.kalshi_connector import KalshiConnector
        from src.mfa.connectors.xtrades_connector import XtradesConnector
        from src.mfa.connectors.ai_research_connector import AIResearchConnector
        from src.mfa.connectors.earnings_connector import EarningsConnector
        from src.mfa.connectors.calendar_spreads_connector import CalendarSpreadsConnector
        from src.mfa.connectors.database_scan_connector import DatabaseScanConnector
        # ... register all 21 connectors

        self.register_connector(DashboardConnector())
        self.register_connector(PositionsConnector())
        self.register_connector(OpportunitiesConnector())
        # ... etc.

    def register_connector(self, connector: DataConnector):
        """Register a data connector"""
        self._connectors[connector.get_name()] = connector

    def get_connector(self, name: str) -> Optional[DataConnector]:
        """Get connector by name"""
        return self._connectors.get(name)

    # ========================================================================
    # HIGH-LEVEL QUERY INTERFACE
    # ========================================================================

    def query(self, feature: str, query_type: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Universal query interface.

        Args:
            feature: Feature name (e.g., 'dashboard', 'positions')
            query_type: Type of query (e.g., 'get_balance', 'fetch_positions')
            params: Query parameters

        Returns:
            Query results

        Example:
            service.query('dashboard', 'get_portfolio_summary')
            service.query('positions', 'fetch_active', {'include_closed': False})
        """
        connector = self.get_connector(feature)
        if not connector:
            raise ValueError(f"Unknown feature: {feature}")

        cache_key = f"{feature}:{query_type}:{hash(str(params))}"
        query_dict = {"type": query_type, "params": params or {}}

        return connector.get_cached_or_fetch(cache_key, query_dict)

    # ========================================================================
    # CONVENIENCE METHODS (Feature-specific)
    # ========================================================================

    # Dashboard Methods
    def get_portfolio_balance(self) -> float:
        """Get current portfolio balance"""
        result = self.query('dashboard', 'get_balance')
        return result.get('balance', 0.0)

    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get complete portfolio summary"""
        return self.query('dashboard', 'get_summary')

    def get_trade_history(self, start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """Get trade history with optional date filters"""
        params = {}
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date

        result = self.query('dashboard', 'get_trade_history', params)
        return result.get('trades', [])

    # Positions Methods
    def get_active_positions(self) -> List[Dict[str, Any]]:
        """Get all active positions"""
        result = self.query('positions', 'fetch_active')
        return result.get('positions', [])

    def get_position_details(self, position_id: str) -> Dict[str, Any]:
        """Get detailed info for specific position"""
        return self.query('positions', 'get_details', {'position_id': position_id})

    def calculate_portfolio_theta(self) -> float:
        """Calculate total theta decay across portfolio"""
        result = self.query('positions', 'calculate_theta')
        return result.get('total_theta', 0.0)

    # Opportunities Methods
    def scan_csp_opportunities(self, min_score: int = 70, dte_range: List[int] = None) -> List[Dict[str, Any]]:
        """Scan for CSP opportunities"""
        params = {'min_score': min_score}
        if dte_range:
            params['dte_min'] = dte_range[0]
            params['dte_max'] = dte_range[1]

        result = self.query('opportunities', 'scan_csp', params)
        return result.get('opportunities', [])

    def evaluate_trade_setup(self, symbol: str, strike: float, dte: int) -> Dict[str, Any]:
        """Evaluate a specific trade setup"""
        params = {'symbol': symbol, 'strike': strike, 'dte': dte}
        return self.query('opportunities', 'evaluate_setup', params)

    # TradingView Methods
    def get_watchlists(self) -> List[Dict[str, Any]]:
        """Get all TradingView watchlists"""
        result = self.query('tradingview', 'fetch_watchlists')
        return result.get('watchlists', [])

    def get_watchlist_symbols(self, watchlist_name: str) -> List[str]:
        """Get symbols in a specific watchlist"""
        result = self.query('tradingview', 'get_symbols', {'watchlist': watchlist_name})
        return result.get('symbols', [])

    # Kalshi Methods
    def get_kalshi_markets(self, category: str = None) -> List[Dict[str, Any]]:
        """Get Kalshi prediction markets"""
        params = {'category': category} if category else {}
        result = self.query('kalshi', 'fetch_markets', params)
        return result.get('markets', [])

    def get_nfl_predictions(self, week: int = None) -> List[Dict[str, Any]]:
        """Get NFL game predictions"""
        params = {'week': week} if week else {}
        result = self.query('kalshi', 'fetch_nfl_predictions', params)
        return result.get('games', [])

    # Xtrades Methods
    def get_recent_alerts(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent Xtrades alerts"""
        result = self.query('xtrades', 'fetch_recent_alerts', {'limit': limit})
        return result.get('alerts', [])

    def get_profile_alerts(self, profile_name: str) -> List[Dict[str, Any]]:
        """Get alerts from specific Xtrades profile"""
        result = self.query('xtrades', 'fetch_profile_alerts', {'profile': profile_name})
        return result.get('alerts', [])

    # AI Research Methods
    def research_stock(self, symbol: str) -> Dict[str, Any]:
        """Run AI research on a stock"""
        return self.query('ai_research', 'analyze_stock', {'symbol': symbol})

    def get_stock_rating(self, symbol: str) -> str:
        """Get AI rating for a stock (BUY/HOLD/SELL)"""
        result = self.query('ai_research', 'get_rating', {'symbol': symbol})
        return result.get('rating', 'UNKNOWN')

    # Earnings Methods
    def get_earnings_date(self, symbol: str) -> Optional[str]:
        """Get earnings date for a symbol"""
        result = self.query('earnings', 'fetch_date', {'symbol': symbol})
        return result.get('earnings_date')

    def check_earnings_risk(self) -> List[Dict[str, Any]]:
        """Check which positions have earnings risk"""
        return self.query('earnings', 'check_position_risk')

    # Calendar Spreads Methods
    def scan_calendar_spreads(self, min_score: int = 60) -> List[Dict[str, Any]]:
        """Scan for calendar spread opportunities"""
        result = self.query('calendar_spreads', 'scan', {'min_score': min_score})
        return result.get('spreads', [])

    # Database Scan Methods
    def get_database_stats(self) -> Dict[str, Any]:
        """Get stock database statistics"""
        return self.query('database_scan', 'get_stats')

    def scan_database(self, sector: str = None, min_price: float = None) -> List[Dict[str, Any]]:
        """Scan stock database for opportunities"""
        params = {}
        if sector:
            params['sector'] = sector
        if min_price:
            params['min_price'] = min_price

        result = self.query('database_scan', 'scan', params)
        return result.get('opportunities', [])

    # ========================================================================
    # CROSS-FEATURE INTELLIGENCE
    # ========================================================================

    def find_watchlist_opportunities(self, watchlist_name: str, min_score: int = 70) -> List[Dict[str, Any]]:
        """Find opportunities within a TradingView watchlist"""
        # Get watchlist symbols
        symbols = self.get_watchlist_symbols(watchlist_name)

        # Scan those symbols for opportunities
        params = {'symbols': symbols, 'min_score': min_score}
        result = self.query('opportunities', 'scan_csp', params)
        return result.get('opportunities', [])

    def check_position_earnings_risk(self) -> List[Dict[str, Any]]:
        """Cross-reference positions with upcoming earnings"""
        positions = self.get_active_positions()
        risky_positions = []

        for position in positions:
            symbol = position.get('symbol')
            expiration = position.get('expiration_date')

            earnings_date = self.get_earnings_date(symbol)

            if earnings_date and expiration:
                # Check if earnings is before expiration
                if earnings_date < expiration:
                    risky_positions.append({
                        'position': position,
                        'earnings_date': earnings_date,
                        'expiration_date': expiration,
                        'days_until_earnings': (earnings_date - datetime.now()).days
                    })

        return risky_positions

    def get_ai_recommended_opportunities(self, rating_filter: str = "bullish") -> List[Dict[str, Any]]:
        """Find opportunities in stocks with specific AI ratings"""
        # This would query cached AI research results
        # Then scan those symbols for opportunities
        # Implementation details...
        pass


# ========================================================================
# SINGLETON INSTANCE
# ========================================================================

_data_service_instance = None

def get_data_service() -> DataIntegrationService:
    """Get singleton instance of DataIntegrationService"""
    global _data_service_instance
    if _data_service_instance is None:
        _data_service_instance = DataIntegrationService()
    return _data_service_instance
```

### 3.3 Example Connector Implementation

```python
# src/mfa/connectors/dashboard_connector.py

from src.mfa.data_integration_service import DataConnector, DataSourceType, CachePolicy
from src.portfolio_balance_tracker import PortfolioBalanceTracker
from src.services.robinhood_client import RobinhoodClient
import psycopg2
from typing import Dict, Any, List
from datetime import datetime


class DashboardConnector(DataConnector):
    """
    Connector for Dashboard feature.

    Provides access to:
    - Portfolio balance
    - Trade history
    - P&L metrics
    - Balance forecasts
    """

    def __init__(self):
        # Dashboard data changes frequently but not in real-time
        # 60-second cache is appropriate
        cache_policy = CachePolicy(enabled=True, ttl_seconds=60)
        super().__init__(cache_policy)

        self.rh_client = RobinhoodClient()
        self.balance_tracker = PortfolioBalanceTracker()
        self.db_config = self._get_db_config()

    def _get_db_config(self) -> Dict[str, str]:
        """Get database configuration from environment"""
        import os
        return {
            'host': os.getenv('DB_HOST', 'localhost'),
            'database': os.getenv('DB_NAME', 'trading'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', '')
        }

    def get_name(self) -> str:
        return "dashboard"

    def get_data_source_type(self) -> DataSourceType:
        return DataSourceType.DATABASE  # Primary source is database

    def fetch_data(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetch dashboard data based on query type.

        Supported query types:
        - 'get_balance': Get current portfolio balance
        - 'get_summary': Get complete portfolio summary
        - 'get_trade_history': Get trade history with filters
        """
        query_type = query.get('type')
        params = query.get('params', {})

        if query_type == 'get_balance':
            return self._get_balance()
        elif query_type == 'get_summary':
            return self._get_summary()
        elif query_type == 'get_trade_history':
            return self._get_trade_history(params)
        else:
            raise ValueError(f"Unknown query type: {query_type}")

    def _get_balance(self) -> Dict[str, Any]:
        """Get current portfolio balance"""
        # Try to get from Robinhood first (live)
        try:
            balance = self.rh_client.get_portfolio_balance()
            return {
                'balance': balance,
                'source': 'robinhood',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            # Fallback to database (last known)
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()

            cur.execute("""
                SELECT balance, timestamp
                FROM portfolio_balances
                ORDER BY timestamp DESC
                LIMIT 1
            """)

            row = cur.fetchone()
            conn.close()

            if row:
                return {
                    'balance': row[0],
                    'source': 'database',
                    'timestamp': row[1].isoformat()
                }
            else:
                return {'balance': 0.0, 'source': 'unknown', 'timestamp': None}

    def _get_summary(self) -> Dict[str, Any]:
        """Get complete portfolio summary"""
        conn = psycopg2.connect(**self.db_config)
        cur = conn.cursor()

        # Get current balance
        balance_data = self._get_balance()

        # Get position count
        cur.execute("SELECT COUNT(*) FROM positions WHERE status = 'active'")
        position_count = cur.fetchone()[0]

        # Get total P&L
        cur.execute("""
            SELECT
                SUM(realized_pnl) as realized,
                SUM(unrealized_pnl) as unrealized
            FROM positions
        """)
        pnl_row = cur.fetchone()

        # Get theta decay
        cur.execute("""
            SELECT SUM(theta) as total_theta
            FROM positions
            WHERE status = 'active'
        """)
        theta_row = cur.fetchone()

        conn.close()

        return {
            'balance': balance_data['balance'],
            'position_count': position_count,
            'realized_pnl': pnl_row[0] or 0.0,
            'unrealized_pnl': pnl_row[1] or 0.0,
            'total_pnl': (pnl_row[0] or 0.0) + (pnl_row[1] or 0.0),
            'theta_decay': theta_row[0] or 0.0,
            'timestamp': datetime.now().isoformat()
        }

    def _get_trade_history(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get trade history with optional filters"""
        conn = psycopg2.connect(**self.db_config)
        cur = conn.cursor()

        # Build query with filters
        query = """
            SELECT
                id, symbol, strategy, open_date, close_date,
                premium_collected, cost_to_close, realized_pnl,
                status
            FROM trade_history
            WHERE 1=1
        """

        query_params = []

        if params.get('start_date'):
            query += " AND open_date >= %s"
            query_params.append(params['start_date'])

        if params.get('end_date'):
            query += " AND open_date <= %s"
            query_params.append(params['end_date'])

        if params.get('symbol'):
            query += " AND symbol = %s"
            query_params.append(params['symbol'])

        query += " ORDER BY open_date DESC"

        if params.get('limit'):
            query += " LIMIT %s"
            query_params.append(params['limit'])

        cur.execute(query, query_params)
        rows = cur.fetchall()
        conn.close()

        trades = []
        for row in rows:
            trades.append({
                'id': row[0],
                'symbol': row[1],
                'strategy': row[2],
                'open_date': row[3].isoformat() if row[3] else None,
                'close_date': row[4].isoformat() if row[4] else None,
                'premium_collected': row[5],
                'cost_to_close': row[6],
                'realized_pnl': row[7],
                'status': row[8]
            })

        return {'trades': trades, 'count': len(trades)}
```

---

## 4. Action Execution Framework

### 4.1 Design Principles

1. **Safety First**: All actions require explicit confirmation
2. **Audit Trail**: Every action is logged with user ID, timestamp, parameters
3. **Rollback Capability**: Support for undoing actions where possible
4. **Permission System**: Different action types have different permission levels
5. **Rate Limiting**: Prevent abuse with rate limits on expensive actions

### 4.2 Action Execution Architecture

```python
# src/mfa/action_execution_service.py

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import threading


class ActionType(Enum):
    """Types of actions MFA can execute"""
    # Read-only (no confirmation needed)
    READ_DATA = "read_data"
    GENERATE_REPORT = "generate_report"

    # Low-risk (simple confirmation)
    ADD_TO_WATCHLIST = "add_to_watchlist"
    CREATE_ALERT = "create_alert"
    UPDATE_PREFERENCES = "update_preferences"

    # Medium-risk (detailed confirmation)
    SYNC_DATA = "sync_data"
    RUN_SCAN = "run_scan"

    # High-risk (requires explicit approval + verification)
    EXECUTE_TRADE = "execute_trade"
    CLOSE_POSITION = "close_position"
    CANCEL_ORDER = "cancel_order"


class PermissionLevel(Enum):
    """Permission levels for actions"""
    PUBLIC = 1    # Anyone can execute
    USER = 2      # Requires user authentication
    VERIFIED = 3  # Requires verified user
    ADMIN = 4     # Requires admin privileges


@dataclass
class ActionDefinition:
    """Definition of an executable action"""
    name: str
    action_type: ActionType
    permission_level: PermissionLevel
    requires_confirmation: bool
    confirmation_message: str
    execute_func: Callable
    undo_func: Optional[Callable] = None
    rate_limit_per_hour: int = 100


@dataclass
class ActionResult:
    """Result of an action execution"""
    success: bool
    action_name: str
    message: str
    data: Dict[str, Any]
    timestamp: datetime
    execution_id: str


class ActionExecutionService:
    """
    Service for executing actions across Magnus platform.

    Handles:
    - Trade execution (Robinhood)
    - Watchlist management (TradingView)
    - Alert creation (Xtrades)
    - Prediction market trades (Kalshi)
    - Scan initiation (Database Scanner)
    - Strategy analysis (Calendar Spreads)
    """

    def __init__(self):
        self._actions: Dict[str, ActionDefinition] = {}
        self._execution_log = []
        self._rate_limits = {}
        self._lock = threading.Lock()
        self._register_all_actions()

    def _register_all_actions(self):
        """Register all executable actions"""

        # Trade Execution Actions
        self.register_action(ActionDefinition(
            name="submit_robinhood_order",
            action_type=ActionType.EXECUTE_TRADE,
            permission_level=PermissionLevel.VERIFIED,
            requires_confirmation=True,
            confirmation_message="⚠️ You are about to submit a REAL trade to Robinhood. Please confirm all details.",
            execute_func=self._execute_robinhood_trade,
            undo_func=self._cancel_robinhood_order,
            rate_limit_per_hour=20  # Max 20 trades per hour
        ))

        # Watchlist Management Actions
        self.register_action(ActionDefinition(
            name="add_to_watchlist",
            action_type=ActionType.ADD_TO_WATCHLIST,
            permission_level=PermissionLevel.USER,
            requires_confirmation=False,
            confirmation_message="",
            execute_func=self._add_to_watchlist,
            rate_limit_per_hour=100
        ))

        # Data Sync Actions
        self.register_action(ActionDefinition(
            name="sync_tradingview",
            action_type=ActionType.SYNC_DATA,
            permission_level=PermissionLevel.USER,
            requires_confirmation=True,
            confirmation_message="This will sync all TradingView watchlists. Continue?",
            execute_func=self._sync_tradingview,
            rate_limit_per_hour=10
        ))

        # Scan Actions
        self.register_action(ActionDefinition(
            name="run_csp_scan",
            action_type=ActionType.RUN_SCAN,
            permission_level=PermissionLevel.USER,
            requires_confirmation=False,
            confirmation_message="",
            execute_func=self._run_csp_scan,
            rate_limit_per_hour=50
        ))

        # ... register all other actions

    def register_action(self, action_def: ActionDefinition):
        """Register an action definition"""
        self._actions[action_def.name] = action_def

    def execute(
        self,
        action_name: str,
        user_id: str,
        params: Dict[str, Any],
        confirmed: bool = False
    ) -> ActionResult:
        """
        Execute an action with safety checks.

        Args:
            action_name: Name of action to execute
            user_id: User requesting the action
            params: Action parameters
            confirmed: Whether user has confirmed (for confirmation-required actions)

        Returns:
            ActionResult with execution status
        """
        action_def = self._actions.get(action_name)
        if not action_def:
            return ActionResult(
                success=False,
                action_name=action_name,
                message=f"Unknown action: {action_name}",
                data={},
                timestamp=datetime.now(),
                execution_id=""
            )

        # Check if confirmation required but not provided
        if action_def.requires_confirmation and not confirmed:
            return ActionResult(
                success=False,
                action_name=action_name,
                message=f"Confirmation required: {action_def.confirmation_message}",
                data={"requires_confirmation": True},
                timestamp=datetime.now(),
                execution_id=""
            )

        # Check rate limits
        if not self._check_rate_limit(action_name, user_id, action_def.rate_limit_per_hour):
            return ActionResult(
                success=False,
                action_name=action_name,
                message="Rate limit exceeded. Please try again later.",
                data={},
                timestamp=datetime.now(),
                execution_id=""
            )

        # Generate execution ID
        import uuid
        execution_id = str(uuid.uuid4())

        # Execute the action
        try:
            result_data = action_def.execute_func(params)

            # Log execution
            self._log_execution(execution_id, action_name, user_id, params, True, "Success")

            return ActionResult(
                success=True,
                action_name=action_name,
                message="Action executed successfully",
                data=result_data,
                timestamp=datetime.now(),
                execution_id=execution_id
            )

        except Exception as e:
            # Log failure
            self._log_execution(execution_id, action_name, user_id, params, False, str(e))

            return ActionResult(
                success=False,
                action_name=action_name,
                message=f"Action failed: {str(e)}",
                data={},
                timestamp=datetime.now(),
                execution_id=execution_id
            )

    def _check_rate_limit(self, action_name: str, user_id: str, limit_per_hour: int) -> bool:
        """Check if action is within rate limits"""
        key = f"{user_id}:{action_name}"
        current_time = datetime.now()

        with self._lock:
            if key not in self._rate_limits:
                self._rate_limits[key] = []

            # Remove executions older than 1 hour
            self._rate_limits[key] = [
                ts for ts in self._rate_limits[key]
                if (current_time - ts).total_seconds() < 3600
            ]

            # Check if under limit
            if len(self._rate_limits[key]) >= limit_per_hour:
                return False

            # Add current execution
            self._rate_limits[key].append(current_time)
            return True

    def _log_execution(
        self,
        execution_id: str,
        action_name: str,
        user_id: str,
        params: Dict[str, Any],
        success: bool,
        message: str
    ):
        """Log action execution to audit trail"""
        log_entry = {
            'execution_id': execution_id,
            'action_name': action_name,
            'user_id': user_id,
            'params': params,
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }

        with self._lock:
            self._execution_log.append(log_entry)

            # Keep only last 10,000 entries in memory
            if len(self._execution_log) > 10000:
                self._execution_log = self._execution_log[-10000:]

        # Also log to database for persistence
        self._persist_to_database(log_entry)

    def _persist_to_database(self, log_entry: Dict[str, Any]):
        """Persist audit log to database"""
        import psycopg2
        import json
        import os

        db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'database': os.getenv('DB_NAME', 'trading'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', '')
        }

        try:
            conn = psycopg2.connect(**db_config)
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO mfa_action_audit_log
                (execution_id, action_name, user_id, params, success, message, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                log_entry['execution_id'],
                log_entry['action_name'],
                log_entry['user_id'],
                json.dumps(log_entry['params']),
                log_entry['success'],
                log_entry['message'],
                log_entry['timestamp']
            ))

            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Failed to persist audit log: {e}")

    # ========================================================================
    # ACTION IMPLEMENTATIONS
    # ========================================================================

    def _execute_robinhood_trade(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a trade on Robinhood"""
        from src.services.robinhood_client import RobinhoodClient

        rh = RobinhoodClient()
        rh.login()

        symbol = params['symbol']
        option_type = params['option_type']  # 'put' or 'call'
        strike = params['strike']
        expiration = params['expiration']
        side = params['side']  # 'buy' or 'sell'
        quantity = params.get('quantity', 1)
        price = params.get('price')  # Limit price (optional)

        # Submit order
        order_result = rh.submit_option_order(
            symbol=symbol,
            option_type=option_type,
            strike=strike,
            expiration=expiration,
            side=side,
            quantity=quantity,
            price=price
        )

        return {
            'order_id': order_result.get('id'),
            'status': order_result.get('state'),
            'filled_quantity': order_result.get('processed_quantity', 0),
            'average_price': order_result.get('average_price')
        }

    def _cancel_robinhood_order(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Cancel a Robinhood order (undo function)"""
        from src.services.robinhood_client import RobinhoodClient

        rh = RobinhoodClient()
        order_id = params['order_id']

        cancel_result = rh.cancel_order(order_id)
        return {'cancelled': True, 'order_id': order_id}

    def _add_to_watchlist(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Add symbol to TradingView watchlist"""
        from src.tradingview_db_manager import TradingViewDBManager

        db = TradingViewDBManager()
        watchlist_name = params.get('watchlist', 'main')
        symbol = params['symbol']

        db.add_symbol_to_watchlist(watchlist_name, symbol)

        return {'added': True, 'symbol': symbol, 'watchlist': watchlist_name}

    def _sync_tradingview(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sync TradingView watchlists"""
        from src.tradingview_api_sync import sync_tradingview_watchlists

        result = sync_tradingview_watchlists()

        return {
            'synced': True,
            'watchlists_count': result.get('watchlists_count', 0),
            'symbols_count': result.get('symbols_count', 0)
        }

    def _run_csp_scan(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run CSP opportunity scan"""
        from src.csp_opportunities_finder import find_csp_opportunities

        min_score = params.get('min_score', 70)
        dte_range = params.get('dte_range', [20, 45])

        opportunities = find_csp_opportunities(
            min_score=min_score,
            dte_min=dte_range[0],
            dte_max=dte_range[1]
        )

        return {
            'opportunities': opportunities,
            'count': len(opportunities)
        }


# ========================================================================
# SINGLETON INSTANCE
# ========================================================================

_action_service_instance = None

def get_action_service() -> ActionExecutionService:
    """Get singleton instance of ActionExecutionService"""
    global _action_service_instance
    if _action_service_instance is None:
        _action_service_instance = ActionExecutionService()
    return _action_service_instance
```

---

## 5. Proactive Management System

### 5.1 Monitoring Architecture

```python
# src/mfa/proactive_management_service.py

from typing import List, Dict, Any, Callable
from dataclasses import dataclass
from datetime import datetime, time
from enum import Enum
import threading
import schedule


class MonitorType(Enum):
    """Types of proactive monitors"""
    POSITION_MONITOR = "position_monitor"
    RISK_MONITOR = "risk_monitor"
    OPPORTUNITY_MONITOR = "opportunity_monitor"
    EARNINGS_MONITOR = "earnings_monitor"
    MARKET_EVENT_MONITOR = "market_event_monitor"


class AlertPriority(Enum):
    """Alert priority levels"""
    LOW = 1      # FYI, no action needed
    MEDIUM = 2   # Should review soon
    HIGH = 3     # Review today
    CRITICAL = 4 # Immediate action required


@dataclass
class ProactiveAlert:
    """An alert generated by proactive monitoring"""
    alert_id: str
    monitor_type: MonitorType
    priority: AlertPriority
    title: str
    message: str
    action_suggestion: str
    data: Dict[str, Any]
    timestamp: datetime


class ProactiveManagementService:
    """
    Service for proactive monitoring and alerting.

    Monitors:
    - All active positions/alerts/markets
    - Portfolio risk metrics
    - Upcoming earnings
    - Market opportunities
    - Unusual market events

    Generates alerts and suggestions for user action.
    """

    def __init__(self):
        self._monitors: Dict[str, Callable] = {}
        self._alerts: List[ProactiveAlert] = []
        self._alert_lock = threading.Lock()
        self._running = False
        self._scheduler_thread = None

        self._register_all_monitors()
        self._schedule_monitors()

    def _register_all_monitors(self):
        """Register all monitoring functions"""
        self._monitors['position_expiration'] = self._monitor_position_expiration
        self._monitors['profit_targets'] = self._monitor_profit_targets
        self._monitors['assignment_risk'] = self._monitor_assignment_risk
        self._monitors['portfolio_delta'] = self._monitor_portfolio_delta
        self._monitors['earnings_risk'] = self._monitor_earnings_risk
        self._monitors['watchlist_opportunities'] = self._monitor_watchlist_opportunities
        self._monitors['unusual_iv'] = self._monitor_unusual_iv
        self._monitors['kalshi_arbitrage'] = self._monitor_kalshi_arbitrage

    def _schedule_monitors(self):
        """Schedule when each monitor runs"""
        # Position monitors (every 1 hour during market hours)
        schedule.every(1).hours.do(self._monitors['position_expiration'])
        schedule.every(1).hours.do(self._monitors['profit_targets'])
        schedule.every(1).hours.do(self._monitors['assignment_risk'])

        # Risk monitors (every 4 hours)
        schedule.every(4).hours.do(self._monitors['portfolio_delta'])

        # Earnings monitor (daily at 7 AM)
        schedule.every().day.at("07:00").do(self._monitors['earnings_risk'])

        # Opportunity monitors (every 30 minutes during market hours)
        schedule.every(30).minutes.do(self._monitors['watchlist_opportunities'])
        schedule.every(30).minutes.do(self._monitors['unusual_iv'])

        # Kalshi monitor (every 15 minutes)
        schedule.every(15).minutes.do(self._monitors['kalshi_arbitrage'])

    def start(self):
        """Start proactive monitoring"""
        if self._running:
            return

        self._running = True
        self._scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self._scheduler_thread.start()

    def stop(self):
        """Stop proactive monitoring"""
        self._running = False

    def _run_scheduler(self):
        """Run the scheduler loop"""
        while self._running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

    def get_active_alerts(self, min_priority: AlertPriority = AlertPriority.LOW) -> List[ProactiveAlert]:
        """Get all active alerts above a certain priority"""
        with self._alert_lock:
            return [
                alert for alert in self._alerts
                if alert.priority.value >= min_priority.value
            ]

    def add_alert(self, alert: ProactiveAlert):
        """Add a new alert"""
        with self._alert_lock:
            self._alerts.append(alert)

            # Keep only last 100 alerts in memory
            if len(self._alerts) > 100:
                self._alerts = self._alerts[-100:]

        # Send notification
        self._send_notification(alert)

    def _send_notification(self, alert: ProactiveAlert):
        """Send notification for alert (Telegram, email, etc.)"""
        # Implementation depends on notification preferences
        pass

    # ========================================================================
    # MONITOR IMPLEMENTATIONS
    # ========================================================================

    def _monitor_position_expiration(self):
        """Monitor positions nearing expiration"""
        from src.mfa.data_integration_service import get_data_service

        data_service = get_data_service()
        positions = data_service.get_active_positions()

        for position in positions:
            dte = position.get('days_to_expiration', 999)

            if dte <= 7:
                # Position expiring within 7 days
                alert = ProactiveAlert(
                    alert_id=f"exp_{position['id']}",
                    monitor_type=MonitorType.POSITION_MONITOR,
                    priority=AlertPriority.HIGH if dte <= 3 else AlertPriority.MEDIUM,
                    title=f"{position['symbol']} Position Expiring Soon",
                    message=f"Your {position['symbol']} {position['strike']} {position['option_type']} expires in {dte} days",
                    action_suggestion="Consider closing for profit, rolling, or letting expire",
                    data=position,
                    timestamp=datetime.now()
                )
                self.add_alert(alert)

    def _monitor_profit_targets(self):
        """Monitor positions that hit profit targets"""
        from src.mfa.data_integration_service import get_data_service

        data_service = get_data_service()
        positions = data_service.get_active_positions()

        for position in positions:
            profit_pct = position.get('profit_percentage', 0)

            if profit_pct >= 50:  # Common profit target
                alert = ProactiveAlert(
                    alert_id=f"profit_{position['id']}",
                    monitor_type=MonitorType.POSITION_MONITOR,
                    priority=AlertPriority.MEDIUM,
                    title=f"{position['symbol']} Hit Profit Target",
                    message=f"Your {position['symbol']} position is up {profit_pct:.1f}% - consider taking profit",
                    action_suggestion="Close position to lock in gains",
                    data=position,
                    timestamp=datetime.now()
                )
                self.add_alert(alert)

    def _monitor_assignment_risk(self):
        """Monitor positions at risk of assignment"""
        from src.mfa.data_integration_service import get_data_service

        data_service = get_data_service()
        positions = data_service.get_active_positions()

        for position in positions:
            if position.get('option_type') == 'put':
                current_price = position.get('current_stock_price', 0)
                strike = position.get('strike', 0)

                if current_price < strike:  # ITM
                    distance = ((strike - current_price) / strike) * 100

                    alert = ProactiveAlert(
                        alert_id=f"assign_{position['id']}",
                        monitor_type=MonitorType.RISK_MONITOR,
                        priority=AlertPriority.HIGH if distance > 2 else AlertPriority.MEDIUM,
                        title=f"{position['symbol']} Assignment Risk",
                        message=f"{position['symbol']} is ${current_price:.2f}, put strike is ${strike:.2f} - {distance:.1f}% ITM",
                        action_suggestion="Consider rolling, closing, or prepare for assignment",
                        data=position,
                        timestamp=datetime.now()
                    )
                    self.add_alert(alert)

    def _monitor_portfolio_delta(self):
        """Monitor overall portfolio delta exposure"""
        from src.mfa.data_integration_service import get_data_service

        data_service = get_data_service()
        positions = data_service.get_active_positions()

        total_delta = sum(pos.get('delta', 0) for pos in positions)

        if abs(total_delta) > 0.5:  # Threshold for delta exposure
            alert = ProactiveAlert(
                alert_id="portfolio_delta",
                monitor_type=MonitorType.RISK_MONITOR,
                priority=AlertPriority.MEDIUM,
                title="High Portfolio Delta Exposure",
                message=f"Your portfolio delta is {total_delta:.2f} - consider hedging",
                action_suggestion="Add opposite delta positions to neutralize",
                data={'total_delta': total_delta, 'positions': positions},
                timestamp=datetime.now()
            )
            self.add_alert(alert)

    def _monitor_earnings_risk(self):
        """Monitor positions with upcoming earnings before expiration"""
        from src.mfa.data_integration_service import get_data_service

        data_service = get_data_service()
        risky_positions = data_service.check_position_earnings_risk()

        for pos_data in risky_positions:
            days_until_earnings = pos_data.get('days_until_earnings', 999)

            if days_until_earnings <= 7:
                alert = ProactiveAlert(
                    alert_id=f"earnings_{pos_data['position']['id']}",
                    monitor_type=MonitorType.EARNINGS_MONITOR,
                    priority=AlertPriority.HIGH if days_until_earnings <= 3 else AlertPriority.MEDIUM,
                    title=f"{pos_data['position']['symbol']} Earnings Risk",
                    message=f"{pos_data['position']['symbol']} reports earnings in {days_until_earnings} days, before your position expires",
                    action_suggestion="Close position before earnings or accept volatility risk",
                    data=pos_data,
                    timestamp=datetime.now()
                )
                self.add_alert(alert)

    def _monitor_watchlist_opportunities(self):
        """Monitor watchlists for new opportunities"""
        from src.mfa.data_integration_service import get_data_service

        data_service = get_data_service()
        watchlists = data_service.get_watchlists()

        for watchlist in watchlists:
            opportunities = data_service.find_watchlist_opportunities(
                watchlist['name'],
                min_score=80  # High-quality only
            )

            if opportunities:
                alert = ProactiveAlert(
                    alert_id=f"opp_{watchlist['name']}",
                    monitor_type=MonitorType.OPPORTUNITY_MONITOR,
                    priority=AlertPriority.LOW,
                    title=f"New Opportunities in {watchlist['name']}",
                    message=f"Found {len(opportunities)} high-quality opportunities in your {watchlist['name']} watchlist",
                    action_suggestion="Review opportunities and consider trades",
                    data={'watchlist': watchlist['name'], 'opportunities': opportunities},
                    timestamp=datetime.now()
                )
                self.add_alert(alert)

    def _monitor_unusual_iv(self):
        """Monitor for unusual IV spikes"""
        # Implementation would check for IV rank > 80 on watchlist stocks
        pass

    def _monitor_kalshi_arbitrage(self):
        """Monitor for Kalshi arbitrage opportunities"""
        # Implementation would compare AI predictions vs market prices
        pass


# ========================================================================
# SINGLETON INSTANCE
# ========================================================================

_proactive_service_instance = None

def get_proactive_service() -> ProactiveManagementService:
    """Get singleton instance of ProactiveManagementService"""
    global _proactive_service_instance
    if _proactive_service_instance is None:
        _proactive_service_instance = ProactiveManagementService()
    return _proactive_service_instance
```

---

## 6. Feature Discovery & Intent Mapping

### 6.1 Intent Classification System

```python
# src/mfa/intent_classifier.py

from typing import Dict, List, Tuple
from enum import Enum
from dataclasses import dataclass


class UserIntent(Enum):
    """All possible user intents"""
    # Portfolio Management
    PORTFOLIO_STATUS = "portfolio_status"
    POSITION_DETAILS = "position_details"
    TRADE_HISTORY = "trade_history"
    PROFIT_LOSS = "profit_loss"

    # Position Analysis
    CLOSE_POSITION = "close_position"
    ROLL_POSITION = "roll_position"
    ASSIGNMENT_CHECK = "assignment_check"
    PROFIT_TARGET_CHECK = "profit_target_check"

    # Opportunity Finding
    FIND_CSP_OPPORTUNITY = "find_csp_opportunity"
    FIND_COVERED_CALL = "find_covered_call"
    FIND_CALENDAR_SPREAD = "find_calendar_spread"
    SCAN_WATCHLIST = "scan_watchlist"

    # Market Research
    RESEARCH_STOCK = "research_stock"
    CHECK_EARNINGS = "check_earnings"
    ANALYZE_IV = "analyze_iv"
    GET_STOCK_RATING = "get_stock_rating"

    # Risk Management
    CHECK_PORTFOLIO_RISK = "check_portfolio_risk"
    CHECK_EARNINGS_RISK = "check_earnings_risk"
    CHECK_DELTA_EXPOSURE = "check_delta_exposure"
    SUGGEST_HEDGES = "suggest_hedges"

    # Trade Execution
    EXECUTE_TRADE = "execute_trade"
    CANCEL_ORDER = "cancel_order"
    CHECK_ORDER_STATUS = "check_order_status"

    # Data Management
    SYNC_TRADINGVIEW = "sync_tradingview"
    ADD_TO_WATCHLIST = "add_to_watchlist"
    SCAN_DATABASE = "scan_database"

    # Prediction Markets
    CHECK_NFL_PREDICTIONS = "check_nfl_predictions"
    CHECK_KALSHI_MARKETS = "check_kalshi_markets"
    FIND_MISPRICED_MARKETS = "find_mispriced_markets"

    # Xtrades
    CHECK_XTRADES_ALERTS = "check_xtrades_alerts"
    FOLLOW_TRADER = "follow_trader"

    # Education
    EXPLAIN_CONCEPT = "explain_concept"
    LEARN_STRATEGY = "learn_strategy"

    # General
    UNKNOWN = "unknown"


@dataclass
class IntentMapping:
    """Mapping from intent to Magnus features"""
    intent: UserIntent
    primary_feature: str          # Main feature to use
    secondary_features: List[str]  # Additional features that may be needed
    requires_parameters: List[str] # Required parameters
    example_queries: List[str]    # Example user queries


class IntentClassifier:
    """
    Classifies user intents and maps them to Magnus features.

    This is the intelligence that determines which feature(s) to activate
    based on what the user asks.
    """

    def __init__(self):
        self._intent_mappings: Dict[UserIntent, IntentMapping] = {}
        self._keyword_patterns: Dict[str, UserIntent] = {}
        self._initialize_mappings()

    def _initialize_mappings(self):
        """Initialize intent → feature mappings"""

        # Portfolio Status
        self._intent_mappings[UserIntent.PORTFOLIO_STATUS] = IntentMapping(
            intent=UserIntent.PORTFOLIO_STATUS,
            primary_feature="dashboard",
            secondary_features=["positions"],
            requires_parameters=[],
            example_queries=[
                "How is my portfolio doing?",
                "What's my current status?",
                "Portfolio summary",
                "How much money do I have?"
            ]
        )

        # Position Details
        self._intent_mappings[UserIntent.POSITION_DETAILS] = IntentMapping(
            intent=UserIntent.POSITION_DETAILS,
            primary_feature="positions",
            secondary_features=["dashboard"],
            requires_parameters=[],
            example_queries=[
                "Show me my positions",
                "What positions do I have?",
                "List my active trades",
                "Which options am I holding?"
            ]
        )

        # Find CSP Opportunity
        self._intent_mappings[UserIntent.FIND_CSP_OPPORTUNITY] = IntentMapping(
            intent=UserIntent.FIND_CSP_OPPORTUNITY,
            primary_feature="opportunities",
            secondary_features=["ai_research", "earnings"],
            requires_parameters=[],
            example_queries=[
                "Find me a CSP opportunity",
                "Find a good put to sell",
                "What's a good cash-secured put?",
                "Find me a trade"
            ]
        )

        # Research Stock
        self._intent_mappings[UserIntent.RESEARCH_STOCK] = IntentMapping(
            intent=UserIntent.RESEARCH_STOCK,
            primary_feature="ai_research",
            secondary_features=["earnings", "opportunities"],
            requires_parameters=["symbol"],
            example_queries=[
                "Research AAPL for me",
                "What do you think about NVDA?",
                "Analyze TSLA",
                "Is MSFT a good buy?"
            ]
        )

        # Check Earnings
        self._intent_mappings[UserIntent.CHECK_EARNINGS] = IntentMapping(
            intent=UserIntent.CHECK_EARNINGS,
            primary_feature="earnings",
            secondary_features=["positions"],
            requires_parameters=[],
            example_queries=[
                "When is AAPL earnings?",
                "Do I have any earnings risk?",
                "Which stocks report earnings this week?",
                "Show me the earnings calendar"
            ]
        )

        # Scan Watchlist
        self._intent_mappings[UserIntent.SCAN_WATCHLIST] = IntentMapping(
            intent=UserIntent.SCAN_WATCHLIST,
            primary_feature="tradingview",
            secondary_features=["opportunities"],
            requires_parameters=[],
            example_queries=[
                "Scan my watchlist",
                "Find opportunities in my watchlist",
                "What's good in my TradingView list?",
                "Check my watchlist for setups"
            ]
        )

        # NFL Predictions
        self._intent_mappings[UserIntent.CHECK_NFL_PREDICTIONS] = IntentMapping(
            intent=UserIntent.CHECK_NFL_PREDICTIONS,
            primary_feature="kalshi",
            secondary_features=[],
            requires_parameters=[],
            example_queries=[
                "What's the prediction for Sunday's games?",
                "NFL predictions",
                "Show me Kalshi NFL markets",
                "Who's favored in the Chiefs game?"
            ]
        )

        # Execute Trade
        self._intent_mappings[UserIntent.EXECUTE_TRADE] = IntentMapping(
            intent=UserIntent.EXECUTE_TRADE,
            primary_feature="positions",
            secondary_features=["dashboard"],
            requires_parameters=["symbol", "strike", "expiration", "action"],
            example_queries=[
                "Sell a put on AAPL at $170",
                "Execute this trade: TSLA $240 put 30 DTE",
                "Close my NVDA position",
                "Buy to close my SPY put"
            ]
        )

        # ... add all other intent mappings

        # Build keyword patterns for fast lookup
        self._build_keyword_patterns()

    def _build_keyword_patterns(self):
        """Build keyword → intent mappings for fast classification"""
        patterns = {
            # Portfolio keywords
            ("portfolio", "status"): UserIntent.PORTFOLIO_STATUS,
            ("portfolio", "balance"): UserIntent.PORTFOLIO_STATUS,
            ("how", "doing"): UserIntent.PORTFOLIO_STATUS,

            # Position keywords
            ("my", "positions"): UserIntent.POSITION_DETAILS,
            ("show", "positions"): UserIntent.POSITION_DETAILS,
            ("active", "trades"): UserIntent.POSITION_DETAILS,

            # Opportunity keywords
            ("find", "csp"): UserIntent.FIND_CSP_OPPORTUNITY,
            ("find", "opportunity"): UserIntent.FIND_CSP_OPPORTUNITY,
            ("find", "trade"): UserIntent.FIND_CSP_OPPORTUNITY,
            ("good", "put"): UserIntent.FIND_CSP_OPPORTUNITY,

            # Research keywords
            ("research",): UserIntent.RESEARCH_STOCK,
            ("analyze",): UserIntent.RESEARCH_STOCK,
            ("what", "think", "about"): UserIntent.RESEARCH_STOCK,
            ("is", "good", "buy"): UserIntent.RESEARCH_STOCK,

            # Earnings keywords
            ("earnings", "when"): UserIntent.CHECK_EARNINGS,
            ("earnings", "risk"): UserIntent.CHECK_EARNINGS_RISK,
            ("earnings", "calendar"): UserIntent.CHECK_EARNINGS,

            # Watchlist keywords
            ("scan", "watchlist"): UserIntent.SCAN_WATCHLIST,
            ("watchlist", "opportunities"): UserIntent.SCAN_WATCHLIST,

            # NFL keywords
            ("nfl", "predictions"): UserIntent.CHECK_NFL_PREDICTIONS,
            ("nfl", "games"): UserIntent.CHECK_NFL_PREDICTIONS,
            ("sunday", "games"): UserIntent.CHECK_NFL_PREDICTIONS,

            # Trade execution keywords
            ("sell", "put"): UserIntent.EXECUTE_TRADE,
            ("execute", "trade"): UserIntent.EXECUTE_TRADE,
            ("close", "position"): UserIntent.CLOSE_POSITION,
        }

        self._keyword_patterns = patterns

    def classify(self, user_message: str) -> Tuple[UserIntent, float]:
        """
        Classify user intent from message.

        Args:
            user_message: User's natural language message

        Returns:
            Tuple of (UserIntent, confidence_score)
        """
        message_lower = user_message.lower()
        words = message_lower.split()

        # Check keyword patterns
        for pattern, intent in self._keyword_patterns.items():
            if all(word in message_lower for word in pattern):
                return (intent, 0.9)  # High confidence for keyword match

        # Fallback: Use LLM for classification (more expensive but accurate)
        intent = self._classify_with_llm(user_message)
        return (intent, 0.7)  # Medium confidence for LLM classification

    def _classify_with_llm(self, user_message: str) -> UserIntent:
        """Use LLM to classify intent (fallback)"""
        # Implementation would use a fast, free LLM (Groq)
        # to classify the intent when keywords don't match
        return UserIntent.UNKNOWN

    def get_feature_for_intent(self, intent: UserIntent) -> IntentMapping:
        """Get feature mapping for an intent"""
        return self._intent_mappings.get(intent)
```

---

## 7. System Integration Diagrams

### 7.1 Complete Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                      USER INPUT                                  │
│                                                                  │
│  "Find me a CSP opportunity on a stock from my watchlist        │
│   that has a bullish AI rating and no earnings this month"      │
└───────────────────────┬─────────────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────────────┐
│              INTENT CLASSIFIER                                 │
│  ✓ Primary: FIND_CSP_OPPORTUNITY                              │
│  ✓ Requires: TradingView, AI Research, Earnings, Opportunities│
└───────────────────────┬───────────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────────────┐
│         CONVERSATION ORCHESTRATOR (LangGraph)                 │
│  Creates multi-step plan:                                     │
│  1. Get watchlist symbols (TradingView)                      │
│  2. Get AI ratings for those symbols (AI Research)            │
│  3. Filter to bullish ratings                                 │
│  4. Check earnings dates (Earnings Calendar)                  │
│  5. Scan filtered symbols for CSP opportunities               │
└───────────────────────┬───────────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────────────┐
│         DATA INTEGRATION SERVICE                               │
│  Executes plan using unified interface:                        │
│                                                                │
│  Step 1: data_service.get_watchlist_symbols("main")          │
│          → ["AAPL", "NVDA", "TSLA", "MSFT", ...]             │
│                                                                │
│  Step 2: for symbol in symbols:                               │
│            ai_rating = data_service.get_stock_rating(symbol)  │
│          → {AAPL: "HOLD", NVDA: "BUY", TSLA: "BUY", ...}     │
│                                                                │
│  Step 3: bullish = [s for s, r in ratings if r == "BUY"]     │
│          → ["NVDA", "TSLA"]                                   │
│                                                                │
│  Step 4: for symbol in bullish:                               │
│            earnings = data_service.get_earnings_date(symbol)  │
│          → {NVDA: "2025-02-15", TSLA: None}                  │
│          Filter: [s for s in bullish if no earnings in 30d]   │
│          → ["TSLA"]                                           │
│                                                                │
│  Step 5: opps = data_service.scan_csp_opportunities(          │
│            symbols=["TSLA"], min_score=70                      │
│          )                                                     │
│          → [TSLA $240 PUT, TSLA $235 PUT, ...]               │
└───────────────────────┬───────────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────────────┐
│         FEATURE CONNECTORS (Parallel Execution)                │
│                                                                │
│  ┌─────────────────┐  ┌──────────────────┐  ┌──────────────┐│
│  │ TradingView     │  │ AI Research      │  │ Earnings     ││
│  │ Connector       │  │ Connector        │  │ Connector    ││
│  │                 │  │                  │  │              ││
│  │ DB: watchlist_  │  │ DB: ai_analysis │  │ DB: earnings ││
│  │     symbols     │  │ Cache: 1hr TTL   │  │     _dates   ││
│  └─────────────────┘  └──────────────────┘  └──────────────┘│
│                                                                │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ Opportunities Connector                                  │ │
│  │                                                          │ │
│  │ DB: opportunities, options_chain                         │ │
│  │ External: Robinhood (options data), yfinance (prices)    │ │
│  │ Cache: 5min TTL                                          │ │
│  └─────────────────────────────────────────────────────────┘ │
└───────────────────────┬───────────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────────────┐
│         RESPONSE SYNTHESIZER                                   │
│  Combines all results into natural language response:          │
│                                                                │
│  "I found 3 excellent CSP opportunities for you:              │
│                                                                │
│  1. TSLA $240 PUT (30 DTE) - Score: 92/100                   │
│     • Premium: $3.20 (1.3% return, 16% annualized)           │
│     • AI Rating: BUY (bullish trend confirmed)                │
│     • No earnings until 4/20 (after expiration) ✓            │
│     • From your 'main' watchlist                             │
│     • Probability of profit: 68%                              │
│                                                                │
│  Would you like me to analyze any of these in more detail?"   │
└───────────────────────┬───────────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────────────┐
│                    USER OUTPUT                                 │
│  • Text response (Streamlit chat)                             │
│  • Voice response (TTS, optional)                              │
│  • Action buttons ("Analyze TSLA", "Execute Trade")           │
└───────────────────────────────────────────────────────────────┘
```

---

## 8. Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)

**Goal**: Build core data integration layer and basic conversational interface

**Tasks**:
1. Implement `DataIntegrationService` base classes
2. Create first 5 connectors:
   - Dashboard Connector
   - Positions Connector
   - Opportunities Connector
   - TradingView Connector
   - AI Research Connector
3. Build `IntentClassifier` with 10 most common intents
4. Create basic Streamlit chat interface
5. Test end-to-end: "What's my portfolio status?"

**Deliverables**:
- `src/mfa/data_integration_service.py` (complete)
- `src/mfa/connectors/` (5 connectors working)
- `src/mfa/intent_classifier.py` (basic version)
- `financial_assistant_page.py` (chat interface)
- Integration tests passing

---

### Phase 2: Complete Feature Integration (Weeks 3-4)

**Goal**: Connect ALL Magnus features to MFA

**Tasks**:
1. Implement remaining 16 connectors:
   - Kalshi, Xtrades, Earnings, Calendar Spreads, etc.
2. Add all 30+ user intents to classifier
3. Implement cross-feature intelligence methods
4. Build `ActionExecutionService` with 10 core actions
5. Test complex queries spanning multiple features

**Deliverables**:
- All 21 connectors operational
- Full intent classification (30+ intents)
- Action execution working for trades, scans, syncs
- Cross-feature queries working
- Integration test suite complete

---

### Phase 3: Proactive Management (Weeks 5-6)

**Goal**: Make MFA proactive and intelligent

**Tasks**:
1. Implement `ProactiveManagementService`
2. Build 8 monitoring functions
3. Create alert generation and notification system
4. Integrate with Telegram for mobile alerts
5. Add daily/weekly summary reports

**Deliverables**:
- Proactive monitoring running 24/7
- Alerts generating correctly
- Telegram notifications working
- Daily portfolio summary email/message
- Alert management UI in Streamlit

---

### Phase 4: Production Hardening (Weeks 7-8)

**Goal**: Production-ready system with safety, performance, monitoring

**Tasks**:
1. Implement comprehensive error handling
2. Add caching optimization across all connectors
3. Build audit logging and compliance features
4. Create admin dashboard for monitoring MFA
5. Write documentation and user guide
6. Performance testing and optimization

**Deliverables**:
- Zero-downtime operation
- Sub-3s response time (95th percentile)
- Complete audit trail
- Admin monitoring dashboard
- User documentation published
- Ready for production deployment

---

## 9. Testing & Validation Strategy

### 9.1 Unit Tests

**Test Coverage**: >90% for core services

```python
# tests/mfa/test_data_integration_service.py

def test_dashboard_connector():
    """Test dashboard connector retrieves balance correctly"""
    service = DataIntegrationService()
    result = service.get_portfolio_balance()
    assert isinstance(result, float)
    assert result >= 0

def test_cross_feature_query():
    """Test cross-feature intelligence"""
    service = DataIntegrationService()
    risky_positions = service.check_position_earnings_risk()
    assert isinstance(risky_positions, list)
    # Should contain position details + earnings dates

def test_cache_invalidation():
    """Test cache invalidates correctly"""
    connector = DashboardConnector()
    # Fetch data (should cache)
    data1 = connector.get_cached_or_fetch("test", {"type": "get_balance"})
    # Invalidate cache
    connector.invalidate_cache("test")
    # Fetch again (should fetch fresh)
    data2 = connector.get_cached_or_fetch("test", {"type": "get_balance"})
    # Implementation should track cache hits/misses
```

### 9.2 Integration Tests

**Test Real Workflows**:

```python
def test_find_watchlist_opportunities():
    """Test complete workflow: watchlist → opportunities"""
    service = DataIntegrationService()

    # Get watchlist symbols
    symbols = service.get_watchlist_symbols("high_iv")
    assert len(symbols) > 0

    # Scan those symbols
    opportunities = service.scan_csp_opportunities(
        symbols=symbols,
        min_score=70
    )

    assert len(opportunities) > 0
    assert all(opp['symbol'] in symbols for opp in opportunities)

def test_earnings_risk_check():
    """Test earnings risk detection"""
    service = DataIntegrationService()

    risky = service.check_position_earnings_risk()

    for item in risky:
        assert 'position' in item
        assert 'earnings_date' in item
        # Earnings should be before expiration
        assert item['earnings_date'] < item['expiration_date']
```

### 9.3 Performance Tests

```python
def test_response_time():
    """Test response times meet SLA"""
    service = DataIntegrationService()

    import time
    start = time.time()
    result = service.get_portfolio_summary()
    duration = time.time() - start

    assert duration < 3.0  # Must respond within 3 seconds

def test_concurrent_queries():
    """Test service handles concurrent requests"""
    import concurrent.futures

    service = DataIntegrationService()

    def query():
        return service.get_portfolio_balance()

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(query) for _ in range(100)]
        results = [f.result() for f in futures]

    assert len(results) == 100
    assert all(isinstance(r, float) for r in results)
```

---

## 10. Performance & Scalability

### 10.1 Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Response Time (p95) | <3 seconds | Time from user query to response |
| Response Time (p99) | <5 seconds | Worst-case response time |
| Throughput | 100 queries/minute | Concurrent user requests |
| Cache Hit Rate | >80% | Percentage served from cache |
| Database Query Time | <500ms | PostgreSQL query execution |
| External API Time | <2s | Robinhood, Kalshi, TradingView |
| Memory Usage | <2GB | Peak memory for all services |
| CPU Usage | <50% | Average CPU utilization |

### 10.2 Caching Strategy

**Multi-Level Caching**:

```
Level 1: In-Memory Cache (Python dicts)
  - TTL: 30s - 5min depending on data type
  - Size: Max 1,000 items per connector
  - Eviction: LRU

Level 2: Redis Cache (Optional)
  - TTL: 5min - 1hour
  - Size: Unlimited
  - Eviction: TTL-based

Level 3: Database (PostgreSQL)
  - Persistent storage
  - Indexed for fast queries
```

**Cache Policies by Data Type**:

| Data Type | TTL | Rationale |
|-----------|-----|-----------|
| Portfolio Balance | 60s | Changes frequently but not real-time |
| Active Positions | 30s | Near real-time updates needed |
| Trade History | 5min | Historical data, rarely changes |
| Options Chains | 5min | Market data updates frequently |
| AI Research Results | 1hour | Expensive to compute, slow-changing |
| Watchlist Symbols | 30min | User-managed, infrequent changes |
| Earnings Dates | 24hours | Event data, rarely changes |
| Kalshi Markets | 5min | Prediction market prices update frequently |

### 10.3 Scalability Considerations

**Horizontal Scaling**:
- Stateless design allows multiple MFA instances
- Load balancer distributes requests
- Shared PostgreSQL and Redis backend

**Database Optimization**:
- Indexes on all foreign keys
- Materialized views for complex queries
- Partitioning for large tables (trade_history)

**External API Rate Limiting**:
- Robinhood: Max 60 req/min (client rate-limited)
- Kalshi: Max 100 req/min
- TradingView: Session-based (no explicit limit)
- LLM APIs: Varies by provider (handled by service layer)

---

## 11. Security & Compliance

### 11.1 Security Measures

**Authentication**:
- User sessions managed by Streamlit
- API keys encrypted in PostgreSQL
- OAuth2 for Robinhood

**Authorization**:
- Action-level permissions
- Trade execution requires verified user
- Audit trail for all actions

**Data Protection**:
- Credentials encrypted at rest
- No sensitive data in logs
- HTTPS for all external API calls

### 11.2 Compliance

**Financial Disclaimers**:
- Displayed on first MFA interaction
- Repeated before trade execution
- Logged in database

**Audit Trail**:
- All actions logged with:
  - User ID
  - Timestamp
  - Action type
  - Parameters
  - Result (success/failure)
  - Execution duration
- Retained for 1 year

---

## 12. Success Metrics

### 12.1 Technical Metrics

- [ ] All 21 Magnus features integrated
- [ ] Response time <3s (p95)
- [ ] Cache hit rate >80%
- [ ] Zero data loss incidents
- [ ] >99% uptime

### 12.2 User Metrics

- [ ] 80%+ of users interact with MFA weekly
- [ ] Average 20+ queries per user per week
- [ ] 4.5/5 satisfaction rating
- [ ] 30%+ time savings vs manual workflow

### 12.3 Business Metrics

- [ ] Increased user retention (+20%)
- [ ] Faster trade execution (via voice/chat)
- [ ] Higher feature discovery (users find features via MFA)
- [ ] Competitive differentiation (unique in market)

---

## Conclusion

This integration architecture provides **complete, robust access** to the entire Magnus ecosystem through the Financial Assistant. Every feature, every data source, every capability is accessible through natural conversation.

**Key Innovations**:
1. **Unified Data Access Layer** - Single interface to 21+ features
2. **Cross-Feature Intelligence** - Combines data across features for insights
3. **Action Execution Framework** - Safe, audited execution of trades and operations
4. **Proactive Management** - 24/7 monitoring with intelligent alerts
5. **Intent-Driven Architecture** - Natural language maps to features automatically

**Next Steps**:
1. Review and approve architecture
2. Begin Phase 1 implementation
3. Iterate based on user feedback
4. Scale to production

---

**Document Status**: ✅ Complete - Ready for Implementation
