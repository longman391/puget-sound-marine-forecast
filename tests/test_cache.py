"""
Tests for cache functionality
"""


class TestCacheMetadata:
    """Tests for cache metadata structure"""

    def test_cache_metadata_structure(self):
        """Test that cache metadata has expected structure"""
        from main import cache_metadata

        assert "last_updated" in cache_metadata
        assert "next_update" in cache_metadata
        assert "update_interval_minutes" in cache_metadata
        assert "total_updates" in cache_metadata
        assert "last_update_duration" in cache_metadata

    def test_cache_update_interval(self):
        """Test that cache update interval is set correctly"""
        from main import cache_metadata

        assert cache_metadata["update_interval_minutes"] == 120


class TestCacheStructure:
    """Tests for forecast cache structure"""

    def test_forecast_cache_exists(self):
        """Test that forecast cache exists"""
        from main import forecast_cache

        assert forecast_cache is not None
        assert isinstance(forecast_cache, dict)

    def test_zones_configuration(self):
        """Test that ZONES configuration is correct"""
        from main import ZONES

        assert isinstance(ZONES, dict)
        assert len(ZONES) == 14
        assert "pzz133" in ZONES
        assert "pzz135" in ZONES
