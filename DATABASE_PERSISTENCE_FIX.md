# Vercel Data Persistence Fix

## Problem
On Vercel serverless, `/tmp/data.db` (SQLite) is ephemeral and wiped between deployments/invocations. This causes:
- Admin logo uploads disappear
- Products disappear
- Orders disappear
- All data resets after refresh

## Solution: Use PostgreSQL (Recommended)

### Step 1: Create a PostgreSQL Database

Choose one:

#### Option A: Neon (Free PostgreSQL hosting)
1. Go to https://neon.tech
2. Sign up, create a new project
3. Copy the connection string (looks like `postgresql://user:pass@host/dbname`)

#### Option B: Railway.app
1. Go to https://railway.app
2. Create new PostgreSQL plugin
3. Copy connection string

#### Option C: Supabase (PostgreSQL + Auth)
1. Go to https://supabase.com
2. Create new project
3. Go to Database → Connection String
4. Copy PostgreSQL connection string

### Step 2: Add to Vercel Environment Variables

1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Add new variable:
   - **Name:** `DATABASE_URL`
   - **Value:** Your PostgreSQL connection string (e.g., `postgresql://user:password@host:5432/dbname`)
   - **Scope:** Production, Preview, Development

Example PostgreSQL URL:
```
postgresql://postgres:mypassword@db.neon.tech:5432/mydb?sslmode=require
```

### Step 3: Deploy
```bash
git push origin main
```

Vercel will redeploy with the new `DATABASE_URL`. The app will automatically use PostgreSQL instead of SQLite.

### Step 4: Run Migrations (First Time Only)
After first deploy, run:
```bash
vercel env pull  # Get env vars locally
flask db upgrade  # or python -m flask db upgrade
```

Or use the provided migration tool:
```bash
python tools/vercel_env_api.py --token YOUR_TOKEN --project YOUR_PROJECT --env-file DATABASE_URL.json
```

## Alternative: Use Database BLOB Storage (Emergency)

If you can't set up PostgreSQL yet, products/logos are already stored in DB as BLOBs:
- `product.product_image_data` (binary)
- `settings.logo_image_data` (binary)

The app already falls back to BLOB storage. Make sure images are being saved to the database:

Check `app.py` lines 2540-2560 (product image upload logic):
- If S3 is not configured, images default to DB BLOB storage
- Logos are saved in `Settings.logo_image_data`

This persists correctly because the database itself persists (if you move to PostgreSQL).

## Verification

After deploy:
1. Log in to admin (`/admin/login`)
2. Add a product with an image (`/admin/new`)
3. Refresh the page — product should still be there
4. Hard refresh browser (Ctrl+Shift+R) — product should persist

## Recommended Free Options

| Provider | Free Tier | Setup Time |
|----------|-----------|-----------|
| Neon | 0.5 GB, always free | 5 min |
| Railway | $5/month credit | 5 min |
| Supabase | 500 MB | 10 min |
| AWS RDS Free | Yes (1 year) | 15 min |

**Recommended: Neon** (easiest, always free, reliable)

