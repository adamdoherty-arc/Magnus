# AVA Chatbot Deep Review & Enhancement Plan

**Date:** November 15, 2025  
**Review Type:** Comprehensive System Access Audit  
**Status:** 🔄 **IN PROGRESS**

---

## Executive Summary

**Current Status:**
- ✅ AVA has 6 basic tools
- ⚠️ **Major Gap:** AVA cannot access most project data
- ⚠️ **Critical:** No tools for sports betting, Kalshi markets, game watchlists, Xtrades, earnings, etc.
- ⚠️ **Issue:** Database access is generic SQL only - no specialized tools

**Recommendation:**
1. Add 20+ specialized database query tools
2. Add data source access tools (ESPN, Kalshi, Robinhood, etc.)
3. Create unified data access layer
4. Document all available data sources

---

## 1. Current AVA Tools (6 Total)

### ✅ Existing Tools

| Tool | Purpose | Status | Limitations |
|------|---------|--------|-------------|
| `query_database_tool` | Generic SQL queries | ✅ Working | User must know SQL and table names |
| `analyze_watchlist_tool` | Stock watchlist analysis | ✅ Working | Only stock watchlists, not sports |
| `get_portfolio_status_tool` | Robinhood portfolio | ✅ Working | Only Robinhood, no other brokers |
| `create_task_tool` | Task management | ✅ Working | Good |
| `get_stock_price_tool` | Stock prices | ✅ Working | Only Robinhood |
| `search_magnus_knowledge_tool` | RAG knowledge base | ✅ Working | Good |

**Gap Analysis:**
- ❌ No sports betting data access
- ❌ No Kalshi markets access
- ❌ No game watchlist access
- ❌ No Xtrades data access
- ❌ No earnings calendar access
- ❌ No options data access
- ❌ No ESPN live scores access
- ❌ No task query tools (only create)
- ❌ No position/recommendation access

---

## 2. Complete Database Schema Inventory

### 2.1 Core Trading Tables

| Table | Purpose | Key Fields | Access Needed |
|-------|---------|------------|---------------|
| `stock_holdings` | User stock positions | symbol, shares, cost_basis | ✅ Need tool |
| `watchlist` | Stock watchlist | symbol, target_price, priority | ✅ Has tool |
| `opportunities` | Trading opportunities | symbol, strategy, premium, confidence | ✅ Need tool |
| `trade_history` | Historical trades | symbol, strategy, profit_loss | ✅ Need tool |
| `positions` | Current positions | symbol, quantity, entry_price | ✅ Need tool |

### 2.2 Sports Betting Tables

| Table | Purpose | Key Fields | Access Needed |
|-------|---------|------------|---------------|
| `kalshi_markets` | Prediction markets | ticker, title, yes_price, volume | ❌ **CRITICAL MISSING** |
| `kalshi_predictions` | AI predictions | market_id, confidence, edge | ❌ **CRITICAL MISSING** |
| `game_watchlist` | Watched games | game_id, user_id, selected_team | ❌ **CRITICAL MISSING** |
| `nfl_games` | NFL game data | game_id, teams, scores, status | ❌ **CRITICAL MISSING** |
| `ncaa_games` | NCAA game data | game_id, teams, scores, status | ❌ **CRITICAL MISSING** |

### 2.3 Xtrades Tables

| Table | Purpose | Key Fields | Access Needed |
|-------|---------|------------|---------------|
| `xtrades_profiles` | Monitored profiles | username, display_name, active | ❌ **CRITICAL MISSING** |
| `xtrades_trades` | Scraped trades | profile_id, ticker, strategy, entry | ❌ **CRITICAL MISSING** |
| `xtrades_notifications` | Trade alerts | trade_id, sent_at, status | ❌ **CRITICAL MISSING** |
| `xtrades_sync_log` | Sync history | profile_id, sync_time, status | ❌ **CRITICAL MISSING** |

### 2.4 Task Management Tables

