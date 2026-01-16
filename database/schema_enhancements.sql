-- ==================== ENHANCED STUDENT DASHBOARD SCHEMA ====================
-- New tables to support advanced features

-- Drop existing views and new tables if they exist
DROP VIEW IF EXISTS placement_stats;
DROP VIEW IF EXISTS branch_placement;
DROP TABLE IF EXISTS interview_experiences;
DROP TABLE IF EXISTS notifications;
DROP TABLE IF EXISTS resume_scores;
DROP TABLE IF EXISTS student_skill_assessments;
DROP TABLE IF EXISTS company_visits;

-- ==================== 1. COMPANY VISITS / DRIVE FEED ====================
CREATE TABLE company_visits (
    id INT PRIMARY KEY AUTO_INCREMENT,
    company_id INT NOT NULL,
    visit_date DATE NOT NULL,
    visit_time TIME,
    location VARCHAR(255),
    description TEXT,
    recruitment_type ENUM('Walk-in', 'Campus Drive', 'Online') DEFAULT 'Campus Drive',
    expected_ctc_range VARCHAR(100),
    eligibility_criteria TEXT,
    status ENUM('Scheduled', 'Ongoing', 'Completed', 'Cancelled') DEFAULT 'Scheduled',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
    INDEX idx_visit_date (visit_date),
    INDEX idx_status (status),
    INDEX idx_company (company_id)
);

-- ==================== 2. NOTIFICATIONS / ALERTS ====================
CREATE TABLE notifications (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    type ENUM('interview_schedule', 'application_update', 'job_match', 'company_visit', 'announcement', 'skill_alert') DEFAULT 'application_update',
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    related_entity_type VARCHAR(50) COMMENT 'e.g., application, job, interview, visit',
    related_entity_id INT,
    is_read BOOLEAN DEFAULT FALSE,
    priority ENUM('low', 'medium', 'high') DEFAULT 'medium',
    action_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    INDEX idx_student (student_id),
    INDEX idx_type (type),
    INDEX idx_is_read (is_read),
    INDEX idx_priority (priority),
    INDEX idx_created_at (created_at)
);

-- ==================== 3. INTERVIEW EXPERIENCES / REPOSITORY ====================
CREATE TABLE interview_experiences (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT,
    company_id INT,
    job_id INT,
    interview_round INT DEFAULT 1,
    interview_type ENUM('Online', 'Phone', 'In-Person', 'Group Discussion') DEFAULT 'Online',
    difficulty_level ENUM('Easy', 'Medium', 'Hard') DEFAULT 'Medium',
    duration_minutes INT,
    topics_covered TEXT COMMENT 'Comma-separated topics',
    experience_summary TEXT,
    questions_asked TEXT,
    tips_advice TEXT,
    outcome ENUM('Passed', 'Failed', 'Waiting') DEFAULT 'Waiting',
    rating INT COMMENT '1-5 star rating',
    is_public BOOLEAN DEFAULT TRUE COMMENT 'Visible to all students',
    interview_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE SET NULL,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE SET NULL,
    INDEX idx_company (company_id),
    INDEX idx_is_public (is_public),
    INDEX idx_difficulty (difficulty_level),
    INDEX idx_rating (rating)
);

-- ==================== 4. RESUME SCORE & ASSESSMENT ====================
CREATE TABLE resume_scores (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    job_id INT NOT NULL,
    resume_url VARCHAR(500),
    overall_match_percentage INT COMMENT '0-100 score',
    skills_match_percentage INT,
    experience_match_percentage INT,
    education_match_percentage INT,
    missing_keywords TEXT COMMENT 'JSON array of missing keywords',
    matched_keywords TEXT COMMENT 'JSON array of matched keywords',
    improvement_suggestions TEXT COMMENT 'JSON array of suggestions',
    assessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    UNIQUE KEY unique_resume_job (student_id, job_id),
    INDEX idx_match_score (overall_match_percentage),
    INDEX idx_student (student_id),
    INDEX idx_job (job_id)
);

-- ==================== 5. SKILL ASSESSMENTS & GAP ANALYSIS ====================
CREATE TABLE student_skill_assessments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    skill_name VARCHAR(100) NOT NULL,
    proficiency_level ENUM('Beginner', 'Intermediate', 'Advanced', 'Expert') DEFAULT 'Beginner',
    years_of_experience DECIMAL(3,1) DEFAULT 0,
    market_demand_level ENUM('Low', 'Medium', 'High', 'Critical') DEFAULT 'Medium',
    endorsements INT DEFAULT 0,
    assessment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    UNIQUE KEY unique_student_skill (student_id, skill_name),
    INDEX idx_student (student_id),
    INDEX idx_demand (market_demand_level),
    INDEX idx_proficiency (proficiency_level)
);

