"""Check jobs in database"""
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

from app import app, db
from models import Job, Student, User

with app.app_context():
    jobs = Job.query.all()
    print(f'Total jobs: {len(jobs)}')
    for job in jobs:
        print(f'  ID: {job.id}, Title: {job.title}, Status: {job.status}, Min CGPA: {job.min_cgpa}')
    
    # Check student profile
    students = Student.query.join(User).filter(User.is_verified == False).all()
    print(f'\nUnverified students: {len(students)}')
    for s in students:
        print(f'  {s.full_name}, CGPA: {s.cgpa}, Branch: {s.branch}')
