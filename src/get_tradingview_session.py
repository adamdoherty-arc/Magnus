"""Automatically retrieve TradingView session ID using Selenium"""

import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from dotenv import load_dotenv, set_key
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


def get_session_id_programmatically(save_to_env: bool = True) -> str:
    """
    Automatically log in to TradingView and retrieve session ID

    Args:
        save_to_env: If True, saves the session ID to .env file

    Returns:
        Session ID string, or empty string if failed
    """
    username = os.getenv('TRADINGVIEW_USERNAME')
    password = os.getenv('TRADINGVIEW_PASSWORD')

    if not username or not password:
        logger.error("TradingView credentials not found in .env file")
        logger.info("Please set TRADINGVIEW_USERNAME and TRADINGVIEW_PASSWORD")
        return ""

    driver = None

    try:
        # Setup Chrome options
        chrome_options = Options()
        # Comment out headless to see the browser (useful for debugging)
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

        logger.info("Starting Chrome browser...")
        driver = webdriver.Chrome(options=chrome_options)

        # Navigate to TradingView login page
        logger.info("Navigating to TradingView login page...")
        driver.get("https://www.tradingview.com/")
        time.sleep(3)

        # Click the "Sign in" button on homepage
        try:
            signin_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'Open user menu')]"))
            )
            signin_button.click()
            time.sleep(2)

            # Click "Sign in" from the menu
            signin_menu = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Sign in')]"))
            )
            signin_menu.click()
            time.sleep(2)
        except:
            # Alternative: go directly to sign-in URL
            logger.info("Direct navigation to signin page...")
            driver.get("https://www.tradingview.com/accounts/signin/")
            time.sleep(3)

        # Click "Email" signin button
        try:
            logger.info("Selecting email login method...")
            email_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@name, 'Email')]"))
            )
            email_button.click()
            time.sleep(2)
        except:
            logger.info("Email button not found, trying alternative selectors...")
            try:
                # Try alternative selector
                email_button = driver.find_element(By.XPATH, "//span[contains(text(), 'Email')]/ancestor::button")
                email_button.click()
                time.sleep(2)
            except:
                logger.warning("Could not find email button, proceeding anyway...")

        # Enter username/email
        logger.info("Entering username...")
        username_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "id_username"))
        )
        username_input.clear()
        username_input.send_keys(username)
        time.sleep(1)

        # Enter password
        logger.info("Entering password...")
        password_input = driver.find_element(By.NAME, "id_password")
        password_input.clear()
        password_input.send_keys(password)
        time.sleep(1)

        # Submit form - try multiple selectors
        logger.info("Submitting login form...")
        submit_found = False

        # Try different submit button selectors
        submit_selectors = [
            "//button[@type='submit']",
            "//button[contains(@class, 'submitButton')]",
            "//button[contains(text(), 'Sign in')]",
            "//button[contains(@aria-label, 'Sign in')]",
            "//span[contains(text(), 'Sign in')]/ancestor::button"
        ]

        for selector in submit_selectors:
            try:
                submit_button = driver.find_element(By.XPATH, selector)
                submit_button.click()
                submit_found = True
                logger.info(f"Clicked submit button using selector: {selector[:50]}")
                break
            except:
                continue

        if not submit_found:
            logger.warning("Could not find submit button with standard selectors")
            logger.info("Taking screenshot for debugging...")
            try:
                driver.save_screenshot("login_page_debug.png")
                logger.info("Screenshot saved as login_page_debug.png")
            except:
                pass

            # Try pressing Enter key on password field as fallback
            try:
                password_input.send_keys(Keys.RETURN)
                logger.info("Submitted form using Enter key")
            except:
                logger.error("All submit methods failed")
                return ""

        # Wait for login to complete
        logger.info("Waiting for login to complete...")
        time.sleep(10)

        # Check if we need to handle 2FA or other verification
        try:
            # Look for any verification code input
            verification_input = driver.find_elements(By.XPATH, "//input[@type='text' or @type='number']")
            if verification_input:
                logger.warning("2FA or verification required!")
                logger.warning("Please complete the verification in the browser window")
                logger.warning("Waiting 60 seconds for manual verification...")
                time.sleep(60)
        except:
            pass

        # Check if logged in by looking for user menu or by checking cookies
        session_id = None

        # Get all cookies
        cookies = driver.get_cookies()
        logger.info(f"Retrieved {len(cookies)} cookies")

        # Find sessionid cookie
        for cookie in cookies:
            if cookie['name'] == 'sessionid':
                session_id = cookie['value']
                logger.info(f"Found session ID: {session_id[:16]}...")
                break

        if not session_id:
            logger.error("Could not find sessionid cookie!")
            logger.info("Login may have failed. Check your credentials or 2FA requirements.")
            return ""

        # Verify the session ID looks valid (should be 32 characters)
        if len(session_id) < 20:
            logger.warning(f"Session ID seems too short: {len(session_id)} characters")
            return ""

        logger.info(f"Successfully retrieved session ID: {session_id[:16]}...")

        # Save to .env file if requested
        if save_to_env:
            env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')

            try:
                # Update or add TRADINGVIEW_SESSION_ID
                set_key(env_path, 'TRADINGVIEW_SESSION_ID', session_id)
                logger.info(f"Session ID saved to .env file at {env_path}")
            except Exception as e:
                logger.error(f"Failed to save to .env file: {e}")
                logger.info(f"Please manually add to .env: TRADINGVIEW_SESSION_ID={session_id}")

        return session_id

    except Exception as e:
        logger.error(f"Error retrieving session ID: {e}")
        import traceback
        traceback.print_exc()
        return ""

    finally:
        if driver:
            logger.info("Closing browser...")
            driver.quit()


def test_session_id(session_id: str) -> bool:
    """Test if the session ID works by making an API request"""
    import requests

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'cookie': f'sessionid={session_id}'
    }

    try:
        response = requests.get(
            'https://www.tradingview.com/api/v1/symbols_list/custom/',
            headers=headers
        )

        if response.status_code == 200:
            logger.info("Session ID is valid and working!")
            return True
        else:
            logger.warning(f"Session ID test failed with status {response.status_code}")
            return False

    except Exception as e:
        logger.error(f"Failed to test session ID: {e}")
        return False


if __name__ == "__main__":
    print("="*60)
    print("TradingView Session ID Retriever")
    print("="*60)
    print("\nThis script will:")
    print("1. Open a browser and log in to TradingView")
    print("2. Extract the session cookie")
    print("3. Save it to your .env file")
    print("\nNote: You may need to complete 2FA if enabled on your account")
    print("="*60)

    # Get session ID
    session_id = get_session_id_programmatically(save_to_env=True)

    if session_id:
        print("\n" + "="*60)
        print("SUCCESS!")
        print("="*60)
        print(f"Session ID: {session_id}")
        print(f"First 16 chars: {session_id[:16]}...")
        print("\nTesting session ID...")

        if test_session_id(session_id):
            print("\n[OK] Session ID is working correctly!")
            print("\nYou can now run:")
            print("  python src/tradingview_api_sync.py")
        else:
            print("\n[WARNING] Session ID retrieved but not working yet")
            print("This might be due to:")
            print("  - 2FA verification needed")
            print("  - Additional security checks")
            print("  - Try running the script again")
    else:
        print("\n" + "="*60)
        print("FAILED")
        print("="*60)
        print("Could not retrieve session ID")
        print("\nPossible issues:")
        print("  - Incorrect username/password in .env")
        print("  - 2FA enabled (requires manual intervention)")
        print("  - TradingView login page changed")
        print("  - Network/firewall issues")
