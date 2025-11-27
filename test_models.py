from app import app, db, get_settings, _ensure_settings_columns, Product, AdminUser, Coupon

with app.app_context():
    print('Creating tables...')
    db.create_all()
    print('Ensuring settings columns...')
    _ensure_settings_columns()
    s = get_settings()
    print('settings before:', getattr(s, 'logo_height', None))
    s.logo_height = 60
    s.logo_top_px = 4
    s.logo_zindex = 1000
    s.cart_on_right = False
    db.session.add(s)
    db.session.commit()
    s2 = get_settings()
    print('settings after:', s2.logo_height, s2.logo_top_px, s2.logo_zindex, s2.cart_on_right)
    p = Product(title='SM', short='s', price_ghc=10, old_price_ghc=15, image='/tmp', featured=False)
    db.session.add(p); db.session.commit()
    print('product to dict:', p.to_dict())
    a = AdminUser(username='testadmin'); a.set_password('secret'); db.session.add(a); db.session.commit()
    print('login check:', a.check_password('secret'), a.check_password('wrong'))
    c = Coupon(code='DISC10', discount_type='percent', discount_value=10)
    db.session.add(c); db.session.commit()
    ok,msg = c.is_valid(); print('coupon valid:', ok,msg); print('discount on 100:', c.calculate_discount(100))
print('Done')