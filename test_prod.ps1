$url = "https://cyberworld-store-d3zak4mem-cyberworldstores-projects.vercel.app/"
try {
    Write-Host "Testing: $url"
    $resp = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 10
    Write-Host "Status: $($resp.StatusCode)"
    $body = $resp.Content
    $first500 = $body.Substring(0, [Math]::Min(500, $body.Length))
    Write-Host "Body (first 500 chars):"
    Write-Host $first500
} catch {
    Write-Host "Error: $($_.Exception.Message)"
}
