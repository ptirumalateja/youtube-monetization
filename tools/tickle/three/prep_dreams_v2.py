#!/usr/bin/env python3
"""Prep the Meta v2 (dreamer figure) frames: crop baked labels, crush the navy background so additive blending works, write assets/dreams/<key>.jpg + meta.json.
usage: python3 prep_dreams_v2.py <v2_dir>   (files named image_20261015_HHMMSS[_n].jpg as downloaded from Drive)"""
import sys, json, numpy as np
from PIL import Image
src = sys.argv[1]
# key -> (file, crop fractions l,t,r,b)
M = {
    "sleeper": ("144736", None), "bedfall": ("150303", None), "brain": ("145803", None), "island": ("145634", None),
    "stairs": ("150037", None), "moon": ("150038", None), "boat": ("144738_1", None), "corridor": ("150300", None),
    "collage": ("150315", (0.05, 0.05, 0.95, 0.96)), "whalecity": ("150542", None), "web": ("150256", (0, 0, 1, 0.93)),
    "heaven": ("145928", None), "eye": ("145844", None), "bed": ("144811", None), "faller": ("144737", None),
}
try: meta = json.load(open("assets/dreams/meta.json"))
except Exception: meta = {}
for k, (f, crop) in M.items():
    im = Image.open(f"{src}/image_20261015_{f}.jpg").convert("RGB")
    if crop: w, h = im.size; im = im.crop((int(crop[0] * w), int(crop[1] * h), int(crop[2] * w), int(crop[3] * h)))
    a = np.asarray(im).astype(float); h, w, _ = a.shape
    b = np.concatenate([a[:8].reshape(-1, 3), a[-8:].reshape(-1, 3), a[:, :8].reshape(-1, 3), a[:, -8:].reshape(-1, 3)])
    bg = np.median(b, 0); o = np.clip((a - bg * 1.3 - 4) * 1.12, 0, 255).astype(np.uint8)
    img = Image.fromarray(o); s = 1800 / max(w, h)
    if s < 1: img = img.resize((int(w * s), int(h * s)), Image.LANCZOS)
    img.save(f"assets/dreams/{k}.jpg", quality=93); meta[k] = list(img.size); print(k, img.size)
json.dump(meta, open("assets/dreams/meta.json", "w"))
