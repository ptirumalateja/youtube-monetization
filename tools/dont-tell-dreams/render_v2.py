#!/usr/bin/env python3
"""Don't Tell Your Dreams, v2. Thick ink lines, expressive faces, orbit-the-friends opening, wind-blast finish.

Story (15.2 s, text cues unchanged from v1 so the song phrases still line up):
  0.0-5.0   hero holds the star and walks a circle around his five friends (they smile while he is in front;
            when he passes BEHIND them the masks drop: coin eyes = opportunists, half-lids + knife = cunning)
  5.0-6.4   he stops, smiles, holds the star out to them
  6.4-7.4   he notices a knife: shock (huge eyes, "!", sweat), the masks fall for good
  7.4-8.5   he pulls the star into his chest and hugs it
  8.5-11.7  push in on his face, chest glow builds, friends loom
  11.7-12.2 whip out, one held breath
  12.2-15.2 chest blast: gold rays + wind whoosh blow the friends (and their knives and coins) off screen

usage: render_v2.py sheet OUT.png t1 t2 ...   |   render_v2.py video OUT.mp4
"""
import math, sys, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from multiprocessing import Pool
import render as R
from render import sm, key, nz, catmull, rotp, Cam, Light, star_pts, W, H, FPS, DUR, N, SS, INK, SMOKE

LEG, TOR, HR = 250, 165, 82
GOLDC = np.array([255, 206, 98], np.float32) / 255
CX, GY = 540, 1290                       # centre of the friends' ring, ground y
HERO_END = 910                           # where the hero stops (right of the ring)
T_BLAST = 12.2

# ---------------------------------------------------------------- layers
class Layer2(R.Layer):
    def __init__(s, cam, boil):
        super().__init__(cam, boil)
        s.gimg = Image.new("L", (W * SS, H * SS), 0)
        s.gdr = ImageDraw.Draw(s.gimg); s.idr = s.d
    def G(s): s.d = s.gdr
    def K(s): s.d = s.idr
    def erase(s, c, rx, ry, n=28):
        for dr in (s.idr, s.gdr):
            s.d = dr; s.ell(c, rx, ry, 0, 0, n)
        s.d = s.idr

# ---------------------------------------------------------------- pieces
def arm_ik(S, Hd, ul, fl, side, bend):
    S = np.asarray(S, float); Hd = np.asarray(Hd, float)
    v = Hd - S; d = float(np.linalg.norm(v))
    if d < 1e-3: return S + np.array([0, ul]), S + np.array([0, ul])
    dirv = v / d; d = min(d, ul + fl - 1.0); Hd = S + dirv * d
    a = (ul * ul - fl * fl + d * d) / (2 * d); hh = math.sqrt(max(0.0, ul * ul - a * a))
    perp = np.array([-dirv[1], dirv[0]])
    c = [S + dirv * a + perp * hh, S + dirv * a - perp * hh]
    e = max(c, key=lambda p: p[1]) if bend == "down" else max(c, key=lambda p: p[0] * side)
    return e, Hd

def dagger(L, base, ang, sc, seed=0):
    ca, sa = math.cos(ang), math.sin(ang)
    def P(a, b): return (base[0] + (a * ca - b * sa) * sc, base[1] + (a * sa + b * ca) * sc)
    L.poly([P(6, -12), P(128, -13), P(166, 0), P(128, 13), P(6, 12)], 255)
    L.line([P(0, -30), P(0, 30)], 12, seed + 1, 255, 0.6, 0)
    L.line([P(-4, 0), P(-52, 0)], 17, seed + 2, 255, 0.6, 0.2)
    # blade glint (gold)
    L.G(); L.poly([P(30, -3), P(112, -4), P(112, 0), P(30, 0)], 255); L.K()

def coin(L, c, r=24, ang=0.0):
    L.ell(c, r, r * abs(math.cos(ang)) + 4, 0, 255, 20)
    L.G(); L.ell(c, r - 6, max(3, (r - 6) * abs(math.cos(ang)) + 1), 0, 255, 20); L.K()
    L.ell(c, r - 6, max(3, (r - 6) * abs(math.cos(ang)) + 1), 0, 0, 20)
    L.G(); L.ell(c, r - 6, max(3, (r - 6) * abs(math.cos(ang)) + 1), 0, 255, 20); L.K()

def draw_star(L, c, ro):
    pts = star_pts(c, ro, ro * 0.47)
    L.G(); L.poly(pts, 255); L.K()
    L.line(pts + [pts[0], pts[1]], 11, 77, 255, 0.8, 0)

