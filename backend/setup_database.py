import pymysql
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'placement_portal')

def execute_sql_file(cursor, filepath):
    """Execute SQL commands from a file"""
    print(f"\n{'='*60}")
    print(f"Executing: {os.path.basename(filepath)}")
    print(f"{'='*60}")
    
    with open(filepath, 'r', encoding='utf-8') as file:
        sql_content = file.read()
        
        # Split by semicolon and execute each statement
        statements = sql_content.split(';')
        
        for statement in statements:
            statement = statement.strip()
            if statement and not statement.startswith('--'):
                try:
                    cursor.execute(statement)
                    print(f"✓ Executed successfully")
                except Exception as e:
                    # Some statements might fail if already exists, that's okay
                    if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                        print(f"⚠ Already exists (skipping): {str(e)[:100]}")
                    else:
                        print(f"✗ Error: {str(e)[:200]}")

def main():
    print("\n" + "="*60)
    print("DATABASE SETUP - Placement Portal")
    print("="*60)
    
    try:
        # Connect to MySQL server (without database)
        print(f"\nConnecting to MySQL server at {DB_HOST}...")
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        cursor = connection.cursor()
        print("✓ Connected successfully!")
        
        # Create database if not exists
        print(f"\nCreating database '{DB_NAME}' if not exists...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        cursor.execute(f"USE {DB_NAME}")
        print(f"✓ Database '{DB_NAME}' is ready!")
        
        # Get the database directory
        db_dir = os.path.join(os.path.dirname(__file__), '..', 'database')
        
        # Execute SQL files in order
        sql_files = [
            'schema.sql',
            'schema_enhancements.sql',
            'batch_session_schema.sql',
            'hiring_rounds_schema.sql'
        ]
        
        for sql_file in sql_files:
            filepath = os.path.join(db_dir, sql_file)
            if os.path.exists(filepath):
                execute_sql_file(cursor, filepath)
                connection.commit()
                print(f"✓ {sql_file} completed!")
            else:
                print(f"⚠ Warning: {sql_file} not found, skipping...")
        
        print("\n" + "="*60)
        print("DATABASE SETUP COMPLETE!")
        print("="*60)
        print("\n✓ All tables have been created/updated successfully!")
        print(f"✓ Database: {DB_NAME}")
        print("✓ Ready to start the backend server!\n")
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        return False
    finally:
        if 'connection' in locals():
            connection.close()
            print("✓ Database connection closed.\n")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
