"""
Quick test script to verify company endpoints are working
Run this to check if company dashboard APIs are functioning
"""

import requests
import json

BASE_URL = "http://localhost:5000/api"

def test_company_endpoints():
    print("🧪 Testing Company Dashboard Endpoints\n")
    print("=" * 50)
    
    # First, try to login with a company account
    print("\n1. Testing Login...")
    print("   Please ensure you have a company account created.")
    print("   If not, register at http://localhost:5000/frontend/register.html")
    
    # Test sessions endpoint (requires auth)
    print("\n2. Testing Sessions Endpoint...")
    print(f"   GET {BASE_URL}/company/sessions")
    print("   ⚠️  This requires authentication token")
    
    # Test jobs endpoint
    print("\n3. Testing Jobs Endpoint...")
    print(f"   GET {BASE_URL}/company/jobs")
    print("   ⚠️  This requires authentication token")
    
    # Test announcements endpoint
    print("\n4. Testing Announcements Endpoint...")
    print(f"   GET {BASE_URL}/announcements")
    
    print("\n" + "=" * 50)
    print("\n📋 To test with authentication:")
    print("1. Login at: http://localhost:5000/frontend/login.html")
    print("2. Open browser console (F12)")
    print("3. Type: localStorage.getItem('auth')")
    print("4. Copy the token value")
    print("5. Use it in API calls with header: Authorization: Bearer <token>")
    print("\n🌐 Or simply open the company dashboard:")
    print("   http://localhost:5000/frontend/company.html")
    print("   Check the browser console for debug logs")

if __name__ == '__main__':
    test_company_endpoints()
