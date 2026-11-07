$ErrorActionPreference = 'Stop'
$repo = Split-Path $PSScriptRoot -Parent
function Invoke-Checked { param([scriptblock]$Command) & $Command; if ($LASTEXITCODE -ne 0) { throw "Check failed with exit code $LASTEXITCODE" } }
Push-Location (Join-Path $repo 'backend')
try {
    Invoke-Checked { & ./.venv/Scripts/python.exe -m ruff check . }
    Invoke-Checked { & ./.venv/Scripts/python.exe -m ruff format --check . }
    Invoke-Checked { & ./.venv/Scripts/python.exe -m mypy app }
    Invoke-Checked { & ./.venv/Scripts/python.exe -m pytest -q }
} finally { Pop-Location }
Push-Location (Join-Path $repo 'web')
try {
    foreach ($task in @('lint', 'format:check', 'test', 'build')) { Invoke-Checked { npm.cmd run $task } }
} finally { Pop-Location }
