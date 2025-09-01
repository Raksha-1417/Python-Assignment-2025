import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import folium

# Load delivery data
df = pd.read_csv("amazon_delivery copy.csv")
df = df[['Store_Latitude', 'Store_Longitude']].dropna()
df = df[(df['Store_Latitude'] != 0) & (df['Store_Longitude'] != 0)]
df = df.head(100)  # Limit to 100 points for performance

points = df.values

# KMeans clustering
k = 5
kmeans = KMeans(n_clusters=k, random_state=42)
labels = kmeans.fit_predict(points)
centroids = kmeans.cluster_centers_

# Save results
np.save("gps_points.npy", points)
np.save("gps_centroids.npy", centroids)
np.save("labels.npy", labels)

# Optional: visualize on map
m = folium.Map(location=[points[:,0].mean(), points[:,1].mean()], zoom_start=13)
colors = ['red', 'blue', 'green', 'purple', 'orange']
for i, point in enumerate(points):
    folium.CircleMarker(location=point, radius=3, color=colors[labels[i] % len(colors)], fill=True).add_to(m)
for i, center in enumerate(centroids):
    folium.Marker(location=center.tolist(), icon=folium.Icon(color='black', icon='cloud')).add_to(m)
m.save("kmeans_map.html")