#!/usr/bin/env bash
# One-shot local setup (no Docker): venv + deps + .env + migrate + seed.
set -euo pipefail
cd "$(dirname "$0")/.."

SERVER=server
if [[ "${OS:-}" == "Windows_NT" ]]; then
  PY="$SERVER/.venv/Scripts/python.exe"; SYS_PY=python
else
  PY="$SERVER/.venv/bin/python"; SYS_PY=python3
fi

echo "==> Creating virtualenv"
"$SYS_PY" -m venv "$SERVER/.venv"
"$PY" -m pip install --upgrade pip
"$PY" -m pip install -r "$SERVER/requirements.txt"

[[ -f "$SERVER/.env" ]] || cp "$SERVER/.env.example" "$SERVER/.env"

echo "==> Running migrations"
(cd "$SERVER" && "../$PY" -m alembic upgrade head)

echo "==> Seeding"
(cd "$SERVER" && "../$PY" -m app.seed.import_seed)

echo "==> Done. Start with: make run   (API on http://localhost:8000/docs)"
