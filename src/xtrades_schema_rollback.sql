-- ============================================================================
-- Xtrades Watchlists Feature - Rollback Script
-- ============================================================================
-- Purpose: Remove all Xtrades-related tables and indexes
-- Database: magnus (PostgreSQL)
-- Created: 2025-11-02
-- ============================================================================
-- IMPORTANT: This will DELETE ALL DATA in these tables
-- Make sure to backup data before running this script
-- ============================================================================

-- Drop tables in reverse order of foreign key dependencies
-- This ensures we don't violate foreign key constraints

-- Drop notifications table first (references xtrades_trades)
DROP TABLE IF EXISTS xtrades_notifications CASCADE;

-- Drop sync log (no foreign keys, but logically dependent)
DROP TABLE IF EXISTS xtrades_sync_log CASCADE;

-- Drop trades table (references xtrades_profiles)
DROP TABLE IF EXISTS xtrades_trades CASCADE;

-- Drop profiles table last (base table)
DROP TABLE IF EXISTS xtrades_profiles CASCADE;

-- ============================================================================
-- Verify all tables and indexes are removed
-- ============================================================================

SELECT
    CASE
        WHEN COUNT(*) = 0 THEN 'SUCCESS: All Xtrades tables have been removed'
        ELSE 'WARNING: Some Xtrades tables still exist'
    END as rollback_status
FROM information_schema.tables
WHERE table_schema = 'public'
    AND table_name LIKE 'xtrades_%';

-- List any remaining Xtrades-related objects
SELECT
    table_name,
    table_type
FROM information_schema.tables
WHERE table_schema = 'public'
    AND table_name LIKE 'xtrades_%';

SELECT 'Rollback complete!' as message;
