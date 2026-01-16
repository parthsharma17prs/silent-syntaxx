import os
import sys
from pathlib import Path

# Ensure we're in the right directory
os.chdir(Path(__file__).parent)

print("=" * 60)
print("Starting Placement Portal Backend Server")
print("=" * 60)

try:
    print("\n1. Importing Flask app...")
    from app import app, db
    print("   ✓ Flask app imported successfully")
    
    print("\n2. Testing database connection...")
    with app.app_context():
        db.engine.connect()
    print("   ✓ Database connection successful")
    
    print("\n3. Starting Flask server...")
    print("   Server will be available at:")
    print("   - http://localhost:5000")
    print("   - http://127.0.0.1:5000")
    print("\n" + "=" * 60)
    
    # Run the Flask app
    app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print(f"\nFull error details:")
    import traceback
    traceback.print_exc()
    sys.exit(1)
