-- ============================================================================
-- Rollback: Performance Optimization Indexes
-- ============================================================================
-- Purpose: Remove all indexes added by add_performance_indexes.sql migration
-- Created: 2025-11-20
-- Database: Magnus (PostgreSQL)
-- ============================================================================

BEGIN TRANSACTION;

-- Drop all performance optimization indexes
-- Each DROP IF EXISTS statement allows safe re-running if index doesn't exist

-- Stock table indexes
DROP INDEX IF EXISTS idx_stocks_sector;
DROP INDEX IF EXISTS idx_stocks_industry;
DROP INDEX IF EXISTS idx_stocks_optionable;

-- Options chains table indexes
DROP INDEX IF EXISTS idx_options_symbol_expiry;
DROP INDEX IF EXISTS idx_options_strike_type;

-- Positions table indexes
DROP INDEX IF EXISTS idx_positions_user_symbol;
DROP INDEX IF EXISTS idx_positions_status;

-- Kalshi markets table indexes
DROP INDEX IF EXISTS idx_kalshi_markets_active;

-- NFL games table indexes
DROP INDEX IF EXISTS idx_nfl_games_upcoming;

COMMIT;

-- ============================================================================
-- Verification Query
-- ============================================================================
-- After running this rollback, verify indexes have been removed:
--
-- SELECT tablename, indexname FROM pg_indexes
-- WHERE schemaname = 'public'
-- AND indexname LIKE 'idx_%'
-- ORDER BY tablename, indexname;
--
-- ============================================================================
