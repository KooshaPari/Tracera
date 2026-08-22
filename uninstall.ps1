#!/usr/bin/env pwsh
# Tracera One-line Uninstaller (Windows)

$ErrorActionPreference = 'Stop'

$InstallDir = if ($env:TRACERA_HOME) { $env:TRACERA_HOME } else { "$env:LOCALAPPDATA\Tracera" }

Write-Host '==> Uninstalling Tracera...' -ForegroundColor Cyan

# Remove install dir
if (Test-Path $InstallDir) {
    Write-Host "    Removing $InstallDir..." -ForegroundColor Gray
    Remove-Item $InstallDir -Recurse -Force
}

# Remove PATH entry
$binPath = "$InstallDir\bin"
$currentPath = [Environment]::GetEnvironmentVariable('Path', 'User')
if ($currentPath -like "*$binPath*") {
    $newPath = ($currentPath -split ';' | Where-Object { $_ -ne $binPath }) -join ';'
    [Environment]::SetEnvironmentVariable('Path', $newPath, 'User')
}

# Remove Start Menu shortcuts
$paths = @(
    "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\PhenotypeApps\Tracera.lnk",
    "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\PhenotypeApps\Tracera CLI.lnk"
)
foreach ($p in $paths) {
    if (Test-Path $p) { Remove-Item $p -Force }
}

# Remove desktop shortcut
if (Test-Path "$env:USERPROFILE\Desktop\Tracera.lnk") {
    Remove-Item "$env:USERPROFILE\Desktop\Tracera.lnk" -Force
}

# Remove registry entries
Remove-Item -Path 'HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\Tracera' -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path 'HKLM:\Software\Tracera' -Recurse -Force -ErrorAction SilentlyContinue

Write-Host 'Tracera uninstalled.' -ForegroundColor Green