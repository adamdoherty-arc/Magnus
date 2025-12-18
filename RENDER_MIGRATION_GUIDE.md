# AVA Platform - Render PostgreSQL Migration Guide

## 🎯 Quick Start (5 Minutes)

### Step 1: Create Render PostgreSQL Database
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"PostgreSQL"**
3. Configure:
   - **Name**: `ava-trading-db`
   - **Database**: `trading` (or keep default `postgres`)
   - **Region**: Oregon (or closest to you)
   - **Plan**: **Starter ($7/month)**
4. Click **"Create Database"**
5. Wait 2-3 minutes for provisioning

### Step 2: Get Connection String
1. Once ready, click on your database
2. Scroll to **"Connections"** section
3. Copy the **"External Connection String"**
   - Looks like: `postgresql://user:pass@dpg-xxx.oregon-postgres.render.com/dbname`

### Step 3: Deploy Schema (First Time Only)
```bash
# Open Command Prompt in your AVA directory
cd c:\Code\Legion\repos\ava

# Run fresh deployment
scripts\deploy_to_render.bat

# When prompted, paste your Render connection string
# Wait ~30 seconds for deployment
```

### Step 4: Update Environment Variables
```bash
# Update .env file with Render credentials
python scripts/update_env_for_render.py

# When prompted, paste your Render connection string again
```

### Step 5: Test Connection
```bash
# Verify everything works
scripts\test_render_connection.bat

# Should show: "✅ Connected successfully!" with table count
```

### Step 6 (Optional): Migrate Existing Data
```bash
# If you have existing local data to migrate
scripts\backup_database.bat
scripts\restore_to_render.bat

# Choose option 2: "Data Restore Only"
```

---

## 🗄️ What Gets Deployed

### Database Architecture (70+ Tables)

**Core Trading (15 tables)**
- `users`, `stocks`, `watchlists`, `watchlist_items`
- `stock_prices` (TimescaleDB hypertable)
- `options_chains`, `positions`, `trades`, `trade_history`
- `trading_accounts`, `wheel_cycles`
- `strategy_signals`, `price_alerts`, `alert_events`
- `risk_metrics`, `system_config`

**Earnings Calendar (4 tables)**
- `earnings_history`, `earnings_events`
- `earnings_sync_status`, `earnings_alerts`

**XTrades Monitoring (8 tables)**
- `xtrades_profiles`, `xtrades_trades`, `xtrades_sync_log`
- `xtrades_alerts`, `xtrades_notification_queue`
- `xtrades_scraper_state`, `xtrades_rate_limiter`

**Kalshi & NFL Markets (13 tables)**
- `kalshi_markets`, `kalshi_predictions`, `kalshi_price_history`, `kalshi_sync_log`
- `nfl_games`, `nfl_plays`, `nfl_player_stats`, `nfl_injuries`
- `nfl_alert_history`, `nfl_data_sync_log`

**Supply/Demand Zones (4 tables)**
- `sd_zones`, `sd_zone_tests`, `sd_alerts`, `sd_scan_log`

**AI Options Agent (3 tables)**
- `ai_options_analyses`, `ai_agent_performance`, `ai_options_watchlist`

**AVA Chatbot (7 tables)**
- `ava_conversations`, `ava_messages`, `ava_unanswered_questions`
- `ava_action_history`, `ava_conversation_context`
- `ava_user_preferences`, `ava_legion_task_log`

**Analytics & Backtesting (5 tables)**
- `prediction_performance`, `feature_store`
- `backtest_results`, `backtest_trades`, `performance_snapshots`

**Plus:**
- 10+ optimized views
- 5+ functions and triggers
- 40+ performance indexes
- TimescaleDB time-series optimization

---

## 💰 Cost Breakdown

### Render PostgreSQL - Starter Plan
- **Monthly**: $7/month
- **Annual**: $84/year
- **Storage**: 10GB included
- **RAM**: 1GB
- **Connections**: 97 max
- **Backups**: Automated daily (7-day retention)
- **Point-in-time recovery**: Included

### What You Get
- ✅ Professional managed database
- ✅ Automatic daily backups
- ✅ SSL/TLS encryption
- ✅ Connection pooling
- ✅ Monitoring dashboard
- ✅ 99.95% uptime SLA
- ✅ DDoS protection
- ✅ Automatic minor version updates

---

## 🔄 Migration Workflows

### Scenario 1: Fresh Start (New Render Database)
```bash
# 1. Deploy schema
scripts\deploy_to_render.bat

# 2. Update .env
python scripts/update_env_for_render.py

# 3. Test
scripts\test_render_connection.bat

# 4. Run dashboard
streamlit run dashboard.py
```

### Scenario 2: Migrating from Local PostgreSQL
```bash
# 1. Backup local data
scripts\backup_database.bat

# 2. Deploy schema to Render
scripts\deploy_to_render.bat

# 3. Restore data to Render
scripts\restore_to_render.bat
# Choose option 2: Data Restore Only

# 4. Update .env
python scripts/update_env_for_render.py

# 5. Test
scripts\test_render_connection.bat
```

