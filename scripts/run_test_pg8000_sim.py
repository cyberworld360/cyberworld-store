import os
import sys
from io import BytesIO
import importlib

sys.path.insert(0, os.getcwd())
from app import app, db, AdminUser
from sqlalchemy.orm import Session

# Simple setup to run the admin settings test simulation

def setup_admin(app, username='pgerradmin'):
    with app.app_context():
        db.create_all()
        admin = AdminUser.query.filter_by(username=username).first()
        if not admin:
            admin = AdminUser(username=username)
            admin.set_password('secret')
            db.session.add(admin)
            db.session.commit()


if __name__ == '__main__':
    setup_admin(app, username='pgerradmin')
    client = app.test_client()
    # login
    resp = client.post('/admin/login', data={'username': 'pgerradmin', 'password': 'secret'}, follow_redirects=True)
    print('login status:', resp.status_code)
    assert resp.status_code == 200

    # monkeypatch Session.flush behavior (similar to pytest test)
    orig_flush = Session.flush
    counter = {'count': 0}

    def fake_flush(*args, **kwargs):
        counter['count'] += 1
        # raise only on second invocation (likely the admin_settings flush)
        if counter['count'] == 2:
            import pg8000
            raise pg8000.exceptions.InterfaceError('simulated interface error for tests')
        return orig_flush(*args, **kwargs)

    # Patch the Session.flush method used by SQLAlchemy sessions created per request
    Session.flush = fake_flush

    import tempfile
    from pathlib import Path
    last_err_path = str(Path(tempfile.gettempdir()) / 'last_error.txt')
    if os.path.exists(last_err_path):
        os.unlink(last_err_path)

    fp = BytesIO(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR')
    fp.name = 'tiny.png'
    resp2 = client.post('/admin/settings', data={'primary_color': '#ffffff', 'logo_file': (fp, 'tiny.png')}, content_type='multipart/form-data', follow_redirects=True)
    print('settings post status:', resp2.status_code)

    if os.path.exists(last_err_path):
        print('last_error file exists; content:')
        print(open(last_err_path, 'r', encoding='utf-8').read())
    else:
        print('last_error file not found')

    # restore original flush
    Session.flush = orig_flush
