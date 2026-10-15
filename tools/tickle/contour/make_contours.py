#!/usr/bin/env python3
"""Turn the approved hero-hand still into contour-line art (iso-distance lines) for the code renderer.
usage: python3 make_contours.py <hero.png> <out_dir>
Segmentation uses the thin red rim light around the hand (the background glow is brighter than the hand,
so luminance thresholds fail), closes it, flood-fills the outside, and keeps the largest component."""
import json, sys, os
import numpy as np
from PIL import Image, ImageFilter, ImageDraw
from scipy import ndimage as ndi
from skimage import measure

src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
im = Image.open(src).convert("RGB"); a = np.asarray(im).astype(int)
R, G, B = a[..., 0], a[..., 1], a[..., 2]
rim = (R > 120) & (G < 0.5 * R) & (B < 0.5 * R)
rim = ndi.binary_dilation(rim, iterations=3)
rim = ndi.binary_closing(rim, iterations=6)
# the skin itself (warm, mid-bright, not the amber background beam): saturation + hue
mx, mn = a.max(2), a.min(2)
sat = (mx - mn) / np.maximum(mx, 1)
skin = (sat > 0.22) & (R > G) & (G >= B * 0.7) & (mx > 14)
# restrict to the neighbourhood of the rim light so the amber background glow is never picked up
strict = (R > 120) & (G < 0.5 * R) & (B < 0.5 * R)
ys, xs = np.where(strict)
y0, y1, x0, x1 = max(0, ys.min() - 30), ys.max() + 30, max(0, xs.min() - 30), xs.max() + 30
box = np.zeros_like(rim); box[y0:y1, x0:x1] = True
mask = (rim | skin) & box
mask = ndi.binary_closing(mask, iterations=7)
mask = ndi.binary_fill_holes(mask)
mask = ndi.binary_opening(mask, iterations=4)
lab, n = ndi.label(mask)
sizes = ndi.sum(mask, lab, range(1, n + 1))
mask = lab == (1 + int(np.argmax(sizes)))
Image.fromarray((mask * 255).astype(np.uint8)).save(f"{out}/hand_mask.png")
dist = ndi.distance_transform_edt(mask)
dist = ndi.gaussian_filter(dist, 1.2)
step = float(os.environ.get("STEP", "7.0"))
polys = []
for lvl in np.arange(1.5, dist.max(), step):
    for c in measure.find_contours(dist, lvl):
        if len(c) < 20: continue
        c = measure.approximate_polygon(c, 0.8)
        polys.append({"d": float(lvl), "pts": [[round(float(x), 1), round(float(y), 1)] for y, x in c]})
json.dump({"w": im.size[0], "h": im.size[1], "polys": polys}, open(f"{out}/hand_contours.json", "w"))
# quick preview: contours in cream on dark
prev = Image.new("RGB", im.size, (8, 10, 14)); d = ImageDraw.Draw(prev)
for p in polys: d.line([tuple(q) for q in p["pts"]], fill=(232, 228, 208), width=2)
prev.save(f"{out}/hand_contours_preview.png")
bb = np.argwhere(mask); print("mask px", int(mask.sum()), "bbox", bb.min(0), bb.max(0), "polys", len(polys), "maxdist", float(dist.max()))
