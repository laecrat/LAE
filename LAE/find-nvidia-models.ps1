# find-nvidia-models.ps1
# Tests which NVIDIA NIM chat models currently work with your API key.
# Requires PowerShell 7+ (uses ForEach-Object -Parallel).
# Reads the key from the Free Claude Code config file, so you never paste it.
# The key is never printed.

$envFile = "$env:USERPROFILE\.fcc\.env"

if (-not (Test-Path $envFile)) {
    Write-Host "Could not find $envFile" -ForegroundColor Red
    exit 1
}

$match = Select-String -Path $envFile -Pattern 'nvapi-[A-Za-z0-9_\-]+' | Select-Object -First 1
if (-not $match) {
    Write-Host "No nvapi- key found in $envFile. Add your key in Free Claude Code first." -ForegroundColor Red
    exit 1
}
$key = $match.Matches[0].Value

# Get the full model list, then drop models that are not general chat models
$skip = 'guard|reward|embed|safety|rerank|parse|clip|vision|vl|ocr|asr|tts|retriev|diffusion|image'
$ids = (Invoke-RestMethod -Uri "https://integrate.api.nvidia.com/v1/models" `
        -Headers @{ Authorization = "Bearer $key" }).data.id |
    Where-Object { $_ -notmatch $skip }

Write-Host "Testing $($ids.Count) models (this can take a few minutes)..."

$results = $ids | ForEach-Object -ThrottleLimit 6 -Parallel {
    $m = $_
    $body = @{
        model      = $m
        messages   = @(@{ role = "user"; content = "say hi" })
        max_tokens = 20
    } | ConvertTo-Json -Depth 5

    $sw = [Diagnostics.Stopwatch]::StartNew()
    try {
        Invoke-RestMethod -Uri "https://integrate.api.nvidia.com/v1/chat/completions" `
            -Method Post `
            -Headers @{ Authorization = "Bearer $using:key" } `
            -ContentType "application/json" `
            -Body $body `
            -TimeoutSec 25 | Out-Null
        [pscustomobject]@{ Model = $m; Seconds = [math]::Round($sw.Elapsed.TotalSeconds, 1) }
    }
    catch { }   # failed, retired or too slow: leave it out
}

Write-Host ""
if ($results) {
    Write-Host "Working models (fastest first):" -ForegroundColor Green
    $results | Sort-Object Seconds | Format-Table -AutoSize
    Write-Host "In Free Claude Code, use the name with 'nvidia_nim/' in front, e.g. nvidia_nim/$($results[0].Model)"
}
else {
    Write-Host "No models answered. You may have hit the rate limit (40 requests/min). Wait a minute and run again." -ForegroundColor Yellow
}
