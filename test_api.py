#!/usr/bin/env python3
"""
Simple test script to verify the BookIt API is working.
Run this after starting the server to test basic functionality.
"""

import asyncio
import httpx
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"

async def test_api():
    """Test basic API functionality."""
    async with httpx.AsyncClient() as client:
        print("🚀 Testing BookIt API...")
        
        # Test health check
        print("\n1. Testing health check...")
        response = await client.get(f"{BASE_URL}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        # Test root endpoint
        print("\n2. Testing root endpoint...")
        response = await client.get(f"{BASE_URL}/")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        # Test user registration
        print("\n3. Testing user registration...")
        user_data = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "testpassword123"
        }
        response = await client.post(f"{BASE_URL}/auth/register", json=user_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 201:
            print("   ✅ User registered successfully")
        else:
            print(f"   ❌ Registration failed: {response.text}")
            return
        
        # Test user login
        print("\n4. Testing user login...")
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        response = await client.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            token_data = response.json()
            print("   ✅ Login successful")
            access_token = token_data["access_token"]
            headers = {"Authorization": f"Bearer {access_token}"}
        else:
            print(f"   ❌ Login failed: {response.text}")
            return
        
        # Test getting user profile
        print("\n5. Testing user profile...")
        response = await client.get(f"{BASE_URL}/me", headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Profile retrieved successfully")
            print(f"   User: {response.json()}")
        else:
            print(f"   ❌ Profile retrieval failed: {response.text}")
        
        # Test getting services (should be empty initially)
        print("\n6. Testing services list...")
        response = await client.get(f"{BASE_URL}/services")
        print(f"   Status: {response.status_code}")
        print(f"   Services: {response.json()}")
        
        # Test creating a service (should fail - not admin)
        print("\n7. Testing service creation (should fail - not admin)...")
        service_data = {
            "title": "Test Service",
            "description": "A test service",
            "price": 50.0,
            "duration_minutes": 60,
            "is_active": True
        }
        response = await client.post(f"{BASE_URL}/services", json=service_data, headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 403:
            print("   ✅ Correctly denied service creation (not admin)")
        else:
            print(f"   ❌ Unexpected response: {response.text}")
        
        print("\n🎉 Basic API tests completed!")
        print("\nTo test admin functionality, you'll need to:")
        print("1. Create an admin user in the database")
        print("2. Or modify a user's role to 'admin'")
        print("3. Then test service creation and booking management")

if __name__ == "__main__":
    asyncio.run(test_api())
