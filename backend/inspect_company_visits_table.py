import os
from dotenv import load_dotenv
import pymysql

load_dotenv()
conn = pymysql.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    user=os.getenv('DB_USER', 'root'),
    password=os.getenv('DB_PASSWORD', ''),
    database=os.getenv('DB_NAME', 'placement_portal'),
    charset='utf8mb4'
)
cur = conn.cursor()
cur.execute("SHOW COLUMNS FROM company_visits")
cols = cur.fetchall()
print('company_visits columns:')
for col in cols:
    # Field, Type, Null, Key, Default, Extra
    print(f"- {col[0]}: {col[1]} null={col[2]} key={col[3]} default={col[4]} extra={col[5]}")
cur.close()
conn.close()
