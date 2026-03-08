"""Tests for the forecast text parser."""

from datetime import datetime

from conftest import (
    SAMPLE_FORECAST_TEXT,
    SAMPLE_NO_ADVISORY_TEXT,
    SAMPLE_SYNOPSIS_HTML,
    SAMPLE_UPCOMING_ADVISORY_TEXT,
)

from app.services.parser import (
    _extract_advisories,
    _extract_forecast_body,
    _extract_issued,
    _extract_zone_name,
    parse_synopsis,
    parse_zone_forecast,
)


class TestExtractZoneName:
    def test_extracts_name_from_header(self):
        assert _extract_zone_name(SAMPLE_FORECAST_TEXT, "PZZ135") == "Puget Sound and Hood Canal"

    def test_falls_back_to_zones_dict(self):
        name = _extract_zone_name("no header here", "PZZ135")
        assert name == "Puget Sound and Hood Canal"

    def test_falls_back_to_generic_label(self):
        name = _extract_zone_name("no header here", "PZZ999")
        assert name == "Zone PZZ999"


class TestExtractIssued:
    def test_parses_standard_timestamp(self):
        dt = _extract_issued(SAMPLE_FORECAST_TEXT)
        assert dt is not None
        assert dt.year == 2026
        assert dt.month == 3
        assert dt.day == 8

    def test_returns_none_for_no_match(self):
        assert _extract_issued("no timestamp here") is None


class TestExtractForecastBody:
    def test_extracts_period_text(self):
        body = _extract_forecast_body(SAMPLE_FORECAST_TEXT)
        assert body.startswith(".TODAY...")
        assert "$$" not in body
        assert ".TONIGHT..." in body
        assert ".MON..." in body

    def test_handles_missing_periods(self):
        result = _extract_forecast_body("just some text without periods")
        assert result == "just some text without periods"


class TestExtractAdvisories:
    def test_detects_active_advisory(self):
        advisories = _extract_advisories(SAMPLE_FORECAST_TEXT)
        assert len(advisories) == 1
        assert "SMALL CRAFT ADVISORY" in advisories[0]

    def test_detects_upcoming_advisory(self):
        advisories = _extract_advisories(SAMPLE_UPCOMING_ADVISORY_TEXT)
        assert len(advisories) == 1
        assert "GALE WARNING" in advisories[0]

    def test_no_advisory(self):
        advisories = _extract_advisories(SAMPLE_NO_ADVISORY_TEXT)
        assert advisories == []


class TestParseZoneForecast:
    def test_full_parse_with_active_advisory(self):
        result = parse_zone_forecast(SAMPLE_FORECAST_TEXT, "pzz135", datetime.now())
        assert result["zone_id"] == "PZZ135"
        assert result["zone_name"] == "Puget Sound and Hood Canal"
        assert result["has_active_advisory"] is True
        assert result["has_upcoming_advisory"] is False
        assert "SMALL CRAFT ADVISORY" in result["advisory_text"]
        assert ".TODAY..." in result["forecast_text"]

    def test_full_parse_with_upcoming_advisory(self):
        result = parse_zone_forecast(SAMPLE_UPCOMING_ADVISORY_TEXT, "pzz133", datetime.now())
        assert result["zone_id"] == "PZZ133"
        assert result["has_active_advisory"] is False
        assert result["has_upcoming_advisory"] is True
        assert "GALE WARNING" in result["advisory_text"]

    def test_full_parse_no_advisory(self):
        result = parse_zone_forecast(SAMPLE_NO_ADVISORY_TEXT, "pzz134", datetime.now())
        assert result["zone_id"] == "PZZ134"
        assert result["has_active_advisory"] is False
        assert result["has_upcoming_advisory"] is False
        assert result["advisory_text"] is None


class TestParseSynopsis:
    def test_extracts_synopsis_text(self):
        result = parse_synopsis(SAMPLE_SYNOPSIS_HTML, datetime.now())
        assert "SYNOPSIS" in result["synopsis_text"]
        assert "front will cross the waters" in result["synopsis_text"]

    def test_handles_missing_synopsis(self):
        result = parse_synopsis("<html>no synopsis</html>", datetime.now())
        assert result["synopsis_text"] == ""
