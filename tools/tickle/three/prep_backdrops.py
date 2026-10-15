#!/usr/bin/env python3
"""Backdrop plates for the v3 worlds: crush navy bg, downscale -> assets/dreams/v3b_<key>.jpg + v3b_meta.json.
usage: python3 prep_backdrops.py <v1_raw_dir> <v2_dir> <v3_raw_dir>"""
import sys, json, os, numpy as np
from PIL import Image
v1, v2, v3 = sys.argv[1:4]
B = {"portal": (v1, "image_20261015_142121"), "face": (v1, "image_20261015_142125_1"), "clocks": (v3, "image_20261015_153813_1"), "moon": (v2, "image_20261015_150038"),
     "vortex": (v1, "image_20261015_142115"), "throat": (v3, "image_20261015_153806"), "heart": (v1, "image_20261015_142117"), "deja": (v3, "image_20261015_153843"),
     "collage": (v2, "image_9eddf1-also-somethng-like-these-5-frames-2"), "train": (v1, "image_20261015_141443"), "city": (v1, "image_20261015_142125"), "brainc": (v1, "image_20261015_142114_1"),
     "heaven": (v2, "image_20261015_145928"), "brainteal": (v1, "image_20261015_141435"), "stairsc": (v1, "image_20261015_142126"), "bed": (v2, "image_20261015_144811")}
meta = {}
for k, (d, f) in B.items():
    im = Image.open(f"{d}/{f}.jpg").convert("RGB"); a = np.asarray(im).astype(float); h, w, _ = a.shape
    b = np.concatenate([a[:8].reshape(-1, 3), a[-8:].reshape(-1, 3), a[:, :8].reshape(-1, 3), a[:, -8:].reshape(-1, 3)]); bg = np.median(b, 0)
    o = Image.fromarray(np.clip((a - bg * 1.3 - 4) * 1.12, 0, 255).astype(np.uint8)); s = 1400 / max(w, h)
    if s < 1: o = o.resize((int(w * s), int(h * s)), Image.LANCZOS)
    o.save(f"assets/dreams/v3b_{k}.jpg", quality=90); meta[k] = list(o.size); print(k, o.size)
json.dump(meta, open("assets/dreams/v3b_meta.json", "w"))
