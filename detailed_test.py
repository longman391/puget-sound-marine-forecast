"""
Detailed test to see full parsing results
"""

import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from scraper import ForecastScraper

async def detailed_test():
    """Test the forecast scraper with full output"""
    scraper = ForecastScraper()
    
    print("=== DETAILED FORECAST PARSING TEST ===")
    print("Fetching PZZ133 (San Juan Islands)...")
    
    try:
        # Test fetching and parsing
        forecast = await scraper.get_forecast("pzz133")
        
        print(f"\n✅ SUCCESSFULLY PARSED FORECAST")
        print(f"Zone: {forecast.zone}")
        print(f"Name: {forecast.name}")
        print(f"Issued: {forecast.issued}")
        print(f"Expires: {forecast.expires}")
        print(f"Number of periods: {len(forecast.periods)}")
        
        print(f"\n=== ALL FORECAST PERIODS ===")
        for i, period in enumerate(forecast.periods, 1):
            print(f"\n--- Period {i}: {period.name} ---")
            print(f"Wind: '{period.wind}'")
            print(f"Waves: '{period.waves}'")
            print(f"Weather: '{period.weather}'")
        
        # Also test PZZ135 (your other zone of interest)
        print(f"\n\n=== TESTING PZZ135 (Puget Sound) ===")
        forecast2 = await scraper.get_forecast("pzz135")
        print(f"Zone: {forecast2.zone}")
        print(f"Name: {forecast2.name}")
        print(f"Number of periods: {len(forecast2.periods)}")
        
        if forecast2.periods:
            period = forecast2.periods[0]
            print(f"\nFirst period: {period.name}")
            print(f"Wind: '{period.wind}'")
            print(f"Waves: '{period.waves}'")
            print(f"Weather: '{period.weather}'")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(detailed_test())
