#!/usr/bin/env python3
"""Slow Light 'epic' grade: warm, rich golden-hour Mahabharata look (replaces the cold documentary grade).

Usage: grade_epic.py IN.png OUT.png
- keeps saffron / gold / crimson rich, pulls teal-cyan toward neutral (no 300-style teal)
- gentle S-curve for depth, warm highlights, slightly lifted warm shadows
"""
import sys
import numpy as np
from PIL import Image

im = np.asarray(Image.open(sys.argv[1]).convert("RGB")).astype(np.float32) / 255.0
r, g, b = im[..., 0], im[..., 1], im[..., 2]
mx, mn = im.max(-1), im.min(-1)
d = mx - mn
v = mx
s = np.where(mx > 0, d / np.maximum(mx, 1e-6), 0)
m = d > 1e-6
rc = np.where(m, (mx - r) / np.maximum(d, 1e-6), 0)
gc = np.where(m, (mx - g) / np.maximum(d, 1e-6), 0)
bc = np.where(m, (mx - b) / np.maximum(d, 1e-6), 0)
h = np.where(r == mx, bc - gc, np.where(g == mx, 2.0 + rc - bc, 4.0 + gc - rc))
h = (h / 6.0) % 1.0
hd = h * 360

k = np.full_like(s, 0.9)
k = np.where((hd >= 0) & (hd < 55), 1.08, k)            # reds, saffron, gold: rich
k = np.where(hd >= 340, 1.05, k)                         # crimson
k = np.where((hd > 150) & (hd < 212), 0.35, k)           # teal/cyan: neutralise
k = np.where((hd >= 212) & (hd <= 262), 1.0, k)          # indigo: keep
s2 = np.clip(s * k, 0, 1)

i = np.floor(h * 6).astype(int) % 6
f = h * 6 - np.floor(h * 6)
p, q, t = v * (1 - s2), v * (1 - f * s2), v * (1 - (1 - f) * s2)
out = np.select([i[..., None] == n for n in range(6)],
                [np.stack(c, -1) for c in [(v, t, p), (q, v, p), (p, v, t), (p, q, v), (t, p, v), (v, p, q)]])
out = out + 0.06 * (out - 0.5) * (1 - np.abs(out - 0.5) * 2)   # gentle S-curve
out[..., 0] = out[..., 0] * 1.04 + 0.01                         # warm
out[..., 1] = out[..., 1] * 1.01
out[..., 2] = out[..., 2] * 0.92
Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8)).save(sys.argv[2])
