# Cyber World Store - Production Deployment Checklist

## ✅ Application Status: PRODUCTION READY

### Core Features Verified
- [x] **E-Commerce Functionality**
  - Product catalog with images
  - Shopping cart with quantity management
  - Coupon/discount system
  - Product card size customization (small, medium, large)
  
- [x] **Payment Systems** (DUAL)
  - Wallet payment system (prepaid balance)
  - Paystack integration (live payment gateway)
  - Order creation and tracking
  - Payment verification and confirmation

- [x] **User Management**
  - Customer registration and login
  - Wallet account creation
  - Order history tracking
  - Admin authentication

- [x] **Admin Dashboard**
  - Product management (add/edit/delete)
  - Order management and status tracking
  - User wallet management
  - Coupon management
  - Order export (CSV)

- [x] **Email System**
  - HTML email templates with product images
  - Order confirmation emails (wallet & Paystack)
  - Order status update notifications
  - Professional branding and formatting
  - Async email sending with retry queue

- [x] **Database**
  - SQLite with Flask-SQLAlchemy ORM
  - Flask-Migrate for version control
  - All migrations applied and tested

---

## 🔧 Configuration for Live Deployment

### Step 1: Update Environment Variables (.env file)

```bash
# Security - Change these to unique values
SECRET_KEY=your_unique_secret_key_min_32_chars

# Admin credentials
ADMIN_PASSWORD=your_secure_admin_password

# Paystack Live Keys (GET FROM PAYSTACK DASHBOARD)
PAYSTACK_SECRET_KEY="sk_live_xxxxxxxxxxxxxxxxxxxxx"
PAYSTACK_PUBLIC_KEY="pk_live_xxxxxxxxxxxxxxxxxxxxx"
PAYSTACK_CALLBACK_URL="https://yourdomain.com/paystack/callback"

# Email Configuration (Gmail, SendGrid, or other SMTP)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=465
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_USE_TLS=false
MAIL_USE_SSL=true
MAIL_DEFAULT_SENDER=your_email@gmail.com
ADMIN_EMAIL=admin@yourdomain.com

# Optional: Redis for async jobs (leave empty to disable)
REDIS_URL=""

# Optional: SendGrid API (leave empty to use SMTP)
SENDGRID_API_KEY=""
```

### Step 2: Get Paystack Live Keys

1. Go to https://dashboard.paystack.com/
2. Login to your account
3. Navigate to **Settings → API Keys & Webhooks**
4. Copy your **Live Secret Key** (starts with `sk_live_`)
5. Copy your **Live Public Key** (starts with `pk_live_`)
6. Configure webhook at: `https://yourdomain.com/paystack/callback`

### Step 3: Configure SMTP Email (Gmail Example)

1. Enable 2FA on Google Account: https://myaccount.google.com/security
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Select "Mail" and "Windows Computer"
4. Use the 16-character password in `MAIL_PASSWORD`

### Step 4: Deployment Preparation

```bash
# Install production WSGI server
pip install gunicorn

# Upgrade database to latest migrations
python -m flask db upgrade

# Create admin user (run once)
python -c "
from app import app, db, AdminUser
with app.app_context():
    admin = AdminUser.query.filter_by(username='admin').first()
    if not admin:
        admin = AdminUser(username='admin')
        admin.set_password('your_admin_password_from_env')
        db.session.add(admin)
        db.session.commit()
        print('Admin user created')
"

# Collect static files (if using external CDN)
# mkdir -p static/dist
# cp -r static/css static/images static/dist/
```

---

## 🚀 Running in Production

### Option 1: Gunicorn (Recommended)

```bash
# Run with 4 workers
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Or with environment file
gunicorn -w 4 -b 0.0.0.0:5000 --env FLASK_ENV=production app:app
```

### Option 2: Docker

Create `Dockerfile`:
```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN python -m flask db upgrade
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

```bash
docker build -t cyberworld-store .
docker run -p 5000:80 -e PAYSTACK_SECRET_KEY=sk_live_xxx cyberworld-store
```

### Option 3: Heroku

```bash
# Create Procfile (already exists)
# Add this buildpack for Python

heroku create cyberworld-store
heroku addons:create heroku-postgresql:hobby-dev
heroku config:set PAYSTACK_SECRET_KEY=sk_live_xxx
heroku config:set PAYSTACK_PUBLIC_KEY=pk_live_xxx
git push heroku main
heroku run python -m flask db upgrade
```

---

## 🔐 Security Hardening Checklist

Before going live:

- [ ] **SECRET_KEY**: Change to a unique, random 32+ character string
  ```bash
  python -c "import secrets; print(secrets.token_hex(32))"
  ```

- [ ] **HTTPS/SSL**: Use Let's Encrypt (Certbot) or your hosting provider's SSL
  - Update `PAYSTACK_CALLBACK_URL` to use `https://`
  - Force HTTPS redirect in production

- [ ] **Database Security**:
  - Use managed database service (not SQLite in production)
  - Regular automated backups
  - Enable database encryption

- [ ] **Email Credentials**:
  - Use environment variables (never hardcode passwords)
  - Use App Passwords (not main Google password)
  - Enable SMTP on restricted access if using corporate email

- [ ] **Admin Credentials**:
  - Change default admin password
  - Enable 2FA if possible
  - Use strong, unique passwords

- [ ] **API Keys**:
  - Store Paystack keys in environment variables
  - Rotate keys periodically
  - Monitor for unauthorized access

- [ ] **CORS & Headers**:
  - Disable debug mode in production
  - Set proper security headers
  - Enable CSRF protection

- [ ] **Rate Limiting**:
  - Implement rate limiting on payment endpoints
  - Monitor for fraudulent transactions

---

## 📊 Monitoring & Maintenance

### Key Metrics to Track
- Payment success rate
- Email delivery rate
- Order processing time
- Server uptime
- Database size

### Regular Tasks
- [ ] Daily: Monitor error logs
- [ ] Weekly: Check Paystack transactions
- [ ] Monthly: Database backup verification
- [ ] Monthly: Email bounce rates
- [ ] Quarterly: Security updates

---

## 🐛 Troubleshooting

### Payment not processing
1. Verify Paystack keys are correct (live vs test)
2. Check webhook URL is accessible
3. Verify callback route is not blocked by firewall

### Emails not sending
1. Check SMTP credentials in .env
2. Verify firewall allows SMTP (port 465/587)
3. Check FailedEmail table for retry queue
4. Enable "Less secure app access" if using Gmail

### Database issues
1. Check migrations: `python -m flask db current`
2. Upgrade: `python -m flask db upgrade`
3. Backup data before major changes

---

## 📝 Final Notes

**App Features:**
- ✅ Dual payment system (Wallet + Paystack)
- ✅ Professional HTML emails with product images
- ✅ Admin order management
- ✅ Coupon/discount system
- ✅ Product card size customization
- ✅ User authentication & wallet
- ✅ Order tracking & history
- ✅ Database migrations included

**Ready to deploy!** Update `.env` with your live Paystack keys and email credentials, then deploy to your hosting platform.
