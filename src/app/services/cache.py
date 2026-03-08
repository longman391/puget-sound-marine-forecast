"""In-memory forecast cache with background refresh."""

import asyncio
import logging
from datetime import datetime, timedelta

from app.config import settings
from app.models import ZONES, ZoneForecast
from app.services.fetcher import fetch_synopsis_html, fetch_zone_text
from app.services.parser import parse_synopsis, parse_zone_forecast

logger = logging.getLogger(__name__)


class ForecastCache:
    """Thread-safe in-memory cache for zone forecasts and synopsis.

    Refreshes all forecasts concurrently on a configurable interval.
    Uses stale-while-revalidate: if a refresh fails, the previous
    cached data is retained rather than cleared.
    """

    def __init__(self) -> None:
        self._forecasts: dict[str, ZoneForecast] = {}
        self._synopsis: dict | None = None
        self._errors: dict[str, str] = {}
        self._last_updated: datetime | None = None
        self._next_update: datetime | None = None
        self._total_updates: int = 0
        self._last_duration: float | None = None
        self._task: asyncio.Task | None = None

    # --- Public read API ---

    def get_forecast(self, zone_id: str) -> ZoneForecast | None:
        return self._forecasts.get(zone_id.upper())

    def get_all_forecasts(self) -> list[ZoneForecast]:
        return list(self._forecasts.values())

    def get_synopsis(self) -> dict | None:
        return self._synopsis

    def get_zone_error(self, zone_id: str) -> str | None:
        return self._errors.get(zone_id.upper())

    @property
    def last_updated(self) -> datetime | None:
        return self._last_updated

    @property
    def next_update(self) -> datetime | None:
        return self._next_update

    @property
    def total_updates(self) -> int:
        return self._total_updates

    @property
    def last_duration(self) -> float | None:
        return self._last_duration

    @property
    def zones_cached(self) -> int:
        return len(self._forecasts)

    @property
    def zones_failed(self) -> int:
        return len(self._errors)

    @property
    def is_ready(self) -> bool:
        return self._last_updated is not None and len(self._forecasts) > 0

    # --- Refresh logic ---

    async def refresh(self) -> None:
        """Fetch and cache all zone forecasts and synopsis."""
        start = datetime.now()
        logger.info("Starting forecast cache refresh...")

        new_forecasts: dict[str, ZoneForecast] = {}
        new_errors: dict[str, str] = {}

        # Fetch all zones concurrently
        tasks = {zone_id: fetch_zone_text(zone_id) for zone_id in ZONES}
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)

        fetched_at = datetime.now()
        for zone_id, result in zip(tasks.keys(), results):
            if isinstance(result, Exception):
                error_msg = f"{type(result).__name__}: {result}"
                logger.warning("Failed to fetch zone %s: %s", zone_id, error_msg)
                new_errors[zone_id] = error_msg
                continue

            try:
                parsed = parse_zone_forecast(result, zone_id, fetched_at)
                new_forecasts[zone_id] = ZoneForecast(**parsed)
            except Exception as e:
                error_msg = f"Parse error: {e}"
                logger.warning("Failed to parse zone %s: %s", zone_id, error_msg)
                new_errors[zone_id] = error_msg

        # Update cache (stale-while-revalidate: only replace zones that succeeded)
        for zone_id, forecast in new_forecasts.items():
            self._forecasts[zone_id] = forecast

        # Clear errors for zones that succeeded this time, keep errors for new failures
        for zone_id in new_forecasts:
            self._errors.pop(zone_id, None)
        for zone_id, error in new_errors.items():
            self._errors[zone_id] = error

        # Fetch synopsis (non-critical; don't fail the whole refresh)
        try:
            html = await fetch_synopsis_html()
            self._synopsis = parse_synopsis(html, fetched_at)
        except Exception as e:
            logger.warning("Failed to fetch synopsis: %s", e)

        end = datetime.now()
        duration = (end - start).total_seconds()

        self._last_updated = end
        self._next_update = end + timedelta(minutes=settings.cache_interval_minutes)
        self._total_updates += 1
        self._last_duration = duration

        logger.info(
            "Cache refresh complete: %d ok, %d failed, %.2fs",
            len(new_forecasts),
            len(new_errors),
            duration,
        )

    # --- Background task ---

    async def start_background_refresh(self) -> None:
        """Start the periodic background refresh task."""
        # Do the initial fetch
        await self.refresh()
        # Schedule periodic refreshes
        self._task = asyncio.create_task(self._refresh_loop())
        logger.info(
            "Background refresh started (every %d minutes)",
            settings.cache_interval_minutes,
        )

    async def stop_background_refresh(self) -> None:
        """Cancel the background refresh task."""
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
            logger.info("Background refresh stopped")

    async def _refresh_loop(self) -> None:
        """Periodically refresh the cache."""
        while True:
            try:
                await asyncio.sleep(settings.cache_interval_minutes * 60)
                await self.refresh()
            except asyncio.CancelledError:
                raise
            except Exception as e:
                logger.error("Error in background refresh: %s", e, exc_info=True)
                # Back off 5 minutes on error
                await asyncio.sleep(5 * 60)


# Module-level singleton
cache = ForecastCache()
