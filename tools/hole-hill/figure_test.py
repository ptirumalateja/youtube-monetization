#!/usr/bin/env python3
"""Side-by-side: reference figure vs our redesigned clay figure on the hill scene. usage: figure_test.py OUT.png [mood] [theta] [hc]"""
import sys, math
import numpy as np
from PIL import Image
sys.path.insert(0, "/home/user/youtube-monetization/tools/cells-reel")
sys.path.insert(0, "/home/user/youtube-monetization/tools/hole-hill")
import figure as F
import render_v3 as V3
W, H = F.W, F.H
out = sys.argv[1]; mood = sys.argv[2] if len(sys.argv) > 2 else "neutral"
th = float(sys.argv[3]) if len(sys.argv) > 3 else -0.62
Hc = float(sys.argv[4]) if len(sys.argv) > 4 else 1000.0
D = 1100.0
C = np.array([D * math.sin(th), Hc, D * math.cos(th)], np.float32); T = np.array([0, 400, 0], np.float32)
r, u, f = F.lookat(C, T)
V3.gdata()
bg = V3.ground_bg(C, r, u, f, 0.0)
dcol, dmask = F.render_double(C, r, u, f, 0.0, alpha=0.95)
img = bg * (1 - dmask[..., None]) + dcol * dmask[..., None]
fig = F.render_figure(C, r, u, f, 0.0, mood=mood)
img = F.composite_figure(img, fig)
ys, xs = np.nonzero(fig["mask"])
x0, x1, y0, y1 = max(0, xs.min() - 140), min(W, xs.max() + 220), max(0, ys.min() - 100), min(H, ys.max() + 100)
ours = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).crop((x0, y0, x1, y1))
ref = Image.open("/tmp/claude-0/-home-user-youtube-monetization/a23e2797-2c3e-5eef-b6ce-d7544fada057/scratchpad/ref2/fig_crop_a.png")
hh = 1000
ref = ref.resize((int(ref.width * hh / ref.height), hh), Image.LANCZOS); ours = ours.resize((int(ours.width * hh / ours.height), hh), Image.LANCZOS)
sheet = Image.new("RGB", (ref.width + ours.width + 20, hh), (20, 20, 24)); sheet.paste(ref, (0, 0)); sheet.paste(ours, (ref.width + 20, 0)); sheet.save(out)
Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).save(out.replace(".png", "_full.png"))
print("wrote", out)