def draw_face(L, F, s, rot, f, seed):
    es = f.get("eyes", "ball"); ew = f.get("ew", 1.0); lid = f.get("lid", 0.0); pr = f.get("pr", 0.55)
    lk = f.get("look", 0.0); lv = f.get("lookv", 0.0)
    if f.get("blink"): es = "closed" if es in ("ball", "happy") else es
    for sd in (-1, 1):
        cx, cy = 34 * sd, -4
        if es == "happy":
            L.line([F(cx - 18, cy + 9), F(cx, cy - 10), F(cx + 18, cy + 9)], 12, seed + 20 + sd, 255, 0.5, 0.3)
        elif es == "closed":
            L.line([F(cx - 18, cy - 3), F(cx, cy + 9), F(cx + 18, cy - 3)], 12, seed + 20 + sd, 255, 0.5, 0.3)
        elif es == "coin":
            r = 22
            L.ell(F(cx, cy), r * s, r * s, rot, 255, 22)
            L.G(); L.ell(F(cx, cy), (r - 5) * s, (r - 5) * s, rot, 255, 22); L.K()
            L.ell(F(cx, cy), (r - 5) * s, (r - 5) * s, rot, 0, 22)
            L.G(); L.ell(F(cx, cy), (r - 5) * s, (r - 5) * s, rot, 255, 22); L.K()
            L.line([F(cx, cy - 10), F(cx, cy + 10)], 7, seed + 25, 255, 0.4, 0)
            L.line([F(cx - 6, cy - 6), F(cx + 6, cy - 6)], 6, seed + 26, 255, 0.4, 0)
            L.line([F(cx - 6, cy + 6), F(cx + 6, cy + 6)], 6, seed + 27, 255, 0.4, 0)
        else:
            rx, ry = 15 * ew, 19 * ew
            L.ell(F(cx, cy), (rx + 5.5) * s, (ry + 5.5) * s, rot, 255, 24)
            L.ell(F(cx, cy), rx * s, ry * s, rot, 0, 24)
            pcx = cx + lk * rx * 0.6; pcy = cy + lv * ry * 0.5
            prad = 5 + 7 * pr
            L.ell(F(pcx, pcy), prad * s, prad * s, rot, 255, 16)
            L.ell(F(pcx - 3, pcy - 3), 2.6 * s, 2.6 * s, rot, 0, 8)      # highlight keeps it alive
            if lid > 0.04:
                yc = -ry + 2 * ry * lid
                pts = []
                for k in range(26):
                    a = 2 * math.pi * k / 26
                    pts.append(F(cx + (rx + 3) * math.cos(a), cy + min(ry * math.sin(a), yc)))
                L.poly(pts, 255)
    for sd, b in ((-1, f.get("bl")), (1, f.get("brr"))):
        if b is None: continue
        rz, tl = b; by = -42 - rz
        L.line([F(8 * sd, by - tl * 16), F(34 * sd, by - 5 - tl * 5), F(58 * sd, by + tl * 6)], 13, seed + 30 + sd, 255, 0.5, 0.3)
    mt = f.get("mt", "smile"); a = f.get("ma", 1.0)
    if mt == "smile":
        L.line([F(-27, 34), F(0, 34 + 18 * a), F(27, 34)], 12, seed + 40, 255, 0.5, 0.3)
    elif mt == "smirk":
        L.line([F(-22, 45), F(2, 47), F(30, 27)], 12, seed + 40, 255, 0.5, 0.3)
        L.line([F(33, 22), F(40, 31)], 8, seed + 41, 255, 0.3, 0)
    elif mt == "flat":
        L.line([F(-21, 42), F(21, 42)], 12, seed + 40, 255, 0.5, 0.3)
    elif mt == "frown":
        L.line([F(-25, 50), F(0, 50 - 18 * a), F(25, 50)], 12, seed + 40, 255, 0.5, 0.3)
    elif mt == "grin":
        pts = [F(-36, 28), F(36, 28)] + [F(36 * math.cos(b), 28 + 30 * a * math.sin(b)) for b in np.linspace(0, math.pi, 16)]
        L.poly(pts, 255)
        L.poly([F(-30, 32), F(30, 32), F(30, 32 + 10 * a), F(-30, 32 + 10 * a)], 0)
        for k in (-15, 0, 15): L.line([F(k, 32), F(k, 32 + 10 * a)], 5, seed + 45, 255, 0.2, 0)
    elif mt == "O":
        L.ell(F(0, 44), (14 * a + 6) * s, (18 * a + 6) * s, rot, 255, 20)
        L.ell(F(0, 44), 14 * a * s, 18 * a * s, rot, 0, 20)
    elif mt == "scream":
        L.ell(F(0, 46), 22 * a * s, 32 * a * s, rot, 255, 22)
    elif mt == "gritted":
        L.poly([F(-30, 28), F(30, 28), F(30, 54), F(-30, 54)], 255)
        L.poly([F(-23, 34), F(23, 34), F(23, 48), F(-23, 48)], 0)
        for k in (-12, 0, 12): L.line([F(k, 34), F(k, 48)], 5, seed + 45, 255, 0.2, 0)
    if f.get("sweat", 0) > 0.05:
        sw = f["sweat"]; c0 = (66, -34 + 14 * (1 - sw))
        pts = [(0, -20), (8, -5), (11, 6), (6, 15), (0, 17), (-6, 15), (-11, 6), (-8, -5)]
        L.poly([F(c0[0] + p[0], c0[1] + p[1]) for p in pts], 255)
        L.poly([F(c0[0] + p[0] * 0.5, c0[1] + 4 + p[1] * 0.5) for p in pts], 0)

