<div align="center">

# Dwellio Backend

### FastAPI + PostgreSQL API · Next.js + MUI Admin

A production-quality backend for the **Dwellio** Flutter real-estate app, plus a polished
**admin dashboard**. The Flutter app works against it by **changing only its base URL** —
identical paths, query params, and JSON shapes.

![Python](https://img.shields.io/badge/Python-3.11–3.14-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-async-009688?logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-CA2C2C)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-psycopg3-336791?logo=postgresql&logoColor=white)
![Next.js](https://img.shields.io/badge/Next.js-App%20Router-000000?logo=next.js&logoColor=white)
![MUI](https://img.shields.io/badge/MUI-v6%20·%20DataGrid%20·%20Charts-007FFF?logo=mui&logoColor=white)

</div>

---

## Contents

- [Highlights](#highlights)
- [Admin screenshots](#admin-screenshots)
- [Project structure](#project-structure)
- [Contract parity](#contract-parity-why-it-matches-the-app)
- [Getting started](#getting-started)
- [Using PostgreSQL](#using-postgresql)
- [Run the admin dashboard](#run-the-admin-dashboard)
- [Connect the Flutter app](#connect-the-flutter-app)
- [API & docs](#api--docs)
- [Configuration](#configuration)
- [Media & uploads](#media--uploads)
- [Seeding](#seeding)
- [Testing & linting](#testing--linting)
- [Make targets](#make-targets)
- [Tech stack](#tech-stack)
- [Troubleshooting](#troubleshooting)
- [Submodule wiring](#submodule-wiring)

---

## Highlights

- **Drop-in for the Flutter app** — same endpoints, camelCase JSON, plain-array list responses.
- **Async all the way** — FastAPI + SQLAlchemy 2.0 (async) + Alembic, Pydantic v2.
- **Postgres or zero-install SQLite** — `DATABASE_URL` selects the engine; unset → local SQLite.
- **Geospatial search** — map-bounds + filters + Haversine distance sort, on Postgres *and* SQLite.
- **Server-side computation** — mortgage estimate, price-per-sqm, distance, and a time-based tour
  status flow are computed on the server and never trusted from the client.
- **Admin API + dashboard** — staff-only `/admin-api` powering a Next.js + MUI admin (CRUD,
  charts, image upload/crop, status management).
- **Tested & linted** — `pytest-asyncio`, `ruff` + `black`; OpenAPI/Swagger out of the box.

---

## Admin screenshots

<table>
  <tr>
    <td width="50%"><img src="screenshots/dashboard.png" alt="Dashboard — KPI cards and MUI X charts" /></td>
    <td width="50%"><img src="screenshots/listings.png" alt="Listings DataGrid with colored boolean cells" /></td>
  </tr>
  <tr>
    <td align="center"><b>Dashboard</b> — KPI count-ups + charts (over time, by type, buy/rent, avg price by city, top agents)</td>
    <td align="center"><b>Listings</b> — DataGrid with photos, deal-type chips, colored featured cells</td>
  </tr>
  <tr>
    <td><img src="screenshots/listing-edit.png" alt="Edit-listing dialog with photo gallery and selects" /></td>
    <td><img src="screenshots/agents.png" alt="Agents management table" /></td>
  </tr>
  <tr>
    <td align="center"><b>Edit listing</b> — photo gallery + crop, agent/type/amenity selects, lat/lng</td>
    <td align="center"><b>Agents</b> — CRUD with avatars, ratings and listing counts</td>
  </tr>
  <tr>
    <td colspan="2"><img src="screenshots/tours.png" alt="Tours with time-based status chips" /></td>
  </tr>
  <tr>
    <td colspan="2" align="center"><b>Tours</b> — status chips computed from <code>scheduledFor</code> (requested → confirmed → upcoming → completed)</td>
  </tr>
</table>

---

## Project structure

```
backend/
├── server/                      FastAPI application
│   ├── app/
│   │   ├── core/                config, security (JWT + bcrypt), async db,
│   │   │                        computations (mortgage/haversine/tour-status),
│   │   │                        event-loop helper
│   │   ├── models/              SQLAlchemy 2.0 models — string PKs (lst_, agt_, usr_…)
│   │   ├── schemas/             Pydantic v2 (camelCase) — public + distinct admin schemas
│   │   ├── api/
│   │   │   ├── deps.py          get_current_user / optional_user / require_staff
│   │   │   ├── serializers.py   ORM → contract-shaped responses
│   │   │   ├── listing_query.py filters + bounds + sort (reusable)
│   │   │   └── routes/          auth, listings, agents, lookups, favorites,
│   │   │                        saved_searches, tours, inquiries, notifications, admin
│   │   ├── seed/                seed_data.json + idempotent importer + superuser
│   │   └── main.py              app wiring: CORS, /media static, routers, handlers
│   ├── alembic/                 async migrations
│   ├── tests/                   pytest-asyncio (auth, bounds/filter, mortgage)
│   ├── run.py                   dev server entrypoint (Windows-safe event loop)
│   ├── requirements.txt  .env.example  pytest.ini  alembic.ini
│
├── admin/                       Next.js (App Router, TS strict) + MUI v6 + X DataGrid/Charts
├── screenshots/                 admin UI screenshots
├── Makefile  make.bat           task runner (Unix make / Windows shim)
└── scripts/  .gitignore  README.md
```

---

## Contract parity (why it matches the app)

The contract was derived from the Flutter app's `lib/data` (Retrofit client + freezed models).
The backend adapts to the app, not the reverse:

| Rule | Detail |
|------|--------|
| **String PKs** | Preserve the app's prefixed ids (`lst_…`, `agt_…`, `usr_…`). |
| **Auth shape** | `POST /auth/login` & `/auth/register` take a JSON body, return `{ token, user }`; `GET /auth/me` → `{ user }`. Login/register never apply the auth dependency, so a stale `Authorization` header can't block signing in. |
| **Plain arrays** | List endpoints return JSON arrays (manual `_page`/`_limit` paging + `X-Total-Count`). |
| **Numbers as numbers** | Price/area/rating/derived values are JSON numbers, never strings. |
| **Plain-string URLs** | Image fields are strings so relative `/media/...` upload paths round-trip. |
| **camelCase** | Everywhere, via a Pydantic `alias_generator`; camelCase query params via `Query(alias=…)`. |
| **Map-bounds search** | `GET /listings` honors `swLat,swLng,neLat,neLng` + all filters + `sort=distance` (Haversine). Plain lat/lng ranges work on Postgres **and** SQLite (PostGIS optional). |
| **Server-side math** | Mortgage (`/listings/{id}/mortgage`), price-per-sqm, distance — computed, never client-trusted. |
| **Time-based state** | Tour status (`requested → confirmed → upcoming → completed`) from `scheduledFor`; saved-search "new matches" computed live. |
| **DB-backed lookups** | `Agent`, `PropertyType`, `Amenity` are real tables with admin CRUD. |

---

## Getting started

**Prerequisites:** Python **3.11+** and Node **18+**. No Docker. PostgreSQL is the documented
target, but a **SQLite fallback** runs with zero setup when `DATABASE_URL` is unset.

```bash
cd backend
make setup      # venv + deps + copy .env
make migrate    # alembic upgrade head
make seed       # import seed_data.json (idempotent)
make run        # → http://localhost:8000  (Swagger at /docs)
```

> **On Windows**, `make` may be missing. Use the bundled **`make.bat`** (same targets:
> `make setup`, `make run`, …) or run the venv Python directly:
>
> ```bat
> cd backend\server
> python -m venv .venv
> .venv\Scripts\python.exe -m pip install -r requirements.txt
> .venv\Scripts\python.exe -m alembic upgrade head
> .venv\Scripts\python.exe -m app.seed.import_seed
> .venv\Scripts\python.exe run.py
> ```

**Seeded accounts**

| Role | Email | Password |
|------|-------|----------|
| Staff / admin | `admin@dwellio.app` | `password` |
| Regular user  | `demo@dwellio.app`  | `password` |

---

## Using PostgreSQL

The database is **not** auto-created (only the SQLite fallback is). The driver is **psycopg v3**
(`postgresql+psycopg://`), which ships binary wheels for every supported Python (incl. 3.14).

```bash
# 1. Create the role + database as a Postgres superuser.
#    Windows: the tools may not be on PATH — use the full install path, e.g.
#    "C:\Program Files\PostgreSQL\18\bin\psql.exe"
psql -U postgres -c "CREATE ROLE dwellio LOGIN PASSWORD 'dwellio';"
createdb -U postgres -O dwellio dwellio

# 2. Point the app at it — server/.env
DATABASE_URL=postgresql+psycopg://dwellio:dwellio@localhost:5432/dwellio

# 3. Apply the schema + seed.
make migrate && make seed
```

Verify:

```bash
psql -U dwellio -d dwellio -c "\dt"      # lists the 13 tables + alembic_version
```

> **Windows + Postgres note:** psycopg's async driver needs a `SelectorEventLoop` (not Windows'
> default `ProactorEventLoop`). `run.py` and the seed/migration scripts handle this automatically.
> The trade-off: **auto-reload is disabled on Windows** (the reload child can't inherit the loop
> policy) — restart manually after code changes, or use the SQLite fallback for reload-heavy dev.
>
> Prefer asyncpg? `pip install asyncpg` and use `postgresql+asyncpg://…` (needs a wheel for your Python).

---

## Run the admin dashboard

```bash
cd backend/admin
cp .env.example .env.local        # NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
npm install
npm run dev                       # → http://localhost:3001  (or: make admin)
npm run build                     # production build
```

Sign in with the **staff** account. The admin is a branded MUI app (seed `#00696D`, light/dark)
with a collapsible animated sidebar and:

- **Dashboard** — animated KPI cards + MUI X charts, backed by `/admin-api/stats`.
- **CRUD** — listings (photo gallery + crop, agent/type/amenity selects, lat/lng), agents,
  property types, amenities.
- **Operations** — tour & inquiry status management, users with a saved-searches/favorites drawer,
  notification broadcasting, self-service profile editing.

---

## Connect the Flutter app

Change **only the base URL** — every path, param and shape already matches.

```bash
flutter run --dart-define=DWELLIO_API_BASE_URL=http://localhost:8000
```

The app also reads a runtime `.env` (`flutter_dotenv`); edit it and restart, no recompile.

| Target            | Base URL |
|-------------------|----------|
| Web / desktop     | `http://localhost:8000` |
| Android emulator  | `http://10.0.2.2:8000` |
| iOS simulator     | `http://localhost:8000` |
| Physical device   | `http://<your-machine-LAN-ip>:8000` |

---

## API & docs

Interactive docs are generated from the code:

| Doc | URL |
|-----|-----|
| Swagger UI | `http://localhost:8000/docs` |
| ReDoc | `http://localhost:8000/redoc` |
| OpenAPI JSON | `http://localhost:8000/openapi.json` |

**Public** (browse): `GET /listings`, `/listings/{id}`, `/listings/{id}/similar`,
`/listings/{id}/mortgage`, `/agents/{id}`, `/property-types`, `/amenities` ·
`POST /auth/login`, `/auth/register`.

**Authenticated** (JWT): `GET /auth/me` · favorites · saved-searches · tours · inquiries ·
notifications · `POST /listings`.

**Staff** (`/admin-api`): `stats`, `upload`, CRUD for listings/agents/property-types/amenities,
tours/inquiries status, users, saved-searches, notification broadcast.

> In Swagger: `POST /auth/login` → copy the `token` → **Authorize** → `Bearer <token>`.

---

## Configuration

Settings come from `server/.env` (see `server/.env.example`):

| Variable | Default | Notes |
|----------|---------|-------|
| `DATABASE_URL` | *(unset → SQLite)* | `postgresql+psycopg://…` for Postgres |
| `SECRET_KEY` | dev value | **change in production** |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `10080` | JWT lifetime (7 days) |
| `MEDIA_ROOT` / `MEDIA_URL` | `media` / `/media` | upload storage / public prefix |
| `MAX_UPLOAD_MB` | `10` | upload size cap |
| `SEED_DATA_PATH` | `app/seed/seed_data.json` | importer default |
| `CORS_ORIGINS` | `localhost:3001,…` | comma-separated origins |

---

## Media & uploads

- `POST /admin-api/upload` (staff-only, multipart `file`) validates the extension, stores under
  `MEDIA_ROOT/uploads/`, and returns a **relative** path `{ "url": "/media/uploads/<id>.ext" }`.
- `/media` is served via `StaticFiles` in dev. Clients prepend their own base URL, so stored
  values are host-independent and existing absolute photo URLs still work.
- **Production:** serve `/media` from a reverse proxy (nginx) or object store (S3/GCS) and point
  `MEDIA_URL` at it.

---

## Seeding

`server/app/seed/seed_data.json` was migrated from the original json-server mock. The importer is
idempotent (upserts by id in dependency order) and stamps "in-progress" tours relative to *now*:

```bash
python -m app.seed.import_seed --path app/seed/seed_data.json   # or: make seed
python -m app.seed.create_superuser --email admin@dwellio.app --password password
```

---

## Testing & linting

```bash
make test    # pytest — auth (incl. stale-token login), bounds/filter parity, server-side mortgage
make lint    # ruff + black --check
make fmt     # ruff --fix + black
```

---

## Make targets

| Target | Action |
|--------|--------|
| `setup` | create venv, install deps, copy `.env` |
| `migrate` | `alembic upgrade head` |
| `seed` | import `seed_data.json` (idempotent) |
| `run` | dev server on `:8000` |
| `admin` | Next.js admin on `:3001` |
| `test` / `lint` / `fmt` | pytest / ruff+black check / ruff+black fix |
| `superuser` | create or promote a staff superuser |
| `reset` | delete the local SQLite db |

On Windows, run the same via `make.bat <target>` (or just `make <target>` if you have GNU make).

---

## Tech stack

**API:** FastAPI · Uvicorn (gunicorn in prod) · SQLAlchemy 2.0 async · Alembic · Pydantic v2 +
pydantic-settings · psycopg v3 / aiosqlite · python-jose (JWT) · bcrypt · python-multipart ·
pytest + pytest-asyncio · ruff + black.

**Admin:** Next.js (App Router, TypeScript strict) · MUI v6 + MUI X DataGrid + Charts · axios ·
@tanstack/react-query · react-hook-form + zod · framer-motion · react-easy-crop.

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `'make' is not recognized` (Windows) | Use `make.bat <target>`, or run the venv Python commands directly. |
| `ModuleNotFoundError: asyncpg` | Expected on Python 3.14 — the project uses **psycopg v3** (`postgresql+psycopg://`). |
| `database "dwellio" does not exist` | Postgres DBs aren't auto-created — see [Using PostgreSQL](#using-postgresql). |
| `MissingGreenlet … ProactorEventLoop` | Windows + psycopg async — start the server via `run.py` (handled automatically). |
| `[WinError 10048] … bind on 0.0.0.0:8000` | Port in use. PowerShell: `Get-NetTCPConnection -LocalPort 8000 -State Listen \| ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }`. |
| `SettingsError … CORS_ORIGINS` | `CORS_ORIGINS` is a plain comma-separated string in `.env` (not JSON). |

---

## Submodule wiring

`backend/` is its own git repository, ready to be a submodule of the Dwellio app repo:

```bash
# from the parent (Dwellio) repo:
git submodule add <remote-url> backend
git commit -m "Add Dwellio backend as a submodule"

# cloning the parent later:
git clone --recurse-submodules <parent-url>
# or, in an existing clone:
git submodule update --init --recursive
```
