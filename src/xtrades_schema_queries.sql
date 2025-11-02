-- ============================================================================
-- Xtrades Watchlists - Useful Query Collection
-- ============================================================================
-- Purpose: Common queries for working with Xtrades data
-- Database: magnus (PostgreSQL)
-- ============================================================================

-- ============================================================================
-- PROFILE MANAGEMENT QUERIES
-- ============================================================================

-- Get all active profiles with their statistics
SELECT
    p.id,
    p.username,
    p.display_name,
    p.active,
    p.last_sync,
    p.last_sync_status,
    p.total_trades_scraped,
    COUNT(t.id) as current_trade_count,
    SUM(CASE WHEN t.status = 'open' THEN 1 ELSE 0 END) as open_positions,
    SUM(CASE WHEN t.status = 'closed' THEN 1 ELSE 0 END) as closed_trades
FROM xtrades_profiles p
LEFT JOIN xtrades_trades t ON p.id = t.profile_id
WHERE p.active = TRUE
GROUP BY p.id, p.username, p.display_name, p.active, p.last_sync, p.last_sync_status, p.total_trades_scraped
ORDER BY p.last_sync DESC NULLS LAST;

-- Find profiles that haven't synced recently (over 24 hours)
SELECT
    username,
    display_name,
    last_sync,
    last_sync_status,
    NOW() - last_sync as time_since_sync
FROM xtrades_profiles
WHERE active = TRUE
    AND (last_sync IS NULL OR last_sync < NOW() - INTERVAL '24 hours')
ORDER BY last_sync ASC NULLS FIRST;

-- ============================================================================
-- TRADE ANALYSIS QUERIES
-- ============================================================================

-- Get all open positions across all profiles
SELECT
    p.username,
    t.ticker,
    t.strategy,
    t.action,
    t.strike_price,
    t.expiration_date,
    t.entry_price,
    t.entry_date,
    t.quantity,
    EXTRACT(DAY FROM (t.expiration_date - CURRENT_DATE)) as days_to_expiration,
    t.alert_text
FROM xtrades_trades t
JOIN xtrades_profiles p ON t.profile_id = p.id
WHERE t.status = 'open'
ORDER BY t.expiration_date ASC, t.ticker;

-- Get recent closed trades with P&L
SELECT
    p.username,
    t.ticker,
    t.strategy,
    t.entry_date,
    t.exit_date,
    t.entry_price,
    t.exit_price,
    t.pnl,
    t.pnl_percent,
    EXTRACT(DAY FROM (t.exit_date - t.entry_date)) as days_held
FROM xtrades_trades t
JOIN xtrades_profiles p ON t.profile_id = p.id
WHERE t.status = 'closed'
    AND t.exit_date >= NOW() - INTERVAL '30 days'
ORDER BY t.exit_date DESC;

-- Performance by strategy
SELECT
    strategy,
    COUNT(*) as total_trades,
    COUNT(CASE WHEN status = 'closed' THEN 1 END) as closed_trades,
    COUNT(CASE WHEN status = 'open' THEN 1 END) as open_trades,
    SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
    SUM(CASE WHEN pnl < 0 THEN 1 ELSE 0 END) as losing_trades,
    SUM(pnl) as total_pnl,
    AVG(pnl) as avg_pnl,
    AVG(pnl_percent) as avg_pnl_percent,
    ROUND(
        (SUM(CASE WHEN pnl > 0 THEN 1 ELSE 0 END)::DECIMAL /
         NULLIF(COUNT(CASE WHEN status = 'closed' THEN 1 END), 0)) * 100,
        2
    ) as win_rate_percent
FROM xtrades_trades
WHERE strategy IS NOT NULL
GROUP BY strategy
ORDER BY total_pnl DESC NULLS LAST;

-- Performance by ticker (top performers)
SELECT
    ticker,
    COUNT(*) as total_trades,
    COUNT(CASE WHEN status = 'closed' THEN 1 END) as closed_trades,
    SUM(pnl) as total_pnl,
    AVG(pnl) as avg_pnl,
    AVG(pnl_percent) as avg_pnl_percent,
    MAX(pnl) as best_trade,
    MIN(pnl) as worst_trade
