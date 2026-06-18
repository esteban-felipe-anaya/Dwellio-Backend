# Dwellio Backend — FastAPI + PostgreSQL + Next.js/MUI Admin

A production-quality backend for the **Dwellio** Flutter real-estate app, plus a
**Next.js + Material UI** admin dashboard. The Flutter app works against this backend by
**only changing its base URL** — same paths, query params, and JSON shapes.

```
backend/
  server/        FastAPI app (async SQLAlchemy 2.0, Alembic, Pydantic v2)
    app/
      core/      config, security (JWT+bcrypt), db (async engine), computations
      models/    SQLAlchemy models (string PKs: lst_, agt_, usr_, …)
      schemas/   Pydantic v2 (camelCase) — public + distinct admin schemas
      api/       deps, serializers, listing_query, routes/ (public + /admin-api)
      seed/      seed_data.json + idempotent importer + superuser script
      main.py    app: CORS, /media static, routers, exception handlers
    alembic/     async migrations
    tests/       pytest-asyncio (auth, bounds/filter parity, server-side mortgage)
  admin/         Next.js (App Router, TS strict) + MUI v6 + X DataGrid/Charts
  Makefile  scripts/  .gitignore
```

## Why it matches the app exactly

The contract was derived from the Flutter app's `lib/data` (Retrofit client + freezed
models). Key parity rules:

- **String primary keys** preserve the app's prefixed ids (`lst_…`, `agt_…`).
- `POST /auth/login` / `/auth/register` take a **JSON body** and return **`{ token, user }`**;
  `GET /auth/me` returns `{ user }`. Login/register **don't** apply the auth dependency, so a
  stale `Authorization` header never blocks signing in.
- **List endpoints return plain JSON arrays** (manual `_page`/`_limit` paging + `X-Total-Count`).
- Money/area/rating are **JSON numbers**, never strings. Image URLs are plain strings (so
  relative `/media/...` upload paths round-trip).
- **camelCase** everywhere via a Pydantic `alias_generator`; camelCase query params via `Query(alias=…)`.
- **Map-bounds search** on `GET /listings` (`swLat,swLng,neLat,neLng`) + all app filters
  (`dealType,q,minPrice,maxPrice,beds,baths,type,minArea,amenities,sort`) + `sort=distance`
  (Haversine). Plain lat/lng range filtering — works on **PostgreSQL and SQLite** (PostGIS is an
  optional prod upgrade).
- **Server-side derived numbers** (never trusted from the client): mortgage estimate
  (`GET /listings/{id}/mortgage`), price-per-sqm, distance.
- **Time-based tour status** (`requested → confirmed → upcoming → completed`) computed from
  `scheduledFor`; saved-search "new matches" computed live.
- `Agent`, `PropertyType`, `Amenity` are **DB-backed lookups** with admin CRUD.

---

## Quick start (no Docker)

Requires **Python 3.11+** and **Node 18+**. PostgreSQL is the documented target; a zero-install
**SQLite fallback** is used automatically when `DATABASE_URL` is unset.

```bash
cd backend
make setup      # venv + deps + .env  (Windows: runs under Git Bash)
make migrate    # alembic upgrade head
make seed       # import seed_data.json (idempotent)
make run        # API on http://localhost:8000  (Swagger at /docs)
```

If `make` is unavailable (Windows), run the venv python directly:

```bash
cd backend/server
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
.venv/Scripts/python.exe -m alembic upgrade head
.venv/Scripts/python.exe -m app.seed.import_seed
.venv/Scripts/python.exe -m uvicorn app.main:app --reload --port 8000
```

**Demo accounts** (seeded): staff `admin@dwellio.app` / `password`, user `demo@dwellio.app` / `password`.

### PostgreSQL (production target)

The database is **not** auto-created (only the SQLite fallback is). Create the role + database
once, then point `DATABASE_URL` at it. The driver is **psycopg v3** (binary wheels on all
Pythons, incl. 3.14) via the `postgresql+psycopg://` URL.

