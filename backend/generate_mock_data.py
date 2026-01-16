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

# Sample data pools
first_names = ['Aarav', 'Vivaan', 'Aditya', 'Vihaan', 'Arjun', 'Sai', 'Arnav', 'Ayaan', 'Krishna', 'Ishaan',
               'Shaurya', 'Atharv', 'Advik', 'Pranav', 'Reyansh', 'Aaradhya', 'Ananya', 'Pari', 'Anika', 'Ira',
               'Diya', 'Anvi', 'Saanvi', 'Navya', 'Prisha', 'Kiara', 'Myra', 'Sara', 'Aanya', 'Aadhya',
               'Rohan', 'Kabir', 'Karan', 'Aryan', 'Rudra', 'Advait', 'Vedant', 'Rishi', 'Samar', 'Aayansh']

last_names = ['Sharma', 'Verma', 'Kumar', 'Singh', 'Patel', 'Reddy', 'Rao', 'Gupta', 'Agarwal', 'Jain',
              'Mishra', 'Pandey', 'Nair', 'Iyer', 'Bhat', 'Kulkarni', 'Deshmukh', 'Patil', 'Mehta', 'Shah',
              'Gandhi', 'Chopra', 'Malhotra', 'Kapoor', 'Khanna', 'Bansal', 'Jindal', 'Saxena', 'Thakur', 'Chauhan']

branches = ['Computer Science', 'Information Technology', 'Electronics and Communication', 
            'Mechanical Engineering', 'Electrical Engineering', 'Civil Engineering']

skills_pool = ['Python', 'Java', 'JavaScript', 'React', 'Node.js', 'Django', 'Flask', 'Angular', 'Vue.js',
               'MongoDB', 'MySQL', 'PostgreSQL', 'AWS', 'Azure', 'Docker', 'Kubernetes', 'Git', 'Machine Learning',
               'Deep Learning', 'Data Science', 'TensorFlow', 'PyTorch', 'C++', 'C', 'HTML', 'CSS', 'Bootstrap',
               'Tailwind', 'Express.js', 'Spring Boot', 'Microservices', 'REST API', 'GraphQL', 'Redis', 'Kafka']

companies_data = [
    ('TechVista Solutions', 'IT Services', 'Large (1000+)', 'Bangalore'),
    ('DataMinds Analytics', 'Data Science', 'Medium (250-1000)', 'Pune'),
    ('CloudWave Technologies', 'Cloud Computing', 'Large (1000+)', 'Hyderabad'),
    ('QuantumLeap AI', 'Artificial Intelligence', 'Medium (250-1000)', 'Bangalore'),
    ('NexGen Software', 'Software Development', 'Large (1000+)', 'Noida'),
    ('CyberShield Security', 'Cybersecurity', 'Medium (250-1000)', 'Mumbai'),
    ('InnovateLabs', 'Product Development', 'Medium (250-1000)', 'Chennai'),
    ('SmartCode Systems', 'IT Consulting', 'Large (1000+)', 'Gurgaon'),
    ('FinTech Innovators', 'Financial Technology', 'Medium (250-1000)', 'Mumbai'),
    ('EcomGrowth Ventures', 'E-commerce', 'Large (1000+)', 'Bangalore'),
    ('HealthTech Solutions', 'Healthcare IT', 'Medium (250-1000)', 'Pune'),
    ('EduLearn Platform', 'EdTech', 'Medium (250-1000)', 'Delhi'),
    ('AgriTech Dynamics', 'AgriTech', 'Small (50-250)', 'Bangalore'),
    ('GameZone Studios', 'Gaming', 'Medium (250-1000)', 'Hyderabad'),
    ('AutoDrive Systems', 'Automotive Tech', 'Large (1000+)', 'Pune'),
    ('SpaceVision Technologies', 'Aerospace', 'Medium (250-1000)', 'Bangalore'),
    ('GreenEnergy Solutions', 'Renewable Energy', 'Medium (250-1000)', 'Ahmedabad'),
    ('MediaWave Digital', 'Digital Marketing', 'Small (50-250)', 'Mumbai'),
    ('RoboTech Industries', 'Robotics', 'Medium (250-1000)', 'Chennai'),
    ('BlockChain Ventures', 'Blockchain', 'Small (50-250)', 'Bangalore')
]

