@echo off
REM Windows shim so `make <target>` works in cmd/PowerShell without GNU make.
REM Mirrors the Makefile targets. Run from the backend\ folder.
setlocal enabledelayedexpansion

set "PY=server\.venv\Scripts\python.exe"
set "TARGET=%~1"
if "%TARGET%"=="" set "TARGET=help"

if /I "%TARGET%"=="help" (
  echo setup      - create venv, install deps, copy .env
  echo migrate    - alembic upgrade head
  echo seed       - import seed_data.json ^(idempotent^)
  echo run        - uvicorn on :8000 ^(reload^)
  echo admin      - Next.js admin on :3001
  echo test       - pytest
  echo lint / fmt - ruff + black
  echo superuser  - create/promote a staff superuser
  echo reset      - delete the local SQLite db
  goto :eof
)

if /I "%TARGET%"=="setup" (
  python -m venv server\.venv || goto :err
  "%PY%" -m pip install --upgrade pip || goto :err
  "%PY%" -m pip install -r server\requirements.txt || goto :err
  if not exist server\.env copy server\.env.example server\.env
  goto :eof
)

if /I "%TARGET%"=="migrate"   ( pushd server & "..\%PY%" -m alembic upgrade head & popd & goto :eof )
if /I "%TARGET%"=="seed"      ( pushd server & "..\%PY%" -m app.seed.import_seed & popd & goto :eof )
if /I "%TARGET%"=="run"       ( pushd server & "..\%PY%" -m uvicorn app.main:app --reload --port 8000 & popd & goto :eof )
if /I "%TARGET%"=="test"      ( pushd server & "..\%PY%" -m pytest -q & popd & goto :eof )
if /I "%TARGET%"=="lint"      ( pushd server & "..\%PY%" -m ruff check app & "..\%PY%" -m black --check app & popd & goto :eof )
if /I "%TARGET%"=="fmt"       ( pushd server & "..\%PY%" -m ruff check --fix app & "..\%PY%" -m black app & popd & goto :eof )
if /I "%TARGET%"=="superuser" ( pushd server & "..\%PY%" -m app.seed.create_superuser & popd & goto :eof )
if /I "%TARGET%"=="reset"     ( if exist server\dev.sqlite3 del server\dev.sqlite3 & goto :eof )
if /I "%TARGET%"=="admin"         ( pushd admin & npm run dev & popd & goto :eof )
if /I "%TARGET%"=="admin-install" ( pushd admin & npm install & popd & goto :eof )

echo Unknown target: %TARGET%
goto :eof

:err
echo.
echo Command failed.
exit /b 1
