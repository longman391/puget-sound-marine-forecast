# Puget Sound Marine Forecast API

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from typing import Dict, List, Optional
import httpx
import asyncio
import re
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
from scraper import ForecastScraper
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Initialize the forecast scraper
scraper = ForecastScraper()

# Input validation patterns
ZONE_PATTERN = re.compile(r'^pzz\d{3}$', re.IGNORECASE)

# In-memory cache for forecasts
forecast_cache = {}
cache_metadata = {
    "last_updated": None,
    "next_update": None,
    "update_interval_minutes": 120,  # Increased from 30 to 120 minutes for personal use
    "total_updates": 0,
    "last_update_duration": None
}

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

async def update_forecast_cache():
    """Update the forecast cache with data from NOAA"""
    start_time = datetime.now()
    print(f"[{start_time.strftime('%Y-%m-%d %H:%M:%S')}] Starting forecast cache update...")
    
    async def fetch_zone_forecast(zone: str):
        """Helper function to fetch a single zone's forecast"""
        try:
            forecast = await scraper.get_forecast(zone)
            return zone, {
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
            print(f"Error fetching forecast for {zone}: {str(e)}")
            return zone, {"error": f"Failed to fetch forecast: {str(e)}"}
    
    try:
        # Fetch all forecasts concurrently
        tasks = [fetch_zone_forecast(zone) for zone in ZONES.keys()]
        results = await asyncio.gather(*tasks)
        
        # Update cache
        new_cache = {}
        successful_count = 0
        failed_count = 0
        
        for zone, forecast_data in results:
            new_cache[zone] = forecast_data
            if "error" in forecast_data:
                failed_count += 1
            else:
                successful_count += 1
        
        # Update global cache and metadata
        global forecast_cache, cache_metadata
        forecast_cache = new_cache
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        cache_metadata.update({
            "last_updated": end_time.isoformat(),
            "next_update": (end_time + timedelta(minutes=cache_metadata["update_interval_minutes"])).isoformat(),
            "total_updates": cache_metadata["total_updates"] + 1,
            "last_update_duration": f"{duration:.2f} seconds"
        })
        
        print(f"[{end_time.strftime('%Y-%m-%d %H:%M:%S')}] Cache update completed: {successful_count} successful, {failed_count} failed, took {duration:.2f}s")
        
    except Exception as e:
        print(f"Error updating forecast cache: {str(e)}")

async def background_update_task():
    """Background task that updates forecasts every 30 minutes"""
    while True:
        try:
            await update_forecast_cache()
            # Wait 120 minutes before next update (optimized for personal use)
            await asyncio.sleep(cache_metadata["update_interval_minutes"] * 60)
        except Exception as e:
            print(f"Error in background update task: {str(e)}")
            # Wait 5 minutes before retrying on error
            await asyncio.sleep(5 * 60)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    # Startup
    print("Starting Puget Sound Marine Forecast API...")
    
    # Initial cache population
    await update_forecast_cache()
    
    # Start background update task
    task = asyncio.create_task(background_update_task())
    print("Background forecast update task started (updates every 120 minutes - optimized for personal use)")
    
    yield
    
    # Shutdown
    print("Shutting down Puget Sound Marine Forecast API...")
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        print("Background task cancelled")

app = FastAPI(
    title="Puget Sound Marine Forecast API",
    description="API for accessing Puget Sound marine weather forecasts",
    version="1.0.0",
    lifespan=lifespan
)

# Security middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware (restrict origins in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict to specific domains in production
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Add trusted host middleware (prevent host header attacks)
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["*"]  # TODO: Restrict to specific hosts in production
)

# Add rate limiting middleware
app.add_middleware(SlowAPIMiddleware)

# Custom error handler for better security
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler to prevent information leakage"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )

# Robots.txt to reduce 404s from crawlers
@app.get("/robots.txt", include_in_schema=False)
async def robots_txt():
    """Robots policy for crawlers."""
    rules = (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /cache/\n"
        "Disallow: /cache/status\n"
        "Disallow: /cache/refresh\n"
    )
    return PlainTextResponse(content=rules)

def validate_zone_input(zone: str) -> str:
    """Validate and sanitize zone input"""
    if not zone or not isinstance(zone, str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Zone parameter is required and must be a string"
        )
    
    zone_clean = zone.strip().lower()
    
    if not ZONE_PATTERN.match(zone_clean):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid zone format. Expected format: pzzXXX (e.g., pzz133)"
        )
    
    if zone_clean not in ZONES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Zone {zone_clean} not found. Available zones: {list(ZONES.keys())}"
        )
    
    return zone_clean

