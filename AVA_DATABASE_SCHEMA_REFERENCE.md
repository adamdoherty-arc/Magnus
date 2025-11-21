# AVA Database Schema Reference

**Database:** `magnus` (PostgreSQL)  
**Purpose:** Complete reference for AVA to understand all available data

---

## Complete Table Inventory

### 1. Trading & Options Tables

#### `stock_holdings`
**Purpose:** User's current stock positions

**Schema:**
```sql
CREATE TABLE stock_holdings (
  id SERIAL PRIMARY KEY,
  symbol VARCHAR(10) NOT NULL,
  shares INTEGER NOT NULL,
  cost_basis DECIMAL(10, 2),
  purchase_date DATE,
  account_type VARCHAR(50),
  notes TEXT,
  active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW()
);
```

**AVA Access:** ✅ `get_positions_tool`

**Query Example:**
```sql
SELECT symbol, shares, cost_basis 
FROM stock_holdings 
WHERE active = true;
```

---

#### `watchlist`
**Purpose:** Stocks to buy (Cash-Secured Puts)

**Schema:**
```sql
CREATE TABLE watchlist (
  id SERIAL PRIMARY KEY,
  symbol VARCHAR(10) NOT NULL UNIQUE,
  target_price DECIMAL(10, 2),
  max_shares INTEGER DEFAULT 100,
  priority INTEGER DEFAULT 5,
  notes TEXT,
  active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW()
);
```

**AVA Access:** ✅ `analyze_watchlist_tool`

---

#### `opportunities`
**Purpose:** Discovered trading opportunities

**Schema:**
```sql
CREATE TABLE opportunities (
  id SERIAL PRIMARY KEY,
  symbol VARCHAR(10) NOT NULL,
  strategy VARCHAR(20) NOT NULL,
  strike DECIMAL(10, 2),
  premium DECIMAL(10, 2),
  expiration DATE,
  confidence_score INTEGER,
  risk_score INTEGER,
  expected_return DECIMAL(10, 2),
  analysis_data JSONB,
  created_at TIMESTAMP DEFAULT NOW(),
  executed BOOLEAN DEFAULT false
);
```

**AVA Access:** ✅ `get_trading_opportunities_tool`

---

#### `trade_history`
**Purpose:** Historical trades for learning

**Schema:**
```sql
CREATE TABLE trade_history (
  id SERIAL PRIMARY KEY,
  symbol VARCHAR(10) NOT NULL,
  strategy VARCHAR(20) NOT NULL,
  strike DECIMAL(10, 2),
  premium DECIMAL(10, 2),
  quantity INTEGER DEFAULT 1,
  expiration DATE,
  entry_date DATE,
  exit_date DATE,
  profit_loss DECIMAL(10, 2),
  exit_reason VARCHAR(50),
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);
```

**AVA Access:** ✅ `get_trade_history_tool`

---

### 2. Sports Betting Tables

#### `kalshi_markets`
**Purpose:** Kalshi prediction markets

**Schema:**
```sql
CREATE TABLE kalshi_markets (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(100) UNIQUE NOT NULL,
    title TEXT NOT NULL,
    subtitle TEXT,
    market_type VARCHAR(50) NOT NULL, -- 'nfl', 'college'
    series_ticker VARCHAR(100),
    home_team VARCHAR(100),
    away_team VARCHAR(100),
    game_date TIMESTAMP WITH TIME ZONE,
    yes_price DECIMAL(5,4), -- 0.0000 to 1.0000
    no_price DECIMAL(5,4),
    volume DECIMAL(15,2) DEFAULT 0,
    open_interest INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'open',
    close_time TIMESTAMP WITH TIME ZONE,
    expiration_time TIMESTAMP WITH TIME ZONE,
    result VARCHAR(10), -- 'yes', 'no', NULL
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    synced_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    raw_data JSONB
);
```

**AVA Access:** ✅ `get_kalshi_markets_tool`

**Query Examples:**
```sql
-- Get active NFL markets
SELECT ticker, title, yes_price, no_price, volume
FROM kalshi_markets
WHERE market_type = 'nfl' AND status = 'active'
ORDER BY volume DESC;

-- Get markets for specific game
SELECT * FROM kalshi_markets
WHERE home_team ILIKE '%Chiefs%' 
  AND away_team ILIKE '%Bills%'
  AND status = 'active';
```

---

#### `kalshi_predictions`
**Purpose:** AI predictions for markets

