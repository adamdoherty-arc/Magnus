# AVA Tool Reference Guide

**Date:** November 15, 2025  
**Total Tools:** 16  
**Status:** ✅ **ALL TOOLS ACTIVE**

---

## Tool Categories

### 1. Core Tools (6)
- `query_database_tool` - Generic SQL queries
- `analyze_watchlist_tool` - Stock watchlist analysis
- `get_portfolio_status_tool` - Robinhood portfolio
- `create_task_tool` - Create tasks
- `get_stock_price_tool` - Stock prices
- `search_magnus_knowledge_tool` - RAG knowledge base

### 2. Sports Betting Tools (4) ⭐ NEW
- `get_kalshi_markets_tool` - Kalshi prediction markets
- `get_live_games_tool` - ESPN live scores
- `get_game_watchlist_tool` - Watched games
- `get_betting_opportunities_tool` - High-EV betting opportunities

### 3. Trading Tools (3) ⭐ NEW
- `get_positions_tool` - Current positions
- `get_trading_opportunities_tool` - CSP/CC opportunities
- `get_trade_history_tool` - Trade history

### 4. Task Management Tools (1) ⭐ NEW
- `get_tasks_tool` - Query tasks (read-only)

### 5. Xtrades Tools (2) ⭐ NEW
- `get_xtrades_profiles_tool` - Monitored profiles
- `get_xtrades_trades_tool` - Recent trades

---

## Detailed Tool Documentation

### Sports Betting Tools

#### `get_kalshi_markets_tool`
**Purpose:** Get Kalshi prediction markets for NFL or NCAA football

**Parameters:**
- `sport` (str, default="nfl"): 'nfl' or 'cfb'
- `status` (str, default="active"): 'active', 'open', 'closed', or 'all'
- `limit` (int, default=10): Maximum markets to return

**Returns:** JSON with ticker, title, prices (cents), volume, status, close_time

**Example Usage:**
```
"What are the top 10 NFL markets on Kalshi?"
"Show me active college football markets"
```

**Database Table:** `kalshi_markets`

---

#### `get_live_games_tool`
**Purpose:** Get live ESPN game scores

**Parameters:**
- `sport` (str, default="nfl"): 'nfl' or 'cfb'

**Returns:** JSON with game_id, teams, scores, status, is_live, clock, period

**Example Usage:**
```
"What games are live right now?"
"Show me NCAA football scores"
```

**Data Source:** ESPN API (`src/espn_live_data.py`, `src/espn_ncaa_live_data.py`)

---

#### `get_game_watchlist_tool`
**Purpose:** Get user's watched games with Telegram alerts

**Parameters:**
- `user_id` (str, default="default_user"): User identifier

**Returns:** JSON with game_id, teams, selected_team, sport, added_at

**Example Usage:**
```
"What games am I watching?"
"Show me my game watchlist"
```

**Database Table:** `game_watchlist`

---

#### `get_betting_opportunities_tool`
**Purpose:** Find high expected value betting opportunities

**Parameters:**
- `min_ev` (float, default=5.0): Minimum EV percentage
- `sport` (str, default="nfl"): 'nfl' or 'cfb'

**Returns:** JSON with game, predicted_winner, win_probability, confidence, expected_value, recommendation, kalshi_odds

**Example Usage:**
```
"What are the best betting opportunities right now?"
"Find me NFL games with EV > 10%"
```

**Data Sources:** ESPN API + Kalshi API + AI Predictions

---

### Trading Tools

#### `get_positions_tool`
**Purpose:** Get current stock positions from database

**Parameters:** None

**Returns:** JSON with symbol, shares, cost_basis, purchase_date, account_type, notes

**Example Usage:**
```
"What are my current positions?"
"Show me my stock holdings"
```

**Database Table:** `stock_holdings`

---

#### `get_trading_opportunities_tool`
**Purpose:** Find trading opportunities (CSP, CC, etc.)

**Parameters:**
- `strategy` (str, default="CSP"): 'CSP' or 'CC'
- `min_score` (float, default=60.0): Minimum profit score (0-100)

**Returns:** JSON with symbol, strategy, strike, premium, expiration, confidence_score, expected_return

**Example Usage:**
```
"What are the best CSP opportunities?"
"Find covered call opportunities with score > 70"
```

**Database Table:** `opportunities`

---

#### `get_trade_history_tool`
**Purpose:** Get trade history

**Parameters:**
- `symbol` (str, optional): Filter by ticker
- `limit` (int, default=10): Maximum trades to return

**Returns:** JSON with symbol, strategy, strike, premium, quantity, expiration, entry_date, exit_date, profit_loss, exit_reason

**Example Usage:**
```
"Show me my trade history"
"What trades did I make on AAPL?"
```

**Database Table:** `trade_history`

---

### Task Management Tools

#### `get_tasks_tool`
**Purpose:** Get development tasks

**Parameters:**
- `status` (str, optional): Filter by status
- `priority` (str, optional): Filter by priority
- `limit` (int, default=10): Maximum tasks to return

**Returns:** JSON with id, title, description, status, priority, assigned_agent, created_at

**Example Usage:**
```
"What tasks are pending?"
"Show me high priority tasks"
```

**Database Table:** `development_tasks`

---

### Xtrades Tools

#### `get_xtrades_profiles_tool`
**Purpose:** Get monitored Xtrades profiles

**Parameters:**
- `active_only` (bool, default=True): Only active profiles

**Returns:** JSON with id, username, display_name, active, added_date, last_sync, total_trades_scraped

