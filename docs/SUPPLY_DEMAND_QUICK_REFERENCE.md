# Supply/Demand Zone Detection - Quick Reference

**Status:** Architecture designed, ready for implementation
**Created:** 2025-11-09

---

## What Is This System?

Automatically detects institutional supply/demand zones (support/resistance levels) and sends Telegram alerts when prices drop into demand zones (buying opportunities) or rise into supply zones (selling opportunities).

### Key Concepts

- **Demand Zone:** Area where institutional buying overwhelms selling (strong support)
- **Supply Zone:** Area where institutional selling overwhelms buying (strong resistance)
- **Fresh Zone:** Untested zone - most powerful
- **Zone Strength:** Based on volume, rejection speed, and tightness

---

## Quick Start

### 1. Create Database Tables

```bash
# Run the schema file
psql -U postgres -d magnus -f src/supply_demand_schema.sql
```

### 2. Directory Structure

```
src/supply_demand/
├── __init__.py
├── zone_detector.py       # Detects zones from price data
├── zone_analyzer.py       # Analyzes zone quality
├── zone_db_manager.py     # Database operations
├── price_monitor.py       # Monitors price vs zones
├── alert_manager.py       # Sends Telegram alerts
└── scanner_service.py     # Scheduled orchestrator
```

### 3. Implementation Order

1. **Database Schema** ✓ (already created)
2. **ZoneDatabaseManager** - CRUD operations
3. **ZoneDetector** - Core zone detection algorithm
4. **ZoneAnalyzer** - Quality scoring and test analysis
5. **PriceMonitor** - Real-time price monitoring
6. **AlertManager** - Telegram integration
7. **ScannerService** - Scheduled automation
8. **Streamlit Dashboard** - UI for viewing zones

---

## How Zone Detection Works

### Detection Algorithm (Swing Point Method)

```
1. Find Swing Highs (potential supply zones):
   - Price makes local high
   - Higher than N candles left AND right
   - Strong down move on high volume after

2. Find Swing Lows (potential demand zones):
   - Price makes local low
   - Lower than N candles left AND right
   - Strong up move on high volume after

3. Validate Zone:
   - Zone width < 3% of price
   - Volume ratio > 1.2x (departure/approach)
   - Clear rejection visible

4. Calculate Strength (0-100):
   - Volume score (40 pts): departure vs approach volume
   - Tightness score (30 pts): narrower = stronger
   - Absolute volume (30 pts): institutional activity
```

### Zone States

```
FRESH → TESTED → WEAK → BROKEN
  ↓       ↓       ↓       ↓
  0      1-2     3+    Failed
tests   tests   tests   test
```

---

## Alert Types

### Demand Zone Alerts (Buying Opportunities)

1. **PRICE_ENTERING_DEMAND** - Price dropping into demand zone
2. **PRICE_AT_DEMAND** - Price at midpoint of demand zone
3. **ZONE_BOUNCE** - Price rejected from demand zone (wick)

### Supply Zone Alerts (Selling Opportunities)

1. **PRICE_ENTERING_SUPPLY** - Price rising into supply zone
2. **PRICE_AT_SUPPLY** - Price at midpoint of supply zone
3. **ZONE_BOUNCE** - Price rejected from supply zone (wick)

### Other Alerts

1. **ZONE_BREAK** - Zone broken through (invalidated)

---

## Configuration

### Environment Variables

Add to `.env`:

```bash
# Supply/Demand Scanner Settings
SD_ZONE_DETECTION_ENABLED=true
SD_PRICE_MONITORING_ENABLED=true
SD_MIN_ZONE_STRENGTH=40.0        # Only show zones >= 40 strength
SD_ALERT_COOLDOWN_HOURS=24       # Don't re-alert same zone for 24h
SD_SWING_LOOKBACK=5              # Candles for swing validation
SD_MAX_ZONE_WIDTH_PCT=3.0        # Max zone width as % of price
SD_VOLUME_THRESHOLD=1.2          # Min departure/approach volume ratio
```

### Scheduler Configuration

```python
# Zone detection: Daily at 4:30 PM (after market close)
scheduler.add_job(run_zone_detection, 'cron', hour=16, minute=30)

# Price monitoring: Every 15 min during market hours (9 AM - 4 PM)
scheduler.add_job(run_price_monitoring, 'cron', day_of_week='mon-fri',
                  hour='9-16', minute='*/15')

# Cleanup: Weekly on Sunday at midnight
scheduler.add_job(cleanup_old_zones, 'cron', day_of_week='sun', hour=0)
```

---

## Usage Examples

### Manual Zone Detection

