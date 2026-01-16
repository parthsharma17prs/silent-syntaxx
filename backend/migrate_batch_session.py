"""
Batch and Session Migration Script
Purpose: Safely migrate existing data to batch/session structure
Date: January 4, 2026
"""

import sys
import os
from datetime import datetime, date

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import PlacementSession, Batch, BatchSessionMapping, Student, Job, Application
from sqlalchemy import text

def run_migration():
    """Execute the migration safely with rollback capability"""
    with app.app_context():
        try:
            print("="*60)
            print("BATCH & SESSION MIGRATION SCRIPT")
            print("="*60)
            
            # Step 1: Execute SQL schema
            print("\n[Step 1] Running SQL schema migration...")
            with open('database/batch_session_schema.sql', 'r') as f:
                sql_script = f.read()
                
                # Execute SQL in chunks (split by CREATE/ALTER/INSERT statements)
                statements = [s.strip() for s in sql_script.split(';') if s.strip()]
                
                for i, statement in enumerate(statements):
                    if statement.startswith('--') or not statement:
                        continue
                    try:
                        db.session.execute(text(statement))
                        db.session.commit()
                        print(f"  ✓ Executed statement {i+1}/{len(statements)}")
                    except Exception as e:
                        if "Duplicate" in str(e) or "already exists" in str(e):
                            print(f"  ⚠ Skipping duplicate: {str(e)[:80]}...")
                            db.session.rollback()
                        else:
                            print(f"  ✗ Error: {str(e)}")
                            db.session.rollback()
                            raise
            
            print("✓ SQL schema migration completed")
            
            # Step 2: Verify default session
            print("\n[Step 2] Verifying default placement session...")
            default_session = PlacementSession.query.filter_by(is_default=True).first()
            
            if not default_session:
                print("  Creating default session...")
                default_session = PlacementSession(
                    name='Legacy Session',
                    description='Default session for existing data migration',
                    start_year=2023,
                    end_year=2024,
                    start_date=date(2023, 7, 1),
                    end_date=date(2024, 6, 30),
                    status='Active',
                    is_default=True
                )
                db.session.add(default_session)
                db.session.commit()
                print(f"  ✓ Created default session: {default_session.name} (ID: {default_session.id})")
            else:
                print(f"  ✓ Default session exists: {default_session.name} (ID: {default_session.id})")
            
            # Step 3: Create/verify batches
            print("\n[Step 3] Creating standard batches...")
            batch_configs = [
                {'batch_code': '2021-2025', 'start_year': 2021, 'end_year': 2025, 'status': 'Graduated'},
                {'batch_code': '2022-2026', 'start_year': 2022, 'end_year': 2026, 'status': 'Active'},
                {'batch_code': '2023-2027', 'start_year': 2023, 'end_year': 2027, 'status': 'Active'},
                {'batch_code': '2024-2028', 'start_year': 2024, 'end_year': 2028, 'status': 'Active'},
            ]
            
            created_batches = []
            for config in batch_configs:
                batch = Batch.query.filter_by(batch_code=config['batch_code']).first()
                if not batch:
                    batch = Batch(
                        batch_code=config['batch_code'],
                        start_year=config['start_year'],
                        end_year=config['end_year'],
                        degree='B.Tech',
                        program='Computer Science',
                        status=config['status']
                    )
                    db.session.add(batch)
                    db.session.commit()
                    print(f"  ✓ Created batch: {batch.batch_code}")
                else:
                    print(f"  ✓ Batch exists: {batch.batch_code}")
                created_batches.append(batch)
            
            # Step 4: Map students to batches
            print("\n[Step 4] Mapping students to batches...")
            unmapped_students = Student.query.filter_by(batch_id=None).all()
            mapped_count = 0
            
            for student in unmapped_students:
                if student.graduation_year:
                    # Find matching batch by graduation year
                    batch = Batch.query.filter_by(end_year=student.graduation_year).first()
                    
                    if not batch:
                        # Create a new batch for this graduation year
                        batch_code = f"{student.graduation_year - 4}-{student.graduation_year}"
                        batch = Batch.query.filter_by(batch_code=batch_code).first()
                        
                        if not batch:
                            batch = Batch(
                                batch_code=batch_code,
                                start_year=student.graduation_year - 4,
                                end_year=student.graduation_year,
                                degree='B.Tech',
                                program='General',
                                status='Graduated' if student.graduation_year <= datetime.now().year else 'Active'
                            )
                            db.session.add(batch)
                            db.session.commit()
                            print(f"  ✓ Created new batch: {batch_code}")
                    
                    student.batch_id = batch.id
                    mapped_count += 1
            
            db.session.commit()
            print(f"  ✓ Mapped {mapped_count} students to batches")
            
            # Step 5: Map jobs to default session
            print("\n[Step 5] Mapping jobs to default session...")
            unmapped_jobs = Job.query.filter_by(session_id=None).all()
            for job in unmapped_jobs:
                job.session_id = default_session.id
            db.session.commit()
            print(f"  ✓ Mapped {len(unmapped_jobs)} jobs to default session")
            
            # Step 6: Map applications to default session
            print("\n[Step 6] Mapping applications to default session...")
            unmapped_apps = Application.query.filter_by(session_id=None).all()
            for app in unmapped_apps:
                app.session_id = default_session.id
            db.session.commit()
            print(f"  ✓ Mapped {len(unmapped_apps)} applications to default session")
            
            # Step 7: Map batches to default session
            print("\n[Step 7] Mapping batches to default session...")
            all_batches = Batch.query.all()
            mapped_batch_count = 0
            
            for batch in all_batches:
                existing_mapping = BatchSessionMapping.query.filter_by(
                    batch_id=batch.id,
                    session_id=default_session.id
                ).first()
                
                if not existing_mapping:
                    mapping = BatchSessionMapping(
                        batch_id=batch.id,
                        session_id=default_session.id,
                        is_eligible=True
                    )
                    db.session.add(mapping)
                    mapped_batch_count += 1
            
            db.session.commit()
            print(f"  ✓ Created {mapped_batch_count} batch-session mappings")
            
            # Step 8: Validation
            print("\n[Step 8] Running validation checks...")
            
            students_without_batch = Student.query.filter_by(batch_id=None).count()
            jobs_without_session = Job.query.filter_by(session_id=None).count()
            apps_without_session = Application.query.filter_by(session_id=None).count()
            
            print(f"  Students without batch: {students_without_batch}")
            print(f"  Jobs without session: {jobs_without_session}")
            print(f"  Applications without session: {apps_without_session}")
            
            if students_without_batch > 0:
                print("  ⚠ Warning: Some students are not mapped to batches")
            if jobs_without_session > 0:
                print("  ⚠ Warning: Some jobs are not mapped to sessions")
            if apps_without_session > 0:
                print("  ⚠ Warning: Some applications are not mapped to sessions")
            
            # Summary
            print("\n" + "="*60)
            print("MIGRATION SUMMARY")
            print("="*60)
            print(f"Total Sessions: {PlacementSession.query.count()}")
            print(f"Total Batches: {Batch.query.count()}")
            print(f"Total Students: {Student.query.count()}")
            print(f"Students Mapped to Batches: {Student.query.filter(Student.batch_id.isnot(None)).count()}")
            print(f"Total Jobs: {Job.query.count()}")
            print(f"Jobs Mapped to Sessions: {Job.query.filter(Job.session_id.isnot(None)).count()}")
            print(f"Total Applications: {Application.query.count()}")
            print(f"Applications Mapped to Sessions: {Application.query.filter(Application.session_id.isnot(None)).count()}")
            print("="*60)
            print("✓ MIGRATION COMPLETED SUCCESSFULLY")
            print("="*60)
            
        except Exception as e:
            print(f"\n✗ Migration failed: {str(e)}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            sys.exit(1)

if __name__ == '__main__':
    run_migration()