**Schema:**
```sql
CREATE TABLE kalshi_predictions (
    id SERIAL PRIMARY KEY,
    market_id INTEGER REFERENCES kalshi_markets(id),
    predicted_outcome VARCHAR(10), -- 'yes' or 'no'
    confidence_score DECIMAL(5,2), -- 0-100
    edge_percentage DECIMAL(5,2),
    reasoning TEXT,
    model_used VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

**AVA Access:** ⚠️ Via `query_database_tool`

---

#### `game_watchlist`
**Purpose:** User's watched games with Telegram alerts

**Schema:**
```sql
CREATE TABLE game_watchlist (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100) NOT NULL,
    game_id VARCHAR(100) NOT NULL,
    sport VARCHAR(10) NOT NULL, -- 'NFL' or 'CFB'
    away_team VARCHAR(100),
    home_team VARCHAR(100),
    selected_team VARCHAR(100), -- Team user is rooting for
    added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, game_id)
);
```

**AVA Access:** ✅ `get_game_watchlist_tool`

---

### 3. Task Management Tables

#### `development_tasks`
**Purpose:** Development task tracking

**Schema:**
```sql
CREATE TABLE development_tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    priority VARCHAR(20) DEFAULT 'medium',
    assigned_agent VARCHAR(100),
    task_type VARCHAR(50),
    source VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**AVA Access:** ✅ `get_tasks_tool`

**Query Examples:**
```sql
-- Get pending tasks
SELECT * FROM development_tasks
WHERE status = 'pending'
ORDER BY 
  CASE priority 
    WHEN 'critical' THEN 1
    WHEN 'high' THEN 2
    WHEN 'medium' THEN 3
    WHEN 'low' THEN 4
  END;

-- Get tasks by agent
SELECT * FROM development_tasks
WHERE assigned_agent = 'AVA'
ORDER BY created_at DESC;
```

---

#### `qa_tasks`
**Purpose:** QA verification tasks

**Schema:**
```sql
CREATE TABLE qa_tasks (
    id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES development_tasks(id),
    status VARCHAR(50) DEFAULT 'pending',
    verification_status VARCHAR(50),
    qa_agent VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);
```

**AVA Access:** ⚠️ Via `query_database_tool`

---

### 4. Xtrades Tables

#### `xtrades_profiles`
**Purpose:** Monitored Xtrades.net profiles

**Schema:**
```sql
CREATE TABLE xtrades_profiles (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    display_name VARCHAR(255),
    active BOOLEAN DEFAULT TRUE,
    added_date TIMESTAMP DEFAULT NOW(),
    last_sync TIMESTAMP,
    last_sync_status VARCHAR(50),
    total_trades_scraped INTEGER DEFAULT 0,
    notes TEXT
);
```

**AVA Access:** ✅ `get_xtrades_profiles_tool`

---

#### `xtrades_trades`
**Purpose:** Scraped trades from Xtrades profiles

**Schema:**
```sql
CREATE TABLE xtrades_trades (
    id SERIAL PRIMARY KEY,
    profile_id INTEGER REFERENCES xtrades_profiles(id),
    ticker VARCHAR(10),
    strategy VARCHAR(50), -- 'CALL', 'PUT', etc.
    strike DECIMAL(10, 2),
    expiration DATE,
    entry_price DECIMAL(10, 2),
    quantity INTEGER,
    scraped_at TIMESTAMP DEFAULT NOW(),
    trade_url TEXT
);
```

**AVA Access:** ✅ `get_xtrades_trades_tool`

**Query Examples:**
```sql
-- Get recent trades from all profiles
SELECT t.*, p.username, p.display_name
FROM xtrades_trades t
JOIN xtrades_profiles p ON t.profile_id = p.id
WHERE p.active = true
ORDER BY t.scraped_at DESC
LIMIT 20;

-- Get consensus on a ticker
SELECT ticker, strategy, COUNT(*) as trade_count,
       AVG(strike) as avg_strike
FROM xtrades_trades
WHERE ticker = 'NVDA'
  AND scraped_at > NOW() - INTERVAL '7 days'
GROUP BY ticker, strategy;
```

---

### 5. Options & Market Data Tables

#### `options_chains`
**Purpose:** Cached options chain data

