import requests
from bs4 import BeautifulSoup

BASE = 'https://www.cyberworldstore.shop'
LOGIN = BASE + '/admin/login'
SETTINGS = BASE + '/admin/settings'

s = requests.Session()
r = s.get(LOGIN, timeout=15)
print('GET /admin/login:', r.status_code)

payload = {'username': 'admin', 'password': 'GITG360'}
r = s.post(LOGIN, data=payload, allow_redirects=True, timeout=15)
print('POST login:', r.status_code, r.url)

r = s.get(SETTINGS, timeout=15)
if r.status_code != 200:
    print('Failed to GET settings:', r.status_code)
    raise SystemExit(1)

soup = BeautifulSoup(r.text, 'html.parser')
form_data = {}
for inp in soup.find_all(['input', 'textarea', 'select']):
    name = inp.get('name')
    if not name:
        continue
    if inp.name == 'textarea':
        form_data[name] = inp.text or ''
    elif inp.name == 'select':
        opt = inp.find('option', selected=True)
        form_data[name] = opt.get('value') if opt else ''
    elif inp.get('type') in ('checkbox', 'radio'):
        if inp.has_attr('checked'):
            form_data[name] = inp.get('value', 'on')
    else:
        form_data[name] = inp.get('value', '')

# Set desired values
form_data['dashboard_layout'] = 'grid'
form_data['seo_visible'] = 'on'
for k in ['site_title', 'meta_tags', 'robots_txt', 'mobile_friendly', 'page_speed', 'ssl_enabled']:
    form_data[k] = 'on'
form_data['site_announcement'] = '<p>Welcome to Cyber World Store — automation test</p>'

print('Posting settings...')
r2 = s.post(SETTINGS, data=form_data, allow_redirects=True, timeout=15)
print('POST /admin/settings:', r2.status_code, r2.url)

# Verify
r3 = s.get(SETTINGS, timeout=15)
if r3.status_code == 200:
    soup2 = BeautifulSoup(r3.text, 'html.parser')
    sel = soup2.find('select', {'id': 'dashboard_layout'})
    opt = sel.find('option', selected=True) if sel else None
    layout = opt.get('value') if opt else None
    seo_visible = bool(soup2.find('input', {'id': 'seo_visible', 'checked': True}))
    area = soup2.find('textarea', {'id': 'site_announcement'})
    announcement = (area.text.strip() if area else '')[:60]
    print(f'Result: layout={layout}, seo_visible={seo_visible}, announcement={announcement}')
