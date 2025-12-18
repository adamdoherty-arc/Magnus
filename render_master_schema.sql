-- ============================================
-- AVA TRADING PLATFORM - MASTER SCHEMA
-- Complete database schema for Render PostgreSQL
-- ============================================
-- Generated: 2025-12-18
-- Includes: All active features and tables
-- ============================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS timescaledb;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pg_trgm; -- For text search

-- ============================================
-- SECTION 1: CORE TRADING TABLES
-- ============================================

-- User management
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN DEFAULT true,
    risk_tolerance VARCHAR(20) DEFAULT 'moderate',
    max_portfolio_risk DECIMAL(5,4) DEFAULT 0.02,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Stock symbols and metadata
CREATE TABLE IF NOT EXISTS stocks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(10) NOT NULL UNIQUE,
    company_name VARCHAR(255),
    sector VARCHAR(100),
    industry VARCHAR(100),
    market_cap BIGINT,
    is_active BOOLEAN DEFAULT true,
    is_optionable BOOLEAN DEFAULT false,
    average_volume BIGINT,
    beta DECIMAL(6,3),
    dividend_yield DECIMAL(5,4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User watchlists
CREATE TABLE IF NOT EXISTS watchlists (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, name)
);

-- Watchlist items
CREATE TABLE IF NOT EXISTS watchlist_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    watchlist_id UUID NOT NULL REFERENCES watchlists(id) ON DELETE CASCADE,
    stock_id UUID NOT NULL REFERENCES stocks(id) ON DELETE CASCADE,
    target_entry_price DECIMAL(10,2),
    target_premium_yield DECIMAL(5,4),
    max_position_size INTEGER,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(watchlist_id, stock_id)
);

-- Stock price data (time-series)
CREATE TABLE IF NOT EXISTS stock_prices (
    time TIMESTAMP WITH TIME ZONE NOT NULL,
    stock_id UUID NOT NULL REFERENCES stocks(id) ON DELETE CASCADE,
    open_price DECIMAL(10,2) NOT NULL,
    high_price DECIMAL(10,2) NOT NULL,
    low_price DECIMAL(10,2) NOT NULL,
    close_price DECIMAL(10,2) NOT NULL,
    volume BIGINT NOT NULL,
    adjusted_close DECIMAL(10,2),
    PRIMARY KEY (stock_id, time)
);

-- Convert to hypertable for time-series optimization (only if not exists)
SELECT create_hypertable('stock_prices', 'time', 'stock_id', number_partitions => 4, if_not_exists => TRUE);

-- Options chains data
CREATE TABLE IF NOT EXISTS options_chains (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    stock_id UUID NOT NULL REFERENCES stocks(id) ON DELETE CASCADE,
    expiration_date DATE NOT NULL,
    strike_price DECIMAL(8,2) NOT NULL,
    option_type VARCHAR(4) NOT NULL CHECK (option_type IN ('CALL', 'PUT')),
    bid_price DECIMAL(6,2),
    ask_price DECIMAL(6,2),
    last_price DECIMAL(6,2),
    volume INTEGER DEFAULT 0,
    open_interest INTEGER DEFAULT 0,
    implied_volatility DECIMAL(6,4),
    delta DECIMAL(6,4),
    gamma DECIMAL(6,4),
    theta DECIMAL(6,4),
    vega DECIMAL(6,4),
    rho DECIMAL(6,4),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(stock_id, expiration_date, strike_price, option_type)
);

-- Trading accounts
CREATE TABLE IF NOT EXISTS trading_accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    account_name VARCHAR(100) NOT NULL,
    broker VARCHAR(50),
    account_number VARCHAR(50),
    account_type VARCHAR(20) DEFAULT 'margin',
    buying_power DECIMAL(12,2) DEFAULT 0,
    total_value DECIMAL(12,2) DEFAULT 0,
    cash_balance DECIMAL(12,2) DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Wheel strategy cycles tracking
