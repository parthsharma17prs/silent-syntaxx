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
    
    print("Creating placement_sessions table...")
    cursor.execute("""
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
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)
    conn.commit()
    print('✓ Created placement_sessions table')
    
    print("\nCreating batches table...")
    cursor.execute("""
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
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)
    conn.commit()
    print('✓ Created batches table')
    
    print("\nCreating batch_session_mapping table...")
    cursor.execute("""
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
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    """)
    conn.commit()
    print('✓ Created batch_session_mapping table')
    
    print("\nInserting default session...")
    cursor.execute("""
        INSERT INTO placement_sessions (name, description, start_year, end_year, start_date, end_date, status, is_default)
        VALUES ('2025-2026 Session', 'Default placement session for academic year 2025-2026', 2025, 2026, '2025-07-01', '2026-06-30', 'Active', TRUE)
        ON DUPLICATE KEY UPDATE id=id
    """)
    conn.commit()
    print('✓ Inserted default session')
    
    print("\nInserting default batches...")
    cursor.execute("""
        INSERT INTO batches (batch_code, start_year, end_year, degree, program, status) VALUES
        ('2022-2026', 2022, 2026, 'B.Tech', 'Computer Science', 'Active'),
        ('2023-2027', 2023, 2027, 'B.Tech', 'Computer Science', 'Active'),
        ('2024-2028', 2024, 2028, 'B.Tech', 'Computer Science', 'Active')
        ON DUPLICATE KEY UPDATE id=id
    """)
    conn.commit()
    print('✓ Inserted default batches')
    
    conn.close()
    print('\n✓ All tables created successfully!')
except Exception as e:
    print(f'✗ Error: {e}')