| Table | Purpose | Key Fields | Access Needed |
|-------|---------|------------|---------------|
| `development_tasks` | Development tasks | title, status, priority, assigned_agent | ❌ **CRITICAL MISSING** |
| `qa_tasks` | QA tasks | task_id, status, verification | ❌ **CRITICAL MISSING** |
| `qa_agent_sign_offs` | QA sign-offs | task_id, agent, status | ❌ **CRITICAL MISSING** |

### 2.5 Options & Analytics Tables

| Table | Purpose | Key Fields | Access Needed |
|-------|---------|------------|---------------|
| `options_chains` | Options data | symbol, expiration, strike, greeks | ❌ **CRITICAL MISSING** |
| `stock_data` | Stock market data | symbol, price, volume, market_cap | ❌ **CRITICAL MISSING** |
| `supply_demand_zones` | Technical zones | symbol, zone_type, price_level | ❌ **CRITICAL MISSING** |
| `position_recommendations` | AI recommendations | symbol, strategy, confidence | ❌ **CRITICAL MISSING** |

### 2.6 Earnings & Calendar Tables

| Table | Purpose | Key Fields | Access Needed |
|-------|---------|------------|---------------|
| `earnings_calendar` | Upcoming earnings | symbol, earnings_date, estimate | ❌ **CRITICAL MISSING** |
| `earnings_history` | Past earnings | symbol, date, actual, estimate | ❌ **CRITICAL MISSING** |

### 2.7 AVA/RAG Tables

| Table | Purpose | Key Fields | Access Needed |
|-------|---------|------------|---------------|
| `conversation_memory` | Chat history | user_id, message, timestamp | ✅ Has state manager |
| `rag_documents` | Knowledge base | document_id, content, metadata | ✅ Has RAG service |

---

## 3. External Data Sources Inventory

### 3.1 Sports Data Sources

| Source | Purpose | Access Method | Status | AVA Access |
|--------|---------|---------------|--------|------------|
| **ESPN API** | Live NFL/NCAA scores | `src/espn_live_data.py` | ✅ Working | ❌ **MISSING** |
| **ESPN NCAA API** | College football scores | `src/espn_ncaa_live_data.py` | ✅ Working | ❌ **MISSING** |
| **Kalshi API** | Prediction markets | `src/kalshi_client.py` | ✅ Working | ❌ **MISSING** |
| **Kalshi Public API** | Public market data | `src/kalshi_public_client.py` | ✅ Working | ❌ **MISSING** |

### 3.2 Trading Data Sources

| Source | Purpose | Access Method | Status | AVA Access |
|--------|---------|---------------|--------|------------|
| **Robinhood** | Portfolio, prices, options | `src/services/robinhood_client.py` | ✅ Working | ⚠️ Partial (only portfolio) |
| **Yahoo Finance** | Stock prices, options | `yfinance` library | ✅ Working | ❌ **MISSING** |
| **Alpha Vantage** | Stock data, fundamentals | API key required | ✅ Configured | ❌ **MISSING** |
| **Polygon.io** | Market data | API key required | ✅ Configured | ❌ **MISSING** |
| **Finnhub** | Real-time quotes | API key required | ✅ Configured | ❌ **MISSING** |

### 3.3 Other Data Sources

| Source | Purpose | Access Method | Status | AVA Access |
|--------|---------|---------------|--------|------------|
| **TradingView** | Watchlists, charts | `src/tradingview_db_manager.py` | ✅ Working | ❌ **MISSING** |
| **Xtrades.net** | Trade alerts | `src/xtrades_scraper.py` | ✅ Working | ❌ **MISSING** |
| **Telegram** | Notifications | `src/telegram_notifier.py` | ✅ Working | ❌ **MISSING** |

---

## 4. Critical Gaps Identified

### 4.1 Sports Betting (HIGH PRIORITY)

**Missing Tools:**
1. ❌ `get_kalshi_markets_tool` - Query Kalshi prediction markets
2. ❌ `get_live_games_tool` - Get ESPN live scores
3. ❌ `get_game_watchlist_tool` - Get user's watched games
4. ❌ `get_ai_predictions_tool` - Get AI betting predictions
5. ❌ `get_betting_opportunities_tool` - Find high-EV bets

