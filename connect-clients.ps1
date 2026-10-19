param([switch]$Preview, [string]$RelocateFrom)
$ErrorActionPreference = 'Stop'
$venvPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $venvPython)) { throw 'Run setup.ps1 first' }
$installerArgs = @((Join-Path $PSScriptRoot 'scripts\install_clients.py'))
if (-not $Preview) { $installerArgs += '--apply' }
if ($RelocateFrom) { $installerArgs += @('--relocate-from', $RelocateFrom) }
& $venvPython @installerArgs
exit $LASTEXITCODE
