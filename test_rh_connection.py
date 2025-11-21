"""Test Robinhood Connection"""

import robin_stocks.robinhood as rh
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("ROBINHOOD CONNECTION TEST")
print("=" * 60)

# Test 1: Check credentials from environment
print("\n1. Checking environment variables...")
username = os.getenv('ROBINHOOD_USERNAME', 'brulecapital@gmail.com')
password = os.getenv('ROBINHOOD_PASSWORD', 'FortKnox')
print(f"   Username: {username}")
print(f"   Password: {'*' * len(password)} ({len(password)} characters)")

# Test 2: Attempt logout first
print("\n2. Clearing any existing sessions...")
try:
    rh.logout()
    print("   ✓ Logged out")
except Exception as e:
    print(f"   - No active session to clear: {e}")

# Test 3: Attempt login
print("\n3. Attempting login...")
try:
    login_result = rh.login(username=username, password=password)
    print(f"   Login result type: {type(login_result)}")
    print(f"   Login result: {login_result}")

    if login_result:
        print("   ✓ Login succeeded")
    else:
        print("   ✗ Login returned None or False")

except Exception as e:
    print(f"   ✗ Login failed with error: {e}")
    print(f"   Error type: {type(e).__name__}")
    import traceback
    print("\n   Full traceback:")
    traceback.print_exc()

# Test 4: Check if MFA is required
print("\n4. Checking MFA status...")
try:
    # If MFA is required, we need to handle it
    import pickle
    import os

    # Check if there's a pickle file for session
    home = os.path.expanduser("~")
    pickle_path = os.path.join(home, ".tokens", "robinhood.pickle")

    if os.path.exists(pickle_path):
        print(f"   Found pickle file: {pickle_path}")
    else:
        print(f"   No pickle file found at: {pickle_path}")
        print("   This might indicate MFA is required")

except Exception as e:
    print(f"   Error checking pickle: {e}")

# Test 5: Test session with profile call
print("\n5. Testing session with load_account_profile...")
try:
    profile = rh.load_account_profile()

    if profile:
        print("   ✓ Successfully loaded account profile")
        print(f"   Account number: {profile.get('account_number', 'N/A')}")
        print(f"   Account type: {profile.get('type', 'N/A')}")
    else:
        print("   ✗ Profile returned None")

except Exception as e:
    print(f"   ✗ Failed to load profile: {e}")
    print(f"   Error type: {type(e).__name__}")

# Test 6: Check authentication endpoint directly
print("\n6. Checking authentication status...")
try:
    # Try to get some basic data that requires auth
    positions = rh.get_open_stock_positions()
    print(f"   ✓ Can access positions (logged in)")
    print(f"   Number of positions: {len(positions) if positions else 0}")
except Exception as e:
    print(f"   ✗ Cannot access positions: {e}")

# Test 7: Check for 2FA requirement
print("\n7. Checking 2FA/MFA requirement...")
try:
    # Check if login was waiting for MFA
    import inspect

    # See what parameters login accepts
    login_sig = inspect.signature(rh.login)
    print(f"   Login function parameters: {list(login_sig.parameters.keys())}")

    # Check if there's an mfa_code parameter
    if 'mfa_code' in login_sig.parameters:
        print("   ⚠️  MFA might be required for this account")
        print("   Try logging in manually and saving the session")

except Exception as e:
    print(f"   Error checking MFA: {e}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
