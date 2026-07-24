Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Warning 'This launcher targets the retired Python/FastAPI service on port 8000. Use the Rust tracera-server and deploy/selfhost instructions for current deployments.'

$repoRoot = 'E:\Dev\Tracera'
$docsUrl = 'http://localhost:8000/docs'

try {
    Set-Location $repoRoot

    $docker = Get-Command docker -ErrorAction SilentlyContinue
    if ($null -ne $docker) {
        docker compose up -d | Out-Null
        Start-Sleep -Seconds 8
    }
    else {
        $uv = Get-Command uv -ErrorAction SilentlyContinue
        if ($null -eq $uv) {
            throw 'Neither docker nor uv is available.'
        }

        Start-Process -FilePath $uv.Source -ArgumentList @(
            'run',
            'uvicorn',
            'tracertm.api.main:app',
            '--host', '127.0.0.1',
            '--port', '8000'
        ) -WorkingDirectory $repoRoot

        Start-Sleep -Seconds 5
    }

    Start-Process $docsUrl
}
catch {
    Write-Error $_
    exit 1
}
