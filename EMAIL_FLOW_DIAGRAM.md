# Email Notification Flow Diagram

## 🔄 Order Processing & Email Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CUSTOMER JOURNEY                             │
└─────────────────────────────────────────────────────────────────────┘

1. CUSTOMER BROWSING
   ├─ Visits website
   ├─ Adds products to cart
   ├─ Proceeds to checkout
   └─ Selects delivery city

2. CHECKOUT PAGE
   ├─ Enters name, phone, city
   ├─ Applies coupon (optional)
   ├─ Chooses payment method:
   │  ├─ Wallet Payment
   │  └─ Paystack Payment
   └─ Submits order

3A. WALLET PAYMENT PATH
    │
    ├─→ Validate wallet balance
    │   ├─ If insufficient → Redirect to Paystack
    │   └─ If sufficient → Deduct from balance
    │
    ├─→ Update order status
    │   ├─ Save order reference
    │   ├─ Clear shopping cart
    │   └─ Display success message
    │
    ├─→ ✉️ SEND EMAIL TO CUSTOMER
    │   ├─ Subject: "Order confirmation — wallet payment [REF]"
    │   ├─ Content:
    │   │  ├─ Customer name, phone, city
    │   │  ├─ Order reference number
    │   │  ├─ Itemized product list
    │   │  ├─ Subtotal amount
    │   │  ├─ Coupon discount (if applied)
    │   │  ├─ Final total charged
    │   │  └─ New wallet balance
    │   └─ Status: Plain text email
    │
    └─→ ✉️ SEND EMAIL TO ADMIN
        ├─ Subject: "New wallet order received — [REF]"
        ├─ Content:
        │  ├─ Customer email address
        │  ├─ Customer name, phone, city
        │  ├─ Order reference number
        │  ├─ Itemized product list
        │  ├─ Subtotal amount
        │  ├─ Coupon discount (if applied)
        │  ├─ Total amount charged
        │  └─ "Process this order in admin panel"
        └─ Sent to: ADMIN_EMAIL from .env

3B. PAYSTACK PAYMENT PATH
    │
    ├─→ Store pending order in session
    │   ├─ Save items list
    │   ├─ Save amounts
    │   └─ Create Paystack payment link
    │
    ├─→ Redirect to Paystack
    │   ├─ User completes payment at Paystack
    │   ├─ User returns to callback URL
    │   └─ Verify payment with Paystack API
    │
    ├─→ Update order status (if verified)
    │   ├─ Save order reference
    │   ├─ Clear shopping cart
    │   └─ Display success message
    │
    ├─→ ✉️ SEND EMAIL TO CUSTOMER
    │   ├─ Subject: "Order confirmation — reference [REF]"
    │   ├─ Content:
    │   │  ├─ Order reference number
    │   │  ├─ Amount paid
    │   │  ├─ Itemized product list
    │   │  └─ "We will process and ship shortly"
    │   └─ Status: Plain text email
    │
    └─→ ✉️ SEND EMAIL TO ADMIN
        ├─ Subject: "New order received — [REF]"
        ├─ Content:
        │  ├─ Customer email address
        │  ├─ Order reference number
        │  ├─ Amount charged
        │  ├─ Itemized product list
        │  └─ "Process this order in admin panel"
        └─ Sent to: ADMIN_EMAIL from .env

4. EMAIL DELIVERY
   │
   ├─→ SMTP Server (Gmail/Outlook/SendGrid/Mailgun)
   │   ├─ Authentication with credentials
   │   ├─ TLS/SSL encryption
   │   └─ Send message
   │
   ├─→ EMAIL DELIVERED TO CUSTOMER
   │   └─ Customer inbox receives order confirmation
   │
   └─→ EMAIL DELIVERED TO ADMIN
       └─ Admin inbox receives order notification

5. FULFILLMENT
   ├─ Admin logs into admin panel
   ├─ Views new orders
   ├─ Processes and ships order
   └─ ✅ Order complete


