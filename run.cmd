@echo off
REM Full stack: Postgres + Redis + Backend + React
REM Usage: run.cmd
cd /d "%~dp0"
docker compose -f docker-compose.full.yml up --build
