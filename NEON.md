# Neon Postgres (Neon) — CI and local test setup

This document explains how to add `NEON_DATABASE_URL` as a GitHub Actions secret and how to run Neon-specific CI tests locally.

## Why use Neon DB secrets
- The project supports `pg8000` and includes tests that simulate driver-specific issues. Neon provides a Postgres-compatible DB for Vercel/production-like testing.
- Setting `NEON_DATABASE_URL` in GitHub Secrets lets CI run integration tests against Neon rather than containerized Postgres when provided.

## Add Neon DB secrets to GitHub
1. Go to your repository -> Settings -> Secrets & variables -> Actions
2. Add a secret named `NEON_DATABASE_URL` with a value of the Neon **pooled** connection string, e.g.:

```
postgresql://neondb_owner:xyz@ep-empty-frog-.../neondb?sslmode=require
```

3. If you require an unpooled connection for migrations or admin jobs, also add `NEON_DATABASE_URL_UNPOOLED`:

```
postgresql://neondb_owner:xyz@ep-empty-frog-.../neondb?sslmode=require
```

> Note: The CI workflows will translate the URL to use `postgresql+pg8000://` for SQLAlchemy automatically when running Neon tests.

## Running Neon tests locally
> Ensure you do not use production data for tests. Use a dedicated Neon test DB.

1. Set your environment to use the Neon URL (pooled):

```pwsh
$env:DATABASE_URL='postgresql+pg8000://neondb_owner:password@ep-empty-frog-.../neondb?sslmode=require'
$env:FLASK_APP='app.py'
```

2. Migrate the DB and run the specific test(s):

```pwsh
python -m flask db upgrade
python -m pytest -q test_admin_settings_pg8000_exception.py::test_admin_settings_handles_pg8000_interface_error
```

## CI: Neon workflow
- CI will automatically run a Neon-specific workflow called `neon-postgres-tests.yml` when `NEON_DATABASE_URL` is present in the repository secrets.

Note: For database migrations the workflows prefer an **unpooled** URL when available so long-running operations are not terminated by connection pooling. If you provide `NEON_DATABASE_URL_UNPOOLED`, it will be used for migrations; otherwise the pooled `NEON_DATABASE_URL` will be used.
- If the secret is not present, the workflow `pg8000-postgres-tests.yml` will instead run a container-based Postgres (docker) job.

## Security notes
- Use a dedicated Neon database with limited permissions for CI and testing. Do not use production credentials for CI.
- Avoid storing secrets in plaintext files in the repository.

## Troubleshooting
- If you see `pg8000.exceptions.InterfaceError` in the app, check `/tmp/last_error.txt` (CI or host tmp dir) for a persisted traceback to help the debugging.
- If the CI job fails to migrate, ensure your Neon URL contains `sslmode=require` and that the DB accepts connections from GitHub Actions (or set CIDR allow rules per provider settings).

If you want, I can also:
- Add a dedicated Neon `test_neon.sh` script to run the Neon test set locally.
- Add an optional job in `deploy.yml` to run database migrations using the unpooled NEON URL during deployment. (This is already partly added in deploy workflows.)
