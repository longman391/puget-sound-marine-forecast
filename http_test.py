"""
Simple HTTP test for our API - Start the server manually first
"""

import asyncio
import httpx

async def test_api_endpoints():
    """Test the API endpoints via HTTP"""
    base_url = "http://127.0.0.1:8000"
    
    print("=== TESTING PUGET SOUND MARINE FORECAST API ===")
    print("Make sure to start the server first with:")
    print("python src/main.py")
    print()
    
    async with httpx.AsyncClient() as client:
        try:
            # Test the root endpoint
            print("1. Testing root endpoint...")
            response = await client.get(f"{base_url}/")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.json()}")
            
            # Test the zones endpoint
            print("\n2. Testing zones endpoint...")
            response = await client.get(f"{base_url}/zones")
            print(f"Status: {response.status_code}")
            zones = response.json()
            print(f"Number of zones: {len(zones['zones'])}")
            print(f"Available zones: {list(zones['zones'].keys())}")
            
            # Test a specific forecast
            print("\n3. Testing forecast endpoint for PZZ133...")
            response = await client.get(f"{base_url}/forecast/pzz133")
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                forecast = response.json()
                print(f"✅ Successfully got forecast for {forecast['zone']}")
                print(f"Zone name: {forecast['name']}")
                print(f"Number of periods: {len(forecast['periods'])}")
                
                if forecast['periods']:
                    period = forecast['periods'][0]
                    print(f"\nFirst period: {period['name']}")
                    print(f"Wind: {period['wind']}")
                    print(f"Waves: {period['waves']}")
                    print(f"Weather: {period['weather']}")
            else:
                print(f"❌ Error: {response.text}")
                
        except httpx.ConnectError:
            print("❌ Could not connect to the API server.")
            print("Please start the server first by running:")
            print("python src/main.py")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_api_endpoints())
