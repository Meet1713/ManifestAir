import random
from app.providers.base import FlightProvider

class MockProvider(FlightProvider):
    """
    A robust mock provider that generates realistic flight data 
    with working logos and prices.
    """
    # FIX: Added 'return_date=None' to accept the 4th argument and prevent the crash
    def search_flights(self, origin, destination, date, return_date=None):
        
        print(f"🧪 MOCK SEARCH: {origin} -> {destination} | Return: {return_date}")
        
        results = []
        
        # List of airlines with working Logo APIs
        airlines = [
            ("British Airways", "https://logo.clearbit.com/britishairways.com"),
            ("Delta Airlines", "https://logo.clearbit.com/delta.com"),
            ("Emirates", "https://logo.clearbit.com/emirates.com"),
            ("Lufthansa", "https://logo.clearbit.com/lufthansa.com"),
            ("Air France", "https://logo.clearbit.com/airfrance.com"),
            ("Virgin Atlantic", "https://logo.clearbit.com/virginatlantic.com")
        ]
        
        # Generate 4-6 random flight options
        for _ in range(random.randint(4, 6)):
            airline_name, airline_logo = random.choice(airlines)
            
            # Generate a realistic price (e.g., $400 - $1200)
            price = random.randint(400, 1200)
            
            # Create random times
            dep_h = random.randint(6, 22)
            arr_h = (dep_h + random.randint(3, 12)) % 24
            dep_min = random.choice(["00", "15", "30", "45"])
            arr_min = random.choice(["00", "15", "30", "45"])
            
            time_str = f"{dep_h:02}:{dep_min} - {arr_h:02}:{arr_min}"
            
            # Build the flight object
            flight = {
                'provider': airline_name,
                'logo': airline_logo,
                'price': price,
                'stops': random.choice([0, 1]), 
                'duration': f"{random.randint(5, 14)}h {random.randint(10, 50)}m",
                'time': time_str,
                'type': 'Round Trip' if return_date else 'One Way',
                'deep_link': "#" 
            }
            
            results.append(flight)
            
        # Sort by price (Cheapest first)
        results.sort(key=lambda x: x['price'])
        
        return results