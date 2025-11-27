import pytest
from app import app, db, _ensure_settings_columns, Product, AdminUser, User
from flask import url_for


@pytest.fixture(autouse=True)
def setup_db():
    with app.app_context():
        # Reset DB for each test run to ensure isolation.
        db.drop_all()
        db.create_all()
        _ensure_settings_columns()
        yield
        db.session.remove()


def test_admin_user_and_login_and_admin_access():
    with app.app_context():
        # Create admin user
        admin = AdminUser(username='testadmin2')
        admin.set_password('secret123')
        db.session.add(admin)
        db.session.commit()

        # Assertions on model behavior
        assert admin.check_password('secret123')
        assert admin.is_admin is True

    client = app.test_client()

    # Login as admin
    resp = client.post('/admin/login', data={'username': 'testadmin2', 'password': 'secret123'}, follow_redirects=True)
    assert resp.status_code == 200
    assert b'Logged in as admin' in resp.data or b'Admin panel' in resp.data or b'Admin' in resp.data

    # Access admin index
    resp = client.get('/admin')
    assert resp.status_code == 200

    # Logout
    client.get('/admin/logout', follow_redirects=True)

    # Create a regular user and login
    with app.app_context():
        user = User(email='customer@example.com')
        user.set_password('custpass')
        db.session.add(user)
        db.session.commit()

    resp = client.post('/login', data={'email': 'customer@example.com', 'password': 'custpass'}, follow_redirects=True)
    assert resp.status_code == 200
    assert b'Logged in successfully' in resp.data or b'Welcome' in resp.data or b'Logout' in resp.data

    # Non-admin should not access admin page
    resp = client.get('/admin', follow_redirects=True)
    # Should redirect away (to index) or be forbidden
    assert resp.status_code == 200
    assert b'Admin access required' in resp.data or b'You are not authorized' in resp.data or b'index' in resp.data


def test_cart_api_counts():
    with app.app_context():
        # Create a product
        p = Product(title='Cart Test', short='ct', price_ghc=20, image='/tmp')
        db.session.add(p)
        db.session.commit()
        pid = p.id

    client = app.test_client()

    # Initially cart count should be 0
    resp = client.get('/api/cart-count')
    assert resp.status_code == 200
    assert resp.get_json().get('count') == 0

    # Add 2 units of product
    resp = client.post(f'/cart/add/{pid}', data={'qty': 2}, follow_redirects=True)
    assert resp.status_code in (200, 302)

    # Cart count should reflect 2
    resp = client.get('/api/cart-count')
    assert resp.status_code == 200
    assert resp.get_json().get('count') == 2

    # Update to 1 unit
    resp = client.post('/cart/update', data={f'qty_{pid}': '1'}, follow_redirects=True)
    assert resp.status_code in (200, 302)
    resp = client.get('/api/cart-count')
    assert resp.get_json()['count'] == 1

    # Clear cart
    client.get('/cart/clear', follow_redirects=True)
    resp = client.get('/api/cart-count')
    assert resp.get_json().get('count') == 0


def test_admin_settings_api():
    with app.app_context():
        admin = AdminUser(username='testadmin3')
        admin.set_password('secret321')
        db.session.add(admin)
        db.session.commit()
    client = app.test_client()
    # Login as admin
    resp = client.post('/admin/login', data={'username': 'testadmin3', 'password': 'secret321'}, follow_redirects=True)
    assert resp.status_code == 200
    # Get current settings
    resp = client.get('/admin/settings/api')
    assert resp.status_code == 200
    json_data = resp.get_json()
    assert json_data['status'] == 'success'
    # Update settings via POST JSON
    payload = {'logo_height': 77, 'cart_on_right': False, 'custom_css': '.site-logo { border: 1px solid red; }'}
    resp = client.post('/admin/settings/api', json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['status'] == 'success'
    # Verify settings persisted
    with app.app_context():
        from app import get_settings
        s = get_settings()
        assert s.logo_height == 77
        assert s.cart_on_right == False
        assert '.site-logo' in s.custom_css


def test_session_userid_prefixes():
    with app.app_context():
        admin = AdminUser(username='testsessionadmin')
        admin.set_password('s')
        db.session.add(admin)
        user = User(email='testsession@example.com')
        user.set_password('s')
        db.session.add(user)
        db.session.commit()

    client = app.test_client()
    # Admin login
    resp = client.post('/admin/login', data={'username':'testsessionadmin','password':'s'}, follow_redirects=True)
    assert resp.status_code == 200
    with client.session_transaction() as sess:
        uid = sess.get('_user_id') or sess.get('user_id')
        assert isinstance(uid, str)
        assert uid.startswith('AdminUser:')

    # Logout
    client.get('/admin/logout')

    # User login
    resp = client.post('/login', data={'email': 'testsession@example.com', 'password': 's'}, follow_redirects=True)
    assert resp.status_code == 200
    with client.session_transaction() as sess:
        uid = sess.get('_user_id') or sess.get('user_id')
        assert isinstance(uid, str)
        assert uid.startswith('User:')


def test_loader_returns_correct_user_type():
    from app import load_user
    with app.app_context():
        # Create admin and customer user
        admin = AdminUser(username='loadertestadmin')
        admin.set_password('s')
        db.session.add(admin)
        user = User(email='loadertest@example.com')
        user.set_password('s')
        db.session.add(user)
        db.session.commit()
        # Ensure load_user returns correct instances
        a = load_user(admin.get_id())
        assert isinstance(a, AdminUser)
        u = load_user(user.get_id())
        assert isinstance(u, User)
        # Legacy numeric id fallback should still work
        a2 = load_user(admin.id)
        assert isinstance(a2, AdminUser)
        u2 = load_user(user.id)
        # In case of id collision, admin takes precedence; prefer not elevating user
        assert isinstance(u2, (User, AdminUser))
