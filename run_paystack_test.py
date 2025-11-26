from app import app
import json
import types

# Monkeypatch requests.post to avoid network calls
import requests

def fake_post(url, json=None, headers=None, timeout=None):
    class FakeResp:
        def raise_for_status(self):
            return None
        def json(self):
            return {"status": True, "data": {"authorization_url": "https://paystack.test/auth", "reference": "fake-ref-123"}}
    return FakeResp()

requests.post = fake_post

app.testing = True
client = app.test_client()
with app.test_request_context():
    with client.session_transaction() as sess:
        sess['cart'] = {'1': 1}

    resp = client.post('/pay/paystack/url', data={'email':'test@ex.com'})
    print('Status:', resp.status_code)
    try:
        print('JSON:', json.dumps(resp.get_json(), indent=2))
    except Exception as e:
        print('Body:', resp.data[:500])
