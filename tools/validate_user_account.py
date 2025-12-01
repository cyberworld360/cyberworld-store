"""Small script to validate the account routes locally.
"""
import os
import importlib.util
from pathlib import Path
from decimal import Decimal

print('[validate] loading app module')
spec = importlib.util.spec_from_file_location('app', os.path.join(os.path.dirname(__file__), '..', 'app.py'))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
print('[validate] app module loaded')

def run_local_check():
    tmp_dir = Path(__file__).parent / 'tmp'
    tmp_db = tmp_dir / 'data.db'
    os.makedirs(tmp_dir, exist_ok=True)
    # remove any existing tmp DB to avoid unique-constraint collisions from prior runs
    try:
        if tmp_db.exists():
            tmp_db.unlink()
    except Exception:
        pass
    mod.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + str(tmp_db)
    print('[validate] set SQLALCHEMY_DATABASE_URI to', mod.app.config['SQLALCHEMY_DATABASE_URI'])
    # Ensure DB engine/session are reset when reusing the app in-process
    try:
        # Dispose the existing engine, flush and remove sessions
        if hasattr(mod.db, 'engine') and mod.db.engine:
            try:
                mod.db.session.remove()
            except Exception:
                pass
            try:
                mod.db.engine.dispose()
            except Exception:
                pass
    except Exception:
        pass
    # Reinitialize extensions with new configuration (safe to call again)
    try:
        if hasattr(mod, '_safe_initialize_extensions') and callable(mod._safe_initialize_extensions):
            mod._safe_initialize_extensions(mod.app)
    except Exception:
        pass
    with mod.app.app_context():
        print('[validate] app context entered')
        # Start from a clean DB for this smoke test to avoid collisions
        try:
            mod.db.drop_all()
        except Exception:
            pass
        mod.db.create_all()
        print('[validate] db.create_all done')
        # Use a unique email per run so previous test data cannot cause UNIQUE constraint errors
        import uuid as _uuid
        unique_email = f"bob+{_uuid.uuid4().hex[:8]}@example.com"
        user = mod.User(email=unique_email)
        user.set_password('secret')
        mod.db.session.add(user)
        mod.db.session.commit()
        print('[validate] created user and committed, user id =', user.id)
        order = mod.Order(reference='ORDER-LOCAL-1', user_id=user.id, email=user.email, subtotal=Decimal('10'), total=Decimal('12'))
        mod.db.session.add(order)
        mod.db.session.commit()
        print('[validate] created order and committed, order id =', order.id)
        # capture the order id while still in-app-context to avoid DetachedInstanceError
        order_id = order.id
    client = mod.app.test_client()
    login_res = client.post('/login', data={'email': unique_email, 'password': 'secret'}, follow_redirects=True)
    print('[validate] login request made')
    print('Login status:', login_res.status_code)
    acct = client.get('/account')
    print('/account status:', acct.status_code)
    print('/account contents snippet:', acct.data[:200])
    detail = client.get(f'/account/order/{order_id}')
    print('/account/order detail status:', detail.status_code)
    print('/account/order detail snippet:', detail.data[:200])

if __name__ == '__main__':
    run_local_check()
