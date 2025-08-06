"""
Test script to verify the API is working
"""

import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from scraper import ForecastScraper

async def test_scraper():
    """Test the forecast scraper"""
    scraper = ForecastScraper()
    
    print("Testing forecast scraper...")
    print("Fetching PZZ133 (San Juan Islands)...")
    
    try:
        # Test fetching raw text
        text = await scraper.fetch_zone_text("pzz133")
        print(f"✅ Successfully fetched {len(text)} characters of forecast text")
        print(f"First 200 characters: {text[:200]}...")
        
        # Test parsing
        forecast = await scraper.get_forecast("pzz133")
        print(f"✅ Successfully parsed forecast")
        print(f"Zone: {forecast.zone}")
        print(f"Name: {forecast.name}")
        print(f"Number of periods: {len(forecast.periods)}")
        
        if forecast.periods:
            print(f"First period: {forecast.periods[0].name}")
            print(f"Wind: {forecast.periods[0].wind}")
            print(f"Waves: {forecast.periods[0].waves}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_scraper())
