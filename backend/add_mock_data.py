import sys
import os
from datetime import datetime, timedelta
import random
from werkzeug.security import generate_password_hash

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, Student, Company, Job, Application, OfferLetter

# Mock data
COMPANY_NAMES = [
    "Tech Innovations Ltd", "Digital Solutions Inc", "Cloud Systems Corp",
    "Data Analytics Pro", "AI Dynamics", "Cyber Security Plus",
    "Software Architects", "Web Technologies", "Mobile Apps Co",
    "Enterprise Solutions", "Smart Systems Ltd", "Future Tech Inc",
    "Code Masters", "Innovation Labs", "Digital Transformation",
    "Tech Giants", "Startup Hub", "IT Services Global",
    "Product Development Co", "Engineering Solutions"
]

FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Arjun", "Sai", "Ishaan", "Rohan", "Aryan",
    "Krishna", "Dhruv", "Aadhya", "Ananya", "Diya", "Isha", "Kavya", "Kiara",
    "Mira", "Navya", "Saanvi", "Sara", "Anika", "Priya", "Riya", "Sneha",
    "Pooja", "Neha", "Raj", "Amit", "Rahul", "Karan", "Varun", "Nikhil"
]

LAST_NAMES = [
    "Sharma", "Patel", "Kumar", "Singh", "Gupta", "Mehta", "Reddy", "Rao",
    "Verma", "Joshi", "Iyer", "Nair", "Agarwal", "Kapoor", "Malhotra", "Desai",
    "Pandey", "Mishra", "Trivedi", "Shah"
]

BRANCHES = ["CSE", "IT", "ECE", "EEE", "MECH", "CIVIL"]
DEGREES = ["B.Tech"]
JOB_ROLES = [
    "Software Engineer", "Data Analyst", "Web Developer", "Full Stack Developer",
    "DevOps Engineer", "Cloud Engineer", "ML Engineer", "QA Engineer",
    "Frontend Developer", "Backend Developer", "Mobile Developer",
    "Data Scientist", "Business Analyst", "System Administrator"
]

def clear_existing_data():
    """Clear existing mock data"""
    print("Clearing existing data...")
    try:
        # Delete applications, jobs, students, companies with mock emails
        mock_users = User.query.filter(User.email.like('%mock%')).all()
        for user in mock_users:
            if user.student:
                Application.query.filter_by(student_id=user.student.id).delete()
            if user.company:
                jobs = Job.query.filter_by(company_id=user.company.id).all()
                for job in jobs:
                    Application.query.filter_by(job_id=job.id).delete()
                Job.query.filter_by(company_id=user.company.id).delete()
            db.session.delete(user)
        
        db.session.commit()
        print("✓ Existing mock data cleared")
    except Exception as e:
        db.session.rollback()
        print(f"Warning during cleanup: {e}")

def add_companies():
    """Add 20 mock companies"""
    print("\nAdding 20 companies...")
    companies = []
    
    # Pre-generate password hash once to speed up
    password_hash = generate_password_hash('company123')
    
    for i, name in enumerate(COMPANY_NAMES, 1):
        email = f"company{i}.mock@company.com"
        
        # Check if company user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user and existing_user.company:
            companies.append(existing_user.company)
            continue
        
        # Create user account for company
        user = User(
            email=email,
            role_id=2,  # Company role
            is_verified=True,
            password_hash=password_hash  # Use pre-generated hash
        )
        db.session.add(user)
        db.session.flush()
        
        # Create company profile
        company = Company(
            user_id=user.id,
            company_name=name,
            industry=random.choice(['IT', 'Software', 'Consulting', 'Manufacturing', 'Finance']),
            hr_name=f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}",
            hr_phone=f"+91{random.randint(7000000000, 9999999999)}",
            company_website=f"www.{name.lower().replace(' ', '')}.com",
            description=f"Leading company in the {random.choice(['technology', 'software', 'consulting', 'engineering'])} sector"
        )
        companies.append(company)
        db.session.add(company)
    
    db.session.commit()
    print(f"✓ Added {len(companies)} companies")
    return companies

def add_students():
    """Add 200 mock students"""
    print("\nAdding 200 students...")
    students = []
    
    # Pre-generate password hash once to speed up
    password_hash = generate_password_hash('student123')
    
    for i in range(1, 201):
        email = f"student{i}.mock@university.edu"
        
        # Check if student user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user and existing_user.student:
            students.append(existing_user.student)
            continue
        
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        branch = random.choice(BRANCHES)
        degree = random.choice(DEGREES)
        
        # Create user account
        user = User(
            email=email,
            role_id=1,  # Student role
            is_verified=True,
            password_hash=password_hash  # Use pre-generated hash
        )
        db.session.add(user)
        db.session.flush()
        
        # Calculate GPA and graduation year
        gpa = round(random.uniform(6.5, 9.8), 2)
        year = random.choice([2025, 2026, 2027, 2028])
        
        student = Student(
            user_id=user.id,
            full_name=f"{first_name} {last_name}",
            enrollment_number=f"EN{2020 + i % 5}{10000 + i}",
            branch=branch,
            cgpa=gpa,
            tenth_percentage=round(random.uniform(75.0, 95.0), 2),
            twelfth_percentage=round(random.uniform(75.0, 95.0), 2),
            graduation_year=year,
            phone=f"+91{random.randint(7000000000, 9999999999)}",
            batch_id=None,  # Don't assign batch_id for now
            skills=random.choice(['Python, Java, SQL', 'JavaScript, React, Node.js', 'C++, Data Structures', 'AWS, Docker, Kubernetes']),
            profile_completed=True
        )
        students.append(student)
        db.session.add(student)
        
        if i % 20 == 0:
            db.session.commit()
            print(f"  Added {i} students...")
    
    db.session.commit()
    print(f"✓ Added {len(students)} students")
    return students

