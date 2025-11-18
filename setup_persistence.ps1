#!/usr/bin/env pwsh
# Quick setup for PostgreSQL persistence on Vercel
# This script guides you through setting up a free PostgreSQL database

Write-Host "=== Vercel Data Persistence Setup ===" -ForegroundColor Cyan
Write-Host ""

Write-Host "Step 1: Choose a Database Provider" -ForegroundColor Yellow
Write-Host "1. Neon (Recommended - Free, easiest)"
Write-Host "2. Railway.app (Free tier + $5 credit)"
Write-Host "3. Supabase (Free 500MB)"
Write-Host ""

$choice = Read-Host "Enter your choice (1-3)"

switch($choice) {
    "1" {
        Write-Host ""
        Write-Host "=== Neon Setup ===" -ForegroundColor Green
        Write-Host "1. Visit: https://neon.tech"
        Write-Host "2. Click 'Sign up'"
        Write-Host "3. Create a new project"
        Write-Host "4. Go to Connection string and copy the full URL"
        Write-Host ""
        Write-Host "Connection string should look like:"
        Write-Host "  postgresql://neon_user:password@ep-xxxxx.neon.tech:5432/neondb"
        Write-Host ""
        $dbUrl = Read-Host "Paste your PostgreSQL connection string"
    }
    "2" {
        Write-Host ""
        Write-Host "=== Railway Setup ===" -ForegroundColor Green
        Write-Host "1. Visit: https://railway.app"
        Write-Host "2. Click 'Start New Project'"
        Write-Host "3. Add 'Database' → 'PostgreSQL'"
        Write-Host "4. Go to Plugins → PostgreSQL → Connect"
        Write-Host "5. Copy 'Connection String'"
        Write-Host ""
        $dbUrl = Read-Host "Paste your PostgreSQL connection string"
    }
    "3" {
        Write-Host ""
        Write-Host "=== Supabase Setup ===" -ForegroundColor Green
        Write-Host "1. Visit: https://supabase.com"
        Write-Host "2. Click 'Start your project'"
        Write-Host "3. Create new project"
        Write-Host "4. Go to Settings → Database → Connection string"
        Write-Host "5. Copy 'PostgreSQL' URI"
        Write-Host ""
        $dbUrl = Read-Host "Paste your PostgreSQL connection string"
    }
    default {
        Write-Host "Invalid choice" -ForegroundColor Red
        exit 1
    }
}

if (-not $dbUrl) {
    Write-Host "Error: No database URL provided" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Step 2: Set Vercel Environment Variable" -ForegroundColor Yellow
Write-Host ""
Write-Host "Go to: Vercel Dashboard → Your Project → Settings → Environment Variables"
Write-Host ""
Write-Host "Add this variable:"
Write-Host "  Name:  DATABASE_URL"
Write-Host "  Value: $dbUrl"
Write-Host "  Scope: Production, Preview, Development"
Write-Host ""
Write-Host "Then click 'Save'"
Write-Host ""

$vercelConfigured = Read-Host "Have you added DATABASE_URL to Vercel? (y/n)"

if ($vercelConfigured -eq "y") {
    Write-Host ""
    Write-Host "Step 3: Redeploy" -ForegroundColor Yellow
    Write-Host "Run: git push origin main"
    Write-Host ""
    $doPush = Read-Host "Push to deploy now? (y/n)"
    
    if ($doPush -eq "y") {
        Write-Host "Pushing to GitHub..." -ForegroundColor Cyan
        git push origin main
        Write-Host "Deployment started! Check Vercel dashboard for status." -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "Step 4: Verify" -ForegroundColor Yellow
Write-Host "After deploy completes:"
Write-Host "1. Visit: https://www.cyberworldstore.shop/admin/login"
Write-Host "2. Log in with admin credentials"
Write-Host "3. Add a new product with an image"
Write-Host "4. Refresh the page - product should persist!"
Write-Host ""
