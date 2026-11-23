#!/usr/bin/env python3
"""How Much of You Is Actually You? v2: immersive 3D version, voice-led (PIL + numpy + ffmpeg).

Timeline is locked to the processed voiceover (vo_proc.wav, 24.3 s):
  0.00-3.38  HOW MUCH OF YOU IS ACTUALLY YOU?     volumetric particle human, slow orbit
  3.79       LESS THAN HALF.                      recolour wave (gold = human cells, teal = bacteria), boom
  5.18-7.64  SO WHO ELSE IS IN THERE?             camera dives THROUGH the body (motion streaks)
  7.2-13.9   microbial world: depth of field, shaded cells and bacteria, light shafts
             8.1-10.1 gold counter to 30T, 10.35-12.3 teal counter to 38T, 12.66 THEY OUTNUMBER YOU.
  14.0-17.3  bars: HOW MANY vs HOW HEAVY (an apple)
  17.45-19.95 camera pulls back out through the body; 17.7 YOU HAVE NEVER BEEN ALONE.
  20.2-24.9  silhouette (same as frame 0, loops) + NEXT: THE OLDEST THING IN YOU IS OLDER THAN THE SUN.
Data: Sender, Fuchs & Milo (2016), PLoS Biology 14(8): ~30T human cells, ~38T bacteria, 70 kg man, bacteria ~0.2 kg.

usage: render3d.py sheet OUT.png t1 t2 ...  |  render3d.py video OUT.mp4 [audio.wav]
"""
import math, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps
from multiprocessing import Pool

W, H, FPS, DUR = 1080, 1920, 30, 24.9
N = int(round(FPS * DUR))
FONT_B = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
FONT_S = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
FONT_M = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"
CREAM = (243, 234, 215); GOLD = (255, 191, 77); TEAL = (52, 214, 196)
CF = np.array(CREAM, np.float32) / 255; GF = np.array(GOLD, np.float32) / 255; TF = np.array(TEAL, np.float32) / 255
COL = {"cream": CREAM, "gold": GOLD, "teal": TEAL}
HITS = [3.79, 7.55, 12.66, 14.2, 17.7]
F_BODY = 1400.0

def sm(x):
    x = min(1.0, max(0.0, x)); return x * x * (3 - 2 * x)

def key(t, ks):
    if t <= ks[0][0]: return ks[0][1]
    for (t0, v0), (t1, v1) in zip(ks, ks[1:]):
        if t <= t1: return v0 + (v1 - v0) * sm((t - t0) / (t1 - t0))
    return ks[-1][1]

# ------------------------------------------------------------------ static data
def build_body():
    rng = np.random.RandomState(7)
    CWD, CHT = 540, 1000
    m = Image.new("L", (CWD, CHT), 0); d = ImageDraw.Draw(m)
    def cap(p0, r0, p1, r1, n=28):
        for k in range(n + 1):
            u = k / n; x = p0[0] + (p1[0] - p0[0]) * u; y = p0[1] + (p1[1] - p0[1]) * u; r = r0 + (r1 - r0) * u
            d.ellipse([x - r, y - r, x + r, y + r], fill=255)
    cap((270, 92), 66, (270, 114), 66)
    cap((270, 168), 23, (270, 218), 32)
    cap((270, 250), 88, (270, 330), 92); cap((270, 330), 92, (270, 450), 74); cap((270, 450), 74, (270, 540), 80)
    cap((205, 262), 40, (335, 262), 40)
    for sd in (-1, 1):
        cx = 270
        cap((cx + sd * 92, 262), 38, (cx + sd * 122, 400), 31); cap((cx + sd * 122, 400), 31, (cx + sd * 142, 530), 25); cap((cx + sd * 142, 530), 25, (cx + sd * 152, 600), 26)
        cap((cx + sd * 48, 560), 64, (cx + sd * 56, 770), 46); cap((cx + sd * 56, 770), 46, (cx + sd * 62, 945), 30); cap((cx + sd * 62, 945), 30, (cx + sd * 70, 985), 32)
    a = np.asarray(m) > 128
    blur = np.asarray(m.filter(ImageFilter.GaussianBlur(20)), np.float32) / 255
    zh = 72 * np.sqrt(np.clip((blur - 0.12) / 0.88, 0, 1))
    gy, gx = np.gradient(zh)
    ys, xs = np.nonzero(a)
    n = 20000
    idx = rng.choice(len(xs), n, replace=False)
    x = xs[idx].astype(np.float32); y = ys[idx].astype(np.float32); zhp = zh[ys[idx], xs[idx]]
    shell = rng.rand(n) < 0.6
    sign = np.where(rng.rand(n) < 0.62, 1.0, -1.0)
    z = np.where(shell, sign * zhp, (rng.rand(n) * 2 - 1) * zhp * 0.9)
    nx, ny = -gx[ys[idx], xs[idx]], -gy[ys[idx], xs[idx]]
    nrm = np.sqrt(nx ** 2 + ny ** 2 + 1.0)
    nx, ny, nzv = nx / nrm, ny / nrm, 1.0 / nrm * sign
    L = np.array([-0.45, -0.5, 0.74]); L = L / np.linalg.norm(L)
    lit = np.clip(nx * L[0] + ny * L[1] + nzv * L[2], 0, 1)
    rim = (1 - np.abs(nzv)) ** 1.5
    bright = np.where(shell, 0.42 + 0.55 * lit + 0.55 * rim, 0.30 + 0.12 * rng.rand(n))
    bright = np.clip(bright, 0.25, 1.15)
    B = dict(X=((x - 270) * 0.9).astype(np.float32), Y=((y - 500) * 0.9).astype(np.float32), Z=(z * 0.9).astype(np.float32),
             r=(1.5 + rng.rand(n) * 1.5).astype(np.float32), br=bright.astype(np.float32), ph=(rng.rand(n) * 6.28).astype(np.float32),
             fx=(0.6 + rng.rand(n) * 1.4).astype(np.float32), fy=(0.6 + rng.rand(n) * 1.4).astype(np.float32),
             teal=(rng.rand(n) < 0.56), jit=rng.rand(n).astype(np.float32), ang=(rng.rand(n) * 6.28).astype(np.float32))
    B["yn"] = ((B["Y"] + 450) / 900).clip(0, 1)
    return B

