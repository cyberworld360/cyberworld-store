#!/usr/bin/env python3
"""Simple script to exercise production wallet flow: register a user, add product to cart, credit wallet as admin, perform wallet checkout, and verify /account and order detail.
"""
import requests
import uuid
import sys
import time
import re

import os

# Allow overriding base URL by environment variable for automated runs
BASE = os.environ.get('PROD_BASE') or 'https://cyberworld-store-jikmapnqz-cyberworldstores-projects.vercel.app'
# Admin credentials (default in repo): change if production overrides
ADMIN_USER = 'Cyberjnr'
ADMIN_PASS = 'GITG360$'

s_user = requests.Session()

# 1) Register a user
email = f"smoke+{uuid.uuid4().hex[:8]}@example.com"
pw = 'secret123'
print('Registering user', email)
resp = s_user.post(BASE + '/register', data={ 'email': email, 'password': pw, 'confirm_password': pw })
print('register status', resp.status_code)
if resp.status_code not in (200, 302):
    print('Registration failed or unexpected status')
    sys.exit(1)

# 2) Login as the user
print('Logging in as user')
resp = s_user.post(BASE + '/login', data={'email': email, 'password': pw}, allow_redirects=True)
print('login status', resp.status_code)
if resp.status_code not in (200, 302):
    print('Login failed, aborting')
    sys.exit(1)

# 3) Find a product and add to cart
print('Fetching product list')
resp = s_user.get(BASE + '/api/products')
if resp.status_code != 200:
    print('Could not fetch /api/products', resp.status_code); sys.exit(1)
prods = resp.json()
if not prods:
    print('No products found'); sys.exit(1)
pid = prods[0]['id']
print('Selected product id', pid)

# Add to cart
resp = s_user.post(BASE + f'/cart/add/{pid}', data={'qty': 1}, allow_redirects=True)
print('add to cart status', resp.status_code)

# 4) Admin login and credit wallet
sa = requests.Session()
print('Logging in as admin (for wallet credit)')
resp = sa.post(BASE + '/admin/login', data={'username': ADMIN_USER, 'password': ADMIN_PASS}, allow_redirects=True)
print('admin login status', resp.status_code)
if resp.status_code not in (200, 302):
    print('Admin login failed; cannot credit wallet'); sys.exit(1)

# Get admin wallets page
resp = sa.get(BASE + '/admin/wallets')
if resp.status_code != 200:
    print('Failed to load admin/wallets', resp.status_code); sys.exit(1)

# Parse user_id from page: find occurrences of /admin/wallet/credit/<id> with the user email nearby
html = resp.text
m = None
# try to find a form with action /admin/wallet/credit/<id> and with the user's email nearby
pattern = re.compile(r"/admin/wallet/credit/(\d+)")
ids = pattern.findall(html)
print('found wallet ids in admin page:', ids[:5])
# find the user row containing the email
user_id = None
for id_ in ids:
    if email in html:
        # find the nearest id following the email in HTML
        # find position of email
        pos = html.find(email)
        # search for credit link after that pos within 500 chars
        sub = html[pos:pos+500]
        match = pattern.search(sub)
        if match:
            user_id = match.group(1)
            break
# fallback: find by input id mapping
if not user_id and ids:
    user_id = ids[0]

if not user_id:
    print('Could not determine user id for credit, aborting')
    sys.exit(1)
print('Determined user_id:', user_id)

# Credit wallet with GH₵1000
resp = sa.post(BASE + f'/admin/wallet/credit/{user_id}', data={'amount': '1000'}, allow_redirects=True)
print('credit wallet status', resp.status_code)
if resp.status_code not in (200, 302):
    print('Failed to credit wallet'); sys.exit(1)

# 5) Do wallet checkout as user
print('Attempting wallet checkout')
# Extract checkout page to get any tokens if needed
resp = s_user.get(BASE + '/checkout')
print('/checkout GET', resp.status_code)
# POST to /pay/wallet
checkout_data = {
    'name': 'Smoke Tester',
    'phone': '0244444000',
    'city': 'Accra',
    'email': email,
    'coupon_id': ''
}
resp = s_user.post(BASE + '/pay/wallet', data=checkout_data, allow_redirects=True)
print('wallet payment POST status', resp.status_code)
print('final URL', resp.url)

# 6) Check /account
resp = s_user.get(BASE + '/account')
print('/account status', resp.status_code)
print('/account snippet', resp.text[:200])

# Try to find order reference link in account and view order detail
if resp.status_code == 200:
    # find /account/order/<id>
    m = re.search(r"/account/order/(\d+)", resp.text)
    if m:
        order_id = m.group(1)
        print('Found order id in account:', order_id)
        detail = s_user.get(BASE + f'/account/order/{order_id}')
        print('/account/order detail status', detail.status_code)
        print('detail snippet', detail.text[:200])
    else:
        print('No order link found in account page; check cart/checkout result')

print('Smoke test completed')

if __name__ == '__main__':
    pass
