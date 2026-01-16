from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        columns_to_add = [
            ('ats_feedback', 'TEXT NULL'),
            ('ats_calculated_at', 'DATETIME NULL'),
            ('experience', 'TEXT NULL'),
            ('projects', 'TEXT NULL'),
            ('certifications', 'TEXT NULL'),
            ('linkedin_url', 'VARCHAR(500) NULL'),
            ('github_url', 'VARCHAR(500) NULL')
        ]
        
        for column_name, column_def in columns_to_add:
            result = db.session.execute(text(f"SHOW COLUMNS FROM students LIKE '{column_name}'"))
            if not result.fetchone():
                print(f"Adding {column_name} column...")
                db.session.execute(text(f"ALTER TABLE students ADD COLUMN {column_name} {column_def}"))
                db.session.commit()
                print(f"✓ Added {column_name} column")
            else:
                print(f"✓ {column_name} column already exists")
            
    except Exception as e:
        print(f"Error: {e}")
        db.session.rollback()

