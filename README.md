# Puget Sound Marine Forecast

A self-hosted service that fetches NOAA marine forecast text for 14 Washington State coastal and inland zones, extracts advisory status, and serves it all through a JSON API. Includes a dark-themed React dashboard and an optional MCP server for AI agent integration.

Built for Docker. Designed for Unraid home servers, but runs anywhere containers run.

## Quick Start

### Docker

```bash
docker compose up --build
```

Open `http://localhost:8000` for the web dashboard, or `http://localhost:8000/docs` for the interactive API docs.

### Local Development

Backend and frontend run on separate dev servers with a Vite proxy bridging them.

```bash
# Python environment
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Start the API server (terminal 1)
cd src && PYTHONPATH=. uvicorn app.main:app --reload

# Start the frontend dev server (terminal 2)
cd frontend && npm install && npm run dev
```

The frontend dev server (default `http://localhost:5173`) proxies `/api` and `/mcp` requests to the backend on port 8000.

## API

All endpoints are under `/api/v1/`. Authentication is required for forecast and admin endpoints when `API_KEY` is set (see [Configuration](#configuration)). Health endpoints are always public.

Pass the API key via `X-API-Key` header or `?api_key=` query parameter.

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/health` | No | Returns `healthy` or `unhealthy` based on cache state |
| GET | `/status` | No | Cache stats: zones cached/failed, update times, health |
| GET | `/zones` | Yes | List all 14 zone IDs and names |
| GET | `/forecast` | Yes | All zone forecasts (503 if cache not ready) |
| GET | `/forecast/{zone_id}` | Yes | Single zone forecast (e.g., `/forecast/PZZ135`) |
| GET | `/synopsis` | Yes | Regional marine synopsis from UW Atmospheric Sciences |
| GET | `/settings` | Yes | Non-sensitive server configuration |
| POST | `/cache/refresh` | Yes | Manually trigger a cache refresh |

### Forecast Response

Each zone forecast includes:

```json
{
  "zone_id": "PZZ135",
  "zone_name": "Puget Sound and Hood Canal",
  "issued": "2025-03-08T03:10:00",
  "expires": "2025-03-08T15:00:00",
  "forecast_text": "...full NOAA forecast text, verbatim...",
  "has_active_advisory": true,
  "has_upcoming_advisory": false,
  "advisory_text": "SMALL CRAFT ADVISORY IN EFFECT...",
  "fetched_at": "2025-03-08T04:00:00"
}
```

The forecast text is returned verbatim from NOAA. No parsing of wind speeds, wave heights, or weather conditions is attempted — that is left to the consumer.

## Web Dashboard

Three pages, served from the same port as the API:

- **Dashboard** — Zone forecast cards in a responsive grid. Cards show advisory status badges (active, upcoming, or clear) and a forecast text preview. Zones can be pinned and reordered via drag-and-drop; preferences persist in localStorage.
- **Zone Detail** — Full forecast text, advisory details, and timestamps for a single zone.
- **Settings** — Cache status, server health, and configurable options (API key, log level, etc.).

Dark theme. No framework — custom CSS with CSS variables. Designed for readability on wall-mounted displays (Dakboard, etc.) as well as desktop and mobile browsers.

## MCP Server

When `MCP_ENABLED=true` (the default), a [Model Context Protocol](https://modelcontextprotocol.io/) server is available at `/mcp` for AI agent integration. Uses stateless HTTP transport.

Exposed tools:

| Tool | Description |
|------|-------------|
| `list_zones()` | All 14 zone IDs and names |
| `get_forecast(zone_id)` | Forecast for a single zone |
| `get_all_forecasts()` | All zone forecasts |
| `get_synopsis()` | Regional marine synopsis |
| `get_advisory_status()` | Advisory summary across all zones |

The MCP server reads from the same in-memory cache as the REST API. No separate data path.

## Supported Zones

All 14 NOAA marine forecast zones for the Washington coast and inland waters:

| Zone | Area |
|------|------|
| PZZ100 | Synopsis — Northern and Central Washington Coastal and Inland Waters |
| PZZ110 | Grays Harbor Bar |
| PZZ130 | West Entrance U.S. Waters Strait of Juan de Fuca |
| PZZ131 | Central U.S. Waters Strait of Juan de Fuca |
| PZZ132 | East Entrance U.S. Waters Strait of Juan de Fuca |
| PZZ133 | Northern Inland Waters Including the San Juan Islands |
| PZZ134 | Admiralty Inlet |
| PZZ135 | Puget Sound and Hood Canal |
| PZZ150 | Coastal Waters — Cape Flattery to James Island (0-10 nm) |
| PZZ153 | Coastal Waters — James Island to Point Grenville (0-10 nm) |
| PZZ156 | Coastal Waters — Point Grenville to Cape Shoalwater (0-10 nm) |
| PZZ170 | Coastal Waters — Cape Flattery to James Island (10-60 nm) |
| PZZ173 | Coastal Waters — James Island to Point Grenville (10-60 nm) |
| PZZ176 | Coastal Waters — Point Grenville to Cape Shoalwater (10-60 nm) |

The dashboard groups these into Salish Sea (PZZ100-PZZ135) and Coastal (PZZ150+) regions.

## Configuration

All settings are via environment variables. Copy `.env.example` to `.env` and edit as needed.

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST` | `0.0.0.0` | Server bind address |
| `PORT` | `8000` | Server port |
| `API_KEY` | _(empty)_ | API key for auth. If empty, auth is disabled entirely. |
| `CACHE_INTERVAL_MINUTES` | `60` | How often to re-fetch forecasts from NOAA (minutes) |
| `ALLOWED_ORIGINS` | `*` | CORS allowed origins (comma-separated, or `*` for all) |
| `MCP_ENABLED` | `true` | Enable the MCP server endpoint at `/mcp` |
| `LOG_LEVEL` | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `TZ` | `America/Los_Angeles` | Timezone for display |
| `NOAA_BASE_URL` | _(NOAA default)_ | Override for testing only |
| `UW_SYNOPSIS_URL` | _(UW default)_ | Override for testing only |
| `NOAA_TIMEOUT_SECONDS` | `30` | HTTP timeout for NOAA requests |

## How It Works

1. On startup, all 14 zones are fetched concurrently from NOAA text files.
2. Each zone's raw text is parsed to extract the zone name, issued/expires timestamps, advisory banners, and the full forecast body.
3. Parsed results are stored in an in-memory cache (no database).
4. A background task re-fetches all zones on a configurable interval (default: 60 minutes). On fetch failure, previously cached data is retained (stale-while-revalidate). On repeated errors, the refresh loop backs off to 5-minute retries.
5. All API and MCP requests are served from cache. No live fetches happen on request.

## Data Sources

- **Zone forecasts**: [NOAA NWS](https://tgftp.nws.noaa.gov/data/forecasts/marine/coastal/pz/) — per-zone plain text files
- **Regional synopsis**: [UW Atmospheric Sciences](https://a.atmos.washington.edu/data/marine_report.html) — HTML page, parsed for the PZZ100 synopsis block

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for local setup, testing, linting, and project structure details.

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for Docker, Unraid, remote access, and client integration examples.

## License

MIT — see [LICENSE](LICENSE).