def add_jobs(companies):
    """Add job postings for companies"""
    print("\nAdding job postings...")
    jobs = []
    
    for company in companies:
        # Each company posts 1-3 jobs
        num_jobs = random.randint(1, 3)
        for _ in range(num_jobs):
            role = random.choice(JOB_ROLES)
            package = random.randint(4, 20)
            min_cgpa = random.choice([6.0, 6.5, 7.0, 7.5])
            
            job = Job(
                company_id=company.id,
                title=role,
                description=f"Looking for talented {role} with strong technical skills",
                requirements=f"{random.randint(0, 2)} years experience, {random.choice(BRANCHES)} background preferred",
                location=random.choice(['Bangalore', 'Hyderabad', 'Pune', 'Mumbai', 'Remote']),
                job_type=random.choice(['Full-Time', 'Internship']),
                salary_range=f"{package}-{package+2} LPA",
                min_cgpa=min_cgpa,
                eligible_branches='["CSE", "IT", "ECE"]',
                min_10th_percentage=60.0,
                min_12th_percentage=60.0,
                application_deadline=(datetime.now() + timedelta(days=random.randint(10, 60))).date(),
                status='Approved',
                session_id=1
            )
            jobs.append(job)
            db.session.add(job)
    
    db.session.commit()
    print(f"✓ Added {len(jobs)} job postings")
    return jobs

def add_applications(students, jobs):
    """Add applications from students to jobs"""
    print("\nAdding job applications...")
    applications = []
    
    statuses = ['Applied', 'Shortlisted', 'Selected', 'Rejected', 'Interview']
    weights = [0.15, 0.25, 0.15, 0.25, 0.20]  # Probability weights
    
    # Each student applies to 2-8 jobs
    for student in students:
        num_applications = random.randint(2, 8)
        selected_jobs = random.sample(jobs, min(num_applications, len(jobs)))
        
        for job in selected_jobs:
            status = random.choices(statuses, weights=weights)[0]
            
            application = Application(
                student_id=student.id,
                job_id=job.id,
                status=status,
                applied_at=datetime.now() - timedelta(days=random.randint(1, 45)),
                session_id=1,
                notes=f"Application for {job.title}"
            )
            applications.append(application)
            db.session.add(application)
            
            if len(applications) % 100 == 0:
                db.session.commit()
                print(f"  Added {len(applications)} applications...")
    
    db.session.commit()
    print(f"✓ Added {len(applications)} applications")
    return applications


def add_offer_letters(applications):
    """Add offer letters for selected students"""
    print("\nAdding offer letters for selected students...")
    offer_letters = []
    
    # Get all selected applications
    selected_apps = [app for app in applications if app.status == 'Selected']
    
    # Keep track of students who already have an offer to avoid duplicates
    students_with_offers = set()
    
    for app in selected_apps:
        # Skip if student already has an offer (they can only have one placement)
        if app.student_id in students_with_offers:
            continue
            
        job = db.session.get(Job, app.job_id)
        if not job:
            continue
            
        # Generate package based on salary range
        package = random.randint(4, 25)  # LPA
        
        # Use direct SQL insert to avoid model/table mismatch
        from sqlalchemy import text
        
        insert_sql = text("""
            INSERT INTO offer_letters 
            (application_id, company_id, student_id, job_id, designation, ctc, annual_ctc, 
             job_location, joining_date, status, created_at, updated_at)
            VALUES 
            (:app_id, :company_id, :student_id, :job_id, :designation, :ctc, :annual_ctc,
             :job_location, :joining_date, :status, NOW(), NOW())
        """)
        
        db.session.execute(insert_sql, {
            'app_id': app.id,
            'company_id': job.company_id,
            'student_id': app.student_id,
            'job_id': job.id,
            'designation': job.title,
            'ctc': f"{package} LPA",
            'annual_ctc': package,
            'job_location': job.location or 'Bangalore',
            'joining_date': (datetime.now().date() + timedelta(days=random.randint(30, 180))),
            'status': random.choice(['Sent', 'Accepted'])
        })
        
        offer_letters.append(app.id)
        students_with_offers.add(app.student_id)
        
        if len(offer_letters) % 20 == 0:
            db.session.commit()
            print(f"  Added {len(offer_letters)} offer letters...")
    
    db.session.commit()
    print(f"✓ Added {len(offer_letters)} offer letters")
    return offer_letters

def main():
    with app.app_context():
        print("=" * 60)
        print("ADDING MOCK DATA TO DATABASE")
        print("=" * 60)
        
        # Clear existing mock data
        clear_existing_data()
        
        # Add companies
        companies = add_companies()
        
        # Add students
        students = add_students()
        
        # Add jobs
        jobs = add_jobs(companies)
        
        # Add applications
        applications = add_applications(students, jobs)
        
        # Add offer letters for selected students
        offer_letters = add_offer_letters(applications)
        
        print("\n" + "=" * 60)
        print("MOCK DATA SUMMARY")
        print("=" * 60)
        print(f"Companies: {len(companies)}")
        print(f"Students: {len(students)}")
        print(f"Jobs: {len(jobs)}")
        print(f"Applications: {len(applications)}")
        print(f"Offer Letters (Placed Students): {len(offer_letters)}")
        print("\nLogin Credentials:")
        print("  Companies: company1.mock@company.com to company20.mock@company.com")
        print("  Password: company123")
        print("  Students: student1.mock@university.edu to student200.mock@university.edu")
        print("  Password: student123")
        print("=" * 60)

if __name__ == '__main__':
    main()
