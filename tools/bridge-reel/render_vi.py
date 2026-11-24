#!/usr/bin/env python3
"""'Waiting for the one game' timeline (21 s, 1080x1920): the same gamer on the couch in 2004 (cheat sheet, CRT), 2013 (flat TV, driving), 2026 (the new sequel reveal, laughing + crying).
Own cartoon drawing; the game on the TVs is a FICTIONAL title ("NEON CITY VI"), no third-party footage, logos or names.
usage: render_vi.py sheet OUT.png t... | frames OUTDIR | video OUT.mp4 AUDIO.wav FRAMESDIR"""
import sys, os, math, random, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_mom import Pen, Cam
from render_bridge3 import sm, lerp, font, MONO

W, H = 1080, 1920; FPS = 30; DUR = 21.0; SS = 2
FD = os.path.dirname(os.path.abspath(__file__)) + "/fonts/"
BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
OUT = (46, 36, 30, 255); WHITE = (252, 250, 246, 255)
SKIN = (255, 255, 255, 255); HAIR = (92, 58, 36, 255); HAIR_D = (60, 38, 24, 255)
CUTS = [1.6, 3.4, 6.2, 8.0, 11.5, 13.2, 16.5]
YEARS = [(0.0, "2004:"), (6.2, "2013:"), (11.5, "2026:")]

# ------------------------------------------------------------------ rooms
def wall(pn, era, floor_y):
    base = {2004: (246, 238, 220), 2013: (240, 240, 238), 2026: (238, 240, 236)}[era]
    pn.poly([(0, 0), (1080, 0), (1080, floor_y), (0, floor_y)], base + (255,))
    for x in range(30, 1080, 110): pn.line([(x, 60), (x, floor_y)], 2, (214, 204, 180, 140) if era == 2004 else (210, 210, 206, 150))
    pn.poly([(0, floor_y), (1080, floor_y), (1080, 1920), (0, 1920)], ((226, 190, 140) if era == 2004 else (206, 168, 122)) + (255,))
def window(pn, x, y, w, h):
    pn.rrect(x, y, x + w, y + h, 6, (178, 214, 238, 255), OUT, 5); pn.line([(x + w / 2, y), (x + w / 2, y + h)], 5, OUT); pn.line([(x, y + h / 2), (x + w, y + h / 2)], 5, OUT)
    pn.circ(x + w * 0.3, y + h * 0.35, 18, (255, 244, 200, 255)); pn.poly([(x, y + h), (x + w * 0.45, y + h * 0.55), (x + w, y + h)], (140, 188, 130, 255))
def picture(pn, x, y, w, h, era):
    pn.rrect(x, y, x + w, y + h, 4, (212, 170, 120, 255) if era == 2004 else (224, 224, 220, 255), OUT, 5)
    pn.poly([(x + 10, y + h - 10), (x + w * 0.4, y + h * 0.4), (x + w - 10, y + h - 10)], (120, 168, 190, 255)); pn.circ(x + w * 0.7, y + h * 0.3, 14, (255, 236, 190, 255))
def lamp(pn, x, y, s=1.0):
    pn.poly([(x - 55 * s, y), (x + 55 * s, y), (x + 38 * s, y - 62 * s), (x - 38 * s, y - 62 * s)], (250, 232, 190, 255), OUT, 4)
    pn.line([(x, y), (x, y + 80 * s)], 8 * s, OUT); pn.rrect(x - 40 * s, y + 78 * s, x + 40 * s, y + 98 * s, 6, (150, 100, 64, 255), OUT, 4)
def plant(pn, x, y, s=1.0):
    pn.rrect(x - 34 * s, y, x + 34 * s, y + 56 * s, 6, (208, 120, 88, 255), OUT, 4)
    for a in (-1.0, -0.4, 0.2, 0.8, 1.3): pn.poly([(x, y), (x + 70 * s * math.sin(a), y - 90 * s * math.cos(a) - 18 * s), (x + 20 * s * math.cos(a), y - 30 * s)], (92, 150, 84, 255), OUT, 3)
def couch(pn, cx, y, w, h, col, pillows=()):
    pn.rrect(cx - w / 2, y - h, cx + w / 2, y + 40, 40, col, OUT, 5)
    pn.rrect(cx - w / 2 - 40, y - h * 0.35, cx - w / 2 + 70, y + 60, 30, col, OUT, 5); pn.rrect(cx + w / 2 - 70, y - h * 0.35, cx + w / 2 + 40, y + 60, 30, col, OUT, 5)
    for k in range(1, 3): pn.line([(cx - w / 2 + k * w / 3, y - h + 50), (cx - w / 2 + k * w / 3, y - 10)], 3, OUT)
    for (px, py, c) in pillows: pn.rrect(px - 58, py - 70, px + 58, py + 70, 22, c, OUT, 4)
