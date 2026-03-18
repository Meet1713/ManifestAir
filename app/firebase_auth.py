import os
import json
import firebase_admin
from firebase_admin import credentials, auth

def init_firebase():
    """Initializes the Firebase Admin SDK using the local key file."""
    if not firebase_admin._apps:
        firebase_json = os.environ.get("FIREBASE_SERVICE_ACCOUNT_JSON")

        if firebase_json:
            try:
                cred_dict = json.loads(firebase_json)
                cred = credentials.Certificate(cred_dict)
                firebase_admin.initialize_app(cred)
                print("🔥 Firebase Admin SDK Initialized successfully from environment.")
            except Exception as e:
                print(f"❌ Firebase initialization error: {e}")
        else:
            print("⚠️ FIREBASE_SERVICE_ACCOUNT_JSON not set. Firebase Auth will fail.")

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