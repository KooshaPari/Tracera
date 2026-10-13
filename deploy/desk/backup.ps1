<# Nightly backup. Postgres: pg_dump -Fc inside the container. SQLite: file copy. Both -> C: and G: with SHA256,
   retention 14 days local. Offsite: Cloudflare R2 FREE TIER ONLY (small dumps, keep the newest 7 objects, hard 5 GB stop).
   R2 creds come from tracera.env as R2_ENDPOINT, R2_BUCKET, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY (set via vault link, never in chat). Skipped with a warning if absent. #>
. "$PSScriptRoot\common.ps1"
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$e = Read-EnvFile
$out = Join-Path $LocalBackupDir $stamp; New-Item -ItemType Directory -Force $out, $BackupDir | Out-Null
if ($e['DATABASE_URL'] -like 'postgres*') {
  $db = ($e['DATABASE_URL'] -split '/')[-1]
  Invoke-PgSh "pg_dump -U `"`$POSTGRES_USER`" -Fc $db > /tmp/t.dump"
  Invoke-Pod @('cp', "${PgCont}:/tmp/t.dump", "/mnt/c/Users/koosh/backups/tracera/$stamp/tracera.dump")
} else {
  Copy-Item (Join-Path $Root 'tracera-1099.db') (Join-Path $out 'tracera.db')
}
Get-ChildItem $out -File | ForEach-Object { "$((Get-FileHash $_.FullName -Algorithm SHA256).Hash)  $($_.Name)" } | Set-Content (Join-Path $out 'SHA256SUMS.txt')
Copy-Item $out (Join-Path $BackupDir $stamp) -Recurse -Force
Get-ChildItem $LocalBackupDir -Directory | Sort-Object Name -Descending | Select-Object -Skip 14 | Remove-Item -Recurse -Force
if ($e['R2_ENDPOINT'] -and $e['R2_BUCKET']) {
  $env:AWS_ACCESS_KEY_ID=$e['AWS_ACCESS_KEY_ID']; $env:AWS_SECRET_ACCESS_KEY=$e['AWS_SECRET_ACCESS_KEY']
  aws s3 cp $out "s3://$($e['R2_BUCKET'])/tracera/$stamp/" --recursive --endpoint-url $e['R2_ENDPOINT']
  $keep = aws s3 ls "s3://$($e['R2_BUCKET'])/tracera/" --endpoint-url $e['R2_ENDPOINT'] | ForEach-Object { ($_ -split '\s+')[-1] } | Sort-Object -Descending | Select-Object -Skip 7
  foreach ($k in $keep) { aws s3 rm "s3://$($e['R2_BUCKET'])/tracera/$k" --recursive --endpoint-url $e['R2_ENDPOINT'] }
} else { Write-Warning 'R2 not configured; offsite copy skipped (local C: + G: copies made).' }
Write-Host "backup ok: $out"
