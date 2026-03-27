import requests

# Unsplash Access Key
UNSPLASH_ACCESS_KEY = os.environ.get('UNSPLASH_ACCESS_KEY')

def fetch_city_image(city_name):
    """
    Fetches a random, high-quality landscape photo of the specified city 
    using the Unsplash JSON API.
    """
    url = "https://api.unsplash.com/photos/random"
    params = {
        "query": f"{city_name}, landmark, travel", # Keywords to ensure good travel photos
        "orientation": "landscape",
        "client_id": UNSPLASH_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            # Return the 'regular' size URL (best balance of quality/speed)
            return data['urls']['regular']
        else:
            print(f"Unsplash API Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print(f"Unsplash Connection Error: {e}")
        return None
