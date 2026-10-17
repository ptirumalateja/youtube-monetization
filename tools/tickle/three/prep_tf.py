#!/usr/bin/env python3
"""Time Flies rebuild: crush navy bg, depth map (Depth Anything V2 small onnx) -> assets/dreams/tf_<key>.jpg, tf_<key>_d.png, tf_meta.json
usage: python3 prep_tf.py <model.onnx> <raw_dir containing tfNN.jpg>"""
import sys, json, numpy as np, onnxruntime as ort
from PIL import Image, ImageFilter
model, raw = sys.argv[1:3]
K = {"phone": "tf04", "eyeA": "tf21", "eyeB": "tf20", "vortex": "tf22", "brain": "tf11", "runner": "tf29", "fly": "tf27", "swirl": "tf13", "strip": "tf30", "ribbon": "tf28",
     "geo": "tf06", "droste": "tf15", "gear": "tf09", "eye": "tf31", "density": "tf05"}
s = ort.InferenceSession(model); mean = np.array([0.485, 0.456, 0.406]); std = np.array([0.229, 0.224, 0.225]); meta = {}
for k, f in K.items():
    im = Image.open(f"{raw}/{f}.jpg").convert("RGB"); a = np.asarray(im).astype(float); h, w, _ = a.shape
    b = np.concatenate([a[:8].reshape(-1, 3), a[-8:].reshape(-1, 3), a[:, :8].reshape(-1, 3), a[:, -8:].reshape(-1, 3)]); bg = np.median(b, 0)
    o = Image.fromarray(np.clip((a - bg * 1.3 - 4) * 1.12, 0, 255).astype(np.uint8)); sc = 2400 / max(w, h)
    if sc < 1: o = o.resize((int(w * sc), int(h * sc)), Image.LANCZOS)
    o.save(f"assets/dreams/tf_{k}.jpg", quality=93)
    sc2 = 518 / min(w, h); nw, nh = max(14, int(w * sc2) // 14 * 14), max(14, int(h * sc2) // 14 * 14)
    x = (np.asarray(im.resize((nw, nh), Image.BICUBIC)).astype(np.float32) / 255 - mean) / std
    d = s.run(None, {"pixel_values": x.transpose(2, 0, 1)[None].astype(np.float32)})[0][0]
    lo, hi = np.percentile(d, 2), np.percentile(d, 98); d = np.clip((d - lo) / (hi - lo + 1e-6), 0, 1)
    dw = min(w, 1000); Image.fromarray((d * 255).astype(np.uint8)).resize((dw, int(dw * h / w)), Image.BICUBIC).filter(ImageFilter.GaussianBlur(1.5)).save(f"assets/dreams/tf_{k}_d.png")
    meta[k] = {"size": list(o.size)}; print(k, o.size, tuple(bg.round()))
json.dump(meta, open("assets/dreams/tf_meta.json", "w"))
