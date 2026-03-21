"""Health and status endpoints."""

from datetime import UTC, datetime

from fastapi import APIRouter

from app.config import settings
from app.models import ZONES, CacheStatus, HealthResponse
from app.services.cache import cache

router = APIRouter(prefix="/api/v1", tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint — always unauthenticated."""
    status_str = "healthy" if cache.is_ready else "unhealthy"
    return HealthResponse(status=status_str, timestamp=datetime.now(tz=UTC))


@router.get("/status", response_model=CacheStatus)
async def cache_status() -> CacheStatus:
    """Detailed cache health and statistics."""
    total = len(ZONES)
    if total == 0:
        health = "unhealthy"
    elif cache.zones_cached >= total * 0.8:
        health = "healthy"
    else:
        health = "degraded"

    return CacheStatus(
        last_updated=cache.last_updated,
        next_update=cache.next_update,
        update_interval_minutes=settings.cache_interval_minutes,
        total_updates=cache.total_updates,
        last_update_duration_seconds=cache.last_duration,
        zones_cached=cache.zones_cached,
        zones_failed=cache.zones_failed,
        health=health,
    )
