#!/usr/bin/env python3
"""
Setup Verification Script for Hack-Vento 2K26 Placement Portal
This script verifies that all dependencies and configurations are properly set up.
"""

import os
import sys
from pathlib import Path
import importlib.util

def check_python_packages():
    """Check if all required Python packages are installed"""
    required_packages = [
        'flask',
        'flask_sqlalchemy', 
        'flask_cors',
        'flask_jwt_extended',
        'pymysql',
        'dotenv',  # python-dotenv package, imported as 'dotenv'
        'werkzeug',
        'cryptography',
        'openpyxl',
        'PyPDF2',
        'docx',
        'groq'
    ]
    
    print("Checking Python packages...")
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        return False
    else:
        print("All packages installed successfully!")
        return True

def check_environment_variables():
    """Check if .env file exists and has required variables"""
    env_file = Path(__file__).parent / '.env'
    
    print("\nChecking environment variables...")
    
    if not env_file.exists():
        print("✗ .env file not found!")
        return False
    
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = [
        'SECRET_KEY',
        'JWT_SECRET_KEY',
        'DB_HOST',
        'DB_USER', 
        'DB_PASSWORD',
        'DB_NAME'
    ]
    
    missing_vars = []
    for var in required_vars:
        if os.getenv(var):
            print(f"✓ {var}")
        else:
            print(f"✗ {var} - NOT SET")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\nMissing environment variables: {', '.join(missing_vars)}")
        return False
    else:
        print("All environment variables configured!")
        return True

def check_database_connection():
    """Test database connection"""
    print("\nTesting database connection...")
    
    try:
        import pymysql
        from dotenv import load_dotenv
        load_dotenv()
        
        conn = pymysql.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        
        with conn.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"✓ Database connection successful! Found {len(tables)} tables.")
            
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

def check_upload_directories():
    """Check if upload directories exist"""
    print("\nChecking upload directories...")
    
    upload_dir = Path(__file__).parent / 'uploads'
    resume_dir = upload_dir / 'resumes'
    
    if upload_dir.exists():
        print(f"✓ Upload directory: {upload_dir}")
    else:
        print(f"✗ Upload directory missing: {upload_dir}")
        return False
        
    if resume_dir.exists():
        print(f"✓ Resume directory: {resume_dir}")
    else:
        print(f"✗ Resume directory missing: {resume_dir}")
        return False
    
    return True

def main():
    """Main verification function"""
    print("=" * 60)
    print("HACK-VENTO 2K26 PLACEMENT PORTAL - SETUP VERIFICATION")
    print("=" * 60)
    
    checks = [
        check_python_packages(),
        check_environment_variables(),
        check_database_connection(),
        check_upload_directories()
    ]
    
    print("\n" + "=" * 60)
    if all(checks):
        print("🎉 ALL CHECKS PASSED! System is ready to run.")
        print("\nTo start the application:")
        print("  Windows: .\\start_backend.bat or .\\start_backend.ps1")
        print("  Manual:  python app.py")
    else:
        print("❌ SOME CHECKS FAILED! Please fix the issues above.")
        sys.exit(1)
    print("=" * 60)

if __name__ == '__main__':
    main()