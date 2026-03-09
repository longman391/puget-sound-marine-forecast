"""Forecast and zone endpoints."""

import re

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth import require_api_key
from app.models import (
    ZONES,
    AllForecastsResponse,
    SynopsisResponse,
    ZoneForecast,
    ZoneInfo,
)
from app.services.cache import cache

router = APIRouter(prefix="/api/v1", tags=["forecast"], dependencies=[Depends(require_api_key)])

_ZONE_PATTERN = re.compile(r"^PZZ\d{3}$", re.IGNORECASE)


def _validate_zone(zone_id: str) -> str:
    """Validate and normalize a zone identifier. Returns uppercase zone ID."""
    zone_id = zone_id.strip().upper()
    if not _ZONE_PATTERN.match(zone_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid zone format: '{zone_id}'. Expected format: PZZ### (e.g., PZZ135)",
        )
    if zone_id not in ZONES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Zone {zone_id} not found. Available zones: {list(ZONES.keys())}",
        )
    return zone_id


@router.get("/zones", response_model=list[ZoneInfo])
async def list_zones() -> list[ZoneInfo]:
    """List all available forecast zones."""
    return [ZoneInfo(zone_id=zid, zone_name=name) for zid, name in ZONES.items()]


@router.get("/forecast/{zone_id}", response_model=ZoneForecast)
async def get_forecast(zone_id: str) -> ZoneForecast:
    """Get the forecast for a specific zone."""
    zone_id = _validate_zone(zone_id)

    forecast = cache.get_forecast(zone_id)
    if forecast is None:
        error = cache.get_zone_error(zone_id)
        if error:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Forecast for {zone_id} currently unavailable: {error}",
            )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Forecast for {zone_id} not yet available. Cache is loading.",
        )

    return forecast


@router.get("/forecast", response_model=AllForecastsResponse)
async def get_all_forecasts() -> AllForecastsResponse:
    """Get forecasts for all zones."""
    forecasts = cache.get_all_forecasts()
    if not forecasts and not cache.is_ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Forecasts not yet available. Cache is loading.",
        )

    errors = []
    for zone_id in ZONES:
        err = cache.get_zone_error(zone_id)
        if err:
            errors.append({"zone_id": zone_id, "error": err})

    return AllForecastsResponse(
        total_zones=len(ZONES),
        successful=len(forecasts),
        failed=len(errors),
        forecasts=forecasts,
        errors=errors or None,
        cache_last_updated=cache.last_updated,
        cache_next_update=cache.next_update,
    )


@router.get("/synopsis", response_model=SynopsisResponse)
async def get_synopsis() -> SynopsisResponse:
    """Get the regional forecast synopsis."""
    synopsis = cache.get_synopsis()
    if synopsis is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Synopsis not yet available. Cache is loading.",
        )
    return synopsis
