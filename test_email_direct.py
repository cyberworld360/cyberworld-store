#!/usr/bin/env python3
"""
Direct test of email functions without going through HTTP.
This tests the core email sending functionality.
"""
import os
import sys
sys.path.insert(0, os.getcwd())

# Load environment
from app import load_dotenv, MAIL_SERVER, MAIL_USERNAME, MAIL_PASSWORD, ADMIN_EMAIL, send_html_email, send_html_email_async, is_valid_email

print("\n" + "="*70)
print(" EMAIL CONFIGURATION CHECK")
print("="*70)

print(f"\n✓ MAIL_SERVER: {MAIL_SERVER}")
print(f"✓ MAIL_USERNAME: {MAIL_USERNAME}")
print(f"✓ MAIL_PASSWORD set: {'Yes' if MAIL_PASSWORD else 'No'}")
print(f"✓ ADMIN_EMAIL: {ADMIN_EMAIL}")

print("\n" + "="*70)
print(" TESTING EMAIL SENDING FUNCTIONS")
print("="*70)

# Test 1: Email validation
print(f"\nTest 1: Email Validation")
test_email = "test@example.com"
invalid_email = "not-an-email"
print(f"  Valid email '{test_email}': {is_valid_email(test_email)}")
print(f"  Invalid email '{invalid_email}': {is_valid_email(invalid_email)}")

# Test 2: Send test email to admin
print(f"\nTest 2: Sending test email to admin")
subject = "[TEST] Email System Check"
html_body = """
<html><body style="font-family:Arial,sans-serif;">
    <div style="background-color:#e8f5e9; padding:20px; border-radius:4px;">
        <h2>✅ Email System Test</h2>
        <p>If you receive this email, the order notification system is working correctly!</p>
        <p><strong>Configuration:</strong></p>
        <ul>
            <li>MAIL_SERVER: {}</li>
            <li>MAIL_USERNAME: {}</li>
            <li>ADMIN_EMAIL: {}</li>
        </ul>
    </div>
</body></html>
""".format(MAIL_SERVER, MAIL_USERNAME, ADMIN_EMAIL)

plain_text = "Email System Test\n\nIf you receive this, the order notification system is working!"

try:
    result = send_html_email(ADMIN_EMAIL, subject, html_body, plain_text)
    print(f"  Result: {'✅ SUCCESS' if result else '❌ FAILED'}")
    if result:
        print(f"  Email sent to: {ADMIN_EMAIL}")
    else:
        print(f"  Check email configuration or SMTP settings")
except Exception as e:
    print(f"  ❌ ERROR: {e}")

print("\n" + "="*70)
print(" VERIFICATION STEPS")
print("="*70)
print("""
1. Check your email (cyberworldstore360@gmail.com) for the test email
2. If received, order emails should work correctly
3. Review .env file settings if not received:
   - MAIL_SERVER should be 'smtp.gmail.com'
   - MAIL_PORT should be 465
   - MAIL_USE_SSL should be true
   - MAIL_USERNAME and MAIL_PASSWORD must be set
4. Run the app and test checkout with wallet/Paystack payment
""")
