"""
Extract Kalshi Session Token from Browser
Run this after logging into Kalshi website in your browser

This method bypasses API key requirements and SMS verification issues
by using your authenticated web session token.
"""

import sys
import os
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("=" * 80)
print("EXTRACT KALSHI SESSION TOKEN FROM BROWSER")
print("=" * 80)
print()
print("WHY THIS METHOD?")
print("- API key authentication requires Premier/Market Maker account")
print("- Email/password API authentication doesn't support SMS verification")
print("- Web login works with SMS verification ✅")
print("- This method uses your web session token to access the API")
print()
print("=" * 80)
print()
print("STEP-BY-STEP INSTRUCTIONS:")
print()
print("1. Open your browser and go to: https://kalshi.com")
print()
print("2. Log in with your email and password")
print("   (Complete SMS verification when prompted)")
print()
print("3. Once logged in successfully, press F12 to open Developer Tools")
print()
print("4. In Developer Tools:")
print("   - Chrome/Edge: Click 'Application' tab → 'Cookies' → 'https://kalshi.com'")
print("   - Firefox: Click 'Storage' tab → 'Cookies' → 'https://kalshi.com'")
print()
print("5. Look for a cookie with one of these names:")
print("   - kalshi_session")
print("   - auth_token")
print("   - bearer")
print("   - token")
print("   - session")
print()
print("6. Click on the cookie and copy its VALUE (not the name)")
print("   - Should be a long string of letters and numbers")
print("   - Example: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
print()
print("=" * 80)
print()

session_token = input("Paste your session token here: ").strip()

if session_token:
    print()
    print("✅ Session token captured!")
    print()
    print(f"Token preview: {session_token[:50]}...")
    print()

    # Save to .env
    save = input("Automatically add to .env file? (y/n): ")
    if save.lower() == 'y':
        # Check if token already exists in .env
        env_path = '.env'
        existing_content = ""
        token_exists = False

        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                existing_content = f.read()
                token_exists = 'KALSHI_SESSION_TOKEN=' in existing_content

        if token_exists:
            # Replace existing token
            print("\n⚠️  KALSHI_SESSION_TOKEN already exists in .env")
            replace = input("Replace it with new token? (y/n): ")
            if replace.lower() == 'y':
                # Replace old token with new one
                import re
                new_content = re.sub(
                    r'KALSHI_SESSION_TOKEN=.*',
                    f'KALSHI_SESSION_TOKEN={session_token}',
                    existing_content
                )
                with open(env_path, 'w') as f:
                    f.write(new_content)
                print("✅ Updated session token in .env file!")
            else:
                print("❌ Keeping existing token")
        else:
            # Append new token
            with open(env_path, 'a') as f:
                f.write(f"\n# Kalshi Session Token (from browser web login)\n")
                f.write(f"# Extracted: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"KALSHI_SESSION_TOKEN={session_token}\n")
            print("✅ Added session token to .env file!")

        print()
        print("=" * 80)
        print("NEXT STEPS:")
        print("=" * 80)
        print()
        print("1. Test authentication:")
        print("   python -c \"from src.kalshi_client_v2 import KalshiClientV2; c=KalshiClientV2(); print('✅ Auth works!' if c.login() else '❌ Auth failed')\"")
        print()
        print("2. Sync Kalshi team winner markets:")
        print("   python sync_kalshi_team_winners.py --sport football")
        print()
        print("3. View synced markets:")
        print("   python sync_kalshi_team_winners.py --list")
        print()
        print("4. Verify game cards system:")
        print("   python verify_game_cards_system.py")
        print()
        print("=" * 80)
    else:
        print()
        print("Manual setup:")
        print(f"Add this line to your .env file:")
        print()
        print(f"KALSHI_SESSION_TOKEN={session_token}")
        print()
else:
    print("❌ No token provided")
    print()
    print("Try again and make sure to copy the full cookie value.")