job_titles = [
    'Software Engineer', 'Full Stack Developer', 'Backend Developer', 'Frontend Developer',
    'Data Scientist', 'Machine Learning Engineer', 'DevOps Engineer', 'Cloud Engineer',
    'Product Manager', 'Business Analyst', 'QA Engineer', 'Automation Engineer',
    'Mobile App Developer', 'UI/UX Designer', 'System Administrator', 'Network Engineer',
    'Data Analyst', 'AI Engineer', 'Security Analyst', 'Technical Support Engineer'
]

def generate_student_data(index):
    """Generate realistic student data"""
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    full_name = f"{first_name} {last_name}"
    email = f"{first_name.lower()}.{last_name.lower()}{index}{random.randint(100,999)}@university.edu"
    enrollment = f"2023{str(10000 + index).zfill(5)}"
    branch = random.choice(branches)
    cgpa = round(random.uniform(6.0, 9.8), 2)
    tenth = round(random.uniform(75.0, 98.0), 2)
    twelfth = round(random.uniform(70.0, 96.0), 2)
    grad_year = random.choice([2026, 2027, 2028])
    current_year = 2026 - grad_year + 4
    
    # Skills (3-8 skills per student)
    student_skills = random.sample(skills_pool, random.randint(3, 8))
    skills = ', '.join(student_skills)
    
    # Projects
    projects = f"Project 1: {random.choice(['E-commerce Platform', 'Social Media App', 'Chat Application', 'Portfolio Website'])} - Built using {random.choice(['MERN', 'Django', 'Flask', 'Spring Boot'])} stack\nProject 2: {random.choice(['Machine Learning Model', 'Data Analysis Dashboard', 'Mobile App', 'Game Development'])} - Implemented {random.choice(['Python', 'Java', 'JavaScript', 'C++'])}"
    
    # Experience
    has_experience = random.choice([True, False, False])  # 33% have experience
    experience = ""
    if has_experience:
        experience = f"{random.choice(['Software Development Intern', 'Web Developer Intern', 'Data Science Intern'])} at {random.choice(['TechCorp', 'StartupXYZ', 'InnovateLabs'])} ({random.randint(2, 6)} months)"
    
    # Certifications
    has_certs = random.choice([True, False, False])
    certifications = ""
    if has_certs:
        certs = random.sample(['AWS Certified', 'Google Cloud Certified', 'Microsoft Azure', 'Oracle Certified Java', 
                              'Python for Data Science', 'Machine Learning Specialization'], random.randint(1, 3))
        certifications = ', '.join(certs)
    
    phone = f"+91{random.randint(7000000000, 9999999999)}"
    linkedin = f"linkedin.com/in/{first_name.lower()}-{last_name.lower()}-{random.randint(100, 999)}"
    github = f"github.com/{first_name.lower()}{last_name.lower()}{random.randint(10, 99)}"
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

