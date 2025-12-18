-- ============================================================================
-- Performance Optimization: Add Critical Database Indexes
-- ============================================================================
-- Purpose: Optimize query performance across all core tables
-- Created: 2025-11-20
-- Version: 1.0
-- Database: Magnus (PostgreSQL)
-- ============================================================================
--
-- This migration adds critical indexes to optimize query performance:
-- 1. Stocks table - sector/industry/optionable filtering
-- 2. Options chains - symbol/expiry and strike/type lookups
-- 3. Positions - user queries and status filtering
-- 4. Kalshi markets - active market queries
-- 5. NFL games - upcoming games queries
--
-- All indexes use IF NOT EXISTS to ensure idempotency.
-- Partial indexes are used where appropriate to reduce storage and improve
-- performance by filtering out rarely-accessed rows.
--
-- Rollback: Run add_performance_indexes_rollback.sql
-- ============================================================================

-- ============================================================================
-- STOCKS TABLE INDEXES
-- ============================================================================
-- These indexes optimize filtering by sector, industry, and optionable status
-- Critical for watchlist filtering and strategy signal queries
-- ============================================================================

-- Index for sector-based stock filtering
-- Usage: WHERE sector = 'Technology'
CREATE INDEX IF NOT EXISTS idx_stocks_sector
    ON stocks (sector)
    WHERE sector IS NOT NULL;
COMMENT ON INDEX idx_stocks_sector IS 'Optimizes stock filtering by sector';

-- Index for industry-based stock filtering
-- Usage: WHERE industry = 'Software'
CREATE INDEX IF NOT EXISTS idx_stocks_industry
    ON stocks (industry)
    WHERE industry IS NOT NULL;
COMMENT ON INDEX idx_stocks_industry IS 'Optimizes stock filtering by industry';

-- Index for optionable stock filtering (partial index)
-- Only indexes stocks where is_optionable = true, reducing storage footprint
-- Usage: WHERE is_optionable = true
CREATE INDEX IF NOT EXISTS idx_stocks_optionable
    ON stocks (is_optionable)
    WHERE is_optionable = true;
COMMENT ON INDEX idx_stocks_optionable IS 'Optimizes filtering of optionable stocks; partial index';

-- ============================================================================
-- OPTIONS CHAINS TABLE INDEXES
-- ============================================================================
-- These indexes optimize common option chain query patterns
-- Critical for chain analysis, strategy screening, and expiration tracking
-- ============================================================================

-- Composite index for symbol + expiration + type lookups
-- Usage: WHERE stock_id = X AND expiration_date = Y AND option_type = 'CALL'
-- Benefits: Avoids join to stocks table, covers all columns
CREATE INDEX IF NOT EXISTS idx_options_symbol_expiry
    ON options_chains (stock_id, expiration_date, option_type);
COMMENT ON INDEX idx_options_symbol_expiry IS 'Composite index for chain analysis by symbol, expiry, and type';

-- Composite index for strike price + option type lookups
-- Usage: WHERE strike_price BETWEEN X AND Y AND option_type = 'PUT'
-- Benefits: Covers strike-based analysis across multiple symbols
CREATE INDEX IF NOT EXISTS idx_options_strike_type
    ON options_chains (strike_price, option_type);
COMMENT ON INDEX idx_options_strike_type IS 'Composite index for strike analysis by price and type';

-- ============================================================================
-- POSITIONS TABLE INDEXES
-- ============================================================================
-- These indexes optimize position query patterns for users
-- Critical for portfolio dashboards, status tracking, and user-specific views
-- ============================================================================

-- Composite index for user + stock lookups
-- Usage: WHERE user_id = X AND stock_id = Y
-- Benefits: Finds specific user positions for single stock efficiently
CREATE INDEX IF NOT EXISTS idx_positions_user_symbol
    ON positions (user_id, stock_id);
COMMENT ON INDEX idx_positions_user_symbol IS 'Optimizes user position lookups by symbol';

-- Partial index for open/active positions (filtered)
-- Usage: WHERE status IN ('open', 'assigned', 'expired')
-- Benefits: Reduces index size by excluding closed positions
CREATE INDEX IF NOT EXISTS idx_positions_status
    ON positions (status)
    WHERE status IN ('open', 'assigned', 'expired');
COMMENT ON INDEX idx_positions_status IS 'Partial index for active position status filtering';

-- ============================================================================
-- KALSHI MARKETS TABLE INDEXES
-- ============================================================================
-- These indexes optimize Kalshi market queries
-- Critical for active market discovery and game date filtering
-- ============================================================================

-- Composite partial index for active markets by game date
-- Usage: WHERE status = 'open' ORDER BY game_date
-- Benefits: Fast filtering of active markets, sorted by game date
-- Partial index: Only indexes open markets, significantly reduces size
CREATE INDEX IF NOT EXISTS idx_kalshi_markets_active
    ON kalshi_markets (status, game_date)
    WHERE status = 'open';
COMMENT ON INDEX idx_kalshi_markets_active IS 'Partial index for active Kalshi markets sorted by game date';

-- ============================================================================
-- NFL GAMES TABLE INDEXES
-- ============================================================================
-- These indexes optimize NFL game queries
-- Critical for upcoming game discovery and live game tracking
-- ============================================================================

