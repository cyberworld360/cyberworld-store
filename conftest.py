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
