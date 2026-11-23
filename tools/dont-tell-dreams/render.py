#!/usr/bin/env python3
"""Don't Tell Your Dreams (stickman reel), procedural renderer. PIL + numpy + ffmpeg only.

Four beats, timed to the song's phrases (the song itself is NOT in the file; add it from the
Instagram/Facebook music library when posting):
  0.0-4.0   Don't tell your dreams to everybody around   (hero + glowing star + smilers)
  4.0-8.0   Some people smile but want to see you down   (smiles turn, dagger, hand reaches)
  8.0-12.0  Keep it quiet, don't make a sound            (hug the star in, push in on the face)
  12.0-15.2 Let your success be what shakes the ground   (whip out, shockwave, haters fall)

usage: render.py sheet OUT.png t1 t2 ...     contact sheet of single frames
       render.py video OUT.mp4               full 1080x1920 30 fps render (4 procs)
"""
import math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
from multiprocessing import Pool

W, H, FPS, DUR = 1080, 1920, 30, 15.2
N = int(round(FPS * DUR))
SS = 2
INK = np.array([24, 18, 15], np.float32) / 255
GOLD = np.array([255, 186, 70], np.float32) / 255
SMOKE = np.array([96, 90, 84], np.float32) / 255
FONT = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"

HX, HS = 540, 1.73               # hero x, hero scale
LEG, TOR, HR = 330, 190, 78      # leg / torso / head radius (local units)
HYG = 1394                       # hero ground y (world)

CUES = [(0.5, 3.9, "Don't tell your dreams\nto everybody around"),
        (4.1, 7.7, "Some people smile\nbut want to see you down"),
        (8.1, 11.7, "Keep it quiet,\ndon't make a sound"),
        (12.1, 15.2, "Let your success be what\nshakes the ground")]

# ---------------------------------------------------------------- helpers
def sm(x):
    x = min(1.0, max(0.0, x)); return x * x * (3 - 2 * x)

def key(t, ks, lin=False):
    if t <= ks[0][0]: return ks[0][1]
    for (t0, v0), (t1, v1) in zip(ks, ks[1:]):
        if t <= t1:
            u = (t - t0) / (t1 - t0)
            return v0 + (v1 - v0) * (u if lin else sm(u))
    return ks[-1][1]

def nz(u, seed):
    return (math.sin(u * 0.9 + seed * 12.9) + 0.6 * math.sin(u * 2.3 + seed * 7.7) + 0.3 * math.sin(u * 5.1 + seed * 3.1)) / 1.9

def catmull(pts, n=8):
    P = [np.asarray(p, float) for p in pts]
    if len(P) == 2:
        return np.array([P[0] + (P[1] - P[0]) * k / 10 for k in range(11)])
    Q = [P[0]] + P + [P[-1]]
    out = []
    for i in range(1, len(Q) - 2):
        p0, p1, p2, p3 = Q[i - 1], Q[i], Q[i + 1], Q[i + 2]
        for k in range(n):
            u = k / n
            out.append(0.5 * (2 * p1 + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u + (-p0 + 3 * p1 - 3 * p2 + p3) * u ** 3))
    out.append(P[-1])
    return np.array(out)

def rotp(p, piv, ang):
    c, s = math.cos(ang), math.sin(ang)
    d = np.asarray(p, float) - piv
    return piv + np.array([d[0] * c - d[1] * s, d[0] * s + d[1] * c])

class Cam:
    def __init__(s, cx, cy, z, sh=(0, 0)):
        s.cx, s.cy, s.z, s.sh = cx, cy, z, np.array(sh, float)
    def tf(s, p):
        a = np.asarray(p, float)
        return ((a - [s.cx, s.cy]) * s.z + [W / 2, H / 2] + s.sh) * SS
    def wscale(s, w):
        return w * (s.z ** 0.85) * SS

