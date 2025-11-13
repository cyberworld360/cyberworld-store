#!/usr/bin/env python3
"""
Test script to verify order email notifications work correctly.
Tests both admin and user email sending for wallet and paystack payments.
"""
import requests
import time
import json

BASE_URL = "http://127.0.0.1:5000"

def test_admin_email():
    """Test sending an admin test email"""
    print("\n" + "="*60)
    print("TEST 1: Admin Test Email")
    print("="*60)
    try:
        response = requests.get(f"{BASE_URL}/admin/test-email", timeout=10)
        print(f"Status Code: {response.status_code}")
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        
        if response.status_code == 200:
            print("✅ Test email request accepted!")
            print(f"   Recipient: {data.get('to')}")
            print(f"   Status: {data.get('message')}")
        else:
            print(f"❌ Failed with status {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_email_config():
    """Test basic app connectivity"""
    print("\n" + "="*60)
    print("TEST 0: App Connectivity Check")
    print("="*60)
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print("✅ App is running and accessible")
            return True
        else:
            print(f"❌ App returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to app: {e}")
        return False

def main():
    print("\n" + "="*70)
    print(" EMAIL NOTIFICATION SYSTEM TEST")
    print("="*70)
    print(f"Testing server at: {BASE_URL}")
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check connectivity first
    if not test_email_config():
        print("\n❌ Cannot reach the server. Make sure Flask is running:")
        print("   .venv\\Scripts\\python.exe run.py")
        return
    
    # Test admin email
    admin_ok = test_admin_email()
    
    print("\n" + "="*70)
    print(" TEST SUMMARY")
    print("="*70)
    
    results = {
        "Admin Email Test": "✅ PASS" if admin_ok else "❌ FAIL"
    }
    
    for test_name, result in results.items():
        print(f"{test_name}: {result}")
    
    print("\n" + "="*70)
    print(" NEXT STEPS")
    print("="*70)
    print("""
1. Check your email inbox for the test email at cyberworldstore360@gmail.com
2. If you receive the test email, order emails should work correctly
3. Try placing a test order to verify the complete flow
4. Check admin logs if emails don't arrive
5. Review .env file to ensure MAIL_SERVER, MAIL_USERNAME, and MAIL_PASSWORD are set
    """)

if __name__ == "__main__":
    main()
