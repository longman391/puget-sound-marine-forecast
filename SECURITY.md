# Security Policy

## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of Puget Sound Marine Forecast API seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### Where to Report

Please report security vulnerabilities by emailing the repository owner directly through GitHub or by creating a **private** security advisory:

1. Go to the [Security Advisories page](https://github.com/longman391/puget-sound-marine-forecast/security/advisories)
2. Click "Report a vulnerability"
3. Provide detailed information about the vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

### What to Include

When reporting a vulnerability, please include:

- Type of vulnerability
- Full paths of source file(s) related to the vulnerability
- Location of the affected source code (tag/branch/commit or direct URL)
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

### Response Timeline

- **Initial Response**: Within 48 hours of report
- **Status Update**: Within 7 days with assessment and timeline
- **Fix Timeline**: Critical issues within 30 days, others as prioritized

## Security Best Practices

### For Users

1. **Environment Variables**: Never commit `.env` files with actual credentials
2. **Rate Limiting**: Keep rate limiting enabled in production
3. **CORS**: Configure `ALLOWED_ORIGINS` restrictively for production
4. **Host Validation**: Set `ALLOWED_HOSTS` to your actual domain(s)
5. **Updates**: Keep dependencies updated using `pip-audit` and Dependabot

### For Contributors

1. **Dependencies**: 
   - Run `pip-audit` before submitting PRs
   - Check for known vulnerabilities
   - Use pinned versions in constraints.txt

2. **Secrets**:
   - Never commit API keys, tokens, or passwords
   - Use `.env.example` for documentation only
   - Scan commits with `detect-secrets` or `gitleaks`

3. **Code Quality**:
   - Run all pre-commit hooks
   - Ensure tests pass with adequate coverage
   - Follow secure coding practices

4. **Input Validation**:
   - Validate all user inputs
   - Use Pydantic models for API validation
   - Sanitize data before processing

## Automated Security Checks

This repository uses:

- **Dependabot**: Automated dependency updates
- **pip-audit**: Python dependency vulnerability scanning
- **detect-secrets**: Secret scanning in commits
- **Gitleaks**: Additional secret detection
- **GitHub Security Advisories**: CVE monitoring

## Security Features

### Implemented

- ✅ Rate limiting (SlowAPI)
- ✅ CORS protection (configurable)
- ✅ Host header validation
- ✅ Request timeouts
- ✅ Input validation (Pydantic)
- ✅ Secure error handling
- ✅ Dependency pinning
- ✅ Automated security scanning in CI

### Planned

- 🔄 Web Application Firewall (WAF) integration
- 🔄 DDoS protection
- 🔄 API authentication/authorization
- 🔄 Request signing
- 🔄 Audit logging

## Disclosure Policy

When we receive a security vulnerability report, we will:

1. Confirm the problem and determine affected versions
2. Audit code to find similar problems
3. Prepare fixes for all supported versions
4. Release patches as soon as possible
5. Credit the reporter (unless anonymity is requested)

## Contact

For questions about this security policy, please open a discussion on GitHub or contact the repository owner.

---

**Last Updated**: 2024-02-09