┌─────────────────────────────────────────────────────────────────────┐
│                         EMAIL SOURCES IN CODE                        │
└─────────────────────────────────────────────────────────────────────┘

WALLET PAYMENT EMAILS:
├─ Location: app.py, lines 515-545
├─ Triggered: After wallet deduction succeeds
├─ Files involved:
│  ├─ templates/checkout.html (form submission)
│  ├─ app.py (wallet_payment route)
│  └─ .env (SMTP credentials)
└─ Emails sent: 2 (customer + admin)

PAYSTACK PAYMENT EMAILS:
├─ Location: app.py, lines 570-597
├─ Triggered: After Paystack verification succeeds
├─ Files involved:
│  ├─ templates/checkout.html (initial form)
│  ├─ Paystack API (payment processing)
│  ├─ app.py (paystack_callback route)
│  └─ .env (SMTP credentials)
└─ Emails sent: 2 (customer + admin)


┌─────────────────────────────────────────────────────────────────────┐
│                         CONFIGURATION                                │
└─────────────────────────────────────────────────────────────────────┘

.env FILE (SMTP SETTINGS)
├─ MAIL_SERVER: SMTP server address
│  └─ Gmail: smtp.gmail.com
│  └─ Outlook: smtp-mail.outlook.com
│
├─ MAIL_PORT: SMTP port number
│  └─ 587 (for TLS)
│  └─ 465 (for SSL)
│
├─ MAIL_USERNAME: Sender email address
│  └─ cyberworldstore360@gmail.com
│
├─ MAIL_PASSWORD: Email account password
│  └─ Gmail App Password (16 characters)
│
├─ MAIL_USE_TLS: Enable TLS encryption
│  └─ true (for port 587)
│
├─ MAIL_USE_SSL: Enable SSL encryption
│  └─ true (for port 465)
│
├─ MAIL_DEFAULT_SENDER: Display name in "From" field
│  └─ no-reply@cyberworldstore.shop
│
└─ ADMIN_EMAIL: Admin email for order notifications
   └─ cyberworldstore360@gmail.com


┌─────────────────────────────────────────────────────────────────────┐
│                         FALLBACK BEHAVIOR                            │
└─────────────────────────────────────────────────────────────────────┘

IF SMTP NOT CONFIGURED:
├─ App continues normally (no error)
├─ Emails are NOT sent
├─ Email content printed to console
│  └─ Looks like: [email disabled] To: customer@gmail.com Subject: ...
└─ Perfect for development/testing

IF SMTP CONFIGURED:
├─ Emails are sent normally
├─ Email delivery depends on SMTP provider
├─ Any errors logged to console
└─ May take 30 seconds to arrive

IF SMTP ERROR OCCURS:
├─ Error is caught (try/except block)
├─ App continues (doesn't block)
├─ Error printed to console for debugging
└─ Customer still sees success message


┌─────────────────────────────────────────────────────────────────────┐
│                         STATUS SUMMARY                               │
└─────────────────────────────────────────────────────────────────────┘

✅ IMPLEMENTED:
├─ Email function: send_email() [lines 240-275]
├─ Wallet payment emails [lines 515-545]
├─ Paystack payment emails [lines 570-597]
├─ Customer notifications with order details
├─ Admin notifications with order details
├─ Coupon discount display in emails
├─ City information in emails
├─ SMTP configuration via .env
├─ Fallback to console logging
├─ Error handling (try/except)
└─ SSL/TLS support

📋 CONFIGURATION:
├─ .env file created with defaults
├─ Gmail configuration ready to use
├─ Alternative providers documented
└─ Credentials secured in .env (not in code)

🧪 TESTING:
├─ Development mode: emails print to console
├─ Production mode: emails sent via SMTP
├─ No blocking if email fails
└─ Customers see success even if email fails

📚 DOCUMENTATION:
├─ EMAIL_NOTIFICATIONS_SETUP.md (comprehensive)
├─ EMAIL_QUICK_SETUP.md (5-minute setup)
└─ This file (visual flow diagram)
