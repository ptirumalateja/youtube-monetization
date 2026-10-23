"""PHP2Shell reel: tilted dot-matrix world map, spreading red pings, arcs, counters.

usage: python3 render.py OUTDIR [--frames a:b] [--still t1,t2,...] [--workers 4]
Writes OUTDIR/f_00000.png ... (1080x1920, 30 fps, 450 frames). Text is drawn by text.py
into the same frame so picture and captions share one pass.
"""
import os, sys, math, argparse
import numpy as np
from multiprocessing import Pool
from scipy.ndimage import gaussian_filter, zoom
from PIL import Image

from timeline import *
import text as T

HERE = os.path.dirname(os.path.abspath(__file__))
Z = np.load(f"{HERE}/data/world.npz")
LAND = Z["land"].astype(np.float64)
HOSTS = Z["hosts"].astype(np.float64)
RANK = Z["order"].astype(np.float64)
FIRST = int(Z["first"])
NH = len(HOSTS)
rng = np.random.default_rng(11)

F = (H / 2) / math.tan(math.radians(25))
CY = 1010.0  # principal point (map centre sits a little below frame centre)
SUB = 3      # motion-blur sub-frames

# infection time per host
TI = 1.2 + RANK ** (1 / 2.2) * (BREATH - 1.2)
TI[FIRST] = 0.0
FLICK = rng.random(NH) * 6.28
FLICK_F = 1.5 + 3 * rng.random(NH)
# drain order at the end (far / late ones first), seed stays lit for the loop
TD = WHO + 0.15 + (1 - RANK) * 1.45

# arcs: early ones radiate from the seed, later ones hop between lit hosts
def gd(a, b):
    la1, la2 = np.radians(a[..., 1]), np.radians(b[..., 1])
    dl = np.radians(a[..., 0] - b[..., 0])
    return np.degrees(np.arccos(np.clip(np.sin(la1) * np.sin(la2) + np.cos(la1) * np.cos(la2) * np.cos(dl), -1, 1)))

ARCS = []
cand = [i for i in np.argsort(TI) if i != FIRST and 1.25 < TI[i] < BREATH - 0.1]
for n, i in enumerate(cand):
    if n < 14:
        ARCS.append((FIRST, i))
        continue
    if rng.random() > 0.075:
        continue
    earlier = np.where(TI < TI[i] - 0.5)[0]
    d = gd(HOSTS[earlier], HOSTS[i][None])
    ok = earlier[(d > 12) & (d < 95)]
    if len(ok):
        ARCS.append((int(rng.choice(ok)), i))
ARC_DUR = 0.55
print("arcs", len(ARCS), file=sys.stderr)

# dust above the plane (parallax)
ND = 900
DUST = np.c_[rng.uniform(-180, 180, ND), rng.uniform(-60, 80, ND), rng.uniform(1.5, 45, ND)]
DUST_V = rng.normal(0, 0.6, (ND, 3)) * [1, 1, 0.2]

# lat/lon grid
gl = []
for lon in range(-180, 181, 15):
    la = np.arange(-60, 80.1, 0.45)
    gl.append(np.c_[np.full_like(la, lon), la])
for lat in range(-60, 76, 15):
    lo = np.arange(-180, 180, 0.45)
    gl.append(np.c_[lo, np.full_like(lo, lat)])
GRID = np.vstack(gl)

# ring template
RING_N = 40
RING_C = np.c_[np.cos(np.linspace(0, 2 * np.pi, RING_N, endpoint=False)), np.sin(np.linspace(0, 2 * np.pi, RING_N, endpoint=False))]

# ---------------- camera ----------------
# (t, target lon, target lat, distance, pitch deg, yaw deg)
KEYS = [
    (0.0, 4.0, 51.0, 40.0, 44.0, -5.0),
    (2.2, 5.0, 50.0, 33.0, 45.0, -4.0),
    (3.6, 12.0, 42.0, 150.0, 46.0, -2.0),
    (8.5, 45.0, 30.0, 250.0, 47.0, 2.0),
    (9.0, 45.0, 30.0, 238.0, 47.0, 2.0),
    (13.0, -5.0, 30.0, 270.0, 48.0, 0.0),
    (14.85, 4.4, 50.8, 41.0, 44.2, -4.9),
    (15.0, 4.0, 51.0, 40.0, 44.0, -5.0),
]