-- Partial index for upcoming games
-- Usage: WHERE game_status IN ('scheduled', 'live') AND game_time > NOW()
-- Benefits: Fast discovery of relevant games, filters out completed games
-- Partial index: Only indexes relevant games, significantly improves performance
CREATE INDEX IF NOT EXISTS idx_nfl_games_upcoming
    ON nfl_games (game_time)
    WHERE game_status IN ('scheduled', 'live') AND game_time > NOW();
COMMENT ON INDEX idx_nfl_games_upcoming IS 'Partial index for upcoming NFL games';

-- ============================================================================
-- PERFORMANCE VERIFICATION
-- ============================================================================
-- After applying this migration, verify indexes are created and used:
--
-- 1. List all indexes in the database:
--    SELECT tablename, indexname FROM pg_indexes
--    WHERE schemaname = 'public'
--    ORDER BY tablename, indexname;
--
-- 2. Check index size and usage:
--    SELECT
--        indexrelname,
--        pg_size_pretty(pg_relation_size(indexrelid)) as index_size,
--        idx_scan as scans
--    FROM pg_stat_user_indexes
--    ORDER BY pg_relation_size(indexrelid) DESC;
--
-- 3. Analyze slow queries before and after:
--    EXPLAIN ANALYZE SELECT * FROM stocks WHERE sector = 'Technology';
--    EXPLAIN ANALYZE SELECT * FROM positions WHERE user_id = X AND stock_id = Y;
--    EXPLAIN ANALYZE SELECT * FROM kalshi_markets WHERE status = 'open' ORDER BY game_date;
--
-- ============================================================================
-- QUERY OPTIMIZATION EXAMPLES
-- ============================================================================
-- These queries now benefit from the new indexes:
--
-- 1. Get all optionable stocks in Technology sector:
--    SELECT symbol, company_name FROM stocks
--    WHERE sector = 'Technology' AND is_optionable = true;
--
-- 2. Get available options for a stock expiring in 30 days:
--    SELECT strike_price, option_type, bid_price, ask_price
--    FROM options_chains
--    WHERE stock_id = '123' AND expiration_date = '2025-12-20'
--    ORDER BY strike_price;
--
-- 3. Get all open positions for a user:
--    SELECT p.*, s.symbol FROM positions p
--    JOIN stocks s ON p.stock_id = s.id
--    WHERE p.user_id = '456' AND p.status = 'open';
--
-- 4. Find active Kalshi markets in next 7 days:
--    SELECT ticker, title, game_date FROM kalshi_markets
--    WHERE status = 'open' AND game_date BETWEEN NOW() AND NOW() + INTERVAL '7 days'
--    ORDER BY game_date;
--
-- 5. Get upcoming NFL games this week:
--    SELECT game_id, home_team, away_team, game_time
--    FROM nfl_games
--    WHERE game_status IN ('scheduled', 'live')
--    AND game_time > NOW()
--    AND game_time <= NOW() + INTERVAL '7 days'
--    ORDER BY game_time;
--
-- ============================================================================
-- STORAGE AND MAINTENANCE NOTES
-- ============================================================================
--
-- Index Storage Impact:
-- - Partial indexes (stocks_optionable, positions_status, kalshi_markets_active,
--   nfl_games_upcoming) consume significantly less disk space than full indexes
-- - Composite indexes provide better performance for queries filtering on
--   multiple columns but slightly slower for single-column lookups
--
-- Maintenance Recommendations:
-- 1. Regular VACUUM ANALYZE to update query planner statistics:
--    VACUUM ANALYZE;
--    This should be scheduled weekly or after large data changes
--
-- 2. Monitor index bloat:
--    SELECT indexrelname, pg_size_pretty(pg_relation_size(indexrelid))
--    FROM pg_stat_user_indexes
--    ORDER BY pg_relation_size(indexrelid) DESC;
--
-- 3. REINDEX if performance degrades (monthly maintenance):
--    REINDEX INDEX idx_stocks_sector;
--    REINDEX INDEX idx_options_symbol_expiry;
--    REINDEX INDEX idx_positions_user_symbol;
--
-- 4. Monitor query performance:
--    Enable pg_stat_statements extension:
--    CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
--    Then analyze top slow queries:
--    SELECT query, mean_exec_time FROM pg_stat_statements
--    ORDER BY mean_exec_time DESC LIMIT 10;
--
-- ============================================================================
-- ROLLBACK INSTRUCTIONS
-- ============================================================================
-- To remove all indexes added by this migration, execute:
--    DROP INDEX IF EXISTS idx_stocks_sector;
--    DROP INDEX IF EXISTS idx_stocks_industry;
--    DROP INDEX IF EXISTS idx_stocks_optionable;
--    DROP INDEX IF EXISTS idx_options_symbol_expiry;
--    DROP INDEX IF EXISTS idx_options_strike_type;
--    DROP INDEX IF EXISTS idx_positions_user_symbol;
--    DROP INDEX IF EXISTS idx_positions_status;
--    DROP INDEX IF EXISTS idx_kalshi_markets_active;
--    DROP INDEX IF EXISTS idx_nfl_games_upcoming;
--
-- Or run the included rollback script:
--    psql -U postgres -d magnus -f add_performance_indexes_rollback.sql
--
-- ============================================================================

-- End of migration
