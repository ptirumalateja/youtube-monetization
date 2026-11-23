#!/usr/bin/env python3
"""How Much of You Is Actually You? v3.
Opening (and the loop-back ending): an orbiting camera around a faceless, ink-hatched white figure on a hill with a monolith, beside a
glitch-particle double (the "not-you"); sky and grass shift green -> crimson on "less than half" while his skin dissolves, word by
word, into glitch pixels (56% of them). Then the camera dives into the body into a microbial world with true shapes
(bacilli, flagellated rods, cocci, chains, staph clusters, spirals, vibrio; red cells, white cells, epithelial cells) and hundreds of
thousands of specks. Voice-locked to vo_proc.wav timings (same as v2).

usage: render_v3.py sheet OUT.png t1 t2 ... | frame OUT.png t | video OUT.mp4 audio.wav
"""
import math, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps
from multiprocessing import Pool
import render3d as R3
from render3d import sm, key, W, H, FPS, DUR, N, put_text, typed, bars_layer, glow_np, hit_fx, COL, CREAM, GOLD, TEAL, FONT_B, FONT_S, FONT_M, font

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
FO = 1400.0
GS = 2048; GW = 5000.0
FZ = 1000.0

# =====================================================================  SHARED BODY DATA
def body_mask():
    CWD, CHT = 540, 1000
    m = Image.new("L", (CWD, CHT), 0); d = ImageDraw.Draw(m)
    def cap(p0, r0, p1, r1, n=28):
        for k in range(n + 1):
            u = k / n; x = p0[0] + (p1[0] - p0[0]) * u; y = p0[1] + (p1[1] - p0[1]) * u; r = r0 + (r1 - r0) * u
            d.ellipse([x - r, y - r, x + r, y + r], fill=255)
    cap((270, 92), 66, (270, 114), 66); cap((270, 168), 23, (270, 218), 32)
    cap((270, 250), 88, (270, 330), 92); cap((270, 330), 92, (270, 450), 74); cap((270, 450), 74, (270, 540), 80)
    cap((205, 262), 40, (335, 262), 40)
    for sd in (-1, 1):
        cx = 270
        cap((cx + sd * 92, 262), 38, (cx + sd * 122, 400), 31); cap((cx + sd * 122, 400), 31, (cx + sd * 142, 530), 25); cap((cx + sd * 142, 530), 25, (cx + sd * 152, 600), 26)
        cap((cx + sd * 48, 560), 64, (cx + sd * 56, 770), 46); cap((cx + sd * 56, 770), 46, (cx + sd * 62, 945), 30); cap((cx + sd * 62, 945), 30, (cx + sd * 70, 985), 32)
    return m

def build_solid(n=120000):
    rng = np.random.RandomState(3)
    m = body_mask(); a = np.asarray(m) > 128
    blur = np.asarray(m.filter(ImageFilter.GaussianBlur(20)), np.float32) / 255
    zh = 72 * np.sqrt(np.clip((blur - 0.12) / 0.88, 0, 1)); gy, gx = np.gradient(zh)
    ys, xs = np.nonzero(a); idx = rng.choice(len(xs), n, replace=False)
    x = xs[idx].astype(np.float32); y = ys[idx].astype(np.float32); zp = zh[ys[idx], xs[idx]]
    sgn = np.where(rng.rand(n) < 0.6, 1.0, -1.0)
    shell = rng.rand(n) < 0.5
    zz = np.where(shell, sgn * zp, (rng.rand(n) * 2 - 1) * zp)
    sgn = np.where(zz >= 0, 1.0, -1.0)
    X = (x - 270) * 0.9; Y = 436 - (y - 500) * 0.9; Z = zz * 0.9
    nx, ny, nz = -gx[ys[idx], xs[idx]], gy[ys[idx], xs[idx]], sgn
    nn = np.sqrt(nx ** 2 + ny ** 2 + 1); nx, ny, nz = nx / nn, ny / nn, nz / nn
    return dict(P=np.stack([X, Y, Z], 1).astype(np.float32), Nm=np.stack([nx, ny, nz], 1).astype(np.float32), rank=rng.rand(n).astype(np.float32),
                cls=rng.choice([1, 2, 3], n, p=[0.55, 0.22, 0.23]), rv=rng.rand(n).astype(np.float32))

