#!/usr/bin/env python3
"""Design sheet for the redesigned clay hero: 3 moods x 2 views. usage: sheet.py OUT.png"""
import sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, "/home/user/youtube-monetization/tools/cells-reel"); sys.path.insert(0, "/home/user/youtube-monetization/tools/hole-hill")
import figure as F
import render_v3 as V3
W, H = F.W, F.H
V3.gdata()
views = [("3/4 high (like the reference)", -0.62, 1000.0, 1100.0, 400.0), ("front", 0.0, 500.0, 1250.0, 470.0)]
moods = [("neutral", {}), ("determined", {}), ("triumph", {"a1": 2.55, "a2": 3.05})]
pw, ph = 360, 640
sheet = Image.new("RGB", (pw * 3, ph * 2 + 60), (14, 16, 22)); d = ImageDraw.Draw(sheet)
fnt = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-SemiBold.otf", 22)
for vi, (vn, th, Hc, D, ty) in enumerate(views):
    C = np.array([D * math.sin(th), Hc, D * math.cos(th)], np.float32); T = np.array([0, ty, 0], np.float32)
    r, u, f = F.lookat(C, T)
    bg = V3.ground_bg(C, r, u, f, 0.0)
    for mi, (mn, pose) in enumerate(moods):
        dcol, dmask = F.render_double(C, r, u, f, 0.0, pose=pose if mn != "triumph" else None, alpha=0.95) if vi == 0 and mn == "neutral" else (None, None)
        img = bg.copy()
        if dmask is not None: img = img * (1 - dmask[..., None]) + dcol * dmask[..., None]
        fig = F.render_figure(C, r, u, f, 0.0, pose=pose, mood=mn)
        img = F.composite_figure(img, fig)
        pil = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).resize((pw, ph), Image.LANCZOS)
        sheet.paste(pil, (mi * pw, 60 + vi * ph))
for mi, (mn, _) in enumerate(moods): d.text((mi * pw + 14, 18), mn.upper(), font=fnt, fill=(244, 236, 214))
sheet.save(sys.argv[1]); print("wrote", sys.argv[1])
