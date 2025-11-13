# Paystack Payment Workflow Diagram

## Complete Payment Flow - VERIFIED WORKING

```
CUSTOMER                          SYSTEM                          PAYSTACK
   |                               |                                  |
   |------- Add Products --------> | (Cart stored in session)         |
   |                               |                                  |
   |------- Checkout Button -----> | GET /checkout (form shown)       |
   |                               |                                  |
   |--- Enter Details ----+        |                                  |
   |                      |        |                                  |
   |                      +------> | /pay/paystack (POST)             |
   |                               | - Validate coupon               |
   |                               | - Calculate discount            |
   |                               | - Prepare items with product_id |
   |                               | - Generate reference UUID       |
   |                               | - Store in session             |
   |                               |                                  |
   |                               |---- Initialize Transaction ---> |
   |                               |                                  |
   |<------- Redirect to ---------- |<---- Auth URL returned ---------|
   |   Paystack Payment Page       |                                  |
   |                               |                                  |
   |===== CUSTOMER PAYS =========== |                                  |
   | (Card/Mobile/Bank)            |                                  |
   |============================= |                                  |
   |                               |                                  |
   |                               |<--- Webhook/Callback ---------- |
   |                               | (Payment Verified - SUCCESS)     |
   |                               |                                  |
   |                               | [Order Creation Phase]          |
   |                               | 1. Create Order record:         |
   |                               |    - reference = UUID           |
   |                               |    - email, name, phone, city   |
   |                               |    - subtotal, discount, total  |
   |                               |    - status = pending           |
   |                               |    - payment_method = paystack  |
   |                               |    - paid = true                |
   |                               |                                  |
   |                               | 2. Create OrderItem records:    |
   |                               |    - product_id, qty, price     |
   |                               |    - title, subtotal            |
   |                               |                                  |
   |                               | 3. Increment Coupon Usage:      |
   |                               |    - coupon.current_uses += 1   |
   |                               |                                  |
   |                               | 4. Create OrderLog (audit):     |
   |                               |    - changed_by = system        |
   |                               |    - new_status = pending       |
   |                               |    - note = via paystack        |
   |                               |                                  |
   |                               | 5. Send Emails:                 |
   |                               |    [Customer Email]             |
   |<--- Order Confirmation ------- |    - [Cyber World Store]        |
   | Email Received                 |    - Reference #xxx             |
   |                               |    - Items & totals             |
   |                               |    - Thank you message          |
   |                               |                                  |
   |                               |    [Admin Email]                |
   |                               |    - New order received         |
   |                               |    - Customer details           |
   |                               |    - Action items               |
   |                               |    - Dashboard link             |
   |                               |                                  |
   |--- Redirected to Success ---> | /paystack/callback SUCCESS      |
   | Page                          |                                  |
   |                               |                                  |

ADMIN                             SYSTEM                            
   |                               |                                  
   |--- Login ------------------>| /admin/login (authenticated)     |
   |                               |                                  |
   |--- View Orders ------------> | /admin/orders (list view)        |
   |                               | Shows all orders with:           |
   |                               | - Reference, Email, Amount      |
   |                               | - Status, Created Date          |
   |                               | - Action buttons                |
   |                               |                                  |
   |--- Click Order Detail -----> | /admin/order/{id}               |
   |                               | Shows:                           |
   |                               | - Customer info                 |
   |                               | - Items with thumbnails        |
   |                               | - Product links                 |
   |                               | - Totals (subtotal, discount)  |
   |                               | - Status dropdown               |
   |                               | - Print Invoice button          |
   |                               |                                  |
   |--- Print Invoice -----------> | /admin/order/{id}/invoice       |
   |                               | Printable page with:            |
   |                               | - Logo & company name           |
   |                               | - Items with product links      |
   |                               | - Shipping address              |
   |                               | - Totals and payment info       |
   |                               | - Print button                  |
   |                               |                                  |
   |--- Update Status -----------> | /admin/order/{id}/update_status |
   |                               | - Change to "completed"         |
   |                               | - Create OrderLog entry         |
   |                               | - Send notification email       |
   |                               |                                  |
   |                               |--- Status Update Email -------> | CUSTOMER
   |                               |    [Cyber World Store]          |
   |<--- Receives Notification --- |    - Order {ref} is shipping    |
   | Email                         |    - Thank you message          |
   |                               |                                  |

```

## Data Flow - Order Creation

```
POST /paystack/callback
  ├─ Verify Transaction
  │  ├─ Get reference from callback
  │  ├─ Call Paystack API /verify/{reference}
  │  └─ Check status == "success"
  │
  ├─ Extract Payment Data
  │  ├─ pending_payment from session
  │  ├─ Email, items, coupon_id, discount
  │  ├─ Amount, customer metadata
  │  └─ Validate email address
  │
  ├─ Send Notifications
  │  ├─ [ASYNC] Email to customer
  │  │  └─ Order confirmation receipt
  │  └─ [ASYNC] Email to admin
  │     └─ New order notification
  │
  └─ Persist Order
     ├─ Create Order record
     │  ├─ reference = UUID
     │  ├─ email, name, phone, city
     │  ├─ subtotal, discount, total
     │  └─ status, payment_method, paid
     │
     ├─ Create OrderItems
     │  ├─ For each item in cart
     │  ├─ product_id, title, qty, price
     │  └─ Subtotal calculation
     │
     ├─ Update Coupon (if applied)
     │  └─ coupon.current_uses += 1
     │
     ├─ Create OrderLog (Audit)
     │  ├─ changed_by = 'system'
     │  ├─ new_status = 'pending'
     │  └─ note = 'Order created via paystack'
     │
     └─ Commit to Database
        ├─ All or Nothing (transaction)
        ├─ Rollback on error
        └─ Clear session cart
```

