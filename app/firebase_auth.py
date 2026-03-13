import os
import firebase_admin
from firebase_admin import credentials, auth

def init_firebase():
    """Initializes the Firebase Admin SDK using the local key file."""
    try:
        if not firebase_admin._apps:
            cred_path = os.path.join(os.getcwd(), 'serviceAccountKey.json')
            
            if os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                print("🔥 Firebase Admin SDK Initialized successfully.")
            else:
                print("⚠️ Warning: serviceAccountKey.json not found. Firebase Auth will fail.")
    except Exception as e:
        print(f"❌ Firebase Init Error: {e}")

def verify_token(id_token):
    """
    Verifies the ID token sent from the client.
    Allows 5 seconds of clock skew to prevent 'Token used too early' errors.
    """
    try:
        # FIX: Added clock_skew_seconds=5
        decoded_token = auth.verify_id_token(id_token, clock_skew_seconds=5)
        return decoded_token
    except Exception as e:
        print(f"❌ Token Verification Failed: {e}")
        return None