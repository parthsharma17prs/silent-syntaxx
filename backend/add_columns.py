import pymysql

try:
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='jpassword',
        database='placement_portal',
        autocommit=True
    )
    cur = conn.cursor()
    
    # Define all columns that should exist
    columns_to_add = {
        'tenth_percentage': 'DECIMAL(5,2)',
        'twelfth_percentage': 'DECIMAL(5,2)',
        'ats_score': 'INT',
        'ats_feedback': 'TEXT',
        'ats_calculated_at': 'DATETIME',
        'experience': 'TEXT',
        'projects': 'TEXT',
        'certifications': 'TEXT',
        'linkedin_url': 'VARCHAR(500)',
        'github_url': 'VARCHAR(500)',
        'current_year': 'SMALLINT'
    }
    
    # Check which columns exist
    cur.execute("""
        SELECT COLUMN_NAME 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = 'placement_portal' 
        AND TABLE_NAME = 'students'
    """)
    
    existing_columns = [row[0] for row in cur.fetchall()]
    
    # Add missing columns
    for column_name, column_type in columns_to_add.items():
        if column_name not in existing_columns:
            cur.execute(f'ALTER TABLE students ADD COLUMN {column_name} {column_type}')
            print(f'Added {column_name} column')
        else:
            print(f'{column_name} column already exists')
    
    conn.close()
    print('Database update completed successfully')
    
except Exception as e:
    print(f'Error: {e}')
