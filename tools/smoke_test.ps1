<#
PowerShell smoke test script for the deployed site.

Usage:
  pwsh ./tools/smoke_test.ps1 -BaseUrl "https://..." [-FollowRedirects]

This script performs a few GET checks and prints status codes and final URLs.
#>

param(
    [Parameter(Mandatory=$true)][string]$BaseUrl,
    [switch]$FollowRedirects
)

function Check-Url {
    param($url)
    Write-Output "Checking: $url"
    if($FollowRedirects) {
        $resp = curl.exe -L -sS -o NUL -w "code:%{http_code} final:%{url_effective}\n" $url
        Write-Output $resp
    } else {
        $hdr = curl.exe -I --max-redirs 0 -sS $url
        Write-Output $hdr
    }
}

Check-Url "$BaseUrl/"
Check-Url "$BaseUrl/admin/login"
Check-Url "$BaseUrl/admin/diag"
Check-Url "$BaseUrl/admin/test-email"

Write-Output "Smoke tests finished. If you see 401 + _vercel_sso_nonce headers, the project is gated by Vercel SSO."