# =====================================================================  HILL / GROUND SCENE
def build_ground():
    rng = np.random.RandomState(11)
    def noise(res, seed):
        r = (np.random.RandomState(seed).rand(res, res) * 255).astype(np.uint8)
        return np.asarray(Image.fromarray(r).resize((GS, GS), Image.BICUBIC), np.float32) / 255
    m = (0.6 * noise(48, 1) + 0.4 * noise(180, 2))[..., None]
    c0 = np.array([20, 42, 13], np.float32); c1 = np.array([66, 94, 27], np.float32)
    img = Image.fromarray(np.clip(c0 + (c1 - c0) * m, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(img)
    pal = [(8, 20, 6), (52, 82, 22), (132, 162, 62)]; pw = [0.55, 0.32, 0.13]
    for k in range(65000):
        x = rng.rand() * GS; y = rng.rand() * GS; a = -math.pi / 2 + rng.randn() * 0.55; L = 8 + rng.rand() * 18
        c = pal[rng.choice(3, p=pw)]
        d.line([(x, y), (x + math.cos(a) * L, y + math.sin(a) * L)], fill=c, width=1 + int(rng.rand() < 0.25))
    def tx(X, Z): return ((X + GW / 2) / GW * GS, (Z + GW / 2) / GW * GS)
    sc = GS / GW
    # soft shadows under the two figures
    sh = Image.new("L", (GS, GS), 0); sd_ = ImageDraw.Draw(sh)
    for (cx, cz, rx, rz) in ((0, 20, 130, 60), (230, -100, 130, 60)):
        x, z = tx(cx, cz); sd_.ellipse([x - rx * sc, z - rz * sc, x + rx * sc, z + rz * sc], fill=150)
    sh = sh.filter(ImageFilter.GaussianBlur(14))
    arr = np.asarray(img, np.float32) * (1 - np.asarray(sh, np.float32)[..., None] / 255 * 0.75)
    img = Image.fromarray(arr.astype(np.uint8)); d = ImageDraw.Draw(img)
    # open pit with a torn paper flap (rotated rectangles)
    def rot(poly, cx, cz, ang):
        c, s = math.cos(ang), math.sin(ang)
        return [tx(cx + p[0] * c - p[1] * s, cz + p[0] * s + p[1] * c) for p in poly]
    flap = rot([(-300, -90), (260, -110), (300, 70), (-260, 100)], -250, 150, 0.35)
    d.polygon(flap, fill=(132, 148, 108), outline=(46, 52, 36))
    for k in range(34):
        a = rng.rand(); b = rng.rand(); p0 = flap[0]; p1 = flap[1]; p2 = flap[3]
        x = p0[0] + (p1[0] - p0[0]) * a + (p2[0] - p0[0]) * b; y = p0[1] + (p1[1] - p0[1]) * a + (p2[1] - p0[1]) * b
        d.line([(x, y), (x + rng.randn() * 9, y + rng.randn() * 9)], fill=(60, 70, 48), width=1)
    pit = rot([(-190, -45), (190, -45), (190, 45), (-190, 45)], -250, 150, 0.35)
    d.polygon(pit, fill=(4, 5, 5), outline=(150, 160, 130))
    # flowers
    for k in range(40):
        fx = rng.uniform(-1500, 1500); fz = rng.uniform(-900, 1300)
        if abs(fx + 250) < 330 and abs(fz - 150) < 190: continue
        x, z = tx(fx, fz); r = (28 + rng.rand() * 26) * sc * 1.9
        for q in range(5):
            a = q * 2 * math.pi / 5 + rng.rand() * 0.2
            d.ellipse([x + math.cos(a) * r * 0.55 - r * 0.42, z + math.sin(a) * r * 0.55 - r * 0.42, x + math.cos(a) * r * 0.55 + r * 0.42, z + math.sin(a) * r * 0.55 + r * 0.42],
                      fill=(236, 236, 232), outline=(30, 30, 24))
        d.ellipse([x - r * 0.2, z - r * 0.2, x + r * 0.2, z + r * 0.2], fill=(40, 28, 12))
    t0 = np.asarray(img, np.float32) / 255
    tb = np.asarray(img.filter(ImageFilter.GaussianBlur(3)), np.float32) / 255
    return t0, tb

_G = {}
def gdata():
    if not _G:
        _G["tex"], _G["texb"] = build_ground()
        _G["solid"] = build_solid()
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        _G["h1"] = ((xx + yy * 0.9) % 7.0) < 1.5
        _G["h2"] = ((xx * 0.9 - yy) % 9.0) < 1.3
        hh, ww = H // 2, W // 2
        gy, gx = np.mgrid[0:hh, 0:ww].astype(np.float32)
        _G["px"] = (gx * 2 - W / 2) / FO; _G["py"] = (gy * 2 - H / 2) / FO
        rng = np.random.RandomState(9)
        _G["clone"] = rng.choice(len(_G["solid"]["P"]), 22000, replace=False)
    return _G

def lookat(C, T):
    f = T - C; f = f / np.linalg.norm(f); r = np.cross(f, [0.0, 1.0, 0.0]); r = r / np.linalg.norm(r); u = np.cross(r, f)
    return r, u, f

def hill_state(t):
    """camera angle, height, distance, omen shift s, conversion p, clone alpha"""
    if t < 5.1:
        u = sm(t / 5.0)
        th = -1.1 * (1 - u); Hc = 380 + 520 * (1 - u); D = 1000.0
        s = sm((t - 3.7) / 1.2)
        pw = key(t, [(3.79, 0.0), (4.03, 0.34), (4.37, 0.66), (4.82, 1.0)])
        clone = 1.0 - sm((t - 3.85) / 0.95)
        return th, Hc, D, s, pw, clone
    u = sm((t - 19.6) / 5.3) if t > 19.6 else 0.0
    th = -1.1 * u; Hc = 380 + 520 * u; D = 1400 - 400 * u
    s = 1 - sm((t - 20.0) / 4.4)
    pw = 1 - sm((t - 21.2) / 2.7)
    clone = sm((t - 23.2) / 1.6)
    return th, Hc, D, s, pw, clone

def sample_bilinear(tex, X, Z):
    u = ((X + GW / 2) / GW * GS) % GS; v = ((Z + GW / 2) / GW * GS) % GS
    iu = u.astype(np.int32); iv = v.astype(np.int32); fu = (u - iu)[..., None]; fv = (v - iv)[..., None]
    iu1 = (iu + 1) % GS; iv1 = (iv + 1) % GS
    return (tex[iv, iu] * (1 - fu) * (1 - fv) + tex[iv, iu1] * fu * (1 - fv) + tex[iv1, iu] * (1 - fu) * fv + tex[iv1, iu1] * fu * fv)

PAL_CALM = dict(top=np.array([0.50, 0.83, 0.68], np.float32), hor=np.array([0.74, 0.93, 0.80], np.float32), hill=np.array([0.10, 0.22, 0.07], np.float32))
PAL_OMEN = dict(top=np.array([0.90, 0.40, 0.46], np.float32), hor=np.array([0.98, 0.66, 0.62], np.float32), hill=np.array([0.30, 0.07, 0.06], np.float32))

def ground_bg(C, r, u, f, s):
    G = gdata(); hh, ww = H // 2, W // 2
    px, py = G["px"], G["py"]
    dx = f[0] + px * r[0] - py * u[0]; dy = f[1] + px * r[1] - py * u[1]; dz = f[2] + px * r[2] - py * u[2]
    below = dy < -1e-3
    tt = np.where(below, -C[1] / np.where(below, dy, -1.0), 1e9).astype(np.float32)
    X = C[0] + tt * dx; Z = C[2] + tt * dz
    far = tt > 5600
    hor_e = dy / np.sqrt(dx * dx + dz * dz + 1e-9)
    az = np.arctan2(dx, dz)
    hill_h = 0.055 + 0.045 * np.sin(2.1 * az + 0.5) + 0.032 * np.sin(5.3 * az + 2.0) + 0.018 * np.sin(11.0 * az)
    sky_t = np.clip(hor_e * 3.0, 0, 1)[..., None]
    top = PAL_CALM["top"] * (1 - s) + PAL_OMEN["top"] * s; hor = PAL_CALM["hor"] * (1 - s) + PAL_OMEN["hor"] * s; hc = PAL_CALM["hill"] * (1 - s) + PAL_OMEN["hill"] * s
    sky = hor + (top - hor) * sky_t
    hill_mask = (hor_e < hill_h) | (far & below)
    hill = hc + (np.array([0.20, 0.36, 0.14], np.float32) * (1 - s) + np.array([0.52, 0.16, 0.12], np.float32) * s - hc) * np.clip((hor_e / np.maximum(hill_h, 1e-3)) * 0.9, 0, 1)[..., None] * 0.9
    out = np.where(hill_mask[..., None], hill, sky)
    gm = below & ~far
    if gm.any():
        Xg = np.where(gm, X, 0); Zg = np.where(gm, Z, 0)
        sharp = sample_bilinear(G["tex"], Xg, Zg); soft = sample_bilinear(G["texb"], Xg, Zg)
        mixk = np.clip((tt - 1200) / 2600, 0, 1)[..., None]
        gcol = sharp * (1 - mixk) + soft * mixk
        red = gcol[..., [1, 0, 2]] * np.array([1.35, 0.62, 0.55], np.float32)
        gcol = gcol * (1 - s) + red * s
        fog = (np.clip(tt / 6200, 0, 1) ** 1.4)[..., None] * 0.55
        gcol = gcol * (1 - fog) + hor * fog
        out = np.where(gm[..., None], gcol, out)
    img = Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
    return np.asarray(img, np.float32) / 255

def project(Pw, C, r, u, f):
    p = Pw - C; xc = p @ r; yc = p @ u; zc = p @ f
    zc = np.maximum(zc, 1.0)
    return W / 2 + FO * xc / zc, H / 2 - FO * yc / zc, zc

def render_solid(t, C, r, u, f, pconv, shade_w, fr_mask=None):
    """solid hatched figure with glitch-pixel skin. returns rgb (H,W,3), mask (H,W)"""
    G = gdata(); S = G["solid"]
    P = S["P"].copy(); Nm = S["Nm"].copy()
    yaw = 0.07 * math.sin(0.8 * t)
    cy_, sy_ = math.cos(yaw), math.sin(yaw)
    P = np.stack([P[:, 0] * cy_ + P[:, 2] * sy_, P[:, 1], -P[:, 0] * sy_ + P[:, 2] * cy_], 1); Nm = np.stack([Nm[:, 0] * cy_ + Nm[:, 2] * sy_, Nm[:, 1], -Nm[:, 0] * sy_ + Nm[:, 2] * cy_], 1)
    P[:, 1] += 3 * math.sin(t * 2.0) * (P[:, 1] > 600)
    sx, sy, zc = project(P, C, r, u, f)
    L = np.array([-0.5, 0.7, 0.55], np.float32); L = L / np.linalg.norm(L)
    lam = np.clip(Nm @ L, 0, 1); view = (C - P); view = view / np.linalg.norm(view, axis=1, keepdims=True)
    facing = np.clip((Nm * view).sum(1), 0, 1)
    shade = np.clip(0.22 + 0.72 * lam + 0.16 * (1 - facing) ** 2 * 0.5, 0, 1)
    colored = S["rank"] < pconv * 0.56
    cls = np.where(colored, S["cls"], 0)
    ix = sx.astype(np.int32); iy = sy.astype(np.int32)
    ok = (ix > 2) & (ix < W - 3) & (iy > 2) & (iy < H - 3)
    order = np.nonzero(ok)[0]; order = order[np.argsort(-zc[order])]
    buf_s = np.zeros((H, W), np.float32); buf_c = np.full((H, W), -1, np.int8); buf_v = np.zeros((H, W), np.float32)
    rad = 2 if FO / np.median(zc[order]) > 1.0 else 1
    offs = [(dy, dx) for dy in range(-rad, rad + 1) for dx in range(-rad, rad + 1)]
    for dy, dx in offs:
        yy = iy[order] + dy; xx = ix[order] + dx
        buf_s[yy, xx] = shade[order]; buf_c[yy, xx] = cls[order]; buf_v[yy, xx] = S["rv"][order]
    mask = buf_c >= 0
    out = np.zeros((H, W, 3), np.float32)
    white = mask & (buf_c == 0)
    Sh = buf_s
    base = np.array([0.97, 0.96, 0.98], np.float32)
    cool = np.array([0.74, 0.77, 0.90], np.float32)
    col = base * (0.40 + 0.60 * Sh[..., None]) * (cool + (1 - cool) * Sh[..., None])
    dark = 1 - Sh
    hatch = (G["h1"] & (dark > 0.36)) | (G["h2"] & (dark > 0.62))
    col = col * (1 - 0.50 * hatch[..., None])
    out = np.where(white[..., None], col, out)
    # glitch pixels (colored skin): blocky, bright, flicker per ~8 fps
    gl = mask & (buf_c > 0)
    if gl.any():
        pal = {1: np.array([0.20, 0.95, 0.82], np.float32), 2: np.array([0.98, 0.28, 0.80], np.float32), 3: np.array([0.55, 0.35, 1.0], np.float32)}
        gcol = np.zeros((H, W, 3), np.float32)
        for k, c in pal.items(): gcol[buf_c == k] = c
        fl = ((buf_v * 7.0 + math.floor(t * 8) * 0.37) % 1.0)[..., None]
        gcol = gcol * (0.72 + 0.6 * fl) * (0.75 + 0.3 * Sh[..., None])
        out = np.where(gl[..., None], gcol, out)
    # chromatic fringe on the right edge (the glitch)
    fr = np.roll(mask, 5, axis=1) & ~mask
    rn = np.random.RandomState(int(t * 8) % 97).rand(H, W).astype(np.float32)
    fcol = np.stack([0.65 + 0.3 * rn, 0.10 + 0.3 * rn, 0.95 - 0.2 * rn], -1)
    out = np.where(fr[..., None], fcol * 0.9, out)
    return out, (mask | fr).astype(np.float32)

def render_clone(t, C, r, u, f, alpha):
    G = gdata(); S = G["solid"]; ci = G["clone"]
    P = S["P"][ci].copy() + np.array([230, 0, -100], np.float32)
    rng = np.random.RandomState(int(t * 10) % 1000)
    P = P + rng.randn(len(ci), 3).astype(np.float32) * 4.0
    sx, sy, zc = project(P, C, r, u, f)
    ix = sx.astype(np.int32); iy = sy.astype(np.int32)
    ok = (ix > 4) & (ix < W - 5) & (iy > 4) & (iy < H - 5) & (rng.rand(len(ci)) < 0.86)
    order = np.nonzero(ok)[0]; order = order[np.argsort(-zc[order])]
    pal = np.array([[0.95, 0.25, 0.85], [0.55, 0.30, 1.0], [0.25, 0.55, 1.0], [0.95, 0.95, 1.0], [0.85, 0.20, 0.95], [0.30, 0.95, 0.85]], np.float32)
    pc = pal[(S["rv"][ci][order] * 6).astype(int) % 6] * (0.6 + 0.6 * rng.rand(len(order), 1).astype(np.float32))
    buf = np.zeros((H, W, 3), np.float32); m = np.zeros((H, W), np.float32)
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            buf[iy[order] + dy, ix[order] + dx] = pc; m[iy[order] + dy, ix[order] + dx] = 1.0
    # digital glitch slices
    for k in range(2):
        if rng.rand() < 0.6:
            y0 = int(rng.uniform(500, 1500)); hgt = int(rng.uniform(20, 90)); sh = int(rng.uniform(-26, 26))
            buf[y0:y0 + hgt] = np.roll(buf[y0:y0 + hgt], sh, axis=1); m[y0:y0 + hgt] = np.roll(m[y0:y0 + hgt], sh, axis=1)
    return buf, m * alpha

def draw_monolith(C, r, u, f):
    cx, cz = -330.0, -90.0; hx, hz, hh = 58.0, 26.0, 310.0; yaw = 0.25
    cs, sn = math.cos(yaw), math.sin(yaw)
    def pt(x, y, z): return np.array([cx + x * cs - z * sn, y, cz + x * sn + z * cs], np.float32)
    V = {(a, b, c): pt(a * hx, b * hh, c * hz) for a in (-1, 1) for b in (0, 1) for c in (-1, 1)}
    faces = [((-1, 0, 1), (1, 0, 1), (1, 1, 1), (-1, 1, 1), (0, 0, 1)), ((1, 0, -1), (-1, 0, -1), (-1, 1, -1), (1, 1, -1), (0, 0, -1)),
             ((-1, 0, -1), (-1, 0, 1), (-1, 1, 1), (-1, 1, -1), (-1, 0, 0)), ((1, 0, 1), (1, 0, -1), (1, 1, -1), (1, 1, 1), (1, 0, 0)),
             ((-1, 1, 1), (1, 1, 1), (1, 1, -1), (-1, 1, -1), (0, 1, 0))]
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    cen = pt(0, hh / 2, 0)
    for fc in faces:
        pts3 = [V[k] for k in fc[:4]]; mid = sum(pts3) / 4
        nrm = np.array([fc[4][0] * cs - fc[4][2] * sn, fc[4][1], fc[4][0] * sn + fc[4][2] * cs], np.float32)
        if nrm @ (C - mid) <= 0: continue
        sx, sy, _ = project(np.array(pts3), C, r, u, f)
        shade = 18 if abs(fc[4][2]) == 1 else (46 if fc[4][1] == 0 else 70)
        d.polygon([(float(a), float(b)) for a, b in zip(sx, sy)], fill=(shade, shade + 2, shade, 255), outline=(150, 156, 142, 255))
        d.line([(float(a), float(b)) for a, b in zip(list(sx) + [sx[0]], list(sy) + [sy[0]])], fill=(158, 164, 150, 255), width=4)
    sx0, sy0, zc0 = project(cen[None], C, r, u, f)
    return np.asarray(img, np.float32) / 255, float(zc0[0])

def hill_scene(t, a_hill):
    th, Hc, D, s, pconv, clone_a = hill_state(t)
    C = np.array([D * math.sin(th), Hc, D * math.cos(th)], np.float32); T = np.array([0.0, 440.0, 0.0], np.float32)
    r, u, f = lookat(C, T)
    img = ground_bg(C, r, u, f, s)
    mono, zm = draw_monolith(C, r, u, f)
    cp = (np.array([0, 436, 0], np.float32) - C) @ f
    def over(base, rgba): return base * (1 - rgba[..., 3:4]) + rgba[..., :3] * rgba[..., 3:4]
    if zm > cp: img = over(img, mono)
    if clone_a > 0.01:
        cb, cm = render_clone(t, C, r, u, f, clone_a)
        img = img * (1 - cm[..., None] * 0.92) + cb * cm[..., None] * 0.92
    fig, fm = render_solid(t, C, r, u, f, pconv, 1.0)
    img = img * (1 - fm[..., None]) + fig * fm[..., None]
    if zm <= cp: img = over(img, mono)
    # eyes (tiny pink dots) when he faces the camera
    head = np.array([0, 806, 62], np.float32); face_dot = float(np.dot(C - head, [0, 0, 1])) / float(np.linalg.norm(C - head))
    if face_dot > 0.4:
        e = np.array([[-24, 806, 64], [24, 806, 64]], np.float32); ex, ey, _ = project(e, C, r, u, f)
        pi = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)); dd = ImageDraw.Draw(pi)
        for a, b in zip(ex, ey): dd.ellipse([a - 5, b - 5, a + 5, b + 5], fill=(214, 44, 130))
        img = np.asarray(pi, np.float32) / 255
    # painterly vignette, heavier in the omen
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    rr = np.sqrt(((xx - W / 2) / (W * 0.72)) ** 2 + ((yy - H * 0.5) / (H * 0.62)) ** 2)
    img = img * np.clip(1.0 - (0.40 + 0.30 * s) * np.clip(rr - 0.3, 0, 1.3) ** 1.6, 0, 1)[..., None]
    img = img * (1.0 - 0.12 * s)
    return img

