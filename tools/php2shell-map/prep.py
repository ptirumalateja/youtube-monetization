"""Build the dot-matrix world and the illustrative host set for the PHP2Shell reel.

Inputs (Natural Earth, public domain), fetched into data/:
  ne_50m_land.geojson, ne_50m_populated_places_simple.geojson
Output: data/world.npz with
  land  (N,2) lon/lat of land dots on a 1.1 degree grid
  hosts (M,2) lon/lat of illustrative "PHP host" points, clustered around cities
  order (M,)  infection time in [0,1] (spread order from the seed)
"""
import json, os
import numpy as np
from shapely.geometry import shape, Point
from shapely.prepared import prep
from shapely.ops import unary_union

D = os.path.join(os.path.dirname(__file__), "data")
rng = np.random.default_rng(7)

land = unary_union([shape(f["geometry"]) for f in json.load(open(f"{D}/ne_50m_land.geojson"))["features"]])
pl = prep(land)

step = 1.1
pts = []
for lat in np.arange(-56, 78, step):
    off = (step / 2) if int(round(lat / step)) % 2 else 0.0  # hex stagger
    for lon in np.arange(-180 + off, 180, step):
        if pl.contains(Point(lon, lat)):
            pts.append((lon, lat))
land_dots = np.array(pts, np.float32)
print("land dots", len(land_dots))

places = json.load(open(f"{D}/ne_50m_populated_places_simple.geojson"))["features"]
cities = np.array([(p["properties"]["longitude"], p["properties"]["latitude"], max(p["properties"]["pop_max"], 1e4)) for p in places])
w = cities[:, 2] ** 0.55
w /= w.sum()
M = 2600
idx = rng.choice(len(cities), M, p=w)
spread = 0.6 + 2.2 * rng.random(M) ** 2
hosts = cities[idx, :2] + rng.normal(0, 1, (M, 2)) * spread[:, None]
hosts[:, 1] = np.clip(hosts[:, 1], -55, 75)

# Spread order: grows outward from a seed in western Europe, with random long jumps
# (new clusters lighting up far away), so the map fills like a contagion.
seed = np.array([4.9, 52.4])
def gdist(a, b):
    la1, la2 = np.radians(a[..., 1]), np.radians(b[..., 1])
    dl = np.radians(a[..., 0] - b[..., 0])
    return np.degrees(np.arccos(np.clip(np.sin(la1) * np.sin(la2) + np.cos(la1) * np.cos(la2) * np.cos(dl), -1, 1)))
jump_seeds = np.array([[-74, 40.7], [139.7, 35.7], [77.2, 28.6], [-46.6, -23.5], [-118, 34], [116.4, 39.9],
                       [37.6, 55.8], [151.2, -33.9], [28, -26.2], [-99.1, 19.4], [103.8, 1.35], [31.2, 30]])
jump_t = np.array([0.18, 0.24, 0.3, 0.36, 0.28, 0.33, 0.21, 0.45, 0.48, 0.4, 0.38, 0.27])
d0 = gdist(hosts, seed[None]) / 180.0
t = d0 ** 0.8 * 0.9
for s, tj in zip(jump_seeds, jump_t):
    t = np.minimum(t, tj + (gdist(hosts, s[None]) / 180.0) ** 0.8 * 0.9)
t = t * (0.75 + 0.5 * rng.random(M))
order = np.argsort(t)
rank = np.empty(M); rank[order] = np.arange(M) / (M - 1)
# hosts[0] is the seed itself (first ping)
first = np.argmin(gdist(hosts, seed[None]))
rank[first] = 0.0
np.savez_compressed(f"{D}/world.npz", land=land_dots, hosts=hosts.astype(np.float32), order=rank.astype(np.float32), first=first)
print("hosts", M, "first", first, hosts[first])
