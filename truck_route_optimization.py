import numpy as np
import random
from haversine import haversine, Unit
import folium

centroids = np.load("gps_centroids.npy")

def geo_distance(p1, p2):
    return haversine(tuple(p1), tuple(p2), unit=Unit.KILOMETERS)

def total_distance(route):
    return sum(geo_distance(centroids[route[i]], centroids[route[(i+1)%len(route)]]) for i in range(len(route)))

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

def genetic_algorithm(generations=300, pop_size=80):
    population = [random.sample(range(len(centroids)), len(centroids)) for _ in range(pop_size)]
    for _ in range(generations):
        population = sorted(population, key=total_distance)
        next_gen = population[:10]
        while len(next_gen) < pop_size:
            p1, p2 = random.choices(population[:40], k=2)
            child = crossover(p1, p2)
            if random.random() < 0.3:
                mutate(child)
            next_gen.append(child)
        population = next_gen
    return population[0]

best_route = genetic_algorithm()

# Map
m = folium.Map(location=centroids.mean(axis=0).tolist(), zoom_start=13)
ordered_centroids = centroids[best_route + [best_route[0]]]
for i, point in enumerate(ordered_centroids):
    folium.Marker(location=point.tolist(), tooltip=f"Stop {i}").add_to(m)
    if i > 0:
        folium.PolyLine([ordered_centroids[i-1].tolist(), point.tolist()], color="blue").add_to(m)
m.save("optimized_truck_drone_map.html")