### Scenario 3: Switching Cloud Providers
```bash
# 1. Backup from current provider
pg_dump "current-provider-url" > backups/migration.sql

# 2. Deploy schema to Render
scripts\deploy_to_render.bat

# 3. Restore data
psql "render-url" < backups/migration.sql

# 4. Update .env
python scripts/update_env_for_render.py
```

---

## 🛠️ Troubleshooting

### Issue: "relation already exists" errors during deployment
**Solution**: This is normal if you're re-running deployment. The schema uses `IF NOT EXISTS` clauses, so it's safe to ignore these warnings.

### Issue: Connection timeout
**Solutions**:
- Check your internet connection
- Verify the connection string is correct
- Check if Render database is "Available" (not "Creating")
- Try from a different network (some corporate firewalls block cloud databases)

### Issue: "permission denied" errors
**Solution**: Use the connection string from Render dashboard - it includes the correct user and credentials

### Issue: Data migration is slow (>5 minutes)
**Solution**: This is normal for large datasets. Render has good bandwidth, but:
- Large `stock_prices` tables (time-series) can take time
- Consider migrating without historical price data initially
- Run migration during off-hours

### Issue: "too many connections"
**Solution**:
- Close other applications using the database
- Check for background sync services
- Render Starter plan allows 97 connections (plenty for AVA)

---

## 🔒 Security Best Practices

### After Migration:
1. **Update .env** - Never commit with Render credentials
2. **Enable SSL** - Render forces SSL by default (good!)
3. **Rotate passwords** - Change database password in Render dashboard if needed
4. **Backup .env.backup** - Keep local backup of original .env

### In Production:
- Keep Render dashboard open in browser for monitoring
- Set up alerts in Render for high memory/CPU usage
- Review connection logs weekly
- Enable automatic backups (included in Starter plan)

---

## 📊 Monitoring & Maintenance

### Render Dashboard Features:
- **Metrics**: CPU, Memory, Storage, Connections
- **Logs**: Query logs and error logs
- **Backups**: Manual backups + automated daily
- **Restore**: Point-in-time recovery
- **Scaling**: Easy upgrade to Pro plan ($65/mo) if needed

### Regular Maintenance:
```bash
# Weekly: Check disk usage
psql "render-url" -c "SELECT pg_size_pretty(pg_database_size('trading'));"

# Monthly: Vacuum analyze (Render does this automatically)
psql "render-url" -c "VACUUM ANALYZE;"

# As needed: Manual backup
pg_dump "render-url" > backups/manual_backup_$(date +%Y%m%d).sql
```

---

## 🚀 Performance Tips

### TimescaleDB Optimization
The schema includes TimescaleDB for `stock_prices` table:
- Automatically partitions data by time
- Compression enabled after 7 days
- Retention policy: 7 years

### Indexing
All critical indexes are included:
- Symbol lookups: Instant
- Time-series queries: Optimized with hypertables
- Join queries: Foreign key indexes
- Text search: pg_trgm for fuzzy matching

### Connection Pooling
AVA uses connection pooling (see `config/default.yaml`):
```yaml
database:
  pool_min: 2
  pool_max: 10
  timeout: 30
```

No changes needed - works perfectly with Render!

---

## 🆘 Need Help?

### Resources:
- **Render Docs**: https://render.com/docs/databases
- **Render Status**: https://status.render.com
- **Support**: help@render.com (or use in-dashboard chat)

### Common Commands:
```bash
# Connect via psql
psql "your-render-connection-string"

# Check table count
psql "your-render-url" -c "SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'public';"

# List all tables
psql "your-render-url" -c "\dt"

# Check database size
psql "your-render-url" -c "SELECT pg_size_pretty(pg_database_size(current_database()));"

# Export data
pg_dump "your-render-url" > backup.sql

# Import data
psql "your-render-url" < backup.sql
```

---

## ✅ Post-Migration Checklist

After successful migration, verify:
- [ ] All 70+ tables created successfully
- [ ] Views are accessible (e.g., `v_current_positions`)
- [ ] Functions work (e.g., `calculate_position_pnl()`)
- [ ] Triggers are active (e.g., `trigger_update_position_pnl`)
- [ ] .env updated with Render credentials
- [ ] Application connects successfully to Render database
- [ ] All pages load without database errors
- [ ] Background sync services work (if applicable)
- [ ] Render dashboard shows healthy metrics

---

## 🎉 Success!

You now have:
- ✅ Professional cloud PostgreSQL ($7/month)
- ✅ Automated daily backups
- ✅ Access from anywhere
- ✅ No more manual table recreation
- ✅ 99.95% uptime guarantee

### Next Steps:
1. Start your application (frontend/backend as configured)
2. Test all features
3. Set up automatic data syncs to Render
4. Consider upgrading to Pro plan ($65/mo) if you need more storage/RAM

**Welcome to cloud-hosted AVA! 🚀**
