-- Update existing hiring_rounds table with new columns for production features
USE placement_portal;

-- Add new columns to hiring_rounds table
ALTER TABLE hiring_rounds 
ADD COLUMN IF NOT EXISTS round_name VARCHAR(255) COMMENT 'Custom name for the round',
ADD COLUMN IF NOT EXISTS round_mode ENUM('MCQ', 'Coding', 'Interview', 'Group Discussion', 'Assignment', 'Case Study', 'Presentation', 'Other') COMMENT 'Type of assessment',
ADD COLUMN IF NOT EXISTS evaluation_criteria TEXT COMMENT 'JSON array of evaluation criteria',
ADD COLUMN IF NOT EXISTS is_elimination_round BOOLEAN DEFAULT TRUE COMMENT 'Whether candidates are eliminated',
ADD COLUMN IF NOT EXISTS scheduled_date DATE COMMENT 'When this round is scheduled',
ADD COLUMN IF NOT EXISTS scheduled_time TIME COMMENT 'Start time for the round',
ADD COLUMN IF NOT EXISTS venue VARCHAR(500) COMMENT 'Physical location or online meeting link',
ADD COLUMN IF NOT EXISTS status ENUM('Draft', 'Active', 'Completed', 'Cancelled') DEFAULT 'Draft' COMMENT 'Round status',
ADD COLUMN IF NOT EXISTS min_passing_score DECIMAL(5,2) COMMENT 'Minimum score to pass',
ADD COLUMN IF NOT EXISTS max_score DECIMAL(5,2) DEFAULT 100.00 COMMENT 'Maximum achievable score',
ADD COLUMN IF NOT EXISTS configuration TEXT COMMENT 'JSON field for round-specific settings',
ADD COLUMN IF NOT EXISTS created_by INT COMMENT 'Company user who created this round',
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

-- Modify round_type column to use ENUM
ALTER TABLE hiring_rounds 
MODIFY COLUMN round_type ENUM('Online', 'Offline', 'Aptitude', 'GD', 'Tech Interview', 'HR') NOT NULL DEFAULT 'Online';

COMMIT;
