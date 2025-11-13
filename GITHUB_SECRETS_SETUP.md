**GitHub Secrets: Setup Guide**

Purpose:
- Keep sensitive credentials out of the repository and provide them securely to CI/CD and hosting environments.

Recommended secrets to add to GitHub (Repository -> Settings -> Secrets & variables -> Actions -> New repository secret):
- `PAYSTACK_SECRET_KEY` : your live Paystack secret (starts with `sk_live_...`)
- `PAYSTACK_PUBLIC_KEY` : your Paystack public key (starts with `pk_live_...`)
- `MAIL_USERNAME` : SMTP username (e.g., Gmail address)
- `MAIL_PASSWORD` : SMTP app password
- `SECRET_KEY` : Flask `SECRET_KEY` / Django secret
- `ADMIN_PASSWORD` : Admin password (if used during automated tests/deploy)

How to use these secrets in GitHub Actions:
- In workflow YAML, reference secrets as `${{ secrets.PAYSTACK_SECRET_KEY }}`.

Example: add a secret
1. Go to `https://github.com/<owner>/<repo>/settings/secrets/deploy`
2. Click `New repository secret` and paste the name and value.

Security notes:
- Rotate any secret immediately if it was ever committed (or exposed) in the repository.
- Limit secret access in organization settings if needed.

Additional deployment secrets (Heroku / Docker):
- `HEROKU_API_KEY` : Heroku API key (use for GitHub Actions deploys)
- `HEROKU_APP_NAME` : Heroku app name to deploy to
- `HEROKU_EMAIL` : Email address for the Heroku account
- `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` : If you prefer to build and push Docker images to Docker Hub

Note: Add these values via `Settings -> Secrets and variables -> Actions` before pushing to trigger deployment workflows.
