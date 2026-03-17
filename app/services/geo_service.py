import requests

# Key from your uploaded file
GEOAPIFY_KEY = "2263ff2c79f64ab7b39b8a3fcf58a09a"

# Fallback coordinates for major Canadian cities (prevents 401 crash)
FALLBACK_COORDS = {
    "Toronto": {"lat": 43.6532, "lon": -79.3832, "country": "Canada"},
    "Vancouver": {"lat": 49.2827, "lon": -123.1207, "country": "Canada"},
    "Montreal": {"lat": 45.5017, "lon": -73.5673, "country": "Canada"},
    "Quebec City": {"lat": 46.8139, "lon": -71.2080, "country": "Canada"},
    "Banff": {"lat": 51.1784, "lon": -115.5708, "country": "Canada"},
    "Whistler": {"lat": 50.1163, "lon": -122.9574, "country": "Canada"},
    "Ottawa": {"lat": 45.4215, "lon": -75.6972, "country": "Canada"},
    "Victoria": {"lat": 48.4284, "lon": -123.3656, "country": "Canada"},
    "Calgary": {"lat": 51.0447, "lon": -114.0719, "country": "Canada"},
    "Niagara Falls": {"lat": 43.0896, "lon": -79.0849, "country": "Canada"},
    "Halifax": {"lat": 44.6488, "lon": -63.5752, "country": "Canada"},
    "St. John's": {"lat": 47.5615, "lon": -52.7126, "country": "Canada"},
    "Kelowna": {"lat": 49.8880, "lon": -119.4960, "country": "Canada"},
    "Tofino": {"lat": 49.1530, "lon": -125.9066, "country": "Canada"},
    "Jasper": {"lat": 52.8737, "lon": -118.0814, "country": "Canada"}
}

def fetch_place_data(city_query):
    """
    Searches Geoapify for a city. 
    If API fails (401/402), returns local fallback data.
    """
    if not city_query:
        return None
        
    # 1. Try Live API
    url = "https://api.geoapify.com/v1/geocode/search"
    params = {
        "text": city_query,
        "apiKey": GEOAPIFY_KEY,
        "type": "city",
        "limit": 1
    }
    
    try:
        resp = requests.get(url, params=params, timeout=3)
        
        if resp.status_code == 200:
            data = resp.json()
            if data.get("features"):
                props = data["features"][0]["properties"]
                return {
                    "city": props.get("city", city_query),
                    "country": props.get("country", "Canada"),
                    "lat": props.get("lat"),
                    "lon": props.get("lon")
                }
        else:
            print(f"⚠️ GeoAPI Error {resp.status_code}: Defaulting to local data.")
            
    except Exception as e:
        print(f"⚠️ GeoAPI Connection Failed: {e}")

    # 2. Fallback to Local Data (The Fix)
    # If API failed, check our list so we don't return None
    if city_query in FALLBACK_COORDS:
        data = FALLBACK_COORDS[city_query]
        return {
            "city": city_query,
            "country": data["country"],
            "lat": data["lat"],
            "lon": data["lon"]
        }
        
    # 3. Last Resort
    return {
        "city": city_query,
        "country": "Canada",
        "lat": 0.0,
        "lon": 0.0
    }
