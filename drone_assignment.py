import numpy as np
from haversine import haversine, Unit

MAX_RANGE_KM = 3.0

points = np.load("gps_points.npy")
centroids = np.load("gps_centroids.npy")
labels = np.load("labels.npy")

clusters = {i: [] for i in range(len(centroids))}
unassigned = []

for i, point in enumerate(points):
    cluster_id = labels[i]
    center = centroids[cluster_id]
    dist = haversine(tuple(point), tuple(center), unit=Unit.KILOMETERS)
    if dist <= MAX_RANGE_KM:
        clusters[cluster_id].append(point.tolist())
    else:
        unassigned.append(point.tolist())

print("Drone-Assigned Deliveries per Cluster:")
for cid, pts in clusters.items():
    print(f"Cluster {cid}: {len(pts)} deliveries")
print(f"Unassigned Deliveries (Out of Drone Range): {len(unassigned)}")