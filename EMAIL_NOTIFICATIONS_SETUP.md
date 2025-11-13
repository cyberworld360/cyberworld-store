# Email Notifications Setup Guide

## Overview
The Cyberworld Paystack Clone application has a complete email notification system that automatically sends order confirmations to **both customers and admin** when payments are made.

## Email Events Triggered

### 1. **Wallet Payment Completion**
- **When**: User pays using wallet balance
- **To Customer**: Order confirmation with itemized list
- **To Admin**: New order alert for processing

### 2. **Paystack Payment Completion**
- **When**: User completes payment via Paystack gateway
- **To Customer**: Order confirmation with itemized list
- **To Admin**: New order alert for processing

## Email Configuration

### Step 1: Create `.env` File

A `.env` file has been created in your project root with the following structure:

```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=cyberworldstore360@gmail.com
MAIL_PASSWORD=your-app-password-here
MAIL_USE_TLS=true
MAIL_USE_SSL=false
MAIL_DEFAULT_SENDER=cyberworldstore360@gmail.com
ADMIN_EMAIL=cyberworldstore360@gmail.com
```

### Step 2: Get Gmail App Password (Recommended)

If using Gmail (free tier supported):

1. **Enable 2-Step Verification** on your Google Account:
   - Go to: https://myaccount.google.com/security
   - Enable "2-Step Verification"

2. **Generate App Password**:
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and "Windows Computer" (or your device)
   - Google will generate a 16-character password
   - Copy this password

3. **Update `.env` File**:
   ```env
   MAIL_PASSWORD=your-16-character-app-password
   ```

### Step 3: Alternative Email Providers

#### **Outlook/Hotmail**
```env
MAIL_SERVER=smtp-mail.outlook.com
MAIL_PORT=587
MAIL_USERNAME=your-email@outlook.com
MAIL_PASSWORD=your-password
MAIL_USE_TLS=true
MAIL_USE_SSL=false
```

#### **SendGrid** (Professional option)
```env
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USERNAME=apikey
MAIL_PASSWORD=SG.your-sendgrid-api-key
MAIL_USE_TLS=true
MAIL_USE_SSL=false
```

#### **Mailgun** (Professional option)
```env
MAIL_SERVER=smtp.mailgun.org
MAIL_PORT=587
MAIL_USERNAME=postmaster@your-domain.mailgun.org
MAIL_PASSWORD=your-mailgun-password
MAIL_USE_TLS=true
MAIL_USE_SSL=false
```

## Email Content Details

### **Customer Email**

#### For Wallet Payments:
```
Subject: Order confirmation — wallet payment [REFERENCE]

Thank you for your order using wallet payment.

Name: John Doe
Phone: 0244123456
City: Accra

Reference: abc123de
Subtotal: GH₵150.00
Discount: -GH₵15.00  (if coupon applied)
Amount Charged: GH₵135.00

Items:
- Nike Air Jordan x2 — GH₵100.00
- Adidas Shoe x1 — GH₵50.00

Wallet balance after payment: GH₵265.00

We will process and ship your order shortly.

Regards,
CyberWorld
```

#### For Paystack Payments:
```
Subject: Order confirmation — reference [REFERENCE]

Thank you for your order.

Reference: abc123de
Amount: GH₵135.00

Items:
- Nike Air Jordan x2 — GH₵100.00
- Adidas Shoe x1 — GH₵50.00

We will process and ship your order shortly.

Regards,
CyberWorld
```

### **Admin Email**

#### For Wallet Payments:
```
Subject: New wallet order received — [REFERENCE]

New wallet payment order received:

Reference: abc123de
Customer: customer@gmail.com
Name: John Doe
Phone: 0244123456
City: Accra

Subtotal: GH₵150.00
Discount Applied: -GH₵15.00 (if applicable)
Amount Charged: GH₵135.00

Items:
- Nike Air Jordan x2 — GH₵100.00
- Adidas Shoe x1 — GH₵50.00

Process this order in the admin panel.
```

#### For Paystack Payments:
```
Subject: New order received — [REFERENCE]

New order received:

Reference: abc123de
Amount: GH₵135.00
Customer: customer@gmail.com

Items:
- Nike Air Jordan x2 — GH₵100.00
- Adidas Shoe x1 — GH₵50.00

Process this order in the admin panel.
```

