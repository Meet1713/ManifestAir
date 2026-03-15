from app.db import get_db
from app.providers.serpapi_prov import SerpApiProvider
from app.providers.mock_prov import MockProvider

class ProviderFactory:
    @staticmethod
    def get_provider():
        try:
            db = get_db()
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT setting_value FROM settings WHERE setting_key = 'provider_mode'")
            row = cursor.fetchone()
            
            mode = row['setting_value'] if row else 'mock'
        except:
            mode = 'mock'
        
        if mode == 'live':
            return SerpApiProvider()
        else:
            return MockProvider()