def shelf(pn, x, y):
    pn.rrect(x, y, x + 190, y + 420, 4, (150, 98, 58, 255), OUT, 5)
    for k in range(3): pn.line([(x, y + 140 * (k + 1)), (x + 190, y + 140 * (k + 1))], 5, OUT)
    rr = random.Random(2)
    for k in range(3):
        xx = x + 10
        while xx < x + 170:
            ww = rr.randint(14, 24); pn.rrect(xx, y + 140 * k + 40, xx + ww, y + 140 * (k + 1) - 6, 2, rr.choice([(196, 90, 70, 255), (70, 110, 150, 255), (214, 176, 80, 255), (90, 140, 100, 255)]), OUT, 2); xx += ww + 2

# ------------------------------------------------------------------ characters
def hair_poly(pn, cx, cy, r, seed, spikes=14, rad=1.25, col=HAIR, front=True):
    rr = random.Random(seed); pts = []
    for i in range(spikes + 1):
        a = math.pi * (1.05 + 0.9 * i / spikes); R = r * (rad if i % 2 else rad - 0.18) * rr.uniform(0.94, 1.08)
        pts.append((cx + R * math.cos(a), cy + R * math.sin(a) * 0.95))
    pts += [(cx + r * 0.95, cy - r * 0.18), (cx + r * 0.55, cy - r * 0.55), (cx - r * 0.5, cy - r * 0.62), (cx - r * 0.95, cy - r * 0.18)]
    pn.poly(pts, col, OUT, 5)
def face(pn, cx, cy, r, mood, look=(0, 0), beard=False, tear=0.0, blink=0.0):
    pn.circ(cx, cy, r, SKIN, OUT, 7)
    if beard:
        pn.poly([(cx - r * 0.98, cy - r * 0.05), (cx - r * 0.9, cy + r * 0.5), (cx - r * 0.45, cy + r * 1.0), (cx + r * 0.45, cy + r * 1.0), (cx + r * 0.9, cy + r * 0.5), (cx + r * 0.98, cy - r * 0.05), (cx + r * 0.6, cy + r * 0.28), (cx - r * 0.6, cy + r * 0.28)], HAIR_D, OUT, 4)
    for sd in (-1, 1):
        ex, ey = cx + sd * r * 0.38, cy - r * 0.12
        if mood in ("laugh", "cry"):
            pn.line([(ex - r * 0.2, ey + r * 0.04), (ex, ey - r * 0.12), (ex + r * 0.2, ey + r * 0.04)], r * 0.07, OUT)
        elif blink > 0.5: pn.line([(ex - r * 0.2, ey), (ex + r * 0.2, ey)], r * 0.07, OUT)
        else:
            pn.circ(ex, ey, r * (0.26 if mood == "shock" else 0.21), WHITE, OUT, 5); pn.circ(ex + look[0] * r * 0.06, ey + look[1] * r * 0.06, r * (0.07 if mood == "shock" else 0.085), OUT)
    my = cy + r * 0.52
    if mood == "o": pn.circ(cx, my, r * 0.09, (80, 40, 40, 255), OUT, 4)
    elif mood == "shock": pn.rrect(cx - r * 0.13, my - r * 0.1, cx + r * 0.13, my + r * 0.16, r * 0.1, (80, 40, 40, 255), OUT, 4)
    elif mood == "tongue": pn.line([(cx - r * 0.2, my), (cx + r * 0.2, my)], r * 0.06, OUT); pn.circ(cx + r * 0.1, my + r * 0.14, r * 0.1, (240, 130, 130, 255), OUT, 4)
    elif mood == "flat": pn.line([(cx - r * 0.16, my), (cx + r * 0.16, my)], r * 0.06, OUT)
    elif mood in ("laugh", "cry"):
        pn.poly([(cx - r * 0.5, my - r * 0.08), (cx + r * 0.5, my - r * 0.08), (cx + r * 0.42, my + r * 0.3), (cx, my + r * 0.46), (cx - r * 0.42, my + r * 0.3)], (110, 40, 44, 255), OUT, 5)
        pn.rrect(cx - r * 0.44, my - r * 0.06, cx + r * 0.44, my + r * 0.1, 3, WHITE, None); pn.circ(cx, my + r * 0.3, r * 0.17, (236, 120, 120, 255))
    if tear > 0:
        for sd in (-1, 1):
            tx = cx + sd * r * 0.5
            L = r * 0.8 * tear; pn.poly([(tx - r * 0.06, cy + r * 0.05), (tx + r * 0.06, cy + r * 0.05), (tx + r * 0.1, cy + r * 0.05 + L), (tx - r * 0.1, cy + r * 0.05 + L)], (150, 206, 244, 255), (60, 120, 180, 255), 3)
