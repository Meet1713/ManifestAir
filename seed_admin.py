import os
from dotenv import load_dotenv

# --- CRITICAL FIX: Load .env file explicitly ---
load_dotenv()

from app import create_app
from app.db import get_db
from werkzeug.security import generate_password_hash

app = create_app()