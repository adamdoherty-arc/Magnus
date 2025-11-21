# Odds Validation System - Integration Guide

## Overview

The Odds Validation System provides bulletproof validation for betting odds, preventing reversed odds and other data quality issues from being displayed to users.

## System Components

1. **OddsValidator** (`src/odds_validator.py`) - Core validation engine
2. **OddsAlertSystem** (`src/odds_alert_system.py`) - Automated alerting
3. **Database Schema** (`src/odds_data_quality_schema.sql`) - Data quality tracking
4. **Dashboard** (`odds_data_quality_dashboard.py`) - Monitoring UI
5. **Unit Tests** (`tests/test_odds_validator.py`) - Comprehensive test suite

## Quick Start

### 1. Setup Database Schema

```bash
# Run the schema setup
psql -U postgres -d magnus -f src/odds_data_quality_schema.sql
```

### 2. Basic Validation

```python
from src.odds_validator import validate_kalshi_market

# Database configuration
db_config = {
    'host': 'localhost',
    'port': '5432',
    'database': 'magnus',
    'user': 'postgres',
    'password': os.getenv('DB_PASSWORD')
}

# Validate odds before displaying
is_valid, results = validate_kalshi_market(
    ticker="KXNFL-DAL-PHI-123",
    away_team="Dallas Cowboys",
    home_team="Philadelphia Eagles",
    away_win_price=0.45,
    home_win_price=0.55,
    db_config=db_config,
    away_record="7-3",
    home_record="9-1",
    last_updated=datetime.now()
)

if not is_valid:
    # CRITICAL issues detected - DO NOT DISPLAY
    print("❌ CRITICAL: Odds failed validation")
    for result in results:
        if not result.passed and result.severity == ValidationSeverity.CRITICAL:
            print(f"  - {result.message}")
else:
    # Safe to display
    print("✅ Odds validated successfully")
```

### 3. Integration with Kalshi Sync

Modify `src/espn_kalshi_matcher.py` to include validation:

```python
from src.odds_validator import validate_kalshi_market
from src.odds_alert_system import send_odds_alert, AlertChannel

def enrich_games_with_kalshi_odds(espn_games: List[Dict]) -> List[Dict]:
    """Enrich ESPN games with VALIDATED Kalshi odds"""
    matcher = ESPNKalshiMatcher()
    enriched_games = matcher.enrich_espn_games_with_kalshi(espn_games)

    # Database config
    db_config = {
        'host': 'localhost',
        'port': '5432',
        'database': 'magnus',
        'user': 'postgres',
        'password': os.getenv('DB_PASSWORD')
    }

    # Alert channels
    alert_channels = [
        AlertChannel(name='console', enabled=True, config={})
    ]

    # Validate each game's odds
    for game in enriched_games:
        kalshi_odds = game.get('kalshi_odds')

        if not kalshi_odds:
            continue

        # Validate odds
        is_valid, results = validate_kalshi_market(
            ticker=kalshi_odds.get('ticker'),
            away_team=game['away_team'],
            home_team=game['home_team'],
            away_win_price=kalshi_odds['away_win_price'],
            home_win_price=kalshi_odds['home_win_price'],
            db_config=db_config,
            away_record=game.get('away_record'),
            home_record=game.get('home_record')
        )

        # Store validation flag
        game['odds_validated'] = is_valid

        # Send alerts for failures
        if not is_valid:
            send_odds_alert(
                ticker=kalshi_odds.get('ticker'),
                away_team=game['away_team'],
                home_team=game['home_team'],
                away_win_price=kalshi_odds['away_win_price'],
                home_win_price=kalshi_odds['home_win_price'],
                validation_results=results,
                db_config=db_config,
                alert_channels=alert_channels
            )

    return enriched_games
```

### 4. Update Game Card Display

Modify `game_cards_visual_page.py` to check validation:

```python
def render_game_card(game):
    """Render game card with validation check"""

    # Check if odds are validated
    odds_validated = game.get('odds_validated', False)
    kalshi_odds = game.get('kalshi_odds')

    if kalshi_odds and not odds_validated:
        # CRITICAL: Do not display unvalidated odds
        st.warning("⚠️ Odds data quality issue detected - using AI predictions only")
        kalshi_odds = None  # Clear invalid odds

    # Continue with rendering...
    if kalshi_odds:
        away_odds = kalshi_odds['away_win_price'] * 100
        home_odds = kalshi_odds['home_win_price'] * 100
        # Display odds...
```

## Validation Rules

### 1. Odds Range Validation (CRITICAL)
- **Rule**: All odds must be between 1% and 99%
- **Severity**: CRITICAL
- **Action**: Block display if failed

### 2. Probability Sum Validation (CRITICAL)
- **Rule**: away_price + home_price should be ~1.0 (0.95 - 1.05)
- **Severity**: CRITICAL (if < 0.95), WARNING (if > 1.05)
- **Action**: Block if critical, flag if warning

### 3. Team Record Correlation (CRITICAL)
- **Rule**: Team with better record must have higher win probability
- **Severity**: CRITICAL
- **Action**: Block display if failed
- **Example**:
  - ✅ VALID: 9-1 team @ 65%, 3-7 team @ 35%
  - ❌ INVALID: 9-1 team @ 35%, 3-7 team @ 65% (REVERSED!)

