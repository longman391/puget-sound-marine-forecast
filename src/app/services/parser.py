"""Lightweight text parser for NOAA forecast files.

Extracts metadata (zone name, timestamps) and advisory banners from the
structured header portions of the forecast. The forecast prose itself is
returned verbatim as a text blob — no regex decomposition of wind/waves/weather.
"""

import logging
import re
from datetime import UTC, datetime

from dateutil import parser as dateutil_parser

from app.models import ZONES

logger = logging.getLogger(__name__)

# Advisory banners appear between triple-dot markers: ...TEXT...
_ADVISORY_PATTERN = re.compile(r"\.\.\.(.*?)\.\.\.", re.DOTALL)

# Keywords that indicate an advisory/warning/watch
_ADVISORY_KEYWORDS = {"ADVISORY", "WARNING", "WATCH", "STATEMENT", "ALERT"}

# Phrases indicating an upcoming (future) advisory
_UPCOMING_PHRASES = re.compile(
    r"FROM |BEGINNING |EXPECTED |LATER |ISSUED AT",
    re.IGNORECASE,
)


def parse_zone_forecast(
    raw_text: str,
    zone_id: str,
    fetched_at: datetime,
) -> dict:
    """Parse a per-zone NOAA forecast text file into a flat dict.

    Returns a dict matching the ZoneForecast model fields.
    """
    zone_id_upper = zone_id.upper()
    zone_name = _extract_zone_name(raw_text, zone_id_upper)
    issued = _extract_issued(raw_text)
    expires = _extract_expires(raw_text, zone_id_upper)
    forecast_text = _extract_forecast_body(raw_text)
    advisories = _extract_advisories(raw_text)

    has_active = False
    has_upcoming = False
    advisory_texts: list[str] = []

    for adv in advisories:
        advisory_texts.append(adv)
        is_upcoming = bool(_UPCOMING_PHRASES.search(adv))
        # Any advisory that isn't explicitly upcoming is treated as active
        if not is_upcoming:
            has_active = True
        if is_upcoming:
            has_upcoming = True

    return {
        "zone_id": zone_id_upper,
        "zone_name": zone_name,
        "issued": issued,
        "expires": expires,
        "forecast_text": forecast_text,
        "has_active_advisory": has_active,
        "has_upcoming_advisory": has_upcoming,
        "advisory_text": "\n".join(advisory_texts) if advisory_texts else None,
        "fetched_at": fetched_at,
    }


def parse_synopsis(raw_html: str, fetched_at: datetime):
    """Parse the UW combined forecast HTML to extract the synopsis section."""
    from app.models import SynopsisResponse

    synopsis_match = re.search(
        r"PZZ100.*?<blockquote>(.*?)</blockquote>",
        raw_html,
        re.DOTALL | re.IGNORECASE,
    )

    if synopsis_match:
        text = synopsis_match.group(1)
        text = re.sub(r"<[^>]+>", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = text.strip()
    else:
        text = ""
        logger.warning("Could not extract synopsis from UW combined forecast")

    issued = _extract_issued(raw_html.replace("<br>", "\n"))

    return SynopsisResponse(synopsis_text=text, issued=issued, fetched_at=fetched_at)


# --- Private helpers ---


def _extract_zone_name(text: str, zone_id: str) -> str:
    """Extract zone name from the header line following the zone code."""
    # Pattern: PZZ135-082315-\nPuget Sound and Hood Canal-\n
    pattern = rf"{re.escape(zone_id)}-\d+-\n(.+?)-\n"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    # Fallback to the static ZONES dict
    return ZONES.get(zone_id, f"Zone {zone_id}")


def _extract_issued(text: str) -> datetime | None:
    """Extract the issued timestamp from the forecast header."""
    # Pattern: "310 AM PDT Sun Mar 8 2026" or "1000 AM PDT Mon Mar 9 2026"
    pattern = r"(\d{1,4}\s+[AP]M\s+\w+\s+\w{3}\s+\w{3}\s+\d{1,2}\s+\d{4})"
    match = re.search(pattern, text)
    if not match:
        return None

    timestamp_str = match.group(1).strip()
    try:
        # NOAA uses compact time format: "310 AM" means "3:10 AM"
        fixed = re.sub(r"^(\d{1,2})(\d{2})\s+([AP]M)", r"\1:\2 \3", timestamp_str)
        return dateutil_parser.parse(fixed)
    except Exception:
        logger.debug("Failed to parse issued timestamp: %s", timestamp_str)
        return None


def _extract_expires(text: str, zone_id: str) -> datetime | None:
    """Extract the expiration code from the zone header.

    Uses the issued timestamp's date as anchor rather than now() to avoid
    timezone and day-rollover issues.
    """
    pattern = rf"{re.escape(zone_id)}-(\d{{6}})-"
    match = re.search(pattern, text, re.IGNORECASE)
    if not match:
        return None

    code = match.group(1)
    try:
        day = int(code[:2])
        hour = int(code[2:4])
        minute = int(code[4:6])

        # Use issued time as date anchor when available, else UTC now
        issued = _extract_issued(text)
        anchor = issued if issued else datetime.now(tz=UTC)

        expires = anchor.replace(day=day, hour=hour, minute=minute, second=0, microsecond=0)
        if expires < anchor:
            month = expires.month + 1
            year = expires.year
            if month > 12:
                month, year = 1, year + 1
            expires = expires.replace(year=year, month=month)
        return expires
    except (ValueError, OverflowError):
        logger.debug("Failed to parse expires code: %s", code)
        return None


def _extract_forecast_body(text: str) -> str:
    """Extract the forecast body text (all periods) from the raw text.

    Captures everything from the first period marker (e.g., '.TODAY...')
    through the end-of-forecast marker ('$$').
    """
    # Find the first period marker
    period_start = re.search(r"^\.[A-Z]", text, re.MULTILINE)
    if not period_start:
        # If no period markers, return everything after the header
        return text.strip()

    body = text[period_start.start() :]

    # Trim at the $$ marker
    end_marker = body.find("$$")
    if end_marker != -1:
        body = body[:end_marker]

    return body.strip()


def _extract_advisories(text: str) -> list[str]:
    """Extract advisory/warning/watch banners from the forecast text.

    Advisories appear as lines wrapped in triple-dot markers:
        ...SMALL CRAFT ADVISORY IN EFFECT UNTIL 11 AM PST THIS MORNING...
    """
    matches = _ADVISORY_PATTERN.findall(text)
    advisories = []
    for match in matches:
        # Normalize whitespace
        clean = re.sub(r"\s+", " ", match).strip()
        # Only include if it contains advisory keywords
        if any(kw in clean.upper() for kw in _ADVISORY_KEYWORDS):
            advisories.append(clean)
    return advisories