def rod_sprite(w=192, h=72):
    y, x = np.mgrid[0:h, 0:w].astype(np.float32); cx, cy = w / 2, h / 2; half = (w - h) / 2
    px = np.clip(x - cx, -half, half); dist = np.sqrt((x - cx - px) ** 2 + (y - cy) ** 2)
    R = h / 2 - 2; r = dist / R; inside = (r < 1).astype(np.float32)
    rim = np.exp(-((r - 0.9) / 0.09) ** 2); body = 0.24 * np.sqrt(np.clip(1 - r ** 2, 0, 1))
    spec = np.exp(-(((x - cx + half * 0.25) / (w * 0.28)) ** 2 + ((y - cy + R * 0.38) / (R * 0.16)) ** 2)) * 0.7
    return np.clip((rim * 0.95 + body + spec * 0.5) * inside, 0, 1.4)

def sphere_sprite(n=96):
    y, x = np.mgrid[0:n, 0:n].astype(np.float32); c = (n - 1) / 2; r = np.sqrt(((x - c) / (c - 2)) ** 2 + ((y - c) / (c - 2)) ** 2)
    inside = (r < 1).astype(np.float32)
    rim = np.exp(-((r - 0.9) / 0.09) ** 2); body = 0.24 * np.sqrt(np.clip(1 - r ** 2, 0, 1))
    spec = np.exp(-(((x - c * 0.7) / (n * 0.16)) ** 2 + ((y - c * 0.62) / (n * 0.14)) ** 2)) * 0.8
    return np.clip((rim * 0.95 + body + spec * 0.5) * inside, 0, 1.4)

def cell_sprite(n=256):
    rng = np.random.RandomState(5)
    y, x = np.mgrid[0:n, 0:n].astype(np.float32); c = (n - 1) / 2
    xx = (x - c) / (c - 3); yy = (y - c) / (c - 3); r = np.sqrt(xx ** 2 + yy ** 2); inside = (r < 1).astype(np.float32)
    rim = np.exp(-((r - 0.93) / 0.045) ** 2) * 1.1
    body = 0.16 * np.sqrt(np.clip(1 - r ** 2, 0, 1)) + 0.05
    nuc = np.exp(-(((xx + 0.12) ** 2 + (yy + 0.06) ** 2) / 0.12) ** 2) * 0.55
    nrim = np.exp(-((np.sqrt((xx + 0.12) ** 2 + (yy + 0.06) ** 2) - 0.34) / 0.03) ** 2) * 0.5
    org = np.zeros_like(r)
    for _ in range(9):
        a = rng.rand() * 6.28; rr = 0.45 + rng.rand() * 0.35
        org += np.exp(-(((xx - math.cos(a) * rr) ** 2 + (yy - math.sin(a) * rr) ** 2) / 0.003)) * 0.5
    spec = np.exp(-(((xx + 0.45) / 0.26) ** 2 + ((yy + 0.55) / 0.12) ** 2)) * 0.45
    return np.clip((rim + body + nuc + nrim + org + spec) * inside, 0, 1.5)

