#!/usr/bin/env python3
"""How Much of You Is Actually You? v4.
Changes on v3:
- the figure is a smooth ray-marched SDF mannequin (clay-doll proportions) with wrap-around ink hatching, an ink outline and a
  chromatic glitch fringe, like the reference
- at "so who else" the figure atomizes BOTTOM TO TOP into coloured atoms (the atoms are sampled from the same SDF volume, so the
  shape matches exactly), the green field darkens, and the camera pans inside
- CTA: "NEXT:" removed from the text and from the voice

usage: render_v4.py sheet OUT.png t1 t2 ... | frame OUT.png t | video OUT.mp4 audio.wav
"""
import math, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from multiprocessing import Pool
import render3d as R3
import render_v3 as V3
from render3d import sm, key, W, H, FPS, DUR, N, put_text, typed, bars_layer, glow_np, hit_fx, COL, CREAM, GOLD, TEAL, FONT_B, FONT_S, font
from render_v3 import SERIF, FO

# =====================================================================  SDF MANNEQUIN
K_SM = 30.0

def smin(a, b, k):
    h = np.maximum(k - np.abs(a - b), 0) / k
    return np.minimum(a, b) - h * h * k * 0.25

def sd_ell(x, y, z, cx, cy, cz, rx, ry, rz):
    q = np.sqrt(((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 + ((z - cz) / rz) ** 2)
    return (q - 1.0) * min(rx, ry, rz)

def sd_cap(x, y, z, a, b, ra, rb):
    ba = (b[0] - a[0], b[1] - a[1], b[2] - a[2]); bb = ba[0] ** 2 + ba[1] ** 2 + ba[2] ** 2
    px, py, pz = x - a[0], y - a[1], z - a[2]
    h = np.clip((px * ba[0] + py * ba[1] + pz * ba[2]) / bb, 0, 1)
    dx, dy, dz = px - ba[0] * h, py - ba[1] * h, pz - ba[2] * h
    return np.sqrt(dx * dx + dy * dy + dz * dz) - (ra + (rb - ra) * h)

def sdf(x, y, z):
    ax = np.abs(x)
    d = sd_ell(x, y, z, 2, 786, 18, 64, 80, 68)                                   # head (big egg, forward)
    d = smin(d, sd_cap(x, y, z, (0, 735, 6), (0, 700, 0), 30, 32), K_SM)           # neck
    d = smin(d, sd_ell(x, y, z, 0, 628, 0, 92, 100, 60), K_SM)                    # chest
    d = smin(d, sd_ell(x, y, z, 0, 516, 10, 84, 110, 58), K_SM)                   # belly
    d = smin(d, sd_ell(x, y, z, 0, 428, 0, 84, 64, 56), K_SM)                     # pelvis
    d = smin(d, sd_ell(ax, y, z, 90, 676, 0, 42, 38, 40), K_SM)                   # sloped shoulders
    d = smin(d, sd_cap(ax, y, z, (98, 660, 0), (112, 552, 18), 33, 28), K_SM)     # upper arm
    d = smin(d, sd_cap(ax, y, z, (112, 552, 18), (104, 448, 46), 28, 24), K_SM)   # forearm
    d = smin(d, sd_ell(ax, y, z, 100, 412, 50, 27, 42, 23), K_SM)                 # big hand
    d = smin(d, sd_cap(ax, y, z, (40, 420, 0), (46, 232, 8), 46, 36), K_SM)       # thigh
    d = smin(d, sd_cap(ax, y, z, (46, 232, 8), (48, 54, 0), 35, 26), K_SM)        # shin
    d = smin(d, sd_ell(ax, y, z, 50, 24, 40, 30, 24, 64), K_SM)                   # foot
    return d

def sdf_normal(x, y, z, e=1.2):
    nx = sdf(x + e, y, z) - sdf(x - e, y, z); ny = sdf(x, y + e, z) - sdf(x, y - e, z); nz = sdf(x, y, z + e) - sdf(x, y, z - e)
    n = np.sqrt(nx * nx + ny * ny + nz * nz) + 1e-9
    return nx / n, ny / n, nz / n

# =====================================================================  DATA (SDF point sets: clone + atoms)
_Z = {"done": False}
def ensure():
    if _Z["done"]: return
    R3.data(); V3.gdata(); V3.world(); V3.sprites()
    rng = np.random.RandomState(5)
    pts = []
    for _ in range(14):
        n = 400000
        x = rng.uniform(-170, 170, n).astype(np.float32); y = rng.uniform(0, 900, n).astype(np.float32); z = rng.uniform(-110, 130, n).astype(np.float32)
        d = sdf(x, y, z); ok = d < 0
        pts.append(np.stack([x[ok], y[ok], z[ok], d[ok]], 1))
        if sum(len(p) for p in pts) > 90000: break
    P = np.concatenate(pts)[:90000]
    d = P[:, 3]; shell = d > -14
    X, Y, Z = P[:, 0], P[:, 1], P[:, 2]
    nx, ny, nz = sdf_normal(X, Y, Z)
    Nm = np.stack([nx, ny, nz], 1).astype(np.float32)
    n = len(P)
    V3._G["solid"] = dict(P=np.stack([X, Y, Z], 1).astype(np.float32), Nm=Nm, rank=rng.rand(n).astype(np.float32),
                          cls=rng.choice([1, 2, 3], n, p=[0.55, 0.22, 0.23]), rv=rng.rand(n).astype(np.float32))
    V3._G["clone"] = np.nonzero(shell)[0][:26000]
    # atom cloud for the dive (screen-style coordinates: Y down, 0 = torso centre)
    sel = np.nonzero(shell | (rng.rand(n) < 0.35))[0][:30000]
    Xs, Ys, Zs = X[sel], 436.0 - Y[sel], Z[sel]
    L = np.array([-0.5, 0.8, 0.6]); L = L / np.linalg.norm(L)
    lit = np.clip(nx[sel] * L[0] + ny[sel] * L[1] + nz[sel] * L[2], 0, 1); rim = (1 - np.abs(nz[sel])) ** 1.5
    br = np.where(shell[sel], 0.45 + 0.55 * lit + 0.45 * rim, 0.32 + 0.1 * rng.rand(len(sel)))
    m = len(sel)
    R3._D["body"] = dict(X=Xs.astype(np.float32), Y=Ys.astype(np.float32), Z=Zs.astype(np.float32), r=(1.6 + rng.rand(m) * 1.7).astype(np.float32),
                         br=np.clip(br, 0.3, 1.15).astype(np.float32), ph=(rng.rand(m) * 6.28).astype(np.float32), fx=(0.6 + rng.rand(m) * 1.4).astype(np.float32),
                         fy=(0.6 + rng.rand(m) * 1.4).astype(np.float32), teal=(rng.rand(m) < 0.56), jit=rng.rand(m).astype(np.float32),
                         ang=(rng.rand(m) * 6.28).astype(np.float32), Yup=Y[sel].astype(np.float32))
    _Z["done"] = True

# =====================================================================  TIMELINE
T_ATOM = 5.18; ATOM_DUR = 1.45
def front_y(t):
    return -1.0 if (t < T_ATOM or t > 10.0) else (t - T_ATOM) / ATOM_DUR * 930.0 - 20.0

def hill_state4(t):
    if t < 19.5:
        u = sm(min(t, 5.0) / 5.0)
        th = -1.1 * (1 - u); Hc = 440 + 460 * (1 - u); D = 1000.0
        s = sm((t - 3.7) / 1.2)
        pw = key(t, [(3.79, 0.0), (4.03, 0.34), (4.37, 0.66), (4.82, 1.0)])
        clone = 1.0 - sm((t - 3.85) / 0.95)
        return th, Hc, D, s, pw, clone
    u = sm((t - 19.6) / 5.3) if t > 19.6 else 0.0
    th = -1.1 * u; Hc = 440 + 460 * u; D = 1400 - 400 * u
    s = 1 - sm((t - 20.0) / 4.4); pw = 1 - sm((t - 21.2) / 2.7); clone = sm((t - 23.2) / 1.6)
    return th, Hc, D, s, pw, clone

_orig_body_cam = R3.body_cam.__wrapped__ if hasattr(R3.body_cam, "__wrapped__") else None
def _real_body_cam():
    # R3.body_cam was monkeypatched by render_v3; recover the original implementation by re-defining it here
    def body_cam(t):
        th = 0.30 * math.sin(0.55 * t)
        if t < 17.45:
            return None
        if t < 19.95:
            u = (t - 17.45) / 2.5; e = 1 - (1 - u) ** 2.2
            return -320 + 1720 * e, 0.0, -140 * (1 - sm(u)), (0.9 * (1 - u)) * (1 - sm(u)) + th * sm(u), 0.25 * (1 - sm(u))
        u = (t - 19.95) / 4.95
        return V3.R3.F_BODY - 60 * math.sin(math.pi * u), 0.0, 0.0, th, 0.0
    return body_cam
_ret = _real_body_cam()

def body_cam4(t):
    th = 0.30 * math.sin(0.55 * t)
    if t < 6.0: return 1000.0, 0.0, 0.0, 0.0, 0.0
    if t < 7.9:
        u = (t - 6.0) / 1.9
        return 1000.0 - 1320.0 * u ** 1.8, 0.0, -140 * sm(u), 0.9 * u, 0.25 * sm(u)
    if t < 17.45: return -320.0, 0.0, -140.0, 0.0, 0.0
    return _ret(t)
R3.body_cam = body_cam4

# =====================================================================  RAY-MARCHED FIGURE
def render_solid4(t, C, r, u, f, pconv, shade_w=1.0):
    G = V3.gdata()
    hh, ww = H // 2, W // 2
    px, py = G["px"], G["py"]
    dx = (f[0] + px * r[0] - py * u[0]).ravel(); dy = (f[1] + px * r[1] - py * u[1]).ravel(); dz = (f[2] + px * r[2] - py * u[2]).ravel()
    nrm = np.sqrt(dx * dx + dy * dy + dz * dz); dx /= nrm; dy /= nrm; dz /= nrm
    ctr = np.array([0.0, 440.0, 0.0], np.float32); RB = 520.0
    ocx, ocy, ocz = ctr[0] - C[0], ctr[1] - C[1], ctr[2] - C[2]
    b = dx * ocx + dy * ocy + dz * ocz; cc = ocx * ocx + ocy * ocy + ocz * ocz - RB * RB
    disc = b * b - cc
    cand = np.nonzero(disc > 0)[0]
    t0 = (b - np.sqrt(np.maximum(disc, 0)))[cand]; t1 = (b + np.sqrt(np.maximum(disc, 0)))[cand]
    tt = np.maximum(t0, 0).astype(np.float32); tmax = t1.astype(np.float32)
    D = np.stack([dx[cand], dy[cand], dz[cand]], 1)
    hit = np.zeros(len(cand), bool); steps = np.zeros(len(cand), np.float32)
    act = np.arange(len(cand))
    for it in range(30):
        if act.size == 0: break
        x = C[0] + tt[act] * D[act, 0]; y = C[1] + tt[act] * D[act, 1]; z = C[2] + tt[act] * D[act, 2]
        d = sdf(x, y, z)
        hm = d < 0.7; fm = tt[act] > tmax[act]
        hit[act[hm]] = True; steps[act[hm]] = it
        keep = ~(hm | fm)
        tt[act[keep]] += d[keep] * 0.9
        act = act[keep]
    hi = np.nonzero(hit)[0]
    X = C[0] + tt[hi] * D[hi, 0]; Y = C[1] + tt[hi] * D[hi, 1]; Z = C[2] + tt[hi] * D[hi, 2]
    nx, ny, nz = sdf_normal(X, Y, Z)
    L = np.array([-0.78, 0.55, 0.42], np.float32); L = L / np.linalg.norm(L)
    lam = np.clip(nx * L[0] + ny * L[1] + nz * L[2], 0, 1)
    ao = 1.0 - 0.30 * (steps[hi] / 30.0)
    shade = np.clip((0.20 + 0.86 * lam ** 0.85) * ao, 0, 1)
    flat = np.zeros(hh * ww, np.float32)
    buf = {}
    for name, val in (("m", np.ones_like(X)), ("s", shade), ("x", X), ("y", Y), ("z", Z), ("nz", nz)):
        arr = flat.copy(); arr[cand[hi]] = val; buf[name] = arr.reshape(hh, ww)
    def up(a, fill=0.0):
        im = Image.fromarray(a.astype(np.float32), mode="F").resize((W, H), Image.BILINEAR)
        return np.asarray(im, np.float32)
    mk = up(buf["m"]); mask = mk > 0.5
    # smooth data up to full-res (mask-weighted so the silhouette does not bleed)
    wgt = np.maximum(mk, 1e-3)
    Sh = up(buf["s"]) / wgt; Xw = up(buf["x"]) / wgt; Yw = up(buf["y"]) / wgt; Zw = up(buf["z"]) / wgt
    # atomization: remove everything below the front, with a glowing seam
    fy = front_y(t)
    seam = np.zeros((H, W), np.float32)
    if fy > 0:
        gone = Yw < fy; seam = np.clip(1 - (Yw - fy) / 38.0, 0, 1) * (~gone) * mask
        mask = mask & ~gone
    base = np.array([0.97, 0.96, 0.98], np.float32)
    cool = np.array([0.70, 0.74, 0.90], np.float32)
    col = base * (0.46 + 0.54 * Sh[..., None]) * (cool + (1 - cool) * Sh[..., None])
    # wrap-around contour hatching + cross hatch in the shadows
    th1 = np.clip((0.78 - Sh) * 1.5, 0, 0.85); th2 = np.clip((0.34 - Sh) * 2.4, 0, 0.7)
    nzz = np.sin(Xw * 0.23 + Zw * 0.19 + 1.3) * np.sin(Yw * 0.11 + Xw * 0.07) + 0.5 * np.sin(Yw * 0.29 + Zw * 0.21)
    l1 = (((Yw / 7.5 + 0.6 * np.sin(Xw / 31.0 + Zw / 44.0) + 0.25 * nzz) % 1.0) < th1) & (nzz > -0.45)
    l2 = ((((Xw * 0.8 + Zw * 0.6) / 8.5 + 0.3 * nzz) % 1.0) < th2) & (nzz > -0.2)
    ink = np.array([0.16, 0.15, 0.24], np.float32)
    lines = (l1 | l2)[..., None]
    col = np.where(lines, col * 0.28 + ink * 0.5, col)
    # glitch skin: object-space voxels dissolve into coloured pixels
    if pconv > 0.001:
        vx = np.floor(Xw / 9.0); vy = np.floor(Yw / 9.0); vz = np.floor(Zw / 9.0)
        hsh = np.sin(vx * 12.9898 + vy * 78.233 + vz * 37.719) * 43758.5453; rk = hsh - np.floor(hsh)
        hs2 = np.sin(vx * 39.346 + vy * 11.135 + vz * 83.155) * 24634.6345; cl = hs2 - np.floor(hs2)
        conv = (rk < pconv * 0.56) & mask
        pal = np.array([[0.20, 0.95, 0.82], [0.98, 0.28, 0.80], [0.55, 0.35, 1.0]], np.float32)
        ci = np.minimum((cl * 3).astype(int), 2)
        gcol = pal[ci] * (0.72 + 0.6 * ((rk * 7.0 + math.floor(t * 8) * 0.37) % 1.0))[..., None] * (0.75 + 0.3 * Sh[..., None])
        col = np.where(conv[..., None], gcol, col)
    # ink outline + chromatic fringe
    er = mask.copy()
    for sh_ in ((2, 0), (-2, 0), (0, 2), (0, -2)):
        er &= np.roll(mask, sh_, axis=(0, 1))
    outline = mask & ~er
    col = np.where(outline[..., None], np.array([0.10, 0.09, 0.16], np.float32), col)
    fr = np.roll(mask, 5, axis=1) & ~mask
    rn = np.random.RandomState(int(t * 8) % 97).rand(H, W).astype(np.float32)
    fcol = np.stack([0.65 + 0.3 * rn, 0.10 + 0.3 * rn, 0.95 - 0.2 * rn], -1)
    col = np.where(fr[..., None], fcol * 0.9, col)
    # atomization seam glow
    if fy > 0:
        col = np.where((seam > 0.02)[..., None], col * (1 - seam[..., None]) + np.array([1.0, 0.86, 0.45], np.float32) * (0.9 + 0.8 * seam[..., None]) * seam[..., None], col)
    return col * mask[..., None], (mask | fr).astype(np.float32)

V3.render_solid = render_solid4
V3.hill_state = hill_state4

# =====================================================================  HILL SCENE WRAPPER (eyes at the new head, darkening)
def hill_scene4(t):
    ensure()
    th, Hc, D, s, pconv, clone_a = hill_state4(t)
    C = np.array([D * math.sin(th), Hc, D * math.cos(th)], np.float32); T = np.array([0.0, 440.0, 0.0], np.float32)
    r, u, f = V3.lookat(C, T)
    img = V3.ground_bg(C, r, u, f, s)
    mono, zm = V3.draw_monolith(C, r, u, f)
    cp = float((np.array([0, 440, 0], np.float32) - C) @ f)
    def over(base, rgba): return base * (1 - rgba[..., 3:4]) + rgba[..., :3] * rgba[..., 3:4]
    if zm > cp: img = over(img, mono)
    if clone_a > 0.01:
        cb, cm = V3.render_clone(t, C, r, u, f, clone_a)
        img = img * (1 - cm[..., None] * 0.92) + cb * cm[..., None] * 0.92
    fig, fm = render_solid4(t, C, r, u, f, pconv)
    img = img * (1 - fm[..., None]) + fig * fm[..., None]
    if zm <= cp: img = over(img, mono)
    head = np.array([0, 802, 66], np.float32)
    face_dot = float(np.dot(C - head, [0, 0, 1])) / float(np.linalg.norm(C - head))
    if face_dot > 0.4 and front_y(t) < 780:
        e = np.array([[-22, 802, 66], [22, 802, 66]], np.float32); ex, ey, _ = V3.project(e, C, r, u, f)
        pi = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)); dd = ImageDraw.Draw(pi)
        for a, b in zip(ex, ey): dd.ellipse([a - 5, b - 5, a + 5, b + 5], fill=(214, 44, 130))
        img = np.asarray(pi, np.float32) / 255
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    rr = np.sqrt(((xx - W / 2) / (W * 0.72)) ** 2 + ((yy - H * 0.5) / (H * 0.62)) ** 2)
    img = img * np.clip(1.0 - (0.40 + 0.30 * s) * np.clip(rr - 0.3, 0, 1.3) ** 1.6, 0, 1)[..., None]
    img = img * (1.0 - 0.12 * s)
    dark = 0.88 * sm((t - 5.45) / 1.0) if 5.0 < t < 8 else 0.0
    return img * (1 - dark)