```python
from src.supply_demand.zone_detector import ZoneDetector
import yfinance as yf

# Initialize detector
detector = ZoneDetector(
    swing_lookback=5,
    max_zone_width_percent=3.0,
    volume_threshold=1.2
)

# Get price data
df = yf.Ticker('AAPL').history(period='6mo', interval='1d')

# Detect zones
zones = detector.detect_zones(ticker='AAPL', df=df, timeframe='1d')

# Print results
for zone in zones:
    print(f"{zone.zone_type} zone: ${zone.zone_bottom:.2f} - ${zone.zone_top:.2f}")
    print(f"  Strength: {zone.strength_score:.0f}/100")
    print(f"  Formed: {zone.formed_date.strftime('%Y-%m-%d')}")
    print()
```

### Query Active Zones

```sql
-- Get all active demand zones for AAPL
SELECT ticker, zone_bottom, zone_top, strength_score, status, test_count
FROM sd_zones
WHERE ticker = 'AAPL'
  AND zone_type = 'DEMAND'
  AND is_active = TRUE
  AND status != 'BROKEN'
ORDER BY strength_score DESC;
```

### Check Recent Alerts

```sql
-- Get alerts from last 24 hours
SELECT a.ticker, a.alert_type, a.setup_quality, a.alert_price,
       z.zone_bottom, z.zone_top, z.strength_score
FROM sd_alerts a
JOIN sd_zones z ON a.zone_id = z.id
WHERE a.sent_at >= NOW() - INTERVAL '24 hours'
ORDER BY a.sent_at DESC;
```

### Scanner Stats

```sql
-- Get scanner performance metrics
SELECT scan_type,
       COUNT(*) as scans,
       AVG(duration_seconds) as avg_duration,
       SUM(zones_found) as zones_found,
       SUM(alerts_sent) as alerts_sent
FROM sd_scan_log
WHERE scan_timestamp >= NOW() - INTERVAL '7 days'
GROUP BY scan_type;
```

---

## Database Schema Summary

### sd_zones (Main zone storage)
- **Key fields:** ticker, zone_type, zone_top, zone_bottom, strength_score, status
- **Indexes:** ticker, status, active, strength_score

### sd_zone_tests (Test history)
- **Key fields:** zone_id, test_date, test_type, penetration_percent, held
- **Purpose:** Track each time price tests a zone

### sd_alerts (Alert log)
- **Key fields:** zone_id, ticker, alert_type, setup_quality, telegram_message_id
- **Purpose:** Prevent duplicate alerts, track alert history

### sd_scan_log (Scanner audit)
- **Key fields:** scan_type, tickers_scanned, zones_found, alerts_sent, status
- **Purpose:** Monitor scanner performance and errors

---

## Integration with Existing Code

### TradingView Watchlists

```python
# Get tickers from TradingView watchlists
from src.tradingview_db_manager import TradingViewDBManager

tv_db = TradingViewDBManager()
watchlists = tv_db.get_all_watchlists(active_only=True)

tickers = []
for watchlist in watchlists:
    symbols = tv_db.get_watchlist_symbols(watchlist['id'])
    tickers.extend([s['symbol'] for s in symbols])
```

### Telegram Alerts

```python
# Send alert using existing Telegram infrastructure
from src.telegram_notifier import TelegramNotifier

notifier = TelegramNotifier()

message = """
🟢 *BUYING OPPORTUNITY*

📈 Ticker: *AAPL*
💰 Current Price: `$170.50`

📊 Zone Details:
  • Type: `DEMAND`
  • Range: `$168.00` - `$172.00`
  • Strength: `85/100`

🎯 Setup Quality: ⭐⭐⭐ `HIGH`
"""

notifier.send_custom_message(message)
```

---

## Performance Expectations

### Zone Detection (Daily Scan)
- **100 stocks:** ~2 minutes
- **500 stocks:** ~10 minutes
- **1000 stocks:** ~20 minutes

### Price Monitoring (Every 15 min)
- **100 stocks:** <10 seconds
- **500 stocks:** ~30 seconds
- **1000 stocks:** ~60 seconds

### Database Size Estimates
- **Zones:** ~10-20 zones per stock = 1,000-2,000 records/100 stocks
- **Tests:** ~2-5 tests per zone = 5,000-10,000 records
- **Alerts:** ~1-3 alerts per day = ~1,000 records/month

---

## Testing Strategy

### Unit Tests