# =====================================================================  DIVE BODY (particles)
def body_cam3(t):
    D, cx, cy, th, roll = _orig_body_cam(t)
    if t < 5.18: D = 1000.0
    elif t < 7.9:
        u = (t - 5.18) / 2.72; D = 1000.0 - 1320.0 * u ** 1.8
    return D, cx, cy, th, roll
_orig_body_cam = R3.body_cam
R3.body_cam = body_cam3

def draw_body3(t, dc, a):
    B = R3.data()["body"]
    sx, sy, d, f = R3.project_body(B, t, t)
    pxs, pys, pd, pf = R3.project_body(B, t, t - 1 / 40.0)
    rad = B["r"] * np.minimum(f, 14.0) ** 0.9 * (1 + 0.14 * np.sin(t * 3 + B["ph"]))
    vis = (sx > -80) & (sx < W + 80) & (sy > -80) & (sy < H + 80) & (d > 25) & (f < 70)
    streak = abs(R3.body_cam(t)[0] - R3.body_cam(t - 1 / 40.0)[0]) > 4
    near = np.clip(d / 220.0, 0.15, 1.0)
    for i in np.nonzero(vis)[0]:
        nm = "teal" if B["teal"][i] else "gold"
        r = float(rad[i]) * (1.3 if nm == "gold" else 1.0); x0, y0 = float(sx[i]), float(sy[i])
        k = a * float(B["br"][i]) * float(near[i]) * (0.82 if nm == "teal" else 1.0)
        col = tuple(min(255, int(c * k * 1.05)) for c in COL[nm])
        if streak and pd[i] > 25:
            ddx, ddy = x0 - float(pxs[i]), y0 - float(pys[i])
            if ddx * ddx + ddy * ddy > 9:
                dc.line([(float(pxs[i]), float(pys[i])), (x0, y0)], fill=col, width=max(1, int(r * 1.3))); continue
        dc.ellipse([x0 - r, y0 - r, x0 + r, y0 + r], fill=col)