def back_head(pn, cx, cy, r, seed, shirt=(120, 120, 120, 255), stripes=False, tank=False):
    pn.circ(cx, cy, r, SKIN, OUT, 7); hair_poly(pn, cx, cy + r * 0.16, r * 0.98, seed, 16, 1.12, HAIR, True)
    pn.circ(cx, cy + r * 0.12, r * 0.94, HAIR, OUT, 6)
    for k in range(7): a = random.Random(seed + k).uniform(0, 6.28); pn.line([(cx + r * 0.5 * math.cos(a), cy + r * 0.3 + r * 0.5 * math.sin(a)), (cx + r * 0.7 * math.cos(a + 0.2), cy + r * 0.3 + r * 0.7 * math.sin(a + 0.2))], 4, HAIR_D)
    pn.poly([(cx - r * 1.7, cy + r * 2.6), (cx - r * 1.1, cy + r * 1.15), (cx + r * 1.1, cy + r * 1.15), (cx + r * 1.7, cy + r * 2.6)], shirt, OUT, 6)
    if stripes:
        for sd in (-1, 1): pn.poly([(cx + sd * r * 0.7, cy + r * 1.3), (cx + sd * r * 0.98, cy + r * 1.7), (cx + sd * r * 0.72, cy + r * 1.74), (cx + sd * r * 0.48, cy + r * 1.36)], (214, 56, 60, 255), OUT, 3)
    if tank: pn.poly([(cx - r * 0.7, cy + r * 1.2), (cx + r * 0.7, cy + r * 1.2), (cx + r * 0.55, cy + r * 2.4), (cx - r * 0.55, cy + r * 2.4)], (252, 252, 252, 255), OUT, 4)
def controller(pn, cx, cy, s, col=(40, 40, 52, 255)):
    pn.rrect(cx - 60 * s, cy - 24 * s, cx + 60 * s, cy + 24 * s, 18 * s, col, OUT, 4)
    for sd in (-1, 1): pn.circ(cx + sd * 26 * s, cy + 2 * s, 11 * s, (90, 90, 108, 255))
def leg(pn, hip, knee, foot, w=14):
    pn.line([hip, knee, foot], w, OUT); fx, fy = foot; pn.poly([(fx - 28, fy - 6), (fx + 36, fy - 6), (fx + 42, fy + 18), (fx - 30, fy + 18)], WHITE, OUT, 4)
