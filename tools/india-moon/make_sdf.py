"""India outline -> signed distance field on the Lambert azimuthal equal-area plane (unit Earth sphere).
python3 make_sdf.py ne_10m_admin_0_countries_ind.geojson   (Natural Earth 10m, India point of view: full J&K incl. Aksai Chin)
Writes tex/india_sdf.f32 (S x S float32, distance in Earth radii, negative inside) and tex/india_meta.json."""
import json, sys
import numpy as np
from matplotlib.path import Path
from scipy.ndimage import distance_transform_edt

S = 1024
d = json.load(open(sys.argv[1]))
geom = [f for f in d['features'] if f['properties']['NAME'] == 'India'][0]['geometry']
polys = [np.radians(np.array(p[0])) for p in geom['coordinates']]
# area-weighted centre on the sphere
allp = np.concatenate(polys); lon0, lat0 = np.radians(80.6), np.radians(22.9)
def laea(lon, lat):
    k = np.sqrt(2 / (1 + np.sin(lat0) * np.sin(lat) + np.cos(lat0) * np.cos(lat) * np.cos(lon - lon0)))
    return k * np.cos(lat) * np.sin(lon - lon0), k * (np.cos(lat0) * np.sin(lat) - np.sin(lat0) * np.cos(lat) * np.cos(lon - lon0))
P = [np.stack(laea(p[:, 0], p[:, 1]), 1) for p in polys]
area = sum(0.5 * abs(np.sum(q[:, 0] * np.roll(q[:, 1], -1) - np.roll(q[:, 0], -1) * q[:, 1])) for q in P)
cen = sum(q.mean(0) * 0.5 * abs(np.sum(q[:, 0] * np.roll(q[:, 1], -1) - np.roll(q[:, 0], -1) * q[:, 1])) for q in P) / area
P = [q - cen for q in P]
B = max(np.abs(np.concatenate(P)).max() * 1.08, 0.01)
xs = (np.arange(S) + .5) / S * 2 * B - B
X, Y = np.meshgrid(xs, xs)
pts = np.stack([X.ravel(), Y.ravel()], 1)
inside = np.zeros(S * S, bool)
for q in P: inside ^= Path(q).contains_points(pts)
inside = inside.reshape(S, S)
px = 2 * B / S
sdf = (distance_transform_edt(~inside) - distance_transform_edt(inside)) * px
sdf.astype(np.float32).tofile('tex/india_sdf.f32')
# y that splits the area in half (for the ".5" India on the Moon)
rows = inside.sum(1); c = np.cumsum(rows[::-1])[::-1]; ysplit = float(xs[np.argmin(abs(c - rows.sum() / 2))])
json.dump(dict(B=float(B), S=S, area_er2=float(area), area_km2=float(area * 6371.0088 ** 2), ysplit=ysplit, inside_frac=float(inside.mean())), open('tex/india_meta.json', 'w'), indent=1)
print(open('tex/india_meta.json').read())
from PIL import Image
Image.fromarray((np.clip(.5 - sdf / (B * .1), 0, 1) * 255).astype(np.uint8)[::-1]).save('/tmp/claude-0/india_sdf_preview.png')
