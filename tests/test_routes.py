"""Tests for API route handlers."""

from datetime import datetime
from unittest.mock import patch

import pytest

from app.models import ZoneForecast
from app.services.cache import cache


@pytest.fixture(autouse=True)
def reset_cache():
    """Reset the cache singleton between tests."""
    cache._forecasts.clear()
    cache._errors.clear()
    cache._synopsis = None
    cache._last_updated = None
    cache._next_update = None
    cache._total_updates = 0
    cache._last_duration = None
    yield
    cache._forecasts.clear()
    cache._errors.clear()


def _make_forecast(zone_id: str = "PZZ135", **kwargs) -> ZoneForecast:
    """Helper to create a ZoneForecast with defaults."""
    defaults = {
        "zone_id": zone_id,
        "zone_name": "Puget Sound and Hood Canal",
        "issued": datetime(2026, 3, 8, 10, 10),
        "expires": datetime(2026, 3, 8, 23, 15),
        "forecast_text": ".TODAY...SW wind 10 to 15 kt. Waves around 2 ft or less.",
        "has_active_advisory": False,
        "has_upcoming_advisory": False,
        "advisory_text": None,
        "fetched_at": datetime.now(),
    }
    defaults.update(kwargs)
    return ZoneForecast(**defaults)


class TestHealthEndpoint:
    def test_health_unhealthy_when_cache_empty(self, client):
        resp = client.get("/api/v1/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "unhealthy"

    def test_health_healthy_when_cache_populated(self, client):
        cache._forecasts["PZZ135"] = _make_forecast()
        cache._last_updated = datetime.now()
        resp = client.get("/api/v1/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"


class TestZonesEndpoint:
    def test_list_zones(self, client):
        resp = client.get("/api/v1/zones")
        assert resp.status_code == 200
        zones = resp.json()
        assert len(zones) == 14
        zone_ids = [z["zone_id"] for z in zones]
        assert "PZZ135" in zone_ids
        assert "PZZ133" in zone_ids


class TestForecastEndpoint:
    def test_get_forecast_success(self, client):
        cache._forecasts["PZZ135"] = _make_forecast()
        cache._last_updated = datetime.now()
        resp = client.get("/api/v1/forecast/pzz135")
        assert resp.status_code == 200
        data = resp.json()
        assert data["zone_id"] == "PZZ135"
        assert ".TODAY..." in data["forecast_text"]

    def test_get_forecast_invalid_zone_format(self, client):
        resp = client.get("/api/v1/forecast/invalid")
        assert resp.status_code == 400

    def test_get_forecast_unknown_zone(self, client):
        resp = client.get("/api/v1/forecast/PZZ999")
        assert resp.status_code == 404

    def test_get_forecast_not_yet_cached(self, client):
        resp = client.get("/api/v1/forecast/PZZ135")
        assert resp.status_code == 503

    def test_get_forecast_with_error(self, client):
        cache._errors["PZZ135"] = "Timeout"
        resp = client.get("/api/v1/forecast/PZZ135")
        assert resp.status_code == 503
        assert "Timeout" in resp.json()["detail"]


class TestAllForecastsEndpoint:
    def test_get_all_forecasts(self, client):
        cache._forecasts["PZZ135"] = _make_forecast()
        cache._last_updated = datetime.now()
        resp = client.get("/api/v1/forecast")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_zones"] == 14
        assert data["successful"] == 1

    def test_all_forecasts_503_when_empty(self, client):
        resp = client.get("/api/v1/forecast")
        assert resp.status_code == 503


class TestSynopsisEndpoint:
    def test_get_synopsis(self, client):
        cache._synopsis = {
            "synopsis_text": "A front will cross the waters...",
            "issued": datetime(2026, 3, 8, 10, 10),
            "fetched_at": datetime.now(),
        }
        resp = client.get("/api/v1/synopsis")
        assert resp.status_code == 200
        assert "front" in resp.json()["synopsis_text"]

    def test_synopsis_503_when_empty(self, client):
        resp = client.get("/api/v1/synopsis")
        assert resp.status_code == 503


class TestCacheRefreshEndpoint:
    def test_refresh_cache(self, client):
        with patch.object(cache, "refresh") as mock_refresh:
            mock_refresh.return_value = None
            cache._last_updated = datetime.now()
            cache._forecasts["PZZ135"] = _make_forecast()
            resp = client.post("/api/v1/cache/refresh")
            assert resp.status_code == 200
            mock_refresh.assert_called_once()
