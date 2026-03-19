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
            if clean_input in city: 
                return code
            
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
        except Exception:
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

            sources = []
            
            if 'best_flights' in results: 
                sources.extend(results['best_flights'])
            if 'other_flights' in results: 
                sources.extend(results['other_flights'])

            if not sources:
                print("⚠️ Success but 0 flights found.")
                return []

            flight_list = []

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
                    
                    outbound_time = self._extract_time_from_legs(flight.get("flights", []))
                    return_time = None

                    if return_date:
                        return_time = self._fetch_return_time(
                            departure_token=flight.get("departure_token"),
                            origin_code=origin_code,
                            dest_code=dest_code,
                            depart_date=depart_date,
                            return_date=return_date
                        )
                    # GET DIRECT AIRLINE LINK
                    booking_link = get_airline_link(airline_name)

                    flight_list.append({
                        'provider': airline_name,
                        'logo': airline_logo,
                        'price': flight.get('price', 0),
                        'stops': len(flight.get('layovers', [])),
                        'duration': f"{hours}h {mins}m",
                        'time': outbound_time,
                        'return_time': return_time,
                        'deep_link': booking_link,
                        'type': 'Round Trip' if return_date else 'One Way'
                    })
                except Exception as e:
                    print(f"⚠️ Skipping flight due to parsing issue: {e}")
                    continue

            return flight_list

        except Exception as e:
            print(f"❌ Critical Failure: {e}")
            return []

    def _fetch_return_time(self, departure_token, origin_code, dest_code, depart_date, return_date):
        """Fetch return-leg options for a selected outbound itinerary."""
        if not departure_token:
            return None

        try:
            params = {
                "engine": "google_flights",
                "departure_id": origin_code,
                "arrival_id": dest_code,
                "outbound_date": depart_date,
                "return_date": return_date,
                "currency": "USD",
                "hl": "en",
                "api_key": self.api_key,
                "type": "1",
                "departure_token": departure_token
            }

            search = serpapi.GoogleSearch(params)
            result = search.get_dict()

            return_sources = []
            if "best_flights" in result:
                return_sources.extend(result["best_flights"])
            if "other_flights" in result:
                return_sources.extend(result["other_flights"])

            if not return_sources:
                return None

            first_return = return_sources[0]
            return self._extract_time_from_legs(first_return.get("flights", []))

        except Exception as e:
            print(f"⚠️ Could not fetch return flight times: {e}")
            return None

    def _extract_time_from_legs(self, legs):
        try:
            if not legs:
                return "See Details"

            dep_full = legs[0].get('departure_airport', {}).get('time', '')
            arr_full = legs[-1].get('arrival_airport', {}).get('time', '')

            if not dep_full:
                dep_full = legs[0].get('departure_token', '')
            if not arr_full:
                arr_full = legs[-1].get('arrival_token', '')

            dep_time = dep_full.split(' ')[-1] if ' ' in dep_full else dep_full
            arr_time = arr_full.split(' ')[-1] if ' ' in arr_full else arr_full

            if dep_time and arr_time:
                return f"{dep_time} - {arr_time}"

            return "See Details"
        except Exception:
            return "See Details"
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

    