from abc import ABC, abstractmethod

class FlightProvider(ABC):
    @abstractmethod
    def search_flights(self, origin, destination, date):
        pass