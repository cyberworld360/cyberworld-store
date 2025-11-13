# ⚡ Email Notifications - Quick Reference Card

## 🎯 Quick Facts

✅ **Already Implemented**: Email notifications are built-in  
✅ **Both Methods Supported**: Wallet payment + Paystack payment  
✅ **Dual Recipients**: Customers receive order confirmations, Admin receives order alerts  
✅ **Zero Setup Required**: Works out of the box (logs to console in dev mode)  
✅ **Easy Activation**: Just add email credentials to `.env`  

## 📧 What Gets Emailed

### **To Customer** (on every order)
- Order reference number
- All items purchased (name, qty, price)
- Total amount charged
- Delivery address (name, phone, city)
- For wallet: New wallet balance
- Confirmation message

### **To Admin** (on every order)
- Order reference number
- Customer email address
- All items ordered (name, qty, price)
- Total amount collected
- Delivery address (name, phone, city)
- Call to action (process in admin panel)

## 🚀 Activation (2 minutes)

### **Step 1: Get Gmail Password**
1. Go: https://myaccount.google.com/apppasswords
2. Select: Mail + Windows Computer
3. Copy: 16-character password

### **Step 2: Update `.env`**
Edit file: `.env` (in project root)
```env
MAIL_PASSWORD=your-16-char-password-here
```

### **Step 3: Restart App**
```powershell
.\.venv\Scripts\python.exe app.py
```

### **Step 4: Test**
1. Create account
2. Add to cart
3. Checkout
4. Check email inbox ✅

## 📍 Email Locations in Code

| What | Where | Line |
|------|-------|------|
| Email function | app.py | 240-275 |
| SMTP config | app.py | 59-69 |
| Wallet → Customer | app.py | 527 |
| Wallet → Admin | app.py | 544 |
| Paystack → Customer | app.py | 585 |
| Paystack → Admin | app.py | 597 |
| Configuration | .env | all |

## ⚙️ Configuration Defaults

```env
MAIL_SERVER=smtp.gmail.com          # Gmail SMTP
MAIL_PORT=587                       # TLS port
MAIL_USERNAME=cyberworldstore360@gmail.com  # Sender email
MAIL_PASSWORD=                      # ← ADD YOUR APP PASSWORD HERE
MAIL_USE_TLS=true                   # Use TLS encryption
MAIL_USE_SSL=false                  # Don't use SSL (we use TLS)
MAIL_DEFAULT_SENDER=cyberworldstore360@gmail.com
ADMIN_EMAIL=cyberworldstore360@gmail.com    # Receives order alerts
```

## 🔄 How It Works

```
WALLET PAYMENT
Customer Places Order → Wallet Deducts → Email to Customer → Email to Admin

PAYSTACK PAYMENT
Customer Places Order → Redirects to Paystack → Payment Verified → 
Email to Customer → Email to Admin
```

## ✅ Verification (3 checks)

### Check 1: Is SMTP Configured?
```
Look at console output when app starts:
- See "[email disabled]" → SMTP not configured (dev mode) ✅
- No error message → SMTP configured or not tested yet
```

### Check 2: Does Wallet Payment Send Emails?
```
1. Create account with real email
2. Add wallet balance
3. Checkout with wallet payment
4. Check both emails arrive in 30 seconds ✅
```

### Check 3: Does Paystack Payment Send Emails?
```
1. Add item to cart
2. Checkout with Paystack payment
3. Complete test payment (card: 4111111111111111)
4. Check both emails arrive in 30 seconds ✅
```

## 🐛 Troubleshooting (30 seconds)

| Problem | Fix |
|---------|-----|
| No emails at all | Configure `.env` with MAIL_PASSWORD |
| Auth failed | Use Gmail App Password (16 chars), not regular password |
| Timeout error | Try MAIL_PORT=465 + MAIL_USE_SSL=true |
| Wrong recipient | Check ADMIN_EMAIL or user registration email |
| In spam folder | Mark as not spam (provider issue, not our code) |

## 📋 Email Examples

### Wallet Payment - Customer
```
TO: john@example.com
SUBJECT: Order confirmation — wallet payment abc12345

Thank you for your order using wallet payment.

Name: John Doe
Phone: 0244123456
City: Accra
Reference: abc12345

Items:
- Nike Shoe x2 — GH₵100.00

Amount Charged: GH₵100.00
Wallet Balance: GH₵250.00

We will process and ship shortly.
```

### Paystack Payment - Admin
```
TO: cyberworldstore360@gmail.com
SUBJECT: New order received — abc12345

New order received:
Reference: abc12345
Amount: GH₵100.00
Customer: john@example.com

Items:
- Nike Shoe x2 — GH₵100.00

Process this order in the admin panel.
```

## 🔐 Security Notes

✅ Credentials stored in `.env` (not in code)  
✅ `.env` should be in `.gitignore` (not committed to git)  
✅ SMTP uses TLS/SSL encryption  
✅ Plain text emails only (no HTML vulnerabilities)  
✅ Email failures don't block order completion  

## 💡 Other Email Providers

### **Outlook**
```env
MAIL_SERVER=smtp-mail.outlook.com
MAIL_PORT=587
MAIL_USERNAME=your-email@outlook.com
MAIL_PASSWORD=your-password
```

### **SendGrid** (Pro)
```env
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USERNAME=apikey
MAIL_PASSWORD=SG.xxx
```

### **Mailgun** (Pro)
```env
MAIL_SERVER=smtp.mailgun.org
MAIL_PORT=587
MAIL_USERNAME=postmaster@your-domain.com
MAIL_PASSWORD=your-mailgun-key
```

## 📚 More Info

- **EMAIL_QUICK_SETUP.md** - Full setup guide
- **EMAIL_NOTIFICATIONS_SETUP.md** - Comprehensive documentation
- **EMAIL_FLOW_DIAGRAM.md** - Visual flow diagrams
- **EMAIL_VERIFICATION_CHECKLIST.md** - Detailed verification
- **EMAIL_IMPLEMENTATION_SUMMARY.md** - Feature overview

## ⏱️ Time Investment

- **Setup**: 2 minutes (get App Password + edit `.env`)
- **Testing**: 5 minutes (place order + check emails)
- **Troubleshooting**: varies (usually 5-10 minutes)

## 🎉 Status

✅ **Code**: Ready  
✅ **Configuration**: Created (needs MAIL_PASSWORD)  
✅ **Documentation**: Complete  
✅ **Testing**: Ready  

**Just add your Gmail App Password and you're done!**

---

*Created: November 12, 2025*  
*App: Cyberworld Paystack Clone*  
*Framework: Flask 2.2.5*
