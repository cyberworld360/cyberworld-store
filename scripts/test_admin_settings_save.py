import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from app import app, db, AdminUser
from io import BytesIO

with app.app_context():
    db.create_all()
    admin = AdminUser.query.filter_by(username='testadminsave').first()
    if not admin:
        admin = AdminUser(username='testadminsave')
        admin.set_password('secret')
        db.session.add(admin)
        db.session.commit()

app.config['PROPAGATE_EXCEPTIONS'] = True
client = app.test_client()
resp = client.post('/admin/login', data={'username':'testadminsave','password':'secret'}, follow_redirects=True)
print('Login status:', resp.status_code)
if resp.status_code != 200:
    print('Login response length:', len(resp.data))

# Post simple settings (no file)
resp = client.post('/admin/settings', data={'primary_color':'#ffffff','secondary_color':'#000000','dashboard_layout':'grid','custom_css':'.test{}'}, follow_redirects=True)
print('/admin/settings status (no file):', resp.status_code)
print(resp.get_data(as_text=True)[:1000])
if resp.status_code >= 500:
    # Try to fetch diagnostic /__last_error if available
    token = os.environ.get('ERROR_VIEW_TOKEN')
    if token:
        le = client.get(f'/__last_error?token={token}')
        print('\nLast error trace:')
        print(le.get_data(as_text=True)[:4000])

# Post with file upload
fp = BytesIO(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR')
fp.name = 'logo.png'
resp2 = client.post('/admin/settings', data={'primary_color':'#ffffff','logo_file': (fp, 'logo.png')}, content_type='multipart/form-data', follow_redirects=True)
print('/admin/settings status (with file):', resp2.status_code)
print(resp2.get_data(as_text=True)[:1000])
if resp2.status_code >= 500:
    token = os.environ.get('ERROR_VIEW_TOKEN')
    if token:
        le2 = client.get(f'/__last_error?token={token}')
        print('\nLast error trace:')
        print(le2.get_data(as_text=True)[:4000])
