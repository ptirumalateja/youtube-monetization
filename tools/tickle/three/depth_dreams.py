#!/usr/bin/env python3
"""Depth maps for the Meta dream frames (Depth Anything V2 small, onnx). usage: python3 depth_dreams.py <model.onnx> <v2_raw_dir> <v1_raw_dir>
writes assets/dreams/<key>_d.png (8-bit, near=white). Same crops as prep_dreams_v2.py / the v1 prep."""
import sys, numpy as np, onnxruntime as ort
from PIL import Image, ImageFilter
model, v2, v1 = sys.argv[1:4]
J = {"sleeper": ("144736", None), "bedfall": ("150303", None), "brain": ("145803", None), "island": ("145634", None), "stairs": ("150037", None), "moon": ("150038", None), "boat": ("144738_1", None),
     "corridor": ("150300", None), "collage": ("150315", (0.05, 0.05, 0.95, 0.96)), "whalecity": ("150542", None), "web": ("150256", (0, 0, 1, 0.93)), "heaven": ("145928", None), "eye": ("145844", None), "bed": ("144811", None), "faller": ("144737", None),
     "heart": ("142117", "v1"), "wave": ("142124", "v1")}
s = ort.InferenceSession(model); mean = np.array([0.485, 0.456, 0.406]); std = np.array([0.229, 0.224, 0.225])
for k, (f, c) in J.items():
    path = f"{(v1 if c == 'v1' else v2)}/image_20261015_{f}.jpg"; im = Image.open(path).convert("RGB")
    if c and c != "v1": w, h = im.size; im = im.crop((int(c[0] * w), int(c[1] * h), int(c[2] * w), int(c[3] * h)))
    w, h = im.size; sc = 518 / min(w, h); nw, nh = max(14, int(w * sc) // 14 * 14), max(14, int(h * sc) // 14 * 14)
    x = (np.asarray(im.resize((nw, nh), Image.BICUBIC)).astype(np.float32) / 255 - mean) / std
    d = s.run(None, {"pixel_values": x.transpose(2, 0, 1)[None].astype(np.float32)})[0][0]
    lo, hi = np.percentile(d, 2), np.percentile(d, 98); d = np.clip((d - lo) / (hi - lo + 1e-6), 0, 1)
    out = Image.fromarray((d * 255).astype(np.uint8)).resize((min(w, 900), int(min(w, 900) * h / w)), Image.BICUBIC).filter(ImageFilter.GaussianBlur(1.2))
    out.save(f"assets/dreams/{k}_d.png"); print(k, out.size)
