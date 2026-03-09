"""Pydantic response models for the forecast API."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app import __version__

# --- Zone registry ---

ZONES: dict[str, str] = {
    "PZZ100": "Synopsis for Northern and Central Washington Coastal and Inland Waters",
    "PZZ110": "Grays Harbor Bar",
    "PZZ130": "West Entrance U.S. Waters Strait Of Juan De Fuca",
    "PZZ131": "Central U.S. Waters Strait Of Juan De Fuca",
    "PZZ132": "East Entrance U.S. Waters Strait Of Juan De Fuca",
    "PZZ133": "Northern Inland Waters Including The San Juan Islands",
    "PZZ134": "Admiralty Inlet",
    "PZZ135": "Puget Sound and Hood Canal",
    "PZZ150": "Coastal Waters From Cape Flattery To James Island Out 10 Nm",
    "PZZ153": "Coastal Waters From James Island To Point Grenville Out 10 Nm",
    "PZZ156": "Coastal Waters From Point Grenville To Cape Shoalwater Out 10 Nm",
    "PZZ170": "Coastal Waters From Cape Flattery To James Island 10 To 60 Nm",
    "PZZ173": "Coastal Waters From James Island To Point Grenville 10 To 60 Nm",
    "PZZ176": "Coastal Waters From Point Grenville To Cape Shoalwater 10 To 60 Nm",
}


# --- Response models ---


class ZoneInfo(BaseModel):
    """A forecast zone identifier and name."""

    zone_id: str = Field(examples=["PZZ135"])
    zone_name: str = Field(examples=["Puget Sound and Hood Canal"])


class ZoneForecast(BaseModel):
    """Complete forecast data for a single zone."""

    zone_id: str = Field(examples=["PZZ135"])
    zone_name: str = Field(examples=["Puget Sound and Hood Canal"])
    issued: datetime | None = Field(default=None, description="When the forecast was issued by NWS")
    expires: datetime | None = Field(default=None, description="When the forecast expires")
    forecast_text: str = Field(description="Full forecast text blob (all periods, verbatim)")
    has_active_advisory: bool = Field(
        default=False, description="True if a warning/advisory/watch is currently in effect"
    )
    has_upcoming_advisory: bool = Field(
        default=False,
        description="True if a warning/advisory/watch is expected in the future",
    )
    advisory_text: str | None = Field(
        default=None, description="Raw advisory/warning/watch banner text, or null if none"
    )
    fetched_at: datetime = Field(description="When the server last fetched this forecast")


class AllForecastsResponse(BaseModel):
    """Response containing forecasts for all zones."""

    total_zones: int
    successful: int
    failed: int
    forecasts: list[ZoneForecast]
    errors: list[dict] | None = None
    cache_last_updated: datetime | None = None
    cache_next_update: datetime | None = None


class SynopsisResponse(BaseModel):
    """Regional forecast synopsis."""

    synopsis_text: str
    issued: datetime | None = None
    fetched_at: datetime


class CacheStatus(BaseModel):
    """Cache health and statistics."""

    last_updated: datetime | None = None
    next_update: datetime | None = None
    update_interval_minutes: int
    total_updates: int
    last_update_duration_seconds: float | None = None
    zones_cached: int
    zones_failed: int
    health: str = Field(description="'healthy', 'degraded', or 'unhealthy'")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    timestamp: datetime
    version: str = __version__


class ServerSettingsResponse(BaseModel):
    """Non-sensitive server settings."""

    cache_interval_minutes: int
    auth_enabled: bool
    mcp_enabled: bool
    allowed_origins: list[str]
    log_level: str
    noaa_base_url: str
    uw_synopsis_url: str