def to_pil(a, gmax):
    return Image.fromarray((np.clip(a / gmax, 0, 1) * 255).astype(np.uint8))

def blurpad(im, rad):
    pad = int(rad * 3) + 2
    return ImageOps.expand(im, border=pad, fill=0).filter(ImageFilter.GaussianBlur(rad))

def build_sprites():
    S = {"rod": [], "cocc": [], "cell": []}
    rod = rod_sprite()
    ang_n = 24
    for lvl, rad in enumerate((0, 3, 8)):
        row = []
        for k in range(ang_n):
            im = to_pil(rod, 1.4).rotate(k * 180.0 / ang_n, expand=True, resample=Image.BILINEAR)
            if rad: im = blurpad(im, rad)
            row.append(im)
        S["rod"].append(row)
        im = to_pil(sphere_sprite(), 1.4)
        S["cocc"].append(blurpad(im, rad) if rad else im)
        im = to_pil(cell_sprite(), 1.5)
        S["cell"].append(blurpad(im, rad * 1.6) if rad else im)
    return S

def build_world():
    r = np.random.RandomState(21)
    nr, nc, nk, nd = 280, 120, 48, 700
    Wd = dict(
        rx=r.uniform(-1100, 1100, nr), ry=r.uniform(-1700, 1700, nr), rz=r.uniform(0, 2600, nr), ra=r.rand(nr) * 3.14,
        rs=0.7 + r.rand(nr) * 0.8, rsp=0.7 + r.rand(nr) * 1.6, rph=r.rand(nr) * 6.28,
        cx=r.uniform(-1100, 1100, nc), cy=r.uniform(-1700, 1700, nc), cz=r.uniform(0, 2600, nc), cs=0.5 + r.rand(nc) * 0.7,
        kx=r.uniform(-900, 900, nk), ky=r.uniform(-1500, 1500, nk), kz=r.uniform(0, 2600, nk), ks=0.8 + r.rand(nk) * 0.7, kph=r.rand(nk) * 6.28,
        dx=r.uniform(-1200, 1200, nd), dy=r.uniform(-1900, 1900, nd), dz=r.uniform(0, 2600, nd), dr=0.6 + r.rand(nd) * 1.8)
    return Wd

def build_beams():
    yy, xx = np.mgrid[0:H + 500, 0:W + 500].astype(np.float32)
    out = np.zeros((H + 500, W + 500), np.float32)
    ang = math.radians(-24); ca, sa = math.cos(ang), math.sin(ang)
    for off, wd, amp in ((120, 70, 1.0), (380, 110, 0.7), (640, 60, 0.9), (900, 130, 0.5), (1150, 80, 0.8)):
        u = (xx * ca + yy * sa) - off
        out += amp * np.exp(-(u / wd) ** 2) * np.clip(1 - (yy / (H + 500)) * 0.4, 0, 1)
    return out

_D = {}
def data():
    if not _D:
        _D["body"] = build_body(); _D["spr"] = build_sprites(); _D["world"] = build_world(); _D["beams"] = build_beams()
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H * 0.47) / (H * 0.65)) ** 2)
        g = np.clip(1 - r, 0, 1) ** 1.6
        c0 = np.array([4, 6, 14], np.float32) / 255; c1 = np.array([14, 24, 50], np.float32) / 255
        _D["bg"] = c0 + (c1 - c0) * g[..., None]
        _D["vig"] = np.clip(1.0 - 0.55 * np.clip(r - 0.35, 0, 1.2) ** 1.7, 0, 1)[..., None]
    return _D

# ------------------------------------------------------------------ camera for the body scene
def body_cam(t):
    """returns camD, camx, camy, theta, roll"""
    th = 0.30 * math.sin(0.55 * t)
    if t < 5.18:
        return F_BODY - 120 * sm(t / 5.18), 0.0, 0.0, th, 0.0
    if t < 7.9:
        u = (t - 5.18) / 2.72
        return 1280 - 1600 * u ** 1.8, -0 * u, -140 * sm(u), th * (1 - sm(u)) + 0.9 * u, 0.25 * sm(u)
    if t < 17.45:
        return -320.0, 0.0, -140.0, 0.0, 0.0
    if t < 19.95:
        u = (t - 17.45) / 2.5
        e = 1 - (1 - u) ** 2.2
        return -320 + 1720 * e, 0.0, -140 * (1 - sm(u)), (0.9 * (1 - u)) * (1 - sm(u)) + th * sm(u), 0.25 * (1 - sm(u))
    u = (t - 19.95) / 4.95
    return F_BODY - 60 * math.sin(math.pi * u), 0.0, 0.0, th, 0.0

