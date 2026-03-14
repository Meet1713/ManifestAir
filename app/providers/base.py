from abc import ABC

class FlightProvider(ABC):
    @abstractmethod
def search_flights(self, origin, destination, date):