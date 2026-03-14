import requests
from flask import current_app

def get_destination_image(query):
    """
    Fetches a high-quality image url for a city from Unsplash.
    Falls back to a placeholder if the API fails or quota is exceeded.
    """
    access_key = current_app.config['UNSPLASH_ACCESS_KEY']
    url = f"https://api.unsplash.com/search/photos"
    params = {
        "query": query,
        "orientation": "landscape",
        "per_page": 1,
        "client_id": access_key
    }
    
    try:
        response = requests.get(url, params=params, timeout=3)
        data = response.json()
        if data['results']:
            return data['results'][0]['urls']['regular']
    except Exception as e:
        print(f"Unsplash API Error: {e}")
    
    # Elegant fallback image (Cloudy Sky)
    return "https://images.unsplash.com/photo-1464037866556-56549c738148?q=80&w=1000&auto=format&fit=crop"