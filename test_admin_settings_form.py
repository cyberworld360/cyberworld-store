import os
import sys
from pathlib import Path
from io import BytesIO

sys.path.insert(0, os.getcwd())
from app import app, db, AdminUser


def setup_admin(app):
    with app.app_context():
        db.create_all()
        admin = AdminUser.query.filter_by(username='formtestadmin').first()
        if not admin:
            admin = AdminUser(username='formtestadmin')
            admin.set_password('secret')
            db.session.add(admin)
            db.session.commit()


def test_admin_settings_form_save():
    setup_admin(app)
    app.config['PROPAGATE_EXCEPTIONS'] = True
    client = app.test_client()
    # login
    resp = client.post('/admin/login', data={'username': 'formtestadmin', 'password': 'secret'}, follow_redirects=True)
    assert resp.status_code == 200

    # simple save
    resp = client.post('/admin/settings', data={'primary_color': '#ffffff', 'secondary_color': '#000000', 'dashboard_layout': 'grid', 'custom_css': '.test{}'}, follow_redirects=True)
    assert resp.status_code == 200
    assert b'Settings saved successfully' in resp.data or b'Error saving settings' not in resp.data

    # save with small image upload
    fp = BytesIO(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR')
    fp.name = 'tiny.png'
    resp2 = client.post('/admin/settings', data={'primary_color': '#ffffff', 'logo_file': (fp, 'tiny.png')}, content_type='multipart/form-data', follow_redirects=True)
    assert resp2.status_code == 200
    assert b'Settings saved successfully' in resp2.data or b'Logo saved to database' in resp2.data
