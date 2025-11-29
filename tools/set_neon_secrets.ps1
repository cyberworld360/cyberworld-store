<#
Set Neon PR preview variable and API key as GitHub Actions repo variable + secret.

Usage:
  # Using environment variables (recommended):
  $env:NEON_PROJECT_ID = 'prj_Va8uGMLFQhjZIx8ybvc2gGTjfmZp'
  $env:NEON_API_KEY = 'rzCmX3i84vL5i3MH4ocTkc72'
  .\tools\set_neon_secrets.ps1 -RepoOwner 'cyberworld360' -RepoName 'cyberworld-store'

  # Or provide values directly (less secure):
  .\tools\set_neon_secrets.ps1 -RepoOwner 'cyberworld360' -RepoName 'cyberworld-store' -ProjectId 'prj_...' -ApiKey 'rzC...'

Notes:
- This script uses GitHub CLI (`gh`). Ensure `gh` is installed and authenticated (`gh auth login`).
- The script does not store the key locally; it calls `gh` to set the repo secrets/variables.
<#

The script is intentionally simple and safe — it uses the GitHub CLI (or falls back to `gh api`) to set:
- A repo Actions variable named `NEON_PROJECT_ID` (non-secret; used by CI workflows)
- A repo Actions secret named `NEON_API_KEY` (secret to create/delete preview branches)

The script will exit non-zero on error.
#>

param(
    [parameter(Mandatory=$false)] [string] $RepoOwner,
    [parameter(Mandatory=$false)] [string] $RepoName,
    [parameter(Mandatory=$false)] [string] $ProjectId = $env:NEON_PROJECT_ID,
    [parameter(Mandatory=$false)] [string] $ApiKey = $env:NEON_API_KEY,
    [switch] $DryRun
)

function Write-Log($msg) { Write-Host "[set_neon_secrets] $msg" }

try {
    gh --version > $null 2>&1
} catch {
    Write-Error "The GitHub CLI (gh) is required. Install it: https://cli.github.com/"
    exit 1
}

try {
    gh auth status > $null 2>&1
} catch {
    Write-Error "Not authenticated with GH CLI. Run 'gh auth login' first."
    exit 1
}

if (-not $RepoOwner -or -not $RepoName) {
    # Try to infer owner/repo from `git` remote
    try {
        $remoteUrl = git remote get-url origin 2>$null
        if ($remoteUrl) {
            # Remove git+ssh or https prefixes
            $remoteUrl = $remoteUrl -replace '^git@github.com:', 'https://github.com/'
            $remoteUrl = $remoteUrl -replace '\.git$', ''
            $parts = $remoteUrl -split '/' | Select-Object -Last 2
            if ($parts.Count -eq 2) {
                $RepoOwner = $parts[0]
                $RepoName = $parts[1]
            }
        }
    } catch {
    }
}

if (-not $RepoOwner -or -not $RepoName) {
    Write-Error "Repo owner/name could not be inferred. Provide -RepoOwner and -RepoName or run in a git repo with origin set."
    exit 1
}

if (-not $ProjectId) {
    Write-Error "NEON project id is required. Set env NEON_PROJECT_ID or pass -ProjectId."
    exit 1
}
if (-not $ApiKey) {
    Write-Error "NEON API key is required. Set env NEON_API_KEY or pass -ApiKey."
    exit 1
}

$repo = "$RepoOwner/$RepoName"
Write-Log "Target repo: $repo"

if ($DryRun) { Write-Log "Dry-run mode; no changes will be applied." }

# 1) Set variable via GH REST API (safe non-secret storage)
Write-Log "Setting Actions variable 'NEON_PROJECT_ID' on repo: $repo"
if (-not $DryRun) {
    $varUrl = "/repos/$RepoOwner/$RepoName/actions/variables/NEON_PROJECT_ID"
    $body = @{ value = $ProjectId } | ConvertTo-Json
    $r = gh api --method PUT $varUrl -f value=$ProjectId 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to set repo variable NEON_PROJECT_ID: $r"
        exit 1
    }
}

# 2) Set secret using GH CLI (repo secret)
Write-Log "Setting Actions secret 'NEON_API_KEY' on repo: $repo"
if (-not $DryRun) {
    $r2 = gh secret set NEON_API_KEY --repo $repo --body "$ApiKey" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to set secret NEON_API_KEY: $r2"
        exit 1
    }
}

Write-Log "Completed. (DryRun=$DryRun)"
Write-Log "Reminder: do NOT commit secrets into source control."

exit 0
