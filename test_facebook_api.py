#!/usr/bin/env python3
"""
Test script for Facebook API endpoints
"""
import requests
import json
from datetime import datetime

# Base URL for the API
BASE_URL = "http://127.0.0.1:8000/api"

def test_endpoints():
    """Test the Facebook API endpoints"""
    
    print("=" * 50)
    print("Testing Facebook API Endpoints")
    print("=" * 50)
    
    # Note: These endpoints require authentication
    # For testing purposes, you would need to:
    # 1. Create a user account
    # 2. Get a JWT token
    # 3. Include the token in the Authorization header
    
    endpoints = [
        "/facebook/post/",
        "/facebook/posts/",
        "/facebook/posts/?limit=3",
        "/facebook/saved-posts/",
    ]
    
    print("\nAvailable endpoints:")
    for endpoint in endpoints:
        print(f"  GET {BASE_URL}{endpoint}")
    
    print(f"\nAdditional endpoints:")
    print(f"  DELETE {BASE_URL}/facebook/clear-saved-posts/")
    print(f"  GET {BASE_URL}/facebook-posts/ (Django REST Framework ViewSet)")
    
    print("\n" + "=" * 50)
    print("Authentication Required")
    print("=" * 50)
    print("""
To test these endpoints, you need to:

1. Create a user account:
   POST /api/auth/register/
   {
       "username": "testuser",
       "email": "test@example.com",
       "password": "testpassword123"
   }

2. Login to get a token:
   POST /api/auth/login/
   {
       "username": "testuser",
       "password": "testpassword123"
   }

3. Use the token in requests:
   Authorization: Bearer <your_token>

Example curl commands:
   curl -H "Authorization: Bearer <token>" http://127.0.0.1:8000/api/facebook/post/
   curl -H "Authorization: Bearer <token>" http://127.0.0.1:8000/api/facebook/posts/
   curl -H "Authorization: Bearer <token>" http://127.0.0.1:8000/api/facebook/saved-posts/
""")
    
    print("\nData Flow:")
    print("1. JSON file contains data for testing (monitoring/data/facebook_data.json)")
    print("2. When API endpoints are called, data is loaded from JSON file")
    print("3. Data is saved to database (FacebookPost model)")
    print("4. Response is returned in Data365 format")
    print("5. Saved posts can be viewed via /facebook/saved-posts/")
    print("6. Later, the JSON loading will be replaced with actual Data365 API calls")

if __name__ == "__main__":
    test_endpoints()
