import pymysql
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import random
from werkzeug.security import generate_password_hash

load_dotenv()

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'placement_portal')

# More diverse data pools
first_names = ['Aarav', 'Vivaan', 'Aditya', 'Vihaan', 'Arjun', 'Sai', 'Arnav', 'Ayaan', 'Krishna', 'Ishaan',
               'Shaurya', 'Atharv', 'Advik', 'Pranav', 'Reyansh', 'Aaradhya', 'Ananya', 'Pari', 'Anika', 'Ira',
               'Diya', 'Anvi', 'Saanvi', 'Navya', 'Prisha', 'Kiara', 'Myra', 'Sara', 'Aanya', 'Aadhya',
               'Rohan', 'Kabir', 'Karan', 'Aryan', 'Rudra', 'Advait', 'Vedant', 'Rishi', 'Samar', 'Aayansh',
               'Raj', 'Dev', 'Om', 'Dhruv', 'Yash', 'Ravi', 'Amit', 'Suresh', 'Priya', 'Sneha']

last_names = ['Sharma', 'Verma', 'Kumar', 'Singh', 'Patel', 'Reddy', 'Rao', 'Gupta', 'Agarwal', 'Jain',
              'Mishra', 'Pandey', 'Nair', 'Iyer', 'Bhat', 'Kulkarni', 'Deshmukh', 'Patil', 'Mehta', 'Shah']

# More balanced branch distribution
branches = [
    'Computer Science', 'Computer Science', 'Computer Science',  # 30% CS
    'Information Technology', 'Information Technology',  # 20% IT
    'Electronics and Communication', 'Electronics and Communication',  # 20% ECE
    'Mechanical Engineering',  # 10% Mech
    'Electrical Engineering',  # 10% EE
    'Civil Engineering'  # 10% Civil
]

skills_pool = ['Python', 'Java', 'JavaScript', 'React', 'Node.js', 'Django', 'Flask', 'Angular', 'Vue.js',
               'MongoDB', 'MySQL', 'PostgreSQL', 'AWS', 'Azure', 'Docker', 'Kubernetes', 'Git', 'Machine Learning',
               'Deep Learning', 'Data Science', 'TensorFlow', 'PyTorch', 'C++', 'C', 'HTML', 'CSS', 'Spring Boot']

companies_data = [
    ('TCS', 'IT Services', 'Large (1000+)', 'Mumbai'),
    ('Infosys', 'IT Consulting', 'Large (1000+)', 'Bangalore'),
    ('Wipro', 'Software Development', 'Large (1000+)', 'Bangalore'),
    ('Amazon', 'E-commerce', 'Large (1000+)', 'Bangalore'),
    ('Microsoft', 'Software', 'Large (1000+)', 'Hyderabad'),
    ('Google', 'Technology', 'Large (1000+)', 'Bangalore'),
    ('Adobe', 'Software', 'Large (1000+)', 'Bangalore'),
    ('Flipkart', 'E-commerce', 'Large (1000+)', 'Bangalore'),
    ('Accenture', 'IT Consulting', 'Large (1000+)', 'Bangalore'),
    ('Cognizant', 'IT Services', 'Large (1000+)', 'Chennai'),
    ('Oracle', 'Software', 'Large (1000+)', 'Bangalore'),
    ('SAP', 'Enterprise Software', 'Large (1000+)', 'Bangalore'),
    ('Deloitte', 'Consulting', 'Large (1000+)', 'Hyderabad'),
    ('Capgemini', 'IT Services', 'Large (1000+)', 'Mumbai'),
    ('Tech Mahindra', 'IT Services', 'Large (1000+)', 'Pune'),
    ('HCL Technologies', 'IT Services', 'Large (1000+)', 'Noida'),
    ('IBM', 'Technology', 'Large (1000+)', 'Bangalore'),
    ('Salesforce', 'Cloud Computing', 'Large (1000+)', 'Hyderabad'),
    ('PayPal', 'FinTech', 'Large (1000+)', 'Bangalore'),
    ('Myntra', 'E-commerce', 'Medium (250-1000)', 'Bangalore')
]

job_titles_by_role = {
    'SDE': ['Software Development Engineer', 'Software Engineer', 'Backend Developer', 'Frontend Developer', 'Full Stack Developer'],
    'Data': ['Data Scientist', 'Data Analyst', 'ML Engineer', 'AI Engineer'],
    'Support': ['System Engineer', 'Technical Support Engineer', 'IT Analyst', 'Associate Engineer'],
    'QA': ['QA Engineer', 'Test Engineer', 'Automation Engineer'],
    'Other': ['Product Manager', 'Business Analyst', 'DevOps Engineer', 'Cloud Engineer']
}