def person_front(pn, cx, hy, s, kind, t, mood, ctrl_swing=0.0, tear=0.0, wipe=0.0, look=(0, 0)):
    r = 92 * s; sh_y = hy + r + 18 * s
    if kind == "kid": shirt, shorts = (140, 142, 148, 255), (46, 76, 140, 255)
    elif kind == "teen": shirt, shorts = (36, 36, 44, 255), (30, 30, 36, 255)
    else: shirt, shorts = (252, 252, 252, 255), (170, 170, 176, 255)
    hip_y = sh_y + 150 * s
    if kind == "kid":
        sw = math.sin(t * 5) * 20 * s
        leg(pn, (cx - 30 * s, hip_y), (cx - 40 * s, hip_y + 90 * s), (cx - 52 * s + sw, hip_y + 190 * s)); leg(pn, (cx + 30 * s, hip_y), (cx + 40 * s, hip_y + 90 * s), (cx + 52 * s - sw, hip_y + 190 * s))
    else:
        leg(pn, (cx - 30 * s, hip_y), (cx - 150 * s, hip_y + 24 * s), (cx - 165 * s, hip_y + 190 * s)); leg(pn, (cx + 30 * s, hip_y), (cx + 150 * s, hip_y + 24 * s), (cx + 165 * s, hip_y + 190 * s))
    pn.poly([(cx - 62 * s, sh_y), (cx + 62 * s, sh_y), (cx + 70 * s, hip_y), (cx - 70 * s, hip_y)], shirt, OUT, 5)
    if kind == "kid": pn.circ(cx, sh_y + 60 * s, 24 * s, (252, 214, 60, 255), OUT, 4)
    if kind == "teen":
        for sd in (-1, 1): pn.poly([(cx + sd * 40 * s, sh_y), (cx + sd * 62 * s, sh_y), (cx + sd * 64 * s, sh_y + 50 * s), (cx + sd * 42 * s, sh_y + 50 * s)], (214, 56, 60, 255), None)
    pn.poly([(cx - 74 * s, hip_y - 14 * s), (cx + 74 * s, hip_y - 14 * s), (cx + 82 * s, hip_y + 44 * s), (cx - 82 * s, hip_y + 44 * s)], shorts, OUT, 5)
    hand = (cx, hip_y - 20 * s)
    for sd in (-1, 1): pn.line([(cx + sd * 56 * s, sh_y + 14 * s), (cx + sd * 78 * s, sh_y + 90 * s), (hand[0] + sd * 30 * s, hand[1])], 13 * s, OUT)
    controller(pn, hand[0], hand[1], 1.0 * s)
    if wipe > 0:
        hx, hy2 = lerp(cx + 78 * s, cx + 62 * s, wipe), lerp(sh_y + 90 * s, hy + r * 0.2, wipe); pn.line([(cx + 56 * s, sh_y + 14 * s), (cx + 150 * s, sh_y + 60 * s), (hx, hy2)], 13 * s, OUT); pn.circ(hx, hy2, 20 * s, WHITE, OUT, 4)
    face_sc = 1.0
    pn.line([(cx, hy + r - 4), (cx, sh_y + 8)], 16 * s, OUT)
    face(pn, cx, hy, r, mood, look, beard=(kind == "man"), tear=tear)
    if kind == "kid": hair_poly(pn, cx, hy - r * 0.05, r, 3, 14, 1.3)
    elif kind == "teen": hair_poly(pn, cx, hy - r * 0.05, r, 5, 12, 1.22)
    else: hair_poly(pn, cx, hy - r * 0.05, r, 7, 12, 1.14, HAIR_D)
    return hand

