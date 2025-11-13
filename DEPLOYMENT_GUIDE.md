# Domain Configuration Guide for CyberWorld Store
## Redirect cyberworldstore.shop to Your Project

---

## Overview

To point your domain `cyberworldstore.shop` to your Flask application, you need to:
1. Deploy your Flask app to a server
2. Configure DNS settings
3. Set up SSL/HTTPS
4. Configure your web server

---

## Option 1: Using Heroku (Easiest - Free)

### Step 1: Create Heroku Account
- Go to https://www.heroku.com
- Sign up for a free account
- Download Heroku CLI

### Step 2: Prepare Your Project
Create a `Procfile` in your project root:
```
web: gunicorn app:app
```

Install gunicorn:
```bash
pip install gunicorn
```

### Step 3: Deploy to Heroku
```bash
heroku login
heroku create your-app-name
git push heroku main
```

### Step 4: Point Domain to Heroku
1. Go to Heroku dashboard
2. Select your app
3. Go to Settings → Domains
4. Add domain: `cyberworldstore.shop`
5. You'll get a Heroku DNS target

### Step 5: Configure DNS
1. Go to your domain registrar (GoDaddy, Namecheap, etc.)
2. Update DNS settings:
   - **Type:** CNAME
   - **Host:** www
   - **Points to:** your-app-name.herokuapp.com

---

## Option 2: Using PythonAnywhere (Recommended for Beginners)

### Step 1: Create Account
- Go to https://www.pythonanywhere.com
- Sign up (free or paid account)

### Step 2: Upload Your Code
1. Use Git or upload ZIP file
2. Create a new web app
3. Select Flask
4. Configure Python version (3.9+)

### Step 3: Configure Settings
1. Go to Web tab
2. Edit WSGI configuration file
3. Point to your app.py

### Step 4: Point Domain
1. Go to Account → Domains
2. Add domain: `cyberworldstore.shop`
3. Get the DNS target
4. Update DNS at your registrar

### Step 5: Get SSL Certificate
- PythonAnywhere provides free SSL with Let's Encrypt

---

## Option 3: Using DigitalOcean (Most Control)

### Step 1: Create Droplet
- Go to https://www.digitalocean.com
- Create Ubuntu 22.04 LTS droplet
- Minimum: $5/month

### Step 2: Install Dependencies
```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx
```

### Step 3: Deploy Flask App
```bash
# Clone or upload your project
cd cyberworld_paystack_clone_final

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn
```

### Step 4: Configure Gunicorn
Create `/etc/systemd/system/cyberworld.service`:
```ini
[Unit]
Description=CyberWorld Flask App
After=network.target

[Service]
User=root
WorkingDirectory=/root/cyberworld_paystack_clone_final
ExecStart=/root/cyberworld_paystack_clone_final/venv/bin/gunicorn --workers 4 --bind 0.0.0.0:5000 app:app

[Install]
WantedBy=multi-user.target
```

Start service:
```bash
sudo systemctl start cyberworld
sudo systemctl enable cyberworld
```

### Step 5: Configure Nginx Reverse Proxy
Create `/etc/nginx/sites-available/cyberworld`:
```nginx
server {
    listen 80;
    server_name cyberworldstore.shop www.cyberworldstore.shop;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /root/cyberworld_paystack_clone_final/static/;
        expires 30d;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/cyberworld /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 6: Set Up SSL with Let's Encrypt
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d cyberworldstore.shop -d www.cyberworldstore.shop
```

### Step 7: Update DNS
1. Get your DigitalOcean droplet IP
2. Go to domain registrar
3. Create A records:
   - **Host:** @ (or leave blank)
   - **Type:** A
   - **Value:** Your droplet IP
   - **TTL:** 3600

---

## Option 4: Using Docker + Cloud Run (Google Cloud)

### Step 1: Create Docker Image
Your Dockerfile is already ready!

### Step 2: Build Image
```bash
docker build -t cyberworld:latest .
```

### Step 3: Push to Google Cloud
```bash
gcloud auth configure-docker
gcloud builds submit --tag gcr.io/YOUR-PROJECT/cyberworld
```

### Step 4: Deploy
```bash
gcloud run deploy cyberworld \
  --image gcr.io/YOUR-PROJECT/cyberworld \
  --platform managed \
  --region us-central1
```

### Step 5: Map Domain
1. Get Cloud Run URL
2. Update DNS CNAME to Cloud Run URL

