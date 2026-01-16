"""
Quick database check to see what data exists for company dashboard
"""
import sys
sys.path.append('.')

from app import app, db
from models import PlacementSession, Job, Announcement, User, Company

with app.app_context():
    print("=" * 60)
    print("DATABASE STATUS CHECK")
    print("=" * 60)
    
    # Check sessions
    print("\n📅 PLACEMENT SESSIONS:")
    sessions = PlacementSession.query.all()
    if sessions:
        for s in sessions:
            print(f"  ✓ {s.name} ({s.status}) - ID: {s.id}")
            print(f"    Start: {s.start_date}, End: {s.end_date}")
    else:
        print("  ⚠️  No sessions found!")
    
    # Check active/upcoming sessions
    active_sessions = PlacementSession.query.filter(
        PlacementSession.status.in_(['Active', 'Upcoming'])
    ).all()
    print(f"\n  Active/Upcoming sessions: {len(active_sessions)}")
    
    # Check companies
    print("\n🏢 COMPANIES:")
    companies = Company.query.all()
    if companies:
        for c in companies:
            user = User.query.filter_by(id=c.user_id).first()
            print(f"  ✓ {c.company_name} - User: {user.email if user else 'N/A'}")
    else:
        print("  ⚠️  No companies found!")
    
    # Check jobs
    print("\n💼 JOBS:")
    jobs = Job.query.all()
    if jobs:
        for j in jobs:
            print(f"  ✓ {j.title} - {j.status} (Session: {j.session_id})")
    else:
        print("  ⚠️  No jobs found!")
    
    # Check announcements
    print("\n📢 ANNOUNCEMENTS:")
    announcements = Announcement.query.all()
    if announcements:
        for a in announcements:
            print(f"  ✓ {a.title} (Target role: {a.target_role})")
    else:
        print("  ⚠️  No announcements found!")
    
    print("\n" + "=" * 60)
    print("RECOMMENDATIONS:")
    print("=" * 60)
    
    if not active_sessions:
        print("⚠️  Create an Active placement session first!")
        print("   Use admin dashboard or run: python backend/init_db.py")
    
    if not companies:
        print("⚠️  Create a company account!")
        print("   Register at: http://localhost:5000/frontend/register.html")
    
    if not announcements:
        print("ℹ️  No announcements - this is optional")
    
    print("\n")
