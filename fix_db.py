import os
from dotenv import load_dotenv
load_dotenv()

from app import create_app
from app.db import get_db

app = create_app()

def migrate_db():
    print("--- Starting Database Upgrade ---")
    with app.app_context():
        db = get_db()
        if db is None:
            print("Error: Not connected to database.")
            return
        
        cursor = db.cursor()

        print("Checking 'users' table...")
        try:
            cursor.execute("SELECT is_banned FROM users LIMIT 1")
            print("'is_banned' column already exists.")
        except Exception:
            print("'is_banned' column missing. Adding it now...")
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN is_banned BOOLEAN DEFAULT FALSE")
                print("Column added successfully.")
            except Exception as e:
                print(f"Failed to alter table: {e}")

        print("\nChecking 'destinations' table...")
        try:
            cursor.execute("SELECT * FROM destinations LIMIT 1")
            print("'destinations' table already exists.")
        except Exception:
            print("'destinations' table missing. Creating it now...")
            try:
                # Create Table
                cursor.execute("""
                    CREATE TABLE destinations (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        city VARCHAR(50) NOT NULL,
                        country VARCHAR(50) NOT NULL,
                        price_estimate INT NOT NULL,
                        image_url VARCHAR(500),
                        is_active BOOLEAN DEFAULT TRUE
                    )
                """)
                # Seed Data
                cursor.execute("""
                    INSERT INTO destinations (city, country, price_estimate, image_url) VALUES 
                    ('Tokyo', 'Japan', 1200, 'https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?auto=format&fit=crop&w=800&q=80'),
                    ('Paris', 'France', 850, 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&w=800&q=80'),
                    ('New York', 'USA', 450, 'https://images.unsplash.com/photo-1496442226666-8d4a0e62e6e9?auto=format&fit=crop&w=800&q=80'),
                    ('Dubai', 'UAE', 920, 'https://images.unsplash.com/photo-1512453979798-5ea932a23518?auto=format&fit=crop&w=800&q=80')
                """)
                print("Table created and data seeded.")
            except Exception as e:
                print(f"Failed to create table: {e}")

    print("\n--- Upgrade Complete ---")

if __name__ == "__main__":
    migrate_db()