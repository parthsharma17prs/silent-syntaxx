import os
import random
from datetime import datetime, timedelta
import pymysql
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_NAME = os.getenv('DB_NAME', 'placement_portal')


def main():
    print("\n" + "=" * 70)
    print("GENERATING OFFER LETTERS FOR SELECTED APPLICATIONS")
    print("=" * 70)
    try:
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            charset='utf8mb4'
        )
        cursor = conn.cursor()

        # Fetch selected applications that do not yet have an offer letter
        cursor.execute(
            """
            SELECT a.id, a.student_id, a.job_id, j.company_id
            FROM applications a
            JOIN jobs j ON a.job_id = j.id
            LEFT JOIN offer_letters o ON o.application_id = a.id
            WHERE a.status = 'Selected' AND o.id IS NULL
            """
        )
        rows = cursor.fetchall()
        if not rows:
            print("No new Selected applications found without offer letters.")
            conn.close()
            return

        created = 0
        for app_id, student_id, job_id, company_id in rows:
            annual_ctc = random.choice([6.5, 8.0, 10.0, 12.0, 15.0])
            ctc_text = f"{annual_ctc} LPA"
            joining = datetime.utcnow().date() + timedelta(days=random.randint(30, 90))
            cursor.execute(
                """
                INSERT INTO offer_letters (
                    application_id, company_id, student_id,
                    designation, ctc, annual_ctc, job_location,
                    offer_content, status, sent_date
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Sent', %s)
                """,
                (
                    app_id,
                    company_id,
                    student_id,
                    'Software Engineer',
                    ctc_text,
                    annual_ctc,
                    'Bangalore',
                    'Congratulations! We are pleased to offer you a position.',
                    joining,
                ),
            )
            created += 1

        conn.commit()
        print(f"✓ Created {created} offer letters for selected applications.")
        conn.close()
    except Exception as e:
        print(f"✗ Error: {e}")


if __name__ == '__main__':
    main()
