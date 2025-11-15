import requests
from bs4 import BeautifulSoup

BASE = 'https://www.cyberworldstore.shop'

endpoints = ['/', '/admin/login', '/admin/settings']

s = requests.Session()

for ep in endpoints:
    url = BASE.rstrip('/') + ep
    try:
        r = s.get(url, timeout=15)
        print(f'GET {ep} ->', r.status_code, url)
        txt = r.text[:600].strip()
        print('--- snippet ---')
        print(txt)
        print('---------------\n')
    except Exception as e:
        print(f'GET {ep} -> ERROR: {e}')

# Try logging in as admin and re-check /admin/settings
try:
    print('Attempting admin login...')
    r = s.post(BASE + '/admin/login', data={'username':'admin','password':'GITG360'}, allow_redirects=True, timeout=15)
    print('POST /admin/login ->', r.status_code, r.url)
    r2 = s.get(BASE + '/admin/settings', timeout=15)
    print('GET /admin/settings after login ->', r2.status_code, r2.url)
    print('settings snippet:\n', r2.text[:800])
except Exception as e:
    print('Admin login check error:', e)
