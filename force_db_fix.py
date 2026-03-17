import os
from dotenv import load_dotenv

# LOAD ENVIRONMENT VARIABLES FIRST
load_dotenv()

# Check if keys are loaded (Debug)
print(f"DEBUG: DB_HOST is {os.environ.get('DB_HOST')}")

from app import create_app
from app.db import get_db

app = create_app()
with app.app_context():
    print("🔧 Connecting to Cloud Database...")
    db = get_db()
    
    if db is None:
        print("❌ CRITICAL: Could not connect to database. Check your .env file.")
        exit(1)

    cursor = db.cursor()
    
    # Force Create Table
    print("🔨 Creating 'system_metrics' table...")
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_metrics (
                metric_key VARCHAR(50) PRIMARY KEY,
                metric_value INT DEFAULT 0,
                last_updated DATE
            );
        """)
        
        # Force Initialize Data
        print("📥 Initializing counter...")
        cursor.execute("""
            INSERT IGNORE INTO system_metrics (metric_key, metric_value, last_updated) 
            VALUES ('api_usage_daily', 0, CURRENT_DATE);
        """)
        
        db.commit()
        print("✅ SUCCESS! Table created.")
    except Exception as e:
        print(f"❌ SQL Error: {e}")