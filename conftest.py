import os
import pytest
from pathlib import Path

@pytest.fixture(autouse=True)
def set_test_env(monkeypatch):
    """Set environment for tests to avoid external calls and enforce local SQLite.
    This runs automatically for all pytest tests in the repository.
    """
    monkeypatch.setenv('DATABASE_URL', 'sqlite:///./data.db')
    monkeypatch.setenv('FORCE_EPHEMERAL', '1')
    monkeypatch.setenv('MAIL_SERVER', '')
    monkeypatch.setenv('MAIL_USERNAME', '')
    monkeypatch.setenv('MAIL_PASSWORD', '')
    monkeypatch.setenv('REDIS_URL', '')
    monkeypatch.setenv('PAYSTACK_PUBLIC', '')
    monkeypatch.setenv('PAYSTACK_SECRET', '')
    monkeypatch.setenv('SENDGRID_API_KEY', '')
    # Optional flags
    monkeypatch.setenv('FLASK_ENV', 'testing')
    monkeypatch.setenv('FLASK_DEBUG', '0')


def pytest_sessionstart(session):
    """Ensure a fresh SQLite DB for the pytest session.

    Removing the existing `data.db` avoids UNIQUE constraint errors
    caused by samples created by previous test runs or by app startup
    logic that creates default users at import time.
    """
    db_path = Path('data.db')
    if db_path.exists():
        try:
            db_path.unlink()
        except Exception:
            # If we cannot remove, continue — tests may still run but may require fixes
            pass


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    """By default, stub out requests to external services for test safety.

    - If `TEST_NO_NETWORK` is set to '0', network calls are allowed (for manual integration testing).
    - Otherwise, `requests.get` and `requests.post` are replaced with stubs that provide expected shapes.
    """
    import requests as _requests
    if os.environ.get('TEST_NO_NETWORK', '1') == '0':
        return

    class StubResponse:
        def __init__(self, status_code=200, json_data=None, text=''):
            self.status_code = status_code
            self._json = json_data or {}
            self.text = text

        def json(self):
            return self._json

    def fake_post(url, *args, **kwargs):
        # Paystack POST initialize
        if 'paystack.co' in url:
            return StubResponse(200, json_data={'status': True, 'data': {'authorization_url': 'https://paystack.test/authorize', 'access_code': 'test_code'}})
        # SendGrid POST
        if 'sendgrid.com' in url:
            return StubResponse(202, json_data={'message': 'accepted'})
        return StubResponse(200, json_data={})

    def fake_get(url, *args, **kwargs):
        # Paystack verify URL
        if 'paystack.co' in url:
            return StubResponse(200, json_data={'status': True, 'data': {'status': 'success'}})
        return StubResponse(200, json_data={})

    monkeypatch.setattr(_requests, 'post', fake_post, raising=False)
    monkeypatch.setattr(_requests, 'get', fake_get, raising=False)
