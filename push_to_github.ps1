# PowerShell script to push project to GitHub
# Usage: Open PowerShell, cd into project root and run this script after installing Git

param(
    [string]$RepoUrl = "https://github.com/YourUsername/cyberworld-store.git",
    [string]$CommitMessage = "Initial commit: Production-ready e-commerce app"
)

Write-Host "Running Git push script..."

# Ensure .gitignore exists
if (-not (Test-Path -Path .gitignore)) {
    Write-Host "Creating .gitignore..."
    Set-Content -Path .gitignore -Value ".env" -Encoding UTF8
}

# Initialize repo (if not already initialized)
if (-not (Test-Path -Path ".git")) {
    git init
}

# Configure user (optional - will use global config if set)
git config user.name "cyberworld360"
git config user.email "cyberworldstore360@gmail.com"

git add .

git commit -m $CommitMessage

# Add remote (if remote already exists, the command will fail)
try {
    git remote add origin $RepoUrl
} catch {
    Write-Host "Remote 'origin' may already exist. Skipping adding remote."
}

git branch -M main

git push -u origin main

Write-Host "Done. If the push fails, check Git installation and remote URL."