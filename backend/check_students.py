#!/usr/bin/env python3
"""Check student data in database"""
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask
from models import db, Student, Job

load_dotenv(Path(__file__).parent / '.env')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT', 3306)}/{os.getenv('DB_NAME')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    print("=== Students ===")
    students = Student.query.all()
    for s in students:
        print(f"ID: {s.id}, Branch: '{s.branch}', CGPA: {s.cgpa}")
    
    print("\n=== Jobs ===")
    jobs = Job.query.filter_by(status='Approved').all()
    for j in jobs:
        print(f"ID: {j.id}, Title: '{j.title}', Eligible Branches: '{j.eligible_branches}', Min CGPA: {j.min_cgpa}")
