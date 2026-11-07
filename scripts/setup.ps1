$ErrorActionPreference = 'Stop'
$repo = Split-Path $PSScriptRoot -Parent
function Invoke-Checked { param([scriptblock]$Command) & $Command; if ($LASTEXITCODE -ne 0) { throw "Command failed with exit code $LASTEXITCODE" } }
Push-Location $repo
try {
    $python = $env:AIFAMS_PYTHON
    if ($python) {
        $version = & $python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
        if ($version -ne '3.13') { throw 'AIFAMS_PYTHON must point to Python 3.13.' }
        Invoke-Checked { & $python -m venv backend/.venv }
    } else {
        Invoke-Checked { py -3.13 -m venv backend/.venv }
    }
    Invoke-Checked { & ./backend/.venv/Scripts/python.exe -m pip install -r backend/requirements-dev.txt }
    if (-not (Test-Path backend/.env)) { Copy-Item backend/.env.example backend/.env }
    Push-Location web
    try { Invoke-Checked { npm.cmd ci } } finally { Pop-Location }
} finally { Pop-Location }