class Layer:
    def __init__(s, cam, boil):
        s.img = Image.new("L", (W * SS, H * SS), 0)
        s.d = ImageDraw.Draw(s.img)
        s.cam, s.boil = cam, boil
    def line(s, pts, w, seed=0, val=255, wob=2.2, taper=0.25):
        P = catmull(pts)
        n = len(P)
        tg = np.gradient(P, axis=0)
        nr = np.stack([-tg[:, 1], tg[:, 0]], 1)
        nr /= (np.linalg.norm(nr, axis=1, keepdims=True) + 1e-6)
        off = np.array([nz(i * 0.35, seed + s.boil * 0.7) for i in range(n)]) * wob
        P = P + nr * off[:, None]
        S = s.cam.tf(P)
        base = s.cam.wscale(w) / 2
        for i in range(n):
            e = 1.0
            if taper:
                f = i / max(1, n - 1)
                e = 1 - taper * (max(0, 0.2 - f) / 0.2 + max(0, f - 0.8) / 0.2) * 0.9
            r = base * e * (0.86 + 0.28 * nz(i * 0.22, seed + 3))
            r = max(r, 0.8)
            if i < n - 1:
                s.d.line([tuple(S[i]), tuple(S[i + 1])], fill=val, width=max(1, int(2 * r)))
            s.d.ellipse([S[i][0] - r, S[i][1] - r, S[i][0] + r, S[i][1] + r], fill=val)
    def poly(s, pts, val=255):
        S = s.cam.tf(np.asarray(pts, float))
        s.d.polygon([tuple(p) for p in S], fill=val)
    def ell(s, c, rx, ry, ang=0.0, val=255, n=22):
        pts = []
        for k in range(n):
            a = 2 * math.pi * k / n
            x, y = rx * math.cos(a), ry * math.sin(a)
            pts.append((c[0] + x * math.cos(ang) - y * math.sin(ang), c[1] + x * math.sin(ang) + y * math.cos(ang)))
        s.poly(pts, val)

