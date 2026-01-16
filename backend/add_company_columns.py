import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'placement_portal')

def column_exists(cursor, table, column):
    cursor.execute(f"""
        SELECT COUNT(*) as count
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = '{DB_NAME}'
        AND TABLE_NAME = '{table}'
        AND COLUMN_NAME = '{column}'
    """)
    result = cursor.fetchone()
    return result[0] > 0

try:
    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    cursor = conn.cursor()
    
    if not column_exists(cursor, 'companies', 'contact_person'):
        cursor.execute("ALTER TABLE companies ADD COLUMN contact_person VARCHAR(255) NULL AFTER company_name")
        print("✓ Added contact_person column")
    
    if not column_exists(cursor, 'companies', 'website'):
        cursor.execute("ALTER TABLE companies ADD COLUMN website VARCHAR(500) NULL")
        print("✓ Added website column")
    
    conn.commit()
    conn.close()
    print("✓ Complete")
except Exception as e:
    print(f"✗ Error: {e}")
