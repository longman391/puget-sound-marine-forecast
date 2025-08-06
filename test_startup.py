#!/usr/bin/env python3
"""
Simple test to check if the API can start without import errors
"""
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    print("Testing imports...")
    from main import app, limiter, scraper
    print("✅ All imports successful!")
    
    print("Testing FastAPI app creation...")
    print(f"✅ App created: {app.title}")
    
    print("Testing limiter...")
    print(f"✅ Rate limiter initialized: {type(limiter)}")
    
    print("Testing scraper...")
    print(f"✅ Scraper initialized: {type(scraper)}")
    
    print("\n🎉 API is ready to start!")
    print("You can now run: cd src && python main.py")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)