def clear_all_data(cursor):
    """Clear all existing mock data"""
    print("\nClearing existing data...")
    tables_to_clear = [
        'notifications', 'company_visits', 'interview_bookings', 
        'application_rounds', 'applications', 'jobs', 
        'companies', 'students', 'users'
    ]
    
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    for table in tables_to_clear:
        try:
            cursor.execute(f"DELETE FROM {table} WHERE id > 0")
            print(f"  ✓ Cleared {table}")
        except Exception as e:
            print(f"  ⚠ Skipped {table}: {str(e)[:50]}")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    print("✓ Data cleared\n")

def generate_student_data(index, branch):
    """Generate realistic student data"""
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    full_name = f"{first_name} {last_name}"
    email = f"{first_name.lower()}.{last_name.lower()}{index}@university.edu"
    enrollment = f"2024{str(10000 + index).zfill(5)}"
    
    # More realistic CGPA distribution
    cgpa_ranges = [(6.0, 7.0), (7.0, 8.0), (8.0, 9.0), (9.0, 9.5), (9.5, 10.0)]
    cgpa_weights = [15, 30, 35, 15, 5]  # Bell curve
    cgpa_range = random.choices(cgpa_ranges, weights=cgpa_weights)[0]
    cgpa = round(random.uniform(cgpa_range[0], cgpa_range[1]), 2)
    
    tenth = round(random.uniform(75.0, 98.0), 2)
    twelfth = round(random.uniform(70.0, 96.0), 2)
    grad_year = random.choice([2026, 2026, 2026, 2027, 2027, 2028])  # More 2026 students
    current_year = 2030 - grad_year
    
    # Skills based on branch
    if 'Computer' in branch or 'Information' in branch:
        skill_count = random.randint(4, 8)
    elif 'Electronics' in branch:
        skill_count = random.randint(3, 6)
    else:
        skill_count = random.randint(2, 5)
    
    student_skills = random.sample(skills_pool, min(skill_count, len(skills_pool)))
    skills = ', '.join(student_skills)
    
    projects = f"Project 1: {random.choice(['Web Application', 'Mobile App', 'IoT System', 'ML Model'])}\nProject 2: {random.choice(['Dashboard', 'E-commerce Site', 'Automation Tool'])}"
    
    has_experience = random.random() < 0.25  # 25% have internship experience
    experience = ""
    if has_experience:
        experience = f"Intern at {random.choice(['Tech Startup', 'IT Company', 'Research Lab'])} (3-6 months)"
    
    has_certs = random.random() < 0.30  # 30% have certifications
    certifications = ""
    if has_certs:
        certifications = random.choice(['AWS Certified', 'Google Cloud', 'Python Certified', 'Java Certified'])
    
    phone = f"+91{random.randint(7000000000, 9999999999)}"
    linkedin = f"linkedin.com/in/{first_name.lower()}-{last_name.lower()}"
    github = f"github.com/{first_name.lower()}{last_name.lower()}"
    resume_url = f"/uploads/resumes/{enrollment}_resume.pdf"
    
    return {
        'email': email,
        'full_name': full_name,
        'enrollment_number': enrollment,
        'branch': branch,
        'cgpa': cgpa,
        'tenth_percentage': tenth,
        'twelfth_percentage': twelfth,
        'graduation_year': grad_year,
        'current_year': current_year,
        'phone': phone,
        'skills': skills,
        'experience': experience,
        'projects': projects,
        'certifications': certifications,
        'linkedin_url': linkedin,
        'github_url': github,
        'resume_url': resume_url,
        'profile_completed': True
    }