## Fallback Behavior

If SMTP is **not configured** (MAIL_SERVER or MAIL_USERNAME missing):
- **Emails are NOT sent to users/admin**
- Instead, email content is **logged to console** for development testing
- Example console output:
  ```
  [email disabled] To: customer@gmail.com Subject: Order confirmation — wallet payment abc12345
  Thank you for your order using wallet payment...
  ```

## Code Implementation Details

### Email Function (`send_email` in app.py)

```python
def send_email(to_address: str, subject: str, body: str):
    """Send a simple plain-text email. This is best-effort and will raise on fatal SMTP errors."""
    if not MAIL_SERVER or not (MAIL_USERNAME and MAIL_PASSWORD):
        # If SMTP not configured, just log to stdout
        print(f"[email disabled] To: {to_address} Subject: {subject}\n{body}")
        return

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = MAIL_DEFAULT_SENDER
    msg["To"] = to_address
    msg.set_content(body)

    context = ssl.create_default_context()
    if MAIL_USE_SSL:
        with smtplib.SMTP_SSL(MAIL_SERVER, MAIL_PORT, context=context) as server:
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.send_message(msg)
    else:
        with smtplib.SMTP(MAIL_SERVER, MAIL_PORT) as server:
            if MAIL_USE_TLS:
                server.starttls(context=context)
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.send_message(msg)
```

### Wallet Payment Flow (Lines 515-545)

**To Customer:**
```python
subject_cust = f"Order confirmation — wallet payment {reference[:8]}"
body_cust = f"Thank you for your order using wallet payment.\n\n"
body_cust += f"Name: {name}\nPhone: {phone}\nCity: {city}\n"
body_cust += f"Reference: {reference}\n"
body_cust += f"Subtotal: GH₵{total:.2f}\n"
if discount > 0:
    body_cust += f"Discount: -GH₵{discount:.2f}\n"
body_cust += f"Amount Charged: GH₵{final_total:.2f}\n\nItems:\n"
for it in items:
    body_cust += f"- {it.get('product')} x{it.get('qty')} — GH₵{it.get('subtotal')}\n"
body_cust += f"\nWallet balance after payment: GH₵{Decimal(current_user.wallet.balance):.2f}\n"
body_cust += "We will process and ship your order shortly.\n\nRegards,\nCyberWorld"
send_email(user_email, subject_cust, body_cust)
```

**To Admin:**
```python
subject_admin = f"New wallet order received — {reference[:8]}"
body_admin = f"New wallet payment order received:\n"
body_admin += f"Reference: {reference}\n"
body_admin += f"Customer: {user_email}\n"
body_admin += f"Name: {name}\nPhone: {phone}\nCity: {city}\n"
body_admin += f"Subtotal: GH₵{total:.2f}\n"
if discount > 0:
    body_admin += f"Discount Applied: -GH₵{discount:.2f}\n"
body_admin += f"Amount Charged: GH₵{final_total:.2f}\n\nItems:\n"
for it in items:
    body_admin += f"- {it.get('product')} x{it.get('qty')} — GH₵{it.get('subtotal')}\n"
body_admin += "\nProcess this order in the admin panel.\n"
send_email(ADMIN_EMAIL, subject_admin, body_admin)
```

### Paystack Payment Flow (Lines 570-597)

**To Customer:**
```python
subject_cust = f"Order confirmation — reference {ref}"
body_cust = f"Thank you for your order.\n\nReference: {ref}\nAmount: GH₵{amount_display}\n\nItems:\n"
for it in items:
    body_cust += f"- {it.get('product')} x{it.get('qty')} — GH₵{it.get('subtotal')}\n"
body_cust += "\nWe will process and ship your order shortly.\n\nRegards,\nCyberWorld"
send_email(user_email, subject_cust, body_cust)
```

**To Admin:**
```python
subject_admin = f"New order received — {ref}"
body_admin = f"New order received:\nReference: {ref}\nAmount: GH₵{amount_display}\nCustomer: {user_email}\n\nItems:\n"
for it in items:
    body_admin += f"- {it.get('product')} x{it.get('qty')} — GH₵{it.get('subtotal')}\n"
body_admin += "\nProcess this order in the admin panel.\n"
send_email(ADMIN_EMAIL, subject_admin, body_admin)
```

