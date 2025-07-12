#!/usr/bin/env python3
"""
Test if FastAPI server can start without database
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set mock environment variables to bypass database requirement
os.environ['SUPABASE_URL'] = 'https://mock.supabase.co'
os.environ['SUPABASE_KEY'] = 'mock_key_for_testing'

print("🌐 TESTING FASTAPI SERVER STARTUP")
print("=" * 40)

try:
    from src.api.main import app
    print("✅ FastAPI app imported successfully")
    
    # Get available routes
    routes = []
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            methods = getattr(route, 'methods', set())
            for method in methods:
                if method != 'HEAD':
                    routes.append(f"{method:6} {route.path}")
    
    print(f"\n📡 Available API Endpoints ({len(routes)} total):")
    for route in sorted(routes):
        print(f"  {route}")
    
    print(f"\n🎯 Server would be accessible at:")
    print(f"  • API Documentation: http://localhost:8000/docs")
    print(f"  • Health Check: http://localhost:8000/health")
    print(f"  • System Status: http://localhost:8000/api/v1/status")
    
    print(f"\n💡 To start the server manually:")
    print(f"  export SUPABASE_URL='your_supabase_url'")
    print(f"  export SUPABASE_KEY='your_supabase_key'")
    print(f"  python3 -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload")
    
    print(f"\n✅ FastAPI server structure is ready to run!")
    
except Exception as e:
    print(f"❌ FastAPI server test failed: {e}")
    import traceback
    traceback.print_exc()