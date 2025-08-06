"""
Test the improved parser
"""

import asyncio
import sys
import os
import json

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from scraper import ForecastScraper

async def test_improved_parser():
    """Test the improved forecast parser"""
    scraper = ForecastScraper()
    
    print("=== TESTING IMPROVED PARSER ===")
    
    # Test both of your key zones
    zones_to_test = ["pzz133", "pzz135"]
    
    for zone in zones_to_test:
        print(f"\n{'='*50}")
        print(f"TESTING ZONE: {zone.upper()}")
        print(f"{'='*50}")
        
        try:
            forecast = await scraper.get_forecast(zone)
            
            print(f"Zone: {forecast.zone}")
            print(f"Name: {forecast.name}")
            print(f"Issued: {forecast.issued}")
            print(f"Expires: {forecast.expires}")
            print(f"Periods: {len(forecast.periods)}")
            
            # Show first 3 periods in detail
            for i, period in enumerate(forecast.periods[:3], 1):
                print(f"\n--- Period {i}: {period.name} ---")
                print(f"Wind:    '{period.wind}'")
                print(f"Waves:   '{period.waves}'")
                print(f"Weather: '{period.weather}'")
            
            # Check for common issues
            empty_winds = sum(1 for p in forecast.periods if not p.wind)
            empty_waves = sum(1 for p in forecast.periods if not p.waves)
            empty_weather = sum(1 for p in forecast.periods if not p.weather)
            
            print(f"\nQuality Check:")
            print(f"Empty wind fields: {empty_winds}/{len(forecast.periods)}")
            print(f"Empty wave fields: {empty_waves}/{len(forecast.periods)}")
            print(f"Empty weather fields: {empty_weather}/{len(forecast.periods)}")
            
        except Exception as e:
            print(f"❌ Error testing {zone}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_improved_parser())
