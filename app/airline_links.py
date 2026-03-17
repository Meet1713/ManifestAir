"""
A dictionary mapping airline names to their official booking websites.
"""

AIRLINE_WEBSITES = {
    # North America  
    "Delta": "https://www.delta.com",
    "Delta Air Lines": "https://www.delta.com",
    "United": "https://www.united.com",
    "United Airlines": "https://www.united.com",
    "American Airlines": "https://www.aa.com",
    "Southwest Airlines": "https://www.southwest.com",
    "JetBlue": "https://www.jetblue.com",
    "Alaska Airlines": "https://www.alaskaair.com",
    "Air Canada": "https://www.aircanada.com",
    "WestJet": "https://www.westjet.com",
    "Spirit Airlines": "https://www.spirit.com",
    "Frontier Airlines": "https://www.flyfrontier.com",

    # Europe
    "British Airways": "https://www.britishairways.com",
    "Lufthansa": "https://www.lufthansa.com",
    "Air France": "https://wwws.airfrance.us",
    "KLM": "https://www.klm.com",
    "Ryanair": "https://www.ryanair.com",
    "EasyJet": "https://www.easyjet.com",
    "Turkish Airlines": "https://www.turkishairlines.com",
    "Swiss International Air Lines": "https://www.swiss.com",
    "Virgin Atlantic": "https://www.virginatlantic.com",
    "Aer Lingus": "https://www.aerlingus.com",
    "Iberia": "https://www.iberia.com",
    "SAS": "https://www.flysas.com",
    "TAP Air Portugal": "https://www.flytap.com",

    # Middle East & Asia
    "Emirates": "https://www.emirates.com",
    "Qatar Airways": "https://www.qatarairways.com",
    "Etihad Airways": "https://www.etihad.com",
    "Singapore Airlines": "https://www.singaporeair.com",
    "Cathay Pacific": "https://www.cathaypacific.com",
    "ANA": "https://www.ana.co.jp",
    "All Nippon Airways": "https://www.ana.co.jp",
    "Japan Airlines": "https://www.jal.co.jp",
    "Korean Air": "https://www.koreanair.com",
    "China Southern": "https://www.csair.com",
    "China Eastern": "https://us.ceair.com",
    "IndiGo": "https://www.goindigo.in",
    "Air India": "https://www.airindia.in",

    # Africa & Oceania
    "Ethiopian Airlines": "https://www.ethiopianairlines.com",
    "Kenya Airways": "https://www.kenya-airways.com",
    "South African Airways": "https://www.flysaa.com",
    "Royal Air Maroc": "https://www.royalairmaroc.com",
    "Qantas": "https://www.qantas.com",
    "Air New Zealand": "https://www.airnewzealand.com"
}

def get_airline_link(airline_name):
    """
    Returns the official website for the airline.
    If unknown, returns a Google Search link for the airline.
    """
    if not airline_name or airline_name == "Unknown Airline":
        return "https://www.google.com/flights"
        
    # clean name
    clean_name = airline_name.strip()
    
    # Try exact match
    if clean_name in AIRLINE_WEBSITES:
        return AIRLINE_WEBSITES[clean_name]
    
    # Try partial match (e.g. "Delta" inside "Delta Airlines")
    for key, url in AIRLINE_WEBSITES.items():
        if key in clean_name or clean_name in key:
            return url
            
    # Fallback: Google Search
    # e.g. https://www.google.com/search?q=book+flight+Lufthansa
    query = f"book flight {clean_name}".replace(" ", "+")
    return f"https://www.google.com/search?q={query}"
