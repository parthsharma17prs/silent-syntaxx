from werkzeug.security import generate_password_hash
import pymysql

# Generate hashes for demo accounts
hashes = {
    'admin@university.edu': generate_password_hash('admin123'),
    'student@university.edu': generate_password_hash('student123'),
    'company@tech.com': generate_password_hash('company123'),
}

print("Generated password hashes:")
for email, hash_val in hashes.items():
    print(f"{email}: {hash_val}")

# Connect and update
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

conn = pymysql.connect(
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", ""),
    database=os.getenv("DB_NAME", "placement_portal"),
    autocommit=True
)
cur = conn.cursor()

for email, hash_val in hashes.items():
    cur.execute("UPDATE users SET password_hash = %s WHERE email = %s", (hash_val, email))

cur.close()
conn.close()
print("\nUpdated database with correct password hashes")