def shoulder(x, yg, s, ln=0.0, bob=0.0):
    return np.array([x + ln * s, yg - (LEG + TOR) * s + 26 * s - bob])

HAIR = {0: [(-26, -26), (-9, -40), (8, -45), (25, -34), (38, -18)], 1: [(0, -34)], 2: [(-24, -34), (24, -34)],
        3: [(-32, -12), (-14, -30), (6, -36)], 4: []}

def draw_char(L, x, yg, s, hands, face, seed, bend=("out", "out"), lean=0.0, walk=(0.0, 0.0), rot=0.0, hstyle=0,
              shift=(0, 0), pivot=None, hair=0.0, knife=None, excl=0.0, fist=False, tremble=0.0):
    piv = np.array(pivot if pivot is not None else (x, yg), float); sh = np.array(shift, float)
    if tremble:
        sh = sh + np.array([math.sin(seed + tremble * 90) * tremble * 5, 0])
    def T(p): return rotp(p, piv, rot) + sh
    ph, wa = walk
    bob = abs(math.sin(ph)) * 8 * s * wa
    ln = lean * s
    hc0 = np.array([x + ln, yg - (LEG + TOR + HR) * s - bob])
    neck0 = hc0 + [0, HR * s]; hip0 = neck0 + [-ln * 0.35, TOR * s]; shl0 = neck0 + [0, 26 * s]
    sp = 48
    feet = []
    for sd in (-1, 1):
        a = ph + (0 if sd < 0 else math.pi)
        f = np.array([x + sd * sp * s + math.sin(a) * 36 * s * wa, yg - max(0.0, math.cos(a)) * 22 * s * wa])
        k = hip0 + (f - hip0) * 0.5 + [sd * 7 * s + math.sin(a) * 10 * s * wa, 0]
        L.line([T(hip0), T(k), T(f)], 25, seed + 1 + sd)
        L.line([T(f), T(f + [sd * 30 * s, 0])], 25, seed + 4 + sd, 255, 0.5, 0.4)
        feet.append(T(f))
    L.line([T(neck0), T(neck0 + [-ln * 0.1, TOR * s * 0.5]), T(hip0)], 25, seed + 5, 255, 1.8, 0.15)
    hw = []
    for i, (sd, nm) in enumerate(((-1, "L"), (1, "R"))):
        hrel = hands[i]
        h = shl0 + np.array(hrel, float) * s
        e, h = arm_ik(shl0, h, 98 * s, 98 * s, sd, bend[i])
        L.line([T(shl0), T(e), T(h)], 22, seed + 6 + sd, 255, 1.6, 0.1)
        r = (19 if not fist else 16) * s
        L.ell(T(h), r, r * 0.86, rot, 255, 16)
        hw.append(T(h))
    L.erase(T(hc0), HR * s * 0.97, HR * s * 0.97)
    pts = []
    for k in range(36):
        a = math.radians(-100 + k * (388 / 35)); rr = HR * s * (1 + 0.012 * nz(k * 0.5, seed + 9))
        pts.append(T(hc0 + np.array([math.cos(a) * rr, math.sin(a) * rr])))
    L.line(pts, 22, seed + 10, 255, 1.4, 0.2)
    top = hc0 + [0, -HR * s]
    for k, (dx, dy) in enumerate(HAIR[hstyle]):
        a0 = top + [dx * s * 0.45, 5 * s]
        L.line([T(a0), T(a0 + [dx * s * 0.5 - hair * 22 * s, dy * s * 0.9 + abs(hair) * 10 * s])], 14, seed + 11 + k, 255, 0.5, 0.4)
    def F(dx, dy): return T(hc0 + [dx * s, dy * s])
    draw_face(L, F, s, rot, face, seed)
    if excl > 0.02:
        e0 = T(hc0 + [-40 * s, -HR * s - 70 * s]); k = excl
        L.line([e0 + [0, -34 * s * k], e0 + [0, 14 * s * k]], 17 * k + 2, seed + 50, 255, 0.4, 0.3)
        L.ell(e0 + [0, 42 * s * k], 9 * s * k + 1, 9 * s * k + 1, 0, 255, 12)
        for a in (-0.9, 0.0, 0.9):
            L.line([e0 + [math.sin(a) * 60 * s * k, -math.cos(a) * 20 * s * k - 10 * s], e0 + [math.sin(a) * 88 * s * k, -math.cos(a) * 36 * s * k - 18 * s]], 8, seed + 51, 255, 0.2, 0)
    if knife:
        ang, vis, pos = knife
        if vis > 0.02: dagger(L, hw[0] if pos is None else pos, ang + (rot if pos is None else 0), s * 0.68 * vis, seed)
    return dict(hc=T(hc0), shl=T(shl0), chest=T(neck0 + [0, 90 * s]), hands=hw, feet=feet)