# =====================================================================  ATOMS (dive cloud with bottom-to-top release)
def draw_atoms(t, dc, a):
    B = R3._D["body"]
    sx, sy, d, f = R3.project_body(B, t, t)
    pxs, pys, pd, pf = R3.project_body(B, t, t - 1 / 40.0)
    tr = T_ATOM + ATOM_DUR * np.clip(B["Yup"] / 880.0, 0, 1) + 0.05 * B["jit"]
    since = t - tr
    rel = since > 0
    fly = np.exp(-np.maximum(since, 0) / 0.35)
    ang = B["ang"]
    ox = np.cos(ang) * 70 * fly; oy = np.sin(ang) * 70 * fly - 25 * fly
    sx = sx + ox * (f / 1.0); sy = sy + oy * (f / 1.0)
    flash = 1 + 0.8 * np.exp(-np.maximum(since, 0) / 0.22)
    rad = B["r"] * np.minimum(f, 14.0) ** 0.9 * (1 + 0.14 * np.sin(t * 3 + B["ph"])) * (1 + 0.35 * np.exp(-np.maximum(since, 0) / 0.2))
    vis = rel & (sx > -80) & (sx < W + 80) & (sy > -80) & (sy < H + 80) & (d > 25) & (f < 70)
    streak = abs(R3.body_cam(t)[0] - R3.body_cam(t - 1 / 40.0)[0]) > 4
    near = np.clip(d / 220.0, 0.15, 1.0)
    for i in np.nonzero(vis)[0]:
        nm = "teal" if B["teal"][i] else "gold"
        r_ = float(rad[i]) * (1.3 if nm == "gold" else 1.0); x0, y0 = float(sx[i]), float(sy[i])
        k = a * float(B["br"][i]) * float(near[i]) * float(flash[i]) * (0.82 if nm == "teal" else 1.0)
        col = tuple(min(255, int(c * min(k, 1.25) * 1.0)) for c in COL[nm])
        if streak and pd[i] > 25:
            ddx, ddy = x0 - float(pxs[i]), y0 - float(pys[i])
            if ddx * ddx + ddy * ddy > 9:
                dc.line([(float(pxs[i]), float(pys[i])), (x0, y0)], fill=col, width=max(1, int(r_ * 1.3))); continue
        dc.ellipse([x0 - r_, y0 - r_, x0 + r_, y0 + r_], fill=col)

