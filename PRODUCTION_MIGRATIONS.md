# Production Migrations Guide

Use these instructions to run migrations against a persistent production database (Neon, Railway, Supabase).

1. Ensure you have the production `DATABASE_URL` connection string.
2. Locally, export it and run migrations:

```powershell
$env:DATABASE_URL='postgresql://user:pass@host:5432/dbname'
$env:FLASK_APP='app.py'
python -m pip install -r requirements.txt
python -m flask db upgrade
```

3. Alternatively, run migrations on a CI runner (recommended). Use the GitHub Actions workflow `.github/workflows/run_migrations_and_smoke.yml` which expects the following repository secrets:
- `DATABASE_URL` — the production database URL
- `DEPLOY_URL` — the public URL for smoke tests (e.g., https://www.cyberworldstore.shop)
- `ADMIN_USER` — admin username or email
- `ADMIN_PASS` — admin password

4. If migrating from SQLite to PostgreSQL:
- Export data from SQLite (if needed) and import into Postgres. Small stores can re-create data via admin UI.

5. Verification:
- After migrations, run smoke tests from the workflow or manually run `scripts/ci_smoke_test.py` with `DEPLOY_URL`, `ADMIN_USER`, and `ADMIN_PASS` set.

