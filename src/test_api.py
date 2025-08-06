"""
API Test Client - Test the FastAPI endpoints directly
"""

import asyncio
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from main import app

# Import TestClient correctly
try:
    from fastapi.testclient import TestClient
except ImportError:
    from starlette.testclient import TestClient

def test_api():
    """Test the API endpoints"""
    client = TestClient(app)
    
    print("=== TESTING PUGET SOUND MARINE FORECAST API ===")
    
    # Test the root endpoint
    print("\n1. Testing root endpoint...")
    response = client.get("/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test the zones endpoint
    print("\n2. Testing zones endpoint...")
    response = client.get("/zones")
    print(f"Status: {response.status_code}")
    zones = response.json()
    print(f"Number of zones: {len(zones['zones'])}")
    print(f"Available zones: {list(zones['zones'].keys())}")
    
    # Test a specific forecast
    print("\n3. Testing forecast endpoint for PZZ133...")
    response = client.get("/forecast/pzz133")
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
    
    # Test PZZ135 (your other zone of interest)
    print("\n4. Testing forecast endpoint for PZZ135...")
    response = client.get("/forecast/pzz135")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        forecast = response.json()
        print(f"✅ Successfully got forecast for {forecast['zone']}")
        print(f"Zone name: {forecast['name']}")
        if forecast['periods']:
            period = forecast['periods'][0]
            print(f"First period wind: {period['wind']}")
            print(f"First period waves: {period['waves']}")
    else:
        print(f"❌ Error: {response.text}")

if __name__ == "__main__":
    test_api()