FROM xtrades_trades
WHERE status = 'closed' AND pnl IS NOT NULL
GROUP BY ticker
HAVING COUNT(CASE WHEN status = 'closed' THEN 1 END) >= 2
ORDER BY total_pnl DESC
LIMIT 20;

-- Performance by profile
SELECT
    p.username,
    p.display_name,
    COUNT(*) as total_trades,
    COUNT(CASE WHEN t.status = 'closed' THEN 1 END) as closed_trades,
    SUM(t.pnl) as total_pnl,
    AVG(t.pnl) as avg_pnl,
    AVG(t.pnl_percent) as avg_pnl_percent,
    ROUND(
        (SUM(CASE WHEN t.pnl > 0 THEN 1 ELSE 0 END)::DECIMAL /
         NULLIF(COUNT(CASE WHEN t.status = 'closed' THEN 1 END), 0)) * 100,
        2
    ) as win_rate_percent
FROM xtrades_profiles p
LEFT JOIN xtrades_trades t ON p.id = t.profile_id
WHERE t.status = 'closed' AND t.pnl IS NOT NULL
GROUP BY p.id, p.username, p.display_name
ORDER BY total_pnl DESC;

-- Recent trades (last 24 hours)
SELECT
    p.username,
    t.ticker,
    t.strategy,
    t.action,
    t.status,
    t.strike_price,
    t.expiration_date,
    t.entry_price,
    t.exit_price,
    t.pnl,
    t.alert_timestamp,
    t.alert_text
FROM xtrades_trades t
JOIN xtrades_profiles p ON t.profile_id = p.id
WHERE t.alert_timestamp >= NOW() - INTERVAL '24 hours'
ORDER BY t.alert_timestamp DESC;

-- Find duplicate trades (by alert_id)
SELECT
    xtrades_alert_id,
    COUNT(*) as duplicate_count,
    STRING_AGG(id::TEXT, ', ') as trade_ids
FROM xtrades_trades
WHERE xtrades_alert_id IS NOT NULL
GROUP BY xtrades_alert_id
HAVING COUNT(*) > 1;

-- ============================================================================
-- EXPIRATION ANALYSIS
-- ============================================================================

-- Trades expiring soon (next 7 days)
SELECT
    p.username,
    t.ticker,
    t.strategy,
    t.strike_price,
    t.expiration_date,
    t.entry_price,
    EXTRACT(DAY FROM (t.expiration_date - CURRENT_DATE)) as days_until_expiration,
    t.alert_text
FROM xtrades_trades t
JOIN xtrades_profiles p ON t.profile_id = p.id
WHERE t.status = 'open'
    AND t.expiration_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '7 days'
ORDER BY t.expiration_date ASC;

-- Expired trades that are still marked as open (data quality check)
SELECT
    p.username,
    t.ticker,
    t.strategy,
    t.expiration_date,
    CURRENT_DATE - t.expiration_date as days_past_expiration,
    t.alert_text
FROM xtrades_trades t
JOIN xtrades_profiles p ON t.profile_id = p.id
WHERE t.status = 'open'
    AND t.expiration_date < CURRENT_DATE;

-- ============================================================================
-- SYNC MONITORING QUERIES
-- ============================================================================

-- Recent sync history
SELECT
    sync_timestamp,
    profiles_synced,
    trades_found,
    new_trades,
    updated_trades,
    status,
    duration_seconds,
    errors
FROM xtrades_sync_log
ORDER BY sync_timestamp DESC
LIMIT 10;

-- Sync success rate (last 30 days)
SELECT
    status,
    COUNT(*) as sync_count,
    ROUND(COUNT(*)::DECIMAL / SUM(COUNT(*)) OVER () * 100, 2) as percentage,
    AVG(duration_seconds) as avg_duration,
    AVG(new_trades) as avg_new_trades
FROM xtrades_sync_log
WHERE sync_timestamp >= NOW() - INTERVAL '30 days'
GROUP BY status
ORDER BY sync_count DESC;

-- Failed syncs with errors
SELECT
    sync_timestamp,
    profiles_synced,
    errors,
    duration_seconds
FROM xtrades_sync_log
WHERE status = 'failed'
    AND sync_timestamp >= NOW() - INTERVAL '7 days'
ORDER BY sync_timestamp DESC;

