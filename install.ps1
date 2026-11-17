#!/usr/bin/env pwsh
# Tracera One-line Installer (Windows)
# Usage: irm https://raw.githubusercontent.com/KooshaPari/Tracera/main/install.ps1 | iex

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

# Configuration
$Repo = 'KooshaPari/Tracera'
$InstallDir = if ($env:TRACERA_HOME) { $env:TRACERA_HOME } else { "$env:LOCALAPPDATA\Tracera" }
$Version = if ($env:TRACERA_VERSION) { $env:TRACERA_VERSION } else { 'latest' }
$RepoRoot = "$env:TEMP\tracera-install-$(Get-Random)"

Write-Host '==> Tracera Installer' -ForegroundColor Cyan
Write-Host "    Install dir: $InstallDir" -ForegroundColor Gray
Write-Host "    Version:     $Version" -ForegroundColor Gray

# 1. Check prerequisites
Write-Host '--> Checking prerequisites...' -ForegroundColor Cyan
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw 'Git is required. Install from https://git-scm.com/downloads'
'
}
if (-not (Get-Command rustc -ErrorAction SilentlyContinue)) {
    Write-Host '    Installing Rust via rustup...' -ForegroundColor Yellow
    Invoke-WebRequest 'https://win.rustup.rs/x86_64' -OutFile "$env:TEMP\rustup-init.exe"
    & "$env:TEMP\rustup-init.exe" -y --default-toolchain stable --profile minimal
    $env:Path = "$env:USERPROFILE\.cargo\bin;$env:Path"
}

# 2. Download Tracera
Write-Host '--> Downloading Tracera...' -ForegroundColor Cyan
New-Item -ItemType Directory -Path $RepoRoot -Force | Out-Null
Push-Location $RepoRoot
git clone --depth 1 --branch main "https://github.com/$Repo.git" . 2>&1 | Out-Null
Pop-Location

# 3. Build binaries
Write-Host '--> Building tracera-server + tracera CLI (release mode)...' -ForegroundColor Cyan
Push-Location $RepoRoot
cargo build --release -p tracera-server -p tracera-cli 2>&1 | Out-Null
Pop-Location

# 4. Install to LOCALAPPDATA
Write-Host '--> Installing to $InstallDir\bin...' -ForegroundColor Cyan
New-Item -ItemType Directory -Path "$InstallDir\bin" -Force | Out-Null
Copy-Item "$RepoRoot\target\release\tracera-server.exe" "$InstallDir\bin\tracera-server.exe" -Force
Copy-Item "$RepoRoot\target\release\tracera.exe" "$InstallDir\bin\tracera.exe" -Force

# 5. Add to PATH
$binPath = "$InstallDir\bin"
$currentPath = [Environment]::GetEnvironmentVariable('Path', 'User')
if ($currentPath -notlike "*$binPath*") {
    [Environment]::SetEnvironmentVariable('Path', "$currentPath;$binPath", 'User')
    $env:Path = "$env:Path;$binPath"
}

# 6. Create Start Menu shortcut
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut("$env:APPDATA\Microsoft\Windows\Start Menu\Programs\PhenotypeApps\Tracera.lnk")
$shortcut.TargetPath = "$InstallDir\bin\tracera-server.exe"
$shortcut.Arguments = "--port 8080"
$shortcut.WorkingDirectory = $InstallDir
$shortcut.Description = 'Tracera - Requirements Traceability'
$shortcut.Save()

# 7. Cleanup
Remove-Item $RepoRoot -Recurse -Force

# 8. Verify
Write-Host '--> Verifying installation...' -ForegroundColor Cyan
$version = & "$InstallDir\bin\tracera.exe" --version 2>&1 | Select-Object -First 1
Write-Host "    tracera-server: $InstallDir\bin\tracera-server.exe" -ForegroundColor Green
Write-Host "    tracera CLI:    $InstallDir\bin\tracera.exe" -ForegroundColor Green
Write-Host "    Version:        $version" -ForegroundColor Green
Write-Host "    Start Menu:     PhenotypeApps\Tracera" -ForegroundColor Green

Write-Host ''
Write-Host 'Tracera installed successfully!' -ForegroundColor Green
Write-Host ''
Write-Host 'To start the server:' -ForegroundColor Cyan
Write-Host '  set DATABASE_URL=sqlite::memory: && tracera-server --port 8080' -ForegroundColor White
Write-Host ''
Write-Host 'Or click Start Menu > PhenotypeApps > Tracera' -ForegroundColor White