# ---------------------------------------------------------------- timeline
RING = [(-141, 0.81), (141, 0.81), (-228, -0.31), (228, -0.31), (0, -1.0)]
ROLE = ["opp", "cun", "cun", "opp", "cun"]
THR = [0.30, 0.45, 0.62, 0.38, 0.52]
FLY = {0: -1, 1: -1, 2: -1, 3: -1, 4: -1}        # all blown to the left, away from the hero

CAMK = [(0.0, 1.00, 540, 960, 0), (5.0, 1.05, 580, 940, 0), (5.9, 1.22, 740, 880, 0), (6.4, 1.22, 740, 880, 0),
        (6.75, 1.75, 880, 740, 0), (7.4, 1.6, 890, 740, 0), (8.5, 2.2, 900, 640, 0), (11.65, 2.7, 902, 610, 1),
        (11.75, 2.7, 902, 610, 0), (12.15, 0.95, 700, 960, 0), (13.4, 0.98, 700, 960, 1), (14.6, 1.02, 910, 960, 0),
        (15.2, 1.04, 910, 960, 1)]

def camera(t):
    ks = CAMK
    if t <= ks[0][0]: z, cx, cy = ks[0][1:4]
    else:
        z, cx, cy = ks[-1][1:4]
        for a, b in zip(ks, ks[1:]):
            if t <= b[0]:
                u = (t - a[0]) / (b[0] - a[0]); u = u if b[4] else sm(u)
                z, cx, cy = [a[i] + (b[i] - a[i]) * u for i in (1, 2, 3)]
                break
    shx = shy = 0
    if t >= T_BLAST:
        a = 20 * math.exp(-(t - T_BLAST) * 5); shx = a * math.sin(t * 63); shy = a * math.cos(t * 51)
    if 6.45 < t < 7.3:
        a = 7 * (1 - sm((t - 6.45) / 0.85)); shx += a * math.sin(t * 80); shy += a * math.cos(t * 70)
    return Cam(cx + 3 * math.sin(t * 0.7), cy + 3 * math.sin(t * 0.5), z, (shx, shy))

def blink(t, k): return ((t * 0.43 + k * 0.37) % 1.0) < 0.07

def hero_state(t):
    u0, u1 = 0.45, 5.0
    th = math.pi / 2 + 1.5 * math.pi * sm((t - u0) / (u1 - u0))
    hx = CX + 370 * math.cos(th); hd = math.sin(th)
    s = 1.55 * (1 + 0.12 * hd); yg = GY + 125 * hd
    wa = sm((t - u0) / 0.35) * (1 - sm((t - u1 + 0.45) / 0.45))
    ph = th * 4.4
    lean = -math.sin(th) * 9 * wa
    return th, hx, hd, s, yg, wa, ph, lean

