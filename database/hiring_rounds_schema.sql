-- ==================== HIRING ROUNDS MANAGEMENT SYSTEM ====================
-- Production-level schema for managing multi-round recruitment workflows

USE placement_portal;

-- Drop existing tables if they exist
DROP TABLE IF EXISTS round_candidate_progress;
DROP TABLE IF EXISTS hiring_rounds;

-- Hiring Rounds Table
-- Stores configuration for each round in the recruitment process
CREATE TABLE hiring_rounds (
    id INT PRIMARY KEY AUTO_INCREMENT,
    job_id INT NOT NULL,
    
    -- Round Configuration
    round_number INT NOT NULL COMMENT 'Sequence order of the round (1, 2, 3...)',
    round_name VARCHAR(255) NOT NULL COMMENT 'e.g., Online Assessment, Technical Interview',
    round_type ENUM('Online', 'Offline') NOT NULL DEFAULT 'Online',
    round_mode ENUM('MCQ', 'Coding', 'Interview', 'Group Discussion', 'Assignment', 'Case Study', 'Presentation', 'Other') NOT NULL,
    
    -- Round Details
    description TEXT COMMENT 'Detailed instructions for candidates',
    duration_minutes INT COMMENT 'Expected duration of the round',
    evaluation_criteria TEXT COMMENT 'JSON array of criteria: [{name, weightage, description}]',
    is_elimination_round BOOLEAN DEFAULT TRUE COMMENT 'Whether candidates are eliminated after this round',
    
    -- Scheduling & Logistics
    scheduled_date DATE COMMENT 'When this round is scheduled',
    scheduled_time TIME COMMENT 'Start time for the round',
    venue VARCHAR(500) COMMENT 'Physical location or online meeting link',
    
    -- Round Status & Metadata
    status ENUM('Draft', 'Active', 'Completed', 'Cancelled') DEFAULT 'Draft',
    min_passing_score DECIMAL(5,2) COMMENT 'Minimum score to pass (e.g., 60.00 for 60%)',
    max_score DECIMAL(5,2) DEFAULT 100.00 COMMENT 'Maximum achievable score',
    
    -- Additional Configuration (JSON)
    configuration JSON COMMENT 'Flexible field for round-specific settings',
    
    -- Audit Fields
    created_by INT COMMENT 'Company user who created this round',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Constraints
    FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
    INDEX idx_job_round (job_id, round_number),
    INDEX idx_status (status),
    INDEX idx_scheduled (scheduled_date, scheduled_time),
    UNIQUE KEY unique_job_round (job_id, round_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Stores hiring round configurations for jobs';

-- Round Candidate Progress Table
-- Tracks individual candidate progress through each round
CREATE TABLE round_candidate_progress (
    id INT PRIMARY KEY AUTO_INCREMENT,
    round_id INT NOT NULL,
    application_id INT NOT NULL,
    student_id INT NOT NULL,
    
    -- Progress Tracking
    status ENUM('Pending', 'Invited', 'In Progress', 'Completed', 'Passed', 'Failed', 'Absent', 'Disqualified') DEFAULT 'Pending',
    score DECIMAL(5,2) COMMENT 'Score achieved in this round',
    candidate_rank INT COMMENT 'Rank in this round (optional)',
    
    -- Detailed Evaluation
    evaluator_notes TEXT COMMENT 'Feedback from interviewer/evaluator',
    evaluation_metrics JSON COMMENT 'Detailed scores for each criterion',
    strengths TEXT COMMENT 'Candidate strengths observed',
    areas_of_improvement TEXT COMMENT 'Areas where candidate can improve',
    
    -- Timestamps
    invited_at TIMESTAMP NULL COMMENT 'When candidate was invited to this round',
    started_at TIMESTAMP NULL COMMENT 'When candidate started the round',
    completed_at TIMESTAMP NULL COMMENT 'When candidate completed the round',
    evaluated_at TIMESTAMP NULL COMMENT 'When evaluation was completed',
    
    -- Additional Data
    attempt_count INT DEFAULT 0 COMMENT 'Number of attempts (for retakes)',
    submission_data JSON COMMENT 'Stores test responses, code submissions, etc.',
    
    -- Audit Fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    -- Constraints
    FOREIGN KEY (round_id) REFERENCES hiring_rounds(id) ON DELETE CASCADE,
    FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    INDEX idx_round_candidate (round_id, student_id),
    INDEX idx_application (application_id),
    INDEX idx_status (status),
    INDEX idx_score (score),
    UNIQUE KEY unique_round_application (round_id, application_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Tracks candidate progress through each hiring round';

-- Create indexes for performance
CREATE INDEX idx_round_job_active ON hiring_rounds(job_id, status);
CREATE INDEX idx_progress_round_status ON round_candidate_progress(round_id, status);

-- View: Round Statistics
CREATE OR REPLACE VIEW round_statistics AS
SELECT 
    hr.id as round_id,
    hr.job_id,
    hr.round_number,
    hr.round_name,
    hr.status as round_status,
    COUNT(DISTINCT rcp.id) as total_candidates,
    COUNT(DISTINCT CASE WHEN rcp.status = 'Passed' THEN rcp.id END) as passed_count,
    COUNT(DISTINCT CASE WHEN rcp.status = 'Failed' THEN rcp.id END) as failed_count,
    COUNT(DISTINCT CASE WHEN rcp.status = 'Pending' THEN rcp.id END) as pending_count,
    COUNT(DISTINCT CASE WHEN rcp.status = 'Completed' THEN rcp.id END) as completed_count,
    AVG(rcp.score) as average_score,
    MAX(rcp.score) as highest_score,
    MIN(rcp.score) as lowest_score
FROM hiring_rounds hr
LEFT JOIN round_candidate_progress rcp ON hr.id = rcp.round_id
GROUP BY hr.id, hr.job_id, hr.round_number, hr.round_name, hr.status;

-- Insert sample data for testing
-- Note: This assumes job_id = 1 exists
INSERT INTO hiring_rounds (job_id, round_number, round_name, round_type, round_mode, description, duration_minutes, is_elimination_round, status) VALUES
(1, 1, 'Online Assessment', 'Online', 'MCQ', 'Multiple choice questions covering technical aptitude, logical reasoning, and domain knowledge.', 60, TRUE, 'Active'),
(1, 2, 'Coding Challenge', 'Online', 'Coding', 'Solve 3 algorithmic problems of varying difficulty levels.', 90, TRUE, 'Draft'),
(1, 3, 'Technical Interview', 'Offline', 'Interview', 'Face-to-face technical discussion covering data structures, algorithms, and system design.', 45, TRUE, 'Draft'),
(1, 4, 'HR Interview', 'Offline', 'Interview', 'Discussion about career goals, cultural fit, and compensation expectations.', 30, FALSE, 'Draft');

COMMIT;
