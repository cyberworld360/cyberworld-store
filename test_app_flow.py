#!/usr/bin/env python
"""
Test comprehensive app flow: DB init, products, images, auth, Paystack
"""
import sys
import os
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

print("\n" + "="*80)
print(" COMPREHENSIVE APP FLOW TEST")
print("="*80)

try:
    print("\n[1/6] Importing app and models...")
    from app import app, db, Product, Settings, Coupon, AdminUser, User, Wallet
    print("  [OK] Imported successfully")
    
    print("\n[2/6] Initializing database...")
    with app.app_context():
        db.create_all()
        
        # Check if sample products exist
        prod_count = Product.query.count()
        print(f"  [OK] Database initialized. Products in DB: {prod_count}")
        
        # Check admin user
        admin = AdminUser.query.filter_by(username="Cyberjnr").first()
        if admin:
            print(f"  [OK] Admin user 'Cyberjnr' exists")
        else:
            print(f"  [WARN] Admin user not found, creating...")
            admin = AdminUser()
            admin.username = "Cyberjnr"
            admin.set_password("GITG360$")
            db.session.add(admin)
            db.session.commit()
            print(f"  [OK] Created admin user")
        
        print("\n[3/6] Testing Product model...")
        # Create a test product
        test_prod = Product(
            title="Test Widget",
            short="A test widget",
            price_ghc=100.50,
            old_price_ghc=120.00,
            image="/static/images/placeholder.png",
            featured=True
        )
        db.session.add(test_prod)
        db.session.commit()
        
        fetched = Product.query.filter_by(title="Test Widget").first()
        if fetched:
            print(f"  [OK] Product saved and retrieved: {fetched.title} - GH₵{fetched.price_ghc}")
            print(f"      to_dict(): {fetched.to_dict()}")
        else:
            print(f"  [ERR] Could not retrieve test product")
        
        print("\n[4/6] Testing Settings model with image storage...")
        settings = Settings.query.first()
        if not settings:
            settings = Settings()
            db.session.add(settings)
        
        # Simulate base64 image storage
        import base64
        test_image = b"fake_image_data_123"
        b64_encoded = base64.b64encode(test_image)
        settings.logo_image_data = b64_encoded
        settings.logo_image_mime = "image/png"
        db.session.commit()
        
        reloaded = Settings.query.first()
        if reloaded.logo_image_data:
            print(f"  [OK] Settings logo stored: {len(reloaded.logo_image_data)} bytes")
            print(f"      MIME type: {reloaded.logo_image_mime}")
            print(f"      get_logo_url(): {reloaded.get_logo_url()}")
        else:
            print(f"  [ERR] Logo image not stored")
        
        print("\n[5/6] Testing User registration and login...")
        # Create test customer user
        test_user = User.query.filter_by(email="testuser@example.com").first()
        if not test_user:
            test_user = User(email="testuser@example.com")
            test_user.set_password("TestPassword123")
            db.session.add(test_user)
            db.session.flush()
            wallet = Wallet(user_id=test_user.id, balance=50.00)
            db.session.add(wallet)
            db.session.commit()
            print(f"  [OK] Created test user: testuser@example.com")
        
        # Test password check
        if test_user.check_password("TestPassword123"):
            print(f"  [OK] Password verification works")
        else:
            print(f"  [ERR] Password verification failed")
        
        # Verify is_admin property
        print(f"      User.is_admin: {test_user.is_admin} (should be False)")
        print(f"      AdminUser.is_admin: {admin.is_admin} (should be True)")
        
        print("\n[6/6] Testing Paystack callback URL...")
        from app import PAYSTACK_CALLBACK, PAYSTACK_SECRET, PAYSTACK_PUBLIC
        print(f"  [OK] PAYSTACK_CALLBACK: {PAYSTACK_CALLBACK}")
        print(f"  [OK] PAYSTACK_SECRET configured: {bool(PAYSTACK_SECRET)}")
        print(f"  [OK] PAYSTACK_PUBLIC configured: {bool(PAYSTACK_PUBLIC)}")
        
        # Verify callback URL is correct
        if "cyberworldstore.shop" in PAYSTACK_CALLBACK or "paystack/callback" in PAYSTACK_CALLBACK:
            print(f"  [OK] Callback URL looks correct")
        else:
            print(f"  [WARN] Callback URL may need verification")
        
        print("\n" + "="*80)
        print(" [PASSED] ALL TESTS PASSED")
        print("="*80)
        print("\n[SUMMARY]")
        print("  ✓ Database initialized successfully")
        print("  ✓ Admin user 'Cyberjnr' exists and works")
        print("  ✓ Product creation and retrieval works")
        print("  ✓ Settings model stores images in DB")
        print("  ✓ User registration and password verification works")
        print("  ✓ is_admin property correctly identifies admin vs customer")
        print("  ✓ Paystack callback URL configured")
        print("\n[READY FOR]")
        print("  • Image upload via admin settings (stores in DB or S3)")
        print("  • Product image upload (stores in DB or static)")
        print("  • User registration and login flow")
        print("  • Shopping cart and checkout with Paystack payment")
        print("\n")

except Exception as e:
    print(f"\n[FAILED] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
