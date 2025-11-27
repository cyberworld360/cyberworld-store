# Copilot / AI Agent Instructions for cyberworld-store

This file is a concise, actionable guide for AI coding agents (like GitHub Copilot/coding agents) to get productive on this repository quickly.

## Big Picture (What this repo is)
- A Flask-based e-commerce demo app in a single primary module: `app.py`.
- Uses Flask + SQLAlchemy + Flask-Migrate + Flask-Login. Optional integrations: Redis/RQ, SendGrid, SMTP, Paystack (payments).
- Designed to run serverless on Vercel, or locally with a traditional Flask server.
- Key files: `app.py` (app + models + routes), `templates/` (HTML templates), `static/` (images, JS, CSS), `run.py`/`run_server.py` (runners), `deploy_vercel.py` (deployment helper), `requirements.txt`.

## Key Concepts & Architectural Notes
- Single-file Flask app pattern: `app.py` includes models, routes, business logic, and helpers across ~3k lines.
- Database: SQLAlchemy supports PostgreSQL or SQLite fallback. `FORCE_EPHEMERAL=1` allows ephemeral SQLite for Vercel.
- Deployment: uses Vercel (see `deploy_vercel.py`) — keep environment variables in `.env` and/or set via Vercel dashboard.
- Email delivery: can use SMTP or SendGrid. If not configured, email sending logs to stdout (dev-friendly).
- Background processing: RQ optional; email retry loop exists (`_retry_failed_emails_loop`) and is started only under `__main__`.

## Tests & Developer Workflows
- Install dependencies locally and create a venv:

  PowerShell (Windows):
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate
  python -m pip install -r requirements.txt
  ```

- Local dev server:
  - `python run_server.py` or `python run.py` (non-debug) — `run_server.py` avoids reloader/async issues on Windows.

- Running tests (note: many tests are E2E and hit HTTP endpoints or external services):
  - For quick local checks, force a local sqlite DB and disable external services to avoid network:

  ```powershell
  $env:DATABASE_URL='sqlite:///./data.db'
  $env:FORCE_EPHEMERAL='1'
  $env:MAIL_SERVER=''
  $env:MAIL_USERNAME=''
  $env:MAIL_PASSWORD=''
  $env:PAYSTACK_PUBLIC=''
  $env:PAYSTACK_SECRET=''
  .\.venv\Scripts\python.exe -m pytest -q -k "not e2e and not paystack and not email"
  ```

  - If a test hangs, suspect network calls (requests to Paystack, SendGrid, or local admin endpoints). Re-run a focused test with `-k` to isolate.

- CLI helpers:
  - `python -m flask initdb` (the repo exposes `app.cli.command('initdb')`) to create tables and defaults.
  - `python -m py_compile app.py` or `python -m compileall -q .` to perform a quick syntax check.

## Code Patterns and Conventions (project-specific)
- Environment variables control optional features. Important envs include: `DATABASE_URL`, `REDIS_URL`, `FORCE_EPHEMERAL`, `PAYSTACK_SECRET_KEY`, `PAYSTACK_PUBLIC_KEY`, `MAIL_*`, `SENDGRID_API_KEY`, `AUTO_MIGRATE`.
- `load_dotenv()` is a custom minimal loader. Don't replace it with heavy dotenv libraries unless needed.
- Avoid starting long-running threads or performing network I/O at module import; instead wrap these in `__main__` or guard via `if app.testing` or `if os.environ.get('CI') == '1'`.
- When adding tests, mock network calls (`requests`) or set env to a local test server.

## Common Troubleshooting & Quick Fix Patterns
- If imports hang during tests (`pytest`): ensure `DATABASE_URL` is set to local SQLite and `FORCE_EPHEMERAL=1` — this prevents attempts to reach Postgres/Neon.
- If migrations fail due to missing Postgres drivers, prefer `pg8000` as a pure Python fallback. See `_safe_initialize_extensions` logic.
- If email tests fail or attempt to send real emails: ensure `MAIL_SERVER`/`MAIL_USERNAME`/`MAIL_PASSWORD` are unset or placeholders; the code will print outputs to console instead of sending.
- If tests attempt to contact Paystack: configure `PAYSTACK_*` env vars with test credentials or mock requests in tests using `pytest-mock`.
- For Vercel: do not rely on ephemeral `/tmp` file persistence. Use a proper hosted Postgres (Neon, Supabase, Railway) or set `FORCE_EPHEMERAL=1` knowing data won’t persist across deployments.

## Deploying (Concise steps)
- Local sanity checks:
  - Run `python -m py_compile app.py` and a limited subset of tests with `DATABASE_URL=sqlite:///./data.db`.
- Use the repo script:
  - `python deploy_vercel.py` (interactive; it expects `.env`) or use `vercel` CLI with properly set env vars.

## Examples for AI Agents (concise actionable items)
- When editing `app.py` or adding new routes: keep code modular — if the change touches DB models, update `flask db` migrations / `initdb` logic.
- For tests that touch external APIs: add `pytest`-level fixtures to inject mocked `requests` responses (use `requests-mock` or `pytest-mock`), or set environment variables to disabled states.
- For refactors: prefer adding tests that assert side effects using the DB via `app.app_context()` with local SQLite; this reduces fragility.

## Files/Paths to Pay Attention To
- `app.py`: All primary app logic — models, routes, helpers
- `run.py`, `run_server.py`: Local runners
- `deploy_vercel.py`, `deploy_vercel.bat`: Deployment scripts for Vercel
- `requirements.txt`: Dependencies
- `templates/`, `static/`: UI
- `tools/`: Utility scripts used for testing and local validation

## PR / Code Review Tips (for the AI agent)
- Focus on behavior change: if you add network I/O in `app.py`, make it optional/guarded and add a test.
- Keep changes backwards compatible (NO breaking env var behavior unless deliberate).
- If adding new package dependencies, add them to `requirements.txt` and update the venv.

---
Please confirm if you want the agent to also create a `pytest.ini` / CI workflow (GitHub Actions) that runs a restricted test suite and ensures `DATABASE_URL` is set to sqlite for CI.