**Schema:**
```sql
CREATE TABLE options_chains (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    expiration DATE NOT NULL,
    strike DECIMAL(10, 2) NOT NULL,
    option_type VARCHAR(5), -- 'CALL' or 'PUT'
    bid DECIMAL(10, 2),
    ask DECIMAL(10, 2),
    last_price DECIMAL(10, 2),
    volume INTEGER,
    open_interest INTEGER,
    implied_volatility DECIMAL(5, 4),
    delta DECIMAL(5, 4),
    gamma DECIMAL(8, 6),
    theta DECIMAL(8, 4),
    vega DECIMAL(8, 4),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**AVA Access:** ⚠️ Via `query_database_tool`

---

#### `stock_data`
**Purpose:** Cached stock market data

**Schema:**
```sql
CREATE TABLE stock_data (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    current_price DECIMAL(10, 2),
    volume BIGINT,
    market_cap BIGINT,
    pe_ratio DECIMAL(8, 2),
    beta DECIMAL(6, 3),
    dividend_yield DECIMAL(5, 4),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**AVA Access:** ⚠️ Via `query_database_tool`

---

### 6. Earnings Tables

#### `earnings_calendar`
**Purpose:** Upcoming earnings dates

**Schema:**
```sql
CREATE TABLE earnings_calendar (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    earnings_date DATE NOT NULL,
    estimate DECIMAL(10, 2),
    fiscal_quarter VARCHAR(10),
    fiscal_year INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**AVA Access:** ⚠️ Via `query_database_tool` (no dedicated tool yet)

---

#### `earnings_history`
**Purpose:** Past earnings data

**Schema:**
```sql
CREATE TABLE earnings_history (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    earnings_date DATE NOT NULL,
    actual DECIMAL(10, 2),
    estimate DECIMAL(10, 2),
    surprise_percent DECIMAL(5, 2),
    created_at TIMESTAMP DEFAULT NOW()
);
```

**AVA Access:** ⚠️ Via `query_database_tool`

---

### 7. Analytics Tables

#### `supply_demand_zones`
**Purpose:** Technical analysis zones

**Schema:**
```sql
CREATE TABLE supply_demand_zones (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    zone_type VARCHAR(20), -- 'supply' or 'demand'
    price_level DECIMAL(10, 2),
    strength DECIMAL(5, 2),
    created_at TIMESTAMP DEFAULT NOW()
);
```

**AVA Access:** ⚠️ Via `query_database_tool`

---

#### `position_recommendations`
**Purpose:** AI position recommendations

**Schema:**
```sql
CREATE TABLE position_recommendations (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    strategy VARCHAR(50),
    confidence DECIMAL(5, 2),
    reasoning TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**AVA Access:** ⚠️ Via `query_database_tool`

---

## Data Source Mapping

### External APIs → Database Tables

| API/Service | Data Stored In | AVA Access |
|-------------|----------------|------------|
| **ESPN API** | Live data (no table) | ✅ `get_live_games_tool` |
| **Kalshi API** | `kalshi_markets` | ✅ `get_kalshi_markets_tool` |
| **Robinhood API** | Live data (no table) | ✅ `get_portfolio_status_tool`, `get_stock_price_tool` |
| **Yahoo Finance** | `stock_data`, `options_chains` | ⚠️ Via `query_database_tool` |
| **Xtrades.net** | `xtrades_profiles`, `xtrades_trades` | ✅ `get_xtrades_profiles_tool`, `get_xtrades_trades_tool` |

---

## Common Query Patterns for AVA

### Get All Tables
```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public'
ORDER BY table_name;
```

### Get Table Columns
```sql
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'table_name'
ORDER BY ordinal_position;
```

### Get Recent Data
```sql
-- Recent Kalshi markets
SELECT * FROM kalshi_markets
WHERE created_at > NOW() - INTERVAL '24 hours'
ORDER BY created_at DESC;

-- Recent trades
SELECT * FROM trade_history
ORDER BY entry_date DESC
LIMIT 10;
```

### Join Queries
```sql
-- Games with Kalshi odds
SELECT g.*, k.ticker, k.yes_price, k.no_price
FROM nfl_games g
LEFT JOIN kalshi_markets k ON g.game_id = k.game_id
WHERE g.is_live = true;
```

---

## AVA Tool Coverage Summary

| Category | Tables | Tools | Coverage |
|----------|--------|-------|----------|
| **Core Trading** | 4 | 3 | ✅ 75% |
| **Sports Betting** | 3 | 4 | ✅ 100% |
| **Task Management** | 2 | 2 | ✅ 100% |
| **Xtrades** | 2 | 2 | ✅ 100% |
| **Options Data** | 2 | 0 | ❌ 0% |
| **Earnings** | 2 | 0 | ❌ 0% |
| **Analytics** | 2 | 0 | ❌ 0% |

**Overall Coverage:** ~60% of tables have dedicated tools

**Workaround:** Use `query_database_tool` for all tables

---

**Last Updated:** November 15, 2025  
**Total Tables Documented:** 20+  
**Tools Available:** 16