# =====================================================================  FRAME
def render(t):
    ensure()
    D = R3.data()
    acc = D["bg"].copy()
    a_hill = 1.0 if t < 6.2 else (1 - sm((t - 6.2) / 0.8) if t < 7.0 else 0.0)
    if t >= 19.5: a_hill = sm((t - 19.5) / 0.6)
    a_body = 0.0
    if 5.18 <= t < 7.9: a_body = 1 - sm((t - 7.2) / 0.7)
    if 17.4 <= t < 20.4: a_body = 1 - sm((t - 19.6) / 0.6)
    a_world = sm((t - 7.15) / 0.7) * (1 - sm((t - 13.95) / 0.45)) if 7.1 < t < 14.4 else 0.0
    a_bars = sm((t - 14.0) / 0.4) * (1 - sm((t - 17.2) / 0.3)) if 13.9 < t < 17.6 else 0.0
    if a_hill > 0.01:
        hs = hill_scene4(t); acc = acc * (1 - a_hill) + hs * a_hill
    C = Image.new("RGB", (W, H), (0, 0, 0)); dc = ImageDraw.Draw(C)
    if a_body > 0.01 and not (7.9 <= t < 17.4): draw_atoms(t, dc, a_body)
    if a_world > 0.01: V3.draw_world3(t, acc, a_world)
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
    if t >= 20.16:
        l1, l2 = "THE OLDEST THING IN YOU", "IS OLDER THAN THE SUN."
        n = int((t - 20.16) * 15.0)
        put_text(ov, [l1[:n], l2[:max(0, n - len(l1))]], 54, 1480, GOLD, sm((t - 20.16) / 0.3), path=SERIF)
        put_text(ov, ["FOLLOW"], 40, 1665, CRM, 0.75 * sm((t - 22.4) / 0.4), path=FONT_S, glow=False)
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
