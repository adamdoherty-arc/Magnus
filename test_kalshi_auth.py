"""
Kalshi Authentication Test Script
Tests different authentication methods to help debug connection issues
"""

import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

print("="*80)
print("KALSHI AUTHENTICATION TEST")
print("="*80)

# Check credentials
api_key = os.getenv('KALSHI_API_KEY')
private_key_path = os.getenv('KALSHI_PRIVATE_KEY_PATH')
email = os.getenv('KALSHI_EMAIL')
password = os.getenv('KALSHI_PASSWORD')

print("\n[CREDENTIAL CHECK]")
print(f"API Key: {'SET' if api_key else 'NOT SET'} ({api_key[:20] + '...' if api_key else 'None'})")
print(f"Private Key Path: {'SET' if private_key_path else 'NOT SET'} ({private_key_path})")
print(f"Private Key File Exists: {os.path.exists(private_key_path) if private_key_path else False}")
print(f"Email: {'SET' if email else 'NOT SET'} ({email})")
print(f"Password: {'SET' if password else 'NOT SET'}")

# Test endpoints
print("\n" + "="*80)
print("TESTING API ENDPOINTS")
print("="*80)

# Test 1: Public markets endpoint (no auth)
print("\n[TEST 1] Public Markets Endpoint (no auth)")
try:
    url = "https://api.elections.kalshi.com/trade-api/v2/markets?limit=1"
    response = requests.get(url, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: Trading API endpoint
print("\n[TEST 2] Trading API Endpoint (no auth)")
try:
    url = "https://trading-api.kalshi.com/trade-api/v2/markets?limit=1"
    response = requests.get(url, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:200]}")
except Exception as e:
    print(f"Error: {e}")

# Test 3: Email/Password Login (if credentials available)
if email and password:
    print("\n[TEST 3] Email/Password Login")
    try:
        url = "https://trading-api.kalshi.com/trade-api/v2/login"
        headers = {
            "accept": "application/json",
            "content-type": "application/json"
        }
        body = {
            "email": email,
            "password": password
        }
        response = requests.post(url, headers=headers, json=body, timeout=10)
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            token = data.get('token', 'No token in response')
            print(f"SUCCESS! Token: {token[:50]}...")

            # Test authenticated request
            print("\n[TEST 4] Authenticated Market Request")
            markets_url = "https://trading-api.kalshi.com/trade-api/v2/markets?limit=5"
            auth_headers = {
                "accept": "application/json",
                "Authorization": f"Bearer {token}"
            }
            markets_response = requests.get(markets_url, headers=auth_headers, timeout=10)
            print(f"Status Code: {markets_response.status_code}")

            if markets_response.status_code == 200:
                markets_data = markets_response.json()
                markets_count = len(markets_data.get('markets', []))
                print(f"SUCCESS! Retrieved {markets_count} markets")
                print(f"Sample: {markets_response.text[:300]}")
            else:
                print(f"Error: {markets_response.text[:200]}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
else:
    print("\n[TEST 3] Email/Password Login - SKIPPED (no credentials)")

print("\n" + "="*80)
print("RECOMMENDATIONS")
print("="*80)

if not email or not password:
    print("""
To use Kalshi integration, you need to set up authentication.

OPTION 1 (RECOMMENDED): Email/Password Authentication
Add to your .env file:
    KALSHI_EMAIL=your_email@example.com
    KALSHI_PASSWORD=your_password

This is the standard method that works with the Kalshi API.

OPTION 2: Contact Kalshi Support
If you were given an API key and private key, you may need to:
- Verify these are for the correct API (production vs demo)
- Ask Kalshi support for documentation on API key authentication
- Confirm the authentication flow for RSA-signed requests

""")
elif email and password:
    print("""
Good news! Your email/password credentials are configured.
The tests above should show if authentication is working.

Next steps:
1. If authentication succeeded, run the full sync:
   python sync_kalshi_complete.py

2. If authentication failed, verify your credentials are correct
   and that your Kalshi account is active.
""")

print("="*80)
