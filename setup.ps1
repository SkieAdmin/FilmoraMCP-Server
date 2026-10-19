param([string]$Python = "python")
$ErrorActionPreference = "Stop"
$projectRoot = $PSScriptRoot
$venvPython = Join-Path $projectRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $venvPython)) {
    & $Python -m venv (Join-Path $projectRoot '.venv')
    if ($LASTEXITCODE -ne 0) { throw 'Could not create virtual environment' }
}
& $venvPython -m pip install -e "${projectRoot}[dev]"
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed' }
& $venvPython (Join-Path $projectRoot 'scripts\write_client_configs.py')
if ($LASTEXITCODE -ne 0) { throw 'Client config generation failed' }
Write-Host "FilmoraMCP ready. See README.md and client-configs. Python: $venvPython"
