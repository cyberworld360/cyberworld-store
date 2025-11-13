# GITHUB PUSH - FINAL STEPS

**Status:** Git not installed on system. Follow steps below to complete push.

---

## STEP 1: Install Git (Choose One Option)

### Option A: Using Windows Package Manager (Easiest)
```powershell
# Run in PowerShell as Administrator
winget install --id Git.Git -e --source winget
```

Or use the included batch file:
```powershell
cd C:\Users\CYBER360\Desktop\cyberworld_paystack_clone_final
.\install_git.bat
```

### Option B: Download & Install Manually
1. Visit: https://git-scm.com/download/win
2. Download Git for Windows
3. Run installer
4. During setup, select: "Use Git from the Windows Command Prompt"
5. Complete installation
6. **Restart PowerShell**

---

## STEP 2: Run Push Script

After installing Git and restarting PowerShell:

```powershell
cd C:\Users\CYBER360\Desktop\cyberworld_paystack_clone_final

# Run the push script with your GitHub repo URL
.\push_to_github.ps1 -RepoUrl 'https://github.com/cyberworld360/cyberworld-store.git'
```

---

## STEP 3: Authenticate with GitHub

When `git push` runs, you'll be asked for credentials:
- **Username:** `cyberworld360` (your GitHub username)
- **Password:** Use a **Personal Access Token** (not your password)

### Generate Personal Access Token:
1. Go to: https://github.com/settings/tokens
2. Click: "Generate new token" → "Generate new token (classic)"
3. Name it: `cyberworld-push`
4. Select scope: ✓ `repo` (full control of private repositories)
5. Click: "Generate token"
6. Copy the token (you won't see it again!)
7. Paste when prompted as password

---

## STEP 4: Verify on GitHub

After successful push:
1. Go to: https://github.com/cyberworld360/cyberworld-store
2. You should see all your files:
   - `app.py`
   - `templates/`
   - `static/`
   - `requirements.txt`
   - `.gitignore`
   - And more...

3. **.env NOT visible** ✓ (correctly excluded)
4. **data.db NOT visible** ✓ (correctly excluded)

---

## Alternative: Run Commands Manually

If the script doesn't work, run these commands one by one:

```powershell
cd C:\Users\CYBER360\Desktop\cyberworld_paystack_clone_final

git config user.name "cyberworld360"
git config user.email "cyberworldstore360@gmail.com"
git init
git add .
git commit -m "Initial commit: Production-ready e-commerce app"
git remote add origin https://github.com/cyberworld360/cyberworld-store.git
git branch -M main
git push -u origin main
```

---

## Troubleshooting

### "git: command not found"
→ Git not installed. Follow STEP 1 above and restart PowerShell.

### "fatal: destination path already exists and is not an empty directory"
→ Git repo already initialized. Run `git status` to check, or delete `.git` folder and retry.

### "fatal: could not read Username for 'https://github.com'"
→ Need Personal Access Token. Follow "Authenticate with GitHub" section above.

### ".env accidentally pushed"
→ Run these commands:
```powershell
git rm --cached .env
git commit -m "Remove .env from tracking"
git push
```

---

## Summary

1. ✓ Files ready (`.gitignore` created)
2. ✓ Script ready (`push_to_github.ps1`)
3. → **Install Git** (this is the blocker)
4. → Run push script
5. → Authenticate with PAT
6. → Verify on GitHub

**Next Action:** Install Git, restart PowerShell, then run the script.

