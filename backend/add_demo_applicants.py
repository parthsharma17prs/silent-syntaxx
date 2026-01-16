import argparse
import os
import random
import string
from datetime import date
from pathlib import Path

import pymysql
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash


def load_env() -> None:
    env_path = Path(__file__).parent / ".env"
    load_dotenv(dotenv_path=env_path)


def db_connect():
    host = os.getenv("DB_HOST", "localhost")
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "")
    database = os.getenv("DB_NAME", "placement_portal")
    port = int(os.getenv("DB_PORT", "3306"))
    return pymysql.connect(host=host, user=user, password=password, database=database, port=port, autocommit=False)


def pick_job(cursor, company_id: int | None, company_name: str | None, job_id: int | None, job_title: str | None):
    if job_id is not None:
        cursor.execute(
            "SELECT id, company_id, session_id, title FROM jobs WHERE id=%s",
            (job_id,),
        )
        row = cursor.fetchone()
        return row

    if company_id is None and company_name is not None:
        cursor.execute(
            "SELECT id FROM companies WHERE company_name=%s ORDER BY id DESC LIMIT 1",
            (company_name,),
        )
        company_row = cursor.fetchone()
        company_id = company_row[0] if company_row else None

    if company_id is None:
        return None

    if job_title:
        cursor.execute(
            "SELECT id, company_id, session_id, title FROM jobs WHERE company_id=%s AND title=%s ORDER BY id DESC LIMIT 1",
            (company_id, job_title),
        )
        row = cursor.fetchone()
        if row:
            return row

    cursor.execute(
        "SELECT id, company_id, session_id, title FROM jobs WHERE company_id=%s ORDER BY id DESC LIMIT 1",
        (company_id,),
    )
    return cursor.fetchone()


def get_available_students(cursor, job_id: int, limit: int):
    cursor.execute(
        """
        SELECT s.id
        FROM students s
        LEFT JOIN applications a ON a.student_id=s.id AND a.job_id=%s
        WHERE a.id IS NULL
        ORDER BY s.id DESC
        LIMIT %s
        """,
        (job_id, limit),
    )
    return [r[0] for r in cursor.fetchall()]


def ensure_students(cursor, needed: int, graduation_year: int = 2026) -> list[int]:
    """Create demo students (and matching users) if the DB doesn't have enough."""
    created_ids: list[int] = []
    if needed <= 0:
        return created_ids

    branches = ["Computer Science", "Information Technology", "Electronics", "Mechanical", "Civil"]

    # Use a stable but random-ish prefix so reruns won't collide as easily.
    prefix = "DEMO" + "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
    password_hash = generate_password_hash("student123")

    for i in range(needed):
        # Create user
        email = f"demo.student.{prefix}.{i}@university.edu"
        cursor.execute(
            "INSERT INTO users (email, password_hash, role_id, is_verified) VALUES (%s, %s, 1, TRUE)",
            (email, password_hash),
        )
        user_id = cursor.lastrowid

        # Create student
        enrollment = f"{prefix}{i:04d}"
        full_name = f"Demo Student {prefix}-{i}"
        branch = random.choice(branches)
        cgpa = round(random.uniform(6.5, 9.4), 2)
        phone = "9" + "".join(random.choices(string.digits, k=9))

        cursor.execute(
            """
            INSERT INTO students
              (user_id, full_name, enrollment_number, branch, cgpa, graduation_year, phone, profile_completed)
            VALUES
              (%s, %s, %s, %s, %s, %s, %s, TRUE)
            """,
            (user_id, full_name, enrollment, branch, cgpa, graduation_year, phone),
        )
        created_ids.append(cursor.lastrowid)

    return created_ids


def seed_rounds(cursor, application_id: int, job_id: int):
    cursor.execute(
        "SELECT id FROM hiring_rounds WHERE job_id=%s ORDER BY round_number ASC",
        (job_id,),
    )
    round_ids = [r[0] for r in cursor.fetchall()]
    if not round_ids:
        return 0

    inserted = 0
    for rid in round_ids:
        cursor.execute(
            "INSERT IGNORE INTO application_rounds (application_id, hiring_round_id, status, created_at) VALUES (%s, %s, 'Pending', NOW())",
            (application_id, rid),
        )
        inserted += cursor.rowcount

    return inserted


def main():
    parser = argparse.ArgumentParser(description="Add demo applicants (applications) for a job/company.")
    parser.add_argument("--company-id", type=int, default=None)
    parser.add_argument("--company-name", type=str, default=None)
    parser.add_argument("--job-id", type=int, default=None)
    parser.add_argument("--job-title", type=str, default=None)
    parser.add_argument("--count", type=int, default=10)
    parser.add_argument("--status", type=str, default="Applied")
    parser.add_argument("--create-students", action="store_true", help="Create demo students if not enough exist")

    args = parser.parse_args()

    load_env()

    conn = db_connect()
    try:
        with conn.cursor() as cursor:
            job_row = pick_job(cursor, args.company_id, args.company_name, args.job_id, args.job_title)
            if not job_row:
                raise SystemExit(
                    "Could not find a job. Provide --job-id, or --company-id/--company-name (and optionally --job-title)."
                )

            job_id, company_id, session_id, title = job_row

            available = get_available_students(cursor, job_id, args.count)
            shortfall = max(0, args.count - len(available))

            created_students: list[int] = []
            if shortfall and args.create_students:
                created_students = ensure_students(cursor, shortfall)
                available.extend(created_students)

            available = available[: args.count]
            if len(available) < args.count:
                raise SystemExit(
                    f"Only found {len(available)} students who haven't applied for job {job_id}. "
                    f"Re-run with --create-students to auto-create {args.count - len(available)} demo students."
                )

            inserted_apps = 0
            inserted_rounds_total = 0

            for student_id in available:
                cursor.execute(
                    """
                    INSERT INTO applications (student_id, job_id, session_id, status, applied_at, updated_at)
                    VALUES (%s, %s, %s, %s, NOW(), NOW())
                    """,
                    (student_id, job_id, session_id, args.status),
                )
                application_id = cursor.lastrowid
                inserted_apps += 1

                inserted_rounds_total += seed_rounds(cursor, application_id, job_id)

            conn.commit()

            print("✅ Added applicants successfully")
            print(f"- Company ID: {company_id}")
            print(f"- Job ID: {job_id} ({title})")
            print(f"- Applications inserted: {inserted_apps}")
            if inserted_rounds_total:
                print(f"- Application rounds seeded: {inserted_rounds_total}")
            if created_students:
                print(f"- Demo students created: {len(created_students)} (password: student123)")

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()