## Testing Email Notifications

### Test 1: Verify SMTP Connection (Development)

Without proper SMTP config, emails will log to console:

1. **Start the app**: `python app.py`
2. **Place an order**: Use wallet payment or Paystack
3. **Check console output** for email logs starting with `[email disabled]`

### Test 2: With Gmail (Recommended for Testing)

1. **Set MAIL_PASSWORD** in `.env` to your App Password
2. **Restart app**: `python app.py`
3. **Place an order**
4. **Check email inbox** for confirmation emails

### Test 3: Verify Customer Gets Email

1. **Register** with a test email address
2. **Add products** to cart
3. **Checkout** and complete payment
4. **Check email** for order confirmation (may take 30 seconds)

### Test 4: Verify Admin Gets Email

1. **Check ADMIN_EMAIL** in `.env` (should be set)
2. **Place an order** as customer
3. **Check admin email** for new order alert

## Environment Variables Reference

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `MAIL_SERVER` | Yes (for emails) | "" | SMTP server address (e.g., smtp.gmail.com) |
| `MAIL_PORT` | Yes (for emails) | 587 | SMTP port (587 for TLS, 465 for SSL) |
| `MAIL_USERNAME` | Yes (for emails) | "" | Email account to send from |
| `MAIL_PASSWORD` | Yes (for emails) | "" | Email account password |
| `MAIL_USE_TLS` | No | "true" | Enable TLS encryption (port 587) |
| `MAIL_USE_SSL` | No | "false" | Enable SSL encryption (port 465) |
| `MAIL_DEFAULT_SENDER` | No | MAIL_USERNAME | Display name in "From" field |
| `ADMIN_EMAIL` | Yes | "cyberworldstore360@gmail.com" | Admin email for order alerts |

## Troubleshooting

### Problem: "Emails not sending"

**Solution 1: Check SMTP Configuration**
```bash
# In .env, ensure these are set:
MAIL_SERVER=smtp.gmail.com  # Don't leave empty
MAIL_PORT=587               # 587 for TLS, 465 for SSL
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

**Solution 2: Enable "Less Secure App Access" (Gmail)**
- If not using App Password, allow less secure apps:
- https://myaccount.google.com/lesssecureapps

**Solution 3: Check Console Logs**
- If you see `[email disabled]` in logs, SMTP not configured
- Look for connection errors starting with `SMTP` in logs

### Problem: "Authentication failed"

**Solution:**
1. Verify email/password in `.env`
2. Ensure no extra spaces in credentials
3. For Gmail, use 16-character App Password (not regular password)
4. Check app-specific passwords don't have `-` characters (they do, keep them)

### Problem: "Connection timeout"

**Solution:**
1. Verify MAIL_SERVER is correct
2. Check MAIL_PORT matches MAIL_USE_TLS/SSL settings
3. Ensure firewall isn't blocking outgoing SMTP
4. Try alternate port: 465 (SSL) instead of 587 (TLS)

### Problem: "TLS not available"

**Solution:**
- Set `MAIL_USE_SSL=true` and `MAIL_USE_TLS=false`
- Change `MAIL_PORT=465`

## Features Summary

✅ **Wallet Payment Notifications**
- Customer receives detailed order confirmation
- Admin receives order for processing
- Includes itemized product list
- Shows wallet balance after payment

✅ **Paystack Payment Notifications**
- Customer receives order confirmation
- Admin receives order alert
- Includes itemized product list
- Payment reference provided

✅ **Fallback Mode**
- Works without email configuration (logs to console)
- Perfect for development/testing
- No blocking errors if email fails

✅ **Coupon Support**
- Discount amounts shown in customer/admin emails
- Reflects savings in order summary

✅ **City Information**
- Customer's city included in both customer and admin emails
- Helps with shipping/fulfillment

## Support

For email delivery issues:
- Gmail: https://support.google.com/mail
- Outlook: https://support.microsoft.com/outlook
- SendGrid: https://sendgrid.com/docs
- Mailgun: https://documentation.mailgun.com
