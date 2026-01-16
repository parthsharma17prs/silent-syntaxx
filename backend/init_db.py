import os
import pymysql
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SCHEMA_PATH = Path(__file__).parent.parent / "database" / "schema.sql"

sql_text = SCHEMA_PATH.read_text(encoding="utf-8")

statements = []
chunk = []
for line in sql_text.splitlines():
    stripped = line.strip()
    if not stripped or stripped.startswith('--'):
        continue
    chunk.append(line)
    if stripped.endswith(';'):
        statements.append('\n'.join(chunk))
        chunk = []
if chunk:
    statements.append('\n'.join(chunk))

# Skip database directives in file; we'll handle explicitly
statements = [s for s in statements if not s.lower().startswith("create database") and not s.lower().startswith("use ")]

# Ensure database exists
bootstrap = pymysql.connect(
    host=os.getenv("DB_HOST", "localhost"), 
    user=os.getenv("DB_USER", "root"), 
    password=os.getenv("DB_PASSWORD", ""), 
    autocommit=True
)
with bootstrap.cursor() as cur:
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {os.getenv('DB_NAME', 'placement_portal')};")
bootstrap.close()

# Now operate inside the DB
conn = pymysql.connect(
    host=os.getenv("DB_HOST", "localhost"), 
    user=os.getenv("DB_USER", "root"), 
    password=os.getenv("DB_PASSWORD", ""), 
    database=os.getenv("DB_NAME", "placement_portal"), 
    autocommit=True
)
cur = conn.cursor()

# Ensure views can be recreated if script ran before
cur.execute("DROP VIEW IF EXISTS placement_stats;")
cur.execute("DROP VIEW IF EXISTS branch_placement;")

for stmt in statements:
    cur.execute(stmt)
cur.close()
conn.close()
print(f"Executed {len(statements)} statements from {SCHEMA_PATH.name}")
