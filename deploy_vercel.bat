@echo off
REM Quick start Vercel deployment for CyberWorld Store
REM Run this batch file to set up and deploy to Vercel automatically

setlocal enabledelayedexpansion

echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║     CyberWorld Store - Quick Vercel Deployment           ║
echo ║                                                          ║
echo ║  This script will:                                       ║
echo ║  1. Install Node.js and Vercel CLI (if needed)          ║
echo ║  2. Validate your setup                                  ║
echo ║  3. Create/configure Vercel project                      ║
echo ║  4. Deploy your app                                      ║
echo ║                                                          ║
echo ║  Requirements:                                           ║
echo ║  - Node.js and npm installed                             ║
echo ║  - Vercel account (free at https://vercel.com)          ║
echo ║  - GitHub account with SSH or HTTPS access              ║
echo ║                                                          ║
echo ║  Time required: ~10 minutes                              ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed
    echo 💡 Install from: https://nodejs.org
    pause
    exit /b 1
)

echo ✅ Node.js is installed
node --version

REM Check npm
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ npm is not installed
    pause
    exit /b 1
)

echo ✅ npm is installed
npm --version
echo.

REM Install Vercel CLI
echo 🔧 Installing Vercel CLI...
call npm install -g vercel
if errorlevel 1 (
    echo ⚠️  Failed to install Vercel CLI
    pause
    exit /b 1
)
echo ✅ Vercel CLI installed
echo.

REM Verify installation
vercel --version
if errorlevel 1 (
    echo ❌ Vercel CLI not working
    pause
    exit /b 1
)
echo.

REM Login to Vercel
echo 🔐 Logging into Vercel...
echo 💡 You'll be prompted to login/verify your account
timeout /t 2 /nobreak
call vercel login
if errorlevel 1 (
    echo ⚠️  Vercel login failed
    pause
    exit /b 1
)
echo.

REM Deploy to Vercel
echo 🚀 Deploying to Vercel...
echo 💡 Select options:
echo    - Use current directory? (y)
echo    - Link to existing project? (n) OR pick your project
echo    - Framework: Other
echo    - Build command: (leave blank)
echo.
timeout /t 3 /nobreak
call vercel

echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║             ✅ Deployment Complete!                      ║
echo ║                                                          ║
echo ║  IMPORTANT NEXT STEPS:                                   ║
echo ║                                                          ║
echo ║  1. Get your Project ID and Org ID:                     ║
echo ║     - Visit: https://vercel.com/dashboard               ║
echo ║     - Click your project                                ║
echo ║     - Go to Settings - General                          ║
echo ║     - Copy Project ID and Org ID                        ║
echo ║                                                          ║
echo ║  2. Create a Vercel Token:                              ║
echo ║     - Visit: https://vercel.com/account/tokens          ║
echo ║     - Create new token                                  ║
echo ║     - Copy it immediately                               ║
echo ║                                                          ║
echo ║  3. Add GitHub Secrets:                                 ║
echo ║     - Go to: https://github.com/cyberworld360/...       ║
echo ║     - /cyberworld-store/settings/secrets/actions        ║
echo ║     - Add VERCEL_TOKEN, VERCEL_ORG_ID, VERCEL_PROJECT_ID║
echo ║     - Add all other secrets from VERCEL_SETUP_COMPLETE.md║
echo ║                                                          ║
echo ║  4. Test your live app:                                 ║
echo ║     - Visit your Vercel deployment URL                  ║
echo ║     - Test admin login, payments, and emails            ║
echo ║                                                          ║
echo ║  📚 Full guide: VERCEL_SETUP_COMPLETE.md               ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

pause
