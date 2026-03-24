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

         # Better matching with Google Flights browser results
        self.force_fresh = os.environ.get("SERPAPI_FORCE_FRESH", "true").lower() == "true"
        self.deep_search = os.environ.get("SERPAPI_DEEP_SEARCH", "true").lower() == "true"

        # Booking-option enrichment
        self.enrich_booking = os.environ.get("SERPAPI_ENRICH_BOOKING", "true").lower() == "true"
        self.booking_details_limit = int(os.environ.get("SERPAPI_BOOKING_DETAILS_LIMIT", "5"))
        
    def _resolve_code(self, user_input):
        """Smart resolution: tries multiple strategies to find airport code"""
        if not user_input:
            return ""

        clean_input = user_input.lower().strip()
        
        if clean_input in ESSENTIAL_CITY_MAPPINGS: 
            return ESSENTIAL_CITY_MAPPINGS[clean_input]
        if len(clean_input) == 3 and clean_input.isalpha(): 
            return clean_input.upper()
        
        code = airport_db.get_airport_code(clean_input)
        if code: return code
        
        if ',' in clean_input:
            city_part = clean_input.split(',')[0].strip()
            if city_part in ESSENTIAL_CITY_MAPPINGS: 
                return ESSENTIAL_CITY_MAPPINGS[city_part]

            db_code = airport_db.get_airport_code(city_part)
            if db_code: return db_code
            
        for city, code in ESSENTIAL_CITY_MAPPINGS.items():
            if clean_input in city: 
                return code
            
        return clean_input.upper()

    def _build_base_params(self, origin_code, dest_code, depart_date, return_date=None):
        """Common parameters for Google Flights search."""
        params = {
            "engine": "google_flights",
            "departure_id": origin_code,
            "arrival_id": dest_code,
            "outbound_date": depart_date,
            "currency": "USD",
            "hl": "en",
            "api_key": self.api_key,
            "type": "1" if return_date else "2",
        }

        if return_date:
            params["return_date"] = return_date

        if self.deep_search:
            params["deep_search"] = "true"

        if self.force_fresh:
            params["no_cache"] = "true"

        return params

    def _extract_airlines(self, flight):
        """Return unique airline names from every leg."""
        airlines = []
        for leg in flight.get("flights", []):
            airline = leg.get("airline")
            if airline and airline not in airlines:
                airlines.append(airline)
        return airlines

    def _choose_logo(self, flight):
        """Pick the best available logo."""
        if flight.get("airline_logo"):
            return flight["airline_logo"]

        legs = flight.get("flights", [])
        if legs:
            return legs[0].get("airline_logo", "https://via.placeholder.com/32")

        return "https://via.placeholder.com/32"   


    def _build_provider_label(self, airlines, primary_airline=None):
        """Short airline label for the UI card."""
        if not airlines:
            return "Unknown Airline"
        if len(airlines) == 1:
            return airlines[0]
        lead = primary_airline if primary_airline else airlines[0]  
        return f"{lead} + {len(airlines) - 1} more"
        
    def _extract_time_from_legs(self, legs):
        """Return a simple departure-arrival time string."""
        try:
            if not legs:
                return "See Details"

            dep_full = legs[0].get("departure_airport", {}).get("time", "")
            arr_full = legs[-1].get("arrival_airport", {}).get("time", "")

            dep_time = dep_full.split(" ")[-1] if " " in dep_full else dep_full
            arr_time = arr_full.split(" ")[-1] if " " in arr_full else arr_full

            if dep_time and arr_time:
                return f"{dep_time} - {arr_time}"

            return "See Details"
        except Exception:
            return "See Details"

    def _flatten_booking_option(self, option):
        """
        Booking options commonly store details under 'together'.
        Fallback to the top level if needed.
        """
        if isinstance(option, dict) and isinstance(option.get("together"), dict):
            return option["together"]
        return option if isinstance(option, dict) else {}     

    def _fetch_booking_details(self, booking_token, google_flights_url, primary_airline):
        """
        Use booking_token to fetch booking options for the selected fare.

        SerpApi returns booking options only when booking_token is provided.
        Some options include booking_request metadata; if we cannot safely turn that
        into a browser-ready direct link, we fall back to the Google Flights URL.
        """
        default_payload = {
            "book_with": primary_airline,
            "book_with_is_airline": True,
            "booking_option_title": "",
            "booking_extensions": [],
            "deep_link": get_airline_link(primary_airline),
            "link_label": "Book on" + primary_airline,
            "booking_link_ready": True,
        }

        if not self.enrich_booking or not booking_token:
            return default_payload

        try:
            params = {
                "engine": "google_flights",
                "booking_token": booking_token,
                "currency": "USD",
                "hl": "en",
                "api_key": self.api_key,
            }

            if self.force_fresh:
                params["no_cache"] = "true"

            booking_result = serpapi.GoogleSearch(params).get_dict()
            options = booking_result.get("booking_options", [])

            if not options:
                return default_payload

            chosen = None
            fallback = None
            ready_fallback = None

            for option in options:
                flat = self._flatten_booking_option(option)
                if not flat:
                    continue

                if fallback is None:
                    fallback = flat

                booking_request = flat.get("booking_request", {}) or {}
                request_url = booking_request.get("url", "")
                post_data = booking_request.get("post_data", "")
                
                if request_url and not post_data and ready_fallback is None:
                    ready_fallback = flat
                seller = (flat.get("book_with") or "").strip().lower()
                primary = (primary_airline or "").strip().lower()

                # Prefer seller that matches the primary airline
                if seller and primary and primary in seller and request_url and not post_data:
                    chosen = flat
                    break

                # Or any airline-direct option
                if request_url and not post_data and chosen is None:
                    chosen = flat

            chosen = chosen or ready_fallback or fallback
            if not chosen:
                return default_payload

            booking_request = chosen.get("booking_request", {}) or {}
            request_url = booking_request.get("url", "")
            post_data = booking_request.get("post_data", "")

            # Safe browser link rule:
            # - if booking_request.url exists and there is NO post_data, use it directly
            # - if post_data exists, fall back to Google Flights result page
            if request_url and not post_data:
                deep_link = request_url
                link_label = "Select"
                booking_link_ready = True
            else:
                deep_link = google_flights_url or "#"
                link_label = "View on Google Flights"
                booking_link_ready = False

            return {
                "book_with": chosen.get("book_with", "Google Flights"),
                "book_with_is_airline": bool(chosen.get("airline", False)),
                "booking_option_title": chosen.get("option_title", ""),
                "booking_extensions": chosen.get("extensions", []),
                "deep_link": deep_link,
                "link_label": link_label,
                "booking_link_ready": booking_link_ready,
            }

        except Exception as e:
            print(f"⚠️ Booking enrichment failed: {e}")
            return default_payload    

    def _fetch_return_time(self, departure_token, origin_code, dest_code, depart_date, return_date):
        """Fetch return-leg times for a selected outbound itinerary."""
        if not departure_token:
            return None

        try:
            params = self._build_base_params(origin_code, dest_code, depart_date, return_date)
            params["departure_token"] = departure_token

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

    def search_flights(self, origin, destination, depart_date, return_date=None):
        if not self.api_key:
            print("❌ Error: SERPAPI_KEY not found.")
            return []

        origin_code = self._resolve_code(origin)
        dest_code = self._resolve_code(destination)
        print(f"✈️ Live Search: {origin} ({origin_code}) -> {destination} ({dest_code})")

        try:
            self._increment_api_counter()
        except Exception:
            pass

        params = self._build_base_params(origin_code, dest_code, depart_date, return_date)

        try:
            search = serpapi.GoogleSearch(params)
            results = search.get_dict()

            if "error" in results:
                print(f"❌ SerpApi Error: {results['error']}")
                return []

            sources = []
            if "best_flights" in results:
                sources.extend(results["best_flights"])
            if "other_flights" in results:
                sources.extend(results["other_flights"])

            if not sources:
                print("⚠️ Success but 0 flights found.")
                return []

            google_flights_url = results.get("search_metadata", {}).get("google_flights_url", "")

            flight_list = []

            for idx, flight in enumerate(sources):
                try:
                    airlines = self._extract_airlines(flight)

                    all_legs = flight.get("flights", [])
                    if all_legs:
                        longest_leg = max(all_legs, key=lambda leg: leg.get("duration", 0))
                        primary_airline = longest_leg.get("airline") or (airlines[0] if airlines else "Unknown Airline")
                    else:
                        primary_airline = airlines[0] if airlines else "Unknown Airline"

                    provider_label = self._build_provider_label(airlines, primary_airline)


                    duration_min = flight.get("total_duration", 0)
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
                            return_date=return_date,
                        )

                    booking_payload = {
                        "book_with": primary_airline,
                        "book_with_is_airline": True,
                        "booking_option_title": "",
                        "booking_extensions": [],
                        "deep_link": get_airline_link(primary_airline),
                        "link_label": "Book on" + primary_airline,
                        "booking_link_ready": True,
                    }

                    # Limit extra booking-option calls to control API usage
                    if idx < self.booking_details_limit:
                        booking_payload = self._fetch_booking_details(
                            booking_token=flight.get("booking_token"),
                            google_flights_url=google_flights_url,
                            primary_airline=primary_airline,
                        )

                    flight_list.append({
                        "provider": provider_label,
                        "primary_airline": primary_airline,
                        "all_airlines": airlines,
                        "all_airlines_text": ", ".join(airlines) if airlines else "Unknown",
                        "is_mixed_itinerary": len(airlines) > 1,
                        "logo": self._choose_logo(flight),
                        "price": float(flight.get("price", 0) or 0),
                        "stops": len(flight.get("layovers", [])),
                        "duration": f"{hours}h {mins}m",
                        "time": outbound_time,
                        "return_time": return_time,
                        "type": "Round Trip" if return_date else "One Way",
                        "deep_link": booking_payload["deep_link"],
                        "link_label": booking_payload["link_label"],
                        "booking_link_ready": booking_payload["booking_link_ready"],
                        "book_with": booking_payload["book_with"],
                        "book_with_is_airline": booking_payload["book_with_is_airline"],
                        "booking_option_title": booking_payload["booking_option_title"],
                        "booking_extensions": booking_payload["booking_extensions"],
                    })
                except Exception as e:
                    print(f"⚠️ Skipping flight due to parsing issue: {e}")
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
