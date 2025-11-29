import os
import json
from decimal import Decimal
from io import BytesIO
import pytest
import importlib.util

# Import app module
spec = importlib.util.spec_from_file_location('app', os.path.join(os.path.dirname(__file__), '..', 'app.py'))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

from app import app, db, Product


@pytest.fixture(autouse=True)
def _setup_db(monkeypatch):
    # Use an ephemeral sqlite db in memory
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        # Create a product
        p = Product(title='Test Product', short='T', price_ghc=Decimal('10.00'))
        db.session.add(p)
        db.session.commit()
        yield
        db.session.remove()


class DummyResp:
    def __init__(self, data, status=200):
        self._data = data
        self.status_code = status

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception('HTTP Error')

    def json(self):
        return self._data


def test_paystack_init_url_success(monkeypatch):
    client = app.test_client()
    # Add product to cart
    with client.session_transaction() as sess:
        sess['cart'] = {'1': 1}
    os.environ['PAYSTACK_SECRET_KEY'] = 'sk_test'

    def fake_post(url, json=None, headers=None, timeout=None):
        return DummyResp({'status': True, 'data': {'authorization_url': 'https://paystack.test/auth', 'reference': 'ref123'}}, 200)

    monkeypatch.setattr('requests.post', fake_post)
    resp = client.post('/pay/paystack/url', data={'email': 'cust@example.com'}, follow_redirects=False)
    assert resp.status_code == 200
    body = json.loads(resp.data.decode('utf-8'))
    assert body['status'] == 'success'
    assert 'authorization_url' in body


def test_paystack_init_redirect(monkeypatch):
    client = app.test_client()
    with client.session_transaction() as sess:
        sess['cart'] = {'1': 1}
    os.environ['PAYSTACK_SECRET_KEY'] = 'sk_test'

    def fake_post(url, json=None, headers=None, timeout=None):
        return DummyResp({'status': True, 'data': {'authorization_url': 'https://paystack.test/auth', 'reference': 'r2'}}, 200)

    monkeypatch.setattr('requests.post', fake_post)
    resp = client.post('/pay/paystack', data={'email': 'cust@example.com'}, follow_redirects=False)
    assert resp.status_code == 302
    assert resp.location.startswith('https://paystack.test/auth')