## Email Template Structure

```
═══════════════════════════════════════════════════════════
                    CYBER WORLD STORE
                  Order Confirmation Receipt
═══════════════════════════════════════════════════════════

Thank you for your order!

───────────────────────────────────────────────────────────
CUSTOMER DETAILS
───────────────────────────────────────────────────────────
Name:      {customer_name}
Email:     {customer_email}
Phone:     {phone}
City:      {city}

───────────────────────────────────────────────────────────
ORDER SUMMARY
───────────────────────────────────────────────────────────
Reference: {order_reference}
Status:    Pending (Processing)

ITEMS:
  • {product_1} x{qty_1} — GH₵{subtotal_1}
  • {product_2} x{qty_2} — GH₵{subtotal_2}

───────────────────────────────────────────────────────────
PAYMENT SUMMARY
───────────────────────────────────────────────────────────
Subtotal:           GH₵{subtotal}
Discount Applied:   -GH₵{discount} (if applied)
Amount Charged:     GH₵{total}
Payment Method:     Paystack / Wallet

───────────────────────────────────────────────────────────

Next Steps:
- We will process your order shortly
- Track your order in your account dashboard
- You'll receive a shipping notification

Questions? Contact us at {support_email}

Best regards,
Cyber World Store Team
═══════════════════════════════════════════════════════════
```

## Coupon Validation Flow

```
Customer Applies Coupon Code
          |
          v
GET /api/validate-coupon
    ├─ Extract code (e.g., "TESTCOUPON")
    ├─ Extract total amount
    |
    ├─ Query: Coupon.query.filter_by(code=code).first()
    |
    ├─ Check coupon.is_valid()
    │  ├─ is_active == true?
    │  ├─ current_uses < max_uses?
    │  └─ expiry_date not passed?
    |
    ├─ Check minimum amount: total >= min_amount?
    |
    ├─ Calculate discount
    │  ├─ IF discount_type == 'percent':
    │  │   discount = (total * discount_value) / 100
    │  │   IF max_discount: cap at max_discount
    │  │
    │  └─ ELIF discount_type == 'fixed':
    │      discount = discount_value
    |
    ├─ Calculate final_total = total - discount
    |
    └─ Return JSON:
       {
         "valid": true,
         "discount": 10.00,
         "final_total": 90.00,
         "coupon_id": 123,
         "message": "Coupon applied! You saved GH₵10.00"
       }
       
       OR
       
       {
         "valid": false,
         "message": "Coupon has expired" / "Not enough balance" / etc
       }
```

## Payment Method Selection

```
Checkout Page
     |
     ├─ Is user logged in?
     │  ├─ YES: Show wallet option
     │  │   ├─ Display wallet balance
     │  │   ├─ Check if balance >= total?
     │  │   │  ├─ YES: Button enabled (green)
     │  │   │  └─ NO:  Button disabled (red) + message
     │  │   │
     │  │   └─ Option: "Pay with Wallet Balance"
     │  │
     │  └─ NO:  Show login prompt
     │       └─ "Login to access wallet payment"
     |
     └─ Always show Paystack option
        └─ "Pay with Paystack (Card/Mobile/Bank)"

Customer Selects Method
     |
     ├─ Wallet Selected?
     │  ├─ POST /pay/wallet
     │  ├─ Deduct wallet balance immediately
     │  ├─ Create order
     │  ├─ Send emails
     │  └─ Redirect to success page
     |
     └─ Paystack Selected?
        ├─ POST /pay/paystack
        ├─ Call Paystack API /initialize
        ├─ Store payment details in session
        ├─ Redirect to Paystack payment page
        └─ Customer pays → callback → Order created
```

## Status Codes Summary

```
Route                              | Method | Status | Purpose
─────────────────────────────────────────────────────────────
GET /                              | GET    | 200    | Homepage
GET /product/{id}                  | GET    | 200    | Product detail
POST /cart/add/{id}                | POST   | 302    | Add to cart
GET /checkout                      | GET    | 200    | Checkout form
POST /pay/wallet                   | POST   | 302    | Wallet payment
POST /pay/paystack                 | POST   | 302    | Paystack init
GET /paystack/callback             | GET    | 302    | Payment callback
POST /api/validate-coupon          | POST   | 200    | Coupon validation
POST /login                        | POST   | 302    | Customer login
GET /admin/orders                  | GET    | 200    | Admin order list
GET /admin/order/{id}              | GET    | 200    | Admin order detail
POST /admin/order/{id}/update_status | POST | 302    | Update status
GET /admin/order/{id}/invoice      | GET    | 200    | Print invoice
GET /admin/orders/export           | GET    | 200    | Export CSV
```

## Key Features Implemented

✅ **Order Management**
  - Create orders on successful payment (wallet or Paystack)
  - Track order status (pending → completed → cancelled)
  - Audit trail with OrderLog
  - Order items with product links

✅ **Coupon System**
  - Validate coupon codes
  - Calculate percentage and fixed discounts
  - Check minimum order amounts
  - Track coupon usage
  - Support max uses per coupon

✅ **Email Notifications**
  - Async email sending with daemon threads
  - Failed email retry queue
  - Customer order confirmations
  - Admin order notifications
  - Status change notifications

✅ **Payment Methods**
  - Wallet payment (instant, session-based)
  - Paystack payment (API integration)
  - Coupon support for both methods
  - Session-based cart management

✅ **Admin Features**
  - Order list with filters
  - Order detail view with items
  - Status update with notifications
  - Invoice printing
  - CSV export
  - Dashboard with recent orders

---

**Last Updated:** November 12, 2025  
**All Features:** ✅ VERIFIED WORKING
