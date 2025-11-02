-- ============================================================================
-- SECTOR ANALYSIS TABLES - Magnus Trading Platform
-- Created: 2025-11-02
-- Purpose: Comprehensive sector classification and analysis for wheel strategy
-- ============================================================================

-- Table 1: Stock Sectors (Classification)
CREATE TABLE IF NOT EXISTS stock_sectors (
    symbol VARCHAR(10) PRIMARY KEY,
    sector VARCHAR(100) NOT NULL,
    industry VARCHAR(200),
    market_cap BIGINT,
    market_cap_category VARCHAR(20),
    is_optionable BOOLEAN DEFAULT true,
    last_updated TIMESTAMP DEFAULT NOW()
);

-- Table 2: Sector Performance Metrics
CREATE TABLE IF NOT EXISTS sector_analysis (
    sector VARCHAR(100) PRIMARY KEY,
    stock_count INTEGER DEFAULT 0,
    avg_premium_yield DECIMAL(10,4),
    avg_monthly_return DECIMAL(10,4),
    top_stocks TEXT[],
    recommended_etf VARCHAR(10),
    overall_score DECIMAL(5,2),
    trend_direction VARCHAR(20),
    ai_recommendation TEXT,
    best_strategy VARCHAR(50),
    risk_level VARCHAR(20),
    last_updated TIMESTAMP DEFAULT NOW()
);

-- Table 3: Sector ETFs
CREATE TABLE IF NOT EXISTS sector_etfs (
    etf_symbol VARCHAR(10) PRIMARY KEY,
    etf_name VARCHAR(255),
    sector VARCHAR(100) NOT NULL,
    expense_ratio DECIMAL(5,4),
    has_options BOOLEAN DEFAULT true,
    description TEXT
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_stock_sectors_sector ON stock_sectors(sector);
CREATE INDEX IF NOT EXISTS idx_sector_etfs_sector ON sector_etfs(sector);

-- Seed GICS sectors
INSERT INTO sector_analysis (sector, best_strategy) VALUES
    ('Technology', 'CSP'),
    ('Healthcare', 'CSP'),
    ('Financials', 'CSP'),
    ('Consumer Discretionary', 'CSP'),
    ('Consumer Staples', 'ETF'),
    ('Industrials', 'CSP'),
    ('Energy', 'CSP'),
    ('Utilities', 'ETF'),
    ('Real Estate', 'ETF'),
    ('Materials', 'CSP'),
    ('Communication Services', 'CSP')
ON CONFLICT (sector) DO NOTHING;

-- Seed sector ETFs
INSERT INTO sector_etfs (etf_symbol, etf_name, sector, expense_ratio, description) VALUES
    ('XLK', 'Technology Select Sector SPDR', 'Technology', 0.0010, 'Tech sector ETF'),
    ('XLV', 'Health Care Select Sector SPDR', 'Healthcare', 0.0010, 'Healthcare sector'),
    ('XLF', 'Financial Select Sector SPDR', 'Financials', 0.0010, 'Financial sector'),
    ('XLY', 'Consumer Discretionary SPDR', 'Consumer Discretionary', 0.0010, 'Consumer disc'),
    ('XLP', 'Consumer Staples SPDR', 'Consumer Staples', 0.0010, 'Consumer staples'),
    ('XLI', 'Industrial Select Sector SPDR', 'Industrials', 0.0010, 'Industrial sector'),
    ('XLE', 'Energy Select Sector SPDR', 'Energy', 0.0010, 'Energy sector'),
    ('XLU', 'Utilities Select Sector SPDR', 'Utilities', 0.0010, 'Utilities sector'),
    ('XLRE', 'Real Estate Select Sector SPDR', 'Real Estate', 0.0010, 'Real estate'),
    ('XLB', 'Materials Select Sector SPDR', 'Materials', 0.0010, 'Materials sector'),
    ('XLC', 'Communication Services SPDR', 'Communication Services', 0.0010, 'Communications')
ON CONFLICT (etf_symbol) DO NOTHING;
