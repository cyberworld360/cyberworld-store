# ⚡ Quick Fix for Data Persistence (Why Logo & Products Disappear)

## The Problem
Your Vercel deployment uses SQLite at `/tmp/data.db`, which is **ephemeral** (temporary). Every time the Vercel function restarts, `/tmp` is wiped clean — so all products, logo uploads, and orders disappear.

## The Solution (Choose One)

### ✅ RECOMMENDED: Use Neon PostgreSQL (Free, 5 minutes)

1. **Visit https://neon.tech and sign up**
2. **Create a new project**
3. **Copy the connection string** (it looks like: `postgresql://user:password@host/dbname`)
4. **Go to Vercel Dashboard:**
   - Your Project → Settings → Environment Variables
   - Add: `Name: DATABASE_URL` | `Value: [paste your PostgreSQL URL]`
   - Scope: Production, Preview, Development
   - Click Save
5. **Deploy:** `git push origin main`
6. **Test:** Log in to `/admin/login`, add a product, refresh the page — it should persist!

### Alternative: Railway.app
Similar process, just visit https://railway.app instead

### Emergency: Use PowerShell Setup Script
```powershell
.\setup_persistence.ps1
```
This will guide you through the setup interactively.

---

## What's Already Done ✅
- ✅ Code updated to check `DATABASE_URL` environment variable first
- ✅ Documentation added (`DATABASE_PERSISTENCE_FIX.md`)
- ✅ Warning messages added to logs for debugging
- ✅ Setup script created for guided installation
- ✅ Changes committed and pushed to GitHub

## What You Need to Do
1. Create a free PostgreSQL database (Neon recommended)
2. Set `DATABASE_URL` in Vercel environment variables
3. Redeploy (or wait for GitHub Actions to trigger)
4. Test that products persist after refresh

---

## Files to Reference
- `DATABASE_PERSISTENCE_FIX.md` — Full detailed instructions
- `setup_persistence.ps1` — Interactive setup helper
- `app.py` lines 80-97 — Database configuration logic

