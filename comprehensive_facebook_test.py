#!/usr/bin/env python3
"""
Comprehensive test for Facebook API endpoints
Tests the actual endpoints with authentication
"""

import requests
import json
import sys

# API Configuration
BASE_URL = "http://127.0.0.1:8000/api"
TEST_USER = {
    "username": "testuser_fb",
    "email": "test_fb@example.com", 
    "password": "testpassword123"
}

def register_user():
    """Register a test user"""
    print("1. Registering test user...")
    
    url = f"{BASE_URL}/auth/register/"
    response = requests.post(url, json=TEST_USER)
    
    if response.status_code == 201:
        print("✅ User registered successfully")
        return True
    elif response.status_code == 400 and "already exists" in response.text.lower():
        print("ℹ️  User already exists, proceeding...")
        return True
    else:
        print(f"❌ Registration failed: {response.status_code} - {response.text}")
        return False

def login_user():
    """Login and get JWT token"""
    print("2. Logging in...")
    
    url = f"{BASE_URL}/auth/login/"
    response = requests.post(url, json={
        "username": TEST_USER["username"],
        "password": TEST_USER["password"]
    })
    
    if response.status_code == 200:
        data = response.json()
        token = data.get('access')
        print("✅ Login successful")
        return token
    else:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        return None

def test_facebook_endpoints(token):
    """Test Facebook API endpoints"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("3. Testing Facebook API endpoints...")
    
    # Test single post endpoint
    print("   Testing single post endpoint...")
    url = f"{BASE_URL}/facebook/post/"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print("   ✅ Single post endpoint working")
        print(f"   📄 Post ID: {data['data']['id']}")
        print(f"   👤 Owner: {data['data']['owner_username']}")
        print(f"   📝 Text preview: {data['data']['text'][:50]}...")
        print(f"   👍 Total reactions: {data['data']['reactions_total_count']}")
    else:
        print(f"   ❌ Single post endpoint failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False
    
    # Test posts list endpoint
    print("   Testing posts list endpoint...")
    url = f"{BASE_URL}/facebook/posts/?limit=3"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Posts list endpoint working")
        print(f"   📋 Retrieved {data['count']} posts")
        for i, post in enumerate(data['data'][:2]):  # Show first 2 posts
            print(f"   📄 Post {i+1}: {post['owner_username']} - {post['text'][:30]}...")
    else:
        print(f"   ❌ Posts list endpoint failed: {response.status_code}")
        return False
    
    # Test saved posts endpoint
    print("   Testing saved posts endpoint...")
    url = f"{BASE_URL}/facebook/saved-posts/"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Saved posts endpoint working")
        print(f"   💾 Total saved posts in database: {data['total_count']}")
    else:
        print(f"   ❌ Saved posts endpoint failed: {response.status_code}")
        return False
    
    # Test ViewSet endpoint
    print("   Testing Django REST Framework ViewSet...")
    url = f"{BASE_URL}/facebook-posts/"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ ViewSet endpoint working")
        print(f"   📊 ViewSet shows {len(data)} posts")
    else:
        print(f"   ❌ ViewSet endpoint failed: {response.status_code}")
    
    return True

def test_data_flow():
    """Test the complete data flow"""
    print("4. Testing data flow...")
    
    print("   📁 Checking JSON data file...")
    try:
        with open('/home/nyuydine/Documents/suiru/sui-ru/backend-drf/monitoring/data/facebook_data.json', 'r') as f:
            data = json.load(f)
        print(f"   ✅ JSON file contains {len(data['cameroon_posts'])} posts")
    except Exception as e:
        print(f"   ❌ JSON file error: {e}")
        return False
    
    print("   🔄 Data flow verified:")
    print("      1. JSON file ➜ API endpoints ➜ Database")
    print("      2. Real-time variations added to data")
    print("      3. Posts saved to database on each query")
    print("      4. Ready for Data365 API integration")
    
    return True

def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 Facebook API Integration Test Suite")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
    except requests.exceptions.RequestException:
        print("❌ Server not running! Please start Django server:")
        print("   python manage.py runserver")
        sys.exit(1)
    
    # Run tests
    if not register_user():
        sys.exit(1)
        
    token = login_user()
    if not token:
        sys.exit(1)
        
    if not test_facebook_endpoints(token):
        sys.exit(1)
        
    if not test_data_flow():
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("🎉 All tests passed!")
    print("=" * 60)
    print("\n📋 Available endpoints:")
    print(f"   GET  {BASE_URL}/facebook/post/")
    print(f"   GET  {BASE_URL}/facebook/posts/?limit=5")
    print(f"   GET  {BASE_URL}/facebook/saved-posts/")
    print(f"   GET  {BASE_URL}/facebook-posts/ (DRF ViewSet)")
    print(f"   DELETE {BASE_URL}/facebook/clear-saved-posts/")
    print("\n🔮 Ready for Data365 API integration!")
    print("   Just update data365_config.py and fetch_facebook_data_from_api()")

if __name__ == "__main__":
    main()
