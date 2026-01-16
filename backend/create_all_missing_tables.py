"""
Create all missing tables for the placement portal
"""
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection
conn = pymysql.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    user=os.getenv('DB_USER', 'root'),
    password=os.getenv('DB_PASSWORD', ''),
    database=os.getenv('DB_NAME', 'placement_portal'),
    charset='utf8mb4'
)

cursor = conn.cursor()

tables_to_create = [
    # interview_slots table
    (
        "interview_slots",
        """
        CREATE TABLE IF NOT EXISTS interview_slots (
            id INT PRIMARY KEY AUTO_INCREMENT,
            hiring_round_id INT NOT NULL,
            company_id INT NOT NULL,
            slot_date DATE NOT NULL,
            slot_time TIME NOT NULL,
            interviewer_name VARCHAR(255),
            interviewer_email VARCHAR(255),
            meeting_link VARCHAR(500),
            location VARCHAR(255),
            max_capacity INT DEFAULT 1,
            current_bookings INT DEFAULT 0,
            status ENUM('Available', 'Full', 'Completed', 'Cancelled') DEFAULT 'Available',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (hiring_round_id) REFERENCES hiring_rounds(id) ON DELETE CASCADE,
            FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
            INDEX idx_slot_round (hiring_round_id),
            INDEX idx_slot_company (company_id),
            INDEX idx_slot_date (slot_date)
        )
        """
    ),
    # interview_bookings table
    (
        "interview_bookings",
        """
        CREATE TABLE IF NOT EXISTS interview_bookings (
            id INT PRIMARY KEY AUTO_INCREMENT,
            interview_slot_id INT NOT NULL,
            application_round_id INT NOT NULL,
            student_id INT NOT NULL,
            status ENUM('Confirmed', 'No-Show', 'Rescheduled', 'Completed') DEFAULT 'Confirmed',
            booking_notes TEXT,
            booked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (interview_slot_id) REFERENCES interview_slots(id) ON DELETE CASCADE,
            FOREIGN KEY (application_round_id) REFERENCES application_rounds(id) ON DELETE CASCADE,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
            INDEX idx_booking_slot (interview_slot_id),
            INDEX idx_booking_student (student_id)
        )
        """
    ),
    # offer_letters table
    (
        "offer_letters",
        """
        CREATE TABLE IF NOT EXISTS offer_letters (
            id INT PRIMARY KEY AUTO_INCREMENT,
            application_id INT NOT NULL,
            company_id INT NOT NULL,
            student_id INT NOT NULL,
            designation VARCHAR(255) NOT NULL,
            ctc VARCHAR(100) NOT NULL,
            annual_ctc DECIMAL(12,2),
            job_location VARCHAR(255),
            joining_date DATE,
            notice_period INT,
            offer_content TEXT NOT NULL,
            template_used VARCHAR(255),
            status ENUM('Generated', 'Sent', 'Accepted', 'Rejected', 'Expired') DEFAULT 'Generated',
            sent_date DATETIME,
            acceptance_date DATETIME,
            expiry_date DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (application_id) REFERENCES applications(id) ON DELETE CASCADE,
            FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
            INDEX idx_offer_app (application_id),
            INDEX idx_offer_company (company_id),
            INDEX idx_offer_student (student_id)
        )
        """
    ),
    # student_verification table
    (
        "student_verification",
        """
        CREATE TABLE IF NOT EXISTS student_verification (
            id INT PRIMARY KEY AUTO_INCREMENT,
            student_id INT NOT NULL UNIQUE,
            status ENUM('Pending', 'Verified', 'Rejected') DEFAULT 'Pending',
            marksheet_10th_url VARCHAR(500),
            marksheet_12th_url VARCHAR(500),
            degree_certificate_url VARCHAR(500),
            verification_date DATETIME,
            rejection_reason TEXT,
            verified_by INT,
            submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
            FOREIGN KEY (verified_by) REFERENCES users(id) ON DELETE SET NULL,
            INDEX idx_verif_student (student_id),
            INDEX idx_verif_status (status)
        )
        """
    )
]

try:
    for table_name, create_sql in tables_to_create:
        print(f"Creating {table_name} table...")
        cursor.execute(create_sql)
        print(f"  ✓ {table_name} created/verified")
    
    conn.commit()
    print("\n✓ All tables created successfully!")
    
    # Verify all tables exist
    print("\nVerifying tables:")
    for table_name, _ in tables_to_create:
        cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
        result = cursor.fetchone()
        if result:
            print(f"  ✓ {table_name} exists")
        else:
            print(f"  ✗ {table_name} MISSING")
    
except Exception as e:
    print(f"✗ Error: {e}")
    conn.rollback()
finally:
    cursor.close()
    conn.close()
