import numpy as np
import random
import requests
import folium
import time

centroids = np.load("gps_centroids.npy")

def get_road_distance(lat1, lon1, lat2, lon2):
    """Get actual road distance using OpenRouteService API"""
    try:
        # Free OpenRouteService API (no key required for basic usage)
        url = f"https://api.openrouteservice.org/v2/directions/driving-car"
        params = {
            'start': f"{lon1},{lat1}",
            'end': f"{lon2},{lat2}"
        }
        headers = {
            'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
        }
        
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            # Distance in meters, convert to km
            return data['features'][0]['properties']['segments'][0]['distance'] / 1000
        else:
            # Fallback to haversine if API fails
            from haversine import haversine, Unit
            return haversine((lat1, lon1), (lat2, lon2), unit=Unit.KILOMETERS)
    except:
        # Fallback to haversine if API fails
        from haversine import haversine, Unit
        return haversine((lat1, lon1), (lat2, lon2), unit=Unit.KILOMETERS)

def get_road_route(lat1, lon1, lat2, lon2):
    """Get actual road route coordinates"""
    try:
        url = f"https://api.openrouteservice.org/v2/directions/driving-car"
        params = {
            'start': f"{lon1},{lat1}",
            'end': f"{lon2},{lat2}"
        }
        headers = {
            'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
        }
        
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            coords = data['features'][0]['geometry']['coordinates']
            # Convert [lon, lat] to [lat, lon] for folium
            return [[coord[1], coord[0]] for coord in coords]
        else:
            return [[lat1, lon1], [lat2, lon2]]
    except:
        return [[lat1, lon1], [lat2, lon2]]

# Cache distances to avoid repeated API calls
distance_cache = {}

def cached_road_distance(i, j):
    if (i, j) in distance_cache:
        return distance_cache[(i, j)]
    if (j, i) in distance_cache:
        return distance_cache[(j, i)]
    
    lat1, lon1 = centroids[i]
    lat2, lon2 = centroids[j]
    dist = get_road_distance(lat1, lon1, lat2, lon2)
    distance_cache[(i, j)] = dist
    time.sleep(0.1)  # Rate limiting
    return dist

def total_distance(route):
    return sum(cached_road_distance(route[i], route[(i+1)%len(route)]) 
               for i in range(len(route)))

def mutate(route):
    a, b = random.sample(range(len(route)), 2)
    route[a], route[b] = route[b], route[a]

def crossover(p1, p2):
    start, end = sorted(random.sample(range(len(p1)), 2))
    child = [-1]*len(p1)
    child[start:end] = p1[start:end]
    ptr = 0
    for gene in p2:
        if gene not in child:
            while child[ptr] != -1:
                ptr += 1
            child[ptr] = gene
    return child

def genetic_algorithm(generations=100, pop_size=50):
    print("Calculating road distances...")
    population = [random.sample(range(len(centroids)), len(centroids)) for _ in range(pop_size)]
    
    for gen in range(generations):
        population = sorted(population, key=total_distance)
        if gen % 20 == 0:
            print(f"Generation {gen}, Best distance: {total_distance(population[0]):.2f} km")
        
        next_gen = population[:10]
        while len(next_gen) < pop_size:
            p1, p2 = random.choices(population[:20], k=2)
            child = crossover(p1, p2)
            if random.random() < 0.3:
                mutate(child)
            next_gen.append(child)
        population = next_gen
    
    return population[0]

print("Optimizing route with real road distances...")
best_route = genetic_algorithm()
print(f"Best route: {best_route}")
print(f"Total distance: {total_distance(best_route):.2f} km")

# Create map with actual road routes
m = folium.Map(location=centroids.mean(axis=0).tolist(), zoom_start=6)

# Add markers
for i, point in enumerate(centroids[best_route]):
    folium.Marker(
        location=point.tolist(), 
        tooltip=f"Stop {i}",
        icon=folium.Icon(color='red', icon='info-sign')
    ).add_to(m)

# Add road routes between consecutive points
print("Getting road routes for visualization...")
for i in range(len(best_route)):
    start_idx = best_route[i]
    end_idx = best_route[(i+1) % len(best_route)]
    
    lat1, lon1 = centroids[start_idx]
    lat2, lon2 = centroids[end_idx]
    
    route_coords = get_road_route(lat1, lon1, lat2, lon2)
    
    folium.PolyLine(
        route_coords,
        color="blue",
        weight=4,
        opacity=0.8
    ).add_to(m)
    
    time.sleep(0.1)  # Rate limiting

m.save("optimized_truck_roads_map.html")
print("Map saved as 'optimized_truck_roads_map.html'")