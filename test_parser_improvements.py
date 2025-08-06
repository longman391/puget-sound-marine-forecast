"""
Test the improved parser via HTTP requests
Run this while the server is running on port 8000
"""

import asyncio
import httpx
import json

async def test_improved_api():
    """Test the improved parser via HTTP"""
    base_url = "http://127.0.0.1:8000"
    
    print("=== TESTING IMPROVED PARSER VIA HTTP ===")
    print("Server should be running on port 8000...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Test PZZ135 (Puget Sound) - this had parsing issues before
            print("\n" + "="*60)
            print("TESTING PZZ135 (Puget Sound and Hood Canal)")
            print("="*60)
            
            response = await client.get(f"{base_url}/forecast/pzz135")
            
            if response.status_code == 200:
                forecast = response.json()
                print(f"✅ SUCCESS! Zone: {forecast['zone']}")
                print(f"Name: {forecast['name']}")
                print(f"Issued: {forecast['issued']}")
                print(f"Expires: {forecast['expires']}")
                print(f"Periods: {len(forecast['periods'])}")
                
                # Analyze first 3 periods for improvements
                print(f"\nDETAILED ANALYSIS OF FIRST 3 PERIODS:")
                print("-" * 50)
                
                for i, period in enumerate(forecast['periods'][:3], 1):
                    print(f"\nPeriod {i}: {period['name']}")
                    print(f"  Wind:    '{period['wind']}'")
                    print(f"  Waves:   '{period['waves']}'")
                    print(f"  Weather: '{period['weather']}'")
                    
                    # Check for improvements
                    issues = []
                    if not period['wind']:
                        issues.append("Missing wind")
                    if not period['waves']:
                        issues.append("Missing waves")
                    if period['weather'] and period['weather'].lower().startswith('waves'):
                        issues.append("Waves in weather field")
                    if period['weather'] and period['weather'].endswith('of'):
                        issues.append("Truncated weather")
                    
                    if issues:
                        print(f"  Issues:  {', '.join(issues)}")
                    else:
                        print(f"  Status:  ✅ Clean parsing")
                
                # Summary stats
                total_periods = len(forecast['periods'])
                empty_wind = sum(1 for p in forecast['periods'] if not p['wind'])
                empty_waves = sum(1 for p in forecast['periods'] if not p['waves'])
                weather_issues = sum(1 for p in forecast['periods'] 
                                   if p['weather'] and (p['weather'].lower().startswith('waves') or p['weather'].endswith('of')))
                
                print(f"\nOVERALL QUALITY SUMMARY:")
                print(f"  Total periods: {total_periods}")
                print(f"  Missing wind: {empty_wind}/{total_periods}")
                print(f"  Missing waves: {empty_waves}/{total_periods}")
                print(f"  Weather issues: {weather_issues}/{total_periods}")
                
                if empty_wind == 0 and empty_waves <= 2 and weather_issues == 0:
                    print(f"  🎉 EXCELLENT PARSING QUALITY!")
                elif empty_waves <= total_periods // 2 and weather_issues <= 1:
                    print(f"  ✅ GOOD PARSING QUALITY")
                else:
                    print(f"  ⚠️  NEEDS MORE IMPROVEMENT")
                    
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"Response: {response.text}")
                
            # Also test PZZ133 for comparison
            print(f"\n" + "="*60)
            print("QUICK TEST: PZZ133 (San Juan Islands)")
            print("="*60)
            
            response = await client.get(f"{base_url}/forecast/pzz133")
            if response.status_code == 200:
                forecast = response.json()
                period = forecast['periods'][0] if forecast['periods'] else {}
                print(f"✅ Zone: {forecast['zone']}")
                print(f"First period wind: '{period.get('wind', '')}'")
                print(f"First period waves: '{period.get('waves', '')}'")
                print(f"First period weather: '{period.get('weather', '')}'")
            else:
                print(f"❌ Error: {response.status_code}")
                
        except httpx.ConnectError:
            print("❌ Cannot connect to API server")
            print("Make sure the server is running: python src/main.py")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_improved_api())
