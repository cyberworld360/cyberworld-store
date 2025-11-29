import os, sys
sys.path.insert(0, os.getcwd())
from app import app, db, Product
from decimal import Decimal

with app.app_context():
    db.create_all()
    # clean up if product exists
    p = Product.query.filter_by(title='PS Test').first()
    if p:
        db.session.delete(p)
        db.session.commit()

    p = Product(title='PS Test', short='pst', price_ghc=Decimal('100.00'))
    db.session.add(p)
    db.session.commit()
    pid = p.id

client = app.test_client()
with client.session_transaction() as sess:
    sess['cart'] = {str(pid): 1}

resp = client.post('/pay/paystack/url', data={'email': 'customer@example.com', 'name': 'John Doe', 'phone': '+233111111111', 'city': 'Accra'}, follow_redirects=True)
print('status', resp.status_code)
try:
    print('json:', resp.get_json())
except Exception:
    print('text:', resp.data[:1024])