def hero_face(t, hd, wa):
    f = dict(eyes="ball", ew=1.0, lid=0.0, pr=0.6, look=0.0, lookv=0.0, mt="smile", ma=1.3, bl=(6, 0.25), brr=(6, 0.25))
    if blink(t, 9): f["blink"] = True
    if t < 5.2:
        f["look"] = -math.sin(math.pi / 2 + 1.5 * math.pi * sm((t - 0.45) / 4.55)) * 0.9
        f["mt"] = "smile"; f["ma"] = 1.3
    elif t < 6.35:                                   # offering
        f.update(look=-0.9, ma=1.6, bl=(10, 0.55), brr=(10, 0.55))
        if t < 5.5: f.update(eyes="happy")
    elif t < 6.5:                                    # notices
        u = sm((t - 6.35) / 0.15)
        f.update(look=-0.8, lookv=0.7 * u, ew=1.0 + 0.15 * u, ma=1.0 - 0.8 * u, mt="smile" if u < 0.5 else "flat", bl=(8, 0.3), brr=(14, 0.6))
    elif t < 7.35:                                   # shock
        f.update(ew=1.55, pr=0.28, look=-0.5, lookv=0.3, mt="O", ma=1.15, bl=(20, 0.85), brr=(20, 0.85), sweat=sm((t - 6.5) / 0.3))
        f.pop("blink", None)
    elif t < 8.45:                                   # hurt, hugging the star
        u = sm((t - 7.35) / 0.5)
        f.update(eyes="closed" if u > 0.4 else "ball", mt="frown", ma=0.9, bl=(6, 0.8), brr=(6, 0.8), sweat=1 - u)
    elif t < 10.0:                                   # calm, eyes shut
        f.update(eyes="closed", mt="flat", bl=(2, -0.1), brr=(2, -0.1)); f.pop("blink", None)
    elif t < T_BLAST + 0.3:                          # resolve
        u = sm((t - 10.0) / 0.5)
        f.update(eyes="ball" if u > 0.15 else "closed", lid=0.42, pr=0.8, look=0.0, mt="gritted", bl=(-2, -0.95), brr=(-2, -0.95))
        f.pop("blink", None)
    else:                                            # calm power
        f.update(lid=0.34, pr=0.8, mt="smirk", ma=1.0, bl=(5, -0.2), brr=(-1, -0.7))
    return f