```bash
# 1. Create the role + database (as a Postgres superuser).
#    On Windows the tools may not be on PATH — use the full install path, e.g.:
#    "C:\Program Files\PostgreSQL\18\bin\psql.exe"
psql -U postgres -c "CREATE ROLE dwellio LOGIN PASSWORD 'dwellio';"
createdb -U postgres -O dwellio dwellio
```

```bash
# 2. server/.env
DATABASE_URL=postgresql+psycopg://dwellio:dwellio@localhost:5432/dwellio
```

```bash
# 3. Apply the schema + seed.
make migrate && make seed
```

> `psycopg[binary]` is in `requirements.txt`. To use asyncpg instead (where a wheel exists for
> your Python): `pip install asyncpg` and use `postgresql+asyncpg://…`.

---

## Run the admin (port 3001)

```bash
cd backend/admin
cp .env.example .env.local      # NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
npm install
npm run dev                      # http://localhost:3001  (or: make admin)
npm run build                    # production build (green)
```

Sign in with the staff account. Features: branded MUI theme (seed `#00696D`) with light/dark
toggle, collapsible animated sidebar, dashboard (KPI count-ups + MUI X charts), DataGrid CRUD for
listings (photo gallery + crop, agent/type/amenity selects, lat/lng), agents, property types,
amenities, tour/inquiry status management, users with a detail drawer, notification broadcasting,
and self-service profile editing.

---

## Point the Flutter app at this backend

Change **only the base URL**:

```bash
flutter run --dart-define=DWELLIO_API_BASE_URL=http://localhost:8000
```

| Target            | Base URL |
|-------------------|----------|
| Web / desktop     | `http://localhost:8000` |
| Android emulator  | `http://10.0.2.2:8000` |
| iOS simulator     | `http://localhost:8000` |
| Physical device   | `http://<your-machine-LAN-ip>:8000` |

The default in `lib/core/env/env.dart` has been set to `http://localhost:8000`.

---

## Image / media handling

- `POST /admin-api/upload` (staff-only, multipart `file`) validates the extension, stores under
  `MEDIA_ROOT/uploads/`, and returns a **relative** path `{"url": "/media/uploads/<id>.ext"}`.
- `/media` is served via `StaticFiles` in dev. Clients prepend their own base URL, so stored
  values are host-independent and any existing absolute photo URLs still work.
- **Production:** serve `/media` via a reverse proxy (nginx) or an object store (S3/GCS) and point
  `MEDIA_URL` at it.

## Seed importer

`server/app/seed/seed_data.json` was migrated from the old json-server `mock-api/db.json`. Re-import
anytime (idempotent, upserts by id in dependency order):

```bash
python -m app.seed.import_seed --path app/seed/seed_data.json
python -m app.seed.create_superuser --email admin@dwellio.app --password password
```

## API docs

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## Environment variables (`server/.env`)

| Var | Default | Notes |
|-----|---------|-------|
| `DATABASE_URL` | (unset → SQLite) | `postgresql+asyncpg://…` for Postgres |
| `SECRET_KEY` | dev value | **change in production** |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 10080 | JWT lifetime |
| `MEDIA_ROOT` / `MEDIA_URL` | `media` / `/media` | upload storage |
| `SEED_DATA_PATH` | `app/seed/seed_data.json` | importer default |
| `CORS_ORIGINS` | localhost:3001,3000 | comma-separated |

## Tests, lint

```bash
make test    # pytest (auth incl. stale-token-login, bounds/filter parity, server-side mortgage)
make lint    # ruff + black --check
make fmt     # ruff --fix + black
```

---

## Submodule wiring

`backend/` is its own git repository, ready to be a submodule. After pushing it to a remote:

```bash
# from the parent (Dwellio) repo, replacing the plain folder with a submodule:
git rm -r --cached backend && rm -rf backend
git submodule add <remote-url> backend
git commit -m "Add Dwellio backend as a submodule"
```
