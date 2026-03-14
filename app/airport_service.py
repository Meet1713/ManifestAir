class AirportDatabase:
    """
    A lightweight, in-memory database of airports to avoid external API calls for simple lookups.
    """
    def __init__(self):
        # A comprehensive mapping of City -> IATA Code
        self.airports = {
            # North America
            "atlanta": "ATL", "boston": "BOS", "chicago": "ORD", "dallas": "DFW", "denver": "DEN",
            "detroit": "DTW", "houston": "IAH", "las vegas": "LAS", "los angeles": "LAX", "miami": "MIA",
            "new york": "JFK", "nyc": "JFK", "newark": "EWR", "orlando": "MCO", "philadelphia": "PHL",
            "phoenix": "PHX", "san francisco": "SFO", "seattle": "SEA", "washington": "IAD", "dc": "IAD",
            "toronto": "YYZ", "vancouver": "YVR", "montreal": "YUL", "mexico city": "MEX", "cancun": "CUN",
            
            # Europe
            "amsterdam": "AMS", "athens": "ATH", "barcelona": "BCN", "berlin": "BER", "brussels": "BRU",
            "budapest": "BUD", "copenhagen": "CPH", "dublin": "DUB", "edinburgh": "EDI", "frankfurt": "FRA",
            "geneva": "GVA", "istanbul": "IST", "lisbon": "LIS", "london": "LHR", "madrid": "MAD",
            "manchester": "MAN", "milan": "MXP", "moscow": "SVO", "munich": "MUC", "oslo": "OSL",
            "paris": "CDG", "prague": "PRG", "rome": "FCO", "stockholm": "ARN", "vienna": "VIE",
            "warsaw": "WAW", "zurich": "ZRH",
            
            # Asia
            "bangkok": "BKK", "beijing": "PEK", "delhi": "DEL", "bali": "DPS", "dubai": "DXB",
            "hong kong": "HKG", "jakarta": "CGK", "kuala lumpur": "KUL", "manila": "MNL", "mumbai": "BOM",
            "osaka": "KIX", "seoul": "ICN", "shanghai": "PVG", "singapore": "SIN", "taipei": "TPE",
            "tokyo": "HND", "doha": "DOH",
            
            # Oceania
            "auckland": "AKL", "brisbane": "BNE", "melbourne": "MEL", "perth": "PER", "sydney": "SYD",
            
            # South America
            "bogota": "BOG", "buenos aires": "EZE", "lima": "LIM", "rio de janeiro": "GIG", 
            "santiago": "SCL", "sao paulo": "GRU",
            
            # Africa
            "cairo": "CAI", "cape town": "CPT", "casablanca": "CMN", "johannesburg": "JNB", 
            "lagos": "LOS", "nairobi": "NBO"
        }

    def get_airport_code(self, city_name):
        """Returns the IATA code for a given city name, or None if not found."""
        if not city_name:
            return None
        return self.airports.get(city_name.lower().strip())