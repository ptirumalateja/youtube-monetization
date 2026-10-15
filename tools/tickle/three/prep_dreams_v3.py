#!/usr/bin/env python3
"""v3 prep: crop baked labels, crush navy bg (additive), depth map (Depth Anything V2 small onnx), figure anchor table.
usage: python3 prep_dreams_v3.py <model.onnx> <v2_raw_dir> [<v1_raw_dir>]  -> assets/dreams/v3_<key>.jpg, v3_<key>_d.png, v3_meta.json"""
import sys, json, numpy as np, onnxruntime as ort
from PIL import Image, ImageFilter
import os
model, v2 = sys.argv[1:3]; v3 = sys.argv[3] if len(sys.argv) > 3 else v2
# key: (file, crop l,t,r,b fractions, figure anchor (u,v) in the CROPPED image, figure height as fraction of image height)
K = {
    "bedfall": ("da1484-also-somethng-like-these-5-frames", None, (0.50, 0.30), 0.40),
    "brain": ("20261015_145754", None, (0.59, 0.62), 0.10),
    "island": ("20261015_145635", None, (0.476, 0.875), 0.07),
    "stairs": ("20261015_150037", None, (0.705, 0.658), 0.05),
    "moon": ("20261015_150038", None, (0.677, 0.80), 0.05),
    "ship": ("20261015_145358", None, (0.875, 0.075), 0.03),
    "wave": ("20261015_144741", None, (0.704, 0.51), 0.10),
    "corridor": ("9eddf1-also-somethng-like-these-5-frames", None, (0.459, 0.50), 0.38),
    "collage": ("9eddf1-also-somethng-like-these-5-frames-2", (0, 0, 1, 0.90), (0.435, 0.52), 0.62),
    "whalecity": ("20261015_150139", (0, 0, 1, 0.93), (0.832, 0.62), 0.17),
    "web": ("20261015_150128", (0.12, 0.09, 0.88, 0.88), (0.5, 0.5), 0.07),
    "heaven": ("20261015_145928", None, (0.52, 0.35), 0.04),
    "eye": ("20261015_145844", None, (0.5, 0.52), 0.10),
    "bed": ("20261015_144811", None, (0.52, 0.30), 0.25),
    "soulpull": ("20261015_165026", None, (0.64, 0.40), 0.5),
    "sleeper": ("20261015_144736", None, (0.5, 0.2), 0.3),
    "head": ("20261015_153816", None, (0.51, 0.53), 0.08),
    "rem": ("20261015_153813", None, (0.56, 0.60), 0.10),
    "ribbon": ("20261015_153807", None, (0.47, 0.43), 0.06),
    "morph": ("20261015_153805", None, (0.52, 0.58), 0.05),
    "lucid": ("20261015_153812", None, (0.55, 0.51), 0.40),
    "loopcard": ("20261015_153807_1", None, (0.50, 0.45), 0.03),
}
MASK = {"bedfall": (0, 0, 0.09, 0.07)}
s = ort.InferenceSession(model); mean = np.array([0.485, 0.456, 0.406]); std = np.array([0.229, 0.224, 0.225]); meta = json.load(open('assets/dreams/v3_meta.json')) if os.path.exists('assets/dreams/v3_meta.json') else {}
ONLY = os.environ.get('ONLY')
for k, (f, c, anc, fh) in K.items():
    if ONLY and k not in ONLY.split(','): continue
    fn = f if f.startswith("9eddf1") or f.startswith("da1484") else "image_" + f
    fn = fn if fn.startswith("image_") else "image_" + fn
    import os
    pth = f"{v2}/{fn}.jpg"; pth = pth if os.path.exists(pth) else f"{v3}/{fn}.jpg"
    im = Image.open(pth).convert("RGB")
    if c: w, h = im.size; im = im.crop((int(c[0] * w), int(c[1] * h), int(c[2] * w), int(c[3] * h)))
    a = np.asarray(im).astype(float); h, w, _ = a.shape
    if k in MASK: m = MASK[k]; a[int(m[1] * h):int(m[3] * h), int(m[0] * w):int(m[2] * w)] = 0
    im = Image.fromarray(a.astype(np.uint8))
    b = np.concatenate([a[:8].reshape(-1, 3), a[-8:].reshape(-1, 3), a[:, :8].reshape(-1, 3), a[:, -8:].reshape(-1, 3)]); bg = np.median(b, 0)
    o = Image.fromarray(np.clip((a - bg * 1.3 - 4) * 1.12, 0, 255).astype(np.uint8)); sc = 2400 / max(w, h)
    if sc < 1: o = o.resize((int(w * sc), int(h * sc)), Image.LANCZOS)
    o.save(f"assets/dreams/v3_{k}.jpg", quality=93)
    sc2 = 518 / min(w, h); nw, nh = max(14, int(w * sc2) // 14 * 14), max(14, int(h * sc2) // 14 * 14)
    x = (np.asarray(im.resize((nw, nh), Image.BICUBIC)).astype(np.float32) / 255 - mean) / std
    d = s.run(None, {"pixel_values": x.transpose(2, 0, 1)[None].astype(np.float32)})[0][0]
    lo, hi = np.percentile(d, 2), np.percentile(d, 98); d = np.clip((d - lo) / (hi - lo + 1e-6), 0, 1)
    dw = min(w, 1000); Image.fromarray((d * 255).astype(np.uint8)).resize((dw, int(dw * h / w)), Image.BICUBIC).filter(ImageFilter.GaussianBlur(1.5)).save(f"assets/dreams/v3_{k}_d.png")
    meta[k] = {"size": list(o.size), "anchor": list(anc), "figH": fh}; print(k, o.size)
json.dump(meta, open("assets/dreams/v3_meta.json", "w"))
