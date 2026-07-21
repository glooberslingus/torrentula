<#
Installs the built TorrentSearch.exe: copies it to a per-user Programs
folder, creates a Start Menu shortcut, and registers it under Windows'
Settings > Apps > Installed apps (and Control Panel > Programs and
Features) so it can be uninstalled from there too.

No administrator rights are needed -- everything is per-user (HKCU).

Run this AFTER build_exe.bat has produced dist\TorrentSearch.exe.
#>

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$exeSource = Join-Path $root "dist\TorrentSearch.exe"

if (-not (Test-Path $exeSource)) {
    Write-Host "Couldn't find dist\TorrentSearch.exe" -ForegroundColor Red
    Write-Host "Run build_exe.bat first, then run this again." -ForegroundColor Red
    exit 1
}

$installDir = Join-Path $env:LOCALAPPDATA "Programs\TorrentSearch"
New-Item -ItemType Directory -Force -Path $installDir | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $installDir "magnetfiles") | Out-Null

$exeDest = Join-Path $installDir "TorrentSearch.exe"
Copy-Item $exeSource $exeDest -Force

# --- Start Menu shortcut ---
$startMenuDir = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs"
$shortcutPath = Join-Path $startMenuDir "Torrent Search.lnk"
$wsh = New-Object -ComObject WScript.Shell
$shortcut = $wsh.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $exeDest
$shortcut.WorkingDirectory = $installDir
$shortcut.IconLocation = $exeDest
$shortcut.Description = "Search multiple torrent sites and rank results by seeders"
$shortcut.Save()

# --- uninstaller, dropped alongside the exe ---
# Written as a single-quoted here-string so $installDir etc. below are NOT
# expanded now -- they become literal text in uninstall.ps1, to be evaluated
# by that script itself when it runs later.
$uninstallScript = @'
$ErrorActionPreference = "SilentlyContinue"
$installDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$startMenuLink = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\Torrent Search.lnk"
Remove-Item $startMenuLink -Force
Remove-Item "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\TorrentSearch" -Recurse -Force
Write-Host "Torrent Search has been uninstalled."

# This script's own file lives inside $installDir, so it can't delete that
# folder while it's still running. Hand off the final cleanup to a short
# detached process instead.
$cleanupCommand = "Start-Sleep -Seconds 1; Remove-Item -Recurse -Force '$installDir'"
Start-Process -FilePath "powershell.exe" -ArgumentList @("-NoProfile", "-WindowStyle", "Hidden", "-Command", $cleanupCommand) -WindowStyle Hidden
'@
Set-Content -Path (Join-Path $installDir "uninstall.ps1") -Value $uninstallScript -Encoding UTF8

# --- register with Windows "Installed apps" / Programs and Features ---
$uninstallKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\TorrentSearch"
New-Item -Path $uninstallKey -Force | Out-Null
Set-ItemProperty -Path $uninstallKey -Name "DisplayName" -Value "Torrent Search"
Set-ItemProperty -Path $uninstallKey -Name "DisplayIcon" -Value $exeDest
Set-ItemProperty -Path $uninstallKey -Name "DisplayVersion" -Value "1.0.0"
Set-ItemProperty -Path $uninstallKey -Name "Publisher" -Value "Local build"
Set-ItemProperty -Path $uninstallKey -Name "UninstallString" -Value "powershell.exe -NoProfile -ExecutionPolicy Bypass -File `"$installDir\uninstall.ps1`""
Set-ItemProperty -Path $uninstallKey -Name "InstallLocation" -Value $installDir
Set-ItemProperty -Path $uninstallKey -Name "NoModify" -Value 1 -Type DWord
Set-ItemProperty -Path $uninstallKey -Name "NoRepair" -Value 1 -Type DWord

Write-Host ""
Write-Host "Installed to:        $installDir" -ForegroundColor Green
Write-Host "Start Menu shortcut: Torrent Search" -ForegroundColor Green
Write-Host "Listed under Settings > Apps > Installed apps as 'Torrent Search'" -ForegroundColor Green
Write-Host ""
Write-Host "Launch it from the Start Menu, or run:"
Write-Host "  $exeDest"
Write-Host ""
Write-Host "To uninstall later: Settings > Apps > Installed apps > Torrent Search > Uninstall"