def cam_at(t):
    for k in range(len(KEYS) - 1):
        a, b = KEYS[k], KEYS[k + 1]
        if a[0] <= t <= b[0]:
            x = (t - a[0]) / (b[0] - a[0])
            if k == 1:      # snap out
                e = ease_out(x) ** 0.9
            elif k == 5:    # fly home: accelerate, then ease into the slow push of frame 0
                e = 1 - (1 - smooth(x)) ** 1.0
            elif k == 6:
                e = x
            else:
                e = smooth(x)
            v = [a[i] + (b[i] - a[i]) * e for i in range(1, 6)]
            # distance interpolates in log space
            v[2] = math.exp(math.log(a[3]) + (math.log(b[3]) - math.log(a[3])) * e)
            return v
    return list(KEYS[-1][1:])


def basis(tx, ty, D, pitch, yaw, shake=(0, 0)):
    p, y = math.radians(pitch), math.radians(yaw)
    # rotate the "south of target" offset by yaw
    off = np.array([math.sin(y) * math.sin(p), -math.cos(y) * math.sin(p), math.cos(p)])
    T3 = np.array([tx + shake[0], ty + shake[1], 0.0])
    C = T3 + D * off
    f = (T3 - C) / D
    r = np.cross(f, [0, 0, 1.0]); r /= np.linalg.norm(r)
    u = np.cross(r, f)
    return C, f, r, u, D


def project(P, cam):
    C, f, r, u, D = cam
    Q = P - C
    z = Q @ f
    x = W / 2 + F * (Q @ r) / np.maximum(z, 1e-3)
    y = CY - F * (Q @ u) / np.maximum(z, 1e-3)
    return x, y, z


def wrap_lon(P, tx):
    P = P.copy()
    P[:, 0] = (P[:, 0] - tx + 180) % 360 - 180 + tx
    return P


# ---------------- splatting ----------------
BINS = [0.7, 1.1, 1.7, 2.6, 4.0, 6.0, 9.0]


class Canvas:
    def __init__(self):
        self.b = [np.zeros((H, W, 3), np.float32) for _ in BINS]

    def add(self, x, y, sig, rgb):
        """x,y screen; sig gaussian sigma px; rgb (N,3) energy."""
        m = (x > -20) & (x < W + 20) & (y > -20) & (y < H + 20) & np.isfinite(x) & np.isfinite(y)
        x, y, sig, rgb = x[m], y[m], sig[m], rgb[m]
        if not len(x):
            return
        bi = np.clip(np.searchsorted(BINS, sig), 0, len(BINS) - 1)
        # compensate peak so a bigger dot is not brighter in total than intended: keep energy
        for k in range(len(BINS)):
            s = bi == k
            if not s.any():
                continue
            self._bil(self.b[k], x[s], y[s], rgb[s])

    @staticmethod
    def _bil(buf, x, y, rgb):
        x0 = np.floor(x).astype(int); y0 = np.floor(y).astype(int)
        fx = (x - x0)[:, None]; fy = (y - y0)[:, None]
        for dx, dy, w in ((0, 0, (1 - fx) * (1 - fy)), (1, 0, fx * (1 - fy)), (0, 1, (1 - fx) * fy), (1, 1, fx * fy)):
            xx, yy = x0 + dx, y0 + dy
            ok = (xx >= 0) & (xx < W) & (yy >= 0) & (yy < H)
            np.add.at(buf, (yy[ok], xx[ok]), (rgb * w)[ok])

    def resolve(self):
        out = np.zeros((H, W, 3), np.float32)
        for s, b in zip(BINS, self.b):
            if b.any():
                # gaussian of energy E with sigma s has peak E/(2 pi s^2); scale so peak ~E
                out += gaussian_filter(b, (s, s, 0), truncate=3.0) * (2 * np.pi * s * s)
        return out