**Impact:** AVA cannot answer questions about:
- "What are the best betting opportunities right now?"
- "What games am I watching?"
- "What does AI predict for the Chiefs game?"
- "Show me Kalshi odds for NFL games"

### 4.2 Trading & Options (HIGH PRIORITY)

**Missing Tools:**
1. ❌ `get_options_chain_tool` - Query options chains
2. ❌ `get_stock_data_tool` - Get comprehensive stock data (not just price)
3. ❌ `get_trading_opportunities_tool` - Find CSP/CC opportunities
4. ❌ `get_positions_tool` - Get current positions
5. ❌ `get_trade_history_tool` - Query trade history

**Impact:** AVA cannot answer questions about:
- "What options are available for AAPL?"
- "Show me my current positions"
- "What are the best CSP opportunities?"
- "What's my trade history?"

### 4.3 Xtrades Integration (MEDIUM PRIORITY)

**Missing Tools:**
1. ❌ `get_xtrades_profiles_tool` - Get monitored profiles
2. ❌ `get_xtrades_trades_tool` - Get recent trades from profiles
3. ❌ `get_xtrades_consensus_tool` - Get AI consensus on trades

**Impact:** AVA cannot answer questions about:
- "What trades did [profile] make?"
- "What's the consensus on NVDA calls?"
- "Show me recent Xtrades alerts"

### 4.4 Task Management (MEDIUM PRIORITY)

**Missing Tools:**
1. ❌ `get_tasks_tool` - Query tasks (can only create, not read)
2. ❌ `get_qa_tasks_tool` - Get QA tasks
3. ❌ `update_task_tool` - Update task status

**Impact:** AVA cannot answer questions about:
- "What tasks are pending?"
- "Show me QA tasks"
- "What's the status of task #123?"

### 4.5 Earnings & Calendar (LOW PRIORITY)

**Missing Tools:**
1. ❌ `get_earnings_calendar_tool` - Get upcoming earnings
2. ❌ `get_earnings_history_tool` - Get past earnings data

**Impact:** AVA cannot answer questions about:
- "When does AAPL report earnings?"
- "What was AAPL's last earnings surprise?"

---

## 5. Recommended Tool Additions

### 5.1 Sports Betting Tools (Priority 1)

```python
@tool
def get_kalshi_markets_tool(sport: str = "nfl", status: str = "active", limit: int = 10) -> str:
    """Get Kalshi prediction markets for NFL or NCAA"""
    
@tool
def get_live_games_tool(sport: str = "nfl") -> str:
    """Get live ESPN game scores"""
    
@tool
def get_game_watchlist_tool(user_id: str) -> str:
    """Get user's watched games with Telegram alerts"""
    
@tool
def get_ai_betting_predictions_tool(game_id: str = None, sport: str = "nfl") -> str:
    """Get AI predictions for games"""
    
@tool
def get_betting_opportunities_tool(min_ev: float = 5.0, sport: str = "nfl") -> str:
    """Find high expected value betting opportunities"""
```

### 5.2 Trading Tools (Priority 1)

```python
@tool
def get_options_chain_tool(ticker: str, expiration: str = None) -> str:
    """Get options chain for a stock"""
    
@tool
def get_stock_data_tool(ticker: str) -> str:
    """Get comprehensive stock data (price, volume, fundamentals)"""
    
@tool
def get_trading_opportunities_tool(strategy: str = "CSP", min_score: float = 60.0) -> str:
    """Find trading opportunities (CSP, CC, etc.)"""
    
@tool
def get_positions_tool() -> str:
    """Get current stock and options positions"""
    
@tool
def get_trade_history_tool(symbol: str = None, limit: int = 10) -> str:
    """Get trade history"""
```

### 5.3 Xtrades Tools (Priority 2)