def project_body(B, t, tt):
    D, cx, cy, th, roll = body_cam(tt)
    amp = 0.5 + 0.5 * key(t, [(0, 0.4), (5.0, 1.0), (7.0, 6.0), (17.4, 6.0), (19.9, 1.0), (24.9, 0.4)])
    X = B["X"] + amp * np.sin(t * B["fx"] + B["ph"]); Y = B["Y"] + amp * np.cos(t * B["fy"] + B["ph"] * 1.3)
    Z = B["Z"]
    c, s = math.cos(th), math.sin(th)
    xr = X * c + Z * s; zr = -X * s + Z * c
    d = D - zr
    f = F_BODY / np.maximum(d, 1e-3)
    sx = (xr - cx) * f; sy = (Y - cy) * f
    if abs(roll) > 1e-4:
        cr, sr = math.cos(roll), math.sin(roll)
        sx, sy = sx * cr - sy * sr, sx * sr + sy * cr
    return sx + W / 2, sy + 960.0, d, f

def draw_body(t, dc, a):
    B = data()["body"]
    sx, sy, d, f = project_body(B, t, t)
    pxs, pys, pd, pf = project_body(B, t, t - 1 / 40.0)
    tr = 3.79 + 0.50 * (1 - B["yn"]) + 0.06 * B["jit"]
    rec_f = 18.9 + 0.7 * B["jit"]
    after = (t >= tr) & (t < rec_f)
    since = np.where(after, t - tr, -1.0)
    pop = np.where(after, 1 + 1.1 * np.exp(-since / 0.14), 1.0)
    rad = B["r"] * np.minimum(f, 14.0) ** 0.9 * pop * (1 + 0.14 * np.sin(t * 3 + B["ph"]))
    vis = (sx > -80) & (sx < W + 80) & (sy > -80) & (sy < H + 80) & (d > 25) & (f < 70)
    streak = abs(body_cam(t)[0] - body_cam(t - 1 / 40.0)[0]) > 4
    near = np.clip(d / 220.0, 0.15, 1.0)
    for i in np.nonzero(vis)[0]:
        if not after[i]: nm = "cream"
        else: nm = "teal" if B["teal"][i] else "gold"
        r = float(rad[i]); x0, y0 = float(sx[i]), float(sy[i])
        k = a * float(B["br"][i]) * float(near[i]) * (0.82 if nm == "teal" else 1.0)
        if nm == "gold": r *= 1.3
        col = tuple(min(255, int(c * k * 1.05)) for c in COL[nm])
        if streak and pd[i] > 25:
            ddx, ddy = x0 - float(pxs[i]), y0 - float(pys[i])
            if ddx * ddx + ddy * ddy > 9:
                dc.line([(float(pxs[i]), float(pys[i])), (x0, y0)], fill=col, width=max(1, int(r * 1.3)))
                continue
        dc.ellipse([x0 - r, y0 - r, x0 + r, y0 + r], fill=col)

# ------------------------------------------------------------------ micro world (sprites)
def add_sprite(acc, img, cx, cy, sc, color, gain):
    w = int(img.width * sc); h = int(img.height * sc)
    if w < 2 or h < 2 or w > 1500 or h > 1500: return
    x0 = int(cx - w / 2); y0 = int(cy - h / 2)
    if x0 >= W or y0 >= H or x0 + w <= 0 or y0 + h <= 0: return
    arr = np.asarray(img.resize((w, h), Image.BILINEAR), np.float32) * (gain / 255.0)
    sx0, sy0 = max(0, -x0), max(0, -y0); ex, ey = min(w, W - x0), min(h, H - y0)
    acc[y0 + sy0:y0 + ey, x0 + sx0:x0 + ex] += arr[sy0:ey, sx0:ex, None] * color

