"""Country outlines -> signed distance fields on the Lambert azimuthal equal-area plane (unit Earth sphere).
python3 make_sdf.py ne_10m_admin_0_countries_ind.geojson
Natural Earth 10m, India point-of-view edition: India includes all of J&K; Pakistan excludes Gilgit-Baltistan and PoK,
so no land is counted twice. Writes tex/sdf_<ISO>.f32 (S x S float32, Earth radii, negative inside) and tex/countries.json."""
import json, sys
import numpy as np
from matplotlib.path import Path
from scipy.ndimage import distance_transform_edt

S = 1024
OFFICIAL = {'IND': 3287263, 'PAK': 796095, 'BGD': 148460, 'NPL': 147181, 'LKA': 65610, 'BTN': 38394}   # km², World Bank 2024 (Pakistan without GB/PoK)
CTY = {'IND': 'India', 'PAK': 'Pakistan', 'BGD': 'Bangladesh', 'NPL': 'Nepal', 'LKA': 'Sri Lanka', 'BTN': 'Bhutan'}
d = json.load(open(sys.argv[1]))
meta = {}
for iso, name in CTY.items():
    geom = [f for f in d['features'] if f['properties']['NAME'] == name][0]['geometry']
    rings = geom['coordinates'] if geom['type'] == 'MultiPolygon' else [geom['coordinates']]
    polys = [np.radians(np.array(p[0])) for p in rings]
    allp = np.concatenate(polys)
    lon0, lat0 = allp[:, 0].mean(), allp[:, 1].mean()
    def laea(lon, lat):
        k = np.sqrt(2 / (1 + np.sin(lat0) * np.sin(lat) + np.cos(lat0) * np.cos(lat) * np.cos(lon - lon0)))
        return k * np.cos(lat) * np.sin(lon - lon0), k * (np.cos(lat0) * np.sin(lat) - np.sin(lat0) * np.cos(lat) * np.cos(lon - lon0))
    P = [np.stack(laea(p[:, 0], p[:, 1]), 1) for p in polys]
    ar = [0.5 * abs(np.sum(q[:, 0] * np.roll(q[:, 1], -1) - np.roll(q[:, 0], -1) * q[:, 1])) for q in P]
    area = sum(ar)
    cen = sum(q.mean(0) * a for q, a in zip(P, ar)) / area
    # centre on the main landmass's bbox so the outline sits in the middle of its tile
    main = P[int(np.argmax(ar))]; cen = (main.min(0) + main.max(0)) / 2
    sc = (OFFICIAL[iso] / (area * 6371.0088 ** 2)) ** .5          # outline scaled to the official area (coast/water differences)
    P = [(q - cen) * sc for q in P]; area *= sc * sc
    B = max(np.abs(np.concatenate(P)).max() * 1.08, 1e-4)
    xs = (np.arange(S) + .5) / S * 2 * B - B
    X, Y = np.meshgrid(xs, xs); pts = np.stack([X.ravel(), Y.ravel()], 1)
    inside = np.zeros(S * S, bool)
    for q in P: inside ^= Path(q).contains_points(pts)
    inside = inside.reshape(S, S)
    sdf = (distance_transform_edt(~inside) - distance_transform_edt(inside)) * (2 * B / S)
    sdf.astype(np.float32).tofile(f'tex/sdf_{iso}.f32')
    w, h = (main.max(0) - main.min(0))
    rows = inside.sum(1); c = np.cumsum(rows[::-1])[::-1]
    meta[iso] = dict(name=name, B=float(B), IA=float(area), km2=float(area * 6371.0088 ** 2), asp=float(w / h),
                     ysplit=float(xs[np.argmin(abs(c - rows.sum() / 2))]))
    print(iso, round(area * 6371.0088 ** 2), round(w / h, 2), round(B, 4))
json.dump(meta, open('tex/countries.json', 'w'), indent=1)
