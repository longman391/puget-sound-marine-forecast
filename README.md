# Puget Sound Marine Forecast

A containerized service that fetches and serves marine forecast data for Puget Sound from NOAA. Provides a REST API, MCP server for AI agents, and a web dashboard.

## Quick Start

### Docker (recommended)
```bash
docker compose up --build
```

The API will be available at `http://localhost:8000/api/v1/`.

### Local Development
```bash
# Set up Python environment
python -m venv .venv && source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Start the API server
cd src && python -m uvicorn app.main:app --reload
```

### Usage
- **API Docs:** http://localhost:8000/docs
- **All Zones:** http://localhost:8000/api/v1/zones
- **Puget Sound Forecast:** http://localhost:8000/api/v1/forecast/PZZ135
- **All Forecasts:** http://localhost:8000/api/v1/forecast
- **Synopsis:** http://localhost:8000/api/v1/synopsis
- **Health Check:** http://localhost:8000/api/v1/health

## About

The University of Washington does an excellent job of providing accurate and timely marine forecasts for Washington State waters. Unfortunately, those forecasts are provided only as unstructured text, making them difficult to consume programmatically.

This service fetches the raw forecast text per-zone, extracts advisory/warning status, and serves it via a clean JSON API — making it easy for Home Assistant, Dakboard, AI agents (via MCP), and other tools to access marine conditions.

## Features

- **REST API** with per-zone and all-zone forecast endpoints
- **Advisory detection** — boolean flags for active and upcoming warnings/advisories/watches
- **MCP server** for AI agent integration (SSE transport, togglable)
- **Hourly caching** with background refresh (configurable interval)
- **API key auth** compatible with Home Assistant, Dakboard, and MCP clients
- **Docker-first** — runs on Unraid, any Docker host, or cloud
- **Web dashboard** for checking forecasts and monitoring server health

## Supported Zones

All 14 NOAA marine forecast zones for Washington:

| Zone | Area |
|------|------|
| PZZ100 | Synopsis |
| PZZ110 | Grays Harbor Bar |
| PZZ130-132 | Strait of Juan de Fuca (West/Central/East) |
| **PZZ133** | **Northern Inland Waters / San Juan Islands** |
| PZZ134 | Admiralty Inlet |
| **PZZ135** | **Puget Sound and Hood Canal** |
| PZZ150-156 | Coastal Waters (0-10 nm) |
| PZZ170-176 | Coastal Waters (10-60 nm) |

## Configuration

All settings via environment variables (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `API_KEY` | _(empty)_ | API key; if empty, auth is disabled |
| `CACHE_INTERVAL_MINUTES` | `60` | Forecast refresh interval |
| `ALLOWED_ORIGINS` | `*` | CORS origins (comma-separated) |
| `MCP_ENABLED` | `true` | Enable MCP server endpoint |
| `LOG_LEVEL` | `INFO` | Logging level |
| `TZ` | `America/Los_Angeles` | Timezone |

## Development

```bash
# Run tests
PYTHONPATH=src pytest tests/ -v

# Lint & format
ruff check src/ tests/
black src/ tests/

# Type check
mypy src/ --ignore-missing-imports
```

## Data Source

- [NOAA NWS Seattle](https://www.weather.gov/sew/) via per-zone text files
- [UW Atmospheric Sciences](https://a.atmos.washington.edu/data/marine_report.html) for regional synopsis

## License

MIT License — see [LICENSE](LICENSE) file.
