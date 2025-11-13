# Paystack Payment System - Quick Reference

**Status: ✅ FULLY OPERATIONAL & TESTED**

---

## What Was Fixed

### 1. Email Branding ✅
- Added "Cyber World Store" header to all emails
- Structured email templates with clear sections
- Professional formatting with dividers and hierarchy

### 2. Checkout Form ✅
- Enhanced visual layout with section headers
- Better order summary display
- Improved payment method selection
- Clear shipping information section

### 3. Paystack Flow ✅
- Order creation from Paystack callback
- Coupon validation and usage tracking
- Email notifications (customer & admin)
- Database persistence with transactions

---

## Payment Flow Overview

```
User Adds Products → Checkout → Fills Details → Selects Payment
                                                        |
                                    ┌───────────────────┴───────────────────┐
                                    |                                       |
                                    v                                       v
                            Wallet Payment                        Paystack Payment
                                    |                                       |
                        Deduct Balance Immediately              Redirect to Paystack
                                    |                                       |
                        Create Order in Database                    Customer Pays
                                    |                                       |
                        Send Confirmation Emails        Return to App (Callback)
                                    |                                       |
                        Show Success Page                Create Order in DB
                                    |                                       |
                                    └───────────────────┬───────────────────┘
                                                       |
                                        Send Confirmation Emails
                                                       |
                                        Show Success Page
```

---

## Email Types

### Customer Emails
1. **Order Confirmation** (immediately after payment)
   - Reference number
   - Items with quantities and prices
   - Payment summary
   - Shipping address

2. **Status Update** (when admin updates order)
   - New status (pending/completed/cancelled)
   - Order reference
   - Amount paid
   - Support contact

### Admin Emails
1. **New Order Notification** (immediately after payment)
   - Customer details
   - Items and amounts
   - Payment verification status
   - Link to admin dashboard

---

## Testing Your Payment Setup

### Test 1: Basic Payment Flow
```
1. Go to http://localhost:5000/
2. Add product to cart
3. Click Checkout
4. Fill in details
5. Click "Pay with Paystack"
6. You'll see Paystack test payment page
```

### Test 2: Wallet Payment
```
1. Register as new customer
2. Admin credits wallet (in admin panel)
3. Add product to cart
4. Checkout
5. Select "Pay with Wallet"
6. Order created immediately
```

### Test 3: Coupon Code
```
1. Admin creates coupon: code=TEST10, discount=10%
2. Checkout
3. Enter "TEST10" in promo code box
4. Click Apply
5. See discount applied
6. Total reduced by 10%
```

---

## Key Settings (.env)

```
# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=465
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_USE_SSL=true
ADMIN_EMAIL=admin@cyberworldstore.com

# Paystack Configuration
PAYSTACK_SECRET_KEY=sk_live_...
PAYSTACK_PUBLIC_KEY=pk_live_...
PAYSTACK_CALLBACK_URL=https://your-domain.com/paystack/callback

# Flask Configuration
SECRET_KEY=your-secret-key
```

---

## Troubleshooting Quick Guide

| Problem | Solution |
|---------|----------|
| Emails not sending | Check MAIL_SERVER and credentials in .env |
| Order not created | Check database is writable, product exists |
| Coupon not applying | Verify code, check expiry, check min amount |
| Paystack init fails | Check PAYSTACK_SECRET_KEY in .env |
| Payment callback failing | Check PAYSTACK_CALLBACK_URL matches domain |

---

## Admin Functions

### View Orders
```
/admin/orders - List all orders
- Shows reference, customer, amount, status
- Click order to see details
```

### Update Order Status
```
/admin/order/{id} - View & edit
- Change status: pending → completed → cancelled
- Automatically sends customer notification email
```

### Print Invoice
```
/admin/order/{id}/invoice - Printable receipt
- Show products with thumbnails
- Display customer and payment info
- Click Print button
```

### Export Orders
```
/admin/orders/export - Download CSV
- All order data
- For spreadsheet analysis
```

---

## Database Tables

| Table | Purpose |
|-------|---------|
| order | Main order records |
| order_item | Individual items in orders |
| order_log | Audit trail of changes |
| coupon | Discount codes |
| failed_email | Queue for retry |
| user | Customer accounts |
| wallet | Customer balances |
| product | Product catalog |

