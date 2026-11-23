#!/usr/bin/env python3
"""Clay figure matched to the reference reel: lean egg-head mannequin, blown-out white, form drawn ONLY by thin ink hatching
(edge combs + crosshatch block in the shadow), chromatic RGB-split fringes, pixel-block glitch on one side, tiny pink heart eyes,
dark jaw line. Plus the dense magenta-violet glitch double with red outline.

API: render_figure(C, r, u, f, t, pose, mood) -> (rgb, mask);  render_double(C, r, u, f, t, offset) -> (rgb, mask)
"""
import math
import numpy as np
from PIL import Image, ImageDraw

W, H = 1080, 1920
FO = 1400.0

# ---------------------------------------------------------------- SDF
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

DEFAULT_POSE = dict(head_yaw=0.38, a1=0.03, a2=0.0, step=12.0, lean=0.0)

def sdf_fig(x, y, z, P):
    ax = np.abs(x)
    c, s = math.cos(P["head_yaw"]), math.sin(P["head_yaw"])
    xh = x * c - z * s; zh = x * s + z * c
    d = sd_ell(xh, y, zh, 0, 842, 8, 50, 60, 54)                       # skull
    d = smin(d, sd_ell(xh, y, zh, 0, 800, 16, 37, 42, 44), 20)         # narrower jaw / chin (egg)
    d = smin(d, sd_cap(x, y, z, (0, 784, 4), (0, 744, 0), 21, 27), 20)  # very short thin neck
    d = smin(d, sd_ell(x, y, z, 0, 676, 0, 76, 84, 44), 26)           # chest
    d = smin(d, sd_ell(x, y, z, 0, 572, 8, 68, 88, 42), 26)           # long torso with a soft belly
    d = smin(d, sd_ell(x, y, z, 0, 478, 0, 62, 52, 40), 24)           # pelvis
    d = smin(d, sd_ell(ax, y, z, 76, 722, 0, 38, 30, 34), 22)         # rounded, sloped shoulders
    a1, a2 = P["a1"], P["a2"]
    S = (82.0, 712.0, 0.0)
    E = (S[0] + 150 * math.sin(a1), S[1] - 150 * math.cos(a1), 16.0)
    Wr = (E[0] + 138 * math.sin(a2), E[1] - 138 * math.cos(a2), 34.0)
    d = smin(d, sd_cap(ax, y, z, S, E, 31, 25), 22)                    # long arms that hug the torso
    d = smin(d, sd_cap(ax, y, z, E, Wr, 25, 19), 20)
    d = smin(d, sd_ell(ax, y, z, Wr[0], Wr[1] - 26 * math.cos(a2), Wr[2] + 4, 22, 40, 18), 14)    # mitten hand
    zl = np.where(x < 0, z - P["step"], z + P["step"] * 0.5)           # one leg a little forward
    d = smin(d, sd_cap(ax, y, zl, (28, 466, 0), (32, 262, 12), 38, 29), 22)                       # thigh
    d = smin(d, sd_cap(ax, y, zl, (32, 262, 12), (34, 64, 4), 28, 19), 20)                        # shin
    d = smin(d, sd_ell(ax, y, zl, 38, 22, 28, 17, 14, 36), 12)                                    # small foot
    return d

def sdf_normal(x, y, z, P, e=1.2):
    nx = sdf_fig(x + e, y, z, P) - sdf_fig(x - e, y, z, P); ny = sdf_fig(x, y + e, z, P) - sdf_fig(x, y - e, z, P); nz = sdf_fig(x, y, z + e, P) - sdf_fig(x, y, z - e, P)
    n = np.sqrt(nx * nx + ny * ny + nz * nz) + 1e-9
    return nx / n, ny / n, nz / n

_GRID = {}
def grid():
    if not _GRID:
        hh, ww = H // 2, W // 2
        gy, gx = np.mgrid[0:hh, 0:ww].astype(np.float32)
        _GRID["px"] = (gx * 2 - W / 2) / FO; _GRID["py"] = (gy * 2 - H / 2) / FO
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        _GRID["xx"], _GRID["yy"] = xx, yy
    return _GRID

def lookat(C, T):
    f = T - C; f = f / np.linalg.norm(f); r = np.cross(f, [0.0, 1.0, 0.0]); r = r / np.linalg.norm(r); u = np.cross(r, f)
    return r, u, f

