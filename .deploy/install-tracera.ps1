# Tracera — PowerShell installer stub
# Builds a self-contained `tracera-launcher.exe` on the user's desktop
# via PS2EXE, plus registers a Start Menu shortcut under phenotypeApps.
# Run on Windows PowerShell 5.1 or PowerShell 7+.
#
#   pwsh -File install-tracera.ps1 -BuildExe
#
# This is the "installer" tier — it does NOT replace in-place cargo build
# or process-compose up; it just wraps the launcher so users can double-click.

[CmdletBinding()]
param(
    [switch]$BuildExe,
    [switch]$AddStartMenuShortcut,
    [string]$Source = "E:\phase-finish-stack\Tracera\.deploy\launch-tracera.bat",
    [string]$ShortcutDir = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\phenotypeApps"
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path $Source)) {
    throw "Missing launcher source: $Source"
}

if ($AddStartMenuShortcut) {
    if (-not (Test-Path $ShortcutDir)) {
        New-Item -ItemType Directory -Force -Path $ShortcutDir | Out-Null
    }
    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut((Join-Path $ShortcutDir "Tracera.lnk"))
    $shortcut.TargetPath = $Source
    $shortcut.WorkingDirectory = (Split-Path $Source -Parent)
    $shortcut.WindowStyle = 7  # minimized
    $shortcut.Description = "Tracera — start the process-compose stack"
    $shortcut.Save()
    Write-Host "[OK] Start Menu shortcut installed at $ShortcutDir\Tracera.lnk"
}

if ($BuildExe) {
    Write-Host "[*] Building tracera-launcher.exe via PS2EXE ..."
    # Install ps2exe if missing
    if (-not (Get-Module -ListAvailable -Name ps2exe)) {
        Install-Module -Name ps2exe -Scope CurrentUser -Force
    }
    Import-Module ps2exe
    $exeOut = Join-Path (Split-Path $Source -Parent) "tracera-launcher.exe"
    Invoke-ps2exe -inputFile $Source -outputFile $exeOut -requireAdmin -noConsole -noError
    Write-Host "[OK] Built: $exeOut"
}

Write-Host ""
Write-Host "Tracera installer stub complete."
Write-Host "Source  : $Source"
Write-Host "Shortcuts: $ShortcutDir\Tracera.lnk"
