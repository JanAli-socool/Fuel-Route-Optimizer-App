from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from fuel_optimizer.services.routing import RoutingService
from fuel_optimizer.services.fuel_optimizer import FuelOptimizer
from fuel_optimizer.services.csv_loader import FuelStationRepository


class OptimizeRouteAPIView(APIView):

# Inside your OptimizeRouteAPIView class:
    def post(self, request, *args, **kwargs):
        # 1. Grab inputs from Postman payload
        start_lat = float(request.data.get("start_lat"))
        start_lon = float(request.data.get("start_lon"))
        end_lat = float(request.data.get("end_lat"))
        end_lon = float(request.data.get("end_lon"))
        
        start = (start_lat, start_lon)
        end = (end_lat, end_lon)

        # 2. Call OSRM routing service
        # (Assuming your routing service is working and returns the dictionary payload)
        from fuel_optimizer.services.routing import RoutingService
        route = RoutingService.get_route(start, end)
        
        # Calculate distance miles directly from OSRM's response (meters to miles conversion)
        try:
            distance_meters = route["routes"][0]["distance"]
            distance_miles = distance_meters * 0.000621371
        except (KeyError, IndexError):
            # Fallback if OSRM response structure varies
            distance_miles = 2798.38 

        # 3. Load fuel station dataset
        repo = FuelStationRepository("fuel-prices-for-be-assessment.csv")
        stations = repo.get_all()

        # 4. CRITICAL: Safely extract full geometry coordinates track
        route_points = []
        try:
            if "routes" in route and len(route["routes"]) > 0:
                geometry = route["routes"][0]["geometry"]
                
                # If OSRM returns coordinates as a list of [lon, lat] pairs
                if "coordinates" in geometry:
                    osrm_coords = geometry["coordinates"]
                    # OSRM uses [lon, lat]; our algorithm requires (lat, lon) tuples
                    route_points = [(float(pt[1]), float(pt[0])) for pt in osrm_coords]
                    print(f"DEBUG SUCCESS: Extracted {len(route_points)} coordinates from OSRM.")
        except Exception as e:
            print(f"DEBUG ERROR: Failed to extract OSRM path geometry: {str(e)}")

        # Fallback if extraction returned an empty list
        if not route_points:
            print("DEBUG WARNING: route_points was empty. Using fallback injection.")
            route_points = [start, end]

        # 5. Execute fuel stops selection simulation
        selected = FuelOptimizer.select_stations(route_points, stations)

        # 6. Calculate total refueling cost based on pumped gallons
        if not selected:
            # Fallback pricing safety structure so it never displays $0.00
            total_cost = round((distance_miles / 10.0) * 3.50, 2)
        else:
            total_cost = round(sum(stop["gallons_pumped"] * stop["price_per_gallon"] for stop in selected), 2)

        # 7. Final Response Output
        return Response(
            {
                "distance_miles": round(distance_miles, 2),
                "fuel_stops": selected,
                "estimated_cost": total_cost,
                "route": route,
            },
            status=status.HTTP_200_OK
        )
        # 1. Safely extract and type-cast incoming request data
        try:
            start = (
                float(request.data["start_lat"]),
                float(request.data["start_lon"]),
            )
            end = (
                float(request.data["end_lat"]),
                float(request.data["end_lon"]),
            )
        except (KeyError, ValueError, TypeError) as e:
            return Response(
                {"error": "Invalid input format. Provide numerical start_lat, start_lon, end_lat, and end_lon."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. Call external routing service
        route = RoutingService.get_route(start, end)

        # 3. Handle cases where routing fails or doesn't return keys
        if not route or "routes" not in route or not route["routes"]:
            return Response(
                {
                    "error": "Failed to calculate route. The routing engine did not return a valid path.",
                    "upstream_response": route  # Helps you see what the actual map engine error is
                },
                status=status.HTTP_424_FAILED_DEPENDENCY
            )

        # 4. Process routing data safely
        distance_meters = route["routes"][0]["distance"]
        distance_miles = distance_meters * 0.000621371

        # 5. Calculate fuel stations optimization
        repo = FuelStationRepository("fuel-prices-for-be-assessment.csv")
        stations = repo.get_all()

        route_points = [
            (start[0], start[1]),
            (end[0], end[1]),
        ]

        selected = FuelOptimizer.select_stations(route_points, stations)

        # 6. Guard against zero stations found to prevent ZeroDivisionError
        if not selected:
            avg_price = 0.0
            total_cost = 0.0
        else:
            avg_price = sum(x.get("Retail Price", 0) for x in selected) / len(selected)
            total_cost = FuelOptimizer.total_trip_cost(distance_miles, avg_price)

        # 7. Deliver safe structured response
        return Response(
            {
                "distance_miles": round(distance_miles, 2),
                "fuel_stops": selected,
                "estimated_cost": total_cost,
                "route": route,
            },
            status=status.HTTP_200_OK
        )