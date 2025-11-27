<#
PowerShell script to add environment variables from a local `.env` file to a Vercel project using the Vercel CLI.

Usage (local):
  $env:VERCEL_TOKEN = 'your_token'
  .\scripts\set_vercel_envs.ps1 -ProjectId "<vercel_project_id>"

Notes:
- This script uses the Vercel CLI; ensure you're logged in or `VERCEL_TOKEN` is set.
- It reads `.env` in repo root and adds each non-empty variable to the production environment.
- It will skip variables with blank values, and skip VERCEL_TOKEN itself.
- Use with caution: this can override environment variables in your Vercel project.
#>
param(
    [Parameter(Mandatory=$true)]
    [string]$ProjectId,
    [switch]$Preview
)

# Where `vercel` is available on PATH
$vercel = "vercel"

if (-not (Test-Path -Path ".env")) {
    Write-Error ".env file not found in repo root. Copy .env.example to .env and fill in secrets."
    exit 1
}

$envLines = Get-Content .env | Where-Object { $_ -and -not $_.Trim().StartsWith('#') }

foreach ($line in $envLines) {
    if ($line -notmatch '\S=') { continue }
    $parts = $line -split('=', 2)
    $key = $parts[0].Trim()
    $value = $parts[1].Trim().Trim('"')

    if ($key -eq 'VERCEL_TOKEN') { continue }
    if ([string]::IsNullOrWhiteSpace($value)) { Write-Host "Skipping $key (empty)"; continue }

    $envTarget = if ($Preview) { 'preview' } else { 'production' }

    # Check if env var exists in the project; if so update it via `vercel env add --yes` after removing
    $exists = $false
    try {
        $list = & $vercel env ls $ProjectId --token $env:VERCEL_TOKEN 2>$null
        if ($list -and $list -match "^$key\s") { $exists = $true }
    } catch {
        # ignore failures; continue to try adding
    }

    if ($exists) {
        Write-Host "Updating existing variable: $key ($envTarget)"
        try {
            & $vercel env rm $key $ProjectId $envTarget --token $env:VERCEL_TOKEN --yes
        } catch {
            Write-Warning "Failed to remove existing variable (attempting add): $key"
        }
    } else {
        Write-Host "Adding variable: $key ($envTarget)"
    }

    # Create the variable by piping in the value to avoid exposing it in the commandline arguments
    $encoded = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($value))
    $decoded = [System.Text.Encoding]::UTF8.GetString([Convert]::FromBase64String($encoded))

    Write-Host "Running: vercel env add $key $ProjectId $envTarget --token <redacted> --yes"
    & $vercel env add $key $ProjectId $envTarget --token $env:VERCEL_TOKEN --yes <<< $decoded | Out-Null
}

Write-Host "Done. Verify envs in Vercel dashboard or via 'vercel env ls <projectId>'"