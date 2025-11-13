# 🚀 Heroku Deployment Guide for CyberWorld Store

## Prerequisites
- Heroku account (free): https://www.heroku.com
- Heroku CLI installed: https://devcenter.heroku.com/articles/heroku-cli
- Git installed (usually already installed)

---

## ✅ Step 1: Prepare Your Local Repository

```powershell
# Navigate to your project directory
cd c:\Users\CYBER360\Desktop\cyberworld_paystack_clone_final

# Initialize git if not already done
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit - CyberWorld e-commerce app with Paystack integration"
```

---

## 🔑 Step 2: Login to Heroku CLI

```powershell
# Login to Heroku (opens browser for authentication)
heroku login

# Verify login
heroku auth:whoami
```

---

## 🆕 Step 3: Create Heroku App

```powershell
# Option A: Let Heroku generate a name (recommended for first time)
heroku create

# Option B: Use a specific app name (must be unique globally)
heroku create your-app-name

# Example:
heroku create cyberworld-shop
```

**Save the app name shown in the output** - you'll need it for all future commands.

---

## 🚀 Step 4: Deploy Your Code to Heroku

```powershell
# Push code to Heroku (this builds and deploys your app)
git push heroku main

# If using 'master' branch instead of 'main':
# git push heroku master

# The deployment output will show:
# - Build process
# - Dependencies installation
# - Startup log
# - Your app URL (something like: https://your-app-name.herokuapp.com)
```

---

## ⚙️ Step 5: Set Environment Variables

Replace values with your actual credentials:

```powershell
# Set all config variables at once
heroku config:set `
  SECRET_KEY="your-super-secret-key-here" `
  ADMIN_PASSWORD="your-secure-admin-password" `
  PAYSTACK_SECRET_KEY="sk_live_your_actual_secret_key" `
  PAYSTACK_PUBLIC_KEY="pk_live_your_actual_public_key" `
  PAYSTACK_CALLBACK_URL="https://your-app-name.herokuapp.com/paystack/callback" `
  FLASK_ENV="production" `
  --app your-app-name

# Verify variables were set
heroku config --app your-app-name
```

---

## 🗄️ Step 6: Initialize Database

```powershell
# Run database initialization on Heroku
heroku run python -c "from app import app, db; app.app_context().push(); db.create_all()" --app your-app-name

# Verify success - you should see output confirming database creation
```

---

## 🌐 Step 7: Test Your Deployed App

```powershell
# Open app in browser (uses your Heroku URL)
heroku open --app your-app-name

# Or check URL manually
heroku apps:info --app your-app-name
```

**Visit:**
- **Homepage:** https://your-app-name.herokuapp.com
- **Admin Login:** https://your-app-name.herokuapp.com/admin/login
- **Credentials:** admin / your-admin-password

---

## 🔗 Step 8: Add Custom Domain (cyberworldstore.shop)

### Add domain to Heroku
```powershell
# Add your domain (both www and root)
heroku domains:add www.cyberworldstore.shop --app your-app-name
heroku domains:add cyberworldstore.shop --app your-app-name

# View DNS targets (you'll need these for registrar)
heroku domains --app your-app-name
```

You'll see output like:
```
Domain                          DNS Target
www.cyberworldstore.shop        some-id.herokudns.com
cyberworldstore.shop            some-id.herokudns.com
```

### Update DNS at Your Registrar (GoDaddy, Namecheap, etc.)

1. Login to your domain registrar
2. Find DNS Management / DNS Settings
3. Create these records:

**For www subdomain:**
- Type: CNAME
- Name/Host: www
- Value/Points To: (the DNS target from Heroku)
- TTL: 3600

**For root domain (cyberworldstore.shop):**
- Type: A or ALIAS/ANAME (if your registrar supports it)
- Value: (the DNS target's IP, or use ALIAS if available)
- TTL: 3600

If your registrar doesn't support ALIAS for root:
- Use a redirect service, or
- Use Cloudflare (free DNS with ALIAS support)

---

## 🔒 Step 9: Enable Automatic HTTPS

```powershell
# Heroku provides free SSL certificates via Let's Encrypt
heroku certs:auto:enable --app your-app-name

# Verify SSL setup
heroku certs:auto --app your-app-name
```

Wait 5-10 minutes for certificate provisioning.

---

## ✨ Step 10: Update Paystack Callback URL

After domain is live on HTTPS, update your Paystack dashboard:

1. Go to Paystack Dashboard
2. Settings → API Keys & Webhooks
3. Update Webhook URL to: `https://cyberworldstore.shop/paystack/callback`
4. Test with a small transaction

---

## 🔍 Monitoring & Logs

```powershell
# View real-time logs
heroku logs --tail --app your-app-name

# View last 100 lines
heroku logs -n 100 --app your-app-name

# View only app errors
heroku logs --grep "ERROR" --app your-app-name
```

---

## 📊 Useful Commands Reference

```powershell
# View all your Heroku apps
heroku apps

# Check app info
heroku apps:info --app your-app-name

# Scale web dynos (ensure at least 1)
heroku ps:scale web=1 --app your-app-name

# Restart app
heroku restart --app your-app-name

# Run a one-off command
heroku run bash --app your-app-name

# Set single variable
heroku config:set KEY=value --app your-app-name

# Unset variable
heroku config:unset KEY --app your-app-name

# Delete app
heroku apps:destroy --app your-app-name --confirm your-app-name
```

---

## 🆘 Troubleshooting

### App Won't Start (H10 Error)
```powershell
# Check logs for errors
heroku logs --tail --app your-app-name

# Likely causes:
# - Missing environment variable
# - Database not initialized
# - Port configuration issue
```

### DNS Not Resolving
- Wait 24-48 hours for DNS propagation
- Check at: https://www.whatsmydns.net/
- Verify registrar DNS records are exact

### SSL Certificate Not Issued
- Wait 5-10 minutes (Let's Encrypt is slow sometimes)
- Ensure domain resolves correctly first
- Check: `heroku certs:auto --app your-app-name`

### Paystack Callback Failing
- Verify PAYSTACK_CALLBACK_URL matches exactly
- Update Paystack dashboard webhook URL
- Check app logs for errors: `heroku logs --tail --app your-app-name`

### Database Issues
```powershell
# Reinitialize database
heroku run python -c "from app import app, db; app.app_context().push(); db.drop_all(); db.create_all()" --app your-app-name
```

---

## 📝 Final Checklist

- [ ] App created on Heroku
- [ ] Code pushed successfully
- [ ] Environment variables configured
- [ ] Database initialized
- [ ] App accessible at https://your-app-name.herokuapp.com
- [ ] Can login to admin: username `admin`, password as set
- [ ] Custom domain added to Heroku
- [ ] DNS records updated at registrar
- [ ] HTTPS working on custom domain
- [ ] Paystack callback URL updated in dashboard
- [ ] Test payment works in sandbox

---

## 🎉 You're Live!

Your app is now deployed and accessible at:
- **https://cyberworldstore.shop** (your custom domain)
- **Admin:** https://cyberworldstore.shop/admin/login

**Start adding products and test the checkout flow!**

---

**Need Help?**
- Heroku Docs: https://devcenter.heroku.com
- Flask Docs: https://flask.palletsprojects.com
- Paystack Docs: https://paystack.com/docs

Last Updated: November 11, 2025
