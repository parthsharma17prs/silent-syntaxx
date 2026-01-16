import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'placement_portal')

try:
    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    cursor = conn.cursor()
    
    print("Creating application_rounds table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS application_rounds (
            id INT PRIMARY KEY AUTO_INCREMENT,
            application_id INT NOT NULL,
            hiring_round_id INT NOT NULL,
            status ENUM('Pending', 'Invited', 'In Progress', 'Completed', 'Passed', 'Failed', 'Absent') DEFAULT 'Pending',
            score DECIMAL(5,2),
            feedback TEXT,
            completed_at TIMESTAMP NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE CASCADE,
            FOREIGN KEY (hiring_round_id) REFERENCES hiring_rounds(id) ON DELETE CASCADE,
            INDEX idx_application (application_id),
            INDEX idx_hiring_round (hiring_round_id),
            INDEX idx_status (status),
            UNIQUE KEY unique_app_round (application_id, hiring_round_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)
    conn.commit()
    print('✓ Created application_rounds table')
    
    print("\nCreating interview_bookings table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interview_bookings (
            id INT PRIMARY KEY AUTO_INCREMENT,
            application_id INT NOT NULL,
            application_round_id INT,
            interview_date DATE NOT NULL,
            interview_time TIME NOT NULL,
            interview_mode ENUM('Online', 'Offline', 'Phone') DEFAULT 'Online',
            venue VARCHAR(500),
            meeting_link VARCHAR(500),
            interviewer_name VARCHAR(255),
            interviewer_email VARCHAR(255),
            status ENUM('Scheduled', 'Completed', 'Cancelled', 'Rescheduled') DEFAULT 'Scheduled',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE CASCADE,
            FOREIGN KEY (application_round_id) REFERENCES application_rounds(id) ON DELETE SET NULL,
            INDEX idx_application (application_id),
            INDEX idx_interview_date (interview_date),
            INDEX idx_status (status)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)
    conn.commit()
    print('✓ Created interview_bookings table')
    
    conn.close()
    print('\n✓ All related tables created successfully!')
except Exception as e:
    print(f'✗ Error: {e}')
