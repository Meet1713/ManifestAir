import time
import requests
from flask import current_app

# Simple in-memory cache to prevent wasting API credits
# Structure: {'rate': 1.35, 'timestamp': 1700000000}
_RATE_CACHE = {"rate": None, "timestamp": 0}
CACHE_DURATION = 3600  # 1 hour in seconds

def get_usd_to_cad_rate():
    """
    Fetches the live USD -> CAD rate from CurrencyAPI.
    Uses caching to limit API calls to once per hour.
    """
    global _RATE_CACHE
    
    # 1. Check Cache (Is it fresh?)
    if _RATE_CACHE["rate"] and (time.time() - _RATE_CACHE["timestamp"] < CACHE_DURATION):
        return _RATE_CACHE["rate"]

    # 2. Fetch from API
    api_key = current_app.config['CURRENCY_API_KEY']
    if not api_key:
        print("Warning: CURRENCY_API_KEY not found. Using fallback.")
        return _RATE_CACHE["rate"] or 1.40

    try:
        response = requests.get(
            "https://api.currencyapi.com/v3/latest",
            params={
                "apikey": api_key,
                "base_currency": "USD",
                "currencies": "CAD"
            },
            timeout=5
        )
        response.raise_for_status()
        data = response.json()
        
        # Extract rate
        rate = data['data']['CAD']['value']
        
        # Update Cache
        _RATE_CACHE["rate"] = rate
        _RATE_CACHE["timestamp"] = time.time()
        print(f"💵 Updated Currency Rate: 1 USD = {rate} CAD")
        return rate
        
    except Exception as e:
        print(f"❌ Currency API Error: {e}")
        # Return fallback if API fails (e.g. quota exceeded) to prevent app crash
        return _RATE_CACHE["rate"] or 1.40 

def to_cad(usd_amount):
    """Converts a USD amount to CAD using the current rate."""
    if usd_amount is None:
        return 0.0
    rate = get_usd_to_cad_rate()
    return round(float(usd_amount) * rate, 2)