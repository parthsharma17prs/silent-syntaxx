"""
Add session_id column to jobs table
"""
import sys
sys.path.append('.')

from app import app, db
from sqlalchemy import text

with app.app_context():
    print("\n🔧 Adding session_id column to jobs table...")
    
    try:
        # Check if column already exists
        result = db.session.execute(text("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'jobs' 
            AND COLUMN_NAME = 'session_id'
        """))
        
        if result.fetchone():
            print("✓ session_id column already exists")
        else:
            # Add the column
            db.session.execute(text("""
                ALTER TABLE jobs 
                ADD COLUMN session_id INT NULL
            """))
            print("✓ Added session_id column")
            
            # Add foreign key constraint
            try:
                db.session.execute(text("""
                    ALTER TABLE jobs
                    ADD CONSTRAINT fk_jobs_session 
                    FOREIGN KEY (session_id) REFERENCES placement_sessions(id)
                """))
                print("✓ Added foreign key constraint")
            except Exception as fk_error:
                print(f"⚠️  Foreign key constraint may already exist: {fk_error}")
            
            db.session.commit()
            
            # Set default session for existing jobs
            result = db.session.execute(text("""
                UPDATE jobs 
                SET session_id = (SELECT id FROM placement_sessions WHERE is_default = TRUE LIMIT 1)
                WHERE session_id IS NULL
            """))
            db.session.commit()
            affected = result.rowcount
            print(f"✓ Updated {affected} existing jobs with default session")

    except Exception as e:
        print(f"❌ Error: {e}")
        db.session.rollback()

print("\n✅ Database update complete!")
print("\nYou may need to restart the backend server for changes to take effect.")