def draw_world(t, acc, dc, a):
    D = data(); S = D["spr"]; Wd = D["world"]
    ZR = 2600.0; Fz = 1000.0
    camZ = 320.0 * (t - 7.0); camx = 130 * math.sin(0.5 * t); camy = 90 * math.sin(0.37 * t) + 40 * (t - 7.0) * 0
    dfoc = 900 + 150 * math.sin(0.6 * t)
    gold_gain = 1.0 + 0.7 * sm((t - 8.0) / 0.3) * (1 - sm((t - 10.25) / 0.3))
    teal_gain = 1.0 + 0.7 * sm((t - 10.3) / 0.3) * (1 - sm((t - 12.4) / 0.3)) + 0.5 * math.exp(-max(0, t - 12.66) / 0.25) * (t > 12.66)
    items = []
    for i in range(len(Wd["cx"])):
        d = ((Wd["cz"][i] - camZ) % ZR) + 60; items.append((d, "c", i))
    for i in range(len(Wd["kx"])):
        d = ((Wd["kz"][i] - camZ) % ZR) + 60; items.append((d, "k", i))
    for i in range(len(Wd["rx"])):
        d = ((Wd["rz"][i] - camZ) % ZR) + 60; items.append((d, "r", i))
    items.sort(key=lambda it: -it[0])
    for d, kind, i in items:
        s = Fz / d
        if kind == "r":
            x, y = Wd["rx"][i], Wd["ry"][i]
        elif kind == "k":
            x, y = Wd["kx"][i], Wd["ky"][i]
        else:
            x, y = Wd["cx"][i], Wd["cy"][i]
        sx = W / 2 + (x - camx) * s; sy = 960 + (y - camy) * s
        near = sm((d - 70) / 240.0); far = 1 - sm((d - 2150) / 400.0); fog = math.exp(-d / 1500.0)
        al = near * far * (0.35 + 0.65 * fog) * a
        if al < 0.02: continue
        blur = abs(d - dfoc); lvl = 0 if blur < 350 else (1 if blur < 800 else 2)
        if lvl: al *= 0.9 if lvl == 1 else 0.75
        if kind == "r":
            ang = Wd["ra"][i] + 0.35 * math.sin(t * Wd["rsp"][i] + Wd["rph"][i])
            k = int(((ang % math.pi) / math.pi) * 24) % 24
            sc = s * Wd["rs"][i] * 0.95
            add_sprite(acc, S["rod"][lvl][k], sx, sy, sc, TF, al * 1.25 * teal_gain)
        elif kind == "k":
            add_sprite(acc, S["cocc"][lvl], sx, sy, s * Wd["ks"][i] * 0.75, TF, al * 1.0 * teal_gain)
        else:
            pul = 1 + 0.04 * math.sin(t * 1.3 + i)
            add_sprite(acc, S["cell"][lvl], sx, sy, s * Wd["cs"][i] * 2.4 * pul, GF, al * 0.78 * gold_gain)
    # motes
    for i in range(0, len(Wd["dx"])):
        d = ((Wd["dz"][i] - camZ) % ZR) + 60; s = Fz / d
        sx = W / 2 + (Wd["dx"][i] - camx) * s; sy = 960 + (Wd["dy"][i] - camy) * s
        if 0 <= sx < W and 0 <= sy < H:
            r = max(0.8, Wd["dr"][i] * s * 1.4); al = a * near_f(d) * 0.55
            dc.ellipse([sx - r, sy - r, sx + r, sy + r], fill=tuple(int(c * al) for c in CREAM))
    # light shafts
    bm = D["beams"]; ox = int(120 + 70 * math.sin(t * 0.3)); oy = int(60 + 40 * math.sin(t * 0.21))
    shaft = bm[oy:oy + H, ox:ox + W] * (0.5 + 0.5 * math.sin(t * 0.8 + 1.0) * 0.4 + 0.3)
    acc += shaft[..., None] * (np.array([0.10, 0.34, 0.38], np.float32) * 0.30 * a)

def near_f(d): return sm((d - 70) / 240.0) * (1 - sm((d - 2150) / 400.0))

# ------------------------------------------------------------------ text helpers
_TX = {}
def font(path, size): return ImageFont.truetype(path, size)

def text_mask(lines, size, path=FONT_B, spacing=1.14):
    kx = (tuple(lines), size, path)
    if kx in _TX: return _TX[kx]
    f = font(path, size); lh = int(size * spacing)
    m = Image.new("L", (W, lh * len(lines) + 30), 0); dd = ImageDraw.Draw(m)
    for i, ln in enumerate(lines):
        w = dd.textlength(ln, font=f); dd.text(((W - w) / 2, 6 + i * lh), ln, font=f, fill=255)
    if len(_TX) > 500: _TX.clear()
    _TX[kx] = m
    return m

