"""Shared fixtures for tests."""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

# Ensure src/ is on the path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


SAMPLE_FORECAST_TEXT = """\
Expires:202603082315;;837763
FZUS56 KSEW 081010
CWFSEW

Coastal Waters Forecast for Washington
National Weather Service Seattle WA
310 AM PDT Sun Mar 8 2026

Inland waters of western Washington and the northern and central
Washington coastal waters including the Olympic Coast National
Marine Sanctuary


PZZ135-082315-
Puget Sound and Hood Canal-
310 AM PDT Sun Mar 8 2026

...SMALL CRAFT ADVISORY IN EFFECT UNTIL 11 AM PST THIS MORNING...

.TODAY...SW wind 10 to 15 kt with gusts to 25 kt, becoming NW 10
to 15 kt this afternoon. Waves around 2 ft or less. Rain likely
early this morning, then a chance of rain late this morning and
afternoon.
.TONIGHT...SW wind 10 to 15 kt, easing to 5 to 10 kt after
midnight. Waves around 2 ft or less. Rain likely in the evening,
then rain and snow after midnight.
.MON...SW wind 10 to 15 kt. Waves around 2 ft or less. Snow in
the morning. Rain.

$$
"""

SAMPLE_UPCOMING_ADVISORY_TEXT = """\
PZZ133-082315-
Northern Inland Waters Including The San Juan Islands-
310 AM PDT Sun Mar 8 2026

...GALE WARNING FROM WEDNESDAY EVENING THROUGH THURSDAY MORNING...

.TODAY...NW wind 10 to 15 kt. Waves around 2 ft or less.
.TONIGHT...W wind 5 to 10 kt. Waves around 2 ft or less.

$$
"""

SAMPLE_NO_ADVISORY_TEXT = """\
PZZ134-082315-
Admiralty Inlet-
310 AM PDT Sun Mar 8 2026

.TODAY...SW wind 10 to 15 kt. Waves around 2 ft or less. Rain.
.TONIGHT...W wind 5 to 10 kt. Waves around 2 ft or less.

$$
"""

SAMPLE_SYNOPSIS_HTML = (
    "<HTML><head/><TITLE>Washington Marine Forecast</TITLE>\n"
    "<b>\n"
    "<br>620 <br>FZUS56 KSEW 081010<br>CWFSEW<br><br>"
    "Coastal Waters Forecast for Washington<br>"
    "National Weather Service Seattle WA<br>"
    "310 AM PDT Sun Mar 8 2026<br><br>"
    "PZZ100-082315-<br>310 AM PDT Sun Mar 8 2026<br><br>"
    "</b><blockquote>"
    "SYNOPSIS FOR THE NORTHERN AND CENTRAL WASHINGTON COASTAL AND INLAND\n"
    "WATERS...A front will cross the waters on Sunday, and move inland\n"
    "through early Monday. A stronger front then arrives around\n"
    "Wednesday, with a return of stronger southerly winds.\n"
    "</blockquote><p><i>$$\n"
)


@pytest.fixture
def mock_cache():
    """Patch the cache with pre-loaded data to avoid network calls during tests."""
    with (
        patch("app.services.cache.cache") as mock_cache_obj,
        patch("app.services.fetcher.fetch_zone_text", new_callable=AsyncMock),
        patch("app.services.fetcher.fetch_synopsis_html", new_callable=AsyncMock),
    ):
        yield mock_cache_obj


@pytest.fixture
def client():
    """Create a test client with the cache startup disabled."""
    from app.config import settings

    # Disable auth for test client by default
    original_key = settings.api_key
    settings.api_key = ""

    # Patch the lifespan to skip the actual network fetch
    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def noop_lifespan(app):
        yield

    from app.main import create_app

    test_app = create_app()
    test_app.router.lifespan_context = noop_lifespan

    with TestClient(test_app) as c:
        yield c

    settings.api_key = original_key