---

## Test Paystack Cards

```
Test Card Numbers:
- Visa:          4111 1111 1111 1111
- Mastercard:    5555 5555 5555 4444
- Verve:         5061 0600 0000 0000 (Nigerian)

Expiry:          Any future date (e.g., 12/25)
CVV:             Any 3 digits (e.g., 123)
OTP:             Any 6 digits (e.g., 123456)

Amount:          Use any amount (in naira/cents)
Reference:       Auto-generated UUID
```

---

## API Endpoints

```
# Public Routes
GET  /                            - Homepage
GET  /product/{id}                - Product detail
POST /cart/add/{id}               - Add to cart
GET  /cart                        - View cart
GET  /checkout                    - Checkout page
POST /pay/wallet                  - Wallet payment
POST /pay/paystack                - Paystack init
GET  /paystack/callback           - Payment callback
POST /api/validate-coupon         - Validate coupon

# Auth Routes
POST /login                       - Customer login
POST /register                    - Customer registration
GET  /logout                      - Customer logout
POST /admin/login                 - Admin login
GET  /admin/logout                - Admin logout

# Admin Routes
GET  /admin                       - Admin dashboard
GET  /admin/orders                - Order list
GET  /admin/order/{id}            - Order detail
POST /admin/order/{id}/update_status - Update status
GET  /admin/order/{id}/invoice    - Print invoice
GET  /admin/orders/export         - Export CSV
```

---

## Common Tasks

### Add a New Coupon
```python
# In Python shell with app context:
coupon = Coupon(
    code='SUMMER20',
    discount_type='percent',
    discount_value=Decimal('20'),
    min_amount=Decimal('100'),
    max_uses=100,
    is_active=True
)
db.session.add(coupon)
db.session.commit()
```

### Credit Customer Wallet
```
1. Go to /admin/wallets
2. Click customer name
3. Enter amount
4. Click "Credit Wallet"
```

### Update Product Price
```
1. Go to /admin
2. Click "Edit" on product
3. Change price
4. Click "Save"
```

### View Failed Emails
```python
# In database:
SELECT * FROM failed_email WHERE attempts < 5;
# These will be retried automatically
```

---

## Performance Notes

- **Async Emails:** Don't block user experience
- **Session Cart:** Fast, no database hits for cart
- **Order Creation:** Atomic transaction (all or nothing)
- **Coupon Validation:** In-memory calculation
- **Email Retry:** Background loop every 60 seconds

---

## Security Features

✅ Password hashing (werkzeug)
✅ Session-based auth (Flask-Login)
✅ CSRF protection (Flask forms)
✅ Email validation (parseaddr)
✅ SQL injection safe (SQLAlchemy ORM)
✅ Secure payment gateway (Paystack)
✅ SSL/TLS for SMTP (port 465)

---

## Monitoring

### Check Email Queue
```python
from app import FailedEmail
pending = FailedEmail.query.filter(FailedEmail.attempts < 5).count()
# Should be 0 if all emails sent successfully
```

### Monitor Orders
```python
from app import Order
today_orders = Order.query.filter(
    Order.created_at >= datetime.today()
).count()
# Orders received today
```

### Check Coupon Usage
```python
from app import Coupon
c = Coupon.query.filter_by(code='TEST10').first()
print(f"Used {c.current_uses} / {c.max_uses} times")
```

---

## Deployment Steps

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   # Copy .env.example to .env
   # Fill in production values
   ```

3. **Initialize Database**
   ```bash
   flask db upgrade
   # Or for fresh setup:
   flask initdb
   ```

4. **Start Server**
   ```bash
   gunicorn app:app
   ```

5. **Enable Email Retry Loop** (optional)
   ```python
   # Start in separate process:
   from app import _retry_failed_emails_loop
   _retry_failed_emails_loop()
   ```

---

## Support

**For errors or questions:**
1. Check console logs
2. Check FailedEmail table
3. Check OrderLog for status changes
4. Review app.py email functions
5. Test with Flask test client

**Email Settings:** MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD
**Paystack Keys:** PAYSTACK_SECRET_KEY, PAYSTACK_PUBLIC_KEY
**Admin Email:** ADMIN_EMAIL

---

**Last Updated:** November 12, 2025
**Status:** ✅ Production Ready
