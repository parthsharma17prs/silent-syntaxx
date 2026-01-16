import os
import pymysql
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Connect to database
conn = pymysql.connect(
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", ""),
    database=os.getenv("DB_NAME", "placement_portal"),
    autocommit=True
)

cur = conn.cursor()

# Get existing columns
cur.execute("SHOW COLUMNS FROM students")
existing_columns = {col[0] for col in cur.fetchall()}

# Define columns to add
columns_to_add = [
    ("ats_score", "INT DEFAULT NULL COMMENT 'ATS score 0-100'"),
    ("ats_feedback", "TEXT DEFAULT NULL COMMENT 'Detailed ATS feedback'"),
    ("ats_calculated_at", "DATETIME DEFAULT NULL COMMENT 'When ATS was last calculated'"),
    ("experience", "TEXT DEFAULT NULL"),
    ("projects", "TEXT DEFAULT NULL"),
    ("certifications", "TEXT DEFAULT NULL"),
    ("linkedin_url", "VARCHAR(500) DEFAULT NULL"),
    ("github_url", "VARCHAR(500) DEFAULT NULL"),
    ("current_year", "SMALLINT DEFAULT NULL COMMENT 'Current study year (1-4)'"),
]

print("Adding missing columns to students table...")

for col_name, col_definition in columns_to_add:
    if col_name not in existing_columns:
        try:
            stmt = f"ALTER TABLE students ADD COLUMN {col_name} {col_definition}"
            cur.execute(stmt)
            print(f"✓ Added column: {col_name}")
        except Exception as e:
            print(f"✗ Error adding {col_name}: {e}")
    else:
        print(f"⊙ Column already exists: {col_name}")

# Verify columns exist
cur.execute("SHOW COLUMNS FROM students")
columns = cur.fetchall()

print("\n\nCurrent students table columns:")
for col in columns:
    print(f"  - {col[0]} ({col[1]})")

cur.close()
conn.close()

print("\n✅ Students table update complete!")
