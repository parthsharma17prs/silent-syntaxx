"""
Sync Batch-Session Mappings Helper
Purpose: Automatically map all active batches to the active session
Run this if you see "No batches mapped to this session" warnings
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import PlacementSession, Batch, BatchSessionMapping

def sync_batch_mappings():
    """Map all active batches to the active placement session"""
    with app.app_context():
        try:
            # Get the active session
            session = PlacementSession.query.filter_by(status='Active').first()
            
            if not session:
                print("❌ No active placement session found")
                print("   Create one via Admin Dashboard -> Sessions tab")
                return False
            
            print(f"✓ Active Session: {session.name} (ID: {session.id})")
            
            # Get all active batches
            batches = Batch.query.filter_by(status='Active').all()
            
            if not batches:
                print("❌ No active batches found")
                print("   Create batches via Admin Dashboard -> Batches tab")
                return False
            
            print(f"\n📦 Found {len(batches)} active batches")
            
            # Create mappings
            mapped_count = 0
            skipped_count = 0
            
            for batch in batches:
                # Check if mapping already exists
                existing = BatchSessionMapping.query.filter_by(
                    batch_id=batch.id,
                    session_id=session.id
                ).first()
                
                if not existing:
                    mapping = BatchSessionMapping(
                        batch_id=batch.id,
                        session_id=session.id,
                        is_eligible=True
                    )
                    db.session.add(mapping)
                    print(f"   + Mapped: {batch.batch_code} -> {session.name}")
                    mapped_count += 1
                else:
                    print(f"   - Already mapped: {batch.batch_code}")
                    skipped_count += 1
            
            db.session.commit()
            
            print(f"\n✅ Sync Complete!")
            print(f"   - New mappings: {mapped_count}")
            print(f"   - Already existed: {skipped_count}")
            print(f"   - Total mappings: {BatchSessionMapping.query.count()}")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error: {str(e)}")
            return False

if __name__ == '__main__':
    print("="*60)
    print("Batch-Session Mapping Sync Tool")
    print("="*60)
    print()
    
    success = sync_batch_mappings()
    
    if success:
        print("\n✓ Done! Refresh the company portal to see batches listed.")
    else:
        print("\n✗ Sync failed. Check the errors above.")
    
    print()
