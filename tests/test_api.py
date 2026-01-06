"""
Tests for API endpoints
"""

import pytest
from fastapi import status


class TestHealthEndpoint:
    """Tests for the /health endpoint"""

    def test_health_check(self, test_client):
        """Test that health check endpoint returns 200 or 503"""
        response = test_client.get("/health")
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_503_SERVICE_UNAVAILABLE]
        
        data = response.json()
        assert "status" in data
        assert data["status"] in ["healthy", "unhealthy"]


class TestRootEndpoint:
    """Tests for the root / endpoint"""

    def test_root_endpoint(self, test_client):
        """Test that root endpoint returns API info"""
        response = test_client.get("/")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "status" in data
        assert data["status"] == "active"


class TestZonesEndpoint:
    """Tests for the /zones endpoint"""

    def test_get_zones(self, test_client):
        """Test that zones endpoint returns list of zones"""
        response = test_client.get("/zones")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "zones" in data
        assert isinstance(data["zones"], dict)
        assert len(data["zones"]) > 0


class TestForecastEndpoint:
    """Tests for the /forecast endpoints"""

    def test_get_forecast_invalid_zone_format(self, test_client):
        """Test that invalid zone format returns 400"""
        response = test_client.get("/forecast/invalid")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_forecast_nonexistent_zone(self, test_client):
        """Test that nonexistent zone returns 404"""
        response = test_client.get("/forecast/pzz999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_all_forecasts(self, test_client):
        """Test that all forecasts endpoint returns data"""
        response = test_client.get("/forecast/")
        # May be 200 or 503 depending on cache state
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_503_SERVICE_UNAVAILABLE]


class TestCacheEndpoints:
    """Tests for cache-related endpoints"""

    def test_cache_status(self, test_client):
        """Test that cache status endpoint returns metadata"""
        response = test_client.get("/cache/status")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert "cache_metadata" in data
        assert "zones_status" in data
