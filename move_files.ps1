# Move all files from LAE directory to root
$laePath = Resolve-Path LAE
Get-ChildItem -Path LAE -Recurse -File | ForEach-Object {
    $relativePath = $_.FullName.Substring($laePath.Path.Length + 1)
    $destPath = Join-Path "." $relativePath
    $destDir = Split-Path $destPath -Parent
    if (!(Test-Path $destDir)) {
        New-Item -ItemType Directory -Path $destDir -Force | Out-Null
    }
    Move-Item $_.FullName $destPath -Force
    Write-Host "Moved: $relativePath"
}

# Remove the now-empty LAE directory
if (Test-Path LAE) {
    Remove-Item -Path LAE -Recurse -Force
    Write-Host "Removed LAE directory"
}

Write-Host "All files moved to root successfully!"
