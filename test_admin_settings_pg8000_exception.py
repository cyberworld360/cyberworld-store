import os
import sys
from io import BytesIO
import pg8000
from pathlib import Path

sys.path.insert(0, os.getcwd())
from app import app, db, AdminUser


def setup_admin(app, username='pgerradmin'):
    with app.app_context():
        db.create_all()
        admin = AdminUser.query.filter_by(username=username).first()
        if not admin:
            admin = AdminUser(username=username)
            admin.set_password('secret')
            db.session.add(admin)
            db.session.commit()


def test_admin_settings_handles_pg8000_interface_error(monkeypatch, tmp_path):
    setup_admin(app, username='pgerradmin')
    client = app.test_client()
    # login
    resp = client.post('/admin/login', data={'username': 'pgerradmin', 'password': 'secret'}, follow_redirects=True)
    assert resp.status_code == 200

    # Force db.session.commit() to raise pg8000.exceptions.InterfaceError
    # Patch only the db.session local instance's flush to avoid polluting other sessions
    orig_flush = db.session.flush
    counter = {'count': 0}

    def fake_flush(*args, **kwargs):
        counter['count'] += 1
        # raise only on second invocation (likely the admin_settings flush)
        if counter['count'] == 2:
            raise pg8000.exceptions.InterfaceError('simulated interface error for tests')
        return orig_flush(*args, **kwargs)

    monkeypatch.setattr(db.session, 'flush', fake_flush, raising=False)

    # make sure any existing last_error file is removed
    last_err_path = Path('/tmp/last_error.txt')
    try:
        if last_err_path.exists():
            last_err_path.unlink()
    except Exception:
        pass

    # First flush should pass (counter=1), the second flush (during the POST request) should raise
    with app.app_context():
        db.session.flush()

    # POST settings with small file and expect app to handle exception gracefully
    fp = BytesIO(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR')
    fp.name = 'tiny.png'
    resp2 = client.post('/admin/settings', data={'primary_color': '#ffffff', 'logo_file': (fp, 'tiny.png')}, content_type='multipart/form-data', follow_redirects=True)
    # Should not crash server; commit should raise and we should persist last_error
    assert resp2.status_code == 200

    # Verify that last_error was persisted with our simulated message
    content = last_err_path.read_text(encoding='utf-8') if last_err_path.exists() else ''
    assert 'simulated interface error for tests' in content

    monkeypatch.setattr(db.session, 'flush', orig_flush, raising=False)
