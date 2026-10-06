#!/usr/bin/env python3
"""Slow Light still grade: faded documentary print, indigo kept as the one strong colour.

Usage: grade.py IN.png OUT.png
- desaturates everything, teal/cyan hardest (kills the AI teal-orange look)
- keeps deep blue/indigo (hue ~215-260 deg) closer to full saturation
- lifts blacks slightly, rolls off highlights, nudges the mid-tones warm-neutral
"""
import sys
import numpy as np
from PIL import Image

im = np.asarray(Image.open(sys.argv[1]).convert("RGB")).astype(np.float32) / 255.0
r, g, b = im[..., 0], im[..., 1], im[..., 2]
mx, mn = im.max(-1), im.min(-1)
v = mx
d = mx - mn
s = np.where(mx > 0, d / np.maximum(mx, 1e-6), 0)
h = np.zeros_like(mx)
m = d > 1e-6
rc = np.where(m, (mx - r) / np.maximum(d, 1e-6), 0)
gc = np.where(m, (mx - g) / np.maximum(d, 1e-6), 0)
bc = np.where(m, (mx - b) / np.maximum(d, 1e-6), 0)
h = np.where(r == mx, bc - gc, np.where(g == mx, 2.0 + rc - bc, 4.0 + gc - rc))
h = (h / 6.0) % 1.0
hd = h * 360

sat_k = np.full_like(s, 0.55)                                   # global
sat_k = np.where((hd > 160) & (hd < 212), 0.22, sat_k)          # teal/cyan: crush
sat_k = np.where((hd >= 212) & (hd <= 262), 0.95, sat_k)        # indigo/deep blue: keep
sat_k = np.where((hd > 15) & (hd < 50), 0.6, sat_k)             # orange: restrain
s2 = s * sat_k

# HSV -> RGB
i = np.floor(h * 6).astype(int) % 6
f = h * 6 - np.floor(h * 6)
p, q, t = v * (1 - s2), v * (1 - f * s2), v * (1 - (1 - f) * s2)
out = np.select([i[..., None] == k for k in range(6)],
                [np.stack(c, -1) for c in [(v, t, p), (q, v, p), (p, v, t), (p, q, v), (t, p, v), (v, p, q)]])
# tone: lift blacks, soft highlight roll-off, slight warm-neutral midtones
out = 0.035 + out * 0.94
out = out - 0.08 * np.clip(out - 0.75, 0, None) ** 1.5
out[..., 0] *= 1.02
out[..., 2] *= 0.97
Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8)).save(sys.argv[2])
