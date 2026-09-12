"""Calculate nearest-POI Haversine distances for geocoded listings."""
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "deliveries/week06/data/raw"


def haversine(lat1, lon1, lat2, lon2):
    earth_radius_km = 6371.0088
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    return 2 * earth_radius_km * np.arcsin(np.sqrt(np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2))


def main():
    listings = pd.read_csv(RAW / "listings_geocoded.csv")
    pois = pd.read_csv(RAW / "pois_lima.csv")
    valid = listings.dropna(subset=["latitude", "longitude"]).copy()
    for category, group in pois.groupby("categoria"):
        distances = []
        for _, listing in valid.iterrows():
            distances.append(haversine(listing.latitude, listing.longitude, group.latitude.to_numpy(), group.longitude.to_numpy()).min())
        valid[f"dist_nearest_{category}_km"] = np.round(distances, 3)
    output = RAW / "listings_poi_distances.csv"
    valid.to_csv(output, index=False)
    print(f"{len(valid)} geocoded listings enriched -> {output}")


if __name__ == "__main__":
    main()