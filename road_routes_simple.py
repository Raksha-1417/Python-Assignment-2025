import numpy as np
import requests
import folium
import time

centroids = np.load("gps_centroids.npy")

def get_osrm_route(lat1, lon1, lat2, lon2):
    """Get route using OSRM (Open Source Routing Machine)"""
    try:
        url = f"http://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}"
        params = {
            'overview': 'full',
            'geometries': 'geojson'
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data['routes']:
                coords = data['routes'][0]['geometry']['coordinates']
                # Convert [lon, lat] to [lat, lon]
                return [[coord[1], coord[0]] for coord in coords]
    except Exception as e:
        print(f"Error getting route: {e}")
    
    return [[lat1, lon1], [lat2, lon2]]

# Create map
m = folium.Map(location=centroids.mean(axis=0).tolist(), zoom_start=6)

# Add markers
for i, point in enumerate(centroids):
    folium.Marker(
        location=point.tolist(), 
        tooltip=f"Cluster {i}",
        icon=folium.Icon(color='red', icon='info-sign')
    ).add_to(m)

# Simple route order
route_order = [0, 1, 2, 3, 4, 0]  # Return to start

print("Getting road routes...")
for i in range(len(route_order) - 1):
    start_idx = route_order[i]
    end_idx = route_order[i + 1]
    
    lat1, lon1 = centroids[start_idx]
    lat2, lon2 = centroids[end_idx]
    
    print(f"Route {start_idx} -> {end_idx}")
    route_coords = get_osrm_route(lat1, lon1, lat2, lon2)
    
    folium.PolyLine(
        route_coords,
        color="red",
        weight=5,
        opacity=0.8
    ).add_to(m)
    
    time.sleep(0.5)  # Rate limiting

m.save("actual_road_routes.html")
print("Map saved as 'actual_road_routes.html'")
print(f"Total route segments: {len(route_order) - 1}")