def march(C, r, u, f, P, offset=(0.0, 0.0, 0.0)):
    G = grid(); hh, ww = H // 2, W // 2
    Co = np.array(C, np.float32) - np.array(offset, np.float32)
    dx = (f[0] + G["px"] * r[0] - G["py"] * u[0]).ravel(); dy = (f[1] + G["px"] * r[1] - G["py"] * u[1]).ravel(); dz = (f[2] + G["px"] * r[2] - G["py"] * u[2]).ravel()
    nrm = np.sqrt(dx * dx + dy * dy + dz * dz); dx /= nrm; dy /= nrm; dz /= nrm
    ctr = np.array([0.0, 450.0, 0.0], np.float32); RB = 520.0
    ocx, ocy, ocz = ctr[0] - Co[0], ctr[1] - Co[1], ctr[2] - Co[2]
    b = dx * ocx + dy * ocy + dz * ocz; cc = ocx * ocx + ocy * ocy + ocz * ocz - RB * RB
    disc = b * b - cc
    cand = np.nonzero(disc > 0)[0]
    sq = np.sqrt(np.maximum(disc, 0))
    tt = np.maximum((b - sq)[cand], 0).astype(np.float32); tmax = (b + sq)[cand].astype(np.float32)
    D = np.stack([dx[cand], dy[cand], dz[cand]], 1)
    hit = np.zeros(len(cand), bool); act = np.arange(len(cand)); steps = np.zeros(len(cand), np.float32)
    for it in range(34):
        if act.size == 0: break
        x = Co[0] + tt[act] * D[act, 0]; y = Co[1] + tt[act] * D[act, 1]; z = Co[2] + tt[act] * D[act, 2]
        d = sdf_fig(x, y, z, P)
        hm = d < 0.6; fm = tt[act] > tmax[act]
        hit[act[hm]] = True; steps[act[hm]] = it
        keep = ~(hm | fm); tt[act[keep]] += d[keep] * 0.9; act = act[keep]
    hi = np.nonzero(hit)[0]
    X = Co[0] + tt[hi] * D[hi, 0]; Y = Co[1] + tt[hi] * D[hi, 1]; Z = Co[2] + tt[hi] * D[hi, 2]
    nx, ny, nz = sdf_normal(X, Y, Z, P)
    flat = np.zeros(hh * ww, np.float32); out = {}
    for name, val in (("m", np.ones_like(X)), ("nx", nx), ("ny", ny), ("nz", nz), ("x", X), ("y", Y), ("z", Z), ("st", steps[hi])):
        a = flat.copy(); a[cand[hi]] = val; out[name] = a.reshape(hh, ww)
    out["Co"] = Co
    return out

def up(a):
    return np.asarray(Image.fromarray(a.astype(np.float32), mode="F").resize((W, H), Image.BILINEAR), np.float32)

def upsample_hits(h):
    mk = up(h["m"]); mask = mk > 0.5; wgt = np.maximum(mk, 1e-3)
    out = {k: up(h[k]) / wgt for k in ("nx", "ny", "nz", "x", "y", "z", "st")}
    n = np.sqrt(out["nx"] ** 2 + out["ny"] ** 2 + out["nz"] ** 2) + 1e-6
    for k in ("nx", "ny", "nz"): out[k] = out[k] / n
    return mask, out

# ---------------------------------------------------------------- figure shading (reference style)
def vnoise(xx, yy, sc, seed):
    return np.sin(xx * sc * 1.0 + seed) * np.sin(yy * sc * 0.77 - seed * 0.6) + 0.5 * np.sin((xx + yy) * sc * 0.6 + seed * 1.7)