```python
@tool
def get_xtrades_profiles_tool(active_only: bool = True) -> str:
    """Get monitored Xtrades profiles"""
    
@tool
def get_xtrades_trades_tool(profile: str = None, limit: int = 10) -> str:
    """Get recent trades from Xtrades profiles"""
    
@tool
def get_xtrades_consensus_tool(ticker: str) -> str:
    """Get AI consensus on trades for a ticker"""
```

### 5.4 Task Management Tools (Priority 2)

```python
@tool
def get_tasks_tool(status: str = None, priority: str = None, limit: int = 10) -> str:
    """Get development tasks"""
    
@tool
def get_qa_tasks_tool(status: str = None) -> str:
    """Get QA tasks"""
    
@tool
def update_task_tool(task_id: int, status: str = None, notes: str = None) -> str:
    """Update a task"""
```

### 5.5 Earnings Tools (Priority 3)

```python
@tool
def get_earnings_calendar_tool(days_ahead: int = 7, symbol: str = None) -> str:
    """Get upcoming earnings calendar"""
    
@tool
def get_earnings_history_tool(symbol: str, limit: int = 4) -> str:
    """Get past earnings data"""
```

---

## 6. Implementation Plan

### Phase 1: Critical Sports Betting Tools (Week 1)
- [ ] Add `get_kalshi_markets_tool`
- [ ] Add `get_live_games_tool`
- [ ] Add `get_game_watchlist_tool`
- [ ] Add `get_ai_betting_predictions_tool`
- [ ] Add `get_betting_opportunities_tool`

### Phase 2: Trading Tools (Week 1)
- [ ] Add `get_options_chain_tool`
- [ ] Add `get_stock_data_tool` (enhanced)
- [ ] Add `get_trading_opportunities_tool`
- [ ] Add `get_positions_tool`
- [ ] Add `get_trade_history_tool`

### Phase 3: Xtrades & Tasks (Week 2)
- [ ] Add Xtrades tools (3 tools)
- [ ] Add task management tools (3 tools)

### Phase 4: Earnings & Analytics (Week 2)
- [ ] Add earnings tools (2 tools)
- [ ] Add analytics tools (if needed)

---

## 7. Database Query Documentation

### 7.1 Common Query Patterns

**Get Kalshi Markets:**
```sql
SELECT ticker, title, yes_price, no_price, volume, status
FROM kalshi_markets
WHERE market_type = 'nfl' AND status = 'active'
ORDER BY volume DESC
LIMIT 10;
```

**Get Live Games:**
```sql
SELECT game_id, away_team, home_team, away_score, home_score, status
FROM nfl_games
WHERE is_live = true;
```

**Get Watched Games:**
```sql
SELECT g.*, gw.selected_team
FROM game_watchlist gw
JOIN nfl_games g ON gw.game_id = g.game_id
WHERE gw.user_id = 'user_id';
```

**Get Trading Opportunities:**
```sql
SELECT symbol, strategy, premium, confidence_score, expected_return
FROM opportunities
WHERE executed = false AND confidence_score >= 70
ORDER BY expected_return DESC;
```

---

## 8. Testing Plan

### 8.1 Unit Tests
- Test each new tool independently
- Verify database connections
- Test error handling

### 8.2 Integration Tests
- Test tool chaining (e.g., get games → get predictions)
- Test with real data
- Verify response formats

### 8.3 User Acceptance Tests
- Test common user queries
- Verify AVA can answer all question types
- Check response quality

---

## 9. Documentation Updates Needed

1. **Tool Reference Guide** - Document all 25+ tools
2. **Database Schema Guide** - Complete table reference
3. **Query Examples** - Common query patterns
4. **Data Source Guide** - How to access each API
5. **AVA Capabilities** - What AVA can and cannot do

---

## 10. Next Steps

1. ✅ **Review Complete** - This document
2. ⏳ **Implement Phase 1** - Sports betting tools
3. ⏳ **Implement Phase 2** - Trading tools
4. ⏳ **Update Documentation** - Tool reference
5. ⏳ **Test & Validate** - End-to-end testing

---

**Status:** Ready for implementation  
**Priority:** HIGH - AVA is currently very limited  
**Estimated Time:** 2 weeks for full implementation

