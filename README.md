# Fuel Route Optimizer API

A robust Django REST Framework backend service designed to optimize commercial long-distance truck travel across the United States. The application dynamically plans cost-effective fuel stops by evaluating real-time trajectory geometry against dynamic fuel pricing datasets.

## 🚀 Core Features
* **Single-Call Routing Integration:** Communicates with the Open Source Routing Machine (OSRM) API to extract high-fidelity highway polylines (over 34,000 track points for coast-to-coast trips) in a single request.
* **Algorithmic Fuel Tracking:** Simulates vehicle progress sequentially using the Haversine distance formula to monitor fuel consumption dynamically.
* **Regional Price Optimization:** Monitors real-time regional intervals using a custom localized timeline match to identify and select the absolute lowest fuel prices from the dataset.
* **Strict Constraint Adherence:** Respects maximum vehicle capacities (500-mile max range), fuel safety buffers (75-mile reserve trigger), and averages calculations exactly at 10 MPG.

---

## 🛠️ Project Architecture
The project follows a clean, modular service-oriented architecture layout:
* `config/` - Core Django system settings and URL routing configurations.
* `fuel_optimizer/` - Main API application container.
  * `api/views.py` - Lean controller handling request parsing, OSRM execution, and response payloads.
  * `services/fuel_optimizer.py` - Core algorithmic business logic isolating tracking math and simulation workflows.
  * `services/csv_loader.py` - Smart repository layer featuring dynamic file auto-detection for the fuel pricing dataset.

---

## 💻 Local Setup & Installation

1. **Clone the Repository:**
   ```bash
   git clone [https://github.com/JanAli-socool/Fuel-Route-Optimizer-App.git](https://github.com/JanAli-socool/Fuel-Route-Optimizer-App.git)
   cd Fuel-Route-Optimizer-App
   ```

# Activate the Virtual Environment:
## Windows PowerShell / Command Prompt:
```bash
.\venv\Scripts\activate
```

## Install Project Dependencies:
```
pip install -r requirements.txt
```

## Boot the Development Server:
```
python manage.py runserver
```

# 📊 API Documentation
Optimize Route Stop Planner
Generates a complete refueling schedule map configuration between any two coordinate pairs within the United States.

Endpoint: POST /api/optimize-route/

Content-Type: application/json

Request Payload Example:
```bash
{
    "start_lat": 40.7128,
    "start_lon": -74.0060,
    "end_lat": 34.0522,
    "end_lon": -118.2437
}
```

Successful Response Schema (200 OK):
```bash
{
    "distance_miles": 2798.38,
    "estimated_cost": 746.72,
    "fuel_stops": [
        {
            "station_name": "HUCKS FOOD & FUEL #379",
            "address": "I-57, EXIT 53, Marion, IL",
            "latitude": 40.6331,
            "longitude": -89.3985,
            "price_per_gallon": 2.929,
            "gallons_pumped": 42.52
        }
        // ... subsequent optimized stops sequentially mapped along the timeline
    ],
    "route": {
        "code": "Ok",
        "routes": [
            {
                "geometry": {
                    "coordinates": [ [-74.005625, 40.712153], [-74.005693, 40.71213] ]
                }
            }
        ]
    }
}
```

# 🔧 Technologies Used:
``` Backend Framework: Django 5.2 & Django REST Framework (DRF) ```

``` Data Processing: Pandas Engine ```

```Geospatial Processing: Haversine Spherical Trigonometry Model ```

```External APIs: Open Source Routing Machine (OSRM) ```
