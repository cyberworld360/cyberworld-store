import requests
from bs4 import BeautifulSoup

BASE = 'https://www.cyberworldstore.shop'
LOGIN = BASE + '/admin/login'
SETTINGS = BASE + '/admin/settings'

s = requests.Session()
# get login page
r = s.get(LOGIN, timeout=15)

payload = {
    'username': 'admin',
    'password': 'GITG360'
}
r = s.post(LOGIN, data=payload, allow_redirects=True, timeout=15)
print('login:', r.status_code, r.url)

# Fetch settings form to collect any hidden inputs (CSRF tokens or similar)
r = s.get(SETTINGS, timeout=15)
if r.status_code != 200:
    print('Failed to GET settings form, status:', r.status_code)
    print(r.text[:1000])
    raise SystemExit(1)

soup = BeautifulSoup(r.text, 'html.parser')

# Build a form payload by copying existing inputs
form_data = {}
for inp in soup.find_all(['input', 'textarea', 'select']):
    name = inp.get('name')
    if not name:
        continue
    # textarea
    if inp.name == 'textarea':
        form_data[name] = inp.text or ''
        continue
    # selects: take current value or first option
    if inp.name == 'select':
        val = None
        opt = inp.find('option', selected=True)
        if opt:
            val = opt.get('value')
        else:
            # fallback to first option value
            first = inp.find('option')
            if first:
                val = first.get('value')
        if val is not None:
            form_data[name] = val
        continue
    typ = inp.get('type', 'text')
    if typ in ('checkbox', 'radio'):
        # preserve checked state if present
        if inp.has_attr('checked'):
            form_data[name] = inp.get('value', 'on')
        else:
            # leave unchecked unless we set it below
            pass
    else:
        form_data[name] = inp.get('value', '')

# Override with desired settings
form_data.update({
    'primary_font': "Arial, sans-serif",
    'secondary_font': "Verdana, sans-serif",
    'primary_color': '#27ae60',
    'secondary_color': '#2c3e50',
    'dashboard_layout': 'grid',
    'site_announcement': '<p>Welcome to Cyber World Store — announcement set by automation.</p>'
})

# Ensure SEO checkboxes are checked by sending them as 'on'
for k in ['site_title', 'meta_tags', 'robots_txt', 'mobile_friendly', 'page_speed', 'ssl_enabled']:
    form_data[k] = 'on'
form_data['seo_visible'] = 'on'

# Submit the form
r2 = s.post(SETTINGS, data=form_data, allow_redirects=True, timeout=15)
print('/admin/settings POST ->', r2.status_code, r2.url)

# Re-fetch to verify
r3 = s.get(SETTINGS, timeout=15)
print('GET /admin/settings', r3.status_code)
if r3.status_code == 200:
    soup2 = BeautifulSoup(r3.text, 'html.parser')
    sel = soup2.find('select', {'id': 'dashboard_layout'})
    layout = None
    if sel:
        opt = sel.find('option', selected=True)
        if opt:
            layout = opt.get('value')
    seo_visible = bool(soup2.find('input', {'id': 'seo_visible', 'checked': True}))
    area = soup2.find('textarea', {'id': 'site_announcement'})
    announcement = area.text.strip() if area else ''
    print('dashboard_layout =', layout)
    print('seo_visible =', seo_visible)
    print('site_announcement =', announcement[:200])
else:
    print('Failed to fetch settings after POST')
