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
    
    # Check if column exists
    cursor.execute(f"""
        SELECT COUNT(*) as count
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = '{DB_NAME}'
        AND TABLE_NAME = 'students'
        AND COLUMN_NAME = 'current_year'
    """)
    result = cursor.fetchone()
    
    if result[0] == 0:
        cursor.execute('ALTER TABLE students ADD COLUMN current_year INT NULL AFTER graduation_year')
        conn.commit()
        print('✓ Added current_year column')
    else:
        print('⚠ Column current_year already exists')
    
    conn.close()
    print('✓ Complete')
except Exception as e:
    print(f'✗ Error: {e}')
