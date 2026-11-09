# Registers LAE to start automatically on Windows login.
# Run once:  powershell -ExecutionPolicy Bypass -File install_startup.ps1
# To remove: run with -Remove

param([switch]$Remove)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$startupDir = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\Startup"
$shortcutPath = Join-Path $startupDir "LAE.lnk"

if ($Remove) {
    if (Test-Path $shortcutPath) {
        Remove-Item $shortcutPath -Force
        Write-Host "LAE removed from Startup." -ForegroundColor Yellow
    } else {
        Write-Host "LAE was not in Startup."
    }
    exit
}

$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($shortcutPath)
$Shortcut.TargetPath = Join-Path $scriptDir "lae.bat"
$Shortcut.WorkingDirectory = $scriptDir
$Shortcut.Description = "LAE AI Assistant (background)"
$Shortcut.WindowStyle = 7  # minimized / hidden
$Shortcut.Save()

Write-Host "LAE added to Startup folder:" -ForegroundColor Green
Write-Host "  $shortcutPath"
Write-Host "It will launch automatically on next login (no console window)."
Write-Host "To undo: powershell -ExecutionPolicy Bypass -File install_startup.ps1 -Remove"
