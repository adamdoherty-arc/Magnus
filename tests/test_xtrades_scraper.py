"""
Unit Tests for Xtrades.net Scraper
===================================
Tests for Discord OAuth login and trade alert parsing functionality.

Run with: pytest tests/test_xtrades_scraper.py -v
"""

import os
import sys
import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path
from datetime import datetime, date

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from xtrades_scraper import (
    XtradesScraper,
    XtradesScraperException,
    LoginFailedException,
    ProfileNotFoundException,
    scrape_profile
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Mock environment variables"""
    monkeypatch.setenv('XTRADES_USERNAME', 'test_user')
    monkeypatch.setenv('XTRADES_PASSWORD', 'test_pass')


@pytest.fixture
def mock_driver():
    """Mock Selenium WebDriver"""
    driver = MagicMock()
    driver.get = MagicMock()
    driver.find_element = MagicMock()
    driver.get_cookies = MagicMock(return_value=[])
    driver.add_cookie = MagicMock()
    driver.current_url = "https://app.xtrades.net"
    driver.page_source = "<html><body>Test content</body></html>"
    driver.title = "Xtrades"
    return driver


@pytest.fixture
def scraper_instance(mock_env_vars):
    """Create scraper instance with mocked driver"""
    with patch('xtrades_scraper.uc.Chrome') as mock_chrome:
        mock_driver_instance = MagicMock()
        mock_chrome.return_value = mock_driver_instance

        scraper = XtradesScraper()
        scraper.driver = mock_driver_instance
        yield scraper


# ============================================================================
# Initialization Tests
# ============================================================================

def test_init_missing_credentials():
    """Test initialization without credentials"""
    with pytest.raises(ValueError, match="XTRADES_USERNAME and XTRADES_PASSWORD"):
        XtradesScraper()


def test_init_with_credentials(mock_env_vars):
    """Test successful initialization"""
    with patch('xtrades_scraper.uc.Chrome'):
        scraper = XtradesScraper()
        assert scraper.username == 'test_user'
        assert scraper.password == 'test_pass'
        assert scraper.BASE_URL == "https://app.xtrades.net"


def test_init_cache_directory(mock_env_vars, tmp_path):
    """Test cache directory creation"""
    with patch('xtrades_scraper.uc.Chrome'):
        cache_dir = tmp_path / 'test_cache'
        scraper = XtradesScraper(cache_dir=str(cache_dir))
        assert scraper.cache_dir.exists()
        assert scraper.cookies_file == cache_dir / 'cookies.pkl'


# ============================================================================
# Alert Parsing Tests
# ============================================================================

class TestAlertParsing:
    """Test suite for alert parsing functionality"""

    def test_parse_csp_alert(self, scraper_instance):
        """Test parsing Cash-Secured Put alert"""
        alert_text = "AAPL CSP: STO 1x $170 PUT @ $2.50 exp 12/15/2024"

        result = scraper_instance.parse_alert(alert_text)

        assert result is not None
        assert result['ticker'] == 'AAPL'
        assert result['strategy'] == 'CSP'
        assert result['action'] == 'STO'
        assert result['entry_price'] == 2.50
        assert result['strike_price'] == 170.0
        assert result['quantity'] == 1
        assert result['expiration_date'] == '2024-12-15'
        assert result['status'] == 'open'

    def test_parse_closed_trade(self, scraper_instance):
        """Test parsing closed trade with P&L"""
        alert_text = "TSLA CSP: STC @ $2.50 - +120% gain, collected $3.50 premium"

        result = scraper_instance.parse_alert(alert_text)

        assert result is not None
        assert result['ticker'] == 'TSLA'
        assert result['action'] == 'STC'
        assert result['status'] == 'closed'
        assert result['pnl_percent'] == 120.0

    def test_parse_covered_call(self, scraper_instance):
        """Test parsing Covered Call"""
        alert_text = "MSFT CC: Sold $350 call @ $4.00, expires 11/30"

        result = scraper_instance.parse_alert(alert_text)

        assert result is not None
        assert result['ticker'] == 'MSFT'
        assert result['strategy'] == 'CC'
        assert result['strike_price'] == 350.0
        assert result['entry_price'] == 4.00

    def test_parse_long_call(self, scraper_instance):
        """Test parsing Long Call"""
        alert_text = "BTO NVDA $500 Call @ $12.50 exp 12/20"

        result = scraper_instance.parse_alert(alert_text)

        assert result is not None
        assert result['ticker'] == 'NVDA'
        assert result['action'] == 'BTO'
        assert result['strike_price'] == 500.0
        assert result['entry_price'] == 12.50

    def test_parse_spread(self, scraper_instance):
        """Test parsing credit spread"""
        alert_text = "SPY Put Credit Spread: 450/445 for $1.25 credit"

        result = scraper_instance.parse_alert(alert_text)

        assert result is not None
        assert result['ticker'] == 'SPY'
        assert result['strategy'] == 'Put Credit Spread'
        assert result['entry_price'] == 1.25

    def test_parse_multiple_contracts(self, scraper_instance):
        """Test parsing trade with multiple contracts"""
        alert_text = "AMD CSP: STO 5x $100 Put @ $2.00"

        result = scraper_instance.parse_alert(alert_text)

        assert result is not None
        assert result['ticker'] == 'AMD'
        assert result['quantity'] == 5
        assert result['entry_price'] == 2.00

    def test_parse_with_pnl_dollar(self, scraper_instance):
        """Test parsing with dollar P&L"""
        alert_text = "AAPL: Closed for +$500 profit"

        result = scraper_instance.parse_alert(alert_text)

        assert result is not None
        assert result['ticker'] == 'AAPL'
        assert result['pnl'] == 500.0
        assert result['status'] == 'closed'

    def test_parse_with_negative_pnl(self, scraper_instance):
        """Test parsing with loss"""
        alert_text = "TSLA: Closed for -$200 loss, -40%"

        result = scraper_instance.parse_alert(alert_text)

        assert result is not None
        assert result['ticker'] == 'TSLA'
        assert result['pnl'] == -200.0
        assert result['pnl_percent'] == -40.0

    def test_parse_expired_trade(self, scraper_instance):
        """Test parsing expired option"""
        alert_text = "AAPL $170 PUT expired worthless - kept full premium"

        result = scraper_instance.parse_alert(alert_text)

        assert result is not None
        assert result['ticker'] == 'AAPL'
        assert result['status'] == 'expired'

    def test_parse_invalid_alert(self, scraper_instance):
        """Test parsing invalid/empty alert"""
        result = scraper_instance.parse_alert("")
        assert result is None

        result = scraper_instance.parse_alert("Invalid text no ticker")
        assert result is None

    def test_parse_date_formats(self, scraper_instance):
        """Test various date format parsing"""
        test_cases = [
            ("12/15/2024", "2024-12-15"),
            ("12/15/24", "2024-12-15"),
            ("12/15", f"{datetime.now().year}-12-15"),
            ("12-15-2024", "2024-12-15"),
        ]

        for date_str, expected in test_cases:
            result = scraper_instance._parse_date(date_str)
            if expected:
                assert result == expected

    def test_parse_iron_condor(self, scraper_instance):
        """Test parsing Iron Condor"""
        alert_text = "SPY Iron Condor: 450/455/445/440 for $2.00 credit"

        result = scraper_instance.parse_alert(alert_text)

        assert result is not None
        assert result['ticker'] == 'SPY'
        assert result['strategy'] == 'Iron Condor'

    def test_parse_straddle(self, scraper_instance):
        """Test parsing Straddle"""
        alert_text = "AAPL Straddle: $170 strike for $8.50 debit"

        result = scraper_instance.parse_alert(alert_text)

        assert result is not None
        assert result['ticker'] == 'AAPL'
        assert result['strategy'] == 'Straddle'
        assert result['strike_price'] == 170.0


# ============================================================================
# Login Flow Tests
# ============================================================================

class TestLoginFlow:
    """Test suite for login functionality"""

    def test_is_logged_in_true(self, scraper_instance):
        """Test logged in state detection"""
        # Mock finding profile element
        scraper_instance.driver.find_element.return_value = MagicMock()
        scraper_instance.driver.get = MagicMock()
        scraper_instance.driver.current_url = "https://app.xtrades.net/dashboard"

        result = scraper_instance._is_logged_in()
        assert result is True

    def test_is_logged_in_false(self, scraper_instance):
        """Test not logged in state detection"""
        # Mock element not found
        from selenium.common.exceptions import NoSuchElementException
        scraper_instance.driver.find_element.side_effect = NoSuchElementException()
        scraper_instance.driver.current_url = "https://app.xtrades.net/login"

        result = scraper_instance._is_logged_in()
        assert result is False

    @patch('xtrades_scraper.pickle')
    def test_save_cookies(self, mock_pickle, scraper_instance, tmp_path):
        """Test cookie saving"""
        scraper_instance.cookies_file = tmp_path / 'cookies.pkl'
        scraper_instance.driver.get_cookies.return_value = [
            {'name': 'session', 'value': 'abc123'}
        ]

        scraper_instance._save_cookies()

        # Verify pickle.dump was called
        assert mock_pickle.dump.called

    @patch('xtrades_scraper.pickle')
    def test_load_cookies(self, mock_pickle, scraper_instance, tmp_path):
        """Test cookie loading"""
        # Create fake cookie file
        cookie_file = tmp_path / 'cookies.pkl'
        cookie_file.touch()
        scraper_instance.cookies_file = cookie_file

        mock_pickle.load.return_value = [
            {'name': 'session', 'value': 'abc123'}
        ]

        with patch('builtins.open', create=True):
            result = scraper_instance._load_cookies()

        # Should attempt to add cookies
        assert scraper_instance.driver.get.called


# ============================================================================
# Profile Scraping Tests
# ============================================================================

class TestProfileScraping:
    """Test suite for profile scraping"""

    def test_profile_not_found(self, scraper_instance):
        """Test handling of non-existent profile"""
        scraper_instance.driver.title = "404 Not Found"

        with pytest.raises(ProfileNotFoundException):
            scraper_instance.get_profile_alerts("nonexistent_user")

    @patch('xtrades_scraper.BeautifulSoup')
    def test_get_profile_alerts_success(self, mock_soup, scraper_instance):
        """Test successful profile scraping"""
        # Mock HTML content
        mock_alert = MagicMock()
        mock_alert.get_text.return_value = "AAPL CSP: STO 1x $170 PUT @ $2.50"

        mock_soup.return_value.find_all.return_value = [mock_alert]

        scraper_instance.driver.title = "Xtrades Profile"
        scraper_instance.driver.page_source = "<html><body>alerts</body></html>"

        alerts = scraper_instance.get_profile_alerts("testuser")

        assert isinstance(alerts, list)
        assert scraper_instance.driver.get.called

    def test_scroll_page(self, scraper_instance):
        """Test page scrolling functionality"""
        scraper_instance._scroll_page(scroll_pause=0.1, num_scrolls=2)

        # Verify execute_script was called
        assert scraper_instance.driver.execute_script.called


# ============================================================================
# Integration Tests (require actual browser)
# ============================================================================

@pytest.mark.integration
class TestIntegration:
    """Integration tests that require actual browser and network"""

    @pytest.mark.skip(reason="Requires manual Discord login")
    def test_full_login_flow(self):
        """Test complete login flow (manual intervention may be required)"""
        scraper = XtradesScraper()
        try:
            result = scraper.login()
            assert result is True
        finally:
            scraper.close()

    @pytest.mark.skip(reason="Requires authentication and network")
    def test_scrape_behappy_profile(self):
        """Test scraping the 'behappy' profile"""
        scraper = XtradesScraper()
        try:
            scraper.login()
            alerts = scraper.get_profile_alerts("behappy", max_alerts=5)

            assert len(alerts) > 0
            assert all('ticker' in alert for alert in alerts)

        finally:
            scraper.close()


# ============================================================================
# Error Handling Tests
# ============================================================================

class TestErrorHandling:
    """Test suite for error handling"""

    def test_login_retry_on_failure(self, scraper_instance):
        """Test retry logic on login failure"""
        scraper_instance._is_logged_in = Mock(return_value=False)
        scraper_instance._find_discord_button = Mock(return_value=None)

        with pytest.raises(LoginFailedException):
            scraper_instance.login(retry_count=2)

    def test_close_without_driver(self):
        """Test closing scraper without initialized driver"""
        with patch.dict(os.environ, {'XTRADES_USERNAME': 'test', 'XTRADES_PASSWORD': 'test'}):
            scraper = XtradesScraper.__new__(XtradesScraper)
            scraper.driver = None
            scraper.close()  # Should not raise exception


# ============================================================================
# Utility Tests
# ============================================================================

def test_convenience_function(mock_env_vars):
    """Test scrape_profile convenience function"""
    with patch('xtrades_scraper.XtradesScraper') as mock_scraper_class:
        mock_instance = MagicMock()
        mock_instance.get_profile_alerts.return_value = [
            {'ticker': 'AAPL', 'strategy': 'CSP'}
        ]
        mock_scraper_class.return_value = mock_instance

        result = scrape_profile("testuser", max_alerts=5)

        assert len(result) == 1
        assert result[0]['ticker'] == 'AAPL'
        assert mock_instance.login.called
        assert mock_instance.close.called


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
