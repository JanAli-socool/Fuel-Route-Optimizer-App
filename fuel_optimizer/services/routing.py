import requests
from django.core.cache import cache

class RoutingService:
    
    @staticmethod
    def get_route(start, end):
        """
        Fetches route geometry and details using the free OSRM API.
        Expects start and end as tuples: (latitude, longitude)
        OSRM expects coordinates in format: longitude,latitude
        """
        # Format the URL inside the function so it can read 'start' and 'end' parameters dynamically
        url = f"http://router.project-osrm.org/route/v1/driving/{start[1]},{start[0]};{end[1]},{end[0]}"
        
        params = {
            "overview": "full",
            "geometries": "geojson"
        }
        
        try:
            response = requests.get(url, params=params)
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": "HTTP Request failed", "details": str(e)}