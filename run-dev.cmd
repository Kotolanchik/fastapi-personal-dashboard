@echo off
REM Режим разработки: hot reload без пересборки
REM Usage: run-dev.cmd   (первый раз добавь --build: docker compose -f docker-compose.dev.yml up --build)
cd /d "%~dp0"
docker compose -f docker-compose.dev.yml up
