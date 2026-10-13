<# Post-deploy verification. Usage: .\verify.ps1 [-Url http://127.0.0.1:8080] [-ExpectProjects 6] [-ExpectBackend postgres]
   Exits non-zero on any failure. Checks: API up, project count, no HTML for unknown /api paths (deploy pattern rule 3), and for postgres row counts. #>
param([string]$Url='http://127.0.0.1:8080',[int]$ExpectProjects=6,[string]$ExpectBackend='')
. "$PSScriptRoot\common.ps1"
$fail = 0
function Check($name,$ok,$detail){ if($ok){Write-Host "PASS $name $detail"}else{Write-Host "FAIL $name $detail"; $script:fail++} }
try { $p = Invoke-RestMethod "$Url/api/v1/projects" -TimeoutSec 15
  $n = if ($p.projects) { @($p.projects).Count } else { @($p).Count }
  Check 'projects' ($n -eq $ExpectProjects) "got $n expected $ExpectProjects" } catch { Check 'projects' $false $_.Exception.Message }
try { $r = Invoke-WebRequest "$Url/api/v1/__nope__" -UseBasicParsing -TimeoutSec 15 -SkipHttpErrorCheck
  Check 'no-html-for-unknown-api' ($r.Headers['Content-Type'] -notlike 'text/html*') "ct=$($r.Headers['Content-Type'])" } catch { Check 'no-html-for-unknown-api' $true 'non-2xx' }
if ($ExpectBackend -eq 'postgres') {
  $c = Invoke-PgSh 'psql -U "$POSTGRES_USER" -d tracera -Atc "select (select count(*) from projects),(select count(*) from items),(select count(*) from links),(select count(*) from teams)"'
  Check 'pg-counts' ($c -match '^\d+\|\d+\|\d+\|\d+$') $c
}
if ($fail) { exit 1 } else { Write-Host 'verify OK' }
