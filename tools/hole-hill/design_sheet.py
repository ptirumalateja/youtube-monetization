#!/usr/bin/env python3
"""Hole-becomes-hill: hero design sheet. Three style directions x three moments (neutral, determined, triumph).
A = ink stickman (thick brush line, expressive face)   B = neon line on black   C = clay mannequin with ink hatching (like the reference)
usage: design_sheet.py OUT.png
"""
import math, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
sys.path.insert(0, "/home/user/youtube-monetization/tools/cells-reel")
sys.path.insert(0, "/home/user/youtube-monetization/tools/dont-tell-dreams")   # first, so "render" is the stickman renderer
import render as R
import render_v2 as R2

W, H = R.W, R.H
FACES = {
    "neutral": dict(eyes="ball", ew=1.0, lid=0.0, pr=0.6, look=0.0, mt="smile", ma=0.7, bl=(2, 0.15), brr=(2, 0.15)),
    "determined": dict(eyes="ball", ew=1.0, lid=0.42, pr=0.85, look=0.0, mt="gritted", ma=1.0, bl=(-2, -0.95), brr=(-2, -0.95)),
    "triumph": dict(eyes="happy", mt="grin", ma=1.15, bl=(12, 0.4), brr=(12, 0.4)),
}
POSES = {
    "neutral": [(-48, 178), (48, 178)],
    "determined": [(-42, 168), (42, 168)],
    "triumph": [(-150, -175), (150, -175)],
}
FIST = {"neutral": False, "determined": True, "triumph": True}

