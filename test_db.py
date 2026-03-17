import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

print("--- Testing Connection ---")
print(f"Host: {os.getenv('DB_HOST')}")
print(f"User: {os.getenv('DB_USER')}")
print(f"SSL: {os.getenv('DB_SSL_CA')}")

try:
    conn = mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        port=int(os.getenv('DB_PORT')),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME'),
        ssl_ca=os.getenv('DB_SSL_CA')
    )
    print("✅ SUCCESS! Connected to Aiven.")
    conn.close()
except Exception as e:
    print("\n FAILED to connect.")
    print(f"Error: {e}")