# Deployment Guide

This guide covers deploying the Puget Sound Marine Forecast API to various environments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Azure Container Apps Deployment](#azure-container-apps-deployment)
- [Environment Configuration](#environment-configuration)
- [Infrastructure as Code](#infrastructure-as-code)
- [CI/CD Automation](#cicd-automation)
- [Monitoring and Maintenance](#monitoring-and-maintenance)

## Prerequisites

### Required Tools

- **Azure CLI**: Version 2.50.0 or later
- **Azure Developer CLI (azd)**: Latest version
- **Docker**: For local container testing
- **Python 3.11+**: For local development
- **Git**: For version control

### Azure Requirements

- Active Azure subscription
- Service Principal with Contributor role
- Resource Group permissions

## Azure Container Apps Deployment

### Option 1: Using Azure Developer CLI (Recommended)

The repository is configured with `azure.yaml` for streamlined deployment using `azd`.

#### Initial Setup

```bash
# Install Azure Developer CLI
# Windows: winget install microsoft.azd
# macOS: brew tap azure/azd && brew install azd
# Linux: curl -fsSL https://aka.ms/install-azd.sh | bash

# Initialize the project
azd init

# Authenticate to Azure
azd auth login

# Provision infrastructure and deploy
azd up
```

#### Configuration

When running `azd up`, you'll be prompted for:
- **Environment Name**: e.g., `dev`, `test`, `prod`
- **Azure Location**: e.g., `westus2`, `eastus`
- **Subscription**: Your Azure subscription

#### Subsequent Deployments

```bash
# Deploy code changes only
azd deploy

# Provision infrastructure changes
azd provision

# Full redeploy
azd up
```

### Option 2: Using GitHub Actions

The repository includes automated deployment workflows.

#### Setup Secrets

Configure these GitHub secrets in your repository settings:

```
AZURE_CLIENT_ID: <service-principal-client-id>
AZURE_TENANT_ID: <azure-tenant-id>
AZURE_SUBSCRIPTION_ID: <azure-subscription-id>
```

#### Create Service Principal

```bash
# Create service principal for GitHub Actions
az ad sp create-for-rbac \
  --name "github-puget-sound-marine-forecast" \
  --role contributor \
  --scopes /subscriptions/<SUBSCRIPTION_ID> \
  --sdk-auth

# Configure federated credentials for GitHub Actions
az ad app federated-credential create \
  --id <APP_ID> \
  --parameters '{
    "name": "github-deploy",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:longman391/puget-sound-marine-forecast:ref:refs/heads/main",
    "audiences": ["api://AzureADTokenExchange"]
  }'
```

#### Trigger Deployment

- **Automatic**: Push to `main` branch with changes to `infra/` directory
- **Manual**: Go to Actions → Infrastructure Deployment → Run workflow

### Option 3: Manual Azure Deployment

#### Step 1: Build and Push Container

```bash
# Build container
docker build -t puget-sound-marine-forecast:latest .

# Login to Azure Container Registry
az acr login --name <your-acr-name>

# Tag and push
docker tag puget-sound-marine-forecast:latest \
  <your-acr-name>.azurecr.io/puget-sound-marine-forecast:latest
docker push <your-acr-name>.azurecr.io/puget-sound-marine-forecast:latest
```

#### Step 2: Deploy Infrastructure

```bash
# Deploy using Bicep
az deployment sub create \
  --name psm-deployment \
  --location westus2 \
  --template-file infra/main.bicep \
  --parameters infra/main.parameters.json \
  --parameters environmentName=prod
```

#### Step 3: Deploy Container App

```bash
# Get outputs from infrastructure deployment
CONTAINER_APP_NAME=$(az deployment sub show \
  --name psm-deployment \
  --query properties.outputs.SERVICE_MARINE_FORECAST_API_NAME.value \
  -o tsv)

RESOURCE_GROUP=$(az deployment sub show \
  --name psm-deployment \
  --query properties.outputs.RESOURCE_GROUP_NAME.value \
  -o tsv)

# Update container app
az containerapp update \
  --name $CONTAINER_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --image <your-acr-name>.azurecr.io/puget-sound-marine-forecast:latest
```

## Environment Configuration

### Development Environment

```bash
# Use development configuration
cp .env.development .env

# Start locally
python src/main.py
```

### Test Environment

```bash
# Deploy to test environment
azd env select test
azd up
```

### Production Environment

```bash
# Deploy to production
azd env select prod
azd up
```

### Environment Variables

Each environment requires configuration of:

| Variable | Description | Example |
|----------|-------------|---------|
| `ENVIRONMENT` | Environment name | `production` |
| `ALLOWED_ORIGINS` | CORS origins | `https://yourdomain.com` |
| `ALLOWED_HOSTS` | Valid hosts | `yourdomain.com` |
| `LOG_LEVEL` | Logging level | `WARNING` |
| `CACHE_UPDATE_INTERVAL_MINUTES` | Cache refresh | `120` |

**Production Note**: Store sensitive configuration in Azure Key Vault, not in `.env` files.

## Infrastructure as Code

### Bicep Files

- **`infra/main.bicep`**: Main deployment template (subscription scope)
- **`infra/main-resources.bicep`**: Resource definitions
- **`infra/main.parameters.json`**: Environment-specific parameters

### Infrastructure Components

The Bicep templates create:

- **Resource Group**: Organized by environment
- **Container Registry**: For Docker images
- **Container Apps Environment**: Managed container runtime
- **Container App**: The API service
- **Log Analytics Workspace**: Monitoring and logs
- **Application Insights**: Telemetry and performance

### Validate Infrastructure

```bash
# Validate Bicep files
az bicep build --file infra/main.bicep
az bicep build --file infra/main-resources.bicep

# What-if analysis
az deployment sub what-if \
  --location westus2 \
  --template-file infra/main.bicep \
  --parameters infra/main.parameters.json
```

## CI/CD Automation

### GitHub Actions Workflows

- **`.github/workflows/ci.yml`**: Build, test, lint, security checks
- **`.github/workflows/infra-deploy.yml`**: Infrastructure deployment

### CI Pipeline

On every push/PR to `main`:
1. Type checking with mypy
2. Code linting with black and ruff
3. Security scanning (secrets, vulnerabilities)
4. Unit tests with 55% coverage requirement
5. Upload coverage to Codecov

### CD Pipeline

Infrastructure deployment triggered by:
- Manual workflow dispatch
- Changes to `infra/` directory
- Scheduled deployments (optional)

## Monitoring and Maintenance

### Health Checks

The API provides several monitoring endpoints:

- `GET /health`: Application health status
- `GET /cache/status`: Cache health and statistics
- `GET /`: API status and version

### Azure Monitoring

```bash
# View application logs
az containerapp logs show \
  --name <app-name> \
  --resource-group <rg-name> \
  --follow

# View metrics
az monitor metrics list \
  --resource <app-id> \
  --metric-names RequestCount,ResponseTime
```

### Application Insights

Configure Application Insights in `infra/main-resources.bicep` and view:
- Request rates and response times
- Dependency tracking (NOAA API calls)
- Exception tracking
- Custom metrics

### Maintenance Tasks

#### Update Dependencies

```bash
# Check for vulnerabilities
pip-audit

# Update dependencies
pip install --upgrade pip
pip list --outdated

# Update constraints.txt after testing
```

#### Rotate Secrets

```bash
# Update Azure secrets
az containerapp secret set \
  --name <app-name> \
  --resource-group <rg-name> \
  --secrets api-key=<new-value>
```

#### Scale Application

```bash
# Scale up
az containerapp update \
  --name <app-name> \
  --resource-group <rg-name> \
  --min-replicas 2 \
  --max-replicas 10
```

## Troubleshooting

### Common Issues

#### 1. Container Build Failures

```bash
# Test locally
docker build -t test .
docker run -p 8000:8000 test
```

#### 2. Deployment Failures

```bash
# Check deployment logs
az deployment sub show --name <deployment-name>

# Validate Bicep
az bicep build --file infra/main.bicep
```

#### 3. Runtime Errors

```bash
# Check container logs
az containerapp logs show --name <app-name> --follow

# Check environment variables
az containerapp show --name <app-name> --query properties.configuration.secrets
```

### Getting Help

- Review [Azure Container Apps documentation](https://learn.microsoft.com/azure/container-apps/)
- Check GitHub Issues
- Review application logs in Azure Portal

## Security Considerations

- ✅ Never commit secrets or credentials
- ✅ Use Azure Key Vault for production secrets
- ✅ Enable managed identity for Azure resources
- ✅ Configure network isolation (optional)
- ✅ Enable Azure DDoS protection
- ✅ Review and apply security recommendations from Azure Security Center

## Cost Optimization

- Use consumption-based pricing for Container Apps
- Configure auto-scaling based on load
- Use Azure Cost Management for monitoring
- Consider Azure Reserved Instances for production

---

**Last Updated**: 2024-02-09  
**Version**: 1.0.0
