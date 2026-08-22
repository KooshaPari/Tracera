$ErrorActionPreference = 'Stop'

$packageName = 'tracera'
$toolsDir = "$(Split-Path -parent $MyInvocation.MyCommand.Definition)"
$url64 = 'https://github.com/KooshaPari/Tracera/releases/download/v2.2.0/tracera-server-x86_64-pc-windows-msvc.exe'
$url = 'https://github.com/KooshaPari/Tracera/releases/download/v2.2.0/tracera-server-i686-pc-windows-msvc.exe'

$packageArgs = @{
  packageName    = $packageName
  unzipLocation  = $toolsDir
  installerType  = 'exe'
  url64bit       = $url64
  url            = $url
  checksum64     = ''
  checksumType64 = 'sha256'
  silentArgs     = '/S'
  validExitCodes = @(0)
  softwareName   = 'Tracera'
}

Install-ChocolateyPackage @packageArgs

# Add to PATH
Install-ChocolateyPath "$env:ChocolateyInstall\lib\tracera\tools"

# Create Start Menu shortcut
$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut("$env:ProgramData\Microsoft\Windows\Start Menu\Programs\PhenotypeApps\Tracera.lnk")
$shortcut.TargetPath = "$env:ChocolateyInstall\lib\tracera\tools\tracera-server.exe"
$shortcut.Arguments = '--port 8080'
$shortcut.Save()

Write-Host 'Tracera installed via Chocolatey!'