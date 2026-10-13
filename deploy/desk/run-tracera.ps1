# Service entry point (run by the TraceraServer scheduled task). Reads tracera.env, appends to server.log.
. "$PSScriptRoot\common.ps1"
$e = Read-EnvFile
foreach ($k in $e.Keys) { Set-Item -Path "Env:$k" -Value $e[$k] }
if (-not $env:TRACERA_FRONTEND_DIST) { $env:TRACERA_FRONTEND_DIST = Join-Path $Root 'fe-dist3' }
if (-not $env:RUST_LOG) { $env:RUST_LOG = 'info' }
$log = if ($env:TRACERA_LOG_FILE) { $env:TRACERA_LOG_FILE } else { Join-Path $Root 'server.log' }
& $Exe *>> $log
exit $LASTEXITCODE
