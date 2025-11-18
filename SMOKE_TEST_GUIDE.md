# Smoke Test Guide

## Local Smoke Tests

### Quick Start
1. Create a `.env` file with test values (see `VERCEL_ENV_EXAMPLE.json` for required keys).
2. Start the Flask app:
   ```bash
   python run.py
   ```
3. In another terminal, run the smoke test script:
   ```pwsh
   pwsh ./tools/smoke_test.ps1 -BaseUrl "http://localhost:5000"
   ```

### What Gets Tested
- `GET /` — home page (should return 200 if public, 302 if redirect to login)
- `GET /admin/login` — admin login page (should return 200)
- `GET /admin/diag` — admin diagnostics endpoint (should return 200 + JSON if authenticated, else 302/401)
- `GET /admin/test-email` — admin test email route (should return 200 + JSON if authenticated, else 302/401)

### Expected Outcomes
- **200 OK**: Endpoint reachable and functional.
- **302 / 401**: If behind login, expected; you may need to authenticate first.
- **Vercel SSO 401 + `_vercel_sso_nonce` cookie**: Indicates the deployment is gated by Vercel SSO on the public site.

## Remote Smoke Tests (Vercel Deployment)

### Prerequisites
1. Ensure Vercel environment variables are set. You can do this:
   - **Via Vercel Dashboard**: Project Settings → Environment Variables.
   - **Via API**: Use `tools/vercel_env_api.py` with a Vercel token.
   - **Via GitHub Actions**: See the workflow at `.github/workflows/deploy_vercel_env.yml`.

### Setting Up GitHub Actions (Optional)
To automatically set Vercel env vars on push to `main`:

1. Add these secrets to your GitHub repo (Settings → Secrets and variables → Actions):
   - `VERCEL_TOKEN`: Your Vercel API token (create at https://vercel.com/account/tokens).
   - `VERCEL_PROJECT`: Your Vercel project ID or slug (from Vercel Dashboard).

2. Update `VERCEL_ENV_EXAMPLE.json` with your actual production values and commit.

3. On next push to `main`, the workflow will run and set all env vars in Vercel.

### Manual Setup via Python Script
```bash
# 1. Copy the example and fill in real values
cp VERCEL_ENV_EXAMPLE.json vercel_env_production.json
# Edit vercel_env_production.json with your actual keys

# 2. Run the script
python tools/vercel_env_api.py \
  --token YOUR_VERCEL_TOKEN \
  --project YOUR_PROJECT_SLUG \
  --env-file vercel_env_production.json

# 3. Trigger a redeploy in Vercel (or push a commit)
```

### Run Remote Smoke Tests
```pwsh
pwsh ./tools/smoke_test.ps1 -BaseUrl "https://your-vercel-deployment-url"
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `401 Unauthorized + _vercel_sso_nonce` | Deployment is gated by Vercel SSO. Disable SSO in Vercel Project Settings or add yourself to the team. |
| `/admin/diag` returns `302 Found` | Admin not authenticated; log in first via `/admin/login`. |
| `vercel_env_api.py` fails with `401` | Vercel token is invalid or expired; regenerate at https://vercel.com/account/tokens. |
| SMTP errors in logs | Check `MAIL_SERVER`, `MAIL_USERNAME`, `MAIL_PASSWORD` are correct in Vercel env vars. |
| Paystack errors | Verify `PAYSTACK_PUBLIC_KEY` and `PAYSTACK_SECRET_KEY` match your Paystack test account keys. |

