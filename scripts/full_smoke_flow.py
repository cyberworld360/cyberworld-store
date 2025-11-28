import requests
from urllib.parse import urljoin

base = 'http://127.0.0.1:5000'

s = requests.Session()

# Register a user
email = 'smoketest@example.com'
password = 'smoketestpass'
print('Registering user...')
resp = s.post(urljoin(base, '/register'), data={'email':email, 'password':password, 'confirm_password':password}, timeout=10)
print('register status', resp.status_code)

# Login user
print('Logging in user...')
resp = s.post(urljoin(base, '/login'), data={'email':email, 'password':password}, allow_redirects=False, timeout=10)
print('user login status', resp.status_code)

# Ensure product exists - GET products list
resp = s.get(urljoin(base, '/api/products'))
products = resp.json() if resp.ok else []
print('products count', len(products))
if not products:
    print('No products found; get admin to add one (skipping)')
    # We can still check /checkout shows empty cart

# Add product to cart
if products:
    pid = products[0]['id']
    resp = s.post(urljoin(base, f'/cart/add/{pid}'), data={'qty':'1'}, allow_redirects=False, timeout=10)
    print('add to cart status', resp.status_code)

    # Attempt wallet payment (requires balance) - prepare details
    resp_pay = s.post(urljoin(base, '/pay/wallet'), data={
        'name': 'Smoke Test User',
        'email': email,
        'phone': '0244000000',
        'city': 'Accra',
        'coupon_id': ''
    }, allow_redirects=False, timeout=10)
    print('wallet payment status', resp_pay.status_code)
    if resp_pay.status_code >= 400:
        print('wallet payment response length:', len(resp_pay.text))

# Attempt checkout page
resp = s.get(urljoin(base, '/checkout'), timeout=10)
print('/checkout', resp.status_code)

# Attempt to use wallet by ensuring wallet has balance via admin login
admin = requests.Session()
print('Admin login...')
resp = admin.post(urljoin(base, '/admin/login'), data={'username':'Cyberjnr', 'password':'GITG360$'}, timeout=10)
print('admin login', resp.status_code)

# Credit the user wallet (api route)
# Find user ID via admin list? We can call /admin/wallets but need to parse HTML. Using API is non-existent.
# For simplicity: print response codes then finish
print('Done')
