# Copilot Instructions — Puget Sound Marine Forecast

## Architecture

FastAPI application that fetches NOAA marine forecast text files per-zone, extracts metadata and advisory banners, and serves the forecast text as-is (no regex decomposition of wind/waves/weather) via a JSON REST API. The app also serves a React web UI and exposes an MCP server for agent integration.

### Source layout

```
src/app/
├── main.py          — FastAPI app factory, lifespan, middleware
├── config.py        — Pydantic settings (env vars)
├── models.py        — Pydantic response models + ZONES registry
├── auth.py          — API key auth dependency
├── routes/
│   ├── forecast.py  — /api/v1/forecast, /api/v1/zones, /api/v1/synopsis
│   ├── admin.py     — /api/v1/cache/refresh, settings
│   └── health.py    — /api/v1/health, /api/v1/status
├── services/
│   ├── fetcher.py   — HTTP fetcher for NOAA text files
│   ├── parser.py    — Lightweight text parser (headers, advisories)
│   └── cache.py     — In-memory cache with TTL + background refresh
└── mcp/
    └── server.py    — MCP server (SSE transport, togglable)
```

### Data flow

1. On startup (`lifespan`), all 14 NOAA zones are fetched concurrently from per-zone text files
2. Raw text is lightly parsed: extract zone name, timestamps, advisory banners, and forecast text blob
3. Parsed results are stored in an in-memory `ForecastCache` singleton
4. A background `asyncio` task re-fetches all zones every 60 minutes (configurable, 5-min backoff on error)
5. Stale-while-revalidate: failed zones retain previous cached data
6. All `/api/v1/forecast/` endpoints serve from cache — no live fetches on request

### Key data model

```python
class ZoneForecast(BaseModel):
    zone_id: str           # e.g. "PZZ135"
    zone_name: str         # e.g. "Puget Sound and Hood Canal"
    issued: datetime | None
    expires: datetime | None
    forecast_text: str     # Full forecast text blob — verbatim from NOAA
    has_active_advisory: bool
    has_upcoming_advisory: bool
    advisory_text: str | None
    fetched_at: datetime
```

### Zone identifiers

All 14 zones follow the pattern `PZZ\d{3}` (e.g., `PZZ133`, `PZZ135`). The `ZONES` dict in `models.py` is the authoritative mapping. Zone input is validated and uppercased in route handlers.

## Commands

```bash
# Run the API server locally
cd src && python -m uvicorn app.main:app --reload

# Run all tests (from repo root)
PYTHONPATH=src pytest tests/ -v

# Code formatting
black src/ tests/

# Linting
ruff check src/ tests/
ruff check --fix src/ tests/

# Type checking
mypy src/ --ignore-missing-imports

# Docker
docker compose up --build
```

## Code Style

- **Formatter**: Black, 100-char line length, target Python 3.12
- **Linter**: Ruff with rules `E, F, I, N, W, UP`
- **Type checker**: mypy (configured in `pyproject.toml`)
- **Imports**: sorted by Ruff (`I` rule); use `from app.xxx import ...` (package-style imports)

## Conventions

- API routes are versioned under `/api/v1/`
- API key auth via `X-API-Key` header or `?api_key=` query param; disabled if `API_KEY` env var is empty
- Health endpoint (`/api/v1/health`) is always unauthenticated
- Error responses use FastAPI's `HTTPException` and never leak internal details
- The fetcher uses `httpx.AsyncClient` with explicit timeouts
- Advisory detection uses simple string matching on structured `...BANNER...` text (not forecast prose)
- Forecast prose is returned verbatim — no regex parsing of wind/waves/weather

## Dependencies

- **Production** (`pyproject.toml`): fastapi, uvicorn, httpx, pydantic, pydantic-settings, python-dateutil
- **Dev**: adds pytest, pytest-asyncio, pytest-cov, respx, black, ruff, mypy
- No database — all state is in-memory

## Deployment

Docker container with `docker-compose.yml`. Targets Unraid servers and other self-hosted Docker environments.
