# Contributing to Puget Sound Marine Forecast API

Thank you for your interest in contributing! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Code Quality](#code-quality)
- [Dependency Management](#dependency-management)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

This is a learning project! We welcome contributions from developers of all skill levels. Please be respectful and constructive in all interactions.

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Git
- Virtual environment tool (venv, conda, etc.)

### Setup Development Environment

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/YOUR-USERNAME/puget-sound-marine-forecast.git
   cd puget-sound-marine-forecast
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   
   # Activate on Windows
   .venv\Scripts\activate
   
   # Activate on macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   # Install all dependencies with version constraints
   pip install -r requirements.txt -c constraints.txt
   
   # Or for development
   pip install -r requirements-dev.txt -c constraints.txt
   ```

4. **Install pre-commit hooks**
   ```bash
   pre-commit install
   ```

5. **Copy environment configuration**
   ```bash
   cp .env.development .env
   ```

## Development Workflow

### Create a Branch

```bash
# Create a feature branch
git checkout -b feature/your-feature-name

# Or a bug fix branch
git checkout -b fix/issue-description
```

### Make Changes

1. Write your code following the [Code Style Guidelines](#code-quality)
2. Add or update tests as needed
3. Update documentation if applicable
4. Run pre-commit hooks: `pre-commit run --all-files`
5. Test your changes locally

### Commit Changes

```bash
# Stage your changes
git add .

# Commit with a descriptive message
git commit -m "feat: add new feature"
# or
git commit -m "fix: resolve issue with X"
```

**Commit Message Format:**
- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `test:` Test additions or modifications
- `refactor:` Code refactoring
- `style:` Code style changes (formatting, etc.)
- `chore:` Maintenance tasks

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html --cov-report=term-missing

# Run specific test file
pytest tests/test_api.py

# Run specific test
pytest tests/test_api.py::TestHealthEndpoint::test_health_check

# Run with verbose output
pytest -v
```

### Test Coverage Requirements

- **Minimum coverage**: 57% overall
- **New code**: Aim for 80%+ coverage on new features
- **Critical paths**: 90%+ coverage on security and data parsing logic

### Writing Tests

Tests should:
- Be clear and focused on a single behavior
- Follow the AAA pattern (Arrange, Act, Assert)
- Use descriptive names: `test_[what]_[condition]_[expected]`
- Mock external dependencies (NOAA API calls)

**Example:**
```python
def test_forecast_parsing_with_valid_data_returns_structured_output(test_client):
    # Arrange
    zone = "pzz133"
    
    # Act
    response = test_client.get(f"/forecast/{zone}")
    
    # Assert
    assert response.status_code == 200
    assert "forecast" in response.json()
```

### Test Organization

- `tests/test_api.py`: API endpoint tests
- `tests/test_scraper.py`: Scraper and parser tests
- `tests/test_cache.py`: Cache functionality tests
- `tests/conftest.py`: Shared fixtures

## Code Quality

### Formatting and Linting

This project uses multiple tools for code quality:

```bash
# Format code with Black (required)
black src/ tests/

# Check formatting
black --check src/ tests/

# Lint with Ruff (required)
ruff check src/ tests/

# Auto-fix linting issues
ruff check --fix src/ tests/

# Type checking with mypy (recommended)
mypy src/ --ignore-missing-imports
```

### Code Style Guidelines

- **Line length**: Maximum 100 characters
- **Python version**: Target 3.11+
- **Formatter**: Black (non-negotiable)
- **Linter**: Ruff with rules: E, F, I, N, W, UP
- **Type hints**: Encouraged but not strictly required
- **Docstrings**: Required for public APIs, recommended for complex functions

### Pre-commit Hooks

Pre-commit hooks run automatically on commit and include:
- Black formatting
- Ruff linting
- mypy type checking
- Trailing whitespace removal
- YAML/TOML validation
- Secret detection (gitleaks)
- Large file check

Run manually:
```bash
pre-commit run --all-files
```

## Dependency Management

### Adding Dependencies

1. **Production dependencies**: Add to `requirements-prod.txt`
2. **Development dependencies**: Add to `requirements-dev.txt`
3. **All dependencies**: Update `requirements.txt` to include both
4. **Version pinning**: Update `constraints.txt` with exact versions

**Before adding a dependency:**

```bash
# Check for security vulnerabilities
pip-audit PACKAGE_NAME==VERSION

# Or install and check
pip install PACKAGE_NAME==VERSION
pip-audit
```

### Updating Dependencies

1. **Test the update locally**
   ```bash
   pip install --upgrade PACKAGE_NAME
   pytest
   ```

2. **Update all files**
   - Update version in appropriate requirements file
   - Update `constraints.txt` with new version
   - Test thoroughly

3. **Document in CHANGELOG.md**
   ```markdown
   ### Changed
   - Updated PACKAGE_NAME from X.Y.Z to A.B.C
   ```

### Dependency Security

- ✅ Run `pip-audit` before adding new dependencies
- ✅ Check for known vulnerabilities
- ✅ Prefer well-maintained packages with active communities
- ✅ Pin versions in `constraints.txt` for reproducibility
- ✅ Review Dependabot PRs promptly

## Pull Request Process

### Before Submitting

1. **Run all checks locally**
   ```bash
   # Format and lint
   black src/ tests/
   ruff check --fix src/ tests/
   mypy src/ --ignore-missing-imports
   
   # Run tests
   pytest --cov=src --cov-report=term-missing
   
   # Security checks
   pip-audit
   detect-secrets scan
   
   # Pre-commit hooks
   pre-commit run --all-files
   ```

2. **Update documentation**
   - Update README.md if adding features
   - Update CHANGELOG.md under `[Unreleased]`
   - Add/update docstrings for new functions
   - Update DEPLOYMENT.md if changing infrastructure

3. **Test coverage**
   - Ensure new code has tests
   - Verify coverage meets minimum (57%)
   - Aim for 80%+ on new features

### Submitting a Pull Request

1. **Push your branch**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create PR on GitHub**
   - Provide a clear title and description
   - Reference any related issues
   - Describe what changed and why
   - Include screenshots for UI changes

3. **PR Description Template**
   ```markdown
   ## Description
   Brief description of changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update
   
   ## Testing
   - [ ] Tests pass locally
   - [ ] Coverage meets requirements
   - [ ] Manual testing completed
   
   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Self-review completed
   - [ ] Documentation updated
   - [ ] No new warnings generated
   ```

4. **Wait for CI checks**
   - All CI checks must pass
   - Address any failing tests or linting issues
   - Respond to review feedback

### Review Process

1. **Automated checks** run on all PRs:
   - Code formatting (Black)
   - Linting (Ruff)
   - Type checking (mypy)
   - Tests and coverage
   - Security scanning

2. **Code review** by maintainers
   - Typically within 1-3 days
   - Address feedback promptly
   - Be open to suggestions

3. **Merge criteria**:
   - All CI checks passing
   - Approved by maintainer
   - No merge conflicts
   - Documentation updated

## Environment Configuration

### Environment Files

- `.env.development`: Local development settings
- `.env.test`: Test environment settings
- `.env.production`: Production settings (template only)
- `.env.example`: Example for documentation

**Never commit actual `.env` files with secrets!**

### Required Environment Variables

See `.env.example` for full list. Key variables:
- `API_TITLE`: API name
- `HOST`: Bind address (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `CACHE_UPDATE_INTERVAL_MINUTES`: Cache refresh interval
- `ALLOWED_ORIGINS`: CORS origins
- `LOG_LEVEL`: Logging level

## Security

### Security Best Practices

- ✅ Never commit secrets, API keys, or credentials
- ✅ Use `.env` files for configuration (gitignored)
- ✅ Run security scans before commits
- ✅ Review dependency vulnerabilities
- ✅ Follow principle of least privilege

### Reporting Security Issues

See [SECURITY.md](SECURITY.md) for reporting vulnerabilities.

## Questions or Problems?

- Open a [GitHub Issue](https://github.com/longman391/puget-sound-marine-forecast/issues)
- Check existing issues for similar questions
- Review [DEPLOYMENT.md](DEPLOYMENT.md) for deployment questions

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Puget Sound Marine Forecast API! 🎉
