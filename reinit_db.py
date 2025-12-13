#!/usr/bin/env python
"""Hard reset of database - drop all tables and recreate from scratch"""
import os
import sys
from app import app, db, AdminUser, Product
from decimal import Decimal

with app.app_context():
    print("Dropping all tables...")
    db.drop_all()
    print("✓ All tables dropped")
    
    print("Creating all tables...")
    db.create_all()
    print("✓ All tables created")
    
    # Create admin user
    admin = AdminUser()
    admin.username = "admin"
    admin.set_password(os.environ.get("ADMIN_PASSWORD", "GITG360"))
    db.session.add(admin)
    db.session.commit()
    print("✓ Admin user created (username: admin, password: GITG360)")
    
    # Add sample products
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
    db.session.commit()
    print("✓ Sample products added")
    
    print("\n✓ DATABASE FULLY REINITIALIZED!")
