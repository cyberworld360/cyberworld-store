import os
import sys
import tempfile
from io import BytesIO
from pathlib import Path

import pg8000
import pytest

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
    """A minimal test that patches SQLAlchemy Session.commit and verifies last_error is written.
    """
    setup_admin(app, username='pgerradmin')
    client = app.test_client()

    # Login as admin
    resp = client.post('/admin/login', data={'username': 'pgerradmin', 'password': 'secret'}, follow_redirects=True)
    assert resp.status_code == 200

    from sqlalchemy.orm import Session
    orig_flush = Session.flush
    counter = {'count': 0}

    def fake_flush(*args, **kwargs):
        counter['count'] += 1
        # Raise on the second flush (first may be setup), to more reliably hit the admin path
        if counter['count'] >= 2:
            raise pg8000.exceptions.InterfaceError('simulated interface error for tests')
        return orig_flush(*args, **kwargs)

    monkeypatch.setattr(Session, 'flush', fake_flush, raising=False)

    last_err_path = Path(tempfile.gettempdir()) / 'last_error.txt'
    try:
        if last_err_path.exists():
            last_err_path.unlink()
    except Exception:
        pass

    fp = BytesIO(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR')
    fp.name = 'tiny.png'
    resp2 = client.post('/admin/settings', data={'primary_color': '#ffffff', 'logo_file': (fp, 'tiny.png')}, content_type='multipart/form-data', follow_redirects=False)
    assert resp2.status_code in (200, 500)

    content = last_err_path.read_text(encoding='utf-8') if last_err_path.exists() else ''
    print('flush call count:', counter['count'])
    if last_err_path.exists():
        print('last_err content:\n', content)
    assert 'simulated interface error for tests' in content

    monkeypatch.setattr(Session, 'flush', orig_flush, raising=False)


def test_session_reset_after_interface_error(monkeypatch):
    """Ensure the DB session is reset after a driver-level InterfaceError
    so subsequent commits do not raise 'in failed transaction block'."""
    from sqlalchemy.orm import Session
    orig_flush = Session.flush
    counter = {'count': 0}

    def fake_flush(*args, **kwargs):
        # Only raise when the current request is for /admin/settings
        try:
            from flask import request
            if request and getattr(request, 'path', '').startswith('/admin/settings'):
                raise pg8000.exceptions.InterfaceError('simulated interface error for tests')
        except Exception:
            # If not in a request context or any error occurs, fallback to original behavior
            pass
        return orig_flush(*args, **kwargs)

    client = app.test_client()
    setup_admin(app, username='sessionreset')
    monkeypatch.setattr(Session, 'flush', fake_flush, raising=False)
    # Login as admin and trigger the interface error
    resp_login = client.post('/admin/login', data={'username': 'sessionreset', 'password': 'secret'}, follow_redirects=True)
    assert resp_login.status_code == 200
    fp = BytesIO(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR')
    fp.name = 'tiny2.png'
    resp = client.post('/admin/settings', data={'primary_color': '#000000', 'logo_file': (fp, 'tiny2.png')}, content_type='multipart/form-data', follow_redirects=False)
    assert resp.status_code in (200, 500)
    monkeypatch.setattr(Session, 'flush', orig_flush, raising=False)
    # Now ensure a new DB commit works (session should have been reset)
    with app.app_context():
        try:
            u = AdminUser(username='sessionreset2')
            u.set_password('secret')
            db.session.add(u)
            db.session.commit()
        finally:
            # cleanup
            try:
                db.session.delete(u)
                db.session.commit()
            except Exception:
                try:
                    _safe_db_rollback_and_close()
                except Exception:
                    pass
