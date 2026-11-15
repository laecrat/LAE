# Creates a desktop shortcut for LAE
# Run: powershell -ExecutionPolicy Bypass -File create_shortcut.ps1

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$desktop = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktop "LAE.lnk"

$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($shortcutPath)
$Shortcut.TargetPath = Join-Path $scriptDir "lae.bat"
$Shortcut.WorkingDirectory = $scriptDir
$Shortcut.Description = "LAE"
$Shortcut.WindowStyle = 7  # Minimized

# Try to set icon if LAE.ico exists in script directory
$iconPath = Join-Path $scriptDir "LAE.ico"
if (Test-Path $iconPath) {
    $Shortcut.IconLocation = $iconPath
}

$Shortcut.Save()

Write-Host "Desktop shortcut created: $shortcutPath" -ForegroundColor Green
Write-Host "Double-click 'LAE' on your desktop to start the assistant in the background."
