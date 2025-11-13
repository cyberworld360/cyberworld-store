# Quick Start: Deploy CyberWorld to cyberworldstore.shop

## ⚡ 5-Minute Quick Start

### **Easiest Option: Heroku (Recommended for Quick Start)**

#### 1️⃣ Create Procfile
Create `Procfile` in your project root:
```
web: gunicorn app:app
```

#### 2️⃣ Install Gunicorn Locally
```bash
pip install gunicorn
```

#### 3️⃣ Create Heroku Account
- Go to https://www.heroku.com
- Click "Sign Up"
- Verify email

#### 4️⃣ Install Heroku CLI
- Windows: Download from https://devcenter.heroku.com/articles/heroku-cli
- Or use: `choco install heroku-cli`

#### 5️⃣ Login to Heroku
```bash
heroku login
```

#### 6️⃣ Create Your App
```bash
cd c:\Users\CYBER360\Desktop\cyberworld_paystack_clone_final
heroku create your-app-name
```

#### 7️⃣ Deploy
```bash
git init
git add .
git commit -m "Initial commit"
git push heroku main
```

#### 8️⃣ Map Domain
1. Log in to Heroku Dashboard
2. Go to your app
3. Settings → Domains → Add domain
4. Add: `cyberworldstore.shop`
5. Copy the DNS target (e.g., `your-app-name.herokuapp.com`)

#### 9️⃣ Update DNS at Registrar
Go to your domain registrar (GoDaddy, Namecheap, etc.):
1. Login to your account
2. Find DNS Management
3. Add CNAME record:
   - **Name:** www
   - **Value:** your-app-name.herokuapp.com
   - **TTL:** 3600

#### 🔟 Wait & Test
- DNS takes 5-30 minutes to propagate
- Visit: `https://cyberworldstore.shop`
- Done! 🎉

---

## 🎯 DNS Settings Summary

### At Your Registrar (GoDaddy, Namecheap, etc.):

```
Type: CNAME
Name/Host: www
Value/Points To: [YOUR-HEROKU-URL].herokuapp.com
TTL: 3600
```

### Check DNS Propagation
Go to: https://www.whatsmydns.net
Enter: cyberworldstore.shop

---

## 📝 Environment Variables (Heroku)

```bash
# Set environment variables on Heroku
heroku config:set SECRET_KEY="your-secret-key" --app your-app-name
heroku config:set ADMIN_PASSWORD="strong-password" --app your-app-name
heroku config:set PAYSTACK_SECRET_KEY="your-key" --app your-app-name
heroku config:set PAYSTACK_PUBLIC_KEY="your-key" --app your-app-name
heroku config:set PAYSTACK_CALLBACK_URL="https://cyberworldstore.shop/paystack/callback" --app your-app-name
```

---

## 🔍 Verify Deployment

```bash
# Check Heroku logs
heroku logs --tail

# Open your app
heroku open

# Visit your domain
# https://cyberworldstore.shop
```

---

## ❌ Troubleshooting

### DNS Not Resolving
- Wait 24-48 hours
- Check https://www.whatsmydns.net
- Verify DNS record is correct

### HTTPS Not Working
- Heroku provides free SSL automatically
- May take 5-10 minutes to activate

### App Not Starting
```bash
heroku logs --tail
# Check for errors
```

### Paystack Callback Error
Update PAYSTACK_CALLBACK_URL:
```bash
heroku config:set PAYSTACK_CALLBACK_URL="https://cyberworldstore.shop/paystack/callback"
```

---

## 📊 What You Get

✅ **Free HTTPS/SSL**  
✅ **Free domain mapping**  
✅ **24/7 uptime**  
✅ **Easy deployments**  
✅ **Easy rollbacks**  

---

## 💰 Costs

- **Heroku Free Tier:** Free (limited)
- **Heroku Paid:** $7-25/month
- **Domain:** $10-15/year

---

## 🚀 Next Steps

1. Create Heroku account
2. Install Heroku CLI
3. Run deployment steps above
4. Update DNS at registrar
5. Wait for DNS propagation
6. Visit `https://cyberworldstore.shop`
7. Login admin at `https://cyberworldstore.shop/admin/login`
8. Start adding products!

---

## 📚 Full Documentation

See `DEPLOYMENT_GUIDE.md` for:
- Other hosting options
- Manual server setup
- Docker deployment
- Advanced configurations

---

**Your site will be live at:** `https://cyberworldstore.shop`

**Admin panel:** `https://cyberworldstore.shop/admin/login`

---

Last Updated: November 11, 2025
