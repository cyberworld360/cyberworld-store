import requests
from urllib.parse import urljoin

base = 'https://cyberworld-store-a0he3v81h-cyberworldstores-projects.vercel.app'

import sys
import traceback

s = requests.Session()
login_url = urljoin(base, '/admin/login')
try:
    resp = s.post(login_url, data={'username':'Cyberjnr', 'password':'GITG360$'}, timeout=10)
    print('login', resp.status_code)
except Exception as e:
    print('Login failed:', e)
    traceback.print_exc()
    sys.exit(1)

# Check status
try:
    resp = s.get(urljoin(base, '/admin/settings'), timeout=10)
    print('get settings', resp.status_code)
except Exception as e:
    print('GET /admin/settings failed:', e)
    traceback.print_exc()
    sys.exit(1)

# Post settings without files
try:
    resp = s.post(urljoin(base, '/admin/settings'), data={'primary_color':'#ffffff','secondary_color':'#000000'}, allow_redirects=False, timeout=10)
    print('post settings status (no file):', resp.status_code)
    print('headers:', resp.headers)
    if resp.status_code >= 400:
        print(resp.text[:800])
        # Try to retrieve last server-side traceback if ERROR_VIEW_TOKEN set
        import os
        token = os.environ.get('ERROR_VIEW_TOKEN')
        if token:
            try:
                last_err = s.get(urljoin(base, f'/__last_error?token={token}'), timeout=5)
                print('\n--- last_error trace ---')
                print(last_err.text[:4000])
            except Exception:
                pass
except Exception as e:
    print('POST /admin/settings failed (no file):', e)
    traceback.print_exc()

# Post settings with a small file upload
fp = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR'
files = {'logo_file': ('logo.png', fp, 'image/png')}
try:
    resp2 = s.post(urljoin(base, '/admin/settings'), data={'primary_color':'#ffffff'}, files=files, timeout=10)
    print('post settings status (with file):', resp2.status_code)
    print('headers2:', resp2.headers)
    if resp2.status_code >= 400:
        print(resp2.text[:800])
        import os
        token = os.environ.get('ERROR_VIEW_TOKEN')
        if token:
            try:
                last_err = s.get(urljoin(base, f'/__last_error?token={token}'), timeout=5)
                print('\n--- last_error trace ---')
                print(last_err.text[:4000])
            except Exception:
                pass
except Exception as e:
    print('POST /admin/settings failed (with file):', e)
    traceback.print_exc()
