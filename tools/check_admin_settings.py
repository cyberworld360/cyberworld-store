import requests
from bs4 import BeautifulSoup

BASE = 'https://cyberworld-store-o5yterqrh-cyber-shop360.vercel.app'
LOGIN = BASE + '/admin/login'
SETTINGS = BASE + '/admin/settings'

s = requests.Session()
# first GET to obtain any cookies
r = s.get(LOGIN, timeout=15)
print('GET /admin/login', r.status_code)

payload = {'username':'admin','password':'GITG360'}
r = s.post(LOGIN, data=payload, allow_redirects=True, timeout=15)
print('POST /admin/login', r.status_code, '->', r.url)

r = s.get(SETTINGS, timeout=15)
print('GET /admin/settings', r.status_code)
if r.status_code != 200:
    print('Failed to fetch admin settings page')
    print(r.text[:1000])
    raise SystemExit(1)

soup = BeautifulSoup(r.text, 'html.parser')
# dashboard layout
sel = soup.find('select', {'id': 'dashboard_layout'})
layout = None
if sel:
    opt = sel.find('option', selected=True)
    if opt:
        layout = opt.get('value')

seo_visible = bool(soup.find('input', {'id':'seo_visible', 'checked':True}))
announcement = ''
area = soup.find('textarea', {'id':'site_announcement'})
if area:
    announcement = area.text.strip()

print('dashboard_layout =', layout)
print('seo_visible =', seo_visible)
print('site_announcement =', repr(announcement[:200]))
