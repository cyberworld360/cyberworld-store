import os, sys
sys.path.insert(0, os.getcwd())
# Set env vars same as conftest
os.environ['DATABASE_URL'] = 'sqlite:///./data.db'
os.environ['FORCE_EPHEMERAL'] = '1'
os.environ['MAIL_SERVER'] = ''
os.environ['MAIL_USERNAME'] = ''
os.environ['MAIL_PASSWORD'] = ''
os.environ['REDIS_URL'] = ''
os.environ['PAYSTACK_PUBLIC'] = 'test_public'
os.environ['PAYSTACK_SECRET'] = 'test_secret'
os.environ['SENDGRID_API_KEY'] = ''
os.environ['FLASK_ENV'] = 'testing'
os.environ['FLASK_DEBUG'] = '0'

from app import app, db, Product
from decimal import Decimal

# Monkeypatch requests globally so the app uses stubs
import requests
class StubResponse:
    def __init__(self, status_code=200, json_data=None, text=''):
        self.status_code = status_code
        self._json = json_data or {}
        self.text = text
    def json(self):
        return self._json


def fake_post(url, *args, **kwargs):
    if 'paystack.co' in url:
        return StubResponse(200, json_data={'status': True, 'data': {'authorization_url': 'https://paystack.test/authorize', 'access_code': 'test_code'}})
    if 'sendgrid.com' in url:
        return StubResponse(202, json_data={'message': 'accepted'})
    return StubResponse(200, json_data={})


def fake_get(url, *args, **kwargs):
    if 'paystack.co' in url:
        return StubResponse(200, json_data={'status': True, 'data': {'status': 'success'}})
    return StubResponse(200, json_data={})

requests.post = fake_post
requests.get = fake_get

with app.app_context():
    db.drop_all()
    db.create_all()
    p = Product(title='PS Test', short='pst', price_ghc=Decimal('100.00'))
    db.session.add(p)
    db.session.commit()
    pid = p.id

client = app.test_client()
with client.session_transaction() as sess:
    sess['cart'] = {str(pid): 1}

resp = client.post('/pay/paystack/url', data={'email': 'customer@example.com', 'name': 'John Doe', 'phone': '+233111111111', 'city': 'Accra'}, follow_redirects=True)
print('status', resp.status_code)
print('json', resp.get_json())
print('text', resp.data[:2048])
