CyberWorld Paystack Clone - Final
--------------------------------

What's included:
- app.py (Flask app with SQLite, admin UI, Paystack integration)
- templates/ and static/ assets
- Dockerfile and docker-compose.yml
- requirements.txt and .env.example

Quick start:
  python -m venv venv
  source venv/bin/activate   # Windows: venv\Scripts\activate
  pip install -r requirements.txt
  cp .env.example .env
  # edit .env to set SECRET_KEY, ADMIN_PASSWORD, PAYSTACK_SECRET_KEY, PAYSTACK_PUBLIC_KEY
  flask --app app initdb
  python app.py
  # or with Docker:
  docker compose up --build

Notes:
- This demo uses Paystack initialize/verify endpoints. Set correct keys in .env.
- For image scraping, run your own fetch_images script locally to populate static/images/.

Running tests:
  # Create a venv and install deps
  python -m venv .venv
  .\.venv\Scripts\Activate
  python -m pip install -r requirements.txt

  # Run a small subset of tests (unit tests only):
  $env:DATABASE_URL='sqlite:///./data.db'
  $env:FORCE_EPHEMERAL='1'
  $env:TEST_NO_NETWORK='1'  # prevent tests from contacting external services
  .\.venv\Scripts\python.exe -m pytest -q -k "not e2e and not paystack and not email"

  # To run all tests including Paystack/email tests, provide the required environment variables (Paystack keys and Mail credentials)
  # WARNING: This will contact external services and may create records in Paystack. Use test/staging keys.

CI / deployment:
  - There are GitHub Actions configured in .github/workflows/pytest.yml and deploy.yml. The deploy workflow requires the following GitHub secrets to be set before it can successfully deploy:
    - VERCEL_TOKEN, VERCEL_ORG_ID, VERCEL_PROJECT_ID
  - For a non-interactive deploy locally, set `VERCEL_TOKEN` in your environment and run:
    python .venv\Scripts\python.exe deploy_vercel.py --non-interactive

