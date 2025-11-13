**Incident: Exposed Secrets Found Locally**

Summary:
- On or before November 13, 2025, live Paystack keys and a Gmail app password were present in the local `.env` file for this repository.
- The repository was previously pushed to GitHub; although the remote was rewritten to a clean commit, sensitive credentials existed in local files and/or older history.

Immediate actions you must take (DO THESE NOW):
- Rotate the Paystack secret key in the Paystack dashboard (revoke existing key, generate a new one).
- Revoke the Gmail app password used in `MAIL_PASSWORD` and create a new app password (or use a managed mail service).
- Do NOT commit the new secrets to git. Keep them only in your local `.env` or in GitHub Secrets.

Removal actions (recommended):
- If `data.db` contains real customer or sensitive data, permanently remove it from repository history with `git-filter-repo` or BFG Repo-Cleaner (instructions below).
- Ensure `.env` and database files are present in `.gitignore` (this project already contains those entries).

Short incident note to share with team / GitHub Security:
"We discovered Paystack and Gmail credentials in a local `.env` file. We performed an emergency cleanup and pushed a clean commit to `main`. Please rotate any exposed credentials immediately and re-clone the repository. Contact ops to confirm no remaining secrets are visible in GitHub's secret scanning alerts."

Full purge instructions (safe approach):
1. Back up your local repo and clones before rewriting history.
2. Install `git-filter-repo`:
   - `pip install git-filter-repo`
3. Mirror the repo and run the purge (example):
   ```powershell
   git clone --mirror https://github.com/<owner>/<repo>.git repo-mirror.git
   cd repo-mirror.git
   git filter-repo --invert-paths --paths data.db --paths data.db.bak --paths '.env' --force
   git push --force --all
   git push --force --tags
   ```
4. Instruct all collaborators to re-clone the repository (do not pull):
   - `git clone https://github.com/<owner>/<repo>.git`

Notes:
- Rewriting history is disruptive. Coordinate with your team and notify them in advance.
- I can run the `git-filter-repo` steps for you after you confirm and/or install `git-filter-repo`.
