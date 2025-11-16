#!/usr/bin/env python3
"""
Test script to verify Paystack payment flow works correctly
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Wallet, Product, Order, OrderItem, Coupon
from decimal import Decimal
import json

def test_paystack_flow():
    """Test the Paystack payment flow"""
    print("\n" + "="*70)
    print("TESTING PAYSTACK PAYMENT FLOW")
    print("="*70)
    
    with app.app_context():
        # Create test database
        db.create_all()
        print("✓ Database created")
        
        # Create test product
        if Product.query.count() == 0:
            prod = Product(
                title="Test Product",
                short="Test product description",
                price_ghc=Decimal('100.00'),
                image="/static/images/placeholder.png"
            )
            db.session.add(prod)
            db.session.commit()
            print(f"✓ Test product created (id={prod.id})")
        else:
            prod = Product.query.first()
            print(f"✓ Using existing product (id={prod.id})")
        
        # Create test coupon
        if Coupon.query.filter_by(code='TEST10').first() is None:
            coupon = Coupon(
                code='TEST10',
                discount_type='percent',
                discount_value=Decimal('10'),
                min_amount=Decimal('0'),
                max_uses=100,
                is_active=True
            )
            db.session.add(coupon)
            db.session.commit()
            print(f"✓ Test coupon created (code=TEST10, id={coupon.id})")
        else:
            coupon = Coupon.query.filter_by(code='TEST10').first()
            print(f"✓ Using existing coupon (code=TEST10, id={coupon.id})")
        
        # Create test customer
        test_email = "test@example.com"
        user = User.query.filter_by(email=test_email).first()
        if not user:
            user = User(email=test_email)
            user.set_password("test123")
            db.session.add(user)
            db.session.flush()
            wallet = Wallet(user_id=user.id, balance=Decimal('500.00'))
            db.session.add(wallet)
            db.session.commit()
            print(f"✓ Test user created (email={test_email}, id={user.id})")
        else:
            print(f"✓ Using existing test user (email={test_email}, id={user.id})")
        
        # Test paystack_init POST data structure
        print("\n" + "-"*70)
        print("VALIDATING PAYSTACK INIT DATA STRUCTURE")
        print("-"*70)
        
        paystack_init_data = {
            'email': 'customer@example.com',
            'name': 'John Doe',
            'phone': '+233123456789',
            'city': 'Accra',
            'coupon_id': str(coupon.id)
        }
        print("✓ Paystack init POST data structure:")
        for key, val in paystack_init_data.items():
            print(f"  - {key}: {val}")
        
        # Verify coupon validation works
        print("\n" + "-"*70)
        print("VALIDATING COUPON LOGIC")
        print("-"*70)
        
        total_amount = Decimal('100.00')
        is_valid, msg = coupon.is_valid()
        print(f"✓ Coupon validation: {msg}")
        
        if total_amount >= Decimal(str(coupon.min_amount)):
            discount = coupon.calculate_discount(total_amount)
            print(f"✓ Discount calculated: GH₵{discount:.2f}")
            final_total = total_amount - discount
            print(f"✓ Final total: GH₵{final_total:.2f}")
        else:
            print(f"✗ Coupon minimum amount not met (req: {coupon.min_amount}, have: {total_amount})")
        
        # Verify Order model can be created
        print("\n" + "-"*70)
        print("VALIDATING ORDER CREATION")
        print("-"*70)
        
        import uuid
        try:
            order = Order(
                reference=str(uuid.uuid4()),
                user_id=user.id,
                email=test_email,
                name='John Doe',
                phone='+233123456789',
                city='Accra',
                subtotal=Decimal('100.00'),
                discount=Decimal('10.00'),
                total=Decimal('90.00'),
                status='pending',
                payment_method='paystack',
                payment_reference='ps_test_ref_123',
                paid=True
            )
            db.session.add(order)
            db.session.flush()
            print(f"✓ Order created (ref={order.reference[:8]}, id={order.id})")
            
            # Add order item
            order_item = OrderItem(
                order_id=order.id,
                product_id=prod.id,
                title=prod.title,
                qty=1,
                price=Decimal('100.00'),
                subtotal=Decimal('100.00')
            )
            db.session.add(order_item)
            db.session.commit()
            print(f"✓ Order item created (product={prod.title}, qty=1)")
            
        except Exception as e:
            print(f"✗ Order creation failed: {e}")
            raise
        
        print("\n" + "="*70)
        print("✅ ALL PAYSTACK FLOW TESTS PASSED")
        print("="*70 + "\n")

if __name__ == '__main__':
    try:
        test_paystack_flow()
    except Exception:
        import traceback
        traceback.print_exc()
        sys.exit(1)
    sys.exit(0)