def generate_company_data(name, industry, size, location):
    """Generate company data"""
    company_email = f"hr@{name.lower().replace(' ', '')}.com"
    contact_person = f"{random.choice(first_names)} {random.choice(last_names)}"
    
    descriptions = {
        'IT Services': 'Leading IT services provider specializing in digital transformation and enterprise solutions.',
        'Data Science': 'Data analytics and business intelligence company helping organizations make data-driven decisions.',
        'Cloud Computing': 'Cloud infrastructure and platform services provider enabling scalable solutions.',
        'Artificial Intelligence': 'AI-first company building intelligent systems and automation solutions.',
        'Software Development': 'Full-service software development company creating innovative digital products.',
        'Cybersecurity': 'Cybersecurity solutions provider protecting businesses from digital threats.',
        'Product Development': 'Product innovation company building next-generation technology solutions.',
        'IT Consulting': 'Strategic IT consulting firm helping businesses optimize their technology investments.',
        'Financial Technology': 'FinTech company revolutionizing financial services through technology.',
        'E-commerce': 'E-commerce platform connecting buyers and sellers across the globe.',
        'Healthcare IT': 'Healthcare technology company improving patient care through digital solutions.',
        'EdTech': 'Educational technology platform making learning accessible and engaging.',
        'AgriTech': 'Agricultural technology company modernizing farming practices.',
        'Gaming': 'Game development studio creating immersive gaming experiences.',
        'Automotive Tech': 'Automotive technology company developing smart vehicle solutions.',
        'Aerospace': 'Aerospace technology company innovating in aviation and space exploration.',
        'Renewable Energy': 'Clean energy company developing sustainable power solutions.',
        'Digital Marketing': 'Digital marketing agency helping brands grow their online presence.',
        'Robotics': 'Robotics company building intelligent automation systems.',
        'Blockchain': 'Blockchain technology company creating decentralized solutions.'
    }
    
    return {
        'email': company_email,
        'company_name': name,
        'contact_person': contact_person,
        'company_description': descriptions.get(industry, 'Innovative technology company'),
        'company_size': size,
        'industry': industry,
        'headquarters_location': location,
        'hr_email': f"recruitment@{name.lower().replace(' ', '')}.com",
        'hr_phone': f"+91{random.randint(7000000000, 9999999999)}",
        'website': f"www.{name.lower().replace(' ', '')}.com"
    }

def generate_job_data(company_id, company_name, industry):
    """Generate job posting data"""
    job_title = random.choice(job_titles)
    
    min_cgpa = random.choice([6.0, 6.5, 7.0, 7.5, 8.0])
    salary_ranges = ['6-8 LPA', '8-12 LPA', '12-18 LPA', '18-25 LPA', '25-35 LPA']
    salary = random.choice(salary_ranges)
    
    job_type = random.choice(['Full-Time', 'Internship', 'Full-Time', 'Full-Time'])
    work_mode = random.choice(['On-site', 'Remote', 'Hybrid', 'Hybrid'])
    
    eligible_branches = random.sample(branches, random.randint(2, 4))
    branches_str = ', '.join(eligible_branches)
    
    requirements = f"Strong knowledge of {random.choice(skills_pool)}, {random.choice(skills_pool)}\nGood problem-solving skills\nExcellent communication abilities"
    
    location = random.choice(['Bangalore', 'Mumbai', 'Pune', 'Hyderabad', 'Delhi', 'Chennai', 'Gurgaon', 'Noida'])
    
    # Application deadline 30-90 days from now
    deadline = (datetime.now() + timedelta(days=random.randint(30, 90))).strftime('%Y-%m-%d')
    
    description = f"We are looking for a talented {job_title} to join our {industry} team. The role involves developing cutting-edge solutions and working with the latest technologies."
    
    return {
        'company_id': company_id,
        'job_title': job_title,
        'job_description': description,
        'requirements': requirements,
        'salary': salary,
        'location': location,
        'job_type': job_type,
        'work_mode': work_mode,
        'min_cgpa': min_cgpa,
        'eligible_branches': branches_str,
        'application_deadline': deadline,
        'session_id': 1,  # Default session
        'status': random.choice(['Approved', 'Approved', 'Approved', 'Closed'])
    }

