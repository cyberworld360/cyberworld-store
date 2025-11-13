# 🔗 GITHUB SETUP GUIDE

## Prerequisites

Before connecting to GitHub, you need:

1. **Git installed** - Download from: https://git-scm.com/download/win
   - During installation, select "Use Git from Windows Command Prompt"
   - Complete the installation

2. **GitHub account** - Sign up at: https://github.com/signup

---

## STEP 1: Create a GitHub Repository

1. Go to: https://github.com/new
2. Fill in:
   - **Repository name:** `cyberworld-store` (or your preferred name)
   - **Description:** `Premium E-Commerce Platform with Paystack Integration`
   - **Visibility:** Choose "Public" or "Private"
   - **Add .gitignore:** Select "Python"
   - **License:** MIT (optional)
3. Click: **Create repository**

You'll see a page with commands. Copy the repository URL (looks like: `https://github.com/YOUR_USERNAME/cyberworld-store.git`)

---

## STEP 2: Initialize Git Locally

After installing Git, open PowerShell in your project folder:

```powershell
cd c:\Users\CYBER360\Desktop\cyberworld_paystack_clone_final

# Initialize Git
git init

# Configure Git (use your GitHub username and email)
git config user.name "Your GitHub Username"
git config user.email "your.email@github.com"

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Production-ready e-commerce app with Paystack integration"

# Add remote repository (replace with your repo URL)
git remote add origin https://github.com/YOUR_USERNAME/cyberworld-store.git

# Rename branch to main (GitHub default)
git branch -M main

# Push to GitHub
git push -u origin main
```

---

## STEP 3: Create .gitignore (if needed)

The `.gitignore` file should exclude sensitive data. Create one if missing:

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.venv/
venv/
ENV/
env/

# Flask
instance/
.webassets-cache

# Database
*.db
*.sqlite
*.sqlite3
data.db

# Environment
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# Uploads
static/images/uploads/
static/uploads/

# OS
.DS_Store
Thumbs.db

# Cache
*.cache
.pytest_cache/
```

---

## QUICK REFERENCE

After Git is installed, run these 8 commands:

```powershell
cd c:\Users\CYBER360\Desktop\cyberworld_paystack_clone_final

git init
git config user.name "YourUsername"
git config user.email "your.email@github.com"
git add .
git commit -m "Initial commit: Production-ready e-commerce app"
git remote add origin https://github.com/YourUsername/cyberworld-store.git
git branch -M main
git push -u origin main
```

---

## STEP 4: Verify on GitHub

After pushing:
1. Go to: https://github.com/YOUR_USERNAME/cyberworld-store
2. You should see all your files
3. Your code is now backed up and version controlled!

---

## IMPORTANT: Protect Your .env File

**Never commit .env to GitHub!** It contains your live Paystack keys.

1. Create a file named `.gitignore` in your project root
2. Add this line: `.env`
3. Your .env file won't be pushed to GitHub

---

## OPTIONAL: Add GitHub Secrets for Deployment

For automated deployment (CI/CD):

1. Go to: https://github.com/YOUR_USERNAME/cyberworld-store/settings/secrets/actions
2. Create secrets:
   - `PAYSTACK_SECRET_KEY`: Your live key
   - `PAYSTACK_PUBLIC_KEY`: Your live key
   - `MAIL_PASSWORD`: Your Gmail app password

This allows automated deployment without storing secrets in code.

---

## NEXT STEPS

After pushing to GitHub:

1. **Deploy from GitHub:** Use Heroku, GitHub Pages, or other services
2. **Track Changes:** Use Git for version control
3. **Collaborate:** Invite team members (Settings → Collaborators)
4. **Backup:** Your code is now safely backed up
5. **CI/CD:** Set up automated testing and deployment

---

## USEFUL GIT COMMANDS

```powershell
# Check status
git status

# View commit history
git log

# Create a new branch
git checkout -b feature/new-feature

# Switch branches
git checkout main

# Push new branch
git push -u origin feature/new-feature

# Pull latest changes
git pull

# Merge branch
git merge feature/new-feature
```

---

## TROUBLESHOOTING

**Issue:** "fatal: not a git repository"
- Solution: Run `git init` first

**Issue:** "Permission denied" when pushing
- Solution: Use HTTPS (included above) or set up SSH keys

**Issue:** ".env file committed by mistake"
- Solution: Run:
  ```
  git rm --cached .env
  git commit -m "Remove .env from tracking"
  git push
  ```

---

## SUMMARY

| Step | Action |
|------|--------|
| 1 | Download Git (https://git-scm.com/download/win) |
| 2 | Create GitHub repo (https://github.com/new) |
| 3 | Run 8 Git commands (see QUICK REFERENCE) |
| 4 | Verify files on GitHub |
| 5 | Start collaborating/deploying |

**That's it! Your code is now on GitHub! 🎉**

