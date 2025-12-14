#!/usr/bin/env python
"""Hard reset of database - drop all tables and recreate from scratch"""
import os
import sys
from app import app, db, AdminUser, Product, Settings
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
    
    # Create default Settings with image URLs
    settings = Settings()
    settings.bg_url = "/static/images/product-bg.svg"
    settings.banner1_url = "/static/images/ads1.svg"
    settings.banner2_url = "/static/images/ads2.svg"
    settings.logo_url = "/static/images/logo.svg"
    db.session.add(settings)
    db.session.commit()
    print("✓ Settings configured with image URLs")
    
    # Add comprehensive sample products
    sample = [
        {"title":"Premium Wireless Soundbar", "short":"Crystal clear sound with 360° surround", "price_ghc":1190.45, "old_price_ghc":1434.00, "featured":True},
        {"title":"Wireless Modem 4G/5G", "short":"Lightning-fast internet connectivity", "price_ghc":700.00, "old_price_ghc":780.00, "featured":True},
        {"title":"Gaming Mechanical Keyboard", "short":"RGB backlit with 120+ key rollover", "price_ghc":450.99, "old_price_ghc":599.99, "featured":True},
        {"title":"4K Webcam Pro", "short":"Ultra HD 4K video for streaming", "price_ghc":320.50, "old_price_ghc":425.00, "featured":False},
        {"title":"Wireless Gaming Mouse", "short":"10000 DPI precision optical sensor", "price_ghc":189.99, "old_price_ghc":249.99, "featured":False},
        {"title":"USB-C Hub 7-in-1", "short":"Multi-port charging and data transfer", "price_ghc":125.00, "old_price_ghc":180.00, "featured":False},
        {"title":"Monitor Light Bar", "short":"Eye-care LED light for desk", "price_ghc":210.75, "old_price_ghc":299.99, "featured":True},
        {"title":"Portable SSD 1TB", "short":"Ultra-fast 550MB/s transfer speed", "price_ghc":580.00, "old_price_ghc":750.00, "featured":False},
        {"title":"Noise Cancelling Earbuds", "short":"Active noise cancellation with 48h battery", "price_ghc":350.00, "old_price_ghc":499.99, "featured":True},
        {"title":"Laptop Cooling Pad", "short":"Dual fan system with adjustable height", "price_ghc":95.50, "old_price_ghc":149.99, "featured":False},
    ]
    for s in sample:
        p = Product(
            title=s["title"], 
            short=s["short"], 
            price_ghc=Decimal(str(s["price_ghc"])), 
            old_price_ghc=Decimal(str(s["old_price_ghc"])), 
            image="/static/images/placeholder.png", 
            featured=s["featured"]
        )
        db.session.add(p)
    db.session.commit()
    print("✓ 10 sample products added")
    
    print("\n✅ DATABASE FULLY REINITIALIZED!")
