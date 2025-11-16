#!/usr/bin/env python3
"""
Verify that the deployed production site has the new /admin/settings/api route.

Usage:
    python tools/verify_production_route.py [--url URL] [--token TOKEN]

Examples:
    python tools/verify_production_route.py
    python tools/verify_production_route.py --url https://www.cyberworldstore.shop --token our-FATHER-360
"""
import os
import sys
import argparse
import requests
import json
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def load_dotenv(path: str = ".env"):
    """Load .env file manually."""
    env_path = Path(path)
    if not env_path.exists():
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

load_dotenv()

LIVE_DOMAIN = os.environ.get("LIVE_DOMAIN", "https://www.cyberworldstore.shop").strip()
ADMIN_API_TOKEN = os.environ.get("ADMIN_API_TOKEN", "our-FATHER-360").strip()

def test_route(url: str, token: str, method: str = "GET", data: dict = None) -> tuple:
    """
    Test a route on the production server.
    
    Returns: (status_code, response_json_or_text, error_msg_or_none)
    """
    headers = {
        "X-ADMIN-TOKEN": token,
        "Content-Type": "application/json"
    }
    
    print(f"\n[INFO] Testing {method} {url}")
    print(f"[INFO] Token: {token[:10]}...")
    
    try:
        if method == "GET":
            resp = requests.get(url, headers=headers, timeout=10, verify=True)
        elif method == "POST":
            resp = requests.post(url, headers=headers, json=data or {}, timeout=10, verify=True)
        else:
            return None, None, f"Unsupported method: {method}"
        
        print(f"[INFO] Status Code: {resp.status_code}")
        
        try:
            resp_data = resp.json()
            return resp.status_code, resp_data, None
        except Exception:
            return resp.status_code, resp.text, None
    
    except requests.exceptions.Timeout:
        return None, None, "Request timeout (10s)"
    except requests.exceptions.ConnectionError as e:
        return None, None, f"Connection error: {e}"
    except requests.exceptions.RequestException as e:
        return None, None, f"Request error: {e}"

def main():
    parser = argparse.ArgumentParser(
        description="Verify production deployment has the /admin/settings/api route."
    )
    parser.add_argument("--url", default=LIVE_DOMAIN, help=f"Production domain (default: {LIVE_DOMAIN})")
    parser.add_argument("--token", default=ADMIN_API_TOKEN, help="Admin API token")
    args = parser.parse_args()
    
    print("="*80)
    print(" PRODUCTION ROUTE VERIFICATION")
    print("="*80)
    
    base_url = args.url.rstrip('/')
    api_url = f"{base_url}/admin/settings/api"
    
    # Test 1: GET current settings
    print(f"\n[TEST 1] GET {api_url}")
    print("-" * 80)
    status, resp_data, error = test_route(api_url, args.token, "GET")
    
    if error:
        print(f"[ERROR] {error}")
        print("[INFO] This likely means:")
        print("  - Production domain is unreachable")
        print("  - Route is not deployed yet")
        print("  - Firewall/WAF is blocking requests")
    elif status == 200:
        print(f"[SUCCESS] Route found! Status 200")
        print(f"[SUCCESS] Response:")
        if isinstance(resp_data, dict):
            print(json.dumps(resp_data, indent=2))
        else:
            print(resp_data[:500])
    elif status == 404:
        print(f"[ERROR] Route not found (404)")
        print("[INFO] This means:")
        print("  - Latest code may not be deployed yet")
        print("  - Build may have failed")
        print("  - Vercel is still routing to older deployment")
    elif status == 403:
        print(f"[ERROR] Forbidden (403)")
        print("[INFO] This could mean:")
        print("  - Token is invalid or expired")
        print("  - Vercel edge security is blocking requests")
    else:
        print(f"[ERROR] Unexpected status: {status}")
        print(f"[RESPONSE] {resp_data}")
    
    # Test 2: Try POST with test data (if GET succeeded)
    if status == 200:
        print(f"\n[TEST 2] POST to {api_url} with test data")
        print("-" * 80)
        test_data = {
            "dashboard_layout": "grid",
            "seo_visible": True,
            "site_announcement": "Deployment verification test"
        }
        status2, resp_data2, error2 = test_route(api_url, args.token, "POST", test_data)
        
        if error2:
            print(f"[ERROR] {error2}")
        elif status2 == 200:
            print(f"[SUCCESS] POST succeeded! Status 200")
            if isinstance(resp_data2, dict):
                print(json.dumps(resp_data2, indent=2))
        else:
            print(f"[ERROR] Unexpected status: {status2}")
            if isinstance(resp_data2, dict):
                print(json.dumps(resp_data2, indent=2))
            else:
                print(resp_data2[:500])
    
    # Test 3: Check home page (sanity check)
    print(f"\n[TEST 3] Sanity check - GET {base_url}/")
    print("-" * 80)
    try:
        resp = requests.get(f"{base_url}/", timeout=10, verify=True)
        print(f"[INFO] Status: {resp.status_code}")
        if resp.status_code == 200:
            print(f"[SUCCESS] Home page is reachable")
        else:
            print(f"[ERROR] Home page returned {resp.status_code}")
    except Exception as e:
        print(f"[ERROR] Cannot reach home page: {e}")
    
    # Summary
    print("\n" + "="*80)
    print(" VERIFICATION SUMMARY")
    print("="*80)
    
    if status == 200:
        print("\n✅ DEPLOYMENT VERIFIED")
        print("   - /admin/settings/api route is accessible")
        print("   - Latest code appears to be deployed")
    elif status == 404:
        print("\n❌ DEPLOYMENT NOT FOUND")
        print("   - Route returns 404, likely not deployed yet")
        print("   - Check Vercel build logs with: python tools/check_vercel_deployment.py --logs")
    else:
        print(f"\n⚠️  UNCERTAIN STATUS: {status}")
        print("   - Route may be blocked or returning unexpected status")
    
    print(f"\n[INFO] Production URL: {args.url}")
    print(f"[INFO] API Endpoint: {api_url}")
    
    sys.exit(0 if status == 200 else 1)

if __name__ == "__main__":
    main()
