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
