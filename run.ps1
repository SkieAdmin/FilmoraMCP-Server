$ErrorActionPreference = 'Stop'
& (Join-Path $PSScriptRoot '.venv\Scripts\python.exe') -m filmora_mcp.server @args
exit $LASTEXITCODE