# =====================================================================  MICROBIAL WORLD: true shapes, lakhs of specks
def lamb(nx, ny, nz):
    L = np.array([-0.5, -0.55, 0.67]); L = L / np.linalg.norm(L); return np.clip(nx * L[0] + ny * L[1] + nz * L[2], 0, 1)

def stamp(I, cx, cy, r):
    x0 = int(cx - r) - 1; x1 = int(cx + r) + 2; y0 = int(cy - r) - 1; y1 = int(cy + r) + 2
    x0c, y0c = max(0, x0), max(0, y0); x1c, y1c = min(I.shape[1], x1), min(I.shape[0], y1)
    if x1c <= x0c or y1c <= y0c: return
    yy, xx = np.mgrid[y0c:y1c, x0c:x1c].astype(np.float32)
    nx = (xx - cx) / r; ny = (yy - cy) / r; d2 = nx * nx + ny * ny; ins = d2 < 1
    nz = np.sqrt(np.clip(1 - d2, 0, 1)); dd = np.sqrt(d2)
    val = (0.20 * nz + 0.60 * lamb(nx, ny, nz) ** 1.4 + 0.62 * np.exp(-((dd - 0.88) / 0.12) ** 2)) * ins
    spec = np.exp(-(((nx + 0.38) ** 2 + (ny + 0.42) ** 2) / 0.02)) * 0.55 * ins
    win = I[y0c:y1c, x0c:x1c]; np.maximum(win, val + spec, out=win)

