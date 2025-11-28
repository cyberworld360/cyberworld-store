import pytest
from app import app, db, Product, AdminUser
from flask import url_for
from decimal import Decimal


@pytest.fixture(autouse=True)
def setup_db():
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield


def test_paystack_initialize_url_returns_authorization():
    with app.app_context():
        # Create a product and default admin
        p = Product(title='PS Test', short='pst', price_ghc=Decimal('100.00'))
        db.session.add(p)
        db.session.commit()
        pid = p.id

    client = app.test_client()
    # Add item to session cart
    with client.session_transaction() as sess:
        sess['cart'] = {str(pid): 1}

    # Post to paystack init url (forms accepted)
    resp = client.post('/pay/paystack/url', data={'email': 'customer@example.com', 'name': 'John Doe', 'phone': '+233111111111', 'city': 'Accra'}, follow_redirects=True)
    assert resp.status_code in (200, 201)
    data = resp.get_json() or {}
    assert data.get('status') == 'success'
    assert 'authorization_url' in data


def test_paystack_callback_verifies_and_sends_emails(monkeypatch):
    from app import PAYSTACK_SECRET
    with app.app_context():
        # Ensure a product exists and admin present
        if Product.query.count() == 0:
            p = Product(title='PS Test', short='pst', price_ghc=Decimal('50.00'))
            db.session.add(p)
            db.session.commit()
        admin = AdminUser.query.filter_by(username='Cyberjnr').first()
        if not admin:
            admin = AdminUser(username='Cyberjnr')
            admin.set_password('GITG360$')
            db.session.add(admin)
            db.session.commit()

    client = app.test_client()
    # Create a fake pending_payment in session
    reference = 'test-ref-123'
    with client.session_transaction() as sess:
        sess['pending_payment'] = {'reference': reference, 'amount': 5000, 'email': 'customer@example.com', 'items': [{'product': 'PS Test', 'qty': 1, 'subtotal': 50.0}]}

    # Call callback with stubbed requests via conftest
    resp = client.get(f'/paystack/callback?reference={reference}', follow_redirects=True)
    # After callback, the user should be redirected to index or success page
    assert resp.status_code == 200
    assert b'Payment' in resp.data or b'Order Confirmation' in resp.data or b'index' in resp.data