class Light:
    """low-res additive glow + smoke layers"""
    def __init__(s, cam):
        s.g = Image.new("L", (W // 4, H // 4), 0); s.gd = ImageDraw.Draw(s.g)
        s.s = Image.new("L", (W // 4, H // 4), 0); s.sd = ImageDraw.Draw(s.s)
        s.cam = cam
    def glow(s, c, r, inten):
        p = s.cam.tf(c) / (SS * 4); rr = r * s.cam.z / 4
        v = int(255 * min(1, inten))
        if v < 4: return
        tmp = Image.new("L", s.g.size, 0)
        ImageDraw.Draw(tmp).ellipse([p[0] - rr, p[1] - rr, p[0] + rr, p[1] + rr], fill=v)
        s.g = ImageChops.lighter(s.g, tmp)
    def smoke(s, c, rx, ry, a):
        p = s.cam.tf(c) / (SS * 4)
        v = int(255 * min(1, a))
        if v < 4: return
        tmp = Image.new("L", s.s.size, 0)
        ImageDraw.Draw(tmp).ellipse([p[0] - rx * s.cam.z / 4, p[1] - ry * s.cam.z / 4, p[0] + rx * s.cam.z / 4, p[1] + ry * s.cam.z / 4], fill=v)
        s.s = ImageChops.lighter(s.s, tmp)
    def arrays(s, gr, sr):
        g = np.asarray(s.g.filter(ImageFilter.GaussianBlur(gr)).resize((W, H), Image.BILINEAR), np.float32) / 255
        m = np.asarray(s.s.filter(ImageFilter.GaussianBlur(sr)).resize((W, H), Image.BILINEAR), np.float32) / 255
        return g, m

# ---------------------------------------------------------------- characters
def star_pts(c, ro, ri, rot=-math.pi / 2):
    return [(c[0] + (ro if k % 2 == 0 else ri) * math.cos(rot + k * math.pi / 5),
             c[1] + (ro if k % 2 == 0 else ri) * math.sin(rot + k * math.pi / 5)) for k in range(10)]

def dagger(ink, base, ang, sc, val=255, seed=0):
    """blade pointing along +angle direction from the hand"""
    ca, sa = math.cos(ang), math.sin(ang)
    def P(a, b): return (base[0] + (a * ca - b * sa) * sc, base[1] + (a * sa + b * ca) * sc)
    ink.poly([P(8, -9), P(120, -11), P(150, 0), P(120, 11), P(8, 9)], val)      # blade
    ink.line([P(0, -26), P(0, 26)], 9, seed + 1, val, 0.8)                      # guard
    ink.line([P(-6, 0), P(-48, 0)], 13, seed + 2, val, 0.8)                     # grip

def draw_char(ink, x, yg, s, pose, face, seed, rot=0.0, shift=(0, 0), head_erase=True, dag=None, fall=0.0, fdir=1):
    """pose: lean, aL=(elbow,hand), aR=(elbow,hand) in s-units rel. shoulder (+x = screen right).
       face: eye, look, brow, mouth, mo.   returns key points"""
    piv = np.array([x, yg], float)
    sh = np.array(shift, float)
    def T(p):
        q = rotp(p, piv, rot)
        if fall:
            d = q - piv; h = -d[1]
            q = np.array([piv[0] + d[0] + fdir * 0.34 * h * math.sin(fall), piv[1] - h * math.cos(fall) + 0.16 * h * math.sin(fall)])
        return q + sh
    lean = pose.get("lean", 0) * s
    hc0 = np.array([x + lean, yg - (LEG + TOR + HR) * s])
    neck0 = hc0 + [0, HR * s]
    hip0 = neck0 + [-lean * 0.3, TOR * s]
    shl0 = neck0 + [0, 24 * s]
    sp = pose.get("stance", 52)
    kneeL = (hip0 + np.array([x - sp * s - hip0[0], yg - hip0[1]]) * 0.5) + [-6 * s, 0]
    kneeR = (hip0 + np.array([x + sp * s - hip0[0], yg - hip0[1]]) * 0.5) + [6 * s, 0]
    fL = np.array([x - sp * s, yg]); fR = np.array([x + sp * s, yg])
    hc, neck, hip = T(hc0), T(neck0), T(hip0)
    # legs and torso
    ink.line([hip, T(kneeL), T(fL)], 15, seed + 1)
    ink.line([hip, T(kneeR), T(fR)], 15, seed + 2)
    ink.line([T(fL), T(fL + [-26 * s * 0.5, 0])], 15, seed + 3, wob=0.8)
    ink.line([T(fR), T(fR + [26 * s * 0.5, 0])], 15, seed + 4, wob=0.8)
    ink.line([neck, T(neck0 + [0, TOR * s * 0.5 + lean * -0.1]), hip], 15, seed + 5, taper=0.15)
    # arms
    hands = {}
    for side, nm in ((-1, "aL"), (1, "aR")):
        el, hd = pose[nm]
        e = shl0 + np.array([el[0] * s, el[1] * s]); h = shl0 + np.array([hd[0] * s, hd[1] * s])
        ink.line([T(shl0), T(e), T(h)], 14, seed + 6 + side, taper=0.1)
        hands[nm] = T(h)
        if pose.get("fists") or pose.get("mitts", True):
            r = (17 if pose.get("mitts", True) else 12) * s * pose.get("hs", 1.0)
            ink.ell(T(h), r, r * 0.8, rot, 255, 14)
    # head
    if head_erase:
        ink.ell(hc, HR * s * 0.98, HR * s * 0.98, 0, 0, 28)
    pts = []
    for k in range(34):
        a = math.radians(-100 + k * (385 / 33))
        rr = HR * s * (1 + 0.012 * nz(k * 0.5, seed + 9))
        pts.append(hc + np.array([math.cos(a) * rr, math.sin(a) * rr]))
    ink.line(pts, 14, seed + 10, wob=1.4, taper=0.2)
    # hair tufts
    top = hc + [0, -HR * s]
    for k, (dx, dy) in enumerate(((-16, -30), (6, -38), (24, -24))):
        a = top + [dx * s * 0.45, 4 * s]
        ink.line([a, a + [dx * s * 0.5, dy * s * 0.9]], 9, seed + 11 + k, wob=0.6, taper=0.4)
    # face
    def F(dx, dy): return T(hc0 + [dx * s, dy * s])
    look = face.get("look", 0) * 6
    eo = face.get("eye", 1)
    for sd in (-1, 1):
        cx = 32 * sd + look
        if eo > 0.3:
            ink.ell(F(cx, -4), 8.5 * s, 13 * s * min(1, eo), rot, 255, 16)
        else:
            ink.line([F(cx - 15, -4), F(cx, -4 + 7), F(cx + 15, -4)], 6, seed + 20 + sd, wob=0.4, taper=0.3)
    b = face.get("brow", 0)
    if abs(b) > 0.2:
        for sd in (-1, 1):
            inner = F(12 * sd, -34 - b * 14); outer = F(46 * sd, -34 + b * 4 - 2)
            ink.line([inner, outer], 8, seed + 30 + sd, wob=0.5, taper=0.3)
    m = face.get("mouth", 0); mo = face.get("mo", 0)
    if mo > 0.4:
        ink.ell(F(0, 40), 9 * s * mo, 12 * s * mo, rot, 255, 14)
    else:
        ink.line([F(-22, 36), F(0, 36 + 14 * m), F(22, 36)], 7, seed + 40, wob=0.4, taper=0.35)
    if dag:
        ang, vis, fl = dag[:3]
        if vis > 0.02:
            hnd = hands["aR"] if dag[3:] == () else hands[dag[3]]
            pos = hnd if fl is None else fl
            dagger(ink, pos, ang + (rot if fl is None else 0), s * 0.62 * vis)
    return dict(hc=hc, neck=neck, hands=hands, shl=T(shl0), chest=T(neck0 + [0, 100 * s]), hip=hip,
                feet=(T(fL), T(fR)))

# ---------------------------------------------------------------- camera
def camera(t):
    z = key(t, [(0, 1.0), (4, 1.08), (8, 1.32), (8.4, 1.42), (11.5, 2.75)], True)
    cy = key(t, [(0, 700), (8, 640), (9.6, 421), (11.5, 421)], True)
    if t > 11.5:
        u = sm((t - 11.5) / 0.55)
        z = 2.75 + (1.12 - 2.75) * u + (0.05 * max(0, t - 12.05) / 3.1 if t > 12.05 else 0)
        cy = 421 + (759 - 421) * u
    shx = shy = 0
    if t >= 13.0:
        a = 15 * math.exp(-(t - 13.0) * 5.5)
        shx = a * math.sin(t * 61); shy = a * math.cos(t * 53)
    return Cam(540 + 4 * math.sin(t * 0.7), cy + 3 * math.sin(t * 0.5), z, (shx, shy))

# ---------------------------------------------------------------- scene
def scene(t, ink, light, cam):
    tt = t
    # ---- hero state
    smile = key(tt, [(0, 1), (4.2, 1), (5.5, -0.5), (7.5, -0.6), (10, -0.3), (10.6, -0.7)])
    brow = key(tt, [(0, 0), (4.4, 0), (5.6, 0.8), (7.6, 0.8), (8.5, 0.2), (9.9, 0.2), (10.5, -0.9)])
    eye = key(tt, [(0, 1), (8.2, 1), (8.9, 0), (10.0, 0), (10.6, 0.5)])
    look = key(tt, [(0, 0), (1.8, 0), (2.6, 0.9), (3.6, 0.9), (4.2, 0)])
    mo = key(tt, [(0, 0), (5.4, 0), (5.9, 0.7), (7.6, 0.7), (8.1, 0)])
    hug = key(tt, [(0, 0), (6.9, 0), (8.5, 1), (11.0, 1), (11.6, 0)])
    star = key(tt, [(0, 1), (5.0, 1), (6.4, 0.55), (7.2, 0.55), (8.6, 0)])
    chestg = key(tt, [(0, 0.0), (7.0, 0.0), (8.9, 0.9), (12.9, 0.9), (13.05, 1.7), (13.7, 1.05), (15.2, 1.15)])
    breathe = 4 * math.sin(tt * 2.2)

    def lerp2(a, b, u): return (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)
    holdL = ((-62, 52), (-22, 100)); holdR = ((62, 52), (22, 100))
    hugL = ((-130, 95), (-14, 92)); hugR = ((130, 95), (14, 92))
    downL = ((-34, 80), (-28, 170)); downR = ((34, 80), (28, 170))
    pL = (lerp2(holdL[0], hugL[0], sm(hug)), lerp2(holdL[1], hugL[1], sm(hug)))
    pR = (lerp2(holdR[0], hugR[0], sm(hug)), lerp2(holdR[1], hugR[1], sm(hug)))
    if tt > 11.0:
        u = sm((tt - 11.0) / 0.5)
        pL = (lerp2(hugL[0], downL[0], u), lerp2(hugL[1], downL[1], u))
        pR = (lerp2(hugR[0], downR[0], u), lerp2(hugR[1], downR[1], u))
    hero_pose = dict(aL=pL, aR=pR, lean=0, stance=52, mitts=(tt < 11.2), hs=1.0)
    hero_face = dict(eye=eye, look=look, brow=brow, mouth=smile, mo=mo)

    # ---- burst lines behind (beat B)
    bi = key(tt, [(5.4, 0), (6.4, 1), (8.0, 1), (8.9, 0)], True)
    if bi > 0.02 and tt < 9.2:
        hc_world = np.array([HX, HYG - (LEG + TOR + HR) * HS])
        c = cam.tf(hc_world) / SS
        rng = np.random.RandomState(int(tt * 12))
        for k in range(72):
            a = rng.rand() * 2 * math.pi
            r0 = 430 + rng.rand() * 200; r1 = r0 + 500 + rng.rand() * 500
            w = 3 + rng.rand() * 5
            p0 = c + np.array([math.cos(a), math.sin(a)]) * r0 * cam.z ** 0.3
            p1 = c + np.array([math.cos(a), math.sin(a)]) * r1 * cam.z ** 0.3
            perp = np.array([-math.sin(a), math.cos(a)])
            ink.d.polygon([tuple((p0 + perp * w * 0.2) * SS), tuple((p1 + perp * w * 1.6) * SS), tuple((p1 - perp * w * 1.6) * SS), tuple((p0 - perp * w * 0.2) * SS)], fill=int(200 * bi))

    # ---- big smilers (A,B), step back during C
    away = sm((tt - 8.2) / 0.8)
    if tt < 9.2:
        sf = key(tt, [(0, 1), (3.9, 1), (4.9, -1)])
        def sface(extra=0.0):
            return dict(eye=1, look=0.3, brow=min(0, sf) * 1.0 + extra, mouth=sf, mo=0)
        R1x = 975 + 220 * away; R2x = 790 + 160 * away
        L1x = 100 - 220 * away; L2x = 318 - 160 * away
        sway = math.sin(tt * 1.6)
        # far ones first
        draw_char(ink, L2x, HYG + 14, 1.9, dict(aL=((-38, 100), (-26, 190)), aR=((38, 100), (26, 190)), lean=-8 + 6 * sway, stance=48, mitts=False), sface(), 100)
        reach = key(tt, [(0, 0), (4.8, 0), (6.1, 1), (7.3, 1), (8.1, 0)])
        draw_char(ink, R2x, HYG + 10, 1.95, dict(aL=((-60, 70), lerp2((-30, 190), (-150, 120), sm(reach))),
                                                  aR=((38, 100), (26, 190)), lean=8 - 6 * sway, stance=48, mitts=True), sface(), 120)
        # hero
        hero = draw_char(ink, HX, HYG, HS, hero_pose, hero_face, 7)
        draw_char(ink, L1x, HYG + 60, 2.25, dict(aL=((-38, 100), (-30, 190)), aR=((38, 100), (30, 190)), lean=-14 + 5 * sway, stance=44, mitts=False), sface(), 140)
        dv = key(tt, [(1.2, 0), (1.9, 1)])
        # dagger is part of R1's near hand (aL points toward hero, screen-left)
        draw_char(ink, R1x, HYG + 66, 2.3, dict(aL=((-44, 104), (-36, 196)), aR=((46, 100), (38, 190)), lean=10 - 5 * sway, stance=44, mitts=True),
                  sface(), 160, dag=(math.pi / 2 + 0.25, dv, None, "aL"))
    else:
        hero = draw_char(ink, HX, HYG, HS, hero_pose, hero_face, 7)

    # ---- star + glows
    sc = hero["shl"] + np.array([0, 78 * HS])
    sp = key(tt, [(5.0, 0), (6.4, 1), (7.2, 1), (8.6, 0)], True)       # drift to chest
    sc = sc + np.array([0, 8 * HS * sm((tt - 6.9) / 1.6)])
    pulse = 1 + 0.06 * math.sin(tt * 5.2)
    if star > 0.02:
        ro = 60 * HS * star * pulse
        ink.poly(star_pts(sc, ro, ro * 0.46, -math.pi / 2), 0)
        # gold fill is drawn by the compositor from the same polygon
        light.glow(sc, 150 * star + 50, 0.9 * star * pulse)
        scene.star = (sc, ro)
    else:
        scene.star = None
    cg = hero["chest"]
    if chestg > 0.02:
        light.glow(cg + np.array([0, 6]), 120 * min(1.4, chestg), min(1.0, 0.7 * chestg))
        light.glow(cg, 55 * min(1.4, chestg), min(1.0, 0.9 * chestg))
        if tt >= 13.0:
            light.glow(cg, 420 * sm((tt - 13.0) / 0.25) * (1 - 0.5 * sm((tt - 13.2) / 0.6)), 0.8 * (1 - sm((tt - 13.0) / 0.9)))
    # ---- ring of small haters + shockwave (D)
    if tt >= 11.5:
        t0 = 13.0
        offs = [(-262, 22), (-160, -8), (176, 2), (276, 28)]
        for i, (ox, oy) in enumerate(offs):
            dirn = 1 if ox > 0 else -1
            th = t0 + 0.05 * i
            u = min(1.0, max(0.0, (tt - th) / 0.95)); e = 1 - (1 - u) ** 3
            appear = sm((tt - 11.55 - 0.05 * i) / 0.25)
            if appear <= 0: continue
            sx = dirn * 95 * e
            ly = -230 * math.sin(math.pi * min(1.0, u * 1.25))
            rt = 0.0; fa = (math.pi / 2) * 0.93 * sm(u * 1.1)
            hit = u > 0
            fc = dict(eye=0.2 if hit else 1, look=0, brow=0.8 if hit else -0.7, mouth=-0.8, mo=0)
            ps = dict(aL=((-34, 88), (-24, 170)), aR=((34, 88), (30, 175)), lean=-dirn * 6 - (dirn * 30 * u), stance=40, mitts=True)
            fl = None
            if hit:
                hp0 = np.array([HX + ox + 30 * 0.9, HYG + oy - (LEG + TOR * 0.2) * 0.9 * 0.5])
                fl = np.array([HX + ox - dirn * (30 + 90 * e), HYG + oy - 330 * math.sin(math.pi * min(1, u * 1.05)) * (1 - u * 0.3)])
            sca = 0.88
            if appear < 1:
                ps["lean"] += 0
            draw_char(ink, HX + ox, HYG + oy, sca, ps, fc, 300 + i * 17, rot=rt, shift=(sx, ly), fall=fa, fdir=dirn,
                      dag=(math.pi / 2 + 0.2 + (u * 7 * dirn if hit else 0), appear, fl, "aR"))
        if tt >= t0:
            for k in range(2):
                u = (tt - t0 - 0.12 * k) / 1.05
                if 0 < u < 1:
                    r = 70 + 1150 * (1 - (1 - u) ** 2.2)
                    pts = [(HX + r * math.cos(a), HYG + 4 + r * 0.2 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 40)]
                    ink.line(pts + [pts[0], pts[1]], 13 * (1 - u * 0.4), 400 + k, val=int(240 * (1 - u) ** 0.8), wob=1.2, taper=0)
            rng = np.random.RandomState(5)
            for k in range(16):
                a = rng.rand() * 2 * math.pi
                u = (tt - t0 - rng.rand() * 0.15) / 1.4
                if 0 < u < 1:
                    r = 90 + 1000 * (1 - (1 - u) ** 2)
                    pos = np.array([HX + r * math.cos(a), HYG + 20 + r * 0.2 * math.sin(a)])
                    light.smoke(pos, 60 + 120 * u, 34 + 60 * u, 0.55 * (1 - u) ** 1.4)
        # ground wash under everyone
        light.smoke(np.array([HX, HYG + 20]), 640, 70, 0.28 * sm((tt - 11.6) / 0.5))
    # ---- sparks around the star
    if star > 0.05 and tt < 9:
        rng = np.random.RandomState(11)
        for k in range(14):
            ph = (tt * (0.35 + 0.3 * rng.rand()) + rng.rand()) % 1
            a = rng.rand() * 2 * math.pi
            pos = sc + np.array([math.cos(a) * (50 + 70 * rng.rand()) * HS * 0.8, -ph * 190 + math.sin(a) * 30])
            light.glow(pos, 9, 0.9 * (1 - ph) * star)

# ---------------------------------------------------------------- compositor
def build_bg():
    rng = np.random.RandomState(3)
    base = np.zeros((H, W, 3), np.float32)
    base[:] = np.array([214, 205, 189], np.float32) / 255
    n = np.zeros((H, W), np.float32)
    for sz, amp in ((6, 0.03), (28, 0.035), (120, 0.04)):
        r = (rng.rand(H // sz + 2, W // sz + 2) * 255).astype(np.uint8)
        im = Image.fromarray(r).resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(sz * 0.4))
        n += (np.asarray(im, np.float32) / 255 - 0.5) * amp * 2
    base += n[..., None]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 * 0.85 + ((yy - H * 0.46) / (H / 2)) ** 2 * 0.8)
    vig = np.clip(r, 0, 1.5) ** 2.3
    grain = [(rng.randn(H // 2, W // 2) * 0.5).astype(np.float32) for _ in range(4)]
    grain = [np.asarray(Image.fromarray(g).resize((W, H), Image.BILINEAR), np.float32) for g in grain]
    return base, vig, grain

_BG = None
_TXT = {}

def text_layer(i):
    if i in _TXT: return _TXT[i]
    t0, t1, s = CUES[i]
    f = ImageFont.truetype(FONT, 60)
    lay = Image.new("L", (W, 260), 0); d = ImageDraw.Draw(lay)
    lines = s.split("\n"); y = 20
    for ln in lines:
        w = d.textlength(ln, font=f)
        d.text(((W - w) / 2, y), ln, font=f, fill=255); y += 82
    ol = Image.new("L", (W, 260), 0); od = ImageDraw.Draw(ol); y = 20
    for ln in lines:
        w = od.textlength(ln, font=f)
        od.text(((W - w) / 2, y), ln, font=f, fill=255, stroke_width=6); y += 82
    ol = ol.filter(ImageFilter.GaussianBlur(2.4))
    out = (np.asarray(lay, np.float32) / 255, np.asarray(ol, np.float32) / 255)
    _TXT[i] = out
    return out

def render(t):
    global _BG
    if _BG is None: _BG = build_bg()
    base, vig, grain = _BG
    cam = camera(t)
    ink = Layer(cam, int(t * 10))
    light = Light(cam)
    scene(t, ink, light, cam)
    vk = key(t, [(0, 0.5), (8.0, 0.5), (10.5, 0.36), (12.0, 0.22), (15.2, 0.22)], True)
    img = base * (1 - vk * vig[..., None]) * 1.0
    g, sm_ = light.arrays(11, 7)
    # smoke
    img = img * (1 - sm_[..., None] * 0.85) + SMOKE * sm_[..., None] * 0.85
    # glow (additive, warm)
    img = img + GOLD * (g[..., None] * 0.55)
    # star body (gold fill)
    if scene.star:
        c, ro = scene.star
        gl = Image.new("L", (W * SS, H * SS), 0); gd = ImageDraw.Draw(gl)
        S = cam.tf(np.array(star_pts(c, ro * 0.96, ro * 0.96 * 0.46)))
        gd.polygon([tuple(p) for p in S], fill=255)
        ga = np.asarray(gl.resize((W, H), Image.BOX), np.float32)[..., None] / 255
        core = np.array([255, 226, 140], np.float32) / 255
        img = img * (1 - ga) + core * ga
    ia = np.asarray(ink.img.resize((W, H), Image.BOX), np.float32)[..., None] / 255
    img = img * (1 - ia) + INK * ia
    # chest light bleeds through the lines in the late beats
    img = img + GOLD * (g[..., None] * 0.18) * ia
    # text
    for i, (t0, t1, _) in enumerate(CUES):
        a = sm((t - t0) / 0.25) * (1 - sm((t - (t1 - 0.25)) / 0.25))
        if a > 0.01:
            tl, ts = text_layer(i)
            y0 = 1390
            reg = img[y0:y0 + 260]
            reg *= (1 - np.clip(ts[..., None] * 1.6, 0, 1) * 0.82 * a)
            col = np.array([250, 242, 224], np.float32) / 255
            reg[:] = reg * (1 - tl[..., None] * a) + col * tl[..., None] * a
    img = img + grain[int(t * 12) % 4][..., None] * 0.022
    return np.clip(img * 255, 0, 255).astype(np.uint8)

def render_bytes(i):
    return render(i / FPS).tobytes()

def main():
    mode = sys.argv[1]
    if mode == "sheet":
        out = sys.argv[2]; ts = [float(x) for x in sys.argv[3:]]
        with Pool(4) as p:
            fr = p.map(render, ts)
        cols = 4; rows = math.ceil(len(fr) / cols)
        sw, sh = 270, 480
        sheet = Image.new("RGB", (cols * sw, rows * sh))
        for k, f in enumerate(fr):
            sheet.paste(Image.fromarray(f).resize((sw, sh), Image.LANCZOS), ((k % cols) * sw, (k // cols) * sh))
        sheet.save(out)
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
    elif mode == "frame":
        Image.fromarray(render(float(sys.argv[3]))).save(sys.argv[2])

if __name__ == "__main__":
    main()