def stick_panel(kind, mood):
    cam = R.Cam(540, 960, 1.0)
    L = R2.Layer2(cam, 3)
    s = 1.7; yg = 1560
    hands = POSES[mood]
    face = dict(FACES[mood])
    bend = ("out", "out")
    R2.draw_char(L, 540, yg, s, hands, face, 7, bend=bend, lean=(-5 if mood == "determined" else 0), fist=FIST[mood], hstyle=0)
    ink = np.asarray(L.img.resize((W, H), Image.BOX), np.float32)[..., None] / 255
    if kind == "A":
        base, vig, grain = R.build_bg()
        img = base * (1 - 0.35 * vig[..., None]); img = img * (1 - ink) + R.INK * ink
        return img
    # B: neon line on black
    bg = np.zeros((H, W, 3), np.float32); bg[:] = np.array([6, 9, 20], np.float32) / 255
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / (W * 0.7)) ** 2 + ((yy - H * 0.55) / (H * 0.6)) ** 2)
    bg = bg + np.clip(1 - r, 0, 1)[..., None] ** 2.2 * np.array([0.02, 0.10, 0.16], np.float32)
    col = np.array([0.35, 0.95, 1.0], np.float32) if mood != "triumph" else np.array([1.0, 0.82, 0.35], np.float32)
    sm_ = Image.fromarray((ink[..., 0] * 255).astype(np.uint8)).resize((W // 4, H // 4), Image.BILINEAR)
    glow = np.asarray(sm_.filter(ImageFilter.GaussianBlur(5)).resize((W, H), Image.BILINEAR), np.float32)[..., None] / 255
    glow2 = np.asarray(sm_.filter(ImageFilter.GaussianBlur(14)).resize((W, H), Image.BILINEAR), np.float32)[..., None] / 255
    return np.clip(bg + col * (ink * 1.0 + glow * 0.9 + glow2 * 0.7), 0, 1)

# ---- clay mannequin (SDF, posed arms)
import render_v4 as V4
import render_v3 as V3
POSE = {"a1": 0.12, "a2": 0.02}
def sdf_posed(x, y, z):
    ax = np.abs(x); K = V4.K_SM
    d = V4.sd_ell(x, y, z, 2, 786, 18, 64, 80, 68)
    d = V4.smin(d, V4.sd_cap(x, y, z, (0, 735, 6), (0, 700, 0), 30, 32), K)
    d = V4.smin(d, V4.sd_ell(x, y, z, 0, 628, 0, 92, 100, 60), K)
    d = V4.smin(d, V4.sd_ell(x, y, z, 0, 516, 10, 84, 110, 58), K)
    d = V4.smin(d, V4.sd_ell(x, y, z, 0, 428, 0, 84, 64, 56), K)
    d = V4.smin(d, V4.sd_ell(ax, y, z, 90, 676, 0, 42, 38, 40), K)
    S = (90.0, 676.0, 0.0); a1, a2 = POSE["a1"], POSE["a2"]
    E = (S[0] + 120 * math.sin(a1), S[1] - 120 * math.cos(a1), 14.0)
    Wr = (E[0] + 110 * math.sin(a2), E[1] - 110 * math.cos(a2), 40.0)
    d = V4.smin(d, V4.sd_cap(ax, y, z, S, E, 33, 28), K)
    d = V4.smin(d, V4.sd_cap(ax, y, z, E, Wr, 28, 24), K)
    d = V4.smin(d, V4.sd_ell(ax, y, z, Wr[0], Wr[1] - 30 * math.cos(a2), Wr[2] + 6, 27, 40, 23), K)
    d = V4.smin(d, V4.sd_cap(ax, y, z, (40, 420, 0), (46, 232, 8), 46, 36), K)
    d = V4.smin(d, V4.sd_cap(ax, y, z, (46, 232, 8), (48, 54, 0), 35, 26), K)
    d = V4.smin(d, V4.sd_ell(ax, y, z, 50, 24, 40, 30, 24, 64), K)
    return d

def clay_panel(mood):
    V3.gdata()
    POSE["a1"], POSE["a2"] = ((2.5, 3.0) if mood == "triumph" else (0.12, 0.02))
    V4.sdf = sdf_posed
    C = np.array([0, 520, 1180], np.float32); T = np.array([0, 520, 0], np.float32)
    r, u, f = V3.lookat(C, T)
    fig, fm = V4.render_solid4(0.0, C, r, u, f, 0.0)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    g = np.clip(yy / H, 0, 1)[..., None]
    bg = np.array([0.62, 0.86, 0.74], np.float32) * (1 - g) + np.array([0.18, 0.34, 0.14], np.float32) * g
    img = bg * (1 - fm[..., None]) + fig * fm[..., None]
    pi = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)); d = ImageDraw.Draw(pi)
    # face marks (the reference figure is almost faceless: tiny eyes, small brow ticks)
    e = np.array([[-26, 798, 82], [26, 798, 82]], np.float32)
    ex, ey, _ = V3.project(e, C, r, u, f)
    ink = (40, 28, 54); pink = (214, 44, 130)
    if mood == "neutral":
        for a, b in zip(ex, ey): d.ellipse([a - 6, b - 6, a + 6, b + 6], fill=pink)
        d.line([(ex[0] + 18, ey[0] + 46), (ex[1] - 18, ey[1] + 46)], fill=ink, width=4)
    elif mood == "determined":
        for a, b in zip(ex, ey): d.ellipse([a - 7, b - 4, a + 7, b + 4], fill=pink)
        d.line([(ex[0] - 20, ey[0] - 22), (ex[0] + 16, ey[0] - 10)], fill=ink, width=6); d.line([(ex[1] + 20, ey[1] - 22), (ex[1] - 16, ey[1] - 10)], fill=ink, width=6)
        d.line([(ex[0] + 14, ey[0] + 44), (ex[1] - 14, ey[1] + 44)], fill=ink, width=6)
    else:
        for a, b in zip(ex, ey): d.arc([a - 12, b - 12, a + 12, b + 8], 200, 340, fill=ink, width=6)
        d.arc([ex[0] + 8, ey[0] + 20, ex[1] - 8, ey[1] + 62], 15, 165, fill=ink, width=6)
    return np.asarray(pi, np.float32) / 255

def main():
    out = sys.argv[1]
    cols = []
    moods = ["neutral", "determined", "triumph"]
    pw, ph = 360, 640
    sheet = Image.new("RGB", (pw * 3, ph * 3 + 70), (14, 16, 22)); dd = ImageDraw.Draw(sheet)
    f = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf", 24)
    labels = ["A  INK STICKMAN", "B  NEON LINE", "C  CLAY + HATCH"]
    for ci in range(3):
        for ri, mood in enumerate(moods):
            if ci == 0: img = stick_panel("A", mood)
            elif ci == 1: img = stick_panel("B", mood)
            else: img = clay_panel(mood)
            pil = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).resize((pw, ph), Image.LANCZOS)
            sheet.paste(pil, (ci * pw, 70 + ri * ph))
        dd.text((ci * pw + 14, 20), labels[ci], font=f, fill=(244, 236, 214))
    sheet.save(out)
    print("wrote", out)

if __name__ == "__main__":
    main()
