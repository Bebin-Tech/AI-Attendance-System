param([switch]$ConfirmReset)
$ErrorActionPreference = 'Stop'
if (-not $ConfirmReset) { throw 'Destructive local reset requires -ConfirmReset. This deletes the AIFAMS development database.' }
$compose = Join-Path (Split-Path $PSScriptRoot -Parent) 'infrastructure/docker-compose.yml'
docker compose -f $compose down --volumes
if ($LASTEXITCODE -ne 0) { throw 'Database reset failed.' }
