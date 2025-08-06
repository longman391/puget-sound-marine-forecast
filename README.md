# Puget Sound Marine Forecast API

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
- [ ] Deploy as Azure Container App (or similar serverless solution)
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

##  Data Source

- University of Washington Marine Weather Forecast via NOAA
- Text files updated regularly by UW meteorology department

##  Contributing

This is a learning project! Feel free to suggest improvements or contribute.

##  License

MIT License - see [LICENSE](LICENSE) file for details.
