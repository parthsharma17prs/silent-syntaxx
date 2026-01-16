import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'placement_portal')

def column_exists(cursor, table, column):
    cursor.execute(f"""
        SELECT COUNT(*) as count
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = '{DB_NAME}'
        AND TABLE_NAME = '{table}'
        AND COLUMN_NAME = '{column}'
    """)
    result = cursor.fetchone()
    return result[0] > 0

try:
    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    cursor = conn.cursor()
    
    print("Checking hiring_rounds table...")
    
    # Drop and recreate the hiring_rounds table with correct schema
    print("\nRecreating hiring_rounds table with full schema...")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    cursor.execute("DROP TABLE IF EXISTS round_candidate_progress")
    cursor.execute("DROP TABLE IF EXISTS interview_bookings")
    cursor.execute("DROP TABLE IF EXISTS application_rounds")
    cursor.execute("DROP TABLE IF EXISTS hiring_rounds")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    
    cursor.execute("""
        CREATE TABLE hiring_rounds (
            id INT PRIMARY KEY AUTO_INCREMENT,
            job_id INT NOT NULL,
            round_number INT NOT NULL,
            round_name VARCHAR(255) NOT NULL,
            round_type ENUM('Online', 'Offline') NOT NULL DEFAULT 'Online',
            round_mode ENUM('MCQ', 'Coding', 'Interview', 'Group Discussion', 'Assignment', 'Case Study', 'Presentation', 'Other') NOT NULL,
            description TEXT,
            duration_minutes INT,
            evaluation_criteria TEXT,
            is_elimination_round BOOLEAN DEFAULT TRUE,
            scheduled_date DATE,
            scheduled_time TIME,
            venue VARCHAR(500),
            status ENUM('Draft', 'Active', 'Completed', 'Cancelled') DEFAULT 'Draft',
            min_passing_score DECIMAL(5,2),
            max_score DECIMAL(5,2) DEFAULT 100.00,
            configuration JSON,
            created_by INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE,
            INDEX idx_job_round (job_id, round_number),
            INDEX idx_status (status),
            INDEX idx_scheduled (scheduled_date, scheduled_time),
            UNIQUE KEY unique_job_round (job_id, round_number)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)
    print("✓ Created hiring_rounds table")
    
    cursor.execute("""
        CREATE TABLE round_candidate_progress (
            id INT PRIMARY KEY AUTO_INCREMENT,
            round_id INT NOT NULL,
            application_id INT NOT NULL,
            student_id INT NOT NULL,
            status ENUM('Pending', 'Invited', 'In Progress', 'Completed', 'Passed', 'Failed', 'Absent', 'Disqualified') DEFAULT 'Pending',
            score DECIMAL(5,2),
            candidate_rank INT,
            evaluator_notes TEXT,
            evaluation_metrics JSON,
            strengths TEXT,
            areas_of_improvement TEXT,
            invited_at TIMESTAMP NULL,
            started_at TIMESTAMP NULL,
            completed_at TIMESTAMP NULL,
            evaluated_at TIMESTAMP NULL,
            attempt_count INT DEFAULT 0,
            submission_data JSON,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (round_id) REFERENCES hiring_rounds(id) ON DELETE CASCADE,
            FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE CASCADE,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
            INDEX idx_round_candidate (round_id, student_id),
            INDEX idx_application (application_id),
            INDEX idx_status (status),
            INDEX idx_score (score),
            UNIQUE KEY unique_round_application (round_id, application_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)
    print("✓ Created round_candidate_progress table")
    
    conn.commit()
    conn.close()
    print('\n✓ Hiring rounds tables created successfully!')
except Exception as e:
    print(f'✗ Error: {e}')