def scene(t, L, light, cam):
    th, hx, hd, hs, hyg, wa, ph, lean = hero_state(t)
    orbit_end = t >= 5.0
    if orbit_end: hx, hd, hs, hyg = HERO_END, 0.0, 1.55, GY
    items = []
    if 0.2 < t < 5.7:
        fade = sm((t - 0.2) / 0.3) * (1 - sm((t - 5.0) / 0.6))
        for k in range(44):
            a0 = k * 2 * math.pi / 44; a1 = a0 + 0.085
            amid = (a0 + 0.04) % (2 * math.pi)
            trail = ((th - (a0 + 0.04)) % (2 * math.pi)) < 2.6 and t < 5.0
            L.line([(CX + 370 * math.cos(a0), GY + 125 * math.sin(a0) + 4), (CX + 370 * math.cos(a1), GY + 125 * math.sin(a1) + 4)], 9, 900 + k,
                   int((120 if trail else 55) * fade), 0.5, 0)

    # ---- friends
    close = sm((t - 6.9) / 0.9)
    tb = t - T_BLAST
    for i, (ox, dp) in enumerate(RING):
        fx = CX + ox + (48 + 10 * i) * close * (1 if i in (1, 3) else 0.5)
        fs = 1.25 * (1 + 0.1 * dp) * (1 + 0.14 * close * (1 if dp > 0 else 0.5))
        fyg = GY + 38 * dp + 22 * close * (1 if dp > 0 else 0)
        items.append((fyg, "f", i, fx, fs))
    # ---- hero
    items.append((hyg, "h", 0, hx, hs))
    items.sort(key=lambda it: it[0])

    star_c = None
    for yg, kind, i, x, s in items:
        # soft ground shadow
        light.smoke(np.array([x, yg + 6]), 78 * s, 15 * s, 0.30)
        if kind == "h":
            hand_rel = None
            off = key(t, [(5.0, 0), (5.7, 1), (6.4, 1), (6.75, 0.15), (7.3, 0.0)])
            hug = key(t, [(0, 0), (7.2, 0), (8.5, 1), (11.5, 1), (12.0, 0)])
            standp = sm((t - 11.8) / 0.5)
            sc = key(t, [(0, 1), (7.3, 1), (8.7, 0)])
            pulse = 1 + 0.05 * math.sin(t * 5.4)
            C = np.array([-108 * off, 72 - 12 * off])                  # star centre, shoulder-relative, s-units
            C = C + np.array([0, 10 * sm((t - 7.4) / 1.2)])
            hold = [(C[0] - 26, C[1] + 32), (C[0] + 26, C[1] + 32)]
            if off > 0.02:
                hold = [(C[0] - 20, C[1] + 34), (C[0] + 44, C[1] + 22)]
            hugp = [(26, 80), (-26, 80)]
            stand = [(-40, 172), (40, 172)]
            def mix(a, b, u): return [(a[k][0] + (b[k][0] - a[k][0]) * u, a[k][1] + (b[k][1] - a[k][1]) * u) for k in (0, 1)]
            hands = mix(mix(hold, hugp, sm(hug)), stand, standp)
            bend = ("out", "out") if (standp < 0.5 and hug < 0.35) else ("down", "down")
            ln = lean
            if t >= T_BLAST: ln += 8 * math.exp(-tb * 2.2)
            hair = 0.0 if t < T_BLAST else 1.0 * math.exp(-tb * 0.9) + 0.25
            walk = (ph, wa)
            sh_w = shoulder(x, yg, s, ln, abs(math.sin(ph)) * 8 * s * wa)
            if sc > 0.02 and not (t >= T_BLAST):
                sc_w = sh_w + C * s
                draw_star(L, sc_w, 62 * s * sc * pulse)
                star_c = (sc_w, sc * pulse, s)
            excl = key(t, [(6.5, 0), (6.62, 1.25), (6.8, 1.0), (7.3, 1.0), (7.5, 0)])
            hdv = draw_char(L, x, yg, s, hands, hero_face(t, hd, wa), 7, bend=bend, lean=ln, walk=walk, hair=hair,
                            excl=excl, fist=(standp > 0.5), tremble=(0.0 if not (6.5 < t < 7.3) else 0.6))
            hero = hdv
        else:
            truth_peek = min(1.0, max(0.0, (-hd - 0.1) / 0.5)) > THR[i] and t < 5.2
            final = t > 6.45 + 0.06 * i
            truth = (truth_peek or final)
            fx = x
            look = max(-1.0, min(1.0, (hx - fx) / 260))
            role = ROLE[i]
            raise_k = sm((t - 7.0) / 0.7)
            blk = blink(t, i)
            if not truth:
                face = dict(eyes="happy", mt="smile", ma=1.4, bl=(5, 0.3), brr=(5, 0.3), blink=blk)
                hands = [(-14, 126), (14, 126)]; knife = None
            elif role == "opp":
                wig = math.sin(t * 22 + i) * 7
                face = dict(eyes="coin", mt="grin", ma=1.0, bl=(13, 0.55), brr=(13, 0.55))
                hands = [(-10 + wig, 104), (10 - wig, 100)]; knife = None
            else:
                lv = -0.75 if (hd < -0.1 and t < 5.2) else 0.15
                face = dict(eyes="ball", ew=1.0, lid=0.5, pr=0.7, look=look if lv > 0 else 0.0, lookv=lv,
                            mt="smirk", ma=1.0, bl=(11, 0.1), brr=(-6, -0.85))
                hands = [(-48, 150 - 105 * raise_k), (30, 140)]
                kang = (math.pi / 2 + 0.42) + (-math.pi / 2 - 0.3 - (math.pi / 2 + 0.42)) * raise_k
                knife = (kang, sm((t - (6.45 + 0.06 * i)) / 0.2) if t > 5.2 else sm(((-hd) - 0.15) / 0.3), None)
            fl = 0.0
            shift = (0, 0); rot = 0.0; pivot = None; ssc = s
            if t >= T_BLAST:
                rank = {1: 0, 3: 1, 4: 2, 0: 3, 2: 4}[i]
                tau = max(0.0, tb - 0.04 * rank)
                if tau > 0:
                    vx = -(1900 + 260 * rank); vy = -(620 + 70 * rank); g = 2300
                    shift = (vx * tau, vy * tau + 0.5 * g * tau * tau)
                    rot = -(tau * (9 + rank * 1.5) + 0.4 * i)
                    pivot = (x, yg - LEG * s)
                    face = dict(eyes="ball", ew=1.5, pr=0.3, lid=0.0, look=0.7, lookv=-0.2, mt="scream", ma=1.0, bl=(20, 0.9), brr=(20, 0.9), sweat=1.0)
                    hands = [(-60, -50), (60, -62)]
                    if role == "cun":
                        knife = (math.pi / 2 + 0.2, 1.0, None)
                    ssc = s * (1 - 0.25 * sm(tau / 0.8) * (1 if i == 4 else 0))
                else:
                    face = dict(eyes="ball", ew=1.2, pr=0.4, lid=0.0, mt="O", ma=0.8, bl=(14, 0.8), brr=(14, 0.8))
            tw = max(0.0, tb - 0.04 * {1: 0, 3: 1, 4: 2, 0: 3, 2: 4}[i]) if t >= T_BLAST else 0.0
            if t >= T_BLAST and tw > 0 and knife:
                # knife leaves the hand on its own path
                ang, vis, _ = knife
                sh_w = shoulder(x, yg, s)
                hand0 = sh_w + np.array(hands[0]) * s
                pos = hand0 + np.array([-(2600) * tw, -(480) * tw + 0.5 * 2300 * tw * tw])
                knife = (ang + (-tw * 14), 1.0, pos)
                if False: pass
            draw_char(L, x, yg, ssc, hands, face, 100 + i * 31, bend=("down", "out" if role != "cun" else "down"), hstyle=[1, 2, 3, 4, 1][i],
                      rot=rot, shift=shift, pivot=pivot, knife=knife)
    # ---- coins spill from the opportunists at the blast
    if t >= T_BLAST:
        for i in (0, 3):
            for k in range(5):
                tau = tb - 0.05 - 0.03 * k
                if tau <= 0: continue
                x0 = CX + RING[i][0]; y0 = GY - 520 + 38 * RING[i][1]
                px = x0 - (900 + 200 * k) * tau; py = y0 - (500 - 90 * k) * tau + 0.5 * 2300 * tau * tau
                coin(L, (px, py), 24, tau * 12 + k)
    # ---- star / chest light
    if star_c is not None:
        c, k, s = star_c
        light.glow(c, 105 * k * s + 30, 0.85 * k)
        rng = np.random.RandomState(11)
        for q in range(14):
            phs = (t * (0.35 + 0.3 * rng.rand()) + rng.rand()) % 1; a = rng.rand() * 2 * math.pi
            light.glow(c + np.array([math.cos(a) * (50 + 80 * rng.rand()) * s, -phs * 200 + math.sin(a) * 30]), 9, 0.9 * (1 - phs) * k)
    cg = hero["chest"]
    chestg = key(t, [(0, 0), (7.6, 0), (9.0, 0.9), (11.6, 1.2), (11.95, 0.5), (T_BLAST, 0.5), (T_BLAST + 0.12, 2.2), (T_BLAST + 0.9, 1.1), (15.2, 1.1)])
    if chestg > 0.02:
        light.glow(cg + np.array([0, 4]), 130 * min(1.6, chestg), min(1.0, 0.7 * chestg))
        light.glow(cg, 58 * min(1.6, chestg), min(1.0, 0.95 * chestg))
        if T_BLAST <= t < T_BLAST + 0.9:
            u = (t - T_BLAST) / 0.9
            light.glow(cg, 520 * sm(u * 3), 0.9 * (1 - u))
    # ---- gold rays + wind whoosh
    if t >= T_BLAST - 0.02:
        L.G()
        rng = np.random.RandomState(4)
        for q in range(30):
            a = q * (2 * math.pi / 30) + rng.rand() * 0.1 + tb * 0.25
            u = min(1.0, tb / 0.55)
            r0 = 40 + 60 * u; r1 = 80 + (900 + rng.rand() * 600) * (1 - (1 - u) ** 2.4)
            wv = 10 + 14 * rng.rand()
            c0 = np.array(cg); d0 = np.array([math.cos(a), math.sin(a)]); pp = np.array([-d0[1], d0[0]])
            al = int(165 * max(0.0, 1 - tb / 1.3))
            if al > 4:
                L.poly([c0 + d0 * r0, c0 + d0 * r1 + pp * wv, c0 + d0 * r1 - pp * wv], al)
        L.K()
        rng = np.random.RandomState(8)
        for q in range(30):
            yq = cg[1] - 640 + q * 46 + rng.randn() * 16
            spd = 3100 + rng.rand() * 1900; ln_ = 520 + rng.rand() * 800
            tq = tb - 0.015 * q * (1 if q % 2 else 0.4) - rng.rand() * 0.1
            if tq <= 0: continue
            headx = cg[0] - 70 - spd * tq; tailx = min(headx + ln_, cg[0] - 60)
            if tailx <= headx + 30: continue
            xs = np.linspace(headx, tailx, 9); amp = 14 + 22 * rng.rand(); ph0 = rng.rand() * 6
            pts = [(xx, yq + amp * math.sin(xx / 150 + ph0 + tb * 6) * (1 - (xx - headx) / max(1, (tailx - headx)) * 0.4)) for xx in xs]
            al = int(215 * max(0.0, 1 - tb / 1.7))
            if al > 6: L.line(pts, 17 + 9 * rng.rand(), 600 + q, al, 1.0, 0.7)
        # dust swept along the ground
        for q in range(12):
            tq = tb - 0.03 * q
            if tq <= 0: continue
            light.smoke(np.array([cg[0] - 120 - 2300 * tq - 40 * q, GY + 20 + rng.rand() * 30]), 90 + 120 * tq, 40 + 40 * tq, 0.5 * max(0, 1 - tq / 1.1))
    return hero

