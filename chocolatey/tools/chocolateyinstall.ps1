$ErrorActionPreference = 'Stop'

# ---------------------------------------------------------------------------
# Tracera Chocolatey installer
#
# Downloads the archive that .github/workflows/release-dist.yml actually
# publishes for its only Windows target, x86_64-pc-windows-msvc:
#
#   tracera-x86_64-windows.zip  ->  tracera-server.exe + tracera.exe (CLI)
#
# There is no i686 build and no bare .exe asset, so this package ships a
# 64-bit-only URL and rejects 32-bit systems with a clear error instead of
# pointing at files that do not exist.
# ---------------------------------------------------------------------------

# === VERSION PIN — the single place to bump when cutting a release. ===
# Keep <version> and <releaseNotes> in ../tracera.nuspec in sync with this tag.
$releaseTag = 'v2.4.0'

# Asset names produced by release-dist.yml (Windows matrix entry). Only
# change these if that workflow renames its artifacts.
$archiveName = 'tracera-x86_64-windows.zip'
$manifestName = 'release-manifest-x86_64-pc-windows-msvc.json'

$packageName = 'tracera'
$toolsDir = "$(Split-Path -Parent $MyInvocation.MyCommand.Definition)"
$releaseBase = "https://github.com/KooshaPari/Tracera/releases/download/$releaseTag"

# release-dist.yml builds only x86_64-pc-windows-msvc. Fail fast and clearly
# on 32-bit Windows rather than installing nothing.
if ((Get-ProcessorBits) -ne 64) {
  throw "Tracera ships only x86_64-pc-windows-msvc builds (see .github/workflows/release-dist.yml in KooshaPari/Tracera). 32-bit Windows is not supported by this package."
}

# Chocolatey refuses HTTPS downloads without a package checksum by default
# (allowEmptyChecksumsSecure is off). The archive's sha256 cannot be pinned
# here before the release exists, so verify against the provenance manifest
# that release-dist.yml generates in CI from the archive bytes and uploads
# alongside it. This catches corrupt, partial, or mismatched downloads.
try {
  [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072 # TLS 1.2
} catch { }

$chocoTempDir = Join-Path $env:TEMP "chocolatey\$packageName\$($env:chocolateyPackageVersion)"
New-Item -ItemType Directory -Force -Path $chocoTempDir | Out-Null
$manifestPath = Join-Path $chocoTempDir $manifestName
Invoke-WebRequest -Uri "$releaseBase/$manifestName" -OutFile $manifestPath -UseBasicParsing
$manifest = Get-Content $manifestPath -Raw | ConvertFrom-Json
$artifact = $manifest.artifacts | Where-Object { $_.name -eq $archiveName }
if (-not $artifact -or -not $artifact.present -or -not $artifact.sha256) {
  throw "Release manifest for $releaseTag has no sha256 for '$archiveName'. Refusing to install an unverified archive."
}

$packageArgs = @{
  packageName    = $packageName
  unzipLocation  = $toolsDir
  url64bit       = "$releaseBase/$archiveName"
  checksum64     = $artifact.sha256
  checksumType64 = 'sha256'
}
Install-ChocolateyZipPackage @packageArgs

# release-dist.yml zips the binaries straight out of the cargo target dir, so
# they extract under target\x86_64-pc-windows-msvc\release\. Flatten them into
# the package tools dir (and drop the leftover target tree) so PATH, the
# Start Menu shortcut, and Chocolatey's automatic shims all see them.
$nestedReleaseDir = Join-Path $toolsDir 'target\x86_64-pc-windows-msvc\release'
if (Test-Path $nestedReleaseDir) {
  Get-ChildItem -Path $nestedReleaseDir -File | Move-Item -Destination $toolsDir -Force
  Remove-Item -Path (Join-Path $toolsDir 'target') -Recurse -Force
}

# The user gets two binaries: the API/UI server (Start Menu shortcut target,
# serves the web app) and the `tracera` CLI for repo operations.
$serverExe = Join-Path $toolsDir 'tracera-server.exe'
$cliExe = Join-Path $toolsDir 'tracera.exe'
if (-not (Test-Path $serverExe)) {
  throw "Expected '$serverExe' after extraction, but it is missing."
}
if (-not (Test-Path $cliExe)) {
  Write-Warning "Expected '$cliExe' after extraction, but it is missing; the tracera CLI will not be available."
}

# Add tools dir to PATH (Chocolatey also auto-shims both exes into
# $env:ChocolateyInstall\bin, which is already on PATH).
Install-ChocolateyPath $toolsDir

# Create Start Menu shortcut launching the server. tracera-server takes no
# CLI arguments: it reads TRACERA_BIND_ADDR / PORT env vars and defaults to
# 127.0.0.1:8080 (crates/tracera-server/src/main.rs), so no Arguments are set.
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut("$env:ProgramData\Microsoft\Windows\Start Menu\Programs\PhenotypeApps\Tracera.lnk")
$shortcut.TargetPath = $serverExe
$shortcut.Save()

Write-Host "Tracera $releaseTag installed via Chocolatey!"
Write-Host "  Server: $serverExe (Start Menu shortcut; 'tracera-server' on PATH)"
Write-Host "  CLI:    $cliExe ('tracera' on PATH)"
