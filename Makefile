SHELL := /bin/bash

.PHONY: help install migrate dwh-migrate run-backend run-frontend docker-up docker-down test lint format

help:
	@echo "Targets:"
	@echo "  install       Install Python dependencies"
	@echo "  migrate       Run app database migrations"
	@echo "  dwh-migrate   Run DWH database migrations"
	@echo "  run-backend   Start FastAPI backend"
	@echo "  run-frontend  Start Streamlit frontend"
	@echo "  docker-up     Start via Docker Compose"
	@echo "  docker-down   Stop Docker Compose"
	@echo "  test          Run pytest"
	@echo "  lint          Run ruff lint"
	@echo "  format        Run ruff format"

install:
	python -m pip install --upgrade pip
	pip install -r requirements.txt -r requirements-dev.txt

migrate:
	alembic upgrade head

dwh-migrate:
	alembic -c dwh/alembic.ini upgrade head

run-backend:
	uvicorn backend.app.main:app --reload --port 8000

run-frontend:
	streamlit run frontend/app.py

docker-up:
	docker compose up --build

docker-down:
	docker compose down

test:
	pytest -q

lint:
	ruff check .

format:
	ruff format .
