"""Track the black hole (dark shadow) centre and radius in every frame of a clip.

usage: track.py small.rgb cx cy r0 out.json   (small.rgb = 270x480 rgb24 frames; cx, cy, r0 = rough start, in frame widths)
Iterates a dark-pixel centroid inside a window around the current estimate, then smooths over time.
"""
import json
import sys
import numpy as np

W, H = 270, 480
src, cx, cy, out = sys.argv[1], float(sys.argv[2]) * W, float(sys.argv[3]) * H, sys.argv[5]
fr = np.fromfile(src, np.uint8).reshape(-1, H, W, 3).astype(np.float32) / 255
lum = fr @ np.array([0.3, 0.59, 0.11], np.float32)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
res = []
r = float(sys.argv[4]) * W
for k in range(len(lum)):
    L = lum[k]
    for _ in range(6):
        win = (xx - cx) ** 2 + (yy - cy) ** 2 < (1.08 * r + 3) ** 2
        dark = win & (L < 0.10)
        n = dark.sum()
        if n < 20:
            break
        cx, cy = xx[dark].mean(), yy[dark].mean()
        r = max(r * 0.97, np.sqrt(n / np.pi) * 1.04)   # may grow, shrinks only slowly
    res.append((cx / W, cy / H, r / W))
a = np.array(res)
# temporal smoothing (centred moving average) so zooms do not jitter
k = 7
pad = np.pad(a, ((k, k), (0, 0)), mode="edge")
sm = np.stack([np.convolve(pad[:, i], np.ones(2 * k + 1) / (2 * k + 1), mode="valid") for i in range(3)], 1)
json.dump(sm.tolist(), open(out, "w"))
for i in range(0, len(sm), 24):
    print(i, np.round(sm[i], 3))