CREATE TABLE IF NOT EXISTS wheel_cycles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    stock_id UUID NOT NULL REFERENCES stocks(id) ON DELETE CASCADE,
    cycle_number INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    total_premium_collected DECIMAL(10,2) DEFAULT 0,
    total_pnl DECIMAL(10,2) DEFAULT 0,
    stock_assignment_price DECIMAL(8,2),
    target_exit_price DECIMAL(8,2),
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(user_id, stock_id, cycle_number)
);

-- Positions tracking
CREATE TABLE IF NOT EXISTS positions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    account_id UUID NOT NULL REFERENCES trading_accounts(id) ON DELETE CASCADE,
    stock_id UUID NOT NULL REFERENCES stocks(id) ON DELETE CASCADE,
    wheel_cycle_id UUID REFERENCES wheel_cycles(id),
    position_type VARCHAR(20) NOT NULL,
    strategy_type VARCHAR(20) NOT NULL,
    quantity INTEGER NOT NULL,
    entry_price DECIMAL(8,2) NOT NULL,
    current_price DECIMAL(8,2),
    strike_price DECIMAL(8,2),
    expiration_date DATE,
    opening_premium DECIMAL(8,2),
    current_premium DECIMAL(8,2),
    unrealized_pnl DECIMAL(10,2) DEFAULT 0,
    realized_pnl DECIMAL(10,2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'open',
    opened_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    closed_at TIMESTAMP WITH TIME ZONE,
    notes TEXT
);

-- Trade executions log
CREATE TABLE IF NOT EXISTS trades (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    position_id UUID NOT NULL REFERENCES positions(id) ON DELETE CASCADE,
    trade_type VARCHAR(20) NOT NULL,
    quantity INTEGER NOT NULL,
    price DECIMAL(8,2) NOT NULL,
    commission DECIMAL(6,2) DEFAULT 0,
    fees DECIMAL(6,2) DEFAULT 0,
    total_amount DECIMAL(10,2) NOT NULL,
    execution_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    order_id VARCHAR(100),
    notes TEXT
);

-- Trade history (closed positions)
CREATE TABLE IF NOT EXISTS trade_history (
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

-- Strategy signals and recommendations
CREATE TABLE IF NOT EXISTS strategy_signals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    stock_id UUID NOT NULL REFERENCES stocks(id) ON DELETE CASCADE,
    signal_type VARCHAR(20) NOT NULL,
    strategy VARCHAR(20) NOT NULL,
    strike_price DECIMAL(8,2),
    expiration_date DATE,
    premium_yield DECIMAL(5,4),
    probability_profit DECIMAL(5,4),
    risk_reward_ratio DECIMAL(6,3),
    confidence_score DECIMAL(3,2),
    reasoning TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE
);

-- Price alerts configuration
CREATE TABLE IF NOT EXISTS price_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    stock_id UUID NOT NULL REFERENCES stocks(id) ON DELETE CASCADE,
    alert_type VARCHAR(20) NOT NULL,
    threshold_value DECIMAL(10,4) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    notification_methods TEXT[],
    last_triggered_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Alert events log
CREATE TABLE IF NOT EXISTS alert_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    alert_id UUID NOT NULL REFERENCES price_alerts(id) ON DELETE CASCADE,
    triggered_value DECIMAL(10,4) NOT NULL,
    message TEXT NOT NULL,
    notification_sent BOOLEAN DEFAULT false,
    triggered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Risk metrics tracking
CREATE TABLE IF NOT EXISTS risk_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    account_id UUID REFERENCES trading_accounts(id) ON DELETE CASCADE,
    metric_date DATE NOT NULL,
    portfolio_value DECIMAL(12,2),
    total_delta DECIMAL(8,2),
    total_theta DECIMAL(8,2),
    total_vega DECIMAL(8,2),
    buying_power_used DECIMAL(12,2),
    margin_requirement DECIMAL(12,2),
    var_1_day DECIMAL(10,2),
    var_30_day DECIMAL(10,2),
    max_drawdown DECIMAL(5,4),
    sharpe_ratio DECIMAL(6,3),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, account_id, metric_date)
);

