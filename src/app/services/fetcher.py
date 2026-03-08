"""HTTP fetcher for NOAA forecast text files."""

import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


async def fetch_zone_text(zone_id: str) -> str:
    """Fetch the raw forecast text for a single zone from NOAA.

    Args:
        zone_id: Zone code like 'PZZ135' (case-insensitive).

    Returns:
        Raw text content of the forecast file.

    Raises:
        httpx.HTTPError: On network or HTTP errors.
    """
    url = f"{settings.noaa_base_url}/{zone_id.lower()}.txt"
    timeout = httpx.Timeout(
        connect=10.0,
        read=float(settings.noaa_timeout_seconds),
        write=10.0,
        pool=10.0,
    )

    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        logger.debug("Fetching zone %s from %s", zone_id, url)
        response = await client.get(url)
        response.raise_for_status()
        return response.text


async def fetch_synopsis_html() -> str:
    """Fetch the combined UW marine forecast HTML (used for synopsis only).

    Returns:
        Raw HTML content of the UW marine report page.

    Raises:
        httpx.HTTPError: On network or HTTP errors.
    """
    timeout = httpx.Timeout(
        connect=10.0,
        read=float(settings.noaa_timeout_seconds),
        write=10.0,
        pool=10.0,
    )

    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        logger.debug("Fetching synopsis from %s", settings.uw_synopsis_url)
        response = await client.get(settings.uw_synopsis_url)
        response.raise_for_status()
        return response.text
