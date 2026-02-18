from typing import List, Dict, Optional
import requests
from app.core.config import settings

def ns_virtualcare_info() -> Dict:
    return {
        "program": "VirtualCareNS",
        "summary": (
            "VirtualCareNS provides Nova Scotians virtual access to a primary care provider. "
            "Eligibility and coverage depend on enrollment/registry status and provincial rules."
        ),
        "official_pages": [
            "https://www.nshealth.ca/virtual-care",
            "https://actionforhealth.novascotia.ca/virtualcarens",
            "https://www.nshealth.ca/accessing-virtual-care-attached-patients",
        ],
    }

def google_places_text_search(query: str, location: Optional[str], radius_m: int = 8000) -> List[Dict]:
    """
    Requires GOOGLE_MAPS_API_KEY.
    """
    if not settings.google_maps_api_key:
        return [{"note": "Google Places not enabled. Set GOOGLE_MAPS_API_KEY to use this tool."}]

    
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {"query": query, "key": settings.google_maps_api_key}
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    data = r.json()
    results = []
    for item in data.get("results", [])[:8]:
        results.append({
            "name": item.get("name"),
            "address": item.get("formatted_address"),
            "rating": item.get("rating"),
            "place_id": item.get("place_id"),
        })
    return results