def tube(size, pts, rads):
    I = np.zeros(size[::-1], np.float32)
    for (x, y), r in zip(pts, rads): stamp(I, x, y, max(1.0, r))
    return I

def path_dense(poly, step):
    out = []
    for a, b in zip(poly, poly[1:]):
        n = max(1, int(np.hypot(b[0] - a[0], b[1] - a[1]) / step))
        for k in range(n): out.append((a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n))
    out.append(poly[-1]); return out

def sprite_bacillus():
    pts = [(x, 40) for x in np.linspace(34, 94, 20)]; return tube((128, 80), pts, [15] * len(pts))
def sprite_flagrod():
    I = tube((300, 110), [(x, 55) for x in np.linspace(150, 200, 14)], [15] * 14)
    rng = np.random.RandomState(4)
    for k in range(4):
        ph = rng.rand() * 6; amp = 8 + rng.rand() * 6; y0 = 55 + (k - 1.5) * 7
        pts = [(150 - s, y0 + amp * math.sin(s / 14.0 + ph) * min(1, s / 30)) for s in np.linspace(0, 140, 90)]
        I = np.maximum(I, tube((300, 110), pts, [2.2] * len(pts)) * 0.75)
    return I
def sprite_coccus(): return tube((64, 64), [(32, 32)], [24])
def sprite_chain():
    pts = [(24 + k * 26, 48 + 9 * math.sin(k * 0.8)) for k in range(6)]; return tube((190, 96), pts, [14] * 6)
def sprite_staph():
    rng = np.random.RandomState(8); pts = []
    for k in range(9):
        a = rng.rand() * 6.28; rr = rng.rand() * 26; pts.append((56 + math.cos(a) * rr, 56 + math.sin(a) * rr))
    I = np.zeros((112, 112), np.float32)
    for (x, y) in sorted(pts, key=lambda p: p[1]): stamp(I, x, y, 14)
    return I
def sprite_spiral():
    pts = [(14 + 232 * s, 40 + 18 * math.sin(2 * math.pi * 3.2 * s)) for s in np.linspace(0, 1, 140)]
    I = tube((260, 80), pts, [6.5] * len(pts))
    for k in range(3):
        fl = [(250 + s, 40 + 18 * math.sin(2 * math.pi * 3.2) + (k - 1) * 3 + 5 * math.sin(s / 6.0)) for s in np.linspace(0, 9, 10)]
        I = np.maximum(I, tube((260, 80), fl, [1.6] * len(fl)) * 0.7)
    return I
