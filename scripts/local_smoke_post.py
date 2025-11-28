import requests
from urllib.parse import urljoin
import sys
from time import sleep

base = 'http://127.0.0.1:5000'

s = requests.Session()
print('Login...')
try:
    resp = s.post(urljoin(base, '/admin/login'), data={'username':'Cyberjnr', 'password':'GITG360$'}, timeout=10)
    print('login', resp.status_code)
    print('cookie headers:', resp.headers.get('Set-Cookie'))
except Exception as e:
    print('Login failed:', e)
    sys.exit(1)

# Slight delay to ensure session stabilizes
sleep(0.5)

try:
    resp = s.get(urljoin(base, '/admin/settings'), timeout=10)
    print('get settings', resp.status_code)
    print(resp.text[:200])
except Exception as e:
    print('GET /admin/settings failed:', e); sys.exit(1)

# Post settings without files
try:
    resp = s.post(urljoin(base, '/admin/settings'), data={'primary_color':'#ffffff','secondary_color':'#000000'}, allow_redirects=False, timeout=10)
    print('post settings status (no file):', resp.status_code)
    print('headers:', resp.headers)
    if resp.status_code >= 400:
        print('Response:', resp.text[:800])
except Exception as e:
    print('POST /admin/settings failed (no file):', e)

# Post settings with a small file upload
fp = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR'
files = {'logo_file': ('logo.png', fp, 'image/png')}
try:
    resp2 = s.post(urljoin(base, '/admin/settings'), data={'primary_color':'#ffffff'}, files=files, timeout=10)
    print('post settings status (with file):', resp2.status_code)
    print('headers2:', resp2.headers)
    if resp2.status_code >= 400:
        print(resp2.text[:800])
except Exception as e:
    print('POST /admin/settings failed (with file):', e)

print('Done')