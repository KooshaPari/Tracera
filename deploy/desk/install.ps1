<#
 Installs the Tracera desk service + nightly backup as Windows scheduled tasks (idempotent).
 Usage (elevated or as koosh):  .\install.ps1 [-Backend sqlite|postgres] [-Staging]
   -Staging   bind 127.0.0.1:18080 against the tracera_staging database (production untouched)
 Does NOT touch an already-running server; it registers tasks and writes tracera.env. Starting is cutover.ps1's job.
#>
param([ValidateSet('sqlite','postgres')][string]$Backend='sqlite', [switch]$Staging)
. "$PSScriptRoot\common.ps1"
$lines = @()
if ($Backend -eq 'sqlite') {
  $lines += 'DATABASE_URL=sqlite:///C:/Users/koosh/agents/tracera/tracera-1099.db?mode=rwc'
} else {
  # Compose the URL inside the container's own env; the password is written only to tracera.env (user ACL), never printed.
  $db = if ($Staging) { 'tracera_staging' } else { 'tracera' }
  $url = Invoke-PgSh ('printf "postgres://%s:%s@127.0.0.1:5432/' + $db + '" "$POSTGRES_USER" "$POSTGRES_PASSWORD"')
  $lines += "DATABASE_URL=$url"
  $lines += 'REDIS_URL=redis://127.0.0.1:6379'
}
if ($Staging) { $lines += 'TRACERA_BIND_ADDR=127.0.0.1:18080'; $lines += 'TRACERA_LOG_FILE=C:\Users\koosh\agents\tracera\staging.log' }
$lines | Set-Content -Encoding ascii $EnvFile
icacls $EnvFile /inheritance:r /grant:r "$env:USERNAME`:F" | Out-Null
$ps = (Get-Command powershell.exe).Source
$name = if ($Staging) { 'TraceraServerStaging' } else { 'TraceraServer' }
$act  = New-ScheduledTaskAction -Execute $ps -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$PSScriptRoot\run-tracera.ps1`""
$trg  = New-ScheduledTaskTrigger -AtStartup
$set  = New-ScheduledTaskSettingsSet -RestartCount 5 -RestartInterval (New-TimeSpan -Minutes 1) -ExecutionTimeLimit ([TimeSpan]::Zero) -StartWhenAvailable -AllowStartIfOnBatteries
Register-ScheduledTask -TaskName $name -Action $act -Trigger $trg -Settings $set -User $env:USERNAME -RunLevel Limited -Force | Out-Null
if (-not $Staging) {
  $bact = New-ScheduledTaskAction -Execute $ps -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$PSScriptRoot\backup.ps1`""
  Register-ScheduledTask -TaskName 'TraceraBackup' -Action $bact -Trigger (New-ScheduledTaskTrigger -Daily -At 3:30am) -User $env:USERNAME -Force | Out-Null
}
Write-Host "Registered $name (backend=$Backend). Not started."
