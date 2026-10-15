#!/usr/bin/env python3
"""Convert an outline-only hand image into the master dense contour-line style (iso-distance lines inside the silhouette,
like the Meta 'contour hand'). usage: python3 outline_to_contours.py <img> <out_prefix> --bg x,y [--bg x,y ...] [--thr 110]
  [--exclude x0,y0,x1,y1 ...] [--step 6] [--keep-largest] ; outputs <prefix>_mask.png, <prefix>_lines.png (RGBA white lines)"""
import sys, argparse
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
from skimage import measure
ap = argparse.ArgumentParser(); ap.add_argument("img"); ap.add_argument("out")
ap.add_argument("--bg", action="append", default=[]); ap.add_argument("--thr", type=float, default=110)
ap.add_argument("--exclude", action="append", default=[]); ap.add_argument("--step", type=float, default=6.0)
ap.add_argument("--seed", action="append", default=[], help="x,y inside the hand to keep (component)")
a = ap.parse_args()
im = Image.open(a.img).convert("RGB"); arr = np.asarray(im).astype(float); H, W = arr.shape[:2]
lum = arr.max(2)
line = lum > a.thr
for e in a.exclude:
    x0, y0, x1, y1 = map(int, e.split(",")); line[y0:y1, x0:x1] = False
line = ndi.binary_dilation(line, iterations=3)
lab, n = ndi.label(~line)
bgids = {lab[int(p.split(",")[1]), int(p.split(",")[0])] for p in a.bg}
bg = np.isin(lab, [i for i in bgids if i > 0])
hand = ~bg
hand = ndi.binary_opening(hand, iterations=2)
for e in a.exclude:
    x0, y0, x1, y1 = map(int, e.split(",")); hand[y0:y1, x0:x1] = False
lab2, n2 = ndi.label(hand)
if a.seed:
    keep = {lab2[int(s.split(",")[1]), int(s.split(",")[0])] for s in a.seed}
    hand = np.isin(lab2, [k for k in keep if k > 0])
else:
    sizes = ndi.sum(hand, lab2, range(1, n2 + 1)); hand = lab2 == (1 + int(np.argmax(sizes)))
Image.fromarray((hand * 255).astype(np.uint8)).save(f"{a.out}_mask.png")
dist = ndi.gaussian_filter(ndi.distance_transform_edt(np.pad(hand, 1, constant_values=False))[1:-1, 1:-1], 1.0)
S = 2; big = Image.new("L", (W * S, H * S), 0); d = ImageDraw.Draw(big)
for lvl in np.arange(1.5, dist.max(), a.step):
    for c in measure.find_contours(dist, lvl):
        if len(c) < 12: continue
        c = measure.approximate_polygon(c, 0.6)
        d.line([(x * S, y * S) for y, x in c], fill=255, width=2 if lvl > 2 else 4, joint="curve")
al = np.asarray(big.resize((W, H), Image.LANCZOS))
out = np.zeros((H, W, 4), np.uint8); out[..., :3] = 255; out[..., 3] = al
Image.fromarray(out, "RGBA").save(f"{a.out}_lines.png")
print("hand px", int(hand.sum()), "maxdist", float(dist.max()))
