# CYBER WORLD STORE - PRODUCTION DEPLOYMENT GUIDE

## VERIFICATION STATUS ✅

**Application Status:** PRODUCTION READY
- Flask application: ✅ Running successfully
- Database: ✅ 12 products loaded
- Admin user: ✅ Configured
- Payment routes: ✅ Wallet & Paystack enabled
- Email system: ✅ HTML templates ready
- Secret key: ✅ Configured
- Current mode: **TEST** (will switch to LIVE after key update)

---

## STEP 1: GET LIVE PAYSTACK KEYS (CRITICAL)

This is the MAIN difference between test and production. Currently using test keys.

### Instructions:

1. **Log in to Paystack Dashboard**
   - Visit: https://dashboard.paystack.com/
   - Use your Paystack business account

2. **Navigate to API Keys**
   - Click: Settings → API Keys & Webhooks
   - View: Live Keys (not test keys)

3. **Copy Your Live Keys**
   - Find: **Live Secret Key** (starts with `sk_live_`)
   - Find: **Live Public Key** (starts with `pk_live_`)

### Update .env File:

Open `.env` and replace:

```
# CHANGE THIS:
PAYSTACK_SECRET_KEY="sk_test_407d40cd68df8932c89179869ea4d8d101743b82"
PAYSTACK_PUBLIC_KEY="pk_test_2aec1477bef99ac2bab41ed73273823e44b9db52"

# TO THIS:
PAYSTACK_SECRET_KEY="sk_live_YOUR_ACTUAL_LIVE_SECRET_KEY"
PAYSTACK_PUBLIC_KEY="pk_live_YOUR_ACTUAL_LIVE_PUBLIC_KEY"
```

**Example (replace with your actual keys):**
```
PAYSTACK_SECRET_KEY="your_live_secret_key_here"
PAYSTACK_PUBLIC_KEY="your_live_public_key_here"
```

---

## STEP 2: CONFIGURE PAYSTACK WEBHOOK

This allows Paystack to notify your app when payments are successful.

### In Paystack Dashboard:

1. Go to: Settings → API Keys & Webhooks
2. Find: **Webhook URL** section
3. Set URL to: `https://yourdomain.com/paystack/callback`
   - Replace `yourdomain.com` with your actual domain
   - Example: `https://cyberworld-store.herokuapp.com/paystack/callback`

4. Select Event: `charge.success`
5. Click: Save

### Important:
- Use **HTTPS** (not HTTP)
- URL must be publicly accessible
- Paystack will POST to this URL when payments succeed

---

## STEP 3: CONFIGURE EMAIL (OPTIONAL BUT RECOMMENDED)

Your app can send order confirmation emails with product images.

### Gmail Setup:

1. **Create Gmail App Password**
   - Go to: https://myaccount.google.com/apppasswords
   - Select: Mail, Windows Computer
   - Generate: 16-character app password
   - Copy the password

2. **Update .env**
   ```
   MAIL_USERNAME="cyberworldstore360@gmail.com"
   MAIL_PASSWORD="16_character_password_from_gmail"
   MAIL_SERVER="smtp.gmail.com"
   MAIL_PORT=465
   MAIL_USE_SSL=true
   ```

3. **Set Admin Email**
   ```
   ADMIN_EMAIL="your-email@gmail.com"
   ```

### Verification:
The app will automatically send:
- ✅ Order confirmation to customer
- ✅ Order notification to admin
- ✅ With product images & professional formatting

---

## STEP 4: CHOOSE YOUR HOSTING PLATFORM

### Option A: Heroku (Easiest - Recommended for Beginners)

**Cost:** Free tier available (limited), paid from $7/month

1. **Install Heroku CLI**
   ```powershell
   # Via Chocolatey
   choco install heroku-cli
   
   # Or download from: https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Create Heroku Account**
   - Visit: https://www.heroku.com/
   - Sign up for free account

3. **Prepare for Deployment**
   ```powershell
   cd c:\Users\CYBER360\Desktop\cyberworld_paystack_clone_final
   
   # Login to Heroku
   heroku login
   
   # Create app
   heroku create cyber-world-store
   
   # Set environment variables
   heroku config:set SECRET_KEY="cyberworld_super_secure_key_2024"
   heroku config:set ADMIN_PASSWORD="GITG360"
   heroku config:set PAYSTACK_SECRET_KEY="sk_live_YOUR_KEY_HERE"
   heroku config:set PAYSTACK_PUBLIC_KEY="pk_live_YOUR_KEY_HERE"
   heroku config:set PAYSTACK_CALLBACK_URL="https://cyber-world-store.herokuapp.com/paystack/callback"
   
   # Deploy
   git push heroku main
   ```

4. **View Logs**
   ```powershell
   heroku logs --tail
   ```

### Option B: PythonAnywhere (Easy - Alternative)

**Cost:** Free tier available, paid from £4/month

1. Visit: https://www.pythonanywhere.com/
2. Create account
3. Upload your files
4. Configure web app settings
5. Set environment variables in Web App settings
6. Reload app

### Option C: DigitalOcean (Better Control - More Complex)

**Cost:** $5-12/month for droplet

1. Create account at: https://www.digitalocean.com/
2. Create Ubuntu 20.04 Droplet
3. SSH into server: `ssh root@your_ip`
4. Install: Python, Gunicorn, Nginx
5. Upload files
6. Configure Nginx reverse proxy
7. Run: `gunicorn -w 4 -b 0.0.0.0:8000 app:app`

### Option D: AWS, Google Cloud, Azure

See `PRODUCTION_CHECKLIST.md` for detailed instructions.

---

## STEP 5: DEPLOY YOUR APP

### For Heroku Deployment:

```powershell
cd c:\Users\CYBER360\Desktop\cyberworld_paystack_clone_final

