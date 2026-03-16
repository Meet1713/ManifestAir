"""
RUN THIS SCRIPT ONCE TO CREATE AN ADMIN USER.
Usage: python seed_admin.py
"""
import os
from dotenv import load_dotenv

# --- CRITICAL FIX: Load .env file explicitly ---
load_dotenv()

from app import create_app
from app.db import get_db
from werkzeug.security import generate_password_hash

app = create_app()

def create_admin():
    # Ensure we are inside the application context so we can access the DB
    with app.app_context():
        db = get_db()
        
        # Check if DB connection succeeded
        if db is None:
            print("Error: Could not connect to the database.")
            print("Check your .env file and ensure DB_HOST is set.")
            return

        cursor = db.cursor()
        
        # Admin Credentials
        email = "admin@manifestair.com"
        password = "adminpassword123" 
        first_name = "System"
        last_name = "Administrator"
        dob = "2000-01-01"
        
        print(f"--- Connecting to: {app.config['DATABASE_HOST']} ---")
        
        try:
            # Check if user already exists
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            existing = cursor.fetchone()
            
            if existing:
                print(f"User {email} already exists. Updating role to ADMIN...")
                cursor.execute("UPDATE users SET role = 'admin' WHERE email = %s", (email,))
            else:
                print(f"Creating new ADMIN user: {email}...")
                cursor.execute(
                    "INSERT INTO users (email, password_hash, first_name, last_name, dob, role) VALUES (%s, %s, %s, %s, %s, 'admin')",
                    (email, generate_password_hash(password), first_name, last_name, dob)
                )
            
            print("Success! You can now login at /auth/admin-login")
            print(f"Email: {email}")
            print(f"Password: {password}")
            
        except Exception as e:
            print(f"Failed to create admin: {e}")

if __name__ == "__main__":
    create_admin()