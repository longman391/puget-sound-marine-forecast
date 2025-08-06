# Puget Sound Marine Forecast API

from fastapi import FastAPI, HTTPException
from typing import Dict, List, Optional
import httpx
from datetime import datetime
from scraper import ForecastScraper

app = FastAPI(
    title="Puget Sound Marine Forecast API",
    description="API for accessing Puget Sound marine weather forecasts",
    version="1.0.0"
)

# Initialize the forecast scraper
scraper = ForecastScraper()

# Available forecast zones
ZONES = {
    "pzz100": "Synopsis for Northern and Central Washington Coastal and Inland Waters",
    "pzz110": "Grays Harbor Bar",
    "pzz130": "West Entrance U.S. Waters Strait Of Juan De Fuca",
    "pzz131": "Central U.S. Waters Strait Of Juan De Fuca", 
    "pzz132": "East Entrance U.S. Waters Strait Of Juan De Fuca",
    "pzz133": "Northern Inland Waters Including The San Juan Islands",
    "pzz134": "Admiralty Inlet",
    "pzz135": "Puget Sound and Hood Canal",
    "pzz150": "Coastal Waters From Cape Flattery To James Island Out 10 Nm",
    "pzz153": "Coastal Waters From James Island To Point Grenville Out 10 Nm",
    "pzz156": "Coastal Waters From Point Grenville To Cape Shoalwater Out 10 Nm",
    "pzz170": "Coastal Waters From Cape Flattery To James Island 10 To 60 Nm",
    "pzz173": "Coastal Waters From James Island To Point Grenville 10 To 60 Nm",
    "pzz176": "Coastal Waters From Point Grenville To Cape Shoalwater 10 To 60 Nm"
}

@app.get("/")
async def root():
    """API status and information"""
    return {
        "message": "Puget Sound Marine Forecast API",
        "version": "1.0.0",
        "status": "active",
        "available_zones": len(ZONES)
    }

@app.get("/zones")
async def get_zones():
    """Get list of all available forecast zones"""
    return {"zones": ZONES}

@app.get("/forecast/{zone}")
async def get_forecast(zone: str):
    """Get forecast for a specific zone"""
    zone_lower = zone.lower()
    
    if zone_lower not in ZONES:
        raise HTTPException(
            status_code=404, 
            detail=f"Zone {zone} not found. Available zones: {list(ZONES.keys())}"
        )
    
    try:
        forecast = await scraper.get_forecast(zone_lower)
        
        # Convert to JSON-serializable format
        return {
            "zone": forecast.zone,
            "name": forecast.name,
            "issued": forecast.issued.isoformat(),
            "expires": forecast.expires.isoformat(),
            "periods": [
                {
                    "name": period.name,
                    "wind": period.wind,
                    "waves": period.waves,
                    "weather": period.weather
                }
                for period in forecast.periods
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching forecast for {zone}: {str(e)}"
        )

@app.get("/forecast/")
async def get_all_forecasts():
    """Get forecasts for all zones"""
    # TODO: Implement fetching all forecasts
    return {
        "message": "All forecasts endpoint - to be implemented",
        "zones": list(ZONES.keys())
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
