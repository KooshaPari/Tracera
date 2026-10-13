<# Cutover sqlite -> Postgres+Redis (run only in an approved window). Rollback keeps sqlite file untouched (kept 7 days).
   Steps: backup -> stop TraceraServer -> final sqlite2pg into `tracera` DB -> install.ps1 -Backend postgres -> start -> verify.
   On any failure: restore sqlite env, restart, exit 1. #>
param([string]$Sqlite='C:\Users\koosh\agents\tracera\tracera-1099.db')
. "$PSScriptRoot\common.ps1"
& "$PSScriptRoot\backup.ps1"
Stop-ScheduledTask -TaskName TraceraServer -ErrorAction SilentlyContinue
Get-Process tracera-live -ErrorAction SilentlyContinue | Stop-Process -Force
try {
  # 1. Point at Postgres and start once so the server applies its migrations to the (empty) `tracera` DB.
  & "$PSScriptRoot\install.ps1" -Backend postgres
  Start-ScheduledTask -TaskName TraceraServer; Start-Sleep 10
  Stop-ScheduledTask -TaskName TraceraServer; Get-Process tracera-live -ErrorAction SilentlyContinue | Stop-Process -Force
  # 2. Final data load (sqlite is quiesced), run inside Fedora where podman lives.
  $wslDb = '/mnt/' + $Sqlite.Substring(0,1).ToLower() + ($Sqlite.Substring(2) -replace '\\','/')
  $wslPy = '/mnt/' + $PSScriptRoot.Substring(0,1).ToLower() + ($PSScriptRoot.Substring(2) -replace '\\','/') + '/sqlite2pg.py'
  & wsl.exe -d $Distro -- python3 $wslPy $wslDb $PgCont tracera
  if ($LASTEXITCODE) { throw 'data load failed' }
  # 3. Start and verify.
  Start-ScheduledTask -TaskName TraceraServer; Start-Sleep 8
  & "$PSScriptRoot\verify.ps1" -ExpectBackend postgres
  if ($LASTEXITCODE) { throw 'verify failed' }
  Write-Host 'CUTOVER OK. sqlite file retained as rollback.'
} catch {
  Write-Warning "rollback: $_"
  Stop-ScheduledTask -TaskName TraceraServer -ErrorAction SilentlyContinue
  & "$PSScriptRoot\install.ps1" -Backend sqlite
  Start-ScheduledTask -TaskName TraceraServer
  exit 1
}
