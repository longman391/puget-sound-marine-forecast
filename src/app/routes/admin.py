"""Admin endpoints — cache refresh, settings."""

from fastapi import APIRouter, Depends

from app.auth import require_api_key
from app.config import settings
from app.services.cache import cache

router = APIRouter(
    prefix="/api/v1",
    tags=["admin"],
    dependencies=[Depends(require_api_key)],
)


@router.post("/cache/refresh")
async def refresh_cache() -> dict:
    """Manually trigger a cache refresh."""
    await cache.refresh()
    return {
        "message": "Cache refresh completed",
        "last_updated": cache.last_updated.isoformat() if cache.last_updated else None,
        "zones_cached": cache.zones_cached,
        "zones_failed": cache.zones_failed,
    }


@router.get("/settings")
async def get_settings() -> dict:
    """Get current server settings (non-sensitive)."""
    return {
        "cache_interval_minutes": settings.cache_interval_minutes,
        "auth_enabled": settings.auth_enabled,
        "mcp_enabled": settings.mcp_enabled,
        "allowed_origins": settings.cors_origins,
        "log_level": settings.log_level,
        "noaa_base_url": settings.noaa_base_url,
        "uw_synopsis_url": settings.uw_synopsis_url,
    }