-- ============================================================================
-- NOTIFICATION QUERIES
-- ============================================================================

-- Recent notifications sent
SELECT
    n.sent_at,
    n.notification_type,
    n.status,
    p.username,
    t.ticker,
    t.strategy,
    t.action
FROM xtrades_notifications n
JOIN xtrades_trades t ON n.trade_id = t.id
JOIN xtrades_profiles p ON t.profile_id = p.id
ORDER BY n.sent_at DESC
LIMIT 20;

-- Failed notifications
SELECT
    n.sent_at,
    n.notification_type,
    n.error_message,
    p.username,
    t.ticker,
    t.alert_text
FROM xtrades_notifications n
JOIN xtrades_trades t ON n.trade_id = t.id
JOIN xtrades_profiles p ON t.profile_id = p.id
WHERE n.status = 'failed'
ORDER BY n.sent_at DESC;

-- Trades without notifications (possibly missed)
SELECT
    t.id,
    p.username,
    t.ticker,
    t.strategy,
    t.status,
    t.alert_timestamp,
    COUNT(n.id) as notification_count
FROM xtrades_trades t
JOIN xtrades_profiles p ON t.profile_id = p.id
LEFT JOIN xtrades_notifications n ON t.id = n.trade_id
WHERE t.scraped_at >= NOW() - INTERVAL '7 days'
GROUP BY t.id, p.username, t.ticker, t.strategy, t.status, t.alert_timestamp
HAVING COUNT(n.id) = 0
ORDER BY t.alert_timestamp DESC;

-- ============================================================================
-- DATA QUALITY CHECKS
-- ============================================================================

-- Trades with missing critical data
SELECT
    'Missing Strategy' as issue,
    COUNT(*) as count
FROM xtrades_trades
WHERE strategy IS NULL
UNION ALL
SELECT
    'Missing Entry Price' as issue,
    COUNT(*) as count
FROM xtrades_trades
WHERE entry_price IS NULL AND status IN ('open', 'closed')
UNION ALL
SELECT
    'Missing Exit Price (Closed)' as issue,
    COUNT(*) as count
FROM xtrades_trades
WHERE status = 'closed' AND exit_price IS NULL
UNION ALL
SELECT
    'Missing PnL (Closed)' as issue,
    COUNT(*) as count
FROM xtrades_trades
WHERE status = 'closed' AND pnl IS NULL;

-- Trades with inconsistent data
SELECT
    p.username,
    t.ticker,
    t.status,
    t.entry_date,
    t.exit_date,
    t.entry_price,
    t.exit_price,
    t.pnl,
    'Exit before entry' as issue
FROM xtrades_trades t
JOIN xtrades_profiles p ON t.profile_id = p.id
WHERE t.exit_date IS NOT NULL
    AND t.entry_date IS NOT NULL
    AND t.exit_date < t.entry_date
UNION ALL
SELECT
    p.username,
    t.ticker,
    t.status,
    t.entry_date,
    t.exit_date,
    t.entry_price,
    t.exit_price,
    t.pnl,
    'Closed but no exit date' as issue
FROM xtrades_trades t
JOIN xtrades_profiles p ON t.profile_id = p.id
WHERE t.status = 'closed' AND t.exit_date IS NULL;

-- ============================================================================
-- SUMMARY DASHBOARD QUERY
-- ============================================================================

-- Overall system statistics
SELECT
    (SELECT COUNT(*) FROM xtrades_profiles WHERE active = TRUE) as active_profiles,
    (SELECT COUNT(*) FROM xtrades_trades) as total_trades,
    (SELECT COUNT(*) FROM xtrades_trades WHERE status = 'open') as open_positions,
    (SELECT COUNT(*) FROM xtrades_trades WHERE status = 'closed') as closed_trades,
    (SELECT SUM(pnl) FROM xtrades_trades WHERE status = 'closed') as total_pnl,
    (SELECT AVG(pnl_percent) FROM xtrades_trades WHERE status = 'closed') as avg_pnl_percent,
    (SELECT MAX(sync_timestamp) FROM xtrades_sync_log) as last_sync,
    (SELECT COUNT(*) FROM xtrades_notifications WHERE sent_at >= NOW() - INTERVAL '24 hours') as notifications_24h;
