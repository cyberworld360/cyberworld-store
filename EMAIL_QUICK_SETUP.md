# Email Notifications - Quick Setup

## ⚡ 5-Minute Setup

### Option 1: Gmail (Free & Easiest)

1. **Update `.env` file** (already created):
   ```env
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USERNAME=cyberworldstore360@gmail.com
   MAIL_PASSWORD=YOUR_APP_PASSWORD_HERE
   MAIL_USE_TLS=true
   MAIL_USE_SSL=false
   MAIL_DEFAULT_SENDER=cyberworldstore360@gmail.com
   ADMIN_EMAIL=cyberworldstore360@gmail.com
   ```

2. **Get App Password**:
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" + "Windows Computer"
   - Copy the 16-character password
   - Paste into `.env` as `MAIL_PASSWORD`

3. **Restart app**:
   ```powershell
   .\.venv\Scripts\python.exe app.py
   ```

4. **Test**: Place an order and check email

### Option 2: Test Mode (No Email Required)

Just leave `.env` empty or don't configure SMTP:
- App will run fine ✅
- Emails will print to **console** instead
- Look for `[email disabled]` logs
- Perfect for development

## 📧 What Gets Emailed

### To Customer (After Order)
- Order confirmation
- Items purchased with prices
- Total amount charged
- Delivery address
- Order reference number

### To Admin (After Order)
- New order alert
- Customer details
- Items ordered
- Amount to collect
- Admin panel link

## ✅ Current Status

| Feature | Status |
|---------|--------|
| Wallet Payment Emails | ✅ Enabled |
| Paystack Payment Emails | ✅ Enabled |
| Customer Notifications | ✅ Enabled |
| Admin Notifications | ✅ Enabled |
| Coupon Info in Email | ✅ Included |
| City Information | ✅ Included |

## 🔧 Configuration File Locations

- **Main Config**: `.env` (in project root)
- **Code**: `app.py` (lines 240-275)
- **Wallet Payment Flow**: `app.py` (lines 515-545)
- **Paystack Payment Flow**: `app.py` (lines 570-597)

## 📋 Email Event Examples

### Wallet Payment Email (Customer)
```
TO: customer@gmail.com
SUBJECT: Order confirmation — wallet payment abc12345

Thank you for your order using wallet payment.

Name: John Doe
Phone: 0244123456
City: Accra
Reference: abc12345
Subtotal: GH₵150.00
Discount: -GH₵15.00
Amount Charged: GH₵135.00

Items:
- Nike Air Jordan x2 — GH₵100.00
- Adidas Shoe x1 — GH₵50.00

Wallet balance after payment: GH₵265.00

We will process and ship your order shortly.
Regards, CyberWorld
```

### Paystack Payment Email (Customer)
```
TO: customer@gmail.com
SUBJECT: Order confirmation — reference abc12345

Thank you for your order.

Reference: abc12345
Amount: GH₵135.00

Items:
- Nike Air Jordan x2 — GH₵100.00
- Adidas Shoe x1 — GH₵50.00

We will process and ship your order shortly.
Regards, CyberWorld
```

### New Order Alert (Admin)
```
TO: cyberworldstore360@gmail.com
SUBJECT: New order received — abc12345

New order received:
Reference: abc12345
Amount: GH₵135.00
Customer: customer@gmail.com
Name: John Doe

Items:
- Nike Air Jordan x2 — GH₵100.00
- Adidas Shoe x1 — GH₵50.00

Process this order in the admin panel.
```

## 🆘 Troubleshooting

| Issue | Solution |
|-------|----------|
| Emails not sending | Check if MAIL_SERVER, MAIL_USERNAME set in `.env` |
| Auth failed | Ensure Gmail App Password (16 chars) used, not regular password |
| Timeout error | Try MAIL_SERVER=smtp.gmail.com + MAIL_PORT=465 + MAIL_USE_SSL=true |
| Seeing `[email disabled]` in logs | SMTP not configured - set credentials in `.env` |

## 🚀 Next Steps

1. ✅ Copy `MAIL_PASSWORD` from Gmail App Passwords
2. ✅ Update `.env` with the password
3. ✅ Restart app: `.\.venv\Scripts\python.exe app.py`
4. ✅ Test: Place an order and check inbox
5. ✅ Verify both customer AND admin receive emails

## 📚 Full Documentation

See `EMAIL_NOTIFICATIONS_SETUP.md` for comprehensive guide including:
- Alternative email providers (Outlook, SendGrid, Mailgun)
- Detailed troubleshooting
- Code implementation details
- Environment variables reference