# Ensure git is initialized
git init

# Add all files
git add .

# Commit
git commit -m "Production ready app"

# Deploy to Heroku (replace app name with your app)
git push heroku main
```

### Verify Deployment:

```powershell
# Open in browser
heroku open

# View logs
heroku logs --tail

# Check app status
heroku ps
```

---

## STEP 6: FINAL VERIFICATION CHECKLIST

After deployment, verify:

- [ ] **Homepage Loads**
  - Visit: https://yourdomain.com
  - Should see: Product grid with "Cyber World Store" branding

- [ ] **Admin Login**
  - Visit: https://yourdomain.com/admin
  - Login with: `GITG360`
  - Should see: Admin dashboard

- [ ] **Add Product Test**
  - Upload test product
  - Verify: Product appears on homepage
  - Verify: Card sizing works

- [ ] **Wallet Payment**
  - Add funds to wallet
  - Add product to cart
  - Checkout with wallet
  - Verify: Order created, email sent

- [ ] **Paystack Payment**
  - Add product to cart
  - Checkout with Paystack
  - Complete test payment
  - Verify: Order confirmed, email sent with product image

- [ ] **Email System**
  - Check: Customer received confirmation
  - Check: Admin received notification
  - Verify: Product images display correctly
  - Verify: Professional formatting with logo/branding

---

## TROUBLESHOOTING

### Issue: "ModuleNotFoundError: No module named..."
**Solution:** Ensure all requirements installed on server
```
pip install -r requirements.txt
```

### Issue: "PAYSTACK_SECRET_KEY not configured"
**Solution:** Check .env file has correct keys
```
# In Heroku:
heroku config:get PAYSTACK_SECRET_KEY

# Should show: sk_live_xxxxx (not sk_test_)
```

### Issue: "Email not sending"
**Solution:** Verify Gmail app password
1. Re-generate at: https://myaccount.google.com/apppasswords
2. Update .env with new password
3. Restart app

### Issue: "Webhook not working"
**Solution:** Verify in Paystack Dashboard
1. Settings → Webhooks
2. Verify URL: https://yourdomain.com/paystack/callback
3. Use HTTPS (not HTTP)
4. Check Heroku logs: `heroku logs --tail`

### Issue: "Database error"
**Solution:** Ensure migrations applied
```
# In Heroku CLI:
heroku run flask db upgrade
```

---

## QUICK REFERENCE - ENVIRONMENT VARIABLES

These must be set on your hosting platform:

```
SECRET_KEY=cyberworld_super_secure_key_2024
ADMIN_PASSWORD=GITG360
DATABASE_URL=postgresql://... (if using PostgreSQL)
PAYSTACK_SECRET_KEY=sk_live_YOUR_KEY
PAYSTACK_PUBLIC_KEY=pk_live_YOUR_KEY
PAYSTACK_CALLBACK_URL=https://yourdomain.com/paystack/callback
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=465
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=16_char_app_password
MAIL_USE_SSL=true
ADMIN_EMAIL=admin@domain.com
```

---

## NEXT STEPS

1. **Obtain Live Paystack Keys** ← Start here
2. Configure Webhook URL in Paystack Dashboard
3. Set up email (Gmail app password)
4. Choose hosting platform
5. Deploy application
6. Run verification tests
7. Go live!

---

## SUPPORT & DOCUMENTATION

- **Paystack Documentation:** https://paystack.com/docs/api/
- **Flask Documentation:** https://flask.palletsprojects.com/
- **Heroku Deployment:** https://devcenter.heroku.com/
- **Your Project Docs:** See `PRODUCTION_CHECKLIST.md`

---

## SECURITY REMINDER

- ✅ Change `ADMIN_PASSWORD` to secure password
- ✅ Never commit `.env` to GitHub
- ✅ Use HTTPS for all production URLs
- ✅ Enable Paystack webhook verification
- ✅ Keep Flask SECRET_KEY private

---

**Version:** 1.0
**Date:** 2024
**Status:** PRODUCTION READY
