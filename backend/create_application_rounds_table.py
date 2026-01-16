"""
Create missing application_rounds table
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

try:
    print("Creating application_rounds table...")
    
    # Drop if exists
    cursor.execute("DROP TABLE IF EXISTS application_rounds")
    
    # Create table
    create_table_sql = """
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
    )
    """
    
    cursor.execute(create_table_sql)
    conn.commit()
    
    print("✓ application_rounds table created successfully!")
    
    # Verify
    cursor.execute("SHOW TABLES LIKE 'application_rounds'")
    result = cursor.fetchone()
    if result:
        print("✓ Table verified in database")
        
        # Show columns
        cursor.execute("DESCRIBE application_rounds")
        columns = cursor.fetchall()
        print("\nTable structure:")
        for col in columns:
            print(f"  - {col[0]}: {col[1]}")
    
except Exception as e:
    print(f"✗ Error: {e}")
    conn.rollback()
finally:
    cursor.close()
    conn.close()