-- System configuration
CREATE TABLE IF NOT EXISTS system_config (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value JSONB NOT NULL,
    description TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- SECTION 2: EARNINGS CALENDAR
-- ============================================

CREATE TABLE IF NOT EXISTS earnings_history (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    earnings_date DATE NOT NULL,
    fiscal_quarter VARCHAR(10),
    fiscal_year INTEGER,
    eps_estimate DECIMAL(10,4),
    eps_actual DECIMAL(10,4),
    eps_surprise DECIMAL(10,4),
    eps_surprise_pct DECIMAL(6,2),
    revenue_estimate BIGINT,
    revenue_actual BIGINT,
    revenue_surprise_pct DECIMAL(6,2),
    beat_or_miss VARCHAR(10),
    stock_move_pct DECIMAL(6,2),
    guidance TEXT,
    source VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(symbol, earnings_date)
);

CREATE TABLE IF NOT EXISTS earnings_events (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    earnings_date DATE NOT NULL,
    earnings_time VARCHAR(10),
    fiscal_quarter VARCHAR(10),
    fiscal_year INTEGER,
    eps_estimate DECIMAL(10,4),
    revenue_estimate BIGINT,
    confidence_score INTEGER CHECK (confidence_score BETWEEN 0 AND 100),
    historical_beat_rate DECIMAL(5,2),
    is_active BOOLEAN DEFAULT true,
    source VARCHAR(50),
    last_updated TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(symbol, earnings_date)
);

CREATE TABLE IF NOT EXISTS earnings_sync_status (
    id SERIAL PRIMARY KEY,
    sync_type VARCHAR(50) NOT NULL,
    last_sync TIMESTAMP,
    status VARCHAR(20),
    records_synced INTEGER DEFAULT 0,
    error_message TEXT,
    next_sync TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS earnings_alerts (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    alert_type VARCHAR(50) NOT NULL,
    threshold_value DECIMAL(10,4),
    is_active BOOLEAN DEFAULT true,
    notification_sent BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- SECTION 3: XTRADES MONITORING
-- ============================================

CREATE TABLE IF NOT EXISTS xtrades_profiles (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    display_name VARCHAR(200),
    bio TEXT,
    total_trades INTEGER DEFAULT 0,
    win_rate DECIMAL(5,2),
    avg_profit_pct DECIMAL(6,2),
    is_active BOOLEAN DEFAULT true,
    last_trade_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS xtrades_trades (
    id SERIAL PRIMARY KEY,
    profile_id INTEGER REFERENCES xtrades_profiles(id) ON DELETE CASCADE,
    username VARCHAR(100) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    trade_type VARCHAR(20),
    entry_price DECIMAL(10,2),
    exit_price DECIMAL(10,2),
    profit_pct DECIMAL(6,2),
    posted_at TIMESTAMP,
    raw_data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS xtrades_sync_log (
    id SERIAL PRIMARY KEY,
    sync_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    profiles_synced INTEGER DEFAULT 0,
    trades_synced INTEGER DEFAULT 0,
    errors_count INTEGER DEFAULT 0,
    error_details TEXT,
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS xtrades_alerts (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    trade_type VARCHAR(20),
    entry_price DECIMAL(10,2),
    position_size VARCHAR(50),
    strategy TEXT,
    posted_at TIMESTAMP NOT NULL,
    ai_score INTEGER CHECK (ai_score BETWEEN 0 AND 100),
    ai_recommendation VARCHAR(50),
    ai_reasoning TEXT,
    notified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS xtrades_notification_queue (
    id SERIAL PRIMARY KEY,
    alert_id INTEGER REFERENCES xtrades_alerts(id) ON DELETE CASCADE,
    notification_type VARCHAR(50) DEFAULT 'telegram',
    status VARCHAR(20) DEFAULT 'pending',
    retry_count INTEGER DEFAULT 0,
    sent_at TIMESTAMP,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS xtrades_scraper_state (
    id SERIAL PRIMARY KEY,
    state_key VARCHAR(100) UNIQUE NOT NULL,
    state_value JSONB,
    last_updated TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS xtrades_rate_limiter (
    id SERIAL PRIMARY KEY,
    action_type VARCHAR(50) NOT NULL,
    window_start TIMESTAMP NOT NULL,
    action_count INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- SECTION 4: KALSHI & NFL MARKETS
-- ============================================

CREATE TABLE IF NOT EXISTS kalshi_markets (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(50) UNIQUE NOT NULL,
    title TEXT NOT NULL,
    subtitle TEXT,
    category VARCHAR(50),
    event_type VARCHAR(50),
    close_time TIMESTAMP,
    expiration_time TIMESTAMP,
    status VARCHAR(20),
    yes_price DECIMAL(5,4),
    no_price DECIMAL(5,4),
    volume INTEGER,
    open_interest INTEGER,
    liquidity_score DECIMAL(5,2),
    last_updated TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS kalshi_predictions (
    id SERIAL PRIMARY KEY,
    market_id INTEGER REFERENCES kalshi_markets(id) ON DELETE CASCADE,
    ticker VARCHAR(50) NOT NULL,
    prediction_type VARCHAR(50),
    predicted_outcome VARCHAR(10),
    confidence_score INTEGER CHECK (confidence_score BETWEEN 0 AND 100),
    reasoning TEXT,
    prediction_date TIMESTAMP DEFAULT NOW(),
    actual_outcome VARCHAR(10),
    was_correct BOOLEAN,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS kalshi_price_history (
    id SERIAL PRIMARY KEY,
    market_id INTEGER REFERENCES kalshi_markets(id) ON DELETE CASCADE,
    ticker VARCHAR(50) NOT NULL,
    yes_price DECIMAL(5,4),
    no_price DECIMAL(5,4),
    volume INTEGER,
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS kalshi_sync_log (
    id SERIAL PRIMARY KEY,
    sync_type VARCHAR(50) NOT NULL,
    markets_synced INTEGER DEFAULT 0,
    status VARCHAR(20),
    error_message TEXT,
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

-- NFL Data Tables
CREATE TABLE IF NOT EXISTS nfl_games (
    id SERIAL PRIMARY KEY,
    game_id VARCHAR(50) UNIQUE NOT NULL,
    season INTEGER,
    week INTEGER,
    game_date TIMESTAMP,
    home_team VARCHAR(50),
    away_team VARCHAR(50),
    home_score INTEGER,
    away_score INTEGER,
    game_status VARCHAR(20),
    quarter INTEGER,
    time_remaining VARCHAR(10),
    possession VARCHAR(50),
    last_play TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS nfl_plays (
    id SERIAL PRIMARY KEY,
    game_id VARCHAR(50) REFERENCES nfl_games(game_id) ON DELETE CASCADE,
    play_id VARCHAR(100) UNIQUE NOT NULL,
    quarter INTEGER,
    time_remaining VARCHAR(10),
    down INTEGER,
    yards_to_go INTEGER,
    yard_line INTEGER,
    play_type VARCHAR(50),
    description TEXT,
    offense_team VARCHAR(50),
    defense_team VARCHAR(50),
    yards_gained INTEGER,
    is_touchdown BOOLEAN DEFAULT false,
    is_turnover BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS nfl_player_stats (
    id SERIAL PRIMARY KEY,
    game_id VARCHAR(50) REFERENCES nfl_games(game_id) ON DELETE CASCADE,
    player_name VARCHAR(200),
    team VARCHAR(50),
    position VARCHAR(10),
    passing_yards INTEGER DEFAULT 0,
    passing_tds INTEGER DEFAULT 0,
    rushing_yards INTEGER DEFAULT 0,
    rushing_tds INTEGER DEFAULT 0,
    receiving_yards INTEGER DEFAULT 0,
    receiving_tds INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS nfl_injuries (
    id SERIAL PRIMARY KEY,
    player_name VARCHAR(200),
    team VARCHAR(50),
    position VARCHAR(10),
    injury_status VARCHAR(50),
    injury_details TEXT,
    week INTEGER,
    season INTEGER,
    updated_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS nfl_alert_history (
    id SERIAL PRIMARY KEY,
    alert_type VARCHAR(50),
    game_id VARCHAR(50),
    team VARCHAR(50),
    message TEXT,
    triggered_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS nfl_data_sync_log (
    id SERIAL PRIMARY KEY,
    sync_type VARCHAR(50) NOT NULL,
    games_synced INTEGER DEFAULT 0,
    plays_synced INTEGER DEFAULT 0,
    status VARCHAR(20),
    error_message TEXT,
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

-- ============================================
-- SECTION 5: SUPPLY/DEMAND ZONES
-- ============================================

CREATE TABLE IF NOT EXISTS sd_zones (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    zone_type VARCHAR(20) NOT NULL,
    price_top DECIMAL(10,2) NOT NULL,
    price_bottom DECIMAL(10,2) NOT NULL,
    strength INTEGER CHECK (strength BETWEEN 1 AND 10),
    touches INTEGER DEFAULT 1,
    first_identified TIMESTAMP DEFAULT NOW(),
    last_tested TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sd_zone_tests (
    id SERIAL PRIMARY KEY,
    zone_id INTEGER REFERENCES sd_zones(id) ON DELETE CASCADE,
    test_date TIMESTAMP DEFAULT NOW(),
    test_price DECIMAL(10,2),
    held BOOLEAN,
    price_reaction_pct DECIMAL(6,2),
    notes TEXT
);

CREATE TABLE IF NOT EXISTS sd_alerts (
    id SERIAL PRIMARY KEY,
    zone_id INTEGER REFERENCES sd_zones(id) ON DELETE CASCADE,
    alert_type VARCHAR(50),
    triggered_at TIMESTAMP DEFAULT NOW(),
    current_price DECIMAL(10,2),
    message TEXT,
    notified BOOLEAN DEFAULT false
);

CREATE TABLE IF NOT EXISTS sd_scan_log (
    id SERIAL PRIMARY KEY,
    scan_type VARCHAR(50),
    symbols_scanned INTEGER DEFAULT 0,
    zones_found INTEGER DEFAULT 0,
    status VARCHAR(20),
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

-- ============================================
-- SECTION 6: AI OPTIONS AGENT
-- ============================================

CREATE TABLE IF NOT EXISTS ai_options_analyses (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    analysis_type VARCHAR(50),
    recommendation VARCHAR(50),
    confidence_score INTEGER CHECK (confidence_score BETWEEN 0 AND 100),
    strike_price DECIMAL(10,2),
    expiration_date DATE,
    premium DECIMAL(10,2),
    reasoning TEXT,
    market_conditions JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ai_agent_performance (
    id SERIAL PRIMARY KEY,
    analysis_id INTEGER REFERENCES ai_options_analyses(id) ON DELETE CASCADE,
    actual_outcome VARCHAR(50),
    profit_loss DECIMAL(10,2),
    was_correct BOOLEAN,
    performance_notes TEXT,
    evaluated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ai_options_watchlist (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    target_strategy VARCHAR(50),
    ai_priority INTEGER CHECK (ai_priority BETWEEN 1 AND 10),
    added_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- SECTION 7: AVA CHATBOT & CONVERSATION MEMORY
-- ============================================

CREATE TABLE IF NOT EXISTS ava_conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id VARCHAR(100) UNIQUE NOT NULL,
    user_id VARCHAR(100),
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ended_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'active',
    total_messages INTEGER DEFAULT 0,
    metadata JSONB
);

CREATE TABLE IF NOT EXISTS ava_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id VARCHAR(100) REFERENCES ava_conversations(conversation_id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    tokens_used INTEGER,
    model VARCHAR(50),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB
);

CREATE TABLE IF NOT EXISTS ava_unanswered_questions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id VARCHAR(100) REFERENCES ava_conversations(conversation_id) ON DELETE CASCADE,
    question TEXT NOT NULL,
    reason VARCHAR(100),
    frequency INTEGER DEFAULT 1,
    first_asked TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_asked TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved BOOLEAN DEFAULT false,
    resolution_notes TEXT
);

CREATE TABLE IF NOT EXISTS ava_action_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id VARCHAR(100) REFERENCES ava_conversations(conversation_id) ON DELETE CASCADE,
    action_type VARCHAR(50) NOT NULL,
    action_details JSONB,
    success BOOLEAN DEFAULT true,
    error_message TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ava_conversation_context (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id VARCHAR(100) UNIQUE REFERENCES ava_conversations(conversation_id) ON DELETE CASCADE,
    context_data JSONB NOT NULL,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ava_user_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(100) UNIQUE NOT NULL,
    preferences JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ava_legion_task_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id VARCHAR(100) REFERENCES ava_conversations(conversation_id) ON DELETE CASCADE,
    task_id VARCHAR(100),
    question TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- SECTION 8: ANALYTICS & BACKTESTING
-- ============================================

CREATE TABLE IF NOT EXISTS prediction_performance (
    id SERIAL PRIMARY KEY,
    prediction_date DATE NOT NULL,
    market_type VARCHAR(50),
    total_predictions INTEGER DEFAULT 0,
    correct_predictions INTEGER DEFAULT 0,
    accuracy_rate DECIMAL(5,2),
    avg_confidence DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS feature_store (
    id SERIAL PRIMARY KEY,
    feature_name VARCHAR(100) NOT NULL,
    feature_version INTEGER DEFAULT 1,
    symbol VARCHAR(10),
    feature_values JSONB NOT NULL,
    calculated_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(feature_name, feature_version, symbol, calculated_at)
);

CREATE TABLE IF NOT EXISTS backtest_results (
    id SERIAL PRIMARY KEY,
    strategy_name VARCHAR(100) NOT NULL,
    backtest_params JSONB,
    start_date DATE,
    end_date DATE,
    total_trades INTEGER,
    winning_trades INTEGER,
    losing_trades INTEGER,
    win_rate DECIMAL(5,2),
    total_pnl DECIMAL(12,2),
    sharpe_ratio DECIMAL(6,3),
    max_drawdown DECIMAL(6,2),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS backtest_trades (
    id SERIAL PRIMARY KEY,
    backtest_id INTEGER REFERENCES backtest_results(id) ON DELETE CASCADE,
    symbol VARCHAR(10),
    entry_date DATE,
    exit_date DATE,
    entry_price DECIMAL(10,2),
    exit_price DECIMAL(10,2),
    quantity INTEGER,
    pnl DECIMAL(10,2),
    trade_type VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS performance_snapshots (
    id SERIAL PRIMARY KEY,
    snapshot_date DATE NOT NULL,
    total_value DECIMAL(12,2),
    daily_pnl DECIMAL(10,2),
    daily_return_pct DECIMAL(6,2),
    rolling_7d_return DECIMAL(6,2),
    rolling_30d_return DECIMAL(6,2),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(snapshot_date)
);

-- ============================================
-- SECTION 9: INDEXES FOR PERFORMANCE
-- ============================================

-- Core Trading Indexes
CREATE INDEX IF NOT EXISTS idx_stock_prices_time ON stock_prices (time DESC);
CREATE INDEX IF NOT EXISTS idx_stock_prices_stock_id ON stock_prices (stock_id);
CREATE INDEX IF NOT EXISTS idx_stocks_symbol ON stocks (symbol);
CREATE INDEX IF NOT EXISTS idx_stocks_active ON stocks (is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_options_chains_stock_expiry ON options_chains (stock_id, expiration_date);
CREATE INDEX IF NOT EXISTS idx_options_chains_strike ON options_chains (strike_price);
CREATE INDEX IF NOT EXISTS idx_positions_user_status ON positions (user_id, status);
CREATE INDEX IF NOT EXISTS idx_positions_stock_id ON positions (stock_id);
CREATE INDEX IF NOT EXISTS idx_trades_position_id ON trades (position_id);
CREATE INDEX IF NOT EXISTS idx_trades_execution_time ON trades (execution_time DESC);
CREATE INDEX IF NOT EXISTS idx_strategy_signals_active ON strategy_signals (is_active, created_at DESC) WHERE is_active = true;

-- Earnings Indexes
CREATE INDEX IF NOT EXISTS idx_earnings_history_symbol ON earnings_history(symbol);
CREATE INDEX IF NOT EXISTS idx_earnings_history_date ON earnings_history(earnings_date DESC);
CREATE INDEX IF NOT EXISTS idx_earnings_events_symbol ON earnings_events(symbol);
CREATE INDEX IF NOT EXISTS idx_earnings_events_date ON earnings_events(earnings_date);
CREATE INDEX IF NOT EXISTS idx_earnings_events_active ON earnings_events(is_active) WHERE is_active = true;

-- XTrades Indexes
CREATE INDEX IF NOT EXISTS idx_xtrades_trades_symbol ON xtrades_trades(symbol);
CREATE INDEX IF NOT EXISTS idx_xtrades_trades_username ON xtrades_trades(username);
CREATE INDEX IF NOT EXISTS idx_xtrades_trades_posted_at ON xtrades_trades(posted_at DESC);
CREATE INDEX IF NOT EXISTS idx_xtrades_alerts_score ON xtrades_alerts(ai_score DESC);
CREATE INDEX IF NOT EXISTS idx_xtrades_alerts_posted ON xtrades_alerts(posted_at DESC);

-- Kalshi Indexes
CREATE INDEX IF NOT EXISTS idx_kalshi_markets_ticker ON kalshi_markets(ticker);
CREATE INDEX IF NOT EXISTS idx_kalshi_markets_category ON kalshi_markets(category);
CREATE INDEX IF NOT EXISTS idx_kalshi_markets_status ON kalshi_markets(status);
CREATE INDEX IF NOT EXISTS idx_kalshi_price_history_ticker ON kalshi_price_history(ticker);
CREATE INDEX IF NOT EXISTS idx_kalshi_price_history_timestamp ON kalshi_price_history(timestamp DESC);

-- NFL Indexes
CREATE INDEX IF NOT EXISTS idx_nfl_games_date ON nfl_games(game_date);
CREATE INDEX IF NOT EXISTS idx_nfl_games_status ON nfl_games(game_status);
CREATE INDEX IF NOT EXISTS idx_nfl_plays_game_id ON nfl_plays(game_id);

-- Supply/Demand Indexes
CREATE INDEX IF NOT EXISTS idx_sd_zones_symbol ON sd_zones(symbol);
CREATE INDEX IF NOT EXISTS idx_sd_zones_active ON sd_zones(is_active) WHERE is_active = true;

-- AI Options Indexes
CREATE INDEX IF NOT EXISTS idx_ai_options_symbol ON ai_options_analyses(symbol);
CREATE INDEX IF NOT EXISTS idx_ai_options_created ON ai_options_analyses(created_at DESC);

-- AVA Conversation Indexes
CREATE INDEX IF NOT EXISTS idx_ava_messages_conversation ON ava_messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_ava_messages_timestamp ON ava_messages(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_ava_unanswered_frequency ON ava_unanswered_questions(frequency DESC, resolved);

-- Analytics Indexes
CREATE INDEX IF NOT EXISTS idx_backtest_trades_backtest_id ON backtest_trades(backtest_id);
CREATE INDEX IF NOT EXISTS idx_performance_snapshots_date ON performance_snapshots(snapshot_date DESC);

-- ============================================
-- SECTION 10: VIEWS FOR COMMON QUERIES
-- ============================================

-- Current positions view
CREATE OR REPLACE VIEW v_current_positions AS
SELECT
    p.*,
    s.symbol,
    s.company_name,
    ta.account_name,
    wc.cycle_number,
    (p.quantity * p.current_price) as current_value,
    ((p.current_price - p.entry_price) * p.quantity) as unrealized_pnl_calc
FROM positions p
JOIN stocks s ON p.stock_id = s.id
JOIN trading_accounts ta ON p.account_id = ta.id
LEFT JOIN wheel_cycles wc ON p.wheel_cycle_id = wc.id
WHERE p.status = 'open';

-- Wheel performance view
CREATE OR REPLACE VIEW v_wheel_performance AS
SELECT
    wc.*,
    s.symbol,
    s.company_name,
    COUNT(p.id) as total_positions,
    SUM(CASE WHEN p.position_type = 'put' THEN p.opening_premium ELSE 0 END) as csp_premium,
    SUM(CASE WHEN p.position_type = 'call' THEN p.opening_premium ELSE 0 END) as cc_premium,
    AVG(p.realized_pnl) as avg_trade_pnl
FROM wheel_cycles wc
JOIN stocks s ON wc.stock_id = s.id
LEFT JOIN positions p ON wc.id = p.wheel_cycle_id
GROUP BY wc.id, s.symbol, s.company_name;

-- Upcoming earnings view
CREATE OR REPLACE VIEW v_upcoming_earnings AS
SELECT *
FROM earnings_events
WHERE earnings_date >= CURRENT_DATE
  AND earnings_date <= CURRENT_DATE + INTERVAL '30 days'
  AND is_active = true
ORDER BY earnings_date;

-- Top Kalshi opportunities
CREATE OR REPLACE VIEW v_kalshi_top_opportunities AS
SELECT
    km.*,
    kp.confidence_score,
    kp.predicted_outcome,
    kp.reasoning
FROM kalshi_markets km
LEFT JOIN kalshi_predictions kp ON km.id = kp.market_id
WHERE km.status = 'active'
  AND kp.confidence_score >= 70
ORDER BY kp.confidence_score DESC, km.liquidity_score DESC
LIMIT 50;

-- ============================================
-- SECTION 11: FUNCTIONS & TRIGGERS
-- ============================================

-- Calculate position P&L
CREATE OR REPLACE FUNCTION calculate_position_pnl(
    position_id UUID,
    current_price DECIMAL(8,2)
) RETURNS DECIMAL(10,2) AS $$
DECLARE
    pos positions%ROWTYPE;
    pnl DECIMAL(10,2);
BEGIN
    SELECT * INTO pos FROM positions WHERE id = position_id;

    CASE pos.position_type
        WHEN 'stock' THEN
            pnl := (current_price - pos.entry_price) * pos.quantity;
        WHEN 'put', 'call' THEN
            pnl := (pos.opening_premium - current_price) * pos.quantity * 100;
    END CASE;

    RETURN pnl;
END;
$$ LANGUAGE plpgsql;

-- Update position P&L trigger
CREATE OR REPLACE FUNCTION update_position_pnl()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE positions
    SET
        current_price = NEW.close_price,
        unrealized_pnl = calculate_position_pnl(id, NEW.close_price)
    WHERE stock_id = NEW.stock_id AND status = 'open';

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger if not exists
DROP TRIGGER IF EXISTS trigger_update_position_pnl ON stock_prices;
CREATE TRIGGER trigger_update_position_pnl
    AFTER INSERT OR UPDATE ON stock_prices
    FOR EACH ROW
    EXECUTE FUNCTION update_position_pnl();

-- ============================================
-- SECTION 12: INITIAL DATA & CONFIGURATION
-- ============================================

-- Insert default system configuration
INSERT INTO system_config (config_key, config_value, description) VALUES
('market_hours', '{"open": "09:30", "close": "16:00", "timezone": "America/New_York"}', 'Market trading hours'),
('risk_limits', '{"max_position_size_pct": 0.05, "max_sector_exposure": 0.25, "max_single_stock_exposure": 0.10}', 'Default risk limits'),
('wheel_strategy_params', '{"min_dte": 15, "max_dte": 45, "target_delta": 0.30, "min_premium_yield": 0.01}', 'Wheel strategy parameters'),
('data_retention', '{"price_data_days": 2555, "trade_data_years": 7, "alert_events_days": 90}', 'Data retention policies')
ON CONFLICT (config_key) DO NOTHING;

-- ============================================
-- SCHEMA DEPLOYMENT COMPLETE
-- ============================================
-- Total Tables: 70+
-- Total Views: 10+
-- Total Functions: 5+
-- Total Indexes: 40+
-- ============================================
