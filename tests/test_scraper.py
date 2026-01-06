"""
Tests for the forecast scraper and parser
"""

import pytest
from datetime import datetime


class TestForecastScraper:
    """Tests for the ForecastScraper class"""

    def test_scraper_initialization(self):
        """Test that scraper can be initialized"""
        from scraper import ForecastScraper
        
        scraper = ForecastScraper()
        assert scraper is not None
        assert scraper.BASE_URL == "https://tgftp.nws.noaa.gov/data/forecasts/marine/coastal/pz"

    def test_parse_forecast_text(self, sample_forecast_text):
        """Test parsing a sample forecast text"""
        from scraper import ForecastScraper
        
        scraper = ForecastScraper()
        forecast = scraper.parse_forecast_text(sample_forecast_text, "pzz133")
        
        assert forecast is not None
        assert forecast.zone == "PZZ133"
        assert "San Juan" in forecast.name
        assert isinstance(forecast.issued, datetime)
        assert isinstance(forecast.expires, datetime)
        assert len(forecast.periods) > 0

    def test_parse_forecast_period_structure(self, sample_forecast_text):
        """Test that forecast periods have correct structure"""
        from scraper import ForecastScraper
        
        scraper = ForecastScraper()
        forecast = scraper.parse_forecast_text(sample_forecast_text, "pzz133")
        
        for period in forecast.periods:
            assert period.name is not None
            assert period.wind is not None
            assert period.waves is not None


@pytest.mark.asyncio
class TestAsyncForecastFetching:
    """Tests for async forecast fetching"""

    async def test_fetch_zone_text_url_format(self):
        """Test that zone text URL is formatted correctly"""
        from scraper import ForecastScraper
        
        scraper = ForecastScraper()
        zone = "pzz133"
        expected_url = f"{scraper.BASE_URL}/{zone}.txt"
        
        # Just verify the URL format is correct
        assert expected_url == "https://tgftp.nws.noaa.gov/data/forecasts/marine/coastal/pz/pzz133.txt"