def main():
    print("\n" + "="*70)
    print("GENERATING COMPREHENSIVE MOCK DATA")
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
        
        # Get batch IDs
        cursor.execute("SELECT id FROM batches")
        batch_ids = [row[0] for row in cursor.fetchall()]
        if not batch_ids:
            print("✗ No batches found. Please create batches first.")
            return
        
        # 1. Create 150 Students (or get existing ones)
        print("\n[1/5] Checking students...")
        cursor.execute("SELECT id FROM students")
        student_ids = [row[0] for row in cursor.fetchall()]
        
        if len(student_ids) >= 150:
            print(f"✓ Already have {len(student_ids)} students, skipping creation")
        else:
            students_to_create = 150 - len(student_ids)
            print(f"Creating {students_to_create} more students...")
            password_hash = generate_password_hash('student123')
            
            for i in range(len(student_ids) + 1, len(student_ids) + students_to_create + 1):
                student_data = generate_student_data(i)
                
                # Create user
                cursor.execute("""
                    INSERT INTO users (email, password_hash, role_id, is_verified)
                    VALUES (%s, %s, 1, TRUE)
                """, (student_data['email'], password_hash))
                user_id = cursor.lastrowid
                
                # Create student profile
                batch_id = random.choice(batch_ids)
                cursor.execute("""
                    INSERT INTO students (
                        user_id, full_name, enrollment_number, branch, cgpa, tenth_percentage,
                        twelfth_percentage, graduation_year, current_year, batch_id, phone, resume_url,
                        skills, experience, projects, certifications, linkedin_url, github_url,
                        profile_completed
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    user_id, student_data['full_name'], student_data['enrollment_number'],
                    student_data['branch'], student_data['cgpa'], student_data['tenth_percentage'],
                    student_data['twelfth_percentage'], student_data['graduation_year'],
                    student_data['current_year'], batch_id, student_data['phone'],
                    student_data['resume_url'], student_data['skills'], student_data['experience'],
                    student_data['projects'], student_data['certifications'], student_data['linkedin_url'],
                    student_data['github_url'], student_data['profile_completed']
                ))
                student_ids.append(cursor.lastrowid)
                
                if len(student_ids) % 30 == 0:
                    print(f"  Created {len(student_ids)} students...")
            
            conn.commit()
            print(f"✓ Successfully created students (Total: {len(student_ids)})")
        
        # 2. Create 20 Companies (or get existing ones)
        print("\n[2/5] Checking companies...")
        cursor.execute("SELECT id, company_name, industry FROM companies")
        company_results = cursor.fetchall()
        company_ids = [(row[0], row[1], row[2]) for row in company_results]
        
        if len(company_ids) >= 20:
            print(f"✓ Already have {len(company_ids)} companies, skipping creation")
        else:
            companies_to_create = 20 - len(company_ids)
            print(f"Creating {companies_to_create} more companies...")
            company_password = generate_password_hash('company123')
            
            for idx, (name, industry, size, location) in enumerate(companies_data[:companies_to_create], 1):
                company_data = generate_company_data(name, industry, size, location)
                
                # Create user
                cursor.execute("""
                    INSERT INTO users (email, password_hash, role_id, is_verified)
                    VALUES (%s, %s, 2, TRUE)
                """, (company_data['email'], company_password))
                user_id = cursor.lastrowid
                
                # Create company profile
                cursor.execute("""
                    INSERT INTO companies (
                        user_id, company_name, contact_person, company_description,
                        company_size, industry, headquarters_location, hr_email, hr_phone, hr_name, website
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    user_id, company_data['company_name'], company_data['contact_person'],
                    company_data['company_description'], company_data['company_size'],
                    company_data['industry'], company_data['headquarters_location'],
                    company_data['hr_email'], company_data['hr_phone'], company_data['contact_person'], company_data['website']
                ))
                company_ids.append((cursor.lastrowid, name, industry))
                
                if idx % 5 == 0:
                    print(f"  Created {idx} companies...")
            
            conn.commit()
            print(f"✓ Successfully created companies (Total: {len(company_ids)})")
        
        # 3. Create 80-100 Job Posts (4-5 per company)
        print("\n[3/5] Creating job posts...")
        job_ids = []
        job_count = 0
        
        for company_id, company_name, industry in company_ids:
            num_jobs = random.randint(3, 6)
            for _ in range(num_jobs):
                job_data = generate_job_data(company_id, company_name, industry)
                
                cursor.execute("""
                    INSERT INTO jobs (
                        company_id, title, description, requirements, salary_range, location,
                        job_type, work_mode, min_cgpa, eligible_branches, application_deadline,
                        session_id, status
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    job_data['company_id'], job_data['job_title'], job_data['job_description'],
                    job_data['requirements'], job_data['salary'], job_data['location'],
                    job_data['job_type'], job_data['work_mode'], job_data['min_cgpa'],
                    job_data['eligible_branches'], job_data['application_deadline'],
                    job_data['session_id'], job_data['status']
                ))
                job_ids.append(cursor.lastrowid)
                job_count += 1
        
        conn.commit()
        print(f"✓ Successfully created {job_count} job posts")
        
        # 4. Create Applications (each student applies to 2-8 jobs)
        print("\n[4/5] Creating job applications...")
        application_count = 0
        placed_students = set()
        
        statuses = ['Applied', 'Shortlisted', 'Rejected', 'Selected', 'Interview']
        status_weights = [40, 25, 20, 10, 5]  # Weighted distribution
        
        for student_id in student_ids:
            num_applications = random.randint(2, 8)
            student_jobs = random.sample(job_ids, min(num_applications, len(job_ids)))
            
            for job_id in student_jobs:
                status = random.choices(statuses, weights=status_weights)[0]
                
                # If student is already placed, don't place them again
                if status == 'Selected' and student_id in placed_students:
                    status = 'Shortlisted'
                elif status == 'Selected':
                    placed_students.add(student_id)
                
                ats_score = random.randint(55, 98) if random.random() > 0.2 else None
                notes = f"Application submitted with {random.choice(['strong', 'good', 'average'])} resume match"
                
                cursor.execute("""
                    INSERT INTO applications (
                        student_id, job_id, session_id, status, notes, ats_score
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                """, (student_id, job_id, 1, status, notes, ats_score))
                application_count += 1
            
            if student_id % 30 == 0:
                print(f"  Created applications for {student_id} students...")
        
        conn.commit()
        print(f"✓ Successfully created {application_count} applications")
        print(f"✓ {len(placed_students)} students placed")
        
        # 5. Create some notifications and company visits
        print("\n[5/5] Creating notifications...")
        
        # Create company visits (if table exists)
        try:
            for company_id, company_name, industry in random.sample(company_ids, min(10, len(company_ids))):
                visit_date = datetime.now() + timedelta(days=random.randint(5, 45))
                cursor.execute("""
                    INSERT INTO company_visits (
                        company_id, visit_date, visit_time, location, description,
                        recruitment_type, expected_ctc_range, status
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    company_id, visit_date.date(), '10:00:00', 'Campus Auditorium',
                    f"{company_name} campus recruitment drive",
                    random.choice(['Campus Drive', 'Walk-in']), '6-12 LPA', 'Scheduled'
                ))
            print("✓ Created company visits")
        except Exception as e:
            print(f"⚠ Skipped company visits (table may not exist): {str(e)[:50]}")
        
        # Create notifications for random students (if table exists)
        try:
            notification_types = ['application_update', 'job_match', 'company_visit', 'interview_schedule']
            for _ in range(100):
                student_id = random.choice(student_ids)
                notif_type = random.choice(notification_types)
                cursor.execute("""
                    INSERT INTO notifications (
                        student_id, type, title, message, is_read, priority
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    student_id, notif_type, f"New {notif_type.replace('_', ' ').title()}",
                    "You have a new update regarding your application.",
                    random.choice([True, False]), random.choice(['low', 'medium', 'high'])
                ))
            print("✓ Created notifications")
        except Exception as e:
            print(f"⚠ Skipped notifications (table may not exist): {str(e)[:50]}")
        
        conn.commit()
        
        # Print summary
        print("\n" + "="*70)
        print("MOCK DATA GENERATION COMPLETE!")
        print("="*70)
        print(f"\n📊 Summary:")
        print(f"  • Students: 150")
        print(f"  • Companies: 20")
        print(f"  • Job Posts: {job_count}")
        print(f"  • Applications: {application_count}")
        print(f"  • Students Placed: {len(placed_students)}")
        print(f"  • Company Visits: 10")
        print(f"  • Notifications: 100")
        print("\n✓ All data created successfully!")
        print("\n🔐 Login Credentials:")
        print("  Students: Any student email / password: student123")
        print("  Companies: Any company email / password: company123")
        print("  Example: aarav.sharma1@university.edu / student123\n")
        
        conn.close()
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
