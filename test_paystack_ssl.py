#!/usr/bin/env python
"""
Test Paystack initialization with SSL options
"""
import os
import sys
from pathlib import Path
import uuid
import requests

# Add the app directory to sys.path
sys.path.insert(0, str(Path(__file__).parent))

# Load .env manually
def load_dotenv(path: str = ".env"):
    env_path = Path(path)
    if not env_path.exists():
        print(f"[ERROR] {path} not found!")
        return
    
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, val = line.split("=", 1)
        key = key.strip()
        val = val.strip()
        if val and val[0] == '"' and val[-1] == '"':
            val = val[1:-1]
        if key and key not in os.environ:
            os.environ[key] = val

# Load .env
load_dotenv()

# Check Paystack secret
PAYSTACK_SECRET = os.environ.get("PAYSTACK_SECRET_KEY")
print(f"[INFO] PAYSTACK_SECRET_KEY: {PAYSTACK_SECRET[:20] if PAYSTACK_SECRET else 'NOT LOADED'}...")

# Test data
initialize_url = "https://api.paystack.co/transaction/initialize"
headers = {
    "Authorization": f"Bearer {PAYSTACK_SECRET}",
    "Content-Type": "application/json"
}

reference = "test-" + str(uuid.uuid4())
payload = {
    "email": "test@example.com",
    "amount": 10000,
    "reference": reference,
    "callback_url": "http://127.0.0.1:5000/paystack/callback"
}

print(f"\n[INFO] Test 1: Request with SSL verification enabled (default)")
try:
    response = requests.post(initialize_url, json=payload, headers=headers, timeout=15)
    print(f"[SUCCESS] Status: {response.status_code}")
    print(f"[SUCCESS] Response: {response.text[:300]}")
except Exception as e:
    print(f"[FAILED] {type(e).__name__}: {e}")

print(f"\n[INFO] Test 2: Request with SSL verification disabled")
try:
    response = requests.post(initialize_url, json=payload, headers=headers, timeout=15, verify=False)
    print(f"[SUCCESS] Status: {response.status_code}")
    print(f"[SUCCESS] Response: {response.text[:300]}")
except Exception as e:
    print(f"[FAILED] {type(e).__name__}: {e}")

print(f"\n[INFO] Test 3: Simple GET to Paystack API")
try:
    response = requests.get("https://api.paystack.co/customer", headers=headers, timeout=15)
    print(f"[SUCCESS] Status: {response.status_code}")
    print(f"[SUCCESS] Response: {response.text[:300]}")
except Exception as e:
    print(f"[FAILED] {type(e).__name__}: {e}")
