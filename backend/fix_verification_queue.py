"""
Create verification records for existing unverified students
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

from app import app, db
from models import User, Student, StudentVerification

with app.app_context():
    # Find all unverified students without verification records
    unverified_students = db.session.query(Student).join(User).filter(
        User.is_verified == False,
        User.role_id == 1
    ).all()
    
    count = 0
    for student in unverified_students:
        # Check if verification record already exists
        existing = StudentVerification.query.filter_by(student_id=student.id).first()
        if not existing:
            verification = StudentVerification(
                student_id=student.id,
                status='Pending'
            )
            db.session.add(verification)
            count += 1
            print(f"Created verification record for: {student.full_name} ({student.user.email})")
    
    if count > 0:
        db.session.commit()
        print(f"\n✅ Created {count} verification records")
    else:
        print("No unverified students without verification records found")