```python
# test_zone_detector.py
def test_swing_high_detection():
    """Test that swing highs are correctly identified."""
    # Create sample data with known swing high
    # Run detector
    # Assert swing high found at correct index

def test_supply_zone_formation():
    """Test supply zone formation from swing high."""
    # Create sample data with supply zone pattern
    # Run detector
    # Assert zone boundaries correct

def test_zone_strength_calculation():
    """Test strength score calculation."""
    # Test with high volume ratio → high score
    # Test with low volume ratio → low score
    # Test with wide zone → lower score
```

### Integration Tests

```python
# test_scanner_integration.py
def test_full_zone_detection_flow():
    """Test complete detection flow with real ticker."""
    # Download real data
    # Run detection
    # Save to database
    # Verify zones saved correctly

def test_alert_generation():
    """Test alert creation and Telegram sending."""
    # Create test zone
    # Simulate price entering zone
    # Verify alert sent
    # Check database alert log
```

---

## Troubleshooting

### No Zones Detected

**Possible causes:**
- Zone width too tight (increase `SD_MAX_ZONE_WIDTH_PCT`)
- Volume threshold too high (decrease `SD_VOLUME_THRESHOLD`)
- Not enough historical data (use 6+ months)
- Stock too volatile or illiquid

**Solution:**
```python
# Relax parameters temporarily for testing
detector = ZoneDetector(
    swing_lookback=3,           # Was: 5
    max_zone_width_percent=5.0, # Was: 3.0
    volume_threshold=1.0        # Was: 1.2
)
```

### Too Many Alerts

**Possible causes:**
- Alert cooldown too short
- Min strength too low
- Too many watchlist stocks

**Solution:**
```bash
# Increase cooldown and minimum strength
SD_ALERT_COOLDOWN_HOURS=48  # Was: 24
SD_MIN_ZONE_STRENGTH=60.0   # Was: 40.0
```

### Zone Tests Not Recording

**Check:**
1. Is price actually in zone boundaries?
2. Is penetration > threshold (30%)?
3. Database connection working?

```sql
-- Check if zones exist and are active
SELECT ticker, COUNT(*) FROM sd_zones
WHERE is_active = TRUE
GROUP BY ticker;

-- Check test logging
SELECT * FROM sd_zone_tests ORDER BY created_at DESC LIMIT 10;
```

---

## API Reference

### ZoneDetector

```python
detector = ZoneDetector(
    swing_lookback=5,           # Candles for swing validation
    min_zone_touches=2,         # Min touches to form zone
    max_zone_width_percent=3.0, # Max % width
    volume_threshold=1.2        # Min vol ratio
)

zones = detector.detect_zones(
    ticker='AAPL',
    df=price_dataframe,  # Must have OHLCV columns
    timeframe='1d',
    lookback_periods=100
)
```

### ZoneAnalyzer

```python
analyzer = ZoneAnalyzer(penetration_threshold=0.3)

# Check if price testing zone
test_info = analyzer.analyze_zone_test(
    zone=zone_object,
    current_price=170.50,
    current_candle=current_ohlc_series
)

# Calculate zone quality
quality = analyzer.calculate_zone_quality(
    zone=zone_object,
    test_history=list_of_tests,
    current_price=170.50
)
# Returns: 'HIGH', 'MEDIUM', or 'LOW'
```

### ZoneDatabaseManager

```python
db = ZoneDatabaseManager()

# Add zone
zone_id = db.add_zone(zone_dict)

# Get active zones
zones = db.get_active_zones(ticker='AAPL', zone_type='DEMAND', min_strength=50.0)

# Record test
test_id = db.add_zone_test(test_dict)

# Log alert
alert_id = db.add_alert(alert_dict)
```

---

## Next Steps

1. **Implement ZoneDatabaseManager** - Start with database operations
2. **Implement ZoneDetector** - Core algorithm with unit tests
3. **Test with real data** - Run on 5-10 tickers, validate zones manually
4. **Implement PriceMonitor** - Real-time monitoring logic
5. **Implement AlertManager** - Telegram integration
6. **Create Streamlit dashboard** - Visualize zones and alerts
7. **Deploy scanner service** - Automated scheduled scanning

---

## Resources

### Full Documentation
- `/docs/architecture/supply_demand_zones_architecture.md` - Complete design doc

### Database Schema
- `/src/supply_demand_schema.sql` - SQL schema file

### Code Structure
- `/src/supply_demand/` - Implementation directory (to be created)

### Existing Integration Points
- `/src/telegram_notifier.py` - Telegram alerts
- `/src/tradingview_db_manager.py` - Watchlist data
- `/src/xtrades_db_manager.py` - Example DB manager pattern

---

## Support

For questions or issues:
1. Review full architecture doc
2. Check database schema comments
3. Review existing DB manager implementations
4. Test with single ticker first before scaling