def sprite_vibrio():
    pts = [(90 + 62 * math.cos(a), 105 - 62 * math.sin(a)) for a in np.linspace(0.45, 2.7, 46)]
    return tube((180, 130), pts, [max(6.5, 11 - 5 * abs(k / 45 - 0.5)) for k in range(46)])

def sprite_rbc(tilt):
    n = 200; y, x = np.mgrid[0:n, 0:n].astype(np.float32); c = (n - 1) / 2; R = 88
    rr = np.sqrt((x - c) ** 2 + (y - c) ** 2) / R; ins = rr < 1
    h = np.sqrt(np.clip(1 - rr ** 2, 0, 1)) * (0.207 + 2.002 * rr ** 2 - 1.123 * rr ** 4) * 0.5
    gy_, gx_ = np.gradient(h * 40)
    nx = -gx_; ny = -gy_; nz = np.ones_like(h); nn = np.sqrt(nx ** 2 + ny ** 2 + nz ** 2)
    lam = lamb(nx / nn, ny / nn, nz / nn)
    I = (0.18 + 0.55 * lam ** 1.3 + 0.55 * np.exp(-((rr - 0.93) / 0.08) ** 2) + 0.25 * (1 - rr)) * ins
    im = Image.fromarray((np.clip(I / 1.5, 0, 1) * 255).astype(np.uint8))
    if tilt > 0.01:
        w = max(40, int(n * math.cos(tilt))); im = im.resize((w, n), Image.BILINEAR)
        cv = Image.new("L", (n, n), 0); cv.paste(im, ((n - w) // 2, 0)); im = cv
    return np.asarray(im, np.float32) / 255 * 1.5

def sprite_wbc():
    n = 230; I = np.zeros((n, n), np.float32); stamp(I, n / 2, n / 2, 98); I *= 0.55
    for (dx, dy) in ((-34, -18), (22, -30), (6, 34)): stamp(I, n / 2 + dx, n / 2 + dy, 30)
    rng = np.random.RandomState(6)
    for k in range(26):
        a = rng.rand() * 6.28; rr = rng.rand() * 78; stamp(I, n / 2 + math.cos(a) * rr, n / 2 + math.sin(a) * rr, 5)
    return I
def sprite_epi():
    n = 260; im = Image.new("L", (n, n), 0); d = ImageDraw.Draw(im)
    hexp = [(130 + 108 * math.cos(math.pi / 3 * k + 0.5), 130 + 108 * math.sin(math.pi / 3 * k + 0.5)) for k in range(6)]
    d.polygon(hexp, fill=70); d.line(hexp + [hexp[0]], fill=235, width=8)
    I = np.asarray(im, np.float32) / 255 * 1.4
    stamp(I, 118, 140, 36)
    rng = np.random.RandomState(2)
    for k in range(70):
        a = rng.rand() * 6.28; rr = 96 + rng.rand() * 14; x = 130 + math.cos(a) * rr; y = 130 + math.sin(a) * rr
        pts = path_dense([(x, y), (x + math.cos(a) * 16, y + math.sin(a) * 16)], 2)
        I = np.maximum(I, tube((n, n), pts, [1.8] * len(pts)) * 0.8)
    return I

def to_pil(a): return Image.fromarray((np.clip(a / 1.5, 0, 1) * 255).astype(np.uint8))
def blurpad(im, rad): pad = int(rad * 3) + 2; return ImageOps.expand(im, border=pad, fill=0).filter(ImageFilter.GaussianBlur(rad))

KINDS = ["bacillus", "flagrod", "coccus", "chain", "staph", "spiral", "vibrio", "rbc0", "rbc1", "rbc2", "wbc", "epi"]
KSCALE = {"bacillus": 0.82, "flagrod": 0.82, "coccus": 0.75, "chain": 0.62, "staph": 0.9, "spiral": 0.98, "vibrio": 0.8, "rbc0": 1.47, "rbc1": 1.47, "rbc2": 1.47, "wbc": 1.3, "epi": 1.45}
ROTATING = {"bacillus", "flagrod", "chain", "spiral", "vibrio"}
_SP = {}
def sprites():
    if _SP: return _SP
    base = dict(bacillus=sprite_bacillus(), flagrod=sprite_flagrod(), coccus=sprite_coccus(), chain=sprite_chain(), staph=sprite_staph(), spiral=sprite_spiral(),
                vibrio=sprite_vibrio(), rbc0=sprite_rbc(0.0), rbc1=sprite_rbc(1.0), rbc2=sprite_rbc(1.35), wbc=sprite_wbc(), epi=sprite_epi())
    for k, I in base.items():
        pil = to_pil(I); lv = []
        for rad in (0, 3, 8):
            if k in ROTATING:
                row = []
                for a in range(24):
                    im = pil.rotate(a * 180.0 / 24, expand=True, resample=Image.BILINEAR)
                    row.append(blurpad(im, rad) if rad else im)
                lv.append(row)
            else:
                lv.append(blurpad(pil, rad * 1.5) if rad else pil)
        _SP[k] = lv
    return _SP

CLS_COL = {"t": np.array([0.20, 0.84, 0.77], np.float32), "c": np.array([0.35, 0.82, 1.0], np.float32), "v": np.array([0.62, 0.46, 1.0], np.float32),
           "m": np.array([1.0, 0.40, 0.78], np.float32), "g": np.array([1.0, 0.75, 0.30], np.float32)}
KIND_COL = {"bacillus": "t", "flagrod": "c", "coccus": "v", "chain": "m", "staph": "v", "spiral": "c", "vibrio": "m", "rbc0": "g", "rbc1": "g", "rbc2": "g", "wbc": "g", "epi": "g"}
KIND_N = {"bacillus": 210, "flagrod": 60, "coccus": 90, "chain": 45, "staph": 34, "spiral": 46, "vibrio": 34, "rbc0": 34, "rbc1": 34, "rbc2": 34, "wbc": 8, "epi": 10}
ZR = 2700.0; ZRF = 9000.0

_W = {}
def world():
    if _W: return _W
    r = np.random.RandomState(31); objs = []
    for k, n in KIND_N.items():
        for _ in range(n):
            objs.append((k, r.uniform(-1200, 1200), r.uniform(-1800, 1800), r.uniform(0, ZR), r.rand() * 3.14, 0.8 + r.rand() * 0.45, r.rand() * 6.28, 0.7 + r.rand() * 1.5))
    _W["objs"] = objs
    n = 900000; rr = np.random.RandomState(77)
    _W["dx"] = rr.uniform(-6500, 6500, n).astype(np.float32); _W["dy"] = rr.uniform(-10500, 10500, n).astype(np.float32); _W["dz"] = rr.uniform(0, ZRF, n).astype(np.float32)
    _W["dc"] = rr.choice(4, n, p=[0.30, 0.10, 0.16, 0.44]).astype(np.int8)    # teal, violet/magenta mix, cyan, gold (44% human)
    _W["do"] = rr.randint(0, 4, n).astype(np.int8)
    beams = R3.data()["beams"]; _W["beams"] = beams
    return _W

def add_sprite(acc, img, cx, cy, sc, color, gain):
    w = int(img.width * sc); h = int(img.height * sc)
    if w < 2 or h < 2 or w > 1700 or h > 1700: return
    x0 = int(cx - w / 2); y0 = int(cy - h / 2)
    if x0 >= W or y0 >= H or x0 + w <= 0 or y0 + h <= 0: return
    arr = np.asarray(img.resize((w, h), Image.BILINEAR), np.float32) * (gain / 255.0)
    sx0, sy0 = max(0, -x0), max(0, -y0); ex, ey = min(w, W - x0), min(h, H - y0)
    acc[y0 + sy0:y0 + ey, x0 + sx0:x0 + ex] += arr[sy0:ey, sx0:ex, None] * color

def cam_z(t):
    tau = max(0.0, t - 7.0)
    return 260.0 * tau + 1700.0 * (1 - math.exp(-tau / 0.9))

def draw_world3(t, acc, a):
    Wd = world(); S = sprites()
    camZ = cam_z(t); camx = 130 * math.sin(0.5 * t); camy = 90 * math.sin(0.37 * t)
    dfoc = 900 + 150 * math.sin(0.6 * t)
    gold_gain = 1.0 + 0.7 * sm((t - 8.0) / 0.3) * (1 - sm((t - 10.25) / 0.3))
    cool_gain = 1.0 + 0.7 * sm((t - 10.3) / 0.3) * (1 - sm((t - 12.4) / 0.3)) + 0.5 * math.exp(-max(0, t - 12.66) / 0.25) * (t > 12.66)
    # --- tier 1: hundreds of thousands of specks
    d = np.mod(Wd["dz"] - camZ, ZRF) + 40.0
    s = FZ / d
    sx = W / 2 + (Wd["dx"] - camx) * s; sy = 960 + (Wd["dy"] - camy) * s
    m = (d > 1400) & (sx >= 2) & (sx < W - 3) & (sy >= 2) & (sy < H - 3)
    idx = sy[m].astype(np.int32) * W + sx[m].astype(np.int32)
    w = (0.62 * np.exp(-d[m] / 6500.0) * np.clip((d[m] - 1400) / 1200, 0, 1)).astype(np.float32) * a
    cl = Wd["dc"][m]; od = Wd["do"][m]
    off = np.where(od == 0, 1, np.where(od == 1, W, np.where(od == 2, W + 1, W - 1)))
    bufs = np.zeros((H, W, 3), np.float32)
    colmap = {0: CLS_COL["t"], 1: CLS_COL["m"] * 0.5 + CLS_COL["v"] * 0.5, 2: CLS_COL["c"], 3: CLS_COL["g"]}
    for k in range(4):
        sel = cl == k
        if not sel.any(): continue
        b = np.bincount(idx[sel], weights=w[sel], minlength=H * W) + np.bincount(np.clip(idx[sel] + off[sel], 0, H * W - 1), weights=w[sel] * 0.6, minlength=H * W)
        bufs += b.reshape(H, W, 1).astype(np.float32) * colmap[k] * (gold_gain if k == 3 else cool_gain)
    acc += bufs * 1.15
    # --- tier 2: true-shaped sprites (shape by species)
    items = []
    for o in Wd["objs"]:
        dd = ((o[3] - camZ) % ZR) + 60; items.append((dd, o))
    items.sort(key=lambda it: -it[0])
    for dd, (k, x, y, z0, ang, sz, ph, sp) in items:
        s2 = FZ / dd
        sx2 = W / 2 + (x - camx) * s2; sy2 = 960 + (y - camy) * s2
        near = sm((dd - 70) / 240.0); far = 1 - sm((dd - 2300) / 400.0); fog = math.exp(-dd / 1700.0)
        al = near * far * (0.35 + 0.65 * fog) * a
        if al < 0.02: continue
        blur = abs(dd - dfoc); lvl = 0 if blur < 350 else (1 if blur < 800 else 2)
        if lvl: al *= 0.9 if lvl == 1 else 0.75
        spr = S[k][lvl]
        if k in ROTATING:
            an = ang + 0.3 * math.sin(t * sp + ph); spr = spr[int(((an % math.pi) / math.pi) * 24) % 24]
        sc = s2 * KSCALE[k] * sz
        cc = CLS_COL[KIND_COL[k]]
        g = al * (0.95 * gold_gain if KIND_COL[k] == "g" else 1.3 * cool_gain)
        add_sprite(acc, spr, sx2, sy2, sc, cc, g)
    # light shafts
    bm = Wd["beams"]; ox = int(120 + 70 * math.sin(t * 0.3)); oy = int(60 + 40 * math.sin(t * 0.21))
    shaft = bm[oy:oy + H, ox:ox + W] * (0.5 + 0.2 * math.sin(t * 0.8 + 1.0) + 0.3)
    acc += shaft[..., None] * (np.array([0.10, 0.34, 0.38], np.float32) * 0.28 * a)

# =====================================================================  FRAME
def render(t):
    D = R3.data(); gdata(); world(); sprites()
    acc = D["bg"].copy()
    a_hill_open = 1 - sm((t - 4.85) / 0.7) if t < 5.6 else 0.0
    a_hill_end = sm((t - 19.5) / 0.6) if t >= 19.5 else 0.0
    a_hill = a_hill_open if t < 10 else a_hill_end
    a_body = 0.0
    if 4.8 <= t < 7.9: a_body = sm((t - 4.85) / 0.7) * (1 - sm((t - 7.2) / 0.7))
    if 17.4 <= t < 20.4: a_body = (1 - sm((t - 19.6) / 0.6))
    a_world = sm((t - 7.15) / 0.7) * (1 - sm((t - 13.95) / 0.45)) if 7.1 < t < 14.4 else 0.0
    a_bars = sm((t - 14.0) / 0.4) * (1 - sm((t - 17.2) / 0.3)) if 13.9 < t < 17.6 else 0.0
    C = Image.new("RGB", (W, H), (0, 0, 0)); dc = ImageDraw.Draw(C)
    if a_body > 0.01 and not (7.9 <= t < 17.4): draw_body3(t, dc, a_body)
    if a_world > 0.01: draw_world3(t, acc, a_world)
    if a_world > 0.01:
        yy = np.arange(H, dtype=np.float32)[:, None, None]
        g = 0.40 + 0.60 * np.clip((yy - 60) / 560.0, 0, 1) ** 1.2
        acc = acc * (1 - a_world * (1 - g))
    sharp = np.asarray(C, np.float32) / 255
    acc += sharp * 0.95 + glow_np(C, 4) * 0.55
    if a_bars > 0.01:
        ov = bars_layer(t, a_bars); arr = np.asarray(ov, np.float32) / 255
        acc = acc * (1 - arr[..., 3:4]) + arr[..., :3] * arr[..., 3:4]
        acc += glow_np(ov.convert("RGB"), 6) * 0.45
    if a_hill > 0.01:
        hs = hill_scene(t, a_hill)
        acc = acc * (1 - a_hill) + hs * a_hill
    bright = np.clip(acc - 0.62, 0, 1)
    bl = np.asarray(Image.fromarray((np.clip(bright, 0, 1) * 255).astype(np.uint8)).resize((W // 8, H // 8), Image.BILINEAR).filter(ImageFilter.GaussianBlur(5)).resize((W, H), Image.BILINEAR), np.float32) / 255
    acc = acc + bl * 0.5
    ca, fl, sx, sy = hit_fx(t)
    if ca > 0.4:
        k = int(round(ca)); acc[..., 0] = np.roll(acc[..., 0], k, axis=1); acc[..., 2] = np.roll(acc[..., 2], -k, axis=1)
    acc = acc + fl
    if sx or sy: acc = np.roll(acc, (sy, sx), axis=(0, 1))
    if a_hill < 0.5: acc = acc * D["vig"]
    base = Image.fromarray((np.clip(acc, 0, 1) * 255).astype(np.uint8)).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    CRM = (244, 236, 214)
    q1, q2 = "HOW MUCH OF YOU", "IS ACTUALLY YOU?"
    if t < 3.8:
        n1 = int(max(0, t - 0.05) * 11.5); n2 = int(max(0, t - 1.8) * 11.5)
        lines = [q1[:n1], q2[:n2]] if t >= 1.8 else [q1[:n1], ""]
        put_text(ov, lines, 68, 130, CRM, 1 - sm((t - 3.55) / 0.2), path=SERIF, dx=sx // 2, dy=sy // 2)
    words = [("LESS", 3.79), ("THAN", 4.03), ("HALF.", 4.37)]
    if 3.79 <= t < 5.3:
        shown = " ".join(w for w, tw in words if t >= tw)
        pop = 1.0 + 0.4 * math.exp(-(t - max(tw for w, tw in words if t >= tw)) / 0.09)
        put_text(ov, [shown], 92, 150, GOLD, sm((t - 3.79) / 0.04) * (1 - sm((t - 4.95) / 0.3)), path=SERIF, scale=min(1.14, pop), dx=sx // 2, dy=sy // 2)
    if 5.18 <= t < 8.0:
        put_text(ov, typed(["SO WHO ELSE", "IS IN THERE?"], int((t - 5.18) * 9.5)), 90, 230, CREAM, sm((t - 5.18) / 0.1) * (1 - sm((t - 7.55) / 0.35)), path=SERIF)
    if 8.0 < t < 14.0:
        d = ImageDraw.Draw(ov); fa = 1 - sm((t - 13.8) / 0.25)
        eg = sm((t - 8.08) / 2.0); et = sm((t - 10.35) / 1.95); ga = sm((t - 8.0) / 0.2) * fa; ta = sm((t - 10.3) / 0.2) * fa
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
        put_text(ov, ["YOU HAVE NEVER", "BEEN ALONE."], 90, 150, CRM, sm((t - 17.7) / 0.06) * (1 - sm((t - 19.8) / 0.3)), path=SERIF, scale=min(1.25, 1 + 0.4 * math.exp(-(t - 17.75) / 0.1)), dx=sx // 2, dy=sy // 2)
    if t >= 20.2:
        l1, l2 = "NEXT: THE OLDEST THING IN YOU", "IS OLDER THAN THE SUN."
        n = int((t - 20.2) * 12.5)
        put_text(ov, [l1[:n], l2[:max(0, n - len(l1))]], 46, 1480, GOLD, sm((t - 20.2) / 0.3), path=SERIF)
        put_text(ov, ["FOLLOW"], 40, 1665, CRM, 0.75 * sm((t - 22.6) / 0.4), path=FONT_S, glow=False)
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
        cmd += ["-t", f"{DUR}", "-c:v", "libx264", "-crf", "22", "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", out]
        pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        with Pool(4) as p:
            for k, b in enumerate(p.imap(render_bytes, range(N), chunksize=3)):
                pr.stdin.write(b)
                if k % 90 == 0: print("frame", k, "/", N, flush=True)
        pr.stdin.close(); pr.wait()

if __name__ == "__main__":
    main()
