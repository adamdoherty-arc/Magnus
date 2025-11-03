"""
Xtrades.net Scraper - Discord OAuth Authentication & Trade Alert Extraction
============================================================================
Logs into Xtrades.net via Discord OAuth and extracts trade alerts from profile pages.

Features:
- Discord OAuth login flow
- Profile scraping (https://app.xtrades.net/profile/{username})
- Alert parsing with multiple strategy types
- Session management with cookie persistence
- Anti-detection measures
- Retry logic with exponential backoff

Author: Magnus Wheel Strategy Dashboard
Created: 2025-11-02
"""

import os
import re
import time
import json
import pickle
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from datetime import datetime, timedelta
from decimal import Decimal

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException
)
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class XtradesScraperException(Exception):
    """Base exception for Xtrades scraper errors"""
    pass


class LoginFailedException(XtradesScraperException):
    """Raised when login fails"""
    pass


class ProfileNotFoundException(XtradesScraperException):
    """Raised when profile is not found"""
    pass


class XtradesScraper:
    """
    Scraper for Xtrades.net that handles Discord OAuth login and trade alert extraction.

    Usage:
        scraper = XtradesScraper()
        try:
            scraper.login()
            alerts = scraper.get_profile_alerts("behappy")
            for alert in alerts:
                print(f"Trade: {alert['ticker']} - {alert['strategy']}")
        finally:
            scraper.close()
    """

    # Constants
    BASE_URL = "https://app.xtrades.net"
    LOGIN_URL = f"{BASE_URL}/login"
    DISCORD_OAUTH_URL = "https://discord.com/api/oauth2/authorize"

    # Alert action patterns
    ACTION_PATTERNS = {
        'BTO': r'\bBTO\b',
        'STC': r'\bSTC\b',
        'BTC': r'\bBTC\b',
        'STO': r'\bSTO\b',
        'OPEN': r'\b(?:opened|opening)\b',
        'CLOSE': r'\b(?:closed|closing)\b'
    }

    # Strategy patterns
    STRATEGY_PATTERNS = {
        'CSP': r'\b(?:CSP|Cash[- ]?Secured[- ]?Put)\b',
        'CC': r'\b(?:CC|Covered[- ]?Call)\b',
        'Long Call': r'\b(?:Long[- ]?Call|LC)\b',
        'Long Put': r'\b(?:Long[- ]?Put|LP)\b',
        'Put Credit Spread': r'\b(?:Put[- ]?Credit[- ]?Spread|PCS)\b',
        'Call Credit Spread': r'\b(?:Call[- ]?Credit[- ]?Spread|CCS)\b',
        'Put Debit Spread': r'\b(?:Put[- ]?Debit[- ]?Spread|PDS)\b',
        'Call Debit Spread': r'\b(?:Call[- ]?Debit[- ]?Spread|CDS)\b',
        'Iron Condor': r'\b(?:Iron[- ]?Condor|IC)\b',
        'Butterfly': r'\b(?:Butterfly|BF)\b',
        'Straddle': r'\b(?:Straddle)\b',
        'Strangle': r'\b(?:Strangle)\b'
    }

    def __init__(self, headless: bool = False, cache_dir: Optional[str] = None):
        """
        Initialize the Xtrades scraper.

        Args:
            headless: Run browser in headless mode (default: False for Discord login)
            cache_dir: Directory for caching cookies and session data
        """
        self.username = os.getenv('XTRADES_USERNAME')
        self.password = os.getenv('XTRADES_PASSWORD')

        if not self.username or not self.password:
            raise ValueError("XTRADES_USERNAME and XTRADES_PASSWORD must be set in .env")

        self.headless = headless
        self.driver: Optional[webdriver.Chrome] = None
        self.wait: Optional[WebDriverWait] = None

        # Cache directory for cookies
        self.cache_dir = Path(cache_dir) if cache_dir else Path.home() / '.xtrades_cache'
        self.cache_dir.mkdir(exist_ok=True)
        self.cookies_file = self.cache_dir / 'cookies.pkl'

        self._setup_driver()

    def _setup_driver(self) -> None:
        """Setup Chrome driver with anti-detection measures"""
        options = uc.ChromeOptions()

        # Anti-detection options
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        # Commented out - incompatible with some Chrome versions
        # options.add_experimental_option("excludeSwitches", ["enable-automation"])
        # options.add_experimental_option('useAutomationExtension', False)

        # User agent
        options.add_argument(
            'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/120.0.0.0 Safari/537.36'
        )

        if self.headless:
            options.add_argument('--headless=new')
            options.add_argument('--disable-gpu')

        # Initialize driver
        try:
            self.driver = uc.Chrome(options=options, use_subprocess=True, version_main=None)
            self.driver.maximize_window()
            self.wait = WebDriverWait(self.driver, 20)

            # Remove webdriver flag
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                '''
            })

            print("Chrome driver initialized successfully")

        except Exception as e:
            raise XtradesScraperException(f"Failed to initialize Chrome driver: {e}")

    def _save_cookies(self) -> None:
        """Save cookies to file for session persistence"""
        try:
            cookies = self.driver.get_cookies()
            with open(self.cookies_file, 'wb') as f:
                pickle.dump(cookies, f)
            print(f"Cookies saved to {self.cookies_file}")
        except Exception as e:
            print(f"Warning: Failed to save cookies: {e}")

    def _load_cookies(self) -> bool:
        """Load cookies from file if available"""
        try:
            if not self.cookies_file.exists():
                return False

            with open(self.cookies_file, 'rb') as f:
                cookies = pickle.load(f)

            # Navigate to base URL first
            self.driver.get(self.BASE_URL)
            time.sleep(2)

            # Add cookies
            for cookie in cookies:
                # Remove expiry if present and invalid
                if 'expiry' in cookie:
                    del cookie['expiry']
                try:
                    self.driver.add_cookie(cookie)
                except Exception as e:
                    print(f"Warning: Could not add cookie {cookie.get('name')}: {e}")

            print("Cookies loaded successfully")
            return True

        except Exception as e:
            print(f"Warning: Failed to load cookies: {e}")
            return False

    def _is_logged_in(self) -> bool:
        """Check if currently logged in to Xtrades"""
        try:
            # Navigate to base URL
            self.driver.get(self.BASE_URL)
            time.sleep(3)

            # Check for user profile elements or dashboard
            indicators = [
                (By.CSS_SELECTOR, "[class*='profile']"),
                (By.CSS_SELECTOR, "[class*='user']"),
                (By.CSS_SELECTOR, "[class*='avatar']"),
                (By.XPATH, "//a[contains(@href, '/profile/')]"),
                (By.XPATH, "//*[contains(text(), 'Dashboard')]"),
            ]

            for by, selector in indicators:
                try:
                    self.driver.find_element(by, selector)
                    print("Already logged in to Xtrades")
                    return True
                except NoSuchElementException:
                    continue

            # Check if we're on login page
            current_url = self.driver.current_url.lower()
            if 'login' in current_url:
                return False

            return False

        except Exception as e:
            print(f"Error checking login status: {e}")
            return False

    def login(self, retry_count: int = 3) -> bool:
        """
        Login to Xtrades.net via Discord OAuth.

        Args:
            retry_count: Number of retry attempts on failure

        Returns:
            True if login successful, False otherwise

        Raises:
            LoginFailedException: If login fails after all retries
        """
        for attempt in range(retry_count):
            try:
                print(f"\nLogin attempt {attempt + 1}/{retry_count}")

                # Try loading saved cookies first
                if attempt == 0 and self._load_cookies():
                    if self._is_logged_in():
                        print("Logged in using saved session")
                        return True
                    else:
                        print("Saved session expired, proceeding with fresh login")

                # Navigate to login page
                print(f"Navigating to {self.LOGIN_URL}")
                self.driver.get(self.LOGIN_URL)
                time.sleep(3)

                # Look for Discord login button
                discord_btn = self._find_discord_button()
                if not discord_btn:
                    raise LoginFailedException("Discord login button not found")

                print("Clicking Discord login button")
                discord_btn.click()
                time.sleep(3)

                # Handle Discord OAuth flow
                if not self._handle_discord_oauth():
                    raise LoginFailedException("Discord OAuth failed")

                # Verify login
                time.sleep(3)
                if self._is_logged_in():
                    print("Login successful!")
                    self._save_cookies()
                    return True
                else:
                    print("Login verification failed")

            except Exception as e:
                print(f"Login attempt {attempt + 1} failed: {e}")
                if attempt < retry_count - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    print(f"Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                continue

        raise LoginFailedException(f"Failed to login after {retry_count} attempts")

    def _find_discord_button(self) -> Optional[webdriver.remote.webelement.WebElement]:
        """Find and return Discord login button"""
        selectors = [
            (By.XPATH, "//button[contains(., 'Discord')]"),
            (By.XPATH, "//a[contains(., 'Discord')]"),
            (By.CSS_SELECTOR, "button[class*='discord']"),
            (By.CSS_SELECTOR, "a[class*='discord']"),
            (By.XPATH, "//*[contains(@class, 'discord')]"),
        ]

        for by, selector in selectors:
            try:
                element = self.wait.until(
                    EC.element_to_be_clickable((by, selector))
                )
                return element
            except TimeoutException:
                continue

        return None

    def _handle_discord_oauth(self) -> bool:
        """
        Handle Discord OAuth login flow.

        Returns:
            True if OAuth completed successfully
        """
        try:
            # Wait for Discord login page
            time.sleep(2)
            current_url = self.driver.current_url

            # Check if we're on Discord OAuth page
            if 'discord.com' not in current_url:
                print("Not redirected to Discord OAuth")
                return False

            print("On Discord OAuth page")

            # Check if already authorized
            if 'authorize' not in current_url or 'xtrades' in current_url:
                print("Already authorized or redirected back")
                return True

            # Look for email input
            try:
                email_input = self.wait.until(
                    EC.presence_of_element_located((By.NAME, "email"))
                )
                email_input.clear()
                email_input.send_keys(self.username)
                print(f"Entered email: {self.username}")
                time.sleep(1)
            except TimeoutException:
                print("Email input not found - might already be logged in")

            # Look for password input
            try:
                password_input = self.driver.find_element(By.NAME, "password")
                password_input.clear()
                password_input.send_keys(self.password)
                print("Entered password")
                time.sleep(1)
            except NoSuchElementException:
                print("Password input not found")

            # Click login button
            try:
                login_btn = self.driver.find_element(By.XPATH, "//button[@type='submit']")
                login_btn.click()
                print("Clicked Discord login button")
                time.sleep(3)
            except NoSuchElementException:
                print("Login button not found")

            # Look for "Authorize" button
            try:
                authorize_btn = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Authorize') or contains(., 'authorize')]"))
                )
                authorize_btn.click()
                print("Clicked Authorize button")
                time.sleep(3)
            except TimeoutException:
                print("Authorize button not found - might be already authorized")

            # Wait for redirect back to Xtrades
            for _ in range(10):
                current_url = self.driver.current_url
                if 'xtrades.net' in current_url and 'login' not in current_url:
                    print("Redirected back to Xtrades")
                    return True
                time.sleep(1)

            print("Warning: Did not detect redirect back to Xtrades")
            return False

        except Exception as e:
            print(f"Error in Discord OAuth flow: {e}")
            return False

    def get_profile_alerts(
        self,
        username: str,
        max_alerts: Optional[int] = None
    ) -> List[Dict]:
        """
        Get trade alerts from a profile page.

        Args:
            username: Xtrades.net username to scrape
            max_alerts: Maximum number of alerts to retrieve (None = all)

        Returns:
            List of parsed trade alert dictionaries

        Raises:
            ProfileNotFoundException: If profile doesn't exist
            XtradesScraperException: For other errors
        """
        profile_url = f"{self.BASE_URL}/profile/{username}"

        try:
            print(f"\nNavigating to profile: {username}")
            self.driver.get(profile_url)
            time.sleep(3)

            # Check for 404 or profile not found
            if "404" in self.driver.title or "not found" in self.driver.page_source.lower():
                raise ProfileNotFoundException(f"Profile '{username}' not found")

            # Scroll to load more content
            self._scroll_page()

            # Get page source and parse
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            # Find alerts
            alerts = self._find_alert_elements(soup)

            if not alerts:
                print(f"No alerts found for {username}")
                return []

            print(f"Found {len(alerts)} alert elements")

            # Parse each alert
            parsed_alerts = []
            for i, alert_elem in enumerate(alerts):
                if max_alerts and i >= max_alerts:
                    break

                try:
                    parsed = self.parse_alert(alert_elem)
                    if parsed:
                        parsed['profile_username'] = username
                        parsed_alerts.append(parsed)
                except Exception as e:
                    print(f"Error parsing alert {i+1}: {e}")
                    continue

            print(f"Successfully parsed {len(parsed_alerts)} alerts")
            return parsed_alerts

        except ProfileNotFoundException:
            raise
        except Exception as e:
            raise XtradesScraperException(f"Error getting profile alerts: {e}")

    def _scroll_page(self, scroll_pause: float = 1.0, num_scrolls: int = 3) -> None:
        """Scroll page to load dynamic content"""
        try:
            for i in range(num_scrolls):
                self.driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);"
                )
                time.sleep(scroll_pause)
                print(f"Scrolled {i+1}/{num_scrolls}")
        except Exception as e:
            print(f"Error scrolling page: {e}")

    def _find_alert_elements(self, soup: BeautifulSoup) -> List:
        """
        Find alert elements in page HTML.

        Args:
            soup: BeautifulSoup object of page HTML

        Returns:
            List of alert elements
        """
        # Try various selectors
        selectors = [
            {'name': 'div', 'class_': re.compile(r'alert', re.I)},
            {'name': 'div', 'class_': re.compile(r'trade', re.I)},
            {'name': 'div', 'class_': re.compile(r'post', re.I)},
            {'name': 'article'},
            {'name': 'div', 'class_': re.compile(r'card', re.I)},
        ]

        for selector in selectors:
            elements = soup.find_all(**selector)
            if elements:
                print(f"Found {len(elements)} elements with selector {selector}")
                return elements

        # Fallback: get all divs with substantial text
        all_divs = soup.find_all('div')
        alerts = [div for div in all_divs if div.get_text(strip=True) and len(div.get_text(strip=True)) > 20]

        return alerts

    def parse_alert(self, alert_element) -> Optional[Dict]:
        """
        Parse individual alert element into structured data.

        Args:
            alert_element: BeautifulSoup element or HTML string

        Returns:
            Dictionary with parsed trade data or None if parsing fails
        """
        try:
            # Get text content
            if isinstance(alert_element, str):
                alert_text = alert_element
            else:
                alert_text = alert_element.get_text(strip=True)

            if not alert_text or len(alert_text) < 5:
                return None

            # Initialize result
            result: Dict = {
                'alert_text': alert_text,
                'ticker': None,
                'strategy': None,
                'action': None,
                'entry_price': None,
                'exit_price': None,
                'quantity': None,
                'strike_price': None,
                'expiration_date': None,
                'pnl': None,
                'pnl_percent': None,
                'alert_timestamp': None,
                'entry_date': None,
                'exit_date': None,
                'status': 'open'
            }

            # Extract ticker (3-5 uppercase letters, isolated)
            ticker_match = re.search(r'\b([A-Z]{1,5})\b', alert_text)
            if ticker_match:
                result['ticker'] = ticker_match.group(1)

            # Extract strategy
            for strategy, pattern in self.STRATEGY_PATTERNS.items():
                if re.search(pattern, alert_text, re.IGNORECASE):
                    result['strategy'] = strategy
                    break

            # Extract action
            for action, pattern in self.ACTION_PATTERNS.items():
                if re.search(pattern, alert_text, re.IGNORECASE):
                    result['action'] = action
                    break

            # Extract prices (looking for $XX.XX or @$XX.XX)
            prices = re.findall(r'[@$]\$?(\d+\.?\d*)', alert_text)
            if prices:
                result['entry_price'] = float(prices[0])
                if len(prices) > 1:
                    # Could be exit price or strike
                    result['exit_price'] = float(prices[1])

            # Extract strike price (often like "$170 strike" or "$170 Put")
            strike_match = re.search(r'\$(\d+\.?\d*)\s*(?:strike|put|call)', alert_text, re.IGNORECASE)
            if strike_match:
                result['strike_price'] = float(strike_match.group(1))

            # Extract quantity
            qty_match = re.search(r'(\d+)\s*x\s*\$', alert_text)
            if not qty_match:
                qty_match = re.search(r'\b(\d+)\s*contracts?\b', alert_text, re.IGNORECASE)
            if qty_match:
                result['quantity'] = int(qty_match.group(1))
            else:
                result['quantity'] = 1  # Default

            # Extract P&L
            pnl_match = re.search(r'(\+|-)\$?(\d+\.?\d*)', alert_text)
            if pnl_match:
                sign = 1 if pnl_match.group(1) == '+' else -1
                result['pnl'] = sign * float(pnl_match.group(2))

            # Extract P&L percentage
            pnl_pct_match = re.search(r'(\+|-)(\d+\.?\d*)%', alert_text)
            if pnl_pct_match:
                sign = 1 if pnl_pct_match.group(1) == '+' else -1
                result['pnl_percent'] = sign * float(pnl_pct_match.group(2))

            # Extract dates (MM/DD, MM/DD/YY, MM/DD/YYYY)
            date_matches = re.findall(r'(\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?)', alert_text)
            if date_matches:
                result['expiration_date'] = self._parse_date(date_matches[0])

            # Determine status
            if result['action'] in ['STC', 'BTC', 'CLOSE'] or result['exit_price']:
                result['status'] = 'closed'
            elif 'expired' in alert_text.lower():
                result['status'] = 'expired'

            # Set timestamps
            result['alert_timestamp'] = datetime.now().isoformat()
            result['scraped_at'] = datetime.now().isoformat()

            # Only return if we have minimum required data
            if result['ticker']:
                return result

            return None

        except Exception as e:
            print(f"Error parsing alert: {e}")
            return None

    def _parse_date(self, date_str: str) -> Optional[str]:
        """
        Parse date string into ISO format.

        Args:
            date_str: Date string in various formats

        Returns:
            ISO format date string or None
        """
        try:
            # Try various formats
            formats = [
                '%m/%d/%Y',
                '%m/%d/%y',
                '%m/%d',
                '%m-%d-%Y',
                '%m-%d-%y',
                '%m-%d'
            ]

            for fmt in formats:
                try:
                    if '/' in date_str or '-' in date_str:
                        dt = datetime.strptime(date_str, fmt)
                        # If year not provided, assume current year
                        if dt.year == 1900:
                            dt = dt.replace(year=datetime.now().year)
                        return dt.date().isoformat()
                except ValueError:
                    continue

            return None

        except Exception as e:
            print(f"Error parsing date '{date_str}': {e}")
            return None

    def close(self) -> None:
        """Close browser and cleanup"""
        if self.driver:
            try:
                self.driver.quit()
                print("Browser closed")
            except Exception as e:
                print(f"Error closing browser: {e}")


# Convenience functions

def scrape_profile(username: str, max_alerts: Optional[int] = None) -> List[Dict]:
    """
    Convenience function to scrape a profile.

    Args:
        username: Xtrades.net username
        max_alerts: Maximum alerts to retrieve

    Returns:
        List of parsed alerts
    """
    scraper = XtradesScraper()
    try:
        scraper.login()
        return scraper.get_profile_alerts(username, max_alerts)
    finally:
        scraper.close()


def main():
    """Example usage"""
    scraper = XtradesScraper()

    try:
        # Login
        print("Logging in to Xtrades.net...")
        scraper.login()

        # Scrape profile
        username = "behappy"  # Example profile
        print(f"\nScraping profile: {username}")
        alerts = scraper.get_profile_alerts(username, max_alerts=10)

        # Display results
        print(f"\n{'='*80}")
        print(f"Found {len(alerts)} alerts from {username}")
        print(f"{'='*80}\n")

        for i, alert in enumerate(alerts, 1):
            print(f"Alert {i}:")
            print(f"  Ticker: {alert['ticker']}")
            print(f"  Strategy: {alert['strategy']}")
            print(f"  Action: {alert['action']}")
            print(f"  Entry Price: ${alert['entry_price']}" if alert['entry_price'] else "  Entry Price: N/A")
            print(f"  Strike: ${alert['strike_price']}" if alert['strike_price'] else "  Strike: N/A")
            print(f"  Expiration: {alert['expiration_date']}" if alert['expiration_date'] else "  Expiration: N/A")
            print(f"  P&L: ${alert['pnl']}" if alert['pnl'] else "  P&L: N/A")
            print(f"  Status: {alert['status']}")
            print(f"  Alert Text: {alert['alert_text'][:100]}...")
            print()

    except LoginFailedException as e:
        print(f"\nLogin failed: {e}")
        print("Please check your credentials in .env file")
    except ProfileNotFoundException as e:
        print(f"\nProfile error: {e}")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        scraper.close()


if __name__ == "__main__":
    main()