-- ==================== 6. APPLICATION EXTENDED FIELDS ====================
-- Alter existing applications table to add new columns
ALTER TABLE applications ADD COLUMN interview_date DATETIME DEFAULT NULL;
ALTER TABLE applications ADD COLUMN interview_location VARCHAR(255);
ALTER TABLE applications ADD COLUMN interview_type ENUM('Online', 'Phone', 'In-Person') DEFAULT 'Online';
ALTER TABLE applications ADD COLUMN resume_matched_score INT DEFAULT NULL;
ALTER TABLE applications ADD COLUMN feedback TEXT;

-- ==================== ANALYTICS VIEWS ====================

-- Updated Placement Statistics View
CREATE VIEW placement_stats AS
SELECT 
    COUNT(DISTINCT s.id) as total_students,
    COUNT(DISTINCT CASE WHEN a.status = 'Selected' THEN s.id END) as placed_students,
    COUNT(DISTINCT j.id) as total_jobs,
    COUNT(DISTINCT c.id) as total_companies,
    COUNT(DISTINCT cv.id) as scheduled_visits,
    ROUND(COUNT(DISTINCT CASE WHEN a.status = 'Selected' THEN s.id END) * 100.0 / COUNT(DISTINCT s.id), 2) as placement_percentage
FROM students s
LEFT JOIN applications a ON s.id = a.student_id AND a.status = 'Selected'
LEFT JOIN jobs j ON j.status = 'Approved'
LEFT JOIN companies c ON c.user_id IN (SELECT id FROM users WHERE is_verified = TRUE)
LEFT JOIN company_visits cv ON cv.status IN ('Scheduled', 'Ongoing');

-- Branch-wise Placement View
CREATE VIEW branch_placement AS
SELECT 
    s.branch,
    COUNT(DISTINCT s.id) as total_students,
    COUNT(DISTINCT CASE WHEN a.status = 'Selected' THEN s.id END) as placed_students,
    COUNT(DISTINCT CASE WHEN a.status = 'Shortlisted' THEN a.id END) as shortlisted_count,
    COUNT(DISTINCT CASE WHEN a.status = 'Interview' THEN a.id END) as interview_count,
    ROUND(COUNT(DISTINCT CASE WHEN a.status = 'Selected' THEN s.id END) * 100.0 / COUNT(DISTINCT s.id), 2) as placement_percentage
FROM students s
LEFT JOIN applications a ON s.id = a.student_id
GROUP BY s.branch;

-- Skill Demand Market View
CREATE VIEW skill_market_analysis AS
SELECT 
    skill_name,
    COUNT(DISTINCT student_id) as students_with_skill,
    AVG(CASE 
        WHEN proficiency_level = 'Beginner' THEN 1
        WHEN proficiency_level = 'Intermediate' THEN 2
        WHEN proficiency_level = 'Advanced' THEN 3
        WHEN proficiency_level = 'Expert' THEN 4
    END) as avg_proficiency_score,
    CASE 
        WHEN market_demand_level = 'Critical' THEN 1
        WHEN market_demand_level = 'High' THEN 2
        WHEN market_demand_level = 'Medium' THEN 3
        WHEN market_demand_level = 'Low' THEN 4
    END as market_priority,
    AVG(endorsements) as avg_endorsements
FROM student_skill_assessments
GROUP BY skill_name
ORDER BY market_priority, avg_endorsements DESC;

-- ==================== 7. APPLICATION ROUND PROGRESS ====================
-- Tracks each applicant's progress through configured hiring rounds
DROP TABLE IF EXISTS application_rounds;

CREATE TABLE application_rounds (
    id INT PRIMARY KEY AUTO_INCREMENT,
    application_id INT NOT NULL,
    hiring_round_id INT NOT NULL,
    status ENUM('Pending', 'Scheduled', 'Completed', 'Passed', 'Failed') DEFAULT 'Pending',
    score DECIMAL(5,2) NULL,
    feedback TEXT,
    completed_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE CASCADE,
    FOREIGN KEY (hiring_round_id) REFERENCES hiring_rounds(id) ON DELETE CASCADE,
    INDEX idx_app_round_app (application_id),
    INDEX idx_app_round_round (hiring_round_id)
);
