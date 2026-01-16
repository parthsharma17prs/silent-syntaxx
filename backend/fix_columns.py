import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'placement_portal')

def add_column_if_not_exists(cursor, table, column, definition):
    """Add a column to a table if it doesn't already exist"""
    try:
        cursor.execute(f"""
            SELECT COUNT(*) as count
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = '{DB_NAME}'
            AND TABLE_NAME = '{table}'
            AND COLUMN_NAME = '{column}'
        """)
        result = cursor.fetchone()
        
        if result['count'] == 0:
            print(f"  Adding column {table}.{column}...")
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
            print(f"  ✓ Added {table}.{column}")
            return True
        else:
            print(f"  ⚠ Column {table}.{column} already exists")
            return False
    except Exception as e:
        print(f"  ✗ Error adding {table}.{column}: {str(e)}")
        return False

def main():
    print("\n" + "="*60)
    print("FIXING MISSING COLUMNS")
    print("="*60)
    
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        cursor = connection.cursor()
        print(f"\n✓ Connected to database: {DB_NAME}\n")
        
        # Add missing columns
        columns_to_add = [
            # Batch/Session columns
            ('students', 'batch_id', 'INT NULL AFTER graduation_year'),
            ('jobs', 'session_id', 'INT NULL AFTER application_deadline'),
            ('applications', 'session_id', 'INT NULL AFTER job_id'),
            
            # Enhanced student columns
            ('students', 'experience', 'TEXT NULL'),
            ('students', 'projects', 'TEXT NULL'),
            ('students', 'certifications', 'TEXT NULL'),
            ('students', 'linkedin_url', 'VARCHAR(500) NULL'),
            ('students', 'github_url', 'VARCHAR(500) NULL'),
            
            # Enhanced company columns
            ('companies', 'company_description', 'TEXT NULL'),
            ('companies', 'company_size', 'VARCHAR(50) NULL'),
            ('companies', 'industry', 'VARCHAR(100) NULL'),
            ('companies', 'headquarters_location', 'VARCHAR(255) NULL'),
            ('companies', 'hr_email', 'VARCHAR(255) NULL'),
            ('companies', 'hr_phone', 'VARCHAR(20) NULL'),
            
            # Enhanced job columns
            ('jobs', 'min_cgpa', 'DECIMAL(3,2) NULL'),
            ('jobs', 'eligible_branches', 'TEXT NULL'),
            ('jobs', 'job_type', "ENUM('Full-Time', 'Internship', 'Part-Time', 'Contract') DEFAULT 'Full-Time'"),
            ('jobs', 'work_mode', "ENUM('On-site', 'Remote', 'Hybrid') DEFAULT 'On-site'"),
            
            # Application enhancements
            ('applications', 'ats_score', 'INT NULL'),
            ('applications', 'ats_feedback', 'TEXT NULL'),
        ]
        
        changes_made = False
        for table, column, definition in columns_to_add:
            if add_column_if_not_exists(cursor, table, column, definition):
                changes_made = True
        
        if changes_made:
            connection.commit()
            print("\n✓ Changes committed to database")
        else:
            print("\n⚠ No changes needed - all columns exist")
        
        print("\n" + "="*60)
        print("COLUMN FIX COMPLETE!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}\n")
        return False
    finally:
        if 'connection' in locals():
            connection.close()
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
