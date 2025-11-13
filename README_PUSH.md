# Push Instructions — Cyber World Store

This file contains the exact steps to push your project to GitHub from PowerShell.

Prerequisites
- Git installed (https://git-scm.com/download/win)
- GitHub repository created (https://github.com/new)

Commands to run in PowerShell (replace repo URL):

```powershell
cd C:\Users\CYBER360\Desktop\cyberworld_paystack_clone_final

# Configure git user once (use your GitHub details)
git config user.name "cyberworld360"
git config user.email "cyberworldstore360@gmail.com"

# Initialize repo
git init

# Add files and commit
git add .
git commit -m "Initial commit: Production-ready e-commerce app"

# Add remote (replace URL) and push
git remote add origin https://github.com/cyberworld360/cyberworld-store.git
git branch -M main
git push -u origin main
```

If `.env` was accidentally committed, remove it from Git history:

```powershell
# Stop tracking .env and commit the change
echo ".env" >> .gitignore
git rm --cached .env
git commit -m "Remove .env from tracking"

git push
```

If you prefer, run the included `push_to_github.ps1` script after installing Git and creating the remote repository. Edit the script to replace `RepoUrl` if needed.
