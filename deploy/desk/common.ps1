# Shared settings for the desk scripts. Dot-source: . "$PSScriptRoot\common.ps1"
$ErrorActionPreference = 'Stop'
$Root      = 'C:\Users\koosh\agents\tracera'
$Exe       = Join-Path $Root 'tracera-live.exe'
$EnvFile   = Join-Path $Root 'tracera.env'        # KEY=VALUE lines, not in git, written by install.ps1
$Distro    = 'FedoraLinux-44'
$PgCont    = 'tracera_postgres17_1'
$BackupDir = 'G:\backups\tracera'
$LocalBackupDir = 'C:\Users\koosh\backups\tracera'
function Invoke-Pod { param([string[]]$Args) & wsl.exe -d $Distro -- podman @Args }
# Run a shell snippet inside the Postgres container so credentials never leave it.
function Invoke-PgSh { param([string]$Cmd) & wsl.exe -d $Distro -- podman exec $PgCont sh -c $Cmd }
function Read-EnvFile { $h=@{}; if (Test-Path $EnvFile) { Get-Content $EnvFile | ForEach-Object { if ($_ -match '^\s*([A-Za-z_][A-Za-z0-9_]*)=(.*)$') { $h[$Matches[1]]=$Matches[2] } } }; $h }
