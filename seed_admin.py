import os
from dotenv import load_dotenv

# --- CRITICAL FIX: Load .env file explicitly ---
load_dotenv()

from app import create_app
from app.db import get_db
from werkzeug.security import generate_password_hash

app = create_app()
def create_admin():
    with app.app_context():
        db = get_db()

        if db is None:
            print("Error: Could not connect to the database.")
            print("Check your .env file and ensure DB_HOST is set.")
            return

        cursor = db.cursor()

        email = "admin@manifestair.com"
        password = "adminpassword123"
        first_name = "System"
        last_name = "Administrator"
        dob = "2000-01-01"