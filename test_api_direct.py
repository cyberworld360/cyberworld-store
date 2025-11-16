"""Quick test: import app directly and test the API endpoint."""
import os
import sys

# Add current dir to path so we can import app
sys.path.insert(0, os.getcwd())

# Set test config
os.environ.setdefault('FLASK_ENV', 'testing')
os.environ['ADMIN_API_TOKEN'] = 'our-FATHER-360'

from app import app, db

# Create app context and initialize DB
with app.app_context():
    db.create_all()
    
    # Use Flask test client
    client = app.test_client()
    
    # Test GET
    print('=== Testing GET /admin/settings/api ===')
    resp = client.get('/admin/settings/api', headers={'X-ADMIN-TOKEN': 'our-FATHER-360'})
    print(f'Status: {resp.status_code}')
    print(f'Response: {resp.get_json()}')
    
    # Test POST
    print('\n=== Testing POST /admin/settings/api ===')
    payload = {
        'dashboard_layout': 'grid',
        'seo_visible': True,
        'site_announcement': 'Test announcement from local client'
    }
    resp = client.post(
        '/admin/settings/api',
        json=payload,
        headers={'X-ADMIN-TOKEN': 'our-FATHER-360', 'Content-Type': 'application/json'}
    )
    print(f'Status: {resp.status_code}')
    print(f'Response: {resp.get_json()}')
    
    # Verify by GETting again
    print('\n=== Verify settings were saved (GET again) ===')
    resp = client.get('/admin/settings/api', headers={'X-ADMIN-TOKEN': 'our-FATHER-360'})
    print(f'Status: {resp.status_code}')
    data = resp.get_json()
    print(f'Response: {data}')
    if data and data.get('status') == 'success':
        settings = data.get('settings', {})
        print(f'\nVerification:')
        print(f'  dashboard_layout: {settings.get("dashboard_layout")} (expected: grid)')
        print(f'  seo_visible: {settings.get("seo_visible")} (expected: True)')
        print(f'  site_announcement: {settings.get("site_announcement")} (expected: Test announcement...)')
