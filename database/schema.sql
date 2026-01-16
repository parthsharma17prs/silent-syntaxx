-- Placement and Internship Management Portal Database Schema
-- MySQL Database

CREATE DATABASE IF NOT EXISTS placement_portal;
USE placement_portal;

-- Drop tables if they exist (for clean setup)
DROP TABLE IF EXISTS applications;
DROP TABLE IF EXISTS jobs;
DROP TABLE IF EXISTS announcements;
DROP TABLE IF EXISTS companies;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS users;

-- Users Table (Centralized Authentication)
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role_id TINYINT NOT NULL COMMENT '1=Student, 2=Company, 3=Admin',
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_role (role_id)
);

-- Students Table (Profile Details)
CREATE TABLE students (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    enrollment_number VARCHAR(50) UNIQUE NOT NULL,
    branch VARCHAR(100) NOT NULL,
    cgpa DECIMAL(3,2) NOT NULL,
    tenth_percentage DECIMAL(5,2),
    twelfth_percentage DECIMAL(5,2),
    graduation_year INT NOT NULL,
    phone VARCHAR(15),
    resume_url VARCHAR(500),
    skills TEXT,
    profile_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_cgpa (cgpa),
    INDEX idx_branch (branch)
);

-- Companies Table (Recruiter Profile)
CREATE TABLE companies (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT UNIQUE NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    industry VARCHAR(100),
    hr_name VARCHAR(255) NOT NULL,
    hr_phone VARCHAR(15),
    company_website VARCHAR(255),
    logo_url VARCHAR(500),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_company_name (company_name)
);

-- Jobs Table
CREATE TABLE jobs (
    id INT PRIMARY KEY AUTO_INCREMENT,
    company_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    job_type ENUM('Internship', 'Full-Time', 'Part-Time') NOT NULL,
    description TEXT NOT NULL,
    requirements TEXT,
    location VARCHAR(255),
    salary_range VARCHAR(100),
    min_cgpa DECIMAL(3,2) DEFAULT 0.00,
    min_10th_percentage DECIMAL(5,2) DEFAULT NULL,
    min_12th_percentage DECIMAL(5,2) DEFAULT NULL,
    eligible_branches TEXT COMMENT 'Comma-separated branch names',
    application_deadline DATE NOT NULL,
    status ENUM('Pending', 'Approved', 'Rejected', 'Closed') DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    INDEX idx_status (status),
    INDEX idx_deadline (application_deadline),
    INDEX idx_company (company_id)
);

-- Applications Table (Pivot Table)
CREATE TABLE applications (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    job_id INT NOT NULL,
    status ENUM('Applied', 'Shortlisted', 'Interview', 'Selected', 'Rejected') DEFAULT 'Applied',
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    notes TEXT COMMENT 'Interview feedback or notes',
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    UNIQUE KEY unique_application (student_id, job_id),
    INDEX idx_status (status),
    INDEX idx_student (student_id),
    INDEX idx_job (job_id)
);

-- Announcements Table (Admin Broadcasts)
CREATE TABLE announcements (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    target_role TINYINT COMMENT '1=Student, 2=Company, NULL=All',
    created_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_target (target_role)
);

-- Insert Default Admin User
-- Password: admin123 (hashed using Werkzeug security)
INSERT INTO users (email, password_hash, role_id, is_verified) VALUES
('admin@university.edu', 'pbkdf2:sha256:600000$samplehash$adminhash', 3, TRUE);

-- Insert Sample Student
INSERT INTO users (email, password_hash, role_id, is_verified) VALUES
('student@university.edu', 'pbkdf2:sha256:600000$samplehash$studenthash', 1, TRUE);

INSERT INTO students (user_id, full_name, enrollment_number, branch, cgpa, graduation_year, phone, profile_completed) VALUES
(2, 'John Doe', 'EN2024001', 'Computer Science', 8.5, 2026, '9876543210', TRUE);

-- Insert Sample Company
INSERT INTO users (email, password_hash, role_id, is_verified) VALUES
('company@tech.com', 'pbkdf2:sha256:600000$samplehash$companyhash', 2, TRUE);

INSERT INTO companies (user_id, company_name, industry, hr_name, hr_phone, company_website) VALUES
(3, 'TechCorp Solutions', 'Software Development', 'Jane Smith', '9876543211', 'https://techcorp.com');

-- Insert Sample Jobs
INSERT INTO jobs (company_id, title, job_type, description, requirements, location, salary_range, min_cgpa, eligible_branches, application_deadline, status) VALUES
(1, 'Software Engineering Intern', 'Internship', 'Join our team as a software engineering intern. Work on cutting-edge projects with experienced mentors.', 'Python, React, JavaScript basics', 'Bangalore', '₹30,000 - ₹50,000/month', 7.0, 'Computer Science,Information Technology', '2026-06-30', 'Approved'),
(1, 'Full Stack Developer', 'Full-Time', 'Looking for passionate full-stack developers to build scalable web applications.', 'React, Node.js, MongoDB, 2+ years experience', 'Remote', '₹8-12 LPA', 7.5, 'Computer Science,Information Technology,Electronics', '2026-07-15', 'Approved');

-- Insert Sample Application
INSERT INTO applications (student_id, job_id, status) VALUES
(1, 1, 'Applied');

-- Create Views for Analytics

-- Placement Statistics View
CREATE VIEW placement_stats AS
SELECT 
    COUNT(DISTINCT s.id) as total_students,
    COUNT(DISTINCT CASE WHEN a.status = 'Selected' THEN s.id END) as placed_students,
    COUNT(DISTINCT j.id) as total_jobs,
    COUNT(DISTINCT c.id) as total_companies
FROM students s
LEFT JOIN applications a ON s.id = a.student_id
LEFT JOIN jobs j ON j.status = 'Approved'
LEFT JOIN companies c ON c.user_id IN (SELECT id FROM users WHERE is_verified = TRUE);

-- Branch-wise Placement View
CREATE VIEW branch_placement AS
SELECT 
    s.branch,
    COUNT(DISTINCT s.id) as total_students,
    COUNT(DISTINCT CASE WHEN a.status = 'Selected' THEN s.id END) as placed_students,
    ROUND(COUNT(DISTINCT CASE WHEN a.status = 'Selected' THEN s.id END) * 100.0 / COUNT(DISTINCT s.id), 2) as placement_percentage
FROM students s
LEFT JOIN applications a ON s.id = a.student_id
GROUP BY s.branch;
