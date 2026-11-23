#!/usr/bin/env python3
"""Glossy white vinyl stickman (design after the attached Meta AI figure): big sphere head, tube limbs with visible joints, fist hands,
simple dot eyes with highlights, brow lines, tiny mouth. Posable by segment directions (forward kinematics), ray-marched SDF.

API: render(pose, mood, C, r, u, f) -> (rgb, mask)   |   POSES, MOODS dicts
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 1080, 1920
FO = 1400.0

def nrm(v):
    v = np.array(v, np.float32); return v / (np.linalg.norm(v) + 1e-9)

# ---------------------------------------------------------------- skeleton (world units, figure ~950 tall, feet at y=0)
LEN = dict(thigh=215, shin=205, torso=200, uarm=148, farm=138)
RAD = dict(head=118, torso0=46, torso1=60, uarm=17, farm=16, hand=29, thigh=21, shin=18, foot=21)

def skeleton(P):
    pel = np.array(P.get("pelvis", (0, 470, 0)), np.float32)
    sp = nrm(P.get("spine", (0, 1, 0)))
    chest = pel + sp * LEN["torso"]
    sk = {"pelvis": pel, "chest": chest}
    # head
    hd = nrm(P.get("neck", (0, 1, 0)))
    sk["head"] = chest + hd * (RAD["head"] * 0.80)
    side = nrm(np.cross(sp, [0, 0, 1])) if abs(sp[2]) < 0.99 else np.array([1, 0, 0], np.float32)
    side = np.array([1.0, 0.0, 0.0], np.float32)
    for sd, nm in ((-1, "L"), (1, "R")):
        sh = chest + np.array([sd * 70, -26, 0], np.float32); sk["sh" + nm] = sh
        ua = nrm(P.get("ua" + nm, (sd * 0.10, -1, 0.0))); fa = nrm(P.get("fa" + nm, (sd * 0.05, -1, 0.0)))
        el = sh + ua * LEN["uarm"]; wr = el + fa * LEN["farm"]
        sk["el" + nm] = el; sk["wr" + nm] = wr; sk["fist" + nm] = wr + fa * 22; sk["fa" + nm] = fa
        hp = pel + np.array([sd * 30, -14, 0], np.float32); sk["hp" + nm] = hp
        th = nrm(P.get("th" + nm, (sd * 0.04, -1, 0.0))); sh_ = nrm(P.get("sh_" + nm, (sd * 0.02, -1, 0.0)))
        kn = hp + th * LEN["thigh"]; an = kn + sh_ * LEN["shin"]
        ft = nrm(P.get("ft" + nm, (sd * 0.35, 0, 1.0)))
        sk["kn" + nm] = kn; sk["an" + nm] = an; sk["toe" + nm] = an + ft * 30
    return sk

def smin(a, b, k):
    h = np.maximum(k - np.abs(a - b), 0) / k
    return np.minimum(a, b) - h * h * k * 0.25

def sd_cap(x, y, z, a, b, ra, rb):
    ba = b - a; bb = float(ba @ ba) + 1e-9
    px, py, pz = x - a[0], y - a[1], z - a[2]
    h = np.clip((px * ba[0] + py * ba[1] + pz * ba[2]) / bb, 0, 1)
    dx, dy, dz = px - ba[0] * h, py - ba[1] * h, pz - ba[2] * h
    return np.sqrt(dx * dx + dy * dy + dz * dz) - (ra + (rb - ra) * h)

def sd_sph(x, y, z, c, r):
    return np.sqrt((x - c[0]) ** 2 + (y - c[1]) ** 2 + (z - c[2]) ** 2) - r

def sd_ell(x, y, z, c, rx, ry, rz):
    q = np.sqrt(((x - c[0]) / rx) ** 2 + ((y - c[1]) / ry) ** 2 + ((z - c[2]) / rz) ** 2)
    return (q - 1.0) * min(rx, ry, rz)

def hand_frame(wr, fa, hint):
    a = nrm(fa); n = hint - a * float(hint @ a)
    n = nrm(n) if np.linalg.norm(n) > 1e-3 else nrm(np.cross(a, [0, 0, 1]))
    s_ = nrm(np.cross(a, n))
    return a, n, s_

def sd_hand(x, y, z, wr, fa, hint, side):
    """fist like the Meta AI figure: palm block + four curled fingers (grooves between them) + thumb across the front"""
    a, n, s_ = hand_frame(wr, fa, hint)
    c = wr + a * 26
    lx = (x - c[0]) * s_[0] + (y - c[1]) * s_[1] + (z - c[2]) * s_[2]
    ly = (x - c[0]) * a[0] + (y - c[1]) * a[1] + (z - c[2]) * a[2]
    lz = (x - c[0]) * n[0] + (y - c[1]) * n[1] + (z - c[2]) * n[2]
    q = np.sqrt((lx / 37.0) ** 2 + (ly / 31.0) ** 2 + (lz / 27.0) ** 2)
    d = (q - 1.0) * 27.0                                           # palm / back of the hand
    base = wr + a * 43
    for k, off in enumerate((-23.0, -7.7, 7.7, 23.0)):
        p0 = base + s_ * off
        p1 = p0 + a * 7 + n * 9
        p2 = p1 + n * 15 - a * 13                                   # finger curls tightly into the palm
        d = smin(d, sd_cap(x, y, z, p0, p1, 11.0, 10.4), 2.0)
        d = smin(d, sd_cap(x, y, z, p1, p2, 10.4, 9.2), 2.0)
    t0 = wr + a * 20 + s_ * (-side * 31) + n * 8
    t1 = wr + a * 50 + s_ * (-side * 8) + n * 27
    d = smin(d, sd_cap(x, y, z, t0, t1, 11.5, 10.0), 3)               # thumb across the fingers
    return d

def make_sdf(P):
    sk = skeleton(P)
    props = P.get("props", [])
    def sdf(x, y, z):
        d = sd_cap(x, y, z, sk["pelvis"], sk["chest"], RAD["torso0"], RAD["torso1"])
        d = smin(d, sd_sph(x, y, z, sk["head"], RAD["head"]), 10)
        for nm in ("L", "R"):
            d = smin(d, sd_cap(x, y, z, sk["sh" + nm], sk["el" + nm], RAD["uarm"], RAD["uarm"]), 6)
            d = smin(d, sd_cap(x, y, z, sk["el" + nm], sk["wr" + nm], RAD["farm"], RAD["farm"]), 6)
            d = smin(d, sd_hand(x, y, z, sk["wr" + nm], sk["fa" + nm], sk["chest"] - sk["wr" + nm], -1 if nm == "L" else 1), 4)
            d = smin(d, sd_cap(x, y, z, sk["hp" + nm], sk["kn" + nm], RAD["thigh"], RAD["thigh"] - 1), 6)
            d = smin(d, sd_cap(x, y, z, sk["kn" + nm], sk["an" + nm], RAD["shin"], RAD["shin"] - 1), 6)
            d = smin(d, sd_cap(x, y, z, sk["an" + nm], sk["toe" + nm], RAD["foot"], RAD["foot"] - 1), 6)
        for pr in props:
            if pr[0] == "cap": d = np.minimum(d, sd_cap(x, y, z, np.array(pr[1], np.float32), np.array(pr[2], np.float32), pr[3], pr[3]))
            if pr[0] == "ell": d = np.minimum(d, sd_ell(x, y, z, np.array(pr[1], np.float32), pr[2], pr[3], pr[4]))
        return d
    return sdf, sk

# ---------------------------------------------------------------- render
_GRID = {}
RES = {"k": 2}
def grid():
    k = RES["k"]
    if _GRID.get("k") != k:
        hh, ww = H // k, W // k
        gy, gx = np.mgrid[0:hh, 0:ww].astype(np.float32)
        _GRID["px"] = (gx * k - W / 2) / FO; _GRID["py"] = (gy * k - H / 2) / FO; _GRID["k"] = k
    return _GRID

def lookat(C, T):
    f = T - C; f = f / np.linalg.norm(f); r = np.cross(f, [0.0, 1.0, 0.0]); r = r / np.linalg.norm(r); u = np.cross(r, f)
    return r, u, f

def march(sdf, C, r, u, f):
    G = grid(); k = RES["k"]; hh, ww = H // k, W // k
    dx = (f[0] + G["px"] * r[0] - G["py"] * u[0]).ravel(); dy = (f[1] + G["px"] * r[1] - G["py"] * u[1]).ravel(); dz = (f[2] + G["px"] * r[2] - G["py"] * u[2]).ravel()
    n = np.sqrt(dx * dx + dy * dy + dz * dz); dx /= n; dy /= n; dz /= n
    ctr = np.array([0.0, 470.0, 0.0], np.float32); RB = 900.0
    oc = ctr - C; b = dx * oc[0] + dy * oc[1] + dz * oc[2]; cc = float(oc @ oc) - RB * RB
    disc = b * b - cc
    cand = np.nonzero(disc > 0)[0]; sq = np.sqrt(np.maximum(disc, 0))
    tt = np.maximum((b - sq)[cand], 0).astype(np.float32); tmax = (b + sq)[cand].astype(np.float32)
    D = np.stack([dx[cand], dy[cand], dz[cand]], 1)
    hit = np.zeros(len(cand), bool); steps = np.zeros(len(cand), np.float32); act = np.arange(len(cand))
    for it in range(40):
        if act.size == 0: break
        x = C[0] + tt[act] * D[act, 0]; y = C[1] + tt[act] * D[act, 1]; z = C[2] + tt[act] * D[act, 2]
        dd = sdf(x, y, z); hm = dd < 0.5; fm = tt[act] > tmax[act]
        hit[act[hm]] = True; steps[act[hm]] = it
        keep = ~(hm | fm); tt[act[keep]] += dd[keep] * 0.9; act = act[keep]
    hi = np.nonzero(hit)[0]
    X = C[0] + tt[hi] * D[hi, 0]; Y = C[1] + tt[hi] * D[hi, 1]; Z = C[2] + tt[hi] * D[hi, 2]
    e = 1.0
    nx = sdf(X + e, Y, Z) - sdf(X - e, Y, Z); ny = sdf(X, Y + e, Z) - sdf(X, Y - e, Z); nz = sdf(X, Y, Z + e) - sdf(X, Y, Z - e)
    nn = np.sqrt(nx * nx + ny * ny + nz * nz) + 1e-9
    flat = np.zeros(hh * ww, np.float32); out = {}
    for name, val in (("m", np.ones_like(X)), ("nx", nx / nn), ("ny", ny / nn), ("nz", nz / nn), ("x", X), ("y", Y), ("z", Z), ("st", steps[hi])):
        a = flat.copy(); a[cand[hi]] = val; out[name] = a.reshape(hh, ww)
    return out

def up(a):
    if a.shape == (H, W): return a.astype(np.float32)
    return np.asarray(Image.fromarray(a.astype(np.float32), mode="F").resize((W, H), Image.BILINEAR), np.float32)

MOODS = {
    "neutral": dict(brow=(0.0, 0.0), eye=1.0, mouth="flat", pupil=(0.0, 0.0)),
    "determined": dict(brow=(-0.55, 0.0), eye=0.92, mouth="frown", pupil=(0.0, 0.0)),
    "shocked": dict(brow=(0.7, 0.0), eye=1.45, mouth="O", pupil=(0.0, 0.0)),
    "strain": dict(brow=(-0.7, 0.0), eye=0.55, mouth="gritted", pupil=(0.0, 0.0)),
    "joy": dict(brow=(0.45, 0.0), eye=0.0, mouth="grin", pupil=(0.0, 0.0)),
}

def render(P, mood, C, r, u, f, bg=None):
    sdf, sk = make_sdf(P)
    h = march(sdf, C, r, u, f)
    mk = up(h["m"]); mask = mk > 0.5; wgt = np.maximum(mk, 1e-3)
    N = np.stack([up(h[k]) / wgt for k in ("nx", "ny", "nz")], -1)
    N = N / (np.linalg.norm(N, axis=-1, keepdims=True) + 1e-6)
    st = up(h["st"]) / wgt
    L = nrm((-0.45, 0.85, 0.6)); lam = np.clip((N * L).sum(-1), 0, 1)
    Hh = nrm(L + nrm(-f)); spec = np.clip((N * Hh).sum(-1), 0, 1) ** 36
    sky = 0.5 + 0.5 * N[..., 1]
    ao = 1 - 0.30 * (st / 40.0)
    sh = np.clip((0.40 + 0.22 * sky + 0.50 * lam) * ao, 0, 1.05)
    col = np.clip(0.30 + 0.72 * sh + 0.30 * spec, 0, 1)[..., None] * np.array([1.0, 1.0, 1.0], np.float32)
    col = col * (np.array([0.93, 0.95, 1.0], np.float32) * (1 - sh[..., None] * 0.6) + sh[..., None] * 0.6)
    img = np.ones((H, W, 3), np.float32) * (0.97 if bg is None else 1.0) if bg is None else bg.copy()
    # contact shadow
    pil = Image.new("L", (W, H), 0); dd = ImageDraw.Draw(pil)
    def proj(p):
        pp = np.array(p, np.float32) - C; zc = max(float(pp @ f), 1.0)
        return W / 2 + FO * float(pp @ r) / zc, H / 2 - FO * float(pp @ u) / zc, zc
    fl = proj(((sk["anL"][0] + sk["anR"][0]) / 2, 0, (sk["anL"][2] + sk["anR"][2]) / 2))
    wd = 330 * FO / fl[2]
    dd.ellipse([fl[0] - wd, fl[1] - wd * 0.16, fl[0] + wd, fl[1] + wd * 0.16], fill=120)
    shadow = np.asarray(pil.filter(ImageFilter.GaussianBlur(22)), np.float32)[..., None] / 255
    img = img * (1 - shadow * 0.42)
    alpha = np.clip((mk - 0.22) / 0.56, 0, 1)[..., None]
    img = img * (1 - alpha) + col * alpha
    # face on the head sphere
    P_ = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)); dr = ImageDraw.Draw(P_)
    hc = sk["head"]; R = RAD["head"]
    yaw = P.get("head_yaw", 0.0); pitch = P.get("head_pitch", 0.0)
    fwd = nrm((math.sin(yaw) * math.cos(pitch), -math.sin(pitch), math.cos(yaw) * math.cos(pitch)))
    hr = nrm(np.cross([0, 1, 0], fwd)); hr = -hr if hr[0] < 0 else hr
    hu = nrm(np.cross(fwd, hr)); hu = hu if hu[1] > 0 else -hu
    M = MOODS[mood]
    def surf(a, b):          # point on the head: a = right offset, b = up offset (as fractions of R)
        v = nrm(fwd + hr * a + hu * b); return hc + v * (R + 0.5), v
    INK = (14, 12, 18)
    for sd in (-1, 1):
        p, v = surf(sd * 0.34, 0.06)
        view = nrm(C - p)
        if float(v @ view) > 0.05:
            ex, ey, zc = proj(p); s = FO / zc * R * 0.001 * 1000 / 1000
            sc = FO / zc
            rx, ry = 0.098 * R * sc * M["eye"] ** 0.3, 0.125 * R * sc * max(M["eye"], 0.12)
            if M["eye"] <= 0.01:      # joy: closed happy arcs
                dr.arc([ex - 0.09 * R * sc, ey - 0.06 * R * sc, ex + 0.09 * R * sc, ey + 0.06 * R * sc], 200, 340, fill=INK, width=max(3, int(0.03 * R * sc)))
            else:
                dr.ellipse([ex - rx, ey - ry, ex + rx, ey + ry], fill=INK)
                hrx = rx * 0.32; dr.ellipse([ex - rx * 0.1, ey - ry * 0.65, ex - rx * 0.1 + hrx * 1.4, ey - ry * 0.65 + hrx * 1.4], fill=(255, 255, 255))
            # brow
            bt = M["brow"][0]
            bx0, by0 = surf(sd * 0.18, 0.28 + 0.12 * (1 if bt > 0 else 0) * bt)[0], None
            pin = surf(sd * 0.16, 0.30 - 0.20 * (-bt if bt < 0 else 0) + 0.16 * (bt if bt > 0 else 0))[0]
            pout = surf(sd * 0.50, 0.30 + 0.08 * (-bt if bt < 0 else 0) + 0.04 * (bt if bt > 0 else 0))[0]
            a = proj(pin)[:2]; b = proj(pout)[:2]; mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2 - 0.02 * R * sc)
            dr.line([a, mid, b], fill=INK, width=max(3, int(0.028 * R * sc)))
    # mouth
    pm, vm = surf(0.0, -0.33)
    if float(vm @ nrm(C - pm)) > 0.05:
        mx, my, zc = proj(pm); sc = FO / zc; w_ = 0.12 * R * sc
        k = M["mouth"]
        if k == "flat": dr.line([(mx - w_, my), (mx + w_, my)], fill=INK, width=max(3, int(0.025 * R * sc)))
        elif k == "frown": dr.arc([mx - w_, my - 0.02 * R * sc, mx + w_, my + 0.12 * R * sc], 200, 340, fill=INK, width=max(3, int(0.028 * R * sc)))
        elif k == "O": dr.ellipse([mx - 0.07 * R * sc, my - 0.09 * R * sc, mx + 0.07 * R * sc, my + 0.09 * R * sc], fill=INK)
        elif k == "gritted":
            dr.rectangle([mx - w_ * 1.1, my - 0.05 * R * sc, mx + w_ * 1.1, my + 0.06 * R * sc], fill=(250, 250, 252), outline=INK, width=3)
            for q in (-0.5, 0, 0.5): dr.line([(mx + q * w_ * 1.1, my - 0.05 * R * sc), (mx + q * w_ * 1.1, my + 0.06 * R * sc)], fill=INK, width=2)
        elif k == "grin":
            dr.chord([mx - w_ * 1.4, my - 0.10 * R * sc, mx + w_ * 1.4, my + 0.12 * R * sc], 0, 180, fill=INK)
    return np.asarray(P_, np.float32) / 255, mask

# ---------------------------------------------------------------- poses (segment directions)
def D(x, y, z): return (x, y, z)
POSES = {
    # like the attached figure: boxing guard, head tucked, knees bent, wide stance
    "guard": dict(spine=D(0.0, 1, 0.30), head_pitch=0.40, neck=D(0, 1, 0.35), pelvis=(0, 450, 0),
                  uaL=D(-0.22, -1.0, 0.25), faL=D(1.0, 0.25, 0.35), uaR=D(0.30, -1.0, 0.20), faR=D(-0.55, 0.85, 0.35),
                  thL=D(-0.55, -1.0, 0.12), sh_L=D(-0.30, -1.0, -0.05), thR=D(0.50, -1.0, 0.10), sh_R=D(0.05, -1.0, 0.0),
                  ftL=D(-0.9, 0, 0.5), ftR=D(0.9, 0, 0.5)),
    # shovelling: bent forward, both hands on the handle, strong lean
    "dig": dict(spine=D(0.0, 1, 0.55), head_pitch=0.45, neck=D(0, 1, 0.5), pelvis=(0, 430, -30),
                uaL=D(-0.18, -1.0, 0.55), faL=D(0.15, -0.7, 0.9), uaR=D(0.18, -1.0, 0.55), faR=D(-0.1, -0.8, 0.85),
                thL=D(-0.30, -1.0, 0.45), sh_L=D(-0.10, -1.0, -0.20), thR=D(0.30, -1.0, 0.40), sh_R=D(0.10, -1.0, -0.15),
                ftL=D(-0.5, 0, 1), ftR=D(0.5, 0, 1),
                props=[("cap", (0, 620, 300), (0, 30, 120), 10), ("ell", (0, 20, 110), 52, 62, 9)]),
    # falling / panic: arms thrown up, legs dangling, leaning back
    "fall": dict(spine=D(0.0, 1, -0.18), head_pitch=-0.25, neck=D(0, 1, -0.2), pelvis=(0, 470, 0),
                 uaL=D(-0.75, 0.70, 0.15), faL=D(-0.45, 1.0, 0.1), uaR=D(0.75, 0.70, 0.15), faR=D(0.45, 1.0, 0.1),
                 thL=D(-0.35, -1.0, 0.30), sh_L=D(-0.15, -1.0, 0.45), thR=D(0.35, -1.0, 0.20), sh_R=D(0.10, -1.0, 0.50),
                 ftL=D(-0.4, -0.2, 1), ftR=D(0.4, -0.2, 1)),
    "stand": dict(),
    # triumph: arms up and out, chest out
    "triumph": dict(spine=D(0.0, 1, -0.06), head_pitch=-0.18, neck=D(0, 1, -0.15),
                    uaL=D(-0.80, 0.55, 0.0), faL=D(-0.45, 1.0, 0.0), uaR=D(0.80, 0.55, 0.0), faR=D(0.45, 1.0, 0.0),
                    thL=D(-0.30, -1.0, 0.0), sh_L=D(-0.18, -1.0, 0.0), thR=D(0.30, -1.0, 0.0), sh_R=D(0.18, -1.0, 0.0),
                    ftL=D(-0.7, 0, 1), ftR=D(0.7, 0, 1)),
}
