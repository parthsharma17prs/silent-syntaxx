import pymysql
from werkzeug.security import generate_password_hash

# Database connection
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='jpassword',
    database='placement_portal',
    autocommit=True
)

cursor = conn.cursor()

# Generate password hashes
admin_hash = generate_password_hash('admin123')
student_hash = generate_password_hash('student123')
company_hash = generate_password_hash('company123')

print("Creating demo accounts...")

# Clear existing demo accounts
cursor.execute("DELETE FROM users WHERE email IN ('admin@university.edu', 'student@university.edu', 'company@tech.com')")

# Insert Admin User
cursor.execute("""
    INSERT INTO users (email, password_hash, role_id, is_verified) 
    VALUES (%s, %s, 3, TRUE)
""", ('admin@university.edu', admin_hash))
admin_user_id = cursor.lastrowid
print(f"✓ Admin account created: admin@university.edu / admin123")

# Insert Student User
cursor.execute("""
    INSERT INTO users (email, password_hash, role_id, is_verified) 
    VALUES (%s, %s, 1, TRUE)
""", ('student@university.edu', student_hash))
student_user_id = cursor.lastrowid

cursor.execute("""
    INSERT INTO students (user_id, full_name, enrollment_number, branch, cgpa, graduation_year, phone, profile_completed) 
    VALUES (%s, 'John Doe', 'EN2024001', 'Computer Science', 8.5, 2026, '9876543210', TRUE)
""", (student_user_id,))
print(f"✓ Student account created: student@university.edu / student123")

# Insert Company User
cursor.execute("""
    INSERT INTO users (email, password_hash, role_id, is_verified) 
    VALUES (%s, %s, 2, TRUE)
""", ('company@tech.com', company_hash))
company_user_id = cursor.lastrowid

cursor.execute("""
    INSERT INTO companies (user_id, company_name, industry, hr_name, hr_phone, company_website) 
    VALUES (%s, 'TechCorp Solutions', 'Software Development', 'Jane Smith', '9876543211', 'https://techcorp.com')
""", (company_user_id,))
company_id = cursor.lastrowid
print(f"✓ Company account created: company@tech.com / company123")

# Add sample jobs from the company
cursor.execute("""
    INSERT INTO jobs (company_id, title, job_type, description, requirements, location, salary_range, min_cgpa, eligible_branches, application_deadline, status) 
    VALUES 
    (%s, 'Software Engineering Intern', 'Internship', 'Join our team as a software engineering intern. Work on cutting-edge projects with experienced mentors.', 
     'Python, React, JavaScript basics', 'Bangalore', '₹30,000 - ₹50,000/month', 7.0, 'Computer Science,Information Technology', '2026-06-30', 'Approved'),
    (%s, 'Full Stack Developer', 'Full-Time', 'Looking for passionate full-stack developers to build scalable web applications.', 
     'React, Node.js, MongoDB, 2+ years experience', 'Remote', '₹8-12 LPA', 7.5, 'Computer Science,Information Technology,Electronics', '2026-07-15', 'Approved')
""", (company_id, company_id))
print(f"✓ Sample jobs created")

cursor.close()
conn.close()

print("\n✅ Demo accounts setup complete!")
print("\nLogin credentials:")
print("━" * 50)
print("Admin:   admin@university.edu / admin123")
print("Student: student@university.edu / student123")
print("Company: company@tech.com / company123")
print("━" * 50)
