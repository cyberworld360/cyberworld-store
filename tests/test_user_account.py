import os
import importlib.util
from decimal import Decimal
from pathlib import Path

# Import the app module by file path so we can run in CI
spec = importlib.util.spec_from_file_location('app', os.path.join(os.path.dirname(__file__), '..', 'app.py'))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_account_shows_user_orders(tmp_path):
    from werkzeug.security import generate_password_hash
    # Ensure sqlite DB is used in tmp for tests
    mod.app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{tmp_path / 'data.db'}"
    with mod.app.app_context():
        # ensure clean sqlite path
        db_path = Path(tmp_path / 'data.db')
        if db_path.exists():
            db_path.unlink()
        mod.db.create_all()
        # Create a customer user
        user = mod.User(email=f'alice_{tmp_path.name}@example.com')
        user.set_password('secret')
        mod.db.session.add(user)
        mod.db.session.commit()
        # Create an order linked to the user
        order = mod.Order(reference='ORDER-TEST-123', user_id=user.id, email=user.email, subtotal=Decimal('50'), total=Decimal('60'), paid=True)
        mod.db.session.add(order)
        mod.db.session.commit()
        order_id = order.id

    client = mod.app.test_client()
    # Login as the user
    login_res = client.post('/login', data={'email': f'alice_{tmp_path.name}@example.com', 'password': 'secret'}, follow_redirects=True)
    assert login_res.status_code == 200
    # Visit account dashboard
    res = client.get('/account')
    assert res.status_code == 200
    assert b'Your Orders' in res.data or b'My Account' in res.data
    # Ensure the order reference is shown (first 8 chars used in listing)
    assert b'ORDER-TE' in res.data or b'ORDER-TEST-123' in res.data

    # Visit the specific order detail
    detail_res = client.get(f'/account/order/{order_id}')
    assert detail_res.status_code == 200
    assert b'Order' in detail_res.data or b'Invoice' in detail_res.data