**Example Usage:**
```
"What Xtrades profiles am I monitoring?"
"Show me all profiles"
```

**Database Table:** `xtrades_profiles`

---

#### `get_xtrades_trades_tool`
**Purpose:** Get recent trades from Xtrades profiles

**Parameters:**
- `profile` (str, optional): Filter by username
- `limit` (int, default=10): Maximum trades to return

**Returns:** JSON with trade details including ticker, strategy, entry, profile info

**Example Usage:**
```
"What trades did [username] make?"
"Show me recent Xtrades alerts"
```

**Database Table:** `xtrades_trades` (joined with `xtrades_profiles`)

---

## Database Tables Reference

### Core Trading Tables

| Table | Purpose | Key Fields | Tool Access |
|-------|---------|------------|-------------|
| `stock_holdings` | Stock positions | symbol, shares, cost_basis | ✅ `get_positions_tool` |
| `watchlist` | Stock watchlist | symbol, target_price, priority | ✅ `analyze_watchlist_tool` |
| `opportunities` | Trading opportunities | symbol, strategy, premium, confidence | ✅ `get_trading_opportunities_tool` |
| `trade_history` | Historical trades | symbol, strategy, profit_loss | ✅ `get_trade_history_tool` |

### Sports Betting Tables

| Table | Purpose | Key Fields | Tool Access |
|-------|---------|------------|-------------|
| `kalshi_markets` | Prediction markets | ticker, title, yes_price, volume | ✅ `get_kalshi_markets_tool` |
| `kalshi_predictions` | AI predictions | market_id, confidence, edge | ⚠️ Via `query_database_tool` |
| `game_watchlist` | Watched games | game_id, user_id, selected_team | ✅ `get_game_watchlist_tool` |

### Task Management Tables

| Table | Purpose | Key Fields | Tool Access |
|-------|---------|------------|-------------|
| `development_tasks` | Dev tasks | id, title, status, priority | ✅ `get_tasks_tool` |
| `qa_tasks` | QA tasks | task_id, status, verification | ⚠️ Via `query_database_tool` |

### Xtrades Tables

| Table | Purpose | Key Fields | Tool Access |
|-------|---------|------------|-------------|
| `xtrades_profiles` | Monitored profiles | username, display_name, active | ✅ `get_xtrades_profiles_tool` |
| `xtrades_trades` | Scraped trades | profile_id, ticker, strategy | ✅ `get_xtrades_trades_tool` |

---

## Common Query Patterns

### Get All Database Tables
```python
query_database_tool("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public'
    ORDER BY table_name
""")
```

### Get Table Schema
```python
query_database_tool("""
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns
    WHERE table_name = 'kalshi_markets'
    ORDER BY ordinal_position
""")
```

---

## Data Source Access

### ESPN Live Scores
- **Tool:** `get_live_games_tool`
- **Source:** ESPN API (no key required)
- **Tables:** None (live API data)

### Kalshi Markets
- **Tool:** `get_kalshi_markets_tool`
- **Source:** Kalshi API → Database
- **Table:** `kalshi_markets`

### Robinhood Portfolio
- **Tool:** `get_portfolio_status_tool`
- **Source:** Robinhood API (requires credentials)
- **Tables:** None (live API data)

### Stock Prices
- **Tool:** `get_stock_price_tool`
- **Source:** Robinhood API
- **Alternative:** Use `query_database_tool` with `stock_data` table

---

## Usage Examples

### Sports Betting Queries
```
"What are the best betting opportunities for NFL games?"
→ Uses: get_betting_opportunities_tool(min_ev=5.0, sport="nfl")

"What games am I watching?"
→ Uses: get_game_watchlist_tool(user_id="default_user")

"Show me live NCAA scores"
→ Uses: get_live_games_tool(sport="cfb")
```

### Trading Queries
```
"What are my current positions?"
→ Uses: get_positions_tool()

"Find me CSP opportunities with score > 70"
→ Uses: get_trading_opportunities_tool(strategy="CSP", min_score=70.0)

"Show me my trade history for AAPL"
→ Uses: get_trade_history_tool(symbol="AAPL")
```

### Task Queries
```
"What tasks are pending?"
→ Uses: get_tasks_tool(status="pending")

"Show me high priority tasks"
→ Uses: get_tasks_tool(priority="high")
```

### Xtrades Queries
```
"What Xtrades profiles am I monitoring?"
→ Uses: get_xtrades_profiles_tool(active_only=True)

"What trades did [username] make?"
→ Uses: get_xtrades_trades_tool(profile="username")
```

---

## Tool Limitations & Notes

### Current Limitations
1. **No write operations** - All tools are read-only (except `create_task_tool`)
2. **No options chain tool** - Options data not directly accessible
3. **No earnings calendar tool** - Earnings data not directly accessible
4. **Limited stock data** - Only Robinhood prices, not comprehensive data

### Workarounds
- Use `query_database_tool` for custom queries
- Use `search_magnus_knowledge_tool` for project documentation
- Combine multiple tools for complex queries

---

## Future Enhancements

### Recommended Additional Tools
1. `get_options_chain_tool` - Options chains with Greeks
2. `get_earnings_calendar_tool` - Upcoming earnings
3. `get_stock_data_tool` - Comprehensive stock data (enhanced)
4. `get_ai_predictions_tool` - AI betting predictions (standalone)
5. `update_task_tool` - Update task status
6. `get_qa_tasks_tool` - QA-specific tasks

---

**Last Updated:** November 15, 2025  
**Total Tools:** 16 (6 core + 10 new)  
**Coverage:** ~70% of project data sources