### 4. Home Field Advantage (WARNING)
- **Rule**: For evenly matched teams, home team should have 2-15% advantage
- **Severity**: WARNING
- **Action**: Flag for review

### 5. Historical Performance (WARNING)
- **Rule**: Current odds should align with historical head-to-head results
- **Severity**: WARNING
- **Action**: Flag if deviation > 20%

### 6. Data Freshness (WARNING)
- **Rule**: Odds should be updated within last 24 hours
- **Severity**: WARNING
- **Action**: Flag stale data

### 7. Upset Detection (INFO)
- **Rule**: Detect when underdog has better record (potential value)
- **Severity**: INFO
- **Action**: Informational only

## Alert System Configuration

### Email Alerts

```python
from src.odds_alert_system import AlertChannel

email_channel = AlertChannel(
    name='email',
    enabled=True,
    config={
        'smtp_host': 'smtp.gmail.com',
        'smtp_port': 587,
        'smtp_user': 'your@email.com',
        'smtp_password': 'your_app_password',
        'from_email': 'alerts@trading.com',
        'to_emails': ['admin@trading.com', 'dev@trading.com']
    }
)
```

### Slack Alerts

```python
slack_channel = AlertChannel(
    name='slack',
    enabled=True,
    config={
        'webhook_url': 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
    }
)
```

### Console Alerts (Development)

```python
console_channel = AlertChannel(
    name='console',
    enabled=True,
    config={}
)
```

## Data Quality Dashboard

Run the monitoring dashboard:

```bash
streamlit run odds_data_quality_dashboard.py
```

Dashboard features:
- **Overview Tab**: Quality scores, failure counts, breakdown by rule type
- **Active Alerts Tab**: Real-time anomaly alerts with acknowledgment workflow
- **Trends Tab**: Quality trends over time, failure rate charts
- **By Rule Type Tab**: Detailed statistics for each validation rule
- **Critical Failures Tab**: Recent critical validation failures

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest tests/test_odds_validator.py -v

# Run specific test class
pytest tests/test_odds_validator.py::TestRecordCorrelationValidation -v

# Run with coverage
pytest tests/test_odds_validator.py --cov=src.odds_validator --cov-report=html
```

## Database Queries

### Get Recent Critical Failures

```sql
SELECT * FROM v_odds_critical_failures LIMIT 10;
```

### Get Active Alerts

```sql
SELECT * FROM v_odds_active_alerts;
```

### Get Quality Trends

```sql
SELECT * FROM v_odds_quality_trends LIMIT 30;
```

### Aggregate Daily Metrics

```sql
SELECT aggregate_daily_odds_metrics(CURRENT_DATE);
```

### Create Manual Alert

```sql
SELECT create_odds_anomaly_alert(
    'KXNFL-DAL-PHI',
    'reversed_odds',
    'critical',
    'Reversed Odds Detected',
    'Better team showing lower win probability',
    'Dallas Cowboys',
    'Philadelphia Eagles',
    0.35,
    0.65,
    '{"away_record": "9-1", "home_record": "3-7"}'::jsonb
);
```

## Metrics and Monitoring

### Key Metrics

1. **Quality Score**: Percentage of validations passed (target: 99%+)
2. **Critical Failure Rate**: Percentage of CRITICAL failures (target: 0%)
3. **Warning Rate**: Percentage of warnings (target: <5%)
4. **Average Validation Time**: Time to validate a game (target: <50ms)

### Alerts to Monitor

- **Critical Alert**: Reversed odds detected
- **Critical Alert**: Invalid probability sum (<95%)
- **Warning Alert**: Missing home field advantage
- **Warning Alert**: Stale data (>24h old)
- **Warning Alert**: Historical performance mismatch

## Best Practices

### DO:
✅ Always validate odds before displaying to users
✅ Block display for CRITICAL validation failures
✅ Log all validation results for analysis
✅ Set up automated alerts for critical issues
✅ Review warnings regularly (may indicate data source issues)
✅ Run daily metric aggregation
✅ Monitor quality score trends

### DON'T:
❌ Display odds that failed CRITICAL validation
❌ Ignore validation warnings (investigate patterns)
❌ Skip validation for "trusted" data sources
❌ Disable validation rules without analysis
❌ Forget to update thresholds based on real-world data

## Troubleshooting

### Issue: High False Positive Rate

**Solution**: Adjust validation thresholds in database:

```sql
UPDATE odds_validation_rules_config
SET parameters = '{"win_pct_threshold": 0.15}'::jsonb
WHERE rule_type = 'team_record_correlation';
```

### Issue: Validation Too Slow

**Solution**:
1. Add database indexes
2. Reduce historical lookback period
3. Implement caching for team records

### Issue: Missing Historical Data

**Solution**:
- Historical validation automatically skips when insufficient data
- Populate historical data by running Kalshi sync for past games

## Support and Maintenance

### Weekly Tasks
- Review active alerts and resolve
- Check quality score trends
- Analyze validation failure patterns

### Monthly Tasks
- Review and adjust validation thresholds
- Analyze false positive rate
- Update rule configurations based on data

### Quarterly Tasks
- Performance optimization review
- Add new validation rules if needed
- Update documentation

## Contact

For questions or issues:
- Check logs in `odds_data_quality_log` table
- Review dashboard at `/odds_data_quality_dashboard`
- Run test suite to verify functionality

---

**Version**: 1.0
**Last Updated**: 2025-11-18
**Status**: Production Ready
