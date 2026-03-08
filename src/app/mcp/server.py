"""MCP server exposing marine forecast tools for AI agents.

Provides tools for querying forecast data, advisory status, and zone info.
Mounted as a sub-application on the main FastAPI app at /mcp.
"""

import logging

from mcp.server.fastmcp import FastMCP

from app.models import ZONES
from app.services.cache import cache

logger = logging.getLogger(__name__)

mcp_server = FastMCP(
    name="Puget Sound Marine Forecast",
    instructions=(
        "Provides marine weather forecasts for Puget Sound and Washington coastal waters. "
        "Use get_forecast to retrieve a specific zone's forecast, list_zones to see available "
        "zones, or get_advisory_status to check for active warnings across all zones."
    ),
    streamable_http_path="/mcp",
    stateless_http=True,
)


@mcp_server.tool()
def list_zones() -> dict:
    """List all available marine forecast zones with their IDs and names."""
    return {"zones": [{"zone_id": zid, "zone_name": name} for zid, name in ZONES.items()]}


@mcp_server.tool()
def get_forecast(zone_id: str) -> dict:
    """Get the marine forecast for a specific zone.

    Args:
        zone_id: NOAA zone code (e.g., PZZ135 for Puget Sound, PZZ133 for San Juan Islands)
    """
    zone_id = zone_id.strip().upper()
    if zone_id not in ZONES:
        return {"error": f"Unknown zone: {zone_id}. Use list_zones to see available zones."}

    forecast = cache.get_forecast(zone_id)
    if forecast is None:
        error = cache.get_zone_error(zone_id)
        return {"error": f"Forecast for {zone_id} not available: {error or 'cache loading'}"}

    return forecast.model_dump(mode="json")


@mcp_server.tool()
def get_all_forecasts() -> dict:
    """Get marine forecasts for all zones at once."""
    forecasts = cache.get_all_forecasts()
    if not forecasts:
        return {"error": "Forecasts not yet available. Cache is loading."}

    return {
        "total_zones": len(ZONES),
        "successful": len(forecasts),
        "forecasts": [f.model_dump(mode="json") for f in forecasts],
    }


@mcp_server.tool()
def get_synopsis() -> dict:
    """Get the regional marine forecast synopsis for Washington waters."""
    synopsis = cache.get_synopsis()
    if synopsis is None:
        return {"error": "Synopsis not yet available. Cache is loading."}
    return synopsis


@mcp_server.tool()
def get_advisory_status() -> dict:
    """Check advisory/warning/watch status across all zones.

    Returns a summary of which zones have active or upcoming advisories.
    """
    forecasts = cache.get_all_forecasts()
    if not forecasts:
        return {"error": "Forecasts not yet available. Cache is loading."}

    active_zones = []
    upcoming_zones = []

    for f in forecasts:
        if f.has_active_advisory:
            active_zones.append(
                {
                    "zone_id": f.zone_id,
                    "zone_name": f.zone_name,
                    "advisory_text": f.advisory_text,
                }
            )
        if f.has_upcoming_advisory:
            upcoming_zones.append(
                {
                    "zone_id": f.zone_id,
                    "zone_name": f.zone_name,
                    "advisory_text": f.advisory_text,
                }
            )

    return {
        "any_active": len(active_zones) > 0,
        "any_upcoming": len(upcoming_zones) > 0,
        "active_advisories": active_zones,
        "upcoming_advisories": upcoming_zones,
        "last_updated": cache.last_updated.isoformat() if cache.last_updated else None,
    }
