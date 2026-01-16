"""
Test Company Section - Comprehensive Check
"""
import sys
import os

# Fix encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.insert(0, os.path.dirname(__file__))

from app import app, db
from models import User, Company, Job, PlacementSession
from flask_jwt_extended import create_access_token

def test_company_endpoints():
    with app.app_context():
        print("=" * 60)
        print("Company Section Diagnostic Test")
        print("=" * 60)
        
        # 1. Check if a company user exists
        print("\n1. Checking for company users...")
        company_user = User.query.filter_by(role_id=2).first()
        if not company_user:
            print("   ❌ No company user found in database")
            print("   Creating a test company user...")
            
            # Create test company user
            user = User(email="test@company.com", role_id=2, is_verified=True)
            user.set_password("password123")
            db.session.add(user)
            db.session.flush()
            
            company = Company(
                user_id=user.id,
                company_name="Test Company",
                industry="Technology",
                hr_name="Test HR",
                hr_phone="1234567890"
            )
            db.session.add(company)
            db.session.commit()
            
            company_user = user
            print("   ✅ Created test company user: test@company.com / password123")
        else:
            print(f"   ✅ Found company user: {company_user.email}")
        
        # Generate JWT token
        token = create_access_token(identity=str(company_user.id))
        print(f"   🔑 JWT Token: {token[:50]}...")
        
        # 2. Check if sessions exist
        print("\n2. Checking for placement sessions...")
        sessions = PlacementSession.query.filter(
            PlacementSession.status.in_(['Active', 'Upcoming'])
        ).all()
        
        if not sessions:
            print("   ❌ No active/upcoming sessions found")
            print("   Creating a test session...")
            
            session = PlacementSession(
                name="2025-26 Placement Drive",
                start_year=2025,
                end_year=2026,
                status="Active",
                is_default=True
            )
            db.session.add(session)
            db.session.commit()
            
            print("   ✅ Created test session")
            sessions = [session]
        else:
            print(f"   ✅ Found {len(sessions)} sessions:")
            for s in sessions:
                print(f"      - {s.name} ({s.status})")
        
        # 3. Check company jobs
        print("\n3. Checking company jobs...")
        if company_user.company:
            jobs = Job.query.filter_by(company_id=company_user.company.id).all()
            print(f"   ✅ Found {len(jobs)} jobs for this company")
            for job in jobs:
                print(f"      - {job.title} ({job.status})")
        else:
            print("   ❌ No company profile found for this user")
        
        # 4. Test API endpoints using test client
        print("\n4. Testing API endpoints...")
        client = app.test_client()
        headers = {'Authorization': f'Bearer {token}'}
        
        # Test GET /api/company/jobs
        print("   Testing GET /api/company/jobs...")
        response = client.get('/api/company/jobs', headers=headers)
        print(f"      Status: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            print(f"      ✅ Response: {len(data) if isinstance(data, list) else 'OK'} jobs")
        else:
            print(f"      ❌ Error: {response.get_json()}")
        
        # Test GET /api/company/sessions
        print("   Testing GET /api/company/sessions...")
        response = client.get('/api/company/sessions', headers=headers)
        print(f"      Status: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            print(f"      ✅ Response: {len(data) if isinstance(data, list) else 'OK'} sessions")
        else:
            print(f"      ❌ Error: {response.get_json()}")
        
        # Test GET /api/company/profile
        print("   Testing GET /api/company/profile...")
        response = client.get('/api/company/profile', headers=headers)
        print(f"      Status: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            print(f"      ✅ Response: {data.get('company_name', 'OK')}")
        else:
            print(f"      ❌ Error: {response.get_json()}")
        
        print("\n" + "=" * 60)
        print("Summary:")
        print("=" * 60)
        print(f"Company User: {company_user.email}")
        print(f"JWT Token Generated: Yes")
        print(f"Sessions Available: {len(sessions)}")
        print(f"Jobs Posted: {len(jobs) if company_user.company else 0}")
        print("\n✅ All checks completed!")
        print("\nYou can now login with:")
        print(f"   Email: {company_user.email}")
        print(f"   Password: password123 (if test user) or your existing password")
        print("=" * 60)

if __name__ == '__main__':
    test_company_endpoints()
