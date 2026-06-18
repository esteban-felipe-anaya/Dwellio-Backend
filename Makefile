# Dwellio backend — developer tasks (no Docker). Runs under Git Bash on Windows.
SHELL := bash
SERVER := server
ADMIN := admin

# Pick the venv python for the host OS.
ifeq ($(OS),Windows_NT)
  PY := $(SERVER)/.venv/Scripts/python.exe
  SYS_PY := python
else
  PY := $(SERVER)/.venv/bin/python
  SYS_PY := python3
endif

.PHONY: setup migrate seed run admin test lint fmt superuser reset admin-install help

help:
	@echo "setup      - create venv, install deps, copy .env"
	@echo "migrate    - alembic upgrade head"
	@echo "seed       - import seed_data.json (idempotent)"
	@echo "run        - uvicorn on :8000 (reload)"
	@echo "admin      - Next.js admin on :3001"
	@echo "test       - pytest"
	@echo "lint / fmt - ruff + black"
	@echo "superuser  - create/promote a staff superuser"
	@echo "reset      - delete the local SQLite db"

setup:
	$(SYS_PY) -m venv $(SERVER)/.venv
	$(PY) -m pip install --upgrade pip
	$(PY) -m pip install -r $(SERVER)/requirements.txt
	cp -n $(SERVER)/.env.example $(SERVER)/.env || true

migrate:
	cd $(SERVER) && ../$(PY) -m alembic upgrade head

seed:
	cd $(SERVER) && ../$(PY) -m app.seed.import_seed

run:
	cd $(SERVER) && ../$(PY) -m uvicorn app.main:app --reload --port 8000

test:
	cd $(SERVER) && ../$(PY) -m pytest -q

lint:
	cd $(SERVER) && ../$(PY) -m ruff check app && ../$(PY) -m black --check app

fmt:
	cd $(SERVER) && ../$(PY) -m ruff check --fix app && ../$(PY) -m black app

superuser:
	cd $(SERVER) && ../$(PY) -m app.seed.create_superuser

reset:
	rm -f $(SERVER)/dev.sqlite3

admin-install:
	cd $(ADMIN) && npm install

admin:
	cd $(ADMIN) && npm run dev