@app.get("/")
@limiter.limit("100/hour")  # Increased from 30/minute for personal use
async def root(request: Request):
    """API status and information"""
    try:
        return {
            "message": "Puget Sound Marine Forecast API",
            "version": "1.0.0",
            "status": "active",
            "available_zones": len(ZONES),
            "cache_status": {
                "cached_forecasts": len([f for f in forecast_cache.values() if "error" not in f]),
                "failed_forecasts": len([f for f in forecast_cache.values() if "error" in f]),
                "last_updated": cache_metadata["last_updated"],
                "next_update": cache_metadata["next_update"],
                "total_updates": cache_metadata["total_updates"],
                "update_interval": f"{cache_metadata['update_interval_minutes']} minutes"
            }
        }
    except Exception as e:
        logger.error(f"Error in root endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve API status"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint for container monitoring"""
    try:
        # Simple health check - verify cache is functioning
        healthy = len(forecast_cache) > 0 and cache_metadata.get("last_updated") is not None
        if healthy:
            return {"status": "healthy", "timestamp": datetime.now().isoformat()}
        else:
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={"status": "unhealthy", "reason": "cache not initialized"}
            )
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "unhealthy", "reason": "health check failed"}
        )

@app.get("/zones")
@limiter.limit("200/hour")  # Increased from 60/minute for personal use
async def get_zones(request: Request):
    """Get list of all available forecast zones"""
    try:
        return {"zones": ZONES}
    except Exception as e:
        logger.error(f"Error in zones endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve zones"
        )

@app.get("/forecast/{zone}")
@limiter.limit("500/hour")  # Increased for personal use
async def get_forecast(request: Request, zone: str):
    """Get forecast for a specific zone (served from cache)"""
    try:
        zone_clean = validate_zone_input(zone)
        
        # Check if we have cached data
        if zone_clean not in forecast_cache:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Forecast data for {zone_clean} not yet available. Cache is being updated."
            )
        
        cached_forecast = forecast_cache[zone_clean]
        
        # Check if cached data has an error
        if "error" in cached_forecast:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Forecast for {zone_clean} currently unavailable: {cached_forecast['error']}"
            )
        
        logger.info(f"Served forecast for zone {zone_clean}")
        return cached_forecast
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in forecast endpoint for zone {zone}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve forecast"
        )

@app.get("/forecast/")
@limiter.limit("200/hour")  # Increased for personal use
async def get_all_forecasts(request: Request):
    """Get forecasts for all zones (served from cache)"""
    try:
        if not forecast_cache:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Forecast data not yet available. Cache is being updated."
            )
        
        # Separate successful forecasts from errors
        successful_forecasts = []
        failed_zones = []
        
        for zone, forecast_data in forecast_cache.items():
            if "error" in forecast_data:
                failed_zones.append({"zone": zone, "error": forecast_data["error"]})
            else:
                successful_forecasts.append(forecast_data)
        
        logger.info(f"Served all forecasts: {len(successful_forecasts)} successful, {len(failed_zones)} failed")
        
        return {
            "total_zones": len(ZONES),
            "successful_forecasts": len(successful_forecasts),
            "failed_forecasts": len(failed_zones),
            "forecasts": successful_forecasts,
            "errors": failed_zones if failed_zones else None,
            "cache_info": {
                "last_updated": cache_metadata["last_updated"],
                "next_update": cache_metadata["next_update"],
                "data_served_from": "cache"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in all forecasts endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve forecasts"
        )

@app.get("/cache/status")
@limiter.limit("60/hour")  # Increased for personal use
async def get_cache_status(request: Request):
    """Get detailed cache status and statistics"""
    try:
        successful_zones = [zone for zone, data in forecast_cache.items() if "error" not in data]
        failed_zones = [zone for zone, data in forecast_cache.items() if "error" in data]
        
        return {
            "cache_metadata": cache_metadata,
            "zones_status": {
                "total_zones": len(ZONES),
                "successful_zones": len(successful_zones),
                "failed_zones": len(failed_zones),
                "successful_zone_list": successful_zones,
                "failed_zone_list": failed_zones
            },
            "cache_health": "healthy" if len(successful_zones) >= len(ZONES) * 0.8 else "degraded"
        }
    except Exception as e:
        logger.error(f"Error in cache status endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve cache status"
        )

@app.post("/cache/refresh")
@limiter.limit("10/hour")  # Relaxed for personal use but still controlled
async def refresh_cache(request: Request):
    """Manually trigger a cache refresh (useful for testing)"""
    try:
        logger.info("Manual cache refresh triggered")
        await update_forecast_cache()
        return {
            "message": "Cache refresh completed",
            "last_updated": cache_metadata["last_updated"],
            "successful_forecasts": len([f for f in forecast_cache.values() if "error" not in f])
        }
    except Exception as e:
        logger.error(f"Error in cache refresh endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error refreshing cache"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
