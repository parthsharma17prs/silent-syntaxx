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
cur.execute("SHOW COLUMNS FROM hiring_rounds")
existing_columns = {col[0] for col in cur.fetchall()}

print("Existing columns:", existing_columns)

# Define new columns to add
columns_to_add = [
    ("round_name", "VARCHAR(255) COMMENT 'Custom name for the round'"),
    ("round_mode", "ENUM('MCQ', 'Coding', 'Interview', 'Group Discussion', 'Assignment', 'Case Study', 'Presentation', 'Other') COMMENT 'Type of assessment'"),
    ("evaluation_criteria", "TEXT COMMENT 'JSON array of evaluation criteria'"),
    ("is_elimination_round", "BOOLEAN DEFAULT TRUE COMMENT 'Whether candidates are eliminated'"),
    ("scheduled_date", "DATE COMMENT 'When this round is scheduled'"),
    ("scheduled_time", "TIME COMMENT 'Start time for the round'"),
    ("venue", "VARCHAR(500) COMMENT 'Physical location or online meeting link'"),
    ("status", "ENUM('Draft', 'Active', 'Completed', 'Cancelled') DEFAULT 'Draft' COMMENT 'Round status'"),
    ("min_passing_score", "DECIMAL(5,2) COMMENT 'Minimum score to pass'"),
    ("max_score", "DECIMAL(5,2) DEFAULT 100.00 COMMENT 'Maximum achievable score'"),
    ("configuration", "TEXT COMMENT 'JSON field for round-specific settings'"),
    ("created_by", "INT COMMENT 'Company user who created this round'"),
    ("updated_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
]

print("\nAdding missing columns to hiring_rounds table...")

for col_name, col_definition in columns_to_add:
    if col_name not in existing_columns:
        try:
            stmt = f"ALTER TABLE hiring_rounds ADD COLUMN {col_name} {col_definition}"
            cur.execute(stmt)
            print(f"✓ Added column: {col_name}")
        except Exception as e:
            print(f"✗ Error adding {col_name}: {e}")
    else:
        print(f"⊙ Column already exists: {col_name}")

# Try to modify round_type if needed
try:
    cur.execute("ALTER TABLE hiring_rounds MODIFY COLUMN round_type VARCHAR(50)")
    print("✓ Modified round_type column")
except Exception as e:
    print(f"⊙ round_type column: {e}")

# Verify final schema
cur.execute("SHOW COLUMNS FROM hiring_rounds")
columns = cur.fetchall()

print("\n\nFinal hiring_rounds table columns:")
for col in columns:
    print(f"  - {col[0]} ({col[1]})")

cur.close()
conn.close()

print("\n✅ Hiring rounds table update complete!")
