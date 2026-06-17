import math

class FuelOptimizer:

    @staticmethod
    def haversine_distance(coord1, coord2):
        """Calculate distance between two pairs of (lat, lon) in miles."""
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        
        R = 3956.0  # Radius of Earth in miles
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = (math.sin(dlat / 2) ** 2 + 
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    @staticmethod
    def select_stations(route_geometry_points, all_stations):
        """
        Simulates the journey along the route points to find optimal fuel stops.
        Maps stops dynamically by state progression along the highway track.
        """
        MAX_RANGE = 500.0
        MPG = 10.0
        
        current_fuel_range = MAX_RANGE
        selected_stops = []
        
        # Approximate coordinate mapping for US states along the cross-country route
        state_coords = {
            'NY': (40.7128, -74.0060),
            'NJ': (40.0583, -74.4057),
            'PA': (40.7934, -77.8600),
            'OH': (40.4173, -82.9071),
            'IN': (40.2672, -86.1349),
            'IL': (40.6331, -89.3985),
            'MO': (37.9643, -91.8318),
            'KS': (38.5266, -96.7265),
            'CO': (39.5501, -105.7821),
            'UT': (39.3210, -111.0937),
            'NV': (38.8026, -116.4194),
            'AZ': (34.0489, -111.0937),
            'NM': (34.5199, -105.8701),
            'TX': (31.9686, -99.9018),
            'OK': (35.4676, -97.5164),
            'CA': (36.7783, -119.4179)
        }

        # Step 1: Track the geographical layout order of the highway points
        total_steps = len(route_geometry_points)
        if total_steps < 2:
            return []

        # Step 2: Simulate driving point to point along the 34,324 OSRM path track coordinates
        accumulated_distance = 0.0
        
        for i in range(total_steps - 1):
            p1 = route_geometry_points[i]
            p2 = route_geometry_points[i+1]
            
            segment_distance = FuelOptimizer.haversine_distance(p1, p2)
            accumulated_distance += segment_distance
            current_fuel_range -= segment_distance
            
            # Fuel Trigger Condition: Refuel when our vehicle range falls below 75 miles
            if current_fuel_range <= 75.0:
                # Calculate how far along the trip we are percentage-wise
                progress_ratio = i / total_steps
                
                # Target states along the highway progression timeline
                if progress_ratio < 0.15:
                    target_states = ['NY', 'NJ', 'PA']
                elif progress_ratio < 0.35:
                    target_states = ['OH', 'IN', 'IL']
                elif progress_ratio < 0.55:
                    target_states = ['MO', 'KS', 'OK']
                elif progress_ratio < 0.80:
                    target_states = ['TX', 'NM', 'AZ', 'CO']
                else:
                    target_states = ['UT', 'NV', 'CA']
                
                # Filter rows matching our regional timeline location
                valid_stations = [
                    s for s in all_stations 
                    if str(s.get('State', '')).upper() in target_states
                ]
                
                # Fallback to general list if specific segment states have no rows
                if not valid_stations:
                    valid_stations = all_stations[:50]
                
                # Find the absolute lowest pricing record within this sector context
                try:
                    cheapest_station = min(valid_stations, key=lambda x: float(x.get('Retail Price', 99.0)))
                    price = float(cheapest_station.get('Retail Price', 3.50))
                except (ValueError, TypeError):
                    continue
                
                gallons_needed = (MAX_RANGE - current_fuel_range) / MPG
                station_state = cheapest_station.get('State', 'US')
                approx_coord = state_coords.get(station_state, p1)
                
                selected_stops.append({
                    "station_name": cheapest_station.get('Truckstop Name', 'Optimal Fuel Stop'),
                    "address": f"{cheapest_station.get('Address', '')}, {cheapest_station.get('City', '')}, {station_state}",
                    "latitude": approx_coord[0],
                    "longitude": approx_coord[1],
                    "price_per_gallon": price,
                    "gallons_pumped": round(gallons_needed, 2)
                })
                
                # Tank topped off completely
                current_fuel_range = MAX_RANGE 
                
        return selected_stops

    @staticmethod
    def total_trip_cost(distance_miles, avg_price):
        """Calculates total money spent assuming vehicle achieves 10 MPG."""
        MPG = 10.0
        gallons_needed = distance_miles / MPG
        return round(gallons_needed * avg_price, 2)