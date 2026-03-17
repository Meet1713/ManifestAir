from app import create_app
from app.db import get_db

def init_metrics():
    app = create_app()
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        
        print("Connecting to Database...")
        
        # Create the table
        try:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_metrics (
                metric_key VARCHAR(50) PRIMARY KEY,
                metric_value INT DEFAULT 0,
                last_updated DATE
            );
            """)
            print("Table 'system_metrics' checked/created.")
        except Exception as e:
            print(f"Error creating table: {e}")

        # Initialize the counter (only if it doesn't exist)
        try:
            cursor.execute("""
            INSERT IGNORE INTO system_metrics (metric_key, metric_value, last_updated) 
            VALUES ('api_usage_daily', 0, CURRENT_DATE);
            """)
            db.commit()
            print("Metric 'api_usage_daily' initialized.")
        except Exception as e:
            print(f"Error initializing metric: {e}")

if __name__ == "__main__":
    init_metrics()