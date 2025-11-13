#!/usr/bin/env python
"""Initialize database with admin user"""
import os
from app import app, db, AdminUser, Product
from decimal import Decimal

with app.app_context():
    # Create all tables
    db.create_all()
    print("✓ Database tables created")
    
    # Create admin user if doesn't exist
    if not AdminUser.query.filter_by(username="admin").first():
        admin = AdminUser()
        admin.username = "admin"
        admin.set_password(os.environ.get("ADMIN_PASSWORD", "GITG360"))
        db.session.add(admin)
        print("✓ Admin user created (username: admin, password: GITG360)")
    else:
        print("✓ Admin user already exists")
    
    # Add sample products if none exist
    if Product.query.count() == 0:
        sample = [
            {"title":"Sample Soundbar", "short":"High quality sound bar", "price_ghc":1190.45, "old_price_ghc":1434.00, "image":"/static/images/placeholder.png", "featured":True},
            {"title":"Wireless Modem 4G/5G", "short":"High speed wireless modem", "price_ghc":700.00, "old_price_ghc":780.00, "image":"/static/images/placeholder.png", "featured":True},
        ]
        for s in sample:
            p = Product(
                title=s["title"], 
                short=s["short"], 
                price_ghc=Decimal(str(s["price_ghc"])), 
                old_price_ghc=Decimal(str(s["old_price_ghc"])), 
                image=s["image"], 
                featured=s["featured"]
            )
            db.session.add(p)
        print("✓ Sample products added")
    else:
        print("✓ Products already exist")
    
    db.session.commit()
    print("\n✓ DATABASE INITIALIZED SUCCESSFULLY!")
    print("  Admin credentials:")
    print("  - Username: admin")
    print("  - Password: GITG360")
