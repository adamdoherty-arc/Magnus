# Xtrades.net Scraper Documentation

## Overview

The Xtrades.net scraper is a comprehensive Python module that automates the extraction of trading alerts from Xtrades.net profile pages using Discord OAuth authentication.

**Key Features:**
- Discord OAuth login automation
- Profile scraping from `https://app.xtrades.net/profile/{username}`
- Advanced alert parsing for multiple strategy types
- Session persistence with cookie caching
- Anti-detection measures
- Exponential backoff retry logic
- PostgreSQL database integration
- Comprehensive error handling

## Table of Contents

1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Quick Start](#quick-start)
4. [Architecture](#architecture)
5. [API Reference](#api-reference)
6. [Alert Parsing](#alert-parsing)
7. [Database Schema](#database-schema)
8. [Usage Examples](#usage-examples)
9. [Testing](#testing)
10. [Known Issues](#known-issues)
11. [Troubleshooting](#troubleshooting)

---

## Installation

### Prerequisites

- Python 3.8+
- PostgreSQL 12+ (for database integration)
- Google Chrome browser
- ChromeDriver (managed automatically by undetected-chromedriver)

### Dependencies

All required packages are in `requirements.txt`:

```bash
selenium==4.16.0
beautifulsoup4==4.12.2
undetected-chromedriver==3.5.4
python-dotenv==1.0.0
psycopg2-binary==2.9.9
requests==2.31.0
```

### Installation Steps

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Setup database schema:**
```bash
psql -U postgres -d magnus -f src/xtrades_schema.sql
```

3. **Configure environment:**
```bash
# Add to .env file
XTRADES_USERNAME=your_discord_username
XTRADES_PASSWORD=your_discord_password
```

---

## Configuration

### Environment Variables

Required variables in `.env`:

```bash
# Xtrades.net Login (Discord OAuth)
XTRADES_USERNAME=sureadam
XTRADES_PASSWORD=your_password

# Database (optional - for persistence)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=magnus
DB_USER=postgres
DB_PASSWORD=your_db_password

# Telegram (optional - for notifications)
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
TELEGRAM_ENABLED=false
```

### Chrome Options

The scraper uses the following Chrome options for anti-detection:

```python
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
```

---

## Quick Start

### Basic Usage

```python
from xtrades_scraper import XtradesScraper

# Initialize scraper
scraper = XtradesScraper()

try:
    # Login
    scraper.login()

    # Scrape profile
    alerts = scraper.get_profile_alerts("behappy", max_alerts=10)

    # Process alerts
    for alert in alerts:
        print(f"{alert['ticker']}: {alert['strategy']} - ${alert['entry_price']}")

finally:
    scraper.close()
```

### Convenience Function

```python
from xtrades_scraper import scrape_profile

# One-liner to scrape a profile
alerts = scrape_profile("behappy", max_alerts=20)
```

---

## Architecture

### Class Structure

```
XtradesScraper
├── __init__()           # Initialize with credentials
├── login()              # Discord OAuth flow
├── get_profile_alerts() # Scrape profile page
├── parse_alert()        # Parse individual alert
└── close()              # Cleanup
```

### Login Flow

```
1. Navigate to app.xtrades.net/login
2. Click "Sign in with Discord" button
3. Enter Discord credentials
4. Authorize Xtrades application
5. Redirect back to Xtrades
6. Save session cookies
```

### Scraping Flow

```
1. Navigate to profile/{username}
2. Check for 404/not found
3. Scroll page to load dynamic content
4. Extract alert elements
5. Parse each alert
6. Return structured data
```

---

## API Reference

### XtradesScraper Class

#### `__init__(headless: bool = False, cache_dir: Optional[str] = None)`

Initialize the scraper.

**Parameters:**
- `headless` (bool): Run browser in headless mode (default: False)
- `cache_dir` (str): Directory for cookie cache (default: ~/.xtrades_cache)

**Raises:**
- `ValueError`: If XTRADES_USERNAME or XTRADES_PASSWORD not set

**Example:**
```python
scraper = XtradesScraper(headless=True, cache_dir='/tmp/xtrades')
```

---

#### `login(retry_count: int = 3) -> bool`

Login to Xtrades.net via Discord OAuth.

**Parameters:**
- `retry_count` (int): Number of retry attempts (default: 3)

**Returns:**
- `bool`: True if login successful

**Raises:**
- `LoginFailedException`: If login fails after all retries

**Example:**
```python
try:
    scraper.login(retry_count=5)
except LoginFailedException as e:
    print(f"Failed to login: {e}")
```

---

#### `get_profile_alerts(username: str, max_alerts: Optional[int] = None) -> List[Dict]`

Scrape alerts from a profile page.

**Parameters:**
- `username` (str): Xtrades.net username
- `max_alerts` (int): Maximum alerts to retrieve (None = all)

**Returns:**
- `List[Dict]`: List of parsed alert dictionaries

**Raises:**
- `ProfileNotFoundException`: If profile doesn't exist
- `XtradesScraperException`: For other errors

**Example:**
```python
alerts = scraper.get_profile_alerts("behappy", max_alerts=50)
```

---

#### `parse_alert(alert_element) -> Optional[Dict]`

Parse individual alert into structured data.

**Parameters:**
- `alert_element`: BeautifulSoup element or HTML string

**Returns:**
- `Dict`: Parsed alert data or None if parsing fails

**Alert Dictionary Structure:**
```python
{
    'ticker': 'AAPL',
    'strategy': 'CSP',
    'action': 'STO',
    'entry_price': 2.50,
    'exit_price': None,
    'quantity': 1,
    'strike_price': 170.0,
    'expiration_date': '2024-12-15',
    'pnl': None,
    'pnl_percent': None,
    'status': 'open',
    'alert_text': 'AAPL CSP: STO 1x $170 PUT @ $2.50 exp 12/15/2024',
    'alert_timestamp': '2024-11-02T12:00:00',
    'profile_username': 'behappy'
}
```

---

#### `close() -> None`

Close browser and cleanup resources.

**Example:**
```python
scraper.close()
```

---

### Convenience Functions

#### `scrape_profile(username: str, max_alerts: Optional[int] = None) -> List[Dict]`

One-liner to scrape a profile (handles login and cleanup).

**Example:**
```python
from xtrades_scraper import scrape_profile

alerts = scrape_profile("behappy", max_alerts=10)
```

---

## Alert Parsing

### Supported Strategies

The parser recognizes these strategy types:

| Strategy | Patterns | Example |
|----------|----------|---------|
| CSP | `CSP`, `Cash-Secured-Put` | "AAPL CSP: STO $170 PUT" |
| CC | `CC`, `Covered-Call` | "AAPL CC: STO $180 Call" |
| Long Call | `Long Call`, `LC` | "BTO AAPL $170 Call" |
| Long Put | `Long Put`, `LP` | "BTO AAPL $170 Put" |
| Put Credit Spread | `PCS`, `Put Credit Spread` | "SPY PCS: 450/445" |
| Call Credit Spread | `CCS`, `Call Credit Spread` | "SPY CCS: 455/460" |
| Iron Condor | `IC`, `Iron Condor` | "SPY IC: 450/455/445/440" |
| Butterfly | `BF`, `Butterfly` | "SPY Butterfly" |
| Straddle | `Straddle` | "AAPL Straddle $170" |
| Strangle | `Strangle` | "AAPL Strangle 170/180" |

### Supported Actions

| Action | Meaning | Patterns |
|--------|---------|----------|
| BTO | Buy To Open | `\bBTO\b`, `opened`, `opening` |
| STO | Sell To Open | `\bSTO\b` |
| BTC | Buy To Close | `\bBTC\b` |
| STC | Sell To Close | `\bSTC\b`, `closed`, `closing` |

### Alert Format Examples

**Cash-Secured Put (Opening):**
```
AAPL CSP: STO 1x $170 PUT @ $2.50 exp 12/15/2024
```
Parsed:
- Ticker: AAPL
- Strategy: CSP
- Action: STO
- Quantity: 1
- Strike: $170
- Entry Price: $2.50
- Expiration: 2024-12-15

**Covered Call (Closing):**
```
TSLA CC: STC @ $1.25 - +150% gain, collected $3.00 premium originally
```
Parsed:
- Ticker: TSLA
- Strategy: CC
- Action: STC
- Exit Price: $1.25
- P&L %: +150%
- Status: closed

**Put Credit Spread:**
```
SPY Put Credit Spread: 450/445 for $1.25 credit exp 11/30
```
Parsed:
- Ticker: SPY
- Strategy: Put Credit Spread
- Entry Price: $1.25
- Expiration: 11/30

---

## Database Schema

### Tables

#### 1. `xtrades_profiles`

Stores monitored profiles.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| username | VARCHAR(255) | Xtrades username (unique) |
| display_name | VARCHAR(255) | Display name |
| active | BOOLEAN | Whether actively monitored |
| added_date | TIMESTAMP | When profile was added |
| last_sync | TIMESTAMP | Last successful sync |
| last_sync_status | VARCHAR(50) | 'success', 'error', 'pending' |
| total_trades_scraped | INTEGER | Running count of trades |
| notes | TEXT | Notes about profile |

#### 2. `xtrades_trades`

Stores individual trades.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| profile_id | INTEGER | FK to xtrades_profiles |
| ticker | VARCHAR(20) | Stock ticker |
| strategy | VARCHAR(100) | Strategy type |
| action | VARCHAR(20) | Trade action |
| entry_price | DECIMAL(10,2) | Entry price |
| exit_price | DECIMAL(10,2) | Exit price |
| quantity | INTEGER | Number of contracts |
| strike_price | DECIMAL(10,2) | Option strike |
| expiration_date | DATE | Option expiration |
| pnl | DECIMAL(10,2) | Profit/Loss ($) |
| pnl_percent | DECIMAL(10,2) | Profit/Loss (%) |
| status | VARCHAR(20) | 'open', 'closed', 'expired' |
| alert_text | TEXT | Full alert text |
| alert_timestamp | TIMESTAMP | When alert was posted |
| scraped_at | TIMESTAMP | When scraped |
| xtrades_alert_id | VARCHAR(255) | Unique alert ID |

#### 3. `xtrades_sync_log`

Tracks synchronization history.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| sync_timestamp | TIMESTAMP | Sync time |
| profiles_synced | INTEGER | Profiles processed |
| trades_found | INTEGER | Trades discovered |
| new_trades | INTEGER | New trades added |
| updated_trades | INTEGER | Trades updated |
| errors | TEXT | Error messages |
| duration_seconds | DECIMAL(10,2) | Sync duration |
| status | VARCHAR(50) | 'success', 'partial', 'failed' |

#### 4. `xtrades_notifications`

Tracks sent notifications.

| Column | Type | Description |
|--------|------|-------------|
| id | SERIAL | Primary key |
| trade_id | INTEGER | FK to xtrades_trades |
| notification_type | VARCHAR(50) | Type of notification |
| sent_at | TIMESTAMP | When sent |
| telegram_message_id | VARCHAR(255) | Telegram message ID |
| status | VARCHAR(20) | 'sent', 'failed' |
| error_message | TEXT | Error message if failed |

---

## Usage Examples

See `src/xtrades_usage_example.py` for detailed examples:

1. **Basic Scraping** - Simple profile scraping
2. **Database Integration** - Store alerts in PostgreSQL
3. **Batch Processing** - Scrape multiple profiles
4. **Error Handling** - Robust retry logic
5. **Telegram Integration** - Send alerts to Telegram
6. **Scheduled Scraping** - Automated periodic scraping

---

## Testing

### Run All Tests

```bash
pytest tests/test_xtrades_scraper.py -v
```

### Run Specific Test Categories

```bash
# Alert parsing tests
pytest tests/test_xtrades_scraper.py::TestAlertParsing -v

# Login flow tests
pytest tests/test_xtrades_scraper.py::TestLoginFlow -v

# Profile scraping tests
pytest tests/test_xtrades_scraper.py::TestProfileScraping -v
```

### Run Integration Tests

```bash
# Requires actual browser and network
pytest tests/test_xtrades_scraper.py -v -m integration
```

### Test Coverage

```bash
pytest tests/test_xtrades_scraper.py --cov=xtrades_scraper --cov-report=html
```

---

## Known Issues

### 1. Discord OAuth CAPTCHA

**Issue:** Discord may present CAPTCHA during login, especially for new IPs.

**Workaround:**
- Run in non-headless mode first time
- Complete CAPTCHA manually
- Session cookies will be saved for future use

**Solution:**
```python
scraper = XtradesScraper(headless=False)  # Allow manual intervention
scraper.login()
```

### 2. Session Expiration

**Issue:** Saved session cookies expire after ~7 days.

**Workaround:**
- Implement periodic re-login
- Check `_is_logged_in()` before each scrape

**Solution:**
```python
if not scraper._is_logged_in():
    scraper.login()
```

### 3. Rate Limiting

**Issue:** Xtrades.net may rate limit aggressive scraping.

**Workaround:**
- Add delays between requests
- Limit scraping frequency
- Use exponential backoff

**Solution:**
```python
import time
for username in profiles:
    alerts = scraper.get_profile_alerts(username)
    time.sleep(5)  # 5 second delay between profiles
```

### 4. Dynamic Content Loading

**Issue:** Some alerts may load dynamically via JavaScript.

**Workaround:**
- Increase scroll pause time
- Increase number of scrolls
- Wait for specific elements

**Solution:**
```python
scraper._scroll_page(scroll_pause=2.0, num_scrolls=5)
```

### 5. Alert Format Variations

**Issue:** Users may post alerts in various formats.

**Workaround:**
- Parse regex patterns are broad
- Multiple pattern matching
- Fallback to raw text

**Limitation:**
Some non-standard formats may not parse completely. Always check `alert_text` field for raw data.

---

## Troubleshooting

### Login Fails

**Problem:** `LoginFailedException` raised

**Debug Steps:**
1. Check credentials in `.env`
2. Run in non-headless mode: `XtradesScraper(headless=False)`
3. Check for CAPTCHA
4. Verify Discord account status
5. Clear cookie cache: `rm ~/.xtrades_cache/cookies.pkl`

### Profile Not Found

**Problem:** `ProfileNotFoundException` raised

**Debug Steps:**
1. Verify username spelling
2. Check profile exists: `https://app.xtrades.net/profile/{username}`
3. Check if profile is public
4. Verify login session is valid

### No Alerts Found

**Problem:** `get_profile_alerts()` returns empty list

**Debug Steps:**
1. Verify profile has alerts
2. Increase scroll count: `scraper._scroll_page(num_scrolls=10)`
3. Check page source: `print(scraper.driver.page_source)`
4. Update alert selectors if page structure changed

### Parsing Issues

**Problem:** Alert data incomplete or incorrect

**Debug Steps:**
1. Check raw alert text: `print(alert['alert_text'])`
2. Test regex patterns manually
3. Update patterns in `STRATEGY_PATTERNS` or `ACTION_PATTERNS`
4. Submit issue with alert example

### ChromeDriver Errors

**Problem:** ChromeDriver crashes or fails to start

**Debug Steps:**
1. Update Chrome browser
2. Clear driver cache: `rm -rf ~/.undetected_chromedriver`
3. Install specific ChromeDriver version
4. Check Chrome process isn't already running

---

## Performance Considerations

### Memory Usage

- Each browser instance uses ~200-300MB RAM
- Consider closing after each scrape if running multiple instances
- Use headless mode to reduce memory

### Speed

- Login: ~10-15 seconds
- Profile scrape: ~5-10 seconds
- Alert parsing: ~0.1 seconds per alert

### Optimization Tips

1. **Reuse sessions:**
```python
scraper = XtradesScraper()
scraper.login()  # Login once

for username in profiles:
    alerts = scraper.get_profile_alerts(username)
    # Process alerts

scraper.close()  # Close once at end
```

2. **Parallel scraping:**
```python
from concurrent.futures import ThreadPoolExecutor

def scrape_user(username):
    return scrape_profile(username)

with ThreadPoolExecutor(max_workers=3) as executor:
    results = executor.map(scrape_user, usernames)
```

3. **Database batching:**
```python
cursor.executemany(insert_query, alerts)
```

---

## Security Considerations

### Credential Storage

- Never commit `.env` file to version control
- Use environment variables or secret management
- Rotate credentials periodically

### Session Management

- Cookie files contain authentication data
- Protect `~/.xtrades_cache/cookies.pkl`
- Set appropriate file permissions: `chmod 600`

### Rate Limiting

- Respect Xtrades.net terms of service
- Don't scrape aggressively
- Implement backoff on errors

---

## Future Enhancements

### Planned Features

1. **WebSocket Integration**
   - Real-time alert monitoring
   - Instant notifications

2. **ML-Based Parsing**
   - Better pattern recognition
   - Handle format variations

3. **Multi-Profile Dashboard**
   - Compare performance across traders
   - Aggregate statistics

4. **Alert Backtesting**
   - Historical performance analysis
   - Strategy evaluation

5. **API Wrapper**
   - REST API for alerts
   - Webhook notifications

---

## Contributing

### Report Issues

Found a bug or have a feature request? Please create an issue with:

1. Description of problem
2. Steps to reproduce
3. Expected vs actual behavior
4. Alert text examples (for parsing issues)
5. Error logs

### Submit Pull Requests

1. Fork the repository
2. Create feature branch
3. Write tests for new features
4. Ensure all tests pass
5. Submit PR with description

---

## License

Part of the Magnus Wheel Strategy Trading Dashboard.

---

## Support

For questions or issues:
- Create GitHub issue
- Check troubleshooting section
- Review usage examples

---

## Changelog

### Version 1.0.0 (2024-11-02)

**Initial Release:**
- Discord OAuth login
- Profile scraping
- Alert parsing for 10+ strategies
- PostgreSQL integration
- Cookie session management
- Anti-detection measures
- Comprehensive tests
- Usage examples

---

## Acknowledgments

Built with:
- Selenium WebDriver
- Undetected ChromeDriver
- BeautifulSoup4
- PostgreSQL
- Python 3.8+

---

**Last Updated:** November 2, 2024
**Version:** 1.0.0
