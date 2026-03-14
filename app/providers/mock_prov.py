import random
from app.providers.base import FlightProvider

class MockProvider(FlightProvider):
    Add search_flights method skeleton for mock provider
    airlines = [
    ("British Airways", "https://logo.clearbit.com/britishairways.com"),
    ("Delta Airlines", "https://logo.clearbit.com/delta.com"),
    ("Emirates", "https://logo.clearbit.com/emirates.com"),
    ("Lufthansa", "https://logo.clearbit.com/lufthansa.com"),
    ("Air France", "https://logo.clearbit.com/airfrance.com"),
    ("Virgin Atlantic", "https://logo.clearbit.com/virginatlantic.com")
]
    for _ in range(random.randint(4, 6)):
    airline_name, airline_logo = random.choice(airlines)
    price = random.randint(400, 1200)
    dep_h = random.randint(6, 22)
arr_h = (dep_h + random.randint(3, 12)) % 24
dep_min = random.choice(["00", "15", "30", "45"])
arr_min = random.choice(["00", "15", "30", "45"])

time_str = f"{dep_h:02}:{dep_min} - {arr_h:02}:{arr_min}"
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
results.sort(key=lambda x: x['price'])
return results