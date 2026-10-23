"""Clean two-shot cut: slow zoom on shot A, a soft dissolve, slow zoom (with a slight roll) on shot B.

usage: clean.py CLIPDIR TRACKDIR KEY_A START_A KEY_B START_B | ffmpeg -f rawvideo -pix_fmt rgb24 -s 1080x1920 -r 24 -i - ...
No effects: only eased zooms toward each black hole and one crossfade.
"""
import json
import subprocess
import sys
import numpy as np
from PIL import Image

CLIPS, TRACK = sys.argv[1], sys.argv[2]
A, SA, B, SB = sys.argv[3], float(sys.argv[4]), sys.argv[5], float(sys.argv[6])
W, H, FPS = 1080, 1920, 24
DA, DB, X = 6.0, 6.0, 1.0           # shot lengths and dissolve (total 11 s)


def load(key, start, dur):
    path = subprocess.check_output(f"ls {CLIPS}/{key}*/*.mp4", shell=True, text=True).strip()
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", str(start), "-i", path, "-t", str(dur + 0.1),
                          "-vf", f"scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)


def ease(u):
    return u * u * (3 - 2 * u)


def view(frame, z, th, cx, cy):
    """Zoom z toward (cx, cy) with roll th, window kept inside the frame."""
    k = 1.0 / z
    ccx, ccy = cx + (W / 2 - cx) * k, cy + (H / 2 - cy) * k
    hw, hh = W / (2 * z), H / (2 * z)
    ex = abs(np.cos(th)) * hw + abs(np.sin(th)) * hh
    ey = abs(np.sin(th)) * hw + abs(np.cos(th)) * hh
    ccx, ccy = min(max(ccx, ex), W - ex), min(max(ccy, ey), H - ey)
    c, s = np.cos(th), np.sin(th)
    a, b, d, e = c / z, -s / z, s / z, c / z
    data = (a, b, ccx - a * W / 2 - b * H / 2, d, e, ccy - d * W / 2 - e * H / 2)
    return np.asarray(Image.fromarray(frame).transform((W, H), Image.AFFINE, data, Image.BICUBIC), np.float32)


def shot(key, start, dur, z1, roll):
    fr = load(key, start, dur)
    tr = json.load(open(f"{TRACK}/{key}.json"))
    # aim at the hole's average position over the shot, so the zoom target does not wander
    i0, i1 = int(start * FPS), min(int((start + dur) * FPS), len(tr) - 1)
    cx = np.mean([p[0] for p in tr[i0:i1]]) * W
    cy = np.mean([p[1] for p in tr[i0:i1]]) * H
    n = int(round(dur * FPS))
    out = []
    for j in range(n):
        u = ease(j / (n - 1)) * 0.85 + 0.15 * j / (n - 1)    # moving from frame 0, eases in and out
        th = np.radians(roll) * u
        z = float(np.exp(np.log(z1) * u))
        z = max(z, abs(np.cos(th)) + (H / W) * abs(np.sin(th)) + 0.005)
        out.append(view(fr[min(j, len(fr) - 1)], z, th, cx, cy))
    return out


sa = shot(A, SA, DA, 1.28, 0.0)
sb = shot(B, SB, DB, 1.35, 5.0)
nx = int(X * FPS)
seq = sa[:-nx]
for k in range(nx):
    w = ease((k + 1) / (nx + 1))
    seq.append(sa[len(sa) - nx + k] * (1 - w) + sb[k] * w)
seq += sb[nx:]
o = sys.stdout.buffer
for f in seq:
    o.write(np.clip(f + 0.5, 0, 255).astype(np.uint8).tobytes())
