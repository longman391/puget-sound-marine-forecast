# Puget Sound Marine Forecast API

[![CI](https://github.com/longman391/puget-sound-marine-forecast/workflows/CI/badge.svg)](https://github.com/longman391/puget-sound-marine-forecast/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/longman391/puget-sound-marine-forecast/branch/main/graph/badge.svg)](https://codecov.io/gh/longman391/puget-sound-marine-forecast)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A Python API that scrapes and serves marine forecast data for Puget Sound from the University of Washington and NOAA. Intended to be easily consumed as a RESTful call from Home Assistant, Dakboard, etc.

##  Quick Start 🚀

### Prerequisites
- Python 3.11+
- Git

### Installation & Running
```bash
# Clone the repository
git clone https://github.com/longman391/puget-sound-marine-forecast.git
cd puget-sound-marine-forecast

# Set up Python environment (auto-configured in VS Code)
# Or manually: python -m venv .venv && .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the API server
cd src
python main.py
```

### Usage
- **API Documentation:** http://localhost:8000/docs
- **All Zones:** http://localhost:8000/zones  
- **San Juan Islands:** http://localhost:8000/forecast/pzz133
- **Puget Sound:** http://localhost:8000/forecast/pzz135
- **All Forecasts:** http://localhost:8000/forecast/

##  About

The University of Washington does an excellent job of providing accurate and timely forecasts for Washington State marine areas. Unfortunately, those forecasts are provided only in unstructured formats from the UW and NOAA, making them difficult to use in other contexts. 

This project attempts to resolve this issue by ingesting the raw forecast texts, parsing them, and providing a structured JSON API for access, making it easy for applications to consume the structured forecast data.

##  Features (Completed ✅)

- [x] Scrape UW marine forecast text files ✅
- [x] Parse forecast data into structured format ✅  
- [x] Provide RESTful JSON API endpoints ✅
- [x] Automatic forecast updates (120-minute background cache - optimized for personal use) ✅
- [x] Infrastructure as Code with Azure Bicep ✅
- [x] Automated CI/CD pipelines ✅
- [x] Security scanning and dependency management ✅
- [ ] Deploy as Azure Container App (infrastructure ready, requires Azure credentials)
- [ ] Historical data storage

##  Tech Stack (Implemented)

**Backend:** Python 3.11+ with FastAPI ✅  
**Dependencies:** httpx, python-dateutil, uvicorn ✅  
**Security:** Rate limiting, input validation, CORS protection ✅  
**Caching:** In-memory cache with 120-minute background updates (personal use optimized) ✅  
**Performance:** Lightning-fast cached responses (<100ms) ⚡  
**Deployment:** Ready for Azure Functions, Azure Container Apps, or Azure App Service  
**Data Format:** Real-time JSON from NOAA text files ✅  
**Parsing:** Advanced regex with estimated 100% wind data accuracy ✅

##  API Endpoints ✅

- `GET /` - API status and cache information
- `GET /zones` - List all 14 available forecast zones  
- `GET /forecast/{zone}` - Get parsed forecast for specific zone (cached)
- `GET /forecast/` - All forecasts for all 14 zones (cached)
- `GET /cache/status` - Detailed cache health and statistics  
- `POST /cache/refresh` - Manually trigger cache refresh

##  Supported Zones ✅

All 14 NOAA marine forecast zones including:
- **PZZ133**: Northern Inland Waters Including The San Juan Islands
- **PZZ135**: Puget Sound and Hood Canal
- PZZ100, PZZ110, PZZ130-132, PZZ134, PZZ150, PZZ153, PZZ156, PZZ170, PZZ173, PZZ176

##  Project Status

🎉 **API Complete & Working**

##  Security Features ✅

- **Rate Limiting**: Optimized for personal use
  - General endpoints: 100-500 requests/hour
  - Cache refresh: 10 requests/hour
  - Cache status: 60 requests/hour
- **Input Validation**: Strict zone format validation with regex patterns
- **Error Handling**: Secure error responses that don't leak internal information
- **CORS Protection**: Configurable cross-origin request policies
- **Host Header Validation**: Protection against host header attacks
- **Request Timeouts**: Configured timeouts for external API calls
- **Comprehensive Logging**: Security event logging for monitoring
- **Automated Security Scanning**: 
  - Dependency vulnerability scanning with pip-audit
  - Secret detection with gitleaks and detect-secrets
  - Automated security updates via Dependabot

See [SECURITY.md](SECURITY.md) for our security policy and reporting vulnerabilities.

##  Data Source

- University of Washington Marine Weather Forecast via NOAA
- Text files updated regularly by UW meteorology department

##  Development

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/longman391/puget-sound-marine-forecast.git
   cd puget-sound-marine-forecast
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv .venv
   
   # On Windows
   .venv\Scripts\activate
   
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -r requirements-dev.txt
   ```

4. **Set up environment variables (optional)**
   ```bash
   cp .env.example .env
   # Edit .env with your preferred settings
   ```

### Running the Application

```bash
cd src
python main.py
```

The API will be available at http://localhost:8000

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_api.py

# Run with verbose output
pytest -v
```

**Test Coverage**: This project enforces a minimum test coverage of 57% (see [pyproject.toml](pyproject.toml)). Current coverage is approximately 58%.

### Code Quality

This project uses **Black** for code formatting, **Ruff** for linting, and **mypy** for type checking.

```bash
# Format code with Black
black src/ tests/

# Check formatting without changes
black --check src/ tests/

# Lint with Ruff
ruff check src/ tests/

# Lint and auto-fix issues
ruff check --fix src/ tests/

# Type checking with mypy
mypy src/ --ignore-missing-imports
```

### Security Checks

```bash
# Check for dependency vulnerabilities
pip-audit --desc

# Scan for secrets (after installing detect-secrets)
pip install detect-secrets
detect-secrets scan

# Run all pre-commit hooks including security checks
pre-commit run --all-files
```

### Pre-commit Hooks

We use pre-commit hooks to ensure code quality before commits.

```bash
# Install pre-commit hooks
pre-commit install

# Run hooks manually on all files
pre-commit run --all-files
```

### Code Style Guidelines

- **Line length**: Maximum 100 characters
- **Python version**: 3.11+
- **Formatter**: Black
- **Linter**: Ruff with selected rules (E, F, I, N, W, UP)
- **Type Checker**: mypy (configured in pyproject.toml)
- **Imports**: Sorted and organized
- **Type hints**: Encouraged but not required
- **Docstrings**: Use for public APIs and complex functions
- **Coverage**: Minimum 57% test coverage enforced

### Project Structure

```
puget-sound-marine-forecast/
├── src/                       # Source code
│   ├── main.py               # FastAPI application
│   ├── scraper.py            # Forecast scraper and parser
│   └── __init__.py
├── tests/                    # Test suite
│   ├── conftest.py           # Pytest fixtures
│   ├── test_api.py           # API endpoint tests
│   ├── test_scraper.py       # Scraper tests
│   └── test_cache.py         # Cache tests
├── infra/                    # Infrastructure as Code (Bicep)
│   ├── main.bicep            # Main infrastructure template
│   ├── main-resources.bicep  # Resource definitions
│   └── main.parameters.json  # Environment parameters
├── .github/
│   ├── workflows/
│   │   ├── ci.yml           # CI pipeline
│   │   └── infra-deploy.yml # Infrastructure deployment
│   └── dependabot.yml       # Automated dependency updates
├── requirements.txt          # All dependencies
├── requirements-prod.txt     # Production dependencies only
├── requirements-dev.txt      # Development dependencies
├── constraints.txt           # Version constraints for reproducibility
├── pyproject.toml            # Project configuration
├── .pre-commit-config.yaml   # Pre-commit hooks
├── .env.example              # Example environment variables
├── .env.development          # Development environment config
├── .env.test                 # Test environment config
├── .env.production           # Production environment config
├── Dockerfile                # Container configuration
├── azure.yaml                # Azure Developer CLI config
├── CHANGELOG.md              # Version history
├── DEPLOYMENT.md             # Deployment guide
└── SECURITY.md               # Security policy
```

## 🚀 Deployment

This project is ready to deploy to Azure Container Apps with full infrastructure automation.

### Quick Deploy with Azure Developer CLI

```bash
# Install Azure Developer CLI
# See: https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd

# Deploy to Azure
azd up
```

For detailed deployment instructions including:
- Azure Container Apps deployment
- GitHub Actions CI/CD setup
- Environment configuration
- Infrastructure as Code with Bicep
- Monitoring and maintenance

See the complete [DEPLOYMENT.md](DEPLOYMENT.md) guide.

## 📋 CI/CD Pipeline

### Continuous Integration

Every push and pull request runs:
- ✅ Code formatting check (Black)
- ✅ Linting (Ruff)
- ✅ Type checking (mypy)
- ✅ Security scanning (pip-audit, detect-secrets)
- ✅ Unit tests with coverage reporting
- ✅ Environment configuration validation

### Infrastructure Deployment

The infrastructure deployment workflow:
- ✅ Validates Bicep templates
- ✅ Supports dev/test/prod environments
- ✅ Uses Azure OIDC for secure authentication
- ✅ Automated deployment on infrastructure changes

## 🔒 Security

This project follows security best practices:

- **Automated Scanning**: Dependencies scanned for vulnerabilities
- **Secret Detection**: Commits scanned for exposed secrets
- **Dependabot**: Automated security updates
- **Type Safety**: mypy type checking enabled
- **Code Quality**: Enforced via pre-commit hooks and CI

For security policies and reporting vulnerabilities, see [SECURITY.md](SECURITY.md).

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and release notes.

##  Contributing

We welcome contributions! This is a learning project and we encourage developers of all skill levels to participate.

### Quick Start for Contributors

1. Fork the repository
2. Create a feature branch
3. Install dependencies: `pip install -r requirements-dev.txt -c constraints.txt`
4. Install pre-commit hooks: `pre-commit install`
5. Make your changes with tests
6. Run quality checks: `pre-commit run --all-files`
7. Submit a pull request

For detailed contributing guidelines, including:
- Development workflow
- Testing requirements (57% minimum coverage)
- Code quality standards
- Dependency management
- Pull request process

See the complete [CONTRIBUTING.md](CONTRIBUTING.md) guide.

##  License

MIT License - see [LICENSE](LICENSE) file for details.