def render_figure(C, r, u, f, t, pose=None, mood="neutral", pconv=0.0):
    P = dict(DEFAULT_POSE); P.update(pose or {})
    G = grid(); xx, yy = G["xx"], G["yy"]
    h = march(C, r, u, f, P)
    mask, d = upsample_hits(h)
    N = np.stack([d["nx"], d["ny"], d["nz"]], -1)
    Pw = np.stack([d["x"], d["y"], d["z"]], -1)
    L = np.array([0.66, 0.55, 0.50], np.float32); L = L / np.linalg.norm(L)
    lam = np.clip((N * L).sum(-1), 0, 1)
    view = np.array(C, np.float32) - Pw; view = view / (np.linalg.norm(view, axis=-1, keepdims=True) + 1e-6)
    edge = 1.0 - np.abs((N * view).sum(-1))
    # blown-out white; the only "shading" is a hint of cool tint in the shadow
    col = np.ones((H, W, 3), np.float32) * (0.94 + 0.06 * lam[..., None]) * (np.array([0.965, 0.955, 1.0], np.float32) * (1 - lam[..., None]) + lam[..., None])
    # hatching density: shadow side + silhouette edges
    Dk_edge = np.clip((edge - 0.58) / 0.42, 0, 1) * np.where(lam < 0.62, 1.0, 0.25)
    Dk_sh = np.clip((0.17 - lam) / 0.17, 0, 1)
    Dk = np.maximum(Dk_edge, 0.8 * Dk_sh)
    nxs = (N * r).sum(-1); nys = (N * u).sum(-1)
    n1 = vnoise(xx, yy, 0.07, 1.3)
    ph_h = yy / 5.4 + 0.12 * n1
    row = np.floor(ph_h); fr_h = ph_h - row
    rh = np.sin(row * 12.9898 + 3.1) * 43758.5453; rh = rh - np.floor(rh)            # per-row random stroke length
    ph_v = xx / 5.4 + 0.12 * n1
    fr_v = ph_v - np.floor(ph_v)
    wdt = np.clip(0.15 + Dk * 0.24, 0, 0.42)
    main = (fr_h < wdt) & (Dk > 0.10 + 0.55 * rh)                                    # comb of strokes, ragged lengths
    grid_ = (fr_v < wdt * 0.85) & (Dk_sh > 0.45) & (fr_h < wdt * 1.6)                # neat crosshatch block in the deepest shadow
    lines = (main | grid_) & mask
    ink = np.array([0.16, 0.12, 0.24], np.float32)
    col = np.where(lines[..., None], col * 0.28 + ink * 0.58, col)
    # jaw line + tick marks, heart eyes (drawn on a PIL layer, then merged)
    pil = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dr = ImageDraw.Draw(pil)
    hc, hs = math.cos(P["head_yaw"]), math.sin(P["head_yaw"])
    def head_pt(xh, y, zh): return np.array([xh * hc + zh * hs, y, -xh * hs + zh * hc], np.float32)
    def proj(p):
        pp = p - np.array(C, np.float32); xc, yc, zc = pp @ r, pp @ u, max(pp @ f, 1.0)
        return W / 2 + FO * xc / zc, H / 2 - FO * yc / zc, zc
    def facing(p, nrm):
        v = np.array(C, np.float32) - p; v = v / np.linalg.norm(v); return float(v @ nrm)
    # jaw
    jaw = []
    for xh in np.linspace(-30, 30, 16):
        zh = 12 + 40 * math.sqrt(max(0.0, 1 - (xh / 41.0) ** 2)); y = 800 - 0.012 * xh * xh
        p = head_pt(xh, y, zh); n_ = head_pt(xh / 41.0, 0.15, 1.0); n_ = n_ / np.linalg.norm(n_)
        if facing(p, n_) > 0.08: jaw.append(proj(p)[:2] + (xh,))
    if len(jaw) > 2:
        dr.line([(a, b) for a, b, _ in jaw], fill=(30, 20, 40, 255), width=3)
        for a, b, xh in jaw[::2]: dr.line([(a, b), (a + 1, b + 9)], fill=(30, 20, 40, 255), width=2)
    # eyes: plain, normal eyes (white, thin ink outline, dark pupil); mood changes lids / brows
    INK_ = (34, 26, 44, 255)
    for sd in (-1, 1):
        p = head_pt(sd * 23, 848, 47)
        n_ = head_pt(sd * 0.35, 0.0, 1.0); n_ = n_ / np.linalg.norm(n_)
        if facing(p, n_) > -0.35:
            ex, ey, zc = proj(p); sc = FO / zc * 0.62
            rx, ry = 12.5 * sc, 9.5 * sc
            if mood == "triumph":
                dr.arc([ex - rx, ey - ry * 0.9, ex + rx, ey + ry * 0.9 + 4], 200, 340, fill=INK_, width=4)
                continue
            dr.ellipse([ex - rx, ey - ry, ex + rx, ey + ry], fill=(252, 250, 255, 255), outline=INK_, width=3)
            px_, pr = ex + 3.0 * sc, 5.2 * sc
            dr.ellipse([px_ - pr, ey - pr, px_ + pr, ey + pr], fill=(24, 18, 30, 255))
            dr.ellipse([px_ - pr * 0.1, ey - pr * 0.7, px_ + pr * 0.45, ey - pr * 0.15], fill=(255, 255, 255, 255))
            if mood == "determined":
                dr.polygon([(ex - rx - 2, ey - ry - 2), (ex + rx + 2, ey - ry - 2), (ex + rx + 2, ey - ry * 0.15), (ex - rx - 2, ey - ry * 0.15)], fill=(236, 233, 242, 255))
                dr.line([(ex - rx - 2, ey - ry * 0.15), (ex + rx + 2, ey - ry * 0.15)], fill=INK_, width=4)
                dr.line([(ex - sd * rx * 1.2, ey - ry * 1.9 - sd * 5 * sc * 0.2), (ex + sd * rx * 0.9, ey - ry * 1.2 + sd * 6 * sc * 0.3)], fill=INK_, width=5)
    layer = np.asarray(pil, np.float32) / 255
    col = col * (1 - layer[..., 3:4]) + layer[..., :3] * layer[..., 3:4]
    # chromatic RGB split on the whole figure layer (edges + hatch lines pick up red / blue fringes)
    def sh(a, k): return np.roll(a, k, axis=1)
    m = mask.astype(np.float32)
    mr, mb = sh(m, -3), sh(m, 3)
    outR = sh(col[..., 0], -3); outB = sh(col[..., 2], 3)
    col2 = np.stack([outR, col[..., 1], outB], -1)
    mask_ch = np.stack([mr, m, mb], -1)
    # glitch pixel blocks along the right / upper-right silhouette
    strip = (np.roll(mask, 4, axis=1) | np.roll(mask, 9, axis=1) | np.roll(mask, 5, axis=0)) & ~mask
    bx = (xx // 4).astype(np.int32); by = (yy // 4).astype(np.int32)
    hsh = np.sin(bx * 12.9898 + by * 78.233 + math.floor(t * 8) * 3.7) * 43758.5453; rk = hsh - np.floor(hsh)
    blocks = strip & (rk < 0.5)
    pal = np.array([[0.92, 0.20, 0.80], [0.50, 0.30, 1.0], [0.30, 0.40, 1.0], [1.0, 0.22, 0.30]], np.float32)
    bc = pal[np.minimum((rk * 8).astype(int), 3)]
    return dict(col=col2, mask_ch=mask_ch, mask=mask, blocks=blocks, bcol=bc)

def composite_figure(bg, fig):
    from PIL import ImageFilter
    m = Image.fromarray((fig["mask"].astype(np.uint8) * 255)).resize((W // 4, H // 4), Image.BILINEAR).filter(ImageFilter.GaussianBlur(7)).resize((W, H), Image.BILINEAR)
    glow = np.asarray(m, np.float32)[..., None] / 255
    bg = bg + glow * 0.42 * np.array([1.0, 0.98, 1.0], np.float32)
    out = bg * (1 - fig["mask_ch"]) + fig["col"] * fig["mask_ch"]
    out = np.where(fig["blocks"][..., None], fig["bcol"], out)
    return out

# ---------------------------------------------------------------- the glitch double
def render_double(C, r, u, f, t, offset=(210.0, 0.0, -110.0), pose=None, alpha=1.0):
    P = dict(DEFAULT_POSE); P.update(pose or {})
    G = grid(); xx, yy = G["xx"], G["yy"]
    h = march(C, r, u, f, P, offset=offset)
    mask, d = upsample_hits(h)
    bx = (xx // 5).astype(np.int32); by = (yy // 5).astype(np.int32)
    fl = math.floor(t * 9)
    hsh = np.sin(bx * 12.9898 + by * 78.233 + fl * 5.1) * 43758.5453; rk = hsh - np.floor(hsh)
    base = np.array([0.55, 0.16, 0.88], np.float32)
    col = np.ones((H, W, 3), np.float32) * base
    pal = np.array([[1.0, 0.22, 0.34], [0.30, 0.34, 1.0], [0.96, 0.96, 1.0], [0.40, 0.95, 0.42], [0.88, 0.22, 0.82]], np.float32)
    idx = np.minimum((rk * 5).astype(int), 4)
    noisy = rk < 0.42
    col = np.where(noisy[..., None], pal[idx], col)
    # red outline
    er = mask.copy()
    for s_ in ((3, 0), (-3, 0), (0, 3), (0, -3)): er &= np.roll(mask, s_, axis=(0, 1))
    col = np.where((mask & ~er)[..., None], np.array([1.0, 0.12, 0.18], np.float32), col)
    # glitch slices
    rng = np.random.RandomState(fl % 1000)
    for k in range(2):
        if rng.rand() < 0.6:
            y0 = int(rng.uniform(300, 1500)); hg = int(rng.uniform(16, 80)); sh_ = int(rng.uniform(-26, 26))
            col[y0:y0 + hg] = np.roll(col[y0:y0 + hg], sh_, axis=1)
    return col, mask.astype(np.float32) * alpha
