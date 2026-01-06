"""
Pytest configuration and fixtures for Puget Sound Marine Forecast API tests
"""

import pytest
import sys
import os
from typing import AsyncGenerator

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from fastapi.testclient import TestClient
from httpx import AsyncClient


@pytest.fixture
def test_client():
    """Create a test client for the FastAPI application"""
    from main import app
    
    return TestClient(app)


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create an async test client for the FastAPI application"""
    from main import app
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def sample_forecast_text():
    """Sample NOAA forecast text for testing parser"""
    return """PZZ133-061800-
Northern Inland Waters Including The San Juan Islands-
1234 AM PST Mon Jan 6 2026

.TONIGHT...N wind 10 kt. Wind waves 1 ft or less.
.TUE...N wind 10 kt. Wind waves 1 ft or less.
.TUE NIGHT...N wind 10 kt. Wind waves 1 ft or less.
.WED...N wind 10 kt. Wind waves 1 ft or less.

$$
"""
