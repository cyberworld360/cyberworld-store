#!/usr/bin/env python
"""
Direct test of Paystack initialization without Flask server
"""
import os
import sys
from pathlib import Path
import uuid

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
print(f"[INFO] PAYSTACK_SECRET_KEY loaded: {PAYSTACK_SECRET[:20]}..." if PAYSTACK_SECRET else "[ERROR] PAYSTACK_SECRET_KEY not loaded!")

# Now test the API call
try:
    import requests
    print("[INFO] requests module imported successfully")
    
    # Test data
    initialize_url = "https://api.paystack.co/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET}",
        "Content-Type": "application/json"
    }
    
    reference = "test-" + str(uuid.uuid4())
    payload = {
        "email": "test@example.com",
        "amount": 10000,  # 100 GHS
        "reference": reference,
        "callback_url": "http://127.0.0.1:5000/paystack/callback"
    }
    
    print(f"\n[INFO] Testing Paystack API with reference: {reference}")
    print(f"[INFO] URL: {initialize_url}")
    print(f"[INFO] Headers: {headers}")
    print(f"[INFO] Payload: {payload}\n")
    
    response = requests.post(initialize_url, json=payload, headers=headers, timeout=15)
    print(f"[INFO] Response status: {response.status_code}")
    print(f"[INFO] Response text: {response.text}\n")
    
    if response.status_code == 200:
        data = response.json()
        print(f"[SUCCESS] Paystack initialized successfully!")
        print(f"[SUCCESS] Authorization URL: {data.get('data', {}).get('authorization_url')}")
        print(f"[SUCCESS] Access Code: {data.get('data', {}).get('access_code')}")
    else:
        print(f"[FAILED] Status code: {response.status_code}")
        print(f"[FAILED] Response: {response.text}")
        
except Exception as e:
    print(f"[ERROR] {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