def main():
    print("\n" + "="*70)
    print("GENERATING REALISTIC DIVERSE MOCK DATA (150 STUDENTS)")
    print("="*70)
    
    try:
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset='utf8mb4'
        )
        cursor = conn.cursor()
        
        # Clear existing data
        clear_all_data(cursor)
        conn.commit()
        
        # Get batch IDs
        cursor.execute("SELECT id FROM batches")
        batch_ids = [row[0] for row in cursor.fetchall()]
        if not batch_ids:
            cursor.execute("INSERT INTO batches (batch_code, start_year, end_year, degree, program, status) VALUES ('2022-2026', 2022, 2026, 'B.Tech', 'Engineering', 'Active')")
            batch_ids = [cursor.lastrowid]
        
        # 1. Create exactly 150 Students with diverse branches
        print("[1/5] Creating 150 diverse students...")
        student_ids = []
        password_hash = generate_password_hash('student123')
        
        for i in range(1, 151):
            branch = random.choice(branches)
            student_data = generate_student_data(i, branch)
            
            cursor.execute("INSERT INTO users (email, password_hash, role_id, is_verified) VALUES (%s, %s, 1, TRUE)",
                          (student_data['email'], password_hash))
            user_id = cursor.lastrowid
            
            batch_id = random.choice(batch_ids)
            cursor.execute("""
                INSERT INTO students (
                    user_id, full_name, enrollment_number, branch, cgpa, tenth_percentage,
                    twelfth_percentage, graduation_year, current_year, batch_id, phone, resume_url,
                    skills, experience, projects, certifications, linkedin_url, github_url, profile_completed
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (user_id, student_data['full_name'], student_data['enrollment_number'],
                  student_data['branch'], student_data['cgpa'], student_data['tenth_percentage'],
                  student_data['twelfth_percentage'], student_data['graduation_year'],
                  student_data['current_year'], batch_id, student_data['phone'],
                  student_data['resume_url'], student_data['skills'], student_data['experience'],
                  student_data['projects'], student_data['certifications'], student_data['linkedin_url'],
                  student_data['github_url'], student_data['profile_completed']))
            student_ids.append(cursor.lastrowid)
        
        conn.commit()
        print(f"✓ Created 150 students across all branches")
        
        # 2. Create 20 Companies
        print("\n[2/5] Creating 20 companies...")
        company_ids = []
        company_password = generate_password_hash('company123')
        
        for name, industry, size, location in companies_data:
            email = f"hr@{name.lower().replace(' ', '')}.com"
            cursor.execute("INSERT INTO users (email, password_hash, role_id, is_verified) VALUES (%s, %s, 2, TRUE)",
                          (email, company_password))
            user_id = cursor.lastrowid
            
            cursor.execute("""
                INSERT INTO companies (user_id, company_name, contact_person, company_size, 
                                     industry, headquarters_location, hr_name, hr_email, hr_phone)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (user_id, name, 'HR Manager', size, industry, location, 'HR Manager', email, f"+91{random.randint(7000000000, 9999999999)}"))
            company_ids.append((cursor.lastrowid, name))
        
        conn.commit()
        print(f"✓ Created 20 companies")
        
        # 3. Create 60-70 Job Posts (3-4 per company)
        print("\n[3/5] Creating job posts...")
        job_ids = []
        
        for company_id, company_name in company_ids:
            num_jobs = random.randint(3, 4)
            for _ in range(num_jobs):
                role_type = random.choices(['SDE', 'Data', 'Support', 'QA', 'Other'], 
                                          weights=[40, 15, 25, 10, 10])[0]
                title = random.choice(job_titles_by_role[role_type])
                
                salary_ranges = ['3.5-5 LPA', '5-7 LPA', '7-10 LPA', '10-15 LPA', '15-20 LPA']
                salary_weights = [30, 35, 20, 10, 5]
                salary = random.choices(salary_ranges, weights=salary_weights)[0]
                
                min_cgpa = random.choice([6.0, 6.5, 7.0, 7.5, 8.0])
                eligible_branches = ', '.join(random.sample(['Computer Science', 'Information Technology', 
                                                             'Electronics and Communication', 'Electrical Engineering'], 
                                                            random.randint(2, 4)))
                
                # Jobs posted over last 90 days
                deadline = (datetime.now() + timedelta(days=random.randint(10, 60))).strftime('%Y-%m-%d')
                
                cursor.execute("""
                    INSERT INTO jobs (company_id, title, description, requirements, salary_range, location,
                                    job_type, min_cgpa, eligible_branches, application_deadline, session_id, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1, 'Approved')
                """, (company_id, title, f"Looking for {title} with good technical skills", 
                      "Strong programming, Good communication", salary, 
                      random.choice(['Bangalore', 'Pune', 'Hyderabad', 'Mumbai', 'Chennai']),
                      random.choice(['Full-Time', 'Internship', 'Full-Time', 'Full-Time']),
                      min_cgpa, eligible_branches, deadline))
                job_ids.append(cursor.lastrowid)
        
        conn.commit()
        print(f"✓ Created {len(job_ids)} job posts")
        
        # 4. Create Applications with diverse statuses and timeline
        print("\n[4/5] Creating diverse job applications...")
        application_count = 0
        placed_students = set()
        
        # Status distribution for realistic scenario
        # Selected: 35-40%, Shortlisted: 25-30%, Interview: 15-20%, Rejected: 15-20%, Applied: remaining
        for student_id in student_ids:
            # Each student applies to 3-7 jobs
            num_applications = random.randint(3, 7)
            student_jobs = random.sample(job_ids, min(num_applications, len(job_ids)))
            
            for job_id in student_jobs:
                # Realistic status distribution
                if student_id in placed_students:
                    # Already placed students don't get selected again
                    status = random.choices(['Applied', 'Shortlisted', 'Interview', 'Rejected'], 
                                          weights=[30, 40, 20, 10])[0]
                else:
                    status = random.choices(['Applied', 'Shortlisted', 'Interview', 'Rejected', 'Selected'], 
                                          weights=[25, 30, 20, 15, 10])[0]
                    if status == 'Selected':
                        placed_students.add(student_id)
                
                ats_score = random.randint(60, 95) if random.random() > 0.3 else None
                notes = f"Application reviewed - {status.lower()}"
                
                cursor.execute("""
                    INSERT INTO applications (student_id, job_id, session_id, status, notes, ats_score)
                    VALUES (%s, %s, 1, %s, %s, %s)
                """, (student_id, job_id, status, notes, ats_score))
                application_count += 1
        
        conn.commit()
        print(f"✓ Created {application_count} applications")
        print(f"✓ {len(placed_students)} students placed ({round(len(placed_students)/150*100, 1)}%)")
        
        # 5. Create some interview rounds for shortlisted/interview status
        print("\n[5/5] Creating hiring rounds data...")
        cursor.execute("""
            SELECT id, job_id FROM applications 
            WHERE status IN ('Shortlisted', 'Interview', 'Selected') 
            LIMIT 100
        """)
        applications_for_rounds = cursor.fetchall()
        
        for app_id, job_id in applications_for_rounds:
            # Create hiring round if doesn't exist
            cursor.execute("SELECT id FROM hiring_rounds WHERE job_id = %s AND round_number = 1", (job_id,))
            result = cursor.fetchone()
            if not result:
                cursor.execute("""
                    INSERT INTO hiring_rounds (job_id, round_number, round_name, round_type, round_mode, status)
                    VALUES (%s, 1, 'Technical Round', 'Online', 'Interview', 'Active')
                """, (job_id,))
                round_id = cursor.lastrowid
            else:
                round_id = result[0]
            
            # Create application round
            cursor.execute("""
                INSERT INTO application_rounds (application_id, hiring_round_id, status, score)
                VALUES (%s, %s, %s, %s)
            """, (app_id, round_id, random.choice(['Passed', 'Pending', 'Completed']), 
                  random.randint(60, 95)))
        
        conn.commit()
        print("✓ Created hiring rounds data")
        
        # Print summary with branch distribution
        cursor.execute("SELECT branch, COUNT(*) as count FROM students GROUP BY branch")
        branch_dist = cursor.fetchall()
        
        cursor.execute("SELECT status, COUNT(*) as count FROM applications GROUP BY status")
        status_dist = cursor.fetchall()
        
        print("\n" + "="*70)
        print("REALISTIC MOCK DATA GENERATION COMPLETE!")
        print("="*70)
        print(f"\n📊 Summary:")
        print(f"  • Total Students: 150")
        print(f"  • Companies: 20")
        print(f"  • Job Posts: {len(job_ids)}")
        print(f"  • Applications: {application_count}")
        print(f"  • Students Placed: {len(placed_students)} ({round(len(placed_students)/150*100, 1)}%)")
        
        print(f"\n📚 Branch Distribution:")
        for branch, count in branch_dist:
            print(f"  • {branch}: {count} students ({round(count/150*100, 1)}%)")
        
        print(f"\n📋 Application Status Distribution:")
        for status, count in status_dist:
            print(f"  • {status}: {count} ({round(count/application_count*100, 1)}%)")
        
        print("\n🔐 Login Credentials:")
        print("  Students: student email / password: student123")
        print("  Companies: company email / password: company123\n")
        
        conn.close()
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
