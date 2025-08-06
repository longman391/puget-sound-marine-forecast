"""
Simple test to verify our setup
"""

import asyncio
import httpx

async def simple_test():
    print("Testing basic HTTP request...")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("https://tgftp.nws.noaa.gov/data/forecasts/marine/coastal/pz/pzz133.txt")
            print(f"✅ Successfully fetched forecast data")
            print(f"Status code: {response.status_code}")
            print(f"Content length: {len(response.text)} characters")
            print(f"First 300 characters:")
            print(response.text[:300])
            print("...")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(simple_test())
