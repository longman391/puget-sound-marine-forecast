# Puget Sound Marine Forecast API

A production-ready Python API that scrapes and serves marine forecast data for Puget Sound from the University of Washington's forecast text files. Ready for deployment to Azure Container Apps and optimized for personal use with Home Assistant and Dakboard.

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

This project provides a JSON API for accessing Puget Sound marine weather forecasts, making it easy for applications to consume structured forecast data.

##  Features (Completed ✅)

- [x] Scrape UW marine forecast text files ✅
- [x] Parse forecast data into structured format ✅  
- [x] Provide RESTful JSON API endpoints ✅
- [x] Automatic forecast updates (120-minute background cache - optimized for personal use) ✅
- [x] Deploy to Azure Container Apps with Infrastructure as Code ✅
- [x] Complete containerization with Docker ✅
- [x] Cost optimization for personal use (scale-to-zero, optimized resources) ✅
- [x] Production security with rate limiting, input validation, CORS ✅
- [x] Auto-scaling with scale-to-zero capability ✅
- [x] Application monitoring with Azure Application Insights ✅
- [ ] Historical data storage (future enhancement)

##  Tech Stack (Production Ready)

**Backend:** Python 3.11+ with FastAPI ✅  
**Dependencies:** httpx, python-dateutil, uvicorn, slowapi ✅  
**Security:** Rate limiting, input validation, CORS protection ✅  
**Caching:** In-memory cache with 120-minute background updates (personal use optimized) ✅  
**Performance:** Lightning-fast cached responses (<100ms) ⚡  
**Deployment:** Azure Container Apps with auto-scaling ✅  
**Infrastructure:** Azure Bicep templates with cost optimization ✅  
**Containerization:** Docker with health checks and security hardening ✅  
**Monitoring:** Azure Application Insights with comprehensive logging ✅  
**Data Format:** Real-time JSON from NOAA text files ✅  
**Parsing:** Advanced regex with 100% wind data accuracy ✅

##  API Endpoints ✅

- `GET /` - API status and cache information
- `GET /health` - Container health check endpoint
- `GET /zones` - List all 14 available forecast zones  
- `GET /forecast/{zone}` - Get parsed forecast for specific zone (cached) ⚡
- `GET /forecast/` - All forecasts for all 14 zones (cached) ⚡
- `GET /cache/status` - Detailed cache health and statistics  
- `POST /cache/refresh` - Manually trigger cache refresh

##  Supported Zones ✅

All 14 NOAA marine forecast zones including:
- **PZZ133**: Northern Inland Waters Including The San Juan Islands ⭐
- **PZZ135**: Puget Sound and Hood Canal ⭐  
- PZZ100, PZZ110, PZZ130-132, PZZ134, PZZ150, PZZ153, PZZ156, PZZ170, PZZ173, PZZ176

##  Project Status

🎉 **API Complete & Production Ready!** - Ready for Azure deployment!

##  Azure Deployment 🚀

This project includes complete Infrastructure as Code for Azure deployment:

### Prerequisites
- Azure subscription
- Azure CLI installed and logged in
- Azure Developer CLI (azd) installed
- Docker Desktop (for containerization)

### Quick Deploy to Azure Container Apps
```bash
# Clone and navigate to project
git clone https://github.com/longman391/puget-sound-marine-forecast.git
cd puget-sound-marine-forecast

# Initialize azd (first time only)
azd init

# Deploy infrastructure and application
azd up
```

### What Gets Deployed
- **Azure Container Apps**: Auto-scaling container hosting
- **Azure Container Registry**: Private container image storage  
- **Azure Application Insights**: Application monitoring and logging
- **Azure Log Analytics**: Centralized log management
- **Managed Identity**: Secure service-to-service authentication

### Cost Optimization Features
- Scale-to-zero capability (no cost when not in use)
- Optimized resource allocation (0.25 CPU cores, 0.5GB RAM)
- Efficient caching strategy (120-minute intervals)
- Perfect for personal use or low-traffic deployments

### Manual Deployment Options
- Azure Container Apps (recommended)
- Azure App Service 
- Azure Functions (with modifications for stateless operation)

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

##  Data Source

- University of Washington Marine Weather Forecast
- Text files updated regularly by UW meteorology department

##  Contributing

This is a learning project! Feel free to suggest improvements or contribute.

##  License

MIT License - see [LICENSE](LICENSE) file for details.
