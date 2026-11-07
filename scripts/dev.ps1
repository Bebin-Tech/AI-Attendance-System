$ErrorActionPreference = 'Stop'
$compose = Join-Path (Split-Path $PSScriptRoot -Parent) 'infrastructure/docker-compose.yml'
docker compose -f $compose up --build
if ($LASTEXITCODE -ne 0) { throw 'Compose failed. Check Docker Desktop and service logs.' }