# ------------------------------------------------------------------ TV screens (our own fictional game)
def game_surface(w, h, kind, t):
    im = Image.new("RGB", (w, h), (0, 0, 0)); d = ImageDraw.Draw(im)
    if kind == "retro":
        for y in range(h // 2): c = int(y / (h / 2) * 60); d.line([(0, y), (w, y)], fill=(238 - c, 146 - c, 96 - c // 2))
        d.rectangle([0, h // 2, w, h], fill=(110, 100, 96))
        off = (t * 120) % 140
        for i in range(-1, 8):
            x = i * 140 - off; hh = 70 + (i * 37) % 80; d.rectangle([x, h // 2 - hh, x + 100, h // 2], fill=(150, 78, 66)); d.rectangle([x + 12, h // 2 - hh + 12, x + 30, h // 2 - hh + 34], fill=(240, 210, 120))
        d.rectangle([0, h * 0.78, w, h * 0.8], fill=(214, 208, 196))
        bx = w * 0.45 + math.sin(t * 2) * 12; by = h * 0.66
        for wx in (bx - 38, bx + 38): d.ellipse([wx - 26, by + 6, wx + 26, by + 58], outline=(20, 20, 20), width=5)
        d.line([(bx - 38, by + 32), (bx, by + 8), (bx + 38, by + 32)], fill=(30, 30, 30), width=5); d.ellipse([bx - 10, by - 36, bx + 10, by - 16], fill=(60, 40, 30)); d.line([(bx, by - 16), (bx, by + 8)], fill=(60, 40, 30), width=8)
        d.ellipse([w * 0.05, h * 0.68, w * 0.05 + 70, h * 0.68 + 70], fill=(60, 66, 60), outline=(220, 220, 220), width=4)
    elif kind == "hd":
        for y in range(h // 2): d.line([(0, y), (w, y)], fill=(int(120 + y / (h / 2) * 70), int(190 + y / (h / 2) * 40), 240))
        d.polygon([(0, h // 2), (w * 0.3, h * 0.28), (w * 0.62, h // 2)], fill=(122, 170, 110)); d.polygon([(w * 0.4, h // 2), (w * 0.78, h * 0.3), (w, h // 2)], fill=(104, 154, 98))
        d.rectangle([0, h // 2, w, h], fill=(96, 98, 104))
        off = (t * 4.2) % 1.0
        for k in range(10):
            z = ((k / 10.0 + off) % 1.0) ** 2; y = h // 2 + z * (h / 2); wdt = 8 + z * 20; d.rectangle([w / 2 - wdt / 2, y, w / 2 + wdt / 2, y + 4 + z * 14], fill=(236, 236, 230))
        for sd in (-1, 1):
            for k in range(6): xx = w / 2 + sd * (w * 0.25 + k * w * 0.1 + ((t * 300) % 140)); d.line([(xx, h * 0.55), (xx + sd * 120, h * 0.55 + 4)], fill=(210, 220, 230), width=3)
        cy = h * 0.72 + math.sin(t * 9) * 4; d.rounded_rectangle([w / 2 - 110, cy - 46, w / 2 + 110, cy + 48], 18, fill=(246, 246, 248), outline=(120, 120, 130), width=3)
        d.rectangle([w / 2 - 84, cy - 30, w / 2 + 84, cy - 6], fill=(60, 70, 90)); d.rectangle([w / 2 - 100, cy + 24, w / 2 - 70, cy + 40], fill=(210, 40, 40)); d.rectangle([w / 2 + 70, cy + 24, w / 2 + 100, cy + 40], fill=(210, 40, 40))
        d.rounded_rectangle([w * 0.04, h * 0.7, w * 0.04 + 80, h * 0.7 + 54], 6, fill=(40, 70, 130), outline=(240, 240, 240), width=2)
        im = im.filter(ImageFilter.GaussianBlur(1.6))
    return im
def paste_tv(pn, im, x0, y0, x1, y1):
    X0, Y0 = pn.p(x0, y0); X1, Y1 = pn.p(x1, y1); sc = im.resize((max(1, int(X1 - X0)), max(1, int(Y1 - Y0))), Image.LANCZOS)
    pn.d._image.paste(sc.convert("RGBA"), (int(X0), int(Y0)))

def logo(pn, cx, cy, s, reveal, glow):
    """fictional 'NEON CITY VI' reveal"""
    lay = Image.new("RGBA", (int(900 * SS), int(520 * SS)), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); f = ImageFont.truetype(BOLD, int(330 * SS))
    mask = Image.new("L", lay.size, 0); ImageDraw.Draw(mask).text((lay.size[0] / 2, lay.size[1] * 0.45), "VI", font=f, fill=255, anchor="mm")
    g = np.zeros((lay.size[1], lay.size[0], 3), np.float32); yy = np.linspace(0, 1, lay.size[1], dtype=np.float32)[:, None, None]
    g[:] = np.array([255, 160, 70], np.float32) * (1 - yy) + np.array([196, 56, 170], np.float32) * yy
    gi = Image.fromarray(g.astype(np.uint8), "RGB").convert("RGBA"); gi.putalpha(mask.point(lambda v: int(v * reveal))); lay.alpha_composite(gi)
    gl = Image.new("RGBA", lay.size, (255, 120, 190, 0)); gl.putalpha(mask.filter(ImageFilter.GaussianBlur(26 * SS)).point(lambda v: int(v * 0.8 * glow * reveal))); lay2 = Image.new("RGBA", lay.size, (0, 0, 0, 0)); lay2.alpha_composite(gl); lay2.alpha_composite(lay)
    w2, h2 = int(lay.size[0] * s * pn.c.z), int(lay.size[1] * s * pn.c.z); X, Y = pn.p(cx, cy)
    pn.d._image.alpha_composite(lay2.resize((w2, h2), Image.LANCZOS), (int(X - w2 / 2), int(Y - h2 / 2)))

# ------------------------------------------------------------------ scenes
def s1(pn, t):   # 2004 wide: kid on couch, cable to the TV
    wall(pn, 2004, 1180); window(pn, 80, 420, 180, 280); picture(pn, 440, 380, 200, 130, 2004); lamp(pn, 130, 840); plant(pn, 100, 900); shelf(pn, 850, 360)
    couch(pn, 540, 1180, 980, 480, (240, 228, 200, 255), pillows=((130, 1010, (60, 88, 150, 255)), (940, 1020, (244, 214, 160, 255))))
    hd = person_front(pn, 540, 800, 1.0, "kid", t, "o")
    pn.line([(540, 1020), (560, 1260), (520, 1500), (540, 1700)], 6, OUT)
    pn.poly([(0, 1560), (1080, 1560), (1080, 1920), (0, 1920)], (36, 36, 44, 255), OUT, 5)
def s2(pn, t):   # close-up: cheat sheet, tongue out
    pn.poly([(0, 0), (1080, 0), (1080, 1920), (0, 1920)], (244, 232, 206, 255)); window(pn, 60, 330, 190, 300); picture(pn, 400, 340, 210, 140, 2004); shelf(pn, 840, 300)
    couch(pn, 760, 1500, 1100, 700, (240, 228, 200, 255), pillows=((100, 1100, (60, 88, 150, 255)),))
    cx, cy, r = 640, 900, 215
    pn.poly([(cx - 190, cy + r + 20), (cx + 190, cy + r + 20), (cx + 220, 1480), (cx - 220, 1480)], (140, 142, 148, 255), OUT, 7); pn.circ(cx + 40, 1340, 70, (252, 214, 60, 255), OUT, 6)
    pn.poly([(cx - 260, 1500), (cx + 260, 1500), (cx + 330, 1700), (cx - 330, 1700)], (46, 76, 140, 255), OUT, 7)
    hand = (cx + 70, 1480); controller(pn, hand[0], hand[1], 2.2)
    pn.line([(cx + 170, cy + r + 90), (cx + 260, 1380), (hand[0] + 70, hand[1])], 26, OUT)
    face(pn, cx, cy, r, "tongue", look=(-1, 1)); hair_poly(pn, cx, cy - r * 0.05, r, 3, 18, 1.32)
    # the cheat sheet
    sw = math.sin(t * 2) * 1.5; ang = math.radians(-8 + sw)
    def R(x, y): return (270 + x * math.cos(ang) - y * math.sin(ang), 1050 + x * math.sin(ang) + y * math.cos(ang))
    pn.poly([R(-170, -300), R(170, -300), R(170, 320), R(-170, 320)], (252, 252, 250, 255), OUT, 6)
    syms = "△→→↓R1|○←↓←L1|□↑↑→R2|△↓←←L1|○→→△R1|□○△↑L2"
    for i in range(10):
        pn.line([R(-130, -250 + i * 56), R(130, -250 + i * 56)], 4, (70, 70, 80, 200))
    pn.circ(R(-150, 290)[0], R(-150, 290)[1], 36, WHITE, OUT, 5)
def tv_stand(pn, era, cx, y):
    if era == 2004:
        pn.rrect(cx - 440, y, cx + 440, y + 40, 4, (150, 98, 58, 255), OUT, 6); pn.rrect(cx - 440, y + 40, cx - 410, y + 330, 3, (150, 98, 58, 255), OUT, 5); pn.rrect(cx + 410, y + 40, cx + 440, y + 330, 3, (150, 98, 58, 255), OUT, 5)
        pn.rrect(cx - 440, y + 190, cx + 440, y + 214, 3, (150, 98, 58, 255), OUT, 5)
        pn.rrect(cx - 200, y + 100, cx + 40, y + 190, 8, (46, 46, 56, 255), OUT, 5)
        for k in range(4): pn.circ(cx - 160 + k * 36, y + 150, 7, (120, 120, 140, 255))
        for k in range(3): pn.rrect(cx + 120, y + 128 + k * 18, cx + 380, y + 146 + k * 18, 3, [(70, 110, 150, 255), (210, 90, 70, 255), (90, 140, 100, 255)][k], OUT, 3)
    else:
        pn.rrect(cx - 520, y, cx + 520, y + 330, 8, (250, 250, 248, 255), OUT, 6)
        for sd in (-1, 1): pn.rrect(cx + sd * 260 - 150, y + 80, cx + sd * 260 + 150, y + 300, 6, (244, 244, 242, 255), OUT, 4)
        pn.rrect(cx - 90, y - 26, cx + 90, y + 4, 4, (36, 36, 44, 255), OUT, 4)
def s3(pn, t):   # 2004 back shot: CRT game
    wall(pn, 2004, 1040); window(pn, 70, 220, 170, 260); plant(pn, 950, 960, 1.2); shelf(pn, 860, 230)
    tv_stand(pn, 2004, 540, 800)
    pn.rrect(250, 360, 830, 800, 28, (56, 56, 66, 255), OUT, 7); pn.rrect(280, 392, 800, 764, 18, (14, 14, 18, 255), None)
    paste_tv(pn, game_surface(480, 330, "retro", t), 300, 420, 780, 750); pn.rrect(300, 420, 780, 750, 14, None, (20, 20, 24, 255), 8)
    pn.line([(540, 990), (520, 1180), (560, 1320)], 6, OUT)
    pn.poly([(0, 1040), (1080, 1040), (1080, 1920), (0, 1920)], (236, 214, 176, 255))
    for k in range(-1, 14): pn.line([(k * 120, 1040), (k * 120 - 100, 1920)], 14, (214, 178, 130, 255))
    for k in range(12): pn.line([(0, 1080 + k * 80), (1080, 1080 + k * 80)], 12, (214, 178, 130, 255))
    back_head(pn, 540, 1470, 215, 11, (140, 142, 148, 255))
def s4(pn, t):   # 2013 wide
    wall(pn, 2013, 1240); window(pn, 80, 380, 190, 320); picture(pn, 420, 360, 230, 150, 2013); lamp(pn, 900, 900); plant(pn, 120, 900)
    couch(pn, 540, 1240, 1000, 440, (248, 246, 240, 255), pillows=((130, 1090, (196, 186, 170, 255)), (940, 1090, (150, 150, 140, 255))))
    person_front(pn, 540, 860, 1.0, "teen", t, "o")
    pn.poly([(0, 1600), (1080, 1600), (1080, 1920), (0, 1920)], (36, 36, 44, 255), OUT, 5)
def s5(pn, t):   # 2013 back shot: flat TV
    wall(pn, 2013, 1010); plant(pn, 130, 930, 1.1); lamp(pn, 930, 860)
    pn.rrect(160, 360, 920, 790, 8, (24, 24, 30, 255), OUT, 7)
    paste_tv(pn, game_surface(740, 410, "hd", t), 170, 370, 910, 780)
    tv_stand(pn, 2013, 540, 870)
    pn.poly([(0, 1180), (1080, 1180), (1080, 1920), (0, 1920)], (206, 168, 122, 255))
    pn.poly([(0, 1560), (1080, 1560), (1080, 1920), (0, 1920)], (248, 246, 240, 255), OUT, 5)
    back_head(pn, 540, 1440, 215, 21, (36, 36, 44, 255), stripes=True)
def s6(pn, t):   # 2026 wide: shocked man
    wall(pn, 2026, 1260); picture(pn, 440, 340, 260, 170, 2026); lamp(pn, 920, 880); plant(pn, 100, 920, 1.2)
    couch(pn, 540, 1260, 1020, 460, (246, 244, 232, 255), pillows=((140, 1100, (140, 168, 128, 255)), (930, 1100, (150, 150, 140, 255))))
    person_front(pn, 540, 880, 1.0, "man", t, "shock", look=(0, -1))
    pn.rrect(230, 1500, 850, 1580, 6, (214, 162, 110, 255), OUT, 6); pn.rrect(300, 1470, 330, 1500, 3, (84, 130, 130, 255), OUT, 3)
    pn.poly([(0, 1640), (1080, 1640), (1080, 1920), (0, 1920)], (36, 36, 44, 255), OUT, 5)
def s7(pn, t):   # 2026 back: the reveal
    u = t - 13.2; wall(pn, 2026, 1010); picture(pn, 800, 330, 180, 120, 2026); plant(pn, 110, 940, 1.2)
    pn.rrect(110, 330, 970, 810, 8, (6, 6, 8, 255), OUT, 7)
    if u > 0.9:
        r = sm((u - 0.9) / 1.0); logo(pn, 540, 560, 0.86 + 0.06 * r, r, 0.6 + 0.4 * math.sin(u * 3))
    pn.rrect(70, 290, 1010, 850, 22, None, (255, 220, 190, int(90 * sm((u - 0.9) / 1.0))), 14)
    if u > 2.4:
        f = ImageFont.truetype(BOLD, int(54 * SS)); a = sm((u - 2.4) / 0.5); X, Y = pn.p(540, 700); pn.d.text((X, Y), "NEON CITY", font=f, fill=(255, 238, 230, int(255 * a)), anchor="mm")
    pn.poly([(0, 1130), (1080, 1130), (1080, 1920), (0, 1920)], (200, 160, 116, 255))
    pn.rrect(70, 1040, 1010, 1130, 10, (214, 162, 110, 255), OUT, 6)
    pn.poly([(0, 1560), (1080, 1560), (1080, 1920), (0, 1920)], (246, 244, 232, 255), OUT, 5)
    back_head(pn, 540, 1430, 215, 31, (252, 252, 252, 255), tank=True)
def s8(pn, t):   # 2026 wide: laugh-cry
    u = t - 16.5; wall(pn, 2026, 1260); picture(pn, 440, 340, 260, 170, 2026); lamp(pn, 920, 880); plant(pn, 100, 920, 1.2)
    couch(pn, 540, 1260, 1020, 460, (246, 244, 232, 255), pillows=((140, 1100, (140, 168, 128, 255)), (930, 1100, (150, 150, 140, 255))))
    wipe = sm((u - 2.6) / 0.4) * (1 - sm((u - 3.7) / 0.4)); sh = math.sin(t * 14) * 6
    person_front(pn, 540, 880 + sh, 1.0, "man", t, "laugh" if wipe < 0.5 else "cry", tear=min(1.0, u / 0.6), wipe=wipe)
    pn.rrect(230, 1500, 850, 1580, 6, (214, 162, 110, 255), OUT, 6); pn.rrect(300, 1470, 330, 1500, 3, (84, 130, 130, 255), OUT, 3)
    pn.poly([(0, 1640), (1080, 1640), (1080, 1920), (0, 1920)], (36, 36, 44, 255), OUT, 5)
SCENES = [(0.0, s1), (1.6, s2), (3.4, s3), (6.2, s4), (8.0, s5), (11.5, s6), (13.2, s7), (16.5, s8)]
def whip(arr, t):
    for c in CUTS:
        dt = abs(t - c)
        if dt < 0.07:
            p = 1 - dt / 0.07; L = int(6 + 70 * p * p); k = np.zeros((1, L), np.float32); k[0, :] = 1.0 / L
            return cv2.filter2D(arr, -1, k, borderType=cv2.BORDER_REFLECT)
    return arr
def frame(t):
    i = max(j for j, s in enumerate(SCENES) if t >= s[0]); t0 = SCENES[i][0]
    z = 1.0 + 0.05 * min(1.0, (t - t0) / 2.2)
    big = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 255)); big.__dict__  # noqa
    d = ImageDraw.Draw(big); d._image = big
    pn = Pen(d, Cam(z, 540, 960)); SCENES[i][1](pn, t)
    img = big.resize((W, H), Image.LANCZOS).convert("RGB")
    arr = np.asarray(img, np.float32); yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    arr = arr * np.clip(1 - 0.18 * (((xx - W / 2) / (W * 0.8)) ** 2 + ((yy - H / 2) / (H * 0.8)) ** 2), 0.7, 1.0)[..., None]
    arr = whip(arr, t); img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB"); dr = ImageDraw.Draw(img)
    yr = [y for (tt, y) in YEARS if t >= tt][-1]; f = ImageFont.truetype(BOLD, 92)
    dr.text((W / 2, 350), yr, font=f, fill=(255, 255, 255), anchor="mm", stroke_width=9, stroke_fill=(0, 0, 0))
    lab = "S L O W   L I G H T"; lf = font(MONO, 22); tw_ = dr.textlength(lab, font=lf)
    dr.rounded_rectangle([W / 2 - tw_ / 2 - 22, 1610 - 22, W / 2 + tw_ / 2 + 22, 1610 + 22], 22, fill=(20, 20, 26)); dr.text((W / 2, 1610), lab, font=lf, fill=(220, 222, 232), anchor="mm")
    return img
def _job(a):
    i, t, out = a; frame(t).save(f"{out}/f{i:04d}.png", compress_level=1); return i
if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "sheet":
        ts = [float(a) for a in sys.argv[3:]]; cols = min(len(ts), 6); rows = math.ceil(len(ts) / cols); tw, th_ = 270, 480
        sheet = Image.new("RGB", (tw * cols, th_ * rows))
        for j, t in enumerate(ts): sheet.paste(frame(t).resize((tw, th_), Image.LANCZOS), ((j % cols) * tw, (j // cols) * th_))
        sheet.save(sys.argv[2]); print("wrote", sys.argv[2])
    elif cmd == "frames":
        from multiprocessing import Pool
        out = sys.argv[2]; os.makedirs(out, exist_ok=True)
        jobs = [(i, i / FPS, out) for i in range(int(DUR * FPS))]
        with Pool(4) as p:
            for n, i in enumerate(p.imap_unordered(_job, jobs)):
                if n % 60 == 0: print(n, "/", len(jobs), flush=True)
    elif cmd == "video":
        out, audio, fr = sys.argv[2:5]
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{fr}/f%04d.png", "-i", audio, "-t", str(DUR), "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", out], check=True); print("wrote", out)
