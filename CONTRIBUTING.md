# Contributing

Development setup, tooling, and project structure for working on the Puget Sound Marine Forecast.

## Prerequisites

- Python 3.12+
- Node.js 22+ and npm
- Docker (for container builds)

## Local Setup

```bash
# Clone and enter the repo
git clone https://github.com/longman391/puget-sound-marine-forecast.git
cd puget-sound-marine-forecast

# Python environment
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Frontend dependencies
cd frontend && npm install && cd ..

# Copy environment config
cp .env.example .env
```

## Running Locally

The backend and frontend run as separate dev servers. Vite proxies API requests to the backend automatically.

```bash
# Terminal 1 — API server
cd src && PYTHONPATH=. uvicorn app.main:app --reload

# Terminal 2 — Frontend dev server (with hot reload)
cd frontend && npm run dev
```

- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173` (proxies `/api` and `/mcp` to port 8000)
- API docs: `http://localhost:8000/docs`

For a production-like build where the frontend is served by FastAPI:

```bash
docker compose up --build
```

## Tests

33 tests covering auth, text parsing, and API routes. No database or network access required — all external calls are mocked.

```bash
# Run all tests
PYTHONPATH=src pytest tests/ -v

# With coverage report
PYTHONPATH=src pytest tests/ -v --cov=app --cov-report=term-missing

# Run a specific test file
PYTHONPATH=src pytest tests/test_parser.py -v
```

The coverage threshold is set to 55% in `pyproject.toml`. CI will fail if coverage drops below that.

### Test Organization

```
tests/
├── conftest.py       — Test client, sample forecast/synopsis data, path setup
├── test_auth.py      — API key validation (header, query param, disabled mode)
├── test_parser.py    — Forecast text parsing (zone names, timestamps, advisories)
└── test_routes.py    — API endpoint behavior (responses, error codes, cache states)
```

## Code Quality

Three tools, all configured in `pyproject.toml`:

```bash
# Lint
ruff check src/ tests/

# Auto-fix lint issues
ruff check --fix src/ tests/

# Format
ruff format src/ tests/

# Type check
mypy src/ --ignore-missing-imports
```

### Style Rules

- **Line length**: 100 characters
- **Target**: Python 3.12
- **Ruff rules**: `E`, `F`, `I`, `N`, `W`, `UP` (pycodestyle, pyflakes, isort, pep8-naming, warnings, pyupgrade)
- **Quotes**: Double quotes
- **Imports**: Sorted by Ruff's isort integration; use `from app.xxx import ...` style

## Project Structure

```
src/app/
├── main.py              — FastAPI app, lifespan events, middleware, SPA serving
├── config.py            — Pydantic settings from environment variables
├── models.py            — Response models and ZONES registry (14 zones)
├── auth.py              — API key dependency (header or query param)
├── routes/
│   ├── health.py        — GET /health, /status (unauthenticated)
│   ├── forecast.py      — GET /zones, /forecast, /forecast/{zone_id}, /synopsis
│   └── admin.py         — POST /cache/refresh, GET /settings
├── services/
│   ├── fetcher.py       — Async HTTP client for NOAA and UW data sources
│   ├── parser.py        — Text extraction (zone names, timestamps, advisories)
│   └── cache.py         — In-memory cache with background refresh loop
└── mcp/
    └── server.py        — MCP server (FastMCP, stateless HTTP, 5 tools)

frontend/src/
├── main.tsx             — Entry point, router setup
├── App.tsx              — Route definitions, navigation bar, toast config
├── pages/
│   ├── Dashboard.tsx    — Zone cards grid with pinning, drag-and-drop, auto-refresh
│   ├── ZoneDetail.tsx   — Full forecast view for a single zone
│   └── Settings.tsx     — Cache status, server config, API key management
├── components/
│   ├── ZoneCard.tsx     — Forecast card with advisory badges, pin/drag controls
│   ├── AdvisoryBadges.tsx
│   ├── SkeletonCards.tsx
│   └── FailedZoneCard.tsx
├── hooks/
│   └── useLocalSettings.ts — localStorage-backed settings with debounced save
├── utils/
│   ├── api.ts           — API client with types and auth header injection
│   ├── zones.ts         — Zone region grouping (Salish Sea vs. Coastal)
│   └── time.ts          — Time formatting (relative and absolute)
└── index.css            — Full CSS theme (dark, CSS variables, responsive)
```

## Key Architecture Details

- **No database.** All state lives in an in-memory `ForecastCache` singleton. A restart re-fetches everything from NOAA.
- **Stale-while-revalidate.** If a zone fetch fails during refresh, the previously cached data is retained rather than cleared.
- **Concurrent fetching.** All 14 zones are fetched in parallel via `asyncio.gather()`.
- **Advisory detection.** Uses triple-dot banner markers (`...ADVISORY...`) from NOAA text. Distinguishes active from upcoming based on keyword heuristics (FROM, BEGINNING, EXPECTED, etc.).
- **Forecast text is verbatim.** No regex decomposition of wind, waves, or weather. The full NOAA text is passed through to consumers.
- **Frontend served by FastAPI.** In production, the built React app is served from `frontend/dist/` by FastAPI's static file mounting, with a catch-all route for client-side routing.

## CI

GitHub Actions runs on every push to `main`/`dev` and on PRs to `main`:

1. Ruff lint and format check
2. mypy type check
3. pytest with coverage
4. Docker image build (on `main`/`dev` only)

Matrix: Python 3.12 and 3.13.

The publish workflow (`publish.yml`) builds multi-platform Docker images on version tags and pushes to GHCR.
