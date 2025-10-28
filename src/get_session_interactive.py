"""Interactive TradingView Session ID Retriever - Handles 2FA manually"""

import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv, set_key
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

load_dotenv()


def get_session_interactive():
    """
    Interactive session ID retrieval - browser stays visible for manual 2FA
    """
    username = os.getenv('TRADINGVIEW_USERNAME')
    password = os.getenv('TRADINGVIEW_PASSWORD')

    if not username or not password:
        logger.error("TradingView credentials not found in .env file")
        return ""

    driver = None

    try:
        # Setup Chrome options - VISIBLE MODE
        chrome_options = Options()
        # DO NOT USE HEADLESS - user needs to see the browser
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

        logger.info("Opening Chrome browser (visible mode)...")
        driver = webdriver.Chrome(options=chrome_options)

        # Go directly to sign-in URL
        logger.info("Navigating to TradingView sign-in page...")
        driver.get("https://www.tradingview.com/accounts/signin/")
        time.sleep(3)

        # Click "Email" signin button
        logger.info("Looking for email login button...")
        try:
            email_selectors = [
                "//button[contains(@name, 'Email')]",
                "//span[contains(text(), 'Email')]/ancestor::button",
                "//button[contains(., 'Email')]"
            ]

            for selector in email_selectors:
                try:
                    email_button = driver.find_element(By.XPATH, selector)
                    email_button.click()
                    logger.info("Clicked email login button")
                    time.sleep(2)
                    break
                except:
                    continue
        except:
            logger.info("Email button not found or already on email form")

        # Enter username/email
        logger.info("Entering credentials...")
        try:
            username_input = driver.find_element(By.NAME, "id_username")
            username_input.clear()
            username_input.send_keys(username)
            time.sleep(1)

            # Enter password
            password_input = driver.find_element(By.NAME, "id_password")
            password_input.clear()
            password_input.send_keys(password)
            time.sleep(1)

            # Submit by pressing Enter
            password_input.send_keys(Keys.RETURN)
            logger.info("Login form submitted")

        except Exception as e:
            logger.error(f"Error filling login form: {e}")
            logger.warning("Please complete the login manually in the browser window")

        # Wait for user to complete login/2FA
        print("\n" + "="*70)
        print("MANUAL INTERVENTION REQUIRED")
        print("="*70)
        print("\nThe browser window should now be open.")
        print("\nPlease complete the following steps:")
        print("  1. Check if you need to complete CAPTCHA")
        print("  2. Enter 2FA code if prompted (email/SMS/authenticator app)")
        print("  3. Complete any other verification steps")
        print("  4. Wait until you see the TradingView main page/chart")
        print("\nDO NOT CLOSE THE BROWSER WINDOW!")
        print("\nWaiting 90 seconds for you to complete login...")
        print("="*70)

        # Wait 90 seconds for manual completion
        for i in range(9):
            time.sleep(10)
            logger.info(f"Still waiting... ({(i+1)*10} seconds elapsed)")

        # Extract session ID
        logger.info("\nChecking for session cookie...")
        cookies = driver.get_cookies()

        session_id = None
        for cookie in cookies:
            if cookie['name'] == 'sessionid':
                session_id = cookie['value']
                break

        if not session_id:
            logger.error("\nSession ID not found!")
            logger.warning("Login may not be complete. Please check the browser.")

            # Give one more chance
            logger.info("Waiting another 30 seconds...")
            time.sleep(30)

            cookies = driver.get_cookies()
            for cookie in cookies:
                if cookie['name'] == 'sessionid':
                    session_id = cookie['value']
                    break

        if session_id:
            logger.info(f"\n\n{'='*70}")
            logger.info("SUCCESS! Session ID found!")
            logger.info(f"{'='*70}")
            logger.info(f"Session ID: {session_id}")
            logger.info(f"Length: {len(session_id)} characters")

            # Save to .env
            env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')

            try:
                # Read existing .env
                with open(env_path, 'r') as f:
                    lines = f.readlines()

                # Update or add session ID
                found = False
                for i, line in enumerate(lines):
                    if line.startswith('TRADINGVIEW_SESSION_ID='):
                        lines[i] = f'TRADINGVIEW_SESSION_ID={session_id}\n'
                        found = True
                        break

                if not found:
                    # Add after TRADINGVIEW_PASSWORD
                    for i, line in enumerate(lines):
                        if line.startswith('TRADINGVIEW_PASSWORD='):
                            lines.insert(i + 1, f'TRADINGVIEW_SESSION_ID={session_id}\n')
                            break

                # Write back
                with open(env_path, 'w') as f:
                    f.writelines(lines)

                logger.info(f"\nSession ID saved to: {env_path}")
                logger.info("\nYou can now run: python src/tradingview_api_sync.py")

            except Exception as e:
                logger.error(f"\nFailed to save to .env: {e}")
                logger.info(f"\nPlease manually add this line to your .env file:")
                logger.info(f"TRADINGVIEW_SESSION_ID={session_id}")

            return session_id

        else:
            logger.error("\nFailed to retrieve session ID")
            logger.info("Possible reasons:")
            logger.info("  - Login was not completed")
            logger.info("  - Incorrect credentials")
            logger.info("  - Additional verification required")
            return ""

    except Exception as e:
        logger.error(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return ""

    finally:
        if driver:
            logger.info("\nKeeping browser open for 10 more seconds...")
            logger.info("(You can close it manually after)")
            time.sleep(10)
            driver.quit()


if __name__ == "__main__":
    import sys

    # Check if running in automated mode (called from another script)
    automated = len(sys.argv) > 1 and sys.argv[1] == '--auto'

    if not automated:
        print("\n" + "="*70)
        print("INTERACTIVE TradingView Session ID Retriever")
        print("="*70)
        print("\nThis script will:")
        print("  1. Open TradingView in a VISIBLE browser window")
        print("  2. Fill in your username and password")
        print("  3. Wait for YOU to complete 2FA/verification")
        print("  4. Extract and save the session cookie")
        print("\nIMPORTANT:")
        print("  - Do NOT close the browser window while script is running")
        print("  - Complete any 2FA/CAPTCHA prompts when they appear")
        print("  - Wait until you see TradingView's main page")
        print("="*70)

        input("\nPress ENTER to start...")

    session_id = get_session_interactive()

    if session_id:
        print("\n" + "="*70)
        print("SETUP COMPLETE!")
        print("="*70)
        print(f"\nSession ID: {session_id[:32]}...")
        if not automated:
            print("\nNext steps:")
            print("  1. Run: python src/tradingview_api_sync.py")
            print("  2. Your watchlists will be synced to the database")
        print("="*70)
        sys.exit(0)  # Success
    else:
        print("\n" + "="*70)
        print("SETUP FAILED")
        print("="*70)
        print("\nPlease try again or check:")
        print("  - Your username/password in .env are correct")
        print("  - You have access to your 2FA device")
        print("  - TradingView account is not locked")
        print("="*70)
        sys.exit(1)  # Failure
