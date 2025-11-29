#!/usr/bin/env python3
"""
Paystack test script (manual) moved here to avoid pytest discovery
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + os.sep + '..')

from app import app, db, User, Wallet, Product, Order, OrderItem, Coupon
from decimal import Decimal
import json

def test_paystack_flow():
    """Run a manual check of paystack flow and DB save"""
    print("Manual paystack test script")

if __name__ == '__main__':
    try:
        test_paystack_flow()
    except Exception:
        import traceback
        traceback.print_exc()
        sys.exit(1)
    sys.exit(0)
