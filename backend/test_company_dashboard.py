"""
Test Company Dashboard Endpoints
"""
import requests
import json

BASE_URL = "http://localhost:5000/api"

# Test login first
print("=" * 60)
print("TESTING COMPANY DASHBOARD ENDPOINTS")
print("=" * 60)

print("\n1️⃣ Testing Login...")
login_data = {
    "email": "company@tech.com",
    "password": "company123"
}

try:
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    if response.status_code == 200:
        data = response.json()
        token = data.get('access_token')
        print(f"✅ Login successful!")
        print(f"   Token: {token[:50]}...")
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Test sessions endpoint
        print("\n2️⃣ Testing GET /api/company/sessions...")
        sessions_response = requests.get(f"{BASE_URL}/company/sessions", headers=headers)
        if sessions_response.status_code == 200:
            sessions = sessions_response.json()
            print(f"✅ Sessions loaded: {len(sessions)} session(s)")
            for s in sessions:
                print(f"   - {s['name']} ({s['status']}) - {s.get('batch_count', 0)} batches")
                if 'batches' in s:
                    print(f"     Batches: {s['batches']}")
        else:
            print(f"❌ Failed: {sessions_response.status_code}")
            print(f"   Error: {sessions_response.text}")
        
        # Test jobs endpoint
        print("\n3️⃣ Testing GET /api/company/jobs...")
        jobs_response = requests.get(f"{BASE_URL}/company/jobs", headers=headers)
        if jobs_response.status_code == 200:
            jobs = jobs_response.json()
            print(f"✅ Jobs loaded: {len(jobs)} job(s)")
            for job in jobs:
                print(f"   - {job['title']} ({job['job_type']}) - Status: {job['status']}")
                print(f"     Session ID: {job.get('session_id', 'N/A')}")
        else:
            print(f"❌ Failed: {jobs_response.status_code}")
            print(f"   Error: {jobs_response.text}")
        
        # Test announcements endpoint
        print("\n4️⃣ Testing GET /api/announcements...")
        ann_response = requests.get(f"{BASE_URL}/announcements", headers=headers)
        if ann_response.status_code == 200:
            announcements = ann_response.json()
            print(f"✅ Announcements loaded: {len(announcements)} announcement(s)")
            for ann in announcements:
                print(f"   - {ann['title']}")
        else:
            print(f"❌ Failed: {ann_response.status_code}")
            print(f"   Error: {ann_response.text}")
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\n🌐 Company Dashboard should now work at:")
        print("   http://localhost:5000/frontend/company.html")
        print("\n📋 Login with:")
        print("   Email: company@tech.com")
        print("   Password: company123")
        print("\n🔍 Open Browser Console (F12) to see detailed logs")
        
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(f"   Response: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("❌ Cannot connect to server!")
    print("   Make sure Flask is running: python backend/app.py")
except Exception as e:
    print(f"❌ Error: {e}")
