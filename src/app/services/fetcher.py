"""HTTP fetcher for NOAA forecast text files."""

import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

_timeout = httpx.Timeout(
    connect=10.0,
    read=float(settings.noaa_timeout_seconds),
    write=10.0,
    pool=10.0,
)
_client = httpx.AsyncClient(timeout=_timeout, follow_redirects=True)


async def close_client() -> None:
    """Close the shared HTTP client (call on app shutdown)."""
    await _client.aclose()


async def fetch_zone_text(zone_id: str) -> str:
    """Fetch the raw forecast text for a single zone from NOAA."""
    url = f"{settings.noaa_base_url}/{zone_id.lower()}.txt"
    logger.debug("Fetching zone %s from %s", zone_id, url)
    response = await _client.get(url)
    response.raise_for_status()
    return response.text


async def fetch_synopsis_html() -> str:
    """Fetch the combined UW marine forecast HTML (used for synopsis only)."""
    logger.debug("Fetching synopsis from %s", settings.uw_synopsis_url)
    response = await _client.get(settings.uw_synopsis_url)
    response.raise_for_status()
    return response.text