# ---------------------------------------------------------------- compositor
_BG = None
def render(t):
    global _BG
    if _BG is None: _BG = R.build_bg()
    base, vig, grain = _BG
    cam = camera(t)
    L = Layer2(cam, int(t * 10)); light = Light(cam)
    scene(t, L, light, cam)
    vk = key(t, [(0, 0.40), (8.0, 0.40), (11.0, 0.34), (12.4, 0.22), (15.2, 0.22)], True)
    img = base * (1 - vk * vig[..., None])
    g, sm_ = light.arrays(11, 7)
    img = img * (1 - sm_[..., None] * 0.8) + SMOKE * sm_[..., None] * 0.8
    img = img + GOLDC * (g[..., None] * 0.55)
    ga = np.asarray(L.gimg.resize((W, H), Image.BOX), np.float32)[..., None] / 255
    img = img * (1 - ga) + GOLDC * 1.0 * ga
    ia = np.asarray(L.img.resize((W, H), Image.BOX), np.float32)[..., None] / 255
    img = img * (1 - ia) + INK * ia
    img = img + GOLDC * (g[..., None] * 0.16) * ia
    for i, (t0, t1, _) in enumerate(R.CUES):
        a = sm((t - t0) / 0.25) * (1 - sm((t - (t1 - 0.25)) / 0.25))
        if a > 0.01:
            tl, ts = R.text_layer(i); y0 = 1390
            reg = img[y0:y0 + 260]
            reg *= (1 - np.clip(ts[..., None] * 1.6, 0, 1) * 0.82 * a)
            col = np.array([250, 242, 224], np.float32) / 255
            reg[:] = reg * (1 - tl[..., None] * a) + col * tl[..., None] * a
    img = img + grain[int(t * 12) % 4][..., None] * 0.022
    return np.clip(img * 255, 0, 255).astype(np.uint8)

def render_bytes(i): return render(i / FPS).tobytes()

def main():
    mode = sys.argv[1]
    if mode == "sheet":
        out = sys.argv[2]; ts = [float(x) for x in sys.argv[3:]]
        with Pool(4) as p: fr = p.map(render, ts)
        cols = 4; rows = math.ceil(len(fr) / cols); sw, sh = 270, 480
        sheet = Image.new("RGB", (cols * sw, rows * sh))
        for k, f in enumerate(fr):
            sheet.paste(Image.fromarray(f).resize((sw, sh), Image.LANCZOS), ((k % cols) * sw, (k // cols) * sh))
        sheet.save(out)
    elif mode == "frame":
        Image.fromarray(render(float(sys.argv[3]))).save(sys.argv[2])
    elif mode == "video":
        out = sys.argv[2]
        cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
               "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-t", f"{DUR}", "-c:v", "libx264", "-crf", "17", "-preset", "medium",
               "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", out]
        pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        with Pool(4) as p:
            for k, b in enumerate(p.imap(render_bytes, range(N), chunksize=3)):
                pr.stdin.write(b)
                if k % 60 == 0: print("frame", k, "/", N, flush=True)
        pr.stdin.close(); pr.wait()

if __name__ == "__main__":
    main()
