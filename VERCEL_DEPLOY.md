**Deploying to Vercel (Flask app)**

Overview:
- Vercel is optimized for static sites and serverless functions. We can run this Flask app on Vercel by wrapping the WSGI Flask app with an ASGI adapter and routing all requests to a single serverless function.

Files added:
- `api/index.py` — ASGI wrapper that exposes the Flask app.
- `vercel.json` — routes all requests to `api/index.py` and sets Python runtime.

Steps to deploy:
1. Create a Vercel account and install the Vercel CLI (optional):
   - `npm i -g vercel`
2. From the project root run (first time):
   - `vercel login`
   - `vercel` and follow the prompts; choose the GitHub repo when asked.
3. Set Environment Variables in the Vercel dashboard (Project → Settings → Environment Variables):
   - `SECRET_KEY`, `ADMIN_PASSWORD`, `PAYSTACK_SECRET_KEY`, `PAYSTACK_PUBLIC_KEY`, `PAYSTACK_CALLBACK_URL`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USE_TLS`, `MAIL_USE_SSL`, `MAIL_DEFAULT_SENDER`, `ADMIN_EMAIL`
   - Use the Production environment for live keys.
4. Deploy:
   - `vercel --prod` or push to the connected GitHub branch and Vercel will auto-deploy.

Notes and caveats:
- Long-running background tasks (e.g., sending emails asynchronously) and WebSocket connections don't map well to serverless functions. For production jobs, use an external worker (e.g., Render, Heroku, or a task queue).
- SQLite (`data.db`) is file-based and not suitable for serverless deployments — migrate to a managed database (Postgres) for production.
- Make sure to rotate any secrets that were exposed before adding them to Vercel.
