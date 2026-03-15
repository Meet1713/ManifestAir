import random
from app.db import get_db

# A robust list of Canadian cities with pre-verified Pexels images
# This bypasses the need for external APIs that might fail (401/404)
CANADIAN_DESTINATIONS = [
    {
        "city": "Toronto",
        "country": "Canada",
        "image": "https://images.pexels.com/photos/374870/pexels-photo-374870.jpeg?auto=compress&cs=tinysrgb&w=800"
    },
    {
        "city": "Vancouver",
        "country": "Canada",
        "image": "https://images.pexels.com/photos/2506923/pexels-photo-2506923.jpeg?auto=compress&cs=tinysrgb&w=800"
    },
    {
        "city": "Montreal",
        "country": "Canada",
        "image": "https://images.pexels.com/photos/11252370/pexels-photo-11252370.jpeg?auto=compress&cs=tinysrgb&w=800"
    },
    {
        "city": "Banff",
        "country": "Canada",
        "image": "https://images.pexels.com/photos/417074/pexels-photo-417074.jpeg?auto=compress&cs=tinysrgb&w=800"
    },
    {
        "city": "Quebec City",
        "country": "Canada",
        "image": "https://images.pexels.com/photos/3076127/pexels-photo-3076127.jpeg?auto=compress&cs=tinysrgb&w=800"
    },
    {
        "city": "Niagara Falls",
        "country": "Canada",
        "image": "https://images.pexels.com/photos/158398/niagara-falls-waterfall-horseshoe-158398.jpeg?auto=compress&cs=tinysrgb&w=800"
    },
    {
        "city": "Victoria",
        "country": "Canada",
        "image": "https://images.pexels.com/photos/18357183/pexels-photo-18357183/free-photo-of-fairmont-empress-hotel-in-victoria-in-canada.jpeg?auto=compress&cs=tinysrgb&w=800"
    },
    {
        "city": "Whistler",
        "country": "Canada",
        "image": "https://images.pexels.com/photos/831889/pexels-photo-831889.jpeg?auto=compress&cs=tinysrgb&w=800"
    }
]

def refresh_trending_destinations(count=4):
    """
    Wipes the current popular destinations and inserts new random ones
    from our internal high-quality list.
    """
    # 1. Pick random unique cities
    selected = random.sample(CANADIAN_DESTINATIONS, min(count, len(CANADIAN_DESTINATIONS)))
    
    db = get_db()
    cursor = db.cursor()
    
    # 2. Clear existing
    cursor.execute("DELETE FROM destinations")
    
    success_count = 0
    print(f"🔄 Injecting {len(selected)} trending destinations...")
    
    for dest in selected:
        # Generate Random Deal Price
        price = random.randint(150, 900)
        
        # Save to DB
        cursor.execute(
            "INSERT INTO destinations (city, country, price_estimate, image_url) VALUES (%s, %s, %s, %s)",
            (dest['city'], dest['country'], price, dest['image'])
        )
        success_count += 1
        print(f"   ✅ Added: {dest['city']} (${price})")
        
    db.commit()
    return success_count