def put_text(ov, lines, size, y, color, alpha=1.0, path=FONT_B, scale=1.0, glow=True, dx=0, dy=0):
    if alpha <= 0.01: return
    m = text_mask(lines, size, path)
    if abs(scale - 1) > 0.005:
        m = m.resize((int(W * scale), int(m.height * scale)), Image.BICUBIC)
        cv = Image.new("L", (W, m.height), 0); cv.paste(m, ((W - m.width) // 2, 0)); m = cv
    a = m.point(lambda v: int(v * alpha))
    if glow:
        sh = a.filter(ImageFilter.GaussianBlur(14)).point(lambda v: min(255, int(v * 1.6)))
        ov.paste(Image.new("RGBA", m.size, (3, 5, 12, 255)), (dx, int(y) + dy), sh.point(lambda v: int(v * 0.8)))
    ov.paste(Image.new("RGBA", m.size, color + (255,)), (dx, int(y) + dy), a)

def typed(lines, n):
    out, left = [], n
    for ln in lines:
        out.append(ln[:max(0, left)]); left -= len(ln)
    return out

# ------------------------------------------------------------------ bars scene
def bars_layer(t, a):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    t0 = 14.15; gx = {"n": 290, "w": 800}; base = 1270; hmax = 520
    ease = sm((t - t0) / 1.3)
    f = font(FONT_B, 50); fs = font(FONT_S, 34); fsm = font(FONT_M, 30)
    def ca(c, al=1.0): return c + (int(255 * a * al),)
    d.text((gx["n"], 560), "HOW MANY", font=f, fill=ca(CREAM), anchor="mm")
    d.text((gx["w"], 560), "HOW HEAVY", font=f, fill=ca(CREAM), anchor="mm")
    items = [("n", -80, 38, 38, TEAL), ("n", 80, 30, 38, GOLD), ("w", -80, 70, 70, GOLD), ("w", 80, 0.2, 70, TEAL)]
    for g, off, v, mx, col in items:
        x = gx[g] + off; h = max(hmax * v / mx * ease, 0)
        if v == 0.2: h = max(h, 8 * ease)
        for k in range(int(h)):
            u = k / max(1, h); sh = 0.78 + 0.22 * u
            d.line([(x - 60, base - k), (x + 60, base - k)], fill=tuple(int(c * sh) for c in col) + (int(255 * a),), width=1)
        if ease > 0.05:
            vv = v * ease; txt = (f"{vv:.0f}T" if g == "n" else ("%.0f kg" % vv if v == 70 else ""))
            if txt: d.text((x, base - h - 38), txt, font=fs, fill=ca(col), anchor="mm")
    for g in ("n", "w"): d.line([(gx[g] - 160, base + 6), (gx[g] + 160, base + 6)], fill=ca(CREAM, 0.6), width=4)
    d.text((gx["n"] - 80, base + 46), "bacteria", font=fsm, fill=ca(TEAL), anchor="mm"); d.text((gx["n"] + 80, base + 46), "you", font=fsm, fill=ca(GOLD), anchor="mm")
    d.text((gx["w"] - 80, base + 46), "you", font=fsm, fill=ca(GOLD), anchor="mm"); d.text((gx["w"] + 80, base + 46), "bacteria", font=fsm, fill=ca(TEAL), anchor="mm")
    ap = sm((t - 16.35) / 0.6)
    if ap > 0.02:
        cx, cy = gx["w"] + 80, base - 330; al = int(255 * ap * a)
        d.line([(cx, base - 24), (cx, cy + 84)], fill=TEAL + (al,), width=5)
        d.ellipse([cx - 74, cy - 62, cx + 74, cy + 78], outline=CREAM + (al,), width=10)
        d.line([(cx, cy - 58), (cx + 10, cy - 102)], fill=CREAM + (al,), width=9)
        d.ellipse([cx + 10, cy - 114, cx + 62, cy - 84], fill=GOLD + (al,))
        d.text((cx, cy + 128), "0.2 kg", font=fs, fill=TEAL + (al,), anchor="mm")
        d.text((cx, cy + 168), "≈ an apple", font=fsm, fill=CREAM + (al,), anchor="mm")
    d.text((W / 2, 1540), "By cell count, 70 kg adult · Sender, Fuchs & Milo, PLoS Biology 2016", font=font(FONT_M, 26), fill=CREAM + (int(150 * a),), anchor="mm")
    return ov

# ------------------------------------------------------------------ frame
def glow_np(img, blur, scale=4):
    s = img.resize((W // scale, H // scale), Image.BILINEAR).filter(ImageFilter.GaussianBlur(blur))
    return np.asarray(s.resize((W, H), Image.BILINEAR), np.float32) / 255

def hit_fx(t):
    ca = fl = sh = 0.0; sx = sy = 0.0
    for h in HITS:
        if t >= h - 0.02:
            e = math.exp(-(t - h) / 0.16); ca += 8.0 * e; fl += 0.16 * math.exp(-((t - h) / 0.07) ** 2); sh += 14.0 * e
            sx += 14.0 * e * math.sin(t * 91); sy += 11.0 * e * math.cos(t * 77)
    return ca, fl, int(sx), int(sy)

def render(t):
    D = data()
    acc = D["bg"].copy()
    a_body = 1.0 if t < 7.2 else (1 - sm((t - 7.2) / 0.55) if t < 7.9 else 0.0)
    if t >= 17.4: a_body = 1.0
    a_world = sm((t - 7.15) / 0.7) * (1 - sm((t - 13.95) / 0.45)) if 7.1 < t < 14.4 else 0.0
    a_bars = sm((t - 14.0) / 0.4) * (1 - sm((t - 17.2) / 0.3)) if 13.9 < t < 17.6 else 0.0
    C = Image.new("RGB", (W, H), (0, 0, 0)); dc = ImageDraw.Draw(C)
    if a_body > 0.01 and not (7.9 <= t < 17.4): draw_body(t, dc, a_body)
    if a_world > 0.01: draw_world(t, acc, dc, a_world)
    sharp = np.asarray(C, np.float32) / 255
    if a_world > 0.01:
        yy = np.arange(H, dtype=np.float32)[:, None, None]
        g = 0.40 + 0.60 * np.clip((yy - 60) / 560.0, 0, 1) ** 1.2
        acc = acc * (1 - a_world * (1 - g))
    acc += sharp * 0.95 + glow_np(C, 4) * 0.55
    # bars
    if a_bars > 0.01:
        ov = bars_layer(t, a_bars); arr = np.asarray(ov, np.float32) / 255
        acc = acc * (1 - arr[..., 3:4]) + arr[..., :3] * arr[..., 3:4]
        acc += glow_np(ov.convert("RGB"), 6) * 0.45
    # post: bloom, chromatic hit, flash, shake, vignette, grain
    bright = np.clip(acc - 0.62, 0, 1)
    bl = np.asarray(Image.fromarray((np.clip(bright, 0, 1) * 255).astype(np.uint8)).resize((W // 8, H // 8), Image.BILINEAR).filter(ImageFilter.GaussianBlur(5)).resize((W, H), Image.BILINEAR), np.float32) / 255
    acc = acc + bl * 0.55
    ca, fl, sx, sy = hit_fx(t)
    if ca > 0.4:
        k = int(round(ca))
        acc[..., 0] = np.roll(acc[..., 0], k, axis=1); acc[..., 2] = np.roll(acc[..., 2], -k, axis=1)
    acc = acc + fl
    if sx or sy: acc = np.roll(acc, (sy, sx), axis=(0, 1))
    acc = acc * D["vig"]
    base = Image.fromarray((np.clip(acc, 0, 1) * 255).astype(np.uint8)).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # ---- text (locked to the voice)
    q1, q2 = "HOW MUCH OF YOU", "IS ACTUALLY YOU?"
    if t < 3.8:
        n1 = int(max(0, t - 0.05) * 11.5); n2 = int(max(0, t - 1.8) * 11.5)
        lines = [q1[:n1], q2[:n2]] if t >= 1.8 else [q1[:n1], ""]
        put_text(ov, lines, 82, 270, CREAM, 1 - sm((t - 3.55) / 0.2), dx=sx // 2, dy=sy // 2)
    if 3.79 <= t < 5.3:
        sc = 1.0 + 0.5 * math.exp(-(t - 3.8) / 0.09)
        put_text(ov, ["LESS THAN", "HALF."], 128, 140, GOLD, sm((t - 3.79) / 0.05) * (1 - sm((t - 4.95) / 0.3)), scale=min(1.35, sc), dx=sx // 2, dy=sy // 2)
    if 5.18 <= t < 8.0:
        h2 = ["SO WHO ELSE", "IS IN THERE?"]
        put_text(ov, typed(h2, int((t - 5.18) * 9.5)), 94, 230, CREAM, sm((t - 5.18) / 0.1) * (1 - sm((t - 7.55) / 0.35)))
    if 8.0 < t < 14.0:
        d = ImageDraw.Draw(ov); fa = 1 - sm((t - 13.8) / 0.25)
        eg = sm((t - 8.08) / 2.0); et = sm((t - 10.35) / 1.95)
        ga = sm((t - 8.0) / 0.2) * fa; ta = sm((t - 10.3) / 0.2) * fa
        pulse = 1 + 0.10 * math.exp(-max(0, t - 12.66) / 0.18) * (t > 12.66)
        if ga > 0.01:
            d.text((300, 250), f"{30 * eg:.1f}T", font=font(FONT_B, 104), fill=GOLD + (int(255 * ga),), anchor="mm")
            d.text((300, 330), "HUMAN CELLS", font=font(FONT_S, 36), fill=GOLD + (int(255 * ga),), anchor="mm")
        if ta > 0.01:
            d.text((780, 250), f"{38 * et:.1f}T", font=font(FONT_B, int(104 * pulse)), fill=TEAL + (int(255 * ta),), anchor="mm")
            d.text((780, 330), "BACTERIA", font=font(FONT_S, 36), fill=TEAL + (int(255 * ta),), anchor="mm")
    if 12.66 <= t < 14.0:
        put_text(ov, ["THEY OUTNUMBER YOU."], 80, 1330, CREAM, sm((t - 12.66) / 0.08) * (1 - sm((t - 13.7) / 0.25)), scale=min(1.15, 1 + 0.2 * math.exp(-(t - 12.7) / 0.1)), dx=sx // 2, dy=sy // 2)
    if 14.15 <= t < 17.5:
        put_text(ov, ["...BUT TOGETHER THEY WEIGH", "ABOUT AS MUCH AS AN APPLE."], 60, 250, CREAM, sm((t - 14.2) / 0.3) * (1 - sm((t - 17.1) / 0.3)))
    if 17.7 <= t < 20.1:
        put_text(ov, ["YOU HAVE NEVER", "BEEN ALONE."], 116, 150, CREAM, sm((t - 17.7) / 0.06) * (1 - sm((t - 19.8) / 0.3)), scale=min(1.25, 1 + 0.4 * math.exp(-(t - 17.75) / 0.1)), dx=sx // 2, dy=sy // 2)
    if t >= 20.2:
        l1, l2 = "NEXT: THE OLDEST THING IN YOU", "IS OLDER THAN THE SUN."
        n = int((t - 20.2) * 12.5)
        put_text(ov, [l1[:n], l2[:max(0, n - len(l1))]], 60, 1470, GOLD, sm((t - 20.2) / 0.3))
        put_text(ov, ["FOLLOW"], 42, 1650, CREAM, 0.75 * sm((t - 22.6) / 0.4), path=FONT_S, glow=False)
    out = Image.alpha_composite(base, ov).convert("RGB")
    arr = np.asarray(out, np.float32) / 255
    rng = np.random.RandomState(int(t * 24) % 6)
    arr = arr + (rng.randn(H // 2, W // 2).astype(np.float32).repeat(2, 0).repeat(2, 1) * 0.011)[..., None]
    return (np.clip(arr, 0, 1) * 255).astype(np.uint8)

def render_bytes(i): return render(i / FPS).tobytes()

def main():
    mode = sys.argv[1]
    if mode == "sheet":
        out = sys.argv[2]; ts = [float(x) for x in sys.argv[3:]]
        with Pool(4) as p: fr = p.map(render, ts)
        cols = 4; rows = math.ceil(len(fr) / cols); sw, sh = 270, 480
        sheet = Image.new("RGB", (cols * sw, rows * sh))
        for k, f in enumerate(fr): sheet.paste(Image.fromarray(f).resize((sw, sh), Image.LANCZOS), ((k % cols) * sw, (k // cols) * sh))
        sheet.save(out)
    elif mode == "frame":
        Image.fromarray(render(float(sys.argv[3]))).save(sys.argv[2])
    elif mode == "video":
        out = sys.argv[2]; audio = sys.argv[3] if len(sys.argv) > 3 else None
        cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"]
        cmd += (["-i", audio] if audio else ["-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo"])
        cmd += ["-t", f"{DUR}", "-c:v", "libx264", "-crf", "21", "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", out]
        pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        with Pool(4) as p:
            for k, b in enumerate(p.imap(render_bytes, range(N), chunksize=3)):
                pr.stdin.write(b)
                if k % 90 == 0: print("frame", k, "/", N, flush=True)
        pr.stdin.close(); pr.wait()

if __name__ == "__main__":
    main()
