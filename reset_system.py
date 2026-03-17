import os
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

# Load env variables
load_dotenv()

from app import create_app
from app.db import get_db
from app.services.cms_service import refresh_trending_destinations

app = create_app()

print("🚨 SYSTEM RESET INITIATED 🚨")
print("----------------------------")

with app.app_context():
    db = get_db()
    cursor = db.cursor()
    
    # 1. Read and Execute Schema (Wipes DB Structure)
    print("1. Wiping Database Structure...", end=" ", flush=True)
    with open('schema.sql') as f:
        sql_commands = f.read().split(';')
        for command in sql_commands:
            if command.strip():
                try:
                    cursor.execute(command)
                except Exception:
                    pass
    db.commit()
    print("✅ Done.")
    
    # 2. Generate Content (Using robust internal list)
    print("2. Generating Content...")
    refresh_trending_destinations(4)

    # 3. Re-Create Admin User
    print("3. Re-seeding Admin Account...", end=" ", flush=True)
    
    admin_email = "admin@manifestair.com"
    admin_pass = "adminpassword123"
    hashed_pw = generate_password_hash(admin_pass)
    
    try:
        # Check if admin exists
        cursor.execute("SELECT id FROM users WHERE email = %s", (admin_email,))
        if cursor.fetchone():
            cursor.execute("UPDATE users SET password_hash = %s, role = 'admin' WHERE email = %s", (hashed_pw, admin_email))
        else:
            cursor.execute(
                "INSERT INTO users (email, password_hash, first_name, last_name, dob, role) VALUES (%s, %s, %s, %s, %s, %s)",
                (admin_email, hashed_pw, "System", "Admin", "2000-01-01", "admin")
            )
        db.commit()
        print("✅ Done.")
        print(f"\n🎉 RESET COMPLETE.")
        print(f"   Login: {admin_email} / {admin_pass}")
        
    except Exception as e:
        print(f"❌ Error: {e}")