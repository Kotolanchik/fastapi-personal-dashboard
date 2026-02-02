# Режим разработки: hot reload без пересборки
# Usage: .\run-dev.ps1   (первый раз: .\run-dev.ps1 --build или добавь --build в команду ниже)
Set-Location $PSScriptRoot
docker compose -f docker-compose.dev.yml up
