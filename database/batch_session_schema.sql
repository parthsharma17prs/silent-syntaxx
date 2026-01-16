-- Batch and Placement Session Schema
-- Purpose: Enable year-wise and session-wise data segregation
-- Date: January 4, 2026

-- =====================================================
-- 1. PLACEMENT SESSIONS TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS placement_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    start_year INT NOT NULL,
    end_year INT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status ENUM('Active', 'Upcoming', 'Archived') DEFAULT 'Active',
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_status (status),
    INDEX idx_years (start_year, end_year)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================
-- 2. BATCHES TABLE
-- =====================================================
CREATE TABLE IF NOT EXISTS batches (
    id INT AUTO_INCREMENT PRIMARY KEY,
    batch_code VARCHAR(50) NOT NULL UNIQUE,
    start_year INT NOT NULL,
    end_year INT NOT NULL,
    degree VARCHAR(100) NOT NULL,
    program VARCHAR(100),
    description TEXT,
    status ENUM('Active', 'Graduated', 'Archived') DEFAULT 'Active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_years (start_year, end_year),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================
-- 3. BATCH-SESSION MAPPING (Many-to-Many)
-- =====================================================
CREATE TABLE IF NOT EXISTS batch_session_mapping (
    id INT AUTO_INCREMENT PRIMARY KEY,
    batch_id INT NOT NULL,
    session_id INT NOT NULL,
    is_eligible BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (batch_id) REFERENCES batches(id) ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES placement_sessions(id) ON DELETE CASCADE,
    UNIQUE KEY unique_batch_session (batch_id, session_id),
    INDEX idx_batch (batch_id),
    INDEX idx_session (session_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =====================================================
-- 4. ALTER EXISTING TABLES - BACKWARD COMPATIBLE
-- =====================================================

-- Add batch_id to students table
ALTER TABLE students 
ADD COLUMN batch_id INT NULL AFTER graduation_year,
ADD FOREIGN KEY (batch_id) REFERENCES batches(id) ON DELETE SET NULL,
ADD INDEX idx_batch (batch_id);

-- Add session_id to jobs table
ALTER TABLE jobs 
ADD COLUMN session_id INT NULL AFTER application_deadline,
ADD FOREIGN KEY (session_id) REFERENCES placement_sessions(id) ON DELETE SET NULL,
ADD INDEX idx_session (session_id);

-- Add session_id to applications table (for audit and filtering)
ALTER TABLE applications 
ADD COLUMN session_id INT NULL AFTER job_id,
ADD FOREIGN KEY (session_id) REFERENCES placement_sessions(id) ON DELETE SET NULL,
ADD INDEX idx_session (session_id);

-- =====================================================
-- 5. CREATE DEFAULT SESSION (MIGRATION SAFETY)
-- =====================================================
INSERT INTO placement_sessions (name, description, start_year, end_year, start_date, end_date, status, is_default)
VALUES ('Legacy Session', 'Default session for existing data migration', 2023, 2024, '2023-07-01', '2024-06-30', 'Active', TRUE)
ON DUPLICATE KEY UPDATE id=id;

-- =====================================================
-- 6. CREATE DEFAULT BATCHES
-- =====================================================
INSERT INTO batches (batch_code, start_year, end_year, degree, program, status) VALUES
('2021-2025', 2021, 2025, 'B.Tech', 'Computer Science', 'Graduated'),
('2022-2026', 2022, 2026, 'B.Tech', 'Computer Science', 'Active'),
('2023-2027', 2023, 2027, 'B.Tech', 'Computer Science', 'Active'),
('2024-2028', 2024, 2028, 'B.Tech', 'Computer Science', 'Active')
ON DUPLICATE KEY UPDATE id=id;

-- =====================================================
-- 7. MIGRATE EXISTING DATA
-- =====================================================

-- Get the default session ID
SET @default_session_id = (SELECT id FROM placement_sessions WHERE is_default = TRUE LIMIT 1);

-- Map students to batches based on graduation year
UPDATE students s
JOIN batches b ON b.end_year = s.graduation_year
SET s.batch_id = b.id
WHERE s.batch_id IS NULL;

-- For students without matching batch, create a generic batch
INSERT INTO batches (batch_code, start_year, end_year, degree, program, status)
SELECT DISTINCT 
    CONCAT(graduation_year - 4, '-', graduation_year) as batch_code,
    graduation_year - 4 as start_year,
    graduation_year as end_year,
    'B.Tech' as degree,
    'General' as program,
    CASE 
        WHEN graduation_year <= YEAR(CURDATE()) THEN 'Graduated'
        ELSE 'Active'
    END as status
FROM students
WHERE batch_id IS NULL AND graduation_year IS NOT NULL
ON DUPLICATE KEY UPDATE id=id;

-- Re-map any remaining students
UPDATE students s
JOIN batches b ON b.end_year = s.graduation_year
SET s.batch_id = b.id
WHERE s.batch_id IS NULL AND s.graduation_year IS NOT NULL;

-- Map all existing jobs to default session
UPDATE jobs 
SET session_id = @default_session_id 
WHERE session_id IS NULL;

-- Map all existing applications to default session
UPDATE applications 
SET session_id = @default_session_id 
WHERE session_id IS NULL;

-- Map all batches to default session
INSERT INTO batch_session_mapping (batch_id, session_id, is_eligible)
SELECT b.id, @default_session_id, TRUE
FROM batches b
WHERE NOT EXISTS (
    SELECT 1 FROM batch_session_mapping bsm 
    WHERE bsm.batch_id = b.id AND bsm.session_id = @default_session_id
);

-- =====================================================
-- 8. ADD AUDIT COLUMNS
-- =====================================================
ALTER TABLE placement_sessions 
ADD COLUMN created_by INT NULL AFTER status,
ADD FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL;

-- =====================================================
-- 9. CREATE VIEWS FOR EASY QUERYING
-- =====================================================

-- View: Active sessions with batch count
CREATE OR REPLACE VIEW v_active_sessions AS
SELECT 
    ps.id,
    ps.name,
    ps.start_year,
    ps.end_year,
    ps.status,
    COUNT(DISTINCT bsm.batch_id) as batch_count,
    COUNT(DISTINCT j.id) as job_count
FROM placement_sessions ps
LEFT JOIN batch_session_mapping bsm ON ps.id = bsm.session_id
LEFT JOIN jobs j ON ps.id = j.session_id
WHERE ps.status = 'Active'
GROUP BY ps.id, ps.name, ps.start_year, ps.end_year, ps.status;

-- View: Student batch details
CREATE OR REPLACE VIEW v_student_batches AS
SELECT 
    s.id as student_id,
    s.full_name,
    s.enrollment_number,
    b.id as batch_id,
    b.batch_code,
    b.start_year,
    b.end_year,
    b.degree,
    b.program,
    b.status as batch_status
FROM students s
LEFT JOIN batches b ON s.batch_id = b.id;

-- =====================================================
-- 10. VALIDATION QUERIES
-- =====================================================

-- Check students without batch assignment
SELECT COUNT(*) as students_without_batch FROM students WHERE batch_id IS NULL;

-- Check jobs without session assignment
SELECT COUNT(*) as jobs_without_session FROM jobs WHERE session_id IS NULL;

-- Check applications without session assignment
SELECT COUNT(*) as applications_without_session FROM applications WHERE session_id IS NULL;

-- Display session summary
SELECT 
    ps.name,
    ps.status,
    COUNT(DISTINCT j.id) as total_jobs,
    COUNT(DISTINCT a.id) as total_applications,
    COUNT(DISTINCT bsm.batch_id) as eligible_batches
FROM placement_sessions ps
LEFT JOIN jobs j ON ps.id = j.session_id
LEFT JOIN applications a ON ps.id = a.session_id
LEFT JOIN batch_session_mapping bsm ON ps.id = bsm.session_id
GROUP BY ps.id, ps.name, ps.status;
