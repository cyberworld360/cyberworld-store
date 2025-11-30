"""Small script to validate the account routes locally.
"""
import os
import importlib.util
from pathlib import Path
from decimal import Decimal

spec = importlib.util.spec_from_file_location('app', os.path.join(os.path.dirname(__file__), '..', 'app.py'))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def run_local_check():
    mod.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + str(Path(__file__).parent / 'tmp' / 'data.db')
    os.makedirs(Path(__file__).parent / 'tmp', exist_ok=True)
    with mod.app.app_context():
        mod.db.create_all()
        user = mod.User(email='bob@example.com')
        user.set_password('secret')
        mod.db.session.add(user)
        mod.db.session.commit()
        order = mod.Order(reference='ORDER-LOCAL-1', user_id=user.id, email=user.email, subtotal=Decimal('10'), total=Decimal('12'))
        mod.db.session.add(order)
        mod.db.session.commit()
    client = mod.app.test_client()
    login_res = client.post('/login', data={'email': 'bob@example.com', 'password': 'secret'}, follow_redirects=True)
    print('Login status:', login_res.status_code)
    acct = client.get('/account')
    print('/account status:', acct.status_code)
    print('/account contents snippet:', acct.data[:200])
    detail = client.get(f'/account/order/{order.id}')
    print('/account/order detail status:', detail.status_code)
    print('/account/order detail snippet:', detail.data[:200])

if __name__ == '__main__':
    run_local_check()
