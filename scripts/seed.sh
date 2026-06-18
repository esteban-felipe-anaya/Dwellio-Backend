#!/usr/bin/env bash
# Re-import the seed data (idempotent).
set -euo pipefail
cd "$(dirname "$0")/../server"
if [[ "${OS:-}" == "Windows_NT" ]]; then PY=".venv/Scripts/python.exe"; else PY=".venv/bin/python"; fi
"$PY" -m app.seed.import_seed "$@"
