"""
Test Kalshi API Key Authentication
"""
import os
import time
import requests
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
import base64
from dotenv import load_dotenv

load_dotenv()

# Load credentials
api_key = os.getenv('KALSHI_API_KEY')
private_key_path = os.getenv('KALSHI_PRIVATE_KEY_PATH')

print(f"API Key: {api_key}")
print(f"Private Key Path: {private_key_path}")
print()

# Load private key
with open(private_key_path, 'rb') as key_file:
    private_key = serialization.load_pem_private_key(
        key_file.read(),
        password=None,
        backend=default_backend()
    )

print("OK: Private key loaded")
print()

# Create signature
timestamp = str(int(time.time() * 1000))
method = "GET"
path = "/markets"
body = ""

# Create signing string
signing_string = f"{timestamp}{method}{path}{body}"
print(f"Signing string: {signing_string}")

# Sign with SHA-256
signature = private_key.sign(
    signing_string.encode('utf-8'),
    padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.MAX_LENGTH
    ),
    hashes.SHA256()
)

# Base64 encode
signature_b64 = base64.b64encode(signature).decode('utf-8')
print(f"Signature (first 50 chars): {signature_b64[:50]}...")
print()

# Test request
base_url = "https://api.elections.kalshi.com/trade-api/v2"
url = f"{base_url}{path}"

headers = {
    "accept": "application/json",
    "KALSHI-ACCESS-KEY": api_key,
    "KALSHI-ACCESS-SIGNATURE": signature_b64,
    "KALSHI-ACCESS-TIMESTAMP": timestamp
}

print(f"Making request to: {url}")
print(f"Headers: KALSHI-ACCESS-KEY={api_key}")
print(f"         KALSHI-ACCESS-TIMESTAMP={timestamp}")
print(f"         KALSHI-ACCESS-SIGNATURE={signature_b64[:30]}...")
print()

try:
    print("Sending request...")
    response = requests.get(url, headers=headers, params={"limit": 5}, timeout=15)

    print(f"Status Code: {response.status_code}")
    print(f"Response Length: {len(response.text)} chars")
    print()

    if response.status_code == 200:
        data = response.json()
        markets = data.get('markets', [])
        print(f"SUCCESS! Got {len(markets)} markets")
        if markets:
            print(f"\nFirst market: {markets[0].get('ticker', '?')} - {markets[0].get('title', '?')}")
    else:
        print(f"✗ FAILED!")
        print(f"Response: {response.text[:500]}")

except Exception as e:
    print(f"✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
