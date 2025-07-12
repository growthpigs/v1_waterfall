"""
Test script to verify Supabase connection and basic operations.
Run this after setting up your .env file with real credentials.
"""

import asyncio
import os
from dotenv import load_dotenv
from datetime import datetime
from uuid import uuid4

# Load environment variables
load_dotenv()

# Import our components
from src.database.supabase_client import supabase_client
from src.database.repositories import CIASessionRepository
from src.database.models import CIASessionCreate


async def test_connection():
    """Test basic Supabase connection and operations."""
    print("Testing Supabase connection...")
    
    # Test 1: Basic connection
    try:
        connected = await supabase_client.test_connection()
        print(f"✅ Connection test: {'Success' if connected else 'Failed'}")
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return
    
    # Test 2: Health check
    try:
        health = await supabase_client.health_check()
        print(f"✅ Health check: {health}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    # Test 3: Create a test session
    try:
        repo = CIASessionRepository()
        test_client_id = uuid4()
        
        session_data = CIASessionCreate(
            url="https://test.example.com",
            company_name="Test Company",
            kpoi="Test Person",
            country="United States",
            testimonials_url="https://test.example.com/testimonials"
        )
        
        # Note: This will fail if tables don't exist yet
        # You need to run the migrations first
        session = await repo.create_session(session_data, test_client_id)
        print(f"✅ Created test session: {session.id}")
        
        # Clean up
        deleted = await repo.delete(session.id, test_client_id)
        print(f"✅ Cleaned up test session: {deleted}")
        
    except Exception as e:
        print(f"⚠️  Session operations not tested (tables may not exist): {e}")
        print("   Run the SQL migrations in Supabase first!")


def main():
    """Run the connection test."""
    print("=" * 50)
    print("Brand BOS CIA System - Supabase Connection Test")
    print("=" * 50)
    
    # Check if environment variables are set
    if not os.getenv("SUPABASE_URL"):
        print("❌ Error: SUPABASE_URL not set in .env file")
        print("   Please copy .env.example to .env and add your credentials")
        return
    
    if not os.getenv("SUPABASE_KEY"):
        print("❌ Error: SUPABASE_KEY not set in .env file")
        return
    
    print(f"URL: {os.getenv('SUPABASE_URL')}")
    print(f"Time: {datetime.now()}")
    print("-" * 50)
    
    # Run async test
    asyncio.run(test_connection())
    
    print("-" * 50)
    print("Test complete!")


if __name__ == "__main__":
    main()