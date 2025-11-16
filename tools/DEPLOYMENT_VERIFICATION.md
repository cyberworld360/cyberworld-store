# Deployment Status & Verification Scripts

Two scripts to diagnose deployment status and verify the new API route is live.

## Scripts

### 1. `check_vercel_deployment.py` — Fetch Vercel Build Logs

Connects to Vercel API to check deployment status and build logs.

**Requirements:**
- `VERCEL_TOKEN` env var (get from https://vercel.com/account/tokens)

**Usage:**
```bash
# Add token to .env:
echo "VERCEL_TOKEN=your_token_here" >> .env

# Check deployment status:
python tools/check_vercel_deployment.py

# Fetch full build logs:
python tools/check_vercel_deployment.py --logs

# Check specific project/team:
python tools/check_vercel_deployment.py --project cyberworld-store --team your-team-id
```

**Output:**
- Lists recent deployments (commit, branch, status)
- Shows deployment states: `READY`, `BUILDING`, `ERROR`
- If `--logs` flag used: prints full build log from latest deployment

**Interpretation:**
- `READY` = Deployed and serving traffic ✅
- `BUILDING` = Still building, wait a few minutes ⏳
- `ERROR` = Build failed, check logs for errors ❌

### 2. `verify_production_route.py` — Test the API Endpoint Live

Directly hits the production `/admin/settings/api` route to confirm deployment.

**Requirements:**
- Production domain reachable
- Optional: `ADMIN_API_TOKEN` env var (default: `our-FATHER-360`)

**Usage:**
```bash
# Test with defaults:
python tools/verify_production_route.py

# Test custom domain/token:
python tools/verify_production_route.py --url https://your-domain.com --token your-token

# Test from production:
python tools/verify_production_route.py --url https://www.cyberworldstore.shop
```

**Output:**
- **Status 200** = Route found and deployed ✅
- **Status 404** = Route not found; code not deployed yet ❌
- **Status 403** = Token invalid or Vercel security blocking
- **Error/Timeout** = Domain unreachable or Vercel down

**Tests performed:**
1. GET `/admin/settings/api` → reads current settings
2. POST `/admin/settings/api` → updates settings with test data
3. GET `/` → sanity check (home page reachable)

## Quick Diagnosis Workflow

### If you see 404 on production:

```bash
# Step 1: Check Vercel build status
python tools/check_vercel_deployment.py

# Step 2: If status is ERROR, see build logs
python tools/check_vercel_deployment.py --logs

# Step 3: Fix any build errors, then push again
git add -A
git commit -m "Fix build issue"
git push origin main

# Step 4: Wait ~2-3 minutes for Vercel to rebuild
# Then check again
python tools/check_vercel_deployment.py --logs
```

### If 200 but still having issues:

```bash
# Verify the route works and test settings update
python tools/verify_production_route.py --url https://www.cyberworldstore.shop --token our-FATHER-360
```

## Environment Variables

Add these to `.env` for convenience (optional):

```env
# Vercel API access (get from https://vercel.com/account/tokens)
VERCEL_TOKEN=your_vercel_token_here

# Vercel project/team (optional, usually auto-detected)
VERCEL_PROJECT_NAME=cyberworld-store
VERCEL_TEAM_ID=your-team-id

# Production domain and API token
LIVE_DOMAIN=https://www.cyberworldstore.shop
ADMIN_API_TOKEN=our-FATHER-360
```

## Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| `VERCEL_TOKEN not set` | Token missing from .env | Add `VERCEL_TOKEN=...` to `.env` or env vars |
| `Connection refused` | Vercel API down or network issue | Check Vercel status; retry |
| Build status `ERROR` | Code has syntax/runtime errors | Check logs with `--logs` flag and fix |
| Route returns `404` | Code not deployed yet | Wait 2-3 min; retry; check if build succeeded |
| Route returns `403` | Token invalid or WAF blocking | Verify token; check Vercel security rules |
| Timeout | Vercel down or firewall blocking | Check Vercel status page; try again later |

## Next Steps

1. **Get Vercel token:**
   - Go to https://vercel.com/account/tokens
   - Create a new token (Personal Tokens)
   - Copy and add to `.env`: `VERCEL_TOKEN=your_token`

2. **Run diagnostic:**
   ```bash
   python tools/check_vercel_deployment.py --logs
   ```

3. **Verify production:**
   ```bash
   python tools/verify_production_route.py
   ```

4. **If still 404:** check Vercel logs for build errors and fix them before redeploying.
