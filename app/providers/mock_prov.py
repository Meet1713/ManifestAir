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