---

## DNS Configuration at Registrar

### For All Options:

**Login to your domain registrar** (GoDaddy, Namecheap, Bluehost, etc.)

#### Option A: Using CNAME (if provider supports)
```
Host: www
Type: CNAME
Value: [provider-url]
TTL: 3600
```

#### Option B: Using A Record (IP Address)
```
Host: @ (root)
Type: A
Value: [your-server-ip]
TTL: 3600

Host: www
Type: A
Value: [your-server-ip]
TTL: 3600
```

#### Option C: Using Nameservers
Replace all nameservers with provider's nameservers

---

## SSL/HTTPS Setup

### For Heroku/PythonAnywhere
✅ Automatic free SSL included

### For DigitalOcean
```bash
sudo certbot --nginx -d cyberworldstore.shop
```

### For Other Servers
Use Let's Encrypt:
```bash
sudo apt install certbot
sudo certbot certonly --standalone -d cyberworldstore.shop
```

---

## Environment Variables Configuration

Create `.env` file with production values:

```env
# Flask Configuration
SECRET_KEY=your-super-secret-key-change-this
FLASK_ENV=production

# Database
SQLALCHEMY_DATABASE_URI=sqlite:////path/to/data.db

# Admin
ADMIN_PASSWORD=your-secure-admin-password

# Paystack
PAYSTACK_SECRET_KEY=your-paystack-secret
PAYSTACK_PUBLIC_KEY=your-paystack-public
PAYSTACK_CALLBACK_URL=https://cyberworldstore.shop/paystack/callback

# Server
PORT=5000
```

---

## Testing Your Domain

After setup, test with:

```bash
# Test HTTP
curl http://cyberworldstore.shop

# Test HTTPS
curl https://cyberworldstore.shop

# Check DNS
nslookup cyberworldstore.shop
dig cyberworldstore.shop
```

---

## Troubleshooting

### Domain Not Working
- ✅ Check DNS propagation: https://www.whatsmydns.net
- ✅ Wait 24-48 hours for DNS to propagate
- ✅ Clear browser cache
- ✅ Verify registrar DNS settings

### SSL Certificate Issues
- ✅ Ensure domain resolves correctly
- ✅ Check certificate expiration
- ✅ Renew certificate if expired

### App Not Running
- ✅ Check server logs
- ✅ Verify all dependencies installed
- ✅ Check port 5000 is open
- ✅ Check firewall settings

### Payment Issues
- ✅ Verify Paystack credentials in `.env`
- ✅ Check PAYSTACK_CALLBACK_URL matches domain
- ✅ Test with Paystack sandbox first

---

## Recommended Setup: DigitalOcean + Nginx + Gunicorn

**Why?**
- ✅ Full control
- ✅ Best performance
- ✅ Most reliable
- ✅ Free SSL with Let's Encrypt
- ✅ Affordable ($5-20/month)

**Steps Summary:**
1. Create DigitalOcean account
2. Create $5/month Ubuntu droplet
3. Follow DigitalOcean section above
4. Update DNS to droplet IP
5. Enable SSL certificate
6. Done! 🎉

---

## Production Checklist

Before going live:

- [ ] Change SECRET_KEY to a secure random value
- [ ] Change ADMIN_PASSWORD
- [ ] Set FLASK_ENV=production
- [ ] Verify PAYSTACK_CALLBACK_URL is correct
- [ ] Test payments with Paystack sandbox
- [ ] Enable SSL/HTTPS
- [ ] Set up automatic backups
- [ ] Monitor server logs
- [ ] Test all admin functions
- [ ] Test product uploads
- [ ] Test checkout process
- [ ] Set up error monitoring

---

## Next Steps

1. **Choose your hosting provider** (Heroku, PythonAnywhere, or DigitalOcean)
2. **Deploy your application**
3. **Configure DNS** at your registrar
4. **Set up SSL certificate**
5. **Test everything thoroughly**
6. **Monitor your site**

---

## Support & Resources

- **Heroku Docs:** https://devcenter.heroku.com
- **PythonAnywhere Docs:** https://help.pythonanywhere.com
- **DigitalOcean Docs:** https://docs.digitalocean.com
- **Let's Encrypt:** https://letsencrypt.org
- **Nginx Docs:** https://nginx.org/en/docs

---

**Last Updated:** November 11, 2025
**Project:** CyberWorld Paystack Clone
**Domain:** cyberworldstore.shop
