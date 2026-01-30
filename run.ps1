# Full stack: Postgres + Redis + Backend + React
# Usage: .\run.ps1   or   pwsh -File run.ps1
Set-Location $PSScriptRoot
docker compose -f docker-compose.full.yml up --build
