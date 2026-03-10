# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- CHANGELOG.md for tracking version history
- Infrastructure deployment automation
- Type checking with mypy
- Security scanning workflows
- Dependency vulnerability scanning
- Coverage threshold enforcement

### Changed
- Improved CI/CD pipeline with additional checks
- Enhanced pre-commit hooks

### Removed
- Empty src/test_api.py file (tests already in /tests directory)

## [1.0.0] - 2024-02-09

### Added
- Initial release
- FastAPI-based marine forecast API
- Scraping and parsing of UW/NOAA marine forecast data
- Support for all 14 Puget Sound forecast zones
- Automatic background cache updates (120-minute interval)
- RESTful JSON API endpoints
- Rate limiting and security features
- Comprehensive test suite
- Docker containerization
- Azure deployment infrastructure files

### Features
- `/` - API status and cache information
- `/zones` - List all available forecast zones
- `/forecast/{zone}` - Get parsed forecast for specific zone
- `/forecast/` - Get all forecasts
- `/cache/status` - Cache health and statistics
- `POST /cache/refresh` - Manually trigger cache refresh

[Unreleased]: https://github.com/longman391/puget-sound-marine-forecast/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/longman391/puget-sound-marine-forecast/releases/tag/v1.0.0
