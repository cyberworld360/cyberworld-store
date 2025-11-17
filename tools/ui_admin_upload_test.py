"""
Simple script to test admin login and upload images via HTTP (no browser required).
- Logs in as admin via POST /admin/login
- Posts a small PNG to /admin/settings with field `logo_file`

Usage (local):
  1. Run the app locally: `python app.py` (default on http://127.0.0.1:5000)
  2. In another shell run: `python tools/ui_admin_upload_test.py http://127.0.0.1:5000 Cyberjnr GITG360$`

Usage (deployed):
  Replace base_url with deployed URL, and ensure admin credentials and session are valid.

Note: This script does NOT navigate the UI; it uses the same endpoints the admin UI uses.
"""

import sys
import requests
import base64
from io import BytesIO

if len(sys.argv) < 4:
    print("Usage: python tools/ui_admin_upload_test.py <base_url> <admin_username> <admin_password>")
    sys.exit(1)

base = sys.argv[1].rstrip('/')
admin_user = sys.argv[2]
admin_pass = sys.argv[3]

s = requests.Session()

print('[1] Logging in as admin...')
login_url = f"{base}/admin/login"
resp = s.post(login_url, data={'username': admin_user, 'password': admin_pass})
print('  -> status:', resp.status_code)
if resp.status_code != 200 and resp.status_code != 302:
    print('Login may have failed. Response length:', len(resp.text))

print('[2] Uploading test logo to /admin/settings')
settings_url = f"{base}/admin/settings"
# generate a tiny PNG (1x1 transparent) in memory
png_bytes = base64.b64decode(
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVQImWNgYAAAAAMAAWgmWQ0AAAAASUVORK5CYII=')
files = {'logo_file': ('test.png', BytesIO(png_bytes), 'image/png')}
# Include some form fields required by settings handler
data = {'primary_color': '#27ae60', 'secondary_color': '#2c3e50', 'dashboard_layout': 'grid'}
resp2 = s.post(settings_url, files=files, data=data)
print('  -> upload status:', resp2.status_code)
if resp2.status_code == 200 or resp2.status_code == 302:
    print('  ✓ Upload request sent. Check admin diagnostics or public site for the new logo.')
else:
    print('  ✗ Upload may have failed. Response length:', len(resp2.text))

print('[3] Fetch admin diagnostics to verify upload/keys...')
diag_url = f"{base}/admin/diagnostics"
rd = s.get(diag_url)
print('  -> diagnostics status:', rd.status_code)
if rd.status_code == 200:
    # Print a snippet to verify fields
    txt = rd.text
    for key in ['PAYSTACK_CALLBACK', 'PAYSTACK_SECRET_CONFIGURED', 'PRODUCT_COUNT', 'SETTINGS_HAS_LOGO_DB']:
        if key in txt:
            start = txt.find(key)
            snippet = txt[start:start+200]
            print('\n  snippet:', snippet)
else:
    print('  ✗ Failed to fetch diagnostics. You may need to login via the web UI first.')
