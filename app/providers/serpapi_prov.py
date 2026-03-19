import os
import serpapi
from app.db import get_db
from app.airport_service import AirportDatabase
from app.airline_links import get_airline_link

# Initialize airport database
airport_db = AirportDatabase()

# Keep essential mappings for speed
ESSENTIAL_CITY_MAPPINGS = {
    "new york": "JFK", "london": "LHR", "tokyo": "HND", "paris": "CDG",
    "dubai": "DXB", "singapore": "SIN", "bangkok": "BKK", "hong kong": "HKG",
    "seoul": "ICN", "miami": "MIA", "los angeles": "LAX", "chicago": "ORD",
    "toronto": "YYZ", "regina": "YQR", "vancouver": "YVR", "ahmedabad": "AMD", "sydney": "SYD", "mumbai": "BOM", "delhi": "DEL",
    "shanghai": "PVG", "beijing": "PEK", "moscow": "SVO", "istanbul": "IST",
    "amsterdam": "AMS", "frankfurt": "FRA", "madrid": "MAD", "rome": "FCO",
    "barcelona": "BCN", "milan": "MXP", "munich": "MUC", "zurich": "ZRH",
    "vienna": "VIE", "prague": "PRG", "warsaw": "WAW", "budapest": "BUD",
    "athens": "ATH", "lisbon": "LIS", "brussels": "BRU", "copenhagen": "CPH",
    "stockholm": "ARN", "oslo": "OSL", "helsinki": "HEL", "dublin": "DUB",
    "manchester": "MAN", "edinburgh": "EDI", "birmingham": "BHX", "glasgow": "GLA",
    "bristol": "BRS", "liverpool": "LPL", "newcastle": "NCL", "leeds": "LBA",
    "nottingham": "EMA", "sheffield": "DSA", "nairobi": "NBO"
}

class SerpApiProvider:
    def __init__(self):
        self.api_key = os.environ.get('SERPAPI_KEY')
        
    def _resolve_code(self, user_input):
        """Smart resolution: tries multiple strategies to find airport code"""
        if not user_input: return ""
        clean_input = user_input.lower().strip()
        
        if clean_input in ESSENTIAL_CITY_MAPPINGS: return ESSENTIAL_CITY_MAPPINGS[clean_input]
        if len(clean_input) == 3 and clean_input.isalpha(): return clean_input.upper()
        
        code = airport_db.get_airport_code(clean_input)
        if code: return code
        
        if ',' in clean_input:
            city_part = clean_input.split(',')[0].strip()
            if city_part in ESSENTIAL_CITY_MAPPINGS: return ESSENTIAL_CITY_MAPPINGS[city_part]
            db_code = airport_db.get_airport_code(city_part)
            if db_code: return db_code
            
        for city, code in ESSENTIAL_CITY_MAPPINGS.items():
            if clean_input in city: return code
            
        return clean_input.upper()

    def search_flights(self, origin, destination, depart_date, return_date=None):
        if not self.api_key:
            print("❌ Error: SERPAPI_KEY not found.")
            return []

        # 1. Resolve Locations
        origin_code = self._resolve_code(origin)
        dest_code = self._resolve_code(destination)
        print(f"✈️ Live Search: {origin} ({origin_code}) -> {destination} ({dest_code})")

        # 2. Update DB Counter
        try:
            self._increment_api_counter()
        except:
            pass

        # 3. Determine Trip Type Logic
        # Google Flights Type: 1 = Round Trip, 2 = One Way
        flight_type = "1" if return_date else "2"

        # 4. Parameters
        params = {
            "engine": "google_flights",
            "q": f"Flights from {origin_code} to {dest_code}",
            "departure_id": origin_code,
            "arrival_id": dest_code,
            "outbound_date": depart_date,
            "currency": "USD",
            "hl": "en",
            "api_key": self.api_key,
            "type": flight_type
        }

        if return_date:
            params["return_date"] = return_date

        try:
            search = serpapi.GoogleSearch(params)
            results = search.get_dict()
            
            if "error" in results:
                print(f"❌ SerpApi Error: {results['error']}")
                return []

            flight_list = []
            sources = []
            
            if 'best_flights' in results: sources.extend(results['best_flights'])
            if 'other_flights' in results: sources.extend(results['other_flights'])

            if not sources:
                print("⚠️ Success but 0 flights found.")
                return []

            for flight in sources:
                try:
                    airline_name = "Unknown Airline"
                    airline_logo = "https://via.placeholder.com/32"
                    
                    if 'flights' in flight and len(flight['flights']) > 0:
                        first_leg = flight['flights'][0]
                        airline_name = first_leg.get('airline', airline_name)
                        airline_logo = first_leg.get('airline_logo', airline_logo)

                    duration_min = flight.get('total_duration', 0)
                    hours = duration_min // 60
                    mins = duration_min % 60
                    
                    # GET DIRECT AIRLINE LINK
                    booking_link = get_airline_link(airline_name)

                    flight_list.append({
                        'provider': airline_name,
                        'logo': airline_logo,
                        'price': flight.get('price', 0),
                        'stops': len(flight.get('layovers', [])),
                        'duration': f"{hours}h {mins}m",
                        'time': self._extract_time(flight), # <--- UPDATED LOGIC USED HERE
                        'deep_link': booking_link,
                        'type': 'Round Trip' if return_date else 'One Way'
                    })
                except:
                    continue

            return flight_list

        except Exception as e:
            print(f"❌ Critical Failure: {e}")
            return []

    def _increment_api_counter(self):
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO system_metrics (metric_key, metric_value, last_updated)
            VALUES ('api_usage_daily', 1, CURRENT_DATE)
            ON DUPLICATE KEY UPDATE
            metric_value = IF(last_updated = CURRENT_DATE, metric_value + 1, 1),
            last_updated = CURRENT_DATE
        """)
        db.commit()

    def _extract_time(self, flight):
        """
        Improved extraction: looks for 'departure_airport' -> 'time' first.
        """
        try:
            legs = flight.get('flights', [])
            if not legs: return "N/A"
            
            # Method 1: Look inside airport objects (Standard SerpApi format)
            # The format is usually "2026-02-02 10:00"
            dep_full = legs[0].get('departure_airport', {}).get('time', '')
            arr_full = legs[-1].get('arrival_airport', {}).get('time', '')
            
            # Method 2: Fallback to tokens if airport time is missing
            if not dep_full: dep_full = legs[0].get('departure_token', '')
            if not arr_full: arr_full = legs[-1].get('arrival_token', '')
            
            # Extract just the time part (HH:MM)
            dep_time = dep_full.split(' ')[-1] if ' ' in dep_full else dep_full
            arr_time = arr_full.split(' ')[-1] if ' ' in arr_full else arr_full
            
            if dep_time and arr_time:
                return f"{dep_time} - {arr_time}"
                
            return "See Details"
        except:
            return "See Details"