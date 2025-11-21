"""
Quick test to verify Kalshi API credentials are working
"""
import os
from dotenv import load_dotenv
from src.kalshi_integration import KalshiIntegration

def test_connection():
    """Test Kalshi API connection with credentials from .env"""

    # Load environment variables
    load_dotenv()

    email = os.getenv('KALSHI_EMAIL')
    password = os.getenv('KALSHI_PASSWORD')

    print("="*80)
    print("KALSHI CONNECTION TEST")
    print("="*80)

    # Check credentials are set
    if not email or email.strip() == '':
        print("[ERROR] KALSHI_EMAIL not set in .env file")
        print("Please add your email to .env")
        return False

    if not password or password.strip() == '':
        print("[ERROR] KALSHI_PASSWORD not set in .env file")
        print("Please add your password to .env")
        return False

    print(f"Email: {email}")
    print(f"Password: {'*' * len(password)} (hidden)")
    print()

    # Test connection
    try:
        print("Connecting to Kalshi API...")
        kalshi = KalshiIntegration()

        print("[OK] Authentication successful!")
        print()

        # Try fetching a few markets
        print("Fetching sample markets...")
        markets = kalshi.get_markets(limit=5, status='active')

        print(f"[OK] Retrieved {len(markets)} sample markets")
        print()

        if markets:
            print("Sample market:")
            m = markets[0]
            print(f"  Ticker: {m.get('ticker', 'N/A')}")
            print(f"  Title: {m.get('title', 'N/A')}")
            print(f"  Status: {m.get('status', 'N/A')}")
            if 'yes_bid' in m:
                print(f"  Yes Price: ${m.get('yes_bid', 0):.2f}")
            print()

        print("="*80)
        print("[SUCCESS] Kalshi integration is working!")
        print("="*80)
        print()
        print("Next step: Run sync script to fetch NFL/NCAA markets")
        print("Command: python pull_nfl_games.py")
        print()
        return True

    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        print()
        print("Troubleshooting:")
        print("1. Check email/password are correct")
        print("2. Try logging into kalshi.com with same credentials")
        print("3. If website works, check for typos in .env")
        print("4. Make sure .env file was saved")
        print()
        return False

if __name__ == "__main__":
    test_connection()