# ---------------- frame ----------------
RED = np.array([1.0, 0.11, 0.08])
HOT = np.array([1.0, 0.62, 0.48])
LANDC = np.array([0.30, 0.07, 0.075])


def scene(t, cv, heat):
    tx, ty, D, pitch, yaw = cam_at(t)
    shake = (0, 0)
    for th, amp in ((HIT, 1.0), (HIT2, 0.5), (0.0, 0.25)):
        if 0 <= t - th < 0.5:
            a = amp * math.exp(-(t - th) / 0.12) * D * 0.004
            shake = (a * math.sin(t * 91), a * math.cos(t * 77))
    cam = basis(tx, ty, D, pitch, yaw, shake)
    gdim = 1.0
    if BREATH <= t < HIT:
        gdim = 1 - 0.55 * smooth((t - BREATH) / 0.25)
    hitb = 0.0
    if t >= HIT:
        hitb = math.exp(-(t - HIT) / 0.35)

    def fog(z):
        return np.clip(1.25 - 0.55 * (z / D), 0.15, 1.15)

    # grid
    P = wrap_lon(np.c_[GRID, np.zeros(len(GRID))], tx)
    x, y, z = project(P, cam)
    s = 0.12 * F / z
    cv.add(x, y, np.maximum(s, 0.7), (np.array([0.06, 0.012, 0.016]) * gdim * fog(z)[:, None]) * np.ones((len(x), 1)))

    # land dots with a scan sweep
    P = wrap_lon(np.c_[LAND, np.zeros(len(LAND))], tx)
    x, y, z = project(P, cam)
    sweep_lon = -180 + ((t / 3.0) % 1.0) * 360
    dl = (P[:, 0] - (sweep_lon + tx) + 180) % 360 - 180
    sw = 0.55 * np.exp(-(dl / 5.0) ** 2)
    lit_frac = spread_level(t) if t < WHO else max(0.0, 1 - (t - WHO) / 1.6)
    base = (0.6 + 0.2 * lit_frac + sw) * gdim * fog(z)
    s = 0.24 * F / z
    cv.add(x, y, np.maximum(s, 0.7), LANDC[None] * base[:, None])

    # hosts
    a = t - TI
    on = a >= 0
    alive = np.ones(NH)
    if t >= WHO:
        alive = np.clip(1 - (t - TD) / 0.3, 0, 1)
        alive[FIRST] = 1.0
    on &= alive > 0
    idx = np.where(on)[0]
    if len(idx):
        P = wrap_lon(np.c_[HOSTS[idx], np.zeros(len(idx))], tx)
        x, y, z = project(P, cam)
        ai = a[idx]
        fl = np.exp(-ai / 0.16)
        steady = (0.62 + 0.22 * np.sin(t * FLICK_F[idx] + FLICK[idx])) * (1 - np.exp(-ai / 0.08))
        if BREATH <= t < HIT:
            steady = steady * 0 + 0.55
        steady = steady * (1 + 1.4 * hitb)
        al = alive[idx] * gdim
        fz = fog(z)
        sc = F / z
        # core
        cv.add(x, y, np.maximum(0.30 * sc, 0.8), (RED[None] * (steady * al * fz)[:, None] * 1.5))
        # flash
        fm = fl > 0.02
        cv.add(x[fm], y[fm], np.maximum(0.9 * sc[fm] * (1 + 1.5 * (1 - fl[fm])), 1.2), HOT[None] * (fl[fm] * al[fm] * fz[fm] * 3.0)[:, None])
        # heat accumulation for the glow field (low res)
        hx = (x / 8).astype(int); hy = (y / 8).astype(int)
        ok = (hx >= 0) & (hx < W // 8) & (hy >= 0) & (hy < H // 8)
        np.add.at(heat, (hy[ok], hx[ok]), (steady * al * fz)[ok] * np.minimum(sc[ok] * 0.08, 1.5))
        # rings
        rm = (ai < 1.0)
        ri = idx[rm]
        if len(ri):
            rad = 0.4 + ai[rm] * (7.0 if t > 2.0 else 4.0)
            pts = HOSTS[ri][:, None, :] + rad[:, None, None] * RING_C[None] * np.array([1, 1])
            pts = pts.reshape(-1, 2)
            P = wrap_lon(np.c_[pts, np.zeros(len(pts))], tx)
            x, y, z = project(P, cam)
            e = np.repeat(((1 - ai[rm]) ** 2) * alive[ri] * gdim, RING_N)
            cv.add(x, y, np.maximum(0.10 * F / z, 0.7), RED[None] * (e * 0.55 * fog(z))[:, None])

    # seed beacon: the first ping keeps a slow pulse ring (this is what frame 0 and the end share)
    sa = (t % 1.5) / 1.5 if t < SPREAD or t > WHO + 1.0 else None
    if sa is not None:
        pts = HOSTS[FIRST][None] + (0.5 + sa * 5.0) * RING_C
        P = np.c_[pts, np.zeros(len(pts))]
        x, y, z = project(P, cam)
        cv.add(x, y, np.maximum(0.10 * F / z, 0.8), RED[None] * ((1 - sa) ** 1.5 * 0.9) * np.ones((len(x), 1)))

    # hit shockwave from the seed across the planet
    if t >= HIT and t - HIT < 1.6:
        ha = (t - HIT) / 1.6
        n = 720
        cc = np.c_[np.cos(np.linspace(0, 2 * np.pi, n, endpoint=False)), np.sin(np.linspace(0, 2 * np.pi, n, endpoint=False))]
        pts = HOSTS[FIRST][None] + ease_out(ha) * 210 * cc
        P = wrap_lon(np.c_[pts, np.zeros(n)], tx)
        x, y, z = project(P, cam)
        cv.add(x, y, np.maximum(0.25 * F / z, 1.0), HOT[None] * ((1 - ha) ** 2 * 1.2 * fog(z))[:, None])

    # arcs
    for (p, c) in ARCS:
        t0 = TI[c] - ARC_DUR
        age = t - t0
        if age < 0 or age > ARC_DUR + 0.7:
            continue
        if t >= WHO and alive[c] <= 0:
            continue
        A = HOSTS[p].copy(); B = HOSTS[c].copy()
        if B[0] - A[0] > 180: B[0] -= 360
        if A[0] - B[0] > 180: B[0] += 360
        d = math.hypot(*(B - A))
        n = max(24, int(d * 2.2))
        sgrid = np.linspace(0, 1, n)
        prog = min(age / ARC_DUR, 1.0)
        prog_e = smooth(prog) * 0.85 + prog * 0.15
        if age <= ARC_DUR:
            tail = 0.45
            w = np.clip(1 - (prog_e - sgrid) / tail, 0, 1) * (sgrid <= prog_e)
            w = w ** 1.6
        else:
            w = np.full(n, 0.25 * (1 - (age - ARC_DUR) / 0.7))
        m = w > 0.01
        if not m.any():
            continue
        sg = sgrid[m]
        XY = A[None] + (B - A)[None] * sg[:, None]
        Zh = 4 * sg * (1 - sg) * (0.22 * d)
        P = wrap_lon(np.c_[XY, Zh], tx)
        x, y, z = project(P, cam)
        e = w[m] * gdim * fog(z)
        cv.add(x, y, np.maximum(0.12 * F / z, 0.8), (RED * 0.8 + HOT * 0.2)[None] * (e * 0.7)[:, None])
        if age <= ARC_DUR:
            hp = A + (B - A) * prog_e
            P = wrap_lon(np.array([[hp[0], hp[1], 4 * prog_e * (1 - prog_e) * 0.22 * d]]), tx)
            x, y, z = project(P, cam)
            cv.add(x, y, np.maximum(0.45 * F / z, 1.2), HOT[None] * 1.6 * fog(z)[:, None])

    # dust
    Pd = DUST + DUST_V * t
    Pd = wrap_lon(Pd, tx)
    x, y, z = project(Pd, cam)
    vis = z > 2
    tw = 0.5 + 0.5 * np.sin(t * 2 + np.arange(ND))
    cv.add(x[vis], y[vis], np.maximum(0.12 * F / z[vis], 0.7), np.array([0.5, 0.16, 0.13])[None] * (0.10 * tw[vis] * gdim)[:, None])
    return cam, hitb


YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
VIG = 1 - 0.62 * np.clip((((XX - W / 2) / (W * 0.62)) ** 2 + ((YY - CY) / (H * 0.55)) ** 2), 0, 1) ** 1.3
SKY = np.clip(1 - YY / (H * 0.5), 0, 1) ** 2  # top of frame = far horizon haze


def render(t):
    acc = np.zeros((H, W, 3), np.float32)
    heat_acc = np.zeros((H // 8, W // 8), np.float32)
    for k in range(SUB):
        ts = t + (k / SUB - 0.5) * (1 / FPS) * 0.6
        ts = min(max(ts, 0.0), DUR - 1e-4)
        cv = Canvas()
        heat = np.zeros((H // 8, W // 8), np.float32)
        cam, hitb = scene(ts, cv, heat)
        acc += cv.resolve()
        heat_acc += heat
    img = acc / SUB
    heat = gaussian_filter(heat_acc / SUB, 6) * 0.006 + gaussian_filter(heat_acc / SUB, 18) * 0.014
    heat = zoom(heat, 8, order=1)[:H, :W]
    img += heat[..., None] * np.array([0.9, 0.10, 0.07], np.float32)[None, None]

    # background: deep red-black with horizon haze
    lit = spread_level(t) if t < WHO else max(0.0, 1 - (t - WHO) / 1.6)
    bg = np.array([0.020, 0.006, 0.008], np.float32) + SKY[..., None] * np.array([0.10, 0.018, 0.02], np.float32) * (0.5 + 0.8 * lit)
    img = img + bg

    # bloom
    small = zoom(img, (0.25, 0.25, 1), order=1)
    b1 = gaussian_filter(small, (3, 3, 0)); b2 = gaussian_filter(small, (12, 12, 0))
    bloom = zoom(b1 * 0.55 + b2 * 0.55, (4, 4, 1), order=1)[:H, :W]
    img = img + bloom * 0.8
    if t >= HIT:
        hb = math.exp(-(t - HIT) / 0.25)
        img = img + hb * 0.10 * np.array([1, 0.25, 0.2], np.float32)
    img = img * VIG[..., None]
    img = 1 - np.exp(-1.35 * img)
    # chromatic split on hits
    for th in (0.0, HIT, HIT2):
        if 0 <= t - th < 0.3:
            sh = int(round(6 * (1 - (t - th) / 0.3)))
            if sh:
                img[:, sh:, 0] = img[:, :-sh, 0].copy()
                img[:, :-sh, 2] = img[:, sh:, 2].copy()
    g = np.random.default_rng(int(t * 1000)).normal(0, 0.012, (H, W, 1)).astype(np.float32)
    img = np.clip(img + g, 0, 1)
    rgb = Image.fromarray((img ** (1 / 1.05) * 255 + 0.5).astype(np.uint8), "RGB")
    cam = basis(*cam_at(t))
    sx, sy, _ = project(np.array([[HOSTS[FIRST][0], HOSTS[FIRST][1], 0.0]]), cam)
    return T.draw(rgb, t, (float(sx[0]), float(sy[0])))


def job(args):
    i, out = args
    p = f"{out}/f_{i:05d}.png"
    if os.path.exists(p):
        return
    render(i / FPS).save(p, compress_level=1)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--frames", default=None)
    ap.add_argument("--still", default=None)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    if a.still:
        for s in a.still.split(","):
            render(float(s)).save(f"{a.out}/still_{float(s):05.2f}.png")
        sys.exit()
    n = int(DUR * FPS)
    lo, hi = (0, n) if not a.frames else map(int, a.frames.split(":"))
    with Pool(a.workers) as pool:
        for k, _ in enumerate(pool.imap_unordered(job, [(i, a.out) for i in range(lo, hi)])):
            if k % 30 == 0:
                print(k, file=sys.stderr, flush=True)
